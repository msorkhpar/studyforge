# REL-06 — handoff

**Kind:** task handoff — REL-06

## Status

**done, self-certified against the epic.** Task `REL-06`, defined in
[`E15` § REL-06](../E15-release-ready.md#rel-06-the-delivery-skill-reads-a-packaged-capability-index).
⭐ **An EPIC TASK, so it has no row file and nothing was minted.** Branch
`chore/REL-06-the-delivery-skill-reads-the-packaged-index`, cut at the release tip `3758d114` and
merged forward to `bed97114` (`REL-03`). Office `dev4`. Milestone **M11**, step **11.3**.

⭐ **The one sentence:** the capability index ships in the package beside the delivery skill, and
the skill's first command, `python3 -m studyforge.skills.delivery`, prints it byte for byte from
any directory, with no plan document anywhere.

⭐ **Author line declared:** every commit and the merge on this branch is
`dev4 <dev4@example.invalid>`, passed with `git -c`. ⛔ Nothing was written to any git config, no
remote was added, nothing was pushed, nothing was moved or deleted.

## Gates

⛔ Run bare from `studyforge-wt/dev4` at the tip carrying this handoff, output to a scratch
file and `$?` read on the next line — never through a pipe. The report to the register carries
each reading and its exit code; ⛔ no figure is copied here.

| gate | environment |
|---|---|
| `./docker/dev/check ruff check .` | pinned image |
| `./docker/dev/check ruff format --check .` | pinned image |
| `python3 -m tools.quality` | host |
| `python3 -m tests.floor` | host |
| `python3 -m pytest -n auto -q` | host |
| `./docker/dev/check python3 -m pytest -n auto -q` | pinned image — the wheel readings SKIP there, saying why (`REL-04/1`) |

## ⛔ The reading `E15` asks for, the control, and the plants

⭐ **The reading**, taken at `732fdd29`. A `git archive` of that commit into the office's scratch
directory (outside the checkout); in it `python3 -m pip wheel . --no-deps --no-build-isolation
--no-index` (the host's own setuptools, nothing fetched); a fresh `python3 -m venv` in scratch,
the wheel installed with `pip install --no-index --no-deps`. From an EMPTY directory, with
`PYTHONPATH` unset, no ancestor of it holding `docs/tasks`, and none inside the venv:

- `import studyforge` resolves inside the venv, never the checkout;
- `python3 -m studyforge.skills.delivery` exits 0, and `cmp` says its output is byte-identical
  to the committed [`src/studyforge/skills/delivery/capability-index.md`](../../../src/studyforge/skills/delivery/capability-index.md) AND to the committed
  [`docs/capability-index.md`](../../capability-index.md);
- the directory is still empty afterwards.

⭐ **The control.** The same build from a `git archive` of the release tip `3758d114`, into its
own fresh venv, from the same empty directory: `python3 -m studyforge.skills.delivery` exits 1
(*"is a package and cannot be directly executed"*); and that tip's OWN step-1 command, read out
of the [`SKILL.md`](../../../src/studyforge/skills/delivery/SKILL.md) its wheel ships (`python3 -m studyforge.skills.documents delivery`), exits 1
with `FileNotFoundError` on [`docs/tasks/README.md`](../README.md), printing nothing.

⭐ **`E15`'s export reading.** A `git clone` of the branch into scratch, then
`git rm -r tools docs/tasks docs/conventions`, committed: `python3 -m pytest
tests/studyforge/skills/delivery -q` is GREEN, exit 0, the thirteen epic- and handoff-reading
tests skipped with their declared reasons; the whole `tests` root there is GREEN, exit 0.
`grep -n "docs/tasks" src/studyforge/skills/delivery/SKILL.md` prints nothing (exit 1).

⭐ **The plants**, each restored from a copy taken before it:

- the index's line dropped from `[tool.setuptools.package-data]` → `test_packaged.py`'s
  declaration, wheel and installed-package readings RED (3 failed, exit 1); restored, GREEN;
- one byte of the shipped index changed (its title) → `test_walkthrough.py::
  test_the_shipped_index_is_exactly_what_the_generator_produces_today` and
  `test_packaged.py::test_the_documents_copy_is_the_shipped_one_while_it_exists` RED (exit 1);
  restored, GREEN. ⭐ That is the acceptance's *a hand-edit to it fails a test*.

## What landed

- **[`src/studyforge/skills/delivery/capability-index.md`](../../../src/studyforge/skills/delivery/capability-index.md)** — the generated index, the
  generator's output byte for byte (a copy of [`docs/capability-index.md`](../../capability-index.md), which was already
  asserted to be that).
- **`src/studyforge/skills/delivery/packaged.py`** — `NAME`, `INDEX` (`Path(__file__).resolve()
  .parent / NAME`), `packaged_index() -> str`, and `main(argv)`, which writes the file's BYTES
  and refuses any argument with `UNUSABLE`. `packaged_index` is on the package's surface.
- **`src/studyforge/skills/delivery/__main__.py`** — four lines on `packaged.main`.
- **[`SKILL.md`](../../../src/studyforge/skills/delivery/SKILL.md) step 1** — the command is `python3 -m studyforge.skills.delivery`; the generator
  `capability_index` is still named as the product code a plan of one's own calls.
- **`pyproject.toml`** — one `package-data` pattern, [`skills/delivery/capability-index.md`](../../../src/studyforge/skills/delivery/capability-index.md), the
  array written one pattern per line.
- **Tests.** `test_packaged.py` (the reader, the one-copy check, the declaration, the wheel and
  the installed package — the wheel built by `test_documents.build_wheel`, split out of that
  module's fixture so both build one way) and `test_main.py`. `test_walkthrough.py` reads the
  shipped index, runs step 1 from an empty `tmp_path` and compares bytes unstripped, resolves
  `-m` modules too, asserts the procedure names no `docs/tasks`, and takes `KNOWN_SOURCES` and
  `named_sources` from `tests.harness.sources` (`REL-02/2`). `test_init.py` excuses `packaged.py`
  for `pathlib` alone, and a new test holds that every `Path(...)` in it is built from
  `__file__`.
- **`tests/harness/process.py`** — `DEFERRED` is empty; twelve live-epic readings (three in
  `test_walkthrough.py`, nine in `test_capability.py`) are declared under a new reason
  `LIVE_EPICS`, and the `QA-04` handoff reading under a new reason `HANDOFF`.
  `tests/test_product_stands_alone.py`'s deferred check loops rather than parametrises, so an
  empty `DEFERRED` prints no skip.
- **`test_findings_log.py`** (`REL-01/2`) — the handoff half of the slot test is its own test,
  declared process; the catalogue-section check reads the section's name out of [`SKILL.md`](../../../src/studyforge/skills/delivery/SKILL.md)
  (*"the catalogue's own \*…\* section"*) and finds it among the catalogue's `## ` headings, so
  a rewrite of that prose stays green exactly while the two agree.

## Decisions

- ⭐ **`python3 -m studyforge.skills.delivery`, writing bytes.** `print()` of a `-c` string
  re-encodes through the locale; writing the file's bytes makes *byte for byte* true by
  construction, the rule `studyforge.skills.documents` already keeps.
- ⭐ **The live-epic readings are declared process, not skipped on a missing document.**
  `process.py` reads absence off the tooling directory only, so a deleted epic in a working
  checkout still turns them RED. They stay in the tree through `REL-10` (the epics are still
  there) and `REL-11` decides what replaces them — see *For dependents*.
- ⭐ **The regeneration test kept its name and its file** (`test_walkthrough.py`), re-pointed at
  the shipped file, so every citation of it still resolves.
- ⚠️ **[`docs/capability-index.md`](../../capability-index.md) stays** — `REL-11` owns it. While both exist,
  `test_the_documents_copy_is_the_shipped_one_while_it_exists` holds them to the same bytes,
  and it passes vacuously once the copy is gone, by design.

## Surprises

- ⚠️ **The delivery package's own filesystem test forbade `pathlib` everywhere in it**
  (*"every module here is handed text"*). A packaged file cannot be read without it, so the
  excuse is by module and by name, and anchored by an `ast` test on `__file__`.
- ⚠️ **In `REL-02`'s export, ten delivery tests were already RED at the release tip** (nine
  live-epic readings in `test_capability.py` and the `QA-04` handoff read); the walkthrough had
  simply not been collected there. All are now declared.

## Findings

| id | marker | where | what |
|---|---|---|---|
| `REL-06/1` | `[local]` | [`CLAUDE.md`](../../../CLAUDE.md), [`README.md`](../../../README.md) | Both still send a reader to [`docs/capability-index.md`](../../capability-index.md) for counts. `REL-11` owns both and removes that file; the shipped index is `python3 -m studyforge.skills.delivery` |
| `REL-06/2` | `[local]` | `tools/quality/board/delivery.py` | The board's delivery reading opens [`docs/capability-index.md`](../../capability-index.md) by path. It is process tooling and leaves with `REL-10`; if it must outlive `REL-11`'s removal of that file, it reads the shipped one instead |

## For dependents

- ⭐ **`REL-10` (the removal commit):** the twelve `LIVE_EPICS` entries and the one `HANDOFF`
  entry in `tests/harness/process.py` are ⛔ **not** tooling. The epics are still on the main
  line after your cut, so the `LIVE_EPICS` tests keep running there; when you empty
  `TESTS`, keep them (they need no tooling). The `HANDOFF` test
  (`test_findings_log.py::test_the_question_is_the_sorts_own_words`) MOVES with the handoffs.
- ⛔ **`REL-11` (the epics trimmed):** the trim removes the task blocks the `LIVE_EPICS`
  readings parse, so in the same commit ⭐ **they must be replaced, never left to fail or
  dropped silently**. The shipped index is then frozen, and the regeneration test is the only
  thing that fails a hand-edit — replace it with a pinned `sha256` of
  [`src/studyforge/skills/delivery/capability-index.md`](../../../src/studyforge/skills/delivery/capability-index.md) in `test_packaged.py` (zero cost once
  nothing regenerates it), or regenerate from the archive branch's epics. The other eleven
  readings test the generator on the live population; the small fixtures in `plans.py` already
  cover the generator, so they may move to the archive with the task text. Removing
  [`docs/capability-index.md`](../../capability-index.md) is yours; `test_the_documents_copy_is_the_shipped_one_while_it_exists`
  needs no change.
- ⭐ **Anyone who changes an epic's task block before `REL-11`:** regenerate BOTH copies (the
  generator's output, byte for byte); the failure message of the regeneration test names the
  three documents it is handed.
- ⛔ **Re-measure; never copy a figure from this handoff.**
