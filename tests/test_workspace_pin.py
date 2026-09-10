"""The pin file as a repository-level fact (FND-05a).

⭐ **Separate from `tools/tests/workspace/`, which tests the tool.** These are
claims about *this* repository's own tracked files: that the pin file is on
contract, that it says which components are owed, and — the one that matters —
that it carries no path at all.

## ⛔ The register is the file, and nothing here restates it

⚠️ **This module used to hold a `COMPONENTS` tuple**, which was Ruling 20's
shape exactly: a second, weaker copy of a list that already existed, in a file
nobody would think to update. ⭐ Ruling 54 replaced it — `status` makes *"this
component is owed and does not exist yet"* sayable in the register itself, so
E12 and E13 **flip a status** rather than remembering a second file.
"""

from __future__ import annotations

import json

from tests.support import repository_root
from tools.workspace import COMPONENT_KEYS, PIN_FILENAME, PIN_KEYS, STATUS, WHERE, read


def components():
    """Every component this repository records, read through the contract."""
    return read(repository_root())


def test_the_pin_file_is_on_contract():
    # ⭐ Derived, not restated: `read` refuses every way a row can be wrong, so
    # this asserts the whole vocabulary at once rather than a copy of it.
    found = components()
    assert found, f"{PIN_FILENAME} records no components at all"
    assert {c.where for c in found} <= set(WHERE)
    assert {c.status for c in found} <= set(STATUS)


def test_this_repository_is_the_one_self_row():
    # ⭐ The acceptance says "every component, `studyforge` included".
    selves = [c for c in components() if c.where == "self"]
    assert [c.name for c in selves] == ["studyforge"]
    assert selves[0].present


def test_a_commit_is_recorded_exactly_when_the_component_exists():
    # ⛔ Ruling 54, in both directions: a `present` row with no commit pins
    # nothing, and a `not-yet-created` row with one claims a commit in a
    # repository that does not exist.
    for component in components():
        assert (component.commit is not None) == component.present, component.name


def test_the_components_still_to_be_created_are_recorded_as_such():
    # ⚠️ Not a list of names — that was the second copy. This asserts only that
    # the register *can* and *does* say a component is owed, which is what
    # E12 and E13 flip.
    owed = [c.name for c in components() if not c.present]
    assert owed, "no component is recorded as owed; if that is right, say so in the review"


def test_the_pin_file_carries_no_path_of_any_kind():
    # ⛔ **The R7 trap this task exists to walk past.** A pin file's natural
    # content is "where each component lives", and on this machine that is a
    # home directory. ⭐ Asserted on the bytes, so it cannot be argued about:
    # a `sibling` resolves at run time and the file says only a name.
    text = (repository_root() / PIN_FILENAME).read_text(encoding="utf-8")
    for forbidden in ("/", "\\", "..", "~", "home", "Users", "://"):
        assert forbidden not in text, f"{PIN_FILENAME} contains {forbidden!r}"


def test_the_pin_file_is_in_key_order():
    document = json.loads((repository_root() / PIN_FILENAME).read_text(encoding="utf-8"))
    assert tuple(document) == PIN_KEYS
    for row in document["components"]:
        assert tuple(row) == COMPONENT_KEYS[: len(row)]


def test_no_gitmodules_anywhere_in_the_repository():
    # ⛔ Not "we chose not to use submodules" — asserted, because the failure
    # is silent: a `.gitmodules` naming an unpushed commit resolves to nothing
    # **including here**, and nothing says so at clone time because nobody
    # clones this.
    found = [
        path.relative_to(repository_root()).as_posix()
        for path in repository_root().rglob(".gitmodules")
    ]
    assert found == []
