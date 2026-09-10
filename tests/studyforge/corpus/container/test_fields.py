"""Reading one declared field, and refusing it without reproducing it (SF-05).

⚠️ The home-path material is assembled at run time rather than written as a
literal; this file is swept by the repository hygiene check like every other.
⛔ Nothing here came from any real machine, account or person.
"""

import pytest

from studyforge.corpus.container.errors import ContainerError
from studyforge.corpus.container.fields import (
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
        ("real", "text"),
        (3, "an int"),
        (3.5, "a float"),
        (True, "a bool"),
        (["a"], "a list"),
        ({"a": 1}, "a dict"),
    ],
)
def test_said_describes_a_value_by_its_type(value, described):
    # ⭐ The same rule `studyforge.version._said` set: name the type, never
    # print an unexpected payload into a message that lands in a log.
    assert said(value) == described


def test_said_never_reproduces_a_payload():
    assert "jane" not in said({"leak": f"{HOME}/x"})
    assert "jane" not in said([f"{HOME}/x"])
    assert said(f"{HOME}/x") == "text"
