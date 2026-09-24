# REL-07 — handoff

**Kind:** task handoff — REL-07

## Status

**done, self-certified against the epic.** Task `REL-07`, defined in
[`E15` § REL-07](../E15-release-ready.md#rel-07-the-readme-is-an-authors-whole-reading-list).
⭐ **An EPIC TASK, so it has no row file and nothing was minted.** Branch
`docs/REL-07-the-readme-is-the-whole-reading-list`, cut at the release tip `f3bfc486`. Office
`dev2`. Milestone **M11**, step **11.4**.

⭐ **The one sentence:** [`README.md`](../../../README.md) is now a stranger's reading list — what
the framework is, how to install it as a wheel, a first run on a shipped example, the skills in
order each with its step, the authoring reference, and how each image is built locally by tag — and
`tests/test_readme.py` fails the suite the moment it links out of the main line, fences a verb or
flag the command does not offer, or leaves a shipped skill unplaced.

⭐ **Author line declared:** every commit on this branch is `dev2 <dev2@example.invalid>`, passed
with `git -c`. ⛔ Nothing was written to any git config, no remote was added, nothing was pushed or
merged. The user's `:8770` serve, containers and the ISO checkouts were not touched; the one image
this task created is the pinned dev image `docker/dev/check` rebuilt because [`README.md`](../../../README.md) is one of
its hashed inputs.

## ⛔ The user ruling this task carries: [`ONBOARDING.md`](../../../ONBOARDING.md) leaves the main line

⭐ **User ruling, 2026-09-23 (`W438/2`)** overrides the epic's *"The tracked [`ONBOARDING.md`](../../../ONBOARDING.md) is NOT
this task's"*: [`ONBOARDING.md`](../../../ONBOARDING.md) moves to the archive branch. ⛔ **`REL-10`
moves it, not this task**, and this task did not touch it. What this task did instead: the README
neither links nor relies on it, and [`ONBOARDING.md`](../../../ONBOARDING.md) is in `tests/test_readme.py`'s
`LEAVES_THE_MAIN_LINE`, so a link to it fails the suite.

## Gates

⛔ Each gate run bare from `studyforge-wt/dev2` at the tip carrying this handoff, output to a scratch
file and `$?` read on the next line — never through a pipe. ⚠️ A first floor run over this handoff
was RED on bare citations of tracked documents (Ruling 285(b)); written as pointers, then every gate
re-run: the lint, format, floor and quality gates GREEN at the tip.

| gate | environment | reading |
|---|---|---|
| `./docker/dev/check ruff check .` | pinned image | GREEN, exit 0 |
| `./docker/dev/check ruff format --check .` | pinned image | GREEN, exit 0 |
| `python3 -m tools.quality` | host | GREEN, exit 0 |
| `python3 -m tests.floor` | host | GREEN, exit 0 |
| `python3 -m pytest -n auto -q` | host | GREEN, exit 0 at `d8632412` (the README and the test). ⚠️ At the handoff tip, RED on `Errno 122` (disk quota), three runs: the shared `/tmp` is filled by concurrent offices, and the failures sit in the modules that write temp files, not in this diff. The commits after `d8632412` touch this handoff only |

## ⛔ The acceptance, read mechanically

⭐ **The instrument is `tests/test_readme.py`**, in the product suite (standard library,
`tests.support` and `tests.authoring.support`; nothing from `tools/`, so it survives `REL-10`).
Its four readings at `d8632412`, all GREEN:

- **every link resolves, anchors included, and none leaves the repository or reaches what leaves
  the main line** — `docs/tasks/`, `docs/conventions/`, `tools/`, [`docs/capability-index.md`](../../capability-index.md),
  [`ONBOARDING.md`](../../../ONBOARDING.md);
- **every fenced `studyforge` line names a verb `python3 -m studyforge.cli --help` lists**, and
  every flag on it appears in that verb's own `--help` (both asked of a real interpreter);
  every fenced `python3 -m studyforge…` form names a module that runs (a package only with a
  `__main__`);
- **every shipped skill is placed at a step**: the population is walked from
  `src/studyforge/skills/*/SKILL.md`, each must be named in exactly one row of the skills table
  with a non-empty step cell, and that row must link the skill's own document;
- the README links every page of [`docs/authoring/`](../../authoring/README.md).

⭐ Each reading has a standing negative beside it (a planted link, anchor, verb, flag, module and
missing row, in memory), so the instrument is shown failing inside the suite, not only once here.

⭐ **The plant, on the real file**, restored from a working-tree copy with `md5sum -c` (`W143`).
Three violations planted in [`README.md`](../../../README.md): a link to [`docs/tasks/BOARD.md`](../BOARD.md), a fenced
`studyforge publish site`, and the `personalarchive` row deleted. `git diff README.md` was printed
BEFORE the run was read. `python3 -m pytest tests/test_readme.py -q`: RED, exit 1 — the three
acceptance tests failed, each naming its plant (the board link, *"which leaves the
main line"*; *"`studyforge --help` offers no verb 'publish'"*; *"the shipped skill
`personalarchive` is placed at no step"*), and the two in-memory negatives that build on the live
text moved with them. Restored: `README.md: OK`, `MD5_EXIT=0`, porcelain clean, the module GREEN,
exit 0.

## ⭐ The stranger's walk-through

⭐ **Taken literally, from the README alone**, in a scratch directory `REL-07` in the session
scratchpad, from a `git clone --branch` of this branch at `d8632412`, host Python 3.14, a fresh
venv, `PYTHONPATH` unset:

| README step | result |
|---|---|
| clone, `python3 -m venv .venv`, activate | exit 0 |
| `python3 -m pip wheel ./studyforge --no-deps -w wheels` | exit 0 (fetched `setuptools` for the isolated build, as the README says) |
| `python3 -m pip install --no-index wheels/studyforge-*.whl` | exit 0; `import studyforge` resolves inside the venv |
| `studyforge --help` | exit 0, lists the six verbs |
| `python3 -m studyforge.skills.onboarding.verify` | exit 0, prints the installed version |
| `git -C studyforge rev-parse HEAD` | exit 0 |
| `studyforge validate studyforge/tests/fixtures/depth1` | exit 0, three unchecked claims, as the README says |
| `studyforge plan …`, `mkdir site`, `studyforge build … --out site` | each exit 0; the clone's `git status` stays clean |
| `studyforge serve … --site site` | printed `http://127.0.0.1:8765/`; `GET /` answered 200; stopped by the walk's own timeout |
| `python3 -m studyforge.skills.documents` and `… reconnaissance` | exit 0; lists the eight skills, prints the document |

⚠️ **Where it assumes knowledge the README does not give** (each is a finding below, not a README
defect this task can close):

1. `git clone <this repository>` has no URL, because nothing is pushed anywhere. A stranger must be
   handed the repository; the README cannot say from where.
2. The two components the images come from, `narrate-service` and `code-server-toolchain`, are
   named but cannot be obtained from anything the README or the skills say — and the skills that
   use them still describe them as siblings pinned by `workspace.json` (`REL-07/1`).
3. Past the first run, the skills' fenced steps are `python3 -c` calls into the library's API
   (`draft`, `commit` as free variables), so step 2 onwards assumes a reader who can hold Python
   state across calls. That is the skills' shape, stated here so `REL-14` reads it deliberately.

## What landed

- **[`README.md`](../../../README.md)**, rewritten. Outline: what it is (and that a prose corpus is
  finished at the reading floor); *Install* — Python 3.14+, git, Docker only for narration and
  practices, the wheel built and installed, the check, and the commit onboarding needs; *A first
  run* on the flat shipped example (`validate`, `plan`, `build`, `serve`); *the skills, in order*
  — the locator command that prints each skill from the installed package, and a table placing
  every shipped skill at a step (0 optional `delivery`; 1 `reconnaissance`; 2 `onboarding`;
  3 `adapter`; 4 `execution`, runnable material only; 5 `exercises`; 6 `buildserve`;
  7 `personalarchive`), each with what it does and when it is done; *the authoring reference*,
  every page linked; *Images, built locally by tag* — the site runs in no container, narration and
  practices come from their components built from their own checkouts, and the framework's own
  build environment; *the design* — the spec and the decisions file. It names no milestone, task,
  row, board, convention or process id.
- **`tests/test_readme.py`** — the instrument above; `link_faults`, `command_faults`,
  `module_faults` and `skill_faults` each return the violations as sentences.

## Decisions

- ⭐ **Verbs are read off `--help`, not the dispatcher's table.** The acceptance says *a verb the
  installed command offers*, and `--help` is the offer a reader sees. The authoring pages keep
  their table-derived check in `tests/test_authoring_reference.py`; the README is deliberately not
  added to `commanded_pages()` there, because that population also runs the `python3 -m` modules
  through a `__main__` rule that refuses `studyforge.skills.documents` (`REL-05/2`), which the README
  must give.
- ⭐ **The spec and [`docs/decisions.md`](../../decisions.md) are linked.** Both stay on the main line
  (`REL-10`'s list) and `REL-14`'s acceptance names both as reachable; neither is on the
  forbidden list.
- ⭐ **`delivery` is step 0, optional**: it plans a conversion rather than producing one, and a
  person converting their own notes need not run it. The step cell must be non-empty, so it is
  placed rather than footnoted.
- ⭐ **Skill links go to each skill's document in the tree, and the README names the locator command beside
  them** (`REL-04/2`'s suggestion), so the reader with only the installed library is not
  stranded.
- ⭐ **The components are named, never linked**: a link out of this repository cannot resolve, and
  the pointer floor refuses one.
- ⭐ **`docker/dev/check` is named as the framework's build environment**, in one sentence, since
  it is the only image this repository builds; if `REL-10` moves `docker/dev/`, that sentence
  goes with it.

## Surprises

- ⚠️ **[`README.md`](../../../README.md) is a hashed input of the dev image** (`docker/dev/check`'s `INPUTS`, and
  `pyproject.toml`'s `readme`), so this edit moves the dev image's tag; the first gate run rebuilt
  it. Expected, and harmless, but every README edit costs a rebuild.
- ⚠️ **The previous README said *"Status: planned, not built … No framework code exists yet"*** and
  sent readers to the board, the task index, the conventions and the capability index file —
  every one of which `REL-06/1` and this task's forbidden list name.

## Findings

| id | marker | where | what |
|---|---|---|---|
| `REL-07/1` | `[local]` | [`execution`'s `SKILL.md`](../../../src/studyforge/skills/execution/SKILL.md) *Before you start*, [`buildserve`'s `SKILL.md`](../../../src/studyforge/skills/buildserve/SKILL.md) narration table | ⚠️ **Both still describe the components as siblings pinned by `workspace.json`**, a development arrangement (R18) a stranger with the installed library does not have, and neither says how a stranger obtains a component. `REL-13` (each component's README as a stranger's reading list) and the skills' owner; the README says only "a separate repository … from its own checkout" |
| `REL-07/2` | `[local]` | [`docs/authoring/examples.md`](../../authoring/examples.md), example A's plan | ⚠️ **The quoted plan summary is stale**: it says `20 path(s) to create, 0 file(s) to edit, 0 ignore line(s)`; the command prints `6 path(s) to create … 3 ignore line(s)` at `d8632412`. `test_authoring_reference` does not read that sentence. The authoring reference's owner |
| `REL-07/3` | `[local]` | `tools/tests/quality/test_pointers.py`, `test_a_pointer_to_a_directory_resolves` | ⚠️ Its comment says the tree carries one directory pointer, [`README.md`](../../../README.md) → `docs/conventions/`. That link is gone; the test builds its own fixture and still passes. Tooling, leaves with `REL-10` |
| `REL-07/4` | `[local]` | [`CLAUDE.md`](../../../CLAUDE.md) | ⚠️ Still names [`docs/capability-index.md`](../../capability-index.md) and `docs/conventions/` as instruments (`REL-06/1`, the README half now closed). `REL-11` owns it |

## For dependents

- ⭐ **`REL-10` (the removal commit):** move [`ONBOARDING.md`](../../../ONBOARDING.md) to the archive
  branch under the user's `W438/2` ruling; nothing on the main line links it after this merge.
  `tests/test_readme.py` imports nothing from `tools/` and stays. If `docker/dev/` leaves, delete
  the README's last *Images* bullet in the same commit.
- ⭐ **`REL-11` (the light board):** [`docs/capability-index.md`](../../capability-index.md) is already on the README's forbidden
  list, so removing it breaks nothing here.
- ⭐ **`REL-14` (the close):** the README's install and first-run block is the walk to repeat from a
  clean clone of the main line; every link from the README reaches only the README,
  `docs/authoring/`, the decisions file, the spec and the skills — `tests/test_readme.py` holds
  that at every ref.
- ⭐ **Anyone adding a skill:** the suite goes RED until the README's skills table places it at a
  step and links its document. That is the intent.
- ⛔ **Re-measure; never copy a figure from this handoff.**
