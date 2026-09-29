"""Mirror of `src/studyforge/skills/execution/standalone/compose.py` (R12).

⭐ Read against the synthetic editor contract `contracts.py` builds and four
toolchain builds shaped as `consuming/builds.py` prints them. ⭐ Where Docker
is on the host, compose itself reads both files (`config -q`), since a YAML this
framework emits is only as valid as the engine that parses it says.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess

import pytest

from studyforge.skills.execution.emit import emit
from studyforge.skills.execution.standalone import compose, images
from tests.studyforge.skills.execution import contracts

#: The four builds, as the toolchain prints them: only the keys the renderer reads.
BUILDS = {
    "runner": {
        "tag": "example/runner:java-maven-amd64-0123456789ab",
        "dockerfile": "docker/minimal/Dockerfile",
        "target": "runner",
        "args": {"CHECKS": "java|java -version|25\nmaven|mvn -v|3", "RUNNER_HOME": "/tmp"},
        "built_here": {},
    },
    "editor": {
        "tag": "example/editor:java-maven-amd64-ba9876543210",
        "dockerfile": "docker/editor/Dockerfile",
        "target": "editor",
        "args": {"RUNNER_IMAGE": "example/runner:x", "PROFILE_D": "export PATH=/opt/x:$PATH"},
        "built_here": {"RUNNER_IMAGE": "runner"},
    },
    "runner-prime": {
        "tag": "example/runner:x-prime-1",
        "dockerfile": "docker/prime/Dockerfile",
        "target": "runner-prime",
        "args": {"BASE_IMAGE": "example/runner:x", "WITH_MAVEN_PRIME": "yes"},
        "built_here": {"BASE_IMAGE": "runner"},
    },
    "editor-prime": {
        "tag": "example/editor:x-prime-1",
        "dockerfile": "docker/prime/Dockerfile",
        "target": "editor-prime",
        "args": {"BASE_IMAGE": "example/editor:x", "WITH_MAVEN_PRIME": "yes"},
        "built_here": {"BASE_IMAGE": "editor"},
    },
}


def plan(**changes) -> compose.Plan:
    names = images.names_for(slug="a-course", course="c0ffee", serve="0.1.0-abc", builds=BUILDS)
    made = {
        "slug": "a-course",
        "names": names,
        "builds": BUILDS,
        "editor": contracts.editor_contract()["editor"],
        "runtimes": ("java", "maven"),
        "binds": (
            (".studyforge/execution/code", f"{contracts.WORKSPACE}/sources"),
            ("practice", f"{contracts.WORKSPACE}/practice"),
        ),
        "site_port": 18772,
        "editor_port": 18444,
    }
    made.update(changes)
    return compose.Plan(**made)


@pytest.fixture(scope="module")
def rendered() -> tuple[str, str]:
    return compose.render(plan())


def test_both_files_run_the_same_three_services_and_only_one_builds(rendered):
    built, pulled = rendered
    for name in ("site:", "runner:", "editor:"):
        assert f"\n  {name}\n" in built and f"\n  {name}\n" in pulled
    assert "build:" not in pulled
    assert built.count("scale: 0") == 4
    for base in ("serve-base", "runner-base", "editor-base", "runner-prime"):
        assert f"\n  {base}:\n" in built and f"\n  {base}:\n" not in pulled


def test_every_port_is_on_loopback_and_every_mount_is_a_named_volume(rendered):
    for text in rendered:
        assert "0.0.0.0:" not in text.replace("--bind-addr=0.0.0.0:8080", "")
        assert "127.0.0.1:${COURSE_SITE_PORT:-18772}:${COURSE_SITE_PORT:-18772}" in text
        assert "127.0.0.1:${COURSE_EDITOR_PORT:-18444}:8080" in text
        assert "docker.sock" not in text
        for line in text.splitlines():
            if line.strip().startswith('- "') and ":/" in line:
                assert not line.strip()[3].startswith((".", "/", "~", "$")), line


def test_a_bases_image_is_read_through_a_named_context_never_pulled(rendered):
    built, _ = rendered
    assert "RUNNER_IMAGE: studyforge-runner-base" in built
    assert 'studyforge-runner-base: "service:runner-base"' in built
    assert 'studyforge-editor-base: "service:editor-base"' in built
    assert 'studyforge-serve-base: "service:serve-base"' in built
    assert "example/runner:x" not in built


def test_a_toolchain_argument_is_passed_as_written(rendered):
    built, _ = rendered
    assert 'PROFILE_D: "export PATH=/opt/x:$$PATH"' in built
    assert 'CHECKS: "java|java -version|25\\nmaven|mvn -v|3"' in built


def test_every_service_runs_as_the_uid_its_volumes_are_seeded_for(rendered):
    for text in rendered:
        assert text.count('user: "1000:1000"') == 3
        assert "HOST_UID" not in text


def test_the_runner_and_the_editor_wait_for_the_site_that_seeds_their_volumes(rendered):
    _, pulled = rendered
    assert pulled.count("condition: service_healthy") == 2


def test_the_findings_catch_a_host_bind_an_open_port_and_a_socket():
    services = {
        "site": {"volumes": ["./course:/corpus"], "ports": ["0.0.0.0:8772:8772"]},
        "runner": {"volumes": ["/var/run/docker.sock:/var/run/docker.sock"]},
    }
    found = compose.findings(emit({"services": services}), services)
    assert any("host path" in one for one in found)
    assert any("off loopback" in one for one in found)
    assert any("socket" in one for one in found)
    clean = {"site": {"volumes": ["code:/corpus/x"], "ports": ["127.0.0.1:1:1"]}}
    assert compose.findings(emit({"services": clean}), clean) == []


def test_a_rendered_file_that_would_break_a_rule_is_refused():
    editor = contracts.editor_contract()["editor"]
    wide = json.loads(json.dumps(editor))
    wide["ports"][0]["host_bind"] = "0.0.0.0"
    with pytest.raises(ValueError):
        compose.render(plan(editor=wide))


@pytest.mark.skipif(shutil.which("docker") is None, reason="no docker CLI on this host")
def test_compose_itself_reads_both_files(tmp_path, rendered):
    env = {
        **os.environ,
        "CODE_SERVER_PASSWORD": "synthetic",
        images.NAMESPACE_VARIABLE: "example-account",
    }
    for name, text in zip(("compose.yaml", "compose.pull.yaml"), rendered, strict=True):
        (tmp_path / name).write_text(text, encoding="utf-8")
        (tmp_path / ".studyforge" / "images" / "toolchain" / "no-prime").mkdir(
            parents=True, exist_ok=True
        )
        (tmp_path / ".studyforge" / "execution" / "prime").mkdir(parents=True, exist_ok=True)
        checked = subprocess.run(
            ["docker", "compose", "-f", name, "config", "-q"],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if checked.returncode != 0 and "Cannot connect" in checked.stderr:
            pytest.skip("docker is installed and no engine answers")
        assert checked.returncode == 0, checked.stderr


def defaults_the_account(text: str) -> bool:
    """Whether a compose text falls back to an account when the variable is unset."""
    return f"${{{images.NAMESPACE_VARIABLE}:-" in text


def test_the_pull_file_has_no_default_account_and_the_build_file_keeps_the_local_one(rendered):
    built, pulled = rendered
    assert not defaults_the_account(pulled)
    assert defaults_the_account(built)
    assert f"${{{images.NAMESPACE_VARIABLE}:?" in pulled
    assert f"${{{images.NAMESPACE_VARIABLE}:-{images.NAMESPACE_DEFAULT}}}/" in built
    assert pulled.count(compose.NAMESPACE_REQUIRED) == 3


def test_the_pull_file_s_message_names_the_variable_and_the_account_it_holds():
    message = compose.NAMESPACE_REQUIRED
    assert message.startswith(images.NAMESPACE_VARIABLE)
    assert "Docker Hub account" in message and "published under" in message
    assert "}" not in message and '"' not in message


def test_a_pull_file_that_kept_a_default_would_be_caught(rendered):
    _, pulled = rendered
    planted = pulled.replace(
        f"${{{images.NAMESPACE_VARIABLE}:?{compose.NAMESPACE_REQUIRED}}}",
        f"${{{images.NAMESPACE_VARIABLE}:-{images.NAMESPACE_DEFAULT}}}",
    )
    assert defaults_the_account(planted)


@pytest.mark.skipif(shutil.which("docker") is None, reason="no docker CLI on this host")
@pytest.mark.parametrize("env_file", [None, f"{images.NAMESPACE_VARIABLE}=\n"])
def test_compose_refuses_the_pull_file_with_the_message_until_the_account_is_set(
    tmp_path, rendered, env_file
):
    (tmp_path / "compose.pull.yaml").write_text(rendered[1], encoding="utf-8")
    if env_file is not None:
        (tmp_path / ".env").write_text(env_file, encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != images.NAMESPACE_VARIABLE}
    env["CODE_SERVER_PASSWORD"] = "synthetic"
    refused = subprocess.run(
        ["docker", "compose", "-f", "compose.pull.yaml", "config", "-q"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert refused.returncode != 0
    assert images.NAMESPACE_VARIABLE in refused.stderr
    assert "Docker Hub account" in refused.stderr
