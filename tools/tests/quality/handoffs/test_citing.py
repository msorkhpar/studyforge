"""Mirror of `tools/quality/handoffs/citing.py` (R12).

⛔ **Asserted in BOTH directions** (`W135`, the row's clause 3): a bare citation of
a tracked document in a new handoff is a finding, the same handoff with the
pointer is green, and a test name, a symbol, a sha or a command beside the same
tracked document is NOT a finding. ⭐ Every negative is `GOOD` with one line
added, in a tree where the cited document exists — so a quiet case and its loud
twin differ by exactly the citation's form.
"""

from __future__ import annotations

import re
import subprocess

import pytest

from tests.support import git, init_repository, repository_root
from tools.quality import CHECKS, NOTICES
from tools.quality.handoffs import bound_handoffs, check_handoffs, handoff_citations
from tools.quality.handoffs.citing import (
    CITATION_PIN,
    RULE_BARE,
    bare_citations,
    citation_findings,
    citation_lines,
    frozen_documents,
)
from tools.tests.quality.handoffs.support import GOOD, rules, write

ROW = "docs/tasks/rows/W99.md"


def cited(tmp_path, line):
    """`GOOD` with `line` added to its Decisions, beside a tracked row file."""
    target = tmp_path / ROW
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# W99\n", encoding="utf-8")
    write(tmp_path, "W99.md", GOOD.replace("**Decisions:** one.", f"**Decisions:** {line}"))


# --- clause 3: both directions, and the negative control --------------------


@pytest.mark.parametrize(
    "line",
    ["argued in `docs/tasks/rows/W99.md`.", "argued in rows/W99.md.", "see `../rows/W99.md#x`."],
)
def test_a_bare_citation_of_a_tracked_document_in_a_new_handoff_is_a_finding(tmp_path, line):
    cited(tmp_path, line)
    assert rules(tmp_path) == [RULE_BARE]


def test_the_same_citation_as_a_pointer_is_green(tmp_path):
    cited(tmp_path, "argued in [`docs/tasks/rows/W99.md`](../rows/W99.md).")
    assert rules(tmp_path) == []


@pytest.mark.parametrize(
    "line",
    [
        "asserted by `test_citing.py::test_the_same_citation_as_a_pointer_is_green`.",
        "the arm is `check_handoffs`, a symbol.",
        "measured at `b182a88`, a sha.",
        "read with `sed -n 1,5p docs/tasks/rows/W99.md`, a command.",
    ],
)
def test_a_test_name_a_symbol_a_sha_or_a_command_is_not_a_finding(tmp_path, line):
    # ⛔ The negative control, in the SAME tree where the bare form fires above.
    cited(tmp_path, line)
    assert rules(tmp_path) == []


def test_a_name_whose_target_is_absent_on_this_ref_is_not_a_finding(tmp_path):
    # ⭐ Ruling 308: the backticked name is right where the target does not exist.
    cited(tmp_path, "argued in `docs/tasks/rows/W98.md`, minted on another branch.")
    assert rules(tmp_path) == []


def test_a_fenced_citation_is_quoted_material_and_is_not_read(tmp_path):
    cited(tmp_path, "one.\n\n```text\ndocs/tasks/rows/W99.md\n```")
    assert rules(tmp_path) == []


def test_the_finding_names_the_pointer_to_write():
    documents = frozenset({ROW})
    text = "a line citing `docs/tasks/rows/W99.md`\n"
    assert bare_citations("docs/tasks/handoffs/W99.md", text, documents) == [
        (1, "docs/tasks/rows/W99.md", ROW)
    ]


# --- clause 2: the exemption is a REF, and it is structural -----------------


def test_a_frozen_handoff_with_a_bare_citation_is_not_read_and_a_new_one_is(tmp_path):
    cited(tmp_path, "argued in `docs/tasks/rows/W99.md`.")
    bound = bound_handoffs(tmp_path)
    assert len(bound) == 1
    relative = bound[0][0]
    assert citation_findings(tmp_path, bound, frozenset({relative})) == []
    assert [f.rule for f in citation_findings(tmp_path, bound, frozenset())] == [RULE_BARE]


def test_an_unreadable_pin_reads_every_handoff_as_new(tmp_path):
    # ⛔ Ruling 216's third answer fails CLOSED: no git here, so nothing is frozen.
    cited(tmp_path, "argued in `docs/tasks/rows/W99.md`.")
    assert frozen_documents(tmp_path) is None
    assert [f.rule for f in check_handoffs(tmp_path)] == [RULE_BARE]


def test_the_frozen_population_is_the_tree_at_the_pin_and_nothing_else(tmp_path):
    repository = init_repository(tmp_path / "repo")
    (repository / "old.md").write_text("# old\n", encoding="utf-8")
    identity = ["-c", "user.name=test", "-c", "user.email=test@example.invalid"]
    subprocess.run([git(), "add", "old.md"], cwd=repository, check=True)
    subprocess.run([git(), *identity, "commit", "-qm", "pin"], cwd=repository, check=True)
    pin = subprocess.run(
        [git(), "rev-parse", "HEAD"], cwd=repository, check=True, capture_output=True, text=True
    ).stdout.strip()
    (repository / "new.md").write_text("# new\n", encoding="utf-8")
    assert frozen_documents(repository, pin) == frozenset({"old.md"})
    assert frozen_documents(repository, "0" * 40) is None


def test_the_shipped_pin_is_a_full_sha_this_repository_can_read():
    assert re.fullmatch(r"[0-9a-f]{40}", CITATION_PIN)
    frozen = frozen_documents(repository_root())
    assert frozen is not None
    assert "docs/tasks/handoffs/W106.md" in frozen
    # ⛔ `W135/6`: the pin is the tree the rule LANDS in, so every handoff merged
    # before it is frozen — the three a pin at the cut read as new among them.
    assert {"docs/tasks/handoffs/W108.md", "docs/tasks/handoffs/W125.md"} <= frozen


def test_the_pin_is_an_ancestor_of_head():
    # ⭐ A pin outside HEAD's history (a typo, a rewritten line) is refused here.
    # ⚠️ It does NOT catch a handoff added before the rule landed and absent from
    # the pin — that survivor is declared in `citing.py`, gap 4.
    result = subprocess.run(
        [git(), "merge-base", "--is-ancestor", CITATION_PIN, "HEAD"],
        cwd=repository_root(),
        check=False,
    )
    assert result.returncode == 0, f"{CITATION_PIN} is not an ancestor of HEAD"


def test_the_exemption_is_load_bearing_on_the_shipped_tree():
    # ⛔ Ruling 309: a THRESHOLD that prints the figure, never a literal. If the
    # frozen records were read, the shipped tree would fire — so the green
    # shipped reading in `test_init.py` is the exemption working, not idling.
    root = repository_root()
    bound = bound_handoffs(root)
    unexempt = {f.path for f in citation_findings(root, bound, frozenset())}
    exempt = citation_findings(root, bound, frozen_documents(root))
    assert len(unexempt) > 0, f"{len(unexempt)} of {len(bound)}"
    assert exempt == [], "\n".join(str(finding) for finding in exempt)


# --- clause 5: the printed figure carries its denominator -------------------

_FIGURE = re.compile(r"^handoff citations: (\d+) of (\d+) new handoffs cite a tracked document")


def test_the_notice_prints_n_of_m(tmp_path):
    cited(tmp_path, "argued in `docs/tasks/rows/W99.md`.")
    line = citation_lines(tmp_path, bound_handoffs(tmp_path), frozenset())[0]
    assert _FIGURE.match(line).groups() == ("1", "1"), line


def test_an_empty_new_population_says_so(tmp_path):
    cited(tmp_path, "argued in `docs/tasks/rows/W99.md`.")
    bound = bound_handoffs(tmp_path)
    line = citation_lines(tmp_path, bound, frozenset({bound[0][0]}))[0]
    assert _FIGURE.match(line).groups() == ("0", "0"), line
    assert "EMPTY" in line
    assert "1 of 1 task and office handoffs are in the tree at the pin" in line


def test_an_unreadable_pin_is_printed_as_unread(tmp_path):
    cited(tmp_path, "argued in `docs/tasks/rows/W99.md`.")
    assert "could NOT be read" in handoff_citations(tmp_path)[0]


# --- clause 4 and clause 1: an arm, and the rule lands once -----------------


def test_it_is_an_arm_of_check_handoffs_and_a_notice_not_a_new_check():
    assert handoff_citations in NOTICES
    assert handoff_citations not in CHECKS
    assert not [check for check in CHECKS if check.__module__.endswith("citing")]


def test_the_rule_lands_once_in_the_agent_protocol():
    conventions = repository_root() / "docs/conventions"
    heading = "#### ⛔ Ruling 285(b) (CTO round 59)"
    sites = [
        path.name
        for path in sorted(conventions.glob("*.md"))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith(heading)
    ]
    assert sites == ["agent-protocol.md"]
