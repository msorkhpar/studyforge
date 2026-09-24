# E02 — Content pipeline

From raw material to the one document every consumer reads. This epic owns the
**archive** — the verbatim record of what a source said — and the **unit
document** generated from it.

**Shared context for this epic.** The archive is the project's memory. Pages,
narration, contents and exercises are all regenerable from it, so it must be
trustworthy in a way generated output need not: it is versioned, digest-covered,
and gated against personal data on the way in. CodeSignal learned this the
expensive way — its archive was Markdown with a hand-maintained
render/parse pair that was **lossy by construction** (bold vanished, images were
dropped, fences came back mislabelled), and it would have had to grow bold,
images and video and then be *proved* lossless again. Blocks are simply stored
now: one writer, one reader, no encode/decode pair to keep in step.

**The rule that governs SF-06 and SF-08 together:** the gate **refuses**, it
never rewrites. A match at the archive boundary means something upstream
failed, and silently cleaning it would corrupt the record of what the source
actually said *and* break its own digest.

**Rulings that bite here:** R6 (fail loud), R7 (personal data), R9 (versions),
R10 (reproducible), R11 (packages), R12 (tests).

---

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E02-content-pipeline.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
