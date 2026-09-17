"""What a generated artifact is called — derived from identity, never from a filename.

**What it does.** Mints every name placement writes: the unit page, the
container page, the media directories, the shared assets, the discovery cache.

**How you use it.** `unit_page_name(7, "Introduction to the Streams API")`.

**Depends on.** `studyforge.address` for slugs and ordinals, and `errors`.

## Every generated page carries a real name, never `index.html`

⛔ §5, and the reason is discovery: a scanner reads names, and a reader browses
directories. `index.html` is neither unique in a listing nor distinguishable
from the root index — and, in `sibling`, twenty units share one directory, so
`index.html` cannot even be written twice.

⛔ **The one `index.html` this framework writes is the root index**, and it is
not a page any scan treats as a unit.

## Where the numbering comes from — settled here, because SF-31 waits on it

⭐ **From identity, never from the source filename.** §5's worked example shows
`4.4.1-introduction-to-the-streams-api.unit.html` beside `README_4.4.1.md`, and
it is tempting to read `4.4.1` out of that filename. ⛔ Three reasons not to:

1. **R1.** `README_<numbering>.md` is one corpus's convention. Measured
   2026-09-09 across the four designed shapes: one spells a unit
   `README_4.4.1.md`, the depth-1 fixture spells it `01-what-a-triple-is.md`,
   and a third spells it `1.md`, `s1.md`, `c1.md`. Deriving from the
   filename means the framework carries a parser per corpus.
2. **R4.** Inferring what an artifact should be *called* from what the source
   file is *named* is inferring meaning from a path, pointed the other way.
3. **R10.** `origin` is optional; a name derived from it would have a fallback,
   and a corpus would then use two naming schemes at once.

⭐ **So the default label is the unit's own ordinal** — `unit-07` — and
`label=` is the seam. A corpus's own display numbering is *data*: the day an
adapter records it, it is passed here and §5's example is reproduced
**exactly, with no change to this module**. See `docs/tasks/handoffs/SF-03.md`,
which routes that field to the archive contract.
"""

from __future__ import annotations

from studyforge.address import Address, require_ordinal, slugify, unit_name
from studyforge.corpus.container.fields import (
    FILENAME_PERMITTED_DESCRIBED,
    is_filename_component,
)
from studyforge.corpus.placement.errors import PlacementError

#: ⛔ The suffix a discovery scan globs for. Load-bearing, not decoration: it
#: is what tells a unit page from a container page and both from the root
#: index, without opening a single file.
UNIT_SUFFIX = ".unit.html"
CONTAINER_SUFFIX = ".section.html"

#: The one `index.html` in a generated site. ⚠️ Named here so nothing else
#: mints a second one.
ROOT_INDEX_FILENAME = "index.html"

#: The discovery cache. ⛔ A cache of the scan and never the authority — a
#: stale one is detected and the scan wins (§5).
SITE_CACHE_FILENAME = "site.json"

#: The ignore file a profile's media rules live in. ⛔ Only ever inside a
#: directory this framework generates, never at the repository root (R3).
IGNORE_FILENAME = ".gitignore"

#: Directory names that appear in generated hrefs, in the reader's own tree and
#: in a scan. ⛔ Named constants because those three must agree, and because
#: eight modules each carrying their own `"audio"` is how the extraction source
#: came to have half a pipeline looking in the old place.
ASSETS_DIRNAME = "assets"
#: ⛔ **The archive root, and its ONE spelling (`INT-06/6`).** At the corpus root beside
#: `corpus.json`, never under `.studyforge/`: `validate`, `plan`, a build and the adapter
#: `Layout` all read it from here, and `test_names` fails on a second literal in `src/`.
ARCHIVE_DIRNAME = "archive"
#: ⛔ **The directory under a container that holds its documents, by variant, and
#: its ONE spelling (`W199`).** §6's layout is `<archive-root>/<address>/raw/<variant>/
#: unit-NN/`: `validate` walks it and the adapter `Layout` writes it, so it was minted
#: twice — `ARCHIVE_ROOT_NAME` in `validate.corpus` and `RAW_DIR` in the adapter layout,
#: neither on a package surface. ⚠️ One variant per container (SF-05), so this is a
#: single directory and not a search.
RAW_DIRNAME = "raw"
UNITS_DIRNAME = "units"
AUDIO_DIRNAME = "audio"
IMAGES_DIRNAME = "images"
VIDEO_DIRNAME = "video"
PRACTICE_DIRNAME = "practice"

#: The per-unit directories a page addresses relatively (R8). Ordered, because
#: `studyforge plan` lists them and R10 forbids depending on set iteration.
UNIT_MEDIA_DIRNAMES = (AUDIO_DIRNAME, IMAGES_DIRNAME, VIDEO_DIRNAME, PRACTICE_DIRNAME)


def unit_stem(ordinal: int, title: str, label: str | None = None) -> str:
    """Return `<label>-<title-slug>` — the stem every artifact of one unit shares.

    ⭐ One stem for the page, its audio, its images, its video and its
    practice, so a reader looking at a directory sees them grouped, and so a
    rename is one decision rather than five.
    """
    require_ordinal(ordinal, "unit ordinal")
    slug = slugify(title)
    if not slug:
        raise PlacementError(
            f"unit {ordinal} has a title that slugifies to nothing, so it can be "
            f"given no name; titles are the corpus's, so this is a corpus defect"
        )
    return f"{label_of(ordinal, label)}-{slug}"


def contained_stem(address: Address, ordinal: int, title: str, label: str | None = None) -> str:
    """Return `<segment>.<segment>.<label>-<title-slug>`: the stem with its container in front.

    ⛔ **`W254`, clause 1: a unit's name is a function of its own identity, and
    its container is part of that identity.** Where many units share a
    directory, `unit_stem` alone gives two containers' units one name as soon
    as their ordinals and titles mirror. Measured on a real corpus: 5 pairs,
    and a build that replaced 5 pages it had written in the same run.

    ⭐ **Distinct containers never share a name, by construction.** An address
    segment is a slug, and a slug carries no `.`. Every address in one corpus
    has the same depth (§4), so the first `depth` dot-separated fields of a name
    are its address. ⚠️ Two units of ONE container with the same label and the
    same title still share a name, and `validate`'s `duplicate-path` refuses
    that by name, as `plan` and a build do.
    """
    if not isinstance(address, Address):
        raise PlacementError("a unit is named with its container's address, and none was given")
    return ".".join(address.segments) + "." + unit_stem(ordinal, title, label)


def label_of(ordinal: int, label: str | None = None) -> str:
    r"""Return the corpus's own numbering for a unit, or its ordinal name.

    ⚠️ A label is presentation, so it is not required to be a slug — but it
    becomes part of a filename, so it must be a **usable filename component**.

    ⛔ **The rule is `container.fields.is_filename_component`, imported and
    never re-spelled.** This function once carried its own forbidden list,
    `"/\\ \t\n"`, a copy of the map's that was missing the carriage return.
    Adding the carriage return would have been the wrong fix twice over:

    1. **Ruling 8.** A forbidden list is an open set and cannot be finished.
       Measured 2026-09-09 on the merged tree, **seven further shapes passed
       both guards into a filename** — a vertical tab, a form feed, a
       non-breaking space, U+2028, `"`, `:` and `*` — and `:` and `"` break
       the `file://` floor, so this was an R8 defect and not a tidy-up.
    2. **One rule has one home.** Two spellings of one rule is the defect; the
       missing character was only how it showed. The predicate replaces the
       constant, so there is no longer a thing to copy.

    ⭐ Defence in depth, and neither guard substitutes for the other: the
    container map refuses a bad label where it enters, so the failure lands
    next to the file that caused it; this refuses one at the point a filename
    is minted, because `label_of` also takes labels from callers that never
    saw a map. ⛔ They agree because they ask the same predicate — not because
    two lists were kept in step, which is what was tried and did not hold.
    """
    if label is None:
        return unit_name(ordinal)
    # ⛔ R7, rubric §1f: a label is read straight out of a file somebody else
    # wrote, so a refusal names the type and the permitted class, never the
    # value. Naming what is *permitted* is also the more useful message — it
    # tells an author what to write, where echoing the label only shows them
    # what they already typed.
    if not isinstance(label, str):
        raise PlacementError(f"a unit label must be a str, got {type(label).__name__}")
    if not is_filename_component(label):
        raise PlacementError(
            "a unit label becomes part of a filename, so it may carry only "
            f"{FILENAME_PERMITTED_DESCRIBED}; the label is not reproduced here (R7)"
        )
    return label


def unit_page_name(ordinal: int, title: str, label: str | None = None) -> str:
    """Return the filename of one unit's reading page."""
    return unit_stem(ordinal, title, label) + UNIT_SUFFIX


def container_page_name(titles: tuple[str, ...]) -> str:
    """Return the filename of a container's own page, from its deepest title.

    ⚠️ The deepest title, not the joined address: a container page sits in a
    directory that already says where it is, and repeating the whole address
    in the filename makes the deepest level unreadable in a listing.
    """
    if not titles:
        raise PlacementError("a container needs at least one title to be named")
    slug = slugify(titles[-1])
    if not slug:
        # ⛔ §1f: the title is the corpus's own text and is described, not
        # reproduced. Its depth is what tells the author where to look.
        raise PlacementError(
            f"the container title at depth {len(titles)} slugifies to nothing, so "
            f"it can be given no name; titles are the corpus's, so this is a "
            f"corpus defect"
        )
    return slug + CONTAINER_SUFFIX


def is_unit_page(name: str) -> bool:
    """Report whether a filename is one a discovery scan should open as a unit."""
    return name.endswith(UNIT_SUFFIX)


def is_container_page(name: str) -> bool:
    """Report whether a filename is one a discovery scan should open as a container."""
    return name.endswith(CONTAINER_SUFFIX)
