"""Mirror of `tools/quality/vacuity.py` (R12).

⛔ Every assertion here runs BOTH ways (R12, `W309`): an empty population is named,
and an inhabited one is not — over fabricated temp trees, and over this repository.
Nothing here reads, prints or writes an identity value; the identifier arm's VALUES
are `W307`'s and are asserted in `personal_data/test_identity.py`.
"""

from __future__ import annotations

import inspect

import pytest

import tools.quality as quality
from tests.support import repository_root
from tools.quality import config, run_all
from tools.quality.approach import approach_notice
from tools.quality.board import board_state
from tools.quality.clauses import clause_census
from tools.quality.collisions import collision_census
from tools.quality.counts import count_census
from tools.quality.creators import creator_census
from tools.quality.docstrings import check_docstrings
from tools.quality.handoffs import handoff_citations
from tools.quality.handoffs.existence import handoff_existence
from tools.quality.handoffs.sweep import pattern_sites
from tools.quality.mirror import check_mirrors
from tools.quality.personal_data import identity_notice
from tools.quality.personal_data.identity import check_identifiers
from tools.quality.personal_data.registry import check_registry
from tools.quality.personal_data.shapes import check_shapes
from tools.quality.pointers import pointer_coverage
from tools.quality.reach import reach_notice
from tools.quality.rulings import rulings_notice
from tools.quality.source_names import check_source_names
from tools.quality.style import check_style
from tools.quality.surfaces import surface_census
from tools.quality.vacuity import DISCLOSED_BY, POPULATIONS, TAG, vacuity_notice

#: ⛔ What each paired notice SAYS over a tree where its check compared nothing. A
#: fragment, never the whole line, so a notice's wording can grow without this
#: breaking — and each one is asserted ABSENT over this repository, below.
EMPTY_READINGS = {
    approach_notice: "of the 0 scanned",
    board_state: "board: none",
    handoff_citations: "the population is EMPTY",
    handoff_existence: "in this checkout, so no row can owe one",
    pointer_coverage: "0 read in 0 markdown files",
    collision_census: "in 0 markdown documents",
    rulings_notice: "no ruling records in this checkout",
    reach_notice: "no ruling records in this checkout",
    clause_census: "headings in 0 documents",
    count_census: "in the prose of 0 Python files",
    creator_census: "not read, no",
    surface_census: "no package was read",
}

#: The function that ACTUALLY iterates each population, so a test can assert the
#: disclosure reads the same walk as the verdict.
READERS = {
    "check_mirrors": (check_mirrors, "mirrored(root)"),
    "check_docstrings": (check_docstrings, "contract_modules(root)"),
    "check_style": (check_style, "config.python_files(root)"),
    "check_personal_data (shapes arm)": (check_shapes, "swept_files(root)"),
    "check_personal_data (identifier arm)": (check_identifiers, "config.text_files(root)"),
    "check_personal_data (registry arm)": (check_registry, "judged_directories(root)"),
    "check_source_names": (check_source_names, "framework_modules(root)"),
    "check_marker_patterns": (pattern_sites, "convention_documents(root, directory)"),
}


def write(root, relative, text='"""A fabricated module for a temp tree, nothing more."""\n'):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def inhabit(root):
    """Give every population in `POPULATIONS` at least one member."""
    write(root, "src/studyforge/placeholder.py")
    write(root, "tools/placeholder.py")
    write(root, "docs/conventions/placeholder.md", "# Placeholder\n")
    (root / config.SANCTIONED_PERSONAL_DATA_DIRS[0]).parent.mkdir(parents=True)


@pytest.fixture(scope="module")
def repository_notices():
    root = repository_root()
    return {notice: "\n".join(notice(root)) for notice in EMPTY_READINGS}


def test_every_check_is_answered_for():
    answered = {check for check, _notice in DISCLOSED_BY} | {p.check for p in POPULATIONS}
    assert quality.CHECKS, "Ruling 48: an empty registry satisfies set() == set()"
    assert answered == set(quality.CHECKS)


def test_every_pairing_names_a_REGISTERED_notice():
    for _check, notice in DISCLOSED_BY:
        assert notice in quality.NOTICES, notice.__name__


def test_every_paired_notice_has_an_empty_reading_or_is_W307s():
    # ⚠️ `identity_notice` reads the MACHINE, not the tree, so an empty temp tree
    # says nothing about it; its both-ways pins live in `test_identity.py`.
    paired = {notice for _check, notice in DISCLOSED_BY} - {identity_notice}
    assert paired == set(EMPTY_READINGS)


@pytest.mark.parametrize("notice", list(EMPTY_READINGS), ids=lambda n: n.__name__)
def test_a_paired_notice_SAYS_its_population_was_empty(notice, tmp_path):
    assert EMPTY_READINGS[notice] in "\n".join(notice(tmp_path))


@pytest.mark.parametrize("notice", list(EMPTY_READINGS), ids=lambda n: n.__name__)
def test_a_paired_notice_does_NOT_read_empty_over_this_repository(notice, repository_notices):
    assert repository_notices[notice], f"{notice.__name__} printed nothing here"
    assert EMPTY_READINGS[notice] not in repository_notices[notice]


def test_an_EMPTY_tree_names_every_population_in_ONE_line(tmp_path):
    lines = vacuity_notice(tmp_path)
    assert len(lines) == 1
    assert lines[0].startswith(TAG)
    for population in POPULATIONS:
        assert f"{population.label()} read 0 {population.noun}" in lines[0]


def test_an_INHABITED_tree_prints_NOTHING(tmp_path):
    inhabit(tmp_path)
    for population in POPULATIONS:
        assert len(population.members(tmp_path)), population.label()
    assert vacuity_notice(tmp_path) == []


def test_a_PARTLY_empty_tree_names_only_the_empty_ones(tmp_path):
    # ⭐ `W307/3`'s visible candidate: Python exists, none of it under `src/`.
    write(tmp_path, "tests/test_placeholder.py")
    (line,) = vacuity_notice(tmp_path)
    assert "check_source_names read 0" in line
    assert "check_mirrors read 0" in line
    assert "check_docstrings read 0" in line
    assert "check_style read 0" not in line
    assert "(shapes arm) read 0" not in line
    assert "(identifier arm) read 0" not in line


def test_this_repository_prints_NOTHING():
    # ⛔ The row forbids a disclosure printed on every green run.
    root = repository_root()
    for population in POPULATIONS:
        assert len(population.members(root)), population.label()
    assert vacuity_notice(root) == []


def test_it_is_a_NOTICE_and_can_never_redden_the_floor(tmp_path):
    assert vacuity_notice not in quality.CHECKS
    assert vacuity_notice(tmp_path)
    assert run_all(tmp_path) == []


def test_every_population_is_the_one_its_check_ITERATES():
    # ⛔ A disclosure over a restated walk could say *inhabited* over a verdict
    # reached on an empty one (`W307`'s decision 2).
    assert {p.label() for p in POPULATIONS} == set(READERS)
    for label, (reader, call) in READERS.items():
        assert call in inspect.getsource(reader), label
