# ruling-46 — handoff

**Kind:** ruling record

**Ruling 46 — a sweep declares what it asserts.**

**Status:** done. `fix/ruling-46-sweep-declaration`, branched from
`release/m0-foundations` @ `ac4ed55`.

**Measured, pinned (`docker/dev/check`), 2026-09-09.**

| | tests | skips | ruff | floor |
|---|---|---|---|---|
| Base `ac4ed55` | 2274 passed | 8 | clean | clean |
| Branch | **2282 passed** | **8** | clean | clean |

⛔ **One file changed.** No fixture-access seam was built — Ruling 43's task
owes three tree-walks and the PO is scoping that seam once.

---

## What landed

`archive_documents(*, asserting)` excludes exactly
`{d for d, rule in INVALID_CORPORA.items() if rule in asserting}`.

⛔ **No default.** A sweep must say what it asserts, because a default is what
let the previous two versions of this helper be wrong without anybody choosing
anything.

| sweep | declares | why |
|---|---|---|
| counts agree with the module | `{"counts", "key-order"}` | two properties: the counts object's key tuple is an *ordering* claim, its values a *counting* one |
| block types are in the vocabulary | `{"vocabulary"}` | `check_blocks` yields one id for an unknown type **and** for a known type with wrong fields |
| blocks carry their row's fields | `{"vocabulary"}` | the same id, correctly |
| practice layout | `()` | ⚠️ **empty, said deliberately** — no rule id names the three-section layout, so there is nothing to exclude; inventing one would be a second vocabulary |

**Measured effect:** the directory exclusion dropped **9 declared-invalid
documents**; the counts sweep now excludes **1** of them and sweeps 8, and the
other three sweeps see all 9. Pinned by
`test_nine_declared_documents_are_swept_that_a_directory_exclusion_would_drop`.

## ⭐ The half that closes the defect is the message, not the exclusion

A sweep that under-declares still reds. ⛔ **The defect was never the red — it
was the misattribution**, because a red that reads as the fixture's fault
pushes toward editing the fixture, which is §1e's *"neutered into an input that
silently passes"*.

`sweeping(path)` returns the string every sweep passes down as its failure
message, so a declared fixture carries its declaration into **every** message
it can appear in — including an `ArchiveError` raised by the code under test,
which is why it is the yielded value rather than a check a sweep must remember
to call. Measured, by removing `"counts"` from one sweep's set:

```
E  AssertionError: invalid/count-mismatch/…/lesson-1.json — ⛔ 'count-mismatch'
   declares rule 'counts'. If this sweep asserts that rule, name it in
   asserting=; do not change the fixture.
```

⭐ The sweeps now yield `(where, document)` rather than `(path, document)`:
`path` was only ever used for `path.name`, so there is no longer an
unattributed name to reach for. **Forgetting is not a thing a call site can
do.**

## Negative controls, run rather than reasoned about

| broken back to | reds |
|---|---|
| directory exclusion (`if declaring(path) is not None`) | **3** tests |
| one sweep under-declaring (`{"counts", "key-order"}` → `{"key-order"}`) | 1 test, **with the attribution as the first line of the failure** |

⚠️ **One of the three only reds because the vacuity was closed.**
`test_a_sweep_excludes_exactly_…` compares `swept({rule})` with
`swept(()) - declaring_it`; under a directory exclusion both sides are empty
and it passes. It now asserts `declaring_it <= swept(())` first. ⛔ That is the
session's *"a check that cannot fail"* pattern, found in a test I had just
written to enforce the other one.

## ⛔ `VIOLATION.md` is documentation, and nothing parses it

Asserted rather than commented, in
`test_the_declaration_is_read_from_the_dict_and_not_from_violation_md`: every
one of the seven states its rule as the **spec** names it (`spec §6`, `R9`,
`R7`, `R5`), and **no checker rule id is a spec-rule token**. The two are
different vocabularies, so parsing the prose would need a prose parser *and* a
`spec §6 → counts` translation table to reach a dict that is already exported
and already pinned to the directory by
`test_the_invalid_set_is_exactly_what_is_on_disk`.

## Findings

### 50 `[structural]` — the test I had just written to enforce one rule broke the other

`test_a_sweep_excludes_exactly_…` was born vacuous. ⚠️ The general shape: *a test that asserts two derived sets are equal passes when both
are empty*, and the emptiness is exactly the bug it guards. ⭐ The fix is one
line asserting the sets are inhabited, and it is cheap enough to be routine.

### 51 `[structural]` — no rule id names a practice's three-section layout

`read_layout`
refuses a malformed practice with an `ArchiveError`, and nothing in
`tests/fixture_checks/` yields a rule for it — so no invalid fixture can
declare it, and that sweep asserts a property the declaration vocabulary cannot
express. ⚠️ Not fixed here: adding a checker rule id is a fixture-surface
change and belongs with whoever scopes that seam. ⛔ Until then the sweep's
`asserting=()` is honest rather than complete, and its comment says so.

## Decisions

**The declaration is `INVALID_CORPORA`, not `VIOLATION.md`.** ⛔ They are two
vocabularies, not two copies of one fact — the prose names the **spec** rule
(`spec §6`, `R9`, `R7`, `R5`) and the dict names the id a sweep uses. Parsing
the prose would have meant a prose parser **and** a `spec §6 → counts`
translation table to reach a dict that is already exported. Asserted, not
asserted-in-a-comment.

**`asserting` takes a set and has no default.** A default is what let the
previous two versions of this helper be wrong without anybody choosing
anything, and a single id under-excludes at exactly the grain the directory
over-excludes.

**The sweeps yield `(where, document)` rather than `(path, document)`.** ⭐ The
stronger form of the ruling's second half: rather than a message a call site
must remember to attach, there is **no unattributed name left to reach for**.
`path` was only ever used for `path.name`.

**`asserting=()` on the practice-layout sweep, said rather than implied.** ⛔ No
rule id names that property, so inventing one would have been a second
vocabulary. Honest rather than complete, with a comment saying which — see
finding 51.

**No fixture-access seam.** Ruling 43's task owes several tree-walks and the PO
is scoping that seam once; this branch changed one file.

## Surprises

⚠️ **The context budget was right about the code and wrong about the mechanism.**
The exclusion was ten minutes; the *attribution* took the rest, because the
obvious designs do not work: a generator cannot see the exception its `for` body
raised (the loop closes it with `GeneratorExit`, and `except AssertionError` at
the `yield` never fires), and a context manager at each call site reintroduces
the forgetting the ruling is about. ⭐ Yielding the message-string instead is
what made the problem disappear rather than be handled.

⚠️ **And the second surprise is finding 50** — a vacuous assertion written *one
paragraph after* implementing the guard against exactly that class. That is the
useful part of it: knowing the pattern by name did not stop me writing it, so
the mechanical tell is worth more than the description.

## For dependents

- ⛔ **A new sweep over the fixture tree must name its rule ids.** There is no
  default; `archive_documents()` with no argument is a `TypeError`, asserted.
- ⭐ **If your sweep reds on a fixture under `tests/fixtures/invalid/`, read the
  first line of the failure before touching anything.** It names the corpus,
  the rule that corpus declares, and what to do — which is to add that rule to
  `asserting=`, never to edit the fixture.
- ⚠️ **Whoever takes Ruling 43's task** inherits finding 51 and the general
  shape of this helper; the exclusion logic is four lines and is meant to move
  into that seam unchanged.
