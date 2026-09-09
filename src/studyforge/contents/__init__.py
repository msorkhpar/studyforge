"""The table of contents and local status, as data rather than as markup.

**What it does.** Produces the corpus's structure — containers, units, order,
and how far the reader has got — as a versioned document. The renderer, the
server and the page's own script are all consumers of it.

**How you use it.** Ask for the contents of a corpus; render it, serve it, or
diff it. It is data on purpose: a table of contents that exists only as
generated HTML cannot be served to a page that wants to highlight the current
unit without re-parsing the markup it just produced.

**Depends on.** `address`, `corpus`, `unit`. ⛔ Not on `render` — the direction
is renderer-depends-on-contents, never the reverse.

⚠️ **Structure and status have different lifetimes** and are versioned
separately so a consumer can cache the stable half. Structure changes when the
corpus is rebuilt; status changes every time the reader finishes a section.

**Skeleton at FND-01.** Filled by SF-13 (E03).
"""
