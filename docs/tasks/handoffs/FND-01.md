# FND-01 — handoff

**Status:** done, with one acceptance clause **blocked on FND-03** (lint —
see *Decisions*, item 2, and *For dependents*).

## What landed

**The package tree of spec §3.2**, `src/studyforge/` — `address`, `corpus`,
`archive`, `unit`, `contents`, `render`, `narrate`, `serve`, `execute`,
`progress`, `exercise`, `validate`, `cli`, `skills`. Every one is a package
with an `__init__.py` carrying its contract (R17): what it does, how you use
it, what it depends on, the rulings that bite on it, and which task fills it.
No implementation — these are contracts, not stubs with bodies.

**The mirrored test tree**, `tests/studyforge/` — one `test_init.py` per
package, asserting the package imports as the name it claims and states a
contract. Plus:

- `tests/support.py` — shared helpers. `assert_package_contract`,
  `repository_root`, `tool_on_path`, `run`. Imported as
  `from tests.support import ...`, never copied.
- `tests/test_quality_floor.py` — the thin wrapper that fails the suite when
  the floor does, and asserts the floor checks itself.
- `tests/test_repository.py` — dependency policy (declared *and* actually
  imported), packaging exclusion, the **ignore-rule regression test**, and the
  optional-tooling checks.

**The quality floor**, `tools/quality/` — standard library only, mirrored at
`tools/tests/quality/`:

| module | rule | what fails the build |
|---|---|---|
| `size.py` | R11 | source module > 400 lines, test module > 600 |
| `mirror.py` | R12 | a source module with no test at the mirrored path |
| `docstrings.py` | R17 | a module under `src/` or `tools/` with no contract |
| `style.py` | — | CRLF, tab indent, trailing whitespace, final newline, line > 100 |
| `config.py` | — | every ceiling, marker and root, declared once |
| `report.py` | — | `Finding`, and `path:line: [rule] message` |

Public surface: `run_all(root) -> list[Finding]`, `format_findings`,
`Finding`, and the ceiling constants. CLI: `python3 -m tools.quality
[--root PATH]`, exit 1 on any finding.

**The size opt-out.** A line `Size exception: <reason>` in the module's first
docstring, parsed with `ast`, case-sensitive, at least 20 characters of
reason. Documented in `docs/conventions/module-structure.md` §"The ceiling is
enforced, and the exception is declared".

**Packaging and runners**, `pyproject.toml` — setuptools src-layout,
`dependencies = []`, extras `test` (pytest) and `lint` (ruff), pytest
configured with `pythonpath = ["src", "."]` so the suite runs from a clean
checkout with **no install and no network**, and ruff configured for wherever
it exists.

**Ignore rules**, `.gitignore` — audio and discovery caches produced by this
repository's own runs, with the scope stated so it does not read as a reversal
of SF-17; and a negation that keeps `tests/fixtures/**` trackable, **tested in
both directions** by `test_golden_fixtures_are_not_ignored` and
`test_the_same_shapes_outside_the_fixtures_are_still_ignored`. The shapes it
asserts on do not exist in the tree yet, which is where the risk is — FND-04
writes them. Both directions, because a one-directional test passes on a
`.gitignore` that ignores nothing at all.

## Decisions

**1. The size checker lives in `tools/`, tested at `tools/tests/`.** The CTO
ruling arrived mid-task and matched the location I had already implemented and
was about to defend; the ruling's second half moved the tests from
`tests/tools/` to `tools/tests/`, which I applied. The reasoning I would have
given, for the record: spec §3.2 enumerates what the framework ships and a lint
tool is not on the list, so `src/` would make the ceiling check part of
`studyforge`'s importable API — versioned under R9, depended on by consumers —
to buy nothing a build script wanted. Both mirror pairs are declared in
`config.MIRRORS`; neither is an exemption. Packaging looks only in `src`, so an
installed `studyforge` contains no `tools`, asserted in
`tests/test_repository.py`. `tools/` is a scan root, so the checker is held to
its own rules. ⚠️ One consequence worth knowing: `tools/tests/` imports
`tests.support` rather than keeping its own copy of `repository_root` and
`run`. Locality of *tests* is what R12 asks for; duplicating two helpers to
achieve locality of *helpers* is the thing `tests/support.py` exists to
prevent.

**2. Lint: ruff, configured and declared, not run.** No linter is installed and
no network install was attempted. Ruff is configured in `pyproject.toml`
(`line-length = 100`, `E,F,W,I,UP,B,D`, formatter) and declared as the `lint`
extra. `tests/test_repository.py` runs `ruff check .` and `ruff format --check
.` **where ruff exists** and otherwise skips with a message naming the extra —
it never passes quietly. ⛔ **I am not claiming lint runs clean; it did not
run.** Alongside it, `tools/quality/style.py` implements the standard-library
subset that always runs: line endings, tab indentation, trailing whitespace,
final newline, line length. ⛔ `[tool.ruff] line-length` and
`tools.quality.config.LINE_LENGTH` are asserted equal, so the always-on checker
and the optional one cannot come to disagree about the same file.

**3. `--import-mode=importlib`** — now a **recorded ruling** (rubric §10a),
not folklore: it is required by R12's mirror, and a diff that drops it is
CHANGES REQUESTED with that as the stated reason.

R12's mirror puts a `test_init.py` in every package
directory. Under pytest's default `prepend` mode, two files with the
same basename in directories that are not packages collide on the module name
and the suite fails to collect. The alternatives were an `__init__.py` in every
test directory, or renaming the mirrors so they stop mirroring. ⚠️ **A task
that changes this setting will break collection**, not style.

**4. Line counting is physical lines** — `len(text.splitlines())`, what
`wc -l` reports — so the tool's arithmetic is checkable from a shell before
anyone trusts it.

**5. The contract check tests presence, not shape.** R17's three parts are
asserted for the §3.2 packages by `tests.support.assert_package_contract`
(which looks for "What it does", "How you use it", "Depends on"), and the
repo-wide floor only requires a docstring of ≥ 40 characters. Parsing every
module for three headings would enforce a template nobody agreed to and would
pass a module that filled it in with nothing.

**6. The mirror check is one-way.** A source module must have a test; a test
need not have a source. `tests/harness/` (SF-26), `tests/visual/` (QA-03) and
`tests/support.py` all exist legitimately without a counterpart, and the
reverse check would turn each into an exemption list.

**7. `requires-python = ">=3.14"`**, matching the extraction source's pipeline
and the only interpreter this was verified on. ⚠️ Not researched against what a
reader's machine is likely to have — if the reading floor should run on an
older Python, that is a decision somebody should take deliberately rather than
inherit from here.

**8. No `[project.scripts]` yet.** SF-28 owns `studyforge/cli/`. Declaring
`studyforge = "studyforge.cli:main"` against a `main` that does not exist
produces an installed package that fails on first invocation.

## Surprises

**The task's `.gitignore` clause contradicts the file it was asked to
change.** FND-01 says "git ignore rules for generated audio"; the existing
`.gitignore` carries a deliberate comment from commit `af628a9` saying audio is
**not** ignored because generated media is committed by default (SF-17).
Resolved by scope rather than by reversal: a *corpus* commits its media under
its own `media` policy, written in the corpus's ignore file; `studyforge`'s own
tree never legitimately holds a clip, so `*.audio/`, `.studyforge/` and
`.discovery-cache/` are ignored **here** with the scope stated in the file.
⭐ **Ruled: the scope resolution stands and E00's wording is the error.** It
predates `af628a9` and should read "generated audio produced by this
repository's own runs and test runs"; the PO carries the task edit.

**The context budget was right, the file list was not.** `CS/tests/support.py`
was worth reading for its "extract it and import it" ruling, which is why
`tests/support.py` exists. `CS/pyproject.toml` is seven lines and contains no
build system, no dependency declaration and no lint configuration — there was
nothing to port, and everything in `pyproject.toml` here is new. Budget ~30k;
actual reading was well under it because the epic and §3.2 carried the shape.

**pytest's default import mode is incompatible with R12's mirror.** Not
mentioned anywhere in the plan, and it fails at collection with fifteen errors
rather than one, which reads like something much worse. See Decisions 3.

## Findings

Defects seen outside my scope, not fixed:

1. **`.gitignore` would have silently swallowed FND-04's golden fixtures.**
   `site.json`, `*.unit.html` and `*.section.html` are ignored repository-wide,
   and those are exactly the filenames FND-04's golden files carry. Dev 2's
   fixtures would have been untracked, their suite passing locally and failing
   on any other checkout. I added `!tests/fixtures/**` because `.gitignore` is
   my deliverable, and verified with `git add -n` that a fixture
   `.studyforge/archive.json`, `site.json` and `a.unit.html` are all trackable.
   ⛔ **Now tested**, in both directions, by `tests/test_repository.py` — see
   *What landed*. The negation works only because `!tests/fixtures/**` also
   matches the intermediate directories; git normally cannot re-include a file
   whose parent directory is excluded, and `.studyforge/` excludes one of
   these parents. Narrowing the pattern to `**/*.json` or moving it above the
   rules it negates breaks it silently — both were run against the test and
   both fail it, as does a `.gitignore` emptied entirely.
   ⚠️ **FND-04 should still confirm this covers the shapes it actually
   writes**, and add them to `FIXTURE_SHAPES` if not.

2. **`docs/tasks/README.md:288` and `CLAUDE.md:33` say "R1–R19"; the spec has
   R20.** Reported by the CTO, confirmed, not fixed — outside this task.

3. **Spec §3.2 lists `render/templates/` and `render/assets/` as part of the
   tree, but they are data directories rather than packages.** Not created:
   an empty directory cannot be committed, and a `.gitkeep` would be a
   placeholder for something SF-11 and SF-12 own. Packaging for them **is**
   declared (`[tool.setuptools.package-data]`), so those tasks add files
   rather than build configuration.

4. **`src/studyforge/skills/` is a Python package, and E11's skills may not be
   Python.** §3.2 puts `skills/` in the source tree; E11's tasks own "the
   reconnaissance skill", "the onboarding skill" and so on, which read like
   documents with procedures. The package is created with a contract saying
   anything in it exists to be *called by* a skill. If the skills turn out to
   be entirely documents, this package should be removed rather than left
   empty — an empty package with a contract is worse than no package.
   ⛔ **Ruled: creating it was correct, and if E11 concludes the skills are
   entirely documents, E11 deletes the package.** An empty package that never
   fills is dead shipped surface.

5. **No repository-hygiene check for R7.** A cheap standard-library check for
   an absolute home path in a tracked file would sit naturally beside the size
   check, and CLAUDE.md records that this rule has already been violated once
   in this repository's own documents. Deliberately not built — it is not in
   FND-01's scope and SF-08 owns the personal-data gate for archive content,
   which is a different check with a different subject.
   ⭐ **Accepted and scoped as a new task**, in `tools/quality/` beside the
   size and mirror checks — deliberately not retrofitted into FND-01.

## For dependents

**Every framework task depends on this. Four things to know:**

**1. Run `pytest`. That is all.** `python3 -m pytest` from the repository root
runs the suite and the quality floor, with no install and no network.
`pythonpath = ["src", "."]` puts `studyforge`, `tools.quality` and
`tests.support` on the path. There is no separate lint command to remember.

**2. Where your test goes.** `src/studyforge/<pkg>/<mod>.py` →
`tests/studyforge/<pkg>/test_<mod>.py`. A package's `__init__.py` →
`test_init.py`. If you are unsure, ask the tool:
`python3 -c "from tools.quality.mirror import mirror_for; print(mirror_for('src/studyforge/serve/routes/content.py'))"`.
**A source module with no test fails the build**, so write the test in the same
task (R12) — the floor will not let you defer it.

**3. When your module gets long.** Split it into a package; that is the
expected outcome. If splitting is genuinely worse, put this in the module's
**first** docstring:

```
Size exception: <one sentence saying why splitting would be worse>
```

⛔ The marker is that literal string, capital S, lowercase e, colon — the
review rubric greps for exactly that token and the checker is case-sensitive to
match. At least 20 characters of reason. A comment elsewhere in the file does
not count.

**4. Your package's `__init__.py` already states its contract — keep it.**
The docstring in your package names the rulings that bite on it and what it
must not depend on; it was written from spec §3.2 and §2, and
`tests/studyforge/<pkg>/test_init.py` asserts it still says "What it does",
"How you use it" and "Depends on". Extend it as you implement; do not replace
it with a label.

**Specifically for:**

- **FND-03 (container).** Two things. The image should `pip install -e
  '.[test,lint]'` — that is what turns the two skipped ruff tests into real
  ones and closes FND-01's blocked lint clause. And the image needs Python
  3.14 (`requires-python = ">=3.14"`); if that is a problem for the base image
  you would like to use, say so, because Decision 7 above was not researched.
- **FND-04 (fixtures).** `tests/fixtures/` is excluded from every quality
  check by `config.EXCLUDED_DIRS`, so a deliberately invalid fixture will not
  be reported as a style defect. Your golden files are kept trackable by a
  `.gitignore` negation that is easy to break and fails silently — it now has
  a regression test (`FIXTURE_SHAPES` in `tests/test_repository.py`). ⚠️ **Add
  the shapes you actually write to that tuple** if they differ from the three
  already there.
- **FND-05 (workspace).** `studyforge` has no git remote yet, which is what a
  submodule pin needs.
- **SF-28 (`cli/`).** `[project.scripts]` is deliberately absent; add it when
  `studyforge.cli:main` exists.
- **SF-11 / SF-12 (`render/`).** `templates/` and `assets/` do not exist yet
  but are already declared in `[tool.setuptools.package-data]`.
