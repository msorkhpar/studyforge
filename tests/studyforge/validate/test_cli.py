"""The command line: one root in, one report out, an exit code a script reads.

⛔ **Three exit codes, and the third is the one that matters.** A script that
cannot tell "invalid" from "you gave me a directory that does not exist" will
treat one as the other, and CI goes green on a typo.
"""

import io

from studyforge.validate.cli import UNUSABLE, build_parser, main
from studyforge.validate.report import INVALID, OK
from tests.studyforge.validate import corpora


def invoke(*argv):
    """Run the CLI, returning `(exit code, what it printed)`."""
    out = io.StringIO()
    return main(list(argv), out=out), out.getvalue()


# --------------------------------------------------------------------------
# the interface
# --------------------------------------------------------------------------


def test_the_parser_takes_one_root_and_says_what_it_is_for():
    parser = build_parser()
    assert parser.prog == "studyforge validate"
    assert "definition of done" in parser.description


def test_the_root_argument_is_required():
    assert build_parser().parse_args(["somewhere"]).root == "somewhere"


# --------------------------------------------------------------------------
# ⛔ the three exit codes
# --------------------------------------------------------------------------


def test_a_valid_corpus_exits_zero(tmp_path):
    code, printed = invoke(str(corpora.one_unit(tmp_path / "c")))
    assert code == OK
    assert "valid:" in printed


def test_an_invalid_corpus_exits_one(tmp_path):
    root = corpora.one_unit(tmp_path / "c", blocks=[])
    code, printed = invoke(str(root))
    assert code == INVALID
    assert "NOT valid:" in printed


def test_a_root_that_is_not_a_directory_exits_two(tmp_path):
    # ⛔ Deliberately distinct from `INVALID`: a missing directory is a mistake
    # in the invocation, and reporting it as "invalid" teaches an adapter
    # author to distrust the one signal they have.
    code, printed = invoke(str(tmp_path / "nowhere"))
    assert code == UNUSABLE
    assert "not a directory" in printed


def test_a_file_given_where_a_directory_was_asked_for_exits_two(tmp_path):
    path = tmp_path / "corpus.json"
    path.write_text("{}", encoding="utf-8")
    assert invoke(str(path))[0] == UNUSABLE


def test_the_three_codes_are_three_different_numbers():
    assert len({OK, INVALID, UNUSABLE}) == 3


# --------------------------------------------------------------------------
# ⛔ output names every failure, not just the first
# --------------------------------------------------------------------------


def test_every_finding_is_printed_not_only_the_first(tmp_path):
    root = corpora.repeated_label(tmp_path / "c")
    code, printed = invoke(str(root))
    assert code == INVALID
    assert printed.count("[duplicate-path]") > 1


def test_unchecked_claims_are_printed_alongside_the_findings(tmp_path):
    printed = invoke(str(corpora.one_unit(tmp_path / "c")))[1]
    assert "not checked" in printed


def test_the_last_line_is_always_the_summary(tmp_path):
    printed = invoke(str(corpora.one_unit(tmp_path / "c")))[1]
    assert printed.strip().splitlines()[-1].startswith(("valid:", "NOT valid:"))


# --------------------------------------------------------------------------
# ⛔ R7: the report is the most-pasted artifact this tool produces
# --------------------------------------------------------------------------


def test_the_unusable_message_names_what_was_asked_for_not_what_it_resolved_to(tmp_path):
    # ⚠️ The argument is given *as typed*, so a relative invocation prints a
    # relative path — the tool never expands it into the absolute one.
    printed = invoke("no-such-corpus")[1]
    assert printed.startswith("no-such-corpus: not a directory")
    assert "/home/" not in printed and "/Users/" not in printed


def test_no_report_line_carries_the_absolute_root_it_was_given(tmp_path):
    root = corpora.one_unit(tmp_path / "c", blocks=[])
    printed = invoke(str(root))[1]
    assert str(root) not in printed
