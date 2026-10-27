#!/usr/bin/env python3
"""extract_encite.py — pull EndNote CWYW field-code citations out of a .docx source for the
ingest skill. Stdlib only (zipfile, re, xml.etree) — no optional engine to install, so
there is nothing for --health-check to report beyond confirming the source itself parses.

    python extract_encite.py SOURCE.docx -o OUTPUT.json
    python extract_encite.py SOURCE.docx --health-check

EndNote's Word plugin (Cite While You Write) embeds one field per in-text citation marker.
When the record is short, Word caches the field's *entire* EndNote XML record as literal text
inside the field's `ADDIN EN.CITE` instruction (`<w:instrText>`). A long record is instead
base64-encoded into the `w:fldData` of a nested `ADDIN EN.CITE.DATA` field, leaving the
instruction bare. This script reads both; a field with neither is counted, never dropped.

One field can bundle several stacked references behind a single marker (e.g. a superscript
"1,2"), so a field is a *citation group* containing one or more EndNote <Cite> records. Output
is the citation groups in document order, plus a deduplicated library keyed by EndNote library
ID and record number (see `record_key`). Each group's `records` lists those keys; its
`display_text` is the marker as printed (e.g. "6-13"), which is what a page's `[ref N]` cites.

This gives an ingest step ground-truth bibliographic data (author, year, title, journal, DOI)
for exactly the source-native markers EndNote generated, instead of inferring them from
whatever the marker renders as (typically a bare superscript number with no data behind it).
It does not help with sources that have no EndNote field codes at all (PPT decks, PDFs, scanned
material, or docx sources where citations were typed by hand) — those keep using the
read-and-tag-from-rendered-text path in ingest.md step 4 unchanged.
"""

# familiar's floor is Python 3.10. On anything older, stop with a plain message instead of a traceback.
import sys
if sys.version_info < (3, 10):
    sys.exit("familiar needs Python 3.10 or newer, but this is Python %d.%d (%s). Install Python 3.10+ "
             "(.familiar/scripts/doctor.py says how), then run this again with it." % (*sys.version_info[:2], sys.executable))

import argparse, base64, binascii, hashlib, json, os, re, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
PAYLOAD_RE = re.compile(r"<EndNote>[\s\S]*?</EndNote>")
DISPLAYTEXT_TAG_RE = re.compile(r'<[^>]+>')


def health_check(source: str | None = None) -> dict:
    """No optional engine here (pure stdlib) — this just confirms a given source is a readable
    docx and reports how many EndNote field codes it carries, so the caller can decide whether
    running the full extraction is worth it before committing to an output path."""
    result = {"stdlib_ok": True, "stdlib_reason": None}
    if not source:
        return result
    try:
        payloads = encite_payloads(source)
    except (FileNotFoundError, KeyError, zipfile.BadZipFile, ET.ParseError) as e:
        result["source_ok"] = False
        result["source_reason"] = f"not a readable .docx: {e}"
        return result
    result["source_ok"] = True
    result["encite_fields_found"] = len(payloads)
    result["encite_fields_without_record"] = sum(1 for payload in payloads if payload is None)
    return result


def fields(root) -> list[dict]:
    """Every field in document order as {"instr", "data", "nested"}, assembled across runs.

    Word splits one field's instruction over as many `w:instrText` nodes as it likes (after an
    edit, tracked change, or paste), so a citation can only be read once the pieces between its
    `begin` and `separate` markers are joined. Matching inside a single node found the intact
    form and silently skipped the split one -- zero citations, no warning. Fields nest, so text
    belongs to the innermost open field. `data` is the base64 `w:fldData` attached to the field's
    `begin` marker; `nested` lists the fields opened inside this one's instruction. `w:fldSimple`
    keeps its instruction in an attribute instead."""
    open_fields, done, order = [], [], 0
    for elem in root.iter():
        if elem.tag == W + "fldSimple":
            done.append({"order": order, "parts": [elem.get(W + "instr", "")], "data": "", "nested": []})
            order += 1
        elif elem.tag == W + "fldChar":
            kind = elem.get(W + "fldCharType")
            if kind == "begin":
                blob = elem.find(W + "fldData")
                field = {"order": order, "parts": [], "in_result": False, "nested": [],
                         "data": (blob.text or "") if blob is not None else ""}
                if open_fields and not open_fields[-1]["in_result"]:
                    open_fields[-1]["nested"].append(field)
                open_fields.append(field)
                order += 1
            elif kind == "separate" and open_fields:
                open_fields[-1]["in_result"] = True
            elif kind == "end" and open_fields:
                done.append(open_fields.pop())
        elif elem.tag == W + "instrText" and open_fields and not open_fields[-1]["in_result"]:
            open_fields[-1]["parts"].append(elem.text or "")
    # A field left open at the end of the body is still reported, not dropped.
    done.extend(open_fields)
    for field in done:
        field["instr"] = "".join(field["parts"])
    return sorted(done, key=lambda field: field["order"])


def _decode_field_data(blob: str) -> str:
    try:
        raw = base64.b64decode("".join(blob.split()))
    except (binascii.Error, ValueError):
        return ""
    for encoding in ("utf-8", "utf-16"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return ""


def encite_payloads(source: str) -> list[str | None]:
    """One entry per EndNote citation field (`ADDIN EN.CITE`, not its `EN.CITE.DATA` carrier) in
    the source's main body: the field's `<EndNote>` XML, or None when none can be found.

    Short records sit inline in the instruction text. Long ones do not: Word leaves the
    instruction as a bare ` ADDIN EN.CITE ` and puts the record, base64-encoded, in the
    `w:fldData` of a nested `ADDIN EN.CITE.DATA` field. Real compiled reports carry
    hundreds of these, so both places are read."""
    with zipfile.ZipFile(source) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    found = []
    for field in fields(root):
        head = field["instr"].strip()
        if not head.startswith("ADDIN EN.CITE") or head.startswith("ADDIN EN.CITE.DATA"):
            continue
        blobs = [field["data"]] + [child["data"] for child in field["nested"]
                                   if child["instr"].strip().startswith("ADDIN EN.CITE.DATA")]
        candidates = [field["instr"]] + [_decode_field_data(blob) for blob in blobs if blob]
        payload = None
        for text in candidates:
            match = PAYLOAD_RE.search(text)
            if match:
                payload = match.group(0)
                break
        found.append(payload)
    return found


def _text(elem, tag):
    child = elem.find(tag)
    return child.text.strip() if child is not None and child.text else None


def _display_text(cite_elem):
    dt = cite_elem.find("DisplayText")
    if dt is None:
        return None
    inner = "".join(dt.itertext())
    return inner.strip() or None


def parse_cite_record(cite_elem) -> dict:
    record = cite_elem.find("record")
    if record is None:
        # Bare <Cite> with no attached library record (e.g. a since-deleted EndNote entry) —
        # report what the field still knows rather than dropping the citation silently.
        return {
            "rec_number": _text(cite_elem, "RecNum"),
            "library_id": None,
            "authors": [_text(cite_elem, "Author")] if _text(cite_elem, "Author") else [],
            "year": _text(cite_elem, "Year"),
            "title": None, "journal": None, "volume": None, "number": None, "pages": None,
            "doi": None, "pmid": None, "url": None, "ref_type": None,
            "unresolved": True,
        }
    authors = [a.text.strip() for a in record.findall("./contributors/authors/author")
               if a.text and a.text.strip()]
    title = _text(record, "./titles/title")
    journal = _text(record, "./titles/secondary-title") or _text(record, "./periodical/full-title")
    ref_type_elem = record.find("ref-type")
    ref_type = ref_type_elem.get("name") if ref_type_elem is not None else None
    url = _text(record, "./urls/related-urls/url") or _text(record, "./urls/web-urls/url")
    key_elem = record.find("./foreign-keys/key")
    return {
        "rec_number": _text(record, "rec-number") or _text(cite_elem, "RecNum"),
        "library_id": key_elem.get("db-id") if key_elem is not None else None,
        "authors": authors,
        "year": _text(record, "./dates/year") or _text(cite_elem, "Year"),
        "title": title,
        "journal": journal,
        "volume": _text(record, "volume"),
        "number": _text(record, "number"),
        "pages": _text(record, "pages"),
        "doi": _text(record, "electronic-resource-num"),
        "pmid": _text(record, "accession-num"),
        "url": url,
        "ref_type": ref_type,
        "unresolved": False,
    }


def record_key(rec: dict) -> str:
    """A record's identity in the output library: `<library_id>:<rec_number>`, or the bare
    record number when the field carries no library ID. A record number is only unique within one
    EndNote library, and a document assembled from several (one real report cited from six) reuses
    the same numbers for different papers. Keying on the number alone merged them silently, so
    citations to the second paper came back carrying the first one's author, title, and DOI."""
    return f"{rec['library_id']}:{rec['rec_number']}" if rec.get("library_id") else rec["rec_number"]


def extract(source: str):
    """Returns (groups, library, malformed, unsupported). `malformed` counts fields whose EndNote
    XML would not parse; `unsupported` counts EN.CITE fields where no record was found inline or
    in field data. Both are reported, never fabricated -- and a document whose citations could
    not be read no longer looks the same as one that has none."""
    groups, library, malformed, unsupported = [], {}, 0, 0
    for payload in encite_payloads(source):
        if payload is None:
            unsupported += 1
            continue
        try:
            root = ET.fromstring(payload)
        except ET.ParseError:
            malformed += 1
            continue
        cites = root.findall("Cite")
        if not cites:
            continue
        group_display = _display_text(cites[0])
        keys, rec_numbers = [], []
        for cite in cites:
            rec = parse_cite_record(cite)
            if rec["rec_number"] is None:
                continue
            key = record_key(rec)
            keys.append(key)
            rec_numbers.append(rec["rec_number"])
            library.setdefault(key, rec)
        for key in keys:
            library[key]["occurrences"] = library[key].get("occurrences", 0) + 1
        groups.append({"display_text": group_display, "records": keys, "rec_numbers": rec_numbers})

    return groups, library, malformed, unsupported


def source_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?")
    ap.add_argument("-o", "--output")
    ap.add_argument("--health-check", action="store_true")
    args = ap.parse_args()

    if args.health_check:
        print(json.dumps(health_check(args.source), indent=2))
        return

    if not args.source or not args.output:
        ap.error("source and -o/--output are required unless --health-check is given")

    if same_file(Path(args.source), Path(args.output)):
        print("ERROR: -o/--output must not be the same file as the source; the source was not touched.",
              file=sys.stderr)
        sys.exit(1)

    source_path = Path(args.source)
    groups, library, malformed, unsupported = extract(args.source)

    from datetime import datetime, timezone
    payload = {
        "source": source_path.name,
        "source_sha256": source_fingerprint(source_path),
        "extracted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "citation_groups": groups,
        "library": library,
        "stats": {
            "citation_groups": len(groups),
            "unique_records": len(library),
            "malformed_fields_skipped": malformed,
            "unsupported_fields_skipped": unsupported,
        },
    }
    Path(args.output).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"citation groups: {len(groups)}")
    print(f"unique EndNote records: {len(library)}")
    unresolved = sum(1 for r in library.values() if r.get("unresolved"))
    if unresolved:
        print(f"WARNING: {unresolved} record(s) had no attached library data (deleted/orphaned EndNote entry) — "
              f"rec_number and author/year only, everything else null.")
    if malformed:
        print(f"WARNING: {malformed} field(s) had unparseable XML and were skipped, not fabricated.")
    if unsupported:
        print(f"WARNING: {unsupported} EndNote field(s) had no readable record, inline or in field "
              f"data, and were skipped, not fabricated. Tag those markers from the rendered text "
              f"per ingest.md step 4.")
    print(f"-> {args.output}")


if __name__ == "__main__":
    main()
