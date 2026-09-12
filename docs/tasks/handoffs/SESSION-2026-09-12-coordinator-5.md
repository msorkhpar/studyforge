# SESSION 2026-09-12 — coordinator handoff, wave 12

**Kind:** session log

**Release tip:** `release/m0-foundations` @ `142b208`.

⛔ **THIS FILE CARRIES NO TRANSCRIBED FIGURES, BY DECISION.** The user ruled this
wave: **run every gate, stop copying its readings into prose.** A figure appears
below only where the figure IS the subject of the thing being reported.

| instrument | environment | reading |
|---|---|---|
| `python3 -m tools.quality` | pinned container | **GREEN**, `FLOOR_EXIT=0` |
| `python3 -m pytest -ra` | pinned container | **GREEN**, `SUITE_EXIT=0` |
| `corroborate` | HOST | **GREEN**, `CORROBORATE_EXIT=0`, `dispatched and unnamed: none` |
| `tools.workspace verify` | HOST | **RED**, `VERIFY_EXIT=1` — ISO pin only, held `pending` by decision |

## ⭐ FIVE MERGES, first-parent line (Ruling 327)

`98aa0ad` → `b80f2c5` → `430363b` → `a073985` → `f7c62ad` → `142b208`.

| # | branch | what it bought |
|---|---|---|
| 1 | `chore/po-round58` | four closes, M3 3.4 and 3.5 opened, the widened step rule |
| 2 | `feat/SF-17-narration-synthesis` | the narration record contract; both Ruling 351 spec cells filled |
| 3 | `fix/W34-rubric-checklist` | the verdict-gate control, VALIDATED by planting; all of `docs/conventions/` |
| 4 | `feat/SF-18-player-highlight-sync` | the player, the highlight sync, and `data-audio` on real pages |
| 5 | `chore/po-round58` (second) | the review-gate sentence removed; five routed items disposed |

⛔ **NO VERDICT ON ANY MERGE, FOR THE FIRST TIME.** Every row self-certified on
its own office's floor + suite GREEN at the ref that merges, and my release-tip
measurement after each. **The floor and the suite were the only gates and
neither went red between merges.**

## ⛔ THE ONE THING TO ACT ON FIRST: A CHECK THAT DISARMS ITSELF AT EVERY WAVE BOUNDARY

⭐ **Found by the cumulative measurement, and only because my written
expectation was REFUTED.** I predicted the closing tip would hold the skip count
SF-18 armed. It did not — one test moved from passing to skipped across a
**markdown-only** merge.

`tools/tests/quality/board/test_contradiction.py:59` skips when no board row
declares a started state. ⛔ **That is precisely the state a register leaves at
the end of every wave, once it has closed everything.** So the live
contradiction check is DISARMED at the exact moment the board is rewritten most
heavily, and re-arms only when the next wave dispatches.

⚠️ **This is the same class `W34` just proved dangerous** — dev3 planted a
collapsed verdict span and showed the gate goes SILENT rather than red, so the
collapse reads as coverage. ⭐ **The cure is the same: assert the population is
NON-EMPTY, or state in the skip why an empty board needs no check.** Not rowed
yet; it is the first thing the next register should hear.

## ⭐ WHAT THE OFFICES DID THAT IS WORTH COPYING

- **`W34` VALIDATED its control instead of running it.** Planted the collapse:
  `SPAN_EXIT` moved to 1 and caught it, **while the gate itself printed
  nothing**. Pass is now the moved exit code AND the silence, both — the first
  is what stops the second being vacuous (Rulings 124, 348).
- **It refused the boundary sha I handed it**, re-derived it, matched, then put
  the DERIVATION beside the pin so a future mismatch reads as **a finding, not a
  re-pin**. Better than what I asked for.
- **`SF-17` and `SF-18` declined the SAME half of the same acceptance,
  independently, in the same terms** — no clip file exists on disk anywhere, and
  ⭐ *"committing binary audio to make a check pass would be a fixture built to
  satisfy the check."* Two offices reaching one refusal separately is worth more
  than either reaching it alone.
- **`SF-18` armed the pre-registered skip UPWARD**, parsing each href back
  through `parse_clip_name` rather than comparing to a set of ids. ⛔ **A skip
  that arms into a weaker assertion than it promised was never worth
  registering.**
- **`SF-18` refused to emit `data-speech-id`** though a frozen record names it.
  ⭐ **An attribute no code reads is markup that cannot go red** — `W37` in
  reverse. It ASKED rather than assumed, which is why it cost one message.
- **The register FOLDED `SF-18/1` into `W183` rather than minting it**, over my
  routing: one `Owns` defect too narrow in GRANULARITY and one too narrow in
  COVERAGE are one argument, and two rows would split it in half (`W17`/`W19`'s
  shape).
- **The register refused to re-cut when I asked**, because a rebase would
  rewrite the history recording four board-size breaches in order — and measured
  the disjointness that made re-cutting unnecessary instead.

## ⛔ FINDINGS AGAINST ME, by id

- **`SF-18/7`** — my SURFACE said *"nothing else"* over a row whose shipped
  contracts FORCE four other files. ⛔ **Second time this wave I wrote a surface
  without checking what existing code obliges** (`PO-58/9` was the first, in the
  opposite direction). ⭐ **The fix is not longer file lists: name the CONTRACTS
  a row must satisfy and let the files follow.**
- **`SF-18/8`** — my brief said capability rows take a CTO verdict; my later
  message said self-certify. ⛔ **A developer hit the contradicting-instructions
  problem the user asked to be eliminated, inside my own brief.**
- **`PO-58/2`** — I published the direct-messaging rule without publishing the
  addresses, so no developer was reachable by name and a Scheduled cell could
  not discharge.
- **I relayed `PO-58/8` onward as an established defect of mine before checking
  it.** It is STRUCK: `graphify-out/` IS ignored, `.gitignore:2`, exit 0. The
  register's exit 1 came from a worktree that does not carry the directory.
  ⚠️ **I had already told the user.** Corrected to them and to both offices.
- **Two refuted expectations, both mine, both recorded because they were
  written down first**: I predicted `CORROBORATE_EXIT=0` where a merged-but-
  unclosed row correctly holds it at 1; and I predicted the closing skip count,
  which is how the self-disarming check above was found.

## ⛔ THE TRAP THAT FIRED THREE TIMES IN ONE WAVE

⭐ **A FILTER THAT RETURNS NOTHING IS NOT A MEASUREMENT. Read the region.**

1. Mine: a case-sensitive `grep` hid `corroborate`'s `UNNAMED` arm from me, and
   I reported the arm as silent when it had named two branches.
2. `SF-18/9`: dev2 grepped an exact phrase in **its own handoff**, got nothing
   because the line was FOLDED across two, and nearly committed a duplicate.
3. Mine again, at the last merge: I grepped `self-certified` and got nothing
   because the document writes **`SELF-CERTIFIED`**. Read the section; it was
   there.

⚠️ **All three were people checking a claim they were confident about.**

## ⛔ THE WALL: `PO-58/10` / `W185`

A register round's **mechanical** footprint now breaches `board-size` **every
time**. It was breached and repaired **four times in round 58 alone**, and the
board shipped **three bytes** under. Ruling 271 forbids raising the term, and
both obvious answers are already refused inside `W185`'s own file. ⛔ **The next
round that closes five rows does not fit.** This is a wall, not a nuisance, and
it is cheaper to design now than at the moment a round cannot ship.

## ⭐ THE NEXT ACTION — wave 13, and it is a USER DECISION, not my composition

⛔ **THE LIVE NARRATION RUN. The user approved it explicitly this session.**
Full plan in the coordinator scratchpad; the grounds:

- ⛔ **`narrate-service` has never generated a single byte of real audio.** Every
  one of its tests runs against `FakeEngine`. `README.md:160` claims a recorded
  real-engine measurement exists; **it is not in the repository.**
- ⭐ **It costs no download.** Both pinned engine images are already on the host
  at exactly the digests `compose.yaml` and `compose.gpu.yaml` pin, and
  `narrate-service:local` is already built.
- ⛔ **DO NOT TOUCH `kokoro-tts-nvidia`.** It belongs to the `codesignal`
  compose project and **the user is retiring it themselves**.
- ⭐ **`W187` is the wiring it needs and the register put it at the queue head.**
  ⛔ **JOIN ON THE SPEECH ID, NEVER THE POSITION** — the record is keyed by id
  and the renderer by position, and a positional implementation **must fail its
  second test**, because positional failure is SILENT with every file present
  and valid.
- ⭐ **Verify the BYTES, not the status code.** The suite already has an MPEG
  parser built from the specification; run the real output through it.
- ⚠️ **This buys the one leg two offices declined this wave**: page ↔ DISK.

⭐ **`W185` (the bound) and `W187` (the wiring) both jump the queue. Everything
else waits.**

## ⛔ STANDING CONDITIONS

- ⛔ **Nothing is pushed to any remote, ever.**
- ⛔ **`ONBOARDING.md` is the user's own untracked file: never moved, deleted,
  committed — and never git-ignored**, because ignoring it removes it from the
  personal-data sweep.
- ⛔ **Offices author under Ruling 296 placeholders.** This office is
  `coordinator <coordinator@example.invalid>`.
- ⛔ **There is no reviewing office and no verdict, for any row.** The floor and
  the suite are the gates. Every live document now says so.
- ⭐ **Waves run CONTINUOUSLY.** The next one is named above.
