# FND-09 — handoff

**Kind:** task handoff — FND-09

*Ruling 46's helper leaves the module that could not hold it, and the two
subsets nobody was pinning turn out to have already gone stale — both of them,
by the same two fixtures.*

**Status:** done — one commit on `feat/FND-09-sweep`, branched from
`release/m0-foundations` @ `f1f22fd`. 13 files, 2 of them new. ⛔ **No fixture
changed and no entry of `INVALID_CORPORA` changed** (both out of scope).

| | tests | skips | quality floor | `ruff check` | `ruff format --check` |
|---|---|---|---|---|---|
| Base `f1f22fd` | 2666 passed | 8 | clean | clean, **266** files | clean, 362 formatted |
| Branch `930cdb7` | **2722 passed** | **8** | clean | clean, **268** files | clean, 365 formatted |

All 8 skips named and identical at both ends: 5 dev-image recursion
(`tests/docker/test_dev_image.py:351,357,377,386,405`), 3 knowledge-index
(`tests/test_knowledge_index.py:125,125,160`). Measured with
`docker/dev/check python3 -m pytest -q -rs`, `docker/dev/check python3 -m
tools.quality`, and — per the standing instruction while `FND-08/4` is under
ruling — `ruff check .` and `ruff format --check .` as their own runs in the
same pinned image, each with `.ruff_cache` purged.

⚠️ **The two `ruff` sub-commands do not count the same denominator** — 268
against 365 on the same tree — which is why both are given. `ruff check
--show-files` diffed at the two refs is **exactly** `tests/fixture_checks/sweeps.py`
and `tests/test_fixture_sweeps.py`, and `ruff format --check --diff` is empty,
so the `+3` in the right-hand column is a counting difference and not a file.
⭐ Ruling 48's habit applied to the instrument itself: a number without its
denominator named is not a reading.

---

## The price, re-measured before building (Ruling 55)

⭐ **Unlike `FND-08`, every recorded number reproduced exactly — and the
membership behind one of them did not.**

| Recorded in `E00` | Measured at `f1f22fd` | |
|---|---|---|
| `INVALID_CORPORA`, **7 entries**, `vocabulary.py:90` | 7 entries, `vocabulary.py:90` | ✅ |
| host module **567 / 600** | 567 | ✅ |
| migration **7 modules, 10 call sites** | 7 modules, 10 call sites | ✅ |
| by directory name **6** · no filter **2** · by declaration **0** | 6 · 2 · 0 | ✅ |
| `INVALID`, **5 of 7**, `validate/test_run.py:19` | 5 of 7, line 19 | ✅ |
| `FIXTURES_WITH_A_VALID_MANIFEST`, **4 of 7**, `manifest/test_document.py:358` | 4 of 7, line 358 | ✅ |
| `including_invalid=` **gone from every `.py`** | 0 hits | ✅ |

⚠️ **But `7 / 10` is not the same seven it was.** The walk table in `E00` cites
`e5bcc85`. Running the same classifier over an export of `e5bcc85` reads
**6 modules and 9 call sites** — `tests/studyforge/unit/builder/test_init.py`
does not exist there. `SF-10` added it (`c33f231`) with a `depth1, depth2` walk,
and it is the seventh module. ⭐ **So the recorded price was taken after `SF-10`
merged and is still exactly right today — while the set it counts gained a
member and would have gained another from any `SF-1x` that walks fixtures.**
⛔ That is Ruling 55 in its quieter form: **the number can be stable while the
thing it counts is not**, and only re-running the instrument tells you which.

`6 · 2 · 0` sums to eight over seven modules because
`tests/studyforge/exercise/test_record.py` carries **both** policies — a
no-filter walk and two `"/invalid/" in path` filters over its result.

---

## What landed

### The seam moved, and gained a denominator

`tests/fixture_checks/sweeps.py` (**new**, 234 lines) holds `archive_documents`,
`declaring` and `sweeping`, beside the `INVALID_CORPORA` they read. `sweeping()`'s
message is **byte-identical** — asserted, not eyeballed. The exclusion is now a
named primitive, `excluded_by(asserting)`, so the two views and the count read
one rule:

| name | what it is |
|---|---|
| `_matching(glob, within)` | ⛔ **the one walk** — numerator and denominator cannot come from two traversals |
| `fixture_paths(*, asserting, glob, within)` | `(where, path)`, whole tree or any glob |
| `archive_documents(*, asserting)` | `(where, document)` — `fixture_paths` restricted to `raw/`, verbatim behaviour |
| `coverage(*, asserting, glob, within)` | `Coverage(swept, excluded)`, `.total`, and a `__str__` that reads as a sentence |
| `ENFORCERS` | the two modules that must never consume it, each with its circularity written out |

⭐ **The attribution is now the yielded value of every view**, not just of the
document one — so a migrated sweep gets Ruling 46's message whether or not its
author read Ruling 46. Asserted by
`test_every_path_the_seam_yields_arrives_attributed`.

`tests/test_fixture_sweeps.py` (**new**, 252 lines) is where Ruling 46's tests
now live — they were never about blocks. `tests/studyforge/archive/test_blocks.py`
goes **567 → 403** lines, which is the size relief `E00` predicted and then some.

### The migration — 10 call sites, 7 modules

| module | was | now | effect |
|---|---|---|---|
| `archive/test_document.py` | `depth1, depth2` | `{counts, digest, personal-data, exercise-trust}` | **11 → 16** documents |
| `archive/test_scrub.py` | excludes `invalid/personal-data` by path | `{personal-data}`, whole tree | same 37, read from the declaration |
| `archive/markdown/test_init.py` | ⛔ no filter at all | `{vocabulary}` | same 40 today; load-bearing the day a fixture declares it |
| `corpus/container/test_document.py` | `depth1, depth2` | `{corpus-api, ordinal-gap}` | **3 → 8** container maps |
| `corpus/placement/test_corpora.py` | `FIXTURES = ("depth1","depth2")` | `{corpus-api}`, derived | **2 → 8** corpora parametrized |
| `exercise/test_record.py` | ⛔ no filter + two `"/invalid/" in path` | `{exercise-trust}`, both sets derived | the refused set is now `excluded_by(ASSERTED)` |
| `unit/builder/test_init.py` | `depth1, depth2` | `{personal-data, exercise-trust}` | **3 → 8** containers |

⭐ **Every one of those gains is a document that was being dropped for a rule it
does not break** — Ruling 46's whole argument, now paid rather than argued.

**One site keeps its walk and carries a named reason:**
`test_no_exercise_appears_anywhere_in_the_depth_one_fixture` names `depth1` as
its **subject**, not as an exclusion policy — E06's clause is about that one
corpus. ⛔ Not the same thing as "skip `invalid/`", and the comment says so.

### The two enforcers, excluded in the code

`sweeps.ENFORCERS` names both with the circularity spelled out, and three tests
hold it: the set is exactly those two, neither imports the seam, and — the half
that would otherwise rot — **both still walk the tree themselves**. An enforcer
excluded from the seam *and* asserting nothing is the state this exclusion
decays into.

### Coverage, everywhere `assert seen > 0` used to be

Ruling 48's denominator replaced ten vacuity guards. `assert seen > 0` passes on
a sweep that read one document of twenty and passes identically the day an
exclusion is widened by mistake; `assert seen == coverage(asserting=…).swept`
does not. Where the property is about a subset (practices among documents) the
floor is **pinned** instead, with a comment saying which.

---

## ⛔ The migration it found: both unknown subsets were already stale, by the same two fixtures

⚠️ **`E00` predicted that "an eighth fixture lands silently in both". It has
already happened, twice, with the seventh and the sixth.** `count-mismatch` and
`user-authoritative` entered `INVALID_CORPORA` and reached **neither** subset.

| | recorded | actual, measured | what it means |
|---|---|---|---|
| `validate/test_run.py:19` `INVALID` | 5 of 7 | ⛔ **all 7 report exactly one rule** — `count-mismatch` → `counts`, `user-authoritative` → `document` | two corpora the validator handles correctly were **never exercised** |
| `manifest/test_document.py:358` `FIXTURES_WITH_A_VALID_MANIFEST` | 4 of 7 | ⛔ **6 of 7 load at depth 1**; only `bad-corpus-api` is refused | two corpora with readable manifests were **never checked** |

Both are now derived from the declaration:

- `INVALID` keeps **its own rule vocabulary** — the module's argument that two
  checkers with different subjects may disagree about a rule's *name* is right —
  and gains `test_every_declared_corpus_is_exercised`, which pins the **keys** to
  `INVALID_CORPORA` and asserts the two dicts still differ, so the divergence
  cannot quietly become an accident.
- `FIXTURES_WITH_A_VALID_MANIFEST` becomes
  `sorted(set(INVALID_CORPORA) - set(WITHOUT_A_VALID_MANIFEST))`, where the
  exception dict carries `bad-corpus-api` **with its `why`** — the
  `personal-data-shapes.md` precedent, not a fresh mechanism.

---

## The sweep — Ruling 70's form, with Ruling 76's agreement

Pinned image `studyforge/dev:local` via `docker/dev/check`. Every row purges
`__pycache__` and `.pytest_cache`, applies **one same-size mutant**, runs the
**whole** suite, and records the **process exit code** and the **pytest summary
tail**. ⛔ **A row with no verdict is a row where those two disagree** — the
harness refuses to print `SURVIVED` or `KILLED` unless they match, and refuses
`KILLED` with zero counted failures. That is Ruling 76's hole: a stuck-green
instrument reports the baseline's correct verdict, so the baseline row cannot
catch it and the agreement has to be checked per row.

```
| row                                                        | exit | fail| verdict   | pytest tail
| BASELINE (opening) — must SURVIVE                          |    0 |   0 | SURVIVED  | 2722 passed, 8 skipped
| exclusion reads the directory, not the declaration         |    1 |  10 | KILLED    | 10 failed, 2676 passed, 8 skipped
| exclusion excludes nothing at all                          |    1 |  20 | KILLED    | 20 failed, 2708 passed, 8 skipped
| sweeping() drops the attribution                           |    1 |   2 | KILLED    | 2 failed, 2720 passed, 8 skipped
| sweeping() drops "do not change the fixture"               |    1 |   2 | KILLED    | 2 failed, 2720 passed, 8 skipped
| asserting= gains a default                                 |    1 |   1 | KILLED    | 1 failed, 2721 passed, 8 skipped
| coverage() reports a vacuous 0                             |    1 |  12 | KILLED    | 12 failed, 2710 passed, 8 skipped
| the walk yields nothing                                    |    2 |  -1 | KILLED    | 1 error in 1.02s
| an enforcer is quietly dropped from ENFORCERS              |    1 |   3 | KILLED    | 3 failed, 2719 passed, 8 skipped
| the validate subset goes back to five of seven             |    1 |   2 | KILLED    | 2 failed, 2718 passed, 8 skipped
| the manifest subset is hand-listed again                   |    1 |   5 | KILLED    | 5 failed, 2714 passed, 8 skipped
| test_document.py goes back to excluding by directory name  |    1 |   2 | KILLED    | 2 failed, 2720 passed, 8 skipped
| test_record.py goes back to the directory name             |    1 |   2 | KILLED    | 2 failed, 2720 passed, 8 skipped
| a sweep in test_blocks.py under-declares                   |    1 |   1 | KILLED    | 1 failed, 2721 passed, 8 skipped
| BASELINE (closing) — must SURVIVE                          |    0 |   0 | SURVIVED  | 2722 passed, 8 skipped
mutants: 13/13 killed · baseline: opening=SURVIVED closing=SURVIVED · SWEEP: PASS
```

⚠️ **Row 7 is the one to read twice.** *"The walk yields nothing"* exits **2**,
not 1, with `1 error` and no failure count — parametrization over an empty walk
is a **collection** error, not a test failure. Exit code and tail still agree
(`2` ≠ 0 and `error` in the tail), which is exactly what the agreement rule is
for: a harness that only grepped for `N failed` would have counted zero and
called this row `SURVIVED`.

⭐ **The harness ran the whole suite for every row, never a subset.** It lives at
`graphify-out/sweep_fnd09.py` — deliberately, because the first attempt put it
at the repository root and **the opening baseline went red**: `ruff`'s `D103`
fired on the harness's own undocumented functions. See `FND-09/1`.

---

## Decisions

**The seam is `tests/fixture_checks/sweeps.py`, not a name beside a caller.** A
helper that reads `INVALID_CORPORA` belongs beside the declaration; anywhere
else and the next person needing one reads the directory name instead. It is the
package's sixth module and the docstring table says so.

**One walk, three views — not one generator and a second file walker.** `E00`
asked for the helpers moved verbatim, and three of the seven call sites walk
things `archive_documents` cannot see (`container.json`, `corpus.json`, the
whole tree for R7). Rather than duplicate the traversal, `fixture_paths` is the
general form and `archive_documents` is it restricted to `raw/`. ⛔ **`coverage`
reads the same `_matching`**, so a numerator and a denominator from two
different traversals is not a state this module can reach.

**The exclusion became a named function.** `excluded_by(asserting)` was four
lines inline; it has its own test now, because a primitive that only ever fails
through a sweep is a primitive whose failure names the wrong subject.

**Rule sets were measured, never guessed.** For each migrated sweep I ran every
invalid corpus through the code under test and read which ones refuse. That is
where `{corpus-api, ordinal-gap}` and `{counts, digest, personal-data,
exercise-trust}` came from — ⛔ **not from reading `VIOLATION.md`**, which names
spec rules and not checker ids (still asserted, in the moved test).

**`INVALID` keeps its own vocabulary; only its keys are pinned.** The module's
argument was right. It just had no mechanism, and "right with no mechanism" is
how it lost two fixtures.

**The `depth1` walk stays a walk.** A test whose *subject* is one corpus is not
a test with an exclusion policy. `E00` forbids "by directory name" as a reason;
this is not that, and the comment distinguishes them so the next reader does not
have to re-derive it.

---

## Surprises

⚠️ **The prices did not move, and I had been told to expect that they would.**
`FND-08`'s founding numbers had *all* moved. Here every one reproduced, to the
line number. ⭐ The useful part is the near-miss underneath: the count `7 / 10`
is stable, and the *set* it counts gained a member (`SF-10`'s builder test) after
the ref the walk table cites. **A reproducing number is not evidence that
nothing moved** — it is evidence that the number reproduces.

⚠️ **`tests/studyforge/corpus/container/test_document.py` was at 599 of 600
lines.** The migration is a net *gain* in coverage and still had to be squeezed
in under a single line of headroom: I dropped a now-dead `FIXTURES` constant and
its `Path` import, turned `fixture_maps` into a generator, and used the seam's
`where` in place of `str(path.relative_to(repository_root()))` — which is
strictly better, because the round-trip failure now carries Ruling 46's
attribution. It landed at **598**. ⛔ **But the lesson is `E00`'s own, arriving
in a second module: a file at its ceiling cannot absorb a migration**, and the
only reason this one did is that the migration happened to make it shorter.

⚠️ **The negative-control harness broke its own baseline, and it was `FND-08/4`
again.** A `.py` file at the repository root is swept by `tests/test_repository.py`,
which runs `ruff` with the pydocstyle rules — so the *opening* baseline read
`1 failed` before a single mutant had been applied. `python3 -m tools.quality`
was clean throughout. ⭐ Ruling 70 says the baseline must survive at both ends,
and this is a good demonstration of why: the failure was in the instrument's
scaffolding, not in the tree, and every mutant row would have been measured
against a red baseline.

---

## Findings

### FND-09/1 `[structural]` The sweep harness is part of the tree it measures

A negative-control harness written as a `.py` file in the checkout is **swept by
the checks it is trying to hold still**. Mine was, and the opening baseline went
red on `ruff D103` before any mutant existed. ⭐ The fix is one line — put the
harness under a `TOOL_OUTPUT_DIRS` path (`graphify-out/`) — but the general
shape is worth a convention: ⛔ **a sweep harness lives outside `SCAN_ROOTS`, or
Ruling 70's baseline is measuring the harness.** ⚠️ This is the third round in
which the pinned image's `ruff` found something `tools.quality` did not; it is
the same surface as `FND-08/4`, which is still under ruling.

### FND-09/2 `[structural]` A stale subset is invisible until something derives it

Both previously-unknown copies of the invalid set were stale, by the **same two
fixtures**, and neither had failed anything. ⭐ The general shape: **a
hand-written subset of a declared set is a check that silently narrows** — it
does not go red when the parent grows, it just tests less, and its coverage
number (if it has one) goes *up*, because it is counting what it kept. ⚠️ The
tell is mechanical: any literal list whose members are all keys of a dict
somewhere else. There are two more of these in the tree that I did not touch
because they are outside this task — see `FND-09/4`.

### FND-09/3 `[structural]` `tests/studyforge/corpus/container/test_document.py` is at its ceiling

598 of 600 after this change, 599 before it. ⛔ **It has no room for the next
migration**, and it is the second module in two tasks to be discovered in that
state (`test_blocks.py` at 567 was `FND-09`'s own premise). ⭐ The split seam is
visible: the round-trip and vocabulary halves share no helper. ⚠️ Not done here —
that is a task, not a line in this diff.

### FND-09/4 `[structural]` Finding 51 is still open and is now the only thing `asserting=()` is honest about

Ruling 46 left `asserting=()` on the practice-layout sweep because no rule id
names a practice's three-section layout. That is still true, and the sweep is
still honest-rather-than-complete. ⚠️ It now sits beside a `coverage()` call that
reports 20 of 20, which reads as *complete* to someone skimming. ⛔ Adding the
rule id is a fixture-surface change and stays out of scope, but the comment
should probably say "the denominator is right and the declaration is empty",
which is a sentence I did not add because it is finding 51's, not mine.

### FND-09/5 `[local]` `test_no_exercise_appears_anywhere_in_the_depth_one_fixture` had no floor

It looped over `depth1` asserting a negative and would have passed on an empty
glob. Given a floor (`swept >= 6`) on the way past, since Ruling 48 was already
the subject. ⚠️ Named here because it is a change outside the ten call sites.

---

## For dependents

- ⛔ **A new sweep over the fixture tree imports from `tests.fixture_checks`, not
  from a test module.** `archive_documents` for `raw/` documents, `fixture_paths`
  for anything else (`glob=`, `within=None`). There is still no default for
  `asserting`, and `archive_documents()` is still a `TypeError`.
- ⭐ **Pair every sweep with `coverage(asserting=…)`.** Same arguments, same
  walk. `assert seen == coverage(...).swept` is the shape; a pinned floor is the
  shape when your property is about a subset of what you read.
- ⚠️ **If your sweep reds on a fixture under `tests/fixtures/invalid/`, read the
  first line of the failure before touching anything.** It names the corpus, the
  rule that corpus declares, and what to do — which is to add that rule to
  `asserting=`, never to edit the fixture. This is unchanged and is now attached
  to every view the seam offers.
- ⛔ **Do not route `tests/test_fixture_consistency.py` or
  `tools/tests/quality/personal_data/test_registry.py` through the seam.** They
  are the declaration's enforcers; `sweeps.ENFORCERS` says so in the code and
  three tests hold it.
- ⭐ **Adding an eighth invalid fixture now reds in four places by design** —
  the on-disk pin, the R7 registry, `validate/test_run.py`'s `INVALID`, and
  `manifest/test_document.py`'s subtraction. ⛔ **That is the point.** Add the
  entry to `INVALID_CORPORA`, then give each red the one line it asks for.
- ⚠️ **`FND-08`'s `tools/quality/pointers.py` and this seam share no code, as
  Ruling 47 asks.** They walk different trees for different units — a markdown
  line versus a JSON document — and the only thing they share is the reasoning
  about what a false positive looks like. Evidence, not a primitive.
