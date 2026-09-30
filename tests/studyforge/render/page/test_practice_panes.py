"""Mirror of `src/studyforge/render/assets/practice-panes.js` and its stylesheet (R12).

⭐ **The description beside the editor is
resized by a divider and closed; the report under the editor is resized by a
divider and collapsed to a bar.** ⚠️ No JavaScript runs in this suite, so what a
TEXT can hold is held here — the markup every control ships as, and the rules
the script and the stylesheet keep — and the behaviour is the visual harness's
(`tests/visual/test_practice_panes.py`).
"""

from __future__ import annotations

import re

from studyforge.render import templates
from studyforge.render.pageassets import ASSET_DIR, script, stylesheet
from studyforge.render.pageassets.bundle import SCRIPT_PARTS, STYLE_PARTS
from tests.studyforge.render.page.test_practice import panel

SCRIPT = ASSET_DIR / "practice-panes.js"
STYLE = ASSET_DIR / "practice-panes.css"


def behaviour() -> str:
    """The script with its comments removed, so a claim is about the code."""
    return re.sub(r"/\*.*?\*/", "", SCRIPT.read_text(encoding="utf-8"), flags=re.DOTALL)


def rules() -> str:
    """The stylesheet with its comments removed."""
    return re.sub(r"/\*.*?\*/", "", STYLE.read_text(encoding="utf-8"), flags=re.DOTALL)


def workspace() -> str:
    return templates.template("practice-workspace.html").template


def tag(markup: str, marker: str) -> str:
    """The one opening tag in `markup` carrying `marker`."""
    found = re.findall(r"<[a-z]+\b[^>]*" + re.escape(marker) + r"[^>]*>", markup)
    assert len(found) == 1, (marker, found)
    return found[0]


def test_both_parts_are_in_the_bundle_after_the_workspace():
    assert SCRIPT.read_text(encoding="utf-8") in script()
    assert STYLE.read_text(encoding="utf-8") in stylesheet()
    scripts, styles = SCRIPT_PARTS.index, STYLE_PARTS.index
    assert scripts("practice-panes.js") == scripts("practice-workspace.js") + 1
    assert styles("practice-panes.css") == styles("practice-workspace.css") + 1


def test_the_description_divider_is_a_focusable_vertical_separator_shipped_hidden():
    divider = tag(workspace(), 'data-workspace-part="divider"')
    for attribute in (
        'role="separator"',
        'aria-orientation="vertical"',
        'tabindex="0"',
        "aria-label=",
        " hidden",
    ):
        assert attribute in divider, attribute
    # ⭐ The value and what it controls are the script's: the width is the
    # reader's, and the description is whichever practice is open.
    body = behaviour()
    for said in ("'aria-valuemin'", "'aria-valuemax'", "'aria-valuenow'", "'aria-controls'"):
        assert said in body, said


def test_the_description_closes_by_a_labelled_button_and_opens_from_an_edge():
    toggle = tag(workspace(), 'data-workspace-act="statement"')
    edge = tag(workspace(), 'data-workspace-act="reopen"')
    assert toggle.startswith('<button type="button"') and edge.startswith('<button type="button"')
    assert 'aria-expanded="true"' in toggle and 'aria-expanded="false"' in edge
    assert " hidden" in toggle and " hidden" in edge
    shell = workspace()
    assert ">Hide description<" in shell and ">Show description<" in shell
    # ⭐ The toggle stands before the title, where the pane it closes is.
    at = shell.index
    assert at('data-workspace-act="statement"') < at('data-workspace-part="title"')


def test_the_report_divider_is_a_horizontal_separator_and_the_bar_collapses_the_report():
    markup = panel()
    divider = tag(markup, 'data-practice-part="report-divider"')
    for attribute in (
        'role="separator"',
        'aria-orientation="horizontal"',
        'tabindex="0"',
        " hidden",
    ):
        assert attribute in divider, attribute
    report = tag(markup, 'data-practice-part="report"')
    body = tag(markup, 'data-practice-part="report-body"')
    bar = tag(markup, 'data-practice-part="report-bar"')
    report_id = re.search(r'id="([^"]+)"', report).group(1)
    body_id = re.search(r'id="([^"]+)"', body).group(1)
    assert f'aria-controls="{report_id}"' in divider
    assert f'aria-controls="{body_id}"' in bar and 'aria-expanded="true"' in bar
    assert bar.startswith('<button type="button"') and " hidden" in bar
    # ⭐ The verdict at a glance, worded in the markup (R13).
    assert 'data-practice-glance="{passed}/{total} passed"' in bar
    # ⛔ The status, the breakdown and the output are all inside the report
    # body, in their old order, and the divider and bar come before them.
    at = markup.index
    assert at('data-practice-part="controls"') < at('data-practice-part="report-divider"')
    assert at('data-practice-part="report-bar"') < at('data-practice-part="report-body"')
    assert at('data-practice-part="report-body"') < at('data-practice-part="status"')
    assert at('data-practice-part="status"') < at('data-practice-part="output"')


def test_nothing_is_moved_copied_or_created_and_no_frame_is_touched():
    body = behaviour()
    for word in (
        "appendChild",
        "insertBefore",
        "replaceChild",
        "removeChild",
        ".append(",
        ".prepend(",
        "replaceWith",
        "cloneNode",
        "innerHTML",
        "outerHTML",
        "insertAdjacent",
        "createElement",
        "iframe",
        "fetch(",
        "/api",
    ):
        assert word not in body, word


def test_a_drag_captures_the_pointer_and_no_frame_takes_it_meanwhile():
    body = behaviour()
    assert "handle.setPointerCapture(event.pointerId);" in body
    assert "root.setAttribute(DRAGGING, axis);" in body
    assert "root.removeAttribute(DRAGGING);" in body
    for name in ("'pointerup'", "'pointercancel'", "'lostpointercapture'"):
        assert name in body, name
    style = rules()
    assert "html[data-workspace-dragging] iframe { pointer-events: none; }" in style
    # ⭐ A touch on a divider drags it rather than scrolling the page.
    assert style.count("touch-action: none;") == 2


def test_the_keys_each_divider_takes():
    body = behaviour()
    limits = "Home: bounds.low, End: bounds.high"
    assert "ArrowLeft: now - STEP, ArrowRight: now + STEP, " + limits in body
    assert "ArrowUp: now + STEP, ArrowDown: now - STEP, " + limits in body
    assert body.count("if (event.key === 'Enter') {") == 2


def test_every_choice_is_kept_through_the_store_and_a_failure_costs_nothing():
    # ⛔ `study-progress.js` is the one file that touches the store; this one
    # asks it, and a store that throws or is absent leaves the page working.
    body = behaviour()
    assert "localStorage" not in body and "sessionStorage" not in body
    assert (
        "try { return store ? store.preference(name) : null; } catch (ignored) { return null; }"
        in body
    )
    assert (
        "try { if (store) { store.prefer(name, String(value)); } } catch (ignored) { return; }"
        in body
    )
    for name in (
        "'workspace-left'",
        "'workspace-statement'",
        "'workspace-report'",
        "'workspace-report-shown'",
    ):
        assert name in body, name


def test_the_description_side_is_a_desktops_and_a_quizs_is_none():
    body = behaviour()
    assert "var NARROW = '(max-width: 40rem)';" in body
    assert "!root.hasAttribute(QUIZ) && !window.matchMedia(NARROW).matches" in body
    style = rules()
    # ⭐ The closed geometry holds only where the workspace does not stack.
    closed = style.index('html[data-workspace-statement="closed"]')
    assert style.rindex("@media not all and (max-width: 40rem) {", 0, closed) >= 0
    assert ":not([data-workspace-quiz])" in style[closed : closed + 200]


def test_the_focus_ring_is_the_themes_own_and_drawn_inside_the_divider():
    style = rules()
    assert "outline: 2px solid var(--focus);" in style and "outline-offset: -2px;" in style
    # ⛔ No colour of its own: every value is a palette token.
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(", style)


def test_a_new_run_opens_the_report_again():
    body = behaviour()
    assert "if (!reportShown) { flipReport(true, false); }" in body
    assert "act.getAttribute('data-practice-act') === 'stop'" in body
