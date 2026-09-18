"""The grader shipped with the material for `greet`."""

from greet import greet


def test_the_greeting_names_who_it_greets():
    assert greet("Ada") == "Hello, Ada"
