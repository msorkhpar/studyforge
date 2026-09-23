"""Mirror of `src/studyforge/skills/execution/composefile.py` and `emit.py` (R12).

⛔ Every value in a rendered file is asserted to be a value the CONTRACT
carries, and each is planted in the contract and watched moving the output.
⭐ That is the claim `TC-05`'s acceptance makes — that a consuming contract is
sufficient to generate a working compose file with no other input — and this is
where it is demonstrated rather than asserted.
"""

from __future__ import annotations

import pytest

from studyforge.skills.execution import composefile, rulings
from studyforge.skills.execution.contract import ContractRefused
from tests.studyforge.skills.execution.contracts import (
    HOME,
    WORKSPACE,
    editor_contract,
    narration_contract,
)

#: What a corpus supplies where the image goes, in these tests.
IMAGE = "${EDITOR_IMAGE:?build it}"

#: Where the corpus's sources are, as the compose file reaches them.
SOURCES = "../../sources"


def editor() -> dict:
    """The synthetic editor block."""
    return editor_contract()["editor"]


def seeds() -> dict:
    """The contract's own runtime-to-volume map."""
    return editor_contract()["runner"]["prime"]["seeds"]


def rendered(**moved: object) -> str:
    """The whole compose file for the synthetic contract."""
    arguments: dict[str, object] = {
        "project": "studyforge-demo",
        "editor": editor(),
        "image": IMAGE,
        "sources": SOURCES,
        "runtimes": ("java", "maven"),
        "seeds": seeds(),
    }
    arguments.update(moved)
    return composefile.render(**arguments)


# --------------------------------------------------------------------------
# What the file carries, and where each value came from
# --------------------------------------------------------------------------


def test_the_image_the_uid_and_the_project_are_what_they_were_given():
    text = rendered()
    assert "name: studyforge-demo" in text
    assert f'image: "{IMAGE}"' in text
    assert 'user: "${HOST_UID:-1000}:${HOST_GID:-1000}"' in text


def test_the_published_port_is_bound_to_loopback_and_to_nothing_else():
    # ⛔ §8.1 ruling 1, in the output rather than in the check.
    assert '- "127.0.0.1:8443:8080"' in rendered()


def test_a_moved_port_moves_the_output_so_nothing_here_is_a_literal():
    block = editor()
    block["ports"][0]["host"] = 9999
    block["ports"][0]["container"] = 7070
    assert '- "127.0.0.1:9999:7070"' in rendered(editor=block)


def test_a_protocol_that_is_not_tcp_is_carried_and_tcp_is_left_implicit():
    block = editor()
    block["ports"][0]["protocol"] = "udp"
    assert "8443:8080/udp" in rendered(editor=block)
    assert "/tcp" not in rendered()


def test_the_only_host_directory_it_mounts_is_the_sources():
    text = rendered()
    assert f'- "{SOURCES}:{WORKSPACE}/sources"' in text
    # ⚠️ The mount lines alone: the ruling-4 footer names the same host path
    # on purpose, and counting it would read one directory as two.
    hosts = [
        line
        for line in text.splitlines()
        if line.startswith('      - "') and ("./" in line or "../" in line)
    ]
    assert hosts == [f'      - "{SOURCES}:{WORKSPACE}/sources"'], hosts


def test_a_read_only_mount_carries_its_flag_and_a_writable_one_does_not():
    block = editor()
    block["mounts"][1]["read_only"] = True
    assert f'"editor-config:{HOME}/.config:ro"' in rendered(editor=block)
    assert ":ro" not in rendered()


def test_the_workspace_root_is_the_tmpfs_the_contract_declares():
    assert f"    tmpfs:\n      - {WORKSPACE}\n" in rendered()


def test_a_workspace_that_is_not_a_tmpfs_emits_none():
    block = editor()
    block["workspace"]["kind"] = "bind"
    assert "tmpfs:" not in rendered(editor=block)


def test_the_command_replaces_the_images_cmd_outright_and_is_the_contracts_own():
    text = rendered()
    assert "      - --auth=password\n" in text
    assert f"      - {WORKSPACE}\n" in text


def test_a_required_variable_with_no_default_arrives_as_the_contracts_interpolation():
    assert 'PASSWORD: "${CODE_SERVER_PASSWORD:?set it before starting}"' in rendered()


def test_a_required_variable_with_neither_a_default_nor_a_compose_value_is_refused():
    # ⛔ Nothing says what a rendered file writes there, so this renderer will
    # not invent it (R19).
    block = editor()
    del block["environment"][0]["compose_value"]
    with pytest.raises(ContractRefused, match="will not invent it"):
        rendered(editor=block)


def test_the_health_check_is_the_contracts_own_command_and_its_own_intervals():
    text = rendered()
    assert "        - /usr/lib/node\n" in text
    assert "      interval: 60s\n" in text and "      retries: 3\n" in text


def test_a_block_with_no_health_check_emits_none():
    block = editor()
    del block["healthcheck"]
    assert "healthcheck:" not in rendered(editor=block)


def test_the_restart_policy_is_quoted_so_compose_does_not_read_it_as_false():
    # ⚠️ YAML 1.1's `no` is a boolean. Unquoted, this file would declare a
    # restart policy of `False` and compose would refuse it.
    assert '    restart: "no"\n' in rendered()


# --------------------------------------------------------------------------
# The declared set decides which cache volumes appear
# --------------------------------------------------------------------------


def test_a_declared_runtime_earns_its_cache_volume_and_an_undeclared_one_does_not():
    with_maven = rendered(runtimes=("java", "maven"))
    assert f'"maven-repo:{HOME}/.m2"' in with_maven
    assert "gradle-home" not in with_maven
    with_gradle = rendered(runtimes=("gradle", "java"))
    assert f'"gradle-home:{HOME}/.gradle"' in with_gradle
    assert "maven-repo" not in with_gradle


def test_a_corpus_that_declares_neither_gets_the_required_volumes_and_no_others():
    text = rendered(runtimes=())
    assert "editor-config" in text
    assert "gradle-home" not in text and "maven-repo" not in text


def test_every_named_volume_in_a_service_is_declared_at_the_top_level():
    text = rendered()
    mounted = {
        line.strip().removeprefix('- "').split(":")[0]
        for line in text.splitlines()
        if line.startswith('      - "') and ":/" in line
    }
    declared = {
        line.strip().removesuffix(": {}") for line in text.splitlines() if line.endswith(": {}")
    }
    assert {one for one in mounted if not one.startswith("..")} == declared


def test_without_the_seed_map_no_optional_volume_is_earned():
    # ⛔ `SK-09/3`: the join lives in the other block's prime map and the mounts
    # themselves carry no key for it, so a renderer handed no map earns nothing.
    assert composefile.volumes_for(None, ("gradle", "maven")) == ()


# --------------------------------------------------------------------------
# Ruling 4, and §8.3 over the bytes
# --------------------------------------------------------------------------


def test_the_file_names_every_bind_source_that_must_exist_before_the_start():
    text = rendered()
    assert "ruling 4" in text and f"#   - {SOURCES}" in text


def test_the_bind_source_it_names_is_the_host_side_and_never_the_container_side():
    # ⚠️ A reader told to create a path inside the image has been told nothing
    # they can act on.
    assert composefile.must_exist_first(editor(), (), SOURCES) == (SOURCES,)


def test_a_contract_with_nothing_to_create_first_emits_no_footer():
    block = editor()
    block["mounts"][0]["must_exist_before_start"] = False
    block["mounts"][0]["kind"] = "volume"
    block["mounts"][0]["volume"] = "sources"
    assert "ruling 4" not in rendered(editor=block)


def test_a_block_that_breaks_a_ruling_is_refused_before_a_byte_is_emitted():
    block = editor()
    block["ports"][0]["host_bind"] = "0.0.0.0"
    with pytest.raises(composefile.ComposeRefused, match="ruling 1"):
        rendered(editor=block)


def test_a_second_components_block_is_checked_even_though_it_is_not_rendered():
    service = narration_contract()["service"]
    assert "narrate" not in rendered(checked=(("narrate", service),))
    service["ports"][0]["host_bind"] = "0.0.0.0"
    with pytest.raises(composefile.ComposeRefused, match="will not stand beside"):
        rendered(checked=(("narrate", service),))


def test_no_rendered_file_names_the_docker_socket():
    assert not rulings.names_a_socket(rendered())


# --------------------------------------------------------------------------
# `W445` — the practice workspaces bound beside the sources, and the runner
# --------------------------------------------------------------------------

#: The practice workspaces, as the compose file reaches them and where they go.
PRACTICE = ("../../practice", f"{WORKSPACE}/practice")


def test_a_further_bind_is_mounted_writable_beside_the_sources():
    text = rendered(binds=(PRACTICE,))
    assert f'"{SOURCES}:{WORKSPACE}/sources"' in text
    assert f'"{PRACTICE[0]}:{PRACTICE[1]}"' in text


def test_a_further_bind_is_named_in_ruling_4s_footer_by_its_host_side():
    footer = rendered(binds=(PRACTICE,)).split("ruling 4", 1)[1]
    assert f"#   - {SOURCES}" in footer and f"#   - {PRACTICE[0]}" in footer
    assert PRACTICE[1] not in footer
    assert composefile.must_exist_first(editor(), (), "src", also=("practice",)) == (
        "src",
        "practice",
    )


def test_the_runner_is_placed_beside_the_editor_as_it_was_rendered():
    service = {"image": "${RUNNER:?why}", "container_name": "studyforge-runner-demo"}
    text = rendered(runner=("runner", service))
    assert "\n  runner:\n" in text and "container_name: studyforge-runner-demo" in text
    assert text.index("  editor:") < text.index("  runner:")


def test_a_runner_that_names_the_socket_is_refused_over_the_bytes():
    service = {"image": "x", "volumes": ["/var/run/docker.sock:/var/run/docker.sock"]}
    with pytest.raises(composefile.ComposeRefused, match="socket"):
        rendered(runner=("runner", service))
