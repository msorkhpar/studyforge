# Board — live status

**Single source of truth for what is in progress and what is done.** Owned by
the framework Product Owner. Task *definitions* live in the epic documents
(`E00`…`E13`); this file carries only **state**.

✅ **M0 COMPLETE. M1 steps 1.1 and 1.2 COMPLETE.** **In flight: M1 step 1.3.**
Release tip pinned at **1512 passed / 46 skipped**, floor clean.
**Release branch: `release/m1-one-page`**, cut from `release/m0-foundations`.
Developers branch off it, the CTO reviews against
`../conventions/review-rubric.md`, only reviewed work merges back. Flow:
`../conventions/delivery-flow.md`.

⚠️ **M1 is fifteen tasks and `README.md` calls it the riskiest milestone** —
where every contract meets every other one for the first time. ⛔ **Two things
follow, and they shape everything below.** Ordering *inside* a step now matters,
because a contract that merges first becomes the shape the next fourteen copy.
And ⭐ **the board must carry more reasoning at fifteen tasks, not less** — the
entries that paid for themselves in M0 were the ones recording *why* (X2's
dissolution, G1's recorded loss, the flattering review base), because a recorded
*why* is what stops a question being re-asked by the next of fifteen agents.

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

✅ **CLOSED 2026-09-09.** Green in the container: **124 passed, 8 skipped**, floor
clean. Four of six tasks done; **FND-05a** and **FND-06** carry into M1 as
residue — see *M0 residue* below. ⭐ Neither gates any M1 task, which is why the
milestone closes rather than waits.

| Task | Title | Owner | Branch | Status | Blocked on | Closes when |
|---|---|---|---|---|---|---|
| FND-01 | Repository scaffolding and quality floor | Developer 1 | *merged* | ✅ `done` | — | **Closed 2026-09-09.** CTO verdict APPROVE after changes. `tools/quality/` (size, mirror, docstrings, style) + `tests/test_quality_floor.py`; `tools/` excluded from packaging; zero runtime dependencies. ✅ **Its one `Blocked` clause is now met** — `FND-03` runs ruff inside the image. ⭐ **No per-condition `Blocked` outcome remains anywhere on this board** |
| FND-02 | Knowledge index | Developer 1 | *merged* | ✅ `done` — ⚠️ **but see the index section: its framework-graph clause was true in one worktree and false in the repository, and `FND-07` is the mechanism** | — | **Closed 2026-09-09**, APPROVE. Corpus graph 11,107 nodes / 25,566 edges, 217 of 217 documents. Both graphs build, the `studyforge` one **rebuilt at the M0/M1 boundary**; three representative queries recorded in `../conventions/graphify.md`; rebuild command documented and incremental; `JS/` ignored via `graphify-out/.gitignore` containing `*` and `git status` there clean |
| FND-03 | Development and test container | Developer 2 | *merged* | ✅ `done` | — *(**C4** closed)* | **Closed 2026-09-09**, APPROVE. ⭐ **FND-01's lint clause moves from Blocked to met** — ruff runs inside the image and the two tests run rather than skip. Full suite runs in the container from a clean checkout with **no host Python**; ⭐ FND-01's two skipped ruff tests **run and pass**, closing its blocked lint clause; suite and quality floor separately invocable; the same commands run on the host; no network needed to run tests |
| FND-04 | Shared contract fixtures | Developer 2 | *merged* | ✅ `done` | — | **Closed 2026-09-09.** CTO verdict APPROVE on every rubric check. 7 corpora, 43 files, 22 tests, re-run green post-merge |
| FND-05a | Workspace, workflow and **the pin file** | *unassigned* — M0 residue | `feat/FND-05a-workspace` | `todo` | — *(unblocked: **B2** ruled)* | A tracked pin file records every component, `studyforge` included; verification **exits 0** when correct and **exits 1 naming the component** both when a recorded commit is absent locally and when a component's `HEAD` moved unrecorded — asserted, not described; the workflow document covers record, verify, advance, the two-commit rule; ⛔ no `.gitmodules` anywhere, and no absolute path in any tracked file |
| FND-06 | Repository personal-data check | Developer 1 | *merged* | ✅ `done` — ⚠️ one follow-up: the **exception text** is unenforced | — | A fifth entry in `tools/quality`'s `CHECKS`: exits non-zero on a purpose-built violating file, zero on the tree; the sanctioned-directory registry is asserted by a test; ⛔ writes no derived identifier anywhere, proved by a test on the refusal message |
| — | Review rubric + M0 readiness audit | CTO | *merged* | ✅ `done` | — | **Closed 2026-09-09.** `../conventions/review-rubric.md` plus four rulings |
| — | Board, delivery flow, rulings carried | PO-Framework | *merged* | ✅ `done` | — | Three rounds; the conflict on FND-05a resolved with both authors' contributions recorded |

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

**C4 — CLOSED.** The container-only formatting failure was `FND-02`'s test
module, authored before the formatter existed. Fixed through `FND-03`'s own
wrapper rather than by hand — ⭐ **and the `Permission denied` seen at the merge
gate was `FND-03`'s hardening working as designed**, the unprivileged-uid test
owning nothing; ⛔ nothing about the container was loosened to get past it, which
is exactly the right instinct. Formatting only, checked rather than asserted: the
parsed AST is identical before and after. Container **124 passed, 8 skipped**,
both ruff gates passing by name. ⚠️ It never reopened `FND-03`, which was
approved — but it **is** the third instance of **C5**.

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
below still has **four** open rows. The question list being empty means the known
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
| C5 | ⛔ **Parallel-authoring defect — three instances, one milestone.** A quality rule merges; a file authored *before* it lands fails it. FND-04/line-length, FND-03's container/formatter, FND-02/formatter. | CTO to rule | ⛔ **open, and no longer a judgement call** |

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

### C5 — ✅ RULED: options 1 **and** 2. Option 3 refused.

⭐ **My recommendation of option 1 was right and was not enough, and the CTO's
correction is the more interesting half.** They are not alternatives: **option 1
prevents, option 2 detects, and only option 2 catches the rule nobody has thought
of yet.**

**The three instances**, kept because they are the evidence: `FND-04`'s fixture
module against the line-length check; `FND-03`'s container run against the
formatter; `FND-02`'s test module against the formatter. All three authored green
on branches where the tool did not yet exist.

**Option 1 — mostly already done.** Its schedulable half (*the floor exists
before parallel authoring starts*) ⭐ **is already true**: M0 is complete, ruff is
configured, `tools/quality` is present, the container builds. M0 was the one
window where the floor was built alongside its first users and ⛔ **that window is
closed — there is no wave-0 prerequisite left to schedule.** Its residue is a
standing rule, now in `FND-06`:

> ⛔ **A commit that adds or tightens a check brings the whole tree into
> compliance in the same commit**, and the check is never merged in a state where
> a tracked file fails it. ⭐ **No open branch is expected to fix a rule it never
> saw.**

**Option 2 — the real fix, and it was the rubric's defect.** ⛔ The gate reviewed
`$BASE...HEAD` — *the branch's own changes* — so all three branches were
correctly green and **the rubric was asking the wrong question.** ⭐ **The diff is
the branch's; the verdict must be the merge's.** Reviewing the branch asks *is
this change good?*; a merge gate asks *is the result good?* — and those come apart
**precisely when two parallel tasks are each correct alone**, which is the only
situation C5 occurs in. §0a now stands up a trial-merge worktree and §4b runs the
suite and the floor inside it.

⚠️ **And the reason this is the half that matters for M1:** option 1 protects
against *style* rules, because style is what we happened to add. The trial merge
sees **any** rule, fixture, contract or checker introduced on one branch and
invisible to every branch cut before it. ⛔ **M1's fifteen tasks author contracts
and fixtures — the next collision probably is not a line length.**

**Option 3 refused.** ⭐ A known cost paid fifteen times is not a known cost; it
is a policy of paying it.

### ⭐ The meta-finding, which the CTO ruled is worth more than C5

My framing was adopted as the ruling rather than softened: **a recorded prediction
that was not acted on and then came true twice more is the most expensive kind of
finding this project produces.** `FND-04`'s finding 10 named the shape, the three
options and the cheapest one. It was filed in the right place, in the right
format, and read.

⛔ **The protocol said to write findings down. It never said anyone had to rule on
one.** ⚠️ That is a hole in the mechanism, not a failure of routing — and blaming
the routing would have left the mechanism intact and guaranteed a repeat. Fixed
on both sides:

- **Author side** (`agent-protocol.md`): findings are marked **`[local]`** or
  **`[structural]`**, and every `[structural]` one is **ruled, scheduled, or
  explicitly accepted before the next wave begins.** ⛔ *"Noted"* is not one of the
  three. The test is one question: *would this happen again to somebody else?*
- **Reviewer side** (`review-rubric.md` §8a): ⭐ **the reviewer routes them, in
  the review** — the reviewer is the last person who reads a handoff while
  anything can still be done about it. ⚠️ And a reviewer who spots an *unmarked*
  structural finding marks it: the author is describing their own scope and is the
  worst-placed person to see that something recurs elsewhere.

⭐ **`grep -rn '\[structural\]' docs/tasks/handoffs/` is the triage list before a
wave**, and running it is now part of opening one. **This PO owns that sweep.**

### The back-triage — ✅ complete, and what it found

⛔ **The first sweep came back empty, and that was a hole rather than a clean
bill.** The marker landed after 23 findings had already been filed — ⚠️ including
`FND-04`'s finding 10, *the one that cost this project two round trips.* ⭐ The
mechanism built to stop unacted-on findings would have missed the finding that
motivated it.

✅ **All 23 are now marked and dispositioned** — ruled, applied, scheduled, or
explicitly accepted with the cost named. ⛔ **"Noted" appears nowhere**, which is
the whole point of the exercise.

⚠️ **Three remain open, and two of them were not on this board.** That is the
argument for the sweep in one line: ⭐ **both untracked ones concern tasks that
have not run yet**, so they were still cheap when found.

1. **The authored overlay's version** — already tracked; R21 register row 1, owed
   before `SF-09` at step 1.3.
2. ⛔ **Port-size debt** (`FND-04` #7). CodeSignal's `markdown.py` is 678 lines
   and `unitdoc.py` 827, against R11's 400. ⭐ `SF-07` handled it correctly and
   shipped a package — but `SF-12` and `SF-19a` have not run, and R11 is explicit
   that the large modules arrive **as packages or not at all**. Routed to both
   tasks rather than left as a general warning.
3. ⛔ **~~The repository-wide R7 sweep is not clean today~~ — WITHDRAWN.**
   ⚠️ **I acted on this finding without re-running it, and it had stopped being
   true.** Re-measured on the merged tip:

   | What | Result |
   |---|---|
   | `tools.quality`'s implemented check, whole tree | ⭐ **0 findings** |
   | Rubric's **current** §1a patterns, over `docs/` + `CLAUDE.md` | ⭐ **0 hits** |
   | Rubric's **superseded** §1a patterns, same scope | ⛔ **24 hits — every one a false positive** |

   ⭐ **The two-character minimum local part kills `n@router.get` exactly** — its
   local part is one character — with the `.local` trailing guard and the dropped
   `$HOME`/`~/` alternatives accounting for the rest. So **the allow-list is a
   mechanism for a hit that no longer fires**, and it is **specified and
   deliberately not built** — the same disposition X2 got, for the same reason,
   and this project has now refused two mechanisms by checking whether the
   problem was still there.

   ⭐ **The correction is a better precedent than my decision was.** An allow-list
   would have recorded **24 instances of a defect in the pattern as 24 facts about
   the tree.** ⛔ **Fix the class; list the instance only when the class is right
   and the instance is genuinely exceptional.** The reasoning that survives — no
   `docs/` exclusion, prose is not a §1e fixture, a short failing list beats a
   silent exclusion — is kept in `FND-06` against the day a real hit arrives.

---

## M1 step 1.1 — the assignment

> M1 closes when a unit page from the `depth1` fixture opens in a browser with
> styles and highlighting, over `file://`.

| Task | Title | Owner | Branch | Status | Blocked on | Closes when |
|---|---|---|---|---|---|---|
| FND-04-fu 1–4 | The `disclosure` fixture, in the ruled shape | Developer 2 | *merged* | ✅ `done` | — | A fixture carries a `disclosure` container block; one block replaced, one added, two dictionaries extended, one digest recomputed. ⛔ **On SF-07's critical path** |
| FND-04-fu 5 | Split `test_fixture_consistency.py` at its five seams | Developer 2 | *merged* | ✅ `done` — ⭐ the formatter interim is **over**: exclusion and its assertion deleted together | — | The module is split along shape · digests · addresses · media · personal data and is under the ceiling **unformatted**; ⛔ `[tool.ruff.format].exclude` **and** its one-entry assertion deleted in the **same commit**, or the guard outlives what it guarded. Lands before M1 closes |
| SF-01 | Logical address model | Developer 2 | *merged* | ✅ `done` | — | Round-trips every §4 address at depths 1–4; a title where a slug is required raises; two slugs differing only by a leading digit yield different identifiers; wrong arity for a declared depth rejected; ⛔ no filesystem import in the package |
| SF-02 | Corpus manifest | Developer 2 | *merged* | ✅ `done` | — | Accepts all four §1 shapes incl. two depth-1; refuses unknown `corpus_api`/`placement`/`media.commit`, empty `levels`/`variants`, a forbidden `permitted_edits` target, an `exclude` with no `why`; ⛔ a file matching neither list is **named and refused**; absent `media` asserted as committed-with-defaults; no module derives runnability from a variant name |
| SF-07 | Block vocabulary and Markdown reader | Developer 1 | *merged* | ✅ `done` | — | CodeSignal's Markdown tests pass unchanged; `disclosure` is a **container block holding blocks**; fence-awareness proved on `depth1` u3 `lesson-2`; parses all 166 Java sub-READMEs **or names every file and construct that fails**; ⛔ no unit yields fewer blocks than its independently-counted structure implies |
| SF-08 | Personal-data gate | Developer 1 | `feat/SF-08-scrub` | `in-progress` | — | Home path refused at the archive boundary; build output scrubbed before a stream; ⛔ **three patterns, no content shape, no username pattern**; a document of 16-digit card-shaped strings **passes**; material that only resembles personal data after escaping is **not** refused; every gate reads decoded strings — asserted |
| SF-11 | Page assets | Developer 2 | `feat/SF-11-assets` | `in-progress` | — | Highlight tests pass incl. no token combination taking the comment colour without being a comment; a page opens with only local requests; every palette token defined in **both** themes and clearing contrast; vendored bundles carry licences, unedited |

| SF-33 | Contract version guard | *first free slot* | `feat/SF-33-version` | `todo` | — | ⛔ A JSON `true` is **refused** where `1` is supported — asserted, with `1.0` and `"1"`; refusal is a raise, never a migration; `SF-02` imports it; ⛔ a test fails if a second version check appears. **Before SF-06** |

### The lanes

⭐ **The organising decision: a collision pair goes to one developer, never
split across two.** Two pairs in these five share a surface, and M0's evidence
is that a shared surface split across agents is where the cost lands — not in
the code, in the reconciliation.

✅ **It held. Four-fifths of the step is merged with no reconciliation cost and no
collision.**

⭐ **And the lanes were swapped between developers, which is evidence *for* the
rule rather than against it.** Lane A went to Developer 2 and lane B to Developer
1, because Developer 1 was mid-`FND-06` and `SF-01` is the exemplar. ⚠️ **The
pairs stayed intact, which is the only thing the rule protects** — *which*
developer owns a pair is a scheduling question and belongs to whoever is
dispatching. ⛔ A rule that also fixed the assignee would have blocked a sensible
swap for no benefit, and the table below records the swap rather than pretending
the original allocation happened.

| Lane | Developer | Order | Reasoning |
|---|---|---|---|
| **A — contracts** | Developer 1 | **SF-01** → **SF-02** | ⚠️ **They share the depth/`levels` concept.** SF-01 rejects *"a key of the wrong arity for a declared depth"*; SF-02 owns `levels`, which *is* the declaration. Split across agents, the two disagree about where arity is validated and the fixtures — which already encode an answer — arbitrate after the fact. One agent, and the question never arises |
| **B — archive** | Developer 2 | **FND-04-fu steps 1–4** → **SF-07** → **SF-08** | ⚠️ **They share the walker.** SF-07 defines the block vocabulary; SF-08's gate walks it and its acceptance turns on *"every gate reads the decoded strings, never a rendered form"* — a statement about traversing SF-07's blocks. Both live in `archive/`. ⭐ **And the `disclosure` ruling lands in both**: SF-07 stores `summary` as content, SF-08 gates it. Two agents would rule it twice |
| **residue** | first free slot | **FND-06** → **SF-11** | Both isolated, neither shares a file with anything above |
| **slack** | Developer 2, alongside | **FND-04-fu step 5** — the module split | ⛔ **Decoupled from lane B on the CTO's ruling, and my earlier gate was wrong — see below.** Lands before M1 closes |

⛔ **SF-11 is deliberately last, not first, despite being the easiest.** It is a
copy rather than a repair — R13 was already satisfied upstream — its consumer is
`SF-12` at step 1.5, and nothing in steps 1.1–1.4 waits on it. ⭐ Easy work with
no dependents is exactly what should absorb slack rather than consume a lane.

### Why Developer 2 owns the FND-04 follow-up — and where I got it wrong

⭐ **Developer 2 is the only correct owner, and that part stands.** The CTO's own
argument against authoring a `Size exception:` was that the exception turns on the
isolation question, which **only somebody who knows the module's internals can
answer** — and Developer 2 authored it and named its five seams (shape · digests ·
addresses · media · personal data) in their own handoff. ⛔ Handing the split to a
third party asks someone to answer a question they cannot.

**Steps 1–4 gate `SF-07`, and that part stands too.** ⛔ `SF-07` implements the
`disclosure` block and **cannot demonstrate its own acceptance without a fixture
carrying one**. It is small — one block replaced, one added, two dictionaries
extended, one digest recomputed — and it is on a critical-path task's critical
path, so it is neither optional nor later.

⛔ **Where I was wrong: I gated `SF-07`'s commit on step 5, the module split.** My
reasoning was that `SF-07` adds a count key to a file already at the ceiling. ⭐
**It does not, and the error is worth naming precisely because it is the kind that
sounds right:** I conflated *606 lines formatted* with *554 lines unformatted*.
The formatted figure is what the exclusion already contains; the growth from the
`disclosure` keys lands in **steps 1–4**, not in `SF-07`, and 554-plus-a-few is
not 600. **The CTO overruled it and the correction improves the plan** — coupling
them would have put a critical-path task behind a refactor for no benefit.

⭐ **So the follow-up splits at the seam that matters:** steps 1–4 are on the
critical path; step 5 rides alongside and lands before M1 closes. ⚠️ **Whoever
takes steps 1–4 should not take step 5 in the same commit.** They are two
different things with two different deadlines, and the interim is safe meanwhile
— the module is not currently failing, and the exclusion list is held to exactly
one named entry by an assertion.

### What must merge before what

| Gate | Rule |
|---|---|
| ⭐ **SF-01 merges first, before anything else in M1** | It is the **exemplar**, not merely first on the critical path (FND-01 → SF-01 → SF-03 → SF-31 → SK-02 → …). It is the first framework contract, and the docstring shape, the raise-vs-return convention and the package layout it establishes are what the next fourteen tasks copy. ⚠️ **Review it as a precedent** — a convention corrected in task 1 costs one diff; corrected in task 8 it costs eight |
| **SF-02 may *start* when SF-01 is in review** | Same developer, same head, and the arity decision is settled by then. ⛔ It must not *merge* before SF-01 |
| ⛔ **FND-04-fu steps 1–4 land before or with SF-07** | The fixture is SF-07's acceptance input; SF-07 cannot demonstrate the `disclosure` ruling without one |
| **FND-04-fu step 5 rides alongside, before M1 closes** | ⛔ **No gate on SF-07** — my earlier one was wrong (see above). ⚠️ Delete the formatter exclusion and its one-entry assertion in the **same commit** as the split, or the guard outlives what it guarded |
| **SF-08 may start when SF-07 is in review** | Its pattern set and its decoded-vs-rendered discipline are independent; only its archive-boundary acceptance needs SF-07's merged vocabulary |
| **FND-06, SF-11** | No gate. Either can merge at any point |

⚠️ **`SF-08` was deliberately *not* given a hard `Depends on SF-07`.** Only half
of it depends on the vocabulary, and a hard dependency would wrongly forbid a
third developer from taking it in parallel later. ⭐ The lane assignment achieves
the ordering; the task definition stays honest about what actually blocks.

### Team sizes, unchanged and worth noting

`SF-11` is `pair` and `SF-01`, `SF-02`, `SF-07`, `SF-08` are `solo`. ⭐ **The lane
assignment does not override that**: a lane is who *owns* the sequence, not who
sits in the room. SF-11 still gets its second pair of eyes when it runs.

---

## M0 residue and the sequencing calls

**FND-06 — first residue task, and it is time-critical.** ⛔ It is a task that
**adds a rule to the floor**, and adding a rule is precisely what has broken
three in-flight branches in one milestone (**C5**). ⭐ **So it should be the
proving instance for whatever C5 rule the CTO makes**, and it should land while
**two** branches are in flight rather than fifteen. If option 1 is ruled, FND-06
carries the mechanism — the rule and the tree-wide pass that makes it true arrive
in one commit. ⚠️ **The window closes as M1 fills**: this is cheap today and
compounding every week it waits.

⛔ **It does not go ahead of SF-01.** SF-01 is the critical path and the
exemplar, and a half-day of R7-by-reviewer-grep is a smaller cost than delaying
the shape fourteen tasks will copy. FND-06 goes to the first slot that frees, or
to a third developer immediately if one appears.

**FND-05a — last, and that is a deliberate ranking rather than neglect.** Nothing
in M1 imports the parent workspace, it is now a pin file plus a verification
command rather than a composition, and it is the one task that can slip without
stopping anybody. ⚠️ It should not slip *indefinitely*: the failure it prevents —
a component at a commit the parent never recorded — has **no symptom**, so it is
discovered by being wrong rather than by failing.

---

## ⛔ The index was never in the repository, and the mechanism that follows

⚠️ **This board recorded `FND-02` as done with *"framework graph rebuilt at the M0
close"*. That was true in the worktree where it ran and false in the
repository.** `graphify-out/` is git-ignored, so ⛔ **an ignored artifact cannot
travel on a branch** — and I own status truth, so this is a defect in my document
before it is anything else.

⭐ **Measured 2026-09-09: 33 worktrees, 2 with an index** — the main checkout and
`FND-02`'s own. **31 of 33 agents could not have queried the graph**, while the
board told them it was there.

⛔ **It is the deepest instance of the shape this milestone keeps producing:
reading a record as a status.** The others were a stale finding acted on and a
back-triage of rulings that had already happened. ⚠️ **This one is worse, because
the record was a completed *acceptance*** — the strongest claim the process makes
— and it was never true where it mattered.

⭐ **And it reframes the coordination finding rather than adding one.** The
coordinator reports hand-assembling briefings instead of querying the graph, and
offers it as a discipline failure. ⛔ **It is not.** The graph was not in their
checkout. **They could not have queried it, and the board is what told them it
existed** — so the fix is not *remember to query*, it is *the index must actually
be present and the claim must be checkable*. ⚠️ Filing this against the
coordinator would have hidden the defect in my own document behind somebody's
diligence.

### The mechanism — `FND-07`, M1 step 1.3

⭐ **The rule generalises; the task ships.**

⛔ **Standing rule, now in `README.md`: no acceptance condition is satisfied by an
untracked artifact alone.** If what a task produces is git-ignored, ⭐ **the task
ships the check** — the check travels on the branch and the artifact does not.

**`FND-07` carries three things:**

| | Behaviour | Why |
|---|---|---|
| **Index absent** | ⚠️ **report the rebuild command, exit 0** | A fresh clone legitimately has none. ⛔ A red suite on clone is hostile and gets muted, which is how a check stops being read |
| **Index older than the newest tracked source** | ⛔ **FAIL** | ⭐ **A stale index is worse than an absent one** — absence is visible; staleness answers confidently with yesterday's tree |
| **Index present, current — and unbridged** | ⛔ **FAIL** on a doc↔code census below a recorded floor | ⚠️ **The worst of the three**, because all the green lights are on |
| **Wave-open checklist** | *index present and current in this checkout*, beside the `[structural]` sweep | Both are the PO's |

⛔ **The bridging half is the sharper finding and it lands on my own ruling.**
Measured on the rebuilt framework index: **232 doc↔code edges out of 6,081 —
3.8%** — and `graphify path "R7 …" "assert_clean()"` returns **no path, even
undirected.** ⚠️ **That is the question this repository most needs answered —
*which ruling does this code implement?* — and the index cannot answer it.** The
3.8% is incidental, from handoffs naming functions in prose.

⭐ **We wrote this rule for somebody else and did not apply it to ourselves.** I
put into `SK-07` that a graph built by running the tool alone has zero doc↔code
edges and that **bridging is the part that would be missed**; `FND-02` built the
bridging pass and ran it on the **corpus** — 806 edges, 162 of 166 lessons — and
nobody ran the equivalent here. ⛔ **A rule written for the consumer and not
applied to the framework is exactly the shape R19 exists to catch**, arriving
from the inside.

⭐ **And the cheap part nobody had measured, which makes R14 affordable.**
`graphify explain` and `graphify path` accept `--graph <path>` and **work from a
worktree with no index of its own**; `graphify query` does not.

⚠️ **That maps exactly onto R14's own qualification.** The two commands the ruling
holds for **unconditionally** are the two needing no local build; the one that
needs a local build is `query`, already the weak one. ⭐ **So the cost is paid once
per repository, not once per worktree** — 33 rebuilds was never payable, and ⛔ **an
unaffordable rule is one that gets skipped**, which is precisely what happened.

---

## Open work items — routed, with owners

| # | Item | Owner | When | Note |
|---|---|---|---|---|
| W1 | ⭐ **`require_slug`/`require_ordinal` format `{value!r}`** — every address segment, identity field and unit ordinal inherits an R7 echo, so **7 of 26 emission sites are one pair of lines seen through their callers** | Developer, with Ruling 10's `describe` extraction | **after step 1.3** | ⭐ **The highest-value single fix available**, and the ratio is why: fixing one pair of lines closes 7 sites. ⛔ A refusal that quotes the value has relocated the leak into a log |
| W2 | **Behavioural §1f check** — poison an absolute path into each string parameter, fail if the refusal reproduces it. Prototyped, deliberately not shipped. **46 pairs before the label fix, 45 after** | *unassigned* | with **W1** | ⭐ It is W1's enforcer: W1 fixes the sites, this stops them coming back. ⚠️ **It needs an owner or it evaporates** — and a delta of one, reported honestly, is exactly the number that makes it credible |
| W3 | ⚠️ **Fixture defect, found by a graph build rather than a test** — `depth1/.../media/diagram.svg` says *"Two nodes and an arrow"*, its lesson's `alt` says *"…joined by one arrow"*, and the geometry is an undecorated `<line>` with **no marker and no arrowhead**; the two accessible names also differ in wording | Developer 2 (FND-04's author) | with the next fixture touch | ⭐ **Worth more than the defect: a graph build found what the test suite did not.** ⚠️ Nobody had been told |
| W4 | **`handoffs/SF-05.md` still describes `LABEL_FORBIDDEN`** and lists its duplication as open finding 6; both are resolved by the hotfix | PO — ✅ **discharged here** | ✅ done | ⛔ **A handoff is a record and is not rewritten** — my own rule — ⭐ **so this row *is* the correction.** The board is where a superseded record gets superseded |
| W5 | **`unitdoc.py` is 827 lines against R11's 400, and belongs to `SF-10`** — not `SF-06` | `SF-10` | at **SF-10**, step 1.4 | ⭐ Routed with the number so the task inherits it. R11: the large modules arrive **as packages or not at all** |

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
| **R21's four remaining open rows** *(was five)* | CTO | each before its named task builds | ✅ `consuming.json` filled. Overlay `content.json` is next, owed before **SF-09** at step 1.3 — ⚠️ **two steps away, so near-term rather than comfortable** |

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
| 2026-09-09 | ⛔ **The framework's own graph is unbridged — 232 doc↔code edges of 6,081, 3.8% — and `path "R7 …" "assert_clean()"` returns nothing, even undirected.** ⚠️ **That is the question this repository most needs answered.** ⭐ **And we wrote this rule for somebody else:** SK-07 item 9 says a tool-built graph has no doc↔code edges and that bridging is the part that gets missed; FND-02 built the pass and ran it on the **corpus** (806 edges, 162/166) — nobody ran it here. ⛔ **A rule written for the consumer and not applied to the framework is R19's shape from the inside.** `FND-07` gains it, and the tripwire fails on a census below a floor: ⛔ **present, current and unbridged is a worse lie than absent**, because every green light is on and the one question that matters returns silence. |
| 2026-09-09 | ✅ **M1 steps 1.1 and 1.2 complete** — SF-01, SF-02, SF-07, SF-08, SF-11, SF-33, SF-03, SF-05, SF-06 all APPROVEd. Step 1.3 in progress: SF-09 awaiting review, SF-25 part-written, SF-23 and SK-01 not started. |
| 2026-09-09 | ⭐ **Ruling 8 retires a class: a filename component is validated by what is *permitted*, not by what is *forbidden*.** The blacklist let **seven** shapes through — vertical tab, form feed, non-breaking space, U+2028, `"`, `:`, `*` — two of which break the `file://` floor, making it an **R8** defect. ⛔ **A forbidden list is an open set and cannot be finished.** ⚠️ This project already refuses unknown contract versions, unknown profile names, unknown document keys — **the character blacklist was the one open set left, and it survived because it looked like a filename question rather than a contract question.** |
| 2026-09-09 | ⛔ **Board defect, mine: `FND-02` was recorded done for an artifact that never reached the repository.** `graphify-out/` is git-ignored, so an ignored artifact cannot travel on a branch. ⭐ **Measured: 33 worktrees, 2 with an index** — the main checkout and FND-02's own. **31 of 33 agents could not have queried the graph while this board said it was there.** |
| 2026-09-09 | ⛔ **The deepest instance yet of *reading a record as a status***, and the first where the record was a completed **acceptance** — the strongest claim the process makes. ⭐ **Mechanism, not a rebuild:** standing rule — **no acceptance is satisfied by an untracked artifact alone; the task ships the check, because the check travels and the artifact does not.** **`FND-07`** created (M1 step 1.3): absent → report the command, exit 0; ⛔ **stale → FAIL**, because a stale index answers confidently with yesterday's tree while absence is at least visible. |
| 2026-09-09 | ⭐ **Measured, and it makes R14 affordable: `graphify explain` and `path` accept `--graph` and work from a worktree with no index; `query` does not.** ⚠️ That maps exactly onto R14's own qualification — the two commands it holds for **unconditionally** need no local build, and the one that does is `query`, already the weak one. **The cost is paid once per repository, not once per worktree.** ⛔ 33 rebuilds was never payable, and an unaffordable rule is one that gets skipped. |
| 2026-09-09 | ⛔ **The coordinator's R14 finding is reframed, not filed.** They report hand-assembling briefings instead of querying, and offer it as a discipline failure. ⭐ **It is not — the graph was not in their checkout, and this board is what told them it was.** The fix is not *remember to query*; it is *the index must be present and the claim must be checkable*. ⚠️ Filing it against the coordinator would have hidden a defect in my own document behind somebody's diligence. |
| 2026-09-09 | **Five findings routed as W1–W5**, with owners. ⭐ **W1 is the highest-value single fix available**: `require_slug`/`require_ordinal` format `{value!r}`, so **7 of 26 R7 emission sites are one pair of lines seen through their callers**. ⚠️ **W1 and W2 are one piece of work** — W1 without W2 is a fix with no guard, W2 without W1 is a red check with 45 findings. |
| 2026-09-09 | ⭐ **W3 is worth more than the defect it names: a graph build found a fixture flaw the test suite did not.** The SVG declares an arrow; the geometry is an undecorated `<line>` with no marker, and its two accessible names disagree. ⚠️ Nobody had been told. |
| 2026-09-09 | **W4 discharged here rather than by editing `handoffs/SF-05.md`.** ⛔ A handoff is a record and is not rewritten — ⭐ **so the board row *is* the correction**, which is what the record-versus-claim rule is for. |
| 2026-09-09 | ⛔ **My allow-list decision is WITHDRAWN — I acted on a finding without re-running it.** Re-measured on the merged tip: the shipped check reports **0**, the rubric's **current** §1a patterns report **0** over `docs/` and `CLAUDE.md` and do not fire on the E02 line; the **superseded** patterns report **24, every one a false positive**. ⭐ The two-character minimum local part kills `n@router.get` exactly. **The allow-list is specified and deliberately not built** — X2's disposition, for X2's reason. |
| 2026-09-09 | ⭐ **The correction is a better precedent than my decision was.** An allow-list would have recorded **24 instances of a defect in the pattern as 24 facts about the tree**. ⛔ **Fix the class; list the instance only when the class is right and the instance is genuinely exceptional.** The surviving reasoning — no `docs/` exclusion, prose is not a §1e fixture, a short failing list beats a silent exclusion — is kept in `FND-06` for a real hit. |
| 2026-09-09 | ⚠️ **Third instance of one shape this milestone: a finding true when written and false when acted on.** ⭐ That is the record-versus-claim rule one level down — a finding is a **record**, but acting on it turns it into a **claim about now**. ⛔ **New rule: a finding is a measurement with an as-of and is re-run before it becomes a task**, and the finding template gains a required **`Measured`** field naming the command and its output. ⚠️ It has now bitten in both directions — a stale finding acted on, and a back-triage where most of the backlog *had already been ruled and could not be seen*. |
| 2026-09-09 | ✅ **Back-triage of the 23 pre-marker findings complete** — all marked and dispositioned, ⛔ **"noted" appears nowhere.** Three remain open and ⭐ **two were not on this board**: the port-size debt (`markdown.py` 678, `unitdoc.py` 827 against R11's 400 — routed to SF-12 and SF-19a, the two port tasks that have not run) and a repository-wide R7 sweep that is **not clean today**. ⚠️ Both untracked ones concern tasks that have not run yet, so both were still cheap when found. |
| 2026-09-09 | ⭐ **Decided: FND-06 gains a narrow allow-list of documented false positives**, not a `docs/` exclusion. The sweep's one hit is E02's own worked example of the escaping artefact that refused three clean lessons. ⛔ Excluding `docs/` would remove the check from the place with the worst record (`CLAUDE.md` records R7 violated there once). ⚠️ **A gate that must be silenced somewhere is safer with a short list that fails when it grows: the list gets read, the exclusion does not.** |
| 2026-09-09 | ✅ **M1 step 1.1 is four-fifths done** — SF-01, SF-02, SF-07 merged on APPROVE, FND-06 and all five follow-up steps complete, **the formatter interim over** (exclusion and assertion deleted together). 755 passed, 8 skipped, ruff clean both ways. SF-08 and SF-11 in progress. |
| 2026-09-09 | ⭐ **The lane rule held — and the lanes were swapped between developers, which is evidence for it.** The *pairs* stayed intact, which is the only thing the rule protects; ⚠️ **which** developer owns a pair is a scheduling question and belongs to whoever dispatches. A rule that also fixed the assignee would have blocked a sensible swap for nothing. |
| 2026-09-09 | ⛔ **`README.md:127` corrected: a forecast that had become history.** "SF-07's count key pushes the module past the ceiling" was ⭐ **true as history, stale as a claim** — and it sat in a plan document, where the next reader would act on it. ⭐ **New convention:** a handoff is a **record** and is never rewritten; a plan document is a **claim about now**, so a statement that has stopped being true is a defect and is edited. |
| 2026-09-09 | ⛔ **Retired: the "README/CLAUDE.md say R1–R19" finding.** Both live documents were corrected rounds ago; it has been re-reported **three times from quotations inside old handoffs**. ⭐ A quotation going stale is the record working correctly. **New rule: before reporting a defect found in a handoff, check the file it is about** — one `grep`, before the report. |
| 2026-09-09 | ⭐ **SF-06 gains the single block-type list**, decided now rather than at M2. `BLOCK_TYPES`/`CONTAINER_TYPES` and `COUNT_KEYS`/`CONTAINER_BLOCKS` are the same contract written twice, and **FND-04 wrote its copy expecting exactly this**. ⛔ Two copies of a contract is the defect diagnosed three times now — the review base in five places, the size ceiling nearly twice, `is_ignored` across two modules. Every task that adds a block type before M2 would add it twice. |
| 2026-09-09 | **SF-12 gains an acceptance clause** — *a `para` of tag-shaped text renders as visible text, not an element.* ⭐ SF-07 declined CommonMark type 7 on the promise that such a line stays prose; **SF-12 is the half that keeps it**. ⛔ Without the clause the promise had an author and no enforcer, and the failure is silent: the text does not vanish from the archive, it vanishes from the page. |
| 2026-09-09 | ⛔ **FND-03 follow-up: three skips in *every* container run.** ⭐ The CTO's framing, adopted: **a skip that every run reports is not a skip; it is an untested claim wearing a skip's clothes.** The container is authoritative by three less than it says. Resolve by detecting the workspace, or by naming those three as covered elsewhere **in the skip message** — ⛔ "leave them skipping" is not an option. |
| 2026-09-09 | **`math` refused as a block type, and written down instead.** ⛔ Inventing a type against **zero sources** is R1's error from the other direction. ⭐ The output is an **integration catalogue** entry: *"never silently drop" is about structure the vocabulary knows; a construct outside it degrades to prose, visibly, text intact* — a scoping fact for whoever plans, not a bug to file. ⚠️ A refused proposal that leaves no trace gets re-proposed. |
| 2026-09-09 | ⭐ **SF-33 created** — the contract version guard, step 1.1, **before SF-06**. R9 names six versioned contracts and **five are unwritten**: one extraction now against six divergent re-implementations later. ⛔ It closes a real hole — `value in SUPPORTED` accepts a JSON `true` where `1` is supported, so a malformed document passes the gate that exists to refuse it, silently, on the read path. **85 tasks; M1 is 16.** |
| 2026-09-09 | **SF-32 owns the media limit names.** ⚠️ `max_total_bytes`/`max_file_bytes` are free to rename **exactly until M2** — the moment an adapter writes one they are a `corpus_api` field and changing them is an R9 migration. ⛔ *"We can rename it later"* is false about anything a manifest declares. |
| 2026-09-09 | **FND-06 follow-up: the exception text is itself unenforced.** `Size exception: needed` passes the same gate as a real justification. ⭐ An opt-out nobody has to justify is a ceiling with a documented bypass — the erosion FND-01 exists to prevent, arriving through the door it left open. |
| 2026-09-09 | ⭐ **Finding closed by exercise — "nobody said of what."** SF-07 reported `rule` in *10 of 166 lesson files* and *15 of 218 markdown files*: same corpus, two denominators, both correct. ⚠️ **A missing denominator is exactly how "18 ISO files carry raw HTML" survived three documents and two review rounds.** A count without its denominator is not a measurement. |
| 2026-09-09 | **ruff formats Python inside Markdown fences**, so every handoff with a ```python block is format-checked. Convention is now `text`. ⭐ It moved from `module-structure.md` to `agent-protocol.md` because **a handoff author has no reason to re-read the module conventions** — ⚠️ placement, not strength, was what the rule lacked. |
| 2026-09-09 | ⛔ **A trial merge tells you the merge is good and nothing about the base.** A green merge over a red base is a normal result — and a release branch was declared healthy from a measurement of a merge. Rubric §0a-i now requires **both** numbers, and ⭐ **a red base is an urgent finding against the release branch**, not against the change under review. |
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
| 2026-09-09 | ⛔ **C5 — the parallel-authoring defect, now THREE instances in one milestone**: FND-04/line-length, FND-03's container/formatter, FND-02/formatter. ⚠️ The third arrived while this entry was being written. ⭐ `FND-04`'s handoff finding 10 predicted it and named the fix — **a recorded prediction that was not acted on and then came true twice more is the most expensive kind of finding this project produces.** Recommendation: land the floor's configuration as a wave-0 prerequisite and run it across the tree in the same commit that adds a rule. ⛔ **Asking the CTO to rule now, not at the next recurrence — M1 adds fifteen tasks, so the next rule meets fifteen branches, not four.** |
| 2026-09-09 | **C4 closed.** Fixed through FND-03's own wrapper; ⭐ the `Permission denied` at the gate was FND-03's unprivileged-uid hardening working as designed, and **nothing about the container was loosened to get past it**. |
| 2026-09-09 | ✅ **M0 COMPLETE** — green in the container, 124 passed / 8 skipped, floor clean. `FND-05a` and `FND-06` carry into M1 as residue; neither gates an M1 task, which is why the milestone closes rather than waits. |
| 2026-09-09 | ⭐ **Implementation decisions delegated to the PO and CTO.** Priority, sequencing, scope and task modification are ours; the user reviews the end result. Escalation is reserved for large or irreversible impact. ⚠️ Recorded because it changes what belongs in this Log: a decision taken is now an entry, not a proposal awaiting one. |
| 2026-09-09 | **M1 step 1.1 assigned in two lanes**, on one rule: ⭐ **a collision pair goes to one developer, never split across two.** Lane A = SF-01 → SF-02 (they share the depth/`levels` concept). Lane B = FND-04 follow-up → SF-07 → SF-08 (they share the `archive/` walker and the `disclosure` ruling). FND-06 then SF-11 to the first free slot. |
| 2026-09-09 | ⭐ **FND-04's follow-up promoted to a blocker of SF-07**, not a parallel chore. Steps 1–4 carry the `disclosure` fixture SF-07's acceptance is judged against; step 5's split must land before SF-07 commits, because **SF-07 adds a count key to a file already at the ceiling**. ⛔ Developer 2 is the only correct owner — the CTO's own argument was that the isolation question can only be answered by whoever knows the internals, and Developer 2 named the five seams. |
| 2026-09-09 | ⭐ **SF-01 ruled the exemplar**, not merely first on the critical path: it is the first framework contract and the conventions it sets are copied by fourteen tasks. Reviewed as a precedent. ⚠️ A convention corrected in task 1 costs one diff; in task 8 it costs eight. |
| 2026-09-09 | ⛔ **SF-08 deliberately given no hard `Depends on SF-07`.** Only its archive-boundary half depends on the vocabulary, and a hard dependency would wrongly forbid a third developer taking it in parallel. ⭐ The lane assignment achieves the ordering; the task definition stays honest about what actually blocks. |
| 2026-09-09 | **`Context` field fixed in `README.md`** — it prices **reading**, and a new **`Effort`** field prices work where the deliverable is a computation. ⭐ Adding a field is cheaper than re-estimating eighty-four tasks and it puts the estimate where the person who can make it is standing. Applied to `SF-07` (166-file triage) and retrospectively to `FND-02`, which is the evidence that produced it. |
| 2026-09-09 | ⭐ **Graphify recommendation decided, not proposed.** `SK-07` now generates the corpus graph, **bridged**, with the R3-safe ignore file — the highest exposure converted into a generated artifact, closing an R19 hole in the same edit. Headroom for SF-19a and the four skills tasks is scheduled for the M1→M2 boundary. |
| 2026-09-09 | ⛔ **`SK-07` corrected: it said "add the framework as a submodule".** R18's amendment had reached the ruling but not the task that consumes it — ⚠️ exactly the drift R21 exists to prevent, one level down. The framework is a **sibling checkout at a recorded commit**. |
| 2026-09-09 | **FND-06 re-sequenced** to be the first task landing under whatever C5 rule the CTO makes — ⭐ it *adds a rule*, so it is the proving instance rather than the next victim, and it should land while two branches are in flight rather than fifteen. ⛔ Still not ahead of SF-01. |
| 2026-09-09 | ✅ **C5 ruled: options 1 AND 2, option 3 refused.** ⭐ My recommendation of option 1 was right and **not enough** — they are not alternatives: option 1 prevents, option 2 detects, and **only option 2 catches the rule nobody has thought of yet.** Option 1's schedulable half was already done when M0 closed; its residue is a standing rule now in `FND-06`. |
| 2026-09-09 | ⛔ **C5's cause was the rubric, not the plan or the routing.** The gate reviewed `$BASE...HEAD` — the branch's own changes — so all three branches were **correctly green** and the rubric was asking the wrong question. ⭐ **The diff is the branch's; the verdict must be the merge's**, and those come apart precisely when two parallel tasks are each correct alone. §0a now reviews a trial merge. |
| 2026-09-09 | ⭐ **The meta-finding was ruled worth more than C5 itself, and my framing was adopted rather than softened.** ⛔ The protocol said to write findings down and never said anyone had to rule on one. Fixed on both sides: authors mark `[local]`/`[structural]`, and ⛔ every `[structural]` finding is **ruled, scheduled or explicitly accepted** before the next wave — *"noted"* is not one of the three. **This PO owns the pre-wave triage sweep.** |
| 2026-09-09 | ⛔ **My step-5 gate on SF-07 was wrong and the CTO overruled it.** I claimed SF-07's new count key pushed `test_fixture_consistency.py` over the ceiling; ⭐ **I had conflated 606 lines formatted with 554 unformatted** — the formatted figure is what the exclusion already contains, and the growth lands in steps 1–4 anyway. The correction improves the plan: coupling them would have put a critical-path task behind a refactor. **FND-04's follow-up splits at the seam — steps 1–4 gate SF-07, step 5 rides alongside.** |
| 2026-09-09 | ⚠️ **My urgency argument for FND-06 is now half wrong, recorded rather than quietly aligned.** I argued it must land while two branches are open rather than fifteen; the C5 ruling removes that pressure at the source, because FND-06 now brings the tree into compliance **in its own commit** and the trial-merge gate catches the rest. ⭐ What survives is the plain reason: R7 is the rubric's one HARD FAIL and is still enforced by hand. |
| 2026-09-09 | ✅ **R21 register: `consuming.json` filled, open rows 5 → 4.** ⭐ This board's correction — *G1 restored which commit; nothing said which version of the promise* — was adopted: the pin file records the **build**, `provides` records the **promise**, `consuming_api` versions the schema. ⚠️ Its *content* is deliberately not designed yet — that would be designing a runtime contract against zero implementations, R1's error from the other direction. |
| 2026-09-09 | ⭐ **Step 1.1 dispatches now, SF-01 first.** The CTO ruled nothing blocks it, and named the reason I had given a round earlier: holding five tasks and two idle developers against work already finished is *waiting for the label rather than the prerequisite* — ⛔ doing that twice, having named it once, would be worse than never having named it. |
| 2026-09-09 | ⛔ **First `[structural]` sweep run, and it is empty — which is a hole, not a clean bill.** The marker landed this round, so the triage list is blind to the **23 findings** filed before it existed (`FND-01` 5, `FND-02` 8, `FND-04` 10) — ⚠️ **including `FND-04`'s finding 10, the one that motivated the mechanism.** ⭐ The machinery built to stop unacted-on findings would have missed the finding that built it. **Back-triage scheduled, PO-owned, before M1's wave opens.** |
| 2026-09-09 | **C2 fixed, and two details kept:** the bug was in **five** places — the shell preamble and all four Python checkers, each re-deriving the base — and ⛔ **the failure mode flatters**, showing more work rather than less, so nobody questions it. ⭐ A check that cries wolf gets waved through; one that under-reports gets believed. |
