"""Mirror of `src/studyforge/skills/execution/siteservice.py` (R12): the site and its runner.

⭐ Read off the compose file the skill writes, the way a reader's `docker compose`
reads it: the site on loopback at the one recorded port, the runner on an
internal network with no port and no socket, and the editor off that network.
"""

from __future__ import annotations

import re

import pytest

from studyforge.execute import instance as names
from studyforge.execute import published
from studyforge.serve.app import DEFAULT_PORT
from studyforge.skills.execution import onboard, siteservice
from studyforge.skills.execution.contract import ContractRefused
from tests.studyforge.skills.execution.contracts import editor_contract
from tests.studyforge.skills.execution.test_instance import compose_of, generated


def service_block(text: str, name: str) -> str:
    """The lines of one service in the rendered file, up to the next service or top key."""
    found = re.search(rf"^  {name}:\n((?:    .*\n|      .*\n)+)", text, flags=re.MULTILINE)
    assert found, f"the file renders no {name} service"
    return found.group(1)


@pytest.fixture
def text(tmp_path) -> str:
    return compose_of(generated(tmp_path)[0])


def test_the_file_renders_a_site_beside_the_editor_and_the_runner(text):
    for name in ("editor", "runner", "site"):
        service_block(text, name)


def test_the_site_is_published_on_loopback_at_the_one_recorded_port_inside_and_out(text):
    site = service_block(text, "site")
    port = f"${{{names.SITE_PORT}:-{names.DEFAULT_SITE_PORT}}}"
    assert f'"127.0.0.1:{port}:{port}"' in site
    assert f'- "{port}"' in site and "--published" in site


def test_the_site_learns_the_editor_origin_from_the_editors_recorded_port(text):
    site = service_block(text, "site")
    assert f'{published.EDITOR_ORIGIN}: "http://127.0.0.1:${{{names.EDITOR_PORT}:-8443}}"' in site
    assert f"{published.RUN_SERVICE}: runner" in site
    assert f'{published.EDITOR_HEALTH}: "http://editor:8080/healthz"' in site


def test_the_runner_joins_only_the_internal_network_publishes_nothing_and_runs_the_service(text):
    runner = service_block(text, "runner")
    assert "ports:" not in runner
    assert "network_mode" not in runner
    assert re.search(r"networks:\n\s+- runs\n", runner)
    assert f"./{siteservice.SCRIPT_FILE}:{siteservice.SCRIPT_INSIDE}:ro" in runner
    assert re.search(r"^networks:\n  runs:\n    internal: true$", text, flags=re.MULTILINE)


def test_the_editor_never_joins_the_network_the_runner_answers_on(text):
    editor = service_block(text, "editor")
    assert "networks:" not in editor, "the editor stays on the default network alone"


def test_no_service_names_the_docker_socket(text):
    assert "docker.sock" not in text
    assert "/var/run" not in text


def test_the_site_is_in_a_profile_so_an_unstaged_corpus_still_brings_up_the_other_two(text):
    site = service_block(text, "site")
    assert f'image: "${{{siteservice.IMAGE}:-}}"' in site
    assert re.search(r"profiles:\n\s+- site\n", site)


def test_the_published_skill_files_are_the_service_script_and_the_list_ignore(tmp_path):
    made, _ = generated(tmp_path)
    files = dict(made.files)
    assert files[f"{onboard.DIRECTORY}/{siteservice.SCRIPT_FILE}"] == (
        published.run_service_script()
    )
    assert files[f"{published.ALLOWED_DIR}/.gitignore"] == published.ALLOWED_IGNORE


def test_the_editor_binds_the_site_hands_a_page_are_the_editors_own(tmp_path):
    made, _ = generated(tmp_path)
    site = service_block(compose_of(made), "site")
    declared = re.search(rf"{published.EDITOR_BINDS}: (.*)\n", site).group(1).strip('"')
    parsed = published.from_environment({published.EDITOR_BINDS: declared}).binds
    editor = service_block(compose_of(made), "editor")
    for base, inside in parsed:
        assert f"../../{base}:{inside}" in editor, (base, inside)


@pytest.mark.parametrize(
    ("command", "url"),
    [
        (
            ["CMD", "node", "-e", "fetch('http://127.0.0.1:8080/healthz')"],
            "http://editor:8080/healthz",
        ),
        (["CMD", "node", "-e", "fetch('/ready')"], "http://editor:8080/ready"),
        (["CMD", "true"], "http://editor:8080/"),
    ],
)
def test_the_editors_health_is_asked_by_service_name_at_its_own_path(command, url):
    block = editor_contract()["editor"]
    block["healthcheck"] = {"command": command}
    assert siteservice.health_url(block) == url


def test_an_editor_with_no_per_project_port_is_refused():
    block = editor_contract()["editor"]
    for entry in block["ports"]:
        entry["per_project"] = False
    with pytest.raises(ContractRefused):
        siteservice.plan(block, source="demo", sources="src", extra=(), runner=("runner", {}))


def test_the_default_site_port_is_the_one_serve_listens_on_by_default():
    assert names.DEFAULT_SITE_PORT == DEFAULT_PORT


def test_a_preflight_checks_the_publishers_values_before_every_other_service(text):
    check = service_block(text, siteservice.PREFLIGHT)
    assert re.search(r"command:\n\s+- preflight\n\s+- /corpus\n", check)
    assert '"../..:/corpus:ro"' in check, "the preflight reads the corpus and writes nothing"
    assert 'network_mode: "none"' in check or "network_mode: none" in check
    assert re.search(r"profiles:\n\s+- site\n", check)
    for name in ("editor", "runner", "site"):
        gated = service_block(text, name)
        assert re.search(
            r"depends_on:\n\s+preflight:\n\s+condition: service_completed_successfully\n"
            r'\s+required: "\$\{STUDYFORGE_PREFLIGHT:-false\}"\n',
            gated,
        ), name
    assert "depends_on" not in check


def test_the_site_is_healthy_only_once_its_published_route_answers(text):
    # ⭐ `up --wait` reads this: a running process is not an answering site.
    site = service_block(text, "site")
    port = f"${{{names.SITE_PORT}:-{names.DEFAULT_SITE_PORT}}}"
    probe = f"urllib.request.urlopen('http://127.0.0.1:{port}/', timeout=2)"
    assert re.search(r"healthcheck:\n\s+test:\n\s+- CMD\n\s+- python3\n\s+- -c\n", site), site
    assert probe in site
    assert re.search(r"start_interval: \"?1s\"?\n", site)
