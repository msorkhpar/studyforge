"""R11's APPROACH to the ceiling, printed as a notice and never as a gate.

**What it does.** Reads every module within `NEAR_BAND` lines of its R11
ceiling, measures how much each GREW over a named window of waves, and prints
the population classified into the three classes that separate a risk from the
ceiling doing its job.

**How you use it.** `approach_notice(repo_root)` returns the lines, and it is
registered in `tools.quality.NOTICES`. `measured(root)` is the reading behind
them — the banded population with growth attached, and the window it was taken
over. Nothing here returns a `Finding` and nothing here moves an exit code.

**Depends on.** `dataclasses`, `pathlib`, `tools.quality.config`,
`tools.quality.size`, `tools.quality.board.unclaimed` for `OFFICE`, and
`tools.workspace.git`. Standard library and this
repository's own tooling; the git calls degrade rather than fail.

## ⛔ THE PREDICATE IS PROXIMITY × GROWTH, AND PROXIMITY ALONE IS THE DEFECT

⭐ **A static module sitting under an enforced ceiling is THE CEILING WORKING.**
⛔ An instrument that flagged it would cry on its own successes, and the figures
say how badly: at `7a7a178`, over the window this module names, **proximity
alone flags 20 modules and proximity × growth flags 0**. ⚠️ Those are two
figures over two different populations, which is the whole of `W155`.

## ⛔ AND THE THIRD CLASS IS THE ONE A NAIVE PREDICATE GETS WRONG

⭐ **A file BORN inside the window has growth equal to its own size, which is
not growth.** ⛔ Without that arm the project's two newest well-sized modules
report as its two worst risks — `tests/visual/test_host_environment.py` at
`+567` and `tools/quality/citations.py` at `+363` were exactly that shape in
the reading that minted `W155` (role `wt/po`, `82bff6d`, taken over THAT
reading's window and not this module's — quoted as context, never as a figure
this module reproduces).

## ⚠️ WHAT THIS MUST NOT BECOME

⛔ **A build failure.** R11's own ceiling is the build failure; a second hard
gate below the first makes the real one unreachable. ⛔ **And not a trim
instruction** — the answer to a module approaching its ceiling is a SPLIT at a
named seam, which is what every standing split condition on the board says.
⚠️ **A CEILING IS NOT A BUDGET** (Ruling 261): nothing here implies that a file
at `+0` with one line of headroom is healthier than one at `+33` with twenty.
It says only that the ceiling is holding the first and is about to be tested by
the second.

⭐ **`W273`: rounds of `WAVE_CLOSE_OFFICES` close waves in precedence**, so a
window never mixes two offices, and its line names the close its waves END at.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.quality import config
from tools.quality.board.unclaimed import OFFICE
from tools.quality.size import count_lines, module_docstring, row_ids, size_exception_marker_line
from tools.workspace import git

#: How close to its ceiling a module has to be before this notice reads it.
#: ⛔ Sixty lines, and the figure is the band `docs/tasks/rows/W155.md` was
#: minted over rather than one chosen here, so the population printed is
#: comparable with the population the argument was made about.
NEAR_BAND = 60

#: How many waves the growth window spans. ⛔ Three, because that is the width
#: the row states its own reading over, and a width chosen after seeing which
#: width produced a flag would not be a measurement.
GROWTH_WAVES = 3

#: Which offices' rounds close a wave, in PRECEDENCE order (`W273`, `W245/1`).
#: ⛔ The branch is read WHOLE with `OFFICE`, imported and never retyped (`W245`).
WAVE_CLOSE_OFFICES = ("cto", "po")

#: ⛔ The three classes the row requires be NAMED in the output, plus the
#: suppression that is not a class. ⭐ `ANSWERED` is a module whose own
#: docstring declares a split condition: the decision is taken and the row
#: named, so re-reporting it would print a decision as a defect.
CLASS_MOVING = "NEAR AND MOVING"
CLASS_STATIC = "near and static"
CLASS_BORN = "born in the window"
CLASS_ANSWERED = "answered — split condition"

#: The prefix every line of this notice carries, so the block is greppable out
#: of a floor run that prints six other notices.
TAG = "size approach:"


@dataclass(frozen=True)
class Round:
    """One office round on the first-parent line: its merge, its office, its branch."""

    sha: str
    office: str
    branch: str


@dataclass(frozen=True)
class Window:
    """The growth window, the close its waves END at, and other offices' rounds `after` it."""

    base: str
    head: str
    end: str
    office: str
    after: tuple[str, ...] = ()

    @property
    def current(self) -> bool:
        """Whether no other office's round has merged after the close the waves end at."""
        return not self.after


@dataclass(frozen=True, order=True)
class Approach:
    """One module inside the band, with everything the classification needs.

    ⚠️ `growth` is `None` when no window could be named, and `None` is not
    zero: *"I cannot measure this"* must never arrive as *"this did not move"*.
    Ordered by `headroom` first, so the population prints closest-to-the-line
    first whatever order the tree walk found it in.
    """

    headroom: int
    path: str
    lines: int
    ceiling: int
    growth: int | None = None
    born: bool = False
    answered: str = ""

    @property
    def classification(self) -> str:
        """The class this module falls in; `""` when no window could be named."""
        if self.answered:
            return f"{CLASS_ANSWERED} {self.answered}"
        if self.growth is None:
            return ""
        if self.born:
            return CLASS_BORN
        return CLASS_MOVING if self.growth > 0 else CLASS_STATIC

    @property
    def flagged(self) -> bool:
        """Whether this module is one the notice asks a reader to look at."""
        return self.classification == CLASS_MOVING

    def line(self) -> str:
        """One printed row: headroom, growth, size against ceiling, path, class."""
        growth = "?" if self.growth is None else f"{self.growth:+d}"
        return (
            f"{TAG}   headroom {self.headroom:>3}  growth {growth:>6}  "
            f"{self.lines:>3}/{self.ceiling:<3}  {self.path}  {self.classification}"
        )


def standing_split(text: str, path: Path) -> str:
    """Return the row id of a split condition the module DECLARES, or `""`.

    ⛔ **Declared in the module, because this package may not read the board**
    (`config.ROW_ID`'s own reason). A condition that stands only in
    `docs/tasks/BOARD.md` is invisible here by construction: the row that owns
    the split says so on the module's `Size exception:` marker line, or this
    notice cannot know and will keep reporting an answered module as a risk.
    """
    ids = row_ids(size_exception_marker_line(module_docstring(text, path)))
    return ids[0] if ids else ""


def near_modules(root: Path, band: int = NEAR_BAND) -> list[Approach]:
    """Every module within `band` lines of its ceiling, closest first, no growth yet.

    ⛔ A module **over** its ceiling is deliberately absent: it is already
    `check_sizes`'s finding, and a notice repeating it would print one defect
    twice and read as a second gate under the first.
    """
    found: list[Approach] = []
    for path in config.python_files(root):
        relative = config.relative(path, root)
        ceiling = config.ceiling_for(relative)
        text = path.read_text(encoding="utf-8")
        lines = count_lines(text)
        if 0 <= ceiling - lines <= band:
            found.append(
                Approach(
                    headroom=ceiling - lines,
                    path=relative,
                    lines=lines,
                    ceiling=ceiling,
                    answered=standing_split(text, path),
                )
            )
    return sorted(found)


def merged_branch(subject: str) -> str:
    """Return the branch a `Merge <branch>:` or `Merge <branch> (…):` subject names, or `""`."""
    words = subject.split(maxsplit=2)
    if len(words) < 2 or words[0] != "Merge":
        return ""
    return words[1].removesuffix(":")


def round_office(subject: str) -> str:
    """Return the office whose round branch a merge subject names, `OFFICE` WHOLE, or `""`."""
    match = OFFICE.fullmatch(merged_branch(subject))
    return match.group(1) if match else ""


def closes_wave(subject: str) -> bool:
    """Whether a first-parent merge subject can close a wave: a round of `WAVE_CLOSE_OFFICES`.

    ⛔ **`fullmatch`, never `startswith`** (`W136`, `W245`): a topic branch under
    the round prefix is not the round, and `chore/cto-round3` is not `…round39`.
    Which office's rounds DO close is `closing_office`'s, read off the history.
    """
    return round_office(subject) in WAVE_CLOSE_OFFICES


def rounds(told: str) -> list[Round]:
    """Every office round in a `%h<TAB>%s` log, newest first, each ROUND once (`W245/2`)."""
    seen: set[str] = set()
    found: list[Round] = []
    for line in told.split("\n"):
        if line.count("\t") != 1:
            continue
        sha, subject = line.split("\t")
        branch = merged_branch(subject)
        if closes_wave(subject) and branch not in seen:
            seen.add(branch)
            found.append(Round(sha, round_office(subject), branch))
    return found


def closing_office(found: list[Round], waves: int = GROWTH_WAVES) -> str:
    """Return the latest office with `waves` rounds merged after every earlier office's newest.

    ⛔ **Precedence, so a window never mixes two offices' rounds** (`W273`).
    """
    for rank in range(len(WAVE_CLOSE_OFFICES) - 1, 0, -1):
        mine = 0
        for item in found:
            if item.office in WAVE_CLOSE_OFFICES[:rank]:
                break
            mine += item.office == WAVE_CLOSE_OFFICES[rank]
        if mine >= waves:
            return WAVE_CLOSE_OFFICES[rank]
    return WAVE_CLOSE_OFFICES[0]


def growth_window(root: Path, waves: int = GROWTH_WAVES) -> Window | None:
    """Return the window, its endpoints as short refs, or `None` if it cannot be named.

    ⛔ **`None` rather than a default span.** A growth figure with no window is
    not a reading, so a tree that is not a repository, a git that will not
    answer, and a history holding fewer than `waves` wave-closing merges all
    produce no growth at all rather than a number a reader would go on to quote.
    """
    head = git(root, "rev-parse", "--short", "HEAD")
    told = git(root, "log", "--first-parent", "--merges", "--format=%h%x09%s", "HEAD")
    if head.returncode != 0 or told.returncode != 0:
        return None
    found = rounds(told.stdout)
    office = closing_office(found, waves)
    closes = [item for item in found if item.office == office]
    if len(closes) < waves:
        return None
    newer = tuple(item.branch for item in found[: found.index(closes[0])])
    return Window(closes[waves - 1].sha, head.stdout.strip(), closes[0].sha, office, newer)


def growth_over(root: Path, base: str, head: str) -> tuple[dict[str, int], set[str]] | None:
    """`({path: net lines gained}, {path born in the window})`, or `None`.

    ⛔ `--no-renames`, so a renamed module arrives as a BIRTH rather than as a
    file that grew by its whole length under a name it did not have at the
    window's start. Net lines added less deleted, because that is exactly the
    delta `wc -l` reports between the two endpoints and R11 counts the same way.
    """
    span = f"{base}..{head}"
    numstat = git(root, "diff", "--numstat", "--no-renames", span)
    added = git(root, "diff", "--name-only", "--diff-filter=A", "--no-renames", span)
    if numstat.returncode != 0 or added.returncode != 0:
        return None
    grown: dict[str, int] = {}
    for line in numstat.stdout.split("\n"):
        fields = line.split("\t")
        if len(fields) == 3 and fields[0] != "-":
            grown[fields[2]] = int(fields[0]) - int(fields[1])
    return grown, set(added.stdout.split("\n")) - {""}


def measured(root: Path, waves: int = GROWTH_WAVES) -> tuple[list[Approach], Window | None]:
    """Return the banded population with growth attached, and the window it was read over."""
    population = near_modules(root)
    window = growth_window(root, waves)
    read = growth_over(root, window.base, window.head) if window else None
    if read is None:
        return population, None
    grown, born = read
    return [
        Approach(
            headroom=item.headroom,
            path=item.path,
            lines=item.lines,
            ceiling=item.ceiling,
            growth=grown.get(item.path, 0),
            born=item.path in born,
            answered=item.answered,
        )
        for item in population
    ], window


def approach_notice(root: Path) -> list[str]:
    """R11's approach, printed whether or not anything is near. ⛔ Never a finding.

    ⛔ **The population is printed IN FULL before any scalar** (Rulings 123,
    128, 140): *"20 modules are near"* and *"2 are near and moving"* are
    figures over two different populations, and the whole of `W155` is that
    difference. A reader who sees only the second cannot check the first.
    """
    population, window = measured(root)
    scanned = len(config.python_files(root))
    lines = [_window_line(window), f"{TAG} the population in full, closest to its ceiling first:"]
    if not population:
        lines.append(f"{TAG}   none — no module of the {scanned} scanned is within {NEAR_BAND}.")
    lines.extend(item.line() for item in population)
    lines.append(_census_line(population, scanned, window))
    lines.append(
        f"{TAG} A CEILING IS NOT A BUDGET (Ruling 261): near and static is the ceiling "
        f"HOLDING rather than a defect, and this says nothing about which module is the "
        f"healthier. The remedy for one that is near AND moving is a SPLIT at a named "
        f"seam, never a trim, and this is a notice — R11's ceiling is the build failure."
    )
    return lines


def _wave() -> str:
    """Say what a wave close is, in the words both window lines share."""
    return (
        f"a wave being closed by a first-parent merge of an office round branch, "
        f"`{OFFICE.pattern}` matched WHOLE and counted once per round, so a topic branch "
        f"under that prefix is no close; offices in precedence "
        f"{', then '.join(WAVE_CLOSE_OFFICES)}, a later office's rounds closing waves once "
        f"{GROWTH_WAVES} of them merged after an earlier office's newest round"
    )


def _window_line(window: Window | None) -> str:
    """Build the first line: the window, the close its waves end at, or why there is none."""
    if window is None:
        return (
            f"{TAG} NO GROWTH WINDOW — git could not name {GROWTH_WAVES} wave-closing "
            f"merges on this checkout's first-parent line, {_wave()}. "
            f"Growth is NOT reported and nothing is classified: a growth figure with no "
            f"window is not a reading. This is not a failure — the floor runs over trees "
            f"that are not this repository."
        )
    span = f"{TAG} window {window.base}..{window.head}"
    if window.current:
        said = f"{span} — the last {GROWTH_WAVES} waves, ending at {window.end}"
    else:
        said = (
            f"{span} — NOT the last {GROWTH_WAVES} waves: its waves END AT {window.end}, and "
            f"{len(window.after)} round(s) of another office merged after it "
            f"({', '.join(window.after)}), so it must not be read as current"
        )
    return (
        f"{said}; `{window.office}` rounds close these waves, {_wave()}. Growth is net "
        f"lines between those two refs; a module BORN inside the window has growth equal "
        f"to its own size, which is not growth, and is classed apart for that reason."
    )


def _census_line(population: list[Approach], scanned: int, window: Window | None) -> str:
    """Build the counting line, which comes AFTER the population it counts."""
    if window is None:
        return (
            f"{TAG} {len(population)} of {scanned} modules within {NEAR_BAND} lines of "
            f"their R11 ceiling. UNCLASSIFIED, and proximity alone would flag every one."
        )
    counts = {CLASS_MOVING: 0, CLASS_BORN: 0, CLASS_STATIC: 0}
    answered = 0
    for item in population:
        if item.answered:
            answered += 1
        else:
            counts[item.classification] += 1
    return (
        f"{TAG} {len(population)} of {scanned} modules within {NEAR_BAND} lines of their "
        f"R11 ceiling — PROXIMITY ALONE FLAGS {len(population)}. Proximity × growth flags "
        f"{counts[CLASS_MOVING]}: {counts[CLASS_MOVING]} {CLASS_MOVING}, "
        f"{counts[CLASS_STATIC]} near and static, {counts[CLASS_BORN]} born in the window, "
        f"{answered} answered by a standing split condition."
    )
