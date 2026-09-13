# Board — live state

⛔ **This file is a REGISTER, and a register carries identity, a naming, an
owner, a state and a pointer — nothing else.** ⭐ **Every argument lives in
exactly one other place**, and this file carries its address rather than a
second copy of it.

| If you want | Read |
|---|---|
| what is open, who owns it, what state it is in | ⭐ **this file, and only this file** |
| why one row exists, and what would settle it | `rows/<ID>.md` — one file per live row, opened only if you are taking it |
| what a closed row was, and every round's reasoning | [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md) — the record, appended to and never edited |
| what a task *is* (its definition, `Owns`, `Depends on`, Acceptance) | the epic, `E00`…`E13`. ⛔ **Never this file** |
| which step a task belongs to | [`README.md`](README.md). ⛔ **Membership is not state** |
| how this file is allowed to grow, and what a cell may carry | [`../conventions/board.md`](../conventions/board.md) — the structural contract, and the check that enforces it |
| how a state is allowed to change | [`../conventions/delivery-flow.md`](../conventions/delivery-flow.md) |

⛔ **RULING 349 IS BEING APPLIED TO THIS FILE, ONE VERIFIED PARAGRAPH AT A TIME, AND
[`W173`](rows/W173.md) OWNS THE SWEEP** — ⭐ **a rule removed here is one whose convention
already carries it, named in that round's record; a rule no convention carries STAYS until
one does.**

---

## Milestones

⭐ **State only.**

| Milestone | State | Ref | The close run |
|---|---|---|---|
| **M0** — foundations | ✅ CLOSED | — | [record](BOARD-ARCHIVE.md#m0-foundations) |
| **M1** — the framework stands up | ✅ CLOSED | `2fe56a4` | [record](BOARD-ARCHIVE.md#m1s-close-run-at-2fe56a4-all-nine-true-at-one-ref-and-rows-18-were-re-taken-not-inherited) |
| **M2** — a corpus is readable | ✅ CLOSED | `2d0cfe7` | [record](BOARD-ARCHIVE.md#m2s-close-run-at-2d0cfe7-nine-rows-the-fifteen-task-merges-re-derived-and-the-two-gaps-are-named-rather-than-absent) |
| **M2 step 2.1** | ✅ CLOSED | `a00337b` | [record](BOARD-ARCHIVE.md#m2-step-21s-close-run-at-a00337b-all-five-re-taken-and-the-ref-moved-twice-underneath-it) |
| **M2 step 2.2** | ✅ CLOSED | `ce80120` | [record](BOARD-ARCHIVE.md#m2-step-22s-close-run-at-ce80120-all-four-re-taken-and-the-four-merges-derived-rather-than-received) |
| **M2 step 2.3** | ✅ CLOSED | `798956c` | [record](BOARD-ARCHIVE.md#m2-step-23s-close-run-at-798956c-both-rows-re-taken-the-two-merges-derived-and-the-negative-control-is-a-synthesised-commit-because-no-branch-in-this-repository-is-unmerged) |
| **M2 step 2.4** | ✅ CLOSED | `2d0cfe7` | [record](BOARD-ARCHIVE.md#m2-step-24s-close-run-at-2d0cfe7-all-four-rows-re-taken-the-merges-derived-and-ruling-204-is-what-makes-it-clean) |
| **M3** — it speaks | ✅ CLOSED | `1ede082` | [record](BOARD-ARCHIVE.md#m3-step-36-and-m3-close-at-1ede082) |
| **M3 step 3.1** | ✅ CLOSED | `7420c34` | [record](BOARD-ARCHIVE.md#m3-step-31s-close-run-at-7420c34-both-merges-re-derived-on-the-first-parent-chain-and-nothing-inherited) |
| **M3 step 3.2** | ✅ CLOSED | `7a7a178` | [record](BOARD-ARCHIVE.md#m3-step-32s-close-run-at-7a7a178-both-merges-re-derived-and-ruling-199s-predicate-c-run-for-each) |
| **M3 step 3.3** | ✅ CLOSED | `bec9d5c` | [record](BOARD-ARCHIVE.md#m3-step-33s-close-run-at-bec9d5c) |
| **M3 step 3.4** | ✅ CLOSED | `abee048` | [record](BOARD-ARCHIVE.md#m3-steps-34-and-35-close-at-abee048-and-m3-itself-does-not) |
| **M3 step 3.5** | ✅ CLOSED | `abee048` | [record](BOARD-ARCHIVE.md#m3-steps-34-and-35-close-at-abee048-and-m3-itself-does-not) |
| **M3 step 3.6** | ✅ CLOSED | `1ede082` | [record](BOARD-ARCHIVE.md#m3-step-36-and-m3-close-at-1ede082) |
| **M4** — it is served | ✅ CLOSED | `4d3c742` | [record](BOARD-ARCHIVE.md#po-round-74-m4-closed-at-4d3c742-and-the-order-after-it-is-m6-m8-m5-m7-then-m9-user-direction) |
| **M4 step 4.1** | ✅ CLOSED | `77e47e5` | [record](BOARD-ARCHIVE.md#po-round-67-wave-20-closed-in-part-steps-41-and-42-closed-sk-03s-edge-corrected-three-mints) |
| **M4 step 4.2** | ✅ CLOSED | `171366c` | [record](BOARD-ARCHIVE.md#po-round-67-wave-20-closed-in-part-steps-41-and-42-closed-sk-03s-edge-corrected-three-mints) |
| **M4 step 4.3** | ✅ CLOSED | `a55303f` | [record](BOARD-ARCHIVE.md#po-round-69-step-43-closed-sf-19b-w105-and-w225-closed-two-mints) |
| **M4 step 4.4** | ✅ CLOSED | `4d3c742` | [record](BOARD-ARCHIVE.md#po-round-74-m4-closed-at-4d3c742-and-the-order-after-it-is-m6-m8-m5-m7-then-m9-user-direction) |
| **M6** — the first corpus reads (`ISO-8583`), next by the user's order | ⏳ **OPEN** — its rows are the ISO track's; ⛔ **no office is dispatched into that repository without the user** | — | [the open](BOARD-ARCHIVE.md#po-round-74-m4-closed-at-4d3c742-and-the-order-after-it-is-m6-m8-m5-m7-then-m9-user-direction) |

⛔ **Ruling 97 binds every one of those refs** ([`../conventions/board.md`](../conventions/board.md)).

## In flight

⛔ **A commits-ahead cell is a READING with an as-of, not a state** (`PO-30/2`); the FORM is
Ruling 246's: `n @ <branch tip>`, `<branch> @ <checkout>`. ⛔ **Ruling 171: `git worktree list`
PRIMARY.** ⭐ **[Why](BOARD-ARCHIVE.md#po-round-44-w98-closed-w126-and-w127-minted-w124-amended-not-re-minted-and-the-refuted-sibling-premise-out-of-claudemd)** (`PO-44/14`–`PO-44/17`).

<!-- inflight -->
| Row | Owner | Checkout | Commits ahead | State |
|---|---|---|---|---|
| `W135` | Developer 3 | `fix/W135-citation-pointer-rule` @ `wt/dev3` | 3 @ `e118372` | in-progress |
| `W150` | Developer 2 | `fix/W150-citation-path-resolves` @ `wt/dev2` | 0 @ `79db35b` | in-progress |
| `W237` | Developer 1 | `fix/W237-process-tests-one-reader` @ `wt/dev1` | 0 @ `0dd9fa4` | in-progress |
<!-- /inflight -->

⭐ **EMPTY IS A STATE** (`W111`, `W147`).
⛔ **AN EPIC TASK IS ADMITTED HERE AND IS NOT A `W` ROW** — ⭐ **`NS-01/2`, MEASURED** ([the reading](BOARD-ARCHIVE.md#wave-7s-dispatch-and-the-observation-table-measured-against-a-non-w-row-rather-than-argued-about)); ⚠️ **its detail file is the EPIC, `W161` the residual.**

⛔ **`corroborate` corroborates the ROW and NEVER the CELL; its exit code is DISCLOSURE at a
merge and a GATE at `git rev-parse <register branch>`** (Ruling 279). ⚠️ **Ruling 264's arm is
printed UNFOLDED (Ruling 348), so it fires while the command exits `0`: read it WHOLE.**
⭐ **A MERGED row stays NAMED here until its worktree is torn down: that arm fires on an
absorbed branch no row names.**

⚠️ **ONE BRANCH CAN CARRY ROWS WITH DIFFERENT OUTCOMES** (Ruling 218), ⛔ **so a cell may name
SEVERAL ROW IDS.**

⭐ **Office checkouts are board DATA, declared below and read by `corroborate`** ([`W125`](BOARD-ARCHIVE.md#w125-the-in-flight-table-is-asserted-and-generating-it-naively-leaves-corroborate-asserting-git-against-itself)).
⛔ **`W144`, `W235` LEFT at `7b2e5d0`, `4d3c742`** (Ruling 199). ⭐ **A CARRIER IS NAMED ON CONFIRMATION** (`PO-61/4`); ⛔ **Ruling 189(c) reads the branch a ROW CLAIMS.**
⭐ **`W150`, `W237` NAMED, CONFIRMED, [ratified](BOARD-ARCHIVE.md#po-round-74-m4-closed-at-4d3c742-and-the-order-after-it-is-m6-m8-m5-m7-then-m9-user-direction); `W135` kept.** ⚠️ **[`W191`](rows/W191.md) unassigned.**

<!-- offices -->
| Checkout |
|---|
| `wt/po` |
| `wt/cto` |
<!-- /offices -->

## Next rows — placed, not yet taken

⭐ **The argument for each placement is in the round record; this table is the
outcome.** ⛔ **Ruling 75 governs a row that jumps an older one, and it is
[`../conventions/delivery-flow.md`](../conventions/delivery-flow.md)'s.**

| Order | Row | Why it is here | Placed |
|---|---|---|---|
| 3 | `W90` | ⛔ **a named gap of `M4`'s close, not a gate** — it jumps nobody older | [72](BOARD-ARCHIVE.md#po-round-72-sk-06-held-open-on-sk-063-so-step-44-and-m4-do-not-close) |
| 5 | `W118` | ⭐ **round 42's remaining mint, jumping nobody** | round 42 |
| 8 | `W136` | ⭐ **the exposure is LATENT, and it jumps nobody** — the reading is the row's | round 47 |
| 9 | `W141` | ⭐ **a stated count nothing re-derives, and it jumps nobody** — `W134/5` | round 49 |
| 11 | `W149`, `W151`, `W153`, `W154`, `W156` | ⭐ **each jumps nobody** | round 51 |
| 12 | `W158`–`W160` | ⭐ **each jumps nobody** | round 52 |
| 13 | `W161`–`W165`, `W168`, `W169`, `W171` | ⭐ **each jumps nobody** | round 54 |
| 15 | `W173` | ⭐ **round 56's mint, jumping nobody** | round 56 |
| 16 | `W174`, `W175` | ⭐ **round 56's re-take mints** | round 56 |
| 17 | `W176`–`W181` | ⭐ **round 57's six mints, jumping nobody** | round 57 |
| 18 | `W184`, `W186` | ⭐ **round 58's wave-12 mints, jump nobody** | 58 |
| 19 | `W192`, `W194` | ⭐ **round 60's mints, jumping nobody** | 60 |
| 22 | `W198`–`W201` | ⭐ **round 60's `E09`-scoping mints, jumping nobody** | 60 |
| 24 | `W204` | ⭐ **round 60's mint, jumping nobody** | 60 |
| 25 | `W205` | ⛔ **NOT DISPATCHABLE — it is a RULING and the freeze is in force; minted so the case is not lost** | 60 |
| 28 | `W210` | ⭐ **both spellings are correct today, so it jumps nobody** — Ruling 285(b)'s ground | 62 |
| 29 | `W214` | ⛔ **§9 INVERTED — a build reads media no adapter is told to write, and the second source is what §12 rests on** | 63 |
| 31 | `W215`, `W216` | ⭐ **round 63's remaining mints, each jumping nobody** | 63 |
| 32 | `W219`–`W223` | ⭐ **round 65's mints, each jumping nobody** | 65 |
| 33 | `W226` | ⭐ **its held half is disclosed on every run, so it jumps nobody** | 66 |
| 34 | `W227`–`W229` | ⭐ **round 67's mints, each jumping nobody** | 67 |
| 35 | `W231` | ⭐ **round 69's mint, jumping nobody** — ⛔ **one owner with `W117` in flight, which holds `docs/conventions/`** | 69 |
| 36 | `W232` | ⭐ **round 70's mints, each jumping nobody** | [70](BOARD-ARCHIVE.md#po-round-70-w106-w107-and-sk-03-closed-w230-sk-06-and-w103-named-two-mints) |
| 37 | `W234` | ⭐ **round 71's mint, jumping nobody** | [71](BOARD-ARCHIVE.md#po-round-71-w230-and-w103-closed-w109-w116-and-w117-named-one-mint) |
| 38 | `W236` | ⭐ **round 72's mint, jumping nobody** | [72](BOARD-ARCHIVE.md#po-round-72-sk-06-held-open-on-sk-063-so-step-44-and-m4-do-not-close) |
| 39 | `W238` | ⭐ **round 74's mint, jumping nobody** | [74](BOARD-ARCHIVE.md#po-round-74-m4-closed-at-4d3c742-and-the-order-after-it-is-m6-m8-m5-m7-then-m9-user-direction) |

⛔ **THE CELLS ARE KEYED BY ROW ID AND NOT BY ORDINAL** — ⭐ **an id resolves; a position does
not.** ⛔ **A cell here carries no census of the jumps, no COUNT, no measurement and no
PREDICTION** (243(c)) — ⭐ **only the row's own sentence decides which of Ruling 281's three
classes it is.** ⭐ **[The reading, with its ref](BOARD-ARCHIVE.md#po-round-51-the-registers-whole-share-measured-as-a-symptom-the-open-step-found-to-admit-exactly-one-row-and-that-rows-deferral-traced-to-an-r18-decision-that-had-already-landed-before-it-was-written).**

⚠️ **`W160` writes `docs/tasks/rows/`, and a REGISTER round writes it too: never beside one** (check 4's sub-step). ⛔ **`W135`,
`W136`, `W141`, `W149`, `W153`, `W154`, `W157`, `W159`, `W160`, `W161`, `W164`, `W165`,
`W168`, `W169`, `W171`, `W179`, `W180`, `W229` and [`W231`](rows/W231.md) name `docs/conventions/` — ⭐ ONE
owner or two waves.**
⛔ **`W150`+`W151` write `tools/quality/citations.py`; `W158`, `W162`, `W163` name `docker/dev/`; `W183`+`W184` write `E04`; `W153`+`W176` DECLARE
`board/corroborate.py` — ONE OWNER or two waves for each set.** ⚠️ **[`W190`](BOARD-ARCHIVE.md#w190-corroborates-dispatched-and-unnamed-arm-has-a-population-of-checkouts-so-a-branch-carrying-work-is-invisible-to-it-whenever-its-office-cleans-up-after-itself)
declares `board/unclaimed.py`, which is where `W132`'s split actually MOVED the arm all three
name — ⛔ so `W153`'s and `W176`'s declared surfaces are stale against their own subject.** ⛔ **`W173`+`W159` write `board/bounds.py` (whose size message reads `register ids`, `W144/4`), and `W173`
writes `docs/tasks/BOARD.md`, which a REGISTER round writes too.** ⛔ **[`W207`](rows/W207.md) joins the `E04` set; [`W216`](rows/W216.md)+[`W221`](rows/W221.md) both name the test harness, and [`W222`](rows/W222.md)+[`W223`](rows/W223.md)+[`W226`](rows/W226.md) all write `narrate/` — ONE OWNER or two waves; and [`W214`](rows/W214.md)+[`W215`](rows/W215.md) are two ends of ONE seam, so a taker of either reads the other.** ⚠️ **This paragraph ranges
over DECLARED surfaces, so a row declaring none is asserted for or is invisible** (Ruling 331,
`PO-54/3`). ⭐ **The `pointers.py` and `handoffs/` sets left it when `W35`, `W148` and `W172`
closed; the `cli/plan/` and emission-harness pairs when `W213` and `W217` did, and `W224`+`W210` when `W224` did; `W225` left the `docker/dev/` set at its close, and `W144` the `bounds.py` set.**

## The register — every `W` row

⛔ **One row per id, and the id space has exactly one minter.** ⭐ **A row's
NAMING is here and nowhere else; its ARGUMENT is behind the pointer and nowhere
else.**

<!-- register -->
| # | Row | Owner | State | Detail |
|---|---|---|---|---|
| W1 | `require_slug`/`require_ordinal` format `{value!r}`, so every caller inherits an R7 echo | Developer 2 | ✅ done — `f569d0e` | [`rows/W1.md`](rows/W1.md) |
| W2 | The behavioural §1f check — poison a path into each string parameter | Developer 2 | ✅ done — `f569d0e` | [`rows/W2.md`](rows/W2.md) |
| W3 | The fixture whose SVG, `alt` text and lesson prose describe three different pictures | Developer 2 | ✅ done | [`rows/W3.md`](rows/W3.md) |
| W4 | `handoffs/SF-05.md` still describes a constant the hotfix removed | PO | ✅ done | [`rows/W4.md`](rows/W4.md) |
| W5 | `SF-10`'s port is re-priced — the file's line count is not the task's | SF-10 | routed — folded into `SF-10` | [`rows/W5.md`](rows/W5.md) |
| W6 | The R7 exception-text check — an `{exc}` interpolation re-emits what the inner refusal withheld | Developer 2 | ✅ done — `f569d0e` | [`rows/W6.md`](rows/W6.md) |
| W7 | `corpus.json` is not gated at all, so a home path in the manifest title validates green | Developer 2 | ✅ done — `f569d0e` | [`rows/W7.md`](rows/W7.md) |
| W8 | The dev image has no JS runtime, so a block of tests can only run off-image | Developer 1 | ✅ done — `dc4686c` | [`rows/W8.md`](rows/W8.md) |
| W9 | The markup contract has one side written — `SF-12` reviews the class names as its first act | SF-12 | ✅ done — landed in `E03` | [`rows/W9.md`](rows/W9.md) |
| W10 | Palette tokens with no painter, as a named self-retiring list | PO → E04, E08 | `todo` — before E04 / E08 are authored | [`rows/W10.md`](rows/W10.md) |
| W11 | `api` is a generic field name and the tree guard would flag an unrelated reader | accepted | accepted — cost named | [`rows/W11.md`](rows/W11.md) |
| W12 | The extraction source's `naming.py` docstring disagrees with its own tree | accepted → E11 | accepted — cost named → E11's catalogue | [`rows/W12.md`](rows/W12.md) |
| W13 | Two copies of the personal-data gate that already disagree | Developer 2 | ✅ done — `f569d0e` | [`rows/W13.md`](rows/W13.md) |
| W14 | The two missing invalid fixtures on `FND-04`'s surface, and they are one task | Developer 1 | ✅ done — `ac4ed55` | [`rows/W14.md`](rows/W14.md) |
| W15 | Tooling wrote to a source repository's root ignore file | PO → OPS-05, SK-07 | `todo` — before any adapter runs against a real source | [`rows/W15.md`](rows/W15.md) |
| W16 | The spec's canonical examples are hand-maintained copies of contracts the code owns | PO / Developer 2 | `todo` — the spec half landed; the two one-way checks are unassigned | [`rows/W16.md`](rows/W16.md) |
| W17 + W19 | One spelling of *describe a value without reproducing it*, and the remaining `{value!r}` sites | Developer 2 | `todo` — after `FND-07` | [`rows/W17.md`](rows/W17.md) |
| W18 | `user` + `authoritative` is accepted, so a reader's grader may declare itself the source's own | Developer 1 | ✅ done — `ac4ed55` | [`rows/W18.md`](rows/W18.md) |
| W20 | The repository-wide §7c check, and its migration in the same commit | Developer 2 | ✅ done | [`rows/W20.md`](rows/W20.md) |
| W21 | Nothing checks for dangling pointers after a docs move | Developer 2 | `todo` — with `FND-08` | [`rows/W21.md`](rows/W21.md) |
| W22 | Finding 44 is owed to the integration catalogue, not to `SK-01` | PO | ✅ done | [`rows/W22.md`](rows/W22.md) |
| W23 | Two personal-data shapes passed the gate clean | Developer 2 | ✅ done — `d178665` | [`rows/W23.md`](rows/W23.md) |
| W24 | A derived-set assertion asserts inhabitation, or it is born vacuous | PO | ✅ done | [`rows/W24.md`](rows/W24.md) |
| W25 | `tools/quality` gains a handoff check, because the six sections are a contract | Developer 2 | ✅ done — `2a272a5` | [`rows/W25.md`](rows/W25.md) |
| W26 | `W7`'s reader tell resolves the name's origin, not its spelling | Developer 2 | `todo` — not started | [`rows/W26.md`](rows/W26.md) |
| W27 | An R7 refusal is never translated into a package's error family | Developer 2 | ✅ done — `5c6c883` | [`rows/W27.md`](rows/W27.md) |
| W28 | `source_files()` respects the repository's own ignore declaration | Developer 1 | ✅ done — `6d65902` | [`rows/W28.md`](rows/W28.md) |
| W29 | One constant naming the three gated trees | Developer 2 | ✅ done — `4f2fbf8` | [`rows/W29.md`](rows/W29.md) |
| W30 | `PYTHONPYCACHEPREFIX` in the dev image — isolation that is structural | framework agent | ✅ done — `3d0eb34` | [`rows/W30.md`](rows/W30.md) |
| W31 | `DOCUMENT_KINDS` names two roles where three produce these documents | framework agent | ✅ done — `3d0eb34` | [`rows/W31.md`](rows/W31.md) |
| W32 | The mixed-form contents fixture, taken from real material | framework agent | `todo` — re-routed to `SF-13`'s acceptance, no longer a queue row | [`rows/W32.md`](rows/W32.md) |
| W33 | The floor prints its lint state, absence included, as a notice | framework agent | ✅ done — `3a45d4c` | [`rows/W33.md`](rows/W33.md) |
| W34 | `review-rubric.md`'s operational checklist, and the document has no index | framework agent | ✅ done — `a073985` | [`rows/W34.md`](rows/W34.md) |
| W35 | `pointers.py` honours the ignore declaration | framework agent | ✅ done — `a8726c1` | [`rows/W35.md`](rows/W35.md) |
| W36 | A browser in the pinned dev image, checksum-pinned | framework agent | ✅ done — `5f7734b` | [`rows/W36.md`](rows/W36.md) |
| W37 | The repo-wide sweep for checks that cannot fail by construction | framework agent | `todo` | [`rows/W37.md`](rows/W37.md) |
| W38 | The floor and `ruff` disagree by rule; pin the divergence with a test | framework agent | `todo` — after `W40` | [`rows/W38.md`](rows/W38.md) |
| W39 | The index goes stale on every merge, so the release tip is red after each one | framework agent | ✅ done — `16049d2` | [`rows/W39.md`](rows/W39.md) |
| W40 | No module in the tree sits at zero headroom against R11 | framework agent | ✅ done — `8b6e241` | [`rows/W40.md`](rows/W40.md) |
| W41 | An R7 refusal borrows the absent state's reason, and the reason is false | framework agent | `todo` — free | [`rows/W41.md`](rows/W41.md) |
| W42 | The marker check judges some documents and reports a verdict for all of them | framework agent | `todo` — collides with `W48` | [`rows/W42.md`](rows/W42.md) |
| W43 | Two clauses `agent-protocol.md` is owed | framework agent | ✅ done — `2caa0d2` | [`rows/W43.md`](rows/W43.md) |
| W44 | `validate/source.py` stood over R11's ceiling on a deferral naming this row | framework agent | ✅ done — `7b5c0a9` | [`rows/W44.md`](rows/W44.md) |
| W45 | `size_exception()` returns the marker line, so a wrapped row id prints with no id | framework agent | ✅ done — `1aa6319` | [`rows/W45.md`](rows/W45.md) |
| W46 | A finding states, per claim, whether its reading was measured or received | framework agent | `todo` | [`rows/W46.md`](rows/W46.md) |
| W47 | `agent-protocol.md` has no index, and its own clause has ruled `grep` unsafe on it | framework agent | `todo` | [`rows/W47.md`](rows/W47.md) |
| W48 | `W43`'s two clauses have no enforcement arm | framework agent | `todo` | [`rows/W48.md`](rows/W48.md) |
| W49 | Live acceptance conditions that name no instrument which can return `no` | framework agent | `todo` | [`rows/W49.md`](rows/W49.md) |
| W50 | An installed `studyforge` ships the skills' code without their procedures | framework agent | `todo` | [`rows/W50.md`](rows/W50.md) |
| W51 | `ARCHIVE_DIR` and `ARCHIVE_ROOT_NAME` are on no package surface | framework agent | `todo` | [`rows/W51.md`](rows/W51.md) |
| W52 | A `Size exception:` on a file under its ceiling is read by nothing the build ships | framework agent | `todo` | [`rows/W52.md`](rows/W52.md) |
| W53 | A clause naming an instrument is not final until its author has run it both ways | framework agent | `todo` | [`rows/W53.md`](rows/W53.md) |
| W54 | An onboarded corpus's knowledge graph is built, bridged and its census asserted | framework agent | `accepted` — ⛔ **WITHDRAWN PO round 61**, the obligation was the retired tool's | [`rows/W54.md`](rows/W54.md) |
| W55 | A decision — is an installed `studyforge` a supported host for an onboarded corpus? | framework agent | `todo` | [`rows/W55.md`](rows/W55.md) |
| W56 | `reconnaissance/proposal._choices` raises one `Uncertainty` per excluded path | framework agent | `todo` | [`rows/W56.md`](rows/W56.md) |
| W57 | `render/page/text.py`'s `SAFE_SCHEMES` refuses a bare same-directory relative href | framework agent | `todo` | [`rows/W57.md`](rows/W57.md) |
| W58 | The zero marker beside a real finding is a build failure | framework agent | `todo` | [`rows/W58.md`](rows/W58.md) |
| W59 | `_escape` crosses a package boundary as a private name; the fix is to move it | framework agent | ✅ done — `a37f827` | [`rows/W59.md`](rows/W59.md) |
| W60 | Two copies of one vocabulary, unlinked, inert, and wire-shaped | framework agent | `todo` | [`rows/W60.md`](rows/W60.md) |
| W61 | Two shipped skills gave a command that does not exist, in a fence | framework agent | ✅ done — `ad27ed2` | [`rows/W61.md`](rows/W61.md) |
| W62 | The latent `Owns` cells, and a trigger that cannot be shelved | PO | `todo` | [`rows/W62.md`](rows/W62.md) |
| W63 | The marker vocabulary's closed check | framework agent | ✅ done — `0183cd1` | [`rows/W63.md`](rows/W63.md) |
| W64 | The kind gate widened across the whole document floor | framework agent | ✅ done — `2c9082d` | [`rows/W64.md`](rows/W64.md) |
| W65 | R7's third subject has no sweep | framework agent | `todo` | [`rows/W65.md`](rows/W65.md) |
| W66 | The non-ASCII narrowing, and the emitter disagrees with the gate | framework agent | `todo` | [`rows/W66.md`](rows/W66.md) |
| W67 | The two zero-headroom test modules | framework agent | `todo` — ahead of any row adding a test to `corpus/container` or `corpus/manifest` | [`rows/W67.md`](rows/W67.md) |
| W68 | The gate walk derives from the tree, not the disk | framework agent | ✅ done — merged late in round 34 | [`rows/W68.md`](rows/W68.md) |
| W69 | A closed check refusing a bare task-count literal | framework agent | `todo` | [`rows/W69.md`](rows/W69.md) |
| W70 | Every Acceptance clause expressible as an `Acceptance` | framework agent | ✅ done — `8b4c92b` | [`rows/W70.md`](rows/W70.md) |
| W71 | The tilde arm, and both callers over all three shapes | framework agent | `todo` | [`rows/W71.md`](rows/W71.md) |
| W72 | `pinned` vs `tracked` in `workspace.json` | framework agent | `todo` — re-scoped round 34 | [`rows/W72.md`](rows/W72.md) |
| W73 | `E11`'s delivery-skill comparison, re-pointed by its taker at the corpus they own | INTEGRATION side | in-progress — taken, re-pointed | [`rows/W73.md`](rows/W73.md) |
| W74 | The sibling runnable-module check widens | framework agent | ✅ done — `a3efb12` | [`rows/W74.md`](rows/W74.md) |
| W75 | No document says how `studyforge` gets on the path | framework agent | `todo` — the pin's conversion landed with `W211`; the documentation half remains | [`rows/W75.md`](rows/W75.md) |
| W76 | `render.page`'s five cross-package helpers are private and every renderer imports them | framework agent | ✅ done — `c3e2919` | [`rows/W76.md`](rows/W76.md) |
| W77 | The corpus-scale comparison for `SF-14`, `SF-15` and `SF-27` | E09 | routed — folded into `E09`'s delivery, `W5`'s precedent | [`rows/W77.md`](rows/W77.md) |
| W78 | Citations into files a live document does not own — a line number that moves, and a `rows/<ID>.md` a close DELETED | framework agent | ✅ done — `26f4a05` | [`rows/W78.md`](rows/W78.md) |
| W79 | Two small carries — each of THREE golden regenerators names the other two, and the census comment cites its command | framework agent | `todo` — minted round 35, widened round 37 | [`rows/W79.md`](rows/W79.md) |
| W80 | `SF-19b`'s Acceptance names a consumer corpus by ROLE, and owes an instrument or a disposition | PO | ✅ done — PO round 68 | [`rows/W80.md`](rows/W80.md) |
| W81 | `SK-03`'s consumer-corpus Acceptance clause, the same class | PO | ✅ done — PO round 68 | [`rows/W81.md`](rows/W81.md) |
| W82 | `SK-04`'s consumer-corpus Acceptance clause, the same class | PO | `todo` | [`rows/W82.md`](rows/W82.md) |
| W83 | `TC-00`'s consumer-corpus Acceptance clause, the same class | PO | `todo` | [`rows/W83.md`](rows/W83.md) |
| W84 | `SK-01`'s consumer-corpus Acceptance clause, answered by Ruling 166 | PO | ✅ done — Ruling 166, `911c56f` | [`rows/W84.md`](rows/W84.md) |
| W85 | The board instrument's six carries — Rulings 182 and 183, and `CTO-47/3`, `/4`, `/5` | Developer 2 | ✅ done — `d430f34` | [`rows/W85.md`](rows/W85.md) |
| W86 | Ruling 184's two clauses into check 3, and the 74 frozen lines `W85` is what unfreezes | Developer 2 | ✅ done — `d430f34` | [`rows/W86.md`](rows/W86.md) |
| W87 | `board_state`'s notice prints the row files whose argument IS their own naming cell | Developer 2 | ✅ done — `d430f34` | [`rows/W87.md`](rows/W87.md) |
| W88 | The thin row files gain an ANCHORED pointer, and four lose a dangling deictic | PO | ✅ done — PO round 73 | [`rows/W88.md`](rows/W88.md) |
| W89 | An R7 gate's false positive on ordinary source, narrowed in the gate and not in the source | framework agent | `todo` — Ruling 179 | [`rows/W89.md`](rows/W89.md) |
| W90 | The root index can link no container page, and it is a `toc_api` question | PO | `todo` — a named gap of `M4`'s close, not a gate (round 72) | [`rows/W90.md`](rows/W90.md) |
| W91 | The hand-maintained rulings index stops short of the live series, so a bare `(Ruling n)` resolves to nothing | Developer 2 | ✅ done — `8be7e86` | [`rows/W91.md`](rows/W91.md) |
| W92 | The capability index cannot say *not this side*, so a reading-floor corpus writes 13 false `why`s | framework agent | `todo` | [`rows/W92.md`](rows/W92.md) |
| W93 | *Point the skill at a corpus* is not performable — no corpus-shaped input on the surface | framework agent | `todo` | [`rows/W93.md`](rows/W93.md) |
| W94 | A shipped refusal names its first witness, not its population — 6 sites against 55 correct | framework agent | `todo` — Ruling 188 | [`rows/W94.md`](rows/W94.md) |
| W95 | No fixture has two units sharing one source file, so `Q23`'s answer cannot be tested | framework agent | ✅ done — `cfe0e0c` | [`rows/W95.md`](rows/W95.md) |
| W96 | A cell declaring a started state asserts a live checkout or a branch ahead of release | framework agent | ✅ done — `3432e9a` | [`rows/W96.md`](rows/W96.md) |
| W97 | `\|clips\| == \|spoken units\|` — *both directions* proves surjectivity, not injectivity | framework agent | `todo` — Ruling 187, before `SF-16` | [`rows/W97.md`](rows/W97.md) |
| W98 | `QA-03`'s harness judges 2 of 6 chrome regions — `site.py` passes no `links` and builds one page kind | framework agent | ✅ done — `8416924` | [`rows/W98.md`](rows/W98.md) |
| W100 | A `## Scheduled` cell declares no state, so the one instrument that reads states cannot read it | framework agent | ✅ done — `6d5aeed` | [`rows/W100.md`](rows/W100.md) |
| W101 | Check 4's sub-step compares `Owns` to a diff, and `Owns` is brace expansion and directory prefixes | framework agent | `todo` — `CTO-48/12`, before the next parallel pair | [`rows/W101.md`](rows/W101.md) |
| W102 | Check 3's pattern is case-sensitive, and the house style writes `RULING <n>` | framework agent | ✅ done — Ruling 184(c), `4e8ba86` | [`rows/W102.md`](rows/W102.md) |
| W103 | A finding's disposition lives only in a frozen record, so `FND-04`'s reads `OPEN` after `SF-09` closed it | framework agent | ✅ done — `a8c4738` | [`rows/W103.md`](rows/W103.md) |
| W104 | The lint notice names no subject, and `ruff format` formats Markdown as well as Python | framework agent | `todo` — not `W38`'s subject | [`rows/W104.md`](rows/W104.md) |
| W105 | The region census has no authorable population, so a region the templates emit and nothing paints is unsayable | framework agent | ✅ done — `17f6d95` | [`rows/W105.md`](rows/W105.md) |
| W106 | The repository-wide marker sweep has no shipped reader, so one vocabulary has three copies | framework agent | ✅ done — `8c24fb7` | [`rows/W106.md`](rows/W106.md) |
| W107 | `FRAGMENT` and `anchor()` are composed in two packages, and the shared-name rule gives them to neither | framework agent | ✅ done — `a82db50` | [`rows/W107.md`](rows/W107.md) |
| W108 | No fixture crosses a module boundary inside one section, so a renderer can pass the clause and be wrong | framework agent | ✅ done — `79db35b` | [`rows/W108.md`](rows/W108.md) |
| W109 | Every consumer that reads `origin` from a document instead of the parser is a second reader of a growing field | framework agent | ✅ done — `e9c7dcd` | [`rows/W109.md`](rows/W109.md) |
| W110 | `corroborate`'s live-checkout arm discharges a branch git already knows is SPENT, so a leaked worktree keeps a stale row green | framework agent | ✅ done — `923a970` | [`rows/W110.md`](rows/W110.md) |
| W111 | Ruling 196's expiry — the header locator ANNOUNCES where a delimiter can REFUSE, and the delimiters have landed | framework agent | ✅ done — `923a970` | [`rows/W111.md`](rows/W111.md) |
| W112 | A browser clause discharged on a HOST reading owes a COMMITTED check, or no second office can reproduce it | framework agent | `todo` — `SF-30/1`, Ruling 204, ⭐ **UNBLOCKED, `W36` merged** | [`rows/W112.md`](rows/W112.md) |
| W113 | `Address(tuple(<str>))` is accepted and splits a string into one segment per character | framework agent | `todo` — `SF-30/2`, `SF-12`'s contract | [`rows/W113.md`](rows/W113.md) |
| W114 | R11's ceiling has no instrument outside `.py`, so an authored asset at the ceiling is invisible to the gate | framework agent | `todo` — Ruling 207 | [`rows/W114.md`](rows/W114.md) |
| W115 | A failed git reading is coerced to a number, so *git could not answer about this branch* lands on REFUTED and one arm exits `0` | framework agent | ✅ done — `0e9a86d` | [`rows/W115.md`](rows/W115.md) |
| W116 | The formatter's target is INFERRED, so an absent declaration made a style decision no document records | framework agent | ✅ done — `b182a88` | [`rows/W116.md`](rows/W116.md) |
| W117 | `**Consumer-side modules:**` is a contract named in ZERO convention documents, and both its sites are consumers | framework agent | ✅ done — `e58213f` | [`rows/W117.md`](rows/W117.md) |
| W118 | A gap named in FOUR consecutive closes is a different fact from a gap named once, and no instrument reads it | PO | `todo` — `CTO-52/5` | [`rows/W118.md`](rows/W118.md) |
| W119 | A committed test reads THIS MACHINE'S worktree set, so it goes RED on a correct tree in the window after every merge | framework agent | ✅ done — `6d5aeed` | [`rows/W119.md`](rows/W119.md) |
| W120 | The bounded Ruling 186 notice is discharged by ONE row over its WHOLE population, and a partial fix is refused | PO | ✅ done — PO round 73 | [`rows/W120.md`](rows/W120.md) |
| W121 | The marker reader cannot see a finding written as a TABLE ROW, which is the form both offices write | framework agent | ✅ done — `e60224b` | [`rows/W121.md`](rows/W121.md) |
| W122 | A count in a SHIPPED file that no unit makes true — the Dockerfile's *"21 shared libraries"* | framework agent | ✅ done — `7b03763` | [`rows/W122.md`](rows/W122.md) |
| W123 | A hang has no deadline anywhere, so a wedged suite returns no reading and no exit code either | framework agent | ✅ done — `7b03763` | [`rows/W123.md`](rows/W123.md) |
| W124 | `0` apt packages are version-constrained, so a font is an undeclared input to a recorded number | framework agent | ✅ done — `7b03763` | [`rows/W124.md`](rows/W124.md) |
| W125 | The In flight table is ASSERTED, and generating it naively leaves `corroborate` asserting git against itself | framework agent | ✅ done — `e48a0bd` | [`rows/W125.md`](rows/W125.md) |
| W126 | Rulings 217–241 reached NO convention document, 0 of 25, and the tail has no instrument asserting they ever will | framework agent | ✅ done — `f65a669` | [`rows/W126.md`](rows/W126.md) |
| W127 | `tests/test_knowledge_index.py` ships a second workspace resolver, so 3 of the 11 skips are a defect | framework agent | ✅ done — `84b717b` | [`rows/W127.md`](rows/W127.md) |
| W128 | A committed verdict may not depend on the host's ENVIRONMENT — Ruling 225's other half, in `tests/visual/` | framework agent | ✅ done — `aaa18a5` | [`rows/W128.md`](rows/W128.md) |
| W129 | A close Ruling 201 DEFINES deletes a row file that FROZEN records point at, so three closes stand behind one clause | framework agent | ✅ done — `94a3a4b` | [`rows/W129.md`](rows/W129.md) |
| W130 | The board's byte allowance is indexed to register rows and cannot see the two tables that grew | framework agent | ✅ done — `94a3a4b` | [`rows/W130.md`](rows/W130.md) |
| W131 | Two shipped checks in `tests/docker/` certify a property a backslash continuation hides from them | framework agent | ✅ done — `208fef3` | [`rows/W131.md`](rows/W131.md) |
| W132 | A by-construction exemption gated on `0` ahead makes the line Ruling 264(c) turned into a GATE unreadable | framework agent | ✅ done — `94a3a4b` | [`rows/W132.md`](rows/W132.md) |
| W133 | `check_rulings_reach`'s predicate cannot read the plural, comma-list or range citation form, and a CHECK's pass condition is satisfiable by one undeclared spelling | framework agent | ✅ done — `6c5bc53` | [`rows/W133.md`](rows/W133.md) |
| W134 | The rulings that reached no convention document — `W126` landed 6 of 25, and the band below the tail is worse than the cliff | framework agent | ✅ done — `4a3642a` | [`rows/W134.md`](rows/W134.md) |
| W135 | A citation of a tracked document written as a bare filename is invisible to the one instrument that checks citations | Developer 3 | in-progress — Ruling 285(b) | [`rows/W135.md`](rows/W135.md) |
| W136 | A pre-merge GATE's exemption is a SPELLING where its ruling's ground is a ROLE, so it flags 13 branches and silently exempts 3 it would flag | framework agent | `todo` — Ruling 265, `W132/2` widened | [`rows/W136.md`](rows/W136.md) |
| W137 | Two committed tests assert the bijection Ruling 270 RETIRED, so the protocol's FIRST close turns a shipped suite red on a correct board | framework agent | ✅ done — `395d543` | [`rows/W137.md`](rows/W137.md) |
| W138 | A third re-derivation of the workspace resolver SUBSTITUTES a synthetic corpus instead of skipping, so `SF-03`'s named acceptance is proved of a 48×5 grid no census can see | framework agent | ✅ done — `6e349be` | [`rows/W138.md`](rows/W138.md) |
| W139 | The reach notice's window is 25 wide and SLIDES, so a ruling still uncited BELOW it reads `unreached 0` and the figure is an artifact | framework agent | ✅ done — `09b6459` | [`rows/W139.md`](rows/W139.md) |
| W140 | 11 anchor names in `BOARD-ARCHIVE.md` answer for 29 headings, and `heading_slugs()` returns a SET so the pointer floor is blind to every one | framework agent | ✅ done — `f814e07` | [`rows/W140.md`](rows/W140.md) |
| W141 | A `RULED ROUND N` heading states its own clause count and no instrument reads it, so two of three were wrong before the branch existed | framework agent | `todo` — `W134/5` | [`rows/W141.md`](rows/W141.md) |
| W142 | Two floor checks reach their verdict through `ruff check .`, which walks the DISK, so an untracked file reddens a correct tree | framework agent | ✅ done — `ed1dcdd` | [`rows/W142.md`](rows/W142.md) |
| W143 | `git checkout -- <dir>` restores a plant to `HEAD`, discarding an uncommitted NEIGHBOUR while `porcelain` reads clean | framework agent | ✅ done — `ed1dcdd` | [`rows/W143.md`](rows/W143.md) |
| W144 | One phrase, two populations — the notice counts table LINES and the bound counts the ID SET, and both say *register rows* | Developer 2 | ✅ done — `7b2e5d0` | [`rows/W144.md`](rows/W144.md) |
| W145 | A citation WRAPPED across a line break is unreadable to the predicate that reads citations, so one of the notice's own three declared gaps is inhabited and its uncited set carries a false member | framework agent | ✅ done — `410d171` | [`rows/W145.md`](rows/W145.md) |
| W146 | The commits-ahead notice compares the COUNT and never the TIP the same cell declares, so a reading TRUE at its own ref prints as a disagreement | framework agent | ✅ done — `743af6a` | [`rows/W146.md`](rows/W146.md) |
| W147 | A committed test asserts the In-flight table is INHABITED, so the shipped suite goes RED on a correct board when nothing is in flight | framework agent | ✅ done — `adab956` | [`rows/W147.md`](rows/W147.md) |
| W148 | The floor's document population is read off the DISK, so an untracked file makes a MAIN reading unreproducible from a worktree | framework agent | ✅ done — `a8726c1` | [`rows/W148.md`](rows/W148.md) |
| W149 | A merge subject's PROSE is re-derived against its record by nobody, and a subject cannot be annotated after it lands | framework agent | `todo` | [`rows/W149.md`](rows/W149.md) |
| W150 | A citation into a file the document does not own, written as a BARE BASENAME, satisfies Ruling 163's letter and is strictly worse | Developer 2 | in-progress | [`rows/W150.md`](rows/W150.md) |
| W151 | Hand-typed counts in docstrings have no instrument, and a derived-count claim and its three typed copies disagree | framework agent | `todo` | [`rows/W151.md`](rows/W151.md) |
| W152 | `docker/dev/check` re-exports provenance on every run, so two offices read different shas for one identical environment | framework agent | ✅ done — `3049de9` | [`rows/W152.md`](rows/W152.md) |
| W153 | `corroborate`'s `dispatched and UNNAMED` arm reads its names from the register, so a wave with no register round is blind by construction | framework agent | `todo` | [`rows/W153.md`](rows/W153.md) |
| W154 | Commits-per-capability has no instrument, and the register may not carry the reading because a register cell carries no measurement | framework agent | `todo` | [`rows/W154.md`](rows/W154.md) |
| W155 | R11's ceiling has an instrument and its APPROACH has none — the predicate is proximity × GROWTH, and proximity alone flags the ceiling working | framework agent | ✅ done — `0011d5d` | [`rows/W155.md`](rows/W155.md) |
| W156 | A row `Owns` inside a component it does not create, with its creator in the SAME step and no declared edge | framework agent | `todo` — its edge half landed with round 74's reorder | [`rows/W156.md`](rows/W156.md) |
| W157 | The knowledge index goes stale on every merge, nothing owns the rebuild, and no instrument can fail on it | framework agent | `accepted` — ⛔ **WITHDRAWN PO round 61**, and the re-scope that preceded it was refuted by this round's own suite | [`rows/W157.md`](rows/W157.md) |
| W158 | The authoritative environment is structurally blind to the workspace assertions, so `green` names two different answers | framework agent | `todo` — `CTO-66/11` | [`rows/W158.md`](rows/W158.md) |
| W159 | Most of the board's tables are UNDELIMITED — `Next rows` and `Standing decisions` among them: no instrument reads them and the size bound gives them no term | framework agent | `todo` — naming corrected `PO-56/8` | [`rows/W159.md`](rows/W159.md) |
| W160 | A live row's SURFACE is checked by nothing, so check 4's sub-step is undecidable and its one answer is a hand-maintained paragraph | framework agent | `todo` | [`rows/W160.md`](rows/W160.md) |
| W161 | The observation table admits an EPIC task and no instrument says where such a row's argument lives, so it is exempt by accident | framework agent | `todo` — `NS-01/2` | [`rows/W161.md`](rows/W161.md) |
| W162 | Ten gated assertions no routine environment reaches, and the skip's own stated ground is false whenever the image is already built | framework agent | `todo` — Ruling 332 | [`rows/W162.md`](rows/W162.md) |
| W163 | `compose.yaml`'s `STUDYFORGE_VISUAL` reasoning, which the row that fired its trigger landed beside and did not carry | framework agent | `todo` — `W128/6` | [`rows/W163.md`](rows/W163.md) |
| W164 | A gate is not only where it is CALLED — a fixture propagates it, so a gated census taken with `grep` under-counts silently | framework agent | `todo` | [`rows/W164.md`](rows/W164.md) |
| W165 | A cost figure over a GATED population carries its spread or only its sample, and one end of a 32x range decided a mode | framework agent | `todo` | [`rows/W165.md`](rows/W165.md) |
| W166 | The standing SPLIT condition `tools/quality/board/verdict.py` is owed, third member inside one package | PO | ✅ done — PO round 55 | [`rows/W166.md`](rows/W166.md) |
| W167 | The handoff check iterates the files that EXIST, so *the handoff is missing* is unreachable by construction | framework agent | ✅ done — `4bfd720` | [`rows/W167.md`](rows/W167.md) |
| W168 | A trial merge run through the reviewer's OWN wrapper measures the reviewer's own tree and reads like a correct run | framework agent | `todo` — `CTO-67/11` | [`rows/W168.md`](rows/W168.md) |
| W169 | Ruling 96's line has no named checkout, and its instrument answers `none` in every office tree and `stale` in one | framework agent | `todo` — `CTO-67/3` | [`rows/W169.md`](rows/W169.md) |
| W170 | A live `trial/*` branch reaches the ONE pre-merge gate line, on the ground Ruling 265 already exempted a namespace for | framework agent | ✅ done — `4d4c7c7` | [`rows/W170.md`](rows/W170.md) |
| W171 | An edit that removes a document's LAST pointer to a record section orphans it, and the pointer floor is tree-shaped so it cannot see a removal | framework agent | `todo` — `CTO-68/4` | [`rows/W171.md`](rows/W171.md) |
| W172 | Ruling 218's GATE THREE — a record's Findings section told from its prose, and the residue `W64` measured rather than chased | framework agent | ✅ done — `a033a45` | [`rows/W172.md`](rows/W172.md) |
| W173 | The board carries RULES where Ruling 349 says a rule is the convention's, and no instrument can tell a board POINTER from a board RESTATEMENT | framework agent | `todo` — Ruling 349 | [`rows/W173.md`](rows/W173.md) |
| W174 | Ruling 201's FOURTH EDIT lands outside the closing office's surface, and the two rules are jointly unsatisfiable for a row cited from code | framework agent | `todo` — `PO-56/3`, converted to a row | [`rows/W174.md`](rows/W174.md) |
| W175 | `W167`'s *owes nothing* escape has no legal site, so a pass that cannot be earned is reachable only by the checker's own default | framework agent | `todo` — ⭐ **UNBLOCKED**; the site is a CONTRACT CHANGE and goes to the reviewer first | [`rows/W175.md`](rows/W175.md) |
| W176 | `corroborate`'s refuted line prints a ROW count beside row SUBJECTS and names neither unit, so `(3)` stands over four ids | framework agent | `todo` — `CTO-72/3` | [`rows/W176.md`](rows/W176.md) |
| W177 | The agent-callable narration path has no personal-data gate owner, so R7's obligation is carried by a tool description | framework agent | `todo` — `NS-06/3` | [`rows/W177.md`](rows/W177.md) |
| W178 | `narrate/__init__.py`'s *Depends on* names a package nothing imports and omits one this wave added | framework agent | `todo` — `NS-05/7` | [`rows/W178.md`](rows/W178.md) |
| W179 | A new source file is outside the format gate's population until it is committed, so a green suite is not a reading of that gate | framework agent | `todo` — `NS-05/12` | [`rows/W179.md`](rows/W179.md) |
| W180 | Ruling 349(a) binds the office CHECKING a removal and no rule binds the office MAKING one | framework agent | `todo` — `CTO-71/9` | [`rows/W180.md`](rows/W180.md) |
| W181 | A register id that is not `W<digits>` crashes the floor instead of reporting, and only the register can create one | framework agent | `todo` — `CTO-71`'s `W167` review | [`rows/W181.md`](rows/W181.md) |
| W182 | Spec §R9 still reads `open` for a contract Ruling 351 LOCATED, so a step is open on a fact its own authority contradicts | framework agent | ✅ done — `430363b` | [`rows/W182.md`](rows/W182.md) |
| W183 | `E04`'s `Owns` lines were drafted without measurement — wrong in GRANULARITY and COVERAGE | framework agent | ✅ done — `7d77b0d` | [`rows/W183.md`](rows/W183.md) |
| W184 | `narrate/__init__.py`'s `Depends on` is wrong a THIRD way, each time found by an office that cannot fix it | framework agent | `todo` `SF-17/3` | [`rows/W184.md`](rows/W184.md) |
| W185 | The close procedure and `board-size` are jointly unsatisfiable; owes a DESIGN DECISION | Developer 2 | ✅ done — `f1684e6` | [`rows/W185.md`](rows/W185.md) |
| W186 | Round 19 §5.3 still instructs `data-speech-id`, ruled NOT emitted | framework agent | `todo` `SF-18` | [`rows/W186.md`](rows/W186.md) |
| W187 | Nothing in `src/` builds the position→filename map; the join is on the SPEECH ID | framework agent | ✅ done — `70131e2` | [`rows/W187.md`](rows/W187.md) |
| W188 | The contradiction check SKIPS when no register cell declares a started state — the state a register leaves at every wave boundary | framework agent | ✅ done — `7d77b0d` | [`rows/W188.md`](rows/W188.md) |
| W189 | `narrate-service` has produced no real audio and its `README` claims a measurement the repository does not hold | framework agent | ✅ done — `978fa1b` | [`rows/W189.md`](rows/W189.md) |
| W190 | `corroborate`'s `dispatched and UNNAMED` arm has a population of CHECKOUTS, so a branch carrying work is invisible to it whenever its office cleans up after itself | framework agent | ✅ done — `c49f254` | [`rows/W190.md`](rows/W190.md) |
| W191 | The floor can be GREEN while the suite is RED at one ref, and every row now self-certifies on a phrase an office can satisfy by reading the floor alone | framework agent | `todo` — ⛔ **UNASSIGNED through four waves** | [`rows/W191.md`](rows/W191.md) |
| W192 | Ruling 218's multi-id cell is readable in exactly ONE spelling, and the comma form observes the wrong row silently | framework agent | `todo` — `PO-59/7` | [`rows/W192.md`](rows/W192.md) |
| W193 | The narration record and its clips grow without bound and nothing prunes; pruning owes a RULE about which clips a build may delete | PO | ✅ done — PO round 64 | [`rows/W193.md`](rows/W193.md) |
| W194 | `narrate-service`'s `docs/api.md` example manifest is schema-stale against the service's own live answer | framework agent | `todo` — `NS-07` F3, sibling | [`rows/W194.md`](rows/W194.md) |
| W195 | There is no build pipeline: nothing walks a corpus and writes pages, so the reading floor cannot be PRODUCED by anything but a test | framework agent | ✅ done — `6ffba1e` | [`rows/W195.md`](rows/W195.md) |
| W196 | Ruling 74 and Ruling 78's suite gate are JOINTLY UNSATISFIABLE — the formatter strips the parens the ruling requires | Developer 2 | ✅ done — `f1684e6` | [`rows/W196.md`](rows/W196.md) |
| W197 | `SF-28` grew by accretion until it stopped being a row — one Definition, five acceptance additions, at least eight deliverables | PO | ✅ done — PO round 61 | [`rows/W197.md`](rows/W197.md) |
| W198 | Nothing in `src/` declares where a unit's authored overlay sits in an archive, so no build can apply one | framework agent | `todo` — `W195/2` | [`rows/W198.md`](rows/W198.md) |
| W199 | `archive`/`raw` are minted twice and neither `validate` name is on `validate.__all__` — Ruling 101's open deviation | framework agent | `todo` — `W195/1` | [`rows/W199.md`](rows/W199.md) |
| W200 | The root ignore file's bare `build/` silently ignores `src/studyforge/build/`, and `SF-28` will walk into it | framework agent | `todo` — `W195/7`, verified by the register | [`rows/W200.md`](rows/W200.md) |
| W201 | The corpus walk is written three times and a test helper binds one constant twice | framework agent | `todo` — `W195/5`, `W195/3` | [`rows/W201.md`](rows/W201.md) |
| W202 | Six decisions a build cannot ship without, every one of them defaulted today by whatever was convenient | PO + user | ✅ done — PO round 63 | [`rows/W202.md`](rows/W202.md) |
| W203 | Graphify retired from every live document and from `tools/`, with the floor/suite scope line | framework agent | ✅ done — `2cf11f1` | [`rows/W203.md`](rows/W203.md) |
| W204 | Prose inside Python is an UNGATED citation surface, so a deleted module stays quoted as authority indefinitely | framework agent | `todo` — `W203`'s measurement | [`rows/W204.md`](rows/W204.md) |
| W205 | A frozen record can be made to fail a gate from outside itself, and Ruling 106's annotate-beneath remedy cannot reach a POINTER | framework agent | `todo` — ⛔ **HELD BY THE RULING FREEZE** | [`rows/W205.md`](rows/W205.md) |
| W206 | Five tasks exist with no step membership: `W197`'s split landed in the epic and its ordering half did not | PO | ✅ done — PO round 64 | [`rows/W206.md`](rows/W206.md) |
| W207 | `E04`'s own `media` example declares a limit `parse_media` refuses by name, so a corpus copying the epic does not validate | framework agent | ✅ done — `4fb111d` | [`rows/W207.md`](rows/W207.md) |
| W208 | An `AddressError` escapes the container reader, so a wrong-depth container map CRASHES `studyforge plan` | framework agent | ✅ done — `6ffba1e` | [`rows/W208.md`](rows/W208.md) |
| W209 | `tests/emission` calls every public writer with fillers, so a green suite writes into the checkout and reports nothing | framework agent | ✅ done — `869fd4c` | [`rows/W209.md`](rows/W209.md) |
| W210 | The media policy is spelled twice — `cli/plan/report.py` re-derives what `ignore_lines` exists to be the one spelling of | framework agent | `todo` — `SF-32/4` | [`rows/W210.md`](rows/W210.md) |
| W211 | The pinned image cannot install this package, so every reading about the INSTALLED command is host-only and no second office can reproduce one | framework agent | ✅ done — `f382a4a` | [`rows/W211.md`](rows/W211.md) |
| W212 | The `AddressError` leak `W208` fixed in `plan` reaches `studyforge build` too, and the justification beside the catch is false | framework agent | ✅ done — `419c805` | [`rows/W212.md`](rows/W212.md) |
| W213 | The manifest reader's catch list is a retyped subset, correct only by a property of the reader that nothing asserts | framework agent | ✅ done — `419c805` | [`rows/W213.md`](rows/W213.md) |
| W214 | A build can find archive media and NO ADAPTER IS INSTRUCTED TO PRODUCE ANY — §9 inverted, the artifact arrived first | framework agent | `todo` — `SF-37/2` | [`rows/W214.md`](rows/W214.md) |
| W215 | A unit's `assets` and `attachments` are declared in the archive and read by nothing in `src/`, and spec C4 says what they are for | framework agent | `todo` — `SF-37/6` | [`rows/W215.md`](rows/W215.md) |
| W216 | `tests/test_emission.py`'s coverage floor sits so far below its own census that it cannot fall, and the sweep is the R7 gate's population | framework agent | `todo` — `W209/5` | [`rows/W216.md`](rows/W216.md) |
| W217 | The suite writes OUTSIDE the checkout, and `W209`'s detector is repository-scoped by construction so it cannot see it | framework agent | ✅ done — `475370c` | [`rows/W217.md`](rows/W217.md) |
| W218 | `W193`'s rule is written and nothing carries it out: dead clips count against a shipped ceiling and no instrument discloses or prunes them | framework agent | ✅ done — `18dc8e1` | [`rows/W218.md`](rows/W218.md) |
| W219 | The `RAISES` sweep reads handler names over `corpus.*` only, so a sliced tuple survives it and `archive` is outside it | framework agent | `todo` — `W212/2` + `W212/4` | [`rows/W219.md`](rows/W219.md) |
| W220 | `reconnaissance.record.read` quotes an EXISTING `path=` back in its refusal — a latent R7 echo the contained census can no longer reach | framework agent | `todo` — `W217/2` | [`rows/W220.md`](rows/W220.md) |
| W221 | The whole suite still writes outside the checkout — temp, cache and browser dirs — and nothing owns or asserts it | framework agent | `todo` — `W217/3` | [`rows/W221.md`](rows/W221.md) |
| W222 | `narrate.synth.audio_dir` takes no `label`, so a labelled unit's clips land where its page does not look | framework agent | `todo` — `SF-42/1` | [`rows/W222.md`](rows/W222.md) |
| W223 | `engine_model` is in the service's cache key and in neither `Health` nor `Conditions`, so a model change requests nothing | framework agent | `todo` — `SF-42/2` + `W212/3` | [`rows/W223.md`](rows/W223.md) |
| W224 | A build into any `--out` but the corpus root ships a player that plays nothing and names no gap, because no pass copies a clip | framework agent | ✅ done — `d7c9d4d` | [`rows/W224.md`](rows/W224.md) |
| W225 | One image tag serves every checkout, so a pinned reading can run in another checkout's image and the guard against it is blind past `W211` | framework agent | ✅ done — `a8742c1` | [`rows/W225.md`](rows/W225.md) |
| W226 | The narration record cannot locate every clip it wrote, so a removed unit's clips and a re-worded passage's old clip are beyond the only prune | framework agent | `todo` — `W218/1` + `W218/2` | [`rows/W226.md`](rows/W226.md) |
| W227 | Nothing runs the non-destructive check on a real build, so spec §11.2 item 11 has an instrument only its own tests invoke | framework agent | `todo` — `OPS-05/2` | [`rows/W227.md`](rows/W227.md) |
| W228 | Ruling 173's population reads `E09` as integration WHOLE, so a framework row homed there escapes the consumer-corpus class — `OPS-05` did | framework agent | `todo` — `PO-67/2` + `OPS-05/1` | [`rows/W228.md`](rows/W228.md) |
| W229 | `W143`'s plant procedure gives no plant a fresh bytecode cache, so two same-size plants can read one `.pyc` | framework agent | `todo` — `OPS-05/7` | [`rows/W229.md`](rows/W229.md) |
| W230 | One instance serving several corpora exists in `serve/` and a reader cannot reach it — the verb never builds it and the static mount refuses a nested corpus | framework agent | ✅ done — `a956b6c` | [`rows/W230.md`](rows/W230.md) |
| W231 | Two fenced commands in `review-rubric.md` read a population the tree no longer means — Ruling 192's literal authorable sweep and Ruling 290's `:local` inspect | framework agent | `todo` — `W105/2` + `W225/1` | [`rows/W231.md`](rows/W231.md) |
| W232 | `test_progress.py` walks the repository's DISK for the reader's store, so a copy under the git-ignored `.scratch/` Ruling 139 prescribes reddens a correct tree | framework agent | `todo` — `W107/4` | [`rows/W232.md`](rows/W232.md) |
| W233 | `test_serve_process.py` reads a line and then calls `communicate()`, so buffered lines are dropped and its assertions hold by reading only the last one | framework agent | ✅ done — `a0c849a` | [`rows/W233.md`](rows/W233.md) |
| W234 | When no checkout holds a row's branch, `corroborate` never compares the checkout the row claims with the branch that checkout holds | framework agent | `todo` — `COORD-21/1` | [`rows/W234.md`](rows/W234.md) |
| W235 | A sharing archive carries a non-UTF-8 file with its contents ungated and unreported, so *no personal data — asserted* holds over a subset | Developer 1 | ✅ done — `4d3c742` | [`rows/W235.md`](rows/W235.md) |
| W236 | A personal archive carries grader passes and no read marks, so a prose corpus's whole record of completion cannot enter one | framework agent | `todo` — `SK-06/2` | [`rows/W236.md`](rows/W236.md) |
| W237 | `W233`'s read-then-`communicate()` defect is live in three more process tests, and `tests.support.ProcessOutput` is now the one reader | Developer 1 | in-progress — `W233/2` + `W233/4`, order 1 | [`rows/W237.md`](rows/W237.md) |
| W238 | The capability index orders milestones by their ids, so the order the user decided prints wrong | framework agent | `todo` — `PO-74/1` | [`rows/W238.md`](rows/W238.md) |
<!-- /register -->

⛔ **`W19` has no row of its own: `W17` and `W19` are ONE COMMIT, ruled, and the
register carries them as one.** ⭐ **`W99` is a reserved sentinel and is not an
id, so round 38's mints START AT `W100`** — ⚠️ **and the gap is deliberate rather
than a missing row.**

## R21 — the register of unlocated contracts

⛔ **Ruled round 17: this register is a POINTER to spec §R9, not a second copy of
it.** ⭐ **The open set is whatever §R9 marks `open`.**

| Open row | Owed before | Owner |
|---|---|---|
| ⭐ **narration regeneration state — LOCATED** (Ruling 351); ⛔ **§R9 still reads `open`, [`W182`](rows/W182.md)** | `SF-17` (M3 step 3.4) | CTO |
| **coverage report** — no file | `EX-05` (M9) | CTO |

⚠️ **ROW ONE NO LONGER BLOCKS `M3 step 3.4`** ([the open](BOARD-ARCHIVE.md#po-round-58-the-register)). ⛔ **A POINTER REPORTS A DIVERGENCE RATHER THAN HIDE IT: §R9's two cells are UN-TRANSCRIBED, and [`W182`](rows/W182.md) carries them.** ⭐ **[Ruling 330's split](BOARD-ARCHIVE.md#the-ns-02ns-03-ordering-ruled-the-edge-lands-and-ruling-330cs-pass-condition-is-satisfiable-for-only-one-of-two-named-contributors) · [why R21 exists](BOARD-ARCHIVE.md#r21-the-register-of-unlocated-contracts).**

## Standing decisions

⭐ **A decision that binds every agent and is not a task.** ⛔ **The decision is
here; the argument is in the record.**

| Decision | Argument |
|---|---|
| **`ONBOARDING.md` does not enter the repository** — not tracked, not corrected into the tree, and not deleted, because it is untracked and therefore not repository state | [record](BOARD-ARCHIVE.md#onboardingmd-ruled-it-does-not-enter-the-repository) |
| ⭐ **`.claude/settings.json` IS tracked, and it is R18 with a machine behind it** — it DENIES `Bash(git push:*)`, `git remote add` and `git remote set-url`, and ALLOWS `Bash(git merge:*)`. ⛔ **The opposite call to `ONBOARDING.md`'s, and the distinction is not tracking: that is the user's own notes, this is a PROJECT RULE** | [record](BOARD-ARCHIVE.md#9-two-standing-module-conditions-recorded-without-their-counts) |
| ⛔ **Same form for `tools/quality/board/register.py`** — the next row touching it splits it, and R11's reading comes from `tools.quality` rather than from this cell. ⭐ **It INHERITS the condition `tools/quality/board/__init__.py` carried, which `W129`/`W130` PERFORMED and DISCHARGED** | [record](BOARD-ARCHIVE.md#po-round-47-the-first-nine-closes-under-ruling-270-the-wall-measured-gone-on-my-own-tree-and-the-empty-population-inhabited) |
| ⛔ **Same form for `tools/quality/board/verdict.py`, a THIRD member inside `tools/quality/board/`** — the next row touching it splits it at a seam its taker NAMES before cutting. ⚠️ **No count here** (Ruling 150's form, Ruling 261) | [record](BOARD-ARCHIVE.md#w166-the-standing-split-condition-toolsqualityboardverdictpy-is-owed-third-member-inside-one-package) |
| ⛔ **Same form for `tests/visual/test_host_environment.py`, and it is a FOURTH member** — ruled [CTO round 62 §5](BOARD-ARCHIVE.md#w128-a-committed-verdict-may-not-depend-on-the-hosts-environment-ruling-225s-other-half-in-testsvisual), against the 600-line TEST ceiling, and the office disclosed it unprompted with its seam. ⚠️ **No count here** (Ruling 150's form, Ruling 261) | [record](handoffs/CTO-2026-09-11-round62.md#5-fixw128-visual-env-verdicts-the-acceptance-is-a-pair-of-readings-and-i-took-both-at-both-refs) |
| ⛔ **NO `W` ROW DISPATCHES INTO A WAVE WHERE AN OPEN-STEP ROW IS DISPATCHABLE AND UNDISPATCHED** — ⭐ **and a step whose rows are ALL MERGED is not a step with no dispatchable row, it is a step awaiting a CLOSE, so the register closes it and opens the next BEFORE any `W` row is placed into that wave** | [record](BOARD-ARCHIVE.md#the-dispatch-bound-landed-because-no-document-carried-it) |
| ⭐ **AMENDED ROUND 53 — THAT BOUND IS PRIORITY, NOT EXCLUSIVITY: it binds a slot an open-step row COULD have taken, never a slot none can fill.** ⛔ **A wave leaving such a slot EMPTY has mis-read it, and the EMPTINESS is the finding** — ⚠️ **CORRECTED round 56: this cell also read *"a slot the open step cannot fill takes the queue head"*, which is in NO record and came from round 55's own handoff** (`PO-56/2`) | [record](BOARD-ARCHIVE.md#the-dispatch-bound-and-a-queue-it-cannot-be-dispatched-into-the-bound-is-priority-not-exclusivity) |
| ⛔ **AMENDED ROUND 58 — the bound is UNTOUCHED; the POPULATION it ranges over widens to *every UNSATURATED step of the open milestone*** ([the step rule](README.md)) | [record](BOARD-ARCHIVE.md#po-round-58-the-register) |
| ⛔ **Same form for `src/studyforge/narrate/client.py`, the FIRST in `src/`** — the next row touching it splits it at the WIRE SEAM, named before cutting. ⚠️ **No count here** (Ruling 150's form) | [record](BOARD-ARCHIVE.md#amendment-po-round-56s-re-take-at-b911f44-appended-and-never-an-edit-of-what-stands-above-ruling-106-ruling-324) |
| ⛔ **Same form for `tools/quality/reach.py`, and it is a THIRD member** — `W133/4` as the reviewer widened it. ⭐ **`W133`'s taker NAMED the seam — the citation grammar as a sibling module — and refused to cut it outside their surface.** ⚠️ **No count here** (Ruling 150's form; Ruling 261: the next edit is a SPLIT, not a trim) | [record](BOARD-ARCHIVE.md#w133-checkrulingsreachs-predicate-cannot-read-the-plural-comma-list-or-range-citation-form-and-a-checks-pass-condition-is-satisfiable-by-one-undeclared-spelling) |


## Scheduled — decided now, executed later

⭐ **Recorded here so they are not rediscovered later.** Each has an owner, a
trigger that is an EVENT rather than a date, and — ⛔ **since round 42 — a STATE
from a closed set, inside its own delimiter.**

⛔ **THE DELIMITER AND THE STATE COLUMN ARE RULING 189'S FAMILY, ruled CTO round 49
in [`../conventions/board.md`](../conventions/board.md).** ⭐ **A `Trigger` cell IS
an asserted state wearing another column name, so it owes an observer; the state's
first word comes from `pending` · `fired` · `expired` · `discharged`; and the
population grows by a DELIMITER, never by inference.** ⚠️ **`W100` reads this table, and
why that made it a PO edit rather than a developer's is in `W100`'s record.**

<!-- scheduled -->
| Item | Owner | State | Trigger | Decision |
|---|---|---|---|---|
| ⭐ **SK-07 generates the corpus graph** — built, **bridged**, with the R3-safe ignore file | framework agent | `discharged` — carried into `E11` | `SK-07` is authored | ⚠️ **Bridging is the half that would have been missed: the tool alone yields ZERO doc↔code edges** |
| **SK-07 must not say "submodule"** | PO | `discharged` — `E11` corrected | `SK-07` is authored | R18's amendment reached the ruling but not the task that consumes it. The framework is a **sibling checkout at a recorded commit** |
| **Context headroom for SF-19a and SK-01/02/05/08** | PO, with CTO agreement | `discharged` — ⭐ **5 of 5 carry a `**Context**` budget, re-measured round 42** | M1 → M2 boundary, PASSED | Five tasks, not eighty-five — the discovery-shaped ones |
| **`Effort` field applied beyond the four named tasks** | PO | `fired` — ⚠️ **a STANDING trigger: it fires again and never discharges, and the closed set has no word for that** (`PO-42/4`) | as each computation-shaped task is assigned | ✅ The field exists (`README.md`), and `SF-07` and `FND-02` carry it. ⛔ Do not backfill; add it when a task is assigned and its shape is known |
| ⛔ **Back-triage the 23 pre-marker findings** | **PO** | `discharged` — re-taken round 38 at `c18df98c`, 23 of 23 | ⛔ **EXPIRED trigger — it named M1's wave open, and M1 CLOSED at `2fe56a4`** | ⭐ **`W100`'s founding case** |
| ⛔ **The `ISO-8583-jPOS-tutorial` pin is NOT advanced** | PO | `pending` | the ISO track reaches one of its TWO finish lines (Q18): `M6`'s close or `M8`'s | ⛔ **Advancing a pin ASSERTS the new HEAD is intended.** The component ADVANCED rather than diverged and the track is `in-progress`, so re-pinning pins a moving target. ⚠️ **And only the environment Ruling 40 does not make authoritative can SEE a stale pin** (Ruling 216) |
| ⛔ **`NS-01` — the DECLINE is LIFTED** | PO | `discharged` — ⭐ **round 51, `NS-01` MERGED at `0fcb6b4`** | ⛔ **`W126` merged AND ≤1 developer branch live** — ⭐ **the trigger FIRED** | ⛔ **All four grounds false or discharged** — [the ruling](BOARD-ARCHIVE.md#po-round-51-the-registers-whole-share-measured-as-a-symptom-the-open-step-found-to-admit-exactly-one-row-and-that-rows-deferral-traced-to-an-r18-decision-that-had-already-landed-before-it-was-written) |
| **R21's open rows** | CTO | ⭐ **`discharged`** — ⛔ **Ruling 351 is the act the trigger names, by the office it names** | ⛔ **`M3 step 3.4` OPENS** — the clearing act is the CTO locating a file and a version | ⛔ **POINTER, not a copy.** ⚠️ **Transcription ≠ location: [`W182`](rows/W182.md)** |
| ⛔ **`SF-32` is told that a `provides` BUMP INVALIDATES EVERY RECORDED ADDRESS** | PO | ⛔ **`fired` AND NOT MET** — ⚠️ **relayed by the coordinator: the register has no channel to that office; it `expired` this way at `SF-17`** | ⛔ **`SF-32` is assigned** — the assignment is the act, the register the office | ⭐ **`NS-05/8`, `NS-04/4`'s residual** ([the narrowing](handoffs/CTO-2026-09-12-round71.md#ns-044-a-cross-repository-coupling-narrowed-off-a-correct-branch)); ⭐ **substance in [the handoff](handoffs/PO-2026-09-12-round58.md)** |
| ⛔ **A FOURTH row `blocked` on Ruling 270's wall before `W129` lands** | framework agent | `discharged` — ⭐ **`W129` at `94a3a4b`** | a MERGED row reaches `blocked` because a FROZEN record points at its detail file | ⛔ **Ruling 288 amended 282 and this cell** — ⭐ **[the discharge](BOARD-ARCHIVE.md#nine-closes-in-one-run-at-one-ref-the-plant-its-control-and-the-population-declared-first)** |
| ⛔ **`docker/dev/compose.yaml`'s REASONING is stale while its DECISION stands** | framework agent | ⛔ **`fired` AND NOT MET** — ⭐ **`W152` owned it and merged at `3049de9` without carrying this; `W163` does** | ⛔ **whichever row next owns `docker/dev/**`** — that row landing is the act, the framework agent is the office | ⭐ **`W128/6`; the conclusion stands and the reasoning does not** |
| ⛔ **`SF-03`'s placement acceptance is RENUMBERED from the archive's own unit ordinal — or REFUSED BY NAME** | framework agent | `pending` — ⭐ **OPEN AND NAMED, never open and silent** | ⛔ **whichever row next REOPENS `SF-03`'s placement acceptance** — that row landing is the act, the framework agent is the office | ⭐ **`W138/2`, ruled as Ruling 312** — [the argument](handoffs/CTO-2026-09-11-round63.md#3a-clause-4s-first-half-my-ruling-and-it-is-ruling-312) |
<!-- /scheduled -->

---

---

## Cross-repo — the ISO-8583 integration track

| | |
|---|---|
| **Repository** | `ISO/` (`ISO-8583-jPOS-tutorial`) |
| **Owner** | PO-Integration |
| **Branch** | `release/studyforge-integration` |
| **Status** | `in-progress` — reconnaissance and delivery plan. ⛔ **The office for `M6` waits on the user** ([74](BOARD-ARCHIVE.md#po-round-74-m4-closed-at-4d3c742-and-the-order-after-it-is-m6-m8-m5-m7-then-m9-user-direction)) |
| **Closes when** | ⛔ **The track has TWO finish lines** — the corpus's (*is this a study site?*) and the exercise's (*is this framework extensible?*) — ⭐ **and asking for them as one is why it had none.** ⭐ **The corpus's is `M6`'s close and the exercise's `M8`'s (round 74).** [Q18, ruled](BOARD-ARCHIVE.md#q18-ruled-2026-09-10-the-track-has-two-finish-lines-and-that-is-why-it-had-none) |
| **The channel** | `../conventions/delivery-flow.md`, non-negotiable. ⛔ **R20: a consumer's task never cites a path inside this repository** |

⭐ **Everything PO-Integration has asked and been answered — Q5, Q18, F18–F20,
the round-4 relay, the `validate` run and its findings — is
[in the record](BOARD-ARCHIVE.md#q18-ruled-2026-09-10-the-track-has-two-finish-lines-and-that-is-why-it-had-none).**

