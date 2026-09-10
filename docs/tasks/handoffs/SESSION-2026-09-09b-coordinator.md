# SESSION-2026-09-09b — coordinator handoff

**Status:** M1 step 1.3 CLOSED. Step 1.4 open, two developers mid-task.
**Release tip:** `5ebf83e` — **2343 passed, 8 skipped, floor clean** (pinned container).
**Written by:** the orchestrating session, for whoever picks the work up next.

⚠️ **Read the predecessor's handoff first** (`SESSION-2026-09-09-coordinator.md`) — its
warning still holds: the CTO, both developers and both POs were **in-process
subagents**. They cannot be restarted or reattached. Everything they knew is in
this repository or is gone.

⛔ **But one thing it says is now WRONG and would cost you ~97k tokens:** it says the
`CTO-*.md` chain is the most valuable thing here and implies reading it. **Read
`the rulings index` instead** — rulings 15–52, one line each, with *where each
landed*, and `↺` marking the eight that contain a reversal. Read a full round
**only** where `↺` says there is an argument rather than a conclusion. The chain is
389KB / 7,508 lines; the index is ~50 lines. **This is deliberate, and it is C6's
payoff: every ruling that still binds was carried into the artifact it governs.**

---

## What closed

**M1 step 1.3 — CLOSED.** SF-23, SF-25, SK-01, FND-07 all merged.
**Fifteen branches merged**, every one with its verdict in the merge message.
**Verdicts: 9 APPROVE, 3 CHANGES REQUESTED, 0 REJECT.**

Skips went **46 → 8**. The 8 are two causes structurally unfixable by an image
(5 in-image recursion guards, 3 absent sibling repositories), and **Ruling 38
makes a ninth cause unrepresentable**: every skip declares a cause from a closed
named set, and a skip for a missing tool has no cause to declare.

⭐ **`R7 — No personal data reaches disk or the wire --implemented_by--> assert_clean()`
now answers in one hop.** FND-07 bridged the framework's own graph: 15 → 222
cross-file prose↔code edges. That is the question the predecessor said the index
could not answer.

---

## In flight — do not re-dispatch these

| Who | Task | Branch |
|---|---|---|
| Developer 1 | **FND-05a** — the pin file. Closes M0. | `feat/FND-05a-workspace` |
| Developer 1 | *first*: Ruling 46 handoff fix — 3 headings, 2 markers | `fix/ruling-46-sweep-declaration` @ `68a269b` |
| Developer 2 | **W20** (repo-wide §7c + its 7 migrations + Ruling 47), then **W25** | not yet cut |

**SF-10 is unblocked** by rulings 50 and 51 and waits on W20. It is a **Team**
task for both developers. Its survey is merged: ⛔ **W5's "827 lines" is right
about the file and misleading about the task — ~250 lines are left to port.**

---

## ⛔ The rulings that changed how this project works

**Enumerate the legal, never the illegal.** First section of `module-structure.md`.
Five rulings converged on it independently. ⭐ **And it has a domain limit, which
matters as much as the rule:** enumerability is a property of the *domain*, not a
choice. Where the permitted set is writable — keys, versions, profiles, skip
causes, contract fields — enumerate it. Where it is free text, the forbidden list
is **forced and known-incomplete**, and the answer is never a longer list: it is
defence in depth, every layer asserted.

**A test beats an acceptance clause beats a board row.** Measured, not argued:
W14 was routed all three ways in one session. The test landed with nobody told;
the acceptance clause was half-met with the reviewer as backstop; **the board row
evaporated twice, silently.**

**Every negative control is itself run negatively.** Five instances of *a check
that cannot fail reporting success*, including one of mine. **All were probes** —
a reviewer's or coordinator's — never a task's own tests, where *watch it fail
first* already applied.

**A ruling states the scope it was argued over** (Ruling 52). Its tell: ⛔ **the
ruling reads *better* than the argument.** ⚠️ And it is the known cost of this
session's own machinery — C6 makes a ruling reach its artifact, *quote don't
summarise* makes it arrive verbatim, **and both propagate an over-broad rule
faithfully and fast.**

**An announcement is not a hand-over.** A hand-over names what the reader must do.

---

## ⚠️ What will bite you

1. ⛔ **A docs-only merge reds the suite.** FND-07's tripwire watches `docs/`.
   Fix: `graphify update . && python3 -m tools.knowledge bridge`. Seconds.
   **Designed. A trial-merge worktree has no index, sees *absent*, and passes —
   so the C5 gate keeps working while the main checkout goes red.**
2. ⛔ **Check the CTO's branch every round.** Verdicts sat unmerged on one for
   seven commits while a developer waited (Finding 52). A ruling can wait for a
   wave; **a verdict cannot.**
3. ⚠️ **`graphify path`/`explain` need NODE IDS, not prose labels.** The label
   form resolves silently by score and can answer from the wrong node — it once
   answered an R7 question from a fixture built to *violate* R7. `graphify.md`
   carries the working form and a test enforces it.
4. ⚠️ **Ratio, denominator, and the set it is over.** An unlabelled `7.9%` caused
   a developer to build a 969-edge bridge before measuring. Three numbers were
   quoted at the wrong scope this session.
5. ⛔ **The board is 68KB and its history is in `BOARD-ARCHIVE.md`.** Sections
   were **moved whole, never summarised.** Do not shorten in place — that breaks
   *more reasoning, not less*, which the live file now restates so nobody does.

---

## Open, with owners

**Unlanded rulings:** 30 (PO, spec text + asserting test to Dev 2) · 43, 47 (in W20) ·
52 (PO — landed at `d55fdda`, verify) · 48 (landed at `d55fdda`) · 49 (`W25`, Dev 2).

**Open questions nobody here can answer:** SK-01's finding 45 — the Java corpus's
`exercises: true` rests on **168 of 792** files that *look* like graders. ⛔ Marked
`UNOWNED until E07 opens`, **and it gates**: nothing declares `exercises: true`
until somebody is accountable. ⭐ PO-Integration **refused** it correctly — *"a
question routed to the wrong owner comes back answered, and nothing marks the
answer as unaccountable."*

**ISO gained a fourth container.** `TestCases.md` is not a unit and not an
aggregate: every one of the 38 units is linked from *inside* a `#` heading, and it
is the only one of 39 targets linked *as* one. 38 → 55 units if ingested. Whether
to ingest is Q5 and is not the integrator's call. ⛔ **If the answer is "exclude",
the `why` cannot say "duplicate" — it is not one.**

---

## ⭐ What I would tell you before anything else

**The rubric had five defects this round and every one was found by *running* it,
never by reading it.** That is the probe rule, the inhabitation rule and *`0 = 0`
is not a pass* all pointing one way: **an instrument is evidence about itself only
when executed.**

⚠️ **And on `graphify`, honestly:** R14 says agents ask the graph before exploring
and every `Context` budget assumes it. **This session produced one clean instance**
— SF-10's survey answered the structure question from 41 line-anchored nodes
before opening a file — **and a lot of counter-evidence**: the census work, the
defect hunting, and every measurement that changed a decision came from `grep`,
purpose-built probes and `pytest`. My recommendation to the user was **keep the
index, drop the mandate**: the graph answers *ruling ↔ code*, which nothing else
does; for everything else, measure directly. The board now records both directions.
