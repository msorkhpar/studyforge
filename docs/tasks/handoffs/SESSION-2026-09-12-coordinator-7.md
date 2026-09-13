# SESSION 2026-09-12 — coordinator handoff, waves 18–20

**Kind:** session log

**Release tip:** `release/m0-foundations` @ `4cb39e8` when written. ⛔ **Floor and suite GREEN
after every merge of waves 18, 19 and 20, measured in the pinned image by the coordinator, and
never red between merges.**

⭐ **A successor reads [the coordinator-6 log](SESSION-2026-09-12-coordinator-6.md) for the role,
the absolute constraints, the merge discipline and the standing preamble — unchanged except as
below — then THIS FILE, then `docs/tasks/BOARD.md`, then the newest `PO-*` round record.**

## ⭐ WHAT CHANGED IN THE PROJECT

- ⭐ **M3 CLOSED at `1ede082`** (PO round 65) on `SF-42`: `studyforge narrate` puts clips on disk.
- ⭐ **M4 steps 4.1, 4.2 and 4.3 CLOSED** (PO rounds 67 and 69). Merged: `SF-38`, `W218`, `W211`,
  `SF-21`, `OPS-05`, `SF-19a`, `W224`, `SF-39`, `SF-19b`, `W105`, `W225`. **M4 stays open on
  step 4.4**, where `SK-03` is in flight.
- ⭐ **In flight at writing:** `SK-03` (build-and-serve skill), `W106` (marker-sweep reader),
  `W107` (anchor home). **Next free slot: `W230`** (order 0) — the multi-corpus serve instance is
  unreachable; its brief is composed.

## ⛔ NEW IN THE DISCIPLINE

1. ⭐ **THE IMAGE IS NAMED BY ITS INPUTS NOW (`W225`).** `docker/dev/check` prints
   `image studyforge/dev:inputs-<digest>`; quote that line with every reading, beside the
   `command -v studyforge` IMAGE_GUARD. ⚠️ A branch cut before `W225` still uses the old shared tag
   and races only other pre-`W225` branches. ⛔ **Never `docker compose down --remove-orphans`:**
   every checkout shares one compose project (`W225/5`).
2. ⛔ **RULING 139 FOR SCRATCH.** Offices collided in the shared session scratchpad (`OPS-05/6`);
   an office's harness and capture files live under its OWN worktree's `.scratch/`.
3. ⛔ **OFFICES STOP BEFORE THEIR OWN PINNED RUN FINISHES** — seen five times. Every brief now
   says: wait on `^SUITE_EXIT=` at the START of a line (one wait matched its own expectation text),
   and hand back only after the last run is read. ⭐ **If one stops anyway, send it one message.**
4. ⭐ **A slot that frees mid-wave is refilled at once**, by the dispatch bound: capability rows
   first; a `W` row only where no capability row can take it. The register confirms carriers by
   message when it is mid-round.
5. ⚠️ **Never put `&` inside a command already run in the background:** the chain detaches and no
   completion notice arrives — watch its capture file for `^WRAPPER_EXIT=` instead.

## ⚠️ OPEN, AND ONE IS THE USER'S

- ⛔ **USER QUESTION (`PO-68/2`, relayed):** the Java corpus (consumer 1) has no integration
  office. Three of its readings — serve it, build-and-serve it, run the non-destructive check on
  it — wait in `OPS-03` at M6; that repository has no `corpus.json` at its pin. Nothing before M6
  is blocked.
- `W226`: the narration record cannot locate every clip it wrote. `W223`: a model change requests
  nothing. `W221`: the whole suite at uid 0 still writes outside the checkout.

## ⛔ THE NEXT ACTION

Merge `SK-03`, `W106`, `W107` as each hands back — corroborate before, guarded floor + suite
(with the printed identity) after every merge. Put `W230` into the first freed slot. When
`SK-03` merges, the register closes step 4.4 and runs **M4's close** against its *Done when*.
