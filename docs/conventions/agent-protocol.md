# Working agreement for agents

How a task is picked up, worked, and handed on. Applies to every task in
`docs/tasks/`.

## ⛔ TWO STANDING USER DECISIONS, and they change how a task ENDS

⛔ **NO REVIEWING OFFICE, NO VERDICT. EVERY ROW IS SELF-CERTIFIED BY THE OFFICE
THAT DID THE WORK.** ⭐ **EVERY DECLARED GATE is green at the ref that will
merge, read by ONE command with ONE exit code**, each reading carrying **ref +
checkout ROLE + ENVIRONMENT**, and the **expectation written BEFORE the
command**. ⛔ **Do not enumerate the gates from memory** (`W191`): a two-item
list is satisfiable by halves, and the floor can exit `0` while the suite does
not at one ref (Ruling 78). ⚠️ Then the
coordinator's release-tip measurement, after the merge. ⛔ **Self-certified is
not a lower bar; it is the same bar signed by a different office** — the runnable
block is in
[`review-rubric.md`](review-rubric.md#there-is-no-reviewing-office-and-no-verdict-every-row-is-self-certified)
and your handoff pastes it.

⛔ **RULING MINT FREEZE, THREE WAVES.** ⭐ **No new ruling unless a defect is
otherwise unpreventable; capacity goes to REACH — landing rulings that exist and
are cited nowhere.** ⚠️ **A finding whose remedy is *"a ruling should say this"*
is discharged by CITING the ruling that already does, or by naming the rule it
would become in a fixed spelling — never by minting a second copy that can
disagree with the first.**

⛔ **RUN EVERY GATE. STOP TRANSCRIBING READINGS INTO PROSE.** ⭐ **Every gate
runs unchanged and RED STOPS THE MERGE; what changes is the RECORD — a handoff,
brief or message reports a gate as `GREEN`/`RED` plus its exit code and quotes
NO figure from it.** ⚠️ **Exceptions and ground:
[`review-rubric.md`](review-rubric.md#run-every-gate-stop-transcribing-readings-into-prose-a-user-decision)
— the canonical home, and this is a pointer rather than a second copy.**

⚠️ **None of these is a ruling, and nothing in this document derives them.**
⛔ **Wherever a clause below says *the reviewer*, read it as the certifying
office; wherever it says *the verdict*, read it as the two gate readings.**

## Picking up a task

1. Read `docs/specs/2026-09-08-studyforge-v1-design.md` — §1–§4 and every
   ruling **R1–R21**. This is the authority you appeal to when the task is
   ambiguous. Do not invent a rule; if one is genuinely missing, say so in your
   handoff and proceed under a stated assumption.
2. Read your **epic document** — it carries the shared context for your task's
   neighbours, so you do not re-derive it.
3. Read `docs/conventions/module-structure.md`.
4. Read **only** the files in your task's *Context* field. ⛔ **Your search path
   is `git grep`, `grep -rn` and `sed -n`.** ⚠️ **There is NO code-graph or index
   tool in this project and no document may name one** — R14 required one and is
   WITHDRAWN IN PLACE in the spec (2026-09-12, user ruling). ⛔ **No context
   budget may assume an index exists.** If you need more files, note it in your
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

### ⛔ Ruling 268 (CTO round 58) — a grant of a decision ON A READING is decided BY THE READING, never by the row's menu of remedies

⭐ **A row that offers two remedies and says the choice is the taker's has granted a DECISION,
and where the row also says *the reading that decides between them is a build, not an
argument*, the grant is to the READING.** ⛔ **So a THIRD remedy the reading produces is inside
the grant, and a taker who takes it is obeying the row rather than exceeding it.** ⚠️ **A row
that meant otherwise has pre-empted the thing it said it was not pre-empting, and that is a
defect in the ROW.**

⛔ **What the taker owes, and it is what makes this a grant rather than an opening:** the
reading that killed each offered remedy, printed, and the reading that chose the third.
⭐ **MEASURED, CTO round 58, where the reading excluded BOTH offered remedies: a pinned `.deb`
added a FOURTH build-time host to buy nothing — three remotes were already required and the
first one's failure fails `apt-get update` two lines earlier — and a vendored font cost
**4 360 440** measured bytes plus a licence while still leaving three remotes.**

⭐ **Flag it as the first thing for the reviewer to attack.** ⚠️ **That is how the taker in
round 58 handled it, and the ratification followed the disclosure rather than the diff.**

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
>
> ⛔ **AMENDED, Ruling 153 (CTO round 40): `<worktree>/.scratch/` holds what a
> sweep WRITES, and it NEVER holds a CHECKOUT.** ⭐ **A trial merge, a second
> clone or any linked worktree is created OUTSIDE every checkout of this
> repository** — `review-rubric.md` §0a's `TRIAL=$(mktemp -d)/trial` was already
> right, and this clause never contradicted it.

⛔ **Why the amendment, and it is not hypothetical.** ⭐ **A second checkout of
this repository is not an artifact; it is another repository's tree, and putting
one inside the first makes every tree-walking instrument in the suite read two
repositories as one.** ⚠️ **Measured at one ref, in the pinned image, the only
difference being where the trial worktree lived:** a linked worktree under
`.scratch/` gave **`2 failed, 31 passed`** (`assert 44 == 88`, naming 44 files
belonging to the nested checkout); moved to a sibling with `.scratch/` empty,
**`33 passed`**.

⛔ **AND THE PART THAT MAKES IT A TRAP RATHER THAN A MISTAKE:
`git status --porcelain` PRINTED NOTHING IN BOTH CASES.** ⚠️ **`.scratch/` is
ignored, so Ruling 131's clean-tree instrument certifies a tree carrying 723
files of a second repository.** ⭐ **Do not expect the tree to warn you; put the
second checkout in `mktemp -d` and there is nothing to warn about.**

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
3  CONTROL  git check-ignore -v .scratch/probe.py
              -> exit 0, and it PRINTS its own location: `.gitignore:<n>:.scratch/`
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
   re-runs it and any other office reproduces it. ⛔ This is the half that makes
   it evidence instead of a claim.
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
verifies the author against the author. ⛔ **With self-certification that is no
longer a hypothetical — it is the ONE failure mode the standard has, and the
answer is that the INSTRUMENT is the gate, never the handoff.** ⛔ **Nor are
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

⛔ **The `tools/quality/handoffs/` PACKAGE runs this, so it is a build failure and not a
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
  ⭐ **`+` and `,` are ONE grammar and read the same here as they do on the
  board** ([`board.md`](board.md), Ruling 218's multi-id cell); ⛔ **any other
  joiner is REFUSED with the part in the finding, never quietly split** (`W192`).
- ⛔ **A row's id is the register's, never its branch's** ([PO round 76](../tasks/BOARD-ARCHIVE.md#po-round-76-the-rounds-closes-the-iso-pin-advanced-to-0d970fd-and-spec-5-amended)). A carrier branch may be named for the findings it settles; its handoff is
  still `<TASK-ID>.md`, declaring `task handoff — <TASK-ID>`, with the `W` id the register
  minted before the dispatch. ⭐ **So the floor's `TASK_ID` never meets a finding id.**
- ⛔ **A supervising office has no task ID, because the id space has ONE MINTER**
  — so it declares `**Kind:** office handoff — <SCOPE>`, where `<SCOPE>` is what
  its findings are numbered inside (`ARCH/1`) and ⛔ **must NOT parse as a task
  ID.** ⭐ **It owes everything a task handoff owes**: the title, the six
  sections and the markers. ⚠️ **It is not an escape hatch, and that is the
  whole point of adding it** — the alternative was an office declaring `survey`
  (*"nothing landed"*, false) or minting an id it does not own.

#### ⛔ Ruling 285(b) (CTO round 59) — a handoff cites a TRACKED DOCUMENT as a resolving POINTER, and the floor binds every handoff written after the pin

> ⛔ **(b) THE POINTER.** ⭐ **A document citing a frozen record, a row file or a ruling section
> cites it as a RESOLVING POINTER, never as a bare filename.** … ⭐ **Scoped deliberately: it
> binds a citation of a TRACKED DOCUMENT, never a test name, a symbol or a sha.**

- ⛔ **Write the link, not the name** — `` [`BOARD.md`](../tasks/BOARD.md) `` — and anchor it
  where the citation is to a section. ⚠️ **A test name, a symbol, a sha and a command are NOT
  citations of a document**, and the floor never reads them.
- ⭐ **Where the target is absent on your ref, the backticked NAME is right** (Ruling 308), and
  the floor agrees: it fires only on a name that resolves to a markdown document git tracks.
  ⛔ **WITH ONE EXCEPTION, AND IT IS YOUR OWN ROW** (`W315`): the register mints
  `docs/tasks/rows/<ID>.md` in the round that merges your branch, so the name is green here and
  the MERGE refuses it — measured, on `W313`'s refused merge and `W312`'s hand-back. ⭐ **Write
  the pointer anyway.** `check_pointers` DEFERS a handoff's link to the row it is the handoff
  FOR, so `docs/tasks/handoffs/<ID>.md` may link `../rows/<ID>.md` before that file exists, and
  the same sentence is green on your branch and after the merge. ⚠️ **Any OTHER row minted in
  the same round is cited by bare ID in prose — `W321` — and never by filename**; the deferral
  is one pointer per handoff, read off the citing document's own name, and is not a list.
- ⛔ **It is an arm of `check_handoffs`, and it binds a task or office handoff ABSENT from the
  tree at `citing.CITATION_PIN`.** ⭐ The frozen records are excluded by that REF, never by a
  list of filenames, so they are not back-filled (Rulings 106, 174). ⛔ **The pin is not a
  knob**: moving it to quiet a red handoff exempts that handoff; the repair is the link.
- ⭐ **The floor prints `n of m new handoffs`** (Ruling 48), empty population included.

#### ⛔ Ruling 176 (CTO round 45) — a new `DOCUMENT_KINDS` entry may be minted by any office ONLY IF it owes at least what the strictest existing kind owes

> ⭐ **A kind that owes MORE, or the same, is a contract being EXTENDED, and may
> be minted by whoever needs it and offered for ratification.** ⛔ **A kind that
> owes LESS is a widening of the ESCAPE SURFACE, and it needs the CTO BEFORE it
> is written, not after.**

⚠️ **The hazard is real and it is `W63`/`W64`: `check_markers` skips every
`ruling record`, so a kind that owes nothing is how a document leaves the
contract altogether.** ⭐ **`office handoff` is the OPPOSITE of that hazard, and
the CTO read the code rather than the claim to be sure: it owes the title, the
six sections and the markers — exactly what `task handoff` owes — with
`_check_office_identity` **INVERTING** the identity rule so that a `<SCOPE>`
which parses as a task ID is itself a finding.** ⛔ **It cannot be used to escape
anything.**

⭐ **The shape that does not rot, and it is why the ratification was cheap:** the
parametrised *owes-only-its-declaration* test excludes the new kind **by name**,
never by an exclusion list that a later kind joins silently.

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

#### ⛔ Ruling 273 (CTO round 58) — a record's FILENAME DATE is the date the record was WRITTEN, and a wrong one is DISCLOSED rather than renamed

⛔ **The date in `CTO-<date>-roundN.md` is the day that record was written — never copied
forward from the previous round's brief.** ⚠️ **MEASURED, CTO round 58:
`CTO-2026-09-10-round57.md` was written on 2026-09-11, its filename says `-09-10`, and the
coordinator disclosed it.** ⭐ **The forward-looking half is a MERGE OBLIGATION on the office
that writes the record, not a row.**

⛔ **AND THE WRONG ONE IS NOT CORRECTED, on a ground four deep — this is the part a later
office reaches for and must not:**

1. ⛔ **Ruling 106: a record is corrected by ANNOTATION, and a filename is part of a record's
   bytes.**
2. ⛔ **Ruling 174 and Ruling 270's wall: a rename RE-ADDRESSES it.** ⚠️ **MEASURED at that
   merge: 855 pointers, 0 unresolved — a rename breaks every pointer at that file and the
   repairs would land INSIDE frozen records, for a cosmetic gain.**
3. ⭐ **The record's own as-ofs do not resolve through its filename.** Every reading inside it
   names its REF, which is what Ruling 260 actually requires, and a ref is strictly stronger
   than a date.
4. ⭐ **A disclosure in a LIVE document reaches a reader the way an annotation does.**

⚠️ **So Ruling 260 is NARROWED rather than contradicted: a record's date is how its as-ofs
resolve, 260 is satisfied by the REF, and the filename is an ADDRESS.**

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
not *work in flight*. ⚠️ An absent generated directory says *this checkout has
not built one*, not *the built one is stale* — ⭐ **which is Ruling 108 arriving
as a special case of this clause rather than as its own fact.**

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

#### ⛔ Ruling 155 (CTO round 40) — the two markers, in a FENCE, because the prose above was not enough

⚠️ **Everything Ruling 155 says is already stated in the prose above, and it was
misused anyway — by two different offices, in consecutive rounds, one round
after the CTO wrote that it was wrong.** ⛔ **`PO-31/9` and `PO-32/7` both put
the none-marker on a **recorded negative** standing beside eight or nine real
findings.** ⭐ **Two rounds, two offices, the same misuse means the vocabulary
was missing a word rather than a scolding, so here it is in the form Ruling 73
says a rule this cheap to break must take:**

```text
[none]   — there was nothing outside this task's scope to report. A claim about
           the EMPTINESS of the findings list; it may not stand beside a member
           of it.
[local]  — a finding, INCLUDING a recorded negative: "checked, not assumed; the
           thing I expected to find is not there." CTO-39/5, CTO-39/6, CTO-39/7
           and SK-08/4 already spell it this way.
```

⛔ **The fence is load-bearing rather than decorative:** §8a's counter reads a
marker that OPENS a line as a finding, ⚠️ **and Ruling 148 proved the checker
cannot fire on a `ruling record` at all** — which is the one document class both
offences were committed in. ⭐ **Ruling 73's answer to a check that cannot see a
shape is the fence, not a weaker check**, and that is why this is written here
and not routed to `check_markers`.

> ⛔ **DATED BY `W172`, CTO round 72 — the sentence above is TRUE OF ITS OWN REF
> AND FALSE OF THE TREE, and it is not edited** (Ruling 106's form, and Ruling 335:
> the office whose task falsified it may not edit it, and the register that owns
> the sentence lands the repair as a POINTER). ⭐ **`W172` shipped Ruling 218's
> gate three: a record's markers ARE now read, inside its Findings section.**
> ⚠️ **Do not take a count from here. The current answer is whatever the shipped
> reader returns — `tools/quality/handoffs/` owns it, and it resolves at read
> time where a typed figure cannot:**
>
> ```bash
> python3 -m tools.quality 2>&1 | grep -E '^(handoff|document)'
> ```
>
> ⛔ **MEASURED at the wave-11 cumulative tree: the reader returns `8` marker
> lines on one ruling record**, so *cannot fire at all* names a behaviour the tree
> no longer has. ⭐ **The FENCE below is UNAFFECTED and still the right advice** —
> its ground was never that the checker was blind, it was that a marker opening a
> line reads as a finding, which `W172` did not change.

⛔ **This is a CORRECTION, not new scope.** ⭐ **`W63` and `W64` remain the
mechanism and their ruled order is unchanged** — and `PO-32/3` sharpens the case
for them past what Ruling 148 said: **76 finding lines across 12 documents**, and
`_FINDING_LEAD` refuses a backticked ID **even inside a task handoff**.
⚠️ **So the contract is not merely *unenforced on ruling records*; it is
*unreadable* wherever the offices' actual format is used.**

#### ⛔ Ruling 158 (CTO round 41) — a ruling that STRIKES a field enumerates its readers and PRINTS the enumeration

> ⛔ **A ruling that strikes a field, a check, a clause or a row enumerates its
> READERS and prints the enumeration.** ⭐ *"No instrument reads it"* is a claim
> about **EMPTINESS**, which Ruling 155 above already says is the claim most in
> need of a population. ⚠️ **An emptiness claim is discharged by a printed
> population of ZERO, never by not having looked.**

⛔ **THE INSTANCE, AND THE CTO FILED IT AGAINST THEMSELVES.** Ruling 154's second
call struck `workspace.json`'s `self` commit on the ground that
`tools.workspace verify` does not read it. ⭐ **The PO re-derived the claim
instead of carrying it (`PO-33/7`) and printed the readers:**

```text
tools/workspace/__init__.py:293   if not holds(directory, component.commit):     # every row, self included
tools/workspace/__init__.py:299   if component.where == "self":
tools/workspace/__init__.py:302       if not is_ancestor(directory, component.commit, head):
tools/workspace/__init__.py:49-54 "equality is *unrepresentable* rather than merely unchecked"
```

⛔ **`self`'s commit is read TWICE, and the module's own docstring states why the
weaker predicate is the strongest TRUE one available.** ⭐ **RULING 154'S SECOND
CALL IS WITHDRAWN**: `W72` does the `pinned`/`tracked` split only, `self`'s
commit stays, and `PO-33/7` is **upheld**. ⚠️ **What remains true is the
observation underneath it — an ancestor predicate cannot go red for a
stale-but-ancestral commit, so the field is WEAKLY checked, not unchecked** —
⛔ **and striking it would have deleted the one check that fires if history is
rewound or rewritten, while citing a ruling.**

⭐ **The finding is the MECHANISM, not the error: it was caught by re-deriving a
received claim instead of carrying it**, the same move `PO-32/9` made against its
own carry table. ⚠️ **Second consecutive round in which re-derivation caught the
CTO, which is a pattern worth naming rather than a coincidence worth forgiving.**

#### ⛔ Ruling 163 (CTO round 42) — a LIVE document may not cite `<file>:<line>` into a file it does not own; cite the COMMAND and its OUTPUT SHAPE

> ⛔ **A document may not cite `<file>:<line>` into a file it does not own,
> where an instrument exists that prints the location itself.** ⭐ **Cite the
> command and its output shape, never the integer.**
>
> ⭐ **This is Ruling 136 GENERALISED, and the generalisation is the point.**
> ⚠️ **The class is not *"board cells"* — it is *a fact about a MUTABLE FILE,
> recorded where NOTHING RE-MEASURES IT*.**
>
> ⛔ **The boundary, so this is not a ban on citations.** A line number is
> **admissible inside a RECORD** — a handoff, a ruling, a review — because a
> record is a reading taken at an instant and is annotated, never edited
> (Ruling 106). ⛔ **It is INADMISSIBLE in a LIVE document, which is read as
> current.**

⛔ **THE INSTANCE, AND IT WAS THIS FILE.** Line 94 above cited *"matched by
`.gitignore:48`"*. ⚠️ **`W68`'s own `.gitignore` amendment moved the rule to line
64 in the same round**, so the citation was correct when written and wrong at the
merge ref, with nothing re-measuring it. ⭐ **The remedy is the instrument's own
output, and it is now what line 94 says:**

```text
git check-ignore -v .scratch/probe.py   ->  .gitignore:<n>:.scratch/    exit 0
```

⚠️ **THE LIVE POPULATION IS 105, NOT 1** — swept by the PO at round 35 over the
**36 live documents** (`docs/**.md`, `CLAUDE.md`, `README.md`, records and the
board archive excluded), spelled to include extensionless dotfiles:

```text
docs/tasks/BOARD.md              83     docs/conventions/review-rubric.md     3
docs/tasks/E00-foundations.md     6     docs/tasks/E03-rendering.md           2
docs/conventions/agent-protocol.md 6    docs/tasks/E05-serving-execution.md   1
docs/tasks/E01-core-contracts.md  4                              TOTAL      105
```

⛔ **So Ruling 163 is a ROW, not a one-line edit** — the one line it names is
landed here, and the class is `W78` on the board. ⚠️ **Four of this file's own
six are the fenced `tools/workspace/__init__.py:293…` reading in the Ruling 158
section above: a RECORD quoted inside a LIVE document, which is the sub-case the
row must decide rather than assume.**

#### ⛔ Ruling 169 (CTO round 43) — a fenced reading inside a LIVE document is admissible **iff it names its ref**

> ⭐ **The FENCE is not what makes a record admissible. The REF is.** A record is
> admissible because it is a **transcript of what a command printed at a named
> ref** — it does not claim *where the code is*, it claims *what was read, then*.
> ⛔ **A fence carries no such claim. A bare fenced line number is a live citation
> wearing a costume, and it goes stale in exactly the way clause 1 exists to
> prevent.**
>
> **The clause:** a `<file>:<line>` citation inside a fenced block in a **live**
> document is admissible **if and only if the same block names the ref or the
> date the reading was taken at**. ⭐ **The remedy for a bare fenced line number
> is to ADD THE REF, never to delete the reading — the reading is the valuable
> half.** ⛔ **Outside a fence, clause 1 binds unchanged.**

⭐ **The evidence was collected by accident, in the round that decided it:** the
CTO's round-43 brief cited *"`W66`'s `Owns` cell (`BOARD.md:3964`)"*. ⛔ **In the
live board that cell is at line `4374` — a drift of 410 lines inside ONE
ROUND**, because `chore/po-round35` added 466 lines above it. ⚠️ **The citation
was wrong before it was read, and the cell was findable only by searching for
its content.**

⛔ **`W78` therefore RE-SWEEPS before it edits.** ⚠️ **The population of `105` was
measured at `911c56f`; `W76` renamed `render/page/text.py`, which
`BOARD.md`'s `W66` block cites by path AND by line, so the class changed under
the same merge that answered the question** (`CTO-43/3`). ⭐ **Roughly four
instances are admissible once they carry a ref; the rest lose the number.**

#### ⛔ CTO round 42, `CTO-42/6` — a reviewing round RE-READS the branch list immediately before writing its verdict section, and records BOTH readings

⛔ **A close-time reading of another office's branch is UNKNOWABLE at the instant
it is taken.** ⚠️ **`git rev-list --count release/m0-foundations..<branch>` read
`0` and read `1` minutes later — three rounds running, predicted in the third
round's own body and happening anyway.** ⭐ **A defect that can be predicted and
not prevented is not a reading error; it is a MISSING HANDSHAKE**: the reviewing
office has no signal for *"this branch is finished"* other than a commit count,
which is indistinguishable from *"not started"* and from *"committing right
now"*. ⛔ **Two readings a minute apart would have caught all three instances.**

⭐ **IT WORKED, on its first application, against its own carrier.** `PO-35/8`:
`W76` read `+0` at wave-open and `+3` (`a65b476`) at close, and the placement
argument for `SF-14` changed as a result. ⭐ **It fired again at CTO round 43's
close, on `chore/board-architecture` (`wt/arch`, `+0`), which NO brief had
named.** ⛔ **The clause is neither weakened nor widened.**

#### ⛔ Ruling 168 (CTO round 43) — a round RE-READS ITS OWN MINTS after its annotation's merges land, and strikes any whose condition is already true

> ⛔ **`CTO-42/6` above checks BRANCH STATE and could not have caught what
> happened next.** ⚠️ **CTO round 42's body minted Ruling 165 — *`SF-14` is not
> dispatched until its Acceptance clause is split* — while the split had ALREADY
> LANDED**, in `753eb26`, merged `18861ae`, an ancestor of the round's own base.
> ⭐ **The round's OWN ANNOTATION merged the branch that discharged it, and the
> body was never re-read.**
>
> **The clause:** a round that mints rulings **re-reads its own mints against the
> tree after its annotation's merges have landed**. ⛔ **Any mint whose condition
> is already satisfied is STRUCK IN THE ANNOTATION, in the annotation's own
> words, beneath the standing text** (Ruling 106).

⚠️ **A ruling left standing in a body that a later annotation invalidated is not
a stale sentence — it is a LIVE INSTRUCTION to the next office, and the next
office will carry it rather than measure it.** ⛔ **That is precisely what
happened: the CTO relayed Ruling 165 to the PO as a live blocker on `SF-14`
(`CTO-43/1`), and step 2.3's last row would have sat blocked for a round had the
PO carried the brief instead of measuring it** (`PO-35/1`). ⭐ **A process that
survives only because the office downstream distrusts the office upstream is not
a process. This clause is what makes the distrust unnecessary, and it is the
PO's own wording.**

#### ⛔ Ruling 171 (CTO round 43) — for in-flight rows `git worktree list` is PRIMARY and `git log` is the CORROBORATOR

> ⛔ **Ruling 130's two instruments disagreed by one row for THREE consecutive
> rounds in the SAME DIRECTION** (`PO-35/2`, asked twice). ⭐ **The mechanism is
> now understood rather than merely observed: `git log` cannot see a row that has
> been dispatched and has not yet committed, and EVERY dispatch opens that
> window.**
>
> **The clause:** ⭐ **`git worktree list` is the PRIMARY instrument for in-flight
> rows; the `git log` walk over the branch list is the CORROBORATOR, not the
> reverse.** A disagreement in which `worktree list` finds a row `git log` does
> not is the **EXPECTED** reading for a dispatched row before its first commit,
> and is reported as such rather than as a discrepancy. ⛔ **A disagreement in
> the OTHER direction — a branch ahead of release with no worktree — is a real
> finding and is chased.**

⭐ **`CTO-42/6`'s amendment is hereby promoted from a caution to a clause.**

#### ⛔ Ruling 172 (CTO round 43) — a measurement PROVES WHICH TREE IT READ, in the same invocation as the number

> ⛔ **`docker/dev/check` derives `ROOT` from where the SCRIPT SITS, not from the
> caller's working directory:** `ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)`.
> ⚠️ **So `$OTHER_TREE/docker/dev/check` invoked from inside the base tree
> measures `$OTHER_TREE`.** ⭐ **`W76`'s first base collection did exactly that
> and was caught only by a human noticing *"the numbers were identical when they
> could not be"* — a proxy defect inside the ONE instrument this project treats
> as authoritative** (`CTO-43/4`).
>
> **The clause:** a base reading and a merge reading prove which tree each was
> taken in, **from inside the same container invocation as the number**:
>
> ```sh
> ./docker/dev/check sh -c 'git rev-parse HEAD; python3 -m tools.quality'
> ```
>
> ⭐ **The sha and the number are then ONE reading and cannot be paired wrongly.**
> ⛔ **Two readings that agree on every number are not evidence of anything until
> they have printed two DIFFERENT shas.**

⚠️ **A base and a merge that agree for the wrong reason is the single failure
this review protocol cannot detect from its own output** — every other clause
here assumes the two readings came from two trees.

#### ⛔ CTO round 42, `CTO-42/8` — a REF written into a verdict is READ BACK, and `git rev-parse` is not the instrument

⛔ **A ref recorded in a verdict, a close or a handoff is verified with
`git cat-file -e <ref>^{commit}` and its exit code read WITHOUT A PIPELINE.**

```text
git rev-parse e6e4d51 2>&1 | tail -1              -> prints "e6e4d51"   ⛔ reads as SUCCESS
git rev-parse --verify e6e4d51^{commit} | tail -1 -> exit 0             ⛔ the pipeline trap
git cat-file -e e6e4d51^{commit}                  -> exit 128           ⭐ the real answer
```

⚠️ **`git rev-parse` on a well-formed-but-unknown sha ECHOES THE STRING BACK**,
so a reviewer checking a ref that way confirms every ref, including invented
ones. ⛔ **Ruling 84 already requires confirming the tip MOVED; it does not
require that the recorded ref BE the tip. Those are different checks, and it is
possible to pass the first while failing the second** — which is how a
**prediction formatted as a measurement** reached a verdict table.

⭐ **Reproduced by the PO at round 35, seven refs, exit codes read with no
pipeline:** six real refs → `0`, `e6e4d51` → `128`.

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
python3 -m tools.quality.handoffs           # the triage list, before a wave (W106)
```

⛔ **This document types no marker pattern: the reader holds the vocabulary.**
It prints every line, a finding or in-text, and the floor refuses a weak
pattern typed into a convention.

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

### ⛔ `W143` — restore a plant FROM A COPY taken before it, per FILE. Never with `git checkout`

⛔ **`git checkout -- <path>` restores to `HEAD`, not to the working tree you
had.** ⚠️ **Over a DIRECTORY it silently discards an UNCOMMITTED repair in a
NEIGHBOURING file your plant never touched — and `git status --porcelain` then
reads CLEAN, because the tree does now match `HEAD`.** ⛔ **It has already cost
this project real work, in the wave it was found in, to an office following the
standing guidance exactly as written.**

⛔ **THE COMMAND AND ITS PASS CONDITION:**

```bash
# ⛔ BEFORE the plant. The baseline comes from the WORKING TREE, per FILE — never
#    from `HEAD`, and never from `git show`. A HEAD-derived baseline AGREES WITH
#    THE LOSS: measured, it reported every file OK after the repair was destroyed.
BAK=$(mktemp -d)                              # ⛔ outside every checkout (Rulings 139, 153)
md5sum $SUBJECTS > "$BAK/plant.md5"           # ⭐ $SUBJECTS = every file the restore touches
for f in $SUBJECTS; do cp "$f" "$BAK/$(echo "$f" | tr / _)"; done

#    … plant, run, read the effect …

# ⛔ THE RESTORE: from the COPY, per FILE, on the HOST — the container cannot restore
#    at all (Ruling 287). ⛔ NOT `git checkout -- <dir>`, and not `git checkout` at all.
for f in $SUBJECTS; do cp "$BAK/$(echo "$f" | tr / _)" "$f"; echo "RESTORE_EXIT=$?"; done
md5sum -c "$BAK/plant.md5"; echo "MD5_EXIT=$?"
```

⭐ **PASS: every file `OK` and `MD5_EXIT=0`.** ⛔ **`git status --porcelain` is
NOT the pass condition here and may not be quoted as one** — ⚠️ **it is the
instrument that agreed with the loss.** ⭐ Keep reading it for what it *can* see:
a plant taken from another ref stages the index, and porcelain shows that where
`md5sum` cannot.

⛔ **WHY THE TWO REMEDIES YOU ALREADY KNOW DO NOT COVER THIS:** ⭐ **Ruling 202
(*commit before planting*) is stated from the AUTHOR's side** — it protects the
file you are about to plant IN, and says nothing about a neighbour, while a plant
over a whole suite naturally takes a directory-wide restore. ⭐ **Ruling 287
(*read `porcelain` after restoring*) was obeyed on the run that lost the work,
and `porcelain` read clean.** ⛔ **Both standing remedies PASS on the failing run;
only a working-tree `md5sum` baseline fails.**

⚠️ **Its relationship to Ruling 287, since 287 sends you to the host as the safe
place:** ⭐ **same class — a silent restore — different mechanism, different
environment.** 287 is the CONTAINER refusing to restore and leaving the plant in
place, caught by an unread exit code; this is the HOST restoring **successfully**
to the **wrong state**, where no exit code anywhere reports it.

⛔ **THE SCOPE IS THIS PROTOCOL AND NOT `git checkout`.** ⭐ `git checkout --
<path>` is correct for what it does; the defect is a procedure that uses a
restore-to-`HEAD` where it needs a restore-to-the-tree-I-had. ⚠️ **And it is not
a reason to stop planting** — Ruling 123's three readings are how this project
inhabits its negative arms. ⭐ **The demonstration, both directions, with the
`HEAD`-baseline control shown REFUSING to find the loss, is the review rubric's
§4c.**

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
mode.** ⚠️ **Measured instance:** a convention document said a command was in
`FND-02`'s handoff; that handoff said it was in the convention. ⛔ **Neither had
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

**2a. And a bare `(Ruling N)` is resolvable, in one hop.** ⛔ **Every office is
told to appeal to rulings by number and forbidden to read the handoff chain end
to end, and for most of the series the number resolved for nobody** (`W91`,
`CTO-48/3`). ⭐ **So: [`../tasks/rulings-index.md`](../tasks/rulings-index.md) —
one row per numbered ruling, the record's own words QUOTED, and an anchored
address for the section that carries them.** ⚠️ **It is GENERATED
(`python3 -m tools.quality.rulings`) and the quality floor fails while it is
stale, so a ruling either has a row or the build is red.** ⛔ **Quoting from
there is quoting the record: it holds no summary for anyone to relay, which is
what clause 2 asks for.**

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

### ⛔ A disposition that can still CHANGE is ADDRESSED on the board, never held in a record

⛔ **Quoted from [`W103`](../tasks/rows/W103.md), whose argument it is:**

> ⭐ **A finding whose disposition can still CHANGE is recorded in the handoff and
> ADDRESSED on the board.** ⛔ **The record keeps the finding and the reading; the
> board keeps the state.**

- ⚠️ **A disposition written in a handoff (`⚠️ OPEN`, `✅ RULED`) is true at that
  record's ref and no later.** ⛔ **When it moves, the record is not edited**
  (Ruling 106).
- ⭐ **An annotation goes beneath instead.** It names the ref it was taken at and
  the artifact that moved the state, and it **points** at where the live state is
  held: a board row, or the Acceptance, epic clause or spec ruling a row names.
  ⛔ **It does not copy the state**, because a copy in a record is the defect again.
- ⛔ **This is not a sweep.** It binds when a moved disposition is found. It does not
  re-open every marker in the project.

⭐ **Worked reference:** [`FND-04`'s annotation](../tasks/handoffs/FND-04.md#annotation-w103-taken-at-71ae733-finding-3-is-closed-elsewhere-finding-7-is-addressed-elsewhere).
Finding 3 had been closed by R21's register while its record still read `OPEN`.

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

> ⛔ **DISCHARGED AND DATED BY `W172`, CTO round 72 — `W172/4`.** ⭐ **The row was
> minted, taken, and shipped as Ruling 218's gate three; this section is annotated
> beneath rather than edited** (Ruling 106, Ruling 335).
>
> ⚠️ **TWO SENTENCES ABOVE ARE NOW FALSE OF THE TREE and both stand unedited.**
> ⛔ *"44 of 84 documents are never read for markers at all"* — a ruling record's
> Findings section IS read now. ⛔ **And the count is doubly dated: it is a typed
> figure over a directory that has grown every wave since** (Ruling 181). ⭐ **Ask
> the reader, which resolves at read time where a figure cannot:**
>
> ```bash
> python3 -m tools.quality 2>&1 | grep -E '^handoff'
> ```
>
> ⛔ **AND THE NAMED REMEDY WAS SUPERSEDED ON A MEASUREMENT, which is the part a
> later reader would otherwise implement.** ⚠️ *"an exemption the document
> DECLARES"* was refused by the row that discharged it: **a declared exemption is
> an off-by-default gate — a check that cannot fail, which is `W37`'s subject —
> and it would need an edit inside every record that carries a marker.** ⭐ **What
> shipped instead is a STRUCTURAL predicate: the markers are read inside a
> record's Findings section and nowhere else**, so no record is edited and no
> document can switch the check off.
>
> ⭐ **MEASURED by that row over 110 ruling records:** the fully widened rule fires
> **181** times in 53 documents; restricted to the Findings section, **27** in 7;
> restricted further to lines claiming a scoped number, **0**. ⛔ **The 27 all sit
> inside records, so a gate printing them would hold the floor red forever — which
> is why the corpus is never chased and the instrument is the subject** (Ruling 193).

## Reporting

Report outcomes faithfully. ⛔ **A gate is reported as `GREEN` or `RED` plus its
exit code, and its figures are NOT transcribed** (the rule and its exceptions are
in [`review-rubric.md`](review-rubric.md#run-every-gate-stop-transcribing-readings-into-prose-a-user-decision)).
⚠️ **If a gate is RED, say which bound broke and by how much — that figure IS the
subject.** If you skipped part of the scope, say which part and why. Do not
describe work as complete before it is verified — run the command and read the
result. ⭐ **Evidence before assertions, always: the evidence is the exit code you
read, not a number you retyped.**

## Escalating

Stop and ask rather than guessing when:

- Two rulings genuinely conflict on your task.
- Your task's acceptance cannot be met without changing another task's surface.
- You would need to modify a pre-existing file in a consumer repository (R3).
- The work turns out substantially larger than the task describes — that is a
  planning defect, and re-planning is cheaper than an overrun.

Refining a task as the project grows is expected and welcome. Silently
expanding one is not.
