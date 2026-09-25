"""Mirror of `src/studyforge/skills/exercises/drafts.py` (R12) — the case, the page, no retreat.

**What it asserts.** That spec §7 §1's three cases are READ off the ledger,
that `words_of` leaves every fence out, that a page the ledger cannot account
for is refused, that a draft of the wrong kind is refused, and that a retry
carrying fewer case or question ids than the draft it replaces is refused — by
id, so swapping the hard case for an easy one is caught too.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from studyforge.exercise import EDGE, Case
from studyforge.exercise.bundle import Places
from studyforge.skills.exercises import (
    CODE_AND_TESTS,
    CODE_NO_TESTS,
    NEITHER,
    SOURCE_CASES,
    AuthoringError,
    Brief,
    require_draft,
    require_no_retreat,
    require_page,
    source_case,
    take,
    words_of,
)
from tests.studyforge.skills.exercises.authoring import (
    BLANK,
    gauge,
    gauge_that_deletes_a_question,
    greeting,
    greeting_that_drops_its_edge,
    write_corpus,
)


def _ledger(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    return take(tmp_path, material, graders, "the ledger"), pages


def _brief(page) -> Brief:
    return Brief(page, NEITHER, 1, Places(page.address, page.variant, page.unit, 1), 1, ())


def test_the_three_cases_are_read_off_the_ledger(tmp_path):
    ledger, pages = _ledger(tmp_path)
    read = [source_case(page, ledger) for page in pages[:3]]
    assert read == [CODE_AND_TESTS, CODE_NO_TESTS, NEITHER] == list(SOURCE_CASES)


def test_a_page_s_case_ignores_what_its_author_might_prefer(tmp_path):
    # ⛔ The same page with its grader undeclared is read as the case it then
    # is — the case follows the ledger and the declaration, never a draft.
    ledger, pages = _ledger(tmp_path)
    assert source_case(replace(pages[0], graders=()), ledger) == CODE_NO_TESTS


def test_words_of_counts_prose_and_leaves_every_fence_out():
    prose = "one two three\n"
    fenced = prose + "```python\nfour five six seven\n```\n"
    assert words_of(prose) == 3
    assert words_of(fenced) == 3, "a fence's body or its language tag was counted"


def test_a_page_the_ledger_did_not_read_is_refused(tmp_path):
    ledger, pages = _ledger(tmp_path)
    with pytest.raises(AuthoringError, match="not material the ledger read"):
        require_page(replace(pages[0], path="lessons/absent.md"), ledger, "p")
    with pytest.raises(AuthoringError, match="does not carry as a grader"):
        require_page(replace(pages[1], graders=("checks/absent.py",)), ledger, "p")
    with pytest.raises(AuthoringError, match="declares a kind"):
        require_page(replace(pages[1], kind="essay"), ledger, "p")


def test_a_draft_of_the_wrong_kind_is_refused(tmp_path):
    _, pages = _ledger(tmp_path)
    with pytest.raises(AuthoringError, match="asked for a CodeDraft"):
        require_draft(pages[0], gauge(_brief(pages[0])), "p")
    with pytest.raises(AuthoringError, match="asked for a QuizDraft"):
        require_draft(pages[3], greeting(_brief(pages[3])), "p")


def test_a_retry_may_not_drop_a_case_or_delete_a_question(tmp_path):
    _, pages = _ledger(tmp_path)
    code = greeting(_brief(pages[0]))
    with pytest.raises(AuthoringError, match="drops 1 case"):
        require_no_retreat(code, greeting_that_drops_its_edge(_brief(pages[0])), "p")
    quiz = gauge(_brief(pages[3]))
    with pytest.raises(AuthoringError, match="drops 1 question"):
        require_no_retreat(quiz, gauge_that_deletes_a_question(_brief(pages[3])), "p")


def test_swapping_the_refused_case_for_an_easier_one_is_a_retreat_too(tmp_path):
    _, pages = _ledger(tmp_path)
    code = greeting(_brief(pages[0]))
    easier = Case("test_an_easy_thing", EDGE, "something easy")
    swapped = replace(code, cases=(code.cases[0], easier), plants={easier.id: "x"})
    assert len(swapped.cases) == len(code.cases), "the swap is not count-preserving"
    with pytest.raises(AuthoringError, match="drops 1 case"):
        require_no_retreat(code, swapped, "p")


def test_a_retry_that_keeps_every_case_and_adds_one_is_accepted(tmp_path):
    _, pages = _ledger(tmp_path)
    code = greeting(_brief(pages[0]))
    more = Case("test_a_second_edge", EDGE, "a second edge")
    grown = replace(code, cases=(*code.cases, more), plants={BLANK.id: "x", more.id: "y"})
    assert require_no_retreat(code, grown, "p") is grown
