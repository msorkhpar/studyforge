# W40 — handoff

**Kind:** task handoff — W40

⛔ **THIS IS THE SECOND HANDOFF FOR `W40` AND IT REPLACES NOTHING.**
⭐ **The first is [`W40.md`](W40.md)** — *"task handoff — W40"*, measured at
`chore/W40-ceiling-population` @ `8c9ce6d` and again at the merge `ef148b2`. ⛔ **It
is a RECORD and is not edited, appended to, or corrected here** (Ruling 106): it
records the round-29 take of this row against a DIFFERENT population — `content.py`
and `test_gate_coverage.py` — and every figure in it stays true of the ref it names.
⚠️ **This document is a new take of the same row against the population that stands
at `bec9d5c`**, and the two are read together, not one over the other.

**Author identity:** every commit on this branch is authored
`dev3 <dev3@example.invalid>`, set with `git -c user.name=… -c user.email=… commit`
per invocation (Ruling 296). ⛔ **`git config user.name` was never run**: inside a
linked worktree it writes the SHARED common `.git/config` and turns the personal-data
gate on every worktree on the host (`W64/14`).

**Status:** done.

---

## ⛔ THE ROW, AND WHAT IT IS NOT

⭐ **`docs/tasks/rows/W40.md` — *NO MODULE IN THE TREE SITS AT ZERO HEADROOM against
R11*.** ⛔ **The row is not edited by this branch and must not be**: it is the
register's, and its round-27 re-framing (`CTO-32/8`) exists precisely to keep a
population OUT of it — *a population enumerated in a row is a second copy nothing
re-measures*. ⚠️ **So no module name from any reading below belongs in that file.**

---

## ⛔ THE DERIVATION, RUN AT PICK-UP IN RULING 119'S OWN FORM

⭐ **Ruling 119 fixes the instrument: two commands and the subtraction between them,
never a cell.** ⛔ **Both were run VERBATIM from the ruling's record — the fenced `A`
and `B` blocks under *`W40` GAINS RULING 119 — both commands and the subtraction,
written out* in `docs/tasks/BOARD-ARCHIVE.md`** — and neither was retyped from memory.

- **A** — every module with `lines >= ceiling`, over `config.python_files`.
- **B** — Ruling 113's standing deferral sweep: every module whose docstring carries a
  live `Size exception:`. ⭐ **A module under a live deferral belongs to the row named
  in it, so it leaves the population.**
- **The population is `A − B`.**

### The reading at the BASE — ROLE `wt/dev3`, ref `bec9d5c`, ENVIRONMENT: HOST

| | |
|---|---|
| modules scanned | **543** |
| **A** | **1** — `tools/quality/board/verdict.py`, `400/400`, headroom `0` |
| over the ceiling (headroom < 0) | **0** |
| **B ∩ A** | **∅** — `git show bec9d5c:tools/quality/board/verdict.py \| grep -c "Size exception:"` reads `0` |
| **A − B** | ⛔ **1. The row was FALSE at the base.** |

### The reading at MY REF — ROLE `wt/dev3`, ref `c2b1bbe`, ENVIRONMENT: pinned container

⭐ **Expectation written before the command ran: `A` empty, `A − B` = 0.** Whole
output redirected to a capture file with no filter between the instrument and the
file, then grepped.

```text
=== A — at or over the ceiling ===
=== A ends ===
=== B — Ruling 113's standing deferral sweep ===
=== B ends ===
DERIVE_EXIT=0
```

⛔ **`A = ∅`, `B = ∅`, `A − B = 0`. THE ROW HOLDS.** ⚠️ **The subtraction MOVED
between the two refs — 1 to 0 — so neither reading is vacuous, and `A − B = 0` is
not the trivial answer of an instrument that returns nothing.**

⚠️ **`A` is not the floor.** `check_sizes` fires only OVER the ceiling
(`if lines <= ceiling: continue`), so **the floor alone returns `∅` at BOTH refs** and
cannot see this row at all. That is Ruling 119's own third table row and it is why
this derivation is not replaced by `quality floor: clean`.

---

## What landed — ⛔ THE SEAM, NAMED BEFORE CUTTING

⭐ **`tools/quality/board/verdict.py` carries a standing SPLIT condition**
(`docs/tasks/BOARD.md`, *Standing decisions*; `W166`, PO round 55): *the next row
touching it splits it at a seam its taker NAMES before cutting*. ⛔ **At `400/400`
that condition was one line from being unsatisfiable by any row that touched the file
before splitting it.** ⭐ **It is PERFORMED by this branch.**

### The seam

> ⭐ **`verdict.py` ANSWERS; `cell.py` SAYS.** ⛔ **What git observes of the BRANCH
> decides — terminality, the count, the live checkout. What the ROW CLAIMS about it is
> printed and never decides.**

**New public surface:** `tools.quality.board.cell.compared(row, branches, branch,
count, graph) -> tuple[str, ...]`. It carries `PO-42/7`'s commits-ahead comparison and
`PO-50/12`'s as-of resolution, with their measurement history, moved whole.

**Unchanged public surface:** `verdict.py` still exports `Answer`, `Claim`, `Verdict`,
`tokens`, `designates`, `claim`, `verdict`. ⛔ **`corroborate.py` and `unclaimed.py`,
its only importers in the tree, are not edited.** The two moved functions were
private (`_cell`, `_as_of`) and had no caller outside the module.

**The seam has teeth, and they are structural rather than stylistic:** `cell.py`
imports **no** name from `verdict.py`, because anything there that could decide a row
would need the `Answer` enum and the import would be a cycle.

| module | before | after |
|---|---|---|
| `tools/quality/board/verdict.py` | `400/400`, headroom `0` | `335/400`, headroom `65` |
| `tools/quality/board/cell.py` | — | `133/400`, headroom `267` |
| `tools/tests/quality/board/test_verdict.py` | `532/600` | `378/600` |
| `tools/tests/quality/board/test_cell.py` | — | `224/600` |

⭐ **`verdict.py` leaves `approach.py`'s 60-line near band entirely**, so it is absent
from the notice's printed population rather than merely reclassified inside it.

### Tests, both directions (R12)

⭐ **The package's tests are split the way the package is.** Five tests moved whole;
two are new and each carries its own negative arm:

- `test_the_CELL_moves_the_NOTICE_and_never_the_ANSWER` — one branch, one git, six
  different commits-ahead cells → **one** `Answer` and **six different** notices.
  ⛔ **The second half is the negative arm and it is load-bearing: an invariant answer
  ALONE would also pass if `compared()` printed nothing at all**, which is exactly the
  `PO-42/7` defect (a comparison nobody can tell from no comparison).
- `test_the_cell_module_IMPORTS_NO_NAME_FROM_THE_VERDICT_AND_THE_VERDICT_IMPORTS_IT` —
  the acyclicity, read off the shipped source with `ast`. ⛔ **Its control is the other
  half: `verdict.py` MUST import `cell.py`, or the assertion would pass over two
  modules that simply do not know each other.**

---

## ⛔ EVERY READING, EACH WITH ITS REF, ROLE AND ENVIRONMENT

⚠️ **Four instruments, and they do not share one environment label** (Ruling 326).
⛔ **No reading below was filtered on its way to its capture file.**

| # | instrument | ref | ROLE | ENVIRONMENT | reading |
|---|---|---|---|---|---|
| 1 | Ruling 119 `A`, `B` | `bec9d5c` | `wt/dev3` | HOST `python3` | `A = 1`, `B ∩ A = ∅`, **`A − B = 1`** |
| 2 | `./docker/dev/check python3 -m tools.quality` | `c2b1bbe` | `wt/dev3` | pinned container | `quality floor: clean`, `FLOOR_EXIT=0` |
| 3 | `./docker/dev/check python3 -m pytest -ra` | `c2b1bbe` | `wt/dev3` | pinned container | **`5791 passed, 18 skipped`** in `92.42s`, `PYTEST_EXIT=0` |
| 4 | Ruling 119 `A`, `B` | `c2b1bbe` | `wt/dev3` | pinned container | `A = ∅`, `B = ∅`, **`A − B = 0`** |

**Reading 2, in full where it bears on this row.** ⭐ **Expectation written before the
command ran and met in every clause:**

```text
size approach:   headroom   1  growth     +0  399/400  tools/quality/board/register.py  near and static
size approach: 20 of 545 modules within 60 lines of their R11 ceiling — PROXIMITY ALONE FLAGS 20.
               Proximity × growth flags 0: 0 NEAR AND MOVING, 19 near and static,
               1 born in the window, 0 answered by a standing split condition.
lint: ruff 0.16.6 — `ruff check .` clean; `ruff format --check .` clean (953 file(s) already formatted).
      This run carries a real lint signal.
quality floor: clean
```

⚠️ **`tools/quality/board/verdict.py` is ABSENT from that population and was its first
line at the base.** ⛔ **The population's own scalar moved `21 → 20` while the
denominator moved `543 → 545`, and those are two different changes in one line: one
module left the band, two modules entered the tree.**

**Reading 3's expectation, written before the command ran:** the brief's base figure
is `5789 passed, 18 skipped` at `b1d6074`; this branch deletes `0` tests, moves `5`,
and adds `2`, so `5791 passed, 18 skipped`. ⭐ **Met exactly, skip count included.**

⚠️ **Other floor figures, unchanged and quoted so a reader can see they did not
move:** board `59006 of 59072` bytes; `350 rulings from 58 ruling records, tail 350`;
`handoff existence: 0 of 2`; `0 unresolved` document pointers.

⛔ **`document pointers: 1528 read in 457 markdown files` — `457` and NOT the main
checkout's `458`.** ⭐ **THE DENOMINATOR MOVES AND THE NUMERATOR DOES NOT**: the
difference is `ONBOARDING.md`, which exists in the main checkout and in no linked
worktree. ⚠️ **Neither figure is the tracked-document count, and a reader comparing
pointer counts across checkouts would wrongly conclude both are checkout-invariant.**

⚠️ **A FIFTH INSTRUMENT COULD NOT BE RUN, AND ITS ABSENCE IS A READING:** R14 asks the
knowledge graph before exploring, and this checkout has no graph — `graphify query`
answers `error: graph file not found`, and the floor's own line agrees:
`knowledge index: none — none in this checkout`. ⛔ **Reported, not worked around
silently**; the exploration below was done with `git grep` and cost accordingly.

⚠️ **THE LAST READING AT THE REF THAT WILL MERGE.** Readings 2–4 are at `c2b1bbe`,
which is the code. ⛔ **This document is a further commit, so the tip that merges is
NOT `c2b1bbe`** — all three instruments were re-run at the tip and those figures are
in the branch's report to the coordinator. ⚠️ **A document cannot quote a reading
taken at the ref that contains it — the regress does not terminate — so what it does
instead is SAY SO, rather than let a reader assume the tip was measured.** ⭐ **An
intermediate reading below is labelled as one; the merge-ref reading exists and is
reported, and the delta between the two refs is markdown only.**

⚠️ **Reading 2 was taken at `c2b1bbe` and re-taken at the handoff commit; the only
figures that moved are the two that COUNT MARKDOWN — the pointer census
(`1528 in 457` → `1529 in 458`) and, less obviously, the lint file count. That second
one is `W40/8`.**

---

## Decisions

1. ⛔ **A SPLIT and not a trim** (R11, Ruling 261). A ceiling is not a budget, and
   deleting docstring history to buy lines would have paid for the row with the
   record that makes the module readable.
2. ⭐ **The seam is the one the module already drew and the test file already
   marked.** `verdict.py`'s docstring said the cell comparison *"is a NOTICE, never a
   refutation"* and *"`PO-42/7` is UNTOUCHED: the notice SAYS more, the verdict
   ANSWERS the same"*; `test_verdict.py` already carried a banner comment at
   `Reading 5`. ⛔ **A seam that is invented at split time is a seam nobody else
   would draw again.**
3. ⭐ **`compared()` takes `(row, branches: int, …)` rather than the `Claim`.** The
   `Claim` lives in `verdict.py`, so importing it would be the cycle the seam exists
   to refuse — and the only thing the comparison ever asked of that object was *how
   many branches*.
4. ⛔ **No gate was added for zero headroom, deliberately.** See `W40/5`.

## Surprises

⭐ **The row's population and its remedy were both already decided in the tree and I
did not have to choose either.** The standing SPLIT condition names the file and
demands a named seam; Ruling 119 fixes the two commands. ⛔ **What the row needed was
somebody to RUN them at a fresh ref, which is exactly what `CTO-32/8`'s re-framing was
designed to force.**

---

## Findings

### W40/1 `[structural]` The brief's mechanism for `corroborate.py`'s live defect is REFUTED, and I inherited it into a commit message before the correction reached me

⛔ **The brief said the module's refuted line *"counts CELLS and labels them ROWS"*,
with three release-tip readings behind it.** ⚠️ **The coordinator self-corrected
mid-wave (`CTO-72/3`, filed by the reviewer). I verified the correction at source at
my own ref rather than inheriting it in turn:**

- `tools/quality/board/corroborate.py` carries the string
  `rows REFUTED by git ({len(refuted)}): {' '.join(refuted)}` — ⭐ **`len(refuted)` and
  `' '.join(refuted)` read the SAME list**, bound from `refuted_rows`, which appends
  `row.subject` once per row. **The scalar is a correct ROW count.**
- The extra backticked id comes from the board, not the instrument:
  `docs/tasks/BOARD.md` carries a row whose id cell is literally
  `` `NS-04` `NS-06` `` — one row, two ids, as Ruling 218 permits.

⛔ **So the scalar is right, the ids are right, and the exit code is right. The real
defect is Ruling 269's: THE DISPLAY NAMES NO UNIT**, so a reader counting backticked
ids gets one more than the count claims. **A labelling defect, not a population one.**

⚠️ **AND THE HALF THAT IS MINE.** Commit `c2b1bbe`'s message repeats the refuted
mechanism as though I had checked it — I had not; I restated the brief. ⛔ **The
commit message is NOT rewritten, because two container readings are pinned to that
ref and rewriting it would invalidate them to tidy a sentence.** ⭐ **It is corrected
here instead, which is the shape this project already uses for a landed record.**
⚠️ **The operative claim in that message is unaffected and remains true:
`corroborate.py` is untouched by this branch — the defect was NEITHER carried into a
new file NOR silently fixed.**

### W40/2 `[structural]` The brief stated a SURFACE for this row and the row declares none

⛔ **`docs/tasks/rows/W40.md` is four lines and names no surface**; the brief named
`tools/quality/board/` and its tests. ⚠️ **Also filed by the reviewer as `CTO-72/2`.**
⭐ **It cost nothing here — the derived population fell inside the stated surface
anyway — but it would have cost a row whose derivation landed OUTSIDE it, and that
taker would have had to choose between the brief and the instrument.** ⛔ **A row
whose population is DERIVED cannot have its surface asserted in advance; the two are
the same question asked twice, and only one of them is measured.**

### W40/3 `[local]` The brief's handoff path already existed, and the second-handoff form was needed

⛔ **`docs/tasks/handoffs/W40.md` exists — 32,138 bytes, `**Kind:** task handoff —
W40`, from the round-29 take.** ⭐ **The brief told me to check first, so this is not
a contradiction in it — recorded because the resolution matters to the next reader:**
Ruling 106 refuses the overwrite and appending would leave a freshly-wrong headline,
so this document takes a new stem beginning with the row id and points back at the
first. ⚠️ **The precedent in the tree is `W64-gate-two.md` and `W19-provenance-pin.md`.**

### W40/4 `[structural]` `verdict.py`'s standing SPLIT condition is now PERFORMED and its board cell is the register's to retire

⭐ **`docs/tasks/BOARD.md`'s *Standing decisions* table carries a row reading
*"Same form for `tools/quality/board/verdict.py`, a THIRD member inside
`tools/quality/board/` — the next row touching it splits it at a seam its taker NAMES
before cutting"*.** ⛔ **This branch is that row and the split is done, at the seam
named above.** ⚠️ **`BOARD.md` is not mine and is not edited — reported so the
register can retire the cell rather than leave a discharged condition standing.**

### W40/5 `[structural]` The row's property has NO instrument that names it, and the module that would carry one is not in this row's reach

⛔ **`tools/quality/approach.py` classified `verdict.py` at `400/400` as `near and
static` and did NOT flag it.** ⭐ **That is correct as written** — Ruling 261 (*a
ceiling is not a budget*) and `W155`'s predicate, proximity × GROWTH, where a static
module under an enforced ceiling is the ceiling WORKING. ⚠️ **But `zero headroom` is
not merely `near`: at headroom `0` the next line added anywhere in the file is a build
failure, so a standing SPLIT condition on that module cannot be discharged by any row
that touches it before cutting.** ⛔ **`W40` is therefore discharged by a derivation
run at pick-up and by nothing that runs on its own.**

⚠️ **`BOARD-ARCHIVE.md` already states this and deliberately did not mint a second
row for it** — *"it is stated here so that whoever takes `W40` reads it"*. ⭐ **I
read it, and I did not build the gate**: `approach.py` sits outside
`tools/quality/board/`, and a hard gate below R11's own ceiling is the exact thing
that module's docstring forbids. ⛔ **Recorded, not fixed. If the register wants the
property instrumented, the notice can name the zero-headroom case WITHOUT becoming a
finding — that is a row, and it is not this one.**

### W40/6 `[local]` `register.py` at `399/400` is the nearest survivor, is NOT in this row's population, and carries its own standing condition

⛔ **Headroom ONE is `near`, not zero, so it is outside `A − B` at every ref above and
this branch does not touch it.** ⭐ **`docs/tasks/BOARD.md`'s *Standing decisions*
carries the same form for it — *the next row touching it splits it*.** ⚠️ **Named here
only so it is not mistaken for part of this row's subject: the brief mentioned it
beside the `400/400` reading, which invited exactly that conflation, and the
coordinator withdrew the invitation mid-wave.** ⛔ **It is one module and one row, and
`W40` was never about two.**

### W40/7 `[local]` R14's knowledge graph is absent from every linked worktree, so R14's context budgets do not apply here

⛔ **`graphify query` answers `error: graph file not found` — there is no
`graphify-out/` in this checkout — and the floor agrees: `knowledge index: none`.**
⭐ **Not a defect of anybody's and not a build failure** (the floor says so
explicitly). ⚠️ **Reported because a brief that budgets context on the assumption
that `graphify query` answers in a few thousand tokens is budgeting against an
instrument this checkout does not have**, and the substitute is `git grep` over
`BOARD-ARCHIVE.md`, which is 18,000+ lines.

### W40/8 `[local]` The floor's lint line counts MARKDOWN, so a markdown-only commit moves a figure a reader will read as Python

⛔ **MEASURED, ROLE `wt/dev3`, pinned container, `ruff 0.16.6`: the floor printed
`953 file(s) already formatted` at `c2b1bbe` and `954` one commit later, and the whole
of that commit is ONE added markdown document.** ⭐ **Confirmed directly rather than
inferred — `ruff format --check` on this handoff alone answers `1 file already
formatted`, so `ruff format --check .` discovers `.md` and counts it.**

⚠️ **The line is not wrong: it says `file(s)`, not modules.** ⛔ **But every other
count on the floor that a reader compares across refs is a Python population, and an
office reading `953 → 954` beside a diff of one markdown file would look for a Python
module that is not there.** ⭐ **Recorded so the next reader spends a sentence on it
rather than a measurement, and because it is the same shape as the pointer count
above: THE POPULATION IS NOT THE ONE THE NEIGHBOURING FIGURES ARE OVER.**

---

## For dependents

- ⭐ **Import `compared` from `tools.quality.board.cell` if you need the
  commits-ahead comparison.** ⛔ **Do not add anything to `cell.py` that returns or
  constructs an `Answer`** — the acyclicity test fails, by design, and the failure is
  the seam telling you the code belongs in `verdict.py`.
- ⭐ **`verdict.py`'s public surface is unchanged**, so nothing that imported it needs
  editing.
- ⚠️ **`tools/quality/board/register.py` is now the closest module to an R11 ceiling
  in the whole tree** (`399/400`). A row that touches it splits it — see `W40/6`.

## What I did not do

⛔ **I merged nothing, and I added, set or queried no remote.** ⛔ **I touched no other
office's worktree and cut none.** ⭐ **The only containers I created are
`docker/dev/check`'s own `run --rm` containers, which removed themselves; `docker ps
-a` shows none of mine, and the three of the user's that have been up for days were
not stopped, restarted or reconfigured.** ⚠️ **`ONBOARDING.md` was not moved, deleted,
committed or git-ignored — it is absent from this linked worktree, and git-ignoring it
would remove it from exactly the population the personal-data sweep reads.**
⛔ **I did not edit `docs/tasks/rows/W40.md`, and no module name from any reading above
was written into it.** ⛔ **I did not edit `docs/tasks/BOARD.md`, `BOARD-ARCHIVE.md`,
`docs/tasks/handoffs/W40.md`, `tools/quality/board/corroborate.py`,
`tools/quality/board/register.py` or `tools/quality/approach.py`.** ⭐ **I closed no
milestone step.**
