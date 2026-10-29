#!/usr/bin/env python3
"""update.py — bring an existing familiar project up to this release, in place.

    python .familiar/scripts/update.py --project . --from _update [--apply]
    python <new familiar-workspace folder>/.familiar/scripts/update.py --project "<project>"
    python <new familiar-workspace folder>/.familiar/scripts/update.py --project "<project>" --apply
    ... --extension "<new extension drop-in folder>"     # repeatable; updates that extension too

The usual way is `--from`: the user drops the downloaded zips (core, any extension, the hooks
package) into the project's `_update/` folder, unzipped or not, and `/system-settings` → Update runs
the project's own copy with `--from _update`. It unpacks the zips into a temporary folder outside the
project, finds each release in them by its manifest (the newest one per owner, if several), and
hands over to the NEW core release's copy of this script, or, with no core release among them,
updates just the extensions against the project's current core. A session never has to read outside
the project (CORE-WORKSPACE-SILO). Without `--from`, run the NEW release's copy against the project;
its default release is the folder it sits in, and `--release` names another. Report only unless
`--apply`.

It decides file by file against the project's own release manifests
(`.familiar/release-manifests/<owner>.json`, one per owner: core is `familiar`, each extension its
own id), which record what the release that last wrote each file shipped:

  same      the project's copy already matches the new release
  update    the project's copy still matches what its old release shipped, so replacing it loses nothing
  diverged  it matches neither: someone edited it. Left alone and reported
  add       the new release has it and the project does not
  retired   the old release shipped it and the new one does not. An untouched copy is moved into the
            update's backup folder, so a retired skill stops loading and nothing is lost
            (CORE-NO-DELETE); an edited one is left in place and reported

The entry files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) are compared and replaced only between
their `<!-- familiar:start -->` / `<!-- familiar:end -->` markers; text outside them is the user's.
Project data is never in a manifest, so it is never read or written.

It stops before writing anything when the two `.familiar-project` files name different
`state-schema:` versions (a migration, not an update), when the project has no core manifest, or
when a release file no longer matches its own manifest. An extension installed in the project with
no `--extension` source is reported and left unchanged; its declared `core` range is checked
against the new version either way.

`--apply` first copies every file it will replace into
`5-System/_update-backups/<old>-to-<new>_<date>/`, then writes, then sets only the
`familiar-version:` line of `.familiar-project`, then replaces each updated owner's manifest, and
finally runs the project's `project_check.py`. Re-running is safe: a second run finds everything
`same`. Standard library only.
"""

# familiar's floor is Python 3.10. On anything older, stop with a plain message instead of a traceback.
import sys
if sys.version_info < (3, 10):
    sys.exit("familiar needs Python 3.10 or newer, but this is Python %d.%d (%s). Install Python 3.10+ "
             "(.familiar/scripts/doctor.py says how), then run this again with it." % (*sys.version_info[:2], sys.executable))

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

MANIFEST_DIR = ".familiar/release-manifests"
BLOCK_START = "<!-- familiar:start -->"
BLOCK_END = "<!-- familiar:end -->"
BACKUP_DIR = "5-System/_update-backups"


class Stop(Exception):
    """A reason to write nothing at all."""


# --- fingerprints: the same rules the release build uses to write the manifests ----------------
def fingerprint(data: bytes) -> str:
    # CRLF folded to LF for text, so a line-ending change is not mistaken for an edit.
    return hashlib.sha256(data if b"\0" in data[:8000] else data.replace(b"\r\n", b"\n")).hexdigest()


def block_of(text: str):
    """The familiar block, markers inclusive, LF line endings; None without exactly one."""
    text = text.replace("\r\n", "\n")
    if text.count(BLOCK_START) != 1 or text.count(BLOCK_END) != 1:
        return None
    start, end = text.index(BLOCK_START), text.index(BLOCK_END)
    return text[start:end + len(BLOCK_END)] if start < end else None


def block_fingerprint(path: Path):
    block = block_of(path.read_bytes().decode("utf-8"))
    return None if block is None else fingerprint(block.encode("utf-8"))


def splice_block(project_text: str, release_text: str) -> str:
    """The project's file with its familiar block replaced by the release's, newlines kept."""
    old, new = block_of(project_text), block_of(release_text)
    if old is None or new is None:
        raise ValueError("both files need exactly one familiar block")
    newline = "\r\n" if "\r\n" in project_text else "\n"
    return project_text.replace("\r\n", "\n").replace(old, new, 1).replace("\n", newline)


# --- small readers --------------------------------------------------------------------------
def marker_field(root: Path, key: str) -> str:
    path = root / ".familiar-project"
    if not path.is_file():
        raise Stop(f"{root} has no .familiar-project")
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def load_manifest(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def version_tuple(text: str):
    return tuple(int(n) for n in re.findall(r"\d+", text)[:3])


def in_range(version: str, spec: str) -> bool:
    """`spec` is space-separated conditions such as `>=0.3.0 <1.0.0`."""
    ops = {">=": lambda a, b: a >= b, ">": lambda a, b: a > b, "<=": lambda a, b: a <= b,
           "<": lambda a, b: a < b, "=": lambda a, b: a == b}
    have = version_tuple(version)
    for part in spec.split():
        op = next((o for o in (">=", "<=", ">", "<", "=") if part.startswith(o)), "=")
        if not ops[op](have, version_tuple(part[len(op):] if part.startswith(op) else part)):
            return False
    return True


# --- the decision ---------------------------------------------------------------------------
def classify(project: Path, source: Path, old: dict, new: dict) -> dict:
    """Sort one owner's files. `spliced` is the subset of `update`/`add` written by block."""
    result = {k: [] for k in ("same", "update", "diverged", "add", "retired")}
    result["spliced"], result["untouched"] = set(), set()
    old_files = {**old.get("retired", {}), **old.get("files", {})}
    old_blocks = old.get("blocks", {})
    for rel, want in sorted(new.get("files", {}).items()):
        if fingerprint((source / rel).read_bytes()) != want:
            raise Stop(f"release file {rel} does not match the release's own manifest; "
                       "re-download the release rather than updating from a modified copy")
        dst = project / rel
        if not dst.is_file():
            result["add"].append(rel)
            continue
        have = fingerprint(dst.read_bytes())
        if have == want:
            result["same"].append(rel)
        elif have == old_files.get(rel):
            result["update"].append(rel)
        else:
            result["diverged"].append(rel)
    for rel, want in sorted(new.get("blocks", {}).items()):
        if block_fingerprint(source / rel) != want:
            raise Stop(f"release file {rel} does not match the release's own manifest")
        dst = project / rel
        if not dst.is_file():
            result["add"].append(rel)
            continue
        have = block_fingerprint(dst)
        if have == want:
            result["same"].append(rel)
        elif have is not None and have == old_blocks.get(rel):
            result["update"].append(rel)
            result["spliced"].add(rel)
        elif have is None and fingerprint(dst.read_bytes()) == old_files.get(rel):
            result["update"].append(rel)  # an untouched copy from before the markers existed
        else:
            result["diverged"].append(rel)
    shipped = set(new.get("files", {})) | set(new.get("blocks", {}))
    result["retired"] = sorted(r for r in set(old_files) | set(old_blocks)
                               if r not in shipped and (project / r).is_file())
    for rel in result["retired"]:
        dst = project / rel
        if fingerprint(dst.read_bytes()) == old_files.get(rel) or \
                (rel in old_blocks and block_fingerprint(dst) == old_blocks[rel]):
            result["untouched"].add(rel)
    return result


def gather(source: Path, scratch: Path) -> tuple:
    """Find the releases in a folder of downloads: zips are unpacked into `scratch`, folders are read
    where they are. Returns (core root or None, extension roots, notes); the newest copy per owner wins."""
    if not source.is_dir():
        raise Stop(f"{source} is not a folder; put the downloaded zips in the project's _update folder")
    places = []
    for entry in sorted(source.iterdir()):
        if entry.is_dir():
            places.append(entry)
        elif entry.suffix.lower() == ".zip":
            target = scratch / entry.stem
            with zipfile.ZipFile(entry) as z:
                for name in z.namelist():
                    if name.startswith(("/", "\\")) or ".." in Path(name).parts or ":" in name:
                        raise Stop(f"{entry.name} holds an unsafe path ({name}); re-download it")
                z.extractall(target)
            places.append(target)
    found = {}
    for place in places:
        for manifests in [place / MANIFEST_DIR, *place.glob("*/" + MANIFEST_DIR), *place.glob("*/*/" + MANIFEST_DIR)]:
            for path in sorted(manifests.glob("*.json")) if manifests.is_dir() else []:
                manifest = load_manifest(path)
                root = manifests.parent.parent
                found.setdefault(manifest["owner"], []).append((version_tuple(manifest.get("version", "0")), root))
    if not found:
        raise Stop(f"no familiar release found in {source}; it should hold the downloaded zips")
    notes, chosen = [], {}
    for owner, copies in sorted(found.items()):
        copies.sort(key=lambda c: c[0])
        chosen[owner] = copies[-1][1]
        if len(copies) > 1:
            notes.append(f"[{owner}] {len(copies)} copies in {source.name}; using the newest")
    core = chosen.pop("familiar", None)
    return core, list(chosen.values()), notes


def plan(project: Path, release: Path, extension_roots: list, allow_self: bool = False) -> tuple:
    if project.resolve() == release.resolve() and not allow_self:
        raise Stop("the project and the release are the same folder; run the NEW release's copy "
                   "of this script against the project")
    old_schema, new_schema = marker_field(project, "state-schema"), marker_field(release, "state-schema")
    if old_schema != new_schema:
        raise Stop(f"state schema differs (project {old_schema}, release {new_schema}): this is a "
                   "migration, not an update. Read the release notes in CHANGELOG.md first")
    core_new = load_manifest(release / MANIFEST_DIR / "familiar.json")
    if core_new is None:
        raise Stop(f"{release} carries no {MANIFEST_DIR}/familiar.json; is it a familiar release?")
    core_old = load_manifest(project / MANIFEST_DIR / "familiar.json")
    if core_old is None:
        raise Stop("the project has no core release manifest, so edited files cannot be told from "
                   "untouched ones. Use the manual procedure in INSTALL.md -> Updating "
                   "(https://github.com/familiar-md/familiar/blob/main/INSTALL.md#updating)")

    # Extensions only (`--from` with no core download): core is not compared with itself, since a
    # local edit would read as a modified release; only the extensions are updated.
    owners = [] if allow_self else [("familiar", release, core_old, core_new)]
    sources = {}
    for root in extension_roots:
        found = sorted((root / MANIFEST_DIR).glob("*.json"))
        if len(found) != 1:
            raise Stop(f"{root} should carry exactly one release manifest, found {len(found)}")
        manifest = load_manifest(found[0])
        sources[manifest["owner"]] = (root, manifest)
    notes = []
    for path in sorted((project / MANIFEST_DIR).glob("*.json")):
        owner = path.stem
        if owner == "familiar":
            continue
        if owner in sources:
            root, manifest = sources.pop(owner)
            owners.append((owner, root, load_manifest(path), manifest))
        else:
            notes.append(f"[{owner}] installed at {load_manifest(path).get('version', '?')}; "
                         "no new copy given, left unchanged")
    for owner in sources:
        notes.append(f"[{owner}] given but not installed in this project (or installed by hand before "
                     "it carried a manifest); copy it onto the project to install it, then update")

    new_version = core_new["version"]
    for pkg in sorted((project / ".familiar" / "extensions").glob("*/package/familiar-extension.json")):
        spec = json.loads(pkg.read_text(encoding="utf-8")).get("core")
        if spec and not in_range(new_version, spec):
            notes.append(f"[{pkg.parts[-3]}] declares core {spec}; {new_version} is outside it. "
                         "Check for a newer copy of that extension before relying on it")
    reports = [(owner, root, new, classify(project, root, old, new)) for owner, root, old, new in owners]
    return reports, notes, new_version


def apply(project: Path, reports: list, new_version: str) -> str:
    old_version = marker_field(project, "familiar-version")
    backup = project / BACKUP_DIR / f"{old_version}-to-{new_version}_{date.today().isoformat()}"
    replaced = [rel for _, _, _, result in reports for rel in result["update"]]
    withdrawn = [rel for _, _, _, result in reports for rel in result["retired"] if rel in result["untouched"]]
    if old_version != new_version:
        replaced.append(".familiar-project")
    for rel in replaced:
        # Keep the earliest copy: a second run must never back up an interim file.
        if not (backup / rel).exists():
            (backup / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(project / rel, backup / rel)
    for rel in withdrawn:
        # Moved, not deleted: the backup keeps it. A folder it leaves empty goes too, so a retired
        # skill's folder does not linger.
        (backup / rel).parent.mkdir(parents=True, exist_ok=True)
        if (backup / rel).exists():
            (project / rel).unlink()
        else:
            shutil.move(str(project / rel), str(backup / rel))
        folder = (project / rel).parent
        while folder != project and folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
            folder = folder.parent
    for _, root, _, result in reports:
        for rel in result["update"] + result["add"]:
            dst = project / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if rel in result["spliced"]:
                # Bytes, not read_text: universal newlines would hide the project's CRLF.
                text = splice_block(dst.read_bytes().decode("utf-8"), (root / rel).read_bytes().decode("utf-8"))
                dst.write_bytes(text.encode("utf-8"))
            else:
                shutil.copy2(root / rel, dst)
    marker = project / ".familiar-project"
    lines = [f"familiar-version: {new_version}" if l.startswith("familiar-version:") else l
             for l in marker.read_text(encoding="utf-8").splitlines()]
    marker.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for owner, _, new, result in reports:
        out = project / MANIFEST_DIR / f"{owner}.json"
        old = load_manifest(out) or {}
        old_fps = {**old.get("retired", {}), **old.get("files", {})}
        # Retired files left in place stay listed, so every later run still reports them.
        record = dict(new, retired={rel: old_fps[rel] for rel in result["retired"]
                                    if rel in old_fps and rel not in result["untouched"]})
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(backup) if replaced or withdrawn else "none needed"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project", required=True, help="the existing project folder to update")
    ap.add_argument("--release", help="the new release's familiar-workspace folder "
                                      "(default: the one this script sits in)")
    ap.add_argument("--extension", action="append", default=[],
                    help="a new extension drop-in folder; repeat for each")
    ap.add_argument("--from", dest="source",
                    help="a folder of downloaded release zips or folders, such as the project's _update")
    ap.add_argument("--apply", action="store_true", help="back up, then write")
    args = ap.parse_args(argv)
    project = Path(args.project).resolve()
    if args.source:
        source = Path(args.source)
        return run_from(project, source if source.is_absolute() else project / source, args.apply)
    release = Path(args.release).resolve() if args.release else Path(__file__).resolve().parents[2]
    return run(project, release, [Path(e).resolve() for e in args.extension], args.apply)


def run_from(project: Path, source: Path, do_apply: bool) -> int:
    scratch = Path(tempfile.mkdtemp(prefix="familiar-update-"))
    try:
        try:
            core, extensions, notes = gather(source, scratch)
        except (Stop, zipfile.BadZipFile) as e:
            print(f"STOP: {e}. Nothing was written.")
            return 2
        for note in notes:
            print(note)
        if core is None:
            # Extensions only: core is compared with itself, so only the extensions change.
            return run(project, project, extensions, do_apply, allow_self=True)
        newer = core / ".familiar" / "scripts" / "update.py"
        if newer.is_file() and newer.read_bytes() != Path(__file__).read_bytes():
            # The new release's own updater does the work, so its rules apply, not this copy's.
            cmd = [sys.executable, "-X", "utf8", str(newer), "--project", str(project), "--release", str(core)]
            for root in extensions:
                cmd += ["--extension", str(root)]
            done = subprocess.run(cmd + (["--apply"] if do_apply else []), capture_output=True, text=True)
            print(done.stdout, end="")
            print(done.stderr, end="", file=sys.stderr)
            return done.returncode
        return run(project, core, extensions, do_apply)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def run(project: Path, release: Path, extensions: list, do_apply: bool, allow_self: bool = False) -> int:
    try:
        reports, notes, new_version = plan(project, release, extensions, allow_self)
    except Stop as e:
        print(f"STOP: {e}. Nothing was written.")
        return 2

    print(f"{project.name}: familiar {marker_field(project, 'familiar-version')} -> {new_version}")
    builds = [load_manifest(r / MANIFEST_DIR / "familiar.json").get("build") for r in (project, release)]
    if builds[0] != builds[1] and all(builds):
        print(f"  core build {builds[0]} -> {builds[1]}")
    for owner, _, _, result in reports:
        print(f"  [{owner}] same {len(result['same'])}, update {len(result['update'])}, "
              f"add {len(result['add'])}, diverged {len(result['diverged'])}, retired {len(result['retired'])}")
        for key in ("diverged", "add", "update", "retired"):
            for rel in result[key]:
                tail = "   (edited here; left alone)" if key == "diverged" else \
                       ("   (no longer shipped; moved to the backup)" if rel in result["untouched"]
                        else "   (no longer shipped, edited here; left in place)") if key == "retired" else ""
                print(f"      {key:8} {rel}{tail}")
    for note in notes:
        print(f"  {note}")
    if not do_apply:
        print("report only -- rerun with --apply to back up and write")
        return 0

    backup = apply(project, reports, new_version)
    print(f"applied; familiar-version -> {new_version}; backup: {backup}")
    check = project / ".familiar" / "scripts" / "project_check.py"
    if check.is_file():
        done = subprocess.run([sys.executable, "-X", "utf8", str(check), "--root", str(project)],
                              capture_output=True, text=True)
        # The summary line only: findings predate the update and belong to the next check-in.
        first = (done.stdout.strip() or done.stderr.strip() or f"exit {done.returncode}").splitlines()[0]
        print(f"project_check: {first} (run {check.relative_to(project).as_posix()} for the details)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
