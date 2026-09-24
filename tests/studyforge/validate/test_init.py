"""Mirror of `src/studyforge/validate/__init__.py` (R12)."""

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from pathlib import Path

from studyforge import validate
from tests.support import assert_package_contract, repository_root

#: This package, as an importer spells it.
PACKAGE = "studyforge.validate"

#: ⛔ **Names another package takes out of a `validate` MODULE that are NOT on
#: `studyforge.validate.__all__`** — Ruling 101's producer half. ⭐ **EMPTY, and
#: the emptiness is the claim:** every such name is now exported, so a
#: name that leaves this surface REAPPEARS here and reds.
#:
#: ⚠️ **It stays as a declared set rather than being folded into a `== set()`**, so
#: the next off-surface name is named in the failure with its module, and so that
#: re-opening it is a deliberate edit carrying a ground — never a quiet append.
#: ⛔ **`W199`'s rule stands: adding an entry to quiet this is declaring a defect,
#: not fixing one.**
OFF_SURFACE: set[tuple[str, str]] = set()

#: ⭐ **The whole public surface, spelled out** — the model is
#: `tests/studyforge/corpus/placement/test_init.py`, which `W199` named as the
#: instrument this package had none of. ⚠️ Duplicated from `__all__` on purpose.
#:
#: ⛔ **It is the half that does not depend on a CONSUMER.** The sweep below holds a
#: name on this surface only while some package still takes it from a module here;
#: fix those spellings to the package form and the sweep goes quiet about them.
#: ⭐ This pin reds either way, so the five shadowing names cannot leave silently.
PUBLIC_SURFACE = frozenset(
    {
        "CHECKS",
        "FENCE",
        "HEADING_LINE",
        "INVALID",
        "OK",
        "RULE_DUPLICATE_PATH",
        "UNUSABLE",
        "Finding",
        "Held",
        "Report",
        "Snapshot",
        "Unchecked",
        "Walk",
        "check_placement",
        "check_untouched",
        "headings",
        "main",
        "snapshot",
        "validate",
    }
)


def surface_order(name: str) -> tuple[int, str]:
    """Where `name` sorts on a package surface: constants, then types, then callables."""
    return (0 if name.isupper() else 1 if name[:1].isupper() else 2, name)


def taken_from_a_module() -> list[tuple[str, str, str]]:
    """Every `(importer, module, name)` a package outside `validate` takes from a module here.

    ⛔ A sub-package is not a submodule: `validate.source` states its own
    `__all__`, so under Ruling 101 it is its own owner and importing from it is
    not reaching past a surface.
    """
    source = repository_root() / "src"
    inside = source / Path(*PACKAGE.split("."))
    taken: list[tuple[str, str, str]] = []
    for path in sorted(source.rglob("*.py")):
        if inside == path or inside in path.parents:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.level or not node.module:
                continue
            parts = node.module.split(".")
            if len(parts) != 3 or ".".join(parts[:2]) != PACKAGE:
                continue
            if (inside / parts[2] / "__init__.py").is_file():
                continue
            where = path.relative_to(repository_root()).as_posix()
            taken.extend((where, node.module, alias.name) for alias in node.names)
    return taken


def test_states_its_contract():
    assert_package_contract(validate, "studyforge.validate")


def test_the_public_surface_is_exactly_what_the_contract_says():
    # ⛔ The pin that does not depend on a consumer's import SPELLING, so the
    # five shadowing names exported here cannot leave while the sweep below stays quiet.
    assert set(validate.__all__) == PUBLIC_SURFACE
    missing = sorted(name for name in PUBLIC_SURFACE if not hasattr(validate, name))
    assert missing == [], "exported but absent: " + ", ".join(missing)


def test_the_headings_export_shadows_its_module_without_hiding_it():
    # ⛔ The shadowing rule, ASSERTED rather than argued. The surface exports the
    # CALLABLE; the module keeps its name in `sys.modules` and every sibling it
    # had, so shadowing costs a reader nothing they could previously reach.
    assert inspect.isfunction(validate.headings), "the surface must export the callable"
    module = importlib.import_module("studyforge.validate.headings")
    assert inspect.ismodule(module), "the submodule must still be reachable as a module"
    assert validate.headings is module.headings, "the export is a SECOND definition, not a binding"
    for sibling in ("count_headings", "region", "Heading", "Region"):
        assert hasattr(module, sibling), f"shadowing hid {sibling!r} on the module"


def test_the_shadowing_binds_the_callable_in_the_as_form_too():
    # ⚠️ **The wart, asserted because writing it down was not enough.** `import
    # a.b.c as x` binds the PACKAGE ATTRIBUTE, which is the function — so the
    # `as` form does NOT hand back the module. ⛔ This mirror's own first draft
    # used it and broke; the assertion is what stops the next reader repeating it.
    # ⭐ It is not a cost the export introduced: every shadowing package in `src/`
    # already behaves this way, which is half the ground for the ruling.
    import studyforge.validate.headings as bound

    assert inspect.isfunction(bound), "the `as` form is expected to bind the callable"
    assert sys.modules["studyforge.validate.headings"] is not bound


def test_every_exported_name_resolves_and_is_declared_once():
    # ⛔ Ruling 101's producer half, over this package's OWN exports: a surface
    # naming something it does not have is a surface a consumer cannot use, and
    # a name declared twice is two entries a reader must reconcile.
    assert validate.__all__, "the package declares no surface at all"
    for name in validate.__all__:
        assert hasattr(validate, name), f"__all__ names {name!r}, which is not exported"
    assert len(set(validate.__all__)) == len(validate.__all__), "a name is exported twice"
    assert list(validate.__all__) == sorted(validate.__all__, key=surface_order), (
        "the surface is out of order: constants, then types, then callables"
    )


def test_a_name_another_package_takes_from_a_module_here_is_on_this_surface():
    # ⛔ `W199`, and it is CLOSED over the tree rather than over two names: the
    # defect the row names is that `archive` and `raw` were minted twice and one
    # copy of each sat on no package surface, where no instrument read it. ⭐ A
    # spot assertion about those two would leave the NEXT name off the surface
    # just as invisible, so what is asserted is the whole population.
    taken = taken_from_a_module()
    source = repository_root() / "src"
    assert taken, (
        f"no package takes anything from a validate module, so this would pass vacuously; "
        f"walked {source} holding {len(list(source.rglob('*.py')))} module(s), cwd {Path.cwd()}"
    )
    exported = set(validate.__all__)
    on_surface = {name for _, _, name in taken if name in exported}
    assert on_surface, "nothing taken is on the surface; the comparison is answering False to all"
    off = {(module, name) for _, module, name in taken if name not in exported}
    print(f"names taken from a validate module: {len(taken)}, off this surface: {len(off)}")
    assert off == OFF_SURFACE, (
        f"a name left or joined this package's off-surface population: "
        f"new {sorted(off - OFF_SURFACE)}, gone {sorted(OFF_SURFACE - off)}"
    )
