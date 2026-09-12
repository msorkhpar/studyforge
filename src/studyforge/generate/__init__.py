r"""Turning what an adapter wrote into the pages a reader opens.

**What it does.** Holds the framework's build — the walk from a corpus root to
files on disk. Today that is unit pages and nothing else; the root index,
container pages, the contents document, the asset bundle, the media copy and
narration are each a separate pass and none of them is here yet.

**How you use it.** `sources(root)` answers *which units have material and
where*; `write_pages(root, into)` renders and writes them, returning what it
wrote and what it refused to touch.

**Depends on.** `units`, and through it the declaration, placement, builder and
renderer packages. ⛔ Nothing here knows any source (R1), and nothing here is a
command: this is the library a command would call, not the command.

## ⛔ This package is a FLOOR, not the build pipeline

⚠️ **`docs/tasks/E09-delivery.md` puts the pipeline in `SF-28` and `OPS-04`,
and both are larger than this.** What is here is the smallest thing that is
genuinely true end to end — a corpus goes in, pages come out, an unnarrated
corpus stays quiet, and nothing that already existed is touched (R3). ⛔ **It
is deliberately not a subcommand and not a flag**: registering an entry point
is `SF-28`'s and its only minter's, and adding one here would put a second
declaration of the build's surface in the tree.

⭐ **Where this package finally homes is the register's call, not this
module's.** It sits beside `cli/` rather than inside it precisely so that
`SF-28` can adopt, move or absorb it without a consumer having imported a
command.

## ⚠️ Why this package is not called `build`

⛔ **The root ignore file carries a bare `build/` rule** — the ordinary Python
packaging artifact — **and a bare rule matches at every depth**, so a package of
that name under `src/` is untracked from the moment it is written and every
check that walks the tracked tree reads it as absent. ⭐ Named here because
`build` is the word every task document uses, so the next author reaches for it
first, and the failure is silent in the worst direction: a green floor over code
git never saw.
"""

from __future__ import annotations

from studyforge.generate.units import (
    BuildError,
    UnitSource,
    Written,
    containers,
    declared_practices,
    read_manifest,
    sources,
    write_pages,
)

__all__ = [
    "BuildError",
    "UnitSource",
    "Written",
    "containers",
    "declared_practices",
    "read_manifest",
    "sources",
    "write_pages",
]
