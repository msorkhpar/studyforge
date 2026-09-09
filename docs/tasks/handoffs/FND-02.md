# FND-02 — handoff

**Status:** done

## What landed

- **`Claude-senior-java-engineer/graphify-out/`** — the corpus graph.
  **11,107 nodes, 25,566 edges, 1,007 communities, 38 hyperedges** over 610
  files and 604,556 words. 217 lesson documents, **100% represented**. ~90 MB
  on disk, git-ignored, never committed.
- **`studyforge/graphify-out/`** — the framework graph. **556 nodes, 870
  edges, 76 communities.** Its rulings `R1`–`R20`, its contracts, its epics and
  task IDs are first-class nodes. ⚠️ **Rebuilt at the M0 close** — see
  *Decisions* 2.
- **`docs/conventions/graphify.md`** — rewritten. The three commands with real
  pasted answers, the rebuild runbook, the rebuild point, the R3-safe corpus
  ignore recipe, and — new — a *What it answers badly* section.
- **`tests/test_knowledge_index.py`** — 251 lines, 10 tests. Asserts the ignore
  rule in both directions, that nothing in `graphify-out/` is tracked, that a
  corpus repository beside this one ignores its index the R3-safe way (skips
  when absent), and that the conventions document still carries the runbook,
  the rebuild point and the ignore recipe.

⛔ **Nothing was committed to `Claude-senior-java-engineer`.** Its
`git status --porcelain` is empty, and its root `.gitignore` blob hash is
byte-identical to what it was before this task started (checked, both ends).

## Acceptance, with the commands

**Both graphs build** — node/edge/community counts above; `GRAPH_REPORT.md`,
`graph.html`, `graph.json` and `manifest.json` written in both.

**`graphify-out/` is git-ignored.** In this repository by FND-01's rule, which
FND-02 asserts rather than adds (ruling 3). In the corpus by the ruled R3-safe
mechanism — a one-line `*` **inside** the generated directory:

```
$ git check-ignore -v --no-index graphify-out/graph.json
graphify-out/.gitignore:1:*	graphify-out/graph.json
$ git status --porcelain          # empty
$ git hash-object .gitignore      # unchanged: the root ignore file was never touched
```

Verified in **both directions** — everything under `graphify-out/` ignored,
`README.md` and `graph.json` at the root still trackable.

**The rebuild command works incrementally**, proved both ways:

- unchanged tree → *"No code-graph topology changes detected; outputs left
  untouched"*, and `graph.json` is **byte-identical** (sha256 compared);
- new module added → *"graph.json, graph.html and GRAPH_REPORT.md updated"*,
  node count grows, the new symbol is in the graph. (Probe module added and
  removed inside this worktree; `git status` clean afterwards.)

**Three representative queries** are in `docs/conventions/graphify.md`, pasted
as they came back — one `explain`, one `path`, one `query`, per the epic's
"confirms the query, path and explain commands answer". All three answered in
**under a second**.

## Decisions

1. **`graphify update` is the documented rebuild command, not `graphify
   extract`.** `extract` is the headless full-pipeline entry point and it wants
   an LLM backend; there is no API key in this environment and the skill is
   explicit that none is needed — the **host agent is the LLM** for the
   semantic half. So the runbook documents `graphify update` (code, incremental,
   deterministic, no key) plus "invoke the `/graphify` skill" for documents.
   The test module's command list was corrected to match what was actually run:
   ⛔ a runbook entry nobody has executed fails for the first person who copies
   it.
2. **The `studyforge` graph was built now anyway, and it is still to be rebuilt
   at the M0 close** (ruling 2). Building it now was not wasted: the expensive
   half is the semantic pass over `docs/`, and that is now **cached**, so the
   M0-close rebuild is a code-only re-extract that takes seconds. What churns
   between now and then is `src/`, which is AST — free and instant. The
   conventions document states the M0-close rebuild as part of closing M0, and
   a test asserts that sentence is still there.
3. **Both graphs are undirected**, matching the extraction source
   (`directed: false` in its `graph.json`), so `query` behaves the same way in
   every repository an agent moves between.
4. **`source_file` is repo-relative everywhere, against the extraction spec's
   wording.** The spec tells subagents to write absolute paths; every subagent
   here was told to override that. Two reasons, and both are load-bearing: the
   AST half already emits repo-relative paths, so a mismatched base would have
   produced ghost duplicate nodes on merge; and an absolute path would put a
   home directory into `graph.json` (R7). ⭐ The extraction source's own graph
   has **zero** absolute home paths, which is what confirmed this is the
   established shape rather than my preference. Swept both trees: **no
   absolute home path in any file**.
5. **Community names: hand-written for the largest, derived for the rest.**
   1,007 communities is past the point where naming each by hand is honest
   work rather than the appearance of it. The 14 largest are named by hand; the
   rest are derived from each community's own principal node, preferring the
   file over a method and skipping generic names — 798 distinct names of 1,007.
   Same approach in this repository: 29 by hand of 76.
6. **The 35-document coverage gap was closed rather than reported.** The first
   pass represented 182 of 217 documents (84%); the systematic miss was
   **module-level `README.md` overviews** — the container-level file JS-05 needs
   most. Two targeted passes brought it to **217 of 217**.
7. **The doc↔code gap was closed deterministically, never by an LLM.** See
   *Findings* 1. The class's simple name appears literally in the lesson's own
   text, so the relationship is `EXTRACTED` in graphify's own sense; guessing at
   it would have been strictly worse than reading it.

## Surprises

- ⛔ **The graph could not answer the question the corpus exists for.** On a
  first build, an agent asking *"which class does this lesson teach?"* got
  nothing, because **the document layer and the code layer had zero edges
  between them**. That is not a slip in this run — it is structural: graphify
  extracts code by AST and prose by LLM, and the semantic pass is handed only
  the doc files, so no extractor ever sees a lesson and its class together.
  Measured before the fix: 13,583 code↔code, 767 doc↔doc, **0 doc↔code**.
- ⭐ **Closing it re-verified spec §7's headline measurement exactly.** Matching
  each lesson's text against the class names in its own module reproduces
  **162 of 166 (97.6%)** — the spec says "162 of the 166 lesson READMEs … a 97%
  signal". Independently derived, from a different direction, two days later.
  The four that do not: `02-control-flow/README_1.2.5.md`,
  `03-methods/README_1.3.3.md`, `22-locks-semaphores/README_6.3.1.md`,
  `29-date-time-api/README_7.3.2.md`.
- **A vague query returns confident noise.** Asked as an English sentence
  (*"which implementation class does the Streams API introduction lesson
  teach?"*), the traversal starts from every node matching **"class"** and
  **"use"** and returns unrelated modules with the same confidence as the right
  answer. Asked as distinctive nouns, it is sharp. This is now the *What it
  answers badly* section of the conventions document — R14's premise holds for
  `explain` and `path` unconditionally, and for `query` only if you phrase it
  like an index lookup rather than a question.
- **The context budget (~20k) was optimistic by roughly an order of
  magnitude** — not for reading, but for *doing*. The read list is small; the
  work is a 12-chunk parallel extraction over 217 documents plus a second pass,
  and the same again for this repository. Worth re-pricing if another task is
  scoped as "build a graph".

## Findings

Defects and gaps outside FND-02's scope. **Not fixed, not in the diff.**

1. `[structural]` ✅ **RULED and APPLIED** — R14 now reads *every repository **in this project's working set***, and says a repository enters that set when it is onboarded (CTO round 3). The spec was the authority and it has been edited.

    *Original finding:* ⛔ **`graphify.md`'s reading of R14 is defective — as the CTO ruled, and
   this task carried it rather than fixing it.** R14 says *every* repository in
   this project carries a built graph; `ISO-8583-jPOS-tutorial` and
   `Claude-SPARQL-tutorial` have none and are not going to before v2. R14
   should bind when a repository **enters the working set**. The conventions
   document now says "a repository in this project's working set", which is the
   narrowest edit that stops the document asserting something false — ⚠️ **but
   R14's own text in the spec is unchanged and still says "every"**, and that
   is the authority. It needs the PO or the CTO, not me.
2. `[structural]` ✅ **SCHEDULED — already in the task, checked rather than assumed.** `SK-07` item 9 generates the graph, bridges the doc↔code layers and writes the R3-safe `graphify-out/.gitignore`. ⭐ It also carries this task's sharpest measurement — an unbridged graph has **0 doc↔code edges**, so *the budget saving R14 promises is a property of a graph somebody bridged, not of the tool*. Nothing further owed.

    *Original finding:* **`SK-07` does not generate a graph, which is a hole in that skill under
   R19** (carried from the CTO's ruling, unexamined by me). Everything a
   working corpus needs is supposed to be produced by a skill; a corpus
   onboarded by `SK-07` today arrives with no index, and R14 then binds on a
   repository nothing built one for. The R3-safe recipe this task wrote down is
   what `SK-07` would need to emit.
3. `[structural]` ✅ **RULED — E07 unblocked** (CTO round 3, carried into `SF-08`). The gate's question is not *is this string identifying?* but *did this build put it there?* ⛔ And `SF-08` never grows a username pattern, because matching one requires **holding** the username — the exact datum R7 forbids the framework to hold.

    *Original finding:* ⛔ **The Java corpus's every source file carries an owner-identifying
   segment in its package path, and E07 will feed those strings to `SF-08`.**
   The package directory is `com/github/<account>/…`, so the account name is in
   345 file paths, in every `import`, and in code blocks on every generated
   page. Three things follow, and none is mine to decide: (a) if `SF-08` ever
   grows a username pattern it will **refuse the entire corpus** — SF-08 already
   warns that a false positive is a failure of the same class as a leak; (b) the
   archive's `origin` fields and the graph's `source_file` values carry it
   legitimately, as the material's own content; (c) any studyforge document
   quoting a Java path carries it too — this task trimmed those paths out of
   `graphify.md` by hand and said so in the document. **This needs a ruling
   before E07 starts**, because "personal data that is also the material" is
   not a case R7 currently distinguishes.
4. `[structural]` ◐ **ACCEPTED, with the cost named.** The dangling edges are graphify's, not ours, and the conventions document already carries the consequence an agent needs: **an absent connection is not proof of absence.** ⛔ Revisit only if a task is ever allowed to conclude something from a *missing* edge.

    *Original finding:* **The graph carries 1,093 dangling-endpoint edges (~4% of extracted
   edges).** Semantic extraction emits edges naming node ids that the
   deterministic ID rule never produced — subagents inventing ids like
   `concept_lazy_evaluation` instead of the `{stem}_{entity}` form. Inert, but
   it means an absent connection is not proof of absence, which the conventions
   document now says. This repository's graph has the same defect at 41 edges.
5. `[structural]` ◐ **ACCEPTED.** A graph is an index, not a record — it is git-ignored and never an artifact, so R10 does not reach it. Recorded so nobody diffs two graphs and concludes the tree changed.

    *Original finding:* **An incremental update and a full build are not node-for-node identical.**
   This repository's graph was 535 nodes after a full build and 556 after an
   add/remove probe plus a forced update, on the same tree. Both are usable
   indexes; neither is a record. Worth knowing before anyone diffs two graphs
   and concludes something changed.
6. `[local]` ✅ **SCHEDULED** — `FND-06` carries the three-line consolidation into `tests/support.py`; it is the next task whose scope legitimately spans both call sites (CTO round 4).

    *Original finding:* **`is_ignored()` is now duplicated** between `tests/test_repository.py`
   (FND-01's, which this task was told not to touch) and
   `tests/test_knowledge_index.py`. ⚠️ `tests/support.py`'s own docstring rules
   that a block repeated between test files is extracted and imported — so this
   is a real violation of a stated rule, created deliberately because the
   alternative was editing a file outside my task. **The extraction belongs to
   whoever owns both files next**; it is three lines and it should move to
   `tests/support.py`.
7. `[local]` ◐ **ACCEPTED.** The 33 are FND-04's `.json` fixtures; graphify classifies `.json` as code and finds no symbols. Cosmetic, and named here so the warning is not mistaken for a defect.

    *Original finding:* **33 files in this repository produce zero graph nodes**, all of them
   FND-04's fixture `.json` documents: graphify classifies `.json` as code and
   its AST pass finds no symbols. Harmless — they are data, not code — but the
   warning prints on every build and will be mistaken for a defect.
8. `[local]` ◐ **ACCEPTED.** Ignored and local, so it costs nothing in git; documented so a first build is not a surprise.

    *Original finding:* **`graphify-out/` is ~90 MB for the Java corpus.** Ignored and local, so it
   costs nothing in git, but a person cloning and building should know it is
   not a small artifact.

## For dependents

**Ask the graph before exploring, and read *What it answers badly* first** —
`docs/conventions/graphify.md`. The short version:

| You want | Use | It is |
|---|---|---|
| what is this, what is it wired to | `graphify explain "<label>"` | sharp, sub-second, a few hundred tokens |
| is X connected to Y, and how | `graphify path "<A>" "<B>"` | the sharpest; answers in hops with a confidence tag |
| everything near a topic | `graphify query "<distinctive nouns>"` | broad; **noisy if phrased as a sentence** |

⭐ **E07 / E08 — the lesson→class link is in the graph now, and it is the one
you were going to re-derive.** `graphify path "<lesson label>" "<ClassName>"`
returns a one-hop `references [EXTRACTED]` edge for **162 of the 166 lesson
READMEs**, and `graphify explain "<lesson label>"` lists a lesson's
implementation class, its test class and its sibling lessons in nine lines.
⚠️ The four exceptions are named in *Surprises* — they are your unmatched-pair
cases, already enumerated, and `00-base` is the one module with no bridged
lesson at all, which is exactly what spec §7 predicted ("it is not a
container").

⚠️ **Do not trust a cross-layer answer in a graph you did not check.** The
doc↔code edges exist because this task added them; a graph built for a new
corpus by running graphify alone will have **zero**. The census command is in
the conventions document — run it before believing a cross-layer answer.

**Rebuilding, for whoever closes M0:** `graphify update <path>` for code (no
key, seconds, byte-identical on an unchanged tree); the `/graphify` skill for
documents. ⛔ **Never mid-task** — rebuild between waves. This repository's
graph indexes a `src/` that is hours old and every M0 task changes it; the
M0-close rebuild is cheap because the document extraction is cached, and it is
part of closing M0, not a follow-up.

**Onboarding a new corpus repository** — the R3-safe ignore, before you build:

```bash
mkdir -p <corpus>/graphify-out && printf '*\n' > <corpus>/graphify-out/.gitignore
cd <corpus> && git check-ignore -v graphify-out/graph.json && git status --porcelain
```

⛔ Never add `graphify-out/` to the corpus's root ignore file. That file is one
of R3's three never-permitted edits, *however declared*.
