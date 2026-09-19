"""Mirror of `src/studyforge/serve/__init__.py` (R12) — and the package's no-spawn property.

⛔ **E05: "The package does not import a process-spawning library — asserted."**
Three arms, each with its own plant: the source of every module is read (`spawns`),
a fresh interpreter imports the package and reports what it loaded, and no module
names the Docker socket or a Docker client (spec §8.3).

⭐ **`SF-22` narrows the second arm, and says so rather than loosening it.** `serve`
depends on `execute` — the runner, the one package that runs a corpus's commands —
through `routes/run.py` and `routes/runs.py` and nowhere else. So the fresh interpreter
imports `execute` FIRST and then asks what importing `serve` loaded on top of it:
nothing. ⛔ The other reading is taken too — without that pre-import the same instrument
DOES see the process library `execute` brings — and a fourth test pins the importers.
"""

from __future__ import annotations

import ast
import json
import sys

import pytest

from studyforge import serve
from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.manifest import MANIFEST_FILENAME
from studyforge.serve import RAISES
from studyforge.serve.discovery import DiscoveryRefused, discover
from tests.studyforge.generate.corpora import a_corpus
from tests.studyforge.serve.serving import LEAK
from tests.support import assert_package_contract, repository_root, run

PACKAGE = repository_root() / "src" / "studyforge" / "serve"

#: The modules SF-19a and SF-19b wrote. ⭐ The scan must reach at least these — a
#: scan whose population silently shrank would pass on nothing.
THIS_ROW = frozenset(
    {
        "__init__.py",
        "app.py",
        "caching.py",
        "response.py",
        "security.py",
        "routes/__init__.py",
        "routes/content.py",
        "routes/assets.py",
        "addressing.py",
        "discovery.py",
        "instance.py",
        "routes/state.py",
        "routes/run.py",
        "routes/runs.py",
    }
)

#: ⛔ The two modules of this package that may import the runner (`SF-22`): the
#: namespace and, split from it at its seam, what a started run is.
EXECUTE = "studyforge.execute"
RUNNER_IMPORTERS = frozenset({"routes/run.py", "routes/runs.py"})

SPAWNING_MODULES = (
    "subprocess",
    "_posixsubprocess",
    "multiprocessing",
    "pty",
    "asyncio.subprocess",
    "concurrent.futures.process",
)
SPAWNING_OS = frozenset({"system", "popen", "fork", "forkpty", "posix_spawn", "posix_spawnp"})
SPAWNING_FROM = {
    "asyncio": frozenset({"create_subprocess_exec", "create_subprocess_shell", "subprocess"}),
    "concurrent.futures": frozenset({"ProcessPoolExecutor", "process"}),
}


def _spawning_module(name: str) -> bool:
    return any(name == module or name.startswith(module + ".") for module in SPAWNING_MODULES)


def _spawning_os(name: str) -> bool:
    return name in SPAWNING_OS or name.startswith(("exec", "spawn"))


def _dynamic_import(node: ast.Call) -> str | None:
    func = node.func
    named = (isinstance(func, ast.Name) and func.id == "__import__") or (
        isinstance(func, ast.Attribute) and func.attr == "import_module"
    )
    first = node.args[0] if node.args else None
    if named and isinstance(first, ast.Constant) and isinstance(first.value, str):
        return first.value
    return None


def spawns(source: str) -> list[str]:
    """Every way `source` reaches a process-spawning library, by name."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found += [alias.name for alias in node.names if _spawning_module(alias.name)]
        elif isinstance(node, ast.ImportFrom) and node.module:
            if _spawning_module(node.module):
                found.append(node.module)
            elif node.module == "os":
                found += [f"os.{a.name}" for a in node.names if _spawning_os(a.name)]
            elif node.module in SPAWNING_FROM:
                wanted = SPAWNING_FROM[node.module]
                found += [f"{node.module}.{a.name}" for a in node.names if a.name in wanted]
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id == "os" and _spawning_os(node.attr):
                found.append(f"os.{node.attr}")
        elif isinstance(node, ast.Call):
            name = _dynamic_import(node)
            if name is not None and _spawning_module(name):
                found.append(name)
    return found


def _docstrings(tree: ast.Module) -> set[int]:
    owners = [tree, *(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef | ast.FunctionDef))]
    return {
        id(owner.body[0].value)
        for owner in owners
        if owner.body
        and isinstance(owner.body[0], ast.Expr)
        and isinstance(owner.body[0].value, ast.Constant)
    }


def reaches_docker(source: str) -> list[str]:
    """Every Docker client import, and every non-docstring string naming the socket."""
    tree = ast.parse(source)
    skipped = _docstrings(tree)
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [a.name for a in node.names if a.name.split(".")[0] == "docker"]
        elif isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] == "docker":
            found.append(node.module)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) not in skipped and "docker.sock" in node.value:
                found.append(node.value)
    return found


def package_modules() -> dict[str, str]:
    return {
        path.relative_to(PACKAGE).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(PACKAGE.rglob("*.py"))
    }


def test_states_its_contract():
    assert_package_contract(serve, "studyforge.serve")


def no_corpus(root):
    return root


def a_leaking_manifest(root):
    manifest = a_corpus(root, "depth1") / MANIFEST_FILENAME
    document = json.loads(manifest.read_text(encoding="utf-8"))
    document["title"] = LEAK
    manifest.write_text(json.dumps(document), encoding="utf-8")
    return root


#: ⛔ `W208`: every member of `RAISES` reached from `discover` by a fixture.
REACHES = {DiscoveryRefused: no_corpus, PersonalDataLeak: a_leaking_manifest}


def test_every_member_of_raises_has_a_fixture_and_nothing_else_does():
    assert set(REACHES) == set(RAISES)


@pytest.mark.parametrize("member", RAISES, ids=lambda m: m.__name__)
def test_each_member_of_raises_is_reached_from_discovery(tmp_path, member):
    root = REACHES[member](tmp_path)
    with pytest.raises(member) as raised:
        discover(root)
    assert str(tmp_path) not in str(raised.value)


def test_the_scan_reaches_every_module_this_row_wrote():
    found = set(package_modules())
    assert THIS_ROW <= found, sorted(THIS_ROW - found)


def test_no_module_in_the_package_reaches_a_process_spawning_library():
    modules = package_modules()
    assert len(modules) >= len(THIS_ROW)
    assert {name: hits for name, text in modules.items() if (hits := spawns(text))} == {}


@pytest.mark.parametrize(
    "planted",
    [
        "import subprocess",
        "import subprocess as sp",
        "from subprocess import run",
        "import multiprocessing.pool",
        "from multiprocessing import Process",
        "import pty",
        "from os import system",
        "from os import execv",
        "import os\nos.popen('x')",
        "import os\nos.posix_spawn('x', [], {})",
        "from asyncio import create_subprocess_exec",
        "from concurrent.futures import ProcessPoolExecutor",
        "__import__('subprocess')",
        "import importlib\nimportlib.import_module('subprocess')",
    ],
)
def test_the_detector_fires_on_every_planted_spelling(planted):
    assert spawns(planted), planted


@pytest.mark.parametrize(
    "legitimate",
    [
        "import os.path",
        "from os import stat_result",
        "import http.server",
        "import os\nos.stat('x')",
    ],
)
def test_the_detector_passes_what_the_package_legitimately_imports(legitimate):
    assert spawns(legitimate) == []


CHILD = """
import importlib, json, pkgutil, sys
sys.path.insert(0, sys.argv[1])
watched = ("subprocess", "_posixsubprocess", "multiprocessing", "pty")
if sys.argv[2] == "runner-first":
    importlib.import_module("studyforge.execute")
before = {name for name in watched if name in sys.modules}
package = importlib.import_module("studyforge.serve")
names = [found.name for found in pkgutil.walk_packages(package.__path__, "studyforge.serve.")]
for name in names:
    importlib.import_module(name)
after = {name for name in watched if name in sys.modules}
print(json.dumps({"imported": len(names) + 1, "loaded": sorted(after - before)}))
"""


def fresh_import(how: str) -> dict:
    """Import the whole package in a fresh interpreter; report what it loaded."""
    argv = [sys.executable, "-c", CHILD, str(repository_root() / "src"), how]
    result = run(argv, repository_root())
    assert result.returncode == 0, result.stderr
    reading = json.loads(result.stdout.strip().splitlines()[-1])
    assert reading["imported"] == len(package_modules())
    return reading


def test_importing_the_whole_package_loads_no_process_library_beyond_the_runners():
    assert fresh_import("runner-first")["loaded"] == []


def test_without_the_runner_imported_first_the_same_instrument_sees_what_it_brings():
    # ⭐ The other reading: the pre-import above is what excuses the process library,
    # and it excuses only the runner's — so the arm is not blind.
    assert "subprocess" in fresh_import("bare")["loaded"]


def imports_of(source: str) -> set[str]:
    """Every module an `import` or `from … import` in `source` names."""
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def test_only_the_run_route_and_its_runs_import_the_runner():
    modules = package_modules()
    importers = {
        name
        for name, text in modules.items()
        if any(m == EXECUTE or m.startswith(EXECUTE + ".") for m in imports_of(text))
    }
    assert importers == RUNNER_IMPORTERS
    assert imports_of("from studyforge.execute.runner import Runner") == {EXECUTE + ".runner"}


def test_no_module_in_the_package_names_the_docker_socket_or_a_docker_client():
    modules = package_modules()
    assert {name: hits for name, text in modules.items() if (hits := reaches_docker(text))} == {}


@pytest.mark.parametrize(
    "planted",
    ["import docker", "from docker import from_env", "SOCKET = '/var/run/docker.sock'"],
)
def test_the_docker_detector_fires_on_every_planted_spelling(planted):
    assert reaches_docker(planted), planted


def test_the_docker_detector_skips_a_docstring_that_explains_the_rule():
    assert reaches_docker('"""The docker.sock is never mounted."""\n') == []
