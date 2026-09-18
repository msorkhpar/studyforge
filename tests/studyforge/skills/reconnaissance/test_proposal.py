"""The draft manifest, and every field it had to choose (SK-01)."""

from __future__ import annotations

import json

from studyforge.address import slugify as sf01_slugify
from studyforge.corpus.manifest import Classification, parse
from studyforge.skills.reconnaissance import assess, draft, find, survey, take
from studyforge.skills.reconnaissance.proposal import slugify
from tests.studyforge.skills.reconnaissance import sources
from tests.support import git, run

#: Shapes whose draft excludes nothing, so the whole draft goes to SF-02 as it
#: stands. ⚠️ A draft's `exclude` is bare paths awaiting a person's reasons,
#: which SK-07's `promote` pairs; that half is not this file's.
EXCLUDES_NOTHING = (
    sources.flat_prose,
    sources.prefixed_groups,
    sources.nested_sections,
    sources.marker_ordinals,
    sources.record_beside_units,
)


def propose(root):
    inventory = take(root)
    return draft(inventory, find(inventory), assess(inventory))


def accepted(proposal):
    """Parse the draft, its reasons given as a person would, with SF-02's own reader.

    ⛔ Its rules are never restated here, and the reasons are the test's (W240/3).
    """
    return parse(json.dumps(sources.settled(proposal)))


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


def test_one_variant_is_proposed_and_still_asked_about(tmp_path):
    # ⚠️ Three of the four designed shapes have one variant. Proposing two
    # would be fitting the exception, and proposing none is refused by SF-02.
    manifest, asked = propose(sources.flat_prose(tmp_path / "c"))
    assert len(manifest["variants"]) == 1
    assert any("one variant" in q.question for q in asked)


def test_the_one_variant_is_the_framework_word_prose(tmp_path):
    # ⛔ Spec §4 (`Q9`): a single-variant prose corpus declares `["prose"]`, the
    # framework's word. ⚠️ Typed here and not read from `SINGLE_VARIANT`, so a
    # rename of the constant is refused rather than followed.
    manifest, _ = propose(sources.flat_prose(tmp_path / "c"))
    assert manifest["variants"] == ["prose"]


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


# --------------------------------------------------------------------------
# ⛔ W240: the draft of `survey('.')` is one SF-02 accepts
# --------------------------------------------------------------------------


def test_a_corpus_surveyed_as_dot_drafts_a_manifest_sf02_accepts(tmp_path, monkeypatch):
    # ⛔ `survey('.')` is the documented call. Its unresolved name is empty,
    # and `variants: []` is refused, so every draft was unpromotable by hand.
    for build in EXCLUDES_NOTHING:
        # ⚠️ Named unlike any fixture's title, so the two sources cannot agree by chance.
        root = build(tmp_path / f"checkout-{build.__name__}")
        monkeypatch.chdir(root)
        manifest = accepted(survey(".").proposal)
        assert manifest.source == sf01_slugify(find(take(root)).title), build.__name__
        assert manifest.source != sf01_slugify(root.name), build.__name__


def test_a_directory_name_with_no_slug_still_drafts_an_accepted_source(tmp_path, monkeypatch):
    root = sources.flat_prose(tmp_path / "\u65e5\u672c")
    monkeypatch.chdir(root)
    accepted(survey(".").proposal)


def test_a_corpus_with_no_record_surveyed_as_dot_drafts_an_accepted_title(tmp_path, monkeypatch):
    # ⚠️ With no record the title falls back to the directory's name, which
    # is the same empty name `source` had.
    root = sources.flat_prose(tmp_path / "c")
    (root / "README.md").unlink()
    monkeypatch.chdir(root)
    accepted(survey(".").proposal)


def test_the_source_slug_is_asked_about(tmp_path):
    manifest, asked = propose(sources.flat_prose(tmp_path / "c"))
    assert any(repr(manifest["source"]) in q.question for q in asked)


def test_no_include_glob_matches_the_curriculum_record(tmp_path):
    # ⛔ A record beside a unit it lists was caught by that unit's wildcard
    # and read as a unit. SF-02's classifier judges; every listed unit stays in.
    for build in EXCLUDES_NOTHING:
        root = build(tmp_path / build.__name__)
        manifest, _ = propose(root)
        content = accepted(manifest).content
        record = find(take(root))
        # ⭐ W249: and it is proposed `not_material`, so it is no longer unclassified.
        assert content.classify(record.path.as_posix()) is Classification.NOT_MATERIAL, (
            build.__name__
        )
        assert all(content.classify(t) is Classification.INCLUDED for t in record.order)


def test_a_record_no_wildcard_catches_keeps_directory_globs(tmp_path):
    # ⭐ The fix lists files only where a wildcard would catch the record.
    manifest, _ = propose(sources.flat_prose(tmp_path / "c"))
    assert manifest["content"]["include"] == ["src/*.md"]
    beside, _ = propose(sources.record_beside_units(tmp_path / "b"))
    assert beside["content"]["include"] == ["chapters/*.md", "intro.md"]


def test_a_corpus_with_no_curriculum_record_keeps_its_draft(tmp_path):
    root = sources.flat_prose(tmp_path / "c")
    (root / "README.md").unlink()
    manifest, _ = propose(root)
    assert manifest["content"] == {"include": ["src/*.md"], "exclude": []}


# --------------------------------------------------------------------------
# ⛔ W249: `source` does not depend on the name of the directory surveyed
# --------------------------------------------------------------------------


def _git(where, *arguments):
    """Run git with a placeholder identity. ⛔ Relative paths only (R7)."""
    identity = ["-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid"]
    result = run([git(), *identity, "-c", "commit.gpgsign=false", *arguments], cwd=where)
    assert result.returncode == 0, result.stderr


def test_two_differently_named_checkouts_of_one_repository_draft_one_proposal(
    tmp_path, monkeypatch
):
    # ⛔ INT-07/1: a worktree named `int` drafted `int`, and a clone named after
    # the repository drafted the repository's name. One corpus, one `source`.
    origin = sources.furnished(tmp_path / "origin")
    _git(origin, "init", "-q")
    _git(origin, "add", "-A")
    _git(origin, "commit", "-q", "-m", "fixture")
    _git(tmp_path, "clone", "-q", "--no-hardlinks", "origin", "a-clone-named-like-a-repository")
    _git(origin, "worktree", "add", "-q", "--detach", "../int")
    clone, worktree = tmp_path / "a-clone-named-like-a-repository", tmp_path / "int"

    drafted = [survey(clone).proposal, survey(worktree).proposal]
    monkeypatch.chdir(worktree)
    drafted.append(survey(".").proposal)

    assert drafted[0] == drafted[1] == drafted[2]
    assert drafted[0]["source"] == sf01_slugify(find(take(clone)).title) == "aggregated"
    globs = [entry["glob"] for entry in drafted[0]["content"]["not_material"]]
    assert globs == sources.FURNISHED_GLOBS
    assert accepted(drafted[0]).source == "aggregated"


def test_with_no_record_the_source_is_a_placeholder_whatever_the_directory(tmp_path):
    names = ("int", "a-clone-named-like-a-repository")
    drafted = []
    for name in names:
        root = sources.flat_prose(tmp_path / name)
        (root / "README.md").unlink()
        drafted.append(propose(root)[0]["source"])
    assert drafted == ["corpus", "corpus"]
