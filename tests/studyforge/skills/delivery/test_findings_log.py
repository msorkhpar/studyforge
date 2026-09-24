"""Mirror of `src/studyforge/skills/delivery/findings_log.py` (R12), and `W346`'s clauses.

⛔ `W346`: a conversion is obliged to write its findings log. Three clauses,
each asserted both ways — the procedure names the log, each finding carries a
disposition slot, and a run that ends without a log is refused, never green.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

from studyforge.skills import adapter, delivery, documents, onboarding
from studyforge.skills.delivery import (
    ANSWERS,
    LOG,
    QUESTION,
    Claim,
    Disposition,
    Entry,
    Finding,
    FindingsLog,
    LogRefused,
    closing,
)
from studyforge.skills.onboarding import pin
from studyforge.validate.source import SKIP_DIRS
from tests.support import repository_root

#: A commit-shaped value for a stub; fabricated, never a real ref.
COMMIT = "0" * 40


def finding(id: str = "INT-19/1", marker: str = "structural") -> Finding:
    claims = () if marker == "none" else (Claim("seen on the corpus", measured="counted"),)
    return Finding(id=id, marker=marker, says="the scaffold wrote no ignore rule", claims=claims)


def rendered(*entries: Entry, run: str = "a conversion") -> str:
    return "\n".join(FindingsLog(run=run, entries=entries).lines()) + "\n"


def skill(package: ModuleType) -> str:
    return (Path(str(package.__file__)).parent / "SKILL.md").read_text("utf-8")


def bare_fences(text: str) -> list[str]:
    """Every fence with no info string, paired open-to-close rather than by regex."""
    found: list[str] = []
    body: list[str] | None = None
    info = ""
    for line in text.splitlines():
        if not line.startswith("```"):
            if body is not None:
                body.append(line)
        elif body is None:
            body, info = [], line[3:].strip()
        else:
            if not info:
                found.append("\n".join(body))
            body = None
    return found


def closing_command(text: str) -> str:
    """The procedure's closing command, read out of the document and never retyped."""
    for fence in bare_fences(text):
        joined = fence.replace("\\\n", "").strip()
        if "closing(" in joined:
            opening = 'python3 -c "'
            assert joined.startswith(opening) and joined.endswith('"'), joined
            return joined[len(opening) : -1]
    raise AssertionError("the procedure gives no closing command")


# --- the disposition slot: the catalogue's admission question ---------------


def test_the_slot_asks_the_question_the_catalogue_refuses_on():
    # ⚠️ The catalogue states the RULE, not the question: its table refuses
    # "anything a skill could generate". The question is the sort's own words,
    # which the next test reads where the sort was written.
    catalogue = (repository_root() / "docs/integration-catalogue.md").read_text("utf-8")
    assert "Anything a skill could generate" in catalogue


def test_the_question_is_the_sorts_own_words():
    # ⚠️ Reads a handoff, which leaves the main line with the process, so
    # `tests/harness/process.py` declares this one test and the archive keeps it.
    sort = (repository_root() / "docs/tasks/handoffs/QA-04.md").read_text("utf-8")
    assert QUESTION in sort


def test_every_answer_in_the_closed_set_is_accepted():
    for answer in ANSWERS:
        why = "" if answer == "open" else "the pin check is generated"
        assert Disposition(answer, why).answer == answer


def test_a_fourth_answer_is_refused():
    with pytest.raises(LogRefused, match="one of yes, no, open"):
        Disposition("maybe", "somebody should look")


@pytest.mark.parametrize(("answer", "why"), [("yes", ""), ("no", " "), ("open", "a reason")])
def test_a_settled_answer_carries_a_reason_and_an_open_one_does_not(answer, why):
    with pytest.raises(LogRefused, match="an `open` disposition carries no reason"):
        Disposition(answer, why)


def test_the_slot_starts_open():
    assert Entry(finding()).disposition == Disposition("open")


def test_an_entry_renders_its_finding_then_its_slot():
    lines = Entry(finding(), Disposition("yes", "the onboarding skill")).lines()
    assert lines[:-1] == finding().lines()
    assert lines[-1] == f"  - *{QUESTION}* **yes** — the onboarding skill"


def test_a_none_entry_carries_no_slot_because_it_writes_zero():
    none = finding("INT-19/1", "none")
    assert Entry(none).lines() == none.lines()


# --- the log refuses what it could not read back -----------------------------


def test_an_empty_log_is_refused_because_zero_is_a_none_finding():
    with pytest.raises(LogRefused, match="Zero is written as one `none` finding"):
        FindingsLog(run="a conversion", entries=())


def test_a_repeated_id_is_refused_by_name():
    with pytest.raises(LogRefused, match="appears twice: INT-19/2"):
        FindingsLog(run="r", entries=(Entry(finding("INT-19/2")), Entry(finding("INT-19/2"))))


def test_a_none_beside_a_real_finding_is_refused():
    with pytest.raises(LogRefused, match="stands beside a real one"):
        FindingsLog(run="r", entries=(Entry(finding()), Entry(finding("INT-19/2", "none"))))


def test_every_refusal_of_a_log_is_named_at_once():
    with pytest.raises(LogRefused) as raised:
        FindingsLog(run=" ", entries=())
    assert str(raised.value).startswith("2 refusals")


def test_a_log_that_can_be_read_back_is_accepted():
    log = FindingsLog(run="r", entries=(Entry(finding()), Entry(finding("INT-19/2"))))
    assert len(log.entries) == 2


# --- closing: a run that ends without a log is refused, never green ----------


def test_a_run_with_no_log_is_refused_and_the_refusal_names_where_it_belongs():
    with pytest.raises(LogRefused, match=re.escape(LOG)):
        closing(None)


def test_a_rendered_log_closes_and_reports_every_finding_and_its_answer():
    text = rendered(
        Entry(finding("INT-19/1"), Disposition("yes", "the adapter scaffold")),
        Entry(finding("INT-19/2"), Disposition("no", "the anchor is source-specific")),
        Entry(finding("INT-19/3")),
    )
    report = closing(text)
    assert report[:3] == ["INT-19/1  yes", "INT-19/2  no", "INT-19/3  open"]
    assert report[-1] == "open: 1 — the sort is not done"


def test_a_fully_sorted_log_says_so():
    text = rendered(Entry(finding(), Disposition("no", "a trap real material sets")))
    assert closing(text)[-1] == "open: 0 — every finding sorted"


def test_a_log_recording_nothing_closes_and_says_it_found_nothing():
    report = closing(rendered(Entry(finding("INT-19/1", "none"))))
    assert "none: the run recorded that it found nothing" in report


def test_a_finding_with_no_slot_is_refused_by_id():
    text = rendered(Entry(finding("INT-19/4")), Entry(finding("INT-19/5")))
    stripped = "\n".join(line for line in text.splitlines() if QUESTION not in line)
    with pytest.raises(LogRefused) as raised:
        closing(stripped)
    assert "INT-19/4 carries no disposition slot" in str(raised.value)
    assert "INT-19/5 carries no disposition slot" in str(raised.value)


def test_a_finding_with_two_slots_is_refused():
    text = rendered(Entry(finding()))
    doubled = text + Disposition("open").line() + "\n"
    with pytest.raises(LogRefused, match="carries 2 disposition slot"):
        closing(doubled)


def test_an_answer_outside_the_set_is_refused_when_read_back():
    text = rendered(Entry(finding())).replace("**open**", "**maybe**")
    with pytest.raises(LogRefused, match="answers 'maybe'"):
        closing(text)


def test_a_settled_answer_with_no_reason_is_refused_when_read_back():
    text = rendered(Entry(finding())).replace("**open**", "**yes**")
    with pytest.raises(LogRefused, match="does not match its reason"):
        closing(text)


def test_text_that_is_not_a_log_is_refused():
    with pytest.raises(LogRefused, match="does not open with"):
        closing("notes\n" + rendered(Entry(finding())))


def test_a_log_holding_no_finding_is_refused():
    with pytest.raises(LogRefused, match="carries no finding"):
        closing("# Findings log — a conversion\n")


def test_a_none_beside_a_real_finding_is_refused_when_read_back():
    text = rendered(Entry(finding())) + "\n" + "\n".join(finding("INT-19/9", "none").lines())
    with pytest.raises(LogRefused, match="stands beside a real one"):
        closing(text)


# --- where the log lives: a place that never makes the corpus invalid -------


def test_the_log_lives_in_a_directory_validate_skips():
    assert LOG.split("/")[0] in SKIP_DIRS


# --- clause 1: the procedure a corpus is pointed at names the log -----------


def test_the_stub_a_corpus_receives_points_at_a_procedure_that_names_the_log():
    # ⭐ The corpus's copy of the procedure is a GENERATED pointer; follow it to
    # the document it names — through the installed package's locator, the way
    # its command does — and read the log's place out of that document.
    assert "onboarding" in pin.SKILLS
    pointer = pin.stub("onboarding", COMMIT, "0.1.0")
    target = re.search(rf"^    {re.escape(pin.DOCUMENTS)} (\S+)$", pointer, re.MULTILINE)
    assert target, pointer
    procedure = documents.text(target.group(1))
    assert f"`{LOG}`" in procedure
    assert QUESTION in procedure


def test_the_adapter_hand_over_step_obliges_the_log_rather_than_a_message():
    assert "findings log" in skill(adapter)
    assert "onboarding skill's step 7" in skill(adapter)


def test_the_delivery_sort_starts_from_the_log_and_points_at_the_catalogue():
    # ⭐ The section's NAME is read out of the procedure, never typed here, so a
    # rewrite of that prose keeps this green exactly when the procedure and the catalogue
    # still agree — and a procedure that names no section at all is refused.
    text = skill(delivery)
    assert f"`{LOG}`" in text
    cited = re.search(r"the catalogue's own \*(.+?)\* section", text)
    assert cited, "the procedure no longer names the catalogue section a finished sort takes"
    catalogue = (repository_root() / "docs/integration-catalogue.md").read_text("utf-8")
    headings = [line for line in catalogue.splitlines() if line.startswith("## ")]
    assert any(cited.group(1) in heading for heading in headings), cited.group(1)


def test_both_procedures_close_on_the_same_command():
    assert closing_command(skill(onboarding)) == closing_command(skill(delivery))


def test_a_procedure_without_a_closing_command_is_caught():
    # ⭐ The other direction: the reader is shown to fail on a document without one.
    with pytest.raises(AssertionError, match="no closing command"):
        closing_command("```\npython3 -c \"print('done')\"\n```\n")


# --- clause 3: the procedure's own command, typed, refuses a run without a log


def run_closing(root: Path) -> subprocess.CompletedProcess[str]:
    source = str(repository_root() / "src")
    return subprocess.run(  # noqa: S603
        [sys.executable, "-c", closing_command(skill(onboarding))],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        env={"PYTHONPATH": source, "PATH": ""},
    )


def test_the_procedures_closing_command_refuses_a_run_that_wrote_no_log(tmp_path):
    done = run_closing(tmp_path)
    assert done.returncode != 0
    assert "LogRefused" in done.stderr
    assert LOG in done.stderr


def test_the_procedures_closing_command_passes_a_run_that_wrote_its_log(tmp_path):
    (tmp_path / ".studyforge").mkdir()
    (tmp_path / LOG).write_text(rendered(Entry(finding())), "utf-8")
    done = run_closing(tmp_path)
    assert done.returncode == 0, done.stderr
    assert "INT-19/1  open" in done.stdout


def test_the_procedures_closing_command_refuses_a_log_with_a_missing_slot(tmp_path):
    (tmp_path / ".studyforge").mkdir()
    text = rendered(Entry(finding()))
    (tmp_path / LOG).write_text(text.replace(Disposition("open").line(), ""), "utf-8")
    done = run_closing(tmp_path)
    assert done.returncode != 0
    assert "INT-19/1 carries no disposition slot" in done.stderr


# --- W345/1: the scaffold's file count is its own listing's, never typed ----

#: Typed counts of the scaffold's file set that `W345` made undercount.
TYPED_COUNTS = re.compile(r"\b(?:seven|eight) (?:generated|files|as generated)\b", re.I)


def test_no_skill_document_types_the_scaffolds_file_count():
    for package in (adapter, onboarding):
        assert not TYPED_COUNTS.findall(skill(package)), package.__name__


def test_the_skill_documents_point_at_the_scaffolds_own_listing():
    assert "the listing above is the count" in skill(adapter)
    assert "`scaffold(...).lines()`" in skill(onboarding)


def test_a_typed_count_is_caught():
    # ⭐ The other direction: the pattern fires on the sentence it replaced.
    assert TYPED_COUNTS.findall("The report names one file as yours and seven as generated.")
    assert TYPED_COUNTS.findall("**Eight files, seven generated:**")
