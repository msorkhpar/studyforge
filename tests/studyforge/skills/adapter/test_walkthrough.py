"""The adapter scaffold's acceptance, run end to end on a source this skill has never seen.

⭐ **Three clauses, and each one is a command here rather than an opinion:**

1. a scaffolded adapter's tests **run and fail informatively** before any source
   reading is written;
2. following the skill on a source it has never seen reaches a
   **`validate`-clean archive**;
3. the generated structure honours **R11's size ceiling** (asserted in
   `test_scaffold.py`, which owns the measurement).

⚠️ **Everything below runs in a subprocess, on purpose.** Importing the
generated suite here would put a second `tests` package on the path beside this
repository's own, and what is being asserted is that *pytest* and
*`python3 -m ingest`* — the two things an integrator will actually type —
produce output a person can act on.

⛔ **The steps run in `SKILL.md`'s own order**: scaffold, run the suite and read
the failure, write `read.py`, ingest, run the suite again. A test that emitted
before step 4 would never see the failure step 4 exists for.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

from studyforge.corpus.container import CONTAINER_FILENAME
from studyforge.corpus.manifest import parse
from studyforge.skills.adapter import plan_for, scaffold
from studyforge.validate import validate
from studyforge.validate.source import RULE_NESTED_REPOSITORY
from tests.studyforge.skills.adapter import corpora
from tests.support import git, init_repository, repository_root, run

#: How long a subprocess is given. ⚠️ A bound rather than a hope: one that
#: hangs turns a failing test into a stalled build.
TIMEOUT = 180

#: A date the hand-written reader records that is NOT the run's.
READER_DATE = "1999-12-31"

#: The directory a repository ignores, planted where a copy must not take it.
IGNORED = "scratch"

#: Where a nested repository is planted, beneath the material.
NESTED = "src/vendored"

#: Runs the GENERATED `test_emit`'s own `_copy` and prints what arrived and
#: what it warned. ⭐ The generated code is exercised, never a copy of it.
COPY_PROBE = "\n".join(
    [
        "import importlib.util, json, tempfile, warnings",
        "from pathlib import Path",
        'test_file = Path("tests/ingest/test_emit.py").resolve()',
        'spec = importlib.util.spec_from_file_location("probe", test_file)',
        "module = importlib.util.module_from_spec(spec)",
        "spec.loader.exec_module(module)",
        "with tempfile.TemporaryDirectory() as tmp, warnings.catch_warnings(record=True) as said:",
        '    warnings.simplefilter("always")',
        "    where = module._copy(Path(tmp))",
        '    files = [p for p in where.rglob("*") if p.is_file()]',
        "    copied = sorted(p.relative_to(where).as_posix() for p in files)",
        '    print(json.dumps({"copied": copied, "said": [str(w.message) for w in said]}))',
    ]
)


def _environment(root):
    """The corpus and the framework on the path, and nothing inherited that steers pytest."""
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(root), str(repository_root() / "src")])
    env.pop("PYTEST_ADDOPTS", None)
    return env


def _run(root, command):
    """Run one command inside the corpus, the way an integrator would."""
    return subprocess.run(
        [sys.executable, *command],
        cwd=root,
        env=_environment(root),
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        check=False,
    )


def _pytest(root):
    """Step 4: run the adapter's own suite."""
    return _run(root, ["-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"])


def _ingest(root):
    """Step 7: emit for real, then audit."""
    return _run(root, ["-m", "ingest", str(root), corpora.INGESTED])


def _scaffolded(root):
    """Steps 1–3: write the corpus, scaffold an adapter into it, classify it."""
    corpora.write(root)
    made = scaffold(plan_for(parse((root / "corpus.json").read_text(encoding="utf-8"))))
    made.write(root)
    # ⭐ The adapter's own files are code, not material, so the
    # manifest has to say so or `validate` reports every one of them. The globs
    # come from the scaffold — nothing here is retyped (R19).
    corpora.classify(root, made.not_material)
    return made


def _written(root, made, text=None):
    """Step 5: write the reading module, the one file that is a person's."""
    (root / made.hand_written[0]).write_text(text or corpora.READ, encoding="utf-8")


def test_the_generated_suite_fails_informatively_before_any_source_is_read(tmp_path):
    # ⛔ Clause 1, and the word doing the work is *fail*. A scaffold whose tests
    # passed on delivery would put a green tick against a corpus with no
    # material in it, and green is the one signal nobody re-reads.
    root = tmp_path / "corpus"
    _scaffolded(root)

    result = _pytest(root)
    assert result.returncode != 0, "the generated suite passed on an adapter that reads nothing"
    output = result.stdout + result.stderr
    assert "NotImplementedError" in output
    assert "is not written yet" in output, "the failure does not say what is missing"
    assert "read.containers" in output, "the failure does not name the step to write next"
    assert "Return a list of studyforge.corpus.container.Container" in output, (
        "the failure names the step but not what it must return"
    )


def test_following_the_skill_reaches_a_validate_clean_archive(tmp_path):
    # ⛔ Clause 2, on a source this skill has never seen. Everything between the
    # manifest and the exit code below is generated.
    root = tmp_path / "corpus"
    made = _scaffolded(root)
    _written(root, made)

    ingested = _ingest(root)
    assert ingested.returncode == 0, ingested.stdout + ingested.stderr
    assert "valid: 0 finding(s)" in ingested.stdout

    report = validate(root)
    assert report.ok, "\n".join(report.lines())

    suite = _pytest(root)
    assert suite.returncode == 0, suite.stdout + suite.stderr


def test_the_audit_refuses_while_the_source_side_count_is_unwritten(tmp_path):
    # ⛔ An unchecked claim is not a pass. `validate` alone is clean here — the
    # archive is well formed — and the run still exits non-zero, because
    # nothing has counted this corpus from anything but its own output.
    root = tmp_path / "corpus"
    made = _scaffolded(root)
    unwritten = corpora.READ.replace('    return {"course"', '    return None  # {"course"')
    _written(root, made, unwritten)

    ingested = _ingest(root)
    assert ingested.returncode != 0, "the audit passed with nothing counted from the source"
    assert "expected_units is not written" in ingested.stdout
    assert validate(root).ok, "validate itself should be clean; only the audit refuses"


def test_the_ingest_never_touches_the_material_it_was_pointed_at(tmp_path):
    # ⛔ R3: no existing file in a source repository is moved, renamed or
    # rewritten. Measured by content, over every file that existed first.
    root = tmp_path / "corpus"
    made = _scaffolded(root)
    _written(root, made)
    before = _contents(root)

    assert _ingest(root).returncode == 0
    after = _contents(root)
    for where, content in before.items():
        assert after.get(where) == content, f"{where} was rewritten by the ingest (R3)"


def test_two_ingests_produce_the_same_bytes(tmp_path):
    # ⭐ R10, at the level an integrator meets it: run the command twice.
    root = tmp_path / "corpus"
    made = _scaffolded(root)
    _written(root, made)

    assert _ingest(root).returncode == 0
    first = _archive(root)
    assert _ingest(root).returncode == 0
    assert _archive(root) == first, "two runs of the same adapter disagree"


def test_nothing_reaches_the_target_path_when_an_emission_breaks_part_way(tmp_path):
    # ⛔ §6: a deliberately corrupted emission leaves no file at the path
    # `validate` reads. ⚠️ The break is on the SECOND document on purpose —
    # the first is already staged, so this is the half-written tree, not a
    # refusal before anything was written.
    root = tmp_path / "corpus"
    made = _scaffolded(root)
    _written(
        root,
        made,
        corpora.READ.replace(
            '"kind": "lesson",', '"kind": "lesson" if unit.n == 1 else "chapter",'
        ),
    )

    result = _ingest(root)
    assert result.returncode != 0, "an emission that could not finish reported success"
    assert not (root / "archive").exists(), "a broken emission left an archive behind"


def test_every_container_map_carries_the_runs_date_whatever_the_reader_recorded(tmp_path):
    # ⛔ Over a GENERATED emit. The reader records a
    # date that is not the run's, so a map that kept it would disagree with the
    # documents beneath it. The date is applied after the reader.
    root = tmp_path / "corpus"
    made = _scaffolded(root)
    reader = corpora.READ.replace(f'INGESTED = "{corpora.INGESTED}"', f'INGESTED = "{READER_DATE}"')
    assert reader != corpora.READ, "premise: the fixture reader no longer records its own date"
    _written(root, made, reader)

    ingested = _ingest(root)
    assert ingested.returncode == 0, ingested.stdout + ingested.stderr
    archive = root / "archive"
    maps = sorted(archive.rglob(CONTAINER_FILENAME))
    documents = sorted(p for p in archive.rglob("*.json") if p.name != CONTAINER_FILENAME)
    assert maps and documents, "premise: nothing was emitted to compare"
    assert {_dated(path) for path in maps} == {corpora.INGESTED}, "a map kept the reader's date"
    assert {_dated(path) for path in documents} == {corpora.INGESTED}

    # ⭐ And the generated suite's own dating test holds on the same corpus.
    suite = _pytest(root)
    assert suite.returncode == 0, suite.stdout + suite.stderr


def test_the_generated_copy_leaves_out_a_directory_the_repository_ignores(tmp_path):
    # ⛔ A working tree ignores `scratch/`, and the
    # generated `test_emit` must not carry it into its copy, nor `.git`, nor the
    # archive. ⭐ The answer is git's, through the one ignore reader.
    root = tmp_path / "corpus"
    made = _scaffolded(root)
    _written(root, made)
    init_repository(root)
    _plant_ignored(root)
    premise = run([git(), "check-ignore", "-q", IGNORED], cwd=root)
    assert premise.returncode == 0, "premise: the repository does not ignore the plant"

    probe = _copied(root)
    assert not [p for p in probe["copied"] if p.startswith(f"{IGNORED}/")], probe["copied"]
    assert {"src/01.md", ".gitignore", "corpus.json"} <= set(probe["copied"])
    assert not [p for p in probe["copied"] if p.startswith((".git/", "archive/"))]
    assert probe["said"] == [], "a working tree's copy warned that it could not ask"


def test_outside_a_working_tree_nothing_is_declared_ignored_and_the_copy_says_so(tmp_path):
    # ⚠️ A corpus that is not a git working tree (a `git archive` export)
    # has no declaration to read. An export holds only what was tracked, so
    # "ignored" means nothing there: the copy takes every file but the archive,
    # and warns rather than looking like a copy that asked.
    root = tmp_path / "corpus"
    made = _scaffolded(root)
    _written(root, made)
    _plant_ignored(root)

    probe = _copied(root)
    assert f"{IGNORED}/deep/left.txt" in probe["copied"]
    assert not [p for p in probe["copied"] if p.startswith("archive/")]
    assert any("not a git working tree" in said for said in probe["said"]), probe["said"]


def test_the_generated_copy_keeps_a_nested_store_and_leaves_out_only_the_roots_own(tmp_path):
    # ⛔ `SKIP_DIRS` at the corpus root only, as `validate`
    # asks it. A nested store is copied, so `validate` meets it in the copy.
    root = tmp_path / "corpus"
    made = _scaffolded(root)
    _written(root, made)
    init_repository(root)
    init_repository(root / NESTED)

    copied = set(_copied(root)["copied"])

    assert f"{NESTED}/.git/HEAD" in copied, "a nested store was left out of the copy"
    assert not [path for path in copied if path.startswith(".git/")], "the root's store was copied"


def test_outside_a_working_tree_a_nested_store_is_copied_too(tmp_path):
    root = tmp_path / "corpus"
    made = _scaffolded(root)
    _written(root, made)
    init_repository(root / NESTED)

    probe = _copied(root)

    assert f"{NESTED}/.git/HEAD" in probe["copied"]
    assert any("not a git working tree" in said for said in probe["said"]), probe["said"]


def test_a_nested_store_turns_the_generated_test_emit_red_by_validates_own_rule(tmp_path):
    # ⛔ Both ways: the root's own store reads clean, and a nested
    # one fails `test_emit` by `validate`'s rule name, never by a name typed here.
    root = tmp_path / "corpus"
    made = _scaffolded(root)
    _written(root, made)
    init_repository(root)
    command = ["-m", "pytest", "tests/ingest/test_emit.py", "-q", "-p", "no:cacheprovider"]

    clean = _run(root, command)
    assert clean.returncode == 0, clean.stdout + clean.stderr

    init_repository(root / NESTED)
    refused = _run(root, command)

    output = refused.stdout + refused.stderr
    assert refused.returncode != 0, "test_emit read clean over a nested repository store"
    assert RULE_NESTED_REPOSITORY in output, output
    assert "test_what_this_adapter_emits_is_what_validate_accepts" in output


def test_the_manifest_the_walkthrough_writes_is_the_one_the_plan_reads(tmp_path):
    # ⭐ A premise check: if the fixture stopped being a corpus this skill can
    # scaffold, every assertion above would pass for the wrong reason.
    root = tmp_path / "corpus"
    corpora.write(root)
    manifest = json.loads((root / "corpus.json").read_text(encoding="utf-8"))
    assert manifest["corpus_api"] == 2
    assert manifest["exercises"] is False
    assert parse(json.dumps(manifest)).source == "walkthrough"


def _contents(root):
    """Every file that is neither the archive nor the manifest, by content."""
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and path.name != "corpus.json"
        and "archive" not in path.relative_to(root).parts[:1]
        and "__pycache__" not in path.parts
    }


def _dated(path):
    """The `ingested` one emitted JSON file carries."""
    return json.loads(path.read_text(encoding="utf-8"))["ingested"]


def _plant_ignored(root):
    """Declare `IGNORED/` ignored, fill it, and leave a stale archive beside it."""
    (root / ".gitignore").write_text(f"{IGNORED}/\n", encoding="utf-8")
    deep = root / IGNORED / "deep"
    deep.mkdir(parents=True)
    (deep / "left.txt").write_text("never copied from a working tree\n", encoding="utf-8")
    (root / "archive").mkdir()
    (root / "archive" / "stale.json").write_text("{}\n", encoding="utf-8")


def _copied(root):
    """Run the generated `_copy` inside the corpus and return what it reported."""
    result = _run(root, ["-c", COPY_PROBE])
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def _archive(root):
    """Every emitted document, by content — what R10 compares."""
    return sorted(
        (path.relative_to(root).as_posix(), path.read_bytes())
        for path in (root / "archive").rglob("*.json")
    )
