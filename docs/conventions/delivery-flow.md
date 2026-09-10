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
| Fix | `fix/<slug>` — a correction to merged work, not a new task | the release branch | the release branch, **after review** |
| Integration | `release/studyforge-integration`, in the corpus repository | that repository's default | that repository only. **Never into `studyforge`** |

⛔ **Nothing is ever pushed to any remote. Everything stays in local
repositories.** This is a standing user decision and it is permanent — ⛔ **no
agent runs `git push`**, to any remote, on any branch, for any reason, and no
agent creates a remote or asks for one to be created. Branches, merges and
reviews all happen locally.

⚠️ **It is written here so nobody re-derives it from an absent remote and
concludes something is broken.** It also has consequences beyond workflow, and
they are on the board rather than in this document: the submodule composition
`FND-05a` was to build has no legal form under it, and R18's *"the parent's
recorded submodule commits are the version pin"* — the sentence R9's
cross-repository reproducibility rests on — has lost its mechanism. ⛔ **A working
practice that quietly voids a ruling is a finding, not a preference**, and it is
recorded as one.

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

⭐ **The rubric is `review-rubric.md` and it is the gate, not a guide.** It
carries one runnable command per ruling and the three verdicts. Read its §9
before you finish a task: your Acceptance bullets get pasted into the review with
the command and its output beneath each one, and ⛔ **restating a condition is not
meeting it**. What follows here is the process around that document, not a second
copy of it.

⛔ **The gate reviews the trial merge, not the branch** (`review-rubric.md` §0a,
§4b). ⭐ **The diff is the branch's; the verdict is the merge's.** Reviewing the
branch asks *is this change good?*; a merge gate asks *is the result good?* — and
those come apart **precisely when two parallel tasks are each correct alone**,
which is the only situation in which the interesting failures happen. A green
branch is not the evidence this gate asks for.

⚠️ **Establish the range before anything else and do not take it on trust.** The
base is the release branch the work was cut from — ⛔ **never `main`**, which goes
stale the moment a milestone opens. A base resolved against a stale branch does
not fail; it **passes the wrong thing**. ⭐ That is the worst property a gate can
have, because nothing looks wrong, and the failure *flatters*: the reviewer sees
more work, not less, so nobody questions the number. A review whose range was
wrong is re-run, not amended.

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
5. ⭐ **Findings marked `[local]` or `[structural]`.** The test is one question:
   *would this happen again to somebody else?* ⛔ **Every `[structural]` finding is
   ruled, scheduled, or explicitly accepted before the next wave opens** —
   *"noted"* is not one of the three. The reviewer routes them **in the review**,
   being the last person to read a handoff while anything can still be done about
   it, and marks an unmarked one: an author describing their own scope is the
   worst-placed person to see that something recurs elsewhere.

⚠️ **This exists because the protocol said to write findings down and never said
anyone had to rule on one.** A prediction was filed in the right place, in the
right format, read — and came true twice more. ⭐ `grep -rn '[structural]'
docs/tasks/handoffs/` is the triage list, and running it is part of opening a
wave. The PO owns that sweep.

### ⛔ Opening a wave: two checks, and the second was assumed for a milestone

```bash
grep -rn '\[structural\]' docs/tasks/handoffs/   # 1. the triage list
python3 -m tools.quality                          # 2. index present and current
```

⭐ **The second line is FND-07's, and it is a line in a checklist because the
alternative was believing a board row.** `FND-02` was marked done for a graph
that never reached the repository: its acceptance was **true in the worktree
where it ran and false everywhere else**, because `graphify-out/` is git-ignored
and ⛔ **an ignored artifact cannot travel on a branch.** Measured 2026-09-09:
**33 worktrees, 2 with a graph** — so every agent since had worked without the
index while the board said it existed, and R14's context budgets rest on it.

⛔ **That is not a criticism of `FND-02`**, which did the work and recorded what
it saw. The defect is that **the acceptance was unverifiable from the
repository** — which is why the answer is a check every checkout runs, and never
a rebuild somebody reports.

⚠️ **An absent index is not a failure and the check says so**, printing the two
commands that build one. ⛔ A *stale* one is not a failure either, since Ruling
96 — it is a **notice**, and the review rubric requires it to be quoted (4b-ii).
⛔ A *current but unbridged* one is still a finding — see `graphify.md`.

⭐ **The INTERIM rebuild step that stood here is DELETED by `W39`, and its expiry
was met rather than lapsed.** ⚠️ **It read *"whoever merges to a release branch
rebuilds the index before quoting the tip"*, because `freshness()` fired on any
change under `docs/` and every merge writes a handoff and a board row.** ⛔ **The
CTO ruled (96) that the rebuild is not the answer**: staleness is now scoped to
what the index actually describes, and a stale index cannot redden a tip. ⭐ **The
rebuild survives in the rubric as a courtesy to the next agent's queries, with no
pass condition and no power to invalidate a number.**

**The CTO's verdict is one of three:** `approved` (PO merges, or the CTO does),
`changes requested` (named, each tied to a ruling or an acceptance condition), or
`rejected — re-plan` (the task as written cannot be met; it returns to the PO as a
planning defect, which is a legitimate and cheap outcome).

⭐ **A fourth outcome exists per condition, and it is not a verdict: `Blocked`.**
An acceptance condition that cannot be *run* — because the tool it needs is not
installed, or the task it depends on has not landed — is Blocked, and the review
records which condition, why, and what will unblock it. ⛔ **Blocked is not
passed, and it is never a reason to delete the condition.** An unenforced rule
erodes exactly like an unenforced ceiling; the point of writing it down is that
somebody has to come back to it.

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

### ⛔ Ruling 75 — a row scheduled ahead of an older unstarted row says so, in the row

⛔ **A newly minted row may not be dispatched ahead of an older `todo` row of the
same size class unless the newer row's **When** cell names what it is jumping and
why.** ⭐ One cell, no ranking scheme, no restructuring — and it is the only thing
being asked for.

⚠️ **Measured, `PO-20/2`:** `W28` and `W29` were minted after `FND-08`/`FND-09`
and scheduled ahead of both; **`FND-09` has now waited two waves behind three
newer rows.** ⛔ **Nobody decided that.** ⭐ **A row arrives with its argument
fresh in the writer's head, which is exactly why it wins a slot it was never
ranked into** — the newer row is more *vivid*, not more urgent, and vividness is
indistinguishable from priority at the moment of writing.

⛔ **This does not forbid the jump, and that is deliberate.** Most jumps are
right: `W29` really did belong in front of `FND-09`, because it placed a ruling
the board had already taken. ⭐ **The defect is not the ordering, it is that the
ordering left no trace** — so the next PO inherits a queue whose shape looks
considered and was not, and the row at the back is invisible precisely because
nothing ever happened to it.

⭐ **It is this project's standard remedy, applied to scheduling: make the skip
leave a mark rather than prevent it** — the same shape as the merge message
naming its verdict, the size ceiling's declared exception, and a `blocked` row
naming its unblocking condition. ⚠️ **A rule that forbade the jump would be
worked around within a wave**; one that costs half a sentence is cheaper to obey
than to evade.

⛔ **A ranked per-developer queue is NOT ruled in.** `PO-20/2` proposes one and
wants a wave for it. ⭐ **That may be right later and it is not needed to close
this**: the failure here was silence, not the absence of a total order, and a
ranking scheme is a bigger instrument than the measurement supports. ⚠️ **Revisit
it if a row waits a third wave with the trace in place** — at that point the
board *has* decided, visibly, and the question becomes whether it decided well,
which is a different question and a better one to have.

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
**Measured:** the command, its output, and the date. Not "I noticed".
**What was needed:** the thing the corpus actually required.
**What the framework offered:** and where it fell short.
**Worked around by:** what was done instead, in the corpus repository only.
**Cost:** what a second source would have to retype (R19).
```

⛔ **A finding is a measurement with an as-of, and it is re-run before it becomes
a task.** ⭐ This is the record-versus-claim rule applied one level down: a finding
is a **record** — true when written, never rewritten — but *acting* on one turns
it into a **claim about now**, and the two can differ by the time anybody gets to
it.

⚠️ **This has happened in both directions in one milestone.** A finding was acted
on after the defect had been fixed, producing a decision to build a mechanism for
a hit that no longer fired; and a back-triage found that most of a backlog *had
already been ruled* and simply could not be seen. ⭐ **Both are the same error —
reading a record as a status** — and both cost more than the re-run would have.

⭐ **The re-run is usually one command, and it is the command the finding names.**
That is why `Measured` is a required field: a finding that does not say how it
was measured cannot be re-measured, and it will be either acted on stale or
quietly dropped.

⭐ **The finding count is the yield, not the failure.** An integration that
reports none has not been conducted honestly.

**A question is the other half of the channel, and it is not a lesser finding.**
⭐ A **question** is what you send when the framework has not been built yet and
you can see that what is planned will not fit; a **finding** is what you send when
it has been built and fell short. ⛔ **A question is never answered in the corpus
repository.** It is recorded on the board with an owner and a **deadline task** —
the framework task that must answer it, not a date — and the answer is carried
into that task's definition by the PO before it is assigned.

⚠️ **A question that arrives after its deadline task has shipped has become a
finding**, and the cost is a schema change under R9 rather than a schema
decision. That is the whole reason questions get deadlines: the cheapest moment
to hear that a contract does not fit a real corpus is before the contract exists.

⛔ **Where a source's needs become an exemption, the exemption is manifest data,
never a pattern hardcoded for one corpus** (R1). An exemption that names a corpus
is the framework learning about a source, which is the one thing it may not do.

**What flows the other way** — framework → integration — is contracts, never
instructions to go and look: the archive contract (`studyforge validate`, SF-25),
the placement contract (`studyforge plan`, SF-31), and each shared component's
`consuming.json` (TC-05, E13). ⛔ **A consumer never reads a Dockerfile to work
out how to run something**; that is the first step toward forking it (R18). If an
integrator has to, the missing `consuming.json` is the finding.

**Durable findings are distilled into the integration catalogue** in this
repository, so the next integration starts further along than the last. A finding
that stays in the corpus repository has taught nobody.

## Two kinds of document, and only one of them gets edited

⭐ **A handoff is a record. A plan document is a claim about now.** They are
maintained in opposite ways and conflating them produces both of the available
mistakes.

- ⛔ **A handoff is never rewritten.** It says what was true when its author
  finished, including what they got wrong. Editing it destroys the only evidence
  of how a decision was reached, and a corrected record is worth less than an
  honest one.
- ⛔ **A plan document — the spec, an epic, `README.md`, this board — asserts
  something about the present, so a statement in it that has stopped being true
  is a **defect**, not history. It is edited.

⚠️ **The failure this prevents:** a forecast that was correct when written
survives as a forecast after it has become history — *"SF-07's count key pushes
the module past the ceiling"* was true as a prediction, stale as a claim, and
sitting in `README.md` where the next reader would act on it. ⭐ **True-as-history
is not a defence for a plan document**, and the fix is one edit rather than a
footnote explaining when it was written.

⛔ **And before reporting a defect found in a handoff, check the file it is
about.** A handoff quotes the documents as they were; a quotation going stale is
the record working correctly. ⚠️ This project re-reported one already-fixed defect
**three times** from quotations inside old handoffs — three rounds of attention
spent on a document that had been correct since the first. **The check is one
`grep` and it goes before the report, not after.**

## Who decides

⭐ **Implementation decisions belong to the PO and the CTO.** Priority,
sequencing, scope and task modification are theirs to take, and the user reviews
the end result rather than adjudicating between options.

⛔ **Escalate to the user only for impact that is large or that could not be
undone later.** A choice between two workable orderings is not that; a decision
that discards work, changes what the product is, or cannot be reversed by a later
commit is. ⚠️ **The failure mode this replaces is a round trip per decision**,
which costs more than a wrong ordering does — an ordering can be changed, a
stalled milestone cannot be un-stalled.

⭐ **The consequence for the board is small and worth stating:** a decision taken
is a Log entry, not a proposal awaiting one. Record *what was decided and why*,
so a later reader can tell a judgement from an accident.

## Escalation

`agent-protocol.md` lists when an agent stops and asks. Two additions here:

- **A developer escalates to the PO**, not to another developer. Cross-task
  negotiation between developers is how two contracts quietly diverge.
- **The PO escalates a technical disagreement to the CTO**, and records the
  ruling on the board's Log. ⛔ **A ruling that is not written down did not
  happen** — that is the whole reason R1–R21 exist as a numbered list. A ruling
  lands in a handoff under `../tasks/handoffs/`, is logged on the board, and is
  **carried into the affected task's definition by the PO** — a ruling that lives
  only in a handoff will be re-derived by whoever picks the task up.
- ⭐ **Where two documents disagree, the measured one wins over the illustrative
  one**, and the disagreement is settled by counting rather than by which section
  is later in the file. This project's documents have twice been corrected that
  way; ⛔ do not inherit a number you can check.
