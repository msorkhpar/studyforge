# SESSION-2026-09-10b — coordinator handoff

**Kind:** session log

**Release tip:** `release/m0-foundations` @ `641f682` — **4343 passed, 63 skipped**,
floor clean, index fresh at `641f682b`, 354 pointers / 278 files / 0 unresolved,
ruff clean at 692 (MAIN; one lower in a clean worktree — see ⛔ below).
**Zero unmerged branches. Zero files over R11's ceiling. Zero size deferrals.**

**Since `e5bcc85`:** 304 commits, 128 merges, 565 files, **+90,842 / −2,191**.

---

## ⛔ Read this file, then the board — and the board is now 245 lines

`docs/tasks/BOARD.md` was **8,545 lines / 753 KB** and is **245 lines / 24 KB**.
It is a **register**: identity, naming, owner, state, pointer. Nothing else.

| If you want | Read |
|---|---|
| what is open, who owns it, its state | **`BOARD.md`, and only that** |
| why one row exists | `docs/tasks/rows/<ID>.md` — **opened only if you are taking it** |
| a closed row, or any round's reasoning | `BOARD-ARCHIVE.md` — appended to, never edited |
| what a task **is** (`Owns`, `Depends on`, Acceptance) | the epic, `E00`…`E13`. ⛔ **Never the board** |
| which step a task is in | `README.md`. ⛔ **Membership is not state** |
| how the board may grow | `docs/conventions/board.md` + the `board:` line the floor prints |

⭐ **The orientation cost fell from ~2,439 to ~77 tokens per task id indexed.**
⛔ **Do not read `BOARD-ARCHIVE.md` (932 KB) and do not read the CTO chain.**
The rulings **index** is in `handoffs/CTO-2026-09-09-round17.md`; the tail is in
each round's own record.

---

## Where the work is

**M0, M1, M2 step 2.1 (`a00337b`) and step 2.2 (`ce80120`) are CLOSED.**
**M2 step 2.3 is OPEN and every row in it has merged** — `SF-27` at `6177738`,
`SF-14` at `ffb2411`. ⛔ **The close was not taken**, because PO round 36 was
scope-limited out of the board while the restructure was in review.

### ⛔ First thing next session — the PO's hold is fully lifted
1. **Close M2 step 2.3** under Ruling 97: measurements at **one named ref**, no
   row inherited. ⚠️ The board's step-2.3 cell and its **In flight** table are
   both stale (they still name `SF-14` as remaining, and list `W14`/`W18`/`W27`
   with no checkout) — expected, recorded, and the PO's first edit.
2. **Ruling 173's five rows** — `SF-19b` (`E05:97`), `SK-03` (`E11:571`),
   `SK-04` (`E11:594`), `TC-00` (`E12:64`), and `SK-01` (`E11:167`) which takes
   **Ruling 166** as a closed row. ⛔ **`SF-03` and `QA-04` are NOT rows** — each
   is a clause inside a task that already has an id.
3. **Rulings 174 and 176**, held all round because their artifacts were held.
4. **Rulings 182, 183, 184's remedies**, and one row for `CTO-47/3`/`4`/`5`.
5. **`SF-34` is dispatchable** and now carries region 6 plus an Acceptance clause
   naming `pageassets.SURFACE_HOOKS` — ⛔ it reads as complete either way, so the
   clause is the only thing stopping it being built against the wrong spelling.

---

## ⚠️ What will bite you

1. ⛔ **`grep -c '^SKIPPED'` reads 29. The answer is 63.** Under plain `-q` it
   reads **0**. Three offices hit this (Ruling 142, 170(b)).
2. ⛔ **`docker/dev/check` derives its root from where the SCRIPT sits**, so a
   base and a merge can agree **for the wrong reason**. ⭐ Always:
   `docker/dev/check sh -c 'git rev-parse HEAD; python3 -m pytest -q'` (Ruling 172).
3. ⛔ **MAIN reads one higher than a clean worktree on two denominators** — the
   user's untracked `ONBOARDING.md`. **Four agents hit it in one round.** It is
   the user's file: ⛔ never moved, deleted or committed. **Name the checkout by
   its ROLE for every count** (Ruling 147).
4. ⚠️ **`$?` after a pipeline reads the pipeline's last command**, and
   `git rev-parse` echoes an unknown sha back. Use `git cat-file -e <ref>^{commit}`.
5. ⚠️ **ruff formats Python fences inside Markdown**, and can report a reformat
   **while `tools.quality` exits 0** — neither a floor pass nor a floor failure.
6. ⛔ **`.scratch/` holds artifacts, never a checkout** (Ruling 153). A nested
   checkout there reddens the suite while `git status --porcelain` prints nothing.
7. ⚠️ **The index goes stale after any `docs/` or `src/` merge.** Rebuild in MAIN:
   `graphify update . && python3 -m tools.knowledge bridge`. It went stale three
   times this session because I stopped doing it on a premise that had expired.

---

## ⭐ The rulings that changed how work is measured

- **115** — a finding states, **per claim**, whether it was *measured* or
  *received*, **and from whom**. ⛔ Minted because I injected a claim into a
  developer's handoff and then quoted it back to the reviewer as corroboration.
- **123 / 128 / 140** — an instrument owes **three readings**: live, **planted**
  (adversarial to the *search term*, not the subject), and **impossible** (a
  reading that must *differ* from the pass). **Print the population before any
  scalar, with the expected reading written down first.** ⛔ `| wc -l` conceals
  exactly what you need to see.
- **146 / 162 / 131** — a sweep asserts its **row count** against a population
  declared before the loop, records each row's **failure reason** (a `NameError`
  row never ran the code), and cleans the **tree**, not just the caches.
- **147** — **name the checkout by its role for every count you quote.**
- **172** — print the ref and the number from **one** invocation.
- **177 / 180 / 182** — a migration is validated over **content**, at a **ref**,
  and *both* sides of the equality are refs. ⛔ A test that forbids what the
  branch's own contract prescribes is a finding **against the test**.
- **183** — a bound removed because its subject became editable is replaced by a
  **notice**, never by nothing.
- **161 / 150 / 136** — the fix for an unmaintainable copy is **removing the
  subject**. `CLAUDE.md` now carries **no live state at all**.

⭐ **The one line to carry:** *an instrument that returns the reading you already
expect returns no disagreement either.* Four separate defects this session were
found only because somebody wrote the expected number down **before** running.

---

## ⛔ My own defects, so the next coordinator does not repeat them

1. **I dispatched two CTOs onto one branch.** I resumed a retired reviewer and
   then spawned a fresh one for the same work. ⭐ **A retired agent that still
   answers is not a live agent.**
2. **I laundered a claim.** I told a developer `SF-36` relocated a constant
   block, they recorded it as a finding, and I cited their finding back to the
   reviewer as independent support. It never happened. → **Ruling 115.**
3. **I pinned stale bases repeatedly** — four agents corrected me. → **Ruling 147.**
4. **I relayed a blocker that had already been discharged.** Had the PO carried
   my brief instead of measuring it, step 2.3's last row would have sat blocked.
5. **I gave every agent the same scratch directory**, and two sweeps truncated
   each other's logs. → **Ruling 153.**
6. **I relayed *"all 79 ids registered for the first time"* unchecked.** The
   completeness half had landed a round earlier; only the **form** changed.

⭐ **The generalisation the CTO gave for the whole family, and it still holds:**
*a reading taken from a proxy, quoted as a property of the thing.*

---

## On the two supervising roles

A **Board Architect** was created by the user this session, standing over the PO
on board **structure** only. It took **three review rounds** and was right to:
round one lost text to a `|` inside a code span, round two's migration test
**forbade two of the four actions its own contract prescribes**, and round three
disclosed the price of the fix rather than letting it be found.

⭐ **It also refused half the instruction it was given**, on measurement: *a
summary of a row is a second copy of its argument and will go stale.* What
shipped is a **complete index with addresses**, not condensation. ⛔ **That
refusal was ratified by the CTO and the numbers were checked before it was put
to the user** — which is the only reason the correction in §6 above was caught.
