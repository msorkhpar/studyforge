"""FND-04's fixtures check themselves, so twelve epics can trust them.

**What it does.** Answers one question about one corpus root: `violations(root)`
returns every rule it breaks, as `(rule_id, message)`. An empty list means the
corpus is valid.

**How you use it.**

    from tests.fixture_checks import FIXTURES, violations

    assert violations(FIXTURES / "depth1") == []

**Depends on.** The standard library and its own modules. ⛔ **It imports no
`studyforge` module on purpose.** `src/studyforge/` was empty when these
fixtures were written; a fixture check that needed the framework could not run
until the framework did, which is the wrong way round. The canonicalisation
rules restated here are the *fixtures'* own contract — SF-06 owns the
framework's, and when it lands the duplication is resolved in its favour.

## Why a fixture checks itself

A fixture nobody validates is a fixture that rots: the first task to build
against it inherits its defects as requirements, and every later task inherits
them from that task. So the invariants spec §4–§6 states about a corpus are
asserted against `tests/fixtures/` before any framework code exists to assert
them for real.

Two things it proves, and the second is the point of the invalid corpora:

* the two valid corpora violate **nothing**;
* each invalid corpus violates **exactly the one rule its directory names**,
  and no other — a fixture that broke two rules would make SF-25's acceptance
  unable to tell which check it was exercising.

⚠️ `tests/fixtures/invalid/personal-data/` deliberately contains
personal-data-shaped strings, every one of them fabricated (see its
`VIOLATION.md`). A repository-wide R7 sweep must exclude that one directory and
only that one.

## What is in the package

⭐ **Five seams, named before they were needed.** FND-04's handoff recorded
that a sixth invalid fixture would want this module split along the seams its
checks already had; the disclosure follow-up and SF-02's `content` key then
grew it past the point where that was optional. Each module is one kind of
question, so a failing check names a concern rather than a file.

| Module | The question it answers |
|---|---|
| `vocabulary` | what a corpus is made of — keys, block types, versions |
| `corpus` | how to read one, and what its digests are taken over |
| `shape` | is this manifest complete, this document canonical, this block named |
| `digests` | do the recorded digests and counts survive recomputation |
| `addresses` | does what a thing says about where it is match where it sits |
| `media` | is every declared file on disk, at the size and digest recorded |
| `personal_data` | does anything carry an R7 shape (R7) |
| `sweeps` | which of these files a given sweep is entitled to read (Ruling 46) |

⭐ **`sweeps` is the sixth, and it arrived from outside.** It was written
against `tests/studyforge/archive/test_blocks.py` and moved here by `FND-09`,
because a helper that reads `INVALID_CORPORA` belongs beside the declaration:
anywhere else and the next person needing one reads the directory name instead.
⛔ **Two modules must never consume it** — see `sweeps.ENFORCERS`.

Run `python3 -m tests.fixture_checks` for the block-type coverage table.
"""

from __future__ import annotations

from tests.fixture_checks.addresses import (
    check_container,
    check_document_identity,
    check_overlays,
)
from tests.fixture_checks.corpus import (
    all_blocks,
    archive_files,
    block_types,
    blocks_of_type,
    canonical,
    containers_in,
    read_json,
    rendered,
    sha256_of,
    strings_in,
)
from tests.fixture_checks.digests import check_digests
from tests.fixture_checks.exercise import check_exercise
from tests.fixture_checks.media import check_media
from tests.fixture_checks.personal_data import check_personal_data, shape_in
from tests.fixture_checks.shape import check_blocks, check_document_shape, check_manifest
from tests.fixture_checks.sweeps import (
    ENFORCERS,
    RAW,
    Coverage,
    archive_documents,
    coverage,
    declaring,
    excluded_by,
    fixture_paths,
    sweeping,
)
from tests.fixture_checks.vocabulary import (
    BLOCK_FIELDS,
    BLOCK_TYPES,
    CONTAINER_TYPES,
    COUNT_KEYS,
    DOCUMENT_KEYS,
    FIXTURES,
    INVALID_CORPORA,
    MARKUP_SHAPED,
    OPTIONAL_KEYS,
    REQUIRED_TYPES,
    RUNNABLE,
    VALID,
)

__all__ = [
    "BLOCK_FIELDS",
    "BLOCK_TYPES",
    "CONTAINER_TYPES",
    "COUNT_KEYS",
    "DOCUMENT_KEYS",
    "ENFORCERS",
    "FIXTURES",
    "INVALID_CORPORA",
    "MARKUP_SHAPED",
    "OPTIONAL_KEYS",
    "RAW",
    "REQUIRED_TYPES",
    "RUNNABLE",
    "VALID",
    "Coverage",
    "all_blocks",
    "archive_documents",
    "archive_files",
    "block_types",
    "blocks_of_type",
    "canonical",
    "containers_in",
    "coverage",
    "declaring",
    "excluded_by",
    "fixture_paths",
    "read_json",
    "rendered",
    "sha256_of",
    "shape_in",
    "strings_in",
    "sweeping",
    "violations",
]


def violations(root):
    """Every rule `root` breaks, as `(rule_id, message)`. Empty means valid."""
    manifest = read_json(root / "corpus.json")
    found = list(check_manifest(manifest))
    found += list(check_personal_data(manifest, "corpus.json"))
    containers = containers_in(root)
    if not containers:
        return found + [("no-container", f"{root.name} holds no container.json")]
    practices = 0
    for container_dir, container in containers:
        found += list(check_container(root, manifest, container_dir, container))
        found += list(check_documents(root, manifest, container_dir, container))
        practices += sum(unit.get("practices") or 0 for unit in container.get("units") or [])
    found += list(check_overlays(root))
    if bool(manifest.get("exercises")) != (practices > 0):
        found.append(
            (
                "exercises-flag",
                f"corpus.json says exercises={manifest.get('exercises')!r} "
                f"and {practices} practice(s) are declared",
            )
        )
    return found


def check_documents(root, manifest, container_dir, container):
    """Every archive document in one container, through every check that has one.

    ⭐ The one fan-out. A new kind of check is added here and applies to every
    document; before the split it would have been added inside a 65-line
    function that also knew about ordinals.
    """
    for unit, kind, ordinal, path in archive_files(container_dir, container.get("variant")):
        where = str(path.relative_to(root))
        document = read_json(path)
        yield from check_document_shape(path, document, where)
        yield from check_blocks(document, where)
        yield from check_digests(document, where)
        yield from check_exercise(document, where)
        yield from check_media(container_dir, document, where)
        yield from check_personal_data(document, where)
        yield from check_document_identity(
            document, where, container, manifest, (unit, kind, ordinal)
        )
