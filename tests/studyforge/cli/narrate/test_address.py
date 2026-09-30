"""Mirror of `src/studyforge/cli/narrate/address.py` (R12): flag, variable, default, and refusals.

The two personal-data cases are assembled at run time so this file holds neither shape.
"""

from __future__ import annotations

import pytest

from studyforge.cli.narrate.address import DEFAULT_SERVICE, ENVIRONMENT_VARIABLE, resolve

AT = "@"
DOT = "."


def test_the_flag_wins_over_the_variable_and_the_variable_over_the_default():
    variable = {ENVIRONMENT_VARIABLE: "http://narrate.example.invalid:9000"}
    assert resolve("http://flag.example.invalid:1", variable) == "http://flag.example.invalid:1"
    assert resolve(None, variable) == "http://narrate.example.invalid:9000"
    assert resolve(None, {}) == DEFAULT_SERVICE
    assert resolve("  ", {ENVIRONMENT_VARIABLE: ""}) == DEFAULT_SERVICE


def test_a_trailing_slash_is_dropped_and_a_path_prefix_kept():
    assert resolve("https://host.example.invalid/tts/", {}) == "https://host.example.invalid/tts"


@pytest.mark.parametrize(
    "address",
    [
        "ftp://host.example.invalid",
        "host.example.invalid:8870",
        "http://",
        "http://user:secret@host.example.invalid",
        "http://user@host.example.invalid",
        "http://host.example.invalid:99999",
        "http://host.example.invalid?token=1",
        "http://host.example.invalid#frag",
        f"http://10.0.0.5/tts/carol{AT}corp.net",
        f"http://somebody-laptop{DOT}local:8870",
    ],
)
def test_an_address_the_client_would_not_call_is_refused_whichever_way_it_arrives(address):
    with pytest.raises(ValueError):
        resolve(address, {})
    with pytest.raises(ValueError):
        resolve(None, {ENVIRONMENT_VARIABLE: address})


def test_a_refused_address_names_its_source_and_never_echoes_a_credential():
    with pytest.raises(ValueError) as caught:
        resolve("http://user:hunter2@host.example.invalid", {})
    assert "--service" in str(caught.value) and "hunter2" not in str(caught.value)
    with pytest.raises(ValueError) as caught:
        resolve(None, {ENVIRONMENT_VARIABLE: "ftp://x"})
    assert ENVIRONMENT_VARIABLE in str(caught.value)
