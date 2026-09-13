"""Mirror of `src/studyforge/progress/keys.py` (R12).

⛔ Every key here is composed by the address package and compared with what the
address package composes — never with a string typed into this file, which
would pass while the store and the page disagreed.
"""

from __future__ import annotations

import pytest

from studyforge.address import Address, parse_unit_key
from studyforge.progress.errors import ProgressError
from studyforge.progress.keys import parse_practice_key, practice_key

#: Assembled rather than written whole, so the hygiene sweep need not except it.
POISON = "/" + "home/jane/private"

ADDRESSES = [
    Address.of("basics"),
    Address.of("basics", "01-getting-started"),
    Address.of("java", "collections", "maps"),
]


@pytest.mark.parametrize("address", ADDRESSES, ids=lambda a: f"depth-{a.depth}")
def test_a_key_round_trips_through_the_address_package(address):
    key = practice_key(address, 7, "practice-java")
    head, _, section = key.rpartition("/")
    # The unit half IS the address package's unit key, and parses back with its inverse.
    assert head == address.unit_key(7)
    assert parse_unit_key(head, address.depth) == (address, 7)
    assert section == "practice-java"
    assert parse_practice_key(key, address.depth) == (address, 7, "practice-java")


def test_an_authored_section_key_without_the_practice_prefix_is_legal():
    address = ADDRESSES[1]
    assert parse_practice_key(practice_key(address, 1, "my-exercise"), 2)[2] == "my-exercise"


def test_a_key_read_at_the_wrong_depth_is_refused():
    key = practice_key(ADDRESSES[1], 3, "practice-java")
    with pytest.raises(ProgressError):
        parse_practice_key(key, 1)


@pytest.mark.parametrize(
    "call",
    [
        lambda: practice_key(ADDRESSES[1], 1, POISON),
        lambda: practice_key(ADDRESSES[1], 0, "practice-java"),
        lambda: practice_key(POISON, 1, "practice-java"),
        lambda: parse_practice_key(POISON, 2),
        lambda: parse_practice_key(f"basics/intro/unit-01/{POISON}", 2),
        lambda: parse_practice_key("basics/intro/unit-1/practice-java", 2),
    ],
)
def test_a_refusal_never_reproduces_what_it_refused(call):
    with pytest.raises(ProgressError) as refused:
        call()
    assert "jane" not in str(refused.value)
