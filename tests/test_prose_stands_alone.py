"""The framework's code and tests cite no process id and send a reader to no process record.

Mirrors no source module. The records of how the framework was built (its work
items, findings, rounds, rulings, handoffs, conventions and tooling) are not on
the main line, so prose that cites them explains nothing. This module holds two
things:

- **No process id.** The population command of `docs/decisions.md`, run with NO
  alias exemption, prints nothing over `src/` (every file, comments included) or
  over the docstrings and comments of every module under `tests/` and the root
  `conftest.py`.
- **No rule id in what the product prints.** A message, a refusal or a line a
  generated file carries says its reason; a reader of the output cannot resolve
  a spec rule id such as `R7`. Docstrings and comments may still cite one.
- **No pointer to a process record.** No file under `src/`, `tests/` or
  `docker/`, nor `.gitignore`, `pyproject.toml` or `conftest.py`, names the
  tooling (`tools/`, a `tools.` module), a handoff, a row file, a convention
  file, the review rubric or `docs/capability-index.md` as something to read,
  unless the same paragraph says the record lives on the `archive/process` branch.

What is not read, and why:

- `src/studyforge/skills/delivery/capability-index.md`: the packaged index is
  DATA whose rows are the framework's own task ids, frozen by a digest.
- The string literals of a test: they are its data, and a test that plants an id
  or a path has to spell one.
- The documents under `docs/`, the README and `CLAUDE.md`: other checks own them.

Standard library only, plus `git`, `bash`, `awk` and `sort`, which the command
itself names.
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
from pathlib import Path

from tests.support import git, repository_root, run
from tests.test_decisions import population, scratch_repository

#: The packaged capability index: data whose rows are task ids, frozen by a digest.
PACKAGED_INDEX = "src/studyforge/skills/delivery/capability-index.md"

#: The root files the pointer sweep reads besides `src/`, `tests/` and `docker/`.
ROOT_FILES = (".gitignore", "pyproject.toml", "conftest.py")

#: The directories the pointer sweep reads.
SWEPT = ("src/", "tests/", "docker/")

#: This module spells every pattern it looks for, so the pointer sweep skips it.
THIS = "tests/test_prose_stands_alone.py"

#: What sends a reader to a process record, by what the record is.
POINTERS = {
    "the tooling": re.compile(r"(?<![\w./-])tools(?:/|\.[a-z_])"),
    "a handoff": re.compile(r"\bhandoffs?\b", re.IGNORECASE),
    "a row file": re.compile(r"\brows/[A-Z]"),
    "a convention": re.compile(
        r"\bconventions/|agent-protocol|review[- ]rubric|module-structure\.md|shapes\.md\b",
        re.IGNORECASE,
    ),
    "the removed capability index": re.compile(r"docs/capability-index\.md"),
}

#: The one way a paragraph may name a process record: by saying where it lives.
ARCHIVE = "archive/process"

#: Files whose match is not a pointer, by the kind matched, each with its reason.
NOT_A_POINTER = {
    ("tests/visual/__init__.py", "a handoff"): "keyboard focus passing, a page behaviour",
    ("tests/visual/served.py", "a handoff"): "keyboard focus passing, a page behaviour",
    ("tests/visual/test_practice_panel.py", "a handoff"): "keyboard focus passing",
    ("tests/test_authoring_reference.py", "the tooling"): "a typo the check must refuse",
    ("tests/test_readme.py", "the tooling"): "names what the README must not link",
    ("tests/test_readme.py", "a convention"): "names what the README must not link",
}


def tracked(root: Path) -> list[str]:
    """Every tracked path under `root`."""
    listed = run([git(), "ls-files"], cwd=root)
    assert listed.returncode == 0, listed.stderr
    return listed.stdout.split()


def _text(path: Path) -> str | None:
    """A file's text, or `None` for a file that is not UTF-8 text (a font, an image)."""
    try:
        return path.read_text("utf-8")
    except UnicodeDecodeError:
        return None


def docstrings(source: str) -> list[str]:
    """The module, class and function docstrings of a module."""
    documented = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    return [
        doc
        for node in ast.walk(ast.parse(source))
        if isinstance(node, documented) and (doc := ast.get_docstring(node, clean=False))
    ]


def comments(source: str) -> list[str]:
    """Every `#` comment of a module."""
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    return [token.string for token in tokens if token.type == tokenize.COMMENT]


def _is_test_code(name: str) -> bool:
    return name.endswith(".py") and (name.startswith("tests/") or name == "conftest.py")


def prose(root: Path) -> dict[str, str]:
    """What the id sweep reads, by file: all of `src/`, and the prose of the test code."""
    read: dict[str, str] = {}
    for name in tracked(root):
        if name == PACKAGED_INDEX:
            continue
        if name.startswith("src/"):
            text = _text(root / name)
        elif _is_test_code(name):
            source = _text(root / name)
            text = None if source is None else "\n".join(docstrings(source) + comments(source))
        else:
            continue
        if text is not None:
            read[name] = text
    return read


# --- no process id ------------------------------------------------------------------


def cited(root: Path, tmp_path: Path) -> list[str]:
    """What the decisions file's own command prints over `root`'s code and test prose."""
    read = prose(root)
    assert read, f"nothing was read under {root}: a blind read, not a pass"
    # Every file goes under `src/`, which the command reads, keeping its own name.
    files = {f"src/{name}.txt": text for name, text in read.items()}
    return population(scratch_repository(tmp_path, files))


def test_the_code_and_the_tests_cite_no_process_id(tmp_path):
    root = repository_root()
    assert len(prose(root)) > 500, "the read reached too few files to mean anything"
    assert cited(root, tmp_path / "live") == [], (
        "the code or a test's prose cites a process id; say the thing itself or cite a spec rule"
    )


# The plants, each an id spelled by concatenation so this file carries none of its own.
PLANTED = "W" + "9876"
LETTERED = "Ruling " + "986a"


def _planted_tree(tmp_path: Path, files: dict[str, str]) -> Path:
    base = {"src/pkg/mod.py": '"""A module."""\n'}
    return scratch_repository(tmp_path / "tree", {**base, **files})


def test_a_planted_id_is_read_wherever_the_sweep_reads(tmp_path):
    places = {
        "src/pkg/skill/SKILL.md": f"See {PLANTED}.\n",
        "src/pkg/assets/page.js": f"// see {PLANTED}\n",
        "src/pkg/doc.py": f'"""A module; see {PLANTED}."""\n',
        "src/pkg/says.py": f'raise ValueError(f"{{x}} is refused ({PLANTED})")\n',
        "src/pkg/commented.py": f"# see {PLANTED}\nX = 1\n",
        "tests/test_doc.py": f'"""See {PLANTED}."""\n',
        "tests/test_commented.py": f"# see {PLANTED}\nX = 1\n",
        "conftest.py": f"# see {PLANTED}\n",
    }
    for n, (name, text) in enumerate(places.items()):
        root = _planted_tree(tmp_path / str(n), {name: text})
        assert cited(root, tmp_path / str(n)) == [PLANTED], f"an id in {name} was not read"


def test_a_lettered_ruling_is_read(tmp_path):
    root = _planted_tree(tmp_path, {"src/pkg/note.md": f"As {LETTERED} says.\n"})
    assert cited(root, tmp_path) == [LETTERED]


def test_what_the_sweep_does_not_read_is_not_read(tmp_path):
    root = _planted_tree(
        tmp_path,
        {
            "docs/guide.md": f"{PLANTED}\n",
            "README.md": f"{PLANTED}\n",
            PACKAGED_INDEX: f"| `{PLANTED}` |\n",
            "tests/test_data.py": f'"""A test."""\nPLANT = "{PLANTED}"\n',
            "tests/fixtures/note.md": f"{PLANTED}\n",
        },
    )
    assert cited(root, tmp_path) == []


# --- no pointer to a process record -----------------------------------------------------


def _paragraphs(text: str) -> list[str]:
    return re.split(r"\n\s*\n", text)


def reading(name: str, text: str) -> list[str]:
    """The prose of one file the pointer sweep reads, as paragraphs."""
    if _is_test_code(name):
        return [p for part in docstrings(text) + comments(text) for p in _paragraphs(part)]
    return _paragraphs(text)


def pointers(root: Path) -> dict[str, list[str]]:
    """Each file's paragraphs that send a reader to a process record, by what they point at."""
    found: dict[str, list[str]] = {}
    for name in tracked(root):
        swept = name.startswith(SWEPT) or name in ROOT_FILES
        text = _text(root / name) if swept and name != THIS else None
        if text is None:
            continue
        hits = [
            f"{what}: {para.strip()[:160]!r}"
            for para in reading(name, text)
            if ARCHIVE not in para
            for what, pattern in POINTERS.items()
            if pattern.search(para) and (name, what) not in NOT_A_POINTER
        ]
        if hits:
            found[name] = hits
    return found


def test_no_file_sends_a_reader_to_a_process_record():
    root = repository_root()
    assert len(tracked(root)) > 500, "the sweep read too few files to mean anything"
    assert pointers(root) == {}, (
        "a file names a process record as something to read; say the thing itself, "
        f"or say that it lives on {ARCHIVE}"
    )


def test_every_kind_of_pointer_is_caught_and_the_archive_excuses_it(tmp_path):
    planted = {
        "src/a.md": "Run `python3 -m tools.quality` first.\n",
        "src/b.md": "The readings are in the task's handoff.\n",
        "src/c.md": "Its argument is `docs/tasks/rows/W1.md`.\n",
        "src/d.md": "The shape is in `docs/conventions/module-structure.md`.\n",
        "src/e.md": "Counts come from `docs/capability-index.md`.\n",
        "src/pkg/mod.py": '"""A module."""\n# measured by tools/quality\n',
        "tests/test_x.py": '"""Mirror of `tools/quality/size.py`."""\n',
        "docker/dev/check": "#   docker/dev/check python3 -m tools.quality\n",
        "src/f.md": "Handoffs live on `archive/process`, in `docs/tasks/handoffs/`.\n",
    }
    found = pointers(scratch_repository(tmp_path, planted))
    kinds = {hit.split(":")[0] for hits in found.values() for hit in hits}
    assert kinds == set(POINTERS), f"a kind of pointer went unseen: {sorted(kinds)}"
    assert sorted(found) == sorted(set(planted) - {"src/f.md"})


def test_what_merely_looks_like_a_pointer_is_not(tmp_path):
    harmless = {
        "src/a.md": "The editor comes from `code-server-toolchain/`, a toolchain image.\n",
        "src/b.md": "A table has a row per unit, and rows/columns are counted.\n",
        "tests/test_x.py": '"""A module."""\nPLANT = "import tools.quality"\n',
        "src/c.md": "The packaged `src/studyforge/skills/delivery/capability-index.md`.\n",
        "docs/d.md": "The readings are in the task's handoff.\n",
    }
    assert pointers(scratch_repository(tmp_path, harmless)) == {}


# --- no rule id in output -----------------------------------------------------------------

#: A spec rule id as the spec numbers them, `R1` to `R21`.
RULE_ID = re.compile(r"\bR(?:[1-9]|1[0-9]|2[01])\b")


def output_literals(source: str) -> list[str]:
    """Every string constant of a module that is not a docstring: what the product prints."""
    tree = ast.parse(source)
    documented = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    skipped = {
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
        and id(node) not in skipped
    ]


def rule_ids(root: Path) -> dict[str, list[str]]:
    """Each module under `src/` whose output literals cite a spec rule id, with the literals."""
    found: dict[str, list[str]] = {}
    for name in tracked(root):
        if name.startswith("src/") and name.endswith(".py"):
            source = _text(root / name) or ""
            hits = [text[:120] for text in output_literals(source) if RULE_ID.search(text)]
            if hits:
                found[name] = hits
    return found


def test_nothing_the_product_prints_cites_a_rule_id():
    assert rule_ids(repository_root()) == {}, "say the reason; a reader cannot resolve a rule id"


def test_a_rule_id_in_a_message_is_caught_and_one_in_a_docstring_is_not(tmp_path):
    rule = "R" + "19"
    planted = {
        "src/pkg/says.py": f'"""A module ({rule})."""\nraise ValueError("hand-edited ({rule})")\n',
        "src/pkg/quiet.py": f'"""A module ({rule})."""\n# a comment ({rule})\n',
    }
    found = rule_ids(scratch_repository(tmp_path, planted))
    assert found == {"src/pkg/says.py": [f"hand-edited ({rule})"]}
