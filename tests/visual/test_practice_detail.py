"""What a run reported about each case, drawn under the case in the panel, in a browser.

⛔ **WHY A BROWSER.** The claim is about a page that has just finished a run: the detail lines arrive
on the run's own
stream, and what a reader sees is those lines joined to the cases Python rendered — a failure
message and a log under
the right case, printed text kept apart from the log, and nothing at all where the server sent no
detail.
⭐ The scripted run says exactly what `serve.routes.breakdown` says, built from its own functions.
"""

from __future__ import annotations

import json
import time

from studyforge.serve.routes.breakdown import DETAIL_LINE, DETAIL_VERSION, said
from tests.visual.test_practice_breakdown import (  # noqa: F401  (fixtures are used by name)
    CASES,
    SETTLE,
    SUBMIT,
    panel,
    tree,
)
from tests.visual.test_practice_panel import RUNNING

READ = """
(() => {
  const text = (node) => node ? node.textContent : null;
  return {
    status: document.querySelector('[data-practice-part="status"]').textContent.trim(),
    output: document.querySelector('[data-practice-part="output"]').textContent,
    rows: Array.from(document.querySelectorAll('[data-practice-case]')).map((row) => ({
      id: row.getAttribute('data-practice-case'),
      message: text(row.querySelector('[data-practice-part="case-message"]')),
      log: text(row.querySelector('[data-practice-part="case-log-lines"]')),
      out: text(row.querySelector('[data-practice-part="case-out-lines"]')),
      outTitle: text(row.querySelector('[data-practice-part="case-out"] summary'))
    })),
    run: text(document.querySelector('[data-practice-part="run-detail"]'))
  };
})()
"""


def line(**record) -> str:
    return DETAIL_LINE.format(json=json.dumps({"v": DETAIL_VERSION, **record}))


def submit(page, origin, lines):
    origin.runs.said = tuple(lines)
    page.evaluate(SUBMIT)
    origin.runs.started.wait(SETTLE)
    origin.runs.release.set()
    deadline = time.monotonic() + SETTLE
    drawn = dict(page.evaluate(READ))
    while drawn["status"] in ("", RUNNING) and time.monotonic() < deadline:
        time.sleep(0.05)
        drawn = dict(page.evaluate(READ))
    assert drawn["status"] not in ("", RUNNING), f"the run never finished; it reads {drawn}"
    return drawn


def verdicts(passed):
    return [said(case["id"], passed[case["id"]]) for case in CASES]


def test_each_case_shows_its_message_its_log_and_its_printed_text(panel):
    page, origin = panel
    state = {"test_greets": False, "test_empty": True, "test_accent": True}
    drawn = submit(
        page,
        origin,
        [
            *verdicts(state),
            line(
                case="test_greets",
                passed=False,
                message="expected 'Hi Ada' but was ''",
                log=["DEBUG greet: input name=Ada"],
                out=["printed"],
                err=[],
            ),
            line(case="test_empty", passed=True, message="", log=[], out=[], err=[]),
            line(case="test_accent", passed=True, message="", log=[], out=[], err=[]),
            line(run=True, log=[], out=[], err=[], truncated=False, perCaseOut=True),
        ],
    )
    first, second, third = drawn["rows"]
    assert first["message"] == "expected 'Hi Ada' but was ''"
    assert first["log"] == "DEBUG greet: input name=Ada"
    assert first["out"] == "printed" and first["outTitle"].startswith("Printed output")
    assert second["message"] is None and second["log"] is None and third["log"] is None
    assert "--- detail" not in drawn["output"]  # taken off the stream like a case line


def test_text_with_markup_is_text(panel):
    page, origin = panel
    state = {"test_greets": False, "test_empty": True, "test_accent": True}
    markup = line(
        case="test_greets", passed=False, message="<b>x</b>", log=["<i>y</i>"], out=[], err=[]
    )
    drawn = submit(page, origin, [*verdicts(state), markup])
    assert drawn["rows"][0]["message"] == "<b>x</b>" and drawn["rows"][0]["log"] == "<i>y</i>"


def test_text_the_tool_records_once_is_shown_once_and_says_so(panel):
    page, origin = panel
    state = {"test_greets": True, "test_empty": True, "test_accent": True}
    whole = line(run=True, log=[], out=["whole run text"], err=[], truncated=True, perCaseOut=False)
    drawn = submit(page, origin, [*verdicts(state), whole])
    assert "does not record printed text per case" in drawn["run"]
    assert "whole run text" in drawn["run"]
    assert "dropped" in drawn["run"]


def test_a_run_without_detail_draws_exactly_what_it_drew_before(panel):
    # ⭐ The compatibility clause: a server that sends no detail line leaves no trace of this part in
    # the panel.
    page, origin = panel
    state = {"test_greets": True, "test_empty": False, "test_accent": True}
    drawn = submit(page, origin, verdicts(state))
    for row in drawn["rows"]:
        assert row["message"] is None and row["log"] is None and row["out"] is None
    assert drawn["run"] is None
