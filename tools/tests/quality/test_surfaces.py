"""Mirror of `tools/quality/surfaces.py` (R12).

⭐ **Every positive here is paired with the legitimate shape it is one character from.**
A check that fired on a sub-package importing its own parent, or on a module imported
from the package that holds it, would be switched off within a day — and then Ruling
101's producer half would be enforced by nobody, which is the state `W199/3` found.
"""

from __future__ import annotations

from pathlib import Path

from tests.support import repository_root
from tools.quality.surfaces import (
    DECLARED,
    RULE_DECLARATION,
    RULE_REACHED_PAST,
    RULE_UNDECLARED,
    Declaration,
    check_producer_half,
    packages,
    reaches,
    surface_census,
)

#: The contract line every synthetic module carries, so the floor's own rules are met.
DOC = '"""Module."""\n\n'


def _write(root: Path, relative: str, text: str) -> Path:
    """Write `text` at `relative` under `root`, creating the directories it needs."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _tree(root: Path, *, owner_all: str, importer: str) -> Path:
    """Build a two-package synthetic tree: an owner declaring `owner_all`, and a taker."""
    _write(root, "src/studyforge/__init__.py", DOC)
    _write(root, "src/studyforge/owner/__init__.py", DOC + f"__all__ = {owner_all}\n")
    _write(root, "src/studyforge/owner/thing.py", DOC + "VALUE = 1\n")
    _write(root, "src/studyforge/taker/__init__.py", DOC + "__all__ = []\n")
    _write(root, "src/studyforge/taker/reads.py", DOC + f"{importer}\n")
    return root


# --- the real tree: closed BOTH ways, and not clean by reading nothing ----------------


def test_this_trees_deviations_are_exactly_what_is_declared():
    # ⛔ Closed at this ref, and the assertion is one line because both arms are in it:
    # an UNDECLARED deviation reds, and a DECLARED one that is GONE reds too.
    findings = check_producer_half(repository_root())
    assert findings == [], "\n".join(str(finding) for finding in findings)


def test_and_the_walk_that_says_so_read_a_real_population():
    # ⛔ **Ruling 48, and Ruling 191 one level up.** The assertion above is an empty
    # list, which is also what a walk that read nothing returns. This pins the
    # population the clean bill was taken over, so "clean" cannot mean "never ran".
    found = reaches(repository_root())
    assert found, "no package takes anything from another package; the check is vacuous"
    assert [reach for reach in found if not reach.module], "the pin arm binds nothing"
    assert [reach for reach in found if reach.module], "the sweep arm sees nothing"
    assert {reach.owner for reach in found} > {"studyforge.validate"}


def test_every_declared_package_is_a_package_this_tree_actually_has():
    # ⚠️ A declaration naming a package that does not exist excuses nothing and would
    # never be read, so it could sit here forever saying something false.
    known = packages(repository_root())
    assert set(DECLARED) <= set(known)
    assert DECLARED, "an empty declaration satisfies every comparison below vacuously"


def test_the_pin_holds_a_name_whichever_spelling_a_consumer_uses():
    # ⭐ `W299/1`: the property that makes a later spelling fix safe. `Held` is on
    # `studyforge.validate.__all__` and is taken by the MODULE spelling today; were that
    # corrected to the package spelling, this arm would still require it on the surface.
    surface = packages(repository_root())["studyforge.validate"]
    assert surface is not None and "Held" in surface


def test_every_package_is_read_and_a_missing_surface_is_not_an_empty_one():
    read = packages(repository_root())
    assert read["studyforge.validate"] is not None
    # ⚠️ `None` is *declares no `__all__`*, and it is a different answer from an empty
    # surface. Collapsing the two would make a package with no surface unreportable.
    assert any(surface is None for surface in read.values())


# --- the PIN arm, both ways ----------------------------------------------------------


def test_a_name_taken_from_a_package_that_does_not_export_it_is_a_finding(tmp_path):
    _tree(tmp_path, owner_all="[]", importer="from studyforge.owner import VALUE")
    findings = check_producer_half(tmp_path)
    assert [finding.rule for finding in findings] == [RULE_UNDECLARED]
    assert "VALUE" in findings[0].message and "studyforge.owner" in findings[0].message
    assert findings[0].path == "src/studyforge/taker/reads.py"
    assert findings[0].line == 3


def test_and_the_same_name_on_the_owners_surface_is_not(tmp_path):
    _tree(tmp_path, owner_all='["VALUE"]', importer="from studyforge.owner import VALUE")
    assert check_producer_half(tmp_path) == []


def test_a_package_declaring_no_surface_at_all_is_reached_past(tmp_path):
    # ⛔ The packages of this tree with no `__all__` are the sharpest case: every name
    # they share is off-surface by construction, and `None` must not read as clean.
    _write(tmp_path, "src/studyforge/__init__.py", DOC)
    _write(tmp_path, "src/studyforge/owner/__init__.py", DOC)
    _write(tmp_path, "src/studyforge/owner/thing.py", DOC + "VALUE = 1\n")
    _write(tmp_path, "src/studyforge/taker/__init__.py", DOC + "__all__ = []\n")
    _write(
        tmp_path,
        "src/studyforge/taker/reads.py",
        DOC + "from studyforge.owner import VALUE\n",
    )
    assert [f.rule for f in check_producer_half(tmp_path)] == [RULE_UNDECLARED]


# --- the SWEEP arm, and the declaration that closes it, both ways ---------------------


def test_an_UNDECLARED_module_spelled_deviation_is_a_finding(tmp_path):
    _tree(tmp_path, owner_all="[]", importer="from studyforge.owner.thing import VALUE")
    findings = check_producer_half(tmp_path)
    assert [finding.rule for finding in findings] == [RULE_REACHED_PAST]
    assert "studyforge.owner.thing" in findings[0].message
    assert "declaring a defect" in findings[0].message


def test_and_a_DECLARED_one_is_not(tmp_path, monkeypatch):
    _tree(tmp_path, owner_all="[]", importer="from studyforge.owner.thing import VALUE")
    monkeypatch.setitem(
        DECLARED, "studyforge.owner", Declaration("a ground", frozenset({"VALUE"}))
    )
    assert check_producer_half(tmp_path) == []


def test_a_DECLARED_deviation_that_is_GONE_reds_rather_than_lingering(tmp_path, monkeypatch):
    # ⛔ What CLOSES the population at its ref: fixing a deviation deletes its own entry,
    # so a declaration can never outlive the thing it excuses.
    _tree(tmp_path, owner_all="[]", importer="pass")
    monkeypatch.setitem(
        DECLARED, "studyforge.owner", Declaration("a ground", frozenset({"DEPARTED"}))
    )
    findings = check_producer_half(tmp_path)
    assert [finding.rule for finding in findings] == [RULE_DECLARATION]
    assert findings[0].path == "src/studyforge/owner/__init__.py"
    assert "DEPARTED" in findings[0].message and "Delete the entry" in findings[0].message


def test_a_declaration_for_a_package_this_tree_lacks_is_not_read(tmp_path):
    # ⚠️ Declared gap 6. Every synthetic tree above would carry this repository's whole
    # declared population as stale findings if the arm did not skip an absent package.
    _tree(tmp_path, owner_all="[]", importer="pass")
    assert "studyforge.archive" in DECLARED
    assert check_producer_half(tmp_path) == []


def test_the_SPELLING_deviation_is_counted_and_never_failed():
    # ⭐ Ruling 101's FIRST row on the real tree: `Held` IS exported by `validate` and is
    # taken by the submodule spelling (`W299/3`). It is printed, and it is not a finding.
    printed = "\n".join(surface_census(repository_root()))
    assert "Held" in printed
    assert not [f for f in check_producer_half(repository_root()) if "Held" in f.message]


# --- the census ----------------------------------------------------------------------


def test_the_census_carries_its_denominators_and_says_what_it_is_not():
    lines = surface_census(repository_root())
    assert lines[0].startswith("producer half (W199/3):")
    assert "cross-package import(s) read" in lines[0]
    # ⚠️ `W298/3`: an instrument that reads a NAME must not be mistaken for a value guard.
    assert "never a VALUE" in lines[0]
    printed = "\n".join(lines)
    for owner in DECLARED:
        assert owner in printed


def test_the_census_says_so_on_a_tree_that_is_not_this_framework(tmp_path):
    lines = surface_census(tmp_path)
    assert len(lines) == 1 and "no src/studyforge" in lines[0]
    assert "not a failure" in lines[0]


# --- the shapes it must NOT fire on --------------------------------------------------


def test_importing_a_MODULE_from_its_own_package_is_not_a_surface_name(tmp_path):
    # ⭐ `from studyforge.serve.routes import assets` is an import of a module, not a
    # reach past a surface. Measured at `2827409`, this tree writes that form.
    _tree(tmp_path, owner_all="[]", importer="from studyforge.owner import thing")
    assert check_producer_half(tmp_path) == []


def test_a_SUB_PACKAGE_is_its_own_owner(tmp_path):
    # ⛔ `validate.source` states its own `__all__`, so importing from it reaches past
    # nothing — the rule `W199` set, applied by structure rather than by name.
    _write(tmp_path, "src/studyforge/__init__.py", DOC)
    _write(tmp_path, "src/studyforge/owner/__init__.py", DOC + "__all__ = []\n")
    _write(
        tmp_path,
        "src/studyforge/owner/inner/__init__.py",
        DOC + '__all__ = ["VALUE"]\n\nVALUE = 1\n',
    )
    _write(tmp_path, "src/studyforge/taker/__init__.py", DOC + "__all__ = []\n")
    _write(
        tmp_path,
        "src/studyforge/taker/reads.py",
        DOC + "from studyforge.owner.inner import VALUE\n",
    )
    assert check_producer_half(tmp_path) == []


def test_a_package_reading_its_OWN_surface_is_not_reaching_past_one(tmp_path):
    _tree(tmp_path, owner_all="[]", importer="pass")
    _write(
        tmp_path,
        "src/studyforge/owner/near.py",
        DOC + "from studyforge.owner import VALUE\n",
    )
    assert check_producer_half(tmp_path) == []


def test_a_module_reading_its_OWN_packages_module_is_not_reaching_past_one(tmp_path):
    _tree(tmp_path, owner_all="[]", importer="pass")
    _write(
        tmp_path,
        "src/studyforge/owner/near.py",
        DOC + "from studyforge.owner.thing import VALUE\n",
    )
    assert check_producer_half(tmp_path) == []


def test_a_RELATIVE_import_is_not_read(tmp_path):
    _tree(tmp_path, owner_all="[]", importer="pass")
    _write(tmp_path, "src/studyforge/taker/near.py", DOC + "from . import reads\n")
    assert check_producer_half(tmp_path) == []


def test_the_PLAIN_import_form_is_declared_and_is_asserted_SILENT(tmp_path):
    # ⚠️ Declared gap 1 of the contract, asserted rather than described: `import a.b`
    # binds a module and this reads no attribute expression. Measured at `2827409`,
    # nothing under `src/studyforge` writes it — so the gap costs this tree nothing.
    _tree(tmp_path, owner_all="[]", importer="import studyforge.owner.thing")
    assert check_producer_half(tmp_path) == []


def test_a_tree_that_is_not_this_framework_is_passed_and_not_failed(tmp_path):
    # ⛔ Declared gap 5: the floor runs over a corpus and an installed tree. An empty
    # population passes HERE and is refused in the mirror, above, where the real tree is.
    assert check_producer_half(tmp_path) == []
    assert reaches(tmp_path) == []
    assert packages(tmp_path) == {}


def test_a_module_that_does_not_parse_is_skipped_rather_than_crashing(tmp_path):
    _tree(tmp_path, owner_all="[]", importer="from studyforge.owner import VALUE")
    _write(tmp_path, "src/studyforge/taker/broken.py", DOC + "def (\n")
    assert [f.rule for f in check_producer_half(tmp_path)] == [RULE_UNDECLARED]
