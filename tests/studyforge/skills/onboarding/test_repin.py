"""Mirror of `src/studyforge/skills/onboarding/repin.py` (R12).

⭐ **No real pip, git or docker runs here.** Each process the command would
start is handed to a recording machine that answers as the real one would, so
the order, the argv and the stop at the first failure are read off what was
ASKED. ⭐ The steps that are framework functions run for real, on a corpus
onboarded in the test's own directory, except `build` and `stage-site`, whose
own suites cover them and which this file replaces with recorders.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

from studyforge.corpus.manifest import parse
from studyforge.skills.execution import onboard as execution
from studyforge.skills.onboarding import cli, hand_edited, library, onboard, repin
from studyforge.skills.onboarding.pin import PIN_FILE, stub_paths
from studyforge.skills.onboarding.repin import compose_argv
from tests.studyforge.skills.execution.contracts import corpus, editor_text, manifest_document
from tests.studyforge.skills.onboarding import corpora

#: The commit the checkout is at, as `git rev-parse HEAD` answers it (shape only).
HEAD = "b" * 40

#: The order every step is named in, the docker and audit steps included.
EVERY = (
    "checkout",
    "wheel",
    "install",
    "hand-over",
    "pin",
    "execution",
    "build",
    "stage-site",
    "compose-up",
    "audit",
)


class Machine:
    """Answers each argv as git, pip, docker or `ingest` would, and records it."""

    def __init__(self, *, status="", head=f"{HEAD}\n", failing=None):
        self.status, self.head, self.failing = status, head, failing
        self.calls: list[list[str]] = []

    def __call__(self, argv, cwd):
        argv = [str(part) for part in argv]
        self.calls.append(argv)
        if self.failing is not None and self.failing in argv:
            return 1, ""
        if "status" in argv:
            return 0, self.status
        if "rev-parse" in argv:
            return 0, self.head
        if "wheel" in argv:
            into = Path(argv[argv.index("-w") + 1])
            (into / "studyforge-0.1.0-py3-none-any.whl").write_bytes(b"")
        return 0, ""

    def asked(self, word):
        return [argv for argv in self.calls if word in argv]


def _onboarded(tmp_path):
    """A corpus onboarded at `corpora.COMMIT`, by a library built from that commit."""
    root = corpora.material(tmp_path / "corpus")
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(library, "commit", lambda *_: corpora.COMMIT)
        onboard(corpora.DRAFT, framework_commit=corpora.COMMIT, root=root).write(root)
    return root


def _checkout(tmp_path):
    checkout = tmp_path / "framework"
    checkout.mkdir()
    return checkout


def _main(argv, machine):
    out = io.StringIO()
    code = repin.main(argv, run=machine, out=out)
    return code, out.getvalue()


# --- the plan, read without running it --------------------------------------


def test_a_dry_run_names_every_step_in_order_and_runs_nothing(tmp_path):
    machine = Machine()

    code, said = _main(["../framework", "--dry-run", "--up", "--audit-date", "2026-01-02"], machine)

    assert code == 0
    assert machine.calls == []
    positions = [said.index(f"] {name}") for name in EVERY]
    assert positions == sorted(positions)


def test_a_dry_run_prints_the_commands_as_given_with_no_path_resolved(tmp_path):
    code, said = _main(["../framework", "--dry-run", "--audit-date", "2026-01-02"], Machine())

    assert code == 0
    assert "pip wheel -q --no-deps --no-build-isolation -w .scratch/wheels/" in said
    assert "../framework" in said
    assert "--no-index --no-deps --force-reinstall" in said
    assert "git -C ../framework rev-parse HEAD" in said
    assert "-m ingest . 2026-01-02" in said
    assert str(tmp_path) not in said


def test_without_up_the_docker_steps_are_printed_as_skipped(tmp_path):
    _, said = _main(["../framework", "--dry-run"], Machine())

    assert "] stage-site: skipped" in said and "] compose-up: skipped" in said
    assert "] audit: skipped" in said
    assert "docker compose" not in said


def test_with_up_the_compose_commands_are_the_execution_skills_own(tmp_path):
    _, said = _main(["../framework", "--dry-run", "--up"], Machine())

    assert " ".join(compose_argv("build", "site")) in said
    assert " ".join(compose_argv("up", "-d", "--wait")) in said
    assert "docker image prune -f --filter label=com.local.compose.project=" in said


def test_the_compose_command_is_the_one_the_execution_document_prints(tmp_path):
    # ⛔ Two spellings of one command drift: this binds the argv to the printed line.
    made = execution.generate(
        parse(json.dumps(manifest_document())), editor_text=editor_text(), root=corpus(tmp_path)
    )
    printed = dict(made.files)[execution.READER_DOC]

    assert " ".join(compose_argv("build", "site")) in printed
    assert " ".join(compose_argv("up", "-d", "--wait")) in printed


def test_the_onboarding_module_takes_repin_as_its_first_word(tmp_path, capsys):
    assert cli.main(["repin", "../framework", "--dry-run"]) == 0
    assert "] checkout" in capsys.readouterr().out


def test_an_audit_date_that_is_not_a_date_is_refused_before_anything_runs(tmp_path):
    with pytest.raises(SystemExit):
        repin.main(["../framework", "--audit-date", "yesterday"], run=Machine(), out=io.StringIO())


# --- the first half: the checkout, the wheel, the install, the hand-over ----


def _first_half(tmp_path, machine, *more):
    root, checkout = tmp_path / "corpus", _checkout(tmp_path)
    root.mkdir()
    return _main([str(checkout), "--root", str(root), *more], machine), root, checkout


def test_a_dirty_checkout_is_refused_and_nothing_is_built(tmp_path):
    machine = Machine(status=" M setup.py\n")

    (code, said), _, _ = _first_half(tmp_path, machine)

    assert code != 0
    assert "stopped at step 'checkout'" in said
    assert "uncommitted" in said
    assert machine.asked("wheel") == [] and machine.asked("install") == []


def test_a_truncated_commit_is_refused_rather_than_pinned(tmp_path):
    # ⛔ The failure this command exists for: a short hash once reached a pin.
    machine = Machine(head="8cccf1ba\n")

    (code, said), _, _ = _first_half(tmp_path, machine)

    assert code != 0 and "stopped at step 'checkout'" in said
    assert machine.asked("wheel") == []


def test_the_steps_run_in_order_and_hand_over_the_full_commit(tmp_path):
    machine = Machine()

    (code, said), root, checkout = _first_half(
        tmp_path, machine, "--toolchain", str(tmp_path / "toolchain"), "--up"
    )

    assert code == 0, said
    built, installed, handed = machine.calls[2:]
    assert built[-1] == str(checkout) and "wheel" in built
    wheel = root / ".scratch/wheels" / HEAD / "studyforge-0.1.0-py3-none-any.whl"
    assert installed == [
        sys.executable, "-m", "pip", "install", "--no-index", "--no-deps",
        "--force-reinstall", str(wheel),
    ]  # fmt: skip
    module = [sys.executable, "-m", "studyforge.skills.onboarding", "repin"]
    assert handed[:5] == [*module, str(checkout)]
    assert handed[handed.index("--installed") + 1] == HEAD
    assert "--up" in handed and str(tmp_path / "toolchain") in handed


def test_the_first_failure_stops_the_run_and_names_its_step(tmp_path):
    machine = Machine(failing="install")

    (code, said), _, _ = _first_half(tmp_path, machine)

    assert code != 0
    assert "stopped at step 'install'" in said
    assert machine.asked("studyforge.skills.onboarding") == []


def test_an_installed_library_that_stops_stops_the_run_at_the_hand_over(tmp_path):
    machine = Machine(failing="--installed")

    (code, said), _, _ = _first_half(tmp_path, machine)

    assert code != 0 and "stopped at step 'hand-over'" in said


def test_a_build_that_leaves_no_wheel_is_refused_by_name(tmp_path):
    machine = Machine()

    def without_wheel(argv, cwd):
        return (0, "") if "wheel" in argv else machine(argv, cwd)

    (code, said), _, _ = _first_half(tmp_path, without_wheel)

    assert code != 0 and "stopped at step 'wheel'" in said
    assert machine.asked("install") == []


# --- the second half: inside the installed library --------------------------


@pytest.fixture
def installed(monkeypatch):
    """The library this test imports, answering as a wheel built from `HEAD`."""
    monkeypatch.setattr(library, "commit", lambda *_: HEAD)
    built: list[Path] = []
    monkeypatch.setattr(repin, "build_site", lambda root, out: built.append(root) or 0)
    return built


def _second_half(root, machine, *more):
    return _main(["../framework", "--root", str(root), "--installed", HEAD, *more], machine)


def test_inside_the_installed_library_the_pin_moves_with_every_stub(tmp_path, installed):
    root = _onboarded(tmp_path)

    code, said = _second_half(root, Machine())

    assert code == 0, said
    pinned = json.loads((root / PIN_FILE).read_text(encoding="utf-8"))
    assert pinned["commit"] == HEAD
    assert all(f"pin: {HEAD}" in (root / where).read_text("utf-8") for where in stub_paths())
    assert hand_edited(root) == []
    assert installed == [root]


def test_a_library_built_from_another_commit_is_refused_before_the_pin_moves(
    tmp_path, installed, monkeypatch
):
    root = _onboarded(tmp_path)
    monkeypatch.setattr(library, "commit", lambda *_: "c" * 40)

    code, said = _second_half(root, Machine())

    assert code != 0 and "stopped at step 'pin'" in said
    assert json.loads((root / PIN_FILE).read_text("utf-8"))["commit"] == corpora.COMMIT
    assert installed == []


def test_a_corpus_with_no_runtimes_writes_no_execution_and_brings_nothing_up(tmp_path, installed):
    root = _onboarded(tmp_path)
    machine = Machine()

    code, said = _second_half(root, machine, "--up")

    assert code == 0, said
    assert "declares no runtimes" in said
    assert machine.asked("compose") == []
    assert not (root / ".studyforge/execution").exists()


def test_the_audit_runs_the_corpus_own_ingest_with_the_date_given(tmp_path, installed):
    root = _onboarded(tmp_path)
    machine = Machine()

    code, said = _second_half(root, machine, "--audit-date", "2026-01-02")

    assert code == 0, said
    assert machine.calls == [[sys.executable, "-m", "ingest", ".", "2026-01-02"]]


def test_a_build_that_fails_stops_before_the_audit(tmp_path, installed, monkeypatch):
    root = _onboarded(tmp_path)
    monkeypatch.setattr(repin, "build_site", lambda root, out: 1)
    machine = Machine()

    code, said = _second_half(root, machine, "--audit-date", "2026-01-02")

    assert code != 0 and "stopped at step 'build'" in said
    assert machine.calls == []


def test_a_framework_function_that_raises_stops_the_run_naming_its_step(
    tmp_path, installed, monkeypatch
):
    # ⛔ A traceback names this module; the operator needs the step.
    root = _onboarded(tmp_path)

    def refuses(root, out):
        raise RuntimeError("an index with no section")

    monkeypatch.setattr(repin, "build_site", refuses)

    code, said = _second_half(root, Machine())

    assert code != 0
    assert "RuntimeError: an index with no section" in said
    assert "stopped at step 'build'" in said


def test_a_corpus_with_no_manifest_is_refused_without_naming_its_directory(tmp_path):
    # ⛔ An OSError formats itself with the full path; a refusal names the file alone (R7).
    root = tmp_path / "private-corpus"
    root.mkdir()

    with pytest.raises(ValueError) as refusal:
        repin.runtimes_of(root)

    assert "corpus.json" in str(refusal.value) and str(tmp_path) not in str(refusal.value)


def test_a_toolchain_with_no_consuming_file_is_refused_without_naming_it(tmp_path):
    root = _onboarded(tmp_path)
    toolchain = tmp_path / "private-toolchain"
    toolchain.mkdir()

    with pytest.raises(repin.Stopped) as refusal:
        repin.write_execution(root, toolchain, None, Machine())

    assert "consuming.json" in str(refusal.value) and str(tmp_path) not in str(refusal.value)


def test_a_dry_run_prints_the_prune_for_this_corpus_project(tmp_path):
    root = _onboarded(tmp_path)

    _, said = _main(["../framework", "--root", str(root), "--dry-run", "--up"], Machine())

    assert "label=com.local.compose.project=studyforge-walkthrough" in said


def test_a_runnable_corpus_with_no_toolchain_is_refused_by_name(tmp_path, installed, monkeypatch):
    root = _onboarded(tmp_path)
    monkeypatch.setattr(repin, "runtimes_of", lambda root: ("python",))

    code, said = _second_half(root, Machine())

    assert code != 0 and "stopped at step 'execution'" in said
    assert "--toolchain" in said


def test_with_up_a_runnable_corpus_is_staged_built_pruned_and_brought_up_in_order(
    tmp_path, installed, monkeypatch
):
    root = _onboarded(tmp_path)
    monkeypatch.setattr(repin, "runtimes_of", lambda root: ("python",))
    executed: list[Path] = []
    monkeypatch.setattr(
        repin, "write_execution", lambda root, toolchain, platform, run: executed.append(toolchain)
    )
    staged: list[Path] = []
    monkeypatch.setattr(repin, "stage_site", lambda root: staged.append(root))
    machine = Machine()

    code, said = _second_half(root, machine, "--toolchain", "../toolchain", "--up")

    assert code == 0, said
    assert executed == [Path("../toolchain")] and staged == [root]
    build, prune, up = machine.calls
    assert build == compose_argv("build", "site")
    assert prune[:3] == ["docker", "image", "prune"]
    assert up == compose_argv("up", "-d", "--wait")


def test_a_failed_compose_build_never_prunes_or_brings_up(tmp_path, installed, monkeypatch):
    root = _onboarded(tmp_path)
    monkeypatch.setattr(repin, "runtimes_of", lambda root: ("python",))
    monkeypatch.setattr(repin, "write_execution", lambda *_: None)
    monkeypatch.setattr(repin, "stage_site", lambda root: None)
    machine = Machine(failing="build")

    code, said = _second_half(root, machine, "--toolchain", "../toolchain", "--up")

    assert code != 0 and "stopped at step 'compose-up'" in said
    assert len(machine.calls) == 1
