# Board — live status

**Single source of truth for what is in progress and what is done.** Owned by
the framework Product Owner. Task *definitions* live in the epic documents
(`E00`…`E13`); this file carries only **state**.

✅ **M0 COMPLETE. M1 steps 1.1 and 1.2 COMPLETE.** **In flight: M1 step 1.3** —
**SF-25** in progress (Developer 1, `feat/SF-25-validate` @ `96dd17e`), **W1+W2**
in progress (Developer 2, `fix/W1-W2-address-echo`); **FND-07**, **SF-23**,
**SK-01** and **W3** sequenced below and not started.

⛔ **Release branch: `release/m0-foundations`, and M1 continues on it.** ⚠️ **This
header previously named `release/m1-one-page`, cut from `release/m0-foundations`.
That branch does not exist and never did** — verified, `git branch -v` lists no
such ref, and every M1 task (SF-01, SF-02, SF-03, SF-05, SF-06, SF-07, SF-08,
SF-09, SF-11, SF-33 and the label-seam hotfix) merged into
`release/m0-foundations`. See **the release-branch reconciliation** below for the
ruling and why it is not re-cut mid-wave. Developers branch off it, the CTO
reviews against `../conventions/review-rubric.md`, only reviewed work merges
back. Flow: `../conventions/delivery-flow.md`.

📏 **Base, measured in the pinned container at `9ad45a2`: 1761 passed, 46
skipped, quality floor clean.**

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
below still has **three** open rows. The question list being empty means the known
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

## Delivery-process defects

| # | Defect | Owner | Status |
|---|---|---|---|
| C2 | **The rubric's review base resolved against a stale `main`** — ~100 changed files instead of ~14, three tasks' work attributed to one author. | CTO | ✅ **fixed** |
| C3 | **`ruff format` vs R11 on one file** — see resolved **Q6**. | CTO | ✅ **ruled**; the split is Developer 2's |
| C5 | ⛔ **Parallel-authoring defect — three instances, one milestone.** A quality rule merges; a file authored *before* it lands fails it. FND-04/line-length, FND-03's container/formatter, FND-02/formatter. | CTO | ✅ **RULED** — options 1 **and** 2, option 3 refused. ⛔ **The reasoning lives in the C5 section below and is deliberately not restated here** |

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
| SF-08 | Personal-data gate | Developer 1 | *merged* `f9be376` | ✅ `done` — ⚠️ **its finding 6 is only one-fifth carried; see W7** | — | Home path refused at the archive boundary; build output scrubbed before a stream; ⛔ **three patterns, no content shape, no username pattern**; a document of 16-digit card-shaped strings **passes**; material that only resembles personal data after escaping is **not** refused; every gate reads decoded strings — asserted |
| SF-11 | Page assets | Developer 2 | *merged* `56caba0` | ✅ `done` — ⚠️ **three rulings from it are uncarried; see W8, W9, W10** | — | Highlight tests pass incl. no token combination taking the comment colour without being a comment; a page opens with only local requests; every palette token defined in **both** themes and clearing contrast; vendored bundles carry licences, unedited |

| SF-33 | Contract version guard | *first free slot* | *merged* `0e59645` | ✅ `done` — ⚠️ one finding accepted with the cost named; see W11 | — | ⛔ A JSON `true` is **refused** where `1` is supported — asserted, with `1.0` and `"1"`; refusal is a raise, never a migration; `SF-02` imports it; ⛔ a test fails if a second version check appears. **Before SF-06** |

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

## ⛔ The release-branch reconciliation — a name read as a scope

⚠️ **This board's header claimed a release branch that does not exist and never
did.** It said *"Release branch: `release/m1-one-page`, cut from
`release/m0-foundations`"*. **Measured 2026-09-09:** `git branch -v` lists no
`release/m1-one-page`; every M1 task — SF-01, SF-02, SF-03, SF-05, SF-06, SF-07,
SF-08, SF-09, SF-11, SF-33 and the label-seam hotfix — merged into
`release/m0-foundations`, and the green base is measured there.

⛔ **It is the third instance in one milestone of reading a record as a status**,
after the stale finding acted on and the index recorded as present. ⚠️ **And it is
a new sub-shape worth naming, because it will recur at every milestone boundary:
the branch's *name* was read as its *scope*.** A branch called
`release/m0-foundations` looks finished when M0 closes, so a plan document
invented its successor — and nobody checked, because the name made the claim
plausible.

### The ruling: M1 continues on `release/m0-foundations`, and the naming scheme is retired

⭐ **Not re-cut mid-wave.** Five agents' bases resolve against that branch, the
only measured-green number in this project is on it, and re-cutting now would
invalidate every one of them for a cosmetic gain. ⛔ **A rename that buys tidiness
and costs five bases is not a trade this board takes mid-wave.**

⭐ **And the deeper fix is not a better name, it is fewer of them.** A
milestone-named release branch is a claim with an expiry date baked into it, so
this defect is *guaranteed* to recur at M2 — the name goes stale the moment the
milestone closes while the branch keeps working perfectly. ⛔ **A name that
encodes a status is a status stored in the one place nothing can update it.**
So: `release/m0-foundations` is **the release branch**, its name is now
**historical rather than descriptive**, and this line is what says so. ⚠️ At the
M1→M2 boundary the PO decides whether a new branch is cut — and if the answer is
another milestone name, the answer is wrong.

---

## M1 step 1.3 — the assignment

> Step 1.3 closes when `validate` defines "done" for an adapter, the exercise
> contract exists, reconnaissance is a skill rather than a thing somebody did by
> hand, and ⛔ **the index this plan's context budgets assume can be trusted.**

| Task | Title | Owner | Branch | Status | Blocked on | Closes when |
|---|---|---|---|---|---|---|
| SF-25 | `studyforge validate` | Developer 1 | `feat/SF-25-validate` @ `96dd17e` | `in-progress` | — | Both valid fixtures pass; each invalid fixture fails with its own message; the silently-skipped-construct fixture fails while every other check passes; ⛔ **a test asserts `validate` calls the SF-08 gate** — carried this round, see **W7**. **Remaining at handoff:** the `report`, `corpus`, `cli`, `init` and `__main__` test modules |
| W1 + W2 | The `{value!r}` echo, and the check that stops it returning | Developer 2 | `fix/W1-W2-address-echo` | `in-progress` | — | `require_slug`/`require_ordinal` stop reproducing the value; the behavioural §1f sweep ships with a declared allowlist that **fails on any new echo**. ⛔ **One piece of work, not two** |
| W3 | The fixture SVG that declares an arrow it does not draw | Developer 2 | *with W1+W2* | `todo` | — | The geometry matches the two accessible names, or the names match the geometry — and they agree with each other |
| FND-07 | Knowledge-index availability and freshness | **Developer 2, next** | — | `todo` | — | Absent → report and exit 0; ⛔ **stale by content, never by mtime** → FAIL; unbridged → FAIL. ⭐ **The task ships the check; the artifact does not travel** |
| SF-23 | Exercise and workspace contract | **Developer 1, next** | — | `todo` | — *(SF-09 merged)* | §7's three states are structural, with no `state` field to forget; ⛔ **it must ship the `graded` fixture, which does not exist** — see below |
| SK-01 | Source reconnaissance | **next free slot, after SF-25 merges** | — | `todo` | ⚠️ soft: SF-25 | Correct manifests for the Java corpus, a flat source, and a prose-only source; ⛔ **colliding and unaddressable titles are named**, carried this round |

### ⛔ Merge order inside step 1.3, ruled — **W1+W2 before SF-25**

⚠️ **CTO round 17, ruling 17.** The boundary is **upstream**: `validate` does not
scrub, ⭐ **W1 is the fix**, and `validate` owns an *end-to-end poison test* which
is not a duplicate of W2 because it is taken from a different vantage point
(rubric §10b, third instance). **Measured:** 6 of 10 poison shapes reproduced an
identifier in a report line; with W1 prototyped, **10 of 10 clean with the
diagnosis intact** — ⛔ so the echo is removed without deleting the sentence that
makes the refusal useful.

⭐ **Both developers already have this, and the board is not where they learned
it** — it is recorded here because the *order* is a scheduling fact and
scheduling facts belong to this document.

### ⛔ New dependency inside step 1.3: `Profile` grows before the sibling check

⚠️ **Found by the trial merge, and it is C5's ruling paying for itself inside one
round** (round 17, finding 12). `structure.py:109` in SF-25 **branches on a
placement profile name**, and **SF-03's `ast` test in another package fails**
because of it. ⭐ **Nothing but the trial merge could have found this** — each
branch is correct alone, which is the only situation C5 ever occurs in. Option 2
was the half that mattered and this is the evidence.

⛔ **Branching on a profile name is R1 in miniature** — the framework knowing a
source-shaped fact by name instead of asking for a capability — so the fix is not
to work around it. `Profile` gains the capability the sibling-collision check
needs.

> ⛔ **SUPERSEDED — Developer 1 declined to grow `Profile`, reported it rather
> than diverging quietly, and they are right.** ⭐ **They used my own argument
> against my conclusion:** I ruled *the only caller writes it, because a
> capability designed with no caller is a guess* — and then measured that the
> collision check needs **no** new capability, so a capability added now would
> have **no caller at all.** ⚠️ **Evidence, not assertion:**
> `test_nothing_downstream_branches_on_a_profile_name` went **1 failed → 1
> passed**, with **zero** profile names in `validate/` and **zero** profiles
> skipped. ⛔ **The premise I ruled on — that a capability was required — was
> simply false**, and the CTO is ruling on the substitution.
>
> ⭐ **Related, and it makes the reversal cheaper than it looks:** finding 18 says
> the check they replaced **reported a non-defect** — the old
> `check_sibling_collisions` was both narrower *and* wrong. ⚠️ So the version I
> was scheduling work to support was not a thing worth supporting.
>
> ⭐ **Recorded rather than quietly aligned, because the reversal is the
> evidence:** a developer who reports a refusal costs one message; one who builds
> the capability I asked for costs a contract nobody calls, ⛔ **and this project
> has now refused three mechanisms by checking whether the problem was still
> there** — X2's card pattern, the R7 allow-list, and this. The reasoning below is
> kept because the *general* rule survives and will be needed again; only its
> application here was wrong.

**Decision — Developer 1 adds it, inside SF-25's branch, and it is reviewed as a
change to the placement contract.**

- ⭐ **The only caller writes it.** `SF-25` is the first and only consumer of this
  capability, and ⛔ **a capability designed by somebody with no caller is a guess
  about what the caller needs** — the same error this board refused when it
  declined to design `consuming.json`'s content against zero implementations.
- ⛔ **`SF-03` is merged, so "SF-03 must add it" cannot mean a task acts.** It
  means the placement contract grows, and the live task holding the need is the
  one that grows it. ⚠️ **Routing it to a task that does not exist is B1's defect
  — a condition phrased as "wait for X" is a task that waits forever**, and this
  board has now cited that twice in one round.
- ⚠️ **It does not go to Developer 2 despite `placement/` being their step-1.1
  surface.** That would put a critical-path task behind another developer's
  queue, ⛔ **which is exactly the coupling the CTO overruled me for in step
  1.1.** Applying the correction is the point of having taken it.
- ⛔ **The review vantage point is what makes this safe:** the CTO reviews the
  `Profile` change as a **contract change on SF-03's surface**, not as a
  `validate` internal. ⭐ A contract that grows inside a consumer's branch is
  exactly where a contract grows badly, and naming the vantage point is the
  cheapest guard available. `E01`'s `SF-03` gains a carried note recording that
  `Profile` grew and why, so the next reader is not left inferring it.
- **Developer 1 builds everything not gated by it first** and reports what
  remains blocked — already instructed by the CTO, recorded here so it is not
  re-decided.

### ⛔ Two questions that are mine, ruled here rather than deferred

**Q16 — the media limit names, and a deadline that pointed at the wrong task.**
⚠️ **This board said `max_total_bytes`/`max_file_bytes` are free to rename
*"exactly until M2"* — but `SF-32`, which owns the real names, is M3.** ⛔ My own
Log entry created a deadline no task could meet.

⭐ **Ruled, and it dissolves rather than reschedules.** Two corrections:

1. ⛔ **The names freeze when the first real manifest declares them, not at a
   milestone.** A milestone is a date; the thing that makes a rename an R9
   migration is **an adapter having written the key**. ⚠️ Same defect as the
   release-branch name — a status inferred from a label rather than from the
   event.
2. ⭐ **So `ISO-04`, the first real manifest, simply omits `media`** — and the
   question does not bite at all. `SF-02`'s acceptance already asserts **absent
   `media` is committed-with-defaults**, so omission is not a workaround, it is
   the declared path. ⛔ **`SK-07` must be told, because it generates manifests**
   and a generator that emits a key nobody needs freezes that key on everybody.

**Q18 — the integration track's definition of done.** ⭐ **It is already implied
by a standing ruling, and saying so is cheaper than inventing one.** §7's three
states and C5 give it: ⛔ **a corpus with no graders is complete at M4, not
short.** ISO has zero graders, zero exercises and structurally empty
`permitted_edits`, so **its definition of done is the reading floor — narrated,
navigable, offline, openable over `file://`.**

⚠️ **And Q8's real ambiguity, which is the half worth ruling:** §11.2 sits above
M4's *"it is served"*. ⛔ **"It is served" is not a condition for a corpus that is
never served.** ⭐ Reading it as one would make a **complete** corpus wait for a
milestone it has no business in — which is exactly the error C5 was written to
prevent, one level up. The track is done when `studyforge validate` and
`studyforge plan` accept ISO's archive and placement and the pages open.

### The assignment, and the reasoning that makes it re-checkable

⭐ **The collision-pair rule again, and it decided both slots.** It is the rule
that held through step 1.1 and it is applied here on **measured** surfaces, not
guessed ones.

> ⛔ **Queues as of the SF-25 handoff, and they supersede the table below where
> they differ.** **Developer 1:** ~~SF-25~~ *(complete, `e6c318c`)* → **SF-23**
> (+ the graded fixture + `W14`) → **`W8`** → **SK-01**. **Developer 2:**
> W1+W2+**W6** → ⛔ **W7+W13 (one commit, urgent)** → **FND-07** → **W3** as slack.
>
> ⚠️ **W7 displaced FND-07 deliberately.** A home path in `corpus.json`'s `title`
> validates green today — ⛔ **an R7 hole in the front door of the one command an
> adapter author is told to trust (R2)**, and R7 is the rubric's single HARD
> FAIL. ⭐ **FND-07 protects the index; W7 protects the product.**
>
> ⭐ **`W8` goes to Developer 1, and ruling 21 is why it cannot ride in SF-12.**
> ⛔ *If the JS runtime arrives in `SF-12`'s branch, `SF-12`'s tests are the first
> thing it runs and a green `SF-12` certifies itself* — C5's shape, failing
> unfalsifiably. ⚠️ **Not Developer 2**: no shared surface (`docker/dev/`, not
> `tools/quality/`), and their lane is full. ⭐ **Acceptance is one number** —
> `-rs` reports **8** skips, not 46, and none names a missing JS runtime; ⛔ **the
> remaining 8 must *stay* skipped**, because a run reaching zero has broken the
> recursion guards. ⚠️ *"It gates a step and a person does not"* — if Developer 1
> is still on SF-23 when SF-12 comes up, it moves, and that is not a re-decision.

| Lane | Developer | Order | Reasoning |
|---|---|---|---|
| **A — the archive-document contract** | Developer 1 | **SF-25** → **SF-23** | ⚠️ **They share one surface: what is legal inside a practice archive document.** `SF-25` decides what `validate` accepts in every archive document; `SF-23` puts a **new `exercise` object inside one** (Q2's ruling — not a sixth contract, an object on the existing `raw_api`). ⛔ Split across two agents, they disagree about whether `validate` knows `exercise` exists, and the disagreement surfaces as a corpus that validates green while its graders are invisible. One agent, and the question never arises |
| **B — `tools/quality`'s `CHECKS`** | Developer 2 | **W1+W2** (+ **W3** as slack) → **FND-07** | ⚠️ **Measured, not assumed:** `handoffs/SF-03.md` finding 6 places W2 *"beside the R7 sweep in `tools/quality`"* in its own words, and `FND-07`'s tripwire registers in the same `CHECKS` tuple — **five entries today**. ⛔ Two agents adding two entries to one tuple in parallel is C5's shape with a contract instead of a line length, and C5 is the defect this milestone has already paid for three times |
| **slack** | Developer 2, alongside | **W3** | One fixture file, decoupled from everything. ⛔ **Its stated trigger was wrong and is corrected below** |
| **queued** | next free slot | **SK-01** | The only step-1.3 item with genuine slack — and the one that most wants a slot where two people can sit |

⛔ **W3's trigger was a task that waits forever, and that is B1's defect
returning.** It was routed to Developer 2 *"with the next fixture touch"* — but
the next fixture touch is now **SF-23's**, which is Developer 1's, so Developer 2
would have waited for an event that never reaches them. ⭐ **A trigger naming
somebody else's work is not a trigger.** W3 is one file, so it is dispatched on
its own, **now, ahead of SF-23**, which also removes the only collision between
the two lanes: both touch `tests/fixtures/` and the split digest modules, and
ordering them in time is cheaper than ruling about them.

### ⛔ SF-23 has no fixture for the state it exists to encode

⚠️ **Measured 2026-09-09:** `grep -rln '"exercise"' tests/fixtures/` returns
**nothing**, while two `practice-1.json` documents exist under `depth2`. So of
§7's three states, the fixtures carry **`none`** (depth1 writes no practice
document) and **`ungraded`** (a practice document with no `exercise` key) — and
⛔ **`graded`, the state the whole task is about, has no fixture at all.**

⭐ **`SF-23` ships that fixture itself, and this reverses a precedent
deliberately.** In step 1.1 the disclosure fixture went to FND-04's author and
**gated a critical-path task on another developer's work** — the CTO overruled
half of that coupling and was right to. ⚠️ The lesson was *do not put a
critical-path task behind another developer's refactor*, and applying it here
means the task that needs the fixture writes the fixture. ⛔ **Additively** (R3),
and the digest recomputation is part of the task, not a follow-up.

### Why SK-01 is last, and it is a ranking rather than neglect

⚠️ **Its `Context` cites *"SF-25 output"* while its `Depends on` says only
SF-02.** That is not a contradiction to fix by deleting one of them: SK-01 can be
*authored* without `validate`, but a reconnaissance skill whose proposal is
judged by `studyforge validate` cannot be **finished** honestly before that
command exists. ⭐ So it wants SF-25 merged, which is exactly what is happening.

⭐ **And §9 — a skill precedes the artifact it produces — is satisfied rather
than strained.** ⚠️ It is worth being honest that it is *already* half-violated:
ISO's reconnaissance was done **by hand** and its conclusions are on this board.
⛔ **That is a finding against SK-01 under R19, not a reason to hurry it** — every
step of that hand-done reconnaissance which SK-01 should have produced is exactly
the evidence this skill needs, and it is available now precisely because somebody
did it manually first.

---

## The wave-open checks — ⛔ **three**, run 2026-09-09 by the PO

⛔ **All three are mine and all three run before the wave, not after it.**

| # | Check | Command |
|---|---|---|
| 1 | Index present and current **in the main checkout** | `built_at_commit` vs `git diff --quiet <it> HEAD -- src tools docs` |
| 2 | The `[structural]` triage list | `grep -rn '\[structural\]' docs/tasks/handoffs/` |
| 3 | ⭐ **NEW — C6: every ruling made since the last wave reached its artifact** | for each, open the task/epic/spec/convention it names and read the clause |

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
| W1 | ⭐ **`require_slug`/`require_ordinal` format `{value!r}`** — every address segment, identity field and unit ordinal inherits an R7 echo, so **7 of 26 emission sites are one pair of lines seen through their callers** | **Developer 2**, `fix/W1-W2-address-echo` | ⛔ **now, and before SF-25 merges** (round 17, ruling 17) | ⭐ **The highest-value single fix available**, and the ratio is why: fixing one pair of lines closes 7 sites. ⛔ A refusal that quotes the value has relocated the leak into a log. ⚠️ **Round 17 finding 9 rides in the same commit:** `AddressError`'s docstring *mandates* the echo this removes |
| W2 | **Behavioural §1f check** — poison an absolute path into each string parameter, fail if the refusal reproduces it. Prototyped, deliberately not shipped. **46 pairs before the label fix, 45 after** | **Developer 2** — ⭐ **it has an owner now** | with **W1**, same branch | ⭐ It is W1's enforcer: W1 fixes the sites, this stops them coming back. ⚠️ A delta of one, reported honestly, is exactly the number that makes it credible. **Measured since:** 6 of 10 poison shapes reproduced an identifier in a `validate` report; 10 of 10 clean with W1 prototyped |
| W3 | ⚠️ **Fixture defect, found by a graph build rather than a test** — `depth1/.../media/diagram.svg` says *"Two nodes and an arrow"*, its lesson's `alt` says *"…joined by one arrow"*, and the geometry is an undecorated `<line>` with **no marker and no arrowhead**; the two accessible names also differ in wording | **Developer 2** (FND-04's author) | ⛔ **now, as slack — trigger corrected** | ⭐ **Worth more than the defect: a graph build found what the test suite did not.** ⛔ **Its old trigger — *"with the next fixture touch"* — named work that is now Developer 1's**, so Developer 2 would have waited forever. A trigger naming somebody else's work is not a trigger |
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

⚠️ **Ruling 19's load argument applies unchanged: it is one test, not two.** ⛔ If
construction shows they are genuinely two tests, the commit still holds — **the
collision surface is identical either way**, and that is what the pairing rule
protects. ⭐ **The combined item inherits W7's deadline, not W13's:** it goes
**ahead of FND-07**, because R7 is the rubric's one HARD FAIL and this one is in
the front door of the command an adapter author is told to trust.

### ⛔ W6–W13 — the eight rulings that had nowhere to land

⚠️ **Every one of these was ruled by the CTO and every one would still have
evaporated**, because a ruling with no row, no clause and no trigger lives only
in a handoff. ⭐ **This table is the destination they lacked** — see *ruling is
not carrying*, above.

| # | Item | Owner | When | Note |
|---|---|---|---|---|
| W6 | ⛔ **The R7 exception-text check** — any `{exc}` interpolation re-emits the absolute path the inner refusal was careful not to emit. `SF-02` finding 1 and `SF-05` finding 4, ruled round 8: *"build it now — a check that arrives after twenty sites exist is one nobody turns on"* | **Developer 2**, with W1+W2 | ⛔ **now** — the developer is standing in `tools/quality` this minute | ⚠️ **`CHECKS` still has five entries and none is this**, four rounds after *"build it now"*. ⭐ The ruling's own urgency argument is the schedule: `SF-04`, `SF-25`, `SF-28` and every adapter each add sites. ⛔ It is a **sibling of W2, not a duplicate** — W2 poisons a *parameter*, this reads a *format string* |
| W7 | ⛔ **URGENT — `corpus.json` is not gated at all.** A home path in the manifest `title` **validates green: zero findings, zero unchecked claims.** ⛔ **The tool an integrator is told to trust (R2) reports the corpus's front door clean.** Plus round 10's call-site table, of which only `SF-06`'s clause had landed | **Developer 2**, ⛔ **one commit with W13** | ⛔ **next, ahead of FND-07** | ⚠️ **Verified independently by the PO, not inherited:** `assert_clean` is called from `archive/document.py`, `corpus/container/document.py` and `unit/content.py` — and ⛔ **`corpus/manifest/` (6 modules, `document.py` among them) calls it nowhere.** ⭐ **`validate` was already wired for it: the catch is correct, the raise never comes** — which is why nothing looked wrong. ⛔ **The fix is a test that every reader gates, never a call added to a list** — a hand-maintained list of readers is how this went missing |
| W8 | ⛔ **The dev image has no JS runtime**, so 38 tests can only run off-image. `SF-11` finding 1, ruled round 11 an `FND-03` follow-up: *"not optional and not 'when convenient'"* | *unassigned* — ⚠️ **needs one** | **before the next E03 task** (`SF-12`, step 1.5) | ⛔ E03 and E04 widen this gap from here, and the container is authoritative *because it is pinned*. ⚠️ A claim only provable off-image is a claim the verdict cannot rest on |
| W9 | **The markup contract has one side written** — `surface.py` guesses `SF-12`'s class names. Ruled round 11: **SF-12 reviews the names in one commit as its first act** | `SF-12` | at **SF-12**, step 1.5 | ⛔ Not in `E03` yet. ⭐ *"Its first act"* is a sequencing instruction and it only works if it reaches the task **before** the task starts |
| W10 | **Palette tokens with no painter** — `--hl-*`, `--player-height`, `--practice*` are defined and unclaimed. Ruled round 11: a **named, self-retiring list**, and E04/E08 acceptance gains *remove your token* | PO → E04, E08 | **before E04 / E08 are authored** (M3, M5) | ⭐ Self-retiring is the good part: the list is a number that must reach zero, ⛔ not an exclusion that lives forever. The word *"unclaimed"* currently appears nowhere |
| W11 | **`api` is a generic field name** — the tree guard would flag a module reading an unrelated `api` key. `SF-33` finding 3 | ◐ **ACCEPTED, cost named** | if a colliding field is ever minted — realistically `SF-10` or E03's TOC | ⭐ **Zero instances today**, and the finding states its own remedy: narrow the rule to the module rather than drop the field. ⛔ Recorded so the remedy is not re-derived under time pressure |
| W12 | **The extraction source's `naming.py` docstring says 1,282 where the tree holds 1,290.** `SF-09` finding 3, routing half | ◐ **ACCEPTED, cost named** → E11's integration catalogue | at **SK-07** / the catalogue | ⭐ A defect in a repository v1 does not modify (R20), and the *rule* it exercised — **a claim about another repository is verified in that repository** — is already ruled and applied. ⚠️ Its ask was *"route to whoever owns the drift catalogue"*; `DOC-2026-09-09-codesignal-drift.md` predates it and has no entry |
| W14 | **The count-mismatch invalid fixture that acceptance has always named and FND-04 never shipped** — `E10` names six, `tests/fixtures/invalid/` holds five. ⭐ **Downgraded on measurement: `check_counts` *is* implemented and tested — only the fixture is absent.** ⛔ **A record defect, not a coverage hole, and it does not gate SF-25's merge** | `SF-23` (Developer 1) — on **FND-04's surface** | at **SF-23**, with the graded fixture | ⛔ **An acceptance clause naming a fixture that does not exist is unfalsifiable** — the same class as an acceptance satisfied by an untracked artifact, arriving in a *condition* instead of a build product. ⭐ Ruled: **build the fixture, keep the clause** — it is the only statement that the count check is exercised, and the count check guards *silently lossy ingestion* |
| W15 | ⛔ **Tooling wrote to a source repository's root ignore file** — a `graphify` git hook appended `graphify-out` to the ISO repository's ignore file on an ordinary commit, unrequested, ⚠️ **in the one repository where R3 is absolute.** Second half: `.claude/settings.json` carries a machine-local absolute path, an R7 exposure **created by tooling that no ruling names as a source** | PO → `OPS-05`, `SK-07` item 9 | ⛔ **before any adapter runs against a real source** | ⭐ **This framework's own repository is clean — checked, not assumed**: zero tracked files carry the real home path, our `graphify-out/` ignore came from `FND-01`'s scaffolding (deliberate, and this is not a source repository), no hooks installed. ⛔ **So the exposure is scoped to the corpus side, which is exactly where R3 bites.** ⚠️ **The rule is written in `graphify.md` and `SK-07` item 9 and is enforced by nothing that runs** — and `OPS-05` checks at **build** time while this happens at **index** time. PO-Integration reverted it and **re-measured after the fix**: the hook fired again, the root file stayed clean |
| W13 | ⛔ **One commit with W7 — ruled, see below.** **Two copies of the personal-data gate that already disagree** — `tests/fixture_checks/personal_data.py` skips dict keys where `SF-08`'s does not (`SF-06` finding 3, ruled **urgent**); and **`imports()` is spelled twice** and should be extracted to `tests/support.py` *"before a third scanner writes a third copy"* (`SF-06` finding 8) | *unassigned* — ⚠️ **needs one** | ⛔ **before `SF-12`**, the next scanner-shaped task | ⭐ **One row because they are one defect**: the project's most-repeated diagnosis is *two copies of a contract*, and here it has produced a copy that **already gives a different answer**. ⚠️ `tests/support.py` exists and has no `imports()` |

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

## Log

| Date | Change |
|---|---|
| 2026-09-09 | ⛔ **URGENT — `corpus.json` is not gated at all, and `W7` is promoted from *carried* to *carried and incomplete*.** A home path in the manifest `title` **validates green: zero findings, zero unchecked claims.** ⚠️ **Verified by the PO independently rather than inherited:** `assert_clean` is called from `archive/document.py`, `corpus/container/document.py` and `unit/content.py`, and ⛔ **`corpus/manifest/` — six modules, `document.py` among them — calls it nowhere.** ⭐ **`validate` was already wired for it: the catch is correct and the raise never comes**, which is exactly why nothing looked wrong. ⛔ **So the tool an integrator is told to trust (R2) reports the corpus's front door clean.** ⭐ **The remedy matters more than the fix: a test that every reader gates, never a call added to a list** — a hand-maintained list of readers is how this went missing. |
| 2026-09-09 | ⭐ **Ruled: `W7` and `W13` are one commit, Developer 2, ahead of FND-07 — Ruling 19's argument a second time.** ⛔ **They are one defect seen from both ends: *the gate's coverage is assumed rather than asserted.*** W13 is **two copies that disagree**; W7 is **one reader that calls no gate at all**. Same remedy, prescribed by the CTO for both: ⭐ **make the omission unrepresentable rather than maintain a list** — this project's most-repeated finding, arriving for the fourth time. ⚠️ **If construction shows they are two tests, the commit still holds** — the collision surface is identical either way. ⛔ **The combined item takes W7's deadline: R7 is the rubric's one HARD FAIL, and FND-07 protects the *index* while W7 protects the *product*.** |
| 2026-09-09 | ⛔ **C6's sixth instance, inside the section that exists to enforce C6 — and the PO carried the fix rather than routing it.** §8a's coverage counters matched `^[0-9]+\.` while **§8 rules the heading form acceptable**, and `SF-03`, `SF-09` and `SF-11` all write findings as `### 1. …`. ⚠️ **For those handoffs both counters returned zero and *"the two numbers must agree"* passed at 0 = 0.** ⛔ **It did not fail; it passed the wrong thing** — C2's failure mode, which this rubric itself calls the worse of the two, because ⭐ **a check that under-reports gets believed.** Regexes widened to accept both forms; ⚠️ **the CTO owns whether to narrow §8 to one spelling instead** — one would be stronger, on this project's own repeated finding that a list of accepted shapes is an open set. |
| 2026-09-09 | ⭐ **Ruling 23 — the `Profile` substitution ACCEPTED, and the CTO overturned their own routing**: *"My round-17 Finding 12 routed this wrongly; theirs is right."* ⛔ **A `generates_beside_material` boolean would be an enumeration in disguise** — it sorts profiles into two classes, the third must declare a side, and a wrong answer costs a **silently skipped check**, ⚠️ *which is the failure the old code already had.* Finding 18 settles it: **the replaced check reported a non-defect**, so a capability would have preserved a **wrong** check behind a cleaner branch. ⭐ **Carried into `agent-protocol.md` as a general rule: name the caller and the question before growing another task's contract; if the question dissolves when you compute the answer directly, compute it directly.** ⚠️ **Third time an author has beaten a ruling this way.** ⛔ Both the PO's decision and its reversal are on this board, because **the reasoning is what stops it being re-decided.** |
| 2026-09-09 | **Ruling 24 — merge sequencing confirmed.** `W1+W2+W6` merges first → **SF-25 deletes its six `OWED_TO_W1` entries in its own rebase** → the CTO re-measures the both-merge and ⭐ **that is the certified number.** ⛔ **SF-25 is legitimately red in between and must not be smoothed** — non-strict xfail is **refused**, because it destroys the property that makes the table useful. ⭐ *A strict xfail going XPASS is the table announcing its own obsolescence.* |
| 2026-09-09 | ⭐ **Finding 19 downgraded on measurement, and the downgrade is the useful part.** `check_counts` **is** implemented and tested — ⛔ **only the fixture is missing**, so it is a **record defect, not a coverage hole, and it does not gate SF-25's merge.** ⚠️ My first routing implied the check itself was unexercised. `W14` stays with `SF-23` on **FND-04's surface** — same developer, same files, digests already being recomputed. |
| 2026-09-09 | ⛔ **Round-16 Finding 8 is superseded here, because it is in a merged handoff and a handoff is a record.** It asserted the `café`/`cafe` collision, ⚠️ **and the CTO has confirmed their own finding was wrong.** ⭐ The conclusion **widens** rather than falling: the real collision class is **punctuation, not accents**, and `Café`/`Cafe` are pinned as **clean** in the tests so nobody "fixes" the check toward the wrong example. **W4's precedent: the board row *is* the correction.** |
| 2026-09-09 | ⭐ **How finding 21 was found is worth as much as the finding.** It surfaced **because** the coordinator flagged that a carried clause had reached its developer only as a paraphrase. ⛔ **The worry was right and what it turned up was not in the clause** — which is the argument for checking a channel rather than only its payload. |
| 2026-09-09 | ⛔ **C6 CLOSED, and by its own logic it was not closed until the edit existed.** ⭐ **C6: *a ruling is made, is correct, and never reaches the artifact it governs*** — C5 one level up (C5 was *the gate asked the wrong question*; C6 is *the answer was right and was never delivered*), with the same tell: **nothing looks wrong.** Five instances, four found in one round, ⛔ **including my own 8 of 30.** The hole was in the rubric's own instrument: §8a's `ruled` outcome said *"with the ruling, or the handoff it went to"* — ⚠️ **and a handoff is never where a ruling lands, so the clause contradicted the standing rule inside the section meant to enforce it.** **Edited:** §8a now requires `ruled` to name the artifact it changed — Acceptance, epic clause, spec ruling, or convention doc, **never a handoff** — and the **wave-open checklist gains check 3**, run by the person who does the carrying. ⛔ **Deliberately not given to the reviewer:** the carry happens *after* the review, so that gate could not fire, and ⭐ **a gate that cannot fire is worse than none because it reads as coverage.** |
| 2026-09-09 | ⛔ **`docs/integration-catalogue.md` did not exist** — referenced by spec §9, by `SK-07`, and by at least three rulings, while `ls docs/` returned `conventions specs tasks`. ⚠️ **PO-Integration had ten durable entries written in its shape and nowhere to put them.** ⭐ **Created this round with eight entries** — the vocabulary degradation, verify-in-the-repository, the missing denominator, proxy-is-not-the-thing, the ordering trap, heading-level-is-not-role, the region that cannot be excluded, and the un-tagged fence. ⛔ **It is C6's sharpest instance: the artifact that never arrived was the artifact itself.** |
| 2026-09-09 | ⛔ **A carried ruling reached its developer only as a paraphrase, the same round the carrying mechanism was built.** ⭐ They wrote nothing to a guess and reported the gap — the right behaviour. **New protocol line: a carried ruling is quoted, not summarised**, and the developer reads the clause in the task document. ⚠️ **A paraphrase is how a ruling arrives *nearly* right, which is worse than not arriving: an absent ruling gets asked about; a nearly-right one gets implemented.** |
| 2026-09-09 | ⛔ **My gate call-site clause was not merely undelivered — it was wrong.** I wrote *"a test asserts `validate` calls the SF-08 gate on every string"*; ⚠️ **that tells one component to re-ask a question another component owns**, which ruling 17 had already settled upstream and finding 20 names as *"two readings from one parser"*. ⭐ **I recorded ruling 17 in the same edit session and did not reconcile the two.** **Verified and closed in substance:** `archive.document.parse` is the caller, `validate/corpus.py` handles `PersonalDataLeak` at three sites, and `test_a_document_the_personal_data_gate_refuses_is_recorded_too` asserts it end-to-end. Clause rewritten to assert the wiring **at the boundary, never behind it**. |
| 2026-09-09 | ⛔ **The `café`/`cafe` collision example is false, and I propagated it into SK-01 the day it was corrected.** **Measured:** `slugify('Café') == 'caf'`, `slugify('Cafe') == 'cafe'` — ⚠️ **an accent collapses to a separator, it is not deleted, so they do not collide.** ⭐ **The conclusion survives and gets stronger:** the real class is **punctuation, not alphabet** — `'Streams: an API'` and `'Streams, an API'` **both** give `streams-an-api`, which needs no exotic input and no reviewer would look twice at. ⛔ **A skill built to catch the accent case would miss the case that actually occurs.** `Café`/`Cafe` are pinned as **clean** in tests so nobody "fixes" the check to match the wrong example. Corrected in `E10` and in my own `E11` carry. |
| 2026-09-09 | ⛔ **An acceptance clause that had never been exercised.** `E10` names **six** invalid fixtures; `tests/fixtures/invalid/` holds **five** — no count-mismatch fixture. ⭐ **Ruled: build the fixture, keep the clause** (`W14` → SF-23). ⚠️ Dropping it would delete the only statement that the count check runs, and that check guards **silently lossy ingestion**, which SF-25's own definition calls the worst outcome available to this project. ⛔ **An acceptance naming a fixture that does not exist is unfalsifiable** — the untracked-artifact defect arriving in a *condition* instead of a build product. |
| 2026-09-09 | ⭐ **`SF-23` inherits a measured seam rather than a predicted one** (finding 20, carried **quoted**). An archive document carrying an unknown top-level `"exercise"` object **validates green — 0 findings, 0 unchecked** — because the digest is over `blocks`. ⛔ **Adding `exercise` must change the known-key set, not be tolerated** — otherwise a **typo** in the key is tolerated too and the graders are invisible. ⚠️ Owner is `archive.document.parse` (SF-02's surface), **not** `validate`. ⭐ **This is the exact failure the board predicted when it put SF-23 behind SF-25 with the same developer — now measured.** |
| 2026-09-09 | ⛔ **My `Profile` ruling is WITHDRAWN — the developer used my own argument against my conclusion and was right.** I ruled *the only caller writes it, because a capability with no caller is a guess*; they measured that the check needs **no new capability**, so one added now would have **no caller at all**. **Evidence:** `test_nothing_downstream_branches_on_a_profile_name` **1 failed → 1 passed**, zero profile names in `validate/`, zero profiles skipped. ⚠️ **The premise I ruled on was false**, and finding 18 adds that the check they replaced *reported a non-defect*. ⭐ **Three mechanisms now refused by checking whether the problem was still there** — X2's card pattern, the R7 allow-list, this. |
| 2026-09-09 | ⭐ **Q16 dissolved rather than rescheduled — and the defect was my own Log entry.** It said the media limit names are free to rename *"exactly until M2"* while `SF-32`, which owns them, is **M3**: ⛔ **a deadline no task could meet.** Ruled: **the names freeze when the first real manifest declares them, not at a milestone** — ⚠️ the same defect as the release-branch name, a status inferred from a label rather than an event — and ⭐ **`ISO-04` simply omits `media`**, which `SF-02` already asserts is committed-with-defaults. ⛔ **`SK-07` must be told, because it generates manifests**, and a generator emitting an unneeded key freezes that key on everybody. |
| 2026-09-09 | ⭐ **Q18 answered from a standing ruling rather than invented.** §7's three states and C5 already give it: ⛔ **a corpus with no graders is complete at M4, not short.** ISO's definition of done is **the reading floor**. ⚠️ **Q8's real ambiguity ruled:** §11.2 sits above M4's *"it is served"* — ⛔ **and "it is served" is not a condition for a corpus that is never served**, or a complete corpus waits on a milestone it has no business in, which is C5's error one level up. |
| 2026-09-09 | ⛔ **`W15` — an R3 violation and an R7 exposure, both created by *tooling* rather than by anybody's edit.** A `graphify` git hook appended `graphify-out` to the **ISO repository's root ignore file** on an ordinary commit, unrequested, ⚠️ **in the one repository where R3 is absolute** — and `.claude/settings.json` carries a machine-local absolute path. ⭐ **This repository checked and clean, not assumed:** zero tracked files carry the real home path, our ignore entry came from `FND-01`'s scaffolding, no hooks installed. ⛔ **The rule is written in `graphify.md` and `SK-07` item 9 and is enforced by nothing that runs**, and `OPS-05` checks at **build** time while this happens at **index** time. |
| 2026-09-09 | ⭐ **SK-01 gains two traps measured in real material, while it is still unassigned — and both flatter the checker.** **Trap 3:** a filename sort puts **35 of 38 units at the wrong index**; count right, pages render, links resolve, nothing raises — ⚠️ **and unit 1 of each group stays first, so the page anybody spot-checks is correct.** ⛔ The only order oracle is the three aggregates, **precisely the files `content.exclude` deletes.** **Trap 4:** **53.7% of a curriculum document is a copy of another document's heading tree**, invisible to any whole-file digest, in a file that **can never be excluded** — so ⛔ **a parser keyed on heading level emits 21 containers for a 3-container corpus and raises nothing.** ⭐ **Detect and report; do not remedy** — the duplicate is a *region*, and the manifest is not growing sub-file exclusion. |
| 2026-09-09 | **`W8` sequenced to Developer 1, after SF-23** (ruling 21). ⛔ **It cannot ride in `SF-12`'s branch: `SF-12`'s tests would be the first thing the new runtime runs, so a green `SF-12` certifies itself** — C5's shape, failing unfalsifiably. Not Developer 2 — no shared surface (`docker/dev/`, not `tools/quality/`) and their lane is full. ⭐ Acceptance is one number: `-rs` reports **8** skips, not 46, none naming a missing JS runtime, ⚠️ **and the 8 must stay skipped** — a run reaching zero has broken the recursion guards. |
| 2026-09-09 | ⛔ **The header named a release branch that does not exist and never did.** `release/m1-one-page` has no ref; all eleven M1 merges landed on `release/m0-foundations`. ⭐ **Ruled: M1 continues there, not re-cut mid-wave** — five agents' bases and the only measured-green number are on it, and a rename that buys tidiness and costs five bases is not a mid-wave trade. ⚠️ **New sub-shape named: the branch's *name* was read as its *scope*.** A milestone-named release branch is a claim with an expiry date, so ⛔ **the naming scheme is retired rather than a better name chosen** — a name that encodes a status stores a status in the one place nothing can update it. |
| 2026-09-09 | ⛔ **Status cells corrected against `git log`: SF-08, SF-11 and SF-33 were `in-progress`/`todo` and are all merged** (`f9be376`, `56caba0`, `0e59645`) while the header three lines above said step 1.1 was complete. ⚠️ A document that contradicts itself in two screens was read as a status by whoever dispatched from it. |
| 2026-09-09 | ⭐ **The finding of the round, and it is against the mechanism rather than any task: ruling is not carrying.** The `[structural]` sweep returned **32 findings**; **30 were ruled** and ⛔ **8 of those will still evaporate**, because they reached no board row, no epic clause and no trigger. ⚠️ **It is the C5 meta-finding one level down, in nearly the same words:** then, *the protocol said to write findings down and never said anyone had to rule on one*; now, ⛔ **the protocol says to rule and never said anyone had to carry the ruling.** Of the three legal outcomes — ruled, scheduled, accepted — **only two name a destination.** ⛔ **Rule tightened: a finding is dispositioned when its outcome has a destination.** A CTO ruling is the decision; ⭐ **delivery is the PO's, and this is the PO's own gap.** The eight are now **W6–W13**. |
| 2026-09-09 | ⛔ **Wave-open check 1 FAILED: the index was stale, and I fixed it.** Built at `220ea4b`, **15 commits and 30 files behind** the tip. ⭐ **Measured by content, not by clock:** an incremental rebuild added **224 nodes and removed 18**, and the additions are exactly the merged-but-unindexed tree — `unit/content.py` (30), `test_content.py` (38), `unit/sections.py` (8), `unit/errors.py` (6), `placement/names.py` (6), `container/fields.py` (7). ⚠️ **Every agent this wave would have queried a graph missing most of SF-09.** Rebuilt with `graphify update` — incremental, **no LLM, no API key**, under a minute; `built_at_commit` now `9ad45a2`; R7-verified, **zero** home paths. |
| 2026-09-09 | ⭐ **A standing caveat retired by measurement: the graph health warning is gone.** `graphify diagnose multigraph` after the rebuild reports **0 dangling, 0 collapsed, 0 self-loops, 0 missing endpoints** — it was 203 / 192 / 1. ⛔ Any briefing still carrying *"203 dangling edges"* is quoting a record as a status. ⚠️ **The caution survives on other grounds and must not be read as *the graph is complete*:** code↔prose is still **510 of 6,463 (7.9%)**, 502 of them incidental mentions, and `path "R7 …" "assert_clean()"` **still returns no path, even undirected.** |
| 2026-09-09 | ⛔ **FND-07 must not use mtime, and the two errors that settled it are worth more than the ruling.** The coordinator measured a false FAIL on a current index — git rewrites mtimes on merge, and ⚠️ **`git worktree add` resets every one**, so the check would fail inside **every trial-merge worktree the rubric requires** and ⛔ **break the gate built to catch C5.** ⚠️ **But their counter-check was also wrong**: it confirmed **one** symbol and generalised, while the index was stale by 224 nodes. ⭐ **Both failures are one shape — a proxy read as the thing.** mtime is a proxy for content; one symbol is a proxy for the tree. ⛔ **A sample is not a census.** ⭐ **And the mechanism already existed and nobody had read it:** `graph.json` carries `built_at_commit`. Ruled and carried: `git diff --quiet <built_at_commit> HEAD -- src tools docs`, ⛔ **never `!= HEAD`** (fails after every commit, including one that touches only this board), plus a test that touches every file and asserts the verdict does not move, so a clock cannot be reintroduced. |
| 2026-09-09 | ⭐ **Step 1.3 assigned on the collision-pair rule, with both surfaces measured rather than guessed.** **Lane A, Developer 1: SF-25 → SF-23** — they share *what is legal inside a practice archive document*; ⛔ split, they disagree about whether `validate` knows `exercise` exists and a corpus validates green with its graders invisible. **Lane B, Developer 2: W1+W2 (+W3, +W6) → FND-07** — ⚠️ **measured from `handoffs/SF-03.md` finding 6's own words**, which place W2 *"beside the R7 sweep in `tools/quality`"*, and FND-07 registers in the same five-entry `CHECKS` tuple. ⛔ Two agents adding two entries to one tuple in parallel is C5 with a contract instead of a line length. **SK-01 queued** to the next free slot. |
| 2026-09-09 | ⛔ **W3's trigger was a task that waits forever — B1's defect, returning.** It was routed *"with the next fixture touch"*, and the next fixture touch is now **SF-23's**, which is the other developer's. ⭐ **A trigger naming somebody else's work is not a trigger.** Dispatched now, on its own, **ahead of SF-23** — which also removes the only cross-lane collision, since both touch `tests/fixtures/` and the split digest modules, and ordering them in time is cheaper than ruling about them. |
| 2026-09-09 | ⛔ **SF-23 has no fixture for the state it exists to encode.** Measured: `grep -rln '"exercise"' tests/fixtures/` returns **nothing**, while two `practice-1.json` exist. Of §7's three states the fixtures carry **none** and **ungraded**; ⛔ **graded has no fixture at all.** ⭐ **SF-23 ships it itself, reversing the step-1.1 precedent deliberately** — that precedent gated a critical-path task on another developer's fixture and the CTO overruled half of it. ⚠️ Additively (R3), digest recomputation included, not a follow-up. |
| 2026-09-09 | ⭐ **New dependency inside step 1.3, and it is C5's ruling paying for itself in one round.** `structure.py:109` branches on a placement profile name and fails `SF-03`'s `ast` test **in another package** — ⛔ **only the trial merge could find it**, because each branch is correct alone, which is the only situation C5 occurs in. **Decision: Developer 1 grows `Profile` inside SF-25's branch**, because ⭐ **the only caller writes it** and a capability designed with no caller is a guess. ⛔ Not Developer 2, despite `placement/` being their step-1.1 surface — **that is the coupling the CTO overruled me for in step 1.1**, and applying the correction is the point of having taken it. ⚠️ Reviewed as a **contract change on SF-03's surface**, not a `validate` internal, and `E01` gains a carried note. |
| 2026-09-09 | **Merge order ruled: W1+W2 before SF-25** (round 17). The boundary is upstream — `validate` does not scrub, W1 is the fix, and `validate`'s end-to-end poison test is not a duplicate of W2 because the vantage point differs (§10b, third instance). Measured: **6 of 10 poison shapes reproduced an identifier in a report; 10 of 10 clean with W1 prototyped**, diagnosis intact. |
| 2026-09-09 | ✅ **R21 register: overlay `content.json` CLOSED** — `content_api` minted, in `CONTRACT_FIELDS`, asserted by name, 23 occurrences. ⭐ **Verified in the tree rather than inherited from the handoff.** ⛔ **And the register was stale by *two* rows, not one** — `consuming_api` is in §R9 already. **Three genuinely open, none due in M1.** Ruled: ⭐ **the register is derived from §R9's `open` entries, not kept as a second copy**; the rows survive only for the reasoning §R9 does not carry. |
| 2026-09-09 | ⛔ **C5's contradiction closed in one place.** The defects table said *"CTO to rule / open"* three screens above a section reading *"✅ RULED"*. ⭐ **The table now carries a pointer and the section carries the reasoning** — and the general rule was ruled with it: **a status table points, it never restates.** |
| 2026-09-09 | ⭐ **Four instances, one defect, and the pattern is now the finding rather than the four corrections.** The release branch, the index, the C5 row, the R21 register — ⛔ **a summary that restates a status owned elsewhere is a copy, and it goes stale in exactly one direction: the summary is what people read, the source is what people update.** ⚠️ **Three of the four are in this file**, which is why the rule is written into its own editing rules. Same argument as C2's *a convention that repeats its own definition is the defect it polices elsewhere*, the single block-type list, the single size ceiling, the single review base. |
| 2026-09-09 | ⛔ **`ONBOARDING.md` ruled: it does not enter the repository.** Untracked at the root, it states three things that are false — *"nothing implemented yet"*, *"composes them as submodules"*, *"ask a teammate for clone URLs"* — and ⚠️ teaches `graphify query` as *the* command, ⛔ **the exact habit that produced the 31-of-33 defect.** ⭐ **Disqualifying independently of all that: it carries an embedded `<!-- INSTRUCTION FOR CLAUDE -->` block**, and tracking it would put instructions to agents, authored by nobody here, at the repository root. ⚠️ **Not deleted** — it is untracked, so it is the user's file and not repository state, and ⭐ **the dichotomy in the question was false.** |
| 2026-09-09 | **`fix/SF-03-label-seam` and `feat/SF-09-unit-document` both merged on APPROVE** — ⭐ **no branch is unmerged.** Step 1.3 is SF-25 (part-written), SF-23, SK-01, and the new **FND-07**. 1797 passed on the host. |
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
