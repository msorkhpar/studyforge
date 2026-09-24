"""What a Submit reported, drawn in the panel, in a browser.

⛔ **WHY THIS NEEDS A BROWSER.** *"A Submit shows the breakdown, naming each
failed edge case"* is a claim about a page that has just finished a run: the
verdicts arrive on the run's own response body, one framed line per declared
case, and what the reader ends up reading is the join of those lines with the
cases Python rendered. ⭐ A text can read the script — and
`tests/studyforge/render/page/test_practice_breakdown.py` does — but it cannot
establish that the reader is shown *edge cases 1 of 2* rather than nothing.

⛔ **AND THE CHANNEL IS THE SUBJECT.** A built page may name no API and no origin
(R8), so the state namespace is out of reach and the run's stream is the
only thing the server already hands this page. ⚠️ **So the scripted run says
exactly what `serve.routes.breakdown` says**, in the place `routes.runs.Stream`
says it — just before the exit line — and a check that fetched the breakdown
some other way would have measured a page no reader has.

⛔ **The reader shown *edge cases 1 of 2* is looking at an INCOMPLETE practice
and never at a failed one.** The status line beside the breakdown is still the
run's own word, which is read here beside it.

⚠️ **The page this module opens is built by `site.build`'s own writer**, so the
stylesheet, the script and the serving process are real; only the one document
is this module's, because no fixture corpus declares `cases` yet.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from pathlib import Path

import pytest

from studyforge.render.page import render

#: ⭐ What the server says about one case, in the shape `serve.routes.breakdown`
#: says it. ⛔ Imported rather than typed, so a reworded line is a red check here
#: instead of a panel that quietly stops drawing anything.
from studyforge.serve.routes.breakdown import said
from tests.studyforge.render.page.sites import FIXTURES as UNIT_CASE_OF
from tests.visual import served, site
from tests.visual.page import OpenPage
from tests.visual.test_practice_panel import RUNNING, SETTLE

#: The corpus this module borrows a document and a placement from.
CORPUS = "depth2"

#: The name of the page this module writes beside that corpus's own unit page,
#: so every relative asset link the framework wrote resolves unchanged.
PAGE = "a-breakdown.unit.html"

#: A record that declares what it is checked IN: one main ask and two
#: edges, each with the sentence a reader is shown.
CASES = (
    {"id": "test_greets", "kind": "main", "says": "It greets the person named."},
    {"id": "test_empty", "kind": "edge", "says": "It handles an empty name."},
    {"id": "test_accent", "kind": "edge", "says": "It handles an accented name."},
)

BROKEN_DOWN = {
    "main_path": "practice/one/src/Greeter.java",
    "test_path": "practice/one/src/GreeterTest.java",
    "run_command": ["mvn", "-q", "compile"],
    "test_command": ["mvn", "-q", "test"],
    "provenance": "generated",
    "trust": "advisory",
    "cases": list(CASES),
    "report": {"format": "junit", "path": "reports"},
    "origin": {"path": "basics/01.md", "section": "What a class is"},
}

#: The whole breakdown, as the browser holds it now.
BREAKDOWN = """
(() => {
  const region = document.querySelector('[data-practice-part="breakdown"]');
  if (!region) return null;
  const rows = Array.from(region.querySelectorAll('[data-practice-case]'));
  return {
    hidden: region.hidden,
    live: region.getAttribute('aria-live'),
    summary: region.querySelector('[data-practice-part="summary"]').textContent.trim(),
    status: document.querySelector('[data-practice-part="status"]').textContent.trim(),
    output: document.querySelector('[data-practice-part="output"]').textContent,
    rows: rows.map((row) => ({
      id: row.getAttribute('data-practice-case'),
      kind: row.getAttribute('data-practice-case-kind'),
      verdict: row.getAttribute('data-practice-verdict'),
      text: row.textContent.trim()
    }))
  };
})()
"""

SUBMIT = """
document.querySelector('[data-practice-act="test"]').click()
"""


@pytest.fixture(scope="module")
def tree(tmp_path_factory: pytest.TempPathFactory) -> site.Site:
    """A real built tree, with one extra page whose practice declares a breakdown."""
    root = tmp_path_factory.mktemp("breakdown-site")
    built = site.build(root)
    case = UNIT_CASE_OF[CORPUS]()
    document = dict(case.document)
    document["sections"] = [
        dict(part, workspace=BROKEN_DOWN) if part.get("kind") == "practice" else part
        for part in document["sections"]
    ]
    where = Path(root / CORPUS / str(case.placement.unit.page))
    (where.parent / PAGE).write_bytes(render(document, case.placement))
    return built


@pytest.fixture
def panel(open_page: OpenPage, tree: site.Site) -> Iterator[tuple[OpenPage, served.Served]]:
    """The page on a SERVED origin, where Submit exists at all.

    ⛔ **`open_page` and never a tab of this module's own**, for
    `test_practice_quiz`'s reason: the browser's own verdict is reached in
    `conftest.py`, which is the one place licensed to reach it.
    """
    with served.serving(tree, CORPUS) as origin:
        open_page.open(f"{origin.origin}/{_where(tree)}")
        yield open_page, origin


def _where(tree: site.Site) -> str:
    """This module's page, relative to the origin's own root."""
    case = UNIT_CASE_OF[CORPUS]()
    return str(Path(str(case.placement.unit.page)).parent / PAGE)


def _submit(page: OpenPage, origin: served.Served, verdicts: dict[str, bool]) -> dict:
    """Press Submit against a run that reports `verdicts`, and read what is drawn."""
    origin.runs.said = tuple(said(case, verdicts[case]) for case in verdicts)
    page.evaluate(SUBMIT)
    origin.runs.started.wait(SETTLE)
    origin.runs.release.set()
    # ⛔ Polled and bounded, never slept through: a fixed sleep is either a slow
    # check or a flaky one, and the wait here is on a script the page runs.
    # ⚠️ Polled on THIS module's own reading, so what is waited for and what is
    # asserted are one object — a wait on a neighbouring module's reading is a
    # wait on a state this check never looks at.
    deadline = time.monotonic() + SETTLE
    drawn = dict(page.evaluate(BREAKDOWN))  # type: ignore[arg-type]
    while drawn["status"] in ("", RUNNING) and time.monotonic() < deadline:
        time.sleep(0.05)
        drawn = dict(page.evaluate(BREAKDOWN))  # type: ignore[arg-type]
    assert drawn["status"] not in ("", RUNNING), f"the run never finished; it reads {drawn}"
    return drawn


def test_a_failing_edge_is_named_and_the_count_says_how_many_are_left(panel):
    # ⛔ The Acceptance's first half. ⭐ Each failed edge is named by its OWN
    # sentence, which is the corpus's text (R1) and was rendered by Python —
    # only the verdict came off the wire.
    page, origin = panel
    drawn = _submit(page, origin, {"test_greets": True, "test_empty": True, "test_accent": False})
    assert drawn["hidden"] is False
    assert drawn["summary"] == "Main ask: done. Edge cases 1 of 2."
    assert [row["verdict"] for row in drawn["rows"]] == ["passed", "passed", "failed"]
    assert CASES[2]["says"] in [row["text"] for row in drawn["rows"]][2]


def test_a_passing_submit_shows_every_case_passed(panel):
    # ⛔ The Acceptance's second half, and it is not the first one's negation:
    # a run can exit zero with an edge still failing, so *every case passed* has
    # to be drawn from the cases and never from the exit code.
    page, origin = panel
    drawn = _submit(page, origin, {"test_greets": True, "test_empty": True, "test_accent": True})
    assert drawn["summary"] == "Main ask: done. Edge cases 2 of 2."
    assert [row["verdict"] for row in drawn["rows"]] == ["passed"] * 3


def test_the_breakdown_is_a_report_and_the_run_s_own_word_is_untouched(panel):
    # ⛔ **The clause this module is measured by.** A reader shown *edge cases 1 of
    # 2* is looking at an INCOMPLETE practice and not at a failed one: the run
    # exited zero, so the status line still says the run passed, and the two
    # sentences stand side by side saying different things on purpose.
    page, origin = panel
    drawn = _submit(page, origin, {"test_greets": False, "test_empty": True, "test_accent": False})
    assert drawn["status"] == "Passed."
    assert drawn["summary"] == "Main ask: not yet. Edge cases 1 of 2."


def test_every_verdict_is_a_word_and_the_region_is_announced(panel):
    # ⛔ The Acceptance: announced to a screen reader rather than only coloured.
    # ⚠️ Read as TEXT, so a stylesheet that lost both its rules would leave this
    # green and a page that said nothing would not.
    page, origin = panel
    drawn = _submit(page, origin, {"test_greets": True, "test_empty": False, "test_accent": True})
    assert drawn["live"] == "polite"
    assert drawn["rows"][0]["text"].startswith("Done")
    assert drawn["rows"][1]["text"].startswith("Not yet")


def test_a_case_line_is_never_left_standing_in_the_reader_s_own_output(panel):
    # ⚠️ A case line is the SERVER talking about this run, and the panel has
    # already drawn it — leaving it in the log beside the breakdown would show
    # the reader the same thing twice, once in the framework's words and once in
    # a frame. ⭐ The negative control: the program's OWN lines are all there.
    page, origin = panel
    drawn = _submit(page, origin, {"test_greets": True, "test_empty": True, "test_accent": True})
    assert "--- case " not in drawn["output"]
    assert "Running the grader…" in drawn["output"]


def test_a_breakdown_of_a_different_practice_is_shown_as_nothing(panel):
    # ⛔ A corpus regenerated after a Submit can change
    # the case map under a reader, and a breakdown whose population does not
    # match the panel's is not *edge cases 1 of 2* — it is a breakdown of a
    # different practice. ⭐ Shown as NOTHING rather than as a partial count.
    page, origin = panel
    drawn = _submit(page, origin, {"test_greets": True, "test_from_another_corpus": False})
    assert drawn["hidden"] is True
    assert drawn["summary"] == ""
    assert [row["verdict"] for row in drawn["rows"]] == [None, None, None]
