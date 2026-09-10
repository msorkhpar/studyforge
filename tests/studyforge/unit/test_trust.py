"""Mirror of `src/studyforge/unit/trust.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.unit import (
    DEFAULT_TRUST,
    PROVENANCE,
    TRUST,
    ContentError,
    check_test_record,
)


def test_a_generated_grader_can_never_be_recorded_as_authoritative():
    # ⛔ SF-09's acceptance, and R5's whole point: presenting a check written
    # here as the source's grader is a claim nobody notices is false until a
    # reader trusts a green tick that was never earned.
    with pytest.raises(ContentError, match="may not be marked authoritative"):
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
    assert check_test_record("user") == ("user", "advisory")
    with pytest.raises(ContentError):
        check_test_record("generated", "authoritative")


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
