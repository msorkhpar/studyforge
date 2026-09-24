"""The decisions file's own acceptance: its id command, and its entry shape.

Mirrors no source module. It holds `docs/decisions.md` to the things that
make the file useful to a reader of the product as it is:

- the header carries ONE command that prints every process id cited in the
  product's prose, and that command sees an id planted in a docstring (the
  plant, below, run in a throwaway repository);
- no message a user reads, and neither the decisions file nor the
  integration catalogue, cites a process id at all: each says the thing
  itself or cites a spec rule;
- each entry states a decision, names where it lives, gives a reason and the
  spec rule it serves, or says why it serves none;
- every code span a Decision part or the catalogue's prose carries resolves
  against the source, by the rules stated above `NOT_CODE` below;
- the file cites nothing that leaves the main line with the process records.

Standard library only, plus `git`, `bash`, `awk` and `sort`, which the command
itself names.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from tests.support import git, init_repository, repository_root, run

#: The document under test, relative to the repository root.
DECISIONS = Path("docs") / "decisions.md"

#: The integration catalogue, which ships beside it and is held to the same no-id rule.
CATALOGUE = Path("docs") / "integration-catalogue.md"

#: The label that opens every entry part, in the order an entry carries them.
PARTS = ("**Decision.**", "**Why.**", "**Serves.**")

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
    assert population(repo) == [], "a message cites a process id; say its reason instead"


def test_a_planted_id_is_printed(tmp_path):
    # The plant: one id added to one docstring. Spelled by concatenation so this
    # file never carries an id-shaped literal of its own.
    planted = "W" + "9876"
    repo = scratch_repository(tmp_path, {"src/pkg/mod.py": f'"""A module; see {planted}."""\n'})
    assert population(repo) == [planted]


def test_an_id_outside_the_four_roots_is_not_read(tmp_path):
    planted = "W" + "9876"
    repo = scratch_repository(tmp_path, {"docs/other/note.md": f"{planted}\n"})
    assert population(repo) == [], "a message cites a process id; say its reason instead"


def test_every_root_is_read(tmp_path):
    files = {f"{root}/probe.txt": f"Ruling {900 + n}\n" for n, root in enumerate(ROOTS)}
    repo = scratch_repository(tmp_path, files)
    assert population(repo) == sorted(f"Ruling {900 + n}" for n in range(len(ROOTS)))


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
        serves = body[body.find(PARTS[2]) :]
        assert re.search(r"\bR([1-9]|1[0-9]|2[01])\b", serves) or NO_RULE in serves, (
            f"{heading!r} names no spec rule and does not say why"
        )


def test_every_entry_names_where_it_lives():
    # A module, a file or a test: a code span holding a dot or a slash.
    for heading, body in entries():
        decision = body[body.find(PARTS[0]) : body.find(PARTS[1])]
        spans = re.findall(r"`([^`]+)`", decision)
        assert any("." in span or "/" in span for span in spans), (
            f"{heading!r} names no module, file or test that carries it"
        )


def test_headings_are_unique():
    headings = [heading for heading, _ in entries()]
    assert len(headings) == len(set(headings))


def test_nothing_is_cited_that_leaves_the_main_line():
    assert re.findall(r"handoffs/|rows/|BOARD", document()) == []


@pytest.mark.parametrize("name", [DECISIONS, CATALOGUE], ids=str)
def test_neither_document_cites_a_process_id(tmp_path, name):
    # The command's own pattern is in the file and prints nothing: a spelling
    # such as `W<n>` is a shape, not an id.
    text = (repository_root() / name).read_text("utf-8")
    assert population(scratch_repository(tmp_path, {"src/document.md": text})) == []


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


def test_no_message_a_user_reads_cites_a_process_id(tmp_path):
    """A refusal, finding or CLI message carries its reason or a spec rule, never a process id.

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
    assert population(repo) == [], "a message cites a process id; say its reason instead"


# --- every code span resolves against the source ---------------------------------
#
# ⭐ A decision names where it lives, and the name has to be TRUE today: a span
# that no longer resolves is a decision that drifted from the source. Each span
# in an entry's Decision part, and each span in the catalogue's prose (its
# fenced examples are not read), is classified by its shape and resolved by the
# first rule that fits:
#
# 1. `python3 -m <module> …`: the module imports.
# 2. `studyforge <verb> …`: the verb is in `studyforge.cli.dispatch.VERBS`, and
#    each `--flag` it carries is spelled somewhere in the searched tree.
# 3. A path (it holds a `/` or ends in a file suffix), read before anything is
#    imported: it exists under the repository root or `src/studyforge/`, or it
#    is the tail of a tracked path (`templates/page.html`, `chrome.css`).
#    Otherwise it is a path the framework writes into a corpus, and the searched
#    tree must spell it verbatim, a `<placeholder>` read as any text.
# 4. A dotted name opening with `studyforge` or `tests`: it must import, with a
#    trailing argument list dropped: the longest importable prefix is imported
#    and every remaining segment is an attribute of it. Nothing else resolves it.
#    A standard-library name (`os.path.lexists`) resolves the same way, and no
#    other module is ever imported.
# 5. Any other dotted name: it resolves under a `studyforge` module whose dotted
#    name ends with its leading segments (`serve.discovery`); or it is a class
#    defined in the searched tree followed by a member defined there
#    (`Offer.installed()`); or every segment is a definition or string constant
#    there (a key path such as `runner.prime.seeds`); or it is spelled verbatim.
# 6. An identifier: a builtin, a module or package name, a definition or a
#    parameter in the searched tree, or a string constant there (a key, a value,
#    a variable).
# 7. Anything else (a rule id, a CSS or HTML token): spelled verbatim in the
#    searched tree.
#
# The searched tree is every tracked file under `src/`, `tests/` and `docker/`,
# plus `setup.py` and `pyproject.toml`, but never this module, which spells the
# misspellings its own tests plant. A span that no rule resolves fails the
# test by name. A span that names no code by design is listed in `NOT_CODE` with
# its reason, and a listing whose span has left its document fails too.

#: Spans that name no code in this repository, by document, each with its reason.
NOT_CODE = {
    (
        DECISIONS,
        "docker/editor/Dockerfile",
    ): "the code-server-toolchain repository's file, so named",
    (DECISIONS, "tests/test_editor_agent_host.py"): "the code-server-toolchain repository's test",
    (CATALOGUE, "$$…$$"): "material syntax an integrator meets, not code",
    (CATALOGUE, "[CLR]*"): "an example of a glob the manifest refuses",
    (CATALOGUE, "CONTRIBUTING.md"): "a file of an example corpus",
    (CATALOGUE, "LICENSE"): "a file of an example corpus",
    (CATALOGUE, "print(n)"): "an illustration of a reconnaissance script",
    (CATALOGUE, "assert n == expected"): "an illustration of a reconnaissance script",
}

#: Where the resolver looks: directories, then single files.
SEARCHED = ("src/", "tests/", "docker/")
SEARCHED_FILES = ("setup.py", "pyproject.toml")

#: This module, which spells its own misspellings and is never searched.
THIS = "tests/test_decisions.py"

#: What makes a span a path.
FILE_SUFFIX = re.compile(r"\.(py|html|md|json|css|js|svg|env|yaml|toml|txt)$")

#: A `<placeholder>` or `{placeholder}` inside a written path or literal.
PLACEHOLDER = re.compile(r"<[^>]+>|\{[^}]+\}")

#: A dotted name, and an identifier.
DOTTED = re.compile(r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+$")
IDENTIFIER = re.compile(r"^[A-Za-z_]\w*$")


class Tree:
    """What the searched tree defines and spells, read once."""

    def __init__(self) -> None:
        import builtins

        root = repository_root()
        listed = run([git(), "ls-files"], cwd=root)
        assert listed.returncode == 0, listed.stderr
        self.tracked = listed.stdout.split()
        names = [
            p for p in self.tracked if (p.startswith(SEARCHED) or p in SEARCHED_FILES) and p != THIS
        ]
        texts = {p: (root / p).read_text("utf-8", errors="replace") for p in names}
        self.text = "\n".join(texts.values())
        self.defined: set[str] = set(dir(builtins))
        self.strings: set[str] = set()
        self.modules: list[str] = []
        for name, text in texts.items():
            if not name.endswith(".py"):
                continue
            dotted = name.removeprefix("src/").removesuffix(".py").replace("/", ".")
            self.modules.append(dotted.removesuffix(".__init__"))
            self.defined.update(dotted.split("."))
            for node in ast.walk(ast.parse(text)):
                self._read(node)

    def _read(self, node: ast.AST) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            self.defined.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                for part in ast.walk(target):
                    if isinstance(part, ast.Name):
                        self.defined.add(part.id)
                    elif isinstance(part, ast.Attribute):
                        self.defined.add(part.attr)
        elif isinstance(node, ast.arg):
            self.defined.add(node.arg)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            self.strings.add(node.value)

    def spells(self, literal: str) -> bool:
        """True when the searched tree carries `literal`, a placeholder read as any text."""
        pieces = [re.escape(piece) for piece in PLACEHOLDER.split(literal)]
        return re.search(".+?".join(pieces), self.text) is not None


def importable(name: str) -> bool:
    """True when `name`'s longest importable prefix imports and the rest are its attributes."""
    import importlib
    import sys

    parts = name.split(".")
    if parts[0] not in ("studyforge", "tests") and parts[0] not in sys.stdlib_module_names:
        return False
    for cut in range(len(parts), 0, -1):
        try:
            found = importlib.import_module(".".join(parts[:cut]))
        except ImportError:
            continue
        for attribute in parts[cut:]:
            if not hasattr(found, attribute):
                return False
            found = getattr(found, attribute)
        return True
    return False


def resolves(span: str, tree: Tree) -> bool:
    """True when `span` names something the source has, by the first rule that fits."""
    from studyforge.cli.dispatch import VERBS

    words = span.split()
    if span.startswith("python3 -m ") and len(words) > 2:
        return importable(words[2])
    if words[0] == "studyforge" and len(words) > 1:
        flags = [word.split("=")[0] for word in words[2:] if word.startswith("--")]
        return words[1] in VERBS and all(tree.spells(flag) for flag in flags)
    bare = re.sub(r"\([^()]*\)$", "", span).replace("[]", "")
    if "/" in bare or FILE_SUFFIX.search(bare):
        return path_resolves(bare, tree)
    if DOTTED.match(bare) and bare.split(".")[0] in ("studyforge", "tests"):
        return importable(bare)
    if DOTTED.match(bare) and importable(bare):
        return True
    if DOTTED.match(bare):
        return dotted_resolves(bare, tree)
    if IDENTIFIER.match(bare):
        return bare in tree.defined or bare in tree.strings
    return tree.spells(span)


def path_resolves(path: str, tree: Tree) -> bool:
    """Rule 4: a tracked path, the tail of one, or a path the framework spells."""
    root = repository_root()
    trimmed = path.lstrip("./") if not path.startswith(".studyforge") else path
    if (root / path).exists() or (root / "src" / "studyforge" / path).exists():
        return True
    if any(name.endswith("/" + trimmed.rstrip("/")) for name in tree.tracked):
        return True
    return tree.spells(path.rstrip("/"))


def dotted_resolves(name: str, tree: Tree) -> bool:
    """Rule 5: relative to a module, a class and its member, a key path, or verbatim."""
    parts = name.split(".")
    for cut in range(len(parts), 0, -1):
        tail = "." + ".".join(parts[:cut])
        for module in tree.modules:
            if ("." + module).endswith(tail) and importable(".".join([module, *parts[cut:]])):
                return True
    if parts[0] in tree.defined and parts[0][0].isupper() and parts[-1] in tree.defined:
        return True
    if all(part in tree.defined or part in tree.strings for part in parts):
        return True
    return tree.spells(name)


def spans(name: Path) -> list[str]:
    """The code spans a document names code with: Decision parts, or the catalogue's prose."""
    text = (repository_root() / name).read_text("utf-8")
    if name == DECISIONS:
        text = "".join(body[body.find(PARTS[0]) : body.find(PARTS[1])] for _, body in entries())
    else:
        text = re.sub(r"^```.*?^```", "", text, flags=re.MULTILINE | re.DOTALL)
    return re.findall(r"`([^`\n]+)`", text)


@pytest.fixture(scope="module")
def tree() -> Tree:
    return Tree()


@pytest.mark.parametrize("name", [DECISIONS, CATALOGUE], ids=str)
def test_every_code_span_resolves_against_the_source(tree, name):
    unresolved = sorted(
        {span for span in spans(name) if (name, span) not in NOT_CODE and not resolves(span, tree)}
    )
    assert unresolved == [], f"{name} names what the source does not have: {unresolved}"


def test_every_listed_exemption_is_still_in_its_document():
    stale = [span for (name, span) in NOT_CODE if span not in spans(name)]
    assert stale == [], f"NOT_CODE lists spans no document names: {stale}"


@pytest.mark.parametrize(
    "span",
    [
        "studyforge.validate.derivedd",
        "Offer.installd()",
        "derivation-recrd",
        "templates/nopage.html",
    ],
)
def test_a_misspelled_name_does_not_resolve(tree, span):
    assert not resolves(span, tree)


@pytest.mark.parametrize(
    "span",
    [
        "studyforge.validate.derived",
        "Offer.installed()",
        "derivation-record",
        "templates/page.html",
    ],
)
def test_the_same_names_spelled_right_resolve(tree, span):
    assert resolves(span, tree)
