# SESSION 2026-09-12 — coordinator handoff, wave 9

**Kind:** session log

**Release tip:** `release/m0-foundations` @ `ad74a55`.

| instrument | environment | reading |
|---|---|---|
| `python3 -m tools.quality` | pinned container, `docker/dev/check` in the main checkout | clean, `FLOOR_EXIT=0` · **349 rulings from 57 records** · **446 markdown files** |
| `python3 -m pytest -ra` | pinned container, same invocation | **5712 passed, 18 skipped**, `PYTEST_EXIT=0` |
| `corroborate` | **host**, main checkout | `CORROBORATE_EXIT=1` — `W64`, `W155`, `W170` all TERMINAL, absorbed this wave; `dispatched and unnamed: none` |
| `tools.workspace verify` | **host** — returns `2` in the pinned container by construction | `VERIFY_EXIT=1`, ONE component: the board-held ISO pin |
| verdict gate control | **host**, git only | **178 merges** in the reviewed span; the control still REFUSES `0183cd1`; the final command prints NOTHING |

⛔ **Five environments are named because there are five, and a block label is
not an environment** (`/32`, against me, wave 7).

## ⭐ FIVE MERGES, COUNTED ON THE FIRST-PARENT LINE (Ruling 327)

`7a7a178` → `4d4c7c7` → `1a55e12` → `0011d5d` → `2c9082d` → `ad74a55`.

| # | Subject | Reviewed at | Verdict |
|---|---|---|---|
| 1 | `fix/W170-trial-namespace-gate` — the gate row | `90ab41a` | APPROVE |
| 2 | `chore/po-round55` — the register | `3d0cb31` | APPROVE |
| 3 | `fix/W155-ceiling-growth` | `56ac8c0` | **APPROVE after changes** |
| 4 | `fix/W64-kind-gate-scope` | `df9ad80` | **APPROVE after changes** |
| 5 | `chore/cto-round70` — the reviewer's record | ``917270c`` | APPROVE x2, APPROVE after changes x2, this record APPROVED |

⛔ **Merges 3 and 4 were held once each and merged on RE-TAKE verdicts.** The
`(CTO: CHANGES REQUESTED)` brackets were ruled at `2039008` and `5b31436` and
nowhere else. ⭐ **Both offices refused to carry their old brackets forward
UNPROMPTED** — the reviewer's own `CTO-70/12` applied back to the reviewer by
the offices it had been ruled at.

## ⛔ THE THING TO CARRY FORWARD: TWO WELL-FORMED VERDICTS THAT DISAGREE

The reviewer's re-take arrived with a summary table reading **APPROVE** for both
subjects and two fenced merge strings both closing **`(CTO: APPROVE after
changes)`**. ⛔ **I stopped and asked rather than picking one.**

⭐ **The reviewer's own reading of why that mattered, and it is the sharpest
sentence of the round:** *a malformed token gets rejected; two well-formed
tokens that disagree get **guessed at**.* Recorded as `CTO-70/19` against
itself, in the record whose own `CTO-70/16` had refused, one commit earlier, to
mint the second copy that can disagree.

⚠️ **The cost of asking is one round-trip. The cost of guessing is a permanent
merge message carrying a verdict nobody ruled.** This is the third wave running
in which the same refusal has paid: `CTO-69/22`, then `CTO-70/12`, now
`CTO-70/19`.

## ⭐ THE WAVE INTERACTION NOBODY HAD MEASURED, AND ORDERING IS NOT MEASURING

⛔ **The reviewer's preview `e61e66f` was release + `W155` + `W64` and did NOT
contain its own record branch.** So the combination that existed at NO ref
anywhere was the one Ruling 340 is about: `W64` widens the kind gate over the
DOCUMENT population, and the round-70 record ADDS a 592-line document to that
population in the same wave, plus 141 lines of `review-rubric.md`.

⚠️ **Ordering the record last does not measure it** — it only guarantees that a
red floor arrives at the last merge instead of an earlier one.

I built `911d1ea` = `1a55e12` + `56ac8c0` + `df9ad80` + `5ba0617`, ROLE
`wt-coord-trial`, pinned image, before merging anything: **floor clean,
`FLOOR_EXIT=0`**, `349 rulings derived from 57 ruling records`, three clean
merges with no manual resolution. ⛔ **And that reading went DATED the moment the
record moved to `b0e7e56`, which is why merge 5 was re-measured at the release
tip rather than inherited from it.**

## ⭐ A CONTROL NOBODY PLANTED: `ONBOARDING.md` IS IN THE SWEEP, AND HERE IS THE PROOF

The reviewer's preview read **`444` markdown files**. My release tip at merge 4
reads **`445`** — with the **identical** `1487` pointers and `799` anchored.
Same content, one extra document, zero extra pointers.

⛔ **The difference is `ONBOARDING.md`: the user's own untracked file, present in
the main checkout and absent from every linked worktree.** ⭐ **That is live
evidence for the standing rule that it must never be git-ignored** — ignoring it
would drop it out of exactly this population, and that population is the
personal-data sweep's.

## RULING 305's ORDER AND RULING 279's DISCLOSURE, PROVED BY INSTRUMENT AGAIN

`corroborate` read WHOLE before every merge, ROLE main checkout, host:

| before merge | refuted | `dispatched and unnamed` | exit |
|---|---|---|---|
| 3 | 1 — `W170` | none | `1` |
| 4 | 2 — `W155` `W170` | none | `1` |
| 5 | 3 — `W64` `W155` `W170` | none | `1` |

⭐ **The arm changes case at every merge and the exit code does not move with
it.** Third wave running.

## MY OWN DEFECTS THIS WAVE, BY ID

⛔ **Thirteen, and they are three shapes, not thirteen.**

**Shape one — I COMPRESS A POPULATION INTO A BRIEF, and the compression drops
members.** `/41` — a count read off a truncated `sed` window and put in a brief;
a count is derived from a complete population, never from a window. `W155/8` —
my restatement of a row's minting reading dropped **four of nine listed modules
and one whole class**, inside a brief whose own preamble names that defect nine
times. `W155/9` — the same brief names the row's surface only in the guardrails.
⭐ **The cure is not more care. A brief POINTS at the row's table and quotes NONE
of it** — the row is already the authority, and restating it adds a second copy
that can drift, which is `board.md`'s own rule arriving in my briefs. It is in
the preamble now.

**Shape two — I WRITE INSTRUMENTS THAT CANNOT DO THE JOB THEY ARE NAMED FOR.**
`/38` — my idle check ran in the same invocation as the measurement it gates;
**a gate that cannot stop what it gates is a log line.** `/39` — it counted
itself. `/40` — I printed the user's real identity values to verify a NULL
CHECK; **a null check proves absence without reading the value**, and the
reviewer then committed the same defect as `CTO-70/1`. `CTO-70/13` — the
redirected form I proposed as the cure still leaks in the failing case.
⭐ **Ruling 343 came out of these**, and this wave's retirement check was run in
its form: own invocation, an EXTRACT rather than a detector, from outside every
subject.

**Shape three — I INHERIT A PREMISE INSTEAD OF MEASURING IT.** `W64/6` — my
brief told an office to write a handoff path that already held the STOP record
Ruling 218 ratified; **Ruling 346** now permits the second handoff on a new stem.
`W170/1` — my brief said three settling conditions where the row has four, the
missing one being Ruling 266's control-that-must-fail. `PO-55/1` — my ground for
placing three `W` rows in wave 9 was refuted **on my own handoff**, which
schedules the step close into the same wave. `PO-55/6` and `CTO-70/6` — I called
branch tips *landed*; in this register **landed takes a merge ref.**

⛔ **And one framing error with no id, which is the one I would keep if I could
keep only one.** I put the board's 17-byte blocker to the reviewer as a
size-versus-safety decision. ⭐ **That framing accepted the premise that the
board had to carry the rule at all**, and Ruling 349 dissolved it instead — *a
rule was never the board's to carry.* ⚠️ **A question can be well-posed, answered
correctly, and still be the defect.**

## ⛔ WHAT THE NEXT WAVE IS, AND THE ONE DEPARTURE IN IT

**Wave 10: register round 56, three developer offices, CTO round 71.**

| office | subject |
|---|---|
| Register, round 56 | closes `W170`, `W155`, `W64` on their merge refs; the 17 bytes; two routed observations |
| Developer 1 | **`NS-04` and `NS-06`** — the sibling `../narrate-service` and one `workspace.json` line |
| Developer 2 | **`NS-05`** — `narrate/client.py`, where R7's boundary lives in code |
| Developer 3 | **`W167`** — `check_handoffs`'s unreachable arm, its hold behind `W64` discharged by this wave's merge 4 |
| CTO, round 71 | the four branches, taken as they land |

⛔ **THE ONE DEPARTURE, AND IT IS MINE TO DEFEND.** `PO-55/1` placed
`NS-04`, `NS-05`, `NS-06` in three developer slots. **I filled them with two
offices, not three**, because `NS-04` and `NS-06` are NOT disjoint. The ground
is measured, not assumed: `git log --oneline -5 -- workspace.json`, ROLE main
checkout, ref `1a55e12`, host — **five consecutive sibling landings, five pin
bumps, one line of one file** — and `git worktree list` inside
`../narrate-service` prints exactly one row, `main`, with zero remotes. ⭐ The
rule applied is the board's own: *"ONE OWNER or two waves, never two takers in
one."* ⚠️ **Round 56 is told this by id and can refute it.**

⚠️ **The wave's real interaction is Ruling 340's and it is in no diff.**
Developer 3 widens an instrument whose population is DOCUMENTS while Developers
1 and 2 add three documents to it. ⛔ **Developer 3 therefore merges LAST among
the developers — and ordering a branch last is not measuring it**, which is this
wave's own lesson: build the combined ref and measure it before anything merges.

**Two observations routed to round 56, neither decided by anyone:**
1. `CTO-70/16` — **Ruling 70 already covered the stale-byte-code hazard** and
   reached neither the office writing a sweep nor the reviewer reading one. Both
   the reviewer and I declined to mint: *"the real defect is reach"*, and a
   second ruling is *"exactly the second copy that can disagree."* Row-shaped.
2. The `ONBOARDING.md` control above, as live evidence for the standing rule.

## ⚠️ FOR THE USER, PARKED AND NOT DECIDED

⛔ **A SECOND REVIEWER is the only change that would materially raise
throughput, and it is not mine to make.** Every wave now ends in a serial queue
at one office: this one spent two re-takes and a verdict correction there while
three developer branches sat measured and green. ⚠️ **It is parked rather than
proposed because it SPLITS the verdict discipline and Ruling 305's merge order,
both of which the user set as non-negotiable** — two reviewers means two verdict
authorities, and the register has spent three rounds proving what a second copy
of anything costs.
