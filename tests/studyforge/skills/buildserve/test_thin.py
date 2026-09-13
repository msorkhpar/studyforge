"""Contract 4 and R1, read from the package's source: thin, and it names no source.

⛔ Each predicate takes source text, so each is planted against below: a check
that has only ever run green has not been shown capable of red.
⭐ The runtime half of thinness — every file under `--out` is one the build
reported writing — is in `test_run.py`.
"""

from __future__ import annotations

import ast
from pathlib import Path

from studyforge.skills import buildserve
from tools.quality.source_names import named_sources

PACKAGE = Path(buildserve.__file__).parent

#: The framework modules the skill may take from. ⛔ A closed, positive set:
#: the verb table, the plan, the no-service sentence, the manifest, the exit codes.
ALLOWED = frozenset(
    {
        "studyforge.cli",
        "studyforge.cli.plan",
        "studyforge.cli.narrate.report",
        "studyforge.corpus.manifest",
        "studyforge.validate.cli",
        "studyforge.validate.report",
    }
)

#: Modules whose import is a way to write, copy, connect or spawn.
DOORS = frozenset({"shutil", "socket", "http", "urllib", "subprocess", "os", "tempfile"})

#: Calls that write, move or open a file. ⛔ Attribute names, so a `Path` or a module both count.
WRITERS = frozenset(
    {
        "write_text",
        "write_bytes",
        "mkdir",
        "makedirs",
        "touch",
        "unlink",
        "rename",
        "rmdir",
        "symlink_to",
        "copyfile",
        "copytree",
        "open",
    }
)


def modules() -> dict[str, str]:
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(PACKAGE.glob("*.py"))}


def reaches_past_the_verbs(source: str) -> list[str]:
    """Every import outside the allowed set, every door module, and every writing call."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom) and node.module:
            found += _judged(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                found += _judged(alias.name)
        elif isinstance(node, ast.Call):
            called = node.func
            name = called.attr if isinstance(called, ast.Attribute) else getattr(called, "id", "")
            if name in WRITERS:
                found.append(f"call {name}")
    return found


def _judged(module: str) -> list[str]:
    if module.split(".")[0] in DOORS:
        return [f"import {module}"]
    if module.startswith("studyforge.") and not module.startswith(buildserve.__name__):
        return [] if module in ALLOWED else [f"import {module}"]
    return []


def test_the_population_is_the_whole_package():
    assert {"__init__.py", "__main__.py", "cli.py", "run.py", "states.py"} <= set(modules())


def test_no_module_reaches_past_the_verbs():
    for name, source in modules().items():
        assert reaches_past_the_verbs(source) == [], name


def test_every_verb_is_reached_through_the_one_table():
    source = modules()["run.py"]
    assert source.count('VERBS["serve"].run(') == 1
    assert "VERBS[argv[0]].run(" in source


def test_a_planted_page_write_is_caught():
    planted = "from pathlib import Path\n(Path('out') / 'index.html').write_text('<html>')\n"
    assert reaches_past_the_verbs(planted) == ["call write_text"]


def test_a_planted_reach_into_the_builder_or_the_server_is_caught():
    for module in ("studyforge.generate", "studyforge.serve.app", "studyforge.narrate.client"):
        assert reaches_past_the_verbs(f"from {module} import x\n") == [f"import {module}"]
    assert reaches_past_the_verbs("import shutil\n") == ["import shutil"]


def test_no_file_the_skill_ships_names_a_source():
    # ⛔ R1, and SKILL.md is in the population: the floor's sweep reads `.py` alone.
    files = sorted(path for path in PACKAGE.iterdir() if path.suffix in (".py", ".md"))
    assert any(path.name == "SKILL.md" for path in files)
    for path in files:
        assert named_sources(path.read_text(encoding="utf-8")) == [], path.name


def test_a_planted_source_name_is_caught():
    planted = "# serves the " + "SPA" + "RQL tutorial\n"
    assert len(named_sources(planted)) == 1
