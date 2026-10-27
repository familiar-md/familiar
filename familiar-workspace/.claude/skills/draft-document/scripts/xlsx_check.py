#!/usr/bin/env python3
"""xlsx_check.py — what is in a workbook, and what an openpyxl round-trip would lose.

    python xlsx_check.py <workbook.xlsx|.xlsm>                 # inventory and round-trip risks
    python xlsx_check.py --compare <before.xlsx> <after.xlsx>  # what the new version lost
    add --json for machine-readable output

Read-only, standard library only: it opens the file as the ZIP package it is and reads its XML parts,
so it runs without openpyxl and never changes the file.

Why it exists. Workbooks are a common deliverable, and openpyxl drops some features when it opens and saves an existing file. Its
own documentation says shapes are lost and that an `.xlsm` saved without `keep_vba=True` will not open
in Excel; at load it warns that the newer data-validation and conditional-formatting extensions "will
be removed" (those are the drop-down lists and rules Excel writes when a list points at another
sheet). So check before editing, and compare after: a version that silently lost a reviewer's
drop-downs looks finished until someone tries to use it.

Exit codes: 0 safe to round-trip (or nothing lost on --compare), 1 at least one risk or loss, 2 error.
"""

# familiar's floor is Python 3.10. On anything older, stop with a plain message instead of a traceback.
import sys
if sys.version_info < (3, 10):
    sys.exit("familiar needs Python 3.10 or newer, but this is Python %d.%d (%s). Install Python 3.10+ "
             "(.familiar/scripts/doctor.py says how), then run this again with it." % (*sys.version_info[:2], sys.executable))

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

FEATURES = {
    # key: (label, regex over the part's XML, parts glob prefix, lost on an openpyxl round-trip?)
    "data_validations": ("drop-down lists and input rules", r"<(?!x14:)(?:\w+:)?dataValidation\b", "xl/worksheets/", False),
    "ext_data_validations": ("drop-down lists in Excel's newer format (lists that point at another sheet)",
                             r"<x14:dataValidation\b", "xl/worksheets/", True),
    "conditional_formats": ("conditional formatting rules", r"<(?!x14:)(?:\w+:)?cfRule\b", "xl/worksheets/", False),
    "ext_conditional_formats": ("conditional formatting in Excel's newer format",
                                r"<x14:cfRule\b", "xl/worksheets/", True),
    "sparklines": ("sparklines", r"<x14:sparklineGroup\b", "xl/worksheets/", True),
    "shapes": ("shapes and text boxes", r"<(?:xdr:)?sp\b", "xl/drawings/drawing", True),
    "charts": ("charts", None, "xl/charts/chart", False),
    "images": ("images", None, "xl/media/", False),
    "form_controls": ("form controls (buttons, check boxes)", None, "xl/ctrlProps/", True),
    "slicers": ("slicers and timelines", None, "xl/slicers/", True),
    "pivot_tables": ("pivot tables", None, "xl/pivotTables/", False),
    "external_links": ("links to other workbooks", None, "xl/externalLinks/", False),
    "comments": ("comments and notes", None, "xl/comments", False),
    "threaded_comments": ("threaded comments", None, "xl/threadedComments/", True),
    "formulas": ("cells with formulas", r"<(?:\w+:)?f[ >]", "xl/worksheets/", False),
    "defined_names": ("named ranges", r"<(?:\w+:)?definedName\b", "xl/workbook.xml", False),
    "tables": ("Excel tables", None, "xl/tables/", False),
}


def inventory(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"ERROR: {path} does not exist")
    try:
        z = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        raise SystemExit(f"ERROR: {path} is not a valid Office package (no readable ZIP directory)")
    names = z.namelist()
    if "[Content_Types].xml" not in names:
        raise SystemExit(f"ERROR: {path} has no [Content_Types].xml; it is not a valid Office package")
    counts = {}
    for key, (_, regex, prefix, _) in FEATURES.items():
        parts = [n for n in names if n.startswith(prefix)]
        if regex is None:
            counts[key] = len([n for n in parts if not n.endswith("/") and "/_rels/" not in n])
        else:
            rx = re.compile(regex)
            counts[key] = sum(len(rx.findall(z.read(n).decode("utf-8", "replace"))) for n in parts
                              if n.endswith(".xml"))
    sheets = re.findall(r'<(?:\w+:)?sheet\b[^>]*\bname="([^"]*)"', z.read("xl/workbook.xml").decode("utf-8", "replace")) \
        if "xl/workbook.xml" in names else []
    macros = "xl/vbaProject.bin" in names
    z.close()
    lock = path.with_name("~$" + path.name)
    return {"file": str(path), "sheets": sheets, "macros": macros, "counts": counts,
            "open_in_excel": lock.exists()}


def risks(inv: dict, path: Path) -> list[str]:
    out = []
    if inv["open_in_excel"]:
        out.append("Excel has the file open (a ~$ lock file sits beside it): ask the user to save and close "
                   "it before anything reads or writes it")
    for key, (label, _, _, lost) in FEATURES.items():
        if lost and inv["counts"][key]:
            out.append(f"{inv['counts'][key]} {label}: openpyxl removes these when it saves this file")
    if inv["macros"]:
        if path.suffix.lower() != ".xlsm":
            out.append("the package holds macros but the name is not .xlsm")
        out.append("macros: load with openpyxl's keep_vba=True and save as .xlsm, or Excel will not open the result")
    return out


def notes(inv: dict) -> list[str]:
    out = []
    if inv["counts"]["formulas"]:
        out.append(f"{inv['counts']['formulas']} formula cells: a file saved by openpyxl keeps the formulas but no "
                   "calculated values until Excel recalculates it, so a script that reads values back gets blanks")
    return out


def compare(before: dict, after: dict) -> list[str]:
    lost = []
    gone = [s for s in before["sheets"] if s not in after["sheets"]]
    if gone:
        lost.append("sheets missing: " + ", ".join(gone))
    for key, (label, _, _, _) in FEATURES.items():
        b, a = before["counts"][key], after["counts"][key]
        if a < b:
            lost.append(f"{label}: {b} before, {a} after")
    if before["macros"] and not after["macros"]:
        lost.append("macros: present before, gone after")
    return lost


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--compare", action="store_true", help="BEFORE AFTER: report what the new version lost")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if args.compare:
        if len(args.files) != 2:
            raise SystemExit("ERROR: --compare takes two files: BEFORE AFTER")
        before, after = (inventory(Path(f)) for f in args.files)
        lost = compare(before, after)
        if args.json:
            print(json.dumps({"before": before, "after": after, "lost": lost}, indent=2))
        else:
            print("nothing lost" if not lost else "LOST in the new version:\n" + "\n".join(f"  - {l}" for l in lost))
        sys.exit(1 if lost else 0)
    if len(args.files) != 1:
        raise SystemExit("ERROR: give one workbook, or --compare BEFORE AFTER")
    path = Path(args.files[0])
    inv = inventory(path)
    found = risks(inv, path)
    if args.json:
        print(json.dumps({**inv, "risks": found, "notes": notes(inv), "openpyxl_round_trip_safe": not found}, indent=2))
    else:
        print(f"{path.name}: {len(inv['sheets'])} sheet(s): " + ", ".join(inv["sheets"]))
        present = [f"{n} {FEATURES[k][0]}" for k, n in inv["counts"].items() if n]
        if present:
            print("contains: " + "; ".join(present))
        print("safe to open and save with openpyxl" if not found else "before editing with openpyxl:\n"
              + "\n".join(f"  - {r}" for r in found))
        for n in notes(inv):
            print(f"note: {n}")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
