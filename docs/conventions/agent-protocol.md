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

### ⛔ Ruling 146 (CTO round 39) — a sweep asserts its own ROW COUNT, and every `docker` call takes `</dev/null`

> ⛔ **A sweep that does not assert how many rows it ran is not a sweep.** The
> count is asserted against a population declared **before** the loop, and every
> `docker` invocation inside a loop is redirected **`</dev/null`** — `docker`
> otherwise consumes the loop's stdin and the sweep silently runs **one** row.

⚠️ **The first sweep to hit this exited 0, printed two agreeing baselines, and
looked healthy.** ⛔ **It defeats Rulings 70, 76, 83 and 123 at once**, because
every recorded signal was true — of the one row that ran.

⭐ **The clause and its measured rows live in
[`review-rubric.md`](review-rubric.md), §4c**, beside Ruling 131's clean-tree
rule; ⛔ **it is cross-referenced here, not copied — a rule written in two places
goes stale in the copy nobody re-measures.**

### ⛔ Ruling 139 (CTO round 38) — a sweep's artifacts live under the agent's **own worktree**

> ⛔ **A sweep row's artifacts — log, table, harness, mutant backup — are written
> under the agent's own worktree (`<worktree>/.scratch/`), never the shared
> scratchpad root.** ⚠️ A sweep is the one artifact that cannot be re-derived
> cheaply: 39 container runs, ~13 minutes.

⚠️ **Why:** `W40/5` and `SK-05/6` are the same defect reported from opposite
sides in one round. Both sweeps wrote `sweep.log` into the shared session
scratchpad; one truncated the other, and `SK-05`'s first log came back carrying
another row's readings. ⭐ **`W40` kept its numbers by luck** — its rows were in a
file the other script did not name.

⛔ **The enabling half already shipped and you must not undo it: `.scratch/` is in
`.gitignore`.** ⚠️ **Without that entry the clause reds the floor** —
`tools.quality.config.text_files` walks everything git has not been told to
ignore, deliberately, because a file you have just written and not yet added is
exactly what an R7 gate must catch (`config.py:253`). ⭐ **Measured in the pinned
image, three readings, `$?` with no pipeline:**

```text
1  LIVE     .scratch/ present and NOT ignored  ->  floor exit 1, 108 findings
1' LIVE     .scratch/ present and ignored      ->  floor exit 0
3  CONTROL  git check-ignore .scratch/          ->  exit 0, matched by .gitignore:48
           git check-ignore tests/support.py    ->  exit 1   (the rule is narrow)
```

⛔ **Run reading 3 before you trust the clause.** ⭐ **It pairs with Ruling 131's
clean-tree clause** (`review-rubric.md`), which is where the sweep's other
tree-sensitivity rule lives — ⚠️ **the ruling named this file and named that
neighbour, and they are two documents; the clause is here and the neighbour is
cross-referenced rather than copied** (`PO-31/5`).

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

### ⛔ An acceptance condition NAMES THE INSTRUMENT THAT WOULD FAIL IT

⛔ **Ruled from `CTO-29/3`.** ⭐ **A condition nobody can fail is not an
acceptance condition. It is a wish** — and a reviewer who meets one has exactly
one move left, which is to trust the handoff of the person they are reviewing.

⚠️ **The measured instance:** Ruling 91's clause reached an *implementation* and
never reached the *acceptance document*, so the review had no way to test it.
⛔ **`W33` catalogued seven instances of *a check that cannot fail*; this is the
EIGHTH and the first inside the ACCEPTANCE instrument** — ⚠️ **which is the
worst place for it, because that instrument is what every other row is judged
with.**

⭐ **So an acceptance condition is written in two parts, and the second is not
decoration:**

| | |
|---|---|
| **the claim** | what must be true when the task is done |
| ⛔ **the instrument** | ⭐ **the thing that returns a DIFFERENT answer when the claim is false, plus the reading that means REFUSED** |

⛔ **Three instrument forms are admissible:**

1. **A command and its expected reading** — `docker/dev/check python3 -m pytest
   -q tests/<file>.py` → `N passed`. ⚠️ **The reading is part of the form**; a
   command with no stated outcome is half a condition.
2. **A test node id** — ⭐ it is collected or it is not, so a deleted test fails
   the condition instead of quietly satisfying it.
3. **A named gate rule** — the gate (`python3 -m tools.quality`) *and* the rule's
   own name, so a reader can reach the code that decides.

⛔ **What is NOT an instrument, and this is the one that keeps getting
written:** ⚠️ ***"the handoff records it."*** ⭐ **A handoff is where a reading is
REPORTED; it is never what TAKES one**, so a condition discharged by reading one
asks the reviewer to verify the author against the author. ⛔ **Nor are
*"reviewed"*, *"documented"*, *"consistent with"* or *"as appropriate"*: none of
them names a thing that can return `no`.**

⭐ **If you cannot write the second column, you have found a defect in the task
rather than a formality to skip.** ⛔ **Report it — the standard this section
opens with is unchanged: implement the half you judge right, say so with the
measurement, and leave the document alone.** ⚠️ **The owner then supplies the instrument or
DROPS the condition, and dropping it costs nothing, because a condition that
could never fail was never doing any work.**

⚠️ **Scope, so the next reader does not supply the widest one (see *a ruling
states the scope it was argued over*, below).** ⛔ **This binds acceptance
conditions — the clauses on a task row, in an epic document or in the rubric,
that somebody signs off against.** ⭐ **It does NOT bind design prose, a
ruling's argument, or a finding**, none of which is a thing anyone passes or
fails.

⭐ **This clause names its own instrument, which is the whole of it:** ⛔ **read
each acceptance condition on the row in front of you and ask what would make it
say `no`. A condition for which that question has no answer FAILS this clause**,
and the empty answer is the reading that refuses it.

## Handoff — required, one file per task

Write `docs/tasks/handoffs/<TASK-ID>.md` before you finish:

```markdown
# <TASK-ID> — handoff

**Kind:** task handoff — <TASK-ID>

**Status:** done | blocked | partial
**What landed:** the public surface you created, named. What a consumer imports.
**Decisions:** anything you chose that the task did not specify, and why.
**Surprises:** what the task or its context budget got wrong.
**Findings:** defects seen outside your scope. Not fixed. Named precisely.
**For dependents:** what the tasks that depend on you need to know.
```

This is the mechanism by which parallel agents share material rather than
re-deriving it. A task with dependents and no handoff is not done.

⛔ **`tools/quality/handoffs.py` runs this, so it is a build failure and not a
reviewer's memory** (Ruling 49). Two literals are load-bearing:

- ⛔ **`**Kind:**` is how a document says what it is**, and `docs/tasks/handoffs/`
  holds four other kinds — `ruling record`, `session log`, `survey`, `index` —
  that owe none of the six sections. ⚠️ **The filename is not the binding.** It
  never was: measured 2026-09-10, **10 of that directory's 53 documents were
  not task handoffs and 8 of those already carried `— handoff` in their own
  title**. A survey that declares itself is exempt *for a reason*; one that
  declares nothing is **refused**, which is a question rather than a silent
  admission. A new kind is one entry in `DOCUMENT_KINDS`.
- ⭐ **A handoff for two tasks declares both** — `**Kind:** task handoff — W17,
  W19` — and its title names both. The filename must begin with the first.

### ⛔ Ruling 134 (CTO round 38) — a history-based instrument silently loses a file at a rename it did not score

> ⛔ **When a task splits a module into parts and no part reaches git's default
> similarity, the handoff RECORDS THE FLAG that recovers the history, and any
> later task tracing a split file's provenance runs `-M20%` before concluding
> the history is gone.**

⚠️ **The failure is silent and it flatters** — the history *looks* complete, it
simply begins later.

```bash
git log --follow tests/gate_coverage/test_coverage.py   # stops at W40's commit
git diff -M20% ddddd05 HEAD -- tests/gate_coverage/     # finds it
```

⛔ **Measured:** no single new module is 50 % of the 600-line original.
⭐ **`W40` already did this; the ruling ratifies it as the standing form rather
than one developer's courtesy.**

### ⛔ A record is ANNOTATED, never edited — and its header names a REF, not a pointer

⛔ **Ruling 106.** ⚠️ **A `session log`, a `ruling record` and a task handoff are
RECORDS: their contract is fidelity to what was known when they were written.**
⭐ **A living document — `CLAUDE.md`, `BOARD.md` — is the opposite: its contract
is CURRENCY, and it is edited.** ⛔ **Each one's failure mode is the other's
contract**, which is why the two are never maintained the same way.

- ⭐ **A record that goes out of date is CORRECTED BENEATH, and the correction
  carries the ref it was taken on.** ⛔ **Editing the original so it reads true
  today destroys the only thing a record is for**, and it is how a document
  quietly claims its author knew something they could not have known.
- ⛔ **But most such staleness is a HEADER-FORM defect rather than a staleness
  defect, and it is avoidable outright.** ⚠️ **A field labelled `Release tip:`
  asserts a MOVING POINTER and goes stale the instant anything merges. A field
  labelled `Measured at: <branch> @ <sha>` is a READING BOUND TO A REF and cannot
  go stale at all.** ⭐ **When this fired, the numbers under the header were exact
  and stayed exact — re-measured at the named ref one round later and reproduced
  to the test; only the word *tip* had aged.** ⛔ **So a record states the ref it
  measured, never the position it inferred a branch was in.**

⛔ **Tag an illustrative fence `text`, not `python`.** The formatter reads
Markdown: `ruff format` discovers `.md`, formats the Python inside a ```` ```python ````
fence, and leaves ```` ```text ```` and untagged fences alone — measured, and it
has now caught three tasks. ⚠️ A tag of `python` is a **promise that the block is
Python**, so a hand-aligned usage example or a transcript is silently re-spaced
and your branch goes red at the gate. If it is output, a transcript or an
illustration, it is `text`.

### ⛔ A reading taken from a PROXY is not a property of the THING

⛔ **Ruled from `CTO-29/8`, and it is Ruling 55 generalised past numbers.**
⭐ **Ruling 55 says a number is an instrument reading, never a property of the
tree. Drop the word *number* and the rule gets much larger:** ⛔ **every reading
comes off something, and that something is usually a PROXY for the subject you
are about to name.**

⚠️ **Six measured instances, four rounds, three different roles:**

| ⭐ **the reading, and it was ACCURATE** | ⛔ **the subject it got called** |
|---|---|
| a **branch** | its **tip** |
| a **disk walk** | the **tree** |
| a **constant** | the **check** that reads it |
| a **worktree** | the **agent** working in it |
| a **board row** | the **rubric** it quotes |
| ⚠️ a **`grep` hit** (`PO-26/3`, below) | the **document** it was found in |

⛔ **In all six the reading was CORRECT and the SUBJECT was WRONG.** ⭐ **That is
why none of them looks like an error, why nothing goes red, and why three roles
committed the same defect in four rounds:** ⚠️ **the sentence is true of the
proxy and false of the thing, and only the author knows which one they measured.**

⭐ **The check is two questions, and you ask them of the SENTENCE you are about
to write, not of the command you just ran:**

1. ⛔ **What did I MEASURE?**
2. ⛔ **What am I about to CALL it?**

⛔ **Different words mean the sentence names the proxy, and it must then say
so.** ⚠️ `git branch --no-merged` returns *branches carrying unmerged commits*,
not *work in flight*. ⚠️ An absent `graphify-out/` says *this checkout has no
index*, not *the index is stale* — ⭐ **which is Ruling 108 arriving as a special
case of this clause rather than as its own fact.**

⭐ **The reporting form is already here:** ⛔ **`Measured at: <branch> @ <sha>`
from the section above, and the instrument beside it.** ⚠️ **A reading whose
instrument is not written down cannot be checked for this defect by anyone
except the person who took it.**

#### ⚠️ `PO-26/3` — and the sixth instance is MANUFACTURED by this document's own rules

⛔ **A `grep` hit inside a block marked `CORRECTED`, `~~struck~~`, *"this section
said"* or *"replaced by"* is NOT a reading of the document.**

⚠️ **Measured instance, PO round 26:** a brief reported that `CLAUDE.md` names M1
step 1.4 and `SF-10` as in flight. ⛔ **It does not** — the live line reads *"In
flight: M2 step 2.1"*, and the `SF-10` hit sits inside the round-19 **correction
record**, quoting the sentence it REPLACED. ⭐ **The document was current; the
reading was stale.**

⛔ **This is not a `grep` defect. It is a defect this file MANUFACTURES.**
⭐ **The section immediately above rules that a record is corrected BENEATH and
that the original stands** — ⚠️ **so a corrected document answers `grep` TWICE
by construction, and the instrument cannot tell the replaced half from the live
one.**

⛔ **The remedy is NOT to stop quoting the replaced text**; a correction nobody
can audit is worse than a duplicate hit. ⭐ **It is that whoever quotes a hit
owes the SURROUNDING LINE.** ⚠️ **A hit under a correction marker is evidence
about the record's HISTORY and evidence of nothing about the document's CURRENT
state.**

⭐ **Runnable, and this clause names its own instrument:** ⛔ **re-take the hit
as `grep -n -C3 '<pattern>' <file>` and REFUSE it when the context carries
`CORRECTED`, `~~`, *said* or *replaced*.** ⚠️ **A row whose reading was taken
with a bare `grep -n` and then quoted as the file's current state FAILS this
clause**, and the surrounding lines are the reading that refuses it.

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

- ⭐ **`[none]`** — *nothing outside this task's scope*, said rather than left
  to be inferred. ⛔ It carries the sentence that says what was looked at, it
  may not stand beside a real finding, and it is the **only** way to write zero.

⛔ **The vocabulary is CLOSED at these three, and a fourth was tried and
refused** (Ruling 105). ⚠️ **`[negative]` — *"I looked, and the answer was no"* —
was written in three documents, by two roles, across three rounds, before anybody
checked whether it counted.** ⛔ **It does not join them.** ⭐ **A marker encodes
ROUTING, and a recorded negative routes exactly where a `[local]` routes:
nowhere.** ⚠️ **Polarity is content, not triage**, so it is written in the
finding's own first words rather than in a fourth word of vocabulary:

- ⭐ **A recorded negative IS a finding, it is marked `[local]`, and its text
  opens with `A NEGATIVE result.`** ⛔ **It is a finding because it was
  investigated, concluded, and recorded so that the next reader does not re-raise
  it** — ⚠️ **and because a round that disproves three suspicions has not produced
  fewer findings than one that confirms them.**
- ⛔ **A "negative" that names a fix, a remedy, a row, or a change anyone should
  make is NOT a negative.** ⭐ **It is `[local]` or `[structural]` on its merits,
  whatever is true about how it was originally filed** — ⚠️ **a finding that was
  NARROWED is still a finding, and that is the failure the fourth marker actually
  produced in one of its three uses.**

⭐ **The test for `[structural]` is one question: *would this happen again to
somebody else?*** If yes, mark it. ⚠️ Over-marking costs a sentence in a triage
list; under-marking costs what C5 cost.

⛔ **A handoff that marks nothing is a build failure** (Ruling 29's other half,
now enforced): a finding *is* a marked item, so an unmarked one does not exist,
and `0` was the reading that used to pass silently. ⚠️ **And a marker in prose
is a finding that does not exist** — write *local* and *structural* as words
when you are talking *about* the markers, and keep the backticks for the item
being marked.

```bash
grep -rn '\[structural\]' docs/tasks/handoffs/     # the triage list, before a wave
```

⛔ **A wave that begins with an untriaged `[structural]` finding is a wave that
has decided to pay for it twice.**

### ⛔ A finding is numbered **inside its own document**, never globally

⭐ **The form is `<TASK-ID>/<n>` — `SF-12-survey/1`, `FND-05a/3` — and `n` starts
at 1 in every document.** ⛔ **Do not mint a number from a project-wide
sequence.**

⛔ **A handoff covering two tasks scopes each finding to one of the IDs it
declares — `W30/1`, `W31/1` — never to the filename's compound stem.**
⚠️ **`W30-W31/1` is refused, and correctly: `check_finding_ids` compares the
scope against the IDs on the `**Kind:**` line, and `W30-W31` is not one of
them** — ⭐ **the file is named `W30-W31.md` because `check_filename` requires the
stem to begin with the *first* declared ID, which is a filename rule and not an
identifier.** ⛔ **Ruled `W31/1`, round 26: the code was right and this document
was silent, and the `W17-W19` precedent in the tree predates the rule, so there
was no worked two-row example to copy.**

⚠️ **Because there is no allocator, and there cannot be one.** ⭐ **A global number
is a contract, so R21 applies: it needs one producer.** ⛔ **A branch cannot have
one.** Every number is minted by an agent who cannot see the other branches, so
**the collision is structurally invisible from the place it happens** — ⚠️ **which
is the tell every expensive defect on this project has shared**, and it is the
wave-open sweep's known blind spot in a new costume: *a sweep sees the tree and
cannot see the branches* (ruling 39).

⛔ **Measured 2026-09-10, and the measurement is what refuses the allocator:**

| | |
|---|---|
| global numbers minted, `handoffs/` | **29**, across 12 documents |
| range | 20 – 58 |
| ⛔ **collisions** | ⛔ **3 — `53`, `54`, `55`** |
| ⚠️ **gaps in the range** | ⚠️ **10** — 21, 23, 24, 34–40 |
| citations of a global number, repo-wide | **46**, across 22 files |
| ⛔ **citations now ambiguous** | ⛔ **8** |

⛔ **The two colliding documents have the SAME AUTHOR, on two branches, in one
wave.** ⭐ **That is the whole argument in one fact: an allocator is a file, a file
on a branch is invisible to another branch, and this author would have edited it
on both.** ⚠️ **Best case it conflicts — which is the reviewer catching it, which
is what already happens. ⛔ Worst case both increments merge cleanly and one
number is silently lost.**

⭐ **And the ten gaps kill the cheap version outright:** ⛔ **`max()` over the tree
is not an allocator's state, it is a lower bound that ignores every unmerged
branch** — so *"read the highest and add one"* is precisely what produced `53`
twice.

⭐ **Per-document numbering makes the collision unrepresentable rather than
detected**, which is this project's most-repeated finding — *enumerate the legal;
do not enumerate the illegal* — ⚠️ **and it is ruling 29's move one level out.**
⭐ **The document name is already unique and already enforced**, so the namespace
costs nothing to create.

#### ⛔ The migration is nearly free, and the reason is a rule this project already has

⛔ **Existing handoffs are NOT renumbered.** ⭐ **A handoff is a record and is never
rewritten** — so numbers **20–58 are a closed legacy range**, every existing
citation keeps resolving, and ⚠️ **the three ambiguous numbers are disambiguated
on `BOARD.md`, not by editing the two documents.** ⭐ **That is `W4`'s precedent:
the board is where a superseded record gets superseded.**

⛔ **So the rule binds new findings only, and its enforcer is Ruling 49's handoff
check (`W25`), which is being built on this exact directory.**

⚠️ **Note what is *not* claimed:** ⛔ **this does not stop two documents describing
the same defect.** ⭐ **It stops two documents claiming the same *name* for
different defects** — which is the failure that re-points a citation silently and
turns nothing red.

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

#### ⛔ Ruling 107 — the marker check judges 40 of 84 documents and says so nowhere

⛔ **Measured 2026-09-10 at `6e80c82`:** `check_markers` runs only where
`kind == TASK_HANDOFF` (`tools/quality/handoffs/__init__.py`), so that directory's
**38 `ruling record`s, 3 `survey`s, 2 `session log`s and 1 `index` — 44 of 84
documents — are never read for markers at all.** ⚠️ **The 38 ruling records are
the CTO's and the PO's own rounds**, which is exactly where the findings that
ROUTE work are filed. ⛔ **The floor reports `0` across the whole directory, and
that `0` is the green report meaning *"I did not look"*** — this section's own
failure, occurring inside the instrument this section governs.

⭐ **It is also why the `[negative]` marker LOOKED invisible while not being the
cause: registering it changes nothing.** ⛔ **Measured both ways — 0 handoff
findings before the marker was added to the registry and 0 after** — ⚠️ **because
all three of its carriers are ruling records, and no marker in any of them has
ever been counted by anything.** ⭐ **The marker was a symptom; the kind filter is
the defect.**

⛔ **This needs a row, and its one hard part is named so the row is not scoped
blind: a ruling record whose SUBJECT is the marker vocabulary must be able to
spell the markers.** ⭐ Ruling 73's table already shows three of the four
mention-shapes are safe; the fourth — a line OPENING with a marker — is the shape
such a document most needs. ⚠️ **The remedy is not a weaker reader; it is an
exemption the document DECLARES**, the way `**Kind:**` is already declared.
⛔ **PO: mint.**

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
