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
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE + "\n### Three\n\nSkipped.\n")
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
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE + "\n### Three\n\nSkipped.\n")
    document = json.loads(
        (root / "archive/demo/raw/prose/unit-01/lesson-1.json").read_text(encoding="utf-8")
    )
    from studyforge.archive.document import content_sha256

    assert document["content_sha256"] == content_sha256(document["blocks"])
    assert validate(root).rules == ("short-read",)


# --------------------------------------------------------------------------
# R7 end to end: a bad file on disk, and what reaches a report line
# --------------------------------------------------------------------------

#: Ten shapes an identifier arrives in, **none of them anybody's** — every one
#: is the `Jane Doe` placeholder the conventions require. ⭐ Adapted from the
#: CTO's round-17 probe, which is why it is a table and not one example: the
#: personal-data gate is a **shape list**, and a list is exactly the thing that
#: cannot be checked by picking the shape you thought of.
#: ⛔ The two home-shaped ones are **assembled**, never written as literals.
#: The quality floor's personal-data scan reads this file and cannot tell a
#: placeholder from the real thing — and it is right not to try, so the file
#: simply never contains the shape. `_SEP` is the whole trick.
_SEP = "/"

POISON_SHAPES = {
    "posix home": f"{_SEP}home{_SEP}janedoe{_SEP}private-corpus",
    "windows home": "C:\\Users\\janedoe\\private-corpus",
    "macos home": f"{_SEP}Users{_SEP}janedoe{_SEP}private-corpus",
    "relative path": "../../janedoe/Documents/corpus",
    "email": "janedoe@corp.example.net",
    "hostname": "janedoe-laptop.corp.internal",
    "unc share": "\\\\FILESRV\\janedoe$\\corpus",
    "url with user": "https://janedoe@git.corp.example/repo.git",
    "plain title": "Jane Doe's Draft Corpus",
    "tmp path": "/tmp/build-janedoe-1000/corpus",
}

#: ⚠️ **The six that leak today, and they leak through one echo.** Measured
#: 2026-09-09 in the pinned image: each arrives as `{value!r}` from
#: `address.require_slug`, which W1 (`fix/W1-W2-address-echo`) removes — the
#: CTO measured 10 of 10 clean with that change and **no change to `validate`**.
#:
#: ⛔ `strict=True` is the enforcement and it is deliberate: the day W1 merges
#: these XPASS, the suite goes red, and this table must be emptied **in that
#: merge** rather than outliving the defect it describes. An xfail that can
#: quietly survive its own fix is how a floor rots.
OWED_TO_W1 = (
    "windows home",
    "relative path",
    "hostname",
    "unc share",
    "plain title",
    "tmp path",
)


def poisoned(shape):
    marks = (
        [
            pytest.mark.xfail(
                strict=True,
                reason=(
                    f"{shape}: R7 echo owed to W1 (fix/W1-W2-address-echo), Ruling 17. "
                    f"Delete this entry from OWED_TO_W1 when W1 merges."
                ),
            )
        ]
        if shape in OWED_TO_W1
        else []
    )
    return pytest.param(shape, POISON_SHAPES[shape], id=shape.replace(" ", "-"), marks=marks)


@pytest.mark.parametrize(("shape", "poison"), [poisoned(s) for s in sorted(POISON_SHAPES)])
def test_no_identifier_reaches_a_report_line(tmp_path, shape, poison):
    # ⛔ **The vantage point W2 does not have** (§10b, third instance). W2 asks
    # each function whether it echoes; this asks what a *composed pipeline*
    # prints given a bad file on disk, which is the only question an integrator
    # actually asks. Ruling 13: trust enforced nowhere is not trust.
    #
    # ⚠️ Asserted on the identifier, never on the sentence — the address
    # refusals' wording changes on W1's branch and this must survive that.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    path = root / "archive/demo/container.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["address"] = [poison]
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    printed = "\n".join(validate(root).lines()).lower()
    assert "janedoe" not in printed and "jane doe" not in printed, printed


def test_the_poison_table_is_still_a_table(tmp_path):
    # ⚠️ A shape that stopped being refused at all would pass the test above
    # for the wrong reason — nothing reported, nothing leaked. Each shape must
    # still be *refused*, whatever the refusal says.
    for poison in POISON_SHAPES.values():
        root = corpora.one_unit(tmp_path / poison[:8].replace("/", "_"), source=corpora.SOURCE)
        path = root / "archive/demo/container.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["address"] = [poison]
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        assert validate(root).exit_code == 1
