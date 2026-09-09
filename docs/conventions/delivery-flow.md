# Delivery flow

How work moves through this team. `agent-protocol.md` says how a **task** is
worked and handed off — read it first; this document does not repeat it. What
follows is only what happens **around** the task: branches, the review gate, the
board, and the channel between the two product owners.

## Roles

| Role | Owns |
|---|---|
| **PO-Framework** | task assignment, priority, task modification, status truth, `../tasks/BOARD.md` |
| **CTO** | technical authority. Reviews every change before it merges to a release branch |
| **Developer** | one task at a time, on one branch |
| **PO-Integration** | one corpus repository, and the findings it produces |

⭐ **A product owner does not write framework code, and a developer does not
change a task's scope.** Refining a task is expected — it goes through the PO and
is recorded on the board. Silently expanding one is not (`agent-protocol.md`).

## Branches

| Kind | Name | Branches from | Merges to |
|---|---|---|---|
| Release | `release/<milestone>` — e.g. `release/m0-foundations` | `main` | `main`, when the milestone closes |
| Task | `feat/<TASK-ID>-<short-slug>` — e.g. `feat/FND-01-scaffolding` | the release branch | the release branch, **after review** |
| Non-code | `chore/<slug>` — e.g. `chore/po-board` | `main` | `main` |
| Integration | `release/studyforge-integration`, in the corpus repository | that repository's default | that repository only. **Never into `studyforge`** |

One task, one branch, one owner. ⛔ **No task branch merges into another task
branch** — that is how two half-finished contracts become one unreviewable diff.
If your task genuinely needs another's unmerged work, that is a dependency the
board got wrong: say so, do not vendor it.

⛔ **No personal data in a branch name, a commit message or a log** (R7). No
absolute home path, hostname, account id, name or email — anywhere, including
pasted command output in a review.

## The review gate

⛔ **Nothing merges to a release branch unreviewed.** The CTO is the only
approver. This is not a formality: M0 is where every later task's assumptions get
fixed, and a defect here is discovered simultaneously by five agents in M1.

**What a developer presents for review — all of it, or the review does not
start:**

1. **The task's Acceptance conditions, run, with output pasted.** Every
   condition in the epic document, in order, each with the command that produced
   it and what it printed. ⭐ **Evidence before assertions.** "Tests pass" is not
   evidence; the runner's output is. A condition phrased as a *failure* — "the
   size check fails on a deliberately oversized module" — is proved by showing the
   failure, not by asserting it would occur.
2. **The handoff file**, `../tasks/handoffs/<TASK-ID>.md`, in the format
   `agent-protocol.md` gives. ⛔ **A task with dependents and no handoff is not
   done** and is not reviewable.
3. **The diff**, and nothing in it outside the task. A defect noticed elsewhere is
   a **finding** in the handoff, not a line in the diff.
4. **A named self-check against the rulings the task touches** — at minimum R7
   (personal data), R11 (size), R12 (tests mirror source).

**The CTO's verdict is one of three:** `approved` (PO merges, or the CTO does),
`changes requested` (named, each tied to a ruling or an acceptance condition), or
`rejected — re-plan` (the task as written cannot be met; it returns to the PO as a
planning defect, which is a legitimate and cheap outcome).

⚠️ **A reviewer who cannot run the acceptance commands has not reviewed
anything.** If a condition has no runnable form, that is the finding.

## The board

`../tasks/BOARD.md` is the **single source of truth** for status. Nowhere else —
not a handoff, not a commit message, not a chat line — makes a task done.

- **The PO writes the board.** Developers do not edit it; they report, and the PO
  records. This keeps status one voice rather than five.
- **A status change is one cell.** Do not restructure the tables to record an
  event; add a line to the **Log** instead.
- **Transitions:** `todo` → `in-progress` when assigned and started ·
  → `in-review` when the developer presents the package above ·
  → `done` **only** on the CTO's `approved` **and** the merge to the release
  branch · → `blocked` at any time, and a `blocked` row must name a **precise
  unblocking condition**, not a symptom.
- ⛔ **`done` never means "the code is written".** It means reviewed, merged, and
  the acceptance output is on the record.

## The two-PO channel

The framework and an integration are run by two product owners. The seam between
them is deliberately narrow, and the spec is strict about it.

⛔ **The integration side's only channel to the framework is questions and
findings — never patches.** (§12.) The integrator does not modify `studyforge`.
Anything the framework cannot do is filed as a **finding** against the task,
contract or skill that should have covered it. ⭐ A test of extensibility run by
somebody who can edit the thing being tested measures nothing — and an integrator
who patches their own way past a shortfall has fixed one repository and taught
the framework nothing.

⛔ **No integration-side task, context field or acceptance ever cites a path
inside the extraction source** (R20). `CS/` and `CSD/` are framework-side
shorthand only. What an integrator needs is carried **in this repository** — as a
ruling, a contract, a skill, or the integration catalogue (§9). ⛔ **No skill
sends an integrator there to find out how something was done.** The source is
moving, it does not generalise, and a consumer that reads it directly puts the
expertise nowhere.

**A finding is filed like this**, in `../tasks/handoffs/`, named for what it is
against rather than for who found it:

```markdown
# FINDING <date> — <one line>

**Against:** the task, contract, ruling or skill that should have covered this.
**What was needed:** the thing the corpus actually required.
**What the framework offered:** and where it fell short.
**Worked around by:** what was done instead, in the corpus repository only.
**Cost:** what a second source would have to retype (R19).
```

⭐ **The finding count is the yield, not the failure.** An integration that
reports none has not been conducted honestly.

**What flows the other way** — framework → integration — is contracts, never
instructions to go and look: the archive contract (`studyforge validate`, SF-25),
the placement contract (`studyforge plan`, SF-31), and each shared component's
`consuming.json` (TC-05, E13). ⛔ **A consumer never reads a Dockerfile to work
out how to run something**; that is the first step toward forking it (R18). If an
integrator has to, the missing `consuming.json` is the finding.

**Durable findings are distilled into the integration catalogue** in this
repository, so the next integration starts further along than the last. A finding
that stays in the corpus repository has taught nobody.

## Escalation

`agent-protocol.md` lists when an agent stops and asks. Two additions here:

- **A developer escalates to the PO**, not to another developer. Cross-task
  negotiation between developers is how two contracts quietly diverge.
- **The PO escalates a technical disagreement to the CTO**, and records the
  ruling on the board's Log. ⛔ **A ruling that is not written down did not
  happen** — that is the whole reason R1–R20 exist as a numbered list.
