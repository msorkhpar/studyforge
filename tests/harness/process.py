"""`REL-02`: which tests police the PROCESS, so the product suite runs without it.

**What it does.** Declares, in one place, every test that guards how the framework was BUILT —
the tooling, the board, the epics, the rubric, a convention whose home is still being sorted —
rather than what the framework DOES. The root `conftest.py` reads this module: with the tooling
present every declared test runs exactly as before; with it absent, a declared FILE is not
collected and a declared TEST is skipped with its reason, and the run says how many.

**How you use it.** `declared(nodeid)` returns the reason a test is process, or `None`.
`files()` is the whole-file population. `present(root)` says whether the process is here.
⭐ This list is what `REL-10` acts on, entry for entry, and each reason says which act: an entry
whose reason says it STAYS is edited in the removal commit; every other one MOVES to the archive
branch. `DEFERRED` is neither — product files another task re-points (`REL-06`).

**Depends on.** Nothing but the standard library. ⛔ It imports no tooling: it is the list of
what does.

## ⛔ Why a declaration and not a marker in each file

⚠️ **A file that imports the tooling at its top cannot be marked from inside**: it fails at
import, before any mark is read, in exactly the checkout the mark exists for. ⭐ So the list
lives outside the files it names, and `tests/test_product_stands_alone.py` refuses a product
test that imports the tooling unless it is named here.

## ⛔ Why "the tooling is present" is the one switch

⭐ With the tooling present nothing changes: every gate runs every test it ran before, so the
merge authority is untouched. ⛔ Absence is read off the tooling directory ONLY, never off a
missing document: a deleted epic in a working checkout must still turn its test red, and would
not if a missing document were read as "the process is absent".
"""

from __future__ import annotations

from pathlib import Path

#: The directory whose presence means the process is in this checkout.
TOOLING = "tools"

#: The marker every declared test carries, and what it means.
MARKER = "process"
MARKER_MEANS = (
    "polices the process (tooling, board, epics, rubric), not the product; "
    "declared in tests/harness/process.py and moved with the tooling by REL-10"
)

#: The reasons, named once so each entry says which kind it is.
EPIC = "reads an epic under docs/tasks/, which REL-11 trims to high-level design"
RUBRIC = "reads the review rubric, which REL-08 sorts and REL-10 archives"
BOARD = "reads a process convention and the board archive, which REL-10 archives"
TOOLING_RUN = "runs or imports the tooling itself, which REL-10 archives"
TWIN = "compares a product-side copy with its tooling original while both exist"
HOME = "reads docs/conventions/commanded-pages.md, whose home REL-08 decides"
HANDOFF = "reads a handoff under docs/tasks/handoffs/, which REL-10 archives"
#: ⭐ `REL-06`: the delivery skill's generator read over THIS repository's epics. The shipped
#: index stands without them; these readings do not, and `REL-11` decides what replaces them.
LIVE_EPICS = (
    "regenerates the delivery skill's index from the epics under docs/tasks/, whose task "
    "blocks REL-11 trims; the shipped index stands without them, this reading does not"
)
#: ⭐ The one kind that does NOT move: a product test whose DATA names the tooling as part of
#: the repository. `REL-10`'s removal commit drops the tooling's row, and the test stays.
LAYOUT = (
    "names the tooling as part of the repository's layout; it STAYS, and REL-10's removal "
    "commit drops the tooling's row from its data"
)
ENFORCER = (
    "names a tooling test as a fixture enforcer; it STAYS, and REL-10 re-points the entry at "
    "that test's product twin, tests/floor/personal_data/test_registry.py"
)

#: ⛔ Whole FILES that are process. Never collected when the tooling is absent.
FILES: dict[str, str] = {
    "tests/test_acceptance_clauses.py": EPIC,
    "tests/test_round_mint_collision_rule.py": BOARD,
    "tests/test_rubric_exit_code_forms.py": RUBRIC,
    "tests/docker/test_dev_check_rubric_form.py": RUBRIC + "; and imports tools.mergegate",
    "tests/test_quality_floor.py": TOOLING_RUN,
    "tests/test_consumer_side_contract.py": HOME,
    "tests/test_process_twins.py": TWIN,
    "tests/test_floor_twins.py": TWIN,
}

#: ⛔ Single TESTS inside an otherwise product file. Skipped, with the reason, when absent.
#: ⭐ An entry names a test function; a `[id]` suffix narrows it to one parametrisation.
TESTS: dict[str, str] = {
    "tests/test_process_starts.py::test_the_epic_names_each_site_in_the_runners_definition": EPIC,
    "tests/test_process_starts.py::test_the_epic_states_the_narrowed_sentence_and_its_exceptions": (
        EPIC
    ),
    "tests/test_fixture_exercise_rule.py::"
    "test_each_document_cites_section_7_for_the_file_only_record[e06]": EPIC,
    "tests/studyforge/corpus/manifest/test_media.py::test_the_example_the_epic_publishes_parses": (
        EPIC
    ),
    "tests/studyforge/corpus/manifest/test_media.py::"
    "test_the_epic_says_which_version_its_example_needs": EPIC,
    "tests/gate_coverage/test_coverage.py::"
    "test_every_named_tree_is_populated_so_the_bound_is_not_vacuous": LAYOUT,
    "tests/test_fixture_sweeps.py::test_the_enforcers_are_named_in_the_code_and_state_why": (
        ENFORCER
    ),
    "tests/test_fixture_sweeps.py::test_no_enforcer_imports_the_seam": ENFORCER,
    "tests/test_fixture_sweeps.py::test_the_enforcers_still_read_the_tree_themselves": ENFORCER,
    "tests/studyforge/skills/delivery/test_walkthrough.py::"
    "test_the_shipped_index_is_exactly_what_the_generator_produces_today": LIVE_EPICS,
    "tests/studyforge/skills/delivery/test_walkthrough.py::"
    "test_every_row_of_the_index_names_a_task_that_is_in_an_epic_document": LIVE_EPICS,
    "tests/studyforge/skills/delivery/test_walkthrough.py::"
    "test_the_index_is_the_only_thing_a_planner_has_to_read_about_the_framework": LIVE_EPICS,
    "tests/studyforge/skills/delivery/test_capability.py::"
    "test_every_task_in_every_epic_document_reaches_the_index": LIVE_EPICS,
    "tests/studyforge/skills/delivery/test_capability.py::"
    "test_the_derivation_the_document_prints_is_computed_and_not_typed": LIVE_EPICS,
    "tests/studyforge/skills/delivery/test_capability.py::"
    "test_every_milestone_section_holds_exactly_the_capabilities_at_it": LIVE_EPICS,
    "tests/studyforge/skills/delivery/test_capability.py::"
    "test_the_live_sections_print_in_the_order_the_task_index_declares": LIVE_EPICS,
    "tests/studyforge/skills/delivery/test_capability.py::"
    "test_no_capability_in_the_live_index_lost_its_area": LIVE_EPICS,
    "tests/studyforge/skills/delivery/test_capability.py::"
    "test_no_side_the_index_reports_is_outside_the_closed_vocabulary": LIVE_EPICS,
    "tests/studyforge/skills/delivery/test_capability.py::"
    "test_the_three_sides_partition_the_index": LIVE_EPICS,
    "tests/studyforge/skills/delivery/test_capability.py::"
    "test_no_component_is_ever_NAMED_in_what_the_index_renders": LIVE_EPICS,
    "tests/studyforge/skills/delivery/test_capability.py::"
    "test_the_split_by_side_the_document_prints_is_derived_too": LIVE_EPICS,
    "tests/studyforge/skills/delivery/test_findings_log.py::"
    "test_the_question_is_the_sorts_own_words": HANDOFF,
}

#: ⚠️ PRODUCT files that still import the tooling and are ANOTHER task's to re-point — never
#: process, never marked, and not collected without the tooling only so a run from the suite's
#: root can collect at all. `tests/test_product_stands_alone.py` fails once an entry stops
#: needing to be here, so none outlives its reason.
#: ⭐ Empty since `REL-06` re-pointed the delivery skill's tests; kept so the next file that
#: needs an excuse is named here rather than excused silently.
DEFERRED: dict[str, str] = {}


def present(root: Path) -> bool:
    """Report whether the tooling — and so the process — is in the checkout at `root`."""
    return (Path(root) / TOOLING).is_dir()


def files() -> frozenset[str]:
    """Return every declared whole-file process test, repository-relative."""
    return frozenset(FILES)


def uncollected() -> frozenset[str]:
    """Return every file a checkout without the tooling does not collect: process, or deferred."""
    return frozenset(FILES) | frozenset(DEFERRED)


def declared(nodeid: str) -> str | None:
    """Return why the test `nodeid` is process, or `None` when it is product.

    ⭐ A file entry covers every test in the file; a test entry covers the function and each
    of its parametrisations, unless the entry itself names one with `[id]`.
    """
    path = nodeid.partition("::")[0]
    if path in FILES:
        return FILES[path]
    for entry, reason in TESTS.items():
        if nodeid == entry or (not entry.endswith("]") and nodeid.startswith(entry + "[")):
            return reason
    return None


def population_line(present: bool) -> str:
    """Return the summary line saying whether this run reached the declared process tests.

    ⛔ Printed on every run, like the unreachable population: a product suite that went green
    WITHOUT its process tests must say so in the same summary that says green.
    """
    declared = (
        f"{len(FILES)} declared process file(s), {len(TESTS)} declared test(s) and "
        f"{len(DEFERRED)} deferred product file(s)"
    )
    if present:
        return f"process population: the tooling is present, so none of the {declared} is held back"
    return (
        f"process population: the tooling is ABSENT, so the {declared} did not run — "
        f"the files were not collected and the tests were skipped (tests/harness/process.py)"
    )
