"""Mirror of `src/studyforge/corpus/discovery/errors.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.address import Address
from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.discovery import DiscoveryError, pages, scan
from studyforge.corpus.placement import UNIT_SUFFIX

DEPTHS = {"code-corpus": 2}
ADDRESS = Address.of("basics", "16-streams-api")


def test_a_discovery_error_is_a_value_error():
    # ⚠️ SF-01's split, and `placement`'s: "you handed me something I cannot
    # scan". ⛔ The malformed *documents* this package meets are reported
    # rather than raised, so they never reach this type's front door.
    assert issubclass(DiscoveryError, ValueError)


def test_a_scan_that_cannot_be_run_at_all_is_the_only_thing_that_raises(tmp_path):
    with pytest.raises(DiscoveryError):
        pages(tmp_path / "not-a-directory")
    with pytest.raises(DiscoveryError):
        scan(tmp_path / "not-a-directory", DEPTHS)


def test_a_refusal_carries_no_absolute_path(tmp_path):
    # ⛔ R7. A scan runs over a real root and its refusals go into a log.
    with pytest.raises(DiscoveryError) as raised:
        scan(tmp_path / "absent", DEPTHS)
    assert str(tmp_path) not in str(raised.value)


def test_a_personal_data_leak_is_not_a_discovery_error(tmp_path):
    # ⛔ Ruling 58, rubric §1d. This family exists so a scan over a thousand
    # files catches one type per file and carries on; an R7 refusal inside it
    # would be filed as one more page that could not be identified.
    assert not issubclass(PersonalDataLeak, DiscoveryError)
    assert not issubclass(PersonalDataLeak, ValueError)


def test_a_page_this_build_cannot_identify_does_not_raise(tmp_path):
    # ⭐ The whole point of the type being small: the walk reports and
    # continues, so a scan of a broken corpus still names everything wrong
    # with it rather than the first thing.
    (tmp_path / f"a{UNIT_SUFFIX}").write_text("<html>nothing</html>", encoding="utf-8")
    (tmp_path / f"b{UNIT_SUFFIX}").write_text("<html>nothing either</html>", encoding="utf-8")
    site = scan(tmp_path, DEPTHS)
    assert len(site.unidentified) == 2
