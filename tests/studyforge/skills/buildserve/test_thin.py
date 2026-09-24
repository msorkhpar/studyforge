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
from tests.harness.sources import named_sources

PACKAGE = Path(buildserve.__file__).parent

#: The framework modules the skill may take from. ⛔ A closed, positive set:
#: the verb table, the plan, the no-service sentence, the narration component's
#: own default address, the manifest, the exit codes.
#:
#: ⚠️ `cli.narrate.cli` is admitted for `DEFAULT_SERVICE` alone, and the argument
#: is `NO_SERVICE`'s: a skill that told an operator to start a service on another
#: port would be sending them where the verb never calls. ⛔ It buys the constant
#: and nothing else — no client, no transport, no socket.
#:
#: ⚠️ `serve.routes.run` is admitted for `NAMESPACE` alone (`SK-03/3`): the
#: execution namespace's one spelling is the route's, and a skill that spelled it
#: again would report `toolchain` against a server that offers it. ⛔ It buys the
#: constant and nothing else — the skill never starts a run.
#:
#: ⚠️ `execute` is admitted for `ModeProbe`, `container_for` and `HOST` alone (`W381`):
#: where a run executes is ruled to be `execute`'s probe's answer, ONE definition, so
#: the skill imports it rather than copying it. ⛔ The probe only reads (`docker
#: inspect`); the skill never starts, stops or enters a container, and never a run.
ALLOWED = frozenset(
    {
        "studyforge.cli",
        "studyforge.execute",
        "studyforge.serve.routes.run",
        "studyforge.cli.plan",
        "studyforge.cli.narrate.cli",
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
    expected = {
        "__init__.py",
        "__main__.py",
        "cli.py",
        "narration.py",
        "run.py",
        "states.py",
        "verbs.py",
    }
    assert expected <= set(modules())


def test_no_module_reaches_past_the_verbs():
    for name, source in modules().items():
        assert reaches_past_the_verbs(source) == [], name


#: The seam onto the verbs, and the skill's own parser — the two modules allowed a `--` flag.
SEAM, OWN_PARSER = "verbs.py", "cli.py"


def outside_the_seam(source: str) -> list[str]:
    """Every reach into the verb table, and every verb flag spelled, in one module's source."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name) and node.id == "VERBS":
            found.append("VERBS")
        elif isinstance(node, ast.alias) and node.name == "VERBS":
            found.append("import VERBS")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value.startswith("--"):
                found.append(node.value)
    return found


def test_every_verb_is_reached_through_the_one_seam():
    # ⛔ The coordinator's relay for `W230`: a verb whose arguments change is an
    # edit to `verbs.py` alone, so no other module may reach the table or spell a flag.
    for name, source in modules().items():
        if name in (SEAM, OWN_PARSER):
            continue
        assert outside_the_seam(source) == [], name
    assert outside_the_seam(modules()[SEAM]), "the seam reaches nothing; this check is vacuous"


def test_a_planted_verb_flag_or_table_reach_outside_the_seam_is_caught():
    assert outside_the_seam('argv = ["serve", corpus, "--site", site]\n') == ["--site"]
    planted = "from studyforge.cli import VERBS\nVERBS\n"
    assert outside_the_seam(planted) == ["import VERBS", "VERBS"]


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
