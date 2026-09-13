# E08 — Java exercise generation

Turning 168 existing test classes into real practices, with **no human in the
loop and no LLM-authored assertions**.

**Shared context for this epic — read this before any task.**

⛔ **`EX-00` BLOCKS ALL OF E08, INCLUDING THE TASK YOU WERE SENT HERE FOR.** It
is a one-agent-day feasibility spike whose **negative result is a success**, and
until it runs nobody knows whether E08 yields a study product or a pile of
generated holes. ⚠️ **It needs `TC-00`'s pinned image: its deliverable is a
wall-clock measurement that decides the shape of this epic, and one taken on a
host JDK is not reproducible (R15).** ⭐ **The gate is stated HERE, in the block
this epic itself flags *read this before any task*, and not only in `EX-00`'s own
heading further down** — ⛔ **because an agent dispatched straight to `EX-01`
opens this file well below the heading that would have told them** (Ruling 167,
CTO round 42).

⛔ **PO round 74 — this whole epic is `M9`.** ⭐ **It waits on the Java adapter (`EX-01` on
`JS-04`), and the user placed that corpus last, as the re-validation** ([`README.md`](README.md)
§ M9). ⚠️ **`TC-00` is still its image, and it lands earlier, at `M5`.**

CodeSignal's scaffolder is 1,793 lines because it must *guess* at a grader it
cannot see. Every assertion it invents is a judgement call, which is why its
governing ruling forbids presenting any of them as authoritative.

**The Java corpus inverts that problem.** It ships the grader: 168 test classes
that are real ground truth, paired 1:1 with implementations in almost every
module. Nothing needs inventing. What needs creating is the *hole* — and the
result is **mechanically self-verifying**:

```
for each (Impl.java, ImplTest.java) pair:
    select the methods the lesson README names   (JS-04's signal)
    for each selected method:
        blank EXACTLY THAT ONE body   ->  candidate hole
        GATE 1: run ImplTest          MUST FAIL, failure attributed
    blank every hole that cleared Gate 1  ->  starting code
    GATE 2: run ImplTest against the original   MUST PASS
    cap the result; split into several practices if over
    ship.  provenance=bundled, trust=authoritative
```

⚠️ **Gate 1 is PER-METHOD. A class-granular gate is close to vacuous** and an
earlier draft of this epic specified one. Blank every body in a class and the
test class fails for almost any pair that has a test at all — proving only
*"this test touches this class"*. Concretely:
`19-concurrency-pitfalls/.../ConcurrencyBestPracticesTest.java` asserts on a
nested record's accessors, `equals`, `hashCode` and compact-constructor
validation; a blanker that leaves records alone keeps ~15 of those assertions
passing while one failure elsewhere still clears a class-level gate. The reader
gets a practice that is mostly already done, marked `authoritative`.

**The claim is per-method, so the check must be.** This is the sentence the
whole `trust=authoritative` position rests on (R5). The cost is roughly one
build per candidate method; EX-02 caches by content address and **EX-00
measures whether it is tolerable before any of this is built**.

**Gate 2 proves the grader works.** A test that fails against the committed
implementation is broken, and shipping it would hand the reader an
unwinnable practice.

A pair clearing both is **provably solvable** — git holds the reference
solution — and **provably non-trivial**. That is a stronger honesty guarantee
than CodeSignal can obtain, with far less machinery, and it is the entire
reason this epic can mark graders `authoritative` under R5 where CodeSignal
cannot.

**Expected yield is below 100%, and that is the honest outcome, not a bug.**
Some tests will not discriminate. Those units ship reading-only and are named.
⛔ **Do not "fix" a low yield by loosening a gate or by generating an
assertion.** That converts a proof into theatre, and it is the one failure mode
this design exists to prevent.

---

### EX-00 — Exercise feasibility spike ⛔ BLOCKS ALL OF E08
**Milestone** **M9** · **Depends on** TC-00 · **Team** pair
**Owns** a findings report; **no shipped code**
**Context** ~40k — spec §7, a hand-picked sample of `JS` classes

⚠️ **This task could not run as originally scheduled, and the fix is TC-00.**
It was written with no dependencies at M0, before any toolchain image existed —
so it would have run Maven on whatever JDK the host happened to have, which R15
exists to forbid. That is not a scheduling detail: this task's headline number is
**wall-clock per gate run**, and the whole shape of E08 is decided from it. A
timing measured on an unpinned host toolchain is not reproducible and cannot
carry that weight. `TC-00` is a minimal pinned JDK + Maven image that exists for
exactly this.

⚠️ **It also left M0 entirely.** Exercises are not on the first consumer's path —
the first corpus is small and its material may not be runnable at all (spec
§11.0) — so spending week one on a Java exercise spike would have been attention
spent on the last thing to be delivered. ⛔ **It remains the first thing done
whenever E08 starts**, for its original reason: it moves the largest unknown to
the front instead of discovering it at the end.

**Definition.** This epic's entire value rests on an unmeasured assumption, and
until EX-00 runs, nobody knows whether E08 yields a study product or a pile of
rejects. It moves the project's largest unknown from M6 to week one for the
cost of one agent-day. **A spike: its output is an answer, and anything built
is explicitly throwaway.**

Three parts:

**(a) Establish the baseline.** Run `mvn test` on the untouched repository
**inside TC-00's image** and record which of the 168 test classes are green
**today**. Gate 2 is "the test passes on the original" — if a class is already
red on the pinned JDK, its pairs silently yield nothing and it will read as a
blanking bug for days. This is step zero and nothing in E08 is meaningful
without it. ⛔ **Record the image tag in the report**: a baseline that does not
say which toolchain produced it cannot be compared against anything later.

**(b) Hand-blank and hand-gate ten pairs** across the shape spectrum, chosen
deliberately, not conveniently: a clean pure-function class
(`16-streams-api/StreamCreation`); a record (`09-records`); a sealed hierarchy
(`10-sealed/Shape`); a concurrency class (`19-concurrency-pitfalls`); the
787-line outlier (`39-data-structures/CommonDataStructures`, ~100 methods,
937-line test); and one from `08-object-oriented`, which has 11 implementation
classes and 3 tests.

**(c) Report** — per-method versus per-class gate behaviour on real code;
observed yield; wall-clock per gate run; exercise size distribution; and
**hang behaviour**, which is the one that can silently burn a day (see EX-02).

⚠️ **Predicted zero-yield shapes, to be confirmed rather than discovered:** 48
files contain records, 34 interfaces, 14 sealed types, 13 enums. Where the
teaching content *is* the declaration — a record's accessors, `equals` and
`hashCode` are implicit and unblankable — there is nothing to blank.
`09-records`, `10-sealed` and much of `05-pattern-matching` and
`28-enhanced-enums` are expected to yield nothing. That is honest (spec §7),
but it must be predicted here, not mistaken for a defect once EX-01 runs.

**Acceptance.** A green/red baseline for all 168 test classes is recorded,
against a **named pinned image tag**. Ten pairs are hand-gated with results. The
report states an expected yield range with its reasoning, per-run cost, and
whether the per-method gate is affordable. **If yield is implausibly low, this task's output is a
recommendation to change or drop the approach — and that is a successful
spike, not a failed one.**

---

### EX-01 — Body-blanking transformer
**Milestone** **M9** · **Depends on** JS-04, **EX-00** · **Team** pair
**Owns** `JS/exercise/blank.py`
**Context** ~40k — a sample of `JS` implementation and test classes

**Definition.** Turns a committed implementation class into starting code by
blanking **selected** method bodies — replaced by a stated TODO and a failing
default, with signatures, imports, class structure and documentation preserved
so the result **compiles**.

⭐ **Selection, not wholesale blanking** (spec §7). The corpus makes this
non-negotiable: implementation classes run to a median of 211 lines and a
maximum of 787, with a median of ~21 blankable bodies and up to ~100. Blanking
`CommonDataStructures` wholesale yields one all-or-nothing practice of ~100
methods across 787 lines graded by a 937-line test. That is a rewrite, not an
exercise.

Two inputs bound it:

- **The lesson README names the methods** — JS-04 exposes this signal, and it
  is the same 97% signal used for attachment. What a lesson discusses is what
  it teaches, and therefore what is worth blanking.
- **A size cap**, expressed in blanked methods and lines. A pair that would
  exceed it emits **several practices**, not one (EX-04). A single hole that
  cannot come under the cap is reported, not shipped.
Compiling matters — Gate 1 must fail on *assertions*, not on a build error,
or it proves nothing about the hole.

The generated file states, in the file, that it is generated and what the
reader is expected to do. Deterministic: same input, same bytes (R10).

A class it cannot transform safely — unusual structure, generated code,
anything ambiguous — is **reported by name and skipped**, never emitted
half-transformed (R6).

**Acceptance.** Blanked output compiles for every pair it accepts. Signatures
and imports are unchanged. Re-running produces identical bytes. A class it
cannot handle is named and skipped. The reference solution is recoverable from
git for every emitted exercise.

---

### EX-02 — Gate runner
**Milestone** **M9** · **Depends on** EX-01, OPS-01 · **Team** pair
**Owns** `JS/exercise/gates.py`
**Context** ~35k — spec §7, EX-01 and OPS-01 outputs

**Definition.** The two gates, run against the dockerised Maven toolchain so a
verdict does not depend on whose machine produced it (R15).

Results are **cached by content address** so a re-run is cheap: 168 pairs × 2
builds is otherwise a long wait for an answer that has not changed. The cache
keys on the blanked source, the test source and the toolchain identity —
because a toolchain change can legitimately flip a gate.

⚠️ **A hang is not a gate verdict, and this corpus will hang.** 23 test classes
call `Thread.sleep`, 10 use Awaitility, 6 depend on `LocalDate.now()` or
`Random`, and only 9 declare `@Timeout`. Blanked code that throws inside a
worker thread leaves a `CountDownLatch` uncounted and the run **hangs** rather
than failing — neither Gate 1 nor Gate 2, and a silent multi-hour stall in a
batch of thousands of builds. **Every gate run carries a hard timeout, and a
timeout is its own recorded verdict**, distinct from pass and from fail.
Likewise a **build error is distinct from a test failure** — Gate 1 must fail on
assertions, not on a broken build, or it proves nothing about the hole.

Every rejection is recorded **with which gate failed and why**. A rejection is
information about the material, not an error to suppress.

**Acceptance.** A pair whose test passes on blanked code is rejected as Gate 1
and named. A pair whose test fails on the original is rejected as Gate 2 and
named. A clearing pair is marked `bundled` + `authoritative`. The run is
reproducible and incremental. A build error is distinguished from a test
failure — they are different verdicts.

---

### EX-03 — Practice module and build wiring
**Milestone** **M9** · **Depends on** EX-01 · **Team** solo
**Owns** `JS/practice/` and its build file
**Context** ~25k — `JS/pom.xml`, a module `pom.xml`

**Definition.** The additive `practice/` Maven module whose source tree mirrors
addresses, joined to the build by **one** `<module>` line in the root
`pom.xml` — the single existing-file change R3 permits.

Reader-facing practice material still co-locates beside the `.md` (§5); only
**compilable** sources live here, because Maven compiles only what sits on a
source root. This is a stated, reasoned exception to co-location, not an
oversight — a practice the build cannot see is a practice the reader cannot run.

**Acceptance.** Generated exercises compile and run in the module. The root
`pom.xml` diff is **exactly one line**. No other pre-existing file is touched.
The module builds offline against the primed cache (TC-03).

---

### EX-04 — Exercise emission
**Milestone** **M9** · **Depends on** EX-02, EX-03, SF-23 · **Team** pair
**Owns** `JS/exercise/emit.py`
**Context** ~40k — SF-23, EX-02, EX-03 outputs

**Definition.** Writes gate-clearing exercises into the archive as practice
documents with their workspace commands, and the reader-facing material into
its co-located location.

⭐ **One pair may emit several practices.** EX-01's size cap means a large class
is split rather than shipped whole, so emission is not one-practice-per-pair.
Each emitted practice is independently gated, independently addressed, and
independently completable — a reader who finishes three of a class's five
practices has finished three practices, not 60% of one.

**Units with no clearing exercise emit nothing** and are recorded as
reading-only — the first-class zero outcome (spec §7). Container maps' declared
practice counts are updated to what actually shipped, so SF-25's
declared-versus-present check stays meaningful rather than being satisfied by a
number nobody set.

**Acceptance.** `studyforge validate` passes. Every emitted exercise cleared
both gates — traceable to EX-02's record. Declared counts match what is
present. A reading-only unit renders with no practice affordance (SF-24).

---

### EX-05 — Coverage report
**Milestone** **M9** · **Depends on** EX-04 · **Team** solo
**Owns** `JS/exercise/report.py`
**Context** ~20k — EX-02 and EX-04 outputs

**Definition.** The honest account: how many of the 168 pairs cleared both
gates, which failed which gate and why, and which of the 166 units are
reading-only as a result.

**Stated as a proportion of the real denominator**, never rounded up and never
framed as a completion percentage. CodeSignal's own documentation is the model
here — it reports "9 of 1,290 units readable and 0 practices captured" without
softening it, and revised its denominator upward when the old one was found to
be flattering. A coverage number that cannot go down is not a measurement.

**Acceptance.** Numbers reconcile with EX-04's output exactly. Every rejected
pair appears with its failing gate. No unit is counted as having an exercise it
does not have. The report is committed and regenerated by OPS-04.
