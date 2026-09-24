"""Mirror of `src/studyforge/skills/adapter/parts/__init__.py` (R12)."""

from __future__ import annotations

import json

from studyforge.corpus.manifest import parse
from studyforge.skills.adapter import parts as package
from studyforge.skills.adapter import plan_for, scaffold
from studyforge.skills.adapter.parts import ADAPTER_PARTS, PARTS, SUITE_PARTS
from tests.studyforge.skills.adapter import corpora
from tests.support import assert_package_contract


def plan():
    """The walkthrough corpus's plan."""
    return plan_for(parse(json.dumps(corpora.MANIFEST)))


def test_states_its_contract():
    assert_package_contract(package, "studyforge.skills.adapter.parts")


def test_the_list_is_the_two_halves_and_nothing_else():
    # ⭐ The list is data, so it is assertable: a renderer that is not in PARTS
    # is a file the procedure does not mention, and this is what would notice.
    assert PARTS == (*ADAPTER_PARTS, *SUITE_PARTS)
    assert len(PARTS) == 8


def test_the_adapter_comes_before_its_tests():
    # ⛔ Order, not just membership: a test for a module nobody has seen is a
    # test nobody reads.
    where = [part.where for part in PARTS]
    assert where.index("{package}/read.py") < where.index("tests/{package}/test_read.py")


def test_exactly_one_part_is_not_generated():
    hand = [part for part in PARTS if not part.generated]
    assert [part.where for part in hand] == ["{package}/read.py"]


def test_every_path_is_distinct_and_root_relative():
    where = [part.path_for(plan()) for part in PARTS]
    assert len(set(where)) == len(where), "two parts claim one path"
    assert all(not path.startswith(("/", ".")) for path in where)


def test_the_package_name_reaches_every_path():
    where = [part.path_for(plan()) for part in PARTS]
    assert all("{package}" not in path for path in where), "a path kept its placeholder"
    assert all("ingest" in path for path in where)


def test_no_part_renders_an_empty_file():
    # ⚠️ Over the parts' own files: a scaffold also carries the short bytecode
    # ignore files it derives, which are no part and are held in test_scaffold.
    made = scaffold(plan())
    rendered = [item for item in made.files if item.where in made.paths[: len(PARTS)]]
    assert len(rendered) == len(PARTS)
    assert all(item.text.strip() for item in rendered)
    assert all(item.length > 5 for item in rendered)
