# Board — live status

**Single source of truth for what is in progress and what is done.** Owned by
the framework Product Owner. Task *definitions* live in the epic documents
(`E00`…`E13`); this file carries only **state**.

## ✅ **M0 CLOSED. M1 CLOSED at `2fe56a4`. M2 STEP 2.1 CLOSED 2026-09-10 at `a00337b`. M2 STEP 2.2 IS OPEN.**

⭐ **M1's close ref is `2fe56a4`** — all nine close conditions true at that one
ref, rows 1–8 **re-taken there** rather than inherited, row 9 taken there by the
coordinator: **3090 passed, 63 skipped, all 63 named; quality floor clean; lint
`ruff 0.16.6` `check` exit 0 and `format --check` exit 0.** ⛔ **The row-by-row
re-take, and why the close ref is `2fe56a4` and NOT `a03aeef`, are
[in the close run below](#m1s-close-run-at-2fe56a4-all-nine-true-at-one-ref-and-rows-18-were-re-taken-not-inherited).**

✅ **M2 STEP 2.1 IS CLOSED. The close ref is `a00337b`, and every one of its five
rows was RE-TAKEN there.** ⛔ **Ruling 97: a close is a set of measurements at ONE
named ref and no row is inherited across a ref change** — ⚠️ **and this close
proves the rule twice over: the round opened against `253cdd3`, the five rows were
taken there, the tip then moved to `1aa6319` and `a00337b`, and ALL FIVE WERE
TAKEN AGAIN.** ⭐ **[The close run, row by row](#m2-step-21s-close-run-at-a00337b-all-five-re-taken-and-the-ref-moved-twice-underneath-it).**

⏳ **OPEN: M2 step 2.2 — `SK-07` ✅, `SF-13` ✅, `SK-05` ✅, `SK-08` ⏳ — ONE ROW
LEFT, and it is in flight.** ⭐ **`SK-05` merged `83f767e` (CTO round 38,
APPROVE); when `SK-08` lands the step CLOSES and Ruling 97's five-row re-take at
one named ref is owed.** ⛔ **Step 2.3 does NOT open on that close alone: `W57`
lands BEFORE step 2.3 opens (`PO-30/5`), and `W57` is in flight too.**
⛔ **Membership is `README.md`'s, state is this file's, and neither copies the
other.** ⭐ **`SK-08`'s in-step edge is DISCHARGED: it *Depends on* `SK-07`, which
merged `2e42c5b`** — ⚠️ **so the step's declared parallelism is true for the
first time, and it became true by the dependency landing rather than by
renumbering the plan into a 2.3.** ⭐ **[the ordering inside 2.2 is
below](#m2-step-22-open-and-its-declared-parallelism-is-false-by-its-own-dependency-graph).**

⏳ **IN FLIGHT at `e309172`, and MEASURED not received:** ⭐ **`W57` on
`fix/W57-safe-schemes` (`wt/dev1k`, **1 authored commit** `b14e04e` + a forward
merge, head `cfea623`) and `SK-08` on `feat/SK-08-delivery` (`wt/dev2n`,
**1 commit**, head `ebf6a65`)** — ⛔ **`W57` was cut at `83f767e` and the release
tip is `e309172`, so it merges forward past `8c8a434` and the round-38 record
before its trial merge means anything.**

⚠️ **~~IN FLIGHT at `8146bdb`: `SK-05` (`wt/dev2m`, 4 commits) and `W40`
(`wt/dev3c`, 4 commits)~~** — ✅ **BOTH MERGED, both APPROVED at CTO round 38:
`W40` → `fd3c0a4`, `SK-05` → `83f767e`.** ⛔ **REPLACED above, not appended
beneath; `PO-29/6` is why.** —
⛔ **INSTRUMENT: `git worktree list` plus `git log --oneline
release/m0-foundations..<branch>`, run in this worktree.** ⛔ **NOT `git branch
--no-merged`, which Ruling 130 says enumerates unmerged COMMITS: it was blind to
`chore/W40-ceiling-population` for a whole round while that row had none.**
⚠️ **`CTO-37/3` measured `W40` at ZERO commits at `ddddd05` and called it
*dispatched, nothing authored*; at `8146bdb` it has four and has already turned
both zero-headroom modules into packages** — ⭐ **`PO-30/2`, and the honest
sentence is that a commit count is a reading with an as-of, not a state.**

⚠️ **~~IN FLIGHT at `ddddd05`: `SF-13` and `SK-07`~~** — ✅ **BOTH DONE.**
⭐ **`SF-13` merged `abe7d1c`; `SK-07` merged `2e42c5b`; both APPROVED by the CTO
at round 37.**

✅ **THE R11 BREACH IS GONE. `W44` MERGED `7b5c0a9` while this round was being
written, and the tree now holds ZERO `Size exception:` deferrals.** ⛔ **Measured
at `7b5c0a9`, `wt/po28`, with Ruling 113's `ast` sweep and NOT with `grep`:
**0**.** ⭐ **Ruling 121's replacement instrument returns its PASS reading for the
first time — `git grep -l 'Size exception:' -- src/ \| wc -l` → **0** — where the
clause it replaced would have printed nothing and exited **1**.** ⚠️ **`W45`
(`1aa6319`) landed first, so its fix was proved against the live deferral before
`W44` deleted it, which is the whole reason for that merge order.**

⭐ **NEXT TWO DEVELOPER ROWS (round 31): `W61` then `W59`** — ⛔ **`W57` and
`SK-08` are IN FLIGHT, so round 30's pair is SPENT; and step 2.2 has NO free
product row while step 2.3 is shut behind `W57`, so BOTH slots go to the
queue.** ⛔ **`W61` IS FIRST AND IT IS A SEQUENCING DECISION, measured:** ⚠️ **two
shipped `SKILL.md` files tell an agent to run `studyforge validate`, in a FENCE,
and the console script does not exist — and `SK-08` is authoring a THIRD skill
package right now.** ⭐ **`SK-05` shipped the instrument that refuses this shape;
its population is one directory too narrow, so widening it AFTER `SK-08` lands
lets a third fence ship and pass its own acceptance doing it.** ⭐ **`W59` is
Ruling 135 — `_escape` MOVES out of `content/`, on code that merged three
commits ago.** ⚠️ **`Owns` verified against the TREE at `e309172` and
`PO-26/1`'s R11 pre-dispatch sum run there — and derivation A came back ZERO for
the first time** — ⭐ **[the placement, with its commands](#round-31-the-next-two-rows-owns-in-ruling-136s-form-verified-at-e309172-and-a-pre-dispatch-sum-that-reads-zero).**

⚠️ **~~NEXT TWO DEVELOPER ROWS (round 30): `W57` then `SK-08`~~** — ⛔ **SPENT,
and kept because it is the placement that WORKED: both rows were taken and both
are authoring.**

✅ **`W40`'s LAST GATE IS STRUCK.** ⛔ **Ruling 125's *gated before `W40`* is
STRUCK by Ruling 127 — `CTO-36/3`, the CTO's own error, caught by applying their
own Ruling 126 to the section one screen above where they minted it.** ⭐ **And
the strike costs this board nothing to apply, which is itself the reading:
`git grep -n 'gated BEFORE\|gated before' -- docs/` at `ddddd05` returns **4**
lines and ALL FOUR are inside `docs/tasks/handoffs/`** — ⛔ **so the gate never
reached this board, and it blocked `W40` only in the CTO's own record.
`PO-29/2`.**

⛔ **FOUR ROWS MINTED ROUND 28 — `W50`, `W51`, `W52`, `W53`.** ⭐ **Every one is a
CTO ruling or a `W45` finding that had reached NO artifact: check 3 came back
**1 of 6** at open.** ⚠️ **Ruling 117 is the standard they are minted under —
guidance with no row is a failing carrier, and the PO is the only minter.**

## ⛔ THE HEADLINE (round 25) — **check 3 came back 10 of 10. Check 4 found EIGHT stale rows, and FIVE of them nobody had named.**

⛔ **The two instruments swapped places in one round, and that is the finding.**
⭐ **Check 3, rulings 99–108: every one reached an artifact, and every one landed
in the RULER'S OWN COMMIT** — `2db881d` (99–104), `c61cae3` (105–107), `19c0447`
(108), each verified by `git log -L` on the landing line rather than by reading
the handoff that claims it. ⛔ **Nine of sixteen last round; ten of ten this
round.**

⛔ **Check 4 is the one that went the other way.** ⚠️ **The CTO named THREE stale
board rows by line in `CTO-2026-09-10-round30.md`.** ⭐ **Re-measuring every row
whose trigger has passed, from the tree, found FIVE MORE — and ~~all five are
one ruling~~ ⛔ **CORRECTED, CTO round 31 @ `e01b360`: FOUR of the five are one
ruling**, Ruling 102, which landed in `E01` two rounds ago and never reached the
board. ⚠️ **The fifth — row 8, the step-2.1 assignment — is stale because `SF-31`
and `SF-04` MERGED, which is not Ruling 102.** ⭐ **The check-4 table below says
*"Rows 4–7 are ONE ruling"* and `PO-25/1` says *"FOUR places"*; only this
headline said five.** ⛔ **`SF-36`'s `Owns` cell still sent a developer to
`corpus/manifest/`, where `origin` does not appear** — verified by the CTO,
`0` occurrences at `ce58a36`.

⭐ **The two readings are the same fact seen from both ends, and it refines
`PO-24/1` rather than confirming it.** ⛔ **`PO-24/1` said *a ruling lands by
itself exactly when its artifact is the ruler's own file.* ⚠️ That is REFUTED as
stated:** rulings 99, 102 and 104 landed in `E01`, `E09` and `E04` **between
them** — **epic documents the PO owns** — and they landed anyway, in the ruler's
own commit. ⛔ **CORRECTED, CTO round 31 @ `e01b360`: read as a per-ruling
mapping that sentence is FALSE** — ⚠️ **Ruling 102 has ZERO occurrences in
`E09`; it is `E01`-only, and Ruling 99 is the one that reached `E09`.** ⭐ **The
check-3 table below has it right (`| 99 | E01's SF-31 section AND E09 |`), and
the refutation stands either way.**
⭐ **The variable is not whose FILE it is. It is whether the ruler wrote the
clause or handed it over** — which is what `PO-24/1`'s own control (Ruling 95)
already showed and its headline sentence then narrowed too far.
⛔ **And the residue is exactly what check 4 caught: Ruling 102 landed in ONE
artifact and the SECOND artifact carrying the same fact — this board — was never
re-measured.** ⭐ **The register section above says how that behaves in its own
words: *"two of its five rows were stale simultaneously, both in the same
direction, which is precisely how a duplicated status behaves."***

⛔ **The rule that follows, and it is Ruling 97's shape one level up: a ruling
that names *"a framework task"* and no id has not reached an artifact — it has
described one.** ⚠️ **The id space has exactly one minter, so a ruling can only
ever *ask* for a row; ⭐ if nobody mints it in the same wave, the ruling is
carried by whoever happens to re-read a handoff.**

⚠️ **This board twice mis-stated `SF-10`'s state in one round — first as
*"unblocked, waiting on nothing"* while it sat built on a branch, then as
`in-review` after it had merged.** ⛔ **Both errors are one cause: a status
measured once and quoted later.**

📏 **BASE (round 31): 3814 passed / 63 skipped in the pinned container at
`e309172`**, the release tip, **exit 0**; `quality floor: clean`, exit **0**.
⛔ **RE-DERIVED BY ME in the LINKED WORKTREE `wt/po31`, not received.** ⚠️ **A
HOST run of the same suite at the same ref reads `3864 passed, 13 skipped`** —
⛔ **50 more passes and 50 fewer skips, because the host has a browser and the
pinned image does not.** ⭐ **Ruling 40 is not a formality: the two runs disagree
by exactly the visual population, and the host's is the one that looks better.**

⭐ **All 63 named, and the census is taken with Ruling 142's instrument rather
than `uniq -c`:** 55 `tests/visual/` (31 `test_contrast.py`, 7 `test_offline.py`,
7 `test_capture.py`, 5 `test_no_script.py`, 5 `test_keyboard.py` — no browser in
the pinned image, `QA-03/1`, `W36` removes them), 5
`tests/docker/test_dev_image.py` (already inside the image), 3
`tests/test_knowledge_index.py` (sibling checkouts, which `git worktree add` does
not carry).

```text
pytest -q -rs | grep -c '^SKIPPED'                          ->  29   ⛔ WRONG
pytest -q -rs | sed -n 's/^SKIPPED \[\([0-9]*\)\].*/\1/p' \
              | paste -sd+ - | bc                           ->  63   ⭐ RIGHT
the run's own tail                                          ->  63   (authoritative)
```

⛔ **The lint denominator is DERIVED, never quoted (Ruling 81, `CTO-37/8`):
`py 407 + md 199 − 47 under tests/fixtures/ = 559` in `wt/po31`, `+1` for the
user's untracked `ONBOARDING.md` = **560** in MAIN** — ⭐ **and both derivations
were run against `ruff format --check`'s own count, which returned 559 and 560.**

⚠️ **~~BASE (round 30): 3759 / 63 @ `8146bdb`~~** — ⛔ **REPLACED, not appended
beneath.**

⚠️ **~~BASE (round 29): 3522 / 63 @ `ddddd05`~~** — ⛔ **REPLACED, not appended
beneath.** ⭐ **`PO-29/6` is the standing reason this paragraph is re-taken at
every round rather than added to: a reader looking for the base stops at the
head, and the head is the copy nobody re-measures.**

⛔ **AND THE TWO LINES THE TWO CHECKOUTS DISAGREE ON, both measured by me at
`ddddd05`, Ruling 108:** ⭐ **lint — `wt/po29` reads **500**, MAIN reads
**501**; index — `wt/po29` reads `none — none in this checkout`, ⛔ **MAIN reads
`stale — built at 8821b118`, which is a DISAGREEMENT with round 28's `fresh` and
is check 1's first non-trivial reading in three rounds.** ⚠️ **`PO-29/1`.**

⚠️ **~~BASE (round 27): 3419 passed / 63 skipped in the pinned container at
`426672c`~~**, the release tip, quality floor clean, **exit 0**.
⛔ **RE-DERIVED BY ME in the LINKED WORKTREE `wt/po27`, not received** — ⚠️ the
coordinator relayed the same two numbers from the MAIN checkout and they agree;
⭐ **Ruling 115 applied on its first day, and this line says which half is which.**
⭐ **All 63 named, by module: 55 `tests/visual/` (31 `test_contrast.py`, 7
`test_offline.py`, 7 `test_capture.py`, 5 `test_no_script.py`, 5
`test_keyboard.py` — no browser in the pinned image, `QA-03/1`, `W36` removes
them), 5 `tests/docker/test_dev_image.py` (already inside the image), 3
`tests/test_knowledge_index.py` (sibling checkouts, which `git worktree add`
does not carry).**

⚠️ **THE TWO CHECKOUTS DISAGREE ON TWO LINES AND NEITHER IS WRONG (Ruling 108,
and `W43`'s clause 2 on its first day):** ⛔ **index — MAIN reads `fresh — built
at 426672c2`, `wt/po27` reads `none — none in this checkout`**, because
`graphify-out/` is untracked. ⛔ **lint denominator — MAIN reads **468**,
`wt/po27` reads **467**.** ⭐ **DERIVED, not quoted:** `git ls-tree -r
--name-only 426672c | grep -Ec '\.(py|md)$'` = **475**, minus the **8** under
`tests/fixtures/` that `pyproject.toml`'s `extend-exclude` drops = ⛔ **467**,
⭐ **and MAIN's 468 is 467 + the one untracked `ONBOARDING.md`** — ⚠️ **which is
`PO-23/5` reproducing EXACTLY, third instance.**

⚠️ **SUPERSEDES `3289 / 63 @ `d1270cd`` (round 26) and `3261 / 63 @ `ce58a36``
(round 25), whose paragraphs are kept whole below.** ⭐ **Ninth base.**

⚠️ **~~BASE (round 25): 3261 passed / 63 skipped at `ce58a36`~~**, the release
tip then, quality floor clean. ⭐ **`SF-31` (`f3ee177`, +89)
and `SF-04` (`0899f0f`, +82) both merged since the round-24 base.**
⛔ **THE SKIP SET IS A PROPERTY OF THE CHECKOUT (Ruling 108)** — ⚠️ **the 63 below
are the CONTAINER'S set, and the container was run from the LINKED WORKTREE
`wt/po25`.** ⭐ **All 63 named: 55 `tests/visual/` (no browser in the pinned image
— `QA-03/1`, `W36` removes them), 5 `tests/docker/test_dev_image.py` 512/518/538/
547/566 (already inside the image), 3 `tests/test_knowledge_index.py` 125 ×2 and
160 (sibling checkouts, which `git worktree add` does not carry).**
⛔ **A host set is not comparable with this one and is not the verdict.**

⚠️ **SUPERSEDES `3090 / 63 @ `d1270cd``, the round-24 base**, whose paragraph is
kept whole below. ⭐ **Eighth base; the seven earlier ones are kept.**

⚠️ **Denominator, per Ruling 86a and DERIVED FROM THE TREE, not the disk:**
`git ls-tree -r --name-only d1270cd | grep -Ec '\.(py|md)$'` = **432**, minus the
**8** under `tests/fixtures/` that `pyproject.toml:86`'s `extend-exclude` drops
= ⛔ **424, which is what `ruff` walks.** ⚠️ **A checkout carrying one untracked
`.md` prints 425 for the same commit** — ⭐ **which is `PO-23/5` exactly, and it
is why the number above is derived rather than quoted.** ⛔ **`CTO-27/1` verified
the derivation at five refs and it is exact at every one.**

⚠️ **SUPERSEDES `3090 / 63 @ `2fe56a4``, M1's close ref**, which round 26's and
round 27's docs merges moved by **zero tests and +3 files**. ⛔ **Per Ruling 97 the
M1 CLOSE STILL STANDS AT `2fe56a4`** — ⭐ **a close records what was true at a
ref and is judged against that ref; it never claimed the tip.**
⚠️ **SUPERSEDES `3026 / 8 @ `ee50f77``, the round-22 base**, which `W30`+`W31`,
`W33` and `QA-03` moved by +64 and +55 skips. ⭐ **Seventh base; the six earlier
ones are kept below.**

⚠️ **The round-22 base's paragraph is kept whole, because a base is *what was
measured, where, and at which commit* and none of them is deleted:**
📏 **Base: 3026 passed / 8 skipped in the pinned container at `ee50f77`**, the
release tip, quality floor clean — ⭐ **the CTO's round-24 tip measurement, and
`release/m0-foundations` now carries it** (`FND-09` +56, `po-round21` docs-only).
⭐ **The 8 skips are the container's 8 and are identical to round 23's set**
(5 × `tests/docker/test_dev_image.py`, 2 for absent sibling checkouts, 1 for an
absent corpus index) — ⛔ **and the host's 8 is a DIFFERENT 8; the two sets are
disjoint and must never be reconciled by count** (`W33/3` measures the
ruff-absent column at three deep, not two).
⛔ **Lint at `ee50f77`: `ruff` PINNED-GREEN** — `ruff 0.16.6` in the dev image,
`check` exit 0 over 295 Python files, `format --check` exit 0 over 397 files
(295 Python plus 102 documents — `W33/4`).
⚠️ **SUPERSEDES `2970 / 8 @ `90dc580``, the round-21 base**, which `FND-09` moved
by +56. ⭐ **Fifth base, and the four earlier ones are kept below.**

⚠️ **The previous base's paragraph is kept because the RULE is in it:**
⛔ **Lint: `ruff` PINNED-GREEN at `90dc580`** — `ruff 0.16.6` in the pinned image,
`check` and `format --check` both exit 0. ⚠️ **Ruling 79 requires this line and
BANS the pairing *"N passed, M skipped, floor clean"* as a summary of a branch:
both halves are true, neither covers lint, and read together they assert a signal
that did not exist.** ⭐ **`floor clean` has never meant `lint-clean`, and in one
wave that gap hid 4 `ruff` errors in `FND-08`, 15 findings and 9 unformatted files
in `SF-12`, and a `SF-12` mutant that passes all 2923 tests and is killed only by
`ruff F401`.** ⛔ **Every earlier base below carries the banned pairing; those are
RECORDS of what was measured and are left as written. This line is the claim about
now, and it states lint.**
⚠️ **SUPERSEDES `2662 / 8 @ `2926dc2``, which `FND-08` (+47) and `SF-12` (+257)
moved, plus the round's docs merges.** ⚠️ **SUPERSEDES `2649 / 8 @ `c84ca2e``,
which `W28` moved by +13.** ⛔ **Fourth base in two rounds, and the previous three
are kept below** — a base is *what was measured, where, and at which commit*. ⚠️ **Third base in one round** — `2568 @ 40731e4`, `2570 @ 1b2d993`, now this. ⚠️ **`2568 / 8 @ `40731e4`` was written earlier
in this same round and was superseded before it was committed — see the close
run's second pass.** ⚠️ **SUPERSEDES *"2490 / 8 at `a7c114b`"*,
which was two merges behind when it was written and is now four.** ⭐ **The
superseded figure is not deleted, because the paragraph below is about it and
the reasoning is what this board keeps:** `2490 / 8 @ `a7c114b`` (container) and
`2487 / 11 @ `e5bcc85`` (host).

⛔ **Read the two commits, not the two numbers.** ⚠️ **`a7c114b` is two merges
behind the tip**, so the container figure is a measurement of a tree nobody is
working on — ⭐ **and the honest form of a base is *what was measured, where, and
at which commit*, never a bare pair of counts.** ⛔ **A base quoted without its
commit is the branch-state-as-tip-state defect wearing a number**, which is the
one this session has catalogued five times. ⚠️ **Neither figure supersedes the
other and both carry their instrument.** ⭐ **The arithmetic reconciles exactly —
`2490 + 8 = 2487 + 11 = 2498` — so the difference is *three tests that skip
off-image*, not three tests that vanished.** ⛔ **Which three is not measured
here**, and that is the first thing to check if the totals ever stop reconciling.

⛔ **CHECK 4 RAN AT WAVE-CLOSE for the first time (round 19) and it found four
stale rows, a failed check 5, and a duplicated `W`-id.** ⭐ **Its SECOND close run
(round 20) found two stale rows and — ⭐ for the first time in four rounds — went
stale nowhere, because no branch was awaiting a verdict while it ran.**
⭐ **Its THIRD close run (round 21) is the third data point for that rule and it
CONFIRMS it: the review queue was empty when the run started, and the run drifted
nowhere.** ⛔ **`PO-20/3` is now measured three times and is promoted from an
observation to the scheduling rule for check 4.**
⛔ **Its FOURTH close run (round 22) is the FIRST NEGATIVE data point and it is
the one the other three could not supply: the queue was NOT empty, and the run
found three rows that had gone stale DURING the wave** — ⚠️ **including an
APPROVED branch that never reached release, for the second consecutive round
(`PO-22/4`).** ⭐ **Three confirmations are a correlation; one contradiction under
the opposite condition is what makes it a rule.**
⭐ **Both runs' readings are in [the wave-checks section](#the-wave-checks-six-at-open-and-check-4-again-at-close);
this line points at them and does not restate them.**

⛔ **Release branch: `release/m0-foundations`, and M1 continues on it.** ⚠️ **Its
name is historical, not descriptive** — there is no `release/m1-*` and there never
was; the milestone-naming scheme is retired, and the argument is in
[`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md). Developers branch off it, the CTO reviews
against `../conventions/review-rubric.md`, only reviewed work merges back. Flow:
`../conventions/delivery-flow.md`.

## ⛔ This file was split, and here is the number

⚠️ **`BOARD.md` reached 1,615 lines / ~180KB — roughly 45k tokens — and every
agent is told to read it. It doubled in one wave.** ⛔ **It had become the single
largest per-agent cost in the project**, on top of the rubric (1,025 lines),
`agent-protocol.md` and `module-structure.md`.

⭐ **Live board ~56KB; [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md) holds the rest.**

⛔ **Nothing was summarised. Closed sections moved *whole*, unedited**, because my
own standing rule is that the board must carry **more** reasoning, not less — and
⚠️ **a condensed copy would have been the stale-copy defect this document has
already committed four times.** ⭐ **The split is not *old versus new*: it is
*what a per-task agent must load*.** A developer needs their rows and the standing
rules; the CTO needs open findings and the register; **only the PO needs the
history.**

⚠️ **Built in the order `SK-01` proved matters: the archive was written and every
moved section verified present *before* anything was removed here.** ⛔ **The
reverse order gives a green suite and a board full of dangling pointers, and
nothing mechanical catches it** — which is why `W21`'s pointer walk now has a
second consumer.

⚠️ **M1 is the riskiest milestone** — where every contract meets every other one
for the first time — so ordering *inside* a step matters, because a contract that
merges first becomes the shape the next tasks copy.

⭐ **And the standing rule the split was designed around, restated because it is
load-bearing and must not be read as weakened: this board carries *more*
reasoning, not less.** The entries that paid for themselves were the ones
recording **why** — X2's dissolution, G1's recorded loss, the flattering review
base — ⛔ **because a recorded *why* is what stops a question being re-asked by
the next agent.** ⚠️ **The split changed *where* the reasoning lives, never
whether it exists**: closed reasoning moved whole to the archive, and ⛔ **a
future editor who shortens a section instead of moving it has broken this rule,
not applied it.**

*Statuses:* `todo` · `in-progress` · `in-review` · `blocked` · `done`.
*Editing rule:* a status change is one cell. Do not restructure rows; record
events in the **Log**, which lives in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md) and
is appended to there.

## ⛔ RULED 2026-09-10 — **findings are numbered per-document; `53`, `54` and `55` are ambiguous and here is which is which**

⭐ **Raised by the coordinator, measured here, ruled here.** ⛔ **The rule lands in
[`../conventions/agent-protocol.md`](../conventions/agent-protocol.md)** — *a
finding is numbered inside its own document, never globally*, as
`<TASK-ID>/<n>` — ⚠️ **and the argument for refusing an allocator is there, not
restated here.**

⛔ **The measurement found more than the report did, and that is Ruling 55 again.**
⚠️ **The report named one collision, from a grep of `5[5-9]`. A full census of
`handoffs/` found THREE — `53`, `54` and `55` — and 10 gaps in a 39-number
range.** ⭐ **The number was a fact about an instrument.**

### ⛔ The disambiguation, because 8 live citations are ambiguous today

⛔ **Neither document is edited — a handoff is a record.** ⭐ **`W4`'s precedent:
the board is where a superseded record gets superseded.** ⚠️ **Numbers 20–58 are a
CLOSED LEGACY RANGE; every existing citation still resolves, and a citation to one
of these three must say which.**

| # | `FND-05a.md` | `SF-10-survey.md` |
|---|---|---|
| **53** | `:137` | `:163` |
| **54** | `:146` | `:168` |
| **55** | `:157` — *this gate cannot run inside …* | `:176` — *the load-side validator …* |

⛔ **Cite these three as `FND-05a/53` or `SF-10-survey/53`, never as "finding 53".**

⭐ **The sharpest fact, and it is the one that refused the allocator:** ⛔ **both
documents have the same author, on two branches, in one wave.** ⚠️ **They collided
with themselves** — so an allocator file would have been edited on both branches
and would either conflict (the reviewer catching it, which is what we already
have) or ⛔ **merge cleanly with both increments and lose one silently.**

### ⭐ The enforcement rides with `W25`, and yes it is worth hurrying for

⛔ **Ruling 49's handoff check is being built this wave, by Developer 2, on this
exact directory.** ⭐ **One commit rather than a second pass over the same file**,
and the check is the natural enforcer: it is already deciding what a handoff *is*.

⚠️ **It does not widen `W25`'s scope so much as give it a second, cheaper
assertion** — ⛔ **`<TASK-ID>/<n>` is a *shape*, and a shape is exactly what that
check was already going to test.** ⭐ **It also inherits `W25`'s hardest problem
for free: 29 of 52 files in that directory are not task-shaped, and a finding
number scoped to its document does not care.**

⛔ **Legacy is not migrated and the check must say so** — ⭐ **numbers 20–58 in the
existing 12 documents are grandfathered, and a check that reds on them would be a
check that demands a record be rewritten.**

---

### ⛔ The editing rule that this document kept breaking: **a summary points, it never restates**

⚠️ **Four instances in one milestone, three of them in this file.** The release
branch that never existed; the index recorded present when it was absent; the C5
row saying *"CTO to rule"* three screens above the section reading *"✅ RULED"*;
and the R21 register carrying **two** rows the spec had already closed.

⭐ **They are one defect wearing four costumes, and the shape is now the finding
rather than the four corrections.** ⛔ **A summary that restates a status owned
somewhere else is a copy, and a copy goes stale in exactly one direction: the
summary is what people read, the source is what people update.** So the summary
is where the *wrong* answer lives and the busy reader is the one who gets it.

⛔ **The rule, and it binds this document first:**

- **A status table carries a pointer to the section or the source, never a
  restatement of it.** *"✅ RULED — see the C5 section"* is a summary. *"Options
  1 and 2, option 3 refused"* in a table is a second copy.
- **A register of things owned elsewhere is derived from that source, not
  maintained beside it** — R21's register is now the reasoning behind §R9's
  `open` entries, and §R9 is what says which are open.
- ⚠️ **This is the same argument as C2's** (*a convention that repeats its own
  definition is the defect it polices elsewhere*) and the same as the single
  block-type list, the single size ceiling and the single review base. ⭐ **The
  fourth appearance is where it stops being a coincidence.**

⛔ **Standing user decision: nothing is ever pushed to any remote. Everything
stays in local repositories.** Permanent, not a phase. ⚠️ It changed the plan
rather than the workflow: **R18 is amended**, git submodules are **not used in
this project**, `FND-05b` is **cancelled**, and `FND-05a` becomes a tracked pin
file verified against the local checkouts. ⭐ **B2** and **G1**, both closed, are in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md).

---

**M0 — Foundations: ✅ CLOSED 2026-09-09**, green in the container, 124 passed / 8 skipped. ⭐ **Its sequencing argument, the C1/C4/B2/G1 items and the FND-05b cancellation are in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md), whole and unedited.** ⚠️ `FND-05a` is the one M0 task still open and it gates nothing.

---

**Open questions: ⭐ none.** Q1–Q7, X1 and X2 are all ruled, merged and carried into the tasks they touch — **the reasoning is in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md)**, kept because it is what stops them being re-asked. ⛔ **An empty list is not evidence that no contract is unlocated** — that is R21's register below.

---

## R21 — the register of unlocated contracts

⭐ **R21 was adopted by explicit user decision**, and it generalises Q1–Q3: *a
contract is located before it is described* — the file it lives in, the key that
versions it (R9), and the one producer that writes it, all stated **before** any
task builds against it. ⛔ A task that meets an unlocated contract **stops and
asks**; choosing quietly is the failure the rule names.

⭐ **The rule earned its number by being surveyed rather than assumed.** Asking
"where else is this true?" turned up **five more instances already sitting in the
spec with no owner**. These are board items, not spec trivia: each is owed by the
task named beside it, *before* that task builds.

| Open row | Owed before | Owner | Why it bites |
|---|---|---|---|
| ~~**authored overlay** `content.json` — unversioned~~ | ~~SF-09~~ | CTO | ✅ **CLOSED by SF-09 — three open rows, not four.** ⭐ **Verified in the tree rather than inherited from the handoff:** `content_api` is minted in `src/studyforge/version.py`, sits in `CONTRACT_FIELDS`, and `test_the_overlay_is_versioned_and_the_key_is_content_api` asserts it — 23 occurrences across `src/` and `tests/`. R9 **gained** the contract rather than excusing it, and the spec now points at the constant instead of re-listing five names, which is why *"R9 lists five and there are seven"* cannot recur |
| ~~⛔ **discovery cache** `.studyforge/site.json` — no version key~~ | ~~`SF-04`~~ | CTO | ✅ **CLOSED by Ruling 95, CTO round 27 — the key is `site_api`, and `SF-04` is the ONE writer.** ⭐ **Verified in the tree rather than inherited from the handoff:** the register row is in spec §R9 and the contract is in `E01`'s `SF-04` section, both at `d1270cd`. ⛔ **The name is the register's own convention, not a preference** — every located contract takes its filename's noun (`corpus.json`→`corpus_api`, `container.json`→`container_api`), so `site.json`→`site_api` is the only name that does not make the column a lookup table. ⚠️ **`SF-09` was the worked example for the MECHANICS and not for the FAILURE**: an unsupported or absent `site_api` **does not raise** — the cache is not read, the scan runs, the cache is rewritten, reported and never silent (R6) — ⛔ **and `site_api` is NOT the staleness mechanism** |
| **narration manifest** — no file, no version | **NS-02 / SF-17** (M3) | CTO | Two producers named for one contract is Q3's shape exactly, and Q3 needed a ruling |
| **coverage report** — no file | **EX-05** (M7) | CTO | Not read back, so the cheapest of the five — but R5 is what the report exists to make honest |
| ~~**component consuming contract** `consuming.json` — no version key~~ | ~~TC-05, E13~~ | CTO | ✅ **CLOSED — and this board was stale by two rows, not one** (CTO round 17, ruling 16). `consuming_api` is in spec §R9. ⭐ The reasoning survives and is worth keeping: the pin file records **which commit**, `provides` records **the promise**, `consuming_api` versions **the schema** — three different questions that G1's answer only looked like it had all covered |

⛔ **Ruled (round 17): this register stops being a second copy of §R9 and becomes
a pointer to it.** ⚠️ **Two of its five rows were stale simultaneously**, both in
the same direction — closed in the spec, open here — which is precisely how a
duplicated status behaves. ⭐ **The open set is whatever §R9 marks `open`**; the
rows below are kept only for the *reasoning*, which §R9 does not carry.

**Genuinely open: two, and NEITHER IS DUE.** ✅ **ROUND 24: the discovery cache
CLOSED (Ruling 95), so for the first time since M1 opened no open R21 row is due
in the open milestone.** ⭐ The two remaining are narration manifest
(`NS-02`/`SF-17`, **M3**) and coverage report (`EX-05`, **M7**).

⚠️ **Worth recording, because the register's own history is the argument for it:
this row was described as *"the near one"* for four rounds, became DUE for one
round, and closed in a single CTO decision.** ⭐ **The cost of R21 is one
escalation; the cost of skipping it is a cache with no version key, which cannot
be refused — only misread.**

✅ **AND THE ONE THAT WAS IN FLIGHT IS ANSWERED — Ruling 102, CTO round 28,
landed in `E01` at `2db881d`. Carried here at round 25.**

⛔ **~~`SF-35` and `SF-36` are two additive manifest shapes in one wave, so do
they share `corpus_api: 2`, or take 2 and 3? The PO's reading is `3`.~~**
⭐ **NEITHER, and the premise was false: `SF-36` does not touch `corpus_api` at
all.** ⚠️ **`origin` is a `container.json` field — `grep -rn 'origin'
src/studyforge/corpus/manifest/` returns NO MATCH — ⛔ so `SF-36` mints
`container_api: 2` and the two tasks are not two additive shapes in ONE
register; they are one shape each in TWO registers.**

⭐ **What R21 gains, and it is the reason to record an answered question rather
than delete it:** ⛔ **the escalation was correct and the reasoning inside it was
correct; what was missing was one question the chain never asked.**

> ⛔ **A contract version is minted in the register of the DOCUMENT that carries
> the new key. ⭐ Name the file the key appears in BEFORE naming the version.**

⚠️ **This is Ruling 81 arriving in a version register: the answer reproduced the
right SHAPE — two shapes, two commits, two numbers — while its SET was wrong.**
⭐ **A matching shape is evidence that the shape matches, and nothing more.**
⛔ **Cost of the escalation: one round of a question. Cost of not escalating: a
developer with a 25k budget opening `corpus/manifest/`, where the field is not.**

⚠️ **`consuming.json` is now the sharper half of what G1 covered.** ⭐ G1's answer
restores *which commit of each component* — that is what `FND-05a`'s pin file
records. It does **not** restore *which version of the promise* each component
made, which is the contract's own job and is still unversioned. ⛔ So a corpus can
now say which components it was built against and still not say what they
guaranteed — and that gap sits on the **runtime seam between the two agents**,
which is the one seam neither can inspect from their own side.

---

**Delivery-process defects C2, C3 and C5: ✅ all ruled and closed.** ⭐ **C5's ruling — options 1 *and* 2, option 3 refused — and the meta-finding the CTO rated above it are in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md).** ⚠️ Its residue is live in two places that are not this board: the standing rule in `FND-06` and the trial-merge step in the rubric's §0a.

---

**M1 step 1.1: ✅ CLOSED.** SF-01, SF-02, SF-07, SF-08, SF-11, SF-33 and the FND-04 follow-up all merged. ⭐ **The lane assignment and the collision-pair reasoning it validated are in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md)** — worth reading before assigning a step, because it is where the rule was first tested.

---

**The release-branch reconciliation: ✅ ruled and closed.** ⛔ **Standing outcome, kept here because it still binds: `release/m0-foundations` is the release branch, its name is historical rather than descriptive, and the milestone-naming scheme is retired.** ⭐ The argument is in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md).

---

**M1 step 1.3: ✅ CLOSED** at `277469e`. ⭐ **Its assignment, the two collision surfaces measured rather than guessed, the `Profile` reversal and the merge-order rulings are in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md).**

---

## M1 step 1.4 — one task, and a gate in front of it

> **Step 1.4 is `SF-10`**, the unit document builder — `Depends on` SF-05, SF-06,
> SF-09, all merged. **Team**-sized, `~70k`, owns `unit/builder.py` and its
> package.

⛔ **This table was rebuilt on 2026-09-10, because it had become the defect it
exists to prevent.** ⚠️ **It carried `W20` twice (`todo` **and** `done`), `SF-10`
twice (`unblocked` **and** `todo`), and three rows whose status disagreed with
the tree.** ⭐ **Every cell below is a measurement taken on `e5bcc85` today**, not
a status inherited from the round that wrote it. The re-measurement is check 4
and this is what it produced.

| Task | Owner | Status | Gate |
|---|---|---|---|
| **W14** — two missing invalid fixtures | Developer 1 | ✅ `done` | — |
| **W18** — Ruling 35, `authoritative ⟹ bundled` | Developer 1 | ✅ `done` | — |
| **W23** — the live R7 hole (tilde, `/export/home/`) | Developer 2 | ✅ `done` — ⛔ **the board said `in-progress` for a round** | — |
| **W20** — repo-wide §7c check **and its migration** | Developer 2 | ✅ `done` — **0 hits, floor clean, exit 0** | — |
| **Ruling 46's helper** — `asserting=` rule-id set + the misattribution message | Developer 1 | ✅ `done` — ⚠️ **the board said `in-progress`; it is merged** | ⛔ **stopped at the helper; the general seam is `FND-08`** |
| **SF-10 survey** — port inventory + R11 package shape (**W5**) | Developer 1 | ✅ `done` — `13b2857`, one document, no code | — |
| **FND-05a** — the workspace pin file and its verification command | Developer 1 | ✅ `done` — ⭐ **M0 CLOSED** | — |
| **SF-10** — Unit document builder | Developer 1 | ✅ **`done` — APPROVED and merged `966ab30`** | ⭐ **M1 step 1.4 CLOSES** |
| **W25** — Ruling 49's handoff check | Developer 2 | ⛔ **`in-review` — `feat/W25-handoff-check` @ `f77bb7d`, 2629 / 8.** ⚠️ **CORRECTED at check 4's close run: the previous cell said *"NEVER STARTED, byte-identical to `HEAD`"* and was true when written.** ⛔ **`HEAD` moved; the sentence did not** | ⛔ **and it is re-priced: see below** |

#### ⛔ The two rows that were lying, and they lied in opposite directions

> ⛔ **AND IT HAPPENED TO ME, IN THIS SECTION, WITHIN THE HOUR.** ⚠️ **I wrote
> `SF-10` up as `in-review` on an unmerged branch; the CTO approved and merged it
> at `966ab30` while I was still writing.** ⭐ **So the row below was correct when
> written and stale when committed — which is the same defect, in the same
> document, in the paragraph diagnosing it.** ⛔ **That is the argument for
> re-measuring at wave-CLOSE, and it is now ruled: see the wave-open checks.**

⚠️ **`SF-10` is the expensive one, and it is a new shape of the same old defect.**
The board said *"unblocked, waiting on nothing"* — ⛔ **while 1,989 lines of it,
across 18 files, sat finished on an unmerged branch.** ⭐ **A second author picking
the row up would have rewritten the entire package**, and nothing on this board
would have told them not to. ⛔ **That is *branch state invisible as tip state*,
which is the mirror of the defect this session has catalogued five times** — and
the mirror is worse, because the familiar version over-reports progress and this
one **under**-reports it, so it reads as caution rather than as error.

⭐ **The row now names the branch and the commit.** ⛔ **A row for work in review
that does not say where the work is has not recorded anything.**

⚠️ **`W25` is the plain one: `in-progress` against a branch containing nothing.**
⭐ **The coordinator's handoff said "never started" and the board disagreed; the
`git diff` settles it and the handoff was right.**

⛔ **`W23` and Ruling 46's helper were both `in-progress` and both merged** — so
three of this table's nine rows were wrong, in **both** directions, in one round.
⚠️ **That is the argument for check 4 being run rather than read**, and it is now
the second time running it has changed the plan.

#### ⚠️ `W25` is re-priced, and the number is the reason it is not a small task

⛔ **Ruling 49 binds `<TASK-ID>.md`, and most of that directory is not
task-shaped.** ⭐ **Measured today, not inherited:**

| `docs/tasks/handoffs/` | count |
|---|---|
| files total | **52** |
| strictly `<TASK-ID>.md` | **23** |
| not task-shaped at all (CTO rounds, sessions, `README.md`, a drift doc, ruling notes) | **23** |
| compound or suffixed task ids (`SF-10-survey`, `W1-W2`, `W7-W13`, `W14-W18`, `W17-W19`, `W19-provenance-pin`) | **6** |
| ⛔ **would need an exemption rule or a rename** | ⛔ **29 of 52 — 56%** |

⛔ **So the check's hard part is not the six sections; it is deciding what a
handoff *is*.** ⚠️ **A naive check demands six sections from a CTO round document
and from a survey that owes none** — the coordinator flagged exactly this and the
measurement makes it 56% of the directory rather than an edge case. ⭐ **The rule
is `FND-08`'s and it is the same one: *exempt documents by declaration, never by
guessing at a filename*.**

### ⭐ Developer 1 takes FND-05a — the M0 residue that has waited a whole milestone

⛔ **`SF-10` was gated on rulings 50 and 51, and `W20` was ahead of it**, so the
build could not start. ⚠️ **This line said *"rulings 53 and 54"* — those are
`FND-05a`'s — and it survived the same table's duplicate rows being corrected.**
⭐ **The *summary points, never restates* rule biting inside the section that
states it**, which is the fourth costume and now the fifth. ⭐ **`FND-05a` is the right use of the gap and it has been
right for a while:** it is a **tracked pin file plus a verification command**,
it touches neither `tools/quality/` (Developer 2's `W20`) nor `unit/`
(`SF-10`), and ⛔ **it is the last open M0 task — landing it closes M0
outright.**

⚠️ **My own words on it, now a full milestone old:** *"it should not slip
**indefinitely**: the failure it prevents — a component at a commit the parent
never recorded — has **no symptom**, so it is discovered by being wrong rather
than by failing."* ⛔ **A task whose justification is *it can slip* accumulates
exactly one counter-argument per milestone**, and this is its second.

⭐ **Acceptance is unchanged and already sharp:** verification **exits 0** when
correct and **exits 1 naming the component** both when a recorded commit is
absent locally and when a component's `HEAD` moved unrecorded — ⛔ **asserted, not
described** — and ⛔ **no `.gitmodules` anywhere, no absolute path in any tracked
file.**

### ⭐ What the survey gives SF-10 — and the seam whose failure is silent

**Proposed shape:** `unit/builder/{__init__,material,derived,authored,document}.py`,
plus ⭐ **`unit/served.py` as a *sibling*, not a child.** ⚠️ Its **name** was
stated rather than taken — correctly left as a team decision.

⛔ **The load-bearing seam, and it is FND-04's argument again:** `derived`
**computes** order; `authored` **must never re-derive it** — because two
consumers ordering differently **mint different speech ids and desynchronise the
page from its audio.**

> ⛔ *"Split, the authored path cannot reach the ordering code by accident; in one
> module they are two branches and nothing but care keeps them apart."*

⭐ **That is a seam, not a slice** — the distinction R11 turns on — ⚠️ **and its
failure is silent**, which is why it is worth a package boundary rather than a
convention. ⭐ **`builder/document.py` has the least headroom at ~290, so its next
seam is named now** rather than discovered at 400.

⛔ **Two CTO rulings are owed before `SF-10` builds — it is gated on them:**

| # | The collision | Why it cannot wait |
|---|---|---|
| **53** | `unitdoc.py` re-gates every archive file on **every read, by design** — ⛔ **and Ruling 17 put that gate upstream** | ⚠️ **Both are defensible and they cannot both be implemented.** A builder written against the wrong one is rewritten, not adjusted |
| **54** | ⛔ **`source` means a *corpus id* here and *a fetch URL* there** | ⛔ **`SF-10` writes the `sources` array, so it is where they collide.** ⚠️ **Rename before 1,290 documents carry it** — R9 makes a written key expensive, and this is the last moment it is free |

⚠️ **Five further open questions are carried in the survey, each with what would
settle it** — including whether the served document gets its own `api` version.
⛔ **No equivalent of `UNIT_API = 3` exists**, which makes it an **R21 register row
in the making**: a contract that is about to be written and is not yet located.

### ⭐ Developer 1's slot: the survey, not the build

⛔ **`SF-10` is `Team`-sized, so its code is not authored by one person ahead of
the other** — that is the collision-pair rule, and splitting a shared surface is
exactly what it forbids. ⚠️ **But the serial part of `SF-10` is not the code.** It
is **`W5`: `unitdoc.py` is 827 lines against R11's 400**, and R11 is explicit that
the large modules arrive **as packages or not at all**.

⭐ **So Developer 1 takes the survey now:** the port inventory, and **a proposed
package shape with its seams named** — the same deliverable that made `FND-04`'s
split cheap, and the same reason the CTO gave for it there: ⛔ **only somebody who
knows the module's internals can answer where it divides.**

⛔ **Deliverable is a design, not builder code.** ⚠️ Nothing is authored on the
shared surface before the team convenes — ⭐ **which keeps the team task intact
while spending the idle time on the part that was always going to be serial.**

### ⛔ Why W14 and W18 gate the step rather than riding alongside

⚠️ **W18 is not bookkeeping — it is a live correctness hole.** Measured:
`FORBIDDEN` still carries only the `generated` pair, so ⛔ **a grader the reader
wrote can declare itself the source's own.** That is R5 failing open, and
`SF-10` is the task that assembles what a reader is shown.

⛔ **And letting them ride alongside is what already failed, twice.** They rode
alongside SK-01 and did not land. ⭐ **A thing that has evaporated twice does not
get a third trigger; it gets a gate.**

### ⛔ SCOPED AND CLOSED — **Ruling 43's four walks are `FND-08` and `FND-09`**, and the count was wrong

⭐ **Ruling 43's task is scoped, once, and the scoping is now in the epic where a
task definition belongs — `E00-foundations.md`, `FND-08` and `FND-09`.** ⛔ **The
section below is kept because its *reasoning* is still load-bearing and its
correction is the best worked example this board has of a scope written against
the wrong artifact. ⚠️ Its forward-looking clauses are superseded by the
measurement.**

⛔ **It owed four walks. Measured on `e5bcc85`, it owes two tasks and one of the
four is refused outright:**

| Walk | Scoped as | ⛔ **Measured today** | Now |
|---|---|---|---|
| **1 — corpus names** | done as `W20` | ✅ **0 hits**, floor clean, exit 0 | ✅ **closed** |
| **2 — dangling pointers** (`W21`) | a check | **41 links, 33 real, ⭐ 0 dangling** — ⛔ **but 8 of 8 naive hits are false** | ⭐ **`FND-08`** |
| **4 — the board's own archive pointers** | ⛔ **"the split added a fourth consumer"** | ⛔ **14 links, 14 resolve, `0` anchors** | ⛔ **REFUSED — it collapses into walk 2** |
| **3 — sweep-by-declaration** (Ruling 46) | one seam, four consumers | **7 modules, 10 call sites, ⛔ 2 more unknown copies** | ⭐ **`FND-09`** |

⛔ **Walk 4 was my own addition and it is the one that had to go.** ⚠️ **I wrote
*"the board split just added a fourth consumer, since every `BOARD.md` pointer
into the archive wants the same walk."*** ⭐ **Measured: all 14 pointers resolve
and not one carries an anchor — so a checker over them can only assert that one
file exists, and it would pass on the day the archive is emptied.** ⛔ **That is a
check that cannot fail, which is Ruling 48's defect, arriving inside the scope
written to prevent it — for the *second* time in this same section.**

⭐ **The first time, I scoped against Ruling 45 and named `VIOLATION.md` without
opening it. This time I named a walk without counting its links.** ⚠️ **Same
error, one level up: the first was a ruling I had not read, the second a
measurement I had not taken.** ⛔ **And both were caught by the *same* remedy —
opening the artifact — which is now the strongest evidence this board has that
Ruling 55 is a rule and not a slogan.**

⭐ **The ordering inverts as a result: `BOARD.md` gains anchors first, and walk 4
becomes an assertion over walk 2's output.** ⛔ **Adding the anchors is mine.**

#### ⭐ Owners, and the measured price each is being asked to pay

| Task | Owner | ⛔ **Measured price** | Gate |
|---|---|---|---|
| **`FND-08`** — the document walk | **Developer 2** — ⭐ **`tools/quality/` is their surface, and `W20`, `W21` and `W25` all live on it** | ⛔ **migration `0`; the cost is the markdown parser** — fence state machine **plus inline code-span stripping**, without which the check is **8-of-8 false** on this tree. ⭐ **The file-walk seam is ~80 % built already** in `tools/quality/config.py` | ⛔ **after `W25`** — same surface, and `W25` has the earlier trigger |
| **`FND-09`** — the fixture-access seam | **Developer 1** — ⭐ **they authored Ruling 46's helper and its negative control** | ⛔ **7 modules, 10 call sites**, plus **2 previously-unknown copies** of the invalid set. ⚠️ **The move is a net size relief**: the helper's host module is at **567 / 600** | ⛔ **not before `SF-10` merges** — it edits the test tree `SF-10` is adding to |

⛔ **Neither task gates the renderer.** ⭐ **Said explicitly because `W20` gated
`SF-10` and the shape is easy to over-apply** — ⚠️ **`W20` gated it because a
repository-wide check accumulates a migration from every new emission site, and
`SF-10` was about to add some.** ⛔ **`FND-08` walks *documents* and `FND-09` walks
*fixtures*; neither accumulates anything from `SF-12`.** ⭐ **Ruling 52 again: the
scope that rule was argued over is checks with a growing backlog.**

⚠️ **And the sharpest single correction: `including_invalid=` does not exist in
any Python file in this repository.** ⭐ **It survives only in prose — including in
the section below.** ⛔ **A scope written against it is quoting a document as
code.**

---

### ⭐ Scoped before the task is written: **W20 ships a fixture-access seam, and three walks consume it** — ⚠️ **superseded above**

⛔ **Decided now because the CTO asked for it before scoping, and because three
tree-walks are about to be written by three different people.** Ruling 43's task
owes **corpus names**, **dangling pointers** (Finding 50 / `W21`), and **Ruling
45's sweep** — ⚠️ **and the board split just added a fourth consumer**, since
every `BOARD.md` pointer into the archive wants the same walk.

> ⛔ **CORRECTED — I scoped this against Ruling 45, which Ruling 46 superseded,
> and building it as written would have produced the defect the supersession
> exists to prevent.** ⚠️ **I named `VIOLATION.md` as the declaration and did not
> open it.** ⭐ **The CTO's new clause on themselves is mine identically: a ruling
> that names an artifact opens it first.**
>
> ⛔ **Measured by me on the tip `ac4ed55`, not inherited:** `INVALID_CORPORA`
> maps a directory to the **checker's** rule id — `"count-mismatch": "counts"`,
> `"user-authoritative": "exercise-trust"`, seven entries — while every
> `VIOLATION.md` names the **spec** rule in prose: `spec §6`, `R9`, `R7`.
> ⛔ **Not one of the seven names the id the sweeps use.**
>
> ⚠️ **They are not two copies of one fact — they are two different
> vocabularies.** So a seam reading `VIOLATION.md` needs **a prose parser *and* a
> `spec §6 → counts` translation table**, to reach a dict that already exists, is
> already exported, and is already pinned to the directory by
> `test_the_invalid_set_is_exactly_what_is_on_disk`. ⛔ **That is a second copy of
> one declaration — the defect diagnosed five times — arriving inside the scope
> written to fix it.**

⛔ **Ruling 46 — the rule the seam implements:** ⭐ ***a sweep names, as a set of
rule ids, every property it asserts***, and the helper excludes exactly
`{d for d, rule in INVALID_CORPORA.items() if rule in asserting}`.

⛔ **A set, not a string, and the block-vocabulary sweep is why:** it asserts
membership **and** counts, so ⚠️ **a single id excludes too little and the
directory excludes too much.**

⛔ **And the half that closes finding 47, which this scope must carry:** a set
still permits **under**-declaration, ⚠️ **and that red reads as the fixture's
fault.** So the failure message names the declaration:

> *"`user-authoritative` declares rule `exercise-trust`; if this sweep asserts
> that rule, name it in `asserting=` — **do not change the fixture**."*

⭐ **The problem was never the red; it was the misattribution.** ⛔ **Without that
sentence the next author neuters a negative control** to make a suite green — and
a neutered control is the one failure this project cannot detect from outside.

⭐ **`VIOLATION.md` keeps its §1e job and nothing parses it:** a file beside the
data telling **a person** what the gate should say. ⚠️ **Documentation, not an
interface.**

⭐ **My instinct — *read from the declaration, never the directory name* — was
right; I pointed it at the wrong artifact.** ⛔ **The declaration is
`INVALID_CORPORA`.** And it is still *enumerate the legal*: a directory name is an
open set somebody keeps extending; **the dict is a closed declaration that already
has an enforcer.**

⚠️ **Measured, and it is why the seam is not a nicety:** all **7** invalid
fixtures agree with the block vocabulary, so `including_invalid=False` drops **9
documents that should be swept** — ⛔ **each invalid in one named way and correct
in every other.** ⭐ Developer 1's fix **stands until this task**: it is correct,
it stops the false red, and it is honest about what it does.

### ⛔ W20 before SF-10, and it is the third instance of one sequencing shape

> ⛔ **HISTORICAL — every number in this subsection is a *pre-migration* reading
> and none of them describes the tree.** ⭐ **Measured 2026-09-10: `0` hits by the
> grep and `0` by the check.** ⚠️ **The sequencing argument below is why the
> answer is `0`; it is not a claim that anything is outstanding.**

⭐ **Ruling 43 measured 7 §7c hits already on the release branch** — `exercise/
states.py` (4), `archive/scrub.py` (1), `address/__init__.py` (2) — ⚠️ **all
predating this work.** So a repository-wide check **goes red the moment it
lands**, and Developer 2's finding 1 is ruled: ⛔ **a commit adding a check owns
its migration.** One task, one commit: the check plus those 7 moved. ⭐ Exemption
generalises as ***exempt documents, never modules.***

⚠️ **`SF-10` is a ~70k builder that will add emission sites.** Landing the check
after it means migrating more than 7 — which is `W6`'s argument (*a check that
arrives after twenty sites exist is one nobody turns on*) and `W13`'s (*a fixture
authored while the checker is weak was never actually bounded*). ⛔ **Third
instance of one shape, so it is a rule now and not a judgement call: a check and
the code it will judge are ordered check-first, or the check inherits a backlog
it did not cause.**

### ⭐ Why both developers take SF-10 together

`SF-10` is **`Team`**-sized in its own definition, and ⛔ **that is not the
collision-pair rule being broken — it is the rule's premise.** The pair rule
exists so a shared surface is not *split*; a team task is one surface with two
people **in** it. ⚠️ It also carries **W5**: `unitdoc.py` is **827 lines against
R11's 400**, and R11 is explicit that the large modules arrive **as packages or
not at all**.

---

## M1 step 1.5 — `SF-12`, then `QA-03`. ⭐ **Order held; the survey is confirmed with three refinements**

> **Step 1.5 is `SF-12`** (Templates and unit page renderer, **Team**, `~110k`,
> owns `render/page/` and `render/templates/`), **then `QA-03`.** ⛔ **`SF-12` is
> the largest port in the project after `SF-19a` and it is a package (R11) — a
> task that produces one large module has not done the task.**

| Task | Owner | Status | Gate |
|---|---|---|---|
| **`SF-12` survey** — port inventory + R11 package shape + ⛔ **W9's name review** | **Developer 1** | ✅ **`done` — APPROVED and merged at `1b2d993`.** ⭐ **Findings `SF-12-survey/1..6`** — ⚠️ **SIX, and round 18's handoff said five**; the branch is right and the handoff is a record | ⛔ **a design, not renderer code** |
| **`SF-12`** — Templates and unit page renderer | ⭐ **Developer 1, whole package — roster CONFIRMED, see below** | ✅ **`done` — APPROVE, merged `f4aa603`.** ⭐ **`2923 / 8` in the pinned container, floor clean, ⛔ lint pinned-green; +257 tests; largest module 235 against R11's 400.** ⚠️ **Eight findings, `SF-12/1..8`; `SF-12/4` and `SF-12/5` are ruled below** | ⛔ **All four conditions DISCHARGED.** ⭐ **One author, never split — the port landed inside the survey's band, so the trigger below never fired** |
| **`QA-03`** — Visual and browser verification harness | **both** | ⏳ **`in-review` — `feat/QA-03-visual` @ `d2dc2c4`, with the CTO** (re-measured at `ee50f77`; the row said `in-progress`) | ⛔ **after `SF-12`.** ⭐ **It is M1's LAST task and the only one M1 waits on.** ⛔ **Both of its load-bearing jobs are DONE: close condition 8 is JUDGED AND PASSED, and the chrome ruling's trigger FIRED AND DID NOT TRIP.** ⭐ **86 tests, 2203 lines, 17 modules; its own trial merge onto `ee50f77` measured `3057 passed, 63 skipped`, floor clean, lint pinned green.** ⚠️ **What M1 now waits on is this branch's MERGE, not its content** |

### ⛔ WHAT OPENS THE MOMENT THE SURVEY IS APPROVED — and it is not `SF-12`

⭐ **`SF-12` is `Team`-sized, so its gate is not a dependency, it is a ROSTER.**
⛔ **Both developers must be free, and right now neither is.** ⚠️ **Recorded
because *"when the survey lands"* reads like one condition and is three.**

| # | Must be true | State at `40731e4` + branches, 2026-09-10 |
|---|---|---|
| 1 | ⛔ **`W27` MERGED** | ✅ **DISCHARGED — merged `5c6c883`** |
| 2 | ⛔ **the survey APPROVED** | ✅ **DISCHARGED — APPROVE, merged `1b2d993`.** ⭐ **Four escalations ruled, notably *one variant per page*.** ⚠️ **`html.py` is 1699 lines, L1112 blank, exactly one template-shaped literal at L1233–1253** — re-run under the CTO's own `ast` sweep |
| 3 | ⛔ **Developer 2 free** | ✅ **DISCHARGED @ `2926dc2` — `W25` merged (`2a272a5`), `W26` merged (in `c84ca2e`).** ⛔ **`FND-08` is PARKED, not done — never started, no branch, no commit** |
| 4 | ⛔ **Developer 1 free** | ✅ **DISCHARGED @ `2926dc2` — `W28` merged (`6d65902`, +13 tests).** ⛔ **`FND-09` is PARKED, not done — never started, no branch, no commit** |

### ⭐ `W27` LANDED FIRST — ⛔ **and the argument is kept because it was right, not because it is still pending**

⚠️ **`W27` touches `unit/content.py`, `corpus/manifest/document.py`,
`corpus/placement/identity.py` and two `errors.py`. `SF-12` owns `render/page/`
and `render/templates/`.** ⭐ **Zero overlap — so on the usual test `W27` would
not gate it.**

⭐ **Merged `5c6c883` on 2026-09-10, ahead of `SF-12`, which is the outcome this argued for.** ⛔ **It gated it, because `SF-12` renders the document `SF-10` builds and
is therefore a CALLER of exactly the three sites `W27` fixes.** ⚠️ **A renderer
written against today's contract wraps a build in `except ContentError` and
swallows a `PersonalDataLeak` — R7 failing open, in new code, on the day it is
written.** ⛔ **And this board's own rule for M1 says why that is the expensive
order: *a contract that merges first becomes the shape the next tasks copy*.**

⭐ **So `W27` before `SF-12` is not a scheduling preference; it is the difference
between one migration of three sites and a fourth site minted after the fix.**

### ⭐ `W26` does NOT gate `SF-12` — measured, and recorded so it is not assumed

⛔ **`W26`'s subject is `tests/test_gate_coverage.py`, an R7 *coverage* check over
modules that decode JSON.** ⚠️ **A renderer consumes an in-memory document; it
does not read JSON.** ⭐ **And `W26` has ZERO migration — the prototype finds the
same six readers.**

⛔ **So `W26` gates *further gate work*, not `SF-12`.** ⚠️ **It still lands in this
window, for the roster reason and not the dependency reason: it is Developer 2's,
it is cheap, and leaving a not-started row open across a `Team` task is how
`W25`'s row came to be wrong twice.**

### ⭐ The fillers, and ⛔ they are fillers — both must be parked before `SF-12` starts

| Task | Owner | Why now | ⛔ **Constraint** |
|---|---|---|---|
| **`FND-09`** — the fixture-access seam | Developer 2 | ⛔ **unblocked: its gate was *"not before `SF-10` merges"*, and `SF-10` merged at `966ab30`** | ✅ **`done` — APPROVE, merged `dfccda1`** (re-measured at `ee50f77`; the row said `in-progress`). ⭐ **+56 tests, reproducing the author's `2666 → 2722` against a base that had moved +304 underneath them.** ⛔ **Ruling 43's last walk is discharged** |
| **`W28`** — `source_files()` respects the repository's ignore declaration | Developer 1 | ✅ **`done` — merged `6d65902`, 2662 / 8** | ⭐ **The set, not the count: `scanned = declared-output + kept`. ⛔ ISO's residual is 17, and 17 is `F18`, which `W28` correctly refused to answer** |
| **`FND-08`** — the document walk | Developer 2 | ✅ **`done` — APPROVE, merged `2eae7da`.** ⭐ **+47 tests, 0 dangling, `check_pointers` in `CHECKS`; 5/5 mutants killed** | ⛔ **Its finding 4 became Rulings 77–79 and `W33` below; its findings 2 and 3 were re-routed BY THE REVIEWER, because *"the PO's call"* and *"whoever adds the anchors"* are not dispositions** |

⛔ **The ordering rule this makes explicit: a `Team` task is scheduled by the LAST
developer to become free, not the first.** ⚠️ **Filling both developers' idle time
with small tasks is correct and is also how a `Team` task slips a wave** —
⭐ **so every filler above carries a park point, and a filler without one is not a
filler.**

### ⭐ The survey is confirmed — ⛔ **on the precedent, and the precedent is measured**

⭐ **`SF-10`'s survey is the reason, and it paid three ways:** it corrected `W5`'s
number from *"an 827-line port"* to **≈250 lines left**, it produced the
`derived`/`authored` seam argument the CTO rated as the read's whole value, and it
was **R14's first clean instance** — 41 line-anchored nodes answering the
structure question before a file was opened. ⛔ **The CTO's reason for it at
`FND-04` holds identically here: only somebody who knows the module's internals
can answer where it divides.**

⛔ **Deliverable is a design, not renderer code**, and the reason is the
collision-pair rule's *premise* rather than the rule: ⭐ **`SF-12` is `Team`-sized,
so its code is not authored by one person ahead of the other.** ⚠️ **But the
serial part is not the code**, and spending the gap on it is what kept the team
task intact at 1.4.

#### ⛔ Three refinements, and the first one is not optional

1. ⛔ **The survey reads `feat/SF-10-unit-builder` @ `c33f231`, NOT the release
   tip.** ⚠️ **`SF-12` renders the document `SF-10` produces, and that document —
   `unit/served.py`, 157 lines — exists only on an unmerged branch.** ⛔ **A survey
   conducted against the tip would be surveying a document that is not there**,
   and this board is exactly why: ⭐ **it said `SF-10` was *"waiting on nothing"*
   while 1,989 lines of it sat finished.** ⛔ **Nobody gets that fact from the
   board unless the row names the branch, which is why the row now does.**

2. ⛔ **`W9` is the survey's job, not the build's.** ⭐ **It has landed in `E03` as
   `SF-12`'s *first act*** — the review of `render/pageassets/surface.py`'s class
   names. ⚠️ **But *"its first act"* only binds if somebody has measured which
   names are wrong**, and the survey is the one moment that is free. ⛔ **The
   deliverable is a table: every published class name against what the port
   actually calls it, and which side moves.** ⭐ **A rename is a change to
   `surface.py` **and** the stylesheet together; inventing a second name is
   forbidden and `test_surface` already fails it.**

3. ⭐ **R13's live work is the survey's sharpest question, and the epic names only
   one instance of it.** ⛔ **`html.py:1112` is `PLAYER = """<footer id="player">`
   — triple-quoted markup in the module being ported.** ⚠️ **The epic's own rule is
   a *judgement per literal*:** the skeleton, figures, panels and section wrapper
   become template files, while loop bodies, inline wrappers and one-line
   containers stay in code, *because a template file for a closing tag removes no
   duplication and adds a hop.* ⛔ **So the survey inventories EVERY triple-quoted
   markup literal and rules on each** — ⭐ **that is `SF-12`'s equivalent of `W5`'s
   inventory, and it is the number the task is currently carrying in its head.**

⚠️ **And one question to carry, not to answer:** `SF-10`'s survey left open
whether the served document gets its own `api` version — ⛔ **no equivalent of
`UNIT_API = 3` exists.** ⭐ **`SF-12` is its consumer.** ⛔ **If `SF-10`'s build did
not mint one, `SF-12` is the second task to meet an unlocated contract, and R21
says it stops and asks rather than choosing quietly.** ⚠️ **`W11` rides here too:
if this task mints an `api` field, it is the colliding one — one line retires it.**

### ⛔ `QA-03` after `SF-12`, and the check-first rule does **not** apply

⚠️ **Worth stating, because the rule was minted one step ago and this is the first
case where it does not hold.** ⭐ **`W20` established: *a check and the code it
will judge are ordered check-first, or the check inherits a backlog it did not
cause.*** ⛔ **`QA-03` is not that kind of check.**

⭐ **The distinction is the backlog.** A repository-wide check goes red on landing
because violations already exist — ⛔ **so the cost of arriving late is real and
grows.** ⚠️ **A visual harness inherits nothing: it needs a page to look at, so it
*cannot* precede the renderer, and arriving after `SF-12` costs it nothing.**

⛔ **Recorded so the rule is not over-applied**, which is Ruling 52's whole
subject: ⭐ **the scope `W20` was argued over is *checks that accumulate a
migration*, and a harness with no migration is outside it.** ⚠️ **A rule stated
without its scope gets carried at its widest, and this one is three steps old.**

⭐ **`QA-03` still lands in M1 rather than M7, and that has not changed:** `SF-14`,
`SF-18`, `SF-24` and `QA-02` each carry an acceptance condition no unit test can
reach, ⛔ **and the precedent is not hypothetical — a highlight misclassification
italicised every string in one language, the tests passed, and only a screenshot
caught it.**

---

---

## ⛔ RULED 2026-09-10 — **§11.2 vs `source_files()`: the spec was already right, and the code never implemented it**

⭐ **Carried from round 18 as *"two definitions of one thing, one in code and one
in spec text I own."*** ⛔ **Re-measured before ruling, and the re-measurement
changed the answer: they are not two definitions. §11.2 has the only definition,
and `validate/source.py` has no definition at all.**

### The measurement, re-run 2026-09-10 on the ISO corpus @ `08e6290`

| | |
|---|---|
| `source_files()` enumerates | **159** |
| the repository tracks (same skips) | **59** |
| ⛔ **scanned but not tracked** | ⛔ **100** |
| tracked but not scanned | ✅ **0** |
| ⛔ **of the 100, `git check-ignore`-positive** | ⛔ **100 — every single one** |
| neither tracked nor ignored | ✅ **0** |
| the 100, by top directory | `graphify-out/` **96** · `.claude/` **2** · `.idea/` **2** |

⛔ **`F20` filed this as 83. It is 100 at `08e6290`, and the difference is
`graphify-out/` growing 79 → 91 → 96 in one day.** ⭐ **That is not a correction
of `F20` — it is `F20`'s own *"no fixed point"* claim, measured a third time by a
third party.**

### ⛔ The disagreement is ONE-DIRECTIONAL, and that is what makes it cheap

⭐ **`tracked but not scanned` is zero.** ⚠️ **So the framework is not missing
material; it is enumerating output** — ⛔ **and every one of the 100 files is one
the corpus's own repository has already declared is not material.**

⛔ **`F20` asked for one ruling over 100 files. It is two populations and they
need different answers:**

| Population | At `08e6290` | Whose |
|---|---|---|
| ⛔ **scanned, git-ignored generated output** | **100** | ⭐ **this ruling — one predicate, no design content** |
| ⛔ **tracked, real material the manifest's `include` does not cover** (`README.md`, `LICENSE`, `CLAUDE.md`, `docs/`, `TestCases.md`, `.gitattributes`, `.gitignore`) | **17**, per `F18` | ⛔ **NOT THIS RULING — `F18`'s third state, a schema decision under R9, the CTO's** |

⚠️ **Splitting them is the whole value.** ⛔ **Held together, `F20` reads as a hard
design problem and blocks on a schema ruling.** ⭐ **Split, the expensive-looking
half is one predicate that removes 100 of 112 findings, and the genuinely
undecided half shrinks to 17 files and stops being urgent.**

### ⭐ The ruling: **the corpus is what the corpus's own repository tracks**

⛔ **§11.2 clause 11 already says so** — *"`git status` shows no modification to
any pre-existing file except the entries its manifest declares in
`permitted_edits`"*. ⚠️ **The acceptance criterion has been git-aware since it was
written.** ⭐ **So this is not the spec and the code disagreeing; it is the code
never having implemented the definition the spec gave it**, and the spec text
needs **no** amendment.

⛔ **R1 is satisfied, and this is the argument that matters:** the framework does
**not** decide what is generated output. ⭐ **The corpus declares it, in the file
every repository already has** — and a declaration the framework reads instead of
a rule the framework knows is R1's whole shape.

⛔ **`SKIP_DIRS` is the defect in miniature, sitting inside the function.** ⚠️ **It
is five hardcoded names, and two of them — `node_modules`, `__pycache__` — are
the framework guessing at two ecosystems' ignore files.** ⭐ **A framework that
ships a list of other people's build directories is a framework that knows about
sources**, and it will be wrong for the first corpus that uses a third ecosystem.
⛔ **`.git` and `.studyforge` stay: they are the framework's own, and `archive`
is R2's.**

### ⛔ The degradation, and it may not guess

⛔ **Where the corpus root is not a git working tree, the current walk stands and
`validate` SAYS SO.** ⭐ **R2 makes an archive a shippable artifact on its own**,
so refusing a non-repository corpus is wrong — ⚠️ **but silently falling back to
a scan that over-reports by 100 files is worse, because it looks like a clean
run.** ⭐ **The precedent is in this module's own docstring: an absent source tree
is reported `Unchecked`, loudly, counted, all-or-nothing.** ⛔ **A half-applied
ignore rule is exactly the half-present source that docstring refuses.**

### ⭐ `W28` — the task

| | |
|---|---|
| **Owns** | `src/studyforge/validate/source.py` — `source_files()` and `SKIP_DIRS` |
| **Owner** | ⛔ **Developer 1.** ⚠️ **`W25`, `W26`, `W27` and `FND-08` are all Developer 2's, on one surface** |
| **Size** | ⭐ **Small.** One predicate, one fallback, `SKIP_DIRS` reduced to three |
| **When** | ⛔ **before `SF-31` (M2).** ⚠️ **`F19` also lands before `SF-31`, on the same function's blind spot** — ⭐ **and a `sibling` build's 79 generated paths are git-ignorable, so this ruling is `F19`'s cheapest half too |
| **Acceptance** | ⛔ **AMENDED 2026-09-10 — see below. Name the SET, never the COUNT** |
| **⛔ Not in scope** | ⛔ **`F18`'s 17 tracked-but-unclassified files.** ⭐ **That is the third state and it is the CTO's.** ⚠️ **A developer who "fixes" those too has answered a schema question in a bugfix** |

#### ⛔ `W28`'s Acceptance, AMENDED — ⭐ **`W22` applied to an acceptance criterion**

⛔ **The number I first wrote — *112 findings → 12* — was UNREACHABLE, and it
pointed at the trap the task's own scope note ring-fences.** ⚠️ **Measured by
PO-Integration after I scoped it, and reproduced here at `1e49225`: the include
globs (`src/*.md`, `TestCases.md`) cover ZERO of the tracked-unclassified files,
so the residual is 17, not 12.**

⛔ **The only route to 12 is widening `include` over the five root files — which
puts `README.md` in, and `README.md` becoming a unit is `F18`'s exact trap.**
⭐ **So the number asked a developer to answer the schema question the scope note
forbids them to answer.** ⚠️ **The scope note was right; the number contradicted
it, in the same table.**

⛔ **And a total could not have survived anyway.** ⭐ **`graphify-out/` has gone
79 → 91 → 96 → 99 across this wave; the corpus total 100 → 112 → 117.**
⚠️ ***"No fixed point"* is now five measurements** — ⛔ **so nothing in this
acceptance may hard-code a total.**

⭐ **Restated as a set, which is re-runnable where a total is a snapshot:**

| # | ⛔ **The criterion** | Reference reading @ `1e49225` |
|---|---|---|
| 1 | ⭐ **Every path `git check-ignore` accepts contributes ZERO findings** — the whole of `graphify-out/`, `.claude/`, `.idea/` | **103**, and ⛔ **the number is illustrative, not the criterion** |
| 2 | ⛔ **The residual is EXACTLY the tracked-but-unclassified set: `docs/studyforge/*` plus the five root files** `.gitattributes`, `.gitignore`, `CLAUDE.md`, `LICENSE`, `README.md` | **17** = 12 + 5. ⚠️ **12 today, 13 the next time that branch files a finding** |
| 3 | ⛔ **`W28` MUST NOT SHRINK the residual.** ⭐ **It is `F18`'s third state, and shrinking it is answering `F18`** | — |
| 4 | a corpus root with no `.git` reports `Unchecked`, counted, ⛔ **never silently scanned** | ⭐ **Ruling 69's one gap; already closed by this clause** |
| 5 | ⛔ **`node_modules` and `__pycache__` are GONE from `SKIP_DIRS`**, and a test asserts a corpus using neither ecosystem is unaffected | — |

⭐ **The decomposition is the assertion.** ⛔ **`117 = 103 ignored + 17 residual −
3 excluded` reconciles; a bare `117` does not, and cannot be re-run tomorrow.**
⚠️ **Their `verify.py` asserts the decomposition at `1e49225`** — ⭐ **so the
framework side and the corpus side are checking the same shape from both ends,
which is the first time that has been true.**

⛔ **Relayed to Developer 1 by the coordinator mid-task, and this row is the
version that agrees with them.**

⛔ **This does not touch spec §11.2.** ⭐ **The finding was filed as a spec/code
disagreement and the re-run dissolved the spec half** — ⚠️ **which is why a
finding is re-run before it becomes a task, and this is the second round running
that the re-run changed the shape rather than the number.**

---

## ⛔ PO-INTEGRATION ROUND 4 — routed 2026-09-10, committed `08e6290` on `release/studyforge-integration`

⭐ **The strongest round the track has produced, and the reason is structural: it
is the first that could *run* the framework rather than reason about it.**
⛔ **Everything below is measured in a real repository, and the numbers are quoted
with that ref.**

⚠️ **Two documents, and the brief I was routing from named only one.** The
reconnaissance document `docs/studyforge/reconnaissance-round-4.md` (507 lines)
carries `F18`–`F22` and `F24`; ⛔ **`F23`, `F25`, `F26`, `F27`, `Q20` and `Q22`
are in `docs/studyforge/questions-for-framework.md` (1,703 lines)**, the
register. ⭐ **Recorded because a routing that names the wrong document sends the
owner to a file that does not contain their item.**

### ⛔ The arithmetic that is the finding

| | |
|---|---|
| `Q5` ruled — a 3,863-line container became **material** | **−1** |
| round 4's reconnaissance document **committed** | **+1** |
| committing it fired the graphify hook: 79 → 91 files | **+12** |
| | ⛔ **100 → 112** |

⭐ ***Ingesting an entire fourth container improved that corpus's validity by one.
Recording the findings worsened it by thirteen.*** ⛔ **A corpus cannot write down
what is wrong with it without making it more wrong** — ⚠️ **and `W28` above is
why: 100 of the 112 are files the repository itself already ignores.**

### The routings

| Item | What it is | ⛔ **Owner** | When |
|---|---|---|---|
| **`F21`** — `origin` names a file; the fourth container's units are **regions** of one. All **17** would record the same `origin`; `check_completeness` compares each against the file's **361** headings → *"sixteen false short-reads, or a check that has to be switched off"* | ⛔ **a framework ruling.** Three shapes offered — sub-file units, a generated split, or one unit — ⭐ **and the integrator explicitly declined to pick, which is §12 working** | ⛔ **CTO** | ⛔ **gates `ISO-09`** |
| **`Q20`** — **2,106** Given/When/Then lines in **244** `gherkin` fences. *"Fluent English prose that a reader does not want read aloud as prose"* | E04 / narration + the block vocabulary. ⚠️ **Option 3 mints a manifest field, and R9 makes a field cheap now and expensive after M2** | ⛔ **CTO** | ⛔ **gates `ISO-12`**; owed **before M3** |
| **`Q22`** — ⛔ **what checks `exercises`?** | ⭐ **ANSWERED — Ruling 60:** `validate` corroborates `exercises` **against the archive, not the declaration**, symmetric, `Unchecked` when documents were refused, same rule id. ⭐ **Reproduced with a negative control** (poisoned corpus: `validate ok=True, findings=0`; the fixture checker loud) | ⛔ **RELAY TO PO-INTEGRATION** — they raised it independently and are owed the answer | ✅ **closed** |
| **`F26`** — a **rule id is an interface** and nothing states whether it is stable | ⭐ **RULED — 64** | ⛔ **RELAY** | ✅ **closed.** ⚠️ **`W27` merged at `5c6c883`, so the rule id it moves has moved: a corpus-side measurement keyed on `[manifest]` for a home path in `corpus.json` now reads `[personal-data]`** |
| **`F25`** — a record refused under R7 is reported downstream as a record **that was never declared**. Two false `Unchecked` reasons | *"Small, cheap, and on a path R7 guarantees somebody walks"* | ⛔ **CTO to rule the shape**, then a framework task | after `W27` |
| **`F27`** — ⛔ **a ruling arrives as a message and nothing propagates it.** `Q5` took **6 hand-edits across 6 artifacts and 0 checks** | ⛔ **mine — see the C6 ruling below** | ⭐ **RULED — 63 (CTO) and check 6 (mine).** ⚠️ **Two rulings on one finding is not duplication here: 63 is the mechanism, check 6 is the carrier** | ✅ |
| **`F23`** — the integration catalogue is a **permissions dead end**. **7 of 11** contributions stranded | ⛔ **mine — the catalogue is in this repository** | ⭐ **ruled here** |
| **`F18`** / **`F19`** / **`F20`** | carried from round 18 | ⛔ **`F20`'s ignore half is RULED as `W28` above.** `F18`'s third state and `F19`'s `sibling`-profile blind spot remain the CTO's | before `SF-31` (M2) |

⛔ **`F21` and `Q20` are recorded `Blocked`, not `not done`** — Q18's ruling,
applied for the first time. ⭐ **`ISO-09` and `ISO-12` keep their acceptance
conditions and name the framework item holding them shut.**

### ⛔ CORRECTION — `SK-01` finding 45 was refused **twice**, not three times

⚠️ **It was routed to me as *"refused a third time."*** ⛔ **Measured in both
documents: they say *"not answered this round either"* and *"still not answered
here, and that is now twice."*** ⭐ **The word *third* in that commit belongs to
`F27`** (*"the third distinct instance"* of C6's family) **and to `F24`/`W22`**
(*"its third violation in four rounds"*) — ⚠️ **two neighbouring threes, and the
count migrated between them in the retelling.**

⛔ **The refusal itself is CORRECT and stands for the third round running:** the
question is about the **Java** corpus, it is unowned until `E07` opens, and
⭐ **it has already been routed — to `JS-01`'s Acceptance, where the `exercises`
flag is actually written.** ⚠️ **What the integrator offers instead is the
*discriminator*, which transfers; the answer does not.**

⭐ **And the standing rule takes a scalp on its first outing: a measurement is
quoted with the ref it was taken on.** ⛔ **An inflated count in a routing brief
is the same defect as an unrefed test total** — ⚠️ **it reads as escalation, and
escalation is what gets an owner to reopen something correctly closed.**

### ⭐ `Q22` arrived from both sides independently, which is the strongest signal available

⛔ **Round 18's `PO-18/1` — framework side, reading `validate/run.py`.** ⛔ **`Q22`
— corpus side, reading `corpus.json`.** ⚠️ **Neither author saw the other's
document.** ⭐ **Two independent measurements of one hole is not two findings; it
is a confirmed one**, and it goes to the CTO as a single item with both citations.

⭐ **The `exercises` answer for ISO is checkable and already known: zero, in all
55 units.** ⛔ **So the CTO's ruling has a free negative control waiting.**

---

## ⛔ RULED 2026-09-10 — **C6's family is *a decision with no carrier*, and `F23` is unblocked by a check, not by a favour**

⛔ **Three instances now, and the integrator is right to ask for one ruling rather
than three findings:**

| Instance | The decision | What was missing |
|---|---|---|
| the **absent catalogue** (round 17) | spec §9, `SK-07` and three rulings named a file | ⛔ **nobody was obliged to create it** |
| ⛔ **`F23`** | R19 says these entries belong in the catalogue | ⛔ **nobody was obliged to read the contributions** |
| ⛔ **`F27`** | `Q5` was ruled, correctly, and was right | ⛔ **nobody was obliged to propagate it** |

⭐ **They are one shape: the decision was correct, was recorded, and had no
carrier — so it stopped at whoever happened to be reading.** ⛔ **C6 has been
stated as *"a ruling that never reaches its artifact"*, which names the symptom.
The cause is that *reaching* was somebody's goodwill and not anybody's task.**

⛔ **RULED: a decision that changes another document is not landed until a
**check** or a **named owner with a trigger** carries it there.** ⭐ **`ruled`
already names the artifact (C6); this adds the second half — it also names who
moves it and when.**

### ⭐ `F23` — the ruling, and PO-Integration changes nothing about what they do

⛔ **They keep writing contributions in their own repository.** ⚠️ **That was never
the defect** — ⭐ **the catalogue's own header already says entries are contributed
*"by whoever measured them, from either side"*, so the contribution was always
legitimate and the permission wall was never the real wall.** ⛔ **The wall was
that adoption had no owner.**

⛔ **Wave-open check 6, mine: read each consumer repository's contributions file,
adopt what qualifies against the catalogue's own *belongs / does not* table, and
RECORD A DECISION FOR WHAT DOES NOT.** ⚠️ **The recorded refusal is the half that
makes this different from goodwill** — ⭐ **a contribution silently not adopted is
`F23` again with an extra step, and the contributor cannot tell the two apart.**

⛔ **Backlog to discharge on check 6's first run: 11 contributions, 4 already
counterparted (entries 5, 6, 7, 9), 7 stranded.** ⭐ **That the 4 arrived at all is
the evidence for the ruling, not against it: they were hand-carried by whoever
was in the room, which is exactly `F27`'s mechanism and exactly as durable.**

⚠️ **And the limit, stated so it is not discovered later:** ⛔ **check 6 is a
person on a trigger, not a machine** — ⭐ **which is weaker than `W25`'s enforcer
and is the right weight for a judgement call about what belongs in a catalogue,**
⚠️ **but it is the same class of mechanism that failed three times above, so it
is on the wave-open list by name or it will fail a fourth.**

## The wave checks — ⛔ **SIX at open, and check 4 AGAIN at close**

⛔ **All six are mine.** ⭐ **Check 6 was added round 19 by `F23`'s ruling.** ⭐ **RULED 2026-09-10: check 4 runs twice — at wave-open
AND at wave-close** — ⚠️ **and the second run is the one that matters, because
the trigger check 4 exists to catch is *a task ending*, not a wave starting.**

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

## ⛔ CHECK 4 — THE FIRST CLOSE RUN, 2026-09-10 @ `75d55a6` → `40731e4`

⭐ **Ruled last round, executed here for the first time.** ⛔ **Instrument, and it
is the cheap one the ruling promised: `git log 75d55a6..` enumerates what moved,
and only those rows are re-measured.** ⚠️ **Everything that moved is the three
merges into the release tip plus four unmerged branches.**

⛔ **Verdict: the rule paid for itself on its first run.** ⭐ **Four rows wrong,
check 5 failing, and a duplicated `W`-id that no open-run could have seen —
because none of it existed when the wave opened.**

### The readings

| Row | Board said, at open | ⛔ **Measured at close** | Ref |
|---|---|---|---|
| **`SF-10`** | `done`, merged | ✅ **correct** | `966ab30` |
| **`SF-10` survey** | `done` | ✅ **correct** | `13b2857` |
| **`W25`** | ⛔ *"`todo` — NEVER STARTED. The branch is byte-identical to `HEAD`"* | ⛔ **FALSE — `in-review` → APPROVED → ✅ `done`, MERGED at third pass.** Three commits: `tools/quality/handoffs.py` **split into a package** (`__init__.py` 259 + `contract.py` 229), four test modules, **72 migrations** across `handoffs/`, plus `agent-protocol.md` and `review-rubric.md` | `feat/W25-handoff-check` @ **`f77bb7d`** — 2629 / 8 |
| **`SF-12` survey** | `in-progress` — *dispatched* | ⛔ **`in-review` at first pass → ✅ `done`, APPROVED and merged** | `1b2d993`; four escalations ruled, notably **one variant per page** |
| **`W26`** | ⛔ **TWO ROWS, TWO MEANINGS** | ⛔ **see the disambiguation below.** ⚠️ **First pass NOT STARTED → second pass `in-review` → ✅ `done`, MERGED at third pass** — ⭐ **22 mutants, 2 real survivors found and closed** | merged in `c84ca2e` |
| **`W27`** | `urgent`, no status | ⛔ **`in-review` at first pass → ✅ `done`, APPROVED and merged** — three translation sites plus two `errors.py` contracts. ⭐ **`validate/corpus.py:157`'s dead `PersonalDataLeak` arm is reachable again, reproduced independently** | merged **`5c6c883`** |
| **check 5 — `CLAUDE.md`** | ✅ at open | ⛔ **FAILS** — see below | `CLAUDE.md:102` |
| **base measurement** | `2490 / 8 @ `a7c114b`` | ⛔ **`2568 @ 40731e4` → `2570 @ 1b2d993` → `2649 @ c84ca2e`.** ⚠️ **THREE times in one round** | tip |

### ⛔ `W25` is the mirror of `W25`, and that is not a typo

⚠️ **Last round check 4 caught `W25` recorded `in-progress` against a branch
containing nothing, and corrected it to *"NEVER STARTED — byte-identical to
`HEAD`"*.** ⛔ **One wave later that sentence is false in the other direction**,
and the row now understates by an entire package with a migration.

⭐ **This is the strongest possible argument for the close run, because it is the
SAME ROW failing the SAME CHECK in the OPPOSITE DIRECTION within one wave.**
⛔ **A status is not a property of a task; it is a property of a task *at a
moment*** — and *"byte-identical to `HEAD`"* is the worst form of it, because it
names a **moving** reference. ⚠️ **`HEAD` moved. The sentence did not, and it
stopped being true without changing a character.**

⛔ **Rule, and it is the ref rule biting a row rather than a number: a status
that compares against `HEAD`, *"the tip"* or *"today"* is unfalsifiable a day
later.** ⭐ **Name the commit both sides were at.** ⚠️ **`fix/W26-gate-tell` is
recorded above as byte-identical to `40731e4`, not to `HEAD`, for exactly this
reason — and it will still be checkable next round.**

### ⭐ Rulings 59–65 arrived mid-round — what each changes for this board

| # | What it settles | ⛔ **What it changes here** |
|---|---|---|
| **59** | ⛔ **the legacy finding-number ceiling is 62, not 58** | ⛔ **`SF-10` minted 59–62 on a branch before the rule existed, and pinning 58 would red-line a merged record.** ⭐ **Developer 2 was right.** ⛔ **The collision is live on 61 AND 62** — `PO-2026-09-10-round18.md`'s own *For dependents* cited both meanings **four words apart**. ⭐ **Remedied by renumbering `po-round18` to `PO-18/1..5`, on this branch; `SF-10` is NOT touched** |
| **60** | ⛔ **`validate` corroborates `exercises` against the ARCHIVE, not the declaration** | ⭐ **Closes `PO-18/1` and PO-Integration's `Q22` in one stroke** — ⛔ **and the relay is owed, because they raised it independently from the corpus side** |
| **61** | ⭐ **Ruling 53's two artifacts are a rule and its worked example** | see the check 3 table |
| **62** | `W25/7` accepted | rides with `W25` |
| **63** | ⛔ **`F27`** — a ruling needs a carrier | ⭐ **pairs with wave check 6**; 63 is the mechanism, check 6 is the carrier |
| **64** | ⛔ **`F26`** — rule-id stability | ⛔ **relay: `W27` merged, so `[manifest]` → `[personal-data]` for a home path in `corpus.json` has ALREADY happened** |
| **65** | §8a's marker spelling | ⭐ **It caught its own author first — the CTO's handoff measured 17 findings against 8 real ones.** ⚠️ **Third instance this wave of a check finding its author** |

### ⭐ Rulings 66–69 — two ratify mine, one narrows it, one is placed here

| # | | ⛔ **What it changes** |
|---|---|---|
| **68** | ⭐ **RATIFIES *one minter per id space*, NARROWED** | ⛔ **Minting is about the ID, never the authority to decide.** ⭐ **C6 locates a ruling by its ARTIFACT, so an UNNUMBERED RULING STILL BINDS** — ⚠️ **without that clause every routing would wait on a CTO round, which is the opposite of what the rule is for.** ⛔ **My W26 ruling above must be read with it: the CTO was never asked to stop routing, only to stop numbering** |
| **69** | ⭐ **needs no amendment** | the one gap the CTO checked — a corpus root with no `.git` — ⭐ **is already closed by `W28`'s criterion 4** |
| **66** | ⛔ **`W25/8`'s remedy REFUSED as a no-op** | ⭐ **The shipped message already interpolates the marker, the 10-line window and the closed set.** ⚠️ **The survey's author simply wrote before the check existed.** ⛔ **Recorded so nobody spends a commit on an approved surface for a gap that is not there** |
| **67** | ⛔ **`W26/1`: the root is correct — ASSERT THE BOUND, DO NOT EXTEND IT** | ⭐ **Three trees under three gates, not one hole.** ⛔ **Extending is refused by Ruling 31, and `tests/fixture_checks/corpus.py` stays ungated under Ruling 60's oracle-independence.** ⛔ **The defect is a bound asserted nowhere — and placing it is mine: see `W29`** |

### ⭐ `W29` — Ruling 67's bound, placed

| | |
|---|---|
| **What** | ⛔ **One constant naming the three gated trees, plus the docstring sentence that says why the fourth is ungated.** ⭐ **Not an extension — an assertion that the existing bound is the intended one** |
| **Owner** | **Developer 2** — `tests/test_gate_coverage.py` is the surface they just finished in `W26` |
| **Size** | ⭐ **Smallest on the board.** One constant, one sentence, one test |
| **When** | ⛔ **with or immediately after `FND-08`**, same author, same wave |
| **Acceptance** | the constant names the three trees · ⛔ **the docstring states why `tests/fixture_checks/corpus.py` is ungated, citing Ruling 60's oracle-independence** · a test fails if a fourth tree appears unnamed |
| **⛔ Not in scope** | ⛔ **extending the gate to a fourth tree.** ⚠️ **Ruling 31 refuses it, and `W26/1` reads as if it were the fix** |

### ⛔ Three findings from CTO round 20, carried

- ⛔ **`CTO-20-2` — `W26/1`'s *"three"* is a count over an UNSTATED SET.** ⚠️ **The
  raw tell finds 20 outside `src/`.** ⭐ **A recurrence of `CTO-19-8`, and the
  second time this wave that a bare count turned out to be a fact about its
  instrument** — ⛔ **which is `W29`'s whole reason for existing: name the set.**
- **`CTO-20-3`** — `W26`'s handoff says 471 lines; measured **478**.
- ⛔ **`CTO-20-5` — `po-round19` moved twice mid-review, THIRD ROUND RUNNING.**
  ⚠️ **Accepted as a real cost, not deflected.** ⭐ **The mitigation is the one
  already in force — every cell names its ref, so a moved branch is *visibly*
  superseded rather than silently wrong** — ⛔ **but it does not make the reviewer's
  re-read free, and this row exists so the next PO does not treat it as solved.**

⛔ **MERGE ORDER, proved with a negative control: `po-round19` BEFORE
`cto-round19`, always.** ⚠️ **Withholding this branch gives 3 failed, floor 1
finding, merge exit 0, no conflict** — ⭐ **the fifth instance of the trial-merge
clause, and the second caught before the merge.**

⛔ **Also approved as written: `FND-08` and `FND-09`, with all five prices
reproduced, and walk 4's refusal STANDS.** ⭐ **A refusal surviving an
independent re-measurement is the strongest form a scoping decision takes.**

### ⛔ THE CLOSE RUN WENT STALE WHILE IT WAS BEING RUN — second pass, tip `1b2d993`

⚠️ **The CTO ruled and the coordinator merged while this section was being
written.** ⛔ **Four of its own readings were superseded before they were
committed:** `W27` and the `SF-12` survey **merged**, `W26` **started**
(`283ae90`), `W25` was **APPROVED**, and the base moved `2568` → `2570`.

⛔ **This is the third consecutive round in which the board's own status work
went stale mid-round**, and last round's handoff diagnosed it happening to its
author in the paragraph diagnosing it. ⭐ **So the close run is not the fix —
it is the same instrument at a better moment, and it has the same failure
mode.**

⛔ **What actually holds, and it is the only thing that has held all three
rounds: every cell names its ref.** ⚠️ **A row that says `in-review @ 655b527`
is not *wrong* once `655b527` merges — it is a true statement about a commit,
and the reader can see it is superseded.** ⛔ **A row that says `in-review` is
wrong the moment it changes and gives the reader nothing to notice it with.**

⭐ **So the rule earns its keep twice over: it does not stop staleness, it makes
staleness VISIBLE — and the first-pass readings above are kept, not overwritten,
for exactly that reason.**

### ⛔ Check 5 FAILED — `CLAUDE.md` contradicted itself in adjacent paragraphs

⚠️ **`:102` said *"In flight: M1 step 1.4 — `SF-10`"*. `:105` said `SF-10` was
done and step 1.4 closed.** ⛔ **The correction had been APPENDED BELOW the stale
sentence instead of replacing it.**

⭐ **Three sentences further on, that same file says a stale line there
*"misdirects every agent that starts."*** ⛔ **It was misdirecting them, in the
paragraph that says so** — which is check 3's `landed in` column and check 4's own
diagnosing-paragraph defect, now three times in two rounds.

⛔ **The generalisation, and it is broader than `CLAUDE.md`: a correction that
leaves the original standing is not a correction, it is a second copy** —
⚠️ **and the reader takes the first sentence that answers their question, which is
the stale one.** ⭐ **Corrected by replacement, and the section now points at this
board for what is open in the step rather than restating it.**

---

## ⛔ CHECK 4 — THE SECOND CLOSE RUN, 2026-09-10 @ `c84ca2e` → `2926dc2`

⭐ **Instrument, unchanged and still the cheap one: `git log c84ca2e..` enumerates
what moved, and only the rows those merges touch are re-measured.** ⛔ **Four
merges** — `W28` (`6d65902`), `po-round19` (`61297a9`), `cto-round19` (`0817b66`),
`cto-round21` (`2926dc2`) — ⭐ **plus two branches dispatched during the wave.**

⛔ **Verdict: two stale rows, both understating, and ZERO of the failure that
made the first run famous.** ⚠️ **Nothing went stale *while* this run was
executed** — ⭐ **the first time in four rounds** — and the reason is measurable
rather than lucky: **no branch was awaiting a verdict when it started.** ⛔ **So
the fix for mid-run staleness was never the instrument; it was running it at a
moment with no open review.**

### The readings

| Row | Board said, before this run | ⛔ **Measured at close** | Ref |
|---|---|---|---|
| **`W28`** | *filler, Developer 1, small* | ✅ **`done`, merged** — ⭐ **+13 tests, and `SKIP_DIRS` lost its two guessed ecosystem names** | `6d65902`; 2662 / 8 |
| **`W25`** | ⛔ *"`in-review` — `feat/W25-handoff-check` @ `f77bb7d`"* | ⛔ **STALE — `done`, merged.** ⚠️ **Third reading of this one row in three runs** | `2a272a5`, in `c84ca2e` |
| **`W26`** | `in-review` @ `283ae90` | ✅ **`done`, merged** | in `c84ca2e` |
| **`SF-12` survey** | ⛔ *"`in-review` @ `afba232`, 2490 / 8"* | ⛔ **STALE — `done`, APPROVED and merged** | `1b2d993` |
| **`SF-12`** | *`unblocked`, waiting on the roster* | ⏳ **`in-progress` — DISPATCHED to Developer 1.** ⛔ **`feat/SF-12-renderer` is byte-identical to `2926dc2`, clean tree: nothing has landed yet AT THAT REF** | `feat/SF-12-renderer` @ `2926dc2` |
| **`W29`** | *Developer 2, with or after `FND-08`* | ⏳ **`in-progress` — DISPATCHED, and ⛔ ahead of `FND-08` rather than after it.** `fix/W29-gate-bound` byte-identical to `2926dc2`, clean tree. ⭐ **No `GATED_TREES`-shaped constant exists in `src/` or `tests/` yet — measured, not assumed** | `fix/W29-gate-bound` @ `2926dc2` |
| **`FND-08` / `FND-09`** | *fillers, must be `done` or parked* | ⛔ **PARKED — never started.** ⚠️ **`git log --all --grep` finds no commit for either, and neither has a branch** | `2926dc2` |
| **rulings 70–73 reached their artifact** | *pending on `chore/cto-round21`* | ✅ **CARRIED — verified in the file, not in the handoff:** `review-rubric.md` §4c (70, 71), §8a (73), §9 (72) | `2926dc2` |
| **check 5 — `CLAUDE.md`** | ⛔ **FAILED at round 19's close** | ✅ **PASSES — `:102` reads *"steps 1.1–1.4 closed, in flight step 1.5"* and points at this board for what is open in it** | `CLAUDE.md:102` @ `2926dc2` |
| **base measurement** | `2649 / 8 @ c84ca2e` | ⛔ **`2662 / 8 @ `2926dc2``**, floor clean, all 8 skips named | tip |

### ⛔ The finding this run produced, and it is about a **park point** rather than a status

⚠️ **`FND-08` and `FND-09` were given park points precisely so a `Team` task could
start, and both were discharged by never starting.** ⛔ **That is a legitimate
discharge and it is also indistinguishable, in the row as written, from work in
flight.** ⭐ **So a filler's row now carries the outcome — `done` or `PARKED @
<ref>` — because *"must be parked before `SF-12`"* describes an obligation and
records no result.**

⛔ **And the sharper half: both fillers are Developer 1's and Developer 2's
*first* items and neither was touched, while `W28` and `W29` — minted after them —
were.** ⚠️ **A filler is scheduled by whoever is free, and what is actually
scheduled is whatever was minted most recently**, which is how `FND-09` has now
waited two waves behind three newer rows. ⭐ **Not a defect to fix this round; a
cost to name, and it is named on `FND-09`'s row.**

---

## ⭐ CHECK 6 — SECOND RUN: **16 contributions, not 11, and every one is now dispositioned**

⛔ **Ruled last round, run for the second time here, and the backlog it inherited
had grown by five while it waited.** ⭐ **Measured on `../ISO-8583-jPOS-tutorial`
@ `1e49225` against `docs/integration-catalogue.md` @ `2926dc2`.**

| | first run (round 19) | ⛔ **this run** |
|---|---|---|
| contributions | 11 | ⛔ **16** |
| already counterparted | 4 | ⭐ **6** — the 4, plus two whose material had landed inside existing entries |
| ⛔ **stranded** | **7** | ⛔ **10 at open, 0 at close** |
| adopted here | — | ⭐ **8 new entries, 11–18** |
| ⛔ **deferred, with a trigger** | — | ⛔ **2** |

⭐ **Adopted as entries 11–18:** the filename hierarchy is a redundant encoding ·
a markup scan cannot tell a document's HTML from a fenced language · mirrored
series collide on title-derived slugs · a report decays, assert instead · an
ignore rule is verified in both directions and the exposure is at index time ·
*complete at the reading floor* needs the never-used surface listed · neither the
verb nor the pronoun decides runnability · an enumeration rule meets a
content-addressed cache.

### ⛔ The two deferrals are the point of the check, not an exception to it

⛔ **`F18`'s three states and `F19`'s interleaved-placement limit are both open
with the CTO.** ⭐ **The catalogue is *for what stays true after the framework is
right*, and both contributions ask whether the framework is right** — ⚠️ **so
adopting them would publish a limit the framework may be about to remove, which is
the one failure a catalogue cannot recover from.** ⛔ **Deferral is a decision and
it carries a trigger: the PO adopts each the day its ruling lands, in whichever
direction it lands.**

### ⭐ What the second run found that the first could not

- ⛔ **The `F2` correction was reported stranded and is not.** ⚠️ **Measured rather
  than inherited: spec §1's C3 already carries the retraction and `E02` carries it
  too.** ⭐ **What was missing was its *catalogue-shaped* half — the method error
  rather than the number — and that is now entry 12.** ⛔ **A contribution can be
  "stranded" in one document while its content is landed in three others**, and
  only a run that opens the destination can tell.
- ⛔ **`F8` is a fixture, not a catalogue entry, and adopting it as an entry would
  have been the wrong destination.** ⭐ **A contents document listing 36 of 38 units
  as list items and 2 as headings produces a parser that reads 36, emits 36, and
  raises nothing** — ⚠️ **the cleanest real instance of *a plausible short parse*
  this project has, written by an author who was not trying to break anything.**
  ⛔ **Carried as `W32`.**
- ⚠️ **Two contributions were already carried and neither contributor could have
  known**: entry 5's closing paragraph absorbed one, and entry 8's correction
  banner **is** the other. ⭐ **Recorded as *already carried* rather than left
  silent — silence is what makes adoption and neglect look identical.**

---

## ⛔ CHECK 4 — THE FOURTH CLOSE RUN, 2026-09-10 @ `90dc580` → `ee50f77`

⭐ **Instrument, unchanged: `git log 90dc580..ee50f77` enumerates what moved, and
only the rows those merges touch are re-measured** — ⛔ **plus the complement,
which is what caught the worst reading below: `git merge-base --is-ancestor` over
EVERY branch in the repository, so a branch that moved without merging is
enumerated too.**

⛔ **Four merges on release** — `po-round21` (`86614c4`), `FND-09` (`dfccda1`),
CTO round 24 (`f06c805`), and the coordinator's landing merge (`ee50f77`).
⚠️ **And FOUR branches ahead of the tip that no merge enumerates.**

### ⛔ THE VERDICT — **the review queue was NOT empty, and the run drifted in three places. `PO-20/3`'s FOURTH data point, and the first NEGATIVE one.**

⭐ **Runs 2 and 3 both had an empty queue and both drifted nowhere; round 21
promoted that to the scheduling rule for check 4 at three data points.** ⛔ **This
run is the first with a NON-empty queue, and it is the first since run 1 to find
rows that went stale during the wave rather than before it.** ⚠️ **Three
confirmations of *"empty queue → no drift"* are a correlation; ⭐ **one
observation of *"queue not empty → drift"* is what makes it a rule**, and it is
the data point the previous three could not supply.

### The readings

| Row | Board said, before this run | ⛔ **Measured at close** | Ref |
|---|---|---|---|
| **`FND-09`** | ⏳ *"`in-progress` — `feat/FND-09-sweep`, dispatched at `90dc580`"* | ⛔ **STALE — ✅ `done`, APPROVED and merged.** ⭐ **+56, reproducing the author's `2666 → 2722` against a base that had moved +304 underneath them** | merged `dfccda1` |
| **`po-round21`** | *unmerged, docs-only* | ✅ **merged, and it moved nothing**, as it claimed | `86614c4` |
| **rulings 81–83** | *pending on `chore/cto-round24`* | ✅ **CARRIED and on release** | `160978d`, in `ee50f77` |
| ⛔ **`W33`** | ⛔ *"`todo` — FIRST of the three"* | ⛔ **WRONG IN THE WORST DIRECTION: `done`, APPROVED — and NOT ON RELEASE.** ⭐ **`feat/ruling-78-lint-notice` @ `5938d48`, merged with an APPROVE into `chore/cto-round25` @ `85f0990`.** ⚠️ **`release/m0-foundations` has not moved** | `85f0990`; `PO-22/4` |
| **`W30`, `W31`** | `todo`, both | ⛔ **STALE — `in-progress`.** `fix/W30-W31` @ `a67f3cd`: one commit, 5 files, 208 insertions, both rows on one branch | `a67f3cd` |
| **`QA-03`** | ⏳ *"`in-progress` — dispatched at `90dc580`"* | ⏳ **`in-review` — `feat/QA-03-visual` @ `d2dc2c4`, with the CTO.** ⭐ **86 tests, 2203 lines, 17 modules** | `d2dc2c4` |
| **`W32`** | *`todo`, with or after `FND-09`* | ✅ **correct, and its gate has now cleared** | `dfccda1` |
| **check 5 — `CLAUDE.md`** | ✅ passed at round 21's close | ✅ **PASSES AGAIN — SECOND consecutive pass.** ⭐ *"M1 steps 1.1–1.4 [closed]. In flight: M1 step 1.5"*, and it delegates the contents to this board | `CLAUDE.md` @ `ee50f77` |
| **base measurement** | `2970 / 8 @ 90dc580` | ⛔ **`3026 / 8 @ `ee50f77``**, floor clean, lint pinned green | tip |

### ⛔ The finding this run produced — **an APPROVED branch merged into the reviewer's OWN branch, twice in consecutive rounds**

⚠️ **Round 24 did it with `FND-09` and `po-round21`: both were reported merged,
both were merged into `chore/cto-round24`, and `release/m0-foundations` did not
move until the coordinator merged the round branch.** ⛔ **Round 25 has done it
again, with `W33` on `chore/cto-round25` @ `85f0990`.**

⛔ **Once is an accident; twice in consecutive rounds is the process.** ⚠️ **The
verdict is real, the work is finished, and the tree does not carry it** — ⭐ **so
every agent that measures `release/m0-foundations` measures a tree missing
approved work, and every base quoted from it understates.**

⭐ **Not mine to fix — I do not merge to release — and it is `PO-22/4`, routed to
the coordinator.** ⛔ **The instrument is one line and it already exists in the
other direction:** `CTO-24/6` runs `git merge-base --is-ancestor <branch> HEAD`
against the round branch; ⚠️ **the check that was missing is the same line against
`release/m0-foundations`.**

⭐ **And the general form, which is check 4's own subject:** ⛔ **a merge is not a
status. *"Merged"* names a destination, and a report that does not name it is
unfalsifiable** — ⚠️ **which is the ref rule (Ruling 72's neighbour) biting a verb
instead of a number.**

---

## ⭐ CHECK 6 — FOURTH RUN: **nothing new, and the reading now carries a ref**

⛔ **The instrument: read each consumer repository's contributions file, adopt
what qualifies, and RECORD A DECISION for what does not.**

| Repository | ⛔ **Measured @ `ee50f77`** |
|---|---|
| **`ISO-8583-jPOS-tutorial`** | ⭐ **`docs/studyforge/catalogue-contributions.md` — 16 entries, last written `4351f28` (2026-09-10, *"Round 4"*).** ⛔ **UNCHANGED since the second run's disposition. Nothing to adopt and nothing to refuse** |
| **`Claude-senior-java-engineer`** | ⛔ **No contributions file exists.** ⭐ **Stated rather than skipped: check 6 reads *each* consumer repository, and only one of the two has ever written one** |

⭐ **The improvement this run makes is small and it is the only one available: the
reading now carries a ref.** ⚠️ **Runs 2 and 3 recorded *"all 16 dispositioned"*
and *"unchanged from round 20"* — ⛔ **neither named the commit, so neither could
be distinguished from a run that did not open the file.** ⭐ **`4351f28` can be.**

---

## ⛔ RULINGS 70–73, CARRIED — and one of them is a task

| # | What binds here | ⛔ **What changes on this board** |
|---|---|---|
| **70** | a mutant sweep states its environment, its purge, and that the unmutated **baseline survived** | ⛔ **Any row whose acceptance names a sweep inherits this.** ⭐ **`W26` and `W25` were re-measured by the CTO under it and both stood** |
| **71** | ⛔ **suspect evidence is RE-MEASURED, not scheduled, when measuring is cheaper than filing** | ⛔ **This is a rule against my own reflex.** ⚠️ **The CTO's four pytest runs cost less than the row I would have written**, and a row would have carried the doubt for a wave. ⭐ **Applied here: the `W29` constant's absence was measured, not asked about** |
| **72** | ⛔ **an acceptance condition is a DECOMPOSITION, never a total** | ⛔ **It routes `W28/2` and it routes M1's close conditions below, which are its first deliberate instance.** ⭐ **`W28`'s own row already carries the identity form** |
| **73** | ⭐ **§8a can be documented in the directory it polices** — fence, table cell and prose-with-a-lead-word already do not count | ⛔ **`PO-19/7` was TOO BROAD and the scaling worry is answered.** ⚠️ **The rubric's hand grep over-counts exactly the documents that discuss §8a; the shipped reader does not** |

### ⭐ Three rows minted from the queue — `W30`, `W31`, `W32`

| | `W30` | `W31` | `W32` |
|---|---|---|---|
| **What** | ⛔ **`PYTHONPYCACHEPREFIX` in the dev image**, pointing outside `/workspace` | ⛔ **`DOCUMENT_KINDS`' sentences name two roles where three produce these documents** | ⭐ **The mixed-form contents fixture — a plausible short parse from real material** |
| **From** | `CTO-21/1` | `PO-19/5` | check 6, the `F8` donation |
| **Owner** | framework agent | framework agent | framework agent |
| **Size** | ⭐ one `ENV` line + a test in `tests/docker/test_dev_image.py` | ⭐ **one word in a docstring** | small — a fixture plus the assertion that the reader does not short-read it |
| **When** | ⛔ **not urgent** — Ruling 70's purge covers the same hole procedurally today | ⛔ **NOW UNBLOCKED — `W25` merged, so `DOCUMENT_KINDS` is no longer a surface under review** | with or after `FND-09` — same fixture tree |
| **Acceptance** | a container run reads **no** `.pyc` from the bind-mounted checkout; the test proves the redirect in **both** directions, per Ruling 70's negative-control clause | `ruling record` admits a PO round; ⛔ **no new kind is minted** | a contents document whose entries are **mixed list items and headings** parses to the full count, and the fixture fails if a parser reads only the list form |

⛔ **`W30`'s finding is sharper than its size, and the board carries the finding
rather than the line:** ⭐ **the pinned image sets `PYTHONDONTWRITEBYTECODE=1` and
therefore CANNOT CREATE the taint** — ⛔ **but the checkout is bind-mounted, so a
container run read a stale `.pyc` that a HOST run had left behind.** ⚠️ **Ruling
40 is necessary and not sufficient**, and that sentence is the reason `W30`
exists at all.

### ⭐ `CTO-21/3` — ACCEPTED AS A COST, with a trigger rather than a row

⛔ **`W28`'s `except OSError, subprocess.SubprocessError:` is legal only since
PEP 758 in Python 3.14, which this project pins.** ⚠️ **It is in range, it passes
`ruff`, and it reads as a Python 2 error to every future reviewer** — ⭐ **the CTO
stopped on it, checked, and recorded the stop so the next reviewer would not
repeat it.**

⛔ **No row.** ⭐ **Rewriting merged-quality code over taste is not a reviewer's
call and it is not a PO's either**, and the parenthesised form buys two characters
of familiarity against one commit against an approved surface. ⛔ **The trigger, so
this is a decision and not a shrug: if a SECOND reviewer stops on it, it becomes a
row** — ⚠️ **at that point the cost is measured (two readers) rather than
predicted (one), and `CTO-21/3`'s own argument flips.**

---

## ⛔ RULED 2026-09-10 — **the page chrome has an owner, and it does NOT block M1**

⛔ **The disagreement, and both sides were right.** `SF-11`'s finding 3 assigns
*"masthead and layout grid and the navigation rail"* to `SF-12`. `SF-12/5`
answers that `reading.css` declares its own scope (*"Masthead, navigation rail,
narration player, progress controls and practice panels are NOT here"*) and that
`test_surface` asserts the published set and the stylesheet's set are **equal in
both directions** — so one new chrome class costs `render/assets/<part>.css`, an
entry in `STYLE_PARTS` and an entry in `SURFACE_HOOKS`: ⛔ **three files in two
packages `SF-12` does not own.** ⭐ **The markup shipped and the rules did not**
(`CTO-23/6`).

### ⭐ The ownership — ruled, and it follows the CTO's

⛔ **The markup is `SF-12`'s and is DONE. The rules belong with `reading.css`,
because a class name with no rule is not styling.** ⭐ **So the chrome's
stylesheet is a task against `render/assets/` + `render/pageassets/`, not a
re-opening of `SF-12`.** It is minted below as **`SF-34`**.

### ⛔ And the part the CTO routed to me: **it does not block M1**

⚠️ **The CTO wrote *"M1 cannot close on that condition today."* I rule the other
way, and the reason is in the decomposition's own second half rather than in
taste.**

| # | The argument | ⛔ **Why it is a measurement and not a preference** |
|---|---|---|
| **1** | ⛔ **M1 explicitly does NOT require cross-unit navigation or a contents page** — it says so in the *does not require* half below | ⭐ **The outline and the between-units bar ARE that chrome.** Styling them at M1 means writing rules for regions whose targets M1 refuses to build |
| **2** | ⭐ **The masthead is the only chrome region M1's single page actually populates, and it is legible unstyled** — a `<header>` with a heading in browser defaults | ⛔ **Rows 4 and 5 are what *"with styles"* decomposes into: references RESOLVE, and highlighting is BOUNDED.** Neither is a claim about polish |
| **3** | ⭐ **`SF-12` addressed the chrome by element, `aria-label` and `data-*` ONLY** | ⛔ **Measured by the author: every class the two goldens carry is in `SURFACE_CLASSES \| SURFACE_HOOKS \| {language-java}`, and the `<header>`, `<nav>` and `<ol>` carry none.** ⭐ **So a chrome part added later needs NO page change and NO re-render — the cost of deciding late is bounded, which is the condition under which a PO defers instead of blocking** |
| **4** | ⛔ **`Q18` and Ruling 72 bind me here** | ⚠️ **Adding a tenth row at close, for regions M1 declines to populate, converts a reachable finish line into one that recedes** — ⭐ **which is the exact failure `Q18` was ruled against** |

### ⛔ What I am NOT doing is deferring it silently — row 8 gains one clause, and it is the trigger

⭐ **`QA-03`'s screenshot is the instrument, and its author was told to CAPTURE
the chrome, not fix it.** ⛔ **Close condition 8 now requires the screenshot to
RECORD the chrome's unstyled appearance as a named observation.** ⚠️ **That costs
nothing and it is the whole difference between *we decided* and *nobody looked*.**

⛔ **The trigger, so this is a decision and not a hope:** ⭐ **if the screenshot
shows the unstyled chrome makes the reading column unreadable — the outline
colliding with it, the masthead swallowing the page, the between-units bar
indistinguishable from body text — then row 8 FAILS, `SF-34` is pulled into M1,
and this ruling is reversed on evidence rather than argued again.**
⚠️ **A legible-but-plain chrome is a PASS.** ⛔ **Legibility is the bar, not
polish, and naming the bar in advance is what stops row 8 becoming a taste
verdict.**

### ⭐ `SF-34` — MINTED. Page chrome styles

| | |
|---|---|
| **Id** | ⛔ **`SF-34`** — the SF high-water mark was `SF-33`; the project goes 86 tasks → **87** |
| **Epic / milestone** | `E03` · ⛔ **M2, step 2.4** |
| **Depends on** | `SF-11`, `SF-12` (both done) |
| **Owns** | ⛔ **`render/assets/chrome.css` (new).** ⚠️ **Plus two ADDITIVE edits outside it — one entry in `STYLE_PARTS` (`pageassets/bundle.py`) and one in `SURFACE_HOOKS` (`pageassets/surface.py`).** ⭐ **Stated on the row so the next author does not stall on the same boundary `SF-11` and `SF-12` stalled on** |
| **Also, in the SAME change** | ⭐ **`CTO-23/6`'s second half: move the two `<nav>` regions out of Python f-strings into `render/templates/`.** ⛔ **They carry a product string (`Contents`) in code, and § 5's one-line-container exception is doing more work there than anywhere else in the page** |
| ⛔ **Why 2.4 and not 2.1** | ⭐ **Two of the three regions get their CONTENT from `SF-13`/`SF-14`/`SF-15`, and `SF-15` is 2.4.** ⛔ **Styling a region before its content exists is `SF-11`'s own finding-3 warning — *the palette defines tokens nothing paints with* — repeated one layer up.** ⭐ **`SF-34` is where the unit page's share of that leniency is claimed** |
| ⚠️ **Pull-forward trigger** | ⛔ **`QA-03`'s screenshot fails row 8's legibility bar → `SF-34` moves into M1 and M1 waits on it** — ⭐ **FIRED AND DID NOT TRIP, [ruled below](#ruled-2026-09-10-m1s-row-8-passes-and-one-third-of-the-bar-was-unfalsifiable). `SF-34` stays at M2 step 2.4** |

---

## ⛔ RULED 2026-09-10 — **M1's row 8 PASSES, and one third of the bar was unfalsifiable**

⛔ **Ruling 82(2): the observer is not the author of the task the row gates.**
⭐ **`QA-03`'s author was told to CAPTURE and DESCRIBE, and they did exactly that
and refused the verdict.** ⛔ **The bar was written by the PO of round 21; it is
judged here, by the PO of round 22, and by nobody else.**

⭐ **THE BAR, verbatim from the ruling above:** row 8 fails *"if the screenshot
shows the unstyled chrome makes the reading column unreadable — the outline
colliding with it, the masthead swallowing the page, the between-units bar
indistinguishable from body text."* ⚠️ **A legible-but-plain chrome is a PASS.
Legibility is the bar, not polish.**

### ⛔ Three named symptoms, scored one at a time — and RE-MEASURED FROM THE TREE

⚠️ **The evidence is `QA-03`'s captures; the verdict is not taken from the
handoff.** ⭐ **Every reading below was re-derived at `ee50f77` from the goldens
and from the stylesheets themselves**, because a symptom read off a picture and a
symptom read off a rule are different measurements — ⛔ **and one of the three
came back differently when the rule was read** (`PO-22/1`).

| # | The named symptom | ⛔ **Verdict** | ⭐ **What says so, measured at `ee50f77`** |
|---|---|---|---|
| **1** | *"the outline colliding with [the reading column]"* | ✅ **ABSENT** | ⛔ **NOT MERELY UNSEEN — NOT EXPRESSIBLE.** ⭐ **No bundled stylesheet contains a `header` or a `nav` selector at all.** `STYLE_PARTS` is `reset · palette · focus · reading · code-highlight · plyr · video-player`, and the only element rules in the first-party four are `body`, `h1`, `h2`–`h6`, `p`, `a` and `main p, main li`. ⚠️ **Nothing positions, floats or overlaps anything**: `<nav aria-label="Outline">` is a normal-flow block that PRECEDES `<main>` in document order. ⛔ **A collision needs a rule, and no rule exists** |
| **2** | *"the masthead swallowing the page"* | ✅ **ABSENT — and the masthead is better dressed than the capture reported** | ⭐ **`<header>` holds one `<h1>` and one `<p>`.** ⛔ **`h1` IS styled — `reading.css:26`, `1.9rem` in `var(--font-ui)` — and NOTHING later in `STYLE_PARTS` overrides it** (`h1` appears in no other bundled sheet, vendored ones included). `p` takes `reading.css:37`; `a` takes `--accent`; all of it is painted on `body`'s `--bg`/`--fg`. ⚠️ **Two lines of the page's OWN type at the top of the page** — ⛔ **`PO-22/1`: the capture reported *"the browser's default heading size"*, and the stylesheet says otherwise** |
| **3** | *"the between-units bar indistinguishable from body text"* | ⛔ **VOID — UNFALSIFIABLE AT THIS REF** | ⭐ **Confirmed independently, three ways:** `navigation.between_units(None)` returns `""`; ⛔ **no caller anywhere in `src/` passes `links=`**; and neither golden contains the string `aria-label="Between units"`. ⚠️ **Nothing computes a reading order before `SF-13`.** ⛔ **It is not legible and it is not illegible. It is absent** |

### ⛔ What I do with the third — because scoring it EITHER way would be dishonest

⚠️ **Scoring it PASS asserts a reading nobody could have taken. Scoring it FAIL
blocks M1 on a region M1 explicitly declines to populate.** ⛔ **And dropping it
silently is `PO-21/1`'s own warning turned on its author: a decomposition can
narrow the promise without anybody noticing.**

⭐ **So it is VOIDED, and voiding is RECORDED and CARRIED:**

| | |
|---|---|
| ⛔ **Struck** | ⭐ **Symptom 3 is struck from row 8's bar.** It was stated against a region the ref does not populate, which is precisely what **Ruling 82(1)** forbids — ⚠️ **and 82(1) landed one round AFTER the bar was written, so this is the rule catching its own predecessor** |
| ⭐ **Re-homed, not deleted** | ⛔ **The bar travels to the artifact: `SF-13` is the task that first computes a reading order, and `SF-34` is the task that writes the bar's rules.** ⭐ **Both carry the clause below, so the promise is kept by whoever can first be held to it** |
| ⛔ **The general form** | ⭐ **A named symptom is scored ONLY against a region the ref populates. One that is absent is VOID — and a VOID symptom is RE-HOMED onto the row that first populates the region, or the bar has silently narrowed.** ⚠️ **82(1) says how to STATE a bar; this says what to do when it was already stated wrongly** |

### ⭐ THE VERDICT — row 8 **PASSES**

⛔ **Row 8's own condition is *"a human-visible check ran — the page was opened
over `file://` and the result RECORDED"*, and it is discharged:** both goldens
opened over `file://` in **Google Chrome 149.0.7827.200**, captured at 1280×900
in light and dark, ⭐ **and the chrome recorded as a named observation, which is
the clause round 21 amended in.**

⛔ **On the bar: two symptoms measured ABSENT, one VOID and re-homed. PASS.**
⭐ **`SF-34` is NOT pulled into M1. The chrome ruling stands — and it now stands
on a measurement instead of on four arguments.**

⚠️ **Two corrections to the premise the ruling was argued on, and BOTH make the
conclusion stronger rather than weaker:**

- ⛔ **TWO chrome regions are populated at this ref, not one.** The masthead on
  both goldens; ⭐ **the outline on `unit-01-your-first-class`, which is the
  **depth2** golden, with 7 `<li>`.** ⚠️ **`unit-02-reading-a-small-graph` is the
  depth1 golden and emits NO `<nav>` at all** — `outline()` suppresses a list of
  fewer than two entries. ⛔ **There is no `depth1` `unit-01` golden; a correction
  in circulation names one, and it is wrong.**
- ⭐ **The bar was written believing the masthead was the ONLY populated region
  and that it was *"legible unstyled"*. It is populated, it is legible, and it is
  not unstyled.**

### ⭐ One observation that was NOT in the bar — and it does not change the verdict

⛔ **Only a capture shows it:** prose is held to `--measure` (`80ch`) while **code
figures and tables span the full 1280px viewport**, so the page reads as a narrow
column with wide islands. ⚠️ **`QA-03` filed it as *"the layout is inconsistent"*.**

⛔ **It is not an inconsistency, and the carrier was in the file being observed.**
⭐ **`reading.css:38–41` states the decision in its own words:** *"Running text
alone keeps a measure the eye can track back from. A figure, a table or a code
block is scanned rather than read and takes the full column."* ⛔ **That is a
deliberate, documented choice, and it is correct.**

⚠️ **What IS real is one word of it: nothing defines *the column*.** ⭐ **`body`
takes `margin: 0; padding: 0 var(--gutter)` and NO `max-width`**, so at 1280px
*"the full column"* is the full viewport and the intent stops holding as the
window grows. ⛔ **Bounding the page's column is the LAYOUT GRID — `SF-11`'s
finding 3 named it and `SF-34` inherited it** — so it lands there and nowhere
else. ⭐ **Filed as `PO-22/6`: the observation was right about the symptom and
wrong about the cause, and reading the carrier changed the routing.**

---

## ⛔ RULED 2026-09-10 (round 22) — **`QA-03`'s nine findings, every one dispositioned**

⭐ **`QA-03` filed nine. Three are `[structural]` and needed a decision; the rest
are recorded, routed or already answered.** ⛔ **A finding with no disposition is
`F23` again, so the refusals are written beside the adoptions.**

| Finding | ⛔ **Disposition** | ⭐ **Where it now lives** |
|---|---|---|
| **`QA-03/1`** — the pinned image has no browser | ⛔ **ADOPTED as `W36`** | ⭐ **And the state it claims is UPHELD: `unpinned green`, not `host-verified`** — see below |
| **`QA-03/2`** — four colour tokens painted by nothing, owned by nobody | ⛔ **ADOPTED by `SF-34` in full** | ⭐ **All four, not two** — see below |
| **`QA-03/3`** — one engine; focus order is the reading most likely to differ | ⭐ **RECORDED, no row** | ⛔ **It is a limit of the instrument, honestly stated, and `SF-24`'s acceptance is about readers rather than about Chromium.** ⚠️ **A second engine is a second transport, so this is a task-sized change with no measured need; it is `QA-02`/`SF-24`'s to raise if it ever bites** |
| **`QA-03/4`** — `ruff` and the floor disagree by RULE while agreeing on the NUMBER | ⛔ **SPLIT — the floor half is `W38`; ~~the rubric half is the CTO's and I do not take it~~ ✅ **THE RUBRIC HALF IS DISCHARGED**, Ruling 88, CTO round 26, `cc85ce1`** | ⭐ **`W38` below.** ⛔ **The rubric half is [corrected at round 25](#ruling-88-discharged-the-rubric-half-43-minutes-before-this-board-said-it-was-untaken)** |
| **`QA-03/5`** — `docker/dev/check` forwards no environment | ⛔ **FOLDED INTO `W36`** | ⭐ **Same file, and it is a trap only once `W36` lands** — see below |
| **`QA-03/6`** — `More to come` on a complete prose corpus | ✅ **ALREADY RULED, round 21** | ⭐ **`SF-12/4` → `SF-28`'s acceptance clause.** ⚠️ **`QA-03` confirms it rather than discovering it, and adds one thing: it is the LAST thing on the page** |
| **`QA-03/7`** — the chrome observation carries no verdict | ✅ **DISCHARGED** | ⛔ **The verdict is [row 8's ruling above](#ruled-2026-09-10-m1s-row-8-passes-and-one-third-of-the-bar-was-unfalsifiable), and the author was right to refuse it** |
| **`QA-03/8`** — the build copies no media | ⛔ **ADOPTED as an acceptance clause on `SF-28` — NOT `SF-27`** | ⭐ **The routing was wrong; see `PO-22/5`** |
| **`QA-03/9`** — 55 skips added to the pinned run | ⭐ **RECORDED as a COST, and `W36` removes it** | ⛔ **The right call was made twice over: the harness stays in `testpaths` (silence would have been worse), and the cost is named rather than netted out** |

### ⭐ `QA-03`'s refusal of `host-verified` is UPHELD

⛔ **They were offered `host-verified` and argued their way to the weaker claim.
That is the right answer and the reasoning is theirs, not mine to improve:**
rubric §4b bounds `host-verified` by *the image is right to exclude the subject*,
and the subject here is **this repository's own rendered output** — ⭐ **a Chromium
in the image would answer the same question BETTER, because it would be pinned.**
⚠️ **So the image's answer is *absent*, not *wrong*, which §4b calls a gap to
close.** ⛔ **`unpinned green` + a filed gap with an owner is the honest state.**

⭐ **Recorded because a task claiming LESS than it was offered is rare enough to be
worth naming**, and because the argument generalises: ⛔ **the tell is not *"can
the image run it"* but *"would the image's answer be different"*.**

### ⛔ `SF-34` ADOPTS ALL FOUR ownerless tokens, and the reason is one sentence in `reading.css`

⚠️ **`QA-03/2` splits them: `--surface-2` and `--accent-soft` look like chrome;
`--practice` and `--practice-soft` belong to the pending-practices panel, which is
not chrome and not M2.** ⛔ **I read the carrier, and the split does not survive it.**

⭐ **`reading.css`'s own scope note disowns FIVE regions by name:** *"Masthead,
navigation rail, narration player, progress controls and **practice panels** are
NOT here: they belong to the tasks that render them."* ⛔ **The practice panel's
markup is `SF-12`'s and `SF-12` is DONE — which is the chrome defect exactly, one
region further along.** ⭐ **`SF-34` IS the ruling that the rules for a region
`SF-12` addressed and no stylesheet paints are a task of their own.** ⚠️ **So it
reaches the practice panel too, or the same defect is re-derived at M4.**

⛔ **`SF-34`'s scope is therefore the chrome list `reading.css` disowns, MINUS the
regions whose markup does not exist yet** — the narration player and the progress
controls are `SF-18`'s at M3 and keep their `UNPAINTED` rows with `SF-18`'s name
on them. ⭐ **Four tokens with no owner at any milestone become four tokens with
one, and nothing is deferred.**

### ⛔ `QA-03/8` routes to `SF-28`, and `SF-27` does not own the build

⚠️ **`QA-03` routed it to `SF-27`.** ⛔ **`SF-27` is the CONTAINER PAGE RENDERER
and owns `render/container/` — it renders a page and copies nothing.** ⭐ **`SF-28`
owns `studyforge/cli/`, which IS the build**, and its acceptance already says
*"Builds and serves both FND-04 fixtures"* — ⛔ **and the depth-1 fixture is the
media-bearing one.**

⭐ **So this TIGHTENS an existing acceptance rather than adding scope**, and it is
the same shape, the same task and the same milestone as round 21's
`exercises: false` clause, for the same reason: ⛔ **M4 is the earliest ref at
which the defect can be OBSERVED, so the clause lands on the task that will be
holding the instrument.**

---

## ⭐ THREE ROWS MINTED — `W36`, `W37`, `W38`

⛔ **High-water mark moves `W35` → `W38`. `SF-34` is unchanged; no task id is
minted this round, and the two adoptions above are acceptance clauses on existing
tasks rather than new work.**

| | ⛔ **`W36`** | **`W37`** | **`W38`** |
|---|---|---|---|
| **What** | ⭐ **A browser in the pinned dev image** | ⭐ **The repo-wide sweep for checks that cannot fail BY CONSTRUCTION** | ⭐ **The floor and `ruff` disagree by RULE; pin the divergence** |
| **From** | `QA-03/1` + `QA-03/5` | `W33/1` | `QA-03/4`, floor half only |
| **Owner** | framework agent | framework agent | framework agent |
| **Owns** | `docker/dev/Dockerfile`, `docker/dev/compose.yaml`, `docker/dev/check` | ⛔ **no source — the deliverable is an ENUMERATION with a verdict per hit**, plus whatever fixes the verdicts license | `tools/quality/config.py` + one test module |
| ⛔ **The decision, already made** | ⭐ **YES, the browser goes in.** ⚠️ **`QA-03/9` names the cost of not doing it: 55 skips added to the pinned run on top of 8, and a skip set that grows faster than anyone reads it is the `SF-01` defect this project has now catalogued three times (`W33/3` is the third).** ⛔ **Against ~150–400 MB on an image nobody ships** | ⭐ **RUN IT, and BOUND IT.** ⛔ **The output is a list with a verdict on each hit, NOT a rewrite of the suite** — a hit that is genuinely a change detector is left alone and said so | ⛔ **The floor STAYS the stricter one.** ⭐ **The always-on checker does not inherit an optional tool's exemption.** ⚠️ **What is defective is `config.py`'s COMMENT, which asserts the two *"must agree"* when they agree only on the number** |
| ⛔ **The clause that stops it being half-done** | ⭐ **Pinned the way the image pins everything else** — `FND-03` pins Node by checksum. ⛔ **An UNPINNED Chromium does not close `QA-03/1`; it relabels it**, and `unpinned green` would still be the honest state. ⚠️ **PLUS `QA-03/5`: `docker/dev/check` forwards no environment, so `STUDYFORGE_VISUAL=required` cannot be demanded through the wrapper. Harmless today; the day this row lands, a CI job would believe it demanded something it did not** | ⛔ **The shape is stated so the sweep is a grep and not a reading:** any test whose **fixture size, loop bound or expected value is computed from the module constant under test**. ⭐ **The remedy generalises as cleanly as the defect: a property with a bound the module does NOT own** — `W33`'s own fix is the worked example | ⛔ **A TEST pins the divergence in both directions**: a line over the limit ending in a pragma is clean to `ruff` and dirty to the floor. ⚠️ **The `ruff` half skips where `ruff` is absent — the same shape `W33/3` already carries** — ⛔ **and the floor may not import or require `ruff` (Ruling 77)** |
| ⭐ **Why it earns its place** | ⛔ **It converts five acceptance clauses from `unpinned green` to `pinned green` and removes 55 skips, and it adds NO dependency** — `--remote-debugging-pipe` is `os.read`/`os.write` from the standard library, so the harness wants a binary on `PATH` and nothing else | ⛔ **SEVENTH instance of a check that cannot fail in this project, and the FIRST found by a sweep rather than by a reviewer.** ⚠️ **Six were found one at a time by somebody who happened to look** | ⚠️ **Two checkers ran in the same image on the same file and returned different verdicts, and neither is a superset of the other.** ⛔ **Today that divergence is undocumented, so the next author to meet it will "fix" the floor to match `ruff`** |
| ⛔ **When** | ⭐ **After `QA-03` merges** — the harness must exist for the image to serve it. ⚠️ **Ruling 75: it JUMPS `W32` and `W35`, both older and unstarted, and the licence is a MEASURED cost (55 skips, named by their own author); `W32` and `W35` have none between them** | ⭐ **Any time.** ⚠️ **Ruling 75: it JUMPS `W32` and `W35` on the same licence — a mutant SURVIVED, which is a measured cost** | ⭐ **Any time; small.** ⛔ **It jumps nothing: `W38` is the same size as `W31` and is queued behind the rest** |

⚠️ **`W34` remains NOT QUEUED** — ⭐ **a 1511-line restructure is not a filler**, and
nothing this round changes that.

---

## ⛔ RULED 2026-09-10 — **`exercises: false` is a DECLARATION OF ZERO, not an absence**

⛔ **`SF-12/4`, and it is the reading floor's own promise contradicted.** A build
that passes no `declared_practices` renders the *"More to come"* panel on **every
page of a complete prose corpus** — ⚠️ **which is the ISO corpus exactly**, and
spec §7's three states (C5) say such a corpus is **complete at M4, not short.**

⭐ **The renderer is right and the builder is right.** `unit.builder.build(...,
declared_practices=None)` yields `{"declared": None, "archived": 0}`, and `None`
is correctly **not** zero: *a map that never stated a count cannot be shown as
complete.* ⛔ **Measured by `SF-12`'s author: `build_unit(depth1/unit-02)` gives
`declared: None` and the page then carries the panel; with `declared_practices=0`
it does not. The `depth1` golden is generated with `0` for exactly this reason.**

### ⭐ The ruling, one-directional on purpose

⛔ **A corpus manifest carrying `"exercises": false` DECLARES zero practices, and
every unit document built from that corpus carries `practices.declared = 0`.**
⚠️ **The converse says nothing:** `exercises: true` does **not** imply a count for
any unit — ⭐ **which is what keeps this a translation of a stated fact rather than
a guess, and R1-clean: the framework reads a manifest field, it does not know a
corpus.**

### ⛔ The routing — an acceptance clause, not a new task, and here is why that is cheaper

⭐ **No framework change is needed.** `build()` already takes `declared_practices`;
the only thing missing is a caller that supplies it. ⛔ **The first caller that
ever exists is `SF-28` — the build pipeline, `E09`, M4 step 4.3** — ⭐ **which is
the same milestone at which the reading floor's *complete at M4* promise first
becomes testable.** ⚠️ **So this is not deferral: M4 is the earliest ref at which
the defect can be OBSERVED, and the clause is landed on the task that will be
holding the instrument.**

⛔ **Landed as an acceptance clause on `SF-28` in [`E09-delivery.md`](E09-delivery.md).**
⚠️ **Its permanent home is the manifest's own docstring** (`corpus/manifest/document.py`,
where `exercises` is defined) — ⭐ **carried here and named for whoever next opens
that module, because a contract recorded only on a board row is `C6`'s *decision
with no carrier*.**

---

## ⛔ RULINGS 77–80, CARRIED — and two of them are tasks

| # | ⛔ **What it settles** | ⭐ **What it changes for this board** |
|---|---|---|
| **77** | ⛔ **Ruling 31 does NOT reach ruff** — it forbids *circularity* (a checker importing its subject), and ruff is not `tools/quality`'s subject | ⭐ **`style.py`'s independence stands on AVAILABILITY instead** — *"a check that can be skipped is a check that will be."* ⛔ **So the floor does not gain ruff, and `W33` below must not add it** |
| **78** | ⛔ **The floor prints the lint state, INCLUDING its absence, as a NOTICE — never a check** | ⭐ **`knowledge_index.notices` is the exact precedent, and it is what makes 78 compatible with 77: a notice reporting a tool's absence does not depend on that tool.** ⛔ **Minted as `W33`** |
| **79** | ⛔ ***"N passed, M skipped, floor clean"* is BANNED as a summary of a branch; a review states its lint line** | ⭐ **Applied to this board's header above.** ⛔ **Live claims gain a lint line; RECORDS keep the phrasing they were written with** — ⚠️ **rewriting a record to satisfy a rule it predates is how a board stops being evidence** |
| **80** | ⛔ **A floor check's verdict may not depend on UNTRACKED state** | ⚠️ **`pointers.py` resolves by existence, so a link to a generated artifact is clean on the machine that built it and a finding on a fresh clone.** ⭐ **Exposure today is `0`; landed in the rubric's § 2e.** ⛔ **Minted as `W35`** |

### ⛔ Why `W33` is urgent in a way its size does not show

⭐ **Four measurements in one wave, and the fourth is the one that settles it:**

| Instrument | ⛔ **What the gap hid** |
|---|---|
| `FND-08` | ⛔ **4 `ruff` D401 errors passed the floor** |
| `SF-12` | ⛔ **15 ruff findings and 9 unformatted files** a host run called green |
| round 22 | ⛔ **2 of 3 tests missing from the host run were `ruff not installed`** — four rounds after § 4b already said the host run is never the verdict |
| ⛔ **the CTO's own `SF-12` sweep** | ⛔ **A mutant that passes all 2923 tests, exit 0, and renders all 11 samples BYTE-IDENTICALLY — killed only by `ruff check`'s `F401`** |

⛔ **So lint is not a style layer on top of the suite.** ⭐ **It is the SOLE
detector for dead-reference defects, because a defect with no behaviour cannot be
seen by a behavioural suite.** ⚠️ **The two tests that catch it,
`test_repository.py:126` and `:134`, are two of the eight skips in every green
baseline this wave reported.**

### ⭐ Three rows minted — `W33`, `W34`, `W35`

| # | Item | Owner | ⛔ **Scope, ruled — so the task is a BUILD and not a decision** |
|---|---|---|
| ⛔ **`W33`** | **The floor prints its lint state** (Ruling 78) | framework agent | ⭐ **A `lint` NOTICE in `tools/quality`, modelled on `knowledge_index.notices` — it prints the tool and version when present and *"not installed in this checkout … this is not a failure"* when absent.** ⛔ **NEVER a check: it may not change the floor's exit code, and it may not import or require ruff, or Ruling 77 is broken.** ⛔ **Enforcement stays in `tests/test_repository.py` — the notice supplies visibility of absence, the test supplies enforcement of presence, and neither closes the hole alone** |
| **`W34`** | ⛔ **`review-rubric.md` is FUSED, not bloated** (`CTO-23/3`) | framework agent | ⭐ **Measured: 1410 lines, of which 263 are executable (19 %), 798 prose, 15 rulings inlined — and it is 1511 today.** ⛔ **The tell is the cost, not the size: the cheapest correct way to read it was for the CTO to DELEGATE §8/§8a to a subagent.** ⭐ **Shape ruled: an operational checklist on top — the executable lines, each with a one-line statement of what it proves — and the reasoning below as the appeal surface, reached by reference.** ⛔ **NOTHING is deleted; §§ are reordered so the short surface is the one a reviewer executes from** |
| **`W35`** | `pointers.py` honours the ignore declaration (Ruling 80) | framework agent | ⭐ **`config.ignored_paths()` already exists.** ⛔ **The rule: a walk that honours `.gitignore` when choosing what to READ honours it when deciding what RESOLVES — the ASYMMETRY is the defect.** ⚠️ **Exposure is `0` today, so this is LOW priority and is not queued ahead of anything** |

⛔ **High-water mark is now `W38`, and `SF-34`** — ⭐ **round 22 minted `W36`,
`W37` and `W38`; the mint block is [above](#three-rows-minted-w36-w37-w38).**
⚠️ **`W26`'s two-minter defect is the reason this line exists — every `W` above
was minted here, by me, in one document.**

### ⛔ `CTO-23/8` and `CTO-23/4` — accepted as costs, with the `CTO-21/3` trigger

⭐ **Neither becomes a row, and both follow the precedent set for `CTO-21/3`: a
reviewer's taste is not a mandate to rewrite merged-quality code.**

- **`CTO-23/8`** — ⛔ **two cosmetic artefacts in link handling, CONFIRMED not
  leaks by the hostile-payload run.** `[x](javascript:alert(1))` renders as `x)`
  because the href pattern is `[^)\s]*`. ⭐ **Cost: one stray character in a case
  that should not occur.** ⛔ **The trigger: it is fixed by whoever next opens
  `page/text.py` — which is `SF-16` at M3, and it is named in `SF-12`'s handoff
  for them.**
- **`CTO-23/4`** — ⛔ **§ 5's R13 script scans test modules, so 80 of 126 hits on
  `SF-12` were assertions about expected output.** ⭐ **A test's expected HTML *is*
  the assertion.** ⛔ **Cost is reviewer time; the fix is one line, and it rides
  with `W34` because `W34` is already reordering § 5's neighbourhood.**

---

## ⛔ M1's CLOSE CONDITIONS — a **decomposition**, not *"`SF-12` green"*

⛔ **`SF-12` and `QA-03` are the last two tasks in M1.** M1's stated Done is *"a
unit page from the depth-1 fixture opens in a browser, with styles and
highlighting, over `file://`"*. ⭐ **Ruling 72 forbids stating that as a total, and
`Q18` is the precedent that says why it matters here: a finish line that names a
state nothing can enter is worse than an open question, because it reads as a
plan.**

⛔ **So M1 closes when every row below is true at one named ref, and each is
separately checkable by somebody who did not build it.**

| # | Condition | Who discharges it | ⛔ **How it is checked** |
|---|---|---|---|
| **1** | ⭐ **The document exists** — `SF-10` builds a unit document from the depth-1 fixture | ✅ **DISCHARGED** | merged `966ab30` |
| **2** | **The renderer exists as a package** — `render/page/` is modules, not a module (R11), and no file exceeds the ceiling without a docstring justification | `SF-12` | ⛔ **`FND-01` makes an over-long file a build failure**; the check is the suite, not a reading |
| **3** | ⛔ **One page is written** — `render(document, placement) -> bytes` produces a file on disk for the depth-1 fixture's unit | `SF-12` | a test asserts the bytes; ⭐ **`QA-03` asserts the file opens** |
| **4** | **Styles resolve over `file://`** — every `href`/`src` the page emits is **relative**, and nothing reaches a network or an absolute path | `SF-12`, `page/assets.py` (R8) | ⛔ **checked as a set: the emitted references, minus the ones that resolve on disk, is EMPTY** |
| **5** | ⭐ **Highlighting is visible AND bounded** — a tagged fence renders highlighted; ⛔ **an untagged fence renders PLAIN** | `SF-12` | catalogue entry 10 is the oracle: ⚠️ **a guess that highlights a diagram as Java satisfies "with highlighting" and is wrong** |
| **6** | ⛔ **Verbatim stays bounded** — `html` bypasses escaping and **nothing else does** | `SF-12`, `page/blocks/verbatim.py` | the survey's *silent seam*: ⭐ **a test that fails if a second block type reaches the raw branch** |
| **7** | ⛔ **R7 holds on the OUTPUT** — no absolute path, no personal data, in any emitted file | `SF-12` + the shipped gate | ⚠️ **The gate has been asserted on inputs; a renderer is the first task that writes files a reader receives** |
| **8** | ⭐ **A human-visible check ran** — the page was opened over `file://` and the result recorded | `QA-03` | ⛔ **the precedent is not hypothetical: a highlight misclassification italicised every string in one language, every test passed, and only a screenshot caught it** |
| **9** | **The suite and the floor are green in the pinned container**, quoted with the ref | both | ⛔ **a number without its ref is not a measurement** |

⛔ **What M1 does NOT require, stated so the line is enterable** — ⭐ **this half is
what `Q18` was about:** no contents page, no cross-unit navigation, no discovery
cache, no narration, no server, no container execution, and **no second fixture**.
⚠️ **Conditions 4 and 8 are the only two that touch a browser**, and neither
implies a site.

⭐ **`QA-03`'s exemption from the check-first rule is restated because condition 8
depends on it:** ⛔ **a harness inherits no backlog** — it needs a page to look at,
so it cannot precede the renderer, and arriving after it costs nothing. ⚠️ **`W20`'s
rule is about checks that accumulate a migration, and it is three steps old, which
is exactly when a rule starts being carried at its widest.**

### ⛔ THE RUN, ROW BY ROW, AT `90dc580` — **8 of 9 MET, one BLOCKED, and it is not the one that was reported**

⛔ **The decomposition is an instrument, so it is RUN and not consulted.** ⭐ **Each
row below names the artifact that discharges it, at one ref, checkable by somebody
who did not build it.**

| # | Condition | ⛔ **Verdict @ `90dc580`** | ⭐ **The artifact that says so** |
|---|---|---|---|
| **1** | The document exists | ✅ **MET** | `SF-10`, merged `966ab30` |
| **2** | The renderer is a PACKAGE, no file over the ceiling | ✅ **MET** | ⭐ **11 modules under `render/page/` + `render/templates/`; largest is `page/document.py` at 234 against R11's 400, no size exception requested.** ⛔ **`FND-01` makes the check the suite, not a reading** |
| **3** | One page is written — `render(document, placement) -> bytes` | ✅ **MET** | `test_render_returns_bytes`, `test_both_fixtures_render_against_their_golden_files`, `test_a_page_is_byte_for_byte_stable_across_runs` |
| **4** | Styles resolve over `file://` — every reference relative, nothing reaching a network | ✅ **MET** | ⭐ **Checked as a SET, as the row demanded:** `test_every_local_reference_resolves_to_a_file_a_build_writes`, `test_every_asset_reference_is_relative_to_the_page`, `test_a_page_issues_no_network_request` — ⛔ **and `test_the_network_check_is_the_negative_control_for_itself`, which is the row's own instrument checked against itself** |
| **5** | Highlighting VISIBLE and BOUNDED | ✅ **MET** | ⛔ **Both directions, which is the half catalogue entry 10 exists to force:** `class="language-java"` asserted on a tagged fence, and `test_a_code_block_with_no_language_carries_no_class_and_a_plain_caption` on an untagged one |
| **6** | Verbatim stays bounded — `html` bypasses escaping and NOTHING else does | ✅ **MET, and over-discharged** | ⛔ **`test_exactly_one_block_type_is_emitted_without_escaping`, plus `test_every_other_block_type_escapes_a_tag_in_its_text` and `test_verbatim_imports_nothing_but_the_future` (an AST walk).** ⭐ **Independently re-verified by the CTO with a hostile payload through every string-bearing field of all 11 block types, 18 variants each: *block types that emitted a payload verbatim: `['html']`* against *`RAW_TYPES`: `['html']`*, MATCH** |
| **7** | R7 holds on the OUTPUT | ✅ **MET** | ⭐ **`test_a_page_carries_no_absolute_path_from_this_machine`, per fixture.** ⛔ **The first task in this project to assert R7 on files a READER receives rather than on inputs** |
| **8** | ⛔ **A human-visible check ran** — the page opened over `file://` and the result RECORDED | ✅ **JUDGED AND PASSED — PO round 22** | ⛔ **`feat/QA-03-visual` @ `d2dc2c4`.** ⭐ **Both goldens opened over `file://` in Google Chrome 149.0.7827.200, captured 1280×900 in both themes; the chrome recorded as a named observation, which is round 21's amendment.** ⛔ **The legibility bar: two symptoms measured ABSENT at `ee50f77`, one VOID and re-homed — [the ruling](#ruled-2026-09-10-m1s-row-8-passes-and-one-third-of-the-bar-was-unfalsifiable).** ⚠️ **The JUDGEMENT is discharged permanently; what remains is the branch's merge, which is row 9's business and not this row's** |
| **9** | Suite and floor green in the pinned container, quoted with the ref | ⏳ **NOT YET TAKEABLE — the close ref does not exist** | ⛔ **`3026 / 8, floor clean, lint pinned-green @ `ee50f77`` is the release tip and does NOT contain `QA-03`.** ⭐ **`QA-03` measured its own trial merge onto `ee50f77` at `3057 passed, 63 skipped`, floor clean, lint pinned-green — but a trial merge is not a ref anyone else can check out.** ⚠️ **M1's close ref is the commit that merges `feat/QA-03-visual` into `release/m0-foundations`, and row 9 is re-taken THERE** |

### ⛔ M1's STATE AFTER THE ROW-8 RULING — **mechanical, and off the PO's desk**

⭐ **Rows 1–8 are DISCHARGED. Row 9 is the only one open, and it is not a
judgement — it is a measurement that cannot be taken until a merge exists.**

⛔ **M1 closes when `feat/QA-03-visual` is APPROVED and merged into
`release/m0-foundations`, and row 9 is re-taken at that merge commit and green.**
⭐ **That is a pre-authorisation: no further PO decision is required, and none of
rows 1–8 is re-opened by the merge.** ⚠️ **Whoever takes row 9 records the ref.**

⛔ **The one condition on row 8's verdict, stated so it is not argued later:** it
is a verdict on **the artifact the page renders**, not on the harness's code.
⭐ **So it survives *"APPROVE after changes"* on `QA-03` unaltered** — ⚠️ **unless
a change moves the EVIDENCE: the captures, the per-golden region counts, or the
goldens themselves.** ⛔ **If any of those three moves, row 8 is re-judged; if the
change is anywhere else in `tests/visual/`, it is not.**

### ⛔ The finding this run produced, and it is about the instrument rather than about `SF-12`

⚠️ **The chrome gap was reported as blocking *"the close condition that a page
opens with working styles."*** ⛔ **NO SUCH ROW EXISTS.** ⭐ **That is M1's stated
*Done* — the very total Ruling 72 forbids appealing to — and the nine rows
decompose *"with styles"* into row 4 (references RESOLVE) and row 5 (highlighting
is BOUNDED), neither of which the chrome touches.**

⛔ **So the decomposition did its job in the direction nobody tests it in:** ⭐ **it
refused a block that the total would have granted.** ⚠️ **And it exposed the
opposite risk too, which is why row 8 was amended rather than left alone:** ⛔ **a
decomposition can also SILENTLY drop something the total covered**, and the only
guard against that is an instrument that looks at the real artifact — ⭐ **which is
row 8, and it is the one row still open.**

⭐ **M1 therefore closes on `QA-03` and on nothing else.** ⛔ **It does not close on
`SF-34`, it does not close on `FND-09`, and it does not close on `W33`–`W38`.**

⭐ **AND THE GUARD HELD, ROUND 22.** ⛔ **Row 8 was the guard against a silently
narrowed promise, and it caught something: one third of its own bar named a
region the ref does not populate.** ⚠️ **The instrument that looks at the real
artifact found a defect in the DECOMPOSITION, not in the renderer** — ⭐ **which is
the second time in two rounds that the nine rows have been more informative about
themselves than about `SF-12`.**

### ✅ M1's CLOSE RUN AT `2fe56a4` — **all nine true at one ref, and rows 1–8 were RE-TAKEN, not inherited**

⛔ **M1 IS CLOSED. The close ref is `2fe56a4`.**

⚠️ **The pre-authorisation named a different ref, and I am recording the
difference rather than papering over it.** ⭐ Round 22 wrote: *"M1 is CLOSED at
the commit that merges `feat/QA-03-visual` into `release/m0-foundations`, the
moment row 9 is re-taken there and green."* ⛔ **That commit is `a03aeef`, and row
9 was never taken there.** It was taken three merges later, at `2fe56a4`.

⭐ **So the close ref is `2fe56a4`, and the rule that decides it is this board's
oldest: a measurement is quoted with the ref it was taken on.** ⛔ **Closing at
`a03aeef` would assert a measurement nobody holds** — the exact defect this board
has catalogued six times, committed in the act of closing a milestone against an
instrument built to prevent it. ⚠️ **The pre-authorisation is honoured in
substance: no PO decision was required and none of rows 1–8 was re-opened. What
it could not do was name, in advance, the ref a later measurement would land on.**

#### ⛔ The coordinator asked whether rows 1–8 must be RE-TAKEN at `2fe56a4`. **Yes, and here they are.**

⭐ **The decomposition says *every row true at ONE named ref*, and "true at
`ee50f77`, merges unchanged" is an argument, not a reading.** ⚠️ **This project's
catalogued defect is *a status measured once and quoted later*; a close run that
inherits eight of its nine rows is that defect with a milestone attached.**
⛔ **But the re-take is CHEAP, and that is the finding worth more than the
verdict:** ⭐ **rows 2–7 name their own instruments, and row 9 IS those
instruments running at `2fe56a4`.** So the re-take is three mechanical questions,
not eight judgements.

| # | Condition | ⛔ **Re-taken @ `2fe56a4`** | ⭐ **The instrument, run in the tree at that ref** |
|---|---|---|---|
| **1** | The document exists | ✅ **MET** | `git merge-base --is-ancestor 966ab30 2fe56a4` → **YES** |
| **2** | Renderer is a PACKAGE, no file over R11's 400 | ✅ **MET** | ⭐ **19 modules under `src/studyforge/render/`, 2366 lines total; largest is `render/page/document.py` at 234, then `page/navigation.py` at 220.** ⛔ **No size exception requested, and `FND-01` makes an over-long file a build failure inside row 9's own suite** |
| **3** | `render(document, placement) -> bytes` | ✅ **MET** | all three named tests present in `tests/studyforge/render/page/test_init.py` |
| **4** | Every reference relative, nothing reaching a network | ✅ **MET** | all four named tests present in `tests/studyforge/render/page/test_init.py`, including the negative control |
| **5** | Highlighting VISIBLE and BOUNDED | ✅ **MET** | `test_a_code_block_with_no_language_carries_no_class_and_a_plain_caption`, `tests/studyforge/render/page/blocks/test_figure.py` |
| **6** | Verbatim bounded — `html` and nothing else | ✅ **MET** | all three named tests present in `tests/studyforge/render/page/blocks/test_verbatim.py` |
| **7** | R7 holds on the OUTPUT | ✅ **MET** | `test_a_page_carries_no_absolute_path_from_this_machine`, `tests/studyforge/render/page/test_init.py` |
| **8** | A human-visible check RAN and was RECORDED | ✅ **MET** | ⭐ **`git merge-base --is-ancestor a03aeef 2fe56a4` → YES**, and the recorded artifacts are in the tree: `tests/visual/` (17 files) and `docs/tasks/handoffs/QA-03.md`. ⛔ **Round 22's judgement is not re-opened; what is re-taken is that the evidence it judged is present at the close ref** |
| **9** | Suite and floor green in the pinned container, with the ref | ✅ **MET** | ⛔ **`3090 passed, 63 skipped` — all 63 named — quality floor clean, `ruff 0.16.6` `check` exit 0 and `format --check` exit 0. Taken by the coordinator at `2fe56a4`, in the pinned container** |

⛔ **The one gap in the re-take, stated because a check that hides its own hole is
worse than no check:** ⭐ **rows 3–7 are re-taken as *the named test exists at the
close ref and is not skippable* — `grep -n skip` over all three files returns
nothing, so none of the twelve is among row 9's 63 skips — ⚠️ but "it ran and
passed individually" is carried by row 9's aggregate, not by a per-test
transcript.** ⛔ **That is a property of the decomposition, not of this run: rows
3–7 were always going to be discharged by the suite, and row 9 is the suite.**

⭐ **What this makes true, and it is the reason to have run it at all:** ⛔ **the
close ref moved by three commits between the pre-authorisation and the
measurement, and the re-take cost about ninety seconds of `git` and `grep`.**
⚠️ **The version of this run that inherited rows 1–8 would have produced the same
verdict and would not have noticed that it was closing on the wrong ref.**

---

## ⛔ `W39` — MINTED. **The index rebuild that exists only in one agent's memory**

⛔ **High-water mark moves `W38` → `W39`.** ⭐ **`CTO-25/9`, the CTO's own and the
sharpest open item on the board, now has a row.** ⚠️ **It was asked as *"give it a
row, or say why the rebuild belongs somewhere other than the board"*, and the
answer is: a row, plus an interim step in `../conventions/delivery-flow.md`,
because the row cannot land tonight and the defect fires tonight.**

| | ⛔ **`W39`** |
|---|---|
| **What** | ⭐ **The knowledge index goes stale on every merge, so the release tip is RED immediately after each one** — and the rebuild that fixes it is in no close procedure, no rubric clause, and no test |
| **From** | `CTO-25/9`, sharpened by the CTO at round 25 |
| **Owner** | framework agent. ✅ **THE MECHANISM IS RULED — Ruling 96, CTO round 27** |
| **Owns** | `tools/knowledge/index.py`, `tools/quality/knowledge_index.py`, `../conventions/review-rubric.md`, `../conventions/delivery-flow.md` and ⛔ **`../conventions/agent-protocol.md`** — ⚠️ **the last was missing from this cell and is added at round 24 on `CTO-27`'s item 1, because `W39` NARROWS Ruling 89 and Ruling 89 lives there** |
| ⛔ **The measured cost, which is what licenses everything below** | ⭐ **The CTO's round-25 measurement, quoted with its ref:** after merging a **one-file, docs-only** addendum, `f97e215` read `2 failed, 3088 passed, 63 skipped — graphify-out/graph.json stale`; after `graphify update . ; python3 -m tools.knowledge bridge`, the same ref read `3090 passed, 63 skipped, floor clean`. ⛔ **And the coordinator ran that rebuild BY HAND after every merge tonight — on the order of fifteen times.** ⚠️ **Invisible from every worktree, because `graphify-out/` is git-ignored** |
| ⭐ **`PO-23/3` — the measurement I am adding, and it NARROWS the three options without choosing between them** | ⛔ **`tools/knowledge/index.py:56` sets `DESCRIBED_TREES = ("src", "tools", "docs")`. Its own docstring, three lines above, says: *"A change anywhere else — a board row, a handoff, a `.gitignore` — does not make the index wrong."*** ⚠️ **`BOARD.md` is `docs/tasks/BOARD.md` and a handoff is `docs/tasks/handoffs/*.md`. Both named examples are INSIDE the described trees.** ⭐ **So the module already intends the CTO's option 2 and does not implement it, and "scoping staleness is a change of intent" is off the table.** ⛔ **That is not a ruling that option 2 wins** — option 1 (`FND-07`'s tripwire becomes a NOTICE, per Ruling 78) still satisfies Ruling 80 in a way option 2 does not, and the CTO owns that trade |
| ⛔ **Ruling 75 — what it jumps, named** | ⭐ **`W39` goes to the FRONT and jumps FIVE older unstarted rows: `W37`, `W36`, `W38`, `W32`, `W35`.** ⚠️ **The licence is the only one this board accepts: a MEASURED cost — and `W39`'s is the largest ever recorded for a `W` row.** ⛔ **`W37` jumps on one survived mutant; `W36` on 55 skips; `W39` makes every tip measurement in the project wrong until somebody knows an undocumented trick, and it has already produced two false failures on a ref the CTO was in the act of certifying** |
| ⛔ **Why it is not merely urgent but FIRST** | ⭐ **It is the only row on the board whose defect corrupts the instrument every other row is judged with.** ⚠️ **M2 opens with a base measurement and closes with one; a milestone opened on a red tip nobody can explain is how a wave starts by debugging its own scoreboard** |

### ✅ THE MECHANISM — **Ruling 96: options 2 AND 1, in that order, and the notice is load-bearing by QUOTATION**

⭐ **The three options were never alternatives. Two of them answer different
questions and the project needs both answers.**

| | The question it answers | Verdict |
|---|---|---|
| **Option 2** — scope staleness | ⛔ *Is the index actually stale?* | ⭐ **REQUIRED.** Today the answer is **wrong** |
| **Option 1** — the tripwire becomes a NOTICE | ⛔ *May the floor's exit code depend on untracked state?* | ⭐ **REQUIRED.** Ruling 80 says no |
| **Option 3** — the rebuild joins the checklist | — | ⛔ **REFUSED as an answer.** Kept as the interim below, and **deleted by this row** |

⛔ **`W39` IS THREE PARTS, AND THE ORDER IS LOAD-BEARING:**

1. ⛔ **`tools/knowledge/index.py`** — `freshness()` stops treating every change
   under `docs/` as staleness. ⭐ **The exclusion list is the docstring's own three
   examples made executable**: `docs/tasks/handoffs/`, `docs/tasks/BOARD.md`,
   `docs/tasks/BOARD-ARCHIVE.md`, passed to git as `:(exclude)` pathspecs beside
   `DESCRIBED_TREES`. ⚠️ **`.gitignore`, the docstring's third example, is already
   outside the trees — name that in the comment so the next reader does not add a
   fourth entry for it.**
2. ⛔ **`tools/quality/knowledge_index.py`** — `STALE` stops returning a `Finding`
   and joins absent-and-unverifiable as a **notice**. ⭐ **After this the floor's
   exit code does not depend on `graphify-out/` in ANY state**, which is Ruling 80
   satisfied exactly rather than approximately.
3. ⛔ **`../conventions/review-rubric.md`** — an **INDEX LINE** beside the lint
   line: `fresh` / `stale` / `unverifiable` / `none`, with the built-at commit, in
   the same clause Ruling 79 wrote. ⛔ **CORRECTED AT ROUND 25 — ~~`QA-03/4`'s
   rubric half is still untaken and edits the same clause, so do them together or
   the clause is edited twice~~ is FALSE and was misdirecting this task.**
   ⭐ **`QA-03/4`'s rubric half was DISCHARGED by Ruling 88 at `cc85ce1`, forty-three
   minutes before this board claimed it was untaken** — ⚠️ **so `W39` part 3 adds
   the index line and NOTHING ELSE, and nothing is owed alongside it.**
   ⭐ **[The measurement, and the four readings it invalidates, are at round 25](#ruling-88-discharged-the-rubric-half-43-minutes-before-this-board-said-it-was-untaken).**

⛔ **Part 1 lands BEFORE part 2.** ⚠️ **If the notice lands first, the pressure
that forces the scoping to be done properly is gone and the scoping is dropped**
— ⭐ **a self-contradicting module with no symptom is a module nobody fixes.**

⭐ **Why option 2 alone is not enough, and this is the trade `PO-23/3` handed the
CTO.** ⛔ Fixing the scope does not satisfy Ruling 80: `graphify-out/` is
git-ignored, so a fresh clone is **clean** and a machine carrying a stale index
is **exit 1**, on the same commit. ⚠️ **Option 2 makes the check fire less often;
it does not change what the verdict depends on** — ⛔ **and firing less often is
exactly how a wrong rule survives.**

⭐ **What replaces the exit code, because *"stale is worse than absent"* is TRUE
and must survive.** ⛔ **The notice is made load-bearing the way this project
already made one load-bearing: it is QUOTED.** ⚠️ **That is the whole trade,
stated plainly: an exit code makes the machine refuse; a quoted line makes the
reviewer accountable.** ⭐ **Ruling 80 forbids the first here, and the second is
not a weaker substitute — it is the one that survives `graphify-out/` being
untracked, which the first never could.**

#### ⛔ What `W39` DELETES, and what it NARROWS rather than deletes

- ⭐ **DELETES: the INTERIM rebuild step in `../conventions/delivery-flow.md`.**
  ⛔ **The expiry below is MET** — ⭐ *"option 3 is 'the rebuild is the answer';
  this is 'the rebuild is what we do until there is an answer'"*, and the CTO
  ruled that the rebuild is not the answer, ⚠️ **which is what makes the expiry
  fire rather than lapse.**
- ⛔ **NARROWS, does not delete: Ruling 89** (whoever merges rebuilds the index in
  the checkout merged into, before quoting the tip). ⚠️ **Two reasons are bundled
  in it and only one survives.** ⛔ **After `W39` a stale index cannot redden a
  tip, so rebuilding stops being a precondition of quoting a measurement** —
  ⭐ **it stays as a courtesy to the next agent's queries (R14's budgets assume an
  index) and loses the power to invalidate anybody's number.**

⚠️ **`CTO-27/6` — and it is the sharpest evidence for option 1 that anyone
produced: Ruling 89 is NOT RUNNABLE IN A LINKED WORKTREE AT ALL.** ⛔ **`git
worktree add` does not carry a git-ignored directory, so `graphify-out/` is
absent, the floor reads *"none in this checkout"*, and there is nothing to
rebuild before quoting the tip.** ⭐ **An obligation that silently evaporates
depending on which checkout you stand in is the same untracked-state dependency
Ruling 80 forbids, wearing a procedure instead of an exit code.**
⚠️ **Reproduced independently in THIS worktree at round 24** — `graphify-out/`
absent, floor clean — ⛔ **so it is measured twice, by two agents, in two
checkouts.**

### ⭐ THE INTERIM STEP — ⛔ **and it names its own deletion, which is what stops it becoming the mechanism**

⛔ **A step that works only because one agent remembers it is what this project
has ruled against six times, and it has been running on exactly that all night.**
⭐ **So it is written down NOW, in `../conventions/delivery-flow.md`'s review-gate
section, where the merge actually happens:** *after any merge to a release
branch, whoever merged rebuilds and bridges the index before quoting the tip.*

⚠️ **It is marked INTERIM and it names `W39` as what deletes it.** ⛔ **This is
not the CTO's option 3 arriving by the back door.** ⭐ **Option 3 is *the rebuild
is the answer*; this is *the rebuild is what we are doing until there is an
answer*, and the difference is that one of them has an expiry written into it.**
⚠️ **If `W39` rules option 3, the interim step loses the word INTERIM and gains a
test. If it rules 1 or 2, the step is deleted. Either way somebody has to come
back to it, which is the property a remembered step does not have.**

---

## ✅ M2 STEP 2.1 — **CLOSED 2026-09-10 at `a00337b`**, and it is a different kind of milestone

⛔ **CLOSED. The header said *OPEN* and this section is kept whole for its
reasoning, which is still the best statement of why M2's first step is not M1's.**
⭐ **The close run, with all five rows re-taken at one ref, is
[in round 28](#m2-step-21s-close-run-at-a00337b-all-five-re-taken-and-the-ref-moved-twice-underneath-it).**

⛔ **M2 step 2.1 = `SF-31` (solo), `SF-04` (pair), `SK-02` (pair), and — added at
round 24 — `SF-35` (solo) and `SF-36` (solo).** ⭐ **M2's Done
is *a whole corpus opens offline with a working index, deep links, prev/next and
read marks — **and the skills that produced it exist***.**

⚠️ **The sentence in `README.md` that makes M2 a different shape from M1, and it
is not decoration:** ⛔ ***"The skills come with this milestone, not after it."***
⭐ **`SK-02` is in step 2.1 rather than at the end because spec §9 says a skill
precedes the artifact it produces — a skill written afterwards has been validated
against exactly one source, which is the whole failure §12 exists to detect.**
⚠️ **M1 was five build tasks in a row; M2's first step is a contract, a scan and
a skill, and only one of the three is ordinary framework code.**

### ✅ THE BLOCKER IS CLOSED — **`SF-04` is startable, Ruling 95**

⛔ **R21's discovery-cache row closed in one CTO decision, exactly as this
section predicted it would.** ⭐ **[The register row now says so](#r21-the-register-of-unlocated-contracts),
and the contract is in `E01`'s `SF-04` section rather than in a handoff.**

| | |
|---|---|
| **File** | `.studyforge/site.json` — ⭐ **the constant already existed**: `SITE_CACHE_FILENAME` in `src/studyforge/corpus/placement/names.py` |
| **Key** | ⛔ **`site_api`**, minted in `src/studyforge/version.py`'s `CONTRACT_FIELDS` **in the commit that writes the cache** |
| **The ONE producer** | ⛔ **`SF-04`, `corpus/discovery.py`.** ⭐ **Confirmed against the tree, not inherited:** `SITE_CACHE_FILENAME` is read in `placement/profile.py`, `placement/locations.py` and `render/page/pages.py`'s fixture — ⚠️ **none of them WRITES it**, so a second producer is now a change to the register rather than a discovery |

⛔ **TWO TRAPS THE BUILDER MUST CARRY, because `SF-09` is the worked example for
a *document* and this is a *cache*.** ⭐ **The mechanics transfer; the failure
behaviour does not, and a builder copying `SF-09` faithfully would get it wrong.**

1. ⛔ **An unsupported or absent `site_api` DOES NOT RAISE.** ⭐ It means the cache
   is not read: the scan runs and the cache is rewritten at the current version.
   ⭐ **That IS R9's refusal** — R9 forbids *migration*, and nothing here is
   carried forward; the old document is discarded whole and the authority (the
   scan) produces a new one. ⚠️ **Raising would be wrong twice over**: it
   contradicts §5's *"a stale cache is detected and the scan wins"*, and it turns
   a git-ignored, derived, rebuildable artifact into a hard failure. ⛔ **Use
   `version.is_supported`, NOT `version.check`** — that module already documents
   `is_supported` as *"the predicate, for a caller that reports rather than
   refuses"*, and this is that caller. ⛔ **REPORTED, never silent (R6)**: the
   path, the declared version, and what this build speaks.
2. ⛔ **`site_api` is NOT the staleness mechanism.** ⚠️ **The trap is specific and
   the CTO says they expect it:** a builder holding a fresh version key will reach
   for it as the staleness token — bump per scan, compare, re-scan on mismatch.
   ⛔ **That makes a contract version into MUTABLE DATA**, and `CONTRACT_FIELDS` is
   a tuple every other contract reads: a member whose value changes per run breaks
   R9's meaning for all of them. ⭐ **Two signals, two tests** — schema staleness
   is `site_api`; content staleness is `SF-04`'s own, and `tools/knowledge/index.py`
   solves it in a different tree and is worth reading before inventing a third
   answer.

⭐ **What this cost, recorded because the register is judged by it: one round
blocked, one escalation, one ruling.** ⛔ **What it bought: a cache whose misread
is detectable, in a project where a misread of this file is invisible.**

### ⭐ THE ASSIGNMENT — Developer 1 takes `SF-35`, and the collision pair has DISSOLVED

⛔ **SUPERSEDED AT ROUND 26 — kept whole for its reasoning, which was right.** ⭐ **Both rows are now IN FLIGHT and the live placement is [round 26's](#round-26-the-next-two-rows-and-the-two-that-had-to-be-held).** ⚠️ **What round 25 could not see: the pair dissolved for R9 and for packages, and then collided anyway on ONE FILE'S LENGTH** — ⛔ **`validate/source.py` is 419 lines merged against R11's 400, which no reading of *whose package is whose* would ever have found.**

⛔ **RE-CUT AT ROUND 25, and the table below is the round-24 cut kept for its
reasoning.** ⭐ **What changed, measured at `ce58a36`:**

| | ⛔ **Round 24 said** | ⭐ **True at `ce58a36`** |
|---|---|---|
| `SF-31` | `in-review` on `feat/SF-31-plan` @ `171a18a` | ✅ **`done`, merged `f3ee177`** |
| `SF-04` | Developer 1's next row | ✅ **`done`, merged `0899f0f`, +82** |
| **Developer 1** | ⛔ **on `SF-31`** | ⭐ **FREE — and takes `SF-35`** |
| **Developer 2** | ⛔ **on `W39`** | ⚠️ **on `W39`, dispatched LATE — see the coordination finding below** |
| `SF-35` ↔ `SF-36` | ⛔ **a COLLISION PAIR, sequenced, different developers** | ⭐ **DISSOLVED — Ruling 102 dropped `Depends on SF-35`; different packages** |

⛔ **DEVELOPER 1 TAKES `SF-35`. The licence is unchanged and it is the strongest
one on this board: it is `ISO-09`'s LAST framework blocker**, so it is the one
row in this wave whose landing unblocks the other agent's whole track. ⭐ **It is
`solo`, it is defined in `E01`, and Ruling 90 already reached the spec's register,
so the task starts on a contract rather than on a handoff.**

⚠️ **What the dissolution BUYS, and it is the reason to record it rather than
just correct it:** ⛔ **for two rounds `SF-35` and `SF-36` could not be worked in
parallel, on a shared-package claim that a single `grep` refutes.** ⭐ **They can
now run concurrently** — ⚠️ **the one real overlap is `validate/source.py`, so the
two developers coordinate on that file and nothing else, and whichever lands
second merges the tip first.** ⛔ **This board sequenced them for R9 and Ruling
102 says explicitly that R9 does not sequence them; sequencing them for developer
load is still legal and is no longer necessary.**

#### ⛔ The round-24 cut, kept for its reasoning

⛔ **My round-21 rule stands and it is why the split columns exist: a split point
is NAMED in advance and measured, never discovered mid-flight.**

⛔ **RE-CUT AT ROUND 24, and every cell now names every row rather than the first
one** — ⚠️ **`CTO-27/5`: this table said *"`W39` first … then `SK-02`"* and
omitted `W40`, which the queue table below carried, so a developer reading the
assignment alone skipped a row.**

| Developer | ⭐ **Now** | ⛔ **Then, in order** |
|---|---|---|
| **Developer 1** | ⭐ **`SF-31` — `studyforge plan`** (`solo`, ~20k) — ⛔ **`in-review` on `feat/SF-31-plan` @ `171a18a`**, one commit, 23 files, **+2028**, branch claims `3179 / 63`. ⚠️ **RE-READ AT ROUND 24'S CLOSE, not at its open — see `PO-24/9`** | ⛔ **`SF-04` — UNBLOCKED (Ruling 95)** → then **`SF-36`** |
| **Developer 2** | ⛔ **`W39`** — smallest row on the board with the largest measured cost, and it fixes the instrument the wave is measured with — ⛔ **IN FLIGHT on `fix/W39-index-step`** | ⭐ **`SF-35`** → **`W40`** → **`W41`** → **`SK-02`** |

⛔ **Why `SF-35` jumps `W40` for Developer 2, and it is measured rather than
felt:** ⭐ **`SF-35` is `ISO-09`'s LAST framework blocker**, so it is the only row
in this wave whose landing unblocks the other agent's track; ⚠️ **and `W40`'s
licence does not bind it** — `SF-35` edits `corpus/manifest/content.py`,
`corpus/manifest/document.py` and `validate/source.py`, adds no module, and
`tests/test_gate_coverage.py` enumerates **document-reader modules under
`GATED_TREES`**, not validate rule ids. ⛔ **Measured, not assumed** —
`grep -n "RULE_\|validate" tests/test_gate_coverage.py` returns nothing that
enumerates a rule id.

⛔ **STRUCK AT ROUND 25 — every clause below is FALSE, and Ruling 102 (CTO round
28) says so.** ⚠️ **Kept whole rather than deleted, because it is the clearest
worked example this board has of a sequencing constraint invented from a package
name nobody ran a command against.**

> ~~⛔ **`SF-35` and `SF-36` are a COLLISION PAIR and they are sequenced, never
> parallel.** ⭐ Both edit `corpus/manifest/` and `validate/source.py`; ⛔ **`SF-35`
> lands first because it owns the `corpus_api` bump and `SF-36`'s number depends on
> it** — ⚠️ **which is the R21 question escalated in the register section above.**
> ⭐ **They also sit with different developers on purpose:** `SF-36` follows `SF-04`
> for Developer 1, so the two manifest changes cannot be in flight at once.~~

⭐ **What is true:** `SF-35` owns `corpus/manifest/`; `SF-36` owns
`corpus/container/`; ⛔ **`origin` does not appear in `corpus/manifest/` at all.**
⚠️ **The one shared file is `validate/source.py`.** ⭐ **`Depends on SF-35` is
dropped and `SF-05` replaces it.**

⭐ **Why `SF-31` goes first and to the developer who is free first:** ⛔ **it is one
of the TWO contracts the integration track is blocked on** (the archive seam has
`validate`; the runtime seam has the consuming contracts; ⚠️ **placement had
nothing**). ⭐ **Three named consumers are waiting on it — `SK-07` renders the
ignore rules and `permitted_edits` from it, `OPS-05` asserts against it, and a
person reads it before letting a tool loose in a repository they care about.**
⛔ **It is also the FIRST real subcommand module under `src/studyforge/cli/`,
which today holds one 29-line `__init__.py` and nothing else** — ⚠️ **so like
`SF-01` before it, `SF-31` is an exemplar whose conventions the next subcommands
copy, and that is an argument for one careful author rather than two fast ones.**

#### ⛔ `SF-04`'s split point — **and the honest answer is that it probably does not split**

| Half | Surface | ⛔ **Why the seam is here** |
|---|---|---|
| ⛔ **First, and NOT splittable** | **the scan** — identity-from-content, the walk, and the reported-by-name path for an artifact with no identity block (R6) | ⭐ **R4's mechanism itself. Everything else in the task consumes it** |
| ⭐ **Second, and joinable** | **the cache** — `site.json`'s read, its write, and its staleness detection | ⭐ **It reaches the scan only through the scan's return type, so a second author lands here without touching the first half's file** |

⛔ **The trigger, so this is a plan and not a hope:** ⭐ **a second author joins
ONLY once (a) the scan is committed on `feat/SF-04-discovery`, (b) R21's row has
closed so the cache's version key exists, and (c) `corpus/discovery.py` has been
promoted to `corpus/discovery/` — because until it is a package there is one file
and two authors in it is the collision-pair rule's exact failure.**

⭐ **HELD, not revised, at round 24 — and condition (b) is now MET.** ⛔ **Ruling
95 closed R21's row, so the split now turns on (a) and (c) alone.** ⚠️ **The
condition is not deleted: it is recorded as met, because a trigger whose
satisfied clauses are erased cannot be audited later** — ⭐ **and the CTO called
(c) *"the first time I have seen a split point stated as a precondition rather
than a hope"*, which is the property being preserved.** ⛔ **The expectation is
still NO SPLIT**: `SF-04` is ~30k against `SF-12`'s ~1420-line port, which one
developer took whole.

⚠️ **And the measurement that says to expect NO split:** ⛔ **`SF-04` is `pair`
and ~30k context; `SF-12` was `Team` and a ~1420-line port across 10 modules, and
one developer took it whole to an approved survey.** ⭐ **`SF-10` is the same
precedent one task earlier.** ⛔ **So the default is one author, the seam above is
a MITIGATION, and the signal to use it is `corpus/discovery.py` passing R11's 400
before the cache is written — not a feeling that the task is large.**

#### ⛔ `SK-02`'s split point — **measured from `SK-01`'s shape, which is in the tree**

⭐ **A skill in this repository is not a document. `SK-01` shipped
`src/studyforge/skills/reconnaissance/` — one `SKILL.md` plus EIGHT python
modules** (`survey`, `report`, `record`, `proposal`, `inventory`, `grouping`,
`duplication`, `capability`). ⛔ **`SK-02` is the same shape at
`src/studyforge/skills/adapter/`, and that is where its seam is:**

| Half | Surface | ⛔ **Why the seam is here** |
|---|---|---|
| ⛔ **First, and NOT splittable** | `SKILL.md` — **the procedure**, written against `studyforge validate` as the definition of done | ⭐ **The scaffold is what the procedure SPECIFIES. Authoring the modules first means writing the thing and then writing down what it was** |
| ⭐ **Second, and joinable** | the scaffold's generated structure, its test tree, and the audit command (the `JS-06` equivalent) | ⭐ **Each is named by a step of the committed procedure, so two authors take different steps without meeting** |

⛔ **The trigger:** ⭐ **a second author joins only once `SKILL.md`'s procedure is
committed on `feat/SK-02-adapter-authoring`.** ⚠️ **Until then there is no list of
steps to divide, and dividing by guess is how two authors produce a scaffold the
skill does not describe** — ⛔ **which is R19's hole reappearing inside the task
that exists to close it.**

#### ⛔ `SK-02` carries a question I cannot answer from this side — **routed to PO-Integration, deadline: before `SK-02`'s review**

⭐ **`SK-02`'s acceptance says: *"E07's adapter package was produced by this skill
— the scaffolding commit precedes the source-reading commits, which git can
check."*** ⛔ **That is a §9 precedence claim about a repository I do not own, and
it is checkable by exactly one instrument: `git log` in `ISO/`.**

⚠️ **PO-Integration round 4 ran `studyforge validate` and got `NOT valid: 100
findings`, which means an ARCHIVE exists — and an archive implies an adapter.**
⛔ **If ISO's adapter is already committed, `SK-02`'s acceptance names a state
that can no longer be entered, and §9's own warning applies to the skill built to
satisfy it: *a skill written after the thing it "produces" has been validated
against exactly one source.***

⭐ **THE QUESTION, and it is one command:** ⛔ **does `ISO/` already carry an
adapter package, and at which commits?** ⚠️ **`SK-02` is startable either way —
the skill is worth building regardless — but its acceptance's second bullet is
either checkable or `Blocked`-with-a-named-finding, and which one it is must be
known before its review, not discovered in it** (`../conventions/delivery-flow.md`,
the fourth outcome). ⛔ **This is `Q18`'s shape again: an acceptance condition
naming a state nothing can enter reads as a plan.**

### ⛔ The queue behind step 2.1

⚠️ **Measured from the tree at `ce58a36`, in the LINKED WORKTREE `wt/po25`
(Ruling 108: name the checkout), and RE-TAKEN at this round's close** —
`PO-24/9`'s rule, which caught its own author last round.

| Reading | ⛔ **At round 25's open, `ce58a36`** | ⛔ **At its close, re-taken** |
|---|---|---|
| `git branch --no-merged release/m0-foundations` | ⭐ **nothing** | ⛔ **`fix/W39-index-step`** — [the close re-take](#the-close-re-take-po-249-gets-its-sixth-instance-and-it-is-the-same-round-that-filed-po-252) |
| `feat/SF-31-plan` | ✅ **MERGED at `f3ee177`** — ⛔ `git merge-base --is-ancestor` → YES | ✅ merged |
| `feat/SF-04-discovery` | ✅ **MERGED at `0899f0f`** — ⛔ `--is-ancestor` → YES | ✅ merged |
| `fix/W39-index-step` | ⚠️ **at `ce58a36`, ZERO commits** — ⛔ **an assignment by the letter of `PO-24/9`, and IN FLIGHT in fact: the worktree exists and the developer was dispatched this round** | ⛔ **`1c7bc79`, TWO commits, 8 files, +975 −118 — `in-review`** |
| ⛔ **Is anything waiting on somebody else?** | ⭐ **no** | ⛔ **YES — `W39` awaits a REVIEWER'S verdict** |
| **Developer 1** | ⭐ **FREE** | ⛔ **assigned `SF-35`** |

⛔ **Checked with `git log release/m0-foundations..<branch>`, because a branch
NAME is not a branch STATE** (`PO-23/4`, `CTO-27/3`) — ⚠️ **and `W39`'s row is
the case where that instrument gives the WRONG answer this round, because the
branch was re-cut to the tip after it was dispatched.** ⭐ **The finding is
`PO-25/2`, and it is mine, not the instrument's.**

⛔ **RE-CUT AT ROUND 27 @ `426672c`, and the four HELD rows of round 26 are
resolved: three are FREE and one is still held for one reason instead of two.**
⭐ **Order below, not lane — there is one queue for both developers.**

| Order | Row | ⛔ **When, and what it jumps** |
|---|---|---|
| ✅ **DONE** | ⛔ **`W39`** · **`SF-31`** · **`SF-04`** · **`SF-36`** · **`SF-35`** · **`W43`** | ⭐ **`16049d2` · `f3ee177` · `0899f0f` · `e4a2677` · `a53aee8` · `2caa0d2`.** ⛔ **Each measured `git merge-base --is-ancestor <merge> 426672c` → YES, not inherited** |
| ⏳ **IN FLIGHT** | ⭐ **`SK-02`** — adapter authoring | ⛔ **Step 2.1's LAST task and what CLOSES the step.** ⚠️ **`wt/dev1i`, branch `feat/SK-02-adapter-skill` at `2d86328` with ZERO commits and an UNTRACKED `src/studyforge/skills/adapter/`** — ⭐ **the case where `git log release..<branch>` reads *nothing* about work that is under way (`PO-23/4`).** ⚠️ **Its PO-Integration question is still due BEFORE its review** |
| ⭐ **NEXT 1** | ⛔ **`W45`** — Ruling 114, the deferral reader | ⭐ **MINTED THIS ROUND.** ⛔ **Gates `W44` — it must MERGE FIRST, because `W44` deletes the one deferral this row's negative control needs.** ⚠️ **Small: `size.py` is 122 lines** |
| ⭐ **NEXT 2** | ⭐ **`W44`** — `validate/source.py` becomes a package | ⛔ **GATE CLEARED: both step-2.1 build merges are ancestors of `426672c`.** ⛔ **The tree is OVER R11 right now (425/400) and only `W44`'s id keeps that legal.** ⭐ **Disjoint from `W45` — the R11 pre-dispatch sum was run and the intersection is ∅.** ⚠️ **Gains Ruling 116's acceptance and `SF-36/1`'s documentation bullet** |
| **3** | ⭐ **`W40`** — no module at zero headroom against R11 | ⛔ **FREED: `SF-36` merged, and its round-26 hold is spent.** ⚠️ **RE-FRAMED THIS ROUND (`CTO-32/8`): the population is DERIVED at pick-up, not enumerated — three files are at or over their ceiling and `validate/source.py` is carved out by its own live deferral.** ⭐ **Still BEFORE `W37` and `W38`, which both add tests** |
| **4** | ⛔ **`W46`** — Ruling 115, provenance per claim | ⭐ **MINTED THIS ROUND.** ⛔ **`agent-protocol.md` + `delivery-flow.md`.** ⚠️ **BEFORE `W47`, which indexes the file this row grows** |
| **5** | ⛔ **`W48`** — `handoff-measured` + the clause-1 denylist | ⭐ **MINTED THIS ROUND.** ⛔ **COLLIDES WITH `W42` on `tools/quality/handoffs/` — ONE DISPATCH, or `W48` first and `W42` re-measures.** ⚠️ **Rides with `CTO-29/4`** |
| **6** | ⭐ **`W42`** — the marker check judges 41 of 88 documents | ⛔ **Moves 7 → 6.** ⭐ **`PO-26/2`'s residue is still its own: the pre-round-26 numbers reproduce under no candidate.** ⚠️ **See `W48`'s collision** |
| **7** | ⛔ **`W47`** — an index for `agent-protocol.md` | ⭐ **MINTED THIS ROUND.** ⛔ **AFTER `W46`: an index built before a clause lands is stale on arrival** |
| **8** | ⭐ **`W41`** — the R7 refusal borrows the absent state's reason | ⛔ **STILL HELD, now for ONE reason: `W44` restructures `validate/source.py`.** ⚠️ **Its two surfaces shifted when `SF-35` merged — `W41` RE-MEASURES rather than inheriting `:191` / `:180`** |
| **9** | `W37` — the checks-that-cannot-fail sweep | ⛔ **GAINS RULING 111 THIS ROUND** — `unit/content.py` is the version-discard class's THIRD member and it is unfixed. ⭐ **Its one-line fix is separable and does not wait for the sweep.** ⚠️ **After `W40`** |
| **10** | ⛔ **`W49`** — the seven acceptance conditions clause 1 fails | ⭐ **MINTED THIS ROUND.** ⛔ **AFTER `W48`, whose denylist is this row's instrument and its definition of done** |
| **11** | ⭐ **`W36`** — the browser in the image | ⛔ **UNBLOCKED since `a03aeef`.** ⭐ **Removes 55 skips — the largest single change to the suite's skip set available** |
| **12** | `W38` | ⭐ **Small, and it jumps NOTHING.** ⚠️ **After `W40`** |
| **13** | `W35` | ⛔ **exposure `0` with a structural reason and a TRIGGER** — [see below](#po-248-discharged-w32-and-w35-measured-and-only-one-of-them-was-a-queue-row) |
| ⛔ **QUEUED AT LAST** | ⭐ **`W34`** — the rubric's operational checklist | ⚠️ **Queued since round 23.** ⛔ **`review-rubric.md` RE-MEASURED at `426672c`: **2068** lines — 1611 → 1784 → 1881 → 1951 → 2015 → **2068**, the SIXTH consecutive round of growth.** ⚠️ **Start condition *no build task in flight*: `SK-02` is, so it is UNMET for the sixth time** — ⛔ **and a condition that has never once been met is a condition that is not scheduling the row, it is shelving it. `PO-24/8`'s remedy applies and the next round to touch this row owes it a TRIGGER or a re-route** |
| ⛔ **NO LONGER A QUEUE ROW** | ⭐ **`W32`** | ⛔ **RE-ROUTED AT ROUND 25 to `SF-13`'s acceptance** — [the measurement is below](#po-248-discharged-w32-and-w35-measured-and-only-one-of-them-was-a-queue-row) |
| ⛔ **not queued** | `SF-34` | ⭐ **M2 step 2.4.** ⛔ **Its M1 route closed when row 8 passed; it enters at its own step and not before** |

⚠️ **~~The round-25 table, superseded above.~~** ⭐ **Its ordering argument is
kept in the round-25 and round-26 sections; ⛔ what is NOT kept is a second copy
of the order, because a queue written twice is the defect this board has filed
against itself in five consecutive rounds.**

⛔ **CORRECTED AT ROUND 25 — ~~this table is Developer 2's ordering and
Developer 1's lane is not in it~~.** ⭐ **It is now ONE queue for both
developers**, because the collision pair dissolved and there is no longer a
second lane to keep separate. ⚠️ **Who holds what is in the assignment table
above; this table is the ORDER.**

### ⭐ `PO-24/8` DISCHARGED — `W32` and `W35` measured, and only ONE of them was a queue row

⛔ **`PO-24/8` said the next agent to touch this queue measures those two rows
and nothing else, because they are the only two whose exposure nobody has ever
measured — and a row that can only ever lose is not queued, it is shelved with a
queue's vocabulary.** ⭐ **Both measured at `ce58a36`, `wt/po25`. The four-round
pattern was RIGHT about one of them and about the other it was the wrong
question entirely.**

| | ⛔ **`W32`** — the mixed-form contents fixture | ⛔ **`W35`** — `pointers.py` honours the ignore declaration |
|---|---|---|
| **The claim** | a parser reading only the list form short-reads 36 of 38 units and raises nothing | a walk that honours `.gitignore` when choosing what to READ must honour it when deciding what RESOLVES |
| ⛔ **Exposure, measured** | ⭐ **`0`, and it CANNOT MOVE.** `src/studyforge/contents/` is `__init__.py` and **20 lines**; `grep` for any list-or-heading parse in it returns nothing. ⚠️ **`SF-13` — the task that first computes a reading order — is M2 step 2.2 and unstarted** | ⭐ **`0`, re-measured.** The floor reads **61 pointers in 126 markdown files**; ⛔ **no tracked document resolves a link into a git-ignored tree** |
| ⭐ **Why the number is that number** | ⛔ **THERE IS NO PARSER TO SHORT-READ.** A fixture whose acceptance is *"the fixture fails if a parser reads only the list form"* is unfalsifiable while no parser exists — ⚠️ **which is `CTO-29/3`'s family, arriving in a queue instead of an acceptance document** | ⛔ **Only `graphify-out/` is reachable at all, and the two documents that write the failing shape both write it INSIDE BACKTICKS** — `review-rubric.md:444`'s own table row is `[the index](../../graphify-out/graph.json)`, ⭐ **the defect demonstrated in the one form the floor cannot read** |
| ⭐ **Disposition** | ⛔ **NOT A QUEUE ROW. Re-routed to `SF-13`'s acceptance**, where it stops competing against work that can be done today and becomes a condition the task that needs it must meet | ⭐ **STAYS LAST, and now stays last with a NUMBER and a TRIGGER** rather than by default |
| ⛔ **Trigger** | `SF-13` is taken | ⛔ **the first tracked document that links to a generated artifact WITHOUT backticks** — ⭐ one `grep`, and until then the exposure is genuinely nil |

⭐ **What this settles, and it is bigger than two rows:** ⛔ **`PO-20/2`'s ranked
queue has a five-round record of not being built, and the reason is now visible —
a ranking was the wrong remedy.** ⚠️ **Neither of these rows needed a rank. One
needed a HOME (it was an acceptance condition wearing a `W` id) and the other
needed a TRIGGER (it was a correct row whose exposure is genuinely zero).**
⭐ **Both cost one command, exactly as `PO-24/8` predicted; ⛔ what `PO-24/8` did
not predict is that measuring a shelved row can DELETE it from the queue rather
than move it up.**

### ⛔ `W40` — MINTED. **`tests/test_gate_coverage.py` is at 600 of 600, and three queued rows all write tests**

⛔ **High-water mark moves `W39` → `W40`.** ⭐ **The "two test modules at R11's
ceiling" were handed to me as *queued and yours to order*. ⚠️ I nearly ordered
them last for want of a number — which is `PO-21/5` exactly, three paragraphs
after I named it for the third time — so I MEASURED them instead, and the
measurement moves them from last to second.**

**Measured in the tree at `2fe56a4`, `wc -l`, against R11's 600-line test
ceiling:**

| Module | Lines | ⛔ **Headroom** |
|---|---|---|
| ⛔ **`tests/test_gate_coverage.py`** | **600** | ⛔ **ZERO. It is AT the ceiling** |
| **`tests/studyforge/corpus/container/test_document.py`** | **598** | ⚠️ **two lines** |
| `tests/docker/test_dev_image.py` | 583 | 17 lines |

⛔ **`FND-01` makes an over-length module a BUILD FAILURE, so the next test added
to `test_gate_coverage.py` reds the suite.** ⭐ **That is not a tidiness item, it
is a tripwire lying directly across this wave's path**, and here is why:

- ⛔ **`W38` owns *"`tools/quality/config.py` + one test module"*.**
- ⛔ **`W37` is a sweep whose remedy is *"a property with a bound the module does
  NOT own"* — i.e. it ADDS tests.**
- ~~⛔ **`W39` changes what the quality floor does with a stale index**~~ —
  ⛔ **STRUCK AT ROUND 24. `PO-23/6`'S LICENCE WAS WRONG ABOUT `W39`, and one
  `grep` would have caught it.** ⭐ **Measured (`CTO-27/2`, reproduced at
  `d1270cd`): `tests/test_gate_coverage.py` enumerates document-reader modules
  under `GATED_TREES` and contains no reference to the knowledge index; `W39`'s
  tests land in `tools/tests/knowledge/test_index.py` (97),
  `tools/tests/quality/test_knowledge_index.py` (138) and
  `tests/test_knowledge_index.py` (306)** — ⭐ **all far from R11's 600.**
  ⚠️ **`W40` is still right and its queue slot is still right: `W39` never needed
  `W40` first, so nothing re-orders.** ⛔ **This is `PO-21/5` again — a row
  ordered on a cost nobody instrumented — written three paragraphs after that
  finding was named for the third time.**

⭐ **So TWO queued rows — not three — write tests onto a surface with zero and two
lines of headroom between them.** ⚠️ **`W40` is the split — both modules become packages,
the way `SF-12`'s renderer did and the way R11 says CodeSignal's largest modules
are ported.** ⛔ **It is done BEFORE those three rows, not after**, because the
alternative is that whichever of them lands first spends its review arguing about
a size failure it did not cause.

⛔ **Ruling 75 — what `W40` jumps:** ⭐ **`W37`, `W36`, `W38`, `W32`, `W35` — five
older unstarted rows, the same five `W39` jumps.** ⚠️ **The licence is a measured
cost and it is the sharpest kind: not a cost already paid, but ⛔ a build failure
that two separately-queued rows will each trigger independently.** ⚠️ **CORRECTED
at round 24 from *three*, per the struck bullet above.** ⭐ **`W40` sits at **3**
in the queue above — ⛔ and `W40` is a filler-sized row, so it rides in front of
`SK-02` without costing the step a developer.**

---

## ⛔ `SF-35` — MINTED. **`content.not_material` and `corpus_api: 2`, and it is `ISO-09`'s last framework blocker**

⛔ **The SF high-water mark moves `SF-34` → `SF-35`; the project goes 87 tasks →
88.** ⭐ **Definition in [`E01-core-contracts.md`](E01-core-contracts.md); this is
the state and the sequencing.**

| | ⛔ **`SF-35`** |
|---|---|
| **What** | ⭐ **`content` gains a third state.** ⛔ A file that was **never material** — the repository's own scaffolding — is not *withheld from the reader*, so calling it `exclude` makes every `why` a small lie |
| **From** | ⛔ **Ruling 90 (CTO round 26), sharpened by Ruling 98 (round 27)** |
| **Owner** | ⛔ **REASSIGNED AT ROUND 25 — framework agent, DEVELOPER 1, NOW.** ⚠️ **~~Developer 2, after `W39`~~: Developer 2 is on `W39` and Developer 1 came free when `SF-04` merged, so putting `ISO-09`'s last blocker behind an in-flight row would cost the integration track a whole round for nothing** |
| **Owns** | ⛔ **POINTER, not a copy — [`E01-core-contracts.md`](E01-core-contracts.md), `SF-35`'s `Owns` cell.** ⚠️ **This board carried a SECOND copy of this cell and the two disagreed for two rounds; `CTO-31/6` is that finding and [the ruling is above](#ruled-round-26-cto-316-validatesourcepy-has-one-owner-one-licensed-region-and-a-pair-that-breaches-r11)** |
| ⚠️ **The one file it shares** | ⛔ **`validate/source.py` is OWNED BY `SF-36`. `SF-35` holds a NAMED LICENCE on two regions of it** — the rule-constant block after `RULE_ORIGIN_MISSING`, and `check_unclassified`. ⭐ **Measured disjoint from `SF-36`'s regions; the one conflict is the shared insertion anchor and BOTH blocks are kept.** ⛔ **The pair breaches R11 at 419 lines and the second lander takes R11's `Size exception:` opt-out NAMING `W44`** |
| **State** | ⛔ **IN FLIGHT @ `d77cb85`, `wt/dev1h`, UNCOMMITTED** — 12 files, **+709 −70**; the branch `feat/SF-35-not-material` is at `16049d2` with ZERO commits. ⚠️ **A worktree is not an agent and a branch is not a tip (`PO-25/2`): this reading is the DIFF, which is neither** |
| ⛔ **Why it is its OWN task and does not ride with `SF-04`** | ⭐ **Ruling 98 refused the rider on a MEASUREMENT, not a preference.** ⚠️ **The stated reason to combine them was that both touch `version.py`/`CONTRACT_FIELDS`** — ⛔ **`F18` touches neither, and Ruling 90 says so in its own words: *"`CONTRACT_FIELDS` gains nothing — `corpus_api` is already in it."*** ⭐ **Zero shared surface; different tracks; different clocks** — ⛔ **and combining them would put the integration track's last framework blocker behind a task that has not started, in a wave where `SF-04` is the second thing its developer picks up |
| ⛔ **One commit** | ⭐ **The field and the version bump land TOGETHER**, per R9's own register note. ⚠️ **Not because old manifests break — they do not — but because a manifest that USES the field is unreadable to an older build** |
| ⛔ **Ruling 90 reaches the SPEC in that same commit** | ⚠️ **It exists only in a handoff today, which is the entire reason a coordinator had to go find it.** ⭐ **C6 closes on this ruling in the commit that implements it, not a round later** |
| ⛔ **Ruling 75 — what it jumps** | ⭐ **`W40`, `W41`, `W37`, `W36`, `W38`, `W32`, `W35`.** ⛔ **The licence: it is `ISO-09`'s LAST framework blocker.** ⚠️ **PO-Integration measured the current framework and got the right refusals — `parse(corpus_api: 2)` REFUSED by R9's gate, `content.not_material` REFUSED as an unknown key — and relabelled their whole delivery section a PROJECTION rather than treating a decision as a delivery.** ⭐ **That is the correct behaviour and it is why this row jumps: a ruled-but-unshipped decision is measured as *unshipped* by the other side, and every round it waits is a round their track cannot move** |

### ⛔ Rule 1a joins the ruling, and it is NOT redundant with rule 3

> ⛔ **A `not_material` entry is either an EXACT PATH, or a glob whose wildcard
> lies inside a directory prefix that is itself entirely not-material.**
>
> ⛔ **A pattern whose correctness depends on which files happen NOT to exist is
> refused, however exactly it matches today.**

⚠️ **Rule 3 catches a loose glob only when the swept file is ALSO in `include`.**
⛔ **The real hole is the file that does not exist yet: a filename-shaped glob can
SILENCE RULE 4 for a file nobody has considered** — the `UNCLASSIFIED` catch goes
quiet precisely because the file is now classified.

⭐ **The strongest evidence that this is the right cut is that nobody fitted it to
the answer.** ⚠️ **PO-Integration reproduced Ruling 90's own three globs against
ISO's 17 residual files, found they cover 17 of 17, and REFUSED TO PROPOSE
THEM** — ⛔ **because `[CLR]*` covers `CLAUDE.md`, `LICENSE` and `README.md` only
because `TestCases.md` begins with T**, and a `why` cannot be true of a
`CHANGELOG.md` nobody has written yet. ⭐ **The CTO then derived rule 1a from rule
4's silencing and it reproduced their five entries.** ⛔ **Two sides, two routes,
one answer: five honest globs, not three clever ones.**

⛔ **`SK-07` is a DEPENDENT, not part of this row.** ⭐ It generates manifests and
must generate globs that satisfy rule 1a — ⚠️ **the finding is against the
generator.** ⭐ **Adopted as [integration catalogue entry 19](../integration-catalogue.md)
this round, because the constraint is what a corpus author meets and no later
ruling removes it.**

---

## ⛔ `SF-36` — MINTED. **`origin` may name a region, and check 3 is why it has a row at all**

⛔ **The SF high-water mark moves `SF-35` → `SF-36`; the project goes 88 tasks →
89.** ⭐ **Definition in [`E01-core-contracts.md`](E01-core-contracts.md).**

| | ⛔ **`SF-36`** |
|---|---|
| **What** | ⭐ **A source that carries several units inside one file has no way to say so.** ⛔ `origin` may become an object — `path` + `section` — where `section` is the exact text of the ATX heading that opens the region, and the region ends at the next heading of the **same or shallower** depth |
| **From** | ⛔ **Ruling 92 (CTO round 26), on `F21`** |
| **Owner** | framework agent, **Developer 2** (⛔ **REASSIGNED at round 25**: it no longer follows `SF-04`, because `Depends on SF-35` is dropped and `SF-04` is merged) |
| **Owns** | ⛔ **POINTER, not a copy — [`E01-core-contracts.md`](E01-core-contracts.md), `SF-36`'s `Owns` cell**, which has been right since Ruling 102 while this board carried a wrong copy for two rounds and then a *different* wrong copy of `SF-35`'s. ⭐ **`CTO-31/6`'s ruling: `validate/source.py`'s ONE owner is `SF-36`** |
| **State** | ⛔ **COMPLETE at `e4a2677`** (change `80bb154` + handoff), 14 files, **+1017 −59**, **3363 passed / 63 skipped**, floor clean — ⭐ **WITH THE CTO for verdict.** ⚠️ **Mints `container_api: 2`; adds `src/studyforge/validate/headings.py` (134 lines)** |
| ⛔ **Its two findings** | ⭐ **`SF-36/1` `[local]`** — spec §4's worked example still declares `container_api: 1` and no region shape; **[homed above](#sf-361-needs-a-home-and-it-is-not-w44s)**. ⭐ **`SF-36/2`** — a RECORDED NEGATIVE: the author declined to split `validate/source.py` at 399/400 because the seam is the one `SF-35` is working across. ⛔ **Correct in isolation, and it is why `W44` exists** |
| ⛔ **The version it mints** | ⭐ **`container_api: 2`, NOT `corpus_api` anything** (Ruling 102). ⛔ **`KNOWN_CONTAINER_API` speaks `{1, 2}`; `corpus_api` is untouched** |
| **Depends on** | ⭐ **`SF-02`, `SF-05`** — ⛔ **`Depends on SF-35` is DROPPED (Ruling 102): it was a VERSION dependency and there is no shared version** |
| ⛔ **Why it had no row until now** | ⚠️ **The ruling says *"framework task, with tests"* and names three modules — ⭐ and that is a DESCRIPTION of a task, not a task.** ⛔ **The id space has one minter, so a ruling can only ask for a row; this one asked at round 26 and nobody minted it until check 3 ran** |
| ⛔ **Why a heading and not a line range** | ⭐ **`check_completeness` exists to DISAGREE with the parser**, so the boundary may not come from the Markdown reader — ⚠️ **a heading anchor would, and that destroys the independence the check is built on.** ⛔ **A line range is parser-independent too and was refused for a different reason: it is brittle against an upstream file that grows a paragraph** |
| ⛔ **The finding it fixes** | ⭐ **Seventeen units sharing one `path` are seventeen comparisons against ONE count.** ⛔ **With disjoint regions it is seventeen against seventeen — ⚠️ not seventeen against 361** |
| ✅ **THE OPEN QUESTION — ANSWERED** | ⛔ **~~`corpus_api: 2` shared with `SF-35`, or `3`? Escalated to the CTO; the PO's reading is `3`~~** — ⭐ **NEITHER. Ruling 102 (CTO round 28): the question's PREMISE was false, `SF-36` does not touch `corpus_api` at all, and the register that moves is `container_api`.** ⚠️ **The PO's reasoning was right in SHAPE and wrong in SET — *two additive shapes in two commits take two versions* holds; the chain never asked WHICH FILE CARRIES THE KEY.** ⭐ **The rule it produced, and it costs one sentence: a contract version is minted in the register of the DOCUMENT that carries the new key** |
| ✅ **Collision pair — DISSOLVED** | ⛔ **~~`SF-35` and `SF-36` both edit `corpus/manifest/` and `validate/source.py`, so they are SEQUENCED, never parallel~~ — FALSE.** ⭐ **`SF-35` edits `corpus/manifest/`; `SF-36` edits `corpus/container/`. The only shared file is `validate/source.py`.** ⚠️ **Ruling 102: *the board may still sequence the two for developer load; it may not sequence them for R9*** — ⛔ **and this board did the second, for two rounds, on a shared package that was never shared** |

⚠️ **`F21/3` — 17 pages landing in a repository root under `sibling` — is real,
is a PLACEMENT question, and is `SF-31`'s, not this row's.** ⛔ **Named here so it
is not folded in during review.**

---

## ⛔ `W41` — MINTED. **An R7 refusal borrows the absent state's reason, and it lies to somebody already having a bad day**

⛔ **High-water mark moves `W40` → `W41`.** ⭐ **From Ruling 94 (CTO round 26), on
`F25` — ⚠️ another ruling that named *"a small, cheap framework task with tests"*
and no id.**

| | ⛔ **`W41`** |
|---|---|
| **What** | ⭐ **An `Unchecked` produced by an R7 refusal carries its OWN reason id and its own sentence** — ⛔ **never the `not-declared` one** |
| **What it replaces** | ⛔ **Two `Unchecked` reasons that are FALSE** — *"nothing in this archive declares an 'origin'"* and *"no container map declares an 'origin'"*. ⚠️ **The archive DOES declare one. That is what was refused** |
| **Owner** | framework agent, **Developer 2**, after `W40` |
| **Owns** | `validate/` — the refusal's reason id and its sentence |
| ⛔ **The precedent is already in this codebase** | ⭐ **`validate/source.py` mints `RULE_IGNORE_DECLARATION` rather than reusing `unclassified`, and says why in a comment: *"The classification check did run; what could not be read is the repository's declaration — a different fact, and one a script filters on separately."*** ⛔ **Same fact, same remedy — this row APPLIES a precedent rather than inventing one** |
| ⛔ **Why it jumps five older rows** | ⚠️ **R6's sibling rule is that an unchecked claim is reported loudly and counted, and an `Unchecked` whose stated reason is UNTRUE is worse than silence** — ⛔ **it sends the corpus owner to fix something that is not broken.** ⭐ **And this one fires only when personal data has just been caught, so its reader is already in the worst five minutes of their integration** |
| **State** | ⭐ **`todo` @ `d1270cd`.** ⛔ **`W27` unblocked it; it did not fix it, and it still reproduces verbatim** |

⭐ **The cross-cut worth keeping, because it is why three findings ruled the same
way on one day:** ⛔ **`W28`, `F18` and `F25` are one defect wearing three
costumes — a check that conflates *"no"* with *"not asked"*.**

| | *"no"* | *"not asked"* | conflated? |
|---|---|---|---|
| `W28` | not ignored | git could not be consulted | ⭐ **fixed** — `RULE_IGNORE_DECLARATION` |
| `F18` | withheld from the reader | never was material | ⛔ **`SF-35`** |
| `F25` | no origin declared | an origin was refused under R7 | ⛔ **`W41`** |

---

## ⛔ ROUND 31 — **check 3 came back 0 of 11**, `Owns` stops naming a `.py`, and the R11 pre-dispatch sum reads ZERO for the first time

### ⛔ ROUND 31 — the six wave-open checks, each with its NAMED instrument and its READING

⭐ **Run at `e309172`, `wt/po31`, pinned image, except where a row names another
checkout.** ⚠️ **Ruling 128 applied to every row: where a reading is a COUNT the
POPULATION is printed beside it, and the EXPECTED reading is written down BEFORE
the command runs.**

| # | Check | ⛔ **Instrument** | ⭐ **Expected, written first** | ⭐ **Reading @ `e309172`** |
|---|---|---|---|---|
| **1** | index present and current | `docker/dev/check python3 -m tools.quality`, the `knowledge index:` line, **per checkout** | MAIN `stale — built at 8146bdb4` (`CTO-38/4` predicted it and left it); `wt/po31` `none` | ✅ **PASSES, and MAIN DISAGREED WITH MY EXPECTATION IN THE GOOD DIRECTION.** MAIN → **`fresh — built at e3091720`**; `wt/po31` → `none — none in this checkout` (Ruling 108; the floor says this is not a failure). ⛔ **`CTO-38/4` is DISCHARGED — the coordinator rebuilt it, which is the remedy that finding named** |
| **2** | the `[structural]` triage sweep | ``git grep -EIc '`\[(local\|structural\|none)\]`' e309172 -- docs``, then `wc -l` for files and `awk -F: '{s+=$NF}'` for lines | ≥ 621 lines / ≥ 99 files (round 30's reading) | ⭐ **660 lines / 103 files**, up **+39 / +4** in one wave — ⚠️ **the SECOND consecutive wave at exactly +39/+4, which is the growth rate `W37` is queued against.** ⛔ **The `[structural]` half alone is **398 lines in 102 files** |
| **3** | ⛔ **every ruling reached an artifact** | `git grep -In "Ruling <n>\b" e309172 -- docs \| cut -d: -f1 \| sort -u` — ⛔ **FILES, not a count**, run for each of 132–142 | ⭐ **11 of 11.** ⚠️ **Written before the run, from round 30's precedent — the CTO carried all three of their own rulings that round, in their own commit** | ⛔ **0 OF 11, AND THE PREDICTION WAS EXACTLY INVERTED.** ⭐ **Every one of rulings 132–142 resolves to ONE file and it is the same file: `docs/tasks/handoffs/CTO-2026-09-10-round38.md`.** ⛔ **A ruling recorded only in a handoff has not landed** — and `agent-protocol.md:598` says the carrying is MINE, so this is my round's work, not a complaint. ⭐ **[All eleven carried below](#round-31-what-i-carried-and-what-i-rowed-all-eleven)** |
| **4** | what moved since the last run | `git log --oneline --merges 8146bdb..e309172`, then every row whose fact that touches, plus the head's own summary paragraphs (`PO-29/6`) | 5 merges, 4 stale rows | ⛔ **7 merge commits (17 commits) and FIVE stale rows.** ⭐ **Enumerated below the table** |
| **5** | `CLAUDE.md`'s *Where to start* | `grep -n 'Where to start' -A16 CLAUDE.md`, read against this board's head | *In flight: M2 step 2.2* | ✅ **PASSES, third round running.** ⭐ **It reads *"M2 step 2.1 closed at `a00337b`… Open: M2 — a corpus is readable. In flight: M2 step 2.2"*, and step 2.2 is still open at `e309172`: `SK-08` is its last row and it is authoring.** ⛔ **No milestone or step closed under this round, so the file needs no edit** — ⚠️ **and it WILL need one the moment `SK-08` merges, which is the next round's first liability** |
| **6** | the two-PO channel | `git -C ../<repo> rev-parse --short HEAD` ×4; `grep -c '^### ' docs/integration-catalogue.md`; `[ -d <repo>/docs/studyforge ]` | 4 unchanged refs, 19 entries | ✅ **NOTHING NEW OWED, NOTHING MOVED.** `../ISO-8583-jPOS-tutorial` @ `6c8dc85` (**tenth** run at that ref), `../Claude-senior-java-engineer` @ `c9cf522`, `../Claude-SPARQL-tutorial` @ `b9aa89b`, `../CodeSignal` @ `49c11d5e`; only the first carries `docs/studyforge/`; catalogue **19** |

#### ⛔ Check 3 — **0 of 11**, and the shape of the failure is what makes it worth a headline

⭐ **The instrument returned ELEVEN identical answers**, which is itself the tell:

```text
for n in 132 … 142; do git grep -In "Ruling $n\b" e309172 -- docs | cut -d: -f2 | sort -u; done
  ->  docs/tasks/handoffs/CTO-2026-09-10-round38.md      (×11, and nothing else)
```

⛔ **Round 30 read 3 of 3 and I wrote *11 of 11* on that precedent. That was
inheriting a reading, and it is the exact error this board files against others.**
⚠️ **Round 30's 3-of-3 was one round's behaviour, not a property of the office**
— ⭐ **and rounds 28 and 29 read `1 of 6` and `0 of 4`, so two of the last four
runs came back at or near zero.** ⛔ **The honest expectation was the MEDIAN of
four readings, not the most recent one.**

⭐ **All eleven are carried in this commit.** ⛔ **Six went to convention
documents, three became rows, one was absorbed into an existing row, and one is
this board's own instrument** — [the table is below](#round-31-what-i-carried-and-what-i-rowed-all-eleven).

#### ⛔ Check 4 — the five stale rows, head first

| # | Where | ⛔ **What it said at open** | ⭐ **Corrected to** |
|---|---|---|---|
| 1 | head — `📏 BASE` | *"round 30: 3759 / 63 @ `8146bdb`"* | ⛔ **3814 / 63 @ `e309172`, REPLACED not appended.** ⭐ **The census now carries Ruling 142's instrument AND the host/pinned disagreement (`3864 / 13` on the host — 50 passes the image cannot make)** |
| 2 | head — in flight | *"`SK-05` and `W40` at `8146bdb`, 4 commits each"* | ⛔ **BOTH MERGED** — `fd3c0a4`, `83f767e`. ⭐ **Now `W57` (1 authored commit) and `SK-08` (1 commit)** |
| 3 | head — next two rows | *"`W57` then `SK-08`, placed not dispatched"* | ⛔ **BOTH TAKEN.** ⭐ **Re-placed: `W61`, `W59`** |
| 4 | head — step 2.2 | *"`SK-07` ✅, `SF-13` ✅, `SK-05` ⏳, `SK-08` UNBLOCKED"* | ⭐ **`SK-05` ✅ merged `83f767e`; `SK-08` ⏳ authoring.** ⛔ **ZERO free product rows, which is why both of this round's slots go to the queue** |
| 5 | ⛔ **step 2.2 table — the COLUMN HEADER** | *"STATE @ `ddddd05` (round 29, re-taken)"* | ⛔ **Three of its four cells had been re-taken at `8146bdb` UNDER that header.** ⭐ **`PO-31/2`, and it is `PO-31/6`'s class in a different office's document in the same round** |

### ⭐ And the seventh, standing from Ruling 113 — the R11 deferral sweep, and **derivation A reads ZERO**

⛔ **EXPECTED, WRITTEN BEFORE THE RUN: `A = 2`.** ⚠️ **Round 30 read two members
and both were `W40`'s own subjects; `W40` merged at `fd3c0a4`, so the honest
expectation was that it cleared them — but a merge is not a measurement.**

```text
Derivation A (at or over ceiling: src/tools 400, tests 600), pinned image, e309172
    A_ROWS = 0      ⭐ FOR THE FIRST TIME — nothing in the tree is at its ceiling

   nearest miss:  tests/studyforge/corpus/container/test_document.py  598/600  headroom 2
   nearest miss:  tests/docker/test_dev_image.py                      583/600  headroom 17
   nearest miss:  src/studyforge/archive/scrub.py                     384/400  headroom 16
   nearest miss:  src/studyforge/corpus/manifest/document.py          370/400  headroom 30

Derivation B (Ruling 113's ast sweep)                     ->  B_ROWS = 0
git grep -l 'Size exception:' -- src/ | wc -l             ->  0        (corroborator)
and the population that `| wc -l` conceals, printed once (Ruling 128):
git grep -l 'Size exception:' -- src/ tools/ tests/       ->  4 files
    tools/quality/config.py            tools/quality/size.py
    tools/tests/quality/test_config.py tools/tests/quality/test_size.py

A − B = 0.
```

⛔ **`tests/studyforge/corpus/container/test_document.py` at 598/600 — headroom
TWO — is the row to watch and it is nobody's task.** ⚠️ **Any row that adds a
single test case to it breaks R11**, and neither row placed this round touches
it. ⭐ **`PO-31/4`, and it is recorded rather than rowed because R11's own remedy
(split at pick-up, Ruling 100) is already the default and needs no new id.**

### ⛔ RULING 136 — **my decision, and it changed every `Owns` cell I wrote this round**

⭐ **Decided BEFORE the rows were placed, which is what the brief asked and what
makes the two `Owns` cells below the first written in the new form.**

⛔ **The ruling says *"names a directory or a package, never a module file"*. I
carried a SHARPER form and I am declaring the divergence rather than burying it:**
⭐ **the cell names a MODULE in Python's own sense — `corpus/manifest/content`,
no extension.**

⚠️ **Why sharper and not merely different.** ⛔ **Writing the directory form
would fix nine true cells by inventing forty-one false ones**: `version.py` →
`` `version/` `` predicts a package that may never exist, and a prediction that
reads as a fact is the defect one door along, not the fix. ⭐ **A module's name
does not change when it becomes a package — that is Python's own semantics, and
it is exactly the change R11 forces.**

⭐ **And the finding that decides it: `docs/tasks/README.md:361` has said
*"`Owns` | The package this task creates. One task, one surface."* since the plan
was written.** ⛔ **The definition was right the whole time; the CELLS drifted
from it.** ⚠️ **So Ruling 136 does not tighten a rule — it restores one — and
that is a materially different thing to carry, because nothing anyone did under
the old convention was licensed by it.** `PO-31/7`.

**What an `Owns` cell IS, restated — three durable forms and no fourth:**

| the subject is | the cell names | why it survives |
|---|---|---|
| a **surface** | the module path, **no extension** — `corpus/manifest/content` | a package split does not rename a module |
| a **document** | the file, with its extension — `docs/conventions/agent-protocol.md` | R11's ceiling is asserted of Python modules; a document's name carries no expiry |
| a **single assertion** | the test function's name | Ruling 133: a shape names the seams, and a function name survives a file split |

⭐ **A test mirror is *"and its mirror"*, never a path. A greenfield directory is
declared as such with its file count at a named ref.** ⛔ **The R11 pre-dispatch
sum's population is DERIVED at pick-up from the cell, never read off it.**
⚠️ **Two rows owning two modules in one package now COLLIDE where a file-level
cell said they did not** — ⭐ **and that refusal is correct, because R11
guarantees either may become a subpackage of that same parent mid-flight. The
remedy is ONE dispatch (`W48`/`W42`), not a finer cell.**

#### ⛔ The live class is **NINE**, not two — and all nine are corrected in this commit

⚠️ **The CTO measured two (`E01:183` from `W40`, `E01:324` from `W44`). Re-derived
from the tree at `e309172` rather than inherited, the class is nine** — every one
a cell naming a `.py` that a package split turned into a directory of the same
name, and **seven of the nine nobody had named**:

```text
docs/tasks/E00-foundations.md:509   tools/quality/personal_data.py -> tools/quality/personal_data/
docs/tasks/E01-core-contracts.md:51    corpus/manifest.py          -> corpus/manifest/
docs/tasks/E01-core-contracts.md:183   corpus/manifest/content.py  -> corpus/manifest/content/   [W40, CTO]
docs/tasks/E01-core-contracts.md:324   validate/source.py          -> validate/source/           [W44, CTO]
docs/tasks/E01-core-contracts.md:524   studyforge/cli/plan.py      -> studyforge/cli/plan/
docs/tasks/E01-core-contracts.md:628   corpus/discovery.py         -> corpus/discovery/
docs/tasks/E01-core-contracts.md:681   corpus/container.py         -> corpus/container/
docs/tasks/E02-content-pipeline.md:93  archive/markdown.py         -> archive/markdown/
docs/tasks/E03-rendering.md:43         render/pageassets.py        -> render/pageassets/

after the edit, the same sweep  ->  0        ⭐ the class is closed, not reduced
```

⛔ **`E01:183` was the worst of them: it named `corpus/manifest/document.py:68` —
a cell pinned to a LINE NUMBER**, which expires on the next edit to that file
rather than on the next split. ⭐ **Rewritten as `KNOWN_CORPUS_API` in
`corpus/manifest/`, which names the thing instead of its coordinates.**

⚠️ **The pointer check reported `0 unresolved` throughout and was RIGHT to** —
all nine sit inside code spans, which `pointers.py` strips by design (use versus
mention). ⛔ **Widening it would flood every document that quotes a command; the
class is killed at source instead.** ⭐ **That is Ruling 136's whole argument and
it holds at nine as well as it held at two.**

⛔ **41 cells still name a `.py` that RESOLVES today — latent, not broken — and
they are `W62`.**

### ⭐ ROUND 31 — the next two rows, `Owns` in Ruling 136's form, verified at `e309172`, and a pre-dispatch sum that reads ZERO

⛔ **PLACED, NOT DISPATCHED.** ⚠️ **`W57` (`fix/W57-safe-schemes`, `wt/dev1k`, 1
authored commit `b14e04e`) and `SK-08` (`feat/SK-08-delivery`, `wt/dev2n`, 1
commit `ebf6a65`) are BOTH IN FLIGHT.** ⛔ **Measured with `git worktree list`
PLUS `git log --oneline release/m0-foundations..<branch>` PLUS this board — and
`CTO-38/2` amended Ruling 130 to say the union of the first two is still only a
LOWER BOUND, because both went blind in opposite directions inside one round.**

⛔ **Step 2.2 has ZERO free product rows and step 2.3 is shut behind `W57`
(`PO-30/5`), so BOTH slots go to the queue. That is not a shortage of plan; it is
the plan working.**

| | ⭐ **Row** | ⛔ **Why it, and why in this order** |
|---|---|---|
| **NEXT 1** | ⛔ **`W61`** — the two `SKILL.md` fences, and `SK-05`'s check widened to every shipped `SKILL.md` | ⛔ **A SEQUENCING DECISION with a measured cost.** ⭐ **Two SHIPPED skills tell an agent, in a FENCE, to run a console script that does not exist; a fenced line reads as a command.** ⚠️ **`SK-08` is authoring a THIRD skill package RIGHT NOW** — ⛔ **widen the check after it lands and a third fence ships and passes its own acceptance doing it, which is `W57`'s argument one door along.** ⭐ **The instrument already exists (`SK-05` shipped it); its population is one directory too narrow.** ⛔ **Ruling 138: it does NOT wait on `SF-28`** |
| **NEXT 2** | ⭐ **`W59`** — `_escape` MOVES out of `content/` | ⭐ **Ruling 135, on code that merged three commits ago and whose context is still in one handoff.** ⛔ **A cross-package reach into a PRIVATE name, currently bridged by a re-export whose alias says it is a bridge.** ⚠️ **Small — one function, two call sites, one pinning test — and the CTO's constraint is a scheduling fact, not a preference: it must not run beside anything owning `corpus/manifest`** |

#### ⛔ `Owns` verified against the TREE at `e309172`, in Ruling 136's form, and `PO-26/1`'s R11 pre-dispatch sum

| | `W61` | `W59` | ⏳ `W57` (in flight) | ⏳ `SK-08` (in flight) | ⛔ **shared** |
|---|---|---|---|---|---|
| `src/` | `studyforge/skills/adapter`, `studyforge/skills/onboarding` (SKILL.md text only — **no `.py` touched**) | `studyforge/corpus/manifest` (**8 modules, largest `document` 370/400**) | `studyforge/render/page/text` (**171**/400) | ⭐ **`studyforge/skills/delivery` — 0 files at `e309172`, greenfield** | ⭐ **none** |
| tests | ⭐ **one assertion:** `test_no_fence_in_the_reference_offers_a_console_script_that_does_not_exist`, and `studyforge/skills/adapter/test_init`'s pinned spelling | `studyforge/corpus/manifest` and its mirror (**largest `test_document` 562/600**) | `studyforge/render/page/test_text` (**114**/600) | ⭐ **none yet — the mirror is created by the row** | ⭐ **none** |
| `docs/` | ⭐ **none** | ⭐ **none** | ⭐ **none** | `docs/integration-catalogue.md` + the capability index | ⭐ **none** |
| **Intersection** | | | | | ⭐ **∅, all four pairwise** |

⭐ **Derivation A run here and PRINTED IN FULL rather than read off a cell — and
it is the first ZERO this board has recorded:**

```text
A_ROWS = 0     (nothing in src/, tools/ or tests/ is at or over its ceiling)
B_ROWS = 0     (Ruling 113's ast sweep; no Size exception: deferral in the tree)
A − B  = 0
   nearest miss:  tests/studyforge/corpus/container/test_document.py  598/600  headroom 2
```

⛔ **So the sum's answer is that no file forbids either row, and the constraint
that DOES bind is a different one: `W59` owns the whole of `corpus/manifest`
under Ruling 136's coarser cell, whose largest members are `document` at 370/400
and `test_document` at 562/600.** ⚠️ **`W59` moves ~10 lines and adds a test; it
will not reach either ceiling.** ⭐ **But this is exactly the coarseness Ruling
136 buys, arriving in the first cell written under it, and it is the right
answer: `_escape` moving between `content/` and `edits` is a change no
file-level pair of cells could have made safe.**

#### ⛔ `W61`'s ONE named collision, at wave-open rather than at the second lander's review

⚠️ **`SK-08` is greenfield `skills/delivery` and will almost certainly ship a
`SKILL.md`.** ⛔ **`W61` widens `SK-05`'s check to `src/**/SKILL.md`, so
`skills/delivery/SKILL.md` JOINS that population the moment `SK-08` merges.**

```text
find src -name SKILL.md          @ e309172  ->  3
    src/studyforge/skills/adapter/SKILL.md          2 fenced `studyforge validate`
    src/studyforge/skills/onboarding/SKILL.md       ... (l.135; l.29 is prose, licensed)
    src/studyforge/skills/reconnaissance/SKILL.md   0 occurrences
                                  after SK-08  ->  4   (predicted)
```

⛔ **ORDER: `W61` FIRST, then `SK-08` re-measures — or one developer takes both.**
⭐ **`PO-26/1` exists precisely so this is found here and not by whoever lands
second.** ⚠️ **And note the third member: `reconnaissance/SKILL.md` is already in
the widened population today and is already clean, which is the negative control
`W61`'s acceptance needs and does not have to construct.**

#### ⛔ Ruling 75 — what `W61` and `W59` jump, named

⭐ **Both go in front of TWELVE older unstarted rows — `W32`, `W34`, `W35`,
`W36`, `W37`, `W38`, `W41`, `W42`, `W48`, `W50`, `W51`, `W53`** (`W40`, `W44`,
`W45` and `W57` have left that list). ⛔ **The licence is the only one this board
accepts: a MEASURED cost.**

- **`W61`** — ⭐ **two shipped skills, two fenced commands, an agent-executed
  artifact, and a third skill authoring right now.** ⛔ **The cost of not jumping
  is not delay, it is a WRONG GREEN.**
- **`W59`** — ⚠️ **weaker, and said plainly: nothing is broken today and the
  bridge is pinned by a test.** ⭐ **The licence is FRESHNESS, not urgency —
  `W40`'s reviewer, its author and the ruling all still have the context, and
  `Ruling 101`'s table is unambiguous about the surface.** ⛔ **If it waits, the
  next agent re-derives why a private name crosses a package boundary from a
  handoff instead of from a live conversation.**

### ⭐ ROUND 31 — what I carried, and what I rowed: **all eleven**

⛔ **Check 3 came back 0 of 11, and `agent-protocol.md:598` puts the carrying on
me: *"A CTO ruling is the decision; carrying it is the PO's, and it is wave-open
check 3."*** ⭐ **So this is the round's work, not its complaint.**

⚠️ **A ruling whose entire deliverable IS a clause is dispositioned by the clause
— *"a task's Acceptance, an epic clause, a spec ruling, or a convention
document"*.** ⛔ **It does NOT also need a row, and minting one would be a second
copy of a discharged obligation.** ⭐ **A ruling whose deliverable is WORK gets a
row. That line is where the eleven split.**

| ruling | ⛔ **carrier** | ⭐ **what landed** |
|---|---|---|
| **132** — a one-way seam is a valid R11 split | `docs/conventions/module-structure.md` | ⭐ **The four things a one-way seam owes, QUOTED not summarised** (Ruling 39), plus the refinement that the inhabitation assertion belongs on every sweep. ⛔ **Beside Rulings 100/101, where R11's split rules live** |
| **133** — a shape names the seams, never the file count | `docs/conventions/module-structure.md` | ⭐ **The two-population table, and *a split that obeys a sketch's arithmetic against the sketch's own reason has followed the wrong half of it*** |
| **134** — a history-based instrument loses a file at a rename | `docs/conventions/agent-protocol.md` | ⭐ **In the HANDOFF section, because the clause's subject is what a handoff records.** `git log --follow` stops; `git diff -M20%` finds it |
| **135** — `_escape` moves out of `content/` | ⛔ **`W59` — MINTED** | ⭐ **Placed NEXT 2 this round** |
| **136** — `Owns` stops naming a `.py` file | `docs/conventions/module-structure.md` **+ 9 cells in 4 epics** | ⛔ **CARRIED IN A SHARPER FORM, declared.** ⭐ **Nine live breaches closed to zero; 41 latent cells are `W62`.** ⚠️ **[The decision is above](#ruling-136-my-decision-and-it-changed-every-owns-cell-i-wrote-this-round)** |
| **137** — the duplicated `RULE_*` / `Classification` vocabulary | ⛔ **`W60` — MINTED** | ⚠️ **Not placed: the CTO measured it INERT (`git grep '\.value'` finds no use on the enum)** |
| **138** — the two `SKILL.md` fences | ⛔ **`W61` — MINTED** | ⭐ **Placed NEXT 1, and it does NOT wait on `SF-28`** |
| **139** — a sweep's artifacts live under the agent's own worktree | `docs/conventions/agent-protocol.md` | ⭐ **The clause, its three readings, and the `.gitignore` dependency stated as a thing not to undo.** ⚠️ **`PO-31/5`: the ruling named this file and named Ruling 131 as its neighbour, and those are two documents — cross-referenced, not copied** |
| **140** — a plant is adversarial to the SEARCH TERM | `docs/conventions/review-rubric.md` | ⭐ **Directly beneath Ruling 123, with all three instances in one table** (`W51`'s bare literals, `W40`'s relative import, `W40`'s tuple-bound name) |
| **141** — the `[none]` count is not the finding | ⛔ **ABSORBED into `W58`'s existing row** | ⭐ **No new id.** ⛔ **`W58` ships the DERIVATION, never a number** — [the clause is on the row](#w58-minted-the-zero-marker-standing-beside-a-real-finding-is-a-build-failure-and-today-the-checker-cannot-see-a-single-instance) |
| **142** — a skip census parses the multiplicity | `docs/conventions/review-rubric.md` **§4b-i** | ⭐ **Landed AND RUN: the shipped one-liner reads **63** at `e309172` where `uniq -c` reads **29**.** ⛔ **Ruling 123 satisfied inside the carry — the PASS reading and the caught-wrong reading are both printed** |

⛔ **Two of the CTO's five for-the-PO rows are DISCHARGED rather than queued —
136 and 139 — because both are mine and both are entirely a document clause.**
⭐ **Saying so is the point: a row minted for work already done reads as
outstanding forever.**

### ⛔ FOUR ROWS MINTED — `W59`, `W60`, `W61`, `W62`

⛔ **High-water mark moves `W58` → `W62`; measured across EVERY branch and both
in-flight worktrees, not just this one:**

```text
for b in $(git branch --format='%(refname:short)'); do
    git grep -hoE '\bW[0-9]{1,3}\b' "$b" -- docs/; done | sort -n -t W | uniq | tail
  ->  … W55  W56  W57  W58  (W99)
grep -rhoE '\bW[0-9]{1,3}\b' <wt/dev1k>/docs <wt/dev2n>/docs | sort -n | tail -1  ->  99
```

⭐ **`W99` is a deliberate NON-id inside an example (`PO-19/6`) and is excluded.**
⛔ **The id space has exactly one minter and this is it.**

#### ⛔ `W59` — MINTED. **`_escape` crosses a package boundary as a private name, and the fix is to MOVE it**

| | ⛔ **`W59`** |
|---|---|
| **From** | Ruling 135 (`W40/1`) |
| **Owner** | framework agent, **solo**. ⛔ **Must not run beside anything owning `corpus/manifest`** |
| **Owns** | `studyforge/corpus/manifest` and its mirror |
| **What** | ⭐ **`_escape` MOVES out of `content/`.** ⛔ **Not exported, and not left.** It answers *"how does this path leave the root"*, which is neither package's subject; `W19` already unified the two refusals onto it; ⚠️ **and exporting a private name to satisfy Ruling 101's table is how a surface grows by accident** |
| ⛔ **Measured** | `git grep -n '_escape' -- src/` @ `e309172` → **5 lines, 3 files**: `content/parse.py:250` (definition) + `:245` (use), `content/__init__.py:54` (the re-export, aliased `_e`), `edits.py:60,179`. ⛔ **No other module names it** |
| **Acceptance** | ⭐ The re-export in `content/__init__.py` is GONE, not aliased. ⭐ `content/` no longer defines `_escape`. ⭐ `test_the_one_private_name_edits_already_takes_is_still_reachable` is deleted or re-pointed **and its deletion is argued**, not silent. ⛔ **A negative control plants the re-export back and the seam test CATCHES it** (Ruling 140: the plant is in the shape the clause forbids) |
| **When** | ⭐ **NEXT 2 this round.** ⚠️ Freshness, not urgency — nothing is broken today |

#### ⛔ `W60` — MINTED. **Two copies of one vocabulary, unlinked, inert, and wire-shaped**

| | ⛔ **`W60`** |
|---|---|
| **From** | Ruling 137 (`W40/4`) |
| **Owner** | framework agent, with `studyforge/validate/source` |
| **Owns** | `studyforge/validate/source` and `studyforge/corpus/manifest/content`, and their mirrors |
| **What** | `Classification.UNCLASSIFIED` / `CONTESTED` carry the SAME STRINGS as `validate/source/classification.py`'s `RULE_UNCLASSIFIED` (54) and `RULE_CONTESTED` (61), with **nothing linking the two copies** |
| ⛔ **Why a row and not a fix** | ⭐ **Ruling 101 makes *export the enum's values* versus *keep two constants* a CONTRACT decision**, and `validate/source/` was outside `W40`'s `Owns`. ⛔ **Correctly not fixed inside `W40`** |
| ⚠️ **Its price** | ⛔ **INERT today** — `git grep '\.value' -- src/ tools/` finds no use on this enum (the CTO measured it) — ⭐ **and WIRE-SHAPED, which is precisely the pair that diverges without anybody noticing.** ⚠️ **Inert is why it is not placed; wire-shaped is why it is not dropped** |
| **When** | ⛔ **Behind `W61` and `W59`.** ⭐ **AHEAD of any task that first reads a classification off the wire** |

#### ⛔ `W61` — MINTED. **Two shipped skills tell an agent to run a command that does not exist, in a fence**

| | ⛔ **`W61`** |
|---|---|
| **From** | Ruling 138 (`SK-05/1`) |
| **Owner** | framework agent, **solo**. ⛔ **It does NOT wait on `SF-28`** |
| **Owns** | `studyforge/skills/adapter`, `studyforge/skills/onboarding` — ⭐ **SKILL.md text only** — and ONE assertion: `test_no_fence_in_the_reference_offers_a_console_script_that_does_not_exist` |
| ⛔ **Measured, by the CTO at `8c8a434` and re-derived by me at `e309172`** | Of every `studyforge validate` occurrence under `src/`, **exactly two sit inside a fenced block**: `skills/adapter/SKILL.md:19` and `skills/onboarding/SKILL.md:135`. ⭐ **Every other occurrence is prose in a docstring naming the seam, which R2 licenses** (`adapter/SKILL.md:5`, `onboarding/SKILL.md:29`) |
| ⛔ **NOT the defect** | ⭐ **`validate` RUNS today** as `python3 -m studyforge.validate`, exercised as a REAL SUBPROCESS by `tests/studyforge/validate/test_main.py`. ⛔ **R2's definition of done is satisfiable at this ref, and `pyproject.toml:27-30` is NOT a defect — somebody reasoned about the entry point in writing, at the point of decision** (Ruling 138, and the coordinator's earlier framing is withdrawn) |
| **What** | ⭐ Re-spell the two fences **as they run**; note that `SF-28` registers the shorter form; re-point `tests/studyforge/skills/adapter/test_init.py:33`'s pinned spelling at the string the skill will then carry; ⛔ **and WIDEN the existing check's population to `src/**/SKILL.md`** |
| **Acceptance** | ⛔ **The widened check is run in all three of Ruling 123's readings.** ⭐ Reading 1 (live tree, all **3** `SKILL.md` under `src/`) → PASS. ⭐ Reading 2 — ⛔ **the plant is a fenced `studyforge validate` in `reconnaissance/SKILL.md`, which is the shape the clause FORBIDS** (Ruling 140) → CAUGHT. ⭐ Reading 3 — a `SKILL.md` with no fences at all → a reading DIFFERENT from row 1 |
| ⚠️ **Its collision, named at wave-open** | ⛔ **`SK-08` is authoring `skills/delivery` and its `SKILL.md` joins this population on merge — 3 today, 4 predicted.** ⭐ **`W61` first, then `SK-08` re-measures; or one dispatch** |
| **When** | ⛔ **NEXT 1.** ⭐ **A wrong green, in an artifact an agent EXECUTES, with a third instance being authored right now** |

#### ⛔ `W62` — MINTED. **The 41 latent `Owns` cells, and a trigger that cannot be shelved**

| | ⛔ **`W62`** |
|---|---|
| **From** | Ruling 136's residue, after this round closed the nine live ones |
| **Owner** | ⭐ **the PO** — `Owns` cells are this board's and the epics' |
| **Owns** | `docs/tasks/E00`…`E13`, the `Owns` field only |
| ⛔ **Population, derived not quoted** | **41** cells naming a `.py` that RESOLVES today, across 11 epics. ⛔ **Every one is a prediction R11 guarantees will expire; none is broken yet** |
| **What** | ⭐ Rewrite each into one of Ruling 136's three durable forms. ⛔ **Mechanical, one commit, no judgement calls except where a cell names a `.py` that does not exist AND has no directory** — those are FORWARD-looking cells for unbuilt tasks and are rewritten to the module form too |
| ⛔ **Its trigger, and why it is not a start condition** | ⭐ **It runs at a wave OPEN, BEFORE that wave's rows are dispatched.** ⚠️ **The only real risk is a developer holding a brief built from a cell this row rewrites, and a brief is built at dispatch** — ⛔ **so a trigger that fires every round cannot be shelved the way `W34`'s *no build task in flight* has been for seven** |
| ⚠️ **Not this round** | ⛔ **`SK-08` is authoring against `E11`'s definition right now.** ⭐ **`E11` holds no member of the nine, so the live class was closable without touching it; the latent sweep is not** |

### ⛔ ROUND 31 — findings

| id | marker | finding |
|---|---|---|
| **`PO-31/1`** | `[structural]` | ⛔ **CHECK 3 CAME BACK 0 OF 11.** **Measured** `git grep -In "Ruling <n>\b" e309172 -- docs \| cut -d: -f2 \| sort -u` for each of 132–142, `wt/po31`, 2026-09-10 → **eleven identical answers, all `docs/tasks/handoffs/CTO-2026-09-10-round38.md`** — **[measured]**. ⭐ **All eleven carried in this commit.** ⚠️ **The second half is mine: I predicted *11 of 11* from round 30's 3-of-3.** ⛔ **Rounds 28/29/30/31 read `1 of 6`, `0 of 4`, `3 of 3`, `0 of 11` — the median is near zero and the most recent reading is the worst possible prior.** ⭐ **Inheriting a reading is the error this board files against others, committed here in the row that measures it** |
| **`PO-31/2`** | `[local]` | ⛔ **The step-2.2 table's column header read *"STATE @ `ddddd05` (round 29, re-taken)"* while three of its four cells had been re-taken at `8146bdb` under it.** **Measured** `grep -n 'STATE @ .ddddd05.' docs/tasks/BOARD.md` → **1 line**, whose own `SK-05` cell says *"Measured at `8146bdb`"* — **[measured]**. ⭐ **Header replaced with `e309172` and every cell re-taken there.** ⚠️ **Same class as `PO-31/6`, in a different office's document, in the same round** |
| **`PO-31/3`** | `[structural]` | ⛔ **The `Owns`/`.py` class is NINE, not two, and seven of the nine nobody had named.** **Measured** — for every `.py` in an `Owns` cell that does not resolve, does a directory of the same stem exist — `wt/po31` @ `e309172` → **9** before the edit, **0** after — **[measured]**. ⭐ **Ruling 136's *kill it at source* argument is stronger at nine than at two.** ⚠️ **41 more are latent and are `W62`** |
| **`PO-31/4`** | `[structural]` | ⛔ **Derivation A reads ZERO for the first time, and the nearest miss has headroom TWO.** **Measured** in the pinned image @ `e309172` → `A_ROWS=0`, `B_ROWS=0`; nearest miss `tests/studyforge/corpus/container/test_document.py` **598/600** — **[measured]**. ⚠️ **One added test case breaks R11 there and it is nobody's task.** ⭐ **Recorded rather than rowed: Ruling 100 already makes *split at pick-up* the default, so a new id would add a gate, not a rule** |
| **`PO-31/5`** | `[local]` | ⛔ **Ruling 139 names `agent-protocol.md` as its home and Ruling 131 as its neighbour, and those are two documents.** **Measured** `git grep -n 'Ruling 131' -- docs/conventions/` → **`review-rubric.md:1219`, one file, not `agent-protocol.md`** — **[measured]**. ⭐ **Carried into the file the ruling NAMED (twice, including in its row table) and cross-referenced from Ruling 131's section.** ⚠️ **This is check 3's *read the neighbouring rulings in that artifact* firing on the ruling that created the need for it** |
| **`PO-31/6`** | `[local]` | ⛔ **`SK-05`'s `400` was ALREADY WRONG at the ref its own header names — `CTO-38/1`'s *stale by one commit* is too generous.** **Measured** `git show 5e947de:tests/test_authoring_reference.py \| wc -l` → **414**; `git merge-base --is-ancestor 7608057 5e947de` → **YES** — **[measured]**. ⭐ **Annotated beneath the handoff, never edited (Ruling 106).** ⚠️ **A stale reading is visible by diffing the named ref against the tip; a reading taken at an EARLIER, unnamed ref is not — and it survived a review for exactly that reason** |
| **`PO-31/7`** | `[local]` | ⭐ **Ruling 136 RESTORES a definition rather than tightening one, and that changes who owns the migration.** **Measured** `grep -n 'Owns' docs/tasks/README.md` → **`:361` — *"The package this task creates. One task, one surface."*** — **[measured]**. ⛔ **Nine cells violated their own field's definition, so *when a convention tightens, the tightening owns the migration* does NOT apply and nothing anyone did was licensed by the old spelling** |
| **`PO-31/8`** | `[structural]` | ⛔ **`W34`: `review-rubric.md` is **2245** lines at `e309172`, the SEVENTH consecutive round of growth — 1611 → 1784 → 1881 → 1951 → 2015 → 2068 → 2245 — and my own two carries this round push it to **2293**.** **Measured** `wc -l docs/conventions/review-rubric.md` — **[measured]**. ⚠️ **Its start condition *no build task in flight* is UNMET for the seventh time (`SK-08`).** ⛔ **`PO-24/8`'s remedy was owed by the next round to touch the row and this round touched it TWICE without discharging it.** ⭐ **Named, not fixed: re-routing `W34` is a scope decision and the CTO owns the rubric** |
| **`PO-31/9`** | `[none]` | ⭐ **A negative result with no cost, recorded so it is not re-run: a HOST run of the suite at `e309172` reads `3864 passed, 13 skipped` against the pinned image's `3814 / 63`.** **Measured** both in `wt/po31`, 2026-09-10 — **[measured]**. ⛔ **The 50-test difference is exactly the visual population, and the HOST's reading is the one that looks better** — ⭐ **which is why Ruling 40 is *pinned container only* and not a preference** |

---

## ⛔ ROUND 30 — nine rows owed and every one landed, `W51` re-priced, and a defect ahead of the tasks that would ship it

⭐ **Measured at `8146bdb`, branch `chore/po-round30`, linked worktree `wt/po30`,
pinned image (Ruling 40)** — ⛔ **the ref AND the checkout** (Ruling 108).
⚠️ **Every reading below was RE-DERIVED here; where one arrived from the CTO it
is labelled `[RECEIVED]` (Ruling 115), and three of the received numbers came
back DIFFERENT.**

⛔ **THE TIP DID NOT MOVE UNDER THIS ROUND.** ⭐ **`git rev-parse HEAD` in
`wt/po30` read `8146bdb` at open and at close.**

| | ⛔ **`8146bdb`, `wt/po30`, pinned image** |
|---|---|
| suite | ⭐ **3759 passed, 63 skipped**, exit **0** |
| floor | ⭐ **`quality floor: clean`**, exit **0** — ⛔ **`$?` taken with NO pipeline** |
| pointers | **141 read in 188 markdown files, 59 carrying an anchor, 0 unresolved** (`wt/po30`) · **189 files** in MAIN, the extra being `ONBOARDING.md` |
| lint | ruff 0.16.6 `check` clean, `format --check` clean, **535** files (`wt/po30`) · ⭐ **536** in MAIN |
| index | **`none — none in this checkout`** (`wt/po30`) · ⭐ **`fresh — built at 8146bdb4`** (MAIN, measured by me) |

⛔ **All 63 skips NAMED with `-rs` and summed rather than eyeballed** — ⚠️ **the
`SKIPPED [n]` prefix is a COUNT, so `sort | uniq -c` on the lines returns **29**
and is the wrong instrument; `awk` summing the bracketed numbers returns 63:**
55 `tests/visual/` (31 `test_contrast.py`, 7 `test_offline.py`, 7
`test_capture.py`, 5 `test_no_script.py`, 5 `test_keyboard.py`), 5
`tests/docker/test_dev_image.py`, 3 `tests/test_knowledge_index.py`.
⭐ **Identical to round 29's three groups, member for member.**

### ⛔ ROUND 30 — the six wave-open checks, each with its NAMED instrument and its READING

⭐ **Run at `8146bdb`, `wt/po30`, pinned image, except where a row names another
checkout.** ⚠️ **Ruling 128 applied to every row: where a reading is a COUNT the
POPULATION is printed beside it, and the EXPECTED reading is written down BEFORE
the command runs.**

| # | Check | ⛔ **Instrument** | ⭐ **Expected, written first** | ⭐ **Reading @ `8146bdb`** |
|---|---|---|---|---|
| **1** | index present and current | `docker/dev/check python3 -m tools.quality`, the `knowledge index:` line, **per checkout** | MAIN `stale` (it was stale all of round 29); `wt/po30` `none` | ⭐ **PASSES, and MAIN DISAGREED WITH MY EXPECTATION IN THE GOOD DIRECTION.** MAIN → **`fresh — built at 8146bdb4`**; `wt/po30` → `none — none in this checkout` (Ruling 108; the floor says this is not a failure). ⛔ **`PO-29/1` is DISCHARGED — the CTO rebuilt it after their merges, which is the remedy that finding named** |
| **2** | the `[structural]` triage sweep | ``git grep -EIc '`\[(local\|structural\|none)\]`' 8146bdb -- docs``, then `wc -l` for files and `awk -F: '{s+=$NF}'` for lines | ≥ 583 lines / ≥ 95 files (round 29's reading) | ⭐ **621 lines / 99 files**, up **+38 / +4** in one wave. ⛔ **The `[structural]` half alone is **382 lines in 98 files**, and it is the population `W37` is queued ninth against** |
| **3** | every ruling reached an artifact | `git grep -In "Ruling <n>\b" 8146bdb -- docs \| cut -d: -f1 \| sort -u` — ⛔ **FILES, not a count** | ⛔ **0 of 3.** ⚠️ **Written before the run, from three rounds of precedent** | ⭐ **3 OF 3, AND THE PREDICTION WAS WRONG.** 129 → `review-rubric.md` (1) + the round-37 handoff (3); 130 → rubric (2) + handoff (5); 131 → rubric (1) + handoff (2). ⛔ **The CTO carried all three themselves, in their own commit.** ⚠️ **`PO-30/1` is the caveat: the carrier is the rubric in all three cases and NONE reached this board, which is correct for 129 and 131 and NOT for 130 — [rowed below](#round-30-what-i-struck-and-what-i-rowed)** |
| **4** | what moved since the last run | `git log --oneline --merges ddddd05..8146bdb`, then every row whose fact that touches | 4 merges, 3 stale rows | ⛔ **5 merges (16 commits) and SIX stale rows.** ⭐ **Enumerated below the table** |
| **5** | `CLAUDE.md`'s *Where to start* | `grep -n 'Where to start' -A14 CLAUDE.md`, read against this board's head | *In flight: M2 step 2.2* | ✅ **PASSES, second round running.** ⭐ **It reads *"M2 step 2.1 closed… Open: M2 — a corpus is readable. In flight: M2 step 2.2"*, and step 2.2 is still open at `8146bdb`: `SK-05` is authoring and `SK-08` was unblocked this round.** ⛔ **No milestone or step closed under this round, so the file needed no edit — which is the first round that has been true** |
| **6** | the two-PO channel | `git -C ../<repo> rev-parse --short HEAD` ×4; `grep -c '^### ' docs/integration-catalogue.md`; `[ -d <repo>/docs/studyforge ]` | 4 unchanged refs, 19 entries | ✅ **NOTHING NEW OWED, NOTHING MOVED.** `../ISO-8583-jPOS-tutorial` @ `6c8dc85` (**ninth** run at that ref), `../Claude-senior-java-engineer` @ `c9cf522`, `../Claude-SPARQL-tutorial` @ `b9aa89b`, `../CodeSignal` @ `49c11d5e`; only the first carries `docs/studyforge/`; catalogue **19** |

#### ⛔ Check 4 — the six stale rows, and one of them is the head's own summary

⭐ **`PO-29/6`'s named population is applied for the first time: the HEAD's own
summary paragraphs are re-taken at every run, because a reader stops at the first
copy and that is the copy nobody re-measures.**

| # | Where | ⛔ **What it said at open** | ⭐ **Corrected to** |
|---|---|---|---|
| 1 | head — `📏 BASE` | *"round 29: 3522 / 63 @ `ddddd05`"* | ⛔ **3759 / 63 @ `8146bdb`, REPLACED not appended, and the lint denominator now carries the DERIVATION** |
| 2 | head — in flight | *"`SF-13` and `SK-07` at `ddddd05`"* | ⛔ **BOTH MERGED.** ⭐ **Now `SK-05` and `W40`, both with 4 commits** |
| 3 | head — next two rows | *"`SK-05` then `W40`, placed not dispatched"* | ⛔ **BOTH TAKEN.** ⭐ **Re-placed: `W57`, `SK-08`** |
| 4 | head — step 2.2 | *"NOT four parallel rows: `SK-08` Depends on `SK-07`"* | ⭐ **The edge is DISCHARGED by `SK-07` landing, not by renumbering — which is what round 28's refusal to invent a 2.3 was betting on** |
| 5 | step 2.2 table, four cells | `SF-13` and `SK-07` `in-progress`; `SK-05` `todo`; `SK-08` `BLOCKED` | ⭐ **`done` · `done` · `in-progress` · `todo`, FREE** |
| 6 | ⛔ **`W51`'s *When* cell** | *"BEFORE `SK-07`, the THIRD package that will read a corpus root"* | ⛔ **STRUCK — the antecedent is FALSE and `SK-07` never joined the population.** ⭐ **Re-priced by members** |

### ⭐ And the seventh, standing from Ruling 113 — the R11 deferral sweep

⛔ **EXPECTED, WRITTEN BEFORE THE RUN: ZERO ROWS.** ⚠️ **`W44` deleted the tree's
last marker at `7b5c0a9` and two branches have merged into `src/` since.**

```text
§3c ast sweep (W40's derivation B), pinned image, wt/po30 @ 8146bdb  ->  B_ROWS=0   [as expected]
git grep -l 'Size exception:' -- src/                               ->  (nothing)  [corroborator]
git grep -l 'Size exception:' -- src/ | wc -l                       ->  0

and the population the `| wc -l` conceals, printed once (Ruling 128):
git grep -l 'Size exception:' -- src/ tools/ tests/                 ->  4 files
    tools/quality/config.py              tools/quality/size.py
    tools/tests/quality/test_config.py   tools/tests/quality/test_size.py
```

⭐ **Four members, every one the checker's own package, on a tree with ZERO
deferrals — unchanged from round 29 across two `src/` merges.**

### ⭐ ROUND 30 — THE NEXT TWO ROWS, `Owns` verified at `8146bdb`, and the R11 pre-dispatch sum

⛔ **PLACED, NOT DISPATCHED.** ⚠️ **`SK-05` (`feat/SK-05-authoring`, `wt/dev2m`,
4 commits) and `W40` (`chore/W40-ceiling-population`, `wt/dev3c`, 4 commits) are
BOTH IN FLIGHT — measured with `git worktree list` plus `git log --oneline
release/m0-foundations..<branch>`, and ⛔ NOT with `git branch --no-merged`,
which Ruling 130 says enumerates unmerged COMMITS.**

| | ⭐ **Row** | ⛔ **Why it, and why in this order** |
|---|---|---|
| **NEXT 1** | ⛔ **`W57`** — `SAFE_SCHEMES` refuses a bare same-directory relative href | ⛔ **A SEQUENCING DECISION, and it is mine to take.** ⭐ **6 of 13 navigation slots dropped silently in SHIPPED `render/page/text.py`, under `sibling` placement, measured by two people.** ⚠️ **The tasks that would first render a full bar are `SF-15` (owns `render/page/navigation.py`), `SF-27` and `SF-14`; if any of them lands first it renders a SHORT BAR and PASSES its own acceptance doing it.** ⭐ **Small, one closed set and its mirror, and it does not re-open M1 (Ruling 97: the bar did not exist at `2fe56a4`)** |
| **NEXT 2** | ⭐ **`SK-08`** — delivery planning | ⭐ **Step 2.2's LAST product row, and `SK-07`'s merge is what freed it.** ⛔ **It has waited two waves inside its own step, which is precisely the `PO-20/2` shape Ruling 75 exists to make visible — and this time the wait is being ENDED rather than extended by a newer row** |

#### ⛔ `Owns` verified against the TREE at `8146bdb`, and `PO-26/1`'s R11 pre-dispatch sum

| | `W57` | `SK-08` | ⏳ `SK-05` (in flight) | ⏳ `W40` (in flight) | ⛔ **shared** |
|---|---|---|---|---|---|
| `src/` | `render/page/text.py` (**171**/400) | ⭐ **`skills/delivery/` — 0 files at `8146bdb`, greenfield** | ⭐ **none — no Python at all** | `corpus/manifest/content.py` (**400**/400) | ⭐ **none** |
| tests | `tests/studyforge/render/page/test_text.py` (**114**/600) | ⭐ **none yet — mirror is created by the row** | ⭐ **none** | `tests/test_gate_coverage.py` (**600**/600) | ⭐ **none** |
| `docs/` | ⭐ **none** | `docs/integration-catalogue.md` (**414**) + the capability index | `docs/authoring/` (**0 files**) | ⭐ **none** | ⭐ **none** |
| **Intersection** | | | | | ⭐ **∅, all four pairwise** |

⭐ **Derivation A run here and PRINTED IN FULL, rather than read off a cell:**

```text
src/studyforge/corpus/manifest/content.py    400/400   headroom 0
tests/test_gate_coverage.py                  600/600   headroom 0
A_ROWS= 2
   nearest miss:  tests/studyforge/corpus/container/test_document.py  598/600  headroom 2
   nearest miss:  src/studyforge/archive/scrub.py                     384/400  headroom 16
   nearest miss:  tests/docker/test_dev_image.py                      583/600  headroom 17
Derivation B (Ruling 113's ast sweep) -> B_ROWS=0 , so A - B = A.
```

⛔ **BOTH members of `A − B` ARE `W40`'S OWN SUBJECTS, and `W40` is in flight
against them right now** — ⭐ **its branch has already turned both into packages
(`8d7251e`).** ⚠️ **So the sum's answer is that neither new row may touch either
file, and neither does: `W57` grows `render/page/`, `SK-08` grows a package that
does not exist.**

#### ⛔ Ruling 75 — what `W57` jumps, named

⭐ **`W57` goes to the FRONT of the queue and jumps TWELVE older unstarted
rows — `W32`, `W34`, `W35`, `W36`, `W37`, `W38`, `W41`, `W42`, `W48`, `W50`,
`W51`, `W53`.** ⛔ **The licence is the only one this board accepts: a MEASURED
cost.** ⚠️ **6 of 13 slots on the `depth2` corpus, 46 % of the between-units bar,
in code that has already shipped, with a negative control run negatively — the
identical href prefixed `./` survives, so the refusal is precisely the missing
bare-relative case and nothing about the filename.** ⭐ **And the cost of NOT
jumping is not a delay, it is a WRONG GREEN: the next renderer to land passes its
acceptance while dropping half the bar.**

#### ⛔ ROUND 30 — `W51` re-priced by members, and my population is wider than the CTO's

⭐ **The CTO reconciled `SK-07/4` (*the count is two*) against `SF-13/2` (*its
third and fourth consumer have arrived*) and found both correct about different
populations.** ⛔ **I re-derived all four at `8146bdb` rather than inheriting
them, and one term came back LARGER:**

```text
A. literal definitions of the archive directory name          -> 3 under 2 names
     src/studyforge/validate/corpus.py:58        ARCHIVE_DIR      (the owner)
     src/studyforge/skills/adapter/layout.py:57  ARCHIVE_DIR
     src/studyforge/corpus/placement/names.py:71 ARCHIVE_DIRNAME  <- a THIRD SPELLING
   (and validate/corpus.py:231 ARCHIVE_ROOT_NAME = "raw", the row's second constant)

B. cross-package reaches into a submodule for it              -> 1
     src/studyforge/cli/plan/derive.py:44  from studyforge.validate.corpus import ARCHIVE_DIR
   studyforge.validate.__all__ is 9 names and neither constant is one of them.

C. copies of the container-map walk                           -> 12   [CTO measured 9]
     src/studyforge/validate/corpus.py:135
     src/studyforge/cli/plan/derive.py:135
  ** src/studyforge/skills/adapter/parts/adapter.py:226   <- EMITTED into every adapter
     tests/studyforge/cli/plan/test_derive.py  x5
     tests/studyforge/contents/corpora.py:51
  ** tests/fixture_checks/corpus.py:66                    <- bare "container.json"
  ** tests/studyforge/corpus/container/test_document.py:85 <- bare "archive"/"container.json"
  ** tests/studyforge/corpus/placement/test_corpora.py:66  <- bare "archive"/"container.json"

D. src/studyforge/skills/onboarding/                          -> 0    [SK-07/4 CONFIRMED]
```

⛔ **The three members the CTO's instrument could not see spell the walk with
BARE LITERALS — `rglob("container.json")` under a literal `"archive"` — so a grep
for `rglob(CONTAINER_FILENAME)` returns 9 and the honest number is 12.**
⭐ **That is Ruling 128 in its own subject matter: a narrower instrument returns
a smaller scalar and neither run returns a disagreement.** ⚠️ **And the two
bare-literal test members are the defect `W51` exists for, wearing the shape the
row's own acceptance grep would miss — ⛔ so `W51`'s clause-1 instrument must
match BOTH spellings or it is a check that cannot fail.** ⭐ **`PO-30/3`.**

⛔ **The member that decides the slot is unchanged and is the CTO's:
`skills/adapter/parts/adapter.py:226` EMITS the walk into every generated
adapter**, so it propagates into repositories R3 forbids editing afterwards.
⭐ **`W51` is therefore priced AHEAD of `SK-09` (the next task that generates an
adapter) and BEHIND `W57` and `SK-08`.**

### ⛔ ROUND 30 — what I struck, and what I rowed

⭐ **All nine of the CTO's for-the-PO rows landed, plus their 9b. ⛔ Every one
reached an ARTIFACT — this board or an epic — and not one was left in a handoff
(Ruling 117).**

| CTO item | ⭐ **landed** |
|---|---|
| **1** — `SK-07`'s `OPS-*` acceptance clause | ⭐ **`E11`'s `SK-07` Acceptance SPLIT under Ruling 129: the met half stays, the `OPS-*` half is RE-HOMED onto `SF-28` in `E09` with the two registration points `SK-07` left for it (`artifacts.paths()` and `NOT_MATERIAL`).** ⛔ **Not deleted — R20's second instance after `SK-02/4`, and the residue is shown unmeetable by a command in the epic** |
| **2** — the onboarded corpus's graph | ⭐ **`W54` — MINTED.** ⛔ **`E11`'s Acceptance clause split in the same edit: the R3-safe ignore file half is MET and stays; the build-bridge-census half moves to the row, because `graphify` is not in the pinned image and `src/` may not import `tools/`** |
| **3** — `SK-02/3` widened | ⭐ **SPLIT ACROSS TWO CARRIERS, and I am saying so rather than minting a duplicate.** ⛔ **The PACKAGING half already has a row — `W50` — whose population I WIDENED from 2 to 3 in place. ⭐ The DECISION half (is an installed framework a supported host for an onboarded corpus?) had no carrier and is `W55`** |
| **4** — reconnaissance asks *why* | ⭐ **`W56` — MINTED.** `skills/reconnaissance/proposal._choices` gains one `Uncertainty` per excluded path |
| **5** — `W53` gains `PO-29/4` | ⭐ **`W53`'s row, as an ABSORBED clause, with the CTO's ratified bound quoted on it.** ⛔ **No `W54` for it; the high-water mark moved for the five NEW rows only** |
| **6** — `SAFE_SCHEMES` | ⭐ **`W57` — MINTED, and PLACED FIRST.** ⛔ **See the sequencing note below: the CTO's *ahead of `SF-12`/`SF-14`* is half-stale and I re-derived the real consumers** |
| **7** — `W51` re-priced | ⭐ **Ordering claim STRUCK in the cell; row re-priced by members, and my population is wider than theirs** |
| **8** — `W38`'s derivation | ⭐ **`W38`'s clause now carries `py + md − (py\|md under tests/fixtures/)` and says the third term is DERIVED AT EVERY REF.** ⛔ **The literal `8` is struck; it would mispredict `8146bdb` by 39** |
| **9** — round 29's pair both spent | ⭐ **Recorded at the head, and RE-MEASURED: `CTO-37/3` had `W40` at ZERO commits and it has four.** ⛔ **`PO-30/2`** |
| **9b** — the `[none]` marker | ⭐ **`W58` — MINTED.** ⛔ **And the population came back BIGGER than the CTO's, in a way that changes the row's shape — `PO-30/4`** |

#### ⛔ Item 6 is a SEQUENCING decision, and the CTO's naming of it is half-stale

⚠️ **The CTO wrote *"ahead of `SF-12`/`SF-14`"*.** ⛔ **`SF-12` is DONE — merged
`f4aa603`, and M1 closed on it at `2fe56a4`** — ⭐ **so half of that instruction
names a task no ordering can be ahead of.** ⛔ **A sequencing instruction that
names a merged task is the stale-conditional class one door along, and it would
have read as satisfied on inspection.**

⭐ **So I re-derived the real consumers rather than accepting the pair:**

```text
who renders the bar today   src/studyforge/render/page/document.py:117
                              nav=_region(navigation.between_units(links))
who supplies `links`        NOBODY in src/  — the caller that turns
                            contents/order.py:150 `links()` into
                            render.page.navigation.Links does not exist yet
the task that owns it       SF-15 — Owns render/page/navigation.py, step 2.4,
                            Depends on SF-12 (done) + SF-13 (done)  <- FREE TODAY
the other two consumers     SF-27 (container page, step 2.3), SF-14 (root index, step 2.3)
```

> ⛔ **THE ORDERING, RULED: `W57` lands BEFORE STEP 2.3 OPENS.** ⭐ **That is
> strictly stronger than *ahead of `SF-14`* and it is the honest bound, because
> the first task that can pass `links=` is `SF-15` and its two dependencies are
> BOTH ALREADY MERGED** — ⚠️ **`SF-15` is a `solo` row sitting in step 2.4 with
> nothing blocking it, so *ahead of `SF-14`* would not have covered it.**
> ⛔ **`PO-30/5`.**

### ⛔ FIVE ROWS MINTED — `W54`, `W55`, `W56`, `W57`, `W58`

⛔ **High-water mark moves `W53` → `W58`; measured across every branch in the
repository at `8146bdb` — `git grep -In '\bW5[4-9]\b' $(git rev-list --all) --
docs` returns hits in three files and EVERY ONE of them is a refusal to mint
`W54`, not a mint.** ⭐ **`W28` and up are minted by the PO only, and this is the
mint.**

#### ⛔ `W54` — MINTED. **`SK-07`'s graph clause cannot be met by any framework task as written**

| | ⛔ **`W54`** |
|---|---|
| **What** | ⭐ **The onboarded corpus's knowledge graph is BUILT, BRIDGED and its doc↔code census ASSERTED — by an artifact that lives OUTSIDE `src/`.** ⛔ **Two admissible shapes and the row picks one: (a) a `tools.knowledge` entry point the onboarding PROCEDURE invokes, or (b) a `cli/` onboarding command that shells out to a pinned binary** |
| **From** | ⛔ **`SK-07/2`, ruled and scheduled by CTO round 37 (item 2), under Ruling 129** |
| **Owner** | framework agent, **queued** |
| ⛔ **Owns** | ⭐ **`tools/knowledge/` (or `src/studyforge/cli/`, if shape (b) wins) and its mirror**, plus the `SKILL.md` procedure line in `src/studyforge/skills/onboarding/` |
| ⛔ **WHY IT IS A ROW AND NOT A BUG IN `SK-07`** | ⭐ **`graphify` is measurably NOT in the pinned image and `src/` may not import `tools/`** — the same rule that made `SK-02` re-declare `SOURCE_LINE_CEILING` rather than import `tools.quality.config`. ⛔ **So NO framework task can ever close `E11`'s clause 9 as it was written**, and the developer reported it instead of patching it, which is the working agreement working |
| ⭐ **What is ALREADY MET and stays in `E11`** | ⛔ **The R3-safe ignore file: `graphify-out/.gitignore` containing a single `*`, written INSIDE the generated directory, with the repository's root ignore file byte-identical to before.** ⚠️ **That half is asserted today; only the build-and-census half moves** |
| ⛔ **Acceptance — clause 1's two columns** | **claim:** an onboarded corpus's graph exists, is bridged, and its doc↔code edge census is non-zero. ⭐ **instrument:** ⛔ **run it on a fixture corpus and assert the census; watched to FAIL FIRST against an UNBRIDGED graph, which returns exactly **0** doc↔code edges** — ⚠️ **`FND-02` measured that zero on the Java corpus (13,583 code↔code, 767 doc↔doc, **0** doc↔code), so the failing reading is already known and the test may not be green on its first run |
| ⛔ **When** | ⭐ **Behind `W57` and `SK-08`; AHEAD of the first corpus onboarded for real, because a corpus onboarded without it has no index and R14's budgets then bind on a repository nothing built one for** |

#### ⛔ `W55` — MINTED. **`SK-07`'s skill stubs resolve only against a checkout, and nothing refuses the installed case out loud**

| | ⛔ **`W55`** |
|---|---|
| **What** | ⭐ **A DECISION, written down, plus whatever code the decision costs: is an INSTALLED `studyforge` a supported host for an onboarded corpus at all?** ⛔ **Today `SK-07` writes stubs pointing at `../studyforge/src/studyforge/skills/<name>/SKILL.md`, which resolves against a sibling CHECKOUT and points at NOTHING against an installed package — silently** |
| **From** | ⛔ **`SK-07/3`'s worse half, scheduled by CTO round 37 (item 3).** ⭐ **The PACKAGING half is `W50`'s and I widened that row rather than duplicating it here** |
| **Owner** | framework agent, **queued** |
| ⛔ **Owns** | ⭐ **`src/studyforge/skills/onboarding/` (the stub writer) and whatever the decision lands in — `docs/conventions/workspace.md` if the answer is *sibling checkout only*** |
| ⛔ **Why the decision cannot be skipped** | ⭐ **The pin already says `"where": "sibling"`, so the supported arrangement IS declared** — ⚠️ **but a declaration that nothing enforces is exactly the gap `W37` sweeps for.** ⛔ **The two honest outcomes are opposite and both are cheap: either the stub RESOLVES for an installed package (which needs `W50`'s glob first), or onboarding REFUSES the installed host by name at the moment it writes the stub** |
| ⛔ **Acceptance — clause 1's two columns** | **claim:** an onboarded corpus's skill stub either resolves or refuses, and never points at nothing. ⭐ **instrument:** ⛔ **onboard a fixture corpus with the framework NOT importable from a sibling checkout; assert the emitted stub's target either exists or the run exits non-zero naming it** — ⚠️ **watched to FAIL against today's code, which emits a dangling path and exits 0** |
| ⛔ **When** | ⭐ **Behind `W50`, whose glob is the precondition for the *resolves* branch.** ⚠️ **Exposure is nil until something installs the package, which is `W50`'s trigger too** |

#### ⛔ `W56` — MINTED. **Reconnaissance never asks WHY a file is withheld, and the integrator meets the refusal from a different skill**

| | ⛔ **`W56`** |
|---|---|
| **What** | ⭐ **`skills/reconnaissance/proposal._choices` raises ONE `Uncertainty` per excluded path, carrying *what would settle it* — the shape that module already uses for its other three** |
| **From** | ⛔ **`SK-07/6`, scheduled by CTO round 37 (item 4).** ⭐ **A SEAM defect, not a bug in either module** |
| **Owner** | framework agent, **queued** |
| ⛔ **Owns** | ⭐ **`src/studyforge/skills/reconnaissance/proposal.py` and its mirror** — ⚠️ **it was outside `SK-07`'s `Owns` and they reported it** |
| ⛔ **The mechanism, measured by the finder** | ⭐ **`proposal._content` returns `content.exclude` as BARE PATH STRINGS; `manifest.content._exclude_of` requires an object with `path` AND a `why` of at least `MIN_WHY_CHARS`.** ⛔ **Each half is correct about its own contract and the mismatch exists only in the traversal between them** — ⚠️ **so a survey that excludes anything hands over a draft that CANNOT BE PROMOTED, and the first thing the integrator learns is a refusal from a skill they were not using** |
| ⛔ **Why it is not left to `promote`** | ⭐ **`promote` already names every unreasoned path at once, so the cost is one round trip rather than *n* — ⚠️ which is why this is a row and not an emergency.** ⛔ **But the question should be asked where the material is OPEN, by the skill that has it open; asking it two skills later is asking a person to remember why they excluded something they read yesterday** |
| ⛔ **Acceptance — clause 1's two columns** | **claim:** a survey that excludes a path produces a draft that `promote` accepts. ⭐ **instrument:** ⛔ **survey a fixture corpus with an exclusion, promote the draft, assert exit 0; watched to FAIL against today's code, which raises on the missing `why`** |
| ⛔ **When** | ⭐ **Behind `W57` and `SK-08`; AHEAD of the first real reconnaissance run on a corpus with exclusions** |

#### ⛔ `W57` — MINTED. **`SAFE_SCHEMES` refuses a bare same-directory relative href, and it drops 6 of 13 navigation slots in shipped code**

| | ⛔ **`W57`** |
|---|---|
| **What** | ⭐ **A DECISION about what a permitted href is, then the one-line consequence: `render/page/text.py`'s `SAFE_SCHEMES` is `("http://", "https://", "mailto:", "#", "/", "./", "../")` and has NO entry for a relative href naming a file in the SAME directory** |
| **From** | ⛔ **`SF-13/1`, CONFIRMED AND WIDENED by the CTO at round 37, scheduled as their item 6** |
| **Owner** | framework agent, **PLACED NEXT 1 this round** |
| ⛔ **Owns** | ⭐ **`src/studyforge/render/page/text.py` (**171**/400) and `tests/studyforge/render/page/test_text.py` (**114**/600)** — ⚠️ **both measured at `8146bdb`; headroom is not a factor on either** |
| ⛔ **THE MEASURED COST, and it is why this row jumps twelve** | ⭐ **`SF-13` measured ONE slot; the CTO re-measured the whole `depth2` population and got **13 slots, 6 dropped** — every same-container *next* AND *previous*, **46 %** of the between-units bar under `sibling` placement, SILENTLY.** ⛔ **`navigation._link` drops a link whose scheme is refused rather than rendering dead text, so the slot vanishes from the page with nothing raised.** ⭐ **Negative control run negatively: the identical href prefixed `./` SURVIVES, so the refusal is precisely the missing bare-relative case and nothing about the filename** |
| ⛔ **It does NOT re-open M1** | ⭐ **Ruling 97: the bar did not exist at `2fe56a4`.** ⚠️ **M1's close condition 8 VOIDED the bar as unfalsifiable — `between_units(None)` returned `""` and no caller passed `links=` — so the close was right and this defect was not observable there** |
| ⛔ **Acceptance — clause 1's two columns** | **claim:** every slot `contents/order.py:links()` computes survives `safe_href` under BOTH placement profiles. ⭐ **instrument:** ⛔ **render the `depth1` (`tree`) and `depth2` (`sibling`) fixture corpora and assert the slot count per page equals the count `links()` returned** — ⚠️ **watched to FAIL FIRST: today `depth2` returns 13 and renders 7** |
| ⛔ **The closed-set rule is NOT relaxed** | ⭐ **The docstring's argument stands and the row may not answer this by switching to a denylist:** *"a closed set of what is permitted, never a list of what is refused: the forbidden list is the one that is silently incomplete, and `vbscript:` is the entry every version of it forgets."* ⛔ **The remedy widens the ALLOWED set with a rule a reviewer can state, not with an exception** |
| ⛔ **When** | ⛔ **BEFORE STEP 2.3 OPENS — [and that bound is stronger than the CTO's, for a measured reason](#item-6-is-a-sequencing-decision-and-the-ctos-naming-of-it-is-half-stale).** ⭐ **Ruling 75 — it jumps `W32`, `W34`, `W35`, `W36`, `W37`, `W38`, `W41`, `W42`, `W48`, `W50`, `W51`, `W53`, and the licence is a MEASURED cost in SHIPPED code** |

#### ⛔ `W58` — MINTED. **The zero marker standing beside a real finding is a build failure, and today the checker cannot see a single instance**

| | ⛔ **`W58`** |
|---|---|
| **What** | ⭐ **`tools/quality/handoffs/` gains the assertion Ruling 105's vocabulary already implies: ⛔ a document carrying `` `[none]` `` beside a `` `[local]` `` or `` `[structural]` `` finding FAILS the floor.** ⚠️ **A recorded negative is written as a local finding whose text opens *A NEGATIVE result*; `` `[none]` `` is only ever the way to write ZERO findings** |
| **From** | ⛔ **`CTO-37/11`, scheduled as their item 9b.** ⭐ **REFUSED absorption into `W53` under the CTO's own ratified bound — it is not a condition on an author shipping a clause that names an instrument — ⚠️ which is the bound costing its author a row rather than saving them one** |
| **Owner** | framework agent, **queued** |
| ⛔ **Owns** | ⭐ **`tools/quality/handoffs/contract.py` (`check_markers`) and `tools/quality/handoffs/__init__.py` (`check_handoffs`, `DOCUMENT_KINDS`), plus their mirrors under `tools/tests/quality/`** |
| ⛔ **THE POPULATION, RE-DERIVED BY ME AND BIGGER THAN THE ROUTING SAID** | ⭐ **The CTO measured **17 in 5 documents**, all handoffs. ⛔ **At `8146bdb` I measure **25 finding-marker instances in 7 documents**, plus 2 more in the two convention files where the marker is the RULE'S OWN DEFINITION and is legal:** `CTO-…round33` 5 · `CTO-…round34` 6 · `CTO-…round35` 2 · `CTO-…round36` 3 · `PO-…round27` 1 · ⛔ **`PO-…round29` 2 (mine)** · ⛔ **`BOARD.md` 6 (this file)**. ⚠️ **Every one of the 7 also carries real findings — `BOARD.md` carries 44.** ⭐ **Documents where it stands ALONE, which is the legal use: ZERO. Impossible-spelling control: 0** |
| ⛔ **AND THE READING THAT SHAPES THE ROW: THE CHECKER CANNOT SEE ONE OF THEM** | ⭐ **`check_handoffs` walks `docs/tasks/handoffs/**.md` ONLY, and `check_markers` runs only when the declared kind is `task handoff`.** ⛔ **All six offending handoffs declare `ruling record`; `BOARD.md` is outside `HANDOFF_DIR` entirely.** ⚠️ **Measured: **51** of **109** documents in `HANDOFF_DIR` declare `task handoff`, so **58** skip `check_markers` outright.** ⛔ **So the naive remedy — one assertion inside `check_markers` — IS A CHECK THAT CANNOT FAIL on today's tree, which is `W37`'s exact class committed inside the row that fixes a vocabulary defect.** ⭐ **`PO-30/4`** |
| ⛔ **What the row must therefore do** | ⭐ **Widen the POPULATION before adding the assertion** — the marker rule applies to any document that carries findings, which is every `DOCUMENT_KINDS` entry that can carry one, and to `BOARD.md`. ⚠️ **Whether `BOARD.md` comes into the floor's reach is the row's one real decision and it is named here rather than discovered** |
| ⛔ **Existing records are NOT edited** | ⭐ **Ruling 106.** ⛔ **The 25 instances stand; the tightening owns its migration by making a twenty-sixth unrepresentable.** ⚠️ **So the row's failing reading must be taken against a PLANTED instance in a temporary root, never against the live tree, and the row says so** |
| ⛔ **Acceptance — clause 1's two columns** | **claim:** a document carrying the zero marker beside a real finding fails `python3 -m tools.quality`. ⭐ **instrument:** ⛔ **plant one in a temporary root: the floor exits **1** with exactly one finding naming the document and the line; remove it and the floor exits **0**** — ⚠️ **and the new rule REPORTS ITS COVERAGE (how many documents it judged), not just its hits** |
| ⛔ **When** | ⭐ **Any time; small.** ⚠️ **Ruling 75: it jumps nothing — it is queued behind `W57`, `SK-08` and the `W50`/`W51` pair** |
| ⛔ **ABSORBED 2026-09-10 (round 31) — RULING 141** | ⭐ **`W58` SHIPS THE DERIVATION, NEVER THE NUMBER.** ⛔ **Quoted:** *"the `[none]` count is **not** the finding; the absent derivation is… `tools/quality/handoffs/__init__.py:254` skips `check_markers` entirely unless `kind == TASK_HANDOFF`, so the live enforcement population for this marker is zero over ruling records, and `BOARD.md` is outside `HANDOFF_DIR` altogether. `PO-30/4` is upheld."* ⚠️ **And the count came out THREE ways in one round — the CTO's brief said **17 in 5**, I measured **25 in 7**, their own grep over `docs/` read **31 in 10** — ⛔ and not one of the three shipped a deriving command.** ⭐ **So the row's deliverable includes the command that produces the population — *documents `check_markers` will run over after the widening* — printed IN FULL before it is reduced to a scalar (Ruling 128).** ⛔ **A row that lands a COUNT instead has re-created the defect it closed.** ⚠️ **No new id: absorbed, because Ruling 141 sharpens this row's shape rather than describing new work** |

### ⛔ ROUND 30 — findings

| id | class | ⛔ **finding** |
|---|---|---|
| `PO-30/1` | `[local]` | ⭐ **A NEGATIVE result, and it is the first time check 3 has come back clean. Rulings 129, 130 and 131 ALL reached an artifact.** **Measured** by me at `8146bdb`: `git grep -In "Ruling 129\b" 8146bdb -- docs \| cut -d: -f1 \| sort -u` → `docs/conventions/review-rubric.md` plus the round-37 handoff, and the same for 130 and 131 — **[measured]**, three commands. ⛔ **The CTO carried all three THEMSELVES, in the commit that minted them, which is Ruling 117 obeyed by its author.** ⚠️ **The caveat I am rowing rather than swallowing: the carrier is the RUBRIC in all three cases and none reached this board. That is correct for 129 and 131, which are review-gate rules — ⛔ it is NOT correct for 130, which is a DISPATCH rule the PO uses and the CTO does not.** ⭐ **Landed: the head's in-flight line now names its instrument and names `git branch --no-merged` as the one it refuses** |
| `PO-30/2` | `[local]` | ⛔ **`CTO-37/3`'s reading of `W40` was true when taken and false when I read it, and the gap is one wave.** **Measured** by them at `ddddd05`: `chore/W40-ceiling-population`, `wt/dev3c`, **0 commits** — *dispatched, nothing authored*. **Measured** by me at `8146bdb`: `git log --oneline release/m0-foundations..chore/W40-ceiling-population` → **4 commits**, head `0315516`, and `8d7251e` has ALREADY turned both zero-headroom modules into packages — **[measured]**, mine; **[RECEIVED: CTO-37/3]** for theirs. ⚠️ **NOT a defect against their round — it is the record-versus-claim rule at wave scale.** ⭐ **The honest sentence is theirs and I am keeping it: a worktree says a checkout exists, not that work is in flight — ⛔ and a commit count says work happened, not that it is still happening. Both are readings with an as-of** |
| `PO-30/3` | `[structural]` | ⛔ **`W51`'s reconciled population is understated by THREE, and the three the instrument missed are the ones its own acceptance grep would miss too.** **Measured** by me at `8146bdb`: `git grep -n 'rglob(CONTAINER_FILENAME)' -- src/ tests/` → **9**, which is the CTO's number; widening the pattern to `rglob("container.json")` under a literal `"archive"` → **12** — **[measured]**, both. ⛔ **The three extras are `tests/fixture_checks/corpus.py:66`, `tests/studyforge/corpus/container/test_document.py:85` and `tests/studyforge/corpus/placement/test_corpora.py:66`, and every one spells the archive root as a BARE LITERAL — which is precisely the defect `W51` exists to end.** ⭐ **Why `[structural]`: `W51`'s clause-1 instrument as written greps for the CONSTANT, so it can only ever find the members that already use the constant. ⛔ A check that finds only the compliant half of its population is a check that cannot fail, and it would ship inside the row that fixes the population.** ⚠️ **Rowed onto `W51` this round, in the cell** |
| `PO-30/4` | `[structural]` | ⛔ **The zero-marker enforcement has NO population inside the checker it was routed to, and the naive remedy is a check that cannot fail.** **Measured** by me at `8146bdb`: `check_handoffs` walks `docs/tasks/handoffs/**.md` only and `check_markers` runs only when `declared_kind` is `task handoff`; **51** of **109** documents in `HANDOFF_DIR` declare it, so **58** skip the marker check — and ALL SIX offending handoffs declare `ruling record` while `BOARD.md`'s **6** instances are outside the directory — **[measured]**, `grep -l '^\*\*Kind:\*\* task handoff'` and the reader in `tools/quality/handoffs/__init__.py:241`. ⛔ **So the live population inside `check_markers`'s reach is **ZERO**, and an assertion added there would be green on arrival and green forever.** ⭐ **Also: the routed count is 17 in 5 and the measured count is **25 in 7** — two of the extra eight are MINE (`PO-…round29`) and six are on THIS BOARD.** ⚠️ **`W58` carries both readings and names the widening as its first act** |
| `PO-30/5` | `[structural]` | ⛔ **A sequencing instruction named a task that had already merged, and it would have read as satisfied.** **Measured** by me at `8146bdb`: the CTO's item 6 says *ahead of `SF-12`/`SF-14`*; `SF-12` is `done`, merged `f4aa603`, and M1 closed on it at `2fe56a4` — **[measured]**, the board row and `git log`. ⛔ **And the pair is not the population: `git grep -n 'between_units' -- src/` shows `render/page/document.py:117` renders the bar and NOTHING in `src/` supplies `links`, so the FIRST task that can pass one is `SF-15` — a `solo` row in step 2.4 whose two dependencies (`SF-12`, `SF-13`) are BOTH MERGED, i.e. free today.** ⚠️ **`SF-14` is step 2.3 and renders the root index, which does not call `document.py` at all.** ⭐ **So *ahead of `SF-14`* would have left the actual first consumer uncovered.** ⛔ **Ruled: `W57` lands before step 2.3 opens, which covers `SF-14`, `SF-27` and `SF-15` together.** ⭐ **The class is `PO-29/4`'s one door along — a stale CONDITIONAL there, a stale ORDINAL here, and both read like live gates** |
| `PO-30/6` | `[local]` | ⭐ **A NEGATIVE result. `PO-29/1` is DISCHARGED and I checked the file rather than re-reporting it.** **Measured** by me at `8146bdb`, `docker/dev/check python3 -m tools.quality` in the MAIN checkout → **`knowledge index: fresh — built at 8146bdb4, and nothing it describes has moved since`** — **[measured]**. ⛔ **Round 29 measured `stale — built at 8821b118` and declined to rebuild another checkout's index; the CTO rebuilt it after their merges, which is the remedy that finding named and the office that owns the merge.** ⚠️ **Recorded because this board has re-reported an already-fixed defect three times from quotations inside old handoffs, and `delivery-flow.md` says the check goes BEFORE the report** |
| `PO-30/7` | `[local]` | ⛔ **The skip summary has a wrong instrument that returns a plausible number.** **Measured** by me at `8146bdb`: `grep '^SKIPPED' \| sed 's/:[0-9]*:.*//' \| sort \| uniq -c` returns **29**, because `pytest -rs` prefixes each line with `SKIPPED [n]` and `uniq -c` counts LINES, not tests; summing the bracketed `n` with `awk` returns **63**, which is what the runner reported — **[measured]**, both forms. ⭐ **Why it matters beyond this round: 29 is not obviously wrong, it is smaller than 63 and it is stable across runs**, so the wrong instrument would corroborate itself every wave. ⛔ **Ruling 128's subject with the population one level down: the summary is a reduction, and this one silently changed what was being summed.** ⚠️ **No row: the fix is the `awk` form, and it is written into this round's base block where the next PO reads it** |

---

## ⛔ ROUND 29 — the two rows re-placed, `W40` freed, and check 3 came back **0 of 4** exactly as predicted

⭐ **Measured at `ddddd05`, branch `chore/po-round29`, linked worktree `wt/po29`,
pinned image (Ruling 40)** — ⛔ **the ref AND the checkout** (Ruling 108).
⚠️ **Every reading below was RE-DERIVED here; where one arrived from the CTO or
the coordinator it is labelled `[RECEIVED]` (Ruling 115).**

⛔ **THE TIP DID NOT MOVE UNDER THIS ROUND.** ⭐ **`ddddd05` at open and at
close, `git rev-parse HEAD` in this worktree both times** — ⚠️ **which is worth
saying only because the last two rounds had to discard readings, and Ruling 97's
cost is paid only when the tip moves.**

| | ⛔ **`ddddd05`, `wt/po29`, pinned image** |
|---|---|
| suite | ⭐ **3522 passed, 63 skipped**, exit **0** |
| floor | ⭐ **`quality floor: clean`**, exit **0** — ⛔ **`$?` taken with NO pipeline** |
| pointers | **94 read in 144 markdown files, 50 carrying an anchor, 0 unresolved** |
| lint | ruff 0.16.6 `check` clean, `format --check` clean, **500** files (`wt/po29`) · ⭐ **501 in MAIN** |
| index | **`none — none in this checkout`** (`wt/po29`) · ⛔ **`stale — built at 8821b118`** (MAIN, measured by me) |

### ⛔ ROUND 29 — the six wave-open checks, each with its NAMED instrument and its READING

⭐ **Run at `ddddd05`, `wt/po29`, pinned image, except where a row names another
checkout.** ⛔ **`PO-27/1` stands: an unnamed instrument fails silently, because
every run returns a number and no run returns a disagreement.** ⚠️ **Ruling 128
is applied to every row below — where a reading is a COUNT, the POPULATION is
printed beside it, and the EXPECTED reading is written down before the command
runs.**

| # | Check | ⛔ **Instrument** | ⭐ **Expected** | ⭐ **Reading @ `ddddd05`** |
|---|---|---|---|---|
| **1** | index present and current | `docker/dev/check python3 -m tools.quality`, read the `knowledge index:` line, **per checkout** | MAIN `fresh`; `wt/po29` `none` | ⛔ **SPLIT, and MAIN DISAGREED WITH ITS OWN LAST READING.** ⭐ **`wt/po29`: `none — none in this checkout`, and the floor says *This is not a failure*** — `graphify-out/` is untracked so `git worktree add` does not carry it (Ruling 108). ⛔ **MAIN: `stale — built at 8821b118`, NOT `fresh`** — the index was built at `8821b11` and three merges have landed since. ⚠️ **`PO-29/1`** |
| **2** | `[structural]` triage | `git grep -EIc '\`\[(local\|structural\|none)\]\`' ddddd05 -- docs`, then `wc -l` for files and `awk -F: '{s+=$NF}'` for lines | ≥ 540 / ≥ 91 — it only grows | ⭐ **583 lines / 95 files**, up from **540 / 91** at `a00337b`. ⛔ **Reproducible at the first attempt for the THIRD round running, and the only thing that ever changed is that `PO-26/2` wrote the instrument down** |
| **3** | C6 — every ruling reached its artifact | `git grep -In "Ruling <n>\b" ddddd05 -- docs \| cut -d: -f2 \| sort \| uniq -c`, ⛔ **printing the FILES and not a count** (Ruling 128), excluding the handoff that minted it | ⛔ **0 of 4** — `[RECEIVED: CTO-36`, for-the-PO item 3`]`, and it is the CTO's PREDICTION not their measurement | ⛔ **0 OF 4, EXACTLY AS PREDICTED.** ⭐ **Population: rulings 125, 126, 127, 128 — every one minted since round 28's check.** ⛔ **125 → 4 hits `CTO-…round35.md` + 6 `…round36.md` · 126 → 2 + 4 · 127 → 3 `…round36.md` · 128 → 2 `…round36.md`. EVERY HIT IS INSIDE `docs/tasks/handoffs/`.** ⚠️ **ALL FOUR LAND THIS ROUND — [rowed below](#round-29-rulings-125128-all-four-into-rows-and-the-cto-asked-for-three) — and note that 126 is the one the CTO's own list omitted; `PO-29/3`** |
| **4** | re-measure every row whose trigger has passed | `git log a00337b..ddddd05` enumerates what moved; only those rows are re-taken | 3 merges since the close ref | ⛔ **SIX stale rows — [the table below](#check-4-round-29-six-rows-and-the-one-that-was-a-conditional-nobody-had-evaluated)** |
| **5** | `CLAUDE.md`'s *Where to start* | `grep -n 'Where to start' -A12 CLAUDE.md`, read against this board's head | *In flight: M2 step 2.2* | ✅ **PASSES, for the first time in three rounds.** ⭐ **It reads *"M2 step 2.1 closed 2026-09-10 at `a00337b`… ⏳ Open: M2 — a corpus is readable. In flight: M2 step 2.2"*, and that is true at `ddddd05`: `SF-13` and `SK-07` both carry a checkout.** ⛔ **AND the round-28 correction REPLACED the stale sentence rather than appending beneath it** — `CTO-36/8`, confirmed by me reading the file, not the diff |
| **6** | catalogue contributions | `git -C ../<repo> rev-parse --short HEAD` per sibling; `grep -c '^### ' docs/integration-catalogue.md`; `[ -d <repo>/docs/studyforge ]` | four unchanged refs, 19 entries | ✅ **NOTHING NEW OWED, and NOTHING MOVED.** ⭐ **`../ISO-8583-jPOS-tutorial` @ `6c8dc85`** — the same ref the third through EIGHTH runs have measured. ⛔ **Catalogue stands at **19** entries.** ⭐ **`../Claude-senior-java-engineer` @ `c9cf522`, `../Claude-SPARQL-tutorial` @ `b9aa89b`, `../CodeSignal` @ `49c11d5e` have NO `docs/studyforge/`, so none contributes and none can** |

⭐ **AND THE SEVENTH, standing from Ruling 113 — every id in a `Size exception:`
reason is a LIVE board row. ⛔ EXPECTED READING, WRITTEN DOWN BEFORE THE RUN
(Ruling 128, and Ruling 123's row 1 as it amends it): ZERO ROWS,** because `W44`
deleted the tree's last marker at `7b5c0a9` and nothing since has touched `src/`.

```text
§3c's ast sweep, pinned image, wt/po29 @ ddddd05          ->  ROWS=0     [as expected]
git grep -l 'Size exception:' -- src/                     ->  (nothing)  [corroborator]
git grep -l 'Size exception:' -- src/ | wc -l             ->  0
```

⛔ **AND THE POPULATION THAT `| wc -l` CONCEALS, printed here once so nobody
re-walks into `PO-28/7`:**

```text
git grep -l 'Size exception:' -- src/ tools/ tests/       ->  4 files
    tools/quality/config.py        tools/quality/size.py
    tools/tests/quality/test_config.py   tools/tests/quality/test_size.py
```

⭐ **Four members, every one the checker's own package or its tests, on a tree
holding ZERO deferrals.** ⛔ **That is Ruling 128 in one screen: the count is
`4`, the members are the finding, and the count is the thing that hides them.**

#### ⛔ CHECK 4 ROUND 29 — six rows, and the one that was a CONDITIONAL nobody had evaluated

⛔ **`git log a00337b..ddddd05` is three merges and four authored commits:**
`7b5c0a9` (`W44`), `8821b11` (CTO round 35), `ec74796` (PO round 28), `ddddd05`
(CTO round 36). ⭐ **Only rows those touch are re-taken.**

| # | Row | ⛔ **What it said** | ⭐ **True at `ddddd05`** |
|---|---|---|---|
| 1 | head — base paragraph | `3419 / 63 @ 426672c` (round 27's, still the head's) | ⛔ **`3522 / 63 @ ddddd05`.** ⚠️ **The head carried a TWO-ROUND-OLD base while the round-28 SECTION carried the current one — the duplicated-status shape again, and this time in the same file** |
| 2 | head — next two rows | *"`SF-13` then `SK-07`, placed not dispatched"* | ⛔ **BOTH ARE IN FLIGHT.** ⭐ **Re-placed: `SK-05`, `W40`** |
| 3 | head — lint / index | `492` (`wt/po28`) · `493` MAIN; index `fresh` | ⛔ **`500` · `501`; index MAIN reads `stale`.** ⭐ **`PO-28/1`'s formula holds at TWO MORE refs — `PO-29/1`** |
| 4 | ⛔ **`W40`'s row** | *"`W40` is FREE and is still not placed ahead of step 2.2's product path"* | ⛔ **The product path NO LONGER HAS a second free row.** ⭐ **`W40` is PLACED, second slot** |
| 5 | ⛔ **`W44`'s Ruling 121 acceptance** | ⛔ **the grep IS the instrument** | ⛔ **DEMOTED by Ruling 123 — the §3c sweep at **0 rows** is the GATE and the grep is a CORROBORATOR beside it. `CTO-36/4`** |
| 6 | ⛔ **`SK-07`'s ceiling warning** | *"if `SK-07` needs to WRITE to `content.py`, `W40` becomes its gate"* | ⛔ **A CONDITIONAL THAT NOBODY EVALUATED, and it is measurably FALSE today.** ⭐ **`PO-29/4`, and it is what frees `W40` to be placed at all** |

⭐ **Row 6 is the one worth the check's whole cost.** ⛔ **It is not a stale
STATUS and not a stale INSTRUMENT — it is a stale CONDITIONAL: a row that says
*if X then gate*, shipped without anybody ever running X.** ⚠️ **It sat on the
board for a round reading like a live gate, and it would have gone on reading
like one until somebody needed `W40`.**

### ⭐ ROUND 29 — THE NEXT TWO ROWS, `Owns` verified at `ddddd05`, and the R11 pre-dispatch sum

⛔ **PLACED, NOT DISPATCHED.** ⚠️ **`SF-13` is IN FLIGHT on `feat/SF-13-contents`
and `SK-07` on `feat/SK-07-onboarding`, both `wt/*` checkouts at `8821b11`** —
⭐ **so these two are what the developers take as those come free.**

| | ⭐ **Row** | ⛔ **Why it, and what it is NOT** |
|---|---|---|
| **NEXT 1** | ⭐ **`SK-05`** — the authoring reference | ⛔ **Step 2.2's ONLY remaining free product row.** ⚠️ **`SK-08` is the other one left and it is blocked INSIDE the step on `SK-07`, which is in flight — so there is no choice to make here, and that is the honest reason.** ⭐ **`solo`, ~35k, and `Owns docs/authoring/` which DOES NOT EXIST at `ddddd05` — a greenfield directory, zero intersection with anything** |
| **NEXT 2** | ⭐ **`W40`** — no module at zero headroom against R11 | ⛔ **The product path has NO second free row, so the second slot goes to the queue and this is the queue's head.** ⭐ **Its gate was struck this round (Ruling 127) and its collision with `SK-07` is measurably absent.** ⚠️ **It is ahead of `W41` (which must re-measure two surfaces after `W44`'s package split), ahead of `W37` and `W38` (which both ADD TESTS, into a file at 600/600), and ahead of `W42`/`W48` (which collide with each other)** |

⛔ **`Owns` VERIFIED AGAINST THE TREE AT `ddddd05`, not against another
document, and the commands are here because Ruling 119 says a derivation stated
in prose is not a carve-out:**

```bash
# SK-05's surface — expected: EMPTY, it is greenfield
git ls-tree -r --name-only ddddd05 -- docs/authoring        # -> (nothing), 0 files
# W40's two subjects — expected: exactly two, both at zero headroom
git ls-tree -r --name-only ddddd05 -- src/studyforge/corpus/manifest/content.py \
                                      tests/test_gate_coverage.py
# the in-flight pair's surfaces
git ls-tree -r --name-only ddddd05 -- src/studyforge/contents        # SF-13
git ls-tree -r --name-only ddddd05 -- src/studyforge/skills/onboarding   # SK-07 -> (nothing)
```

⛔ **THE R11 PRE-DISPATCH SUM — `PO-26/1`'s sub-step, measured at `ddddd05` with
derivation A in the pinned image and `wc -l`.**

| | `SK-05` | `W40` | ⛔ **shared** |
|---|---|---|---|
| `src/` surface | ⭐ **NONE — it owns `docs/authoring/` and no Python at all** | ⛔ `src/studyforge/corpus/manifest/content.py` (**400/400**, headroom **0**) | ⭐ **none** |
| test surface | ⭐ **none** | ⛔ `tests/test_gate_coverage.py` (**600/600**, headroom **0**) | ⭐ **none** |
| ⛔ **Intersection** | | | ⭐ **∅ — and the sum is not needed, which IS the reading** |

⛔ **DERIVATION A, RUN HERE AND PRINTED IN FULL (Ruling 128), rather than read
off a cell:**

```text
src/studyforge/corpus/manifest/content.py    400/400   headroom 0
tests/test_gate_coverage.py                  600/600   headroom 0
A_ROWS= 2
   -- nearest miss, for context --
tests/studyforge/corpus/container/test_document.py   598/600   headroom 2
```

⭐ **A − B where B is §3c's sweep at **0**, so A − B = A: `W40`'s subject is
exactly those two modules.** ⛔ **`validate/source.py` has left A entirely —
`W44` made it a package, and the collision that Ruling 119 was minted over is
now IMPOSSIBLE rather than merely avoided.**

##### ⛔ `W40` vs the two rows IN FLIGHT — derived, not asserted

⚠️ **This is the check that would have stopped `W44`'s pair breach a round
early, so it is run rather than waved:**

| ⛔ **the worry** | ⭐ **the command** | ⛔ **the reading @ `ddddd05`** |
|---|---|---|
| `SK-07` must WRITE `content.not_material` into `content.py`, whose ceiling is full | `git grep -n 'not_material' ddddd05 -- src/ \| cut -d: -f2 \| sort \| uniq -c` | ⭐ **The vocabulary is ALREADY MINTED — 21 in `content.py` (`SF-35`), 3 in `manifest/document.py`, 1 in `manifest/edits.py`, 3 in `manifest/__init__.py`, 4 in `validate/source/classification.py`, and ⛔ **4 in `skills/adapter/scaffold.py` + 3 in `skills/adapter/SKILL.md`, which is `SK-07`'s side ALREADY GENERATING THE GLOBS**.** ⚠️ **So `SK-07` READS the vocabulary and WRITES into a corpus's `corpus.json`. It does not extend `content.py`** |
| `SK-07` imports the module `W40` would split | `git grep -ln 'manifest.content\|from .content' ddddd05 -- src/ tests/` | ⭐ **SIX files, and ⛔ **NOT ONE of them is under `src/studyforge/skills/`**: `manifest/__init__.py`, `manifest/document.py`, `manifest/edits.py`, `validate/source/classification.py`, `tests/emission/documents.py`, `tests/studyforge/corpus/manifest/test_content.py`** |
| `SF-13` must extend `tests/test_gate_coverage.py`, at 600/600 | read `GATED_TREES` in that file | ⭐ **THREE roots — `src/studyforge`, `tools`, `tests` — and `contents/` falls UNDER `src/studyforge`.** ⛔ **The file scans the tree and asserts; a new module under an existing root needs NO edit to it.** ⚠️ **A new ROOT would, and `SF-13` does not add one** |

⛔ **SO THE PLACEMENT IS SAFE AND IT IS SAFE BY MEASUREMENT.** ⭐ **`W40` must
still preserve `corpus.manifest`'s public surface across the split — a PURE
MOVE, exactly as `W44` was proved to be — because `SK-07` and `SF-35`'s
consumers reach `not_material` through it.** ⚠️ **That is the row's condition,
written here, and it is the only coupling the three commands found.**

⛔ **AND THE ROWS I AM NOT PLACING, each with its reason:**

| Row | ⛔ **Why not now** |
|---|---|
| `SK-08` | ⛔ **BLOCKED INSIDE ITS OWN STEP on `SK-07`, which is in flight.** ⭐ **`PO-28/2`, unchanged, and the CTO ruled the SENTENCE is the defect — do NOT invent a step 2.3** |
| `W41` | ⭐ **FREE at last — `W44` merged.** ⛔ **Behind `W40`: it must RE-MEASURE both its surfaces, because `validate/source.py` is a PACKAGE now and its cited line numbers are gone, not moved** |
| `W42` / `W48` | ⛔ **Collide on `tools/quality/handoffs/` — ONE DISPATCH or an order.** Unchanged |
| `W34` | ⭐ **Unblocked (Ruling 118)** — ⛔ but behind `W47`, which establishes the index form it adopts. Unchanged |
| `W37` / `W38` | ⛔ **BOTH ADD TESTS, and `tests/test_gate_coverage.py` is at 600 of 600.** ⭐ **That is exactly why `W40` is in front of them, and it has been said for three rounds** |
| `W50`…`W53` | ⭐ **Queued.** ⛔ **`W52` has a TRIGGER rather than a slot, and Ruling 127 sharpens it this round** |

### ⛔ ROUND 29 — Rulings 125–128, ALL FOUR into rows, and the CTO asked for THREE

⭐ **Check 3 came back 0 of 4, which the CTO PREDICTED — and predicting a check's
result is not the same as discharging it.** ⛔ **Their for-the-PO item 3 names
**125, 127 and 128** and omits **126**, while their own `CTO-36/5` measured
125 AND 126 as reaching no artifact.** ⚠️ **Ruling 126 is live, load-bearing, and
was the rule the CTO used to catch themselves this round — a ruling that good is
exactly the kind that gets carried in a handoff forever. `PO-29/3`.**

| Ruling | ⛔ **What it says, in one line** | ⭐ **Where it landed this round** |
|---|---|---|
| **125** | ⛔ **`check_sizes` reads the FIRST docstring of every module regardless of length, so a `Size exception:` at or under the ceiling is a finding (`size-exception-stale`)** — ⚠️ **its *gated before `W40`* half is STRUCK by 127** | ⭐ **`W52`'s row: the surviving half is the row's SUBJECT; the struck half is recorded in this board's HEAD with the measurement that shows it never reached this board** |
| **126** | ⛔ **A ruling that quantifies over a population STATES THE COMMAND that derives it** | ⭐ **`W53`'s row — it is the same class as Ruling 122's and 128's, and `W53` is the row that owns the rubric's half of that class.** ⚠️ **Rowed HERE because the CTO's list omitted it** |
| **127** | ⭐ **`W52` stands with its trigger; the trigger fires on the sweep going non-empty FOR ANY REASON, over-ceiling included** | ⭐ **`W52`'s row and its mint block — [the clause, written out](#w52-gains-ruling-127-the-trigger-fires-on-any-non-empty-sweep-and-that-is-strictly-earlier-than-any-split-gate)** |
| **128** | ⛔ **An instrument that reduces a population to a SCALAR prints that population IN FULL before the clause ships; the expected reading is written down BEFORE the command runs** | ⭐ **`W53`'s row, AND applied to every check in this round's own table** |

#### ⛔ `W52` GAINS RULING 127 — the trigger fires on ANY non-empty sweep, and that is strictly EARLIER than any split gate

⚠️ **As minted, `W52`'s trigger read *"the row fires BEFORE the next deferral is
written"* beside an instrument that can only fire once one HAS been written.**
⛔ **Read literally those contradict.** ⭐ **They do not, and the CTO measured
why — `[RECEIVED: CTO round 36]`, three probes planted at once at `ed8442d`:**

```text
probe                                    §3c sweep                       grep -rl src/
over-ceiling deferral (425/400)          CAUGHT  "425/400, over"         caught
under-ceiling stale marker (6/400)       CAUGHT  "6/400, UNDER — STALE"  caught
marker in a COMMENT, not a docstring     correctly IGNORED               FALSE POSITIVE
live tree, probes removed                ROWS=0                          0
```

> ⭐ **THE CLAUSE, and it is what the row now carries: the trigger fires when
> §3c's `ast` sweep returns NON-EMPTY FOR ANY REASON — a perfectly legal
> over-ceiling deferral counts.** ⛔ **A legal deferral today is a stale marker
> after the split that retires it, so the over-ceiling reading is the PRECURSOR
> of every stale one.** ⚠️ **That fires ONE WHOLE TASK before any split could
> strand a marker, and it does not depend on guessing which task is the next
> split.**

⛔ **AND THAT IS WHY RULING 125'S GATE WAS BOTH WRONG AND UNNECESSARY.** ⭐ **The
residue hazard needs a marker to exist BEFORE the split; `W40`'s two subjects
carry none (sweep → `ROWS=0`, measured by me above), and a split never ADDS one
— splitting is what removes the reason for one.**

#### ⛔ `W44`'s ACCEPTANCE — Ruling 123's NARROWING, and the two instruments disagree on a real input

⛔ **`W44` is MERGED, so this is a record and not a gate** — ⭐ **and it is
corrected anyway, because `CTO-36/4` is right that the board still names the
grep as THE instrument where Ruling 123 demotes it.**

| | ⛔ **the GATE** | ⭐ **the CORROBORATOR, quoted beside it** |
|---|---|---|
| what | §3c's `ast` sweep — `W40`'s derivation B | `git grep -l 'Size exception:' -- src/ \| wc -l` |
| pass reading | ⭐ **`ROWS=0`** | ⭐ **`0`** |
| ⛔ **on a marker in a COMMENT** | ⭐ **correctly IGNORED** — it reads only the first DOCSTRING | ⛔ **FALSE POSITIVE** |
| ⛔ **on a TYPO in the pattern** | ⭐ **cannot happen: the marker is `config.SIZE_EXCEPTION_MARKER`** | ⛔ **returns `0`, which is the PASS reading** |

⛔ **THE TWO DISAGREE ON A REAL INPUT, and that is the whole reason one of them
is the gate.** ⚠️ **`| wc -l` returns `0` for a typo exactly as it does for a
clean tree, which is Ruling 123's row 3 failing on the instrument Ruling 123 was
used to bless — `CTO-36/2`, and it is why Ruling 128 exists.**

### ⛔ ROUND 29 — findings

| id | class | ⛔ **finding** |
|---|---|---|
| `PO-29/1` | `[local]` | ⛔ **MAIN's knowledge index is STALE at the release tip, and check 1 read `fresh` one round ago.** **Measured** by me, 2026-09-10, `docker/dev/check python3 -m tools.quality` in the MAIN checkout at `ddddd05` → `knowledge index: stale — built at 8821b118, and src/, tools/ or docs/ has changed since` — **[measured]**. ⚠️ **Three merges have landed since `8821b11` and none rebuilt it.** ⭐ **NOT a failure and not a licence (`W39`, Ruling 96): the floor prints it and exits **0**.** ⛔ **It IS a live R14 hazard — a stale index answers confidently with yesterday's tree — and `SF-13` and `SK-07` are both in flight against it right now.** ⭐ **REMEDY, and it is two commands somebody with the MAIN checkout runs: `graphify update .; python3 -m tools.knowledge bridge`.** ⛔ **I did NOT run it: `graphify-out/` is untracked, this is a linked worktree that does not carry it, and a PO rebuilding another checkout's index is a change nobody reviews** |
| `PO-29/2` | `[none]` | ⭐ **Ruling 125's *gated before `W40`* never reached this board, so striking it cost nothing and freed nothing that was actually held.** **Measured** by me at `ddddd05`: `git grep -n 'gated BEFORE\|gated before' -- docs/` → **4 lines, ALL in `docs/tasks/handoffs/`** (`CTO-…round35.md:259`, `CTO-…round36.md:158/217/358`) — **[measured]**. ⛔ **The CTO's item 2 asked me to strike it *wherever Ruling 125 put it*, and Ruling 125 put it nowhere a dispatcher reads.** ⭐ **That is Ruling 117 from the encouraging direction for once: guidance with no row did not carry, and this time the thing that failed to carry was a MISTAKE** |
| `PO-29/3` | `[local]` | ⛔ **The CTO's for-the-PO item 3 names rulings 125, 127 and 128 and OMITS 126, while their own `CTO-36/5` measured 125 AND 126 as reaching no artifact.** **Measured** by me at `ddddd05`: `git grep -In 'Ruling 126\b' ddddd05 -- docs \| cut -d: -f2 \| sort \| uniq -c` → **2 `CTO-…round35.md`, 4 `CTO-…round36.md`, and nothing else** — **[measured]**. ⚠️ **Ruling 126 is the rule the CTO used to catch their OWN error this round, one screen below where they broke it.** ⛔ **A ruling good enough to convict its author is exactly the kind that gets quoted in handoffs forever and never rowed.** ⭐ **Rowed on `W53` this round** |
| `PO-29/4` | `[structural]` | ⛔ **Round 28 shipped a CONDITIONAL gate and nobody ever evaluated its condition.** ⚠️ **The cell read *"if `SK-07` needs to WRITE there, `W40` becomes its gate"* — and the antecedent is measurably FALSE.** **Measured** by me at `ddddd05`, three commands, all **[measured]**: `git grep -n 'not_material' ddddd05 -- src/` → **the vocabulary is already minted, 21 hits in `content.py`, and `skills/adapter/scaffold.py` already GENERATES the globs (4 hits)**; `git grep -ln 'manifest.content\|from .content' ddddd05 -- src/ tests/` → **6 files, NOT ONE under `src/studyforge/skills/`**; `git ls-tree -r --name-only ddddd05 -- src/studyforge/skills/onboarding` → **empty, `SK-07` is greenfield**. ⛔ **So `SK-07` READS the vocabulary and writes globs into a corpus's `corpus.json`; it never adds a line to `content.py`.** ⭐ **This is a NEW class beside the stale STATUS and the stale INSTRUMENT: a stale CONDITIONAL, which reads like a live gate for as long as nobody needs the row it gates.** ⚠️ **`W40` was gated by it for a round and the gate was never real** |
| `PO-29/5` | `[local]` | ⭐ **`CTO-36/1` is CONFIRMED and it is mine.** **Measured** by me at `ddddd05`: `git ls-tree -r --name-only <ref> \| grep -c '\.md$'` → `7b5c0a9` = **141**, `ce3afcd` = **142**; so `7b5c0a9`'s row is `364 + (141−8) =` **497**, not the **498** `PO-28/1` recorded against that ref — **[measured]**, both refs. ⛔ **The formula is untouched; the REF was wrong, and it was my own branch one commit later.** ⚠️ **Ruling 108 exactly, committed inside the finding that establishes the formula.** ⭐ **AND THE FORMULA NOW HOLDS AT SIX REFS, two of them measured by nobody before this round: `a00337b` 492, `7b5c0a9` 497, `8821b11` 498, `ed8442d` 499, ⭐ **`ddddd05` 500 (`wt/po29`) and 501 (MAIN, = 500 + the untracked `ONBOARDING.md`)** — and it tracks BOTH file kinds independently at every one** |
| `PO-29/6` | `[structural]` | ⛔ **The head carried a TWO-ROUND-OLD base (`3419 / 63 @ 426672c`) while the round-28 section carried the current one.** **Measured** by me at `ddddd05`: `grep -n '📏 \*\*BASE' docs/tasks/BOARD.md` → **two paragraphs, round 27's at the head and round 26's below** — **[measured]**, before this round's edit. ⛔ **That is the duplicated-status mechanism the round-25 headline describes, occurring INSIDE the one file that is supposed to be the instrument.** ⭐ **A reader looking for the base stops at the head, which is the copy nobody re-measures.** ⚠️ **Fixed by REPLACING the head's paragraph and striking it, not by appending beneath — Ruling 106 governs merged HANDOFFS, and this board is live text** |
| `PO-29/7` | `[none]` | ⭐ **Five consecutive rounds of one class, across all three roles — and the coordinator asked whether it should be a standing row rather than a new ruling each round. MY ANSWER: a standing row, and it is `W53`.** ⛔ **The class is not *instruments* in general; it is precisely *a clause shipped against an instrument nobody ran in its population-printing form*, and rulings 122, 123, 126 and 128 are four narrowings of that ONE claim.** ⚠️ **Four rulings for one class is the symptom `W53` exists to end.** ⭐ **So `W53` absorbs 126 and 128 rather than the board minting `W54`, and the high-water mark does NOT move this round — [the reasoning is on `W53`'s row](#round-29-rulings-125128-all-four-into-rows-and-the-cto-asked-for-three)** |

---

## ⛔ ROUND 28 — step 2.1 CLOSED, step 2.2 OPENED, six rulings rowed, and a number that was never what it said

⭐ **Measured at `a00337b`, branch `chore/po-round28`, linked worktree `wt/po28`,
pinned image (Ruling 40)** — ⛔ **the ref AND the checkout** (Ruling 108, narrowed
by `CTO-31/4`). ⚠️ **Every reading below was RE-DERIVED here; where one arrived
from the coordinator or the CTO it is labelled `[RECEIVED]` (Ruling 115).**

⛔ **THE TIP MOVED THREE TIMES UNDER THIS ROUND.** ⭐ **The brief pinned
`253cdd3`; I took all six checks and all five close rows there; `1aa6319`
(`W45` APPROVE) and `a00337b` (Rulings 121–122) then merged, and ⛔ **I THREW THE
READINGS AWAY AND TOOK THEM AGAIN AT `a00337b`.** ⚠️ **Then `7b5c0a9` (`W44`
APPROVE) merged while this section was being written.**

⛔ **THE CLOSE REF STAYS `a00337b` AND THAT IS RULING 97 READ AS WRITTEN:**
⭐ ***the ref need not be the tip, and a close does not go stale when the tip
moves past it — the record names its own ref, and a reader can diff that ref
against the tip to see what has moved since.*** ⚠️ **`git log a00337b..7b5c0a9`
is that diff and it is one merge: `W44`.** ⛔ **What DOES have to be re-taken is
every ROW `7b5c0a9` moved, and four were — `W44`, `W41`, `W40` and `W52`,
[below](#the-fourth-ref-move-the-rows-7b5c0a9-moved-and-the-instrument-it-caught-me-writing-unrun).**

⭐ **Ruling 97 cost something for the first time here — about four minutes — and
it is the whole of what the rule buys: the discarded set would have returned the
SAME VERDICT and would never have noticed it was closing on the wrong ref.**

| | ⛔ **`a00337b`, `wt/po28`, pinned image** |
|---|---|
| suite | ⭐ **3515 passed, 63 skipped**, exit **0** |
| floor | ⭐ **`quality floor: clean`**, exit **0** — ⛔ **`$?` taken with NO pipeline** |
| pointers | **81 read in 140 markdown files, 37 carrying an anchor, 0 unresolved** |
| lint | ruff 0.16.6 `check` clean, `format --check` clean, **492** files (`wt/po28`) · ⭐ **493 in MAIN** — ⛔ **and that number is not what six rounds have taken it to mean; `PO-28/1`** |
| index | **`none — none in this checkout`** (`wt/po28`) · ⭐ **`fresh — built at a00337bd`** (MAIN, measured by me) |

⛔ **ALL 63 SKIPS NAMED (`-rs`), and the three groups are unchanged:** **55**
`tests/visual/` (no browser in the pinned image — `QA-03/1`, `W36` removes them),
**5** `tests/docker/test_dev_image.py` (already inside the image), **3**
`tests/test_knowledge_index.py` (sibling checkouts absent — a property of this
LINKED WORKTREE, not of the repository).

### ✅ M2 STEP 2.1'S CLOSE RUN AT `a00337b` — all five RE-TAKEN, and the ref moved twice underneath it

⛔ **THE CLOSE REF IS `a00337b`.** ⭐ **Membership is `README.md`'s — *2.1 — SF-04,
SF-31, SF-35, SF-36, SK-02* — and this table is STATE, taken here, inheriting
nothing.** ⚠️ **The instrument is one command per row and it is written down:**
`git merge-base --is-ancestor <merge> a00337b`, **exit 0 = YES**.

| # | Row | merge | ⛔ **`--is-ancestor <merge> a00337b`** |
|---|---|---|---|
| 1 | `SF-31` — `studyforge plan`, the placement dry-run | `f3ee177` | ✅ **YES** |
| 2 | `SF-04` — corpus discovery and the site cache | `0899f0f` | ✅ **YES** |
| 3 | `SF-36` — `origin` may name a region, `container_api: 2` | `e4a2677` | ✅ **YES** |
| 4 | `SF-35` — `content.not_material`, `corpus_api: 2` | `a53aee8` | ✅ **YES** |
| 5 | `SK-02` — the adapter-authoring skill | `a48b09a` | ✅ **YES** |

⭐ **AND THE STEP'S OWN CONDITION, which is not any row's:** ⛔ **the tree is green
at the close ref, in the pinned image, in one checkout I name** — **3515 passed,
63 skipped, exit 0; `quality floor: clean`, exit 0; ruff `check` and
`format --check` both clean.**

⛔ **`SK-02/4` IS OPEN AND DOES NOT BLOCK THIS CLOSE.** ⭐ **It is `E11`'s clause
about `E07`'s repository — *the adapter package was produced by this skill, the
scaffolding commit precedes the source-reading commits* — and `git log` in a
repository this side does not own is the only instrument.** ⚠️ **R20 keeps it out
of this close: a framework close may not be gated on a measurement only the
integration agent can take.** ⛔ **It is PO-Integration's, it is recorded as
theirs, and it is not silently dropped.**

⚠️ **WHY THE CLOSE IS NOT AT `253cdd3`, which is what my brief pinned and what
the CTO named:** ⭐ **because the tip moved and Ruling 97 has no escape clause.**
⛔ **A brief's SHA states when the brief was written, not a property that holds
(`W43/2` → `W46`)** — and this round is the second consecutive one in which that
sentence was load-bearing rather than decorative.

### ⏳ M2 STEP 2.2 — OPEN, and its declared parallelism is FALSE by its own dependency graph

⛔ **MEMBERSHIP, from `README.md` and not restated from memory:**
**2.2 — `SK-07`, `SK-05`, `SK-08`, `SF-13`.** ⭐ **`README.md` says *within a
milestone, each step runs in parallel*.** ⚠️ **It does not, and the refutation is
in the epic documents this board points at rather than copies:**

| Row | Team | ⛔ **Depends on** | ⚠️ **State @ `a00337b`** | ⭐ **STATE @ `e309172` (round 31, re-taken)** |
|---|---|---|---|---|
| `SF-13` — table of contents | `pair` | `SF-04` ✅, `SF-05` ✅ | `todo`, FREE | ✅ **`done` — APPROVED (CTO round 37), merged `abe7d1c`.** ⭐ **+152 tests; six findings, `SF-13/1` and `SF-13/2` both routed to rows this round** |
| `SK-07` — corpus onboarding | `team` | `SK-02` ✅, `SF-03` ✅, `SF-02` ✅, `SF-31` ✅ | `todo`, FREE | ✅ **`done` — APPROVED (CTO round 37), merged `2e42c5b`.** ⭐ **+85 tests; `SK-02/1` closed end to end.** ⛔ **Its Acceptance was SPLIT under Ruling 129, not waived — [the two clauses and where they went](#round-30-what-i-struck-and-what-i-rowed)** |
| `SK-05` — authoring reference | `solo` | `SK-02` ✅ | `todo`, FREE | ✅ **`done` — APPROVED (CTO round 38), merged `83f767e`** at branch tip `77405dd`. ⭐ **+33 tests and the instrument `W61` widens.** ⚠️ **Its handoff's `400` for `test_authoring_reference.py` is **414**, and was 414 at the ref its own header names — annotated beneath, `PO-31/6`** |
| ⭐ **`SK-08`** — delivery planning | `pair` | `SK-01` ✅, ⭐ **`SK-07` ✅**, `SF-31` ✅ | `todo`, BLOCKED | ⏳ **`in-progress` — `feat/SK-08-delivery`, `wt/dev2n`, **1 commit**, head `ebf6a65`.** ⛔ **THE STEP'S LAST ROW: when it lands, step 2.2 closes and Ruling 97's re-take at one ref is owed.** ⚠️ **Its `skills/delivery/SKILL.md` joins `W61`'s widened population the moment it merges — [named at wave-open, not at its review](#round-31-the-next-two-rows-owns-in-ruling-136s-form-verified-at-e309172-and-a-pre-dispatch-sum-that-reads-zero)** |

⛔ **THE STEP IS DOWN TO ZERO FREE PRODUCT ROWS — three done, one in flight —
and that is why BOTH of round 31's slots go to the queue.** ⚠️ **Instrument:
`git worktree list` PLUS `git log --oneline release/m0-foundations..<branch>`
PLUS this board, run by me in `wt/po31` at `e309172` — MEASURED, not received.**
⛔ **Ruling 130, amended by `CTO-38/2`: neither `git worktree list` nor
`git branch --no-merged` is a superset of the other — both went blind in opposite
directions inside one round — so the union is a LOWER BOUND and this board is the
only total instrument.**

⚠️ **~~STATE @ `ddddd05` (round 29, re-taken)~~ was the column header until round
31, and three of its four cells had been re-taken at `8146bdb` under it.**
⛔ **A header naming a ref its own cells were not taken at is `PO-31/6`'s class
exactly — the same defect the CTO found in `SK-05`'s handoff in the same round,
in a different office's document.** ⭐ **`PO-31/2`.**

✅ **AND `README.md`'S SENTENCE IS FIXED THIS ROUND, which is what the CTO ruled
rather than either option `PO-28/2` weighed.** ⛔ **A STEP IS A BATCH BOUNDARY,
NOT A PARALLELISM GUARANTEE: it says *nothing outside this step may start* and
says nothing about edges inside it; in-step edges are read off the epic.**
⚠️ **`PO-28/2` was right to refuse renumbering — a step 2.3 existing only to
protect a sentence would be moved again by the next in-step edge.**

⛔ **`SK-08` depends on `SK-07` and both are in step 2.2, so the step has an
internal order and the plan does not say so.** ⭐ **I am not renumbering the step:
the dependency is real, it is one edge, and moving `SK-08` to a 2.3 that does not
exist would be renumbering the plan to make a sentence true.** ⚠️ **What I am
doing is writing the edge down HERE, where state lives, so a dispatcher reading
*"2.2 runs in parallel"* does not put two developers on `SK-08` and `SK-07` at
once.** ⛔ **`PO-28/2`.**

⚠️ **AND THE LOAD PROBLEM, named rather than discovered:** ⭐ **`SK-07` is `team`
and `SF-13` is `pair`, against TWO developers.** ⛔ **`team` means *dispatch a
small team; subtasks listed* (`README.md`'s vocabulary table), and `SK-07`'s
definition lists five generated artifacts.** ⚠️ **So step 2.2 cannot be run four
abreast and probably cannot be run two abreast either once `SK-07` starts** —
⭐ **which is a sequencing fact the milestone table's *14 tasks* hides, and it is
the same shape as M4's *serial bottleneck wearing a milestone's name*.**

### ⭐ ROUND 28 — THE NEXT TWO ROWS, `Owns` verified, and the R11 pre-dispatch sum

⛔ **PLACED, NOT DISPATCHED.** ⚠️ **`W44` is IN FLIGHT right now on
`refactor/W44-source-package` @ `0095bf7`, and `W45` merged at `1aa6319`** —
⭐ **so these two are what the developers take as they come free, and the board
says so rather than implying it.**

| | ⭐ **Row** | ⛔ **Why it, and what it is NOT** |
|---|---|---|
| **NEXT 1** | ⭐ **`SF-13`** — the site's contents AS DATA | ⛔ **M2's Done says *a working index*, and this row IS the index.** ⭐ **Every dependency merged; it is the only step-2.2 row with no in-step edge.** ⚠️ **It is also the FIRST thing in the project that computes a reading order, so it is what finally populates the between-units bar that M1's close condition 8 had to VOID as unfalsifiable** |
| **NEXT 2** | ⭐ **`SK-07`** — corpus onboarding | ⛔ **It GATES `SK-08`, which is in its own step, so it is step 2.2's critical path.** ⭐ **It also absorbs `SK-02/1`, which has no other home.** ⚠️ **`team`, ~55k — it is not a second `pair` slot and must not be planned as one** |

⛔ **THE R11 PRE-DISPATCH SUM — `PO-26/1`'s sub-step. Measured at `a00337b` with
`git ls-tree` and `wc -l`, against another tree and not against another
document.**

| | `SF-13` | `SK-07` | shared |
|---|---|---|---|
| `src/` surface | ⭐ `src/studyforge/contents/__init__.py` (**20**) — a stub with no parser | ⛔ **`src/studyforge/skills/onboarding/` — DOES NOT EXIST YET**; touches `src/studyforge/skills/__init__.py` (**32**) | ⭐ **none** |
| test mirror | `tests/studyforge/contents/test_init.py` (**10**) | `tests/studyforge/skills/onboarding/` — new | ⭐ **none** |
| ⛔ **Intersection** | | | ⭐ **∅ — and the sum is not needed, which IS the reading** |

⛔ **ONE CEILING WARNING THAT THE SUM DOES NOT CATCH, and it is `SK-07`'s alone:**
⭐ **`SK-02/1` gives `SK-07` the job of WRITING `content.not_material` globs into
`corpus.json`, and the vocabulary lives in
`src/studyforge/corpus/manifest/content.py`, which is at **400 of 400** —
ZERO HEADROOM.** ⚠️ **Reading it is free; adding one line to it is an R11 breach
on contact.** ⛔ **That module is `W40`'s subject, so if `SK-07` needs to WRITE
there, `W40` becomes its gate** — ⭐ **and the pick-up derivation, not this cell,
is what decides it (`CTO-32/8`).**

⛔ **AND THE ROWS I AM NOT PLACING, each with its reason:**

| Row | ⛔ **Why not now** |
|---|---|
| `W40` | ⛔ **RULING 119 BARS IT.** ⭐ Its carve-out is prose, `W44` is in flight, and the two may not be in flight together until the row carries both commands. ⚠️ **The row now carries them — [below](#w40-gains-ruling-119-both-commands-and-the-subtraction-written-out) — so the bar lifts the moment `W44` merges, and `W44` merging removes the collision anyway** |
| `W41` | ⛔ **STILL HELD behind `W44`**, which restructures `validate/source.py`. Unchanged |
| `W42` / `W48` | ⛔ **Collide on `tools/quality/handoffs/` — ONE DISPATCH or an order.** Unchanged, and neither is ahead of step 2.2's product path |
| `W34` | ⭐ **UNBLOCKED at last (Ruling 118) and it gets a queue slot** — ⛔ but behind `W47`, which establishes the index form it adopts. ⚠️ **Six rounds recorded as blocked by a sentence; [the re-measurement is below](#w34-gains-ruling-118-the-start-condition-is-replaced-and-i-watched-it-return-a-disagreement)** |
| `W50`…`W53` | ⭐ **Minted this round, queued, none of them ahead of `SF-13`.** ⛔ **`W52` has a TRIGGER rather than a slot, and the trigger is measurable** |

### ⛔ ROUND 28 — the six wave-open checks, each with its NAMED instrument

⭐ **Run at `a00337b`, `wt/po28`, pinned image, except where a row names another
checkout.** ⛔ **`PO-27/1`: an unnamed instrument fails silently, because every run
returns a number and no run returns a disagreement** — ⚠️ **so every row below
carries the command, and check 6 and the seventh check each returned a
DISAGREEMENT this round, which is the first evidence any of them can produce.**

| # | Check | ⛔ **Instrument** | ⭐ **Reading @ `a00337b`** |
|---|---|---|---|
| **1** | index present and current | `docker/dev/check python3 -m tools.quality`, read the `knowledge index:` line, per checkout | ⚠️ **SPLIT, both halves correct and BOTH measured by me.** ⭐ **MAIN: `fresh — built at a00337bd, and nothing it describes has moved since`.** ⛔ **`wt/po28`: `none — none in this checkout`, and the floor says *This is not a failure*** — `graphify-out/` is untracked so `git worktree add` does not carry it (Ruling 108) |
| **2** | `[structural]` triage | `git grep -EIc '\`\[(local\|structural\|none)\]\`' a00337b -- docs`, then `wc -l` for files and `awk` the sum for lines | ⭐ **540 lines / 91 files**, up from **504 / 87** at `426672c` and **531 / 90** at `253cdd3`. ⛔ **Reproducible at the first attempt for the second round running, and the only thing that ever changed is that `PO-26/2` wrote the instrument down** |
| **3** | C6 — every ruling reached its artifact | `git grep -In "Ruling <n>" a00337b -- docs`, excluding the handoff that minted it | ⛔ **1 OF 6 AT OPEN.** ⭐ **Population: rulings 117–122, every one minted since round 27's check.** ⛔ **117 → 0 · 118 → 0 · 119 → 0 · 120 → 0 · 122 → 0. ⭐ 121 → 1 (`review-rubric.md`, in the ruler's own commit).** ⚠️ **ALL SIX LAND THIS ROUND — [rowed below](#round-28-rulings-117122-every-one-into-a-row-and-none-left-in-a-handoff)** |
| **4** | re-measure every row whose trigger has passed | `git log 426672c..a00337b` enumerates what moved; only those rows are re-taken | ⛔ **NINE stale rows — [the table below](#check-4-round-28-nine-rows-and-two-of-them-were-instruments)** |
| **5** | `CLAUDE.md`'s *Where to start* | `grep -n 'Where to start' -A6 CLAUDE.md`, read against this board's head | ⛔ **FAILED AT OPEN, and it failed BECAUSE OF THIS ROUND.** ⚠️ **It said *In flight: M2 step 2.1*, which was true at `426672c` and false the moment step 2.1 closed.** ⭐ **CORRECTED IN THIS COMMIT** — and note what the check actually caught: not somebody else's staleness, but MINE, in the same commit that created it |
| **6** | catalogue contributions | `git -C ../<repo> rev-parse --short HEAD` per sibling; `grep -c '^### ' docs/integration-catalogue.md`; `[ -d <repo>/docs/studyforge ]` | ✅ **NOTHING NEW OWED, and the reading DISAGREED with the last one.** ⭐ **`../ISO-8583-jPOS-tutorial` @ `6c8dc85`** — the same ref the third through seventh runs measured. ⛔ **Catalogue stands at **19** entries** — ⚠️ **but it last MOVED at `f875158`, not `4351f28` as round 27 recorded; `PO-28/3`.** ⭐ **`../Claude-senior-java-engineer` @ `c9cf522`, `../Claude-SPARQL-tutorial` @ `b9aa89b`, `../CodeSignal` @ `49c11d5e` have NO `docs/studyforge/`, so none contributes and none can** |

⭐ **AND THE SEVENTH, standing from Ruling 113, run on the sweep AS CORRECTED by
Ruling 121's commit — every id in a `Size exception:` reason is a LIVE board row:**

```text
src/studyforge/validate/source.py (425/400, over): W44 splits this module into a
package, and it is deferred to that row rather than done here because this file
crossed the ceiling only when SF-35 and SF-36 merged — each is under it alone,
and neither task may restructure a file the other is concurrently editing.
```

⛔ **ONE deferral, `W44` was live, the check PASSED at `a00337b`.** ✅ **RE-TAKEN
AT `7b5c0a9` AFTER `W44` MERGED: the sweep returns **0**, the tree holds no
deferral at all, and Ruling 121's replacement instrument returns its PASS reading
for the first time (`git grep -l 'Size exception:' -- src/ \| wc -l` → **0**),
where the clause it replaced would have printed nothing and exited **1**.**
⭐ **And look at what changed at `a00337b`: last round this same check printed
`…and it is deferred to`, stopping mid-sentence, and the round-34 verdict quoted
that truncation as *Ruling 114 demonstrating itself*.** ⚠️ **It was not a demonstration, it was the refutation:
truncation was a property of EVERY multi-line justification, not of badly-wrapped
ones, and the reading was filed as a confirmation because it was the reading
already expected.** ⛔ **`PO-27/1` generalised one notch: an instrument that
returns the answer you expect returns no disagreement either.**

#### ⛔ CHECK 4 ROUND 28 — nine rows, and TWO of them were instruments

| # | Row | ⛔ **What it said** | ⭐ **True at `a00337b`** |
|---|---|---|---|
| 1 | head — step 2.1 | *"five tasks, FOUR ARE DONE and `SK-02` alone remains"* | ✅ **ALL FIVE DONE. CLOSED at `a00337b`** |
| 2 | head — next two rows | *"`W45` then `W44`"* | ⛔ **`W45` MERGED `1aa6319`; `W44` IN FLIGHT.** ⭐ **Re-placed: `SF-13`, `SK-07`** |
| 3 | base paragraph | `3419 / 63 @ 426672c` | ⛔ **`3515 / 63 @ a00337b`** |
| 4 | ⛔ **`W44`'s Ruling 116 acceptance** | ⛔ **`git grep -c 'Size exception:' -- src/` → `0`** | ⛔ **UNREACHABLE, AND IT INVERTS. Replaced by Ruling 121, and `W44` was in flight against it** |
| 5 | ⛔ **`W40`'s carve-out** | *"`validate/source.py` is EXCLUDED BY THE DERIVATION ITSELF, not by a sentence"* | ⛔ **FALSE as inscribed — Ruling 119. The derivation returns it FIRST of three; only a SECOND command removes it** |
| 6 | `W34`'s start condition | *"no build task in flight"*, UNMET for the sixth round | ⭐ **REPLACED by Ruling 118's ownership test, and the new condition is MET** |
| 7 | `W34`'s harm | *"2015 → 2068, six rounds of growth"* | ⛔ **The GROWTH is not the harm — refuted by the governor's own instrument. The harm is 2068 lines / 100 headings / no index** |
| 8 | `W49`'s disposition set | *"gains an instrument or is DROPPED"* | ⛔ **Reads as three dispositions; for a DELIVERED task there are TWO — Ruling 117** |
| 9 | catalogue last-moved ref | *"`catalogue-contributions.md` last moved at `4351f28`"* | ⚠️ **`docs/integration-catalogue.md` last moved at `f875158`; `PO-28/3`** |

⭐ **Rows 4 and 5 are the ones worth the check's whole cost: they are not stale
STATUSES, they are stale INSTRUMENTS** — ⛔ **and an instrument that is wrong does
not go quiet, it returns a confident wrong answer to whoever runs it next.**
⚠️ **Both were dispatched against. `W44` is in flight against row 4 this minute.**

### ⛔ ROUND 28 — Rulings 117–122, every one into a ROW, and none left in a handoff

⭐ **Check 3 came back 1 of 6.** ⛔ **Ruling 117 is the standard: guidance with no
row is a failing carrier, and the CTO ratified that after diagnosing it in
`CTO-33/5` and then committing it in `CTO-33/3` in the same handoff.** ⚠️ **So
each of the six lands in a row's own cell below, quoted, not pointed at.**

| Ruling | ⭐ **Where it landed** |
|---|---|
| **117** | ⛔ **`W49`'s row — the DROP/RESTATE bound** |
| **118** | ⛔ **`W34`'s row — the start condition REPLACED** |
| **119** | ⛔ **`W40`'s row — both commands and the subtraction** |
| **120** | ⭐ **`W50` — MINTED** |
| **121** | ⛔ **`W44`'s acceptance — the inverted instrument replaced** |
| **122** | ⭐ **`W53` — MINTED** |

#### ⛔ `W40` GAINS RULING 119 — both commands and the subtraction, written out

⛔ **The row claimed its carve-out was an instrument. It is an instruction, and
the CTO ran it.** ⭐ **`W40`'s subject is *NO MODULE SITS AT ZERO HEADROOM against
R11*, and the population is DERIVED AT PICK-UP by these two commands and the
subtraction between them — never read off a cell:**

```bash
# A — at or over the ceiling. Run in the pinned image, from the repository root.
python3 - <<'EOF'
import pathlib
from tools.quality import config
root = pathlib.Path(".")
for path in config.python_files(root):
    rel = config.relative(path, root)
    lines, ceiling = len(path.read_text(encoding="utf-8").splitlines()), config.ceiling_for(rel)
    if lines >= ceiling:
        print(f"{rel}\t{lines}/{ceiling}\theadroom {ceiling - lines}")
EOF

# B — Ruling 113's standing deferral sweep, as corrected by Ruling 121's commit.
python3 - <<'EOF'
import pathlib
from tools.quality import config
from tools.quality.size import size_exception, module_docstring
root = pathlib.Path(".")
for path in config.python_files(root):
    rel = config.relative(path, root)
    text = path.read_text(encoding="utf-8")
    reason = size_exception(module_docstring(text, path))
    if reason is not None:
        print(rel)
EOF

# THE POPULATION IS A − B. A module under a live deferral belongs to the row named in it.
```

⛔ **Why one command is not enough, measured by the CTO at `426672c` and
RE-MEASURED by me at `a00337b`** — ⭐ **`[measured]` for B and for the floor,
`[RECEIVED: CTO-34/1]` for A's three-row output:**

| what was run | ⛔ **what it returns** |
|---|---|
| **A alone** | ⛔ **`validate/source.py` FIRST of three** — the wrong population |
| **B alone** | ⭐ **exactly `validate/source.py`** — measured by me at `a00337b`, one line |
| ⛔ **the floor alone** | ⛔ **∅ at exit 0** — `check_sizes` fires only OVER the ceiling (`size.py`, `if lines <= ceiling: continue`), so it catches NEITHER zero-headroom module |
| ⭐ **A − B** | ⭐ **the two zero-headroom modules, which is the row's actual subject** |

⛔ **UNTIL THIS ROW CARRIED BOTH COMMANDS, `W40` AND `W44` COULD NOT BE IN FLIGHT
TOGETHER.** ⭐ **It carries them now.** ⚠️ **The exposure was one round wide
anyway: Ruling 116 makes deleting the deferral `W44`'s LAST step, after which
`source.py` is a package and leaves A entirely.** ⛔ **The lesson is not the
window, it is that *the carve-out is an instrument, not an instruction* was
ITSELF an instruction — the stale KIND that the re-framing was minted to remove,
reproduced one level up.**

#### ⛔ `W34` GAINS RULING 118 — the start condition is REPLACED, and I watched it return a DISAGREEMENT

⛔ **`PO-27/4`'s conclusion was right and its evidence was refuted by the
governor's own instrument.** ⭐ **`[RECEIVED: CTO-34/3]` — the fenced share ROSE
13.0% → 13.6% → 13.9% across the three rounds the governor has been in force, and
total lines is the quantity the governor explicitly permits a correctness clause
to raise.** ⛔ **So *the file grew* is not a harm and a row justified on it is
justified on nothing.** ⭐ **THE HARM IS: `review-rubric.md` is 2068 lines with
100 headings and NO index, and it is the instrument every row in this project is
judged with** — ⚠️ **`W47`'s argument a fortiori, at 2.5× the lines and 2.9× the
headings of the document already ruled unnavigable.**

⭐ **THE START CONDITION, REPLACED — *no build task in flight* was a PROXY for a
property nobody ever measured:**

| | |
|---|---|
| **the claim** | ⭐ **no in-flight branch and no dirty worktree owns `docs/conventions/review-rubric.md`** |
| ⛔ **the instrument** | `git diff --name-only release/m0-foundations...<each live branch>` and `git status --porcelain` in every worktree, `grep -c review-rubric` → **0** |
| ⛔ **the TRIGGER** | ⭐ **fires anyway at 100 headings OR 2000 lines, whichever first — BOTH already true** |

⛔ **AND THE READING THAT MAKES THIS A REAL INSTRUMENT RATHER THAN A BETTER
SENTENCE — I ran it twice in one round and IT DISAGREED WITH ITSELF:**

```text
@ 253cdd3, 07:39      MAIN checkout dirty on docs/conventions/review-rubric.md   -> 1   [measured]
@ a00337b             all four live branches -> 0 ; all five worktrees -> 0       -> 0   [measured]
```

⭐ **The `1` was the CTO's Ruling 121/122 edit, uncommitted, in the MAIN checkout,
carrying a ruling number above the then high-water mark. It merged as `a00337b`
and the condition went back to `0`.** ⛔ **Six rounds of *UNMET* never once
produced a reading; the replacement produced a disagreement within four hours.**
⚠️ **`PO-28/4` is what that transient is, and it is not about `W34`.**

⭐ **`W34` IS UNBLOCKED AND QUEUED BEHIND `W47` ONLY**, because `W47` establishes
the index form the rubric adopts. ⛔ **`CTO-28/1`'s governor fix and `CTO-31/3`'s
gameability note still ride here.**

#### ⛔ `W49` GAINS RULING 117'S BOUND — a DELIVERED task's clause-1 failure takes DROP or RESTATE, never a new live gate

⭐ **`W49` STANDS — the CTO ratified my override of them, and their words are the
argument: *guidance is not a carrier; a row is*.** ⛔ **But four of the seven
conditions sit in `FND-02` and `FND-04`, both DELIVERED with an APPROVE recorded
at `E00:217`, and giving a delivered task's acceptance condition a NEW instrument
creates a gate that has never been run against the work it judges.**

| disposition | when | ⛔ **what it may NOT do** |
|---|---|---|
| ⭐ **DROP** | the condition was never doing work | — |
| ⭐ **RESTATE as delivered** | it described something real | ⛔ **never add a condition that must now PASS** |
| ⛔ **~~instrument it~~** | ⛔ **UNAVAILABLE for a closed task** | ⭐ **it is Ruling 97's re-opening in a row's clothing** |

⛔ **The three conditions in OPEN epics — `E04:298`, `E06:143`, `E08:121` — take
all three dispositions and SHOULD be instrumented.** ⭐ **M0 STAYS CLOSED: a close
records what was true at a named ref under the standard of the day.**

### ⛔ FOUR ROWS MINTED — `W50`, `W51`, `W52`, `W53`

⛔ **High-water mark moves `W49` → `W53`; measured across every branch in the
repository at `a00337b` — `git grep -In '\bW5[0-5]\b' $(git rev-list --all) --
docs` returns NOTHING outside this round's own commit.** ⭐ **`W28` and up are
minted by the PO only, and this is the mint.**

#### ⛔ `W50` — MINTED. **Ruling 120: an installed `studyforge` ships the skills' code without their procedures**

| | ⛔ **`W50`** |
|---|---|
| **What** | ⭐ **TWO things, and one alone is not the row: (a) a `SKILL.md` glob in `pyproject.toml`'s `[tool.setuptools.package-data]`, and (b) a test that ENUMERATES `src/**/SKILL.md` and asserts each is matched by the package data** |
| **From** | ⛔ **Ruling 120, ratifying `SK-02/3`.** ⭐ **It is a defect against the RELEASE BRANCH and it is `SK-01`'s, not `SK-02`'s** |
| **Owner** | framework agent, **queued** |
| ⛔ **Owns** | ⭐ **`pyproject.toml`** and a new test in `tests/` — ⚠️ **`pyproject.toml` was outside `SK-02`'s `Owns` and they REPORTED it rather than patching it, which is the working agreement working** |
| ⛔ **It predates `SK-02` and that is measured** | ⭐ **`src/studyforge/skills/reconnaissance/SKILL.md` was ALREADY unshipped at `426672c`** — ⚠️ **`SK-01` introduced it, `SK-02` is the second instance and the one that made it visible.** ⛔ **`SK-02` neither caused it nor may be held for it** |
| ⛔ **Exposure is NIL TODAY, and that is the reason to ROW it rather than remember it** | ⭐ **NOTHING installs the package — the pinned image installs pytest and ruff, and `pythonpath = ["src", "."]` runs the suite from the checkout.** ⛔ **It becomes real at the FIRST install, and the consumer seam is exactly that shape: R20 says what a consumer needs is carried HERE, and a consumer who installs gets a skill's modules without the procedure that calls them — §9 inverted, for the only audience the skill was written for** |
| ⛔ **Why the glob alone is refused** | ⭐ **One glob fixes the two instances that exist and NOTHING then stops the third**, and a skill's procedure going missing is SILENT: the package imports fine and the document is simply absent. ⛔ **That is a fix that cannot fail, which is `W37`'s whole subject** |
| ⛔ **Acceptance — clause 1's two columns** | **claim:** every `SKILL.md` under `src/` is in the built distribution. ⭐ **instrument:** ⛔ **the enumerating test is watched to FAIL FIRST — remove the glob and it exits non-zero naming the missing file** — ⚠️ **a test that has only ever been green against a correct `pyproject.toml` has not been seen to work** |
| ⛔ **When** | ⭐ **AHEAD of the first task that INSTALLS rather than bind-mounts; behind `W44`.** ⚠️ **`SK-05` and `SK-07` both ship documents, so the population grows before the exposure does** |
| ⛔ **POPULATION WIDENED ROUND 30 — TWO → THREE, and the prediction in the row above came true in one wave** | ⭐ **`SK-07` shipped the third `SKILL.md`: `git ls-tree -r --name-only 8146bdb -- src/studyforge/skills | grep -c 'SKILL.md$'` → **3** (reconnaissance, adapter, onboarding), and `[tool.setuptools.package-data]` is still `["**/templates/*.html", "**/assets/*"]`, which matches NONE of them.** ⛔ **`SK-07/3`. The enumerating test's population is 3, not 2 — and the row already refuses the glob-alone remedy for exactly this reason: the third instance arrived while the row sat in the queue** |

#### ⛔ `W51` — MINTED. **`SF-31/3` has no carrier anywhere, and a SKILL has now joined `cli/plan` in re-deriving the archive root**

| | ⛔ **`W51`** |
|---|---|
| **What** | ⭐ **`ARCHIVE_DIR` and `ARCHIVE_ROOT_NAME` reach a package surface — one line on `studyforge.validate.__all__` — or the archive root becomes a real parameter (§6 permits a corpus to put its archive elsewhere, and `Layout` already takes it as a field)** |
| **From** | ⛔ **`SF-31/3`, and `SK-02/2` as its SECOND MEASURED INSTANCE** |
| **Owner** | framework agent, **queued** |
| ⛔ **Owns** | ⭐ **`src/studyforge/validate/__init__.py`** (whose `__all__` is nine names at `a00337b`, none of them these two) **and its mirror** — ⚠️ **measured at `a00337b`, `wt/po28`** |
| ⛔ **WHY IT IS A ROW AT ALL, and this is the whole justification** | ⭐ **`SF-31/3` reached NO artifact: `grep -n 'SF-31/3' docs/tasks/BOARD.md docs/tasks/E*.md` at `a00337b` → **0 hits**.** ⛔ **`SF-31` is merged and closed, so the finding has no owner, no row and no epic** — ⚠️ **it survives only inside `SF-31`'s own handoff, which is exactly the carrier Ruling 117 rules against.** ⭐ **`PO-28/5`** |
| ⛔ **It WIDENED, and the widening is why it stops being deferrable** | ⭐ **`SF-31/3` predicted the class by construction — *"four more commands are planned under `cli/`, and every one of them reads a corpus root"*.** ⚠️ **`SK-02` measured a SKILL doing it: `skills/adapter/layout.py` is the second package to re-derive both constants.** ⛔ **So the population is no longer *commands under `cli/`*; it is *anything that reads a corpus root*, which includes every future skill** |
| ⛔ **Acceptance — clause 1's two columns** | **claim:** no module outside `validate/` re-derives either constant. ⭐ **instrument:** ⛔ **a test that greps `src/` for the two literals outside `src/studyforge/validate/` → **0 hits**, watched to FAIL against the tree as it stands today** — ⚠️ **which it must, because `skills/adapter/layout.py` is a live positive** |
| ⛔ **When** | ⛔ **~~BEFORE `SK-07`, which is the THIRD package that will read a corpus root; after it, this is a migration instead of a fix~~ — STRUCK, round 30 (CTO round 37, on `SK-07/4`).** ⚠️ **`SK-07` did NOT join the population — `grep -rn 'ARCHIVE_DIR\|archive_dir' src/studyforge/skills/onboarding/` → **0** — so nothing became a migration and the row's urgency never rested on where it sat.** ⭐ **RE-PRICED BY ITS MEMBERS, [re-derived by me at `8146bdb`](#round-30-w51-re-priced-by-members-and-my-population-is-wider-than-the-ctos): the member that decides the slot is `skills/adapter/parts/adapter.py:226`, which EMITS the walk into every generated adapter and therefore propagates it into repositories R3 forbids editing afterwards.** ⛔ **Slot: ahead of the next task that GENERATES an adapter, which is `SK-09`; behind `W57` and `SK-08`** |

#### ⛔ `W52` — MINTED. **A `Size exception:` on a file UNDER its ceiling is read by nothing the build ships**

| | ⛔ **`W52`** |
|---|---|
| **What** | ⭐ **`check_sizes` reads the deferral marker regardless of a file's length, so a marker left behind by a split is a FINDING rather than invisible.** ⛔ **A new rule with a new coverage story, not a widened one** |
| **From** | ⛔ **`W45/3`.** ⚠️ **HALF of it is already discharged — Ruling 121's commit dropped the length guard from §3c's wave-open sweep, which now prints `UNDER — STALE`.** ⭐ **That half is a HAND FORM; this row is the SHIPPED half** |
| **Owner** | framework agent — ⛔ **the CTO names `W37` as its home and I am RECORDING IT HERE INSTEAD, [with the reason below](#w52-is-a-row-and-not-a-clause-on-w37-and-i-am-overriding-the-ctos-routing)** |
| ⛔ **Owns** | ⭐ **`tools/quality/size.py` and its mirror `tools/tests/quality/test_size.py`** — ⚠️ **`W45` just landed there and merged, so the surface is free** |
| ⛔ **The mechanism, measured** | ⭐ **`size.py`'s `if lines <= ceiling: continue` precedes `module_docstring(...)`, so the shipped floor never opens an under-ceiling file's docstring.** ⛔ **`[RECEIVED: the CTO's W45 verdict]` — a planted stale marker on an under-ceiling file prints `UNDER — STALE` from the corrected sweep while the shipped floor reports CLEAN, proved in one run** |
| ⛔ **THE TRIGGER, and it is measurable rather than a date** | ⭐ **Exposure is `0` and MEASURED `0` at `7b5c0a9`: `W44` merged mid-round and deleted the tree's last marker, so the gap is LATENT, not live.** ⛔ **It becomes real the moment a `Size exception:` is written into a module under its ceiling, or into one that later shrinks below it. THE ROW FIRES BEFORE THE NEXT DEFERRAL IS WRITTEN.** ⭐ **INSTRUMENT: Ruling 113's `ast` sweep — `W40`'s derivation B — returns non-empty.** ⛔ **NOT `git grep`: I wrote `git grep -l 'Size exception:' -- src/ tools/ tests/ \| wc -l` into this row, then RAN it and it returned **4**, every one the checker's own package or its tests. ⚠️ That is the trap §3c states in terms — *do NOT grep the tree for the marker* — and I walked into it in the same commit that minted `W53` to stop exactly this. `PO-28/7`** |
| ⛔ **Acceptance — clause 1's two columns** | **claim:** a marker on a module under its ceiling is reported by `python3 -m tools.quality`. ⭐ **instrument:** ⛔ **plant one on an under-ceiling module in a temporary root; the floor exits **1** with exactly one finding naming it; remove it and the floor exits **0**** — ⚠️ **and the new rule REPORTS ITS COVERAGE, per `agent-protocol.md`'s *a new check reports its coverage, not just its hits*** |
| ⛔ **The cheapest shape, from the developer who found it** | ⭐ **The existing walk already reads every file's text — dropping the ceiling guard for the MARKER QUESTION ALONE costs one pass and no new I/O** |

##### ⛔ `W52` is a ROW and not a clause on `W37`, and I am overriding the CTO's routing

⚠️ **The CTO's `W45` verdict names `W37` as this finding's home, and `W37` is the
sweep for *checks that cannot fail by construction*, which this plainly is.**
⛔ **I am refusing the routing and the reason is Ruling 117, applied to me:**

⭐ **`W37` is queued NINTH, is a repository-wide SWEEP, and already carries three
widenings (`Ruling 111`, `CTO-31/1`, `CTO-32/5`) plus a separable one-line fix.**
⛔ **A finding with a DEADLINE — *before the next deferral is written* — attached
to a sweep with no slot is a finding whose carrier is a queue position**, and this
board's own repeated measurement is that such a carrier fails. ⚠️ **It is also the
`W40` shape one door along: a POPULATION absorbed into a row that enumerates a
RULE.**

⭐ **What I am NOT doing is duplicating it: `W37`'s row gains ONE pointer to
`W52`, not a second copy of the finding**, and if `W37` is picked up first its
sweep will find `W52`'s member and find it already owned.

#### ⛔ `W53` — MINTED. **Ruling 122: a clause naming an instrument is not final until its author has RUN it, in both directions, and recorded both readings**

| | ⛔ **`W53`** |
|---|---|
| **What** | ⭐ **One clause, two documents: `docs/conventions/review-rubric.md` and `docs/conventions/agent-protocol.md` beside clause 1** — ⛔ **an acceptance condition or gate command is not final until its author has run it against a tree that PASSES and a tree that FAILS, and written both readings beside it** |
| **From** | ⛔ **Ruling 122.** ⭐ **The CTO bound it to their OWN office first, and their sentence is the argument: *an unrun instrument minted in a ruling carries more authority and gets less scrutiny than one in a branch*** |
| **Owner** | framework agent, **queued** |
| ⛔ **Owns** | ⭐ **`docs/conventions/review-rubric.md` (**2068**, and this is `W34`'s file) and `docs/conventions/agent-protocol.md` (**825**, and this is `W46`/`W47`'s file)** — ⚠️ **measured at `a00337b`** |
| ⛔ **IT COLLIDES WITH THREE ROWS** | ⛔ **`W46` and `W47` both write `agent-protocol.md`; `W34` writes `review-rubric.md`.** ⭐ **ORDER: `W46` → `W47` → `W53` → `W34`, or one developer takes the run.** ⚠️ **Named here at wave-open, which is what `PO-26/1` exists for** |
| ⛔ **Why it is not `W43`'s clause 1 again** | ⭐ **`W43`'s clause 1 says an acceptance condition NAMES the instrument that would fail it. This says the author RUNS it.** ⚠️ **Ruling 116 named an instrument and satisfied clause 1 completely — and the instrument was unreachable and INVERTED.** ⛔ **Naming is not running, and Ruling 121 is the measured cost of the gap** |
| ⛔ **Acceptance — clause 1's two columns** | **claim:** both files carry the clause and each names the two-reading obligation, not only the naming one. ⭐ **instrument:** ⛔ **`W48`'s denylist is NOT its enforcement arm and this row says so rather than pretending prose is gated** — the instrument is `docker/dev/check python3 -m tools.quality` → exit 0 plus both clauses quoted in the handoff by line number |
| ⛔ **The worked example it must cite** | ⭐ **Ruling 116 → `W45/2` → Ruling 121, end to end**, because it is the shortest complete instance the project has: a clause that named its instrument, passed every check, and could not return the reading it claimed |
| ⛔ **ABSORBED ROUND 30 — `PO-29/4`'s CONDITIONAL form (CTO round 37, item 5)** | ⭐ **`agent-protocol.md`'s *names the instrument* clause gains one sentence: ⛔ a clause of the form *if X then gate* names the COMMAND that evaluates `X` and WHO re-evaluates it, or it is not a gate.** ⚠️ **`PO-29/4` is the measured instance — round 28 shipped *"if `SK-07` needs to WRITE there, `W40` becomes its gate"*, nobody ever ran the antecedent, and it held `W40` for a whole wave while being FALSE.** ⛔ **ABSORBED rather than given `W54`, under the CTO's ratified bound: it is a condition on the same act — an author shipping a clause that names an instrument — and it lands in the two files this row already owns.** ⭐ **`CTO-37/11` was tested against the same bound and REFUSED absorption; it is `W58`** |

### ⛔ ROUND 28 — the two `SK-02` findings that needed homes, and both got one

| Finding | ⭐ **Home** |
|---|---|
| ⛔ **`SK-02/1`** — a corpus's adapter is not material and NOTHING puts that in the manifest | ⭐ **`SK-07`'s definition in `E11`** — onboarding owns the manifest a new corpus starts from, and today a person copies two lines out of a report, which is R19's *anything a second source would have to retype*. ⛔ **Landed in `E11`, not here: it is a DEFINITION and this file carries state** |
| ⛔ **`SK-02/2`** — a second measured instance of `SF-31/3` | ⭐ **`W51`, minted above** — ⚠️ **and the finding is that `SF-31/3` itself had no home at all** |
| ⛔ **`SK-02/3`** | ⭐ **`W50`, minted above** (Ruling 120) |
| ⛔ **`SK-02/4`** | ⭐ **PO-Integration's, in `E07`'s repository. Open, recorded, and it does NOT block step 2.1's close** |
| ⭐ **`SK-02/5`** | ⭐ **A NEGATIVE result, complete as filed. No row: it answers a question and closes it** |

#### ⛔ THE FOURTH REF MOVE — the rows `7b5c0a9` moved, and the instrument it caught me writing UNRUN

⛔ **`W44` merged at `7b5c0a9` while this section was being written.** ⭐ **The
close ref stays `a00337b` (Ruling 97), and the ROWS were re-taken:**

| Row | ⛔ **said, at `a00337b`** | ⭐ **true at `7b5c0a9`** |
|---|---|---|
| `W44` | **NEXT 2**, in flight on `refactor/W44-source-package` | ✅ **`done`, MERGED `7b5c0a9`** |
| `W41` | ⛔ **HELD — `W44` restructures `validate/source.py`** | ⭐ **FREE.** ⚠️ **And its cited line numbers are GONE, not moved: the file is a package now** |
| `W40` | ⛔ **BARRED by Ruling 119 while `W44` is in flight** | ⭐ **FREE, and the collision is now IMPOSSIBLE — `source.py` left derivation A.** ⛔ **A = two modules, B = **0**, so A − B = A** |
| `W52` | exposure `0` *after `W44`* | ⭐ **`0`, MEASURED.** ⛔ **And its TRIGGER INSTRUMENT WAS WRONG — `PO-28/7`** |

⛔ **The head, the seventh check and all four rows above were re-taken here.**
⭐ **Nothing else in this round's readings depends on `a00337b..7b5c0a9`, because
that range is one merge touching `src/studyforge/validate/source*` and its
mirror, and no other row's surface is in it** — ⚠️ **which is check 4's cheap
instrument used the way Ruling 97 describes it, rather than a second full sweep.**

### ⛔ FINDINGS — round 28

#### ⛔ `PO-28/1` `[structural]` — the lint denominator every round quotes is not a count of this project's source files

⛔ **Six rounds have quoted *"lint clean at N files"* as a source-file count and
argued about a one-file difference between checkouts.** ⭐ **`N` is Python files
PLUS Markdown files, less the `tests/fixtures` exclusion, and no document in this
repository says so.**

**Measured** 2026-09-10 at `a00337b`, pinned image — **all `[measured]`**:

```text
wt/po28   git ls-files | grep -c '\.py$'                -> 360
          git ls-files | grep -c '\.md$'                -> 140
          git ls-files 'tests/fixtures/*' | grep -c '\.md$' -> 8
          360 + (140 - 8)                               =  492
          floor's own notice: "492 file(s) already formatted"   ✅ EXACT
MAIN      141 markdown (the 140 tracked + untracked ONBOARDING.md)
          360 + (141 - 8)                               =  493
          floor's own notice: "493 file(s) already formatted"   ✅ EXACT
container find /workspace -name '*.py' | wc -l          -> 360
          find /workspace -name '*.pyi' | wc -l         ->   0
```

⭐ **The formula was derived in `wt/po28` and then PREDICTED MAIN's number before
it was read.** ⛔ **So the mechanism is confirmed, not fitted.**

⚠️ **~~FOURTH CONFIRMATION, on a structurally different tree — `7b5c0a9`, after
`W44` turned one module into a package (+4 `.py`) and two handoffs landed
(+2 `.md`):~~ `364 + (142 - 8) = 498`, and the floor prints
~~`498 file(s) already formatted`~~.** ⛔ **CORRECTED ROUND 29 — THE REF IS
WRONG AND IT IS MINE.** ⭐ **`CTO-36/1`, RE-MEASURED by me at `ddddd05`:
`git ls-tree -r --name-only <ref> | grep -c '\.md$'` → `7b5c0a9` = **141**,
`ce3afcd` = **142**.** ⛔ **So `7b5c0a9`'s row is `364 + (141 − 8) =` **497**,
which is what CTO round 35 measured there; the **498** came from `ce3afcd` — my
OWN branch, one commit later, and the extra file is my own handoff.**
⚠️ **Ruling 108 exactly — a reading that named a REF when it came from a
CHECKOUT that was not at it — committed INSIDE the finding that establishes the
formula. `PO-29/5`.** ⭐ **THE FORMULA IS UNTOUCHED AND IT NOW HOLDS AT SIX
REFS, measured by two offices: 492 · 497 · 498 · 499 · 500 (`wt/po29`) · 501
(MAIN).** ⛔ **It tracks BOTH kinds of file independently at every one, which no
coincidence does.**

⚠️ **`CTO-34/5` reached the right conclusion — the `+1` is `ONBOARDING.md` — by a
mechanism that cannot be right: an untracked file at the root inflates a
*formatted-file* count only because ruff 0.16.6 formats embedded code in
Markdown.** ⛔ **Their remedy, *name the checkout beside every denominator*, is
correct and insufficient**, because it makes the number reproducible without
making it MEAN anything. ⭐ **Two readers comparing 492 and 493 would both have
been right and neither would have known they were counting prose.**

⛔ **Why `[structural]`:** ⚠️ **this number sits in the `§0a-i` table of every
round's handoff, on both sides of the review seam, and it is the ONLY lint
quantity either office records.** ⭐ **It is `PO-27/1` again with a different
subject — every run returned a number, no run returned a disagreement, and the
one round that produced a disagreement (`CTO-34/5`) explained it away.**
⛔ **NO ROW: the fix is one clause on whichever row next touches the notice, and
the notice's own line is the right place for it. `W38` owns that surface.**

#### ⛔ `PO-28/2` `[structural]` — M2 step 2.2's declared parallelism is refuted by its own dependency graph

⛔ **`README.md`: *within a milestone, each step runs in parallel*. `SK-08`
*Depends on* `SK-07`, and both are in step 2.2.**

**Measured** 2026-09-10 at `a00337b`: `docs/tasks/E11-skills-authoring.md:317`
reads `**Depends on** SK-01, SK-07, SF-31` — **`[measured]`**, read in the epic
document rather than off this board (round 26's `Owns`-is-a-pointer rule).

⚠️ **It is one edge and the plan is not wrong to keep it inside one step** —
⛔ **but the ordering principle is stated as a GUARANTEE and a dispatcher may act
on it.** ⭐ **Recorded as state here, where a dispatcher reads. NO ROW, and no
renumbering: renumbering the plan to make a sentence true is the failure this
board files against other people.**

#### ⚠️ `PO-28/3` `[local]` — the catalogue's last-moved ref was wrong for at least four rounds

⛔ **Round 27's check 6 recorded *`catalogue-contributions.md` last moved at
`4351f28`, before any of them*.** ⭐ **The file is `docs/integration-catalogue.md`
and it last moved at `f875158`.**

**Measured** 2026-09-10 at `a00337b`, `wt/po28`:
`git log -1 --format='%h %ad' --date=short -- docs/integration-catalogue.md` →
`f875158 2026-09-10` — **`[measured]`**. ⚠️ **The entry count is UNAFFECTED and
still **19** by `grep -c '^### '`, so the check's VERDICT was right both times.**

⛔ **Why it is worth a line: the wrong ref was the half of the reading that made
*nothing has moved* falsifiable**, and it was carried across four runs because
each inherited the previous round's cell. ⭐ **The entry count was re-derived every
round and stayed right; the ref was not and drifted. Same table, same round, two
different disciplines.**

#### ⛔ `PO-28/4` `[structural]` — a ruling was drafted in the MAIN checkout, uncommitted, above the high-water mark

⛔ **At `253cdd3` the MAIN checkout — the reference checkout every cross-checkout
number in this project is measured against — carried an UNCOMMITTED 43-line edit
to `docs/conventions/review-rubric.md`, citing *Ruling 121* and *`W45`'s merge*,
both of which were then in the future.**

**Measured** 2026-09-10, MAIN checkout at `253cdd3`: `git status --porcelain` →
` M docs/conventions/review-rubric.md` plus `?? ONBOARDING.md`; `git diff` →
`34 insertions(+), 9 deletions(-)`; file mtime `2026-09-10T07:39` —
**all `[measured]` by me**. ⚠️ **It merged as `a00337b` about four hours later and
MAIN is clean of it now — `[measured]` at `a00337b`.**

⭐ **It resolved correctly and no harm reached the tree. Filed anyway, for two
reasons that are not about this edit:**

1. ⛔ **On no branch, it belonged to no ref.** ⚠️ **Ruling 108 makes every number
   name its checkout — and this is the case where naming the checkout is not
   enough, because MAIN was carrying a change no ref described.** ⭐ **Anyone
   measuring MAIN in that window would have measured a tree that did not exist
   in the repository.**
2. ⭐ **IT IS THE FIRST DISAGREEMENT RULING 118's NEW CONDITION EVER PRODUCED.**
   ⛔ **The condition it replaced returned *UNMET* six times without a command
   being run. The replacement returned `1` at `253cdd3` and `0` at `a00337b`,
   four hours apart, on the same question.** ⚠️ **That is the difference between
   a proxy and an instrument, measured rather than argued.**

⛔ **NO ROW.** ⭐ **Ruling 122 already covers the authoring half, and the process
half — *work in the reference checkout goes on a branch* — belongs to whoever next
touches `delivery-flow.md`, which is `W46`.**

#### ⛔ `PO-28/5` `[structural]` — `SF-31/3` had no carrier of any kind, and the second instance is what found that out

⛔ **`SF-31/3` predicted its own recurrence in `SF-31`'s handoff and was never
rowed, never routed and never written into an epic.**

**Measured** 2026-09-10 at `a00337b`, `wt/po28`:
`grep -n 'SF-31/3' docs/tasks/BOARD.md docs/tasks/E*.md` → **0 hits** —
**`[measured]`**.

⚠️ **`SF-31` merged, so the finding's only home became a handoff for a closed
task.** ⛔ **It surfaced again only because `SK-02` independently hit it and filed
`SK-02/2`** — ⭐ **which means the detection mechanism was *a second developer
stubbing their toe on the same rock*, at one task's full cost.** ⛔ **Rowed as
`W51`.**

⚠️ **The generalisation, and it is bigger than this finding:** ⭐ **a `[structural]`
finding on a task that then MERGES has no owner by default** — the task closes,
the handoff freezes, and check 2 counts the marker forever without asking whether
anything happened. ⛔ **Check 2 counts markers; it does not count DISPOSITIONS.**
⭐ **That is `W42`'s neighbourhood and I am not minting a sixth row for it this
round; it is named here so the next round can weigh it.**

#### ⛔ `PO-28/7` `[structural]` — I minted `W53` to stop unrun instruments and shipped one in `W52` in the same commit

⛔ **`W52`'s trigger instrument, as I first wrote it, was
`git grep -l 'Size exception:' -- src/ tools/ tests/ \| wc -l` returns non-zero.**
⭐ **I then ran it.**

**Measured** 2026-09-10 at `7b5c0a9`, `wt/po28` — **all `[measured]`**:

```text
git grep -l 'Size exception:' -- src/ tools/ tests/   -> 4
  tools/quality/config.py         tools/quality/size.py
  tools/tests/quality/test_config.py   tools/tests/quality/test_size.py
Ruling 113's ast sweep (W40's derivation B)           -> 0
```

⛔ **The instrument returns `4` on a tree that holds ZERO deferrals, and every
hit is the checker's own package or its tests.** ⚠️ **§3c says this in terms —
*Do NOT `grep` the tree for the marker: `tools/quality/size.py`, its config and
its tests all contain the literal string and always will*** — ⭐ **and I wrote a
`grep` trigger into a row four paragraphs after quoting the sweep that exists
because of it.**

⛔ **CORRECTED IN THIS COMMIT: `W52`'s trigger is the `ast` sweep, which returns
`0` today and non-zero when a real deferral is written.**

⭐ **Why this is `[structural]` and not an embarrassment I could have quietly
fixed:** ⛔ **it is Ruling 122's case, produced by the round that ROWED Ruling
122, inside the row minted from `W45/3`.** ⚠️ **The CTO bound the ruling to their
own office first — *an unrun instrument minted in a ruling carries more authority
and gets less scrutiny than one in a branch*.** ⭐ **A row on this board is the
same shape: it is read as a decision, not as a draft, and nothing between here
and a developer's terminal runs it.** ⛔ **So `W53` binds the PO too, and this
finding is the evidence — measured, in the same commit, by the person the rule
was written for.**

⚠️ **It is also the FOURTH consecutive round in which the same class landed: a
CLAIM about an instrument, believed because it read like one.** ⭐ **Ruling 116
named an unreachable command; `W40`'s carve-out named a derivation that returns
the wrong set; the round-34 verdict read a truncation as a demonstration; and
this row named a `grep` its own rubric forbids.** ⛔ **Four different authors,
three different offices, one mechanism.**

#### ⚠️ `PO-28/6` `[local]` — I corrected my own `+142` and the number that carries forward is `+86`

⛔ **I relayed `SK-02` as **+142 tests**. The CTO measured **+86**.** ⭐ **My base
was two merges stale.**

**Measured** 2026-09-10 at `a00337b`: base `426672c` → **3419**, `SK-02`'s merge
`3cbf510` → **3505**, difference **86** — **`[RECEIVED: CTO-34/7]`** for both
endpoints; ⛔ **the branch's own base `2d86328` → 3363 is `[RECEIVED: SK-02's
handoff]` and is the number I quoted without its ref.**

⭐ **This is the third form of one defect in one night — a stale base quoted as a
merge delta, a hunk header quoted as a relocation, and a laundered claim quoted as
corroboration.** ⛔ **Ruling 115 exists because of the third. The first wants the
same treatment and gets it here: A NUMBER CARRIES THE REF IT WAS TAKEN AT, OR IT
IS NOT A NUMBER** — ⚠️ **which is already `W46`'s clause, and this finding is
recorded as its second worked example rather than as a new rule.**

---

## ⛔ ROUND 27 — the next two rows, the R11 pre-dispatch sum, and five mints

⭐ **Measured at `426672c`, branch `chore/po-round27`, linked worktree `wt/po27`**
— ⛔ **the ref AND the checkout** (Ruling 108, narrowed by `CTO-31/4`).
⚠️ **Every number in this section was RE-DERIVED here, and where one arrived
from the coordinator it is labelled — Ruling 115, on the round that minted it.**

⛔ **The tip moved TWICE while this round was being run** — `987eac4` when the
brief was written, `426672c` when it was finished, with `W43` (`2caa0d2`) and
`SF-35` (`a53aee8`) merging in between. ⭐ **Every reading below names `426672c`
and none names a branch**, which is `W43/2` treated as an instruction rather
than as a finding somebody else filed.

### ⭐ THE NEXT TWO ROWS — placed, not dispatched

⭐ **The collision set dissolved.** ⛔ **Round 26 held four rows because
`SF-35` and `SF-36` were both live on `validate/source.py`. Both have merged,
so the hold is spent** — ⚠️ **and re-measuring it moved `W44` from queued-8th to
NEXT, and put a row in front of it that did not exist when the round opened.**

| | ⭐ **Row** | ⛔ **Why it, and what it is NOT** |
|---|---|---|
| **NEXT 1** | ⛔ **`W45`** — Ruling 114: the deferral reader takes the WHOLE justification | ⭐ **MINTED THIS ROUND, and it is small: `tools/quality/size.py` is 122 lines.** ⛔ **It is not tidy-up — it is the only thing standing between the board and dispatching `W44`.** ⚠️ **[Gated BEFORE `W44`, and the gate has a reason that can fail](#w45-minted-ruling-114-the-deferral-reader-takes-the-whole-justification-and-the-tree-has-exactly-one-live-instance-to-test-it-against)** |
| **NEXT 2** | ⭐ **`W44`** — `validate/source.py` becomes a package | ⛔ **ITS GATE HAS CLEARED**: it was *"after both `SF-35` and `SF-36` merge"* and both are ancestors of `426672c`. ⭐ **The tree is over R11 RIGHT NOW — 425 against 400 — and the only thing making that legal is a deferral naming this row.** ⚠️ **Gains Ruling 116's acceptance and `SF-36/1`'s documentation bullet** |

⛔ **THE R11 PRE-DISPATCH SUM — `PO-26/1`'s sub-step, run for the first time on
rows it was written for.** ⭐ **The check is: when two rows in one wave share a
file, sum their expected growth against R11's ceiling BEFORE dispatching them in
parallel.**

| | `W45` | `W44` | shared |
|---|---|---|---|
| `src/` surface | — | ⛔ **`src/studyforge/validate/source.py` → `validate/source/`** | ⭐ **none** |
| `tools/` surface | ⛔ **`tools/quality/size.py` (122), `tools/quality/config.py` (299)** | — | ⭐ **none** |
| test mirror | `tools/tests/quality/test_size.py` (**144**) | `tests/studyforge/validate/test_source.py` (**574**) | ⭐ **none** |
| ⛔ **Intersection** | | | ⭐ **∅ — the sum is not needed and that IS the reading** |

⚠️ **Both cells verified against the tree at `426672c` with `git ls-tree` and
`wc -l`, not against another document** — ⭐ **and `W` rows are minted here, so
this board IS their definition and the cells are ORIGINALS, which is round 26's
`Owns`-is-a-pointer ruling read the way it was written.**

⛔ **THE GATE BETWEEN THEM IS A MERGE ORDER, NOT A DISPATCH ORDER.** ⭐ **The
surfaces are disjoint, so both may be dispatched today; `W45` must MERGE first,
and that is an acceptance condition on `W44` with an instrument beside it:**

| | |
|---|---|
| **the claim** | `W45` is in `W44`'s merge base at review time |
| ⛔ **the instrument** | ⭐ `git merge-base --is-ancestor <W45's merge> HEAD` → **exit 0**. ⚠️ **exit 1 REFUSES the review** |

⭐ **Why the order and not the reverse, stated so it can be argued with:**
⛔ **`W44` DELETES the tree's only deferral.** ⚠️ **`W45` fixes the reader that
parses deferrals, and after `W44` there is nothing left in the tree to test it
against** — ⭐ **so `W45` merging second turns a live negative control into a
fixture somebody has to invent.** ⛔ **That is the same shape as `W32`: a check
whose subject does not exist is unfalsifiable, and here the subject exists for
exactly one row's worth of time.**

### ⛔ What was HELD and is now free, and what is still held

| Row | ⛔ **Round 26 said** | ⭐ **True at `426672c`** |
|---|---|---|
| `W40` | **HELD** — `SF-36` edits `test_document.py` | ⭐ **FREE. `SF-36` merged.** ⚠️ **And its FRAMING is wrong — `CTO-32/8`, [re-framed below](#w40-re-framed-round-27-cto-328-the-population-is-derived-at-pick-up-not-enumerated-in-the-row)** |
| `W41` | **HELD** — both live branches edit `source.py` | ⛔ **STILL HELD, and now for ONE reason instead of two: `W44` restructures the file.** ⭐ **AFTER `W44`, unchanged** |
| `W44` | **queued 8th**, gated behind two merges | ⭐ **NEXT 2. Gate cleared** |
| `W43` | **NEXT 2**, `todo` | ✅ **DONE, merged `2caa0d2`** |
| `SK-02` | **NEXT 1**, `pair`, not splittable at its first half | ⏳ **IN FLIGHT — `wt/dev1i`, branch `feat/SK-02-adapter-skill` at `2d86328` with ZERO commits and an UNTRACKED `src/studyforge/skills/adapter/`.** ⛔ **A branch name is not a branch state (`PO-23/4`) and this is the case where the instrument reads *nothing in flight* about work that is under way** |

### ⛔ `W40` RE-FRAMED ROUND 27 — `CTO-32/8`: the population is DERIVED at pick-up, not enumerated in the row

⛔ **The board read *"the two test modules at R11's ceiling"* at `BOARD.md:2444`
for three rounds and the CTO named it three times.** ⭐ **It is not a stale
number — it is a stale KIND. The row enumerated a population, and a population
enumerated in a row is a second copy that nothing re-measures**, which is this
board's own repeated finding arriving inside a row instead of inside a status.

**Measured at `426672c`, every tracked `.py` outside `tests/fixtures/`, against
R11's 400 (`src/`, `tools/`) and 600 (`tests/`):**

| module | lines | ceiling | ⛔ **headroom** |
|---|---|---|---|
| ⛔ **`src/studyforge/validate/source.py`** | **425** | 400 | ⛔ **−25 — OVER, and legal only via `W44`'s deferral** |
| ⛔ **`src/studyforge/corpus/manifest/content.py`** | **400** | 400 | ⛔ **0** |
| ⛔ **`tests/test_gate_coverage.py`** | **600** | 600 | ⛔ **0** |
| ⚠️ `tests/studyforge/corpus/container/test_document.py` | 598 | 600 | ⚠️ **2** |
| `src/studyforge/archive/scrub.py` | 384 | 400 | 16 |
| `tests/docker/test_dev_image.py` | 583 | 600 | 17 |
| `tools/tests/workspace/test_init.py` | 378 | 400 | 22 |
| `tests/studyforge/validate/test_source.py` | 574 | 600 | 26 |
| `src/studyforge/corpus/manifest/document.py` | 370 | 400 | 30 |
| `tests/studyforge/corpus/manifest/test_document.py` | 562 | 600 | 38 |

⭐ **So the row's subject is not *these modules*. It is: NO MODULE IN THE TREE
SITS AT ZERO HEADROOM against R11** — ⛔ **and the population is derived by a
command at pick-up, which is what makes it survive the next merge.**

⛔ **`validate/source.py` is EXCLUDED BY THE DERIVATION ITSELF, not by a
sentence somebody has to remember:** ⭐ **it carries a live `Size exception:`
deferral naming `W44`, and a module under a live deferral belongs to the row
named in it.** ⚠️ **That is why `W40` and `W44` do not collide even though both
are R11 splits** — ⛔ **the carve-out is an instrument, not an instruction.**

### ⛔ THE ROWS OWED FROM ROUND 32, LANDED — and `CTO-33/5` is why they nearly were not

⛔ **`Ruling 111` and `CTO-32/8` had been stated three times and had reached no
artifact.** ⭐ **Measured at `987eac4`, before this round's edits:
`grep -rn 'Ruling 111' docs/` and `grep -rn 'CTO-32/' docs/`, each excluding
`CTO-2026-09-10-round32.md`, returned **0** and **0**.**

⚠️ **`CTO-33/5` reads it as SEQUENCING rather than transmission failure — no PO
round ran between round 32 and this one — and that reading is correct and it is
also the finding.** ⛔ **A ruling whose only carrier is *"the next PO round will
pick it up"* is carried by a schedule, and a schedule is not an artifact.**
⭐ **Both landed in this round's edits: `Ruling 111` on `W37`'s row,
`CTO-32/8` in `W40`'s re-framing above.**

### ⛔ ROUND 27 — the six wave-open checks

⭐ **Run at `426672c`, linked worktree `wt/po27`, pinned image, except where a
row names another checkout.**

| # | Check | ⛔ **Reading @ `426672c`** |
|---|---|---|
| **1** | index present and current | ⚠️ **SPLIT, and both halves are correct.** ⛔ **MAIN checkout: `fresh — built at 426672c2`** (relayed by the coordinator — **RECEIVED**, Ruling 115). ⭐ **`wt/po27`, measured by me: `none — none in this checkout`, and the floor says *"This is not a failure"*.** ⛔ **`graphify-out/` is untracked, so `git worktree add` does not carry it — Ruling 108, and `W43`'s clause 2 says to name the checkout rather than the tree.** ⭐ **`document pointers: 75 read in 135 markdown files, 31 carrying an anchor, 0 unresolved` · `quality floor: clean`, exit 0** |
| **2** | `[structural]` triage | ⭐ **RUNNABLE THIS ROUND, and that is the change.** ⛔ **`git grep -EIc '\`\[(local\|structural\|none)\]\`' 426672c -- docs` → **504 lines / 87 files**, up from **455 / 81** at `d77cb85`.** ⚠️ **It reproduces because `PO-26/2` wrote the instrument down last round; the numbers quoted BEFORE round 26 still reproduce under no candidate, and that half is `W42`'s** — ⛔ **`PO-27/1` below** |
| **3** | C6 — every ruling reached its artifact | ⛔ **1 of 3 at open, 3 of 3 at close.** ⭐ **Population: rulings 111, 112, 113 — every one minted since round 26's check.** ⛔ **111 → NO artifact at `987eac4` (0 hits outside the round-32 handoff); landed on `W37`'s row THIS ROUND.** ⭐ **112 → struck in place by 113 in the ruler's own commit; a struck ruling owes no artifact and this one says so.** ⭐ **113 → `review-rubric.md:563`, §3c, in the ruler's own commit.** ⚠️ **Rulings 114–116 are NEWER than this check's population and are rowed below, not swept here** |
| **4** | re-measure every row whose trigger has passed | ⛔ **SEVEN stale rows — [the table below](#check-4-round-27-the-rows-and-the-one-the-sub-step-found)** |
| **5** | `CLAUDE.md`'s *Where to start* | ✅ **PASS.** ⭐ **It says M0 and M1 closed, *"Open: M2 — a corpus is readable. In flight: M2 step 2.1"*, and it explicitly refuses to carry either MEMBERSHIP or STATE.** ⛔ **Both claims are still TRUE at `426672c` — step 2.1 is open on `SK-02` alone — so the file is current and needs no edit.** ⚠️ **The `SF-10` hit is still inside the round-19 correction record; re-taken with `-C3` per `W43`'s clause 2 and REFUSED as a reading, exactly as `PO-26/3` predicted it would be** |
| **6** | catalogue contributions | ✅ **NOTHING NEW OWED.** ⭐ **`../ISO-8583-jPOS-tutorial` @ `6c8dc85`** — ⚠️ **the same ref the third, fourth, fifth and sixth runs measured, and `catalogue-contributions.md` last moved at `4351f28`, before any of them.** ⛔ **The catalogue stands at **19** entries — counted as `grep -c '^### '`, and the instrument is written down because `grep -c '^| '` returns **17** and would have looked like drift.** ⚠️ **`../Claude-senior-java-engineer` @ `c9cf522` and `../Claude-SPARQL-tutorial` @ `b9aa89b` have NO `docs/studyforge/` directory, so neither contributes and neither can** |

⭐ **AND A SEVENTH, standing from Ruling 113 and run here for the first time on a
non-empty tree: every id in a `Size exception:` reason is a LIVE board row.**

```text
src/studyforge/validate/source.py: Size exception: W44 splits this module into a package, and it is deferred to
```

⛔ **ONE deferral, `W44` is live, the check PASSES** — ⚠️ **and look at where the
printed line stops: `…and it is deferred to`, mid-sentence.** ⭐ **The id is
visible only because of where this developer's sentence happened to wrap, which
is Ruling 114 demonstrating itself in the wave check that motivated it.**

#### ⛔ CHECK 4 ROUND 27 — the rows, and the one the sub-step found

| # | Row | ⛔ **What it said** | ⭐ **True at `426672c`** |
|---|---|---|---|
| 1 | head — step 2.1 | *"five tasks; TWO ARE DONE and three remain"* | ⛔ **FOUR done; `SK-02` alone remains** |
| 2 | head — the R11 pair | *"398 on `SF-35`, 419 merged"* | ⛔ **425 IN THE TREE, with a deferral.** ⚠️ **419 / 420 / 421 / 425 are four accurate readings of four different trees (`SF-35/5`, `CTO-33`)** |
| 3 | head — next two rows | *"`SK-02` and `W43`"* | ⛔ **`W43` MERGED `2caa0d2`; `SK-02` in flight.** ⭐ **Re-placed: `W45`, `W44`** |
| 4 | base paragraph | `3261 / 63 @ ce58a36` | ⛔ **`3419 / 63 @ 426672c`** |
| 5 | queue — `W40` **HELD** | *"`SF-36` edits `test_document.py`"* | ⭐ **FREE, and its FRAMING is wrong — `CTO-32/8`** |
| 6 | `W34`'s row | *"`review-rubric.md` 2015 lines @ `d77cb85`"* | ⛔ **2068 — SIXTH consecutive round of growth: 1611 → 1784 → 1881 → 1951 → 2015 → **2068*** |
| ⭐ **NEW — the sub-step** | `W45` vs `W44` | — | ⭐ **∅ intersection, verified before dispatch rather than at the second lander's review.** ⛔ **This is the first wave in which `PO-26/1`'s step ran BEFORE the dispatch it was written for** |

### ⛔ `PO-27/1` — check 2 is reproducible now, and the fix was writing down the instrument

⛔ **`[structural]`.** ⭐ **`PO-26/2` said check 2 had been quoted for six rounds
with no recorded instrument and could not be reproduced at any ref.** ⚠️ **It is
reproducible THIS round, at the first attempt, and nothing about the sweep
changed** — ⭐ **the only thing that changed is that last round wrote the command
into the row.**

⛔ **That is worth more than the number: the check was not broken, it was
UNNAMED** — ⚠️ **and an unnamed instrument fails silently, because every run
returns a number and no run returns a disagreement.** ⭐ **The residue is still
`W42`'s and it is unchanged: the numbers quoted BEFORE round 26 reproduce under
no candidate, the file counts miss by exactly **8**, and the CTO reads that 8 as
`extend-exclude`'s `tests/fixtures/` files against a **463** population.**
⛔ **This round supplies an independent check of that reading and it AGREES:**
the same 8 files are the entire difference between `475` tracked `.py`/`.md` and
the `467` `ruff` walks.

**Measured** 2026-09-10 at `426672c`, `wt/po27`:

```text
git grep -EIc '`\[(local|structural|none)\]`' 426672c -- docs   -> 504 lines / 87 files
git ls-tree -r --name-only 426672c | grep -Ec '\.(py|md)$'      -> 475
  ... same, restricted to tests/fixtures/                       -> 8
docker/dev/check python3 -m tools.quality  (wt/po27)            -> 467 file(s) already formatted
docker/dev/check python3 -m tools.quality  (MAIN, relayed)      -> 468   [RECEIVED]
```

### ⛔ `PO-27/2` — a claim I injected returned to me wearing a finding's authority

⛔ **`[structural]`. Filed against MY OWN briefing**, and the CTO has ruled it as
**Ruling 115**.

⛔ **I told the CTO that `SF-36` relocated a constant block. It does not.**
⚠️ **I had told Developer 1 the same thing first; they recorded it in `SF-35/4`;
I then cited their finding back to the CTO as INDEPENDENT CORROBORATION of a
claim that originated with me.** ⭐ **The same finding's other half — the line
count — they genuinely did reproduce by re-running `git merge-file`.** ⛔ **The
two arrived in one finding and I read both as measured.**

⭐ **Why it is NOT `W43`'s clause 2, and the distinction is the whole ruling:**
⛔ **a proxy still points at the thing** — a branch really has a tip. ⚠️ **A
laundered reading points at NOTHING; its entire authority came from having been
written down**, and the round-trip through a handoff is what manufactured it.

⛔ **ROUTED: `agent-protocol.md`, beside clause 2 — and the `delivery-flow.md`
half is routed with it**, because *a brief states a SHA and the receiver
re-derives it* happens BETWEEN roles and `delivery-flow.md` is where between-
roles lives. ⭐ **Both are `W46`, minted below.** ⛔ **NOT into `W43`: that branch
is merged, and a remedy that edits its own subject measures nothing.**

**Measured** 2026-09-10 — ⭐ **and this reading is the CTO's, RECEIVED, which is
the clause applied to the finding that created it:**

```text
git diff 16049d2 987eac4 -- src/studyforge/validate/source.py \
  | grep -c '^[-+].*IGNORE_DECLARATION'        -> 0      [RECEIVED: CTO-33/4, SF-35/7]
```

⚠️ **I did not re-run it, and under Ruling 115 that is legal and must be
stated.** ⛔ **What I contribute is not corroboration — it is the ORIGIN, which
is the one fact neither the developer nor the CTO could supply.**

### ⛔ `PO-27/3` — the third role to commit `CTO-29/8` in one round, and it happened inside the review of `CTO-29/8`

⛔ **`[structural]`. Recorded here rather than left in a handoff, because the
count is the argument.** ⭐ **In ONE round: a developer (`SF-35/4`), the
coordinator (`PO-27/2`), and the CTO — whose `awk` stopped at a blank line and
nearly filed the two BEST-instrumented acceptance sections in the repository as
the worst clause-1 hits.** ⚠️ **The emptiness was a property of their reader.**

⭐ **Each was caught by the same move and by no other: OPENING THE LINES BEFORE
QUOTING THEM.** ⛔ **That is `W43`'s clause 2 *owe the surrounding line*, and it
is now the only instrument with three independent saves in one round.**
⚠️ **It is also why `W47`'s index is a row and not a nicety: the document that
carries that clause is 825 lines with 34 headings and no index.**

**Measured** 2026-09-10 at `426672c`: `wc -l docs/conventions/agent-protocol.md`
→ **825**; `grep -c '^#'` → **34**. ⭐ **The three instances are `SF-35/4`,
`PO-27/2` and `CTO-33`'s own negative control — the last two RECEIVED, and named
as such.**

### ⛔ FIVE ROWS MINTED — `W45`, `W46`, `W47`, `W48`, `W49`

⛔ **High-water mark moves `W44` → `W49`; measured across every branch in the
repository at `426672c` — `git grep -In '\bW4[5-9]\b' $(git rev-list --all)`
returns NOTHING outside this round's own commit.** ⭐ **`W28` and up are minted
by the PO only, and this is the mint.**

⚠️ **FOUR of the five are CTO round 33's *"what the PO must row"*, item for
item.** ⛔ **The fifth (`W49`) is not on their list and I am saying so: they
handed the seven clause-1 failures over as *authoring guidance* and named a row
as a CANDIDATE. I am rowing it, because guidance with no row is the exact carrier
`CTO-33/5` just measured failing.**

#### ⛔ `W45` — MINTED. **Ruling 114: the deferral reader takes the WHOLE justification, and the tree has exactly ONE live instance to test it against**

| | ⛔ **`W45`** |
|---|---|
| **What** | ⭐ **Three changes, one row (Ruling 114 says *"one row, not two"*): `size_exception()` returns the whole justification rather than the marker line; the row id is REQUIRED on the marker line; and `check_sizes`' remedy text offers BOTH §3c forms instead of only `<why splitting would be worse>`** |
| **From** | ⛔ **Ruling 114, ratifying `SF-35/6`** — ⭐ **the CTO calls it *"a defect in my own Ruling 113"*** |
| **Owner** | framework agent, **queued NEXT 1** — ⛔ **NOT dispatched by this row** |
| ⛔ **Owns** | ⭐ **`tools/quality/size.py` (**122**), `tools/quality/config.py` (**299**) if the marker constant moves, and the mirror `tools/tests/quality/test_size.py` (**144**)** — ⚠️ **verified with `git ls-tree` and `wc -l` at `426672c`, not read off another document** |
| ⛔ **When — and the gate has a reason that can FAIL** | ⭐ **BEFORE `W44` merges.** ⛔ **`W44` deletes the tree's only `Size exception:`, and this row's negative control IS that line.** ⚠️ **Merge it after `W44` and the fix ships against a fixture somebody invented** |
| ⛔ **Why it is not cosmetic** | ⭐ **`MIN_JUSTIFICATION_CHARS` is 20 and it is measured against the marker line too**, so a long, correct, multi-line justification with a short first line is REFUSED for being short — ⚠️ **a false negative and a false positive in the same function** |
| ⛔ **Acceptance — clause 1's two columns** | **claim:** a deferral whose id is on the marker line is accepted and prints its id; one whose id wraps is REFUSED with a message naming both §3c forms. ⭐ **instrument:** two docstrings differing only in where the line breaks, as unit tests in `tools/tests/quality/test_size.py`; ⛔ **and the negative control run against the tree's real deferral — strip it and `tools.quality` exits **1** with exactly one finding** |
| ⛔ **Ruling 75 — what it jumps** | ⭐ **`W37`, `W36`, `W38`, `W35`, `W42`, `W34`.** ⚠️ **The licence is that the row it precedes is already dispatchable and this one is its gate** |

#### ⛔ `W44` GAINS TWO CLAUSES THIS ROUND — Ruling 116's acceptance, and `SF-36/1`'s documentation bullet

⛔ **Both were ruled elsewhere and neither had reached this board.** ⭐ **They are
written HERE, in the row, because `CTO-32/4` and `CTO-33/5` are the same lesson
twice: a clause that lives only in a handoff has not landed.**

⭐ **RULING 116 — the acceptance clause, and it is the FIRST row authored under
`W43`'s clause 1, so it is written in two columns or it is not written:**

| | |
|---|---|
| **the claim** | ⭐ **`validate/source.py` is a package and NO `Size exception:` remains anywhere in it** |
| ⛔ **the instrument** | ⭐ **`docker/dev/check python3 -m tools.quality` → exit **0**, ⛔ **AND** ~~`git grep -c 'Size exception:' -- src/` → **0**~~ — ⛔ **REPLACED AT ROUND 28 BY RULING 121, and the replacement is `git grep -l 'Size exception:' -- src/ \| wc -l` → **0**, the reading being the PRINTED NUMBER and never `$?`** — ⛔ **THEN NARROWED AT ROUND 29 BY RULING 123: that grep is the CORROBORATOR, not the gate. THE GATE IS §3c's `ast` sweep at **ROWS=0** ([the two, side by side](#w44s-acceptance-ruling-123s-narrowing-and-the-two-instruments-disagree-on-a-real-input))** |

⛔ **RULING 123, LANDED HERE ROUND 29 — the grep is DEMOTED, and the two
instruments DISAGREE on a real input, which is the whole reason one of them is
the gate.** ⭐ **`[RECEIVED: CTO-36/4]` for the discrimination, RE-MEASURED by me
at `ddddd05` for the pass reading:**

| | ⛔ **the GATE** | ⭐ **the CORROBORATOR** |
|---|---|---|
| what | §3c's `ast` sweep — `W40`'s derivation B | `git grep -l 'Size exception:' -- src/ \| wc -l` |
| pass reading @ `ddddd05` | ⭐ **`ROWS=0`** | ⭐ **`0`** |
| ⛔ **marker in a COMMENT** | ⭐ **correctly IGNORED** — it reads the first DOCSTRING only | ⛔ **FALSE POSITIVE** |
| ⛔ **a TYPO in the pattern** | ⭐ **impossible: `config.SIZE_EXCEPTION_MARKER`** | ⛔ **returns `0`, which IS the pass reading** |

⚠️ **`W44` is MERGED, so this correction is a RECORD and not a gate** — ⛔ **and
it is made anyway, because the next row to reach for an acceptance instrument
reads this block, not the merge.**

⛔ **RULING 121, LANDED HERE ROUND 28 — the instrument above was INVERTED, and
`W44` was in flight against it.** ⭐ **`git grep -c` cannot return `0`: on a match
it prints `path:count` and exits **0**; on no match it prints NOTHING and exits
**1**.** ⚠️ **Measured by me at `a00337b`, `wt/po28`, both directions:**

```text
git grep -c 'Size exception:' -- src/            -> src/studyforge/validate/source.py:1 , exit 0
git grep -l 'Size exception:' -- src/ | wc -l    -> 1        [the fail state, today]
git grep -l 'Size exception:' -- src/studyforge/serve/ | wc -l -> 0   [the pass state]
```

⛔ **It does not merely misstate a number, it INVERTS.** ⭐ **Script the number and
a correct branch FAILS; script the exit code and the branch PASSES exactly when
the stale deferral SURVIVES** — ⚠️ **the failure state passing, which is the one
direction a gate may never fail in.** ⛔ **`W45/2` measured it, the CTO ratified
it as Ruling 121, and neither of them edited this cell, because a row's
acceptance is the PO's to write** — ⭐ **which is the working agreement working,
and is why this correction is here rather than in a handoff.**

⛔ **The second half is not decoration, and the reason is the best argument for
clause 1 anyone has produced yet:** ⚠️ **`tools.quality` ALONE CANNOT FAIL THIS
CONDITION.** ⭐ **Once the package is split, every file is under the ceiling, so
`check_sizes` never opens the docstring — and a stale deferral survives GREEN.**
⛔ **A check that cannot fire, found by writing the instrument column.** ⚠️ **And
the residue is a real defect: a deferral pointing at a LANDED row is *a deferral
nobody owns*, which §3c makes a finding against the RELEASE BRANCH — so deleting
the line is the LAST STEP OF `W44`, never cleanup.**

⭐ **`SF-36/1` — the documentation bullet, ruled by the CTO to ride here:**
⛔ **spec §4's worked example still declares `container_api: 1` and documents no
region shape.** ⚠️ **Verified by me at `426672c`, not inherited:
`grep -n 'container_api' docs/specs/2026-09-08-studyforge-v1-design.md` → line
**438** (the register row) and line **892** (`{ "container_api": 1,` — the
worked example).** ⚠️ **It read `827` at `987eac4` two hours earlier and `SF-35`'s
spec edits moved it — ⛔ which is exactly why `W49`'s first step is to re-derive
its own seven line numbers rather than inherit them.** ⛔ **`SF-36` bumped the contract to `2` and the example still
teaches `1`.**

⭐ **The transferable half, and it is R9's register note generalised:** ⛔ **a
contract bump and its worked example land in ONE commit, or the example teaches
the old shape to the next reader.** ⚠️ **`SF-35`'s definition already carried
exactly this clause and `SF-36`'s did not, which was the real defect — and the
CTO ruled that `SF-36/1` binds neither `e4a2677` nor its successor, because
`docs/specs/` was outside that developer's `Owns` and R20 keeps a spec example
from being a task's silent scope.**

#### ⛔ `W46` — MINTED. **Ruling 115: a finding states, PER CLAIM, whether it was measured or received**

| | ⛔ **`W46`** |
|---|---|
| **What** | ⭐ **Two clauses, two files.** ⛔ **`agent-protocol.md`, beside clause 2: a finding states for each load-bearing claim whether it was MEASURED (with the command, per §8a's `Measured` field) or RECEIVED (naming the source); a received claim may be true and citing it is fine, ⛔ but it may NEVER be offered as corroboration of its own source.** ⭐ **`delivery-flow.md`: a brief STATES a SHA and the receiver RE-DERIVES it** |
| **From** | ⛔ **Ruling 115**, on `PO-27/2` / `CTO-33/4`; ⭐ **and `W43/2`'s process half, which the CTO routed to `delivery-flow.md` rather than to `agent-protocol.md`** |
| **Owner** | framework agent, **queued** |
| ⛔ **Owns** | ⭐ **`docs/conventions/agent-protocol.md` (**825**) and `docs/conventions/delivery-flow.md` (**359**)** — ⚠️ **measured at `426672c`** |
| ⛔ **PER CLAIM, not per finding** | ⭐ **`SF-35/4` carried TWO halves — a line count they reproduced by re-running `git merge-file`, and a relocation they received from the coordinator.** ⛔ **They arrived in one finding and were read as equally load-bearing.** ⚠️ **A per-FINDING provenance field would have marked that finding *measured* and been correct and useless** |
| ⛔ **When** | ⭐ **BEFORE `W47`.** ⚠️ **An index built before a clause lands is stale on arrival** |
| ⛔ **Acceptance — clause 1's two columns** | **claim:** both files carry the clause and `delivery-flow.md`'s half names the receiver's obligation, not only the sender's. ⭐ **instrument:** `W48`'s `handoff-measured` rule is the enforcement arm and is a SEPARATE row — ⛔ **so this row's instrument is `docker/dev/check python3 -m tools.quality` → exit 0 plus the two clauses quoted in the handoff by line number**, and the row says so rather than pretending prose is gated |
| ⛔ **Ruling 75 — what it jumps** | ⭐ **`W37`, `W36`, `W38`, `W35`, `W34`.** ⚠️ **Licence: three roles committed the class in one round (`PO-27/3`)** |

#### ⛔ `W47` — MINTED. **`agent-protocol.md` is 825 lines, 34 headings, no index — and its own clause 2 now distrusts `grep` on it**

| | ⛔ **`W47`** |
|---|---|
| **What** | ⭐ **A heading index at the top of `agent-protocol.md`.** ⛔ **NOT a split** — a split breaks every citation of the form *"see `agent-protocol.md`, §…"*, and the CTO and the developer independently reached the same conclusion |
| **From** | ⛔ **`W43/4`, ratified as `CTO-33/7`** |
| **Owner** | framework agent, **queued** |
| ⛔ **Owns** | ⭐ **`docs/conventions/agent-protocol.md`** — ⚠️ **the SAME file as `W46`, which is why it is gated behind it rather than dispatched beside it** |
| ⛔ **The argument, and it is not tidiness** | ⭐ **The only way to navigate the instrument every row is judged with is `grep`** — ⛔ **and that document's own clause 2, merged at `2caa0d2`, has just ruled `grep` unsafe on a document carrying corrections.** ⚠️ **`CTO-33/6` measured the refusal rate on it: **42 of 698** lines sit within ±3 of a correction marker.** ⛔ **So one line in seventeen is a hit a reader must open before quoting, on the file they cannot navigate any other way** |
| ⛔ **Acceptance — clause 1's two columns** | **claim:** every `##`/`###` heading in the file appears in the index, and the index carries no heading the file does not. ⭐ **instrument:** ⛔ **`diff <(grep -n '^#\{2,3\} ' <file> | …) <(the index)` → empty**, run as a test in `tools/tests/`, so a heading added later without an index entry FAILS. ⚠️ **A hand-written index with no test is a second copy, which is this board's most-repeated finding** |
| ⛔ **When** | ⭐ **AFTER `W46`** |

#### ⛔ `W48` — MINTED. **`handoff-measured`, and the clause-1 denylist — `W43`'s two clauses get their enforcement arms**

| | ⛔ **`W48`** |
|---|---|
| **What** | ⭐ **Two lints on one surface.** ⛔ **(a) `handoff-measured`: a FIFTH `tools/quality/handoffs` rule — a finding line carrying `[local]` or `[structural]` owes a `Measured` line in the same document naming a command AND a ref.** ⭐ **(b) the clause-1 DENYLIST over `docs/tasks/E*.md`'s `**Acceptance.**` paragraphs, using the clause's own wordlist — *documented*, *consistent with*, *reviewed*, *as appropriate*** |
| **From** | ⛔ **`W43/1`'s first half (agreed as a task by CTO round 33, *"the PO mints it"*) and `CTO-33/3`, which REFUTED `W43/1`'s second half** |
| **Owner** | framework agent, **queued** |
| ⛔ **Owns** | ⭐ **`tools/quality/handoffs/contract.py` (**229**) and its mirror** — ⚠️ **measured at `426672c`** |
| ⛔ **It rides with `CTO-29/4`** | ⭐ **`FINDING_MARKERS` is unguarded, same surface, and the CTO confirmed the reader already exists: `marker_lines()`, `_MARKERS_ON_LINE`, `_FINDING_LEAD` are all in `contract.py` today.** ⛔ **A rule on an existing reader, not a new reader** |
| ⛔ **IT COLLIDES WITH `W42`** | ⚠️ **Both write `tools/quality/handoffs/`.** ⛔ **ONE DISPATCH: the same developer takes both, or `W48` merges first and `W42` re-measures.** ⭐ **Named here because `PO-26/1` exists precisely so this is found at wave-open and not at the second lander's review** |
| ⛔ **RULED — the `[none]` scope question, which the CTO left to me** | ⭐ **`[none]` IS in scope.** ⚠️ **The CTO's own argument for leaving it out is that it is *an exposure verdict rather than a reading* — ⛔ but they then wrote *"`[none]` is still a CONCLUSION from a measurement"*, and that is the whole of it.** ⭐ **`MIN_NONE_CHARS` already forces a sentence; forcing the sentence to name a command is the same rule one notch tighter, and a `[none]` nobody can reproduce is exactly the `0` that `MIN_NONE_CHARS` was written because nobody could reproduce** |
| ⛔ **Do NOT inherit `W43/1`'s asymmetry** | ⚠️ **`W43/1` ruled clause 1 *not machine-checkable by design*.** ⛔ **REFUTED by `CTO-33/3`, who ran it: **7 hits in 4 epics**.** ⭐ **That was a property of the CURRENT reader stated as a property of the RULE — `CTO-29/8` again, and the fourth instance this round** |
| ⛔ **Acceptance — clause 1's two columns** | **claim:** both rules are registered in `CHECKS` and each was watched to FAIL first. ⭐ **instrument:** ⛔ **`docker/dev/check python3 -m tools.quality` → exit **1** on a crafted violation of each rule separately, then exit **0** after the fix** — ⚠️ **and the denylist reports its COVERAGE, per `agent-protocol.md`'s *a new check reports its coverage, not just its hits*, because it is PARTIAL and must never claim completeness** |

#### ⛔ `W49` — MINTED. **The seven live acceptance conditions that `W43`'s clause 1 fails**

| | ⛔ **`W49`** |
|---|---|
| **What** | ⭐ **Give each of seven acceptance conditions an instrument, or DROP it** — ⛔ **and dropping costs nothing, because a condition that could never fail was never doing any work (clause 1's own words)** |
| **From** | ⛔ **`CTO-33/3`.** ⚠️ **The CTO named a row as a CANDIDATE and handed the seven over as authoring guidance; ⭐ I am rowing them, because `CTO-33/5` is this round's measurement of what guidance-with-no-row does** |
| **Owner** | framework agent, **queued** |
| ⛔ **Owns** | ⭐ **`docs/tasks/E00-foundations.md` lines 111, 112, 213, 215; `docs/tasks/E04-*.md`:298; `docs/tasks/E06-*.md`:143; `docs/tasks/E08-*.md`:121** — ⚠️ **line numbers are the CTO's reading, RECEIVED; ⛔ the row's FIRST step is to re-derive them with `W48`'s lint, because line numbers drift and a row that inherits them is `PO-27/2`'s shape** |
| ⛔ **The seven** | `E00:111` *"return **useful** answers"* · `E00:112` *"is **documented** and works incrementally"* · `E00:213` *"complete and **internally consistent**"* · `E00:215` *"**small enough to read**"* · `E04:298` and `E06:143` *"**fully keyboard accessible**"* · `E08:121` *"the report **states** an expected yield range"* |
| ⛔ **M0 STAYS CLOSED — ruled by the CTO and I am not reopening it** | ⚠️ **`E00:111`–`215` belong to `FND-02` and `FND-04`, both DELIVERED with an APPROVE recorded at `E00:217`.** ⭐ **The clause reaching retrospectively into approved work is the strongest available evidence that it does something** — ⛔ **and Ruling 97's shape applies: a close records what was true at a named ref under the standard of the day** |
| ⛔ **When** | ⭐ **AFTER `W48`**, whose denylist is this row's instrument and its definition of done |
| ⛔ **Acceptance — clause 1's two columns** | **claim:** every hit is instrumented or dropped. ⭐ **instrument:** ⛔ **`W48`'s denylist over `docs/tasks/E*.md` → **0** hits**, and ⚠️ **the row says out loud that 0 hits is not 0 unfalsifiable conditions — the lint is PARTIAL, it catches named phrases, and *"asserted"* naming no real test still passes it** |

---

## ⛔ ROUND 26 — one ruling, one mint, two rows placed, and a check that cannot be reproduced

⭐ **Measured at `d77cb85`, branch `chore/po-round26`, linked worktree `wt/po26`**
— ⛔ **the ref AND the checkout** (Ruling 108, as narrowed by `CTO-31/4`).

📏 **BASE (round 26): 3289 passed / 63 skipped in the pinned container at
`d77cb85`**, the release tip, floor clean, index **`fresh`** — ⚠️ **taken by the
coordinator in the MAIN checkout, and the checkout is named because
`CTO-31/4` settled that the divergence Ruling 108 recorded is a **HOST**
phenomenon and not a checkout one.** ⭐ **Ninth base. `W39` (`16049d2`, **+28**)
is the only merge since round 25's `ce58a36`.**

⛔ **THE SKIP SET, all 63 named, unchanged from round 31's:** 55 `tests/visual/`
(no browser in the pinned image — `QA-03/1`, `W36` removes them), 5
`tests/docker/test_dev_image.py` (already inside the image), 2
`tests/test_knowledge_index.py:125` (sibling checkouts absent), 1
`tests/test_knowledge_index.py:160` (no corpus repository with a built index).

⚠️ **CARRIED FORWARD, and it corrects a row of this board's own:** ⛔ **Ruling
108's measured row — *"main checkout `∩ 5`, linked worktree `∩ 7`"* — DOES NOT
REPRODUCE** (`CTO-31/4`, measured twice at `c1a5a79`: 28 unique `file:line` skip
rows in both checkouts, identical). ⭐ **`docker/dev/compose.yaml` mounts `../..`
and nothing else, so no sibling checkout is visible from EITHER checkout.**
⛔ **What survives is the whole of the ruling's value — name where a number came
from — and what is struck is the claim that the container column moves.**
⚠️ **[Ruling 108's row below](#rulings-105-106-and-108-carried-and-none-of-them-needs-a-row) is annotated in place.**

### ⛔ RULED ROUND 26 — `CTO-31/6`: `validate/source.py` has ONE owner, ONE licensed region, and a pair that breaches R11

⛔ **THE QUESTION.** `SF-35`'s `Owns` on this board included
`src/studyforge/validate/source.py`; `E01` carried the same file in `SF-35`'s
**`Context`** and gave it to `SF-36`'s **`Owns`**. ⚠️ **Both tasks were
dispatched and both edited it.** ⭐ **By this board's cells the intersection was
exactly that file; by `E01`'s cells it was EMPTY.**

#### The measurement, re-run by me rather than inherited

⛔ **Both diffs, at `d77cb85`, from the worktrees and not from a brief:**

| | `SF-35` (`wt/dev1h`, uncommitted) | `SF-36` (`e4a2677`, with the CTO) |
|---|---|---|
| **whole diff** | 12 files, **+709 −70** | 14 files, **+1017 −59** |
| **its half of `source.py`** | ⭐ the rule-constant block after `RULE_ORIGIN_MISSING`, and `check_unclassified` — its docstring and its classify loop | ⭐ the module docstring, the imports, `check_completeness`, `_compare`, and the EXTRACTION of `count_headings`/`HEADING_LINE`/`FENCE` into a new `validate/headings.py` |
| **lines changed there** | **43** | **110** |
| ⛔ **the file's own length** | **398** | **399** |

⭐ **Base is 377. The two are DISJOINT except one insertion anchor** — both
append a `#:`-commented constant block immediately after `RULE_ORIGIN_MISSING`
(`RULE_CONTESTED`; `RULE_SECTION_MISSING` + `RULE_SECTION_AMBIGUOUS`).
⛔ **Reproduced with `git merge-file`: exit 1, ONE conflict, three marker lines.**

#### ⛔ AND THE PART NOBODY'S GATE ASKED — the pair breaches R11

```text
git merge-file <SF-36 copy> <base> <SF-35 copy>
  exit 1 · 1 conflict · merged length 422 · ~419 with both blocks kept cleanly
  R11's SOURCE_LINE_CEILING = 400
```

⛔ **Each branch is individually LEGAL at 399 and 398. The merge is not.**
⚠️ **R11 is asserted per branch and NOTHING asserts it of the pair** — and
`FND-01` makes the result a build failure. ⭐ **`SF-36/2` is a recorded negative:
Developer 2 declined to split at 399/400 *"because the seam a split would use is
exactly the one Developer 1 is working across this round."*** ⛔ **That was
CORRECT in isolation and it is now the blocker — two locally-right decisions
composing into a defect, which is the class, not the incident.**

#### ⭐ THE RULING, in four parts

> ⛔ **1. `validate/source.py` has ONE owner and it is `SF-36`.** ⭐ The owner of
> a module is whoever its SHAPE is answerable to, and `SF-36` moves the shape:
> 110 lines against 43, a new sibling module extracted out of it, and a changed
> function signature. ⚠️ **`E01` was right and this board's cell was the copy
> that went stale.**
>
> ⛔ **2. `SF-35` holds a NAMED LICENCE, not ownership** — the rule-constant
> block and `check_unclassified`. ⭐ **Regions, not a file lock**, and they are
> regions `SF-36` does not touch, measured above. ⛔ **A licence is written into
> the epic beside the `Owns` cell; it is not an `Owns` cell.**
>
> ⛔ **3. The conflict is ONE anchor and it is resolved by KEEPING BOTH BLOCKS.**
> ⭐ Constants are ordered by rule id and NO precedence is claimed between them —
> `RULE_CONTESTED` and the two `origin-section-*` ids answer different questions.
> ⚠️ **The protocol is ORDER-INDEPENDENT and this board does not encode which
> branch lands first**: a landing order is a reading of a moment, and
> `PO-25/2` is what happens when one is written down.
>
> ⛔ **4. THE SECOND LANDER DOES NOT SPLIT THE MODULE.** ⭐ They take R11's own
> declared opt-out — a `Size exception:` line in the module docstring, ≥20
> characters of reason, matched by `ast` from the FIRST docstring — and the
> reason **names `W44` by id.** ⛔ **The opt-out is a DEFERRAL WITH AN ID, never
> a permanent exception**, and `W44` deletes it.

⭐ **Why part 4 rather than "split it now":** ⛔ **splitting a module across a
task boundary is exactly what `SF-36/2` correctly declined**, and asking the
second lander to do it would price a package split into a task whose budget was
set for a contract change. ⚠️ **R11's opt-out is not a loophole — `size.py`'s own
docstring says the ceiling is *"a signal, not a law — the opt-out exists and is
meant to be used, in the module, in the diff, in front of the reviewer."***
⛔ **It stops being legitimate the moment nobody owns its removal, which is why
the id is mandatory.**

#### ⛔ THE INSTRUMENT CHANGE — and it is the OPPOSITE of widening check 4

⚠️ **This is the THIRD consecutive round in which the board and an epic carried
different cells for one fact.** ⛔ **Round 25's answer was to WIDEN check 4's
population to *rows whose fact is also written somewhere else*; `CTO-31/5` then
added briefs to the somewhere-elses.** ⭐ **A population that grows every round is
a check losing a race.**

> ⛔ **RULED: an `Owns` cell is a DEFINITION field. The epic carries it; this
> board POINTS at it and does not copy it.** ⭐ **A brief is built from the
> EPIC** (`CTO-31/5`), never from a board row. ⛔ **Check 4 does not compare the
> two copies — it asserts that the second copy does not exist.**

⭐ **That is one `grep` instead of a widening population, and it makes the
class unreachable rather than detectable.** ⚠️ **APPLIED THIS ROUND to `SF-35`,
`SF-36`, `SK-02` and `W43`; ⛔ every other row's `Owns` becomes a pointer WHEN
THAT ROW IS NEXT TOUCHED** — a sweep is not owed and is not being deferred
silently: the rows below carry copies and are labelled as such.

⚠️ **`W` rows have NO epic definition — they are minted here and this board IS
their definition document, so their `Owns` cells are ORIGINALS, not copies,
and the rule does not bite them.** ⭐ **That asymmetry is why the rule is cheap.**

### ⛔ `W44` — MINTED. **`validate/source.py` becomes a package, and two correct decisions composed into a build failure**

⛔ **High-water mark moves `W43` → `W44`; measured across every branch in the
repository at `d77cb85` — `git grep -In '\bW44\b' $(git rev-list --all)` returns
NOTHING.** ⭐ **`W28` and up are minted by the PO only, and this is the mint.**

| | ⛔ **`W44`** |
|---|---|
| **What** | ⭐ **`src/studyforge/validate/source.py` becomes `validate/source/`**, and the second lander's `Size exception:` line is DELETED in the same commit |
| **From** | ⛔ **`CTO-31/6`'s ruling above, and `SF-36/2`'s recorded negative** |
| **Owner** | framework agent, **queued** — ⛔ **NOT dispatched by this row** |
| **Owns** | ⭐ **`src/studyforge/validate/source.py` → `src/studyforge/validate/source/`, and its test mirror `tests/studyforge/validate/test_source.py`** — ⚠️ **an ORIGINAL cell, verified at `d77cb85`: the file is **377** lines and the mirror is **364**; on `SF-36` they are **399** and **490** |
| ⛔ **When — and it is a hard gate** | ⭐ **AFTER both `SF-35` and `SF-36` have merged**, because the seam a split would use is the one they are working across (`SF-36/2`, and it was right) — ⛔ **and BEFORE `W41`, which adds a FOURTH rule id to the same module** |
| ⛔ **The seam is NOT invented here** | ⭐ **`SF-36` already extracted `validate/headings.py` (134 lines) OUT of this module and it still GREW, 377 → 399.** ⚠️ **That is the measurement that says the remaining content is genuinely two things, not one thing that needs tidying** |
| ⛔ **Ruling 75 — what it jumps** | ⭐ **`W37`, `W36`, `W38`, `W35`.** ⚠️ **The licence is a build failure that is already latent in two branches, and R11's opt-out is holding it back with an id that only this row retires** |

#### ⛔ `PO-26/1` — the finding underneath the mint, and it is a class

> ⛔ **A gate asserted per branch is not asserted of the merge.** ⭐ **R11 asked
> the right question of `SF-35` (398 ✓) and of `SF-36` (399 ✓) and NOTHING asked
> it of the 419.**

⚠️ **This is NOT an escaped defect and saying so matters:** ⛔ **the existing
review gate DOES catch it** — the second lander's trial merge is branch→tip, the
tip will already carry the first lander's 399, and `python3 -m tools.quality`
fails there. ⭐ **It is caught LATE: at the review of the developer who did
nothing wrong, after both tasks are built, attributable to neither.**

⛔ **So the remedy is not a new gate. It is SEQUENCING KNOWLEDGE AT WAVE-OPEN**,
and it is mine: ⭐ **when two rows in one wave share a file, the PO sums their
expected growth against R11's ceiling BEFORE they are dispatched in parallel.**
⚠️ **That step needs the `Owns` cells to be right, which is `CTO-31/6`'s whole
subject** — ⛔ **so the ruling above and this finding are one instrument, not
two.**

⭐ **Added to the wave checks as check 4's sibling, and it costs one `wc -l` per
shared file.** ⛔ **It is stated as a step and not as a hope, because
`PO-24/8` is the precedent: a row nobody measured is a row nobody ordered.**

### ⭐ ROUND 26 — the next two rows, and the two that had to be HELD

⛔ **Two developers are busy (`SF-35` uncommitted, `SF-36` with the CTO) and a
CTO round is running.** ⚠️ **A board row recording an assignment is NOT an agent
running (`PO-24/9`, `PO-25/2`): the rows below are PLACED, and the coordinator
dispatches.**

⛔ **THE MEASUREMENT THAT SET THE ORDER, and nothing on this board carried it:
FOUR of the queued rows collide with a LIVE branch.**

| Row | Its surface | ⛔ **Collides with a live branch?** |
|---|---|---|
| ⭐ **`SK-02`** | `src/studyforge/skills/adapter/` — ⛔ **`0` occurrences at `d77cb85`; it is a CREATE** | ⭐ **NO** |
| ⭐ **`W43`** | `docs/conventions/agent-protocol.md` | ⭐ **NO** — ⚠️ the only `docs/` file either branch touches is `docs/specs/…design.md`, on `SF-35` |
| ⛔ **`W40`** | `tests/test_gate_coverage.py` **and `tests/studyforge/corpus/container/test_document.py`** | ⛔ **YES — `SF-36` edits the second module**, and `W40` would convert it to a package |
| ⛔ **`W41`** | ⚠️ **`validate/source.py:191` and `validate/paths.py:180`** — measured, and the board's cell said only *"`validate/`"* | ⛔ **YES — BOTH branches edit `validate/source.py`**, and `W44` restructures it |
| ⛔ **`W44`** | `validate/source.py` | ⛔ **YES, by construction — it is gated behind both** |

⭐ **So the next two rows pick themselves, and that is the point of measuring
rather than ranking:**

| | ⭐ **Row** | ⛔ **Why it, and what it is NOT** |
|---|---|---|
| **NEXT 1** | ⭐ **`SK-02` — adapter authoring** | ⛔ **It is step 2.1's LAST task and closes the step.** ⚠️ **It is `pair`, and its first half is explicitly NOT splittable** — so the first developer to free takes it ALONE and writes `SKILL.md`'s procedure; the second joins at the named trigger. ⭐ **Spec §9: the skill precedes the artifact it produces, which is why it is in step 2.1 and not after it** |
| **NEXT 2** | ⭐ **`W43` — the two `agent-protocol.md` clauses** | ⛔ **Its gate is CLEARED: *"strictly after `W39` merges"*, and `16049d2` is an ancestor of `d77cb85`.** ⭐ **It is also moot** — `git diff --name-only ce58a36 16049d2` shows `agent-protocol.md` is NOT in `W39`'s diff, so the gate was about a claim. ⚠️ **Filler-sized, zero collision, and it is the instrument every other row is judged with** |

⛔ **`W43` MOVES FROM 7 TO 2 and it does not need Ruling 75's licence to do it**
— ⭐ **the four rows it passes are HELD, not outranked**, and a held row is not
jumped. ⚠️ **That distinction is new and it is worth keeping: `W40` and `W41`
were queued 5th and 6th on merit and are still 5th and 6th on merit;
they are unpickable this wave for a reason that has nothing to do with their
value.**

⭐ **`SK-02`'s `Owns`, VERIFIED AGAINST THE TREE at `d77cb85` and NOT against
another document** — ⚠️ **`E11`'s cell reads *"the adapter-authoring skill"*, a
prose label with no path, which is `CTO-31/6`'s defect in its other form: a cell
nobody can run a command against:**

```text
src/studyforge/skills/adapter/            0 files   ⭐ a CREATE
src/studyforge/skills/reconnaissance/    10 files   ⛔ SKILL.md + 8 modules + __init__
tests/studyforge/skills/reconnaissance/  10 files   ⛔ the mirror R12 requires
```

⛔ **So the cell is `src/studyforge/skills/adapter/` AND
`tests/studyforge/skills/adapter/`** — ⚠️ **the mirror is named because `W39/3`
is four hours old: an `Owns` that names no test module is what a brief is built
from.** ⭐ **`E11`'s cell is corrected to the paths this round.**

⚠️ **`SK-02`'s open question to PO-Integration is STILL OPEN and still due
BEFORE its review, not in it** — ⛔ *does `ISO/` already carry an adapter
package, and at which commits?* ⭐ **The task is startable either way.**

### ⛔ `SF-36/1` needs a home, and it is not `W44`'s

⛔ **`[local]`. Spec §4's worked example declares `container_api: 1` and
documents no region shape** — ⚠️ **outside `SF-36`'s `Owns`, correctly not taken,
and it arrived after `e4a2677` was complete.**

⭐ **RULED: the clause goes into `E01`'s `SF-36` Acceptance, where it should have
been** — ⛔ **`SF-35`'s definition already carries exactly this clause
(*"spec §4's `content` text and §R9's register row both carry `not_material` in
the same commit"*) and `SF-36`'s did not, which is the real defect.**
⚠️ **It is written with its own date and the CTO decides whether it binds
`e4a2677` or its successor** — ⛔ **I am not changing a bar mid-review by
stealth.** ⭐ **If the CTO merges as-is, it rides with `W44`, named here so it is
not lost.**

⛔ **The transferable half: a contract bump and its worked example land in ONE
commit, or the example teaches the old shape to the next reader.** ⭐ **That is
R9's register note generalised, and it now sits in `E01` twice rather than once.**

### ⛔ `CTO-31/1` and `CTO-31/3` — NEITHER had landed, and item 4's answer is *no*

⛔ **Measured: `grep -rn "CTO-31/" docs/` at `d77cb85` returns exactly ONE hit
outside the round-31 handoff — `CTO-31/6`, in `PO-2026-09-10-round25.md`'s
annotation.** ⭐ **So both were carried in a handoff and nowhere else, which is
this project's own standing rule failing on the round that quotes it: a ruling
recorded only in a handoff has not landed.**

| | ⛔ **What it says** | ⭐ **Landed here as** |
|---|---|---|
| `CTO-31/1` | ⛔ **M7 survived**: `test_a_stale_index_is_a_NOTICE_and_never_a_finding` asserts `== []` in a state the constant renders unreachable, because `stale_repository()` writes the index AT `BRIDGE_FLOOR`. ⭐ **Third instance of the class.** ⚠️ **`W37`'s population WIDENS** from *an expectation built from the constant* to *any assertion whose fixture is sized by the constant under test* | ⭐ **`W37`'s row**, plus the CTO's own one-row test carried by name |
| `CTO-31/3` | ⛔ **The growth governor's ratio is gameable by indenting prose into a fence.** ⚠️ The CTO's honest first draft measured `12.68%` and **failed the governor while being the better document** | ⭐ **`W34`'s row**, beside `CTO-28/1` |
| `CTO-31/2` | ⚠️ **`knowledge index: none — none in this checkout.`** stutters; cosmetic, exit 0, and `4b-ii` requires reviewers to QUOTE that line | ⛔ **RE-ROUTED: not `W43`.** ⭐ `W43` owns `agent-protocol.md` and this is a sentence in `tools/quality/knowledge_index.py` — ⚠️ **an `Owns` cell would have been wrong on arrival.** ⛔ **It rides with `W37`**, which is already going into that module's test mirror for `CTO-31/1` |
| `CTO-31/4` | ⭐ **Ruling 108 should say `host`, not `checkout`** | ⛔ **CTO's own, next round** — ⚠️ **annotated on this board's Ruling 108 row and in this round's base paragraph, because this board QUOTES that ruling** |
| `CTO-31/5` | ⚠️ **A brief is a place a stale board row becomes an instruction** | ⭐ **Answered by the `Owns`-is-a-pointer ruling above**: a brief is built from the epic |

⭐ **`CTO-31/1`'s one-row fix is NOT deferred to the whole sweep.** ⛔ **The CTO
wrote it, ran it against the unmutated tree (`1 passed`) and against M7
(`1 failed`)** — ⚠️ **so `W37` lands it as its FIRST commit, and the sweep
follows.** ⭐ **Exposure is `0`: the shipped behaviour is correct and the gap is
in the tests alone, which is why it is a finding with an owner rather than a
blocked merge** (Ruling 80's precedent, quoted by the CTO).

### ⛔ ROUND 26 — the six wave-open checks, and check 2 cannot be reproduced

⭐ **Run at `d77cb85`, linked worktree `wt/po26`, except where a row names
another checkout.**

| # | Check | ⛔ **Reading @ `d77cb85`** |
|---|---|---|
| **1** | index present and current | ✅ **PASS, and it is the first PASS this check has ever returned from a real reading.** ⭐ **MAIN checkout: `knowledge index: fresh — built at d77cb85f, and nothing it describes has moved since.` · `document pointers: 68 read in 130 markdown files, 26 carrying an anchor, 0 unresolved.` · `quality floor: clean`** — ⛔ **`W39` is why the line prints at all** |
| **2** | `[structural]` triage | ⛔ **FAILED AS AN INSTRUMENT — `PO-26/2` below.** ⭐ **My reading, with the instrument NAMED: `git grep -EIc '\`\[(local\|structural\|none)\]\`' -- docs` → **455 lines / 81 files** at `d77cb85`** — ⚠️ **and I cannot reproduce ANY previously quoted number with ANY candidate instrument** |
| **3** | C6 — every ruling reached its artifact | ✅ **2 of 2.** ⛔ **Population: rulings 109 and 110, the only ones minted since round 25.** ⭐ **109 → `review-rubric.md:647` (§4b), and its OWN pass condition holds at the tip: `grep -c 'ruff check --no-cache \.' review-rubric.md` → **1**. 110 → `review-rubric.md:461` (§2e).** ⚠️ **Both in the ruler's own commit, which is `PO-25/3`'s corrected rule getting an eleventh and twelfth data point** |
| **4** | re-measure every row whose trigger has passed | ⛔ **FIVE stale rows, and the instrument CHANGED — see the table below** |
| **5** | `CLAUDE.md`'s *Where to start* | ✅ **PASS — and my BRIEF said it FAILED.** ⛔ **`PO-26/3` below, and it is `CTO-31/5` arriving inside the round that was asked to check for it** |
| **6** | catalogue contributions | ✅ **NOTHING OWED.** ⭐ **`../ISO-8583-jPOS-tutorial` @ `6c8dc85`** — ⚠️ **the same ref the third, fourth and fifth runs measured, and `catalogue-contributions.md` last moved at `4351f28`, before any of them.** ⛔ **The catalogue stands at **19** entries.** ⚠️ **`../Claude-senior-java-engineer` @ `c9cf522` has NO `docs/studyforge/` directory at all, so it contributes nothing and cannot** |

#### ⛔ CHECK 4 — the rows, and the new sub-step that found two of them

| # | Row | ⛔ **What it said** | ⭐ **True at `d77cb85`** |
|---|---|---|---|
| 1 | head — `W39` | *"in flight … ZERO commits"* | ✅ **MERGED `16049d2`** — `--is-ancestor` → YES |
| 2 | head — the assignment | *"DEVELOPER 1 IS FREE and takes `SF-35`"* | ⛔ **BOTH developers busy; `SF-36` complete at `e4a2677`** |
| 3 | queue row 7 — `W43` | *"STRICTLY AFTER `W39` MERGES"* | ✅ **GATE CLEARED, and moot: `agent-protocol.md` is not in `W39`'s diff** |
| 4 | base paragraph | `3261 / 63 @ ce58a36` | ⛔ **`3289 / 63 @ d77cb85`** |
| 5 | Ruling 108's carried row | *"main checkout `∩ 5`, worktree `∩ 7`"* | ⛔ **DOES NOT REPRODUCE — `CTO-31/4`** |
| ⭐ **NEW** | `SF-35` **`Owns`** | `validate/source.py` included | ⛔ **CONTRADICTED `E01`. Ruled above; the cell is now a POINTER** |
| ⭐ **NEW** | `W40`, `W41` queue slots | *"queued 5th / 6th"* — no collision named | ⛔ **BOTH collide with a live branch.** ⚠️ **HELD, not re-ranked** |

⭐ **The two NEW rows are the sub-step this round adds** — ⛔ **compare a
dispatched row's surface against the LIVE DIFFS, not against another
document** — ⚠️ **and it is what `PO-26/1` generalises: a cell is only as good as
the command nobody ran against it.**

#### ⛔ `PO-26/2` — check 2 has been quoted for six rounds and its instrument was never recorded

**Measured:** `[structural]`, `[local]`, `[none]` — three candidate greps, three
refs, from the main checkout so the tree is the tracked one:

| instrument | @ `e5bcc85` | @ `d1270cd` | @ `d77cb85` |
|---|---|---|---|
| `` `[structural]` `` backticked | 153 / 40 | 261 / 72 | 287 / 81 |
| `[structural]` bare | 158 / 40 | 270 / 72 | 296 / 81 |
| ⭐ **all three markers, backticked** | 219 / 40 | 398 / 72 | **455 / 81** |
| ⛔ **what the board QUOTED** | ⛔ **131 / 32** | ⛔ **235 / 64** | — |

⛔ **NOTHING reproduces the quoted numbers**, and the file counts miss by exactly
**8** at both refs, in both directions of narrowing. ⭐ **So the gap is a
population, not a regex — some eight-document subtree was excluded and nobody
wrote down which.** ⚠️ **`[structural]` `PO-26/2`. Measured: the three commands
above, `d77cb85`, 2026-09-10.**

⭐ **This is `W42`'s own sentence arriving in a WAVE CHECK rather than in a
tool: *an uncounted set has no canonical count*.** ⛔ **A check whose reading
cannot be reproduced is a check that has been REPORTED for six rounds and RUN
for none of them** — ⚠️ **and it is the same shape as `CTO-29/8`: the number was
accurate and the SUBJECT was never pinned.**

⛔ **ROUTED TO `W42`**, which already owns *"the row must name its instrument, or
it will report a fourth number"* and already enumerates four instruments over
one set. ⭐ **This is the fifth, it is in a wave check rather than in
`tools/quality/`, and `W42`'s remedy — a check that reports its COVERAGE — is
exactly what makes check 2 reproducible.** ⚠️ **`W42`'s row gains the clause;
its queue slot does not move.**

#### ⛔ `PO-26/3` — my own brief carried a stale claim, and check 5 is why I caught it

⛔ **My brief said: *"[`CLAUDE.md`] currently says M1 step 1.4 / `SF-10` is in
flight — verify that against reality."*** ⭐ **VERIFIED. It does not.**

```text
CLAUDE.md:103   ⏳ Open: M2 — a corpus is readable. In flight: M2 step 2.1.
CLAUDE.md:125   ⚠️ CORRECTED 2026-09-10 (PO round 19, check 5). This section
CLAUDE.md:126   said "In flight: M1 step 1.4 — SF-10" directly above …
```

⛔ **Line 126 is the round-19 correction RECORD quoting the sentence it
replaced.** ⚠️ **A `grep` for `SF-10` in `CLAUDE.md` hits it, and the hit reads
exactly like a live claim.** ⭐ **`CLAUDE.md` is CURRENT and check 5 PASSES.**

⛔ **`[structural]` `PO-26/3`. Measured: `grep -n "SF-10\|step 1.4\|In flight"
CLAUDE.md` at `d77cb85`, 2026-09-10.** ⚠️ **This is `CTO-31/5` — *a brief is a
place a stale board row becomes an instruction* — arriving in the very round
that was asked to check for it, and reaching the PO rather than a developer.**

⭐ **And it sharpens `CTO-31/5` by one word:** ⛔ **the brief did not carry a
stale ROW. It carried a stale READING of a current document** — ⚠️ **and the
mechanism is the one `Ruling 106` predicted: a correction that quotes the text
it replaced is a document that answers `grep` twice, with the wrong half
indistinguishable from the right one.** ⛔ **The remedy is NOT to stop quoting —
a correction that does not quote cannot be audited.** ⭐ **It is that a `grep`
hit inside a block a document has marked `CORRECTED` or `~~struck~~` is not a
reading, and whoever quotes one owes the surrounding line.**

---

## ⛔ ROUND 25 — the stale rows, two mints, and the three checks

⭐ **Measured at `ce58a36`, branch `chore/po-round25`, linked worktree
`wt/po25`** — ⛔ **the ref AND the checkout, because Ruling 108 says a skip set
is a property of the checkout and this round quotes one.**

#### ⛔ Ruling 88 discharged the rubric half 43 minutes BEFORE this board said it was untaken

⛔ **THE ROW WAS INSTRUCTING A DEVELOPER TO DO WORK THAT DID NOT EXIST**, and it
was doing it inside the clause `W39` is editing right now.

⭐ **Measured by ANCESTRY, not by reading the board — the CTO's chain, reproduced
here at `ce58a36`:**

```text
b14ed5f  03:33  PO round 22   the SPLIT row: "the rubric half is the CTO's and I do not take it"
cc85ce1  03:49  CTO round 26  ⭐ Ruling 88 lands: "the floor and ruff are TWO checks"
f875158  04:32  PO round 24   ⛔ "QA-03/4's rubric half is still untaken"
git merge-base --is-ancestor cc85ce1 f875158   →  YES
```

⛔ **Three board sites are corrected this round and all three are struck in
place, never deleted:** the `QA-03` disposition table's `QA-03/4` row; `W39`'s
part 3, which is where the damage was; and the `fix/W39-index-step` reading in
the queue table. ⭐ **`W39` part 3 adds the index line and NOTHING ELSE.**

⛔ **AND THE COORDINATION ERROR BEHIND IT IS MINE, not a developer's, and it is
recorded rather than corrected quietly.** ⚠️ **`W39` was never dispatched. Its
worktree was created, two other agents were dispatched, and *"Developer 2 is on
`W39`"* was then reported in FOUR briefs from the worktree's existence alone.**
⛔ **Two review rounds deferred `QA-03/4` to avoid a conflict with an agent who
was not there, over a task that was already done.** ⭐ **Round 29 even observed
the branch had zero commits and inferred the other way, because a brief
outranked a measurement.**

⭐ **What should have caught it is this board's own instrument, and that is the
part worth keeping:** ⛔ **a row saying *"untaken"* is a CLAIM ABOUT ANOTHER
DOCUMENT, and nobody re-measured it for four rounds.** ⚠️ **The rubric was on
disk the whole time and answers in one `grep`.**

### ⭐ CHECK 3 — 10 OF 10, and it REFUTES the rule my predecessor drew from 9 of 16

⛔ **Population: rulings 99–108. Instrument: `git log -L <line>,<line>:<file>` on
the line that carries each ruling — the LANDING, not the handoff that claims it.**

| Ruling | Artifact | ⛔ **Landed in** |
|---|---|---|
| **99** | `E01`'s `SF-31` section **and** `E09` | ⭐ `2db881d` — the ruler's own commit |
| **100** | `module-structure.md` | ⭐ `2db881d` |
| **101** | `module-structure.md` | ⭐ `2db881d` |
| **102** | `E01`'s `SF-36` section | ⭐ `2db881d` |
| **103** | `review-rubric.md` §4a | ⭐ `2db881d` |
| **104** | `E04`'s window clause | ⭐ `2db881d` |
| **105** | `agent-protocol.md` §Findings are triaged | ⭐ `c61cae3` |
| **106** | `agent-protocol.md` §Handoff | ⭐ `c61cae3` |
| **107** | `agent-protocol.md` §A new check reports its coverage | ⭐ `c61cae3` — ⚠️ **clause landed; the ROW is minted here** |
| **108** | `review-rubric.md` §4b-i | ⭐ `19c0447` |

⛔ **`PO-24/1` said: *a ruling lands by itself EXACTLY when its artifact is the
ruler's own file.* ⚠️ REFUTED as stated.** ⭐ **Rulings 99, 102 and 104 landed in
`E01`, `E09` and `E04` — epic documents the PO owns, not the CTO — and all three
landed, in the ruler's own commit, at `2db881d`.**

⭐ **The corrected rule, and `PO-24/1`'s own control already contained it:**

> ⛔ **A ruling reaches its artifact exactly when the RULER WRITES THE CLAUSE.**
> ⚠️ **Whose file it is does not matter. Whether it was written or handed over
> does.** ⭐ **Ruling 95 was the control that showed this and the headline
> narrowed past it; rounds 28, 29 and 30 are ten more data points in the same
> direction.**

⛔ **The residue check 3 CANNOT see, and check 4 caught it:** ⭐ **Ruling 102
landed in `E01` and the SECOND document carrying the same fact — this board —
was never re-measured.** ⚠️ **Check 3 asks *did the ruling reach an artifact*. It
does not ask *did every artifact carrying that fact get updated*, and a
duplicated status is exactly where the answer differs.**

#### ⛔ Three `PO: mint` asks were outstanding, which is the column `PO-24/3` asked for

⭐ **`grep -rn "PO: mint" docs/` returns four sites and three distinct asks** —
`CTO-29/2` (with `CTO-29/4`), `CTO-29/3` and `CTO-29/8`. ⛔ **All three are
minted below as `W42` and `W43`.** ⭐ **The convention works: it cost one `grep`
where round 24 cost a twenty-minute audit.**

### ⛔ CHECK 4 — THE SEVENTH CLOSE RUN, and it found five stale rows nobody had named

⛔ **The CTO named THREE by line. Re-measuring every row whose trigger has
passed, FROM THE TREE, found EIGHT.**

| # | Row | ⛔ **What it said** | ⭐ **True at `ce58a36`** | Named by |
|---|---|---|---|---|
| 1 | `QA-03/4`'s disposition | *"the rubric half is the CTO's and I do not take it"* | ✅ **DISCHARGED, Ruling 88, `cc85ce1`** | CTO round 30 |
| 2 | `W39` part 3 | *"still untaken — do them together"* | ⛔ **DELETED — it was misdirecting an in-flight task** | CTO round 30 |
| 3 | `fix/W39-index-step` | *"zero commits — an assignment"* | ⚠️ **still zero, and DISPATCHED** | CTO round 30 |
| 4 | `SF-36` **Owns** | `corpus/manifest/` | ⛔ **`corpus/container/`** — `origin` is not in the manifest package at all | ⭐ **round 25** |
| 5 | `SF-36` open question | *"escalated; the PO's reading is `3`"* | ✅ **ANSWERED — `container_api: 2`, Ruling 102** | ⭐ **round 25** |
| 6 | `SF-36` collision pair | *"sequenced, never parallel"* | ⛔ **DISSOLVED — `Depends on SF-35` dropped** | ⭐ **round 25** |
| 7 | R21 register | *"one new one is already in flight"* | ✅ **ANSWERED by Ruling 102** | ⭐ **round 25** |
| 8 | step 2.1 assignment | `SF-31` *"in-review @ `171a18a`"*, `SF-04` next | ✅ **BOTH MERGED** — `f3ee177`, `0899f0f` | ⭐ **round 25** |

⭐ **Rows 4–7 are ONE ruling.** ⛔ **Ruling 102 landed on 2026-09-10 at `2db881d`
and this board carried its refuted premise for two rounds** — ⚠️ **including an
`Owns` cell that would have sent a developer with a 25k budget into
`corpus/manifest/`, which is `PO-21/5`'s family: a cell nobody ran a command
against.**

⛔ **The instrument change this run earns, and it is one line in the wave
checks:** ⭐ **check 4's population is not *rows with a trigger*. It is *rows
whose fact is ALSO written somewhere else*.** ⚠️ **Every one of rows 4–7 had its
trigger fire in a document that is not this one, so a check scanning only this
board's own triggers could not see any of them.**

### ⭐ CHECK 6 — FIFTH RUN, and the SK-08 findings have been sitting in the open for a day

⛔ **Measured on `../ISO-8583-jPOS-tutorial` @ `6c8dc85` — ⚠️ the SAME ref the
third run measured, so the repository has not moved.** ⭐ **`catalogue-contributions.md`
is unchanged; the catalogue stands at **19 entries** and no new contribution is
owed.** ⛔ **Nothing to adopt, and that is the check working rather than the check
idling.**

⚠️ **But the sweep found something the catalogue is the wrong home for, and this
board had no row for it either.**

⛔ **`docs/studyforge/finding-sk08-delivery-planning.md` — 263 lines, committed
`eb6f2d2` on 2026-09-09 — carries SIX findings against `SK-08`, and this board
has never dispositioned one of them.** ⭐ **The channel section already says these
are *"this track's most valuable output before M2, because they arrive while
`SK-08` can still be shaped by them"*** — ⚠️ **and then nothing carried them, for
a day, which is `PO-24/3`'s shape exactly: an ask with no destination.**

| Finding | ⛔ **What it says `SK-08` cannot do** |
|---|---|
| **SK08-A** | a corpus milestone is gated on a FRAMEWORK milestone and nothing says so |
| **SK08-B** | the capability→milestone map was derived by reading thirteen epic documents |
| **SK08-C** | nothing asks the planner where the corpus FINISHES |
| **SK08-D** | `SK-08`'s task template assumes the integrator WRITES things |
| **SK08-E** | ⭐ **the question mechanism — named there as the highest-value item, and no skill defines it** |
| **SK08-F** | `SK-08` asks for concentration risk and cannot express where this one sits |

⛔ **DISPOSITION: all six are INPUTS TO `SK-08`'s DEFINITION, not new tasks and
not catalogue entries.** ⭐ **They are carried into `E11`'s `SK-08` section by id
and by claim** — ⚠️ **by CLAIM and not by path, because a task in this repository
may not depend on a file in a moving repository (R20's reason, applied in the
direction it is usually not).** ⛔ **`SK-08` is M2 step 2.2 and unstarted, so this
lands while the skill can still be shaped — which is the entire argument the
channel section makes and had not acted on.**

### ⛔ `W42` — MINTED. **The marker check judges 41 of 88 documents and reports `0` for all 88**

⛔ **The `W` high-water mark moves `W41` → `W42`.** ⭐ **From Ruling 107 (CTO
round 29), carrying `CTO-29/2` and `CTO-29/4`.**

| | ⛔ **`W42`** |
|---|---|
| **What** | ⭐ **`check_markers` runs only on `Kind: task handoff` and reports `0` for every document it did not read.** ⛔ **`agent-protocol.md`'s own clause — *a new check reports its coverage, not just its hits* — is violated by the check that section governs** |
| **From** | ⛔ **Ruling 107, with `CTO-29/4`** (`FINDING_MARKERS` is unguarded: a fourth marker was added and `tools/tests/quality/` still returned `281 passed, 1 skipped`) |
| **Owner** | framework agent, **queued** — ⭐ **`tools/quality/handoffs/` is FREE surface** |
| **Owns** | `tools/quality/handoffs/`, and its test mirror |
| ⛔ **Two parts** | ⭐ **(a) the check REPORTS its coverage** — how many documents it read, of how many, by kind. ⭐ **(b) a test PINS the marker vocabulary**, so Ruling 105's closed set is closed by something other than convention |
| ⛔ **THE HARD PART, named so the row is not scoped blind** | ⭐ **A ruling record whose SUBJECT is the marker vocabulary must be able to SPELL the markers.** ⚠️ **Ruling 73's table shows three of the four mention-shapes are already safe; the fourth — a line OPENING with a marker — is exactly the shape such a document needs.** ⛔ **The remedy is an exemption the document DECLARES, the way `**Kind:**` is declared. NOT a weaker reader** |
| ⛔ **AND THE PART THIS ROUND ADDS** | ⭐ **THE ROW MUST NAME ITS INSTRUMENT, or it will report a fourth number.** ⚠️ **Measured at `ce58a36` in `wt/po25`, four instruments over the same set: 189 (lines containing a registered marker) · **197** (occurrences of `` `[local]` ``/`` `[structural]` ``/`` `[none]` ``, `_MARKERS_ON_LINE`'s own regex) · 202 (the CTO's, at `6850c3c`) · 211 (any `` `[word]` ``).** ⛔ **An uncounted set has no canonical count** |
| **When** | ⛔ **Queued at 8, and the CTO's own call is *mint it WITH the wave, not before it*** — ⭐ nothing is blocked, the gap is coverage rather than correctness, and blocking a wave-open on a linear cost is the trade this board refused for `W34` |

⭐ **Coverage RE-MEASURED here rather than inherited, and per Ruling 81 the
members are printed rather than the count:**

```text
at 6e80c82 (CTO round 29)   84 documents · 40 judged · 44 unjudged
at 6850c3c (CTO round 30)   86 documents · 40 judged · 46 unjudged
at ce58a36 (this round)     88 documents · 41 judged · 47 unjudged
  by kind: ruling record 40 · task handoff 41 · session log 3 · survey 3 · index 1
  markers in the unjudged set: 197 occurrences across 29 documents
  largest single carrier: CTO-2026-09-09-round17.md, 43
```

⛔ **Every CTO and PO round files its findings in a `ruling record`, which is the
one kind the check skips** — ⭐ **so the unread set grows by construction, about
two documents and ten markers a round, and the growth is in exactly the documents
that ROUTE work.**

### ⛔ `W43` — MINTED. **Two clauses `agent-protocol.md` is owed, and both are about the instrument**

⛔ **High-water mark moves `W42` → `W43`.** ⭐ **From `CTO-29/3` and `CTO-29/8`,
both of which end in `PO: mint`.**

| | ⛔ **`W43`** |
|---|---|
| **Part 1 — `CTO-29/3`** | ⭐ **An acceptance condition NAMES THE INSTRUMENT THAT WOULD FAIL IT.** ⛔ **The claim is *a condition nobody can fail is not an acceptance condition*** — Ruling 91's clause reached an implementation without reaching the acceptance document, so the review had no way to test it and would have had to trust the same handoff. ⚠️ **`W33` catalogued seven instances of *a check that cannot fail*; this is the EIGHTH and the first in the ACCEPTANCE instrument** |
| **Part 2 — `CTO-29/8`** | ⭐ **A reading taken from a PROXY, quoted as a property of the THING.** ⛔ **A branch is a proxy for a tip; a disk walk is a proxy for a tree; a constant is a proxy for a check.** ⚠️ **In every instance the reading was ACCURATE and the SUBJECT was wrong, which is why none of them looks like an error.** ⭐ **The check is two questions: what did I MEASURE, and what am I about to CALL it?** ⛔ **It is Ruling 55 generalised past numbers, and it belongs beside Ruling 106** |
| **Owner** | framework agent, **queued at 7** |
| **Owns** | `docs/conventions/agent-protocol.md` — ⛔ **two clauses, neither of them Ruling 89** |
| ⛔ **When — and this is load-bearing** | ⭐ **STRICTLY AFTER `W39` MERGES.** ⚠️ **`W39` holds a clause in this file (it NARROWS Ruling 89), and its claim is CLAUSE-SCOPED rather than a file lock** — ⛔ **but two rows editing one document inside one wave is precisely what `QA-03/4` cost this board, and that lesson is four hours old** |
| ⛔ **Why they are ONE row and not two** | ⭐ **Same file, same section, one clause each, and both are about the instrument every other row is judged with.** ⚠️ **A second row would collide with `W39` twice instead of once** |
| ⛔ **Ruling 75 — what it jumps** | ⭐ **`W37`, `W36`, `W38`, `W35`.** ⚠️ **The licence is a MEASURED rate: `CTO-29/8`'s form has FIVE instances in three rounds — the worktree that stood for an agent, the branch that stood for a tip, the disk walk that stood for a tree, the constant that stood for a check, and the board row that stood for the rubric** — ⛔ **and the fifth is what this round opened by cleaning up** |

⚠️ **`CTO-29/3` was offered to me as *"PO: mint, OR RULE IT"*, and I am minting
rather than ruling.** ⛔ **A rule stated in a board section is a rule nobody
executes from; the acceptance instrument lives in `agent-protocol.md` and a
clause there is what a reviewer actually reads.** ⭐ **That is C6's own
preference order arriving in a choice I was explicitly given.**

### ⭐ Rulings 105, 106 and 108 — carried, and none of them needs a row

| Ruling | ⛔ **What it binds here** |
|---|---|
| **105** | ⛔ **The marker vocabulary is CLOSED at three.** ⭐ **A recorded negative IS a finding: write `` `[local]` `` and open the text with `A NEGATIVE result.`** ⚠️ **`[negative]` is not a marker, and the reason is not Ruling 65's** — ⛔ **a marker encodes ROUTING, a negative's routing is identical to `[local]`'s (nowhere), so the fourth word carries zero routing and one new failure mode.** ⭐ **The existing uses are NOT re-marked: they live in records, and Ruling 106 says a record is annotated, never edited** |
| **106** | ⛔ **A record is ANNOTATED, never edited** — ⚠️ **and the elegant half is the one to actually use: `Release tip:` names a MOVING POINTER, so the field ages by construction; `Measured at:` names a REF and cannot age.** ⭐ **ADOPTED for this board's own round headers, starting with round 25's above** |
| **108** | ⛔ **CORRECTED BY `CTO-31/4`, round 31 — read `HOST`, not `CHECKOUT`.** ⚠️ ~~Same commit, same image, at `6850c3c`: main checkout `host 10 · ∩ 5`; linked worktree `host 13 · ∩ 7`~~ — ⛔ **that row DOES NOT REPRODUCE**: re-measured twice at `c1a5a79`, both checkouts return **28** unique `file:line` skip rows and the sets are IDENTICAL, because `docker/dev/compose.yaml` mounts `../..` and nothing else so no sibling is visible from either. ⭐ **The divergence is real on the HOST only.** ⚠️ **A skip set is a property of the CHECKOUT on the host and of nothing inside the image** — ⭐ **the difference is `test_knowledge_index.py`, whose subject is the sibling checkouts, which `git worktree add` does not carry.** ⛔ **EVERY reviewer measures in a trial worktree, which is the checkout that returns the OTHER number** — ⭐ **so this board's base paragraph now names its checkout, not only its ref** |

⛔ **`SF-04/2` and `CTO-30/1` are RIDERS, not rows, and they are recorded here so
they are not re-raised:** ⭐ **`SF-04/2` (`version._said` has a second
implementation in `cache._said`) is ruled into `E01`'s `SF-33` section and rides
with whoever next mints a `CONTRACT_FIELDS` member — realistically E03's TOC
schema version, which `W11` already names.** ⭐ **`CTO-30/1` (`freshness.py`
promises the caller three unverifiable causes and there are FOUR; the fourth does
not name itself) rides with the next task touching `corpus/discovery/`.**

### ⛔ THE CLOSE RE-TAKE — `PO-24/9` gets its SIXTH instance, and it is the same round that filed `PO-25/2`

⛔ **The branch reading aged out INSIDE this round, for the second consecutive
round, and this time it aged out in the direction that PROVES the finding written
four paragraphs above it.**

| Reading | ⛔ **At round 25's OPEN, `ce58a36`** | ⛔ **At its CLOSE, re-taken** |
|---|---|---|
| `git branch --no-merged release/m0-foundations` | ⭐ **nothing** | ⛔ **`fix/W39-index-step`** |
| `fix/W39-index-step` | ⚠️ **`ce58a36`, ZERO commits** | ⛔ **`1c7bc79`, TWO commits, 8 files, +975 −118** |
| ⛔ **Is anything waiting on somebody else?** | ⭐ **no** | ⛔ **YES — `W39` awaits a REVIEWER'S verdict** |
| Live worktrees | ⭐ **3** | ⛔ **6 — a CTO round 31 is running, with a trial merge at `419bc3f`** |

⭐ **`W39` shipped what its row said it would**, measured from the diff rather
than from the handoff: `delivery-flow.md` (the interim step, deleted),
`review-rubric.md` (the index line), `tools/knowledge/index.py` and
`tools/quality/knowledge_index.py` (the scoping and the notice), and three test
mirrors. ⛔ **`agent-protocol.md` is NOT in the diff** — ⚠️ **so `W43`'s
after-`W39` gate is about a claim rather than a collision, and it stands as
written until `W39` merges.**

⛔ **`PO-25/2`, confirmed at the close of the round that filed it.** ⭐ **At the
open the branch had zero commits and the developer WAS dispatched; at the close
it had two.** ⚠️ **The same instrument returned *assignment* and *in flight* for
the same branch four hours apart, and neither reading told anybody which state it
was in** — ⛔ **which is why the remedy is that dispatch is RECORDED, not
inferred.**

### ⛔ THE LINT LINE (Ruling 79) — `chore/po-round25`

⛔ **Pinned green — `ruff 0.16.6` in the dev image (`docker/dev/check`), taken in
the LINKED WORKTREE `wt/po25` (Ruling 108):**

```text
BASE   release/m0-foundations @ ce58a36
  pytest                3261 passed, 63 skipped   (container's set, all 63 named above)
  check --no-cache      All checks passed!        exit 0
  format --check        455 files                 exit 0   (tracked, tree-derived)
  floor                 clean                     exit 0

BRANCH chore/po-round25 (docs-only)
  pytest                3261 passed, 63 skipped   (unchanged — no code)
  check --no-cache      All checks passed!        exit 0
  format --check        456 files                 exit 0   (tracked, tree-derived)
  floor                 clean                     exit 0
  pointers              67 read in 126 .md / 0 unresolved
  index                 NONE in this checkout     (linked worktree — CTO-27/6)

DELTA  +1 .md (this round's handoff). No test, no .py, no rubric line moved.
```

⭐ **Denominator DERIVED per Ruling 86a, `git ls-files` with ruff's own
`--force-exclude` rather than a hand-typed exclusion (`CTO-29/6`):** **337 `.py`
+ 127 `.md` − 8 under `tests/fixtures/` = 456**, and ⛔ **`ruff` printed exactly
456.** ⚠️ **This worktree carries ZERO untracked files, so the disk walk and the
tree derivation coincide — ⛔ they were still computed separately rather than
allowed to cancel** (`PO-24/5`).

⚠️ **The floor needed a SECOND PASS, and it was `PO-24/7`'s class again:** ⛔ **two
anchors broke because I RENAMED the headings they pointed at** — `W28–W41` →
`W28–W43`, and *"RE-CUT at round 24"* → *"round 25"*. ⭐ **Both were correct when
written and both were broken from the other end.** ⛔ **The floor caught both; the
four NEW anchors this round were asked of `pointers.slug()` before being typed and
none of them broke.** ⭐ **The rule stands and gains a word: renaming a heading is
a TWO-SITE edit, and the second site is not always in another file.**

## ⛔ CHECK 4 — THE FIFTH CLOSE RUN, and `PO-20/3` gets its fifth data point

⭐ **Run at `2fe56a4`, which is M1's close ref and M2's open ref — the first time
one run has served as both.** ⛔ **Instrument, the cheap one the ruling promised:
`git branch --no-merged release/m0-foundations` plus one
`git merge-base --is-ancestor` per row whose trigger had passed.**

### ⛔ `PO-20/3` — FIFTH DATA POINT, and it CONFIRMS the rule the fourth contradicted

⭐ **The rule, as promoted at round 20: *check 4's close run drifts when the
review queue is not empty, and does not when it is*.**

| Run | Queue at start | Did the run drift? |
|---|---|---|
| 2nd (round 20) | ⭐ **empty** | ⭐ **no** |
| 3rd (round 21) | ⭐ **empty** | ⭐ **no** |
| 4th (round 22) | ⛔ **NOT empty** | ⛔ **YES — three places.** The first NEGATIVE point |
| ⭐ **5th (round 23)** | ⛔ **NOT empty — ONE branch, `chore/po-round22`** | ⭐ **NO** |

⛔ **So the fifth point does NOT confirm the rule. It BREAKS it, and the break is
more useful than a fourth confirmation would have been.** ⚠️ **A non-empty queue
did not produce drift this time** — ⭐ **and the difference between run 4 and run 5
is not the queue's SIZE but who was holding it: at round 22 the queue held
branches awaiting a REVIEWER'S VERDICT, and a verdict can land mid-run. This
round it held one branch awaiting a MERGE, by me, and I merged it myself as my
first act.**

⭐ **`PO-23/2` — the rule, restated at its real width:** ⛔ **the close run drifts
when something in the queue can change WITHOUT THE RUNNER DOING IT.** ⚠️ **"Queue
empty" was a proxy for that and it is a leaky one — it is right in four cases out
of five and wrong in the fifth, which is exactly how a proxy behaves.** ⭐ **The
scheduling rule for check 4 is therefore not *"run it when the queue is empty"*
but ⛔ ***"run it when nothing in the queue is waiting on somebody else"*** — a
condition the runner can actually establish, rather than one they can only hope
holds for the duration.

### ⛔ THE READING THAT CHANGED THE PLAN — **the pre-authorisation was on an unmerged branch**

⛔ **`PO-23/1`. `git branch --no-merged release/m0-foundations` @ `2fe56a4`
returned exactly one branch: `chore/po-round22`** — ⭐ **my predecessor's, carrying
382 lines of board, `W36`–`W38`, and the M1 close pre-authorisation this round
exists to execute.**

⚠️ **The CTO's round-25 close ran the same check and recorded *"check B —
`git branch --no-merged` — empty: everything landed."*** ⛔ **That was true when
taken and false by the time this round opened**, which is the third consecutive
round in which a branch-versus-tip reading has aged out inside a single round
(`PO-22/4`, `PO-23/4`, and this).

⭐ **What it would have cost to skip the check:** ⛔ **this round's board edits were
about to be written against a `BOARD.md` that did not contain them, and the merge
that reconciled the two would have taken whichever side git preferred.**
⚠️ **Nothing would have looked wrong.** ⭐ **The predecessor's branch was merged
into `chore/po-round23` as this round's FIRST commit, before a single edit.**

### The six at open, run at `2fe56a4`

| # | Check | ⛔ **Reading @ `2fe56a4`** |
|---|---|---|
| **1** | index present and current | ⚠️ **`none in this checkout` — NOT a failure, and it is `W39`'s whole subject.** ⛔ **A worktree never has one, `graphify-out/` being git-ignored, which is precisely why the tip's redness is invisible from here** |
| **2** | `[structural]` triage | ⭐ **224 marker lines across 61 files** — ⚠️ **up from 131 across 32 at round 19: the sweep's surface has nearly doubled in four rounds** |
| **3** | C6 — every ruling reached its artifact | ⛔ **NOT RUN THIS ROUND, and I am naming the omission rather than leaving a blank cell.** ⭐ **Rulings 84–87 and 86a landed on `chore/cto-round25` and are carried on the tip; the audit that would confirm each reached its artifact is `W34`'s surface, and `W34` is queued this round for the first time** |
| **4** | re-measure every row whose trigger has passed | ⛔ **FOUR rows wrong, all in one direction** — `W30`, `W31`, `W33` `todo`/`awaiting release` for work that had landed, and `W36` `blocked` on a gate that had cleared. ⭐ **Corrected in [the `W` table](#w28w58-the-live-w-rows-and-this-is-a-pointer)** |
| **5** | `CLAUDE.md`'s *Where to start* | ⛔ **FAILED at open — it named M1 step 1.5 as in flight while M1 was closing.** ✅ **FIXED BY REPLACEMENT, not by appending**, which is check 5's own founding rule |
| **6** | catalogue contributions | ⛔ **NOT RUN — the sibling checkouts are not present in this worktree.** ⚠️ **Owed at this wave's close, and named so it is not read as clean** |

### ⛔ THE LINT LINE (Ruling 79), and it produced a finding about its own denominator

⛔ **`chore/po-round23`, pinned container, `docker/dev/check`, `ruff 0.16.6`:**

```
ruff check .            All checks passed!            exit 0
ruff format --check .   422 files already formatted   exit 0
quality floor           clean                         exit 0
```

⭐ **Quality floor: `clean`, exit 0** — ⚠️ **and it did NOT start clean.** ⛔ **The
first run returned `5 findings`, every one a dead `[anchor]` in `BOARD.md`, every
one hand-typed by me.** ⭐ **My predecessor's warning, one round old, was that a
hand-typed slug is not what `pointers.slug()` produces — so I asked the checker
for the four real slugs instead of guessing again**, and the differences were
invisible by eye: a double hyphen where the em-dash had been, and `test_gate_coverage.py`
slugging to `testgatecoveragepy` rather than `test_gate_coveragepy`.

#### ⭐ `PO-23/5` — **Ruling 86a's denominator has TWO sources of divergence, not one, and `CTO-25/10` found only the first**

⛔ **`CTO-25/10` measured the floor's notice at **421** against a tracked walk of
**420** and diagnosed the difference as one untracked `ONBOARDING.md` — *the
notice quotes the disk denominator*.** ⚠️ **Measured here, that diagnosis is
incomplete:**

| | ⛔ **Count @ `2fe56a4`** | |
|---|---|---|
| ⭐ **Untracked files in this worktree** | **0** | ⛔ **so disk and tree are the SAME set here** |
| `git ls-files '*.py' '*.md'` — the tracked denominator Ruling 86a asks for | **429** | ⭐ **exit 0, all formatted, run explicitly through `xargs`** |
| `ruff format --check .` — what the notice quotes | **421** | ⛔ **EIGHT FEWER, in a checkout with nothing untracked** |
| ⭐ **The reconciliation, exact** | **429 − 8 = 421** | ⛔ **`pyproject.toml:86`, `extend-exclude = ["tests/fixtures"]`, and `git ls-files 'tests/fixtures/**' \| grep -E '\.(py\|md)$'` returns exactly 8** |

⛔ **So the number is neither the disk nor the tree: it is `ruff`'s CONFIGURED
WALK, and it diverges from the tracked set in two independent directions at
once** — ⭐ **plus one for anything untracked, minus one for anything excluded.**
⚠️ **In the user's own checkout those two were +1 and −0; here they are +0 and −8.
A checkout with one untracked file and one excluded file would show ZERO
divergence and the defect would be invisible.**

⭐ **This sharpens the routing rather than changing it.** ⛔ **`CTO-25/10` proposed
the notice *"either label its number `disk` or derive it from the tree"*.**
⚠️ **Labelling it `disk` is now known to be WRONG — it is not the disk either.**
⭐ **Deriving it from the tree remains right, and the row that does it must
subtract the configured exclusions or it will report 429 for a run that checked
421.** ⛔ **Routed to `W38`, which already owns `pyproject.toml`'s lint
configuration and the floor/`ruff` divergence, rather than to `W34`'s wave.**

---

## ⛔ CHECK 4 — THE SIXTH CLOSE RUN, and **`PO-23/2` gets its sixth data point**

⭐ **Run at `d1270cd`, the release tip.** ⛔ **Instrument, unchanged and cheap:
`git branch --no-merged release/m0-foundations`, one
`git log release/m0-foundations..<branch>` per named in-flight branch, and
`git diff --stat` across the window since the last run's ref.**

### ⭐ `PO-23/2` — SIXTH DATA POINT, and the re-widened rule HOLDS

⭐ **The rule, as re-widened at round 23: *the close run drifts when something in
the queue can change WITHOUT THE RUNNER DOING IT*.**

| Run | Could anything change without the runner? | Did the run drift? |
|---|---|---|
| 2nd (round 20) | ⭐ **no** — queue empty | ⭐ **no** |
| 3rd (round 21) | ⭐ **no** — queue empty | ⭐ **no** |
| 4th (round 22) | ⛔ **YES** — branches awaiting a REVIEWER'S verdict | ⛔ **YES — three places** |
| 5th (round 23) | ⭐ **no** — one branch awaiting the runner's OWN merge | ⭐ **no** |
| ⛔ **6th (round 24)** | ⛔ **YES, discovered at the CLOSE** — ⭐ at the open `--no-merged` returned nothing and both named branches carried zero commits; ⛔ **by the close `feat/SF-31-plan` carried a commit and awaited a verdict** | ⛔ **YES — one place, and it is [the queue reading](#the-queue-behind-step-21)** |

⛔ **SIX POINTS, AND THE SIXTH CONFIRMS THE RULE BY DRIFTING.** ⭐ **At the run's
open the answer to *"can anything change without the runner?"* was NO — two
assigned branches, zero commits between them.** ⚠️ **It became YES during the
round, without the runner doing anything, and the run drifted in exactly the row
that reading fed.**

⭐ **That is the rule working rather than failing, and the distinction matters:**
⛔ **the rule does not predict that a run will not drift; it predicts that a run
drifts WHEN something in the queue can change without the runner.** ⚠️ **The
condition was false at the open and true at the close, and the drift arrived with
it.**

⛔ **What the sixth point ADDS, and it is the thing five rounds of this finding
had not produced:** ⭐ **the condition is not a property of the queue at a moment
— it is a property of the WINDOW.** ⚠️ **A runner can establish *"nothing is
waiting on somebody else"* at the instant they look, and cannot establish it for
the duration of a round in which two developers are working.** ⛔ **So the
scheduling rule gains its missing half: re-take the reading at the CLOSE, not
only at the open** — ⭐ **which is what caught this, ninety minutes after the
first reading and one commit after the finding that says to do it.**

### The six at open, run at `d1270cd`

| # | Check | ⛔ **Reading @ `d1270cd`** |
|---|---|---|
| **1** | index present and current | ⚠️ **`none in this checkout` — NOT a failure.** ⛔ **`graphify-out/` is absent from this linked worktree**, `git worktree add` not carrying git-ignored directories — ⭐ **which independently reproduces `CTO-27/6` and is evidence for `W39` part 2** |
| **2** | `[structural]` triage | ⭐ **235 marker lines across 64 files** — ⚠️ **224/61 at round 23, so +11 lines and +3 files in one round.** ⛔ **131/32 at round 19: the surface has nearly doubled in five rounds and `W37` is still queued 6th** |
| **3** | C6 — every ruling reached its artifact | ⛔ **RUN, and it FAILED SEVEN WAYS.** ⭐ **[The table is below](#check-3-run-for-the-first-time-in-three-rounds-and-seven-of-sixteen-rulings-had-reached-no-artifact)** |
| **4** | re-measure every row whose trigger has passed | ⭐ **ZERO rows moved, and the instrument says why:** `git log 2fe56a4..d1270cd` is **eight commits, every one docs**, and `git diff --stat` touches no `src/`, `tools/` or `tests/` path. ⛔ **So every `W` row's status at `2fe56a4` is still true at `d1270cd`** — ⚠️ **and the table's cells are re-stamped rather than inherited, because a status quoted at the wrong ref is this board's catalogued defect** |
| **5** | `CLAUDE.md`'s *Where to start* | ⭐ **PASSED at open** — it named M2 step 2.1 correctly. ⛔ **UPDATED anyway**: step 2.1 gained `SF-35` and `SF-36` this round, so the file was edited **in the same commit as the board**, which is the point of check 5 |
| **6** | catalogue contributions | ⭐ **RUN — third run, and the OWED reading from round 23 is discharged.** ⛔ **[Below](#check-6-third-run-both-deferrals-triggers-have-fired-and-one-left-a-constraint-behind)** |

### ⛔ Check 3 — RUN for the first time in three rounds, and **seven of sixteen rulings had reached no artifact**

⛔ **Instrument, and it is the one the check's own definition names: for each
ruling, open the artifact it names and read the clause.** ⭐ **Mechanically:
`grep -rn "Ruling NN" docs/ src/ tools/ tests/`, excluding the handoff that made
it — because a ruling citing itself in its own handoff is the thing being tested
for.**

| Ruling | The artifact it names | ⛔ **Measured @ `d1270cd`** |
|---|---|---|
| **84** | `review-rubric.md` | ⭐ **LANDED** — line 1730 |
| **85** | `review-rubric.md` | ⭐ **LANDED** — line 348 |
| **86** | `review-rubric.md` | ⭐ **LANDED** — line 826 |
| **86a** | `review-rubric.md` | ⭐ **LANDED** — line 848 |
| **87** | `review-rubric.md` | ⭐ **LANDED** — line 727 |
| **88** | `review-rubric.md` | ⭐ **LANDED** — line 889 |
| **89** | `review-rubric.md` | ⭐ **LANDED** — line 1778 |
| ⛔ **90** | *"a framework task"* — no id | ⛔ **NOTHING.** ⭐ **Carried this round as `SF-35`** |
| ⛔ **91** | ***an acceptance condition on `SF-31`*** | ⛔ **NOTHING** — ⚠️ **and `SF-31` IS IN FLIGHT.** ⭐ **Carried this round into `E01`'s `SF-31` section** |
| ⛔ **92** | *"framework task, with tests"* — no id | ⛔ **NOTHING.** ⭐ **Carried this round as `SF-36`** |
| ⛔ **93** | *"E04 one condition, the block vocabulary one sentence"* | ⛔ **NOTHING.** ⭐ **Carried this round into `E04`'s `SF-16` section; the spec sentence rides with that task** |
| ⛔ **94** | *"small, cheap, framework task with tests"* — no id | ⛔ **NOTHING.** ⭐ **Carried this round as `W41`** |
| **95** | spec §R9 register **and** `E01`'s `SF-04` | ⭐ **LANDED, both, in the ruling's own commit** |
| ⛔ **96** | `W39`'s row, and three modules | ⚠️ **PARTIAL — the row did not name the mechanism.** ⭐ **Carried this round** |
| ⛔ **97** | the close standard | ⛔ **NOTHING — no artifact at all.** ⭐ **Carried this round into [the wave-checks section](#the-wave-checks-six-at-open-and-check-4-again-at-close)** |
| ⛔ **98** | `F18`'s task | ⛔ **NOTHING.** ⭐ **Carried this round as `SF-35`** |

⛔ **Seven of sixteen, and FIVE of the seven are round 26's.** ⚠️ **The five that
landed cleanly are 84–89 — every one of them lands in `review-rubric.md`, which
is the CTO's own document.** ⭐ **Every ruling that reached its artifact reached a
document its author owns; every ruling that did not needed somebody ELSE to act.**

⛔ **That is the general form, and it is sharper than *"C6 is owed"*:** ⭐ **a
ruling lands by itself exactly when its artifact is the ruler's own file.**
⚠️ **The moment a ruling's carrier is a task id, a board row, or another agent's
epic, it needs a HANDOFF to a second party — and the handoff is a
broadcast, which `CTO-27/3` has already measured as having a half-life shorter
than a round.**

⭐ **The cheap remedy, and it is check 3 itself run every wave rather than every
third wave:** ⛔ **check 3 was skipped at rounds 22 and 23. Five rulings
accumulated in one of those gaps.** ⚠️ **It cost twenty minutes to run and it is
the only instrument that found them** — ⛔ **`F18` was found by a coordinator by
luck, and luck found one of five.**

### ⭐ CHECK 6 — THIRD RUN: **both deferrals' triggers have fired, and one left a constraint behind**

⛔ **Measured on `../ISO-8583-jPOS-tutorial` @ `6c8dc85` against
[`../integration-catalogue.md`](../integration-catalogue.md) @ `d1270cd`.**
⚠️ **Round 23 named this check OWED rather than clean, because a worktree has no
sibling checkouts** — ⭐ **it does have the workspace root two levels above the
git common directory, which is how the reading was taken here without writing a
path into any file (R7).**

| | second run (round 20) | ⭐ **this run** |
|---|---|---|
| contributions in `catalogue-contributions.md` | 16 | ⭐ **16 — UNCHANGED since `1e49225`** |
| new adoptions from that file | 8 | ⭐ **0** |
| ⛔ **deferrals outstanding** | **2** | ⛔ **2 at open, 0 at close** |
| new entry | — | ⭐ **1 — entry 19** |

⛔ **Both deferrals ruled in the same direction: THE FRAMEWORK CHANGES.**
⭐ **Which is exactly what the deferral's own trigger said to do with them** — *if
the framework changes, it was a finding; if it does not, it is a limit and it
belongs.* ⚠️ **So neither becomes an entry as filed:** `F19`'s classification half
closed with `W28` and its residue is now an acceptance condition on `SF-31`;
`F18`'s third state is `SF-35`.

⛔ **But `F18`'s ruling CREATED a limit that no later ruling removes, and that is
entry 19:** ⭐ ***a pattern that is correct only because of which files do not
exist is not a declaration.*** ⚠️ **The integrator who measured it refused to
propose it** — ⛔ **and the refusal is the entry**, because the next integrator
will reach for the same clever glob and needs to be told why it is refused before
a validator tells them.

⚠️ **What the run did NOT sweep, named so the instrument is not read as wider than
it is:** `questions-for-framework.md` grew by 317 lines and `tasks.md` by 68 in
the same window. ⛔ **Those are questions and a delivery plan, routed through the
board's question channel** — ⭐ **and a check that quietly widened its own
instrument would be catalogue entry 4 arriving inside the catalogue's own
process.**

### ⛔ THE LINT LINE (Ruling 79) — `chore/po-round24`

⛔ **`chore/po-round24`, pinned container, `docker/dev/check`, `ruff 0.16.6`:**

```
pytest                  3090 passed, 63 skipped     (identical skip set to base)
ruff check .            All checks passed!          exit 0
ruff format --check .   425 files already formatted exit 0
quality floor           clean                       exit 0
document pointers       0 unresolved                exit 0
```

⭐ **Denominator per Ruling 86a, DERIVED FROM THE TREE:** at `d1270cd`,
`git ls-tree -r --name-only` counts **432** `.py`/`.md`, minus the **8** under
`tests/fixtures/` that `pyproject.toml:86` excludes = **424**, ⛔ **and `ruff`
printed exactly 424 before this branch's handoff was written.** ⭐ **This branch
adds one tracked file, so `433 − 8 = 425`.**

⛔ **`PO-24/5` — the derivation was verified against BOTH numbers rather than
against one**, because `PO-23/5`'s two divergences can cancel: this worktree has
**zero** untracked files (`git status --porcelain -uall` → empty), so `ruff`'s
walk and the tracked set differ by the exclusion list ALONE. ⚠️ **The user's own
checkout carries one untracked file and prints 425 for `d1270cd`** — ⭐ **the same
commit, a different number, and neither is wrong.**

⛔ **The floor did NOT need a second pass this round, and that is `PO-23/8`
working:** ⭐ **the four new anchors were asked of `pointers.slug()` before being
typed, not after the floor rejected them.** ⚠️ **One EXISTING anchor did break —
`#w28w40-…` — because this round renamed the heading it points at**, ⛔ **which is
a failure mode the previous round did not have: not a mistyped slug but a
CORRECT slug whose target moved.**

---

## ⭐ THE ROSTER — Developer 1 takes `SF-12` whole, CONFIRMED, and the split point is named IN ADVANCE

⛔ **SUPERSEDED at round 23 by [M2 step 2.1's assignment](#m2-step-21-closed-2026-09-10-at-a00337b-and-it-is-a-different-kind-of-milestone).**
⭐ **Kept whole and unedited, because the reasoning is what this board keeps:**
this is where the one-author-for-a-`Team`-task precedent was argued, and `SF-04`
and `SK-02` both inherit it. ⚠️ **`SF-12`, `QA-03`, `W30`, `W31` and `W33` are all
DONE and merged; the round-21 and round-22 queues inside this section are spent.**

⛔ **Confirmed, not merely accepted.** ⚠️ **`SF-12` is `Team`-sized and my own rule
is that a `Team` task is scheduled by the LAST developer to become free — which was
this moment, with both free** — ⭐ **and the rule says when to *start* it, not how
many authors it takes.**

**Why one author is right here, and it is a precedent plus a measurement:**

- ⛔ **`SF-10` is the precedent** — also `Team`, built by one developer to its
  approved survey, with the CTO recording *"`SF-10` is half a `Team` task and the
  half that landed is the right half"* and routing the remaining subtask
  separately.
- ⛔ **The collision-pair rule forbids splitting a shared surface**, and two agents
  cannot safely author one branch at once. ⚠️ **Splitting `SF-12` across two
  branches today would put both authors in `page/__init__.py` and `page/text.py`
  on day one** — ⭐ **the two modules every other module consumes.**
- ⭐ **The survey priced the port at ~1420 lines across 10 modules**, inside the
  1260–1890 band its own expansion ratio predicts. ⛔ **That is a large task and it
  is not two tasks.**

### ⛔ The split point, measured from the survey rather than invented

⭐ **If the task has to be split mid-flight, this is where — and naming it now is
what keeps the split cheap:**

| Half | Modules | ⛔ **Why the seam is here** |
|---|---|---|
| ⛔ **First, and NOT splittable** | `page/__init__.py` (the contract), `page/text.py` (escaping), `page/blocks/` (dispatch + prose + figure + verbatim) | ⭐ **Every other module consumes these.** ⛔ **They are authored once, first, by one person** |
| ⭐ **Second, and joinable** | `page/section.py`, `page/navigation.py`, `page/assets.py`, `page/document.py`, `render/templates/` | ⭐ **The composer half reaches the block renderers only through the dispatcher contract**, so a second author lands here without touching the first half's files |

⛔ **The trigger, so this is a plan and not a hope:** ⭐ **Developer 2 joins at the
composer half ONLY once `page/__init__.py`, `page/text.py` and `page/blocks/` are
committed on `feat/SF-12-renderer`** — ⚠️ **and only if the port measures past the
survey's top of band (>1890 lines) or the wave is otherwise at risk.** ⛔ **Until
that commit exists there is no seam to split on, and a split before it is the
collision-pair rule's exact failure.**

### Developer 2's queue, confirmed and re-ordered

⭐ **`W29` first** (smallest row on the board, and `tests/test_gate_coverage.py` is
the surface they just finished in `W26`), **then `FND-08`** (unblocked — `W25`
merged at `2a272a5`), **then `W31`** (one word, and its surface is no longer under
review). ⛔ **`W30` is not urgent and is not queued ahead of any of them.**

#### ⭐ RE-QUEUED at round 21 — ⛔ **`W33` jumps three older unstarted rows, and Ruling 75 says it must name them**

⛔ **Both developers are engaged:** Developer 1 on `QA-03` (`feat/QA-03-visual`),
Developer 2 on `FND-09` (`feat/FND-09-sweep`). ⭐ **`W29` and `FND-08` both closed,
so the round-20 queue is spent.**

| Order | Row | ⛔ **When, and what it jumps** |
|---|---|---|
| **1** | ⛔ **`W33`** — the lint notice | ⭐ **The next row either developer picks up.** ⛔ **It JUMPS `W30`, `W31` and `W32`, all older and all unstarted** — ⚠️ **and the reason is the only one that licenses a jump: a measured cost.** ⭐ **The gap it closes hid 4 errors, 15 findings, 9 unformatted files and one surviving mutant in ONE wave; `W30`–`W32` have no measured cost between them** |
| **2** | `W31` | one word in a docstring, surface no longer under review |
| **3** | `W32` | the mixed-form contents fixture — ⭐ **with or after `FND-09`, which is now in flight, so this is close to ready** |
| **4** | `W30` | ⛔ **not urgent; Ruling 70's purge covers it procedurally today** |
| **5** | `W35` | ⛔ **exposure `0`. Genuinely last, and named so it is not read as forgotten** |
| ⛔ **not queued** | `W34` | ⚠️ **A 1511-line restructure is not a filler and must not be picked up as one.** ⭐ **It wants a slot of its own, and the right one is a wave in which no build task is in flight** |

⛔ **`SF-34` is NOT in this queue** — it is M2 step 2.4, and its only route into
this wave is `QA-03`'s screenshot failing row 8.

#### ⛔ RE-QUEUED at round 22 — **the round-21 queue is spent at the top and two of its rows had already started**

⚠️ **Measured, not assumed: `W33` is APPROVED (and off release — `PO-22/4`), and
`W30`/`W31` are on a branch the board called `todo`.** ⛔ **Three of the five
round-21 rows had moved.**

| Order | Row | ⛔ **When, and what it jumps** |
|---|---|---|
| ⭐ **in flight** | `W30` + `W31` | `fix/W30-W31` @ `a67f3cd` — ⛔ **not queued, because it is already being done** |
| ⭐ **awaiting release** | `W33` | ⛔ **APPROVED on `chore/cto-round25` @ `85f0990`. Nothing to pick up; somebody has to MERGE it** |
| **1** | ⛔ **`W37`** — the checks-that-cannot-fail sweep | ⭐ **The next row either developer picks up.** ⛔ **It JUMPS `W32` and `W35`, both older and unstarted** — ⚠️ **and the licence is the only one that licenses a jump (Ruling 75): a MEASURED cost.** ⭐ **A mutant SURVIVED against `W33`'s own cap test, and this is the seventh instance in the project; `W32` and `W35` have no measured cost between them** |
| **2** | ⛔ **`W36`** — the browser in the image | ⛔ **BLOCKED until `QA-03` merges** — the harness must exist for the image to serve it. ⭐ **Also jumps `W32` and `W35`, on `QA-03/9`'s measured 55 skips** |
| **3** | `W38` | ⭐ **Small, and it jumps NOTHING** — ⚠️ **stated because a row minted this round that does not jump is worth telling apart from two that do** |
| **4** | `W32` | the mixed-form contents fixture — ⭐ **its gate cleared; `FND-09` merged at `dfccda1`** |
| **5** | `W35` | ⛔ **exposure `0`. Genuinely last, and named so it is not read as forgotten** |
| ⛔ **not queued** | `W34` | ⚠️ **Unchanged: a 1511-line restructure is not a filler.** ⭐ **It wants a wave in which no build task is in flight** |

⚠️ **`PO-21/5` bites again and I am naming it rather than pretending otherwise:**
⛔ **BOTH rows that jump this round jump on a cost somebody happened to
instrument**, and `W32` and `W35` lose again for the second consecutive round —
⭐ **not because they are less important, but because nobody has measured them.**
⛔ **That is `PO-20/2`'s ranked queue, still owed, now with a two-round record.**

⚠️ **The cost of this roster, named rather than discovered:** ⛔ **one developer on
a `Team`-sized task is the slowest safe arrangement, and if it slips, the wave
slips with it.** ⭐ **The mitigation is the seam above, and it is only a mitigation
if the first half lands early** — ⛔ **so a `SF-12` that has not committed
`page/blocks/` by mid-wave is the signal, not the deadline.**

---

## ⛔ RULED 2026-09-10 — **`W26` was minted twice, and an id space gets ONE MINTER**

⛔ **Measured at close: two different `W26` rows are live on this board, from two
branches, in one wave — and the merge combined them cleanly with no conflict.**

| | Subject | Minted by | State |
|---|---|---|---|
| **`W26`(PO-18)** | `PO-18/2` — PEP 758 syntax in `tools/quality/config.py`; **NOT A DEFECT** | PO, `chore/po-round18` | ✅ **closed, discharged** |
| **`W26`(CTO-18)** | ⛔ **Ruling 57** — `W7`'s reader tell resolves the name's *origin*, not its spelling | CTO, `chore/cto-round18` | ⛔ **live** — Developer 2, branch `fix/W26-gate-tell` |

### ⭐ This is the finding-number collision one level up, and it refutes the same remedy

⚠️ **Last round ruled that findings are numbered per-document because an
allocator file is invisible across branches, and warned in terms:** ⛔ ***"worst
case both increments merge cleanly and one number is lost silently."***
⭐ **That is not a prediction any more. It happened, to `W`-ids, in the very wave
the warning was written**, and the warning's own wording is why it was found:
`git merge` reported success.

⛔ **But the finding rule's REMEDY does not transfer, and that is the interesting
half.** ⚠️ **Findings were fixed by scoping the number to its document — and
`W`-ids already live in exactly one document.** ⭐ **So the defect is not *no
allocator*. It is *two allocators*: one file, two authors, two branches.**

⛔ **RULED: an id space has exactly one minter, and the minter is whoever owns the
document the space lives in.**

| Space | Minter | Why it has never collided |
|---|---|---|
| **Ruling numbers** | **CTO** | one author, and it is why `57` and `58` are clean |
| **`W`-ids, task ids, board rows** | ⛔ **PO** | `BOARD.md` is the PO's document (line 3) |
| **Finding numbers** | per-document author | ruled round 18 |

⭐ **The CTO does not lose anything they were using this for.** ⚠️ **Their round-18
routing of `SF-10`'s two structural findings was correct, wanted, and urgent** —
⛔ **what it did not need was a number.** ⭐ **A routed finding arrives as
*Ruling 57* and *Ruling 58*, in the space the CTO already owns and already mints
without collision; the PO gives it a `W`-id when it lands on a row.** ⚠️ **One
extra hop, and it is the hop that makes the collision unrepresentable rather than
detected** — ruling 29's move, again.

### ⛔ The disambiguation — `W4`'s precedent, and NEITHER is renumbered

⛔ **`W26`(CTO-18) KEEPS the bare id `W26`.** ⭐ **A branch (`fix/W26-gate-tell`),
an assignee and an urgency all already point at it**, and renaming a live branch
to tidy an id is the migration costing more than the ambiguity.

⛔ **`W26`(PO-18) is SUPERSEDED IN PLACE and is cited as `W26(PO-18)`.** ⭐ **It is
closed, discharged, and cited in exactly one place outside its own row** — the
round-18 handoff, ⚠️ **which is a record and is not rewritten.** ⭐ **The board is
where a superseded record gets superseded**, exactly as `53` / `54` / `55` were.

⛔ **`W28` and up are minted by the PO only.** ⭐ **High-water mark measured across
every branch in the repository, 2026-09-10 @ `2926dc2`: `W32`** — `W28` and `W29`
last round, ⭐ **`W30`, `W31` and `W32` this round.** (`W99` exists and is a
deliberate non-id in an example.)

### The six, at open

⛔ **6 — catalogue contributions: read each consumer repository's contributions file, adopt what qualifies, and RECORD A DECISION FOR WHAT DOES NOT.** ⭐ **Added round 19; the argument is in `F23`'s ruling above.** ⚠️ **First run owes a decision on 11 contributions, 7 of them stranded.**

### ⭐ This round's readings — ⛔ **checks 3 and 4 both changed the plan**

| # | Check | Reading, 2026-09-10 @ `e5bcc85` |
|---|---|---|
| 1 | index present and current | ✅ clean in the pinned image |
| 2 | `[structural]` triage | ✅ **131 marker lines across 32 files** |
| 3 | ⛔ **C6 — every ruling reached its artifact** | ⛔ **the index was wrong on 6 of 10 audited, all in one direction** |
| 4 | ⛔ **re-measure every row whose trigger has passed** | ⛔ **3 of 9 step-1.4 rows wrong, in *both* directions** |
| 5 | `CLAUDE.md`'s *Where to start* | ✅ names M1 step 1.4 / `SF-10`, matching the board. ⛔ **AND IT FAILED AT CLOSE — see the close run** |
| 6 | catalogue contributions | ⛔ **did not exist at open; first run owed next wave** |

⭐ **Round 20's readings, @ `2926dc2`** — ⛔ **and this table is a pointer, not a
second copy:** check 4's second close run and check 6's second run are two
sections above, with their instruments and their refs. ✅ **Check 5 passes again**
after round 19 fixed it by replacement.

### ⛔ Check 3 — **the rulings index is an audit, and the audit was wrong six ways**

⚠️ **The index at `handoffs/CTO-2026-09-09-round17.md` lists 30, 43, 47, 48, 49,
52, 53, 55 and 56 as unlanded or partly so, and summarises itself as *"six
rulings have not reached an artifact."*** ⛔ **Measured by opening every named
artifact: six of the ten audited had landed and the index says they had not.**

| # | Index says | ⛔ **Measured** | Where it actually is |
|---|---|---|---|
| **30** | not landed | ⛔ **was true — ✅ LANDED THIS ROUND** | spec §4, *The complete key list*. ⭐ **The reversal held: `media` was never wrongly added, and no test asserts equality** |
| **43** | *"not scoped — four walks waiting"* | ⭐ **LANDED** | `tools/quality/source_names.py`, shipped with its migration |
| **47** | *"W20 — scheduled"* | ⭐ **LANDED** | `../conventions/personal-data-shapes.md` + `tests/test_shape_vocabulary.py` |
| **48** | *"`agent-protocol.md`"* | ⭐ **LANDED — in the other file** | `../conventions/module-structure.md:445`. ⛔ **`W24`'s row was right and the index was stale** |
| **49** | not landed | ✅ **correct — genuinely open** | nothing handoff-shaped in `tools/quality/`. This is `W25` |
| **52** | *"not landed"* | ⭐ **LANDED verbatim** | `../conventions/agent-protocol.md:226` |
| **53** | *"`FND-05a` ✅ · rubric §4b"* | ⭐ **RESOLVED by Ruling 61 — and BOTH my predecessor and I had the framing wrong** | ⛔ **The two sites are NOT duplicates and neither is emptied.** ⭐ **They are a rule and its worked example:** `review-rubric.md` §4b is the source; `../conventions/workspace.md` keeps its section because it holds the **exit-2 design fact the rubric must not own.** ⚠️ **We both read *"one clause in two files"* and reached for a collision** — ⛔ **the actual defect was the index**, which is check 3's own subject. ⭐ **The pointer note stands; the reasoning behind it does not** |
| **55** | *"Ruling 43's task"* | ⭐ **LANDED verbatim** | `../conventions/agent-protocol.md:200` |
| **56** | *"`module-structure.md` — PO"* | ⭐ **LANDED** | `../conventions/module-structure.md:39` |
| **46** | landed ✅ | ⭐ **LANDED** | ⚠️ **7 call sites, all in the defining module. Zero external consumers** |

⛔ **Genuinely open after the audit: 30 (now closed), 49, and 53's rubric half.**
⭐ **Three, not six.**

#### ⛔ The finding, and it is worth more than the nine corrections

⚠️ **An audit column is a *summary of a status owned elsewhere* — which is this
board's own named defect, arriving in the instrument built to catch it.** ⭐ **It
went stale in the same direction all six times: *understating* what had landed.**

⛔ **And that direction is the expensive one, because it is the one that looks
diligent.** ⚠️ **An index that over-reports landing gets caught the first time
somebody looks for the clause.** ⭐ **One that under-reports it costs a re-landing
— and a ruling landed twice, by two people, in two documents, is how `48` came to
be claimed for `agent-protocol.md` and to actually live in `module-structure.md`.**

⛔ **The rule: an index of where rulings landed is *derived by opening the
artifacts*, never maintained beside them.** ⚠️ **Its author said the writing of it
*was* C6's audit — ⭐ and it was, for the rulings whose artifact they had just
written. It was a guess for the ones somebody else carried**, and every one of the
six errors is in that second set.

#### ⛔ Ruling 55's own founding number is recorded three different ways

⚠️ **The rule says a number in a ruling is an instrument reading. Its own
measurement — the §7c grep versus the check — is on record as:**

| Artifact | Reading |
|---|---|
| `../conventions/agent-protocol.md:203` and `BOARD-ARCHIVE.md` | **7 → 19, across 11 modules** |
| `../conventions/review-rubric.md:691` | **7 → 19** |
| ⛔ `tools/quality/source_names.py:42` | ⛔ **7 → 13** |
| ⭐ **the tree today** | ⭐ **0 → 0** |

⛔ **Three artifacts, two answers, one experiment** — ⭐ **and the rule is right,
which is why this is not embarrassing but confirming.** ⚠️ **The correction is
`FND-08`'s and it is one line: whichever number is true, it is stale, because the
migration ran.** ⛔ **A number quoted from a ruling after the migration it measured
has completed is not merely imprecise; it describes a tree that no longer exists.**

| # | Check | Command |
|---|---|---|
| 1 | Index present and current **in the main checkout** | `built_at_commit` vs `git diff --quiet <it> HEAD -- src tools docs` |
| 2 | The `[structural]` triage list | `grep -rn '\[structural\]' docs/tasks/handoffs/` |
| 4 | ⭐ **Nothing ruled is queued-but-unlanded across the boundary** | ask each document owner; ⛔ **and re-measure every board row whose trigger has passed** |
| 5 | ⭐ **NEW — `CLAUDE.md`'s *"Where to start"* names the open milestone** | ⛔ **read it.** It loads into **every** session, so a stale sentence there misdirects every agent that starts — ⚠️ **and it has been the last to learn twice in two rounds** |
| 3 | ⭐ **C6: every ruling made since the last wave reached its artifact** — ⛔ **and it stays exactly here** (Ruling 39) | for each, open the task/epic/spec/convention it names and read the clause — ⛔ **and the neighbouring rulings in it, not only the clause being added** |

⚠️ **Check 3's scope, corrected on a measurement (Ruling 39) — I had this wrong.**
I proposed it belonged *closer to the code*, because an author caught a collision
this check did not. ⛔ **Measured: a sweep of the release tip at that moment would
have found three files and none was the colliding guard — it lived only on an
unmerged branch.** ⭐ **Distance was never the problem; the code was not in the
tree the sweep reads.** ⚠️ **And *"move rather than grow"* was the wrong
dichotomy — the answer is neither.**

⛔ **A check covers what is there; a broadcast covers what is coming.** This check
is the backstop for rulings whose subject is **already merged** — a real,
non-empty, otherwise-unwatched set.

### ⛔ Check 4, and the measurement that forced it — **a board row is the weakest destination there is**

⚠️ **Measured on the release tip `277469e`, 2026-09-09, opening step 1.4:**

| Item | Ruled | State on the tip |
|---|---|---|
| **W14** — the two missing invalid fixtures | ✅ ruled twice | ⛔ **`tests/fixtures/invalid/` holds FIVE.** Not landed |
| **W18** — Ruling 35, `authoritative ⟹ bundled` | ✅ ruled | ⛔ **`FORBIDDEN = (("generated", "authoritative"),)`** — the `generated` pair only. **`user` + `authoritative` is still accepted today** |

⛔ **Both were routed to Developer 1 *"with W14, before SK-01"*. SK-01 merged.
Neither travelled, and there is no review left to catch them.**

⭐ **This is the destination hierarchy proving itself, and W14 is the controlled
experiment because it was routed twice, two different ways:**

| Destination | What happened to W14 |
|---|---|
| ⭐ **a failing test** | *"The failing SF-02 test was the instruction."* The graded fixture shipped **without anybody being told** |
| **an Acceptance clause** | ⚠️ half-met — but **the reviewer was the backstop and it was caught in review** |
| ⛔ **a board row with an owner and a trigger** | ⛔ **evaporated, twice, silently** |

⛔ **So: a board row is a destination only for work nobody is currently in a
position to encode as a test or a clause.** ⚠️ **W6–W13 gave eight rulings a
destination and that was the right fix for having none — but I recorded it as
though all destinations were equal, and they are not.** ⭐ **A trigger that names
a task is only as good as somebody re-reading the board when that task ends** —
which is precisely the re-read that check 4 now forces.

⛔ **Step 1.4 does not open until W14 and W18 land** — see the step 1.4 section.
⚠️ Opening a wave while two ruled items sit unlanded is the exact defect check 4
was added to catch, and adding the check while committing the defect would make
it a rule nobody believes. ⭐ **The branch half is a *broadcast*
obligation on the ruling's author, not a sweep**, and it is now one command in
`../conventions/agent-protocol.md`: ⛔ **a ruling that changes a shared name names
its blast radius across branches.** ⚠️ Moving either instrument to do the other's
job leaves both holes open.

⛔ **Check 3 exists because checks 1 and 2 cannot see it.** ⚠️ A ruling that was
made, was correct, and never reached the artifact it governs looks **identical to
a delivered one** from every angle the other two checks have: the handoff says
ruled, the review says ruled, and the task that must act never hears. ⭐ **It is
the PO's check because the PO does the carrying**, and ⛔ **it deliberately did
not go to the reviewer** — the carry happens after the review, so a reviewer's
gate could not fire, and a gate that cannot fire is worse than none because it
reads as coverage.

### 1. Index present and current — ⚠️ **FAILED, and it has been fixed**

⛔ **The index in the main checkout was stale, and every agent this wave would
have queried yesterday's tree.** ⚠️ Note the trap this board documented last
round: `graphify-out/` is git-ignored, so a **worktree has no index of its own** —
the check is run against the **main checkout**, and agents reach it with
`--graph`, which is what makes R14 affordable at all.

**Measured, main checkout, `release/m0-foundations` @ `9ad45a2`:**

| | Before | After |
|---|---|---|
| `graph.json` `built_at_commit` | `220ea4b` — **15 commits behind**, 30 files changed | `9ad45a2` ✅ |
| nodes / edges | 3,075 / 6,081 | **3,281 / 6,463** |
| dangling-endpoint edges (`graphify diagnose multigraph`) | **203**, 192 collapsed, 1 self-loop | ⭐ **0 / 0 / 0** |
| code↔prose edges | 232 (3.8%) | 510 (7.9%) — ⛔ still not a bridge |
| `path "R7 — No Personal Data" "assert_clean()"` | no path | ⛔ **still no path, even undirected** |

⭐ **The fix was `graphify update <path>`: incremental, no LLM, no API key, under
a minute.** R7-verified after the rebuild: **zero** home paths in `graph.json`.

⚠️ **Two things this measurement retires, and one it does not.**

- ⭐ **Retired: "203 dangling edges — absence of a connection is not proof of
  absence"** as a *current* claim. The tool's own diagnostic now reports zero
  dangling, zero collapsed, zero self-loops, zero missing endpoints. ⛔ Any
  briefing still carrying the 203 is quoting a record as a status — the same
  defect, and this board is where it gets superseded. ⚠️ **The caution itself
  survives on other grounds** (the graph is unbridged), so do not read this as
  *the graph is now complete*.
- ⛔ **Not retired: the bridge.** `FND-07`'s hardest clause is still owed, and the
  one question this repository most needs answered still returns silence.

### 2. The `[structural]` sweep — ⭐ 32 findings, and it found a hole in its own rule

**Measured:** `grep -rn '\[structural\]' docs/tasks/handoffs/` — **32 findings
across 9 task handoffs** (⚠️ SF-03 carries four, not the two a quick count sees).
FND-01/02/04's 23 pre-marker findings were back-triaged last round and are not
re-swept.

⭐ **Only two are undispositioned, and both are correctly *accepted with the cost
named*** — which is one of the three legal outcomes, not a shrug:

1. **`SF-33` finding 3 — `api` is a generic field name.** The tree guard would
   flag a module reading an unrelated `api` key. ⭐ **Zero instances today** and
   the finding states its own remedy (narrow the rule to the module rather than
   drop the field). ⛔ **Accepted**, owner is whoever first mints a colliding
   field — realistically `SF-10` or the E03 TOC task.
2. **`SF-09` finding 3, routing half — the extraction source's `naming.py`
   docstring says 1,282 where the tree holds 1,290.** ⭐ **Accepted**: it is a
   defect in a repository v1 does not modify (R20), and the *rule* it exercised —
   *a claim about another repository is verified in that repository* — is already
   ruled and applied. ⚠️ Its ask was *"route to whoever owns the drift
   catalogue"*; `DOC-2026-09-09-codesignal-drift.md` predates it and has no entry.
   It goes to **E11's integration catalogue** rather than nowhere.

### ⛔ And the finding that is worth more than either check: **ruling is not carrying**

⚠️ **Thirty of thirty-two were ruled. Eight of those will still evaporate**,
because a ruling that reached no board row, no epic clause and no trigger is a
ruling that lives only in a handoff — ⛔ **and this board's own standing rule is
that a ruling living only in a handoff gets re-derived by whoever picks the task
up.**

⭐ **This is the C5 meta-finding one level down, and the sentence is almost
identical.** Then: *"the protocol said to write findings down; it never said
anyone had to rule on one."* Now: ⛔ **the protocol says to rule on findings; it
never said anyone had to carry the ruling.** The three words — *ruled, scheduled,
accepted* — were treated as terminal, and **only two of them name a destination.**
"Ruled" names a decision and no home.

⛔ **The rule tightens, and this is the correction: a `[structural]` finding is
dispositioned when its outcome has a *destination* — a task definition, an
acceptance clause, or a board row with an owner and a trigger.** ⭐ **A CTO
ruling is the decision, not the delivery**, and the person who owns delivery is
the PO. ⚠️ The test is unchanged and still the right one — *would this happen
again to somebody else?* — it was simply being asked one step too early.

⭐ **The eight are now rows W6–W13 below**, which is the destination they lacked;
three of them were carried into task definitions this round because their
triggers are imminent.

---

**M0 residue: `FND-05a` only**, and it is still the one task that can slip without stopping anybody. ⭐ Reasoning in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md). ⚠️ It should not slip *indefinitely* — the failure it prevents has **no symptom**.

---

**The index defect: ✅ closed by `FND-07`** (merged `1cc4e6d`). ⭐ **The measurement that produced it — 33 worktrees, 2 with an index — and the standing rule it generalised are in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md).** ⛔ **The rule is live and is not archived: no acceptance condition is satisfied by an untracked artifact alone — the task ships the check.**

---

## Open work items — routed, with owners

| # | Item | Owner | When | Note |
|---|---|---|---|---|
| W1 | ⭐ **`require_slug`/`require_ordinal` format `{value!r}`** — every address segment, identity field and unit ordinal inherits an R7 echo, so **7 of 26 emission sites are one pair of lines seen through their callers** | **Developer 2** | ✅ **merged `f569d0e`** | ⭐ **The highest-value single fix available**, and the ratio is why: fixing one pair of lines closes 7 sites. ⛔ A refusal that quotes the value has relocated the leak into a log. ⚠️ **Round 17 finding 9 rides in the same commit:** `AddressError`'s docstring *mandates* the echo this removes |
| W2 | **Behavioural §1f check** — poison an absolute path into each string parameter, fail if the refusal reproduces it. Prototyped, deliberately not shipped. **46 pairs before the label fix, 45 after** | **Developer 2** | ✅ **merged `f569d0e`** | ⭐ It is W1's enforcer: W1 fixes the sites, this stops them coming back. ⚠️ A delta of one, reported honestly, is exactly the number that makes it credible. **Measured since:** 6 of 10 poison shapes reproduced an identifier in a `validate` report; 10 of 10 clean with W1 prototyped |
| W3 | ⚠️ **Fixture defect, found by a graph build rather than a test** — `depth1/.../media/diagram.svg` says *"Two nodes and an arrow"*, its lesson's `alt` says *"…joined by one arrow"*, and the geometry is an undecorated `<line>` with **no marker and no arrowhead**; the two accessible names also differ in wording | **Developer 2** (FND-04's author) | ✅ **merged** | ⭐ **Worth more than the defect: a graph build found what the test suite did not.** ⛔ **Its old trigger — *"with the next fixture touch"* — named work that is now Developer 1's**, so Developer 2 would have waited forever. A trigger naming somebody else's work is not a trigger |
| W4 | **`handoffs/SF-05.md` still describes `LABEL_FORBIDDEN`** and lists its duplication as open finding 6; both are resolved by the hotfix | PO — ✅ **discharged here** | ✅ done | ⛔ **A handoff is a record and is not rewritten** — my own rule — ⭐ **so this row *is* the correction.** The board is where a superseded record gets superseded |
| W5 | ⛔ **CORRECTED — the number is right about the *file* and misleading about the *task*.** `unitdoc.py` is **827 lines**; ⭐ **about 250 are left to port.** SF-05, SF-06 and SF-09 already landed the overlay reader (`unit/content.py`, 300 lines), the section-key vocabulary, the error type and `AUTHOR_MAY_NOT_WRITE` as `DERIVED_FIELDS`, and **`_check_address_against_map`'s job is already done by `validate/structure.py`** | `SF-10` | at **SF-10** | ⚠️ **`SF-10` has been carrying an 827-line port in its head and the real figure is a third of that** — so the task is **re-priced**, and this row is corrected so the number stops being quoted at its old scope. ⭐ **The inventory *sums* to 827** (201 header / 30 gates / 74 archive reading / 189 derived / 97 build / 134 `content.json` / 102 `unit.json`), so it is checkable rather than asserted. ⭐ **It still wants to be a package, for a measured reason: the same contract is ~145 lines in the source and 300 here — ≈2.1× expansion.** ⚠️ **One data point, and the survey said so** |

### ⛔ Ruled: **W7 and W13 are one commit**, and it is Ruling 19's argument again

⭐ **They look like two chores and they are one defect: *the gate's coverage is
assumed rather than asserted.*** ⛔ **W13 is two copies of the gate that
disagree; W7 is one reader that calls no gate at all** — the same hole seen from
its two ends. ⚠️ And the CTO has prescribed the **same remedy for both**: a test
that makes the omission **unrepresentable**, rather than a list that has to be
maintained.

⭐ **That is this project's most-repeated finding arriving for the fourth time** —
*make the illegal value unrepresentable; do not enumerate it.* ⛔ **A
hand-maintained list of readers is how W7 went missing in the first place**, so
fixing W7 by adding a call to a list would reproduce the defect while closing the
instance.

⛔ **One commit, but TWO NAMED TESTS — and my *"one test, not two"* was the loose
version the CTO corrected (ruling 27).** ⭐ *"'One implementation exists' and
'every reader calls it' are different assertions, and fusing them yields one
vague test proving neither."*

⚠️ **The reason to land them together is sharper than the load argument I gave:
separately each has a hole, and each hole is a live defect today.**

| Alone | The hole it leaves | Today's instance |
|---|---|---|
| **W13** alone | one authoritative implementation — **with a reader that never calls it** | ⛔ `corpus.json` |
| **W7** alone | every reader calls *a* gate — ⛔ **and calling the weaker copy satisfies it** | ⛔ `fixture_checks` |

⭐ **So the pairing is not a scheduling convenience, it is what makes either test
mean anything.** ⚠️ **Ruling 14's cross-package refusal does not apply** — that
refused an *unruled hotfix*, whereas ⛔ **C5's standing rule positively requires
the call sites to land with the test.**

⭐ **The combined item inherits W7's deadline, not W13's:** it goes **ahead of
FND-07**, because R7 is the rubric's one HARD FAIL and this one is in the front
door of the command an adapter author is told to trust.

⭐ **And the fact that dates the ordering, which neither the CTO nor I had when we
each reached it (ruling 25): my own `W14` ruling is what makes `W13` urgent.** I
ruled *build the count-mismatch fixture* — so ⛔ **W14 adds a new fixture to the
very tree the weaker gate guards.** ⚠️ *A fixture authored while the checker
misses 3 of 4 home-path shapes and every dict key is a fixture whose boundary was
never actually asserted*, and §1e's whole point is that the exception is bounded
**by tests rather than by memory.** ⭐ That turns a priority call between
abstractions into **a sequencing fact with a date on it.**

⚠️ **Recorded as convergence rather than as an override.** The CTO's text says
ruling 25 overrides `47df43a`; ⭐ **`6acff60` had already moved FND-07 behind
W7+W13 before that ruling landed**, so the two of us reached the same order from
different directions — and *that* is the part worth keeping, because an ordering
two people derive independently is one neither has to defend again.

### ⛔ SK-01's six findings, marked here — the board row **is** the triage

⚠️ **Finding 49, the CTO against themselves: `SK-01` was APPROVEd twice without
§8a, and its handoff carries six findings and zero markers.** ⛔ **The old counter
would have returned `0 = 0` and passed**, so running it would not have helped —
⭐ **which is exactly why the fix was the redesign and not the discipline.**

⭐ **Marked here rather than by editing the handoff — W4's precedent: a handoff is
a record, and the board row is the correction.**

| # | Finding | Marker | Disposition |
|---|---|---|---|
| 41–43 | Defects found and fixed within the task | `[local]` | ✅ **closed in `SK-01`** — no destination owed |
| 44 | ⛔ **The denominator finding** — two of its three numbers came from the integration side | `[structural]` | ✅ **routed to the integration catalogue as `W22`.** ⛔ Not fixed in `SK-01`: a cross-source fact buried in one skill is where the next source cannot find it (R19) |
| 45 | ⛔ **Java's `exercises: true` rests on 168 files that *look* like graders — out of 792 files, ⚠️ and *that* denominator is what the count was missing** | `[structural]` | ⛔ **UNOWNED, explicitly, until `E07` opens — and my routing to PO-Integration was WRONG.** See below. ⛔ **Nothing declares `exercises: true` for the Java corpus until this has an accountable owner** |
| 46 | ⛔ **ISO's record links the 3,863-line `TestCases.md` as its 39th unit** | `[structural]` | ✅ **ANSWERED — it is a fourth *container*.** The ingest decision remains open; see below |

⛔ **45 and 46 are not owed to the framework and must not be answered here.** ⭐
**They are exactly what `SK-01` was built to produce: *"I cannot determine this —
please confirm."*** ⚠️ **A skill reporting an honest uncertainty is the skill
working**, and it would be a defect to resolve them by guessing on the corpus
owner's behalf — R6, and the reason reconnaissance reports rather than decides.

#### ✅ ROUTED 2026-09-10 — **finding 45's accountability is `JS-01`'s Acceptance, and the *claim* is bounded by a check**

⛔ **`UNOWNED until E07 opens` is not a routing; it is a row waiting for somebody
to arrive.** ⚠️ **And it was sitting in the destination this board measured as the
weakest there is** — a board row with an owner and a trigger — ⭐ **which is the
same destination `W14` evaporated from, twice.**

⭐ **The routing, and it has two halves because the question does:**

| Half | Goes to | Why there |
|---|---|---|
| ⭐ **the judgement** — *do those files ask the reader to produce something?* | ✅ **`JS-01`'s Acceptance** (`E07`, M6) | ⛔ **`JS-01` owns `JS/corpus.json`. It is the task that writes the flag**, so it is the task that justifies it. ⭐ **An acceptance clause has a reviewer behind it** |
| ⛔ **the claim** — *does `exercises: true` match what the archive holds?* | ⛔ **`studyforge validate` — `PO-18/1`, below** | ⭐ **Nobody has to be *trusted*. The tool decides**, and it decides source-agnostically (R1) |

⛔ **That second half is what makes this closable, and it is the part the original
question could not see.** ⚠️ **The finding asked *"who is accountable for a
judgement about 168 files?"*** ⭐ **The better question is *what is the judgement
allowed to be wrong about?*** — and the answer is: the adapter decides what it
**emits**, after which the flag is corroborated against the emission. ⛔ **A
judgement only a person can make, bounded by a check a machine makes.**

##### ⚠️ And the finding was already stale in the epic it was routed to

⛔ **`E07`'s own measured-facts table has carried the finer numbers all along and
nobody cross-referenced them.** ⭐ **`168` is the *test-class* count; the same
table records `163` maximum name-paired exercises and `14` impl classes with no
`<Name>Test.java`.**

⚠️ **So the finding's headline number was superseded, in this repository, before
it was routed anywhere** — ⭐ **which is the standing rule arriving from a new
direction: a finding is a measurement with an as-of, and it is re-run before it
becomes a task.** ⛔ **Here the re-run was not even a command; it was reading the
epic the finding named.**

##### ⛔ `PO-18/1` — `studyforge validate` does not corroborate `exercises`, and the fixture checker does

**Measured 2026-09-10, `e5bcc85`:**

| | |
|---|---|
| the fixture checker | ⭐ `tests/fixture_checks/__init__.py:140` — `if bool(manifest.get("exercises")) != (practices > 0)`, rule id **`exercises-flag`** |
| `studyforge validate`'s check list | `validate/run.py:30` — `structure.CHECKS + paths.CHECKS + source.CHECKS` |
| ⛔ **an `exercises-flag` check among them** | ⛔ **none** |
| what it *does* check | ⭐ `check_practice_counts` — **per-unit** declared-vs-on-disk |

⛔ **So the manifest's front-door boolean is asserted in our own test scaffolding
and unasserted in the tool an adapter author is told to trust (R2).** ⚠️ **That is
`W7`'s shape exactly** — *"the tool an integrator is told to trust reports the
corpus's front door clean"* — ⭐ **and `W7` is the row this board rated URGENT.**

⚠️ **The gap is narrow and real:** per-unit counts are checked, so a corpus that
declares two practices and ships one fails. ⛔ **A corpus that declares
`exercises: true` and ships no practice anywhere passes**, because no unit
declared any to disagree with.

⭐ **Owner: CTO to rule the check's shape, then Developer 2.** ⛔ **Owed before
`JS-01` runs**, and `JS-01`'s Acceptance says so, which is what stops it becoming
another row nobody re-reads.

---

#### ⛔ Finding 45: I routed it to the wrong owner, and the refusal is worth more than the routing

⚠️ **PO-Integration owns ISO. Finding 45 is about the *Java* corpus.** They
declined it, correctly, and ⛔ **the clause that matters is not that I was wrong
but what being wrong would have produced:**

> ⛔ *"Routing it to me would make the mechanism look like it worked while
> producing an answer nobody is accountable for."*

⛔ **That is a new failure mode and it belongs with C6's family: a question routed
to the wrong owner comes back *answered*, and nothing marks the answer as
unaccountable.** ⚠️ **An unaccountable answer and a correct one are
indistinguishable on this board** — and the routing *looks* discharged, so
nobody checks. ⭐ **The refusal was the only thing that could have surfaced it**,
which is why an owner declining a question is a contribution and not an
obstruction.

⛔ **Disposition: `UNOWNED until E07 opens`, stated as a status rather than left
implied.** The Java corpus **has no PO in this session**. ⚠️ **A row that sits
looking answered is worse than an empty one**, so this one says it is unowned in
the field the board reads. ⛔ **And it gates: nothing declares `exercises: true`
for that corpus until the question has somebody accountable for the answer.**

⭐ **The transferable half PO-Integration contributed instead is now catalogue
entry 8** — *runnability is decided by the reader's obligation, not the file's
shape* — ⚠️ **and their own example is the one that proves shape insufficient:
`TestCases.md` is **191** Gherkin scenario declarations that look exactly like a grader corpus
and ask the reader to do nothing.**

⚠️ **They also turned `W22` back on us, correctly: *"168 of 792"* states a
denominator the source never stated**, so the ratio was unusable where it was
written. ⭐ **One line at the source versus an unrecoverable ambiguity
downstream** — the rule applying to us as readily as to them.

#### ⭐ Finding 46 answered decisively, and it changes ISO's shape

**`TestCases.md` is a fourth *container*. Not a unit, not an aggregate.**

| Measurement | Result |
|---|---|
| link targets in `README.md` | 39 |
| position of `TestCases.md` | 39 |
| markup carrying it (line 310) | `# [Test cases](TestCases.md)` |
| unit links carried by a `#` heading | ⛔ **0 of 38** |

⛔ **Every one of the 38 units is linked from *inside* a `#` heading; not one is
linked *as* one.** `TestCases.md` is linked **as** a `#` heading — same markup,
level and document as the three group headings, and **the only one of 39 targets
sitting where a container sits.**

**Not an aggregate, decisively:** of its **2,524** distinct non-blank lines,
**1** appears anywhere in `src/`, and that one is a bare code fence. The three
real aggregates are digest-identical concatenations.

⭐ **And the sharpest part: the evidence that made it look like an aggregate is
what proves it is a container.** Trap 4's **361 duplicated headings *are* its 17
chapters and their sub-structure**, recorded in the curriculum exactly as the
other containers' units are — ⭐ **so §6's *recorded, never derived* is satisfiable
for it**, which was the objection that would otherwise have sunk ingesting it.

**Consequence:** still depth-1, a fourth `test-scenarios` container of 17 units,
**38 → 55 units**, adding `gherkin` (244 fences).

⛔ **Whether to ingest is a separate, still-open decision — and it carries one
constraint that must not be lost.** ⚠️ **If the answer is *exclude*, the `why`
cannot say "duplicate", because it is not one.** It would be **material withheld
from the reader**, ⭐ **which is X1's exact test** — an exclusion states its
reason, and the reason has to be true.

#### ✅ **Q5 RULED 2026-09-10 — INGEST it. ⛔ 38 → 55 units, and `exercises` stays `false`.**

⭐ **This is the PO's call, not the integrator's, and the deciding argument is
that there is no true reason to exclude it.** ⛔ **X1 does not ask *is exclusion
defensible?* — it asks for a `why` that is TRUE**, and every candidate `why` has
been measured away:

| Candidate `why` | ⛔ **Measured** |
|---|---|
| *"duplicate"* / *"aggregate"* | ⛔ **False.** 1 of its 2,524 distinct lines appears in `src/`, and that one is a bare code fence. Real aggregates are digest-identical concatenations |
| *"structure cannot be recorded"* | ⛔ **False.** Its 361 duplicated headings **are** its 17 chapters, recorded in the curriculum exactly as every other container's units are — **§6 is satisfiable** |
| *"it is a unit, not a container"* | ⛔ **False.** 0 of 38 unit links sit where this one sits; it is the only one of 39 targets linked **as** a `#` heading |
| *"it is grader material"* | ⛔ **False, and it is the catalogue's own entry 8** |

⛔ **With no true `why` available, exclusion is unavailable.** ⭐ **That is X1
working as designed: the asymmetry — an inclusion needs no justification, an
exclusion does — decides this case on its own, without anybody weighing 17 units
against the cost of ingesting them.**

⭐ **And the affirmative reason, which is worth more than the absence of a
negative one:** ⚠️ **excluding it would make ISO an *easier* corpus, and ISO's job
is to be a hard one.** ⛔ **It is the second source (§12), and its value is
measured in findings, not in a tidy site.** ⭐ **A fourth container that is a
different shape — 17 chapters, **191** Gherkin scenario declarations, a fence language nothing
else uses — is exactly the extensibility signal M8 exists to produce.** ⚠️ **The
39th target being the one odd one is not a nuisance; it is the test.**

**Two constraints ride with the ingest, and they are Acceptance, not advice:**

1. ⛔ **`exercises` stays `false`. This does not make ISO runnable.** ⭐ **Catalogue
   entry 8 is the rule and this is the case it was written on:** *191 Gherkin
   scenarios that look exactly like a grader corpus and ask the reader to do
   nothing.* ⛔ **Ask whether the reader is asked to produce something — not
   whether the files look like test code.** ⚠️ **ISO remains complete at the
   reading floor and never enters the execution track (§11.0, C5).**
2. ⛔ **The 244 `gherkin` fences render as plain fenced text, asserted, not
   assumed.** ⭐ **`SF-11`'s ruling already decides this** — *a language with no
   grammar is left alone rather than dressed up as code* — ⚠️ **and catalogue
   entry 10 is the sibling: a default that guesses is worse than a default that is
   plain.** ⛔ **`gherkin` has no vendored Prism grammar, so the failure mode is a
   silent mis-highlight, which is `SF-11`'s screenshot defect again.**

⭐ **The two open questions turned out to be one rule seen from both sides**, and
that is the most transferable thing here: ⛔ **finding 45 asks *"168 files that
look like graders — are they?"* and Q5 asks *"191 scenarios that look like
graders — are they?"*** ⚠️ **Two corpora, two integrators, one question.** ⛔ **The
framework's answer must be identical and must not be a per-corpus judgement (R1)
— which is why both now land on the same check: `exercises` is corroborated
against what the archive holds, by the tool** (`PO-18/1`, above).

⚠️ **Recorded as a decision, not a proposal awaiting one**, per the standing rule
that implementation decisions belong to the PO and the CTO. ⛔ **It is reversible
by a later commit** — an ingested container can be excluded with a true `why`
later; ⭐ **the irreversible direction is the other one**, because a corpus that
shipped without it teaches nobody that the shape exists.

### ⛔ W6–W13 — the eight rulings that had nowhere to land

⚠️ **Every one of these was ruled by the CTO and every one would still have
evaporated**, because a ruling with no row, no clause and no trigger lives only
in a handoff. ⭐ **This table is the destination they lacked** — see *ruling is
not carrying*, above.

| # | Item | Owner | When | Note |
|---|---|---|---|---|
| W6 | ⛔ **The R7 exception-text check** — any `{exc}` interpolation re-emits the absolute path the inner refusal was careful not to emit. `SF-02` finding 1 and `SF-05` finding 4, ruled round 8: *"build it now — a check that arrives after twenty sites exist is one nobody turns on"* | **Developer 2** | ✅ **merged `f569d0e`** | ⚠️ **`CHECKS` still has five entries and none is this**, four rounds after *"build it now"*. ⭐ The ruling's own urgency argument is the schedule: `SF-04`, `SF-25`, `SF-28` and every adapter each add sites. ⛔ It is a **sibling of W2, not a duplicate** — W2 poisons a *parameter*, this reads a *format string* |
| W7 | ⛔ **URGENT — `corpus.json` is not gated at all.** A home path in the manifest `title` **validates green: zero findings, zero unchecked claims.** ⛔ **The tool an integrator is told to trust (R2) reports the corpus's front door clean.** Plus round 10's call-site table, of which only `SF-06`'s clause had landed | **Developer 2** | ✅ **merged `f569d0e`** | ⚠️ **Verified independently by the PO, not inherited:** `assert_clean` is called from `archive/document.py`, `corpus/container/document.py` and `unit/content.py` — and ⛔ **`corpus/manifest/` (6 modules, `document.py` among them) calls it nowhere.** ⭐ **`validate` was already wired for it: the catch is correct, the raise never comes** — which is why nothing looked wrong. ⛔ **The fix is a test that every reader gates, never a call added to a list** — a hand-maintained list of readers is how this went missing |
| W8 | ⛔ **The dev image has no JS runtime**, so 38 tests can only run off-image. `SF-11` finding 1, ruled round 11 an `FND-03` follow-up: *"not optional and not 'when convenient'"* | **Developer 1** | ✅ **merged `dc4686c`** — ⭐ **skips 46 → 8** | ⛔ E03 and E04 widen this gap from here, and the container is authoritative *because it is pinned*. ⚠️ A claim only provable off-image is a claim the verdict cannot rest on |
| W9 | **The markup contract has one side written** — `render/pageassets/surface.py` guesses `SF-12`'s class names. Ruled round 11: **SF-12 reviews the names in one commit as its first act** | `SF-12` | at **SF-12**, step 1.5 | ✅ **LANDED 2026-09-10 in `E03`** as `SF-12`'s *First act* subsection — ⭐ **and the row's own warning is why it went there:** *"its first act"* is a sequencing instruction that only works if it reaches the task **before** the task starts, ⛔ **and a board row is the destination that has evaporated twice.** ⚠️ **The path was under-specified here too** — the module is `render/pageassets/surface.py`, and its docstring already carries the *may-rename-never-duplicate* rule this row was asking for |
| W10 | **Palette tokens with no painter** — `--hl-*`, `--player-height`, `--practice*` are defined and unclaimed. Ruled round 11: a **named, self-retiring list**, and E04/E08 acceptance gains *remove your token* | PO → E04, E08 | **before E04 / E08 are authored** (M3, M5) | ⭐ Self-retiring is the good part: the list is a number that must reach zero, ⛔ not an exclusion that lives forever. The word *"unclaimed"* currently appears nowhere |
| W11 | **`api` is a generic field name** — the tree guard would flag a module reading an unrelated `api` key. `SF-33` finding 3 | ◐ **ACCEPTED, cost named** | if a colliding field is ever minted — realistically `SF-10` or E03's TOC | ⭐ **Zero instances today**, and the finding states its own remedy: narrow the rule to the module rather than drop the field. ⛔ Recorded so the remedy is not re-derived under time pressure |
| W12 | **The extraction source's `naming.py` docstring says 1,282 where the tree holds 1,290.** `SF-09` finding 3, routing half | ◐ **ACCEPTED, cost named** → E11's integration catalogue | at **SK-07** / the catalogue | ⭐ A defect in a repository v1 does not modify (R20), and the *rule* it exercised — **a claim about another repository is verified in that repository** — is already ruled and applied. ⚠️ Its ask was *"route to whoever owns the drift catalogue"*; `DOC-2026-09-09-codesignal-drift.md` predates it and has no entry |
| W14 | ⏳ **in flight** — ⛔ **TWO missing invalid fixtures on FND-04's surface, and they are one task** — the **count-mismatch** fixture (`E10` names six, five exist) and the **`user` + `authoritative` R5 pair** (finding 29). ⭐ **Both are record defects, not coverage holes: `check_counts` and the trust rule are implemented and tested — only the fixtures are absent** | **Developer 1**, after `W8` | ⛔ **before `SK-01`**, which reads `SF-25`'s output as its model of "valid" | ⚠️ **Measured on `feat/SF-23-exercise` @ `5a01a30`: the graded fixture shipped, the count-mismatch fixture did not** — `tests/fixtures/invalid/` still holds five. ⛔ **`SF-23`'s Acceptance names both, so this is a live review item, not an escaped one** — flagged to the CTO while the branch is in review. ⭐ **That is the mechanism working: routing an item into a task's *Acceptance* rather than a board row is what makes a reviewer the backstop** | ⛔ **An acceptance clause naming a fixture that does not exist is unfalsifiable** — the same class as an acceptance satisfied by an untracked artifact, arriving in a *condition* instead of a build product. ⭐ Ruled: **build the fixture, keep the clause** — it is the only statement that the count check is exercised, and the count check guards *silently lossy ingestion* |
| W23 | ⛔ **WAS a live R7 hole — two personal-data shapes passed the gate clean:** **tilde-rooted paths** and **`/export/home/<name>/`**, both carrying an account name. ⚠️ **Blast radius was wider than `origin`** — `assert_clean` walks **every string in a document**. Developer 2's finding 3 (two overlapping refusal sets) rode the same task | **Developer 2** | ✅ **`done` — merged `d178665`, handoff `R44-gate-shapes.md`** | ⛔ **The board carried this as `in-progress` for a full round after it merged — check 4 caught it.** ⭐ **The remedy was not a longer list: three asserted layers, a 9×3 matrix with two controls, and — the part worth keeping — ⛔ a *declared* `RESIDUAL` of three shapes the gate deliberately does not refuse**, because refusing `/var/lib/home/cache/x.md` would refuse a legitimate corpus. ⚠️ **Finding 3 closed structurally**: both readers now import one predicate and a test asserts they agree |
| W24 | **Ruling 48 — a derived-set assertion asserts *inhabitation*.** `test_a_sweep_excludes_exactly_…` was **born vacuous**: both sides computed, both empty under a directory exclusion, and it passed | PO | ✅ **LANDED this round** in `../conventions/module-structure.md` | ⭐ **Fifth instance of *a check that cannot fail*, and the first with a mechanical tell** — the four before it needed judgement. ⚠️ **It is *`0 = 0` is not a pass* in a second instrument**, and ⛔ **a rule ruled in one instrument does not transfer itself to another**: the same person ruled both without seeing the second while writing the first |
| W25 | **Ruling 49 — `tools/quality` gains a handoff check.** ⛔ **The six sections and the markers are a *contract*, and the only thing enforcing them is a grep in a rubric that a person runs from memory** | **Developer 2** | ✅ **`done` — APPROVED and merged at `2a272a5`, in the tip `c84ca2e`.** ⚠️ **CORRECTED TWICE by check 4: at round 18's open it read *"NEVER STARTED, byte-identical to `HEAD`"*; at round 19's close it read `in-review @ f77bb7d`; both were true when written and neither survived a day.** ⛔ **THIRD reading of one row in three runs, which is the whole argument for naming the commit rather than the tip** | ⚠️ **Three instances: `SK-01` (six findings, no markers — approved twice), `fix/gate-shapes`, and this.** ⭐ **This project ruled four times in one round that a rule a machine can check should not be a rule a person checks — and then left its own handoff contract as the exception.** ⛔ **RE-PRICED, and it is not small: 29 of 52 files in `handoffs/` are not `<TASK-ID>.md`** — 23 not task-shaped at all, 6 compound or suffixed. ⭐ **So the hard part is deciding what a handoff *is*, and the answer is `FND-08`'s: exempt by declaration, never by guessing at a filename.** ⛔ **SCOPE ADDED 2026-09-10 — this check is also the enforcer for per-document finding numbers** (`<TASK-ID>/<n>`, ruled above): ⭐ **a second, cheaper assertion on the same file, and a *shape* is what this check was already going to test.** ⚠️ **Numbers 20–58 in the existing 12 documents are GRANDFATHERED** — ⛔ **a check that reds on them demands that a record be rewritten, which this project forbids** |
| W20 | ⛔ **Repository-wide §7c check — and its migration, in the same commit** (Ruling 43) | **Developer 2** | ✅ **`done`** — ⭐ **re-measured 2026-09-10: `0` hits by the check, `0` by the grep, floor clean, exit 0** | ⛔ **The board carried this row twice, as `todo` and as `done`, two rows apart.** ⭐ **A repository-wide check goes red the moment it lands**, so Developer 2's finding 1 is ruled: **a commit adding a check owns its migration.** ⭐ **The exemption generalises: exempt *documents*, never modules.** ⚠️ **Its pre-migration count is on record three different ways — 7→19 in two conventions, 7→13 in the check's own docstring** — ⛔ **and all three are now equally stale, because the migration ran.** ⭐ **That is Ruling 55 confirming itself** |
| W21 | ⚠️ **A fifth rubric gap: nothing checks for dangling pointers after a docs move.** `SK-01` built the far end before deleting the near one — ⛔ *"the reverse order would have produced a green suite and sixteen dangling pointers, and nothing in the rubric would have caught it"* | ⭐ **REASSIGNED — `FND-08`, Developer 2.** ⛔ **Not the CTO and not the rubric** | with `FND-08` | ⛔ **A rubric clause is a rule a person runs from memory, which is the exact thing Ruling 49 refuses.** ⭐ **Measured, and it inverts the price: `0` dangling links today, so there is no migration — ⛔ but 8 of 8 naive hits are FALSE, every one illustrative markdown inside backticks.** ⚠️ **So the cost is the parser, not the sweep**, and a repo-wide check that is 100% false-positive on its first run is one somebody switches off |
| W22 | **Finding 44 owed to the integration catalogue**, not to `SK-01` — ⭐ **two of its three numbers came from PO-Integration** | **PO** → catalogue | ✅ **routed this round** | ⛔ Fixing it inside `SK-01` would have put a cross-source fact in one skill, where the next source cannot find it (R19) |
| W17 **+ W19** | ⛔ **One commit, and for the reason W7+W13 were.** **W17:** *"describe a value without reproducing it"* — ⭐ **four spellings shrank to two documented holdouts while the item waited** (ruling 36). **W19:** ⛔ **the 39 remaining `{value!r}` sites, ruled urgent** | **Developer 2**, after `FND-07` | ⛔ **after `FND-07`** | ⭐ **This is the `label_of` defect at repository scale, and it is live: `W1` and `W7` are both on this exact discipline, so a fix to one spelling leaves three.** ⚠️ **It compounds with Ruling 20 one level down:** the personal-data **gate** had two copies that disagreed; the **diagnosis helper** has four. ⛔ §1a's *"do not re-derive the patterns, refused five times"* was about the **patterns**, not the **helpers** — so nobody swept here. ⚠️ **Deliberately not unified now:** three of the four are other tasks' contract surfaces and it would collide with two branches mid-flight |
| W18 | ⏳ **in flight, with W14** — ⛔ **`user` + `authoritative` is accepted today** — measured — so **a grader the reader wrote may declare itself the source's own.** ✅ **RULED 35: `authoritative ⟹ bundled`, stated positively** | **Developer 1**, with `W14` | before `SK-01` | ⭐ **The author believed the set should be `("bundled",)` and did not change it**, because `unit.trust` owns the rule and `E06` names only the `generated` pair — ⚠️ **an argument, not a measurement**, and they said so. ⛔ **Exactly the restraint R21 asks for**: a task that meets an unlocated contract stops and asks. One entry in `unit.trust.FORBIDDEN` if the CTO agrees |
| W16 | ⛔ **Every canonical example in the spec is a hand-maintained copy of a contract the code now owns** — ⭐ **the last such pair in the project.** The instance: `MANIFEST_KEYS` has **ten** keys, spec §4's example carries **nine**, and `media` was unteachable from the spec | ✅ **spec text — PO, LANDED 2026-09-10**; ⏳ **the asserting test — Developer 2, still owed** | ⛔ **before `SK-07` generates a manifest** | ✅ **§4 now carries *The complete key list* beside the example, with required/optional marked and the derivation named.** ⛔ **REMEDY INVERTED — Ruling 28 REVERSED by Ruling 30, and the reversal HELD: `media` was never added to the example, and no test asserts equality.** ⭐ **The two one-way checks are what remain: subset (the spec cannot teach a key the code lacks) and coverage (the code cannot own a key the spec never names — ⭐ the half that closes `media`).** ⛔ **Equality would have *compelled* the harm**: `SK-07` **generates** manifests, so an exhaustive example propagates an optional key onto every corpus, including ones with no media, and R9 freezes it at first declaration |
| W15 | ⛔ **Tooling wrote to a source repository's root ignore file** — a `graphify` git hook appended `graphify-out` to the ISO repository's ignore file on an ordinary commit, unrequested, ⚠️ **in the one repository where R3 is absolute.** Second half: `.claude/settings.json` carries a machine-local absolute path, an R7 exposure **created by tooling that no ruling names as a source** | PO → `OPS-05`, `SK-07` item 9 | ⛔ **before any adapter runs against a real source** | ⭐ **This framework's own repository is clean — checked, not assumed**: zero tracked files carry the real home path, our `graphify-out/` ignore came from `FND-01`'s scaffolding (deliberate, and this is not a source repository), no hooks installed. ⛔ **So the exposure is scoped to the corpus side, which is exactly where R3 bites.** ⚠️ **The rule is written in `graphify.md` and `SK-07` item 9 and is enforced by nothing that runs** — and `OPS-05` checks at **build** time while this happens at **index** time. PO-Integration reverted it and **re-measured after the fix**: the hook fired again, the root file stayed clean |
| W13 | ⛔ **One commit with W7 — ruled, see below.** **Two copies of the personal-data gate that already disagree** — `tests/fixture_checks/personal_data.py` skips dict keys where `SF-08`'s does not (`SF-06` finding 3, ruled **urgent**); and **`imports()` is spelled twice** and should be extracted to `tests/support.py` *"before a third scanner writes a third copy"* (`SF-06` finding 8) | **Developer 2** | ✅ **merged `f569d0e`** | ⭐ **One row because they are one defect**: the project's most-repeated diagnosis is *two copies of a contract*, and here it has produced a copy that **already gives a different answer**. ⚠️ `tests/support.py` exists and has no `imports()` |
| ⛔ **`W26`(PO-18)** — ⚠️ **AMBIGUOUS ID, disambiguated above; the bare `W26` means Ruling 57's row** | ⭐ **`PO-18/2`, RAISED AND CLOSED IN ONE STEP — recorded so it is not re-raised.** `tools/quality/config.py:205` and `:256` use PEP 758 unparenthesized `except OSError, subprocess.SubprocessError:`, which is a `SyntaxError` on ≤3.13. ⚠️ **Reported to me as *"this silently pins the quality floor to 3.14+"*** | PO — ✅ **discharged here** | ✅ **closed** | ⛔ **NOT A DEFECT. `pyproject.toml:19` already declares `requires-python = ">=3.14"`** — ⭐ **so the pin is explicit, not silent, and the syntax is legal in the only interpreter this project supports.** ⚠️ **The word *silently* was the whole finding, and it was the part nobody checked.** ⭐ **Kept as a row because the check cost one `grep` and the finding cost a paragraph** — ⛔ **and because the next reader who spots that syntax will raise it again unless this says they need not.** ⭐ **Standing rule, arriving from a new direction: before reporting a defect, open the file it is about** |

⚠️ **W1 and W2 are one piece of work and should be assigned together.** W1 without
W2 is a fix with no guard; W2 without W1 is a red check with 45 findings.

### ⛔ W26–W27 — SF-10's two structural findings, routed by the CTO at round 18

⭐ **Both are R7 coverage, both were found by the author and offered rather than
assumed, and neither is `SF-10`'s to fix.** ⛔ **`W27` is the more urgent of the
two: it is a live R7 fail-open that has already produced an unreachable catch
arm in `validate`.**

| # | Item | Owner | When | Note |
|---|---|---|---|---|
| W26 | ⛔ **Ruling 57 — W7's reader tell resolves the *name's origin*, not its spelling.** `SF-10` narrowed `DECODES` from `("loads", "load")` to `("loads", "json.load")` to stop flagging `unit/builder/material.py`, which delegates to `archive.document.load` and decodes nothing. ⭐ **The direction is ratified; the spelling is not.** Replace the token match in `tests/test_gate_coverage.py` with an `ast` walk that maps each module's own imports to an origin and asks whether the call resolves to `json.load`/`json.loads` | **Developer 2** | ⛔ **`todo` — NOT STARTED.** `fix/W26-gate-tell` is **byte-identical to `40731e4`**, measured 2026-09-10. ⛔ **next**, ahead of any further gate work | ⚠️ **Measured 2026-09-10, with a control: the shipped narrowing misses two genuine ungated readers** — `from json import load` + bare `load(h)`, and `import json as j` + `j.load(h)` — **both of which the old spelling caught.** ⭐ **The tree is not yet inhabited by either** (`import json`, unaliased, is the only spelling in `src/`), which is why this is next rather than urgent. ⛔ **A false negative in an R7 *coverage* check is worse than a false positive**: the false positive is what produced this ruling; the false negative is silent. ⭐ **Prototyped in the trial merge: the import-resolving tell gets all eight probe shapes right — A–E and H readers, F and G delegation — and finds the same six readers in the tree, so there is no migration** |
| W27 | ⛔ **Ruling 58 — an R7 refusal is never translated into a package's error family.** Three sites translate: `unit/content.py` → `ContentError`, `corpus/placement/identity.py` → `PlacementError`, `corpus/manifest/document.py` → `ManifestError`. Re-raise `PersonalDataLeak` as itself at all three, and **state the exception in each package's `errors.py` contract**, exactly as `archive/errors.py` and `corpus/container/errors.py` already do (*"two exceptions travel through, deliberately"*) | **Developer 2** | ⛔ **`in-review` — `fix/W27-r7-no-translation` @ `655b527`, 2570 / 8** — 12 files, 501 insertions, all three translation sites plus two `errors.py` contracts. ⛔ **urgent — before M1 step 1.5** | ⚠️ **R7 is a HARD FAIL rule failing open**: a family exists so a caller catches one type per item and continues, so a translated leak is logged as *"that unit did not build"* and the walk finishes green. ⛔ **Already load-bearing, measured with a control 2026-09-10:** because the manifest translates, `validate/corpus.py:157`'s `except PersonalDataLeak` arm for the manifest **is unreachable**, and a home path in `corpus.json` is filed under `RULE_MANIFEST` rather than `RULE_PERSONAL_DATA` — *"the catch was correct and the raise never came"*, which is W7's own sentence one layer up. ⭐ **The migration is cheap: zero tests assert the translated message** (`grep -rn 'carries personal data and is refused' tests/` → 0). ⚠️ **`corpus/manifest/document.py`'s docstring says it follows `unit.content._gate` *"exactly"*** — that sentence is how one site became three, and it goes with the fix |

### ⭐ W28–W58 — the live `W` rows, and this is a pointer

⛔ **RE-STAMPED AT `8146bdb`, 2026-09-10 (PO round 30's wave-open check 4), and
FIVE ROWS WERE ADDED — `W54`, `W55`, `W56`, `W57`, `W58`.** ⭐ **High-water mark
`W53` → `W58`; measured across every branch with `git grep -In '\bW5[4-9]\b'
$(git rev-list --all) -- docs`, which returns hits in three files and ⛔ EVERY ONE
OF THEM IS A REFUSAL TO MINT `W54`, not a mint.** ⭐ **`W57` goes to the FRONT and
jumps twelve older unstarted rows on a MEASURED cost in shipped code (Ruling 75).**
⚠️ **TWO ROWS MOVED TO `in-progress` — `SK-05` and `W40`, both with four
commits — and `W51`'s ORDERING CLAIM WAS STRUCK; `W50`'s population widened
2 → 3; `W38`'s clause now carries a DERIVATION where it carried the literal `8`;
`W53` absorbed `PO-29/4`'s conditional-instrument sentence.**

⚠️ **~~RE-STAMPED AT `a00337b` (round 28)~~ — superseded as a status; kept below.**

⛔ **RE-STAMPED AT `a00337b`, 2026-09-10 (PO round 28's wave-open check 4), and
FOUR ROWS WERE ADDED — `W50`, `W51`, `W52`, `W53`.** ⭐ **High-water mark
`W49` → `W53`; measured across every branch with
`git grep -In '\bW5[0-5]\b' $(git rev-list --all) -- docs` → NOTHING outside
this round's own commit.**

⛔ **ONE ROW MOVED TO DONE and THREE CARRY A RULING THAT HAD REACHED NO
ARTIFACT:** ⭐ **`W45` → `done` (`1aa6319`); `W40` gains **Ruling 119**'s two
commands; `W34` gains **Ruling 118**'s replaced start condition and is UNBLOCKED
after six rounds; `W49` gains **Ruling 117**'s DROP-or-RESTATE bound; and
`W44`'s Ruling 116 acceptance is REPLACED by **Ruling 121** because the
instrument it named was INVERTED.**

⚠️ **Two numbers each row's licence rests on, re-measured at `a00337b`,
`wt/po28`:** ⛔ **`W40` — `content.py` **400/400**, `test_gate_coverage.py`
**600/600**, `validate/source.py` **425/400** with a live deferral naming `W44`,
`test_document.py` **598/600**.** ⛔ **`W34` — `review-rubric.md` is **2068**
with **100** headings and no index; its start condition is REPLACED and the new
one measures **0** across four live branches and five worktrees, so it is MET.**

⚠️ **~~The round-27 re-stamp at `426672c`~~ — superseded as a status; its
instrument argument stands and is kept below.**

⛔ **THREE ROWS MOVED and one was RE-FRAMED, and none of it was inherited:**
⭐ **`W43` → `done` (`2caa0d2`); `W40` → FREE and re-framed (`CTO-32/8`, stated
three times before it reached this cell); `W37` gains **Ruling 111**, which had
reached NO artifact for three rounds; `W44`'s gate CLEARED.**

⚠️ **Two numbers each row's licence rests on, re-measured at `426672c`:**
⛔ **`W40` — `content.py` **400/400**, `test_gate_coverage.py` **600/600**,
`validate/source.py` **425/400** with a live deferral, `test_document.py`
**598/600**.** ⛔ **`W34` — `review-rubric.md` is **2068**, up **+53** from 2015,
the SIXTH consecutive round of growth and the sixth in which its start condition
is unmet.**

⚠️ **~~The round-25 re-stamp at `ce58a36`~~ — kept below for its instrument
argument, superseded as a status.**


⛔ **Statuses RE-STAMPED AT `ce58a36`, 2026-09-10 (check 4's SEVENTH close run),
and ZERO `W` rows moved.** ⚠️ **The CHEAP instrument the last two runs used does
NOT apply this round and I am saying so rather than reusing it:** ⛔ **`git log
d1270cd..ce58a36` touches **37** distinct `src/`, `tools/` and `tests/` paths**,
because `SF-31` and `SF-04` both merged in this window. ⭐ **So each row was
checked against the CHANGED-PATH LIST rather than against a claim that nothing
moved** — and every changed path is under `cli/plan/`, `corpus/discovery/`,
`corpus/placement/`, `version.py` or their test mirrors, ⛔ **none of which is any
`W` row's surface.**

⭐ **Two numbers each `W` row's licence rests on, re-measured rather than
inherited:** ⛔ **`W40` — `tests/test_gate_coverage.py` is still **600**,
`test_document.py` still **598**, `test_dev_image.py` still **583**; the tripwire
is exactly where it was.** ⛔ **`W34` — `review-rubric.md` is **1951** lines,
up **+70** from `1881` at `d1270cd`, which is the fourth consecutive round of
growth and the fourth in which its start condition is unmet.**

⚠️ **`git branch --no-merged release/m0-foundations` returned NOTHING at this
round's open** — ⛔ **and that reading is RE-TAKEN at the close, per `PO-24/9`.**

⛔ **The cells are RE-STAMPED, not inherited, and the difference is Ruling 97's:**
⭐ **a status carried across a ref change without being re-taken is a measurement
nobody holds** — ⚠️ **and the fifth run found four rows wrong precisely because
nobody had re-stamped them.**

⚠️ **THE COLUMN HEADER SAID `@ ee50f77` FOR A WHOLE ROUND while every cell said
`@ 2fe56a4`** (`CTO-27/5`). ⛔ **On this board's own ref rule a FALSE ref in a
header is worse than no ref**, because it is the cell a reader trusts to date the
whole table. ⭐ **Fixed at round 24, and the round-22 reading survives inside the
cells that still explain something.**

| # | Item | Owner | ⛔ **Status @ `ce58a36`, `wt/po25`** | Where it is argued |
|---|---|---|---|---|
| W28 | `source_files()` respects the repository's own ignore declaration | Developer 1 | ✅ **`done`, merged `6d65902`** | the §11.2 ruling above |
| W29 | Ruling 67's bound — one constant naming the three gated trees | Developer 2 | ✅ **`done`, merged `4f2fbf8`** | round 19's `W29` block |
| W30 | ⛔ **`PYTHONPYCACHEPREFIX` in the dev image** — isolation that is structural rather than procedural | framework agent | ✅ **`done` @ `ce58a36`, merged `3d0eb34`** — ⚠️ **board said `in-progress`** | rulings 70–73, carried |
| W31 | `DOCUMENT_KINDS` names two roles where three produce these documents | framework agent | ✅ **`done` @ `ce58a36`, merged `3d0eb34`** — ⭐ **same merge as `W30`** | rulings 70–73, carried |
| W32 | ⭐ **The mixed-form contents fixture** — a plausible short parse taken from real material | framework agent | ⛔ **`todo` @ `ce58a36` and NO LONGER A QUEUE ROW** — ⭐ **re-routed to `SF-13`'s acceptance at round 25: exposure measured `0`, and `src/studyforge/contents/` is a 20-line stub with no parser to short-read** | [`PO-24/8` discharged](#po-248-discharged-w32-and-w35-measured-and-only-one-of-them-was-a-queue-row) |
| ⛔ **W33** | ⛔ **The floor prints its lint state, absence included, as a NOTICE** (Ruling 78) | framework agent | ✅ **`done` @ `ce58a36`, on release via `3a45d4c`** — ⚠️ **board said *awaiting release*, and `PO-22/4` was true when taken and false minutes later.** ⭐ **`PO-23/4`: this is the second consecutive round in which a PO's branch-versus-tip reading aged out inside one round** | rulings 77–80, carried |
| ⭐ **W34** | `review-rubric.md`'s operational checklist — ⛔ **THE HARM IS 2068 LINES, 100 HEADINGS AND NO INDEX** — ⚠️ **~~six consecutive rounds of growth~~, which is the quantity the governor EXPRESSLY permits a correctness clause to raise** | framework agent | ⭐ **`todo` @ `a00337b`, UNBLOCKED AT LAST — Ruling 118.** ⛔ **The start condition *no build task in flight* is REPLACED, not re-scheduled: it was a PROXY the project's operating model never produces, so it was anti-correlated with its own subject.** ⭐ **NEW CONDITION — claim: no in-flight branch and no dirty worktree owns `docs/conventions/review-rubric.md`; instrument: `git diff --name-only release/m0-foundations...<branch>` and `git status --porcelain` per worktree, `grep -c review-rubric` → **0**. TRIGGER fires anyway at 100 headings OR 2000 lines, and BOTH are already true.** ⛔ **MEASURED `0` at `a00337b` across four live branches and five worktrees — MET, and probably met for most of the six rounds it was recorded blocked.** ⚠️ **It measured `1` at `253cdd3` (an uncommitted rubric edit in MAIN, `PO-28/4`), which is the first DISAGREEMENT this row's condition has ever produced.** ⛔ **`PO-27/4`'s conclusion was right and its EVIDENCE was refuted by the governor's own instrument: the fenced share ROSE 13.0 → 13.6 → 13.9%.** ⭐ **AFTER `W47` only, whose index form this file adopts. `CTO-28/1`'s governor fix and `CTO-31/3`'s gameability note still ride here, and so does `W53`'s rubric half** | [Ruling 118, rowed round 28](#w34-gains-ruling-118-the-start-condition-is-replaced-and-i-watched-it-return-a-disagreement) |
| W35 | `pointers.py` honours the ignore declaration (Ruling 80) | framework agent | `todo` @ `ce58a36` — ⛔ **exposure RE-MEASURED and still `0`: 61 pointers in 126 markdown files, none resolving into a git-ignored tree.** ⭐ **Queued LAST, now with a number and a TRIGGER** | [`PO-24/8` discharged](#po-248-discharged-w32-and-w35-measured-and-only-one-of-them-was-a-queue-row) |
| ⛔ **W36** | ⭐ **A browser in the pinned dev image**, checksum-pinned, plus `check`'s environment pass-through | framework agent | ⭐ **`todo` @ `ce58a36`, queued 10th, and UNBLOCKED** — ⚠️ **board said *blocked until `QA-03` merges*; `QA-03` is an ancestor of the tip.** ⛔ **Removes 55 skips and converts five clauses to `pinned green`** | round 22's mint block above |
| **W37** | ⭐ **The repo-wide sweep for checks that cannot fail BY CONSTRUCTION** | framework agent | ⛔ **`todo` @ `426672c`, queued 9th.** ⛔ **GAINS RULING 111 THIS ROUND, and it had reached NO artifact for three rounds** (`CTO-33/5`; measured `grep -rn 'Ruling 111' docs/` outside the round-32 handoff → **0** at `987eac4`): ⭐ **the version-discard class has a THIRD, UNFIXED member — `src/studyforge/unit/content.py` stores `content_api: int = CONTENT_API` and never passes it through, so `from_document` returns the BUILD's default instead of what the document DECLARED.** ⚠️ **Exposure `0` TODAY and that is precisely the trap: `KNOWN_CONTENT_API` holds one member, so the default is right BY COINCIDENCE — the exact condition under which `corpus_api` and `container_api` were invisible until somebody bumped them.** ⛔ **The RULE is what stops the fourth instance: a register that stores its version on the object is checked by a test that reads back a document declaring an OLDER version and asserts the field survives; a round-trip test that only uses the current version CANNOT FAIL, which is this row's class.** ⭐ **The one-line fix at the call site is SEPARABLE and does not wait for the sweep.** ⛔ **POPULATION also widened by `CTO-31/1` (M7: an assertion made in a state the constant renders unreachable) and by `CTO-32/5`.** ⭐ **The one-row M7 kill is WRITTEN AND PROVED by the CTO (`1 passed` unmutated, `1 failed` under M7) and lands as this row's FIRST commit.** ⭐ **`CTO-31/2` rides here: `knowledge index: none — none in this checkout.` stutters, and `4b-ii` makes reviewers quote that line.** ⛔ **ROUND 28 — ONE POINTER, NOT A WIDENING: `W45/3` is a member of this row's class (`check_sizes` returns before opening an under-ceiling file's docstring, so a stale deferral is read by NOTHING the build ships) and it is OWNED BY `W52`, because it carries a deadline and this row carries a queue position.** ⭐ **If this sweep runs first it will find that member already owned** | round 22's mint block above |
| **W38** | ⭐ **The floor and `ruff` disagree by RULE; pin the divergence with a test** | framework agent | `todo` @ `ce58a36`, queued 11th — ⭐ **small; jumps nothing.** ⛔ **After `W40`** — ⚠️ **and the reason is now measured rather than asserted: this row ADDS A TEST, and `tests/test_gate_coverage.py` is at **600 of 600**.** ⚠️ **`QA-03/4`'s OTHER half — the rubric half — is DISCHARGED (Ruling 88); this row is the floor half only.** ⭐ **GAINS ONE CLAUSE, ROUND 29 (`CTO-36`, item 6, ratifying `PO-28/1`): ⛔ **THE FLOOR'S LINT LINE SAYS IT COUNTS MARKDOWN TOO.** ⚠️ Six rounds read *"N file(s) already formatted"* as a count of this project's PYTHON source; it is not.** ⛔ **THE CLAUSE STATES THE DERIVATION AND NEVER THE LITERAL `8` (round 30, `CTO-37/8`).** ⭐ **The identity is `py + md − (py|md under tests/fixtures/)`, and the THIRD TERM IS DERIVED AT EVERY REF:** `a00337b` 360+140−8 = **492** · `7b5c0a9` 364+141−8 = **497** · `8821b11` **498** · `ed8442d` **499** · `ddddd05` **500** (`wt/po29`) / **501** (MAIN) · ⭐ **`8146bdb` 394+188−**47** = **535** (`wt/po30`) / **536** (MAIN), re-derived by me.** ⛔ **`SF-13` donated a 39-file fixture family and took that term from 8 to 47; the literal form would have predicted `394 + (188 − 8) = 574` and been WRONG BY 39.** ⚠️ **All SIX earlier confirmations had the term at 8, so not one of them could have caught it — Ruling 81 exactly: a total reproduced six times while one of its components had never moved.** ⭐ **The `+1` in MAIN is the user's untracked `ONBOARDING.md` and is a measurement, not a defect.** ⛔ **It tracks BOTH file kinds independently at every ref, which no coincidence does — and each run COULD HAVE returned a disagreement, which is what makes it a corroboration rather than a citation** | round 22's mint block above |
| ✅ **W39** | ⛔ **The index goes stale on every merge, so the release tip is RED after each one** (`CTO-25/9`) | framework agent | ✅ **`done`, MERGED `16049d2`** (CTO round 31, APPROVE) — ⛔ **`--is-ancestor 16049d2 d77cb85` → YES.** ⭐ **The CTO watched the floor print `knowledge index: stale` and exit `0` where it had exited `1` all night.** ⚠️ **Four findings, and TWO of them corrected the CTO: Ruling 109 (a gate command is written in ONE block) and Ruling 110 (§2e has exactly ONE standing exception, enumerated rather than denied)** | round 23's `W39` block |
| ⛔ **W40** | ⛔ **RE-FRAMED ROUND 27 (`CTO-32/8`): NO MODULE IN THE TREE SITS AT ZERO HEADROOM against R11** — ⚠️ **~~`tests/test_gate_coverage.py` is at 600 of 600~~ named a POPULATION, and a population enumerated in a row is a second copy nothing re-measures** | framework agent | ⭐ **`todo` @ `426672c`, FREE — its round-26 hold is spent, `SF-36` merged at `e4a2677`.** ⛔ **THE POPULATION IS DERIVED AT PICK-UP, not read off this cell.** ⚠️ **At `426672c` it is THREE modules at or over the ceiling — `src/studyforge/corpus/manifest/content.py` **400/400**, `tests/test_gate_coverage.py` **600/600**, and `src/studyforge/validate/source.py` **425/400** — plus `tests/studyforge/corpus/container/test_document.py` at **598/600**.** ⛔ **~~`validate/source.py` is EXCLUDED BY THE DERIVATION, not by a sentence~~ — REFUTED BY RULING 119 AND CORRECTED ROUND 28.** ⚠️ **The derivation returns `source.py` as its FIRST row of three; it leaves only when a SECOND command — §3c's deferral sweep — is run and SUBTRACTED. The floor alone returns ∅.** ⭐ **THE ROW NOW CARRIES BOTH COMMANDS AND THE SUBTRACTION, written out, so the carve-out is an instrument in fact and not in claim.** ⛔ **UNTIL IT DID, `W40` AND `W44` COULD NOT BE IN FLIGHT TOGETHER.** ✅ **THE BAR IS LIFTED: `W44` MERGED `7b5c0a9`, so `source.py` is a package and has left derivation A entirely — the collision is now IMPOSSIBLE rather than merely avoided.** ⭐ **RE-MEASURED at `7b5c0a9`: derivation A returns exactly TWO modules — `corpus/manifest/content.py` **400/400** and `tests/test_gate_coverage.py` **600/600** — and derivation B returns **0**, so A − B = A and the row's subject is those two.** ⚠️ **~~`W40` is FREE and is still not placed ahead of step 2.2's product path~~ — SUPERSEDED ROUND 29: the product path has NO second free row, so this row IS the second slot.** ⭐ **PLACED **NEXT 2**, round 29.** ⭐ **BEFORE `W37` and `W38`, which both add tests — into a file at 600 of 600, which is why that order has held for three rounds.** ⛔ **Stated three times by the CTO before it reached a row.** ✅ **RE-MEASURED AT `ddddd05`, derivation A printed IN FULL (Ruling 128): exactly TWO modules — `src/studyforge/corpus/manifest/content.py` **400/400** headroom **0**, `tests/test_gate_coverage.py` **600/600** headroom **0**; nearest miss `tests/studyforge/corpus/container/test_document.py` **598/600**. Derivation B → **ROWS=0**, so A − B = A.** ✅ **RULING 125'S GATE IS STRUCK (Ruling 127, `CTO-36/3`) — and it never reached this board: `git grep -n 'gated BEFORE\|gated before' -- docs/` at `ddddd05` → **4** lines, all in `docs/tasks/handoffs/`. `PO-29/2`.** ⛔ **AND ITS OTHER GATE WAS A CONDITIONAL NOBODY EVALUATED: ~~*"if `SK-07` needs to WRITE to `content.py`, `W40` becomes its gate"*~~ is measurably FALSE — the `not_material` vocabulary is already minted (21 hits in `content.py`) and `skills/adapter/scaffold.py` already GENERATES the globs; no file under `src/studyforge/skills/` imports `manifest.content`. `PO-29/4`.** ⛔ **THE ROW'S CONDITION, and it is the only coupling three commands found: the split must PRESERVE `corpus.manifest`'s public surface — a PURE MOVE, exactly as `W44` was proved to be** | [Ruling 119, rowed round 28](#w40-gains-ruling-119-both-commands-and-the-subtraction-written-out) · [placed round 29](#round-29-the-next-two-rows-owns-verified-at-ddddd05-and-the-r11-pre-dispatch-sum) |
| ⭐ **W41** | ⛔ **An R7 refusal borrows the absent state's `Unchecked` reason, and the reason is FALSE** (Ruling 94) | framework agent | ⭐ **`todo` @ `7b5c0a9` and FREE — its last hold is spent: `W44` MERGED `7b5c0a9`.** ⚠️ **~~STILL HELD — `W44` restructures `validate/source.py`~~, true at `426672c`.** ⛔ **RE-MEASURE BOTH SURFACES BEFORE STARTING: `validate/source.py` is now the PACKAGE `validate/source/`, so this row's cited line numbers are gone, not moved.** ⚠️ **Its two surfaces SHIFTED when `SF-35` merged, so this row RE-MEASURES rather than inheriting `validate/source.py:191` and `validate/paths.py:180`.** ⭐ **`CTO-32/9` gives its cross-cut a FOURTH costume: `declared_kind()` reports *absent* while detecting *malformed*.** ⛔ **AFTER `W44`** | round 24's `W41` block |
| ⭐ **W42** | ⛔ **The marker check judges 41 of 88 documents and reports `0` for all 88** (Ruling 107, with `CTO-29/4`) | framework agent | ⭐ **`todo` @ `426672c`, queued 6th (was 7th).** ⛔ **COLLIDES WITH `W48` on `tools/quality/handoffs/` — ONE DISPATCH, or `W48` merges first and this row re-measures.** ⚠️ **`PO-26/2`'s residue is unchanged and is still this row's: the numbers quoted BEFORE round 26 reproduce under no candidate instrument.** ⭐ **`PO-27/1` narrows it — check 2 IS reproducible now, and the only thing that changed is that the instrument was written down** | [round 25's `W42` block](#w42-minted-the-marker-check-judges-41-of-88-documents-and-reports-0-for-all-88) |
| ✅ **W43** | ⛔ **Two clauses `agent-protocol.md` is owed** — an acceptance condition names the instrument that would fail it (`CTO-29/3`), and a reading from a PROXY is not a property of the THING (`CTO-29/8`) | framework agent | ✅ **`done`, MERGED `2caa0d2`** (CTO round 33, APPROVE) — ⛔ **measured `git merge-base --is-ancestor 2caa0d2 426672c` → YES.** ⭐ **The CTO reviewed it by RUNNING both clauses negatively: clause 2 discriminated on its own cited instance, and clause 1 failed SEVEN live acceptance conditions in four epics.** ⚠️ **FOUR findings, and three became rows this round: `W43/1` → `W48`, `W43/2` → `W46`, `W43/4` → `W47`** | [round 25's `W43` block](#w43-minted-two-clauses-agent-protocolmd-is-owed-and-both-are-about-the-instrument) |
| ✅ **W44** | ⛔ **`validate/source.py` was 425 lines against R11's ceiling of 400, and the only thing making that legal was a deferral naming this row** | framework agent | ✅ **`done`, MERGED `7b5c0a9`** (CTO APPROVE) — ⛔ **measured `git merge-base --is-ancestor 7b5c0a9 HEAD` → YES at `7b5c0a9`.** ⭐ **The tree now holds ZERO `Size exception:` deferrals, measured with Ruling 113's `ast` sweep and NOT with `grep`: **0**.** ⚠️ **Round-27 state, kept: `todo` @ `426672c`, NEXT 2 — ITS GATE HAD CLEARED.** ⛔ **`SF-36` (`e4a2677`) and `SF-35` (`a53aee8`) are both ancestors of the tip; the pair breach that was predicted at 419 landed at **425**, and 419/420/421/425 are four accurate readings of four different trees.** ✅ **`W45` HAS MERGED (`1aa6319`) — the merge-order gate is DISCHARGED**, and the review-time instrument stands: `git merge-base --is-ancestor 1aa6319 HEAD` → exit **0**. ⛔ **BEFORE `W41`.** ⭐ **CARRIES RULING 116 and `SF-36/1`** — ⛔ **and RULING 121 REPLACES Ruling 116's instrument, which was UNREACHABLE AND INVERTED: it is now `git grep -l 'Size exception:' -- src/ \| wc -l` → **0**, the reading being the PRINTED NUMBER and never `$?`.** ⚠️ **`W44` was dispatched against the broken clause; the developer must name what they actually ran rather than substitute one silently.** ⛔ **NARROWED ROUND 29 BY RULING 123 (`CTO-36/4`): that grep is the CORROBORATOR and §3c's `ast` sweep at **ROWS=0** is THE GATE — the two disagree on a marker in a COMMENT (sweep ignores it, grep false-positives) and `\| wc -l` returns `0` for a TYPO exactly as for a clean tree** | [round 26's `W44` block](#w44-minted-validatesourcepy-becomes-a-package-and-two-correct-decisions-composed-into-a-build-failure) · [Ruling 123's narrowing](#w44s-acceptance-ruling-123s-narrowing-and-the-two-instruments-disagree-on-a-real-input) |
| ✅ **W45** | ⛔ **Ruling 114 — `size_exception()` returns the marker LINE, so a deferral whose row id wraps prints with NO id and reads as a permanent design claim; and both remedy messages name only `<why splitting would be worse>`, the ONE form Ruling 113 excused** | framework agent | ✅ **`done`, MERGED `1aa6319`** (CTO round 34 addendum, APPROVE) — ⛔ **measured `git merge-base --is-ancestor 1aa6319 a00337b` → YES.** ⭐ **+10 tests, and a six-mutant same-size sweep killed every one with the baseline surviving both ends.** ⚠️ **THE BOARD NAMED THE WRAPPED CASE AND THE TREE FAILED THE UN-WRAPPED ONE TOO: truncation was a property of EVERY multi-line justification, and round 34's verdict quoted the truncated string as *Ruling 114 demonstrating itself* — it was the refutation, read as a confirmation.** ⛔ **FOUR findings: `W45/1` and `W45/4` DISCHARGED by the CTO in their own files; `W45/2` → **Ruling 121**, which replaced `W44`'s inverted acceptance instrument; `W45/3` → **`W52`**, minted round 28** | [round 27's mints](#w45-minted-ruling-114-the-deferral-reader-takes-the-whole-justification-and-the-tree-has-exactly-one-live-instance-to-test-it-against) |
| ⛔ **W46** | ⛔ **Ruling 115 — a finding states, PER CLAIM, whether its reading was MEASURED or RECEIVED, and from whom; plus `W43/2`'s process half, that a brief STATES a SHA and the receiver RE-DERIVES it** | framework agent | ⭐ **`todo` @ `426672c`, MINTED ROUND 27, queued 4th.** ⛔ **TWO files: `docs/conventions/agent-protocol.md` (825, beside clause 2) and `docs/conventions/delivery-flow.md` (359, because the receiver's obligation happens BETWEEN roles).** ⚠️ **PER CLAIM, not per finding — `SF-35/4` carried one measured half and one laundered half in one finding, and a per-finding field would have marked it *measured* and been correct and useless.** ⛔ **NOT into `W43`: that branch is merged and a remedy that edits its own subject measures nothing.** ⭐ **GAINS A THIRD LABEL ROUND 28 — `CTO-34/4`: `[ATTESTED]` joins `[measured]` and `[RECEIVED]`, for a claim about the author's OWN act that no command can reproduce** (`PO-27/2`'s origin claim was the first instance and had nowhere to sit). ⭐ **AND `PO-28/4`'s process half rides here, in `delivery-flow.md`: work in the reference checkout goes on a BRANCH, because a change on no ref is a tree nobody can name.** ⭐ **BEFORE `W47`, and before `W53`** | [round 27's mints](#w46-minted-ruling-115-a-finding-states-per-claim-whether-it-was-measured-or-received) |
| ⛔ **W47** | ⛔ **`agent-protocol.md` is 825 lines with 34 headings and no index, and its OWN clause 2 has just ruled `grep` unsafe on a document carrying corrections** (`W43/4`, ratified `CTO-33/7`) | framework agent | ⭐ **`todo` @ `426672c`, MINTED ROUND 27, queued 7th.** ⛔ **A heading INDEX, never a split — a split breaks every citation of the form *see `agent-protocol.md`, §…*.** ⚠️ **`CTO-33/6` measured the cost: **42 of 698** lines sit within ±3 of a correction marker, so one line in seventeen is a hit a reader must open before quoting, on the file they cannot navigate any other way.** ⛔ **AFTER `W46`, which grows the file: an index built before a clause lands is stale on arrival.** ⭐ **The index is TESTED or it is a second copy** | [round 27's mints](#w47-minted-agent-protocolmd-is-825-lines-34-headings-no-index-and-its-own-clause-2-now-distrusts-grep-on-it) |
| ⛔ **W48** | ⛔ **`W43`'s two clauses have no enforcement arm: `handoff-measured` (a marker line owes a `Measured` line naming a command AND a ref) and the clause-1 DENYLIST over `docs/tasks/E*.md`** | framework agent | ⭐ **`todo` @ `426672c`, MINTED ROUND 27, queued 5th. Agreed as a task by CTO round 33 — *"the PO mints it"*.** ⛔ **A fifth rule on an EXISTING reader: `contract.py` already carries `marker_lines()`, `_MARKERS_ON_LINE` and `_FINDING_LEAD`.** ⛔ **COLLIDES WITH `W42` on `tools/quality/handoffs/` — ONE DISPATCH, or this row first and `W42` re-measures.** ⭐ **RULED: `[none]` IS in scope — the CTO left the call to me and their own sentence decides it, *`[none]` is still a CONCLUSION from a measurement*; `MIN_NONE_CHARS` already forces a sentence and this forces that sentence to name a command.** ⚠️ **DO NOT inherit `W43/1`'s *not machine-checkable by design*: REFUTED by `CTO-33/3`, who ran a denylist and got **7 hits in 4 epics**. It was a property of the current reader named as a property of the rule.** ⛔ **The denylist is PARTIAL and reports its COVERAGE** | [round 27's mints](#w48-minted-handoff-measured-and-the-clause-1-denylist-w43s-two-clauses-get-their-enforcement-arms) |
| ⛔ **W49** | ⛔ **SEVEN live acceptance conditions in four epics fail `W43`'s clause 1 — each names no instrument that can return `no`** (`CTO-33/3`) | framework agent | ⭐ **`todo` @ `426672c`, MINTED ROUND 27, queued 10th.** ⛔ **`E00`:111/112/213/215, `E04`:298, `E06`:143, `E08`:121 — line numbers RECEIVED from `CTO-33/3` and this row's FIRST step is to RE-DERIVE them with `W48`'s lint, because line numbers drift and inheriting them is `PO-27/2`'s shape.** ⚠️ **TWO are in DELIVERED `FND-02`/`FND-04`, so the clause reaches retrospectively into work the review office already approved — which is the strongest available evidence that it does something.** ⛔ **M0 STAYS CLOSED, ruled by the CTO and not reopened here.** ⛔ **RULING 117'S BOUND, LANDED ROUND 28 — and it is why *"gains an instrument or is DROPPED"* was a defect: for a condition belonging to an ALREADY-CLOSED task there are exactly TWO dispositions, ⭐ DROP (it was never doing work) or RESTATE AS DELIVERED (it described something real), and ⛔ INSTRUMENTING IT IS UNAVAILABLE — a gate that appears after a close is Ruling 97's re-opening in a row's clothing.** ⭐ **`E00`'s four take the two; `E04:298`, `E06:143` and `E08:121` are in OPEN epics and take all three.** ⚠️ **Ruling 117 also RATIFIES this row's existence over the CTO's own disposition, and they say why: they diagnosed guidance-with-no-row in `CTO-33/5` and then used it in `CTO-33/3` in the same handoff.** ⛔ **AFTER `W48`, whose denylist is this row's instrument and its definition of done** | [Ruling 117, rowed round 28](#w49-gains-ruling-117s-bound-a-delivered-tasks-clause-1-failure-takes-drop-or-restate-never-a-new-live-gate) |
| ⭐ **W50** | ⛔ **An installed `studyforge` ships the skills' CODE without their PROCEDURES — `package-data` has no `SKILL.md` glob** (Ruling 120, ratifying `SK-02/3`) | framework agent | ⭐ **`todo` @ `a00337b`, MINTED ROUND 28, queued.** ⛔ **A defect against the RELEASE BRANCH and it is `SK-01`'s: `skills/reconnaissance/SKILL.md` was ALREADY unshipped at `426672c`. `SK-02` is the second instance and neither caused it nor may be held for it.** ⭐ **EXPOSURE NIL TODAY — nothing installs the package; the pinned image is pytest + ruff and `pythonpath` runs the suite from the checkout.** ⛔ **TWO THINGS OR IT IS NOT THE ROW: the glob AND a test enumerating `src/**/SKILL.md` — the glob alone is a fix that cannot fail, which is `W37`'s subject, and a missing procedure is SILENT because the package imports fine.** ⚠️ **`pyproject.toml` was outside `SK-02`'s `Owns` and they reported it rather than patching it** | [round 28's mints](#w50-minted-ruling-120-an-installed-studyforge-ships-the-skills-code-without-their-procedures) |
| ⭐ **W51** | ⛔ **`ARCHIVE_DIR` and `ARCHIVE_ROOT_NAME` are on no package surface, so every package that reads a corpus root RE-DERIVES them** (`SF-31/3`, with `SK-02/2` as its second measured instance) | framework agent | ⭐ **`todo` @ `a00337b`, MINTED ROUND 28.** ⛔ **`SF-31/3` had NO CARRIER OF ANY KIND — `grep -n 'SF-31/3' docs/tasks/BOARD.md docs/tasks/E*.md` at `a00337b` → **0 hits** — and `SF-31` is merged, so its only home was a closed task's handoff (`PO-28/5`).** ⚠️ **It WIDENED: `SF-31/3` predicted *four more commands under `cli/`*, and a SKILL has now joined them — `skills/adapter/layout.py` is the second package to re-derive both.** ⭐ **Remedy is one line on `studyforge.validate.__all__` (nine names today, neither of these), or the archive root becoming a real parameter — §6 permits it and `Layout` already takes it as a field.** ⛔ **BEFORE `SK-07`, which is the THIRD package that will read a corpus root; after it, this is a migration** | [round 28's mints](#w51-minted-sf-313-has-no-carrier-anywhere-and-a-skill-has-now-joined-cliplan-in-re-deriving-the-archive-root) |
| ⭐ **W52** | ⛔ **A `Size exception:` on a file UNDER its ceiling is read by NOTHING the build ships — `check_sizes` returns before it opens the docstring** (`W45/3`) | framework agent | ⭐ **`todo` @ `a00337b`, MINTED ROUND 28.** ⛔ **HALF DISCHARGED ALREADY: Ruling 121's commit dropped the length guard from §3c's wave-open sweep, which now prints `UNDER — STALE`. That half is a HAND FORM; this row is the SHIPPED half.** ⚠️ **`size.py`'s `if lines <= ceiling: continue` precedes `module_docstring(...)`, so the floor never opens the docstring — proved in one run by the CTO, whose planted marker printed `UNDER — STALE` from the sweep while the floor reported CLEAN.** ⛔ **TRIGGER, not a slot: exposure is `0` and MEASURED `0` at `7b5c0a9` — `W44` merged and deleted the tree's last marker, so nothing is unreadable today. The row FIRES BEFORE THE NEXT DEFERRAL IS WRITTEN.** ⭐ **INSTRUMENT: Ruling 113's `ast` sweep (`W40`'s derivation B) returns non-empty.** ⛔ **NOT `git grep` — ~~`git grep -l 'Size exception:' -- src/ tools/ tests/`~~ was this row's first instrument and it is WRONG: it returns **4** at `7b5c0a9`, all of them the checker's own package and its tests, which is the exact trap §3c warns about. `PO-28/7`.** ⛔ **The CTO routed this to `W37` and I OVERRODE the routing; the argument is in the mint** — ✅ **and the override is RATIFIED, Ruling 127: *"a queued sweep is guidance with an id"*, the CTO applying their own Ruling 117 to themselves.** ⭐ **RULING 127'S CLAUSE, LANDED ROUND 29 — THE TRIGGER FIRES ON THE SWEEP RETURNING NON-EMPTY **FOR ANY REASON**, a perfectly legal over-ceiling deferral included, because a legal deferral today is a stale marker after the split that retires it.** ⛔ **That resolves the row's apparent self-contradiction (*fires before the next deferral is written*, with an instrument needing one to exist) AND is strictly EARLIER than any split gate — it fires ONE WHOLE TASK before a split could strand anything, and does not depend on guessing which task is the next split.** ⚠️ **`[RECEIVED: CTO round 36]`, three probes at `ed8442d`: over-ceiling `425/400, over` CAUGHT · under-ceiling `6/400, UNDER — STALE` CAUGHT · marker in a COMMENT correctly IGNORED by the sweep and a FALSE POSITIVE for grep · clean tree `ROWS=0`.** ⭐ **Exposure RE-MEASURED by me at `ddddd05`: sweep → **ROWS=0**, `git grep -l 'Size exception:' -- src/` → nothing. STILL LATENT** | [round 28's mints](#w52-minted-a-size-exception-on-a-file-under-its-ceiling-is-read-by-nothing-the-build-ships) · [Ruling 127's clause](#w52-gains-ruling-127-the-trigger-fires-on-any-non-empty-sweep-and-that-is-strictly-earlier-than-any-split-gate) |
| ⭐ **W53** | ⛔ **A clause naming an instrument is not final until its author has RUN it, in both directions, and recorded both readings** (Ruling 122) | framework agent | ⭐ **`todo` @ `a00337b`, MINTED ROUND 28.** ⛔ **TWO files: `docs/conventions/review-rubric.md` (**2068**) and `docs/conventions/agent-protocol.md` (**825**) beside clause 1.** ⚠️ **The CTO bound it to their OWN office first — *an unrun instrument minted in a ruling carries more authority and gets less scrutiny than one in a branch*.** ⭐ **It is NOT `W43`'s clause 1 again: that says an acceptance condition NAMES its instrument, this says the author RUNS it — and Ruling 116 satisfied clause 1 completely while naming an instrument that was unreachable and INVERTED.** ⛔ **COLLIDES WITH `W46` and `W47` (`agent-protocol.md`) and `W34` (`review-rubric.md`) — ORDER `W46` → `W47` → `W53` → `W34`, or one developer takes the run.** ⭐ **Its worked example is Ruling 116 → `W45/2` → Ruling 121, end to end.** ⛔ **WIDENED ROUND 29, AND IT IS THE STANDING ROW FOR THE WHOLE CLASS — `PO-29/7`. Rulings 122, 123, 126 and 128 are FOUR NARROWINGS OF ONE CLAIM, and four rulings for one class is the symptom this row exists to end, so it ABSORBS them rather than the board minting `W54`. The high-water mark does NOT move.** ⭐ **RULING 126, ROWED HERE ROUND 29 — *a ruling that quantifies over a population STATES THE COMMAND that derives it.* ⚠️ It reached NO artifact (measured at `ddddd05`: 2 hits `CTO-…round35.md`, 4 `CTO-…round36.md`, nothing outside handoffs) and the CTO's own for-the-PO list OMITTED it while their `CTO-36/5` measured it. `PO-29/3`.** ⭐ **RULING 128, ROWED HERE ROUND 29 — *an instrument that reduces a population to a SCALAR prints that population IN FULL at least once, in the round that writes the clause, and the reviewer reads the MEMBERS not only the number; `\| wc -l` is added AFTER the members have been read.* ⛔ AND Ruling 123's row 1 is AMENDED by it: the EXPECTED reading is written down BEFORE the command runs.** ⛔ **WHY 123 ALONE IS NOT ENOUGH, measured by the CTO at `ed8442d` against `W52`'s broken original trigger: live **4**, planted **5**, impossible **0** — three distinct readings, ALL THREE of Ruling 123's rows satisfied, on an instrument returning non-zero for a tree with ZERO deferrals. `CTO-36/2`.** ⚠️ **PLUS `CTO-36/6`, one line and it has no other home: ⛔ **A PRE-COMMIT CHECK MAY NEVER BE A `git grep`** — `git grep` reads the INDEX, so it is blind to written-but-unstaged work. Measured by accident at `ed8442d`: an unstaged probe left the count at **4**; `git add` took it to **5**. Harmless for a REVIEW gate that runs on commits, disqualifying for anything an author runs before committing, and no document says so** | [round 28's mints](#w53-minted-ruling-122-a-clause-naming-an-instrument-is-not-final-until-its-author-has-run-it-in-both-directions-and-recorded-both-readings) · [widened round 29](#round-29-rulings-125128-all-four-into-rows-and-the-cto-asked-for-three) |
| ⛔ **W54** | ⭐ **An onboarded corpus's knowledge graph is BUILT, BRIDGED and its doc↔code census ASSERTED, by an artifact OUTSIDE `src/`** | framework agent | ⛔ **`todo` @ `8146bdb`, MINTED ROUND 30 from `SK-07/2` (CTO round 37 item 2, Ruling 129).** ⭐ **`E11`'s clause 9 was SPLIT, not waived: the R3-safe ignore file half is MET and stays in the epic; the build-and-census half is this row.** ⚠️ **`graphify` is measurably NOT in the pinned image and `src/` may not import `tools/`, so NO framework task could ever close the clause as written.** ⭐ **Its failing reading is already known — an unbridged graph returns exactly **0** doc↔code edges (`FND-02`, measured 13,583 code↔code / 767 doc↔doc / **0** doc↔code on the Java corpus)** | [round 30's mints](#w54-minted-sk-07s-graph-clause-cannot-be-met-by-any-framework-task-as-written) |
| ⛔ **W55** | ⭐ **A DECISION: is an INSTALLED `studyforge` a supported host for an onboarded corpus at all?** | framework agent | ⛔ **`todo` @ `8146bdb`, MINTED ROUND 30 from `SK-07/3`'s worse half (CTO round 37 item 3).** ⚠️ **`SK-07` writes skill stubs pointing at `../studyforge/src/studyforge/skills/<name>/SKILL.md`: resolves against a sibling CHECKOUT, points at NOTHING against an installed package, silently, exit 0.** ⭐ **The PACKAGING half is `W50`'s and that row's population was WIDENED here rather than duplicated.** ⛔ **Behind `W50`, whose glob is the precondition for the *resolves* branch** | [round 30's mints](#w55-minted-sk-07s-skill-stubs-resolve-only-against-a-checkout-and-nothing-refuses-the-installed-case-out-loud) |
| ⛔ **W56** | ⭐ **`skills/reconnaissance/proposal._choices` raises one `Uncertainty` per EXCLUDED PATH, carrying what would settle it** | framework agent | ⛔ **`todo` @ `8146bdb`, MINTED ROUND 30 from `SK-07/6` (CTO round 37 item 4).** ⚠️ **A SEAM defect: `proposal._content` returns `content.exclude` as bare path strings, `manifest.content._exclude_of` requires `path` AND a `why` of at least `MIN_WHY_CHARS`.** ⛔ **So a survey that excludes anything hands over a draft that CANNOT BE PROMOTED, and the integrator meets the refusal from a skill they were not using.** ⭐ **The question belongs where the material is OPEN** | [round 30's mints](#w56-minted-reconnaissance-never-asks-why-a-file-is-withheld-and-the-integrator-meets-the-refusal-from-a-different-skill) |
| ⛔ **W57** | ⛔ **`render/page/text.py`'s `SAFE_SCHEMES` refuses a bare same-directory relative href** | framework agent | ⛔ **`todo` @ `8146bdb`, MINTED ROUND 30 from `SF-13/1`, confirmed and WIDENED by the CTO (round 37 item 6). ⭐ PLACED **NEXT 1**.** ⛔ **13 slots, **6 dropped SILENTLY** — every same-container *next* AND *previous*, **46 %** of the between-units bar under `sibling` placement, in SHIPPED code.** ⭐ **Negative control run negatively: the identical href prefixed `./` survives.** ⚠️ **It does NOT re-open M1 (Ruling 97: the bar did not exist at `2fe56a4`).** ⛔ **WHEN: BEFORE STEP 2.3 OPENS — stronger than the CTO's *ahead of `SF-12`/`SF-14`*, because `SF-12` is already `done` and the first task that can pass `links=` is `SF-15`, whose two dependencies are both merged. `PO-30/5`.** ⭐ **Ruling 75 — it jumps `W32`, `W34`, `W35`, `W36`, `W37`, `W38`, `W41`, `W42`, `W48`, `W50`, `W51`, `W53`, on a MEASURED cost** | [round 30's mints](#w57-minted-safeschemes-refuses-a-bare-same-directory-relative-href-and-it-drops-6-of-13-navigation-slots-in-shipped-code) |
| ⛔ **W58** | ⭐ **The zero marker `` `[none]` `` standing beside a real finding is a BUILD FAILURE** | framework agent | ⛔ **`todo` @ `8146bdb`, MINTED ROUND 30 from `CTO-37/11` (item 9b).** ⭐ **REFUSED absorption into `W53` under the CTO's own ratified bound — not a condition on an author shipping a clause that names an instrument.** ⛔ **POPULATION RE-DERIVED AND BIGGER THAN THE ROUTING SAID: **25 instances in 7 documents**, ZERO legal uses, and 8 of the 25 are outside the CTO's population — **2 mine** (`PO-…round29`) and **6 on this board**.** ⛔ **AND THE READING THAT SHAPES IT: `check_markers` runs only for `task handoff` (51 of 109 documents) and `check_handoffs` never leaves `docs/tasks/handoffs/`, so the LIVE POPULATION INSIDE THE CHECKER'S REACH IS **ZERO** — the naive one-assertion remedy is a check that cannot fail. `PO-30/4`.** ⚠️ **Existing records are NOT edited (Ruling 106): the failing reading is taken against a PLANTED instance in a temporary root** | [round 30's mints](#w58-minted-the-zero-marker-standing-beside-a-real-finding-is-a-build-failure-and-today-the-checker-cannot-see-a-single-instance) |

---

---

## Scheduled — decided now, executed later

⭐ **Recorded here so they are not rediscovered at M2.** Each has an owner and a
trigger, and the trigger is an event rather than a date.

| Item | Owner | Trigger | Decision |
|---|---|---|---|
| ⭐ **SK-07 generates the corpus graph** — built, **bridged**, with the R3-safe ignore file | framework agent | ✅ **done now** — carried into `E11` this round | The highest graphify exposure converted into a generated artifact, closing an R19 hole in the same edit. ⚠️ Bridging is the part that would have been missed: a graph built by running the tool alone has **zero** doc↔code edges |
| **SK-07 must not say "submodule"** | PO | ✅ **done now** — `E11` corrected | R18's amendment reached the ruling but not the task that consumes it. The framework is a **sibling checkout at a recorded commit** |
| **Context headroom for SF-19a and SK-01/02/05/08** | PO, with CTO agreement | **M1 → M2 boundary** | Five tasks, not eighty-five. They are the discovery-shaped ones, where you do not know the name of the thing you are looking for — `query`'s weak case |
| **`Effort` field applied beyond the four named tasks** | PO | as each computation-shaped task is assigned | ✅ The field exists now (`README.md`), and `SF-07` and `FND-02` carry it. ⛔ Do not backfill eighty-four tasks; add it when a task is assigned and its shape is known |
| ⛔ **Back-triage the 23 pre-marker findings** — `FND-01` (5), `FND-02` (8), `FND-04` (10) | **PO** | ⛔ **before M1's wave opens** | The `[structural]` sweep is blind to findings filed before the marker existed — ⚠️ **including the one that motivated the mechanism** |
| **R21's three remaining open rows** *(was five, then four)* | CTO | each before its named task builds | ✅ `consuming.json` filled; ✅ **overlay `content.json` closed by SF-09** — `content_api` minted and asserted. ⛔ **ROUND 23: the discovery cache is no longer "the near one" — M2 step 2.1 IS OPEN and `SF-04` is BLOCKED on it.** ⭐ **Escalated to the CTO as this round's first item, alongside `W39`** |

---

## Cross-repo — the ISO-8583 integration track

| | |
|---|---|
| **Repository** | `ISO/` (`ISO-8583-jPOS-tutorial`) |
| **Owner** | PO-Integration |
| **Branch** | `release/studyforge-integration` |
| **Status** | `in-progress` — reconnaissance and delivery plan |
| **Closes when** | ⭐ **See *Q18 ruled*, below.** ⛔ This cell said *"a milestone-ordered backlog exists…"*, which is the **reconnaissance task's** close condition, not the track's — ⚠️ **and mistaking one for the other is why Q18 stayed open two rounds** |

### ⛔ Q18 RULED 2026-09-10 — **the track has two finish lines, and that is why it had none**

⚠️ **I carried this for two rounds as *"the track has no definition of done"*, and
that framing is what kept it open.** ⭐ **It is not one missing definition. It is
two definitions that were being asked for as one, and they close at different
milestones, are owned by different people, and are made of different material.**

| | ⭐ **The corpus's finish line** | ⭐ **The exercise's finish line** |
|---|---|---|
| **Asks** | *is this corpus a study site?* | *is this framework extensible?* |
| **Deliverable** | ⭐ **the site** | ⛔ **the findings log** (§12, §11.2) |
| **Lands** | **M4** — the reading floor | **M8** — `QA-04` |
| **Owner** | PO-Integration | ⛔ **the framework side** — §12 forbids the integrator grading their own extensibility |
| **Done when** | ISO opens offline over `file://`, narrated, navigable, read marks recorded, ⛔ **minus what the source genuinely lacks** | the findings log exists, ⛔ **every hand-edit is named as a defect in the onboarding skill**, and the framework pin is accounted for |

⛔ **ISO never enters the execution track**, so its corpus finish line is **M4 and
complete there** — ⭐ **a pass, not a shortfall** (§11.0, C5). ⚠️ **Zero exercises
is a first-class outcome and the finish line must say so in the positive**, or the
next integrator reads a shortfall into a corpus that has none.

#### ⛔ And the ruling that F18/F19/F20 forced: **`studyforge validate` green is a GATE, not a finish line**

⚠️ **`ISO-09`'s acceptance is *"`studyforge validate` green"*. Measured this
round: `NOT valid: 100 findings`, ⛔ and zero of the 100 is a corpus defect.**

⛔ **So the track's finish line currently names a state no corpus can enter, for
reasons §12 forbids the integrator to fix.** ⭐ **That is worse than an open
question, because it reads as a plan** — a task sitting at *"not done"* looks like
work outstanding, ⚠️ **when what it actually records is a framework defect wearing
a corpus's status field.**

⛔ **Ruled: a gate held shut by a framework defect is `Blocked`, not `not done`,
and it is reported as a finding rather than waited on.** ⭐ **`Blocked` already
exists and is already defined** — `../conventions/delivery-flow.md` gives it per
acceptance condition: *name which condition, why, and what will unblock it.*
⚠️ **It was defined for reviews and never applied to the track**, which is a
mechanism this project already owns not reaching one of its two halves.

⛔ **`Blocked` is not passed, and it is never a reason to delete the condition.**
⭐ **`ISO-09` keeps *"validate green"* and records it as Blocked on F18/F19/F20 by
name** — so the finish line stays honest **and** the framework defect stays
visible, ⚠️ **instead of one being traded for the other.**

#### ⭐ What this makes checkable, which is the point of ruling it

⛔ **The track closes when:**

1. ⭐ **The corpus reaches the reading floor** — offline, narrated, navigable, read
   marks — ⛔ **minus what the source genuinely lacks, stated positively.**
2. ⛔ **Every acceptance condition is `passed` or `Blocked`-with-a-named-finding.**
   ⭐ **No condition is silently dropped**, and a Blocked one names what unblocks it.
3. ⛔ **The findings log exists and is non-empty.** ⭐ **A finding count of zero
   fails this** — *an integration that reports none has not been conducted
   honestly*, and that is already the spec's sentence, not a new rule.
4. ⛔ **Every hand-edit is named as a defect in the onboarding skill** (R19).
   ⭐ **That list is what turns *"extensible"* into something with edges.**
5. **The framework pin did not move, or every commit it moved across is accounted
   for.**

⚠️ **Note what is deliberately NOT in the list: *"validate green"*.** ⭐ **It is
condition 2's subject, not condition 1's** — ⛔ **a gate the corpus must pass
through or explain, never the thing being measured.**

⭐ **Carried into `ISO-09`'s acceptance by the PO before it is assigned**, which is
what the question channel is for — ⚠️ **and it is late by exactly the two rounds I
carried it.**

---

**Confirmed by reconnaissance — record it, because it settles a scope question.**
⭐ **ISO is complete at the reading floor and never enters the execution track.**
Zero build files, zero graders, zero exercises in any of §7's three states, and
`permitted_edits` structurally `[]`. Per §11.0 and C5 that is a **pass, not a
shortfall**. Two things follow: the corpus is done at M4, and it is a **real
rather than synthetic empty-declaration case for `OPS-05`**, which is worth more
than a fixture because nobody built it to be convenient.

⚠️ **It is also a depth-1 corpus** — `levels` is `["group"]`, 38 units in three
groups (CTO ruling 1, which corrected §4's table). So depth-1 is the majority of
the four designed sources, not the exotic path.

### Questions from PO-Integration — routed, with deadlines

⭐ **These arrived as questions, not findings, and that is correct.** A question
is what the channel is for when the framework has not been built yet; a finding
is what it is for when the framework has been built and fell short.

✅ **Both are ruled and merged** — see *Resolved* above. X1 becomes `corpus.json`'s
`content` block, landing in SF-02 before it is assigned. ⭐ **X2 dissolved**: R7
governs identifiers arriving from the build environment, not identifiers that are
the material's subject matter, so the gate ships **no** payment-card pattern and
ISO needs no exemption at all.

⭐ **Both were answered before the task they land in was assigned, which is the
whole point of the deadline being a task rather than a date.** X1 in particular
was a schema change, and a schema is the one thing R9 makes expensive to alter
afterwards. ⚠️ The integration side got its answer at the cost of asking early —
recording that, because the next integrator's incentive to ask early is entirely
built out of whether this one's questions were worth asking.

### ⛔ PO-Integration round 4 — **`studyforge validate` ran, and it says `NOT valid: 100 findings`**

⭐ **The first round that could *run* the framework rather than reason about it**,
because `SF-02` and `SF-25` shipped. ⛔ **Zero of the 100 is a defect in the
corpus** — ⚠️ **all three causes are framework-side, and all three are mine.**

⛔ **They block the track's finish line by construction:** `ISO-09`'s acceptance is
*"`studyforge validate` green"*, ⚠️ **which is currently unreachable for reasons
the integrator is forbidden to fix (§12).** ⭐ **That is the seam working exactly
as designed — and it is also why these cannot wait for M2.**

| # | Finding | ⛔ **Measured** | Owner | Owed before |
|---|---|---|---|---|
| **F18** | ⛔ **`content` has two states and a real repository is mostly a third** | **141 files: 38 included, 3 excluded, ⛔ 100 UNCLASSIFIED.** ⭐ **Only 3 are *material withheld from the reader*** | **CTO** — it is a **schema** change (R9) | ⛔ **`SF-31`**, and before `SK-07` generates a manifest |
| **F19** | ⛔ **a `sibling` build makes its own corpus invalid** | **79 of 79 generated artifacts classify `UNCLASSIFIED`**; `tree` escapes only because `.studyforge` is in `SKIP_DIRS` | **CTO**, then `SF-31` | ⛔ **`SF-31`** — ⭐ **filed *before* it, deliberately** |
| **F20** | ⛔ **the framework mandates a knowledge graph the manifest cannot declare out** | **79 files, 67 content-hash names, and `exclude` refuses globs** — ⛔ **so the list cannot be WRITTEN, not merely not justified.** Plus `source_files()` ignores git, so `validate` and §11.2 disagree **by 83 files** | **CTO** (schema) + **PO** (§11.2) | ⛔ **`SF-31`** |

#### ⛔ Why F18 is the one to rule first, and it is not the biggest number

⚠️ **`README.md` can be *neither* included nor excluded, and that is a proof
rather than an inconvenience.** ⛔ **Include it and it becomes a unit that is its
own table of contents. Exclude it and the `why` must call the sole record of every
address, title and ordinal *"withheld from the reader"*.**

⭐ **X1's asymmetry is what breaks here, and X1 is mine.** ⛔ **I ruled that an
inclusion needs no justification and an exclusion does — on the premise that those
are the only two states.** ⚠️ **A real repository is mostly a third: files that are
neither material nor withheld, because they are not material at all.** ⭐ **The
missing state is *not source material*, and it is not a weakening of X1 — it is
the domain limit X1 was stated without**, which is Ruling 52 arriving against my
own rule rather than somebody else's.

⛔ **`spec §4`'s *"a file matching neither list is unclassified and `validate`
exits 1"* is the clause that has to move**, and it is a schema decision under R9,
so it is the CTO's and not mine. ⚠️ **I am recording the shape, not choosing it.**

⭐ **And the detail worth keeping, because it is the whole finding in one line:**
⛔ **writing the finding took the count from 100 to 101 — the new entry is the file
containing it.** ⚠️ **A rule that classifies its own bug report as unclassified
source material has told you its domain is wrong.**

#### ⚠️ F20's second half is mine, not the CTO's

⛔ **`source_files()` ignores git, so `studyforge validate` and §11.2's acceptance
disagree about what the corpus contains by 83 files.** ⚠️ **Two definitions of
*"the corpus"*, one in code and one in the spec** — ⭐ **which is the two-copies
diagnosis this project has made more than any other, arriving in the one place it
decides whether an acceptance is reachable.** ⛔ **§11.2 is spec text and mine.**

### ⭐ `Q5` is answered and they were still running when I ruled it

⛔ **INGEST — 38 → 55 units, `exercises` stays `false`.** ⭐ **They parse-tested
*both* branches, so the answer costs no round.** ⚠️ **The coordinator is relaying.**

⭐ **It does not change `JS-01`'s Acceptance** — checked rather than assumed:
⛔ **`JS-01` is the *Java* corpus and `Q5` is ISO's fourth container.** ⚠️ **What
they share is the rule, not the corpus**, and the rule was already carried into
`JS-01` as *the reader's obligation, not the file's shape*.

### ⏳ Still mine, carried and named rather than left implied

- ✅ **`Q18` — RULED this round**, after two carried. ⭐ **It had no answer because
  it was two questions: the corpus's finish line (M4, the site) and the exercise's
  (M8, the findings log).** ⛔ **And `validate` green is neither — it is a gate, and
  a gate a framework defect holds shut is `Blocked`, not `not done`.** See above.
- ⭐ **`F24` — corrected.** See the catalogue banner and the four board sites.

### ⛔ OWED TO PO-INTEGRATION — the round-20 relay, and the first item is now REAL

⭐ **Everything below is owed BY ME, and check 6 is the carrier that stops it
being goodwill.**

1. ⛔ **`W28` HAS MERGED (`6d65902`, in `2926dc2`), so `112 → 17` is no longer a
   prediction.** ⭐ **The framework now asks the repository what it generates
   instead of guessing**, and a declared-output directory that ignores itself is
   not enumerated at all. ⛔ **RE-MEASURE `studyforge validate` against the corpus
   at your own ref and quote the ref** — ⚠️ **and state the identity rather than
   the total (Ruling 72): `scanned = declared-output + kept`.** ⭐ **The residual
   17 is `F18` and is expected to stay red until `F18` rules; `ISO-09` is
   `Blocked` on it, not failing.**
2. ⭐ **Check 6 ran a second time and your 16 contributions are all
   dispositioned** — ⛔ **8 adopted as catalogue entries 11–18, 2 recorded as
   already carried, 2 deferred behind `F18`/`F19` with a trigger, `F2` measured as
   already landed in the spec and `E02`, and `F8` adopted as `W32` because it is a
   fixture rather than an entry.** ⚠️ **Nothing is stranded, and the refusals are
   written down beside the adoptions.**
3. ⛔ **Rulings 60 and 64 are still owed to you from round 19 and are repeated here
   rather than assumed delivered:** 60 answers `Q22` (`validate` corroborates
   `exercises` against the **archive**, not the declaration); 64 is rule-id
   stability, ⚠️ **and it has already bitten — `W27` merged, so a measurement keyed
   on `[manifest]` for a home path in `corpus.json` now reads `[personal-data]`.**
   ⭐ **Your round-4 census was keyed on rule ids, so this is not academic.**
4. ⚠️ **A correction owed in your direction, and it is small:** ⛔ **your round-4
   note says contributions 1, 5, 6, 8, 9, 10 and the `F2`/`F8` corrections are
   stranded because *"the catalogue lives in a repository this role may not write
   to"*.** ⭐ **The permission wall was never the real wall** — the catalogue's own
   header invites entries from either side — ⛔ **adoption having no owner was, and
   it now has one on a wave-open trigger.**
5. ⛔ **Still with the CTO and unchanged:** `F18` (the schema's missing third
   state, R9), `F19`, `F21` (gates `ISO-09`), `Q20` (gates `ISO-12`), `F25`
   (⚠️ **`W27` unblocked it; it did not fix it**).

---

### The channel — encoded in `../conventions/delivery-flow.md`, non-negotiable

- ⛔ **Questions and findings, never patches.** The integration side does not
  modify `studyforge` (§12).
- ⛔ **No task, context field or acceptance on that side ever cites a path inside
  the extraction source** (R20). `CS/` and `CSD/` are framework-side shorthand
  only. What an integrator needs is carried **here**.
- ⚠️ **SK-08, the delivery-planning skill, does not exist** — it is M2. So this
  plan is hand-written, and ⭐ **every step of it that SK-08 should have generated
  is a finding against SK-08** (R19). Those are this track's most valuable output
  before M2, because they arrive while SK-08 can still be shaped by them.
  ⛔ **AND UNTIL ROUND 25 THIS CLAUSE NAMED A VALUE AND NO DESTINATION** — ⚠️ six
  such findings sat undispositioned for a day (`PO-25/8`). ⭐ **THE DESTINATION IS
  `E11-skills-authoring.md`'s `SK-08` section**, and a finding against `SK-08`
  goes there on the day it is filed rather than on the day somebody sweeps.
  ⛔ **Carried by CLAIM, never by path** — R20's reason, applied in the direction
  it is usually not read: a task here may not depend on a file in a repository
  that moves.
- ⚠️ **The track still has no definition of done.** `studyforge validate`
  (SF-25) is the archive contract and lands at M1; `studyforge plan` (SF-31) is
  the placement contract and lands at M2.
- **Durable findings are distilled into the integration catalogue**, so the third
  source starts further along than the second.

---

### ⭐ R14's first clean instance, recorded because the counter-evidence was accumulating

⚠️ **This board has spent the session collecting honest evidence *against* R14's
premise** — the index absent from 31 of 33 worktrees, `query` confidently wrong
when phrased as a sentence, a graph with zero doc↔code edges, a coordinator who
hand-assembled briefings because the graph was not there to ask.

⭐ **`SF-10`'s survey is the first clean instance of the graph doing what every
`Context` budget in this plan assumes.** The structure question was **answered
before any file was opened** — 41 line-anchored symbol nodes — and the reading
that followed was **the contract surface only**: one docstring, the signatures,
the banners. ⛔ **No CodeSignal generation code, no second large module.**

⭐ **And it happened on the task where the context discipline was hardest** — a
~70k budget against an 827-line source module. ⚠️ **Recorded deliberately:** a
board that logs only the counter-evidence produces a plan nobody trusts, and the
premise is now **measured in both directions** rather than defended in one.

**Context budgets: ⭐ the analysis is in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md).** ⛔ **Two conclusions stay live:** `explain` and `path` take `--graph` and work from an index-less worktree while `query` does not, so **the index cost is paid once per repository**; and **a graph built by running the tool alone has zero doc↔code edges**, so R14's saving is a property of a graph somebody bridged.

---

## ⛔ `ONBOARDING.md` — ruled: it does not enter the repository

⚠️ **An untracked `ONBOARDING.md` sits at the repository root** (created
2026-09-09, never committed). ⭐ **It is not a team document at all** — it is a
generated onboarding template, and reading it changes the question.

**Three of its claims are false, and each is false in the expensive direction:**

| It says | The truth |
|---|---|
| *"Design + backlog; nothing implemented yet"* | ⛔ M0 closed; **1761 passed, 46 skipped** in the pinned container |
| *"composes them as submodules"* | ⛔ **R18 is amended, submodules are not used, `FND-05b` is cancelled** |
| *"Ask a teammate for clone URLs"* | ⛔ **Nothing is ever pushed to any remote.** Standing user decision, permanent |

⚠️ **And a fourth that is subtler and worse for this project specifically:** it
teaches `graphify query "..."` as *the* command. ⛔ That is the one command R14's
own amendment says holds **only when phrased as distinctive nouns**, and the one
that needs a local index — while `explain` and `path` take `--graph` and work
from a worktree that has none. ⭐ **It would teach a newcomer the exact habit that
produced the 31-of-33 defect**, on the day they arrive.

⛔ **Decision: not tracked, and not corrected into the tree.**

- ⭐ **Everything it is for is already owned by a document that is kept true** —
  `CLAUDE.md` (what this is, the hard rules, the workspace, where to start),
  `docs/conventions/`, and this board. ⛔ **A second front door is a second thing
  to keep true, and this one failed at that in four places while sitting
  untracked for a single afternoon.** That is the pointer-not-restatement rule
  again, at the scale of a whole document.
- ⛔ **It carries an embedded `<!-- INSTRUCTION FOR CLAUDE: … -->` block**
  addressed to an assistant, telling it how to conduct an onboarding
  conversation. ⚠️ **Tracking that would put instructions to agents, written by
  nobody on this project, at the repository root** — where every agent reads.
  ⭐ **That is disqualifying on its own**, independent of the false claims:
  correcting the prose would leave the block, and deleting the block leaves a
  document whose remaining content is already elsewhere.

⚠️ **What I did *not* do, deliberately: I did not delete it.** It is untracked, so
it is not repository state — it is a file in the user's working directory, and
⛔ **deleting an untracked file is irreversible and outside what a status document
should do on its own.** ⭐ **The dichotomy in the question was false: the answer is
neither "track it corrected" nor "delete it", because it is not the
repository's.** It is recorded here so it is never committed, and the one useful
thing it contains is noted: it is *evidence* that a newcomer's first document
gets written when nobody points at `CLAUDE.md` — which is a routing fact, not a
missing document.

---

**The Log — every dated entry of this project — is in [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md).** ⭐ **Moved whole, not summarised.** ⛔ **New entries are appended there, not here**: a log is a record, and this file is a claim about now.

---
