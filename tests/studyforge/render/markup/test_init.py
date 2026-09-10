"""Mirror of `src/studyforge/render/markup/__init__.py` (R12).

⭐ **What this module holds that `test_text.py` cannot.** `test_text.py` asks
whether the functions are right; this asks whether there is exactly **one** of
each of them in the framework and whether a consumer can reach them without
naming a submodule — which is `W76`'s whole subject and `SF-27/1`'s finding.
"""

from __future__ import annotations

import ast
from types import ModuleType

from studyforge.render import markup
from studyforge.render.markup import text
from tests.support import assert_package_contract, repository_root

#: Where the sweep below looks. ⛔ `src/` only: a mirror test's subject **is**
#: the module it mirrors (R12), so `tests/` is the one tree where naming a
#: submodule is correct rather than a defect.
SOURCE_ROOT = repository_root() / "src" / "studyforge"

#: The names that must have exactly one definition in the whole framework. ⚠️ A
#: second `escape` agrees with the first on the day it is written and disagrees
#: the day one of them learns about `'`; the page still renders and still
#: carries every word, and the difference is an injection.
ONE_OF_EACH = ("escape", "escape_attribute", "inline", "safe_href", "segments")

#: Where each of those is allowed to be defined, as a path relative to
#: `SOURCE_ROOT`. ⛔ One entry, and that is the claim.
MAY_DEFINE = ("render/markup/text.py",)


def modules_defining(names: tuple[str, ...], root=None) -> list[str]:
    """Every module under `root` that defines a top-level function in `names`.

    ⛔ Top-level `def` only, and by AST rather than by grep: a comment or a
    docstring that mentions `def escape` is not a second definition, and a
    sweep that cannot tell them apart is a sweep that reports a defect the
    first time somebody documents one.
    """
    base = SOURCE_ROOT if root is None else root
    found: list[str] = []
    for path in sorted(base.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        defined = {
            node.name
            for node in tree.body
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        }
        if defined & set(names):
            found.append(path.relative_to(base).as_posix())
    # ⚠️ Sorted by the path STRING, never by the walk: `rglob` sorts
    # `render/index/` before `render/markup/`, so a reading compared against a
    # hand-written order passes or fails on the planted module's name.
    return sorted(found)


def test_the_package_states_its_contract():
    assert_package_contract(markup, "studyforge.render.markup")


def test_the_public_surface_is_exactly_the_module_s_public_names():
    # ⭐ Derived on both sides rather than typed on one: a name added to `text`
    # and forgotten on `__all__` fails here instead of being discovered by the
    # next renderer, which is `SF-27/1` arriving a second time.
    # ⚠️ Imported modules and `from __future__` flags are what a module's
    # namespace carries besides its own names; neither is a surface.
    public = {
        name
        for name, value in vars(text).items()
        if not name.startswith("_") and not isinstance(value, ModuleType) and name != "annotations"
    }
    assert public, "the sweep found no public name at all in text.py"
    assert set(markup.__all__) == public, sorted(set(markup.__all__) ^ public)


def test_every_exported_name_is_the_module_s_own_object():
    # ⛔ Identity, not spelling. A re-export that had been re-bound somewhere on
    # the way would compare equal by name and be a different function.
    for name in markup.__all__:
        assert getattr(markup, name) is getattr(text, name), name


def test_the_framework_defines_each_primitive_exactly_once():
    # ⛔ `SF-27/1`'s second measurement, now asserted rather than reported:
    # "there is no other home … a second escaper would be Ruling 20's deleted
    # duplicate, arriving again."
    defining = modules_defining(ONE_OF_EACH)
    # ⭐ The inhabitation assertion, before the claim (Ruling 132): a sweep that
    # found nothing at all would pass the line below just as loudly.
    assert defining, f"the sweep found no module at all under {SOURCE_ROOT.name}"
    assert defining == list(MAY_DEFINE), defining


def test_the_sweep_above_would_notice(tmp_path):
    # ⛔ Ruling 123, all three readings. Reading 1 is the test above, live.
    for name in MAY_DEFINE:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text("def escape(value):\n    return value\n", "utf-8")

    # ⭐ Reading 2, planted: a second escaper, in the spelling somebody would
    # actually write — a private helper on a renderer that "just needed one".
    (tmp_path / "render" / "index").mkdir(parents=True)
    (tmp_path / "render" / "index" / "listing.py").write_text(
        "def escape(value):\n    return value.replace('<', '&lt;')\n", encoding="utf-8"
    )
    assert modules_defining(ONE_OF_EACH, tmp_path) == sorted(
        [*MAY_DEFINE, "render/index/listing.py"]
    )

    # ⚠️ And the shape that must NOT read as a second definition: a module that
    # only *talks* about one. ⛔ Without this the sweep is a grep with an AST
    # tax, and the first documented primitive turns the branch red.
    (tmp_path / "render" / "index" / "listing.py").write_text(
        '"""How not to write your own def escape(value)."""\n# def safe_href(x): ...\n',
        encoding="utf-8",
    )
    assert modules_defining(ONE_OF_EACH, tmp_path) == list(MAY_DEFINE)

    # ⭐ Reading 3, the impossible subject: a tree where nothing defines any of
    # them must read differently from both of the above.
    empty = tmp_path / "elsewhere"
    empty.mkdir()
    (empty / "quiet.py").write_text("VALUE = 'escape'\n", encoding="utf-8")
    assert modules_defining(ONE_OF_EACH, empty) == []
