# Graphify — the project's knowledge index

Enforces **R14**. A repository in this project's working set carries a built
graph, and agents query it before exploring.

## Why this is a rule and not a nicety

Task context budgets assume an agent can find what it needs without reading the
tree. Without a graph the alternative is every agent grepping the whole
repository to re-derive structure another agent already established — which is
exactly the cost the budgets exist to prevent. It also degrades answers: a grep
finds a name, the graph finds the *relationship*.

⭐ **Measured, not asserted** (FND-02). Against the Java corpus — 610 files,
604,556 words — `explain` and `path` each answered in **under a second** and in
**a few hundred tokens**. Reading the four files those answers name costs
roughly 20,000. That is the ratio R14 is claiming, and it holds for the
*locating* questions. ⚠️ It does not hold uniformly; see **What it answers
badly** below, which is the half worth reading before you trust an answer.

## Where the graphs live

| Repository | What its graph holds | Built |
|---|---|---|
| `studyforge/graphify-out/` | the rulings R1–R20, the contracts, the epics and task IDs, the `src/` and `tools/` call structure | FND-02; **rebuilt at each wave close** |
| `Claude-senior-java-engineer/graphify-out/` | 217 lesson documents, 345 classes, and the lesson→class links between them | FND-02 |
| `CodeSignal/graphify-out/` | the extraction source (R20) | already built |

`graphify-out/` is **git-ignored in every one of them**, and nothing inside it
is ever committed. The graph is a local index, rebuilt rather than merged.

⚠️ **There is no committed `.gitkeep`, and there cannot be one.** An earlier
version of this document said there was. `graphify-out/` excludes the
*directory*, and git cannot re-include a file inside an excluded directory, so
a `.gitkeep` there is ignored too — `git check-ignore` says so in this
repository and in the extraction source, and neither tracks one.

## Ignoring the index in a corpus repository — the R3-safe way

⛔ **Never add `graphify-out/` to a corpus repository's root ignore file.** R3
forbids editing it *however declared*: the repository's root ignore file is one
of the three edits that are never permitted. The ruled mechanism instead:

```bash
mkdir -p <corpus>/graphify-out
printf '*\n' > <corpus>/graphify-out/.gitignore
```

A one-line `*` **inside** the generated directory. It adds a file rather than
editing one, it ignores itself, and it makes the whole index invisible to
`git status`. ⚠️ Because it ignores itself it is never committed — it is
recreated by the build, which is why the recipe lives here and not in the
corpus.

⭐ **Verify it in both directions, always.** A rule that ignores everything
passes the first check and is strictly worse than no rule:

```bash
cd <corpus>
git check-ignore -v graphify-out/graph.json   # expect: the rule, from graphify-out/.gitignore
git check-ignore -q README.md ; echo $?       # expect: 1  (NOT ignored)
git status --porcelain                        # expect: empty
```

`tests/test_knowledge_index.py` runs exactly this against any corpus checked out
beside this repository, and skips when none is.

## What an agent does

**Before broad exploration, ask the graph.** Use it for *where / what is
connected to what / how does X reach Y*. Read files directly when you already
know the file and want its exact contents — the graph locates, it does not
quote.

### The three commands, with real answers

These are FND-02's acceptance, run against the Java corpus and pasted as they
came back.

**1. `explain` — what is this, and what is it wired to?** The best first move
when you have a name and no context.

```
$ graphify explain "Streams API Introduction"
Node: Streams API Introduction
  ID:        16_streams_api_readme_intro
  Source:    16-streams-api/README_4.4.1.md None
  Type:      document
  Community: Parallel Streams
  Degree:    9

Connections (9):
  --> StreamIntro [references] [EXTRACTED]
  --> StreamIntroTest [references] [EXTRACTED]
  <-- Stream Terminal Operations [references] [EXTRACTED]
  <-- Stream Intermediate Operations [references] [EXTRACTED]
  <-- Creating and Using Streams [references] [EXTRACTED]
  <-- Parallel Streams and Performance [references] [EXTRACTED]
  --> Lazy Evaluation [rationale_for] [EXTRACTED]
  --> Short-Circuit Operations [rationale_for] [EXTRACTED]
  --> Stream Pipeline Architecture [rationale_for] [EXTRACTED]
```

One lesson, the implementation class it teaches, its test class, its four
sibling lessons and the three ideas it explains — in nine lines.

**2. `path` — is X connected to Y, and how?** The sharpest of the three, and
the one that answers the question E08 is built on: *does this lesson name the
class it teaches?*

```
$ graphify path "Streams API Introduction" "StreamIntro"
Shortest path (1 hops):
  Streams API Introduction --references [EXTRACTED]--> StreamIntro
```

**3. `query` — a BFS from whatever your words match.** Broad context, at the
cost of precision.

```
$ graphify query "happens-before guarantees and volatile visibility" --budget 900
Traversal: BFS depth=2 | Start: ['Happens-before Relationships and Memory Visibility',
  'volatile', 'VolatileHappensBefore', 'BeforeEach', ...] | 135 nodes found

[!] TRUNCATED: showing 17 of 135 nodes (~900-token budget).

NODE Happens-before Relationships and Memory Visibility [src=18-happens-before/README.md ...]
NODE volatile                                           [src=18-happens-before/README_5.2.2.md ...]
NODE VolatileHappensBefore                              [src=21-synchronization/.../VolatileKeyword.java L113]
NODE .programOrderGuaranteesCorrectSum()                [src=18-happens-before/.../HappensBeforeDefinitionTest.java L24]
NODE VisibilityIssueTest                                [src=19-concurrency-pitfalls/.../VisibilityIssueTest.java L11]
NODE 5.3.3. Visibility Issues and Proper Synchronization Techniques [src=19-concurrency-pitfalls/README_5.3.3.md]
```

Three modules that teach one idea, found together, which no single grep
returns. ⚠️ **The `src=` paths are trimmed here on purpose** — the corpus's Java
package directory carries its owner's account name, and R7 keeps that out of
this repository's files. Trim it whenever you paste graph output into a
document here.

## What it answers badly — read this before trusting an answer

⛔ **A vague query returns noise, and the noise looks like signal.** Asked
*"which implementation class does the Streams API introduction lesson teach?"*,
the graph starts its traversal from every node matching **"class"** and
**"use"** as well — and returns annotation-processing and executor material with
equal confidence. The right answer was in there; so were forty nodes that were
not. **Phrase a query as the distinctive nouns of the thing you want**
(`happens-before volatile visibility`), never as a natural-language sentence
with common words in it. When you already know the name, prefer `explain` or
`path`, which do not guess.

⚠️ **Documents and code are two layers, and they are only joined where somebody
joined them.** graphify extracts code structurally (AST) and prose semantically
(LLM), and the two passes never see each other's files — so on a first build of
this corpus there were **13,583 code↔code edges, 767 doc↔doc edges, and zero
edges between the two.** The 806 lesson→class edges that make the `path` answer
above possible were added deliberately, by matching each lesson's text against
the class names in its own module. **A new corpus's graph will have the same
hole until somebody closes it**; check with the census below before believing a
cross-layer answer.

⛔ **This document and `handoffs/FND-02.md` pointed at each other for that
census and neither one had it** — which is the whole reason `studyforge`'s own
graph went unbridged for a milestone while both documents said to check. The
command is here now, and it is a command rather than a reference:

```bash
python3 -m tools.knowledge census    # prose-to-code edges, and the floor
python3 -m tools.knowledge bridge    # add the ruling->code edges, then re-census
```

⭐ **`census` counts only edges that cross a file boundary**, and that
distinction is the measurement. A docstring pointing at the function it sits
above has one code endpoint and one prose endpoint and is **not a bridge**:
measured on this repository, **495 of 510** such edges never left their own
file, which is how an unbridged graph came to be reported as 7.9% bridged. The
honest number was **15**.

⭐ **`bridge` joins each ruling to the code whose docstring cites it.**
Deterministic, literal, no model: `**Rn — …**` in `docs/specs/` on one side,
`Rn` in a docstring on the other. Measured 2026-09-09 on the graph rebuilt at
`dc4686c`, it took the census from **15 to 222** and made this answer possible
for the first time:

```text
$ graphify path "docs_specs_2026_09_08_studyforge_v1_design_r7" "assert_clean()"
Shortest path (1 hops):
  R7 — No personal data reaches disk or the wire --implemented_by [EXTRACTED]--> assert_clean()
```

⚠️ **The bridge is only as good as the citing.** Code that implements a ruling
without naming it stays unbridged — visibly, as a number — which is a better
failure than a heuristic that guesses.

⚠️ **The graph reports its own damage; read it.** The Java build carries 1,093
dangling-endpoint edges (~4% of extracted edges) — semantic extraction naming
node ids that the deterministic ID rule never produced. They are inert, but
they mean an absent connection is not proof of absence.

⭐ **The source wins.** `EXTRACTED` is a fact from the file. `INFERRED` is a
lead, `AMBIGUOUS` a guess. If an answer contradicts the source, the graph is
stale or wrong — rebuild it, and say so.

## Querying from a worktree, which is where the cost was

⭐ **`explain` and `path` take `--graph <path>` and need no local index at
all.** This is the clause that makes R14 affordable:

```bash
graphify explain "src_studyforge_address_slug_require_slug" --graph <repo>/graphify-out/graph.json
graphify path "docs_specs_2026_09_08_studyforge_v1_design_r7" "assert_clean()" \
        --graph <repo>/graphify-out/graph.json
```

⛔ **Both take a node id, and that is not fussiness — see the ambiguity rule
below.** These two ran, as written, on 2026-09-09.

⚠️ **`query` does not take `--graph`.** It reads `./graphify-out/graph.json` and
nothing else, so it is the one command that needs a build where you are
standing.

⭐ **That maps exactly onto R14's own qualification.** The two commands the
ruling holds for *unconditionally* are the two that need no local build; the
one that needs a local build is `query`, already the weak one. ⛔ **So the index
is built once per repository, not once per worktree** — measured 2026-09-09,
**33 worktrees and 2 with a graph**, because the per-worktree cost was never
payable and an unaffordable rule is one that gets skipped.

## ⛔ Ambiguity: `explain` refuses, `path` does not — and that difference bites

⚠️ **Labels repeat.** `R7 — No personal data reaches disk or the wire` is the
label of *two* nodes — the spec's ruling and a fixture's `VIOLATION.md` — and
`require_slug()` is the label of two more, the function and a handoff naming it
in prose. ⛔ **The two commands do not handle that the same way, and only one of
them is safe.**

⭐ **`explain` refuses, and hands you the ids:**

```text
$ graphify explain "R7 — No personal data reaches disk or the wire" --graph <repo>/…/graph.json
Ambiguous: 'R7 — No personal data reaches disk or the wire' matches 2 nodes in different files.
  docs/specs/2026-09-08-studyforge-v1-design.md
    id: docs_specs_2026_09_08_studyforge_v1_design_r7
  tests/fixtures/invalid/personal-data/VIOLATION.md
    id: tests_fixtures_invalid_personal_data_violation_r7
Retry with the repo-relative path or the full node id.
```

⛔ **`path` resolves it silently, by score, and then answers — from whichever
node won:**

```text
$ graphify path "R7 — No personal data reaches disk or the wire" "assert_clean()" --graph …
warning: source match was ambiguous (top score 62411.2, runner-up 62407.8)
No directed path found between 'R7 — …' and 'assert_clean()'. Re-run with --undirected…
```

⚠️ **Read that second line on its own and it is a fact about the graph.** It is
not: the path exists, and it is one hop. The warning is *above* the answer, a
reader who scrolls to the result never sees it, and the two scores differ by
four parts in sixty thousand — so which node wins is not something anybody can
predict or reproduce across a rebuild.

⭐ **So: give `path` a node id, always.** `explain` is where you get one, and it
is the command that will not let you skip the step.

⛔ **This is the same defect the index tripwire exists to catch, arriving
through the runbook instead of through the graph** — a green light and a silent
answer. The census reported *"bridged, 222 edges"* while the invocation printed
in this very document returned a confident negative.

## ⚠️ A ruling is filed as `rationale`, not as a document

All twenty-one of this project's rulings are nodes, and `graphify` gives them
`file_type: "rationale"` — the same type as a docstring. ⛔ **Any tool that
separates prose from docstrings by node type will silently drop the rulings**,
and one did: FND-07's first census filtered on document types, found no ruling,
and concluded in a handoff that the nodes did not exist.

⭐ **The remedy is structural rather than a longer type list**: ask whether an
edge **crosses a file boundary**, not what its endpoints are called.
`graphify`'s taxonomy is `graphify`'s and will change; whether two nodes come
from the same file will not.

## ⛔ A document may hold a thing, or point at where it is held — never both ways

This document told readers to check the doc↔code census in
`handoffs/FND-02.md`. That handoff told them the census was in this document.
⛔ **Neither one had it**, and `studyforge`'s own graph went unbridged for a
milestone while both documents said to check.

⚠️ **Neither author could have caught it**, because each saw a pointer to a
place they believed held the thing. ⭐ **So: hold it, or point at a holder — a
pointer to a pointer is a command nobody has ever run.**

## Rebuilding

```bash
graphify update <path>            # incremental: re-extract changed CODE, no LLM, no key
graphify update <path> --force    # full code re-extract, after deletions or a refactor
graphify export html              # regenerate graph.html from graph.json
python3 -m tools.knowledge bridge # ⛔ then bridge, or the index answers no cross-layer question
```

⛔ **`graphify update` and `bridge` are one operation with two commands.** An
index that is present and current and **unbridged** is the worst of the three
states this repository has met: every green light is on and *"which ruling does
this code implement?"* returns silence. `tools/quality/` fails the build on it,
against a recorded floor.

`graphify update` is the day-to-day command and it is honest about doing
nothing: on an unchanged tree it prints *"No code-graph topology changes
detected; outputs left untouched"* and leaves `graph.json` **byte-identical**.
On a tree with a new module it reports the update and the node count grows.
Both were verified in FND-02. ⚠️ An incremental update and a full build are not
node-for-node identical — treat the graph as an index, never as a record.

**Documents need the full pipeline**, because their extraction is semantic and
the host agent is the LLM: invoke the `graphify` skill (`/graphify <path>`) and
let it dispatch extraction subagents. There is **no API key** in this project
and none is needed — do not prompt for one.

### When it is rebuilt

- After a task lands that adds, removes or renames a package or module.
- **Before a wave begins**, so that wave's agents start from a current index.
- ⛔ **Never mid-task by the agent doing the work** — a graph rebuilt against a
  half-finished tree indexes a state nobody will see again.

⚠️ **`studyforge`'s own graph is rebuilt at the M0 close, and that rebuild is
part of closing M0.** The graph FND-02 built indexes a `src/` that had existed
for hours; every M0 task changes it. The doc half is already cached, so the
rebuild is cheap — but a graph of an empty tree is worse than no graph, because
an agent will trust it.
