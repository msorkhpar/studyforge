# E10 — Validation and QA

The machinery that makes "done" a fact rather than an opinion.

**Shared context for this epic.** Two of these tasks are dependencies of other
people's work rather than final checks, and that is deliberate. SF-25 lands
before the Java adapter is written, so the adapter is built against a green/red
signal. SF-26 lands before the corpus is generated, so byte-for-byte
reproducibility (R10) is enforced from the first page rather than asserted
about the last one.

**A check that can be satisfied by weakening it is not a check.** Every task
here fails loudly and names what failed (R6); none of them may be taught to
ignore a case in order to pass.

**A gate and a tracker are two commands, and neither replaces the other.** A
**gate** exits non-zero while anything is wrong, and its denominator is what was
built. A **tracker** always exits 0, and its denominator is the whole corpus —
it answers *"how much of this material exists at all?"*, which is a different
question and a useful one. ⛔ A tracker never restates a gate's verdicts, and ⛔
a scoped tracker prints but does not overwrite the full report, because a
filtered view written over a complete one lies about everything it did not look
at. CodeSignal needed both and confused them first.

⚠️ **Narration counts in the tracker.** A build that reports success while units
have pages and no audio is a build reporting on half its own output — CodeSignal
finished a wave with 80 silent units and called it complete. This is *not* the
same as making narration mandatory: an absent narration service stays a known
partial state (R8, SK-03). It is only that the partial state must be **named**,
never merely permitted.

---

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E10-validation-qa.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
