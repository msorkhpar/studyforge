# E06 — Exercise contract

What an exercise *is* to the framework, independent of how any source produces
one, and the reader-facing surface that presents it.

**Shared context for this epic.** Two rulings govern everything here.

**There are THREE exercise states, not two** (spec §7, C5): **none**,
**ungraded** (a prompt with nothing to check it), and **graded**. This was
verified against real material — all 19 SPARQL lessons end in an exercise and
none ships a test, so a two-state model would have deleted their exercises to
satisfy the schema. Only a graded exercise can complete a practice.

**Zero remains a first-class outcome.** Many Java units will have none, because
a pair failing a gate ships nothing rather than something weak. A unit with no
exercise renders as a clean reading page, not a broken practice page.

⛔ **RE-SCOPED 2026-09-19 (`W389`, user direction): zero is NAMED, never silent.** ⭐ **The
contract property above is unchanged** — a unit with no exercise still renders as a clean
reading page, and a gate that refuses still ships nothing rather than something weak.
⚠️ **What changed is what zero MEANS.** From `M10` an exercise is authored for material the
source did not grade, so zero is a reading the gates produced and the coverage report names
the gate that produced it — ⛔ **never a default nobody tried to move**
([`E14`](E14-authored-exercises.md), [spec
§7](../specs/2026-09-08-studyforge-v1-design.md#exercises-authored-for-every-corpus-w389)).

**R5 — nothing generated is presented as more authoritative than it is.** The
vocabulary is deliberately small and deliberately enforced in code, not in
review: provenance is `bundled`, `generated` or `user`; trust is
`authoritative` or `advisory`; and a `generated` grader **cannot** be recorded
or rendered as authoritative. CodeSignal needs this because its real grader is
hidden and unknowable. The Java corpus earns `authoritative` honestly, by
mechanical proof (E08) — which is exactly why the contract must be able to
express the difference rather than assuming one answer.

**This epic defines the contract. It generates nothing.** Generation is E08.

---

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E06-exercise-contract.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
