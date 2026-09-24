"""Mirror of `tests/floor/palettes/rejected.py` (R12).

⛔ **The grammar is asserted both ways**: a band the document could write is
read, and one it must never accept — a bound in saturation, a half-written range
— is refused, taking its whole row out of the population rather than widening it.

⭐ **The LIVE table is asserted inhabited and PARSED**: a renamed
column reads as zero rejected identities, and a check that compares nothing is
green over everything. ⛔ **That is a red suite here, never a quiet pass at the
floor.**

⭐ **The accepted identity is asserted here too**: the spec records it beside the
rejected one, and never locates a page in any form the predicate below can find.
"""

from __future__ import annotations

import re

import tests.floor.palettes.rejected as rejected_module
from tests.floor.palettes.rejected import (
    GRADIENT_ROLE,
    Band,
    band,
    convention,
    part,
    roles,
    signatures,
)
from tests.floor.palettes.support import CREAM, GRADIENT, SATURATED, SLATE, convention_text
from tests.support import assert_package_contract, repository_root

#: The spec's record of the accepted identity, located by the heading it carries.
ACCEPTED_HEADING = "The accepted identity"

#: ⛔ What a reference page must NEVER be given as: a URL, a home path, or any
#: multi-segment path. ⭐ Named in words is the whole instruction.
_LOCATED = re.compile(r"https?://|~/|(?:/[\w.-]+){2,}")


def accepted() -> str:
    """The accepted-identity section of the live convention, up to the next heading."""
    lines = convention_text().splitlines()
    found = [
        at for at, line in enumerate(lines) if line.startswith("#") and ACCEPTED_HEADING in line
    ]
    assert len(found) == 1, f"the convention carries {len(found)} accepted-identity sections"
    start = found[0]
    level = len(lines[start]) - len(lines[start].lstrip("#"))
    for at in range(start + 1, len(lines)):
        if lines[at].startswith("#") and len(lines[at]) - len(lines[at].lstrip("#")) <= level:
            return "\n".join(lines[start:at])
    return "\n".join(lines[start:])


def test_states_its_contract():
    assert_package_contract(rejected_module, "tests.floor.palettes.rejected")


# --- the grammar, both ways ----------------------------------------------------


def test_a_band_is_read_in_either_form():
    assert band("hue 20-70") == Band("hue", 20, 70, "hue 20-70")
    assert band("chroma >= 25").low == 25
    assert band("chroma >= 25").high == 100
    assert band("light <= 12") == Band("light", 0, 12, "light <= 12")


def test_a_band_over_something_that_is_not_a_measure_is_refused():
    assert band("saturation >= 40") is None
    assert band("hue") is None
    assert band("hue 20 to 70") is None


def test_a_part_whose_band_is_malformed_is_NOT_a_part():
    assert part("ground: hue 20-70, light >= 85").role == "ground"
    assert part("ground: hue 20-70, saturation >= 40") is None
    assert part("ground") is None


def test_a_ROW_whose_parts_do_not_parse_is_dropped_rather_than_guessed_at():
    header = "| Rejected identity | Every part must be present | Why |\n|---|---|---|\n"
    assert signatures(header + "| Bad | `ground: saturation >= 40` | prose |\n") == ()
    assert len(signatures(header + "| Good | `ground: chroma >= 30` | prose |\n")) == 1


def test_the_tables_are_found_by_their_HEADER_and_not_by_a_heading():
    text = convention_text()
    assert signatures(text.replace("| Rejected identity |", "| Rejected palette |")) == ()
    assert roles(text.replace("| Role | Read from |", "| Role | Read |")) == {}


def test_a_row_is_a_CONJUNCTION_and_keeps_the_roles_it_is_written_over():
    header = "| Rejected identity | Every part must be present | Why |\n|---|---|---|\n"
    row = "| Two | `ground: chroma >= 30` + `accent: hue 0-20, chroma >= 45` | prose |\n"
    (signature,) = signatures(header + row)
    assert len(signature.parts) == 2
    assert signature.roles() == ("ground", "accent")
    assert signature.ground == "prose"


# --- the live table ------------------------------------------------------------


def test_the_LIVE_table_is_inhabited_and_every_row_PARSES():
    carried, rejected = convention(repository_root())
    assert len(rejected) >= 5
    assert {signature.name for signature in rejected} >= {CREAM, SLATE, SATURATED, GRADIENT}
    assert carried
    for signature in rejected:
        assert signature.parts
        assert signature.ground.strip()
        for one in signature.parts:
            assert one.role in carried, one.text


def test_the_GRADIENT_role_is_the_one_role_no_token_carries():
    carried, _rejected = convention(repository_root())
    assert carried[GRADIENT_ROLE] == ()
    assert all(tokens for role, tokens in carried.items() if role != GRADIENT_ROLE)


def test_a_tree_with_no_convention_reads_two_EMPTY_answers(tmp_path):
    # ⛔ The floor runs over trees that are not this repository.
    assert convention(tmp_path) == ({}, ())


# --- the other half of the table: the accepted identity ----------------------------


def test_the_convention_RECORDS_the_accepted_identity():
    text = accepted()
    assert "cool slate" in text.lower()
    assert "ONE loud accent" in text
    assert "none in the identity" in text


def test_the_accepted_identity_is_described_and_never_LOCATED():
    text = accepted()
    assert _LOCATED.search(text) is None, "the identity is described in words, never located"


def test_the_predicate_that_says_so_actually_FIRES_on_a_planted_location():
    # ⛔ The other direction: the green above must not be a pattern matching nothing.
    for planted in ("https://example.invalid/page", "~/pages/reference.html", "/a/b/c.html"):
        assert _LOCATED.search(accepted() + planted) is not None
