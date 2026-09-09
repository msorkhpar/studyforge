# Board — live status

**Single source of truth for what is in progress and what is done.** Owned by
the framework Product Owner. Task *definitions* live in the epic documents
(`E00`…`E13`); this file carries only **state**.

**Milestone in flight: M0 — Foundations.**
**Release branch: `release/m0-foundations`.** Developers branch off it, the CTO
reviews against `../conventions/review-rubric.md`, only reviewed work merges
back. Flow: `../conventions/delivery-flow.md`.

*Statuses:* `todo` · `in-progress` · `in-review` · `blocked` · `done`.
*Editing rule:* a status change is one cell. Do not restructure rows; record
events in the **Log**.

⛔ **Standing user decision: nothing is ever pushed to any remote. Everything
stays in local repositories.** Permanent, not a phase. ⚠️ It changed the plan
rather than the workflow: **R18 is amended**, git submodules are **not used in
this project**, `FND-05b` is **cancelled**, and `FND-05a` becomes a tracked pin
file verified against the local checkouts. See **B2** and **G1**, both closed.

---

## M0 — Foundations

> **Milestone closes when:** an agent can pick up any M1 task without inventing
> a layout, hunting for a graph, or building its own fixtures.

**Step 0.1** — FND-01 ✅, FND-02, FND-04 ✅ · **Step 0.2** — FND-03, FND-06, FND-05a

⭐ **Step 0.1 is done bar FND-02, and step 0.2 is fully unblocked.** Three tasks
remain in M0, none of them blocked, and none of them on M1's critical path.

| Task | Title | Owner | Branch | Status | Blocked on | Closes when |
|---|---|---|---|---|---|---|
| FND-01 | Repository scaffolding and quality floor | Developer 1 | *merged* | ✅ `done` | — | **Closed 2026-09-09.** CTO verdict APPROVE after changes. `tools/quality/` (size, mirror, docstrings, style) + `tests/test_quality_floor.py`; `tools/` excluded from packaging; zero runtime dependencies. ✅ **Its one `Blocked` clause is now met** — `FND-03` runs ruff inside the image. ⭐ **No per-condition `Blocked` outcome remains anywhere on this board** |
| FND-02 | Knowledge index | Developer 1 | *merged* | ✅ `done` | — | **Closed 2026-09-09**, APPROVE. Corpus graph 11,107 nodes / 25,566 edges, 217 of 217 documents; framework graph rebuilt at the M0 close. Both graphs build, the `studyforge` one **rebuilt at the M0/M1 boundary**; three representative queries recorded in `../conventions/graphify.md`; rebuild command documented and incremental; `JS/` ignored via `graphify-out/.gitignore` containing `*` and `git status` there clean |
| FND-03 | Development and test container | Developer 2 | *merged* | ✅ `done` | ⚠️ one formatting fix outstanding, Developer 2, **C4** | **Closed 2026-09-09**, APPROVE. ⭐ **FND-01's lint clause moves from Blocked to met** — ruff runs inside the image and the two tests run rather than skip. Full suite runs in the container from a clean checkout with **no host Python**; ⭐ FND-01's two skipped ruff tests **run and pass**, closing its blocked lint clause; suite and quality floor separately invocable; the same commands run on the host; no network needed to run tests |
| FND-04 | Shared contract fixtures | Developer 2 | *merged* | ✅ `done` | — | **Closed 2026-09-09.** CTO verdict APPROVE on every rubric check. 7 corpora, 43 files, 22 tests, re-run green post-merge |
| FND-05a | Workspace, workflow and **the pin file** | *unassigned* | `feat/FND-05a-workspace` | `todo` | — *(unblocked: **B2** ruled)* | A tracked pin file records every component, `studyforge` included; verification **exits 0** when correct and **exits 1 naming the component** both when a recorded commit is absent locally and when a component's `HEAD` moved unrecorded — asserted, not described; the workflow document covers record, verify, advance, the two-commit rule; ⛔ no `.gitmodules` anywhere, and no absolute path in any tracked file |
| FND-06 | Repository personal-data check | *unassigned* | `feat/FND-06-r7-check` | `todo` | — | A fifth entry in `tools/quality`'s `CHECKS`: exits non-zero on a purpose-built violating file, zero on the tree; the sanctioned-directory registry is asserted by a test; ⛔ writes no derived identifier anywhere, proved by a test on the refusal message |
| — | Review rubric + M0 readiness audit | CTO | *merged* | ✅ `done` | — | **Closed 2026-09-09.** `../conventions/review-rubric.md` plus four rulings |
| — | Board + delivery flow | PO-Framework | `chore/po-board-m0-update` | `in-progress` | — | Board reflects the first review round; the ruled task edits are carried into `docs/tasks/` |

**Out of M0:** ⛔ **`FND-05b` is CANCELLED**, not deferred — its whole content was
*add the three components `FND-05a` could not, as submodules*, and submodules are
no longer used. Its residue costs nothing: those three are rows in `FND-05a`'s pin
file, added by the tasks that create them. ⭐ **M0 is five live tasks and the plan
is 84.**

### Open items

**C1 — FND-01, closed, and its blocked clause is closed too.** ⭐ `FND-03` merged
with ruff inside the image, so "lint and format run clean" is **met**, not
deferred, and ⭐ **the board carries no per-condition `Blocked` outcome anywhere.**
The value of having refused to delete the clause is now visible: it was carried
for two rounds by a task that could not satisfy it and closed by the task that
could.

*History, kept because it is the argument:* the clause shipped `Blocked` because
no linter existed on the machines available, and two tests **skipped with a
message naming the extra** rather than passing quietly. ⛔ Deleting it would have
been the easy move and would have left formatting unenforced permanently.

**C4 — FND-03, one formatting fix outstanding, and it is not mine.** The tree is
green on the host — **125 passed, 7 skipped**, floor clean — and **red in the
container** on a formatting check against a file authored before the floor
existed. Routed to Developer 2. ⚠️ **It does not reopen FND-03**, which was
approved; it is the second instance of **C5**.

**B2 — RULED AND CLOSED.** `FND-05a` is unblocked and reshaped; `FND-05b` is
cancelled. ⭐ **All three submodule forms were closed, and the third is the one
that settles it**: absolute local path is an R7 violation in a tracked file;
relative URL resolves against a parent remote that will not exist; and **a real
remote names a commit nobody pushed, so it resolves to nothing *including
here*.** That last one is why this could not be worked around locally rather than
merely inconveniently.

⭐ **The insight that made the answer cheap:** a submodule is exactly two things,
a URL and a commit, and **only the URL half needed pushing.** So the parent keeps
a **tracked pin file verified against the local checkouts** — mechanically
checkable, which is how this project enforces everything else. The two-commit
rule stops being folklore and becomes a command that exits 1 naming the
component.

**G1 — CLOSED, and what was given up is recorded here rather than left in a
merge.** R18 is **amended**, and its claim **shrunk to the true one**:

- ⭐ **Kept:** reproducible **across time on this machine** — which is what R9's
  cross-repository versioning actually needs, and it was the half doing the work.
- ⛔ **Given up, explicitly:** reproducible **across machines**. ⚠️ **This is a
  real reduction in what R18 promised**, not a restatement, and no document in
  the workspace may claim otherwise. If pushing is ever adopted the recorded
  commits are already exactly the data submodules would have wanted — so the
  reduction is recoverable, but it is not currently held.
- **`studyforge` is in the pin file too.** The only reason to exclude it was the
  missing remote, and nothing is being fetched.

⚠️ **Two consequences reach beyond the question that was asked**, which is why
they are on the board and not only in a handoff:

1. **§9's distribution story changes.** The framework is a **sibling checkout at
   a recorded commit**, not a submodule — so ⛔ **`SK-07` must not be written
   against `git submodule add`.** *Never vendored, never copied, never forked* is
   unchanged. This must reach E11 before SK-07 is built.
2. ⚠️ **The silent first-run failure changed shape rather than disappearing.** It
   is no longer an empty submodule directory — nobody clones this. It is **a
   component sitting at a commit the parent never recorded**, which is the same
   surprise with **no symptom at all**. ⭐ That is precisely why verification is a
   command and not a paragraph.

### Sequencing the unassigned tasks

**Order: FND-02 → FND-03 → FND-06 → FND-05a.** ✅ The first two are **done**.
⭐ **Two tasks remain in M0**, neither blocked, neither gating M1.

1. **FND-02 first, startable now.** `graphify` is on PATH and it depends on
   nothing. It is the only M0 task that *repays* the others — R14 is what keeps
   every downstream context budget honest, and `JS/`'s graph (212 documents, 345
   classes) is the largest single saving available to M6. ⚠️ **Its two halves are
   separated in time:** the `JS/` graph is buildable today; the `studyforge`
   graph is rebuilt at the M0/M1 boundary, because one built now would index a
   tree that is about to change completely. ⛔ **Do not ignore `graphify-out/` by
   editing `JS/`'s root ignore file** — R3 forbids that however declared. The
   ignore file goes *inside* the generated directory.
2. **FND-03 second, the moment FND-01 merges.** Docker is reachable; the block is
   content, not environment. It is also where the missing linter is solved.
3. **FND-06 third, alongside FND-03 — and its dependency is now satisfied.**
   ⭐ This is `FND-01`'s own finding 5, and `FND-01` left the seam ready: a fifth
   entry in `tools/quality`'s `CHECKS` tuple. Its consumer already exists on the
   release branch — `FND-04` shipped sanctioned personal-data fixtures, and until
   this lands the rubric's §1e boundary is upheld by a reviewer running greps by
   hand. ⛔ `CLAUDE.md` records that R7 has already been violated once here.
4. **FND-05a last, and now unblocked** — it is a pin file and a verification
   command, not a submodule composition. Nothing in M1 imports the parent
   workspace, so it is still the one M0 task that can slip without stopping
   anybody.

---

## Open questions — owners and deadlines

⭐ **None. The list is empty for the first time.** Every question this board has
raised — Q1 through Q7, X1 and X2 — is ruled, merged, and carried into the tasks
it touches rather than left in a handoff.

⚠️ **That is a state to notice, not to relax into.** ⛔ **An empty list is not
evidence that no contract is unlocated** — R21 exists because five more were
found by *surveying* rather than by waiting to trip over them, and the register
below still has five open rows. The question list being empty means the known
unknowns are answered; R21's register is where the unknown ones are tracked.

**Work items carried out of the rulings:**

| Item | Owner | Closes when |
|---|---|---|
| **FND-04 follow-up, now five steps** — the `disclosure` fixture change, and **step 5: split `tests/test_fixture_consistency.py` along its five named seams** (shape · digests · addresses · media · personal data), then delete `[tool.ruff.format].exclude` **and its one-entry assertion in the same commit** | Developer 2 | The module is under the ceiling unformatted, and the exclusion list is gone rather than shorter |
| **C4** — the container-only formatting failure on a pre-floor file | Developer 2 | Container and host agree |
| **§9 / SK-07: the framework is a sibling checkout at a recorded commit, not a submodule** | PO → E11 | E11 says so before SK-07 is written |

### Resolved — kept, not deleted, because the reasoning is what stops them being re-asked

| # | Ruling | Landed in |
|---|---|---|
| Q6 | ⭐ **The interim stands; the resolution is the split, and it belongs to FND-04's open follow-up.** ⛔ A `Size exception:` would be wrong on principle — the rubric says an exception states *why splitting would be worse*, and splitting is **not** worse here: the module has five natural seams its own handoff already named. ⛔ And a third party cannot author one anyway, because the exception turns on the isolation question, which only somebody who knows the internals can answer. ⭐ **The split is not optional regardless** — the follow-up *adds* to `BLOCK_FIELDS` and `COUNT_KEYS`, so the file goes over 600 with or without the formatter. Formatting is not what pushed it over; it is what pushed it over **first**. The one-entry assertion is kept until the split lands, because an exclusion list that cannot grow without a test failing is what stops it becoming where difficult files go. | E00 follow-up |
| Q7 | **R14 amended in the spec**, so document and authority agree again. ⭐ It gained more than the narrowing: the **measured** qualification is now in the ruling itself — `explain` and `path` hold unconditionally, `query` **only when phrased as distinctive nouns**. ⛔ That belongs in the ruling and not only in the convention, because *confidently wrong is not the same failure as slow*: a budget premised on a slow tool produces late work, one premised on a wrong tool produces **wrong** work and the agent has no signal it did. | spec R14 |
| Q4 | ⭐ **Resolved on the strongest possible ground: the pattern cannot be built.** `SF-08` will never grow a username pattern — to match *"this is the user's username"* the gate must **hold the username**, which is the exact datum R7 forbids it to hold. ⚠️ So this is not a judgement call that could have gone the other way, and it is a sharper answer than X2's: X2 turned on what R7 *governs*, Q4 turns on what a gate can *physically be*. **E07 is unblocked** — do not scrub the account name from package paths, do not refuse it, and do not trim it from generated code, or the Java stops compiling. An email in a lesson comment is still refused. | spec, E02, E07 |
| Q5 | **B2 / G1** — see *Open items*. R18 amended, `FND-05b` cancelled, the pin file replaces the composition. | spec R18, E00 |
| Q1 | **A disclosure is a container block holding blocks**, exactly as a quote does. Flattening keeps the text and destroys the hiding; storing raw tags keeps the hiding and makes the body invisible to the block-count gate — ⭐ both fail oppositely, and C5's lesson is that *shown* and *absent* are not the only states. The archive records the semantics, the renderer owns the markup (R13). **Narration speaks the summary and stops**, and the withheld count is reported, so the omission reads as a decision rather than a bug in the walker. | spec, E02, E04 |
| Q2 | The exercise declaration is **an object inside the practice archive document**, versioned by that document's `raw_api`. | spec §7, E06 |
| Q3 | **Hand-authorable survives, narrowed to two editorial fields of a generated document.** ⭐ Not a hole in a skill: R19 forbids a second source *retyping* what a skill could produce, and a judgement about one's own material is the one thing no skill can produce. | E01 |
| X1 | **`corpus.json` gains `content`** — include globs and exclude entries that each carry their reason. An inclusion needs no justification; **an exclusion is material withheld from the reader**. A file matching neither is unclassified and **refused**, because silence is the failure C2 describes. | spec §4, E01 |
| X2 | ⭐ **Dissolved rather than exempted.** R7 governs identifiers arriving from **the environment the build runs in**, not identifiers that are the **material's subject matter** — so the gate is not a content classifier and ships no payment-card pattern. Checked before ruling: the inherited gate has three patterns and none is a content shape. The manifest-declared exemption is **specified and deliberately not built**. | spec, E02 |

⭐ **X2 is the one to remember, and it is worth being precise about why.** The
board's own constraint was that any exemption must be manifest data, never a
pattern hardcoded for one corpus. That constraint is what made the dissolution
findable: forced to write the exemption generally, the CTO had to say what class
of thing R7 governs — and the answer showed no exemption was needed. ⛔ **No
manifest knob, no card pattern, nothing built.** A rule stated generally
eliminated the feature that a rule stated per-corpus would have required.

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
| **authored overlay** `content.json` — unversioned | **SF-09** (M1 step 1.3) | CTO | ⭐ **Close this one next.** It is the only document a **person** edits, which makes it the likeliest to drift, and R9 does not list it. Either R9 gains it, or R9 says in words why a hand-edited document needs no version — ⛔ but not silence |
| **discovery cache** `.studyforge/site.json` — no version key | **SF-04** (M2 step 2.1) | CTO | R9 refuses an unknown version rather than migrating; a cache with no version cannot be refused, only misread |
| **narration manifest** — no file, no version | **NS-02 / SF-17** (M3) | CTO | Two producers named for one contract is Q3's shape exactly, and Q3 needed a ruling |
| **coverage report** — no file | **EX-05** (M7) | CTO | Not read back, so the cheapest of the five — but R5 is what the report exists to make honest |
| **component consuming contract** `consuming.json` — no version key | **TC-05** (M5), **E13** (M3) | CTO | ⛔ This is the *runtime seam between the two agents*. An unversioned cross-repository contract is precisely what R9 exists for, and **G1's answer only half covers it** — the pin file records *which commit*, and this contract still does not say *which version of the promise* |

⚠️ **`consuming.json` is now the sharper half of what G1 covered.** ⭐ G1's answer
restores *which commit of each component* — that is what `FND-05a`'s pin file
records. It does **not** restore *which version of the promise* each component
made, which is the contract's own job and is still unversioned. ⛔ So a corpus can
now say which components it was built against and still not say what they
guaranteed — and that gap sits on the **runtime seam between the two agents**,
which is the one seam neither can inspect from their own side.

---

## Delivery-process defects

| # | Defect | Owner | Status |
|---|---|---|---|
| C2 | **The rubric's review base resolved against a stale `main`** — ~100 changed files instead of ~14, three tasks' work attributed to one author. | CTO | ✅ **fixed** |
| C3 | **`ruff format` vs R11 on one file** — see resolved **Q6**. | CTO | ✅ **ruled**; the split is Developer 2's |
| C5 | ⚠️ **Parallel-authoring defect, now recurred** — a quality rule merges, and a file authored *before* it lands fails it. Twice: first the line-length check, now the formatter. | PO | open — see below |

⛔ **C2 silently corrupted every review it touched**, which is the worst property
a gate can have: it did not fail, it **passed the wrong thing**. Two details from
the fix are worth keeping, because both generalise:

- ⚠️ **The bug was in five places, not one** — §0's shell preamble *and all four
  Python checkers*, each re-deriving the base internally. ⭐ **A convention that
  repeats its own definition is the defect it polices elsewhere**, which is the
  same argument that put one implementation behind `tools.quality` and one
  definition of the size ceiling behind `FND-01`'s checker.
- ⛔ **The failure mode flatters.** The reviewer sees *more* work, not less — so
  nobody questions it, and there is no moment at which the number looks wrong.
  ⭐ A check that cries wolf gets waved through; a check that under-reports gets
  **believed**. The second is worse and it is the one that had no advocate.

Any review run before the fix is re-run against the corrected base, not assumed
sound.

### C5 — the parallel-authoring defect, and it has now happened twice

⚠️ **The pattern:** a quality rule merges, and a file authored **before** it
landed fails it — through no fault of either author. **First** the line-length
check (`FND-04`, caught at the merge gate). **Now** the formatter (`C4`, red in
the container, green on the host). ⭐ **Two data points is the threshold I said
would decide this**, and it has been reached in a single milestone with four
agents. It will recur every time the floor gains a rule, and M0 is *the milestone
that exists to gain rules*.

**The three options are unchanged; the cheapest now has evidence behind it.**

1. ⭐ **Run the floor across the whole tree when a rule lands, in the same
   commit** — the rule and the tree it makes true arrive together, so no branch in
   flight can be stale against it. **This is the one I recommend**, and both
   incidents would have been prevented by it at the cost of a wider diff on the
   commit that adds a rule.
2. **Re-run the floor at the merge gate rather than at authoring time** — catches
   it, but late, and it charges the cost to whoever merges second, which is
   arbitrary.
3. **Accept it and fix forward** — what has happened twice. ⛔ It is only free
   while the tree is small, and it teaches agents that a red floor is somebody
   else's problem.

⚠️ **Recorded rather than decided: this is the CTO's to rule**, and it is the
kind of thing that is cheap now and expensive at fifty modules.

---

## Next up — M1 step 1.1

> M1 closes when a unit page from the `depth1` fixture opens in a browser with
> styles and highlighting, over `file://`. **M1 is the riskiest milestone** —
> every contract meets every other one for the first time.

| Task | Title | Prerequisite | Startable? |
|---|---|---|---|
| SF-01 | Logical address model | FND-01 ✅, FND-04 ✅ | ⭐ **now** — and it is on the critical path |
| SF-02 | Corpus manifest | FND-01 ✅, FND-04 ✅ | ⭐ **now** — X1 ruled: it gains a `content` block |
| SF-07 | Block vocabulary and Markdown reader | FND-01 ✅, FND-04 ✅ | ⭐ **now** — Q1 ruled: a disclosure is a container block |
| SF-08 | Personal-data gate | FND-01 ✅, FND-04 ✅ | ⭐ **now** — X2 ruled: ⛔ ships **no** content pattern. ⚠️ Q4 is not this task's blocker but E07's |
| SF-11 | Page assets | FND-01 ✅ | ⭐ **now** — the cheapest to start |

- ⭐ **Step 1.1 is already unblocked, and that is the most useful thing on this
  board.** Every task in it declares `Depends on —`; the standing rule is that
  each implicitly depends on **FND-01's layout and FND-04's fixtures**, and both
  are merged. ⛔ **M0's three remaining tasks gate nothing in M1** — FND-02 saves
  context, FND-03 closes a blocked clause, FND-05a pins a workspace nothing
  imports. Waiting for the milestone label rather than the prerequisite would
  idle four developers against a formality.
- ⭐ **The risk this board recorded on 2026-09-09 — the fixtures encoding
  contracts nobody had written — is retired**; see the Log.
- ⭐ **SF-01 is on the project critical path** (FND-01 → SF-01 → SF-03 → SF-31 →
  SK-02 → …). Assign it the day M0 closes; do not let it queue behind SF-02.
- ⭐ **All five questions that held step 1.1 are ruled and merged.** ⛔ **Step 1.1
  has no open blocker of any kind** — prerequisites met, questions answered,
  rulings carried into E01, E02, E04 and E06 rather than left in a handoff. This
  is the moment to assign it; the constraint is now developers, not decisions.
- ⚠️ **One M1 task acquired a debt rather than a blocker:** `SF-09` (step 1.3)
  owes the authored overlay's version under R21 before it builds. It is the row
  the CTO singled out to close next, and step 1.3 is two steps away — comfortable,
  but not indefinite.
- **`SF-31` gained an acceptance clause**: it commits `plan` output for both
  fixtures as the golden. That is the agreed close on the largest gap `FND-04`
  deliberately left open — `FND-04` could not write a golden for output nobody
  has designed. `handoffs/FND-04.md` names the rest and who owes each.

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

## Context budgets and the knowledge index

⚠️ **`FND-02`'s honest verdict changes a planning assumption, and it needs an
answer rather than a status line.** R14's premise — *ask the graph before
exploring* — holds unconditionally for `explain` and `path`. For `query` it holds
**only when the question is phrased as distinctive nouns**; asked as an English
sentence it returns unrelated material *with the same confidence as a right
answer*. Every task's **Context** budget in this plan assumes the graph replaces
exploration.

**Do the budgets need revisiting? Yes — but not the ones you would expect, and
not by re-pricing all 85.**

⭐ **The phrasing defect is the smaller problem, and it is already mitigated.**
`FND-02` wrote it up as *What it answers badly* in `graphify.md`, with the three
commands and what each is good for. A documented failure mode that an agent reads
before its first query costs a sentence, not a budget. ⛔ **The real exposure is
two other findings in the same handoff**, and neither is about phrasing:

1. ⛔ **A graph built by running graphify alone has *zero* doc↔code edges.** The
   lesson→class link that makes `JS/`'s graph worth 212 documents of reading
   exists **only because `FND-02` built it by hand** — measured before the fix:
   13,583 code↔code, 767 doc↔doc, **0 doc↔code**. It is structural, not a slip:
   code is extracted by AST, prose by LLM, and no extractor ever sees a lesson
   and its class together. ⭐ So the budget saving R14 promises is **not a
   property of the tool** — it is a property of a graph somebody bridged.
2. **~4% of edges are dangling**, so *absence of a connection is not proof of
   absence*. A task that concludes "nothing calls this" from a query has
   concluded nothing.

**Which tasks are most exposed, in order.**

| Exposure | Tasks | Why |
|---|---|---|
| ⛔ **Highest** | **QA-04** (M8, the second source), and **SK-07** | A new corpus arrives with **no graph at all** — and `SK-07` does not generate one, which is `FND-02`'s finding 2 and a hole in the skill under R19. M8's whole measurement is what an integrator had to do by hand; ⚠️ "build and bridge a graph" would be a large, uncounted item on that list |
| ⛔ **High** | **SF-19a** | Named on this board as *"a serial bottleneck wearing a milestone's name"* — one task carrying a very large share of the port surface, unsplittable. It is discovery-shaped: you do not know the name of the thing you are looking for, which is exactly `query`'s weak case |
| ⚠️ **Medium** | **SK-01, SK-02, SK-05, SK-08** | Skills answer *"what does the framework do about X"* — questions, not lookups. Same weak case, smaller surface |
| ⭐ **Reduced, not raised** | **JS-03, JS-04, E08** | The opposite direction: `FND-02` pre-built the lesson→class link these were going to re-derive. `path` returns it in one hop for **162 of 166** lessons, and the four exceptions are enumerated. These budgets are now *safer* than planned |

**What I recommend, and it is three cheap things rather than a re-plan.**

1. ⛔ **Do not re-price all 85 budgets.** Most tasks are lookup-shaped and
   unaffected, and a plan-wide re-estimate would cost more than the error.
2. ⭐ **Give `SK-07` the graph** — build it, bridge it, and write the R3-safe
   ignore recipe `FND-02` already proved. That converts the highest exposure into
   a generated artifact and closes an R19 hole in the same edit. This is the one I
   would act on first.
3. **Add explicit headroom to SF-19a and the four skills tasks**, and let the CTO
   agree the number. They are five tasks, not eighty-five.

⚠️ **And one plan-wide defect worth naming once.** `FND-02` reports its own
~20k budget was optimistic *by roughly an order of magnitude* — ⭐ **not for
reading, but for doing.** The read list was small and correct; the task was a
12-chunk parallel extraction over 217 documents, twice. The **Context** field in
`README.md` is defined as *"the files to read, and a rough budget"*, and those are
two different quantities wearing one number. ⛔ **Any task whose deliverable is a
*computation* rather than a *change* is mispriced by construction** — `FND-02`,
`SF-17`'s synthesis run, `EX-00`'s spike, `EX-04`'s emission. Recommend the field
say plainly that the number prices reading, and that work is estimated separately;
that is a one-line fix to a definition rather than 85 re-estimates.

---

## Log

| Date | Change |
|---|---|
| 2026-09-09 | Board opened. M0 in flight: FND-01 and FND-04 assigned, FND-02/03 sequenced, FND-05 blocked. |
| 2026-09-09 | **First review round closed.** Board, delivery flow, the CTO's rubric and readiness audit, and **FND-04 (APPROVE)** merged to `release/m0-foundations`; fixture suite re-run green post-merge, 22 passed. |
| 2026-09-09 | **FND-04 → done.** 7 corpora, 43 files, 22 tests. |
| 2026-09-09 | **FND-01 → done.** Changes requested (C1, the `.gitignore` negation regression test) landed in both directions and the task merged, CTO verdict APPROVE after changes. ⚠️ Its lint clause merged as **Blocked**, not passed — `FND-03` closes it. |
| 2026-09-09 | ⭐ **Risk 3 retired.** This board argued FND-04 was M0's real critical path because its fixtures encode contracts nobody has written, and staffed it as a pair for that reason. The CTO checked all thirteen of its assumptions against CodeSignal HEAD rather than accepting them, and confirmed the three with the widest blast radius — the archive document key set, `quote` holding **blocks** rather than text, and `video` being both a block type and a document record. ⭐ **The drift was checked for and not found.** Recorded because the mitigation worked and the mechanism is reusable: a fixture task's assumptions get *counted*, not reviewed. |
| 2026-09-09 | **FND-05 split** into `FND-05a` (M0) and `FND-05b` (M5), per CTO ruling 2. The blocking premise on this board was **corrected**: four of five sibling repos have remotes; only `studyforge` does not. |
| 2026-09-09 | **FND-06 added** to M0 step 0.2 — R7 enforced by the build. Number assigned by the PO on the CTO's proposal. |
| 2026-09-09 | **M0 re-cut into two steps.** "All parallel" was false: FND-03 and FND-06 both depend on FND-01. |
| 2026-09-09 | **Task edits carried:** FND-04's golden-files clause struck and re-homed in SF-31's acceptance; FND-01's ignore wording corrected so it cannot be read as ignoring a corpus's committed narration; FND-02's acceptance names the M0-close rebuild and the R3-safe ignore file; README task count 83 → 85, M0 5 → 6, M5 12 → 13, and its reading list corrected from R1–R19 to R1–R20. |
| 2026-09-09 | **Three open questions given owners and deadlines** (Q1–Q3), and two ISO questions routed to the tasks that must answer them (X1 → SF-02, X2 → SF-06/SF-08). |
| 2026-09-09 | **ISO confirmed complete at the reading floor** — no graders, no exercises, `permitted_edits` empty. It never enters the execution track and is a real empty-declaration case for OPS-05. |
| 2026-09-09 | ⛔ **Standing user decision: nothing is ever pushed to any remote**, permanently. Recorded as a **plan change**, not a workflow note: `FND-05a`'s composition half loses its only legal form (**B2**) and R18's version pin loses its mechanism (**G1**). |
| 2026-09-09 | **B1 replaced by B2.** The old unblocking condition named an account action — an owner creating a remote for `studyforge` — that will now never happen. ⛔ A condition phrased as "wait for a remote" is a task that waits forever. |
| 2026-09-09 | **R21 adopted by explicit user decision** — *a contract is located before it is described*. ⭐ The CTO **surveyed rather than assumed** and found five more unlocated contracts already in the spec; they are now a §2 register and five board items with owners. The overlay's row closes next: it is the only document a person edits, and R9 does not list it. |
| 2026-09-09 | **Q1, Q2, Q3, X1, X2 all ruled and merged**, and moved to *Resolved* rather than deleted. ⛔ **Step 1.1 now has no open blocker of any kind.** |
| 2026-09-09 | ⭐ **X2 dissolved rather than exempted.** R7 governs identifiers arriving from the build environment, not identifiers that are the material's subject matter. No manifest knob, no card pattern, nothing built — the mechanism is specified and deliberately unbuilt. Recorded because the board's own constraint (*any exemption is manifest data, never a per-corpus pattern*) is what forced the general statement that showed no exemption was needed. |
| 2026-09-09 | **FND-02 and FND-03 complete, in review with the CTO.** FND-03 closes FND-01's blocked lint clause for real — ruff runs inside the image and the two tests **run rather than skip**. |
| 2026-09-09 | **Q4 opened and it blocks E07**: the Java corpus carries its owner's account name in 345 package paths. X2's shape, ⚠️ likely not X2's answer — an account name identifies a real person *and* is the material. |
| 2026-09-09 | **Q6 opened** — `ruff format` explodes FND-04's test module past R11's 600-line ceiling. Interim: formatter-excluded, still linted, still floored, exclusion list asserted at exactly one entry. |
| 2026-09-09 | **C2 recorded** — the rubric's `$BASE` resolved against a stale `main`, so reviews showed ~100 files instead of ~14 and misattributed three tasks to one author. ⛔ It did not fail; it passed the wrong thing. Reviews run before the fix should be re-run against the corrected base. |
| 2026-09-09 | **Q7 opened** — R14's text in the spec still says "every repository" while `graphify.md` was narrowed to the working set. ⚠️ A document and its authority disagree in writing. |
| 2026-09-09 | ⭐ **Context-budget judgement recorded** on FND-02's verdict. Short answer: the `query` phrasing defect is the smaller problem and is already documented; the real exposure is that a graph built by running graphify alone has **zero doc↔code edges**. Five tasks need headroom, not eighty-five. |
| 2026-09-09 | `CLAUDE.md` task count corrected 83 → 85. |
| 2026-09-09 | **Merge conflict on `FND-05a` resolved by the PO**, the CTO's ruling taken as substance. ⭐ **Neither author's contribution dropped silently**: the PO's stop sign is superseded and removed — a blocked notice on a startable task stops the wrong person — and the epic's revision note records why. The argument behind it survives: an agent reads the epic and not always the board. |
| 2026-09-09 | ⭐ **B2 ruled and closed.** All three submodule forms are closed, and the third settles it — **a real remote names a commit nobody pushed, so it resolves to nothing including here.** `FND-05a` becomes a pin file plus a verification command; **`FND-05b` cancelled outright**, not deferred. Plan is **84 tasks**, M0 is **five**. |
| 2026-09-09 | ⭐ **G1 closed, and the reduction recorded.** A submodule is a URL and a commit, and only the URL half needed pushing — so the pin survives as a tracked file verified locally. ⛔ **R18's claim shrinks to the true one:** reproducible **across time on this machine**, explicitly **not across machines**. That is a real loss, recoverable if pushing is ever adopted, not currently held. |
| 2026-09-09 | **Two consequences beyond the question asked:** §9's distribution story changes — the framework is a **sibling checkout at a recorded commit**, so ⛔ SK-07 must not be written against `git submodule add` — and the silent first-run failure **changed shape rather than disappearing**: a component at a commit the parent never recorded, with **no symptom at all**. |
| 2026-09-09 | **FND-02 → done** (APPROVE): 11,107 nodes, 217 of 217 documents. **FND-03 → done** (APPROVE). ⭐ **FND-01's lint clause moves from Blocked to met** — ruff runs in the image and the two tests run rather than skip. **No per-condition `Blocked` outcome remains on this board.** |
| 2026-09-09 | ⭐ **Q4 resolved, E07 unblocked — on the ground that the pattern cannot be built.** To match "this is the user's username" the gate must hold the username, the exact datum R7 forbids it to hold. Sharper than X2: X2 turned on what R7 *governs*, Q4 on what a gate can physically *be*. |
| 2026-09-09 | **Q6 and Q7 ruled.** ⭐ **The open-question list is empty for the first time** — Q1–Q7, X1, X2 all closed. ⚠️ Not evidence that no contract is unlocated: R21's register still carries five open rows, and those were found by surveying rather than by tripping over them. |
| 2026-09-09 | ⚠️ **C5 recorded — the parallel-authoring defect has recurred.** A rule merges; a file authored before it fails it. Line-length, then the formatter. ⭐ Two data points in one milestone with four agents, and M0 is the milestone that exists to gain rules. Recommendation: run the floor across the tree in the same commit that adds a rule. **The CTO's to decide.** |
| 2026-09-09 | **C2 fixed, and two details kept:** the bug was in **five** places — the shell preamble and all four Python checkers, each re-deriving the base — and ⛔ **the failure mode flatters**, showing more work rather than less, so nobody questions it. ⭐ A check that cries wolf gets waved through; one that under-reports gets believed. |
