# Graphify — the project's knowledge index

Enforces **R14**. Every repository in this project carries a built graph, and
agents query it before exploring.

## Why this is a rule and not a nicety

Task context budgets assume an agent can find what it needs without reading the
tree. Without a graph the alternative is every agent grepping the whole
repository to re-derive structure another agent already established — which is
exactly the cost the budgets exist to prevent. It also degrades answers: a grep
finds a name, the graph finds the *relationship*.

CodeSignal already proves the setup works — it carries a built index at
`CodeSignal/graphify-out/` with a `GRAPH_REPORT.md`, an interactive
`graph.html` and a queryable `graph.json`.

## Where the graphs live

| Repository | Purpose |
|---|---|
| `studyforge/graphify-out/` | the framework — packages, contracts, call structure |
| `Claude-senior-java-engineer/graphify-out/` | the material *and* the adapter |
| `CodeSignal/graphify-out/` | already built; the extraction source |

`graphify-out/` is git-ignored except for a `.gitkeep`. The graph is a local
index, not a committed artifact — it is rebuilt, not merged.

## What an agent does

**Before broad exploration, ask the graph.**

```bash
graphify query "which modules read the corpus manifest?"
graphify query "how does a unit document reach the page renderer?" --dfs
graphify path "Address" "PageRenderer"
graphify explain "PlacementProfile"
```

Use it for *where / what calls / how does X reach Y* questions. Read files
directly when you already know the file and want its exact contents — the graph
locates, it does not quote.

**Budget note.** A query answers in a few thousand tokens where the equivalent
exploration costs tens of thousands. A task whose context budget looks tight is
usually a task that should be asking the graph.

## When it is rebuilt

- After a task lands that adds, removes or renames a package or module.
- Before a wave begins, so that wave's agents start from a current index.
- Never mid-task by the agent doing the work — a graph rebuilt against a
  half-finished tree indexes a state nobody will see again.

```bash
graphify .            # full build
graphify . --update   # incremental; only new or changed files
```

## Honesty

The graph reports what it extracted, with an audit trail — `EXTRACTED`,
`INFERRED`, `AMBIGUOUS`. Treat an `INFERRED` edge as a lead, not a fact. If an
answer from the graph contradicts the source, **the source wins** and the graph
is stale — rebuild it and say so.
