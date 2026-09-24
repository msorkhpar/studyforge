"""Contract 5 and R1, read from the package's source: thin, one door onto progress, no source.

⛔ Each predicate takes source text and is planted against below. A check that has only
ever run green has not been shown capable of red. ⭐ The runtime half is the digest chain
in `test_record.py`: every change to a corpus's record happens inside `record_run`.
"""

from __future__ import annotations

import ast
from pathlib import Path

from studyforge.skills import personalarchive
from tests.harness.sources import named_sources
from tests.studyforge.skills.personalarchive.archiving import skill_text

PACKAGE = Path(personalarchive.__file__).parent

#: The framework modules the skill may take from. ⛔ A closed, positive set, and each is
#: a package's public surface: never `studyforge.progress.store` or `.document`.
ALLOWED = frozenset(
    {
        "studyforge.progress",
        "studyforge.corpus.manifest",
        "studyforge.archive.scrub",
        "studyforge.version",
    }
)

#: The only modules that may import `studyforge.progress`, and the only one that may
#: name where the store keeps its file.
PROGRESS_DOORS = frozenset({"merge.py", "record.py"})
STORE_DOOR = "record.py"
STORE_NAMES = frozenset({"PROGRESS_FILENAME", "store_dir"})


def modules() -> dict[str, str]:
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(PACKAGE.glob("*.py"))}


def imported(source: str) -> list[str]:
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom) and node.module:
            found.append(node.module)
        elif isinstance(node, ast.Import):
            found += [alias.name for alias in node.names]
    return found


def reaches_past_the_surface(source: str) -> list[str]:
    """Every framework import outside the allowed set, and every private attribute reached."""
    found = [
        f"import {module}"
        for module in imported(source)
        if module.startswith("studyforge.")
        and not module.startswith(personalarchive.__name__)
        and module not in ALLOWED
    ]
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            if not (node.attr.startswith("__") and node.attr.endswith("__")):
                found.append(f"private {node.attr}")
    return found


def names_the_store(source: str) -> list[str]:
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name) and node.id in STORE_NAMES:
            found.append(node.id)
        elif isinstance(node, ast.alias) and node.name in STORE_NAMES:
            found.append(node.name)
        elif isinstance(node, ast.Constant) and node.value == "progress.json":
            found.append("progress.json")
    return found


def test_the_population_is_the_whole_package():
    expected = {
        "__init__.py",
        "__main__.py",
        "cli.py",
        "export.py",
        "layout.py",
        "merge.py",
        "record.py",
        "restore.py",
    }
    assert set(modules()) == expected


def test_no_module_reaches_past_a_public_surface():
    for name, source in modules().items():
        assert reaches_past_the_surface(source) == [], name


def test_only_the_two_doors_import_progress_and_only_record_names_the_store():
    for name, source in modules().items():
        if name not in PROGRESS_DOORS:
            assert "studyforge.progress" not in imported(source), name
        if name != STORE_DOOR:
            assert names_the_store(source) == [], name
    assert names_the_store(modules()[STORE_DOOR]), "the door names nothing; this check is vacuous"


def test_a_planted_reach_into_the_stores_internals_is_caught():
    assert reaches_past_the_surface("store._update(change)\n") == ["private _update"]
    planted = "from studyforge.progress.store import Progress\n"
    assert reaches_past_the_surface(planted) == ["import studyforge.progress.store"]
    assert reaches_past_the_surface("from studyforge.generate import build\n") == [
        "import studyforge.generate"
    ]


def test_a_planted_store_path_outside_the_door_is_caught():
    planted = "from studyforge.progress import store_dir\n(store_dir(root) / 'progress.json')\n"
    assert sorted(names_the_store(planted)) == ["progress.json", "store_dir", "store_dir"]


def test_no_file_the_skill_ships_names_a_source():
    # ⛔ R1, and SKILL.md is in the population: the floor's sweep reads `.py` alone.
    files = sorted(path for path in PACKAGE.iterdir() if path.suffix in (".py", ".md"))
    assert any(path.name == "SKILL.md" for path in files)
    for path in files:
        assert named_sources(path.read_text(encoding="utf-8")) == [], path.name
    assert skill_text()


def test_a_planted_source_name_is_caught():
    planted = "# exports the " + "SPA" + "RQL tutorial\n"
    assert len(named_sources(planted)) == 1
