# ruling-78 — handoff

**Kind:** ruling record

**Ruling 78 — the quality floor prints the lint state, including its absence,
as a NOTICE.**

⛔ **This is a task handoff in everything but its declaration.** No `W`-id
existed when it was written, and **Ruling 68** puts the `W` id space in exactly
one minter's hands — the PO's. ⭐ **When the row is minted:** rename this file
to `<W-id>.md`, change the declaration to `**Kind:** task handoff — <W-id>`,
and renumber the findings below from `ruling-78/<n>` to `<W-id>/<n>`. The
document is written to the six-section contract already, so the rename is the
whole of the work. ⚠️ `ruling-46.md` is the precedent for the interim form.

**Status:** done. Branch `feat/ruling-78-lint-notice`, cut from
`release/m0-foundations` @ `90dc580`. One commit. No source under `src/`
touched; the diff is `tools/quality/` and its mirror.

---

## What landed

**`tools/quality/lint.py`** (new, 264 lines) — `lint_notice(root)`, a **NOTICE**
registered third in `tools.quality.NOTICES`. It reports the repository's lint
state in four states and **can never change an exit code**.

**`tools/quality/__init__.py`** — `NOTICES = (notices, pointer_coverage,
lint_notice)`, with the paragraph that says why it is a notice and why it is
**last**.

**`tools/tests/quality/test_lint.py`** (new, 334 lines) — the mirror. 26 tests.

**`tools/tests/quality/test_init.py`** — registration, **order**, and the
assertion that the new entry is not in `CHECKS` and does not move `run_all`.

### ⭐ What it prints, in each state — measured, not described

**Absent** (a real host run, `python3 -m tools.quality`, ruff not installed):

```
lint: ruff is NOT installed, so this run carries no lint signal at all. `ruff check .` and
`ruff format --check .` did not run, and the two gates in tests/test_repository.py skipped
rather than passed. `quality floor: clean` reports the standard-library floor and has never
meant lint-clean (Ruling 78). Get the signal with `pip install -e '.[lint]'`, or run the
pinned environment: `docker/dev/check`. This is not a failure — Ruling 77 keeps the floor
standard-library-only, so absence is reported here and never punished.
```

**Present and clean** (inside the pinned image):

```
lint: ruff 0.16.6 — `ruff check .` clean; `ruff format --check .` clean (395 file(s) already
formatted). This run carries a real lint signal.
```

**Present and dirty** (pinned image, over a tree with one unused import and two
unformatted files):

```
lint: ruff 0.16.6 — `ruff check .` 2 finding(s) in 1 file(s) (F401, I001); `ruff format
--check .` 2 file(s) would be reformatted. Not a floor failure and not a floor pass:
enforcement is in tests/test_repository.py, which fails the build on these wherever ruff is
installed (Ruling 78).
```

**Present and it would not answer** — the fourth state, which the ruling did
not name and the code needs: an unexpected exit, an unparseable report, a
timeout, or a process that will not start. It prints
`lint: ruff <version> is installed and could not be run — <reason>. This run
carries no lint signal;…`, and the reason is **an exit code or a class of
failure, never a captured stream** (see finding `ruling-78/2`).

⛔ **The line is printed immediately above `quality floor:`** — the line it
exists to qualify — and `test_the_lint_notice_prints_last` pins that.

---

## Decisions

**1. The notice runs the tool; it does not merely detect it.**
Ruling 78 asks for *"whether a linter was found, its version, and what it
said"*. The last clause needs an invocation, so `lint_notice` shells out.
⭐ **Ruling 77 survives intact** because what it forbids is the floor's **exit
code** depending on an optional install — and a notice has no exit code.
`test_the_lint_notice_cannot_change_the_exit_code` asserts the boundary
directly: `lint_notice not in CHECKS`, and `run_all` unchanged.

**2. Standard-library-only, asserted rather than promised.**
`test_the_notice_module_imports_only_the_standard_library` parses the module and
checks every import root against `sys.stdlib_module_names`. ⚠️ It also asserts
the parse found *something*, so the guard cannot pass on an unreadable file.

**3. ⛔ No path ruff reports is ever printed (R7).**
`--output-format=json` carries an **absolute** `filename` per finding; on a
contributor's machine that contains their home directory. Filenames are counted
into a `file(s)` number and dropped. Same reasoning on the error path: an exit
code cannot leak a path and a captured stderr can, so only the code is used.
Two tests hold both directions.

**4. `--no-cache` on both invocations.**
A notice that made the floor write `.ruff_cache/` into the tree it is reporting
on would be changing its subject in order to describe it. Two mutants (M5, M6).

**5. The displayed command is not the executed one.**
`ruff check .` is what a reader is told and can paste; `check --no-cache
--output-format=json .` is what runs. Pinned by a test, because the two drifting
apart would print a command that gives a different answer.

**6. The format counts come from the summary line, not from counting diffs.**
`ruff format --check` renders a per-file diff whose shape is presentation and has
changed between versions; `"9 files would be reformatted, 383 files already
formatted"` is the sentence the tool writes for a human. Regex on the summary.

**7. Enforcement was not moved.** `tests/test_repository.py:126` and `:134` are
untouched. ⭐ Notice supplies visibility of absence; test supplies enforcement of
presence.

---

## Surprises

⭐ **The notice's first real run caught its own defect.** The first pass through
the pinned image reported
`lint: ruff 0.16.6 — ruff check . 10 finding(s) in 1 file(s) (D401)` — **ten
`D401` errors in `lint.py` itself**, in a module written to close the hole that
four unreported `D401`s went through on `FND-08`. ⚠️ Noun-phrase docstrings
(*"The absolute path to `name`…"*) are flagged; the repository's existing ones
(*"Every non-test module missing…"*, *"Lines to print that are…"*) are not, so
the trap is `The`, not the noun phrase. All ten are now imperative.

⚠️ **The floor's own R7 gate refused my R7 test fixture.** The test that proves
absolute paths are never printed used a home-rooted absolute path as its example, and
`check_personal_data` failed the build on it — correctly. ⭐ The rule held
against the test written to demonstrate it, which is the strongest form it has.
The fixture is now `/path/to/checkout/…`.

⚠️ **The first sweep found a survivor, and it was in my own tests** — see
`ruling-78/1`. That is the negative control doing its job: a sweep that reports
14/14 on its first run has usually not been run properly.

---

## Findings

**`ruling-78/1` `[structural]` — a test that sizes its own input off the
constant it is meant to pin cannot fail.**
`test_a_long_tail_of_codes_is_capped_rather_than_dumped` generated
`MAX_CODES + 3` codes. ⛔ **Mutant M9 (`MAX_CODES = 6` → `60`) SURVIVED**: the
test grew its input with the constant and still saw a cap. ⭐ The fix is not a
literal pin of `6` — that is a change detector — but a **property test with a
hand-written bound the module does not own**: 40 distinct codes must leave at
most `MOST_CODES_A_NOTICE_MAY_NAME = 10` named in the line. It survives an
honest re-tuning of `MAX_CODES` to anything ≤ 10 and kills the mutant.
⚠️ **Worth a sweep of its own across the repository**: any test whose fixture
size, loop bound or expected value is computed from the module constant under
test has this shape. I did not look outside my task.

**`ruling-78/2` `[local]` — a diagnostic stream is a path leak and an exit code
is not.**
The obvious `_Unrunnable` reason is ruff's stderr, and on a config error ruff
prints the offending file's absolute path. The module carries **exit codes and
failure classes only**, and `test_the_unrunnable_line_carries_no_diagnostic_stream`
holds it. Recorded because the next person to improve this error message will
reach for stderr first.

**`ruling-78/3` `[structural]` — the host skip set gains a third
`ruff not installed` member, and the two sets are now 8 (container) / 12 (host).**
`tools/tests/quality/test_lint.py:330` — the one test that uses the real tool —
skips where ruff is absent, exactly as `test_repository.py:126` and `:134` do.
⭐ **That is contained by design**: every other state, including both states the
current machine cannot be in, is driven through a fake runner, so the skip costs
one invocation-level assertion and no coverage of behaviour. ⚠️ **But it is a
third member of the set the CTO measured as disjoint**, and a reviewer
reconciling host skips against a pinned 8 will now be off by four, not three.
⛔ **The remaining host/container gap is environmental, not code**: three
`test_knowledge_index.py` skips need the sibling repositories beside the
workspace root, which a worktree under `scratchpad/wt/` does not have.

**`ruling-78/4` `[structural]` — ⛔ `ruff format --check .` covers **Markdown**
in the pinned version, so a documents-only change can turn the lint line red.**
Measured on `ruff 0.16.6`: the tree holds **294** `.py` files and
`ruff format --check .` reports **395**; excluding `docs/` drops it to **297**.
⭐ Adding this handoff moved the number by one, which is how it was found — a
`.md` file is formatted for the Python inside its fenced blocks. ⚠️ **Nothing
in the tree is dirty today** and no change is proposed. The consequence for
reviewers is the one worth carrying: **a documentation-only branch still needs
its lint line**, and `docs/conventions/review-rubric.md` §4b's four states apply
to it exactly as they do to a source branch.

---

## For dependents

⭐ **A reviewer's lint line can now be copied off the floor.** Ruling 79 requires
a review to state lint on its own line with the version that produced it;
`python3 -m tools.quality` now prints exactly that, in all four states, one line
above `quality floor:`. ⛔ **`did not run` is no longer something a reviewer has
to notice was missing** — the floor says it, in capitals, with both commands and
both remedies.

⚠️ **The notice is not a gate and must never be read as one.** A dirty line says
*"Not a floor failure and not a floor pass"* and names
`tests/test_repository.py`. If a future task wants lint to fail the floor, that
is a change to **Ruling 77**, not to this module.

**Adding a fifth state** means a new `_…()` builder and a row in the sweep. The
four are: absent, present-clean, present-dirty, present-unrunnable.

### ⛔ The sweep — Ruling 70's form, Ruling 76's rows

**Environment:** the pinned image, `docker/dev/check`,
`python:3.14-slim`, `ruff==0.16.6`, `pytest==9.1.1`.
**Isolation:** the tree is copied to `/tmp/sweep` **inside the container** and
mutated there — ⛔ never the bind-mounted worktree, because a mutant a crashed
run leaves behind is a defect the next agent inherits.
**Cache purge:** every `__pycache__`, `.pytest_cache` and `.ruff_cache` removed
before **each** run; `-p no:cacheprovider` throughout.
**Suite per row:** `tools/tests/quality` + `tests/test_quality_floor.py`, `-x`.
**Ruling 76:** each row prints the **exit code** and the **pytest tail**, and the
verdict is void unless they agree.

```
BASELINE (before) : exit 0 | 283 passed in 3.15s | SURVIVING
BASELINE (after)  : exit 0 | 283 passed in 3.14s | SURVIVING
```

| mutant | verdict | exit | pytest tail |
|---|---|---|---|
| M1  unregister the notice | KILLED | 1 | `1 failed, 136 passed in 0.36s` |
| M2  print it before the pointer census | KILLED | 1 | `1 failed, 137 passed in 0.37s` |
| M3  say nothing when the tool is absent | KILLED | 1 | `1 failed, 151 passed in 1.20s` |
| M4  invert the absence test | KILLED | 1 | `1 failed, 151 passed in 1.26s` |
| M5  let the lint run write a cache | KILLED | 1 | `1 failed, 173 passed in 1.21s` |
| M6  let the format run write a cache | KILLED | 1 | `1 failed, 173 passed in 1.22s` |
| M7  report filenames instead of rule codes | KILLED | 1 | `1 failed, 160 passed in 1.23s` |
| M8  accept an unexpected exit as a verdict | KILLED | 1 | `1 failed, 167 passed in 1.21s` |
| M9  stop capping the rule codes | KILLED | 1 | `1 failed, 164 passed in 1.22s` |
| M10 call half-dirty a real signal | KILLED | 1 | `1 failed, 162 passed in 1.23s` |
| M11 drop the timeout from its reason | KILLED | 1 | `1 failed, 171 passed in 1.19s` |
| M12 read a failed version probe as a version | KILLED | 1 | `1 failed, 159 passed in 1.22s` |
| M13 default a missing summary count to one | KILLED | 1 | `1 failed, 156 passed in 1.20s` |
| M14 drop the fallback rule name | KILLED | 1 | `1 failed, 165 passed in 1.24s` |

**14 / 14 killed.** Every mutant is a **single-line swap**; byte deltas ranged
`-28` to `+30`, and M2 and M13 are byte-identical in length.

#### ⛔ The negative controls, and both were run negatively

**Control 1 — the harness can report a survivor, and did.** The first sweep run
returned **M9 SURVIVED, exit 0, `282 passed in 3.16s`**, both channels
agreeing. That is not a hypothetical: it found the real weakness recorded as
`ruling-78/1`, and the row above is the re-run after the test was fixed.

**Control 2 — a kill that carries no `N failed` is still a kill.** Replacing
`from tools.quality import lint` with a name that does not exist:

```
CONTROL  import-error mutant : exit 1 | 1 error in 0.11s | KILLED
CONTROL  restored            : exit 0 | 283 passed in 3.15s | SURVIVING
```

⛔ **`1 error in 0.11s` carries no failure count at all** — a harness grepping
only for `N failed` would have called that SURVIVED. The verdict function reads
**both** channels and requires them to agree, which is the whole of Ruling 76
and the lesson `FND-09`'s row 7 paid for.

### The numbers, both ends

| | passed | skipped | floor | lint |
|---|---|---|---|---|
| **base `90dc580`**, pinned image | **2970** | 8 | clean | ⭐ **pinned green** |
| **merge**, pinned image | **2998** | 8 | clean | ⭐ **pinned green** |
| base `90dc580`, host | 2967 | 11 | clean | ⛔ **did not run** — ruff absent |
| merge, host | 2994 | 12 | clean | ⛔ **did not run** — ruff absent |

**Delta: +28 tests.** ⭐ **The container skip set did not move**: the same eight,
five `test_dev_image.py` build tests (already inside the image) and three
`test_knowledge_index.py` (workspace not mounted). The host set is 12 — the
six `test_dev_image.py` skips (the five build tests plus `:296`, which only a
run inside the image can satisfy), the three knowledge-index tests, and the
**three** `ruff not installed` skips (`ruling-78/3`).

**Lint:** `pinned green` — ruff 0.16.6 in the dev image; `ruff check .` exit 0
(*All checks passed!*) and `ruff format --check .` exit 0 (**395 files already
formatted** at the merge, **392** at the base — see `ruling-78/4`).
