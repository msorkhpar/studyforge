"""Reading `docs/authoring/` as data, so its claims can be compared to the code.

**What it does.** Turns the authoring reference into structures a test can
assert against: the documents, their sections, their tables, and their fenced
blocks.

**How you use it.** `document(name)` for one document's text, `documents()` for
all of them, `rows_under(text, heading)` for a table's cells, `fences(text)`
for the code blocks, and `vocabulary_under(text, heading)` for the backticked
first column that names a closed set.

⭐ **One population here is not a parser: `commanded_pages()` and everything
derived from it.** It lives here because `W74` widened the runnable-module check
onto the same derivation its sibling already used, and a derivation two modules
can each hold a copy of is how that pair came to disagree at all. ⛔ **The
derivation and both declared exemptions are here; every assertion over them is
in `tests/test_authoring_reference.py`.**

**Depends on.** The standard library and `tests.support`. ⛔ Nothing under
`src/` — this half reads the document; the assertions import the code. ⚠️
**`run_bare()` is the one accessor that does not read a document: Ruling 156
clause 3 requires a REAL interpreter, because `find_spec` measures the runner's
path rather than the reader's. It spawns one; it still imports nothing.**

⚠️ **The parsers here are deliberately small and strict.** A lenient markdown
parser that silently found nothing would turn every check that reads it into a
check that cannot fail, which is the failure mode this whole module exists to
avoid. Each accessor raises when it finds no subject.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tomllib
from collections.abc import Iterable
from pathlib import Path

from tests.support import repository_root

#: Where the reference lives, relative to the repository root.
AUTHORING = "docs/authoring"

#: Where the shipped skill documents live, relative to the repository root.
#: ⛔ A glob, never a list. `W61`: `SK-05` shipped its console-script check with
#: a population one directory wide, and two shipped `SKILL.md` files carried the
#: exact defect it refuses for as long as it did.
SKILLS = "src"

#: The document every other one is reached from. ⛔ Named here rather than in
#: each test, because "is this document reachable" needs one definition of
#: where reachability starts.
INDEX = "README.md"

#: A markdown heading: the hashes, then the text.
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")

#: A fenced block's opening line, with whatever info string it carries.
_FENCE = re.compile(r"^```(\S*)\s*$")

#: An inline code span. ⚠️ Single backticks only: a vocabulary is written
#: `like-this`, and a doubled span in the reference would be quoting markdown
#: rather than naming a value.
_CODE_SPAN = re.compile(r"`([^`]+)`")

#: An escaped pipe inside a table cell, which must survive the split that
#: separates cells. ⚠️ `<lesson\|practice>` is a real cell in `validate.md`.
_ESCAPED_PIPE = "\x00"


def authoring_root() -> Path:
    """Return the directory holding the reference."""
    return repository_root() / AUTHORING


def document_paths() -> list[Path]:
    """Every markdown document in the reference, sorted."""
    paths = sorted(authoring_root().glob("*.md"))
    if not paths:
        raise AssertionError(f"{AUTHORING}/ holds no markdown documents at all")
    return paths


def documents() -> dict[str, str]:
    """Map every document's filename to its text."""
    return {path.name: path.read_text(encoding="utf-8") for path in document_paths()}


def skill_documents() -> dict[str, str]:
    """Every shipped `SKILL.md` under `src/`, keyed by its repository-relative path.

    ⛔ **Walked, not listed.** The population is whatever `src/**/SKILL.md`
    finds, so a fifth skill package joins it by existing rather than by
    somebody remembering to add it here — which is the whole of `W61`: the
    check that refuses a fenced console script shipped watching one directory,
    and the two skills that ship the defect were never in its population.
    """
    root = repository_root()
    paths = sorted((root / SKILLS).glob("**/SKILL.md"))
    if not paths:
        raise AssertionError(f"{SKILLS}/ ships no SKILL.md at all")
    return {str(path.relative_to(root)): path.read_text(encoding="utf-8") for path in paths}


def document(name: str) -> str:
    """Return one document's text, or fail naming what is missing."""
    path = authoring_root() / name
    if not path.is_file():
        raise AssertionError(f"{AUTHORING}/{name} does not exist")
    return path.read_text(encoding="utf-8")


def prose_lines(text: str) -> list[tuple[int, str]]:
    """Return `(line number, line)` for every line outside a fenced block.

    ⛔ Fence-aware, and it is not an optimisation. A fenced block is quoted
    material: its `#` is not a heading and its backticks pair with each other,
    so a walk that read it would mis-pair every code span in the rest of the
    document — which is exactly what this module's first run did.
    """
    kept: list[tuple[int, str]] = []
    inside = False
    for number, line in enumerate(text.splitlines()):
        if _FENCE.match(line):
            inside = not inside
            continue
        if not inside:
            kept.append((number, line))
    return kept


def section(text: str, heading: str) -> str:
    """Return the lines under `heading`, up to the next heading of its level or higher.

    `heading` is matched against the heading's text with its hashes stripped,
    so a caller writes the words rather than the markup.
    """
    lines = text.splitlines()
    start = None
    depth = 0
    for number, line in prose_lines(text):
        match = _HEADING.match(line)
        if match is None:
            continue
        if start is None:
            if match.group(2).strip() == heading:
                start, depth = number + 1, len(match.group(1))
            continue
        if len(match.group(1)) <= depth:
            return "\n".join(lines[start:number])
    if start is None:
        raise AssertionError(f"no section titled {heading!r}; the reference was reorganised")
    return "\n".join(lines[start:])


def rows_under(text: str, heading: str) -> list[list[str]]:
    """Return every table row under `heading` as a list of stripped cells.

    Header rows and the `|---|` separator are dropped: a row is kept only when
    it follows a separator in the same table.
    """
    rows: list[list[str]] = []
    live = False
    for line in section(text, heading).splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            live = False
            continue
        cells = _cells(stripped)
        if all(set(cell) <= {"-", ":"} and cell for cell in cells):
            live = True
            continue
        if live:
            rows.append(cells)
    if not rows:
        raise AssertionError(f"the table under {heading!r} has no body rows")
    return rows


def _cells(line: str) -> list[str]:
    """Split one table line into cells, keeping escaped pipes inside them."""
    guarded = line.replace("\\|", _ESCAPED_PIPE)
    return [cell.strip().replace(_ESCAPED_PIPE, "|") for cell in guarded.strip("|").split("|")]


def vocabulary_under(text: str, heading: str, column: int = 0) -> set[str]:
    """Return the backticked tokens in one column of the table under `heading`.

    ⛔ Backticked, never bare: a cell that names a value writes it in code
    spans, and reading bare prose would let a sentence about a value be
    mistaken for the value.
    """
    found: set[str] = set()
    for row in rows_under(text, heading):
        if column >= len(row):
            continue
        found.update(_CODE_SPAN.findall(row[column]))
    if not found:
        raise AssertionError(f"column {column} under {heading!r} names no backticked value")
    return found


def fences(text: str, info: str | None = None) -> list[str]:
    """Return every fenced block's body, optionally only those with `info`."""
    found: list[str] = []
    body: list[str] | None = None
    opened = ""
    for line in text.splitlines():
        match = _FENCE.match(line)
        if match is None:
            if body is not None:
                body.append(line)
            continue
        if body is None:
            body, opened = [], match.group(1)
            continue
        if info is None or opened == info:
            found.append("\n".join(body))
        body = None
    return found


def json_fences(text: str) -> list[dict]:
    """Every ```json block in `text`, parsed. ⛔ A block that is not JSON fails here."""
    parsed = []
    for number, body in enumerate(fences(text, "json"), start=1):
        try:
            parsed.append(json.loads(body))
        except json.JSONDecodeError as error:  # pragma: no cover - the failure is the point
            raise AssertionError(f"json block {number} does not parse: {error}") from error
    return parsed


def code_spans(text: str) -> set[str]:
    """Every inline code span in `text`, read outside the fenced blocks."""
    found: set[str] = set()
    for _, line in prose_lines(text):
        found.update(_CODE_SPAN.findall(line))
    return found


def commanded_pages() -> dict[str, str]:
    """Every page that hands a reader a fenced command: the reference, and every skill.

    ⛔ **`W61` widened this, and the widening is the fix.** `SK-05` shipped its
    console-script check over `docs/authoring/` alone; `skills/adapter/SKILL.md` and
    `skills/onboarding/SKILL.md` gave `studyforge validate` in a fence the
    whole time and were never looked at. Both halves are walked rather than
    listed, so nothing joins the tree outside the population.
    """
    pages = {f"{AUTHORING}/{name}": text for name, text in documents().items()}
    pages.update(skill_documents())
    return pages


def assert_both_halves_reached(pages: Iterable[str]) -> None:
    """⛔ The population must reach both halves, or it has silently narrowed.

    Without this a check over `commanded_pages()` degrades to the one directory
    it used to watch — the state `W61` exists to leave — and stays green.
    """
    names = sorted(pages)
    assert any(name.startswith(f"{AUTHORING}/") for name in names), "no reference page reached"
    assert any(name.endswith("SKILL.md") for name in names), "no SKILL.md reached"


#: Every `python3 -m <token>` form any page gives. ⛔ `<` and `>` are inside the
#: character class deliberately: a token this pattern cannot SEE is a token the
#: placeholder rule cannot be ASSERTED over, and the narrow `[\w.]+` this widens
#: could not see `python3 -m <package>` at all.
COMMAND = re.compile(r"python3 -m ([\w.<>-]+)")

#: A commanded token that is a substitution for the reader, not a module name.
#: ⛔ Lexical, not a list somebody maintains — no module name may contain either
#: character, so the rule is a property of the token.
PLACEHOLDER = re.compile(r"[<>]")

#: The machine-readable line a page uses to declare a commanded module it does
#: NOT own. ⛔ Ruling 156: the exemption is the DOCUMENT's, never a list in this
#: file — `ingest` earns its exemption from `skills/onboarding/SKILL.md`.
DECLARES_CONSUMER_SIDE = re.compile(r"^\*\*Consumer-side modules:\*\*(.*)$", re.MULTILINE)


def commanded_modules() -> dict[str, set[str]]:
    """Every `python3 -m <token>` any page gives, mapped to the pages giving it.

    ⛔ **Ruling 156 clause 1 — ONE population, both halves.** This read
    `documents()` while its sibling above read `commanded_pages()`, and a pair
    of checks over two different populations is exactly how `W61` happened: a
    typo'd module inside a `SKILL.md` fence was measured by nothing.
    """
    found: dict[str, set[str]] = {}
    for page, text in sorted(commanded_pages().items()):
        for token in COMMAND.findall(text):
            found.setdefault(token, set()).add(page)
    assert found, "no page gives a runnable command at all"
    return found


def consumer_side() -> dict[str, set[str]]:
    """Every module a page DECLARES it does not own, mapped to the pages declaring it.

    ⛔ **The exemption is scoped to the page that makes it.** A module named in
    one page's fence earns nothing from another page's declaration, so moving a
    consumer-side command to a page that does not declare it fails a check.
    """
    declared: dict[str, set[str]] = {}
    for page, text in sorted(commanded_pages().items()):
        for line in DECLARES_CONSUMER_SIDE.findall(text):
            for token in re.findall(r"`([\w.]+)`", line):
                declared.setdefault(token, set()).add(page)
    return declared


def must_run() -> dict[str, set[str]]:
    """The commanded tokens this repository has to be able to run, after both exemptions."""
    declared = consumer_side()
    wanted: dict[str, set[str]] = {}
    for token, pages in sorted(commanded_modules().items()):
        if PLACEHOLDER.search(token):
            continue
        owned = pages - declared.get(token, set())
        if owned:
            wanted[token] = owned
    return wanted


def resolves(name: str) -> bool:
    """Whether `name` is importable here. ⛔ `find_spec` RAISES on a missing parent."""
    try:
        return importlib.util.find_spec(name) is not None
    except ImportError, ValueError:
        return False


def run_bare(name: str, pythonpath: str | None) -> str:
    """Run `python3 -m <name> --help` in a real interpreter; return everything it said.

    ⛔ **Ruling 156 clause 3 — a subprocess, NOT `find_spec`.** `find_spec`
    measures the runner's `sys.path` and the runner's already-imported modules.
    It cannot see a `__main__.py` that raises, and it cannot see a module that
    resolves only because a plugin put it there.
    """
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    if pythonpath is not None:
        env["PYTHONPATH"] = pythonpath
    done = subprocess.run(  # noqa: S603 — fixed argv, interpreter is `sys.executable`
        [sys.executable, "-m", name, "--help"],
        cwd=repository_root(),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    return done.stdout + done.stderr


def installed_for_a_bare_shell() -> bool:
    """Does the interpreter `run_bare` uses carry `studyforge` as an INSTALLED distribution?

    ⭐ Asked of that interpreter in a subprocess, from the same root with the same
    scrubbed `PYTHONPATH` — never of this runner, whose `sys.path` pytest widened.
    ⚠️ True in the pinned image since `W211` (an editable install), False on a host
    that installed nothing.
    """
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    probe = "import importlib.metadata as m; m.distribution('studyforge')"
    done = subprocess.run(  # noqa: S603 — fixed argv, interpreter is `sys.executable`
        [sys.executable, "-c", probe],
        cwd=repository_root(),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    return done.returncode == 0


#: What a real interpreter says when it could not find the module at all.
UNRESOLVED = ("No module named", "Error while finding module specification")


def declared_pythonpath() -> str:
    """The path `pyproject.toml` puts the RUNNER on, derived rather than typed."""
    config = tomllib.loads((repository_root() / "pyproject.toml").read_text("utf-8"))
    entries = config["tool"]["pytest"]["ini_options"]["pythonpath"]
    assert entries, "pyproject.toml declares no pythonpath"
    return os.pathsep.join(entries)


def console_scripts() -> dict[str, str]:
    """`[project.scripts]`, read from `pyproject.toml` — the ground of the derivation.

    ⛔ Asserted non-empty. Ruling 157 converted the check above this one rather
    than deleting it, and a converted check whose population can silently
    become empty is the deletion wearing a different name.
    """
    config = tomllib.loads((repository_root() / "pyproject.toml").read_text("utf-8"))
    scripts = config.get("project", {}).get("scripts", {})
    assert scripts, "pyproject.toml registers no console script; the derivation has no ground"
    return scripts


def registered_verbs() -> dict[str, frozenset[str]]:
    """Each installed command mapped to the verbs it registers.

    ⛔ **Derived, never listed here.** The script name and its target come from
    `[project.scripts]`; the verbs come from the target module's own `VERBS`.
    A verb retired in the dispatcher is retired here in the same commit, which
    is the property a list in this file could not have.
    """
    found: dict[str, frozenset[str]] = {}
    for name, target in sorted(console_scripts().items()):
        module_name = target.partition(":")[0]
        module = importlib.import_module(module_name)
        verbs = getattr(module, "VERBS", None)
        assert verbs, f"{module_name} registers no verbs, so `{name} <verb>` provides nothing"
        found[name] = frozenset(verbs)
    return found


def offered_verbs(pages: dict[str, str]) -> list[tuple[str, str, str]]:
    """Every fenced line giving an installed command, as (page, command, verb).

    ⚠️ The verb is `""` when a fence gives the bare command with no verb after
    it, which is not something the tree provides either.
    """
    commands = sorted(registered_verbs())
    found: list[tuple[str, str, str]] = []
    for page, text in sorted(pages.items()):
        for body in fences(text, ""):
            for raw in body.splitlines():
                line = raw.strip()
                for command in commands:
                    if line != command and not line.startswith(f"{command} "):
                        continue
                    rest = line[len(command) :].split()
                    found.append((page, command, rest[0] if rest else ""))
    return found


def assert_fenced_commands_are_registered(pages: dict[str, str]) -> None:
    """⛔ Every fenced `<command> <verb>` names a verb the tree actually installs."""
    registered = registered_verbs()
    for page, command, verb in offered_verbs(pages):
        assert verb in registered[command], (
            f"{page} offers {command!r} with the verb {verb!r}, and "
            f"[project.scripts] registers no such verb"
        )
