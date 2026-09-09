"""Which colour a combined token lands on — read from the stylesheet's own order.

⭐ **Split deliberately from `test_highlight_grammars.py`.** That one runs the
real vendored bundle under node and *discovers* which class combinations the
grammars emit; this one needs no runtime at all and asserts what the stylesheet
does with a combination once you have it. ⛔ The split exists because the dev
image has no JS runtime: the highest-value assertion — no combination takes the
comment colour without being a comment — must run in the gate, against the
combinations already measured, rather than skipping there.

⚠️ The two halves are not redundant. This one cannot notice a new combination;
that one cannot run everywhere.
"""

from __future__ import annotations

import re

import pytest

from studyforge.render.pageassets import text

#: The stylesheet's groups, weakest first, each identified by the declaration
#: it ends with. ⚠️ These are MARKERS, not the order: the order is read out of
#: the file below, and this tuple is what the file is checked against.
GROUP_ORDER_MARKERS = (
    ("container", "color: inherit;"),
    ("punct", "var(--tok-punct)"),
    ("type", "var(--tok-type)"),
    ("function", "var(--tok-function)"),
    ("number", "var(--tok-number)"),
    ("string", "var(--tok-string)"),
    ("keyword", "var(--tok-keyword)"),
    ("comment", "var(--tok-comment)"),
    ("body", "var(--code-fg)"),
)

#: ⭐ EVERY ONE OF THESE WAS TAKEN FROM REAL GRAMMAR OUTPUT, not invented.
#: `test_highlight_grammars.py` runs the vendored bundle over its samples and
#: fails if it emits a combination this table does not record — which is what
#: stops the half that runs everywhere from falling behind the half that needs
#: a JS runtime. ⚠️ The annotations are the interesting rows: they carry
#: `punctuation` too, and would read as punctuation if `type` did not come
#: after it in the stylesheet.
MEASURED_COMBINATIONS = {
    "annotation builtin": "type",
    "annotation punctuation": "type",
    "builtin": "type",
    "class-name": "type",
    "comment": "comment",
    "decorator annotation punctuation": "type",
    "expression": "container",
    "function": "function",
    "function-variable function": "function",
    "interpolation": "body",
    "interpolation-punctuation punctuation": "punct",
    "keyword": "keyword",
    "number": "number",
    "operator": "punct",
    "parameter": "container",
    "punctuation": "punct",
    "regex": "string",
    "regex-delimiter": "punct",
    "regex-flags": "punct",
    "regex-source language-regex": "string",
    "string": "string",
    "string-literal multiline": "string",
    "string-literal singleline": "string",
    "template-punctuation string": "string",
    "template-string": "string",
    "triple-quoted-string string": "string",
}


def groups():
    """`[(group, {class, ...}), ...]` in stylesheet order, weakest first."""
    css = text("code-highlight.css")
    blocks = []
    for group, marker in GROUP_ORDER_MARKERS:
        start = css.index(marker)
        head = css.rfind("}", 0, start)
        selectors = css[head + 1 : start]
        blocks.append((group, set(re.findall(r"\.token\.([a-z-]+)", selectors)), start))
    blocks.sort(key=lambda block: block[2])
    return [(group, classes) for group, classes, _ in blocks]


def resolve(classes):
    """Which colour the browser lands on for an element carrying `classes`."""
    winner = None
    for group, members in groups():
        if members & set(classes):
            winner = group
    return winner


def test_the_group_order_is_the_one_the_stylesheet_documents():
    # ⛔ Every selector has the same specificity, so the LAST group to match
    # wins and the order IS the mapping. Reorder the groups and every combined
    # token changes colour, silently. This is the tripwire.
    assert [group for group, _ in groups()] == [group for group, _ in GROUP_ORDER_MARKERS]


def test_no_class_is_filed_under_two_groups():
    # A class in two groups resolves by whichever comes last, which makes the
    # earlier mention a lie a reader will believe.
    seen = {}
    for group, classes in groups():
        for klass in classes:
            assert klass not in seen, f"{klass} is in both {seen[klass]} and {group}"
            seen[klass] = group


@pytest.mark.parametrize("combination,expected", sorted(MEASURED_COMBINATIONS.items()))
def test_every_measured_combination_lands_where_it_should(combination, expected):
    # ⚠️ The annotations are the interesting ones: they carry `punctuation`
    # too, and would read as punctuation if `type` did not come after it.
    assert resolve(combination.split()) == expected


@pytest.mark.parametrize("combination", sorted(MEASURED_COMBINATIONS))
def test_no_measured_combination_takes_the_comment_colour_unless_it_is_one(combination):
    # ⛔ THE BUG THIS FILE EXISTS FOR. A string-literal variant filed under
    # comment italicised every string in one language, the tests still passed,
    # and only a screenshot caught it.
    if resolve(combination.split()) == "comment":
        assert "comment" in combination.split(), (
            f"`{combination}` takes the comment colour and italics but is not a comment"
        )


def test_an_interpolated_expression_reads_as_code_and_not_as_string():
    # ⭐ It wins on being the INNER element, not on order — which is why it
    # can sit last without repainting the string that contains it.
    assert resolve(["interpolation"]) == "body"
    assert resolve(["string"]) == "string"


def test_a_container_token_paints_nothing():
    # Prism nests other tokens inside these. If they painted, they would
    # override the child that carries the meaning.
    for klass in dict(groups())["container"]:
        assert resolve([klass]) == "container"


def test_the_highlighter_is_carried_by_the_page_s_own_script():
    # ⛔ Concatenated into the one script every page links, not a second
    # `<script>` — which is what keeps a page self-contained over `file://`.
    from studyforge.render.pageassets import SCRIPT_PARTS

    assert "prism.js" in SCRIPT_PARTS


def test_the_stylesheet_carries_the_token_rules():
    from studyforge.render.pageassets import stylesheet

    assert "figure.code .token.keyword" in stylesheet()
