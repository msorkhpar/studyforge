# Working agreement for agents

How a task is picked up, worked, and handed on. Applies to every task in
`docs/tasks/`.

## Picking up a task

1. Read `docs/specs/2026-09-08-studyforge-v1-design.md` — §1–§4 and every
   ruling **R1–R21**. This is the authority you appeal to when the task is
   ambiguous. Do not invent a rule; if one is genuinely missing, say so in your
   handoff and proceed under a stated assumption.
2. Read your **epic document** — it carries the shared context for your task's
   neighbours, so you do not re-derive it.
3. Read `docs/conventions/module-structure.md` and `graphify.md`.
4. Read **only** the files in your task's *Context* field. If you need more,
   **ask the graph first** (R14). If you still need more, note it in your
   handoff — a wrong context budget is a planning defect worth recording.
5. Check `docs/tasks/handoffs/` for notes from tasks you depend on.

## While working

- **Tests are part of the task** (R12), not a follow-up.
- **Do not exceed the size ceiling** (R11). If your module is heading past 400
  lines, split it — that is the expected outcome, not a deviation.
- **Do not port inherited debt whole.** CodeSignal's large modules are ported
  as packages.
- **Stay inside your task.** A defect you notice outside it goes in your
  handoff as a finding, not into your diff. Unrequested scope is how parallel
  work collides.
- **Prefer the existing decision.** Where CodeSignal already ruled on
  something and recorded why, follow it and cite it. Where you think it is
  wrong, say so in the handoff — do not quietly diverge.

## ⛔ An acceptance clause you cannot meet is reported, never rewritten

⚠️ **Sometimes the plan contradicts itself and only one half can hold.** SF-03
met one: its own task entry asked for the extraction source's paths
*byte-identically* and, three paragraphs later, for every generated page to
carry a real name because a scan reads names. Both were written down; both were
believed; they cannot both be true of a filename.

⭐ **The standard, and it is not a small one:** ⛔ **implement the half you
judge right, say so in the handoff with the measurement that decides it, and
leave the document alone.** A task that quietly edits its own acceptance to
match what it built has removed the only record that a decision was made — and
the next reader finds a clause that agrees with the code for no stated reason.
⚠️ A task reporting *"I cannot meet this as written, here is why, here is what I
did instead"* is doing the harder and more useful thing.

⛔ **The document is then corrected by whoever owns it** — the CTO rules, the PO
edits — ⭐ **and the correction cites the ruling**, so the clause carries its own
history. ⚠️ **Do not leave it uncorrected either**: a reported contradiction
that nobody edits is a trap re-sprung on the next task that reads the clause and
believes it.

⚠️ **This is not licence to reinterpret an acceptance you merely find
inconvenient.** The test is whether the two halves are *jointly unsatisfiable*
and you can show it — a measurement, a counter-example, a contract that would
have to be versioned twice. "I would have designed it differently" is a finding,
not a contradiction.

### ⛔ "Loads a real \<source\> file" is met by a recorded measurement, not by a path

⚠️ **The clause cannot be met the way it reads, and that is a rule collision
rather than a contradiction.** A test citing the file needs an absolute home
path (R7) and a path inside the extraction source (R20). ⛔ The acceptance asks
for a thing the project forbids, and the cheapest way to satisfy it literally is
to paste a path — **which is the R7 failure arriving through an acceptance
criterion.**

⭐ **It is met by three things together, and none of them alone:**

1. **The measurement is run** against the real source at development time, over
   **all** of it, not a sample.
2. **Its command and its output are recorded in the handoff**, so a reader
   re-runs it and a reviewer reproduces it. ⛔ This is the half that makes it
   evidence instead of a claim.
3. **The suite pins the shape** — a key census, one real document committed as a
   fixture and reproduced field for field, and a test that no field is lost.

⚠️ **The fixture is not the evidence.** It was built to match the claim, so it
agrees with the claim by construction. It proves the *reader* still works; only
step 1 proves the *claim*. ⛔ **A claim about another repository is verified in
that repository** — a CTO ruling was overruled in round 14 for exactly this.

⚠️ **`grep -rn "a real " docs/tasks/E0*.md` finds 12 occurrences.** Unnamed,
eleven more tasks each invent their own answer.

## Handoff — required, one file per task

Write `docs/tasks/handoffs/<TASK-ID>.md` before you finish:

```markdown
# <TASK-ID> — handoff

**Status:** done | blocked | partial
**What landed:** the public surface you created, named. What a consumer imports.
**Decisions:** anything you chose that the task did not specify, and why.
**Surprises:** what the task or its context budget got wrong.
**Findings:** defects seen outside your scope. Not fixed. Named precisely.
**For dependents:** what the tasks that depend on you need to know.
```

This is the mechanism by which parallel agents share material rather than
re-deriving it. A task with dependents and no handoff is not done.

⛔ **Tag an illustrative fence `text`, not `python`.** The formatter reads
Markdown: `ruff format` discovers `.md`, formats the Python inside a ```` ```python ````
fence, and leaves ```` ```text ```` and untagged fences alone — measured, and it
has now caught three tasks. ⚠️ A tag of `python` is a **promise that the block is
Python**, so a hand-aligned usage example or a transcript is silently re-spaced
and your branch goes red at the gate. If it is output, a transcript or an
illustration, it is `text`.

## Findings are triaged, not filed

⛔ **Writing a finding down does not discharge it, and until 2026-09-09 nothing
in this protocol said who had to act on one.** That gap has a measured price.
`FND-04`'s finding 10 predicted the parallel-authoring defect exactly, named the
three options and said which was cheapest. It was filed in the right place, in
the right format, and read. **The same defect then happened twice more, to two
other agents, in the same milestone.**

⭐ **A finding filed correctly still cost two round trips, because nothing
obliged anyone to rule on it.** That is the most expensive kind of finding this
project produces: the knowledge was already where the protocol says to put it.

So findings carry a marker, and the marker creates an obligation:

- **`[local]`** — a defect in one place, fixed by whoever next touches it. Filing
  it is enough.
- ⛔ **`[structural]`** — a defect that **will recur**, or that describes a
  mechanism rather than an instance. ⭐ **Every `[structural]` finding is ruled
  on, scheduled, or explicitly accepted before the next wave begins** — by the
  CTO for a technical rule, by the PO for sequencing. "Noted" is not one of the
  three outcomes.

⭐ **The test for `[structural]` is one question: *would this happen again to
somebody else?*** If yes, mark it. ⚠️ Over-marking costs a sentence in a triage
list; under-marking costs what C5 cost.

```bash
grep -rn '\[structural\]' docs/tasks/handoffs/     # the triage list, before a wave
```

⛔ **A wave that begins with an untriaged `[structural]` finding is a wave that
has decided to pay for it twice.**

### ⛔ Before growing another task's contract, name the caller and the question

⭐ **Carried from CTO ruling 23, 2026-09-09, and the CTO notes this is the *third*
time an author has beaten a ruling of theirs this way.**

⛔ **Before adding a capability to another task's contract surface: name the
caller, and name the question the capability answers. ⭐ If the question dissolves
when you compute the answer directly, compute it directly.**

⚠️ **The instance:** `validate` branched on a placement profile *name*, and the
PO and CTO both ruled that `Profile` should grow a capability. The author
measured instead — the check needs **none** — and declined, reporting it with
evidence rather than diverging quietly. ⭐ **The CTO's own words on accepting it:**
*"You asked what a capability must answer that placing-and-comparing does not.
**Nothing — and that is the test, not a concession.** They cleared my standard by
removing the question rather than answering it."*

⛔ **And why the capability would have been worse than the branch it replaced.** A
`generates_beside_material` boolean is **an enumeration in disguise**: it sorts
profiles into two classes, the third must declare a side, and a wrong answer
costs a **silently skipped check** — ⚠️ *which is the failure the old code already
had.* The replaced check reported a **non-defect**, so the capability would have
preserved a **wrong** check behind a cleaner branch.

⭐ **This is *make the illegal value unrepresentable, do not enumerate it*,
arriving in a contract rather than in a validator** — and the cheapest form of it
is the one where nothing gets built at all.

### ⛔ Ruling is not carrying, and a carried ruling is **quoted**

⚠️ **Two holes were found in this mechanism, one round apart, and both were in
the mechanism rather than in anybody's diligence.**

**1. Ruled is not a destination.** ⭐ Of the three outcomes above, **only two name
one.** *Scheduled* names a task and *accepted* names a cost; ⛔ **"ruled" named a
decision and no home** — so a finding could be correctly ruled by the CTO, marked
correctly in the review, and still reach nobody. **Measured 2026-09-09: 30 of 32
findings ruled, and 8 of those had no board row, no epic clause and no trigger.**

⛔ **So a finding is dispositioned when its outcome has an artifact**: a task's
**Acceptance**, an **epic clause**, a **spec ruling**, or a **convention
document**. ⭐ **Never a handoff** — a handoff is a record, records are not
rewritten, and a ruling filed into one has been filed into the past. **A CTO
ruling is the decision; carrying it is the PO's, and it is wave-open check 3.**

**2. A carried ruling is quoted, not summarised.** ⚠️ **The round this mechanism
was built, a clause carried into a task reached its developer only as a
coordinator's paraphrase.** ⭐ The developer wrote nothing to a guess and reported
the gap, which is the right behaviour — but the ruling never arrived.

⛔ **A ruling relayed as somebody's summary has been through a lossy channel, and
the relayer is the lossy part.** ⭐ **The developer must be able to read the
clause itself**, in the words it was ruled in, in the task document — not a
description of it in a briefing. ⚠️ A paraphrase is how a ruling arrives *nearly*
right, which is worse than not arriving: ⛔ **an absent ruling gets asked about; a
nearly-right one gets implemented.**

## When a convention tightens, the tightening owns the migration

⛔ **No work done under an older convention is at fault for failing a newer one,
and the commit that tightens owns bringing the corpus into compliance.**

⭐ **This is the C5 rule, applied to documents instead of code.** There it reads
*no open branch is expected to fix a rule it never saw*; here it reads *no
handoff filed before a marker existed is expected to carry it*. Same argument,
same asymmetry of knowledge, same answer.

⚠️ **One difference changes what "compliance" costs.** A style rule can be
satisfied mechanically — run the formatter, commit. A *convention* usually
cannot: deciding whether an existing finding is structural takes judgement, one
at a time. So the obligation is to discharge it **before the next wave**, not
necessarily inside the one commit. What the tightening commit must do is choose,
out loud:

1. **bring the corpus into compliance**, or
2. **name the backlog and its deadline**, in the commit that tightens.

⛔ **The forbidden third option is silence** — tighten, and let the gap be found
by whoever runs the new check and reads an empty result as a clean bill.

### ⛔ A new check reports its coverage, not just its hits

⭐ **An empty result from a newly-introduced check is not evidence. It is an
unanswered question**, and it has two indistinguishable causes: there is nothing
to find, or nothing has been marked yet.

So a check introduced over a corpus that predates it **says how much of that
corpus it was able to judge** — "17 findings marked across 5 handoffs; 2 handoffs
carry 13 unmarked findings" — never a bare count of hits.

⚠️ **This project has already paid for this exact failure once, in a different
guise.** CodeSignal's synthesis runner decided a clip was current by whether the
file existed; on a re-capture **619 clips went on speaking the previous wording**
and the run reported *"0 synthesised"* with every gate green (spec §8.2). ⭐ A
green report meaning *"I did not look"* is indistinguishable from one meaning
*"there was nothing to find"*, and only the check itself can tell them apart.

## Reporting

Report outcomes faithfully. If tests fail, say so and include the output. If
you skipped part of the scope, say which part and why. Do not describe work as
complete before it is verified — run the command and read the result. Evidence
before assertions, always.

## Escalating

Stop and ask rather than guessing when:

- Two rulings genuinely conflict on your task.
- Your task's acceptance cannot be met without changing another task's surface.
- You would need to modify a pre-existing file in a consumer repository (R3).
- The work turns out substantially larger than the task describes — that is a
  planning defect, and re-planning is cheaper than an overrun.

Refining a task as the project grows is expected and welcome. Silently
expanding one is not.
