# REL-09 — handoff

**Kind:** task handoff — REL-09

## Status

**partial.** Task [`REL-09`](../E15-release-ready.md), branch
`docs/REL-09-process-ids-leave-the-product-prose`, cut at `f3bfc486`. Office `dev1`, worktree
`studyforge-wt/dev1`. Every commit is `dev1 <dev1@example.invalid>`, passed with `git -c`. Nothing
was pushed, merged or deleted.

⛔ **The prose half is done and the first Acceptance clause is NOT met.** No comment, docstring or
shipped prose file under `src/` or `tests/` still cites a non-alias id, except four docstrings the
twin check pins (see *Findings*, `REL-09/2`). The population command still prints non-alias ids.
Every one of them sits in code (a string literal), fixture data, the generated capability index or
one of those four twin docstrings. The task forbids changing any of these, so the clause is
reported here and not rewritten (see *Findings*).

## What landed

Eight commits, one per package, each changing prose only:

| commit | package |
|---|---|
| `1deeb3c0` | `src/studyforge/skills/`, including the skill documents |
| `7d0afbf9` | `tests/studyforge/skills/`, `tests/studyforge/render/` |
| `a393077d` | the rest of `tests/studyforge/` |
| `4cad7538` | `tests/docker/`, `tests/visual/` |
| `76c9ae4a` | `src/studyforge/` outside `skills/`, including the `.css`/`.js` asset comments |
| `4f9d2730` | `tests/gate_coverage/`, `tests/harness/` |
| `4eb78193` | the top-level `tests/test_*.py` and the prose of [`tests/fixtures/README.md`](../../../tests/fixtures/README.md) |
| `5a0ddd09` | `tests/floor/`, `tests/fixture_checks/`, `tests/emission/`, `tests/authoring/`, the top-level test helpers |

How each id was handled:

- **The reason was already in the sentence:** the citation was dropped.
- **The id was the whole point** ("see Wnnn", "Ruling N requires"): the one sentence that matters
  was read from the archive and written in. For example, "a sweep states its denominator", "watch
  it fail without the mechanism", or "a declared list is a closed claim".
- **A task label naming who built something:** replaced by the component's name ("the page
  renderer", "the manifest reader"), or dropped where it was pure provenance. This includes the
  "Skeleton at FND-01. Filled by …" lines.
- **Example ids in usage docstrings:** replaced by placeholder shapes the grep does not read.
- **Aliased ids:** left alone. The decisions file resolves them.

## The readings

Taken at the tip of this branch, in `studyforge-wt/dev1`, on the host. The population is REL-01's
header command with the roots cut to `src tests`. It is compared with `LC_ALL=C comm` against the
backticked ids on the Aliases lines of [`docs/decisions.md`](../../decisions.md). The figures are
this row's subject.

| | distinct ids printed | of which on no Aliases line |
|---|---|---|
| before, at `f3bfc486` | 719 | 336 |
| after, at this branch's tip | 508 | 125 |

Non-alias occurrences by the span they sit in, classified by tokenizing each module:

| span | before | after |
|---|---|---|
| comment | 620 | 0 |
| docstring | 719 | 4 (the twin docstrings, `REL-09/2`) |
| non-Python file | 232 | 196 (generated index 192, fixture data 4) |
| string literal (code) | 147 | 147 (not touched, by the task's rule) |

Prose occurrences before, per package. Each is now 0, except `tests/gate_coverage` + `tests/harness`,
which has the 4 twin docstrings left:

| package | before |
|---|---|
| `src/studyforge/skills/` (with the skill documents) | 118 |
| `src/studyforge/` others (with asset comments) | 193 |
| `tests/studyforge/skills/` + `render/` | 186 |
| `tests/studyforge/` others | 232 |
| `tests/floor/` + fixture_checks + emission + authoring + helpers | 181 |
| `tests/docker/` + `tests/visual/` | 169 |
| `tests/gate_coverage/` + `tests/harness/` | 117 |
| top-level `tests/test_*.py` + [`tests/fixtures/README.md`](../../../tests/fixtures/README.md) | 179 |

## The syntax-tree comparator

A scratch tool, not committed. For every `.py` file that differs from `f3bfc486`, it parses the
base blob and the working file and removes the docstring from each module, class and function body
(the first string statement). It then compares `ast.dump(..., include_attributes=False)` of the
two. Comments never reach the tree. It exits 1 if any module differs or fails to parse.

- **At the tip:** every touched module is SAME, and the command exits 0. It ran once per package
  before that package's commit, and once more over the whole diff.
- **The plant:** in `src/studyforge/version.py`, `declared in accepted` became
  `declared not in accepted`. The diff was printed before the planted run was read. The planted run
  exited 1, naming exactly that module as DIFFERENT. The file was restored from a copy taken before
  the plant, and the whole-diff run then exited 0 again.

## Gates

Each gate was run bare from `studyforge-wt/dev1` at `5a0ddd09`, the last prose commit, with its output
sent to a scratch file and `$?` read on the next line. The only commits after it add this file,
and `python3 -m tools.quality` and `python3 -m tests.floor` were re-run at that later commit, both GREEN, exit 0.

⚠️ **The suite re-run after `5a0ddd09` is RED, and the cause is the environment.** At `0b9950d0`
it exited 1: every failure and error is under `tools/tests/`, which this diff does not touch, and
the output carries `Errno 122` throughout. Three earlier attempts were killed outright with
`OSError: [Errno 122] Disk quota exceeded`. `/tmp` is a tmpfs with a per-user quota, shared with
the other offices' concurrent runs and their `pytest-of-*` base directories. Nothing outside this
office's scratch was deleted to make room. The `5a0ddd09` reading stands for the tree, because
the only difference is one markdown handoff.

| gate | environment | reading |
|---|---|---|
| `./docker/dev/check ruff check .` | pinned image | GREEN, exit 0 |
| `./docker/dev/check ruff format --check .` | pinned image | GREEN, exit 0 |
| `python3 -m tools.quality` | host | GREEN, exit 0 |
| `python3 -m tests.floor` | host | GREEN, exit 0 |
| `python3 -m pytest -n auto -q` | host | GREEN, exit 0 |

## Decisions

- ⭐ **"Docstring" means the first string statement of a module, class or function.** That is
  what the comparator strips. Any other string is code, even a bare one or an assertion message.
  The task rule is that code does not change, so none of those was edited.
- ⭐ **Prose in non-Python files under the roots was treated as in scope**: the skill
  documents, CSS/JS comments and [`tests/fixtures/README.md`](../../../tests/fixtures/README.md). The Acceptance command reads them,
  and they are prose. Fixture DATA (the JSON records and the golden pages) was not touched,
  because a golden and an audio digest depend on it.
- ⭐ **The work was split into eight subteams by package over disjoint file sets**, as the epic
  plans. Each subteam ran the comparator on its own files, and this office re-ran it before each
  commit.
- ⭐ **Aliased ids were left in place.** REL-01's Acceptance admits them, and rewriting them
  would widen the diff without removing any dependence on the archive.

## Surprises

- ⚠️ **Some `tests/harness/` docstrings must stay byte-identical to their `tools/` originals.**
  `tests/test_process_twins.py` compares the copies whole, docstrings included. The docstrings of
  twinned functions can only change together with `tools/`, which this task does not own.
  `tests/test_floor_twins.py` compares with docstrings stripped, so it did not constrain the
  floor copies.
- ⚠️ **One sentence was false as well as citing an id.** In `tests/test_authoring_reference.py`,
  "a worktree carries no sibling component (Ruling 159)" contradicts [`CLAUDE.md`](../../../CLAUDE.md). It now names
  the container mount as the reason a sibling can be absent.

## Findings

| id | marker | where | what |
|---|---|---|---|
| `REL-09/1` | `[structural]` | `src/studyforge/skills/exercises/aspects.py`, `…/exercises/corpus.py`, `src/studyforge/validate/ledger.py` | ⛔ **User-facing refusal messages cite `W453` and `W456`** inside f-strings. That is product prose in code, which this task may not change. It needs either a code row rewording the messages, or aliases for `W453`/`W456` in [`docs/decisions.md`](../../decisions.md) |
| `REL-09/2` | `[local]` | `tests/harness/skipped.py`, `tests/harness/workspace.py` | Four docstrings (`W158`, `Ruling 328`, `Ruling 54`, `Ruling 31`) are twins of `tools/` originals and pinned byte for byte. They go away when REL-10 removes `tools/` (the twin check goes with it), or they can be edited together with the originals |
| `REL-09/3` | `[structural]` | [`capability-index.md`](../../../src/studyforge/skills/delivery/capability-index.md) | Most of the residue is here: task ids as the generated index's DATA. It is byte-compared with a regeneration, so a hand edit fails a test. It clears only if the population command stops reading this file, or when the index's content changes (REL-06 / REL-11). The owner has to decide which |
| `REL-09/4` | `[structural]` | `tests/studyforge/skills/delivery/`, `tests/floor/test_size.py`, `tests/test_acceptance_clauses.py` | Test DATA uses real-shaped ids (`SF-02`, `INT-19/1`, `W44`, `TC-01` and more) as fixture ids or quoted clauses. A code row could switch them to shapes the grammar does not read. `test_size.py` exists to parse row ids and cannot drop them |
| `REL-09/5` | `[local]` | process tests: `tests/harness/process.py`, `tests/test_rubric_exit_code_forms.py`, `tests/test_round_mint_collision_rule.py`, `tests/docker/*` | Ids in assertion messages and reason strings of tests that leave with the tooling in REL-10. The residue goes with them |
| `REL-09/6` | `[structural]` | [`docs/decisions.md`](../../decisions.md) | `W445`–`W456` and `SF-19b` were cited after REL-01's ref and are on no Aliases line. `W451`/`W452` (the quiz answer key never leaves the server) carry a product decision the file does not yet hold. The prose now states it inline |
| `REL-09/7` | `[local]` | REL-01's population command | The grammar does not read a ruling number with a letter suffix (`Ruling 86a` was found and removed in `tests/gate_coverage/test_coverage.py`). A future one would pass unseen |
| `REL-09/8` | `[local]` | spans the grep cannot read | Some comments still use process vocabulary the grammar does not match ("the CTO measured", "rounds 36"). They were rewritten only where a line was already being edited |

## For dependents

- ⭐ **`REL-10`:** once `tools/` and the process tests leave, `REL-09/2` and `REL-09/5` go with
  them. Re-take the population after the cut. What remains then is `REL-09/1`, `REL-09/3` and
  `REL-09/4`, each of which needs a code or data owner.
- ⭐ **Whoever owns [`docs/decisions.md`](../../decisions.md):** see `REL-09/6`.
- ⭐ **Re-taking this reading:** the population command is REL-01's header command with the roots
  cut to `src tests`. Classify each occurrence by tokenizing the module (comment, docstring,
  string), not by grepping the line.
