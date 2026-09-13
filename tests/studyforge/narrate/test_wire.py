"""Mirror of `src/studyforge/narrate/wire.py` (R12): the wire, and who loads it (`W223`).

⛔ **`SF-38/9` and `W224/4` are asserted over `sys.modules` in a FRESH interpreter**,
never over source text. `tests/studyforge/generate/test_no_synthesis.py` reads
import lines as text, and could not see `import studyforge.generate` loading the
HTTP client through `narrate.synth`'s own module-level import. ⭐ The positive
control runs the same child over an importer that does load the wire.

⚠️ The home-path material below is assembled at run time, as in `test_client.py`.
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
from studyforge.narrate.wire import (
    Received,
    ServiceRefused,
    ServiceUnavailable,
    UnreadableAnswer,
    decoded,
    field_of,
    object_of,
)
from tests.support import imports_module, repository_root, run

SOURCE = Path(inspect.getfile(wire))
WIRE = "studyforge.narrate.wire"
CLIENT = "studyforge.narrate.client"

# ⛔ Assembled, never written as a literal.
HOME = "/" + "home/jane"

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
# ⛔ SF-38/9 and W224/4: a build and a plan load no wire
# --------------------------------------------------------------------------


@pytest.mark.parametrize("importer", ["studyforge.generate", "studyforge.cli.plan"])
def test_importing_the_build_or_the_plan_loads_no_wire_in_a_fresh_interpreter(importer):
    loaded = loaded_by(importer)
    # ⭐ Inhabitation first: the importer does reach narration's read side, so
    # the absence below is a property of the seam and not of a moved import.
    assert "studyforge.narrate.synth" in loaded, f"{importer} no longer reaches narrate.synth"
    assert [name for name in (WIRE, CLIENT) if name in loaded] == []


def test_the_plan_reaches_the_narrate_verb_through_the_dispatcher():
    # ⚠️ MEASURED: `cli/plan` has TWO routes to the client, `narrate.synth` and
    # the dispatcher, which imports every verb. This pins the second route as
    # inhabited, so the absence above covers it rather than missing it.
    assert "studyforge.cli.narrate.stage" in loaded_by("studyforge.cli.plan")


@pytest.mark.parametrize("importer", [CLIENT, WIRE])
def test_the_same_instrument_sees_the_wire_arrive_when_an_importer_loads_it(importer):
    # ⭐ The control: a child that could not see a loaded module would pass above.
    assert WIRE in loaded_by(importer)


# --------------------------------------------------------------------------
# ⛔ W212/3: the decode error is the wire's, and inside the narration family
# --------------------------------------------------------------------------


def test_every_refusal_about_a_service_answer_is_this_modules_and_a_narration_error():
    for refusal in (ServiceUnavailable, ServiceRefused, UnreadableAnswer):
        assert refusal.__module__ == WIRE, refusal
        assert issubclass(refusal, NarrationError), refusal


@pytest.mark.parametrize("body", [b"<html>", b"\xff\xfe", b"[1, 2]", b'"text"'])
def test_a_body_that_is_not_a_json_object_is_unreadable(body):
    with pytest.raises(UnreadableAnswer):
        decoded(Received(200, "text/html", body), "/healthz")


def test_a_json_object_decodes_the_positive_control():
    assert decoded(Received(200, "application/json", b'{"a": 1}'), "/healthz") == {"a": 1}


def test_a_missing_field_is_unreadable_and_names_the_field_and_the_route():
    with pytest.raises(UnreadableAnswer) as refused:
        field_of({"provides": 3}, "engine_model", "/healthz")
    assert "engine_model" in str(refused.value)
    assert "/healthz" in str(refused.value)
    assert field_of({"engine_model": "m"}, "engine_model", "/healthz") == "m"


def test_a_value_that_is_not_an_object_is_refused_without_being_quoted():
    with pytest.raises(UnreadableAnswer) as refused:
        object_of([f"{HOME}/work"], "/v1/jobs")
    assert "jane" not in str(refused.value)


# --------------------------------------------------------------------------
# ⛔ Standard library only, and the wire imports no client and no policy
# --------------------------------------------------------------------------


def test_the_module_imports_only_the_standard_library_and_three_framework_modules():
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
        "json",
        "studyforge.archive.scrub",
        "studyforge.describe",
        "studyforge.narrate.answers",
        "urllib.error",
        "urllib.request",
    }


def test_the_wire_imports_neither_the_client_nor_the_placement_policy():
    for module in (CLIENT, "studyforge.corpus.placement", "studyforge.corpus.placement.names"):
        assert not imports_module(SOURCE, module), module
