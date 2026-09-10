"""Mirror of `src/studyforge/skills/adapter/scaffold.py` (R12)."""

from __future__ import annotations

import compileall
import json

import pytest

from studyforge.corpus.manifest import MIN_WHY_CHARS, Classification, parse
from studyforge.skills.adapter import (
    PARTS,
    SOURCE_LINE_CEILING,
    Scaffold,
    ScaffoldRefused,
    plan_for,
    scaffold,
)
from tests.studyforge.skills.adapter import corpora
from tools.quality.config import SOURCE_LINE_CEILING as OWNED_CEILING


def made():
    """A scaffold for the walkthrough corpus."""
    return scaffold(plan_for(parse(json.dumps(corpora.MANIFEST))))


def test_the_ceiling_is_the_one_the_quality_floor_owns():
    # ⛔ The pin for the copy in `scaffold.py`. `tools/` is developer tooling
    # and shipped code may not import it, so the number is duplicated — and a
    # duplicate nobody compares is how two rules become two different rules.
    assert SOURCE_LINE_CEILING == OWNED_CEILING


def test_every_generated_file_is_under_r11s_ceiling():
    # ⭐ SK-02's acceptance clause, as a measurement rather than an assertion.
    assert made().oversized() == ()


def test_exactly_one_file_is_a_persons_to_write():
    # ⛔ R19 is unusable unless a reader can tell which files it covers.
    scaffolded = made()
    assert len(scaffolded.hand_written) == 1
    assert scaffolded.hand_written[0].endswith("/read.py")


def test_every_part_names_a_step_and_every_step_produces_a_part():
    # ⭐ A part with no step is a file the procedure never mentions; a step
    # with no part is a step that produces nothing.
    steps = {part.step for part in PARTS}
    assert steps == set(range(min(steps), max(steps) + 1)) - {2}, steps
    assert all(part.why.strip() for part in PARTS)


def test_the_scaffold_compiles_as_python(tmp_path):
    made().write(tmp_path)
    assert compileall.compile_dir(str(tmp_path), quiet=1), "a generated module is not valid Python"


def test_it_refuses_rather_than_overwriting_and_names_everything_in_the_way(tmp_path):
    # ⛔ Every collision, never the first: an integrator told about one file at
    # a time has been given a guessing game (R6's argument).
    scaffolded = made()
    scaffolded.write(tmp_path)
    with pytest.raises(ScaffoldRefused) as refused:
        scaffolded.write(tmp_path)
    message = str(refused.value)
    for where in scaffolded.paths:
        assert where in message, f"{where} was in the way and was not named"


def test_regenerate_rewrites_the_generated_files_and_still_refuses_the_written_one(tmp_path):
    scaffolded = made()
    scaffolded.write(tmp_path)
    hand = tmp_path / scaffolded.hand_written[0]
    hand.write_text(corpora.READ, encoding="utf-8")
    generated = tmp_path / "ingest/emit.py"
    generated.write_text("# edited by hand\n", encoding="utf-8")

    with pytest.raises(ScaffoldRefused) as refused:
        scaffolded.write(tmp_path, regenerate=True)
    assert scaffolded.hand_written[0] in str(refused.value)
    assert hand.read_text(encoding="utf-8") == corpora.READ, "the hand-written module was rewritten"
    assert generated.read_text(encoding="utf-8") == "# edited by hand\n"


def test_regenerate_does_rewrite_when_only_generated_files_are_present(tmp_path):
    scaffolded = made()
    scaffolded.write(tmp_path)
    (tmp_path / scaffolded.hand_written[0]).unlink()
    generated = tmp_path / "ingest/emit.py"
    generated.write_text("# edited by hand\n", encoding="utf-8")
    scaffolded.write(tmp_path, regenerate=True)
    assert "# edited by hand" not in generated.read_text(encoding="utf-8")


def test_the_scaffold_declares_its_own_files_not_material(tmp_path):
    # ⛔ `SK-02/1`: every file a scaffold writes is code the corpus is built
    # with, so a manifest that says nothing leaves all eight `unclassified` —
    # and R19 says the remedy arrives as data rather than as instructions.
    scaffolded = made()
    entries = scaffolded.not_material
    assert entries, "the scaffold declares nothing about the files it writes"
    policy = parse(
        json.dumps(
            {
                **corpora.MANIFEST,
                "content": {
                    "include": ["src/*.md"],
                    "not_material": [dict(entry) for entry in entries],
                },
            }
        )
    ).content
    for where in scaffolded.paths:
        assert policy.classify(where) is Classification.NOT_MATERIAL, where


def test_the_declaration_is_globs_so_it_survives_this_skill_changing():
    # ⚠️ Two entries for eight files. A list of exact paths would have to be
    # re-typed the next time a part is added, which is the retyping R19 forbids.
    entries = made().not_material
    assert len(entries) < len(made().paths)
    assert all(entry["glob"].endswith("/**") for entry in entries)


def test_every_declaration_carries_a_reason_the_manifest_will_accept():
    # ⛔ A reason the document refuses is a reason the integrator has to invent.
    for entry in made().not_material:
        assert len(entry["why"]) >= MIN_WHY_CHARS, entry["glob"]


def test_the_report_hands_over_the_declaration_rather_than_describing_it():
    lines = made().lines()
    assert any("content.not_material" in line for line in lines)
    assert any(line.strip() == "ingest/**" for line in lines)


def test_a_plan_is_required_and_a_manifest_is_not_one():
    with pytest.raises(ScaffoldRefused):
        scaffold(corpora.MANIFEST)  # type: ignore[arg-type]


def test_the_report_says_what_done_is():
    lines = made().lines()
    assert any("studyforge validate" in line for line in lines), (
        "the scaffold's own report does not name its definition of done"
    )
    assert isinstance(made(), Scaffold)
