# Board — live status

**Single source of truth for what is in progress and what is done.** Owned by
the framework Product Owner. Task *definitions* live in the epic documents
(`E00`…`E13`); this file carries only **state**.

**Milestone in flight: M0 — Foundations.**
**Release branch: `release/m0-foundations`.** Developers branch off it, the CTO
reviews, only reviewed work merges back. Flow: `../conventions/delivery-flow.md`.

*Statuses:* `todo` · `in-progress` · `in-review` · `blocked` · `done`.
*Editing rule:* a status change is one cell. Do not restructure rows.

---

## M0 — Foundations

> **Milestone closes when:** an agent can pick up any M1 task without inventing
> a layout, hunting for a graph, or building its own fixtures.

| Task | Title | Owner | Branch | Status | Blocked on | Closes when |
|---|---|---|---|---|---|---|
| FND-01 | Repository scaffolding and quality floor | Developer 1 | `feat/FND-01-scaffolding` | `in-progress` | — | Trivial package + mirrored test green from a clean checkout; size check **fails** on an oversized module and **passes** with a justified opt-out; lint and format clean; `pyproject` declares zero runtime dependencies |
| FND-02 | Knowledge index | *unassigned* | `feat/FND-02-knowledge-index` | `todo` | — | Both graphs build; three representative queries recorded as examples in `../conventions/graphify.md`; the rebuild command is documented and works incrementally; `graphify-out/` is ignored |
| FND-03 | Development and test container | *unassigned* | `feat/FND-03-dev-container` | `todo` | FND-01 merged to the release branch | Full suite runs in the container from a clean checkout with **no host Python**; the same command runs on the host; no network needed to run tests |
| FND-04 | Shared contract fixtures | Developer 2 | `feat/FND-04-fixtures` | `in-progress` | — | `depth1/` and `depth2/` complete and internally consistent; every block type appears at least once; each invalid fixture violates **exactly one** rule, named in a comment; fixtures small enough to read |
| FND-05 | Workspace and submodule composition | *unassigned* | `feat/FND-05-workspace` | `blocked` | **B1** — no component has a git remote | Recursive clone on a clean machine yields every component at its pinned commit; component change + parent pin reproducible by another checkout; a non-recursive clone fails pointing at the documented command; the workflow document covers clone, update, advance, and the two-commit rule |
| — | Review rubric + M0 readiness audit | CTO | `chore/cto-rubric` | `in-progress` | — | Rubric published; every M0 acceptance condition has a named command that produces green/red output |
| — | Board + delivery flow | PO-Framework | `chore/po-board` | `in-review` | — | This file and `../conventions/delivery-flow.md` exist and the CTO has read them |

### Blocking reasons

**B1 — FND-05.** `studyforge` and every sibling repository have **no git
remote**, and a submodule records a *URL* plus a commit. Two of the components
R18 names (`code-server-toolchain`, `narrate-service`) do not exist yet — E12 and
E13 create them. So the parent can be stood up today only against local
filesystem paths, which makes "a recursive clone on a clean machine" — the task's
own first acceptance condition — unverifiable.

⛔ **Do not assign FND-05 until this is decided.** It is a decision, not work.
**Unblocking condition, precisely:** the CTO rules on the submodule URL for a
remote-less component — either (a) each component gains a reachable remote, or
(b) the workspace adopts a declared bare-mirror convention inside the workspace
root and FND-05's acceptance is re-worded to test *that* rather than "a clean
machine" — **and** FND-05's component list is cut to the components that exist,
with re-pinning TC and NS recorded as follow-on work under E12/E13.

⚠️ **M0 can close without FND-05.** Nothing in M1 imports the parent workspace;
it is R18's *reproducibility* artifact, not a prerequisite of any framework task.
If it is still blocked when FND-01…04 are done, M0 closes and FND-05 carries
into M1 rather than holding the milestone hostage.

### Sequencing the three unassigned tasks

**Order: FND-02 → FND-03 → FND-05.**

1. **FND-02 first, and it can start now.** `graphify` is on PATH and needs
   nothing from any other task. It is also the only M0 task that *repays* the
   others: R14 is what keeps every downstream context budget honest, and the
   Java repository's graph (212 documents, 345 classes) is the single largest
   saving available to M6. ⚠️ **Split its two halves by time.** The
   `Claude-senior-java-engineer` graph is buildable today and is the valuable
   one. The `studyforge` graph built today would index a tree with no `src/` —
   "a state nobody will see again", which is the exact failure the task's own
   rebuild rule warns about — so that half is rebuilt **at the M0/M1 boundary**,
   after FND-01's layout exists. The rebuild is the deliverable's proof, not an
   afterthought.
2. **FND-03 second, the moment FND-01 merges.** Docker is reachable, so the task
   is not blocked on the environment — it is blocked on *content*. Its acceptance
   is "the full test suite runs in the container", and until FND-01 lands there is
   no suite, no test runner and no lint invocation for the image to run. Starting
   it earlier produces an image that has to be rewritten the day FND-01 chooses a
   toolchain. ⭐ It is also where the **missing linter** is solved (see findings):
   no `ruff`/`black`/`uv`/`poetry` exists on the host, and this image is the right
   place for a dev-only dependency to live.
3. **FND-05 last, and blocked meanwhile.** See **B1**.

---

## Next up — M1 step 1.1

> M1 closes when a unit page from the `depth1` fixture opens in a browser with
> styles and highlighting, over `file://`. **M1 is the riskiest milestone** —
> every contract meets every other one for the first time.

| Task | Title | Unblocked by | Ready when M0 lands? |
|---|---|---|---|
| SF-01 | Logical address model | FND-01 (layout), FND-04 (fixtures) | **yes** |
| SF-02 | Corpus manifest | FND-01, FND-04 | **yes** |
| SF-07 | Block vocabulary and Markdown reader | FND-01, FND-04 | **yes** |
| SF-08 | Personal-data gate | FND-01, FND-04 | **yes** |
| SF-11 | Page assets | FND-01 only | **yes — and earliest** |

All five declare `Depends on —`; their only prerequisite is M0 itself
(`README.md`, *Standing rules*). Two consequences worth planning around:

- ⭐ **SF-11 is startable on FND-01 alone.** It touches no fixture, so it is the
  right task to hand the first developer who frees up if FND-04 is still moving.
- ⚠️ **Four of the five consume FND-04.** If the fixtures slip, step 1.1 becomes
  a one-task step. That is the reason FND-04 is staffed as a `pair` and is the
  milestone's real critical path, not FND-01.
- ⭐ **SF-01 is on the project critical path** (FND-01 → SF-01 → SF-03 → SF-31 →
  SK-02 → …). Assign it the day M0 closes; do not let it queue behind SF-02.

---

## Cross-repo — the ISO-8583 integration track

| | |
|---|---|
| **Repository** | `ISO/` (`ISO-8583-jPOS-tutorial`) |
| **Owner** | PO-Integration |
| **Branch** | `release/studyforge-integration` |
| **Status** | `in-progress` — reconnaissance and delivery plan |
| **Closes when** | A milestone-ordered backlog exists whose every task ends in something a person can be shown, with acceptance the framework can evaluate |

**What this track can and cannot depend on right now.**

- ⚠️ **It has no definition of done yet.** `studyforge validate` (SF-25) is the
  archive contract (R2) and lands at M1; `studyforge plan` (SF-31) is the
  placement contract and lands at M2. Until then the integration side is
  **reconnaissance and planning only** — it cannot produce an archive that
  anything can judge, and an adapter written against a contract that does not
  exist is an adapter written against a guess.
- ⚠️ **SK-08, the delivery-planning skill, does not exist** — it is M2. So this
  plan is being written by hand. ⭐ **Every step of it that SK-08 should have
  generated is a finding against SK-08** (R19), and those findings are this
  track's most valuable output before M2, because they arrive while SK-08 can
  still be shaped by them.
- **Whether this corpus enters the execution track is a §11.0 question**, and it
  is decided by the material, not by ambition. ⛔ **A corpus with no graders is
  complete at M4, not short** (C5). Recon should answer it explicitly rather than
  assume containers.

**The channel between the two POs — encoded in `../conventions/delivery-flow.md`
and non-negotiable.**

- ⛔ **Questions and findings, never patches.** The integration side does not
  modify `studyforge` (§12). A framework shortfall is filed as a finding against
  the task or skill that should have covered it.
- ⛔ **No task, context field or acceptance on that side ever cites a path inside
  the extraction source** (R20). `CS/` and `CSD/` are framework-side shorthand
  only. What an integrator needs is carried **here** — as a ruling, a contract, a
  skill, or the integration catalogue (§9).
- **Findings land in this repository**, and the durable ones are distilled into
  the integration catalogue so the *third* source starts further along than the
  second. A finding that stays in the corpus repository has taught nobody.

---

## Log

| Date | Change |
|---|---|
| 2026-09-09 | Board opened. M0 in flight: FND-01 and FND-04 assigned, FND-02/03 sequenced, FND-05 blocked on **B1**. |
