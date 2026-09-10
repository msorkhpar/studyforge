# SESSION-2026-09-09 — coordinator handoff

**Status:** partial — M1 step 1.3 in progress, two branches awaiting review
**Written by:** the orchestrating session, for whatever session picks the work up next

⚠️ **Read this first, because it changes what "resume" means.** The CTO, the two
developers and the two Product Owners were **in-process subagents of one
session**. They cannot be restarted or reattached. A new session spawns *new*
agents, and everything they knew is in this repository or is gone. That is not a
defect — it is the reason `handoffs/`, `BOARD.md` and the knowledge graph exist —
but it means the next coordinator's first job is **reading**, not messaging.

---

## Where the work actually is

**Release branch** `release/m0-foundations`, tip `220ea4b`.
Pinned (container, authoritative): **1512 passed, 46 skipped**, ruff clean both
ways, quality floor clean. Unpinned (host, has node): higher — see the three-state
rule below.

**M0 — complete.** FND-01…FND-06 all merged. FND-05b cancelled outright.
**M1 step 1.1 — complete.** SF-01, SF-02, SF-07, SF-08, SF-11, plus SF-33.
**M1 step 1.2 — complete.** SF-03, SF-05, SF-06.
**M1 step 1.3 — in progress.** SF-09 written; SF-25 part-written; SF-23 and SK-01
not started.

### ⛔ Two branches are unmerged and both are ready for review, not for work

| Branch | State | What it needs |
|---|---|---|
| `fix/SF-03-label-seam` | 2 commits, container green | CTO review, then merge |
| `feat/SF-09-unit-document` | 1 commit, rebased by its author onto `220ea4b`, container green | CTO review, then merge |

`git merge-tree` was rehearsed by the author: **they merge cleanly with each other
in either order.** Neither has been reviewed. ⚠️ Merge them **adjacently and run
once with both** — a prior round proved that a seam between two branches is
invisible to each one alone, and that is exactly how the label defect survived.

### Work in flight that was interrupted

**SF-25 (`studyforge validate`)** — ⭐ **committed as WIP at `96dd17e` on
`feat/SF-25-validate`; it is NOT lost.** An earlier revision of this handoff said it
was, and that was wrong — the work was uncommitted in a worktree, and the first act
of this round was to get it onto the branch. The package is written and working: 58
tests passing, both valid fixtures green, all five invalid fixtures reporting
exactly one rule each. ⚠️ Its author found and fixed a real defect while building
it: a document refused by the R7 gate was *also* reported as a missing unit — one
defect wearing two names — closed by recording refused files so a downstream check
reports `Unchecked` rather than absence. **Remaining:** the `report`, `corpus`,
`cli`, `init` and `__main__` test modules, then the handoff.

⛔ **A worktree is not storage.** The agent worktrees live in a session-scoped
scratchpad; the branches live in `.git`. Anything uncommitted dies with the session.
Commit before ending a session, always, even untidy.

⚠️ **And an escalation of finding 1, raised by SF-25's author and worth measuring:**
`validate` forwards `str(error)` from SF-01's exceptions straight into a `Finding`.
If a container map's bad address segment reaches a report through `AddressError`,
then **`validate` is an R7 emission site by inheritance** — which would make the
`require_slug`/`require_ordinal` fix load-bearing for the one command an adapter
author is told to trust. Measure it rather than assume it.

---

## Findings that are routed but not closed

1. ⛔ **`address/slug.py:require_slug` and `address/ordinal.py:require_ordinal`
   format `{value!r}`**, so every address segment, identity field and unit ordinal
   inherits an R7 echo — **7 of 26 emission sites in the tree are that one pair of
   lines seen through their callers.** Single highest-value fix available. Lands
   naturally beside Ruling 10's `describe` extraction, already queued after step 1.3.
2. **A behavioural §1f check** was prototyped, not shipped: poison an absolute path
   into each string parameter of each public callable, fail if the raised message
   reproduces it. Measured **46 echoing callable/parameter pairs before the label
   fix, 45 after** — the author reported that delta honestly rather than dressing it
   up. 19 of the 45 are `where=`/`what=`, which a refusal exists to name; the other
   26 sit in 18 modules across 6 packages.
3. ⚠️ **A fixture defect found by the graph build, not by a test.**
   `tests/fixtures/depth1/.../media/diagram.svg` has `aria-label` "Two nodes and an
   arrow" and the lesson's `alt` says "…joined by one arrow", but the geometry is an
   undecorated `<line>` with **no marker and no arrowhead**. The two accessible names
   also differ in wording. Belongs to FND-04's fixture set; nobody has been told.
4. `docs/tasks/handoffs/SF-05.md` still describes `LABEL_FORBIDDEN` and lists its
   duplication as open finding 6. Both are resolved by the hotfix. A handoff is a
   record and is **not** rewritten — but the board should say so.
5. **`unitdoc.py` is 827 lines against R11's 400** and belongs to **SF-10**, not
   SF-06. Routed with the number; no owner has picked it up.

---

## The rulings a coordinator must enforce, because they are about *routing*

- ⛔ **Nothing merges without a CTO verdict**, and the verdict goes in the merge
  message: `Merge <branch>: <one line> (CTO: APPROVE)`. This session broke that
  twice under critical-path pressure and the CTO's response was the right one: *it
  did not ask for a stricter promise, it made the omission visible in the log
  afterwards.*
- ⛔ **Measure the base and the merge, and report both numbers.** A green merge over
  a red base is a normal result. A red base is an urgent finding **against the
  release branch**, not against the change.
- ⛔ **The container is authoritative because it is pinned, not because it is
  better.** Three states: *pinned green* is the verdict; *unpinned green* is real
  evidence, named in the review, with the image gap filed as a finding; *did not
  run* is not evidence at all. Every skip is named — `pytest -q -rs`.
- ⛔ **A finding is a measurement with an as-of, and it is re-run before it becomes
  a task.** Findings carry `[local]`/`[structural]` and a `Measured` field: the
  command, its output, the date. **Not "I noticed."**
- ⛔ **A claim about another repository is verified in that repository.** A
  CTO-verified ruling was overruled because what got verified was a *fixture's*
  consistency, not the claim about the source the fixture had been built to match.
- ⛔ **Nothing is ever pushed to any remote.** Permanent, by the user's decision.
  R18 is amended accordingly: reproducible across time on one machine, explicitly
  **not** across machines.
- ⭐ **Implementation decisions belong to the PO and the CTO.** Escalate to the user
  only for huge impact or something that could not be undone. When something blocks,
  dispatch everything it does not gate before reporting it.

---

## The knowledge graph — built this session, and the process gap it exposed

`graphify-out/` now holds a graph of this repository: **3,075 nodes, 6,081 edges,
141 labelled communities** (2,072 AST + 1,003 semantic). `graph.html`,
`GRAPH_REPORT.md`, `graph.json`. R7-verified: zero home paths in either artifact.

⚠️ **Three things the next coordinator needs to know about it.**

1. ⛔ **`graphify-out/` is git-ignored, so it cannot travel on a branch.** FND-02
   built the framework's graph inside a disposable worktree and its acceptance was
   satisfied *there*; the graph never reached the working checkout, and `BOARD.md`
   recorded it as done. **That is a record-versus-claim defect in the board itself.**
   The graph must be rebuilt in the checkout that is being worked in, and the M1
   close should carry a tripwire so "the graph is current" fails loudly rather than
   being assumed.
2. ⚠️ **GRAPH HEALTH WARNING: 203 dangling-endpoint edges, 192 collapsed, 1
   self-loop** — the merge seam between the AST and semantic extractors. The graph is
   usable; *absence of a connection is not proof of absence.*
3. ⛔ **Three of five extraction agents wrote absolute `source_file` paths** because
   the extraction spec demands them verbatim. 2,143 were relativised before merging.
   A mismatched base produces ghost duplicate nodes **and** writes a home directory
   into `graph.json`. `handoffs/FND-02.md` decision 4 had already ruled this; two
   agents rediscovered it independently. **Relativise every chunk, together.**

4. ⚠️ **The graph answers two of three question shapes. Measured, not assumed.**

   | Query | Result |
   |---|---|
   | `graphify explain "assert_clean()"` | ⭐ works — sub-second, 27 connections, exact call sites with line numbers |
   | `graphify query "..."` | works, but noisy — confirms FND-02's finding that `query` holds only when phrased as distinctive nouns |
   | `graphify path "R7 — No Personal Data…" "assert_clean()"` | ⛔ **no path, even undirected** |

   ⛔ **The last one is the question this repository most needs answered — "which
   ruling does this code implement?" — and the graph cannot answer it.** Measured:
   **232 doc↔code edges out of 6,081 (3.8%)**. Better than the Java corpus's
   initial *zero* only because handoffs name functions explicitly; it is not a
   deliberate bridge. FND-02 built the bridging pass and applied it **to the corpus
   only** — 806 edges, 162 of 166 lessons — and nobody ran the equivalent here.
   ⭐ **So R14's saving is a property of a graph somebody bridged, and the
   framework's own graph is unbridged.** The bridging recipe is in
   `handoffs/FND-02.md`; it is deterministic (literal symbol occurrence, never an
   LLM) and it is the highest-value single improvement available to the index.

⭐ **And the honest finding about this session's own conduct.** R14 says agents ask
the graph before exploring, and every task's `Context` budget assumes it. This
coordinator did not: it hand-assembled a long briefing for each developer from its
own reading instead. That costs more tokens than a query and inserts the
coordinator's judgement between the spec and the developer. **The two rounds where
a developer corrected an inherited claim — `folder`, and C3's raw-HTML count — are
exactly the cases a graph query would have reached faster.** The next coordinator
should point developers at the graph for structural questions and keep its own
briefs to rulings and constraints: the things that genuinely are not in the code.

---

## If you are restarting: the order that wastes least

1. Read `BOARD.md`, then this file, then `docs/conventions/delivery-flow.md` and
   `review-rubric.md`. Do not re-read the spec end to end — **query the graph**.
2. Spawn a CTO. Give it the rubric and the two unmerged branches. It reviews them
   as the merges they produce, not as diffs.
3. Merge on its verdict, adjacently, measuring base and merge.
4. Spawn the PO. The board is behind: M1 step 1.3 progress, the five findings above,
   and the graph's own tripwire all need placing.
5. Re-dispatch SF-25 from scratch, and SF-23 and SK-01 to close step 1.3.
6. The ISO integration track is parked at `release/studyforge-integration` in the
   consumer repository, one commit, documents only. ⛔ It cannot start building
   until the framework reaches M2, and its PO may not patch `studyforge` or read the
   extraction source.

⭐ **The single most valuable thing in this repository is not the code.** It is the
chain of rulings in `handoffs/CTO-*.md` — why a check is import-aware rather than
narrowed, why a filename is validated by what is permitted, why a gate that must
hold the secret to detect the secret cannot be built. Those cost real rounds to
reach and are not recoverable from the source. The graph now edges the
overrule chain between them. Use it.
