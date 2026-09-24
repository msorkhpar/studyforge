"""The one process-start detector: every standard-library way to start a process.

⛔ **This module DETECTS; it asserts nothing.** ⭐ Its plants — each spelling, both
ways — live in [`test_process_starts.py`](test_process_starts.py), beside the sweep
of `src/` that is the detector's main reader. `serve`'s no-spawn test
([`studyforge/serve/test_init.py`](studyforge/serve/test_init.py)) imports it too.

⚠️ **Why a module of its own:** a detector living in one package's test file makes a
rename in that mirror break a tree-wide sweep at import. ⭐ It knows `webbrowser`, whose
`open` starts a browser process: importing it loads `subprocess`.

⭐ **What counts as a way to start a process** — the tables below, and nothing else:

- a **module whose purpose is starting one**, imported under any spelling (`import`,
  `from … import`, `__import__`, `importlib.import_module`) — `SPAWNING_MODULES`;
- an **`os` function that starts or replaces one** — `os.system`, `os.popen`, the
  `fork`s, the `posix_spawn`s, `os.startfile`, and every `exec*` and `spawn*`;
- a **name imported out of a package that is not itself a spawner** — `asyncio`'s
  subprocess coroutines and `concurrent.futures`' process pool.

⚠️ **What it does NOT count, and says so:** a general-purpose module that starts a
process from inside one routine (`http.server`'s CGI handler, `platform`, `uuid`,
`ctypes.util`, `imaplib`'s stream transport) — the detector reads imports, and
counting those would refuse `http.server`, which `serve` is built on.
"""

from __future__ import annotations

import ast

#: ⛔ Modules whose purpose is starting a process; a submodule of one counts too.
SPAWNING_MODULES = (
    "subprocess",
    "_posixsubprocess",
    "_winapi",
    "multiprocessing",
    "pty",
    "webbrowser",
    "asyncio.subprocess",
    "concurrent.futures.process",
)

#: ⛔ The `os` functions that start or replace a process, besides every `exec*` and `spawn*`.
SPAWNING_OS = frozenset(
    {"system", "popen", "fork", "forkpty", "posix_spawn", "posix_spawnp", "startfile"}
)

#: ⛔ The prefixes of the `os` function families that start or replace a process.
SPAWNING_OS_PREFIXES = ("exec", "spawn")

#: ⛔ Names imported out of a package that is not itself a spawner.
SPAWNING_FROM = {
    "asyncio": frozenset({"create_subprocess_exec", "create_subprocess_shell", "subprocess"}),
    "concurrent.futures": frozenset({"ProcessPoolExecutor", "process"}),
}


def spawning_module(name: str) -> bool:
    """Whether importing `name` reaches a module whose purpose is starting a process."""
    return any(name == module or name.startswith(module + ".") for module in SPAWNING_MODULES)


def spawning_os(name: str) -> bool:
    """Whether `os.<name>` starts or replaces a process."""
    return name in SPAWNING_OS or name.startswith(SPAWNING_OS_PREFIXES)


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
            found += [alias.name for alias in node.names if spawning_module(alias.name)]
        elif isinstance(node, ast.ImportFrom) and node.module:
            if spawning_module(node.module):
                found.append(node.module)
            elif node.module == "os":
                found += [f"os.{a.name}" for a in node.names if spawning_os(a.name)]
            elif node.module in SPAWNING_FROM:
                wanted = SPAWNING_FROM[node.module]
                found += [f"{node.module}.{a.name}" for a in node.names if a.name in wanted]
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id == "os" and spawning_os(node.attr):
                found.append(f"os.{node.attr}")
        elif isinstance(node, ast.Call):
            name = _dynamic_import(node)
            if name is not None and spawning_module(name):
                found.append(name)
    return found
