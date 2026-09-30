"""The reader of the sibling's runner declaration — `container.py`, with no Docker and no sibling.

⭐ **Why this exists.** `container.py` is test support, but it is also the
framework's only reader of how the runner image is RUN, and it reads the
sibling's declaration, never its README prose. A reader of data needs its own
reading asserted both ways — a declaration it accepts, and each way one can be
wrong — or the skip that hides a broken sibling looks exactly like the skip that
means "no Docker here".

⛔ **Every case below builds its own contract in a temp directory.** The real
sibling is read in ONE case, which skips when it is not reachable, so this
module is green in the pinned image and on a host with no sibling checked out.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tests.harness import sibling
from tests.harness.workspace import WORKSPACE_ENV
from tests.studyforge.execute import container

MODULE = Path(container.__file__)


def a_declaration() -> dict:
    """A minimal, valid runner block — the shape the sibling's contract carries."""
    return {
        "image": {"repository": "code-server-toolchain/runner", "run_value": "<tag>"},
        "runs_as": {"run_flag": "--user", "run_value": "$(id -u):$(id -g)", "required": True},
        "workspace": {"container_path": "/work", "kind": "bind"},
        "mounts": [
            {
                "container_path": "/work",
                "kind": "bind",
                "host_path": "<source root>",
                "read_only": False,
                "must_exist_before_start": True,
            }
        ],
        "network": {"mode": "none", "run_flag": "--network"},
        "ports": [],
        "init": {"enabled": True, "run_flag": "--init"},
        "command": [],
        "command_notes": {
            "exec_template": ["docker", "exec", "-w", "/work/<directory>", "<name>", "<command...>"]
        },
        "run": {
            "detached": True,
            "detach_flag": "-d",
            "name_flag": "--name",
            "name_template": "studyforge-runner-<source>",
        },
        "docker_socket": False,
    }


def a_contract(tmp_path: Path, **changes) -> Path:
    """Write a whole contract to `tmp_path`, with top-level keys replaced."""
    contract = {
        "consuming_api": container.CONSUMING_API,
        "provides": container.PROMISE,
        "component": container.SIBLING,
        container.BLOCK: a_declaration(),
    }
    contract.update(changes)
    (tmp_path / container.CONTRACT).write_text(json.dumps(contract), encoding="utf-8")
    return tmp_path


# --- what it accepts, and each way it can be refused ---------------------------------


def test_a_contract_that_promises_what_this_was_built_against_is_read(tmp_path):
    root = a_contract(tmp_path)
    assert container.declaration_reason(root) is None
    assert container.declaration(root) == a_declaration()


def test_a_sibling_that_is_not_there_is_named_rather_than_crashed_on(tmp_path):
    assert "not reachable" in container.declaration_reason(tmp_path)
    assert container.declaration(tmp_path) is None


def test_a_contract_that_is_not_json_is_refused_like_a_missing_one(tmp_path):
    (tmp_path / container.CONTRACT).write_text("{ not json", encoding="utf-8")
    assert "not reachable" in container.declaration_reason(tmp_path)


def test_another_schema_is_refused_by_number(tmp_path):
    root = a_contract(tmp_path, consuming_api=container.CONSUMING_API + 1)
    reason = container.declaration_reason(root)
    assert "schema" in reason and str(container.CONSUMING_API) in reason


def test_a_sibling_that_promises_less_is_refused_rather_than_migrated(tmp_path):
    """R9: the record is the point — a mismatch stops here, it is not worked around."""
    root = a_contract(tmp_path, provides=container.PROMISE - 1)
    reason = container.declaration_reason(root)
    assert "promises" in reason and "R9" in reason


def test_a_sibling_that_promises_more_is_accepted(tmp_path):
    root = a_contract(tmp_path, provides=container.PROMISE + 1)
    assert container.declaration_reason(root) is None


def test_a_contract_with_no_runner_block_says_the_shape_is_not_data(tmp_path):
    root = a_contract(tmp_path, **{container.BLOCK: {}})
    assert "not data" in container.declaration_reason(root)


# --- ⛔ where the contract was READ from -------------------------------------------


def a_local_reading(tmp_path) -> sibling.Reading:
    """A well-formed contract that was read from a working tree and says so."""
    a_contract(tmp_path)
    return sibling.read_directory(tmp_path, container.CONTRACT)


def test_a_contract_read_off_a_working_tree_is_refused_when_the_sibling_was_ours_to_find(tmp_path):
    # ⛔ Mid-merge, a STAGED `consuming.json` on no ref read
    # as present and went green — on this host only. The contract below is
    # perfectly valid; what is refused is WHERE it came from.
    reading = a_local_reading(tmp_path)
    reason = container.reason_for(reading, must_be_committed=True)
    assert reason is not None
    assert "LOCAL" in reason and container.SIBLING in reason


def test_the_same_reading_is_accepted_when_the_caller_named_the_directory(tmp_path):
    # ⭐ The other direction, and it is why the refusal is a parameter rather
    # than a rule: no commit covers a directory somebody handed in, so there is
    # no commit for that reading to fail to be at.
    reading = a_local_reading(tmp_path)
    assert container.reason_for(reading, must_be_committed=False) is None


def test_a_directory_the_caller_named_is_read_and_never_demanded_to_be_committed(tmp_path):
    root = a_contract(tmp_path)
    assert container.contract_reading(root).working_tree
    assert container.declaration_reason(root) is None


def test_an_absent_sibling_is_an_answer_carrying_its_sentence_rather_than_a_crash(tmp_path):
    # ⭐ A clean clone's case, and the pinned image's: no sibling is named, so
    # none resolves at all. It must stay a named skip, in both policies.
    absent = sibling.read_directory(tmp_path, container.CONTRACT)
    assert absent.absent
    for demanded in (True, False):
        reason = container.reason_for(absent, must_be_committed=demanded)
        assert "not reachable" in reason and absent.source in reason


def test_the_real_sibling_is_found_through_the_variable_and_never_by_path(monkeypatch):
    # ⛔ No `root`: this is the resolution the runner cases actually use, and it
    # goes through `STUDYFORGE_WORKSPACE` rather than joining a path onto a parent.
    reading = container.contract_reading()
    assert reading.state in sibling.STATES
    # ⛔ R7: this sentence lands in skip messages, so it carries no path.
    assert str(Path(container.__file__).parent) not in reading.source
    # ⭐ Unset, nothing is guessed: the sibling is absent and the sentence names the variable.
    monkeypatch.delenv(WORKSPACE_ENV, raising=False)
    unset = container.contract_reading()
    assert unset.absent and WORKSPACE_ENV in unset.source


# --- the run it renders --------------------------------------------------------------


def test_every_placeholder_is_filled_and_none_survives_into_the_argv():
    argv = container.run_argv(a_declaration(), name="run-1", source_root="/sources", tag="an-image")
    assert argv[:9] == [
        "docker",
        "run",
        "-d",
        "--name",
        "run-1",
        "--init",
        "--network",
        "none",
        "--user",
    ]
    assert argv[-3:] == ["-v", "/sources:/work", "an-image"]
    for placeholder in ("<tag>", "<source root>", "<source>", "$(id -u):$(id -g)"):
        assert placeholder not in argv


def test_it_runs_as_a_real_uid_gid_and_never_ships_the_shells_substitution():
    """The declaration's value is what a PERSON types; a subprocess has no shell to expand it."""
    argv = container.run_argv(
        a_declaration(), name="n", source_root="/s", tag="t", user="4242:4243"
    )
    assert argv[argv.index("--user") + 1] == "4242:4243"
    assert not any("$" in part for part in argv)


def test_it_publishes_no_port_and_mounts_no_socket():
    argv = container.run_argv(a_declaration(), name="n", source_root="/s", tag="t")
    assert "-p" not in argv and "--publish" not in argv
    assert not any("docker.sock" in part for part in argv)


def test_a_declaration_that_moves_the_workspace_moves_the_mount_with_it():
    """The proof that this reads the data rather than carrying its own copy of /work."""
    moved = a_declaration()
    moved["workspace"]["container_path"] = "/elsewhere"
    moved["mounts"][0]["container_path"] = "/elsewhere"
    argv = container.run_argv(moved, name="n", source_root="/s", tag="t")
    assert "/s:/elsewhere" in argv
    assert "/s:/work" not in argv
    assert container.workspace_path(moved) == "/elsewhere"


def test_a_read_only_bind_is_rendered_read_only():
    declared = a_declaration()
    declared["mounts"][0]["read_only"] = True
    assert "/s:/work:ro" in container.run_argv(declared, name="n", source_root="/s", tag="t")


def test_a_volume_in_the_declaration_is_not_a_bind_and_is_not_mounted():
    declared = a_declaration()
    declared["mounts"].append({"container_path": "/cache", "kind": "volume", "volume": "c"})
    argv = container.run_argv(declared, name="n", source_root="/s", tag="t")
    assert argv.count("-v") == 1


def test_an_undetached_or_uninitialised_declaration_renders_without_those_flags():
    declared = a_declaration()
    declared["run"]["detached"] = False
    declared["init"]["enabled"] = False
    argv = container.run_argv(declared, name="n", source_root="/s", tag="t")
    assert "-d" not in argv and "--init" not in argv


def test_the_exec_template_is_filled_from_the_declaration():
    argv = container.exec_argv(
        a_declaration(), name="run-1", directory="unit-3", command=["mvn", "-q", "test"]
    )
    assert argv == ["docker", "exec", "-w", "/work/unit-3", "run-1", "mvn", "-q", "test"]
    assert "<command...>" not in argv


# --- it reads data, and the real sibling satisfies it --------------------------------


def test_this_module_reads_the_contract_and_parses_no_prose():
    """The README is documentation, not an interface."""
    source = MODULE.read_text(encoding="utf-8")
    body = source.split('"""', 2)[2]
    assert "README" not in body, "the run shape is read from the declaration, never from prose"
    assert container.CONTRACT == "consuming.json"


def test_the_real_sibling_declares_a_shape_this_can_render():
    reason = container.declaration_reason()
    if reason is not None:
        # ⭐ A working-tree-only contract lands here too, and the skip
        # says so rather than letting an unreproducible reading go green.
        pytest.skip(reason)
    assert container.contract_reading().committed
    runner = container.declaration()
    argv = container.run_argv(runner, name="run-probe", source_root="/sources", tag="an-image")
    assert argv[:2] == ["docker", "run"]
    assert "--network" in argv and argv[argv.index("--network") + 1] == "none"
    assert f"/sources:{container.workspace_path(runner)}" in argv
    assert runner["docker_socket"] is False


# --- an image that does not declare what the cases run is skipped by name ------------


def an_image_declaring(monkeypatch, label: str | None) -> None:
    """A named, held image whose runtimes label reads `label`, with no Docker touched."""

    def docker(*arguments: str):
        stdout = "<no value>" if label is None else label
        return subprocess.CompletedProcess(["docker", *arguments], 0, stdout=stdout, stderr="")

    monkeypatch.setenv(container.IMAGE_VARIABLE, "an-image")
    monkeypatch.setattr(container, "tool_on_path", lambda _name: "docker")
    monkeypatch.setattr(container, "_docker", docker)
    monkeypatch.setattr(container, "declaration_reason", lambda: None)


@pytest.mark.parametrize("label", ["java maven", None])
def test_a_runner_that_does_not_declare_python_skips_the_runnable_cases_naming_it(
    monkeypatch, label
):
    """⭐ A java-maven runner has no `python3`: the case skips saying so, never fails."""
    an_image_declaring(monkeypatch, label)
    reason = container.skip_reason(needs=container.RUNNABLE_RUNTIME)
    assert reason is not None and "python" in reason and container.IMAGE_VARIABLE in reason


def test_a_runner_that_declares_python_runs_the_runnable_cases(monkeypatch):
    an_image_declaring(monkeypatch, "java maven python")
    assert container.skip_reason(needs=container.RUNNABLE_RUNTIME) is None
    an_image_declaring(monkeypatch, "java maven")
    assert container.skip_reason() is None, "a case that needs nothing reads no label"
