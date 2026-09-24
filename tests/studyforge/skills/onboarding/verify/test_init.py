"""Mirror of `src/studyforge/skills/onboarding/verify/__init__.py` (R12), and the installed reading.

⭐ Two halves. The command, called in process: exit `0` for a pin naming the
installed version, `1` for another, `UNUSABLE` with a sentence when there is no
pin or no version. ⛔ And THE READING: a wheel of this tree installed into a
fresh venv outside the checkout, a fixture corpus onboarded BY that installed
library with nothing beside it, and every fenced line of the reader's document,
the stubs' command and the generated pin check run from the corpus root there.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import zipfile

import pytest

from studyforge.exitcodes import UNUSABLE
from studyforge.skills.onboarding import artifacts, library, pin, verify
from tests.studyforge.skills.adapter import corpora as adapter
from tests.studyforge.skills.onboarding import corpora, wheels

#: How long one command in the installed venv is given.
TIMEOUT = 180


def _pinned(root, version):
    (root / pin.PIN_DIR).mkdir(parents=True)
    document = pin.pin_document(corpora.COMMIT, version)
    (root / pin.PIN_FILE).write_text(json.dumps(document), encoding="utf-8")
    return root


def test_with_no_root_it_prints_the_version_this_python_imports(capsys):
    assert verify.main([]) == 0
    assert capsys.readouterr().out == (
        f"studyforge {library.version()} is the library this Python imports, "
        f"a source tree that cannot say which commit it is\n"
    )


def test_a_pin_naming_the_installed_version_exits_zero(tmp_path, capsys):
    root = _pinned(tmp_path, library.version())

    assert verify.main([str(root)]) == 0
    assert "the installed version" in capsys.readouterr().out


def test_a_pin_naming_another_version_exits_one_naming_both(tmp_path, capsys):
    root = _pinned(tmp_path, "0.0.1")

    assert verify.main([str(root)]) == verify.MISMATCH == 1
    out = capsys.readouterr().out
    assert "pins studyforge 0.0.1" in out and "NOT the installed version" in out


def test_no_pin_is_unusable_and_says_why(tmp_path, capsys):
    assert verify.main([str(tmp_path)]) == UNUSABLE
    assert "there is no pin" in capsys.readouterr().err


@pytest.mark.parametrize("argv", [["a", "b"], ["--help"]])
def test_a_bad_invocation_is_unusable(argv, capsys):
    assert verify.main(argv) == UNUSABLE
    assert "usage:" in capsys.readouterr().err


# --------------------------------------------------------------------------
# ⛔ The reading: the INSTALLED library, and no framework checkout on disk
# --------------------------------------------------------------------------


#: Onboards the corpus at the working directory with whatever `studyforge` imports.
#: ⭐ `W467`: no commit is passed; a built wheel pins its own.
ONBOARD = (
    "import json, sys; from studyforge.skills.onboarding import onboard; "
    "made = onboard(json.loads(sys.argv[1]), *sys.argv[2:3]); made.write('.'); "
    "print(made.hand_written[0])"
)

#: Onboards naming a commit, which a built wheel checks against its own.
NAMED = (
    "import json, sys; from studyforge.skills.onboarding import onboard; "
    "onboard(json.loads(sys.argv[1]), framework_commit=sys.argv[2])"
)

#: Runs every test the generated pin check defines, with no test runner (`W467`).
PIN_CHECK = ["python3", "tests/test_framework_pin.py"]

#: Runs the one generated check that asks the installed library its version.
INSTALLED_CHECK = (
    "import runpy; runpy.run_path('tests/test_framework_pin.py')"
    "['test_the_installed_library_is_the_pinned_version']()"
)


def _fenced(text):
    lines, inside = [], False
    for line in text.splitlines():
        if line.startswith("```"):
            inside = not inside
        elif inside:
            lines.append(line)
    return lines


@pytest.fixture(scope="module")
def installed(tmp_path_factory):
    """A venv holding a wheel of this tree, its `bin`, and the wheel itself."""
    scratch = tmp_path_factory.mktemp("installed")
    wheel = wheels.build(scratch)
    return wheels.venv(scratch / "venv", wheel), wheel


def _in_venv(bin_dir, root, argv):
    return subprocess.run(
        argv,
        cwd=root,
        env=wheels.environment(bin_dir),
        capture_output=True,
        timeout=TIMEOUT,
        check=False,
    )


def test_a_corpus_onboarded_by_the_installed_library_runs_as_written_with_nothing_beside_it(
    installed, tmp_path
):
    bin_dir, wheel = installed
    root = corpora.material(tmp_path / "work" / "corpus")
    where = _in_venv(
        bin_dir, root, ["python3", "-c", "import studyforge; print(studyforge.__file__)"]
    )
    assert where.stdout.decode().startswith(str(bin_dir.parent)), "the checkout was imported"

    made = _in_venv(bin_dir, root, ["python3", "-c", ONBOARD, json.dumps(corpora.SETTLED)])
    assert made.returncode == 0, made.stderr.decode()
    (root / made.stdout.decode().strip()).write_text(adapter.READ, encoding="utf-8")

    assert sorted(path.name for path in (tmp_path / "work").iterdir()) == ["corpus"]
    text = (root / artifacts.READER_DOC).read_text(encoding="utf-8")
    ran = [(line, _in_venv(bin_dir, root, ["sh", "-c", line])) for line in _fenced(text)]
    assert len(ran) == len(_fenced(text)) > 1
    assert [(line, done.stderr.decode()) for line, done in ran if done.returncode] == []

    with zipfile.ZipFile(wheel) as archive:
        shipped = archive.read("studyforge/skills/onboarding/SKILL.md")
    stub = (root / pin.stub_paths(("onboarding",))[0]).read_text(encoding="utf-8")
    command = next(line.strip() for line in stub.splitlines() if pin.DOCUMENTS in line)
    assert _in_venv(bin_dir, root, ["sh", "-c", command]).stdout == shipped

    checks = _in_venv(bin_dir, root, PIN_CHECK)
    assert checks.returncode == 0, checks.stdout.decode()
    said = checks.stdout.decode().splitlines()
    assert len(said) == 6 and all(line.startswith("ok test_") for line in said), said


def test_the_installed_pin_check_fails_on_another_version(installed, tmp_path):
    bin_dir, _wheel = installed
    root = corpora.material(tmp_path / "corpus")
    made = _in_venv(bin_dir, root, ["python3", "-c", ONBOARD, json.dumps(corpora.DRAFT)])
    assert made.returncode == 0, made.stderr.decode()
    pinned = json.loads((root / pin.PIN_FILE).read_text(encoding="utf-8"))
    (root / pin.PIN_FILE).write_text(json.dumps({**pinned, "version": "0.0.1"}), encoding="utf-8")

    checks = _in_venv(bin_dir, root, ["python3", "-c", INSTALLED_CHECK])
    verified = _in_venv(bin_dir, root, ["sh", "-c", pin.VERIFY])

    assert checks.returncode != 0 and b"install the pinned version" in checks.stderr
    assert verified.returncode == verify.MISMATCH


# --------------------------------------------------------------------------
# ⭐ `W467`: the installed library knows its commit, and the checks need no pytest
# --------------------------------------------------------------------------


def _export_head(wheel):
    """The commit of the export the wheel was built from (`wheels.build`'s layout)."""
    export = wheel.parent.parent / "export"
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=export, capture_output=True, text=True, check=True
    ).stdout.strip()


def test_the_wheel_carries_the_commit_it_was_built_from_and_the_library_says_it(
    installed, tmp_path
):
    bin_dir, wheel = installed
    stamp = wheels.stamp_of(wheel)
    said = _in_venv(
        bin_dir,
        tmp_path,
        [
            "python3",
            "-c",
            "from studyforge.skills.onboarding import library; print(library.commit())",
        ],
    )
    printed = _in_venv(bin_dir, tmp_path, ["sh", "-c", pin.VERIFY.removesuffix(" .")])

    assert stamp == _export_head(wheel)
    assert said.stdout.decode().strip() == stamp
    assert f"built from {stamp}" in printed.stdout.decode()


def test_onboarding_pins_the_wheels_own_commit_and_refuses_another(installed, tmp_path):
    bin_dir, wheel = installed
    root = corpora.material(tmp_path / "corpus")

    refused = _in_venv(
        bin_dir, root, ["python3", "-c", NAMED, json.dumps(corpora.DRAFT), corpora.COMMIT]
    )
    made = _in_venv(bin_dir, root, ["python3", "-c", ONBOARD, json.dumps(corpora.DRAFT)])

    assert refused.returncode != 0 and b"another commit" in refused.stderr
    assert made.returncode == 0, made.stderr.decode()
    pinned = json.loads((root / pin.PIN_FILE).read_text(encoding="utf-8"))
    assert pinned["commit"] == wheels.stamp_of(wheel)


def test_the_generated_checks_run_with_no_test_runner_and_fail_on_another_commit(
    installed, tmp_path
):
    bin_dir, _wheel = installed
    root = corpora.material(tmp_path / "corpus")
    assert _in_venv(bin_dir, root, ["python3", "-c", "import pytest"]).returncode != 0
    made = _in_venv(bin_dir, root, ["python3", "-c", ONBOARD, json.dumps(corpora.DRAFT)])
    assert made.returncode == 0, made.stderr.decode()
    assert _in_venv(bin_dir, root, PIN_CHECK).returncode == 0

    pinned = json.loads((root / pin.PIN_FILE).read_text(encoding="utf-8"))
    (root / pin.PIN_FILE).write_text(json.dumps({**pinned, "commit": "b" * 40}), encoding="utf-8")
    checks = _in_venv(bin_dir, root, PIN_CHECK)
    verified = _in_venv(bin_dir, root, ["sh", "-c", pin.VERIFY])

    assert checks.returncode == 1
    assert b"FAIL test_the_installed_library_was_built_from_the_pinned_commit" in checks.stdout
    assert verified.returncode == verify.MISMATCH
    assert b"NOT the installed build" in verified.stdout


def test_a_wheel_is_not_built_from_a_tree_that_cannot_say_its_commit(tmp_path):
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    wheels.build(scratch)  # ⭐ skips, saying why, where there is no build backend
    export = scratch / "export"
    shutil.rmtree(export / ".git")
    (tmp_path / "out").mkdir()

    built = subprocess.run(
        [sys.executable, "-c", wheels.BUILD, str(tmp_path / "out")],
        cwd=export,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )

    assert built.returncode != 0
    assert "not the top of a git checkout" in built.stderr
    assert list((tmp_path / "out").iterdir()) == []
