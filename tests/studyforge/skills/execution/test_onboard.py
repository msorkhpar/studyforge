"""Mirror of `src/studyforge/skills/execution/generate.py` (R12) — the acceptance.

⛔ `E11`'s execution-skill acceptance, clause by clause: a runnable corpus gets a
working compose file and a primed image **from manifest data alone**; a corpus
whose manifest says it is not runnable gets **nothing from this skill and no
error**; re-running changes nothing; and §8.1's four rulings are honoured, each
asserted rather than remembered (they are, in `test_rulings.py` and
`test_composefile.py`, and the refusal is asserted to reach this far here).
"""

from __future__ import annotations

import json

import pytest

from studyforge.address import Address
from studyforge.corpus.manifest import parse
from studyforge.execute import container_for, editor_container_for
from studyforge.exercise.bundle import Places
from studyforge.skills.execution import onboard as skill
from tests.studyforge.skills.execution.contracts import (
    WORKSPACE,
    corpus,
    editor_contract,
    editor_text,
    manifest_document,
    narration_text,
)


def manifest(**moved: object):
    """A parsed manifest for the synthetic corpus."""
    return parse(json.dumps(manifest_document(**moved)))


def made(tmp_path, **moved: object):
    """Generate for the synthetic corpus, with `moved` merged into its manifest."""
    return skill.generate(manifest(**moved), editor_text=editor_text(), root=corpus(tmp_path))


# --------------------------------------------------------------------------
# ⛔ A corpus that is not runnable gets nothing, and no error
# --------------------------------------------------------------------------


def test_a_corpus_that_declares_no_runtime_gets_nothing_and_no_error(tmp_path):
    result = made(tmp_path, runtimes=[], exercises=True)
    assert result.runnable is False
    assert result.paths() == () and result.files == () and result.copies == ()
    assert result.selection is None and result.primed is None


def test_a_corpus_with_no_runtime_key_at_all_is_the_same_answer(tmp_path):
    document = manifest_document()
    del document["runtimes"]
    result = skill.generate(
        parse(json.dumps(document)), editor_text=editor_text(), root=corpus(tmp_path)
    )
    assert result.runnable is False and result.paths() == ()


def test_writing_a_corpus_that_is_not_runnable_writes_no_file(tmp_path):
    root = corpus(tmp_path)
    before = sorted(one.relative_to(root).as_posix() for one in root.rglob("*"))
    assert skill.write(made(tmp_path, runtimes=[]), root) == ()
    assert sorted(one.relative_to(root).as_posix() for one in root.rglob("*")) == before


def test_it_never_reads_a_contract_for_a_corpus_that_is_not_runnable(tmp_path):
    # ⛔ Not an optimisation: a book's corpus must not fail because a component
    # it never needed is unpinned, unreadable or at a promise nobody recorded.
    result = skill.generate(
        manifest(runtimes=[]), editor_text="not a contract at all", root=corpus(tmp_path)
    )
    assert result.runnable is False


# --------------------------------------------------------------------------
# ⭐ A runnable corpus, from manifest data alone
# --------------------------------------------------------------------------


def test_a_runnable_corpus_gets_a_compose_file_a_selection_a_prime_and_a_document(tmp_path):
    result = made(tmp_path)
    assert result.runnable is True
    written = result.paths()
    assert skill.COMPOSE_FILE in written
    assert skill.TOOLCHAIN_FILE in written
    assert skill.READER_DOC in written
    assert any(one.startswith(skill.PRIME_DIR) for one in written)


def test_the_declared_set_reaches_the_build_command_and_nothing_else_does(tmp_path):
    result = made(tmp_path, runtimes=["java", "maven"])
    assert result.selection.build[-1] == "java,maven"
    assert result.selection.tag_from[-1] == "--print-tag"


def test_a_runtime_the_image_cannot_carry_is_reported_and_never_dropped(tmp_path):
    result = made(tmp_path, runtimes=["java", "maven", "sqlite"])
    assert [name for name, _ in result.selection.withheld] == ["sqlite"]
    assert result.selection.carried == ("java", "maven")
    document = dict(result.files)[skill.READER_DOC]
    assert "sqlite" in document and "does not carry" in document


def test_the_selection_document_records_no_tag(tmp_path):
    # ⛔ A tag is a function of the build's inputs, so a written one names
    # nothing — and the document says so rather than leaving it to be inferred.
    selection = json.loads(dict(made(tmp_path).files)[skill.TOOLCHAIN_FILE])
    assert "no_tag_is_recorded_here" in selection
    assert selection["declared"] == ["java", "maven"]


def test_the_prime_the_document_names_is_the_prime_that_is_copied(tmp_path):
    result = made(tmp_path)
    assert result.copies == tuple(
        (f"{skill.PRIME_DIR}/{inside}", origin) for inside, origin in result.primed.copies()
    )


def test_the_written_prime_holds_one_project_per_seeded_tool_and_nothing_else(tmp_path):
    # ⛔ `W440`: the component refuses anything at the prime's top but a seeded
    # tool's project, so the top is exactly the seed keys the corpus declares.
    root = corpus(tmp_path)
    skill.write(skill.generate(manifest(), editor_text=editor_text(), root=root), root)
    prime = root / skill.PRIME_DIR
    assert sorted(one.name for one in prime.iterdir()) == ["maven"]
    assert (prime / "maven/pom.xml").is_file()
    assert (prime / "maven/src/main/java/demo/Demo.java").is_file()


def test_the_reader_is_told_the_contracts_own_prime_flag(tmp_path):
    document = dict(made(tmp_path).files)[skill.READER_DOC]
    assert f"--prime <this corpus>/{skill.PRIME_DIR}" in document
    assert "`maven/pom.xml` ← `sources/app/pom.xml`" in document


def test_a_contract_with_no_prime_flag_is_refused_by_the_key_it_lacks(tmp_path):
    runner = {"prime": {"seeds": {"maven": "maven-repo"}}}
    with pytest.raises(skill.contract.ContractRefused) as refused:
        skill.generate(manifest(), editor_text=editor_text(runner=runner), root=corpus(tmp_path))
    assert "runner.prime.declared_by" in str(refused.value)


def test_a_corpus_with_no_seeded_tool_gets_no_prime_and_says_so(tmp_path):
    root = corpus(tmp_path)
    (root / "sources/app/run.py").write_text("def one():\n    return 1\n", encoding="utf-8")
    (root / "sources/app/test_run.py").write_text("def test_one():\n    pass\n", encoding="utf-8")
    result = skill.generate(manifest(runtimes=["python"]), editor_text=editor_text(), root=root)
    assert result.copies == () and result.primed.projects == ()
    document = dict(result.files)[skill.READER_DOC]
    assert "no prime" in document and "--prime" not in document


def test_write_puts_every_path_on_disk_and_the_copies_are_byte_identical(tmp_path):
    root = corpus(tmp_path)
    result = skill.generate(manifest(), editor_text=editor_text(), root=root)
    written = skill.write(result, root)
    assert set(written) == set(result.paths())
    for where, origin in result.copies:
        assert (root / where).read_bytes() == (root / origin).read_bytes()


def test_re_running_it_changes_nothing(tmp_path):
    root = corpus(tmp_path)
    result = skill.generate(manifest(), editor_text=editor_text(), root=root)
    skill.write(result, root)
    before = {
        one.relative_to(root).as_posix(): one.read_bytes()
        for one in sorted(root.rglob("*"))
        if one.is_file()
    }
    skill.write(skill.generate(manifest(), editor_text=editor_text(), root=root), root)
    after = {
        one.relative_to(root).as_posix(): one.read_bytes()
        for one in sorted(root.rglob("*"))
        if one.is_file()
    }
    assert after == before


def test_a_reader_document_somebody_else_wrote_is_refused_rather_than_overwritten(tmp_path):
    root = corpus(tmp_path)
    (root / skill.READER_DOC).write_text("mine, and hand-written\n", encoding="utf-8")
    with pytest.raises(skill.ExecutionRefused, match="did not write"):
        skill.write(skill.generate(manifest(), editor_text=editor_text(), root=root), root)
    assert (root / skill.READER_DOC).read_text(encoding="utf-8") == "mine, and hand-written\n"


def test_a_document_this_skill_wrote_is_regenerated_without_complaint(tmp_path):
    root = corpus(tmp_path)
    result = skill.generate(manifest(), editor_text=editor_text(), root=root)
    skill.write(result, root)
    assert skill.GENERATED in (root / skill.READER_DOC).read_text(encoding="utf-8")
    skill.write(result, root)


# --------------------------------------------------------------------------
# ⛔ Ruling 2 decides which directory is bound, and it is derived
# --------------------------------------------------------------------------


def test_the_bound_directory_is_the_common_root_of_the_declared_material():
    assert skill.source_root(manifest()) == "sources"
    moved = manifest(content={"include": ["a/b/*.md", "a/b/c/*.md"], "exclude": []})
    assert skill.source_root(moved) == "a/b"


def test_an_include_naming_one_file_still_says_where_the_material_lives():
    one = manifest(content={"include": ["docs/intro.md"], "exclude": []})
    assert skill.source_root(one) == "docs"


def test_material_at_the_repository_root_is_refused_by_ruling_2():
    # ⛔ There is then no directory to bind that is not the repository, and
    # §8.1 ruling 2 mounts only the sources. Reported, never defaulted.
    with pytest.raises(skill.ExecutionRefused, match="ruling 2"):
        skill.source_root(manifest(content={"include": ["*.md"], "exclude": []}))


def test_globs_that_share_no_directory_are_refused_rather_than_widened():
    with pytest.raises(skill.ExecutionRefused, match="ruling 2"):
        skill.source_root(manifest(content={"include": ["a/*.md", "b/*.md"], "exclude": []}))


def test_the_compose_file_reaches_the_sources_from_where_it_sits(tmp_path):
    # ⚠️ Compose resolves a relative bind against the compose file's own
    # directory, so the rendered path climbs out of the generated directory.
    text = dict(made(tmp_path).files)[skill.COMPOSE_FILE]
    assert "../../sources:" in text


# --------------------------------------------------------------------------
# The rulings reach this far, and the manifest declares what this skill writes
# --------------------------------------------------------------------------


def test_a_contract_that_breaks_a_ruling_refuses_the_whole_generation(tmp_path):
    broken = json.loads(editor_text())
    broken["editor"]["ports"][0]["host_bind"] = "0.0.0.0"
    with pytest.raises(Exception, match="ruling 1"):
        skill.generate(manifest(), editor_text=json.dumps(broken), root=corpus(tmp_path))


def test_the_narration_contract_is_checked_and_its_service_is_not_rendered(tmp_path):
    result = skill.generate(
        manifest(),
        editor_text=editor_text(),
        root=corpus(tmp_path),
        narration_text=narration_text(),
    )
    text = dict(result.files)[skill.COMPOSE_FILE]
    assert "narrate" not in text
    document = dict(result.files)[skill.READER_DOC]
    assert "narrate-service" in document and "compose.yaml" in document


def test_every_path_this_skill_writes_is_classified_by_a_glob_it_declares(tmp_path):
    # ⛔ A path added without a glob fails HERE rather than reporting
    # `unclassified` in somebody's repository (R19, and onboarding's own guard).
    unclassified = [one for one in made(tmp_path).paths() if not skill.classified(one)]
    assert unclassified == []


def test_every_glob_it_declares_carries_a_reason_the_manifest_would_accept():
    from studyforge.corpus.manifest import parse_content

    policy = parse_content(
        {
            "include": ["sources/**"],
            "exclude": [],
            "not_material": list(skill.NOT_MATERIAL),
        }
    )
    assert len(policy.not_material) == len(skill.NOT_MATERIAL)


def test_a_path_no_glob_covers_is_reported_rather_than_passed():
    # ⭐ The other direction: the classifier is not vacuous.
    assert not skill.classified("sources/app/Demo.java")


# --------------------------------------------------------------------------
# ⛔ One command brings up an editor that sees every practice, and the runner
# --------------------------------------------------------------------------


def compose(tmp_path, **moved: object) -> str:
    return dict(made(tmp_path, **moved).files)[skill.COMPOSE_FILE]


def test_the_editor_binds_the_practice_workspaces_beside_the_sources(tmp_path):
    # ⭐ Read from where `emit` places a workspace, never a second spelling of it.
    places = Places(Address(("demo",)), "java", unit=1, ordinal=1)
    top = places.workspace.split("/")[0]
    text = compose(tmp_path)
    assert "../../sources:" in text and f'"../../{top}:{WORKSPACE}/{top}"' in text
    assert skill.workspaces_bind(editor_block(), "sources") == (top, f"{WORKSPACE}/{top}")


def test_sources_that_already_hold_the_practice_workspaces_get_no_second_bind():
    assert skill.workspaces_bind(editor_block(), "practice") is None


def test_a_contract_already_mounting_where_the_workspaces_go_is_refused():
    block = editor_block()
    block["mounts"][0]["container_path"] = f"{WORKSPACE}/practice"
    with pytest.raises(skill.ExecutionRefused, match="shadow"):
        skill.workspaces_bind(block, "sources")


def test_the_runner_comes_up_with_the_editor_under_the_names_execute_looks_for(tmp_path):
    made_ = made(tmp_path)
    text = dict(made_.files)[skill.COMPOSE_FILE]
    assert "\n  runner:\n" in text
    assert f"container_name: {container_for('demo')}" in text
    assert made_.runner is not None and made_.runner.name == container_for("demo")
    # ⭐ The editor's name is compose's own: `<project>-<service>-1`.
    assert "name: studyforge-demo\n" in text and "\n  editor:\n" in text
    assert editor_container_for("demo") == "studyforge-demo-editor-1"
    assert '"../..:/work"' in text


def test_the_compose_file_names_no_tag_and_the_env_file_is_the_skills_own(tmp_path):
    text = compose(tmp_path)
    assert "${STUDYFORGE_RUNNER_IMAGE:?" in text and "example/runner:" not in text
    assert skill.classified(skill.RUNNER_ENV)


def editor_block() -> dict:
    return editor_contract()["editor"]
