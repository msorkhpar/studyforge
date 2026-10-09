"""`example_run` and a tab's `run` (`render.page.examplerun`): no strip when off, a program strip when named."""

from __future__ import annotations

from types import SimpleNamespace

from studyforge.render.page import examplerun

TAB = {"lang": "kotlin", "span": 1, "code": "examples/a/src/main/kotlin/A.kt"}


def placement(**extra):
    base = {"code": (".kt",), "pairing": lambda path: (path, "examples/a/src/test/kotlin/ATest.kt"), "corpus": "c"}
    return SimpleNamespace(**{**base, **extra})


def test_a_tab_paired_with_a_test_draws_the_strip_it_always_did():
    drawn = examplerun.strip(TAB, placement())
    assert 'data-example-run="examples/a/src/main/kotlin/A.kt"' in drawn
    assert "data-example-program" not in drawn


def test_example_run_off_draws_no_strip_on_any_tab():
    assert examplerun.strip(TAB, placement(example_run=False)) == ""
    assert examplerun.strip({**TAB, "run": ["gradle", "run"]}, placement(example_run=False)) == ""


def test_a_tab_that_names_its_program_draws_a_program_strip_with_no_test_needed():
    drawn = examplerun.strip({**TAB, "run": ["gradle", "-q", "runExample"]}, placement(pairing=None))
    assert "data-example-program" in drawn
