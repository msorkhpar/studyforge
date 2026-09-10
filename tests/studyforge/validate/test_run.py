"""The whole of `validate`, against the committed fixtures (SF-25)."""

import json
from pathlib import Path

import pytest

from studyforge.validate import validate
from studyforge.validate.run import CHECKS
from tests.studyforge.validate import corpora
from tests.support import repository_root

FIXTURES = Path("tests/fixtures")

#: FND-04's five, and the one rule each is expected to break. ⛔ Written out
#: rather than derived from `tests/fixture_checks`: that package's rule ids are
#: its own checker's, and two checkers with different subjects must be allowed
#: to disagree. What is asserted here is that **this** tool reports exactly one.
INVALID = {
    "bad-corpus-api": "manifest",
    "address-directory-mismatch": "address-directory",
    "digest-mismatch": "digest",
    "ordinal-gap": "container",
    "personal-data": "personal-data",
}


def fixture(name):
    return repository_root() / FIXTURES / name


@pytest.mark.parametrize("name", ["depth1", "depth2"])
def test_a_valid_corpus_passes(name):
    report = validate(fixture(name))
    assert report.findings == (), "\n".join(f.line() for f in report.findings)
    assert report.exit_code == 0


@pytest.mark.parametrize(("name", "rule"), sorted(INVALID.items()))
def test_each_invalid_corpus_fails_on_exactly_its_one_rule(name, rule):
    # ⚠️ **Exactly one.** FND-04 built each of these to break a single rule and
    # two of its tests hold that property structurally. A validator reporting
    # two here is a finding about the validator or about the fixture, and the
    # first time this ran it was the validator: a document refused by the R7
    # gate was then reported as a *missing unit*, which is one defect wearing
    # two names. See `corpus.Refused`.
    report = validate(fixture("invalid") / name)
    assert report.rules == (rule,), "\n".join(f.line() for f in report.findings)
    assert report.exit_code == 1


@pytest.mark.parametrize("name", sorted(INVALID))
def test_the_message_names_the_file_and_never_an_absolute_path(name):
    # ⛔ R7: a report is the most-pasted artifact this tool produces.
    root = fixture("invalid") / name
    report = validate(root)
    for line in report.lines():
        assert str(root) not in line
        assert "/home/" not in line and "/Users/" not in line


def test_every_rule_the_tool_can_emit_is_reachable():
    # ⭐ A rule id nobody can produce is a message nobody will ever see, and a
    # check with no rule id is a finding nobody can filter. Both are failures.
    emitted = set()
    for name in ("depth1", "depth2", *(f"invalid/{n}" for n in INVALID)):
        report = validate(fixture(name))
        emitted |= {f.rule for f in report.findings} | {u.rule for u in report.unchecked}
    assert emitted


def test_the_check_list_is_one_list():
    # ⛔ "What does validate check" has one answer, not four.
    assert len(CHECKS) == len({check.__name__ for check in CHECKS})
    assert all(callable(check) for check in CHECKS)


# --------------------------------------------------------------------------
# The completeness check — the one this task exists for
# --------------------------------------------------------------------------


def test_a_corpus_whose_source_is_present_is_checked_against_it(tmp_path):
    report = validate(corpora.one_unit(tmp_path / "c", source=corpora.SOURCE))
    assert report.exit_code == 0
    assert "short-read" not in {u.rule for u in report.unchecked}


def test_a_construct_the_parser_silently_skipped_is_caught(tmp_path):
    # ⭐ **The fixture this task exists for.** Every other check passes: the
    # digest matches its blocks, the counts match its blocks, the address
    # matches its directory, the version is known and the gate is clean. The
    # source carries a third heading the archive does not, and only a count
    # taken outside the parser can see it.
    root = corpora.one_unit(
        tmp_path / "c", source=corpora.SOURCE + "\n### Three\n\nSkipped.\n"
    )
    report = validate(root)
    assert report.rules == ("short-read",)
    assert report.exit_code == 1


def test_and_every_other_check_really_does_pass_on_that_input(tmp_path):
    # ⚠️ Without this the test above proves only that *something* is wrong.
    # The same corpus with the extra heading removed from the source is clean,
    # so the difference is the source and nothing else.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    assert validate(root).findings == ()


def test_a_digest_check_cannot_see_a_short_read(tmp_path):
    # ⛔ The argument in one assertion: the digest is computed from the blocks
    # and compared against the blocks, so it agrees with itself no matter what
    # the source said. Two readings from one parser are not two readings.
    root = corpora.one_unit(
        tmp_path / "c", source=corpora.SOURCE + "\n### Three\n\nSkipped.\n"
    )
    document = json.loads(
        (root / "archive/demo/raw/prose/unit-01/lesson-1.json").read_text(encoding="utf-8")
    )
    from studyforge.archive.document import content_sha256

    assert document["content_sha256"] == content_sha256(document["blocks"])
    assert validate(root).rules == ("short-read",)
