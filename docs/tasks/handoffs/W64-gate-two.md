# W64 — handoff

**Kind:** task handoff — W64

⛔ **This is the SECOND handoff for `W64`, and it does not replace the first.**
⭐ **[`W64.md`](W64.md) is the STOP** — the taker who widened the gate, dry-ran
it, and refused to force exit `0` — ⛔ **and Ruling 218 RATIFIED that refusal, so
Ruling 106 protects it as a record and it is not edited here, not even its
`Status:` line.** ⚠️ **Its finding ids `W64/1`–`W64/5` are minted; this document
continues at `W64/6`.** ⚠️ **Writing over it was what my brief directed —
`W64/6` below, UPHELD and disposed by Ruling 346, which now says in the rubric
that a re-taken row MAY carry a second handoff on a new stem pointing back.**

## Status

⭐ **Done — GATE TWO ONLY, and exit `0` was not aimed at** (Ruling 218). Branch
`fix/W64-kind-gate-scope`, cut at `7a7a178`, **code tip `6f156a3`**, and the
branch tip is this document's own commit — one document, no code. ⛔ Not merged
and not pushed; no remote was added, set or queried, and this checkout has none.
⭐ Every commit is authored `dev1 <dev1@example.invalid>`, **passed per
invocation with `git -c user.name=… -c user.email=…` and NEVER with
`git config`** — ⛔ **which is Ruling 296 as Ruling 345 now spells it, and
`W64/14` is one of the two independent findings behind that ruling.**

### ⛔ Round 70: CHANGES REQUESTED at `5b31436`, discharged here

⛔ **`CTO-70/9` is the whole of the required change and it is UPHELD IN FULL:**
two figures in the coupling table reproduced under no unit, because the pair was
**derived and not measured**. ⭐ **That section is REPLACED** — one instrument
reading both columns in one process, at two named refs, with the three units
named and distinguished. The re-derivation is printed beside the table it
replaces, and the cause is named to the digit.

⚠️ **Nothing else was asked of me.** `W64/6` is disposed by Ruling 346 and this
document already complied; `W64/11` is UPHELD and independently reproduced — a
planted `QQQ-999/1` produced 0 findings, confirming that refusing to ship the
citation rule left a real residue and not an imagined one.

⛔ **This tip is NOT covered by that verdict.** The bracket
`(CTO: CHANGES REQUESTED)` was ruled at `5b31436` and nowhere else; it is not
mine to carry forward, and nothing here should be merged on it.

⛔ **The row prices three gates and this document ships one.** Gate one was
`W121` and merged this wave. ⭐ **Gate two — a declarable scope for
`ruling record` — is what landed here.** ⚠️ **Gate three — a rule separating a
record's Findings section from its prose — is NOT YET A ROW and is deliberately
not minted, so its residue is MEASURED below and not chased** (Ruling 193).

## What landed

Four files, one of them new source and one of them its R12 mirror.

- **`tools/quality/handoffs/records.py`** — new, 178 lines of 400. Holds the
  derivation Ruling 219 described and never shipped (`W121/2`), and the check
  that uses it. `derived_scope(stem)`, `record_scopes(stem, declared)`,
  `check_record(relative, stem, declared, text)`.
- **`tools/quality/handoffs/__init__.py`** — 331 lines of 400. `check_handoffs`
  no longer returns at the kind test for a `ruling record`; the registry
  sentence for that kind stopped saying *owes nothing further*, because it now
  owes a scope.
- **`tools/quality/handoffs/contract.py`** — 330 lines of 400.
  `check_finding_ids` gains one keyword, `cites_elsewhere`, and its legacy
  message stopped indexing `ids[0]` unconditionally.
- **`tools/tests/quality/handoffs/test_records.py`** — new, 188 lines of 600.
  17 tests, of which **5 go red with the gate removed and everything else left
  in place**; the counterfactual is in **Readings**.

⭐ **A record's scope is DERIVED from its filename** —
`CTO-2026-09-12-round69.md` files inside `CTO-69` — **and MAY be declared beside
it.** ⛔ **Zero record edits, which is the whole of Ruling 219's re-pricing.**

⛔ **It did not ship behind a flag** (the row's own clause, and `W37`).

## Decisions

### ⛔ What the gate now applies to a record, and what it deliberately does not

⭐ **Applied:** the record's scope declaration, and `check_finding_ids` over the
record's own finding lines.

⛔ **NOT applied, and this is gate three's, not mine:** `check_markers` (the
prose-marker rule), `check_sections` (the six), and *marks no finding*. ⚠️
**Measured residue if they were applied — my instrument, my ref, in
`For dependents`: 220 findings in 73 documents from the two marker rules, plus
427 `handoff-section` findings that a record should never have owed.** ⛔ Turning
any of those on today would print the exit-`0` chase Ruling 193 forbids.

⭐ **`test_a_record_is_held_to_neither_the_marker_rule_nor_the_six_sections`
pins that absence**, so widening it later is a visible decision rather than a
quiet one.

### ⛔ The office's own spelling is READ, not corrected

⚠️ **37 of the 106 records already declare a scope**, in the spelling the
offices actually write: `**Kind:** ruling record — CTO round 69`. ⛔ **Nothing
in the tree read it** — `check_handoffs` returned before the ids were used — so
those 37 declarations were free text. ⭐ `_ROUND_DECLARATION` normalises
`<OFFICE> round <N>` to `<OFFICE>-<N>`, and `<OFFICE>-<N>` is accepted directly.

⛔ **Demanding this module's punctuation would have been 37 record edits for no
reading gained**, which is the shape Ruling 219 re-priced the row away from.
**Measured: all 37 normalise to the scope their own filename derives, zero
disagreements.**

### ⛔ For a record, a scope it does not own is a CITATION — the one rule that inverts

⚠️ **A task handoff numbering `W91/1` inside `W99.md` has taken another task's
name, and that stays refused.** ⭐ **A review record's disposition table does
exactly that on purpose**, because the row it reviewed is where those findings
are numbered — Ruling 219's single named disagreement (`CTO-51` routing to
`W91`) was this, and it is now 170 lines in 14 documents.

⭐ **The inversion is asserted as a PAIR in one test**
(`test_a_record_CITES_another_scope_and_a_handoff_TAKES_it`), which is `W121`'s
discipline: the two halves cannot drift apart if one test holds both.

### ⛔ A rule I MEASURED GREEN and then REFUSED to ship

⭐ **The obvious way to stop `cites_elsewhere` being a hole is to require the
cited scope to EXIST.** ⚠️ **I built it and measured it: over the 170 citation
lines, resolved 170, dangling 0**, against a universe of 308 scopes assembled
from declared task IDs, office scopes, derived record scopes and the row files.

⛔ **I did not ship it, and the reason is the reason this row was stopped once
already.** ⚠️ **Its failure mode is a red nobody may discharge:** the citation
lives inside a record, a record is annotated and never edited (Ruling 106), so
the day a row file is retired the floor goes red and the only repair is
forbidden. ⭐ **A check whose failure cannot be fixed is worse than the hole it
closes.** ⚠️ Routed to gate three's row as `W64/11`, with the reading, so the
next taker inherits the measurement and not the idea.

### ⛔ `survey` is measured in the population and NOT admitted

⚠️ **Every reading this row inherited measured *records + surveys*** — 109 at my
ref, of which **3** are surveys. ⛔ **The row names ONE kind.** ⭐ Admitting a
second is a decision the row does not make, so `test_a_survey_is_still_outside_this_gate`
pins it and the 3 are reported as residue rather than swept in.

### ⚠️ Five records own no scope, and they are not refused

⛔ **Refusing would demand a rename, or a declaration added inside a record
Ruling 106 protects.** ⭐ They are held to the legacy-ceiling rule and nothing
else, and **every record written under the settled `<OFFICE>-<DATE>-round<N>`
filename derives one, so the uncovered set does not grow.** ⚠️ It is in the
module docstring as a Ruling 220 *held off by convention*, not only here.

### ⛔ Why this is a second document and not an edit to `W64.md`

⚠️ **My brief said to write `docs/tasks/handoffs/W64.md`.** ⛔ **That file
exists, it is the STOP Ruling 218 ratified, and its `Status:` line reads
*STOPPED — no module change, no document edit*.** ⭐ **Overwriting it destroys a
record; appending to it leaves a freshly-wrong headline at the top of a document
whose top is what a reader sees** — CLAUDE.md's own subject. ⚠️ **So: a second
document, whose stem begins with the declared ID as `agent-protocol.md`
requires, pointing back at the first.** ⛔ **No check in `tools/quality` enforces
one handoff per task, and no other task in the tree has two** — measured, all
104 task handoffs, zero task ID declared twice — **so this is a departure and it
is named rather than hidden.** `W64/6`.

## Surprises

⭐ **The largest one: 37 records were already declaring a scope, and the
declaration reader was already parsing it.** ⛔ **`declared_kind` returns the ids
for every kind, and `check_handoffs` then threw them away** — so the data gate
two needed had been sitting in the tree, unread, since the declaration landed.
The row's *"a declarable scope"* was closer to done than anyone priced.

⚠️ **Two offices' table-row figures disagreed, and NEITHER is wrong.** `W121`
reports **393** and `CTO-69` reading F reports **395**, both at `5b54936`. At my
ref, with my instrument, **395** marker-bearing lines contain a `|` anywhere and
**393** BEGIN a table row. ⛔ **The gap is a DEFINITION, not a ref and not the
corpus** — 2 lines carry a cell boundary without starting a row. `W64/10`.

⭐ **`W121`'s two-organ diagnosis inverts here.** That row could not be validated
through the floor because the gate did not admit its documents; this one adds
**748 finding lines** to a floor rule and the floor still prints `clean`,
because the corpus already obeys the rule that was never applied to it.

## Findings

### ⛔ `W64/6` `[structural]` — my brief directed me to overwrite a record Ruling 218 ratified

⛔ **The brief's hand-back clause reads *"WRITE `docs/tasks/handoffs/W64.md`
with `**Kind:** task handoff — W64` and the six sections"*.** ⚠️ **That file
already exists**, it is the previous taker's STOP, and the brief's own body
tells me in three places that the stop was right and that Ruling 106 protects
records. ⭐ **The brief also says the ROW wins and a contradiction is a finding
against the coordinator, so this is filed as one.** ⛔ Resolved by writing a
second document; the departure from one-handoff-per-task is in **Decisions** and
is the reviewer's to rule on.

### ⛔ `W64/7` `[structural]` — `docs/tasks/rows/W64.md` still carries the unit `W121/1` refuted

⛔ **The row argument still reads *"48 finding lines claiming none"* and quotes
Ruling 219's *"the 48 that claim no scope are the table-form records"*.** ⚠️
**`W121/1` measured that `48` as DOCUMENTS — `31 + 1 + 48 = 80`, the whole
population — and the CTO upheld it at full width in round 69.** ⭐ **The finding-
LINE figure at Ruling 219's own reproducing ref is `77`, not `48`.** ⛔ **I did
not edit it:** `docs/tasks/rows/` is the PO's live register surface and this is
the third document to inherit the same mislabel. Routed to the PO with the
correction already measured twice by two offices.

### ⛔ `W64/8` `[structural]` — the row's price for gate two, *216 of the 522*, is not the population gate two reaches

⛔ **The row's gate table prices gate two at *216 of the 522*.** ⚠️ **That `216`
is a count of `handoff-finding-id` FINDINGS produced by a dry run of the FULLY
widened gate at base `2d0cfe7`** — the row's own quoted block says so. ⭐ **What
gate two actually reaches, measured at `7a7a178` with the shipped derivation:
748 finding lines in 106 `ruling record` documents, of which 0 are findings.**
⛔ **The two numbers answer different questions** — one is *how red would the
full widening be*, the other is *how much does this rule now read* — and only
the second is an acceptance figure for this row. ⚠️ **`170` of the `216` are the
citations gate two RULES LEGITIMATE rather than fixes**, so the residue the row
implies is overstated by that much. Full derivation in **For dependents**.

### ⚠️ `W64/9` `[local]` — `CTO-69/2`'s denominator moved by one wave of corpus growth

⭐ **`CTO-69/2` re-prices gate two at `4 in 47 → 14 in 69` and orders `W64` to
inherit that and not `1 in 32 → 14 in 69`. I inherited the corrected one.** ⚠️
**Re-measured at `7a7a178` it is `14 in 70`**: 54 records file only inside their
own scope, 2 are mixed, 14 cite elsewhere, so 70 records claim a scope at all.
⛔ **The numerator did not move and the ratio is 20.0 % against 20.3 %** — the
conclusion is untouched and this is filed so the next taker compares like with
like rather than reading `69` as a property of the tree (Ruling 55).

### ⛔ `W64/10` `[local]` — a recorded negative: I predicted two offices disagreed, and they do not

⚠️ **I opened this row expecting to file `393` (`W121`) against `395` (my
brief, and `CTO-69` reading F) as an unreconciled disagreement at one ref.** ⛔
**Both reproduce at MY ref, under two definitions, and my prediction was
wrong:** marker-bearing lines containing a cell boundary anywhere = **395**;
marker-bearing lines that BEGIN a table row = **393**. ⭐ **The 2-line gap is
definitional.** ⚠️ **Kept rather than tidied** (Ruling 155): the pattern this
project keeps recording is an office's own instrument refuting its own
expectation, and this is mine for the wave.

### ⛔ `W64/11` `[structural]` — the citation-resolution rule: measured green, refused, and handed to gate three

⛔ **Requiring a cited scope to EXIST is the rule that would make
`cites_elsewhere` safe rather than merely measured.** ⭐ **It is green today: 170
of 170 citation lines resolve; 0 dangling.** ⚠️ **I refused to ship it because
its failure mode is an undischargeable red** — the offending line is inside a
record, and a record is annotated, never edited. ⛔ **Gate three's row owns
this**, together with the 220 marker-rule findings, because the same document
surgery answers both. The instrument is named in **For dependents** so the next
taker re-runs it rather than rebuilding it — which is exactly `W121/2`'s
complaint about Ruling 219, and I am not repeating it.

### ⚠️ `W64/12` `[local]` — `tools/quality/pointers.py` still carries the sentence `W121` falsified, and I did not fix it either

⛔ **`tools/quality/pointers.py` still contains the string *"a table cell does
not count" for free, because a marker in a cell has a…"*.** ⭐ **Corroborates
`W121/5` at a second ref**; nothing about it changed this wave. ⛔ **I left it
alone for `W121`'s reasons and one more of my own:** `docs/tasks/rows/W155.md`
tracks that module's R11 headroom, `W148` and `W35` declare it as their surface,
and my row touched a different module in the same package. Routed to whichever
of `W148`, `W35` or `W155` lands first.

### ⭐ `W64/13` `[local]` — a second recorded negative: `W167`'s false surface claim was ALREADY corrected

⚠️ **`W121/3` filed `docs/tasks/rows/W167.md`'s *"Shares a surface with no
queued row"* as false, and I expected to corroborate it against `W64`.** ⛔ **The
sentence is already gone**: that row now carries a `CORRECTED PO round 54` block
which QUOTES the old claim rather than deleting it, names `W121` explicitly, and
routes the structural cause to `W160` under Ruling 331. ⭐ **So there is nothing
to file and the register moved faster than the finding** — recorded because a
dependent reading it in `W121`'s handoff would otherwise re-derive it.

### ⛔ `W64/14` `[structural]` — Ruling 296's obvious implementation REDDENS THE FLOOR WITH 329 FINDINGS, and it writes into a config every worktree shares

⛔ **I did it, I caught it with the floor, and I undid it — and the trap is
general enough that the next office will do the same.** ⚠️ **`git config
user.name dev1` in a LINKED worktree does not write a worktree-local value: it
writes `[user]` into the common `.git/config`**, which the main checkout and
every other office's worktree read. ⭐ **Then
`tools/quality/personal_data/identity.py` reads `git config --get user.name` as
*this machine's git author* and flags every tracked occurrence of the string** —
and this project's documents are full of `dev1`, `dev2`, `dev3`.

```text
before:  quality floor: clean
after `git config user.name dev1`:  quality floor: 329 findings
  — including [personal-data-identifier] on documents I have never opened
after removing the [user] section:  quality floor: clean
```

⛔ **So the placeholder Ruling 296 mandates becomes, to the floor's own
instrument, the personal datum R7 forbids.** ⭐ **The safe form, and what every
commit on this branch used:** `git -c user.name=dev1 -c
user.email=dev1@example.invalid commit …`, which sets the author of record and
leaves no config for the next reader — or `GIT_AUTHOR_*` in the environment.
⚠️ **Two defects, and only the first is mine:** I wrote into a config shared with
offices measuring concurrently tonight (it stood for roughly two minutes and was
removed; the section did not exist before, so the removal restored the prior
state exactly), and **Ruling 296 does not say which mechanism it means.** ⛔ The
second is routed to the CTO as a one-clause amendment; the first is a defect of
mine, recorded rather than tidied.

⭐ **DISPOSED, round 70: this became Ruling 345, from two offices' independent
findings in one night.** ⛔ **The ruling's own words are that the instrument did
NOT malfunction** — it fired correctly, in about two minutes, on a premise
nobody meant to establish — ⭐ which is the better reading and is not the one I
filed. ⚠️ **And `CTO-70/13` corrects the null check I would have reached for
next:** bare `git config --local --get-regexp '^user\.'` **prints the values** at
rc 0 when a slot is set, so it is safe only when it passes. ⛔ **The redirected
form is the one that proves absence without emitting what it is checking for**,
and every absence check taken on this branch after round 70 used it.

### ⛔ `W64/15` `[structural]` — `CTO-70/9`'s illustration re-measured its AFTER column and inherited its BEFORE column, which is the class it filed

⭐ **`CTO-70/9` says in its own words that its figures are an ILLUSTRATION and
explicitly not a required means, and that if the office finds the population it
did not, the finding is its.** ⛔ **I found it, so it is filed here.**

⚠️ **The illustration quotes three pairs at ref `5b31436`. Every AFTER column
reproduces EXACTLY at that ref. No BEFORE column does — and each is short by
exactly this document's own contribution at that ref, because each is the figure
measured at `7a7a178`, where this handoff does not exist.**

```text
one instrument, one process, both columns, at each ref (mine, HOST):

                                   7a7a178            5b31436
  documents reaching a rule       105 ->  211      106 ->  212
  finding lines HANDED            566 -> 1366      575 -> 1375
  numbered claims JUDGED          552 -> 1300      561 -> 1309

  CTO-70/9's illustration, all three declared at 5b31436:
  documents                       105 ->  212   <- before is 7a7a178's
  finding lines HANDED            566 -> 1375   <- before is 7a7a178's
  numbered claims JUDGED          552 -> 1309   <- before is 7a7a178's

  this document contributes 1 document and 9 finding lines at 5b31436,
  and 9 is exactly the gap in both line-unit BEFORE columns
```

⛔ **So the row *documents held to more than say what you are: 105 → 211* was
never wrong** — it is my `7a7a178` reading, and `212` is the same quantity at
`5b31436`. ⚠️ **What was wrong is that the table named no ref**, so a reviewer
measuring at the merge ref got a different right answer. ⭐ **`560 → 1308` is a
different matter and is wholly mine: `552 + 8 = 560` is this document at the
moment it carried 8 findings, and `1308` was `560 + 748` rather than a reading.**
⛔ **`CTO-70/9` is upheld in full on that second row and the whole table is
replaced rather than patched.**

⚠️ **The point that generalises, and it is the reviewer's own:** *a population
that contains the document measuring it has no single before column* — the ref
must be named, and both offices reached for the one that suited the sentence.

### ⚠️ `W64/16` `[local]` — round 70's two per-subject sections point at the WRONG finding id, each off by one

⛔ **In the `W64` section the closing sentence reads *"What does NOT reproduce is
`CTO-70/10` below"*, and in the `W155` section it reads *"What does not
reproduce is `CTO-70/11` below"*** — in
`docs/tasks/handoffs/CTO-2026-09-12-round70.md`, at the record's live tip, and I
re-read it there rather than at the sha I was first handed. ⚠️ **`W64`'s finding
is `CTO-70/9` and `W155`'s is `CTO-70/10`; `CTO-70/11` is a recorded negative in
`W155`'s FAVOUR that asks for nothing.** ⛔ **So each subject's own section sends
it at the next subject's charge, and `W155`'s sends it at a finding it does not
have to discharge.**

⭐ **Recoverable, which is why it carries the local marker and not the
structural one** (Ruling 65 — the marker is named, not spelled): **the record's own
*THE REQUIRED CHANGES, by id* table routes both correctly**, and that table is
what I acted on. ⛔ **Not edited** — a record is annotated, never edited
(Ruling 106) — and filed here so the two documents agree.

### ⛔ `W64/17` `[structural]` — the WITHDRAWN pair `560 → 1308` reproduces EXACTLY at the release tip, and that must not be read as a defence

⛔ **Measured, cold cache, at `1a55e12` — the release tip after `W170` and the
register's round 55 landed, a ref that did not exist when I wrote the figure:**
`numbered claims JUDGED by check_finding_ids` is **`560 → 1308`**, digit for
digit the pair `CTO-70/9` charged and I have withdrawn.

```text
REF 1a55e12   228 documents, 107 ruling records, this branch NOT in it
  documents reaching a rule beyond the declaration   106 -> 213   +107
  finding lines HANDED                               574 -> 1374  +800
  numbered claims JUDGED                             560 -> 1308  +748
  findings returned by check_handoffs                  0 ->    0    +0
```

⚠️ **So a reviewer who re-measures at the release tip will reproduce my
withdrawn pair and may conclude `CTO-70/9` was wrong. It was not.** ⭐ **A figure
is a reading of a ref, never a property of the tree** (Ruling 55), and mine was
taken at NO ref: `748` came from `7a7a178`, `560` from a working tree holding
this handoff at 8 findings, and `1308` from addition. ⛔ **Agreeing by accident
with a ref one never measured is not measurement**, and the agreement is the
strongest possible argument for the property `CTO-70/9` demands rather than
against it.

⭐ **And the original table's OTHER row is exactly right at a DIFFERENT ref:**
`105 → 211` is `7a7a178` to the digit. ⚠️ **Two rows, each correct, at two refs,
in one unnamed-ref table** — that is `CTO-70/9`'s charge stated as cleanly as it
can be stated, and it is why the replacement prints the ref on every block.

### ⭐ `W64/18` `[local]` — a recorded negative: the stale byte-code hazard eliminated three ways, not assumed away

⚠️ **The coordinator routed `W155/12` to me because this row plants and mutates:
CPython invalidates cached byte-code on `(mtime, size)`, so a same-length
in-place edit inside one mtime tick re-runs the PREVIOUS source and fails
silently in the direction of agreement.** ⛔ **I did not reason it away; I
eliminated it.**

1. ⭐ **It cannot apply to the coupling table at all.** The *gate OFF* column is
   built by REBINDING `handoffs.RULING_RECORD` in the running process — **no
   file is edited, so no source's `(mtime, size)` is consulted and no cached
   module is reloaded.** ⛔ That is a property of the instrument, not an
   accident, and it is the reason it was written that way.
2. ⭐ **Re-run cold anyway:** every `__pycache__` removed and
   `PYTHONDONTWRITEBYTECODE=1` set, at both refs and at the release tip. **Every
   figure identical.**
3. ⭐ **The R12 counterfactual is a file edit and therefore the exposed one** —
   but it REMOVES four lines, so the size changes and the invalidation cannot
   miss it. ⚠️ **Re-run cold in the pinned container regardless: `5 failed, 12
   passed`, `EXIT=1`**, and the restore verified by `md5sum` against
   `git show HEAD:` rather than by a grep (`CTO-53/6`'s lesson).

⛔ **Filed as a negative because a hazard that was checked and absent is worth
exactly as much on the record as one that was found**, and because the reviewer
nearly read three silent plants as a pass in this same round (`CTO-70/4`).

## For dependents

### ⛔ The population, re-derived at my own ref and NOT inherited

⭐ **Instrument:** `tools.quality.handoffs.record_scopes` and
`tools.quality.handoffs.contract.marker_lines` — **the SHIPPED derivation**, so
this reading is reproducible from the tree rather than from prose (`W121/2` is
discharged by that, and the driver that prints the table below is a scratchpad
script that imports both and adds no logic of its own).
⭐ **Ref:** `7a7a178`, the branch base — **the corpus this branch INHERITED, in
which this document does not yet exist.** ⛔ **At the merge ref the directory
holds 227 rather than 226, because this handoff is itself in the population the
rule reads**, and every figure below that counts a `ruling record` is unmoved by
that while every figure that counts a `task handoff` is not. ⚠️ **The
`ruling record` corpus is byte-identical between the two refs: this branch adds
no record and edits none.** ⭐ The coupling section prints both refs.
⭐ **Directory:** `docs/tasks/handoffs`, **226** documents at this ref.

```text
UNIT = documents          directory = docs/tasks/handoffs, 226 total
  task handoff   104     ruling record  106     session log  11
  survey           3     office handoff   1     index         1

  POPULATION this row admits (`ruling record`)          : 106
  measured by every inherited reading, NOT admitted     :   3  (survey)

UNIT = documents          population = 106 ruling records
  owns a scope (derived from the filename, or declared) : 101
  owns NO scope                                         :   5
  ------------------------------------------------------------
  all findings inside its own scope                     :  54
  mixed: own scope and unscoped numbers                 :   2
  CITES a scope it does not own                         :  14
  only unscoped numbers                                 :   3
  files no numbered finding at all                      :  33
                                                          ---
                                                          106

UNIT = finding lines      population = 106 ruling records
  claiming the record's OWN scope                       : 550
  claiming another scope — a CITATION, permitted        : 170
  claiming no scope (all within the closed 20–62 range) :  28
                                                          ---
  TOTAL newly read by `handoff-finding-id`              : 748   (was 0)
```

⛔ **`0` findings on all 748.** ⭐ The corpus already obeyed the rule that had
never been applied to it, which is why this row could ship green without one
record being touched.

### ⛔ POPULATION COUPLING — RE-DERIVED at the real call site (`CTO-70/9`)

⛔ **`CTO-70/9` is UPHELD and the table it charges is REPLACED, not patched.**
⭐ **The reviewer's arithmetic gave the defect away exactly** — `1308 − 560 =
748` — and it was right: **the pair was derived, not measured.** ⚠️ **The whole
cause, which I can now name to the line:** `748` was measured over the corpus at
`7a7a178`, `560` was measured minutes later over the working tree **after this
handoff had been written into it carrying 8 findings**, and `1308` was then
added rather than read. ⛔ **552 + 8 = 560.** ⭐ **So the two rows of that table
were in two different populations and the table named no ref at all.**

⚠️ **`W64` is file-disjoint from `W155` (`tools/quality/size.py`) and `W170`
(`tools/quality/board/unclaimed.py`) and is NOT population-disjoint from them,
because every office writes a handoff and the floor reads it.**

⛔ **THE INSTRUMENT, and it is one instrument reading both columns in one
process at one ref.** ⭐ It wraps the SHIPPED `check_handoffs` at its own call
sites — `check_finding_ids`, `check_sections`, `check_markers`, `check_record` —
and counts what they are actually handed. ⛔ **The *gate OFF* column is the same
shipped code with `handoffs.RULING_RECORD` rebound to a string no document
declares**, so the gate is disabled and **nothing else differs**: not the
reader, not the corpus, not the process. ⚠️ It is a scratchpad driver of about
50 lines that adds no logic of its own; the derivation it calls is shipped.

⛔ **THREE UNITS APPEAR BELOW AND THEY ARE THREE DIFFERENT UNITS**, which is the
half the replaced table did not say. ⭐ *Documents* is a count of files;
*lines HANDED* is every finding line `check_markers` and `check_record` pass
down; *claims JUDGED* is the subset of those on which `_FINDING_NUMBER` matched
and a verdict was therefore reached. **A line handed and not judged carries no
number and collides with nothing.**

⛔ **AND THE POPULATION CONTAINS THIS DOCUMENT**, which is why two refs are
printed rather than one. ⭐ **`7a7a178` is the corpus this branch INHERITED —
226 documents, this handoff not yet written.** ⭐ **The merge ref is the corpus
that MERGES — 227 documents, this handoff among them, contributing its own
findings to the columns that count findings.** ⚠️ **Neither is the *true* one
and quoting either without its ref is the defect `CTO-70/9` filed.**

```text
INSTRUMENT   the shipped check_handoffs, wrapped at its own call sites;
             the OFF column is the same code with the ruling-record gate
             disabled by rebinding handoffs.RULING_RECORD

REF 7a7a178  — the corpus INHERITED, 226 documents, this handoff absent
UNIT                                            gate OFF   gate ON    delta
documents reaching a rule beyond the declaration     105       211     +106
finding lines HANDED to check_finding_ids            566      1366     +800
numbered claims JUDGED by check_finding_ids          552      1300     +748
findings returned by check_handoffs                    0         0       +0

REF the branch AT ITS TIP (Ruling 347) — the corpus that MERGES:
             227 documents, this handoff among them, carrying 13 findings
UNIT                                            gate OFF   gate ON    delta
documents reaching a rule beyond the declaration     106       212     +106
finding lines HANDED to check_finding_ids            579      1379     +800
numbered claims JUDGED by check_finding_ids          565      1313     +748
findings returned by check_handoffs                     0         0      +0

⭐ the two refs differ by exactly this document's own contribution, and that
   is the arithmetic that shows the population is self-inclusive rather than
   the arithmetic that shows a figure was derived

⚠️ a THIRD ref, the release tip 1a55e12, is in W64/17 — where the pair this
   section withdraws reproduces exactly, by coincidence, and must not be read
   as a refutation of CTO-70/9
```

⛔ **THE INSTRUMENT ITSELF, so the table can be re-taken by whoever doubts it
without asking me for a scratchpad** (Ruling 221, and `W121/2` at a second
site). ⭐ Run it from a checkout root; pass a root to read another ref's corpus.

```text
import sys; sys.path.insert(0, ".")
from pathlib import Path
import tools.quality.handoffs as H
from tools.quality.handoffs import contract as C, records as R
from tools.quality.handoffs.contract import _FINDING_NUMBER, _MARKUP, _claim_free_end

IDS, SEC, MRK, REC = C.check_finding_ids, C.check_sections, C.check_markers, H.check_record

def run(gate, root=Path(".")):
    docs, handed, judged = set(), [], []
    def ids(rel, lines, i, **kw):
        docs.add(rel); handed.extend(lines)
        judged.extend(l for _n, l in lines
                      if _FINDING_NUMBER.match(l[_claim_free_end(l, _MARKUP):]))
        return IDS(rel, lines, i, **kw)
    def wrap(fn):
        return lambda rel, *a, **k: (docs.add(rel), fn(rel, *a, **k))[1]
    C.check_finding_ids = R.check_finding_ids = ids
    C.check_sections = H.check_sections = wrap(SEC)
    C.check_markers = H.check_markers = wrap(MRK)
    H.check_record = wrap(REC)
    saved, H.RULING_RECORD = H.RULING_RECORD, H.RULING_RECORD if gate else "\x00"
    try:
        found = H.check_handoffs(root)
    finally:
        H.RULING_RECORD = saved
        C.check_finding_ids = R.check_finding_ids = IDS
        C.check_sections = H.check_sections = SEC
        C.check_markers = H.check_markers = MRK
        H.check_record = REC
    return len(docs), len(handed), len(judged), len(found)

print("gate OFF", run(False), "\ngate ON ", run(True))
```

⚠️ **`"\x00"` is a kind no document declares, so the OFF column disables the
gate and only the gate.** ⛔ **Restoring in a `finally` is not decoration** — a
half-restored module would make the second column a reading of a third thing,
which is the failure this table is being corrected for.

| population | direction and size, ref-independent |
|---|---|
| documents `check_handoffs` reads at all | ⭐ unchanged |
| documents reaching a rule beyond the declaration | ⛔ **+106** |
| numbered claims judged by `handoff-finding-id` | ⛔ **+748** |
| finding lines handed to it | ⛔ **+800** |
| rules a `ruling record` can fail | ⛔ **1 → 3**, and the reviewer fired each by its own plant |
| directories read | ⭐ unchanged |

⭐ **The DELTAS are the ref-independent half and they reproduce at both refs**,
which is why `CTO-70/9` says the direction and the deltas were always right.

⛔ **Every document any office writes as a `ruling record` this wave is now in
the floor's population**, including the CTO's own round record and the PO's.
⭐ **What it costs them is one line: a filename of the settled shape, or
`**Kind:** ruling record — <OFFICE> round <N>`.** ⚠️ **A record that declares a
scope disagreeing with its filename is now RED, and that is a new way for a
merge to go red that did not exist at `7a7a178`.** ⭐ **`po-round55` is the first
record to face the rule and the reviewer verified it passes.**

⭐ **No new directory is read and no new file type**, so check 4's file-growth
sub-step still sees everything it saw before.

### ⛔ The residue gate three would still owe, measured

⭐ **Instrument:** `check_markers` and `check_sections` from the shipped
`contract`, applied to the 106 records with `record_scopes` as their ids — i.e.
the fully widened gate, dry-run, exactly as `W64.md`'s stop did it. **Ref
`7a7a178`.**

```text
if the kind gate were widened FULLY to `ruling record`:
  handoff-section      427 findings   ⚠️ NOT gate three — a record is not a
                                         handoff and never owed the six
  handoff-marker       178 findings in 51 documents  ⛔ gate three
  handoff-findings      42 findings in 42 documents  ⛔ gate three
  handoff-finding-id   170 findings                  ⭐ DISCHARGED by this row:
                                         they are citations, and gate two rules
                                         them legitimate rather than fixing them
  -----------------------------------------------------------------
  gate three's residue proper          220 findings in 73 documents
```

⛔ **So the row's *216 of the 522* is retired by two separate corrections:** the
unit (`W64/8`) and the fact that 170 of the 216 are now a permission rather than
a debt. ⭐ **What is left for exit `0` is 220 marker findings in 73 documents,
plus a decision that a record does not owe the six sections at all** — and the
first of those needs a rule that separates a record's Findings section from its
prose, which is the gate the row declined to mint.

⚠️ **Also outstanding and NOT in that 220:** the 3 surveys, the 5 records that
own no scope, and `W64/11`'s citation-resolution rule.

### ⚠️ `W167`, you share `tools/quality/handoffs/` with this branch

⛔ **`W167` is queued on this package and was not dispatched, so nothing here is
a patch to it.** ⭐ The diff is: one NEW module `records.py`; in `contract.py`
one keyword on `check_finding_ids`, one local for the message and one docstring
paragraph; in `__init__.py` one import, two `__all__` entries, the
`ruling record` registry sentence, four lines in `check_handoffs` and one
docstring section. ⚠️ **`check_markers`, `marker_lines`, `LEAD_TOKENS` and
`_FINDING_NUMBER` are untouched**, so `W121`'s change and this one do not
overlap on a single line.

## Readings

⛔ **Every reading carries its ref, its ROLE and its ENVIRONMENT** (Ruling 326).
⭐ **ROLE:** the `dev1` linked worktree at `studyforge-wt/dev1`, branch
`fix/W64-kind-gate-scope`. ⚠️ **ENVIRONMENT:** the pinned container, invoked as
`./docker/dev/check` from that checkout — except the one line explicitly marked
HOST below. ⛔ **No run was killed**; each printed a complete summary line and
its own exit status, and **no filter stood between an instrument and its capture
file** — each was redirected whole, then read.

⭐ **The expectation was written before each run: floor clean, suite green, and
the counterfactual RED on exactly the tests that only the new gate can pass.**

```text
ref                 fix/W64-kind-gate-scope AT ITS TIP (Ruling 347 — a branch
                    tip is named as a tip, and its sha is in the coordinator
                    hand-back where it cannot go stale in a frozen record). ⛔ The
                    round-70 discharge changes THIS DOCUMENT ONLY; the code ref
                    is unmoved at 6f156a3 and the readings below are re-runs at
                    the tip, not carried forward from 5b31436.
ROLE                studyforge-wt/dev1, branch fix/W64-kind-gate-scope
ENVIRONMENT         the pinned container, ./docker/dev/check, from this checkout

quality floor       ./docker/dev/check python3 -m tools.quality
                    "quality floor: clean"                        EXIT=0
                    lint: ruff 0.16.6 — `ruff check .` All checks passed;
                    `ruff format --check .` clean, 929 files

suite               ./docker/dev/check python3 -m pytest -ra
                    5688 passed, 18 skipped                       EXIT=0
                    (5671 + 18 at 5b54936 per W121; +17 is test_records.py)

coupling table      the instrument printed in For dependents, run at that tip
                    the shipped check_handoffs wrapped at its own call sites
                    227 documents; the six figures printed above  EXIT=0
                    ENVIRONMENT: HOST — standard library only, no container
                    dependency; reproduced in the pinned container as well
                    ⛔ RE-RUN COLD (W155/12's hazard, W64/18): every
                    __pycache__ removed and PYTHONDONTWRITEBYTECODE=1, at all
                    THREE refs. Every figure identical.

R12 cold            the same counterfactual, cache cleared, byte-code writing
                    disabled inside the container, -p no:cacheprovider:
                    5 failed, 12 passed in 0.07s                  EXIT=1
                    restore verified by md5sum against git show HEAD:, not by
                    a grep (CTO-53/6)

R12, second way     the four-line gate in check_handoffs removed, everything
                    else in place:
                    ./docker/dev/check python3 -m pytest \
                        tools/tests/quality/handoffs/test_records.py -ra
                    5 failed, 12 passed in 0.07s                  EXIT=1
                    git status --short empty after the restore

ENVIRONMENT: HOST   python3 -m tools.workspace verify
                    1 component disagrees with workspace.json     EXIT=2*
                    ⚠️ ISO-8583-jPOS-tutorial HEAD 76e689c6a535, pin
                    a94151747cb0. INHERITED and pre-existing: this branch
                    touches tools/ and one document and no component, and no
                    pin file is in the diff. *the process exit was 1; the
                    figure `2` in circulation is the CONTAINER's, and this is
                    the HOST reading (Ruling 326).
```

⛔ **R12 in BOTH directions.** The second direction is the one that counts: with
the four-line gate in `check_handoffs` removed and everything else left in place
— `records.py`, the docstrings, the whole test module — **5 of the 17 tests go
red**, and they are the five that assert something fires. ⚠️ The other 12 pass
under both gates and that is correct: they are the derivation's unit tests and
the pins on what gate two must NOT do, and a gate that never widened satisfies
those too. ⭐ The gate was restored before every reading above was taken.
