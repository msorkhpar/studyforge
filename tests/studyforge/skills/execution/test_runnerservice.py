"""Mirror of `src/studyforge/skills/execution/runnerservice.py` (R12) — `W445`'s runner.

⛔ Every value of the rendered service is the contract's, and the one that
matters most is asserted against the framework's OTHER spelling of it: the
container name `execute.commands.container_for` looks a Submit's runner up by.
"""

from __future__ import annotations

import pytest

from studyforge.execute import container_for
from studyforge.skills.execution import runnerservice
from studyforge.skills.execution.contract import ContractRefused
from tests.studyforge.skills.execution.contracts import editor_contract, runner_block

#: Where the compose file reaches the corpus's root.
ROOT = "../.."


def planned(source: str = "demo", **moved: object) -> runnerservice.Runner:
    document = editor_contract(runner=runner_block(**moved))
    return runnerservice.plan(
        document,
        source=source,
        root=ROOT,
        runtimes=("java", "maven"),
        runs_as=document["editor"]["runs_as"],
    )


@pytest.mark.parametrize("source", ["demo", "iso-like-source-1"])
def test_the_container_is_named_exactly_as_execute_looks_it_up(source):
    # ⛔ Two spellings of one name: if they came apart every Submit would
    # silently run on the host, and nothing would fail.
    made = planned(source)
    assert made.name == container_for(source)
    assert made.service["container_name"] == container_for(source)


def test_the_image_is_the_runner_blocks_own_variable_and_never_a_tag():
    image = planned().service["image"]
    assert isinstance(image, str) and image.startswith("${STUDYFORGE_RUNNER_IMAGE:?")
    assert "example/runner:" not in image


def test_the_source_root_is_bound_where_the_contract_says_writable():
    assert planned().service["volumes"] == [f"{ROOT}:/work"]


def test_a_read_only_bind_carries_its_flag():
    mounts = runner_block()["mounts"]
    mounts[0]["read_only"] = True
    assert planned(mounts=mounts).service["volumes"] == [f"{ROOT}:/work:ro"]


def test_it_runs_offline_with_an_init_as_the_sources_owner_and_restarts_never():
    service = planned().service
    assert service["network_mode"] == "none"
    assert service["init"] is True
    assert service["user"] == editor_contract()["editor"]["runs_as"]["compose_value"]
    assert service["restart"] == "no"
    assert "ports" not in service and "command" not in service


def test_a_moved_network_mode_moves_the_output_so_nothing_here_is_a_literal():
    assert planned(network={"mode": "example-none"}).service["network_mode"] == "example-none"


def test_no_init_declared_is_no_init_emitted():
    assert "init" not in planned(init={"enabled": False}).service


def test_the_argv_is_the_runner_blocks_own_with_the_set_in_its_slot():
    made = planned()
    assert made.selection.tag_from == (
        "python3",
        "runner.py",
        "--runtimes",
        "java,maven",
        "--print-tag",
    )
    assert made.repository == "example/runner"
    assert made.prime_flag == "--prime <directory>"


@pytest.mark.parametrize(
    ("moved", "refusal"),
    [
        ({"docker_socket": True}, runnerservice.RunnerRefused),
        (
            {"ports": [{"container": 1, "host": 1, "host_bind": "127.0.0.1"}]},
            runnerservice.RunnerRefused,
        ),
        ({"run": {"name_template": "studyforge-runner"}}, ContractRefused),
        ({"run": {}}, ContractRefused),
        ({"network": {}}, ContractRefused),
    ],
)
def test_a_block_that_breaks_a_ruling_or_lacks_a_key_is_refused(moved, refusal):
    with pytest.raises(refusal):
        planned(**moved)


def test_a_mount_with_no_host_side_this_renderer_knows_is_refused():
    mounts = [dict(runner_block()["mounts"][0], per_project=False)]
    with pytest.raises(runnerservice.RunnerRefused):
        planned(mounts=mounts)


def test_a_bind_that_is_not_the_source_root_slot_is_refused():
    mounts = [dict(runner_block()["mounts"][0], host_path="./elsewhere")]
    with pytest.raises(ContractRefused):
        planned(mounts=mounts)
