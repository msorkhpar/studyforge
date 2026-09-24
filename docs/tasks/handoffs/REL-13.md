# REL-13 — handoff

**Kind:** task handoff — REL-13

## Status

**partial: the cleanup landed on both siblings; one sibling's own suite reads RED for reasons that
are already on its main.** Task [`REL-13`](../E15-release-ready.md), milestone **M11**, step **11.5**.
Office `dev4`. ⭐ An epic task, so it has no row file and nothing was minted.

| repository | branch | cut at | tip | worktree |
|---|---|---|---|---|
| `code-server-toolchain` | `chore/REL-13-release-ready` | `65c3851` (its main) | `aca5b88` | `code-server-toolchain-wt/rel13` |
| `narrate-service` | `chore/REL-13-release-ready` | `ce975b6` (its main) | `31f491c` | `narrate-service-wt/rel13` |

⭐ **Author line declared:** every commit on both branches, and this handoff's commit, is
`dev4 <dev4@example.invalid>`, passed with `git -c`. ⛔ No git config was written, no remote was
added, nothing was pushed, no branch was deleted and no worktree was removed. Neither main was
committed on.

⛔ **Not done here, and the register's:** merging the two branches, advancing `workspace.json`'s
two pins to the merge commits (the Definition's last clause), and the branch and worktree
deletions under *For dependents*, which wait for the user's go-ahead.

## Gates

⭐ **Each reading was taken in a clean clone**: `git clone` of the local repository into the
office's scratch directory, checked out at the branch tip above, nothing else in it. Output to a
scratch file, exit code read on the next line. ⛔ Every container job ran under the shared
`/tmp/studyforge-container-gate.lock`. `TC_KEEP_IMAGES=1` was set for every toolchain run.

| repository @ tip | reading | environment | result |
|---|---|---|---|
| `narrate-service` @ `31f491c` | `python3 -m pytest -ra` | host, clean clone | GREEN, exit 0 |
| `narrate-service` @ `31f491c` | `python3 -m tools.plant` (every negative control) | host, clean clone | GREEN, exit 0 — every control fired on the test that names its property |
| `narrate-service` @ `31f491c` | `docker build --pull=false -t narrate-service:rel13-31f491c .` | host Docker | GREEN, exit 0 — only the digest-pinned base, already local |
| `code-server-toolchain` @ `aca5b88` | `python3 docker/minimal/build.py --runtimes java,maven` | host Docker | GREEN, exit 0 → `code-server-toolchain/runner:java-maven-amd64-a5c56ce13905` |
| `code-server-toolchain` @ `aca5b88` | `python3 docker/editor/build.py --runtimes java,maven` | host Docker + host Chrome | GREEN, exit 0 → `code-server-toolchain/editor:java-maven-amd64-dddf9c860a69` (activation and confinement both proved) |
| `code-server-toolchain` @ `aca5b88` | `python3 -m unittest discover -s tests` | host, clean clone | GREEN, exit 0 |
| `code-server-toolchain` @ `aca5b88` | `TC_DOCKER=1 python3 -m unittest discover -s tests -v` | host Docker + host Chrome | ⛔ **RED, exit 1** — 5 failures and 2 errors, every one also present on `65c3851` (below) |

⭐ **The RED, and the control that places it on main, not on this branch.** Both failure classes
were reproduced from a clean clone of `code-server-toolchain` main `65c3851`, with the same
commands, under the same lock:

- **The 2 errors** (`test_editor_image.TheEditorImage` and
  `test_editor_selection_image.TheSelectedImages`, both `setUpClass`): the five-runtime and the
  `python`-only editor builds are refused by the confinement gate — *"the extension reports 4
  keybinding removals the session did not load -- the seed no longer covers this workbench"*.
  Control: `python3 docker/editor/build.py --runtimes python` at `65c3851` exits 1 with the same
  refusal and the same missing count. The `java,maven` build is GREEN on both refs. → `REL-13/1`.
- **The 5 failures** (every planted-copy build in `test_image.TheRunnerImage`): the planted copy
  holds `pins.json` and `docker/minimal/` only, and the runner Dockerfile copies `prime/`, so each
  plant fails with `"/prime": not found` before reaching the defect it plants. Control: the same
  planted-copy build at `65c3851` exits 1 with the same error. → `REL-13/2`.
- ⚠️ `test_consuming_image.TheComposeContract` **SKIPPED** on this host, by its own guard: the
  reference compose file publishes `127.0.0.1:8443`, which the reader's running editor holds.
  → `REL-13/3`.

⭐ **The process-id grep**, run in each worktree at its tip with the decisions-file spellings
([`docs/decisions.md`](../../decisions.md)'s header command's pattern, over the whole sibling, plus the `E<nn>` epic
spelling). It prints only what *Decisions* lists as kept.

## What landed

### `narrate-service` (`31f491c`)

- **The sibling's README** opens with a **Reading list** (this README, `consuming.json` and what it
  promises, `docs/api.md`, `docs/agent.md`, `docs/engine-measurement.md`) and gains **Build the
  image**: the contract's tag `narrate-service:local` via `docker compose build narrate`, or any
  tag of one's own via `docker build -t`, and the engine as a separate digest-pinned image.
- **Every process id in prose is replaced by the reason it stood for**, across `narrate/`,
  `tests/`, `tools/` and `docs/api.md`: task ids by the feature they built (the voice catalogue,
  the agent adapter, the CPU/GPU profiles, the batch job), review findings by the defect they
  named, ruling numbers by the rule, and `E13` by what it said. No code, test logic or plant anchor
  changed; the suite and every control read GREEN in the worktree before the commit, and again in
  the clean clone.

### `code-server-toolchain` (`aca5b88`)

- **The sibling's README** opens with a **Reading list** (this README, `consuming.json` and what its two
  blocks promise, `docs/consuming.md`, `docs/compose.reference.yaml`, the two pin files) and what
  a build needs on the host. The image descriptions no longer name the tasks that built them.
- **Every process id in prose is replaced or dropped** across `docker/`, `lockdown/`, `prime/`,
  `consuming/`, `pins.json`, `editor-pins.json` and `tests/`, including three build-failure
  messages in `docker/editor/Dockerfile` that read *"W454/W448 patches exactly one"* (now *"this
  step patches exactly one"*) and the two tests that assert them, one finding message in
  `docker/minimal/plan.py` and the test that filtered on its id (it now filters on the message's
  own words), and a test constant `TC01_PATH` renamed `FIRST_IMAGE_PATH`.
- ⚠️ **Every runner and editor tag moves.** The tag is a digest over its inputs, and comments in
  `docker/`, `lockdown/`, `prime/` and the pin files are inputs. `java,maven` on main is
  `runner …-d82ccc2e214c` / `editor …-d961830755e8`; on this branch `runner …-a5c56ce13905` /
  `editor …-dddf9c860a69`. ⭐ **No tag the reader's site uses was rebuilt or overwritten**; see
  *For dependents* for what a pin advance then owes.

## Decisions

- ⭐ **`consuming.json` is untouched in both siblings**, and so is `docs/compose.reference.yaml`,
  which is generated from the toolchain's contract. Four prose values there still cite a process
  id; they are questions, not edits (`REL-13/4`).
- ⭐ **Kept, with the reason** — the only lines the process-id grep prints after this task:

  | where | what | why it stays |
  |---|---|---|
  | `code-server-toolchain`: `consuming.json` `editor.command_notes.workspace_trust`, `editor.extensions.the_command_surface_is_confined`, `editor.extensions.must_run_not_merely_be_installed` | `W432`, `W433` | the contract (`REL-13/4`) |
  | `code-server-toolchain`: `docs/compose.reference.yaml` | `W432` | generated from the contract; a test asserts it equals the rendering |
  | `code-server-toolchain`: `docs/consuming.md` and `tests/test_consuming_image.py` | `ruling 1` … `ruling 5` | ⭐ not a process id: they are the numbered sections of `docs/consuming.md`'s own *The five rulings a consumer inherits*, and resolve inside the repository |
  | `narrate-service`: `consuming.json` `api.cache.note` | `NS-04`, `CTO-69/19` | the contract (`REL-13/4`) |

- ⭐ **Spec rules (`R5`, `R7`, `R9`, `R19`, `§8.3`) were left where they stood**, as
  [`docs/decisions.md`](../../decisions.md) defines them: a spec rule is not a process id.
- ⭐ **The comments in the tag inputs were rewritten, not kept**, although that moves every tag:
  a tag is designed to move with its inputs, the corpus's own procedure already re-records the
  tag whenever the pin moves, and keeping them would have left the component's most-read files
  citing the archive.
- ⚠️ **The narrate-service image was built with `docker build`, not `docker compose`**:
  `compose.yaml` names the image `narrate-service:local`, which the reader's deployment uses, so a
  compose build would have overwritten it. The distinct tag `narrate-service:rel13-31f491c` was used.

## Surprises

- ⚠️ **`code-server-toolchain`'s Docker suite is RED on its own main** (`REL-13/1`, `REL-13/2`).
  The Definition assumed a clean checkout of main passes its suite; it does not, independent of
  this task.
- ⚠️ **`docker compose build` has no `--pull never`**: its `--pull` is a boolean that is off by
  default. The rule applies to `up`; the README's build line carries no pull flag.
- ⚠️ The brief expected a narrate-service container on `127.0.0.1:8870`; none was running when
  this office first listed containers, and none was started or stopped here.
- ⚠️ The first `git worktree add` was given a path relative to the workspace while `git -C`
  resolved it inside the repository; the new worktree was moved with `git worktree move` to
  `code-server-toolchain-wt/rel13` before any work, and the stray empty directory removed.

## Findings

| id | marker | where | what |
|---|---|---|---|
| `REL-13/1` | `[local]` | `code-server-toolchain`: `docker/editor/seed/keybindings.json` and the confinement gate | ⛔ **Only a `java,maven` editor builds.** The seed was generated against one workbench; the five-runtime and `python` sets load 4 removals fewer and the gate refuses them. Present on main `65c3851`. A corpus declaring any other editor set cannot build its editor |
| `REL-13/2` | `[local]` | `code-server-toolchain`: `tests/test_image.py`, `planted_copy` | ⚠️ **Every planted runner build fails on `"/prime": not found`**, because the copy takes `plan.INPUT_ROOTS` and the Dockerfile copies `prime/`. The five plant tests therefore never reach their plant. Present on main `65c3851` |
| `REL-13/3` | `[local]` | `code-server-toolchain`: `tests/test_consuming_image.py` | ⚠️ **The compose contract's live test skips on any host serving a corpus**, because the reference file's port is the one the reader's editor holds. It could take a free port, as its two-tags clause already does |
| `REL-13/4` | `[structural]` | both `consuming.json` files, the four fields in *Decisions* | ❓ **May a contract's prose-only value be rewritten?** Each is an explanatory string no code in `studyforge` reads today (checked by grep over `src/` and `tests/`), and changing it changes no key and no value a generator acts on; the toolchain's `docs/compose.reference.yaml` would regenerate from it. Until that is ruled, the four citations stay |
| `REL-13/5` | `[local]` | `workspace.json` pins, the first corpus's execution records | ⚠️ **Advancing the toolchain pin moves every tag**, so the corpus's recorded runner tag and editor tag need re-recording, and both images a rebuild (the runner with its prime), before the site is regenerated against the new pin |

## For dependents

- ⭐ **The register (merge and pin):** merge each `chore/REL-13-release-ready` into its sibling's
  main, then advance `workspace.json`'s two rows to the merge commits. ⚠️ After the toolchain pin
  moves, `REL-13/5` applies before anything regenerates the first corpus's execution files.
- ⭐ **`REL-14`:** the toolchain's clean-clone reading is RED on `REL-13/1` and `REL-13/2`, and
  both are on main; neither is this task's to fix.
- ⭐ **Images this task left on the host** (`TC_KEEP_IMAGES=1`, and nothing that was already there
  was touched): every `code-server-toolchain/runner:*-a5c56ce13905` and
  `code-server-toolchain/editor:*-dddf9c860a69`, and `narrate-service:rel13-31f491c`. The refused
  editor builds are untagged, reachable only by id. ⭐ Still present and untouched:
  `code-server-toolchain/editor:java-maven-amd64-d961830755e8`,
  `code-server-toolchain/runner:java-maven-amd64-7a5a2f2aacba` and `narrate-service:local`.

### Every local branch, read at the time of this handoff

`is-ancestor` is the exit code of `git merge-base --is-ancestor <tip> main` in that repository.

**`code-server-toolchain`** (main `65c3851`)

| branch | tip | is-ancestor | checked out in |
|---|---|---|---|
| `chore/REL-13-release-ready` | `aca5b88` | 1 (this task; not merged yet) | `code-server-toolchain-wt/rel13` |
| `fix/W374-a-runner-image-holds-only-what-is-declared` | `2ea7f5a` | 0 | |
| `fix/W379-the-runner-cache-collision-reversed` | `2059b16` | 0 | |
| `fix/W387-the-runner-names-an-unpinned-runtime` | `a15a0b0` | 0 | |
| `fix/W390-the-runner-warms-a-corpus-cache` | `748f4fb` | 0 | `code-server-toolchain-wt/dev4` |
| `fix/W391-the-inputs-helper-lives-once` | `98bf055` | 0 | |
| `fix/W401-the-runner-declares-its-run-shape` | `92f5f5a` | 0 | `code-server-toolchain-wt/dev6` |
| `fix/W432-the-lockdown-actually-runs` | `be9b428` | 0 | |
| `fix/W433-the-practice-frame-is-confined` | `4a21021` | 0 | |
| `fix/W448-the-side-bar-starts-closed` | `f25900a` | 0 | |
| `fix/W454-the-editor-carries-no-copilot` | `57b578e` | 0 | `code-server-toolchain-wt/dev2` |
| `main` | `65c3851` | 0 | `code-server-toolchain` |
| `task/TC-01-the-editor-image` | `8914ac8` | 0 | |
| `task/TC-02-toolchain-selection` | `0b35abb` | 0 | |
| `task/TC-03-cache-priming` | `f85800a` | 0 | |
| `task/TC-04-workbench-lockdown` | `3d2c9c8` | 0 | |
| `task/TC-05-compose-and-mount` | `72c3931` | 0 | |
| `task/TC-06-versioning-and-pinning` | `a3aee75` | 0 | `code-server-toolchain-wt/dev1` |

The four `dev*` worktrees have no tracked or untracked change; each holds only ignored caches
(`__pycache__/`, `.pytest_cache/`).

**`narrate-service`** (main `ce975b6`)

| branch | tip | is-ancestor | checked out in |
|---|---|---|---|
| `chore/REL-13-release-ready` | `31f491c` | 1 (this task; not merged yet) | `narrate-service-wt/rel13` |
| `feat/NS-04-NS-06` | `c4dcb82` | 0 | |
| `feat/W13-engine-live-measurement` | `ce975b6` | 0 | |
| `main` | `ce975b6` | 0 | `narrate-service` |

### The deletion commands, for the register to run after the user's go-ahead

From the workspace root. ⛔ Re-take the table first: a tip that moved, or an `is-ancestor` that is
no longer 0, is not deleted. `branch -d` (never `-D`) refuses an unmerged branch by itself.

```sh
# code-server-toolchain: the idle worktrees on merged branches, then the merged branches
git -C code-server-toolchain worktree remove ../code-server-toolchain-wt/dev1
git -C code-server-toolchain worktree remove ../code-server-toolchain-wt/dev2
git -C code-server-toolchain worktree remove ../code-server-toolchain-wt/dev4
git -C code-server-toolchain worktree remove ../code-server-toolchain-wt/dev6
git -C code-server-toolchain branch -d \
  fix/W374-a-runner-image-holds-only-what-is-declared fix/W379-the-runner-cache-collision-reversed \
  fix/W387-the-runner-names-an-unpinned-runtime fix/W390-the-runner-warms-a-corpus-cache \
  fix/W391-the-inputs-helper-lives-once fix/W401-the-runner-declares-its-run-shape \
  fix/W432-the-lockdown-actually-runs fix/W433-the-practice-frame-is-confined \
  fix/W448-the-side-bar-starts-closed fix/W454-the-editor-carries-no-copilot \
  task/TC-01-the-editor-image task/TC-02-toolchain-selection task/TC-03-cache-priming \
  task/TC-04-workbench-lockdown task/TC-05-compose-and-mount task/TC-06-versioning-and-pinning

# narrate-service: the merged branches
git -C narrate-service branch -d feat/NS-04-NS-06 feat/W13-engine-live-measurement

# after each REL-13 branch is merged into its main
git -C code-server-toolchain worktree remove ../code-server-toolchain-wt/rel13
git -C code-server-toolchain branch -d chore/REL-13-release-ready
git -C narrate-service worktree remove ../narrate-service-wt/rel13
git -C narrate-service branch -d chore/REL-13-release-ready
```
