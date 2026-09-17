r"""Ruling 241's two FORMS, read out of the rubric and asserted SOUND (`W304`).

⛔ **The defect this exists to stop, and it is not the one the row alleged.**
`W304` was opened against the rubric's floor snippet on the reading that `$?`
after a pipeline is `tail`'s. ⭐ **It is not, THERE:** the line sits in Ruling
241's own `FORM 1` and the line above it is `set -o pipefail`, which makes `$?`
the PIPELINE's status. The row's excerpt quoted the pipeline line **detached
from the line that binds it**, and the detachment is what produced the charge.

⚠️ **So the real defect is that the binding was detachable**, and this module is
what makes losing it loud: if `set -o pipefail` is ever dropped, moved below the
pipeline, or split into another fence, `FORM 1` silently becomes the very defect
Ruling 241 mints — green in every other instrument, because a snippet that is
only READ is never run.

## ⛔ THE COUNTER-EXAMPLE IS EXEMPT BY A PROPERTY IT CARRIES, NEVER BY LINE NUMBER

⭐ **Ruling 76's block deliberately contains the WRONG construction as teaching
material**, and says so in its own trailing comment. ⛔ **An office working from
*"fix the `$?`-after-pipeline sites"* would delete the example that teaches the
trap, and the page would get WORSE while every gate stayed green.** ⚠️ So the
exemption here is the comment the line carries about itself — a property in the
text — and `test_the_counter_example_is_still_wrong_and_still_says_so` fails if
somebody "corrects" it.

## ⛔ THE BOUND, STATED: TWO BLOCKS, AND THIS IS NOT A LINT RULE OVER PROSE

⛔ **This reads exactly the two fenced blocks Ruling 241 owns** — its FORM block
and the counter-example it annotates — each located by text it carries and each
asserted UNIQUE. ⭐ **It is deliberately NOT a sweep over every shell snippet in
the document.** ⚠️ The rubric contains wrong snippets on purpose, as warnings; a
checker that could not tell a warning from an instruction would refuse the
document for teaching, which is a worse defect than the one it would catch.
⛔ **The wider population is a FINDING in `W304`'s handoff, not a rule here.**
"""

from __future__ import annotations

import pytest

from tests.support import repository_root

#: The document carrying both blocks. ⚠️ A path rather than a pointer: this is a
#: test, and Ruling 285(b) binds a handoff's citations, not a constant.
RUBRIC = "docs/conventions/review-rubric.md"

#: ⛔ The FORM block, located by what it CALLS ITSELF rather than by a line
#: number or a heading — both of which move every time the rubric is re-wrapped.
FORM_MARKERS = ("FORM 1", "FORM 2")

#: The binding that makes a pipeline carry its own exit code.
PIPEFAIL = "set -o pipefail"

#: ⛔ The counter-example's own description of itself, which is what exempts it.
#: ⭐ Ruling 76's block exists to SHOW the trap, and this is the text in which it
#: says so. A "correction" that removed the wrongness would remove this too.
WARNS = "this is tail's exit"


def rubric() -> str:
    return (repository_root() / RUBRIC).read_text(encoding="utf-8")


def fenced_blocks(text: str) -> list[list[str]]:
    """Every ``` fenced block in `text`, as its lines."""
    blocks: list[list[str]] = []
    current: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            if inside:
                blocks.append(current)
                current = []
            inside = not inside
            continue
        if inside:
            current.append(line)
    return blocks


def _sole(blocks: list[list[str]], predicate, what: str) -> list[str]:
    """The one block satisfying `predicate`, asserted unique."""
    found = [block for block in blocks if predicate(block)]
    assert len(found) == 1, f"expected one {what} block in {RUBRIC}, found {len(found)}"
    return found[0]


def form_block() -> list[str]:
    """Ruling 241's FORM block — the one naming both forms."""
    return _sole(
        fenced_blocks(rubric()),
        lambda block: all(any(marker in line for line in block) for marker in FORM_MARKERS),
        "Ruling 241 FORM",
    )


def counter_example_block() -> list[str]:
    """Ruling 76's block, which carries the WRONG construction on purpose."""
    return _sole(
        fenced_blocks(rubric()),
        lambda block: any(WARNS in line for line in block),
        "Ruling 76 counter-example",
    )


def reads_exit_after_pipeline(line: str) -> bool:
    """Whether `line` reads `$?` with a pipeline to its left, on the SAME line.

    ⛔ `||` is not a pipeline. ⭐ The question is only ever about one physical
    line: `$?` read on the NEXT line is FORM 2 and is correct by construction.
    """
    if "$?" not in line:
        return False
    left = line.split("$?", 1)[0].replace("||", "")
    return "|" in left


def bound_lines(block: list[str]) -> list[tuple[int, str]]:
    """`(index, line)` for each pipeline-exit read in `block` that `pipefail` binds."""
    return [
        (index, line)
        for index, line in enumerate(block)
        if reads_exit_after_pipeline(line) and any(PIPEFAIL in earlier for earlier in block[:index])
    ]


def unbound_lines(block: list[str]) -> list[tuple[int, str]]:
    """`(index, line)` for each pipeline-exit read in `block` that nothing binds."""
    reads = [(index, line) for index, line in enumerate(block) if reads_exit_after_pipeline(line)]
    return [pair for pair in reads if pair not in bound_lines(block)]


# --- the predicate itself, asserted BOTH WAYS before it is trusted (R12) ------

BOUND = [PIPEFAIL, 'python3 -m tools.quality | tail -4; echo "FLOOR_EXIT=$?"']
DETACHED = ['python3 -m tools.quality | tail -4; echo "FLOOR_EXIT=$?"']


def test_the_predicate_reads_a_pipeline_exit_and_refuses_what_is_not_one():
    # ⭐ The positive direction, and three negatives. Without these the module
    # below could be asserting a property of a predicate that answers `False`
    # to everything — Ruling 191's family at the level of a helper.
    assert reads_exit_after_pipeline('python3 -m tools.quality | tail -4; echo "E=$?"')
    assert not reads_exit_after_pipeline('echo "PYTEST_EXIT=$?"'), "FORM 2 is not a pipeline read"
    assert not reads_exit_after_pipeline("python3 -m tools.quality | tail -4"), "no $? at all"
    assert not reads_exit_after_pipeline('cmd || exit; echo "E=$?"'), "`||` is not a pipeline"


def test_a_form_that_keeps_its_binding_is_accepted_and_one_that_loses_it_is_refused():
    # ⛔ **THE PLANT, in the instrument's own terms.** `DETACHED` is FORM 1 with
    # exactly one line removed — the line `W304`'s excerpt omitted — and the
    # reader must call that out rather than agree with it.
    assert bound_lines(BOUND) and not unbound_lines(BOUND), "the bound form must be accepted"
    assert unbound_lines(DETACHED) and not bound_lines(DETACHED), (
        "FORM 1 with `set -o pipefail` removed must be REFUSED; a reader that accepts "
        "it would have agreed with the detached quotation that opened W304"
    )


# --- FORM 1 keeps its binding -------------------------------------------------


def test_the_form_block_actually_contains_a_pipeline_exit_read():
    # ⛔ **INHABITATION, and it is not decoration** (Rulings 124, 191). Every
    # assertion below is vacuously true of a block that stopped containing the
    # construction, and a green from an empty population is the pass reading
    # this project has been burned by more than once.
    block = form_block()
    reads = [line for line in block if reads_exit_after_pipeline(line)]
    assert reads, (
        "Ruling 241's FORM block no longer contains a pipeline whose exit code is "
        "read, so FORM 1 has changed shape and these checks guard nothing"
    )


def test_form_one_pipeline_is_bound_by_pipefail_in_its_own_fence():
    # ⛔ **THE WHOLE OF `W304`.** Unbound, this line IS the defect Ruling 241
    # mints — and it would be green in every other instrument, because a snippet
    # that is only read is never run.
    block = form_block()
    assert not unbound_lines(block), (
        f"Ruling 241's FORM block reads $? after a pipeline with no `{PIPEFAIL}` "
        f"above it in the same fence: {[line for _index, line in unbound_lines(block)]}. "
        f"That is the defect this ruling exists to mint, printed as the remedy"
    )


def test_the_binding_precedes_the_pipeline_rather_than_merely_appearing():
    # ⭐ Order is the property, not presence. `pipefail` set BELOW the pipeline
    # binds nothing, and a check for the string alone would pass on it.
    block = form_block()
    for index, line in bound_lines(block):
        above = [number for number, text in enumerate(block[:index]) if PIPEFAIL in text]
        assert above, f"{line!r} is not preceded by {PIPEFAIL} in its own fence"


def test_form_two_reads_its_exit_on_the_very_next_line():
    # ⛔ FORM 2's whole claim is *nothing in between*. A `tail` slipped between
    # the command and the `echo` would make its reading `tail`'s, which is the
    # same defect wearing the other form.
    block = form_block()
    redirects = [index for index, line in enumerate(block) if "> /tmp/out.txt" in line]
    assert len(redirects) == 1, f"expected one redirect in FORM 2, found {len(redirects)}"
    following = block[redirects[0] + 1]
    assert "$?" in following, (
        f"FORM 2's exit code is not read on the line after the redirect; the next "
        f"line is {following!r}, and anything in between makes the reading its own"
    )


# --- and the counter-example is left exactly as wrong as it was --------------


def test_the_counter_example_is_still_wrong_and_still_says_so():
    # ⛔ **EXEMPT BY THE PROPERTY IT CARRIES, NEVER BY LINE NUMBER.** This block
    # is teaching material: it shows the reader the trap and describes itself as
    # doing so. An office "fixing the $?-after-pipeline sites" would delete the
    # example that teaches the defect, and every gate would stay green.
    block = counter_example_block()
    assert unbound_lines(block), (
        "Ruling 76's counter-example no longer demonstrates the defect it exists to "
        "teach; it is EXEMPT from the rule above and must not be 'corrected'"
    )
    assert any(WARNS in line for line in block), (
        f"the counter-example no longer says {WARNS!r} about itself, which is the "
        f"only thing distinguishing it from a snippet a reader should copy"
    )


@pytest.mark.parametrize("marker", FORM_MARKERS)
def test_both_forms_are_still_named_in_the_block(marker):
    # ⭐ The locator's own premise, asserted rather than assumed: if a form were
    # renamed, `form_block()` would raise on uniqueness and the failure would
    # read as a missing block rather than as a renamed one.
    assert any(marker in line for line in form_block()), f"{marker} is no longer named"
