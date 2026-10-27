#!/usr/bin/env python3
"""ref_count.py — count a knowledge page's claim tags and source-native citation markers.

    python .familiar/scripts/ref_count.py 3-Knowledge/<page>.md [--json]

Called by ingest before a page counts as finished (`.familiar/core/ingest.md` → Ingest procedure
step 5). The model used to count its own tagged claims and stamp the total into
`ref_carry_through`; a 219-page superscripted source once produced 58 tagged claims of which only 5
carried a marker, and nobody noticed for three sessions. This counts what is actually on the page
and compares it with the stamp. It reads one file and writes nothing.

What counts, in the page body (front matter excluded):
  claim tag      a bracket carrying a locator: `p.N`, `§`, section, slide, table, tab, sheet,
                 or a marker (`[Langley 2022, p.1, ref 3]`). Cross-links to other pages
                 (`[Other-page.md]`), Markdown links, and checkboxes are not claim tags.
  carried        a claim tag with a source-native marker: `ref N`, `refs N-M`, or
                 `citing <Author Year>`
  ambiguous      `ref: ambiguous`, the marker ingest step 4 requires when one cannot be read

The counts are evidence, not a verdict: a legitimately interpretive page carries few markers.
Ingest reports a stamp that disagrees with the count, and a low carried share against a source that
cites densely, and fixes the page or the stamp before calling the page done.
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
from pathlib import Path

# A tag often wraps across lines ("[Langley 2022, p.1, ref 2, citing Husereau\n  ...]").
BRACKET = re.compile(r"(?<!\[)\[([^\[\]]{3,400})\](?![(\[])")
LOCATOR = re.compile(r"\bp{1,2}\.\s*\d|§|\bsection\b|\bslide\b|\btable\b|\btab\b|\bsheet\b|\bfig(?:ure)?\.?\s*\d|"
                     r"\brefs?\b\s*\d|\bciting\b|\bref:\s*ambiguous", re.IGNORECASE)
CARRIED = re.compile(r"\brefs?\.?\s*\d|\bciting\b", re.IGNORECASE)
AMBIGUOUS = re.compile(r"\bref:\s*ambiguous", re.IGNORECASE)
STAMP = re.compile(r"ref_carry_through:\s*`?\s*(n/a[^\n`]*|(\d+)\+?\s+claims tagged,\s*(\d+)\+?\s+carried)", re.IGNORECASE)


def split_front_matter(text: str) -> tuple[str, str]:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[3:end], text[end + 4:]
    return "", text


def close(stamped: int, counted: int) -> bool:
    """Within 10% (and never less than 2) of the count. One bracket can hold two claims and a
    model may count a claim per sentence, so exact agreement is not the test; a stamp that says 90
    when the page carries 51 is."""
    return abs(stamped - counted) <= max(2, round(0.1 * max(stamped, counted)))


def count(text: str) -> dict:
    front, body = split_front_matter(text)
    tags = [m.group(1) for m in BRACKET.finditer(body) if LOCATOR.search(m.group(1))
            and not m.group(1).strip().lower().endswith(".md") and m.group(1).strip() not in ("x", " ")]
    carried = [t for t in tags if CARRIED.search(t)]
    ambiguous = [t for t in tags if AMBIGUOUS.search(t)]
    stamp = STAMP.search(front) or STAMP.search(body)
    freehand = stamp is None and "ref_carry_through" in text
    result = {"claims_tagged": len(tags), "carried": len(carried), "ambiguous": len(ambiguous),
              "carried_share": round(len(carried) / len(tags), 2) if tags else None,
              "stamp": "freehand" if freehand else None, "stamp_tagged": None, "stamp_carried": None,
              "matches_stamp": None}
    if stamp:
        result["stamp"] = stamp.group(1).strip()
        if stamp.group(2):
            result["stamp_tagged"], result["stamp_carried"] = int(stamp.group(2)), int(stamp.group(3))
            result["matches_stamp"] = close(result["stamp_tagged"], len(tags)) and \
                close(result["stamp_carried"], len(carried))
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("page")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    result = count(Path(args.page).read_text(encoding="utf-8", errors="replace"))
    if args.json:
        print(json.dumps(result, indent=2))
        return
    share = f"{result['carried_share']:.0%}" if result["carried_share"] is not None else "n/a"
    print(f"{result['claims_tagged']} claims tagged, {result['carried']} carried a source-native marker "
          f"({share}), {result['ambiguous']} marked ref: ambiguous")
    if result["stamp"] is None:
        print("ref_carry_through: MISSING -- the page is not complete without it (ingest.md step 5)")
    elif result["stamp"] == "freehand":
        print("ref_carry_through is present but not in the standard form "
              "`<N> claims tagged, <M> carried a source-native marker`; restate it with the counts above")
    elif result["matches_stamp"] is False:
        print(f"ref_carry_through stamp says {result['stamp_tagged']} tagged / {result['stamp_carried']} carried "
              "-- more than 10% away from what the page carries; correct the stamp or the page")
    elif result["matches_stamp"] is None:
        print(f"ref_carry_through: {result['stamp']}")
    else:
        print(f"ref_carry_through stamp ({result['stamp_tagged']} / {result['stamp_carried']}) is consistent with the page")


if __name__ == "__main__":
    main()
