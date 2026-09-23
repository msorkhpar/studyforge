# REL-03 — handoff

**Kind:** task handoff — REL-03

## Status

**done, self-certified against the epic.** Task `REL-03`, defined in
[`E15` § REL-03](../E15-release-ready.md#rel-03-the-product-floor-is-the-products).
⭐ **An EPIC TASK, so it has no row file and nothing was minted.** Branch
`chore/REL-03-the-product-floor-is-the-products`, cut at the release tip `f3f5485a`. Office `dev6`.
Milestone **M11**, step **11.2**.

⭐ **The one sentence:** the product's rules now have a home of their own under `tests/floor/`,
standard library only, run by `python3 -m tests.floor` and by the product suite, and they run and
go red in a checkout with `tools/`, `docs/tasks/` and `docs/conventions/` removed; `tools/quality`
is untouched and is still the merge authority.

⭐ **Author line declared:** every commit on this branch is `dev6 <dev6@example.invalid>`, passed
with `git -c`. ⛔ Nothing was written to any git config, no remote was added and nothing was
pushed. ⛔ Nothing was moved, deleted or archived; no file under `tools/` was edited.

## Gates

⛔ Each gate was run bare from `studyforge-wt/dev6` at this branch's tip, its output sent to a
scratch file and `$?` read on the next line — never through a pipe.

| gate | environment | reading |
|---|---|---|
| `./docker/dev/check ruff check .` | pinned image | GREEN, exit 0 |
| `./docker/dev/check ruff format --check .` | pinned image | GREEN, exit 0 |
| `python3 -m tools.quality` | host | GREEN, exit 0 |
| `python3 -m pytest -n auto -q` | host | GREEN, exit 0 |
| `./docker/dev/check python3 -m pytest -n auto -q` | pinned image | GREEN, exit 0 |

## ⛔ The reading `E15` asks for, and the plants

⭐ **The scratch export is `REL-02`'s:** a `git clone` of this branch into the office's scratch
directory, then `git rm -r tools docs/tasks docs/conventions`, committed. In it:

| command | reading |
|---|---|
| `python3 -m tests.floor` on the unplanted export | GREEN, exit 0 |
| `python3 -m pytest tests -q -n auto --ignore=tests/studyforge/skills/delivery` | GREEN, exit 0 |
| R11 plant: a 401-line module under `src/studyforge/`, with a contract and a mirrored test | RED, exit 1, one `[size]` finding naming the file |
| R7 plant: a home path under a fabricated placeholder account, in `docs/notes.md` | RED, exit 1, one `[personal-data]` finding; the value is not printed |
| R12 plant: a module under `src/studyforge/` with a contract and no mirrored test | RED, exit 1, one `[mirror]` finding naming the test it owes |
| R17 plant: a mirrored module under `src/studyforge/` with no module docstring | RED, exit 1, one `[contract]` finding |
| the R12 plant again, run through the suite's wrapper `tests/floor/test_init.py` | RED, exit 1 |

⭐ Each plant was made on a clean reset of the export and removed before the next. ⭐ The same
four plants, plus an R1 plant (a corpus named in framework source), are carried as a standing
test in [`tests/floor/test_main.py`](../../../tests/floor/test_main.py), each refused through a
real `python3 -m tests.floor` subprocess.

⭐ **With the tooling present**, in a scratch clone of the full tree: the R12 plant turns
`python3 -m tools.quality` RED, exit 1, with the same `[mirror]` finding, so the tooling's floor
still refuses exactly as before. And a one-character drift planted in the product copy
(`SOURCE_LINE_CEILING` in `tests/floor/config.py`) turns `tests/test_floor_twins.py` RED, exit 1;
restored, it is GREEN, exit 0.

## The sort

⭐ **Every check and notice `tools.quality` registers, and its side.** ⛔ The table is also CODE:
`tests/test_floor_twins.py` holds `PROCESS` and `DEFERRED` with these reasons and fails when a
tooling check has no side, so this table cannot drift from the registry while both exist.

| tooling check or notice | side | the rule, or why it is process |
|---|---|---|
| `check_sizes` (`size.py`) | ⭐ **product** | R11, the size ceiling, Python and the authored stylesheets, scripts and templates |
| `check_mirrors` (`mirror.py`) | ⭐ **product** | R12, the mirrored test |
| `check_docstrings` (`docstrings.py`) | ⭐ **product** | R17, the module contract |
| `check_style` (`style.py`) | ⭐ **product** | the standard-library style layer: line endings, tabs, trailing space, final newline, line length |
| `check_personal_data` (`personal_data/`) | ⭐ **product** | R7: the shapes arm, the negative-fixture registry arm and the identifier arm |
| `check_source_names` (`source_names.py`) | ⭐ **product** | R1, framework source names no corpus |
| `check_producer_half` (`surfaces.py`, `deviations.py`) | ⭐ **product** | a name one package takes from another is on the owner's `__all__` (Ruling 101) |
| `surface_census`, `identity_notice` | ⭐ **product** | the denominators of the producer half and of R7's identifier arm |
| `check_rejected_palettes`, `palette_census` (`palettes/`) | ⚠️ **product, DEFERRED to `REL-08`** | the UI identity; it reads `docs/conventions/ui-design.md`'s table, whose product home `REL-08` decides (`REL-03/2`) |
| `vacuity_notice` | process | the tooling's registry of its own checks — the product floor has its OWN `tests/floor/vacuity.py` |
| `approach_notice` | process | R11's approach, but read off branches and offices in git history |
| `lint_notice` | process | what ruff said; the product enforces lint in `tests/test_repository.py` already |
| `check_board`, `board_state` | process | the board as a register |
| `check_handoffs`, `handoff_citations`, `check_handoff_existence`, `handoff_existence`, `check_marker_patterns` | process | handoffs and finding markers |
| `check_rulings_index`, `rulings_notice`, `check_rulings_reach`, `reach_notice` | process | rulings |
| `check_pointers`, `pointer_coverage`, `check_anchor_collisions`, `collision_census`, `location_notice` | process | links between the process documents (`REL-03/5`) |
| `check_clause_counts`, `clause_census` | process | the conventions' stated clause counts |
| `check_derived_counts`, `count_census` | process | a figure in prose must name the ref it was measured at |
| `check_owns_before_creator`, `creator_census` | process | the plan's graph |

⭐ **And the modules that are no check at all:** `config.py` and `report.py` are copied (the
product checks need them); `tools/reserved_addresses.py` is copied (R7's shapes arm reads it);
`certify.py`, `subject.py`, `trial.py`, `gated.py`, `citations.py`, `ids.py`, `markdown.py`,
`plan_parse.py`, `board/`, `handoffs/`, `rulings/`, `clauses.py`, `counts.py`, `creators.py`,
`reach.py`, `pointers.py`, `collisions.py`, `locations.py`, `approach.py`, `lint.py`, `vacuity.py`,
`__init__.py` and `__main__.py` stay with the tooling.

## What landed

- ⭐ **[`tests/floor/`](../../../tests/floor/__init__.py)** — the product floor. `CHECKS` (the seven
  product checks), `NOTICES` (`surface_census`, `vacuity_notice`, `identity_notice`), `run_all`,
  `run_notices`. **The command is `python3 -m tests.floor [--root PATH]`**: it exits 1 on any
  finding, and its last line says it is not the suite.
- ⭐ **Copies, module for module, of** `tools/quality/{config,report,size,mirror,docstrings,style,
  source_names,surfaces,deviations}.py`, `tools/quality/personal_data/{__init__,shapes,registry,
  identity}.py` and `tools/reserved_addresses.py`. Only the imports were rewritten, and each
  docstring gained one paragraph saying what the copy is.
- ⭐ **[`tests/floor/vacuity.py`](../../../tests/floor/vacuity.py)** — the product floor's own
  answer for an empty run, shaped as the tooling's and naming the product's checks only.
- ⭐ **The plants moved with their checks**: the tooling's mirrors of those modules were ported
  under `tests/floor/` (imports rewritten; a test about a tooling path was pointed at the
  product's own file), plus `test_init.py` (the suite's wrapper over the whole tree, the registry
  and a standard-library-only import sweep), `test_main.py` (the plants through the command) and
  `test_vacuity.py`.
- ⭐ **[`tests/test_floor_twins.py`](../../../tests/test_floor_twins.py)** — a PROCESS test, declared
  in [`tests/harness/process.py`](../../../tests/harness/process.py)'s `FILES`: each copy's code
  is its original's (docstrings stripped, imports compared as a set under the one declared
  rewrite), with a plant proving it goes red on a code drift and stays green on a prose one; and
  the sort, as code.
- ⭐ **`REL-02`'s two re-points**: `tests/test_authoring_reference.py::test_the_reference_carries_no_personal_data_shape`
  reads `tests.floor.personal_data.shapes`, and
  `tests/studyforge/skills/adapter/test_scaffold.py::test_the_ceiling_is_the_one_the_quality_floor_owns`
  reads `tests.floor.config.SOURCE_LINE_CEILING`, both at the top of the file. Their `TESTS`
  entries and the `R7`/`R11` reasons are gone from the declaration.

## Decisions

- ⭐ **The home is `tests/floor/`, not `src/` and not a `dev` extra.** `src/` would make the
  floor shipped, versioned API (the tooling's own docstring records why that was ruled out), and
  an extra declares dependencies, of which a standard-library floor has none. Under `tests/` it
  travels with the product suite, is never packaged, and the suite runs it on every checkout.
  ⛔ **`pyproject.toml` was not touched.**
- ⭐ **Twins, not pointing the tooling at the copy.** Three reasons. (1) The tooling is the merge
  authority, and it must go red exactly as it does today: with twins, not one byte of
  `tools/quality` changed, so "every gate is unchanged" is true by construction, not by a reading.
  Pointing would have rewritten a dozen of its imports and moved the target of every
  `monkeypatch` in its tests. (2) Pointing would make the tooling import from `tests/` for as
  long as the two share a line — and that is only until `REL-10`, when the tooling leaves and the
  single definition would come anyway. (3) It is `REL-02`'s pattern, so the milestone has one
  mechanism and `REL-10` deletes one kind of test.
- ⭐ **The twins compare CODE, not text** — the parse with every docstring stripped. That leaves
  the prose free for `REL-09` to rewrite in `tests/floor/` without touching the tooling, and it
  still catches a one-character change to a constant, a pattern or a message.
- ⭐ **The product `config.py` keeps the tooling's `tools` entries in `SCAN_ROOTS`, `TEST_ROOTS`
  and `MIRRORS`.** A byte-for-byte copy is the proof that nothing got weaker; an absent root is
  skipped (`python_files` reads only directories that exist), so the entries cost a tree without
  the tooling nothing, and with the tooling present the product floor is a subset of the
  tooling's. `REL-10` drops them (see *For dependents*).
- ⭐ **R1, the producer half and the style layer are product too**, not only the four rules the
  task names: each binds `src/`, and none reads a process document.

## Surprises

- ⚠️ **Two ported tests passed on the full tree and FAILED in the export**, because they named
  tooling files as evidence that the walk works (`tests/floor/test_config.py`). They now name
  the product's own files. ⭐ This is `REL-02`'s surprise again: only the export found them.
- ⚠️ **The product floor is fast.** It runs in seconds, where the tooling's floor takes about a
  minute: almost all of the tooling's time is its process checks.

## Findings

| id | marker | where | what |
|---|---|---|---|
| `REL-03/1` | `[local]` | [`E15` § REL-03](../E15-release-ready.md#rel-03-the-product-floor-is-the-products) | ⚠️ **The Acceptance says *"a public function with no contract"*; R17's floor check reads the MODULE docstring**, and a function's docstring is ruff's `D` rules in `tests/test_repository.py`, which needs the `lint` extra. The plant here is the brief's: a module missing its contract. Neither check was changed |
| `REL-03/2` | `[local]` | `tools/quality/palettes/` | ⚠️ **`check_rejected_palettes` is a PRODUCT check with no product home yet.** It reads `docs/conventions/ui-design.md`, and `REL-08` decides where that table lives. ⛔ `REL-10` must not remove `tools/quality/palettes/` before `REL-08` has homed its table and the check has been copied under `tests/floor/` and registered in `CHECKS` (one entry; `test_floor_twins.py`'s `DEFERRED` then loses its two entries) |
| `REL-03/3` | `[local]` | [`module-structure.md`](../../conventions/module-structure.md), `pyproject.toml`'s ruff comment | ⚠️ **Both name `tools/quality/` and `tests/test_quality_floor.py` as the floor.** Product prose; `REL-08` (the convention) and whoever owns the comment re-point them at `python3 -m tests.floor` |
| `REL-03/4` | `[local]` | `tests/harness/sources.py`, `tests/floor/source_names.py` | ⚠️ **R1's registry has two product copies now**: `REL-02`'s, for the product tests, and the floor's. `tests/floor/test_source_names.py` asserts they are the same registry, and that test stays after `REL-10`. One could become an import of the other |
| `REL-03/5` | `[local]` | `tools/quality/pointers.py`, `collisions.py`, `locations.py` | ⚠️ **Link integrity leaves with the tooling.** It is process here because it walks every document and most of them leave; after `REL-10` a broken link in `README.md`, the spec or `docs/authoring/` has no floor check. For `REL-10` or `REL-14` to decide whether the product needs a narrower one |

## For dependents

**`REL-10` — the removal commit.**

- Move `tests/test_floor_twins.py` with the tooling. It is in `tests/harness/process.py`'s `FILES`.
- In `tests/floor/config.py`, drop the `tools` entries from `SCAN_ROOTS`, `TEST_ROOTS` and
  `MIRRORS`. ⛔ Not before: the twins test compares them. Then drop the mirror tests about the
  tooling's layout: `test_tools_mirrors_itself_beside_itself` and
  `test_the_tooling_passes_with_its_mirror_beside_it` in `tests/floor/test_mirror.py`,
  `test_tools_are_held_to_the_same_contract` in `tests/floor/test_docstrings.py`, and
  `test_test_files_get_the_test_ceiling`'s tooling rows in `tests/floor/test_config.py`.
  ⭐ They pass without the tooling (they build their trees under `tmp_path`); they just stop
  being about anything.
- ⛔ **`tests/test_quality_floor.py` leaves; `tests/floor/test_init.py` is the product's wrapper
  that stays.**
- `tests/fixture_checks`' `ENFORCERS` entry for `tools/tests/quality/personal_data/test_registry.py`:
  its product twin is `tests/floor/personal_data/test_registry.py`. Re-point the entry there.
- ⛔ **`tools/quality/palettes/` is `REL-03/2`'s**: do not remove it before its product home exists.
- ⭐ After the cut, the product floor is `python3 -m tests.floor`, GREEN on the main line. It is
  the reading `REL-10`'s and `REL-14`'s *"the product floor is GREEN with no `tools/` present"* take.

**`REL-08`** — `REL-03/2` (the palettes table) and `REL-03/3` (`module-structure.md` names the
tooling's floor). ⭐ When `ui-design.md`'s table has a home, the palettes check copies into
`tests/floor/palettes/` the same way the others did, with its `UI_CONVENTION` path re-pointed.

**`REL-09`** — the copies under `tests/floor/` carry the tooling's docstrings, row and ruling ids
included, so they add to the population `REL-01`'s command prints. ⭐ The twins test ignores
docstrings, so rewriting that prose does not touch `tools/` and does not turn anything red.
