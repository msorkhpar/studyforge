"""Mirror of `src/studyforge/skills/buildserve/narration.py` (R12).

⛔ The subject is a set of facts about a **sibling component**, so each one is
checked against the thing it describes rather than against a copy of itself:
the address against the verb's own default, the promise against that
component's `consuming.json` wherever it is on disk, and the routes against
their absence.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from studyforge.cli.narrate.cli import DEFAULT_SERVICE
from studyforge.skills.buildserve import narration
from tests.support import repository_root
from tools.workspace import pinned, read
from tools.workspace.__main__ import DEV_CONTAINER

#: Every path the component's API publishes. ⛔ Typed HERE and nowhere in `src/`:
#: this file's whole job is to assert that no skill repeats them.
ROUTES = ("/healthz", "/v1/voices", "/v1/speech", "/v1/jobs", "/v1/artifacts")

#: The two documents `narration` points at instead of copying.
SKILL = Path(narration.__file__).parent / "SKILL.md"


def declared() -> pinned.Reading:
    """The component's own `consuming.json`, **read at the commit the pin names**.

    ⛔ `W404`: this used to read whatever sat in the sibling's working tree, so a
    staged file on no ref read as the contract and the green result reproduced on
    no other host. ⭐ The reading now says which of the three things happened —
    read at the pin, read from a working tree and therefore LOCAL, or absent —
    and the cases below skip on anything but the first, quoting the sentence.

    ⚠️ The pinned image mounts exactly one directory, so every sibling is absent
    in there and reporting one absent would be a well-formed wrong answer. That
    is the `ABSENT` state, and it arrives as a sentence rather than a crash.
    """
    return pinned.read_sibling(
        narration.COMPONENT, narration.CONTRACT[0], repository_root=repository_root()
    )


def test_the_address_is_the_verbs_own_default_and_is_loopback():
    # ⛔ One spelling in the tree: a skill that sent an operator to another port
    # would be telling them to start a service the verb never calls.
    assert narration.ADDRESS is DEFAULT_SERVICE
    assert narration.ADDRESS.startswith("http://127.0.0.1:")


def test_the_component_is_the_one_the_workspace_pins():
    # ⭐ Read from the pin file, so a renamed component goes RED here.
    if os.environ.get(DEV_CONTAINER):
        pytest.skip("the pinned image mounts one directory, so no sibling can be resolved")
    named = [component.name for component in read(repository_root())]
    assert narration.COMPONENT in named, named


def test_the_recorded_promise_is_the_one_that_component_declares():
    reading = declared()
    if not reading.pinned:
        # ⛔ A LOCAL reading is skipped rather than believed: it would green here
        # and red on any other checkout of the same pin file (`W404`).
        pytest.skip(
            f"{narration.COMPONENT}'s {narration.CONTRACT[0]} was not read at "
            f"its pin: {reading.source}"
        )
    # ⛔ Its own API asks every caller to record the promise it built against and
    # refuses a mismatch rather than migrating it, so a bump must be read, not guessed.
    assert narration.PROMISE == json.loads(reading.text)["provides"]


def test_a_reading_that_is_not_at_the_pin_is_never_believed(tmp_path):
    """⭐ The skip above is a decision, so it is asserted in both directions (`W404`)."""
    local = pinned.read_directory(tmp_path, narration.CONTRACT[0])
    (tmp_path / narration.CONTRACT[0]).write_text('{"provides": 99}', encoding="utf-8")
    found = pinned.read_directory(tmp_path, narration.CONTRACT[0])
    assert local.absent and not local.pinned
    # ⛔ A contract that is only on disk is readable and still not pinned — the
    # exact shape that read as green while existing on no ref.
    assert found.working_tree and not found.pinned
    assert json.loads(found.text)["provides"] == 99


def test_the_promise_is_a_whole_number_and_the_contract_names_two_documents():
    assert isinstance(narration.PROMISE, int) and not isinstance(narration.PROMISE, bool)
    assert narration.CONTRACT == ("consuming.json", "docs/api.md")


def test_no_route_of_that_component_is_repeated_in_the_module_or_the_procedure():
    # ⛔ *Must not become a second copy of the service's API.* The component owns
    # its routes; this skill points. ⚠️ Both files are on trial, not just the module.
    for text in (Path(narration.__file__).read_text("utf-8"), SKILL.read_text("utf-8")):
        assert [route for route in ROUTES if route in text] == []


def test_a_planted_route_is_caught():
    # ⭐ A check that has only ever run green has not been shown capable of red.
    planted = "fetch the manifest from /v1/jobs and the audio after it\n"
    assert [route for route in ROUTES if route in planted] == ["/v1/jobs"]


def test_the_sentences_name_the_component_the_address_and_the_remedy_composes_them():
    assert narration.COMPONENT in narration.AVAILABLE
    assert narration.ADDRESS in narration.AVAILABLE
    assert narration.COMPONENT in narration.HOW and "--voice" in narration.HOW
    assert "loopback" in narration.FETCHED
    for sentence in (narration.AVAILABLE, narration.HOW, narration.FETCHED):
        assert sentence in narration.REMEDY


def test_no_sentence_carries_a_path_or_promises_a_container_command():
    # ⛔ R7: no absolute path anywhere. ⛔ §8.3: the skill starts no container, so
    # the sentences carry a pointer rather than a command a reader would paste.
    for sentence in (narration.AVAILABLE, narration.HOW, narration.FETCHED, narration.REMEDY):
        assert "/home/" not in sentence and not sentence.startswith("/")
        assert "docker" not in sentence.lower()
