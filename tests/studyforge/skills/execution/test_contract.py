"""Mirror of `src/studyforge/skills/execution/contract.py` (R12).

⛔ Both directions for every claim: a contract this reader accepts and, planted
beside it, one it must refuse. ⭐ The readings taken against the **real**
sibling are separated and skip where no sibling is resolvable — the pinned
image mounts one directory, so a test that needed one could not run in the gate
that votes.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.skills.buildserve import narration
from studyforge.skills.execution import contract
from tests.studyforge.skills.execution.contracts import (
    CONTAINER_USER,
    HOME,
    editor_text,
)
from tests.support import repository_root
from tools.workspace import read as read_workspace
from tools.workspace.__main__ import DEV_CONTAINER, workspace_root

#: An account name this contract never declares as its own. ⚠️ Composed rather
#: than written, for the reason `contracts.py` states.
STRANGER = f"/home/{'somebodyelse'}/repo"


def loaded(**moved: object):
    """The synthetic contract, read the way this skill reads a real one."""
    return contract.read(
        editor_text(**moved),
        component=contract.EDITOR_COMPONENT,
        api=contract.EDITOR_API,
        promise=contract.EDITOR_PROMISE,
    )


def declared() -> dict | None:
    """The real component's `consuming.json`, or `None` where none is readable."""
    if os.environ.get(DEV_CONTAINER):
        return None
    root = repository_root()
    for component in read_workspace(root):
        if component.name == contract.EDITOR_COMPONENT:
            where = component.directory(workspace_root(root), root) / contract.CONSUMING
            return json.loads(where.read_text(encoding="utf-8")) if where.is_file() else None
    return None


# --------------------------------------------------------------------------
# R9 — recorded, refused, never migrated
# --------------------------------------------------------------------------


def test_a_contract_at_the_recorded_shape_and_promise_is_read():
    assert loaded()["component"] == contract.EDITOR_COMPONENT


def test_a_promise_below_the_recorded_one_is_refused_and_a_higher_one_is_read():
    # ⭐ Both directions of the asymmetry, which is the whole of the decision:
    # new keys move `provides` and leave what is there alone, so refusing a
    # newer component would make every release break every consumer.
    with pytest.raises(contract.ContractRefused, match="Nothing is migrated"):
        loaded(provides=contract.EDITOR_PROMISE - 1)
    assert loaded(provides=contract.EDITOR_PROMISE + 7)["provides"] > contract.EDITOR_PROMISE


def test_a_shape_this_reader_has_not_read_is_refused_in_either_direction():
    # ⛔ `consuming_api` versions the SHAPE of what is already there, and a
    # shape nobody has read is not a shape to guess at.
    for moved in (contract.EDITOR_API + 1, contract.EDITOR_API + 9):
        with pytest.raises(contract.ContractRefused, match="Nothing is migrated"):
            loaded(consuming_api=moved)


def test_a_version_that_is_not_a_whole_number_is_refused_without_quoting_it():
    with pytest.raises(contract.ContractRefused) as refused:
        loaded(provides="/two")
    assert "/two" not in str(refused.value)
    assert "whole number" in str(refused.value)


def test_a_boolean_is_not_read_as_a_version():
    # ⚠️ `True == 1` in Python, so a contract carrying `provides: true` would
    # pass a naive comparison at promise 1 and mean nothing.
    with pytest.raises(contract.ContractRefused, match="whole number"):
        loaded(provides=True)


def test_another_components_contract_is_refused_by_name():
    with pytest.raises(contract.ContractRefused, match="wrong sibling"):
        loaded(component="some-other-component")


def test_text_that_is_not_a_json_object_is_refused():
    for text in ("not json at all", "[1, 2]", "7"):
        with pytest.raises(contract.ContractRefused):
            contract.read(
                text,
                component=contract.EDITOR_COMPONENT,
                api=contract.EDITOR_API,
                promise=contract.EDITOR_PROMISE,
            )


# --------------------------------------------------------------------------
# R7 — the gate, and the one account name a contract may carry
# --------------------------------------------------------------------------


def test_the_container_home_the_contract_declares_passes_the_gate():
    # ⭐ The positive half. A component legitimately states the paths inside its
    # own image, and they hang off the home of the account it declares.
    document = loaded()
    assert contract.container_users(document) == (CONTAINER_USER,)
    assert HOME in json.dumps(document)


def test_a_home_path_the_contract_never_declared_is_still_refused():
    # ⛔ The half that makes the mask narrow rather than an off switch: an
    # account name this contract does not declare as its own is a leak.
    moved = json.loads(editor_text())
    moved["editor"]["workspace"]["container_path"] = STRANGER
    with pytest.raises(PersonalDataLeak):
        contract.read(
            json.dumps(moved),
            component=contract.EDITOR_COMPONENT,
            api=contract.EDITOR_API,
            promise=contract.EDITOR_PROMISE,
        )


def test_a_contract_that_declares_no_user_masks_nothing():
    moved = json.loads(editor_text())
    del moved["editor"]["runs_as"]["user"]
    with pytest.raises(PersonalDataLeak):
        contract.read(
            json.dumps(moved),
            component=contract.EDITOR_COMPONENT,
            api=contract.EDITOR_API,
            promise=contract.EDITOR_PROMISE,
        )


def test_the_mask_does_not_change_what_a_renderer_reads():
    # ⚠️ The masking is over a COPY. A renderer that got the placeholder back
    # would emit a compose file mounting a path that does not exist.
    assert loaded()["editor"]["workspace"]["container_path"] == f"{HOME}/repo"


# --------------------------------------------------------------------------
# R19 — a missing key is a finding, never a value written in here
# --------------------------------------------------------------------------


def test_a_key_the_contract_does_not_carry_is_named_and_called_a_finding():
    with pytest.raises(contract.ContractRefused) as refused:
        contract.require(loaded(), "editor", "image", "never_declared")
    assert "editor.image.never_declared" in str(refused.value)
    assert "finding" in str(refused.value) and "R19" in str(refused.value)


def test_an_optional_key_is_absent_rather_than_refused_and_a_declared_null_is_a_value():
    document = loaded()
    assert contract.optional(document, "editor", "image", "registry", default="none") == "none"
    moved = json.loads(editor_text())
    moved["editor"]["image"]["registry"] = None
    assert contract.optional(moved, "editor", "image", "registry", default="none") is None


def test_a_list_key_is_refused_when_it_is_not_a_list_of_strings():
    moved = json.loads(editor_text())
    moved["editor"]["runtimes"]["selectable"] = "java"
    with pytest.raises(contract.ContractRefused, match="must be a list"):
        contract.words(moved, "editor", "runtimes", "selectable")
    moved["editor"]["runtimes"]["selectable"] = ["java", 7]
    with pytest.raises(contract.ContractRefused, match="must be a string"):
        contract.words(moved, "editor", "runtimes", "selectable")


def test_a_block_list_is_refused_when_its_entries_are_not_objects():
    moved = json.loads(editor_text())
    moved["editor"]["mounts"] = ["a bind"]
    with pytest.raises(contract.ContractRefused, match="must be an object"):
        contract.blocks(moved["editor"], "mounts")


# --------------------------------------------------------------------------
# Against the real sibling — skipped where none is readable
# --------------------------------------------------------------------------


def test_the_component_is_the_one_the_workspace_pins():
    if os.environ.get(DEV_CONTAINER):
        pytest.skip("the pinned image mounts one directory, so no sibling can be resolved")
    named = [component.name for component in read_workspace(repository_root())]
    assert contract.EDITOR_COMPONENT in named, named


def test_the_recorded_promise_is_one_that_component_can_satisfy():
    document = declared()
    if document is None:
        pytest.skip(f"{contract.EDITOR_COMPONENT}'s {contract.CONSUMING} is not readable here")
    # ⛔ Its own contract asks every consumer to record what it built against.
    # A component providing LESS than the record is the refusal R9 exists for.
    assert document["provides"] >= contract.EDITOR_PROMISE
    assert document["consuming_api"] == contract.EDITOR_API


def test_the_real_contract_is_read_by_this_reader_without_a_single_key_written_in():
    document = declared()
    if document is None:
        pytest.skip(f"{contract.EDITOR_COMPONENT}'s {contract.CONSUMING} is not readable here")
    where = Path(contract.CONSUMING)
    read = contract.read(
        json.dumps(document),
        component=contract.EDITOR_COMPONENT,
        api=contract.EDITOR_API,
        promise=contract.EDITOR_PROMISE,
        where=where.name,
    )
    assert read["component"] == contract.EDITOR_COMPONENT


def test_the_narration_promise_is_imported_and_never_respelled():
    # ⛔ One copy in the tree: `buildserve.narration` records it and this reader
    # reads that record, so a bump is made once.
    assert contract.NARRATION_PROMISE is narration.PROMISE
    assert contract.NARRATION_COMPONENT is narration.COMPONENT
