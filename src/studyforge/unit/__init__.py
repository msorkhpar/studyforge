"""The served unit document: archive content, the authored overlay, and section keys.

**What it does.** Builds what a reader is actually served for one unit, by
composing the archive's blocks with whatever the corpus authored on top of them
and assigning the section keys that navigation, narration and progress all
address.

**How you use it.** Give the builder an archive document and the corpus's
overlay for that address; take back a versioned unit document. That document's
`api` field is checked, not migrated at read time — an unknown version is
refused (R9).

**Depends on.** `address` and `archive`. ⛔ Not on `render`: this package
decides *what* a unit is, and the renderer decides what it looks like. That
split is what lets the same unit document serve a page, a table of contents
entry and a narration script without three ideas of the same content.

⚠️ **Section keys are load-bearing.** The player highlights by them, progress
records by them, and in-page navigation links by them, so a key that changes
when the prose is edited silently detaches a reader's saved position from the
thing it marked.

⭐ **A unit with an overlay and a unit with none are the same shape.** One with
none is complete, not deficient — the fixtures carry both from wave 0 so the
no-overlay path is never the one discovered late.

**Skeleton at FND-01.** Filled by SF-09 and SF-10 (E02).
"""
