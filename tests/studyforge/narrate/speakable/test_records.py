"""Mirror of `src/studyforge/narrate/speakable/records.py` (R12)."""

from __future__ import annotations

import dataclasses

import pytest

from studyforge.narrate.speakable import records
from studyforge.narrate.speakable.records import Speakable, SpeakableError, SpeechUnit


def a_unit(**changed) -> SpeechUnit:
    """One record with the fields a caller usually cares about, overridable."""
    fields = {
        "id": "corpus--unit-01.shared.b1",
        "speak": "one",
        "section": "shared",
        "block_path": (0,),
        "sub_index": None,
        "kind": "para",
    }
    return SpeechUnit(**{**fields, **changed})


def test_a_speech_unit_cannot_be_edited_after_it_is_built():
    # ⛔ The list is a contract two other components read and neither may edit.
    with pytest.raises(dataclasses.FrozenInstanceError):
        a_unit().speak = "something else"


def test_a_speakable_cannot_be_edited_either():
    whole = Speakable(unit_key="corpus/unit-01", units=(a_unit(),), withheld=0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        whole.withheld = 9


def test_the_position_is_the_lookup_key_and_it_has_one_spelling():
    # ⭐ So a renderer never writes the tuple out again, which would be the second
    # numbering scheme this package exists to prevent.
    unit = a_unit(block_path=(1, 2), sub_index=3)
    assert unit.position == ("shared", (1, 2), 3)


def test_two_units_at_one_position_have_one_position_key():
    assert a_unit(id="x").position == a_unit(id="y").position


def test_the_id_is_one_based_and_the_coordinates_are_zero_based():
    # ⛔ The two bases differ on purpose: an id is a name, the coordinates are a
    # subscript, and quietly making one look like the other is how an off-by-one
    # hides — in audio, where nothing renders wrong.
    unit = a_unit(id="corpus--unit-01.shared.b1", block_path=(0,))
    assert unit.id.endswith("b1")
    assert unit.block_path == (0,)


def test_the_contract_says_what_withheld_does_not_count():
    # ⚠️ `docs/conventions/module-structure.md`: when one half of a pair is
    # constrained, name what sits beside it that is not. A coverage report reading
    # `withheld` as "everything the listener does not hear" would under-report.
    contract = records.__doc__ or ""
    assert "It is NOT a total count" in contract
    for beside in ("image", "video", "rule", "html"):
        assert beside in contract


def test_the_refusal_is_its_own_family_and_not_a_value_error_by_accident():
    assert issubclass(SpeakableError, Exception)
    assert not issubclass(SpeakableError, ValueError)


def test_the_records_module_reaches_for_nothing_but_dataclasses():
    # ⛔ A record that could not be read without the code that built it is not a
    # record. `dataclasses` is the whole import list.
    source = open(records.__file__, encoding="utf-8").read()
    imports = sorted(
        line.strip() for line in source.splitlines() if line.startswith(("import ", "from "))
    )
    assert imports == ["from __future__ import annotations", "from dataclasses import dataclass"]
