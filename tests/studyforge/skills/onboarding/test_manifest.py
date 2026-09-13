"""Mirror of `src/studyforge/skills/onboarding/manifest.py` (R12).

⭐ **The two properties worth failing a build over are both about what is *not*
emitted:** a key nobody needs, and a version nobody needed. Both freeze
something on every corpus that comes after, silently, from the one place nobody
re-reads.
"""

from __future__ import annotations

import json

import pytest

from studyforge.corpus.manifest import (
    CORPUS_API,
    MANIFEST_KEYS,
    MIN_WHY_CHARS,
    ManifestError,
    parse,
)
from studyforge.skills.onboarding.manifest import (
    NOT_MATERIAL_API,
    PromotionRefused,
    promote,
    render,
)
from tests.studyforge.skills.onboarding import corpora

WHY = "kept for the archive of the previous edition and never shown to a reader"
GLOB = {"glob": "ingest/**", "why": "the adapter this corpus is built with, not material"}

#: A declared edit, with every field `permitted_edits` requires. ⚠️ The shape
#: is the manifest's, not this skill's — an edit is a path, a kind, an anchor,
#: the line added and the reason.
EDIT = {
    "path": "pom.xml",
    "kind": "insert-line",
    "anchor": "</modules>",
    "content": "<module>study</module>",
    "why": "the build file the toolchain image needs one module added to",
}


def test_a_draft_becomes_a_manifest_the_framework_reads_back():
    manifest = parse(render(promote(corpora.DRAFT)))

    assert manifest.source == "walkthrough"
    assert manifest.depth == 1


def test_every_emitted_key_is_one_the_contract_carries():
    # ⛔ The subset half. A promoter that emitted a key the manifest does not
    # know would produce a corpus that refuses to parse, in the integrator's
    # repository rather than here.
    document = promote(corpora.DRAFT, not_material=[GLOB])

    assert set(document) <= set(MANIFEST_KEYS)


def test_the_keys_are_written_in_the_order_the_contract_declares_them():
    document = promote(corpora.DRAFT, not_material=[GLOB])

    order = [key for key in MANIFEST_KEYS if key in document]
    assert list(document) == order


def test_no_media_block_is_invented():
    # ⛔ An absent `media` key is a *stated* default (SF-02), and a generator
    # that wrote one out would freeze the footprint limits' names on every
    # corpus — R9 makes a rename a migration from the first declaration.
    assert "media" not in promote(corpora.DRAFT)


def test_a_media_block_a_person_declared_is_not_discarded():
    # ⭐ The rule is that this generator adds nothing, not that it overrules
    # somebody's declaration — customisation enters as manifest data.
    assert promote(corpora.draft(media={"commit": "always"}))["media"] == {"commit": "always"}


def test_an_empty_permitted_edits_is_dropped_rather_than_written():
    assert "permitted_edits" not in promote(corpora.draft(permitted_edits=[]))


def test_a_declared_edit_survives_promotion():
    edit = EDIT
    document = promote(corpora.draft(permitted_edits=[edit]))

    assert document["permitted_edits"] == [edit]


def test_the_version_rises_only_when_the_data_needs_it():
    # ⭐ Both halves in one test, because the pair is the rule: `not_material`
    # needs 2, and a corpus without it stays at what the draft asked for.
    assert promote(corpora.DRAFT)["corpus_api"] == 1
    assert promote(corpora.DRAFT, not_material=[GLOB])["corpus_api"] == NOT_MATERIAL_API


def test_the_version_never_falls_below_what_the_draft_asked_for():
    assert promote(corpora.draft(corpus_api=2))["corpus_api"] == 2


def test_not_material_is_unreadable_one_version_below_the_one_promote_writes():
    # ⛔ The behavioural pin for `NOT_MATERIAL_API`, which is re-derived here
    # because the owner's key-to-version map is not on its `__all__`
    # (Ruling 101). ⚠️ A literal compared against the same literal would agree
    # with itself; this asks the manifest package what it actually accepts.
    document = promote(corpora.DRAFT, not_material=[GLOB])
    lowered = {**document, "corpus_api": NOT_MATERIAL_API - 1}

    with pytest.raises(ManifestError):
        parse(render(lowered))
    assert parse(render(document)).corpus_api == NOT_MATERIAL_API


def test_an_unknown_version_is_refused_by_name_and_never_migrated():
    with pytest.raises(PromotionRefused) as refused:
        promote(corpora.draft(corpus_api=CORPUS_API + 99))

    assert str(CORPUS_API + 99) in str(refused.value)


def test_an_excluded_path_without_a_reason_is_refused_and_they_are_named_at_once():
    drafted = corpora.draft(content={"include": ["src/*.md"], "exclude": ["old/a.md", "old/b.md"]})

    with pytest.raises(PromotionRefused) as refused:
        promote(drafted)

    message = str(refused.value)
    assert "old/a.md" in message and "old/b.md" in message, "one refusal names every path"


def test_a_reason_shorter_than_the_manifest_accepts_is_refused_here_rather_than_there():
    drafted = corpora.draft(content={"include": ["src/*.md"], "exclude": ["old/a.md"]})

    with pytest.raises(PromotionRefused):
        promote(drafted, reasons={"old/a.md": "n/a"})
    assert len(WHY) >= MIN_WHY_CHARS
    promote(drafted, reasons={"old/a.md": WHY})


def test_a_reason_a_person_gave_lands_beside_the_path_it_is_about():
    drafted = corpora.draft(content={"include": ["src/*.md"], "exclude": ["old/a.md"]})

    document = promote(drafted, reasons={"old/a.md": WHY})

    assert document["content"]["exclude"] == [{"path": "old/a.md", "why": WHY}]


def test_no_reason_is_invented():
    # ⭐ A NEGATIVE control for the refusal above: the module has no default
    # reason anywhere, so the refusal cannot be bypassed by omission.
    drafted = corpora.draft(content={"include": ["src/*.md"], "exclude": ["old/a.md"]})

    with pytest.raises(PromotionRefused):
        promote(drafted, reasons={})


def _with_notes(*entries) -> dict:
    return corpora.draft(content={**corpora.DRAFT["content"], "not_material": list(entries)})


def test_a_not_material_block_a_person_declared_survives_merged_with_the_generated_globs():
    # ⛔ INT06-1: the block was silently dropped, so a corpus's own declarations
    # could not be generated. ⭐ The person's entries first, as written, then the
    # generated ones in their sorted order.
    other = {"glob": "tests/*.py", "why": "the generated checks this corpus carries"}

    document = promote(_with_notes(corpora.NOTES), not_material=[other, GLOB])

    assert document["content"]["not_material"] == [corpora.NOTES, GLOB, other]
    assert document["corpus_api"] == NOT_MATERIAL_API
    assert parse(render(document)).content.not_material[0].glob == corpora.NOTES["glob"]


def test_a_persons_block_alone_is_carried_and_raises_the_version_it_needs():
    # ⚠️ `onboard`'s provisional pass promotes with no generated globs at all.
    document = promote(_with_notes(corpora.NOTES))

    assert document["content"]["not_material"] == [corpora.NOTES]
    assert document["corpus_api"] == NOT_MATERIAL_API


def test_a_reason_the_survey_left_open_is_paired_from_the_reasons_a_person_gave():
    # ⭐ W249: reconnaissance drafts the glob with `why: None`; the reason is a
    # person's (W240/3), handed over keyed by the glob. A written reason is kept.
    opened = {"glob": "LICENSE", "why": None}
    document = promote(_with_notes(corpora.NOTES, opened), reasons={"LICENSE": WHY})

    assert document["content"]["not_material"] == [corpora.NOTES, {"glob": "LICENSE", "why": WHY}]
    assert parse(render(document)).content.why_not_material("LICENSE") == WHY


def test_every_open_reason_is_named_at_once_and_none_is_invented():
    opened = [{"glob": "LICENSE", "why": None}, {"glob": "notes/**", "why": None}]
    with pytest.raises(PromotionRefused) as refused:
        promote(_with_notes(*opened), reasons={"LICENSE": "too short"})
    assert "2 not_material glob(s) have no reason: ['LICENSE', 'notes/**']" in str(refused.value)


def test_without_a_drafted_block_the_content_is_exactly_what_it_was():
    # ⭐ The unplanted control: no drafted block, and an empty one, both emit
    # the generated globs alone and stay at the draft's version without them.
    for drafted in (corpora.DRAFT, _with_notes()):
        assert promote(drafted)["content"] == {"include": ["src/*.md", "README.md"]}
        assert promote(drafted)["corpus_api"] == 1
        assert promote(drafted, not_material=[GLOB])["content"] == {
            "include": ["src/*.md", "README.md"],
            "not_material": [GLOB],
        }


def test_a_glob_the_draft_and_a_generator_both_declare_is_refused_naming_both_sides():
    # ⛔ Never resolved by precedence: neither reason is kept over the other,
    # because the manifest itself refuses a repeated glob as two audits.
    mine = {"glob": GLOB["glob"], "why": "a person's reason for the same directory"}

    with pytest.raises(PromotionRefused) as refused:
        promote(_with_notes(corpora.NOTES, mine), not_material=[GLOB])

    message = str(refused.value)
    assert "content.not_material[1]" in message, "the draft's side is not named"
    assert "generated" in message, "the generated side is not named"
    assert GLOB["glob"] in message
    assert corpora.NOTES["glob"] not in message, "a glob that does not collide was named"


def test_a_collision_is_refused_even_when_both_sides_give_the_same_reason():
    # ⚠️ Ruled (INT06-1): a person retyping a generated declaration is R19's
    # retyping, and the manifest refuses the repeat whatever the reasons say.
    with pytest.raises(PromotionRefused):
        promote(_with_notes(GLOB), not_material=[GLOB])


def test_every_collision_is_named_at_once():
    second = {"glob": "tests/*.py", "why": "the generated checks this corpus carries"}

    with pytest.raises(PromotionRefused) as refused:
        promote(_with_notes(GLOB, second), not_material=[GLOB, second])

    message = str(refused.value)
    assert "content.not_material[0]" in message and "content.not_material[1]" in message


def test_two_generators_declaring_one_glob_are_refused_naming_both_sides():
    # ⛔ INT06-1/4 (W242): keeping the first generator's reason was precedence
    # between generators, which W239 refused between a draft and a generator.
    other = {"glob": "tests/*.py", "why": "the generated checks this corpus carries"}
    again = {**GLOB, "why": "a second generator's reason for the same directory"}

    with pytest.raises(PromotionRefused) as refused:
        promote(corpora.DRAFT, not_material={"the scaffold": [GLOB], "the skill": [other, again]})

    message = str(refused.value)
    assert "the scaffold[0]" in message and "the skill[1]" in message
    assert "precedence" in message


def test_a_collision_between_generators_is_refused_even_with_the_same_reason():
    with pytest.raises(PromotionRefused):
        promote(corpora.DRAFT, not_material={"one": [GLOB], "two": [GLOB]})


def test_one_sequence_declaring_a_glob_twice_is_refused_naming_both_positions():
    with pytest.raises(PromotionRefused) as refused:
        promote(corpora.DRAFT, not_material=[GLOB, GLOB])

    message = str(refused.value)
    assert "not_material[0]" in message and "not_material[1]" in message


def test_distinct_globs_from_several_generators_merge_in_sorted_order():
    other = {"glob": "tests/*.py", "why": "the generated checks this corpus carries"}

    document = promote(corpora.DRAFT, not_material={"b": [other], "a": [GLOB]})

    assert document["content"]["not_material"] == [GLOB, other]


def test_a_drafted_block_that_is_not_a_list_is_refused():
    with pytest.raises(PromotionRefused):
        promote(corpora.draft(content={"include": ["src/*.md"], "not_material": "notes/**"}))


def test_a_key_no_manifest_carries_is_refused_by_name():
    with pytest.raises(PromotionRefused) as refused:
        promote({**corpora.DRAFT, "toolchain": "java"})

    assert "toolchain" in str(refused.value)


def test_a_required_field_left_open_is_refused_and_they_are_named_at_once():
    drafted = {key: value for key, value in corpora.DRAFT.items() if key not in ("levels", "title")}

    with pytest.raises(PromotionRefused) as refused:
        promote(drafted)

    message = str(refused.value)
    assert "levels" in message and "title" in message


def test_a_draft_that_is_not_a_dict_is_refused_rather_than_coerced():
    with pytest.raises(PromotionRefused):
        promote(["corpus_api", 1])


def test_a_promoted_manifest_that_would_not_parse_is_refused_rather_than_written():
    with pytest.raises(PromotionRefused):
        promote(corpora.draft(placement="somewhere-else"))


def test_render_is_json_a_person_can_read_and_a_diff_can_hold_still():
    text = render(promote(corpora.DRAFT, not_material=[GLOB]))

    assert text.endswith("\n")
    assert json.loads(text)["corpus_api"] == NOT_MATERIAL_API
    assert render(json.loads(text)) == text, "a second render must not reformat the first"


def test_a_promoted_manifest_carrying_a_home_path_is_refused_as_itself():
    # ⛔ Ruling 58: `_refuse_unreadable` catches the reader's `RAISES` but
    # re-raises the leak rather than filing it as a promotion refusal.
    from studyforge.archive.scrub import PersonalDataLeak

    with pytest.raises(PersonalDataLeak):
        promote(corpora.draft(title="notes from " + "/" + "home/jane/x"))
