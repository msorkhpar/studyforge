# SESSION-2026-09-10 — coordinator handoff

**Kind:** session log

**Release tip:** `release/m0-foundations` @ `d1270cd` — **3090 passed, 63 skipped,
floor clean**, `ruff check` exit 0, `ruff format --check` exit 0 (**424 derived
from the tree**; see the denominator note below).
**M1 is CLOSED at `2fe56a4`. M2 step 2.1 is open.**
⚠️ **The tip above went stale while this file was being written.** `SF-31` was
approved and merged at `f3ee177` (**3179 passed, 63 skipped**) between the header
being typed and the commit landing. ⛔ **Left as written and corrected here rather
than edited, because it is defect 4 below demonstrating itself in the document
that records it** — the reading's half-life was shorter than the writing.

**Written by:** the orchestrating session, overnight, with the user asleep and a
standing instruction to advance the project as far as it would go.

---

## What moved

**96 commits, 41 merges, suite 2490 → 3090.** M1's remaining build work landed
whole: `SF-10` (unit document builder), `SF-12` (the page renderer, +257 tests),
`QA-03` (the visual harness), `SF-31` (the placement contract, in review), plus
`W25`–`W33`, `W39` in flight, `FND-08`, `FND-09`, and rulings **57–98**.

⭐ **M1's Done — *a unit page from the depth-1 fixture opens in a browser, with
styles and highlighting, over `file://`* — is met and was verified in a real
browser rather than asserted.**

---

## ⛔ The four defects this session committed, in the order they will recur

**1. Branch state quoted as tip state — four instances, two of them mine.**
Twice a CTO merged approved work into their own round branch and reported it
landed; the release branch had not moved. Once I closed M1 citing a
pre-authorisation that existed only on an unmerged branch. ⭐ **Ruling 84 is the
fix and it is one line: after merging, confirm the tip moved** (`git log
--format='%P' -1 | wc -w`, and `git branch --no-merged` against the board).
⛔ **Reporting a merge you did not make is worse than not merging** — the next
agent measures a tree that does not exist.

**2. A disk-derived number quoted as a property of the commit — mine, twice.**
Every lint denominator I reported was one too high, because this checkout carries
one untracked file at the root. ⛔ **Ruling 86a: the verdict is the exit code and
the denominator is derived from the tree** (`git ls-tree -r --name-only`, minus
`tests/fixtures`). ⚠️ **Two agents' 398s once agreed for entirely different
reasons.** Check both directions separately rather than letting them cancel.

**3. A ruling that reached no artifact — seven at once.**
Check 3 found rulings 90–94, 96 and 97 landed nowhere, five from a single round,
four naming framework work with no row. ⭐ **The diagnosis is the most useful
sentence of the session: *a ruling lands by itself exactly when its artifact is
the ruler's own file*, with Ruling 95 as the control that proves it is not
seniority.**

**4. Two agents writing, one reading.**
`F18` was ruled at 03:49 and the PO committed at 03:50:51 — neither at fault, and
the row simply did not exist. ⭐ **General form: *any repository reading has a
half-life shorter than a round when two agents write, and only the merger can
take a reading still true when acted on.***

---

## ⚠️ What will bite the next session

- ⛔ **The release tip goes red after every merge** — a stale knowledge index,
  invisible in every worktree because `graphify-out/` is gitignored. I rebuilt it
  by hand roughly twenty times. `W39` is in flight to fix it; until then the
  interim step is in `delivery-flow.md` **with a written expiry**.
- ⛔ **Ruling 89 is not runnable in a linked worktree at all** — `git worktree
  add` does not carry the gitignored index. **Rebuild in the main checkout.**
- ⛔ **CORRECTED — the line below is FALSE and I propagated it into a dozen
  briefs.** The sets **intersect on 5 rows**: `tests/docker/test_dev_image.py`
  512/518/538/547/566 skip in **both**, for different reasons (in the container,
  *already inside the image*; on the host, docker tests disabled). Measured at
  `6850c3c`: container 29 skip rows, host 10, `comm -12` → 5. ⚠️ **A third
  environment (`STUDYFORGE_DOCKER_TESTS=1`) runs those five.** ⭐ **The true
  claim is the useful half and it survives: the sets do not RECONCILE BY COUNT,
  so matching them by number matches rows wrongly.** ⛔ **I inherited "disjoint"
  from a round that had measured the totals, not the rows, and never re-measured
  it — a reading taken from a proxy, quoted as a property of the thing, which is
  the common form of every defect in this list.**
- ⚠️ ~~**Host and container skip sets are DISJOINT**~~ (55 visual, 5 docker, 3
  sibling vs. 2 ruff-absent). They reconcile on the total and on nothing else;
  **matching them by count matches every row wrongly.**
- ⚠️ **Two test modules are at R11's ceiling** — `test_gate_coverage.py` at
  600/600 and `corpus/container/test_document.py` at 598/600. `W40` splits them.
- ⚠️ **The rubric is 1881 lines and has grown four rounds running.** `W34` is
  deliberately unqueued while a build task is in flight.

---

## ⭐ The rulings that changed how the work is measured

- **A measurement is quoted with the ref it was taken on, or it is not a
  measurement.** Two agents counted the same thing correctly and disagreed; the
  entire difference was which tree, and neither had named it.
- **An acceptance condition is a decomposition, never a total** (72). Its proof:
  across four measurements of one corpus the totals went 100 → 112 → 117 → 17
  while **the residual never moved from 17.**
- **A number can be stable while the thing it counts is not** (81). A price
  reproduced exactly at two refs while its membership had changed underneath.
- **A mutant sweep states its environment, its purge, and shows its unmutated
  baseline SURVIVING** (70) — **and prints exit code, pytest tail and skip
  count, all three agreeing** (76, 83). ⛔ **Emptying a walk once produced `exit
  0, all passed` while six tests vanished into empty parametrisations.**
- **Lint is a sole detector, not a style layer** (79). The deciding evidence was
  a mutant that **passes all 2923 tests and is killed only by `ruff F401`.**
- **A milestone close is a set of measurements at one named ref; no row is
  inherited across a ref change** (97). No escape clause: the rows cost ~90
  seconds, and if one is ever too expensive to re-take, that is the finding.
- **Every decomposition needs one row whose discharge is *somebody looked at the
  real thing*** — and **the observer is not the author of the task the row
  gates** (82).

---

## The integration track

⭐ **Its backlog is empty for the first time.** `F18`, `F19`, `F21`, `Q20` and
`F25` are all ruled. `ISO-09` is now blocked on **two framework deliveries**
(`SF-35`, `SF-31`) rather than two open questions — ⛔ *undefined → unshipped is
the whole change*, and `Q18`'s `Blocked` framing is what kept the finish line
honest while it happened.

⭐ **The strongest single contribution of the session came from that side:** told
that `F18` was ruled, they ran the framework against it, got the correct
refusals, and **relabelled their own section a projection rather than treat a
decision as a delivery.** Then they reproduced the ruling's own three globs,
found they worked, and **refused to propose them** — because one matched three
files only by an accident of alphabetisation, and *a `why` cannot be true of a
file nobody has written yet.*

⛔ **And they retracted one of their own findings:** *a finding that overstates
its own necessity is how an integrator wins an argument the framework should have
won.*

---

## Open, in order

1. `chore/cto-round28` — verdicts on `SF-31` and `chore/po-round24`.
2. `fix/W39-index-step` — the index step, Ruling 96 (options 2 **and** 1,
   scoping first).
3. `SF-35` — `F18`'s implementation. **`ISO-09`'s last framework blocker.**
4. `SF-04` — unblocked by Ruling 95 (`site_api`); both traps are on the board.
5. `SK-02`, then M2 step 2.2.

⛔ **`SK-08` still does not exist and is still M2.** Every step of the
integration plan it should have generated is a finding against it, and those
remain the highest-value output of that track while it can still be shaped.
