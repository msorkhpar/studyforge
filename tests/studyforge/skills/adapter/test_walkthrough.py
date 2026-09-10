"""SK-02's acceptance, run end to end on a source this skill has never seen.

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

from studyforge.corpus.manifest import parse
from studyforge.skills.adapter import plan_for, scaffold
from studyforge.validate import validate
from tests.studyforge.skills.adapter import corpora
from tests.support import repository_root

#: How long a subprocess is given. ⚠️ A bound rather than a hope: one that
#: hangs turns a failing test into a stalled build.
TIMEOUT = 180


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
    # ⚠️ `SK-02/1`: the manifest cannot classify the adapter until the adapter's
    # paths exist, so this amendment happens after the scaffold rather than
    # before it. That ordering is the finding, not a convenience.
    corpora.classify(root, made.paths)
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


def test_the_manifest_the_walkthrough_writes_is_the_one_the_plan_reads(tmp_path):
    # ⭐ A premise check: if the fixture stopped being a corpus this skill can
    # scaffold, every assertion above would pass for the wrong reason.
    root = tmp_path / "corpus"
    corpora.write(root)
    manifest = json.loads((root / "corpus.json").read_text(encoding="utf-8"))
    assert manifest["corpus_api"] == 1
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


def _archive(root):
    """Every emitted document, by content — what R10 compares."""
    return sorted(
        (path.relative_to(root).as_posix(), path.read_bytes())
        for path in (root / "archive").rglob("*.json")
    )
