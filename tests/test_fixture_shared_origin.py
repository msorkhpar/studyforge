"""Two units, one source file — the property `Q23` asked about.

**What it asserts.** That some valid fixture corpus declares two units whose
`origin.path` is *the same path*, and that this is therefore a corpus on which a
path-derived key **collides**, while a key derived from the unit's logical
address (`SF-01`) does not.

⛔ **Why the fixture had to exist before `SF-16` ships — Ruling 187.** *"Asserted
in both directions"* proves **surjectivity, not injectivity**. Seventeen clips
colliding onto one filename means every `<audio>` still resolves and every file
on disk is still named by a page: both stated directions pass, the suite stays
green, and sixteen units play the wrong audio. ⭐ The form that states injectivity
is a **cardinality equality** — `|clips| == |spoken units|` — and it cannot be
written at all against a fixture set in which no two units share a source file.

⭐ **The answer being tested is ruled, not re-decided here** (`Q23`, carried in
`docs/tasks/E04-narration.md`): a clip is keyed `<speech-id>-<digest>`, the
speech id from the unit's **logical address** and the digest from the **spoken
text**. ⛔ Neither half comes from the source path. `origin` is *provenance*, and
provenance is never identity.

**What this module is not.** ⛔ It does not mint a clip name — `SF-16` owns the
minter and is M3. What is asserted here is the property the minter will be
measured against and the *fixture* that makes that measurement possible: the
positional half of the key is already shipped (`SF-01`'s `unit_key`), so the
half that must separate two units sharing a file is testable today.

**Depends on.** `tests.fixture_checks` for the declaration, and the framework's
own readers — the container map's `origin` has two shapes (Ruling 92) and this
module reads neither of them itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from studyforge.corpus.container import CONTAINER_FILENAME
from studyforge.corpus.container import parse as parse_container
from studyforge.corpus.container.document import REGION_ORIGIN_API
from studyforge.corpus.manifest import MANIFEST_FILENAME
from studyforge.corpus.manifest import parse as parse_manifest
from studyforge.validate.headings import count_headings, region
from tests.fixture_checks import FIXTURES, VALID, violations

#: The corpus this row added, named once. ⚠️ Its *membership of `VALID`* is what
#: makes every contract test in the suite see it, and that is pinned below
#: rather than assumed: a fixture corpus outside the declaration is a directory
#: no check opens, and every assertion that iterated it would pass by iterating
#: nothing.
SHARED = "shared-origin"

#: The archive's spelling in the fixtures — the stand-in for `<archive-root>`,
#: which placement owns (SF-03). ⚠️ Named, never assumed to be a constant on
#: some package's surface.
ARCHIVE_DIR = "archive"


@dataclass(frozen=True)
class Unit:
    """One unit of one fixture corpus: its identity, and its provenance.

    ⭐ **The two are separate fields here on purpose**, because that separation
    is the whole subject. `corpus`, `address`, `variant` and `n` are identity —
    what `SF-01` calls the logical address. `origin` and `section` are
    provenance — where the material came from. ⛔ Nothing keys off the second.
    """

    corpus: str
    address: str
    variant: str
    n: int
    title: str
    unit_key: str
    origin: str | None
    section: str | None
    headings: int


def units_of(name: str) -> tuple[Unit, ...]:
    """Every unit of one fixture corpus, read through the framework's readers.

    ⛔ **`origin` is not read here.** It carries two shapes — a path for a whole
    file, `{path, section}` for a region of a shared one — and a second reader
    of a two-shaped field is how sixteen regions get taken for sixteen whole
    files. The container map's own parser hands back the halves separately.

    Sorted, because R10 forbids depending on filesystem enumeration order.
    """
    root = FIXTURES / name
    manifest = parse_manifest((root / MANIFEST_FILENAME).read_text(encoding="utf-8"))
    found: list[Unit] = []
    for path in sorted((root / ARCHIVE_DIR).rglob(CONTAINER_FILENAME)):
        where = path.relative_to(root).as_posix()
        container = parse_container(path.read_text(encoding="utf-8"), where, manifest)
        for unit in container.units:
            found.append(
                Unit(
                    corpus=manifest.source,
                    address=container.address.key,
                    variant=container.variant,
                    n=unit.n,
                    title=unit.title,
                    unit_key=container.address.unit_key(unit.n),
                    origin=unit.origin,
                    section=unit.origin_section,
                    headings=_headings_recorded(path.parent, container.variant, unit.n),
                )
            )
    return tuple(sorted(found, key=lambda unit: (unit.address, unit.n)))


def _headings_recorded(container_dir: Path, variant: str, n: int) -> int:
    """The `headings` count the archive records for one unit, summed over its documents.

    ⚠️ **Summed, and that is the unit's number rather than a document's.** A
    unit may hold several archive documents; comparing one of them against a
    whole source region would report a short read on every multi-document unit.
    """
    raw = container_dir / "raw" / variant / f"unit-{n:02d}"
    if not raw.is_dir():
        return 0
    total = 0
    for path in sorted(raw.glob("*.json")):
        document = parse_json(path)
        total += (document.get("counts") or {}).get("headings", 0)
    return total


def parse_json(path: Path) -> dict:
    """One JSON document, read as UTF-8. ⚠️ Imported nowhere else; see the note above."""
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def groups() -> tuple[tuple[str, str, tuple[Unit, ...]], ...]:
    """`(corpus, origin path, units)` for every path **two or more** units declare.

    ⭐ **Derived over the declaration, never over a directory name.** Which
    corpora exist is `VALID`'s to say, so a fixture dropped from the
    declaration empties this list and the parametrized tests below **skip**
    rather than pass. The pin that the list is non-empty is a test
    of its own, immediately after the derivation.
    """
    found: list[tuple[str, str, tuple[Unit, ...]]] = []
    for name in sorted(VALID):
        by_path: dict[str, list[Unit]] = {}
        for unit in units_of(name):
            if unit.origin is not None:
                by_path.setdefault(unit.origin, []).append(unit)
        for path, units in sorted(by_path.items()):
            if len(units) > 1:
                found.append((name, path, tuple(units)))
    return tuple(found)


#: ⛔ Computed once at import, so the parametrization and the inhabitation pin
#: read **one** derivation. A numerator from one walk and a denominator from
#: another is how a coverage figure stops meaning anything.
GROUPS = groups()


def label(group: tuple[str, str, tuple[Unit, ...]]) -> str:
    """A test id naming the corpus and how many units share the path — never the path."""
    name, _path, units = group
    return f"{name}-{len(units)}-units-on-one-path"


IDS = [label(group) for group in GROUPS]


# --------------------------------------------------------------------------
# ⛔ Inhabitation and wiring, first — both of the ways this row could be vacuous
# --------------------------------------------------------------------------


def test_the_shared_origin_corpus_is_a_member_of_the_declared_valid_set():
    # ⛔ **The anti-vacuity pin, and it is not ceremony.** A corpus on disk that
    # the declaration does not name is a corpus `violations()` is never run
    # against, which no parametrized contract test in this suite sees, and whose
    # every property is asserted by iterating an empty set.
    assert SHARED in VALID, VALID
    assert (FIXTURES / SHARED).is_dir()
    found = violations(FIXTURES / SHARED)
    assert found == [], "\n".join(f"{rule}: {message}" for rule, message in found)


def test_some_valid_fixture_corpus_declares_two_units_on_one_origin_path():
    # ⛔ **A denominator.** Every assertion below is parametrized over `GROUPS`, and
    # an empty `GROUPS` would skip all of them in silence. This is the one
    # assertion that reds instead.
    assert GROUPS, (
        "no valid fixture corpus has two units sharing one 'origin.path', so the "
        "collision Ruling 187 is about cannot be exhibited and every assertion "
        "below is parametrized over nothing"
    )
    assert sum(len(units) for _name, _path, units in GROUPS) >= 2, GROUPS


# --------------------------------------------------------------------------
# ⭐ The capability demonstration: the collision, and its absence
# --------------------------------------------------------------------------


@pytest.mark.parametrize("group", GROUPS, ids=IDS)
def test_a_key_derived_from_the_source_path_collides_on_this_group(group):
    """⛔ What `SF-17`'s bidirectional assertion cannot see.

    ⭐ **This is the fixture's whole value.** A corpus that *cannot* produce the
    collision is a corpus against which `SF-16`'s negative is untestable, and a
    negative nobody can test is the vacuous shape this project keeps catching.
    So the collision is asserted to exist, here, as a property of the fixture.
    """
    _name, path, units = group
    keys = sorted({unit.origin for unit in units})
    assert keys == [path], keys
    assert len(keys) == 1 < len(units), (
        f"{len(units)} units, {len(keys)} path-derived key(s): a minter reading "
        f"'origin.path' writes one clip and {len(units) - 1} unit(s) play it"
    )


@pytest.mark.parametrize("group", GROUPS, ids=IDS)
def test_the_logical_address_separates_the_units_the_path_does_not(group):
    """⭐ `Q23`'s answer, on the fixture that can disagree with it.

    The positional half of `<speech-id>-<digest>` is the unit's logical address,
    and `SF-01` ships it. ⛔ The digest half is `SF-16`'s and is *not* what does
    the separating here: the cardinality below is already equal without it,
    which is the point — two units sharing a file key apart **by construction**
    rather than by being worded differently.
    """
    _name, _path, units = group
    keys = sorted({f"{unit.corpus}/{unit.variant}/{unit.unit_key}" for unit in units})
    assert len(keys) == len(units), keys


@pytest.mark.parametrize("group", GROUPS, ids=IDS)
def test_no_part_of_the_key_is_read_out_of_the_source_path(group):
    # ⛔ R1 and Ruling 92 in one line: `origin` is provenance. A key carrying any
    # of it would make a corpus's directory layout part of its audio's identity,
    # and a source file renamed upstream would orphan every clip under it.
    _name, path, units = group
    for unit in units:
        key = f"{unit.corpus}/{unit.variant}/{unit.unit_key}"
        assert path not in key, key
        assert Path(path).stem not in key, key
        assert unit.section is None or unit.section not in key, key


# --------------------------------------------------------------------------
# ⛔ Ruling 187's form: a cardinality equality, over every valid corpus
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", VALID)
def test_the_key_space_is_exactly_as_large_as_the_unit_space(name):
    """⛔ `|keys| == |units|`, which is the only form that states injectivity.

    ⭐ It is the shape `SF-16` owes for `|clips| == |spoken units|`, asked of
    what is shipped today: the positional half of the key, over every unit of
    every corpus the declaration names.
    """
    units = units_of(name)
    assert units, name
    keys = {f"{unit.corpus}/{unit.variant}/{unit.unit_key}" for unit in units}
    assert len(keys) == len(units), sorted(keys)


@pytest.mark.parametrize("name", VALID)
def test_the_path_derived_key_space_is_smaller_exactly_where_a_file_is_shared(name):
    # ⭐ **The instrument's discriminating reading.** The test above passes for
    # every corpus, including the ones with nothing to catch; this one is the
    # half that proves the measurement can come out differently. For a corpus
    # with no shared file the two key spaces are the same size — and for the one
    # with a shared file, the path-derived space is strictly smaller.
    units = [unit for unit in units_of(name) if unit.origin is not None]
    assert units, name
    shared = {path for corpus, path, _u in GROUPS if corpus == name}
    by_path = len({unit.origin for unit in units})
    if shared:
        assert by_path < len(units), (name, by_path, len(units))
    else:
        assert by_path == len(units), (name, by_path, len(units))


def test_the_corpora_with_nothing_to_catch_are_a_populated_control():
    """⛔ **A control prints the size of its population before its verdict.**

    *"No group here"* read off an **empty** population returns the same value as
    *"no group here"* read off a real one — ⛔ and for a control that is green
    where red was required. So the corpora that produce no group are counted,
    the units they declare are counted with them, and both numbers travel in
    the assertion message rather than being implied by its absence.
    """
    producing = {corpus for corpus, _path, _units in GROUPS}
    control = [name for name in sorted(VALID) if name not in producing]
    declared = [unit for name in control for unit in units_of(name) if unit.origin is not None]
    population = (
        f"control corpora {control}; units declaring an origin: {len(declared)}; "
        f"distinct paths: {len({unit.origin for unit in declared})}"
    )
    assert control, f"every valid corpus shares a file, so the control is empty — {population}"
    assert len(declared) >= 2, population
    # ⭐ The reading itself, and it must DIFFER from the live one (1 group).
    assert len({unit.origin for unit in declared}) == len(declared), population


# --------------------------------------------------------------------------
# ⭐ Ruling 92's other half, which the same fixture makes live
# --------------------------------------------------------------------------


@pytest.mark.parametrize("group", GROUPS, ids=IDS)
def test_the_shared_file_gives_one_heading_count_for_every_unit_in_it(group):
    """⛔ Why the region shape exists at all, measured rather than described.

    ⭐ A completeness check that compared each of these units against the whole
    file would compare several units against **one** number, and every unit
    whose region is smaller than the file short-reads by construction. The
    region count is per-unit; the file count is not. ⚠️ Skipped when the source
    file is not committed beside the archive — an archive is a shippable
    artifact on its own (R2), and the absent-source path is `validate`'s
    `Unchecked`, not a fixture defect.
    """
    name, path, units = group
    source = FIXTURES / name / path
    if not source.is_file():
        pytest.skip(f"{name} commits no source file for its shared origin")
    text = source.read_text(encoding="utf-8")
    whole = count_headings(text)
    recorded = sorted(unit.headings for unit in units)
    assert whole not in recorded, (whole, recorded)
    for unit in units:
        assert unit.section is not None, unit.unit_key
        found = region(text, unit.section)
        assert found.occurrences == 1, (unit.unit_key, found)
        assert found.headings == unit.headings, (unit.unit_key, found, unit.headings)


@pytest.mark.parametrize("group", GROUPS, ids=IDS)
def test_the_regions_of_one_shared_file_are_distinct(group):
    # ⚠️ Two units naming the *same* section would be a corpus whose regions
    # overlap — the shape `origin-section-ambiguous` refuses — and it would make
    # the fixture above pass for the wrong reason.
    _name, _path, units = group
    sections = [unit.section for unit in units if unit.section is not None]
    assert len(sections) == len(units), units
    assert len(set(sections)) == len(sections), sections


# --------------------------------------------------------------------------
# ⛔ Both `origin` shapes have an input, which is what the version is for
# --------------------------------------------------------------------------


def container_versions() -> dict[str, set[int]]:
    """`{corpus: {container_api declared}}` over every valid corpus, sorted in."""
    found: dict[str, set[int]] = {}
    for name in sorted(VALID):
        root = FIXTURES / name
        manifest = parse_manifest((root / MANIFEST_FILENAME).read_text(encoding="utf-8"))
        for path in sorted((root / ARCHIVE_DIR).rglob(CONTAINER_FILENAME)):
            where = path.relative_to(root).as_posix()
            container = parse_container(path.read_text(encoding="utf-8"), where, manifest)
            found.setdefault(name, set()).add(container.container_api)
    return found


def test_the_fixture_set_gives_each_origin_shape_an_input():
    # ⛔ A whole-file `origin` and a region `origin` are two code paths, and the
    # README's own argument for the unit page's two overlay shapes applies: each needs
    # an input. ⚠️ Pinned per corpus, so a fixture silently downgraded to
    # version 1 — which would drop the region shape out of the set entirely —
    # reds here rather than in whatever reads it next.
    versions = container_versions()
    assert versions, VALID
    assert REGION_ORIGIN_API in versions[SHARED], versions
    assert {1} in [versions[name] for name in versions if name != SHARED], versions


def test_only_a_map_that_declares_the_region_version_carries_a_section():
    # ⛔ R9's other direction, pinned on the fixtures: a map using the v2 shape
    # may not call itself v1. The framework refuses it; this asserts the set on
    # disk has not grown a copy that slips past a v1-only reader.
    versions = container_versions()
    for name in sorted(VALID):
        sections = [unit for unit in units_of(name) if unit.section is not None]
        if sections:
            assert min(versions[name]) >= REGION_ORIGIN_API, (name, versions[name])
