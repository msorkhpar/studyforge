"""The OTHER direction: what `git` can see that the board does not NAME.

**What it does.** Reads every live checkout and every `trial/*` / `tmp-*` branch against
the release branch and prints ⭐ **seven readings NO BOARD CELL CARRIES** — the checkouts no
row claims, the office round branches Ruling 265 exempts, ⛔ **the `SPENT`-namespace branches
`W170` exempts on Ruling 265's OWN ground**, the checkouts that are invisible to git by
construction, the ones git could not count at all, the spent branches that are deletable,
and the spent ones still checked out.

**How you use it.** `unnamed(rows, live, graph)` returns `(lines, the count of checkouts
git could not read)` — ⛔ **the count is RETURNED so `corroborate`'s fold can reach exit
`NOT_AUTHORITATIVE`** (Ruling 216) — and `spent(graph, live)` returns lines alone.

**Depends on.** `board.observation` for the row type, `board.graph` for every git answer,
`board.verdict` for `tokens`, and `pathlib`. ⛔ **Nothing here decides a verdict** and
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

from pathlib import Path

from tools.quality.board.graph import Graph
from tools.quality.board.observation import Observation
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

#: ⛔ **`W132`, Ruling 265: an OFFICE's own round branch, and the prefix is ANCHORED.**
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
#: ⛔ **`startswith`, never `in`.** ⚠️ **`fix/W99-po-round-guard` CONTAINS `po-round` and is
#: a developer's branch** — the same defect as `chore/cto-round3` reading terminal off
#: `Merge chore/cto-round39:` one module over (Ruling 199). ⭐ **Ruling 185's form: the
#: exemption is implemented in the POPULATION and PRINTED with its count and its reason,
#: because Ruling 264(c) made this line a gate and a gate that hides a rule is unreadable.**
OFFICE = ("chore/cto-round", "chore/po-round")


def unnamed(
    rows: tuple[Observation, ...], live: dict[str, str], graph: Graph
) -> tuple[list[str], int]:
    """Report the other direction: work git can see that the board does not name.

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

    ## ⛔ `W132`/Ruling 265 and `W170` — FIVE lines now, and each is a DIFFERENT answer

    | line | its population |
    |---|---|
    | `dispatched and UNNAMED` | ahead `> 0`, unclaimed, ⛔ **neither an office branch nor a
      `SPENT` namespace** — ⚠️ the line Ruling 264(c) made the PRE-MERGE GATE |
    | ⭐ `OFFICE round branches` | `chore/{cto,po}-round*`, ANY count — see `OFFICE` |
    | ⭐ `SPENT namespaces` | `W170`: `trial/*` / `tmp-*` that WOULD have been gated —
      ⛔ **the DIFFERENCE the exemption made, printed with its count** |
    | `invisible BY CONSTRUCTION` | ahead `== 0`, unclaimed — ⛔ **a `fix/W*` branch at `0`
      STAYS HERE and is still NAMED**, and so does a `SPENT` branch at `0`: ⚠️ **that one
      was never in the gate's population, so this exemption removed NOTHING from it** |
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
    claimed = {name for row in rows for name in tokens(row.checkout)}
    counts = {branch: graph.ahead(branch) for branch in live if branch != graph.release}
    unread = sorted(Path(live[b]).name for b, n in counts.items() if n is None)
    # ⛔ `W132`, Ruling 265: the office exemption is taken out of the POPULATION before
    # either arm reads it, and is then PRINTED with its count and its reason.
    office = sorted(b for b in counts if b.startswith(OFFICE))
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
        and not b.startswith(OFFICE)
        and not b.startswith(SPENT)
    )
    blind = sorted(
        Path(live[b]).name
        for b, n in counts.items()
        if n == 0 and b not in claimed and not b.startswith(OFFICE)
    )
    lines = (
        [f"  ⛔ dispatched and UNNAMED by any row: {' '.join(missing)}"]
        if missing
        else ["  dispatched and unnamed: none."]
    )
    lines.append(
        f"  ⭐ OFFICE round branches, EXEMPT by Ruling 265 REGARDLESS of commits ahead "
        f"({len(office)}): "
        + ", ".join(f"{b} +{counts[b]}" for b in office)
        + " — ⛔ the exemption is the BRANCH NAMESPACE and not emptiness: no register row "
        "will EVER name one of these, because a row naming an office's round branch would "
        "be a row naming its own recorder. ⚠️ Ruling 130's `0 ahead` form was right about "
        "the population and wrong about the reason, and an office branch stops being `0` "
        "ahead the moment it records anything (Ruling 264(c) made this line a GATE)."
        if office
        else f"  office round branches exempt by Ruling 265 ({'|'.join(OFFICE)}*): none."
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
        f"row: {len(blind)}" + (f" — {' '.join(blind)}" if blind else "")
    )
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
