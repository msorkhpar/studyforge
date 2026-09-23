"""Mirror of `src/studyforge/skills/execution/record.py` (R12) — the runner's tag, recorded.

⛔ **`W445`'s second clause**: the tag the corpus's primed build produced is
recorded by the SKILL — asked of the component, never typed and never a
hand-written file. ⭐ Most cases hand in a fake `ask`, so they need no sibling;
⭐ one asks the REAL sibling at its pin, and skips where none is readable.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from studyforge.corpus.manifest import parse
from studyforge.skills.execution import onboard, record
from studyforge.skills.execution.onboard import ExecutionRefused
from tests.studyforge.execute import container
from tests.studyforge.exercise.bundle.test_dependency_image import sibling as component
from tests.studyforge.skills.execution.contracts import corpus, editor_text, manifest_document

#: What the fake component prints.
TAG = "example/runner:java-maven-amd64-0123456789ab"


def made(root: Path, **moved: object) -> onboard.Execution:
    """Generate and write for the synthetic corpus at `root`."""
    manifest = parse(json.dumps(manifest_document(**moved)))
    execution = onboard.generate(manifest, editor_text=editor_text(), root=corpus(root))
    onboard.write(execution, root)
    return execution


class Asked:
    """A fake `ask`: remembers what it was asked and answers what it was told to."""

    def __init__(self, code: int = 0, printed: str = TAG + "\n") -> None:
        self.code, self.printed = code, printed
        self.calls: list[tuple[list[str], Path]] = []

    def __call__(self, argv, cwd):
        self.calls.append((list(argv), Path(cwd)))
        return self.code, self.printed


def test_the_tag_the_component_printed_is_what_compose_reads(tmp_path):
    execution = made(tmp_path)
    asked = Asked()
    assert (
        record.record_runner(execution, tmp_path, tmp_path / "component", ask=asked)
        == onboard.RUNNER_ENV
    )
    written = (tmp_path / onboard.RUNNER_ENV).read_text(encoding="utf-8")
    assert f"STUDYFORGE_RUNNER_IMAGE={TAG}\n" in written
    assert onboard.GENERATED in written
    lines = [one for one in written.splitlines() if one and not one.startswith("#")]
    assert lines == [f"STUDYFORGE_RUNNER_IMAGE={TAG}"]


def test_it_asks_the_runner_blocks_own_tag_from_with_the_prime_this_skill_wrote(tmp_path):
    execution = made(tmp_path)
    asked = Asked()
    record.record_runner(execution, tmp_path, tmp_path / "component", ask=asked)
    [(argv, cwd)] = asked.calls
    prime = str((tmp_path / onboard.PRIME_DIR).resolve())
    assert argv == [
        "python3",
        "runner.py",
        "--runtimes",
        "java,maven",
        "--print-tag",
        "--prime",
        prime,
    ]
    assert cwd == tmp_path / "component"


def test_a_corpus_with_no_prime_asks_for_the_unprimed_tag(tmp_path):
    execution = made(tmp_path, runtimes=["python"])
    asked = Asked()
    record.record_runner(execution, tmp_path, tmp_path / "component", ask=asked)
    assert "--prime" not in asked.calls[0][0]


def test_no_absolute_path_reaches_the_file(tmp_path):
    record.record_runner(made(tmp_path), tmp_path, tmp_path / "component", ask=Asked())
    written = (tmp_path / onboard.RUNNER_ENV).read_text(encoding="utf-8")
    assert str(tmp_path) not in written


def test_re_recording_the_same_answer_rewrites_the_same_bytes(tmp_path):
    execution = made(tmp_path)
    record.record_runner(execution, tmp_path, tmp_path, ask=Asked())
    first = (tmp_path / onboard.RUNNER_ENV).read_bytes()
    record.record_runner(execution, tmp_path, tmp_path, ask=Asked())
    assert (tmp_path / onboard.RUNNER_ENV).read_bytes() == first


def test_the_file_is_classified_by_a_glob_the_skill_declares():
    assert onboard.classified(onboard.RUNNER_ENV)


def test_a_component_that_fails_is_refused_and_its_output_is_not_reproduced(tmp_path):
    execution = made(tmp_path)
    leak = str(tmp_path / onboard.PRIME_DIR)
    with pytest.raises(ExecutionRefused, match="exited 2") as refused:
        record.record_runner(execution, tmp_path, tmp_path, ask=Asked(2, f"refused: {leak}\n"))
    assert leak not in str(refused.value)
    assert not (tmp_path / onboard.RUNNER_ENV).exists()


@pytest.mark.parametrize(
    "printed",
    [
        "",
        "somebody/else:java-amd64-0123",
        "example/runner:",
        "example/runner:a tag",
        "example/runner:one\nexample/runner:two",
        "example/runner:x=y",
        "example/runner:x#y",
        "example/runner-other:java",
    ],
)
def test_anything_but_one_tag_of_the_runners_own_repository_is_refused(tmp_path, printed):
    execution = made(tmp_path)
    with pytest.raises(ExecutionRefused, match="not one tag"):
        record.record_runner(execution, tmp_path, tmp_path, ask=Asked(0, printed))
    assert not (tmp_path / onboard.RUNNER_ENV).exists()


def test_a_corpus_that_is_not_runnable_has_no_runner_to_record(tmp_path):
    with pytest.raises(ExecutionRefused, match="no runner"):
        record.record_runner(onboard.Execution(runnable=False), tmp_path, tmp_path, ask=Asked())


def test_the_real_component_prints_the_tag_that_is_recorded(tmp_path):
    # ⭐ The sibling at its pin, its own `tag_from`: `--print-tag` hashes files
    # and starts no Docker, so this needs the checkout and nothing else.
    reason = container.declaration_reason()
    if reason is not None:
        pytest.skip(reason)
    text = container.contract_reading().text
    sibling = component()
    manifest = parse(json.dumps(manifest_document(runtimes=["java", "maven"])))
    execution = onboard.generate(manifest, editor_text=text, root=corpus(tmp_path))
    onboard.write(execution, tmp_path)

    def ask(argv, cwd):
        done = subprocess.run(
            list(argv), cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True
        )
        return done.returncode, done.stdout

    record.record_runner(execution, tmp_path, sibling, ask=ask)
    again = ask(record.argv(execution, tmp_path), sibling)[1].strip()
    variable = json.loads(text)["runner"]["image"]["env_var"]
    assert f"{variable}={again}\n" in (tmp_path / onboard.RUNNER_ENV).read_text(encoding="utf-8")
