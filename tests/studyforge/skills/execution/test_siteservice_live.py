"""The live runner and its egress proxy in the compose file, and their absence everywhere else.

Mirrors the live half of `src/studyforge/skills/execution/siteservice.py` (R12). ⭐ Read off the
rendered file as `docker compose` reads it. ⛔ A corpus that declares no live run renders the
bytes it always did: the proof against the earlier tree is a render of both and a comparison of
their hashes; here the same claim is read as properties (no service, network, variable, profile or
script) and as a plant that must turn it red.
"""

from __future__ import annotations

import re

import pytest

from studyforge.execute import published
from studyforge.skills.execution import onboard, siteservice
from tests.studyforge.skills.execution.test_instance import generated
from tests.studyforge.skills.execution.test_siteservice import service_block

LIVE = {
    "host": "api.example.test",
    "key_variable": "EXAMPLE_API_KEY",
    "examples": [{"path": "src/a.py", "command": ["python3", "src/a.py"]}],
}


def made(tmp_path, live=True):
    moved = {"corpus_api": 8, "live": LIVE} if live else {}
    return generated(tmp_path, **moved)[0]


def text_of(tmp_path, live=True) -> str:
    return dict(made(tmp_path, live).files)[onboard.COMPOSE_FILE]


def test_a_corpus_with_no_live_run_renders_no_live_anything(tmp_path):
    result = made(tmp_path, live=False)
    text = dict(result.files)[onboard.COMPOSE_FILE]
    for word in ("live", "egress", "EGRESS", "STUDYFORGE_LIVE", "liverun", "proxy", "PROXY"):
        assert word not in text, word
    assert not any(where.endswith(("liverun.pl", "egress.py")) for where, _ in result.files)
    assert re.search(r"^networks:\n  runs:\n    internal: true\n", text, flags=re.M)
    assert text.count("internal: true") == 1


def test_plan_with_no_live_is_the_plan_it_always_was(tmp_path):
    from tests.studyforge.skills.execution.test_siteservice import editor_contract

    block = editor_contract()["editor"]
    args = {"source": "demo", "sources": "src", "extra": (), "runner": ("runner", {"image": "x"})}
    assert siteservice.plan(block, **args) == siteservice.plan(block, live=None, **args)


def test_a_declaring_corpus_gets_a_live_runner_and_a_proxy_in_the_live_profile_only(tmp_path):
    text = text_of(tmp_path)
    for name in (siteservice.LIVE, siteservice.EGRESS):
        block = service_block(text, name)
        assert re.search(r"profiles:\n\s+- live\n", block)
        assert "ports:" not in block, f"{name} publishes nothing"
    for name in ("editor", "runner", "site", "preflight"):
        assert "- live\n" not in service_block(text, name).split("profiles:")[-1][:20]


def test_the_live_runner_is_hardened_reaches_only_runs_and_the_proxy_reads_only(tmp_path):
    live = service_block(text_of(tmp_path), siteservice.LIVE)
    assert "read_only: true" in live and "- ALL" in live and "no-new-privileges:true" in live
    assert re.search(r"ulimits:\n\s+core: 0\n", live)
    for limit in ("mem_limit", "pids_limit", "cpus"):
        assert limit in live
    assert re.search(r"networks:\n\s+- runs\n\s+- live-net\n", live)
    assert "network_mode" not in live
    volumes = re.search(r"volumes:\n((?:\s+- .*\n)+)", live).group(1)
    assert all(line.strip().strip('"').endswith(":ro") for line in volumes.splitlines())
    assert "perl" in live and siteservice.LIVE_SCRIPT_INSIDE in live


def test_the_proxy_joins_the_internal_network_and_the_routed_one_and_allows_one_host(tmp_path):
    text = text_of(tmp_path)
    egress = service_block(text, siteservice.EGRESS)
    assert re.search(r"networks:\n\s+- live-net\n\s+- live-out\n", egress)
    assert "EGRESS_ALLOW_HOST: api.example.test" in egress and "read_only: true" in egress
    nets = text.split("\nnetworks:\n")[1]
    assert re.search(r"live-net:\n\s+internal: true", nets)
    assert "live-out:" in nets and nets.count("internal: true") == 2


def test_nothing_but_the_live_runner_and_the_proxy_joins_the_new_networks(tmp_path):
    text = text_of(tmp_path)
    for name in ("editor", "runner", "site"):
        assert "live-net" not in service_block(text, name)
        assert "live-out" not in service_block(text, name)


def test_the_graded_runner_is_exactly_what_it_was_and_has_no_key_name_or_proxy(tmp_path):
    with_live, without = text_of(tmp_path / "a"), text_of(tmp_path / "b", live=False)
    assert service_block(with_live, "runner") == service_block(without, "runner")
    runner = service_block(with_live, "runner")
    for word in ("EXAMPLE_API_KEY", "PROXY", "proxy", "STUDYFORGE_LIVE"):
        assert word not in runner


def test_the_key_variable_is_a_name_the_live_runner_holds_and_no_value_is_written(tmp_path):
    result = made(tmp_path)
    text = dict(result.files)[onboard.COMPOSE_FILE]
    assert "STUDYFORGE_LIVE_KEY_NAME: EXAMPLE_API_KEY" in service_block(text, "live")
    assert text.count("EXAMPLE_API_KEY") == 1
    assert "sk-" not in text and "${EXAMPLE_API_KEY" not in text


def test_the_site_is_told_where_the_live_runner_is_and_only_then(tmp_path):
    assert f"{published.LIVE_SERVICE}: live" in service_block(text_of(tmp_path), "site")
    assert published.LIVE_SERVICE not in text_of(tmp_path / "b", live=False)


def test_the_two_scripts_are_written_beside_the_compose_only_for_a_declaring_corpus(tmp_path):
    result = made(tmp_path)
    written = dict(result.files)
    assert written[f"{onboard.DIRECTORY}/liverun.pl"] == published.live_runner_script()
    assert written[f"{onboard.DIRECTORY}/egress.py"] == published.egress_proxy_script()
    assert "STUDYFORGE_LIVE_KEY_NAME" in published.live_runner_script()
    assert siteservice.files("d", "x") == siteservice.files("d", "x", False)
    assert len(siteservice.files("d", "x", True)) == len(siteservice.files("d", "x")) + 2


@pytest.mark.parametrize("word", ["ANTHROPIC", "anthropic"])
def test_no_vendor_is_named_by_the_framework_in_the_live_services(tmp_path, word):
    assert word not in text_of(tmp_path)
    assert word not in published.live_runner_script() + published.egress_proxy_script()
