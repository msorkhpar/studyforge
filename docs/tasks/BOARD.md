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
| how this file is allowed to grow | [`../conventions/board.md`](../conventions/board.md) — the structural contract, and the check that enforces it |

⛔ **The rule that governs every edit to this file, and it is not new:**
`../conventions/delivery-flow.md` has said since it was written that *"a status
change is one cell"* and that an event goes to the Log rather than into the
tables. ⚠️ **Nothing enforced it, and this file reached 8,545 lines / 753 KB
(`bfb8c8c`).**
⭐ **`../conventions/board.md` is that sentence with an instrument behind it.**

---

## Milestones

⭐ **State only.** ⛔ **Which tasks are in which step is `README.md`'s;
why a close ran the way it did is the archive's.**

| Milestone | State | Ref | The close run |
|---|---|---|---|
| **M0** — foundations | ✅ CLOSED | — | [record](BOARD-ARCHIVE.md#m0-foundations) |
| **M1** — the framework stands up | ✅ CLOSED | `2fe56a4` | [record](BOARD-ARCHIVE.md#m1s-close-run-at-2fe56a4-all-nine-true-at-one-ref-and-rows-18-were-re-taken-not-inherited) |
| **M2** — a corpus is readable | ✅ CLOSED | `2d0cfe7` | [record](BOARD-ARCHIVE.md#m2s-close-run-at-2d0cfe7-nine-rows-the-fifteen-task-merges-re-derived-and-the-two-gaps-are-named-rather-than-absent) |
| **M2 step 2.1** | ✅ CLOSED | `a00337b` | [record](BOARD-ARCHIVE.md#m2-step-21s-close-run-at-a00337b-all-five-re-taken-and-the-ref-moved-twice-underneath-it) |
| **M2 step 2.2** | ✅ CLOSED | `ce80120` | [record](BOARD-ARCHIVE.md#m2-step-22s-close-run-at-ce80120-all-four-re-taken-and-the-four-merges-derived-rather-than-received) |
| **M2 step 2.3** | ✅ CLOSED | `798956c` | [record](BOARD-ARCHIVE.md#m2-step-23s-close-run-at-798956c-both-rows-re-taken-the-two-merges-derived-and-the-negative-control-is-a-synthesised-commit-because-no-branch-in-this-repository-is-unmerged) |
| **M2 step 2.4** | ✅ CLOSED | `2d0cfe7` | [record](BOARD-ARCHIVE.md#m2-step-24s-close-run-at-2d0cfe7-all-four-rows-re-taken-the-merges-derived-and-ruling-204-is-what-makes-it-clean) |
| **M3 step 3.1** | ⏳ **OPEN** | — | [opened](BOARD-ARCHIVE.md#m3-step-31-open-two-rows-no-in-step-edge-and-one-of-them-needs-a-repository-that-does-not-exist) |

⛔ **Ruling 97 binds every one of those refs: a close is a set of measurements at
ONE named ref, and no row is inherited across a ref change.**

## In flight

⛔ **A commit count is a reading with an as-of, not a state** (`PO-30/2`), so
this table names the ref it was taken at and nothing here is inherited.
⭐ **Ruling 171: `git worktree list` PRIMARY, `git branch` corroborating.**

⭐ **RE-TAKEN IN ROUND 44 AS ITS LAST ACT: stale at a base for the EIGHTH wave,
`corroborate` `3 of 3 REFUTED` at the tip, the cell `3`→`4`→`5`→`6` while the round was
written with exit `0` every time, and `wt/dev3` retired under it** — ⛔ **so a
commits-ahead cell now CARRIES ITS AS-OF, which is Ruling 246 applied to the column it
names: a bare number is false the moment a developer commits, `n @ <tip>` is true
forever, and `observation.py` reads the first integer so the column still parses**
([the re-take and every reading](BOARD-ARCHIVE.md#po-round-44-w98-closed-w126-and-w127-minted-w124-amended-not-re-minted-and-the-refuted-sibling-premise-out-of-claudemd),
`PO-44/14`–`PO-44/17`). ⛔ **THE SAME HOLDS OF THE `Checkout` COLUMN — that branch sat
at `wt/dev3`, then at NO checkout, then at `wt/dev1`, in one round** — ⭐ **so the cell
names the BRANCH, which does not move, and the checkout is written as the as-of it is**
(`PO-44/17`).

<!-- inflight -->
| Row | Owner | Checkout | Commits ahead | State |
|---|---|---|---|---|
| `W124` | framework agent | `fix/W124-W122-W123-docker-pins` @ `wt/dev1` | 6 @ `5b1528a` | in flight |
| `W122` | framework agent | `fix/W124-W122-W123-docker-pins` @ `wt/dev1` | 6 @ `5b1528a` | in flight |
| `W123` | framework agent | `fix/W124-W122-W123-docker-pins` @ `wt/dev1` | 6 @ `5b1528a` | in flight |
<!-- /inflight -->

⛔ **`corroborate` corroborates the ROW and NEVER the CELL** (`PO-42/7`, `PO-43/9`,
`PO-44/14`). ⛔ **And RULING 262 IS FALSE AS STATED: absorbing a branch is what refutes
its In-flight cell, so a merge-time exit check passes a wrong cell and fails a correct
merge — the obligation lives only at the WAVE CLOSE** (`PO-44/10`, routed).

⛔ **THE DELIMITERS ARE RULING 196'S** — ⭐ **a header is INFERRED and can only be
ANNOUNCED; a delimiter is DECLARED and can be REFUSED.** ⭐ **`W111` landed at
`923a970`; the floor reads `1 <!-- inflight --> blocks declared, 0 unreadable`.**

⚠️ **ONE BRANCH CAN CARRY TWO ROWS WITH DIFFERENT OUTCOMES** (Ruling 218): ⛔ **`W63`
DONE and `W64` STOPPED on one branch.** ⭐ **`W119` and `W100` shared one too and
closed SEPARATELY for a THIRD reason — `done` against `blocked`** (`PO-44/8`).

⛔ **The office checkouts are NOT named here, and that is one fact with one home
rather than a deletion:** ⭐ **`corroborate` prints every checkout no row names,
counted and named.** ⛔ **`W96/5` — make that exclusion DATA — was scheduled on
`W100` here and `W100` CANNOT DISCHARGE IT** (`W100/4`): ⭐ **RE-SCHEDULED ON
[`W125`](rows/W125.md), whose middle shape owes the declaration.**

## Next rows — placed, not yet taken

⛔ **A row scheduled ahead of an older unstarted row says what it is jumping and
why, in the row** (Ruling 75, `../conventions/delivery-flow.md`). ⭐ **The
argument for each placement is in the round record; this table is the outcome.**

| Order | Row | Why it is here | Placed |
|---|---|---|---|
| 1 | `W126` | ⛔ **every round since 53 has OPENED on a refuted premise and five rulings are invisible to the agents they bind** — Ruling 245 | round 44 |
| 2 | `W127` | ⛔ **3 of the 11 skips every office quotes are an INSTRUMENT DEFECT wearing a legitimate absence** — Ruling 248(e) | round 44 |
| 3 | `W115` | ⛔ **the only open row that can make a WAVE-CLOSE GATE return a false pass**, every wave runs it, and 3 of 3 cells were false at round 56 — Ruling 247(b) | round 42, promoted round 56 |
| 4 | `W128` | ⛔ **Ruling 225's OTHER half — a committed verdict depending on the host's ENVIRONMENT**, and Ruling 263 mints it because a developer may not scope a class they were not given | round 44 |
| 5 | `W78` | ⭐ **PROMOTED — one close added 8 to its population, all 8 in documents this office may not edit** | round 35, promoted round 42 |
| 6 | `W88` | ⛔ **its PREDICATE is falsified and its population GREW to 30 — re-measured at dispatch, Ruling 214** | [round 41](BOARD-ARCHIVE.md#round-41-the-queue-re-taken-and-the-coordinators-jump-against-my-placement-ratified) |
| 7 | `W120` | ⛔ **Ruling 222, and it shares `docs/tasks/rows/` with `W88`** — one owner for both | round 42 |
| 8 | `W121` | ⛔ **Ruling 218's GATE ONE, and it changes gate two's population** — before any re-take of `W64` | round 42 |
| 9 | `W103` | carries Ruling 194's disposition-liveness half by the CTO's round-50 disposition | round 40 |
| 10 | `W105`–`W109` | ⭐ **round 39's five mints**, and `W105` is UNBLOCKED — `W36` merged | round 39 |
| 11 | `W116` → `W117` → `W118` | ⭐ **round 42's remaining mints, jumping nobody** | round 42 |
| 12 | `W125` | ⛔ **it owes a DESIGN DECISION before it owes code** — Ruling 231(c), and it jumps nobody | round 43 |

⛔ **THE CELLS ARE KEYED BY ROW ID AND NOT BY ORDINAL** — ⚠️ **this paragraph once
read *"rows 1–2 do not invoke Ruling 75"*, and the ordinals stopped being true the
moment two rows were dispatched out.** ⭐ **An id resolves; a position does not.**
⛔ **And a *Next rows* cell may carry no measurement AND no PREDICTION** (243(c)).

⛔ **EIGHT ROWS HERE INVOKE RULING 75 AND EACH SAYS SO IN ITS OWN FILE — MEASURED
over every row file: `W126`, `W127`, `W115`, `W128`, `W88`, `W120`, `W121`, `W103`.**
⚠️ **This sentence said SEVEN and named `W115`, whose file had no such section;
`rows/W103.md` had none either. Both now do** (`PO-44/2`). ⭐ **`W78` jumps NOBODY.**
⚠️ **`W78`, `W88` and `W120` all write `docs/`: ONE OWNER or three waves, never
three takers in one** (check 4's sub-step) — ⭐ **while `W126` and `W127` share NO
surface and may run concurrently.**

## The register — every `W` row

⛔ **One row per id, and the id space has exactly one minter.** ⭐ **A row's
NAMING is here and nowhere else; its ARGUMENT is behind the pointer and nowhere
else.** ⚠️ **A cell in this table carries no measurement, no ref other than a
merge ref, and no reasoning** — those are the three things that go stale, and
they have exactly one home each.

<!-- register -->
| # | Row | Owner | State | Detail |
|---|---|---|---|---|
| W1 | `require_slug`/`require_ordinal` format `{value!r}`, so every caller inherits an R7 echo | Developer 2 | ✅ done — `f569d0e` | [record](BOARD-ARCHIVE.md#w1-requireslugrequireordinal-format-valuer-so-every-caller-inherits-an-r7-echo) |
| W2 | The behavioural §1f check — poison a path into each string parameter | Developer 2 | ✅ done — `f569d0e` | [record](BOARD-ARCHIVE.md#w2-the-behavioural-1f-check-poison-a-path-into-each-string-parameter) |
| W3 | The fixture whose SVG, `alt` text and lesson prose describe three different pictures | Developer 2 | ✅ done | [record](BOARD-ARCHIVE.md#w3-the-fixture-whose-svg-alt-text-and-lesson-prose-describe-three-different-pictures) |
| W4 | `handoffs/SF-05.md` still describes a constant the hotfix removed | PO | ✅ done | [record](BOARD-ARCHIVE.md#w4-handoffssf-05md-still-describes-a-constant-the-hotfix-removed) |
| W5 | `SF-10`'s port is re-priced — the file's line count is not the task's | SF-10 | routed — folded into `SF-10` | [`rows/W5.md`](rows/W5.md) |
| W6 | The R7 exception-text check — an `{exc}` interpolation re-emits what the inner refusal withheld | Developer 2 | ✅ done — `f569d0e` | [record](BOARD-ARCHIVE.md#w6-the-r7-exception-text-check-an-exc-interpolation-re-emits-what-the-inner-refusal-withheld) |
| W7 | `corpus.json` is not gated at all, so a home path in the manifest title validates green | Developer 2 | ✅ done — `f569d0e` | [record](BOARD-ARCHIVE.md#w7-corpusjson-is-not-gated-at-all-so-a-home-path-in-the-manifest-title-validates-green) |
| W8 | The dev image has no JS runtime, so a block of tests can only run off-image | Developer 1 | ✅ done — `dc4686c` | [record](BOARD-ARCHIVE.md#w8-the-dev-image-has-no-js-runtime-so-a-block-of-tests-can-only-run-off-image) |
| W9 | The markup contract has one side written — `SF-12` reviews the class names as its first act | SF-12 | ✅ done — landed in `E03` | [record](BOARD-ARCHIVE.md#w9-the-markup-contract-has-one-side-written-sf-12-reviews-the-class-names-as-its-first-act) |
| W10 | Palette tokens with no painter, as a named self-retiring list | PO → E04, E08 | `todo` — before E04 / E08 are authored | [`rows/W10.md`](rows/W10.md) |
| W11 | `api` is a generic field name and the tree guard would flag an unrelated reader | accepted | accepted — cost named | [`rows/W11.md`](rows/W11.md) |
| W12 | The extraction source's `naming.py` docstring disagrees with its own tree | accepted → E11 | accepted — cost named → E11's catalogue | [`rows/W12.md`](rows/W12.md) |
| W13 | Two copies of the personal-data gate that already disagree | Developer 2 | ✅ done — `f569d0e` | [record](BOARD-ARCHIVE.md#w13-two-copies-of-the-personal-data-gate-that-already-disagree) |
| W14 | The two missing invalid fixtures on `FND-04`'s surface, and they are one task | Developer 1 | ✅ done — `ac4ed55` | [record](BOARD-ARCHIVE.md#w14-the-two-missing-invalid-fixtures-on-fnd-04s-surface-and-they-are-one-task) |
| W15 | Tooling wrote to a source repository's root ignore file | PO → OPS-05, SK-07 | `todo` — before any adapter runs against a real source | [`rows/W15.md`](rows/W15.md) |
| W16 | The spec's canonical examples are hand-maintained copies of contracts the code owns | PO / Developer 2 | `todo` — the spec half landed; the two one-way checks are unassigned | [`rows/W16.md`](rows/W16.md) |
| W17 + W19 | One spelling of *describe a value without reproducing it*, and the remaining `{value!r}` sites | Developer 2 | `todo` — after `FND-07` | [`rows/W17.md`](rows/W17.md) |
| W18 | `user` + `authoritative` is accepted, so a reader's grader may declare itself the source's own | Developer 1 | ✅ done — `ac4ed55` | [record](BOARD-ARCHIVE.md#w18-user-authoritative-is-accepted-so-a-readers-grader-may-declare-itself-the-sources-own) |
| W20 | The repository-wide §7c check, and its migration in the same commit | Developer 2 | ✅ done | [record](BOARD-ARCHIVE.md#w20-the-repository-wide-7c-check-and-its-migration-in-the-same-commit) |
| W21 | Nothing checks for dangling pointers after a docs move | Developer 2 | `todo` — with `FND-08` | [`rows/W21.md`](rows/W21.md) |
| W22 | Finding 44 is owed to the integration catalogue, not to `SK-01` | PO | ✅ done | [record](BOARD-ARCHIVE.md#w22-finding-44-is-owed-to-the-integration-catalogue-not-to-sk-01) |
| W23 | Two personal-data shapes passed the gate clean | Developer 2 | ✅ done — `d178665` | [record](BOARD-ARCHIVE.md#w23-two-personal-data-shapes-passed-the-gate-clean) |
| W24 | A derived-set assertion asserts inhabitation, or it is born vacuous | PO | ✅ done | [record](BOARD-ARCHIVE.md#w24-a-derived-set-assertion-asserts-inhabitation-or-it-is-born-vacuous) |
| W25 | `tools/quality` gains a handoff check, because the six sections are a contract | Developer 2 | ✅ done — `2a272a5` | [record](BOARD-ARCHIVE.md#w25-toolsquality-gains-a-handoff-check-because-the-six-sections-are-a-contract) |
| W26 | `W7`'s reader tell resolves the name's origin, not its spelling | Developer 2 | `todo` — not started | [`rows/W26.md`](rows/W26.md) |
| W27 | An R7 refusal is never translated into a package's error family | Developer 2 | ✅ done — `5c6c883` | [record](BOARD-ARCHIVE.md#w27-an-r7-refusal-is-never-translated-into-a-packages-error-family) |
| W28 | `source_files()` respects the repository's own ignore declaration | Developer 1 | ✅ done — `6d65902` | [record](BOARD-ARCHIVE.md#w28-sourcefiles-respects-the-repositorys-own-ignore-declaration) |
| W29 | One constant naming the three gated trees | Developer 2 | ✅ done — `4f2fbf8` | [record](BOARD-ARCHIVE.md#w29-one-constant-naming-the-three-gated-trees) |
| W30 | `PYTHONPYCACHEPREFIX` in the dev image — isolation that is structural | framework agent | ✅ done — `3d0eb34` | [record](BOARD-ARCHIVE.md#w30-pythonpycacheprefix-in-the-dev-image-isolation-that-is-structural) |
| W31 | `DOCUMENT_KINDS` names two roles where three produce these documents | framework agent | ✅ done — `3d0eb34` | [record](BOARD-ARCHIVE.md#w31-documentkinds-names-two-roles-where-three-produce-these-documents) |
| W32 | The mixed-form contents fixture, taken from real material | framework agent | `todo` — re-routed to `SF-13`'s acceptance, no longer a queue row | [`rows/W32.md`](rows/W32.md) |
| W33 | The floor prints its lint state, absence included, as a notice | framework agent | ✅ done — `3a45d4c` | [record](BOARD-ARCHIVE.md#w33-the-floor-prints-its-lint-state-absence-included-as-a-notice) |
| W34 | `review-rubric.md`'s operational checklist, and the document has no index | framework agent | `todo` — unblocked | [`rows/W34.md`](rows/W34.md) |
| W35 | `pointers.py` honours the ignore declaration | framework agent | `todo` — queued last | [`rows/W35.md`](rows/W35.md) |
| W36 | A browser in the pinned dev image, checksum-pinned | framework agent | ✅ done — `5f7734b` | [record](BOARD-ARCHIVE.md#w36-a-browser-in-the-pinned-dev-image-checksum-pinned) |
| W37 | The repo-wide sweep for checks that cannot fail by construction | framework agent | `todo` | [`rows/W37.md`](rows/W37.md) |
| W38 | The floor and `ruff` disagree by rule; pin the divergence with a test | framework agent | `todo` — after `W40` | [`rows/W38.md`](rows/W38.md) |
| W39 | The index goes stale on every merge, so the release tip is red after each one | framework agent | ✅ done — `16049d2` | [record](BOARD-ARCHIVE.md#w39-the-index-goes-stale-on-every-merge-so-the-release-tip-is-red-after-each-one) |
| W40 | No module in the tree sits at zero headroom against R11 | framework agent | `todo` — free | [`rows/W40.md`](rows/W40.md) |
| W41 | An R7 refusal borrows the absent state's reason, and the reason is false | framework agent | `todo` — free | [`rows/W41.md`](rows/W41.md) |
| W42 | The marker check judges some documents and reports a verdict for all of them | framework agent | `todo` — collides with `W48` | [`rows/W42.md`](rows/W42.md) |
| W43 | Two clauses `agent-protocol.md` is owed | framework agent | ✅ done — `2caa0d2` | [record](BOARD-ARCHIVE.md#w43-two-clauses-agent-protocolmd-is-owed) |
| W44 | `validate/source.py` stood over R11's ceiling on a deferral naming this row | framework agent | ✅ done — `7b5c0a9` | [record](BOARD-ARCHIVE.md#w44-validatesourcepy-stood-over-r11s-ceiling-on-a-deferral-naming-this-row) |
| W45 | `size_exception()` returns the marker line, so a wrapped row id prints with no id | framework agent | ✅ done — `1aa6319` | [record](BOARD-ARCHIVE.md#w45-sizeexception-returns-the-marker-line-so-a-wrapped-row-id-prints-with-no-id) |
| W46 | A finding states, per claim, whether its reading was measured or received | framework agent | `todo` | [`rows/W46.md`](rows/W46.md) |
| W47 | `agent-protocol.md` has no index, and its own clause has ruled `grep` unsafe on it | framework agent | `todo` | [`rows/W47.md`](rows/W47.md) |
| W48 | `W43`'s two clauses have no enforcement arm | framework agent | `todo` | [`rows/W48.md`](rows/W48.md) |
| W49 | Live acceptance conditions that name no instrument which can return `no` | framework agent | `todo` | [`rows/W49.md`](rows/W49.md) |
| W50 | An installed `studyforge` ships the skills' code without their procedures | framework agent | `todo` | [`rows/W50.md`](rows/W50.md) |
| W51 | `ARCHIVE_DIR` and `ARCHIVE_ROOT_NAME` are on no package surface | framework agent | `todo` | [`rows/W51.md`](rows/W51.md) |
| W52 | A `Size exception:` on a file under its ceiling is read by nothing the build ships | framework agent | `todo` | [`rows/W52.md`](rows/W52.md) |
| W53 | A clause naming an instrument is not final until its author has run it both ways | framework agent | `todo` | [`rows/W53.md`](rows/W53.md) |
| W54 | An onboarded corpus's knowledge graph is built, bridged and its census asserted | framework agent | `todo` | [`rows/W54.md`](rows/W54.md) |
| W55 | A decision — is an installed `studyforge` a supported host for an onboarded corpus? | framework agent | `todo` | [`rows/W55.md`](rows/W55.md) |
| W56 | `reconnaissance/proposal._choices` raises one `Uncertainty` per excluded path | framework agent | `todo` | [`rows/W56.md`](rows/W56.md) |
| W57 | `render/page/text.py`'s `SAFE_SCHEMES` refuses a bare same-directory relative href | framework agent | `todo` | [`rows/W57.md`](rows/W57.md) |
| W58 | The zero marker beside a real finding is a build failure | framework agent | `todo` | [`rows/W58.md`](rows/W58.md) |
| W59 | `_escape` crosses a package boundary as a private name; the fix is to move it | framework agent | ✅ done — `a37f827` | [record](BOARD-ARCHIVE.md#w59-escape-crosses-a-package-boundary-as-a-private-name-the-fix-is-to-move-it) |
| W60 | Two copies of one vocabulary, unlinked, inert, and wire-shaped | framework agent | `todo` | [`rows/W60.md`](rows/W60.md) |
| W61 | Two shipped skills gave a command that does not exist, in a fence | framework agent | ✅ done — `ad27ed2` | [record](BOARD-ARCHIVE.md#w61-two-shipped-skills-gave-a-command-that-does-not-exist-in-a-fence) |
| W62 | The latent `Owns` cells, and a trigger that cannot be shelved | PO | `todo` | [`rows/W62.md`](rows/W62.md) |
| W63 | The marker vocabulary's closed check | framework agent | ✅ done — `0183cd1` | [record](BOARD-ARCHIVE.md#w63-the-marker-vocabularys-closed-check) |
| W64 | The kind gate widened across the whole document floor | framework agent | `todo` — ⛔ **STOPPED and RE-SCOPED**, Ruling 218; gated on `W121` | [`rows/W64.md`](rows/W64.md) |
| W65 | R7's third subject has no sweep | framework agent | `todo` | [`rows/W65.md`](rows/W65.md) |
| W66 | The non-ASCII narrowing, and the emitter disagrees with the gate | framework agent | `todo` | [`rows/W66.md`](rows/W66.md) |
| W67 | The two zero-headroom test modules | framework agent | `todo` — ahead of any row adding a test to `corpus/container` or `corpus/manifest` | [`rows/W67.md`](rows/W67.md) |
| W68 | The gate walk derives from the tree, not the disk | framework agent | ✅ done — merged late in round 34 | [record](BOARD-ARCHIVE.md#w68-the-gate-walk-derives-from-the-tree-not-the-disk) |
| W69 | A closed check refusing a bare task-count literal | framework agent | `todo` | [`rows/W69.md`](rows/W69.md) |
| W70 | Every Acceptance clause expressible as an `Acceptance` | framework agent | ✅ done — `8b4c92b` | [record](BOARD-ARCHIVE.md#w70-every-acceptance-clause-expressible-as-an-acceptance) |
| W71 | The tilde arm, and both callers over all three shapes | framework agent | `todo` | [`rows/W71.md`](rows/W71.md) |
| W72 | `pinned` vs `tracked` in `workspace.json` | framework agent | `todo` — re-scoped round 34 | [`rows/W72.md`](rows/W72.md) |
| W73 | `E11`'s delivery-skill comparison, re-pointed by its taker at the corpus they own | INTEGRATION side | in-progress — taken, re-pointed | [`rows/W73.md`](rows/W73.md) |
| W74 | The sibling runnable-module check widens | framework agent | ✅ done — `a3efb12` | [record](BOARD-ARCHIVE.md#w74-the-sibling-runnable-module-check-widens) |
| W75 | No document says how `studyforge` gets on the path | framework agent | `todo` | [`rows/W75.md`](rows/W75.md) |
| W76 | `render.page`'s five cross-package helpers are private and every renderer imports them | framework agent | ✅ done — `c3e2919` | [record](BOARD-ARCHIVE.md#w76-renderpages-five-cross-package-helpers-are-private-and-every-renderer-imports-them) |
| W77 | The corpus-scale comparison for `SF-14`, `SF-15` and `SF-27` | E09 | routed — folded into `E09`'s delivery, `W5`'s precedent | [`rows/W77.md`](rows/W77.md) |
| W78 | Citations into files a live document does not own — a line number that moves, and a `rows/<ID>.md` a close DELETED | framework agent | `todo` — minted round 35, widened rounds 40 and 41 | [`rows/W78.md`](rows/W78.md) |
| W79 | Two small carries — each of THREE golden regenerators names the other two, and the census comment cites its command | framework agent | `todo` — minted round 35, widened round 37 | [`rows/W79.md`](rows/W79.md) |
| W80 | `SF-19b`'s Acceptance names a consumer corpus by ROLE, and owes an instrument or a disposition | PO | `todo` | [`rows/W80.md`](rows/W80.md) |
| W81 | `SK-03`'s consumer-corpus Acceptance clause, the same class | PO | `todo` | [`rows/W81.md`](rows/W81.md) |
| W82 | `SK-04`'s consumer-corpus Acceptance clause, the same class | PO | `todo` | [`rows/W82.md`](rows/W82.md) |
| W83 | `TC-00`'s consumer-corpus Acceptance clause, the same class | PO | `todo` | [`rows/W83.md`](rows/W83.md) |
| W84 | `SK-01`'s consumer-corpus Acceptance clause, answered by Ruling 166 | PO | ✅ done — Ruling 166, `911c56f` | [record](BOARD-ARCHIVE.md#w84-sk-01s-consumer-corpus-acceptance-clause-answered-by-ruling-166) |
| W85 | The board instrument's six carries — Rulings 182 and 183, and `CTO-47/3`, `/4`, `/5` | Developer 2 | ✅ done — `d430f34` | [record](BOARD-ARCHIVE.md#w85-the-board-instruments-six-carries-rulings-182-and-183-and-cto-473-4-5) |
| W86 | Ruling 184's two clauses into check 3, and the 74 frozen lines `W85` is what unfreezes | Developer 2 | ✅ done — `d430f34` | [record](BOARD-ARCHIVE.md#w86-ruling-184s-two-clauses-into-check-3-and-the-74-frozen-lines-w85-is-what-unfreezes) |
| W87 | `board_state`'s notice prints the row files whose argument IS their own naming cell | Developer 2 | ✅ done — `d430f34` | [record](BOARD-ARCHIVE.md#w87-boardstates-notice-prints-the-row-files-whose-argument-is-their-own-naming-cell) |
| W88 | The thin row files gain an ANCHORED pointer, and four lose a dangling deictic | PO | `todo` — ⭐ **UNBLOCKED, `W91` merged** | [`rows/W88.md`](rows/W88.md) |
| W89 | An R7 gate's false positive on ordinary source, narrowed in the gate and not in the source | framework agent | `todo` — Ruling 179 | [`rows/W89.md`](rows/W89.md) |
| W90 | The root index can link no container page, and it is a `toc_api` question | PO | `todo` — owed by M4 | [`rows/W90.md`](rows/W90.md) |
| W91 | The hand-maintained rulings index stops short of the live series, so a bare `(Ruling n)` resolves to nothing | Developer 2 | ✅ done — `8be7e86` | [record](BOARD-ARCHIVE.md#w91-the-hand-maintained-rulings-index-stops-short-of-the-live-series-so-a-bare-ruling-n-resolves-to-nothing) |
| W92 | The capability index cannot say *not this side*, so a reading-floor corpus writes 13 false `why`s | framework agent | `todo` | [`rows/W92.md`](rows/W92.md) |
| W93 | *Point the skill at a corpus* is not performable — no corpus-shaped input on the surface | framework agent | `todo` | [`rows/W93.md`](rows/W93.md) |
| W94 | A shipped refusal names its first witness, not its population — 6 sites against 55 correct | framework agent | `todo` — Ruling 188 | [`rows/W94.md`](rows/W94.md) |
| W95 | No fixture has two units sharing one source file, so `Q23`'s answer cannot be tested | framework agent | ✅ done — `cfe0e0c` | [record](BOARD-ARCHIVE.md#w95-no-fixture-has-two-units-sharing-one-source-file-so-q23s-answer-cannot-be-tested) |
| W96 | A cell declaring a started state asserts a live checkout or a branch ahead of release | framework agent | ✅ done — `3432e9a` | [record](BOARD-ARCHIVE.md#w96-a-cell-declaring-a-started-state-asserts-a-live-checkout-or-a-branch-ahead-of-release) |
| W97 | `\|clips\| == \|spoken units\|` — *both directions* proves surjectivity, not injectivity | framework agent | `todo` — Ruling 187, before `SF-16` | [`rows/W97.md`](rows/W97.md) |
| W98 | `QA-03`'s harness judges 2 of 6 chrome regions — `site.py` passes no `links` and builds one page kind | framework agent | ✅ done — `8416924` | [record](BOARD-ARCHIVE.md#w98-qa-03s-harness-judges-2-of-6-chrome-regions-sitepy-passes-no-links-and-builds-one-page-kind) |
| W100 | A `## Scheduled` cell declares no state, so the one instrument that reads states cannot read it | framework agent | `blocked` — ⛔ **DELIVERED and MERGED `6d5aeed`; its CLOSE is blocked, `PO-44/8`** | [`rows/W100.md`](rows/W100.md) |
| W101 | Check 4's sub-step compares `Owns` to a diff, and `Owns` is brace expansion and directory prefixes | framework agent | `todo` — `CTO-48/12`, before the next parallel pair | [`rows/W101.md`](rows/W101.md) |
| W102 | Check 3's pattern is case-sensitive, and the house style writes `RULING <n>` | framework agent | ✅ done — Ruling 184(c), `4e8ba86` | [record](BOARD-ARCHIVE.md#w102-check-3s-pattern-is-case-sensitive-and-the-house-style-writes-ruling-n) |
| W103 | A finding's disposition lives only in a frozen record, so `FND-04`'s reads `OPEN` after `SF-09` closed it | PO | `todo` | [`rows/W103.md`](rows/W103.md) |
| W104 | The lint notice names no subject, and `ruff format` formats Markdown as well as Python | framework agent | `todo` — not `W38`'s subject | [`rows/W104.md`](rows/W104.md) |
| W105 | The region census has no authorable population, so a region the templates emit and nothing paints is unsayable | framework agent | `todo` — Ruling 192, ⭐ **UNBLOCKED, `W36` merged** | [`rows/W105.md`](rows/W105.md) |
| W106 | The repository-wide marker sweep has no shipped reader, so one vocabulary has three copies | framework agent | `todo` — Ruling 103's class | [`rows/W106.md`](rows/W106.md) |
| W107 | `FRAGMENT` and `anchor()` are composed in two packages, and the shared-name rule gives them to neither | framework agent | `todo` — `SF-15/1` | [`rows/W107.md`](rows/W107.md) |
| W108 | No fixture crosses a module boundary inside one section, so a renderer can pass the clause and be wrong | framework agent | `todo` — `SF-15/6`, before `SF-27` | [`rows/W108.md`](rows/W108.md) |
| W109 | Every consumer that reads `origin` from a document instead of the parser is a second reader of a growing field | framework agent | `todo` — `W95/3` | [`rows/W109.md`](rows/W109.md) |
| W110 | `corroborate`'s live-checkout arm discharges a branch git already knows is SPENT, so a leaked worktree keeps a stale row green | framework agent | ✅ done — `923a970` | [record](BOARD-ARCHIVE.md#w110-corroborates-live-checkout-arm-discharges-a-branch-git-already-knows-is-spent-so-a-leaked-worktree-keeps-a-stale-row-green) |
| W111 | Ruling 196's expiry — the header locator ANNOUNCES where a delimiter can REFUSE, and the delimiters have landed | framework agent | ✅ done — `923a970` | [record](BOARD-ARCHIVE.md#w111-ruling-196s-expiry-the-header-locator-announces-where-a-delimiter-can-refuse-and-the-delimiters-have-landed) |
| W112 | A browser clause discharged on a HOST reading owes a COMMITTED check, or no second office can reproduce it | framework agent | `todo` — `SF-30/1`, Ruling 204, ⭐ **UNBLOCKED, `W36` merged** | [`rows/W112.md`](rows/W112.md) |
| W113 | `Address(tuple(<str>))` is accepted and splits a string into one segment per character | framework agent | `todo` — `SF-30/2`, `SF-12`'s contract | [`rows/W113.md`](rows/W113.md) |
| W114 | R11's ceiling has no instrument outside `.py`, so an authored asset at the ceiling is invisible to the gate | framework agent | `todo` — Ruling 207 | [`rows/W114.md`](rows/W114.md) |
| W115 | A failed git reading is coerced to a number, so *git could not answer about this branch* lands on REFUTED and one arm exits `0` | framework agent | `todo` — Ruling 216 | [`rows/W115.md`](rows/W115.md) |
| W116 | The formatter's target is INFERRED, so an absent declaration made a style decision no document records | framework agent | `todo` — Ruling 210 | [`rows/W116.md`](rows/W116.md) |
| W117 | `**Consumer-side modules:**` is a contract named in ZERO convention documents, and both its sites are consumers | framework agent | `todo` — `W74/3` | [`rows/W117.md`](rows/W117.md) |
| W118 | A gap named in FOUR consecutive closes is a different fact from a gap named once, and no instrument reads it | PO | `todo` — `CTO-52/5` | [`rows/W118.md`](rows/W118.md) |
| W119 | A committed test reads THIS MACHINE'S worktree set, so it goes RED on a correct tree in the window after every merge | framework agent | ✅ done — `6d5aeed` | [record](BOARD-ARCHIVE.md#w119-a-committed-test-reads-this-machines-worktree-set-so-it-goes-red-on-a-correct-tree-in-the-window-after-every-merge) |
| W120 | The bounded Ruling 186 notice is discharged by ONE row over its WHOLE population, and a partial fix is refused | framework agent | `todo` — Ruling 222 | [`rows/W120.md`](rows/W120.md) |
| W121 | The marker reader cannot see a finding written as a TABLE ROW, which is the form both offices write | framework agent | `todo` — Ruling 218's gate one, before `W64` | [`rows/W121.md`](rows/W121.md) |
| W122 | A count in a SHIPPED file that no unit makes true — the Dockerfile's *"21 shared libraries"* | framework agent | in flight — Ruling 240 | [`rows/W122.md`](rows/W122.md) |
| W123 | A hang has no deadline anywhere, so a wedged suite returns no reading and no exit code either | framework agent | in flight — Ruling 235(d) | [`rows/W123.md`](rows/W123.md) |
| W124 | `0` apt packages are version-constrained, so a font is an undeclared input to a recorded number | framework agent | in flight — ⛔ **Ruling 236; it now gates a hole the SUITE declares, `W98` having closed** | [`rows/W124.md`](rows/W124.md) |
| W125 | The In flight table is ASSERTED, and generating it naively leaves `corroborate` asserting git against itself | framework agent | `todo` — Ruling 231(c), routed and never minted | [`rows/W125.md`](rows/W125.md) |
| W126 | Rulings 217–241 reached NO convention document, 0 of 25, and the tail has no instrument asserting they ever will | CTO | `todo` — Ruling 245, routed round 56 | [`rows/W126.md`](rows/W126.md) |
| W127 | `tests/test_knowledge_index.py` ships a second workspace resolver, so 3 of the 11 skips are a defect | framework agent | `todo` — Ruling 248(e) | [`rows/W127.md`](rows/W127.md) |
| W128 | A committed verdict may not depend on the host's ENVIRONMENT — Ruling 225's other half, in `tests/visual/` | framework agent | `todo` — Ruling 263 | [`rows/W128.md`](rows/W128.md) |
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
| **narration manifest** — no file, no version | `NS-02` / `SF-17` (M3) | CTO |
| **coverage report** — no file | `EX-05` (M7) | CTO |

⭐ **Neither is due in the open milestone.** ⛔ **The reasoning — why R21 exists,
what each closed row cost, and the ruling that a contract version is minted in
the register of the document that carries the key — is
[in the record](BOARD-ARCHIVE.md#r21-the-register-of-unlocated-contracts).**

## Standing decisions

⭐ **A decision that binds every agent and is not a task.** ⛔ **The decision is
here; the argument is in the record.**

| Decision | Argument |
|---|---|
| **`ONBOARDING.md` does not enter the repository** — not tracked, not corrected into the tree, and not deleted, because it is untracked and therefore not repository state | [record](BOARD-ARCHIVE.md#onboardingmd-ruled-it-does-not-enter-the-repository) |
| ⭐ **`.claude/settings.json` IS tracked, and it is R18 with a machine behind it** — it DENIES `Bash(git push:*)`, `git remote add` and `git remote set-url`, and ALLOWS `Bash(git merge:*)`. ⛔ **The opposite call to `ONBOARDING.md`'s, and the distinction is not about tracking: that file is the user's own notes, this one is a PROJECT RULE, and a rule that protects one untracked checkout protects no worktree** | [record](BOARD-ARCHIVE.md#9-two-standing-module-conditions-recorded-without-their-counts) |
| ⛔ **A row that touches `render/page/navigation.py` SPLITS IT, at the seam named in [`handoffs/SF-15.md`](handoffs/SF-15.md)** — the condition binds the NEXT row, never the row that left the file where it is. ⭐ **No count here: the count is the floor's and goes stale on the next edit** (Ruling 150's form) | [record](BOARD-ARCHIVE.md#9-two-standing-module-conditions-recorded-without-their-counts) |
| ⛔ **Same form for `tools/quality/board/__init__.py`** — the next row touching it splits it, and R11's reading comes from `tools.quality` rather than from this cell | [record](BOARD-ARCHIVE.md#9-two-standing-module-conditions-recorded-without-their-counts) |


## Scheduled — decided now, executed later

⭐ **Recorded here so they are not rediscovered later.** Each has an owner, a
trigger that is an EVENT rather than a date, and — ⛔ **since round 42 — a STATE
from a closed set, inside its own delimiter.**

⛔ **THE DELIMITER AND THE STATE COLUMN ARE RULING 189'S FAMILY, ruled CTO round 49
in [`../conventions/board.md`](../conventions/board.md).** ⭐ **A `Trigger` cell IS
an asserted state wearing another column name, so it owes an observer; the state's
first word comes from `pending` · `fired` · `expired` · `discharged`; and the
population grows by a DELIMITER, never by inference.** ⚠️ **`W100` is the row that
reads this table, and it could not be built until the table existed — the same
shape as `W96`/`W111`'s `<!-- inflight -->` markers, which is why this is a PO
board edit and not a developer's.**

<!-- scheduled -->
| Item | Owner | State | Trigger | Decision |
|---|---|---|---|---|
| ⭐ **SK-07 generates the corpus graph** — built, **bridged**, with the R3-safe ignore file | framework agent | `discharged` — carried into `E11` | `SK-07` is authored | The highest graphify exposure converted into a generated artifact, closing an R19 hole in the same edit. ⚠️ Bridging is the part that would have been missed: a graph built by running the tool alone has **zero** doc↔code edges |
| **SK-07 must not say "submodule"** | PO | `discharged` — `E11` corrected | `SK-07` is authored | R18's amendment reached the ruling but not the task that consumes it. The framework is a **sibling checkout at a recorded commit** |
| **Context headroom for SF-19a and SK-01/02/05/08** | PO, with CTO agreement | `discharged` — ⭐ **5 of 5 carry a `**Context**` budget in their epic, re-measured round 42** | M1 → M2 boundary, PASSED | Five tasks, not eighty-five. They are the discovery-shaped ones, where you do not know the name of the thing you are looking for — `query`'s weak case |
| **`Effort` field applied beyond the four named tasks** | PO | `fired` — ⚠️ **a STANDING trigger: it fires again and never discharges, and the closed set has no word for that** (`PO-42/4`) | as each computation-shaped task is assigned | ✅ The field exists (`README.md`), and `SF-07` and `FND-02` carry it. ⛔ Do not backfill; add it when a task is assigned and its shape is known |
| ⛔ **Back-triage the 23 pre-marker findings** — `FND-01` (5), `FND-02` (8), `FND-04` (10) | **PO** | `discharged` — re-taken round 38 at `c18df98c`, 23 of 23 carrying a marker AND a disposition | ⛔ **EXPIRED trigger — it named M1's wave open, and M1 CLOSED at `2fe56a4`** | ⭐ **The work discharged itself round by round while this cell could not say so. That is `W100`'s founding case, and this row is now the proof the column was needed** |
| ⛔ **The `ISO-8583-jPOS-tutorial` pin is NOT advanced** | PO | `pending` | the ISO track reaches one of its TWO finish lines (Q18) | ⛔ **Advancing a pin ASSERTS the new HEAD is intended.** The component ADVANCED rather than diverged — the pin is still an ancestor — and the track is `in-progress`, so re-pinning now pins a moving target. ⚠️ **And the only environment that can SEE a stale pin is the one Ruling 40 does not make authoritative** (Ruling 216) |
| ⛔ **`NS-01` is NOT dispatched** — no sibling `narrate-service` | PO | `pending` — ⭐ **the DECLINE is RATIFIED, only the TRIGGER moved** (Ruling 248(c)) | ⛔ **`W126` merged AND ≤1 developer branch live** — ⭐ **the second half is SATISFIED, so `W126`'s merge is all that holds it** (Ruling 256) | ⭐ **Two of four reasons survive and suffice: scope creep, and `NS-01` is an `E13` task opened by `README.md`'s ordering, not by a handoff.** ⛔ **The reason that collapsed — *a worktree carries no siblings* — is REFUTED (Ruling 248(a)), which is why `W126` gates it |
| **R21's open rows** | CTO | `pending` — neither is due in the open milestone | each before its named task builds | ⛔ **POINTER, not a second copy — the open set is `## R21` above, and that section resolves from spec §R9.** ⚠️ **The narrative this replaces typed a COUNT that disagreed with `## R21` on the same board** — ⭐ **re-taken round 38 against §R9's own table and routed to the CTO, whose register it is** |
<!-- /scheduled -->

---

---

## Cross-repo — the ISO-8583 integration track

| | |
|---|---|
| **Repository** | `ISO/` (`ISO-8583-jPOS-tutorial`) |
| **Owner** | PO-Integration |
| **Branch** | `release/studyforge-integration` |
| **Status** | `in-progress` — reconnaissance and delivery plan |
| **Closes when** | ⛔ **The track has TWO finish lines** — the corpus's (*is this a study site?*) and the exercise's (*is this framework extensible?*) — ⭐ **and asking for them as one is why it had none.** [Q18, ruled](BOARD-ARCHIVE.md#q18-ruled-2026-09-10-the-track-has-two-finish-lines-and-that-is-why-it-had-none) |
| **The channel** | `../conventions/delivery-flow.md`, non-negotiable. ⛔ **R20: a consumer's task never cites a path inside this repository** |

⭐ **Everything PO-Integration has asked and been answered — Q5, Q18, F18–F20,
the round-4 relay, the `validate` run and its findings — is
[in the record](BOARD-ARCHIVE.md#q18-ruled-2026-09-10-the-track-has-two-finish-lines-and-that-is-why-it-had-none).**

---

## Where everything else went, and why it is not here

| It was | It is now | Because |
|---|---|---|
| every round's reasoning — rounds 25 → 34, the close runs, the mint arguments, the carried rulings | [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md), **moved whole and unedited** | ⛔ **A record is corrected by annotating beneath, never by editing** (Ruling 106). ⭐ **Nothing was summarised** — the round-25 split's own standing rule, and this move keeps it |
| the full argument for a live row | `rows/<ID>.md`, one file per row | ⭐ **A live row's argument is AMENDED — re-scoped, re-framed, struck.** ⛔ **A record cannot be amended, so a live argument may not live in one** |
| the wave checks, and how this board is maintained | [`../conventions/board.md`](../conventions/board.md) | ⛔ **A process is not a state.** ⭐ **A convention is where a rule lives; a board is where a reading lives** |
| the Log | [`BOARD-ARCHIVE.md`](BOARD-ARCHIVE.md) | unchanged — it was already there |

⛔ **If a fact appears both here and behind a pointer, ONE OF THE TWO IS WRONG,
and it is a finding.** ⭐ **When a fact changes, exactly one file changes.**
