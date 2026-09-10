"""Mirror of `src/studyforge/skills/adapter/plan.py` (R12)."""

from __future__ import annotations

import json

import pytest

from studyforge.corpus.manifest import parse
from studyforge.skills.adapter import PACKAGE, Plan, PlanError, plan_for
from tests.studyforge.skills.adapter import corpora


def manifest(**changes):
    """Parse the walkthrough manifest with `changes` applied."""
    document = json.loads(json.dumps(corpora.MANIFEST))
    document.update(changes)
    return parse(json.dumps(document))


def test_every_field_came_from_the_manifest():
    # ⛔ R19: customisation enters as manifest data. A field that could arrive
    # any other way is a source-specific fact that never appears in corpus.json.
    plan = plan_for(manifest())
    assert plan.source == "walkthrough"
    assert plan.levels == ("course",)
    assert plan.variants == ("prose",)
    assert plan.exercises is False


def test_depth_is_the_manifests_own_arity():
    assert plan_for(manifest(levels=["section", "module"])).depth == 2


def test_a_corpus_with_no_exercises_gets_no_practice_path():
    # ⭐ §7's three states, C5: "no graders" is an answer, not a gap. A path
    # that is never taken reads as unfinished work for the corpus's whole life.
    assert plan_for(manifest(exercises=False)).kinds == ("lesson",)
    assert plan_for(manifest(exercises=True)).kinds == ("lesson", "practice")


def test_a_sole_variant_is_named_and_two_are_not():
    # ⚠️ A container carries one variant (SF-05), so a corpus declaring two
    # chooses per container — and a scaffold that picked the first would be
    # silently right for one corpus in two.
    assert plan_for(manifest()).sole_variant == "prose"
    assert plan_for(manifest(variants=["prose", "code"])).sole_variant is None


def test_the_default_package_is_the_frameworks_decision_and_is_fixed():
    # ⭐ R20: a reviewer who has seen one adapter knows where the next one's
    # reading step lives, so this is not a per-corpus choice.
    assert plan_for(manifest()).package == PACKAGE


def test_a_package_name_that_is_not_an_identifier_is_refused():
    # ⛔ Stated as what is permitted: a generated `import` has to satisfy two
    # grammars at once, and a separator blacklist would admit every keyword.
    for bad in ("in-gest", "class", "match", "", "2ingest"):
        with pytest.raises(PlanError):
            plan_for(manifest(), package=bad)


def test_an_unparsed_manifest_is_refused_rather_than_read_as_a_mapping():
    with pytest.raises(PlanError):
        plan_for(dict(corpora.MANIFEST))


def test_the_plan_reads_back_before_anything_is_written():
    lines = plan_for(manifest()).lines()
    assert any("walkthrough" in line for line in lines)
    assert any("adapter package" in line for line in lines)


def test_a_plan_is_immutable_once_built():
    plan = plan_for(manifest())
    with pytest.raises((AttributeError, TypeError)):
        plan.source = "somewhere-else"  # type: ignore[misc]
    assert isinstance(plan, Plan)
