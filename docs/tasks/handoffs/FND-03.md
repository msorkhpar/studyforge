# FND-03 — handoff

**Status:** done. ⭐ **FND-01's lint clause is closed** — `ruff check` and
`ruff format --check` both run for real inside the image and both pass. One
file is excluded from the **formatter** for a named reason that is a genuine
conflict between two project rules; see *Findings* 1. Lint itself has no
exclusion.

## What landed

**`docker/dev/` — the framework's build environment (R15).**

| file | what it is |
|---|---|
| `Dockerfile` | `python:3.14-slim`, pinned by tag **and digest**; git; the pinned tools; no source |
| `requirements.txt` | pytest, ruff and their transitive dependencies, every one `==` |
| `compose.yaml` | the `dev` service: the checkout bind-mounted, `network_mode: "none"`, never root |
| `check` | POSIX sh wrapper — `docker`, `id` and builtins only, no Python |

**Usage, and the whole point of it in one line:**

```
docker/dev/check                            # the suite, in the container
docker/dev/check python3 -m tools.quality   # anything else, in the container
python3 -m pytest                           # the same work, on the host
```

⭐ **The command inside the container is the command a contributor runs on the
host.** There is no container-specific entry point, no `ENTRYPOINT`, and no
second thing to learn. A build environment invoked differently from the host is
one whose divergence you find out about late.

**`tests/docker/test_dev_image.py`** — 14 static checks that always run (pinned
base, exact pins, no network at run time, no Docker socket, source mounted not
copied, never root, no path from anybody's machine, the formatter exclusion is
one named file) and 5 integration checks that build the image and run the suite
inside it, gated on `STUDYFORGE_DOCKER_TESTS=1`.

**`pyproject.toml`** — three corrections to the ruff configuration FND-01 wrote
blind, plus the one formatter exclusion. See *Decisions* 8–10.

**Twelve lines of lint fixes** across files FND-01 and FND-04 already merged.
⚠️ This is diff outside `docker/dev`, and it is here because FND-03's acceptance
is that the suite passes in the container and the suite runs ruff. It is named
in full in *Decisions* 11 so a reviewer does not have to discover it.

## Decisions

**1. The network tension resolves by time, not by compromise.** `pip install`
needs the network; a test run must not have one. They are different moments, so
the install is in the `Dockerfile` and **nowhere else**, and the service sets
`network_mode: "none"` — no interface at all. A test that quietly reached for a
package index or an API now fails here rather than passing on whichever machine
happened to have one. `test_the_network_is_needed_only_at_build_time` asserts
the install appears in the Dockerfile and in neither of the other two files.

**2. The source is bind-mounted, never copied.** "From a clean checkout" means
the checkout on disk, not a snapshot baked into a layer at some earlier commit.
A `COPY . .` produces a container that reports on code the contributor is not
editing. `test_the_source_is_mounted_not_copied` pins the Dockerfile to exactly
one `COPY`, and it is the pin file.

**3. `studyforge` is not installed into the image — not even `-e`.**
`pythonpath = ["src", "."]` already resolves it from the mount. Installing it
would put a second copy in site-packages that can shadow the mount, so the
container and the host would run different code while reporting the same
result — precisely the failure R15 exists to prevent.

**4. Pinned by digest, and transitively.** A tag is a moving pointer;
`python:3.14-slim` will mean different bytes next month. Tools are pinned with
`==` including transitive dependencies, because a pin that stops at the direct
ones is not a pin. Refreshing them is a documented one-liner **run in the base
image**, never on a host — a host resolution picks up whatever that machine
already had.

**5. Never root, and no uid is written down.** `check` reads `id -u`/`id -g` at
run time and passes them through; nothing derived from this machine reaches a
file (R7). The compose default is `65534:65534`, chosen so that forgetting to
set it degrades to *cannot write* rather than to *writes as root*.
`PYTHONDONTWRITEBYTECODE=1` is in the image for the same reason: a
`__pycache__` written into a bind mount is a file in someone's working tree
owned by a uid they may not have.

**6. git is in the image, and it is a test dependency rather than a
convenience.** `tests/test_repository.py` asks `git check-ignore` whether the
ignore rules still keep FND-04's golden fixtures trackable. Without git the
check cannot answer, and a check that cannot answer has stopped guarding
anything.

**7. The integration tests are opt-in on `STUDYFORGE_DOCKER_TESTS=1`, and
deliberately not on "is Docker reachable".** ⛔ `docker build` needs the
network. Auto-running whenever a daemon is up would mean the default suite
needs network, which refutes this task's own acceptance. They are gated a
second time on `STUDYFORGE_DEV_CONTAINER`, the marker the image sets: without
it the suite would build a container, run the suite, which would build a
container, forever.

**8. Ruff's docstring rules do not apply to test modules.** The first ever run
reported 126 findings, **95 of them D103** — "undocumented public function", on
test functions. That is not 95 defects; it is one wrong rule selection. The
per-file-ignore defers to a ruling this repository had already made, in
`tools/quality/docstrings.py`: *"a test module's name and its assertions say
what it covers. Demanding a contract from it would be demanding a second
description of the same thing, which is a description that goes stale."*
⚠️ Scoped to the two test trees by name. D103 in `src/` or `tools/quality/`
still fails the build.

**9. `known-first-party = ["studyforge", "tests", "tools"]`.** Left to
inference, ruff read `studyforge` as first-party and `tests` as third-party,
and sorted a module's own package *below* the test helper it imports — a
16-file diff reversing the reading order of every mirrored test for no reason a
reader could name. Declaring the three roots removed all 16 findings with
**zero code churn**. ⭐ Worth stating because the first instinct was to accept
the auto-fix; the config was the defect.

**10. `ruff format` is adopted, with exactly one file excluded.** See
*Findings* 1 — it is a real conflict between the formatter and R11, not a
preference, and resolving it is not this task's call.

**11. The image is uid-agnostic, and finding that out cost two real defects.**
Running the service directly, without `check`, falls back to `nobody` — a uid
that owns none of the mounted files. Two things then broke: git refused the
tree as *"dubious ownership"* and returned 128 instead of a verdict, silently
turning FND-01's ignore-rule regression test into a test with no answer; and
ruff tried to write its cache into the bind mount. Fixed in the image with
`git config --system --add safe.directory /workspace` (⛔ scoped to the one
path this image ever holds, and ⛔ the same line on a host would be wrong) and
`RUFF_CACHE_DIR=/tmp/ruff-cache`. `test_the_suite_passes_for_a_uid_that_owns_nothing`
is what stops both coming back. `check` also now lets an already-set
`STUDYFORGE_UID` win, so a CI or rootless runner can choose without editing
anything.

**12. The lint fixes outside `docker/dev`, named in full.** Twelve lines:

- 5 × D401 non-imperative summary lines reworded — `tools/quality/config.py`
  (3), `tools/quality/size.py` (2). FND-01's own files.
- 1 × UP028 in `tests/test_fixture_consistency.py` — a `for … yield` became
  `yield from`. **FND-04's file, three lines, mechanical, ruff's own
  suggestion.** ⚠️ Flagged rather than absorbed: it is outside this task's
  `Owns`, and it is in the diff because the alternative was an acceptance
  condition that could not pass. If the reviewer would rather it were routed to
  FND-04, reverting it costs one commit and reopens one lint finding.
- `tests/docker/test_dev_image.py` and 5 files reformatted by `ruff format`
  (`tools/quality/config.py`, `tools/quality/size.py`, `tests/test_repository.py`,
  and three under `tools/tests/quality/`) — all FND-01's, all mechanical.

## Surprises

**The lint clause was not "install ruff and watch it pass".** It was 126
findings on first contact, and the interesting part is the breakdown: 95 were a
rule that should never have been selected for test files, 16 were a *config*
defect that produced churn until `known-first-party` was declared, 5 were real
and mine, 1 was real and somebody else's. ⭐ **A linter nobody has run is a
configuration nobody has evaluated** — FND-01 chose this ruleset honestly and
could not know, which is exactly what "Blocked" meant.

**The formatter and R11 disagree, and nobody had ruled on it.** See *Findings*
1. This is the kind of thing that only surfaces the first time both checks run
on the same tree.

**A linked git worktree breaks inside the container, and it is invisible until
it isn't.** `.git` is a *file* naming a git directory that lives outside the
checkout, so mounting only the checkout leaves git unable to answer anything —
and FND-01's ignore-rule regression test then has no verdict. `check` detects
the case and mounts the real git directory read-only. ⚠️ A plain clone needs
none of this and gets none of it. Nothing about the path is written to a file.

**The context budget (~25k, `CSD/docker-compose.yml`) was right in size and
wrong in kind.** That file is a *runtime* stack — three services, GPU
reservations, an IDE, an embed origin — and this task is a build environment
with one service and no ports. What it was genuinely worth reading for is one
sentence: *"No docker socket is mounted anywhere."* That is the convention this
image inherits, and `test_no_docker_socket_is_mounted_anywhere` now carries it.

## Findings

**1. ⛔ `ruff format` and R11 conflict on `tests/test_fixture_consistency.py`,
and the conflict is unresolved.** The file is 554 lines. The formatter honours
the magic trailing comma, so it explodes that module's hand-packed key tuples
one entry per line and the file becomes **606 lines — over R11's 600-line test
ceiling**. Formatting it would mean either splitting somebody else's merged
test module or authoring a `Size exception:` for work this task did not write.
Neither is FND-03's call.

⭐ **Routed, not resolved:** the file is excluded from the **formatter only**
(`[tool.ruff.format] exclude`), still linted, still measured by the quality
floor, still fully tested. `test_the_formatter_exclusion_is_exactly_one_named_file`
asserts the list has exactly that one entry, so it cannot become the place
difficult files go. **For FND-04 and the PO:** format it and split it, format
it and justify it, or keep it hand-packed and keep the exclusion. Any of the
three is a decision; the assertion exists so it is taken rather than inherited.

**2. ⚠️ The review rubric's `$BASE` is wrong for any branch cut from a release
branch, and it silently inflates the diff.** `docs/conventions/review-rubric.md`
§0 says `BASE=$(git merge-base HEAD main)`. `main` is still at `b1569e2`, before
FND-01 and FND-04 merged, so on this branch that base presents **100 changed
files** instead of the ~13 this task wrote — and every later check (`$PY`, R7's
added-lines sweep, R11, R12, scope) then runs over three tasks' work as if it
were one author's. Measured:

```
merge-base HEAD main                    -> b1569e2   (100 files in $BASE...HEAD)
merge-base HEAD release/m0-foundations  -> c7360b0   (13 files)
```

Suggested fix, which needs no per-task knowledge:
`BASE=$(git merge-base HEAD "${REVIEW_BASE:-release/m0-foundations}")`, or
resolve the branch's upstream. Not fixed here — `docs/conventions/` is not this
task's to edit.

**3. ⚠️ The host and the container do not run the same pytest, and only one of
them is pinned.** Container: pytest 9.1.1, Python 3.14.7, both pinned. Host:
whatever is installed — here pytest 9.0.2 on Python 3.14.4, pinned by nothing.
Both pass, so nothing is wrong today. ⛔ But R15's claim is that *a result never
depends on whose machine produced it*, and only the container run can make that
claim. **See *For dependents*: the container is authoritative and the host run
is a convenience.** This is worth a line in `agent-protocol.md` when somebody
edits it; it is not mine to add.

**4. `docs/tasks/README.md:288` and `CLAUDE.md:33` still say "R1–R19" while the
spec has R20.** Reported in FND-01's handoff, still open, still outside scope.

**5. E00's FND-03 wording is accurate and needs nothing.** Recorded because
FND-01's did not, and the contrast is useful: this task's Definition and
Acceptance survived contact unchanged.

## For dependents

⭐ **This image is now the definition of "the tests passed".** Every later task
inherits it.

**1. Run this.**

```
docker/dev/check                # needs Docker and nothing else
python3 -m pytest               # the same work, if you have Python 3.14
```

⛔ **When the two disagree, the container is right.** It is the only one whose
Python and whose tools are pinned (*Findings* 3). If you are about to claim a
change is green, claim it from the container.

**2. FND-01's blocked lint clause is closed, and the evidence is a skip count.**
On the host, `test_ruff_lint_is_clean_where_ruff_exists` and
`test_ruff_format_is_clean_where_ruff_exists` **skip** — ruff is not installed.
In the image they **run**: 115 passed / 6 skipped on the host becomes 117
passed / 4 skipped in the container, and the four remaining skips are the
opt-in docker tests skipping *because they are already inside the container*.
`test_lint_actually_runs_in_there_rather_than_skipping` asserts exactly that, so
the clause cannot silently reopen by ruff falling out of the image and two
tests going quietly back to skipping.

**3. Adding a test-only dependency is two edits, and a test enforces both.**
Add it to `pyproject.toml`'s `test` or `lint` extra **and** pin it with `==` in
`docker/dev/requirements.txt`.
`test_the_image_carries_everything_the_declared_extras_name` fails if you do
one and not the other. ⛔ Refresh the pins in the base image, never on a host:

```
docker run --rm python:3.14-slim sh -c 'pip install -q "pytest>=8.0" "ruff>=0.6" && pip freeze'
```

**4. Running the container tests yourself:** `STUDYFORGE_DOCKER_TESTS=1 python3
-m pytest tests/docker`. They are off by default because `docker build` needs
the network and this project's acceptance is that a test run does not.

**5. ⛔ This is not E12's image and must not become it.**
`code-server-toolchain` is the *reader's* IDE for a consuming project — a JDK, a
build tool, their primed caches. This one carries pytest and ruff so a
contributor can prove a change. Conflating them puts a compiler in a lint image
and ties the framework's build to whichever corpus happened to be first.

**6. ⛔ No Docker socket, here or anywhere** (spec §8.3). The rule is written
about the serving process; a build image is exactly where somebody reaches for
one "just to run the integration tests". `test_no_docker_socket_is_mounted_anywhere`
is permanent and costs nothing. It did not arise in this task and nothing here
talks to a daemon from inside a container.

**Specifically for:**

- **FND-04 / the PO** — *Findings* 1 is a decision waiting for you.
- **FND-05 (workspace)** — the image is built from `docker/dev/compose.yaml`
  with `context: .`, so it needs no path outside `docker/dev/` and composes
  into a parent workspace unchanged.
- **E10 (QA)** — `docker/dev/check` is the reproducible harness your acceptance
  runs should quote. A result from the host is a convenience; a result from
  here is evidence.
- **E12 (toolchain image)** — read *For dependents* 5 before you start. The two
  images share a rule (`no socket`) and nothing else.
