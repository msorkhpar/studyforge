"""Mirror of `src/studyforge/skills/delivery/finding.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.skills.delivery import MARKERS, NEGATIVE_OPENING, Claim, Finding, FindingRefused


def claim(**overrides: object) -> Claim:
    fields: dict[str, object] = {"says": "the CLI holds one command", "measured": "counted here"}
    fields.update(overrides)
    return Claim(**fields)  # type: ignore[arg-type]


def finding(**overrides: object) -> Finding:
    fields: dict[str, object] = {
        "id": "SV-08/1",
        "marker": "structural",
        "says": "the planner cannot express a gate on a shared component",
        "claims": (claim(),),
    }
    fields.update(overrides)
    return Finding(**fields)  # type: ignore[arg-type]


def test_the_marker_vocabulary_is_closed_at_three():
    assert set(MARKERS) == {"local", "structural", "none"}


def test_every_marker_in_the_vocabulary_is_accepted():
    # ⭐ Coverage over the closed set: a marker declared and unusable is a
    # vocabulary entry nobody can reach.
    for marker in MARKERS:
        claims = () if marker == "none" else (claim(),)
        assert Finding(id="SV-08/1", marker=marker, says="x" * 20, claims=claims).marker == marker


def test_a_fourth_marker_is_refused_and_the_refusal_names_the_three():
    # ⚠️ `negative` was written in three documents by two roles before anybody
    # checked whether it counted. It does not join them.
    with pytest.raises(FindingRefused, match="closed at local, structural, none"):
        finding(marker="negative")


def test_a_recorded_negative_is_local_and_says_so_in_its_first_words():
    # ⭐ A marker encodes ROUTING, and a recorded negative routes where a
    # `local` routes: nowhere. Polarity is content.
    recorded = finding(marker="local", says=f"{NEGATIVE_OPENING} the predicted breach is absent")
    assert recorded.is_negative
    assert not recorded.obliges_a_ruling


def test_a_structural_finding_obliges_somebody_to_rule():
    assert finding().obliges_a_ruling


def test_a_none_marker_beside_a_real_claim_is_refused():
    # ⛔ It is the ONLY way to write zero, so it may not stand beside a finding.
    with pytest.raises(FindingRefused, match="beside a real claim"):
        finding(marker="none")


def test_a_none_marker_alone_is_the_way_to_write_zero():
    assert Finding(id="SV-08/1", marker="none", says="nothing outside scope", claims=()).marker


def test_a_finding_with_a_marker_and_no_claims_states_nothing_checkable():
    with pytest.raises(FindingRefused, match="no claims"):
        finding(claims=())


def test_a_finding_numbered_globally_is_refused():
    # ⛔ The form is <TASK-ID>/<n>: a finding is numbered inside its own
    # document, never globally.
    with pytest.raises(FindingRefused, match="not a finding id"):
        finding(id="44")


def test_a_claim_that_is_neither_measured_nor_received_is_refused():
    with pytest.raises(FindingRefused, match="This one says neither"):
        Claim("the CLI holds one command")


def test_a_claim_that_is_both_measured_and_received_is_refused():
    # ⚠️ A finding is usually both; the UNIT is the claim, so one claim is one
    # provenance.
    with pytest.raises(FindingRefused, match="This one says both"):
        Claim("the CLI holds one command", measured="counted", received="the board")


def test_a_measured_and_a_received_claim_render_differently():
    assert claim().line().startswith("  - *measured:*")
    assert Claim("a check is open", received="the plan").line().startswith("  - *received:*")


def test_a_claim_with_no_text_claims_nothing():
    with pytest.raises(FindingRefused, match="claims nothing"):
        Claim("  ", measured="counted")


def test_the_rendered_finding_carries_its_marker_in_brackets():
    assert "`[structural]`" in finding().lines()[0]
