# E07 — Java ingestion adapter

The first consumer. Turns `Claude-senior-java-engineer` into a valid corpus.

**Shared context for this epic.** The adapter's **entire** obligation is to
write a valid archive (R2): a manifest, 45 container maps, and 166 archive
documents. Nothing downstream is its concern — it does not render, does not
narrate, does not know a page exists. `studyforge validate` (SF-25) is its
definition of done, which is why SF-25 is a dependency of JS-05: the adapter is
built against a machine-checkable signal rather than anybody's judgement.

**The material.** 10 curriculum sections → 45 modules → **166 lesson READMEs**
(166 sub-READMEs + 45 module READMEs + 1 root = the 212 files on disk, so
nothing is unaccounted for). Lessons are *mostly* uniform: **132 of 166 carry
exactly nine `##` headings** — *Concept Explanation, Code Examples, Common
Pitfalls, Interview Q&A Section* and the rest — and the remainder range from 6
to 13, some with numbered variants (`## 3.2.4. Checked vs. Unchecked
Exceptions`). They ingest as ordinary heading blocks, which still gives SF-15
its jump list and E04 its narration chunking cheaply — but **not for free**:
every consumer of that structure must handle a ragged heading set, not the
canonical nine.

**Why this is wiring, not parser work.** SF-07's strict Markdown reader already
exists and is proven. The adapter reads structure and delegates content.

⛔ **R3 — nothing existing is modified.** No README is moved, renamed or
rewritten. Generated artifacts land beside them (§5). OPS-05 asserts it.

**Measured facts this epic depends on** — established by counting the real
repository, not assumed:

| | |
|---|---|
| Curriculum sections | **10** |
| Lesson READMEs | 166 — **all 166 links resolve; zero broken** |
| Lessons with exactly the canonical nine headings | 132 of 166 (**79%**) |
| Implementation classes | 177 |
| Test classes | 168 |
| **Impl classes with no `<Name>Test.java`** | **14** — nine of them in `08-object-oriented` |
| **Maximum name-paired exercises** | **163**, not 168 |
| **Lessons naming an impl class that exists in their module** | **162 of 166 (97%)** — the attachment signal |
| Modules where lessons ↔ classes are cleanly 1:1 | 87% (39 of 45) |
| Outliers | `08-object-oriented` (3 lessons / 11 classes), `22-locks-semaphores` (2/4), `21-synchronization` (2/3), `01-java-basics` (4/5), `25-fork-join` (5/4), `29-date-time-api` (8/7) |
| Not a lesson container | `00-base` — 0 READMEs, holds a shared test utility |
| Markdown constructs beyond SF-07's vocabulary | 10 files with `---` thematic breaks, 1 with a blockquote |
| Images · video · raw HTML · mermaid | **zero of each** — the material is clean prose, code fences and tables |

---

⚠️ **This epic is SK-02's and SK-07's first output, not their input** (spec §9,
E11). The adapter package, its test tree and its audit command are **scaffolded
by the skills** before any source reading is written here — reversing the
original plan, where these tasks came first and the skills were reverse-
engineered from them at M7. What remains genuinely this epic's own work is the
part that is irreducibly source-specific: reading Java's curriculum, its lessons
and its class pairings.

⭐ **Anything in this epic that a second source would also have to write is a
finding against a skill** (R19), not work to be repeated. Record it; do not
absorb it.

⛔ **PO round 74 — this epic is `M9`, the re-validation** (user direction, 2026-09-12:
*"…and then apply it to java-senior project to revalidate being a framework"*). ⭐ **This
corpus now comes LAST: after `ISO-8583` proves the framework (`M8`) and the execution track
is finished (`M5`, `M7`)** — [`README.md`](README.md) § M9.

---

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E07-java-adapter.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
