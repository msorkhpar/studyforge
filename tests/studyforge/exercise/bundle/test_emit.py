"""The emission an adapter calls, and the workspace it creates."""

from __future__ import annotations

import pytest

from studyforge.archive.blocks import STARTING_CODE_HEADING, STATEMENT_HEADING, read_layout
from studyforge.archive.document import parse, render
from studyforge.exercise import ExerciseError
from studyforge.exercise import of as exercise_of
from studyforge.exercise.bundle import REFERENCE_SUMMARY, bundle_of, emit, emit_page, write
from tests.studyforge.exercise.bundle import bundles


def a_bundle(root, **overrides):
    """One bundle on disk, and the `Bundle` that reads it."""
    bundles.write_bundle(root, **overrides)
    return bundle_of(bundles.document(**overrides), "bundle.json")


def an_emission(root, **overrides):
    return emit(root, a_bundle(root, **overrides), source="demo", ingested="2026-01-05")


def test_a_bundle_emits_a_practice_document_the_archive_reads(tmp_path):
    emission = an_emission(tmp_path)
    document = emission.document
    assert document["kind"] == "practice"
    assert document["ordinal"] == 1
    # ⭐ The round trip through the archive's own reader is the assertion that
    # this is a valid `practice-M.json` and not merely a dict that looks like one.
    assert parse(render(document), "practice-1.json") == document
    assert read_layout(document, "practice-1.json") is not None


def test_the_record_names_the_readers_own_files_and_not_the_bundles(tmp_path):
    emission = an_emission(tmp_path)
    exercise = exercise_of(emission.document, "practice-1.json")
    assert exercise.main_path == "practice/demo/prose/unit-02/practice-1/bitmap.py"
    assert exercise.test_path == "practice/demo/prose/unit-02/practice-1/test_bitmap.py"
    assert "exercises/" not in exercise.main_path
    assert exercise.report.path == "practice/demo/prose/unit-02/practice-1/target/report.xml"


def test_the_record_carries_the_cases_and_the_origin_it_was_built_from(tmp_path):
    exercise = exercise_of(an_emission(tmp_path).document, "practice-1.json")
    assert [case.id for case in exercise.cases] == ["test_builds", "test_empty"]
    assert exercise.origin.path == "src/one.md"
    assert exercise.breaks_down


def test_the_statement_and_the_starting_code_come_out_of_the_bundle(tmp_path):
    document = an_emission(tmp_path).document
    assert document["starting_code"] == bundles.STARTER
    headings = [b["text"] for b in document["blocks"] if b["type"] == "heading"]
    assert headings[0] == STATEMENT_HEADING and headings[-1] == STARTING_CODE_HEADING
    assert any(b["type"] == "list" for b in document["blocks"])


def test_the_reference_solution_ships_withheld_but_present(tmp_path):
    # ⭐ The user's ruling: always available, never revealed automatically, and
    # never gated on a pass. The archive's own *present but withheld* state.
    document = an_emission(tmp_path).document
    disclosures = [b for b in document["blocks"] if b["type"] == "disclosure"]
    assert len(disclosures) == 1
    assert disclosures[0]["open"] is False
    assert disclosures[0]["summary"] == REFERENCE_SUMMARY
    assert disclosures[0]["blocks"][0]["text"] == bundles.REFERENCE


def test_r5s_forbidden_pair_is_refused_by_the_module_that_owns_it(tmp_path):
    # ⛔ Not re-spelled here: `unit.trust` refuses it through `record`.
    with pytest.raises(Exception) as raised:
        an_emission(tmp_path, trust="authoritative")
    assert "authoritative" in str(raised.value)


def test_a_command_reaching_outside_the_workspace_is_refused(tmp_path):
    with pytest.raises(ExerciseError, match="outside the exercise's own workspace"):
        an_emission(tmp_path, test_command=["python3", "-m", "pytest", "practice/other"])


def test_a_missing_bundle_file_is_named_and_never_guessed(tmp_path):
    bundle = a_bundle(tmp_path)
    (tmp_path / bundle.places.bundle / "reference" / bundle.main_file).unlink()
    with pytest.raises(ExerciseError, match="reference/bitmap.py"):
        emit(tmp_path, bundle, source="demo", ingested="2026-01-05")


def test_an_edge_case_with_no_planted_solution_is_refused(tmp_path):
    bundle = a_bundle(tmp_path)
    (tmp_path / bundle.places.bundle / "plants" / "edge-1" / bundle.main_file).unlink()
    with pytest.raises(ExerciseError, match="planted to fail edge case 1"):
        emit(tmp_path, bundle, source="demo", ingested="2026-01-05")


def test_an_emission_writes_nothing_until_it_is_asked(tmp_path):
    emission = an_emission(tmp_path)
    assert not (tmp_path / emission.paths[0]).exists()
    assert write(tmp_path, emission, "emission") == emission.paths
    assert (tmp_path / emission.paths[0]).read_text(encoding="utf-8") == bundles.STARTER
    assert (tmp_path / emission.paths[1]).read_text(encoding="utf-8") == bundles.TESTS


def test_an_emission_writes_no_existing_file(tmp_path):
    # ⛔ R3, observed: the file is really there, with content of its own, and
    # it is still there unchanged after the refusal.
    emission = an_emission(tmp_path)
    target = tmp_path / emission.paths[0]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("the reader's own work\n", encoding="utf-8")
    assert target.read_text(encoding="utf-8") == "the reader's own work\n"
    with pytest.raises(ExerciseError, match="non-destructive"):
        write(tmp_path, emission, "emission")
    assert target.read_text(encoding="utf-8") == "the reader's own work\n"
    assert not (tmp_path / emission.paths[1]).exists()


def test_the_readers_file_starts_as_the_starter_and_never_as_the_reference(tmp_path):
    emission = an_emission(tmp_path)
    write(tmp_path, emission, "emission")
    assert (tmp_path / emission.paths[0]).read_text(encoding="utf-8") != bundles.REFERENCE


def test_several_exercises_on_one_page_take_the_ordinals_one_to_n(tmp_path):
    first = a_bundle(tmp_path)
    second = a_bundle(tmp_path, ordinal=2)
    emissions = emit_page(tmp_path, (second, first), source="demo", ingested="2026-01-05")
    assert [one.document["ordinal"] for one in emissions] == [1, 2]
    # ⛔ Two exercises on one page never share a workspace file.
    assert set(emissions[0].paths).isdisjoint(emissions[1].paths)


def test_a_page_whose_ordinals_have_a_gap_is_refused_before_anything_is_emitted(tmp_path):
    first = a_bundle(tmp_path)
    third = a_bundle(tmp_path, ordinal=3)
    with pytest.raises(ExerciseError, match="no gap and no repeat"):
        emit_page(tmp_path, (first, third), source="demo", ingested="2026-01-05")


def test_bundles_from_two_pages_are_refused_rather_than_numbered_together(tmp_path):
    first = a_bundle(tmp_path)
    other = a_bundle(tmp_path, unit=3, ordinal=2)
    with pytest.raises(ExerciseError, match="one page's exercises at a time"):
        emit_page(tmp_path, (first, other), source="demo", ingested="2026-01-05")


def test_a_statement_the_archive_cannot_carry_is_a_named_failure(tmp_path):
    bundle = a_bundle(tmp_path)
    (tmp_path / bundle.places.statement).write_text("```py\nnever closed\n", encoding="utf-8")
    with pytest.raises(ExerciseError, match="not Markdown"):
        emit(tmp_path, bundle, source="demo", ingested="2026-01-05")


def test_a_bundle_file_that_is_not_utf8_is_a_named_failure(tmp_path):
    bundle = a_bundle(tmp_path)
    (tmp_path / bundle.places.statement).write_bytes(b"\xff\xfe not text")
    with pytest.raises(ExerciseError, match="statement.md"):
        emit(tmp_path, bundle, source="demo", ingested="2026-01-05")


def test_the_lesson_section_carries_what_the_adapter_hands_it(tmp_path):
    bundle = a_bundle(tmp_path)
    emission = emit(
        tmp_path,
        bundle,
        source="demo",
        ingested="2026-01-05",
        lesson=({"type": "para", "text": "How bitmaps work."},),
        lesson_title="Bitmaps",
    )
    layout = read_layout(emission.document, "practice-1.json")
    assert layout.lesson_title == "Bitmaps"
    assert layout.lesson[0]["text"] == "How bitmaps work."
    assert layout.starting_code == bundles.STARTER


def test_the_same_emission_serves_a_second_source_with_no_framework_change(tmp_path):
    # ⛔ R1: every source-specific fact is data. Nothing about this bundle is
    # the first one's, and the framework took no edit to emit it.
    elsewhere_root = "practice/other-corpus/chapter-1/java/unit-07/practice-1"
    elsewhere = dict(
        address=["other-corpus", "chapter-1"],
        variant="java",
        unit=7,
        lang="java",
        main_file="src/Parser.java",
        test_file="src/ParserTest.java",
        run_command=["java", f"{elsewhere_root}/src/Parser.java"],
        test_command=["java", f"{elsewhere_root}/src/ParserTest.java"],
    )
    bundle = a_bundle(tmp_path, **elsewhere)
    emission = emit(tmp_path, bundle, source="other", ingested="2026-02-02")
    assert emission.paths[0] == f"{elsewhere_root}/src/Parser.java"
    assert parse(render(emission.document), "practice-1.json")["source"] == "other"
    assert write(tmp_path, emission, "emission") == emission.paths


# ⭐ The build role reaches the reader's workspace, byte for byte.


def test_a_declared_build_file_is_laid_into_the_workspace_beside_the_readers_files(tmp_path):
    emission = an_emission(tmp_path, build=["pom.xml", "config/deps.toml"])
    workspace = "practice/demo/prose/unit-02/practice-1"
    assert emission.paths[2:] == (f"{workspace}/pom.xml", f"{workspace}/config/deps.toml")
    write(tmp_path, emission, "emission")
    for path in emission.paths[2:]:
        assert (tmp_path / path).read_text(encoding="utf-8") == bundles.BUILD_TEXT


def test_an_exercise_with_no_build_role_emits_only_the_readers_two_files(tmp_path):
    # ⭐ The M7 shape, unchanged: nothing is added where nothing was declared.
    assert len(an_emission(tmp_path).paths) == 2


def test_a_build_file_is_copied_as_bytes_and_never_interpreted(tmp_path):
    bundle = a_bundle(tmp_path, build=["lib.bin"])
    raw = bytes(range(256))
    (tmp_path / bundle.places.bundle / "build" / "lib.bin").write_bytes(raw)
    emission = emit(tmp_path, bundle, source="demo", ingested="2026-01-05")
    assert dict(emission.files)[bundle.places.in_workspace("lib.bin")] == raw


def test_a_declared_build_file_the_bundle_does_not_hold_is_named(tmp_path):
    bundle = a_bundle(tmp_path, build=["pom.xml"])
    (tmp_path / bundle.places.bundle / "build" / "pom.xml").unlink()
    with pytest.raises(ExerciseError, match="build/pom.xml"):
        emit(tmp_path, bundle, source="demo", ingested="2026-01-05")


def test_a_command_may_name_the_build_file_it_laid_into_the_workspace(tmp_path):
    # ⭐ The whole reach of the channel: a workspace-relative argument, which
    # `emit` already permits, and no absolute path anywhere (`safety`).
    workspace = "practice/demo/prose/unit-02/practice-1"
    command = ["mvn", "-o", "-q", "-f", f"{workspace}/pom.xml", "test"]
    document = an_emission(tmp_path, build=["pom.xml"], test_command=command).document
    assert exercise_of(document, "practice-1.json").test_command == tuple(command)
