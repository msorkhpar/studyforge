# SESSION 2026-09-12 — coordinator handoff, waves 18–20

**Kind:** session log

**Release tip:** `release/m0-foundations` @ `171366c` when written. ⛔ **Floor and suite GREEN
after every merge of waves 18, 19 and 20 so far, measured in the pinned image by the
coordinator, and never red between merges.**

⭐ **A successor reads [the coordinator-6 log](SESSION-2026-09-12-coordinator-6.md) for the role,
the absolute constraints, the merge discipline and the standing preamble — unchanged except as
below — then THIS FILE, then `docs/tasks/BOARD.md`, then the newest `PO-*` round record.**

## ⭐ WHAT CHANGED IN THE PROJECT

- ⭐ **M3 CLOSED at `1ede082`** (PO round 65) on `SF-42`: `studyforge narrate` puts clips on disk.
  The end-to-end leg is a HOST reading — the pinned image has no network.
- ⭐ **M4 is OPEN.** Merged: `SF-38` (narrate → build plays clips or names the gap), `W218`
  (`narrate --prune`), `W211` (the image installs the package), `SF-21` (progress store), `OPS-05`
  (non-destructive check, partial: the Java corpus has no archive), `SF-19a` (serving API: content,
  assets, security).
- ⭐ **In flight at writing:** `W224` (the build copies clips into `--out`), `SF-39`
  (`studyforge serve`), `SF-19b` (state, discovery, addressing), PO round 67.

## ⛔ NEW IN THE DISCIPLINE

1. ⛔ **THE IMAGE GUARD.** `docker/dev/check` rebuilds ONE shared tag from whichever worktree runs
   it (`W211/2`, measured racing). Every pinned invocation starts with
   `command -v studyforge >/dev/null; echo "IMAGE_GUARD=$?"`. ⚠️ **It only tells a pre-`W211`
   image from a later one** — `W225` owns the real fix. ⛔ **When a row changes `docker/dev/`, hold
   every office off `check` from its merge until each has rebased onto it.**
2. ⛔ **PER-OFFICE SCRATCH DIRECTORIES.** Offices collided in the shared session scratchpad and
   one ran another's plant script (`OPS-05/6`). The preamble now requires `<scratchpad>/<office>/`,
   restores from per-file copies (never `git checkout --`), and a fresh bytecode cache per plant.
3. ⭐ **A slot that frees mid-wave is refilled at once**, by the dispatch bound: capability rows
   first, and a `W` row only where no capability row can take the slot.

## ⚠️ OPEN AND WORTH A SUCCESSOR'S FIRST LOOK

- ⛔ **`SK-03` was NOT dispatched against `PO-66/2`:** E11 places the wrapping skills at M7 as
  wrappers over entry points that already work, while its own section and the README say M4 step
  4.4. PO round 67 was asked to settle it.
- `W80`–`W83`: every Acceptance clause naming the Java corpus is unmeetable — measured, the corpus
  has no archive.

## ⛔ THE NEXT ACTION

Merge PO round 67 FIRST, then `W224`, `SF-39`, `SF-19b` as each hands back — corroborate before,
guarded floor + suite after every merge. Refill each freed slot from M4's dispatchable rows, else
the queue head (`W225` is order 0).
