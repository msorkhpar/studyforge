"""The build role, read live: an exercise whose tests import a library, graded in the REAL runner.

⭐ **The row's first clause, read the only way it can be:** a bundle whose
tests import a library the JDK does not carry is emitted into a corpus, the
reader's container is started over it from the sibling's own declaration
(`--network none`, the reader's uid, the source root alone), the record's
`test_command` runs through `execute.Runner` in container mode, and the report
it leaves is folded into the per-case verdicts.

⛔ **And both ways** (R12): the same exercise in a runner primed WITHOUT the
library fails naming it; in a runner with no prime at all it fails naming what
it could not resolve offline; and the corpus it ran over holds no jar and a
build file naming no repository — so the channel is the only thing that could
have resolved it.

⭐ **Opt-in, because it builds images.** `STUDYFORGE_RUNNER_BUILDS=1` consents to the
sibling's own build (which pulls its pinned inputs); without it, without Docker, or
without the sibling at its pin, every case SKIPS and says which. ⛔ The pinned dev image
carries no Docker, so this is a HOST reading, and it must be taken holding the shared
container lock.
"""

from __future__ import annotations

import os
import subprocess
import time
import uuid
from pathlib import Path

import pytest

from studyforge.execute import CONTAINER, Runner, exit_line
from studyforge.exercise import breakdown_of
from studyforge.exercise import of as exercise_of
from studyforge.exercise.bundle import RUN_OUTPUT_DIRNAME, emit, write
from tests.harness import engine
from tests.studyforge.execute import container
from tests.studyforge.exercise.bundle import dependency
from tests.support import tool_on_path

#: The consent this module needs before it builds an image.
CONSENT = "STUDYFORGE_RUNNER_BUILDS"


@pytest.fixture
def tmp_path():
    """⭐ Engine-visible, never the host's temporary directory (`tests.harness.engine`).

    A container in this module binds the test's directory, and Docker Desktop shares
    no host `/tmp` while Windows has none.
    """
    with engine.shared("w436") as where:
        yield where


def reason_to_skip() -> str | None:
    """Why these readings cannot be taken here, or `None` when they can."""
    if os.environ.get(CONSENT) != "1":
        return f"set {CONSENT}=1 to let this module build the sibling's runner images"
    if tool_on_path("docker") is None:
        return "no docker CLI in this environment (the pinned dev image carries none)"
    return container.declaration_reason()


def sibling() -> Path:
    """The sibling's checkout. ⭐ `reason_to_skip` has already found it, or this never runs."""
    from tests.harness.workspace import sibling as checkout

    found = checkout(container.SIBLING)
    assert found is not None, "the declaration was read, so the checkout was named"
    return found


@pytest.fixture(scope="module")
def images(tmp_path_factory):
    """The three runners, each tag asked of the sibling: primed, primed without, unprimed."""
    reason = reason_to_skip()
    if reason is not None:
        pytest.skip(reason)
    runner = container.declaration()
    base = tmp_path_factory.mktemp("w436-images")
    bare = dependency.image_for(runner, sibling())
    with engine.shared("w436-library") as library:
        jar = dependency.build_library(library, bare)
    with_library = dependency.write_prime(base / "prime-with", jar)
    without_library = dependency.write_prime(base / "prime-without", None)
    return {
        "primed": dependency.image_for(runner, sibling(), prime=with_library),
        "without": dependency.image_for(runner, sibling(), prime=without_library),
        "bare": bare,
    }


def corpus(root: Path, *, solved: bool = True):
    """Emit the exercise into a fresh corpus; the reader's file solved when asked."""
    bundle = dependency.write_bundle(root)
    emission = emit(root, bundle, source="demo", ingested="2026-01-05")
    write(root, emission, "the exercise")
    if solved:
        (root / bundle.places.in_workspace(dependency.MAIN_FILE)).write_text(
            dependency.REFERENCE, encoding="utf-8"
        )
    return bundle, exercise_of(emission.document, "practice-1.json")


def graded(root: Path, image: str, exercise):
    """Start the reader's container over `root` from the declaration, Submit, and fold."""
    runner = container.declaration()
    name = f"w436-{uuid.uuid4().hex[:10]}"
    argv = container.run_argv(runner, name=name, source_root=root, tag=image)
    started = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    assert started.returncode == 0, f"the declared run line did not start: {started.stderr}"
    try:
        assert container.settings(name).split()[0] == runner["network"]["mode"] == "none"
        grading = Runner(root, name, timeout=600.0)
        assert grading.mode() == CONTAINER
        began = time.time()
        lines = list(grading.start([list(exercise.test_command)]).lines())
        return lines, breakdown_of(exercise, root, "practice-1.json", started=began)
    finally:
        container.remove(name)


def test_the_exercise_resolves_its_library_offline_and_yields_per_case_verdicts(images, tmp_path):
    bundle, exercise = corpus(tmp_path / "corpus")
    lines, breakdown = graded(tmp_path / "corpus", images["primed"], exercise)
    assert lines[-1] == exit_line(0), "\n".join(lines[-40:])
    assert breakdown is not None, "the run left no report at the declared path"
    assert breakdown.ask and (breakdown.edges_passed, breakdown.edges_total) == (1, 1)
    report = tmp_path / "corpus" / exercise.report.path
    assert report.is_dir() and report.relative_to(tmp_path / "corpus" / bundle.places.workspace)


def test_an_edge_the_solution_ignores_is_named_by_its_sentence(images, tmp_path):
    bundle, exercise = corpus(tmp_path / "corpus")
    (tmp_path / "corpus" / bundle.places.in_workspace(dependency.MAIN_FILE)).write_text(
        dependency.PLANT, encoding="utf-8"
    )
    lines, breakdown = graded(tmp_path / "corpus", images["primed"], exercise)
    assert lines[-1] != exit_line(0)
    assert breakdown.ask and breakdown.failed_edges == ("a blank name greets nobody",)


def test_nothing_in_the_corpus_could_have_resolved_the_library(images, tmp_path):
    # ⛔ "Resolved ONLY through the new channel": no jar anywhere in the tree the
    # container mounts, and a build file that names no repository of its own.
    bundle, _ = corpus(tmp_path / "corpus")
    root = tmp_path / "corpus"
    assert not [path for path in root.rglob("*.jar")]
    build = (root / bundle.places.in_workspace(dependency.BUILD_FILE)).read_text(encoding="utf-8")
    assert dependency.COORDINATES.split(":")[1] in build
    assert dependency.names_no_repository(build)


def test_a_runner_primed_without_the_library_fails_naming_it(images, tmp_path):
    _, exercise = corpus(tmp_path / "corpus")
    lines, breakdown = graded(tmp_path / "corpus", images["without"], exercise)
    said = "\n".join(lines)
    assert lines[-1] != exit_line(0)
    assert dependency.COORDINATES in said, said[-3000:]
    assert breakdown is None, "a run that could not resolve its build still wrote a report"


def test_a_runner_with_no_prime_fails_naming_what_it_could_not_resolve(images, tmp_path):
    _, exercise = corpus(tmp_path / "corpus")
    lines, breakdown = graded(tmp_path / "corpus", images["bare"], exercise)
    said = "\n".join(lines)
    assert lines[-1] != exit_line(0)
    assert "offline" in said and "has not been downloaded" in said, said[-3000:]
    assert breakdown is None


def test_the_same_exercise_without_its_build_role_fails_in_the_primed_runner(images, tmp_path):
    # ⭐ The channel removed on the corpus side: the image still carries the
    # library, and the exercise can no longer reach it.
    root = tmp_path / "corpus"
    bundle, exercise = corpus(root)
    (root / bundle.places.in_workspace(dependency.BUILD_FILE)).unlink()
    lines, breakdown = graded(root, images["primed"], exercise)
    assert lines[-1] != exit_line(0)
    assert dependency.BUILD_FILE in "\n".join(lines)
    assert breakdown is None


def test_a_run_leaves_its_output_where_the_one_ignore_line_reaches(images, tmp_path):
    # ⭐ Everything the run wrote into the reader's workspace is
    # under the run-output directory, so one ignore line covers all of it.
    root = tmp_path / "corpus"
    bundle, exercise = corpus(root)
    before = {path for path in (root / bundle.places.workspace).rglob("*") if path.is_file()}
    graded(root, images["primed"], exercise)
    after = {path for path in (root / bundle.places.workspace).rglob("*") if path.is_file()}
    added = sorted(path.relative_to(root / bundle.places.workspace) for path in after - before)
    assert added and all(path.parts[0] == RUN_OUTPUT_DIRNAME for path in added), added
