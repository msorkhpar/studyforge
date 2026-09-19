"""`SF-29`'s decisive clauses read against REAL `mvn test` output, in the runner image.

⭐ **Opt-in, exactly as `SF-20`'s container cases are** (`container.py`):
`STUDYFORGE_RUNNER_IMAGE=<tag>` names a runner image built with
`--runtimes java,maven`. Without one, or without Docker, every case SKIPS and
says why. ⚠️ **This office could not build one** (`SF-29/1`), so these cases
have not yet run. They are the readings `transcripts.py` could not capture:
a compile error and a failing test's stack trace, from the pinned Maven.

⭐ **The input is the component's own Maven smoke project**, read from the
sibling at run time and copied, never edited in place. It has three states:
clean, the test plant its `smoke.json` declares, and a compile plant. The
command is `smoke.json`'s, run through `SF-20`'s `Runner` in container mode,
with only `-q` removed. Quiet mode is the filtering this module exists to
replace, so it cannot be the input.

⛔ **An image whose label does not declare `maven` is REFUSED — every case
SKIPS, naming the label it read** (`W374`). These cases once passed against a
`python` image that held Maven only because its build was wrong; what an image
happens to hold is not what it declares, and only the declaration is read.
"""

from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from studyforge.execute import CONTAINER, Runner, exit_line
from studyforge.execute.quiet import MAVEN, filter_lines
from tests.studyforge.execute import container
from tests.support import repository_root

COMPILE_PLANT = {"file": "src/main/java/smoke/Adder.java", "from": "a + b", "to": "a + c"}
#: The label `code-server-toolchain`'s build writes: the declared set, space-separated.
RUNTIMES_LABEL = "org.studyforge.runner.runtimes"


def smoke_project():
    from tools.workspace.__main__ import workspace_root

    return workspace_root(repository_root()) / container.SIBLING / "docker/minimal/smoke/maven"


def declared_runtimes(image: str) -> str | None:
    """The image's declared-runtimes label, or `None` when it carries none."""
    template = f'{{{{index .Config.Labels "{RUNTIMES_LABEL}"}}}}'
    inspected = subprocess.run(
        ["docker", "image", "inspect", "--format", template, image],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False,
    )
    label = inspected.stdout.strip()
    return label if inspected.returncode == 0 and label and label != "<no value>" else None


def undeclared_reason(label: str | None) -> str | None:
    """Why an image labelled so cannot carry these cases; `None` when it declares `maven`."""
    if label is None:
        return f"the runner image carries no {RUNTIMES_LABEL} label, so it declares no maven"
    if "maven" not in label.split():
        return f"the runner image declares '{label}', not maven: build it with java,maven"
    return None


def reason_to_skip() -> str | None:
    if not (smoke_project() / "smoke.json").is_file():
        return f"the sibling {container.SIBLING}'s Maven smoke project is not reachable"
    return container.skip_reason() or undeclared_reason(declared_runtimes(container.image()))


def maven_run(where, plant=None) -> list[str]:
    """The raw lines of `mvn test` on a copy of the smoke project, in the reader's container."""
    root = shutil.copytree(smoke_project(), where / "smoke")
    if plant is not None:
        target = root / plant["file"]
        text = target.read_text(encoding="utf-8")
        assert plant["from"] in text, "the plant no longer applies to the smoke project"
        target.write_text(text.replace(plant["from"], plant["to"]), encoding="utf-8")
    declared = json.loads((root / "smoke.json").read_text(encoding="utf-8"))["command"]
    command = [arg for arg in declared if arg != "-q"]
    name = container.start(root)
    try:
        runner = Runner(root, name, timeout=600.0)
        assert runner.mode() == CONTAINER
        return list(runner.start([command]).lines())
    finally:
        container.remove(name)


@pytest.fixture
def raw(tmp_path):
    reason = reason_to_skip()
    if reason is not None:
        pytest.skip(reason)
    return lambda plant=None: maven_run(tmp_path, plant)


def contiguous(block, lines) -> bool:
    return any(lines[i : i + len(block)] == block for i in range(len(lines) - len(block) + 1))


def test_a_real_passing_run_is_reduced_to_its_verdict(raw):
    lines = raw()
    kept = list(filter_lines(lines, MAVEN))
    assert lines[-1] == exit_line(0) and kept[-1] == exit_line(0)
    assert any("Tests run: 1, Failures: 0" in line for line in kept)
    assert "[INFO] BUILD SUCCESS" in lines and "[INFO] BUILD SUCCESS" not in kept


def test_a_real_failing_tests_stack_trace_survives_intact(raw):
    lines = raw(json.loads((smoke_project() / "smoke.json").read_text(encoding="utf-8"))["plant"])
    kept = list(filter_lines(lines, MAVEN))
    start = next(i for i, line in enumerate(lines) if "AssertionFailedError" in line)
    end = start + 1
    while end < len(lines) and lines[end].lstrip().startswith(("at ", "...", "Caused by")):
        end += 1
    trace = lines[start:end]
    assert len(trace) > 1, "the instrument found no frames under the assertion"
    assert contiguous(trace, kept)
    assert lines[-1] == exit_line(1) and kept[-1] == exit_line(1)


def test_a_real_compile_error_survives_intact(raw):
    lines = raw(COMPILE_PLANT)
    kept = list(filter_lines(lines, MAVEN))
    error = [line for line in lines if "Adder.java" in line or "symbol" in line]
    assert error, "the instrument found no compile error in the run"
    assert [line for line in kept if line in error] == error
    assert not any(line.startswith("[INFO] Running ") for line in lines), "tests ran"
    assert kept[-1] == exit_line(1)


def test_an_image_that_does_not_declare_maven_is_refused_naming_its_label():
    for label in ("python", "java", "java node", "mavenrepo"):
        reason = undeclared_reason(label)
        assert reason is not None and f"'{label}'" in reason and "maven" in reason
    assert "no " + RUNTIMES_LABEL in undeclared_reason(None)


def test_an_image_that_declares_maven_is_not_refused():
    for label in ("java maven", "gradle java kotlin maven node python sqlite"):
        assert undeclared_reason(label) is None
