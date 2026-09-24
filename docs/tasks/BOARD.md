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

## Open now — M11, the findings before the close

Every earlier `M11` task is done, and `REL-14`'s reading holds on a clean clone. The user
ruled on 2026-09-24 that every carried finding is fixed before the close.

| Work | Who has it | State |
|---|---|---|
| `W465` — the quiz key stays out of the editor's reach; a second instance runs beside a live one | Developer 1 | in progress |
| `W466` — the execution skill's outputs are guarded, and its remedies point at the corpus | Developer 2 | in progress |
| `W467` — six onboarding, packaging and narration edges a stranger meets | Developer 3 | in progress |
| `W468` — the editor idles light and wears the page's font; three sibling guards | Developer 4 | in progress |
| `W469` — the product's prose without the process | Developer 5 | in progress |
| `W470` — two backlog branches: merge what has value, drop the rest | Developer 6 | in progress |
| The first corpus's fifteen pre-rebuild branches, the same way | integration agent | in progress |

## Next

1. The first corpus regenerates once against the fixes, and `REL-14` is read again.
2. `M11` closes. Merged branches and idle worktrees are kept until the code is pushed (the
   user's ruling); `REL-12` runs then.
3. **M9** — the Java corpus, converted from the README and the skills alone.

## Waiting on the user

- Whether the first corpus's generated onboarding guide stays in `docs/archive/` or returns to
  its root.
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
