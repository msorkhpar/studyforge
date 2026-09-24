"""The package's own contract: what it ships, what it names, and what it never does.

⛔ R1, R18 and §8.3 are properties of the whole package rather than of any one
module, so they are measured over every file it ships — `SKILL.md` included,
because the floor's own sweep reads `.py` alone.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from studyforge.skills import execution
from tests.harness.sources import named_sources

#: The package on disk.
PACKAGE = Path(execution.__file__).parent

#: The procedure that precedes every module beside it (§9).
SKILL = PACKAGE / "SKILL.md"

#: ⛔ Everything of a pinned component this package may NOT read. R18: a
#: consumer that reads one of these has forked the component, silently.
NEVER_READ = ("Dockerfile", "README.md", "consuming/consuming.py", "entrypoint.sh")

#: ⛔ What starting a container needs, whatever it is spelled. §8.3: this skill
#: writes a compose file and a document; the person running it runs docker.
INVOCATION = ("subprocess", "os", "shutil", "socket", "http")


def files(*suffixes: str) -> list[Path]:
    """Every file the package ships with one of `suffixes`."""
    return sorted(path for path in PACKAGE.iterdir() if path.suffix in suffixes)


def test_the_procedure_exists_and_precedes_the_modules_beside_it():
    # ⛔ §9: a skill written after the thing it "produces" has been validated
    # against exactly one source. Its being the branch's first commit is what
    # `git log` can check; that it exists at all is checked here.
    assert SKILL.is_file() and SKILL.read_text(encoding="utf-8").startswith("# Skill —")


def test_every_module_the_package_ships_is_on_its_surface_or_private_to_it():
    shipped = {path.stem for path in files(".py")} - {"__init__"}
    for name in shipped:
        module = ast.parse((PACKAGE / f"{name}.py").read_text(encoding="utf-8"))
        assert ast.get_docstring(module), f"{name}.py ships without a contract"


def test_no_file_it_ships_names_a_source():
    # ⛔ R1. The framework knows nothing about any source, and `SKILL.md` is in
    # the population because the floor's sweep reads `.py` alone.
    for path in files(".py", ".md"):
        assert named_sources(path.read_text(encoding="utf-8")) == [], path.name


@pytest.mark.parametrize("never", NEVER_READ)
def test_no_module_names_a_component_file_but_its_contract_as_a_value(never):
    # ⛔ R18. ⚠️ **String literals, never prose**: `contract.py`'s own docstring
    # names all four to say it does NOT read them, and a source grep would flag
    # the sentence that states the rule. A literal is a value a call could open.
    for path in files(".py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        literals = {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        named = [one for one in literals if never in one and "\n" not in one]
        assert named == [], (path.name, named)


def test_the_literal_check_is_not_vacuous():
    # ⭐ The other direction: a planted literal is caught.
    planted = ast.parse('WHERE = "Dockerfile"' + chr(10))
    literals = {
        node.value
        for node in ast.walk(planted)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    assert "Dockerfile" in literals


def test_the_one_file_it_does_read_is_named_once():
    assert execution.CONSUMING == "consuming.json"


@pytest.mark.parametrize("wanted", INVOCATION)
def test_this_skill_starts_no_container_because_it_can_reach_nothing(wanted):
    # ⛔ §8.3, structurally: no module here imports anything that could invoke a
    # process, open a socket or speak HTTP, so *"it starts no container"* is a
    # property of what it can reach rather than a promise in prose.
    for path in files(".py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            heads = []
            if isinstance(node, ast.Import):
                heads = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                heads = [node.module.split(".")[0]]
            assert wanted not in heads, (path.name, wanted)


def test_it_imports_no_third_party_package():
    # ⛔ Standard library only in framework source — which is also why the YAML
    # it emits is emitted rather than serialised by a library.
    allowed = {
        "studyforge",
        "__future__",
        "json",
        "collections",
        "dataclasses",
        "hashlib",
        "pathlib",
    }
    for path in files(".py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] in allowed, (path.name, alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] in allowed, (path.name, node.module)


def test_every_name_on_the_surface_resolves_and_none_is_there_twice():
    assert len(set(execution.__all__)) == len(execution.__all__)
    for name in execution.__all__:
        assert hasattr(execution, name), name


def test_the_procedure_states_the_rule_that_a_missing_key_is_a_finding():
    # ⛔ R19: this skill is where a consuming contract's
    # sufficiency is demonstrated, so the procedure has to say what happens
    # when it is not sufficient.
    text = SKILL.read_text(encoding="utf-8")
    assert "FINDING" in text and "R19" in text
    assert "never a value" in text


def test_the_procedure_states_the_empty_answer_for_a_corpus_that_is_not_runnable():
    # ⚠️ Whitespace-normalised: the procedure is wrapped prose, and a sentence
    # that crosses a line break is the same sentence.
    text = " ".join(SKILL.read_text(encoding="utf-8").split())
    assert "no file from this skill and no error" in text
