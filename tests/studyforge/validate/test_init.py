"""Mirror of `src/studyforge/validate/__init__.py` (R12)."""

from __future__ import annotations

import ast
from pathlib import Path

from studyforge import validate
from tests.support import assert_package_contract, repository_root

#: This package, as an importer spells it.
PACKAGE = "studyforge.validate"

#: ⛔ **Names another package takes out of a `validate` MODULE that are NOT on
#: `studyforge.validate.__all__`** — Ruling 101's producer half, unmet, DECLARED so
#: that the next one reds instead of joining them invisibly (`W199`).
#:
#: ⚠️ **Declared is not exempt.** Each is a `W199` finding, and none is `W199`'s own
#: subject: the two names that were — the `archive` root and the `raw/` segment — are
#: minted once now, in `corpus.placement`, and reach this package as imports.
#: ⛔ **Why they are not fixed here:** each is another package's vocabulary
#: (`cli.plan`, `cli.site`, `skills.reconnaissance`), and `headings` collides with
#: the module `validate.headings`, so exporting it needs a ruling rather than a line.
OFF_SURFACE = {
    ("studyforge.validate.corpus", "Held"),
    ("studyforge.validate.corpus", "Walk"),
    ("studyforge.validate.headings", "headings"),
    ("studyforge.validate.paths", "RULE_DUPLICATE_PATH"),
    ("studyforge.validate.paths", "check_placement"),
}


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
