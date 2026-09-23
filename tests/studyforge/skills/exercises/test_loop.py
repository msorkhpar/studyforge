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

from studyforge.archive.document import build, render
from studyforge.skills.adapter import Layout
from studyforge.skills.exercises import (
    ATTEMPTS,
    AuthoringError,
    author_corpus,
    author_page,
    carried_practices,
    gate_code,
    gate_quiz,
    require_after_carried,
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
        pages[GREETING],
        ledger,
        author,
        None,
        Running(),
        source="demo",
        where="the page",
        carried=(),
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
        author_page(
            pages[GREETING], ledger, author, None, None, source="demo", where="p", carried=()
        )


@pytest.mark.parametrize("function", [author_corpus, author_page, gate_code, gate_quiz])
def test_no_gate_budget_or_option_can_be_handed_to_the_loop(function):
    # ⛔ Spec §7 §11: never by loosening a gate. There is no parameter through
    # which a caller could name a gate to skip or a budget to widen.
    named = set(inspect.signature(function).parameters)
    loosening = {"gates", "skip", "budget", "attempts", "options", "strict", "only"}
    assert not named & loosening, f"{function.__name__} takes {sorted(named & loosening)}"
    assert isinstance(ATTEMPTS, int) and ATTEMPTS >= 2, "a budget with no room for a retry"


# ⛔ W437: a unit may already carry practices — the first corpus's
# `iso-fundamentals` units 2, 3 and 4 each carry a bundled `practice-1` — and
# an authored exercise numbered from 1 would collide with it. ⭐ What a unit
# carries is READ off its archive, never declared, and authoring numbers after it.


def _carry(root, page, ordinals):
    """Archive a `bundled`-shaped practice for each ordinal on the page's unit, as ingestion would."""
    written = []
    for ordinal in ordinals:
        document = build(
            source="demo",
            address=page.address,
            variant=page.variant,
            unit=page.unit,
            kind="practice",
            ordinal=ordinal,
            ingested="2026-01-05",
            title=f"The source's own practice {ordinal}",
            blocks=[{"type": "para", "text": "A practice the source shipped."}],
        )
        path = Layout(root).document(page.address, page.variant, page.unit, "practice", ordinal)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(document), encoding="utf-8")
        written.append(path.relative_to(root).as_posix())
    return written


def test_what_a_unit_carries_is_read_off_its_archive(tmp_path):
    page = fixture_pages()[GREETING]
    assert carried_practices(tmp_path, page, "p") == (), "a unit with no archive carries nothing"
    _carry(tmp_path, page, (1, 2))
    assert carried_practices(tmp_path, page, "p") == (1, 2)
    other = fixture_pages()[GREETING + 1]
    assert carried_practices(tmp_path, other, "p") == (), "another unit's practices were read"


def test_a_unit_whose_archived_practices_have_a_gap_is_refused(tmp_path):
    page = fixture_pages()[GREETING]
    _carry(tmp_path, page, (1, 3))
    with pytest.raises(AuthoringError, match="no gap and no repeat"):
        carried_practices(tmp_path, page, "p")


def test_a_unit_that_carries_a_practice_numbers_its_authored_exercises_after_it(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    author = Scripted({pages[GREETING].path: [greeting]})
    outcome = author_page(
        pages[GREETING], ledger, author, None, Running(), source="demo", where="p", carried=(1,)
    )
    assert outcome.shipped, "nothing shipped, so this asserts nothing"
    ordinals = [gated.places.ordinal for gated in outcome.shipped]
    assert ordinals == list(range(2, len(ordinals) + 2)), "authored exercises did not follow"
    assert author.briefs[0].places.ordinal == 2, "the author was briefed at a carried ordinal"


def test_the_whole_pass_numbers_after_the_archive_and_leaves_its_practice_untouched(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    (kept,) = _carry(tmp_path, pages[GREETING], (1,))
    before = snapshot(tmp_path)[kept]
    _, authored = _again(tmp_path, material, graders, pages[:1], {pages[0].path: [greeting]})
    (covered,) = authored.pages
    assert covered.shipped and all(not b.endswith("/practice-1") for b in covered.shipped)
    assert covered.shipped[0].endswith("/practice-2"), "the first authored one is not next"
    assert snapshot(tmp_path)[kept] == before, "the source's own practice was rewritten"
    # ⭐ R10: a re-run with nothing changed reads the same unit and writes nothing.
    after = snapshot(tmp_path)
    author, again = _again(tmp_path, material, graders, pages[:1], {pages[0].path: [greeting]})
    assert again.written == () and author.briefs == [] and snapshot(tmp_path) == after


@pytest.mark.parametrize(
    ("carried", "shipped", "says"),
    [((1,), (1,), "practice-1"), ((1, 2), (2, 3), "practice-2"), ((1,), (3,), "no gap")],
)
def test_an_authored_ordinal_that_collides_or_leaves_a_gap_is_refused_by_name(
    carried, shipped, says
):
    with pytest.raises(AuthoringError, match=says):
        require_after_carried(carried, shipped, "p")
    assert require_after_carried(carried, (len(carried) + 1,), "p") is None
