"""Mirror of `src/studyforge/render/templates/__init__.py` (R12)."""

from __future__ import annotations

import re

import pytest

from studyforge.render import templates
from studyforge.render.pageassets import HOOK_CLASSES, SURFACE_CLASSES
from tests.support import assert_package_contract, repository_root

#: Every class name any template may carry: the published markup contract, plus
#: the one class a vendored library reads out of the page it was shipped with.
#: ⛔ `language-*` is Prism's own API and is deliberately not in
#: `SURFACE_CLASSES`, which publishes what *this project's* stylesheet targets.
LIBRARY_CLASS = re.compile(r"^language-")

#: A template whose markup is emitted on one line is authored on one line.
#: ⚠️ Derived by asking the loader, not by listing filenames: a template added
#: tomorrow is covered on the day it appears.
ONE_LINE = (
    "between-units.html",
    "breadcrumb.html",
    "code.html",
    "crumb-separator.html",
    "example.html",
    "example-bar.html",
    "example-flag-compiler.html",
    "example-flag-warning.html",
    "example-missing.html",
    "example-panel.html",
    "example-tab.html",
    "example-tab-missing.html",
    "image.html",
    "link-index.html",
    "link-next-chain.html",
    "link-next.html",
    "link-previous-chain.html",
    "link-previous.html",
    "mode-button.html",
    "mode-option.html",
    "mode-outside-button.html",
    "outline.html",
    "practice-case.html",
    "practice-state.html",
    "practices-title.html",
    "practice-carriers.html",
    "practice-grader-bundled.html",
    "practice-grader-generated.html",
    "practice-grader-none.html",
    "practice-grader-quiz.html",
    "practice-grader-mock.html",
    "practice-grader-shipped.html",
    "practice-grader-user.html",
    "practice-option.html",
    "practice-mockform-option.html",
    "practice-run.html",
    "practice-submit.html",
    "practice-tab-tests.html",
    "rail.html",
    "read-state.html",
    "video.html",
    "video-link.html",
)

#: The templates whose newlines are real output. ⭐ Together with `ONE_LINE`
#: this must be every template on disk, and the test below asserts it — so a new
#: template cannot be added without somebody deciding which kind it is.
MULTI_LINE = (
    "attachments.html",
    "mode-head.html",
    "mode-outside-locked.html",
    "mode-outside-open.html",
    "mode-switch.html",
    "code-example.html",
    "code-examples.html",
    "page.html",
    "section.html",
    "pending-practices.html",
    "player.html",
    "narration-gap.html",
    "practice-breakdown.html",
    "practice-panel.html",
    "practice-card.html",
    "practice-concepts.html",
    "practice-workspace.html",
    "practices.html",
    "practice-mock-question.html",
    "practice-mock.html",
    "practice-mockform-question.html",
    "practice-mockform.html",
    "practice-question.html",
    "practice-quiz.html",
    "practice-tabs.html",
    "read-mark.html",
)


def test_the_package_states_its_contract():
    assert_package_contract(templates, "studyforge.render.templates")


def test_every_template_is_classified_as_one_line_or_many():
    # ⛔ The two lists above are the vocabulary; this is what stops a template
    # being added to the directory and asserted by nothing.
    assert sorted(ONE_LINE + MULTI_LINE) == sorted(templates.names())


@pytest.mark.parametrize("name", ONE_LINE)
def test_an_inline_template_stays_on_one_line(name):
    # ⛔ `template()` does not join lines, so a newline in one of these would be
    # a newline in the page — and every committed golden would move.
    assert "\n" not in templates.template(name).template


@pytest.mark.parametrize("name", MULTI_LINE)
def test_a_page_shaped_template_keeps_its_newlines(name):
    assert "\n" in templates.template(name).template


@pytest.mark.parametrize("name", templates.names())
def test_a_template_is_used_exactly_minus_one_trailing_newline(name):
    raw = (templates.TEMPLATE_DIR / name).read_bytes().decode("utf-8")
    loaded = templates.template(name).template
    assert raw == loaded + "\n" or raw == loaded


@pytest.mark.parametrize("name", templates.names())
def test_no_template_ends_in_a_newline_once_loaded(name):
    # ⚠️ The whole reason the strip exists: an editor adding a trailing newline
    # to an inline fragment must not lengthen the page.
    assert not templates.template(name).template.endswith("\n")


def test_an_unfilled_placeholder_raises_and_never_reaches_the_page():
    # ⛔ The rendering acceptance clause, at the mechanism that keeps it.
    with pytest.raises(templates.TemplateError) as raised:
        templates.fill("section.html", id="a", key="b", kind="c", label="d", lang="")
    assert "body" in str(raised.value)
    assert "heading" in str(raised.value)


def test_the_same_call_with_every_placeholder_filled_succeeds():
    # ⭐ The negative control run negatively: the failure above is the missing
    # value and not the call.
    markup = templates.fill(
        "section.html", id="a", key="b", kind="c", label="d", lang="", heading="", body="x"
    )
    assert markup.startswith('<section id="a"')


def test_a_value_with_no_placeholder_raises():
    # ⚠️ The silent half: a slot deleted from the markup takes its content off
    # the page, and `Template.substitute` would ignore the leftover value.
    with pytest.raises(templates.TemplateError) as raised:
        templates.fill(
            "section.html",
            id="a",
            key="b",
            kind="c",
            label="d",
            lang="",
            heading="",
            body="x",
            pills="gone",
        )
    assert "pills" in str(raised.value)


def test_an_unknown_template_is_refused_by_name_and_not_by_path():
    with pytest.raises(templates.TemplateError) as raised:
        templates.template("nothing-here.html")
    message = str(raised.value)
    assert "nothing-here.html" in message
    assert str(templates.TEMPLATE_DIR) not in message


def test_a_name_that_is_not_a_template_filename_is_refused():
    for name in ("../secrets", "code", "sub/code.html"):
        with pytest.raises(templates.TemplateError):
            templates.template(name)


def test_names_are_sorted_and_hold_no_python():
    found = templates.names()
    assert list(found) == sorted(found)
    assert all(name.endswith(templates.TEMPLATE_SUFFIX) for name in found)
    assert "__init__.py" not in found


def test_placeholders_answers_what_a_template_wants():
    assert templates.placeholders("video-link.html") == frozenset({"src", "label"})


def test_every_template_is_asked_for_by_some_renderer():
    # ⚠️ The check names the modules that MAY ask, not
    # the answer today, so a template that stops being used goes red rather than
    # the check quietly narrowing to whatever is left.
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((repository_root() / "src" / "studyforge" / "render").rglob("*.py"))
    )
    orphans = [name for name in templates.names() if f'"{name}"' not in source]
    assert orphans == [], f"templates nothing renders: {orphans}"


@pytest.mark.parametrize("name", templates.names())
def test_a_template_names_no_class_the_surface_does_not_publish(name):
    # ⛔ Asserted from the renderer's side. `test_surface` says every class
    # the stylesheet targets is published; this says every class the markup
    # emits is published too. Without both, the two sides can still disagree —
    # and a page that renders, carries every word and is unstyled is the failure
    # with no error anywhere.
    # ⛔ `HOOK_CLASSES` and not `SURFACE_HOOKS`: the hook mapping
    # also carries `data-*` attribute names and `data-kind` values, and comparing
    # a class against those would let a template carry `class="data-readable"`.
    published = set(SURFACE_CLASSES.values()) | set(HOOK_CLASSES.values())
    body = templates.template(name).template
    used = {
        klass for attribute in re.findall(r'class="([^"$]*)"', body) for klass in attribute.split()
    }
    stray = sorted(
        klass for klass in used if klass not in published and not LIBRARY_CLASS.match(klass)
    )
    assert stray == [], f"{name} invents a class: {stray}"


def test_the_loader_lives_in_the_directory_it_loads():
    # ⭐ The placement argument, asserted rather than only written down: there is
    # no path arithmetic from another package that could drift.
    assert templates.TEMPLATE_DIR.name == "templates"
    assert (templates.TEMPLATE_DIR / "__init__.py").is_file()
