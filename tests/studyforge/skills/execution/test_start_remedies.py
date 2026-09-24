"""Every remedy that tells a reader to start the containers names the corpus's own command (`W466`).

⚠️ **Measured (`W464/1`):** serve's `host` remedy, the build-and-serve procedure
and the practice panel's no-editor sentence each sent a reader to
`code-server-toolchain`'s README, while the one command that reads BOTH tags
the execution skill recorded is in the corpus's own `EXECUTION.md`. The user
ruled the fix on 2026-09-24. ⭐ So the three places are read here as a reader
meets them, and the section each one names is read out of a document the skill
really generates, so a renamed section or a moved command turns this RED.
"""

from __future__ import annotations

import re

from studyforge.render.templates import template
from studyforge.skills import documents
from studyforge.skills.buildserve.states import HOST_EXECUTION, START_DOCUMENT, START_SECTION
from studyforge.skills.execution import COMPOSE_FILE, EDITOR_ENV, READER_DOC, RUNNER_ENV
from tests.studyforge.skills.execution.test_onboard import made


def the_command_under(document: str, heading: str) -> str:
    """The first fenced line under `## heading` in a generated document."""
    section = document.split(f"\n## {heading}\n", 1)
    assert len(section) == 2, f"no section {heading!r} in the generated document"
    fenced = re.search(r"```\n(.+?)\n```", section[1], re.S)
    assert fenced, f"no command under {heading!r}"
    return fenced[1]


def remedies() -> dict[str, str]:
    """Each place that tells a reader how to start the containers, as the reader meets it."""
    panel = template("practice-panel.html").template
    no_editor = panel.split('data-practice-part="no-editor">', 1)[1].split("</p>", 1)[0]
    procedure = documents.text("buildserve")
    host = procedure[procedure.index("Its `remedy` line says what to do") :]
    return {
        "the host state's remedy": HOST_EXECUTION.remedy,
        "the practice panel's no-editor sentence": no_editor,
        "the build-and-serve procedure": host[: host.index("The probe's")],
    }


def test_the_document_the_remedies_name_is_the_one_the_skill_writes():
    assert START_DOCUMENT == READER_DOC


def test_the_section_they_name_holds_the_one_command_that_reads_both_tags(tmp_path):
    document = dict(made(tmp_path).files)[READER_DOC]
    command = the_command_under(document, START_SECTION)
    assert command.startswith("docker compose ")
    assert f"--env-file {RUNNER_ENV}" in command and f"--env-file {EDITOR_ENV}" in command
    assert f"-f {COMPOSE_FILE}" in command and command.endswith(" up -d --wait")


def test_every_start_remedy_names_that_command_and_no_readme():
    for where, sentence in remedies().items():
        flat = " ".join(sentence.split())
        assert f'"{START_SECTION}"' in flat, where
        assert START_DOCUMENT in flat, where
        assert "README" not in flat, where
