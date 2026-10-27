#!/usr/bin/env python3
"""extract_pdf.py — local, token-efficient PDF -> LLM-ready markdown for the ingest skill.

Primary engine: PyMuPDF4LLM (fully local, no GPU, no hosted API — safe for confidential
client material). Neither it nor PyMuPDF is guaranteed to be installed on every host --
run --health-check first and report the exact missing piece rather than attempting an
unvalidated extraction.

    python extract_pdf.py --health-check
    python extract_pdf.py SOURCE.pdf -o OUTPUT.md [--ocr auto|force|off] [--pages 9-10,15]

--ocr modes:
  auto  (default) PyMuPDF4LLM; it OCRs image/scanned pages on its own. Fast, cheap. Trusts
        the born-digital text layer — which can carry silent charmap/ligature corruption
        ("fluticasone" -> "futicasone"). Fine for reading/synthesis; risky for exact values.
  force OCRmyPDF --force-ocr first (rasterize + re-OCR), then extract — REBUILDS the text
        layer, repairing ligature/charmap corruption and scanned pages. Combine with --pages
        to force-OCR only the pages you cite exact values from (keeps it cheap). Needs
        ocrmypdf+tesseract. (--redo-ocr does NOT fix born-digital corruption; force uses --force-ocr.)
  off   no OCR at all -- pages with no born-digital text layer come back blank rather than
        silently invoking the same OCR path as `auto`. Only takes effect when the installed
        PyMuPDF4LLM has `pymupdf.layout` available (see health check's `layout_ocr_control`);
        without it, this build has no per-call OCR switch and `off` cannot be honored -- the
        script says so rather than pretending.

--pages  restrict to a page range (1-based, e.g. "9-10,15"). Locators keep the ORIGINAL page
         numbers. Use it to scope big documents (CSRs) and to force-OCR just the cited pages.
         Every requested page number must exist in the source; "9-10,15" against a 12-page PDF
         is an error naming page 15, not a silent 2-page result. A limited re-read merges into
         an existing cache only when that cache records the same source fingerprint and source
         page count; a legacy or different-source cache is replaced, never mixed.

Page fidelity (every run, local, no model tokens): each page's extract is compared with the PDF's
own text layer as word and number multisets. A page that lost its body text -- in practice `auto`
OCR keeping a figure's OCR text and dropping the prose beside it -- is repaired on the spot, first
by re-extracting it with OCR off, then from the raw text layer, and is listed as RECOVERED. A page
that cannot be repaired is FLAGGED; a page with no text layer to compare (a scan) is UNVERIFIED;
a SUSPECT line is a pattern hit such as a range that lost its hyphen ("78.586.7") or a table cell
that closes a range with ")" and never opens it. All of it is recorded in the cache header as
`page_fidelity=<page>:<status>,...` (`none` when every page passed; `unchecked` marks cached pages
from a cache written before this check existed). Not checked under `--ocr force`, which rebuilds the
text layer it would compare against. It cannot catch a fault in the PDF's own text layer, and it
does not read figures.

Decision rule (the agent decides, the user does not spot-check): `ingest.md` requires an active
extraction capability and preserved locators. For this utility, use `auto` first; scan recovered data
table rows for blank or truncated cells and re-run with `--ocr force --pages <those pages>`
on any hit, before filing the synthesis page. Only prompt the user when OCR is needed but not
possible (ocrmypdf/tesseract missing, or an open-password PDF). For documents `force` still
garbles (dense multi-column / formulas), escalate to Docling/Marker.
"""

# familiar's floor is Python 3.10. On anything older, stop with a plain message instead of a traceback.
import sys
if sys.version_info < (3, 10):
    sys.exit("familiar needs Python 3.10 or newer, but this is Python %d.%d (%s). Install Python 3.10+ "
             "(.familiar/scripts/doctor.py says how), then run this again with it." % (*sys.version_info[:2], sys.executable))

import argparse, hashlib, os, re, shutil, subprocess, sys, tempfile, unicodedata
from collections import Counter
from pathlib import Path


def health_check() -> dict:
    try:
        import pymupdf4llm  # noqa: F401
        pymupdf4llm_ok, pymupdf4llm_reason = True, None
    except ImportError as e:
        pymupdf4llm_ok, pymupdf4llm_reason = False, f"pymupdf4llm not importable: {e}"
    try:
        import pymupdf  # noqa: F401
        pymupdf_ok, pymupdf_reason = True, None
    except ImportError as e:
        pymupdf_ok, pymupdf_reason = False, f"pymupdf not importable: {e}"
    try:
        import ocrmypdf  # noqa: F401
        ocrmypdf_ok = True
    except ImportError:
        ocrmypdf_ok = False
    tesseract = shutil.which("tesseract")
    ghostscript = shutil.which("gs") or shutil.which("gswin64c") or shutil.which("gswin32c")
    force_ocr = ocrmypdf_ok and tesseract is not None and ghostscript is not None
    layout_ocr_control = False
    if pymupdf4llm_ok:
        try:
            import pymupdf4llm
            layout_ocr_control = bool(getattr(pymupdf4llm, "_use_layout", False))
        except ImportError:
            pass
    return {
        "extract": pymupdf4llm_ok and pymupdf_ok,
        "extract_reason": pymupdf4llm_reason or pymupdf_reason,
        "force_ocr": force_ocr,
        "force_ocr_reason": None if force_ocr else
            "needs ocrmypdf (pip) plus the external Tesseract and Ghostscript binaries",
        "layout_ocr_control": layout_ocr_control,
        "layout_ocr_control_reason": None if layout_ocr_control else
            "this PyMuPDF4LLM build has no pymupdf.layout -- --ocr off cannot be honored, "
            "'auto' and 'off' will make the same call",
        "qpdf": shutil.which("qpdf") is not None,
    }


def parse_pages(spec, n):
    """1-based page spec -> sorted 0-based indices. Every named page must exist in the
    n-page source -- a page number out of range is an error, not a silently dropped request
    (requesting "1,999" of a 1-page document must not quietly come back as page 1 alone)."""
    idx = set()
    out_of_range = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-")
            for p in range(int(a), int(b) + 1):
                (idx if 1 <= p <= n else out_of_range).add(p)
        else:
            p = int(part)
            (idx if 1 <= p <= n else out_of_range).add(p)
    if out_of_range:
        raise ValueError(
            f"--pages names page(s) {sorted(out_of_range)} but the source has only {n} page(s)."
        )
    return sorted(p - 1 for p in idx)


def run_force_ocr(src, workdir):
    out = str(Path(workdir) / "force_ocr.pdf")
    # invoke via `python -m` so it works even when the ocrmypdf console-script dir isn't on PATH
    subprocess.run([sys.executable, "-m", "ocrmypdf", "--force-ocr", "--quiet", src, out], check=True)
    return out


PAGE_MARKER_RE = re.compile(r"<!-- PDF page (\d+) -->\n\n")


def split_page_chunks(md):
    """Parse a previously-written extract's own `<!-- PDF page N -->` markers back into
    {page_number: text}. Used to splice a limited re-extraction into an existing cache
    without discarding the pages that were not re-selected."""
    matches = list(PAGE_MARKER_RE.finditer(md))
    pages = {}
    for i, m in enumerate(matches):
        pno = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        pages[pno] = md[start:end].rstrip("\n")
    return pages


def render_page_chunks(pages: dict) -> str:
    parts = [f"\n\n<!-- PDF page {pno} -->\n\n{text.rstrip()}\n" for pno, text in sorted(pages.items())]
    return "".join(parts).lstrip("\n")


# -- page fidelity: extract vs the PDF's own text layer ---------------------------------------
# A text-layer page whose extract lost body text (a figure's OCR winning over the prose, a
# dropped column) or corrupted numbers is caught by comparing the two as word/number multisets.
# Order-free on purpose: two-column reading order differs without losing content. Pages with no
# text layer (scans) cannot be compared; they are reported `unverified`, plus cheap pattern flags.
FIDELITY_MIN_WORDS = 10      # below this the page is too sparse to judge by recall
FIDELITY_MIN_NUMBERS = 8
FIDELITY_WORD_RECALL = 0.85
FIDELITY_NUMBER_RECALL = 0.70   # looser: a dropped running header or DOI costs a few numbers

_ALPHA = re.compile(r"[^\W\d_]{3,}")
_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
_FUSED_RANGE = re.compile(r"(?<![\w./-])\d{1,3}\.\d{2,3}\.\d{1,3}(?![\w/]|\.\d)")   # 78.586.7 <- 78.5-86.7
_PICTURE_TEXT = re.compile(r"<!-- Start of picture text -->.*?<!-- End of picture text -->", re.S)
_CI_CLOSE = re.compile(r"\d\s?[-–]\s?\d[\d.]*\s?\)")                     # "76.6-91.0)"


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).replace("­", "")
    # rejoin a word hyphenated across a line break; never a numeric range ("78.5-\n86.7")
    return re.sub(r"(?<=[A-Za-z])-[ \t]*\n[ \t]*(?=[a-z])", "", text)


def _multisets(text):
    text = _normalize(text)
    return Counter(w.lower() for w in _ALPHA.findall(text)), Counter(_NUMBER.findall(text))


def _recall(native, got):
    total = sum(native.values())
    if not total:
        return None
    return sum(min(n, got[t]) for t, n in native.items()) / total


def page_fidelity(native_text, extract_text):
    """Compare one page's extract with its text layer. `status` is `ok`, `flagged` (text lost
    or numbers corrupted) or `unverified` (no text layer to compare). `suspects` lists pattern
    hits that apply to any page, compared or not."""
    body = _PICTURE_TEXT.sub("", extract_text)   # figure OCR is noise, not table content
    suspects = sorted(set(_FUSED_RANGE.findall(body)))
    for line in body.splitlines():
        if "|" in line:
            suspects += [f"table cell {c.strip()!r} closes a range with ')' but never opens '('"
                         for c in line.split("|") if c.count(")") > c.count("(") and _CI_CLOSE.search(c)]
    suspects = suspects[:6]
    nat_w, nat_n = _multisets(native_text)
    ext_w, ext_n = _multisets(extract_text)
    n_words, n_nums = sum(nat_w.values()), sum(nat_n.values())
    out = {"word_recall": None, "number_recall": None, "missing_numbers": [], "suspects": suspects}
    if n_words == 0 and n_nums == 0:
        out["status"] = "unverified"
        return out
    out["word_recall"] = _recall(nat_w, ext_w)
    out["number_recall"] = _recall(nat_n, ext_n)
    out["missing_numbers"] = sorted((nat_n - ext_n).elements())[:12]
    low_words = n_words >= FIDELITY_MIN_WORDS and out["word_recall"] < FIDELITY_WORD_RECALL
    low_nums = n_nums >= FIDELITY_MIN_NUMBERS and out["number_recall"] < FIDELITY_NUMBER_RECALL
    out["status"] = "flagged" if (low_words or low_nums) else "ok"
    return out


def recover_page(src, index, native_text, layout_active):
    """Repair one flagged page, cheapest first: re-extract it with OCR off, then fall back to
    the raw text layer. Returns (text, fidelity, how) for the first attempt that passes, or
    None. A recovered page keeps its place and its original page number."""
    import pymupdf4llm
    attempts = []
    if layout_active:
        try:
            ch = pymupdf4llm.to_markdown(src, pages=[index], page_chunks=True, use_ocr=False)
            attempts.append(((ch[0].get("text") or "").rstrip(), "re-extracted, OCR off"))
        except Exception:
            pass
    attempts.append((native_text.strip(), "raw text layer, structure flattened"))
    for text, how in attempts:
        fid = page_fidelity(native_text, text)
        if text and fid["status"] == "ok":
            return text, fid, how
    return None


def extract(source, ocr="auto", pages=None, low_text=200):
    """Core extraction logic, reusable by the CLI and by an HTTP service. Returns
    (markdown, stats_dict, page_chunks) where page_chunks is [(page_num, text), ...]
    in document order -- callers that need to splice in corrected pages (e.g. a
    selective re-OCR pass) work from page_chunks; callers that just want the final
    text use markdown. Any slice/OCR working files this run creates are cleaned up before
    returning -- neither is meant to outlive the call that made it."""
    import pymupdf4llm
    import pymupdf

    with tempfile.TemporaryDirectory(prefix="extract_pdf_") as workdir:
        src = source
        page_map = None  # slice-index -> original 1-based page number
        base = sub = doc = None
        try:
            if pages:
                base = pymupdf.open(source)
                sel = parse_pages(pages, base.page_count)  # raises on an out-of-range page
                if not sel:
                    raise ValueError("--pages selected no valid pages.")
                page_map = [i + 1 for i in sel]
                sub = pymupdf.open(source); sub.select(sel)
                src = str(Path(workdir) / "slice.pdf"); sub.save(src)

            ocr_note = ""
            if ocr == "force":
                src = run_force_ocr(src, workdir)
                ocr_note = "text layer REBUILT via OCRmyPDF --force-ocr (charmap/ligature-safe)"

            # `off` must actually disable OCR, not just be a policy label `auto` also satisfies --
            # only takes effect on a PyMuPDF4LLM build with pymupdf.layout (see health_check's
            # layout_ocr_control); older/non-layout builds have no such switch to pass.
            use_ocr = ocr != "off"
            layout_active = bool(getattr(pymupdf4llm, "_use_layout", False))
            if layout_active:
                chunks = pymupdf4llm.to_markdown(src, page_chunks=True, use_ocr=use_ocr)
            else:
                if ocr == "off":
                    ocr_note = ("requested but NOT honored: this PyMuPDF4LLM build has no "
                                 "pymupdf.layout, so it has no per-call OCR switch -- this call "
                                 "was identical to 'auto'") + (f"; {ocr_note}" if ocr_note else "")
                chunks = pymupdf4llm.to_markdown(src, page_chunks=True)
            doc = pymupdf.open(src)
            source_pages = base.page_count if pages else doc.page_count
            fig_pages = [(page_map[i] if page_map else i + 1)
                         for i in range(doc.page_count) if doc[i].get_images()]

            parts, low_text_pages, page_chunks, fidelity = [], [], [], {}
            for i, ch in enumerate(chunks):
                # PyMuPDF4LLM versions differ in whether they expose page_number in
                # each chunk's metadata. Keep locators valid even when it is absent.
                pno = page_map[i] if page_map else (ch["metadata"].get("page_number") or i + 1)
                txt = ch.get("text") or ""
                parts.append(f"\n\n<!-- PDF page {pno} -->\n\n{txt.rstrip()}\n")
                page_chunks.append((pno, txt.rstrip()))
                if len(txt.strip()) < low_text:
                    low_text_pages.append(pno)
                # A force-OCR'd source has a rebuilt text layer, not the original, so there is
                # nothing independent to compare against.
                if ocr == "force" or i >= doc.page_count:
                    fid = {**page_fidelity("", txt), "status": "unverified"}
                else:
                    native = doc[i].get_text("text")
                    fid = page_fidelity(native, txt)
                    if fid["status"] == "flagged":
                        rec = recover_page(src, i, native, layout_active)
                        if rec:
                            txt, rfid, how = rec
                            fid = {**rfid, "status": "recovered", "how": how, "suspects": fid["suspects"],
                                   "before": {k: fid[k] for k in ("word_recall", "number_recall", "missing_numbers")}}
                            parts[-1] = f"\n\n<!-- PDF page {pno} -->\n\n{txt.rstrip()}\n"
                            page_chunks[-1] = (pno, txt.rstrip())
                fidelity[pno] = fid
        finally:
            # Close every PyMuPDF handle onto a file inside `workdir` before the
            # TemporaryDirectory context tries to remove it -- otherwise Windows refuses to
            # delete a still-open file and cleanup itself raises.
            for handle in (base, sub, doc):
                if handle is not None:
                    handle.close()

    md = "".join(parts).lstrip("\n")
    tbl_rows = sum(1 for l in md.splitlines() if l.count("|") >= 2)

    stats = {
        "pages": len(chunks),
        "source_pages": source_pages,
        "scoped_to": pages,
        "markdown_chars": len(md),
        "markdown_table_rows": tbl_rows,
        "figure_pages": fig_pages,
        "low_text_pages": low_text_pages,
        "fidelity": fidelity,
        "ocr_mode": ocr,
        "ocr_note": ocr_note,
    }
    return md, stats, page_chunks


HEADER_RE = re.compile(r"<!-- extract_pdf\.py: (?P<fields>.*?) -->\n\n?")


def source_fingerprint(path: Path) -> str:
    """SHA-256 of the actual input bytes, streamed for large source documents."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cached_header(text: str) -> dict[str, str] | None:
    match = HEADER_RE.match(text)
    if match is None:
        return None
    fields = {}
    for token in match.group("fields").split():
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key] = value
    return fields


def fidelity_exceptions(fidelity: dict) -> dict:
    """{page: status} for every page that is not plainly `ok`: recovered, flagged, unverified,
    or `suspect` (a pattern hit on a page that otherwise passed)."""
    out = {}
    for pno, fid in fidelity.items():
        if fid["status"] != "ok":
            out[pno] = fid["status"]
        elif fid["suspects"]:
            out[pno] = "suspect"
    return out


def parse_fidelity_field(value: str) -> dict:
    return {int(p): st for p, st in (t.split(":", 1) for t in value.split(",") if ":" in t)}


def build_header(source_name, source_sha256, ocr_mode, page_numbers, source_pages, extracted_at,
                 page_ocr=None, fidelity=None) -> str:
    complete = set(page_numbers) == set(range(1, source_pages + 1))
    pages_field = "all" if complete else ",".join(str(p) for p in sorted(page_numbers))
    page_ocr = page_ocr or {p: ocr_mode for p in page_numbers}
    page_ocr_field = ",".join(f"{p}:{page_ocr[p]}" for p in sorted(page_ocr))
    fidelity_field = ""
    if fidelity is not None:   # only the non-ok pages are listed; `none` means every page passed
        listed = ",".join(f"{p}:{fidelity[p]}" for p in sorted(fidelity)) or "none"
        fidelity_field = f" page_fidelity={listed}"
    return (f"<!-- extract_pdf.py: source={source_name} extracted={extracted_at} "
            f"source_sha256={source_sha256} source_pages={source_pages} ocr_mode={ocr_mode} "
            f"page_ocr={page_ocr_field}{fidelity_field} pages={pages_field} "
            f"complete={str(complete).lower()} -->\n\n")


def atomic_write(path: Path, text: str) -> None:
    """A cache is either the old complete write or the new complete write, never a half file."""
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False,
    ) as stream:
        temp = Path(stream.name)
        stream.write(text)
    try:
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def same_file(a: Path, b: Path) -> bool:
    """True when two paths name one file, including via a different spelling, case, or link.
    The output path is chosen by the caller (often the model), so a mistyped `-o` equal to the
    source would otherwise replace the source with extracted text and still exit 0."""
    try:
        if a.exists() and b.exists():
            return os.path.samefile(a, b)
    except OSError:
        pass
    return a.resolve() == b.resolve()


def report_fidelity(fidelity: dict, ocr_mode: str) -> None:
    by = {}
    for pno, fid in sorted(fidelity.items()):
        by.setdefault(fid["status"], []).append(pno)
    if ocr_mode == "force":
        print("fidelity: not checked -- --ocr force rebuilt the text layer, so there is no independent "
              "layer to compare against.")
    else:
        checked = len(fidelity) - len(by.get("unverified", []))
        print(f"fidelity: {checked} page(s) compared with the PDF text layer; "
              f"{len(by.get('ok', []))} ok, {len(by.get('recovered', []))} recovered, "
              f"{len(by.get('flagged', []))} flagged")
    if by.get("recovered"):
        print(f"  RECOVERED p.{by['recovered']}: body text or numbers were lost in extraction and the "
              f"page was repaired from the text layer (see page_fidelity in the cache header).")
    if by.get("flagged"):
        print(f"  FLAGGED p.{by['flagged']}: text lost and NOT recoverable from the text layer. Do not "
              f"cite values from these pages; view them rendered, or re-run with --ocr force.")
    if by.get("unverified"):
        print(f"  UNVERIFIED p.{by['unverified']}: no text layer to compare (scan or image-only). "
              f"Check any value you cite from these pages against the PDF.")
    for pno, fid in sorted(fidelity.items()):
        for hit in fid["suspects"]:
            print(f"  SUSPECT p.{pno}: {hit}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?")
    ap.add_argument("-o", "--output")
    ap.add_argument("--ocr", choices=["auto", "force", "off"], default="auto")
    ap.add_argument("--pages", help="1-based page range, e.g. '9-10,15' (locators keep original numbers)")
    ap.add_argument("--low-text", type=int, default=200)
    ap.add_argument("--health-check", action="store_true")
    args = ap.parse_args()

    if args.health_check:
        import json
        print(json.dumps(health_check(), indent=2))
        return

    if not args.source or not args.output:
        ap.error("source and -o/--output are required unless --health-check is given")

    if same_file(Path(args.source), Path(args.output)):
        print("ERROR: -o/--output must not be the same file as the source; the source was not touched.",
              file=sys.stderr)
        sys.exit(1)

    try:
        md, stats, _ = extract(args.source, ocr=args.ocr, pages=args.pages, low_text=args.low_text)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"ERROR: --ocr force needs ocrmypdf (pip) plus the external Tesseract and "
              f"Ghostscript binaries installed ({e}). See SETUP.md. Until then use --ocr auto "
              f"and flag any cited values as unverified.", file=sys.stderr)
        sys.exit(3)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr); sys.exit(4)

    out_path = Path(args.output)
    input_fingerprint = source_fingerprint(Path(args.source))
    new_pages = split_page_chunks(md)
    new_page_ocr = {pno: stats["ocr_mode"] for pno in new_pages}
    new_fid = fidelity_exceptions(stats["fidelity"])
    merged_note = ""
    if args.pages and out_path.exists():
        # A limited re-read must not discard pages a prior full (or wider) extraction already
        # cached -- splice the freshly extracted pages into the existing ones instead of
        # replacing the whole file.
        previous_text = out_path.read_text(encoding="utf-8")
        previous = cached_header(previous_text)
        matches_source = previous is not None and (
            previous.get("source_sha256") == input_fingerprint
            and previous.get("source_pages") == str(stats["source_pages"])
        )
        if matches_source:
            existing = HEADER_RE.sub("", previous_text, count=1)
            old_pages = split_page_chunks(existing)
            merged = dict(old_pages)
            merged.update(new_pages)
            final_md = render_page_chunks(merged)
            covered_pages = set(merged)
            old_page_ocr = {
                int(pno): mode
                for pno, mode in (
                    token.split(":", 1) for token in previous.get("page_ocr", "").split(",") if ":" in token
                )
            }
            page_ocr = {pno: old_page_ocr.get(pno, previous.get("ocr_mode", "unknown"))
                        for pno in old_pages}
            page_ocr.update(new_page_ocr)
            if "page_fidelity" in previous:   # cached pages keep their recorded status
                old_fid = parse_fidelity_field(previous["page_fidelity"].replace("none", ""))
                page_fid = {p: st for p, st in old_fid.items() if p in old_pages}
            else:                              # a legacy cache was never checked
                page_fid = {p: "unchecked" for p in old_pages}
            page_fid = {p: st for p, st in page_fid.items() if p not in new_pages}
            page_fid.update(new_fid)
            merged_note = f" (merged with {len(old_pages)} cached page(s) already in {args.output})"
        else:
            final_md = render_page_chunks(new_pages)
            covered_pages = set(new_pages)
            page_ocr = new_page_ocr
            page_fid = new_fid
            merged_note = " (existing cache belongs to a different or legacy source; replaced, not merged)"
    else:
        final_md = render_page_chunks(new_pages)
        covered_pages = set(new_pages)
        page_ocr = new_page_ocr
        page_fid = new_fid

    from datetime import datetime, timezone
    header_ocr_mode = stats["ocr_mode"] if len(set(page_ocr.values())) == 1 else "mixed"
    header = build_header(
        Path(args.source).name, input_fingerprint, header_ocr_mode, covered_pages, stats["source_pages"],
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        page_ocr, page_fid,
    )
    atomic_write(out_path, header + final_md)

    print(f"pages: {stats['pages']}" + (f" (scoped to {stats['scoped_to']})" if stats['scoped_to'] else "")
          + merged_note)
    print(f"markdown chars: {stats['markdown_chars']} (~{round(stats['markdown_chars']/4)} tokens)")
    print(f"markdown table-rows recovered: {stats['markdown_table_rows']}")
    print(f"figure pages (embedded images — verify, may be OCR-noisy): {stats['figure_pages'] or 'none'}")
    print(f"low-text pages (<{args.low_text} chars — possible scan/figure-only): {stats['low_text_pages'] or 'none'}")
    report_fidelity(stats["fidelity"], stats["ocr_mode"])
    print(f"ocr mode: {stats['ocr_mode']}" + (f" — {stats['ocr_note']}" if stats['ocr_note'] else ""))
    if args.ocr == "auto":
        print("NOTE: 'auto' trusts the source text layer (possible silent charmap/ligature "
              "corruption). Before citing EXACT values, re-run `--ocr force --pages <those pages>`.")
    print(f"-> {args.output} ({'complete' if set(covered_pages) == set(range(1, stats['source_pages'] + 1)) else 'partial'})")


if __name__ == "__main__":
    main()
