"""E11's acceptance for the delivery skill, asserted end to end rather than described.

⛔ The subjects here are the two documents the skill ships — `SKILL.md` and
the generated capability index the package ships beside it — plus
one whole plan built through the public surface. The per-module refusals are
next door; what lives here is the claim that the pieces compose into the thing
the epic asked for.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

from studyforge.skills import delivery
from studyforge.skills.delivery import JIRA, Carrier, concentration, export
from tests.harness.sources import KNOWN_SOURCES, named_sources
from tests.studyforge.skills.delivery import plans
from tests.support import repository_root


def skill_document() -> str:
    return (Path(delivery.__file__).parent / "SKILL.md").read_text("utf-8")


def index_document() -> str:
    """The index the package ships, read the way an installed package reads it."""
    return delivery.packaged_index()


def first_command() -> list[str]:
    """The procedure's step-1 command's arguments, read out of `SKILL.md` and never retyped."""
    step = re.search(r"^### 1\..*?^```\n(.*?)^```", skill_document(), re.S | re.M)
    assert step, "step 1 carries no command"
    words = step.group(1).replace("\\\n", "").split()
    assert words[:2] == ["python3", "-m"] and len(words) == 3, words
    return words[1:]


# --- R19: the index is generated, and says so --------------------------------


def test_the_index_says_it_is_generated_so_nobody_edits_it_by_accident():
    assert delivery.BANNER in index_document()


# --- R20: nothing here cites a path inside the extraction source ------------


def extraction_source() -> re.Pattern[str]:
    for corpus, pattern, _ in KNOWN_SOURCES:
        if corpus == "the extraction source":
            return pattern
    raise AssertionError("the registry no longer names the extraction source")


def test_nothing_this_skill_ships_cites_a_path_inside_the_extraction_source():
    # ⛔ R20 read as the epic states it. The check is on the PATH shape, since
    # a document is allowed to say the repository exists and this one does not
    # even do that.
    slug = extraction_source().pattern
    citation = re.compile(rf"{slug}[/\\]\S", re.IGNORECASE)
    package = Path(delivery.__file__).parent
    for path in sorted(package.iterdir()):
        if path.is_dir():
            continue
        assert not citation.search(path.read_text("utf-8")), f"{path.name} cites a path inside it"


def test_the_instrument_that_checks_for_a_source_name_actually_fires():
    # ⛔ The PLANTED reading, for the two checks below. `named_sources`
    # returning `[]` for everything would make both of them pass while checking
    # nothing, and that is the exact failure the impossible reading caught three
    # times in the last skill to ship. So it is shown finding one first.
    planted = "a study corpus built from a CodeSignal export"
    found = named_sources(planted)
    assert [corpus for _, corpus, _ in found] == ["the extraction source"]
    assert named_sources("a study corpus built from an export") == []


def test_the_procedure_names_no_source_at_all():
    # ⚠️ Stronger than R20 asks, and matched to what every other SKILL.md in
    # this tree already does: none of them names a corpus.
    assert named_sources(skill_document()) == []


def test_no_module_in_this_package_names_a_source():
    # ⛔ R1's prose form. The product floor sweeps `src/**/*.py` itself; this
    # asserts it here too, so a failure names this package.
    package = Path(delivery.__file__).parent
    for module in sorted(package.glob("*.py")):
        assert named_sources(module.read_text("utf-8")) == [], module.name


# --- every command the procedure gives is one that actually runs ------------


def test_every_module_the_procedure_runs_can_be_imported():
    document = skill_document()
    named = set(re.findall(r"from ([\w.]+) import", document))
    named |= set(re.findall(r"python3 -m ([\w.]+)", document))
    assert named, "the procedure gives no command at all"
    for name in sorted(named):
        assert importlib.util.find_spec(name) is not None, f"no module {name}"


def test_every_name_the_procedure_imports_is_on_the_packages_surface():
    # ⛔ A procedure that imports a name the package does not export sends its
    # reader to an ImportError on the first step they take.
    imported: set[str] = set()
    for names in re.findall(
        r"from studyforge\.skills\.delivery import ([^\n;\"]+)", skill_document()
    ):
        imported.update(part.strip() for part in names.split(",") if part.strip())
    assert imported
    assert imported <= set(delivery.__all__), imported - set(delivery.__all__)


def test_the_procedure_offers_no_console_script_that_does_not_exist():
    # ⚠️ `studyforge validate` is not a console command — `pyproject.toml`
    # documents the omission deliberately, and two shipped SKILL.md files name
    # it anyway. Every command here is spelled the way it runs.
    for fence in re.findall(r"^```\n(.*?)^```", skill_document(), re.S | re.M):
        for line in fence.splitlines():
            assert not line.strip().startswith("studyforge "), line


def test_the_procedures_first_command_runs_and_prints_the_index(tmp_path):
    # ⛔ The live reading: the command a reader types first, typed.
    # ⭐ read out of `SKILL.md` rather than retyped here, so the procedure
    # and this test cannot drift apart with the test still green.
    # ⭐ Run from a directory that holds no plan document at all, and
    # compared byte for byte — never stripped.
    done = subprocess.run(  # noqa: S603
        [sys.executable, *first_command()],
        cwd=tmp_path,
        capture_output=True,
        env={"PYTHONPATH": str(repository_root() / "src"), "PATH": "/usr/bin:/bin"},
        check=False,
    )
    assert done.returncode == 0, done.stderr.decode("utf-8", "replace")
    assert done.stdout == index_document().encode("utf-8")


def test_the_procedure_never_sends_a_planner_to_a_plans_documents():
    # ⛔ The skill reads the package, and its procedure names
    # no directory a plan's documents live in.
    assert "docs/tasks" not in skill_document()


# --- the whole plan, through the public surface only ------------------------


def test_a_plan_reaches_a_document_an_export_and_a_risk_report():
    index = plans.index()
    plan = plans.backlog().checked(index)
    document = "\n".join(plan.lines())
    assert document.startswith("# Delivery plan — a repository of teaching prose")
    assert "**Critical path.**" in document
    assert "## This corpus finishes at M2" in document

    exported = export(plan, JIRA)
    assert exported.splitlines()[0].startswith("Issue key")
    assert len(exported.splitlines()) == len(plan.tasks) + 1

    report = concentration(plan.tasks, outside=(Carrier("RS-02", "the framework", 6),))
    assert "outside this repository" in report.headline()


def test_every_task_in_a_checked_plan_ends_in_something_a_person_is_shown():
    # ⭐ E11's clause, asserted over the whole plan rather than trusted to the
    # constructor that made each task.
    for task in plans.backlog().checked(plans.index()).tasks:
        assert task.demonstrable.strip()


def test_every_acceptance_clause_in_a_checked_plan_names_its_instrument():
    for task in plans.backlog().checked(plans.index()).tasks:
        for clause in task.acceptance:
            assert clause.instrument


def test_the_plan_a_reader_gets_is_the_plan_the_export_renders():
    plan = plans.backlog().checked(plans.index())
    document = "\n".join(plan.lines())
    for row in export(plan, JIRA).splitlines()[1:]:
        assert f"### {row.split(',')[0]} —" in document


def test_a_plan_that_contradicts_the_index_never_reaches_a_document():
    # ⛔ The negative control for the whole walkthrough. Without it, a
    # walkthrough that only ever sees green cannot tell you the green means
    # anything.
    from studyforge.skills.delivery import Milestone, PlanRefused

    broken = plans.backlog(
        milestones=(
            Milestone("C1", "first", (plans.reading_task("C-01", depends_on=("RS-20",)),), "M1"),
        )
    )
    with pytest.raises(PlanRefused, match="waits on RS-20, which lands at M5"):
        broken.checked(plans.index())
