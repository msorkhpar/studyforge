# FND-08 — handoff

**Kind:** task handoff — FND-08

## Status

✅ **Done.** Ruling 43's second walk ships: `tools/quality/pointers.py` reads
every markdown document in the repository, fails on a pointer that resolves to
nothing and on an anchor that names no heading, and prints its **denominator**
through the notice channel. ⛔ **The migration is `0`** — as recorded — but
⭐ **every founding number the task was scoped on had moved**, which is Ruling
55 confirming itself for the fourth time.

| | |
|---|---|
| Branch | `feat/FND-08-walk`, off `release/m0-foundations` @ `2926dc2` |
| Base | **2662 passed, 8 skipped**, floor clean, exit 0 — reproduced |
| Merge | **2709 passed, 8 skipped**, floor clean, exit 0 |
| New tests | **+47** |
| Files | `tools/quality/pointers.py` (340), `config.py` (+24), two mirrors |
| Ceiling | ⭐ every file under R11 with headroom; **no exception requested** |

⚠️ **The 8 skips are the base's 8, unchanged and all named:** five are
`tests/docker/test_dev_image.py` refusing to rebuild the dev image from inside
it, and three are `tests/test_knowledge_index.py` with no corpus checked out
beside this repository.

## What landed

**`tools/quality/pointers.py`** — the parser and the check. `scan(root)` is one
pass; `check_pointers` reads its findings and `pointer_coverage` reads its
denominator, so the two channels can never describe different walks.

**`tools/quality/config.py`** — `markdown_files(root)`, the one narrowing the
task asked for. ⛔ **It is four lines and it is a filter over `text_files`**, not
a walk: acceptance 6 forbids a second file-walking helper, so exclusions,
git-ignore handling and sort order are inherited rather than restated.

**Registration** — `check_pointers` is the ninth entry in `CHECKS`;
`pointer_coverage` is the **second** entry in `NOTICES`, which had held exactly
one since `FND-07`.

**Mirrors** — `tools/tests/quality/test_pointers.py` (45 tests) and two added
to `test_config.py`.

### ⭐ Watched fail first, on the real tree, in both directions

⛔ **Acceptance 2 is not met by a fixture alone**, so it was run against the
repository itself: two deliberate pointers appended to `docs/tasks/BOARD.md`,
the floor run, the file restored, the floor run again.

```
document pointers: 37 read in 102 markdown files, 2 carrying an anchor, 2 unresolved.
docs/tasks/BOARD.md:2032: [pointer] points at 'docs/tasks/NO-SUCH-FILE.md' — no such file. …
docs/tasks/BOARD.md:2033: [anchor] points at anchor 'no-such-heading', which names no
                          heading in 'BOARD-ARCHIVE.md'. …
quality floor: 2 findings                                              (exit 1)

  … file restored …

document pointers: 35 read in 102 markdown files, 1 carrying an anchor, 0 unresolved.
quality floor: clean                                                   (exit 0)
```

⭐ **Both shapes fail, both name the file and the line, both paths are
repo-relative (R7).** The negative direction is the 11 measured mentions, held
**verbatim** in `MEASURED_MENTIONS` and asserted twice — collectively and one
shape per parametrised case.

### ⛔ Mutant sweep — Ruling 70's form, and the baseline survives at both ends

**Environment:** the pinned dev container (`docker/dev/check`), Python 3.14.7,
target sha `2926dc2`. **Cache purge:** every `__pycache__` outside `.git` and
`.pytest_cache` removed **before every row**, and `-p no:cacheprovider` on
every run. ⚠️ Ruling 40 is necessary but not sufficient — the checkout is
bind-mounted, so the image's `PYTHONDONTWRITEBYTECODE=1` cannot be relied on
alone. **Suite:** `tools/tests/quality/ tests/test_quality_floor.py`.

| row | verdict | summary | size |
|---|---|---|---|
| **BASELINE (before)** | ⭐ **SURVIVED** | 255 passed in 2.71s | — |
| M1 code spans are not stripped (**the task itself**) | ⛔ **KILLED** | 16 failed, 239 passed | same-size |
| M2 the fence state machine never toggles | ⛔ **KILLED** | 6 failed, 249 passed | same-size |
| M3 anchors are never resolved | ⛔ **KILLED** | 2 failed, 253 passed | same-size |
| M4 slugs keep their hyphen runs | ⛔ **KILLED** | 5 failed, 250 passed | same-size |
| M5 a link leaving the repository is accepted | ⛔ **KILLED** | 1 failed, 254 passed | same-size |
| **BASELINE (after)** | ⭐ **SURVIVED** | 255 passed in 2.76s | — |

⭐ **Five of five killed and five of five same-size** — each mutant padded with
a comment to the original line's exact length, so no mutation is detectable by
file size. ⛔ **M1 is the one that matters**: it is the task's whole thesis, and
removing span-stripping kills 16 tests rather than one.

## Decisions

### ⭐ 1. Slugs collapse runs of hyphens, and the tree's one real anchor is why

GitHub does not collapse: `## A — B` slugs to `a---b` there and `a-b` here.
⛔ **Nothing in this repository is ever pushed to any remote and no renderer is
authoritative over it**, so matching a hosting service's exact algorithm buys
nothing — and it would fail the tree's **one real anchor**, which points
unambiguously at a real heading and reads correctly to every human.

**Measured, both readings:**

```
heading  ## The wave checks — ⛔ **SIX at open, and check 4 AGAIN at close**
target   the-wave-checks-six-at-open-and-check-4-again-at-close
tolerant the-wave-checks-six-at-open-and-check-4-again-at-close   ✅ resolves
strict   the-wave-checks---six-at-open-and-check-4-again-at-close ⛔ 1 finding
```

⚠️ **The tolerant direction is also the safe one** for a check whose entire
thesis is that a false positive gets it switched off. See `FND-08/2`.

### ⭐ 2. `tests/fixtures/` is IN, by decision

The task said to choose deliberately and say which. It is in `EXCLUDED_DIRS`,
so a `python_files`-shaped walk would not see it — ⭐ **but this walk is
`text_files`-shaped, where `EXCLUDED_DIRS` never applied.** A fixture is allowed
to be *shaped* wrong, and `tests/fixtures/README.md` is prose a person reads.
⛔ **Measured before deciding: 8 markdown files there carrying 0 pointers**, so
including them costs no migration and closes the hole before one is written.

### ⭐ 3. A link that leaves the repository is a finding

R18 pins the sibling components and R20 makes the extraction one-way, so a link
reaching out of this checkout asserts something no checkout can guarantee.
⛔ **Measured: 0 in the tree**, so this costs no migration either.

### ⛔ 4. Walk 4 stayed refused and `FND-09` stayed out

Neither was folded in. E00 line 772's reason for `FND-09` being separate — its
output is a generator feeding a test, not a `Finding` — held on inspection:
nothing in this task's `Finding` seam would have carried `sweeping()`'s
attributed message.

## Surprises

### ⛔ Every founding number moved except the one the task was scoped on

⭐ **Re-run first, as instructed. Both readings:**

| | recorded on `e5bcc85` | ⛔ **re-measured on `2926dc2`** |
|---|---|---|
| markdown files | 90 | ⛔ **102** |
| links found, fence-aware | 41 | ⛔ **45** |
| apparent dangling, fence-aware only | 8 | ⛔ **11** |
| ⭐ true dangling, after code spans stripped | 0 | ⭐ **0** |
| false-positive rate of the naive walker | 8 of 8 | ⛔ **11 of 11 — 100 %** |
| links carrying an `#anchor` | 0 | ⛔ **1** |

⚠️ **The right-hand column is the base tree.** This handoff is itself a
markdown document, so the committed tree reads **103** — ⭐ **a founding number
moving inside the commit that founds it**, which is why the live figures are
printed by `pointer_coverage` rather than maintained by hand anywhere.

⭐ **The shape survived and the numbers did not** — which is exactly the claim
Ruling 55 makes. The migration is still `0`, the naive walker is still wrong
about *every single hit it reports*, and ⛔ **the check would still have been
switched off within a day without the span parser.**

⚠️ **The check's own steady-state reading is `35 pointers`, not `45`.** The two
instruments count different things and both are right: 45 is what a fence-aware
walker *finds*, 35 is what survives span-stripping (34 paths + 1 same-document
anchor). ⭐ **That gap of 10 is the parser, printed on every run** — which is
what makes Ruling 55 mechanical here rather than a thing the next agent has to
rebuild an instrument to learn.

### ⛔ "No link anywhere in this repository carries an anchor" is no longer true

The task's acceptance 4 asked for anchor resolution *"even though the tree
carries zero anchors today"*. ⭐ **It carries one** — `docs/tasks/BOARD.md:37`,
added since `e5bcc85` — so the speculative half of this check was exercised by
the tree on its first run rather than by a fixture alone. ⚠️ **A `0` scoped as
"and it will stay 0" lasted six commits.**

### ⭐ Ruling 73's distinction needed one extra layer here, and the tree proves it

`marker_lines` gets *"a table cell does not count"* for free, because a marker
in a cell has a lead word in front of it. ⛔ **A link has no such tell** —
`` | `[a](b.md)` | `` and `| [a](b.md) |` differ only by backticks — so the span
parser is load-bearing here in a way it was not there. **Three of the eleven
measured false positives are exactly that shape.**

⚠️ **And a fixed `` `[^`]*` `` pattern gets three more of them wrong**: the real
documents use a *double*-backtick span wrapping a single-backtick one, and a
fixed pattern reads the inner ticks as delimiters and strips the wrong half of
the line, leaving the link exposed. The span regex matches a variable-length
run for that reason, and `M1` in the sweep above is what proves it matters.

### ⚠️ Four ruff `D401` errors that the floor's own style check cannot see

The floor passed clean while `ruff check .` failed on four non-imperative
docstring first lines. ⛔ **`tests/test_repository.py` is what caught them**, not
`python3 -m tools.quality`. Fixed. Not a defect — `style.py` says in its own
contract that it is the standard-library subset and not a substitute — but
⚠️ **a developer who runs only the floor will hand the reviewer a red branch.**

## Findings

FND-08/1 `[local]` — **The naive walker's false-positive count is now a
printed number, not a document's claim.** `pointer_coverage` prints
`35 read in 102 markdown files` on every run. ⭐ Anyone re-pricing this walk
reads the current figure off the floor instead of rebuilding the instrument,
which is Ruling 55 made mechanical rather than remembered.

FND-08/2 `[structural]` — **The slug algorithm is a decision with one
customer, and the customer is the PO's file.** Hyphen-run collapse is what
makes `docs/tasks/BOARD.md:37` resolve; a strict GitHub-exact slugger produces
exactly **1** finding, in `BOARD.md`. ⛔ Adding or repairing anchors in
`BOARD.md` is out of scope for this task by its own *Out of scope* line, so the
decision was taken in the check rather than in the board. ⚠️ **If the PO would
rather the board carried GitHub-exact anchors, the change is one regex in
`pointers.slug` plus one anchor in `BOARD.md`** — and it should be one commit,
because Ruling 43 says a check owns its migration. **Routing: this is the PO's
call at wave-open, not a developer's.**

FND-08/3 `[structural]` — **Walk 4 is now unblocked and is a two-line
assertion, not a walk.** Anchor resolution ships and is exercised. ⛔ The
remaining blocker is unchanged and is still the PO's: `BOARD.md` carries 14
links into `BOARD-ARCHIVE.md` and **still 0 of them carry a fragment**, so the
inverse check — *the archive still holds the sections the board's prose claims
are in it* — remains unbuildable. ⭐ **The ordering the task predicted held
exactly**: the checker had to come first and the pointers have to gain
fragments second. **Routing: scheduled — it belongs to whoever adds the
anchors, and it is no longer blocked on any framework code.**

FND-08/4 `[local]` — **The floor and `ruff` disagree, and only the suite
knows.** Four `D401` errors passed `python3 -m tools.quality` and failed
`tests/test_repository.py`. ⚠️ Not a defect in either tool, but the developer
workflow *"run the floor, then commit"* is one a reviewer will receive red.
⭐ Cheapest fix if anyone wants one: the floor's notice channel could say
*"ruff is installed and was not run"*. **Routing: accepted — the cost is one
extra command, and the suite does catch it before review.**

## For dependents

⭐ **`FND-09` is unaffected.** Nothing here touched `tests/fixture_checks/`,
`test_blocks.py` or `archive_documents`. The shared primitive it was told to
reuse — walk-and-exclude — is `config.markdown_files`/`text_files`, and
`markdown_files` is the worked example of the narrowing it should copy:
⛔ **a filter over the shared walk, never a second walk.** The report is *not*
shared, exactly as Ruling 46 requires.

⭐ **Anyone adding a repository-wide check reads `pointers.py`'s docstring
first.** It carries the third distinct exemption mechanism this floor has —
neither a scan root, nor a list, nor a declaration, but **the parser**: a link
inside backticks is a *mention*, so a document is excused by saying what it
means rather than by being named somewhere. ⛔ That generalises `W20`'s
*exempt documents, never modules* one step further and it is the reason this
check has no allow-list and needs none.

⚠️ **Anyone writing a document that demonstrates a broken link** puts it in a
fence or in backticks. Both work, both are tested, and the check's own message
says so on the way out.

⛔ **Do not add a line to `tests/test_gate_coverage.py`.** It is untouched here
and remains the file nearest its ceiling.
