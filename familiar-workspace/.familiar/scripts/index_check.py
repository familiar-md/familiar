#!/usr/bin/env python3
"""index_check.py — does `3-Knowledge/_knowledge-index.md` agree with the pages it catalogs?

    python .familiar/scripts/index_check.py            # from anywhere inside the project
    python .familiar/scripts/index_check.py --json
    python .familiar/scripts/index_check.py --sync     # copy page dates into their index rows

Called by ingest after it writes a page (`.familiar/core/ingest.md` → Ingest procedure step 6),
and by `project_check.py`. Each page's front matter is the authority for its own facts; the index
row repeats them so a person can scan the catalog without opening every page. This compares the
two, column by column, for every column the index has:

  Source date                 the page's `source_date` must appear in the cell
  Track                       equal to the page's `track`
  Supersedes / superseded by  every non-`none` `supersedes` / `superseded_by` page must be named
  Last verified, Review by    the page's date must appear in the cell

and, for a page with no row, prints a row built from its front matter with the summary left for the
model to write. It reads and writes nothing else; the one-line summary is judgment and stays with
the model.

`--sync` is the one write. For each existing row it copies the page's own `source_date`,
`last_verified` and `review_by` into the matching cells, because those are facts the page already
states and nobody should retype them: a check pass that re-verifies seventy pages otherwise leaves
seventy rows out of date. It touches no other cell, adds no row, bumps the index's `revision` stamp,
and replaces the file atomically. Standard library only.
"""

# familiar's floor is Python 3.10. On anything older, stop with a plain message instead of a traceback.
import sys
if sys.version_info < (3, 10):
    sys.exit("familiar needs Python 3.10 or newer, but this is Python %d.%d (%s). Install Python 3.10+ "
             "(.familiar/scripts/doctor.py says how), then run this again with it." % (*sys.version_info[:2], sys.executable))

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

LINK = re.compile(r"\[([^\]]+)\]\(\./?([^)#]+\.md)\)")
ISO = re.compile(r"\d{4}-\d{2}-\d{2}")


def find_root(start: Path) -> Path | None:
    for folder in (start, *start.parents):
        if (folder / ".familiar-project").is_file():
            return folder
    return None


def front_matter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    fields, key = {}, None
    for line in text[3:end if end != -1 else None].splitlines():
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            fields[key] = m.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            fields[key] += " " + line.strip()
    return fields


def index_rows(text: str):
    header, rows = None, {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            if cells and cells[0].lower() == "page":
                header = [c.lower() for c in cells]
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        link = LINK.search(cells[0])
        if link:
            rows[Path(link.group(2)).name] = dict(zip(header, cells))
    return header or [], rows


def page_names(value: str) -> list[str]:
    """Page stems named in a supersedes/superseded_by value, ignoring notes in parentheses."""
    value = re.sub(r"\([^)]*\)?", "", value)
    return [v.strip().removesuffix(".md") for v in re.split(r"[;,]", value)
            if v.strip() and v.strip().lower() not in ("none", "n/a", "unknown")]


def date_in(cell: str, value: str) -> bool:
    dates = ISO.findall(value or "")
    return not dates or dates[0] in cell


def check(root: Path) -> dict:
    folder = root / "3-Knowledge"
    header, rows = index_rows((folder / "_knowledge-index.md").read_text(encoding="utf-8", errors="replace")
                              if (folder / "_knowledge-index.md").is_file() else "")
    col = lambda *names: next((h for h in header if any(n in h for n in names)), None)
    c_date, c_track = col("source date"), col("track")
    c_sup, c_ver, c_rev = col("supersede"), col("last verified"), col("review by")
    mismatches, missing = [], []
    for page in sorted(folder.glob("*.md")):
        if page.name.startswith("_"):
            continue
        fm = front_matter(page.read_text(encoding="utf-8", errors="replace"))
        row = rows.get(page.name)
        if row is None:
            missing.append("| " + " | ".join([
                f"[{page.stem}](./{page.name})", fm.get("source_date", "unknown"), fm.get("track", ""),
                "<one line — write from the page>",
                "; ".join(filter(None, [f"supersedes {s}" for s in page_names(fm.get('supersedes', ''))] +
                                 [f"superseded by {s}" for s in page_names(fm.get('superseded_by', ''))])) or "—",
                fm.get("last_verified", ""), fm.get("review_by", "")]) + " |")
            continue
        problems = []
        if c_date and fm.get("source_date") and not date_in(row.get(c_date, ""), fm["source_date"]):
            problems.append(f"source date: index `{row.get(c_date)}`, page `{fm['source_date']}`")
        if c_track and "track" in fm and row.get(c_track, "") != fm["track"]:
            problems.append(f"track: index `{row.get(c_track)}`, page `{fm['track']}`")
        if c_sup:
            named = page_names(fm.get("supersedes", "")) + page_names(fm.get("superseded_by", ""))
            absent = [n for n in named if n not in row.get(c_sup, "")]
            if absent:
                problems.append(f"supersession: page names {', '.join(absent)}; the index row does not")
        if c_ver and fm.get("last_verified") and not date_in(row.get(c_ver, ""), fm["last_verified"]):
            problems.append(f"last verified: index `{row.get(c_ver)}`, page `{fm['last_verified']}`")
        if c_rev and fm.get("review_by") and not date_in(row.get(c_rev, ""), fm["review_by"]):
            problems.append(f"review by: index `{row.get(c_rev)}`, page `{fm['review_by']}`")
        if problems:
            mismatches.append({"page": page.name, "problems": problems})
    orphans = sorted(name for name in rows if not (folder / name).is_file())
    return {"mismatches": mismatches, "missing_rows": missing, "rows_without_page": orphans}


SYNC_FIELDS = {"source date": "source_date", "last verified": "last_verified", "review by": "review_by"}


def sync(root: Path) -> list[str]:
    """Copy each page's dates into its existing index row. Returns one line per changed row."""
    index = root / "3-Knowledge" / "_knowledge-index.md"
    if not index.is_file():
        return []
    lines, header, changed = index.read_text(encoding="utf-8").splitlines(), None, []
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            if cells and cells[0].lower() == "page":
                header = [c.lower() for c in cells]
            continue
        if set("".join(cells)) <= set("-: ") or len(cells) != len(header):
            continue
        link = LINK.search(cells[0])
        page = root / "3-Knowledge" / Path(link.group(2)).name if link else None
        if page is None or not page.is_file():
            continue
        fm = front_matter(page.read_text(encoding="utf-8", errors="replace"))
        before = list(cells)
        for n, name in enumerate(header):
            key = next((v for k, v in SYNC_FIELDS.items() if k in name), None)
            date = ISO.findall(fm.get(key, "")) if key else []
            if date and date[0] not in cells[n]:
                old = ISO.findall(cells[n])
                cells[n] = cells[n].replace(old[0], date[0], 1) if old else date[0]
        if cells != before:
            lines[i] = "| " + " | ".join(cells) + " |"
            changed.append(f"{page.name}: " + "; ".join(
                f"{header[n]} {before[n] or '—'} -> {cells[n]}" for n in range(len(cells)) if cells[n] != before[n]))
    if changed:
        out = "\n".join(lines) + "\n"
        rev = re.search(r"<!--\s*revision:\s*(\d+)\s*-->", out)
        if rev:
            out = out.replace(rev.group(0), f"<!-- revision: {int(rev.group(1)) + 1} -->", 1)
        out = re.sub(r"<!--\s*last-updated:\s*[^\s>]+\s*-->",
                     f"<!-- last-updated: {datetime.date.today().isoformat()} -->", out, count=1)
        tmp = index.with_name(index.name + ".tmp")
        tmp.write_text(out, encoding="utf-8", newline="")
        os.replace(tmp, index)
    return changed


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--sync", action="store_true", help="copy page dates into their existing index rows")
    ap.add_argument("--root")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    start = Path(args.root) if args.root else Path(__file__).resolve().parent
    root = find_root(start.resolve())
    if root is None:
        raise SystemExit("ERROR: no .familiar-project found at or above " + str(start))
    if args.sync:
        changed = sync(root)
        if args.json:
            print(json.dumps({"synced": changed}, indent=2))
        else:
            print(f"synced {len(changed)} index row(s)" + "".join(f"\n  {c}" for c in changed))
        return
    result = check(root)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    if not any(result.values()):
        print("knowledge index agrees with every page")
        return
    for item in result["mismatches"]:
        print(f"{item['page']}:")
        for problem in item["problems"]:
            print(f"  - {problem}")
    if result["missing_rows"]:
        print("pages with no index row (fill in the summary):")
        for row in result["missing_rows"]:
            print(f"  {row}")
    for name in result["rows_without_page"]:
        print(f"index row points at {name}, which does not exist")


if __name__ == "__main__":
    main()
