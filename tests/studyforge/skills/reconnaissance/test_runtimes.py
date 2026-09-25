"""Mirror of `src/studyforge/skills/reconnaissance/runtimes.py` (R12).

⭐ Every clause is asserted both ways, over fabricated corpora of
each shape: a corpus whose material evidences runtimes drafts them, and prose
drafts no key. ⛔ The vocabulary is the manifest's and is imported, never retyped.
"""

from __future__ import annotations

import json

import pytest

from studyforge.corpus.manifest import KEY_VERSIONS, RUNTIMES, ManifestError, parse
from studyforge.skills.onboarding import promote, render
from studyforge.skills.reconnaissance import assess, draft, find, survey, take
from studyforge.skills.reconnaissance.runtimes import (
    BUILD_EVIDENCE,
    RUNTIMES_API,
    SOURCE_EVIDENCE,
    propose,
)
from tests.studyforge.skills.reconnaissance import sources


def drafted(root):
    """The draft manifest and its questions, the way `survey` makes them."""
    inventory = take(root)
    return draft(inventory, find(inventory), assess(inventory))


def corpus(root, extra):
    """A two-unit prose corpus with a record, plus `extra` — the material's code."""
    files = {f"src/{n}.md": sources.unit(f"Chapter {n}") for n in (1, 2)}
    files["README.md"] = "# Coded\n\n" + "\n".join(
        f"- [{n}. Chapter {n}](src/{n}.md)" for n in (1, 2)
    )
    return sources.write(root, {**files, **extra})


PYTHON = {"pyproject.toml": "[project]\n", "code/a.py": "A = 1\n", "tests/test_a.py": "pass\n"}
#: A graded Maven build: its sources, and a test that is a grader.
JAVA_GRADED = {
    "pom.xml": "<project/>\n",
    "src/main/java/A.java": "class A {}\n",
    "src/test/java/ATest.java": "class ATest {}\n",
}
KOTLIN = {
    "build.gradle.kts": "\n",
    "src/main/kotlin/A.kt": "class A\n",
    "src/test/kotlin/ATest.kt": "class ATest\n",
}


def asked_about_runtimes(questions):
    return [q for q in questions if "runtime" in q.question]


# --------------------------------------------------------------------------
# ⭐ clause 1: evidenced material drafts `runtimes`; prose drafts no key
# --------------------------------------------------------------------------


def test_a_graded_corpus_with_a_maven_build_drafts_java_and_maven(tmp_path):
    manifest, _ = drafted(sources.runnable(tmp_path / "c"))
    assert manifest["runtimes"] == ["java", "maven"]


def test_a_prose_corpus_drafts_no_runtimes_key_and_asks_nothing_about_one(tmp_path):
    manifest, asked = drafted(sources.flat_prose(tmp_path / "c"))
    assert "runtimes" not in manifest
    assert asked_about_runtimes(asked) == []


def test_a_graded_python_corpus_drafts_python_and_nothing_it_does_not_evidence(tmp_path):
    manifest, _ = drafted(corpus(tmp_path / "c", PYTHON))
    assert manifest["runtimes"] == ["python"]


def test_kotlin_source_drafts_a_jvm_beside_it_from_the_owner_rule(tmp_path):
    # ⛔ `REQUIRES_JAVA` refuses `kotlin` or `gradle` alone; the draft reads back.
    manifest, _ = drafted(corpus(tmp_path / "c", KOTLIN))
    assert manifest["runtimes"] == ["gradle", "java", "kotlin"]
    assert parse(json.dumps(sources.settled(manifest))).runtimes == ("gradle", "java", "kotlin")


def test_sql_names_a_language_not_an_engine_so_no_sqlite_is_drafted(tmp_path):
    # ⛔ Never a runtime nothing evidences: SQL does not say which engine runs it.
    manifest, _ = drafted(corpus(tmp_path / "c", {**PYTHON, "code/q.sql": "SELECT 1;\n"}))
    assert manifest["runtimes"] == ["python"]
    manifest, _ = drafted(corpus(tmp_path / "d", {**PYTHON, "code/q.sqlite": "\x00"}))
    assert manifest["runtimes"] == ["python", "sqlite"]


def test_the_drafted_runtimes_are_asked_about_with_their_evidence(tmp_path):
    _, asked = drafted(sources.runnable(tmp_path / "c"))
    [question] = asked_about_runtimes(asked)
    assert "['java', 'maven']" in question.question
    assert "pom.xml" in question.why and "ThingTest.java" in question.why


# --------------------------------------------------------------------------
# ⛔ only beside `exercises: true`, and evidence there is never dropped silently
# --------------------------------------------------------------------------


def test_evidence_with_no_grader_drafts_no_key_and_says_why(tmp_path):
    java = {"pom.xml": "<project/>\n", "src/main/java/A.java": "class A{}\n"}
    root = corpus(tmp_path / "c", java)
    manifest, asked = drafted(root)
    assert manifest["exercises"] is False
    assert "runtimes" not in manifest
    [question] = asked_about_runtimes(asked)
    assert "no grader" in question.question and "maven" in question.why


def test_graders_with_a_build_no_runtime_names_draft_no_key_and_ask_which(tmp_path):
    # ⭐ The closed map's cost is one question, naming the build it could not map.
    root = corpus(tmp_path / "c", {"Cargo.toml": "\n", "tests/a_test.rs": "\n"})
    manifest, asked = drafted(root)
    assert manifest["exercises"] is True and "runtimes" not in manifest
    [question] = asked_about_runtimes(asked)
    assert question.question.startswith("which runtimes") and "Cargo.toml" in question.why


# --------------------------------------------------------------------------
# ⛔ the framework's own generated half evidences nothing
# --------------------------------------------------------------------------

#: What onboarding generates: Python, into a corpus whose own material is Java.
SCAFFOLD = {"tests/test_non_destructive.py": "pass\n", "ingest/read.py": "pass\n"}


def test_generated_python_the_record_names_is_not_evidence(tmp_path):
    root = sources.onboarded(sources.runnable(tmp_path / "c"), SCAFFOLD)
    assert drafted(root)[0]["runtimes"] == ["java", "maven"]
    assert propose(assess(take(root))).set_aside == {}


def test_the_same_files_unrecorded_ARE_read_so_the_clause_above_measures_something(
    tmp_path,
):
    # ⭐ Unrecorded, they are the corpus's own Python under its Maven build: read,
    # and set aside by name because the build holding them builds no Python.
    root = sources.write(sources.runnable(tmp_path / "c"), SCAFFOLD)
    assert drafted(root)[0]["runtimes"] == ["java", "maven"]
    assert sorted(propose(assess(take(root))).set_aside["python"]) == sorted(SCAFFOLD)


# --------------------------------------------------------------------------
# ⛔ a source file a build holds evidences only what that build builds
# --------------------------------------------------------------------------


def test_a_python_file_under_a_maven_build_is_set_aside_and_named(tmp_path):
    notes = {"docs/notes/reader.py": "pass\n", "scripts/check.sh": "true\n"}
    root = corpus(tmp_path / "c", {**JAVA_GRADED, **notes})
    manifest, asked = drafted(root)

    assert manifest["runtimes"] == ["java", "maven", "shell"]
    [question] = asked_about_runtimes(asked)
    assert "set aside" in question.why and "docs/notes/reader.py" in question.why


def test_a_python_file_no_build_holds_is_still_evidence(tmp_path):
    root = corpus(tmp_path / "c", {"code/a.py": "A = 1\n", "tests/test_a.py": "pass\n"})
    assert drafted(root)[0]["runtimes"] == ["python"]


def test_a_python_file_under_its_own_build_inside_a_maven_repository_is_evidence(tmp_path):
    tools = {"tools/pyproject.toml": "[project]\n", "tools/run.py": "pass\n"}
    root = corpus(tmp_path / "c", {**JAVA_GRADED, **tools})
    assert drafted(root)[0]["runtimes"] == ["java", "maven", "python"]


# --------------------------------------------------------------------------
# ⭐ the draft reads back: `corpus_api` 4, through the manifest reader and `promote`
# --------------------------------------------------------------------------


def test_a_draft_carrying_runtimes_declares_the_version_that_reads_it(tmp_path):
    manifest, _ = drafted(sources.runnable(tmp_path / "c"))
    # ⭐ At least the runtimes' version, and exactly what the drafted keys need:
    # a draft with a record also carries `curriculum`.
    assert manifest["corpus_api"] == max(RUNTIMES_API, _curriculum_api(manifest))
    assert parse(json.dumps(sources.settled(manifest))).runtimes == ("java", "maven")


def test_the_version_is_pinned_by_the_reader_refusing_one_lower(tmp_path):
    # ⛔ Behavioural, never a literal: one version lower, the reader refuses the key.
    manifest, _ = drafted(sources.runnable(tmp_path / "c"))
    older = {**sources.settled(manifest), "corpus_api": RUNTIMES_API - 1}
    with pytest.raises(ManifestError, match="runtimes"):
        parse(json.dumps(older))


def test_a_draft_with_no_runtimes_does_not_raise_its_version_for_them(tmp_path):
    manifest, _ = drafted(corpus(tmp_path / "c", {"pom.xml": "<project/>\n"}))
    assert "runtimes" not in manifest
    # ⛔ Nothing the runtimes need: whatever it declares, another key asked for.
    declared = manifest["corpus_api"]
    assert declared < RUNTIMES_API or declared == _curriculum_api(manifest)


def _curriculum_api(manifest: dict) -> int:
    """The version the drafted `curriculum` block needs, or `1` when there is none."""
    return KEY_VERSIONS[(None, "curriculum")] if "curriculum" in manifest else 1


def test_promote_reads_the_drafted_runtimes_back(tmp_path):
    # ⭐ Promote only raises `corpus_api` for `not_material`, so the draft
    # must ask for the version itself — and it does, so onboarding keeps the key.
    proposal = survey(sources.runnable(tmp_path / "c")).proposal
    document = promote(proposal, reasons=sources.reasons(proposal))
    assert document["runtimes"] == ["java", "maven"]
    assert parse(render(document)).runtimes == ("java", "maven")


# --------------------------------------------------------------------------
# ⛔ the vocabulary is the owner's
# --------------------------------------------------------------------------


def test_every_name_either_map_evidences_is_in_the_owner_vocabulary():
    maps = (*BUILD_EVIDENCE.values(), *SOURCE_EVIDENCE.values())
    evidenced = {name for names in maps for name in names}
    assert evidenced <= set(RUNTIMES)


def test_propose_on_no_files_evidences_nothing(tmp_path):
    found = propose(assess(take(sources.flat_prose(tmp_path / "c"))))
    assert found.evidence == {} and found.names == () and found.api == 1
