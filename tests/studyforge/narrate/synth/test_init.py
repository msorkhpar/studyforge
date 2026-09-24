"""The synthesis package's surface, and the two clauses it asserts about itself.

⛔ **Both source-shape tests run over EVERY module in the package**, not over the
one that happened to be split out. ⭐ Each has a positive control beside it: a
scanner that saw nothing, or a path that pointed at the wrong file, would pass
forever and prove the same nothing.
"""

import ast
import re
from pathlib import Path

from studyforge.corpus.placement.names import AUDIO_DIRNAME
from studyforge.corpus.placement.profile import GENERATED_ROOT
from studyforge.narrate import synth
from studyforge.version import CONTRACT_FIELDS

PACKAGE = Path(synth.__file__).parent
MODULES = sorted(PACKAGE.glob("*.py"))


def code_constants(path: Path) -> set[str]:
    """Every string constant a module's CODE holds, ⛔ its docstrings excluded."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    prose = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef))
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
    }
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in prose
    }


def test_the_package_has_the_three_modules_the_seam_names():
    assert [path.name for path in MODULES] == [
        "__init__.py",
        "incremental.py",
        "location.py",
        "record.py",
    ]


def test_everything_the_package_exports_is_reachable_by_that_name():
    for name in synth.__all__:
        assert hasattr(synth, name), name
    # ⚠️ Not `sorted()`: the tree's convention is ruff's, which groups
    # SCREAMING_CASE ahead of CamelCase ahead of lower_case, and
    # `corpus/placement/__init__.py` is the precedent. Asserted as a set.
    assert set(synth.__all__) == {name for name in dir(synth) if not name.startswith("_")} - {
        "incremental",
        "location",
        "record",
        "studyforge",
    }


def test_narration_api_is_registered_in_the_one_tuple():
    # ⛔ `CONTRACT_FIELDS`' own convention: a task that versions a new contract
    # registers it in the same commit, or `check` refuses the name outright.
    assert "narration_api" in CONTRACT_FIELDS
    # ⛔ Version 1 still reads, so an existing record is never refused for its age.
    assert synth.KNOWN_NARRATION_API == frozenset({1, synth.NARRATION_API})


def test_no_module_in_the_package_names_version_control_or_an_exclusion_file():
    # ⛔ The package's acceptance, asserted rather than reviewed. Whether media is
    # carried is a manifest policy and this package has no
    # opinion — so the words are absent from the prose as well as from the code.
    pattern = re.compile(r"(?i)\b(git|gitignore|ignore|ignored|ignoring|exclude)\b")
    offenders = {path.name: pattern.findall(path.read_text(encoding="utf-8")) for path in MODULES}
    assert {name: hits for name, hits in offenders.items() if hits} == {}


def test_that_scan_reads_the_package_and_would_see_the_word():
    # ⭐ The positive control: the population is non-empty and the pattern fires.
    assert len(MODULES) == 4
    assert re.search(r"(?i)\bignore\b", "an ignore file")


def test_no_module_spells_a_media_directory_or_the_generated_root_of_its_own():
    # ⛔ R4: `into` is an argument, and the only spellings of those two names are
    # the constants the placement package exports.
    # ⚠️ **Syntactic, and deliberately so** — the same argument
    # `tests/studyforge/test_version.py` makes about its own scanner: a docstring
    # explaining why a caller must not compose a name is not a breach of it.
    spelled = {name: code_constants(path) for name, path in ((p.name, p) for p in MODULES)}
    for name, constants in spelled.items():
        assert constants & {AUDIO_DIRNAME, GENERATED_ROOT} == set(), name


def test_the_scanner_that_says_so_can_see_a_string_at_all():
    # ⭐ The positive control for the test above.
    assert synth.NARRATION_STATE_FILENAME in code_constants(PACKAGE / "record.py")
    assert synth.CLIP_ABSENT in code_constants(PACKAGE / "incremental.py")


def test_the_record_half_does_not_import_the_pass_half():
    # ⛔ The seam runs one way. A report or a coverage tracker must be able to
    # read the contract without dragging a client in.
    source = (PACKAGE / "record.py").read_text(encoding="utf-8")
    assert "incremental" not in source
    assert "from studyforge.narrate.synth.record import" in (PACKAGE / "incremental.py").read_text(
        encoding="utf-8"
    )
