"""The draft manifest, and every field it had to choose (SK-01)."""

from __future__ import annotations

from studyforge.skills.reconnaissance import assess, draft, find, take
from studyforge.skills.reconnaissance.proposal import slugify
from tests.studyforge.skills.reconnaissance import sources


def propose(root):
    inventory = take(root)
    return draft(inventory, find(inventory), assess(inventory))


# --------------------------------------------------------------------------
# ⛔ depth comes from ordinals, not from the presence of groups
# --------------------------------------------------------------------------


def test_a_flat_corpus_with_no_grouping_is_one_level(tmp_path):
    manifest, _ = propose(sources.flat_prose(tmp_path / "c"))
    assert manifest["levels"] == ["course"]


def test_a_corpus_with_three_groups_is_still_ONE_container_level(tmp_path):
    # ⛔ **A grouping is not automatically a second level**, and getting this
    # wrong costs an entire ingestion. Measured: ISO's ordinals restart per
    # group, so the group *is* the container level.
    manifest, _ = propose(sources.prefixed_groups(tmp_path / "c"))
    assert manifest["levels"] == ["group"]


def test_a_corpus_whose_ordinals_nest_is_two_levels(tmp_path):
    # ⭐ Java's shape: `1.1.` and `1.1.1.`, so modules sit inside sections.
    manifest, _ = propose(sources.nested_sections(tmp_path / "c"))
    assert manifest["levels"] == ["section", "module"]


def test_the_level_names_are_always_asked_about(tmp_path):
    # ⛔ §4 rules the vocabulary is the corpus's own; this skill cannot know it.
    _, asked = propose(sources.nested_sections(tmp_path / "c"))
    assert any("right names for the levels" in q.question for q in asked)


# --------------------------------------------------------------------------
# the rest of the draft
# --------------------------------------------------------------------------


def test_the_title_comes_from_the_record_rather_than_a_filename(tmp_path):
    # ⚠️ `README` is not what anybody calls their course.
    manifest, _ = propose(sources.flat_prose(tmp_path / "c"))
    assert manifest["title"] == "A Prose Course"


def test_variants_are_empty_until_something_says_otherwise(tmp_path):
    # ⚠️ Three of the four designed shapes have one variant. Proposing two
    # would be fitting the exception.
    manifest, asked = propose(sources.flat_prose(tmp_path / "c"))
    assert manifest["variants"] == []
    assert any("one variant" in q.question for q in asked)


def test_exercises_follows_what_ships_with_the_material(tmp_path):
    assert propose(sources.flat_prose(tmp_path / "c"))[0]["exercises"] is False
    assert propose(sources.runnable(tmp_path / "c"))[0]["exercises"] is True


def test_material_the_record_does_not_name_is_proposed_for_exclusion(tmp_path):
    manifest, _ = propose(sources.aggregated(tmp_path / "c"))
    assert "src/Whole.md" in manifest["content"]["exclude"]


def test_the_placement_choice_is_always_explained(tmp_path):
    _, asked = propose(sources.flat_prose(tmp_path / "c"))
    assert any("right placement" in q.question for q in asked)


# --------------------------------------------------------------------------
# ⚠️ the collision class, with the ruling's example corrected
# --------------------------------------------------------------------------


def test_accents_do_not_collide_and_the_ruling_saying_they_do_is_wrong():
    # ⛔ Measured. An accent is a non-alphanumeric, so it collapses to a
    # *separator* — `caf` and `cafe`, which are two names.
    assert slugify("Café") == "caf"
    assert slugify("Cafe") == "cafe"
    assert slugify("Café") != slugify("Cafe")


def test_punctuation_is_the_class_that_actually_occurs():
    # ⭐ A skill built for the accent case would miss the case that happens.
    assert slugify("Streams: an API") == slugify("Streams, an API") == "streams-an-api"


def test_titles_that_would_become_one_address_are_reported(tmp_path):
    # ⚠️ Measured at 15 of 38 units in one corpus, because two of its series
    # deliberately mirror each other. It is the **good** material that does this.
    root = sources.prefixed_groups(tmp_path / "c")
    readme = root / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8")
        .replace("Server chapter 1]", "Basic Setup]")
        .replace("Client chapter 1]", "Basic Setup]"),
        encoding="utf-8",
    )
    _, asked = propose(root)
    assert any("would produce one address" in q.question for q in asked)


def test_more_ordinal_levels_than_this_skill_can_name_is_asked_about(tmp_path):
    # ⛔ Said out loud rather than truncated to the two names it has. A
    # proposal that quietly drops a level is exactly the confident wrong answer
    # about a hierarchy that costs an entire ingestion.
    _, asked = propose(sources.over_deep_ordinals(tmp_path / "c"))
    assert any("container levels" in question.question for question in asked)
