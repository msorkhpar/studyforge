r"""One corpus root in, its unit pages on disk — the caller the renderer never had.

**What it does.** Builds each declared unit's served document from the material
an adapter wrote, places it under the corpus's own placement profile, renders
its page with the bar and the trail the contents document computes, and writes
the bytes.

**How you use it.** `write_pages(root, into)` for a corpus root;
`unit_pages(corpus, into)` when the declarations have already been read. ⛔
`into` is **required and has no default** — where a build's output goes is a
decision this module does not take.

**Depends on.** `generate.declarations` for the corpus, `generate.navigation`
for the join — the bar, the trail and the rail across containers —
`generate.containers` for where a crumb and a rail row point, `generate.writing`
for R3, `generate.narration` for what each page plays, `unit.builder` for the
document and `render.page` for the bytes. ⛔ It names no source (R1).

## ⛔ Why this module exists at all

Measured at `2d2af22`, population `src/**/*.py`, instrument `git grep`: **no
module outside `render/` called the page renderer, and no module anywhere wrote
a unit page.** The renderer, the builder, the placement profiles and the
navigation join were finished and reachable only from tests.

## ⚠️ Two things this module deliberately does NOT do, each for a reason

⛔ **No synthesis.** Each page's narration is `generate.narration`'s answer
over the record `studyforge narrate` wrote; a corpus with no record renders
`SILENT`, byte for byte the pre-narration page. A build never invokes synthesis
(R8).

⛔ **No authored overlay.** A unit that has one is built without it: this
module hands `build_unit` a unit's archive documents and nothing else.

⚠️ **What changed under this sentence, and what did not**. It used to
say nothing in `src/` declared *where* an overlay sits, so this module could
not have applied one even had it wanted to. ⭐ **That half is closed:
`skills.adapter.Layout.content(address, unit)` is the address now**, so a
build has somewhere to look. ⛔ **The verb is the half that remains and it is
unowned** — reading the file, refusing its version, composing it over the
archive's blocks and deciding what a conflict means are none of them decided,
and this module will not decide them by being the first caller. ⭐ A path
invented here would still be a second authority on the archive's shape; that
is why the address is asked for rather than composed.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path, PurePosixPath

from studyforge.corpus.placement import relative_href
from studyforge.generate.containers import page_paths
from studyforge.generate.declarations import Corpus, read_corpus, unit_location
from studyforge.generate.narration import narrated, narration_for
from studyforge.generate.navigation import bar, index_href, rail, trail
from studyforge.generate.writing import Written, place
from studyforge.render.page import Placement, render
from studyforge.unit.builder import build_unit


def write_pages(root: Path | str, into: Path | str) -> Written:
    """Render every unit that has material and write its page under `into`.

    ⛔ `into` is separate from `root` and required. A build that defaulted it to
    the corpus root would have decided, silently, that generated output belongs
    inside the material — which is the one placement question §5 gives to the
    corpus and not to the framework.
    """
    return unit_pages(read_corpus(root), into)


def unit_pages(corpus: Corpus, into: Path | str) -> Written:
    """Run the unit-page pass over declarations that have already been read."""
    out = Path(into)
    written: list[PurePosixPath] = []
    refused: list[PurePosixPath] = []
    replaced: list[PurePosixPath] = []
    for at, body in unit_bodies(corpus):
        place(out, at, body, written, refused, replaced, footprint=corpus.footprint)
    return Written(pages=tuple(written), refused=tuple(refused), replaced=tuple(replaced))


def unit_bodies(corpus: Corpus) -> Iterator[tuple[PurePosixPath, bytes]]:
    """Yield `(page path, rendered bytes)` for every unit with material, writing nothing.

    The narration record is read once, before the first page is rendered, so an
    unreadable record stops the pass before anything reaches disk.
    """
    state = narrated(corpus)
    shared = corpus.shared
    absent = corpus.absent
    above = page_paths(corpus)
    for source in corpus.units:
        at = unit_location(corpus, source)
        document = build_unit(source.directory, declared_practices=source.declared_practices)
        placement = Placement(corpus=corpus.manifest.source, unit=at, shared=shared)
        body = render(
            document,
            placement,
            bar(corpus.contents, source.key, absent),
            trail(
                corpus.contents,
                source.key,
                index_href(corpus.contents, source.key),
                {key: relative_href(at.page, page) for key, page in above.items()},
            ),
            narration_for(corpus, source, at, document, placement, state),
            rail(
                corpus.contents,
                at.page,
                above,
                container=source.container.address.key,
                unit=source.key,
                absent=absent,
            ),
        )
        yield at.page, body
