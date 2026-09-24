"""Mirror of `src/studyforge/corpus/manifest/content/__init__.py` (R12).

⛔ The package contract, asserted rather than described: what a consumer may
import, that the seam really is one-way, and that the split lost nothing.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from studyforge.corpus.manifest import content, errors
from studyforge.corpus.manifest.content import parse, policy

PACKAGE = Path(content.__file__).parent

#: ⛔ Derived, then asserted to be what it should be **before** anything sweeps
#: it: a sweep over an empty set passes, and a sweep over a set that quietly
#: lost a module passes just as loudly.
MODULES = sorted(path.name for path in PACKAGE.glob("*.py"))


def imported_modules(source: str) -> set[str]:
    """Every module name this source imports from, however it spells it."""
    named: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            named.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            prefix = "." * node.level + (node.module or "")
            named.add(prefix)
            named.update(f"{prefix}.{alias.name}" for alias in node.names)
    return named


def test_the_package_is_the_three_modules_this_file_sweeps():
    # ⭐ The inhabitation assertion. Every sweep below runs over `MODULES`, so
    # a fourth module arriving — or one of these disappearing — is a failure
    # here rather than a check that silently stops covering it.
    assert MODULES == ["__init__.py", "parse.py", "policy.py"]


def test_the_public_surface_is_what_a_consumer_needs_and_no_more():
    # ⛔ One exported home (R21): a name a second package needs is on this
    # list, and reaching past it for one that is not is the deviation.
    assert content.__all__ == [
        "MIN_WHY_CHARS",
        "WILDCARDS",
        "Classification",
        "ContentPolicy",
        "Exclusion",
        "NotMaterial",
        "parse_content",
    ]
    for name in content.__all__:
        assert hasattr(content, name), name


def test_the_seam_holds_and_the_model_never_reads_the_reader():
    # ⛔ The direction is the whole seam: `parse` builds what `policy` defines,
    # and `policy` has no reason to know a manifest was ever a dict. A cycle
    # here is an import error at build time; the check is that it cannot start.
    model = imported_modules(Path(policy.__file__).read_text(encoding="utf-8"))
    assert not any("content.parse" in name or name == ".parse" for name in model), model

    reader = imported_modules(Path(parse.__file__).read_text(encoding="utf-8"))
    assert "studyforge.corpus.manifest.content.policy" in reader, reader


def test_the_guard_above_would_notice(tmp_path):
    # ⛔ Watch it pass without the mechanism. Nothing in the real
    # package is in the forbidden shape, so the control builds one — and it is
    # built in the spelling the clause did **not** picture, a relative import.
    planted = tmp_path / "policy.py"
    planted.write_text("from .parse import parse_content\n", encoding="utf-8")
    named = imported_modules(planted.read_text(encoding="utf-8"))
    assert any("content.parse" in name or name == ".parse" for name in named), named

    # ⭐ And a subject that cannot match: a module importing neither half must
    # read differently from the pass above, or the guard is answering `True`
    # to everything.
    innocent = tmp_path / "unrelated.py"
    innocent.write_text("from pathlib import PurePosixPath\n", encoding="utf-8")
    assert imported_modules(innocent.read_text(encoding="utf-8")) == {
        "pathlib",
        "pathlib.PurePosixPath",
    }


def test_every_public_name_in_the_package_is_reachable_through_it():
    # ⭐ Derived from the submodules rather than retyped, so a name added to
    # either half and not exported fails here instead of being discovered by a
    # consumer who cannot import it.
    defined: set[str] = set()
    for name in MODULES:
        if name == "__init__.py":
            continue
        tree = ast.parse((PACKAGE / name).read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.ClassDef | ast.FunctionDef):
                defined.add(node.name)
            elif isinstance(node, ast.Assign):
                defined.update(target.id for target in node.targets if isinstance(target, ast.Name))
    public = {name for name in defined if not name.startswith("_")}
    assert public, defined
    assert public == set(content.__all__), sorted(public ^ set(content.__all__))


def routes_to_the_escaping_phrase() -> list[str]:
    """Every name on this package through which `errors._escape` is reachable.

    ⛔ Identity, not spelling: a bridge need not be spelled `_escape`.
    """
    return sorted(name for name, value in vars(content).items() if value is errors._escape)


def test_the_package_neither_defines_nor_routes_to_the_escaping_phrase():
    # ⛔ The escaping phrase has one home, in `manifest.errors`. There is no
    # bridge through this package, so a test asserting one
    # still stands would be asserting the defect. ⭐ What is worth pinning is
    # the other half of the same fact — `edits` does not reach past this
    # package's `__all__`, because there is nothing here to reach.
    defined = [
        name
        for name in MODULES
        for node in ast.parse((PACKAGE / name).read_text(encoding="utf-8")).body
        if isinstance(node, ast.FunctionDef) and node.name == "_escape"
    ]
    assert defined == [], defined
    assert routes_to_the_escaping_phrase() == []
    assert "_escape" not in content.__all__

    # ⭐ And it did not move by being copied: `parse` still calls the one
    # function both refusals share, from its home.
    assert parse._escape is errors._escape


def test_the_route_check_above_would_notice(monkeypatch):
    # ⛔ Three readings, and the plant takes a shape the clause did not picture: the
    # clause pictured a name `_escape`, so the plant is the SAME function
    # bound under a different one — the redundant-alias bridge, renamed.
    monkeypatch.setattr(content, "_e", errors._escape, raising=False)
    assert routes_to_the_escaping_phrase() == ["_e"]

    # ⭐ The impossible subject: a decoy that carries the forbidden *name* and
    # is not the function reads clean, which is how this differs from a grep.
    monkeypatch.delattr(content, "_e")
    monkeypatch.setattr(content, "_escape", len, raising=False)
    assert routes_to_the_escaping_phrase() == []


@pytest.mark.parametrize(
    "name",
    ["MIN_WHY_CHARS", "WILDCARDS", "Classification", "ContentPolicy", "Exclusion", "NotMaterial"],
)
def test_the_package_answers_the_spelling_the_module_answered(name):
    # ⭐ Every importer in the tree names `studyforge.corpus.manifest.content`
    # and none of them changed: a package answers the spelling a module did.
    assert getattr(content, name) is not None
