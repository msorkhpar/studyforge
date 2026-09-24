"""Mirror of `src/studyforge/skills/execution/reader.py` (R12) — the reader's `EXECUTION.md`.

⭐ The reader-facing half: ONE command brings up the editor and the runner,
reading both tags the skill recorded; both builds are printed with the prime; and
the list of what must exist before the start (§8.1) names the practice
workspaces beside the sources.
"""

from __future__ import annotations

import json

from studyforge.corpus.manifest import parse
from studyforge.skills.execution import onboard as skill
from tests.studyforge.skills.execution.contracts import (
    corpus,
    editor_text,
    manifest_document,
    narration_text,
)


def document(tmp_path, *, narration: bool = False, **moved: object) -> str:
    """The reader's document the skill generates for the synthetic corpus."""
    made = skill.generate(
        parse(json.dumps(manifest_document(**moved))),
        editor_text=editor_text(),
        narration_text=narration_text() if narration else None,
        root=corpus(tmp_path),
    )
    return dict(made.files)[skill.READER_DOC]


def test_one_command_brings_up_both_reading_both_recorded_tags(tmp_path):
    text = document(tmp_path)
    command = (
        f"docker compose --env-file {skill.RUNNER_ENV} --env-file {skill.EDITOR_ENV} "
        f"--env-file {skill.INSTANCE_ENV} -f {skill.COMPOSE_FILE} up -d --wait"
    )
    assert command in text
    assert text.count("docker compose") == 1


def test_the_instance_file_is_named_with_what_it_holds_and_who_reads_it(tmp_path):
    """⭐ the reader is told a second checkout records its own four values."""
    text = document(tmp_path)
    assert f"`{skill.INSTANCE_ENV}` holds this checkout's compose project" in text
    assert "the study server finds the containers by" in text


def test_the_runner_and_where_it_comes_from_are_named(tmp_path):
    text = document(tmp_path)
    assert "`studyforge-runner-demo`, from `STUDYFORGE_RUNNER_IMAGE`" in text
    assert "python3 runner.py --runtimes java,maven --print-tag" in text
    assert f"writes `{skill.RUNNER_ENV}`" in text


def test_the_editors_tag_is_recorded_by_the_same_step_and_named_with_its_file(tmp_path):
    text = document(tmp_path)
    assert "python3 build.py --runtimes java,maven --print-tag" in text
    assert f"writes `{skill.EDITOR_ENV}`" in text


def test_both_builds_are_printed_and_the_runner_carries_the_prime(tmp_path):
    text = document(tmp_path)
    flag = f"--prime <this corpus>/{skill.PRIME_DIR}"
    assert f"python3 runner.py --runtimes java,maven {flag}" in text
    assert "python3 build.py --runtimes java,maven\n" in text
    # ⭐ A contract that declares no editor prime (`provides` 2): the sentence
    # says the runner's line alone carries it, which is what the block prints.
    assert f"The runner's build above carries `{flag}`." in text


def test_a_corpus_with_no_prime_builds_its_runner_without_one(tmp_path):
    text = document(tmp_path, runtimes=["python"])
    assert "python3 runner.py --runtimes python\n" in text
    assert "--prime" not in text and "no prime" in text


def test_what_must_exist_first_names_the_practice_workspaces_beside_the_sources(tmp_path):
    text = document(tmp_path)
    assert "- the practice workspaces the editor binds too: `practice`" in text
    first = text.split("exist on the host before the start", 1)[1]
    assert "- `sources`\n- `practice`" in first


def test_sources_that_hold_the_practice_workspaces_name_no_second_bind(tmp_path):
    text = document(tmp_path, content={"include": ["practice/**/*.md"], "exclude": []})
    assert "binds too" not in text


def test_narration_is_pointed_at_and_never_rendered(tmp_path):
    text = document(tmp_path, narration=True)
    assert "## Narration" in text and "- `compose.yaml`" in text
