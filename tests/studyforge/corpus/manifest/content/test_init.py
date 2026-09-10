"""Mirror of `src/studyforge/corpus/manifest/content/__init__.py` (R12).

⛔ The package contract, asserted rather than described: what a consumer may
import, that the seam really is one-way, and that the split lost nothing.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from studyforge.corpus.manifest import content
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
    # ⛔ Ruling 101's producer half: a name a second package needs is on this
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
    # ⛔ Ruling 11: watch it pass without the mechanism. Nothing in the real
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


def test_the_one_private_name_edits_already_takes_is_still_reachable():
    # ⛔ `W40/1`. `manifest.edits` imports `_escape` from this package and has
    # since W19 unified the two refusals; the split moved it into `parse`, so
    # the package re-exports it. ⭐ Pinned here rather than left to be found
    # by an ImportError in a module this task does not own.
    from studyforge.corpus.manifest.content import _escape

    assert _escape("/etc/passwd") == "begins with a slash"
    assert _escape is parse._escape
    assert "_escape" not in content.__all__


@pytest.mark.parametrize(
    "name",
    ["MIN_WHY_CHARS", "WILDCARDS", "Classification", "ContentPolicy", "Exclusion", "NotMaterial"],
)
def test_the_package_answers_the_spelling_the_module_answered(name):
    # ⭐ Every importer in the tree names `studyforge.corpus.manifest.content`
    # and none of them changed: a package answers the spelling a module did.
    assert getattr(content, name) is not None
