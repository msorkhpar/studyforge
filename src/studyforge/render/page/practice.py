r"""The practice panel: the reader-facing surface of one graded or ungraded exercise.

**What it does.** Renders the controls that sit under a practice section's
statement — where the reader's file is, the editor slot and its two tabs, the
control that maximises the panel, Run and Submit, the streamed result, and the
label saying what a pass here is worth.

**How you use it.** `practice.render(section, document, placement)` returns the
panel's markup, or `''` for a section that sets no work; `page.document` joins
it after the section it belongs to.

**Depends on.** `studyforge.exercise` for what a workspace *is* — ⛔ the record's
own predicates, never a second reading of `provenance` and `trust`;
`studyforge.progress` and `studyforge.address` for the key a run is named by;
`page.mark` for the unit half of that key; `render.templates` and
`render.markup`. ⛔ **Not on `serve`**: a page that needed a server to render is
a page that fails the `file://` floor (R8), and this panel renders there — it
simply renders as the honest statement that Run and Submit are not available.

## ⛔ The statement is the SECTION; this is only the controls

⚠️ A practice's prose, its hint and its starting code are ordinary blocks and
are rendered by `page.section` like any other material (R1: every word a reader
sees that is not this framework's own structure comes out of the document). ⭐ So
this module never touches `blocks`, and a corpus that words its problem
statement differently needs no change here.

## ⛔ Three honesty requirements, and none of them is polish

1. ⛔ **The editor container is deliberately not auto-started.** It is an IDE
   with a shell, and starting one because somebody opened a reading page is not
   a decision a page gets to make. So the editor slot ships with the sentence
   that says the editor is not running and how to start it — ⭐ **a panel that
   says so is not a panel that renders blank and looks broken**, and blank is
   what an `<iframe>` pointed at a container that is down gives you.
2. ⛔ **An advisory grader is labelled** (R5). A reader must be able to tell
   *"the tests that ship with this material passed"* from *"something generated
   locally passed"*, and the two sentences are two template files.
3. ⛔ **A QUIZ renders no panel at all** (`AX-05`, `W429`). It carries questions
   in place of a workspace: no file, no editor window, no Run and no Submit.
   ⚠️ The two shapes share this one surface, and one of them renders with **no
   frame at all** — as an absence, never as controls a reader may not use.
4. ⛔ **A reading-only unit shows NO practice control — not a disabled one.**
   A dead button is a promise the page cannot keep. A section with no
   `workspace` gets no panel at all, and Submit is emitted only where the
   record names a test command (`W357`).

## ⛔ The maximise is GEOMETRY, and the panel emits only its control (`W431`)

⛔ **The reader asked for a way to give the practice the whole viewport** — the
code, the tests, Run and Submit — and the panel already carries every one of
them. ⭐ So this module emits one more real `<button>` and nothing else: which
part of the page is large is `practice.css`'s, and the attribute that says so is
`practice.js`'s.

⚠️ **Both of the control's words are HERE**, in the template — the one it ships
showing and the one it carries for the other state — because the Python side is
the single source for what is emitted, and a label spelled in the script too
would be a second place for it to drift.

⛔ **It ships `hidden`, like the controls beside it.** Over `file://` the panel
is one sentence, and a control that makes a sentence full-screen is the dead
button this module refuses everywhere else. ⚠️ **A quiz renders no panel**, so
it cannot carry this control either — asserted, not assumed.

## ⛔ R5's keys never reach the page

⚠️ `provenance` and `trust` are the framework's vocabulary for how much a
verdict is worth; neither is a word a reader was ever told the meaning of. ⭐ So
this module asks the record's own predicates — `Exercise.graded` and
`Exercise.authoritative` — and chooses between two sentences. **No `data-*`
attribute carries either key**, which is what stops the words leaking back onto
the page through a stylesheet hook.

## ⛔ The practice key is ASKED FOR, never composed

⭐ `progress.practice_key` is the one composer and `page.mark.key` is the one
spelling of the unit half — the same string the read mark is filed under and the
run route parses back. This module joins them through
`address.parse_unit_key`, the address package's own inverse, so there is no
string arithmetic here and no second format anywhere on the page. ⚠️ A key
spelled twice and differing by one character simply never matches anything, with
nothing failing anywhere; that is the defect `progress.keys` records paying for.

## ⛔ The page names no API, no origin and no client file (R8, `W370`)

⭐ The panel reads `window.studyforge.run` and nothing else. The execution
client is added to a served page by the **serving process**
(`serve.routes.assets`), because only a server knows it is a server — and a
built text that named the client would be a defect R8's floor reads
(`tests/studyforge/cli/serving.py`). ⚠️ Over `file://` the object is absent, the
controls stay hidden, and the panel says why.

## ⭐ Where `AX-09` joins, so it is a seam rather than a rewrite (`E14`, M10)

⚠️ Three additions land on this same surface at M10 and none of them reopens
what is here: the Submit **breakdown** (*main ask ✓*, *edge cases n/m*, each
failed case named) is a new part inside the panel's output region; the
**reference solution**, always available, is a new region beside the editor
slot; and the **learner-worded label** is a rewording of the two grader
templates and of nothing else. ⛔ A **quiz** renders in this panel with no
editor, no Run and no Submit — which this module already expresses as *a section
with no workspace gets no panel* rather than as disabled controls.
"""

from __future__ import annotations

from studyforge.address import AddressError, parse_unit_key
from studyforge.archive.scrub import PersonalDataLeak
from studyforge.exercise import RUN, TEST, Exercise, ExerciseError, from_document
from studyforge.progress import RAISES as PROGRESS_RAISES
from studyforge.progress import practice_key
from studyforge.render import templates
from studyforge.render.markup import escape, escape_attribute
from studyforge.render.page import mark
from studyforge.render.page.assets import Placement
from studyforge.render.page.errors import PageError

#: The section kind that can carry a workspace. ⛔ The archive's word, and the
#: same one `serve.routes.run.PRACTICE` selects on.
PRACTICE = "practice"

#: The panel itself: the editor slot, the controls, the status line and the
#: output region — a whole element with attributes, so a file (R13).
PANEL_TEMPLATE = "practice-panel.html"

#: The two windows, and the tab that reaches each. ⭐ The Tests tab is emitted
#: only where the record NAMES a test — the same honesty Submit already gets
#: (`W357`): a tab over a file the material does not have is a dead control.
#: ⛔ The tablist ships hidden; it is shown only where a running editor answered.
TABS_TEMPLATE = "practice-tabs.html"
TESTS_TAB_TEMPLATE = "practice-tab-tests.html"

#: The two acts, one template each. ⭐ The LABEL is markup and the MODE is
#: `exercise`'s own word, substituted in — so the vocabulary the client posts
#: under is spelled once, in the package that owns it.
ACT_TEMPLATES = {RUN: "practice-run.html", TEST: "practice-submit.html"}

#: `is this the source's own grader? -> the sentence a reader is shown`. ⛔ Keyed
#: on the record's predicate and never on the `trust` word, so neither R5 key can
#: reach the page through this mapping.
GRADER_TEMPLATES = {True: "practice-grader-shipped.html", False: "practice-grader-generated.html"}

#: What closes an optional region inside the panel. ⚠️ The same shape
#: `page.document._region` uses, and for the same reason: a region is exactly
#: empty or exactly its markup plus one newline, never a conditional newline
#: somewhere else (R10).
JOIN = "\n"


def render(section: dict, document: dict, placement: Placement) -> str:
    """Return one practice section's panel, or `''` where the unit sets no work.

    ⛔ Empty is the ordinary answer and it is the whole product decision: §7's
    three states are structural, and a unit with no exercise is COMPLETE at the
    reading floor rather than short (C5). ⭐ So a lesson, a practice with no
    workspace and a corpus that ships no graders at all each render with no
    practice affordance whatever — not a disabled one.
    """
    if not isinstance(section, dict) or section.get("kind") != PRACTICE:
        return ""
    workspace = section.get("workspace")
    if not isinstance(workspace, dict):
        return ""
    exercise = _exercise(workspace)
    if exercise.is_quiz:
        # ⛔ **A quiz is not work at a file** (`AX-05`): it carries questions in
        # place of a workspace, so there is no file to name, nothing to open in
        # an editor, no command to Run and no grader to Submit to. ⭐ The two
        # shapes share this one surface and this one renders with no frame at
        # all — and with no dead control either, which is the same rule a
        # reading-only unit gets two lines above. ⚠️ A quiz's OWN surface, the
        # questions and how they are answered, is `AX-06`'s and `AX-09`'s.
        return ""
    return templates.fill(
        PANEL_TEMPLATE,
        key=escape_attribute(key_of(document, section)),
        corpus=escape_attribute(placement.corpus),
        main=escape(exercise.main_path),
        grader=_region(grader(exercise)),
        tabs=_region(tabs(exercise)),
        controls=controls(exercise),
    )


def key_of(document: dict, section: dict) -> str:
    """Return the key this practice's runs and passes are recorded under.

    ⛔ **Composed by `progress.practice_key` and by nothing here.** The unit half
    is `page.mark.key`, which is also the string the read mark is filed under, and
    it is taken apart again by the address package's own inverse at the depth the
    document's own address states — so no separator is typed in this module.
    """
    unit = mark.key(document)
    depth = len(document.get("address") or ())
    try:
        address, ordinal = parse_unit_key(unit, depth)
        return practice_key(address, ordinal, section.get("key"))
    except (AddressError, *PROGRESS_RAISES) as error:
        # ⛔ **`progress.RAISES` is named WHOLE** (`tests/test_raises_convention.py`):
        # a handler that listed one member would stop naming the tuple the day
        # that package widens it, and the symptom is an exception nobody catches.
        # ⛔ **And `PersonalDataLeak` still travels through as itself** (Ruling 58):
        # a caller rendering a site catches `PageError` per unit and carries on,
        # and an R7 refusal folded into that family would be logged as one more
        # page that did not render, with the leak the thing nobody looked at.
        if isinstance(error, PersonalDataLeak):
            raise
        # ⛔ Re-typed, not re-worded: `address` and `progress` own what a key is,
        # and a caller rendering a site catches one family per page. ⚠️ The
        # message carries their sentence, which describes rather than echoes
        # what arrived (R7) — this runs over every unit in a corpus and into a
        # build log.
        raise PageError(
            f"this practice cannot say what its runs would be recorded under: {error}"
        ) from None


def controls(exercise: Exercise) -> str:
    """Return the acts this workspace can actually perform, in a stated order.

    ⛔ **Run is always offered and Submit only where a test command is named**
    (`W357`, and `serve.routes.run` answers `409` for the other case): a record
    carries `main_path` and `run_command` or it is not a record, while the
    grader half is written whole or not at all. ⚠️ Offering a Submit that can
    only fail is the dead button this row exists to refuse.
    """
    acts = [RUN] if exercise.test_command is None else [RUN, TEST]
    return "".join(templates.fill(ACT_TEMPLATES[act], mode=act) for act in acts)


def tabs(exercise: Exercise) -> str:
    """Return the tablist over this practice's two editor windows.

    ⭐ **Two windows of ONE editor, never a split pane** (`W429`): the file a
    reader may type in and the file that judges it are two different acts of
    reading, and standing them side by side halves the width of both.

    ⛔ **The second tab is emitted only where a test is named.** ⚠️ This module
    names neither file and builds no URL: which file a window shows is decided
    by that window's own URL, which only a served origin can say (R8) — the
    tabs are the surface, and `practice.js` asks for the two addresses.
    """
    tests = templates.fill(TESTS_TAB_TEMPLATE) if exercise.test_path is not None else ""
    return templates.fill(TABS_TEMPLATE, tests=tests)


def grader(exercise: Exercise) -> str:
    """Return the sentence saying what a pass here is worth, or `''` for no grader.

    ⭐ **Two sentences, two files, one predicate** (R5, R13). ⚠️ An ungraded
    exercise carries no line at all rather than a third sentence: the page
    already offers no Submit, which says the same thing without a claim about a
    grader that does not exist.
    """
    if not exercise.graded:
        return ""
    return templates.fill(GRADER_TEMPLATES[exercise.authoritative])


def _exercise(workspace: dict) -> Exercise:
    """Read the section's workspace as the record it is, or refuse saying so.

    ⚠️ Read through `exercise.from_document`, which owns R5's rule by way of
    `unit.trust`. ⛔ No provenance or trust logic is spelled here; a second
    spelling of that rule is the defect `exercise.record` refuses.
    """
    try:
        return from_document(workspace, "this unit's practice workspace")
    except ExerciseError as error:
        raise PageError(f"this practice's workspace cannot be rendered: {error}") from None


def _region(markup: str) -> str:
    """Return one optional region: exactly empty, or its markup and one newline."""
    return f"{markup}{JOIN}" if markup else ""
