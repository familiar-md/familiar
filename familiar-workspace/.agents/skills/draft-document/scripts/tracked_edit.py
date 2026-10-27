#!/usr/bin/env python3
"""tracked_edit.py -- tracked-change and comment edits to a team-owned Word file.

The review branch (`references/review.md`) uses this instead of `build_docx.py --revise`, which
cannot write tracked changes and rebuilds the runs it touches. Everything here is additive: it
wraps text in `w:ins`/`w:del` by one author, adds comments and replies, and never alters another
author's tracked change, comment or reference-manager field.

    python tracked_edit.py --apply SOURCE.docx EDITS.json OUT.docx
    python tracked_edit.py --check SOURCE.docx OUT.docx
    python tracked_edit.py --list-comments SOURCE.docx
    python tracked_edit.py --accept-copy SOURCE.docx COPY.docx

EDITS.json:
    {"author": "Claude (AI)",                      # optional; this is the default
     "protect_prefixes": ["Note to "],             # optional; replies to comments starting with
                                                   #   one of these are refused (default shown)
     "protect_comments": ["7"],                    # optional; refuse replies to these ids
     "edits": [
       {"action": "replace",      "anchor": "exact text", "text": "new text"},
       {"action": "delete",       "anchor": "exact text"},
       {"action": "insert_after", "anchor": "exact text", "text": "new text"},
       {"action": "comment",      "anchor": "exact text", "text": "comment"},
       {"action": "reply",        "comment_id": "3",      "text": "reply"}]}
Any replace/delete/insert_after may also carry "comment": "text" to attach a comment to the change.
`occurrence` (1-based) is required only when the anchor appears more than once in the document.

`anchor` is a substring of one paragraph. Only plain text runs that are direct children of the
paragraph are editable: text inside another author's insertion or deletion, inside a hyperlink,
or anywhere in a complex field (a reference-manager citation) is opaque, and an anchor that spans
it is refused. A match must be unique or disambiguated by `occurrence`, otherwise it is refused.
`--apply` is all-or-nothing: if any edit is refused, nothing is written.

--check SOURCE OUT proves the pass was safe: rejecting this author's changes in OUT reproduces
SOURCE's text, every tracked change, comment and field run in SOURCE is byte-identical in OUT, and
everything new in OUT is by this author. --accept-copy writes a copy with every tracked change
accepted, for formatting checks (insertions skew the font-share check in build_docx.py --validate).

Needs lxml, which python-docx already requires. Standard library otherwise.
"""

# familiar's floor is Python 3.10. On anything older, stop with a plain message instead of a traceback.
import sys
if sys.version_info < (3, 10):
    sys.exit("familiar needs Python 3.10 or newer, but this is Python %d.%d (%s). Install Python 3.10+ "
             "(.familiar/scripts/doctor.py says how), then run this again with it." % (*sys.version_info[:2], sys.executable))

import argparse
import copy
import datetime
import json
import random
import sys
import zipfile
from pathlib import Path

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
W15 = "http://schemas.microsoft.com/office/word/2012/wordml"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
XML = "http://www.w3.org/XML/1998/namespace"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
COMMENTS_REL = OFFICE_REL + "/comments"
COMMENTS_EX_REL = "http://schemas.microsoft.com/office/2011/relationships/commentsExtended"
COMMENTS_CT = "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"
COMMENTS_EX_CT = "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml"
DEFAULT_AUTHOR = "Claude (AI)"
DEFAULT_PROTECT = ["Note to "]
OPAQUE = "￼"


def q(ns, tag):
    return f"{{{ns}}}{tag}"


class Refusal(Exception):
    pass


# --------------------------------------------------------------------------- package

class Package:
    def __init__(self, path: Path):
        with zipfile.ZipFile(path) as z:
            self.infos = z.infolist()
            self.data = {i.filename: z.read(i.filename) for i in self.infos}
        self.changed: dict[str, bytes] = {}
        rels = etree.fromstring(self.data["_rels/.rels"])
        target = next((r.get("Target") for r in rels if r.get("Type") == OFFICE_REL + "/officeDocument"),
                      "word/document.xml")
        self.doc_path = target.lstrip("/")
        self.rels_path = str(Path(self.doc_path).parent / "_rels" / (Path(self.doc_path).name + ".rels")
                             ).replace("\\", "/")
        self.rels = etree.fromstring(self.data[self.rels_path])
        self.document = etree.fromstring(self.data[self.doc_path])
        self.comments = self._part(COMMENTS_REL)
        self.comments_ex = self._part(COMMENTS_EX_REL)
        self.comments_path = self._target(COMMENTS_REL) or "word/comments.xml"
        self.comments_ex_path = self._target(COMMENTS_EX_REL) or "word/commentsExtended.xml"
        self.content_types = etree.fromstring(self.data["[Content_Types].xml"])
        self.new_parts: set[str] = set()

    def _target(self, rel_type):
        for r in self.rels:
            if r.get("Type") == rel_type:
                base = Path(self.doc_path).parent
                return str((base / r.get("Target")).as_posix()) if not r.get("Target").startswith("/") \
                    else r.get("Target").lstrip("/")
        return None

    def _part(self, rel_type):
        path = self._target(rel_type)
        return etree.fromstring(self.data[path]) if path and path in self.data else None

    def ensure_comments(self):
        if self.comments is None:
            self.comments = etree.fromstring(
                f'<w:comments xmlns:w="{W}" xmlns:w14="{W14}" xmlns:w15="{W15}" xmlns:mc="{MC}" '
                f'mc:Ignorable="w14 w15"/>'.encode())
            self._add_part(self.comments_path, COMMENTS_REL, COMMENTS_CT)

    def ensure_comments_ex(self):
        if self.comments_ex is None:
            self.comments_ex = etree.fromstring(
                f'<w15:commentsEx xmlns:w15="{W15}" xmlns:mc="{MC}" mc:Ignorable="w15"/>'.encode())
            self._add_part(self.comments_ex_path, COMMENTS_EX_REL, COMMENTS_EX_CT)

    def _add_part(self, path, rel_type, content_type):
        self.new_parts.add(path)
        ids = {r.get("Id") for r in self.rels}
        n = 1
        while f"rId{n}" in ids:
            n += 1
        etree.SubElement(self.rels, q(PKG_REL, "Relationship"), Id=f"rId{n}", Type=rel_type,
                         Target=Path(path).name)
        etree.SubElement(self.content_types, q(CT, "Override"), PartName="/" + path, ContentType=content_type)

    def save(self, out: Path):
        def ser(root):
            return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
        self.changed[self.doc_path] = ser(self.document)
        if self.comments is not None:
            self.changed[self.comments_path] = ser(self.comments)
        if self.comments_ex is not None:
            self.changed[self.comments_ex_path] = ser(self.comments_ex)
        if self.new_parts:
            self.changed[self.rels_path] = ser(self.rels)
            self.changed["[Content_Types].xml"] = ser(self.content_types)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for info in self.infos:
                payload = self.changed.get(info.filename, self.data[info.filename])
                z.writestr(info, payload, compress_type=info.compress_type)
            for name in sorted(self.new_parts):
                z.writestr(name, self.changed[name])


# --------------------------------------------------------------------------- paragraph model

def _run_text(run):
    return "".join(t.text or "" for t in run.findall(q(W, "t")))


def _is_plain(run):
    # Word writes w:lastRenderedPageBreak into long paragraphs on every save. It is a cached layout
    # hint with no text, so it does not make a run uneditable (review 2026-10-10, 02 M5: it was the
    # likeliest cause of live "anchor not found" refusals on team files).
    return all(c.tag in (q(W, "rPr"), q(W, "t"), q(W, "lastRenderedPageBreak")) for c in run)


def field_runs(root):
    """Every run that sits inside a complex field, tracked across paragraphs in document order.

    A reference-manager bibliography (EndNote `ADDIN EN.REFLIST`) or a table of contents opens in one
    paragraph and closes many paragraphs later; counting field depth per paragraph left the middle
    paragraphs editable (review 2026-10-10, 02 H1)."""
    inside, depth = set(), 0
    for run in root.iter(q(W, "r")):
        fld = run.find(q(W, "fldChar"))
        kind = fld.get(q(W, "fldCharType")) if fld is not None else None
        if kind == "begin":
            depth += 1
        if depth or kind is not None:
            inside.add(run)
        if kind == "end":
            depth = max(0, depth - 1)
    return inside


def segments(p, in_field=None):
    """Virtual text of a paragraph: editable runs as text, everything else as one OPAQUE char.
    Returns (text, [(run, start, end)]). A complex field (reference-manager citation) is opaque
    from its begin to its end, result runs included; pass `in_field` (from field_runs) so a field
    that spans paragraphs is opaque in every paragraph it covers."""
    out, pos, depth = [], 0, 0
    parts = []
    for child in p:
        if child.tag == q(W, "r"):
            fld = child.find(q(W, "fldChar"))
            if fld is not None:
                kind = fld.get(q(W, "fldCharType"))
                if kind == "begin":
                    depth += 1
                parts.append(OPAQUE)
                pos += 1
                if kind == "end":
                    depth = max(0, depth - 1)
                continue
            if depth or (in_field is not None and child in in_field) or not _is_plain(child):
                parts.append(OPAQUE)
                pos += 1
                continue
            t = _run_text(child)
            if t:
                out.append((child, pos, pos + len(t)))
                parts.append(t)
                pos += len(t)
        elif child.tag in (q(W, "pPr"), q(W, "commentRangeStart"), q(W, "commentRangeEnd"),
                           q(W, "bookmarkStart"), q(W, "bookmarkEnd"), q(W, "proofErr")):
            continue
        else:
            parts.append(OPAQUE)
            pos += 1
    return "".join(parts), out


def _set_text(run, text):
    for t in run.findall(q(W, "t")):
        run.remove(t)
    t = etree.SubElement(run, q(W, "t"))
    t.text = text
    t.set(q(XML, "space"), "preserve")


def _split(run, k):
    text = _run_text(run)
    right = copy.deepcopy(run)
    _set_text(run, text[:k])
    _set_text(right, text[k:])
    run.addnext(right)
    return right


def isolate(p, s, e, in_field=None):
    """Split plain runs so [s, e) is covered by whole runs; return those runs."""
    for cut in (s, e):
        _, segs = segments(p, in_field)
        for run, a, b in segs:
            if a < cut < b:
                _split(run, cut - a)
                break
    _, segs = segments(p, in_field)
    return [run for run, a, b in segs if a >= s and b <= e and b > a]


def _blocker(p, anchor):
    """Name what keeps an anchor that is in a paragraph's text from being editable."""
    full = "".join(t.text or "" for t in p.iter(q(W, "t")))
    i = full.find(anchor)
    if i == -1:
        return None
    seen = 0
    for t in p.iter(q(W, "t")):
        seen += len(t.text or "")
        if seen > i:
            anc = t.getparent()
            while anc is not None and anc is not p:
                name = etree.QName(anc).localname
                if name in ("ins", "del"):
                    return f"it sits inside a tracked change by {anc.get(q(W, 'author'))!r}"
                if name == "hyperlink":
                    return "it sits inside a hyperlink"
                if name == "sdtContent":
                    return "it sits inside a content control"
                anc = anc.getparent()
            break
    return ("it sits inside a field (a reference-manager citation or bibliography) or a run holding a "
            "tab, symbol or other special content")


# --------------------------------------------------------------------------- editing

class Editor:
    def __init__(self, pkg: Package, author: str, protect_prefixes, protect_comments):
        self.pkg, self.author = pkg, author
        self.protect_prefixes = protect_prefixes
        self.protect_comments = {str(c) for c in protect_comments}
        self.body = pkg.document.find(q(W, "body"))
        self.in_field = field_runs(self.body)
        ids = [int(v) for el in pkg.document.iter() for k, v in el.attrib.items()
               if k == q(W, "id") and v.lstrip("-").isdigit()]
        self.next_rev = max(ids, default=0) + 1
        self.now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.paraids = {el.get(q(W14, "paraId")) for el in pkg.document.iter() if el.get(q(W14, "paraId"))}
        if pkg.comments is not None:
            self.paraids |= {el.get(q(W14, "paraId")) for el in pkg.comments.iter() if el.get(q(W14, "paraId"))}

    def _rev(self, tag):
        el = etree.Element(q(W, tag))
        el.set(q(W, "id"), str(self.next_rev))
        el.set(q(W, "author"), self.author)
        el.set(q(W, "date"), self.now)
        self.next_rev += 1
        return el

    def _paraid(self):
        while True:
            v = f"{random.randint(1, 0x7FFFFFFE):08X}"
            if v not in self.paraids:
                self.paraids.add(v)
                return v

    def find(self, anchor, occurrence):
        if not anchor or OPAQUE in anchor:
            raise Refusal(f"unusable anchor {anchor!r}")
        hits = []
        for p in self.body.iter(q(W, "p")):
            text, _ = segments(p, self.in_field)
            i = text.find(anchor)
            while i != -1:
                hits.append((p, i))
                i = text.find(anchor, i + 1)
        if not hits:
            reason = next((r for r in (_blocker(p, anchor) for p in self.body.iter(q(W, "p"))) if r), None)
            if reason:
                raise Refusal(f"anchor is in the document but not editable: {reason}. Comment on nearby "
                              f"text instead, or ask the author: {anchor!r}")
            raise Refusal(f"anchor not found in the document's text (check spelling, quotes and "
                          f"spaces; an anchor must sit within one paragraph): {anchor!r}")
        if occurrence is None and len(hits) > 1:
            raise Refusal(f"anchor matches {len(hits)} places; set occurrence: {anchor!r}")
        n = (occurrence or 1) - 1
        if not 0 <= n < len(hits):
            raise Refusal(f"occurrence {occurrence} out of range ({len(hits)} matches): {anchor!r}")
        p, i = hits[n]
        return p, i, i + len(anchor)

    def _wrap_del(self, runs):
        dels = []
        for run in runs:
            d = self._rev("del")
            run.addprevious(d)
            d.append(run)
            for t in run.findall(q(W, "t")):
                t.tag = q(W, "delText")
                t.set(q(XML, "space"), "preserve")
            dels.append(d)
        return dels

    def _ins_after(self, node, rpr_from, text):
        ins = self._rev("ins")
        run = etree.SubElement(ins, q(W, "r"))
        rpr = rpr_from.find(q(W, "rPr")) if rpr_from is not None else None
        if rpr is not None:
            run.append(copy.deepcopy(rpr))
        _set_text(run, text)
        node.addnext(ins)
        return ins

    def _comment_on(self, first, last, text, parent_id=None):
        cid = self._new_comment(text, parent_id)
        start = etree.Element(q(W, "commentRangeStart"))
        start.set(q(W, "id"), cid)
        end = etree.Element(q(W, "commentRangeEnd"))
        end.set(q(W, "id"), cid)
        first.addprevious(start)
        last.addnext(end)
        ref = etree.Element(q(W, "r"))
        etree.SubElement(ref, q(W, "commentReference")).set(q(W, "id"), cid)
        end.addnext(ref)
        return cid

    def _new_comment(self, text, parent_para_id=None):
        pkg = self.pkg
        pkg.ensure_comments()
        ids = [int(c.get(q(W, "id"))) for c in pkg.comments.findall(q(W, "comment"))
               if (c.get(q(W, "id")) or "").isdigit()]
        cid = str(max(ids, default=-1) + 1)
        c = etree.SubElement(pkg.comments, q(W, "comment"))
        c.set(q(W, "id"), cid)
        c.set(q(W, "author"), self.author)
        c.set(q(W, "date"), self.now)
        c.set(q(W, "initials"), "AI")
        p = etree.SubElement(c, q(W, "p"))
        para_id = self._paraid()
        p.set(q(W14, "paraId"), para_id)
        r1 = etree.SubElement(p, q(W, "r"))
        etree.SubElement(r1, q(W, "annotationRef"))
        r2 = etree.SubElement(p, q(W, "r"))
        _set_text(r2, text)
        if parent_para_id is not None:
            pkg.ensure_comments_ex()
            ex = etree.SubElement(pkg.comments_ex, q(W15, "commentEx"))
            ex.set(q(W15, "paraId"), para_id)
            ex.set(q(W15, "paraIdParent"), parent_para_id)
            ex.set(q(W15, "done"), "0")
        elif pkg.comments_ex is not None:
            ex = etree.SubElement(pkg.comments_ex, q(W15, "commentEx"))
            ex.set(q(W15, "paraId"), para_id)
            ex.set(q(W15, "done"), "0")
        return cid

    def locate(self, edit):
        """Where an edit lands, resolved against the document as it is now. None for a reply."""
        action = edit.get("action")
        if action == "reply":
            return None
        if action not in ("replace", "delete", "insert_after", "comment"):
            raise Refusal(f"unknown action {action!r}")
        if action in ("replace", "insert_after", "comment") and not edit.get("text"):
            raise Refusal(f"{action} needs text: {edit.get('anchor')!r}")
        return self.find(edit.get("anchor"), edit.get("occurrence"))

    def apply(self, edit, loc=None):
        action = edit.get("action")
        text = edit.get("text")
        if action == "reply":
            return self._reply(str(edit.get("comment_id")), text)
        p, s, e = loc or self.find(edit.get("anchor"), edit.get("occurrence"))
        if action in ("replace", "insert_after") and not text:
            raise Refusal(f"{action} needs text: {edit.get('anchor')!r}")
        if action == "comment":
            runs = isolate(p, s, e, self.in_field)
            if not runs:
                raise Refusal(f"nothing editable to comment on: {edit.get('anchor')!r}")
            self._comment_on(runs[0], runs[-1], text)
            return
        if action in ("replace", "delete"):
            runs = isolate(p, s, e, self.in_field)
            if not runs:
                raise Refusal(f"nothing editable at: {edit.get('anchor')!r}")
            template = runs[0]
            dels = self._wrap_del(runs)
            last = dels[-1]
            first = dels[0]
            if action == "replace":
                last = self._ins_after(last, template, text)
        elif action == "insert_after":
            runs = isolate(p, s, e, self.in_field)
            if not runs:
                raise Refusal(f"nothing editable at: {edit.get('anchor')!r}")
            first = last = self._ins_after(runs[-1], runs[-1], text)
        else:
            raise Refusal(f"unknown action {action!r}")
        if edit.get("comment"):
            self._comment_on(first, last, edit["comment"])

    def _reply(self, comment_id, text):
        pkg = self.pkg
        if not text:
            raise Refusal(f"reply to comment {comment_id} needs text")
        parent = None
        if pkg.comments is not None:
            parent = next((c for c in pkg.comments.findall(q(W, "comment")) if c.get(q(W, "id")) == comment_id),
                          None)
        if parent is None:
            raise Refusal(f"no comment with id {comment_id}")
        body = "".join(t.text or "" for t in parent.iter(q(W, "t"))).strip()
        if comment_id in self.protect_comments or any(body.startswith(pre) for pre in self.protect_prefixes):
            raise Refusal(f"comment {comment_id} is protected (addressed to the client); not replying")
        paras = parent.findall(q(W, "p"))
        parent_para = paras[-1].get(q(W14, "paraId")) if paras else None
        if not parent_para:
            raise Refusal(f"comment {comment_id} has no paragraph id, so a threaded reply cannot be linked "
                          f"without editing it; add a new comment instead")
        cid = self._new_comment(text, parent_para)
        doc = pkg.document
        start = next((el for el in doc.iter(q(W, "commentRangeStart")) if el.get(q(W, "id")) == comment_id), None)
        end = next((el for el in doc.iter(q(W, "commentRangeEnd")) if el.get(q(W, "id")) == comment_id), None)
        if start is None or end is None:
            raise Refusal(f"comment {comment_id} is not anchored in the document body")
        ns = etree.Element(q(W, "commentRangeStart"))
        ns.set(q(W, "id"), cid)
        start.addnext(ns)
        ne = etree.Element(q(W, "commentRangeEnd"))
        ne.set(q(W, "id"), cid)
        end.addnext(ne)
        # the reply's reference run goes after the parent's reference run when there is one
        anchor_node = ne
        for r in doc.iter(q(W, "r")):
            ref = r.find(q(W, "commentReference"))
            if ref is not None and ref.get(q(W, "id")) == comment_id:
                anchor_node = r
                break
        ref_run = etree.Element(q(W, "r"))
        etree.SubElement(ref_run, q(W, "commentReference")).set(q(W, "id"), cid)
        anchor_node.addnext(ref_run)


# --------------------------------------------------------------------------- check / accept / list

def _c14n(el):
    return etree.tostring(el, method="c14n", exclusive=True)


def _is_field_run(el):
    return el.tag == q(W, "r") and (el.find(q(W, "fldChar")) is not None or el.find(q(W, "instrText")) is not None)


def protected_items(pkg: Package):
    items = []
    for el in pkg.document.iter(q(W, "ins"), q(W, "del")):
        if el.getparent().tag != q(W, "rPr"):
            items.append(_c14n(el))
    in_field = field_runs(pkg.document)
    for el in pkg.document.iter(q(W, "r"), q(W, "fldSimple")):
        # A field's result runs (between `separate` and `end`, possibly paragraphs later) are part of
        # the field: --check must see an edit to a bibliography entry as an altered field.
        if el.tag == q(W, "fldSimple") or _is_field_run(el) or el in in_field:
            items.append(_c14n(el))
    if pkg.comments is not None:
        for el in pkg.comments.findall(q(W, "comment")):
            items.append(_c14n(el))
    return items


def projected_text(pkg: Package, author: str):
    """Paragraph texts after rejecting this author's tracked changes."""
    out = []
    for p in pkg.document.iter(q(W, "p")):
        buf = []
        for el in p.iter(q(W, "t"), q(W, "delText")):
            anc = el.getparent()
            mine_ins = mine_del = False
            while anc is not None and anc is not p:
                if anc.tag == q(W, "ins") and anc.get(q(W, "author")) == author:
                    mine_ins = True
                if anc.tag == q(W, "del") and anc.get(q(W, "author")) == author:
                    mine_del = True
                anc = anc.getparent()
            if el.tag == q(W, "t") and not mine_ins:
                buf.append(el.text or "")
            elif el.tag == q(W, "delText") and mine_del:
                buf.append(el.text or "")
        out.append("".join(buf))
    return out


def check(source: Path, out: Path, author=DEFAULT_AUTHOR):
    a, b = Package(source), Package(out)
    problems = []
    # Own-author edits from earlier passes are already in the source; project both the same way.
    if projected_text(a, author) != projected_text(b, author):
        problems.append("rejecting this author's changes does not reproduce the source text")
    src, dst = protected_items(a), protected_items(b)
    remaining = list(dst)
    for item in src:
        if item in remaining:
            remaining.remove(item)
        else:
            problems.append("a tracked change, comment or field run from the source is missing or altered: "
                            + item[:120].decode("utf-8", "replace"))
    for item in remaining:
        el = etree.fromstring(item)
        if el.tag in (q(W, "ins"), q(W, "del"), q(W, "comment")) and el.get(q(W, "author")) != author:
            problems.append(f"new {etree.QName(el).localname} by {el.get(q(W, 'author'))!r}, not {author!r}")
        elif el.tag in (q(W, "r"), q(W, "fldSimple")):
            problems.append("a field run appeared that is not in the source")
    return problems


def accept_copy(source: Path, out: Path):
    pkg = Package(source)
    for d in list(pkg.document.iter(q(W, "del"))):
        if d.getparent().tag != q(W, "rPr"):
            d.getparent().remove(d)
    for i in list(pkg.document.iter(q(W, "ins"))):
        if i.getparent().tag == q(W, "rPr"):
            i.getparent().remove(i)
            continue
        parent, idx = i.getparent(), i.getparent().index(i)
        for k, child in enumerate(list(i)):
            parent.insert(idx + k, child)
        parent.remove(i)
    pkg.save(out)


def list_comments(source: Path):
    pkg = Package(source)
    rows = []
    parents = {}
    if pkg.comments_ex is not None:
        for ex in pkg.comments_ex:
            parents[ex.get(q(W15, "paraId"))] = ex.get(q(W15, "paraIdParent"))
    if pkg.comments is None:
        return rows
    para_to_id = {}
    for c in pkg.comments.findall(q(W, "comment")):
        for p in c.findall(q(W, "p")):
            if p.get(q(W14, "paraId")):
                para_to_id[p.get(q(W14, "paraId"))] = c.get(q(W, "id"))
    for c in pkg.comments.findall(q(W, "comment")):
        last = c.findall(q(W, "p"))[-1] if c.findall(q(W, "p")) else None
        pid = last.get(q(W14, "paraId")) if last is not None else None
        rows.append({"id": c.get(q(W, "id")), "author": c.get(q(W, "author")),
                     "reply_to": para_to_id.get(parents.get(pid)),
                     "text": "".join(t.text or "" for t in c.iter(q(W, "t")))})
    return rows


def apply(source: Path, edits_path: Path, out: Path):
    data = json.loads(edits_path.read_text(encoding="utf-8"))
    edits = data["edits"] if isinstance(data, dict) else data
    meta = data if isinstance(data, dict) else {}
    if out.exists():
        raise Refusal(f"{out} already exists; a rerun must not overwrite a saved version")
    if out.resolve() == source.resolve():
        raise Refusal("output is the source file")
    pkg = Package(source)
    editor = Editor(pkg, meta.get("author", DEFAULT_AUTHOR), meta.get("protect_prefixes", DEFAULT_PROTECT),
                    meta.get("protect_comments", []))
    # Resolve every edit against the untouched document first, so `occurrence` means the Nth match in
    # the file as the user read it. Resolving each edit after the previous one had run let a tracked
    # deletion shift the count and land a second edit on the wrong sentence (review 2026-10-10, 02 H2).
    failures, located = [], []
    for n, edit in enumerate(edits, 1):
        try:
            located.append((n, edit, editor.locate(edit)))
        except Refusal as e:
            failures.append((n, str(e)))
    order = {p: i for i, p in enumerate(editor.body.iter(q(W, "p")))}
    spans = sorted(((order[loc[0]], loc[1], loc[2], n) for n, _, loc in located if loc), key=lambda t: t[:2])
    for (pa, sa, ea, na), (pb, sb, eb, nb) in zip(spans, spans[1:]):
        if pa == pb and sb < ea:
            failures.append((nb, f"overlaps edit {na} in the same paragraph; merge them into one edit"))
    if failures:
        return len(edits) - len(failures), sorted(failures)
    # Apply from the end of the document backwards: an edit only changes text at or after its own
    # start, so every earlier location stays exact. Replies touch no body text and go last.
    body_edits = sorted((x for x in located if x[2]), key=lambda x: (order[x[2][0]], x[2][1]), reverse=True)
    for n, edit, loc in body_edits + [x for x in located if not x[2]]:
        try:
            editor.apply(edit, loc)
        except Refusal as e:
            failures.append((n, str(e)))
    if failures:
        return len(edits) - len(failures), sorted(failures)
    pkg.save(out)
    return len(edits), []


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--apply", nargs=3, metavar=("SOURCE", "EDITS", "OUT"))
    g.add_argument("--check", nargs=2, metavar=("SOURCE", "OUT"))
    g.add_argument("--list-comments", metavar="SOURCE")
    g.add_argument("--accept-copy", nargs=2, metavar=("SOURCE", "COPY"))
    ap.add_argument("--author", default=DEFAULT_AUTHOR, help="with --check: the author to verify")
    args = ap.parse_args()
    try:
        if args.apply:
            src, edits, out = map(Path, args.apply)
            done, failures = apply(src, edits, out)
            if failures:
                print("UNAPPLIED (nothing written):", file=sys.stderr)
                for n, why in failures:
                    print(f"  #{n}: {why}", file=sys.stderr)
                sys.exit(2)
            print(f"applied {done}/{done} edits -> {out}")
        elif args.check:
            problems = check(Path(args.check[0]), Path(args.check[1]), args.author)
            if problems:
                print(f"CHECK FAILED ({len(problems)}):")
                for p in problems:
                    print(f"  - {p}")
                sys.exit(1)
            print("check: reject-all reproduces the source; source changes, comments and fields untouched; "
                  "new content is by " + args.author)
        elif args.list_comments:
            for r in list_comments(Path(args.list_comments)):
                reply = f" (reply to {r['reply_to']})" if r["reply_to"] else ""
                print(f"{r['id']}\t{r['author']}{reply}\t{r['text'][:100]}")
        else:
            accept_copy(Path(args.accept_copy[0]), Path(args.accept_copy[1]))
            print(f"-> {args.accept_copy[1]}")
    except Refusal as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
