"""Mirror of `src/studyforge/address/errors.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.address import Address, AddressError, identifier, require_slug, unit_name

#: One call per public entry point that can fail, with an argument it must
#: refuse. ⛔ The table is the test: a new entry point that raises something
#: else is what this catches, and it catches it by being forgotten here.
REFUSALS = [
    ("Address", lambda: Address(("Not A Slug",))),
    ("Address.of", lambda: Address.of("Not A Slug")),
    ("Address.require_depth", lambda: Address.of("basics").require_depth(2)),
    ("Address.unit_key", lambda: Address.of("basics").unit_key(0)),
    ("require_slug", lambda: require_slug("Not A Slug", "segment")),
    ("identifier", lambda: identifier("Not A Slug")),
    ("unit_name", lambda: unit_name(0)),
]


def test_it_is_a_value_error():
    # ⚠️ A deliberate divergence from the extraction source, whose equivalents
    # subclass `Exception`. Every failure in this package is one shape — a
    # caller passed a value it cannot accept — which is what `ValueError`
    # means, so code that already handles bad input handles these without
    # importing anything from the framework.
    assert issubclass(AddressError, ValueError)


@pytest.mark.parametrize("name,call", REFUSALS, ids=[name for name, _ in REFUSALS])
def test_every_entry_point_raises_the_one_exception(name, call):
    with pytest.raises(AddressError):
        call()


@pytest.mark.parametrize("name,call", REFUSALS, ids=[name for name, _ in REFUSALS])
def test_nothing_returns_a_sentinel_instead_of_raising(name, call):
    # R6, stated as a test: none of these repairs a value quietly, returns
    # `None`, or hands back a "best effort". A caller never has to check.
    try:
        call()
    except AddressError:
        return
    pytest.fail(f"{name} returned instead of raising")


@pytest.mark.parametrize("name,call", REFUSALS, ids=[name for name, _ in REFUSALS])
def test_every_message_names_the_offending_value(name, call):
    # ⛔ Never only "invalid". An address model that reports a problem without
    # naming the string costs more to diagnose than to fix.
    with pytest.raises(AddressError) as raised:
        call()
    message = str(raised.value)
    assert message
    assert any(character in message for character in "'\"0123456789"), message
