"""Mirror of `src/studyforge/execute/preflight.py` (R12): each value that cannot work, by name.

⭐ Over a corpus root holding the publisher's `instance.env` and, where a test
needs it, a compose file: every refusal names its key, and none quotes the value.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.execute import RunRefused, instance_problems, refuse_instance
from studyforge.execute.instance import COMPOSE_FILE, INSTANCE_FILE

CLEAN = {
    "STUDYFORGE_PROJECT": "w505-demo",
    "STUDYFORGE_EDITOR_PORT": "18505",
    "STUDYFORGE_EDITOR_NAME": "w505-editor",
    "STUDYFORGE_RUNNER_NAME": "w505-runner",
    "STUDYFORGE_SITE_PORT": "18504",
    "STUDYFORGE_SITE_NAME": "w505-site",
}

#: The published ports of a compose file the skill renders, with the address in its slot.
COMPOSE = (
    "services:\n  editor:\n    ports:\n"
    '      - "{address}:${{STUDYFORGE_EDITOR_PORT:-8443}}:8080"\n'
    "    command:\n      - --auth=none\n"
    "  site:\n    ports:\n"
    '      - "127.0.0.1:${{STUDYFORGE_SITE_PORT:-8765}}:${{STUDYFORGE_SITE_PORT:-8765}}"\n'
)


def corpus(tmp_path: Path, extra: str = "", **values: str) -> Path:
    root = tmp_path / "corpus"
    (root / INSTANCE_FILE).parent.mkdir(parents=True, exist_ok=True)
    lines = "".join(f"{key}={value}\n" for key, value in {**CLEAN, **values}.items())
    (root / INSTANCE_FILE).write_text("# the publisher's\n" + lines + extra, encoding="utf-8")
    return root


def test_a_clean_instance_has_no_problem_and_is_not_refused(tmp_path):
    root = corpus(tmp_path)
    assert instance_problems(root) == []
    refuse_instance(root)


def test_a_corpus_with_no_instance_file_is_compose_s_defaults_and_fine(tmp_path):
    assert instance_problems(tmp_path) == []


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("STUDYFORGE_SITE_PORT", "0"),
        ("STUDYFORGE_SITE_PORT", "70000"),
        ("STUDYFORGE_EDITOR_PORT", "65536"),
        ("STUDYFORGE_EDITOR_PORT", "eighty"),
        ("STUDYFORGE_SITE_PORT", "0.0.0.0:18504"),
        ("STUDYFORGE_SITE_NAME", "two words"),
        ("STUDYFORGE_RUNNER_NAME", "a/b"),
        ("STUDYFORGE_PROJECT", "Upper"),
    ],
)
def test_each_value_that_cannot_work_is_refused_by_its_key_and_never_quoted(tmp_path, key, value):
    [sentence] = instance_problems(corpus(tmp_path, **{key: value}))
    assert sentence.startswith(f"{INSTANCE_FILE}: {key} ")
    assert value not in sentence.split(key, 1)[1], "a refusal never quotes the value"


def test_two_services_on_one_port_is_refused_naming_both_keys(tmp_path):
    [sentence] = instance_problems(corpus(tmp_path, STUDYFORGE_SITE_PORT="18505"))
    assert "STUDYFORGE_EDITOR_PORT and STUDYFORGE_SITE_PORT name one port" in sentence


def test_every_problem_is_said_not_only_the_first(tmp_path):
    found = instance_problems(
        corpus(tmp_path, STUDYFORGE_SITE_PORT="0", STUDYFORGE_EDITOR_PORT="70000")
    )
    assert [line.split(" ")[1] for line in found] == [
        "STUDYFORGE_EDITOR_PORT",
        "STUDYFORGE_SITE_PORT",
    ]


def test_a_key_that_tries_to_set_a_bind_is_refused_as_needing_the_editors_auth(tmp_path):
    [sentence] = instance_problems(corpus(tmp_path, extra="STUDYFORGE_SITE_BIND=0.0.0.0\n"))
    assert sentence.startswith(f"{INSTANCE_FILE}: STUDYFORGE_SITE_BIND is not a value")
    assert "needs the editor's authentication" in sentence and "0.0.0.0" not in sentence


def test_any_other_key_the_file_does_not_carry_is_refused_rather_than_ignored(tmp_path):
    [sentence] = instance_problems(corpus(tmp_path, extra="STUDYFORGE_SITE_PROT=1\n"))
    assert "STUDYFORGE_SITE_PROT is not a value this file carries" in sentence


def test_a_compose_file_that_publishes_off_loopback_with_no_editor_password_is_refused(tmp_path):
    root = corpus(tmp_path)
    (root / COMPOSE_FILE).write_text(COMPOSE.format(address="0.0.0.0"), encoding="utf-8")
    [sentence] = instance_problems(root)
    assert sentence.startswith(f"{COMPOSE_FILE}: STUDYFORGE_EDITOR_PORT is published")
    assert "restore the editor's authentication" in sentence
    (root / COMPOSE_FILE).write_text(COMPOSE.format(address="127.0.0.1"), encoding="utf-8")
    assert instance_problems(root) == []


def test_refuse_raises_with_every_sentence(tmp_path):
    root = corpus(tmp_path, STUDYFORGE_SITE_PORT="0", extra="STUDYFORGE_BIND=x\n")
    with pytest.raises(RunRefused) as refused:
        refuse_instance(root)
    said = str(refused.value)
    assert said.startswith("the instance cannot be served: ")
    assert "STUDYFORGE_SITE_PORT" in said and "STUDYFORGE_BIND" in said
