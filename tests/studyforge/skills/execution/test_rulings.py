"""Mirror of `src/studyforge/skills/execution/rulings.py` (R12).

⛔ **Each of spec §8.1's four rulings, and §8.3's, is asserted rather than
remembered** — and each is asserted BOTH WAYS: the clean block reports nothing,
and a block with that one ruling planted in it reports exactly that ruling.
⭐ A renderer that only ever saw clean contracts could not tell you its checks
do anything.
"""

from __future__ import annotations

import copy

import pytest

from studyforge.skills.execution import rulings
from studyforge.skills.execution.contract import ContractRefused
from tests.studyforge.skills.execution.contracts import (
    HOME,
    editor_contract,
    narration_contract,
)


def editor() -> dict:
    """The synthetic editor block, which breaks no ruling."""
    return editor_contract()["editor"]


def test_a_block_that_breaks_no_ruling_reports_nothing():
    assert rulings.findings(editor(), name="editor") == ()
    assert rulings.findings(narration_contract()["service"], name="narrate") == ()


@pytest.mark.parametrize("bind", rulings.EVERY_INTERFACE)
def test_loopback_a_port_published_on_every_interface_is_reported(bind):
    block = editor()
    block["ports"][0]["host_bind"] = bind
    found = rulings.findings(block, name="editor")
    assert len(found) == 1 and "to loopback only" in found[0]


def test_loopback_is_also_reported_when_the_contract_says_so_in_its_own_flag():
    block = editor()
    block["ports"][0]["publish_on_all_interfaces"] = True
    assert any("to loopback only" in one for one in rulings.findings(block, name="editor"))


def test_loopback_reaches_the_narration_block_too():
    # ⭐ §8.1 names that service as publishing on all interfaces TODAY and says
    # it is to be fixed rather than copied, so it is on trial here as well.
    block = narration_contract()["service"]
    block["ports"][0]["host_bind"] = "0.0.0.0"
    assert any("to loopback only" in one for one in rulings.findings(block, name="narrate"))


@pytest.mark.parametrize("host_path", rulings.NEVER_BOUND)
def test_sources_only_a_bind_of_the_repository_or_a_home_is_reported(host_path):
    block = editor()
    block["mounts"][0]["host_path"] = host_path
    assert any("only the sources" in one for one in rulings.findings(block, name="editor"))


def test_sources_only_a_second_per_project_bind_is_reported():
    block = editor()
    block["mounts"].append(copy.deepcopy(block["mounts"][0]))
    found = [one for one in rulings.findings(block, name="editor") if "only the sources" in one]
    assert found and "2 per-project binds" in found[0]


def test_sources_only_no_per_project_bind_at_all_is_reported():
    block = editor()
    block["mounts"][0]["per_project"] = False
    assert any("only the sources" in one for one in rulings.findings(block, name="editor"))


def test_owner_uid_a_block_that_binds_and_names_no_uid_is_reported():
    block = editor()
    del block["runs_as"]["compose_value"]
    assert any("uid:gid" in one for one in rulings.findings(block, name="editor"))


def test_owner_uid_does_not_fire_on_a_block_that_binds_nothing():
    # ⚠️ Both directions. A service with no bind writes into no host directory,
    # so the ruling has nothing to be about and a finding there would be noise.
    block = editor()
    block["mounts"] = [one for one in block["mounts"] if one["kind"] != "bind"]
    assert rulings.findings(block, name="editor") == ()


def test_owner_uid_accepts_a_run_value_where_a_block_is_consumed_by_a_run_line():
    block = editor()
    block["runs_as"] = {"user": "coder", "run_value": "$(id -u):$(id -g)"}
    assert not [one for one in rulings.findings(block, name="editor") if "uid:gid" in one]


def test_bind_source_first_a_bind_that_need_not_exist_first_is_reported():
    block = editor()
    block["mounts"][0]["must_exist_before_start"] = False
    found = [one for one in rulings.findings(block, name="editor") if "before the start" in one]
    assert found and "root-owned" in found[0]


def test_section_8_3_a_declared_socket_is_reported():
    block = editor()
    block["docker_socket"] = True
    assert any("§8.3" in one for one in rulings.findings(block, name="editor"))


@pytest.mark.parametrize("path", rulings.SOCKET_PATHS)
def test_section_8_3_a_socket_smuggled_in_as_a_mount_is_reported(path):
    # ⛔ Not behind a flag and not "only locally": a block that declares
    # `docker_socket: false` and then binds the socket is the shape that check
    # would otherwise miss entirely.
    block = editor()
    block["mounts"].append(
        {
            "container_path": "/var/run/docker.sock",
            "kind": "bind",
            "host_path": path,
            "per_project": False,
            "required": True,
            "must_exist_before_start": True,
        }
    )
    assert any("§8.3" in one for one in rulings.findings(block, name="editor"))


def test_the_socket_reading_over_bytes_answers_both_ways():
    assert rulings.names_a_socket(f"- /var/run/docker.sock:{HOME}/docker.sock")
    assert not rulings.names_a_socket(f"- {HOME}/.config:/config")


def test_a_block_missing_a_list_the_rulings_need_is_refused_rather_than_passed():
    # ⛔ A contract with no `ports` key is not a contract that publishes
    # nothing; it is a contract this renderer has not read (R19).
    block = editor()
    del block["ports"]
    with pytest.raises(ContractRefused, match="ports"):
        rulings.findings(block, name="editor")


def test_the_name_reaches_every_finding_so_a_reader_knows_which_block_broke_it():
    block = editor()
    block["ports"][0]["host_bind"] = "0.0.0.0"
    block["docker_socket"] = True
    found = rulings.findings(block, name="the-editor")
    assert len(found) == 2 and all(one.startswith("the-editor ") for one in found)
