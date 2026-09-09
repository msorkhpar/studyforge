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
(C2), so a naive glob double-ingests — now declarable, and refused when
undeclared, via `corpus.json`'s `content` (spec §4); and **26 of its 41 files
carry XML inside fenced code blocks**, so SF-07 must be fence-aware (C3) or the
ingest stops dead. ⚠️ **Recounted 2026-09-09:** an earlier draft said "18 of its
files contain raw HTML". With fences stripped ISO has **none** — the requirement
is fence-awareness, not an HTML vocabulary, and the raw-HTML constituency is
SPARQL (6 of 19).

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

---

## Added by the 2026-09-09 review

These are CodeSignal rulings that were **deliberately not** carried into v1 —
either because they are that source's operational detail, or because the
condition that forced them does not reach this framework yet. They are recorded
so nobody re-derives them at full cost when it does.

**V2-14 — Heavy generated media as release assets.** ⭐ **v1 commits generated
media** (SF-17) and **v1 knows when it must stop** (SF-32, which measures the
footprint and refuses loudly at the ceiling). What v1 deliberately does *not*
build is the way out: packing media out of git and restoring it. This entry is
that mechanism, and it becomes necessary the first time SF-32 refuses.
CodeSignal solved it the hard way when it met GitHub: **11.42 GiB of pack against a 5 GB
soft limit and one video at 150.9 MiB against a hard 100 MiB per-file limit**,
so the push was impossible rather than merely large. Its answer: gitignore the
media, publish it as release assets in 999 MB volumes, and ship a restore script
in both `sh` and PowerShell. ⭐ **The files stayed exactly where they were on
disk and every page still addressed a clip as plain `audio/<clip>.mp3`** — which
is the only reason it was a script rather than a re-render of 1,290 pages, and
it is why spec §5 now rules delivery orthogonal to placement.

Scale is why this is not v1: the Java corpus is ~0.9 GiB of audio and no video,
so neither blocker reproduces and committing is comfortable. The threshold sits
somewhere between that and CodeSignal's 11.7 GiB — which is exactly what SF-32's
default limits encode, and why they are manifest data rather than constants. ⚠️ **A private repository's `releases/download/…` URL is
public-only and 404s with any credential** — private assets come back through
the API by asset id, which is why a restore needs a token route as well as a
`gh` route. That fact costs an afternoon to rediscover.

**V2-15 — Fetching from a live third party.** No v1 task goes near a network:
every source in scope is a local repository. When one is a website, the design
is already measured and must not be re-derived:

- **One policy, shared by every transport.** Not a throttle per call site.
- **Two clocks, honouring the later** — an in-process timestamp and a
  wall-clock file. ⚠️ Not optional: every real caller is a **fresh process**, so
  a per-process throttle resets on every command and paces nothing. ⭐ The file
  can only ever make a process wait *longer* — missing, stale or from a jumped
  clock all cost at most one extra interval and never a request too soon.
- **A halt exit code distinct from skip** — *1 means skip this one, 4 means send
  nothing more.* A rate-limit refusal halts the whole run, not just the worker
  that met it, and resuming is a human decision.
- **The refusal exception is deliberately not a subclass of any error the
  transport already raises**, so it punches through every `except` between the
  socket and `main`. Otherwise a stop becomes a retry with a different guess.
- ⛔ **A rate limit does not have to arrive as a status code.** A WAF answers
  with a challenge page and a **200** of well-formed HTML that passes every
  status and truncation check, so the run reports "did not parse", exits, and
  goes straight on to the next request — at exactly the permitted pace, into a
  wall. The defence is a positive test that the *site* answered. ⛔ **Never a
  scan of the body for words like "rate limit" or "captcha"**: a catalog that
  teaches API rate limiting would refuse its own lessons.
- ⛔ **No identifying contact of any kind**, in a header or anywhere else (R7).
  A third party's documented requirement for one is not permission.

**V2-16 — A whole-catalog navigation rail.** CodeSignal put its entire catalog
on every unit page as one shared generated script assigning a global — ⛔ not
`fetch`ed, which is refused over `file://`, and ⛔ not inlined, because 0.28 MB
across 1,290 pages is 360 MB. Not v1: `studyforge` has a route CodeSignal never
had — the container page (SF-27), giving unit → module → section → index — and
CodeSignal deleted its own per-page drill-down precisely *because* the rail
superseded it. Revisit when a corpus is large enough that the container page is
not enough. ⚠️ The delivery mechanism is the part worth keeping: **a shared
generated script assigning a global is the only way to put the same data on
every page** under R8, and it is written by whichever stage holds the whole
hierarchy — so a page-generation stage must sweep only its own outputs or it
will delete it.
