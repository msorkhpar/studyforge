"""Mirror of `render/page/practice.py`'s BREAKDOWN, and of the reference beside it.

⛔ **Its own module, because `test_practice.py` had no room** — it stood at `599`
of R11's `600` the day this row opened, and a trim of four other rows' prose is
not a seam (`W422`'s second clause). ⭐ The seam is the SUBJECT: that file is
*the panel, its controls and its label*, and this is *what a Submit reported and
what the reader may always read instead*.

⚠️ **Every clause is asserted BOTH WAYS**, for `test_practice.py`'s own reason:
a breakdown that is absent where it should be and one that is present where it
should not be both render, carry every word and pass `validate`.
"""

from __future__ import annotations

from studyforge.exercise.bundle.emit import REFERENCE_SUMMARY
from studyforge.render.page import render
from tests.studyforge.render.page.pages import sample_placement
from tests.studyforge.render.page.test_practice import (
    GENERATED,
    behaviour,
    document,
    panel,
    section,
)

# --- ⛔ `AX-09`: the Submit breakdown, and the reference that is always there -


#: A record that declares what it is checked IN (`AX-00`): a main ask and two
#: edges, each with the sentence a reader is shown.
BROKEN_DOWN = {
    **GENERATED,
    "cases": [
        {"id": "test_greets", "kind": "main", "says": "It greets the person named."},
        {"id": "test_empty", "kind": "edge", "says": "It handles an empty name."},
        {"id": "test_accent", "kind": "edge", "says": "It handles an accented name."},
    ],
    "report": {"format": "junit", "path": "reports"},
    "origin": {"path": "basics/01.md", "section": "What a class is"},
}


def broken_down() -> str:
    """The panel for a practice that declares a breakdown."""
    return panel(sections=[section(workspace=BROKEN_DOWN)])


def test_the_breakdown_region_is_emitted_only_where_the_record_declares_one():
    # ⛔ `Exercise.breaks_down` is the predicate and both keys are one claim. ⭐ A
    # region with nothing to report is the dead control this panel refuses
    # everywhere else — asserted both ways over two real records.
    assert 'data-practice-part="breakdown"' in broken_down()
    assert 'data-practice-part="breakdown"' not in panel()


def test_every_declared_case_is_emitted_with_its_kind_and_the_corpus_s_sentence():
    # ⛔ **The counts are DERIVED and were never recorded** (`AX-02`): what a run
    # reports is `{case id: did it pass}`, so *main ask* and *edge cases n/m* are
    # that map joined with these. ⭐ In the order the corpus wrote them, because
    # re-ordering would be this framework editing the material (R1).
    said = broken_down()
    for case in BROKEN_DOWN["cases"]:
        assert f'data-practice-case="{case["id"]}"' in said
        assert f'data-practice-case-kind="{case["kind"]}"' in said
        assert case["says"] in said
    at = [said.index(case["says"]) for case in BROKEN_DOWN["cases"]]
    assert at == sorted(at)


def test_the_breakdown_ships_hidden_and_is_announced_rather_than_only_coloured():
    # ⛔ Nothing is reported before a Submit reports it. ⭐ And the region is a
    # live one, so a reader who cannot see the ink is told what changed — which
    # is this row's Acceptance, not a preference.
    region = broken_down().split('data-practice-part="breakdown"')[1].split(">")[0]
    assert "hidden" in region
    assert 'role="status"' in region and 'aria-live="polite"' in region


def test_every_word_the_breakdown_says_lives_in_the_markup_and_not_in_the_script():
    # ⭐ The two-sided spelling every hook on this page has (`W431`): a sentence
    # spelled in the script too would be a second place for it to drift. ⚠️ The
    # counting sentence is a PATTERN in the markup, and the script substitutes.
    said = broken_down()
    body = behaviour()
    for word in ("Main ask", "Edge cases", "Done", "Not yet"):
        assert word in said, word
        assert word not in body, word
    assert "{passed}" in said and "{total}" in said


def test_the_script_draws_nothing_when_the_two_case_populations_disagree():
    # ⛔ `AX-02`, *For dependents*: a corpus regenerated after a Submit can change
    # the case map under a reader, and a breakdown whose population does not
    # match the practice is not *edge cases 1/2* — it is a breakdown of a
    # different practice. ⭐ Both directions are read, because either alone lets
    # a partial count through.
    body = behaviour()
    assert "known === rows.length" in body
    assert "known === Object.keys(said).length" in body
    assert "!!rows.length &&" in body
    assert body.index("if (!whole(said)) { clear(); return; }") < body.index("var edges = 0;")


def test_the_breakdown_is_read_off_this_run_s_stream_and_is_never_fetched():
    # ⛔ A built page may name no API, no origin and no client file (R8, `W370`),
    # so the state namespace is out of reach and the run's own body is the one
    # channel left. ⚠️ Read for BOTH: the line's shape, and the absence of any
    # second way of asking.
    body = behaviour()
    assert "--- case " in body
    for word in ("fetch(", "XMLHttpRequest", "/api", "state/"):
        assert word not in body, word


def test_a_case_line_is_taken_off_the_stream_and_every_other_line_is_shown():
    # ⚠️ A case line is the SERVER talking about this run rather than the
    # program's own output — but the breakdown's own REFUSAL is prose for the
    # reader, and it must still arrive. ⛔ So exactly one shape is consumed.
    body = behaviour()
    assert (
        "if (found) { said[found[1]] = found[2] === PASSED; } else { append(output, line); }"
        in body
    )
    assert body.count("CASE_LINE.exec(line)") == 1


def test_the_breakdown_never_decides_what_passed():
    # ⛔ **The clause this row is measured by.** `progress.is_pass` is the
    # verdict and the breakdown is a report; a panel that called a practice
    # complete because every case passed would be the second definition of a
    # pass `AX-02` exists to avoid. ⭐ So the status line is set from the run's
    # own answer and never from the case map.
    body = behaviour()
    assert "status.textContent = text;" in body
    for word in ("first_passed_at", "complete", "is_pass"):
        assert word not in body, word


def test_the_reference_solution_is_present_closed_and_gated_on_nothing():
    # ⛔ The user's ruling (spec §7 §8): always available, never revealed
    # automatically, and asking is never recorded as a failure. ⭐ It arrives as
    # the archive's own `disclosure` block — a real `<details>` that opens with
    # scripting off entirely — so there is nothing in the panel that could
    # withhold it, which is the property asserted here.
    withheld = {
        "type": "disclosure",
        "summary": REFERENCE_SUMMARY,
        "open": False,
        "blocks": [{"type": "code", "lang": "java", "text": "class Greeter {}"}],
    }
    unit = document(sections=[dict(section(workspace=BROKEN_DOWN), blocks=[withheld])])
    page = render(unit, sample_placement()).decode("utf-8")
    assert "<details" in page and "<details open" not in page
    assert f"<summary>{REFERENCE_SUMMARY}</summary>" in page or REFERENCE_SUMMARY in page
    assert "class Greeter {}" in page
    # ⛔ And nothing about it is conditional on a pass: the same page carries a
    # panel that has never been run and the reference is already in it.
    assert 'data-practice-part="breakdown"' in page
