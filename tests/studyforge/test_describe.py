"""Mirror of `src/studyforge/describe.py` (R12) — the one describer."""

from __future__ import annotations

import pytest

from studyforge.describe import SAFE_TO_QUOTE, describe, describe_keys

#: ⛔ Synthetic, and it has to be. A fixture carrying this machine's real home
#: path is the exact violation these tests exist to prevent (R7).
POISON = "/" + "home/example/project/notes"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "nothing"),
        (3, "3"),
        (0, "0"),
        (True, "a bool"),
        (False, "a bool"),
        ("anything at all", "a str"),
        ("", "an empty string"),
        ("   ", "an empty string"),
        (3.5, "a float"),
        (["a"], "a list"),
        (("a",), "a tuple"),
        ({"a": 1}, "a dict"),
        (object(), "an object"),
        (set(), "a set"),
    ],
)
def test_describe_names_the_type_and_quotes_only_numbers(value, expected):
    assert describe(value) == expected


def test_the_article_agrees_with_the_type_name():
    # ⚠️ Cosmetic, and it is here because the extraction had to preserve it:
    # the copy this module replaced computed the article with a `replace("  ",
    # " ")` on a doubled space, which is the kind of line a rewrite silently
    # changes.
    assert describe(object()) == "an object"
    assert describe(3.5) == "a float"


@pytest.mark.parametrize(
    "carrier",
    [
        POISON,
        [POISON],
        {"origin": POISON},
        (POISON, POISON),
        {POISON},
    ],
)
def test_nothing_that_carries_a_path_is_reproduced(carrier):
    # ⛔ R7, at the source. Every shape a decoded JSON document can
    # take, carrying a path in the position a refusal would have quoted.
    assert POISON not in describe(carrier)
    assert "example" not in describe(carrier)


def test_a_string_is_never_safe_to_quote():
    # ⛔ The one widening that would undo the module. `str` in this tuple is
    # the whole defect the one describer exists to remove (R7), so it is
    # asserted rather than left to review.
    assert str not in SAFE_TO_QUOTE
    assert SAFE_TO_QUOTE == (int,)


def test_a_bool_is_named_rather_than_quoted():
    # ⛔ Safety is not the question — a bool carries no identifier
    # either way. `True` is not what the integrator typed: they wrote JSON
    # `true` where `1` was wanted, and "a bool" names that mistake while
    # `True` obscures it. ⚠️ `version._said` had this argument written down and
    # pinned by a test while the extraction quoted the opposite; the copy that
    # had made the case won.
    assert describe(True) == "a bool"
    assert describe(False) == "a bool"


def test_an_empty_string_is_named_rather_than_called_a_str():
    # ⭐ The behaviour `corpus.container.fields.said` had and the extraction
    # lost. Absent and present-but-blank are different mistakes; the second is
    # somebody who meant to write something.
    assert describe("") == "an empty string"
    assert describe("   ") == "an empty string"
    assert describe("real") == "a str"


def test_the_check_is_not_vacuous():
    # ⭐ Watch the assertion fail without the mechanism. A describer
    # that returned `repr(value)` would pass every "names the type" test above
    # for `None` and for integers, and fail only here.
    assert repr(POISON) != describe(POISON)


def test_the_unit_package_re_exports_rather_than_re_implements():
    # ⛔ One describer, asserted rather than trusted: `unit.errors` carries the
    # same object, which is a claim a later edit cannot quietly break.
    from studyforge.unit import errors

    assert errors.describe is describe
    assert errors.SAFE_TO_QUOTE is SAFE_TO_QUOTE


# --- describe_keys: the other question, and why it is a second function ------


def test_plain_identifier_keys_are_named_because_they_can_be():
    # ⭐ **The point of the whole function.** "You misspelled a field" is only
    # actionable if the field is named, and a key that is a plain lowercase
    # identifier structurally cannot be a path, an address or a token.
    assert describe_keys(["timeout_s", "grader"]) == "['grader', 'timeout_s']"


def test_the_naming_is_sorted_so_a_message_is_reproducible():
    # ⛔ R10: a refusal whose wording depends on dict ordering is a refusal two
    # runs disagree about.
    assert describe_keys(["b", "a"]) == describe_keys(["a", "b"])


@pytest.mark.parametrize(
    "key",
    [
        POISON,
        "contact@example.com",
        "has space",
        "Capitalised",
        "with/slash",
        "with:colon",
    ],
)
def test_a_key_that_could_carry_an_identifier_is_counted_not_shown(key):
    # ⛔ The guarantee is **structural, never a shape list**: a shape list
    # passes every poison shape it happens not to name.
    said = describe_keys([key])
    assert key not in said
    assert "1 of which 0 can be named safely" in said


def test_a_mixed_set_still_says_how_many_there_were():
    # ⚠️ The count is never dropped. A caller must learn how many keys went
    # unrecognised even when none of them can be quoted — otherwise a leaky key
    # beside a safe one disappears from the message entirely.
    said = describe_keys(["grader", POISON])
    assert "2 of which 1 can be named safely: ['grader']" == said
    assert POISON not in said


def test_it_answers_a_different_question_from_describe():
    # ⭐ Why this is a second function rather than a call to the first. Ruling
    # 10 removed *duplicate* rules; it did not ask for one function to answer
    # two questions. `describe` may never reproduce a str; this may, for the
    # subset that provably carries nothing.
    assert describe("grader") == "a str"
    assert "grader" in describe_keys(["grader"])


def test_no_module_carries_a_second_copy_of_this_rule():
    # ⛔ One describer: a verbatim copy of `_named` in another module is a
    # second spelling of one discipline, and this assertion refuses it.
    import ast

    from tests.support import repository_root

    offenders = []
    for path in sorted((repository_root() / "src").rglob("*.py")):
        tree = ast.parse(path.read_text("utf-8"), filename=path.name)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and "can be named safely" in ast.dump(node):
                if path.name != "describe.py":
                    offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == [], f"a second copy of the key-naming rule: {offenders}"


def test_the_contract_says_what_a_plain_key_can_still_be():
    # ⛔ **What a plain key can still be.** The docstring's promise is that a plain key cannot be a
    # path, an address or a token — which is true, and is *not* the same as
    # "cannot identify anybody". A bare lowercase personal name is a valid
    # lowercase identifier, and this function reproduces it verbatim:
    assert describe_keys(["jane"]) == "['jane']"
    # ⭐ So the contract has to say so, in the place a caller reads before
    # deciding what to pass. ⚠️ Many call sites depend on this distinction:
    # keys here, values through `describe`.
    # ⚠️ Whitespace-normalised: the sentence is wrapped prose, and a test that
    # depended on where the formatter broke the line would fail on a reflow
    # that changed nothing.
    said = " ".join((describe_keys.__doc__ or "").split())
    assert "categorical, not total" in said
    assert "pass keys here, never values" in said
