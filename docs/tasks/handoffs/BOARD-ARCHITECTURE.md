# BOARD-ARCHITECTURE — handoff

**Kind:** office handoff — ARCH

**Status:** done

**Base:** `c65b8a4` (MAIN, `release/m0-foundations`) · **Merge:** `3aedd40`
(`chore/board-architecture`, `wt/arch`)

⚠️ **The tip moved FOUR times under this branch** — PO round 35 + `W76`
(`bfb8c8c`), `W70` + CTO round 44 (`9a57b13`), CTO round 45 (`4b25274`),
`SF-14` + CTO round 46 (`c65b8a4`).
⭐ **`BOARD.md` was untouched by the last two**, so each cost one register cell:
the partition is heading-driven rather than line-numbered.

⛔ **CHANGES REQUESTED at CTO round 45, and both items were real text loss and a
real hole.** ⭐ **`ARCH/10`, `ARCH/11` and `ARCH/12` below are what came back**,
and the load-bearing claim of the pushback — *it is a partition* — is now
asserted over CONTENT rather than over line counts.

---

## What landed

⭐ **`docs/tasks/BOARD.md` is now a REGISTER**, and everything that is not a
register row has a single other home.

| Artifact | What it is |
|---|---|
| `docs/tasks/BOARD.md` | **238 lines / 24 KB.** Milestones, in flight, next rows, the `W` register, R21, standing decisions, Scheduled, cross-repo — ⛔ **identity, naming, owner, state, pointer, and nothing else** |
| `docs/tasks/rows/<ID>.md` | **50 files**, one per row that is not `done`. ⛔ **Titled `# W40` — no naming, no owner, no state.** ⭐ **Zero duplicated facts, by construction** |
| `docs/tasks/BOARD-ARCHIVE.md` | **9,737 lines.** Every line of the old board, verbatim — including ⭐ **the 78 register lines `CTO-45/1` found had gone nowhere** — plus the 28 closed rows' bodies |
| `docs/conventions/board.md` | ⭐ **The standing contract** — one-fact-one-home, what a row may carry, how the PO adds to the board, the instrument. **The wave checks moved into it whole** |
| `tools/quality/board/` | ⛔ **A PACKAGE (R11)** — `__init__.py` carries the six checks, `register.py` the parser where both of `CTO-45`'s defects lived |
| `tools/tests/quality/board/` | **60 tests** — `test_init.py` (the six rules), `test_register.py` (the two `CTO-45` defects, verbatim corpus), `test_migration.py` (⭐ **Ruling 177, four equalities, subject = a named ref under Ruling 180**) |
| `docs/conventions/delivery-flow.md` | Four lines: `## The board` now points at `board.md` |
| `tools/quality/handoffs/__init__.py` | ⛔ **One new document kind, `office handoff`, which owes EXACTLY what a task handoff owes** — `ARCH/8` |
| `docs/conventions/agent-protocol.md` | The new kind, named where handoffs are described |

## The measured before/after

⛔ **Both readings taken at named refs, `python3 -m tools.quality` in the tree
that printed the sha (Ruling 172).**

```text
$ ./docker/dev/check sh -c 'git rev-parse HEAD; ruff --version; ruff check .;
                            ruff format --check .; python3 -m tools.quality;
                            python3 -m pytest -q'

MAIN(base)  -> c65b8a4efeea9784a7df0283dadd2b19e63295e0
  ruff 0.16.6 · check: All checks passed! · format: 633 files already formatted
  document pointers: 205 read in 224 markdown files, 86 anchored, 0 unresolved
  quality floor: clean            (no `board:` line — the check does not exist there)
  4279 passed, 63 skipped

MERGE(arch) -> 3aedd409490c865c576223c89cb3ae1cd632b1cf
  ruff 0.16.6 · check: All checks passed! · format: 689 files already formatted
  document pointers: 353 read in 275 markdown files, 125 anchored, 0 unresolved
  board: 78 register rows, 50 live, 50 detail files in docs/tasks/rows/;
         4393 bytes narrative of 8192, widest row 415 of 600,
         24388 bytes total of 32032 allowed
  quality floor: clean
  4342 passed, 63 skipped
```

⛔ **Two different shas printed from inside the same invocation as the numbers**
(Ruling 172), ⭐ **so the base and the merge cannot have been paired wrongly.**
⚠️ **`+63` tests: 60 in `tools/tests/quality/board/` and 3 for the office-handoff
kind.** ⛔ **One F401 was caught by the PINNED image alone** — the host has no
ruff, and `quality floor: clean` has never meant lint-clean (Ruling 78).
⚠️ **Skips are 63 in BOTH — 55 `tests/visual/` + 5 `tests/docker/` + 3
`tests/test_knowledge_index.py`.** ⛔ **A host run of `wt/arch` reads 13 instead,
because the host has a browser and the pinned image has none (`QA-03/1`) — the
two numbers describe the MACHINE, not the tree.**

| | ⛔ `bfb8c8c` | ⭐ after |
|---|---|---|
| `BOARD.md` | **8,545 lines / 770,843 B** | **246 lines / 24,388 B** |
| bytes NOT inside a table | 382,194 | **4,393** |
| bytes inside tables | 388,649 | 19,995 |
| widest single table row | **3,485 B** | **415 B** |
| ⭐ **bytes a reader must load per `W` id indexed** | **9,757** | **308** |
| ⭐ **the same, in tokens at 4 B/token** | **~2,439** | **~77** |

⭐ **The number that answers the user's question — *what must a reader load to be
correctly oriented?*** ⛔ **Before: the whole file, ~193k tokens, which is larger
than most agents' entire budget** — so in practice nobody loaded it, and the
proof is in the file itself: **its own paragraph claimed the live board was
"~56KB" while it was 753KB**, and that sentence stood for twelve rounds in the
document every agent reads first. ⭐ **After: 24 KB, ~6k tokens, and the whole
register is in it.**

**Deriving command**, run in `wt/arch` (Ruling 126):

```sh
python3 - <<'PY'
import subprocess, pathlib, re
old = subprocess.run(["git","show","bfb8c8c:docs/tasks/BOARD.md"],
                     capture_output=True, text=True).stdout
new = pathlib.Path("docs/tasks/BOARD.md").read_text(encoding="utf-8")
for name, t in (("BEFORE", old), ("AFTER", new)):
    lines = t.split("\n"); tbl = [l for l in lines if l.startswith("|")]
    nar = sum(len(l.encode())+1 for l in lines if not l.startswith("|"))
    ids = {m for m in re.findall(r"\bW\d+\b", t)} - {"W99"}
    b = len(t.encode())
    print(name, len(lines), b, nar, b-nar,
          max(len(l.encode()) for l in tbl), len(ids), b//len(ids))
PY
```

## Decisions

### ⭐ 1. The shape: a PARTITION, not a summary — and that is how it reconciles with the round-25 ruling

⛔ **The PO's standing rule is *"Nothing was summarised. Closed sections moved
whole, unedited"*, and it is right.** ⭐ **This work does not break it: every
line of the old board is in the record, verbatim.**

⛔ **AND IT IS NO LONGER A SUM — the word is withdrawn, `CTO-46/5`.** ⚠️ **The
old sum was TRUE and it was the wrong instrument: it passed while 28,262 bytes
of the Status column reached nothing** (`ARCH/10`). ⭐ **Ruling 177 replaced it
with four equalities over content:**

```text
$ python3 -m pytest tools/tests/quality/board/test_migration.py -q
6 passed

  BASE   = bfb8c8c                          (the migration's input)
  OUTPUT = 5688dcd1a280aaaee27aa1d0763ce897389f2e3e   (its output — Ruling 180)

  every line of BOARD.md@BASE is verbatim in a destination
      -> 2 of 8,546 differ, both ARCH/4's re-addressed anchor, and the test
         asserts BOTH the count and the re-addressed form (a third fails it)
  every consumed register line is in the RECORD          -> 78 of 78
  every block of every row file at OUTPUT is a WHOLE CELL of its own row
  no row file at OUTPUT carries the status column
  both readers SKIP on an unreachable ref
```

⛔ **BOTH halves of the pair are refs, and the working tree is not this module's
business** (Ruling 180, `ARCH/13`). ⭐ **The live tree's shape is the FLOOR's —
`check_board`, which is amendment-safe by construction.**

⭐ **Both directions run** (Ruling 122): the damaged files restored from
`e9ddf9d` name **exactly the three fragments**; stripping the record names
**80 of 8,546** and **78 of 78**; ⛔ **an unreachable ref SKIPS rather than
passing** — `0 = 0` wearing a migration is the reading this exists to refuse.

⭐ **And the readings that decide whether the contract and the instrument agree
— expectations written before any command ran, tree restored and
`git status --porcelain` printed between rows:**

| # | the action, in the contract's own words | migration | floor | `board:` |
|---|---|---|---|---|
| **R1** | live | **6 passed** | exit 0, clean | `78 / 50 / 50` |
| **R2** | *"re-scope a live row — editing it is the point"* | ⭐ **6 passed** | exit 0, clean | `78 / 50 / 50` |
| **R3** | *"mint a row — one register line, and `rows/<ID>.md`"* | ⭐ **6 passed** | exit 0, clean | `79 / 51 / 51` |
| **R4** | *"close a row"* — cell, move, delete | **6 passed** | exit 0, clean | `78 / 49 / 49` |
| **R5** | ⛔ negative control: an ORPHAN row file | 6 passed | ⛔ **exit 1, `[board-orphan]`** | — |
| **R6** | a 228-byte status fragment appended to a live row | 6 passed | exit 0 | ⚠️ **silent, and `ARCH/14` says why** |
| **R7** | ⛔ a row file that LOST its frame | 6 passed | ⛔ **exit 1, `[board-frame]`** | — |

⚠️ **R2 and R3 were `1 failed, 5 passed` and `2 failed, 4 passed` before this
round** — ⛔ **the branch's own contract reddening the branch's own suite.**

⚠️ **R4 took THREE runs and the first two failures were my PLANT's, not the
instrument's** — a row body carries `](../BOARD-ARCHIVE.md#…)` links that must be
re-addressed to `](#…)` when the body moves INTO the record, and the register's
Detail cell must change too. ⭐ **The pointer check caught both, which is the
instrument doing its job on the person testing it** — and the contract now says
closing a row is three edits rather than two.

⭐ **Where each of the old board's 8,545 lines is now, and it DOES account for
all of them** (`CTO-46/5` — the earlier table dropped the 78 and stood under the
word *sum*):

| Destination | Lines | Why there |
|---|---|---|
| `BOARD-ARCHIVE.md` — the moved block | **8,351** | rounds, close runs, mint arguments, carried rulings — ⛔ **a record, appended to and never edited** (Ruling 106) |
| `BOARD-ARCHIVE.md` — ⭐ **the 78 register lines, verbatim** | **78** | ⛔ **the ones `CTO-45/1` found had gone nowhere**, Owner and Status columns included |
| `BOARD.md` | **16** | the *Scheduled* table, verbatim |
| `docs/conventions/board.md` | **101** | the wave checks — ⛔ **a process is not a state** |
| ⭐ **total** | **8,546** | ⚠️ 8,545 lines plus the trailing empty line `split` yields |
| `rows/<ID>.md` | ⛔ **NOT a destination** | a LIVE EXTRACT of 50 rows' arguments — ⭐ **the record keeps the original, which is what lets a row file be amended** |

⚠️ **The board's live facts — milestone refs, in-flight rows, namings, owners,
states — were RE-DERIVED on the new board rather than moved, so they also appear
in the archived block.** ⛔ **That is not a second copy of a state: it is a
reading with an as-of, which this project already distinguishes** (`PO-30/2`).
⭐ **The archive banner says which one is authoritative in one sentence.**

### ⭐ 2. *When a fact changes, how many files must change?* — **ONE, and with no assertion needed**

⛔ **The obvious design has the board's naming and the row file's H1 carrying the
same sentence, kept honest by a check.** ⭐ **That was rejected: it is still two
copies, and a copy kept true by an instrument is a copy.**

⭐ **A row file is titled `# W40` and carries no naming, no owner and no state.**
So:

| The fact | Changes | Files touched |
|---|---|---|
| a row's state | `todo` → `done` | **1** — `BOARD.md` |
| a row's argument | re-scoped, re-framed, struck | **1** — `rows/W40.md` |
| a row's naming | re-worded | **1** — `BOARD.md` |
| a task's `Owns` | | **1** — the epic |
| a round's reasoning | | **1** — `BOARD-ARCHIVE.md` |

⛔ **Closing a row touches two files and that is not an exception — it is a MOVE:
`rows/W40.md`'s body goes under a heading in the archive and the file is
deleted.** ⭐ **`board-orphan` fails the build if the second half is skipped.**

### ⭐ 3. Why live rows need FILES and not archive anchors, measured

⚠️ **The cheap alternative was to point every live row at the round section where
it was minted — zero new files.** ⛔ **It is wrong, and the board says why: `W72`
was RE-SCOPED at round 34, `W40` RE-FRAMED at round 27, `W51`'s ordering claim
STRUCK, `W38`'s clause replaced by a derivation, `W44`'s acceptance replaced
because the instrument it named was inverted.** ⭐ **A live row's argument is
amended, and Ruling 106 forbids amending a record.** ⛔ **Pointing a live
instruction into a frozen record is exactly the append-beneath defect this
document has committed four times.**

### ⛔ 4. `docs/tasks/rows/` is DESCRIBED by the knowledge index, and I did not change the tuple

⚠️ **`UNDESCRIBED_PATHS` in `tools/knowledge/index.py` is
`("docs/tasks/handoffs", "docs/tasks/BOARD.md", "docs/tasks/BOARD-ARCHIVE.md")`
and `tools/knowledge/` is not mine.** ⛔ **So `docs/tasks/rows/` is described, and
editing a row file will mark the index STALE.**

⭐ **Measured, so the cost is a number and not a worry** (over the 40 commits
before the split, in `wt/arch`):

```sh
for c in $(git rev-list -n 40 HEAD); do
  git diff --name-only "$c^" "$c" \
  | grep -E '^(src|tools|docs)/' \
  | grep -vE '^docs/tasks/(handoffs/|BOARD\.md|BOARD-ARCHIVE\.md)' | wc -l
done
```

| Reading | Count |
|---|---|
| commits that already stale the index | **18 of 40** |
| ⛔ **commits the exclusion ACTUALLY saved a rebuild for** | **21 of 40** |

⛔ **So the exclusion is doing real work, and putting row files in a described
path converts a large share of those 21 into stale-makers — reintroducing
`CTO-25/9`, the defect `W39` just closed.** ⭐ **`ARCH/1` is the proposed
one-line tuple entry, and it does NOT weaken the check: the tuple's own docstring
states the principle as *"a change anywhere else — a board row, a handoff — does
not make the index wrong"*, and a per-row detail file IS a board row.** ⛔ **This
is the same exemption re-spelled for the same subject's new carrier, not a
widened one.**

⚠️ **Timing, stated so nobody is surprised:** this merge makes the index stale
anyway (it touches `docs/conventions/`), so there is no window where this change
alone reds the floor. ⛔ **The regression begins at the next PO round that edits
a row file**, which gives the tuple row one full round to land.

### ⭐ 5. The wave checks moved to `docs/conventions/board.md`

⛔ **They are a process, and the board is state.** ⭐ **They are also the board's
own operating procedure, so the document that governs the board is where they
belong.** ⚠️ **Moved WHOLE and unedited, and reversible in one commit if the PO
disagrees — this is the one call in here that is squarely inside the PO's
territory, and it is flagged rather than assumed.**

## Surprises

### ⛔ 1. The check found a hole in ITSELF before it shipped — twice

⭐ **Ruling 140's adversarial plant did exactly what it exists to do, and it found
a real gap in my first instrument:**

| Plant | `board-narrative` | `board-row-width` | Verdict |
|---|---|---|---|
| round 33's narrative appended as prose | 17,903 / 8,192 ⛔ | 1 hit | caught |
| ⛔ **the same, pasted ONE LINE PER TABLE ROW** | **3,436 — unmoved** | **1 hit** | ⛔ **GOT THROUGH** |

⛔ **320 lines of a round's narrative moved the narrative reading by ZERO and
tripped the width rule ONCE.** ⭐ **`board-size` is the fix and it is a third
bound rather than a tweak: the whole file against
`BOARD_FRAME + BOARD_PER_ROW × register rows`.** ⚠️ **Text that indexes nothing
raises the numerator and leaves the denominator alone.**

⭐ **Second defect, found by the check firing on its own author:** the first
`_register` inferred the register from row shape — *any five-cell row naming a
`W` id* — ⛔ **and the very next edit, an *In flight* table naming four rows, was
read as four DUPLICATE register rows.** ⭐ **The register is now delimited by
`<!-- register -->`; an inferred boundary is one that moves when somebody writes
an ordinary table.** ⚠️ **Both defects are kept as tests.**

### ⭐ 2. Ruling 163's population is not what I expected, and my restructure breaks none of it

⛔ **`W78` carries 105 live line-number citations. Measured here, into
`BOARD.md`/`BOARD-ARCHIVE.md` specifically:**

```sh
grep -rnoE 'BOARD(-ARCHIVE)?\.md:[0-9]+' --include=*.md docs/
```

| | Count |
|---|---|
| in **live** documents | **1** — and it is inside `BOARD-ARCHIVE.md`, ⭐ **a record, where Ruling 163 makes it admissible** |
| in `docs/tasks/handoffs/` (records) | **20** |
| ⭐ **admissible citations this restructure breaks** | ⛔ **ZERO** |

### ⭐ 3. The pointer checker DOES resolve same-file anchors, and the restructure improved its coverage

⚠️ **I had inferred from a count mismatch that bare `](#anchor)` links were
unchecked. That was WRONG, and the instrument corrected me**: two dangled
immediately when the wave-checks heading left the file. ⭐ **The move converts 21
same-file anchors in row files into cross-file, path-carrying pointers**, and the
coverage denominator rises **205 → 353 pointers in 219 → 270 files, 86 → 124
anchored, 0 unresolved throughout.**

### ⚠️ 4. Skip count reads 13 here, not 63, and it is the checkout

⛔ **`wt/arch` has a browser on the host, so `tests/visual/` RUNS rather than
skipping.** ⭐ **13 = 7 `tests/docker/` (5 image-build + 2 in-image) + 3
`tests/test_knowledge_index.py` (no sibling checkouts) + 3 ruff-absent
(`tests/test_repository.py` ×2, `tools/tests/quality/test_lint.py`).**
⚠️ **MAIN's 63 includes 55 `tests/visual/`, which is a property of the machine
and not of the tree** — ⛔ **the two numbers are not comparable and neither is
wrong.**

## Findings

⛔ **Every claim states whether it was MEASURED here or RECEIVED, and from
whom** (Ruling 115). ⭐ **Each finding carries its own marker on its heading.**

### ARCH/1 `[structural]` — `docs/tasks/rows` belongs in `UNDESCRIBED_PATHS`, and the tuple is not mine

**Measured** (`wt/arch`, `bfb8c8c`): the exclusion saves a rebuild on **21 of the
last 40 commits**; **18 of 40** already stale the index. **Received**: the brief
states `tools/knowledge/` is not this office's.

⭐ **Proposal, one line:**

```python
UNDESCRIBED_PATHS = (
    "docs/tasks/handoffs",
    "docs/tasks/rows",  # ⭐ a board row's argument IS a board row
    "docs/tasks/BOARD.md",
    "docs/tasks/BOARD-ARCHIVE.md",
)
```

⛔ **Owed to the PO as a row, before the next PO round edits a row file.**
⭐ **`tools/tests/knowledge/test_index.py`'s assertions are derivations and pass
unchanged — verified by reading them, not by running the edit.**

### ARCH/2 `[structural]` — the board's self-description was stale by 13× for twelve rounds

**Measured**: `BOARD.md` line 479 @ `bfb8c8c` still read *"Live board ~56KB"* in
a file of **753 KB**. ⛔ **Fixed by removal — the sentence is now in the archive
with the round that wrote it, and the live number is PRINTED by `board_state` on
every floor run instead of being typed.** ⭐ **Ruling 55's own remedy: do not
maintain a number by hand.**

### ARCH/3 `[structural]` — `delivery-flow.md` already forbade what happened, and nothing enforced it

**Measured**: `docs/conventions/delivery-flow.md` `## The board` has carried *"A
status change is one cell. Do not restructure the tables to record an event; add
a line to the **Log** instead"* since it was written. ⛔ **The board reached 8,545
lines under that sentence.** ⭐ **This is not a new rule; `board.md` is that rule
with an instrument.** ⚠️ **The general finding is the one worth carrying: THIS
PROJECT'S OWN LESSON — a rule recorded only in prose has not landed — was
committed by the document that governs its most-read file.**

### ARCH/4 `[local]` — two links inside moved material were RE-ADDRESSED, and that is an edit

**Measured**: `2` occurrences of `](#the-wave-checks-…)` inside the 8,351 archived
lines pointed at a heading that moved to `docs/conventions/board.md`.
⛔ **Retargeted rather than left dangling**, because the pointer check is live
and must stay at zero unresolved.

⚠️ **ACCEPTED by Ruling 174, on a NARROWER ground than I argued, and the
correction matters.** ⛔ **My *"a pointer is an ADDRESS, not a statement"* is
REFUSED** — ⭐ **it would license editing frozen records, which is exactly what
Ruling 106 exists to stop.** ⭐ **The admitted ground: Ruling 106's freeze
attaches when material BECOMES a record, not while it is being moved into one.**
⚠️ **2 lines of 8,546; no other byte was changed, and
`test_migration.py::test_every_line_of_the_old_board_survives_verbatim` now
asserts exactly that — it fails if a THIRD line ever differs.**

### ARCH/5 `[local]` — one line-number citation inside the archive is now false

**Measured**: `BOARD-ARCHIVE.md` carries `BOARD.md:2444`, written when that line
existed. ⛔ **NOT corrected: it is inside a record and Ruling 106 forbids
editing one.** ⭐ **It is admissible under Ruling 163 precisely because it is in a
record, and a record's citations are read as *"at the time"*.**

### ARCH/6 `[structural]` — Ruling 171's two instruments disagree by one row in EACH direction

**Measured** (`bfb8c8c`, 108 non-release branches asserted against 108):

```text
git worktree list  ->  MAIN(release) · wt/arch · wt/cto44 · wt/dev1o(feat/SF-14-index)
branches ahead     ->  chore/W70-consumer-clause-sweep +3 · chore/board-architecture +1
```

⛔ **`git log` is blind to `SF-14` (a checkout, no commit); `git worktree list` is
blind to `W70` (commits, no checkout).** ⚠️ **Every prior round recorded the
disagreement in ONE direction.** ⭐ **This is the first reading where it goes both
ways at once, which strengthens `CTO-38/2`/Ruling 171 rather than qualifying it:
the union is a lower bound and the board is the only total instrument.**

### ARCH/7 `[local]` — `W70`'s population is UNCHANGED by this move

**Measured**: `Acceptance` occurrences — **108 in 14 `docs/tasks/E*.md`,
unchanged** (no `E*.md` was touched). ⛔ **The board's 56 occurrences moved to
`BOARD-ARCHIVE.md`, which is still under `docs/tasks/`, and 2 landed in
`rows/`** — ⭐ **so the population is unchanged whether `W70`'s sweep is scoped to
`E*.md` or to all of `docs/tasks/`.** ⚠️ **`W70` is in flight; it will merge into
a tree where its subject did not move.**

### ARCH/8 `[structural]` — `docs/tasks/handoffs/` had no kind this document could declare

**Measured**: `DOCUMENT_KINDS` held five kinds, and this document fits none.
⛔ **`task handoff` requires a task ID and THIS OFFICE DOES NOT HOLD THE ID
SPACE**; ⚠️ **`survey` says *"nothing landed, so nothing to hand over"*, which is
false here.** ⭐ **So the only ways to file it were to mint an id I may not mint,
or to declare a kind that owes NOTHING and thereby dodge the very contract this
work exists to strengthen.**

⛔ **Added `office handoff`, and it owes EXACTLY what a task handoff owes** — the
six sections, the markers, the title — ⭐ **with one inversion: it declares a
SCOPE that must NOT parse as a task ID (`— ARCH`), because naming one would be
minting one.** ⚠️ **A kind that lets a document escape the contract is not a
kind, it is a hole**, and the three tests say so in both directions.

⚠️ **This touches a shared contract (`tools/quality/handoffs/`) and the migration
is zero — measured: no existing document declares the new kind, and the
parametrised *owes-only-its-declaration* test now excludes it by name rather
than by an exclusion list.** ⛔ **It is offered for the CTO to accept or reject;
if rejected, this document needs an id from the PO instead.**

### ARCH/10 `[local]` — the partition was over LINES, and three files carried the wrong cell

**Received** from `CTO-45/1`; **measured** here. ⛔ **A naive `|` split broke on
pipes INSIDE CODE SPANS**, so `rows/W38.md`, `rows/W40.md` and `rows/W53.md` each
carried a mid-sentence fragment of the STATUS cell — text that existed nowhere
else in the tree.

| The row | The span that broke it |
|---|---|
| `W38` | ``(py\|md under tests/fixtures/)`` — an unescaped pipe |
| `W40` | ``'gated BEFORE\\\|gated before'`` — a regex alternation |
| `W53` | ``` `\\\| wc -l` ``` — a shell pipeline |

⭐ **Every one is a pipe no renderer splits on either**, so the parser was not
merely strict — ⛔ **it disagreed with what the reader sees.**

⛔ **The residue was a COLUMN, not three files: 28,262 bytes of Owner and
Status reached no destination**, and three files were only where it became
unrecoverable. ⭐ **Fixed at the level the loss happened: the 78 consumed
register lines are now in `BOARD-ARCHIVE.md` VERBATIM**, which makes the claim
simpler and stronger — ⭐ **every line of the source board is in the record, and
`rows/` is a LIVE EXTRACT rather than a fourth destination.**

⚠️ **`cells()` reuses `pointers.strip_code_spans`, which blanks spans while
keeping columns** — ⭐ **the same trick, for the same reason, in a third
instrument.**

### ARCH/11 `[structural]` — `is_closed` was a substring test, and the failure was silent

**Received** from `CTO-45/2`; **measured** here. ⛔ **A live row whose state cell
merely MENTIONED `done` was closed**: no detail file owed, out of the bijection,
`quality floor: clean`, no finding.

⚠️ **The population, printed before the scalar** (`register`/`state` over the
live board, expected `0 undeclared` before running):

| declared state | rows |
|---|---|
| `todo` | 43 |
| `done` | **28** |
| `accepted` | 2 |
| `in flight` | 2 |
| `routed`, `in-progress`, `in-review` | 1 each |
| ⛔ **undeclared** | **0** |

⛔ **28 of 78 carry the `✅ done — <ref>` idiom, so a live cell was one
subordinate clause away** — ⭐ **not exotic, routine.**

⭐ **Closed by the standard remedy — make the illegal value unrepresentable.** A
state cell DECLARES its state from a closed set, matched **on a word boundary**;
`board-state` is the finding when it declares nothing. ⚠️ **Two live cells failed
on the day it landed, `W5` and `W16`, and both were rows a reader would have
sworn were fine.** ⭐ **The word-boundary rule came from the IMPOSSIBLE reading,
not from argument: a prefix match read `DONE-ish` as `done`.**

### ARCH/12 `[local]` — the instrument outgrew R11 and is now a package

**Measured**: `tools/quality/board.py` reached **431 lines** against R11's 400.
⛔ **Split as a package, never as a file** (`CLAUDE.md`): `board/__init__.py`
carries the checks, `board/register.py` the parser, and the test tree mirrors it.
⭐ **The parser was the right seam anyway — both of `CTO-45`'s defects live in
it, and they now have a module whose whole docstring is about them.**

### ARCH/13 `[structural]` — the migration test's subject was the WORKING TREE, and the contract turned it red

**Received** from `CTO-46/1`; **measured** here. ⛔ **Two of the four things
`docs/conventions/board.md` tells a PO to do reddened a test shipped in the same
commit** — re-scoping a live row (`1 failed, 5 passed`) and minting one
(`2 failed, 4 passed`, while the floor stayed clean and read `79/51/51`).

⛔ **It is `CTO-45/1`'s own class inside `CTO-45/1`'s fix: the right PROPERTY
over the wrong SUBJECT.** ⚠️ **And I had already reasoned about it correctly one
test over** — `test_the_row_files_are_an_extract_…` sliced `[:1]` precisely so
amendment would survive — ⭐ **which makes it an oversight, and a `[:1]` slice a
WORKAROUND for the wrong subject rather than a design.**

⭐ **Ruling 180: a migration test's subject is the migration's OUTPUT at a named
ref.** Both halves of the pair are now refs — `BASE = bfb8c8c` and
`OUTPUT = 5688dcd…` — and the row files are read with `git show`, exactly as the
input already was. ⛔ **The `[:1]` slice is gone: every block of every file is in
scope, because nothing in the working tree can move it.**

⚠️ **Sha written in full, not abbreviated: a short sha is a prefix, and a prefix
can become ambiguous in a repository that keeps growing.** ⭐ **The population is
asserted — `assert len(names) == 50` — so a typo in the ref empties nothing
silently** (Ruling 48).

### ARCH/14 `[local]` — what Ruling 180 COSTS, and the guarantee I put back

⛔ **Ruling 180 is right and it is not free: bound to a ref, `test_migration.py`
stops watching the live tree entirely.** ⚠️ **Measured — `R6` re-run: a 228-byte
fragment of the status column appended to a live `rows/W40.md` is now invisible
to BOTH the migration test and the floor.**

⭐ **And on inspection that is CORRECT, not a hole.** ⛔ **Appending prose to a
row file is the contract's own prescribed action**, so no checker can tell *"the
PO re-scoped a row"* from *"the PO pasted a fragment"* — ⚠️ **and one that tried
would be exactly the gate Ruling 180 just removed.**

⭐ **What IS still a defect, and now fires: a row file that loses its IDENTITY.**
`board-frame` requires every row file to open `# <ID>` and say what it is.
⛔ **It survives every amendment by construction** — amending a row adds to its
argument and never removes its frame — ⚠️ **so it is the one thing that can be
required of a file the PO is told to edit freely.** **Measured, `R7`:
`floor-exit=1`, `[board-frame]`, with a true message.**

### ARCH/15 `[local]` — the contract typed five measurements of the thing it governs

**Received** from `CTO-46/2`; **all five stale at merge**. ⛔ **`ARCH/2`'s own
defect recurring inside `ARCH/2`'s remedy — the *"live board ~56KB"* sentence,
in the document written to kill it.**

⭐ **Ruling 181 applied by REMOVAL, which is Ruling 161's shape: the fix for an
unmaintainable copy is removing the subject.** `docs/conventions/board.md` now
types **no** measurement of the board; it shows `board_state`'s printed line and
points at the handoff for the `bfb8c8c` readings, which are a record beside
their ref (Ruling 169). ⚠️ **`ARCH/2` claimed the number was *printed, not
typed*, and that claim is true for the first time.**

### ARCH/16 `[local]` — three fold-ins, and one of them was a real number in the wrong place

⛔ **`CTO-46/3`** — `board.md` named `tools/quality/board.py`, which `ARCH/12`
deleted in the same branch. ⚠️ **Inline code, not a link, so the pointer check
could not see it.** Fixed; **0 mentions remain**.

⛔ **`CTO-46/4a`** (`CTO-45/3`) — `handoffs.__all__` had `OFFICE_HANDOFF` after
`SECTIONS`. Sorted; asserted.

⛔ **`CTO-46/4b`** (`CTO-45/5`) — `register.py` said *"round 33's alone was 833
lines"*. **Measured over the archive's own sections:** round 33's is **31**
lines, the largest is **`ROUND 35` at 1,151**, and ⚠️ **`833` was a real reading
from somewhere else** (CTO round 43's `117 files / 833 lines`). ⭐ **That is the
lesson worth keeping and the comment now carries it: a wrong citation that is a
REAL NUMBER survives a re-read**, which is why this needed measuring rather than
eyeballing.

⛔ **`CTO-46/5`** — the *Decisions* table dropped the 78 register lines while
standing under the word *sum*. ⭐ **Both fixed: the 78 are rowed, the table now
accounts for 8,546, and the word *sum* is withdrawn** — the claim is the four
equalities.

### ARCH/9 `[structural]` — where I think the PO's board practice should change

⛔ **This is the supervisory half, and it is three sentences.**

1. ⭐ **A round is a RECORD and is written to `BOARD-ARCHIVE.md` FIRST, then the
   board's cells are changed to match.** ⛔ **The board is the OUTPUT of a round,
   never its transcript.** ⚠️ **Rounds 25–35 wrote the transcript into the board
   and changed the cells afterwards, which is how eight rows went stale while the
   file grew by 6,500 lines.**
2. ⭐ **A correction REPLACES.** ⛔ **The board's own repeated defect —
   `~~struck~~` text left standing above its replacement — is not a style
   problem: a reader stops at the first sentence that answers their question.**
   ⚠️ **`BOARD_ROW_CEILING` now makes the struck-plus-replacement cell physically
   not fit, which is the enforcement the prose never had.**
3. ⛔ **Check 4 should be re-derived from `board_state`, not run by hand.** ⭐ **It
   re-stamps rows against a tree; three of its rules are now machine-checked, so
   the human part shrinks to the one thing a machine cannot do — *is this state
   still TRUE?*** ⚠️ **Not done here: check 4 is the PO's instrument and
   `ARCH/9.3` is a proposal, not a change.**

### ⛔ Where I think the user's request was wrong, and what I did instead

⭐ **Two of the three asks were right and are delivered as asked.** ⛔ **The
third — *"the summaries should be enough for everyone to know enough about the
other tasks"* — is the one I would restate.**

⚠️ **A SUMMARY of a row is a second copy of its argument and it will go stale;
this project has killed that class three times** (Ruling 150, Ruling 161, Ruling
136). ⭐ **What actually orients a reader is not a smaller version of the
argument — it is a complete INDEX: every row present, named distinctly enough to
recognise, with its owner, its state, and where the rest is.** ⛔ **The board was
not failing to summarise; it was failing to be complete** — ⚠️ **`PO-34/7`
measured seventeen minted ids that appeared in NO register table, and the reader
had no way to tell.** ⭐ **So the deliverable is completeness plus addresses, not
condensation, and the register carries all 79 ids for the first time.**

### ⭐ The contract was exercised before it was handed over

⛔ **`W70` merged while this branch was open, so it was CLOSED THROUGH THE
CONTRACT rather than by editing a cell:** its state cell was replaced, its body
moved under `### W70 — <naming>` in the archive, and `rows/W70.md` was deleted.
⭐ **One register cell, one move, one deletion; the check stayed green and the
bijection held at 50/50.** ⚠️ **The pointer count went 353 → 352 and the anchored
count 124 → 125, which is the move showing up in the instrument.**

## For dependents

- ⛔ **PO:** ⭐ **read `docs/conventions/board.md` before your next round.** The
  four things you do — mint, change a state, re-scope, close — each have one
  named destination, and the floor now fails if you skip one.
  ⛔ **`<!-- register -->` delimits the register; a `W`-shaped table outside it is
  not read as one.**
- ⛔ **PO:** `ARCH/1` needs a row before the next round edits `docs/tasks/rows/`.
- ⭐ **Everyone:** `BOARD.md` is 24 KB and complete. ⛔ **Read it whole; do not
  head/tail it.** Open `rows/<ID>.md` only for a row you are taking.
- ⚠️ **CTO:** three calls want a verdict — the wave checks moving into
  `docs/conventions/board.md` (decision 5), the two re-addressed archive links
  (`ARCH/4`), and `ARCH/1`'s tuple entry.
- ⭐ **`W78`:** ⛔ **this restructure breaks ZERO admissible line-number
  citations** (`ARCH/5`), and it does not change your population of 105.
- ⭐ **`W70`:** your population is unchanged (`ARCH/7`).
