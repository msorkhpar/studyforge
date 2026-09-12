"""Mirror of `src/studyforge/skills/onboarding/artifacts.py` (R12).

⭐ **The test that matters most here asserts coverage, not a list.** A seventh
artifact added without a `content.not_material` glob is an `unclassified`
finding in somebody else's repository, discovered by them; this asks the same
question here, of every path the module says it writes.
"""

from __future__ import annotations

import ast

from studyforge.corpus.manifest import MIN_WHY_CHARS, Classification, parse
from studyforge.skills.onboarding import artifacts
from studyforge.skills.onboarding.manifest import promote, render
from tests.studyforge.skills.onboarding import corpora

EDIT = {
    "path": "pom.xml",
    "kind": "insert-line",
    "anchor": "</modules>",
    "content": "<module>study</module>",
    "why": "the build file the toolchain image needs one module added to",
}


def _manifest(**changes):
    return parse(render(promote(corpora.draft(**changes), not_material=artifacts.NOT_MATERIAL)))


def test_every_path_this_skill_writes_is_classified_by_a_glob_it_declares():
    # ⛔ Coverage, over the paths themselves. The manifest is the only thing
    # that can answer `validate`'s unclassified check, and a path this module
    # writes without a glob is a finding it created for its consumer.
    unclassified = [
        where
        for where in artifacts.paths()
        if where != artifacts.MANIFEST and not artifacts.classified(where)
    ]
    assert not unclassified, f"these have no not_material glob: {unclassified}"


def test_the_globs_are_answered_by_the_manifest_itself_and_not_only_by_this_module():
    # ⭐ The behavioural half: `classified` is this module's own opinion, and
    # `ContentPolicy.classify` is what the corpus will actually be judged by.
    manifest = _manifest()

    for where in artifacts.paths():
        if where == artifacts.MANIFEST:
            continue
        assert manifest.content.classify(where) is Classification.NOT_MATERIAL, where


def test_the_manifest_is_not_declared_not_material_by_the_document_it_is():
    assert not artifacts.classified(artifacts.MANIFEST)


def test_this_skill_never_writes_a_repository_root_ignore_file():
    # ⛔ R3, and W15's measured breach: tooling appended to a source
    # repository's root ignore file on an ordinary commit, unrequested.
    roots = [where for where in artifacts.paths() if where in (".gitignore", ".gitattributes")]
    assert not roots, f"this skill writes a repository-root ignore file: {roots}"


def test_no_ignore_rule_this_skill_writes_reaches_the_archive():
    # ⛔ SF-32's verdict: generated media is committed by default, so an ignore
    # rule that swept it out would flip a corpus's policy without anybody
    # declaring it. ⭐ This skill now writes no ignore rule at all, at any
    # depth — the assertion is over every path it occupies, not one name.
    rules = [where for where in artifacts.paths() if where.rsplit("/", 1)[-1] == ".gitignore"]
    assert not rules, f"this skill writes an ignore rule: {rules}"


def test_the_generated_non_destructive_check_bakes_in_this_corpus_declared_edits():
    text = artifacts.edits_test(_manifest(permitted_edits=[EDIT]))

    assert "'pom.xml'" in text
    ast.parse(text)


def test_a_corpus_that_declares_no_edit_gets_a_check_that_permits_none():
    text = artifacts.edits_test(_manifest())

    assert "PERMITTED = []" in text


def test_the_generated_checks_are_modules_that_parse():
    for text in (artifacts.edits_test(_manifest()),):
        ast.parse(text)


def test_the_reader_document_is_written_from_the_declarations_rather_than_invented():
    text = artifacts.reader_document(_manifest(), ("ingest/read.py",))

    assert "A Walkthrough Corpus" in text
    assert "course" in text
    assert "ingest/read.py" in text
    assert "not known yet" in text, "a unit count at onboarding time would be invented"


def test_a_corpus_with_no_graders_is_told_it_is_complete_rather_than_short():
    # ⛔ §7's three states, C5: a corpus with no graders is complete at the
    # reading floor. Telling its reader otherwise is the failure C5 describes.
    text = artifacts.reader_document(_manifest(exercises=False))

    assert "complete product" in text
    assert "waiting on one" in text


def test_a_corpus_with_graders_is_told_about_the_execution_track():
    assert "Run and Submit" in artifacts.reader_document(_manifest(exercises=True))


def test_the_reader_is_told_the_two_ways_forward_before_the_media_stops_fitting():
    # ⭐ And never that the policy was flipped for them.
    text = artifacts.reader_document(_manifest())

    assert "will not pick one for you" in text
    assert "change to `corpus.json`" in text


def test_the_declared_edits_are_quoted_to_the_reader_with_their_reasons():
    text = artifacts.reader_document(_manifest(permitted_edits=[EDIT]))

    assert "pom.xml" in text
    assert EDIT["why"] in text


def test_every_reason_clears_the_minimum_the_manifest_enforces():
    # ⚠️ A reason the document refuses is a reason the integrator has to
    # invent, which is the retyping R19 forbids. ⛔ The minimum is imported
    # from the module that owns it, never re-typed as a number here.
    for entry in artifacts.NOT_MATERIAL:
        assert len(entry["why"].strip()) >= MIN_WHY_CHARS, entry["glob"]
