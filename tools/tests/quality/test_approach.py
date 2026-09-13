"""Mirror of `tools/quality/approach.py` (R12).

⛔ **The acceptance is ASSERTED IN BOTH DIRECTIONS, and the silent arm is the
one worth planting.** `test_a_near_and_static_module_is_not_flagged` is the
whole argument of `W155`: a static module under an enforced ceiling is the
ceiling WORKING, and an instrument that named it would cry on its own
successes.

⭐ **`test_proximity_alone_would_flag_both` is the CONTROL that makes the pair
mean something.** ⚠️ A test that still passed with a proximity-only predicate
in place would not be testing the predicate at all, so that one asserts the
two fixtures are indistinguishable by proximity — same band, same ceiling —
and the pair above then separates them on growth alone.

⛔ **The fixtures are a REAL git repository with real commits** (`conftest`'s
argument, Ruling 191(b)): growth is read out of `git diff --numstat`, so a
stubbed history would certify the stub rather than the reader.

⭐ **The identity every fixture commits with is a PLACEHOLDER** (R7). A test
that committed as whoever runs the suite would write their git identity into a
fixture, which is the one datum this project refuses to record anywhere.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from tools.quality import CHECKS, NOTICES, approach, config
from tools.quality.approach import (
    CLASS_ANSWERED,
    CLASS_BORN,
    CLASS_MOVING,
    CLASS_STATIC,
    GROWTH_WAVES,
    NEAR_BAND,
    WAVE_CLOSE_OFFICE,
    Approach,
    approach_notice,
    closes_wave,
    growth_window,
    measured,
    near_modules,
    standing_split,
)
from tools.quality.board import unclaimed
from tools.workspace import git

#: ⛔ Fabricated, and `.invalid` is reserved by RFC 2606 so it reaches nobody.
AUTHOR = ("-c", "user.name=Example Author", "-c", "user.email=author@example.invalid")


def run(root: Path, *arguments: str) -> str:
    """One git command in `root`, with a placeholder identity, asserting success."""
    done = git(root, *AUTHOR, *arguments)
    assert done.returncode == 0, done.stdout + done.stderr
    return done.stdout.strip()


def module_of(lines: int, docstring: str = "") -> str:
    """A syntactically valid module of exactly `lines` physical lines."""
    head = f'"""{docstring}"""\n' if docstring else ""
    return head + "".join(f"x{n} = {n}\n" for n in range(lines - len(head.splitlines())))


def write(root: Path, relative: str, text: str) -> None:
    """Write `text` at `relative` under `root`, creating parents."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def close_wave(root: Path, number: int) -> None:
    """Land an empty merge whose subject closes a wave, as the release line does."""
    run(root, "checkout", "-q", "-B", f"chore/cto-round{number}")
    run(root, "commit", "-q", "--allow-empty", "-m", f"round {number}")
    run(root, "checkout", "-q", "main")
    run(
        root,
        "merge",
        "--no-ff",
        "-q",
        "-m",
        f"Merge chore/cto-round{number}: the wave measured green",
        f"chore/cto-round{number}",
    )


def repository(tmp_path: Path) -> Path:
    """⭐ The fixture the whole module turns on, and the two arms differ ONLY in growth.

    Both modules are source modules in the same band under the same 400-line
    ceiling. ⛔ `moving.py` reaches its size across the window; `static.py` is
    written at that size BEFORE the window opens and never touched again.
    """
    root = tmp_path / "repository"
    (root / "src" / "studyforge").mkdir(parents=True)
    run(root.parent, "init", "-q", "-b", "main", str(root))
    # --- before the window: both modules exist, both already in the band ---
    write(root, "src/studyforge/static.py", module_of(380))
    write(root, "src/studyforge/moving.py", module_of(340))
    run(root, "add", "-A")
    run(root, "commit", "-q", "-m", "the tree before the window")
    close_wave(root, 1)
    # --- inside the window: one module grows, one is born, one is untouched ---
    close_wave(root, 2)
    write(root, "src/studyforge/moving.py", module_of(380))
    write(root, "src/studyforge/newborn.py", module_of(390))
    run(root, "add", "-A")
    run(root, "commit", "-q", "-m", "growth, and a birth")
    close_wave(root, 3)
    close_wave(root, 4)
    return root


# --- the window (its two endpoints are the reading) -------------------------


def test_the_window_names_two_endpoints(tmp_path):
    root = repository(tmp_path)
    window = growth_window(root)
    assert window is not None
    base, head = window
    assert head == run(root, "rev-parse", "--short", "HEAD")
    assert base != head
    # ⛔ The window opens at the wave-closing merge `GROWTH_WAVES` back on the
    # first-parent line. Four waves closed here, so it opens at round 2 — and
    # the assertion is on the SUBJECT, because the subject is what picked it.
    assert run(root, "log", "-1", "--format=%s", base) == (
        f"Merge chore/cto-round{5 - GROWTH_WAVES}: the wave measured green"
    )


def test_an_ordinary_branch_merge_does_not_close_a_wave(tmp_path):
    # ⛔ The negative control for `closes_wave`. A wave is closed by a
    # round merge; a branch landing inside a wave must not slide the window,
    # or "three waves" would mean whatever number of branches happened to land.
    root = repository(tmp_path)
    before = growth_window(root)
    run(root, "checkout", "-q", "-B", "fix/W1")
    run(root, "commit", "-q", "--allow-empty", "-m", "work on a row")
    run(root, "checkout", "-q", "main")
    run(root, "merge", "--no-ff", "-q", "-m", "Merge fix/W1: a branch, not a wave", "fix/W1")
    after = growth_window(root)
    assert after[0] == before[0], "a branch merge slid the window"
    assert after[1] != before[1], "HEAD did not move, so the fixture proved nothing"


def test_a_tree_with_too_few_waves_reports_no_window_rather_than_a_span(tmp_path):
    # ⛔ A growth figure with no window is not a reading, so the reader returns
    # None rather than falling back to a default span nobody named.
    root = tmp_path / "shallow"
    (root / "src" / "studyforge").mkdir(parents=True)
    run(root.parent, "init", "-q", "-b", "main", str(root))
    write(root, "src/studyforge/thing.py", module_of(380))
    run(root, "add", "-A")
    run(root, "commit", "-q", "-m", "one commit, no wave has closed")
    assert growth_window(root) is None
    population, window = measured(root)
    assert window is None
    assert [item.growth for item in population] == [None]
    assert [item.classification for item in population] == [""]


def test_a_tree_that_is_not_a_repository_reports_no_window(tmp_path):
    (tmp_path / "src" / "studyforge").mkdir(parents=True)
    write(tmp_path, "src/studyforge/thing.py", module_of(380))
    assert growth_window(tmp_path) is None
    lines = approach_notice(tmp_path)
    assert any("NO GROWTH WINDOW" in line for line in lines)
    assert any("not a reading" in line for line in lines)
    # ⛔ And no growth figure anywhere in the block, in either sign.
    assert not any("growth      +" in line or "growth      -" in line for line in lines)


# --- R12 in BOTH directions, which is the acceptance ------------------------


def test_proximity_alone_would_flag_both(tmp_path):
    # ⭐ THE CONTROL. If the two fixtures differed by proximity, the pair below
    # would pass with a proximity-only predicate in place and would be testing
    # nothing. They are the same size, in the same band, under the same ceiling.
    root = repository(tmp_path)
    band = {item.path: item for item in near_modules(root)}
    assert band["src/studyforge/static.py"].headroom == band["src/studyforge/moving.py"].headroom
    assert band["src/studyforge/static.py"].ceiling == band["src/studyforge/moving.py"].ceiling
    assert 0 <= band["src/studyforge/static.py"].headroom <= NEAR_BAND


def test_a_near_and_moving_module_is_named(tmp_path):
    root = repository(tmp_path)
    population, window = measured(root)
    moving = next(item for item in population if item.path == "src/studyforge/moving.py")
    assert window is not None
    assert moving.growth == 40
    assert moving.classification == CLASS_MOVING
    assert moving.flagged
    assert any(
        "src/studyforge/moving.py" in line and CLASS_MOVING in line
        for line in approach_notice(root)
    )


def test_a_near_and_static_module_is_not_flagged(tmp_path):
    # ⛔ THE SILENT ARM, and it is the whole argument of `W155`: a static module
    # under an enforced ceiling is the ceiling WORKING, not a risk.
    root = repository(tmp_path)
    population, _ = measured(root)
    static = next(item for item in population if item.path == "src/studyforge/static.py")
    assert static.growth == 0
    assert static.classification == CLASS_STATIC
    assert not static.flagged
    assert not any(
        "src/studyforge/static.py" in line and CLASS_MOVING in line
        for line in approach_notice(root)
    )


def test_a_module_born_in_the_window_is_classed_apart(tmp_path):
    # ⭐ Growth equal to its own size is not growth. Without this arm the two
    # newest well-sized modules in a tree read as its two worst risks.
    root = repository(tmp_path)
    population, _ = measured(root)
    newborn = next(item for item in population if item.path == "src/studyforge/newborn.py")
    assert newborn.born
    assert newborn.growth == 390  # its whole length, which is why it is not "moving"
    assert newborn.classification == CLASS_BORN
    assert not newborn.flagged


# --- a standing split condition is ANSWERED, never re-reported --------------


def test_a_declared_split_condition_suppresses_the_flag(tmp_path):
    # ⛔ A module under a standing split condition has been decided about. An
    # instrument that flagged it would report a DECISION as a defect.
    root = repository(tmp_path)
    docstring = (
        "A module with a seam already named.\n\n"
        "Size exception: W148 splits this module at the seam its own row names,\n"
        "and it is deferred there rather than done here."
    )
    write(root, "src/studyforge/moving.py", module_of(380, docstring))
    run(root, "add", "-A")
    run(root, "commit", "-q", "-m", "declare the standing split condition")
    population, _ = measured(root)
    answered = next(item for item in population if item.path == "src/studyforge/moving.py")
    assert answered.answered == "W148"
    assert answered.growth > 0  # ⚠️ still moving, and still NOT flagged
    assert answered.classification == f"{CLASS_ANSWERED} W148"
    assert not answered.flagged
    assert any("answered by a standing split condition" in line for line in approach_notice(root))


def test_standing_split_reads_the_marker_line_only():
    text = module_of(10, "Thing.\n\nSize exception: W44 splits this module, deferred there.")
    assert standing_split(text, Path("thing.py")) == "W44"
    assert standing_split(module_of(10, "Thing."), Path("thing.py")) == ""
    # ⛔ A design claim citing a rule is not a deferral and buys no suppression.
    claim = module_of(10, "Thing.\n\nSize exception: one table, and R11 permits this.")
    assert standing_split(claim, Path("thing.py")) == ""


# --- the population is printed IN FULL before any scalar --------------------


def test_every_banded_module_is_printed_before_the_count(tmp_path):
    # ⛔ Rulings 123/128/140. "20 are near" and "2 are moving" are figures over
    # two different populations, and the whole of `W155` is that difference.
    root = repository(tmp_path)
    lines = approach_notice(root)
    population, _ = measured(root)
    census = next(index for index, line in enumerate(lines) if "PROXIMITY ALONE FLAGS" in line)
    printed = "\n".join(lines[:census])
    for item in population:
        assert item.path in printed
    assert f"PROXIMITY ALONE FLAGS {len(population)}" in lines[census]
    assert f"{sum(item.flagged for item in population)} {CLASS_MOVING}" in lines[census]


def test_the_census_names_all_three_classes(tmp_path):
    root = repository(tmp_path)
    census = next(line for line in approach_notice(root) if "PROXIMITY ALONE FLAGS" in line)
    for name in (CLASS_MOVING, "near and static", "born in the window"):
        assert name in census


def test_the_window_is_quoted_in_the_output(tmp_path):
    # ⛔ A growth figure with no window is not a reading, so the endpoints are
    # in the block a reader copies, not only in this module's docstring.
    root = repository(tmp_path)
    base, head = growth_window(root)
    assert any(f"window {base}..{head}" in line for line in approach_notice(root))


# --- what it must NOT become ------------------------------------------------


def test_the_approach_is_a_notice_and_never_a_check():
    # ⛔ R11's ceiling is the build failure. A second hard gate below the first
    # would make the real one unreachable.
    assert approach_notice in NOTICES
    assert approach_notice not in CHECKS
    assert all(isinstance(line, str) for line in approach_notice(Path(".")))


def test_a_module_over_its_ceiling_is_not_in_the_band(tmp_path):
    # ⛔ It is `check_sizes`'s finding already; printing it here would report
    # one defect twice and make the notice read as a second gate.
    root = tmp_path / "over"
    (root / "src" / "studyforge").mkdir(parents=True)
    write(root, "src/studyforge/over.py", module_of(config.SOURCE_LINE_CEILING + 1))
    assert near_modules(root) == []


def test_the_notice_never_tells_anybody_to_trim(tmp_path):
    # ⛔ The remedy for a module approaching its ceiling is a SPLIT at a named
    # seam. A ceiling is not a budget (Ruling 261).
    root = repository(tmp_path)
    block = "\n".join(approach_notice(root))
    assert "A CEILING IS NOT A BUDGET" in block
    assert "SPLIT at a named seam" in block
    assert "never a trim" in block


# --- the shapes the classification has to get right -------------------------


def test_an_unmeasured_module_is_not_a_static_one():
    # ⚠️ `None` is not zero: "I cannot measure this" must never arrive as
    # "this did not move".
    unmeasured = Approach(headroom=10, path="a.py", lines=390, ceiling=400)
    assert unmeasured.growth is None
    assert unmeasured.classification == ""
    assert not unmeasured.flagged
    assert " ?" in unmeasured.line()


def test_a_shrinking_module_is_static_not_moving():
    shrunk = Approach(headroom=10, path="a.py", lines=390, ceiling=400, growth=-40)
    assert shrunk.classification == CLASS_STATIC
    assert not shrunk.flagged


def test_the_band_is_the_minted_width_and_the_window_the_minted_depth():
    # ⭐ Both figures come from `docs/tasks/rows/W155.md` rather than from here,
    # so this population is comparable with the one the row argues about.
    assert NEAR_BAND == 60
    assert GROWTH_WAVES == 3


# --- `W245`: a wave close is the WHOLE round name, `OFFICE` imported ---------

#: ⛔ The four topic branches the row measured under the prefix, and the two
#: shapes `W136` names: a developer branch containing the office word, and a
#: round number that is a prefix of another.
TOPIC = [
    "Merge chore/cto-round17-close: Ruling 52, and the round's closing state",
    "Merge chore/cto-round31-corrections: the two changes po-round25 was approved after",
    "Merge chore/cto-round34-rubric: Rulings 121-122",
    "Merge chore/cto-round49-annotation: Ruling 192",
    "Merge fix/W99-cto-round-guard: a developer's branch",
    "Merge branch 'chore/cto-round5'",
    "Merge chore/cto-round: no number",
]


@pytest.mark.parametrize("subject", TOPIC)
def test_a_topic_branch_inside_the_prefix_is_not_a_close(subject):
    assert not closes_wave(subject), subject


@pytest.mark.parametrize(
    "subject",
    ["Merge chore/cto-round72: a merge order", "Merge chore/cto-round3 (CTO round 3): x"],
)
def test_a_round_branch_is_a_close(subject):
    assert closes_wave(subject), subject


def test_the_population_is_cto_rounds_and_a_po_round_is_not_silently_added():
    # ⚠️ `W245/1`: no ruling names a close's office. `W155` shipped over `cto`,
    # and a widening is a population change that must go RED here, not pass.
    assert WAVE_CLOSE_OFFICE == "cto"
    assert not closes_wave("Merge chore/po-round79 (PO round 79): W249 closed")


def test_the_pattern_is_unclaimeds_office_imported_and_never_retyped(monkeypatch):
    # ⛔ Identity, and then BEHAVIOUR: a retyped copy under any other name keeps
    # reading rounds as closes after `OFFICE` is swapped for a pattern that
    # matches nothing, so this goes RED on the copy whatever it is called.
    assert approach.OFFICE is unclaimed.OFFICE
    assert closes_wave("Merge chore/cto-round72: x")
    monkeypatch.setattr(approach, "OFFICE", re.compile(r"(?!)(cto)"))
    assert not closes_wave("Merge chore/cto-round72: x")


def test_the_source_imports_office_and_spells_no_branch_of_its_own():
    # ⛔ PLANTED AND SURVIVED without this (`W245/3`): `OFFICE = re.compile(<the
    # same pattern>)` retyped IN `approach.py` passes the identity check above,
    # because `re` caches compiled patterns and returns the SAME object. So the
    # import is read off the SOURCE: imported once, never assigned, no `re`, and
    # no string outside a docstring that spells a `chore/` branch.
    tree = ast.parse(Path(approach.__file__).read_text(encoding="utf-8"))
    imported = [
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "tools.quality.board.unclaimed"
        for alias in node.names
    ]
    assert imported == ["OFFICE"]
    assigned = [
        target.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign | ast.AnnAssign)
        for target in (node.targets if isinstance(node, ast.Assign) else [node.target])
        if isinstance(target, ast.Name)
    ]
    assert "OFFICE" not in assigned
    modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert "re" not in modules
    docstrings = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Module | ast.FunctionDef | ast.ClassDef)
        and node.body
        and isinstance(node.body[0], ast.Expr)
    }
    spelled = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
        and "chore/" in node.value
    ]
    assert spelled == []


def test_a_topic_merge_under_the_prefix_does_not_slide_the_window(tmp_path):
    # ⛔ The row's measured shape on a real history: `chore/cto-round17-close`
    # merged three times after its round closed. Under the prefix each slid the
    # window by one wave.
    root = repository(tmp_path)
    before = growth_window(root)
    for n in range(GROWTH_WAVES):
        run(root, "checkout", "-q", "-B", "chore/cto-round4-close")
        run(root, "commit", "-q", "--allow-empty", "-m", f"topic {n}")
        run(root, "checkout", "-q", "main")
        subject = f"Merge chore/cto-round4-close: ruling {n}"
        run(root, "merge", "--no-ff", "-q", "-m", subject, "chore/cto-round4-close")
    after = growth_window(root)
    assert after[0] == before[0], "a topic branch under the round prefix slid the window"
    assert after[1] != before[1], "HEAD did not move, so the fixture proved nothing"
