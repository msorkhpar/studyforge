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

## ⭐ How to add to the board, by the four things a PO actually does

| You are | Do this | ⛔ Not this |
|---|---|---|
| **minting a row** | one register line, and `../tasks/rows/<ID>.md` with the argument | a mint section on the board |
| **changing a state** | ⭐ **replace the state cell** | append the new state beneath the old one |
| **re-scoping a live row** | edit `../tasks/rows/<ID>.md` — ⭐ **it is a live document and editing it is the point** | annotate the board |
| **closing a row** | ⛔ **THREE edits.** ⭐ set the state to `done` with its merge ref **and repoint the Detail cell at the record**; move `rows/<ID>.md`'s body under a `### <ID> — <naming>` heading in `BOARD-ARCHIVE.md`, **re-addressing its `](../BOARD-ARCHIVE.md#…)` links to `](#…)` now that they are inside it**; delete the row file | leave the row file behind — ⛔ **`board-orphan` will say so** — or leave either link pointing where it used to |
| **writing a round** | ⭐ **`BOARD-ARCHIVE.md`, appended** — and the board's cells change to match | a `## ROUND n` section on the board |

⛔ **The archive is a RECORD: it is appended to and corrected by annotating
beneath, never by editing** (Ruling 106). ⭐ **That is precisely why a live row's
argument may not live there** — and it is the whole reason `rows/` exists rather
than one more archive section.

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
| `board-detail` | a live register row has no `rows/<ID>.md` | an argument with no home is an argument that goes back into the cell |
| `board-orphan` | a `rows/<ID>.md` has no live register row | a file nobody is sent to; ⭐ **the bijection is asserted in BOTH directions, because one of the two always survives a careless edit** |
| `board-duplicate` | one id has two register rows | ⚠️ **the board once carried `W20` twice, as `todo` AND `done`, two rows apart** |
| `board-narrative` | non-table bytes exceed `BOARD_NARRATIVE_CEILING` | ⭐ **invariant to the number of rows** — a new row is a table line and adds nothing to it |
| `board-row-width` | one table row exceeds `BOARD_ROW_CEILING` | a cell that wide is an argument, and an argument goes behind a pointer |
| `board-size` | the whole file exceeds `BOARD_FRAME + BOARD_PER_ROW ×` register rows | ⭐ **the bound with no gap** — see below |
| `board-state` | a register row's state cell DECLARES no state | ⛔ **the hole that let a LIVE row leave the register in silence** — see below |
| `board-frame` | a row file does not begin `# <ID>` **or** does not contain the frame's phrase | ⭐ **the one live-tree property left after Ruling 180.** ⛔ **TWO SUBSTRINGS and nothing more** — it cannot read what the file *says*, and that weakness is what lets it survive every amendment (`CTO-47/4`) |

⛔ **The Ruling 140 plant found a hole in this instrument BEFORE it shipped, and
the third rule is the fix rather than a tweak to the first two.** ⚠️ **Run
against `board-narrative` and `board-row-width` alone: 320 lines of round 33's
narrative, pasted one line per table row, moved the narrative reading by ZERO
and tripped the width rule exactly ONCE.** ⭐ **`board-size` catches it because
text that indexes nothing raises the numerator and leaves the denominator
alone.** ⛔ **The other two are kept as DIAGNOSIS: `board-size` says the board is
too big, and they say WHERE — a governor that only says *too big* is one
somebody raises rather than obeys.**

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
> ⭐ **And the reason both clauses go the same way:** this check's failure mode is
> a **FALSE EMPTY** — *"nobody carried it"* returned for something that was
> carried. ⛔ **So it is tuned to OVER-match, and that is safe for one specific
> reason: check 3 prints FILES, not a count.** ⚠️ **A false positive costs one
> `git show`; a false empty costs a lost ruling.**

⛔ **The instrument, and it is PCRE (`-P`), not ERE** — `(?:`, `\s` and `\b` are
not POSIX ERE and `git grep -E` refuses the pattern outright with *"Invalid
preceding regular expression"*:

```bash
# For each ruling minted since check 3 last ran. ⛔ FILES, never a count.
for n in <the rulings>; do
  echo "Ruling $n:"
  git grep -lP "Rulings?\s+(?:$n|[0-9]+[^.]*\b$n)\b" -- docs src tools tests | sort
done
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
against, not the tree it produced.** ⚠️ **Its own founding case proves the
timing:** `W14` and `W18` evaporated because *"a trigger that names a task is only
as good as somebody re-reading the board when that task ends"* — ⭐ **and a task
ends during the wave, not before the next one.**

⭐ **The close run is cheaper than the open run**, and that is why this is not a
doubling: at open, every row whose trigger has passed must be re-measured; ⛔ **at
close, only the rows this wave touched** — the merges are enumerable from
`git log`, so the instrument is *"what moved since I last measured"*, not a sweep.

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

---
