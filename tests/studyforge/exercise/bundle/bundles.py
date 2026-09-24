"""One real authored exercise on disk, so every check can be shown to bite.

⛔ **Nothing here is stubbed.** A bundle these functions write is a directory
with real files in it, and a gate record written over it is digested from those
files — so a plant is an edit to a real file whose effect can be printed before
a check is read, rather than a value typed into a dictionary.
"""

from __future__ import annotations

import json
from pathlib import Path

from studyforge.exercise.bundle import Places, bundle_of
from studyforge.exercise.gates import GateRecord, Verdict, record_document, taken_over

#: The bundle document every test starts from. ⚠️ A copy is taken per test, so
#: one test's edit is never another's input.
DOCUMENT = {
    "bundle_api": 1,
    "address": ["demo"],
    "variant": "prose",
    "unit": 2,
    "ordinal": 1,
    "title": "Build a bitmap",
    "lang": "python",
    "main_file": "bitmap.py",
    "test_file": "test_bitmap.py",
    "run_command": ["python3", "practice/demo/prose/unit-02/practice-1/bitmap.py"],
    "test_command": ["python3", "-m", "pytest", "practice/demo/prose/unit-02/practice-1"],
    "provenance": "generated",
    "trust": "advisory",
    "cases": [
        {"id": "test_builds", "kind": "main", "says": "builds a bitmap"},
        {"id": "test_empty", "kind": "edge", "says": "handles no fields at all"},
    ],
    "report": {"format": "junit", "path": "target/report.xml"},
    "origin": {"path": "src/one.md", "section": "Bitmaps"},
}

STATEMENT = "Write a builder for the primary bitmap.\n\n- eight bytes\n- counted from one\n"
STARTER = "def build(fields):\n    ...\n"
REFERENCE = "def build(fields):\n    return sum(1 << (64 - n) for n in fields)\n"
TESTS = "def test_builds():\n    pass\n\n\ndef test_empty():\n    pass\n"
PLANT = "def build(fields):\n    return 1\n"

#: What a build file of this fixture holds. ⚠️ Not a real tool's file:
#: the framework never reads one, so its bytes only have to arrive intact.
BUILD_TEXT = "[build]\nrequires = ['placeholder']\n"

#: The five gates the gate framework declares for the `code` family, all held.
HELD = ("G1", "G2", "G3", "G4", "G5")


def document(**overrides) -> dict:
    """A bundle document, with any key replaced.

    ⚠️ The two commands follow the identity unless a test replaces them: a
    command names a path as the corpus root sees it, so a fixture that kept the
    default while moving the unit would be refused for the right reason in the
    wrong test.
    """
    declared = {**json.loads(json.dumps(DOCUMENT)), **overrides}
    spot = bundle_of({**declared, **_DEFAULT_COMMANDS}, "bundle.json").places
    if "run_command" not in overrides:
        declared["run_command"] = ["python3", spot.in_workspace(declared["main_file"])]
    if "test_command" not in overrides:
        declared["test_command"] = ["python3", "-m", "pytest", spot.workspace]
    return declared


#: Commands that pass containment for any identity, used only while the real
#: ones are being derived.
_DEFAULT_COMMANDS = {"run_command": ["python3"], "test_command": ["python3"]}


def places(**overrides) -> Places:
    """Where the document's exercise sits."""
    return bundle_of(document(**overrides), "bundle.json").places


def write_bundle(root: Path, **overrides) -> Places:
    """Write one complete bundle under `root` and return where it landed."""
    declared = document(**overrides)
    bundle = bundle_of(declared, "bundle.json")
    where = root / bundle.places.bundle
    (where / "starter").mkdir(parents=True, exist_ok=True)
    (where / "reference").mkdir(parents=True, exist_ok=True)
    (where / "tests").mkdir(parents=True, exist_ok=True)
    (where / "plants" / "edge-1").mkdir(parents=True, exist_ok=True)
    _put(where / "bundle.json", json.dumps(declared, indent=2) + "\n")
    _put(where / "statement.md", STATEMENT)
    _put(where / "starter" / bundle.main_file, STARTER)
    _put(where / "reference" / bundle.main_file, REFERENCE)
    _put(where / "tests" / bundle.test_file, TESTS)
    _put(where / "plants" / "edge-1" / bundle.main_file, PLANT)
    for path in bundle.build:
        _put(where / "build" / path, BUILD_TEXT)
    return bundle.places


def _put(path: Path, text: str) -> None:
    """Write one file, making whatever directory it needs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def inputs_of(root: Path, spot: Places) -> tuple:
    """Digest every file of the bundle, in the order a `code` family writes them."""
    bundle = bundle_of(json.loads((root / spot.document).read_text(encoding="utf-8")), "b")
    return taken_over(
        root / spot.bundle,
        (
            ("statement", "statement.md"),
            ("starter", f"starter/{bundle.main_file}"),
            ("reference", f"reference/{bundle.main_file}"),
            ("tests", f"tests/{bundle.test_file}"),
            (f"plant:{bundle.cases[1].id}", f"plants/edge-1/{bundle.main_file}"),
            *((f"build:{path}", f"build/{path}") for path in bundle.build),
        ),
        spot.bundle,
    )


def write_gate_record(root: Path, spot: Places, *, held: bool = True) -> dict:
    """Write a gate record over the bundle's real files and return what was written."""
    record = GateRecord(
        inputs=inputs_of(root, spot),
        origins=(),
        verdicts=tuple(
            Verdict(
                id=gate,
                family="code",
                held=held or gate != "G3",
                says="the gate held" if held or gate != "G3" else "an edge plant passed",
                recorded=(),
            )
            for gate in HELD
        ),
    )
    written = record_document(record)
    (root / spot.gates).write_text(json.dumps(written, indent=2) + "\n", encoding="utf-8")
    return written
