"""Mirror of `src/studyforge/skills/execution/record.py` (R12) — both images' tags, recorded.

⛔ **The tag the corpus's primed runner build produced, and the editor's tag,
are recorded by the SKILL** — asked of the component, never typed and never a
hand-written file — ⭐ and the one compose command the reader's document prints
reads both from where they were recorded. ⭐ Most cases hand in a fake `ask`, so
they need no sibling; ⭐ one per image asks the REAL sibling at its pin, and
skips where none is readable; the compose reading skips where no docker CLI is.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
from pathlib import Path

import pytest

from studyforge.corpus.manifest import parse
from studyforge.skills.execution import onboard, record
from studyforge.skills.execution.onboard import ExecutionRefused
from tests.studyforge.execute import container
from tests.studyforge.exercise.bundle.test_dependency_image import sibling as component
from tests.studyforge.skills.execution.contracts import corpus, editor_text, manifest_document
from tests.support import tool_on_path

#: What the fake component prints.
TAG = "example/runner:java-maven-amd64-0123456789ab"

#: What the fake component prints for the editor.
EDITOR_TAG = "example/editor:java-maven-amd64-ba9876543210"

#: ⭐ The runner's file as a corpus already carries it. Recording the editor is
#: additive (R3): these bytes do not move.
RUNNER_BYTES = (
    f"# {onboard.GENERATED}\n"
    "# The primed runner's tag, as the component's own runner.image.tag_from printed it\n"
    "# for the prime beside this file. Re-run the skill's record step when the\n"
    "# component's pin, the prime or the host's architecture moves.\n"
    f"STUDYFORGE_RUNNER_IMAGE={TAG}\n"
)


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


def test_the_runners_file_is_the_bytes_a_corpus_already_carries(tmp_path):
    record.record_runner(made(tmp_path), tmp_path, tmp_path, ask=Asked())
    assert (tmp_path / onboard.RUNNER_ENV).read_text(encoding="utf-8") == RUNNER_BYTES


# ---------------------------------------------------------------------------
# The editor's tag: recorded the way the runner's is, in a file of its own.
# ---------------------------------------------------------------------------


def test_the_editors_tag_the_component_printed_is_recorded_beside_the_runners(tmp_path):
    execution = made(tmp_path)
    assert (
        record.record_editor(execution, tmp_path, tmp_path, ask=Asked(0, EDITOR_TAG + "\n"))
        == onboard.EDITOR_ENV
    )
    written = (tmp_path / onboard.EDITOR_ENV).read_text(encoding="utf-8")
    assert onboard.GENERATED in written
    lines = [one for one in written.splitlines() if one and not one.startswith("#")]
    assert lines == [f"EDITOR_IMAGE={EDITOR_TAG}"]
    assert str(tmp_path) not in written


def test_it_asks_the_editor_blocks_own_tag_from_and_hands_it_no_prime(tmp_path):
    # ⭐ A contract before `provides` 3 declares a prime flag for the runner
    # alone, and the reader's document then prints the editor's build without
    # one: the tag recorded is the tag that printed build produces. The primed
    # editor is `test_editor_prime.py`'s.
    execution = made(tmp_path)
    assert execution.primed is not None and execution.primed.projects, "no prime: vacuous"
    asked = Asked(0, EDITOR_TAG)
    record.record_editor(execution, tmp_path, tmp_path / "component", ask=asked)
    [(argv, cwd)] = asked.calls
    assert argv == ["python3", "build.py", "--runtimes", "java,maven", "--print-tag"]
    assert cwd == tmp_path / "component"


def test_recording_the_editor_leaves_the_runners_file_as_it_was(tmp_path):
    execution = made(tmp_path)
    record.record_runner(execution, tmp_path, tmp_path, ask=Asked())
    record.record_editor(execution, tmp_path, tmp_path, ask=Asked(0, EDITOR_TAG))
    assert (tmp_path / onboard.RUNNER_ENV).read_text(encoding="utf-8") == RUNNER_BYTES


def test_the_editors_file_is_classified_by_a_glob_the_skill_declares():
    assert onboard.classified(onboard.EDITOR_ENV)


@pytest.mark.parametrize("printed", ["", TAG, "example/editor:", "example/editor:a tag"])
def test_anything_but_one_tag_of_the_editors_own_repository_is_refused(tmp_path, printed):
    # ⛔ The runner's tag is one of them: each image is checked against its own
    # repository, so the two can never be recorded crosswise.
    with pytest.raises(ExecutionRefused, match="editor.image.repository"):
        record.record_editor(made(tmp_path), tmp_path, tmp_path, ask=Asked(0, printed))
    assert not (tmp_path / onboard.EDITOR_ENV).exists()


def test_an_editor_tag_from_that_fails_is_refused_by_its_own_block(tmp_path):
    with pytest.raises(ExecutionRefused, match="editor.image.tag_from exited 3"):
        record.record_editor(made(tmp_path), tmp_path, tmp_path, ask=Asked(3, ""))


def test_an_image_the_step_records_nothing_for_is_refused_without_its_name():
    with pytest.raises(ExecutionRefused, match="no other image") as refused:
        record.text("EDITOR_IMAGE", EDITOR_TAG, image="narration-private")
    assert "narration-private" not in str(refused.value)


def test_a_corpus_that_is_not_runnable_has_no_editor_to_record(tmp_path):
    with pytest.raises(ExecutionRefused, match="no editor"):
        record.record_editor(onboard.Execution(runnable=False), tmp_path, tmp_path, ask=Asked())


def test_the_one_printed_compose_command_reads_both_recorded_tags(tmp_path):
    # ⭐ The compose path, run as printed: the command the reader's document
    # prints, with its verb swapped for `config --images`, which reads the file
    # and both env files and starts nothing. ⛔ Neither variable is in the
    # environment, so a tag compose answers can only have come from the corpus.
    if tool_on_path("docker") is None:
        pytest.skip("no docker CLI in this environment (the pinned dev image carries none)")
    execution = made(tmp_path)
    record.record_runner(execution, tmp_path, tmp_path, ask=Asked())
    record.record_editor(execution, tmp_path, tmp_path, ask=Asked(0, EDITOR_TAG))
    document = (tmp_path / onboard.READER_DOC).read_text(encoding="utf-8")
    [line] = [one for one in document.splitlines() if one.endswith(" up -d --wait")]
    argv = shlex.split(line.removesuffix(" up -d --wait")) + ["config", "--images"]
    environment = {
        name: value
        for name, value in os.environ.items()
        if name not in ("EDITOR_IMAGE", "STUDYFORGE_RUNNER_IMAGE")
    }
    # The synthetic contract's one other required variable, which is not a tag
    # and which no corpus file holds: a placeholder, so compose reads the rest.
    environment["CODE_SERVER_PASSWORD"] = "placeholder"
    done = subprocess.run(
        argv, cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=60
    )
    assert done.returncode == 0, done.stderr[-2000:]
    assert sorted(done.stdout.split()) == sorted([EDITOR_TAG, TAG])


def test_the_real_component_prints_the_editor_tag_that_is_recorded(tmp_path):
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

    record.record_editor(execution, tmp_path, sibling, ask=ask)
    assert execution.selection is not None
    again = ask(execution.selection.tag_from, sibling)[1].strip()
    variable = json.loads(text)["editor"]["image"]["env_var"]
    assert f"{variable}={again}\n" in (tmp_path / onboard.EDITOR_ENV).read_text(encoding="utf-8")
