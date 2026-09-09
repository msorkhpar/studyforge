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

---

## M0 — Foundations

> **Milestone closes when:** an agent can pick up any M1 task without inventing
> a layout, hunting for a graph, or building its own fixtures.

**Step 0.1** — FND-01 ✅, FND-02, FND-04 ✅ · **Step 0.2** — FND-03, FND-06, FND-05a

⭐ **Step 0.1 is done bar FND-02, and step 0.2 is fully unblocked.** Three tasks
remain in M0, none of them blocked, and none of them on M1's critical path.

| Task | Title | Owner | Branch | Status | Blocked on | Closes when |
|---|---|---|---|---|---|---|
| FND-01 | Repository scaffolding and quality floor | Developer 1 | *merged* | ✅ `done` | — | **Closed 2026-09-09.** CTO verdict APPROVE after changes. `tools/quality/` (size, mirror, docstrings, style) + `tests/test_quality_floor.py`; `tools/` excluded from packaging; zero runtime dependencies. ⚠️ **One clause shipped `Blocked`, not passed:** lint — ruff is configured and declared as the `lint` extra, and `FND-03` is what runs it |
| FND-02 | Knowledge index | *unassigned* | `feat/FND-02-knowledge-index` | `todo` | — | Both graphs build, the `studyforge` one **rebuilt at the M0/M1 boundary**; three representative queries recorded in `../conventions/graphify.md`; rebuild command documented and incremental; `JS/` ignored via `graphify-out/.gitignore` containing `*` and `git status` there clean |
| FND-03 | Development and test container | *unassigned* | `feat/FND-03-dev-container` | `todo` | — | Full suite runs in the container from a clean checkout with **no host Python**; ⭐ FND-01's two skipped ruff tests **run and pass**, closing its blocked lint clause; suite and quality floor separately invocable; the same commands run on the host; no network needed to run tests |
| FND-04 | Shared contract fixtures | Developer 2 | *merged* | ✅ `done` | — | **Closed 2026-09-09.** CTO verdict APPROVE on every rubric check. 7 corpora, 43 files, 22 tests, re-run green post-merge |
| FND-05a | Workspace, workflow and the first submodule | *unassigned* | `feat/FND-05a-workspace` | `todo` | — | Workflow document covers clone, update, advance and the two-commit rule; non-recursive clone fails pointing at the documented command; `corpora/java-senior` pinned and verified; no absolute path in any tracked file |
| FND-06 | Repository personal-data check | *unassigned* | `feat/FND-06-r7-check` | `todo` | — | A fifth entry in `tools/quality`'s `CHECKS`: exits non-zero on a purpose-built violating file, zero on the tree; the sanctioned-directory registry is asserted by a test; ⛔ writes no derived identifier anywhere, proved by a test on the refusal message |
| — | Review rubric + M0 readiness audit | CTO | *merged* | ✅ `done` | — | **Closed 2026-09-09.** `../conventions/review-rubric.md` plus four rulings |
| — | Board + delivery flow | PO-Framework | `chore/po-board-m0-update` | `in-progress` | — | Board reflects the first review round; the ruled task edits are carried into `docs/tasks/` |

**Out of M0:** `FND-05b` — composing `studyforge`, `TC/` and `NS/` — moved to
**M5**, step 5.5. See **B1**.

### Open items

**C1 — FND-01, closed.** The one change requested — a regression test for the
`.gitignore` fixture negation, asserted in **both** directions — landed and the
task merged. ⚠️ **One acceptance clause shipped `Blocked`, and that is not
`done`:** no `ruff`, `black`, `uv` or `poetry` exists on the machines available,
so "lint and format run clean" had nothing to run. Ruff is configured and
declared as the `lint` extra, and two tests **skip with a message naming it**
rather than passing quietly. ⛔ **`FND-03` is the task that closes this**, and
until it does, R13-adjacent formatting is unenforced. The clause is not dropped —
an unenforced format erodes exactly like an unenforced ceiling.

**B1 — FND-05b, blocked, and not an M0 problem.** ⚠️ **The earlier note on this
board said no repository has a remote. That was wrong and the CTO caught it by
counting.** Measured 2026-09-09: `JS/`, `CS/`/`CSD/`, `ISO/` and `SPARQL/` each
have one. ⛔ **Only `studyforge` has none** — R18's "every component has its own
remote" is currently false of the one component the parent exists to pin — and
⛔ `TC/` and `NS/` **do not exist**, since E12 and E13 create them at M5 and M3.

Two consequences. First, most of `FND-05` was always deliverable, which is why it
split rather than sat red: `FND-05a` lands the parent, the whole workflow
document, the clone guard and the one submodule that can be pinned today.
Second, `FND-05b`'s unblocking condition is precise and **one half of it is not
an agent's to take**: an empty remote repository created by the owner for
`studyforge`, plus E12 and E13 existing. ⛔ The URL lives in untracked
`.git/config` and no agent writes it into a document (R7).

⚠️ Neither local-path workaround survives: an absolute path in `.gitmodules`
writes a home directory into a tracked file, and a relative URL resolves against
the parent's own remote, which does not exist.

### Sequencing the unassigned tasks

**Order: FND-02 → FND-03 → FND-06 → FND-05a.**

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
4. **FND-05a last, and unblocked.** Nothing in M1 imports the parent workspace,
   so it is the one M0 task that can slip without stopping anybody.

---

## Open questions — owners and deadlines

⚠️ **These block later epics, not M0.** Each is a decision nobody has taken, each
has a task that cannot start without it, and the deadline is that task — not a
date. ⛔ **A ruling that is not written down did not happen**: each is answered as
a CTO ruling in a handoff, and the answer is carried into the task by the PO.

| # | Question | Owner | Must be answered before |
|---|---|---|---|
| Q1 | **`<details>` is ruled in two opposite and both-wrong directions.** CodeSignal flattens a disclosure into ordinary blocks — text kept, hiding destroyed, so a SPARQL exercise answer is shown outright. `FND-04` chose a raw `html` block — hiding kept, but the speakable contract then reads the answer aloud while the page still shows it collapsed. **Both fail, oppositely.** | CTO | **SF-07 (M1 step 1.1)** — and E04. ⛔ **The most urgent of the three: SF-07 is starting now.** |
| Q2 | **§7's exercise declaration has no home.** `main_path`, `test_path`, `run_command`, `test_command`, `provenance`, `trust` name no document, while every other contract in §4–§6 names its own. **R5 is what stops a generated grader being rendered as authoritative, and there is nowhere to write the field that turns it on.** | CTO | **SF-23 (M1 step 1.3)** — before E06 builds, not during |
| Q3 | **`container.json` has two owners.** §6 says an adapter generates it; `SF-05` says it is hand-authorable and never written by the render pipeline. Reconcilable — one clarifying sentence in `SF-05` settles which producer owns which case. | CTO | **SF-05 (M1 step 1.2)** |

⭐ Q1 and Q2 are the same shape and worth naming as one: **a contract that R5 or
the reading floor depends on, which the spec describes but does not locate.** A
task that discovers this while building will invent a location, and an invented
location is the thing R9's versioning cannot fix later.

---

## Next up — M1 step 1.1

> M1 closes when a unit page from the `depth1` fixture opens in a browser with
> styles and highlighting, over `file://`. **M1 is the riskiest milestone** —
> every contract meets every other one for the first time.

| Task | Title | Prerequisite | Startable? |
|---|---|---|---|
| SF-01 | Logical address model | FND-01 ✅, FND-04 ✅ | ⭐ **now** — and it is on the critical path |
| SF-02 | Corpus manifest | FND-01 ✅, FND-04 ✅ | **now**, but ⚠️ carries **X1**, the ISO include/exclude question |
| SF-07 | Block vocabulary and Markdown reader | FND-01 ✅, FND-04 ✅ | ⛔ **not until Q1 is ruled** |
| SF-08 | Personal-data gate | FND-01 ✅, FND-04 ✅ | **now**, but ⚠️ carries **X2**, the ISO `assert_clean` question |
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
- ⛔ **Three of the five carry an unanswered question** (Q1, X1, X2), and with the
  prerequisites already met **the questions are now the only thing holding step
  1.1 back.** Getting them ruled is this PO's highest-value work — an answer
  arriving mid-task is a re-plan, and one arriving after is a rework of a
  versioned contract (R9).
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

| # | Question | Lands in | Deadline |
|---|---|---|---|
| X1 | **`corpus.json` has no include/exclude field**, so a corpus structurally cannot declare files out. ISO ships three whole-series aggregates that are digest-identical concatenations of the per-unit files, so a `src/*.md` glob ingests everything **twice**. C2 demands the countermeasure and §4's schema cannot express it. | **SF-02** | ⛔ **Before SF-02 is assigned** — M1 step 1.1. This is a schema change, and a schema is the one thing R9 makes expensive to change afterwards. |
| X2 | **`assert_clean` will refuse the ISO corpus entirely.** 96 card-shaped digit strings such as a 16-digit test PAN are that corpus's **core teaching content**, and R7's gate refuses rather than rewrites, with no escape hatch. | **SF-06 / SF-08** | Before SF-06 ships |

⚠️ **X2 is the harder of the two and it is not a bug in the gate.** R7's refusal
is deliberate and `FND-06` is about to enforce the same shape repository-wide. The
question is whether "card-shaped digit string" is personal data at all when the
values are published test numbers in a payments tutorial — and if the answer is a
declared exemption, ⛔ it must be **manifest data read by the gate**, never a
pattern hardcoded for one corpus (R1, and the same argument R3 already won for
`permitted_edits`). ⭐ An exemption that names a corpus is the framework learning
about a source.

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
