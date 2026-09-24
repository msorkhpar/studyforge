"""The package's own contract: nothing in this gate stopped being covered.

⛔ **Splitting a gate is riskier than splitting a module.** A module that stops
being exercised fails when somebody calls it; a *coverage* check that stops
covering something passes forever, which is the shape W7 itself was opened
against. ⭐ So the split is asserted rather than trusted: the module set is
derived and its inhabitation asserted before anything sweeps it; every helper
module is asserted to be imported by a test module, and every name those
helpers define is asserted to be read by something.
"""

import ast
from pathlib import Path

from tests.gate_coverage import GATED_TREES, HOME, SCAN_ROOT

PACKAGE = Path(__file__).parent

#: ⛔ Derived, never listed — the mistake this whole file exists to make loud.
MODULES = sorted(path.name for path in PACKAGE.glob("*.py"))

#: The modules that hold the machinery rather than the assertions.
HELPERS = ("tell.py", "probes.py")


def defined_names(source: str) -> set[str]:
    """Every name bound at the top level of `source`."""
    names: set[str] = set()
    for node in ast.parse(source).body:
        if isinstance(node, ast.ClassDef | ast.FunctionDef):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
                elif isinstance(target, ast.Tuple):
                    names.update(e.id for e in target.elts if isinstance(e, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def loaded_names(source: str) -> set[str]:
    """Every name this source *reads* — never the ones it merely binds.

    ⚠️ `ast.Store` is excluded on purpose. A name that appears only where it is
    assigned is a name nothing uses, and counting its own binding as a use is
    how a dead helper looks alive.
    """
    seen: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            seen.add(node.id)
        elif isinstance(node, ast.Attribute):
            seen.add(node.attr)
        elif isinstance(node, ast.ImportFrom):
            seen.update(alias.asname or alias.name for alias in node.names)
    return seen


def imported_modules(source: str) -> set[str]:
    """Every `tests.gate_coverage.*` module this source imports from."""
    named: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
            "tests.gate_coverage"
        ):
            named.add((node.module or "").rpartition(".")[2] + ".py")
    return named


def test_the_package_is_the_six_modules_this_file_sweeps():
    # ⭐ The inhabitation assertion, first, because every sweep below runs over
    # `MODULES` and a sweep over an empty set passes.
    assert MODULES == [
        "__init__.py",
        "probes.py",
        "tell.py",
        "test_coverage.py",
        "test_init.py",
        "test_tell.py",
    ]
    assert all(name in MODULES for name in HELPERS)


def test_every_helper_module_is_imported_by_a_test_module():
    # ⛔ **The first half of the split's guard.** A helper module that no test
    # module imports any more is a piece of this gate that stopped being
    # covered — and it would not go red, it would go quiet.
    tests = {name for name in MODULES if name.startswith("test_")}
    assert tests == {"test_coverage.py", "test_init.py", "test_tell.py"}
    imported: set[str] = set()
    for name in tests:
        imported |= imported_modules((PACKAGE / name).read_text(encoding="utf-8"))
    assert set(HELPERS) <= imported, sorted(set(HELPERS) - imported)


def test_every_name_the_helpers_define_is_read_somewhere_in_the_package():
    # ⛔ **The second half, and it is the one that survives a careless split.**
    # ⚠️ Five of these are reached *transitively* rather than by a test naming
    # them — `DECODERS`, `READER`, `DELEGATES`, `_dotted`, `resolved_calls` —
    # so the question asked is "does anything read it", not "does a test name
    # it". ⛔ A name whose only reader moved to the other half of the split
    # would answer no, and nothing else in this repository would notice.
    read: set[str] = set()
    for name in MODULES:
        read |= loaded_names((PACKAGE / name).read_text(encoding="utf-8"))

    defined: set[str] = set()
    for name in HELPERS:
        defined |= defined_names((PACKAGE / name).read_text(encoding="utf-8"))
    assert len(defined) >= 12, sorted(defined)

    assert sorted(defined - read) == [], sorted(defined - read)


def test_the_guard_above_would_notice(tmp_path):
    # ⛔ Watched failing first, and the planted thing is in a shape the clause did not
    # picture: a name bound by tuple assignment, which is how `READER,
    # DELEGATES` is spelled and is the one form a naive walk drops.
    helper = tmp_path / "helper.py"
    helper.write_text("SEEN, UNSEEN = 1, 2\n\n\ndef use():\n    return SEEN\n", "utf-8")

    defined = defined_names(helper.read_text(encoding="utf-8"))
    read = loaded_names(helper.read_text(encoding="utf-8"))
    assert defined == {"SEEN", "UNSEEN", "use"}
    assert sorted(defined - read) == ["UNSEEN", "use"]

    # ⛔ And the orphan-module half, planted the same way: a test module that
    # imports only one of the two helpers leaves the other unreached.
    reader = tmp_path / "test_reader.py"
    reader.write_text("from tests.gate_coverage.tell import GATE\n", encoding="utf-8")
    assert imported_modules(reader.read_text(encoding="utf-8")) == {"tell.py"}
    assert "probes.py" not in imported_modules(reader.read_text(encoding="utf-8"))

    # ⭐ And a subject that cannot match, whose reading must differ from both
    # passes above: a module that defines nothing and imports nothing from this
    # package answers the empty set to both questions, which is why the
    # inhabitation bounds are asserted before either sweep runs.
    empty = tmp_path / "empty.py"
    empty.write_text('"""Nothing here."""\n', encoding="utf-8")
    assert defined_names(empty.read_text(encoding="utf-8")) == set()
    assert imported_modules(empty.read_text(encoding="utf-8")) == set()


def test_the_bound_lives_in_the_contract_and_the_tell_does_not_read_it():
    # ⛔ The seam. `tell.py` answers *is this a reader*; it must not know which
    # trees this repository decided to gate, or the bound and the scan drift
    # into one thing again — a root chosen by a string nobody defends.
    tell = (PACKAGE / "tell.py").read_text(encoding="utf-8")
    assert "GATED_TREES" not in tell
    assert "SCAN_ROOT" not in tell
    assert SCAN_ROOT in GATED_TREES
    assert HOME.startswith("/") and "jane" in HOME
