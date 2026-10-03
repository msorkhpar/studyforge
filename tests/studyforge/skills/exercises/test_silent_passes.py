"""A test that cannot fail is refused by the gates, in Python and in TypeScript.

⭐ **Every reading is a real process** (`pytest`, `node --test`) over real files: a planted
test that asserts nothing, asserts a truthy value, compares loosely, asserts inside a loop that
never runs or leaves a promise unawaited is put in the place of the main ask's test, and the
gates run as they do for any draft. A test that passes on the starter proves nothing about the
task, so `G2` (every test fails on the starter) refuses each one, and the draft does not ship.

**What it asserts.**
- the unplanted draft of each language clears, so a refusal below is the plant's;
- each planted test of each language is refused, and by `G2`: the one gate whose reading is "every
  test fails on the starter" (a plant that fails to load, or whose file fails, is told apart by
  the failure not being an assertion);
- the refusal names the case whose test passed on the starter.

⛔ Nothing here asserts about a corpus: the drafts are the shared fixtures of the pytest and
`node --test` practices.
"""

from __future__ import annotations

import pytest

from studyforge.exercise.gates import G2
from studyforge.skills.exercises import gate_code
from tests.studyforge.skills.exercises import node_practice as node
from tests.studyforge.skills.exercises import pytest_practice as python
from tests.studyforge.skills.exercises.authoring import Running
from tests.studyforge.skills.exercises.test_node_practice import Recording as NodeRunning
from tests.studyforge.skills.exercises.test_pytest_practice import _brief, _g

ASK = 'assert normalise(" one two") == "one two"'

#: The main ask's test, five ways of passing on a starter that returns its input.
PYTHON_PLANTS = {
    "asserts nothing": "    normalise(\" one two\")",
    "asserts a truthy value": "    assert normalise(\" one two\")",
    "asserts a tuple": "    assert (normalise(\" one two\") == \"one two\", \"never read\")",
    "asserts in a loop that never runs": "    for got in []:\n        assert got == \"one two\"",
    "asserts that it is not None": "    assert normalise(\" one two\") is not None",
}

TS_ASK = 'assert.equal(normalise(" one two"), "one two");'
TS_PLANTS = {
    "asserts nothing": 'normalise(" one two");',
    "asserts a truthy value": 'assert.ok(normalise(" one two"));',
    "asserts in a loop that never runs": (
        'for (const got of [] as string[]) {\n    assert.equal(got, "one two");\n  }'
    ),
    "compares loosely": 'assert.equal(normalise(" 1") == (1 as unknown as string), true);',
}


def _python(tmp_path, body: str):
    brief, ledger = _brief(tmp_path)
    made = python.draft(brief)
    planted = made.tests.replace(f"    {ASK}", body)
    assert planted != made.tests, "the plant did not change the test"
    made = python.draft(brief, tests=planted)
    return gate_code(made, brief, ledger, Running(), source="demo", where="w")


def _running(made) -> NodeRunning:
    """The real `node --test` runner, told which solution each run has in place."""
    return NodeRunning(
        {
            "reference": made.reference,
            "starter": made.starter,
            **{f"plant:{case}": text for case, text in made.plants.items()},
        }
    )


def _node(tmp_path, body: str):
    brief, ledger = _brief(tmp_path)
    made = node.draft(brief)
    planted = made.tests.replace(f"  {TS_ASK}", f"  {body}")
    assert planted != made.tests, "the plant did not change the test"
    made = node.draft(brief, tests=planted)
    return gate_code(made, brief, ledger, _running(made), source="demo", where="w")


def test_the_unplanted_drafts_clear_so_a_refusal_is_the_plants(tmp_path):
    brief, ledger = _brief(tmp_path)
    assert gate_code(python.draft(brief), brief, ledger, Running(), source="demo", where="w").clears
    made = node.draft(brief)
    assert gate_code(made, brief, ledger, _running(made), source="demo", where="w").clears


@pytest.mark.parametrize("how", sorted(PYTHON_PLANTS))
def test_a_python_test_that_cannot_fail_is_refused_by_g2(tmp_path, how):
    gated = _python(tmp_path, PYTHON_PLANTS[how])
    assert not gated.clears
    assert _g(gated, G2).held is False
    assert python.MAIN_CASE.says in _g(gated, G2).says


@pytest.mark.parametrize("how", sorted(TS_PLANTS))
def test_a_typescript_test_that_cannot_fail_is_refused_by_g2(tmp_path, how):
    gated = _node(tmp_path, TS_PLANTS[how])
    assert not gated.clears
    assert _g(gated, G2).held is False
    assert node.MAIN_CASE.says in _g(gated, G2).says


def test_an_unawaited_promise_does_not_clear_either(tmp_path):
    # ⚠️ Node reports an assertion that settles after its test ended against the FILE, not the
    # test, so this plant is refused by a different reading than the others: never shipped.
    body = 'assert.rejects(async () => normalise(" one two"), RangeError);'
    gated = _node(tmp_path, body)
    assert not gated.clears
