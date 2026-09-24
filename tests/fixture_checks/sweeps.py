"""Which fixture files a sweep is entitled to look at, and what a red means.

**What it does.** Walks `tests/fixtures/` once and hands back only the files a
sweep is entitled to assert against — excluding exactly the corpora *declared*
to violate one of the rules that sweep names. Every path it yields arrives with
`sweeping()`'s attribution attached, so a red on a declared fixture says whose
fault it is.

**How you use it.** A sweep names, as a set of rule ids, every property it
asserts::

    from tests.fixture_checks import archive_documents, coverage

    seen = 0
    for where, document in archive_documents(asserting={"counts"}):
        assert document["counts"] == counts_of(document["blocks"]), where
        seen += 1
    assert seen == coverage(asserting={"counts"}).swept

⛔ **`asserting` has no default and never gains one.** A default is what let the
two previous versions of this helper be wrong without anybody choosing
anything. `archive_documents()` is a `TypeError`, asserted.

**Depends on.** `json`, `pathlib` and `vocabulary`'s `INVALID_CORPORA` — the
declaration this whole module reads from. ⛔ Never the directory name.

## Why this lives here and not beside a sweep

The declaration is `INVALID_CORPORA`, and this reads it; a helper that lived
beside one of its callers would be read from the directory instead by the next
person who needed one. ⭐ It moved out of `tests/studyforge/archive/test_blocks.py`
unchanged in behaviour — the module that defined it was at
567 of its 600 lines, so the seam could not grow where it lived.

## ⛔ Two modules must never consume this — see `ENFORCERS`

They are the declaration's enforcers. Routing them through a helper that reads
the declaration would make them assert the declaration against itself.
"""

from __future__ import annotations

import json
from collections.abc import Collection, Iterator
from pathlib import Path
from typing import NamedTuple

from tests.fixture_checks.vocabulary import FIXTURES, INVALID_CORPORA

__all__ = [
    "ENFORCERS",
    "Coverage",
    "archive_documents",
    "coverage",
    "declaring",
    "excluded_by",
    "fixture_paths",
    "sweeping",
]

#: An archive document is one that sits under a `raw/` tree. ⚠️ `corpus.json`
#: and `container.json` are the corpus's own declarations, not its material,
#: and a sweep over documents must not silently pick them up.
RAW = "/raw/"

#: ⛔ **The two modules that must NOT consume this seam, and why — named in the
#: code rather than left to be rediscovered**.
#:
#: Both are the enforcers of the very declaration this module reads. Routing
#: them through `excluded_by()` would have them assert `INVALID_CORPORA`
#: against itself: the on-disk pin would agree with the dict because it *was*
#: the dict, and the R7 registry would sanction whatever the dict sanctioned.
#: ⭐ A check that reads its own answer for its question cannot fail, which is
#: the vacuous sweep arriving by the door marked "consistency".
ENFORCERS = {
    "tests/test_fixture_consistency.py": (
        "pins the invalid set on disk to INVALID_CORPORA; consuming a helper "
        "that reads INVALID_CORPORA would compare the dict with itself"
    ),
    "tools/tests/quality/personal_data/test_registry.py": (
        "pins the §1e sanctioned-directory registry to what is on disk; a "
        "helper that already excludes the declared directories would hide "
        "exactly the directory the registry exists to sanction"
    ),
}


class Coverage(NamedTuple):
    """How many files a sweep saw, and how many its declaration dropped.

    ⛔ **The denominator a sweep owes.** A sweep that excluded everything
    reports `0` findings and looks identical to a clean one; `swept` beside
    `excluded` is what tells the two apart.
    """

    swept: int
    excluded: int

    @property
    def total(self) -> int:
        """Every file the walk matched, before the declaration was applied."""
        return self.swept + self.excluded

    def __str__(self) -> str:
        return f"{self.swept} of {self.total} swept ({self.excluded} declared-excluded)"


def excluded_by(asserting: Collection[str]) -> set[str]:
    """The corpora declared to violate one of the rules `asserting` names.

    ⭐ **The exclusion rule, in four lines** — the whole of the exclusion policy, read
    from the declaration and never from a directory name.

    ⛔ **A set of rule ids, not a name.** Both coarser forms were tried and both
    are wrong at a different grain: excluding by directory drops nine documents
    that should be swept — each invalid in exactly one *named* way and correct
    in every other — and excluding by a single id under-excludes for a sweep
    that asserts two properties.
    """
    return {name for name, rule in INVALID_CORPORA.items() if rule in asserting}


def declaring(path) -> str | None:
    """The invalid corpus this file belongs to, or `None` for a valid one."""
    parts = Path(path).relative_to(FIXTURES).parts
    return parts[1] if parts and parts[0] == "invalid" else None


def sweeping(path) -> str:
    """Where this file is — and, if it declares a violation, why that matters.

    ⛔ **This is the half that closes the defect, not the exclusion.** A sweep
    that forgets to name one of its properties still goes red the day a fixture
    declaring that rule is added, and the failure a reader sees decides what
    they do about it. Unattributed, it reads as *"this fixture is broken"* and
    the fixture gets edited — ⛔ §1e's exact failure: a negative control
    neutered into an input that silently passes, which is worse than the sweep
    that provoked it.

    ⭐ So a declared fixture carries its declaration into every message it can
    appear in, including an `ArchiveError` raised by the code under test, which
    is why this returns the string the sweeps pass down rather than a check
    they must remember to call.
    """
    where = Path(path).relative_to(FIXTURES).as_posix()
    corpus = declaring(path)
    if corpus is None:
        return where
    return (
        f"{where} — ⛔ {corpus!r} declares rule {INVALID_CORPORA[corpus]!r}. "
        f"If this sweep asserts that rule, name it in asserting=; "
        f"do not change the fixture."
    )


def fixture_paths(
    *,
    asserting: Collection[str],
    glob: str = "*.json",
    within: str | None = None,
) -> Iterator[tuple[str, Path]]:
    """`(where, path)` for every fixture file a sweep asserting `asserting` may read.

    ⭐ **One walk, three views.** `archive_documents` is this restricted to
    `raw/` and parsed; `coverage` is this counted. There is no second file
    walker, so an exclusion added here cannot be missed by one of the three.

    `within` is a posix path fragment every yielded path must contain — how a
    sweep says *"the material, not the corpus's declarations about it"*.
    """
    excluded = excluded_by(asserting)
    for path in _matching(glob, within):
        if declaring(path) in excluded:
            continue
        yield sweeping(path), path


def archive_documents(*, asserting: Collection[str]) -> Iterator[tuple[str, dict]]:
    """Every archive document a sweep asserting `asserting` is entitled to look at.

    ⭐ **The exclusion rule.** A sweep names, as a set of rule ids, every property it
    asserts; this excludes exactly the fixtures *declared* to violate one of
    them — see `excluded_by`.

    ⚠️ **The declaration is `INVALID_CORPORA`, not `VIOLATION.md`.** The two
    are not copies of one fact: `VIOLATION.md` names the **spec** rule in prose
    (`spec §6`, `R9`, `R7`, `R5`) for a person reading beside the data, and no
    one of them names the id a sweep uses. ⛔ Nothing parses it.

    ⭐ **And the failure message matters as much as the exclusion** — see
    `sweeping`. A sweep that under-declares still reds, and the point was never
    the red: it was that the red read as the fixture's fault, which is the
    pressure that neuters a negative control.
    """
    for where, path in fixture_paths(asserting=asserting, within=RAW):
        yield where, json.loads(path.read_text(encoding="utf-8"))


def coverage(
    *,
    asserting: Collection[str],
    glob: str = "*.json",
    within: str | None = RAW,
) -> Coverage:
    """What `fixture_paths` will sweep and what it will drop, counted.

    ⛔ **A sweep asserts this rather than `> 0`.** `assert seen > 0` passes on
    a walk that matched one file out of forty, and passes identically on the
    day an exclusion is widened by mistake; `assert seen == coverage(...).swept`
    names the denominator the sweep was supposed to have.

    ⚠️ Defaults to the archive documents, because that is what most sweeps
    walk; pass `within=None` for the whole tree.
    """
    excluded = excluded_by(asserting)
    swept = dropped = 0
    for path in _matching(glob, within):
        if declaring(path) in excluded:
            dropped += 1
        else:
            swept += 1
    return Coverage(swept, dropped)


def _matching(glob: str, within: str | None) -> Iterator[Path]:
    """Every fixture file the walk matches, before any declaration is applied.

    ⛔ **The one walk.** `fixture_paths` and `coverage` both read it, so the
    numerator and the denominator cannot come from two different traversals —
    which is the way a coverage figure quietly stops meaning anything.
    """
    for path in sorted(FIXTURES.rglob(glob)):
        if within is None or within in path.as_posix():
            yield path
