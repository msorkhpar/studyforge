r"""Turning what an adapter wrote into the pages a reader opens.

**What it does.** Holds the framework's build — the walk from a corpus root to
files on disk. Today that is the **reading floor's HTML**: every unit page, one
container page per declared container, the root index, and the shared bundle
those three link. The media copy and narration are each a separate pass and
neither is here yet.

**How you use it.**

    from studyforge.generate import write_site

    written = write_site(corpus_root, output_root)

`sources(root)` answers *which units have material and where*;
`read_corpus(root)` hands back everything a corpus declares, read once;
`write_pages(root, into)` runs the unit-page pass alone. `BuildError` is the
only exception any of it raises.

**Depends on.** the declaration, contents, placement, builder and renderer
packages. ⛔ Nothing here knows any source (R1), and nothing here is a command:
this is the library a command would call, not the command.

## ⛔ This package is a FLOOR, not the build pipeline

⚠️ **`docs/tasks/E09-delivery.md` puts the pipeline in `SF-28` and `OPS-04`, and
both are larger than this.** What is here is the part that is genuinely true end
to end — a corpus goes in, a navigable site comes out, an unnarrated corpus stays
quiet, and nothing that already existed is touched (R3). ⛔ **It is deliberately
not a subcommand and not a flag**: registering an entry point is `SF-28`'s and
its only minter's, and adding one here would put a second declaration of the
build's surface in the tree.

⭐ **Where this package finally homes is the register's call, not this module's.**
It sits beside `cli/` rather than inside it precisely so that `SF-28` can adopt,
move or absorb it without a consumer having imported a command.

## What is in the package

| Module | Owns |
|---|---|
| `declarations` | `Corpus` — the manifest, the container maps, the tree, the walk |
| `writing` | `Written`, and the one call that makes R3 a refusal |
| `navigation` | the contents document joined to a page's bar and its trail |
| `units` | the unit-page pass |
| `containers` | the `*.section.html` pass, and where each one went |
| `site` | the whole floor: the three passes, the index, and the bundle |

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

from studyforge.generate.containers import container_pages, page_paths
from studyforge.generate.declarations import (
    BuildError,
    Corpus,
    UnitSource,
    containers,
    declared_practices,
    read_corpus,
    read_manifest,
    sources,
    unit_location,
)
from studyforge.generate.navigation import ancestors, bar, index_href, trail
from studyforge.generate.site import assets, root_index, write_site
from studyforge.generate.units import unit_pages, write_pages
from studyforge.generate.writing import Written

#: ⛔ The package's whole public surface. A consumer that has to import
#: `studyforge.generate.declarations` directly is a consumer this contract
#: failed — `docs/conventions/module-structure.md` calls `__init__.py` the
#: contract.
__all__ = [
    "BuildError",
    "Corpus",
    "UnitSource",
    "Written",
    "ancestors",
    "assets",
    "bar",
    "container_pages",
    "containers",
    "declared_practices",
    "index_href",
    "page_paths",
    "read_corpus",
    "read_manifest",
    "root_index",
    "sources",
    "trail",
    "unit_location",
    "unit_pages",
    "write_pages",
    "write_site",
]
