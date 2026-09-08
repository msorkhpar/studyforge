# v2 — future backlog

Not planned in detail, on purpose. Each item gets its own design pass when its
time comes, sized against how far both projects have actually moved by then.
Estimating them now would be false precision — v1's own shape has already
changed several times under new information, and v2's will too.

**The one thing v2 must not be:** a dumping ground that justifies cutting
corners in v1. Nothing here excuses a v1 task from meeting its acceptance.

---

## Convergence with CodeSignal

CodeSignal continues to advance during v1 and is deliberately untouched by it
(spec §10). Convergence is a v2 project with its own planning.

**V2-01 — Absorb what CodeSignal advanced.** Review what changed in its study
layer during v1, decide what belongs in the framework, and bring it across.
Requires its own review pass: not everything CodeSignal builds is generic, and
the split in spec §3 is the test.

**V2-02 — CodeSignal ingestion adapter.** Its capture pipeline writing the same
archive every other adapter writes (R2). This is the task that proves the
contracts hold for a source nothing like the Java one — a live site, an
authenticated session, hidden graders, three variants per concept.

**V2-03 — Migrate CodeSignal onto the framework, delete its copy.** Its
byte-for-byte page tests are the strongest regression harness available
anywhere in this project; they are what will prove the extraction preserved
behaviour rather than merely appearing to. The `tree` placement profile (SF-03)
and the declared archive root exist precisely so this migration is not also a
relocation.

**V2-04 — Drift tooling, only if divergence starts to cost.** Nothing has
diverged yet. Building this before it hurts is speculation.

## Proving the generalisation

Both repositories are now cloned as siblings in the workspace and were counted
on 2026-09-08. The descriptions below are measured, not assumed — and both
differed from what was first written (spec §1, C1-C5).

**V2-05 — SPARQL adapter.** 19 flat lessons, **one** container level. Proves
the shallow path. Note what it is *not*: it is **runnable** (Docker with Fuseki
and Jupyter) and **every one of its 19 lessons ends in an exercise** — ungraded,
since nothing checks them. So it exercises the `ungraded` state (C5), not the
zero state. It also ships two Jupyter notebooks and two `.ttl` datasets, which
are the first real test of the **attachment** class (C4) — material a reader
needs that is neither prose nor inline media. Its fences use 8 languages plus
157 bare ones.

**V2-06 — ISO-8583 adapter.** **One** container level, three groups
(fundamentals 16, server 11, client 11 = 38 units), **encoded in filename
prefixes rather than directories** (C1). No build file; `TestCases.md` is prose
scenarios. Two things make it the harder adapter and the better test: it
carries the same material twice, per-unit *and* as whole-series aggregates
(C2), so a naive glob double-ingests; and **18 of its files contain raw HTML**,
which SF-07 must already handle (C3) or the ingest stops dead.

**V2-07 — Ragged-depth hierarchies.** Only if a real source demands what spec
§4's YAGNI currently refuses. The cost is high — every flat contract downstream
becomes a tree walk — so the bar is a source that genuinely cannot be
normalised by its adapter, not a source where normalising is merely
inconvenient.

## Features the framework has room for

**V2-08 — Interview Q&A as an interactive mode.** Every one of the Java
corpus's 166 lessons carries a uniform `Interview Q&A Section`; it ingests as
ordinary blocks in v1. Turning it into a quiz or flashcard surface needs **no
framework change** — which is the point of having ingested it as structure
rather than prose.

**V2-09 — Cross-corpus dedupe and concept equivalence.** Reuse CodeSignal's
existing engine so material already covered in one corpus is marked in another.
Directly useful the moment two corpora exist: the Java repo's 45 modules
overlap heavily with CodeSignal's Java paths — *Functional Programming*,
*Concurrency*, *Design Patterns*, *TDD*, *Clean Code* — and the engine that
found 105 echoes across 285 courses could say which enrolled paths are already
covered by hand-built material.

**V2-10 — Multi-variant merged units.** One concept's Java, Kotlin and Python
treatments rendered as one page. The section-key vocabulary (SF-09) and the
variant axis (SF-02) were designed to allow this; nothing in v1 exercises it.

**V2-11 — Search across corpora.**

**V2-12 — Progress sync across machines**, building on SK-06's export/import.

**V2-13 — Exercise generation for sources with no shipped grader.** ⛔ This
reopens R5's hard question and must not be attempted casually. E08 works
because the graders are real and the gates are mechanical; without a grader
there is nothing to verify against, and the honest v1 answer — zero exercises —
remains the honest answer until somebody has a genuinely better idea than
"generate an assertion and hope".
