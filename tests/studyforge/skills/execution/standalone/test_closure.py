"""Mirror of `src/studyforge/skills/execution/standalone/closure.py` (R12).

⭐ The closure is PROVED, not trusted: the vendored files are copied into an
empty directory, and the study server is started from that directory alone, in
an interpreter that sees no other `studyforge`, and asked for a page. ⛔ Each
reading below has a plant beside it that turns it red.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

import pytest

from studyforge.generate import write_site
from studyforge.skills.execution.standalone import closure
from tests.studyforge.cli.serving import LISTENING
from tests.studyforge.execute.runnable import fixture_copy

SRC = Path(closure.__file__).resolve().parents[4]


def vendor(into: Path, src: Path = SRC) -> Path:
    """The vendored runtime, copied into `into`, as the export copies it."""
    for one in closure.vendored(src):
        (into / one).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src / one, into / one)
    return into


def isolated(library: Path, *argv: str, cwd: Path, **kwargs) -> subprocess.Popen:
    """A Python that imports `studyforge` from `library` and from nowhere else."""
    return subprocess.Popen(
        [sys.executable, "-S", "-B", *argv],
        cwd=cwd,
        env={"PYTHONPATH": str(library), "PYTHONDONTWRITEBYTECODE": "1"},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        **kwargs,
    )


# -------------------------------------------------------------- the reading


def test_the_real_tree_serves_with_nothing_a_learner_never_carries():
    served = closure.served(SRC)
    assert "studyforge.serve.app" in served
    assert "studyforge.cli.serve" in served
    assert closure.forbidden(served) == ()


def test_every_declared_deferred_edge_is_one_the_tree_still_makes():
    assert closure.stale(SRC) == ()
    for importer, imported in closure.DEFERRED:
        assert imported in closure.imported(SRC, importer), (importer, imported)


def test_a_planted_import_of_a_skill_in_a_served_module_is_forbidden(tmp_path):
    planted = Path(shutil.copytree(SRC / "studyforge", tmp_path / "studyforge"))
    target = planted / "serve" / "app.py"
    target.write_text(
        target.read_text(encoding="utf-8") + "\nfrom studyforge.skills.adapter import Layout\n",
        encoding="utf-8",
    )
    assert "studyforge.skills.adapter" in closure.forbidden(closure.served(tmp_path))


def test_a_planted_function_local_import_is_followed_too(tmp_path):
    planted = Path(shutil.copytree(SRC / "studyforge", tmp_path / "studyforge"))
    target = planted / "serve" / "app.py"
    target.write_text(
        target.read_text(encoding="utf-8")
        + "\n\ndef _late():\n    from studyforge.narrate.synth import plan\n",
        encoding="utf-8",
    )
    assert "studyforge.narrate.synth" in closure.forbidden(closure.served(tmp_path))


def test_a_deferred_edge_the_tree_stopped_making_is_stale(tmp_path):
    planted = Path(shutil.copytree(SRC / "studyforge", tmp_path / "studyforge"))
    ledger = planted / "validate" / "ledger.py"
    ledger.write_text(
        ledger.read_text(encoding="utf-8").replace(
            "from studyforge.skills.exercises import scan", "scan = None"
        ),
        encoding="utf-8",
    )
    assert ("studyforge.validate.ledger", "studyforge.skills.exercises.scan") in closure.stale(
        tmp_path
    )


def test_a_packages_data_travels_with_it_and_a_skipped_packages_does_not():
    files = closure.vendored(SRC)
    assert any(one.startswith("studyforge/render/templates/") for one in files)
    assert any(one.startswith("studyforge/render/assets/") for one in files)
    assert not any(one.startswith("studyforge/narrate/release/") for one in files)
    assert not any(one.startswith("studyforge/skills/") for one in files)
    assert not any("__pycache__" in one or one.endswith(".pyc") for one in files)
    assert f"{closure.PACKAGE}/{closure.STAMP}" not in files


# ---------------------------------------------------------- the proof, served


def test_the_served_app_imports_from_the_vendored_tree_alone(tmp_path):
    library = vendor(tmp_path / "library")
    probe = (
        "import sys; import studyforge.serve.app, studyforge.cli.serve, studyforge.cli.preflight; "
        "from studyforge.cli.dispatch import VERBS; VERBS['serve'].run; VERBS['preflight'].run; "
        "print(studyforge.serve.app.__file__.startswith(sys.argv[1]))"
    )
    ran = isolated(library, "-c", probe, str(library), cwd=tmp_path)
    out, _ = ran.communicate(timeout=120)
    assert ran.returncode == 0, out
    assert out.strip().endswith("True"), out


def test_the_vendored_tree_holds_no_module_a_learner_never_carries(tmp_path):
    library = vendor(tmp_path / "library")
    for name in closure.FORBIDDEN:
        assert not (library / Path(*name.split("."))).exists(), name
        assert not (library / Path(*name.split("."))).with_suffix(".py").exists(), name


def test_a_vendored_tree_missing_its_templates_is_caught_by_the_proof(tmp_path):
    library = vendor(tmp_path / "library")
    shutil.rmtree(library / "studyforge" / "render" / "templates")
    with pytest.raises(AssertionError):
        serve_a_page(tmp_path, library)


def test_the_vendored_tree_serves_a_built_course_and_answers_its_pages(tmp_path):
    serve_a_page(tmp_path, vendor(tmp_path / "library"))


def serve_a_page(tmp_path: Path, library: Path) -> None:
    """Build the runnable fixture in place, serve it from `library` alone, and read `/`."""
    root = fixture_copy(tmp_path / "course")
    write_site(root, root)
    server = isolated(
        library, "-m", "studyforge.cli", "serve", str(root), "--port", "0", cwd=tmp_path
    )
    try:
        port = None
        for _ in range(200):
            line = server.stdout.readline()
            if not line:
                break
            if found := LISTENING.match(line):
                port = int(found.group(1))
                break
        assert port is not None, "the vendored server never listened"
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=20) as answer:
            assert answer.status == 200
            assert b"<html" in answer.read().lower()
    finally:
        server.terminate()
        server.communicate(timeout=30)
