"""A corpus that names an image profile, exported against a real toolchain checkout.

⭐ The same export as `test_profile_export.py`, but the toolchain is a real checkout that
computes the profile's tags and the course layer's builds, and the corpus carries a real Gradle
prime. Nothing is built here: the test writes the tree a learner would build from, and leaves it
in `STUDYFORGE_PROFILE_OUT` for the container steps: `docker compose build runner` over it,
with the layers' network off.
⚠️ Skipped unless it is told where to look:

- `STUDYFORGE_PROFILE_TOOLCHAIN`: a code-server-toolchain checkout that carries the profile;
- `STUDYFORGE_PROFILE_RUNNER_DIGEST`: the `sha256:` image id of the profile's runner, built from
  that checkout (the lock names it, and the course layer starts from it);
- `STUDYFORGE_PROFILE_OUT`: a new or empty directory for the exported tree, never under the
  host's temporary directory, which a Docker Desktop VM cannot mount.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from studyforge.execute import published
from studyforge.skills.execution.standalone import bases, vendor, write
from tests.studyforge.skills.execution.standalone.test_bases import lock, parsed
from tests.studyforge.skills.execution.standalone.test_profile_export import (
    DECLARED,
    GIT,
    NAME,
)

CHECKOUT, DIGEST, OUT = (
    os.environ.get(name)
    for name in (
        "STUDYFORGE_PROFILE_TOOLCHAIN",
        "STUDYFORGE_PROFILE_RUNNER_DIGEST",
        "STUDYFORGE_PROFILE_OUT",
    )
)
needs_toolchain = pytest.mark.skipif(
    not (CHECKOUT and DIGEST and OUT),
    reason=(
        "set STUDYFORGE_PROFILE_TOOLCHAIN, STUDYFORGE_PROFILE_RUNNER_DIGEST "
        "and STUDYFORGE_PROFILE_OUT"
    ),
)

RUNTIMES = "gradle,java,kotlin,node,python"
PLATFORM = ("--platform", "linux/amd64")
PRIME_BUILD = """plugins {
    kotlin("jvm") version "2.4.20"
}

repositories {
    mavenCentral()
}

kotlin {
    jvmToolchain(25)
}

dependencies {
    testImplementation(kotlin("test"))
}

tasks.test {
    useJUnitPlatform()
}
"""
GREETING = "fun greeting(name: String): String = \"hello, $name\"\n"
GREETING_TEST = """import kotlin.test.Test
import kotlin.test.assertEquals

class GreetingTest {
    @Test
    fun greets() {
        assertEquals("hello, claude", greeting("claude"))
    }
}
"""


def run(argv, cwd):
    """The caller's one way in: a real process, `python3` being this interpreter."""
    done = subprocess.run(
        [sys.executable if one == "python3" else one for one in argv],
        cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return done.returncode, done.stdout


def real_course(where: Path, declared: Path = DECLARED) -> Path:
    """The fixture's corpus with a Gradle prime and the primed tags the real toolchain computes."""
    root = Path(shutil.copytree(DECLARED.parent, where))
    if declared != DECLARED:
        shutil.copyfile(declared, root / "corpus.json")
    prime = root / ".studyforge" / "execution" / "prime" / "gradle"
    (prime / "src" / "main" / "kotlin").mkdir(parents=True)
    (prime / "src" / "test" / "kotlin").mkdir(parents=True)
    (prime / "gradle").mkdir()
    (prime / "settings.gradle.kts").write_text('rootProject.name = "prime"\n', encoding="utf-8")
    (prime / "build.gradle.kts").write_text(PRIME_BUILD, encoding="utf-8")
    (prime / "src" / "main" / "kotlin" / "Greeting.kt").write_text(GREETING, encoding="utf-8")
    test = prime / "src" / "test" / "kotlin" / "GreetingTest.kt"
    test.write_text(GREETING_TEST, encoding="utf-8")
    shutil.copyfile(
        Path(CHECKOUT) / "profiles" / NAME / "jvm" / "gradle" / "verification-metadata.xml",
        prime / "gradle" / "verification-metadata.xml",
    )
    (root / ".studyforge" / "execution" / "runservice.pl").write_text(
        published.run_service_script(), encoding="utf-8"
    )
    for image, env, variable in (
        ("runner", "runner.env", "STUDYFORGE_RUNNER_IMAGE"),
        ("editor", "editor.env", "EDITOR_IMAGE"),
    ):
        code, printed = run(
            ["python3", "consuming/builds.py", image, "--runtimes", RUNTIMES, "--prime",
             str(root / ".studyforge" / "execution" / "prime"), "--platform", "linux/amd64"],
            Path(CHECKOUT),
        )
        assert code == 0, image
        # the course records the tag of its primed image: the toolchain's own, asked just now
        tag = json.loads(printed)["tag"]
        recorded = root / ".studyforge" / "execution" / env
        recorded.write_text(f"{variable}={tag}\n", encoding="utf-8")
    subprocess.run([*GIT, "init", "-q"], cwd=root, check=True)
    subprocess.run([*GIT, "add", "-A"], cwd=root, check=True)
    subprocess.run([*GIT, "commit", "-q", "-m", "fixture"], cwd=root, check=True)
    return root


def computed(image: str) -> str:
    code, printed = run(
        ["python3", "docker/profile_packages/package_build.py", "--profile", NAME, "--image", image,
         "--runtimes", RUNTIMES, "--platform", "linux/amd64", "--print-tag"],
        Path(CHECKOUT),
    )
    assert code == 0
    return printed.strip().split(":", 1)[1]


def base_lock(**profile) -> bases.Bases:
    """A lock of the real tags: the bases' (computed by the toolchain) and the profile's runner."""
    code, printed = run(
        ["python3", "consuming/builds.py", "runner", "--runtimes", RUNTIMES, *PLATFORM],
        Path(CHECKOUT),
    )
    editor = run(
        ["python3", "consuming/builds.py", "editor", "--runtimes", RUNTIMES, *PLATFORM],
        Path(CHECKOUT),
    )[1]
    entry = {
        "name": NAME,
        "runner": {
            "image": bases.profile_image("runner", NAME),
            "tag": computed("runner"),
            "digest": DIGEST,
        },
        **profile,
    }
    document = lock(
        runner={**lock()["runner"], "tag": json.loads(printed)["tag"].split(":", 1)[1]},
        editor={**lock()["editor"], "tag": json.loads(editor)["tag"].split(":", 1)[1]},
        profile=entry,
    )
    return parsed(document)


@needs_toolchain
def test_the_real_toolchain_computes_the_profile_the_lock_names_and_the_layer_starts_from_it(
    tmp_path,
):
    root = real_course(tmp_path / "course")
    out = Path(OUT)
    made = write.release(
        root, out, toolchain=Path(CHECKOUT), platform="linux/amd64", bases=base_lock(), run=run
    )
    built = (out / "compose.yaml").read_text(encoding="utf-8")
    runner = f"{bases.profile_image('runner', NAME)}:{computed('runner')}@{DIGEST}"
    assert runner in built
    assert made.names.runner_base.endswith(f"{computed('runner')}@{DIGEST}")
    document = json.loads((out / write.MANIFEST).read_text(encoding="utf-8"))
    assert document["bases"]["profile"]["runner"]["tag"] == computed("runner")
    assert document["bases"]["profile"]["name"] == NAME
    assert "editor" not in document["bases"]["profile"]


@needs_toolchain
def test_the_real_toolchain_refuses_an_unknown_profile_and_a_tag_it_does_not_compute(tmp_path):
    unknown = tmp_path / "unknown.json"
    declared = json.loads(DECLARED.read_text(encoding="utf-8"))
    unknown.write_text(json.dumps({**declared, "profile": "no-such-profile"}), encoding="utf-8")
    with pytest.raises(vendor.VendorRefused, match="refused profile no-such-profile"):
        write.release(
            real_course(tmp_path / "a", unknown), tmp_path / "out-a", toolchain=Path(CHECKOUT),
            platform="linux/amd64", bases=base_lock(), run=run,
        )
    stale = base_lock()
    stale = parsed(
        lock(
            runner={**lock()["runner"], "tag": stale.runner.tag},
            editor={**lock()["editor"], "tag": stale.editor.tag},
            profile={
                "name": NAME,
                "runner": {
                    "image": bases.profile_image("runner", NAME), "tag": "stale", "digest": DIGEST,
                },
            },
        )
    )
    with pytest.raises(bases.BasesRefused, match="is locked at tag stale"):
        write.release(
            real_course(tmp_path / "b"), tmp_path / "out-b", toolchain=Path(CHECKOUT),
            platform="linux/amd64", bases=stale, run=run,
        )
    assert not (tmp_path / "out-b").exists()
