# Board — live status

**Single source of truth for what is in progress and what is done.** Owned by
the framework Product Owner. Task *definitions* live in the epic documents
(`E00`…`E13`); this file carries only **state**.

✅ **M0 COMPLETE. M1 steps 1.1, 1.2 and 1.3 COMPLETE.** ⏳ **M1 step 1.4 is OPEN** —
`SF-10`, the unit document builder. **`W14` and `W18` landed and the gate
cleared.**

📏 **Base, measured in the pinned container at `ac4ed55`: 2274 passed, 8 skipped,
quality floor clean.** ⭐ **Skips 46 → 8**, both remaining causes structurally
unfixable by an image.

⛔ **Release branch: `release/m0-foundations`, and M1 continues on it.** ⚠️ **Its
name is historical, not descriptive** — there is no `release/m1-*` and there never
was; the milestone-naming scheme is retired, and the argument is in
[`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md). Developers branch off it, the CTO reviews
against `../conventions/review-rubric.md`, only reviewed work merges back. Flow:
`../conventions/delivery-flow.md`.

## ⛔ This file was split, and here is the number

⚠️ **`BOARD.md` reached 1,615 lines / ~180KB — roughly 45k tokens — and every
agent is told to read it. It doubled in one wave.** ⛔ **It had become the single
largest per-agent cost in the project**, on top of the rubric (1,025 lines),
`agent-protocol.md` and `module-structure.md`.

⭐ **Live board ~56KB; [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md) holds the rest.**

⛔ **Nothing was summarised. Closed sections moved *whole*, unedited**, because my
own standing rule is that the board must carry **more** reasoning, not less — and
⚠️ **a condensed copy would have been the stale-copy defect this document has
already committed four times.** ⭐ **The split is not *old versus new*: it is
*what a per-task agent must load*.** A developer needs their rows and the standing
rules; the CTO needs open findings and the register; **only the PO needs the
history.**

⚠️ **Built in the order `SK-01` proved matters: the archive was written and every
moved section verified present *before* anything was removed here.** ⛔ **The
reverse order gives a green suite and a board full of dangling pointers, and
nothing mechanical catches it** — which is why `W21`'s pointer walk now has a
second consumer.

⚠️ **M1 is the riskiest milestone** — where every contract meets every other one
for the first time — so ordering *inside* a step matters, because a contract that
merges first becomes the shape the next tasks copy.

⭐ **And the standing rule the split was designed around, restated because it is
load-bearing and must not be read as weakened: this board carries *more*
reasoning, not less.** The entries that paid for themselves were the ones
recording **why** — X2's dissolution, G1's recorded loss, the flattering review
base — ⛔ **because a recorded *why* is what stops a question being re-asked by
the next agent.** ⚠️ **The split changed *where* the reasoning lives, never
whether it exists**: closed reasoning moved whole to the archive, and ⛔ **a
future editor who shortens a section instead of moving it has broken this rule,
not applied it.**

*Statuses:* `todo` · `in-progress` · `in-review` · `blocked` · `done`.
*Editing rule:* a status change is one cell. Do not restructure rows; record
events in the **Log**, which lives in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md) and
is appended to there.

### ⛔ The editing rule that this document kept breaking: **a summary points, it never restates**

⚠️ **Four instances in one milestone, three of them in this file.** The release
branch that never existed; the index recorded present when it was absent; the C5
row saying *"CTO to rule"* three screens above the section reading *"✅ RULED"*;
and the R21 register carrying **two** rows the spec had already closed.

⭐ **They are one defect wearing four costumes, and the shape is now the finding
rather than the four corrections.** ⛔ **A summary that restates a status owned
somewhere else is a copy, and a copy goes stale in exactly one direction: the
summary is what people read, the source is what people update.** So the summary
is where the *wrong* answer lives and the busy reader is the one who gets it.

⛔ **The rule, and it binds this document first:**

- **A status table carries a pointer to the section or the source, never a
  restatement of it.** *"✅ RULED — see the C5 section"* is a summary. *"Options
  1 and 2, option 3 refused"* in a table is a second copy.
- **A register of things owned elsewhere is derived from that source, not
  maintained beside it** — R21's register is now the reasoning behind §R9's
  `open` entries, and §R9 is what says which are open.
- ⚠️ **This is the same argument as C2's** (*a convention that repeats its own
  definition is the defect it polices elsewhere*) and the same as the single
  block-type list, the single size ceiling and the single review base. ⭐ **The
  fourth appearance is where it stops being a coincidence.**

⛔ **Standing user decision: nothing is ever pushed to any remote. Everything
stays in local repositories.** Permanent, not a phase. ⚠️ It changed the plan
rather than the workflow: **R18 is amended**, git submodules are **not used in
this project**, `FND-05b` is **cancelled**, and `FND-05a` becomes a tracked pin
file verified against the local checkouts. ⭐ **B2** and **G1**, both closed, are in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md).

---

**M0 — Foundations: ✅ CLOSED 2026-09-09**, green in the container, 124 passed / 8 skipped. ⭐ **Its sequencing argument, the C1/C4/B2/G1 items and the FND-05b cancellation are in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md), whole and unedited.** ⚠️ `FND-05a` is the one M0 task still open and it gates nothing.

---

**Open questions: ⭐ none.** Q1–Q7, X1 and X2 are all ruled, merged and carried into the tasks they touch — **the reasoning is in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md)**, kept because it is what stops them being re-asked. ⛔ **An empty list is not evidence that no contract is unlocated** — that is R21's register below.

---

## R21 — the register of unlocated contracts

⭐ **R21 was adopted by explicit user decision**, and it generalises Q1–Q3: *a
contract is located before it is described* — the file it lives in, the key that
versions it (R9), and the one producer that writes it, all stated **before** any
task builds against it. ⛔ A task that meets an unlocated contract **stops and
asks**; choosing quietly is the failure the rule names.

⭐ **The rule earned its number by being surveyed rather than assumed.** Asking
"where else is this true?" turned up **five more instances already sitting in the
spec with no owner**. These are board items, not spec trivia: each is owed by the
task named beside it, *before* that task builds.

| Open row | Owed before | Owner | Why it bites |
|---|---|---|---|
| ~~**authored overlay** `content.json` — unversioned~~ | ~~SF-09~~ | CTO | ✅ **CLOSED by SF-09 — three open rows, not four.** ⭐ **Verified in the tree rather than inherited from the handoff:** `content_api` is minted in `src/studyforge/version.py`, sits in `CONTRACT_FIELDS`, and `test_the_overlay_is_versioned_and_the_key_is_content_api` asserts it — 23 occurrences across `src/` and `tests/`. R9 **gained** the contract rather than excusing it, and the spec now points at the constant instead of re-listing five names, which is why *"R9 lists five and there are seven"* cannot recur |
| **discovery cache** `.studyforge/site.json` — no version key | **SF-04** (M2 step 2.1) | CTO | R9 refuses an unknown version rather than migrating; a cache with no version cannot be refused, only misread |
| **narration manifest** — no file, no version | **NS-02 / SF-17** (M3) | CTO | Two producers named for one contract is Q3's shape exactly, and Q3 needed a ruling |
| **coverage report** — no file | **EX-05** (M7) | CTO | Not read back, so the cheapest of the five — but R5 is what the report exists to make honest |
| ~~**component consuming contract** `consuming.json` — no version key~~ | ~~TC-05, E13~~ | CTO | ✅ **CLOSED — and this board was stale by two rows, not one** (CTO round 17, ruling 16). `consuming_api` is in spec §R9. ⭐ The reasoning survives and is worth keeping: the pin file records **which commit**, `provides` records **the promise**, `consuming_api` versions **the schema** — three different questions that G1's answer only looked like it had all covered |

⛔ **Ruled (round 17): this register stops being a second copy of §R9 and becomes
a pointer to it.** ⚠️ **Two of its five rows were stale simultaneously**, both in
the same direction — closed in the spec, open here — which is precisely how a
duplicated status behaves. ⭐ **The open set is whatever §R9 marks `open`**; the
rows below are kept only for the *reasoning*, which §R9 does not carry.

**Genuinely open: three, and ⭐ none is due in M1** — discovery cache
(`SF-04`, M2), narration manifest (`NS-02`/`SF-17`, M3), coverage report
(`EX-05`, M7).

⚠️ **`consuming.json` is now the sharper half of what G1 covered.** ⭐ G1's answer
restores *which commit of each component* — that is what `FND-05a`'s pin file
records. It does **not** restore *which version of the promise* each component
made, which is the contract's own job and is still unversioned. ⛔ So a corpus can
now say which components it was built against and still not say what they
guaranteed — and that gap sits on the **runtime seam between the two agents**,
which is the one seam neither can inspect from their own side.

---

**Delivery-process defects C2, C3 and C5: ✅ all ruled and closed.** ⭐ **C5's ruling — options 1 *and* 2, option 3 refused — and the meta-finding the CTO rated above it are in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md).** ⚠️ Its residue is live in two places that are not this board: the standing rule in `FND-06` and the trial-merge step in the rubric's §0a.

---

**M1 step 1.1: ✅ CLOSED.** SF-01, SF-02, SF-07, SF-08, SF-11, SF-33 and the FND-04 follow-up all merged. ⭐ **The lane assignment and the collision-pair reasoning it validated are in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md)** — worth reading before assigning a step, because it is where the rule was first tested.

---

**The release-branch reconciliation: ✅ ruled and closed.** ⛔ **Standing outcome, kept here because it still binds: `release/m0-foundations` is the release branch, its name is historical rather than descriptive, and the milestone-naming scheme is retired.** ⭐ The argument is in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md).

---

**M1 step 1.3: ✅ CLOSED** at `277469e`. ⭐ **Its assignment, the two collision surfaces measured rather than guessed, the `Profile` reversal and the merge-order rulings are in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md).**

---

## M1 step 1.4 — one task, and a gate in front of it

> **Step 1.4 is `SF-10`**, the unit document builder — `Depends on` SF-05, SF-06,
> SF-09, all merged. **Team**-sized, `~70k`, owns `unit/builder.py` and its
> package.

| Task | Owner | Status | Gate |
|---|---|---|---|
| **W14** — two missing invalid fixtures | Developer 1 | ✅ `done` | — |
| **W18** — Ruling 35, `authoritative ⟹ bundled` | Developer 1 | ✅ `done` | — |
| **W23** — the live R7 hole (tilde, `/export/home/`) | Developer 2 | ⏳ `in-progress` | ⛔ **before W20** |
| **W20** — repo-wide §7c check **and its migration** | Developer 2 | `todo` | ⛔ **before SF-10 lands** |
| **SF-10 survey** — port inventory + R11 package shape (**W5**) | **Developer 1, now** | ⏳ `in-progress` | ⛔ **design only, no builder code** |
| **SF-10** — Unit document builder | **both, as a team** | `todo` | when the survey and W20 land |

### ⭐ Developer 1's slot: the survey, not the build

⛔ **`SF-10` is `Team`-sized, so its code is not authored by one person ahead of
the other** — that is the collision-pair rule, and splitting a shared surface is
exactly what it forbids. ⚠️ **But the serial part of `SF-10` is not the code.** It
is **`W5`: `unitdoc.py` is 827 lines against R11's 400**, and R11 is explicit that
the large modules arrive **as packages or not at all**.

⭐ **So Developer 1 takes the survey now:** the port inventory, and **a proposed
package shape with its seams named** — the same deliverable that made `FND-04`'s
split cheap, and the same reason the CTO gave for it there: ⛔ **only somebody who
knows the module's internals can answer where it divides.**

⛔ **Deliverable is a design, not builder code.** ⚠️ Nothing is authored on the
shared surface before the team convenes — ⭐ **which keeps the team task intact
while spending the idle time on the part that was always going to be serial.**

### ⛔ Why W14 and W18 gate the step rather than riding alongside

⚠️ **W18 is not bookkeeping — it is a live correctness hole.** Measured:
`FORBIDDEN` still carries only the `generated` pair, so ⛔ **a grader the reader
wrote can declare itself the source's own.** That is R5 failing open, and
`SF-10` is the task that assembles what a reader is shown.

⛔ **And letting them ride alongside is what already failed, twice.** They rode
alongside SK-01 and did not land. ⭐ **A thing that has evaporated twice does not
get a third trigger; it gets a gate.**

### ⭐ Scoped before the task is written: **W20 ships a fixture-access seam, and three walks consume it**

⛔ **Decided now because the CTO asked for it before scoping, and because three
tree-walks are about to be written by three different people.** Ruling 43's task
owes **corpus names**, **dangling pointers** (Finding 50 / `W21`), and **Ruling
45's sweep** — ⚠️ **and the board split just added a fourth consumer**, since
every `BOARD.md` pointer into the archive wants the same walk.

⛔ **Ruling 45 states the rule the seam has to implement:** *a sweep asserting
property P excludes exactly the fixtures **declared** to violate P — read from the
declaration, never from the directory name.*

⭐ **The machinery already exists and is unused.** Every invalid fixture carries a
**`VIOLATION.md` naming its rule**, and `test_invalid_corpus_violates_exactly_
its_one_rule` **already proves that declaration true and singular.** ⚠️ So the
declaration is trustworthy today and nobody is reading it.

⚠️ **Measured, and it is why the seam is not a nicety:** all **7** invalid
fixtures agree with the block vocabulary, so `including_invalid=False` drops **9
documents that should be swept** — ⛔ **each invalid in one named way and correct
in every other.** ⭐ Developer 1's fix **stands until this task**: it is correct,
it stops the false red, and it is honest about what it does.

⭐ **And it is *enumerate the legal* again:** a directory name is an open set
somebody keeps extending; ⛔ **`VIOLATION.md` is a closed declaration that already
has an enforcer.** The seam answers one question — *which fixtures should be
swept for property P?* — and four walks stop each inventing an answer.

### ⛔ W20 before SF-10, and it is the third instance of one sequencing shape

⭐ **Ruling 43 measured 7 §7c hits already on the release branch** — `exercise/
states.py` (4), `archive/scrub.py` (1), `address/__init__.py` (2) — ⚠️ **all
predating this work.** So a repository-wide check **goes red the moment it
lands**, and Developer 2's finding 1 is ruled: ⛔ **a commit adding a check owns
its migration.** One task, one commit: the check plus those 7 moved. ⭐ Exemption
generalises as ***exempt documents, never modules.***

⚠️ **`SF-10` is a ~70k builder that will add emission sites.** Landing the check
after it means migrating more than 7 — which is `W6`'s argument (*a check that
arrives after twenty sites exist is one nobody turns on*) and `W13`'s (*a fixture
authored while the checker is weak was never actually bounded*). ⛔ **Third
instance of one shape, so it is a rule now and not a judgement call: a check and
the code it will judge are ordered check-first, or the check inherits a backlog
it did not cause.**

### ⭐ Why both developers take SF-10 together

`SF-10` is **`Team`**-sized in its own definition, and ⛔ **that is not the
collision-pair rule being broken — it is the rule's premise.** The pair rule
exists so a shared surface is not *split*; a team task is one surface with two
people **in** it. ⚠️ It also carries **W5**: `unitdoc.py` is **827 lines against
R11's 400**, and R11 is explicit that the large modules arrive **as packages or
not at all**.

---

## The wave-open checks — ⛔ **four**, run 2026-09-09 by the PO

⛔ **All four are mine and all four run before the wave, not after it.**

| # | Check | Command |
|---|---|---|
| 1 | Index present and current **in the main checkout** | `built_at_commit` vs `git diff --quiet <it> HEAD -- src tools docs` |
| 2 | The `[structural]` triage list | `grep -rn '\[structural\]' docs/tasks/handoffs/` |
| 4 | ⭐ **NEW — nothing ruled is queued-but-unlanded across the boundary** | ask each document owner; ⛔ **and re-measure every board row whose trigger has passed** |
| 3 | ⭐ **C6: every ruling made since the last wave reached its artifact** — ⛔ **and it stays exactly here** (Ruling 39) | for each, open the task/epic/spec/convention it names and read the clause — ⛔ **and the neighbouring rulings in it, not only the clause being added** |

⚠️ **Check 3's scope, corrected on a measurement (Ruling 39) — I had this wrong.**
I proposed it belonged *closer to the code*, because an author caught a collision
this check did not. ⛔ **Measured: a sweep of the release tip at that moment would
have found three files and none was the colliding guard — it lived only on an
unmerged branch.** ⭐ **Distance was never the problem; the code was not in the
tree the sweep reads.** ⚠️ **And *"move rather than grow"* was the wrong
dichotomy — the answer is neither.**

⛔ **A check covers what is there; a broadcast covers what is coming.** This check
is the backstop for rulings whose subject is **already merged** — a real,
non-empty, otherwise-unwatched set.

### ⛔ Check 4, and the measurement that forced it — **a board row is the weakest destination there is**

⚠️ **Measured on the release tip `277469e`, 2026-09-09, opening step 1.4:**

| Item | Ruled | State on the tip |
|---|---|---|
| **W14** — the two missing invalid fixtures | ✅ ruled twice | ⛔ **`tests/fixtures/invalid/` holds FIVE.** Not landed |
| **W18** — Ruling 35, `authoritative ⟹ bundled` | ✅ ruled | ⛔ **`FORBIDDEN = (("generated", "authoritative"),)`** — the `generated` pair only. **`user` + `authoritative` is still accepted today** |

⛔ **Both were routed to Developer 1 *"with W14, before SK-01"*. SK-01 merged.
Neither travelled, and there is no review left to catch them.**

⭐ **This is the destination hierarchy proving itself, and W14 is the controlled
experiment because it was routed twice, two different ways:**

| Destination | What happened to W14 |
|---|---|
| ⭐ **a failing test** | *"The failing SF-02 test was the instruction."* The graded fixture shipped **without anybody being told** |
| **an Acceptance clause** | ⚠️ half-met — but **the reviewer was the backstop and it was caught in review** |
| ⛔ **a board row with an owner and a trigger** | ⛔ **evaporated, twice, silently** |

⛔ **So: a board row is a destination only for work nobody is currently in a
position to encode as a test or a clause.** ⚠️ **W6–W13 gave eight rulings a
destination and that was the right fix for having none — but I recorded it as
though all destinations were equal, and they are not.** ⭐ **A trigger that names
a task is only as good as somebody re-reading the board when that task ends** —
which is precisely the re-read that check 4 now forces.

⛔ **Step 1.4 does not open until W14 and W18 land** — see the step 1.4 section.
⚠️ Opening a wave while two ruled items sit unlanded is the exact defect check 4
was added to catch, and adding the check while committing the defect would make
it a rule nobody believes. ⭐ **The branch half is a *broadcast*
obligation on the ruling's author, not a sweep**, and it is now one command in
`../conventions/agent-protocol.md`: ⛔ **a ruling that changes a shared name names
its blast radius across branches.** ⚠️ Moving either instrument to do the other's
job leaves both holes open.

⛔ **Check 3 exists because checks 1 and 2 cannot see it.** ⚠️ A ruling that was
made, was correct, and never reached the artifact it governs looks **identical to
a delivered one** from every angle the other two checks have: the handoff says
ruled, the review says ruled, and the task that must act never hears. ⭐ **It is
the PO's check because the PO does the carrying**, and ⛔ **it deliberately did
not go to the reviewer** — the carry happens after the review, so a reviewer's
gate could not fire, and a gate that cannot fire is worse than none because it
reads as coverage.

### 1. Index present and current — ⚠️ **FAILED, and it has been fixed**

⛔ **The index in the main checkout was stale, and every agent this wave would
have queried yesterday's tree.** ⚠️ Note the trap this board documented last
round: `graphify-out/` is git-ignored, so a **worktree has no index of its own** —
the check is run against the **main checkout**, and agents reach it with
`--graph`, which is what makes R14 affordable at all.

**Measured, main checkout, `release/m0-foundations` @ `9ad45a2`:**

| | Before | After |
|---|---|---|
| `graph.json` `built_at_commit` | `220ea4b` — **15 commits behind**, 30 files changed | `9ad45a2` ✅ |
| nodes / edges | 3,075 / 6,081 | **3,281 / 6,463** |
| dangling-endpoint edges (`graphify diagnose multigraph`) | **203**, 192 collapsed, 1 self-loop | ⭐ **0 / 0 / 0** |
| code↔prose edges | 232 (3.8%) | 510 (7.9%) — ⛔ still not a bridge |
| `path "R7 — No Personal Data" "assert_clean()"` | no path | ⛔ **still no path, even undirected** |

⭐ **The fix was `graphify update <path>`: incremental, no LLM, no API key, under
a minute.** R7-verified after the rebuild: **zero** home paths in `graph.json`.

⚠️ **Two things this measurement retires, and one it does not.**

- ⭐ **Retired: "203 dangling edges — absence of a connection is not proof of
  absence"** as a *current* claim. The tool's own diagnostic now reports zero
  dangling, zero collapsed, zero self-loops, zero missing endpoints. ⛔ Any
  briefing still carrying the 203 is quoting a record as a status — the same
  defect, and this board is where it gets superseded. ⚠️ **The caution itself
  survives on other grounds** (the graph is unbridged), so do not read this as
  *the graph is now complete*.
- ⛔ **Not retired: the bridge.** `FND-07`'s hardest clause is still owed, and the
  one question this repository most needs answered still returns silence.

### 2. The `[structural]` sweep — ⭐ 32 findings, and it found a hole in its own rule

**Measured:** `grep -rn '\[structural\]' docs/tasks/handoffs/` — **32 findings
across 9 task handoffs** (⚠️ SF-03 carries four, not the two a quick count sees).
FND-01/02/04's 23 pre-marker findings were back-triaged last round and are not
re-swept.

⭐ **Only two are undispositioned, and both are correctly *accepted with the cost
named*** — which is one of the three legal outcomes, not a shrug:

1. **`SF-33` finding 3 — `api` is a generic field name.** The tree guard would
   flag a module reading an unrelated `api` key. ⭐ **Zero instances today** and
   the finding states its own remedy (narrow the rule to the module rather than
   drop the field). ⛔ **Accepted**, owner is whoever first mints a colliding
   field — realistically `SF-10` or the E03 TOC task.
2. **`SF-09` finding 3, routing half — the extraction source's `naming.py`
   docstring says 1,282 where the tree holds 1,290.** ⭐ **Accepted**: it is a
   defect in a repository v1 does not modify (R20), and the *rule* it exercised —
   *a claim about another repository is verified in that repository* — is already
   ruled and applied. ⚠️ Its ask was *"route to whoever owns the drift
   catalogue"*; `DOC-2026-09-09-codesignal-drift.md` predates it and has no entry.
   It goes to **E11's integration catalogue** rather than nowhere.

### ⛔ And the finding that is worth more than either check: **ruling is not carrying**

⚠️ **Thirty of thirty-two were ruled. Eight of those will still evaporate**,
because a ruling that reached no board row, no epic clause and no trigger is a
ruling that lives only in a handoff — ⛔ **and this board's own standing rule is
that a ruling living only in a handoff gets re-derived by whoever picks the task
up.**

⭐ **This is the C5 meta-finding one level down, and the sentence is almost
identical.** Then: *"the protocol said to write findings down; it never said
anyone had to rule on one."* Now: ⛔ **the protocol says to rule on findings; it
never said anyone had to carry the ruling.** The three words — *ruled, scheduled,
accepted* — were treated as terminal, and **only two of them name a destination.**
"Ruled" names a decision and no home.

⛔ **The rule tightens, and this is the correction: a `[structural]` finding is
dispositioned when its outcome has a *destination* — a task definition, an
acceptance clause, or a board row with an owner and a trigger.** ⭐ **A CTO
ruling is the decision, not the delivery**, and the person who owns delivery is
the PO. ⚠️ The test is unchanged and still the right one — *would this happen
again to somebody else?* — it was simply being asked one step too early.

⭐ **The eight are now rows W6–W13 below**, which is the destination they lacked;
three of them were carried into task definitions this round because their
triggers are imminent.

---

**M0 residue: `FND-05a` only**, and it is still the one task that can slip without stopping anybody. ⭐ Reasoning in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md). ⚠️ It should not slip *indefinitely* — the failure it prevents has **no symptom**.

---

**The index defect: ✅ closed by `FND-07`** (merged `1cc4e6d`). ⭐ **The measurement that produced it — 33 worktrees, 2 with an index — and the standing rule it generalised are in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md).** ⛔ **The rule is live and is not archived: no acceptance condition is satisfied by an untracked artifact alone — the task ships the check.**

---

## Open work items — routed, with owners

| # | Item | Owner | When | Note |
|---|---|---|---|---|
| W1 | ⭐ **`require_slug`/`require_ordinal` format `{value!r}`** — every address segment, identity field and unit ordinal inherits an R7 echo, so **7 of 26 emission sites are one pair of lines seen through their callers** | **Developer 2** | ✅ **merged `f569d0e`** | ⭐ **The highest-value single fix available**, and the ratio is why: fixing one pair of lines closes 7 sites. ⛔ A refusal that quotes the value has relocated the leak into a log. ⚠️ **Round 17 finding 9 rides in the same commit:** `AddressError`'s docstring *mandates* the echo this removes |
| W2 | **Behavioural §1f check** — poison an absolute path into each string parameter, fail if the refusal reproduces it. Prototyped, deliberately not shipped. **46 pairs before the label fix, 45 after** | **Developer 2** | ✅ **merged `f569d0e`** | ⭐ It is W1's enforcer: W1 fixes the sites, this stops them coming back. ⚠️ A delta of one, reported honestly, is exactly the number that makes it credible. **Measured since:** 6 of 10 poison shapes reproduced an identifier in a `validate` report; 10 of 10 clean with W1 prototyped |
| W3 | ⚠️ **Fixture defect, found by a graph build rather than a test** — `depth1/.../media/diagram.svg` says *"Two nodes and an arrow"*, its lesson's `alt` says *"…joined by one arrow"*, and the geometry is an undecorated `<line>` with **no marker and no arrowhead**; the two accessible names also differ in wording | **Developer 2** (FND-04's author) | ✅ **merged** | ⭐ **Worth more than the defect: a graph build found what the test suite did not.** ⛔ **Its old trigger — *"with the next fixture touch"* — named work that is now Developer 1's**, so Developer 2 would have waited forever. A trigger naming somebody else's work is not a trigger |
| W4 | **`handoffs/SF-05.md` still describes `LABEL_FORBIDDEN`** and lists its duplication as open finding 6; both are resolved by the hotfix | PO — ✅ **discharged here** | ✅ done | ⛔ **A handoff is a record and is not rewritten** — my own rule — ⭐ **so this row *is* the correction.** The board is where a superseded record gets superseded |
| W5 | **`unitdoc.py` is 827 lines against R11's 400, and belongs to `SF-10`** — not `SF-06` | `SF-10` | at **SF-10**, step 1.4 | ⭐ Routed with the number so the task inherits it. R11: the large modules arrive **as packages or not at all** |

### ⛔ Ruled: **W7 and W13 are one commit**, and it is Ruling 19's argument again

⭐ **They look like two chores and they are one defect: *the gate's coverage is
assumed rather than asserted.*** ⛔ **W13 is two copies of the gate that
disagree; W7 is one reader that calls no gate at all** — the same hole seen from
its two ends. ⚠️ And the CTO has prescribed the **same remedy for both**: a test
that makes the omission **unrepresentable**, rather than a list that has to be
maintained.

⭐ **That is this project's most-repeated finding arriving for the fourth time** —
*make the illegal value unrepresentable; do not enumerate it.* ⛔ **A
hand-maintained list of readers is how W7 went missing in the first place**, so
fixing W7 by adding a call to a list would reproduce the defect while closing the
instance.

⛔ **One commit, but TWO NAMED TESTS — and my *"one test, not two"* was the loose
version the CTO corrected (ruling 27).** ⭐ *"'One implementation exists' and
'every reader calls it' are different assertions, and fusing them yields one
vague test proving neither."*

⚠️ **The reason to land them together is sharper than the load argument I gave:
separately each has a hole, and each hole is a live defect today.**

| Alone | The hole it leaves | Today's instance |
|---|---|---|
| **W13** alone | one authoritative implementation — **with a reader that never calls it** | ⛔ `corpus.json` |
| **W7** alone | every reader calls *a* gate — ⛔ **and calling the weaker copy satisfies it** | ⛔ `fixture_checks` |

⭐ **So the pairing is not a scheduling convenience, it is what makes either test
mean anything.** ⚠️ **Ruling 14's cross-package refusal does not apply** — that
refused an *unruled hotfix*, whereas ⛔ **C5's standing rule positively requires
the call sites to land with the test.**

⭐ **The combined item inherits W7's deadline, not W13's:** it goes **ahead of
FND-07**, because R7 is the rubric's one HARD FAIL and this one is in the front
door of the command an adapter author is told to trust.

⭐ **And the fact that dates the ordering, which neither the CTO nor I had when we
each reached it (ruling 25): my own `W14` ruling is what makes `W13` urgent.** I
ruled *build the count-mismatch fixture* — so ⛔ **W14 adds a new fixture to the
very tree the weaker gate guards.** ⚠️ *A fixture authored while the checker
misses 3 of 4 home-path shapes and every dict key is a fixture whose boundary was
never actually asserted*, and §1e's whole point is that the exception is bounded
**by tests rather than by memory.** ⭐ That turns a priority call between
abstractions into **a sequencing fact with a date on it.**

⚠️ **Recorded as convergence rather than as an override.** The CTO's text says
ruling 25 overrides `47df43a`; ⭐ **`6acff60` had already moved FND-07 behind
W7+W13 before that ruling landed**, so the two of us reached the same order from
different directions — and *that* is the part worth keeping, because an ordering
two people derive independently is one neither has to defend again.

### ⛔ SK-01's six findings, marked here — the board row **is** the triage

⚠️ **Finding 49, the CTO against themselves: `SK-01` was APPROVEd twice without
§8a, and its handoff carries six findings and zero markers.** ⛔ **The old counter
would have returned `0 = 0` and passed**, so running it would not have helped —
⭐ **which is exactly why the fix was the redesign and not the discipline.**

⭐ **Marked here rather than by editing the handoff — W4's precedent: a handoff is
a record, and the board row is the correction.**

| # | Finding | Marker | Disposition |
|---|---|---|---|
| 41–43 | Defects found and fixed within the task | `[local]` | ✅ **closed in `SK-01`** — no destination owed |
| 44 | ⛔ **The denominator finding** — two of its three numbers came from the integration side | `[structural]` | ✅ **routed to the integration catalogue as `W22`.** ⛔ Not fixed in `SK-01`: a cross-source fact buried in one skill is where the next source cannot find it (R19) |
| 45 | ⛔ **Java's `exercises: true` rests on 168 files that *look* like graders — out of 792 files, ⚠️ and *that* denominator is what the count was missing** | `[structural]` | ⛔ **UNOWNED, explicitly, until `E07` opens — and my routing to PO-Integration was WRONG.** See below. ⛔ **Nothing declares `exercises: true` for the Java corpus until this has an accountable owner** |
| 46 | ⛔ **ISO's record links the 3,863-line `TestCases.md` as its 39th unit** | `[structural]` | ✅ **ANSWERED — it is a fourth *container*.** The ingest decision remains open; see below |

⛔ **45 and 46 are not owed to the framework and must not be answered here.** ⭐
**They are exactly what `SK-01` was built to produce: *"I cannot determine this —
please confirm."*** ⚠️ **A skill reporting an honest uncertainty is the skill
working**, and it would be a defect to resolve them by guessing on the corpus
owner's behalf — R6, and the reason reconnaissance reports rather than decides.

#### ⛔ Finding 45: I routed it to the wrong owner, and the refusal is worth more than the routing

⚠️ **PO-Integration owns ISO. Finding 45 is about the *Java* corpus.** They
declined it, correctly, and ⛔ **the clause that matters is not that I was wrong
but what being wrong would have produced:**

> ⛔ *"Routing it to me would make the mechanism look like it worked while
> producing an answer nobody is accountable for."*

⛔ **That is a new failure mode and it belongs with C6's family: a question routed
to the wrong owner comes back *answered*, and nothing marks the answer as
unaccountable.** ⚠️ **An unaccountable answer and a correct one are
indistinguishable on this board** — and the routing *looks* discharged, so
nobody checks. ⭐ **The refusal was the only thing that could have surfaced it**,
which is why an owner declining a question is a contribution and not an
obstruction.

⛔ **Disposition: `UNOWNED until E07 opens`, stated as a status rather than left
implied.** The Java corpus **has no PO in this session**. ⚠️ **A row that sits
looking answered is worse than an empty one**, so this one says it is unowned in
the field the board reads. ⛔ **And it gates: nothing declares `exercises: true`
for that corpus until the question has somebody accountable for the answer.**

⭐ **The transferable half PO-Integration contributed instead is now catalogue
entry 8** — *runnability is decided by the reader's obligation, not the file's
shape* — ⚠️ **and their own example is the one that proves shape insufficient:
`TestCases.md` is 188 Gherkin scenarios that look exactly like a grader corpus
and ask the reader to do nothing.**

⚠️ **They also turned `W22` back on us, correctly: *"168 of 792"* states a
denominator the source never stated**, so the ratio was unusable where it was
written. ⭐ **One line at the source versus an unrecoverable ambiguity
downstream** — the rule applying to us as readily as to them.

#### ⭐ Finding 46 answered decisively, and it changes ISO's shape

**`TestCases.md` is a fourth *container*. Not a unit, not an aggregate.**

| Measurement | Result |
|---|---|
| link targets in `README.md` | 39 |
| position of `TestCases.md` | 39 |
| markup carrying it (line 310) | `# [Test cases](TestCases.md)` |
| unit links carried by a `#` heading | ⛔ **0 of 38** |

⛔ **Every one of the 38 units is linked from *inside* a `#` heading; not one is
linked *as* one.** `TestCases.md` is linked **as** a `#` heading — same markup,
level and document as the three group headings, and **the only one of 39 targets
sitting where a container sits.**

**Not an aggregate, decisively:** of its **2,524** distinct non-blank lines,
**1** appears anywhere in `src/`, and that one is a bare code fence. The three
real aggregates are digest-identical concatenations.

⭐ **And the sharpest part: the evidence that made it look like an aggregate is
what proves it is a container.** Trap 4's **361 duplicated headings *are* its 17
chapters and their sub-structure**, recorded in the curriculum exactly as the
other containers' units are — ⭐ **so §6's *recorded, never derived* is satisfiable
for it**, which was the objection that would otherwise have sunk ingesting it.

**Consequence:** still depth-1, a fourth `test-scenarios` container of 17 units,
**38 → 55 units**, adding `gherkin` (244 fences).

⛔ **Whether to ingest is a separate, still-open decision — and it carries one
constraint that must not be lost.** ⚠️ **If the answer is *exclude*, the `why`
cannot say "duplicate", because it is not one.** It would be **material withheld
from the reader**, ⭐ **which is X1's exact test** — an exclusion states its
reason, and the reason has to be true.

### ⛔ W6–W13 — the eight rulings that had nowhere to land

⚠️ **Every one of these was ruled by the CTO and every one would still have
evaporated**, because a ruling with no row, no clause and no trigger lives only
in a handoff. ⭐ **This table is the destination they lacked** — see *ruling is
not carrying*, above.

| # | Item | Owner | When | Note |
|---|---|---|---|---|
| W6 | ⛔ **The R7 exception-text check** — any `{exc}` interpolation re-emits the absolute path the inner refusal was careful not to emit. `SF-02` finding 1 and `SF-05` finding 4, ruled round 8: *"build it now — a check that arrives after twenty sites exist is one nobody turns on"* | **Developer 2** | ✅ **merged `f569d0e`** | ⚠️ **`CHECKS` still has five entries and none is this**, four rounds after *"build it now"*. ⭐ The ruling's own urgency argument is the schedule: `SF-04`, `SF-25`, `SF-28` and every adapter each add sites. ⛔ It is a **sibling of W2, not a duplicate** — W2 poisons a *parameter*, this reads a *format string* |
| W7 | ⛔ **URGENT — `corpus.json` is not gated at all.** A home path in the manifest `title` **validates green: zero findings, zero unchecked claims.** ⛔ **The tool an integrator is told to trust (R2) reports the corpus's front door clean.** Plus round 10's call-site table, of which only `SF-06`'s clause had landed | **Developer 2** | ✅ **merged `f569d0e`** | ⚠️ **Verified independently by the PO, not inherited:** `assert_clean` is called from `archive/document.py`, `corpus/container/document.py` and `unit/content.py` — and ⛔ **`corpus/manifest/` (6 modules, `document.py` among them) calls it nowhere.** ⭐ **`validate` was already wired for it: the catch is correct, the raise never comes** — which is why nothing looked wrong. ⛔ **The fix is a test that every reader gates, never a call added to a list** — a hand-maintained list of readers is how this went missing |
| W8 | ⛔ **The dev image has no JS runtime**, so 38 tests can only run off-image. `SF-11` finding 1, ruled round 11 an `FND-03` follow-up: *"not optional and not 'when convenient'"* | **Developer 1** | ✅ **merged `dc4686c`** — ⭐ **skips 46 → 8** | ⛔ E03 and E04 widen this gap from here, and the container is authoritative *because it is pinned*. ⚠️ A claim only provable off-image is a claim the verdict cannot rest on |
| W9 | **The markup contract has one side written** — `surface.py` guesses `SF-12`'s class names. Ruled round 11: **SF-12 reviews the names in one commit as its first act** | `SF-12` | at **SF-12**, step 1.5 | ⛔ Not in `E03` yet. ⭐ *"Its first act"* is a sequencing instruction and it only works if it reaches the task **before** the task starts |
| W10 | **Palette tokens with no painter** — `--hl-*`, `--player-height`, `--practice*` are defined and unclaimed. Ruled round 11: a **named, self-retiring list**, and E04/E08 acceptance gains *remove your token* | PO → E04, E08 | **before E04 / E08 are authored** (M3, M5) | ⭐ Self-retiring is the good part: the list is a number that must reach zero, ⛔ not an exclusion that lives forever. The word *"unclaimed"* currently appears nowhere |
| W11 | **`api` is a generic field name** — the tree guard would flag a module reading an unrelated `api` key. `SF-33` finding 3 | ◐ **ACCEPTED, cost named** | if a colliding field is ever minted — realistically `SF-10` or E03's TOC | ⭐ **Zero instances today**, and the finding states its own remedy: narrow the rule to the module rather than drop the field. ⛔ Recorded so the remedy is not re-derived under time pressure |
| W12 | **The extraction source's `naming.py` docstring says 1,282 where the tree holds 1,290.** `SF-09` finding 3, routing half | ◐ **ACCEPTED, cost named** → E11's integration catalogue | at **SK-07** / the catalogue | ⭐ A defect in a repository v1 does not modify (R20), and the *rule* it exercised — **a claim about another repository is verified in that repository** — is already ruled and applied. ⚠️ Its ask was *"route to whoever owns the drift catalogue"*; `DOC-2026-09-09-codesignal-drift.md` predates it and has no entry |
| W14 | ⏳ **in flight** — ⛔ **TWO missing invalid fixtures on FND-04's surface, and they are one task** — the **count-mismatch** fixture (`E10` names six, five exist) and the **`user` + `authoritative` R5 pair** (finding 29). ⭐ **Both are record defects, not coverage holes: `check_counts` and the trust rule are implemented and tested — only the fixtures are absent** | **Developer 1**, after `W8` | ⛔ **before `SK-01`**, which reads `SF-25`'s output as its model of "valid" | ⚠️ **Measured on `feat/SF-23-exercise` @ `5a01a30`: the graded fixture shipped, the count-mismatch fixture did not** — `tests/fixtures/invalid/` still holds five. ⛔ **`SF-23`'s Acceptance names both, so this is a live review item, not an escaped one** — flagged to the CTO while the branch is in review. ⭐ **That is the mechanism working: routing an item into a task's *Acceptance* rather than a board row is what makes a reviewer the backstop** | ⛔ **An acceptance clause naming a fixture that does not exist is unfalsifiable** — the same class as an acceptance satisfied by an untracked artifact, arriving in a *condition* instead of a build product. ⭐ Ruled: **build the fixture, keep the clause** — it is the only statement that the count check is exercised, and the count check guards *silently lossy ingestion* |
| W23 | ⛔ **LIVE R7 HOLE — two personal-data shapes pass the gate clean.** Confirmed by probe **with a control**: **tilde-rooted paths** and **`/export/home/<name>/`** both carry an account name and both pass. ⚠️ **Blast radius is wider than `origin`** — `assert_clean` walks **every string in a document**, so a title or block text carrying either shape reaches disk. Developer 2's finding 3 (two overlapping refusal sets) joins the same task | **Developer 2** — ⏳ **dispatched** | ⛔ **now, before `W20`** | ⭐ **The remedy is not a longer list** — see the domain limit now carried in `../conventions/module-structure.md`: where the permitted set is free text it cannot be enumerated, so the answer is **defence in depth, every layer asserted**, because no layer is sufficient |
| W20 | ⛔ **Repository-wide §7c check — and its migration, in the same commit** (Ruling 43). **Measured: 7 hits already on the release branch**, all predating this work — `exercise/states.py` (4), `archive/scrub.py` (1), `address/__init__.py` (2) | **Developer 2** | ⛔ **before `SF-10`** | ⭐ **A repository-wide check goes red the moment it lands**, so Developer 2's finding 1 is ruled: **a commit adding a check owns its migration.** One task, one commit. ⭐ **The exemption generalises: exempt *documents*, never modules** |
| W21 | ⚠️ **A fifth rubric gap: nothing checks for dangling pointers after a docs move.** `SK-01` built the far end before deleting the near one — ⛔ *"the reverse order would have produced a green suite and sixteen dangling pointers, and nothing in the rubric would have caught it"* | **CTO** (rubric) | with the four queued rubric edits | ⛔ **The suite would have been green.** ⭐ It is the pointer rule needing an enforcer: *hold it or point at where it is held* is a convention today and nothing mechanical holds it |
| W22 | **Finding 44 owed to the integration catalogue**, not to `SK-01` — ⭐ **two of its three numbers came from PO-Integration** | **PO** → catalogue | ✅ **routed this round** | ⛔ Fixing it inside `SK-01` would have put a cross-source fact in one skill, where the next source cannot find it (R19) |
| W17 **+ W19** | ⛔ **One commit, and for the reason W7+W13 were.** **W17:** *"describe a value without reproducing it"* — ⭐ **four spellings shrank to two documented holdouts while the item waited** (ruling 36). **W19:** ⛔ **the 39 remaining `{value!r}` sites, ruled urgent** | **Developer 2**, after `FND-07` | ⛔ **after `FND-07`** | ⭐ **This is the `label_of` defect at repository scale, and it is live: `W1` and `W7` are both on this exact discipline, so a fix to one spelling leaves three.** ⚠️ **It compounds with Ruling 20 one level down:** the personal-data **gate** had two copies that disagreed; the **diagnosis helper** has four. ⛔ §1a's *"do not re-derive the patterns, refused five times"* was about the **patterns**, not the **helpers** — so nobody swept here. ⚠️ **Deliberately not unified now:** three of the four are other tasks' contract surfaces and it would collide with two branches mid-flight |
| W18 | ⏳ **in flight, with W14** — ⛔ **`user` + `authoritative` is accepted today** — measured — so **a grader the reader wrote may declare itself the source's own.** ✅ **RULED 35: `authoritative ⟹ bundled`, stated positively** | **Developer 1**, with `W14` | before `SK-01` | ⭐ **The author believed the set should be `("bundled",)` and did not change it**, because `unit.trust` owns the rule and `E06` names only the `generated` pair — ⚠️ **an argument, not a measurement**, and they said so. ⛔ **Exactly the restraint R21 asks for**: a task that meets an unlocated contract stops and asks. One entry in `unit.trust.FORBIDDEN` if the CTO agrees |
| W16 | ⛔ **Every canonical example in the spec is a hand-maintained copy of a contract the code now owns** — ⭐ **the last such pair in the project.** The instance: `MANIFEST_KEYS` has **ten** keys, spec §4's example carries **nine**, and `grep -c '"media"'` over the spec returns **0** for a key the contract owns, so ⛔ **`media` is unteachable from the spec** | **CTO** (spec is theirs) — ⚠️ **explicitly not Developer 2** | ⛔ **before `SK-01` proposes a manifest against the example** | ⛔ **REMEDY INVERTED — Ruling 28 REVERSED by Ruling 30. Do not add `media` to the example.** ⚠️ `media` is **not in `REQUIRED_KEYS`** — it is optional and defaulted, so **the example was not wrong to omit it.** ⭐ **The corrected remedy: §4 gains the complete key list *beside* the example; the example stays a realistic instance, not an exhaustive one; and ⛔ the test asserts subset one way and coverage the other — never equality.** ⛔ **Equality is what Ruling 28 required and it would have *compelled* the Q16 harm**: names freeze at first declaration, `ISO-04` omits `media`, and `SK-07` **generates** manifests — so an exhaustive example propagates an optional key through a generator and **freezes it on every corpus, including ones with no media** |
| W15 | ⛔ **Tooling wrote to a source repository's root ignore file** — a `graphify` git hook appended `graphify-out` to the ISO repository's ignore file on an ordinary commit, unrequested, ⚠️ **in the one repository where R3 is absolute.** Second half: `.claude/settings.json` carries a machine-local absolute path, an R7 exposure **created by tooling that no ruling names as a source** | PO → `OPS-05`, `SK-07` item 9 | ⛔ **before any adapter runs against a real source** | ⭐ **This framework's own repository is clean — checked, not assumed**: zero tracked files carry the real home path, our `graphify-out/` ignore came from `FND-01`'s scaffolding (deliberate, and this is not a source repository), no hooks installed. ⛔ **So the exposure is scoped to the corpus side, which is exactly where R3 bites.** ⚠️ **The rule is written in `graphify.md` and `SK-07` item 9 and is enforced by nothing that runs** — and `OPS-05` checks at **build** time while this happens at **index** time. PO-Integration reverted it and **re-measured after the fix**: the hook fired again, the root file stayed clean |
| W13 | ⛔ **One commit with W7 — ruled, see below.** **Two copies of the personal-data gate that already disagree** — `tests/fixture_checks/personal_data.py` skips dict keys where `SF-08`'s does not (`SF-06` finding 3, ruled **urgent**); and **`imports()` is spelled twice** and should be extracted to `tests/support.py` *"before a third scanner writes a third copy"* (`SF-06` finding 8) | **Developer 2** | ✅ **merged `f569d0e`** | ⭐ **One row because they are one defect**: the project's most-repeated diagnosis is *two copies of a contract*, and here it has produced a copy that **already gives a different answer**. ⚠️ `tests/support.py` exists and has no `imports()` |

⚠️ **W1 and W2 are one piece of work and should be assigned together.** W1 without
W2 is a fix with no guard; W2 without W1 is a red check with 45 findings.

---

## Scheduled — decided now, executed later

⭐ **Recorded here so they are not rediscovered at M2.** Each has an owner and a
trigger, and the trigger is an event rather than a date.

| Item | Owner | Trigger | Decision |
|---|---|---|---|
| ⭐ **SK-07 generates the corpus graph** — built, **bridged**, with the R3-safe ignore file | framework agent | ✅ **done now** — carried into `E11` this round | The highest graphify exposure converted into a generated artifact, closing an R19 hole in the same edit. ⚠️ Bridging is the part that would have been missed: a graph built by running the tool alone has **zero** doc↔code edges |
| **SK-07 must not say "submodule"** | PO | ✅ **done now** — `E11` corrected | R18's amendment reached the ruling but not the task that consumes it. The framework is a **sibling checkout at a recorded commit** |
| **Context headroom for SF-19a and SK-01/02/05/08** | PO, with CTO agreement | **M1 → M2 boundary** | Five tasks, not eighty-five. They are the discovery-shaped ones, where you do not know the name of the thing you are looking for — `query`'s weak case |
| **`Effort` field applied beyond the four named tasks** | PO | as each computation-shaped task is assigned | ✅ The field exists now (`README.md`), and `SF-07` and `FND-02` carry it. ⛔ Do not backfill eighty-four tasks; add it when a task is assigned and its shape is known |
| ⛔ **Back-triage the 23 pre-marker findings** — `FND-01` (5), `FND-02` (8), `FND-04` (10) | **PO** | ⛔ **before M1's wave opens** | The `[structural]` sweep is blind to findings filed before the marker existed — ⚠️ **including the one that motivated the mechanism** |
| **R21's three remaining open rows** *(was five, then four)* | CTO | each before its named task builds | ✅ `consuming.json` filled; ✅ **overlay `content.json` closed by SF-09** — `content_api` minted and asserted. ⚠️ **The next one is the discovery cache, owed before `SF-04` at M2 step 2.1** — no longer "two steps away", so it is the near one now |

---

## Cross-repo — the ISO-8583 integration track

| | |
|---|---|
| **Repository** | `ISO/` (`ISO-8583-jPOS-tutorial`) |
| **Owner** | PO-Integration |
| **Branch** | `release/studyforge-integration` |
| **Status** | `in-progress` — reconnaissance and delivery plan |
| **Closes when** | A milestone-ordered backlog exists whose every task ends in something a person can be shown, with acceptance the framework can evaluate |

**Confirmed by reconnaissance — record it, because it settles a scope question.**
⭐ **ISO is complete at the reading floor and never enters the execution track.**
Zero build files, zero graders, zero exercises in any of §7's three states, and
`permitted_edits` structurally `[]`. Per §11.0 and C5 that is a **pass, not a
shortfall**. Two things follow: the corpus is done at M4, and it is a **real
rather than synthetic empty-declaration case for `OPS-05`**, which is worth more
than a fixture because nobody built it to be convenient.

⚠️ **It is also a depth-1 corpus** — `levels` is `["group"]`, 38 units in three
groups (CTO ruling 1, which corrected §4's table). So depth-1 is the majority of
the four designed sources, not the exotic path.

### Questions from PO-Integration — routed, with deadlines

⭐ **These arrived as questions, not findings, and that is correct.** A question
is what the channel is for when the framework has not been built yet; a finding
is what it is for when the framework has been built and fell short.

✅ **Both are ruled and merged** — see *Resolved* above. X1 becomes `corpus.json`'s
`content` block, landing in SF-02 before it is assigned. ⭐ **X2 dissolved**: R7
governs identifiers arriving from the build environment, not identifiers that are
the material's subject matter, so the gate ships **no** payment-card pattern and
ISO needs no exemption at all.

⭐ **Both were answered before the task they land in was assigned, which is the
whole point of the deadline being a task rather than a date.** X1 in particular
was a schema change, and a schema is the one thing R9 makes expensive to alter
afterwards. ⚠️ The integration side got its answer at the cost of asking early —
recording that, because the next integrator's incentive to ask early is entirely
built out of whether this one's questions were worth asking.

### The channel — encoded in `../conventions/delivery-flow.md`, non-negotiable

- ⛔ **Questions and findings, never patches.** The integration side does not
  modify `studyforge` (§12).
- ⛔ **No task, context field or acceptance on that side ever cites a path inside
  the extraction source** (R20). `CS/` and `CSD/` are framework-side shorthand
  only. What an integrator needs is carried **here**.
- ⚠️ **SK-08, the delivery-planning skill, does not exist** — it is M2. So this
  plan is hand-written, and ⭐ **every step of it that SK-08 should have generated
  is a finding against SK-08** (R19). Those are this track's most valuable output
  before M2, because they arrive while SK-08 can still be shaped by them.
- ⚠️ **The track still has no definition of done.** `studyforge validate`
  (SF-25) is the archive contract and lands at M1; `studyforge plan` (SF-31) is
  the placement contract and lands at M2.
- **Durable findings are distilled into the integration catalogue**, so the third
  source starts further along than the second.

---

**Context budgets: ⭐ the analysis is in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md).** ⛔ **Two conclusions stay live:** `explain` and `path` take `--graph` and work from an index-less worktree while `query` does not, so **the index cost is paid once per repository**; and **a graph built by running the tool alone has zero doc↔code edges**, so R14's saving is a property of a graph somebody bridged.

---

## ⛔ `ONBOARDING.md` — ruled: it does not enter the repository

⚠️ **An untracked `ONBOARDING.md` sits at the repository root** (created
2026-09-09, never committed). ⭐ **It is not a team document at all** — it is a
generated onboarding template, and reading it changes the question.

**Three of its claims are false, and each is false in the expensive direction:**

| It says | The truth |
|---|---|
| *"Design + backlog; nothing implemented yet"* | ⛔ M0 closed; **1761 passed, 46 skipped** in the pinned container |
| *"composes them as submodules"* | ⛔ **R18 is amended, submodules are not used, `FND-05b` is cancelled** |
| *"Ask a teammate for clone URLs"* | ⛔ **Nothing is ever pushed to any remote.** Standing user decision, permanent |

⚠️ **And a fourth that is subtler and worse for this project specifically:** it
teaches `graphify query "..."` as *the* command. ⛔ That is the one command R14's
own amendment says holds **only when phrased as distinctive nouns**, and the one
that needs a local index — while `explain` and `path` take `--graph` and work
from a worktree that has none. ⭐ **It would teach a newcomer the exact habit that
produced the 31-of-33 defect**, on the day they arrive.

⛔ **Decision: not tracked, and not corrected into the tree.**

- ⭐ **Everything it is for is already owned by a document that is kept true** —
  `CLAUDE.md` (what this is, the hard rules, the workspace, where to start),
  `docs/conventions/`, and this board. ⛔ **A second front door is a second thing
  to keep true, and this one failed at that in four places while sitting
  untracked for a single afternoon.** That is the pointer-not-restatement rule
  again, at the scale of a whole document.
- ⛔ **It carries an embedded `<!-- INSTRUCTION FOR CLAUDE: … -->` block**
  addressed to an assistant, telling it how to conduct an onboarding
  conversation. ⚠️ **Tracking that would put instructions to agents, written by
  nobody on this project, at the repository root** — where every agent reads.
  ⭐ **That is disqualifying on its own**, independent of the false claims:
  correcting the prose would leave the block, and deleting the block leaves a
  document whose remaining content is already elsewhere.

⚠️ **What I did *not* do, deliberately: I did not delete it.** It is untracked, so
it is not repository state — it is a file in the user's working directory, and
⛔ **deleting an untracked file is irreversible and outside what a status document
should do on its own.** ⭐ **The dichotomy in the question was false: the answer is
neither "track it corrected" nor "delete it", because it is not the
repository's.** It is recorded here so it is never committed, and the one useful
thing it contains is noted: it is *evidence* that a newcomer's first document
gets written when nobody points at `CLAUDE.md` — which is a routing fact, not a
missing document.

---

**The Log — every dated entry of this project — is in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md).** ⭐ **Moved whole, not summarised.** ⛔ **New entries are appended there, not here**: a log is a record, and this file is a claim about now.

---
