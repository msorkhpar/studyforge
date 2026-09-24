"""The prime the skill writes is the one the REAL component builds from.

⭐ **Read against the sibling itself rather than a restatement of it.** A
fixture corpus with its own Maven build at its root AND
an emitted exercise whose build role names a library nobody can resolve is run
through `onboard.generate` with the sibling's own `consuming.json` at its pin.
The prime it writes is handed to the sibling's own `tag_from` and `built_by`
argv — each substituted by `toolchain.select` from the contract's `runner`
block, the prime flag from `runner.prime.declared_by` — and ⛔ **no tag is typed**.

⛔ **And the negative, by name** (R12): the same files laid out at their
corpus-relative paths, are refused by the component before Docker starts,
naming the directory it will not warm.

⭐ **Two consents, because two things differ.** The tag cases run the sibling's
build script with `--print-tag`, which reads and guards the prime and starts no
Docker: they need only the sibling at its pin. ⚠️ The build case builds an image
(pulling the sibling's pinned inputs and the prime's JUnit through the warmer's
placeholder User-Agent), so it is opt-in behind
`STUDYFORGE_RUNNER_BUILDS=1`, is a HOST reading, and is taken holding the shared
container lock.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from studyforge.corpus.manifest import parse
from studyforge.exercise.bundle import emit, write
from studyforge.skills.execution import onboard, toolchain
from tests.studyforge.execute import container
from tests.studyforge.exercise.bundle import dependency
from tests.studyforge.exercise.bundle.test_dependency_image import CONSENT, sibling
from tests.studyforge.skills.execution.contracts import manifest_document
from tests.support import tool_on_path

#: What the corpus declares: a language and the build tool the component seeds.
RUNTIMES = ["java", "maven"]


@pytest.fixture(scope="module")
def contract():
    """The sibling's whole contract at its pin, or a skip naming why not."""
    reason = container.declaration_reason()
    if reason is not None:
        pytest.skip(reason)
    return container.contract_reading().text


def corpus(root: Path) -> Path:
    """A corpus whose own build is at its root, and one emitted exercise beneath it."""
    put(root / "pom.xml", dependency.pom("w440-corpus", library=False))
    source = dependency.PRIME_SOURCE.format(expression='"Hello, prime"')
    put(root / "src/main/java/prime/Prime.java", source)
    put(root / "src/test/java/prime/PrimeTest.java", dependency.PRIME_TEST)
    put(root / "src/one.md", "# One\n")
    bundle = dependency.write_bundle(root)
    write(root, emit(root, bundle, source="demo", ingested="2026-01-05"), "the exercise")
    return root


def generated(root: Path, text: str) -> onboard.Execution:
    """Run the skill over `root` with the sibling's contract, and write what it made."""
    document = manifest_document(
        runtimes=RUNTIMES, content={"include": ["src/**/*.md"], "exclude": []}
    )
    made = onboard.generate(parse(json.dumps(document)), editor_text=text, root=root)
    onboard.write(made, root)
    return made


def argv(text: str, key: str, prime: Path | None) -> list[str]:
    """The runner block's own argv, the set substituted by the framework, the prime by the flag."""
    whole = json.loads(text)
    selection = toolchain.select(RUNTIMES, whole, block="runner")
    command = list(selection.tag_from if key == "tag_from" else selection.build)
    if prime is not None:
        flag = whole["runner"]["prime"]["declared_by"].split()
        command += [str(prime) if part == onboard.DIRECTORY_SLOT else part for part in flag]
    return command


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=sibling(), stdin=subprocess.DEVNULL, capture_output=True, text=True
    )


def test_the_skills_prime_is_one_the_component_accepts_and_folds_into_its_tag(contract, tmp_path):
    root = corpus(tmp_path / "corpus")
    generated(root, contract)
    primed = run(argv(contract, "tag_from", root / onboard.PRIME_DIR))
    assert primed.returncode == 0, primed.stderr[-2000:]
    bare = run(argv(contract, "tag_from", None))
    assert bare.returncode == 0, bare.stderr[-2000:]
    assert primed.stdout.strip() and primed.stdout.strip() != bare.stdout.strip()


def test_the_exercise_build_role_never_reaches_the_prime(contract, tmp_path):
    root = corpus(tmp_path / "corpus")
    made = generated(root, contract)
    assert made.primed.build_files == ("pom.xml",)
    held = [one for one in (root / onboard.PRIME_DIR).rglob("*") if one.is_file()]
    assert all(dependency.COORDINATES.split(":")[1] not in one.read_text() for one in held)


def test_the_old_layout_is_refused_by_the_component_by_name(contract, tmp_path):
    # ⛔ The refused layout: every file at its corpus-relative path.
    root = corpus(tmp_path / "corpus")
    made = generated(root, contract)
    old = tmp_path / "old-prime"
    for _, origin in made.primed.copies():
        put(old / origin, (root / origin).read_text(encoding="utf-8"))
    refused = run(argv(contract, "tag_from", old))
    assert refused.returncode == 2, refused.stdout + refused.stderr
    assert "a prime holds only" in refused.stderr and "'src'" in refused.stderr


def test_a_runner_is_built_from_the_skills_prime(contract, tmp_path):
    if os.environ.get(CONSENT) != "1":
        pytest.skip(f"set {CONSENT}=1 to let this module build the sibling's runner image")
    if tool_on_path("docker") is None:
        pytest.skip("no docker CLI in this environment (the pinned dev image carries none)")
    root = corpus(tmp_path / "corpus")
    generated(root, contract)
    prime = root / onboard.PRIME_DIR
    tag = run(argv(contract, "tag_from", prime)).stdout.strip()
    built = run(argv(contract, "built_by", prime))
    assert built.returncode == 0, (built.stdout + built.stderr)[-4000:]
    label = json.loads(contract)["runner"]["image"]["labels"]["runtimes"]
    read = subprocess.run(
        ["docker", "image", "inspect", "--format", f'{{{{index .Config.Labels "{label}"}}}}', tag],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    assert read.returncode == 0, read.stderr
    assert set(RUNTIMES) <= set(read.stdout.replace(",", " ").replace("-", " ").split())


def put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
