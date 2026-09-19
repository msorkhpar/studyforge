"""Who in `src/` may start a process — a sweep of the whole tree (`W361`, `SF-20/4`, `SF-22/6`).

⛔ **E05's settled sentence:** `execute` is the only package that runs a corpus's
commands and the only package permitted to start a process, save two named sites
that each ask the local `git` a fixed question about a source checkout. Any other
package reaches a process only by handing a command to `execute`.

⭐ What this file asserts, each clause both ways:

- **the closed list** — every module outside `execute/` that reaches a
  process-spawning library is one of the named sites; a start planted anywhere
  else, in a temp copy of the tree, is refused by that module's name, and one
  planted inside `execute/` is not;
- **the list is not stale** — each named site still starts a process, so a site
  that stops needing one takes its name out of the epic rather than leaving an
  excuse behind;
- **the exceptions ask `git`** — every process call in a named site hands an argv
  literal whose first element is the resolved `git`, and a planted other program
  is refused;
- **the epic names the list** — `SF-20`'s section in `E05` names each site;
- **the detector knows every standard-library way to start a process** (`W375`) —
  each entry of each of its tables is planted under each spelling it can take and
  fires, and a lookalike of each is planted and passes; `webbrowser` among them.

⭐ The detector is ONE, `tests/spawning.py`'s `spawns`, shared with `serve`'s
no-spawn test — so neither file's rename breaks the other, and one list answers
both questions (`W375`, closing `W361/2` and `W361/3`).
"""

from __future__ import annotations

import ast
import json
import shutil
import sys
from pathlib import Path

import pytest

from tests.spawning import SPAWNING_FROM, SPAWNING_MODULES, SPAWNING_OS, spawns
from tests.support import repository_root, run

SOURCE = repository_root() / "src" / "studyforge"
EPIC = repository_root() / "docs" / "tasks" / "E05-serving-execution.md"

#: The package that runs a corpus's commands (`SF-20`).
RUNNER = "execute"

#: ⛔ The named sites outside the runner, relative to the package root.
EXCEPTIONS = frozenset({"validate/source/enumeration.py", "skills/onboarding/pin.py"})

#: The name every named site's argv starts with — the resolved `git`.
GIT = "git"

#: What a process call is spelled as in a named site.
PROCESS_CALLS = frozenset({"run", "Popen", "call", "check_call", "check_output"})


def modules(root: Path) -> dict[str, str]:
    """Every Python module beneath `root`, by its relative path."""
    return {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*.py"))
        if "__pycache__" not in path.parts
    }


def starters(root: Path) -> dict[str, list[str]]:
    """Every module beneath `root` that reaches a process-spawning library, and how."""
    return {name: hits for name, text in modules(root).items() if (hits := spawns(text))}


def unexcused(root: Path) -> dict[str, list[str]]:
    """The starters the settled sentence does not permit."""
    return {
        name: hits
        for name, hits in starters(root).items()
        if name.split("/")[0] != RUNNER and name not in EXCEPTIONS
    }


def process_calls(source: str) -> list[ast.Call]:
    """Every `subprocess.<call>(…)` in `source`."""
    return [
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr in PROCESS_CALLS
    ]


def not_git(source: str) -> list[str]:
    """Each process call whose argv is not a literal list starting with `git`, unparsed."""
    refused = []
    for call in process_calls(source):
        argv = call.args[0] if call.args else None
        first = argv.elts[0] if isinstance(argv, ast.List) and argv.elts else None
        if not (isinstance(first, ast.Name) and first.id == GIT):
            refused.append(ast.unparse(call))
    return refused


def a_copy(tmp_path: Path) -> Path:
    root = tmp_path / "studyforge"
    shutil.copytree(SOURCE, root, ignore=shutil.ignore_patterns("__pycache__"))
    return root


# --- the real tree ---------------------------------------------------------


def test_the_sweep_reads_every_package_in_the_tree():
    packages = {p.parent.relative_to(SOURCE).as_posix() for p in SOURCE.rglob("__init__.py")}
    scanned = {name.rsplit("/", 1)[0] if "/" in name else "." for name in modules(SOURCE)}
    assert packages <= scanned
    assert RUNNER in packages


def test_nothing_outside_the_runner_and_the_named_sites_starts_a_process():
    assert unexcused(SOURCE) == {}


def test_the_runner_starts_processes_so_the_sweep_is_not_blind():
    assert any(name.split("/")[0] == RUNNER for name in starters(SOURCE))


@pytest.mark.parametrize("site", sorted(EXCEPTIONS))
def test_each_named_site_still_starts_a_process(site):
    assert site in starters(SOURCE), f"{site} starts nothing: take it out of E05's list"


@pytest.mark.parametrize("site", sorted(EXCEPTIONS))
def test_each_named_site_asks_git_and_nothing_else(site):
    source = (SOURCE / site).read_text(encoding="utf-8")
    assert set(spawns(source)) == {"subprocess"}, "a named site imports `subprocess` plainly"
    assert process_calls(source), site
    assert not_git(source) == []


def sf20_section() -> str:
    text = EPIC.read_text(encoding="utf-8")
    start = text.index("### SF-20 ")
    return text[start : text.index("\n### ", start + 1)]


@pytest.mark.parametrize("site", sorted(EXCEPTIONS))
def test_the_epic_names_each_site_in_the_runners_definition(site):
    assert f"`{site}`" in sf20_section()


def test_the_epic_states_the_narrowed_sentence_and_its_exceptions():
    section = sf20_section()
    assert "runs a corpus's commands" in section
    assert "save two named sites" in section


# --- plants, in a temp copy ------------------------------------------------

PLANTS = [
    "render/planted.py",
    "serve/routes/planted.py",
    "cli/planted.py",
    "planted.py",
    "validate/source/planted.py",
    "skills/onboarding/planted.py",
]


@pytest.mark.parametrize("where", PLANTS)
@pytest.mark.parametrize(
    "spelling", ["import subprocess\n", "from os import system\n", "import webbrowser\n"]
)
def test_a_start_planted_outside_the_list_is_refused_by_name(tmp_path, where, spelling):
    root = a_copy(tmp_path)
    (root / where).write_text(spelling, encoding="utf-8")
    assert list(unexcused(root)) == [where]


def test_a_start_planted_inside_the_runner_is_permitted(tmp_path):
    root = a_copy(tmp_path)
    (root / RUNNER / "planted.py").write_text("import subprocess\n", encoding="utf-8")
    assert f"{RUNNER}/planted.py" in starters(root)
    assert unexcused(root) == {}


@pytest.mark.parametrize(
    "planted",
    [
        "subprocess.run(['sh', '-c', 'x'])",
        "subprocess.Popen(command)",
        "subprocess.check_output([python, '-c', 'x'])",
        "subprocess.run([])",
    ],
)
def test_a_named_site_that_starts_another_program_is_refused(planted):
    assert not_git(f"import subprocess\n{planted}\n") == [planted]


def test_a_git_question_passes_the_git_check():
    assert not_git("import subprocess\nsubprocess.run([git, '-C', where, 'status'])\n") == []


# --- the detector itself: each way to start a process, both ways (`W375`) --


def module_spellings(module: str) -> list[str]:
    """Every spelling of reaching `module` that the detector reads."""
    return [
        f"import {module}",
        f"import {module} as renamed",
        f"from {module} import anything",
        f"__import__({module!r})",
        f"import importlib\nimportlib.import_module({module!r})",
    ]


MODULE_PLANTS = [(m, s) for m in SPAWNING_MODULES for s in module_spellings(m)]
OS_NAMES = sorted(SPAWNING_OS | {"execv", "execvpe", "spawnl", "spawnvp"})
OS_PLANTS = [s for n in OS_NAMES for s in (f"from os import {n}", f"import os\nos.{n}('x')")]
FROM_PLANTS = [
    f"from {pkg} import {name}" for pkg, names in SPAWNING_FROM.items() for name in sorted(names)
]


@pytest.mark.parametrize(("module", "planted"), MODULE_PLANTS)
def test_the_detector_fires_on_each_spawning_module_under_each_spelling(module, planted):
    assert module in spawns(planted), planted


@pytest.mark.parametrize("planted", OS_PLANTS + FROM_PLANTS)
def test_the_detector_fires_on_each_spawning_name(planted):
    assert spawns(planted), planted


@pytest.mark.parametrize("module", SPAWNING_MODULES)
def test_the_detector_passes_a_lookalike_of_each_spawning_module(module):
    # ⭐ The other way: a longer name, the name only as a string, and its parent package.
    lookalikes = [f"import {module}ish", f"NAME = {module!r}", f"from {module}ish import x"]
    if "." in module:
        lookalikes.append(f"import {module.rsplit('.', 1)[0]}")
    assert [s for s in lookalikes if spawns(s)] == []


@pytest.mark.parametrize(
    "legitimate",
    [
        "import os.path",
        "from os import stat_result",
        "from os import environ, stat",
        "import os\nos.stat('x')",
        "import http.server",
        "from asyncio import sleep",
        "from concurrent.futures import ThreadPoolExecutor",
        "execv = 1",
    ],
)
def test_the_detector_passes_what_does_not_start_a_process(legitimate):
    assert spawns(legitimate) == []


@pytest.mark.parametrize(
    "planted",
    ["import multiprocessing.pool", "from multiprocessing import Process", "import webbrowser"],
)
def test_the_detector_fires_on_a_submodule_or_member_of_a_spawner(planted):
    assert spawns(planted), planted


def test_every_spawning_module_is_a_standard_library_module():
    # ⭐ A typo in the table would plant and pass on a module nothing can import.
    assert [m for m in SPAWNING_MODULES if m.split(".")[0] not in sys.stdlib_module_names] == []


WEBBROWSER = """
import json, sys
before = "subprocess" in sys.modules
import webbrowser
print(json.dumps({"before": before, "after": "subprocess" in sys.modules}))
"""


def test_webbrowser_is_listed_because_importing_it_loads_subprocess():
    # ⭐ `W361/3`, measured rather than asserted: a fresh interpreter has no
    # `subprocess` until `webbrowser` is imported, and has it after.
    result = run([sys.executable, "-I", "-c", WEBBROWSER], repository_root())
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout.strip().splitlines()[-1]) == {"before": False, "after": True}
    assert "webbrowser" in SPAWNING_MODULES
    assert spawns("import webbrowser\nwebbrowser.open('x')") == ["webbrowser"]
