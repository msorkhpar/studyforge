# SESSION 2026-09-12 — coordinator handoff, waves 12–17

**Kind:** session log

**Release tip:** `release/m0-foundations` @ `6199164`. ⛔ **Floor and suite GREEN
after every merge of every wave; the tip was RED once, mid-wave-15, and repaired
in the same wave before anything else merged.**

⭐ **A successor reads THIS FILE, then `docs/tasks/BOARD.md`, then the newest
`PO-*` round record. Nothing else is required to resume.**

## ⛔ THE ROLE

Dispatch offices in waves, MEASURE every branch yourself, merge, repeat.
⛔ **The coordinator writes no feature code.** Four offices per wave: a REGISTER
(`wt/po`) and three developers (`wt/dev1`, `wt/dev2`, `wt/dev3`), each in a
linked worktree. ⛔ **Only the coordinator merges. An office never does.**

## ⛔ ABSOLUTE, AND THEY OVERRIDE EVERYTHING BELOW

- ⛔ **Nothing is pushed to any remote, ever.** `git remote` reads ZERO here and
  in the `narrate-service` sibling. That condition is load-bearing: it is why a
  real git identity in local commits is acceptable and ⛔ **must not be
  re-escalated or rewritten.**
- ⛔ **NO PERSONAL DATA IN ANY FILE, MESSAGE, COMMIT, BRANCH NAME OR LOG** — no
  email, name, hostname or absolute home path. Placeholders only. ⚠️ Measured
  twice this session that the sweep catches real leaks, including one an office
  typed *into the sentence describing the personal-data plant*.
- ⛔ **`ONBOARDING.md` is the user's own untracked file: never moved, deleted,
  committed — and never git-ignored**, because ignoring it removes it from the
  personal-data sweep.
- ⛔ **Offices author under Ruling 296 placeholders**, per invocation with
  `git -c user.name=… -c user.email=…`. ⚠️ **NEVER `git config user.name`** — in
  a linked worktree that writes the SHARED config and reddens the whole tree.
  The coordinator is `coordinator <coordinator@example.invalid>`.

## ⛔ THE MERGE DISCIPLINE, and it is not optional

1. ⛔ **Read `corroborate` BEFORE every merge and put its exit code and refuted
   list in the merge body** (Ruling 264(a)). ⭐ **The gate is TWO LINES now** —
   `dispatched and unnamed` (LIVE CHECKOUTS ONLY) and `unmerged branches held by
   no checkout, named by no row`. ⚠️ **Read both. The exit code does NOT move
   with either arm.**
2. ⛔ **THE REGISTER MERGES FIRST.** Measured repeatedly: at the release tip the
   264(c) arm fires on the developer branches and ONLY the register's board
   clears it. That is a measurement, not deference (Ruling 279).
3. ⛔ **MEASURE THE RELEASE TIP AFTER EVERY SINGLE MERGE**, in the pinned
   container, in ONE invocation, running the `docker/dev/check` copy inside the
   checkout being measured. ⛔ **Floor AND suite — the floor can be GREEN while
   the suite is RED at the same ref** (Ruling 78; the floor now prints a scope
   sentence saying so). ⛔ **Never leave the tip red between merges.**
4. ⛔ **Write the expected reading, with its refutation condition, BEFORE the
   command runs.** ⭐ Four expectations of mine were refuted this session and
   every refutation found something real.
5. ⛔ **A record quoting a reading is composed AFTER its capture file exists and
   is READ FROM IT** — never in the same invocation, never from memory.

## ⭐ THE STANDING PREAMBLE — recreate it in the scratchpad and put it in EVERY brief

1. ⭐ The ruling mint freeze **has expired**, but its lesson held every time:
   capacity goes to making existing rulings FINDABLE before writing new text.
2. ⛔ **NO CTO REVIEWER AND NO VERDICT, FOR ANY ROW.** Every row is
   SELF-CERTIFIED by its own office on its own green readings plus the
   coordinator's release-tip measurement. The floor and the suite are the gates.
3. **NO round record, no dispositions, no accumulator, no verdict bracket.**
   Findings are a TABLE.
4. **The register and developers may be relayed through the coordinator.**
5. ⛔ **Keep every document SHORT.**
6. ⭐ **The search path is `git grep`, `grep -rn`, `sed -n`.** ⛔ There is no
   code-graph or index tool in this project (graphify was RETIRED at the user's
   instruction) and no document may name one.
7. ⛔ **RUN EVERY GATE; DO NOT TRANSCRIBE ITS FIGURES.** Report GREEN/RED plus
   the exit code. ⭐ **ONE EXCEPTION: a figure stays when the figure IS the row's
   subject.** Ground: zero defects this session came from RUNNING an instrument;
   six came from copying a figure into a sentence.
8. ⛔ **Offices CANNOT address each other** — addresses are assigned at dispatch
   and do not exist when a brief is written. **Route through the coordinator.**
   ⚠️ Measured three times: an office told to "message X directly" cannot, and
   the work depending on the exchange silently does not happen.

## ⛔ MY DEFECTS, BY CLASS, BECAUSE A SUCCESSOR WILL REPEAT THEM OTHERWISE

- ⛔ **DISPATCHING AGAINST A ROW THAT DOES NOT EXIST.** Seven recorded instances.
  Minting an id first was the wrong fix at the wrong level: ⭐ **AN ID ALONE IS A
  LABEL ON AN EMPTY BOX — the row must EXIST and CARRY ITS ACCEPTANCE before an
  office is dispatched against it.** Twice I told an office to "cite the row as
  the authority" when the row was unreachable from every branch head.
- ⛔ **WRITING A SURFACE THAT CANNOT CONTAIN THE ROW.** Charged four times.
  ⭐ **Name the CONTRACTS a row must satisfy and let the file list follow.**
  Always give the office the escape hatch: take the file, record a finding.
- ⛔ **STATING A POPULATION I HAD NOT MEASURED.** The worst: I told an office
  `studyforge plan` enumerates every path a build creates. It also enumerates
  two it does NOT, including `archive/` — ⚠️ **a reader of that sentence alone
  would have let a rebuild overwrite the corpus's own archive.**
- ⛔ **A FILTER THAT RETURNS NOTHING IS NOT A MEASUREMENT.** Five instances, four
  of them mine — a case-sensitive grep, a folded line, a wrong population.
  ⭐ **Read the region.**

## ⭐ THE FAMILY OF DEFECTS THIS PROJECT KEEPS PRODUCING — state it in briefs

⛔ **AN INSTRUMENT EXITING 0 HAS TOLD YOU NOTHING FAILED, NOT THAT EVERYTHING WAS
CHECKED.** An arm that stands down silently, or fires without gating, is
indistinguishable from an arm that passed. ⭐ **Six independent instances in six
waves**, and the cure was identical every time: **make the population size a
MOVED EXIT CODE or a PRINTED COUNT, never an assumption.**

⭐ **THE HOUSE STANDARD THAT CAME OUT OF IT, and offices now do it unprompted:**
⛔ **PLANT EVERY CONTROL.** A control that has only ever run green has not been
shown capable of red. ⚠️ **A plant that SURVIVES is worth more than ten that
die** — three waves running, a survivor exposed a belief its author had
documented confidently and wrongly. ⭐ And a clean personal-data sweep is quoted
only when it has ALSO been shown to fire on a planted string.

## ⭐ THE USER'S THREE DECISIONS — product promises, not preferences

⛔ **They live in `docs/tasks/E09-delivery.md` § "W202 — WHAT A BUILD IS". CITE
that; do not re-derive it.** All six items are answered there.

1. **Where a build writes** — ⛔ NOWHERE by default; `--out` stays REQUIRED.
2. **A rebuild** — ⛔ OVERWRITES ONLY WHAT THE BUILD ITSELF WROTE, refusing any
   other path BY NAME. ⭐ **The R3 refinement this carries is in the SPEC at R3:
   R3 distinguishes the build's own prior output from the user's material.**
   ⚠️ **The discrimination is BY PATH, never by content** — a hand-edited page is
   inside the footprint and IS replaced. The user was told.
3. **A corpus with no narration record** — ⛔ no player and NO NOTICE (a prose
   corpus is COMPLETE, not short); a player when a record exists; ⭐ **and the
   page NAMES THE GAP only when the record PROMISED a clip that is not on disk.**
4. **Item 3, the register's:** ⛔ **A BUILD NEVER SYNTHESISES.** Synthesis is its
   own verb, `studyforge narrate`. The record and clips are INPUTS. Order is
   narrate → build, and a narrate AFTER a build is answered by a REBUILD.

## ⛔ THE NEXT ACTION — wave 18, composed and grounded

⭐ **`SF-42` — `studyforge narrate`, and it is the critical path.** ⛔ `M3` has
ALL FIVE STEPS CLOSED and STILL CANNOT CLOSE, because its *Done when* is
*"narration is generated"* and ⛔ **`narrate.synth` has been a library with NO
CALLER since the day it landed.** Not a missing page state — **a missing ACT.**
⭐ **`SF-42` is the first thing in this project that will put a clip file on
disk.**

⚠️ **Everything needed for it already exists and is merged:** the narration
record (`narrate/synth/`), the join (`narrate/playable.py`, keyed on the SPEECH
ID and never the position), the renderer's three states (`SF-38`), and the
sibling service, which was **proved against a real engine** — see
`docs/tasks/handoffs/NS-07.md` and `docs/engine-measurement.md` in the
`narrate-service` sibling.

⭐ **The other rows worth the remaining slots:** `W211` (⛔ the pinned image
cannot install this package — no setuptools, no network — so every
installed-command acceptance in the plan is HOST-ONLY until it lands),
`SF-38`'s BUILD half (the renderer has the three states; `generate/` still
renders SILENT), and `W210` (fenced all session; the media policy spelled twice).

## ⚠️ OPEN, UNOWNED, AND NOT TO BE FORGOTTEN

- ⛔ **The suite writes OUTSIDE the checkout.** At uid 0 in the pinned image,
  `/home` gains an entry during the emission tests; the default uid fails on
  permissions, which is the only reason nobody has seen it. The tree-state net
  is repo-scoped BY CONSTRUCTION and does not reach it.
- **`W187/1`** — the narration record grows without bound; nothing prunes, and
  unpruned clips count against a build's own media ceiling.
- **`SF-37/2`** — §9 inverted: a build can FIND archive media and no adapter is
  instructed to PRODUCE it.
- **`W202` item 5** — where the build package finally homes; `generate/` was
  ratified on merit, but `SF-43/2` found a circular import that is evidence
  against it.

## ⭐ WHAT THE PROJECT CAN ACTUALLY DO NOW, measured rather than claimed

`studyforge build <corpus> --out <dir>` is an installed command. It writes an
index, container pages, unit pages, media and the shared asset bundle; a second
run REPLACES only what it wrote and REFUSES anything else by name. ⭐ **On the
`depth1` fixture the built site has NO dangling reference of any kind.**
⛔ **What it cannot do is narrate: nothing has ever run synthesis from inside
this repository. That is `SF-42`.**
