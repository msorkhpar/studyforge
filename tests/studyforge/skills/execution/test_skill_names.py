"""Every Python name the execution `SKILL.md` prints resolves in the installed package.

⛔ **A procedure that names an entry point which does not exist cannot be
followed as printed**, and the next corpus is promised it can be. The first
corpus met exactly that: step 1 named a class method nobody ever wrote, and
step 5 a method the class does not have.

⭐ **What is read, and why each rule is the one it is:**

- **The document is the installed one** — `studyforge.skills.documents.text`,
  the reader the next corpus uses — never a path into this checkout.
- **Every call is a name**, backticked (`` `toolchain.select(…)` ``) or in an
  indented example block, and **every call must resolve**: a call is the one
  thing a reader types.
- **A dotted name resolves when its head is Python** — a name the execution
  package exports, one of its modules, or a `studyforge` subpackage. ⚠️ Any other
  head (`runner.image.tag_from`, `manifest.runtimes`) is a contract key path or a
  variable's attribute, which the Python namespace cannot answer, and it is
  skipped rather than guessed at, as is a span that names a file (`corpus.json`).
- **An example block's own `from … import …` must resolve**, and what it
  imports is a name the calls after it may use.
"""

from __future__ import annotations

import importlib
import re
from types import ModuleType

import pytest

from studyforge.skills import documents, execution

#: The skill whose document is read.
SKILL = "execution"

#: A backticked span that is a dotted name, optionally called.
SPAN = re.compile(r"`([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)(\(.*\))?`")

#: A call inside an example block: a dotted name not preceded by a name, a dot
#: or a closing bracket, so a method on an expression is not read as a name.
CALL = re.compile(r"(?<![\w.)\]])([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\(")

#: One `from … import …` line of an example block.
IMPORT = re.compile(r"^from ([\w.]+) import (.+)$")

#: What a span ending in one of these names: a file, never a Python name.
FILE_SUFFIXES = frozenset({"json", "md", "yaml", "env", "py", "toml", "txt", "html"})

#: Python's own words that look like calls in an example and are not names.
BUILTINS = frozenset({"print", "open", "list", "dict", "str", "len"})

#: The two sentences the first corpus met in step 1 and step 5. Both are
#: planted below and each must be read as unresolved.
MET = (
    "`Execution.for_corpus(manifest, ...)`",
    "`Execution.write(root)`",
)


def _examples(text: str) -> list[str]:
    """Every line of an indented example block, dedented."""
    return [line[4:] for line in text.splitlines() if line.startswith("    ") and line.strip()]


def _imported(lines: list[str]) -> tuple[dict[str, object], list[str]]:
    """What the example blocks import, and every import that does not resolve."""
    bound: dict[str, object] = {}
    broken: list[str] = []
    for line in lines:
        found = IMPORT.match(line.strip())
        if not found:
            continue
        module = importlib.import_module(found.group(1))
        for name in (one.strip() for one in found.group(2).split(",")):
            if hasattr(module, name):
                bound[name] = getattr(module, name)
            else:
                broken.append(f"from {found.group(1)} import {name}")
    return bound, broken


def _head(name: str, bound: dict[str, object]) -> object | None:
    """Return what the first segment of `name` is in Python, or `None` when it is not."""
    if name in bound:
        return bound[name]
    if hasattr(execution, name):
        return getattr(execution, name)
    try:
        return importlib.import_module(f"studyforge.{name}")
    except ModuleNotFoundError:
        return None


def _resolves(dotted: str, bound: dict[str, object]) -> bool | None:
    """Whether `dotted` resolves; `None` when its head is not a Python name at all."""
    first, *rest = dotted.split(".")
    found = _head(first, bound)
    if found is None:
        return None
    for part in rest:
        if not hasattr(found, part) and isinstance(found, ModuleType):
            try:
                importlib.import_module(f"{found.__name__}.{part}")
            except ModuleNotFoundError:
                return False
        if not hasattr(found, part):
            return False
        found = getattr(found, part)
    return True


def unresolved(text: str) -> list[str]:
    """Every name `text` prints that must resolve and does not."""
    lines = _examples(text)
    bound, broken = _imported(lines)
    for dotted, called in SPAN.findall(text):
        if not called and dotted.rsplit(".", 1)[-1] in FILE_SUFFIXES:
            continue
        answer = _resolves(dotted, bound)
        if answer is False or (called and answer is None):
            broken.append(f"`{dotted}{called}`")
    for line in lines:
        if IMPORT.match(line.strip()):
            continue
        for dotted in CALL.findall(line.split("#", 1)[0]):
            if dotted not in BUILTINS and _resolves(dotted, bound) is not True:
                broken.append(f"{dotted}(…) in an example")
    return sorted(set(broken))


def test_every_name_the_procedure_prints_resolves():
    text = documents.text(SKILL)

    assert unresolved(text) == []


def test_the_procedure_names_its_entry_point_and_both_record_steps():
    # ⭐ Not vacuous: the names a reader types are there to be resolved.
    text = documents.text(SKILL)

    for name in ("generate(", "write(execution, corpus)", "record_runner(", "record_editor("):
        assert name in text, name


@pytest.mark.parametrize("sentence", MET)
def test_the_names_the_first_corpus_met_are_read_as_unresolved(sentence):
    # ⛔ Both directions: the reader above must go RED on exactly what was met.
    assert unresolved(f"Call {sentence}.") == [sentence]


def test_a_call_in_an_example_that_names_nothing_is_unresolved():
    text = "    from studyforge.skills.execution import generate\n    made = for_corpus(x)\n"

    assert unresolved(text) == ["for_corpus(…) in an example"]


def test_an_import_of_a_name_the_package_does_not_export_is_unresolved():
    text = "    from studyforge.skills.execution import for_corpus\n"

    assert unresolved(text) == ["from studyforge.skills.execution import for_corpus"]


def test_a_contract_key_path_or_a_file_is_not_read_as_python():
    assert unresolved("`runner.image.tag_from`, `manifest.runtimes`, `corpus.json`") == []
