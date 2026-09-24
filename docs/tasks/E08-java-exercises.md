# E08 — Java exercise generation

Turning 168 existing test classes into real practices, with **no human in the
loop and no LLM-authored assertions**.

⛔ **SCOPED 2026-09-19 (`W389`, user direction) — that sentence is about THIS EPIC, and it
was read for a while as a rule about the framework.** ⭐ **It stays true of everything here:
a `bundled` exercise is blanked from a grader the corpus already ships, cleared by the two
gates below, and labelled `authoritative` — and it is exactly that property that earns the
stronger label.** ⭐ **Exercises whose assertions ARE authored exist now, are
`generated`/`advisory`, clear a different set of gates, and live in
[`E14`](E14-authored-exercises.md)** ([spec
§7](../specs/2026-09-08-studyforge-v1-design.md#exercises-authored-for-every-corpus-w389)).
⛔ **The two never trade labels, and nothing in `E14` re-opens this epic's mechanism.**
⚠️ **Two seams `E14` takes over rather than duplicating:** `EX-04` emits through the
bundle (`AX-04`) instead of its own emission,
and `EX-05`'s coverage report takes the
ledger's (`AX-07`) format so
one report covers every case. ⭐ **Both are edges to declare when `E14` lands, not work
inside this epic.**

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

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E08-java-exercises.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
