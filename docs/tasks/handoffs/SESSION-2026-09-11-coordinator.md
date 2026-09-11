# SESSION-2026-09-11 — coordinator handoff

**Kind:** session log

**Release tip:** `release/m0-foundations` @ `0fe5df6` — **5561 passed, 15 skipped**, floor
clean, `CORROBORATE_EXIT=1` (see [Status](#status)), rulings index **309 from 48 records**,
board **135 rows / 79 live / 88 detail files**.

**Since `798956c`:** 217 commits, **52 merges**, 271 files, **+58,271 / −1,073**.
CTO rounds **48–61**, PO rounds **37–47**, **17** developer branches merged.

---

## Status

⛔ **THE REGISTER IS STALE AT THE TIP AND THAT IS THE NORMAL POST-WAVE STATE, NOT A DEFECT.**

```text
0fe5df62378f23b3a03d7867cc1f67a96e4222ef        ROLE = MAIN
python 3.14.7 | node v24.21.0 | ruff 0.16.6 | Chrome for Testing 153.0.8010.36 | shm 1.0G
PYTEST_EXIT=0        5561 passed, 15 skipped      12 skip GROUPS / 15 skips
FLOOR_EXIT=0         pointers 1132 in 375, 641 anchored, 0 unresolved | ruff 855
                     45577 bytes of 49440 (14336 frame + 224×136 + 160×2 + 480×9)
                     rulings index 309 from 48, tail 309
CORROBORATE_EXIT=1   ⛔ 2 of 2 rows REFUTED — both branches the last wave absorbed
```

⭐ **The first act of the next register round is the In-flight re-take** (Ruling 231), and
`CORROBORATE_EXIT` must read `0` at that round's own tip — **the register's tip, never the
release tip after the wave's last merge** (Ruling 279, and the gate POINT is the whole of it).

⚠️ **`../../../docs/tasks/BOARD.md` is the instrument for everything that moves.** Only
`wt/po-int` stands; every other worktree is retired.

---

## What landed

**Six waves, every branch measured by the coordinator in the pinned container before routing
and again after merging.** The three-office shape that worked every time: **one register
round, two developers on disjoint surfaces, one reviewer** — the reviewer taking branches as
they land rather than waiting for the wave.

| wave | merged | the thing worth remembering |
|---|---|---|
| 1 | [`W98`](W98.md), PO 43, [CTO 56](CTO-2026-09-10-round56.md) | a recorded px figure REFUSED in favour of an equality invariant under any font |
| 2 | [`W119`+`W100`](W119.md), [CTO 57](CTO-2026-09-10-round57.md) | a committed test that read the machine's worktree set stopped doing so |
| 3 | [`W124`/`W122`/`W123`](W124.md), PO 44, [CTO 58](CTO-2026-09-11-round58.md) | the font pinned by version + 12 digests; an untrue count DELETED, not corrected |
| 4 | [`W129`/`W130`/`W132`](W129.md), [`W131`](W131.md), PO 45–46, [CTO 59](CTO-2026-09-11-round59.md)/[60](CTO-2026-09-11-round60.md) | the board bound now PRINTS ITS OWN DERIVATION and re-derives its shipped constant |
| 5 | [`W126`](W126.md), [`W115`](W115.md) | §8a's pass condition made satisfiable for the first time since round 54 |
| 6 | [`W137`](W137.md), [`W127`](W127.md), [`W133`](W133.md), PO 47, [CTO 61](CTO-2026-09-11-round61.md) | nine closes performed; a register shipped RED on purpose and its gate merged first |

⭐ **Rulings 241 → 309.** ⭐ **`docs/tasks/rulings-index.md` resolves every `(Ruling N)`;
regenerate with `python3 -m tools.quality.rulings`.** ⛔ **Do not read the CTO record chain —
it is over 3 MB.**

---

## Decisions

- ⛔ **MERGE ORDER IS RULED, NOT PREFERRED** — Ruling 305, amending 279: **the gate row first
  when one exists, then the register, then the developer branches, then the reviewer's
  record.** ⭐ Ground: *a release tip is the base every office reads its own branch against,
  so a red tip for even minutes means any base reading taken in that window inherits a
  failure its taker cannot separate from their own.*
- ⭐ **Ruling 264(a): `corroborate` is RUN at every merge and its exit code AND refuted list
  go into the merge body verbatim.** Ruling 264(c): the pre-merge arm is the printed line
  `dispatched and UNNAMED by any row`, **not** the exit code — and **Ruling 265** exempts the
  office-branch namespace from it.
- ⭐ **Ruling 296: offices author commits under a placeholder identity** (`po@example.invalid`
  and so on). ⛔ **Never amend to a real one — that writes the user's identity into a commit.**
  ⚠️ An office refused to author as another office's placeholder because *a placeholder naming
  another live office is a false attribution*; that refusal was ratified and is stronger than
  the ruling.
- ⭐ **Ruling 255: `-ra`, never bare `-q`, never `-rs` alone** — a reading that can fail must
  be able to NAME its failure. ⭐ **Ruling 275: a skip figure carries BOTH units** (today
  `grep -c '^SKIPPED'` reads 12 and pytest reads 15).
- ⭐ **Ruling 290: discharge 238(d) by PINS.** Five distinct image ids were measured under one
  unchanged tag in a single session.
- ⭐ **Ruling 287: the container CANNOT restore and the failure is SILENT.** Restore on the
  host, verify with `md5sum -c`, read `git status --porcelain` after every plant.

---

## Surprises

1. ⛔ **A register was shipped RED ON PURPOSE and it was the right call.** Nine closes under
   the stub protocol made two committed tests fail; the office measured three candidate states
   and **none was both true and green**, chose the honest one, minted the gate, and put the
   verdict to the reviewer. [`PO-2026-09-11-round47.md`](PO-2026-09-11-round47.md).
2. ⛔ **A protocol shipped with an EMPTY population passed six plants and still broke on first
   live use.** [`W129`](W129.md)'s own handoff said the population would stay empty until a
   close was performed; [`W137`](W137.md) is what that first use cost.
3. ⛔ **The reach notice reads `unreached 0` and that zero is an ARTIFACT.** The window is 25
   wide and slides; seven genuinely unreached rulings (`266, 267, 268, 269, 273, 274, 275`)
   live only in [CTO round 61's record](CTO-2026-09-11-round61.md). ⭐ **The reviewer found it
   against their own mint, the register office found the class independently, and an earlier
   round's own sentence is a third instance.** ⚠️ **Routed to `W134`. Do not quote that zero.**
4. ⛔ **A third re-derivation of one rule exists and the skip census CANNOT SEE IT** — it
   substitutes a *synthetic* shape rather than skipping, so a named property was being proved
   of a 48×5 grid while the real corpus sat beside the tree. [`W127`](W127.md).
5. ⭐ **The archive-pointer ratchet finally has a mechanism:** a close under the stub protocol
   CREATES new frozen archive pointers at other row files, which is why the control reading
   went 2 → 5 → 26 across three rounds.

---

## Findings

⚠️ **These are the coordinator's own, recorded so the next one does not repeat them. Every one
was caught by an office that measured instead of inheriting.**

- **`SESSION-2026-09-11/1`** `[structural]` — **an invented REQUIREMENT is worse than a wrong
  number, because a wrong number gets refuted and a wrong requirement gets SATISFIED.** A
  brief demanded *"the refuted list printed even when empty"*; that output did not exist, an
  office wrote a plausible line to satisfy it, and a full review reproduced every figure
  around it. **Measured:** the invented string was absent from `tools/`, `src/` and `tests/`
  over 400 commits. Three of the ten defects below are this shape.
- **`SESSION-2026-09-11/2`** `[structural]` — **a brief must never assert a live inventory of
  worktrees or offices; it POINTS AT `git worktree list` and `corroborate`.** A snapshot
  cannot be kept true — the defect `../../../CLAUDE.md` was rewritten over. **Measured:**
  charged twice, and the second time the same brief stated the remedy and violated it.
- **`SESSION-2026-09-11/3`** `[structural]` — **relay a finding BY ID, never by description.**
  The finding one round turned on reached the reviewer only because they read it off a handoff
  in the merge tree. **Measured:** its content was relayed prominently, its id never attached.
- **`SESSION-2026-09-11/4`** `[local]` — **a derived figure loses to a measured one.** Three
  predictions were wrong this session; every time the office's measurement was right.
  **Measured:** a delta inherited from a summary table that straddled a release move.
- **`SESSION-2026-09-11/5`** `[local]` — **an instrument's reach is checked before its
  reading is quoted.** `find /opt -name headless-shell` reads ABSENT for a binary that is
  present; `-rs` catches a failure it cannot name; a nested-quote probe printed BLANK pins,
  which is worse than absent because blank reads as measured-and-empty. **Measured:** three
  separate instruments of the coordinator's, three separate rounds.
- **`SESSION-2026-09-11/6`** `[none]` — recorded negative: **every verdict string of the last
  three waves was checked against the rubric's own regex BEFORE the first merge**, and none
  was rejected. **Measured:** the gate's own `grep -v` selected nothing, five strings.

---

## For dependents

⭐ **Read this file, then [`../BOARD.md`](../BOARD.md), then nothing else until you have a
task.** ⛔ **Do not read `../BOARD-ARCHIVE.md` or the CTO chain.**

**The first four things, in order:**

1. ⛔ **Dispatch a register round.** Its first act is the In-flight re-take; `CORROBORATE_EXIT`
   must read `0` at its own tip. It also owes a row for [`W127/1`](W127.md)'s third
   re-derivation, which CTO round 61 routed as a row rather than a merge obligation.
2. ⭐ **`W134` is the head of the queue and it is the one with a clock on it** — its population
   is scrolling out of the reach notice's 25-wide window at roughly nine rulings per wave, and
   surprise 3 above is that loss happening.
3. **Then:** `W128` → `W78` → `W88` → `W120` → `W121` → `W103` → `W105`–`W109` →
   `W116`–`W118` → `W125` → `W135` → `W136`. ⚠️ `W78`, `W88` and `W120` all write
   `../rows/` — **one owner or three waves.**
4. ⚠️ **Two files are near R11's ceiling:** `tools/quality/board/register.py` at **399 of
   400** and `tools/quality/reach.py` at **385**. ⛔ Ruling 261 — a ceiling is not a budget —
   but 399 is one line from a build failure for whoever next opens that package.

**What bites, and all of it is measured:**

| ⛔ | ⭐ the form that works |
|---|---|
| `docker/dev/check` derives its root from where the **script** sits | run the copy inside the checkout you mean to measure |
| the image **tag** and the image **id** are both disqualified | name the PINS, in the same invocation as the sha (238/290) |
| `$?` after a pipeline reads the pipeline's last command | `set -o pipefail`, or redirect and read `$?` with nothing between (241) |
| MAIN reads one higher on **two** denominators | name the checkout by its ROLE; the pointer TOTAL is identical (147) |
| the container cannot restore, and it fails **silently** | plant and restore on the HOST, verify with `md5sum -c` (287) |
| a ruling that only its own record remembers | a convention document carries it, and the minter owns that edit (245/286) |

⛔ **Owed to the user, and unresolved by design:** the four sibling repositories carry push
URLs and `studyforge` has none. **Ruling 215 says that is the user's call and not this
repository's to enforce. Nothing was changed.**
