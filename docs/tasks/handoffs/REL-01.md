# REL-01 — handoff

**Kind:** task handoff — REL-01

## Status

**done.** Task [`REL-01`](../E15-release-ready.md), branch `docs/REL-01-the-decisions-file`, cut at
`7f68b790` with the release tip `0e590b06` merged in. Office `dev4`, worktree `studyforge-wt/dev4`.
Every commit and the merge are `dev4 <dev4@example.invalid>`, passed with `git -c`. Nothing was
moved, deleted or archived; no remote was added and nothing was pushed.

## What landed

- [`docs/decisions.md`](../../decisions.md) — the decisions still shaping the product, in sections
  by area, each entry carrying **Decision**, **Why**, **Serves** (a spec rule, or `No spec rule:`
  and the reason) and **Aliases** (the process ids it replaces). A decision the spec already states
  is a pointer entry naming the spec section or rule, never a copy. The header carries the
  population command and why each of its choices is there.
- `tests/test_decisions.py` — runs the header's command in a throwaway repository: a clean tree
  prints nothing, a planted id in a docstring is printed, an id outside the four roots is not,
  every root is read, and every alias is a spelling the command prints back unchanged. It also
  holds each entry to its four parts in order, a rule or a stated reason for none, one decision
  per alias, unique headings, and the forbidden-strings grep. ⚠️ **It deliberately does NOT
  assert coverage of the live tree** — see *Decisions*.

## How the population was taken, and the reading

Taken from the worktree root at the tip this handoff is committed on: the header's fenced
command extracted from [`docs/decisions.md`](../../decisions.md) and run with `bash`, its output compared with
`LC_ALL=C comm` against the backticked ids on the Aliases lines together with the table at the
end of this handoff.

Reading: every id the command printed is either an alias in the file or in the table below, and
no id is both. The split between the two is a reading of this ref and is not carried forward as
a figure; re-take it.

⭐ **The plant, proved on a real scratch export.** `git archive` of the tip into scratch,
`git init` and `git add -A` there, the command run (its output identical to the worktree's),
then `W9876` added to the first line of `src/studyforge/describe.py`'s docstring and the command
run again: the one new line printed was `W9876`. The export was removed afterwards. The same
plant is held permanently, on a synthetic tree, by `test_a_planted_id_is_printed`.

## Gates

Each run bare from `studyforge-wt/dev4`, output to a scratch file, exit code read on the next line.

| gate | environment | reading |
|---|---|---|
| `./docker/dev/check ruff check .` | pinned image | GREEN, exit 0 |
| `./docker/dev/check ruff format --check .` | pinned image | GREEN, exit 0 |
| `python3 -m tools.quality` | host | GREEN, exit 0 |
| `python3 -m pytest tests/test_decisions.py tests/test_repository.py -q` | host | GREEN, exit 0 |

⚠️ The first `ruff format --check .` was RED, exit 1, on the new test's line wrapping; fixed with
`ruff format` on that one file.

## Decisions

- ⭐ **The id grammar is the product's prose, not the rulings index's.** It reads rows and
  findings, task ids and their findings (the eleven epic prefixes plus `INT`, `ISO`, `PO`, `CTO`),
  `ISO-M<n>`, rounds with or without an office, and `Ruling`/`Rulings` with a list of members.
  ⛔ `ISO-8583` and the `CTO-2026-…` record names are excluded by the three-digit bound. Range
  (`Rulings 264–278`) and `+` forms were checked absent from the four roots at this ref and are
  not read; if one lands, widen the grammar.
- ⛔ **`LC_ALL=C sort -u` is load-bearing.** Under `en_US.UTF-8` the `/` is ignored by the
  collation, so `W39/5` and `W395` compare equal and `sort -u` silently dropped one of them —
  measured: five ids vanished from the first draft's population. The header says so.
- ⭐ **Coverage is not a test.** The explains-nothing list lives in this handoff (it is `REL-09`'s
  input and leaves the main line in `REL-10`), and a test pinned to it would go red on every other
  branch that adds a citation while `M10` is running. The test holds the mechanism (the plant,
  the alias spelling) and the shape; coverage is this handoff's reading.
- ⭐ **Spec-stated decisions are pointer entries in the same shape**, one per governing rule or
  spec section, so one test holds every entry and a reader finds an id the same way.
- ⭐ **Test-suite decisions are carried** (the visual harness, the pinned dev image's browser,
  the chrome census, checking authoring pages against the code): the product's tests stay on the
  main line, and these constrain them. Test-method rulings that constrain only how tests are
  written (sweeps, plants, gate coverage) are on the list below as process.
- ⭐ **The classification was drafted in six parallel passes by area and merged by hand**:
  duplicate decisions across areas were folded into one entry (refusal wording, the personal-data
  refusal, re-onboarding, lazy verb loading, narration pruning, the control a practice cannot
  honour, the two serve forms, positive legal combinations, permitted character classes, the
  narration record as a plan input).

## Surprises

- ⚠️ **`Ruling 1`–`Ruling 4` in spec §8.1 are that section's own numbered rulings, not the
  rulings index's `1`–`4`.** Two series share one spelling; they are pointer aliases to §8.1 here.
- ⚠️ **The spec itself cites process ids heavily**, including ids that explain nothing (see
  *Findings*); `REL-09` owns only `src/` and `tests/`.

## Findings

| id | marker | where | what |
|---|---|---|---|
| `REL-01/1` | `[structural]` | [the spec](../../specs/2026-09-08-studyforge-v1-design.md) | ⛔ **Ids on the list below that the spec cites stay after `REL-09`**, because `REL-09` owns only `src/` and `tests/`: `CTO round 69`, `EX-00`, `EX-02`, `EX-04`, `FND-05`, `FND-08`, `JS-05`, `NS-01/1`, `NS-02`, `NS-02/3`, `NS-03`, `NS-03/2`, `NS-04`, `OPS-03`, `PO round 67`, `PO round 72`, `PO-38/2`, `QA-05`, `Ruling 106`, `Ruling 150`, `Ruling 181`, `Ruling 28`, `Ruling 335`, `Ruling 48`, `SF-09`, `SF-10`, `SF-21/1`, `SK-06/5`, `SK-07`, `TC-00/3`, `TC-01`, `round 113`, `round 53`. The spec's prose is `REL-08`'s surface; it needs to own this residue or the command keeps printing it after the archive leaves |
| `REL-01/2` | `[local]` | `tests/studyforge/skills/delivery/test_findings_log.py` | The test asserts the literal *`QA-04` sort* in `findings_log.py`'s text and in [`docs/integration-catalogue.md`](../../integration-catalogue.md). Rewriting that prose (`REL-09`) turns the test red unless the test changes in the same diff — and the delivery tests are `REL-06`'s |
| `REL-01/3` | `[local]` | spec §8.1 | `Ruling 1`–`Ruling 4` there collide in spelling with the rulings index's first four rulings (*Surprises*); a rewrite should give them a section-local name |

## For dependents

- ⭐ **`REL-09`:** your population is the header's command with the roots cut to `src tests`.
  Every id it prints that is on an Aliases line may be rewritten to cite the entry (its heading is
  its anchor) or to carry the reason; every id in the table below carries no product decision, so
  the prose citing it is rewritten to carry its own reason, or the citation is dropped. ⛔ Re-take
  the population at your ref: ids minted after this ref are in neither place, and each must be
  classified (an alias added to the decisions file, in the same act) before it is rewritten.
- ⭐ **`REL-10`:** [`docs/decisions.md`](../../decisions.md) cites no handoff, row or board anchor, and links only to
  the spec. From the cut on, a handoff that decides something still shaping the product adds or
  extends an entry here in the same act — the test holds its shape and the alias spelling.
- ⭐ **`REL-08`:** see `REL-01/1`; and a rubric clause moved into the spec may make a pointer entry
  here the right home for aliases that are now on the list.

## The ids that explain nothing without the archive

⭐ **`REL-09`'s input.** Each is printed by the header's command at this ref and is on no
Aliases line. The reason is the classifying pass's own, one line each.

| id | why it explains nothing without the archive |
|---|---|
| `AX-02/1` | a residual timing gap noted in a test docstring |
| `AX-10` | task label naming who built a module, no decision |
| `CTO-20` | finding about how the gate-coverage test states its set |
| `CTO-21/1` | dev-image test history about a stale bytecode read |
| `CTO-36/6` | finding about gate-coverage tooling and pre-commit checks, process |
| `CTO-45/6` | review observation behind an import-sweep test; process only |
| `CTO-55/5` | measurement reference for a snapshot figure; provenance only |
| `CTO-64/1` | finding about the formatter's subject in quality tooling |
| `CTO round 27` | provenance of when a ruling was made |
| `CTO round 41` | meeting reference cited by a frozen record, provenance only |
| `CTO round 69` | correction of how the spec described another component's file |
| `EX-00` | task label for a cost measurement, no decision carried |
| `EX-02` | task label naming who builds the content-addressed cache |
| `EX-04` | task label naming the builder that updates practice counts |
| `FND-01` | package skeleton provenance, names who filled which package |
| `FND-02` | task label naming who built an earlier mechanism |
| `FND-05` | task label naming where pin behaviour gets documented |
| `FND-06` | task label naming who consolidated test helpers |
| `FND-07` | task label for registering quality checks, process tooling |
| `FND-08` | task label naming whose seam an owed check sits on |
| `FND-09` | test-fixture consolidation task that moved checks between test modules |
| `INT-14/4` | finding about a sentence naming a closed task |
| `INT-19/1` | example id used as fixture data in a delivery test |
| `INT-19/2` | example id used as fixture data in a delivery test |
| `INT-19/3` | example id used as fixture data in a delivery test |
| `INT-19/4` | example id used as fixture data in a delivery test |
| `INT-19/5` | example id used as fixture data in a delivery test |
| `INT-19/9` | example id used as fixture data in a delivery test |
| `ISO-21/1` | a measurement taken on the first corpus, no decision |
| `ISO-M10` | measurement provenance for a re-survey defect already explained |
| `JS-01` | example id in a usage docstring of the capability index |
| `JS-05` | task label naming the adapter task that generates container.json |
| `NS-01/1` | finding about splitting the batch API across two tasks |
| `NS-02` | task label for the narration batch route; decision carried elsewhere |
| `NS-02/3` | finding reporting a stale spec sentence, pure provenance |
| `NS-03` | task label for the profiles half of consuming.json |
| `NS-03/2` | finding reporting a stale spec sentence, pure provenance |
| `NS-04` | task label for the voices half of consuming.json |
| `NS-05/2` | measurement provenance for a placement mistake |
| `OPS-03` | task label naming who fixes the loopback binding |
| `OPS-04` | task label naming a progress writer and the pipeline owner |
| `OPS-07` | task label naming who will build a future verb |
| `PO-38/2` | document-maintenance finding about a typed count, process |
| `PO-105/4` | register misreading its own probe; process record only |
| `PO round 25` | round when a test fixture was re-routed, provenance |
| `PO round 67` | round when a register row was transcribed, provenance |
| `PO round 72` | round when a register row was transcribed, provenance |
| `PO round 133` | pinned ref label for a previous-reader test control |
| `QA-03/3` | open harness finding about a second engine; provenance |
| `QA-03/8` | measurement that found the missing media copy, provenance only |
| `QA-05` | task label for the Java corpus re-validation |
| `Ruling 9` | merge-conflict procedure for the contract tuple, process |
| `Ruling 11` | test-methodology ruling: watch a check fail, not product |
| `Ruling 27` | test-design ruling keeping two gate assertions separate |
| `Ruling 28` | reversed by a later ruling; nothing of it remains |
| `Ruling 31` | quality-tooling boundary: tools must not import the framework |
| `Ruling 42` | review ruling on test survivors, test methodology only |
| `Ruling 46` | test-methodology ruling on which fixtures a sweep reads |
| `Ruling 48` | test-methodology ruling that sweeps state their denominator |
| `Ruling 54` | workspace pin tooling ruling, process not product |
| `Ruling 55` | test-tooling ruling on migrating the gate-coverage tell |
| `Ruling 56` | docstring discipline to name unasserted neighbours; process only |
| `Ruling 57` | test-tooling ruling on how gate coverage recognises readers |
| `Ruling 60` | test-design ruling on oracle independence of fixture checks |
| `Ruling 67` | test-tooling ruling bounding the gate-coverage scan root |
| `Ruling 70` | negative controls must be exercised; test-methodology process |
| `Ruling 72` | reporting-process ruling that counts are decompositions |
| `Ruling 74` | code-style convention for except-clause spelling, not product behaviour |
| `Ruling 76` | process ruling on a rubric counter-example block |
| `Ruling 77` | quality-tooling ruling on scratch-file findings never failing |
| `Ruling 78` | quality-tooling ruling on scratch-file findings never failing |
| `Ruling 80` | quality-tooling ruling that checks read tracked files only |
| `Ruling 106` | process rule that frozen records are annotated, not edited |
| `Ruling 123` | test-methodology ruling on planting instruments; process only |
| `Ruling 124` | test-methodology ruling on sweeps stating their population |
| `Ruling 126` | test-methodology ruling on stating the measuring command |
| `Ruling 132` | test-methodology ruling on inhabitation assertions; process only |
| `Ruling 139` | where agent sweep artifacts live; worktree process rule |
| `Ruling 140` | test-planting methodology for quality tooling, not product behaviour |
| `Ruling 143` | process ruling about inverting a quality-tooling test |
| `Ruling 146` | test sweep discipline about asserting row counts, process only |
| `Ruling 150` | process ruling about task counts in documents |
| `Ruling 151` | process ruling on how task Acceptance clauses are worded |
| `Ruling 153` | test-tooling ruling that gate coverage reads the git index |
| `Ruling 155` | process ruling on retiring stale Acceptance declarations |
| `Ruling 157` | process ruling on converting a documentation check |
| `Ruling 159` | dated ruling about worktrees and siblings, since corrected |
| `Ruling 166` | process ruling restating a task as delivered |
| `Ruling 178` | import-sweep methodology ruling for tests; process only |
| `Ruling 179` | personal-data gate false positive handling; quality tooling process |
| `Ruling 181` | process ruling about typed measurements in governing documents |
| `Ruling 183` | quality-tooling ruling on demoting a working-tree reading |
| `Ruling 185` | how a gate exemption is implemented; quality tooling process |
| `Ruling 191` | process ruling on test controls and empty populations |
| `Ruling 208` | process ruling on naming test instruments by reach |
| `Ruling 209` | process ruling on pinned expiries in test instruments |
| `Ruling 210` | quality-tooling ruling on the formatter declaration |
| `Ruling 214` | re-reading task rows against later rulings; process only |
| `Ruling 220` | process ruling on declaring a checks token coverage |
| `Ruling 235` | process ruling on quoting harness timeout bounds |
| `Ruling 236` | how test thresholds state their looseness; review process |
| `Ruling 238` | process ruling on naming a reading environment |
| `Ruling 240` | process ruling on counts in shipped files |
| `Ruling 241` | process ruling on exit-code forms in the review rubric |
| `Ruling 257` | instrument reach declaration discipline; quality tooling process |
| `Ruling 258` | declared-gaps lists are closed claims; review process |
| `Ruling 267` | process ruling on dev-image test acceptance widening |
| `Ruling 277` | counts in shipped files state unit and ref; documentation process |
| `Ruling 285` | process ruling on citations inside handoff records |
| `Ruling 317` | process ruling on image digests quoted beside readings |
| `Ruling 328` | test-suite process ruling on skips under parallel runs |
| `Ruling 333` | process ruling on dev check build cost |
| `Ruling 335` | process ruling about keeping spec sentences true as tasks land |
| `Ruling 344` | process ruling on reviewers requiring properties not means |
| `Ruling 348` | test-methodology ruling on a moved exit code as pass |
| `SF-02` | task label naming who built a module, no decision |
| `SF-09` | task label naming who built the authored overlay contract |
| `SF-10` | task label and its acceptance clauses for the served unit |
| `SF-10b` | task label quoted inside fixture text, provenance only |
| `SF-11` | task label naming who built the page assets |
| `SF-12` | task label naming who built the unit page renderer |
| `SF-12/3` | finding label on a deferred palette token; provenance |
| `SF-13/2` | finding about where a test helper lives, provenance |
| `SF-13/3` | finding about a test guard missing one reader name |
| `SF-14/2` | measurement that a mutant was killed only by lint |
| `SF-14/7` | finding label found while fixing another; provenance |
| `SF-15` | task label naming who built the trail module |
| `SF-15/2` | finding pointing a container trail at another task |
| `SF-15/5` | module split seam provenance between anchors and navigation |
| `SF-15/6` | fixture discharge of a finding; test provenance |
| `SF-17/11` | finding behind a test-harness plant, test provenance |
| `SF-18` | task label naming who built the narration player |
| `SF-18/4` | provenance of a closed hole in a test comment |
| `SF-19b` | task label naming who built serve modules |
| `SF-20/1` | pointer to a register reading in a test docstring |
| `SF-21/1` | finding that a register row was missing, provenance |
| `SF-22` | task label naming who built the run route |
| `SF-22/5` | finding about a raises-sweep floor, test tooling |
| `SF-23` | task label naming who filled the exercise package |
| `SF-24/3` | harness blindness finding on zero-size boxes; provenance |
| `SF-24/6` | file-size measurement that triggered a test split |
| `SF-26` | task label for the test harness's acceptance clauses |
| `SF-27` | task label naming who built the container page |
| `SF-27/3` | finding label on an aria-label remedy; provenance |
| `SF-27/4` | test runner import-path finding; tooling provenance |
| `SF-29/1` | provenance note that a transcript could not be captured |
| `SF-31` | task label naming who delivered placement goldens and ignore output |
| `SF-31/1` | finding recorded against another module's wording, provenance |
| `SF-31/3` | finding about a constant's public surface in tests |
| `SF-35` | task label for the process id-convention, not product behaviour |
| `SF-39` | task label naming who registered the serve verb |
| `SF-41` | example id used as fixture data in a delivery test |
| `SF-42` | task label naming who built the narrate verb |
| `SF-60` | example id used as fixture data in a delivery test |
| `SF-61` | example id used as fixture data in a delivery test |
| `SF-77` | example id used as fixture data in a delivery test |
| `SF-90` | example id used as fixture data in a delivery test |
| `SF-99` | example id used as fixture data in a delivery test |
| `SK-01` | task label naming who built a module, no decision |
| `SK-02` | task label naming who built a module, no decision |
| `SK-03` | task label naming who built a module, no decision |
| `SK-03/5` | finding behind the test process-output reader, test tooling |
| `SK-03/6` | test coverage detail about which suffixes a sweep reads |
| `SK-04` | task label; its grader-less refusal was superseded by authoring |
| `SK-05` | task label naming who built the authoring reference check |
| `SK-06/5` | finding that a register row was missing, provenance |
| `SK-07` | task label naming who built a module, no decision |
| `SK-08` | task label naming who built a module, no decision |
| `SK-08/1` | example id used as fixture data in a delivery test |
| `SK-09` | task label naming who built a module, no decision |
| `SK-09/6` | finding label; the reason is stated where it is cited |
| `TC-00/3` | finding about a module near its size bound, provenance |
| `TC-01` | task label and delivery test fixture id, no decision |
| `W13` | test-helper consolidation row, not a product decision |
| `W16` | doc-versus-code test provenance and a fixture example string |
| `W22` | reporting-process row on decompositions versus totals |
| `W26` | test-tooling row behind the gate-coverage tell |
| `W26/1` | finding about gate-coverage scan scope, test tooling |
| `W29` | test-tooling row naming the gate-coverage scan root |
| `W30` | development image test setting, quality tooling not product |
| `W36/5` | measurement reference for a snapshot figure; provenance only |
| `W37` | label for the class of guards that cannot fail |
| `W39/5` | names a test-assertion shape, test methodology only |
| `W40` | row splitting an oversized test package, process |
| `W40/3` | a surviving mutant that motivated a test, provenance only |
| `W40/4` | a surviving mutant that motivated a test, provenance only |
| `W59` | names the task that moved a function, provenance only |
| `W68` | test-tooling row scoping gate coverage to tracked files |
| `W70` | process row reference in a test comment, provenance |
| `W75` | open process row referenced by a test, provenance |
| `W76/2` | docstring import-list correction; provenance only |
| `W80` | open acceptance case recorded in a task record |
| `W92b` | module seam naming provenance inside the delivery package |
| `W95` | fixture provenance for two units sharing one origin |
| `W95/3` | test helper finding, test-only provenance |
| `W107/4` | measurement reference for a sweep exemption; provenance only |
| `W108` | fixture provenance; the fixture note states its own purpose |
| `W116` | quality-tooling row about the formatter declaration |
| `W117` | docs-convention row about one declaration home, process |
| `W117/2` | finding about splitting a test module, process |
| `W119/2` | finding about helper reach in a guard; process |
| `W123` | dev check timeout tooling, process quality instrument |
| `W124/4` | dev-image test provenance finding |
| `W127` | test harness workspace resolver measurement, process provenance |
| `W131` | dev tooling sweep of continuation-line readers |
| `W138` | test harness resolver reuse, test-only provenance |
| `W138/2` | a recorded limitation of one test sweep harness |
| `W142` | quality-tooling row on reading tracked files only |
| `W143` | test-harness row on where plants are written |
| `W148` | task label behind a scratch-tree sweep query |
| `W151` | test-harness row family reference, provenance only |
| `W151/5` | measurement reference for a sweep exemption; provenance only |
| `W152` | dev check provenance export tooling, process instrument |
| `W158/6` | dev gate skip reason tooling finding |
| `W162` | dev docker gate skip tooling, process instrument |
| `W162/5` | dev docker gate warm-cache tooling finding |
| `W162/6` | dev docker gate flag tooling finding |
| `W162/7` | dev docker gate default-run tooling finding |
| `W163` | dev docker gate tooling finding |
| `W191` | rubric self-certification form tooling, process |
| `W195/8` | formatter conflict note for code style, not product behaviour |
| `W196` | quality-tooling row about per-file formatter overrides |
| `W198/4` | finding about tests composing archive addresses, test hygiene |
| `W198/5` | finding about tests composing archive addresses, test hygiene |
| `W209` | label for a class of checkout-write defects in tests |
| `W209/5` | test-harness finding reference, provenance only |
| `W211` | dev image puts the command on PATH; tooling |
| `W211/2` | dev image racing measurement, tooling provenance |
| `W211/3` | dev image Dockerfile sentence check, tooling |
| `W212/2` | finding about raises-sweep plants surviving, test tooling |
| `W216` | test-harness row on the emission sweep's floor |
| `W217` | test-harness row on emission sweep write containment |
| `W217/5` | test-harness finding on readers inside the containment |
| `W219` | row rebuilding the raises-convention test instrument, test tooling |
| `W225` | dev check image naming by input content, tooling |
| `W229` | test-harness row on bytecode caches in plants |
| `W232` | sweep population rule for agent scratch trees; process |
| `W233` | test-harness row on one reader of child output |
| `W233/5` | test-harness finding on clock waits, test tooling |
| `W237` | test-harness row sharing the process-output reader |
| `W242/9` | measurement reference for a sweep exemption; provenance only |
| `W264/2` | rider about the fixture check admitting a test key |
| `W264/4` | rider naming a test clause exit code, provenance only |
| `W280` | module split at the size bound, names who moved code |
| `W298/2` | finding about a fixture check composing addresses, test hygiene |
| `W299` | internal package export-shadowing convention, not product behaviour |
| `W301` | rubric certification block check, process tooling |
| `W304` | process row on the review rubric's shell snippet |
| `W309` | provenance of the developer tooling report reader |
| `W326/2` | measurement of largest container size; fixture provenance |
| `W328/3` | harness reads declarations before geometry; test-method provenance |
| `W329/5` | test environment detail about bytecode settings under pytest |
| `W330` | docs-test row checking authoring guide trees, process |
| `W333/2` | measurement about harness fixtures lacking a rail |
| `W345/4` | test fixture provenance about committed bytecode state |
| `W352` | test-fixture row for the runnable corpus, not product |
| `W352/1` | test fixture provenance for an untested file |
| `W352/5` | finding about the runnable fixture's syntax, test provenance |
| `W361/2` | finding about the spawn detector's home, test tooling |
| `W361/3` | finding about the spawn detector missing a module, test tooling |
| `W364` | test-suite row on plugins under parallel runs, process |
| `W375` | test-tooling row for the one process-start detector |
| `W378` | test stand-in signal handling fix, test infrastructure only |
| `W381/2` | measurement behind a process rule on row minting |
| `W382` | test-suite row on where child processes import from |
| `W392` | process row reference, provenance only |
| `W395` | process row on the mint-collision rule, process |
| `W431/2` | test repair for browser room dependence; provenance |
| `W438` | process row for release cleanup, not product |
| `W441` | test repair for smooth-scroll timing; harness provenance |
| `round 2` | measurement round reference, pure provenance |
| `round 9` | integration round reference for a test plant, provenance only |
| `round 16` | review round finding reference in a test comment |
| `round 22` | round when an acceptance clause was added, provenance |
| `round 53` | round when a task dependency edge was added, provenance |
| `round 75` | process ruling on dev docker gate default runs |
| `round 113` | round when the register corrected a premise, provenance |
| `round 119` | pins record provenance for vendored font archives |
