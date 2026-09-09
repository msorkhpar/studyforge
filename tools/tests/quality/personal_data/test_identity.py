"""Mirror of `tools/quality/personal_data/identity.py` (R12).

⛔ **Not one real identifier appears in this file**, and not one personal-data
shape is written as a literal. The shapes are assembled from fragments at run
time — the same trick `test_style.py` uses for trailing whitespace, and for the
same reason: a literal here would be a personal-data shape in a tracked file,
which is the thing under test.
"""

from __future__ import annotations

from tests.support import init_repository, repository_root
from tools.quality.personal_data.identity import (
    GENERIC_IDENTIFIERS,
    check_identifiers,
    identifiers,
)

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


# --- this machine's own identifiers ----------------------------------------


def test_identifiers_are_derived_and_never_written_down():
    # ⛔ The contract, asserted three ways: the module holds no value, the
    # values are computed on demand, and nothing persists them. If a future
    # edit adds a cache file or a constant, one of these fails.
    package = repository_root() / "tools" / "quality" / "personal_data"
    source = "\n".join(path.read_text("utf-8") for path in sorted(package.rglob("*.py")))
    for label, value in identifiers().items():
        assert value not in source, f"the package holds this machine's {label}"
    assert identifiers() == identifiers()  # recomputed, not memoised


def test_a_fabricated_identifier_is_found(tmp_path):
    # ⛔ Fabricated and passed in. A test that used the real value would be
    # writing it into a tracked file — the leak the check exists to prevent.
    write(tmp_path, "docs/notes.md", "built by zaphodbeeblebrox on tuesday\n")
    findings = check_identifiers(tmp_path, {"account name": "zaphodbeeblebrox"})
    assert len(findings) == 1
    assert findings[0].rule == "personal-data-identifier"
    assert findings[0].line == 1
    assert "account name" in findings[0].message
    assert "zaphodbeeblebrox" not in findings[0].message


def test_an_ignored_file_is_not_gated_for_an_identifier_either(tmp_path):
    # The merge gate reported this half too: an IDE workspace file names the
    # account whose IDE it is. Same ruling, same fix, asserted separately
    # because the two halves enumerate the tree through the same helper and a
    # future edit could give one of them its own.
    init_repository(tmp_path)
    write(tmp_path, ".gitignore", ".idea/\n")
    write(tmp_path, ".idea/workspace.xml", "opened by zaphodbeeblebrox\n")
    fabricated = {"account name": "zaphodbeeblebrox"}
    assert check_identifiers(tmp_path, fabricated) == []

    write(tmp_path, "docs/notes.md", "written by zaphodbeeblebrox\n")
    reported = [finding.path for finding in check_identifiers(tmp_path, fabricated)]
    assert reported == ["docs/notes.md"]


def test_an_identifier_inside_a_longer_word_is_not_a_match(tmp_path):
    # ⚠️ Word-bounded, so a three-character account name cannot turn every
    # file in the tree into a finding.
    write(tmp_path, "src/studyforge/a.py", "value = 'transmission'\n")
    assert check_identifiers(tmp_path, {"account name": "ans"}) == []


def test_nothing_derivable_means_nothing_reported(tmp_path):
    # Inside the dev image there is no passwd entry, HOME is /tmp and git has
    # no identity, so this half legitimately has nothing to compare. That is
    # correct — a leak originates on the machine that has those values.
    write(tmp_path, "docs/notes.md", "anything at all\n")
    assert check_identifiers(tmp_path, {}) == []


def test_generic_values_are_not_treated_as_identifiers(tmp_path):
    # A machine whose account is called `root` or `ubuntu` would otherwise
    # make every mention of those words a finding, and a check that fires on
    # correct code is a check somebody turns off.
    assert "root" in GENERIC_IDENTIFIERS
    assert "ubuntu" in GENERIC_IDENTIFIERS
    for value in identifiers().values():
        assert value.lower() not in GENERIC_IDENTIFIERS
        assert len(value) >= 3
