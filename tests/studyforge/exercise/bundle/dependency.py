"""A graded exercise whose tests import a library the JDK does not carry.

⭐ **The dependency is BUILT HERE, never downloaded.** `tiny` is one class
compiled and jarred inside the runner image this module is handed, with no
network, and the only way it reaches a graded run is the channel the build role
declares: the exercise's build role names it, and the runner's prime carries
it. ⛔ **No jar is ever written into the corpus**, and the exercise's
own build file names no repository, so nothing else could resolve it.

⭐ **Two primes, one fact apart.** `write_prime(directory, jar)` warms the
library and JUnit; `write_prime(directory, None)` warms JUnit alone. The same
exercise in the second fails naming the library — which isolates the
dependency as what the channel carried, rather than anything else the warm
happened to fetch.

⚠️ **The fixture's prime stands in for Maven Central with a `file:` repository
inside the prime directory**, because the dependency exists nowhere else. It is
read once, by the image build's warm, and never by a graded run: the seed the
warm leaves carries no record of where a file came from.

⛔ **Every image tag is ASKED of the sibling** through the argv its contract
declares, and never typed: the tag is a function of the build's inputs.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from studyforge.address import Address
from studyforge.exercise.bundle import RUN_OUTPUT_DIRNAME, Bundle, Places, bundle_of
from tests.harness import engine

#: The declared set the runner is built for: the language and its build tool.
RUNTIMES = "java,maven"

#: The slot the contract's argv leaves for the set, and the one its prime flag leaves.
SET_SLOT = "<the declared set>"
DIRECTORY_SLOT = "<directory>"

#: The library's coordinates. ⚠️ `example` names: nothing here is anybody's.
GROUP, ARTIFACT, VERSION = "org.example.w436", "tiny", "1.0"
COORDINATES = f"{GROUP}:{ARTIFACT}"

LIBRARY_SOURCE = """package org.example.w436.tiny;

public final class Greeting {
    private Greeting() {}

    public static String of(String who) {
        return "Hello, " + who;
    }
}
"""

#: ⭐ Compiled and jarred with a fixed date, so the jar — and so the primed
#: image's tag, which folds the prime's bytes — is the same on every run.
COMPILE = (
    "javac --release 25 -d classes Greeting.java"
    " && jar --create --file tiny.jar --date=2000-01-01T00:00:00Z -C classes ."
)

JUNIT = """    <dependency>
      <groupId>org.junit.jupiter</groupId>
      <artifactId>junit-jupiter</artifactId>
      <version>5.14.4</version>
      <scope>test</scope>
    </dependency>
"""

LIBRARY = f"""    <dependency>
      <groupId>{GROUP}</groupId>
      <artifactId>{ARTIFACT}</artifactId>
      <version>{VERSION}</version>
    </dependency>
"""

FIXTURE_REPOSITORY = """  <repositories>
    <repository>
      <id>w436-fixture</id>
      <url>file://${project.basedir}/repo</url>
    </repository>
  </repositories>
"""


def pom(artifact: str, *, library: bool, repository: bool = False) -> str:
    """A Maven build naming JUnit, and the library when asked. ⭐ Maven's own layout."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>{GROUP}</groupId>
  <artifactId>{artifact}</artifactId>
  <version>1</version>
  <properties>
    <maven.compiler.release>25</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>
{FIXTURE_REPOSITORY if repository else ""}  <dependencies>
{LIBRARY if library else ""}{JUNIT}  </dependencies>
</project>
"""


PRIME_SOURCE = """package prime;

public final class Prime {{
    public static String greet() {{
        return {expression};
    }}
}}
"""

PRIME_TEST = """package prime;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class PrimeTest {
    @Test
    void greets() {
        assertEquals("Hello, prime", Prime.greet());
    }
}
"""


def build_library(directory: Path, image: str) -> bytes:
    """Compile and jar the library inside `image`, with no network. ⛔ Nothing is fetched."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "Greeting.java").write_text(LIBRARY_SOURCE, encoding="utf-8")
    done = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            *engine.run_as(),
            "-v",
            f"{engine.bindable(directory)}:/work",
            "-w",
            "/work",
            image,
            "sh",
            "-c",
            COMPILE,
        ],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, f"the library did not build: {done.stdout}{done.stderr}"
    return (directory / "tiny.jar").read_bytes()


def write_prime(directory: Path, jar: bytes | None) -> Path:
    """A prime in the component's own shape (`DIR/maven/`); with the library when `jar` is given.

    ⚠️ A prime must compile a real source and run a real test, or the warm
    refuses it, so each one's source uses what its build declares.
    """
    maven = directory / "maven"
    expression = 'org.example.w436.tiny.Greeting.of("prime")' if jar else '"Hello, prime"'
    _put(maven / "pom.xml", pom("w436-prime", library=jar is not None, repository=jar is not None))
    _put(maven / "src/main/java/prime/Prime.java", PRIME_SOURCE.format(expression=expression))
    _put(maven / "src/test/java/prime/PrimeTest.java", PRIME_TEST)
    if jar is not None:
        _publish(maven / "repo", jar)
    return directory


def _publish(repository: Path, jar: bytes) -> None:
    """Lay the library out as a Maven repository does, checksums included (the warm is `-C`)."""
    folder = repository / GROUP.replace(".", "/") / ARTIFACT / VERSION
    described = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<project xmlns="http://maven.apache.org/POM/4.0.0">\n'
        "  <modelVersion>4.0.0</modelVersion>\n"
        f"  <groupId>{GROUP}</groupId>\n  <artifactId>{ARTIFACT}</artifactId>\n"
        f"  <version>{VERSION}</version>\n</project>\n"
    ).encode()
    named = ((f"{ARTIFACT}-{VERSION}.jar", jar), (f"{ARTIFACT}-{VERSION}.pom", described))
    for name, data in named:
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_bytes(data)
        (folder / f"{name}.sha1").write_text(hashlib.sha1(data).hexdigest(), encoding="utf-8")
        (folder / f"{name}.md5").write_text(hashlib.md5(data).hexdigest(), encoding="utf-8")


REFERENCE = """package fixture;

import org.example.w436.tiny.Greeting;

public final class Greeter {
    public static String greet(String who) {
        return who.isBlank() ? "" : Greeting.of(who);
    }
}
"""

STARTER = """package fixture;

public final class Greeter {
    public static String greet(String who) {
        return null;
    }
}
"""

TESTS = """package fixture;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.example.w436.tiny.Greeting;
import org.junit.jupiter.api.Test;

class GreeterTest {
    @Test
    void greets() {
        assertEquals(Greeting.of("Ada"), Greeter.greet("Ada"));
    }

    @Test
    void blank() {
        assertEquals("", Greeter.greet(" "));
    }
}
"""

#: The solution planted to ignore the edge case: it greets a blank name too.
PLANT = REFERENCE.replace('who.isBlank() ? "" : ', "")

MAIN_FILE = "src/main/java/fixture/Greeter.java"
TEST_FILE = "src/test/java/fixture/GreeterTest.java"
BUILD_FILE = "pom.xml"

#: Where the exercise sits: one address, one unit, one practice.
PLACES = Places(Address(["deps"]), "java", 1, 1)


def document(*, build: bool = True) -> dict:
    """The exercise's `bundle.json`. ⭐ The command names its build file workspace-relatively."""
    command = ["mvn", "-o", "-q", "-f", PLACES.in_workspace(BUILD_FILE)]
    declared = {
        "bundle_api": 1,
        "address": list(PLACES.address.segments),
        "variant": PLACES.variant,
        "unit": PLACES.unit,
        "ordinal": PLACES.ordinal,
        "title": "Greet through a library",
        "lang": "java",
        "main_file": MAIN_FILE,
        "test_file": TEST_FILE,
        "run_command": [*command, "compile"],
        "test_command": [*command, "test"],
        "provenance": "generated",
        "trust": "advisory",
        "cases": [
            {"id": "fixture.GreeterTest#greets", "kind": "main", "says": "greets by name"},
            {
                "id": "fixture.GreeterTest#blank",
                "kind": "edge",
                "says": "a blank name greets nobody",
            },
        ],
        "report": {"format": "junit", "path": f"{RUN_OUTPUT_DIRNAME}/surefire-reports"},
        "origin": {"path": "src/one.md", "section": "Greeting"},
    }
    if build:
        declared["build"] = [BUILD_FILE]
    return declared


def write_bundle(root: Path, *, build: bool = True) -> Bundle:
    """Write the exercise's bundle under `root` and return what it declares."""
    declared = document(build=build)
    bundle = bundle_of(declared, "bundle.json")
    where = root / bundle.places.bundle
    _put(where / "bundle.json", json.dumps(declared, indent=2) + "\n")
    _put(where / "statement.md", "Greet somebody through the library.\n")
    _put(where / "starter" / MAIN_FILE, STARTER)
    _put(where / "reference" / MAIN_FILE, REFERENCE)
    _put(where / "tests" / TEST_FILE, TESTS)
    _put(where / "plants" / "edge-1" / MAIN_FILE, PLANT)
    if build:
        _put(where / "build" / BUILD_FILE, pom("w436-exercise", library=True))
    return bundle


def names_no_repository(text: str) -> bool:
    """Whether a build file names no repository and no file of its own to resolve from."""
    return not re.search(r"<repositor|<systemPath|file:", text)


def contract_argv(runner: dict, key: str, *, prime: Path | None = None) -> list[str]:
    """The contract's own argv under `runner.image.<key>`, the set and the prime filled in."""
    argv = [RUNTIMES if part == SET_SLOT else part for part in runner["image"][key]]
    if prime is not None:
        flag = runner["prime"]["declared_by"].split()
        argv += [str(prime) if part == DIRECTORY_SLOT else part for part in flag]
    return argv


def image_for(runner: dict, sibling: Path, *, prime: Path | None = None) -> str:
    """Ask the sibling for the tag, and build the image only when this daemon lacks it."""
    tag = _run(contract_argv(runner, "tag_from", prime=prime), sibling).stdout.strip()
    held = subprocess.run(
        ["docker", "image", "inspect", tag], stdin=subprocess.DEVNULL, capture_output=True
    )
    if held.returncode != 0:
        _run(contract_argv(runner, "built_by", prime=prime), sibling)
    return tag


def _run(argv: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    done = subprocess.run(
        argv, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False
    )
    assert done.returncode == 0, (
        f"the sibling's argv failed: {done.stdout[-2000:]}{done.stderr[-2000:]}"
    )
    return done


def _put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
