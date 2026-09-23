"""Mirror of `tests/floor/reserved_addresses.py` (R12): the vocabulary, and R7's policy over it.

⭐ **Ported from the tooling's own mirror of the original.** The tooling's copy also reads the
MERGE PATH's policy over the same list — an office's author line — and that half is process: it
stays with the tooling's test. What is here is the vocabulary's own membership question and the
floor's R7 exemption built from it, with the plant that proves the exemption tracks the list.

⛔ **EVERY ADDRESS IN THIS FILE IS FABRICATED, AND THE FIXTURES ARE BUILT TO STAY LEGAL.**
An address whose domain is not reserved matches the floor's own email shape and is NOT
exempt, so writing one whole would redden the floor this file is half about. ⭐ Two
techniques: a person's stand-in is DOTLESS (`workstation`), which the shape regex cannot
match because it requires a dot in the domain; and every other non-exempt domain is
ASSEMBLED from fragments, so no literal is ever address-shaped.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import tests.floor.reserved_addresses as reserved
from tests.floor.personal_data.shapes import build_allowed_address, shape_matches
from tests.support import assert_package_contract

#: ⛔ A FABRICATED token in neither RFC and in no tree. The plant adds it to the vocabulary.
_PLANTED = "zzz" + "reserved"

#: ⭐ Domains that ARE reserved, derived from the vocabulary itself rather than retyped.
_RESERVED = (
    *reserved.RESERVED_TLDS,
    *reserved.RESERVED_DOMAINS,
    *(f"host.{name}" for name in reserved.RESERVED_TLDS),
    *(f"mail.{name}" for name in reserved.RESERVED_DOMAINS),
)

#: ⛔ Domains that are NOT reserved, every one assembled so no literal is address-shaped.
_NOT_RESERVED = (
    "workstation",
    "notexample" + ".co",
    "gmail" + ".com",
)

#: ⚠️ A domain somebody really owns, carrying a reserved name that is NOT where it ENDS.
#: ⛔ **The two sides DISAGREE here, and the disagreement is in their GRAMMARS and not in
#: the vocabulary**: the floor looks for a reserved name INSIDE free text and stops at a
#: word boundary, while `tools.authorship` parses the domain and tests its SUFFIX. ⭐ This
#: row shares the LIST and rewrites neither grammar, so the divergence is asserted below as
#: the state of the tree rather than smoothed away — it is filed as `W310/1`.
_GRAMMARS_DISAGREE = "example.com" + ".elsewhere.co.uk"


def _floor_exempts(domain: str) -> bool:
    """Report whether the floor's R7 arm exempts an address at `domain`, rebuilt now."""
    return bool(build_allowed_address().search("@" + domain))


# --- the contract ------------------------------------------------------------------------


def test_states_its_contract():
    assert_package_contract(reserved, "tests.floor.reserved_addresses")


def test_the_vocabulary_is_INHABITED_and_the_probes_hold_BOTH_verdicts():
    # ⛔ Ruling 191: an empty vocabulary, or a probe list of one verdict, would satisfy
    #    every comparison below for free — green where red was required.
    assert reserved.RESERVED_TLDS, "the reserved TLDs are empty"
    assert reserved.RESERVED_DOMAINS, "the reserved domains are empty"
    assert len(_RESERVED) >= 8 and len(_NOT_RESERVED) >= 3
    assert {reserved.is_reserved(domain) for domain in (*_RESERVED, *_NOT_RESERVED)} == {
        True,
        False,
    }


def test_this_module_carries_NO_DEPENDENCY_because_the_merge_path_would_inherit_it():
    # ⛔ The copy keeps the original's leaf property: a vocabulary module reaches nothing
    #    that can fail to import, so the floor cannot crash on a tree too broken to import.
    #
    # ⚠️ READ AS A PARSE, NEVER AS A LINE SCAN, and the first form of this test was the
    #    line scan: it matched a DOCSTRING SENTENCE beginning "from ", which is Ruling
    #    337's defect — a claim about a module established by grepping its text.
    source = Path(reserved.__file__).read_text(encoding="utf-8")
    imported = [
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, (ast.Import, ast.ImportFrom))
        and getattr(node, "module", None) != "__future__"
    ]
    assert imported == [], [ast.dump(node) for node in imported]


# --- the vocabulary's own membership question, both ways (R12) -----------------------------


@pytest.mark.parametrize("domain", _RESERVED)
def test_a_reserved_domain_is_reserved(domain):
    assert reserved.is_reserved(domain) is True


@pytest.mark.parametrize("domain", (*_NOT_RESERVED, _GRAMMARS_DISAGREE))
def test_anything_else_is_not(domain):
    assert reserved.is_reserved(domain) is False


def test_case_and_surrounding_space_are_absorbed_and_nothing_is_a_verdict():
    assert reserved.is_reserved("  EXAMPLE.INVALID  ") is True
    assert reserved.is_reserved("") is False
    assert reserved.is_reserved("   ") is False


# --- ONE VOCABULARY, TWO POLICIES: they agree on the LIST -----------------------------------


@pytest.mark.parametrize("domain", (*_RESERVED, *_NOT_RESERVED))
def test_the_floor_exempts_exactly_what_is_RESERVED(domain):
    # ⛔ The row's subject. `tools.authorship` reads a reserved address as an OFFICE's line;
    #    the floor reads it as exempt from R7's shape arm. ⭐ Two policies — but the LIST
    #    behind them is one, so the two answers move together on every domain.
    assert _floor_exempts(domain) is reserved.is_reserved(domain)


def test_the_two_GRAMMARS_differ_where_a_reserved_name_is_not_where_the_domain_ENDS():
    # ⛔ DISCLOSED, never smoothed (`W310/1`). The VOCABULARY is one list and both sides
    #    read it; what differs is how each LOOKS FOR a name in it, and that is each side's
    #    own policy. ⚠️ `W310` shares the list and rewrites neither grammar — an earlier
    #    form of this row DID anchor the floor's, and it reddened the floor on another
    #    office's negative fixture, which is how the divergence was measured at all.
    assert reserved.is_reserved(_GRAMMARS_DISAGREE) is False
    assert _floor_exempts(_GRAMMARS_DISAGREE) is True


def test_they_share_a_VOCABULARY_and_NOT_a_VERDICT():
    # ⚠️ The thing this row must not become. The floor exempts this project's attribution
    #    trailer, which is at a REAL domain — so the two are NOT the same predicate, and a
    #    change that made them one would be a widening of the merge path's policy.
    trailer = "noreply@" + "anthropic.com"
    assert _floor_exempts(trailer.partition("@")[2]) is True
    assert reserved.is_reserved("anthropic" + ".com") is False


# --- THE PLANT (Ruling 123): a change to the vocabulary moves BOTH readings ------------------


def test_PLANTING_the_vocabulary_moves_the_FLOOR(monkeypatch):
    # ⛔ THE ROW'S REAL GUARD. A divergence nobody can produce is not a guarded one, so the
    #    vocabulary is MOVED and both readings are watched. ⭐ If either side goes back to a
    #    private copy, its reading stops moving here and this test goes red.
    planted = "host." + _PLANTED

    # ⭐ ROW 1 — the live tree. Neither side calls it reserved.
    assert reserved.is_reserved(planted) is False
    assert _floor_exempts(planted) is False

    # ⛔ ROW 2 — the vocabulary moves, in ONE place, and BOTH readings move with it.
    monkeypatch.setattr(reserved, "RESERVED_TLDS", (*reserved.RESERVED_TLDS, _PLANTED))
    assert reserved.is_reserved(planted) is True
    assert _floor_exempts(planted) is True, "the floor did not move"

    # ⛔ ROW 3 — the negative control. A domain the plant did NOT name is unmoved, or row 2
    #    would be satisfied by a predicate stuck on True.
    unplanted = "host." + "zzz" + "unplanted"
    assert reserved.is_reserved(unplanted) is False
    assert _floor_exempts(unplanted) is False


def test_the_PLANT_is_restored_and_the_shipped_vocabulary_is_unchanged():
    # ⭐ Ruling 202's spirit for an in-process plant: the next reader must not inherit it.
    assert _PLANTED not in reserved.RESERVED_TLDS
    assert _PLANTED not in reserved.RESERVED_DOMAINS


# --- what the shared list does NOT change about either policy --------------------------------


def test_a_BARE_reserved_token_is_unreachable_through_the_floors_own_shape():
    # ⚠️ The one region where the rebuilt exemption is wider than the pattern it replaced:
    #    a bare `@invalid` now matches it, where the old literal required a dot. ⛔ It is
    #    unreachable through `shape_matches`, whose email shape requires a dot in the
    #    domain — so no address the floor can reach changed verdict, and the two sides
    #    agreeing about a bare token is the point rather than a cost.
    for token in reserved.RESERVED_TLDS:
        assert _floor_exempts(token) is True
        assert shape_matches("someone@" + token) == []
