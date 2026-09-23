# REL-04 — handoff

**Kind:** task handoff — REL-04

## Status

**done, self-certified against the epic.** Task `REL-04`, defined in
[`E15` § REL-04](../E15-release-ready.md#rel-04-the-skills-ship-in-the-package). ⭐ **An EPIC
TASK, so it has no row file and nothing was minted.** Branch
`chore/REL-04-the-skills-ship-in-the-package`, cut at the release tip `f3f5485a`. Office `dev1`.
Milestone **M11**, step **11.3**.

⭐ **The one sentence:** every skill document under `src/studyforge/skills/` now ships in the wheel,
and `studyforge.skills.documents` is the one way code and a reader find a skill document from an
installed package.

⭐ **Author line declared:** every commit on this branch is `dev1 <dev1@example.invalid>`, passed
with `git -c`. ⛔ Nothing was written to any git config, no remote was added, nothing was pushed,
nothing was moved or deleted.

## Gates

⛔ Each gate was run bare from `studyforge-wt/dev1` at the code commit, its output sent to a
scratch file and `$?` read on the next line — never through a pipe.

| gate | environment | reading |
|---|---|---|
| `./docker/dev/check ruff check .` | pinned image | GREEN, exit 0 |
| `./docker/dev/check ruff format --check .` | pinned image | GREEN, exit 0 |
| `python3 -m tools.quality` | host | GREEN, exit 0 |
| `python3 -m pytest tests/studyforge/skills tests/test_repository.py tests/authoring -q` | host | GREEN, exit 0 |
| `./docker/dev/check python3 -m pytest tests/studyforge/skills/test_documents.py -q -rs` | pinned image | GREEN, exit 0 — the two wheel tests SKIP there, saying why (`REL-04/1`) |

## ⛔ The reading `E15` asks for, the control, and the plant

⭐ **The reading.** A `git archive` of the code commit into the office's scratch directory; in
it, `python3 -m pip wheel . --no-deps --no-build-isolation --no-index -w <scratch>` (the host's
own setuptools, nothing fetched). A fresh `python3 -m venv` in scratch, the wheel installed into
it with `pip install --no-index --no-deps`, and from an empty directory outside the checkout,
with `PYTHONPATH` unset:

- `import studyforge` resolves inside the venv, never the checkout;
- `python3 -m studyforge.skills.documents` lists every skill, exit 0;
- `python3 -m studyforge.skills.documents <name>` for each listed name, exit 0, and `cmp` says
  each output is byte-identical to the same skill document in the tree;
- the listed population equals `ls src/studyforge/skills/*/SKILL.md`, and an unknown name exits
  `2` naming the known ones.

⭐ **The control.** The same build from a `git archive` of the release tip `f3f5485a`: the wheel
lists no skill document, and installed into its own fresh venv, `find` in the venv and a walk of
`importlib.resources.files("studyforge.skills")` both find none (`W438/5`, confirmed).

⭐ **The plant.** `pyproject.toml`'s glob narrowed to `skills/[!d]*/SKILL.md` (drops `delivery`
only), restored from a copy taken before it: `test_every_document_is_declared_package_data`,
`test_the_wheel_carries_every_document_unchanged` and
`test_the_installed_package_reads_every_document` went RED, the first two naming
the delivery skill's document ([`SKILL.md`](../../../src/studyforge/skills/delivery/SKILL.md)); restored, all GREEN. ⭐ And the tests' own negative control: run
before the glob was added, the same three were RED.

## What landed

- **`pyproject.toml`, `[tool.setuptools.package-data]` only:** the pattern
  `skills/**/SKILL.md` joins the templates and assets. ⛔ A glob, never a list: a new skill ships
  by existing.
- **`src/studyforge/skills/documents.py`, the locator.** Standard library only
  (`pathlib`; the directory is `Path(__file__).parent`, as `render.templates` does it):
  - `names() -> tuple[str, ...]` — every sub-package of `studyforge.skills` holding a
    skill document, sorted, walked from the installed package;
  - `document(name) -> Path` — raises `UnknownSkill` (a `LookupError`) for a name that
    ships no document; ⭐ that membership test is the ONE check on a name, so `../x` is refused
    rather than joined, and ⛔ the refusal names the known skills and NEVER the name it refused
    (R7);
  - `text(name) -> str`;
  - `python3 -m studyforge.skills.documents [SKILL]` — no argument lists the skills one per line;
    a name writes that document's BYTES to stdout unchanged; anything else exits `UNUSABLE`.
- **`tests/studyforge/skills/test_documents.py`**, three readings: the locator against the tree's
  walked population; the declaration (every tree skill document matches a `package-data` pattern and
  no `exclude-package-data` one); the effect (a wheel built from an export in a temp directory,
  unpacked and read through `-m studyforge.skills.documents` from a directory outside the
  checkout, byte-compared).

## Decisions

- ⭐ **`Path(__file__).parent`, not `importlib.resources`.** Every `importlib` import is a
  run-time door the isolation test refuses (see *Surprises*); the framework already locates its
  templates and assets from its own `__file__`. A path from `document(name)` is for code at run
  time. ⛔ A generated document names a skill by NAME and the command that prints it, never a
  path (R7).
- ⭐ **A module entry point, not a `studyforge` verb.** The verbs are `SF-40`'s table and outside
  this task's Owns; `python3 -m studyforge.skills.documents` needs no dispatcher. A verb that
  delegates to `documents.main` is one line for whoever owns the table, if one is wanted.
- ⭐ **The wheel test builds from an export, never the checkout**, because a setuptools build
  writes `build/` and `*.egg-info` into its source tree. It calls `setuptools.build_meta` in a
  subprocess with no isolation and no pip, so nothing is fetched.
- ⭐ **No file a skill document links needs shipping.** Every `](…)` in the eight documents was
  read: the only targets are `TestCases.md` and `x`, both inside code spans as examples of a
  corpus's syntax, not links a reader follows.

## Surprises

- ⚠️ **The pinned image uninstalls setuptools** once it has installed the package, so in the image
  the wheel cannot be built. The effect tests skip there with a stated reason (the repository's
  skip disclosure prints it); the declaration test is the always-on proxy. See `REL-04/1`.
- ⚠️ **The register's merge gate refused the first tip (`58a17112`) on two tree-wide checks a
  package-scoped run never reached**, both fixed on this branch: `tests/test_emission.py` — the
  refusal quoted the name it refused (R7); and `tests/harness/test_isolation.py` — the module
  imported `importlib.resources`, which is a run-time door by that test's rule. ⭐ The lesson for
  REL-05 and REL-06: run the FULL suite before handing back, not the package's tests.

## Findings

| id | marker | where | what |
|---|---|---|---|
| `REL-04/1` | `[local]` | `docker/dev/Dockerfile`, the editable-install `RUN` | ⚠️ **No build backend in the pinned image**, so a full-suite run there reads the declaration and not the wheel. The host run reads both. Whoever next touches the image may keep the pinned setuptools installed (it is already hashed there) if the image's suite should read the effect too; not a user decision |
| `REL-04/2` | `[local]` | [`docs/authoring/exercises.md`](../../authoring/exercises.md) | ⚠️ **Links the execution skill by its tree path** (`../../src/studyforge/skills/execution/SKILL.md`), which resolves in a checkout and not for someone with the installed library. `REL-07` (the README as the author's reading list) is the natural place to name the locator command beside such links |

## For dependents

- ⭐ **`REL-05` (onboarding stubs resolve through the installed package):** write the stub as a
  skill NAME plus the command `python3 -m studyforge.skills.documents <name>`, and check it in
  code with `studyforge.skills.documents.names()` / `document(name)`. ⛔ Replace
  `onboarding/pin.py`'s `PROCEDURE` and `SIBLING` addressing (a tree path under a sibling
  checkout) — that is yours, and this task did not touch it. `UnknownSkill` is the refusal to
  catch for a stub naming a skill the installed library does not ship.
- ⭐ **`REL-06` (the delivery skill reads a packaged capability index):** the index is NOT a
  skill document, so it ships only if you add its pattern to `[tool.setuptools.package-data]` — this
  task owned that section; append a pattern, keep the existing three. Read it the same way — from
  the delivery package's own `Path(__file__).parent`, ⛔ never through `importlib` (the
  isolation test refuses it) — and reuse
  `test_documents.py`'s shape for the proof: the `wheel` fixture builds from an export and the
  installed-package test reads from a directory with no checkout. ⚠️ Run that proof on the host:
  the image has no build backend (`REL-04/1`).
- ⛔ **Re-measure; never copy a figure from this handoff.** The population is whatever
  `python3 -m studyforge.skills.documents` prints at your ref.
