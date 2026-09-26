"""Mirror of `src/studyforge/skills/exercises/loop.py` (R12) — the budget, the retry, the report.

**What it asserts.** The re-authoring loop: a planted
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
from dataclasses import replace

import pytest

from studyforge.archive.document import build, render
from studyforge.exercise import CODE, QUIZ
from studyforge.exercise.bundle import BUNDLE_FILENAME
from studyforge.skills.adapter import Layout
from studyforge.skills.exercises import (
    ATTEMPTS,
    PERSONAL_DATA,
    QUIZ_DOCUMENT,
    AuthoringError,
    author_corpus,
    author_page,
    carried_practices,
    gate_code,
    gate_quiz,
    quiz_of,
    require_after_carried,
    take,
)
from tests.studyforge.skills.exercises.authoring import (
    BLANK,
    GIVEAWAY,
    GREETS,
    GivingAway,
    Judging,
    Running,
    Scripted,
    gauge,
    gauge_keyed_twice,
    gauge_that_deletes_a_question,
    greeting,
    greeting_and_its_quiz,
    greeting_that_drops_its_edge,
    greeting_whose_plant_handles_its_edge,
    greeting_with_a_vacuous_ask,
    mixed,
    shout,
    snapshot,
    write_corpus,
)
from tests.studyforge.skills.exercises.authoring import pages as fixture_pages

#: The code page with tests, and the prose page, by position in `pages()`.
GREETING, GAUGE = 0, 3


def _pass(root, pages, script, judge=None):
    """Write the corpus under `root` and run one pass over `pages` with this script."""
    material, graders, _ = write_corpus(root)
    return _again(root, material, graders, pages, script, judge)


def _again(root, material, graders, pages, script, judge=None):
    """Run one pass over a corpus already on disk."""
    author = Scripted(script)
    authored = author_corpus(
        root,
        source="demo",
        material=material,
        graders=graders,
        pages=pages,
        author=author,
        judge=Judging() if judge is None else judge,
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


def test_a_retry_after_a_q2_giveaway_is_briefed_with_the_reader_s_reason(tmp_path):
    # ⛔ A Q2 refusal is never answered by re-asking with the same brief: the
    # retry carries the cue the page-free reader named.
    pages = fixture_pages()
    judge = GivingAway(times=1)
    author, authored = _pass(
        tmp_path, pages[GAUGE : GAUGE + 1], {pages[GAUGE].path: [gauge]}, judge
    )
    first, second = author.briefs
    print("refused on the retry:", [(v.id, v.says) for v in second.refused])
    assert judge.calls == 2 and authored.shortfalls == ()
    assert first.refused == () and [verdict.id for verdict in second.refused] == ["Q2"]
    assert GIVEAWAY in second.refused[0].says, "the retry was not told which cue gave it away"
    assert first != second


def test_a_quiz_every_reading_gives_away_is_reported_with_the_reason(tmp_path):
    pages = fixture_pages()
    script = {pages[GAUGE].path: [gauge]}
    author, authored = _pass(tmp_path, pages[GAUGE : GAUGE + 1], script, GivingAway(ATTEMPTS))
    assert len(author.briefs) == ATTEMPTS
    assert all(GIVEAWAY in brief.refused[0].says for brief in author.briefs[1:])
    ((_, missed),) = authored.shortfalls
    print(missed.gate, missed.says)
    assert missed.gate == "Q2" and GIVEAWAY in missed.says


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


# ⛔ A unit may already carry practices — a bundled `practice-1`, say — and
# an authored exercise numbered from 1 would collide with it. ⭐ What a unit
# carries is READ off its archive, never declared, and authoring numbers after it.


#: ⭐ A practice an earlier authoring pass generated, as an adapter archives it:
#: a quiz, whose record leaves its provenance to be read as `generated`.
GENERATED = {
    "kind": "quiz",
    "questions": [
        {
            "id": "q-1",
            "stem": "What does the greeting name?",
            "options": [
                {"id": "a", "text": "Who it greets", "correct": True, "says": "It names them."},
                {"id": "b", "text": "The time", "correct": False, "says": "No clock is read."},
            ],
            "origin": {"path": "lessons/greeting.md", "section": "The function"},
        }
    ],
}


def _carry(root, page, ordinals, generated=()):
    """Archive a practice for each ordinal on the page's unit, as ingestion would.

    ⭐ An ordinal in `generated` is archived as an earlier authoring pass left it.
    """
    written = []
    for ordinal in ordinals:
        extra = {"exercise": GENERATED} if ordinal in generated else {}
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
            **extra,
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


# ⭐ A unit may carry code practices AND a quiz. The quiz is one planned
# exercise of the code page, named by `Page.quiz`, drafted after the code.


def test_a_code_page_carries_its_quiz_after_its_code(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    page = mixed(pages[GREETING])
    author, authored = _again(
        tmp_path, material, graders, [page], {page.path: [greeting_and_its_quiz]}
    )
    assert authored.shortfalls == () and authored.bare == ()
    # ⭐ Asked for code first and the quiz last, each by the brief's own kind.
    assert [(brief.kind, brief.name) for brief in author.briefs] == [
        (CODE, "greet"),
        (QUIZ, "check"),
    ]
    (covered,) = authored.pages
    code, asked = (tmp_path / bundle for bundle in covered.shipped)
    assert (code / BUNDLE_FILENAME).is_file() and not (code / QUIZ_DOCUMENT).exists()
    assert asked.name == "practice-2" and not (asked / BUNDLE_FILENAME).exists()
    quiz = quiz_of(
        json.loads((asked / QUIZ_DOCUMENT).read_text(encoding="utf-8")), covered.shipped[1]
    )
    assert quiz.exercise.is_quiz and quiz.places.ordinal == 2
    # ⛔ The quiz's key lives in its bundle, never in a workspace a reader is handed.
    workspace = tmp_path / "practice" / "kata" / "python" / "unit-01"
    assert [one.name for one in sorted(workspace.iterdir())] == ["practice-1"]
    (report,) = tmp_path.glob("exercises/**/coverage.json")
    written = json.loads(report.read_text(encoding="utf-8"))
    assert (written["kind"], written["quiz"]) == (CODE, "check")
    # ⭐ R10: a re-run with nothing changed asks nobody and writes nothing.
    after = snapshot(tmp_path)
    again, rerun = _again(tmp_path, material, graders, [page], {page.path: [greeting_and_its_quiz]})
    assert again.briefs == [] and rerun.written == () and snapshot(tmp_path) == after


def test_a_quiz_no_aspect_names_or_a_quiz_on_a_quiz_page_is_refused(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    author = Scripted({})
    unplanned = replace(pages[GREETING], quiz="check")
    with pytest.raises(AuthoringError, match="names a quiz that no aspect"):
        author_page(
            unplanned, ledger, author, Judging(), Running(), source="d", where="p", carried=()
        )
    on_a_quiz = replace(pages[GAUGE], quiz="notes")
    with pytest.raises(AuthoringError, match="only a 'code' page may"):
        _again(tmp_path, material, graders, [on_a_quiz], {})
    assert author.briefs == [], "a refused page was drafted"


def test_naming_a_quiz_on_a_unit_already_authored_is_refused_as_moved(tmp_path):
    # ⛔ The same aspects and the same plan, and one exercise now a quiz: the
    # committed code bundle was never a quiz, so the unit is refused by name.
    material, graders, pages = write_corpus(tmp_path)
    page = mixed(pages[GREETING])
    unnamed = replace(page, quiz=None)
    script = {page.path: [greeting_and_its_quiz]}
    _, authored = _again(tmp_path, material, graders, [unnamed], script)
    assert len(authored.pages[0].shipped) == 2, "both exercises should ship as code"
    before = snapshot(tmp_path)
    with pytest.raises(AuthoringError, match="unit-01.*has since moved"):
        _again(tmp_path, material, graders, [page], script)
    assert snapshot(tmp_path) == before, "a refused pass wrote something"


def test_a_practice_an_earlier_pass_generated_is_never_carried(tmp_path):
    # ⛔ Ruled: only the source's own practices are carried. A unit authored
    # again after its bundles were removed still has the old authored practice
    # in its archive, and it must not push the new exercises past it.
    page = fixture_pages()[GREETING]
    _carry(tmp_path, page, (1, 2), generated=(2,))
    assert carried_practices(tmp_path, page, "p") == (1,)


def test_a_unit_authored_again_numbers_from_the_source_s_own_practices(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    _carry(tmp_path, pages[GREETING], (1,), generated=(1,))
    _, authored = _again(tmp_path, material, graders, pages[:1], {pages[0].path: [greeting]})
    (covered,) = authored.pages
    assert covered.shipped and covered.shipped[0].endswith("/practice-1"), covered.shipped


def test_the_author_s_order_sets_the_plan_and_the_quiz_is_still_drafted_last(tmp_path):
    # ⭐ The page's `order` is the plan's teaching order; the quiz it names is
    # drafted after every code exercise wherever the order puts it.
    material, graders, pages = write_corpus(tmp_path)
    page = replace(mixed(pages[GREETING]), order=("check", "greet"))
    ledger = take(tmp_path, material, graders, "the ledger")
    author = Scripted({page.path: [greeting_and_its_quiz]})
    outcome = author_page(
        page, ledger, author, Judging(), Running(), source="demo", where="p", carried=()
    )
    assert [planned.name for planned in outcome.plan.exercises] == ["check", "greet"]
    assert [(brief.kind, brief.places.ordinal) for brief in author.briefs] == [
        (CODE, 1),
        (QUIZ, 2),
    ]


#: ⚠️ Built by concatenation so no file in this tree spells a machine name (R7).
MACHINE = "db" + ".local"


def _shout_naming_a_machine(brief):
    """⛔ The measured leak: a statement that names a `.local` host, as S2's did."""
    draft = shout(brief)
    return replace(draft, statement=draft.statement + f"It connects to {MACHINE} on port 5432.\n")


def test_a_draft_carrying_personal_data_refuses_that_exercise_and_the_pass_carries_on(tmp_path):
    pages = fixture_pages()[:2]
    script = {pages[0].path: [greeting], pages[1].path: [_shout_naming_a_machine]}
    author, authored = _pass(tmp_path, pages, script)
    ((page, missed),) = authored.shortfalls
    # ⭐ The plant, OBSERVED: R7's own gate refused the host the statement names.
    assert "local hostname" in missed.says, missed.says
    assert (page, missed.slot, missed.gate) == (pages[1].path, 1, PERSONAL_DATA)
    assert "personal data" in missed.says and MACHINE not in missed.says
    assert len(author.briefs) == 1 + ATTEMPTS, "the retry was not briefed, or the pass stopped"
    assert author.briefs[-1].refused[0].id == PERSONAL_DATA
    # ⛔ The other exercise's gate runs were not lost: it shipped and was committed.
    shipped = [path.parent.name for path in tmp_path.glob("exercises/**/bundle.json")]
    print("shipped:", shipped, "refused:", missed.says)
    assert len(shipped) == 1
    committed = [one.read_text(encoding="utf-8") for one in tmp_path.glob("exercises/**/*.*")]
    assert committed and not any(MACHINE in text for text in committed)
