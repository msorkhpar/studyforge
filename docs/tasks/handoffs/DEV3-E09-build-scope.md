# DEV3-E09-build-scope — handoff

**Kind:** office handoff — DEV3

## ⛔ THE SCOPE ANSWER FIRST: E09 IS NOT ONE ROW

⛔ **E09 holds eight rows across three milestones and both agents**, and the
"build pipeline" the coordinator's brief names is two of them, one per agent.
Read from [`E09-delivery.md`](../E09-delivery.md)'s own headers:

| row | milestone | agent | what it is |
|---|---|---|---|
| `SF-28` | M4 | framework | the framework's build-and-serve CLI — **the orchestration** |
| `OPS-05` | M4 | framework | R3 as a check, `studyforge/validate/nondestructive.py` |
| `OPS-01` | M6 | integration | a corpus's toolchain image |
| `OPS-02` | M6 | integration | a corpus's narration deployment |
| `OPS-03` | M6 | integration | a corpus's compose file |
| `OPS-04` | M7 | integration | **corpus configuration over `SF-28`**, not orchestration |
| `OPS-06` | M7 | integration | reader documentation, generated |
| `OPS-07` | M7 | framework | stale artifact reconciliation |

⭐ **`SF-28` is where the whole build lives, and it is itself not one row.**
Counted in its own section: **one Definition plus five separately-headed
acceptance additions**, minted by four different rulings (99, 129, 157, and two
PO rulings of 2026-09-10). Reading them as work items it carries at least eight
independently deliverable things:

1. the unit-page build — a walk that reads material and writes pages
2. the container pages, root index and contents document
3. joining contents into prev/next `Links` and a breadcrumb trail
4. the media copy (the renderer emits `<img src=…>` and copies nothing)
5. narration wiring — who invokes synthesis, and when
6. `serve`
7. `[project.scripts]` **plus an eleven-file caveat sweep the row itself tabulates**
8. the `exercises: false` → `declared_practices = 0` translation

⛔ **Item 7 alone is a wave.** ⭐ **My recommendation to the register: split
`SF-28` before dispatching it.** Items 1–3 are one row (the build), 4 is one, 5
is one, 6 is `serve` and was always separate, 7 is a mechanical sweep with one
owner, 8 is a two-line translation that item 1 absorbs. **This branch delivers
item 1's floor and item 8, and nothing else.**

### ⭐ What already exists that a build calls — the real entry points, measured

| what | entry point |
|---|---|
| walk a corpus's declarations | `corpus.manifest.parse`, `corpus.container.parse`, and `validate.corpus.read` |
| the archive's own path layout | `skills.adapter.Layout` — `archive`, `container_dir`, `variant_dir`, `unit_dir` |
| a unit's served document | `unit.builder.build_unit(directory, overlay=, declared_practices=, title=)` |
| where an artifact goes | `corpus.placement.profile_for(name)` → `.unit(...)`, `.container(...)`, `.corpus()` |
| the page bytes | `render.page.render(document, placement, links=, trail=, narration=)` |
| the container page, the index | `render.container.render`, `render.index.render`, `render.index.from_contents` |
| the asset bundle | `render.pageassets.written_files`, `.script`, `.stylesheet` |
| the contents document | `contents.build(manifest, containers)`, `contents.write`, `contents.links` |
| what is speakable, and its clips | `narrate.speakable.speakable_of`, `narrate.playable.playable_of` |
| synthesis, incrementally | `narrate.synth.plan`, `.batches`, `.synthesise`; `narrate.client.place` |
| what a build will create | `cli.plan.derive.plan_for(root)` — **already goldened** |

### ⛔ What is genuinely missing, as named things

1. ⛔ **The caller.** Nothing outside `render/` rendered a page and nothing
   anywhere wrote one. **This branch closes it for unit pages only.**
2. ⛔ **Where a unit's authored overlay sits in an archive.** `unit.content`
   mints `content.json`; `Layout` mints every other archive path and not this
   one. A build therefore cannot apply an overlay — `DEV3/2`.
3. ⛔ **The contents→`Links`/`Crumb` join.** It exists only in
   `tests/studyforge/render/page/sites.py`, which says so in its own docstring
   and names `SF-28` as the caller it stands in for.
4. ⛔ **The media copy.** No module copies a unit's `media/` into the placed
   `images/` directory. `SF-28`'s Acceptance already carries the clause.
5. ⛔ **`serve/`, `execute/`, `progress/` are docstring-only stubs** — no `def`,
   no `class` in any of the three.
6. ⛔ **No console entry point.** `pyproject.toml` declares its absence.
7. ⛔ **No `validate/nondestructive.py`** (`OPS-05`) and no `cli/reconcile.py`
   (`OPS-07`).

### ⛔ THE DECISIONS A BUILD FORCES THAT ARE NOT MINE — I TOOK NONE OF THESE

1. ⛔ **Where output goes.** `write_pages(root, into)` takes `into` as a
   **required argument with no default**. Whether a build writes inside the
   material repository, beside it, or somewhere named per corpus is open.
2. ⛔ **What a rebuild does to a file the previous build wrote.** This branch
   writes over **nothing**, names what it refused, and says in the module
   docstring that this is R3's floor rather than a rebuild policy.
3. ⛔ **Who invokes narration and when.** Every page here renders `SILENT`.
4. ⛔ **What a corpus with no narration record shows.** Today: nothing — no
   `data-audio` attribute is emitted at all, which is the quiet direction.
5. ⛔ **Where this package finally homes.** It is `studyforge/generate/`, beside
   `cli/` and not inside it, precisely so `SF-28` can adopt or absorb it.
6. ⛔ **Whether a build should drain findings like `validate` or stop.** I made
   it stop on the first unreadable declaration and said why in the docstring;
   changing it is one function.

**Status:** done, as a scoping answer plus one increment. ⭐ The scope answer is
the deliverable; the code is item 1's floor. ⛔ **Nothing was decided from the
list above** — each is stated as a parameter, a refusal or a named gap.

**What landed:** ⭐ **`studyforge.generate`** — a package whose surface is
`sources(root)`, `write_pages(root, into)`, `declared_practices(manifest, n)`,
`read_manifest(root)`, `containers(root, manifest)`, and the records
`UnitSource`, `Written`, `BuildError`. ⛔ **It is the first non-test caller the
page renderer has ever had.** No subcommand, no flag, no `__main__` — asserted
by a test, because `[project.scripts]` has one minter and it is not me. Tests
mirror it at `tests/studyforge/generate/`.

**Decisions:** ⭐ **Every archive path is asked of `skills.adapter.Layout`**
rather than composed here — a build that spelled `archive/<address>/raw/<variant>`
itself would be a second authority on a layout the adapter writes to one.
⭐ **`exercises: false` is implemented as a declaration of zero** and
`exercises: true` as *no statement*, the count then coming from the container
map — that is the PO's ruling of 2026-09-10 carried out, not a choice, and the
site harness already demonstrates both directions. ⭐ **A declared unit with no
material is skipped in silence**, because `validate` already reports it as
`unit-missing` and a second sentence would make one defect read as two.

**Surprises:** ⚠️ **The build was already written — in `tests/`.**
`tests/studyforge/render/page/pages.py` and `sites.py` are 613 lines that walk,
build, place, render and write, and `sites.py`'s docstring says outright that it
is standing in for `SF-28`'s caller. ⭐ The gap was never knowledge; it was that
the knowledge lived where no product could reach it. ⚠️ **`cli/plan` already
enumerates every path a build creates and its output is goldened**, so Ruling
99's path-for-path clause was runnable the moment a writer existed — this branch
runs its unit-page half against those goldens rather than against a retyped list.

## Findings

| # | marker | what |
|---|---|---|
| `DEV3/1` | `[structural]` | `archive` and `raw` are minted **twice** — `validate/corpus.py` (`ARCHIVE_DIR`, `ARCHIVE_ROOT_NAME`) and `skills/adapter/layout.py` (`ARCHIVE_DIR`, `RAW_DIR`). Neither `validate` name is on `studyforge.validate.__all__`, so `cli/plan/derive.py`'s import of `ARCHIVE_DIR` is the Ruling 101 deviation Ruling 101's own text records as still open. |
| `DEV3/2` | `[structural]` | Nothing in `src/` declares where a unit's authored overlay sits inside an archive. `unit.content` mints `CONTENT_FILENAME` and `Layout` mints every other archive path. Consequence: a build cannot apply an overlay. Marked by a premise test that fails the day `Layout` grows the path. |
| `DEV3/3` | `[structural]` | `PLANTED_SHAPE` is bound **twice** in `tests/studyforge/render/page/sites.py`. The second binding wins; both are identical today, so nothing is red and a divergent edit to the first would be silently dead. |
| `DEV3/4` | `[structural]` | The manifest's `exercises` flag and the container map's `units[].practices` both bear on one number and **no module in `src/` joined them** until this branch — the join existed only in a test harness, which is where `SF-28`'s ruled clause would have been quietly satisfiable without a build. |
| `DEV3/5` | `[local]` | "rglob every `container.json` under the archive" is now written **three times** — `validate/corpus.py`, `cli/plan/derive.py` and `generate/units.py`. Mine is the third. Each returns a different record type, so none is reusable as written; `SF-28` should collapse them onto one walk. |
| `DEV3/8` | `[structural]` | ⛔ **Ruling 74 is contradicted by an enforced gate and its own population figure is stale.** The ruling rules `except A, B:` out and says *"no lint rule, no checker"* is needed and that **two** instances exist. Measured at this branch's tip, instrument `git grep -nE '^\s*except [A-Za-z_][A-Za-z_0-9.]*, '`, population tracked `*.py`: **28**. ⭐ **Cause: `ruff format` — not the linter — strips the parentheses whenever the clause has no `as` binding**, and `ruff format --check` is a suite gate under Ruling 78, so the two cannot both be satisfied by one clause. ⚠️ My own parenthesised clause was rewritten into the forbidden form by the formatter before I noticed; I split it into one type per clause instead. **Either Ruling 74 needs a formatter setting or it needs withdrawing — an author cannot obey it and the suite at once.** |
| `DEV3/7` | `[structural]` | ⛔ **The root ignore file's bare `build/` rule (line 11) matches at every depth**, so a package named `studyforge/build/` is untracked the moment it is written — the floor and the suite then run green over code git never saw. Measured: `git add` refused the path, `git check-ignore -v` named the rule. ⭐ **`build` is the word every task document uses for this work**, so `SF-28` will reach for it first. I renamed to `generate/` and said why in the package docstring rather than editing a root ignore file, which R3 forbids outright for a corpus and which this repository should not do casually either. |
| `DEV3/6` | `[structural]` | Against the coordinator: `PREAMBLE.md` §8's roster reads `_(filled per wave)_`. Its own escape clause fires — I proceeded with no inter-office exchange and assert nothing that needed one. This is the class fix arriving unfilled, which is `W188/3` recurring in a new form rather than repaired. |

**For dependents:** ⭐ **`SF-28`, read `DEV3/2` and `DEV3/5` before starting.**
The build's next three increments in dependency order are: **(a)** declare the
overlay path on `Layout` and pass the overlay through `build_unit` — one field
and one argument; **(b)** the contents pass, which unlocks `Links` and `Crumb`
and lets `sites.py`'s `bar_for`/`trail_for` be deleted rather than duplicated;
**(c)** the media copy, which is the only one of the three that can make a page
that already renders correct. ⛔ **`write_pages` writes over nothing** — the
first row that wants a rebuild has to decide the policy in the open, and that is
the intended friction.
