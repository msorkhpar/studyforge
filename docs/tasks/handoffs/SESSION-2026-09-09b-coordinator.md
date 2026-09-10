# SESSION-2026-09-09b — coordinator handoff

**Release tip:** `release/m0-foundations` — **2490 passed, 8 skipped, floor clean** (pinned).
**M0 is CLOSED. M1 step 1.3 is CLOSED. Step 1.4 is open.**
**Written by:** the orchestrating session. Read this before `SESSION-2026-09-09-coordinator.md`,
which it supersedes on two points marked ⛔ below.

---

## ⛔ Read the INDEX, not the chain

The predecessor called `handoffs/CTO-*.md` the most valuable thing here and implied
reading it. **It is 389KB / 7,508 lines — about 97k tokens per agent, per fire.**

⭐ **Read the rulings index instead** (in `CTO-2026-09-09-round17.md`): rulings 15–56,
one line each, **with where each landed**, and `↺` marking the eight that contain a
reversal. Read a full round **only** where `↺` says there is an argument rather than
a conclusion.

⛔ **This is not a downgrade of the chain — it is C6's payoff.** Every ruling that
still *binds* was carried into the artifact it governs (the rubric, the conventions,
a task's Acceptance). **The chain is now reasoning, not authority.**

---

## ⛔ The context finding — read this before spawning anything

**An agent's context is mostly the coordinator's prose, and it compounds every round.**

Measured this session: four long-lived agents reached **3.1MB–6.2MB** of transcript
(`~/.claude/projects/<project>/<session>/subagents/*.jsonl`). Every `SendMessage`
resume replays the agent's whole history. The coordinator sent each agent a dozen-plus
briefings of 800–1500 words, densely formatted, **each appended permanently.**

**What to do instead:**

1. ⭐ **Fresh agent per wave.** Retire and respawn at a milestone or step boundary.
   Everything an agent needs is in the repository — that is what the repository is for.
2. ⛔ **A brief is a verdict, a constraint, and the one ruling that shapes the work.**
   Not the reasoning chain. The reasoning is in the index and the conventions.
3. ⭐ **Point, do not restate.** *"Ruling 46 applies — read it in the index"* costs a
   line; quoting it costs a page and goes stale.
4. ⚠️ **`ListAgents` does not list in-process subagents.** It lists sessions and peers.
   It returning "no reachable agents" is not evidence your subagents are gone.

---

## Where the work is

**Merged this session: 92 commits, 87 new source files, +14,025 lines, tests 1761 → 2490,
skips 46 → 8.** Every merge carries its verdict in the message.

**Done:** SF-23 · SF-25 · SK-01 · FND-07 · **FND-05a (closes M0)** · W1 · W2 · W3 · W6 ·
W7 · W8 · W13 · W14 · W17 · W18 · W19 · W20 · rulings 37/42/46 implemented.

### ⛔ Branches left open — deliberate, not forgotten

| branch | state | what to do |
|---|---|---|
| `feat/SF-10-unit-builder` | 1 commit, **2568/8, floor clean** | **needs a CTO verdict.** Built to its own reviewed survey |
| `chore/cto-round17` | 2 commits, **CONFLICTS** | ⛔ Both sides are the CTO's own appends to their handoff. **A handoff is a record — a fresh CTO resolves it, not a coordinator by hand** |
| `feat/W14-invalid-fixtures` | superseded | content is on the tip under `fix/W14-W18`; safe to delete |
| `fix/describe-keys-contract` | superseded | content is on the tip under `fix/ruling-37-describe-keys`; safe to delete |

**W25 was never started** — no branch, nothing lost.

### ⚠️ Two exceptions this coordinator recorded rather than hid

1. **`chore/po-round17`'s 9 commits merged without a fresh CTO verdict.** Docs-only;
   measured in the pinned container instead. Reversible. It carried the board split,
   M0's closure, rulings 44–56, the spec's R9 row and `CLAUDE.md`'s wave-open check.
   ⛔ **Until that merge, the board split existed only on a branch while this
   coordinator reported it as the tip state** — branch state quoted as tip state,
   the defect this session catalogued five times.
2. **The rulings index lists four rulings as unlanded.** Verify before trusting it;
   the column is an audit, and it found six the first time it was run.

---

## Next, in order

1. **`feat/SF-10-unit-builder`** — CTO verdict. Its two findings need rulings:
   **59** ⛔ W7's gate-coverage tell cannot distinguish *decoding* from *delegating*,
   and Ruling 50 makes that difference load-bearing. The narrowing shipped and **is
   offered for ratification, not assumed.**
   **60** ⛔ one R7 refusal, two behaviours: `unit/content.py` translates
   `PersonalDataLeak` into `ContentError`, so a caller looping over units **logs a
   leak as "that unit did not build" and finishes.** Not changed — that file is SF-09's.
2. **W25** — Ruling 49's handoff contract, machine-checked. `tools/quality`.
   ⚠️ Binds `<TASK-ID>.md`: the first non-handoff in that directory was a **survey**,
   and a naive migration would demand six sections of a document that owes none.
3. **Ruling 43's task** — repo-wide walks. It owes **four**: corpus names (done as W20),
   dangling pointers, sweep-by-declaration, and the board's own pointers. ⛔ **Scope the
   fixture-access seam once, not four times**, and re-price it: **Ruling 55 says the
   migration is whatever the check finds** — W20's ruling said 7 and the check found 19.
4. **Step 1.4 proper** — the PO holds the row order.

### Open questions nobody in this session could answer
- ⛔ **SK-01 finding 45** — the Java corpus's `exercises: true` rests on **168 of 792**
  files that *look* like graders. Marked **`UNOWNED until E07 opens`, and it gates.**
  ⭐ PO-Integration **refused it correctly**: *a question routed to the wrong owner comes
  back answered, and nothing marks the answer as unaccountable.*
- **ISO gained a fourth container.** `TestCases.md` is not a unit and not an aggregate:
  all 38 units are linked from *inside* a `#` heading; it is the only one of 39 targets
  linked *as* one. 38 → 55 units if ingested. Whether to ingest is Q5 and is not the
  integrator's call. ⛔ **If the answer is "exclude", the `why` cannot say "duplicate".**

---

## ⚠️ What will bite you

1. ⛔ **A docs-only merge reds the suite.** FND-07's tripwire watches `docs/`.
   Fix: `graphify update . && python3 -m tools.knowledge bridge`. Seconds. **Designed** —
   a trial-merge worktree has no index, sees *absent*, and passes, so the C5 gate keeps
   working while the main checkout goes red.
2. ⛔ **Check the CTO's branch every round.** Verdicts sat unmerged for seven commits
   while a developer waited (Finding 52). ⭐ **A ruling can wait for a wave; a verdict cannot.**
   And ⭐ **an announcement is not a hand-over** — a hand-over names what the reader must do.
3. ⚠️ **`graphify path`/`explain` need NODE IDS, not prose labels.** The label form
   resolves silently by score — it once answered an R7 question from a fixture built to
   *violate* R7. `graphify.md` carries the working form and a test enforces it.
4. ⚠️ **Clean up worktrees when you retire agents.** 22 stale ones blocked this session's
   start by holding branches checked out. Done for this session's four.

---

## ⭐ The rulings that changed how this project works

- **Enumerate the legal, never the illegal** — first section of `module-structure.md`.
  ⛔ **And its domain limit:** enumerability is a property of the *domain*, not a choice.
  Where the permitted set is writable, enumerate it. Where it is free text, the forbidden
  list is **forced and known-incomplete**, and the answer is defence in depth, every layer
  asserted.
- **A guarantee does not extend to what sits beside it** (56) — *a file being clean is not
  a property of the file.* Placed beside the rule above **because it bounds it.**
- **A test beats an acceptance clause beats a board row** — measured, not argued: W14 was
  routed all three ways. The test landed with nobody told; the clause was half-met with the
  reviewer as backstop; **the board row evaporated twice, silently.**
- **Every negative control is itself run negatively.** ⛔ **Six instances this session of a
  check that could not fail reporting success — two the CTO's, one the coordinator's.
  All were probes.** Never a task's own tests, where *watch it fail first* already applied.
- **A ruling states the scope it was argued over** (52), and **a number in a ruling is a
  measurement from an instrument, never a property of the tree** (55). ⚠️ Same defect, two
  grammars. ⛔ **And this project's own carrying machinery propagates an over-broad rule
  faithfully and fast — the better the delivery, the more expensive the over-reach.**

⭐ **The one line to read first, from the CTO:** *the rubric had five defects this round and
every one was found by **running** it, never by reading it.*

---

## On `graphify`, honestly

R14 says agents ask the graph before exploring and every `Context` budget assumes it.
**This session produced one clean instance** — SF-10's survey answered the structure
question from 41 line-anchored nodes before opening a file — **and a lot of
counter-evidence**: the census work, the defect hunting, and every measurement that
changed a decision came from `grep`, purpose-built probes and `pytest`.

⭐ **FND-07 bridged the framework's own graph**, so `R7 --implemented_by--> assert_clean()`
now answers in one hop (15 → 222 cross-file prose↔code edges). **That is the one thing
nothing else does.**

**Recommendation given to the user: keep the index, drop R14's mandate.** The graph answers
*ruling ↔ code*; for everything else, measure directly. The board records both directions
deliberately, because ⛔ *a board that records only the counter-evidence produces a plan
nobody trusts.*
