"""Reading one declared field, and refusing it without reproducing it (SF-05).

⚠️ The home-path material is assembled at run time rather than written as a
literal; this file is swept by the repository hygiene check like every other.
⛔ Nothing here came from any real machine, account or person.
"""

import string
from urllib.parse import quote

import pytest

from studyforge.address import is_slug
from studyforge.corpus.container.errors import ContainerError
from studyforge.corpus.container.fields import (
    FILENAME_PERMITTED,
    FILENAME_PERMITTED_DESCRIBED,
    is_filename_component,
    optional_label,
    optional_path,
    optional_slug,
    optional_text,
    required_text,
    said,
)

HOME = "/" + "home/jane"
WHERE = "container.json"


def test_required_text_returns_what_was_declared():
    assert required_text("Getting Started", "title", WHERE) == "Getting Started"


@pytest.mark.parametrize("value", [None, "", "   ", 3, ["a"], {"a": 1}])
def test_required_text_refuses_anything_else(value):
    with pytest.raises(ContainerError, match="required"):
        required_text(value, "title", WHERE)


def test_optional_text_lets_absence_through():
    assert optional_text(None, "note", WHERE) is None
    assert optional_text("why", "note", WHERE) == "why"


@pytest.mark.parametrize("value", ["", "   ", 3, ["a"]])
def test_optional_text_refuses_present_but_wrong(value):
    # ⚠️ Absent and empty are different: absent says "nothing to say", empty
    # says "somebody meant to write something here". Only one is a decision.
    with pytest.raises(ContainerError, match="text, or absent"):
        optional_text(value, "note", WHERE)


def test_optional_path_accepts_a_location_inside_the_source():
    assert optional_path("basics/01/README.md", "origin", WHERE) == "basics/01/README.md"
    assert optional_path(None, "origin", WHERE) is None


@pytest.mark.parametrize("value", ["/etc/passwd", "~/corpus", "../outside/x.md", "a/../../b"])
def test_optional_path_refuses_an_absolute_or_escaping_path(value):
    with pytest.raises(ContainerError, match="absolute or escaping path"):
        optional_path(value, "origin", WHERE)


@pytest.mark.parametrize("value", ["/etc/passwd", "~/corpus", "../outside/x.md"])
def test_and_never_quotes_it(value):
    # ⛔ **The one shape being refused here is precisely the shape that carries
    # a home directory**, so a refusal quoting it would copy personal data into
    # a log from the check that exists to catch it (R7). SF-03 measured that on
    # its own first attempt; this module is where the care lives so that a new
    # field reader cannot forget it.
    with pytest.raises(ContainerError) as raised:
        optional_path(value, "origin", WHERE)
    assert value not in str(raised.value)


def test_a_home_shaped_path_is_refused_without_a_trace_of_it():
    with pytest.raises(ContainerError) as raised:
        optional_path(f"{HOME}/corpus/README.md", "origin", WHERE)
    assert "jane" not in str(raised.value)


def test_optional_slug_requires_a_slug():
    # ⚠️ Measured: of the extraction source's 1290 unit entries, 0 carry a
    # `url_slug` that is not a slug, so this is a real contract and not a
    # hopeful one.
    assert optional_slug("what-a-triple-is", "url_slug", WHERE) == "what-a-triple-is"
    assert optional_slug(None, "url_slug", WHERE) is None
    with pytest.raises(ContainerError, match="slug, or absent"):
        optional_slug("Not A Slug", "url_slug", WHERE)


@pytest.mark.parametrize(
    ("value", "described"),
    [
        (None, "nothing"),
        ("", "an empty string"),
        ("   ", "an empty string"),
        ("real", "a str"),
        (3, "3"),
        (3.5, "a float"),
        (True, "a bool"),
        (["a"], "a list"),
        ({"a": 1}, "a dict"),
    ],
)
def test_said_describes_a_value_by_its_type(value, described):
    # ⭐ The same rule `studyforge.version._said` set: name the type, never
    # print an unexpected payload into a message that lands in a log.
    # ⛔ W17: `said` **is** `studyforge.describe.describe` now, imported under
    # this module's name for its callers. Two entries moved when the three
    # copies were reconciled — `3` is quoted, because an integer cannot carry
    # an identifier and a refusal that will not say `unit 4` is unactionable;
    # and a non-empty string is `a str`, because "text" said less. ⭐ What this
    # module had and the others lacked — an **empty string** named as one —
    # survived, and it is above.
    assert said(value) == described


def test_said_never_reproduces_a_payload():
    assert "jane" not in said({"leak": f"{HOME}/x"})
    assert "jane" not in said([f"{HOME}/x"])
    assert said(f"{HOME}/x") == "a str"


def test_optional_label_accepts_a_corpus_s_own_numbering():
    # ⭐ Not a slug: a label is presentation, and `4.4.1`, `vii` and `01` are
    # all things real material calls a unit.
    # ⚠️ `§4`, `A` and `unit_07` are NOT among them any more, and that is
    # Ruling 8's cost stated honestly: a permitted set admits less than a
    # forbidden list did. A corpus whose numbering is not in the class records
    # one that is and keeps the original in its **title**, which is under no
    # filename constraint at all.
    for label in ("4.4.1", "vii", "1-2", "01", "s1", "c1", "1"):
        assert optional_label(label, "label", WHERE) == label
    assert optional_label(None, "label", WHERE) is None


#: ⛔ **Measured 2026-09-09 on the merged tree: seven of these thirteen passed
#: both this guard and SF-03's `label_of` into a filename.** They are here as a
#: regression suite, not as a longer blacklist — the rule below is a permitted
#: set, and these are how it is checked.
UNUSABLE = [
    "a/b",
    "a\\b",
    "4 4 1",
    "a\tb",
    "a\nb",
    "a\rb",
    "a\vb",
    "a\fb",
    "a\xa0b",
    "a b",
    'a"b',
    "a:b",
    "a*b",
    "..",
    ".hidden",
    "-x",
]


@pytest.mark.parametrize("label", UNUSABLE)
def test_optional_label_refuses_what_could_not_become_a_filename(label):
    # ⛔ **The seam, closed where it opens.** SF-03's `label_of` refuses these
    # too. A map that accepted one would produce a corpus that validates and
    # then fails at render — a milestone later, in another package, with
    # nothing in between saying why.
    with pytest.raises(ContainerError, match="may carry only"):
        optional_label(label, "label", WHERE)


@pytest.mark.parametrize("label", ["a/b", "4 4 1", f"{HOME}/x"])
def test_and_the_refusal_never_reproduces_the_label(label):
    # ⛔ Rubric §1f, the emission clause: every refusal in this module describes
    # a fault rather than echoing a value read out of somebody else's file.
    with pytest.raises(ContainerError) as raised:
        optional_label(label, "label", WHERE)
    assert label not in str(raised.value)
    assert "jane" not in str(raised.value)


def test_the_refusal_states_the_permitted_class():
    # ⭐ A closed statement an author can act on. A forbidden class can only
    # ever be a partial one, which is Ruling 8 in one sentence.
    with pytest.raises(ContainerError, match=FILENAME_PERMITTED_DESCRIBED):
        optional_label("a b", "label", WHERE)


def test_the_rule_is_a_permitted_set_and_not_a_forbidden_list():
    # ⛔ **Ruling 8, asserted rather than described.** A forbidden list is an
    # open set: it is checkable only against characters somebody thought of. A
    # permitted set is checkable against *everything*, so this test can sweep
    # the whole of Latin-1 plus a sample of what lies beyond it and know the
    # answer for every character without having listed one.
    permitted = {chr(code) for code in range(0x110000) if is_filename_component("a" + chr(code))}
    assert permitted == set(string.ascii_lowercase + string.digits + ".-")


def test_a_filename_component_must_begin_with_a_letter_or_digit():
    # ⛔ What a permitted set alone does not give you: `..` is a path traversal
    # and every character in it is permitted.
    assert is_filename_component("a.b") and not is_filename_component("..")
    assert is_filename_component("a-b") and not is_filename_component("-b")


def test_every_accepted_label_survives_a_file_url_untouched():
    # ⛔ **R8 is why the open set was a defect and not untidiness**: `:` and `"`
    # both passed the old forbidden list, and neither survives a `file://`
    # href. The permitted set is a subset of RFC 3986's unreserved class, so a
    # name minted from it never needs escaping to be linkable.
    for character in sorted(string.ascii_lowercase + string.digits + ".-"):
        assert quote(character, safe="") == character


@pytest.mark.parametrize("label", ["A", "VII", "Part2", "unit_07"])
def test_an_uppercase_or_underscored_label_is_refused(label):
    # ⚠️ **Ruling 8's cost, and the reason it is worth paying.** `A` and `a`
    # are one filename on a case-insensitive filesystem, and the `sibling`
    # profile places twenty units in a single directory — so an uppercase label
    # is a collision this framework would generate and then fail to detect on
    # the very machine that generated it. `_` is simply not what a slug
    # accepts, and the class is derived from that rather than curated.
    with pytest.raises(ContainerError, match="may carry only"):
        optional_label(label, "label", WHERE)


def test_the_permitted_class_is_the_slug_class_and_is_not_re_typed():
    # ⛔ **A constant exported and then re-typed is a finding on sight**, so
    # this one is derived: it is exactly what `is_slug` accepts, plus `.` for
    # `4.4.1`. ⭐ Pinned literally here so a change to `is_slug` silently
    # widening what reaches a filename is a decision somebody makes, not one
    # that arrives.
    assert FILENAME_PERMITTED == frozenset(string.ascii_lowercase + string.digits + "-.")
    assert all(is_slug(character) for character in FILENAME_PERMITTED - {"-", "."})
