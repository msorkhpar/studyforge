"""Mirror of `src/studyforge/corpus/manifest/runtimes.py` (R12) — `W350`.

⭐ Every settling clause of the row is asserted both ways: each refusal fires by
name, and every valid shape parses. The version gate is reached through the
document, because `corpus_api` is the document's and not this module's.
⚠️ Two instruments read beyond the module: the spec's §4 carries the key, and
the vocabulary agrees with the runner image's pin file at its pinned commit.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from studyforge.corpus import manifest as package
from studyforge.corpus.manifest import (
    NO_RUNTIMES,
    REQUIRES_JAVA,
    RUNTIMES,
    ManifestError,
    from_document,
    parse_runtimes,
)
from tests.harness import sibling
from tests.support import repository_root

#: A manifest that may declare runtimes: it sets exercises, at the version
#: that added the key.
BASE = {
    "corpus_api": 4,
    "source": "example-corpus",
    "title": "Example Corpus",
    "levels": ["section"],
    "variants": ["java"],
    "exercises": True,
    "placement": "tree",
    "content": {"include": ["*/README*.md"], "exclude": []},
}


def refusal(value: object, *, exercises: bool = True) -> str:
    """The message `parse_runtimes` gives for a declaration it will not accept."""
    with pytest.raises(ManifestError) as raised:
        parse_runtimes(value, exercises=exercises)
    return str(raised.value)


# --- the vocabulary ----------------------------------------------------------


def test_the_vocabulary_is_the_ruled_one_and_is_held_sorted():
    # ⭐ Literal, never read from the constant it pins: round 112's accepted set.
    assert RUNTIMES == ("gradle", "java", "kotlin", "maven", "node", "python", "shell", "sqlite")
    assert list(RUNTIMES) == sorted(RUNTIMES)


def test_the_names_that_need_java_are_in_the_vocabulary_and_java_is_not_one_of_them():
    assert REQUIRES_JAVA == ("gradle", "kotlin", "maven")
    assert set(REQUIRES_JAVA) <= set(RUNTIMES)
    assert "java" not in REQUIRES_JAVA


# --- every valid shape parses ------------------------------------------------


@pytest.mark.parametrize("name", RUNTIMES)
def test_every_name_parses_on_its_own_or_beside_java(name):
    declared = [name] if name not in REQUIRES_JAVA else [name, "java"]
    assert parse_runtimes(declared, exercises=True) == tuple(sorted(declared))


def test_the_whole_vocabulary_parses_at_once():
    assert parse_runtimes(list(reversed(RUNTIMES)), exercises=True) == RUNTIMES


def test_order_carries_no_meaning_and_two_equal_declarations_are_one_value():
    # R10: the parsed value is sorted, whatever order the corpus wrote.
    assert parse_runtimes(["maven", "java"], exercises=True) == ("java", "maven")
    assert parse_runtimes(["java", "maven"], exercises=True) == ("java", "maven")


def test_an_absent_key_is_no_runtimes_whatever_exercises_says():
    assert parse_runtimes(None, exercises=True, present=False) == NO_RUNTIMES == ()
    assert parse_runtimes(None, exercises=False, present=False) == NO_RUNTIMES


def test_an_empty_list_beside_exercises_is_no_runtimes():
    assert parse_runtimes([], exercises=True) == NO_RUNTIMES


# --- each refusal fires by name ----------------------------------------------


@pytest.mark.parametrize("entry", ["sql", "Java", "java21", "maven:3.9", "", 1, None, ["java"]])
def test_a_name_outside_the_vocabulary_is_refused_naming_the_vocabulary(entry):
    # ⛔ Names only, never versions: `java21` and `maven:3.9` are the two ways a
    # version would sneak in, and both are refused like any unknown name.
    message = refusal(["java", entry])
    assert "'runtimes[1]'" in message
    assert str(list(RUNTIMES)) in message


@pytest.mark.parametrize("value", [None, "java", {"java": True}, 1, True])
def test_a_declared_value_that_is_not_a_list_is_refused(value):
    # ⚠️ An explicit `null` is a corpus that tried to declare something, and it
    # is refused rather than read as absent.
    assert "'runtimes' must be a list" in refusal(value)


def test_a_repeated_name_is_refused_by_name():
    message = refusal(["java", "node", "java"])
    assert "['java']" in message
    assert "more than once" in message


@pytest.mark.parametrize("name", REQUIRES_JAVA)
def test_a_jvm_name_without_java_is_refused_by_name_and_parses_with_it(name):
    message = refusal([name])
    assert f"['{name}']" in message
    assert "'java'" in message
    assert parse_runtimes([name, "java"], exercises=True) == tuple(sorted([name, "java"]))


def test_every_jvm_name_missing_java_is_named_at_once():
    message = refusal(["maven", "kotlin", "node"])
    assert "['kotlin', 'maven']" in message


@pytest.mark.parametrize("value", [["java"], [], None])
def test_the_key_beside_exercises_false_is_refused(value):
    # ⛔ The key at all, whatever it holds: a runner for nothing to run (§7).
    assert "exercises: false" in refusal(value, exercises=False)


# --- through the document: the field, the version gate (`TC-00/2`) ------------


def test_the_manifest_carries_the_declaration_sorted():
    built = from_document({**BASE, "runtimes": ["maven", "java"]})
    assert built.runtimes == ("java", "maven")


@pytest.mark.parametrize("api", [1, 2, 3, 4])
def test_a_manifest_without_the_key_declares_none_at_every_version(api):
    # ⭐ Absent means none, and none is complete at the reading floor (C5).
    assert from_document({**BASE, "corpus_api": api}).runtimes == NO_RUNTIMES
    assert from_document({**BASE, "corpus_api": api, "exercises": False}).runtimes == ()


@pytest.mark.parametrize("api", [1, 2, 3])
def test_the_top_level_key_is_refused_under_every_earlier_version(api):
    # ⛔ `TC-00/2`: the version map read nested keys only, so a top-level key
    # with no entry would have parsed under `3`. Refused naming both numbers.
    with pytest.raises(ManifestError) as raised:
        from_document({**BASE, "corpus_api": api, "runtimes": ["java"]})
    message = str(raised.value)
    assert "'runtimes'" in message
    assert f"corpus_api {api}" in message
    assert "corpus_api 4" in message


def test_the_version_map_keys_the_top_level_key_under_no_block():
    from studyforge.corpus.manifest.document import KEY_VERSIONS

    assert KEY_VERSIONS[(None, "runtimes")] == 4


def test_a_refusal_from_the_key_arrives_through_the_document_as_the_package_error():
    with pytest.raises(package.RAISES):
        from_document({**BASE, "runtimes": ["maven"]})
    with pytest.raises(ManifestError, match="exercises: false"):
        from_document({**BASE, "exercises": False, "runtimes": ["java"]})


def test_the_key_is_optional_and_is_read_by_this_build():
    assert "runtimes" in package.MANIFEST_KEYS
    assert "runtimes" not in package.REQUIRED_KEYS
    # ⭐ JSON text in, value out: the path a corpus actually takes.
    assert package.parse(json.dumps({**BASE, "runtimes": ["node"]})).runtimes == ("node",)


# --- spec §4 carries the key -------------------------------------------------

SPEC = Path("docs") / "specs" / "2026-09-08-studyforge-v1-design.md"
KEY_TABLE = "### The complete key list"


def key_section(text: str) -> str:
    """The text from §4's key-list heading to the next heading, or `""`."""
    _, found, after = text.partition(KEY_TABLE)
    return after.split("\n#", 1)[0] if found else ""


def carries_the_key(text: str) -> bool:
    """Whether §4's key list names `runtimes` as optional and says `4` added it."""
    section = key_section(text)
    return "| `runtimes` | *optional* |" in section and "`4` added `runtimes`" in section


def test_the_spec_s_key_list_carries_the_key_and_the_version_that_added_it():
    assert carries_the_key((repository_root() / SPEC).read_text(encoding="utf-8"))


def test_the_spec_instrument_can_go_red():
    # ⭐ Held on synthetic text, so the reader is proved able to refuse.
    table = f"{KEY_TABLE}\n\n| `corpus_api` | **required** | `3` added `media.max_files` |\n"
    assert not carries_the_key(table)
    assert not carries_the_key("no such heading")
    with_row = table + "| `runtimes` | *optional* | names |\n`4` added `runtimes`\n"
    assert carries_the_key(with_row)


# --- the vocabulary agrees with the runner image's pins ------------------------

PINS = "pins.json"
RUNNER = "code-server-toolchain"


def unpinned(vocabulary: tuple[str, ...], pins: dict) -> list[str]:
    """Every declarable name the pin file does not pin, sorted.

    ⭐ One-way, never an equality (the shape Ruling 30 gave `MANIFEST_KEYS`): a
    pin no vocabulary names is harmless, a name nothing pins is a build refusal.
    """
    return sorted(set(vocabulary) - set(pins.get("runtimes", {})))


def pinned_runtimes() -> sibling.Reading:
    """The runner's `pins.json` at its checked-out commit, and what it was read from."""
    return sibling.read_sibling(RUNNER, PINS)


def test_the_agreement_instrument_can_go_red():
    assert unpinned(RUNTIMES, {"runtimes": {"java": {}}}) == sorted(set(RUNTIMES) - {"java"})
    assert unpinned(("java",), {"runtimes": {"java": {}, "ruby": {}}}) == []


def test_every_declarable_runtime_is_pinned_by_the_runner_image():
    reading = pinned_runtimes()
    if not reading.committed:
        pytest.skip(
            f"{RUNNER}'s {PINS} was not read at a commit here ({reading.source}), so the "
            f"vocabulary is proved against no pin file. The refusal is held on synthetic "
            f"pins above"
        )
    assert unpinned(RUNTIMES, json.loads(reading.text)) == []
