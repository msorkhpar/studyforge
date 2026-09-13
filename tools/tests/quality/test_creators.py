"""Mirror of `tools/quality/creators.py` (R12).

⛔ **Asserted in BOTH directions** (`W156`'s fifth clause): the pre-reorder plan names `TC-00`
and nothing else, and the members that reach their creator, one of them only transitively,
stay silent. ⚠️ The weak derivation is asserted PRINTED (the fourth clause), and the live plan
is asserted to carry a non-empty population with both derivations in it.
"""

from __future__ import annotations

import json

import tools.quality.creators as creators
from tests.support import assert_package_contract, repository_root
from tools.quality.creators import (
    RULE_CREATOR,
    check_owns_before_creator,
    creator_census,
    graph,
    placement,
    read,
    rows,
)

E12 = "docs/tasks/E12-toolchain-image.md"
E13 = "docs/tasks/E13-narration-service.md"
E11 = "docs/tasks/E11-skills-authoring.md"

LEGEND = (
    "`SF/` = `studyforge/` (this repo) · `CS/` = `CodeSignal/.pipeline/` · "
    "`TC/` = `code-server-toolchain` · `NS/` = `narrate-service`.\n"
)

WORKSPACE = {
    "workspace_api": 1,
    "components": [
        {"name": "studyforge", "where": "self", "status": "present"},
        {"name": "CodeSignal", "where": "sibling", "status": "present"},
        {"name": "code-server-toolchain", "where": "sibling", "status": "not-yet-created"},
        {"name": "narrate-service", "where": "sibling", "status": "present"},
    ],
}


def task(row: str, depends: str, owns: str, context: str = "~10k") -> str:
    """One epic entry in the shape the epics write it."""
    return (
        f"### {row} — a row\n**Milestone** **M5** · **Depends on** {depends} · **Team** solo\n"
        f"**Owns** {owns}\n**Context** {context}\n\nDefinition.\n\n---\n\n"
    )


def epic(title: str, repository: str, *entries: str) -> str:
    """An epic whose preamble declares its repository in bold code."""
    return f"# {title}\n\nIt becomes **`{repository}`**.\n\n---\n\n" + "".join(entries)


def sequence(*steps: str) -> str:
    """A README carrying step lines and the shorthand legend."""
    return "### M5 — It runs code\n\n" + "".join(f"{s}\n" for s in steps) + "\n" + LEGEND


BEFORE = sequence(
    "- **5.1** — TC-00, TC-01, SF-20",
    "- **5.2** — TC-02, TC-03",
    "- **5.3** — TC-05",
)

BEFORE_E12 = epic(
    "E12 — Toolchain image",
    "code-server-toolchain",
    task("TC-00", "—", "`TC/docker/minimal/`"),
    task("TC-01", "—", "`TC/` — the repository, `Dockerfile`, `seed/`"),
    task("TC-02", "TC-01", "the image's build-argument surface"),
    task("TC-03", "TC-01", "`TC/prime/` — the contract"),
    task("TC-05", "TC-02, TC-03", "`TC/docs/consuming.md`, `TC/consuming.json`"),
)


def plan(readme: str = BEFORE, **epics: str):
    """The graph of a plan handed as text, the workspace pinned as above."""
    return graph(readme, json.dumps(WORKSPACE), epics or {E12: BEFORE_E12})


def unsound(readme: str = BEFORE, **epics: str) -> dict[str, str]:
    """Every `Owns` member that is not sound, by id, with its verdict."""
    return {
        member.row.id: member.verdict
        for member in plan(readme, **epics).members
        if member.arm == "Owns" and member.verdict != "sound"
    }


def test_states_its_contract():
    assert_package_contract(creators, "tools.quality.creators")


# --- clause 5: both directions ---------------------------------------------------------------


def test_the_pre_reorder_plan_NAMES_TC_00_and_nothing_else():
    found = unsound()
    assert list(found) == ["TC-00"]
    assert "TC-01" in found["TC-00"] and "SAME step" in found["TC-00"]


def test_the_sound_members_stay_SILENT_including_one_reached_only_TRANSITIVELY():
    members = {member.row.id: member for member in plan().members if member.arm == "Owns"}
    assert {"TC-02", "TC-03", "TC-05"} <= set(members)
    assert all(members[row].verdict == "sound" for row in ("TC-02", "TC-03", "TC-05"))
    assert "TC-01" not in members, "the creator is not its own member"


def test_the_finding_names_the_row_at_its_heading(tmp_path):
    (tmp_path / "docs/tasks").mkdir(parents=True)
    (tmp_path / "docs/tasks/README.md").write_text(BEFORE, encoding="utf-8")
    (tmp_path / "workspace.json").write_text(json.dumps(WORKSPACE), encoding="utf-8")
    (tmp_path / E12).write_text(BEFORE_E12, encoding="utf-8")
    findings = check_owns_before_creator(tmp_path)
    assert [(f.path, f.rule) for f in findings] == [(E12, RULE_CREATOR)]
    assert BEFORE_E12.splitlines()[findings[0].line - 1].startswith("### TC-00")


# --- clause 1: the reorder settles the edge, and the predicate follows it ----------------------


def test_the_reorder_makes_TC_00_the_creator_and_TC_01_a_SOUND_member():
    readme = sequence("- **5.1** — TC-00, SF-20", "- **7.1** — TC-01", "- **7.2** — TC-02")
    text = epic(
        "E12 — Toolchain image",
        "code-server-toolchain",
        task("TC-00", "—", "`TC/` — it creates the repository — and `TC/docker/minimal/`"),
        task("TC-01", "TC-00", "`TC/` — the repository"),
        task("TC-02", "TC-01", "the image's build-argument surface"),
    )
    reading = plan(readme, **{E12: text})
    assert reading.creators["code-server-toolchain"].id == "TC-00"
    assert unsound(readme, **{E12: text}) == {}
    assert {m.row.id for m in reading.members if m.arm == "Owns"} == {"TC-01", "TC-02"}


# --- clause 2: the predicate, beyond the one instance ----------------------------------------


def test_an_EARLIER_step_creator_with_no_edge_is_named():
    readme = sequence("- **5.1** — TC-01", "- **5.2** — TC-03")
    text = epic(
        "E12",
        "code-server-toolchain",
        task("TC-01", "—", "`TC/`"),
        task("TC-03", "—", "`TC/prime/`"),
    )
    assert "EARLIER step" in unsound(readme, **{E12: text})["TC-03"]


def test_a_LATER_step_creator_is_named_even_with_an_edge():
    readme = sequence("- **5.1** — TC-03", "- **5.2** — TC-01")
    text = epic(
        "E12",
        "code-server-toolchain",
        task("TC-01", "—", "`TC/`"),
        task("TC-03", "TC-01", "`TC/prime/`"),
    )
    assert "LATER step" in unsound(readme, **{E12: text})["TC-03"]


def test_a_component_NOBODY_creates_is_named_when_absent_and_unwalked_when_present():
    text = epic(
        "E12",
        "code-server-toolchain",
        task("TC-03", "—", "`TC/prime/`"),
        task("CX-01", "—", "`CS/tools/`"),
    )
    readme = sequence("- **5.1** — TC-03, CX-01")
    assert "no row creates it" in unsound(readme, **{E12: text})["TC-03"]
    assert "CX-01" not in {member.row.id for member in plan(readme, **{E12: text}).members}


# --- clause 4: the weak derivation is declared ------------------------------------------------


def test_the_PROSE_derivation_is_printed_apart_from_the_PATH_one(tmp_path):
    (tmp_path / "docs/tasks").mkdir(parents=True)
    (tmp_path / "docs/tasks/README.md").write_text(BEFORE, encoding="utf-8")
    (tmp_path / "workspace.json").write_text(json.dumps(WORKSPACE), encoding="utf-8")
    (tmp_path / E12).write_text(BEFORE_E12, encoding="utf-8")
    census = creator_census(tmp_path)
    assert "4 Owns members, 1 read from epic prose, 1 unsound" in census[0]
    assert any(line.strip().startswith("TC-02 Owns prose inside") for line in census)
    assert any(line.strip().startswith("TC-03 Owns path inside") for line in census)


def test_a_cell_WITH_a_span_is_never_read_from_the_preamble():
    text = epic(
        "E13",
        "narrate-service",
        task("NS-01", "—", "`narrate-service` — the repository"),
        task("NS-05", "—", "`narrate/client.py` in `studyforge`"),
        task("NS-02", "NS-01", "the job API"),
    )
    readme = sequence("- **3.1** — NS-01", "- **3.2** — NS-02, NS-05")
    members = {m.row.id: m.derivation for m in plan(readme, **{E13: text}).members}
    assert members == {"NS-02": "prose"}


# --- clause 3: Context is a second arm, printed and never failing ------------------------------


def test_a_CONTEXT_read_prints_and_never_fails(tmp_path):
    reads = epic(
        "E11",
        "nothing-pinned",
        task("SK-09", "—", "the execution half", "~30k — `TC/consuming.json`, SK-07's output"),
    )
    (tmp_path / "docs/tasks").mkdir(parents=True)
    readme = sequence("- **5.1** — TC-01", "- **7.4** — SK-09")
    (tmp_path / "docs/tasks/README.md").write_text(readme, encoding="utf-8")
    (tmp_path / "workspace.json").write_text(json.dumps(WORKSPACE), encoding="utf-8")
    creator = epic("E12", "code-server-toolchain", task("TC-01", "—", "`TC/`"))
    (tmp_path / E12).write_text(creator, encoding="utf-8")
    (tmp_path / E11).write_text(reads, encoding="utf-8")
    assert check_owns_before_creator(tmp_path) == []
    line = next(line for line in creator_census(tmp_path) if "SK-09" in line)
    assert "Context path inside code-server-toolchain" in line and "never a finding" in line


# --- the parse -----------------------------------------------------------------------------


def test_placement_blanks_parentheses_and_spans_and_the_FIRST_step_line_wins():
    steps = placement(
        "- **5.1** — TC-00, **SF-20** · `SF-99`\n"
        "- **9.1** — JS-01, EX-00  *(needs TC-00's pinned image)*\n"
        "- **9.2** — TC-00\n"
        "- ⭐ **alongside 1.4** — **FND-08**\n"
    )
    assert steps == {"TC-00": "5.1", "SF-20": "5.1", "JS-01": "9.1", "EX-00": "9.1"}


def test_a_CANCELLED_row_is_not_read_and_a_wrapped_Owns_cell_is():
    text = (
        "### FND-05b — cancelled\n**Milestone** — · **Depends on** — · **Team** —\n"
        "**Owns** — **Context** —\n\n"
        "### SF-35 — wrapped\n**Milestone** **M2** · **Depends on** SF-02, *SF-05* · **Team** x\n"
        "**Owns** `corpus/manifest/content/`, and `KNOWN` in\n`version.py`\n**Context** ~5k\n"
    )
    [row] = rows("E01.md", text)
    assert (row.id, row.depends, row.context) == ("SF-35", ("SF-02", "SF-05"), "~5k")
    assert "`version.py`" in row.owns


def test_an_UNREAD_tree_says_so_and_finds_nothing(tmp_path):
    assert read(tmp_path) is None
    assert check_owns_before_creator(tmp_path) == []
    assert "not read" in creator_census(tmp_path)[0]


# --- the live plan ---------------------------------------------------------------------------


def test_the_live_plan_carries_a_population_with_both_derivations_and_is_sound():
    reading = read(repository_root())
    assert reading is not None
    owners = [member for member in reading.members if member.arm == "Owns"]
    assert {member.derivation for member in owners} == {"path", "prose"}
    assert "code-server-toolchain" in reading.creators
    assert check_owns_before_creator(repository_root()) == []
