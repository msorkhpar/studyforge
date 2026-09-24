"""Mirror of `src/studyforge/skills/adapter/scaffold.py` (R12)."""

from __future__ import annotations

import compileall
import json
from dataclasses import replace
from pathlib import PurePosixPath

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
from studyforge.skills.adapter.parts import Part
from studyforge.skills.adapter.scaffold import (
    BYTECODE_RULES,
    IGNORE_FILE,
    bytecode_ignore,
    bytecode_ignores,
)
from tests.floor.config import SOURCE_LINE_CEILING as OWNED_CEILING
from tests.studyforge.skills.adapter import corpora


def made():
    """A scaffold for the walkthrough corpus."""
    return scaffold(plan_for(parse(json.dumps(corpora.MANIFEST))))


def test_the_ceiling_is_the_one_the_quality_floor_owns():
    # ⛔ The pin for the copy in `scaffold.py`. The product floor under `tests/floor/`
    # owns R11's ceiling and shipped code may not import a test package, so the
    # number is duplicated — and a duplicate nobody compares is how two rules
    # become two different rules.
    assert SOURCE_LINE_CEILING == OWNED_CEILING


def test_every_generated_file_is_under_r11s_ceiling():
    # ⭐ The scaffold's acceptance clause, as a measurement rather than an assertion.
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


def _generated_beside(scaffolded):
    """A generated file in the hand-written module's own directory."""
    package = PurePosixPath(scaffolded.hand_written[0]).parent
    return next(
        item.where
        for item in scaffolded.files
        if item.generated and PurePosixPath(item.where).parent == package
    )


def test_regenerate_rewrites_the_generated_files_and_keeps_the_one_that_is_yours(tmp_path):
    # ⛔ After step 4 the hand-written module always exists, so refusing
    # on it would refuse every regenerate, and overwriting it is R19 broken.
    scaffolded = made()
    scaffolded.write(tmp_path)
    hand = tmp_path / scaffolded.hand_written[0]
    hand.write_bytes(corpora.READ.encode("utf-8"))
    before = hand.read_bytes()
    generated = tmp_path / _generated_beside(scaffolded)
    generated.write_text("# edited by hand\n", encoding="utf-8")

    written = scaffolded.write(tmp_path, regenerate=True)

    assert hand.read_bytes() == before, "a regenerate rewrote the hand-written module"
    assert "# edited by hand" not in generated.read_text(encoding="utf-8")
    assert scaffolded.hand_written[0] not in written, "a regenerate reported writing it"
    assert sorted(written) == sorted(set(scaffolded.paths) - set(scaffolded.hand_written))


def test_the_kept_module_is_the_seam_the_scaffold_declares_and_not_a_name(tmp_path):
    # ⛔ R1: which module is kept comes from `Written.generated`. Move the seam,
    # and what a regenerate keeps must move with it.
    moved = tuple(
        part if part.generated else replace(part, where="{package}/elsewhere.py") for part in PARTS
    )
    scaffolded = scaffold(plan_for(parse(json.dumps(corpora.MANIFEST))), moved)
    scaffolded.write(tmp_path)
    assert scaffolded.hand_written == ("ingest/elsewhere.py",), "the seam did not move"
    hand = tmp_path / scaffolded.hand_written[0]
    hand.write_text("# mine\n", encoding="utf-8")

    scaffolded.write(tmp_path, regenerate=True)

    assert hand.read_text(encoding="utf-8") == "# mine\n"


def test_a_first_scaffold_over_the_hand_written_module_alone_refuses_by_name(tmp_path):
    scaffolded = made()
    hand = tmp_path / scaffolded.hand_written[0]
    hand.parent.mkdir(parents=True)
    hand.write_text("# mine\n", encoding="utf-8")

    with pytest.raises(ScaffoldRefused) as refused:
        scaffolded.write(tmp_path)

    assert scaffolded.hand_written[0] in str(refused.value)
    assert [path for path in tmp_path.rglob("*") if path.is_file()] == [hand], "it wrote anyway"


def test_regenerate_writes_the_stub_when_the_hand_written_module_is_absent(tmp_path):
    scaffolded = made()
    scaffolded.write(tmp_path)
    (tmp_path / scaffolded.hand_written[0]).unlink()
    generated = tmp_path / _generated_beside(scaffolded)
    generated.write_text("# edited by hand\n", encoding="utf-8")

    written = scaffolded.write(tmp_path, regenerate=True)

    assert "# edited by hand" not in generated.read_text(encoding="utf-8")
    assert scaffolded.hand_written[0] in written


def test_the_scaffold_declares_its_own_files_not_material(tmp_path):
    # ⛔ Every file a scaffold writes is code the corpus is built
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


# --------------------------------------------------------------------------
# ⛔ Every directory the scaffold puts Python in ignores its own bytecode
# --------------------------------------------------------------------------


def test_every_directory_holding_a_generated_module_carries_its_own_ignore_file():
    # ⛔ Clause 1: derived from the modules, so the adapter's package and its
    # tests' package each get one — and a scaffold run on its own gets them too.
    scaffolded = made()
    homes = {str(PurePosixPath(w).parent) for w in scaffolded.paths if w.endswith(".py")}

    texts = {item.where: item.text for item in scaffolded.files}
    assert homes == {"ingest", "tests/ingest"}
    for home in homes:
        assert texts[f"{home}/{IGNORE_FILE}"] == bytecode_ignore(), home


def test_the_ignore_file_names_bytecode_and_nothing_else():
    rules = [line for line in bytecode_ignore().splitlines() if not line.startswith("#")]
    assert rules == list(BYTECODE_RULES) == ["__pycache__/", "*.py[co]"]


def test_a_directory_with_no_module_gets_no_ignore_file():
    # ⭐ The other way: derived, never listed — a directory holding no Python
    # is given nothing, and neither is a non-module file in one.
    assert bytecode_ignores(["notes/a.md", "data/b.json", "ingest/c.pyi"]) == ()
    assert bytecode_ignores(["ingest/a.py", "ingest/b.py"]) == (f"ingest/{IGNORE_FILE}",)


def test_a_module_at_the_repository_root_never_gets_the_root_ignore_file():
    # ⛔ R3: the root ignore file is a source file, never generated.
    assert bytecode_ignores(["setup.py"]) == ()
    assert bytecode_ignores(["setup.py", "pkg/a.py"]) == (f"pkg/{IGNORE_FILE}",)


def test_a_module_added_in_a_new_directory_gains_an_ignore_file_without_a_list():
    # ⭐ Derived rather than listed: a part in a directory no part used before
    # is given its ignore file with nobody editing a list of directories.
    extra = Part(
        where="{package}/extra/more.py",
        step=6,
        why="a planted module",
        generated=True,
        render=lambda plan: "x = 1\n",
    )
    scaffolded = scaffold(made().plan, (*PARTS, extra))

    assert f"ingest/extra/{IGNORE_FILE}" in scaffolded.paths
    assert f"ingest/extra/{IGNORE_FILE}" not in made().paths


def test_each_ignore_file_is_built_at_the_first_step_that_puts_python_there():
    steps = {item.where: item.step for item in made().files}

    assert steps[f"ingest/{IGNORE_FILE}"] == min(
        steps[w] for w in steps if w.startswith("ingest/") and w.endswith(".py")
    )
    assert steps[f"tests/ingest/{IGNORE_FILE}"] == min(
        steps[w] for w in steps if w.startswith("tests/ingest/") and w.endswith(".py")
    )


def test_the_ignore_files_add_no_glob_the_manifest_must_carry():
    # ⭐ They land in directories the scaffold already declares, so an
    # onboarded corpus already carries every glob they need.
    without = Scaffold(plan=made().plan, files=made().files[: len(PARTS)])
    assert made().not_material == without.not_material
