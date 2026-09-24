# Board

The milestones, what is open, who has it, and what is next. Nothing else lives here: what a
task *is* is its epic, the milestone order and what each milestone is done when is
[`README.md`](README.md), and the history of how the work was done is on the local branch
`archive/process`.

## Milestones

In the order the work runs, which is not the order the ids sort to.

| Milestone | What works when it lands | State |
|---|---|---|
| **M0** — Foundations | An agent can start work without inventing anything | ✅ closed |
| **M1** — One page renders | A unit page from a fixture opens in a browser | ✅ closed |
| **M2** — A corpus is readable | Any corpus, offline, with contents, navigation and read marks, and the skills that built it | ✅ closed |
| **M3** — It speaks | Narration with highlight sync, and an honest media footprint | ✅ closed |
| **M4** — It is served | An origin, an API, and a record of practice passes | ✅ closed |
| **M6** — The first corpus reads | `ISO-8583` is a narrated, navigable, offline study site | ✅ closed |
| **M8** — It is a framework | `ISO-8583` converted by the skills alone, and the findings written down | ✅ closed |
| **M5** — It runs code | A reader runs a unit's test from the terminal; Run and Submit from the page | ✅ closed |
| **M7** — It has practices | The browser editor and the practice panel | ✅ closed |
| **M10** — Every corpus has practices | Exercises authored for every corpus, each graded on the main ask and every edge case | ✅ closed |
| **M11** — It is release-ready | Every repository cleaned for release, and the next corpus needs only the README and the skills | ⏳ **open** — step 11.5 |
| **M9** — The Java corpus re-validates | `Claude-senior-java-engineer` converted under §12's rules, practices included | not started |

## Open now — M11, step 11.5

| Work | Who has it | State |
|---|---|---|
| `REL-10` — the archive branch, and the main line without the process | Developer 6 | ✅ done |
| `REL-11` — a light board, and epics as high-level design | Developer 3 | ✅ done |
| `REL-13` — the framework's siblings are release-ready | Developer 4 | ✅ done |
| `W463` — every declared runtime set builds an editor (in `code-server-toolchain`) | Developer 7 | ✅ done |
| The first corpus on the installed library | integration agent | ✅ done — regenerated on the release line, both image tags recorded, and serving |
| `REL-14` — `M11`'s close, read from a clean clone | Developer 1 | in progress — the reading; the close waits on `REL-12` |
| `W464` — the execution skill's procedure can be followed as printed | Developer 2 | ✅ done |

## Next

1. `REL-12` — prune merged branches and idle worktrees. Prepared; waits on the user's go-ahead.
2. `REL-14` closes `M11` once `REL-12` has run.
3. **M9** — the Java corpus, converted from the README and the skills alone.

## Waiting on the user

- Whether each repository's `main` advances to its release line, and merged branches and idle worktrees
  are pruned (`REL-12`, and the same in each sibling and the corpus).
- Whether the reading measure should rise now the column is wider. Not blocking.

## Standing for every corpus

Two decisions of the user's that bind every conversion, `M9`'s included:

- **An unruled question blocks its milestone.** A recommendation never becomes the decision by
  silence.
- **A defect a reader sees in a corpus is fixed in the framework or the skills, and the corpus
  is regenerated, never patched.** The test of a fix is the next corpus.

## Older backlog

Work items filed before the release cleanup that are still open are listed, each with its
argument, on `archive/process`:

```sh
git show archive/process:docs/tasks/BOARD.md
```

None of them is scheduled. One is brought onto this board when it is taken.
