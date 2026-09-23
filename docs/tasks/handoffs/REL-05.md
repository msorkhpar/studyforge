# REL-05 — handoff

**Kind:** task handoff — REL-05

## Status

**done, self-certified against the epic.** Task `REL-05`, defined in
[`E15` § REL-05](../E15-release-ready.md#rel-05-onboarding-pins-the-installed-library-not-a-sibling-checkout).
⭐ **An EPIC TASK, so it has no row file and nothing was minted.** Branch
`chore/REL-05-onboarding-pins-the-installed-library`, cut at the release tip `3758d114`, with the
release tip `bed97114` (REL-03) merged in by a signed merge commit. Office `dev3`. Milestone
**M11**, step **11.3**.

⭐ **The one sentence:** a corpus now records the INSTALLED library's version and the commit it was
built from, every skill stub names the command that prints its procedure from the installed
package, and the generated pin check asks the installed library — nothing onboarding writes names a
path to a framework checkout.

⭐ **Author line declared:** every commit on this branch is `dev3 <dev3@example.invalid>`, passed
with `git -c`. ⛔ Nothing was written to any git config, no remote was added, nothing was pushed.
⛔ The ISO corpus was read and exported to scratch, never written.

## Gates

⛔ Each gate was run bare from `studyforge-wt/dev3` at the merge commit `02d3b76a`, its output sent to
a scratch file and `$?` read on the next line — never through a pipe.

| gate | environment | reading |
|---|---|---|
| `./docker/dev/check ruff check .` | pinned image | GREEN, exit 0 |
| `./docker/dev/check ruff format --check .` | pinned image | GREEN, exit 0 |
| `python3 -m tools.quality` | host | GREEN, exit 0 |
| `python3 -m tests.floor` | host | GREEN, exit 0 |
| `python3 -m pytest -n auto -q` | host | GREEN, exit 0 |
| `./docker/dev/check python3 -m pytest -n auto -q` | pinned image | GREEN, exit 0 — the two installed-wheel tests SKIP there, saying why (`REL-04/1`: no build backend in the image) |

⚠️ A first host run at `0eb50d72` was RED on `Errno 122` (disk quota) across `tools/tests/`, a
shared `/tmp` filled by concurrent offices; re-run once space returned, GREEN. It also surfaced the
one real defect, fixed before the merge: see *Surprises*.

## ⛔ The reading `E15` asks for, the control, and the plant

⭐ **The reading**, at `02d3b76a`, by a script in the office's scratch directory: a `git archive` of
that commit; a wheel built from it with the host's own setuptools (nothing fetched), and the export
DELETED; a fresh `python3 -m venv` in scratch, the wheel installed with `pip install --no-index
--no-deps`; a directory `work/` holding ONLY the fixture corpus (`corpora.material`, the settled
draft). With `PYTHONPATH` unset and the venv first on `PATH`, from the corpus root:

- `import studyforge` resolves inside the venv; `ls ..` prints `corpus` and nothing else;
- the settled draft onboards with the installed library and writes; the pin reads
  `"where": "installed"`, `"version": "0.1.0"`, the commit passed;
- **every fenced line of the corpus's reader document (`artifacts.READER_DOC`) exits 0** — the verify command, the skill-document
  listing, the adapter's ingest, `validate`, `plan`, `build`, `narrate --help` and the standing;
- the command the onboarding stub names prints bytes **identical to the wheel's** copy of the onboarding
  skill document;
- the generated `tests/test_framework_pin.py`, every test in it run as the corpus's suite would,
  passes — against the installed library.

⭐ The same reading is a test on the host: `tests/studyforge/skills/onboarding/verify/test_init.py`
builds a wheel from an export, installs it into a `--without-pip` venv outside the checkout, and
asserts all of the above plus that the installed pin check and the verify command both fail on a
pin naming another version.

⭐ **The control.** The same script at the release tip `bed97114`: `onboard(...).write('.')` raises
`PinRefused: there is no framework checkout where the pin looks for one, a sibling named
'studyforge' beside the corpus's main checkout…`, and nothing is written (no reader document, no
`.studyforge/`). Its `pin.stub` addresses the procedure as
`` `../studyforge/src/studyforge/skills/onboarding/SKILL.md` ``.

⭐ **The plant.** `pin.stub`'s command line replaced with the tree path
`../studyforge/src/studyforge/skills/{name}/SKILL.md`, restored from a copy taken before it:
`test_no_generated_document_reaches_the_framework_by_path`,
`test_a_stub_carries_the_pin_and_names_the_installed_command_never_a_path`,
`test_every_stub_names_a_command_that_prints_its_procedure_from_the_package`, the delivery skill's
`test_the_stub_a_corpus_receives_points_at_a_procedure_that_names_the_log`, and the installed-wheel
reading went RED; restored, all GREEN and `git status` clean. ⭐ And the corpus side:
`test_a_stub_pointed_back_at_a_tree_path_fails_the_generated_test` keeps the sibling-shaped stub as
a standing negative against the generated drift check.

⭐ **`E15`'s grep.** `git grep -n '\.\./studyforge' -- src/studyforge/skills` prints nothing, exit 1.

## What landed

- **`onboarding/pin.py`** — `pin_document(commit, version, skills)` writes `pin_api: 2`,
  `where: "installed"`, `version`, `commit`; `stub(name, commit, version)` writes `pin:` and
  `version:` lines, then the two commands (`DOCUMENTS`: `python3 -m studyforge.skills.documents
  <name>`; `VERIFY`: `python3 -m studyforge.skills.onboarding.verify .`) and no path;
  `check_version` refuses a non-version without quoting it (R7). `pin_test(skills)` is the new
  generated check: the pin's shape, **the installed library is the pinned version**, **every stub
  names a skill the installed library ships** (`documents.names()`), no stub drifted from the pin's
  commit OR version, no submodule. ⛔ `SIBLING`, `PROCEDURE`, `main_checkout`, `framework_of`,
  `check_held` and the git lookups are gone: `pin.py` starts no process now.
- **`onboarding/library.py`** (new) — `version()` reads the loaded `studyforge`'s version: the
  `studyforge-*.dist-info/METADATA` beside the package (a wheel install), else the `pyproject.toml`
  of a `src/`-layout tree above it (a checkout or an editable install); two distributions or
  neither is `LibraryRefused` by name. `pinned(root)` reads a pin back through the R7 gate and
  refuses one that predates this task. ⛔ No `importlib` (the isolation test's rule).
- **`onboarding/verify/`** (new package, `__init__` + `__main__`) —
  `python3 -m studyforge.skills.onboarding.verify [ROOT]`: prints the installed version; with a
  root, exit 0 when the pin names it, 1 when it names another, `UNUSABLE` with a sentence otherwise.
- **`onboard`** reads the running library's version (refusing by name if it cannot), pins it, and
  `write` refuses a pin naming another version than the library running it. The report prints
  `framework  studyforge <version>, built from <commit>`.
- **`reonboard`** reads a `pin_api 1` (sibling) pin's commit and skills, and without
  `framework_commit` refuses to keep it — and refuses to keep a pin naming another version than
  the one running. With `framework_commit` it migrates.
- **`artifacts.reader_document(..., commit, version)`** — the fresh-clone section says the
  framework is the installed library at `version`, built from `commit`; install is said in prose
  (a wheel's location is the reader's); every fence reaches the library by module name, with no
  `PYTHONPATH`.
- **The onboarding skill's [`SKILL.md`](../../../src/studyforge/skills/onboarding/SKILL.md)** — *Before you start* says install the library; the stubs, the verify command,
  what is verified and what is recorded, and how a sibling-pinned corpus migrates.
- Tests: `test_pin.py`, `test_library.py`, `verify/test_init.py`, `verify/test_main.py` and the
  `wheels.py` helper; `test_artifacts`, `test_onboard`, `test_reonboard` and `corpora` rewritten
  for no sibling; three outside callers of the fixture or the stub (see *Decisions*).

## Decisions

- ⭐ **The version is verified; the commit is recorded.** A wheel carries no git history, so
  nothing can say whether an installed library holds a commit — `W270`'s check needed a checkout
  and retired with it. The commit is the operator's statement, shape-checked. See `REL-05/1`.
- ⭐ **The version is read from the LOADED package, never from `importlib.metadata`.** The
  isolation test refuses every `importlib` import in `src`, and reading beside the loaded package
  also means a stale distribution elsewhere on `sys.path` cannot answer for code that is not the
  one running. The `pyproject.toml` fallback is what lets this framework's own suite, an editable
  install and a `PYTHONPATH` checkout all onboard — the path is resolved at run time and never
  written (R7).
- ⭐ **The generated check calls the installed library's own `version()` and
  `documents.names()`**, rather than carrying a copy of the rule (the `W286` pattern), because the
  question IS "what does the installed library say". A missing library is an assertion with a
  sentence, not a collection error.
- ⭐ **`verify` is a package with a `__main__`, not a module with a guard.** Two reasons, both
  measured: `onboard` imports `library`, so `-m` on it warned about a double import on every run;
  and the commanded-page check refuses a `python3 -m` form whose `__main__` does not resolve (see
  `REL-05/2`).
- ⛔ **Three files outside Owns changed, each only because it tested this skill's output:**
  `tests/test_process_starts.py` drops `skills/onboarding/pin.py` from its named process sites
  (it starts none now, and the site test would fail); `tests/studyforge/skills/delivery/test_findings_log.py`
  follows the stub's command through the locator instead of a `../studyforge` regex;
  `tests/studyforge/skills/reconnaissance/test_furniture.py` stops building a synthetic sibling.

## Surprises

- ⚠️ **The commanded-page check cannot see a plain runnable module.** The first full host run went
  RED on `test_every_command_the_reference_gives_names_a_module_that_can_be_run` because
  the onboarding [`SKILL.md`](../../../src/studyforge/skills/onboarding/SKILL.md) gave `python3 -m studyforge.skills.documents onboarding` — `REL-04`'s own command —
  and the check asks `find_spec('<name>.__main__')`. Fixed inside Owns: the skill document names the
  locator in prose, and `verify` is a package. See `REL-05/2`.
- ⚠️ **The ISO corpus's pin check was already RED at its `06df27f`**, before this task
  (`test_no_stub_has_drifted_from_the_pin`: the pin advanced to `638e233e`, the stubs still at
  `aa4e2569`). By `acde021` it reads green again. Not caused here; recorded because the constraint
  was "keep passing".

## Findings

| id | marker | where | what |
|---|---|---|---|
| `REL-05/1` | `[local]` | `pyproject.toml` build, owner of packaging | ⚠️ **The wheel carries no commit**, so a pin's `commit` is the operator's word, checked for shape only. A build-time stamp (a generated module or a metadata field) would let `library` and the generated check verify it too. Not a user decision |
| `REL-05/2` | `[local]` | `tests/authoring/support.py` `resolves` / `test_every_command_the_reference_gives_names_a_module_that_can_be_run` | ⚠️ **A plain module run with `-m` is refused as "not runnable"** (it asks for `<name>.__main__`), so no commanded page can give `python3 -m studyforge.skills.documents <name>`, which runs. `REL-07`'s README will meet it if README joins the commanded pages |
| `REL-05/3` | `[local]` | [`docs/decisions.md`](../../decisions.md) — the decision naming `pin.SIBLING` and `git cat-file -e` | ⚠️ **Stale at this merge**: the pin is the installed library's version and commit, checked by version, and no document addresses the framework by path. Whoever owns the decisions file carries the new decision |
| `REL-05/4` | `[local]` | [`E05`](../E05-serving-execution.md) `SF-20`, "save two named sites" | ⚠️ **One named process site is left** (`validate/source/enumeration.py`); `pin.py` no longer starts git. The test still passes on the sentence; the sentence is now false. `REL-11` trims the epic anyway |

## For dependents

- ⭐ **`REL-07` (the README):** the install story a corpus is told is the wheel, built locally and
  installed with `python3 -m pip install --no-index <the wheel>`; the two commands to name are
  `python3 -m studyforge.skills.documents [SKILL]` and
  `python3 -m studyforge.skills.onboarding.verify .`. ⚠️ Mind `REL-05/2` if the README is a
  commanded page. ⛔ The tracked [`ONBOARDING.md`](../../../ONBOARDING.md) is still the user's, and this task did not touch it;
  the reader document a CORPUS receives is what changed.
- ⭐ **`REL-14` (the close):** at a corpus onboarded after this merge, the pin check reads the
  INSTALLED library — run the corpus's `tests/test_framework_pin.py` and
  `python3 -m studyforge.skills.onboarding.verify .` in the empty environment, and record both. ⛔ A
  corpus still carrying a `"where": "sibling"` pin will fail its OWN pin check there (it looks for a
  sibling checkout), which is that corpus's re-onboarding, not a framework defect.
- ⛔ **The integration office (the ISO corpus): nothing breaks until you re-onboard.** Your
  committed `tests/test_framework_pin.py` imports no framework code and still checks the sibling
  checkout; your other generated tests import nothing this task changed. Measured: an export of the
  corpus at `acde021`, its suite run against the framework at `bed97114` and at `02d3b76a`, reads the
  same — the only failure in both is the sibling-absent pin test, because an export has no sibling.
  ⭐ **On your next regenerate**, after the framework sibling is at a commit containing this merge:
  1. `reonboard('.')` alone now REFUSES by name (`predates the installed library`); re-pin:
     `reonboard('.', framework_commit=<the full sha of the framework you run>).write('.', regenerate=True)`,
     then `hand_edited('.')` must print `[]`.
  2. The pin becomes `"where": "installed"` with a `version`; the three stubs, the reader document,
     `tests/test_framework_pin.py` and `installed.json` are rewritten together.
  3. ⚠️ **Your fences no longer carry `PYTHONPATH=../studyforge/src`**, and the new pin check imports
     `studyforge`. Run them in a Python where `studyforge` is importable: a venv with the wheel (or
     `pip install -e` of the framework) installed, or export `PYTHONPATH` to the framework's `src`
     yourself in the workspace. `python3 -m studyforge.skills.onboarding.verify .` says which
     version that Python imports.
- ⛔ **Re-measure; never copy a figure from this handoff.**
