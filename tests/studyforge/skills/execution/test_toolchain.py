"""Mirror of `src/studyforge/skills/execution/toolchain.py` (R12).

⛔ The selection is a JOIN of two declarations — the corpus's and the
component's — and neither list is written in the module, so each claim here is
asserted by MOVING one of them and watching the answer move.

⚠️ **One test in here is a held-open hole.** `SET_SEPARATOR` is provisional
because the component's contract leaves `<the declared set>` in one argv slot
and declares nowhere how a set is written into it. ⭐ The guard
below goes RED the day that key appears, which is when the constant is deleted.
"""

from __future__ import annotations

import json
import os

import pytest

from studyforge.skills.execution import contract, toolchain
from tests.harness.workspace import DEV_CONTAINER
from tests.studyforge.skills.execution.contracts import editor_contract
from tests.studyforge.skills.execution.test_contract import declared


def selected(runtimes, **moved):
    """A selection over the synthetic contract, with `moved` merged into it."""
    return toolchain.select(runtimes, editor_contract(**moved))


def test_the_carried_set_is_the_intersection_and_it_is_sorted():
    assert selected(["maven", "java"]).carried == ("java", "maven")
    assert selected(["maven", "java"]).declared == ("java", "maven")


def test_a_runtime_the_image_cannot_carry_is_withheld_with_the_contracts_own_reason():
    withheld = selected(["java", "sqlite"]).withheld
    assert [name for name, _ in withheld] == ["sqlite"]
    assert withheld[0][1] == "the editor copies only /opt out of the runner"


def test_widening_the_contracts_selectable_list_moves_the_answer():
    # ⭐ The vocabulary is the component's, not this module's: nothing here
    # knows which runtimes exist.
    document = editor_contract()
    document["editor"]["runtimes"]["selectable"].append("sqlite")
    assert toolchain.select(["java", "sqlite"], document).carried == ("java", "sqlite")


def test_a_withheld_runtime_with_no_stated_reason_is_refused_rather_than_explained():
    # ⛔ A corpus is owed the reason, and inventing one here would be this skill
    # answering for the component (R19).
    document = editor_contract()
    document["editor"]["runtimes"]["not_carried"] = {}
    with pytest.raises(contract.ContractRefused, match="not_carried"):
        toolchain.select(["java", "sqlite"], document)


def test_the_declared_set_is_substituted_into_the_slot_the_contract_left():
    selection = selected(["java", "maven"])
    assert selection.build == ("python3", "build.py", "--runtimes", "java,maven")
    assert selection.tag_from[-1] == "--print-tag"
    assert toolchain.PLACEHOLDER not in selection.build


def test_an_argv_with_no_slot_for_the_set_is_refused():
    document = editor_contract()
    document["editor"]["image"]["built_by"] = ["python3", "build.py"]
    with pytest.raises(contract.ContractRefused, match="leaves no slot"):
        toolchain.select(["java"], document)


def test_the_image_value_may_be_a_compose_interpolation_or_a_run_value():
    assert selected(["java"]).image_value.startswith("${EDITOR_IMAGE")
    document = editor_contract()
    del document["editor"]["image"]["compose_value"]
    document["editor"]["image"]["run_value"] = "<tag>"
    assert toolchain.select(["java"], document).image_value == "<tag>"


def test_a_block_that_says_neither_is_refused():
    document = editor_contract()
    del document["editor"]["image"]["compose_value"]
    with pytest.raises(contract.ContractRefused, match="neither compose_value nor run_value"):
        toolchain.select(["java"], document)


def test_another_block_of_the_same_contract_can_be_selected_from():
    # ⚠️ The runner is consumed by a run line rather than by compose, and the
    # block name is a parameter for exactly that reason.
    document = editor_contract()
    document["runner"] = json.loads(json.dumps(document["editor"]))
    document["runner"]["image"]["env_var"] = "STUDYFORGE_RUNNER_IMAGE"
    assert toolchain.select(["java"], document, block="runner").image_env == (
        "STUDYFORGE_RUNNER_IMAGE"
    )


def test_a_block_that_is_not_there_is_refused_by_the_key_path_it_wanted():
    with pytest.raises(contract.ContractRefused) as refused:
        toolchain.select(["java"], editor_contract(), block="nowhere")
    assert "nowhere" in str(refused.value)


def test_the_rendered_selection_is_json_a_corpus_can_keep():
    document = json.loads(selected(["java", "maven"]).render())
    assert document["carried"] == ["java", "maven"]
    assert document["image"]["env_var"] == "EDITOR_IMAGE"
    assert document["build"][-1] == "java,maven"


# --------------------------------------------------------------------------
# ⚠️ The held-open hole
# --------------------------------------------------------------------------


def test_the_component_still_declares_no_separator_for_its_own_build_flag():
    # ⛔ `SET_SEPARATOR` is PROVISIONAL and this is what holds it
    # open: the day the component declares how a set is written into that argv
    # slot, this goes RED, the constant is deleted, and the value is read.
    document = declared()
    if document is None:
        pytest.skip(f"{contract.EDITOR_COMPONENT}'s {contract.CONSUMING} is not readable here")
    for block in ("editor", "runner"):
        found = contract.optional(document, block, *toolchain.SEPARATOR_KEY)
        assert found is None, (
            f"{block}.{'.'.join(toolchain.SEPARATOR_KEY)} now exists: delete "
            f"toolchain.SET_SEPARATOR and read this instead"
        )


def test_the_real_contract_still_leaves_the_slot_this_module_substitutes_into():
    document = declared()
    if document is None:
        pytest.skip(f"{contract.EDITOR_COMPONENT}'s {contract.CONSUMING} is not readable here")
    assert toolchain.PLACEHOLDER in document["editor"]["image"]["built_by"]


def test_the_real_contract_is_sufficient_for_a_selection_with_no_other_input():
    # ⭐ §8.1's sufficiency clause, for the selection half: every key this
    # join needs is one the component publishes. A host reading only.
    if os.environ.get(DEV_CONTAINER):
        pytest.skip("the pinned image mounts one directory, so no sibling can be resolved")
    document = declared()
    if document is None:
        pytest.skip(f"{contract.EDITOR_COMPONENT}'s {contract.CONSUMING} is not readable here")
    selection = toolchain.select(["java", "maven"], document)
    assert selection.carried == ("java", "maven")
    assert selection.build[-1] == "java,maven"


def test_the_repository_a_recorded_tag_must_name_is_read_and_never_written_to_the_selection():
    # ⭐ The record step checks a printed tag against it; ⛔ the kept selection
    # stays the bytes a corpus already carries, so it is not in the document.
    selection = selected(["java"])
    assert selection.repository == "example/editor"
    assert "example/editor" not in selection.render()
