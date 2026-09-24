"""Mirror of `src/studyforge/unit/trust.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.unit import (
    DEFAULT_TRUST,
    MAY_BE_AUTHORITATIVE,
    PROVENANCE,
    TRUST,
    ContentError,
    check_test_record,
)


def test_a_generated_grader_can_never_be_recorded_as_authoritative():
    # ⛔ The unit content's acceptance, and R5's whole point: presenting a check written
    # here as the source's grader is a claim nobody notices is false until a
    # reader trusts a green tick that was never earned.
    with pytest.raises(ContentError, match="may be marked authoritative"):
        check_test_record("generated", "authoritative")


def test_the_refusal_says_why_rather_than_only_that():
    with pytest.raises(ContentError) as raised:
        check_test_record("generated", "authoritative")
    assert "the source's grader" in str(raised.value)


@pytest.mark.parametrize("provenance", PROVENANCE)
def test_every_provenance_has_a_default_trust(provenance):
    # ⚠️ Defaulted rather than required: the default is right in every case,
    # and a field an author must fill in to say the obvious is a field an
    # author fills in wrongly.
    assert check_test_record(provenance) == (provenance, DEFAULT_TRUST[provenance])


def test_only_material_that_came_with_the_source_defaults_to_authoritative():
    assert DEFAULT_TRUST["bundled"] == "authoritative"
    assert DEFAULT_TRUST["generated"] == "advisory"
    assert DEFAULT_TRUST["user"] == "advisory"


@pytest.mark.parametrize("trust", TRUST)
def test_a_bundled_test_may_be_recorded_either_way(trust):
    # ⭐ A source that ships real tests is a different situation from one whose
    # grader is hidden; both are expressible.
    assert check_test_record("bundled", trust) == ("bundled", trust)


def test_a_user_written_test_may_be_advisory_and_not_authoritative():
    # ⛔ **Named for `user`, and it asserts `user`**: a test named for one
    # provenance and asserting another leaves `user` + `authoritative`
    # refused by nobody and asserted by nobody.
    assert check_test_record("user") == ("user", "advisory")
    with pytest.raises(ContentError):
        check_test_record("user", "authoritative")


@pytest.mark.parametrize("provenance", ["", None, "Bundled", "upstream", 1, True])
def test_an_unknown_provenance_is_refused_naming_the_ones_there_are(provenance):
    with pytest.raises(ContentError) as raised:
        check_test_record(provenance)
    for name in PROVENANCE:
        assert name in str(raised.value)


@pytest.mark.parametrize("trust", ["", "trusted", "Authoritative", 1])
def test_an_unknown_trust_is_refused(trust):
    with pytest.raises(ContentError, match="trust must be one of"):
        check_test_record("bundled", trust)


def test_the_vocabulary_is_exactly_what_sf23_will_consume():
    assert PROVENANCE == ("bundled", "generated", "user")
    assert TRUST == ("authoritative", "advisory")


# --------------------------------------------------------------------------
# ⛔ `authoritative` ⟹ `bundled`, stated positively
# --------------------------------------------------------------------------


@pytest.mark.parametrize("provenance", PROVENANCE)
def test_only_a_provenance_in_the_legal_set_may_claim_authoritative(provenance):
    # ⭐ **The expectation is derived from the rule, not restated beside it.**
    # A second hand-kept list of what may be authoritative would be the same
    # open set this ruling deleted, one directory further away.
    if provenance in MAY_BE_AUTHORITATIVE:
        assert check_test_record(provenance, "authoritative") == (provenance, "authoritative")
    else:
        with pytest.raises(ContentError, match="may be marked authoritative"):
            check_test_record(provenance, "authoritative")


def test_a_provenance_nobody_has_decided_about_is_non_authoritative_automatically(monkeypatch):
    # ⛔ **This is the whole difference between the two spellings of the rule,
    # and it is the test the forbidden-pair list could not pass.** A fourth
    # provenance arriving with no row written for it was *accepted* as
    # authoritative under a list of forbidden pairs, silently. Under the legal
    # set it is refused on the day it is added, and somebody has to decide.
    monkeypatch.setattr("studyforge.unit.trust.PROVENANCE", (*PROVENANCE, "imported"))
    monkeypatch.setitem(DEFAULT_TRUST, "imported", "advisory")
    assert check_test_record("imported") == ("imported", "advisory")
    with pytest.raises(ContentError, match="may be marked authoritative"):
        check_test_record("imported", "authoritative")


def test_the_legal_set_is_a_subset_of_the_vocabulary_it_draws_from():
    # ⚠️ A closed set that names something the vocabulary does not have is a
    # rule about nothing, and it would pass every test above.
    assert set(MAY_BE_AUTHORITATIVE) <= set(PROVENANCE)
    assert MAY_BE_AUTHORITATIVE == ("bundled",)


@pytest.mark.parametrize("provenance", PROVENANCE)
def test_no_default_trust_is_a_pair_the_rule_would_refuse(provenance):
    # ⭐ The cross-check that catches the *other* way this fails open: a rule
    # nothing violates because the defaults quietly stopped agreeing with it.
    assert check_test_record(provenance) == (provenance, DEFAULT_TRUST[provenance])
