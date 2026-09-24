# REL-10 — handoff

**Kind:** task handoff — REL-10

## Status

**done, self-certified against the epic.** Task `REL-10`, defined in
[`E15` § REL-10](../E15-release-ready.md#rel-10-the-archive-branch-and-the-main-line-without-the-process).
⭐ **An EPIC TASK, so it has no row file and nothing was minted.** Branch
`chore/REL-10-the-process-leaves-the-main-line`, cut at the release tip `fc6c8008`. Office `dev6`.
Milestone **M11**, step **11.5**.

⭐ **The one sentence:** the branch is two commits on `fc6c8008` — this handoff, then the ONE
removal commit — so the register cuts `archive/process` at the removal commit's parent, which
holds every removed path byte for byte AND this handoff, and fast-forwards the main line to the
removal commit.

⭐ **Author line declared:** every commit on this branch is `dev6 <dev6@example.invalid>`, passed
with `git -c`. ⛔ Nothing was written to any git config, no remote was added, nothing was pushed.
⛔ **No ref was created or moved outside this branch**: `archive/process` does not exist yet, and
cutting it is the register's (commands below). Every trial ref lived in a scratch clone.

## ⭐ Which of the brief's two handoff placements, and why

**Committed on the branch BEFORE the removal commit.** The removal commit deletes
`docs/tasks/handoffs/` whole, so this file is on the main line for exactly one commit and then
lives on `archive/process` — the brief's first option. ⭐ It costs the register nothing: the cut
is still `<branch>^`, and there is no second commit to place on the archive afterwards.
⚠️ **So the removal commit's parent is this handoff's commit, not `fc6c8008` itself**; the
parent of THAT is `fc6c8008`. ⭐ The removal commit's TREE does not contain this file, so every
reading below — taken on a first build of the removal commit straight on `fc6c8008`, before this
file existed — is a reading of the identical tree (the regeneration asserts the tree ids equal).

## ⛔ The Acceptance, clause by clause

⛔ Each was run bare, output to a scratch file, `$?` read on the next line. ⭐ The readings were
taken on the removal commit's tree in two checkouts: this worktree (where ignored `__pycache__`
directories of the old tooling survive the checkout, as they will in the main checkout), and a
`git clone` of the branch into the office's scratch directory, which has no `tools/` at all.

| clause | instrument | reading |
|---|---|---|
| every path the removal commit deletes is on the archive branch with the same blob | in the scratch clone: `git branch archive/process HEAD^`, then `archive_holds.sh archive/process HEAD` (below) | GREEN, exit 0: no deleted path missing or different |
| — its plants | the same instrument against a commit on the archive with one removed file's blob changed, and against one with one removed file absent | RED, exit 1, each; the changed file and the absent one are counted |
| `git grep -nE '^\s*(from|import) tools'` prints nothing | run at the removal commit | prints nothing, exit 1 (no match) |
| the product floor is GREEN with no `tools/` | `python3 -m tests.floor` in the scratch clone | GREEN, exit 0 |
| — and in the pinned image | `./docker/dev/check python3 -m tests.floor` in the scratch clone | GREEN, exit 0 |
| the product suite is GREEN with no `tools/` | `./docker/dev/check python3 -m pytest -n auto -q` in the scratch clone | GREEN, exit 0 |
| — on the host | `python3 -m pytest -n auto -q --basetemp=<scratch>` in the scratch clone | RED, exit 1: ONLY the three `test_serve_process.py` socket tests, which refuse a socket path of 100 characters or more — the brief-mandated scratch `--basetemp` is that long (`REL-08/6`, re-measured). The same three are GREEN in the pinned image row above, and GREEN on the host in the merge trial with the three deselected |
| the removal commit's parent is the archive's tip, so `git merge-base --is-ancestor archive/process <main>` exits zero | in the scratch clone, after the cut above | exit 0 |

`archive_holds.sh`, as run (standard `git` and POSIX `sh` only):

```sh
#!/bin/sh
# Usage: archive_holds.sh <archive-ref> <removal-commit>
set -eu
archive=$1; removal=$2
deleted=$(git diff --raw --no-abbrev --no-renames --diff-filter=D "$removal^" "$removal" | wc -l)
[ "$deleted" -gt 0 ] || { echo "no deletion read: vacuous"; exit 2; }
missing=$(git diff --raw --no-abbrev --no-renames --diff-filter=D "$removal^" "$removal" |
  while IFS="$(printf '\t')" read -r meta path; do
    blob=$(echo "$meta" | cut -d' ' -f3)
    have=$(git rev-parse -q --verify "$archive:$path" 2>/dev/null || echo none)
    [ "$have" = "$blob" ] || echo "$path"
  done | wc -l)
echo "deleted paths: $deleted; not held byte for byte on $archive: $missing"
[ "$missing" -eq 0 ]
```

## Gates

Run bare at the removal commit's tree, from `studyforge-wt/dev6`, output to a scratch file,
`$?` on the next line.

| gate | environment | reading |
|---|---|---|
| `./docker/dev/check ruff check .` | pinned image | GREEN, exit 0 |
| `./docker/dev/check ruff format --check .` | pinned image | GREEN, exit 0 |
| `python3 -m tests.floor` | host | GREEN, exit 0 |
| `./docker/dev/check python3 -m pytest -n auto -q` | pinned image | GREEN, exit 0 |
| `python3 -m pytest -n auto -q --basetemp=<scratch>` | host | RED, exit 1 — the three socket tests of `REL-08/6` and nothing else (see above) |
| `python3 -m tools.quality` | host, at this handoff's commit (the archive's tip) | GREEN, exit 0 — the one place the tooling still exists |

⚠️ **The pinned image is content-addressed over `pyproject.toml`**, which this commit edits, so
the first `docker/dev/check` at this tree built a new dev image tag from the pinned base. No other
image or container was touched.

## What landed

⭐ **No public surface**: nothing under `src/` changed but one sentence of the onboarding skill.
What leaves, and what moved so nothing got weaker:

**Leaves the main line** (on `archive/process` byte for byte): `tools/`, `docs/tasks/handoffs/`,
`docs/tasks/rows/`, [`docs/tasks/BOARD-ARCHIVE.md`](../BOARD-ARCHIVE.md), [`docs/tasks/rulings-index.md`](../rulings-index.md), all of
`docs/conventions/` (the rubric and every convention: `REL-08` carried each product clause into
the spec), `tests/harness/process.py`, and every test it declared process — the whole files, and
the single tests deleted from the product files that held them.

**Moved in the same commit, because it is product:**

- ⭐ **The rejected-palette check joins the product floor** (`REL-03/2`, `REL-08/3`):
  `tools/quality/palettes/` and its tests are now `tests/floor/palettes/`, imports rewritten, the
  table read from the spec's §8.4, registered in `CHECKS`, `palette_census` in `NOTICES`, and the
  pair answered for in `tests/floor/vacuity.py`. ⚠️ Its test `support.py` derives the repository
  root itself, because a non-test floor module may import only the standard library and the floor.
- ⭐ **The consumer-side fence moved into the spec's §9 amendment** (`REL-08/2`, the prescribed
  act): `tests/test_consumer_side_contract.py` reads `HOME` from the spec and STAYS on the main
  line as product; the onboarding skill's sentence and the authoring reader's comment name the
  spec. The test's sweep no longer reads `tools/` or `docs/conventions/`, and reads the spec for
  its fence only.
- ⭐ **The fixture-enforcer entry** points at `tests/floor/personal_data/test_registry.py`.

**Edited to stand without the tooling:** the root `conftest.py` (no `process` marker, no
`reads_tree` marker, no merge-gate selection seam — no test carries `reads_tree` by hand);
`pyproject.toml` (one test root; no `tools` in ruff's `src`, per-file ignores or first-party
roots; comments re-pointed at `tests.floor` and the spec); `tests/floor/config.py` (the tooling's
scan, test and mirror roots) and the floor tests that were about the tooling's layout;
`tests/gate_coverage/` (the tooling's row); `tests/test_product_stands_alone.py` (the sweep and
its plants stay; the declaration's tests went with the declaration); the delivery test helpers
only the removed tests used; the README link plant (below); the docker continuation census.

## Decisions

- ⭐ **`tests/harness/process.py` is deleted, not emptied.** Empty, it would print *"the tooling
  is ABSENT, so the 0 declared …"* on every run forever, and three of its guard's tests index the
  first entry. The guard that matters — no file under `tests/` or the root conftest imports the
  tooling, with its plants — stays in `tests/test_product_stands_alone.py`.
- ⭐ **The `LIVE_EPICS` and `HANDOFF` tests leave now**, although the epics stay until `REL-11`:
  they are in the declaration, and the Definition moves every declared test. See *For dependents*.
- ⛔ **`docker/dev/` was NOT edited**, although `check` and `compose.yaml` still print
  `docker/dev/check python3 -m tools.quality` as a usage line: every file in `docker/dev/` is an
  input of the image's content address, so a comment edit there rebuilds the dev image for every
  office. Routed as a finding.
- ⭐ **The README link test's plant was re-aimed, not weakened.** It planted a link into
  `docs/conventions/`, which is now refused as *dangling* before it can be refused as *leaving the
  main line*; it now plants two links that still exist and still leave ([`docs/tasks/BOARD.md`](../BOARD.md),
  [`docs/tasks/README.md`](../README.md)), and the dangling case keeps its own test.

## ⛔ After the cut: how the register merges

⚠️ **`tools.mergegate` cannot be used from the cut on — including for this branch.** Its first
gate runs `python3 -m tools.quality` against the MERGED tree, which has no `tools/`, so every
merge would be refused; running it from a worktree of `archive/process` stages the merge in the
archive, not the main line. ⭐ **The least machinery that keeps the product gates is the same
shape by hand**: stage, read every product gate on the merged tree, commit only on all-green,
abort and read the restore back on any red.

From the main checkout, on the main line, tracked tree clean:

```sh
before=$(git rev-parse HEAD)
git merge --no-ff --no-commit <branch>
python3 -m tests.floor;                                echo "floor $?"
./docker/dev/check ruff check .;                        echo "ruff $?"
./docker/dev/check ruff format --check .;               echo "format $?"
python3 -m pytest -n auto -q;                           echo "host suite $?"
./docker/dev/check python3 -m pytest -n auto -q;        echo "image suite $?"
# every one 0:
git commit -F <body-file>
# any one non-zero — stop there, then:
git merge --abort
test "$(git rev-parse HEAD)" = "$before" && test -z "$(git status --porcelain --untracked-files=no)"
```

⚠️ Stop at the first red, as the gate did. ⚠️ Where `STUDYFORGE_CONTAINER_LOCK` is set, wrap the
three `docker/dev/check` lines in `flock "$STUDYFORGE_CONTAINER_LOCK"` so offices still queue for
the container; the gate did that itself.

**The trial**, in a scratch clone of this branch, the removal commit as its main line, the
procedure run as one scratch script with the gates in the order above:

| branch | reading |
|---|---|
| `trial/red` — a 421-line module under `src/studyforge/` with no mirror | REFUSED at the floor, exit 1, `[size]` and `[mirror]` findings; `merge --abort`; `HEAD` and the tracked tree read back restored |
| `trial/green` — one docstring line in a test | floor, ruff, format, host suite, image suite each exit 0; the merge commit written |

⚠️ The trial's host suite passed a scratch `--basetemp` and deselected the three `REL-08/6`
socket tests, for the path-length reason above; the register runs it bare.

## ⛔ The register's commands

From the main checkout, on `release/m0-foundations`:

```sh
# 0. The tip must still be the one this branch was built on; if not, regenerate (below).
test "$(git rev-parse release/m0-foundations)" = fc6c8008c3ed0ec4d1280f31a2e64a40d0048ac4
# 1. Cut the archive at the removal commit's parent (this handoff's commit).
git branch archive/process chore/REL-10-the-process-leaves-the-main-line^
# 2. Land the removal commit.
git merge --ff-only chore/REL-10-the-process-leaves-the-main-line
# 3. Read the Acceptance on the landed main line.
git merge-base --is-ancestor archive/process release/m0-foundations; echo "ancestor $?"
sh <scratch>/REL-10/archive_holds.sh archive/process release/m0-foundations; echo "holds $?"
git grep -nE '^\s*(from|import) tools';                              echo "grep $? (1 = none)"
python3 -m tests.floor;                                              echo "floor $?"
```

⭐ The gates were read on exactly the tree step 2 lands (the branch tip); a fast-forward writes no
new tree. ⚠️ The main checkout keeps ignored `__pycache__` directories under `tools/` after the
fast-forward; nothing reads them, and they are the checkout's to clean.

**If the tip has moved**, from a linked worktree (never the main checkout):
`regenerate.sh <new-tip> <this handoff's commit>`, kept beside the patch it applies in the
office's scratch directory (`REL-10/`). It stops if the palette check changed since `fc6c8008`
(the copy would be stale), cherry-picks this handoff, applies the edit patch with `--3way`
(a conflict stops it), `git rm -r`s the leaving directories as they stand at the NEW tip (so a
handoff or row added since leaves too), commits with the same message, and prints whether the
main line still imports the tooling. ⛔ **Then every Acceptance clause and gate above is re-read**:
a new tip can carry a new process test, a new tooling import or a new link a product gate reads.

**From the cut on**, a handoff is committed to `archive/process` (a worktree of it, or a branch
cut from it that the register fast-forwards the archive to), and a decision it makes that still
shapes the product goes into [`docs/decisions.md`](../../decisions.md) on the main line in the same act.

## Surprises

- ⚠️ **The merge gate cannot land the branch that removes it.** Its floor gate is a subprocess
  of the tooling run against the merged tree, so the removal is the first merge that needs the
  post-cut procedure — not the second.
- ⚠️ **Two prescribed acts had no owner until now**: the palette check's move (`REL-08/3`) and the
  consumer-side fence's move (`REL-08/2`) were both still open at `fc6c8008`, and removing
  `tools/` or `docs/conventions/` without them would have dropped a product check. Both are in
  the removal commit.
- ⚠️ **A plant that names a path which leaves turns into a different refusal once it has left**:
  the README test's plant, above. The whole suite was run at the removal commit to find any
  other; that was the only one.

## Findings

| id | marker | where | what |
|---|---|---|---|
| `REL-10/1` | `[local]` | [`CLAUDE.md`](../../../CLAUDE.md) | ⛔ **For `REL-11`: it names what no longer exists on the main line** — `python3 -m tools.workspace verify` and `tools/workspace`'s resolution (the workspace section), `docs/conventions/` as a reading-list item, the review rubric's anchor for the gate clause, and *"Write a handoff at `docs/tasks/handoffs/<TASK-ID>.md`"* with its format in [`agent-protocol.md`](../../conventions/agent-protocol.md) — handoffs now go to `archive/process` |
| `REL-10/2` | `[local]` | the board, the task index, the epics, [`docs/tasks/CROSSREPO.md`](../CROSSREPO.md) | ⛔ **For `REL-11`: links into removed paths now dangle** — rows, handoffs, the board archive, the rulings index, the conventions. ⚠️ **No product gate reads them**: the link checker was the tooling's (`REL-03/5`), so they do not turn anything red, and `REL-11`'s Acceptance is the only instrument. [`CROSSREPO.md`](../CROSSREPO.md) and [`v2-backlog.md`](../v2-backlog.md) are named by no `E15` task |
| `REL-10/3` | `[structural]` | `tests/studyforge/skills/delivery/` | ⚠️ **For `REL-11`: the packaged capability index has no regeneration check on the main line any more** — the byte-equality and hand-edit tests were `LIVE_EPICS`, declared process, and left. And `test_epics.py` still reads the live epics through `plans.live_epics()`, undeclared, so trimming the epics changes what it reads; `test_packaged.py` reads [`docs/capability-index.md`](../../capability-index.md), which `REL-11` removes |
| `REL-10/4` | `[local]` | [the spec](../../specs/2026-09-08-studyforge-v1-design.md) | ⚠️ **Markdown links into removed paths**: the board archive's round anchors and `W357`'s handoff, plus prose naming `tools/` and `tools/catalog/`. No product gate reads the spec's links, so nothing is red; it widens `REL-01/1` / `REL-08/1`, whose owner is unassigned |
| `REL-10/5` | `[local]` | `docker/dev/check`, `docker/dev/compose.yaml`, `docker/dev/Dockerfile`, `.gitignore` | ⚠️ **Usage lines print `python3 -m tools.quality`** (should be `python3 -m tests.floor`), and comments cite handoffs, rows and [`agent-protocol.md`](../../conventions/agent-protocol.md). Not edited here: `docker/dev/` is the image's content address (see *Decisions*); bundle it with the next change that rebuilds the image anyway |
| `REL-10/6` | `[local]` | `tests/floor/` docstrings, `tests/floor/size.py`'s finding text | ⚠️ **For `REL-09`: prose about the tooling that left** — each copy's *"Mirror of `tools/quality/…`"* header, and the `[size]` finding text *"The review rubric admits …"*, which a user now reads with no rubric to find. Plus the wider population of `src/` and `tests/` docstrings naming `tools.quality` or `tools/`, which `git grep -n 'tools[./]' -- src tests` prints |
| `REL-10/7` | `[local]` | `tests/gate_coverage/` | ⚠️ Prose and one test name still speak of three trees and a *fourth*; the map now holds two rows. Comment-only, `REL-09`'s shape |
| `REL-10/8` | `[local]` | the office's scratch directory | ⚠️ **A host suite run with `--basetemp` in scratch peaks near 2 GB before it is deleted**, over the brief's 500M ceiling; it was deleted after each run. ⭐ The pinned-image run keeps its temp inside the container |

## For dependents

- ⭐ **`REL-11`:** `REL-10/1`, `REL-10/2`, `REL-10/3`. The epics, the board, the task index and
  [`docs/capability-index.md`](../../capability-index.md) are untouched here.
- ⭐ **`REL-12`:** the archive branch is `archive/process`; a branch is prunable when its tip is an
  ancestor of the main line or of that branch.
- ⭐ **`REL-14`:** the product floor is `python3 -m tests.floor`; the product suite runs from a
  clone with no `tools/`; clone, never `git archive` (`REL-02`'s surprise, still true).
- ⭐ **Every office from the cut on:** merges are by the procedure above, never `tools.mergegate`.
