"""`W364` clause 3: the root `conftest.py`'s plugins still tell the truth under `pytest -n`.

⭐ **Every end-to-end arm runs a CHILD pytest in a throwaway git repository whose
`conftest.py` is a byte copy of the REAL root one**, so the hook under test is the shipped
hook and `_root()` resolves to the child — a planted stray dirties the child, never this
checkout. Each arm runs the child SERIAL and PARALLEL and asserts the SAME verdict: a planted
dirtied tree is RED in both, a planted skip is disclosed identically in both.

⚠️ **The two visual-line arms are the exception, and they write nothing:** they run a
browser-free module of THIS checkout's `tests/visual/` in both forms, because the line they
compare is printed by that directory's own conftest, which a byte copy would not exercise.

⚠️ **The parallel arms need `pytest-xdist`**, which the pinned image carries and a host may
not; there they SKIP with a reason that names it — a disclosure, never a pass (Ruling 328).
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.support import git, repository_root, run

#: A bound on each child run: a hang is no verdict.
TIMEOUT = 180

#: The two forms every arm is taken in. ⭐ `-n 2`, not `auto`: two workers are enough to
#: make a worker's session distinct from the controller's, on any host.
FORMS = {"serial": [], "parallel": ["-n", "2"]}

_XDIST = importlib.util.find_spec("xdist") is not None
needs_xdist = pytest.mark.skipif(
    not _XDIST, reason="pytest-xdist is not importable here; the pinned image carries it"
)

_IDENTITY = ("-c", "user.name=test", "-c", "user.email=test@example.invalid")


def _root_conftest():
    """The REAL root conftest, loaded as a module under a name of its own."""
    spec = importlib.util.spec_from_file_location("w364_root", repository_root() / "conftest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _child(tmp_path: Path, files: dict[str, str]) -> Path:
    """A committed throwaway repository carrying the real root conftest and `files`."""
    root = tmp_path / "child"
    root.mkdir()
    shutil.copyfile(repository_root() / "conftest.py", root / "conftest.py")
    (root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    for name, body in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(f"import os, pytest\n\n{body}", encoding="utf-8")
    for arguments in (("init", "-q"), ("add", "."), (*_IDENTITY, "commit", "-q", "-m", "c")):
        result = run([git(), *arguments], cwd=root)
        assert result.returncode == 0, result.stdout + result.stderr
    return root


def _pytest(
    root: Path, form: str, target: tuple[str, ...] = (".",), **extra: str
) -> subprocess.CompletedProcess:
    """Run `target` under `root` in `form`, with this repository's `tools` importable."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTEST_", "STUDYFORGE_"))}
    env["PYTHONPATH"] = str(repository_root())
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.update(extra)
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *FORMS[form], *target],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        check=False,
    )


# --- the worker guard, read off the hooks themselves ----------------------------------


def test_a_WORKER_session_takes_no_snapshot_and_the_CONTROLLER_does():
    conftest = _root_conftest()
    worker = SimpleNamespace(config=SimpleNamespace(workerinput={}))
    conftest.pytest_sessionstart(worker)
    assert conftest._BEFORE == [], "a worker snapshotted the tree"
    controller = SimpleNamespace(config=SimpleNamespace())
    conftest.pytest_sessionstart(controller)
    assert len(conftest._BEFORE) == 1, "the controller took no snapshot"


def test_a_WORKER_never_sets_the_exit_status_where_the_CONTROLLER_would():
    # ⛔ The plant: a "before" snapshot naming a path the tree does not hold, so the delta
    #    is non-empty and a session that ran the check MUST go red — the control proves it.
    quiet = SimpleNamespace(get_plugin=lambda name: None)
    readings = {}
    for role, config in (
        ("worker", SimpleNamespace(workerinput={}, pluginmanager=quiet)),
        ("controller", SimpleNamespace(pluginmanager=quiet)),
    ):
        conftest = _root_conftest()
        conftest._BEFORE.append({f"planted-{uuid.uuid4().hex}": "untracked"})
        session = SimpleNamespace(config=config, exitstatus=0)
        conftest.pytest_sessionfinish(session, 0)
        readings[role] = session.exitstatus
    assert readings == {"worker": 0, "controller": 1}, readings


def test_every_SERIAL_entry_states_its_reason():
    serial = _root_conftest().SERIAL
    assert serial, "no directory is declared serial"
    for prefix, reason in serial.items():
        assert prefix.endswith("/") and (repository_root() / prefix).is_dir(), prefix
        assert len(reason) > 40, prefix


# --- clause 3, end to end, in BOTH forms -----------------------------------------------


@needs_xdist
@pytest.mark.parametrize("form", FORMS)
def test_a_PLANTED_dirtied_tree_is_RED_in_both_forms(tmp_path, form):
    stray = f"stray-{uuid.uuid4().hex}.txt"
    body = f"def test_writes():\n    open({stray!r}, 'w').close()\n\ndef test_ok():\n    pass\n"
    result = _pytest(_child(tmp_path, {"test_plant.py": body}), form)
    assert result.returncode == 1, result.stdout + result.stderr
    assert stray in result.stdout, result.stdout


@needs_xdist
@pytest.mark.parametrize("form", FORMS)
def test_a_CLEAN_run_is_GREEN_and_says_so_in_both_forms(tmp_path, form):
    result = _pytest(_child(tmp_path, {"test_clean.py": "def test_ok():\n    pass\n"}), form)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "tree state: unchanged by this run" in result.stdout, result.stdout


@needs_xdist
def test_a_PLANTED_skip_is_disclosed_IDENTICALLY_in_both_forms(tmp_path):
    reason = f"a sibling {uuid.uuid4().hex} is not checked out"
    body = f"def test_skips():\n    pytest.skip({reason!r})\n\ndef test_ok():\n    pass\n"
    root = _child(tmp_path, {"test_skip.py": body})
    readings = {}
    for form in FORMS:
        result = _pytest(root, form)
        assert result.returncode == 0, result.stdout + result.stderr
        readings[form] = [line for line in result.stdout.splitlines() if reason in line]
    assert readings["serial"] == [f"  1 × {reason}"], readings
    assert readings["parallel"] == readings["serial"], readings


#: The two shapes a run reaches `tests/visual/` in. ⚠️ BOTH MEASURED in the pinned image:
#: from `tests`, the controller never loads that conftest and the line was ABSENT under `-n`;
#: from an argument INSIDE it, the conftest is an initial one there and the forward printed
#: it a SECOND time.
VISUAL_TARGETS = {
    "from-the-suite-root": ("tests", "-k", "test_contrast_math"),
    "from-inside-the-directory": ("tests/visual/test_contrast_math.py",),
}


@needs_xdist
@pytest.mark.parametrize("target", VISUAL_TARGETS.values(), ids=VISUAL_TARGETS)
def test_the_VISUAL_harness_line_is_printed_ONCE_and_IDENTICALLY_in_both_forms(target):
    lines = {}
    for form in FORMS:
        result = _pytest(repository_root(), form, target=target)
        assert result.returncode == 0, result.stdout + result.stderr
        lines[form] = [line for line in result.stdout.splitlines() if "visual harness:" in line]
    assert len(lines["serial"]) == 1, lines
    assert lines["parallel"] == lines["serial"], lines


@needs_xdist
def test_the_CONTROL_a_run_that_reaches_NO_visual_test_prints_no_visual_line_in_either_form():
    lines = {}
    for form in FORMS:
        result = _pytest(repository_root(), form, target=("tools/tests/test_gates.py",))
        assert result.returncode == 0, result.stdout + result.stderr
        lines[form] = [line for line in result.stdout.splitlines() if "visual harness:" in line]
    assert lines == {"serial": [], "parallel": []}, lines


# --- the SERIAL groups: one worker for a declared directory, and a control -------------

#: Enough tests that `load` scheduling spreads an unmarked directory over both workers.
_MANY = 24


def _workers(tmp_path: Path, directory: str) -> set[str]:
    """Run `_MANY` tests under `directory` in parallel; return the workers that ran them."""
    record = tmp_path / "workers"
    record.mkdir()
    body = "".join(
        f"def test_{n}():\n    import time; time.sleep(0.05)\n"
        f"    open(os.path.join(os.environ['W364_RECORD'], '{n}'), 'w')"
        f".write(os.environ['PYTEST_XDIST_WORKER'])\n\n"
        for n in range(_MANY)
    )
    root = _child(tmp_path, {f"{directory}/test_spread.py": body})
    result = _pytest(root, "parallel", W364_RECORD=str(record))
    assert result.returncode == 0, result.stdout + result.stderr
    ran = {path.name: path.read_text(encoding="utf-8") for path in record.iterdir()}
    assert len(ran) == _MANY, ran
    return set(ran.values())


@needs_xdist
def test_a_SERIAL_directory_runs_on_ONE_worker_under_a_bare_n(tmp_path):
    # ⭐ A bare `-n 2`: the conftest's promotion to `loadgroup` is what honours the group.
    assert len(_workers(tmp_path, "tests/visual")) == 1


@needs_xdist
def test_the_CONTROL_an_undeclared_directory_spreads_over_both_workers(tmp_path):
    assert len(_workers(tmp_path, "tests/elsewhere")) == 2
