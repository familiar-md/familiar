#!/usr/bin/env python3
"""source_register.py — the project's ledger of input files and what ingest did with each one.

    python source_register.py scan                      # read-only receipt of 1-Inputs/
    python source_register.py scan --json
    python source_register.py record PATH --status ingested --page 3-Knowledge/X.md \\
        [--id SOURCE-ID] [--role source] [--role template] [--supersedes VERSION] [--note TEXT]

Run from anywhere inside the project; the project root is the nearest parent holding
`.familiar-project`. Standard library only.

The register is `3-Knowledge/_source-register.md`, a Markdown table a person can read and edit. It
answers "what has been ingested?", which the knowledge index cannot: the index lists pages, not
inputs, and says nothing about a file that was read, skipped, failed, or never touched.

One row per *version*. A version is identified by the SHA-256 of the file's bytes (the first 12
hex digits shown), the same fingerprint the PDF extraction cache records in its header. A logical
source keeps one `Source ID` across versions.

`scan` compares 1-Inputs/ against the register and sorts every file into:
  unchanged     same path, same bytes as a recorded version — nothing to do
  incomplete    same bytes as a version recorded `partial` or `failed` — resume it
  alias         same bytes as a recorded version, different path — a rename or copy, not new work
  changed       a recorded path whose bytes differ — a possible revision; confirm before re-ingesting
  new           never recorded
  missing       a recorded path that no longer exists (reported, never removed from the register)
It writes nothing.

`record` adds or updates one row after an ingest (or a skip, failure, or partial run). Recording a
file whose bytes match an existing row adds the path as an alias of that row instead of a new row.
`--supersedes <version>` marks that earlier version's row `superseded`. Nothing else in the file
changes, and the revision comment is incremented.
"""

# familiar's floor is Python 3.10. On anything older, stop with a plain message instead of a traceback.
import sys
if sys.version_info < (3, 10):
    sys.exit("familiar needs Python 3.10 or newer, but this is Python %d.%d (%s). Install Python 3.10+ "
             "(.familiar/scripts/doctor.py says how), then run this again with it." % (*sys.version_info[:2], sys.executable))

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

REGISTER = Path("3-Knowledge") / "_source-register.md"
INPUTS = Path("1-Inputs")
COLUMNS = ["Source ID", "Version", "Path", "Aliases", "Roles", "Status", "Knowledge page",
           "Supersedes", "Last processed", "Note"]
STATUSES = {"read", "ingested", "partial", "failed", "skipped", "superseded"}
ROLES = {"source", "template", "example", "admin"}
FOLDER_ROLE = {"sources": "source", "templates": "template", "examples": "example", "admin": "admin"}
REVISION = re.compile(r"<!--\s*revision:\s*(\d+)\s*-->")
LAST_UPDATED = re.compile(r"<!--\s*last-updated:\s*[^>]*-->")
# `_about.md` in each input folder is release prose describing the folder, not an input.
SKIP_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini", "_about.md"}

HEADER = """<!-- familiar-state-schema: 1.0 -->
<!-- revision: 0 -->
<!-- last-updated: not-yet-written -->
# Source Register

Every input file and what ingest did with it. Maintained by
the ingest skill's `scripts/source_register.py` (`.familiar/core/ingest.md` → Ingest procedure); edit a
row by hand only to correct it. One row per version: `Version` is the first 12 hex digits of the
file's SHA-256. `Status` is read, ingested, partial, failed, skipped, or superseded. `Roles` is any
of source, template, example, admin.

"""


def find_root(start: Path) -> Path | None:
    for folder in (start, *start.parents):
        if (folder / ".familiar-project").is_file():
            return folder
    return None


def fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()[:12]


def cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def load(root: Path):
    """Returns (text, rows). Rows are dicts keyed by COLUMNS; unknown columns are kept verbatim."""
    path = root / REGISTER
    text = path.read_text(encoding="utf-8") if path.is_file() else HEADER
    rows, header = [], None
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
        if header is None:
            header = cells
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        rows.append(dict(zip(header, cells)))
    return text, rows


def render(text: str, rows: list[dict], today: str) -> str:
    before_table = text.split("\n|", 1)[0].rstrip("\n") + "\n\n"
    rev = REVISION.search(before_table)
    number = int(rev.group(1)) + 1 if rev else 1
    before_table = REVISION.sub(f"<!-- revision: {number} -->", before_table, count=1) if rev else \
        f"<!-- revision: {number} -->\n" + before_table
    before_table = LAST_UPDATED.sub(f"<!-- last-updated: {today} -->", before_table, count=1)
    lines = ["| " + " | ".join(COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
    for row in rows:
        lines.append("| " + " | ".join(cell(row.get(c, "")) for c in COLUMNS) + " |")
    return before_table + "\n".join(lines) + "\n"


def write_atomic(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".register-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def input_files(root: Path):
    folder = root / INPUTS
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.rglob("*")
                  if p.is_file() and p.name not in SKIP_NAMES and not p.name.startswith("~$"))


def paths_of(row: dict) -> list[str]:
    aliases = [a.strip() for a in row.get("Aliases", "").split(";") if a.strip()]
    return [row.get("Path", "")] + aliases


def scan(root: Path) -> dict:
    _, rows = load(root)
    by_version = {row["Version"]: row for row in rows if row.get("Version")}
    by_path = {}
    for row in rows:
        for p in paths_of(row):
            by_path.setdefault(p, []).append(row)
    receipt = {k: [] for k in ("unchanged", "incomplete", "alias", "changed", "new", "missing")}
    seen = set()
    for path in input_files(root):
        rel = path.relative_to(root).as_posix()
        seen.add(rel)
        version = fingerprint(path)
        recorded_here = by_path.get(rel, [])
        match = next((r for r in recorded_here if r.get("Version") == version), None)
        if match is not None:
            if match.get("Status") in ("partial", "failed"):
                receipt["incomplete"].append({"path": rel, "version": version, "status": match.get("Status"),
                                              "source_id": match.get("Source ID"), "note": match.get("Note", "")})
            else:
                receipt["unchanged"].append({"path": rel, "version": version})
        elif version in by_version:
            row = by_version[version]
            receipt["alias"].append({"path": rel, "version": version, "of": row.get("Path"),
                                     "source_id": row.get("Source ID")})
        elif recorded_here:
            latest = recorded_here[-1]
            receipt["changed"].append({"path": rel, "version": version, "was": latest.get("Version"),
                                       "source_id": latest.get("Source ID")})
        else:
            receipt["new"].append({"path": rel, "version": version})
    for row in rows:
        if row.get("Status") == "superseded":
            continue
        for p in paths_of(row):
            if p and p not in seen:
                receipt["missing"].append({"path": p, "version": row.get("Version"),
                                           "source_id": row.get("Source ID")})
    return receipt


def suggest_role(rel: str) -> str:
    parts = [p.lower() for p in Path(rel).parts]
    for part in parts[1:-1]:
        if part in FOLDER_ROLE:
            return FOLDER_ROLE[part]
    return "source"


def slug(rel: str) -> str:
    stem = Path(rel).stem
    return re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-")[:60] or "source"


def record(root: Path, args) -> str:
    target = Path(args.path)
    target = target if target.is_absolute() else (Path.cwd() / target)
    if not target.is_file():
        target = root / args.path
    if not target.is_file():
        raise SystemExit(f"ERROR: no such file: {args.path}")
    rel = target.resolve().relative_to(root.resolve()).as_posix()
    if not rel.startswith(INPUTS.as_posix() + "/"):
        raise SystemExit(f"ERROR: {rel} is not under {INPUTS.as_posix()}/")
    if args.status not in STATUSES:
        raise SystemExit(f"ERROR: --status must be one of {', '.join(sorted(STATUSES))}")
    roles = args.role or [suggest_role(rel)]
    bad = [r for r in roles if r not in ROLES]
    if bad:
        raise SystemExit(f"ERROR: unknown role(s) {bad}; use {', '.join(sorted(ROLES))}")

    text, rows = load(root)
    version = fingerprint(target)
    today = date.today().isoformat()
    existing = next((r for r in rows if r.get("Version") == version), None)
    if existing is not None:
        if rel not in paths_of(existing):
            existing["Aliases"] = "; ".join([a for a in paths_of(existing)[1:]] + [rel])
            action = f"added {rel} as an alias of {existing['Source ID']} @ {version}"
        else:
            action = f"updated {existing['Source ID']} @ {version}"
        existing["Status"] = args.status
        existing["Last processed"] = today
        if args.page:
            existing["Knowledge page"] = args.page
        if args.role:
            existing["Roles"] = ", ".join(roles)
        if args.note:
            existing["Note"] = args.note
    else:
        source_id = args.id
        if source_id is None and args.supersedes:
            prior = next((r for r in rows if r.get("Version") == args.supersedes), None)
            source_id = prior.get("Source ID") if prior else None
        source_id = source_id or slug(rel)
        rows.append({"Source ID": source_id, "Version": version, "Path": rel, "Aliases": "",
                     "Roles": ", ".join(roles), "Status": args.status, "Knowledge page": args.page or "",
                     "Supersedes": args.supersedes or "", "Last processed": today, "Note": args.note or ""})
        action = f"recorded {source_id} @ {version} ({args.status})"
    if args.supersedes:
        prior = next((r for r in rows if r.get("Version") == args.supersedes), None)
        if prior is None:
            raise SystemExit(f"ERROR: --supersedes {args.supersedes}: no row with that version")
        prior["Status"] = "superseded"
        action += f"; marked {args.supersedes} superseded"
    write_atomic(root / REGISTER, render(text, rows, today))
    return action


def print_receipt(receipt: dict):
    counts = {k: len(v) for k, v in receipt.items()}
    total = sum(counts[k] for k in ("unchanged", "incomplete", "alias", "changed", "new"))
    print(f"{total} input file(s): {counts['unchanged']} already processed and unchanged, "
          f"{counts['incomplete']} incomplete, {counts['new']} new, {counts['changed']} possible "
          f"revision(s), {counts['alias']} renamed/copied, {counts['missing']} recorded but missing")
    for item in receipt["incomplete"]:
        print(f"  incomplete {item['path']}  ({item['source_id']}: {item['status']}"
              + (f"; {item['note']}" if item["note"] else "") + ") -- resume, do not start over")
    for item in receipt["new"]:
        print(f"  new       {item['path']}  ({item['version']})")
    for item in receipt["changed"]:
        print(f"  changed   {item['path']}  ({item['was']} -> {item['version']}; {item['source_id']}) "
              "-- confirm it is a revision before re-ingesting")
    for item in receipt["alias"]:
        print(f"  alias     {item['path']}  = {item['of']} ({item['source_id']}) -- same bytes, "
              "do not synthesize again")
    for item in receipt["missing"]:
        print(f"  missing   {item['path']}  ({item['source_id']})")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--json", action="store_true")
    s.add_argument("--root")
    r = sub.add_parser("record")
    r.add_argument("path")
    r.add_argument("--status", required=True)
    r.add_argument("--page")
    r.add_argument("--id")
    r.add_argument("--role", action="append")
    r.add_argument("--supersedes")
    r.add_argument("--note")
    r.add_argument("--root")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    root = find_root(Path(args.root).resolve() if args.root else Path.cwd().resolve())
    if root is None:
        raise SystemExit("ERROR: no .familiar-project at or above the current folder")
    if args.command == "scan":
        receipt = scan(root)
        if args.json:
            print(json.dumps(receipt, indent=2))
        else:
            print_receipt(receipt)
    else:
        print(record(root, args))


if __name__ == "__main__":
    main()
