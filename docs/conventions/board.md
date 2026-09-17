# The board — its structure, and the contract for growing it

⛔ **This document governs `../tasks/BOARD.md`'s SHAPE.** ⭐ **It does not govern
its content**: what is open, in what order, and who owns it stay the Product
Owner's, and nothing here overrules a priority call. ⚠️ **What it does overrule
is the habit of recording that call *in the board*.**

## ⛔ The board reached 8,545 lines, and the rule that would have stopped it was already written

⭐ **`delivery-flow.md` has said since it was written that a status change is
ONE CELL, and that an event goes to the Log rather than into the tables.**
⛔ **Nothing enforced it.**

⛔ **This document types NO measurement of the board, and Ruling 181 is why:**
⭐ **a document governing a SHAPE may not carry a typed measurement of that
shape.** ⚠️ **Five were typed here and all five were stale at merge** — which is
`ARCH/2`'s own defect recurring inside `ARCH/2`'s remedy, and it is the
*"live board ~56KB"* sentence this office was created to kill, reappearing in
the document written to kill it.

⭐ **Every live number is PRINTED, on every floor run, by `board_state`:**

```text
$ python3 -m tools.quality | grep '^board:'
board: <rows> register rows, <live> live, <files> detail files in docs/tasks/rows/;
       <bytes> bytes narrative of 8192, widest row <bytes> of 600,
       <bytes> bytes total of <allowed> allowed.
```

⚠️ **The before/after readings that argued for this split are a RECORD, taken at
`bfb8c8c`, and they live in
[`../tasks/handoffs/BOARD-ARCHITECTURE.md`](../tasks/handoffs/BOARD-ARCHITECTURE.md)
beside the ref they were taken at** (Ruling 169). ⛔ **Do not copy them here: the
next reader would check them, and this document has no way to keep them true.**

⚠️ **The split was already tried once.** ⛔ **Round 25 moved the closed sections
out for exactly this reason, wrote *"live board ~56KB"* in the file, and twelve
rounds later that sentence was wrong by more than an order of magnitude in the
document every agent is told to read first.** ⭐ **A restructure with no instrument
regrows**, which is why the second half of this document is a check rather than
a paragraph.

## ⭐ One fact, one home — the whole contract in one table

⛔ **When a fact changes, EXACTLY ONE file changes.** ⚠️ **If you find yourself
writing a sentence on the board that also exists behind one of its pointers, one
of the two is wrong, and it is a finding.**

| The fact | Its one home | ⛔ Never |
|---|---|---|
| a task's **definition** — `Owns`, `Depends on`, Acceptance, `Effort` | the epic, `../tasks/E00`…`E13` | the board, and not a brief either (Ruling 136) |
| a task's **step membership** | `../tasks/README.md` | the board |
| a row's **state** — `todo`, in flight, in-review, `done`, blocked | ⭐ **the board, and only the board** | a handoff, a commit message, a chat line |
| a row's **naming** — the one line that says which row this is | ⭐ **the board's register cell** | the row's detail file, which is titled by its id alone |
| a **live** row's argument — why it exists, what would settle it, what it is gated on | `../tasks/rows/<ID>.md` | the board; and ⛔ **never the archive, because a live argument is AMENDED and a record may not be** |
| a **closed** row's argument | `../tasks/BOARD-ARCHIVE.md` | anywhere it could be edited |
| a **round's** reasoning — placements, close runs, mint arguments, carried rulings | `../tasks/BOARD-ARCHIVE.md` | ⛔ **the board. This is the one that produced 8,133 lines** |
| a **process** — how a wave opens, what check 4 does | ⭐ **this document** | the board: a process is not a state |
| a **contract version** | the spec's §R9 register | the board, which points at it |

## ⛔ What a register row may carry, and it is five things

> **id · naming · owner · state · pointer.**

- ⛔ **No measurement.** Not a line count, not a file count, not a test count.
  ⚠️ **A measurement is a reading with an as-of** (`PO-30/2`), and a reading
  written into a register is a reading nobody will re-take.
- ⛔ **No ref except a merge ref.** A merge ref is part of the state *`done`*;
  every other ref belongs to the argument that quoted it.
- ⛔ **No reasoning.** ⭐ **The naming says WHICH row this is. It does not say why
  the row is right** — that is what the pointer is for.
- ⛔ **No struck-through history.** ⚠️ **A correction that leaves the original
  standing is not a correction; it is a second copy, and the reader takes the
  first one.** ⭐ **Replace the cell. The previous reading is in the archive with
  the round that took it.**

⭐ **`BOARD_ROW_CEILING` is 600 bytes and it is not arbitrary: it is the width at
which a cell stops being a naming and starts being an argument.**

### ⛔ The register is DELIMITED, and the marker is not decoration

```
<!-- register -->
| # | Row | Owner | State | Detail |
…
<!-- /register -->
```

⚠️ **The first version of the check inferred the register — *any five-cell row
whose first cell names a `W` id* — and the very next edit broke it.** ⛔ **An
*In flight* table naming four rows was read as four DUPLICATE register rows, and
`board-duplicate` fired on the author of `board-duplicate`.** ⭐ **A board may
hold as many `W`-shaped tables as it likes; exactly one of them is the register,
and it SAYS SO.** ⛔ **An inferred boundary is a boundary that moves the moment
somebody writes an ordinary table.**

### ⛔ A cell may name SEVERAL rows, and there is ONE spelling of it — Ruling 218's multi-id cell

⭐ **The separators are `+` and `,`, and that is the whole grammar.** ⛔ **Markup is
not part of an id**, and the order the cell writes them in is the order they are read
in — so `` `W17` + `W19` `` and `` `W17`, `W19` `` name the same two rows.

⛔ **THE GRAMMAR HAS ONE HOME AND IT IS AN INSTRUMENT, NOT THIS PARAGRAPH:**
`tools/quality/ids.py`. ⭐ **Every reader of a multi-id cell calls it** — the
register's parser, the In-flight table's parser, and the `**Kind:**` line of a handoff
([`agent-protocol.md`](agent-protocol.md)) — ⚠️ **so a cell cannot mean one thing to
the board and another to the floor.**

⛔ **THE DEFECT IT CLOSES, and it is why the spelling is DECLARED rather than left to
each reader.** ⚠️ **The comma form parsed as ONE id and took the LAST, so a cell naming
two rows silently observed the WRONG one — not the second-best row and not no row —
with no notice and exit `0`.** ⭐ **A second reader was its exact INVERSE and refused
the `+` form the handoff title check demanded**, so closing two rows in one round
required writing BOTH spellings into one file and no instrument could see it.
⛔ **Those readings are [`W192`](../tasks/rows/W192.md)'s and are quoted there with the
refs they were taken at.**

⚠️ **A JOINER THIS GRAMMAR DOES NOT DECLARE IS NOT A SEPARATOR, and the readers part
there deliberately.** ⭐ **The board's readers still name EVERY id in such a cell and
never take the last** — reading more than is declared is the direction that cannot be
silently wrong — ⛔ **while a handoff's `**Kind:**` line REFUSES the part BY NAME,
because every part of that line claims to be a task id.** ⛔ **And a RANGE is not a
multi-id cell: no reader expands `` `W177`–`W181` ``, so a cell meaning five rows names
five.**

## ⭐ How to add to the board, by the four things a PO actually does

| You are | Do this | ⛔ Not this |
|---|---|---|
| **minting a row** | one register line, and `../tasks/rows/<ID>.md` with the argument — ⭐ **BORN WITH AN ANCHORED POINTER TO ITS ARGUMENT** (Ruling 244(e)) | a mint section on the board, or ⛔ **a row file carrying no `](…#…)` back to the argument that minted it** |
| **changing a state** | ⭐ **replace the state cell** | append the new state beneath the old one |
| **re-scoping a live row** | edit `../tasks/rows/<ID>.md` — ⭐ **it is a live document and editing it is the point** | annotate the board |
| **closing a row** | ⛔ **FOUR edits** (Ruling 201 added the fourth; ⭐ **Ruling 270 changed the third**; ⛔ **`W185` changed the FIRST — see below**). ⭐ set the state to `done` with its merge ref and ⛔ **LEAVE THE DETAIL CELL WHERE IT IS**, pointing at `rows/<ID>.md`; move `rows/<ID>.md`'s body under a `### <ID> — <naming>` heading in `BOARD-ARCHIVE.md`, **re-addressing its `](../BOARD-ARCHIVE.md#…)` links to `](#…)` now that they are inside it**; ⛔ **REPLACE the row file with a REDIRECT STUB — never delete it** (Ruling 270, below); ⛔ **re-point every INBOUND citation of `rows/<ID>.md` in a LIVE document at the archive record** — see Ruling 201 below | leave the row file behind **with its argument still in it** — ⛔ **`board-orphan` will say so** — ⛔ **DELETE it, which breaks every FROZEN pointer at it and no office may repair those** — leave either link pointing where it used to, or ⛔ **leave a backticked `rows/<ID>.md` standing in live prose or code, which NO instrument can see** |
| **writing a round** | ⭐ **`BOARD-ARCHIVE.md`, appended** — and the board's cells change to match | a `## ROUND n` section on the board |

⛔ **The archive is a RECORD: it is appended to and corrected by annotating
beneath, never by editing** (Ruling 106). ⭐ **That is precisely why a live row's
argument may not live there** — and it is the whole reason `rows/` exists rather
than one more archive section.

### ⛔ `W185` (PO round 59) — A CLOSE MAY NOT GROW THE BOARD, SO THE DETAIL CELL OF A CLOSED ROW STOPS MOVING

⛔ **THIS IS A CLAUSE, NOT A RULING.** ⭐ **The mint freeze is in force and no defect here
was otherwise unpreventable; the decision is the register's own procedure, so it lands in
the register's own convention.**

⛔ **THE DEFECT IT SETTLES.** ⭐ **Edit one used to RE-POINT a closed row's Detail cell from
`rows/<ID>.md` at the archive anchor, and an archive anchor is the row's whole NAMING
slugified.** ⚠️ **So every close made the board PERMANENTLY LONGER by an amount
proportional to how well the row was named, and a long descriptive naming — which the
register is otherwise right to want — was the expensive case.** ⛔ **`PO-58/10` measured a
round OVERRUNNING `board-size` by 257 bytes before one word of STATE was written, and the
same round breached and repaired four times.**

⭐ **THE DECISION.** ⛔ **A close leaves the Detail cell exactly as it was born: `[`rows/<ID>.md`](rows/<ID>.md)`.**
⭐ **Ruling 270 already guarantees that file is a REDIRECT STUB whose whole argument is one
anchored pointer onward, so the reader still lands on the argument — in two hops instead of
one, and never on a search.**

⛔ **ASSERTED IN BOTH DIRECTIONS (R12), because one direction alone is satisfiable by doing
nothing:**

| the property | ⛔ what asserts it |
|---|---|
| **a close must not GROW the board** | ⭐ **`board-detail`, in `tools/quality/board/bijection.py`** — a closed row's Detail cell must EQUAL `born_detail(<ID>)`, and never an archive link. ⚠️ **The arm was owed by [`W185`](../tasks/BOARD-ARCHIVE.md#w185-the-close-procedure-and-board-size-are-jointly-unsatisfiable-owes-a-design-decision) and is DISCHARGED** |
| **the reader must still LAND ON THE ARGUMENT** | `board-orphan`'s Ruling 270 exception, unchanged: a closed row's file must EXIST and must BE a stub with a resolving archive anchor. ⭐ **Two instruments already hold this half — `bijection.py` and the pointer floor — so this direction is asserted today** |

⛔ **THE REFUSALS ARE RECORDED SO THE NEXT ROUND DOES NOT RE-DERIVE THEM:**

1. ⛔ **RAISING A TERM IS REFUSED** — Ruling 271 refused all three by measurement, and this
   clause does not reopen it.
2. ⛔ **ANOTHER PROSE COMPRESSION PASS IS REFUSED** — ⚠️ **that is the act `W185` exists
   because of: a round's worth of tokens for a round's worth of headroom** (Ruling 149's
   subject).
3. ⛔ **A SHORTER ARCHIVE ANCHOR (`#w148`) IS REFUSED, and the ground is not taste.**
   ⭐ **It saves nothing the stub does not: `[record](BOARD-ARCHIVE.md#w148)` and
   `[`rows/W148.md`](rows/W148.md)` are within a couple of bytes of each other.** ⛔ **It
   recovers NOTHING already spent, because an explicit anchor beside an existing archive
   heading is an edit to a FROZEN byte** (Ruling 106) — ⚠️ **so it could only ever apply
   forward.** ⛔ **And it would need a second anchor form, a second derivation and a second
   collision check beside Ruling 306's.**
4. ⛔ **DECOMPOSING THE REGISTER IS DEFERRED, NOT REFUSED.** ⭐ **It stays available and is
   the answer if this clause's headroom is ever spent** — ⚠️ **it is the largest change and
   the one that does not have to be taken twice, so it is not taken while a smaller one
   holds.**

⭐ **PERFORMED RETROACTIVELY IN THE SAME ROUND, and that was forced rather than tidy: the
board shipped with THREE bytes of headroom, so no wave could be opened without it.** ⛔ **The
sweep created a Ruling 270 stub for every closed row whose file a pre-270 close had DELETED,
each carrying the anchor its own Detail cell already resolved, and then re-pointed every
closed Detail cell at that stub.** ⚠️ **NO ARCHIVE SECTION WAS ORPHANED: the pointer moved
from the board to the stub, it did not disappear** — ⭐ **which is [`W171`](../tasks/BOARD-ARCHIVE.md#w171-an-edit-that-removes-a-documents-last-pointer-to-a-record-section-orphans-it-and-the-pointer-floor-is-tree-shaped-so-it-cannot-see-a-removal)'s
subject, and the reason the sweep is stated here rather than left to be noticed.**

### ⛔ RULING 270 (CTO round 58) — A CLOSE REPLACES THE ROW FILE WITH A REDIRECT STUB, AND DOES NOT DELETE IT

⛔ **THREE RULES WERE JOINTLY UNSATISFIABLE AND THREE CLOSES STOOD BEHIND THE
COLLISION.** ⚠️ **Ruling 201 DEFINES a close as deleting `rows/<ID>.md`; Rulings 106 and
174 forbid editing a frozen record; and frozen records POINT AT row files.** ⭐ **So a
close had to break a pointer that NO OFFICE MAY REPAIR** — and `W100`, `W122` and `W124`
could not reach a `done` state at all, which left every round ending with a register that
was true only because it declined to say `done`.

⭐ **THE RESOLUTION, and it is the POINTER FLOOR that yields rather than the freeze:**
⛔ **no frozen byte is edited, ever, for any reason, including this one.**

⭐ **THE STUB IS EXACTLY THREE THINGS, and a fourth makes it not a stub:**

```markdown
# <ID>

⛔ **This file carries the ARGUMENT for board row `<ID>` and nothing else.**
⭐ **Its argument has CLOSED and moved to the record.**

[the argument](../BOARD-ARCHIVE.md#<the-record-s-own-anchor>)
```

1. ⭐ **the `# <ID>` frame line** — `board-frame` reads it;
2. ⭐ **the frame phrase** (`and nothing else.`) — `board-frame` reads that too;
3. ⭐ **ONE pointer at the ARCHIVE ANCHOR where the argument now lives** — ⛔ **anchored,
   never a bare `BOARD-ARCHIVE.md`**: Ruling 270's own sentence is *"the reader lands on
   the argument"*, and a bare link lands them at the top of a record hundreds of sections
   long (Ruling 244(e)'s property).

⛔ **THE PREDICATE IS *THE ARGUMENT **IS** THE POINTER*, NEVER *CONTAINS ONE*, and that is
measured rather than stylistic.** ⚠️ **MEASURED at `51dee3b`, role `wt/dev1`: of the **83**
live row files, **50** carry an anchored `BOARD-ARCHIVE.md#` pointer somewhere and **42**
END with one.** ⭐ **A `contains` test would therefore have read FIFTY full argument files
as stubs and silenced `board-orphan` on exactly the files it guards.** ⛔ **There is no
byte threshold and there is not going to be one** — Ruling 186's remedy, reused: a closed
predicate retires a disagreement instead of settling it.

⚠️ **A STUB IS STILL JUDGED. The clause is *a CLOSED row's detail file MAY be a stub*, and
never *a file under `rows/` may be anything*:**

| the file | ⛔ the reading |
|---|---|
| a stub whose id has a CLOSED register row | ⭐ **clean** — the one exception |
| a FULL argument file left behind by a close | ⛔ `board-orphan` — the close did not happen |
| a stub whose id has NO register row | ⛔ `board-orphan` — the register lost it |
| a stub whose id has a LIVE register row | ⛔ `board-detail` — ⚠️ **a live argument is
  AMENDED, so it may not live in the archive**, which is what that finding's message has
  said since it was written |
| a stub with no frame phrase | ⛔ `board-frame` **and** `board-orphan` |
| a stub whose archive pointer does not resolve | ⛔ the POINTER FLOOR, one instrument over |

⭐ **WHY THE STUB AND NOT A FLOOR ARM THAT RESOLVES AN ARCHIVE LINK AT A CLOSED ROW.**
⛔ **MEASURED by the PO at `6c4e3d0`, role `wt/po`, four states, every expectation written
down BEFORE the command ran** ([the record](../tasks/handoffs/CTO-2026-09-11-round58.md#6b-ruling-270-w100-is-correctly-blocked-the-po-read-ruling-174-right-the-pointer-floor-yields-and-the-freeze-does-not)):
⚠️ **performing Ruling 201's delete left **3 unresolved pointers, all FROZEN**; the stub
leaves **2 findings from ONE arm of ONE instrument** and **0 unresolved.** ⭐ **The
alternative would have taught the pointer floor to accept a dangling path ON A CONDITION,
and the condition is a STATE CELL in another file.** ⛔ **The stub keeps the floor's
predicate exactly as strict as it is and moves the single exception into the instrument
that already reads the register.**

### ⛔ Ruling 244(e) (CTO round 56) — a row is BORN with an ANCHORED POINTER to its argument

```bash
# ⛔ Run on the row being minted, BEFORE the mint commit lands. `-L` lists the
#    files with NO match, so the pass condition is a silence.
grep -LE '\]\(\.\./(BOARD-ARCHIVE\.md|handoffs/[^)]*)#' ../tasks/rows/<ID>.md
```

⛔ **Pass: the command names no file.** ⚠️ **An UNANCHORED pointer is not a pass:
the address has to resolve to the argument, not to the document that contains
it** — ⭐ **which is the property a pointer has and a restatement does not.**

⭐ **MECHANISED BY RUNNING THE BLOCK ABOVE, never by restating it** (`W306`):
[`born.py`](../../tools/quality/board/born.py) PARSES the pattern out of that fenced
command at run time and branches on it, as an arm of the floor's board check.
⛔ **So an amendment to the command above moves the instrument's verdict in the same
commit** — ⚠️ **which is why no regular expression is typed into the instrument: a
second spelling of a clause is free to disagree with the first, and the copy nobody
re-measures is the one that rots.** ⭐ **A clause the instrument cannot READ is a
FINDING and never a silence, because an empty population is not the pass reading
(Ruling 191).** ⛔ **The rows this clause never bound are excluded BY NAME in the
instrument and PRINTED in its reading** (Ruling 185's form) — ⚠️ **a gate that
reddened the tree over one would BE the retroactive sweep the paragraph below says
this clause is not.**

⭐ **The evidence that the clause costs nothing: the PO did it for all four of
round 44's mints WITHOUT the clause.** ⚠️ **Without it, `W88`'s population grows by
one per mint, and 8 of its 10 new members at round 56 were the minter's own** —
[round 56's record](../tasks/handoffs/CTO-2026-09-10-round56.md#3-ruling-244-a-row-whose-own-predicate-has-rotted-is-amended-never-re-minted-the-dispatch-predicate-is-stated-once-the-rotted-one-is-left-standing-and-dated-and-the-row-is-placed-rather-than-dispatched).

⛔ **This clause binds the MINT and nothing else. It is not a retroactive sweep of
`rows/`, and the backlog is `W88`'s** — ⚠️ **MEASURED at `6c4e3d0`, role `wt/dev1`,
clean worktree, the command above widened to `../tasks/rows/*.md`: **33** of **80**
row files carry no anchored pointer to an argument. ⛔ **Reading it as this clause's
pass condition would make the clause unsatisfiable on the day it landed**, which is
Ruling 185(a)'s defect and Ruling 223's worked example.

### ⛔ Ruling 231(b) (CTO round 54) — a REGISTER must be TRUE WHEN IT MERGES, and the freshness check is an INSTRUMENT IN THE MERGE PATH, never a habit

⭐ **The clause, verbatim as the PO supplied it in round 43 and as
[round 56's record](../tasks/handoffs/CTO-2026-09-10-round56.md#4-ruling-245-a-ruling-no-convention-carries-is-not-a-gap-it-is-a-cliff-rulings-217241-have-reached-no-convention-document-0-of-25-against-a-control-of-17-of-21)
ordered it landed** (Ruling 195 — quoted, never paraphrased):

> ⛔ Before a merge to a release branch the coordinator runs
> `python3 -m tools.quality.board.corroborate` and quotes its reading in the merge
> message's record, beside the verdict. ⚠️ A non-zero exit is a BLOCKING condition
> on the merge, not a note: a register that is wrong when it merges is wrong for
> every agent that opens it next

```bash
python3 -m tools.quality.board.corroborate > /tmp/corr.txt 2>&1
echo "CORR_EXIT=$?"     # ⛔ read on the NEXT line, nothing in between (Ruling 241)
cat /tmp/corr.txt       # ⭐ the READING is what the merge message quotes
```

⛔ **Pass: `CORR_EXIT=0`, reported as `GREEN`/`RED` plus that exit code
([the rule](review-rubric.md#run-every-gate-stop-transcribing-readings-into-prose-a-user-decision)).**
⚠️ **The quoted clause says *quotes its reading*; the record now carries the
verdict word and the code, and the FIGURES only where a row is refuted — which
is a gate's own bound and is the exception.**
⚠️ **Exit `2` is the real third state and is NOT a pass** — see Ruling 216 below.

⚠️ **THE QUOTED CLAUSE SAYS *beside the verdict* AND IT IS LEFT UNEDITED**
(Ruling 195 — a ruling is quoted, never paraphrased). ⛔ **There is no verdict
any more: no reviewing office and no bracket, a USER DECISION**
([`delivery-flow.md`](delivery-flow.md#the-gate-is-self-certification-there-is-no-reviewing-office-a-user-decision)).
⭐ **The GATE is unchanged and the OBLIGATION is unchanged — the coordinator runs
it before the merge and quotes the reading in the merge message's record. Only
the thing it stood beside is gone.**

⛔ **AND THE BOUND ON WHAT THIS GATE CAN PROMISE, adopted into the ruling at round
56 as Ruling 247: a merge-time gate that exits `0` against a FALSE cell gates
nothing.** ⭐ **`corroborate` already holds both numbers and prints them side by
side; turning that into one comparison is `W115`'s, not this clause's.**

⭐ **Ruling 231 does NOT amend Ruling 97 and does not weaken it.** ⛔ **A RECORD is
true at the ref it was taken at, forever; a REGISTER is true NOW or it is wrong** —
⚠️ **and Ruling 97 was never the right instrument for a document every agent opens
as the CURRENT state, which is what a board is FOR.**

#### ⛔ `W302` — the merge path READS BOTH ENVIRONMENTS on the MERGED TREE, and a runner in one office's scratchpad is not a gate

⛔ **Ruling 231(b) above puts the freshness check IN THE MERGE PATH rather than in a habit.
This is the same clause, for the thing the floor cannot answer at all.** ⚠️ **The defect it
closes is measured and it is this register's own: a release tip was certified on a HOST
floor that printed, in its own output, that it carried no lint signal and that the two
gates in `tests/test_repository.py` had SKIPPED rather than passed — and the wave merged.**
⭐ **The sentence was there, in full, both times, and a printed warning is not a gate** —
[`W296`](../tasks/rows/W296.md)'s family exactly.

```bash
python3 -m tools.mergegate <branch> --body <body-file>
# ⛔ exit 0 merged · 1 a gate refused and NOTHING was committed · 2 nothing was read
```

⛔ **It stages with `--no-commit` and reads the MERGED tree, never `HEAD`** — ⚠️ most of
that tip's deviations ARRIVED WITH CARRIERS, so a `HEAD`-side reading would have passed
every one of them. ⭐ **A red reading ends in `git merge --abort`, and the restore is then
VERIFIED BY READING the tree** rather than by the abort's own exit code
([Ruling 287](review-rubric.md#ruling-287-the-container-cannot-restore-and-a-restore-whose-exit-code-is-unread-is-not-a-restore)).

⛔ **THE PAIR IS THE UNIT AND NEITHER ENVIRONMENT MAY BE SWAPPED FOR THE OTHER.** ⭐ The
host cannot answer the `ruff` enforcement
([Ruling 78](review-rubric.md#ruling-78-the-floor-prints-the-lint-state-including-its-absence))
or any in-image assertion; the pinned image cannot reach the sibling and workspace ones,
because it mounts only the checkout. ⚠️ **A gate that swapped one for the other would trade
a blind spot rather than close it**
([Ruling 326](review-rubric.md#ruling-326-a-reading-is-quoted-with-its-environment-or-it-is-not-a-measurement-and-green-names-the-environment-that-produced-it)).
⛔ **What each environment REACHES is a property of the host and not of the branch, so it
is a DISCLOSURE and never gated here**
([Ruling 328](review-rubric.md#ruling-328-a-gates-predicate-ranges-over-state-the-branch-controls-a-property-over-host-state-is-a-disclosure-and-never-a-gate));
the suite already prints it.

⛔ **It is a COMMAND and not a floor check, and that is forced rather than chosen:** a floor
check may not read a branch position
([Ruling 80](review-rubric.md#2e-ruling-80-a-floor-checks-verdict-may-not-depend-on-untracked-state)),
and one that shelled into git and found nothing would return the PASS reading from an empty
population
([Ruling 191](review-rubric.md#ruling-191-cto-round-49-a-control-owes-inhabitation-and-an-empty-population-returns-the-pass-reading-rather-than-no-reading)).
⭐ **WHAT IT IS NOT: a second copy of the lint rules.** `tests/test_repository.py` already
fails the build wherever `ruff` exists; this RUNS that and BRANCHES ON ITS EXIT. ⛔ **And it
reads the tree being merged, NEVER history** — a report over landed tips is a backlog no
office may clear.

### ⛔ Ruling 174 — Ruling 106's freeze attaches when material BECOMES a record, not while it is being moved into one

> ⭐ **Re-addressing a link inside material that is being moved into
> `../tasks/BOARD-ARCHIVE.md`, in the SAME COMMIT that moves it, is part of the
> MOVE.** ⛔ **Once it has landed, it is frozen like every other byte and is
> corrected by annotating beneath.**

⚠️ **This is the narrow ground and it is the only one that holds.** ⛔ **The wider
ground *"a pointer is an address, not a statement"* was OFFERED and REFUSED**,
because it would license editing addresses inside records that are already
frozen — ⭐ **which is the whole of Ruling 106's subject.**

⭐ **What makes a move admissible rather than merely unnoticed is the DISCLOSURE:**
the archive's own banner says which links were re-addressed and why, and
`../../tools/tests/quality/board/test_migration.py` asserts the count — ⛔ **so a
THIRD re-addressed line fails by name instead of passing as *probably the same
two*.**

## ⛔ The instrument — `tools/quality/board/`, and it runs on every floor

| Rule | Fires when | Why it is that and not a line count |
|---|---|---|
| `board-detail` | a live register row has no `rows/<ID>.md` — ⭐ **or has one that is a Ruling 270 REDIRECT STUB**, ⛔ **or an In-flight `W` subject has no `rows/<ID>.md`** (`W161`; an epic task owes none — see the subject vocabulary below) | an argument with no home is an argument that goes back into the cell; ⛔ **and a LIVE row's argument is AMENDED, so it may not live in the archive either** |
| `board-orphan` | a `rows/<ID>.md` has no live register row — ⭐ **UNLESS its id has a CLOSED register row AND the file is a Ruling 270 REDIRECT STUB** | a file nobody is sent to; ⭐ **the bijection is asserted in BOTH directions, because one of the two always survives a careless edit.** ⛔ **The one exception is Ruling 270's, above: a close REPLACES the row file rather than deleting it, because frozen records point at row files and no office may repair a frozen pointer** |
| `board-duplicate` | one id has two register rows | ⚠️ **the board once carried `W20` twice, as `todo` AND `done`, two rows apart** |
| `board-narrative` | non-table bytes exceed `BOARD_NARRATIVE_CEILING` | ⭐ **invariant to the number of rows** — a new row is a table line and adds nothing to it |
| `board-row-width` | one table row exceeds `BOARD_ROW_CEILING` | a cell that wide is an argument, and an argument goes behind a pointer |
| `board-size` | the whole file exceeds `BOARD_FRAME + BOARD_PER_ROW ×` register rows `+ BOARD_PER_OBSERVATION_ROW ×` delimited observation rows `+ BOARD_PER_SCHEDULED_ROW ×` delimited scheduled rows | ⭐ **the bound with no gap** — see below. ⛔ **`W130` added the last two terms: Ruling 271 measured the allowance indexed to a population that could not see its own numerator, and the SLOPE was the defect rather than the size** |
| `board-state` | a register row's state cell DECLARES no state | ⛔ **the hole that let a LIVE row leave the register in silence** — see below |
| `board-frame` | a row file does not begin `# <ID>` **or** does not contain the frame's phrase | ⭐ **the one live-tree property left after Ruling 180.** ⛔ **TWO SUBSTRINGS and nothing more** — it cannot read what the file *says*, and that weakness is what lets it survive every amendment (`CTO-47/4`) |
| `board-inflight` | one observation row declares a started state, names **no** checkout and counts **0** commits | ⛔ **Ruling 189(b), and it is a CONTRADICTION PRINTED ON ONE ROW** — ⚠️ the founding bytes stood for 350 commits while every git instrument read correctly |
| `board-unobserved` | a register cell declares a started state and **no** observation row names it | ⭐ **an asserted state owes an observer** — ⛔ the board is the only instrument that ASSERTS in-flight rather than OBSERVING it, so this is the only direction it can be stale in |
| `board-disagreement` | one table says the row is **started** and the other says it is **finished** | ⛔ **both cannot be true of one row**, and a state has ONE home; ⚠️ `todo` against started is NOT this — see the narrowing below |
| `board-unreadable` | a `<!-- inflight -->` block is DECLARED and **no table inside it declares the observation columns** | ⛔ **Ruling 196(b)'s expiry, discharged by `W111`** — ⚠️ the CTO's own plant renamed two column NAMES and read `NONE FOUND, 0 rows` on a GREEN floor, so the instrument announced where it should have refused. ⭐ **The delimiter makes the refusal POSSIBLE; this rule is what makes it HAPPEN** |
| `board-trigger` | a `## Scheduled` row's state cell DECLARES no state | ⛔ **`board-state`'s rule ONE TABLE OVER, and the shipped message gives the ground in its own words: *"a `Trigger` cell IS an asserted state wearing another column name (Ruling 189's family), and a scheduled item whose state no instrument can read is one that cannot report that it is owed OR that it was met"*** — ⚠️ MEASURED in that message: one such cell read `before M1's wave opens` through the close of M1 and all four steps of M2 while the work behind it was being done. ⭐ **`expired` is in the set precisely so a trigger whose event has passed can SAY so** |

⛔ **THIS TABLE IS A CLOSED CLAIM AND IT WAS INCOMPLETE FOR THREE ROUNDS** — ⭐ **Ruling
276 (CTO round 58), and Ruling 258 is the clause it failed: a declared-gaps list is a
closed claim, so an incomplete one is worse than none.** ⚠️ **MEASURED at `ad5ce24`, both
populations printed in full and the gap in ONE direction only: `tools/quality/board/`
defines **13** `RULE_*` constants and this table listed **12**; the one missing was
`board-trigger`.** ⛔ **It was routed to the CTO in three consecutive rounds and landed in
none of them, which is Ruling 245's cliff with a name on it** — ⭐ **so the fourth routing
was refused and the row was written instead.**

### ⛔ Ruling 189(b) is THREE rules, and the population is located by a DELIMITER

⭐ **`tools/quality/board/observation.py`** carries all three, and ⛔ **it reads no
`git` at all** — which is what lets `W100` reuse the half it needs without
inheriting a git dependency (ruled round 49, below).

- ⛔ **The observation table is DELIMITED**, `<!-- inflight -->` /
  `<!-- /inflight -->`, the `<!-- register -->` pattern reused. ⭐ **The locator
  that answered is NAMED in the line `board_state` prints**, so a board with no
  markers says so on every run instead of being assumed. ⛔ **An ordinary
  five-cell table is not an observation table**, which is the whole difference
  between a declared boundary and the inferred one that made
  `board-duplicate` fire on its own author.
- ⛔ **RULING 196(b) HAS EXPIRED AND `W111` DISCHARGED IT.** ⭐ **The header locator
  survives for a board carrying NO marker at all** — R10's arbitrary roots, and the
  form [`W111`'s record](../tasks/BOARD-ARCHIVE.md#w111-ruling-196s-expiry-the-header-locator-announces-where-a-delimiter-can-refuse-and-the-delimiters-have-landed)
  asked to be preferred — ⛔ **but a board that DECLARES a block
  is read ONLY inside its markers, and a declared block whose header declares no
  role is `board-unreadable` rather than a `NONE FOUND` notice.** ⚠️ **The refusal
  fires on a header that declares NO role and never on one that declares them
  differently**, because Ruling 189(b)'s roles are read FROM the header precisely so
  the PO may rename, reorder, emphasise or prefix a column. ⭐ **And `corroborate`
  exits `2` for the same two populations, which is where `PO-40/4` lands: the command
  used to print Ruling 191(a)'s own sentence and return the PASS code beside it.**
- ⭐ **The roles are read FROM the header, never from a column position** — ⛔ so
  renaming, reordering, emphasising or prefixing a column cannot blind the
  recogniser, which is Ruling 192's question asked of this rule.
- ⛔ **`W73` is a STAND-IN, excluded BY NAME** (`CTO-49/4`): its carrier lives in a
  repository this one does not own, so observing it would cross the seam (R20,
  Ruling 151). ⭐ **Ruling 185's form — the POPULATION is narrowed in the
  instrument and the name is printed; the PREDICATE is never widened.**
- ⚠️ **THE NARROWING, and it came from the rule firing on correct work.** ⛔ **The
  first `board-disagreement` flagged any started-against-not-started pairing, and
  its first live reading hit a row the PO had just dispatched** — because this
  board dispatches a row by naming it in the observation table and leaving its
  register cell at `` `todo` ``. ⭐ **So a finding is STARTED against a TERMINAL
  state** (`done`, `accepted`, `routed`), and the `todo` pairing is **PRINTED
  rather than flagged** (Ruling 179, Ruling 183's form). ⛔ **A notice whose first
  wave fires on work its author just did is a notice nobody reads twice.**

### ⛔ `W161` — the In-flight table's SUBJECT VOCABULARY, and where each subject is argued

⭐ **The observation table admits more than a `W` row, and this is the closed list of what a
subject may be and where its argument lives:**

| the subject | its form | ⛔ where its argument lives | what the bijection does |
|---|---|---|---|
| a **board row** | `W<digits>` | `rows/<ID>.md` | ⛔ **no row file is `board-detail`**, in the register AND in this table |
| an **EPIC TASK** | `<PREFIX>-<digits>`, optional letter (`NS-03`, `SF-19b`) | ⭐ **its EPIC**, `docs/tasks/E<nn>-*.md`, ⛔ **which DEFINES it and argues it there** | ⭐ **owes NO row file**; a `rows/<ID>.md` for it is `board-orphan` — a second home. ⛔ **One no epic defines is `board-detail`** (`W262`): what defines a task is decided in [`vocabulary.py`](../../tools/quality/board/vocabulary.py), not here |
| anything else (`INT-09/5`) | neither form | ⚠️ **undeclared** | ⭐ **read and PRINTED by name, never refused** |

⛔ **Two things this is NOT.** ⚠️ **Not a rule that every observation row owns a `rows/` file**
— that gives a task's argument two homes, the defect `rows/` exists to prevent. ⛔ **And not a
narrowing of the parser**: refusing a non-`W` subject re-opens `NS-01/2` as a build failure.
⭐ **The `bijection` line of the `board:` notice names the population `board-detail` and
`board-orphan` were over — `W` ids only — beside the epic tasks outside it and the residue**,
so a clean run over a `W`-only population is not read as a claim about every row (Ruling 48's
shape, Ruling 331's arriving form). Enforced in `../../tools/quality/board/bijection.py`.

### ⛔ May the floor shell out for clause (c)? NO, and the instrument is separate

⭐ **[`W96`'s record](../tasks/BOARD-ARCHIVE.md#w96-a-cell-declaring-a-started-state-asserts-a-live-checkout-or-a-branch-ahead-of-release)
owed this answer before it owed code, and the answer is a SPLIT:** ⛔ **clause (b) runs on every floor and clause (c) runs at a wave's
close**, as `python3 -m tools.quality.board.corroborate`, which
`tools.quality.CHECKS` does not import.

| Why the floor may not | Which rule |
|---|---|
| a floor check's verdict may not depend on untracked state, and a branch position is the purest untracked state there is | Ruling 80 |
| the floor runs over **arbitrary roots** — a temp tree, a corpus repository — where no release branch exists at all | R10 |
| ⛔ **the decisive one**: a git check that found nothing would return **the PASS reading from an empty population** | Ruling 191 |

⭐ **So `corroborate` has THREE answers, not two** — `0` corroborated, `1`
refuted, ⛔ **`2` NOT AUTHORITATIVE** (Ruling 53's fourth state), because *"git
could not answer"* and *"nothing is wrong"* must never arrive as the same
verdict.

⛔ **THE PRODUCERS OF EXIT `2` ARE **SIX**, AND THIS LIST IS A CLOSED CLAIM**
(`W115/2`, routed by round 59; Ruling 276's form — a declared-gaps list is read as
EXHAUSTIVE, so an incomplete one is worse than none). ⚠️ **It read *"`W111` added the THIRD
producer"* for two waves while `W115` was adding the fifth and sixth, which is the same
defect as this document's rule table and is why the claim now carries its count:**

| # | the producer | its row | the reading that inhabits it |
|---|---|---|---|
| 1 | no `docs/tasks/BOARD.md` in this checkout | — | `test_impossible_a_checkout_with_no_board_is_NOT_AUTHORITATIVE` |
| 2 | the release branch does not resolve | — | `test_impossible_a_release_branch_that_cannot_exist_is_NOT_AUTHORITATIVE` |
| 3 | a DECLARED `<!-- inflight -->` block whose header declares no role | `W111`, `PO-40/4` | `test_planted_an_UNREADABLE_DECLARED_TABLE_IS_EXIT_2_AND_NOT_A_PASS` |
| 4 | a board carrying NO marker at all, located by Ruling 196(b)'s RAMP | `W111` | `test_planted_a_board_with_NO_MARKER_is_exit_2_and_names_the_RAMP` |
| 5 | ⭐ **one ROW whose branch git could not count** — `Answer.NOT_ANSWERABLE`, folded | `W115`, Ruling 216 | `test_planted_a_ROW_whose_branch_GIT_CANNOT_COUNT_exits_2_AND_NOT_1` |
| 6 | ⭐ **one LIVE CHECKOUT whose `ahead` git could not count** | `W115`, Ruling 216 | `test_planted_a_LIVE_CHECKOUT_git_cannot_count_is_NOT_filed_under_BY_CONSTRUCTION` |

⚠️ **Five RETURN SITES carry those six, because 5 and 6 share one fold** — ⛔ **and that
fold is the point of Ruling 216: `NOT_ANSWERABLE` DOMINATES, so one unanswerable row makes
the RUN exit `2` and never `0` or `1`.**

⛔ **A DECLARED, READABLE, EMPTY block is exit `0` and says so in its own
sentence: that is *nothing is in flight*, which is a real answer, and a refusal there would
fire on every wave the PO closed correctly.**

⭐ **AND THE THREE POPULATIONS THAT FOLD INTO THAT EXIT CODE ARE EACH NAMED, INCLUDING WHEN
EMPTY** (`PO-46/14`): `rows REFUTED by git (N): …` / `rows refuted by git: none.`,
`rows NOT ANSWERABLE (N): …` / `rows git could not answer about: none.`, and
`git COULD NOT COUNT … for N live checkout(s)` / `live checkouts git could not count: none.`
⛔ **THE DEFECT THIS CLOSES IS RULING 264(a)'s OWN SUBJECT, and the office that caused it
disclosed it:** ⚠️ **a round-45 brief demanded *"the refuted list printed even when empty"*
and THAT OUTPUT DID NOT EXIST — `REFUTED ROWS` is quoted in
[`BOARD-ARCHIVE.md`](../tasks/BOARD-ARCHIVE.md) and in
[`PO-2026-09-11-round45.md`](../tasks/handoffs/PO-2026-09-11-round45.md) and appears nowhere
in `tools/`, `src/` or `tests/`.** ⛔ **A fabricated REQUIREMENT induced a fabricated
MEASUREMENT, and a review reproduced every figure around the line without catching the line.**
⭐ **The two ROW verdicts were COUNTERS with no population at all, while five branch-side
readings each named theirs and said `none.` when empty** — ⚠️ **so the asymmetry was never
four-versus-one: it was that the populations whose counts ARE the exit code were the ones
with no list.** ⛔ **A DECLARED, READ, EMPTY table prints NEITHER row line, because two
`none.`s about a population with no members to have is the `0 = 0` the idiom refuses.**

⚠️ **And it prints the readings NO BOARD CELL CARRIES, which are
`tools/quality/board/unclaimed.py`'s** (`W132`'s split) — ⭐ **each of which reads as
dispatched work to a human, which is Ruling 189's subject with nowhere to print it.**
⛔ **THE LIST IS A POINTER AND CARRIES NO COUNT, and that is a repair rather than a style:**
⚠️ **the sentence that stood here said SIX and enumerated five, having never been updated
when `W170` added the `SPENT`-namespace exemption line** — ⭐ **so read the table in that
module's own `unnamed()` docstring, which resolves at read time and cannot be one short.**
⛔ **One of them is Ruling 264(c)'s GATE, and its population is LIVE CHECKOUTS: a branch no
worktree holds is read on the line BELOW it, never on it.**

#### ⛔ `W153` — a CARRIER is DECLARED on its own branch, so the gate can read a dispatch the register has not recorded

⚠️ **The gate took its names from the In flight table alone, and only a register round writes
that table.** So a wave with no register round (`PO-50/7`) was blind by construction, and a
carrier at `0` ahead landed on Ruling 130's line instead (PO round 52). ⭐ **Measured at
`5f772d9`, role `wt/dev3`, HOST, before any edit: of 3 carriers dispatched since the last
round, 1 was on the gate and 2 were on the `BY CONSTRUCTION` line.**

⛔ **THE CONTRACT: the office that cuts a carrier declares its rows in the same invocation.**

```sh
git switch -c fix/W153-slug <ref> && git config branch.fix/W153-slug.description W153
```

⚠️ **This is shared config on purpose**: the key belongs to that branch alone, and it is never
`user.*`. `git branch -D` deletes the key along with the branch.

| the declaration | what `corroborate` does |
|---|---|
| on a branch an In flight row claims | ⭐ **never read**: the row answers, and the count is printed |
| every id names an OPEN register row the table carries nowhere | accepted: it counts as claimed, exactly like a row's branch |
| no id, an unknown id, a closed row, or an id the table carries elsewhere | ⛔ **REFUSED with its reason, and the branch stays gated** |
| `git config` did not read | ⛔ nothing is taken off, and the line says so |

⛔ **The exit code does not move, and with no description every line reads as before.**

| candidate home | ⛔ why not |
|---|---|
| the In flight table | unwritable in a wave with no register round: the defect itself |
| a tracked file | needs a commit, so unreadable at `0` ahead, and collides with `docs/tasks/` writers |
| the branch name | carries no row id: `fix/INT06-9-highlight-languages` carried `W243` |
| ⭐ **the branch description** | **TAKEN**: needs no commit, every worktree reads it, and it is deleted with its branch |

⛔ **NOT A THIRD COPY.** A description is read only where no row claims the branch, and an id
the table carries elsewhere is refused, so wherever the table speaks it is the only home. The
register never edits a description. ⛔ **`inflight.py` may never read one** (`W125`, Ruling
231(c)): a table generated from a declaration would assert git against itself.

#### ⛔ RULING 265 (CTO round 58) — the `UNNAMED` arm exempts the OFFICE-BRANCH PATTERN, not `0` ahead

⚠️ **A checkout with NO commit is invisible to every git instrument BY CONSTRUCTION
(Ruling 130), so those are COUNTED AND NAMED as unreadable rather than judged.** ⛔ **But
that exemption was gated on `0` commits ahead, and an office's own round branch stops
satisfying it THE MOMENT IT RECORDS ANYTHING** — ⭐ **so `dispatched and UNNAMED by any
row` named a `chore/po-round*` or `chore/cto-round*` branch in every wave, forever, and
Ruling 264(c) had just made that printed line the project's ONE pre-merge gate.** ⚠️ **A
reviewer was therefore taught to skim a gate, checking only whether a DEVELOPER name
appeared in it.**

⭐ **MEASURED, one branch and two readings, the only variable being whether the office had
written anything down yet:** `chore/po-round45` exempt at `6c4e3d0` at `0` ahead;
`chore/po-round44` named as *dispatched and UNNAMED* at `b5b0577` after it committed.

⛔ **THE PREDICATE IS THE BRANCH NAMESPACE AND NOT EMPTINESS: no register row will EVER
name an office's round branch, because a row naming it would be a row naming its own
recorder.** ⭐ **That is decidable from the NAME, the prefix is ANCHORED — `startswith`,
never `in`, or `fix/W99-po-round-guard` would be exempt — and the exemption is PRINTED with
its count and its reason**, because a gate that hides a rule is unreadable.

⚠️ **`W136` replaced the prefix with the WHOLE name, because the anchored prefix exempted
topic branches such as `chore/cto-round34-rubric`:** ⭐ the spelling is
[the office round-branch convention](delivery-flow.md#office-round-branches).

⚠️ **The DETACHED checkout is still in NONE of those lines, and that is NOT absorbed here:**
⛔ **`wt/po-int` has no `branch refs/heads/…` line for `worktree list --porcelain` to
report, so the instrument never sees it.** ⭐ **That hole is `PO-44/5`'s and `W125`'s with
`W96/5`, and the office line carries its OWN count precisely so that Ruling 265's exemption
shrinks no other line's number without saying where the branches went.**

⛔ **The Ruling 140 plant found a hole in this instrument BEFORE it shipped, and
the third rule is the fix rather than a tweak to the first two.** ⚠️ **Run
against `board-narrative` and `board-row-width` alone: 320 lines of round 33's
narrative, pasted one line per table row, moved the narrative reading by ZERO
and tripped the width rule exactly ONCE.** ⭐ **`board-size` catches it because
text that indexes nothing raises the numerator and leaves the denominator
alone.** ⛔ **The other two are kept as DIAGNOSIS: `board-size` says the board is
too big, and they say WHERE — a governor that only says *too big* is one
somebody raises rather than obeys.**

### ⛔ RULING 271 (CTO round 58) — `board-size`'s DENOMINATOR counts THREE populations, and the SLOPE was the defect

⚠️ **MEASURED by the PO at `6c4e3d0`, role `wt/po`: the board stood at `42707 of 42784`
— **77** bytes of headroom, **99.82 %** consumed — and round 45's own obligations summed
to MORE than the `4 × 224 = 896` its four mints earned, before one byte of narrative.**
⛔ **The register's own round could not be recorded inside the bound that governs the
register, and that is not a *may*: it BOUND the round.**

⛔ **THE DEFECT IS NOT SIZE. What grew was `## In flight` (+1 880 B) and `## Scheduled`,
and NEITHER IS A REGISTER ROW** — ⚠️ **so the allowance was indexed to a population that
cannot see its own numerator.** ⭐ **Both of those tables are DELIMITED and
`tools/quality/board/` already parses both, so the remedy is a DENOMINATOR TERM PER TABLE:**

```text
allowed = BOARD_FRAME
        + BOARD_PER_ROW             × ids the register names
        + BOARD_PER_OBSERVATION_ROW × rows inside <!-- inflight -->
        + BOARD_PER_SCHEDULED_ROW   × rows inside <!-- scheduled -->
```

⛔ **THREE REMEDIES ARE REFUSED, each on a measured ground, so nobody reaches for one:**

| the move | ⛔ why the reading kills it |
|---|---|
| raise `BOARD_PER_ROW` | it rewards MINTING, and minting was never the cause — ⚠️ **a LIVE
  register line means **169.8 B** against an allowance of 224 at `51dee3b`, so each mint
  already EARNS +54** |
| archive CLOSED register lines | ⛔ **the slope is ZERO** — a closed line means **229.6 B**
  against `BOARD_PER_ROW = 224`, so archiving one frees **5.6 B** |
| raise `BOARD_NARRATIVE_CEILING` | ⚠️ **the SAME defect one bound over**: the narrative is
  not what grew, and a ceiling raised to absorb a table's growth stops measuring prose |

⭐ **THE FIGURES ARE DERIVED AND THE RULE IS ONE RULE** (Ruling 277 — a number is binding
wherever it is written, so it is written once, in `tools/quality/board/bounds.py`):
⛔ **a per-row term is its population's MEASURED MEAN LINE, rounded UP to the next multiple
of 32, plus one further 32.** ⚠️ **Its property is a STATED, UNIFORM slope — a row earns
between 32 and 64 bytes more than the mean row of its own population costs — and the rule
RE-DERIVES `BOARD_PER_ROW = 224`, the constant that has shipped since the split, from
today's register and from the `~170 B` measured at the split itself.** ⭐ **That is what
makes it a derivation rather than a figure chosen to clear today's board.**

⛔ **AND THE RULING 140 EVASION STILL FAILS, which had to be re-asserted because a wider
denominator is exactly where it would have got back in.** ⭐ **A data row counts only when
its table's own parser reads it, and both parsers require a row to carry at least as many
cells as their DECLARED HEADER has roles** — ⚠️ **so 400 lines of prose pasted one line per
table row INSIDE both delimited blocks raise NEITHER denominator.** ⛔ **And only DELIMITED
rows count: `observation.read` still answers for a board with no marker through Ruling
196(b)'s header RAMP, and an INFERRED population in a denominator would be the evasion with
a header on it.**

#### ⛔ Ruling 294 (CTO round 60) — a per-row BOUND states its TERM's DERIVATION beside its verdict, and *a row earns more than it costs* is a claim about the MEAN

⛔ **The section above derives three terms; this is the rule that keeps them derived.** ⭐ **A
bound of the form `frame + per-row × rows` carries two numbers somebody CHOSE, and a chosen
number in a denominator is the thing a later round raises rather than obeys.** ⛔ **So the term
is DERIVED by a stated rule, the rule is RE-TAKEN by a test on every run, and the bound PRINTS
the derivation beside its verdict.**

⚠️ **MEASURED, CTO round 60, printed by the instrument itself:**

```text
14336 frame + 224×131 register + 160×2 observation + 480×8 scheduled = 47840
rule: the population's measured MEAN line, ceiled to the next multiple of 32, plus 32
  224 <- four independent means taken by three offices: 191.4, 169.8, 166.8, 173.4
  160 <- 97.5        480 <- 418.4
```

⭐ **A figure four independent means agree on is DERIVED; a figure one mean produces is
CHOSEN.**

⛔ **AND THE SECOND CLAUSE, which is the honest one: the invariant *a row raises the allowance
by more than it costs* holds for the MEAN row and NOT for every row, and the bound SAYS SO in
its own text.** ⚠️ **A row may legally be 600 bytes (`BOARD_ROW_CEILING`) and earns 224, so
the WIDEST LEGAL row costs more than it earns and the invariant is false of it.** ⛔ **How
close the live board actually runs to that ceiling is a READING and is NOT TYPED HERE** —
⭐ **this document types no measurement of the board (Ruling 181, and the preamble at the top
of this file); the instrument prints it every run as `widest row N of 600`, and round 60's
own dated reading is in
[its record](../tasks/handoffs/CTO-2026-09-11-round60.md).** ⛔ **A ceiling-based term
(640) is REFUSED — raising the allowance to cover the worst case is the *raise it rather than
obey it* move these bounds exist to prevent.** ⭐ **TWO terms and not one, also by measurement:
418 B for a scheduled row against 98 B for an observation row means a single constant gifts the
smaller population 4.8x.**

### ⛔ A state cell DECLARES its state — it does not mention one

⛔ **`board-state` exists because the first `is_closed` was a SUBSTRING TEST.**
⚠️ **A live row reading `` `todo` — after `W44` is done `` was therefore
CLOSED**: it owed no detail file, left the bijection, and the floor printed
`quality floor: clean` with no finding at all. ⭐ **28 of the 78 cells carry the
`✅ done — <ref>` idiom today**, so this was one subordinate clause from routine
rather than exotic.

⭐ **A state cell now begins with a word from a CLOSED set** — `todo`,
`in flight`, `in-progress`, `in-review`, `accepted`, `blocked`, `routed`,
`done` — ⛔ **and a cell that begins with anything else is a finding, not a
guess.** ⚠️ The match ends on a word boundary, so `DONE-ish` declares nothing;
that reading came from the impossible plant, not from argument.

⭐ **This is the project's standard remedy applied to a status: make the illegal
value unrepresentable rather than enumerate it.** ⛔ **Two live cells failed on
the day it landed — `W5` and `W16` — and both were rows a reader would have
sworn were fine.**

### ⛔ A migration that decomposes this board is validated over CONTENT

⚠️ **The split's first validation was a LINE PARTITION and it PASSED while text
was lost.** ⛔ **A line partition cannot see a line that was split into pieces
where only some of the pieces were kept** — here, 78 register lines counted as
consumed while only two of their five cells were written anywhere, losing the
**Owner** and **Status** columns, **28,262 bytes**.

⭐ **Ruling 177.** `tools/tests/quality/board/test_migration.py` asserts the
content claim instead, and it is four equalities rather than a sum:

| It asserts | Which catches |
|---|---|
| every line of the source board is verbatim in a destination | a whole line going nowhere |
| every consumed register line is in the RECORD | a column going nowhere |
| every block of a row file is a WHOLE CELL of its own row | ⛔ **a fragment, and text from the wrong cell** |
| no row file carries the status column | a live copy of a state |

⚠️ **The third replaced a PROXY.** ⛔ Its first version asked *does the block
start mid-sentence?* and flagged two correct cells — ⭐ **a reading from a proxy
is not a property of the thing**, and an equality against the source's own cells
is both cheaper and exact.

⛔ **Ruling 149 retired a line-count governor on `review-rubric.md` because it
alarmed seven times while the property improved seven times.** ⭐ **No bound here
can do that, and it is measured rather than argued: twenty new register rows
raise the allowance from 31,584 to 36,064 while costing 2,220 bytes** — ⛔ **a
longer backlog moves the board FURTHER from the bound, never closer.**
⚠️ **`board_state` prints the whole population on every run — rows, live rows,
detail files, all three readings and all three limits — before anything is
reduced to a verdict** (Ruling 128).

### ⛔ What the `board:` line covers, and the two things it prints with NO bound

⭐ **`rows/`, with its BYTES as well as its count — Ruling 183.** ⛔ **A bound on
a row file would forbid the thing the file exists for**: appending to a live
row's argument is the action the table above prescribes, and nothing can tell
*"the PO re-scoped a row"* from *"the PO pasted a fragment"*. ⚠️ **That argument
retires the GATE and does not retire the MEASUREMENT** — and the reading that
decided it is `rows/` inflated **112×** with the `board:` line byte-identical
and the floor clean, because the line printed a COUNT. ⛔ **A bound REMOVED
because its subject became editable is replaced by a NOTICE, never by nothing.**

⭐ **The FILES whose argument IS their naming — Ruling 186.** ⛔ **`board-frame` is
the right instrument asked the wrong question**: a row file can carry its frame
and argue nothing, and some carry **as their entire argument a normalised copy of
their own register naming cell** — ⚠️ **which is the one thing the frame sentence
inside them forbids:** *"not here, and not in two places."* ⛔ **`startswith` and
`in` cannot read a contradiction**, so `board-frame` passes them and is right to:
widening it to judge whether an argument is PRESENT rebuilds exactly the gate
Ruling 180 removed, because nothing can tell a thin argument from one the PO has
not finished writing.

⛔ **It is a CLOSED PREDICATE — equality against that row's own naming, after
normalising markup, emoji, spacing and a trailing stop — and there is NO byte
measure and NO cutoff.** ⚠️ **Two sweeps read 16 and 19 *thin* rows under two
unruled thresholds; both answered a question that should not have been asked**, so
⭐ **the disagreement is retired rather than settled.** ⛔ **A cutoff appearing in
`board_state` is the signal that a gate has been rebuilt.**

⭐ **And the span is the ARGUMENT, never the FILE** (Ruling 186's clause (c)):
frame overhead runs to a few hundred bytes and varies by more than a hundred
between files, so anything read at file level is the right question over the
wrong span. ⛔ **The frame is located by its own TEXT** — one row file carries an
extra frame block, and an index would have skipped that row's whole argument.

⛔ **An argument that EXTENDS its naming is not this, and is not reported.**
⭐ **Restating what the row is and then arguing it is exactly what the file exists
for** — ⚠️ **equality, never a prefix**, because a notice that flags correct work
is one people learn to scroll past.

⭐ **And the second clause, over the frame's OTHER prohibition: an argument that
DUPLICATES A STATE.** ⛔ **The predicate is the opening IDIOM — an emphasised
label, set off by a dash, that declares a state — and NOT a state word anywhere
past the frame.** ⚠️ **A row argument is *about* states constantly**: *"gated on
`W63` landing"*, *"accepted at round 22"*, *"already DONE by …"*. ⛔ **A
vocabulary search fires on every one of those, and it inherits `is_closed`'s own
founding defect one layer up** — which is why clause one is safe and this one had
to be narrowed: ⭐ **clause one is an EQUALITY against the register cell.**

⚠️ **And the over-match SCALES WITH THE POPULATION, which is the reading that
settled it:** a *state word anywhere* predicate read **3** hits over 50 row files
and **6** over 64 — four of the six being rows their author had just written —
while the idiom predicate read **2** and then **0**, correctly, because both true
hits had closed. ⛔ **A notice whose first wave fires on four rows its author just
wrote is a notice nobody reads twice** (Ruling 179).

⚠️ **This clause is asserted against a PLANTED fixture and a corpus quoted at its
ref, never against the live tree** — ⛔ **a live population of `0` is born vacuous
and a pass with no planted hit is not green** (Ruling 48).

⛔ **No figure from any of these readings is typed into this document**
(Ruling 181): `board_state` prints them every run, and a number copied here is a
number that goes stale in the copy nobody re-measures.

⭐ **What it deliberately does not bound: `BOARD-ARCHIVE.md`.** ⛔ **A record is
supposed to grow monotonically, and capping it would push the reasoning back
onto the board** — which is the defect rather than the remedy.

---

## ⛔ The wave checks — moved WHOLE from `BOARD.md`, 2026-09-10

⭐ **A process is not a state.** ⛔ **This section is the board's own operating
procedure and it was living inside the thing it operates on** — moved here
unedited, and reversible by the PO in one commit if they want it back.

## The wave checks — ⛔ **SIX at open, and check 4 AGAIN at close**

⛔ **All six are mine.** ⭐ **Check 6 was added round 19 by `F23`'s ruling.** ⭐ **RULED 2026-09-10: check 4 runs twice — at wave-open
AND at wave-close** — ⚠️ **and the second run is the one that matters, because
the trigger check 4 exists to catch is *a task ending*, not a wave starting.**

### ⛔ RULED ROUND 47 — check 3 takes the WHOLE TREE, and admits the PLURAL (Ruling 184)

⭐ **Check 3 asks *did every ruling reach an artifact* — C6's own check.** ⛔ **Two
clauses, one instrument, and they pull the same way on purpose.**

> ⭐ **(a) Scope.** A ruling's artifact is wherever the rule is ENFORCED, and this
> project enforces rules in Python as often as in prose. ⛔ **The population is
> `-- docs src tools tests`, not `-- docs`.**
>
> ⭐ **(b) Spelling.** The pattern admits the plural form, because ⛔ **a ruling
> that instructs a JOINT carry must not be invisible to the check that verifies
> carries.**
>
> ⭐ **(c) CASE — added CTO round 49, against this office's own instrument.**
> ⛔ **The pattern is CASE-INSENSITIVE (`-iP`), because this project's house style
> sets a ruling's own heading in CAPS for emphasis and the carry is therefore
> spelled `RULING N` exactly where it is most deliberate.** ⚠️ **Measured at
> `c18df98c`, re-reading round 48's six mints: the case-sensitive form returned a
> FALSE EMPTY on TWO of them, and both witnesses are real artifacts** —
> `docs/tasks/E04-narration.md` for Ruling 187 and `docs/tasks/rows/W94.md` for
> Ruling 188. ⭐ **`-iP` finds both; a ruling that cannot exist still reads empty,
> so the widening is not a wildcard.**
>
> ⭐ **And the reason all three clauses go the same way:** this check's failure mode
> is a **FALSE EMPTY** — *"nobody carried it"* returned for something that was
> carried. ⛔ **So it is tuned to OVER-match, and that is safe for one specific
> reason: check 3 prints FILES, not a count.** ⚠️ **A false positive costs one
> `git show`; a false empty costs a lost ruling** — ⛔ **and clause (c) is that cost
> paid twice inside the round whose mints the check was verifying.**

⛔ **The instrument, and it is PCRE (`-P`), not ERE** — `(?:`, `\s` and `\b` are
not POSIX ERE and `git grep -E` refuses the pattern outright with *"Invalid
preceding regular expression"*:

```bash
# For each ruling minted since check 3 last ran. ⛔ FILES, never a count.
# ⛔ -i is LOAD-BEARING (clause (c)): `RULING 187` is how a carried ruling's own
#    heading is spelled, and the case-sensitive form missed two of six mints.
for n in <the rulings>; do
  echo "Ruling $n:"
  git grep -liP "Rulings?\s+(?:$n|[0-9]+[^.]*\b$n)\b" -- docs src tools tests | sort
done
# Row 3, and it must DIFFER: a ruling that cannot exist reads EMPTY.
# ⛔ The probe number must be MENTIONED NOWHERE, and a number a record has quoted
#    has STOPPED BEING IMPOSSIBLE — `9999` now matches two records that quote this
#    very line. ⭐ Measured at 5e608bf: 9999 -> 2 records; 7431 -> empty. It is the
#    use-versus-mention cost the marker counter already pays, and the remedy is a
#    fresh number per run, never a wider pattern.
git grep -liP "Rulings?\s+(?:<a number mentioned nowhere>)\b" -- docs src tools tests
```

⭐ **Measured at `96e8c95`, `dev2` worktree, host git 2.47.3 and the pinned image
in agreement — and each clause earns its keep on a real reading:**

```text
(a)  Ruling 175, `-- docs`             -> four handoffs, 0 non-handoff files
     Ruling 175, `-- docs src tools tests` -> + tools/knowledge/index.py
                                              + tools/tests/knowledge/test_index.py
(b)  Ruling 76 in docs/conventions/agent-protocol.md
       `Ruling 76\b`                   -> ⛔ NOTHING. A FALSE EMPTY, in an
                                          ARTIFACT rather than a handoff
       plural-admitting                -> line 42, "defeats Rulings 70, 76, 83
                                          and 123 at once"
     ⚠️ and the over-match it costs, in the same file: line 450's "76 finding
        lines across 12 documents" — ⭐ one `git show` to dismiss, which is the
        price clause (b) was ruled to be worth
```

⛔ **The rule this does NOT license: teaching the tree to please the
instrument.** ⚠️ **`PO-36/9` found the same gap from the other side and fixed the
DOCUMENT so the standing check would read it** — ⭐ **that was right at the time,
and it is the instrument's turn now.**

#### ⛔ RULED ROUND 51 — Ruling 200: a ruling's PRIMARY artifact NAMES ITS OWN NUMBER, and the minting reviewer runs check 3 against it

⛔ **A ruling whose own home document never spells its number is INVISIBLE to the
check that asks whether a ruling reached an artifact.** ⭐ **That is a FALSE EMPTY
with a third cause — not case (clause (c)), not the plural (clause (b)), but an
artifact that does not name the rule it carries.** ⛔ **Run at MINT time, by the
reviewer who minted it, against the document they just wrote:**

```bash
# For each ruling you minted THIS round, and the pass condition is a FILE, not a count.
# ⛔ RULING 212 (CTO round 52): THREE exclusions, not one, and the command PRINTS them.
#    handoffs/           — a record.
#    BOARD-ARCHIVE.md    — ALSO a record, and `^docs/tasks/handoffs/` never reached it.
#    rulings-index.md    — GENERATED from the records, so EVERY ruling is in it by
#                          construction: the records reshaped, never an artifact reached.
EXCLUDE='^docs/tasks/handoffs/|^docs/tasks/BOARD-ARCHIVE\.md$|^docs/tasks/rulings-index\.md$'
echo "excluded by name: $EXCLUDE"          # ⛔ the REACH printed beside the verdict
for n in <the rulings you just minted>; do
  printf 'Ruling %s -> ' "$n"
  git grep -liP "Rulings?\s+(?:$n|[0-9]+[^.]*\b$n)\b" -- docs src tools tests \
    | grep -vE "$EXCLUDE" | paste -sd' ' -
done
```

⛔ **Pass: every ruling names at least one file that survives `$EXCLUDE`, and the
reviewer confirms one of them is the document the rule was WRITTEN INTO.**
⚠️ **A record is not an artifact: a ruling found only under
`docs/tasks/handoffs/`, only in `BOARD-ARCHIVE.md`, or only in the GENERATED
index has reached nobody, which is why the filter is in the command and not in
the reader's head.**

⛔ **MEASURED at `2d0cfe7` — Ruling 212, `PO-41/3` CONFIRMED and WIDENED:**
Rulings **15**, **62** and **68** each returned `docs/tasks/rulings-index.md` and
nothing else — ⛔ **a PASS under the old filter, a TRUE EMPTY under this one.**
⚠️ **Two fresh IMPOSSIBLE probe numbers read EMPTY as well, and that is the sharp
statement of the defect: with the index in the population this check
distinguished *minted* from *never minted*, NOT *landed* from *not landed* — the
predicate was SUBSTITUTED by a document landing** (Ruling 208's class).
⭐ **At `05e230b` the same three gained `BOARD-ARCHIVE.md` as a second
non-artifact, and the line that did it was the finding's own text.**

⭐ **MEASURED at `1c5e913`, against this office's own round-50 mints:** Ruling 196
returned **one** file, the minting CTO's own handoff — ⛔ **while its rule had been
written into THIS document, whose `RULED ROUND 50` heading named no number at all.**
⚠️ **Its round-48 neighbour names `(Ruling 189)` in the heading and reads
correctly, so the form was already here and was not followed.** ⭐ **The heading
gained `(Ruling 196)` in round 51 and the reading moved to this file. `PO-40/3`,
found by the office that could not fix it.**

### ⛔ RULED ROUND 26 — check 4 gains a SUB-STEP and LOSES a population

⭐ **Two changes, and they pull in opposite directions on purpose.**

> ⛔ **THE POPULATION SHRINKS.** ⭐ An `Owns` cell is a **definition** field: the
> epic carries it, this board POINTS at it, and a brief is built from the EPIC
> (`CTO-31/5`). ⛔ **Check 4 no longer compares the two copies — it asserts the
> second copy does not exist.** ⚠️ **Round 25 widened the population to *rows
> whose fact is written somewhere else* and round 31 added briefs to the
> somewhere-elses; a population that grows every round is a check losing a
> race.** ⭐ **`W` rows are minted here and this board IS their definition, so
> their cells are originals and the rule does not bite them.**
>
> ⛔ **THE SUB-STEP: SUM THE SHARED FILES.** ⭐ **When two rows in one wave share
> a file, the PO sums their expected growth against R11's ceiling BEFORE
> dispatching them in parallel.** ⚠️ **`SF-35` (398) and `SF-36` (399) are each
> legal and their merge is 419 against a ceiling of 400** — ⛔ **R11 is asserted
> per branch and NOTHING asserts it of the pair.** ⭐ **One `wc -l` per shared
> file, and it needs the `Owns` cells to be right, which is why these two
> changes are one instrument rather than two.**

⚠️ **Not an escaped defect and the record says so:** ⛔ **the second lander's
trial merge is branch→tip and `python3 -m tools.quality` fails there.** ⭐ **The
sub-step does not add a gate; it moves the discovery from the review of the
developer who did nothing wrong to the wave-open of the person who sequenced
them.** ⛔ **`PO-26/1`.**

### ⛔ Why, and this round is the entire argument

⚠️ **I ran check 4 once, at open. In the same round, three things it exists to
catch happened AFTER it ran:**

| What moved | When | What the board said until now |
|---|---|---|
| ⛔ **`SF-10` approved and merged `966ab30`** | mid-round | `in-review`, on an unmerged branch |
| ⛔ **Ruling 53 merged into the rubric `1ee184f`** | mid-round | *"pending on an unmerged branch"* |
| **`CTO-18-1` / `CTO-18-2`** | mid-round | uncarried |

⭐ **Check 4 caught three stale rows at open and then went stale itself**, ⛔ **and
it went stale in the paragraph diagnosing exactly that.**

⛔ **A check that runs only at wave-open measures the tree the wave was PLANNED
against, not the tree it produced.** ⚠️ **Its own founding case proves the timing,
and the case is CORRECTED here rather than removed** (Ruling 183's form — ⛔ **a
sentence withdrawn because it was false is replaced by a NOTICE, never by
nothing**):

> ⛔ **`W14` and `W18` did NOT evaporate. They FINISHED, and merged with a verdict
> at `ac4ed55`, and this board went on printing `in flight` for 350 commits.**
> ⚠️ **The sentence stood here, in the document that diagnoses exactly that, and
> it named the wrong mechanism for the case it is the record of.** ⭐ **The true
> mechanism is the one the clause above still gets right — *a trigger that names a
> task is only as good as somebody re-reading the board when that task ends*, and
> a task ends DURING the wave, not before the next one.** ⛔ **`CTO-48/8`, and it
> is the founding case for Ruling 189.**

### ⛔ RULED ROUND 48 — an ASSERTED state owes a corroborating OBSERVATION (Ruling 189)

⭐ **Ruling 171 found that `worktree list` can see a row `git log` cannot, and
concluded the board is the only TOTAL instrument.** ⛔ **It did not say the board
is RELIABLE** — ⚠️ **and the board is the only instrument that ASSERTS in-flight
rather than OBSERVING it, so it is the only one that can be stale in this
direction.** ⭐ **An observed state cannot go stale; an asserted state with no
observer can only be kept freshly wrong.**

> ⭐ **(b) The PRIMARY reading is INTERNAL and needs no git at all.** ⛔ **`state ∈
> {in flight, in-progress, in-review}` ∧ `Checkout = none` ∧ `ahead = 0` is a
> CONTRADICTION printed on ONE ROW**, and the board printed its own refutation, in
> the same row, for 350 commits. ⚠️ **Every instrument read DOWN A COLUMN.**
>
> ⭐ **(c) The CORROBORATING reading is git, and its coverage is the VERDICT
> CONVENTION's coverage.** ⛔ **`git log --merges --first-parent --format='%h %s'
> release/m0-foundations | grep -iE '<row>'` finds the merge only if the merge
> message NAMES the row** — which `Merge <branch>: <line> (CTO: …)` guarantees and
> the pre-clause tail does not. ⚠️ **So a row-state audit is reliable exactly over
> the range the verdict clause governs, and not one commit earlier.**
>
> ⭐ **(d) ADDED CTO ROUND 49, from `PO-38/3`. The ref is derived from the BRANCH,
> never from the ROW, because a branch carries N rows and a merge message names one
> thing: ITSELF.** ⛔ **`--grep '<row id>'` over merge messages is a LOWER BOUND on
> closes and reads `0` for every row that shared a branch** — ⚠️ **measured: all
> three of `W85`, `W86` and `W87` returned nothing, and `W86` is named in no commit
> message on its own branch at all.** ⭐ **So the derivation is TWO steps and both
> are printed: row → branch, then branch → merge.** ⛔ **The first step is an
> ASSERTION and owes clause (c)'s observation like any other; only the second is an
> observation.** ⚠️ **And existence is checked as its OWN command — `git rev-parse
> --verify` before any grep — never behind a pipeline, because a misspelled branch
> and an unmerged branch both return empty.**

⛔ **`--ancestry-path | tail -1` is RECORDED AS WRONG for (c) and is not reused:
it returned a different branch's merge, and the error was caught only because both
forms were run.**

✅ **ALL FOUR CLAUSES NOW HAVE AN INSTRUMENT, landed by `W96`** — ⭐ **(b) as three
floor rules in `../../tools/quality/board/observation.py`, and (c) with (d) as
`../../tools/quality/board/corroborate.py`**, which is run at a wave's close and
is not on the floor. ⛔ **The instrument table above is where each rule's predicate
is stated; this block stays the RULING and does not restate it.**

### ⛔ RULED ROUND 49 — `W100`'s population is DELIMITED, a trigger gains a CLOSED VOCABULARY, and it is NOT one instrument with `W96`

⭐ **The question put to me: should `board-state`'s population be every table that
carries a trigger?** ⛔ **No — every table it can FIND is an inferred boundary, and
this document has already paid for one:** ⚠️ **the first register check inferred
its boundary and an ordinary *In flight* table was read as four duplicate register
rows, so `board-duplicate` fired on the author of `board-duplicate`.** ⭐ **An
inferred boundary moves the moment somebody writes an ordinary table.** The three
clauses:

> ⭐ **(a) A `Trigger` cell IS an asserted state wearing another column name.**
> ⛔ *"before M1's wave opens"* declares **not yet** and has no observer, so Ruling
> 189 binds it. ⚠️ **Measured cost of its not being read: one trigger stood unfired
> through M1's close and all four steps of M2, and the work behind it had been done
> the whole time.**
>
> ⭐ **(b) So the population GROWS BY A DELIMITER, never by inference.**
> ⛔ **`## Scheduled` gains its own `<!-- scheduled -->` / `<!-- /scheduled -->`
> markers and a STATE column, exactly as the register has**, and `board-state`
> reads **both delimited tables and nothing else.**
>
> ⭐ **(c) And a trigger's state comes from a CLOSED SET, declared as the cell's
> first word** — ⛔ **`pending`, `fired`, `expired`, `discharged`** — ⚠️ **so
> EXPIRED becomes REPRESENTABLE, which is the whole defect: the trigger that
> expired could not say so.** ⭐ **The project's standard remedy applied to a
> second status: make the illegal value unrepresentable rather than enumerate it.**

⛔ **AND THE SEPARATION, because a developer is building `W96` this hour and must
not wait:** ⭐ **`W96` and `W100` are TWO RULES, not one instrument.** ⚠️ **`W96`
reads `git` — which nothing in `tools/quality/board/` does today, and that is its
own open design question; `W100` is a PURE TREE property and must not inherit a git
dependency to get built.** ⛔ **So: `W96` is NOT GATED on `W100`.** ⭐ **What they
share is the DELIMITER — one board edit, landing with whichever row arrives first,
and the other reads it rather than adding a second one.**

⭐ **The close run is cheaper than the open run**, and that is why this is not a
doubling: at open, every row whose trigger has passed must be re-measured; ⛔ **at
close, only the rows this wave touched** — the merges are enumerable from
`git log`, so the instrument is *"what moved since I last measured"*, not a sweep.

### ⛔ Ruling 288 (CTO round 60) — a TRIGGER names the ACT that clears it and the OFFICE that can perform that act

⛔ **Ruling 189's family, one clause further: a trigger's state cell is an asserted state, and
an asserted state whose only clearing act is UNAVAILABLE to the office the trigger binds is
Ruling 185(a)'s defect wearing a board trigger.** ⭐ **This is the sentence a PO writing a
`## Scheduled` row is looking for, which is why it is here and not only in the rubric.**

⭐ **THE CLAUSE:** ⛔ **a trigger names the ACT that clears it and the OFFICE that can perform
that act, and its CHANGES-REQUESTED cause attaches to THAT office's round.** ⚠️ **Where the act
is a ROW LANDING, the trigger's discharge condition is that row being IN THE WAVE** — which is
measured, not waited for:

```bash
python3 -m tools.quality 2>&1 | grep '^scheduled'          # by state — … fired N …
git branch --format='%(refname:short)' | grep -F "$THE_ROW_THAT_CLEARS_IT"
```

⛔ **AND THE SECOND HALF, which is the one that saves a round: a trigger whose condition is
ALREADY TRUE is written `fired`, never `pending`.** ⭐ **A trigger whose condition holds is not
pending, and RATIFIED as the standing form.**

⚠️ **MEASURED, CTO round 60, and the defect was the REVIEWER'S from round 59:** of the four
board states available to the PO for a merged row whose close could not be performed, every one
was FALSE (`done`, or `in flight` on a merged row) or RED (`done` with the file deleted, or with
a Ruling 270 stub), ⛔ **so `blocked` was the only compliant cell and the trigger fired against
the one office that could not have prevented it.** ⭐ **A ceiling on a population that grows by
somebody else's merge cannot charge the office that merely REPORTS the growth.**

### ✅ RULING 97 — **the close standard, landed here 2026-09-10 (round 24), because it had reached no artifact**

> ⛔ **A milestone close is a set of measurements at ONE named ref. Every row in
> it must have been taken at that ref. No row is inherited across a ref change.**
>
> ⭐ **The ref need not be the tip, and a close does not go stale when the tip
> moves past it** — the record names its own ref, and a reader can diff that ref
> against the tip to see what has moved since.

⛔ **THERE IS NO ESCAPE CLAUSE, and the reason is that the rows are cheap:
~90 seconds, measured at M1's close.** ⚠️ **If a close row is ever expensive
enough that re-taking it is a real cost, THAT IS THE FINDING** — ⭐ **a milestone
condition nobody can afford to re-measure is a condition that was never really
being checked.** ⛔ **Do not add an exemption; DECOMPOSE THE ROW.**

⛔ **The argument that was REFUSED, recorded because it is the one that will be
reached for again:** ⚠️ *"rows 1–8 are properties of artifacts that merge
unchanged, so they are still true."* ⭐ **That is an argument, not a reading** —
and the decisive answer is a DETECTION argument, which survives *"it would have
been the same anyway"*:

> ⛔ **The version that inherited rows 1–8 would have returned the same verdict
> and would never have noticed it was closing on the wrong ref.**

⭐ **The re-take's value was never the eight verdicts. It was that re-taking them
forces the runner to TYPE THE REF, and typing the ref is what caught `a03aeef`.**

⚠️ **And the corollary for pre-authorisation, which is where this started:**
⛔ **a pre-authorisation may name the DECISION it pre-approves; it may NOT name
the REF, because the ref is an OUTPUT of the run.**

⛔ **And the standing rule this generalises, which is broader than check 4:**
⭐ **a measurement is quoted with the ref it was taken on, or it is not a
measurement.** ⚠️ **Measured this round: the coordinator and I both counted
`host-verified` correctly and reported different answers, and the entire
difference was which tree.** ⛔ **Neither of us named the ref.** ⭐ **A number
without its ref is not a weak claim — it is an unfalsifiable one**, because the
reader cannot reproduce it and disagreement looks like error rather than drift.

---

## ⛔ RULED ROUND 50 — `corroborate`'s THIRD ANSWER is ratified, the HEADER locator is a RAMP, and the `todo` pairing stays PRINTED (Ruling 196)

⚠️ **Three questions `W96` routed to me before it owed code, answered on
measurements I took in a trial merge of `W96` over `chore/po-round39` — which is
the only place either could be answered, because the instrument reads the table
the other branch rewrote.** ⭐ **The reading that matters most:**

```text
corroborate, against the board W96 was written over   : 2 of 2 REFUTED, exit 1
corroborate, against the board chore/po-round39 wrote : 0 of 2 REFUTED, exit 0
  ⭐ SF-26 corroborated at wt/dev1, 2 ahead;  W96 corroborated at wt/dev2, 1 ahead
```

### ⭐ (a) Exit `2` is a REAL third state, and it is RATIFIED as the standing form

⛔ **A clause claiming a third exit code owes that code's INHABITATION, or it is a
pass wearing a number** (Ruling 191). ⭐ **Both producers inhabited, expected
readings written before the commands, in a throwaway clone outside every checkout:**

```text
no release branch in the checkout  -> exit 2, "NOT AUTHORITATIVE — no branch … "
no BOARD.md in the checkout        -> exit 2, "nothing to corroborate."
a corroborated board               -> exit 0   ⭐ all three sentences DIFFER
```

⛔ **Pass condition for any future git-reading instrument in this repository: three
answers, and the unanswerable one is inhabited in the round that ships it.**
⚠️ **And the floor may NOT shell out to git** — ⭐ **the split is FORCED, not
chosen, and the decisive reason is measured rather than stylistic: the floor runs
in a pinned image over arbitrary roots where no release branch exists, so a git
check there would return the PASS reading from an empty population.**

### ⛔ (b) The HEADER-declared locator is a MIGRATION RAMP and NOT a contract

⭐ **Admissible, because it PRINTS which locator answered on every run.** ⛔ **But
it expires when the markers land, and the reason is a measurement rather than a
preference:**

```text
PLANTED: two column NAMES changed in the observation table header
  -> observations (NONE FOUND …): 0 rows     three rules silently inapplicable
  -> quality floor: clean, exit 0            corroborate: 0 of 0, exit 0
  restored: git status --porcelain empty, content diff 0 lines
```

⛔ **A header is INFERRED, so an absent table is indistinguishable from a renamed
column and can only be ANNOUNCED.** ⭐ **A delimiter is DECLARED, so an absent
marker can be REFUSED.** ⚠️ **The printed locator name is the whole of what keeps
the ramp honest, and it is therefore not optional** — ⛔ **so: the `<!-- inflight -->`
markers are OWED as one PO board edit, and the header branch is removed or turned
into a refusal in the round after they land.** ⭐ **It is not a defect in `W96`: the
developer implemented the ruled form and shipped the ramp because the board had not
been edited yet, and said so.**

### ⭐ (c) `todo` against a started observation stays PRINTED, and owes NO rule of its own

⛔ **Because this board's DISPATCH PROTOCOL is exactly that pairing** — a row is
dispatched by naming it in the observation table while its register cell is still
`` `todo` `` — ⚠️ **so a predicate that flagged it would be flagging the protocol,
and its first live reading did: it fired on a row the PO had written correctly.**
⭐ **`W87`'s shape, and Ruling 179's answer applies unchanged: a notice whose first
wave fires on work its author just did is a notice nobody reads twice.**

⛔ **What IS ruled is that the printing is load-bearing rather than decorative:**
the pairing is named on every run, with its ids, in the line the floor prints.
⭐ **A finding remains STARTED against a TERMINAL state, which both cannot be true
of one row** — ⚠️ **and if the dispatch protocol ever changes so that a register
cell moves off `` `todo` `` at dispatch, this clause is what must be re-read, not
the predicate.**

---

## ⛔ RULED ROUND 51 — the TERMINAL predicate is read off the COMMIT GRAPH (Ruling 199), and a close owes a FOURTH edit (Ruling 201)

### ⛔ (a) Ruling 199 — `MERGED ∧ 0-ahead` is REFUTED, the MESSAGE is a corroborator, and the GRAPH is the predicate

⛔ **`corroborate`'s live-checkout arm returns `CORROBORATED` before `merged()` is
ever called, so a leaked worktree keeps a spent row green** (`PO-40/1`, `W110`).
⚠️ **The remedy routed from this office was *MERGED ∧ 0-ahead refutes
unconditionally* and it is WRONG: `merged()` is `merge-base --is-ancestor`, and a
branch cut AT the release tip is an ancestor of it.** ⭐ **Three candidate
predicates, all three measured over the WHOLE local-branch population:**

```bash
R=release/m0-foundations
git log --merges --first-parent --format='%H' $R \
  | while read -r m; do git rev-list --parents -n1 "$m" | tr ' ' '\n' | tail -n +3; done \
  | sort -u > /tmp/absorbed            # ⭐ C: the ABSORBED tips
git log --merges --first-parent --format='%s' $R > /tmp/subjects
git branch --format='%(refname:short)' | while read -r b; do
  A=0; git merge-base --is-ancestor "$b" $R && [ "$(git rev-list --count $R..$b)" = 0 ] && A=1
  B=0; grep -qF "$b" /tmp/subjects && B=1                      # ⛔ SUBSTRING — see (b)
  C=0; grep -qx "$(git rev-parse "$b")" /tmp/absorbed && C=1
  [ "$B" != "$C" ] && echo "DISAGREE $b B=$B C=$C"
done
```

⛔ **Pass: the predicate is `C`, the disagreements with `B` are PRINTED, and a
branch reading terminal under `C` REFUTES even when a checkout holds it.**

⭐ **MEASURED at `1c5e913`, 120 local branches, 173 absorbed tips:**

```text
A  refutes release/m0-foundations ITSELF and chore/cto-round51 — ⛔ correct work,
   on sight. The W87 shape: a predicate that fires on the thing it guards.
B  vs C: 80 agree terminal, 14 agree non-terminal, ⛔ 27 DISAGREE
   25 are C=1 B=0  -> absorbed by a merge whose subject never named the branch
                      (pre-convention history). B's false-NEGATIVE population.
    2 are B=1 C=0  -> ⛔ chore/cto-round3 matched "Merge chore/cto-round39:" and
                      chore/cto-round17 matched "Merge chore/cto-round17-close:".
                      A PREFIX. B's false-POSITIVE mechanism, and it is the
                      SHIPPED `merge_of()`'s own `if branch in subject:`.
C's own blind spot, NAMED rather than hidden: a FAST-FORWARDED merge leaves no
   merge commit. ⚠️ MEASURED, not hypothetical — 7 spent branches read 00.
   ⭐ That failure mode is SAFE: it degrades to today's behaviour and can never
   refute correct work.
```

⛔ **So: `C` is the gate because its only error is a missed refutation; `B` is
PRINTED beside it as the human-readable ref and its substring test becomes an
EXACT match on the `Merge <branch>:` idiom.** ⭐ **A predicate whose failure mode
is a false REFUTATION may not ship; one whose failure mode is a false PASS may,
once the gap is measured and printed.**

### ⛔ (b) Ruling 201 — a close re-points its INBOUND citations, because the pointer check cannot see them

⛔ **`document pointers … 0 unresolved` resolves `](…)` targets ONLY, so a
backticked `` `rows/W96.md` `` in live prose or in a docstring is INVISIBLE to the
one instrument that exists for exactly this** (`PO-40/5`, `W78`).

```bash
for f in $(git grep -lI 'rows/W[0-9]*\.md' -- docs src tools tests); do
  grep -onE 'rows/W[0-9]+\.md' "$f" | while IFS=: read -r ln ref; do
    [ -f "docs/tasks/$ref" ] || echo "DANGLING $f:$ln -> $ref"
  done
done
```

⛔ **Pass: every printed row is a RECORD (`docs/tasks/handoffs/`,
`BOARD-ARCHIVE.md` — ⭐ a record may not be edited), a TEST FIXTURE with a
synthetic id, `W78`'s own tracking table, or ⛔ **THIS CLAUSE'S OWN MEASURED
POPULATION, immediately below** — ⚠️ **which is named here because the instrument
flags its own clause otherwise, and a check that fails on the document that
defines it teaches a reviewer to ignore its output** (Ruling 185's form: narrow
the population and PRINT the name, never widen the predicate).** ⚠️ **Anything
else is the fourth edit, undone.** ⭐ **The remedy is always to RE-POINT at the
archive record, never to delete the sentence** — a citation saying where a design
question was answered is true about the past.

⭐ **MEASURED at the round-40 merge tree: 40 dangling rows, of which `4` are live
non-fixture citations** — `docs/conventions/board.md:179` and
`tools/quality/board/corroborate.py:20` added by `W96`'s own close, plus
`tools/tests/quality/board/test_observation.py:207` → `rows/W95.md` and
`tools/quality/board/register.py:351` → `rows/W18.md` pre-existing.
⚠️ **The PO's population printed `3`; the fourth is `register.py:351`, and
`rows/W18.md` did exist — added at `f7d7e1b`, deleted at `cae114e`.**

### ⛔ (c) Ruling 206 — TWO OWNERSHIP FACTS NO INSTRUMENT CAN READ, and neither is the reporting office's fault

⛔ **Both halves are the same shape: a fact about WHO owns a thing, which every
office can SEE and only one office can ANSWER.**

> ⭐ **(i) A dispatch reads the `Owner` cell, and where shipped work contradicts
> the cell, THE CELL IS THE DEFECT.** ⛔ **MEASURED: `W91`'s register owner reads
> `PO` and the row was dispatched to a developer, who shipped 5 modules and 49
> tests.** ⚠️ **The work is developer work, so the cell was wrong** — ⭐ **but the
> coordinator named that conclusion as a rationalisation after the fact and they
> were right to, so it is RULED rather than assumed: the cell is read BEFORE
> dispatch, and a cell that disagrees with the work a row actually needs is a PO
> fix, never a silent re-assignment.** ⛔ **`W91`'s own register text also still
> read *"rulings run to 186"* against a tail of `197` — the row describing the
> staleness was itself stale, which is why this is a cell defect and not a
> dispatch defect.**

> ⭐ **(ii) A WORKTREE IS INDISTINGUISHABLE FROM A LEAK TO EVERY OFFICE BUT ITS
> OWNER.** ⛔ **So REPORTING one is NEVER wrong, and REMOVING one you did not cut
> is ALWAYS wrong.** ⚠️ **Attribution is answered by the live reviewer, from the
> commit graph, not guessed from the path:**
>
> ```bash
> git rev-list --parents -n1 <the worktree's HEAD>   # ⭐ a trial merge names BOTH parents
> ```
>
> ⭐ **MEASURED, round 51: `…/scratchpad/trial-r51` @ `21a1104`, parents `1c5e913`
> + `696ad81` — the REVIEWER's own live trial merge, reported THREE times by TWO
> offices, and both offices correctly refused to touch it.** ⛔ **Two of the three
> worktrees reported this session really were leaks, so the reports are signal and
> not noise** — ⚠️ **and `corroborate`'s `spent trial/tmp branches` line has the
> same blind spot, which is `W110`'s neighbourhood.**

## ⛔ RULED ROUND 52 — a close-time decomposition, a stale row, and a per-ROW third state

⭐ **The reasoning is in [`../tasks/handoffs/CTO-2026-09-10-round52.md`](../tasks/handoffs/CTO-2026-09-10-round52.md) §4.**

### ⭐ Ruling 213 — a milestone may be DECOMPOSED AT CLOSE TIME; its MEMBERSHIP may not

⛔ **A decomposition authored waves early is a PREDICTION about what the close
will measure, and this project has watched six consecutive waves refute their own
author's written prediction.** ⭐ **So the questions may be authored at the close —
Ruling 97 already says a close is a set of measurements at ONE named ref.**

```bash
# ⛔ The population is declared BEFORE the loop and asserted against its own count.
echo "population declared before the loop: <N> tasks, membership from <file>:<lines>"
# … then the rows … then:
echo "ROWS=<N> asserted against <N>   [Ruling 146]"
```

⛔ **Pass: the membership cites a source that PRE-EXISTS the close, the count is
asserted rather than printed, and the record SAYS the decomposition was authored
at the close.** ⚠️ **A close that chose both its questions AND its population at
the moment of closing can always pass.**

⭐ **MEASURED at `2d0cfe7` (`M2`'s close):** nine rows authored at the close and
declared as such; membership `15 tasks, from README.md:191-194`, `ROWS=15 against
15`; ⛔ **and row 1 re-derives ALL FIFTEEN task merges rather than inheriting four
step closes taken at four moved refs — the first close here to refuse to inherit
its own sub-closes, and the standard for the next.** ⚠️ **A close-time
decomposition also owes its GAPS named rather than omitted.**

### ⛔ Ruling 214 — a row that names a MECHANISM is re-read at DISPATCH against every ruling minted since it was written, and the amendment is ADDITIVE

```bash
# ⛔ At dispatch, not at take. The DISPATCHER runs this; a taker cannot audit a row
#    against rulings they have not read.
git log --oneline --since="<the row's last edit>" -- docs/tasks/handoffs/'CTO-*.md'
```

⛔ **Pass: the row's named mechanism is either unaffected, or SUPERSEDED BY
APPENDED TEXT that leaves the original standing under a heading saying it is
superseded** (Ruling 106's form, applied to a row). ⚠️ **A reworded row loses the
record of what was offered, and a taker on an older base then reads two different
rows with one name.**

⭐ **MEASURED at `05e230b`:** [`W110`'s record](../tasks/BOARD-ARCHIVE.md#w110-corroborates-live-checkout-arm-discharges-a-branch-git-already-knows-is-spent-so-a-leaked-worktree-keeps-a-stale-row-green)
was **three rulings stale inside one wave** and a taker implementing it as written would have shipped a false-terminal
generator. ⛔ **The amendment is 14 lines APPENDED, nothing reworded.** ⚠️ **And
the letter `B` was introduced BY the amendment to retro-label a prose offer that
named no letter — so the row was INCOMPLETE, never self-contradictory.**

⛔ **The corollary, ruled because a refusal that is right for an unstated reason
rots: implementing a ruling and REPORTING its measured cost is ONE task; widening
the predicate is a SECOND.** ⭐ **A developer who widens it on their own reading
has replaced the ruling with theirs, and `W111`'s refusal to widen `B` — having
measured that the fix trades 1 false positive for 19 more false negatives, `27 →
44` disagreements — is CORRECT and is ratified.** ⚠️ **`B` stays as ruled: a
printed corroborator whose errors are false PASSES, which is the side
Ruling 199's asymmetry permits.**

### ⛔ Ruling 216 — *NOT AUTHORITATIVE* is owed PER ROW, not only per PROCESS, and the exit code is a FOLD of the rows

⛔ **`corroborate` has three process codes and a row verdict has two, so *git
could not answer about this branch* lands on `1` — a FALSE REFUTATION, which is
exactly the failure mode Ruling 199 refused in a predicate.**

```bash
# ⛔ Every git reading that can fail returns a THIRD value, and the fold preserves it:
#    one unanswerable row  ->  the run exits 2, never 0 and never 1.
```

⛔ **Pass: a row's verdict carries `corroborated` / `refuted` / `not answerable`;
no `None` reading is coerced to a number; and no message prints a count git never
gave.** ⚠️ **MEASURED at `b5b3982`, and WIDER than `W110/3` filed it:**
`graph.ahead()` returns `None` on failure, `if count:` is falsey, and the
REFUTED arm then prints *"is 0 ahead"* — ⛔ **a number git never produced.** ⭐ **Two
more sites: `_held()` prints *"is None commits ahead"* and returns `refuted=False`
(exit `0`), and `_unnamed()` coerces `ahead(branch) or 0`, silently filing a
failed reading under *invisible to git BY CONSTRUCTION*.**

⭐ **AND THE CORROBORATION IS FROM AN UNRELATED TOOL, which is why this is a rule
and not a row comment:** `python3 -m tools.workspace verify` exits **1** on the
host (a stale pin) and **2** in the pinned container, which mounts one directory
and cannot see a sibling. ⛔ **So the only environment that can TAKE the reading
is the one Ruling 40 does not make authoritative, and the authoritative one
correctly answers NOT AUTHORITATIVE.** ⚠️ **Two instruments reached by different
routes need the same third state, so the third state is a property of this
project's instruments — and Ruling 204 already said a SKIP is a reading OF THE
GATE. This is that, for an exit code.**

## ⛔ RULED ROUND 62 — a HELD row file may be amended, and the test is the DIFF rather than the author's assurance

⚠️ **Reasoning and the measurement that decided it:
[`../tasks/handoffs/CTO-2026-09-11-round62.md`](../tasks/handoffs/CTO-2026-09-11-round62.md).**

### ⛔ Ruling 311 — a post-dispatch amendment to a row a developer is HOLDING is permitted only where it widens NO acceptance clause, and that is READ OFF THE DIFF

⛔ **A row file is read into a taker's context at dispatch, so what the taker acts on is a
SNAPSHOT and not the tree** — ⚠️ **the same property `CLAUDE.md` opens with, and the reason a
row's round-47 section can call *"nobody holds this row"* the SAFE half of a fold.** ⭐ **The
unsafe half is nevertheless permitted, because the alternative is a ruling that lives only in
a record, which is Ruling 295's defect and the very thing such a row exists to close.**

```bash
# ⛔ Run BEFORE amending a row file that a `git worktree list` shows checked out.
#    The amendment must be ADDITIVE and every ACCEPTANCE clause byte-identical.
git diff --numstat "$BASE"...HEAD -- docs/tasks/rows/"$ROW".md    # deletions MUST be 0
git diff "$BASE"...HEAD -- docs/tasks/rows/"$ROW".md | grep '^@@'  # hunks, and where they land
```

⛔ **Pass: `0` deletions, and no hunk touches the clause that states the acceptance.** ⚠️ **An
amendment that widens an acceptance is a re-dispatch, not an amendment, and it is refused —
the holder cannot be failed against a clause their snapshot cannot contain.** ⭐ **Where the
amendment is additive the holder's worst case is that they do not do the extra, and the extra
is not owed: so the snapshot stays sufficient, which is the whole of the permission.**

⭐ **THE MEASUREMENT THAT RATIFIED IT, and it is stronger than any of the three arguments
offered for it** (CTO round 62, in the pinned container): ⛔ **the amendment converted four
rulings into a row that was dispatched and HELD; `git diff --numstat` read `+76 / -0` with a
single hunk appended past the acceptance; and the holder — working from a snapshot taken
BEFORE the amendment existed — landed `266 267 268 269 273 274 275`, which contains ALL FOUR
of the rulings the amendment was being written about.** ⚠️ **A holder who independently does
the work an amendment describes is the proof that the amendment widened nothing.**

⛔ **AND THE DISCLOSURE IS NOT OPTIONAL** (Ruling 283's standing clause): the amending office
states IN THE ROW FILE that the row is held as the section lands, so a later reader can tell a
snapshot-safe section from one taken before dispatch.

---

## ⛔ Ruling 314 (CTO round 64) — Ruling 270 GAINS THE CLAUSE: the archive move RE-ADDRESSES EVERY relative pointer in the moved body, not only the ones aimed at the archive

⛔ **A close moves a row's argument from `docs/tasks/rows/<ID>.md` to
`docs/tasks/BOARD-ARCHIVE.md`, which is ONE DIRECTORY SHALLOWER — so every
relative pointer in the moved body is re-addressed by the move.** ⚠️ **The
closing procedure above enumerates exactly ONE of them** — *re-addressing its
`](../BOARD-ARCHIVE.md#…)` links to `](#…)` now that they are inside it* —
⛔ **and that reads as the complete list because it sits inside a table of FOUR
NAMED EDITS.** ⭐ **It is the SELF-REFERENTIAL case only. Every OTHER pointer in
the body — at a handoff, at a sibling row, at a convention document — is broken
by the same move and is named by no clause.**

⛔ **MEASURED, and the reading is the register office's against its own round**
(`PO-50/2`, routed to me because Rulings 270 and 306 are mine): **the floor found
`10` of them in one close of two rows.** ⚠️ **Ruling 306 extended 270 with the
ANCHOR-collision clause and did not reach the PATH, so the gap survived the one
amendment that was looking directly at it.**

```bash
# ⛔ BEFORE the body is pasted into BOARD-ARCHIVE.md — every relative pointer it carries.
grep -oE '\]\([^)#][^)]*\)' docs/tasks/rows/"$ROW".md | sort -u
# ⭐ Each one is re-addressed by REMOVING one `../`, because rows/ is one level deeper:
#      ](../../conventions/x.md)  ->  ](../conventions/x.md)
#      ](../handoffs/X.md)        ->  ](handoffs/X.md)
#      ](./W99.md) or ](W99.md)   ->  ](rows/W99.md)
#      ](../BOARD-ARCHIVE.md#a)   ->  ](#a)          ⭐ the case the table already named
# ⛔ AFTER the whole close, at the closing office's own ref:
python3 -m tools.quality 2>&1 | grep 'document pointers:'
```

⛔ **PASS: `0 unresolved`, and the closing office states the COUNT it re-addressed.**
⚠️ **`0 unresolved` alone is not the pass condition** — ⭐ **a body whose pointers
were all absolute or all anchors reads `0` without the office having looked, and
that is the run that teaches the next office the step does not exist.**

⛔ **WHY THIS IS A CLAUSE AND NOT A SHRUG, given the floor already catches it:**
⭐ **the floor is a SAFETY NET and it is why nothing has ever been lost here.**
⚠️ **But an office that meets ten broken pointers with no clause telling it to
expect them cannot tell a consequence of its own move from a defect it inherited**
— ⛔ **and the one thing a closing office may NOT do is repair a pointer inside
frozen archived bytes it did not move** (Ruling 106). ⭐ **Knowing which ten are
YOURS is the whole of the difference, and only the clause can say so.**

## ⛔ `W171` — an edit that removes a record section's LAST live pointer is reported over TWO refs, never on the floor

⛔ **The pointer floor asserts that every pointer RESOLVES. A deleted pointer does not dangle, so
it resolves vacuously, and the section it was the last route to is orphaned in silence**
(`CTO-68/4`). ⭐ **Most record headings never acquire a pointer, so the predicate is LAST POINTER
REMOVED, never HEADING UNREFERENCED**, and the unreferenced figure is printed as the denominator.

```bash
# the merging office, on the release checkout, right after each --no-ff merge:
python3 -m tools.quality.board.last_pointer HEAD^1 HEAD
# an office, on its own branch, before hand-back:
python3 -m tools.quality.board.last_pointer "$(git merge-base release/m0-foundations HEAD)" HEAD
```

⛔ **Pass: exit `0`.** Exit `1` names each section and the pointer that was its last. Exit `2`
read nothing and is never a pass (Ruling 191). ⭐ **The remedy is to RE-POINT from a live
document: never delete the sentence, and never edit the record** (Ruling 201(b), Ruling 106).
⛔ **It is not a ban on trimming**: the ask is that the pointer survives the trim.

⭐ **What is a record, a live document and a moved pointer is decided and declared once, in
[the command's docstring](../../tools/quality/board/last_pointer.py)**, and why it is a command
rather than a floor arm is [the handoff](../tasks/handoffs/W171.md)'s design decision.
