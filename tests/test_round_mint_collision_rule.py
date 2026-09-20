"""`W395`: the mint-collision rule, read OUT of `delivery-flow.md` and asserted both ways.

⛔ **The defect it answers, measured as `W381/2`:** two rows minted in ONE round
contradicted each other — one row's clause kept a test of a state the other
row's ruling removed — and the collision surfaced only when the second office
ran the first's tests. ⭐ **The rule cannot be a checker**: whether one clause
quotes another row's subject is a reading of two arguments, and no instrument
here reads a clause for what it depends on.

⚠️ **So what IS asserted is the one thing that can be:** the rule is in the
document, it states BOTH of its remedies rather than one, it says that neither
is not an option, it names the round it was read on, and that round RESOLVES.
⛔ **Each obligation is asserted in both directions** — deleting one from a copy
of the live section is refused by the same predicate that accepts the live one —
so a rule quietly softened to *the register may order them* turns this red
instead of reading green over half a rule.

⭐ **Why a test at all for a document.** `W381/2`'s cost was an office-round, and
the sentence that prevents it is one nobody runs. A clause that nothing reads is
the exact failure `W392` is open for one directory over.
"""

from __future__ import annotations

import re

import pytest

from tests.support import repository_root

DOCUMENT = "docs/conventions/delivery-flow.md"
ARCHIVE = "docs/tasks/BOARD-ARCHIVE.md"

#: The section, located by text it carries rather than by a line number.
HEADING = "A round that mints one row whose clause QUOTES what another of the same round may remove"

#: ⛔ Each obligation the rule is made of, and the text the section carries for
#: it. ⚠️ A FRAGMENT and never the whole sentence, so the rule can be worded
#: better without this file refusing the improvement — but never SHORTER by one
#: obligation, which is the failure being guarded.
OBLIGATIONS = {
    "both rows carry it": "both rows say so",
    "or the register orders them": "the register ORDERS them",
    "and never neither": "never neither",
    "the office reads its own row": "An office reads ITS",
    "the measurement it answers": "`W381/2`",
    "the round it was read on": "#po-round-126",
}


def document(name: str = DOCUMENT) -> str:
    """The tracked document, as text."""
    return (repository_root() / name).read_text(encoding="utf-8")


def section(text: str, heading: str = HEADING) -> str:
    """The one section whose heading carries `heading`, up to the next heading of its level.

    ⛔ Returns `""` when the heading is absent, so a missing section is a refusal
    and never an empty pass.
    """
    lines = text.splitlines()
    found = [at for at, line in enumerate(lines) if line.startswith("#") and heading in line]
    if len(found) != 1:
        return ""
    start = found[0]
    level = len(lines[start]) - len(lines[start].lstrip("#"))
    for at in range(start + 1, len(lines)):
        current = lines[at]
        if current.startswith("#") and len(current) - len(current.lstrip("#")) <= level:
            return "\n".join(lines[start:at])
    return "\n".join(lines[start:])


def stated(text: str) -> set[str]:
    """Which of `OBLIGATIONS` the given section states."""
    return {name for name, carried in OBLIGATIONS.items() if carried in text}


def slug(heading: str) -> str:
    """A heading's anchor, as the markdown the board is rendered with derives it."""
    return re.sub(r"[^a-z0-9 -]", "", heading.strip("# ").lower()).replace(" ", "-")


def test_the_document_carries_the_rule_exactly_once():
    # ⛔ Ruling 48: an absent heading returns "", and "" states no obligation —
    # so this assertion is what keeps every one below from passing over nothing.
    assert section(document()), f"{DOCUMENT} does not carry the mint-collision rule"


def test_the_rule_states_EVERY_obligation():
    assert stated(section(document())) == set(OBLIGATIONS)


@pytest.mark.parametrize("obligation", sorted(OBLIGATIONS))
def test_a_rule_with_ONE_obligation_removed_is_REFUSED(obligation):
    # ⛔ The other direction, per obligation: a rule softened to one of its two
    # remedies, or one that stops naming its reading, is not this rule.
    softened = section(document()).replace(OBLIGATIONS[obligation], "")
    assert stated(softened) == set(OBLIGATIONS) - {obligation}


def test_the_rule_names_TWO_remedies_and_not_one():
    # ⭐ The half that `W381/2` actually needed: an office reads its own row, so
    # a note written only where the removal happens reaches nobody.
    text = section(document())
    assert stated(text) >= {"both rows carry it", "or the register orders them"}
    assert "either" in text


def test_the_reading_it_names_RESOLVES_in_the_archive():
    # ⛔ A citation is not an edge until both ends exist: the round it was read
    # on has to be a heading somebody can open, not a number in a sentence.
    anchor = OBLIGATIONS["the round it was read on"].lstrip("#")
    headings = {slug(line) for line in document(ARCHIVE).splitlines() if line.startswith("#")}
    assert anchor in headings


def test_the_rule_sits_under_the_board_section():
    # ⭐ Where a row is MINTED is where the obligation lands, and that is the
    # board's part of the flow — not the review gate's and not an office's.
    text = document()
    assert text.index("## The board") < text.index(HEADING) < text.index("## The two-PO channel")
