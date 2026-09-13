"""`W109`: `origin` has ONE reader, `fields.optional_origin`, as a standing tree property.

⭐ **The row's settlement.** `W95/3` found a test helper that took `origin` raw
out of a document and handed `sibling` a dict the moment a fixture used Ruling
92's region shape. The fix went through the one reader; this module makes that a
property of the tree instead of a reading at one ref.

⛔ **A guard that cannot fail is `W37`'s class**, so the synthesised plants below
are the inhabitation reading Ruling 191 asks for: each shape of second reader is
planted into a `tmp_path` tree and must be refused, each permitted shape must be
accepted (the positive row), and each stated survivor must survive, so the
instrument's limit is a reading and not a belief.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.studyforge.corpus.container.origin_sites import (
    ASSERTED,
    BARE,
    DECLARED,
    HANDED,
    PARSER,
    PARSER_HOME,
    TRANSCRIBED,
    WRITER,
    findings,
    sites,
)
from tests.support import repository_root

#: The sites the claim is about, which the sweep must have FOUND: the parser's own
#: hand-off and `W95/3`'s repaired helper (Ruling 132, the population first).
ONE_READER_REACHED = (
    "src/studyforge/corpus/container/document.py::_unit",
    "tests/studyforge/corpus/placement/test_corpora.py::placed",
)


def test_the_tree_holds_no_second_reader_of_origin():
    found, swept = sites(repository_root())
    print(f"origin access sites: {len(found)} in {swept} modules swept")
    for site in found:
        print(f"  {site}")
    assert swept > len({name.split("::")[0] for name in DECLARED}), swept
    # ⛔ One assertion, so neither half can mask the other: a second reader that
    # REPLACES the one reader must name its own line, not only the missing hand-off.
    handed = {site.name for site in found if site.use == HANDED}
    unreached = sorted(set(ONE_READER_REACHED) - handed)
    assert (findings(found, DECLARED), unreached) == ([], [])


def test_every_declaration_is_a_named_role_and_a_parser_lives_in_the_container_package():
    for name, (role, why) in DECLARED.items():
        assert role in (PARSER, WRITER), name
        assert why.strip(), name
        assert role != PARSER or name.startswith(PARSER_HOME), name


def plant(root: Path, where: str, source: str) -> list:
    """Write one planted module into a synthetic `src/` + `tests/` tree and sweep it."""
    (root / "src").mkdir(exist_ok=True)
    (root / "tests").mkdir(exist_ok=True)
    (root / where).parent.mkdir(parents=True, exist_ok=True)
    (root / where).write_text(source, encoding="utf-8")
    found, swept = sites(root)
    assert swept == 1, swept
    return found


TO_PLACEMENT = (
    'def placed(profile, address, unit):\n    return profile.unit(address, 1, "t", origin={})\n'
)

SECOND_READERS = {
    "tests, W95/3's own shape": ("tests/planted.py", TO_PLACEMENT.format('unit.get("origin")')),
    "src, the same": ("src/studyforge/planted.py", TO_PLACEMENT.format('unit.get("origin")')),
    "subscript": ("tests/planted.py", TO_PLACEMENT.format('unit["origin"]')),
    "pop": ("tests/planted.py", TO_PLACEMENT.format('unit.pop("origin")')),
    "concatenated key": ("tests/planted.py", TO_PLACEMENT.format('unit["ori" + "gin"]')),
    "module constant": (
        "tests/planted.py",
        'ORIGIN = "origin"\n' + TO_PLACEMENT.format("unit.get(ORIGIN)"),
    ),
    "local, through a walrus": (
        "tests/planted.py",
        TO_PLACEMENT.format('unit[(key := "origin")] or unit[key]'),
    ),
    "loop variable": (
        "tests/planted.py",
        'def placed(unit):\n    for key in ("n", "origin"):\n        use(unit[key])\n',
    ),
    "imported constant, through a module": (
        "tests/planted.py",
        "from studyforge.corpus import container\n"
        "def placed(unit):\n    return [use(unit[key]) for key in container.UNIT_KEYS]\n",
    ),
    "match mapping": (
        "src/studyforge/planted.py",
        'def placed(unit):\n    match unit:\n        case {"origin": o}:\n            return o\n',
    ),
    "a local function that only shares the reader's name": (
        "tests/planted.py",
        "def optional_origin(value, what, where):\n    return value, None\n"
        'origin, _ = optional_origin(unit.get("origin"), "o", "w")\n',
    ),
}


@pytest.mark.parametrize("case", SECOND_READERS, ids=list(SECOND_READERS))
def test_a_planted_second_reader_is_refused(tmp_path, case):
    where, source = SECOND_READERS[case]
    found = plant(tmp_path, where, source)
    assert found and {site.use for site in found} == {BARE}, found
    refused = findings(found, {})
    assert len(refused) == len(found), refused
    assert all("a second reader" in line for line in refused), refused


def test_a_declared_writer_that_also_reads_is_refused(tmp_path):
    source = (
        "def built(profile, unit):\n"
        '    unit["origin"] = "a.md"\n'
        '    return profile.unit(None, 1, "t", origin=unit["origin"])\n'
    )
    found = plant(tmp_path, "tests/planted.py", source)
    refused = findings(found, {"tests/planted.py::built": (WRITER, "planted")})
    assert refused == [
        "tests/planted.py:3 read/bare in built: a second reader; hand it to fields.optional_origin"
    ]


def test_a_writer_not_declared_by_name_is_refused_and_a_stale_declaration_too(tmp_path):
    found = plant(tmp_path, "tests/planted.py", 'def built(unit):\n    unit["origin"] = "a.md"\n')
    assert findings(found, {}) == [
        "tests/planted.py:2 write/stored in built: a writer not declared by name"
    ]
    stale = {"tests/planted.py::gone": (WRITER, "planted")}
    assert findings(found, {**stale, "tests/planted.py::built": (WRITER, "planted")}) == [
        "tests/planted.py::gone: declared, and nothing there touches origin"
    ]


def test_a_parser_declared_outside_the_container_package_is_not_a_parser(tmp_path):
    found = plant(tmp_path, "tests/planted.py", 'def parse(unit):\n    return unit.get("origin")\n')
    assert len(findings(found, {"tests/planted.py::parse": (PARSER, "planted")})) == 1


# --- the positive row (Ruling 191(c)): what the instrument must ACCEPT -------------


@pytest.mark.parametrize(
    "imported",
    [
        "from studyforge.corpus.container.fields import optional_origin as read\n",
        "from studyforge.corpus.container import fields\n",
    ],
)
def test_a_read_handed_straight_to_the_one_reader_needs_no_name(tmp_path, imported):
    call = "read" if "as read" in imported else "fields.optional_origin"
    source = imported + f'def placed(unit):\n    return {call}(unit.get("origin"), "o", "w")\n'
    found = plant(tmp_path, "tests/planted.py", source)
    assert [site.use for site in found] == [HANDED]
    assert findings(found, {}) == []


def test_a_declared_writer_may_store_assert_and_transcribe(tmp_path):
    source = (
        "def built(unit, document):\n"
        '    unit["origin"] = "a.md"\n'
        '    del unit["origin"]\n'
        '    assert document["origin"] == "a.md"\n'
        '    return {"origin": unit["origin"]}\n'
    )
    found = plant(tmp_path, "tests/planted.py", source)
    assert [site.use for site in found] == ["stored", "deleted", ASSERTED, TRANSCRIBED]
    assert findings(found, {"tests/planted.py::built": (WRITER, "planted")}) == []


def test_the_parser_may_read_inside_its_own_package(tmp_path):
    where = PARSER_HOME + "document.py"
    found = plant(tmp_path, where, 'def from_document(d):\n    return d.get("origin")\n')
    assert findings(found, {f"{where}::from_document": (PARSER, "planted")}) == []


# --- what is not an access, and the stated survivors (Ruling 56) ---------------------

NOT_ACCESSES = {
    "a dict display": 'unit = {"n": 1, "origin": "a.md"}\n',
    "a membership test": 'bare = "origin" in unit\n',
    "a docstring that quotes the defect": '"""Never `unit.get("origin")`."""\n',
    "another document key": 'path = region["path"]\n',
}

SURVIVORS = {
    "a key passed in as a parameter": (
        'def read(unit, key):\n    return use(unit[key])\nread(u, "origin")\n'
    ),
    "a document unpacked with **": "profile.unit(address, **unit)\n",
    "a key found by iterating items()": (
        'for k, v in unit.items():\n    if k == "origin":\n'
        '        profile.unit(a, 1, "t", origin=v)\n'
    ),
    "operator.itemgetter": 'import operator\norigin = operator.itemgetter("origin")(unit)\n',
    "an f-string with a formatted constant": "origin = unit[f\"{'origin'}\"]\n",
}


@pytest.mark.parametrize("source", list(NOT_ACCESSES.values()), ids=list(NOT_ACCESSES))
def test_what_is_not_an_access_is_not_in_the_population(tmp_path, source):
    assert plant(tmp_path, "tests/planted.py", source) == []


@pytest.mark.parametrize("source", list(SURVIVORS.values()), ids=list(SURVIVORS))
def test_the_stated_survivors_do_survive(tmp_path, source):
    # ⚠️ Reading the limit, so the module docstring's claim about it is measured.
    assert findings(plant(tmp_path, "tests/planted.py", source), {}) == []


def test_a_value_transcribed_under_another_key_survives_in_a_declared_writer(tmp_path):
    source = (
        "def built(profile, unit):\n"
        '    copy = {"o": unit["origin"]}\n'
        '    return profile.unit(None, 1, "t", origin=copy["o"])\n'
    )
    found = plant(tmp_path, "tests/planted.py", source)
    assert findings(found, {"tests/planted.py::built": (WRITER, "planted")}) == []
