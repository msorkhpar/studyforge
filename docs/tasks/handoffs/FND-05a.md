# FND-05a — handoff

**Status:** done, round 2 — the R7 amendment, Ruling 53 and Ruling 54.
`feat/FND-05a-workspace`, rebased onto `release/m0-foundations` @ `6738559`.

**Measured, pinned (`docker/dev/check`), 2026-09-09.**

| | tests | skips | ruff | floor |
|---|---|---|---|---|
| Base `6738559` | 2351 passed | 8 | clean | clean |
| Branch | **2420 passed** | **8** | clean | clean |

⚠️ Round 1 read 2343 → 2384 at `5ebf83e`; both pairs are recorded so a reviewer
can tell a rebase from a change.

⭐ **+41 tests, and the same 8 skips — this task added none.** ⚠️ Worth saying
because the obvious way to test a pin file is to reach for the sibling
checkouts, which would have skipped inside the authoritative image. Every test
here builds real `git init` repositories in `tmp_path` instead.

## What landed

**`workspace.json`** — five rows: `studyforge` as `self`, and `CodeSignal`,
`Claude-senior-java-engineer`, `ISO-8583-jPOS-tutorial`, `Claude-SPARQL-tutorial`
as `sibling`. ⛔ **It contains no `/`, no `..`, no `~`, no host, and no home
directory** — asserted on the bytes.

**`tools/workspace/`** — `verify` exits **0** when correct and **1** naming the
component when not; `record` rewrites the commits from what is checked out.

**`docs/conventions/workspace.md`** — record, verify, advance, and the
two-commit rule.

**`tests/test_workspace_pin.py`** and **`tools/tests/workspace/`** — 41 tests.

⛔ **No `.gitmodules`, asserted rather than asserted-about**
(`test_no_gitmodules_anywhere_in_the_repository`).

### The two failure directions, asserted

| direction | test | what it looks like without the check |
|---|---|---|
| a recorded commit **absent locally** | `test_a_recorded_commit_absent_locally_is_named` | the checkout is present, on a branch, and looks fine |
| a component's `HEAD` **moved unrecorded** | `test_a_component_whose_head_moved_unrecorded_is_named` | ⛔ every recorded commit still resolves, so a naive check passes and the build "reproduces" a different workspace |

**Both controls run negatively**, before trusting either to pass:

| branch deleted from `verify` | reds |
|---|---|
| `HEAD moved unrecorded` | **4** tests |
| `recorded commit absent` | **2** tests |

## Round 2 — what the review found, and what closed it

⛔ **The file was clean and the reader was not.** Three probes, all reproduced,
all closed — and the CTO's diagnosis was right that they are **one** root cause:
⭐ `where` was a closed set and `name` was **free text in the same row**.

| probe | before | now |
|---|---|---|
| `workspace_api` holding a home-path string | echoed verbatim | `must declare workspace_api 1, got a str` |
| `name` holding a home-path string | echoed verbatim | names the permitted shape, quotes nothing |
| `name` = `../../elsewhere` or `/etc` | ⛔ **accepted**, resolved outside the workspace | refused |

⭐ **Constraining `name` to a single path component makes the echo and the
escape unrepresentable together** — `where`'s own move carried the rest of the
way. `SAFE_NAME` is `^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$`: no
separator, no traversal, no leading dot, and nothing a refusal has to quote.

**The version echo** is a local two-line `describe` — ⚠️ local, not a call:
Ruling 31 keeps `tools/` from importing `studyforge`. ⭐ An `int` is still
quoted, because an integer cannot carry a home directory, an address or a token.

**Ruling 53 — the image now refuses instead of answering.** Reporting four
components absent in there was a plausible, well-formed, **wrong** answer.
`verify` inside the pinned image exits **2** and says it is host-verified.
⚠️ Three answers, three codes: collapsing it into 1 would read as *"the
workspace disagrees"* and into 0 as *"it agrees"*, and this run can make neither
claim. An explicit `--workspace` is still answered — the seam is *the computed
workspace is not visible*, not *we are in a container*.

**Ruling 54 — the pin file is the register.** Rows gained `status`
(`present` / `not-yet-created`) with `commit` required **exactly when
`present`**, in both directions. `code-server-toolchain` and `narrate-service`
now have rows. ⛔ And `tests/test_workspace_pin.py`'s `COMPONENTS` tuple is
**deleted** — it was Ruling 20's second, weaker copy — so that module derives
from the file it is checking.

⭐ **A third failure direction came free with `status`:** a component recorded
as not-yet-created whose checkout appears is a finding. E12 and E13 cannot
create a component and forget to flip it.

## Decisions

**The pin file records a name and a `where`, never a path.** ⛔ **This is the
whole difficulty of the task.** A pin file's natural content is *"where each
component lives"*, and on this machine that is a home directory — the thing this
project forbids most absolutely and has already violated once in its own
documents. ⭐ `where` is a **closed set of two** (`self`, `sibling`); a sibling
resolves to `<workspace>/<name>` at run time. Same argument as W8's: `mvn` is a
fact about the environment, `/usr/bin/mvn` is a fact about one laptop.

**The workspace root is computed, and worktrees are handled.** A `git worktree`
lives outside the repository it belongs to, so its own parent is the wrong
answer; `git rev-parse --git-common-dir` names the main checkout. ⚠️ Not
gold-plating — every agent on this project works in a worktree, so the plain
parent would have made the gate report five missing components to whoever ran it.

**`studyforge`'s row is verified by ancestry, not equality.** A file inside a
repository cannot contain the hash of the commit that contains it. ⛔ So equality
is **unrepresentable** rather than quietly skipped, and the strongest true
statement — present locally and reachable from `HEAD` — is the one asserted.

**`record` never discovers a component.** It updates the commits of rows that
exist. A version that walked the workspace would pin whatever happened to sit
beside the repository that day.

**The two components that do not exist yet have no row.** ⛔ A row holding a
placeholder commit would be the file pretending. E12 and E13 add theirs — see
finding 56 for the cost of that choice.

## Surprises

⚠️ **The budget expected submodule mechanics and the task had none.** The real
work was two questions neither of which is about git: *what can a pin file say
that is not a path*, and *what can a file say about the commit that contains
it*. ⭐ Both have clean answers and neither is discoverable from the acceptance
wording, which says "records every component" — the honest reading of which is
"and its location".

⚠️ **The pinned image cannot run this gate** — see finding 55. That was not
anticipated and it is the one place this task's verification is unlike every
other check in the repository.

## Findings

### 53 `[local]` — a control test passed for the wrong reason, and only breaking it showed that

`test_verify_exits_one_and_names_the_component_when_a_commit_is_absent` asserted
the exit code and the component name. With the *absent-commit* branch deleted,
the **stale-commit** branch caught the same fixture and the test still passed —
⛔ the right number for the wrong reason. ⭐ Found by running the control
negatively rather than reading it, which is the rule that required it. Fixed:
both CLI tests now assert the direction-specific sentence. **Fixed.**

### 54 `[structural]` — two top-level documents still claimed submodule composition

`README.md` said components are "composed as **submodules** of one parent
workspace … while each keeps its own remote", and `CLAUDE.md` said "composed as
submodules of one parent". ⛔ Both are false under R18's amendment, and the
first is doubly so — there are no remotes. Corrected here, because the
acceptance forbids a document claiming otherwise. ⚠️ **The shape is the
finding:** the amendment landed in `E00-foundations.md` and the documents a new
agent reads *first* were not swept, so the wrong version was the one on the path
of least resistance.

### 55 `[structural]` — this gate cannot run inside the authoritative image — **ruled**

FND-03 mounts exactly one directory, so the sibling components are invisible from
inside the pinned container: `verify` there reports all four absent, correctly.
⛔ **So `python3 -m tools.workspace verify` is a host command, and it is the only
check in this repository that is.** ⭐ **Ruled 53, and the ruling is stronger than the finding:** pinning it would
be **wrong**, not merely hard — mounting the workspace hands the build four
sibling repositories and widens the container's trust boundary for a
convenience. ⛔ **And the ruling reversed this branch's behaviour**: reporting
the components absent in there was a plausible, well-formed, wrong answer, so
`verify` now refuses with exit 2. **Closed in this round.**

### 56 `[structural]` — a component that does not exist yet is unrepresentable, and so is the fact that it is owed — **ruled**

⛔ **The pin file cannot say "`narrate-service` is expected and absent"**, by
design — the alternative was a placeholder commit, which is worse. ⚠️ But that
means nothing mechanical states the two are owed: the closed set lives in
`tests/test_workspace_pin.py::COMPONENTS`, so E12 and E13 must each edit **two**
places, and forgetting the test leaves a component pinned by nobody. ⭐ **Ruled 54, and the correction was that `COMPONENTS` was the defect rather
than the fix**: the pin file is the register and the test derives from it, with
`status` carrying the owed half. **Closed in this round**, and it lands before
E12 because R9 makes a key expensive once written.

## For dependents

- ⭐ **Run `python3 -m tools.workspace verify` on the host**, from anywhere
  inside the repository or one of its worktrees. **0** verified, **1**
  disagrees, **2** this run could not tell — ⛔ **inside the pinned image it
  refuses with 2 rather than answering** (Ruling 53).
- ⛔ **Advancing a component is two commits** — one in the component, one here
  recording it. `record` writes the second; a message saying *why* is yours.
- ⚠️ **E12 and E13:** your component already has a row. Your task **flips its
  `status` to `present` and adds its `commit`**, in the commit that creates the
  repository — one file, not two (Ruling 54). ⛔ And `verify` reds the moment
  the checkout exists and the status has not been flipped.
- ⛔ **Do not add a URL to the pin file.** All three submodule failures return
  the moment one appears; `docs/conventions/workspace.md` has the table.

### 57 `[local]` — my own R7 discipline stopped at the file and not at the reader

⛔ **The pin file carries zero path bytes and the refusals carried them
straight back out.** ⚠️ **The shape is worth more than the fix:** I asserted the
*artifact* was clean — on the bytes, with a test — and never asked the same
question of the *messages the artifact's reader emits*. That is R7-by-inheritance
again, which is a measurement I made myself in SF-25 (6 of 10 poison shapes
reached a report line) and did not apply here. ⭐ A file being clean is not a
property of the file; it is a property of everything that reads it. **Fixed.**

### 58 `[structural]` — a closed set beside free text in one row reads as safe

⛔ **`where` being a closed set made the row *look* enumerated.** Both my own
review and the design docstring called the vocabulary closed, and it was — for
one of the two fields that decide where a component resolves. ⚠️ The general
tell: **when one field of a pair is constrained and the other is not, the
constrained one is the one everybody reads.** ⭐ Worth stating next to
*enumerate the legal*, because the failure is not an open set — it is a closed
set doing PR for the open one beside it.
