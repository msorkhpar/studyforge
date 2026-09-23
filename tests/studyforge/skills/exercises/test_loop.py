"""Mirror of `src/studyforge/skills/exercises/loop.py` (R12) — the budget, the retry, the report.

**What it asserts.** `AX-08`'s Acceptance on the re-authoring loop: a planted
gate failure is re-authored inside the budget; a plant that cannot clear
exhausts the budget and is reported rather than shipped, naming the page, the
exercise, the gate, the case and the run's last output; and a retry that drops
a case or deletes a question is refused rather than shipped — ⛔ a gate failure
is never answered by asking less.

⭐ **Each plant is observed, not assumed**: every refusal below is read off a
gate verdict the real runs produced, and each test prints nothing it did not
first assert was planted.
"""

from __future__ import annotations

import inspect
import json

import pytest

from studyforge.skills.exercises import (
    ATTEMPTS,
    AuthoringError,
    author_corpus,
    author_page,
    gate_code,
    gate_quiz,
    take,
)
from tests.studyforge.skills.exercises.authoring import (
    BLANK,
    GREETS,
    Judging,
    Running,
    Scripted,
    gauge,
    gauge_keyed_twice,
    gauge_that_deletes_a_question,
    greeting,
    greeting_that_drops_its_edge,
    greeting_whose_plant_handles_its_edge,
    greeting_with_a_vacuous_ask,
    snapshot,
    write_corpus,
)
from tests.studyforge.skills.exercises.authoring import pages as fixture_pages

#: The code page with tests, and the prose page, by position in `pages()`.
GREETING, GAUGE = 0, 3


def _pass(root, pages, script):
    """Write the corpus under `root` and run one pass over `pages` with this script."""
    material, graders, _ = write_corpus(root)
    return _again(root, material, graders, pages, script)


def _again(root, material, graders, pages, script):
    """Run one pass over a corpus already on disk."""
    author = Scripted(script)
    authored = author_corpus(
        root,
        source="demo",
        material=material,
        graders=graders,
        pages=pages,
        author=author,
        judge=Judging(),
        runner=Running(),
    )
    return author, authored


def test_a_planted_gate_failure_is_re_authored_inside_the_budget(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    script = {pages[GREETING].path: [greeting_whose_plant_handles_its_edge, greeting]}
    author = Scripted(script)
    outcome = author_page(
        pages[GREETING], ledger, author, None, Running(), source="demo", where="the page"
    )
    assert len(outcome.shipped) == 1 and outcome.shortfalls == ()
    first, second = author.briefs
    assert (first.attempt, second.attempt) == (1, 2) and 2 <= ATTEMPTS
    assert first.refused == () and first.previous is None
    # ⭐ The plant was real: the retry was handed G3's own refusal, naming the edge.
    assert [verdict.id for verdict in second.refused] == ["G3"]
    assert BLANK.says in second.refused[0].says
    assert second.previous is not None and second.output, "the retry was not told what failed"


def test_a_plant_that_cannot_clear_exhausts_the_budget_and_is_reported_not_shipped(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    script = {pages[GREETING].path: [greeting_with_a_vacuous_ask]}
    author, authored = _again(tmp_path, material, graders, pages[:1], script)
    assert len(author.briefs) == ATTEMPTS, "the budget was not spent, or was exceeded"
    assert authored.bare == (pages[GREETING].path,), "a page with nothing shipped is not named"
    ((page, missed),) = authored.shortfalls
    assert (page, missed.slot, missed.gate) == (pages[GREETING].path, 1, "G2")
    assert GREETS.says in missed.says, "the report does not name the case the gate refused"
    assert missed.output and str(tmp_path) not in missed.output
    assert not list(tmp_path.glob("exercises/**/bundle.json")), "a refused exercise shipped"
    assert not (tmp_path / "practice").exists(), "a refused exercise wrote a workspace"
    (report,) = tmp_path.glob("exercises/**/coverage.json")
    written = json.loads(report.read_text(encoding="utf-8"))
    assert written["page"] == pages[GREETING].path and written["shipped"] == []
    (named,) = written["shortfalls"]
    assert list(named) == ["slot", "gate", "says", "output"]
    assert (named["gate"], named["says"], named["output"]) == ("G2", missed.says, missed.output)


def test_a_retry_that_drops_a_case_is_refused_and_nothing_is_written(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    retreat = [greeting_whose_plant_handles_its_edge, greeting_that_drops_its_edge]
    before = snapshot(tmp_path)
    with pytest.raises(AuthoringError, match="drops 1 case"):
        _again(tmp_path, material, graders, pages[:1], {pages[GREETING].path: retreat})
    assert snapshot(tmp_path) == before, "a pass refused for a retreat wrote something"


def test_a_quiz_defect_is_re_authored_and_a_deleted_question_is_refused(tmp_path):
    pages = fixture_pages()
    fixed = {pages[GAUGE].path: [gauge_keyed_twice, gauge]}
    author, authored = _pass(tmp_path / "fixed", pages[GAUGE : GAUGE + 1], fixed)
    assert len(author.briefs) == 2 and authored.shortfalls == ()
    assert [verdict.id for verdict in author.briefs[1].refused] == ["Q4"], "Q4 did not refuse"
    deleted = {pages[GAUGE].path: [gauge_keyed_twice, gauge_that_deletes_a_question]}
    with pytest.raises(AuthoringError, match="drops 1 question"):
        _pass(tmp_path / "deleted", pages[GAUGE : GAUGE + 1], deleted)


def test_a_page_whose_gates_have_nothing_to_run_them_is_refused(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    author = Scripted({pages[GREETING].path: [greeting]})
    with pytest.raises(AuthoringError, match="no runner"):
        author_page(pages[GREETING], ledger, author, None, None, source="demo", where="p")


@pytest.mark.parametrize("function", [author_corpus, author_page, gate_code, gate_quiz])
def test_no_gate_budget_or_option_can_be_handed_to_the_loop(function):
    # ⛔ Spec §7 §11: never by loosening a gate. There is no parameter through
    # which a caller could name a gate to skip or a budget to widen.
    named = set(inspect.signature(function).parameters)
    loosening = {"gates", "skip", "budget", "attempts", "options", "strict", "only"}
    assert not named & loosening, f"{function.__name__} takes {sorted(named & loosening)}"
    assert isinstance(ATTEMPTS, int) and ATTEMPTS >= 2, "a budget with no room for a retry"
