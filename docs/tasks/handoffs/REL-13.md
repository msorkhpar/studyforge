# REL-13 — handoff

**Kind:** task handoff — REL-13

## Status

**done within its scope; the toolchain's Docker suite reads RED only on `REL-13/1`, which the register
took out of this task and minted as its own row, `W463`.** Task [`REL-13`](../E15-release-ready.md),
milestone **M11**, step **11.5**. Office `dev4`. ⭐ An epic task, so it has no row file and nothing was minted here.

| repository | branch | cut at | tip | worktree |
|---|---|---|---|---|
| `code-server-toolchain` | `chore/REL-13-release-ready` | `65c3851` (its main) | `d5a3b02` | `code-server-toolchain-wt/rel13` |
| `narrate-service` | `chore/REL-13-release-ready` | `ce975b6` (its main) | `da8fa84` | `narrate-service-wt/rel13` |

⭐ **Two passes.** The first pass (`aca5b88`, `31f491c`) did the README and prose cleanup. The
second pass (`d5a3b02`, `da8fa84`) followed the register's rulings on the first report: rewrite the
four contract prose values (`REL-13/4`, ruled yes), and fix the planted runner copies (`REL-13/2`,
ruled inside this task). `REL-13/1` was ruled out of scope.

⭐ **Author line declared:** every commit on both branches, and this handoff's commits, is
`dev4 <dev4@example.invalid>`, passed with `git -c`. ⛔ No git config was written, no remote was
added, nothing was pushed, no branch was deleted and no worktree was removed. Neither main was
committed on.

⛔ **Not done here, and the register's:** merging the two branches, advancing `workspace.json`'s
two pins to the merge commits (the Definition's last clause), and the branch and worktree
deletions under *For dependents*, which wait for the user's go-ahead.

## Gates

⭐ **Each reading was taken in a clean clone**: `git clone` of the local repository into the
office's scratch directory, checked out at the tip named in the row, nothing else in it. Output to
a scratch file, exit code read on the next line. ⛔ Every container job ran under the shared
`/tmp/studyforge-container-gate.lock`. `TC_KEEP_IMAGES=1` was set for every toolchain run.

| repository @ tip | reading | environment | result |
|---|---|---|---|
| `narrate-service` @ `da8fa84` | `python3 -m pytest -ra` | host, clean clone | GREEN, exit 0 |
| `narrate-service` @ `da8fa84` | `python3 -m tools.plant` (every negative control) | host, clean clone | GREEN, exit 0 — every control fired on the test that names its property |
| `narrate-service` @ `da8fa84` | `docker build --pull=false -t narrate-service:rel13-da8fa84 .` | host Docker | GREEN, exit 0 — only the digest-pinned base, already local |
| `code-server-toolchain` @ `aca5b88` | `python3 docker/minimal/build.py --runtimes java,maven` | host Docker | GREEN, exit 0 → `code-server-toolchain/runner:java-maven-amd64-a5c56ce13905` |
| `code-server-toolchain` @ `aca5b88` | `python3 docker/editor/build.py --runtimes java,maven` | host Docker + host Chrome | GREEN, exit 0 → `code-server-toolchain/editor:java-maven-amd64-dddf9c860a69` (activation and confinement both proved) |
| `code-server-toolchain` @ `d5a3b02` | `python3 -m unittest discover -s tests` | host, clean clone | GREEN, exit 0 |
| `code-server-toolchain` @ `d5a3b02` | `TC_DOCKER=1 python3 -m unittest discover -s tests -v` | host Docker + host Chrome | ⛔ **RED, exit 1** — 2 errors, both `REL-13/1` (below); ⭐ no other failure and no other error |

⭐ **The two image builds need no re-read at `d5a3b02`.** The second pass changed
`consuming.json`, `docs/compose.reference.yaml` and `tests/test_image.py`, and none of them is a
tag input: `--print-tag` at `d5a3b02` gives the same two tags. The suite at `d5a3b02` builds
`java,maven` again during its own run.

⭐ **The two errors, both waiting on `W463` (`REL-13/1`), and nothing else:**
`test_editor_image.TheEditorImage` (the default five-runtime set) and
`test_editor_selection_image.TheSelectedImages` (the `python` set). Both fail in `setUpClass`,
because the editor build is refused. The exact refusals, with the image id elided:

```text
refused: <id>: the practice frame is not confined -- the extension reports 4 keybinding removals the session did not load -- the seed no longer covers this workbench (studyforge.practice-focus: confined keybindings: derived=855 loaded=853 missing=4 extra=0 file=present)
refused: <id>: the practice frame is not confined -- the extension reports 4 keybinding removals the session did not load -- the seed no longer covers this workbench (studyforge.practice-focus: confined keybindings: derived=849 loaded=853 missing=4 extra=0 file=present)
```

The first is the five-runtime set and the second the `python` set. Each build then printed *"the
image was built and is NOT tagged; it is reachable only by its id"*. The control from the first
pass stands: `python3 docker/editor/build.py --runtimes python` at main `65c3851` is refused the
same way, with the same missing count.

⭐ **`REL-13/2` is closed, and each plant is RED for its named reason.** At `d5a3b02` every plant in
`test_image.TheRunnerImage` passed, and each one asserts the build failed *and* names its own reason:

- `test_a_wrong_checksum_stops_the_build_before_anything_is_unpacked`: the output matches
  `checksum`, and the unplanted copy of the same inputs builds (exit 0).
- `test_a_version_the_runtime_does_not_report_stops_the_build`: `does not report`.
- `test_an_undeclared_runtime_under_opt_stops_the_build`:
  `/opt holds 'node'; the declared set places ''`.
- `test_a_warm_file_that_differs_from_its_pin_stops_the_build`: both sub-plants (*a changed hash*,
  *an unpinned file*) match `checksum differs from pins.json|unpinned file`.

On the first pass the same five plants failed on `"/prime": not found`.

⚠️ `test_consuming_image.TheComposeContract` **SKIPPED** on this host, by its own guard: the
reference compose file publishes `127.0.0.1:8443`, which the reader's running editor holds.
→ `REL-13/3`.

⭐ **The process-id grep**, re-taken in each worktree at its tip with
[`docs/decisions.md`](../../decisions.md)'s header pattern over the whole sibling, plus the `E<nn>`
epic spelling. In `narrate-service` it prints nothing. In `code-server-toolchain` it prints only
the `ruling 1` … `ruling 5` lines kept under *Decisions*.

## What landed

### `narrate-service` (`31f491c`, then `da8fa84`)

- **The sibling's README** opens with a **Reading list** (this README, `consuming.json` and what it
  promises, `docs/api.md`, `docs/agent.md`, `docs/engine-measurement.md`) and gains **Build the
  image**. That section shows the contract's tag `narrate-service:local` via
  `docker compose build narrate`, any tag of one's own via `docker build -t`, and the engine as a
  separate digest-pinned image.
- **Every process id in prose is replaced by the reason it stood for**, across `narrate/`,
  `tests/`, `tools/` and `docs/api.md`. No code, test logic or plant anchor changed.
- **`consuming.json` `api.cache.note`** no longer says *"(NS-04, closing CTO-69/19)"*; the sentence
  states the fact alone.

### `code-server-toolchain` (`aca5b88`, then `d5a3b02`)

- **The sibling's README** opens with a **Reading list** (this README, `consuming.json` and what its
  two blocks promise, `docs/consuming.md`, `docs/compose.reference.yaml`, the two pin files) and
  says what a build needs on the host.
- **Every process id in prose is replaced or dropped** across `docker/`, `lockdown/`, `prime/`,
  `consuming/`, `pins.json`, `editor-pins.json` and `tests/`. That includes three build-failure
  messages in `docker/editor/Dockerfile` (*"W454/W448 patches exactly one"* is now *"this step
  patches exactly one"*) and the two tests that assert them. It also includes one finding message
  in `docker/minimal/plan.py`, whose test now filters on the message's own words, and the test
  constant `TC01_PATH`, renamed `FIRST_IMAGE_PATH`.
- **`consuming.json`, three prose values**:
  - `editor.command_notes.workspace_trust` drops *"(W432)"* and says why the flag matters:
    without it, the lockdown was once installed and never ran.
  - `editor.extensions.the_command_surface_is_confined` drops its leading *"W433: "*.
  - `editor.extensions.must_run_not_merely_be_installed` drops *", W433"*.
- **`docs/compose.reference.yaml` regenerated** with `python3 consuming/consuming.py --write`,
  because the generator renders `command_notes.workspace_trust` as a comment above `command:`.
  `--check` reports no findings.
- **`tests/test_image.py`'s `planted_copy`** now copies the runner's whole build context,
  `build.PRIMED_INPUT_ROOTS` (read, never re-listed), instead of `plan.INPUT_ROOTS`. The
  Dockerfile's warm step binds `prime/` in every build, primed or not. ⭐ An unprimed tag is still
  taken over `plan.INPUT_ROOTS` alone: `--print-tag` on the planted copy and on the tree give the
  same `…-a5c56ce13905`.
- ⚠️ **Every runner and editor tag moves** relative to main, because comments in the tag inputs
  changed. For `java,maven`, main gives runner `…-d82ccc2e214c` and editor `…-d961830755e8`; this
  branch gives runner `…-a5c56ce13905` and editor `…-dddf9c860a69`. ⭐ No tag the reader's site
  uses was rebuilt or overwritten.

### ⭐ The contract diff is prose-only, shown

Every leaf path of each `consuming.json` was compared before and after, by path, type and value, with a
throwaway script in scratch:

| contract | same paths | same types | values that changed |
|---|---|---|---|
| `code-server-toolchain` | yes | yes | `editor.command_notes.workspace_trust`, `editor.extensions.the_command_surface_is_confined`, `editor.extensions.must_run_not_merely_be_installed` |
| `narrate-service` | yes | yes | `api.cache.note` |

Every key, every type and every other value is identical. The four that changed are the four the
register ruled. `docs/compose.reference.yaml`'s diff is nine comment lines replaced by ten (the same
note re-wrapped). No YAML key or value line changed.

## Decisions

- ⭐ **Kept, with the reason.** These are the only lines the process-id grep prints after this task:

  | where | what | why it stays |
  |---|---|---|
  | `code-server-toolchain`: `docs/consuming.md` and `tests/test_consuming_image.py` | `ruling 1` … `ruling 5` | ⭐ not a process id: they are the numbered sections of `docs/consuming.md`'s own *The five rulings a consumer inherits*, and resolve inside the repository |

- ⭐ **Spec rules (`R5`, `R7`, `R9`, `R19`, `§8.3`) were left where they stood**, as
  [`docs/decisions.md`](../../decisions.md) defines them: a spec rule is not a process id.
- ⭐ **The comments in the tag inputs were rewritten, not kept**, although that moves every tag. A
  tag is designed to move with its inputs, and the corpus's own procedure already re-records the tag
  whenever the pin moves.
- ⭐ **`planted_copy` reads `PRIMED_INPUT_ROOTS` rather than adding `"prime"` by hand.**
  `docker/minimal/build.py` declares that tuple as the one place the runner's primed inputs are
  listed, and its comment says a planted context is copied by reading it. A second list is the
  drift `tests/build_inputs.py` exists to prevent.
- ⚠️ **The narrate-service image was built with `docker build`, not `docker compose`.**
  `compose.yaml` names the image `narrate-service:local`, which the reader's deployment uses, so a
  compose build would have overwritten it.

## Surprises

- ⚠️ **`code-server-toolchain`'s Docker suite was RED on its own main** (`REL-13/1`, `REL-13/2`).
  The Definition assumed a clean checkout of main passes its suite.
- ⚠️ **`docker compose build` has no `--pull never`**: its `--pull` is a boolean that is off by
  default. The README's build line carries no pull flag.
- ⚠️ **A narrate-service negative-control run killed by `timeout` left its plant in the tree.** In a
  scratch clone, `timeout 590 python3 -m tools.plant` was cut off by SIGTERM, and
  `narrate/artifacts.py` stayed planted. The harness restores in a `finally`, which SIGTERM does not
  run. It happened in a throwaway clone and was restored with `git checkout`; the full run was taken
  again afterwards (GREEN, above). → `REL-13/6`.
- ⚠️ The first `git worktree add` resolved its path inside the repository. The worktree was moved
  with `git worktree move` to `code-server-toolchain-wt/rel13` before any work.

## Findings

| id | marker | where | what |
|---|---|---|---|
| `REL-13/1` | `[local]` | `code-server-toolchain`: `docker/editor/seed/keybindings.json` and the confinement gate | ⛔ **Only a `java,maven` editor builds**; the seed covers that workbench only. ⭐ **Ruled out of this task by the register and minted as `W463`**, whose branch `fix/W463-every-runtime-set-builds-an-editor` is cut at this task's tip. The two refused tests and their exact refusals are under *Gates* |
| `REL-13/2` | `[local]` | `code-server-toolchain`: `tests/test_image.py`, `planted_copy` | ⭐ **Closed on this branch** (`d5a3b02`). Every plant is now RED for its named reason |
| `REL-13/3` | `[local]` | `code-server-toolchain`: `tests/test_consuming_image.py` | ⚠️ **The compose contract's live test skips on any host serving a corpus**, because the reference file's port is the one the reader's editor holds. It could take a free port, as its two-tags clause already does |
| `REL-13/4` | `[structural]` | both `consuming.json` files | ⭐ **Ruled yes by the register and done** (`d5a3b02`, `da8fa84`). The contract diff is prose-only, shown above |
| `REL-13/5` | `[local]` | `workspace.json` pins, the first corpus's execution records | ⚠️ **Advancing the toolchain pin moves every tag**, so the corpus's recorded runner tag and editor tag need re-recording, and both images a rebuild (the runner with its prime), before the site is regenerated against the new pin |
| `REL-13/6` | `[local]` | `narrate-service`: `tools/plant.py` | ⚠️ **A plant survives SIGTERM.** Restoration is in a `finally`, which a signal kill skips, so a harness stopped by `timeout` or a closed terminal leaves a planted source file in the working tree. A signal handler that raises would make the `finally` run |

## For dependents

- ⭐ **The register (merge and pin):** merge each `chore/REL-13-release-ready` into its sibling's
  main, then advance `workspace.json`'s two rows to the merge commits. ⚠️ After the toolchain pin
  moves, `REL-13/5` applies before anything regenerates the first corpus's execution files.
- ⭐ **`W463`:** the two editor-image test classes above are the ones waiting on it. At
  `d5a3b02` nothing else in the toolchain's Docker suite fails.
- ⭐ **`REL-14`:** the toolchain's clean-clone suite is RED on `W463` only.
- ⭐ **Images this task left on the host** (`TC_KEEP_IMAGES=1`; nothing that was already there was
  touched): every `code-server-toolchain/runner:*-a5c56ce13905` and
  `code-server-toolchain/editor:*-dddf9c860a69`, plus `narrate-service:rel13-31f491c` and
  `narrate-service:rel13-da8fa84`. The refused editor builds are untagged, reachable only by id.
  ⭐ Still present and untouched: `code-server-toolchain/editor:java-maven-amd64-d961830755e8`,
  `code-server-toolchain/runner:java-maven-amd64-7a5a2f2aacba` and `narrate-service:local`.

### Every local branch, read at the time of this handoff

`is-ancestor` is the exit code of `git merge-base --is-ancestor <tip> main` in that repository.

**`code-server-toolchain`** (main `65c3851`)

| branch | tip | is-ancestor | checked out in |
|---|---|---|---|
| `chore/REL-13-release-ready` | `d5a3b02` | 1 (this task; not merged yet) | `code-server-toolchain-wt/rel13` |
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
| `fix/W463-every-runtime-set-builds-an-editor` | `d5a3b02` | 1 (not merged; minted by the register for `REL-13/1`, cut at this task's tip; not this task's to delete) | `code-server-toolchain-wt/dev7` |
| `main` | `65c3851` | 0 | `code-server-toolchain` |
| `task/TC-01-the-editor-image` | `8914ac8` | 0 | |
| `task/TC-02-toolchain-selection` | `0b35abb` | 0 | |
| `task/TC-03-cache-priming` | `f85800a` | 0 | |
| `task/TC-04-workbench-lockdown` | `3d2c9c8` | 0 | |
| `task/TC-05-compose-and-mount` | `72c3931` | 0 | |
| `task/TC-06-versioning-and-pinning` | `a3aee75` | 0 | `code-server-toolchain-wt/dev1` |

The four `dev*` worktrees on merged branches (`dev1`, `dev2`, `dev4`, `dev6`) have no tracked or untracked change; each holds only ignored caches
(`__pycache__/`, `.pytest_cache/`).

**`narrate-service`** (main `ce975b6`)

| branch | tip | is-ancestor | checked out in |
|---|---|---|---|
| `chore/REL-13-release-ready` | `da8fa84` | 1 (this task; not merged yet) | `narrate-service-wt/rel13` |
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
