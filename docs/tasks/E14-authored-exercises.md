# E14 — Authored exercises

Exercises for **every** corpus: built from the source's own examples, its practice code
and its tests where it has them, and authored from the page's material where it has none
— each one a real-life ask, graded by tests of the main ask and of every edge case.

**Shared context for this epic — read this before any task.**

⛔ **The authority is [spec §7, *Exercises authored for every
corpus*](../specs/2026-09-08-studyforge-v1-design.md#exercises-authored-for-every-corpus-w389),
and it should be read whole before any row here is started.** ⭐ **The argument, with the
user's words unabridged and the four answers that closed its open questions, is
`W389` and its proposal.**

⭐ **The user's sentence this epic exists to satisfy:** *"we are building CodeSignal or
LeetCode with the idea of LLM extracting the content from a given source and make it an
enjoyable interactive easy to read and navigate website."*

## ⛔ Four properties, and every row here is judged against them

1. ⛔ **Nothing the source already has is lost.** The reading floor is untouched and every
   example still renders verbatim. The **source ledger** is the proof: every fenced example
   and every test file is either the basis of an exercise or carried with a written reason
   it is not, and an entry with neither is refused.
2. ⛔ **Authoring happens ONCE, at ingestion**, by a skill the converting agent runs, into
   the **corpus repository**. ⛔ **No model runs at build time and none at serve time.** The
   site stays offline (R8) and the build stays byte-reproducible from the committed
   bundles (R10).
3. ⛔ **R5's honesty survives as GATES, not as a promise.** An authored grader is
   `generated`, therefore `advisory`, and ships only with a gate record `studyforge
   validate` re-reads. ⛔ **No gate may be disabled by configuration, and a shortfall is
   reported rather than engineered away.**
4. ⛔ **The framework still knows nothing about any source** (R1). Every source-specific
   fact arrives as data — the bundle on disk, the manifest, the ledger — and the adapter
   seam stays where R2 put it.

## ⭐ What the user ruled, 2026-09-19, and what it changed

| the question | the answer | what it binds here |
|---|---|---|
| a corpus whose subject is not code | ⭐ **the quiz shape is IN this milestone** | `AX-05`, `AX-06`, and `AX-09`'s second surface |
| is the reference solution shown | ⭐ **always available to the reader** | `AX-04` ships it; `AX-09` offers it, never gated on a pass |
| is an authored grader labelled | ⭐ **yes, worded for a learner** | `AX-09`; R5's vocabulary stays internal |
| the three-page ISO pilot | ⭐ **the user reviews it once**, then the rest run on the gates | step 10.4, and `AX-11`'s reading |

## ⚠️ What is NOT in this epic, and where it is instead

- ⛔ **The spec amendment is LANDED, not a task.** It went in with `W389`'s second stage,
  at §1's table note, C5, R5, §7's new subsection, §7's two-gates scoping, §11.0, §11.2 #14
  and §12. ⚠️ **A row that re-proposes it is re-deriving a settled thing.**
- ⛔ **The runner's per-corpus warm cache is `W390`, a board row already in
  flight — cite it, never re-derive it.** Every ISO page leans on jPOS, so an exercise
  faithful to the page needs a third-party artifact resolved under `--network none`; that
  is `W390`'s, and this epic depends on its outcome rather than restating it.
- ⛔ **Nothing here re-opens the derivation gates of [`E08`](E08-java-exercises.md).** A
  `bundled` exercise keeps its mechanism and its `authoritative` label unchanged.

---

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E14-authored-exercises.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
