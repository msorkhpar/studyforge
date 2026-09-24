"""Mirror of `src/studyforge/narrate/wire.py` (R12): the wire, and who loads it.

⛔ **A build and a plan loading no wire is asserted over `sys.modules` in a FRESH interpreter**,
never over source text. `tests/studyforge/generate/test_no_synthesis.py` reads
import lines as text, and could not see `import studyforge.generate` loading the
HTTP client through `narrate.synth`'s own module-level import. ⭐ The positive
control runs the same child over an importer that does load the wire.

⭐ Reading an answer's bytes is `narrate.client`'s and is tested in `test_client.py`
(a health answer and a job body that are not JSON objects).
"""

from __future__ import annotations

import ast
import inspect
import json
import sys
from pathlib import Path

import pytest

from studyforge.narrate import wire
from studyforge.narrate.answers import NarrationError
from studyforge.narrate.wire import ServiceRefused, ServiceUnavailable, UnreadableAnswer
from tests.support import imports_module, repository_root, run

SOURCE = Path(inspect.getfile(wire))
WIRE = "studyforge.narrate.wire"
CLIENT = "studyforge.narrate.client"

#: One import in a clean interpreter, then every `studyforge` module it loaded.
CHILD = """
import importlib, json, sys
sys.path.insert(0, sys.argv[1])
importlib.import_module(sys.argv[2])
print(json.dumps(sorted(name for name in sys.modules if name.startswith("studyforge."))))
"""


def loaded_by(importer: str) -> list[str]:
    """Every `studyforge` module a fresh interpreter holds after importing `importer`."""
    root = repository_root()
    result = run([sys.executable, "-c", CHILD, str(root / "src"), importer], root)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


# --------------------------------------------------------------------------
# ⛔ A build and a plan load no wire
# --------------------------------------------------------------------------


@pytest.mark.parametrize("importer", ["studyforge.generate", "studyforge.cli.plan"])
def test_importing_the_build_or_the_plan_loads_no_wire_in_a_fresh_interpreter(importer):
    loaded = loaded_by(importer)
    # ⭐ Inhabitation first: the importer does reach narration's read side, so
    # the absence below is a property of the seam and not of a moved import.
    assert "studyforge.narrate.synth" in loaded, f"{importer} no longer reaches narrate.synth"
    assert [name for name in (WIRE, CLIENT) if name in loaded] == []


def test_the_plan_no_longer_reaches_the_narrate_verb_through_the_dispatcher():
    # ⚠️ `cli/plan` has two possible routes to the client,
    # `narrate.synth` and the dispatcher. ⭐ The dispatcher
    # resolves a verb only when it is dispatched, so the second route is closed;
    # this pins it closed, and `tests/studyforge/cli/test_dispatch.py` owns the clause.
    assert "studyforge.cli.narrate.stage" not in loaded_by("studyforge.cli.plan")


@pytest.mark.parametrize("importer", [CLIENT, WIRE])
def test_the_same_instrument_sees_the_wire_arrive_when_an_importer_loads_it(importer):
    # ⭐ The control: a child that could not see a loaded module would pass above.
    assert WIRE in loaded_by(importer)


# --------------------------------------------------------------------------
# ⛔ The decode error is the wire's, and inside the narration family
# --------------------------------------------------------------------------


def test_every_refusal_about_a_service_answer_is_this_modules_and_a_narration_error():
    for refusal in (ServiceUnavailable, ServiceRefused, UnreadableAnswer):
        assert refusal.__module__ == WIRE, refusal
        assert issubclass(refusal, NarrationError), refusal


# --------------------------------------------------------------------------
# ⛔ Standard library only, and the wire imports no client and no policy
# --------------------------------------------------------------------------


def test_the_module_imports_only_the_standard_library_and_two_framework_modules():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert imported == {
        "__future__",
        "collections.abc",
        "dataclasses",
        "studyforge.archive.scrub",
        "studyforge.narrate.answers",
        "urllib.error",
        "urllib.request",
    }


def test_the_wire_imports_neither_the_client_nor_the_placement_policy():
    for module in (CLIENT, "studyforge.corpus.placement", "studyforge.corpus.placement.names"):
        assert not imports_module(SOURCE, module), module
