"""Mirror of `tests/floor/personal_data/registry.py` (R12).

⛔ **Not one real identifier appears in this file**, and not one personal-data
shape is written as a literal. The shapes are assembled from fragments at run
time — the same trick `test_style.py` uses for trailing whitespace, and for the
same reason: a literal here would be a personal-data shape in a tracked file,
which is the thing under test.
"""

from __future__ import annotations

from tests.floor import config
from tests.floor.personal_data.registry import check_registry
from tests.floor.personal_data.shapes import check_shapes, shape_matches
from tests.support import repository_root

# ⛔ Assembled, never written down. Each of these is a personal-data shape, and
# each would be a finding against this very file if it appeared as a literal.
HOME_SHAPE = "/" + "home" + "/somebody/project"
MAC_SHAPE = "/" + "Users" + "/somebody/project"
ADDRESS = "a" + "somebody@" + "elsewhere.co.uk"
HOSTNAME = "some" + "box.loc" + "al"
TOKEN = "Bearer " + "abcdef0123456789"


def write(root, relative: str, text: str):
    """Write `text` at `relative` under `root`, creating parents."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --- the sanctioned directory, bounded in both directions ------------------


def test_the_registered_directory_is_the_only_one_exempt(tmp_path):
    sanctioned = config.SANCTIONED_PERSONAL_DATA_DIRS[0]
    write(tmp_path, f"{sanctioned}/VIOLATION.md", "# personal-data\n")
    write(tmp_path, f"{sanctioned}/lesson.json", HOME_SHAPE + " " + ADDRESS + "\n")
    write(tmp_path, "tests/fixtures/invalid/ordinal-gap/lesson.json", ADDRESS + "\n")
    reported = [finding.path for finding in check_shapes(tmp_path)]
    assert reported == ["tests/fixtures/invalid/ordinal-gap/lesson.json"]


def sanctioned_shapes() -> set[str]:
    """Every shape the real negative fixture actually carries."""
    root = repository_root()
    sanctioned = root / config.SANCTIONED_PERSONAL_DATA_DIRS[0]
    names = set()
    for path in sorted(sanctioned.rglob("*")):
        text = config.read_text(path) if path.is_file() else None
        if text:
            names.update(name for _line, name in shape_matches(text))
    return names


def test_the_real_sanctioned_directory_really_does_carry_the_shapes():
    # ⛔ The half that is easy to forget: if the
    # negative fixture were ever neutered into an input that this sweep
    # accepts, the exemption above would be protecting an empty box and
    # nobody would notice, because everything would stay green.
    assert "home path" in sanctioned_shapes()


def test_this_gate_and_the_archive_gate_disagree_about_the_fixture_s_address():
    # ⚠️ Not a defect — the two gates have different subjects, and this pins
    # the difference so a later edit cannot erase it by accident.
    #
    # The fixture's address is `…@example.invalid`: an RFC 2606 reserved TLD,
    # deliberately unreachable. **This** gate is repository hygiene, and an
    # address that can reach nobody identifies nobody, so it is allowed here —
    # authors are told to write such placeholders.
    # ⛔ **The archive gate's subject is the archive**, where any address is wrong content
    # whether or not it is deliverable, and `tests/test_fixture_consistency.py`
    # carries the stricter rule with no allow-list at all.
    #
    # So the fixture trips this sweep on its home path and not on its email,
    # and it must keep tripping the archive gate on both.
    assert "email address" not in sanctioned_shapes()


def test_the_registry_is_exactly_what_is_on_disk():
    # ⛔ A new negative fixture cannot appear without
    # appearing in a test. Any directory under `tests/fixtures/invalid/` whose
    # own content trips the sweep must be registered.
    root = repository_root()
    carriers = set()
    for path in sorted((root / "tests" / "fixtures").rglob("*")):
        if not path.is_file():
            continue
        text = config.read_text(path)
        if text and shape_matches(text):
            carriers.add(config.relative(path, root).rsplit("/", 1)[0])
    unregistered = sorted(
        directory for directory in carriers if not config.is_sanctioned_personal_data(directory)
    )
    assert unregistered == []


def test_the_registry_requires_a_violation_document(tmp_path):
    sanctioned = config.SANCTIONED_PERSONAL_DATA_DIRS[0]
    (tmp_path / sanctioned).mkdir(parents=True)
    findings = check_registry(tmp_path)
    assert [finding.rule for finding in findings] == ["personal-data-registry"]
    assert "VIOLATION.md" in findings[0].path


def test_a_registered_directory_that_has_vanished_is_a_finding(tmp_path):
    # The fixture area exists; the registered directory inside it does not.
    # ⛔ That is a live exemption pointing at nothing, which is the state where
    # a later directory of the same name inherits it silently.
    (tmp_path / config.SANCTIONED_PERSONAL_DATA_DIRS[0]).parent.mkdir(parents=True)
    findings = check_registry(tmp_path)
    assert [finding.rule for finding in findings] == ["personal-data-registry"]
    assert "not a directory" in findings[0].message


def test_the_real_registry_is_satisfied():
    assert check_registry(repository_root()) == []


def test_a_tree_without_the_fixture_area_is_not_judged(tmp_path):
    # ⚠️ The other four checks are properties of any tree; this one is a
    # property of this repository's fixture tree. A floor that reported "the
    # negative fixture is missing" against every temporary directory could not
    # be run on anything but the real root.
    assert check_registry(tmp_path) == []
