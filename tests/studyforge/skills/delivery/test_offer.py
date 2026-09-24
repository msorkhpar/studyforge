"""Mirror of `src/studyforge/skills/delivery/offer.py` (R12).

⭐ The offer is read from the installed command table and skill tree, so these
tests read both registries and compare, and plant a wrong offer to see each
refusal fire.
"""

from __future__ import annotations

import io

import pytest

from studyforge.cli.dispatch import VERBS
from studyforge.exitcodes import UNUSABLE
from studyforge.skills import documents
from studyforge.skills.delivery import offer
from studyforge.skills.delivery.offer import Capability, Offer, OfferRefused


def test_the_installed_offer_is_every_command_then_every_skill_but_the_planner():
    ids = [capability.id for capability in Offer.installed().capabilities]
    commands = [f"studyforge {name}" for name in VERBS]
    skills = [f"skill {name}" for name in documents.names() if name != offer.PLANNER]
    assert ids == commands + skills


def test_the_planner_is_this_package():
    assert offer.PLANNER == "delivery"


def test_a_command_is_described_by_its_own_summary():
    described = {capability.id: capability.what for capability in Offer.installed().capabilities}
    for name, verb in VERBS.items():
        assert described[f"studyforge {name}"] == verb.summary


def test_a_skill_is_described_by_its_documents_title():
    described = {capability.id: capability.what for capability in Offer.installed().capabilities}
    assert described["skill reconnaissance"] == "source reconnaissance"


def test_a_skill_document_with_no_title_line_is_described_by_its_name():
    assert offer._title("A document with no heading.\n", "example") == "example"


def test_the_rendered_offer_carries_one_row_per_capability_and_no_roadmap():
    installed = Offer.installed()
    rendered = installed.render()
    rows = [line for line in rendered.splitlines() if line.startswith("| `")]
    assert len(rows) == len(installed.capabilities)
    assert offer.BANNER in rendered
    assert "finding" in rendered
    for word in ("milestone", "epic", "lands at", "roadmap"):
        assert word not in rendered.lower(), word


def test_an_empty_offer_is_refused():
    with pytest.raises(OfferRefused, match="offer of nothing"):
        Offer(())


def test_every_id_offered_twice_is_named_at_once():
    twice = (
        Capability("tool a", "does one thing"),
        Capability("tool a", "does it again"),
        Capability("tool b", "does another"),
        Capability("tool b", "and again"),
    )
    with pytest.raises(OfferRefused) as refused:
        Offer(twice)
    assert str(refused.value).startswith("2 refusals")


def test_a_capability_with_no_id_or_no_description_is_refused():
    with pytest.raises(OfferRefused, match="needs an id"):
        Capability("  ", "does a thing")
    with pytest.raises(OfferRefused, match="needs an id"):
        Capability("tool a", "")


def test_main_prints_the_offer(monkeypatch):
    out = io.StringIO()
    monkeypatch.setattr("sys.stdout", out)
    assert offer.main([]) == 0
    assert out.getvalue() == Offer.installed().render()


def test_main_refuses_an_argument(monkeypatch):
    err = io.StringIO()
    monkeypatch.setattr("sys.stderr", err)
    assert offer.main(["anything"]) == UNUSABLE
    assert offer.USAGE in err.getvalue()
