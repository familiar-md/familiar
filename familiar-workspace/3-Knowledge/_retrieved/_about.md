# _retrieved

Documents a skill downloaded from an external source during a retrieval task — not something the
user placed in the workspace themselves. `1-Inputs/` stays reserved for user-supplied material; a file
that arrived because a skill fetched it lands here instead.

Name each file `<publisher>_<product>_<doctype>_<YYYY-MM-DD-published>.pdf` (or the source's native
extension). Validate a download before relying on it — confirm it is the expected document, not an
error page served with a 200. A file that fails validation is not retrievable; do not substitute a
different document and do not silently drop the gap.

Run `/ingest` on a file placed here the same way as any other source — it produces the
`3-Knowledge/_extract-<stable-source-ID>.md` cache and a synthesis page per `_page-template.md`. See
`.familiar/core/file-handling.md` § Workspace map.
