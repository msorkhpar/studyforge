# SESSION-2026-09-11 (second) — coordinator handoff

**Kind:** session log

**Release tip:** `release/m0-foundations` @ `76d9d37` — **5574 passed, 15 skipped** with
`STUDYFORGE_VISUAL` **unset AND `=required`**, floor clean, `CORROBORATE_EXIT=1`
(see [Status](#status)), rulings index **311 from 49 records**, board **137 register rows /
78 live / 90 detail files**.

**Since `270296d`:** 4 first-parent commits, **all four merges**, 20 commits absorbed,
23 files, **+2,853 / −246**. **One wave**: PO round 48, CTO round 62, two developer branches.

⭐ **The previous session's handoff is [`SESSION-2026-09-11-coordinator.md`](SESSION-2026-09-11-coordinator.md)**
and everything in its *What bites* table still holds. ⛔ **This file does not restate it.**

---

## Status

```text
76d9d37670cd6ac9bcea2eea25bbe33bd37ede1b        ROLE = MAIN
python 3.14.7 | node v24.21.0 | ruff 0.16.6 | Chrome for Testing 153.0.8010.36 | shm 1.0G
PYTEST unset     exit 0   5574 passed, 15 skipped     12 skip GROUPS / 15 skips
PYTEST required  exit 0   5574 passed, 15 skipped     ⭐ THE PAIR IS THE POINT — see W128
FLOOR_EXIT=0     pointers 1231 in 382, 678 anchored, 0 unresolved
                 rulings index 311 from 49, tail 311
CORROBORATE_EXIT=1   ⛔ 2 of 2 rows REFUTED — `W134` `W128`, both absorbed by this wave
verdict gate     147 merges in scope; un-exempted grep prints ONLY `0183cd1`; exempted NOTHING
```

⛔ **THE REFUTATION IS STRUCTURAL AND RULING 305 GUARANTEES IT — it is not the register office
being late.** ⭐ **The register must merge FIRST so the developer branches are named, which
means the register is stale about those same branches from the instant they land.** ⚠️ **The
exit code is DISCLOSURE at a merge and a GATE only at the register branch's own tip** (Ruling
279) — ⭐ **and that gate read `0` at `git rev-parse chore/po-round48` = `9cf75af`.**
⛔ **The first act of the next register round clears it** (Ruling 231).

---

## What landed

**One wave, four branches, every one measured by the coordinator in the pinned container before
routing and again after merging, and the release tip re-measured after EVERY merge.**

| # | merged | verdict | the thing worth remembering |
|---|---|---|---|
| 1 | [`chore/po-round48`](PO-2026-09-11-round48.md) `110504b` | `(CTO: APPROVE)` | three closes, Ruling 306 run against **693** archive anchors rather than trusted |
| 2 | [`W134`](W134.md) `4a3642a` | `(CTO: APPROVE after changes)` | seven rulings landed against a rate of five; a figure typed into the document that forbids typed figures |
| 3 | [`W128`](W128.md) `aaa18a5` | `(CTO: APPROVE)` | the suite now reads **identically** with the demand variable unset and set |
| 4 | [`CTO round 62`](CTO-2026-09-11-round62.md) `76d9d37` | `(CTO: APPROVE x2, APPROVE after changes, this record APPROVED)` | Rulings **310** and **311**; an R7 hard fail the reviewer committed and rewrote |

⭐ **Rulings 310 and 311.** ⭐ **`docs/tasks/rulings-index.md` resolves every `(Ruling N)`;
regenerate with `python3 -m tools.quality.rulings`.** ⛔ **Do not read the CTO record chain —
it is over 3 MB. Read the index, then at most the ONE record a ruling points at.**

---

## Decisions

- ⛔ **MERGE ORDER, RULING 305, EXECUTED AND CONFIRMED WORKING:** no gate row existed this wave,
  so it was **register → developer branches → reviewer's record**. ⭐ **The pre-merge arm proved
  the order is load-bearing rather than tidy:** before the register merged, `corroborate`
  printed `dispatched and UNNAMED by any row: fix/W128-visual-env-verdicts
  fix/W134-conventions-reach` — **unnamed because the register that names them was the very
  next merge.** ⚠️ It cleared to `dispatched and unnamed: none` the moment the register landed.
- ⭐ **THE FOLD QUESTION WAS HANDED TO THE REGISTER OFFICE, NOT DECIDED BY THE COORDINATOR** —
  and it is now **Ruling 311**. ⛔ The coordinator asserted the fold applied to BOTH held rows;
  the office **measured** that `W128`'s population was empty and declined it (`PO-48/3`), and
  **converted** `W134`'s four on three stated grounds. ⭐ **Ratified on a measurement rather
  than on the arguments: `+76 / −0`, one hunk past the acceptance, no clause widened.**
- ⛔ **EVERY VERDICT STRING WAS CHECKED AGAINST THE RUBRIC'S OWN REGEX BEFORE THE FIRST MERGE,
  by the coordinator, not inherited from the reviewer's claim to have done it.** ⭐ **All four
  passed and the control still refused the enumerated counter-example**, so the instrument can
  both accept and refuse (Ruling 191).
- ⭐ **Office worktrees are RETIRED at wave end.** `git worktree list` now reads MAIN and
  `wt/po-int` only. ⛔ **Never assert that inventory — point the next agent at the command.**

---

## Surprises

1. ⛔ **THE REVIEWER COMMITTED AN R7 HARD FAIL, AND FOUND IT ITSELF.** Its round record carried
   a home-path shape; the shipped check read `FLOOR_EXIT=1`, 2 failed, on a clean tree. ⚠️ **It
   had reproduced the exact defect another office had already caught one round earlier — BY
   QUOTING IT.** ⭐ **Remedied as R7 requires: the commit was REWRITTEN, not patched.** ⛔ **The
   clause it earned: a finding that names a forbidden shape DESCRIBES it, never REPRODUCES it,
   or the routing chain becomes a transmission mechanism.**
2. ⛔ **A FALSE RED ON A CORRECT WAVE, CAUSED BY THE READER'S OWN PROBE FILE.** The reviewer's
   first four-way reading was `3 failed, exit 1` — **twenty minutes after it had measured that
   exact defect** (`W134/6`: `ruff check .` walks the DISK, so the floor's lint verdict depends
   on untracked state, and §2e's *"ONE dependency remains, enumerated rather than denied"* is
   therefore false). ⭐ **What caught it was a `git status --porcelain` line it had printed and
   ignored.**
3. ⭐ **AMENDING A HELD ROW WAS RIGHT, AND THE EVIDENCE IS ACCIDENTAL.** The register converted
   four rulings into `W134`'s row file *while a developer held it*; that developer, working
   from a snapshot taken **before** the amendment existed, landed **all four** of them anyway.
4. ⛔ **A FINDING GREW UNDER RE-MEASUREMENT INSTEAD OF SHRINKING.** `W134/5` was filed as a
   heading misplacement. Re-measured, the defect is that **a `RULED ROUND N` heading states its
   own clause count and NO INSTRUMENT READS IT** — `ROUND 52` said *four* over 16 children and
   `ROUND 61` *seven* over 13, so **two of three were already wrong before the branch existed**.
   ⭐ The developer's own words: *"I had declined a fix I never measured, which was the worse
   half of that finding."*
5. ⛔ **`git checkout -- <dir>` IS NOT A PLANT RESTORE** (`W128/3`). It restores to HEAD, and it
   silently discarded an uncommitted repair in a NEIGHBOURING file **while `porcelain` read
   clean**. ⚠️ **Ruling 287 already says the container cannot restore and fails silently; this
   is a SECOND silent-restore failure, on the HOST — which is where 287 sends everybody.**

---

## Findings

⚠️ **The coordinator's own, recorded so the next one does not repeat them.**

- **`SESSION-2026-09-11b/1`** `[structural]` — ⛔ **a brief carried a function name that does not
  exist, INHERITED FROM THE ROW FILE INSTEAD OF CHECKED AGAINST THE TREE.** Both the row and the
  brief named `reach._cited`. **Measured:** it existed at `84b717b` and `W133` replaced it with
  `reach._citations` (public `reach.cited_numbers`); `grep '_cited\b' tools/quality/reach.py`
  exits 1 at `270296d`. ⭐ **It cost the developer nothing because it measured instead of
  inheriting — which is the entire argument for the rule.** Charged as `W134/2`.
- **`SESSION-2026-09-11b/2`** `[structural]` — ⛔ **an assertion about another row's live state,
  which is the class the PREVIOUS session was charged with twice.** The brief asserted the fold
  question applied to `W128`; the office measured an EMPTY population — its row was last edited
  at `f7ae024` and CTO rounds 60 and 61 name it **zero** times. Charged as `PO-48/3`.
- **`SESSION-2026-09-11b/3`** `[local]` — ⛔ **`tail -40` on the first tip reading cut the sha
  and the pins off the coordinator's own invocation**, leaving a result with no subject. Re-taken
  with the whole output captured. ⚠️ **Same class as the previous session's `/5`, first command
  of the session.**
- **`SESSION-2026-09-11b/4`** `[local]` — ⛔ **`git merge -F -` does not read stdin.** The merge
  did not happen and the error was easy to miss. ⭐ **Caught only because HEAD was printed
  immediately afterwards** — a merge is confirmed by reading the ref, never by the absence of a
  complaint.
- **`SESSION-2026-09-11b/5`** `[local]` — ⛔ **`git log --merges --first-parent … | wc -l` counts
  LINES, not COMMITS: it read `78` where the answer is `4`.** ⭐ **Caught because the number was
  implausible against a denominator already known** (4 first-parent commits). ⚠️ **`rev-list
  --count` is the instrument that answers the question asked.**
- **`SESSION-2026-09-11b/6`** `[none]` — recorded negative: **the release tip was measured after
  every one of the four merges and was never red**; floor and suite green at `110504b`,
  `4a3642a`, `aaa18a5` and `76d9d37`.
- **`SESSION-2026-09-11b/7`** `[structural]` — ⛔ **OPEN, AND OWED TO THE USER: the four merge
  commits of this wave carry the USER'S REAL GIT IDENTITY in their author and committer fields,
  supplied by the machine's global git config.** ⭐ **MEASURED at `76d9d37`: every OFFICE commit
  obeyed Ruling 296 — `po`, `dev1`, `dev2`, `cto`, all `@example.invalid`, 16 of the 20 commits
  absorbed this session — and all four exceptions are the coordinator's own merges.** ⚠️ **It is
  PRE-EXISTING and not introduced here: 39 of the last 40 first-parent commits carry it, the
  single exception being the previous coordinator's handoff commit.** ⛔ **Ruling 296's own words
  are that *a UNIFORM history bought with a real git identity is an R7 violation*, so the defect
  is the merges and never the offices' placeholders.** ⚠️ **The remedy is NOT the coordinator's
  to choose: rewriting them changes four shas that later merge bodies, this file and the archive
  already quote as measurements, and the rubric's own enumerated exemption says in terms that
  *an audit trail that edits away its own defects is not one*.** ⭐ **Nothing is pushed to any
  remote, so the exposure is local.** ⛔ **ESCALATED AND RULED BY THE USER, 2026-09-11:
  *“as far as you don't push, it's fine to use them locally”*.** ⭐ **So the four merges STAND,
  no history is rewritten, and a local git identity in this repository is NOT a defect to be
  re-raised** — ⚠️ **the condition is the whole of it: NOTHING IS EVER PUSHED TO ANY REMOTE.**
  ⛔ **Ruling 296 is unchanged for OFFICES: an agent still authors under a placeholder, and this
  ruling narrows nothing about what may be written into a FILE.**

---

## For dependents

⭐ **Read this file, then [`../BOARD.md`](../BOARD.md), then nothing else until you have a
task.** ⛔ **Do not read `../BOARD-ARCHIVE.md` or the CTO chain.**

**The first four things, in order:**

1. ⛔ **Dispatch a register round (round 49).** Its first act is the In-flight re-take;
   `CORROBORATE_EXIT` must read `0` at **its own tip**. It owes closes for **`W134`** and
   **`W128`**, and it owes mints for what [CTO round 62](CTO-2026-09-11-round62.md) scheduled —
   ⭐ **read that ONE record's routing section, not the chain.** Known members: **`CTO-62/3`**
   (11 colliding anchor names in `BOARD-ARCHIVE.md`, invisible to the pointer floor **by
   construction** because `heading_slugs()` returns a **set**), **`W134/4`** (the reach notice's
   `unreached 0`), **`W134/5`** (heading clause counts), **`W128/3`** and **`W128/6`**.
2. ⭐ **The queue head is `W138` → `W139`**, both minted round 48 — `W138` is Ruling 298's class
   member where **the absent branch SUBSTITUTES rather than SKIPS, so no instrument here can
   report it**; `W139` is Ruling 304's row.
3. **Then:** `W78` → `W88` → `W120` → `W121` → `W103` → `W105`–`W109` → `W116`–`W118` →
   `W125` → `W135` → `W136`. ⚠️ **`W78`, `W88` and `W120` all write `../rows/` — one owner or
   three waves.** ⚠️ **`W135` and `W136` share `docs/conventions/` with each other.**
4. ⚠️ **R11 headroom, MEASURED at `76d9d37`:** `tools/quality/board/register.py` **399 of 400**,
   `tools/quality/reach.py` **385**, and now `tests/visual/test_host_environment.py` **567 of
   600**. ⛔ **Ruling 261 — a ceiling is not a budget** — but the register has already put
   `reach.py` on the standing split condition beside `register.py`.

**What bites, beyond the previous handoff's table:**

| ⛔ | ⭐ the form that works |
|---|---|
| `git merge -F -` silently does nothing | write the message to a file; confirm by reading HEAD |
| `git log … \| wc -l` counts lines | `git rev-list --count` answers the question asked |
| `git checkout -- <dir>` is not a restore | plant and restore per FILE on the host, `md5sum -c` (`W128/3`) |
| an untracked `.py` at the root turns the floor RED | read `git status --porcelain` BEFORE believing a red |
| quoting a forbidden shape to report it | describe the shape; never reproduce it (round 62's clause) |

⛔ **Owed to the user and still unresolved by design:** the four sibling repositories carry push
URLs and `studyforge` has none. **Ruling 215 says that is the user's call. Nothing was changed.**
