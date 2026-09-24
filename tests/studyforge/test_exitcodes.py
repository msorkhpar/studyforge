"""Mirror of `src/studyforge/exitcodes.py` (R12).

⛔ **`W320`: the shared exit code belongs to no stage.** Two halves, and the
second is the one the row exists for — the value is unchanged and every old
spelling still resolves to the same object, AND importing this module brings no
other `studyforge` module with it. ⭐ The second is measured in a FRESH
interpreter, never read off the source text, which cannot see an import
(`SF-38/9`); the instrument's inhabitation is a module that DOES pull others.
"""

from __future__ import annotations

import ast
import json
import sys

from studyforge import exitcodes
from studyforge.exitcodes import UNUSABLE
from studyforge.validate.report import INVALID, OK
from tests.harness import isolation
from tests.support import repository_root, run

#: Import one module in a clean interpreter and print every OTHER `studyforge`
#: module the interpreter then holds. ⚠️ The package itself is excluded: a
#: submodule cannot be imported without it, so it is not a dependency anyone
#: chose.
CHILD = """
import importlib, json, sys
sys.path.insert(0, sys.argv[1])
importlib.import_module(sys.argv[2])
held = sorted(
    name
    for name in sys.modules
    if name.startswith("studyforge") and name not in ("studyforge", sys.argv[2])
)
print(json.dumps(held))
"""


def loaded_by(importer: str) -> list[str]:
    """Every other `studyforge` module a fresh interpreter holds after `importer`."""
    root = repository_root()
    result = run([sys.executable, "-c", CHILD, str(root / "src"), importer], root)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_the_shared_code_is_the_value_it_has_always_had():
    # ⛔ `W320` moves a definition; it renumbers nothing. A script that greps
    # for `2` today must keep getting `2`.
    assert UNUSABLE == 2


def test_the_three_exit_codes_still_mean_three_different_things():
    # ⛔ The reason the split is `2` alone: `0` and `1` are verdicts about an
    # archive and stay with `validate.report`. All three must stay distinct.
    assert len({OK, INVALID, UNUSABLE}) == 3


def test_every_old_spelling_still_reaches_the_shared_code():
    # ⛔ No consumer moves: the two spellings that existed before `W320` and the
    # dispatcher's own binding must all still answer.
    import studyforge.validate as validate_package
    from studyforge.cli import dispatch
    from studyforge.validate.cli import UNUSABLE as from_the_verb

    assert from_the_verb == UNUSABLE
    assert validate_package.UNUSABLE == UNUSABLE
    assert dispatch.UNUSABLE == UNUSABLE
    assert "UNUSABLE" in validate_package.__all__


def test_exactly_one_framework_module_defines_the_shared_exit_code():
    # ⛔ "One definition, imported by both" is a property of the TREE and not of
    # one module, so it is quantified over the whole of `src/`: a second
    # `UNUSABLE = …` anywhere names its own file here.
    #
    # ⚠️ **`is` was written above first, and the plant refuted it.** Copying
    # `UNUSABLE = 2` back into `validate/cli.py` passes an identity check,
    # because CPython caches small integers and both names then point at the
    # same `2`. ⭐ An identity assertion cannot see a second definition of a
    # small int at all; reading the tree can.
    defining = sorted(
        module.name for module in isolation.framework_modules() if _assigns(module.tree, "UNUSABLE")
    )
    print(defining)
    assert defining == ["src/studyforge/exitcodes.py"]


def _assigns(tree: ast.Module, name: str) -> bool:
    """Whether `tree` binds `name` by assignment anywhere in it."""
    for node in ast.walk(tree):
        targets = getattr(node, "targets", None) or ([node.target] if _is_annotated(node) else [])
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            return True
    return False


def _is_annotated(node: ast.AST) -> bool:
    """Whether `node` is an annotated assignment, which carries one target."""
    return isinstance(node, ast.AnnAssign)


def test_importing_the_shared_module_brings_no_other_framework_module():
    # ⛔ The property the dispatcher rests on: this module is importable without
    # loading a stage, so importing the command loads no verb.
    held = loaded_by("studyforge.exitcodes")
    print(held)
    assert held == [], f"the shared exit code dragged {held} in with it"


def test_that_instrument_reports_what_a_module_with_dependencies_pulls_in():
    # ⭐ Inhabitation: a child that imported nothing also reports
    # an empty list, so the pass reading above is only attributable once the
    # same instrument is seen to report something. `validate.cli` is the module
    # `UNUSABLE` used to live in, and it pulls its own package's modules.
    held = loaded_by("studyforge.validate.cli")
    print(held)
    assert "studyforge.exitcodes" in held
    assert [name for name in held if name.startswith("studyforge.validate.")] != []


def test_the_module_states_no_dependency_because_it_has_none():
    # ⛔ The contract is checkable, not decorative (R17): the "Depends on"
    # sentence says "Nothing", and the assertion above is what makes it true.
    assert "**Depends on.** Nothing" in exitcodes.__doc__
