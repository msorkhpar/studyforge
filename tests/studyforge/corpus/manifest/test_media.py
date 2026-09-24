"""Mirror of `src/studyforge/corpus/manifest/media.py` (R12)."""

from __future__ import annotations

import json
import re

import pytest

from studyforge.corpus.manifest import (
    COMMIT_MODES,
    DEFAULT_MEDIA,
    ManifestError,
    MediaPolicy,
    parse_media,
)
from tests.support import repository_root

#: ⛔ **The epic is where the intent was written down, and until `W207` nothing
#: read it.** Its `media` example declared `max_files` for a whole milestone
#: while the shipped reader refused the key by name, so a corpus copying the
#: published example got a `ManifestError`. ⭐ The example is now the fixture.
EPIC = "docs/tasks/E04-narration.md"


def test_an_absent_media_key_is_a_stated_default_and_not_a_shrug():
    # ⭐ The manifest's acceptance in as many words: an absent `media` block means
    # committed-with-default-limits, **asserted rather than assumed**. The
    # default is a value this module publishes, so a test can compare against
    # it rather than restate it.
    assert parse_media(None) == DEFAULT_MEDIA
    assert DEFAULT_MEDIA.commit == "auto"
    assert DEFAULT_MEDIA.commits is True


def test_auto_commits_and_that_is_not_a_deferred_decision():
    # ⚠️ `auto` is not "decide later": it is "commit, and stop loudly when
    # the limits say to". A reader that treated it as undecided would produce
    # the silent clone the whole policy exists to prevent.
    assert MediaPolicy(commit="auto").commits is True
    assert MediaPolicy(commit="auto").has_limits is True


@pytest.mark.parametrize("mode,commits", [("always", True), ("auto", True), ("never", False)])
def test_each_mode_says_whether_it_commits(mode, commits):
    assert MediaPolicy(commit=mode).commits is commits


@pytest.mark.parametrize("mode", ["always", "never"])
def test_only_auto_consults_the_limits(mode):
    assert MediaPolicy(commit=mode).has_limits is False


def test_the_defaults_are_the_measured_numbers():
    # §5's numbers: a ~5 GB soft limit on a repository, and a hard 100 MiB
    # per-file block. The extraction source found out about both when a push
    # became impossible, after the history already held the blob.
    assert DEFAULT_MEDIA.max_total_bytes == 5_000_000_000
    assert DEFAULT_MEDIA.max_file_bytes == 100 * 1024 * 1024


def test_a_corpus_may_declare_its_own_limits():
    policy = parse_media({"commit": "auto", "max_total_bytes": 10, "max_file_bytes": 5})
    assert (policy.max_total_bytes, policy.max_file_bytes) == (10, 5)


def test_a_partial_declaration_keeps_the_defaults_for_the_rest():
    policy = parse_media({"commit": "never"})
    assert policy.max_total_bytes == DEFAULT_MEDIA.max_total_bytes


@pytest.mark.parametrize("mode", ["Always", "yes", True, None, "commit", ""])
def test_an_unknown_commit_mode_is_refused(mode):
    with pytest.raises(ManifestError, match="media.commit"):
        parse_media({"commit": mode})


def test_the_refusal_names_the_modes_that_are_accepted():
    with pytest.raises(ManifestError) as raised:
        parse_media({"commit": "sometimes"})
    for mode in COMMIT_MODES:
        assert mode in str(raised.value)


@pytest.mark.parametrize("value", [0, -1, "5000000000", 1.5, None, True])
def test_a_limit_must_be_a_positive_int_of_bytes(value):
    with pytest.raises(ManifestError, match="positive int of bytes"):
        parse_media({"commit": "auto", "max_total_bytes": value})


def test_an_unknown_key_in_media_is_refused():
    with pytest.raises(ManifestError, match="unknown key"):
        parse_media({"commit": "auto", "max_gigabytes": 5})


@pytest.mark.parametrize("value", ["auto", [], 7])
def test_media_must_be_an_object(value):
    with pytest.raises(ManifestError, match="'media' must be an object"):
        parse_media(value)


# --- max_files: the count ceiling `corpus_api` 3 added ----------------------


def test_an_undeclared_count_ceiling_is_unbounded_and_not_zero():
    # ⛔ The direction this field must never fail in. A reader that took an
    # unstated ceiling for `0` would refuse the first clip every corpus
    # generates, and it would do it on a number nobody wrote.
    assert DEFAULT_MEDIA.max_files is None
    assert parse_media({"commit": "auto"}).max_files is None


def test_a_corpus_may_declare_a_count_ceiling():
    assert parse_media({"commit": "auto", "max_files": 20_000}).max_files == 20_000


@pytest.mark.parametrize("value", [0, -1, "20000", 1.5, None, True, []])
def test_a_count_ceiling_must_be_a_positive_int_of_files(value):
    # ⚠️ `None` is in this list on purpose: an ABSENT key is unbounded, and an
    # explicit `null` is a corpus that tried to state a ceiling and wrote
    # something that is not one. The two are different answers.
    with pytest.raises(ManifestError, match="positive int of files"):
        parse_media({"commit": "auto", "max_files": value})


def test_the_count_refusal_does_not_ask_for_bytes():
    # ⛔ The message is read by a person editing `corpus.json`. "A positive int
    # of bytes" against `max_files` sends them to convert a count into a size.
    with pytest.raises(ManifestError) as raised:
        parse_media({"commit": "auto", "max_files": 0})
    assert "bytes" not in str(raised.value)


def test_a_byte_limit_still_asks_for_bytes():
    # ⭐ The control for the case above: the unit is per-field, not removed.
    with pytest.raises(ManifestError, match="positive int of bytes"):
        parse_media({"commit": "auto", "max_file_bytes": 0})


def epic_media_example() -> dict:
    """The `media` block `E04-narration.md` publishes, read from the epic itself."""
    text = (repository_root() / EPIC).read_text(encoding="utf-8")
    blocks = [
        found
        for found in re.findall(r"```json\n(.*?)```", text, re.DOTALL)
        if found.lstrip().startswith('"media"')
    ]
    # ⛔ A filter that returns nothing is not a measurement: without this the
    # test below would pass by parsing an empty list of examples.
    assert len(blocks) == 1, f"{EPIC} publishes {len(blocks)} media examples, expected 1"
    return json.loads("{" + blocks[0] + "}")["media"]


def test_the_example_the_epic_publishes_parses():
    # ⛔ **This is the row.** The epic declared `max_files: 20000` while
    # `parse_media` refused unknown keys by name, so the only written record of
    # the intent was an example that did not validate — and no test anywhere
    # read it, which is why it could stay wrong for a milestone.
    policy = parse_media(epic_media_example())
    assert policy.commits is True
    assert policy.max_files is not None


def test_the_epic_says_which_version_its_example_needs():
    # ⚠️ Half the trap: an example that parses through `parse_media` but is
    # pasted into a `corpus_api: 2` manifest is refused by the version gate.
    # The reader has to be told the number, not left to find it in a raise.
    text = (repository_root() / EPIC).read_text(encoding="utf-8")
    assert "corpus_api: 3" in text or "corpus_api` 3" in text
