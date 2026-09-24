"""The decisions file's own acceptance: its population command, and its entry shape.

Mirrors no source module. It holds `docs/decisions.md` to the four things that
make the file useful to a reader who has no process archive to consult:

- the header carries ONE command that derives the population of process ids
  cited in the product's prose, and that command sees an id planted in a
  docstring (the plant, below, run in a throwaway repository);
- every alias the file lists is a spelling that command reads and prints back
  unchanged, so a reader grepping the file for an id they met in a docstring
  finds the same string;
- each entry states a decision, a reason and the spec rule it serves, or says
  why it serves none;
- the file cites nothing that leaves the main line with the process records.

What it does not assert is COVERAGE of the live tree. Which ids explain nothing
without the archive is a list another task consumes and rewrites away, and a
test pinned to it would turn red on every branch that adds a citation.

Standard library only, plus `git`, `bash`, `awk` and `sort`, which the command
itself names.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from tests.support import git, init_repository, repository_root, run

#: The document under test, relative to the repository root.
DECISIONS = Path("docs") / "decisions.md"

#: The label that opens every entry part, in the order an entry carries them.
PARTS = ("**Decision.**", "**Why.**", "**Serves.**", "**Aliases.**")

#: How an entry says it serves no spec rule.
NO_RULE = "No spec rule:"

#: The four roots the command reads, as the header states them.
ROOTS = ("src", "tests", "docs/specs", "docs/authoring")


def document() -> str:
    """The decisions file's text."""
    return (repository_root() / DECISIONS).read_text("utf-8")


def command() -> str:
    """The first `sh` fence in the file: the population command."""
    match = re.search(r"```sh\n(.*?)```", document(), re.DOTALL)
    assert match, f"{DECISIONS} carries no ```sh fence with its population command"
    return match.group(1)


def population(repo: Path) -> list[str]:
    """What the header's command prints, run at the root of `repo`."""
    result = run(["bash", "-c", command()], cwd=repo)
    assert result.returncode == 0, result.stderr
    return result.stdout.splitlines()


def entries() -> list[tuple[str, str]]:
    """Every `### ` entry as (heading, body), in document order."""
    chunks = re.split(r"^### (.+)$", document(), flags=re.MULTILINE)
    return [(chunks[i], chunks[i + 1]) for i in range(1, len(chunks), 2)]


def aliases(body: str) -> list[str]:
    """The backticked ids on an entry's Aliases line."""
    line = next(ln for ln in body.splitlines() if ln.startswith(PARTS[3]))
    return re.findall(r"`([^`]+)`", line)


def scratch_repository(tmp_path: Path, files: dict[str, str]) -> Path:
    """A throwaway repository with `files` written and staged, so `git grep` reads them."""
    repo = init_repository(tmp_path / "repo")
    for name, text in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, "utf-8")
    staged = run([git(), "add", "-A"], cwd=repo)
    assert staged.returncode == 0, staged.stderr
    return repo


# --- the command ---------------------------------------------------------------


def test_the_command_names_the_four_roots():
    for root in ROOTS:
        assert f" {root}" in command(), f"the command does not read {root}"


def test_a_clean_tree_prints_nothing(tmp_path):
    repo = scratch_repository(tmp_path, {"src/pkg/mod.py": '"""A module."""\n'})
    assert population(repo) == []


def test_a_planted_id_is_printed(tmp_path):
    # The plant: one id added to one docstring. Spelled by concatenation so this
    # file never carries an id-shaped literal of its own.
    planted = "W" + "9876"
    repo = scratch_repository(tmp_path, {"src/pkg/mod.py": f'"""A module; see {planted}."""\n'})
    assert population(repo) == [planted]


def test_an_id_outside_the_four_roots_is_not_read(tmp_path):
    planted = "W" + "9876"
    repo = scratch_repository(tmp_path, {"docs/other/note.md": f"{planted}\n"})
    assert population(repo) == []


def test_every_root_is_read(tmp_path):
    files = {f"{root}/probe.txt": f"Ruling {900 + n}\n" for n, root in enumerate(ROOTS)}
    repo = scratch_repository(tmp_path, files)
    assert population(repo) == sorted(f"Ruling {900 + n}" for n in range(len(ROOTS)))


def test_every_alias_is_a_spelling_the_command_prints_unchanged(tmp_path):
    listed = sorted({a for _, body in entries() for a in aliases(body)})
    repo = scratch_repository(tmp_path, {"src/aliases.txt": "".join(f"{a}\n" for a in listed)})
    printed = population(repo)
    assert sorted(set(printed) ^ set(listed)) == []


# --- the entries ---------------------------------------------------------------


def test_the_file_has_entries():
    assert entries(), f"{DECISIONS} carries no entry"


def test_every_entry_carries_its_four_parts_in_order():
    for heading, body in entries():
        places = [body.find(part) for part in PARTS]
        assert -1 not in places, f"{heading!r} lacks a part of {PARTS}"
        assert places == sorted(places), f"{heading!r} carries its parts out of order"


def test_every_entry_names_a_spec_rule_or_says_why_none():
    for heading, body in entries():
        serves = body[body.find(PARTS[2]) : body.find(PARTS[3])]
        assert re.search(r"\bR([1-9]|1[0-9]|2[01])\b", serves) or NO_RULE in serves, (
            f"{heading!r} names no spec rule and does not say why"
        )


def test_an_alias_names_one_decision():
    seen: dict[str, str] = {}
    for heading, body in entries():
        for alias in aliases(body):
            assert alias not in seen, f"{alias} aliases {seen[alias]!r} and {heading!r}"
            seen[alias] = heading


def test_headings_are_unique():
    headings = [heading for heading, _ in entries()]
    assert len(headings) == len(set(headings))


def test_nothing_is_cited_that_leaves_the_main_line():
    assert re.findall(r"handoffs/|rows/|BOARD", document()) == []


# --- what a user reads -----------------------------------------------------------


def literals(source: str) -> list[str]:
    """Every string constant in a module that is not a docstring: what a user can be shown."""
    tree = ast.parse(source)
    documented = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    docstrings = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, documented)
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
    }
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    ]


def test_a_planted_id_in_a_message_is_read_and_a_docstring_is_not():
    planted = "W" + "9876"
    source = f'"""A module; see {planted}."""\nraise ValueError(f"{{x}} is refused ({planted})")\n'
    assert [text for text in literals(source) if planted in text] == [f" is refused ({planted})"]


def test_no_message_a_user_reads_cites_an_id_this_file_does_not_alias(tmp_path):
    """A refusal, finding or CLI message carries its reason or a spec rule, never a bare process id.

    Every non-docstring string literal under `src/` is written into a throwaway
    repository and read by the header's own command, so the grammar is the one
    the file states, never a second spelling of it.
    """
    root = repository_root()
    tracked = run([git(), "ls-files", "src/*.py"], cwd=root)
    assert tracked.returncode == 0, tracked.stderr
    text = "".join(
        f"{literal}\n"
        for name in tracked.stdout.split()
        for literal in literals((root / name).read_text("utf-8"))
    )
    repo = scratch_repository(tmp_path, {"src/literals.txt": text})
    listed = {a for _, body in entries() for a in aliases(body)}
    assert sorted(set(population(repo)) - listed) == []
