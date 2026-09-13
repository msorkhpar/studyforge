"""The OTHER direction: what `git` can see that the board does not NAME.

**What it does.** Reads every live checkout, ⛔ **every local branch NO checkout holds**, and
every `trial/*` / `tmp-*` branch against the release branch, and prints ⭐ **nine readings NO
BOARD CELL CARRIES** — the checkouts no row claims, the office round branches Ruling 265
exempts, ⛔ **the `SPENT`-namespace branches `W170` exempts on Ruling 265's OWN ground**, the
checkouts that are invisible to git by construction, ⭐ **which of those the board DECLARES an
office (`W125`)**, the ones git could not count at all,
⛔ **the UNMERGED branches HELD BY NO CHECKOUT**, the spent branches that are deletable, and
the spent ones still checked out.

## ⛔ `W-dispatch-population` — the GATE's population was CHECKOUTS, and its NAME says BRANCHES

⚠️ **MEASURED at `70131e2` by the coordinator and reproduced at `2d2af22`, role `wt/dev2`,
host:** ⛔ **`docs/NS-07-handoff` existed at `10a5470`, carried a real commit, was named by no
row, and `dispatched and UNNAMED by any row` printed `none.`** — ⭐ **because `counts` is built
over `graph.checkouts()`, so a branch is in Ruling 264(c)'s ONE pre-merge gate only while some
worktree holds it.** ⚠️ **The office that made it used a throwaway worktree and removed it,
which is CORRECT hygiene: the gate goes blind exactly when an office cleans up after itself.**

⛔ **The reading was already committed and read as design rather than as a hole:**
`test_planted_the_OTHER_direction_work_git_sees_and_the_board_does_not_name` asserts
`feat/live` ABSENT until a worktree is added, and its own justification is a statement of
MECHANISM — *"`worktree list` cannot see it either"* — not of intent. ⭐ **`rows/W136.md`
states the same fact in prose.**

⭐ **THE CHOICE TAKEN, and the two refused ones, because a gate that cries wolf is worse than
the hole:**

- ⛔ **REFUSED — widening the gate arm itself.** ⚠️ **Its population and this one need
  DIFFERENT actions: a branch a checkout holds is work SOMEBODY IS ON, and a branch no
  checkout holds is work NOBODY IS ON.** ⭐ **Folding two answers onto one line where they
  cannot be told apart is the exact coercion `W115` removed one line over.**
- ⛔ **REFUSED — narrowing the arm's NAME to *checked out and unnamed*.** ⚠️ That makes the
  gate honest and leaves the hole open, and Ruling 319 had just made this line the wave's
  only reading of undeclared work.
- ⛔ **REFUSED — a `docs/*` namespace exemption for the measured instance.** ⚠️ **Ruling 319
  refuses the `fix/*` widening on the ground that it empties the population the gate exists to
  read; `docs/*` is the same error one namespace over — a handoff branch IS dispatched work.**
- ⛔ **REFUSED — folding this line into the exit code.** ⚠️ That changes every merge's
  disclosure in this project, which is a ruling and not a detail. ⭐ **It is a NOTICE, like
  the five beside it, and `CORROBORATE_EXIT` does not move with it.**

⭐ **AND THE SPLIT IS SELF-DISCLOSING: the gate line NAMES its own population**, because a
reader who takes one line of two as exhaustive is Ruling 258's shape. ⛔ **The pointer carries
NO other line's selector** — `unnamed()`'s own `W170` note records what a decoy anchor costs.

⚠️ **MEASURED at `2d2af22`, role `wt/dev2`, host: of 208 local branches every one is `0` ahead
of the release branch, so this line names NOTHING today.** ⭐ **That is the cry-wolf answer:
the `ahead > 0` filter is SELF-RETIRING — a branch leaves this population the moment it
merges — so the line speaks only while genuinely unmerged work is held by nobody.**

**How you use it.** `unnamed(rows, live, graph, declaration)` returns `(lines, the count of
checkouts git could not read)` — ⛔ **the count is RETURNED so `corroborate`'s fold can reach exit
`NOT_AUTHORITATIVE`** (Ruling 216) — and `spent(graph, live)` returns lines alone.

**Depends on.** `board.observation` for the row type, `board.graph` for every git answer,
`board.verdict` for `tokens`, `board.offices` for the board's declared offices, and
`pathlib`. ⛔ **Nothing here decides a verdict** and
nothing here raises a `Finding`: these are NOTICES.

## ⛔ Why this is its own module, and the seam is the DIRECTION rather than a line count

⚠️ **`corroborate.py` stood at 352 of R11's 400 lines and `W132` adds a fourth printed
line with an argument behind it.** ⭐ **The split is the one the rest of this package is
already built on — `notice.py` off the surface (`W96`), `observation.py` (`W111`),
`bounds.py` and `scheduled.py` (`W100`), `bijection.py` (`W129`) — and the seam here is
real rather than arithmetic:**

⛔ **`corroborate` answers *is what the board ASSERTS corroborated* and folds the rows into
one exit code.** ⭐ **This module answers *what does git see that the board never
mentions* — which has NO board cell at all, judges no row, and is the half Ruling 189
named with nowhere to print it.** ⚠️ **Ruling 183's form, one direction over: a reading
that forbids nothing is still a reading, and it goes where it cannot be mistaken for a
gate.**

⛔ **The ONE thing that crosses back is a COUNT** — the live checkouts git could not read —
⭐ **because `W115` made a FAILED reading an input to the exit code and Ruling 216 folds it.**
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.quality.board.graph import Graph
from tools.quality.board.observation import Observation
from tools.quality.board.offices import Declaration, judged
from tools.quality.board.verdict import tokens

#: ⛔ Branch namespaces whose members are DELETED once they are ancestors of the
#: release branch. ⚠️ **The standing form, measured by the CTO at `0285a92` and
#: `c3e2919`:** such a branch carries nothing unique, is invisible to
#: `--no-merged` by construction, and its only remaining effect is ⭐ **to read as
#: dispatched work to a human — which is Ruling 189's subject with no board cell
#: to print it in.** ⛔ **So this instrument is where it gets printed.**
#:
#: ⛔ **`W170`: this tuple is ALSO taken out of the `dispatched and UNNAMED` GATE's
#: population, on Ruling 265's OWN stated ground.** ⭐ **That ground is *no register row
#: will EVER name one of these*, and it transfers whole: a `trial/*` or `tmp-*` branch is
#: a REVIEWER'S TRIAL MERGE — never dispatched, never taken by a row, and already reported
#: by `spent()`'s own two lines.** ⚠️ **Ruling 265 chose the NAMESPACE over emptiness
#: deliberately, so the namespace was simply not enumerated; `W132`'s defect survived here
#: in a second namespace and fired precisely when a review was in progress, which is the
#: only moment Ruling 264(c)'s gate is read.**
#:
#: ⛔ **This NARROWS a population and does NOT widen the predicate** (Ruling 185(b)).
#: ⚠️ **Ruling 319 refuses extending this exemption to `fix/*` — that would exempt the
#: whole population the gate exists to read.** ⭐ **`fix/W*` is untouched here, and
#: `test_unclaimed.py` asserts that direction as its own reading.**
SPENT = ("trial/", "tmp-")

#: ⛔ **`W132`, Ruling 265: an OFFICE's own round branch — and `W136`: the WHOLE NAME.**
#:
#: ⭐ **The predicate is NOT *this branch has no commits* but *NO REGISTER ROW WILL EVER
#: NAME THIS BRANCH*** — ⛔ **a property of the BRANCH NAMESPACE, decidable from the name:
#: the register names rows, rows are taken on `fix/W*` branches, and an office's round
#: branch is the vehicle for the register itself, so a row naming it would be a row naming
#: its own recorder.** ⚠️ **Ruling 130's `0 ahead` form was right about the population and
#: wrong about the reason, which is Ruling 225's shape: a defended property false as stated.**
#:
#: ⭐ **MEASURED, one branch and two readings, the only variable being whether the office
#: had written anything down yet:** `chore/po-round45` exempt at `6c4e3d0` at `0` ahead;
#: `chore/po-round44` named as *dispatched and UNNAMED* at `b5b0577` after it committed.
#:
#: ⛔ **`W136`: a whole-name match, never a prefix and never `in`.** ⚠️ **The anchored
#: prefix exempted `chore/cto-round34-rubric`, a TOPIC branch the ground would flag, and
#: `in` would exempt `fix/W99-po-round-guard`.** ⭐ **The spelling is the written naming
#: convention in `docs/conventions/delivery-flow.md`, one spelling and not a vocabulary of
#: separators (Ruling 65); a `chore/` branch outside it is out of convention and the gate
#: naming it once it carries work is the TRUE answer.** ⛔ `[0-9]`, never `\d`, which
#: admits every Unicode digit.
OFFICE = re.compile(r"chore/(cto|po)-round[0-9]+")


def office(branch: str) -> bool:
    """Whether `branch` is an office round branch: `OFFICE` over the WHOLE name (`W136`)."""
    return OFFICE.fullmatch(branch) is not None


def unnamed(
    rows: tuple[Observation, ...],
    live: dict[str, str],
    graph: Graph,
    declaration: Declaration,
    carriers: frozenset[str] = frozenset(),
) -> tuple[list[str], int]:
    """Report the other direction: work git can see that the board does not name.

    ⭐ **`W153`: `carriers` are the ones `dispatch.judge` ACCEPTED**, and each is claimed
    exactly as a row's branch is. ⛔ With none, every line reads as it did before `W153`.

    ⛔ **The measured failure was BIDIRECTIONAL** — stale rows present and live
    rows absent, in the same table — ⚠️ **and a check that only read the rows the
    board printed would have passed the half where the board printed nothing.**

    ⛔ **And the BLIND SPOT is printed rather than implied.** ⚠️ **A checkout with
    no commit is invisible to every git instrument BY CONSTRUCTION** (Ruling 130,
    and Ruling 171's founding case): *just dispatched* and *office checkout* are
    the same bytes to `git`. ⭐ **So those are COUNTED AND NAMED as unreadable
    here, never silently dropped and never judged** — the board is the only
    instrument that can tell them apart, which is the whole of Ruling 171.

    ⛔ **Directory BASENAMES, never the path** (R7): `git worktree list` answers
    in absolute paths, and an absolute path carries the user's home directory.

    ⛔ **`W115`: the coercion that lived here was `ahead(branch) or 0`**, which filed a
    FAILED reading under *invisible to git BY CONSTRUCTION* — ⚠️ **the one line whose
    whole job is to say *this is unreadable*, and where a failure is indistinguishable
    from a legitimate `0`.** ⭐ **It gets its own line and its own count now, and the
    count is RETURNED so the caller's fold can reach exit `NOT_AUTHORITATIVE`**
    (Ruling 216).

    ## ⛔ `W132`/Ruling 265, `W170`, `W125` and the population row — SEVEN lines, SEVEN answers

    | line | its population |
    |---|---|
    | `dispatched and UNNAMED` | ⛔ **LIVE CHECKOUTS**, ahead `> 0`, unclaimed, neither an
      office branch nor a `SPENT` namespace — ⚠️ the line Ruling 264(c) made the PRE-MERGE
      GATE, ⭐ **and it now NAMES that population in its own text** |
    | ⛔ `UNMERGED and HELD BY NO CHECKOUT` | the SAME three exemptions over the branches
      `git worktree list` cannot see — ⭐ **the gate's other half, a NOTICE, never folded** |
    | ⭐ `OFFICE round branches` | `OFFICE` over the WHOLE name (`W136`), ANY count |
    | ⭐ `SPENT namespaces` | `W170`: `trial/*` / `tmp-*` that WOULD have been gated —
      ⛔ **the DIFFERENCE the exemption made, printed with its count** |
    | `invisible BY CONSTRUCTION` | ahead `== 0`, unclaimed — ⛔ **a `fix/W*` branch at `0`
      STAYS HERE and is still NAMED**, and so does a `SPENT` branch at `0`: ⚠️ **that one
      was never in the gate's population, so this exemption removed NOTHING from it**. ⭐
      **`W132/3`: `none.` at zero** |
    | `office checkouts` | `W125`/`W96/5`: the ones the board's `<!-- offices -->` block
      DECLARES, taken off the line above ALONE — ⛔ **ABSENT, UNREADABLE and EMPTY answer
      nothing** (`offices.py`) |
    | `git COULD NOT COUNT` | `ahead()` returned `None` — a FAILED reading (`W115`) |

    ⚠️ **The DETACHED checkout is in NONE of the five, deliberately** — it has no branch
    line for `graph.checkouts()` to read. ⭐ **That hole is `PO-44/5`'s and `W125`'s, and
    neither Ruling 265's widening nor `W170`'s must make it harder to see**, which is why
    each exemption line carries its OWN count rather than merely shrinking another line's
    number.

    ⛔ **`W170`: the `SPENT` exemption touches the GATE arm ALONE.** ⭐ **`spent()`'s
    `trial/tmp branches STILL CHECKED OUT` line reads the SAME branches and is UNCHANGED,
    because removing a branch from the GATE must never remove it from the INSTRUMENT**
    (Ruling 206(ii): reporting a worktree you did not cut is never wrong).
    """
    claimed = {name for row in rows for name in tokens(row.checkout)} | carriers
    counts = {branch: graph.ahead(branch) for branch in live if branch != graph.release}
    unread = sorted(Path(live[b]).name for b, n in counts.items() if n is None)
    # ⛔ `W132`, Ruling 265: the office exemption is taken out of the POPULATION before
    # either arm reads it, and is then PRINTED with its count and its reason.
    rounds = sorted(b for b in counts if office(b))
    # ⛔ `W170`, Ruling 265's OWN ground: the `SPENT` namespaces come out of the GATE's
    # population too — and this list is the DIFFERENCE, exactly what the gate would have
    # named and no longer does, so the exclusion is auditable rather than asserted.
    trial = sorted(
        b
        for b, n in counts.items()
        if b.startswith(SPENT) and n is not None and n > 0 and b not in claimed
    )
    missing = sorted(
        b
        for b, n in counts.items()
        if n is not None
        and n > 0
        and b not in claimed
        and not office(b)
        and not b.startswith(SPENT)
    )
    blind = {
        Path(live[b]).name: live[b]
        for b, n in counts.items()
        if n == 0 and b not in claimed and not office(b)
    }
    # ⛔ `W125`: the board's DECLARED offices leave THIS population and no other.
    named, declared = judged(declaration, blind)
    # ⛔ The GATE's OTHER HALF: the same three exemptions over the branches no worktree holds.
    # ⭐ The exemptions are applied to the POPULATION before any `ahead()` runs (Ruling 185(b)),
    # which is also why this costs one git call per CANDIDATE and not one per local branch.
    candidates = [
        b
        for b in graph.heads()
        if b != graph.release
        and b not in live
        and b not in claimed
        and not office(b)
        and not b.startswith(SPENT)
    ]
    held_by_none = {b: graph.ahead(b) for b in candidates}
    adrift = sorted(b for b, n in held_by_none.items() if n is not None and n > 0)
    # ⛔ NOT `or 0`: `W115`'s coercion, and the line it would land on is the one whose whole
    # job is to say *this is unreadable*, where a failure cannot be told from a real `0`.
    unjudged = sorted(b for b, n in held_by_none.items() if n is None)
    lines = (
        [
            f"  ⛔ dispatched and UNNAMED by any row: {' '.join(missing)}"
            f" — ⚠️ population: LIVE CHECKOUTS only; a branch no worktree holds is read on the"
            f" line below and NEVER here."
        ]
        if missing
        else [
            "  dispatched and unnamed: none. — ⚠️ population: LIVE CHECKOUTS only; a branch no "
            "worktree holds is read on the line below and NEVER here."
        ]
    )
    # ⛔ IMMEDIATELY BELOW THE GATE, because the gate's own text points at *the line below* and
    # a pointer that has to be searched for is a pointer a reader skips.
    #
    # ⛔ **THIS LINE'S PROSE CARRIES NO OTHER LINE'S SELECTOR** — not `dispatched and`, not
    # `could not count`, not `STILL CHECKED OUT` — ⚠️ because `W170`'s own note records a decoy
    # anchor selecting the wrong line out of this very instrument's output.
    lines.append(
        f"  ⛔ UNMERGED and HELD BY NO CHECKOUT, named by no row ({len(adrift)}): "
        f"{' '.join(adrift)} — ⚠️ this is the GATE's other half: a branch carrying real work "
        f"that `git worktree list` cannot see, which is what an office leaves behind when it "
        f"removes a throwaway worktree. ⛔ A NOTICE and NOT folded into the exit code, because "
        f"folding it would change every merge's disclosure and that is a ruling, not a detail."
        if adrift
        else f"  unmerged branches held by no checkout, named by no row: none. — ⭐ the same "
        f"three exemptions as the gate above ({OFFICE.pattern} whole, {'|'.join(SPENT)}*, and "
        f"any branch a row claims), over {len(candidates)} candidate branch(es)."
    )
    if unjudged:
        lines.append(
            f"  ⛔ git DECLINED to answer *commits ahead* for {len(unjudged)} branch(es) NO "
            f"WORKTREE IS ON: {' '.join(unjudged)} — ⚠️ a FAILED reading, printed rather than "
            f"coerced to `0` (`W115`), and ⛔ NOT folded into the exit code: the fold Ruling "
            f"216 built is over LIVE CHECKOUTS, and widening it is a ruling and not a detail."
        )
    lines.append(
        f"  ⭐ OFFICE round branches, EXEMPT by Ruling 265 REGARDLESS of commits ahead "
        f"({len(rounds)}): "
        + ", ".join(f"{b} +{counts[b]}" for b in rounds)
        + " — ⛔ the exemption is the BRANCH NAMESPACE and not emptiness: no register row "
        "will EVER name one of these, because a row naming an office's round branch would "
        "be a row naming its own recorder. ⚠️ Ruling 130's `0 ahead` form was right about "
        "the population and wrong about the reason, and an office branch stops being `0` "
        "ahead the moment it records anything (Ruling 264(c) made this line a GATE)."
        if rounds
        else f"  office round branches exempt by Ruling 265 ({OFFICE.pattern} whole): none."
    )
    # ⛔ `W170`. ⭐ APPENDED AFTER the office line deliberately: both carry the token
    # `Ruling 265`, and the office line's own readings select on it.
    #
    # ⛔ **AND THIS LINE'S PROSE QUOTES NO OTHER LINE'S ANCHOR VERBATIM.** ⚠️ **The first
    # draft said *STILL REPORTED below on `trial/tmp branches STILL CHECKED OUT`* and a
    # `next(... if "STILL CHECKED OUT" in line)` then selected THIS line instead of that
    # one** — ⭐ **a decoy anchor in an instrument's own output, which costs a human
    # grepping the reading exactly what it cost the reading that caught it.**
    lines.append(
        f"  ⭐ SPENT namespaces EXEMPT from the GATE on Ruling 265's OWN ground "
        f"({'|'.join(SPENT)}*) ({len(trial)}): "
        + ", ".join(f"{b} +{counts[b]}" for b in trial)
        + " — ⛔ a trial/tmp branch is a REVIEWER'S TRIAL MERGE: never dispatched, never "
        "taken by a row, so no register row will EVER name one, which is the ground "
        "Ruling 265 gave and it transfers whole. ⚠️ This line is the DIFFERENCE the "
        "exemption made, and every branch on it is STILL REPORTED by the standing-worktree "
        "line below — removing it from the GATE never removes it from the INSTRUMENT "
        "(Ruling 206(ii)). ⛔ NARROWING a population, never widening the predicate "
        "(Ruling 185(b)); Ruling 319 refuses the `fix/*` widening, which this is not."
        if trial
        else f"  spent namespaces exempt from the gate ({'|'.join(SPENT)}*): none."
    )
    lines.append(
        f"  invisible to git BY CONSTRUCTION (Ruling 130), 0 commits ahead and named by no "
        f"row: {len(named)} — {' '.join(named)}"
        if named
        else "  invisible to git BY CONSTRUCTION (Ruling 130), 0 commits ahead and named by no "
        "row: none."
    )
    lines.append(declared)
    lines.append(
        f"  ⛔ git COULD NOT COUNT *commits ahead* for {len(unread)} live checkout(s): "
        f"{' '.join(unread)} — ⚠️ a FAILED reading, and NOT the Ruling 130 exemption above: "
        f"that one is earned by a checkout with no commit, this one is git declining to "
        f"answer. ⛔ `ahead(branch) or 0` used to fold these two together, so a failure "
        f"read as a `0` somebody had already agreed to ignore."
        if unread
        else "  live checkouts git could not count: none."
    )
    return lines, len(unread)


def spent(graph: Graph, live: dict[str, str]) -> list[str]:
    """`trial/*` and `tmp-*` branches that are now ancestors of the release branch.

    ⚠️ **Ruling 206(ii) named this line's own blind spot and routed it here:** a
    trial worktree that is STILL CHECKED OUT is excluded by `name not in live`, so
    the one shape that keeps a spent row green is the one shape this line cannot
    print. ⭐ **It is printed now, separately and as a NOTICE**, because removing a
    worktree you did not cut is always wrong and reporting one never is.

    ⛔ **`W170` DEPENDS ON THIS LINE AND DOES NOT TOUCH IT.** ⭐ **The `SPENT` namespaces
    are exempt from `unnamed()`'s GATE precisely BECAUSE this arm already reports them** —
    ⚠️ **so a change here that narrowed `standing` would remove the only reading of a
    standing trial worktree, which is the one shape Ruling 206(ii) exists to print.**
    """
    names = [name for name in graph.heads() if name.startswith(SPENT)]
    spent = sorted(name for name in names if name not in live and graph.merged(name))
    standing = sorted(name for name in names if name in live)
    lines = (
        [
            f"  ⚠️ spent and deletable ({len(spent)}): {' '.join(spent)} — each is an ancestor "
            f"of {graph.release}, checked out nowhere, and reads as dispatched work to a human."
        ]
        if spent
        else ["  spent trial/tmp branches: none."]
    )
    lines.append(
        f"  ⚠️ trial/tmp branches STILL CHECKED OUT ({len(standing)}): {' '.join(standing)} — "
        f"⛔ report, never remove one you did not cut (Ruling 206(ii))."
        if standing
        else "  trial/tmp branches still checked out: none."
    )
    return lines
