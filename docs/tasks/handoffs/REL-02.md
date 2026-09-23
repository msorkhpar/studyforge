# REL-02 — handoff

**Kind:** task handoff — REL-02

## Status

**done, self-certified against the epic.** Task `REL-02`, defined in
[`E15` § REL-02](../E15-release-ready.md#rel-02-the-product-suite-stands-without-the-tooling).
⭐ **An EPIC TASK, so it has no row file and nothing was minted.** Branch
`chore/REL-02-the-product-suite-stands-alone`, cut at `7f68b790`, with the release tip `0e590b06`
merged in. Office `dev5`. Milestone **M11**, step **11.2**.

⭐ **The one sentence:** the product's test suite now runs, GREEN, in a checkout with `tools/`,
`docs/tasks/` and `docs/conventions/` removed, and with the tooling present every gate runs every
test it ran before, unchanged.

⭐ **Author line declared:** every commit on this branch, the merge included, is
`dev5 <dev5@example.invalid>`, passed with `git -c`. ⛔ Nothing was written to any git config, no
remote was added and nothing was pushed. ⛔ Nothing was moved, deleted or archived; no tool was
edited.

## Gates

⛔ Each gate was run bare from `studyforge-wt/dev5` at the merge commit, its output sent to a
scratch file and `$?` read on the next line — never through a pipe.

| gate | environment | reading |
|---|---|---|
| `./docker/dev/check ruff check .` | pinned image | GREEN, exit 0 |
| `./docker/dev/check ruff format --check .` | pinned image | GREEN, exit 0 |
| `python3 -m tools.quality` | host | GREEN, exit 0 |
| `python3 -m pytest -n auto -q` | host | GREEN, exit 0 |
| `./docker/dev/check python3 -m pytest -n auto -q` | pinned image | GREEN, exit 0 |

## ⛔ The reading `E15` asks for, and the plants

⭐ **The scratch export.** A `git clone` of this branch into the office's scratch directory —
a clone and not a `git archive`, because `test_previous_reader.py` reads the previous reader out
of history and an archive carries none — then `git rm -r tools docs/tasks docs/conventions`,
committed, so the tree-state check has a clean `HEAD` to compare against. In it:

| command | reading |
|---|---|
| `python3 -m pytest tests -q -n auto --ignore=tests/studyforge/skills/delivery` (`E15`'s command) | GREEN, exit 0; the summary prints `process population: the tooling is ABSENT …` |
| `python3 -m pytest --co -q` (bare, so `testpaths` is read with `tools/tests` absent) | exit 0, and no `tools/` node collected |
| a planted test writing a file into the checkout's root | RED, exit 1, the stray file named by `tests/harness/treestate.py` |
| `import tools.quality` planted at the top of `tests/test_workspace_pin.py` | RED, exit 2: the file fails collection |

⭐ **And in a scratch clone WITH the tooling present**, the same plant turns
`tests/test_product_stands_alone.py::test_no_product_test_reaches_the_tooling` RED, exit 1,
naming the file and the line; with the plant removed it is GREEN, exit 0.

⭐ `git grep -nE '^\s*(from|import) tools' -- tests conftest.py` prints only the files and tests
declared process in [`tests/harness/process.py`](../../../tests/harness/process.py), plus the one
file `DEFERRED` names for `REL-06`. ⛔ It prints nothing for `conftest.py`.

## What landed

- ⭐ **[`tests/harness/process.py`](../../../tests/harness/process.py)** — the declaration of every
  process test: `FILES` (whole files), `TESTS` (single tests, a `[id]` suffix narrowing to one
  parametrisation), `DEFERRED` (product files another task re-points), `present(root)`,
  `declared(nodeid)`, `uncollected()` and `population_line(present)`.
- ⭐ **The root [`conftest.py`](../../../conftest.py)** imports no tooling. It registers a `process`
  marker, applies it from the declaration, and — only when `tools/` is absent — leaves a declared
  file uncollected (`pytest_ignore_collect`) and skips a declared test with its reason. Every run
  prints a `process population:` line after the unreachable population.
- ⭐ **Standard-library copies under `tests/harness/`**, each with its tests carried beside it:
  `treestate.py` (from `tools/treestate.py`), `skipped.py` (the unreachable population, from
  `tools/quality/report.py`), `workspace.py` (the pin READER and `workspace_root`, from
  `tools/workspace/`), `pinned.py` (from `tools/workspace/pinned.py`), `sources.py` (the R1
  registry, from `tools/quality/source_names.py`), `workspaces.py` (the synthetic-workspace test
  support), and `personal-data-shapes.json` (the shape table, from the convention's fence).
- ⭐ **[`tests/test_product_stands_alone.py`](../../../tests/test_product_stands_alone.py)** — the
  standing guard: an AST sweep of every file under `tests/` and the root conftest for an import
  of the tooling, static or through `import_module`/`__import__`, unless declared; its plants;
  and the declaration's integrity (every entry names a file and a test that exist, every
  deferred file still needs its entry).
- ⭐ **[`tests/test_process_twins.py`](../../../tests/test_process_twins.py)** — a PROCESS test: each
  copied definition is its original's source byte for byte, each copied constant its value, and
  the shape table the convention's table row for row.
- Re-pointed at the copies: `tests/harness/isolation.py` (its own walk), `test_runtimes.py`,
  `test_corpora.py`, `execute/container.py`, `execute/test_container.py`, `test_quiet_image.py`,
  `test_dependency_image.py`, `buildserve/test_narration.py`, `buildserve/test_thin.py`,
  `execution/test_contract.py`, `execution/test_init.py`, `execution/test_toolchain.py`,
  `personalarchive/test_thin.py`, `validate/test_nondestructive.py`, `test_spec_corpus_table.py`,
  `test_workspace_pin.py`, `tests/support.py` (the shape table). `test_fixture_exercise_rule.py`
  reads the epic inside its test, never at collection. `test_parallel_suite.py`'s control targets
  a product file instead of one of the tooling's tests. `test_authoring_reference.py` and
  `adapter/test_scaffold.py` import the tooling inside their one declared test.

## Decisions

- ⭐ **The tree-state exit condition became the PRODUCT suite's own.** Both measured instances it
  exists for (`SF-17/11`, `SF-28/2`) were a framework writer under test leaving a file in the
  checkout — a product defect — so the check has to hold wherever the product's tests run,
  including a checkout with no tooling. It was already standard library only, so it is carried
  verbatim, and `E15`'s *"a stray file planted during a run still fails the session"* is read in
  the export above. The unreachable population (`W158`) followed it for the same reason.
- ⭐ **The `reads_tree` RULE stays with the tooling.** It exists for the merge gate's selection,
  so without the tooling there is nothing to select for. ⛔ The conftest reaches it through ONE
  seam, `TREE_READERS = "tools.treereaders"`, imported by name only when `tools/` exists — and
  unguarded then, so a broken rule fails the run rather than quietly marking nothing. The
  marker's REGISTRATION stays in the conftest, because `--strict-markers` refuses a hand-written
  `@pytest.mark.reads_tree` without it. `test_product_stands_alone` asserts that seam is the
  conftest's only mention of the tooling.
- ⛔ **`testpaths` KEEPS `tools/tests`, which `E15`'s Definition says should go.** The merge gate's
  full-scope suite passes no path and reads `testpaths` (`tools/gates.py`, `scoped`), so dropping
  the root would stop every suite gate running the tooling's own tests while the tooling is still
  the merge authority — the brief's critical constraint forbids exactly that. ⭐ Measured: an
  absent root costs a tooling-less checkout nothing (bare collection above). The reason is in
  `pyproject.toml`'s comment; `REL-10`'s removal commit drops the entry with `tools/`.
- ⭐ **Copies, not moves**, because the brief forbids moving anything before `REL-10`. ⛔ Two copies
  nobody compares become two rules, so `test_process_twins.py` compares them; it is itself
  declared process and leaves with the originals.
- ⭐ **"The process is absent" is read off the `tools/` DIRECTORY only**, never off a missing
  document: a deleted epic in a working checkout must still turn its test red.
- ⭐ **A declared file is not collected; a declared test is skipped.** A file that imports the
  tooling at its top fails at import before any mark is read, so it cannot be skipped from
  inside; a single test in a product file can, and its skip reason reaches the unreachable
  population.

## Surprises

- ⚠️ **`E15`'s *"prints nothing"* over `tests` cannot hold before `REL-10`.** A process test that
  imports the tooling is still a file under `tests/` until `REL-10` moves it, and the delivery
  skill's `test_walkthrough.py` is `REL-06`'s. What holds now is the brief's form: the grep
  prints only declared process tests and the one deferred file.
- ⚠️ **Four product tests name the tooling as DATA, not by import**, and only the export found
  them: `gate_coverage/test_coverage.py` counts `tools` as a gated tree, and three tests in
  `test_fixture_sweeps.py` read `tools/tests/quality/personal_data/test_registry.py` as a fixture
  enforcer. ⭐ They are declared, and their reasons say they STAY (see *For dependents*).
- ⚠️ **A `git archive` export is not enough for this suite**: `test_previous_reader.py` needs the
  commit it reads the previous reader from. `REL-14`'s clean-checkout close should clone.

## Findings

| id | marker | where | what |
|---|---|---|---|
| `REL-02/1` | `[local]` | [`E15` § REL-02](../E15-release-ready.md#rel-02-the-product-suite-stands-without-the-tooling) | ⚠️ **The Definition's *"the test roots stop naming `tools/tests`"* conflicts with the merge gate reading `testpaths`.** Resolved here by keeping the root until `REL-10` (see *Decisions*). ⭐ For the register to confirm, not a user decision: no ruling is re-asked |
| `REL-02/2` | `[local]` | `tests/studyforge/skills/delivery/test_walkthrough.py` | ⚠️ **Still imports `tools.quality.source_names`**, and it is `REL-06`'s. `tests.harness.sources` now carries the same registry; `REL-06` can take it from there and remove the `DEFERRED` entry, which `test_product_stands_alone` then demands |
| `REL-02/3` | `[local]` | [`docs/conventions/personal-data-shapes.md`](../../conventions/personal-data-shapes.md) | ⚠️ **Ruling 47's one table has a product copy now**, `tests/harness/personal-data-shapes.json`, held equal by `test_process_twins.py`. `REL-08` places the convention; whichever side it lands on, one of the two copies should become a pointer to the other |

## For dependents

⭐ **The population is the declaration: [`tests/harness/process.py`](../../../tests/harness/process.py),
entry for entry.** It is listed here as it stands at this handoff's tip; ⛔ the file is the
authority if the two ever differ.

**`REL-10` — MOVE to the archive branch (whole files).** Each is never collected without the
tooling:

| file | why it is process |
|---|---|
| `tests/test_acceptance_clauses.py` | reads every epic under `docs/tasks/` |
| `tests/test_round_mint_collision_rule.py` | reads the delivery-flow convention and the board archive |
| `tests/test_rubric_exit_code_forms.py` | reads the review rubric |
| `tests/docker/test_dev_check_rubric_form.py` | reads the rubric and imports `tools.mergegate` |
| `tests/test_quality_floor.py` | runs the tooling's floor itself (`REL-03`: the product floor gets its own wrapper) |
| `tests/test_consumer_side_contract.py` | reads [`docs/conventions/commanded-pages.md`](../../conventions/commanded-pages.md) — ⚠️ if `REL-08` puts that convention on the product side, re-point this file instead of moving it |
| `tests/test_process_twins.py` | compares the product copies with their tooling originals |

**`REL-10` — MOVE or cut (single tests inside a product file).** Each is skipped, with its
reason, without the tooling:

| test | why |
|---|---|
| `tests/test_process_starts.py::test_the_epic_names_each_site_in_the_runners_definition` | reads `E05` |
| `tests/test_process_starts.py::test_the_epic_states_the_narrowed_sentence_and_its_exceptions` | reads `E05` |
| `tests/test_fixture_exercise_rule.py::test_each_document_cites_section_7_for_the_file_only_record[e06]` | reads `E06`; the `authoring-guide` case is product |
| `tests/studyforge/corpus/manifest/test_media.py::test_the_example_the_epic_publishes_parses` | reads `E04` |
| `tests/studyforge/corpus/manifest/test_media.py::test_the_epic_says_which_version_its_example_needs` | reads `E04` |

⛔ A test declared one-by-one does not move by moving its file, which is product. Delete the test
from the main line in the removal commit, and the archive branch keeps it byte for byte.

**`REL-03` — RE-POINT at the product floor.** Declared process today because they reach the
tooling's rule:

| test | re-point it at |
|---|---|
| `tests/test_authoring_reference.py::test_the_reference_carries_no_personal_data_shape` | the product's own R7 check |
| `tests/studyforge/skills/adapter/test_scaffold.py::test_the_ceiling_is_the_one_the_quality_floor_owns` | the product's own R11 ceiling |

⭐ Once re-pointed, remove the entry from `TESTS`; `test_product_stands_alone` will refuse the
tooling import if one is left behind.

**`REL-10` — STAY, with the tooling's row dropped in the removal commit.**

| test | the edit |
|---|---|
| `tests/gate_coverage/test_coverage.py::test_every_named_tree_is_populated_so_the_bound_is_not_vacuous` | drop the `"tools"` row from `tests/gate_coverage/__init__.py`'s `GATED_TREES` |
| `tests/test_fixture_sweeps.py::test_the_enforcers_are_named_in_the_code_and_state_why`, `::test_no_enforcer_imports_the_seam`, `::test_the_enforcers_still_read_the_tree_themselves` | re-point `tests/fixture_checks`' `ENFORCERS` entry for `tools/tests/quality/personal_data/test_registry.py` wherever `REL-03` puts that test, or drop it if it is archived |

**`REL-10` — and the rest of the removal commit.**

- Drop `"tools/tests"` from `testpaths` in `pyproject.toml`.
- Delete the conftest's `TREE_READERS` seam and `_tree_readers`; keep the `reads_tree` marker's
  registration while any test still carries it by hand.
- Empty `FILES`, `TESTS` and `DEFERRED` in `tests/harness/process.py` (or delete the module and
  its three call sites in the conftest). ⭐ `tests/harness/treestate.py`, `skipped.py`,
  `workspace.py`, `pinned.py`, `sources.py` and `workspaces.py` stay: they are the product's now.

**`REL-06`** — `tests/studyforge/skills/delivery/test_walkthrough.py` is the one `DEFERRED` file.
Read `KNOWN_SOURCES` and `named_sources` from `tests.harness.sources`, then remove the entry.

⛔ **The export reading needs a CLONE, not an archive** (see *Surprises*).
