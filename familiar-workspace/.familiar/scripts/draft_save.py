#!/usr/bin/env python3
"""draft_save.py — the save path for `2-Drafts/` (`.familiar/core/file-handling.md` → Saving under `2-Drafts/`).

    python .familiar/scripts/draft_save.py next --slug S --status DRAFT --ext docx [--ai]
    python .familiar/scripts/draft_save.py register --slug S --file <path> [--note ...]
    python .familiar/scripts/draft_save.py adopt <file> --deliverable S --marker XX [--note ...]
    python .familiar/scripts/draft_save.py migrate [--dry-run]

Add `--dry-run` to see the plan without changing anything, `--json` for machine-readable output,
`--root` to name the project (default: found from this script's location).

`next` plans the version, performs the moves (v2 creates `2-Drafts/<slug>/` and moves v1 into it;
v3 and later move every earlier version, with its same-stem sidecars, to `<slug>/_superseded/`) and
prints the path to write, plus `source now at:` — where the current version sits after those moves,
which is the path a Review pass or a `--revise` must read. Run it once per new version, before
writing the file. `register` runs
after the file exists: it appends one line to `<slug>/_versions.md` (when the deliverable has a
folder) and writes the deliverable's row in `_draft-index.md`. `adopt` takes a file edited outside
familiar, does the moves, renames it to the convention with an author marker in place of `_AI`, and
registers it.

`migrate` brings a project that kept its drafts flat onto the folder layout: every deliverable with two
or more versions in the `2-Drafts/` root gets its folder, its older versions go where the rules put them,
its `_versions.md` is back-filled from the filenames and the old index rows, and the index preamble loses
the retired flat-layout rule. Run it with `--dry-run` first and show the plan before running it for real:
it moves files. It backs up `_draft-index.md` under `.familiar/backups/` first, skips a deliverable whose
file is open in Office or whose target exists, and lists the project files that still name a moved file.

It plans every move first, refuses if any target already exists, moves files before it writes the
version log and index, and never deletes or overwrites. Re-running after an interruption redoes only
what is left. Standard library only.
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
import shutil
import sys
from pathlib import Path

SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
STATUSES = ("DRAFT", "REVIEW", "FINAL")
CELL_LIMIT = 120
INDEX_HEADER = ["Deliverable", "Current file", "Version / date", "Track", "Status", "Produced by",
                "AI runtime", "Versions"]
INDEX_TEXT = ("# Drafts — Index\n\n"
              "> Human-readable list of draft deliverables, one row per deliverable. familiar updates this when it\n"
              "> creates or supersedes a draft. Keep every cell short: per-version rationale goes in the\n"
              "> deliverable's `_versions.md`, never here. Save rules: `.familiar/core/file-handling.md`.\n\n"
              "| " + " | ".join(INDEX_HEADER) + " |\n|" + "---|" * len(INDEX_HEADER) + "\n")


class Refusal(Exception):
    pass


def find_root(start: Path) -> Path | None:
    for folder in (start, *start.parents):
        if (folder / ".familiar-project").is_file():
            return folder
    return None


def version_pattern(slug: str) -> re.Pattern:
    return re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})_(?i:" + re.escape(slug) + ")" +
                      r"_(?P<status>DRAFT|REVIEW|FINAL)_v(?P<n>\d+)(?P<marker>_AI|_[A-Z]{2,4})?(?P<rest>[._].*)?$")


def scan(drafts: Path, slug: str) -> list[dict]:
    """Every file of this deliverable, wherever it currently sits."""
    pattern = version_pattern(slug)
    found = []
    for where, folder in (("flat", drafts), ("folder", drafts / slug), ("superseded", drafts / slug / "_superseded")):
        if not folder.is_dir():
            continue
        for entry in sorted(folder.iterdir()):
            m = entry.is_file() and pattern.match(entry.name)
            if m:
                found.append({"path": entry, "where": where, "n": int(m["n"]), "date": m["date"],
                              "status": m["status"], "marker": m["marker"] or "",
                              "key": (m["date"], m["status"], int(m["n"]), m["marker"] or "")})
    return found


def plan_next(drafts: Path, slug: str, status: str, ext: str, marker: str, date: str,
              ignore: Path | None = None) -> dict:
    found = [f for f in scan(drafts, slug) if f["path"] != ignore]
    n = max((f["n"] for f in found), default=0) + 1
    folder = drafts / slug
    foldered = n >= 2 or folder.is_dir()
    target_dir = folder if foldered else drafts
    target = target_dir / f"{date}_{slug}_{status}_v{n}{marker}.{ext.lstrip('.')}"
    moves = []
    for f in found:
        if f["where"] == "superseded":
            continue
        if n >= 3:
            dest = folder / "_superseded" / f["path"].name
        elif f["where"] == "flat":
            dest = folder / f["path"].name
        else:
            continue
        moves.append((f["path"], dest))
    mkdirs = []
    if foldered and not folder.is_dir():
        mkdirs.append(folder)
    if any(d.parent.name == "_superseded" for _, d in moves) and not (folder / "_superseded").is_dir():
        mkdirs.append(folder / "_superseded")
    # The current version, at the path it will have after the moves: a pass that reads its source
    # after `next` (Review, a revise) must read it there, not where it was.
    previous = None
    if found:
        top = max(found, key=lambda f: (f["n"], not f["path"].name.lower().endswith((".pdf", ".json")), f["date"]))
        moved = dict(moves)
        previous = moved.get(top["path"], top["path"])
    return {"version": n, "target": target, "moves": moves, "mkdirs": mkdirs, "previous": previous}


def check_plan(plan: dict, extra_targets: list[Path] = ()) -> None:
    seen = set()
    for dest in [d for _, d in plan["moves"]] + [plan["target"], *extra_targets]:
        if dest.exists():
            raise Refusal(f"refusing: {dest} already exists; nothing was changed")
        if dest in seen:
            raise Refusal(f"refusing: two files would land on {dest}; nothing was changed")
        seen.add(dest)


def execute_moves(plan: dict, root: Path, log: list[str]) -> None:
    for folder in plan["mkdirs"]:
        folder.mkdir(parents=True, exist_ok=True)
        log.append(f"created {folder.relative_to(root).as_posix()}/")
    for src, dest in plan["moves"]:
        os.rename(src, dest)
        log.append(f"moved {src.relative_to(root).as_posix()} -> {dest.relative_to(root).as_posix()}")


def cell(value: str, name: str, limit: int = CELL_LIMIT) -> str:
    value = re.sub(r"\s+", " ", (value or "").replace("|", "/")).strip()
    if len(value) > limit:
        raise Refusal(f"refusing: {name} is {len(value)} characters (limit {limit}); shorten it, "
                      "per-version rationale belongs in _versions.md")
    return value


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def write_atomic(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="")
    os.replace(tmp, path)


def update_versions(drafts: Path, slug: str, file: Path, note: str, found: list[dict], log: list[str]) -> bool:
    """Append this version's line to <slug>/_versions.md. A new log is back-filled from files found."""
    folder = drafts / slug
    if not folder.is_dir():
        return False
    log_path = folder / "_versions.md"
    pattern = version_pattern(slug)

    def row(name: str, rationale: str) -> str | None:
        m = pattern.match(name)
        return f"| v{int(m['n'])} | {m['date']} | {m['status']} | `{name}` | {rationale} |" if m else None

    rows, text = [], None
    if log_path.is_file():
        text = log_path.read_text(encoding="utf-8")
    else:
        order = lambda name: (name.lower().endswith((".pdf", ".json")), len(name), name)
        groups = {}
        for f in found:
            groups.setdefault(f["key"], []).append(f["path"].name)
        mine = next((f["key"] for f in found if f["path"].name == file.name), None)
        rows = [row(min(groups[k], key=order), "—") for k in sorted(groups, key=lambda k: (k[2], k[0]))
                if k != mine]
    if text is None or f"`{file.name}`" not in text:
        rows.append(row(file.name, cell(note, "note") or "—"))
    rows = [r for r in rows if r]
    if text is None:
        text = (f"# {slug} — versions\n\n| Version | Date | Status | File | Rationale |\n|---|---|---|---|---|\n")
    elif not rows:
        return True
    elif not text.endswith("\n"):
        text += "\n"
    write_atomic(log_path, text + "".join(r + "\n" for r in rows))
    log.append(f"updated {log_path.relative_to(drafts.parent).as_posix()} (+{len(rows)})")
    return True


def update_index(drafts: Path, slug: str, file: Path, title: str, track: str, produced_by: str, runtime: str,
                 has_log: bool, log: list[str]) -> None:
    index = drafts / "_draft-index.md"
    text = index.read_text(encoding="utf-8") if index.is_file() else INDEX_TEXT
    pattern = version_pattern(slug)
    m = pattern.match(file.name)
    rel = file.relative_to(drafts).as_posix()
    row = [cell(title or slug, "deliverable"), f"`{cell(rel, 'file', 200)}`", f"v{int(m['n'])} / {m['date']}",
           cell(track, "track"), m["status"], cell(produced_by, "produced by"), cell(runtime, "AI runtime"),
           f"[history]({slug}/_versions.md)" if has_log else ""]
    new_line = "| " + " | ".join(row) + " |"
    lines, replaced = text.splitlines(), False
    for i, line in enumerate(lines):
        if not line.startswith("|") or set(line) <= set("|-: "):
            continue
        cells = split_row(line)
        current = Path(cells[1].strip("`")) if len(cells) > 1 else Path()
        if cells and (cells[0] in (title, slug) or current.parts[:1] == (slug,) or pattern.match(current.name)):
            if replaced:
                raise Refusal(f"refusing: the index has two rows for {slug}; fix it by hand first")
            kept = list(row)
            if not title:
                kept[0] = cells[0]
            # A flag left out keeps the cell's existing value: a register run without
            # --produced-by must not blank the provenance an earlier run recorded.
            for n in (3, 5, 6):
                if not kept[n] and len(cells) > n:
                    kept[n] = cells[n]
            lines[i], replaced = "| " + " | ".join(kept) + " |", True
    if not replaced:
        lines = [l for l in lines if not l.lstrip().startswith("| _(none yet)_")]
        while lines and not lines[-1].strip():
            lines.pop()
        lines.append(new_line)
    write_atomic(index, "\n".join(lines) + "\n")
    log.append(f"{'updated' if replaced else 'added'} index row for {row[0]}")


def do_next(args, root: Path, drafts: Path, log: list[str]) -> dict:
    marker = "_AI" if args.ai else ""
    plan = plan_next(drafts, args.slug, args.status, args.ext, marker, args.date)
    check_plan(plan)
    if not args.dry_run:
        execute_moves(plan, root, log)
    return plan


def do_register(args, root: Path, drafts: Path, log: list[str]) -> None:
    file = Path(args.file).resolve()
    if not file.is_file():
        raise Refusal(f"refusing: {file} does not exist; write the file before registering it")
    if drafts.resolve() not in file.parents:
        raise Refusal("refusing: the file is not under 2-Drafts/")
    file = drafts / file.relative_to(drafts.resolve())
    if not version_pattern(args.slug).match(file.name):
        raise Refusal(f"refusing: {file.name} does not match YYYY-MM-DD_{args.slug}_<STATUS>_vN[_marker].<ext>")
    if args.dry_run:
        log.append(f"would register {file.relative_to(drafts).as_posix()}")
        return
    has_log = update_versions(drafts, args.slug, file, args.note, scan(drafts, args.slug), log)
    update_index(drafts, args.slug, file, args.title, args.track, args.produced_by, args.ai_runtime, has_log, log)


def adopt_note(note: str, original: str) -> str:
    """The version-log note for an adopted file, always within the cell limit: the original name is
    the part that must survive, so a long one is shortened in the middle rather than refused."""
    head = f"{note or 'adopted external edit'} (original name: "
    room = CELL_LIMIT - len(head) - 1
    if room < 12:
        head, room = "adopted (original name: ", CELL_LIMIT - len("adopted (original name: ") - 1
    name = original if len(original) <= room else original[:room // 2 - 1] + "…" + original[-(room - room // 2):]
    return head + name + ")"


def do_adopt(args, root: Path, drafts: Path, log: list[str]) -> dict | None:
    src = Path(args.file)
    src = (src if src.is_absolute() else Path.cwd() / src).resolve()
    log_path = drafts / args.deliverable / "_versions.md"
    if not src.exists():
        recorded = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
        if f"original name: {src.name})" in recorded or adopt_note(args.note, src.name) in recorded:
            log.append(f"already adopted: {src.name} is recorded in {log_path.relative_to(root).as_posix()}")
            return None
        raise Refusal(f"refusing: {src} does not exist")
    if drafts.resolve() not in src.resolve().parents:
        raise Refusal("refusing: an adopted file must already be under 2-Drafts/")
    if "_superseded" in src.resolve().parts:
        raise Refusal("refusing: that file is already in _superseded/")
    marker = "_" + args.marker.upper()
    if not re.fullmatch(r"_[A-Z]{2,4}", marker) or marker == "_AI":
        raise Refusal("refusing: --marker must be the editor's 2-4 initials, and not AI")
    plan = plan_next(drafts, args.deliverable, args.status, src.suffix, marker, args.date, ignore=src)
    check_plan(plan)
    # Validate every register input before anything moves (review 2026-10-10, R3): a refusal after
    # the rename used to leave a renamed, unregistered file and a re-run that could not find it.
    args.note = adopt_note(args.note, src.name)
    for value, name in ((args.note, "note"), (args.title, "title"), (args.track, "track"),
                        (args.produced_by, "produced by"), (args.ai_runtime, "AI runtime")):
        cell(value, name)
    if args.dry_run:
        log.append(f"would rename {src.name} -> {plan['target'].relative_to(root).as_posix()}")
        return plan
    execute_moves(plan, root, log)
    if not plan["target"].parent.is_dir():
        plan["target"].parent.mkdir(parents=True)
    os.rename(src, plan["target"])
    log.append(f"renamed {src.relative_to(root.resolve()).as_posix()} -> {plan['target'].relative_to(root).as_posix()}")
    args.file = str(plan["target"])
    args.slug = args.deliverable
    do_register(args, root, drafts, log)
    return plan


FILE_NAME = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})_(?P<slug>.+?)_(?P<status>DRAFT|REVIEW|FINAL)_v(?P<n>\d+)"
                       r"(?P<marker>_AI|_[A-Z]{2,4})?(?P<rest>[._].*)?$")
RETIRED_RULE = re.compile(r"[\s>]+".join(
    [re.escape(w) for w in "Keep files flat while the list is small; create one folder per deliverable only after".split()]
    + [r"\w+"] + [re.escape(w) for w in "versions or when this directory exceeds twenty draft files.".split()]))
NEW_RULE = ("A deliverable's second version creates its own folder (`draft_save.py` does it). Per-version\n"
            "> rationale goes in the deliverable's `_versions.md`, never here.")
REFERENCE_SUFFIXES = (".md", ".txt", ".csv", ".json")
REFERENCE_SKIP = {"2-Drafts", ".git", ".scratch", "_del", "node_modules", "__pycache__", "backups"}


def locked_names(drafts: Path) -> set[str]:
    """Names of files an Office lock file (`~$...`) says are open."""
    rests = [e.name[2:] for e in drafts.iterdir() if e.name.startswith("~$")]
    return {e.name for e in drafts.iterdir() if e.is_file()
            and any(e.name == r or e.name[2:] == r or (len(r) >= len(e.name) - 3 and e.name.endswith(r)) for r in rests)}


def plan_migration(drafts: Path) -> tuple[list[dict], list[str]]:
    """One plan per deliverable with two or more versions that still has files in the root."""
    slugs = set()
    for entry in sorted(drafts.iterdir()):
        m = entry.is_file() and FILE_NAME.match(entry.name)
        if m:
            slugs.add(m["slug"].lower())
    plans, skipped = [], []
    locked = locked_names(drafts)
    for slug in sorted(slugs):
        if not SLUG.match(slug):
            if len({FILE_NAME.match(e.name)["n"] for e in drafts.iterdir()
                    if e.is_file() and FILE_NAME.match(e.name) and FILE_NAME.match(e.name)["slug"].lower() == slug}) > 1:
                skipped.append(f"{slug}: not a lowercase hyphenated slug; left flat")
            continue
        found = scan(drafts, slug)
        if not any(f["where"] == "flat" for f in found) or len({f["n"] for f in found}) < 2:
            continue
        current = max(f["n"] for f in found)
        folder = drafts / slug
        moves = []
        for f in found:
            if f["where"] == "superseded":
                continue
            if f["n"] < current and current >= 3:
                dest = folder / "_superseded" / f["path"].name
            elif f["where"] == "flat":
                dest = folder / f["path"].name
            else:
                continue
            moves.append((f["path"], dest))
        busy = [s.name for s, _ in moves if s.name in locked]
        clash = [d.name for _, d in moves if d.exists()]
        if busy:
            skipped.append(f"{slug}: {busy[0]} is open in Office; close it and run migrate again")
        elif clash:
            skipped.append(f"{slug}: {clash[0]} already exists in the target; resolve it by hand")
        else:
            mkdirs = [d for d in (folder, folder / "_superseded")
                      if not d.is_dir() and any(dest.parent == d for _, dest in moves)]
            plans.append({"slug": slug, "found": found, "current": current, "moves": moves,
                          "mkdirs": mkdirs, "folder": folder})
    return plans, skipped


def short_title(text: str) -> str:
    text = re.sub(r"\s+", " ", text.replace("|", "/")).strip()
    if len(text) <= CELL_LIMIT:
        return text
    for mark in (" (", ": ", " — ", "; ", ". "):
        at = text.find(mark, 20)
        if 0 < at <= CELL_LIMIT:
            return text[:at].rstrip(" ,;:")
    return text[:CELL_LIMIT - 1].rstrip(" ,;:") + "…"


def deliverable_title(text: str, slug: str) -> str:
    """The name of the deliverable from an old row that also described one version of it."""
    head = re.split(r"[:(;—]|\s-\s", re.sub(r"\s+", " ", text), maxsplit=1)[0]
    head = re.sub(r"\s+v\d+$", "", head.strip(" ,"))
    return short_title(head) if len(head) >= 8 else short_title(text) or slug


def file_cell(cell_text: str) -> str:
    link = re.search(r"\]\(([^)]+)\)", cell_text)
    return (link[1] if link else cell_text).strip().strip("`").replace("%20", " ")


def rewrite_index(drafts: Path, plans: list[dict], log: list[str]) -> dict:
    """Fold each migrated deliverable's rows into one and point it at its folder. Returns the old
    rows' text per (slug, version), which becomes the rationale in `_versions.md`."""
    index = drafts / "_draft-index.md"
    rationale = {}
    if not index.is_file():
        return rationale
    text = index.read_text(encoding="utf-8")
    lines = text.splitlines()
    head = next((i for i, l in enumerate(lines) if l.startswith("|") and len(l.split("|")) > 2
                 and l.split("|")[1].strip().lower().startswith("deliverable")), None)
    by_slug = {p["slug"]: p for p in plans}
    if head is not None and plans:
        cols = [c.strip().lower() for c in split_row(lines[head])]
        col = lambda *names: next((i for i, c in enumerate(cols) if any(c.startswith(n) for n in names)), None)
        c_title, c_file, c_ver, c_status = col("deliverable"), col("current"), col("version"), col("status")
        c_sup, c_hist = col("superseded"), col("versions")
        rows = {}
        for i in range(head + 2, len(lines)):
            if not lines[i].startswith("|"):
                continue
            cells = split_row(lines[i])
            if c_file is None or len(cells) <= c_file:
                continue
            name = Path(file_cell(cells[c_file])).name
            m = FILE_NAME.match(name)
            if m and m["slug"].lower() in by_slug:
                slug = m["slug"].lower()
                rationale[(slug, int(m["n"]))] = re.sub(r"\s+", " ", cells[c_title].replace("|", "/")).strip()
                rows.setdefault(slug, []).append((int(m["n"]), i, cells))
        drop = set()
        for slug, entries in rows.items():
            plan = by_slug[slug]
            latest = max(plan["found"], key=lambda f: (f["n"], f["date"]))
            keep = max(entries, key=lambda e: (e[0], e[1]))
            drop.update(i for _, i, _ in entries if i != keep[1])
            cells = keep[2]
            cells[c_file] = f"`{slug}/{latest['path'].name}`"
            cells[c_title] = deliverable_title(cells[c_title], slug)
            if c_ver is not None and len(cells) > c_ver:
                cells[c_ver] = f"v{latest['n']} / {latest['date']}"
            if c_status is not None and len(cells) > c_status:
                cells[c_status] = latest["status"]
            link = f"[history]({slug}/_versions.md)"
            for c in (c_hist, c_sup):
                if c is not None and len(cells) > c:
                    cells[c] = link
                    break
            lines[keep[1]] = "| " + " | ".join(cells) + " |"
            if keep[0] != latest["n"]:
                log.append(f"note: the index row for {slug} described v{keep[0]}; v{latest['n']} is current")
        lines = [l for i, l in enumerate(lines) if i not in drop]
        end = max((i for i in range(head + 2, len(lines)) if lines[i].startswith("|")), default=head + 1)
        for plan in plans:
            if plan["slug"] in rows:
                continue
            latest = max(plan["found"], key=lambda f: (f["n"], f["date"]))
            new = [""] * len(cols)
            for c, value in ((c_title, plan["slug"]), (c_file, f"`{plan['slug']}/{latest['path'].name}`"),
                             (c_ver, f"v{latest['n']} / {latest['date']}"), (c_status, latest["status"]),
                             (c_hist if c_hist is not None else c_sup, f"[history]({plan['slug']}/_versions.md)")):
                if c is not None:
                    new[c] = value
            lines.insert(end + 1, "| " + " | ".join(new) + " |")
            end += 1
            log.append(f"note: {plan['slug']} had no index row; added a bare one, fill in the name and track")
    new_text = RETIRED_RULE.sub(lambda _: NEW_RULE, "\n".join(lines) + "\n")
    if new_text != text:
        write_atomic(index, new_text)
        log.append("updated _draft-index.md (rows folded, retired flat-layout rule replaced)")
    return rationale


def write_versions(plan: dict, rationale: dict, log: list[str]) -> None:
    drafts, slug = plan["folder"].parent, plan["slug"]
    where = plan["folder"] / "_versions.md"
    pattern = version_pattern(slug)
    groups = {}
    for f in scan(drafts, slug):
        groups.setdefault(f["key"], []).append(f["path"].name)
    order = lambda name: (name.lower().endswith((".pdf", ".json")), len(name), name)
    text = where.read_text(encoding="utf-8") if where.is_file() else (
        f"# {slug} — versions\n\n| Version | Date | Status | File | Rationale |\n|---|---|---|---|---|\n")
    added = 0
    for key in sorted(groups, key=lambda k: (k[2], k[0])):
        name = min(groups[key], key=order)
        if f"`{name}`" in text:
            continue
        m = pattern.match(name)
        if not text.endswith("\n"):
            text += "\n"
        text += f"| v{int(m['n'])} | {m['date']} | {m['status']} | `{name}` | {rationale.get((slug, int(m['n'])), '—')} |\n"
        added += 1
    if added:
        write_atomic(where, text)
        log.append(f"wrote {where.relative_to(drafts.parent).as_posix()} (+{added})")


def find_references(root: Path, names: list[str]) -> dict:
    hits = {}
    for here, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in REFERENCE_SKIP]
        for name in files:
            path = Path(here) / name
            if path.suffix.lower() not in REFERENCE_SUFFIXES or path.stat().st_size > 4_000_000:
                continue
            try:
                body = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            count = sum(body.count(n) for n in names if n in body)
            if count:
                hits[path.relative_to(root).as_posix()] = count
    return hits


def do_migrate(args, root: Path, drafts: Path, log: list[str]) -> dict:
    plans, skipped = plan_migration(drafts)
    names = sorted({s.name for p in plans for s, _ in p["moves"]})
    if args.dry_run:
        for p in plans:
            log.append(f"would fold {p['slug']}: {len(p['moves'])} file(s) move, current v{p['current']}")
        log.extend("would skip " + s for s in skipped)
        return {"plans": plans, "skipped": skipped, "references": find_references(root, names) if names else {}}
    if not plans:
        log.extend("skipped " + s for s in skipped)
        # Still retire the old preamble rule, which misleads whoever reads the index.
        rewrite_index(drafts, [], log)
        return {"plans": [], "skipped": skipped, "references": {}}
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    saved = root / ".familiar" / "backups" / f"{stamp}-drafts-migration" / "2-Drafts"
    saved.mkdir(parents=True)
    index = drafts / "_draft-index.md"
    if index.is_file():
        shutil.copy2(index, saved / index.name)
    (saved / "moves.txt").write_text("".join(f"{s.relative_to(root).as_posix()} -> {d.relative_to(root).as_posix()}\n"
                                             for p in plans for s, d in p["moves"]), encoding="utf-8")
    log.append(f"backed up the index and the move list to {saved.parent.relative_to(root).as_posix()}/")
    done = []
    for p in plans:
        moved = []
        try:
            for folder in p["mkdirs"]:
                folder.mkdir(parents=True, exist_ok=True)
            for src, dest in p["moves"]:
                os.rename(src, dest)
                moved.append((src, dest))
        except OSError as e:
            for src, dest in reversed(moved):
                os.rename(dest, src)
            skipped.append(f"{p['slug']}: {e}; its files were put back")
            continue
        log.append(f"folded {p['slug']}: {len(moved)} file(s), current v{p['current']}")
        done.append(p)
    rationale = rewrite_index(drafts, done, log)
    for p in done:
        write_versions(p, rationale, log)
    log.extend("skipped " + s for s in skipped)
    moved_names = sorted({s.name for p in done for s, _ in p["moves"]})
    return {"plans": done, "skipped": skipped, "references": find_references(root, moved_names) if moved_names else {}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root")
    common.add_argument("--dry-run", action="store_true")
    common.add_argument("--json", action="store_true")
    common.add_argument("--date", default=datetime.date.today().isoformat())
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("next", parents=[common])
    n.add_argument("--slug", required=True)
    n.add_argument("--status", default="DRAFT", choices=STATUSES)
    n.add_argument("--ext", required=True)
    n.add_argument("--ai", action="store_true")
    r = sub.add_parser("register", parents=[common])
    a = sub.add_parser("adopt", parents=[common])
    sub.add_parser("migrate", parents=[common])
    r.add_argument("--slug", required=True)
    r.add_argument("--file", required=True)
    a.add_argument("file")
    a.add_argument("--deliverable", required=True)
    a.add_argument("--marker", required=True)
    a.add_argument("--status", default="DRAFT", choices=STATUSES)
    for p in (r, a):
        p.add_argument("--note", default="")
        p.add_argument("--title", default="")
        p.add_argument("--track", default="")
        p.add_argument("--produced-by", default="")
        p.add_argument("--ai-runtime", default="")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    slug = getattr(args, "slug", None) or getattr(args, "deliverable", None)
    if args.cmd != "migrate" and not SLUG.match(slug):
        raise SystemExit(f"ERROR: slug `{slug}` must be lowercase words joined by hyphens")
    start = Path(args.root) if args.root else Path(__file__).resolve().parent
    root = find_root(start.resolve())
    if root is None:
        raise SystemExit("ERROR: no .familiar-project found at or above " + str(start))
    drafts = root / "2-Drafts"
    if not drafts.is_dir():
        raise SystemExit("ERROR: no 2-Drafts/ folder in " + str(root))
    log: list[str] = []
    plan = migration = None
    try:
        if args.cmd == "migrate":
            migration = do_migrate(args, root, drafts, log)
        elif args.cmd == "next":
            plan = do_next(args, root, drafts, log)
        elif args.cmd == "register":
            do_register(args, root, drafts, log)
        else:
            plan = do_adopt(args, root, drafts, log)
    except Refusal as e:
        raise SystemExit(f"ERROR: {e}")
    result = {"dry_run": args.dry_run, "steps": log}
    if migration is not None:
        result.update(folded=[p["slug"] for p in migration["plans"]], skipped=migration["skipped"],
                      moves=[[a.relative_to(root).as_posix(), b.relative_to(root).as_posix()]
                             for p in migration["plans"] for a, b in p["moves"]],
                      references=migration["references"])
        if args.json:
            print(json.dumps(result, indent=2))
            return
        for line in log:
            print(line)
        if args.dry_run:
            for a, b in result["moves"]:
                print(f"would move {a} -> {b}")
        if result["references"]:
            print(f"{len(result['references'])} project file(s) still name a moved file (not edited):")
            for path, count in sorted(result["references"].items()):
                print(f"  {path} ({count})")
        if not (migration["plans"] or migration["skipped"]):
            print("nothing to migrate")
        return
    if plan:
        result.update(version=plan["version"], target=plan["target"].relative_to(root).as_posix(),
                      mkdirs=[d.relative_to(root).as_posix() for d in plan["mkdirs"]],
                      moves=[[s.relative_to(root).as_posix(), d.relative_to(root).as_posix()] for s, d in plan["moves"]],
                      previous=plan["previous"].relative_to(root).as_posix() if plan.get("previous") else None)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    if plan and args.dry_run:
        for d in result["mkdirs"]:
            print(f"would create {d}/")
        for s, d in result["moves"]:
            print(f"would move {s} -> {d}")
    for line in log:
        print(line)
    if plan and args.cmd == "next":
        if result.get("previous"):
            print(f"source now at: {result['previous']}")
        print(f"write: {result['target']}")
    elif plan:
        print(f"version: v{result['version']} -> {result['target']}")


if __name__ == "__main__":
    main()
