"""The generated compose file brings up the runner `execute` finds.

⭐ **A HOST reading, opt-in behind `STUDYFORGE_RUNNER_BUILDS=1`**, because it
builds the sibling's runner (from the skill's own prime, through the contract's
own `built_by`) and starts a container. A fixture corpus is run through
`onboard.generate`, `onboard.write` and `record.record_runner` with the
sibling's contract at its pin; ⛔ **no tag is typed** — the one compose command
`EXECUTION.md` prints is run, naming only the runner service, and then:

- ⭐ `execute.ModeProbe` over the corpus root answers `container`, so a Submit
  runs in the runner rather than falling back to the host;
- ⭐ the container is the one `execute.container_for` names, and it holds the
  corpus's own files at the contract's workspace.

⚠️ The editor is not started here: its image is the component's to build and
this module builds none. ⭐ `EDITOR_IMAGE` is set to a placeholder only because
compose interpolates the whole file; the service it names is never pulled.
⛔ Torn down whatever happens.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from studyforge.corpus.manifest import parse
from studyforge.execute import CONTAINER, ModeProbe, container_for
from studyforge.skills.execution import onboard, record
from tests.harness import engine
from tests.studyforge.execute import container
from tests.studyforge.exercise.bundle.test_dependency_image import CONSENT, sibling
from tests.studyforge.skills.execution.contracts import manifest_document
from tests.studyforge.skills.execution.test_prime_image import argv, corpus
from tests.support import tool_on_path

#: A source no other reading on this host names, so its container name is its own.
SOURCE = "w445-compose-reading"


@pytest.fixture
def tmp_path():
    """⭐ Engine-visible, never the host's temporary directory (`tests.harness.engine`).

    A container in this module binds the test's directory, and Docker Desktop shares
    no host `/tmp` while Windows has none.
    """
    with engine.shared("compose") as where:
        yield where


def ask(command, cwd):
    done = subprocess.run(
        list(command), cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True
    )
    return done.returncode, done.stdout


def docker(*arguments: str, cwd: Path | None = None, env=None):
    return subprocess.run(
        ["docker", *arguments],
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )


def test_the_one_generated_command_brings_up_the_runner_execute_finds(tmp_path):
    if os.environ.get(CONSENT) != "1":
        pytest.skip(f"set {CONSENT}=1 to let this module build and start the sibling's runner")
    if tool_on_path("docker") is None:
        pytest.skip("no docker CLI in this environment (the pinned dev image carries none)")
    reason = container.declaration_reason()
    if reason is not None:
        pytest.skip(reason)
    text = container.contract_reading().text
    root = corpus(tmp_path / "corpus")
    manifest = parse(
        json.dumps(
            manifest_document(
                source=SOURCE,
                runtimes=["java", "maven"],
                content={"include": ["src/**/*.md"], "exclude": []},
            )
        )
    )
    made = onboard.generate(manifest, editor_text=text, root=root)
    onboard.write(made, root)
    record.record_runner(made, root, sibling(), ask=ask)
    built = subprocess.run(
        argv(text, "built_by", root / onboard.PRIME_DIR),
        cwd=sibling(),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    assert built.returncode == 0, (built.stdout + built.stderr)[-4000:]
    env = dict(os.environ, EDITOR_IMAGE="example/editor:never-pulled")
    compose = ("compose", "--env-file", onboard.RUNNER_ENV, "-f", onboard.COMPOSE_FILE)
    try:
        up = docker(*compose, "up", "-d", "--wait", "runner", cwd=root, env=env)
        assert up.returncode == 0, (up.stdout + up.stderr)[-4000:]
        name = container_for(SOURCE)
        assert made.runner is not None and made.runner.name == name
        assert ModeProbe(root, name).mode() == CONTAINER
        workdir = json.loads(text)["runner"]["workspace"]["container_path"]
        held = docker("exec", name, "test", "-f", f"{workdir}/pom.xml")
        assert held.returncode == 0, held.stderr
    finally:
        down = docker(*compose, "down", "-v", "--remove-orphans", cwd=root, env=env)
        assert down.returncode == 0, down.stderr[-2000:]
