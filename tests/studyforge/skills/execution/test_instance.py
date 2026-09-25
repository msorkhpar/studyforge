"""Mirror of `src/studyforge/skills/execution/instance.py` (R12) — a second instance, recorded.

⭐ As the skill writes it: the compose file interpolates the
project, the editor's port and both container names with the values they
always had as defaults; `write` records those defaults once and never over a
recorded file; `record_instance` records a second checkout's own four; and the
loopback bind stays literal whatever is recorded.
"""

from __future__ import annotations

import json
import re

import pytest

from studyforge.corpus.manifest import parse
from studyforge.execute import container_for, editor_container_for
from studyforge.execute import instance as names
from studyforge.skills.execution import onboard, record_instance, written
from studyforge.skills.execution.onboard import ExecutionRefused
from tests.studyforge.skills.execution.contracts import (
    corpus,
    editor_contract,
    editor_text,
    manifest_document,
    runner_block,
)


def generated(tmp_path, **moved):
    root = corpus(tmp_path)
    made = onboard.generate(
        parse(json.dumps(manifest_document(**moved))), editor_text=editor_text(), root=root
    )
    return made, root


def compose_of(made) -> str:
    return dict(made.files)[onboard.COMPOSE_FILE]


def test_the_four_values_are_interpolations_whose_defaults_are_the_old_literals(tmp_path):
    text = compose_of(generated(tmp_path)[0])
    assert 'name: "${STUDYFORGE_PROJECT:-studyforge-demo}"' in text
    assert '"127.0.0.1:${STUDYFORGE_EDITOR_PORT:-8443}:8080"' in text
    assert f'"${{STUDYFORGE_EDITOR_NAME:-{editor_container_for("demo")}}}"' in text
    assert f'"${{STUDYFORGE_RUNNER_NAME:-{container_for("demo")}}}"' in text


def test_no_published_port_is_left_literal_and_the_bind_is_never_interpolated(tmp_path):
    text = compose_of(generated(tmp_path)[0])
    published = re.findall(r'^      - "([^"]*:\d+)"$', text, flags=re.MULTILINE)
    assert published == ["127.0.0.1:${STUDYFORGE_EDITOR_PORT:-8443}:8080"]
    assert all(one.startswith("127.0.0.1:${") for one in published)


def test_write_records_the_defaults_once_and_never_over_a_recorded_file(tmp_path):
    made, root = generated(tmp_path)
    assert onboard.INSTANCE_ENV in onboard.write(made, root)
    recorded = names.read(root)
    assert recorded == dict(made.instance)
    record_instance(made, root, project="demo-second", port=18443)
    before = (root / onboard.INSTANCE_ENV).read_bytes()
    assert onboard.INSTANCE_ENV not in onboard.write(made, root)
    assert (root / onboard.INSTANCE_ENV).read_bytes() == before


def test_a_second_instance_records_its_own_four_and_serve_reads_the_same(tmp_path):
    made, root = generated(tmp_path)
    onboard.write(made, root)
    written = record_instance(
        made,
        root,
        project="demo-second",
        port=18443,
        editor="second-ed",
        runner="second-run",
        site_port=18444,
        site="second-site",
    )
    assert written == onboard.INSTANCE_ENV
    assert names.read(root) == {
        names.PROJECT: "demo-second",
        names.EDITOR_PORT: "18443",
        names.EDITOR_NAME: "second-ed",
        names.RUNNER_NAME: "second-run",
        names.SITE_PORT: "18444",
        names.SITE_NAME: "second-site",
    }
    assert names.recorded(root, "demo") == names.Names("second-run", "second-ed")


def test_a_value_it_is_not_handed_keeps_its_default(tmp_path):
    made, root = generated(tmp_path)
    record_instance(made, root, port=18443)
    assert names.read(root) == dict(made.instance, **{names.EDITOR_PORT: "18443"})


@pytest.mark.parametrize(
    "choice",
    [
        {"port": 80},
        {"project": "Not-Lower"},
        {"runner": "a;b"},
        {"editor": ""},
        {"site_port": 80},
        {"site": "a b"},
        {"site_port": 8443},
    ],
)
def test_a_value_compose_or_the_bind_would_misread_is_refused(tmp_path, choice):
    made, root = generated(tmp_path)
    with pytest.raises(ExecutionRefused):
        record_instance(made, root, **choice)
    assert not (root / onboard.INSTANCE_ENV).exists()


def test_a_corpus_that_is_not_runnable_has_no_instance_to_record(tmp_path):
    made, root = generated(tmp_path, runtimes=[])
    with pytest.raises(ExecutionRefused, match="no runtime"):
        record_instance(made, root)
    assert onboard.write(made, root) == ()


def test_the_instance_file_is_this_skills_own_and_classified(tmp_path):
    assert onboard.classified(onboard.INSTANCE_ENV)
    assert onboard.INSTANCE_ENV.startswith(f"{onboard.DIRECTORY}/")


def test_each_default_is_read_from_the_contract_whose_field_keeps_its_meaning(tmp_path):
    """⛔ Clause 4: `ports[].host` is still the port published when nothing is recorded,
    and `runner.run.name_template` still the runner's name — read, never typed."""
    contract = editor_contract(runner=runner_block(run={"name_template": "lab-<source>"}))
    contract["editor"]["ports"][0]["host"] = 9999
    root = corpus(tmp_path)
    made = onboard.generate(
        parse(json.dumps(manifest_document())), editor_text=json.dumps(contract), root=root
    )
    text = compose_of(made)
    assert '"127.0.0.1:${STUDYFORGE_EDITOR_PORT:-9999}:8080"' in text
    assert 'container_name: "${STUDYFORGE_RUNNER_NAME:-lab-demo}"' in text
    assert dict(made.instance)[names.EDITOR_PORT] == "9999"
    assert dict(made.instance)[names.RUNNER_NAME] == "lab-demo"


def test_a_recorded_second_instance_is_no_hand_edit_and_an_edit_to_it_is(tmp_path):
    """⭐ `record_instance` stamps what it writes, as `record_runner` does."""
    made, root = generated(tmp_path)
    onboard.write(made, root)
    record_instance(made, root, project="demo-second", port=18443)
    assert written.hand_edited(root) == []
    target = root / onboard.INSTANCE_ENV
    target.write_text(target.read_text(encoding="utf-8") + "# edited\n", encoding="utf-8")
    assert [one.split(" ", 1)[0] for one in written.hand_edited(root)] == [onboard.INSTANCE_ENV]
