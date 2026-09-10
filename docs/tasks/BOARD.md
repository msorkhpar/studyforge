# Board — live status

**Single source of truth for what is in progress and what is done.** Owned by
the framework Product Owner. Task *definitions* live in the epic documents
(`E00`…`E13`); this file carries only **state**.

⭐ **M0 is CLOSED — `FND-05a` merged and the last M0 task is done.** ✅ **M1 steps
1.1, 1.2 and 1.3 COMPLETE.** ✅ **M1 step 1.4 is CLOSED — `SF-10`
APPROVED and merged at `966ab30`.** ⏳ **Step 1.5 is OPEN: `SF-12`, then `QA-03`.**
⚠️ **This board twice mis-stated `SF-10`'s state in one round — first as
*"unblocked, waiting on nothing"* while it sat built on a branch, then as
`in-review` after it had merged.** ⛔ **Both errors are one cause: a status
measured once and quoted later.**

📏 **Base: 2649 passed / 8 skipped in the pinned container at `c84ca2e`**, the
release tip, quality floor clean. ⚠️ **Third base in one round** — `2568 @ 40731e4`, `2570 @ 1b2d993`, now this. ⚠️ **`2568 / 8 @ `40731e4`` was written earlier
in this same round and was superseded before it was committed — see the close
run's second pass.** ⚠️ **SUPERSEDES *"2490 / 8 at `a7c114b`"*,
which was two merges behind when it was written and is now four.** ⭐ **The
superseded figure is not deleted, because the paragraph below is about it and
the reasoning is what this board keeps:** `2490 / 8 @ `a7c114b`` (container) and
`2487 / 11 @ `e5bcc85`` (host).

⛔ **Read the two commits, not the two numbers.** ⚠️ **`a7c114b` is two merges
behind the tip**, so the container figure is a measurement of a tree nobody is
working on — ⭐ **and the honest form of a base is *what was measured, where, and
at which commit*, never a bare pair of counts.** ⛔ **A base quoted without its
commit is the branch-state-as-tip-state defect wearing a number**, which is the
one this session has catalogued five times. ⚠️ **Neither figure supersedes the
other and both carry their instrument.** ⭐ **The arithmetic reconciles exactly —
`2490 + 8 = 2487 + 11 = 2498` — so the difference is *three tests that skip
off-image*, not three tests that vanished.** ⛔ **Which three is not measured
here**, and that is the first thing to check if the totals ever stop reconciling.

⛔ **CHECK 4 RAN AT WAVE-CLOSE for the first time (round 19) and it found four
stale rows, a failed check 5, and a duplicated `W`-id.** ⭐ **The readings are in
[the wave-checks section](#the-wave-checks-six-at-open-and-check-4-again-at-close);
this line points at them and does not restate them.**

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

## ⛔ RULED 2026-09-10 — **findings are numbered per-document; `53`, `54` and `55` are ambiguous and here is which is which**

⭐ **Raised by the coordinator, measured here, ruled here.** ⛔ **The rule lands in
[`../conventions/agent-protocol.md`](../conventions/agent-protocol.md)** — *a
finding is numbered inside its own document, never globally*, as
`<TASK-ID>/<n>` — ⚠️ **and the argument for refusing an allocator is there, not
restated here.**

⛔ **The measurement found more than the report did, and that is Ruling 55 again.**
⚠️ **The report named one collision, from a grep of `5[5-9]`. A full census of
`handoffs/` found THREE — `53`, `54` and `55` — and 10 gaps in a 39-number
range.** ⭐ **The number was a fact about an instrument.**

### ⛔ The disambiguation, because 8 live citations are ambiguous today

⛔ **Neither document is edited — a handoff is a record.** ⭐ **`W4`'s precedent:
the board is where a superseded record gets superseded.** ⚠️ **Numbers 20–58 are a
CLOSED LEGACY RANGE; every existing citation still resolves, and a citation to one
of these three must say which.**

| # | `FND-05a.md` | `SF-10-survey.md` |
|---|---|---|
| **53** | `:137` | `:163` |
| **54** | `:146` | `:168` |
| **55** | `:157` — *this gate cannot run inside …* | `:176` — *the load-side validator …* |

⛔ **Cite these three as `FND-05a/53` or `SF-10-survey/53`, never as "finding 53".**

⭐ **The sharpest fact, and it is the one that refused the allocator:** ⛔ **both
documents have the same author, on two branches, in one wave.** ⚠️ **They collided
with themselves** — so an allocator file would have been edited on both branches
and would either conflict (the reviewer catching it, which is what we already
have) or ⛔ **merge cleanly with both increments and lose one silently.**

### ⭐ The enforcement rides with `W25`, and yes it is worth hurrying for

⛔ **Ruling 49's handoff check is being built this wave, by Developer 2, on this
exact directory.** ⭐ **One commit rather than a second pass over the same file**,
and the check is the natural enforcer: it is already deciding what a handoff *is*.

⚠️ **It does not widen `W25`'s scope so much as give it a second, cheaper
assertion** — ⛔ **`<TASK-ID>/<n>` is a *shape*, and a shape is exactly what that
check was already going to test.** ⭐ **It also inherits `W25`'s hardest problem
for free: 29 of 52 files in that directory are not task-shaped, and a finding
number scoped to its document does not care.**

⛔ **Legacy is not migrated and the check must say so** — ⭐ **numbers 20–58 in the
existing 12 documents are grandfathered, and a check that reds on them would be a
check that demands a record be rewritten.**

---

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

⛔ **This table was rebuilt on 2026-09-10, because it had become the defect it
exists to prevent.** ⚠️ **It carried `W20` twice (`todo` **and** `done`), `SF-10`
twice (`unblocked` **and** `todo`), and three rows whose status disagreed with
the tree.** ⭐ **Every cell below is a measurement taken on `e5bcc85` today**, not
a status inherited from the round that wrote it. The re-measurement is check 4
and this is what it produced.

| Task | Owner | Status | Gate |
|---|---|---|---|
| **W14** — two missing invalid fixtures | Developer 1 | ✅ `done` | — |
| **W18** — Ruling 35, `authoritative ⟹ bundled` | Developer 1 | ✅ `done` | — |
| **W23** — the live R7 hole (tilde, `/export/home/`) | Developer 2 | ✅ `done` — ⛔ **the board said `in-progress` for a round** | — |
| **W20** — repo-wide §7c check **and its migration** | Developer 2 | ✅ `done` — **0 hits, floor clean, exit 0** | — |
| **Ruling 46's helper** — `asserting=` rule-id set + the misattribution message | Developer 1 | ✅ `done` — ⚠️ **the board said `in-progress`; it is merged** | ⛔ **stopped at the helper; the general seam is `FND-08`** |
| **SF-10 survey** — port inventory + R11 package shape (**W5**) | Developer 1 | ✅ `done` — `13b2857`, one document, no code | — |
| **FND-05a** — the workspace pin file and its verification command | Developer 1 | ✅ `done` — ⭐ **M0 CLOSED** | — |
| **SF-10** — Unit document builder | Developer 1 | ✅ **`done` — APPROVED and merged `966ab30`** | ⭐ **M1 step 1.4 CLOSES** |
| **W25** — Ruling 49's handoff check | Developer 2 | ⛔ **`in-review` — `feat/W25-handoff-check` @ `f77bb7d`, 2629 / 8.** ⚠️ **CORRECTED at check 4's close run: the previous cell said *"NEVER STARTED, byte-identical to `HEAD`"* and was true when written.** ⛔ **`HEAD` moved; the sentence did not** | ⛔ **and it is re-priced: see below** |

#### ⛔ The two rows that were lying, and they lied in opposite directions

> ⛔ **AND IT HAPPENED TO ME, IN THIS SECTION, WITHIN THE HOUR.** ⚠️ **I wrote
> `SF-10` up as `in-review` on an unmerged branch; the CTO approved and merged it
> at `966ab30` while I was still writing.** ⭐ **So the row below was correct when
> written and stale when committed — which is the same defect, in the same
> document, in the paragraph diagnosing it.** ⛔ **That is the argument for
> re-measuring at wave-CLOSE, and it is now ruled: see the wave-open checks.**

⚠️ **`SF-10` is the expensive one, and it is a new shape of the same old defect.**
The board said *"unblocked, waiting on nothing"* — ⛔ **while 1,989 lines of it,
across 18 files, sat finished on an unmerged branch.** ⭐ **A second author picking
the row up would have rewritten the entire package**, and nothing on this board
would have told them not to. ⛔ **That is *branch state invisible as tip state*,
which is the mirror of the defect this session has catalogued five times** — and
the mirror is worse, because the familiar version over-reports progress and this
one **under**-reports it, so it reads as caution rather than as error.

⭐ **The row now names the branch and the commit.** ⛔ **A row for work in review
that does not say where the work is has not recorded anything.**

⚠️ **`W25` is the plain one: `in-progress` against a branch containing nothing.**
⭐ **The coordinator's handoff said "never started" and the board disagreed; the
`git diff` settles it and the handoff was right.**

⛔ **`W23` and Ruling 46's helper were both `in-progress` and both merged** — so
three of this table's nine rows were wrong, in **both** directions, in one round.
⚠️ **That is the argument for check 4 being run rather than read**, and it is now
the second time running it has changed the plan.

#### ⚠️ `W25` is re-priced, and the number is the reason it is not a small task

⛔ **Ruling 49 binds `<TASK-ID>.md`, and most of that directory is not
task-shaped.** ⭐ **Measured today, not inherited:**

| `docs/tasks/handoffs/` | count |
|---|---|
| files total | **52** |
| strictly `<TASK-ID>.md` | **23** |
| not task-shaped at all (CTO rounds, sessions, `README.md`, a drift doc, ruling notes) | **23** |
| compound or suffixed task ids (`SF-10-survey`, `W1-W2`, `W7-W13`, `W14-W18`, `W17-W19`, `W19-provenance-pin`) | **6** |
| ⛔ **would need an exemption rule or a rename** | ⛔ **29 of 52 — 56%** |

⛔ **So the check's hard part is not the six sections; it is deciding what a
handoff *is*.** ⚠️ **A naive check demands six sections from a CTO round document
and from a survey that owes none** — the coordinator flagged exactly this and the
measurement makes it 56% of the directory rather than an edge case. ⭐ **The rule
is `FND-08`'s and it is the same one: *exempt documents by declaration, never by
guessing at a filename*.**

### ⭐ Developer 1 takes FND-05a — the M0 residue that has waited a whole milestone

⛔ **`SF-10` was gated on rulings 50 and 51, and `W20` was ahead of it**, so the
build could not start. ⚠️ **This line said *"rulings 53 and 54"* — those are
`FND-05a`'s — and it survived the same table's duplicate rows being corrected.**
⭐ **The *summary points, never restates* rule biting inside the section that
states it**, which is the fourth costume and now the fifth. ⭐ **`FND-05a` is the right use of the gap and it has been
right for a while:** it is a **tracked pin file plus a verification command**,
it touches neither `tools/quality/` (Developer 2's `W20`) nor `unit/`
(`SF-10`), and ⛔ **it is the last open M0 task — landing it closes M0
outright.**

⚠️ **My own words on it, now a full milestone old:** *"it should not slip
**indefinitely**: the failure it prevents — a component at a commit the parent
never recorded — has **no symptom**, so it is discovered by being wrong rather
than by failing."* ⛔ **A task whose justification is *it can slip* accumulates
exactly one counter-argument per milestone**, and this is its second.

⭐ **Acceptance is unchanged and already sharp:** verification **exits 0** when
correct and **exits 1 naming the component** both when a recorded commit is
absent locally and when a component's `HEAD` moved unrecorded — ⛔ **asserted, not
described** — and ⛔ **no `.gitmodules` anywhere, no absolute path in any tracked
file.**

### ⭐ What the survey gives SF-10 — and the seam whose failure is silent

**Proposed shape:** `unit/builder/{__init__,material,derived,authored,document}.py`,
plus ⭐ **`unit/served.py` as a *sibling*, not a child.** ⚠️ Its **name** was
stated rather than taken — correctly left as a team decision.

⛔ **The load-bearing seam, and it is FND-04's argument again:** `derived`
**computes** order; `authored` **must never re-derive it** — because two
consumers ordering differently **mint different speech ids and desynchronise the
page from its audio.**

> ⛔ *"Split, the authored path cannot reach the ordering code by accident; in one
> module they are two branches and nothing but care keeps them apart."*

⭐ **That is a seam, not a slice** — the distinction R11 turns on — ⚠️ **and its
failure is silent**, which is why it is worth a package boundary rather than a
convention. ⭐ **`builder/document.py` has the least headroom at ~290, so its next
seam is named now** rather than discovered at 400.

⛔ **Two CTO rulings are owed before `SF-10` builds — it is gated on them:**

| # | The collision | Why it cannot wait |
|---|---|---|
| **53** | `unitdoc.py` re-gates every archive file on **every read, by design** — ⛔ **and Ruling 17 put that gate upstream** | ⚠️ **Both are defensible and they cannot both be implemented.** A builder written against the wrong one is rewritten, not adjusted |
| **54** | ⛔ **`source` means a *corpus id* here and *a fetch URL* there** | ⛔ **`SF-10` writes the `sources` array, so it is where they collide.** ⚠️ **Rename before 1,290 documents carry it** — R9 makes a written key expensive, and this is the last moment it is free |

⚠️ **Five further open questions are carried in the survey, each with what would
settle it** — including whether the served document gets its own `api` version.
⛔ **No equivalent of `UNIT_API = 3` exists**, which makes it an **R21 register row
in the making**: a contract that is about to be written and is not yet located.

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

### ⛔ SCOPED AND CLOSED — **Ruling 43's four walks are `FND-08` and `FND-09`**, and the count was wrong

⭐ **Ruling 43's task is scoped, once, and the scoping is now in the epic where a
task definition belongs — `E00-foundations.md`, `FND-08` and `FND-09`.** ⛔ **The
section below is kept because its *reasoning* is still load-bearing and its
correction is the best worked example this board has of a scope written against
the wrong artifact. ⚠️ Its forward-looking clauses are superseded by the
measurement.**

⛔ **It owed four walks. Measured on `e5bcc85`, it owes two tasks and one of the
four is refused outright:**

| Walk | Scoped as | ⛔ **Measured today** | Now |
|---|---|---|---|
| **1 — corpus names** | done as `W20` | ✅ **0 hits**, floor clean, exit 0 | ✅ **closed** |
| **2 — dangling pointers** (`W21`) | a check | **41 links, 33 real, ⭐ 0 dangling** — ⛔ **but 8 of 8 naive hits are false** | ⭐ **`FND-08`** |
| **4 — the board's own archive pointers** | ⛔ **"the split added a fourth consumer"** | ⛔ **14 links, 14 resolve, `0` anchors** | ⛔ **REFUSED — it collapses into walk 2** |
| **3 — sweep-by-declaration** (Ruling 46) | one seam, four consumers | **7 modules, 10 call sites, ⛔ 2 more unknown copies** | ⭐ **`FND-09`** |

⛔ **Walk 4 was my own addition and it is the one that had to go.** ⚠️ **I wrote
*"the board split just added a fourth consumer, since every `BOARD.md` pointer
into the archive wants the same walk."*** ⭐ **Measured: all 14 pointers resolve
and not one carries an anchor — so a checker over them can only assert that one
file exists, and it would pass on the day the archive is emptied.** ⛔ **That is a
check that cannot fail, which is Ruling 48's defect, arriving inside the scope
written to prevent it — for the *second* time in this same section.**

⭐ **The first time, I scoped against Ruling 45 and named `VIOLATION.md` without
opening it. This time I named a walk without counting its links.** ⚠️ **Same
error, one level up: the first was a ruling I had not read, the second a
measurement I had not taken.** ⛔ **And both were caught by the *same* remedy —
opening the artifact — which is now the strongest evidence this board has that
Ruling 55 is a rule and not a slogan.**

⭐ **The ordering inverts as a result: `BOARD.md` gains anchors first, and walk 4
becomes an assertion over walk 2's output.** ⛔ **Adding the anchors is mine.**

#### ⭐ Owners, and the measured price each is being asked to pay

| Task | Owner | ⛔ **Measured price** | Gate |
|---|---|---|---|
| **`FND-08`** — the document walk | **Developer 2** — ⭐ **`tools/quality/` is their surface, and `W20`, `W21` and `W25` all live on it** | ⛔ **migration `0`; the cost is the markdown parser** — fence state machine **plus inline code-span stripping**, without which the check is **8-of-8 false** on this tree. ⭐ **The file-walk seam is ~80 % built already** in `tools/quality/config.py` | ⛔ **after `W25`** — same surface, and `W25` has the earlier trigger |
| **`FND-09`** — the fixture-access seam | **Developer 1** — ⭐ **they authored Ruling 46's helper and its negative control** | ⛔ **7 modules, 10 call sites**, plus **2 previously-unknown copies** of the invalid set. ⚠️ **The move is a net size relief**: the helper's host module is at **567 / 600** | ⛔ **not before `SF-10` merges** — it edits the test tree `SF-10` is adding to |

⛔ **Neither task gates the renderer.** ⭐ **Said explicitly because `W20` gated
`SF-10` and the shape is easy to over-apply** — ⚠️ **`W20` gated it because a
repository-wide check accumulates a migration from every new emission site, and
`SF-10` was about to add some.** ⛔ **`FND-08` walks *documents* and `FND-09` walks
*fixtures*; neither accumulates anything from `SF-12`.** ⭐ **Ruling 52 again: the
scope that rule was argued over is checks with a growing backlog.**

⚠️ **And the sharpest single correction: `including_invalid=` does not exist in
any Python file in this repository.** ⭐ **It survives only in prose — including in
the section below.** ⛔ **A scope written against it is quoting a document as
code.**

---

### ⭐ Scoped before the task is written: **W20 ships a fixture-access seam, and three walks consume it** — ⚠️ **superseded above**

⛔ **Decided now because the CTO asked for it before scoping, and because three
tree-walks are about to be written by three different people.** Ruling 43's task
owes **corpus names**, **dangling pointers** (Finding 50 / `W21`), and **Ruling
45's sweep** — ⚠️ **and the board split just added a fourth consumer**, since
every `BOARD.md` pointer into the archive wants the same walk.

> ⛔ **CORRECTED — I scoped this against Ruling 45, which Ruling 46 superseded,
> and building it as written would have produced the defect the supersession
> exists to prevent.** ⚠️ **I named `VIOLATION.md` as the declaration and did not
> open it.** ⭐ **The CTO's new clause on themselves is mine identically: a ruling
> that names an artifact opens it first.**
>
> ⛔ **Measured by me on the tip `ac4ed55`, not inherited:** `INVALID_CORPORA`
> maps a directory to the **checker's** rule id — `"count-mismatch": "counts"`,
> `"user-authoritative": "exercise-trust"`, seven entries — while every
> `VIOLATION.md` names the **spec** rule in prose: `spec §6`, `R9`, `R7`.
> ⛔ **Not one of the seven names the id the sweeps use.**
>
> ⚠️ **They are not two copies of one fact — they are two different
> vocabularies.** So a seam reading `VIOLATION.md` needs **a prose parser *and* a
> `spec §6 → counts` translation table**, to reach a dict that already exists, is
> already exported, and is already pinned to the directory by
> `test_the_invalid_set_is_exactly_what_is_on_disk`. ⛔ **That is a second copy of
> one declaration — the defect diagnosed five times — arriving inside the scope
> written to fix it.**

⛔ **Ruling 46 — the rule the seam implements:** ⭐ ***a sweep names, as a set of
rule ids, every property it asserts***, and the helper excludes exactly
`{d for d, rule in INVALID_CORPORA.items() if rule in asserting}`.

⛔ **A set, not a string, and the block-vocabulary sweep is why:** it asserts
membership **and** counts, so ⚠️ **a single id excludes too little and the
directory excludes too much.**

⛔ **And the half that closes finding 47, which this scope must carry:** a set
still permits **under**-declaration, ⚠️ **and that red reads as the fixture's
fault.** So the failure message names the declaration:

> *"`user-authoritative` declares rule `exercise-trust`; if this sweep asserts
> that rule, name it in `asserting=` — **do not change the fixture**."*

⭐ **The problem was never the red; it was the misattribution.** ⛔ **Without that
sentence the next author neuters a negative control** to make a suite green — and
a neutered control is the one failure this project cannot detect from outside.

⭐ **`VIOLATION.md` keeps its §1e job and nothing parses it:** a file beside the
data telling **a person** what the gate should say. ⚠️ **Documentation, not an
interface.**

⭐ **My instinct — *read from the declaration, never the directory name* — was
right; I pointed it at the wrong artifact.** ⛔ **The declaration is
`INVALID_CORPORA`.** And it is still *enumerate the legal*: a directory name is an
open set somebody keeps extending; **the dict is a closed declaration that already
has an enforcer.**

⚠️ **Measured, and it is why the seam is not a nicety:** all **7** invalid
fixtures agree with the block vocabulary, so `including_invalid=False` drops **9
documents that should be swept** — ⛔ **each invalid in one named way and correct
in every other.** ⭐ Developer 1's fix **stands until this task**: it is correct,
it stops the false red, and it is honest about what it does.

### ⛔ W20 before SF-10, and it is the third instance of one sequencing shape

> ⛔ **HISTORICAL — every number in this subsection is a *pre-migration* reading
> and none of them describes the tree.** ⭐ **Measured 2026-09-10: `0` hits by the
> grep and `0` by the check.** ⚠️ **The sequencing argument below is why the
> answer is `0`; it is not a claim that anything is outstanding.**

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

## M1 step 1.5 — `SF-12`, then `QA-03`. ⭐ **Order held; the survey is confirmed with three refinements**

> **Step 1.5 is `SF-12`** (Templates and unit page renderer, **Team**, `~110k`,
> owns `render/page/` and `render/templates/`), **then `QA-03`.** ⛔ **`SF-12` is
> the largest port in the project after `SF-19a` and it is a package (R11) — a
> task that produces one large module has not done the task.**

| Task | Owner | Status | Gate |
|---|---|---|---|
| **`SF-12` survey** — port inventory + R11 package shape + ⛔ **W9's name review** | **Developer 1** | ⛔ **`in-review` — `feat/SF-12-survey` @ `afba232`, 2490 / 8.** ⭐ **Findings renumbered `SF-12-survey/1..6`** — ⚠️ **SIX, and round 18's handoff said five**; the branch is right and the handoff is a record | ⛔ **a design, not renderer code** |
| **`SF-12`** — Templates and unit page renderer | **both, as a team** | ⛔ **`unblocked` — waiting on the ROSTER, not on a dependency** | ⛔ **Conditions 1, 2 and `SF-10` are all DISCHARGED. The only thing left is Developer 2** |
| **`QA-03`** — Visual and browser verification harness | **both** | `todo` | ⛔ **after `SF-12`** |

### ⛔ WHAT OPENS THE MOMENT THE SURVEY IS APPROVED — and it is not `SF-12`

⭐ **`SF-12` is `Team`-sized, so its gate is not a dependency, it is a ROSTER.**
⛔ **Both developers must be free, and right now neither is.** ⚠️ **Recorded
because *"when the survey lands"* reads like one condition and is three.**

| # | Must be true | State at `40731e4` + branches, 2026-09-10 |
|---|---|---|
| 1 | ⛔ **`W27` MERGED** | ✅ **DISCHARGED — merged `5c6c883`** |
| 2 | ⛔ **the survey APPROVED** | ✅ **DISCHARGED — APPROVE, merged `1b2d993`.** ⭐ **Four escalations ruled, notably *one variant per page*.** ⚠️ **`html.py` is 1699 lines, L1112 blank, exactly one template-shaped literal at L1233–1253** — re-run under the CTO's own `ast` sweep |
| 3 | ⛔ **Developer 2 free** | ⛔ **STILL THE BINDING CONSTRAINT — `W25` (APPROVED, unmerged), `W26` (`in-review` @ `283ae90`), then `FND-08`** |
| 4 | ⛔ **Developer 1 free** | ⛔ **`FND-09` unblocked as of `966ab30`; `W28` newly minted.** ⭐ **`FND-08`/`FND-09` APPROVED as written; all five prices reproduced** |

### ⭐ `W27` LANDED FIRST — ⛔ **and the argument is kept because it was right, not because it is still pending**

⚠️ **`W27` touches `unit/content.py`, `corpus/manifest/document.py`,
`corpus/placement/identity.py` and two `errors.py`. `SF-12` owns `render/page/`
and `render/templates/`.** ⭐ **Zero overlap — so on the usual test `W27` would
not gate it.**

⭐ **Merged `5c6c883` on 2026-09-10, ahead of `SF-12`, which is the outcome this argued for.** ⛔ **It gated it, because `SF-12` renders the document `SF-10` builds and
is therefore a CALLER of exactly the three sites `W27` fixes.** ⚠️ **A renderer
written against today's contract wraps a build in `except ContentError` and
swallows a `PersonalDataLeak` — R7 failing open, in new code, on the day it is
written.** ⛔ **And this board's own rule for M1 says why that is the expensive
order: *a contract that merges first becomes the shape the next tasks copy*.**

⭐ **So `W27` before `SF-12` is not a scheduling preference; it is the difference
between one migration of three sites and a fourth site minted after the fix.**

### ⭐ `W26` does NOT gate `SF-12` — measured, and recorded so it is not assumed

⛔ **`W26`'s subject is `tests/test_gate_coverage.py`, an R7 *coverage* check over
modules that decode JSON.** ⚠️ **A renderer consumes an in-memory document; it
does not read JSON.** ⭐ **And `W26` has ZERO migration — the prototype finds the
same six readers.**

⛔ **So `W26` gates *further gate work*, not `SF-12`.** ⚠️ **It still lands in this
window, for the roster reason and not the dependency reason: it is Developer 2's,
it is cheap, and leaving a not-started row open across a `Team` task is how
`W25`'s row came to be wrong twice.**

### ⭐ The fillers, and ⛔ they are fillers — both must be parked before `SF-12` starts

| Task | Owner | Why now | ⛔ **Constraint** |
|---|---|---|---|
| **`FND-09`** — the fixture-access seam | Developer 1 | ⛔ **unblocked: its gate was *"not before `SF-10` merges"*, and `SF-10` merged at `966ab30`** | ⛔ **must be `done` or parked before `SF-12`** |
| **`W28`** — `source_files()` respects the repository's ignore declaration | Developer 1 | ⭐ **removes 100 of ISO's 112 findings**; owed before `SF-31` (M2) | ⭐ **small; the natural companion to `FND-09`** |
| **`FND-08`** — the document walk | Developer 2 | ⛔ **after `W25`** — same surface | ⛔ **must be parked before `SF-12`** |

⛔ **The ordering rule this makes explicit: a `Team` task is scheduled by the LAST
developer to become free, not the first.** ⚠️ **Filling both developers' idle time
with small tasks is correct and is also how a `Team` task slips a wave** —
⭐ **so every filler above carries a park point, and a filler without one is not a
filler.**

### ⭐ The survey is confirmed — ⛔ **on the precedent, and the precedent is measured**

⭐ **`SF-10`'s survey is the reason, and it paid three ways:** it corrected `W5`'s
number from *"an 827-line port"* to **≈250 lines left**, it produced the
`derived`/`authored` seam argument the CTO rated as the read's whole value, and it
was **R14's first clean instance** — 41 line-anchored nodes answering the
structure question before a file was opened. ⛔ **The CTO's reason for it at
`FND-04` holds identically here: only somebody who knows the module's internals
can answer where it divides.**

⛔ **Deliverable is a design, not renderer code**, and the reason is the
collision-pair rule's *premise* rather than the rule: ⭐ **`SF-12` is `Team`-sized,
so its code is not authored by one person ahead of the other.** ⚠️ **But the
serial part is not the code**, and spending the gap on it is what kept the team
task intact at 1.4.

#### ⛔ Three refinements, and the first one is not optional

1. ⛔ **The survey reads `feat/SF-10-unit-builder` @ `c33f231`, NOT the release
   tip.** ⚠️ **`SF-12` renders the document `SF-10` produces, and that document —
   `unit/served.py`, 157 lines — exists only on an unmerged branch.** ⛔ **A survey
   conducted against the tip would be surveying a document that is not there**,
   and this board is exactly why: ⭐ **it said `SF-10` was *"waiting on nothing"*
   while 1,989 lines of it sat finished.** ⛔ **Nobody gets that fact from the
   board unless the row names the branch, which is why the row now does.**

2. ⛔ **`W9` is the survey's job, not the build's.** ⭐ **It has landed in `E03` as
   `SF-12`'s *first act*** — the review of `render/pageassets/surface.py`'s class
   names. ⚠️ **But *"its first act"* only binds if somebody has measured which
   names are wrong**, and the survey is the one moment that is free. ⛔ **The
   deliverable is a table: every published class name against what the port
   actually calls it, and which side moves.** ⭐ **A rename is a change to
   `surface.py` **and** the stylesheet together; inventing a second name is
   forbidden and `test_surface` already fails it.**

3. ⭐ **R13's live work is the survey's sharpest question, and the epic names only
   one instance of it.** ⛔ **`html.py:1112` is `PLAYER = """<footer id="player">`
   — triple-quoted markup in the module being ported.** ⚠️ **The epic's own rule is
   a *judgement per literal*:** the skeleton, figures, panels and section wrapper
   become template files, while loop bodies, inline wrappers and one-line
   containers stay in code, *because a template file for a closing tag removes no
   duplication and adds a hop.* ⛔ **So the survey inventories EVERY triple-quoted
   markup literal and rules on each** — ⭐ **that is `SF-12`'s equivalent of `W5`'s
   inventory, and it is the number the task is currently carrying in its head.**

⚠️ **And one question to carry, not to answer:** `SF-10`'s survey left open
whether the served document gets its own `api` version — ⛔ **no equivalent of
`UNIT_API = 3` exists.** ⭐ **`SF-12` is its consumer.** ⛔ **If `SF-10`'s build did
not mint one, `SF-12` is the second task to meet an unlocated contract, and R21
says it stops and asks rather than choosing quietly.** ⚠️ **`W11` rides here too:
if this task mints an `api` field, it is the colliding one — one line retires it.**

### ⛔ `QA-03` after `SF-12`, and the check-first rule does **not** apply

⚠️ **Worth stating, because the rule was minted one step ago and this is the first
case where it does not hold.** ⭐ **`W20` established: *a check and the code it
will judge are ordered check-first, or the check inherits a backlog it did not
cause.*** ⛔ **`QA-03` is not that kind of check.**

⭐ **The distinction is the backlog.** A repository-wide check goes red on landing
because violations already exist — ⛔ **so the cost of arriving late is real and
grows.** ⚠️ **A visual harness inherits nothing: it needs a page to look at, so it
*cannot* precede the renderer, and arriving after `SF-12` costs it nothing.**

⛔ **Recorded so the rule is not over-applied**, which is Ruling 52's whole
subject: ⭐ **the scope `W20` was argued over is *checks that accumulate a
migration*, and a harness with no migration is outside it.** ⚠️ **A rule stated
without its scope gets carried at its widest, and this one is three steps old.**

⭐ **`QA-03` still lands in M1 rather than M7, and that has not changed:** `SF-14`,
`SF-18`, `SF-24` and `QA-02` each carry an acceptance condition no unit test can
reach, ⛔ **and the precedent is not hypothetical — a highlight misclassification
italicised every string in one language, the tests passed, and only a screenshot
caught it.**

---

---

## ⛔ RULED 2026-09-10 — **§11.2 vs `source_files()`: the spec was already right, and the code never implemented it**

⭐ **Carried from round 18 as *"two definitions of one thing, one in code and one
in spec text I own."*** ⛔ **Re-measured before ruling, and the re-measurement
changed the answer: they are not two definitions. §11.2 has the only definition,
and `validate/source.py` has no definition at all.**

### The measurement, re-run 2026-09-10 on the ISO corpus @ `08e6290`

| | |
|---|---|
| `source_files()` enumerates | **159** |
| the repository tracks (same skips) | **59** |
| ⛔ **scanned but not tracked** | ⛔ **100** |
| tracked but not scanned | ✅ **0** |
| ⛔ **of the 100, `git check-ignore`-positive** | ⛔ **100 — every single one** |
| neither tracked nor ignored | ✅ **0** |
| the 100, by top directory | `graphify-out/` **96** · `.claude/` **2** · `.idea/` **2** |

⛔ **`F20` filed this as 83. It is 100 at `08e6290`, and the difference is
`graphify-out/` growing 79 → 91 → 96 in one day.** ⭐ **That is not a correction
of `F20` — it is `F20`'s own *"no fixed point"* claim, measured a third time by a
third party.**

### ⛔ The disagreement is ONE-DIRECTIONAL, and that is what makes it cheap

⭐ **`tracked but not scanned` is zero.** ⚠️ **So the framework is not missing
material; it is enumerating output** — ⛔ **and every one of the 100 files is one
the corpus's own repository has already declared is not material.**

⛔ **`F20` asked for one ruling over 100 files. It is two populations and they
need different answers:**

| Population | At `08e6290` | Whose |
|---|---|---|
| ⛔ **scanned, git-ignored generated output** | **100** | ⭐ **this ruling — one predicate, no design content** |
| ⛔ **tracked, real material the manifest's `include` does not cover** (`README.md`, `LICENSE`, `CLAUDE.md`, `docs/`, `TestCases.md`, `.gitattributes`, `.gitignore`) | **17**, per `F18` | ⛔ **NOT THIS RULING — `F18`'s third state, a schema decision under R9, the CTO's** |

⚠️ **Splitting them is the whole value.** ⛔ **Held together, `F20` reads as a hard
design problem and blocks on a schema ruling.** ⭐ **Split, the expensive-looking
half is one predicate that removes 100 of 112 findings, and the genuinely
undecided half shrinks to 17 files and stops being urgent.**

### ⭐ The ruling: **the corpus is what the corpus's own repository tracks**

⛔ **§11.2 clause 11 already says so** — *"`git status` shows no modification to
any pre-existing file except the entries its manifest declares in
`permitted_edits`"*. ⚠️ **The acceptance criterion has been git-aware since it was
written.** ⭐ **So this is not the spec and the code disagreeing; it is the code
never having implemented the definition the spec gave it**, and the spec text
needs **no** amendment.

⛔ **R1 is satisfied, and this is the argument that matters:** the framework does
**not** decide what is generated output. ⭐ **The corpus declares it, in the file
every repository already has** — and a declaration the framework reads instead of
a rule the framework knows is R1's whole shape.

⛔ **`SKIP_DIRS` is the defect in miniature, sitting inside the function.** ⚠️ **It
is five hardcoded names, and two of them — `node_modules`, `__pycache__` — are
the framework guessing at two ecosystems' ignore files.** ⭐ **A framework that
ships a list of other people's build directories is a framework that knows about
sources**, and it will be wrong for the first corpus that uses a third ecosystem.
⛔ **`.git` and `.studyforge` stay: they are the framework's own, and `archive`
is R2's.**

### ⛔ The degradation, and it may not guess

⛔ **Where the corpus root is not a git working tree, the current walk stands and
`validate` SAYS SO.** ⭐ **R2 makes an archive a shippable artifact on its own**,
so refusing a non-repository corpus is wrong — ⚠️ **but silently falling back to
a scan that over-reports by 100 files is worse, because it looks like a clean
run.** ⭐ **The precedent is in this module's own docstring: an absent source tree
is reported `Unchecked`, loudly, counted, all-or-nothing.** ⛔ **A half-applied
ignore rule is exactly the half-present source that docstring refuses.**

### ⭐ `W28` — the task

| | |
|---|---|
| **Owns** | `src/studyforge/validate/source.py` — `source_files()` and `SKIP_DIRS` |
| **Owner** | ⛔ **Developer 1.** ⚠️ **`W25`, `W26`, `W27` and `FND-08` are all Developer 2's, on one surface** |
| **Size** | ⭐ **Small.** One predicate, one fallback, `SKIP_DIRS` reduced to three |
| **When** | ⛔ **before `SF-31` (M2).** ⚠️ **`F19` also lands before `SF-31`, on the same function's blind spot** — ⭐ **and a `sibling` build's 79 generated paths are git-ignorable, so this ruling is `F19`'s cheapest half too |
| **Acceptance** | ⛔ **AMENDED 2026-09-10 — see below. Name the SET, never the COUNT** |
| **⛔ Not in scope** | ⛔ **`F18`'s 17 tracked-but-unclassified files.** ⭐ **That is the third state and it is the CTO's.** ⚠️ **A developer who "fixes" those too has answered a schema question in a bugfix** |

#### ⛔ `W28`'s Acceptance, AMENDED — ⭐ **`W22` applied to an acceptance criterion**

⛔ **The number I first wrote — *112 findings → 12* — was UNREACHABLE, and it
pointed at the trap the task's own scope note ring-fences.** ⚠️ **Measured by
PO-Integration after I scoped it, and reproduced here at `1e49225`: the include
globs (`src/*.md`, `TestCases.md`) cover ZERO of the tracked-unclassified files,
so the residual is 17, not 12.**

⛔ **The only route to 12 is widening `include` over the five root files — which
puts `README.md` in, and `README.md` becoming a unit is `F18`'s exact trap.**
⭐ **So the number asked a developer to answer the schema question the scope note
forbids them to answer.** ⚠️ **The scope note was right; the number contradicted
it, in the same table.**

⛔ **And a total could not have survived anyway.** ⭐ **`graphify-out/` has gone
79 → 91 → 96 → 99 across this wave; the corpus total 100 → 112 → 117.**
⚠️ ***"No fixed point"* is now five measurements** — ⛔ **so nothing in this
acceptance may hard-code a total.**

⭐ **Restated as a set, which is re-runnable where a total is a snapshot:**

| # | ⛔ **The criterion** | Reference reading @ `1e49225` |
|---|---|---|
| 1 | ⭐ **Every path `git check-ignore` accepts contributes ZERO findings** — the whole of `graphify-out/`, `.claude/`, `.idea/` | **103**, and ⛔ **the number is illustrative, not the criterion** |
| 2 | ⛔ **The residual is EXACTLY the tracked-but-unclassified set: `docs/studyforge/*` plus the five root files** `.gitattributes`, `.gitignore`, `CLAUDE.md`, `LICENSE`, `README.md` | **17** = 12 + 5. ⚠️ **12 today, 13 the next time that branch files a finding** |
| 3 | ⛔ **`W28` MUST NOT SHRINK the residual.** ⭐ **It is `F18`'s third state, and shrinking it is answering `F18`** | — |
| 4 | a corpus root with no `.git` reports `Unchecked`, counted, ⛔ **never silently scanned** | ⭐ **Ruling 69's one gap; already closed by this clause** |
| 5 | ⛔ **`node_modules` and `__pycache__` are GONE from `SKIP_DIRS`**, and a test asserts a corpus using neither ecosystem is unaffected | — |

⭐ **The decomposition is the assertion.** ⛔ **`117 = 103 ignored + 17 residual −
3 excluded` reconciles; a bare `117` does not, and cannot be re-run tomorrow.**
⚠️ **Their `verify.py` asserts the decomposition at `1e49225`** — ⭐ **so the
framework side and the corpus side are checking the same shape from both ends,
which is the first time that has been true.**

⛔ **Relayed to Developer 1 by the coordinator mid-task, and this row is the
version that agrees with them.**

⛔ **This does not touch spec §11.2.** ⭐ **The finding was filed as a spec/code
disagreement and the re-run dissolved the spec half** — ⚠️ **which is why a
finding is re-run before it becomes a task, and this is the second round running
that the re-run changed the shape rather than the number.**

---

## ⛔ PO-INTEGRATION ROUND 4 — routed 2026-09-10, committed `08e6290` on `release/studyforge-integration`

⭐ **The strongest round the track has produced, and the reason is structural: it
is the first that could *run* the framework rather than reason about it.**
⛔ **Everything below is measured in a real repository, and the numbers are quoted
with that ref.**

⚠️ **Two documents, and the brief I was routing from named only one.** The
reconnaissance document `docs/studyforge/reconnaissance-round-4.md` (507 lines)
carries `F18`–`F22` and `F24`; ⛔ **`F23`, `F25`, `F26`, `F27`, `Q20` and `Q22`
are in `docs/studyforge/questions-for-framework.md` (1,703 lines)**, the
register. ⭐ **Recorded because a routing that names the wrong document sends the
owner to a file that does not contain their item.**

### ⛔ The arithmetic that is the finding

| | |
|---|---|
| `Q5` ruled — a 3,863-line container became **material** | **−1** |
| round 4's reconnaissance document **committed** | **+1** |
| committing it fired the graphify hook: 79 → 91 files | **+12** |
| | ⛔ **100 → 112** |

⭐ ***Ingesting an entire fourth container improved that corpus's validity by one.
Recording the findings worsened it by thirteen.*** ⛔ **A corpus cannot write down
what is wrong with it without making it more wrong** — ⚠️ **and `W28` above is
why: 100 of the 112 are files the repository itself already ignores.**

### The routings

| Item | What it is | ⛔ **Owner** | When |
|---|---|---|---|
| **`F21`** — `origin` names a file; the fourth container's units are **regions** of one. All **17** would record the same `origin`; `check_completeness` compares each against the file's **361** headings → *"sixteen false short-reads, or a check that has to be switched off"* | ⛔ **a framework ruling.** Three shapes offered — sub-file units, a generated split, or one unit — ⭐ **and the integrator explicitly declined to pick, which is §12 working** | ⛔ **CTO** | ⛔ **gates `ISO-09`** |
| **`Q20`** — **2,106** Given/When/Then lines in **244** `gherkin` fences. *"Fluent English prose that a reader does not want read aloud as prose"* | E04 / narration + the block vocabulary. ⚠️ **Option 3 mints a manifest field, and R9 makes a field cheap now and expensive after M2** | ⛔ **CTO** | ⛔ **gates `ISO-12`**; owed **before M3** |
| **`Q22`** — ⛔ **what checks `exercises`?** | ⭐ **ANSWERED — Ruling 60:** `validate` corroborates `exercises` **against the archive, not the declaration**, symmetric, `Unchecked` when documents were refused, same rule id. ⭐ **Reproduced with a negative control** (poisoned corpus: `validate ok=True, findings=0`; the fixture checker loud) | ⛔ **RELAY TO PO-INTEGRATION** — they raised it independently and are owed the answer | ✅ **closed** |
| **`F26`** — a **rule id is an interface** and nothing states whether it is stable | ⭐ **RULED — 64** | ⛔ **RELAY** | ✅ **closed.** ⚠️ **`W27` merged at `5c6c883`, so the rule id it moves has moved: a corpus-side measurement keyed on `[manifest]` for a home path in `corpus.json` now reads `[personal-data]`** |
| **`F25`** — a record refused under R7 is reported downstream as a record **that was never declared**. Two false `Unchecked` reasons | *"Small, cheap, and on a path R7 guarantees somebody walks"* | ⛔ **CTO to rule the shape**, then a framework task | after `W27` |
| **`F27`** — ⛔ **a ruling arrives as a message and nothing propagates it.** `Q5` took **6 hand-edits across 6 artifacts and 0 checks** | ⛔ **mine — see the C6 ruling below** | ⭐ **RULED — 63 (CTO) and check 6 (mine).** ⚠️ **Two rulings on one finding is not duplication here: 63 is the mechanism, check 6 is the carrier** | ✅ |
| **`F23`** — the integration catalogue is a **permissions dead end**. **7 of 11** contributions stranded | ⛔ **mine — the catalogue is in this repository** | ⭐ **ruled here** |
| **`F18`** / **`F19`** / **`F20`** | carried from round 18 | ⛔ **`F20`'s ignore half is RULED as `W28` above.** `F18`'s third state and `F19`'s `sibling`-profile blind spot remain the CTO's | before `SF-31` (M2) |

⛔ **`F21` and `Q20` are recorded `Blocked`, not `not done`** — Q18's ruling,
applied for the first time. ⭐ **`ISO-09` and `ISO-12` keep their acceptance
conditions and name the framework item holding them shut.**

### ⛔ CORRECTION — `SK-01` finding 45 was refused **twice**, not three times

⚠️ **It was routed to me as *"refused a third time."*** ⛔ **Measured in both
documents: they say *"not answered this round either"* and *"still not answered
here, and that is now twice."*** ⭐ **The word *third* in that commit belongs to
`F27`** (*"the third distinct instance"* of C6's family) **and to `F24`/`W22`**
(*"its third violation in four rounds"*) — ⚠️ **two neighbouring threes, and the
count migrated between them in the retelling.**

⛔ **The refusal itself is CORRECT and stands for the third round running:** the
question is about the **Java** corpus, it is unowned until `E07` opens, and
⭐ **it has already been routed — to `JS-01`'s Acceptance, where the `exercises`
flag is actually written.** ⚠️ **What the integrator offers instead is the
*discriminator*, which transfers; the answer does not.**

⭐ **And the standing rule takes a scalp on its first outing: a measurement is
quoted with the ref it was taken on.** ⛔ **An inflated count in a routing brief
is the same defect as an unrefed test total** — ⚠️ **it reads as escalation, and
escalation is what gets an owner to reopen something correctly closed.**

### ⭐ `Q22` arrived from both sides independently, which is the strongest signal available

⛔ **Round 18's `PO-18/1` — framework side, reading `validate/run.py`.** ⛔ **`Q22`
— corpus side, reading `corpus.json`.** ⚠️ **Neither author saw the other's
document.** ⭐ **Two independent measurements of one hole is not two findings; it
is a confirmed one**, and it goes to the CTO as a single item with both citations.

⭐ **The `exercises` answer for ISO is checkable and already known: zero, in all
55 units.** ⛔ **So the CTO's ruling has a free negative control waiting.**

---

## ⛔ RULED 2026-09-10 — **C6's family is *a decision with no carrier*, and `F23` is unblocked by a check, not by a favour**

⛔ **Three instances now, and the integrator is right to ask for one ruling rather
than three findings:**

| Instance | The decision | What was missing |
|---|---|---|
| the **absent catalogue** (round 17) | spec §9, `SK-07` and three rulings named a file | ⛔ **nobody was obliged to create it** |
| ⛔ **`F23`** | R19 says these entries belong in the catalogue | ⛔ **nobody was obliged to read the contributions** |
| ⛔ **`F27`** | `Q5` was ruled, correctly, and was right | ⛔ **nobody was obliged to propagate it** |

⭐ **They are one shape: the decision was correct, was recorded, and had no
carrier — so it stopped at whoever happened to be reading.** ⛔ **C6 has been
stated as *"a ruling that never reaches its artifact"*, which names the symptom.
The cause is that *reaching* was somebody's goodwill and not anybody's task.**

⛔ **RULED: a decision that changes another document is not landed until a
**check** or a **named owner with a trigger** carries it there.** ⭐ **`ruled`
already names the artifact (C6); this adds the second half — it also names who
moves it and when.**

### ⭐ `F23` — the ruling, and PO-Integration changes nothing about what they do

⛔ **They keep writing contributions in their own repository.** ⚠️ **That was never
the defect** — ⭐ **the catalogue's own header already says entries are contributed
*"by whoever measured them, from either side"*, so the contribution was always
legitimate and the permission wall was never the real wall.** ⛔ **The wall was
that adoption had no owner.**

⛔ **Wave-open check 6, mine: read each consumer repository's contributions file,
adopt what qualifies against the catalogue's own *belongs / does not* table, and
RECORD A DECISION FOR WHAT DOES NOT.** ⚠️ **The recorded refusal is the half that
makes this different from goodwill** — ⭐ **a contribution silently not adopted is
`F23` again with an extra step, and the contributor cannot tell the two apart.**

⛔ **Backlog to discharge on check 6's first run: 11 contributions, 4 already
counterparted (entries 5, 6, 7, 9), 7 stranded.** ⭐ **That the 4 arrived at all is
the evidence for the ruling, not against it: they were hand-carried by whoever
was in the room, which is exactly `F27`'s mechanism and exactly as durable.**

⚠️ **And the limit, stated so it is not discovered later:** ⛔ **check 6 is a
person on a trigger, not a machine** — ⭐ **which is weaker than `W25`'s enforcer
and is the right weight for a judgement call about what belongs in a catalogue,**
⚠️ **but it is the same class of mechanism that failed three times above, so it
is on the wave-open list by name or it will fail a fourth.**

## The wave checks — ⛔ **SIX at open, and check 4 AGAIN at close**

⛔ **All six are mine.** ⭐ **Check 6 was added round 19 by `F23`'s ruling.** ⭐ **RULED 2026-09-10: check 4 runs twice — at wave-open
AND at wave-close** — ⚠️ **and the second run is the one that matters, because
the trigger check 4 exists to catch is *a task ending*, not a wave starting.**

### ⛔ Why, and this round is the entire argument

⚠️ **I ran check 4 once, at open. In the same round, three things it exists to
catch happened AFTER it ran:**

| What moved | When | What the board said until now |
|---|---|---|
| ⛔ **`SF-10` approved and merged `966ab30`** | mid-round | `in-review`, on an unmerged branch |
| ⛔ **Ruling 53 merged into the rubric `1ee184f`** | mid-round | *"pending on an unmerged branch"* |
| **`CTO-18-1` / `CTO-18-2`** | mid-round | uncarried |

⭐ **Check 4 caught three stale rows at open and then went stale itself**, ⛔ **and
it went stale in the paragraph diagnosing exactly that.**

⛔ **A check that runs only at wave-open measures the tree the wave was PLANNED
against, not the tree it produced.** ⚠️ **Its own founding case proves the
timing:** `W14` and `W18` evaporated because *"a trigger that names a task is only
as good as somebody re-reading the board when that task ends"* — ⭐ **and a task
ends during the wave, not before the next one.**

⭐ **The close run is cheaper than the open run**, and that is why this is not a
doubling: at open, every row whose trigger has passed must be re-measured; ⛔ **at
close, only the rows this wave touched** — the merges are enumerable from
`git log`, so the instrument is *"what moved since I last measured"*, not a sweep.

⛔ **And the standing rule this generalises, which is broader than check 4:**
⭐ **a measurement is quoted with the ref it was taken on, or it is not a
measurement.** ⚠️ **Measured this round: the coordinator and I both counted
`host-verified` correctly and reported different answers, and the entire
difference was which tree.** ⛔ **Neither of us named the ref.** ⭐ **A number
without its ref is not a weak claim — it is an unfalsifiable one**, because the
reader cannot reproduce it and disagreement looks like error rather than drift.

---

---

## ⛔ CHECK 4 — THE FIRST CLOSE RUN, 2026-09-10 @ `75d55a6` → `40731e4`

⭐ **Ruled last round, executed here for the first time.** ⛔ **Instrument, and it
is the cheap one the ruling promised: `git log 75d55a6..` enumerates what moved,
and only those rows are re-measured.** ⚠️ **Everything that moved is the three
merges into the release tip plus four unmerged branches.**

⛔ **Verdict: the rule paid for itself on its first run.** ⭐ **Four rows wrong,
check 5 failing, and a duplicated `W`-id that no open-run could have seen —
because none of it existed when the wave opened.**

### The readings

| Row | Board said, at open | ⛔ **Measured at close** | Ref |
|---|---|---|---|
| **`SF-10`** | `done`, merged | ✅ **correct** | `966ab30` |
| **`SF-10` survey** | `done` | ✅ **correct** | `13b2857` |
| **`W25`** | ⛔ *"`todo` — NEVER STARTED. The branch is byte-identical to `HEAD`"* | ⛔ **FALSE — `in-review` → APPROVED → ✅ `done`, MERGED at third pass.** Three commits: `tools/quality/handoffs.py` **split into a package** (`__init__.py` 259 + `contract.py` 229), four test modules, **72 migrations** across `handoffs/`, plus `agent-protocol.md` and `review-rubric.md` | `feat/W25-handoff-check` @ **`f77bb7d`** — 2629 / 8 |
| **`SF-12` survey** | `in-progress` — *dispatched* | ⛔ **`in-review` at first pass → ✅ `done`, APPROVED and merged** | `1b2d993`; four escalations ruled, notably **one variant per page** |
| **`W26`** | ⛔ **TWO ROWS, TWO MEANINGS** | ⛔ **see the disambiguation below.** ⚠️ **First pass NOT STARTED → second pass `in-review` → ✅ `done`, MERGED at third pass** — ⭐ **22 mutants, 2 real survivors found and closed** | merged in `c84ca2e` |
| **`W27`** | `urgent`, no status | ⛔ **`in-review` at first pass → ✅ `done`, APPROVED and merged** — three translation sites plus two `errors.py` contracts. ⭐ **`validate/corpus.py:157`'s dead `PersonalDataLeak` arm is reachable again, reproduced independently** | merged **`5c6c883`** |
| **check 5 — `CLAUDE.md`** | ✅ at open | ⛔ **FAILS** — see below | `CLAUDE.md:102` |
| **base measurement** | `2490 / 8 @ `a7c114b`` | ⛔ **`2568 @ 40731e4` → `2570 @ 1b2d993` → `2649 @ c84ca2e`.** ⚠️ **THREE times in one round** | tip |

### ⛔ `W25` is the mirror of `W25`, and that is not a typo

⚠️ **Last round check 4 caught `W25` recorded `in-progress` against a branch
containing nothing, and corrected it to *"NEVER STARTED — byte-identical to
`HEAD`"*.** ⛔ **One wave later that sentence is false in the other direction**,
and the row now understates by an entire package with a migration.

⭐ **This is the strongest possible argument for the close run, because it is the
SAME ROW failing the SAME CHECK in the OPPOSITE DIRECTION within one wave.**
⛔ **A status is not a property of a task; it is a property of a task *at a
moment*** — and *"byte-identical to `HEAD`"* is the worst form of it, because it
names a **moving** reference. ⚠️ **`HEAD` moved. The sentence did not, and it
stopped being true without changing a character.**

⛔ **Rule, and it is the ref rule biting a row rather than a number: a status
that compares against `HEAD`, *"the tip"* or *"today"* is unfalsifiable a day
later.** ⭐ **Name the commit both sides were at.** ⚠️ **`fix/W26-gate-tell` is
recorded above as byte-identical to `40731e4`, not to `HEAD`, for exactly this
reason — and it will still be checkable next round.**

### ⭐ Rulings 59–65 arrived mid-round — what each changes for this board

| # | What it settles | ⛔ **What it changes here** |
|---|---|---|
| **59** | ⛔ **the legacy finding-number ceiling is 62, not 58** | ⛔ **`SF-10` minted 59–62 on a branch before the rule existed, and pinning 58 would red-line a merged record.** ⭐ **Developer 2 was right.** ⛔ **The collision is live on 61 AND 62** — `PO-2026-09-10-round18.md`'s own *For dependents* cited both meanings **four words apart**. ⭐ **Remedied by renumbering `po-round18` to `PO-18/1..5`, on this branch; `SF-10` is NOT touched** |
| **60** | ⛔ **`validate` corroborates `exercises` against the ARCHIVE, not the declaration** | ⭐ **Closes `PO-18/1` and PO-Integration's `Q22` in one stroke** — ⛔ **and the relay is owed, because they raised it independently from the corpus side** |
| **61** | ⭐ **Ruling 53's two artifacts are a rule and its worked example** | see the check 3 table |
| **62** | `W25/7` accepted | rides with `W25` |
| **63** | ⛔ **`F27`** — a ruling needs a carrier | ⭐ **pairs with wave check 6**; 63 is the mechanism, check 6 is the carrier |
| **64** | ⛔ **`F26`** — rule-id stability | ⛔ **relay: `W27` merged, so `[manifest]` → `[personal-data]` for a home path in `corpus.json` has ALREADY happened** |
| **65** | §8a's marker spelling | ⭐ **It caught its own author first — the CTO's handoff measured 17 findings against 8 real ones.** ⚠️ **Third instance this wave of a check finding its author** |

### ⭐ Rulings 66–69 — two ratify mine, one narrows it, one is placed here

| # | | ⛔ **What it changes** |
|---|---|---|
| **68** | ⭐ **RATIFIES *one minter per id space*, NARROWED** | ⛔ **Minting is about the ID, never the authority to decide.** ⭐ **C6 locates a ruling by its ARTIFACT, so an UNNUMBERED RULING STILL BINDS** — ⚠️ **without that clause every routing would wait on a CTO round, which is the opposite of what the rule is for.** ⛔ **My W26 ruling above must be read with it: the CTO was never asked to stop routing, only to stop numbering** |
| **69** | ⭐ **needs no amendment** | the one gap the CTO checked — a corpus root with no `.git` — ⭐ **is already closed by `W28`'s criterion 4** |
| **66** | ⛔ **`W25/8`'s remedy REFUSED as a no-op** | ⭐ **The shipped message already interpolates the marker, the 10-line window and the closed set.** ⚠️ **The survey's author simply wrote before the check existed.** ⛔ **Recorded so nobody spends a commit on an approved surface for a gap that is not there** |
| **67** | ⛔ **`W26/1`: the root is correct — ASSERT THE BOUND, DO NOT EXTEND IT** | ⭐ **Three trees under three gates, not one hole.** ⛔ **Extending is refused by Ruling 31, and `tests/fixture_checks/corpus.py` stays ungated under Ruling 60's oracle-independence.** ⛔ **The defect is a bound asserted nowhere — and placing it is mine: see `W29`** |

### ⭐ `W29` — Ruling 67's bound, placed

| | |
|---|---|
| **What** | ⛔ **One constant naming the three gated trees, plus the docstring sentence that says why the fourth is ungated.** ⭐ **Not an extension — an assertion that the existing bound is the intended one** |
| **Owner** | **Developer 2** — `tests/test_gate_coverage.py` is the surface they just finished in `W26` |
| **Size** | ⭐ **Smallest on the board.** One constant, one sentence, one test |
| **When** | ⛔ **with or immediately after `FND-08`**, same author, same wave |
| **Acceptance** | the constant names the three trees · ⛔ **the docstring states why `tests/fixture_checks/corpus.py` is ungated, citing Ruling 60's oracle-independence** · a test fails if a fourth tree appears unnamed |
| **⛔ Not in scope** | ⛔ **extending the gate to a fourth tree.** ⚠️ **Ruling 31 refuses it, and `W26/1` reads as if it were the fix** |

### ⛔ Three findings from CTO round 20, carried

- ⛔ **`CTO-20-2` — `W26/1`'s *"three"* is a count over an UNSTATED SET.** ⚠️ **The
  raw tell finds 20 outside `src/`.** ⭐ **A recurrence of `CTO-19-8`, and the
  second time this wave that a bare count turned out to be a fact about its
  instrument** — ⛔ **which is `W29`'s whole reason for existing: name the set.**
- **`CTO-20-3`** — `W26`'s handoff says 471 lines; measured **478**.
- ⛔ **`CTO-20-5` — `po-round19` moved twice mid-review, THIRD ROUND RUNNING.**
  ⚠️ **Accepted as a real cost, not deflected.** ⭐ **The mitigation is the one
  already in force — every cell names its ref, so a moved branch is *visibly*
  superseded rather than silently wrong** — ⛔ **but it does not make the reviewer's
  re-read free, and this row exists so the next PO does not treat it as solved.**

⛔ **MERGE ORDER, proved with a negative control: `po-round19` BEFORE
`cto-round19`, always.** ⚠️ **Withholding this branch gives 3 failed, floor 1
finding, merge exit 0, no conflict** — ⭐ **the fifth instance of the trial-merge
clause, and the second caught before the merge.**

⛔ **Also approved as written: `FND-08` and `FND-09`, with all five prices
reproduced, and walk 4's refusal STANDS.** ⭐ **A refusal surviving an
independent re-measurement is the strongest form a scoping decision takes.**

### ⛔ THE CLOSE RUN WENT STALE WHILE IT WAS BEING RUN — second pass, tip `1b2d993`

⚠️ **The CTO ruled and the coordinator merged while this section was being
written.** ⛔ **Four of its own readings were superseded before they were
committed:** `W27` and the `SF-12` survey **merged**, `W26` **started**
(`283ae90`), `W25` was **APPROVED**, and the base moved `2568` → `2570`.

⛔ **This is the third consecutive round in which the board's own status work
went stale mid-round**, and last round's handoff diagnosed it happening to its
author in the paragraph diagnosing it. ⭐ **So the close run is not the fix —
it is the same instrument at a better moment, and it has the same failure
mode.**

⛔ **What actually holds, and it is the only thing that has held all three
rounds: every cell names its ref.** ⚠️ **A row that says `in-review @ 655b527`
is not *wrong* once `655b527` merges — it is a true statement about a commit,
and the reader can see it is superseded.** ⛔ **A row that says `in-review` is
wrong the moment it changes and gives the reader nothing to notice it with.**

⭐ **So the rule earns its keep twice over: it does not stop staleness, it makes
staleness VISIBLE — and the first-pass readings above are kept, not overwritten,
for exactly that reason.**

### ⛔ Check 5 FAILED — `CLAUDE.md` contradicted itself in adjacent paragraphs

⚠️ **`:102` said *"In flight: M1 step 1.4 — `SF-10`"*. `:105` said `SF-10` was
done and step 1.4 closed.** ⛔ **The correction had been APPENDED BELOW the stale
sentence instead of replacing it.**

⭐ **Three sentences further on, that same file says a stale line there
*"misdirects every agent that starts."*** ⛔ **It was misdirecting them, in the
paragraph that says so** — which is check 3's `landed in` column and check 4's own
diagnosing-paragraph defect, now three times in two rounds.

⛔ **The generalisation, and it is broader than `CLAUDE.md`: a correction that
leaves the original standing is not a correction, it is a second copy** —
⚠️ **and the reader takes the first sentence that answers their question, which is
the stale one.** ⭐ **Corrected by replacement, and the section now points at this
board for what is open in the step rather than restating it.**

---

## ⛔ RULED 2026-09-10 — **`W26` was minted twice, and an id space gets ONE MINTER**

⛔ **Measured at close: two different `W26` rows are live on this board, from two
branches, in one wave — and the merge combined them cleanly with no conflict.**

| | Subject | Minted by | State |
|---|---|---|---|
| **`W26`(PO-18)** | `PO-18/2` — PEP 758 syntax in `tools/quality/config.py`; **NOT A DEFECT** | PO, `chore/po-round18` | ✅ **closed, discharged** |
| **`W26`(CTO-18)** | ⛔ **Ruling 57** — `W7`'s reader tell resolves the name's *origin*, not its spelling | CTO, `chore/cto-round18` | ⛔ **live** — Developer 2, branch `fix/W26-gate-tell` |

### ⭐ This is the finding-number collision one level up, and it refutes the same remedy

⚠️ **Last round ruled that findings are numbered per-document because an
allocator file is invisible across branches, and warned in terms:** ⛔ ***"worst
case both increments merge cleanly and one number is lost silently."***
⭐ **That is not a prediction any more. It happened, to `W`-ids, in the very wave
the warning was written**, and the warning's own wording is why it was found:
`git merge` reported success.

⛔ **But the finding rule's REMEDY does not transfer, and that is the interesting
half.** ⚠️ **Findings were fixed by scoping the number to its document — and
`W`-ids already live in exactly one document.** ⭐ **So the defect is not *no
allocator*. It is *two allocators*: one file, two authors, two branches.**

⛔ **RULED: an id space has exactly one minter, and the minter is whoever owns the
document the space lives in.**

| Space | Minter | Why it has never collided |
|---|---|---|
| **Ruling numbers** | **CTO** | one author, and it is why `57` and `58` are clean |
| **`W`-ids, task ids, board rows** | ⛔ **PO** | `BOARD.md` is the PO's document (line 3) |
| **Finding numbers** | per-document author | ruled round 18 |

⭐ **The CTO does not lose anything they were using this for.** ⚠️ **Their round-18
routing of `SF-10`'s two structural findings was correct, wanted, and urgent** —
⛔ **what it did not need was a number.** ⭐ **A routed finding arrives as
*Ruling 57* and *Ruling 58*, in the space the CTO already owns and already mints
without collision; the PO gives it a `W`-id when it lands on a row.** ⚠️ **One
extra hop, and it is the hop that makes the collision unrepresentable rather than
detected** — ruling 29's move, again.

### ⛔ The disambiguation — `W4`'s precedent, and NEITHER is renumbered

⛔ **`W26`(CTO-18) KEEPS the bare id `W26`.** ⭐ **A branch (`fix/W26-gate-tell`),
an assignee and an urgency all already point at it**, and renaming a live branch
to tidy an id is the migration costing more than the ambiguity.

⛔ **`W26`(PO-18) is SUPERSEDED IN PLACE and is cited as `W26(PO-18)`.** ⭐ **It is
closed, discharged, and cited in exactly one place outside its own row** — the
round-18 handoff, ⚠️ **which is a record and is not rewritten.** ⭐ **The board is
where a superseded record gets superseded**, exactly as `53` / `54` / `55` were.

⛔ **`W28` and up are minted by the PO only.** ⭐ **High-water mark measured across
every branch in the repository, 2026-09-10: `W27`.** (`W99` exists and is a
deliberate non-id in an example.)

### The six, at open

⛔ **6 — catalogue contributions: read each consumer repository's contributions file, adopt what qualifies, and RECORD A DECISION FOR WHAT DOES NOT.** ⭐ **Added round 19; the argument is in `F23`'s ruling above.** ⚠️ **First run owes a decision on 11 contributions, 7 of them stranded.**

### ⭐ This round's readings — ⛔ **checks 3 and 4 both changed the plan**

| # | Check | Reading, 2026-09-10 @ `e5bcc85` |
|---|---|---|
| 1 | index present and current | ✅ clean in the pinned image |
| 2 | `[structural]` triage | ✅ **131 marker lines across 32 files** |
| 3 | ⛔ **C6 — every ruling reached its artifact** | ⛔ **the index was wrong on 6 of 10 audited, all in one direction** |
| 4 | ⛔ **re-measure every row whose trigger has passed** | ⛔ **3 of 9 step-1.4 rows wrong, in *both* directions** |
| 5 | `CLAUDE.md`'s *Where to start* | ✅ names M1 step 1.4 / `SF-10`, matching the board. ⛔ **AND IT FAILED AT CLOSE — see the close run** |
| 6 | catalogue contributions | ⛔ **did not exist at open; first run owed next wave** |

### ⛔ Check 3 — **the rulings index is an audit, and the audit was wrong six ways**

⚠️ **The index at `handoffs/CTO-2026-09-09-round17.md` lists 30, 43, 47, 48, 49,
52, 53, 55 and 56 as unlanded or partly so, and summarises itself as *"six
rulings have not reached an artifact."*** ⛔ **Measured by opening every named
artifact: six of the ten audited had landed and the index says they had not.**

| # | Index says | ⛔ **Measured** | Where it actually is |
|---|---|---|---|
| **30** | not landed | ⛔ **was true — ✅ LANDED THIS ROUND** | spec §4, *The complete key list*. ⭐ **The reversal held: `media` was never wrongly added, and no test asserts equality** |
| **43** | *"not scoped — four walks waiting"* | ⭐ **LANDED** | `tools/quality/source_names.py`, shipped with its migration |
| **47** | *"W20 — scheduled"* | ⭐ **LANDED** | `../conventions/personal-data-shapes.md` + `tests/test_shape_vocabulary.py` |
| **48** | *"`agent-protocol.md`"* | ⭐ **LANDED — in the other file** | `../conventions/module-structure.md:445`. ⛔ **`W24`'s row was right and the index was stale** |
| **49** | not landed | ✅ **correct — genuinely open** | nothing handoff-shaped in `tools/quality/`. This is `W25` |
| **52** | *"not landed"* | ⭐ **LANDED verbatim** | `../conventions/agent-protocol.md:226` |
| **53** | *"`FND-05a` ✅ · rubric §4b"* | ⭐ **RESOLVED by Ruling 61 — and BOTH my predecessor and I had the framing wrong** | ⛔ **The two sites are NOT duplicates and neither is emptied.** ⭐ **They are a rule and its worked example:** `review-rubric.md` §4b is the source; `../conventions/workspace.md` keeps its section because it holds the **exit-2 design fact the rubric must not own.** ⚠️ **We both read *"one clause in two files"* and reached for a collision** — ⛔ **the actual defect was the index**, which is check 3's own subject. ⭐ **The pointer note stands; the reasoning behind it does not** |
| **55** | *"Ruling 43's task"* | ⭐ **LANDED verbatim** | `../conventions/agent-protocol.md:200` |
| **56** | *"`module-structure.md` — PO"* | ⭐ **LANDED** | `../conventions/module-structure.md:39` |
| **46** | landed ✅ | ⭐ **LANDED** | ⚠️ **7 call sites, all in the defining module. Zero external consumers** |

⛔ **Genuinely open after the audit: 30 (now closed), 49, and 53's rubric half.**
⭐ **Three, not six.**

#### ⛔ The finding, and it is worth more than the nine corrections

⚠️ **An audit column is a *summary of a status owned elsewhere* — which is this
board's own named defect, arriving in the instrument built to catch it.** ⭐ **It
went stale in the same direction all six times: *understating* what had landed.**

⛔ **And that direction is the expensive one, because it is the one that looks
diligent.** ⚠️ **An index that over-reports landing gets caught the first time
somebody looks for the clause.** ⭐ **One that under-reports it costs a re-landing
— and a ruling landed twice, by two people, in two documents, is how `48` came to
be claimed for `agent-protocol.md` and to actually live in `module-structure.md`.**

⛔ **The rule: an index of where rulings landed is *derived by opening the
artifacts*, never maintained beside them.** ⚠️ **Its author said the writing of it
*was* C6's audit — ⭐ and it was, for the rulings whose artifact they had just
written. It was a guess for the ones somebody else carried**, and every one of the
six errors is in that second set.

#### ⛔ Ruling 55's own founding number is recorded three different ways

⚠️ **The rule says a number in a ruling is an instrument reading. Its own
measurement — the §7c grep versus the check — is on record as:**

| Artifact | Reading |
|---|---|
| `../conventions/agent-protocol.md:203` and `BOARD-ARCHIVE.md` | **7 → 19, across 11 modules** |
| `../conventions/review-rubric.md:691` | **7 → 19** |
| ⛔ `tools/quality/source_names.py:42` | ⛔ **7 → 13** |
| ⭐ **the tree today** | ⭐ **0 → 0** |

⛔ **Three artifacts, two answers, one experiment** — ⭐ **and the rule is right,
which is why this is not embarrassing but confirming.** ⚠️ **The correction is
`FND-08`'s and it is one line: whichever number is true, it is stale, because the
migration ran.** ⛔ **A number quoted from a ruling after the migration it measured
has completed is not merely imprecise; it describes a tree that no longer exists.**

| # | Check | Command |
|---|---|---|
| 1 | Index present and current **in the main checkout** | `built_at_commit` vs `git diff --quiet <it> HEAD -- src tools docs` |
| 2 | The `[structural]` triage list | `grep -rn '\[structural\]' docs/tasks/handoffs/` |
| 4 | ⭐ **Nothing ruled is queued-but-unlanded across the boundary** | ask each document owner; ⛔ **and re-measure every board row whose trigger has passed** |
| 5 | ⭐ **NEW — `CLAUDE.md`'s *"Where to start"* names the open milestone** | ⛔ **read it.** It loads into **every** session, so a stale sentence there misdirects every agent that starts — ⚠️ **and it has been the last to learn twice in two rounds** |
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
| W5 | ⛔ **CORRECTED — the number is right about the *file* and misleading about the *task*.** `unitdoc.py` is **827 lines**; ⭐ **about 250 are left to port.** SF-05, SF-06 and SF-09 already landed the overlay reader (`unit/content.py`, 300 lines), the section-key vocabulary, the error type and `AUTHOR_MAY_NOT_WRITE` as `DERIVED_FIELDS`, and **`_check_address_against_map`'s job is already done by `validate/structure.py`** | `SF-10` | at **SF-10** | ⚠️ **`SF-10` has been carrying an 827-line port in its head and the real figure is a third of that** — so the task is **re-priced**, and this row is corrected so the number stops being quoted at its old scope. ⭐ **The inventory *sums* to 827** (201 header / 30 gates / 74 archive reading / 189 derived / 97 build / 134 `content.json` / 102 `unit.json`), so it is checkable rather than asserted. ⭐ **It still wants to be a package, for a measured reason: the same contract is ~145 lines in the source and 300 here — ≈2.1× expansion.** ⚠️ **One data point, and the survey said so** |

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

#### ✅ ROUTED 2026-09-10 — **finding 45's accountability is `JS-01`'s Acceptance, and the *claim* is bounded by a check**

⛔ **`UNOWNED until E07 opens` is not a routing; it is a row waiting for somebody
to arrive.** ⚠️ **And it was sitting in the destination this board measured as the
weakest there is** — a board row with an owner and a trigger — ⭐ **which is the
same destination `W14` evaporated from, twice.**

⭐ **The routing, and it has two halves because the question does:**

| Half | Goes to | Why there |
|---|---|---|
| ⭐ **the judgement** — *do those files ask the reader to produce something?* | ✅ **`JS-01`'s Acceptance** (`E07`, M6) | ⛔ **`JS-01` owns `JS/corpus.json`. It is the task that writes the flag**, so it is the task that justifies it. ⭐ **An acceptance clause has a reviewer behind it** |
| ⛔ **the claim** — *does `exercises: true` match what the archive holds?* | ⛔ **`studyforge validate` — `PO-18/1`, below** | ⭐ **Nobody has to be *trusted*. The tool decides**, and it decides source-agnostically (R1) |

⛔ **That second half is what makes this closable, and it is the part the original
question could not see.** ⚠️ **The finding asked *"who is accountable for a
judgement about 168 files?"*** ⭐ **The better question is *what is the judgement
allowed to be wrong about?*** — and the answer is: the adapter decides what it
**emits**, after which the flag is corroborated against the emission. ⛔ **A
judgement only a person can make, bounded by a check a machine makes.**

##### ⚠️ And the finding was already stale in the epic it was routed to

⛔ **`E07`'s own measured-facts table has carried the finer numbers all along and
nobody cross-referenced them.** ⭐ **`168` is the *test-class* count; the same
table records `163` maximum name-paired exercises and `14` impl classes with no
`<Name>Test.java`.**

⚠️ **So the finding's headline number was superseded, in this repository, before
it was routed anywhere** — ⭐ **which is the standing rule arriving from a new
direction: a finding is a measurement with an as-of, and it is re-run before it
becomes a task.** ⛔ **Here the re-run was not even a command; it was reading the
epic the finding named.**

##### ⛔ `PO-18/1` — `studyforge validate` does not corroborate `exercises`, and the fixture checker does

**Measured 2026-09-10, `e5bcc85`:**

| | |
|---|---|
| the fixture checker | ⭐ `tests/fixture_checks/__init__.py:140` — `if bool(manifest.get("exercises")) != (practices > 0)`, rule id **`exercises-flag`** |
| `studyforge validate`'s check list | `validate/run.py:30` — `structure.CHECKS + paths.CHECKS + source.CHECKS` |
| ⛔ **an `exercises-flag` check among them** | ⛔ **none** |
| what it *does* check | ⭐ `check_practice_counts` — **per-unit** declared-vs-on-disk |

⛔ **So the manifest's front-door boolean is asserted in our own test scaffolding
and unasserted in the tool an adapter author is told to trust (R2).** ⚠️ **That is
`W7`'s shape exactly** — *"the tool an integrator is told to trust reports the
corpus's front door clean"* — ⭐ **and `W7` is the row this board rated URGENT.**

⚠️ **The gap is narrow and real:** per-unit counts are checked, so a corpus that
declares two practices and ships one fails. ⛔ **A corpus that declares
`exercises: true` and ships no practice anywhere passes**, because no unit
declared any to disagree with.

⭐ **Owner: CTO to rule the check's shape, then Developer 2.** ⛔ **Owed before
`JS-01` runs**, and `JS-01`'s Acceptance says so, which is what stops it becoming
another row nobody re-reads.

---

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
`TestCases.md` is **191** Gherkin scenario declarations that look exactly like a grader corpus
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

#### ✅ **Q5 RULED 2026-09-10 — INGEST it. ⛔ 38 → 55 units, and `exercises` stays `false`.**

⭐ **This is the PO's call, not the integrator's, and the deciding argument is
that there is no true reason to exclude it.** ⛔ **X1 does not ask *is exclusion
defensible?* — it asks for a `why` that is TRUE**, and every candidate `why` has
been measured away:

| Candidate `why` | ⛔ **Measured** |
|---|---|
| *"duplicate"* / *"aggregate"* | ⛔ **False.** 1 of its 2,524 distinct lines appears in `src/`, and that one is a bare code fence. Real aggregates are digest-identical concatenations |
| *"structure cannot be recorded"* | ⛔ **False.** Its 361 duplicated headings **are** its 17 chapters, recorded in the curriculum exactly as every other container's units are — **§6 is satisfiable** |
| *"it is a unit, not a container"* | ⛔ **False.** 0 of 38 unit links sit where this one sits; it is the only one of 39 targets linked **as** a `#` heading |
| *"it is grader material"* | ⛔ **False, and it is the catalogue's own entry 8** |

⛔ **With no true `why` available, exclusion is unavailable.** ⭐ **That is X1
working as designed: the asymmetry — an inclusion needs no justification, an
exclusion does — decides this case on its own, without anybody weighing 17 units
against the cost of ingesting them.**

⭐ **And the affirmative reason, which is worth more than the absence of a
negative one:** ⚠️ **excluding it would make ISO an *easier* corpus, and ISO's job
is to be a hard one.** ⛔ **It is the second source (§12), and its value is
measured in findings, not in a tidy site.** ⭐ **A fourth container that is a
different shape — 17 chapters, **191** Gherkin scenario declarations, a fence language nothing
else uses — is exactly the extensibility signal M8 exists to produce.** ⚠️ **The
39th target being the one odd one is not a nuisance; it is the test.**

**Two constraints ride with the ingest, and they are Acceptance, not advice:**

1. ⛔ **`exercises` stays `false`. This does not make ISO runnable.** ⭐ **Catalogue
   entry 8 is the rule and this is the case it was written on:** *191 Gherkin
   scenarios that look exactly like a grader corpus and ask the reader to do
   nothing.* ⛔ **Ask whether the reader is asked to produce something — not
   whether the files look like test code.** ⚠️ **ISO remains complete at the
   reading floor and never enters the execution track (§11.0, C5).**
2. ⛔ **The 244 `gherkin` fences render as plain fenced text, asserted, not
   assumed.** ⭐ **`SF-11`'s ruling already decides this** — *a language with no
   grammar is left alone rather than dressed up as code* — ⚠️ **and catalogue
   entry 10 is the sibling: a default that guesses is worse than a default that is
   plain.** ⛔ **`gherkin` has no vendored Prism grammar, so the failure mode is a
   silent mis-highlight, which is `SF-11`'s screenshot defect again.**

⭐ **The two open questions turned out to be one rule seen from both sides**, and
that is the most transferable thing here: ⛔ **finding 45 asks *"168 files that
look like graders — are they?"* and Q5 asks *"191 scenarios that look like
graders — are they?"*** ⚠️ **Two corpora, two integrators, one question.** ⛔ **The
framework's answer must be identical and must not be a per-corpus judgement (R1)
— which is why both now land on the same check: `exercises` is corroborated
against what the archive holds, by the tool** (`PO-18/1`, above).

⚠️ **Recorded as a decision, not a proposal awaiting one**, per the standing rule
that implementation decisions belong to the PO and the CTO. ⛔ **It is reversible
by a later commit** — an ingested container can be excluded with a true `why`
later; ⭐ **the irreversible direction is the other one**, because a corpus that
shipped without it teaches nobody that the shape exists.

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
| W9 | **The markup contract has one side written** — `render/pageassets/surface.py` guesses `SF-12`'s class names. Ruled round 11: **SF-12 reviews the names in one commit as its first act** | `SF-12` | at **SF-12**, step 1.5 | ✅ **LANDED 2026-09-10 in `E03`** as `SF-12`'s *First act* subsection — ⭐ **and the row's own warning is why it went there:** *"its first act"* is a sequencing instruction that only works if it reaches the task **before** the task starts, ⛔ **and a board row is the destination that has evaporated twice.** ⚠️ **The path was under-specified here too** — the module is `render/pageassets/surface.py`, and its docstring already carries the *may-rename-never-duplicate* rule this row was asking for |
| W10 | **Palette tokens with no painter** — `--hl-*`, `--player-height`, `--practice*` are defined and unclaimed. Ruled round 11: a **named, self-retiring list**, and E04/E08 acceptance gains *remove your token* | PO → E04, E08 | **before E04 / E08 are authored** (M3, M5) | ⭐ Self-retiring is the good part: the list is a number that must reach zero, ⛔ not an exclusion that lives forever. The word *"unclaimed"* currently appears nowhere |
| W11 | **`api` is a generic field name** — the tree guard would flag a module reading an unrelated `api` key. `SF-33` finding 3 | ◐ **ACCEPTED, cost named** | if a colliding field is ever minted — realistically `SF-10` or E03's TOC | ⭐ **Zero instances today**, and the finding states its own remedy: narrow the rule to the module rather than drop the field. ⛔ Recorded so the remedy is not re-derived under time pressure |
| W12 | **The extraction source's `naming.py` docstring says 1,282 where the tree holds 1,290.** `SF-09` finding 3, routing half | ◐ **ACCEPTED, cost named** → E11's integration catalogue | at **SK-07** / the catalogue | ⭐ A defect in a repository v1 does not modify (R20), and the *rule* it exercised — **a claim about another repository is verified in that repository** — is already ruled and applied. ⚠️ Its ask was *"route to whoever owns the drift catalogue"*; `DOC-2026-09-09-codesignal-drift.md` predates it and has no entry |
| W14 | ⏳ **in flight** — ⛔ **TWO missing invalid fixtures on FND-04's surface, and they are one task** — the **count-mismatch** fixture (`E10` names six, five exist) and the **`user` + `authoritative` R5 pair** (finding 29). ⭐ **Both are record defects, not coverage holes: `check_counts` and the trust rule are implemented and tested — only the fixtures are absent** | **Developer 1**, after `W8` | ⛔ **before `SK-01`**, which reads `SF-25`'s output as its model of "valid" | ⚠️ **Measured on `feat/SF-23-exercise` @ `5a01a30`: the graded fixture shipped, the count-mismatch fixture did not** — `tests/fixtures/invalid/` still holds five. ⛔ **`SF-23`'s Acceptance names both, so this is a live review item, not an escaped one** — flagged to the CTO while the branch is in review. ⭐ **That is the mechanism working: routing an item into a task's *Acceptance* rather than a board row is what makes a reviewer the backstop** | ⛔ **An acceptance clause naming a fixture that does not exist is unfalsifiable** — the same class as an acceptance satisfied by an untracked artifact, arriving in a *condition* instead of a build product. ⭐ Ruled: **build the fixture, keep the clause** — it is the only statement that the count check is exercised, and the count check guards *silently lossy ingestion* |
| W23 | ⛔ **WAS a live R7 hole — two personal-data shapes passed the gate clean:** **tilde-rooted paths** and **`/export/home/<name>/`**, both carrying an account name. ⚠️ **Blast radius was wider than `origin`** — `assert_clean` walks **every string in a document**. Developer 2's finding 3 (two overlapping refusal sets) rode the same task | **Developer 2** | ✅ **`done` — merged `d178665`, handoff `R44-gate-shapes.md`** | ⛔ **The board carried this as `in-progress` for a full round after it merged — check 4 caught it.** ⭐ **The remedy was not a longer list: three asserted layers, a 9×3 matrix with two controls, and — the part worth keeping — ⛔ a *declared* `RESIDUAL` of three shapes the gate deliberately does not refuse**, because refusing `/var/lib/home/cache/x.md` would refuse a legitimate corpus. ⚠️ **Finding 3 closed structurally**: both readers now import one predicate and a test asserts they agree |
| W24 | **Ruling 48 — a derived-set assertion asserts *inhabitation*.** `test_a_sweep_excludes_exactly_…` was **born vacuous**: both sides computed, both empty under a directory exclusion, and it passed | PO | ✅ **LANDED this round** in `../conventions/module-structure.md` | ⭐ **Fifth instance of *a check that cannot fail*, and the first with a mechanical tell** — the four before it needed judgement. ⚠️ **It is *`0 = 0` is not a pass* in a second instrument**, and ⛔ **a rule ruled in one instrument does not transfer itself to another**: the same person ruled both without seeing the second while writing the first |
| W25 | **Ruling 49 — `tools/quality` gains a handoff check.** ⛔ **The six sections and the markers are a *contract*, and the only thing enforcing them is a grep in a rubric that a person runs from memory** | **Developer 2** | ⛔ **`in-review` — `feat/W25-handoff-check` @ `f77bb7d`, 2629 / 8.** ⚠️ **CORRECTED at check 4's close run: the previous cell said *"NEVER STARTED, byte-identical to `HEAD`"* and was true when written.** ⛔ **`HEAD` moved; the sentence did not** | ⚠️ **Three instances: `SK-01` (six findings, no markers — approved twice), `fix/gate-shapes`, and this.** ⭐ **This project ruled four times in one round that a rule a machine can check should not be a rule a person checks — and then left its own handoff contract as the exception.** ⛔ **RE-PRICED, and it is not small: 29 of 52 files in `handoffs/` are not `<TASK-ID>.md`** — 23 not task-shaped at all, 6 compound or suffixed. ⭐ **So the hard part is deciding what a handoff *is*, and the answer is `FND-08`'s: exempt by declaration, never by guessing at a filename.** ⛔ **SCOPE ADDED 2026-09-10 — this check is also the enforcer for per-document finding numbers** (`<TASK-ID>/<n>`, ruled above): ⭐ **a second, cheaper assertion on the same file, and a *shape* is what this check was already going to test.** ⚠️ **Numbers 20–58 in the existing 12 documents are GRANDFATHERED** — ⛔ **a check that reds on them demands that a record be rewritten, which this project forbids** |
| W20 | ⛔ **Repository-wide §7c check — and its migration, in the same commit** (Ruling 43) | **Developer 2** | ✅ **`done`** — ⭐ **re-measured 2026-09-10: `0` hits by the check, `0` by the grep, floor clean, exit 0** | ⛔ **The board carried this row twice, as `todo` and as `done`, two rows apart.** ⭐ **A repository-wide check goes red the moment it lands**, so Developer 2's finding 1 is ruled: **a commit adding a check owns its migration.** ⭐ **The exemption generalises: exempt *documents*, never modules.** ⚠️ **Its pre-migration count is on record three different ways — 7→19 in two conventions, 7→13 in the check's own docstring** — ⛔ **and all three are now equally stale, because the migration ran.** ⭐ **That is Ruling 55 confirming itself** |
| W21 | ⚠️ **A fifth rubric gap: nothing checks for dangling pointers after a docs move.** `SK-01` built the far end before deleting the near one — ⛔ *"the reverse order would have produced a green suite and sixteen dangling pointers, and nothing in the rubric would have caught it"* | ⭐ **REASSIGNED — `FND-08`, Developer 2.** ⛔ **Not the CTO and not the rubric** | with `FND-08` | ⛔ **A rubric clause is a rule a person runs from memory, which is the exact thing Ruling 49 refuses.** ⭐ **Measured, and it inverts the price: `0` dangling links today, so there is no migration — ⛔ but 8 of 8 naive hits are FALSE, every one illustrative markdown inside backticks.** ⚠️ **So the cost is the parser, not the sweep**, and a repo-wide check that is 100% false-positive on its first run is one somebody switches off |
| W22 | **Finding 44 owed to the integration catalogue**, not to `SK-01` — ⭐ **two of its three numbers came from PO-Integration** | **PO** → catalogue | ✅ **routed this round** | ⛔ Fixing it inside `SK-01` would have put a cross-source fact in one skill, where the next source cannot find it (R19) |
| W17 **+ W19** | ⛔ **One commit, and for the reason W7+W13 were.** **W17:** *"describe a value without reproducing it"* — ⭐ **four spellings shrank to two documented holdouts while the item waited** (ruling 36). **W19:** ⛔ **the 39 remaining `{value!r}` sites, ruled urgent** | **Developer 2**, after `FND-07` | ⛔ **after `FND-07`** | ⭐ **This is the `label_of` defect at repository scale, and it is live: `W1` and `W7` are both on this exact discipline, so a fix to one spelling leaves three.** ⚠️ **It compounds with Ruling 20 one level down:** the personal-data **gate** had two copies that disagreed; the **diagnosis helper** has four. ⛔ §1a's *"do not re-derive the patterns, refused five times"* was about the **patterns**, not the **helpers** — so nobody swept here. ⚠️ **Deliberately not unified now:** three of the four are other tasks' contract surfaces and it would collide with two branches mid-flight |
| W18 | ⏳ **in flight, with W14** — ⛔ **`user` + `authoritative` is accepted today** — measured — so **a grader the reader wrote may declare itself the source's own.** ✅ **RULED 35: `authoritative ⟹ bundled`, stated positively** | **Developer 1**, with `W14` | before `SK-01` | ⭐ **The author believed the set should be `("bundled",)` and did not change it**, because `unit.trust` owns the rule and `E06` names only the `generated` pair — ⚠️ **an argument, not a measurement**, and they said so. ⛔ **Exactly the restraint R21 asks for**: a task that meets an unlocated contract stops and asks. One entry in `unit.trust.FORBIDDEN` if the CTO agrees |
| W16 | ⛔ **Every canonical example in the spec is a hand-maintained copy of a contract the code now owns** — ⭐ **the last such pair in the project.** The instance: `MANIFEST_KEYS` has **ten** keys, spec §4's example carries **nine**, and `media` was unteachable from the spec | ✅ **spec text — PO, LANDED 2026-09-10**; ⏳ **the asserting test — Developer 2, still owed** | ⛔ **before `SK-07` generates a manifest** | ✅ **§4 now carries *The complete key list* beside the example, with required/optional marked and the derivation named.** ⛔ **REMEDY INVERTED — Ruling 28 REVERSED by Ruling 30, and the reversal HELD: `media` was never added to the example, and no test asserts equality.** ⭐ **The two one-way checks are what remain: subset (the spec cannot teach a key the code lacks) and coverage (the code cannot own a key the spec never names — ⭐ the half that closes `media`).** ⛔ **Equality would have *compelled* the harm**: `SK-07` **generates** manifests, so an exhaustive example propagates an optional key onto every corpus, including ones with no media, and R9 freezes it at first declaration |
| W15 | ⛔ **Tooling wrote to a source repository's root ignore file** — a `graphify` git hook appended `graphify-out` to the ISO repository's ignore file on an ordinary commit, unrequested, ⚠️ **in the one repository where R3 is absolute.** Second half: `.claude/settings.json` carries a machine-local absolute path, an R7 exposure **created by tooling that no ruling names as a source** | PO → `OPS-05`, `SK-07` item 9 | ⛔ **before any adapter runs against a real source** | ⭐ **This framework's own repository is clean — checked, not assumed**: zero tracked files carry the real home path, our `graphify-out/` ignore came from `FND-01`'s scaffolding (deliberate, and this is not a source repository), no hooks installed. ⛔ **So the exposure is scoped to the corpus side, which is exactly where R3 bites.** ⚠️ **The rule is written in `graphify.md` and `SK-07` item 9 and is enforced by nothing that runs** — and `OPS-05` checks at **build** time while this happens at **index** time. PO-Integration reverted it and **re-measured after the fix**: the hook fired again, the root file stayed clean |
| W13 | ⛔ **One commit with W7 — ruled, see below.** **Two copies of the personal-data gate that already disagree** — `tests/fixture_checks/personal_data.py` skips dict keys where `SF-08`'s does not (`SF-06` finding 3, ruled **urgent**); and **`imports()` is spelled twice** and should be extracted to `tests/support.py` *"before a third scanner writes a third copy"* (`SF-06` finding 8) | **Developer 2** | ✅ **merged `f569d0e`** | ⭐ **One row because they are one defect**: the project's most-repeated diagnosis is *two copies of a contract*, and here it has produced a copy that **already gives a different answer**. ⚠️ `tests/support.py` exists and has no `imports()` |
| ⛔ **`W26`(PO-18)** — ⚠️ **AMBIGUOUS ID, disambiguated above; the bare `W26` means Ruling 57's row** | ⭐ **`PO-18/2`, RAISED AND CLOSED IN ONE STEP — recorded so it is not re-raised.** `tools/quality/config.py:205` and `:256` use PEP 758 unparenthesized `except OSError, subprocess.SubprocessError:`, which is a `SyntaxError` on ≤3.13. ⚠️ **Reported to me as *"this silently pins the quality floor to 3.14+"*** | PO — ✅ **discharged here** | ✅ **closed** | ⛔ **NOT A DEFECT. `pyproject.toml:19` already declares `requires-python = ">=3.14"`** — ⭐ **so the pin is explicit, not silent, and the syntax is legal in the only interpreter this project supports.** ⚠️ **The word *silently* was the whole finding, and it was the part nobody checked.** ⭐ **Kept as a row because the check cost one `grep` and the finding cost a paragraph** — ⛔ **and because the next reader who spots that syntax will raise it again unless this says they need not.** ⭐ **Standing rule, arriving from a new direction: before reporting a defect, open the file it is about** |

⚠️ **W1 and W2 are one piece of work and should be assigned together.** W1 without
W2 is a fix with no guard; W2 without W1 is a red check with 45 findings.

### ⛔ W26–W27 — SF-10's two structural findings, routed by the CTO at round 18

⭐ **Both are R7 coverage, both were found by the author and offered rather than
assumed, and neither is `SF-10`'s to fix.** ⛔ **`W27` is the more urgent of the
two: it is a live R7 fail-open that has already produced an unreachable catch
arm in `validate`.**

| # | Item | Owner | When | Note |
|---|---|---|---|---|
| W26 | ⛔ **Ruling 57 — W7's reader tell resolves the *name's origin*, not its spelling.** `SF-10` narrowed `DECODES` from `("loads", "load")` to `("loads", "json.load")` to stop flagging `unit/builder/material.py`, which delegates to `archive.document.load` and decodes nothing. ⭐ **The direction is ratified; the spelling is not.** Replace the token match in `tests/test_gate_coverage.py` with an `ast` walk that maps each module's own imports to an origin and asks whether the call resolves to `json.load`/`json.loads` | **Developer 2** | ⛔ **`todo` — NOT STARTED.** `fix/W26-gate-tell` is **byte-identical to `40731e4`**, measured 2026-09-10. ⛔ **next**, ahead of any further gate work | ⚠️ **Measured 2026-09-10, with a control: the shipped narrowing misses two genuine ungated readers** — `from json import load` + bare `load(h)`, and `import json as j` + `j.load(h)` — **both of which the old spelling caught.** ⭐ **The tree is not yet inhabited by either** (`import json`, unaliased, is the only spelling in `src/`), which is why this is next rather than urgent. ⛔ **A false negative in an R7 *coverage* check is worse than a false positive**: the false positive is what produced this ruling; the false negative is silent. ⭐ **Prototyped in the trial merge: the import-resolving tell gets all eight probe shapes right — A–E and H readers, F and G delegation — and finds the same six readers in the tree, so there is no migration** |
| W27 | ⛔ **Ruling 58 — an R7 refusal is never translated into a package's error family.** Three sites translate: `unit/content.py` → `ContentError`, `corpus/placement/identity.py` → `PlacementError`, `corpus/manifest/document.py` → `ManifestError`. Re-raise `PersonalDataLeak` as itself at all three, and **state the exception in each package's `errors.py` contract**, exactly as `archive/errors.py` and `corpus/container/errors.py` already do (*"two exceptions travel through, deliberately"*) | **Developer 2** | ⛔ **`in-review` — `fix/W27-r7-no-translation` @ `655b527`, 2570 / 8** — 12 files, 501 insertions, all three translation sites plus two `errors.py` contracts. ⛔ **urgent — before M1 step 1.5** | ⚠️ **R7 is a HARD FAIL rule failing open**: a family exists so a caller catches one type per item and continues, so a translated leak is logged as *"that unit did not build"* and the walk finishes green. ⛔ **Already load-bearing, measured with a control 2026-09-10:** because the manifest translates, `validate/corpus.py:157`'s `except PersonalDataLeak` arm for the manifest **is unreachable**, and a home path in `corpus.json` is filed under `RULE_MANIFEST` rather than `RULE_PERSONAL_DATA` — *"the catch was correct and the raise never came"*, which is W7's own sentence one layer up. ⭐ **The migration is cheap: zero tests assert the translated message** (`grep -rn 'carries personal data and is refused' tests/` → 0). ⚠️ **`corpus/manifest/document.py`'s docstring says it follows `unit.content._gate` *"exactly"*** — that sentence is how one site became three, and it goes with the fix |

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
| **Closes when** | ⭐ **See *Q18 ruled*, below.** ⛔ This cell said *"a milestone-ordered backlog exists…"*, which is the **reconnaissance task's** close condition, not the track's — ⚠️ **and mistaking one for the other is why Q18 stayed open two rounds** |

### ⛔ Q18 RULED 2026-09-10 — **the track has two finish lines, and that is why it had none**

⚠️ **I carried this for two rounds as *"the track has no definition of done"*, and
that framing is what kept it open.** ⭐ **It is not one missing definition. It is
two definitions that were being asked for as one, and they close at different
milestones, are owned by different people, and are made of different material.**

| | ⭐ **The corpus's finish line** | ⭐ **The exercise's finish line** |
|---|---|---|
| **Asks** | *is this corpus a study site?* | *is this framework extensible?* |
| **Deliverable** | ⭐ **the site** | ⛔ **the findings log** (§12, §11.2) |
| **Lands** | **M4** — the reading floor | **M8** — `QA-04` |
| **Owner** | PO-Integration | ⛔ **the framework side** — §12 forbids the integrator grading their own extensibility |
| **Done when** | ISO opens offline over `file://`, narrated, navigable, read marks recorded, ⛔ **minus what the source genuinely lacks** | the findings log exists, ⛔ **every hand-edit is named as a defect in the onboarding skill**, and the framework pin is accounted for |

⛔ **ISO never enters the execution track**, so its corpus finish line is **M4 and
complete there** — ⭐ **a pass, not a shortfall** (§11.0, C5). ⚠️ **Zero exercises
is a first-class outcome and the finish line must say so in the positive**, or the
next integrator reads a shortfall into a corpus that has none.

#### ⛔ And the ruling that F18/F19/F20 forced: **`studyforge validate` green is a GATE, not a finish line**

⚠️ **`ISO-09`'s acceptance is *"`studyforge validate` green"*. Measured this
round: `NOT valid: 100 findings`, ⛔ and zero of the 100 is a corpus defect.**

⛔ **So the track's finish line currently names a state no corpus can enter, for
reasons §12 forbids the integrator to fix.** ⭐ **That is worse than an open
question, because it reads as a plan** — a task sitting at *"not done"* looks like
work outstanding, ⚠️ **when what it actually records is a framework defect wearing
a corpus's status field.**

⛔ **Ruled: a gate held shut by a framework defect is `Blocked`, not `not done`,
and it is reported as a finding rather than waited on.** ⭐ **`Blocked` already
exists and is already defined** — `../conventions/delivery-flow.md` gives it per
acceptance condition: *name which condition, why, and what will unblock it.*
⚠️ **It was defined for reviews and never applied to the track**, which is a
mechanism this project already owns not reaching one of its two halves.

⛔ **`Blocked` is not passed, and it is never a reason to delete the condition.**
⭐ **`ISO-09` keeps *"validate green"* and records it as Blocked on F18/F19/F20 by
name** — so the finish line stays honest **and** the framework defect stays
visible, ⚠️ **instead of one being traded for the other.**

#### ⭐ What this makes checkable, which is the point of ruling it

⛔ **The track closes when:**

1. ⭐ **The corpus reaches the reading floor** — offline, narrated, navigable, read
   marks — ⛔ **minus what the source genuinely lacks, stated positively.**
2. ⛔ **Every acceptance condition is `passed` or `Blocked`-with-a-named-finding.**
   ⭐ **No condition is silently dropped**, and a Blocked one names what unblocks it.
3. ⛔ **The findings log exists and is non-empty.** ⭐ **A finding count of zero
   fails this** — *an integration that reports none has not been conducted
   honestly*, and that is already the spec's sentence, not a new rule.
4. ⛔ **Every hand-edit is named as a defect in the onboarding skill** (R19).
   ⭐ **That list is what turns *"extensible"* into something with edges.**
5. **The framework pin did not move, or every commit it moved across is accounted
   for.**

⚠️ **Note what is deliberately NOT in the list: *"validate green"*.** ⭐ **It is
condition 2's subject, not condition 1's** — ⛔ **a gate the corpus must pass
through or explain, never the thing being measured.**

⭐ **Carried into `ISO-09`'s acceptance by the PO before it is assigned**, which is
what the question channel is for — ⚠️ **and it is late by exactly the two rounds I
carried it.**

---

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

### ⛔ PO-Integration round 4 — **`studyforge validate` ran, and it says `NOT valid: 100 findings`**

⭐ **The first round that could *run* the framework rather than reason about it**,
because `SF-02` and `SF-25` shipped. ⛔ **Zero of the 100 is a defect in the
corpus** — ⚠️ **all three causes are framework-side, and all three are mine.**

⛔ **They block the track's finish line by construction:** `ISO-09`'s acceptance is
*"`studyforge validate` green"*, ⚠️ **which is currently unreachable for reasons
the integrator is forbidden to fix (§12).** ⭐ **That is the seam working exactly
as designed — and it is also why these cannot wait for M2.**

| # | Finding | ⛔ **Measured** | Owner | Owed before |
|---|---|---|---|---|
| **F18** | ⛔ **`content` has two states and a real repository is mostly a third** | **141 files: 38 included, 3 excluded, ⛔ 100 UNCLASSIFIED.** ⭐ **Only 3 are *material withheld from the reader*** | **CTO** — it is a **schema** change (R9) | ⛔ **`SF-31`**, and before `SK-07` generates a manifest |
| **F19** | ⛔ **a `sibling` build makes its own corpus invalid** | **79 of 79 generated artifacts classify `UNCLASSIFIED`**; `tree` escapes only because `.studyforge` is in `SKIP_DIRS` | **CTO**, then `SF-31` | ⛔ **`SF-31`** — ⭐ **filed *before* it, deliberately** |
| **F20** | ⛔ **the framework mandates a knowledge graph the manifest cannot declare out** | **79 files, 67 content-hash names, and `exclude` refuses globs** — ⛔ **so the list cannot be WRITTEN, not merely not justified.** Plus `source_files()` ignores git, so `validate` and §11.2 disagree **by 83 files** | **CTO** (schema) + **PO** (§11.2) | ⛔ **`SF-31`** |

#### ⛔ Why F18 is the one to rule first, and it is not the biggest number

⚠️ **`README.md` can be *neither* included nor excluded, and that is a proof
rather than an inconvenience.** ⛔ **Include it and it becomes a unit that is its
own table of contents. Exclude it and the `why` must call the sole record of every
address, title and ordinal *"withheld from the reader"*.**

⭐ **X1's asymmetry is what breaks here, and X1 is mine.** ⛔ **I ruled that an
inclusion needs no justification and an exclusion does — on the premise that those
are the only two states.** ⚠️ **A real repository is mostly a third: files that are
neither material nor withheld, because they are not material at all.** ⭐ **The
missing state is *not source material*, and it is not a weakening of X1 — it is
the domain limit X1 was stated without**, which is Ruling 52 arriving against my
own rule rather than somebody else's.

⛔ **`spec §4`'s *"a file matching neither list is unclassified and `validate`
exits 1"* is the clause that has to move**, and it is a schema decision under R9,
so it is the CTO's and not mine. ⚠️ **I am recording the shape, not choosing it.**

⭐ **And the detail worth keeping, because it is the whole finding in one line:**
⛔ **writing the finding took the count from 100 to 101 — the new entry is the file
containing it.** ⚠️ **A rule that classifies its own bug report as unclassified
source material has told you its domain is wrong.**

#### ⚠️ F20's second half is mine, not the CTO's

⛔ **`source_files()` ignores git, so `studyforge validate` and §11.2's acceptance
disagree about what the corpus contains by 83 files.** ⚠️ **Two definitions of
*"the corpus"*, one in code and one in the spec** — ⭐ **which is the two-copies
diagnosis this project has made more than any other, arriving in the one place it
decides whether an acceptance is reachable.** ⛔ **§11.2 is spec text and mine.**

### ⭐ `Q5` is answered and they were still running when I ruled it

⛔ **INGEST — 38 → 55 units, `exercises` stays `false`.** ⭐ **They parse-tested
*both* branches, so the answer costs no round.** ⚠️ **The coordinator is relaying.**

⭐ **It does not change `JS-01`'s Acceptance** — checked rather than assumed:
⛔ **`JS-01` is the *Java* corpus and `Q5` is ISO's fourth container.** ⚠️ **What
they share is the rule, not the corpus**, and the rule was already carried into
`JS-01` as *the reader's obligation, not the file's shape*.

### ⏳ Still mine, carried and named rather than left implied

- ✅ **`Q18` — RULED this round**, after two carried. ⭐ **It had no answer because
  it was two questions: the corpus's finish line (M4, the site) and the exercise's
  (M8, the findings log).** ⛔ **And `validate` green is neither — it is a gate, and
  a gate a framework defect holds shut is `Blocked`, not `not done`.** See above.
- ⭐ **`F24` — corrected.** See the catalogue banner and the four board sites.

---

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

### ⭐ R14's first clean instance, recorded because the counter-evidence was accumulating

⚠️ **This board has spent the session collecting honest evidence *against* R14's
premise** — the index absent from 31 of 33 worktrees, `query` confidently wrong
when phrased as a sentence, a graph with zero doc↔code edges, a coordinator who
hand-assembled briefings because the graph was not there to ask.

⭐ **`SF-10`'s survey is the first clean instance of the graph doing what every
`Context` budget in this plan assumes.** The structure question was **answered
before any file was opened** — 41 line-anchored symbol nodes — and the reading
that followed was **the contract surface only**: one docstring, the signatures,
the banners. ⛔ **No CodeSignal generation code, no second large module.**

⭐ **And it happened on the task where the context discipline was hardest** — a
~70k budget against an 827-line source module. ⚠️ **Recorded deliberately:** a
board that logs only the counter-evidence produces a plan nobody trusts, and the
premise is now **measured in both directions** rather than defended in one.

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
