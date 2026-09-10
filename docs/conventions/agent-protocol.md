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

### ⛔ Every negative control is itself run negatively

⭐ **Show the probe failing on the defect before trusting it to pass.**

⚠️ **Four instances in one session, and the pattern is what makes it a rule:** an
`mv` that reported 38 passed; a rubric edit whose comment swallowed a colon and
broke collection; a formatter; and ⛔ **a probe that reported all four gate shapes
REFUSED because `leaks()` returns a generator and the prober tested
truthiness.**

⛔ **The last one is the dangerous shape, and it was a *verification of somebody
else's finding*.** ⚠️ **Had the finding been false, a real R7 hole would have been
closed on the strength of a probe that could not fail.** A green probe and a
correct system are indistinguishable from the outside — ⭐ **which is the whole
reason a control has to be shown failing first.**

⚠️ **All four were probes** — a reviewer's or a coordinator's — ⛔ **never a
task's own tests, where *watch it fail first* already applies.** ⭐ **That is the
gap: the discipline existed for code under test and not for the instruments used
to decide whether code needs testing.** A probe is how a finding gets verified
before it becomes a task, so an unfalsifiable probe corrupts the input to
everything downstream.

### ⛔ A number in a ruling is evidence, never a bound

⭐ **A number in a ruling is a measurement from an instrument, never a property of
the tree.**

⚠️ **Measured instance, and the gap is the argument:** the rubric's §7c grep found
**7** hits in 3 modules; the check built to replace it found **19** in 11.
⛔ **Twelve real violations the grep could not see** — all one shape, **a corpus
named in English** (*"the Java corpus"*) rather than by its repository slug, and
§7c's own sentence is *"a fail even in a comment."*

⛔ **The incentive is the thing to avoid, and its author named it:** *"bound the
migration by a number and the cheapest compliance is a check scoped to its own
backlog — which is worse than no check because it's green."*

⭐ **So a ruling that cites a count says what produced it**, and a task that
inherits one **re-measures with its own instrument rather than treating the
number as the size of the job.** ⚠️ **The implementer's line is the one to carry:**

> ⛔ *"The number was a fact about an instrument. Building the check to find seven
> would have been fitting the instrument to the backlog."*

⚠️ **This is Ruling 52's shape in a number rather than a sentence** — a figure
stated without its instrument is quoted as a bound, exactly as a rule stated
without its scope is quoted at its widest.

### ⛔ A ruling states the scope it was argued over

⭐ **Name the case that produced it, and say what is outside it.** ⚠️ **Otherwise
the next reader supplies a scope — and they will supply the widest one the
sentence allows.**

⛔ **The tell is what makes this expensive: the ruling reads *better* than the
argument.** A rule stated without its scope is shorter, more quotable, and lands
more cleanly — ⚠️ **which is exactly why it gets carried further than it was ever
argued.** Nothing about it looks wrong; it looks *finished*.

**Two measured instances, and they are one pattern:**

| Ruling | What was argued | What was ruled |
|---|---|---|
| **28 → 30** | that the contract should be **teachable** from the spec | ⛔ *"the example gains `media`"* — **the remedy over-generalised**, and it would have frozen an optional key on every corpus |
| **17's qualifier** | **one seam** | ⛔ the boundary **stated generally** — and it contradicted a clause carried in the same session |

⚠️ **Both were caught by an implementer meeting a case the argument never
covered. Neither was caught by anyone re-reading the ruling** — because re-reading
is exactly what a well-stated over-broad rule survives.

⭐ **Ruling 44 is the model, and it was accidental:** it ruled a boundary **and
named its domain** (*enumerate the legal — except where the permitted set is free
text*). ⛔ **The rulings that needed correcting are the ones with no such
sentence.**

#### ⚠️ The known cost of the carrying clauses above, and it is theirs specifically

⛔ **This is the one place the carrying machinery makes things worse.** C6 says a
ruling **reaches its artifact**; *quote, don't summarise* says it arrives
**verbatim**. ⭐ **Both propagate an over-broad rule faithfully and fast.**

⛔ **The better the delivery, the more expensive the over-reach.** ⚠️ Recorded here
as the carrying clauses' known cost — beside the two limits of the measurement
discipline — because ⭐ **a mechanism whose failure mode is undocumented gets
trusted in exactly the case it fails.**

### ⛔ An announcement is not a hand-over

⚠️ *"Committed as `<sha>`"* reads as bookkeeping **because it is phrased from the
writer's side.** ⭐ **A hand-over names what the reader must do:** *"merge
`<branch>`; route Ruling 52 to the PO."*

⛔ **Measured instance, and both halves were real:** one side left **seven
unmerged commits**; the other **read seven announcements of them and merged
none.** ⚠️ **Nobody was idle and nothing moved** — which is the shape to watch
for, because it looks like progress from both ends.

⭐ **Every agent here reports upward or sideways**, so this applies to all of
them: **end a report with the reader's next action, not the writer's last one.**

### ⛔ Hold it, or point at where it is held — never point at a document that points back

⭐ **Rated the best finding of its round, and it is the pointer rule's own failure
mode.** ⚠️ **Measured instance:** `graphify.md` said the census command was in
`FND-02`'s handoff; that handoff said it was in `graphify.md`. ⛔ **Neither had
it.** Two documents pointed at each other and the thing they pointed at did not
exist anywhere.

⛔ **A document may *hold* a thing, or *point at where it is held*. It may never
point at a document that points back.**

⚠️ **This is the sharp edge of *a summary points, it never restates*** — that rule
is right and it created this one, because ⭐ **a pointer is cheap to write and
nobody checks that the far end holds anything.** A stale copy is at least a copy:
you can read it and see it is wrong. ⛔ **A cycle of pointers reads as
well-organised and contains nothing** — every hop looks like diligence.

⭐ **So the obligation lands on the pointer's author: follow it once, and confirm
the far end *holds* rather than *forwards*.**

⚠️ **And the tension a later author will hit, dissolved rather than excepted.**
When a justification rests on a **measurement**, it can look as though the rule
forbids naming the corpus the number came from. ⛔ **It does not.** ⭐ **The number
is the justification; the corpus name was only its citation** — so ⚠️ **this is
not an exception to the pointer rule, it is the pointer rule applied to the right
unit.** Hold the number; cite where it came from.

### ⛔ A citation is not an edge until both ends exist in one index

⚠️ **Quoted into the record because a census depends on it.** A prose-to-code
count moves when a branch merges — not because anything drifted, but because ⭐ **a
citation only becomes an edge once both of its ends are in the same index.**
⛔ **Without this sentence beside it, somebody reads the movement as drift** and
investigates a number that is behaving correctly.

⚠️ **And its companion, which cost real work: state the ratio, the denominator,
and the set it is over — or it will be quoted wrongly.** A bare *"7.9%"* was
carried as a citation defect when it was a **design input**: a developer *"built
a 969-edge bridge on it before measuring."* ⭐ **It belongs beside the number it
governs, not in a ruling nobody rebuilding a census would read** — placement, not
strength, is what that rule lacked.

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

**3. The owner is a field, not a sentence.** ⛔ **A ruling that assigns work names
the owner in the field the board reads, not only in the sentence that reasons
about it.**

⚠️ **The instance, and both halves were right alone — which is why it is C6
again.** The CTO ruled a finding's content and priority correctly but **named no
owner in a field**; the PO read *"needs an owner"* and assigned **the only name
attached to the ruling — the CTO** — which was a category error: they do not
write framework code, and it would have had them write a fix and then review it,
⛔ **§12's rule applied to themselves.** ⭐ Neither was careless. The owner existed
in nobody's field, so the board's reader supplied one from context.

### ⚠️ The known blind spot in all of the above, recorded rather than discovered later

⛔ **These clauses make a ruling arrive *faithfully*. None of them makes it
arrive *correct*.**

⭐ **"A wrong ruling carried promptly is worse than a right ruling carried
slowly."** ⚠️ **Measured instance:** a CTO finding asserted a `slugify` collision
that does not exist, and the PO carried it into a task definition **the same
day** — ⛔ **the quote-don't-summarise clause worked perfectly and propagated an
error faster.** What caught it was not a carrying rule. **It was somebody
measuring.**

⛔ **So a carried ruling that makes a factual claim is re-measured at the point of
carrying**, exactly as a finding is re-run before it becomes a task. ⭐ Same rule,
one step later in the pipeline, and for the same reason: **carrying turns a
record into a claim about now.**

#### ⛔ And the second failure mode, which is worse, because measuring is the fix for the first

⭐ **A count answers the question you asked. It does not tell you it was the wrong
one.**

⚠️ **Measured instance, and the CTO filed it against their own ruling.** Ruling 28
came **from** a measurement — they counted `MANIFEST_KEYS` at ten against the
spec example's nine, found exactly one missing, and ruled that the example gain
it. ⛔ **It was still wrong.** They had measured *what the example omitted* and
never asked **whether the omission was correct** — and `media` is **not in
`REQUIRED_KEYS`. The fact that would have caught it sat two lines from the tuple
they counted.**

⛔ **The harm was not hypothetical:** an exhaustive canonical example propagates
through `SK-07`, which **generates** manifests, and freezes an optional key on
every corpus including ones with no media.

⚠️ **This project has now found two independent failure modes of its own
verification discipline in one round** — *a wrong ruling carried promptly*, and
*a correct measurement of the wrong question* — ⛔ **and neither is fixed by the
carrying mechanism.** ⭐ **Recorded together, because the first one's remedy is
"measure", and the second one is a way measuring fails.**

### ⛔ The sideways channel — a finding that arrives from outside the task line

⚠️ **Both of the largest findings of 2026-09-09 arrived sideways**, from another
agent's unrelated ruling rather than down the task line: the ungated
`corpus.json` surfaced from a complaint about a **paraphrase**, and Ruling 28's
reversal was caught by a **scheduling note about key names**. ⭐ **Neither was
found by the person who owned the thing that was wrong**, and neither would have
been found by that person continuing to look.

⛔ **The task line carries a task's own findings. It has no channel for *"while
doing X, I noticed Y about Z"*** — and the two most expensive findings of the
round both had that shape and both arrived by luck of routing.

⭐ **The mechanism, and it is one line rather than a process:** when carrying a
ruling that touches a **shared** artifact — the spec, a contract, a generator, a
convention — ⛔ **name the other agents whose standing constraints it could
collide with, and if one exists the carry waits for their check.**

⚠️ **It is cheap because the collision is nearly always already written down.**
Ruling 28 collided with a **scheduling** constraint the PO had recorded four
hours earlier; the gate clause collided with a **boundary** ruling recorded in
the same session. ⭐ **Neither needed new information — only somebody asking
whose constraint this lands on.** ⛔ **The question is the mechanism; the answer
is usually one name and often none.**

#### ⛔ A check covers what is there; a broadcast covers what is coming

⚠️ **Corrected by Ruling 39, on a measurement, and the correction is the useful
part.** The PO proposed that this belonged *closer to the code* than to the wave,
on the evidence that an author caught a collision the wave-open check did not.
⛔ **Measured: at the time, a sweep of the release tip would have found three
files and none of them was the colliding guard — it lived only on an unmerged
branch.**

⭐ **So distance was never the problem. The code was not in the tree the sweep
reads.** ⚠️ That is the vantage-point argument for the fourth time: ⛔ **a sweep
sees the tree and cannot see the branches.**

⛔ **And "move it rather than grow it" was the wrong dichotomy — the answer is
neither.** The wave-open check is the backstop for rulings whose subject is
**already merged**, which is a real, non-empty, otherwise-unwatched set. ⭐ **The
two instruments cover different sets, and moving one to do the other's job leaves
both holes open.**

**So the obligation sits on the ruling's author, and it is one command:**

```bash
# ⛔ a ruling that changes a shared name names its blast radius across BRANCHES
git grep -l "<the name>" $(git branch --format='%(refname:short)' | grep -E 'feat/|fix/')
```

⚠️ **Run it while writing the ruling, not after.** ⭐ It finds the collision
directly — in the instance that produced this clause it named the exact test file
a ruling would have broken. ⛔ **Asking *"whose constraint does this land on?"*
depends on already knowing who; this does not.**

⭐ **And the sentence worth keeping, which the CTO wrote about themselves:** *"I
didn't run it, and the author covered for me. **A reviewer covered for by an
author has found a hole in their own procedure, not good luck.**"* ⚠️ **A
broadcast that works because somebody happened to tell the right person is not a
mechanism** — it is a mechanism's outcome, arriving by luck, and it will not
arrive next time.

### ⚠️ C5's shape in prose, and there is no trial merge for documents

⛔ **Two correct things authored hours apart can contradict each other with
neither author careless.** ⭐ **Measured instance:** a clause carried into a task
contradicted a ruling **written by the same person in the same session** — the
clause told one component to re-ask a question the ruling had just placed
elsewhere.

⚠️ **That is exactly C5** — *each correct alone, wrong together* — ⛔ **and the
trial-merge gate that catches C5 in code has no equivalent for documents.** The
nearest thing is the PO's wave-open check 3, which re-reads the artifact a ruling
landed in: ⭐ **read the neighbouring rulings in that artifact, not only the
clause you are adding.**

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
