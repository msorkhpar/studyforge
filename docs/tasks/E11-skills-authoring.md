# E11 — Skills and authoring kit

**This epic is the product** (R16). Everything before it is the means.

**Shared context for this epic — read spec §9 first.**

The end state is not "the Java repository has a study site". It is that
somebody points a skill at material they care about — a course site, a book, a
paper collection, a repository of exercises, their own notes — and gets this
format back: pages, narration, contents, navigation, practices, examples, and
their own progress. And then **keeps it**, as a durable personal record they
can review, re-run and extend.

**The Java corpus is the proving ground, not the destination.** Acceptance item
11 requires that the corpus was produced *by these skills*, not by bespoke
scripts, which is why OPS-04's entry points must be clean: a skill that has to
reach past a public entry point into internals is a skill that will not work
for anybody else's material.

**The division of labour mirrors R2.** Exactly one skill reasons about
unfamiliar material (SK-01). Every other skill is source-agnostic and operates
on contracts. If a second skill starts needing to understand a source, the seam
has been drawn wrong.

**⚠️ These do not all come late, and the original plan was wrong to say so.**
Every skill was scheduled at M7 — after the Java corpus had been built by hand
across M2–M6 — which made acceptance item 11 (*"the corpus was produced by the
skills"*) not merely unsatisfiable but **unfalsifiable**: a claim about history
that nothing recorded, about a corpus built before any skill existed.

⛔ **A skill precedes the artifact it produces, or it is a retrospective**
(spec §9). A skill written afterwards has been validated against exactly one
source — the one it was reverse-engineered from — and its first genuine test is
the second source, which is precisely where it must not fail.

So the epic splits in two:

| | Skills | Milestone | Why |
|---|---|---|---|
| **Producing** | SK-01, SK-02, SK-07, SK-05 | **M1–M2** | E07 and E09 are their **first output**, not their input |
| **Wrapping** | SK-03, SK-06 | **M4** | genuinely thin wrappers over entry points that must exist first |
| **Wrapping** | SK-04 | M9 | the same |

⛔ **CORRECTED, PO round 67 (`PO-67/1`): this table read `M7` for `SK-03` and `SK-06` after `b1569e2` moved both headers to `M4`.** ⭐ **The headers and [`README.md`](README.md) step 4.4 decide; the reason column stood.**

⚠️ **The cost of the front half is real and is accepted.** SK-02 at M2 is
written before anybody knows what a second adapter looks like. The answer is
that it starts deliberately minimal and grows — scaffolding a package layout, a
test tree and an audit command, leaving the source-specific reading to be filled
in, is buildable at M2 and is already exactly what its definition asks for. The
alternative is worse: a corpus built by hand and skills written afterwards to
claim they produced it.

⚠️ **The back half's original reasoning still stands** for SK-03, SK-04 and
SK-06: they are thin wrappers over entry points that already work, which is only
possible because the pipeline was built with those entry points in mind.

---

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E11-skills-authoring.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
