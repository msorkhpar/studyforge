# Shared contract fixtures

The synthetic corpora `tests/fixture_checks`' `VALID` names, and the
deliberately invalid ones its `INVALID_CORPORA` registers. **Every test that
needs a corpus tests against these**, so that no suite invents its own idea of
valid input — which is how parallel work drifts into incompatible mental
models.

⚠️ **This file states no count of them, deliberately.** A count in prose is a
fact nothing checks, and a pointer resolves at read time where a number
cannot.

They are synthetic on purpose. A fixture that depends on 166 real files is a
fixture nobody can debug.

`tests/fixture_checks/` states every invariant below — one module per seam:
`vocabulary`, `corpus`, `shape`, `digests`, `addresses`, `media`,
`personal_data` — and `tests/test_fixture_consistency.py` asserts them. Those
modules are the authority on what these files claim. Read them before changing
one of these files, and run `python3 -m tests.fixture_checks` for the
block-type coverage table.

⚠️ **One property has a test module of its own**,
`tests/test_fixture_shared_origin.py`: two units on one `origin.path` is a
property *of the set* rather than of a corpus, and what it asserts is a
cardinality — see `shared-origin/` below.

## The valid corpora

⭐ **`depth1/` is the common case, not the exotic one.** Two of the four
designed source shapes are depth 1 — SPARQL (`["course"]`) and ISO-8583
(`["group"]`). It is given at
least the care `depth2/` gets, and it exercises two things `depth2/` does not:
a unit with **two** archive documents, and real media on disk with real
digests.

| | `depth1/` | `depth2/` | `shared-origin/` |
|---|---|---|---|
| Shape it stands for | SPARQL, ISO-8583 — **2 of the 4** | Java-senior, CodeSignal | **two units, one source file** |
| `levels` | `["course"]` — **1** | `["section","module"]` — **2** | `["guide"]` — **1** |
| `container_api` | 1 — a whole-file `origin` | 1 — a whole-file `origin` | **2** — a **region** `origin` |
| Containers | 1 | 3 — two of them in one section | 1 |
| Units | 3 (4 archive documents) | 6 (3 + 2 + 1) | 2 (2 archive documents) |
| Variants | 1 (`prose`) | 1 (`java`) | 1 (`prose`) |
| Exercises | **zero** | 2 practices | **zero** |
| Placement | `tree` | `sibling` | `sibling` |
| `permitted_edits` | `[]` — the normal case | one `pom.xml` insert (R3) | `[]` |
| `media` in the manifest | **absent** — the default case | declared, `auto` + limits | **absent** |
| Authored overlay | none | `basics/01-getting-started` unit 1 only | none |
| Source material on disk | no | no | ⭐ **yes** |
| Block types exercised | 10 of 11 (no `video`) | **11 of 11** | 3 — it is not a coverage corpus |

`depth1` exists to keep the 1-level and no-exercise paths first-class rather
than discovered late. ⛔ **A corpus with no graders is complete,
not short** (spec §7, C5) — nothing here should be read as a degraded corpus.

`depth2` carries, deliberately, one unit **with** an authored overlay
(`units/unit-01/content.json`) and two **without**, because a unit page's two shapes
— derived and authored — are different code paths and each needs an input.

## ⛔ `shared-origin/` exists for one property, and it is not coverage

⭐ **Two units declare the same `origin.path` and differ only in
`origin.section`.** Nothing else in this set does, and without it, *how is a
clip keyed when several units share one source file?* could not be tested in
this repository at all. ⛔ **It is the smallest corpus that can exhibit the
collision** — two is all the pigeonhole needs — and a larger one would be a
reading taken inside a consumer repository rather than here.

⛔ **Why the property needs a fixture of its own.** *"Asserted in
both directions"* proves **surjectivity, not injectivity**. Clips colliding onto
one filename means every `<audio>` still resolves **and** every file on disk is
still named by a page: both stated directions pass, the suite stays green, and
every unit but one plays the wrong audio. ⭐ The form that states injectivity is
a **cardinality equality** — `|clips| == |spoken units|` — and it is
unwritable against a set in which no two units share a file.
`tests/test_fixture_shared_origin.py` asserts both halves: that a path-derived
key **does** collide here, and that one derived from the unit's logical address
 does not. ⚠️ A fixture asserted to be shared-origin without the first
half is the vacuous shape the second half would hide.

⭐ **It also gives each `origin` shape an input**, which is `depth2`'s own
argument about overlays applied one field along: a whole file and a *region* of
one are two code paths, so the set carries `container_api` 1 and 2 rather than
only the newest.

⭐ **And its source material is committed beside its archive** — as
`runnable/`'s is — so `validate` reports nothing `Unchecked` on it: the heading-count check (`short-read`) and the region checks
(`origin-section-missing`, `origin-section-ambiguous`) actually run. ⚠️ The
fenced block inside unit 1's region is load-bearing for that and is **depth 3**
on purpose: a fence-blind count reads **6** headings in that file where there
are 4 and **4** in unit 1's region where there are 2, so it short-reads. Make
those comment lines `#` instead of `###` and they become depth-1 headings that
*terminate* the region rather than inflating it — the count stays 2 and nothing
reds.

⛔ **Nothing in this corpus names any real source.** The shape is the subject —
two units, one file — and a source-specific measurement belongs to that
source, never to the framework (R1).

## ⛔ `runnable/` is the one corpus whose units RUN

⭐ **It exists because the runner and the terminal command need something to
execute**, and every other corpus here is JSON and Markdown:
`depth2` declares practices, and nothing in it can run. ⛔ **It is an execution
fixture, not a coverage corpus**, so it is required to exercise three block
types and no more, exactly as `shared-origin/` is.

One container, `kata`, five units, **one runtime — Python, graded by pytest**:

| Unit | Shape | Its file | Its run command | Its test command |
|---|---|---|---|---|
| 1 | graded, the test **passes** | `practice/passes/greet.py` | succeeds | passes |
| 2 | graded, the test **fails** | `practice/fails/total.py` | succeeds | fails |
| 3 | **ungraded** — a file and **no test** | `practice/untested/hello.py` | succeeds | collects nothing |
| 4 | graded, the file does **not compile** | `practice/broken/area.py` | a `SyntaxError` | errors at collection |
| 5 | **none** — reading only | — | — | — |

⛔ **Unit 4's error is `'break' outside loop`, which the COMPILER raises and the
parser accepts.** A missing colon would be a parse error, and several walkers in
this suite `ast.parse` every `.py` under `tests/`; `tests/test_fixture_runnable.py`
pins both halves.

⭐ *A file with no test is not a failure* (spec §7) — unit 3. ⭐ *The
first failure ends the run* — unit 4's run command fails, so a runner
that honours it never reaches a grader that could only have errored.

⛔ **Its graders are `check_*.py`, never `test_*.py`, and that is load-bearing.**
This repository's pytest collects everything under `tests/`, so a grader under
the default pattern would be run by the suite itself — and units 2 and 4 fail
on purpose. The corpus's own `pytest.ini` declares the pattern (and turns off
pytest's cache), so a run from the corpus root collects them.
`tests/test_fixture_runnable.py` asserts both halves.

⛔ **Never run anything in this directory.** The fixture tree is un-ignored
(`!tests/fixtures/**`), so a grader run here leaves an untracked `__pycache__`.
Copy the corpus somewhere a run may write, as `tests/test_fixture_runnable.py`
does.

⚠️ **It declares `runtimes: ["python"]`**, and `tests/test_fixture_runnable.py`
holds the manifest to exactly that.

### What each unit is for

`depth1`

| Unit | Carries | So that |
|---|---|---|
| 1 | `heading`, `para`, `code`, `list` | the plainest possible unit |
| 2 | `table`, `image`, `quote`, an asset manifest, `assets_sha256`, an **attachment** | C4 — a file the page links rather than renders |
| 3 · `lesson-1` | `rule`, and a **`disclosure`** withholding why the unit sets no work | the third state: present but withheld (C5, Q1) |
| 3 · `lesson-2` | three fences full of XML/HTML, a **`disclosure`**, and a raw-HTML block with **the same tags** | fence awareness — see below. Also: a unit with two archive documents |

`depth2`

| Unit | Carries | So that |
|---|---|---|
| `basics/01-getting-started` 1 | a lesson, a practice, the authored overlay, and the **only `exercise` record outside `runnable/`** | the authored shape, a practice's three-section layout, and §7's **graded** state |
| `basics/01-getting-started` 2 | `table`, `rule`, no overlay | the derived shape |
| `basics/01-getting-started` 3 | a `video` block, a `video` record, `media_skipped` | media named and deliberately not fetched |
| `advanced/02-going-further` 1 | a lesson, a practice with **no `exercise` key**, `url_slug` | a second container, a carried field, and §7's **ungraded** state |
| `advanced/02-going-further` 2 | a closing lesson, plus a fenced Maven POM | a container whose last unit has no exercise; fence awareness at depth 2 |
| `advanced/03-putting-it-together` 1 | a heading and a para, in a second module of `advanced` | ⛔ **the set's only module change inside one section** — the walk's other crossing changes section and module at once, and a renderer can get that one right and this one wrong |

`shared-origin`

| Unit | Carries | So that |
|---|---|---|
| 1 | two `heading`s, two `para`s, and a fence whose comment lines are **depth 3** | a region with a subsection of its own — the bound is the next *shallower* heading, not the next one — and a fence-blind count short-reads it |
| 2 | one `heading`, one `para`, a markup-shaped fence | a second region of **the same file**, disjoint from the first, so `origin.path` names both units and identifies neither |

## ⛔ §7's three exercise states are carried by the set, not by a flag

⭐ **All three appear across `depth1` and `depth2` — and again inside
`runnable/`, whose units 1–5 carry all three — and none of them is written down
anywhere as a state.** There is no `state` field to set and none to
forget — the state *is* which files exist (spec §7, C5):

| State | Where it is | How it appears |
|---|---|---|
| **none** | all of `depth1` | no `practice-M.json` at all |
| **ungraded** | `advanced/02-going-further` unit 1 | a practice document with blocks and **no `exercise` key** |
| **graded** | `basics/01-getting-started` unit 1 | the `exercise` key is present |

⚠️ **`depth1` is the common case and it is `none` throughout.** ISO-8583 is
`none` for all 38 units and SPARQL is `ungraded` for all 19; the Java repo is
the exception. ⛔ A corpus with no graders is **complete, not short** (§11.0,
C5), so nothing in `depth1` should be read as a fixture that is missing
something.

⛔ **Do not add an `exercise` to a second document to "improve coverage".** The
graded state is the exception in real material, and a set in which it is the
majority is a set that will let a design fitted to the exception look correct.
⚠️ **`runnable/` is the one sanctioned exception, and it is stated rather than
counted:** a runner's fixture must grade, so the rule the tests state is *"exactly
one exercise that validates, outside `runnable/`"*.

⚠️ **One sanctioned second copy, and its licence is that it must fail.**
`invalid/user-authoritative/` carries an `exercise` that records
`provenance: user` with `trust: authoritative`. ⛔ It is not coverage — it is
R5's **negative control**: spell R5 as a list of forbidden pairs and that
corpus violates no rule at all, which reds the fixture-consistency suite. The
rule the tests state is therefore *"exactly one exercise that **validates**"*,
not *"exactly one exercise"*.

## Fence awareness — the highest-value thing in this set

⛔ **A parser that scans for `<` without tracking fences is wrong, and it fails
silently.** In real material, `<tag>`-shaped text is mostly XML *inside
fenced code blocks* — Maven POM, Spring beans, jPOS config — and a count of
angle brackets reads it as raw HTML.

So `depth1` unit 3 `lesson-2.json` carries three fenced blocks of XML and HTML
— one of them a fence *about* a `<details>` — **and** a raw `html` block, in one
document. Coverage of each block type separately cannot prove a parser tells
them apart; only material where the two are the same text can.
`test_the_same_tags_appear_fenced_and_raw_in_one_corpus` asserts that overlap
still exists, so it cannot be edited away by accident.

⚠️ **The overlap is exactly `<p>` and `</p>`, and that is load-bearing.**
Disclosures are `disclosure` blocks, so the only raw `html` in `depth1` is the
callout — and the callout **must** contain a `<p>`, or the test goes red for a
reason that has nothing to do with fences.

⚠️ **Fence awareness does not weaken the vocabulary requirement.** `rule`,
`quote`, `html` and `disclosure` are all needed: the
disclosure is a *SPARQL* requirement (6 of 19 lessons, every one of them hiding
an exercise answer), and thematic breaks (10 lessons) and blockquotes (1) are
the *Java corpus's*. All four appear in both corpora here.

## The invalid corpora

`invalid/<name>/` is a complete, tiny corpus that is valid in **every respect
but one**. Each carries a `VIOLATION.md` naming the rule it breaks, the file
that breaks it, and what `studyforge validate` is expected to say.

| Fixture | The one rule broken |
|---|---|
| `bad-corpus-api/` | R9 — unknown `corpus_api`, refused rather than migrated |
| `address-directory-mismatch/` | §6 — a container map's address must match the directory holding it |
| `digest-mismatch/` | §6 — `content_sha256` must cover the blocks |
| `ordinal-gap/` | §6 — unit ordinals contiguous from 1 |
| `personal-data/` | R7 — `assert_clean` must refuse, never rewrite |
| `count-mismatch/` | §6 — a document's `counts` must agree with its blocks |
| `user-authoritative/` | **R5** — `authoritative` implies `bundled` |

⭐ **`count-mismatch/` is the one an inspection cannot find.** Its digest is
correct, so the corpus is byte-exact and still lies about itself — and `counts`
is the field every consumer reads *instead of* walking the blocks.

⛔ **`user-authoritative/` is a negative control, not coverage.** Spelled as a
list of forbidden pairs naming `generated` only, R5 would let a grader the
reader wrote declare itself the source's own and nothing would raise. Spell it
that way and this corpus violates no rule at all — which reds `test_invalid_corpus_violates_exactly_its_one_rule`
rather than waiting for a reviewer.

⚠️ **`invalid/personal-data/` deliberately contains personal-data shapes.**
Both values in it are fabricated — an obviously-placeholder absolute home path
and an address under the RFC 2606 reserved `.invalid` TLD, which can never be
delivered. Nothing in it came from any real machine, account or person, and
its own `VIOLATION.md` says so. **A repository-wide R7 sweep must
exclude that one directory and only that one** — and this is not a matter of
trust: `test_only_the_personal_data_fixture_carries_personal_data` sweeps the
whole fixture tree and enforces exactly that boundary, in both directions.

⛔ The scrubber's own replacement address is deliberately **not** used as the
leak. A correct gate skips its own placeholder, so a fixture built out of one
would be refused by nothing.

## The archive document, as these fixtures spell it

Key order is the document's own and reaches disk unsorted, so an unchanged
document re-renders to identical bytes (R10):

```
raw_api  source  address  variant  unit  kind  ordinal  ingested  title
blocks  video  assets  attachments  counts  content_sha256
```

then, only when they have something to say and always **after** the digest:
`assets_sha256`, `starting_code`, `media_skipped`.

- **Rendered as** `json.dumps(document, indent=2, ensure_ascii=False, sort_keys=False) + "\n"`.
- **`content_sha256`** is `sha256` over `json.dumps(blocks, separators=(",",":"), ensure_ascii=False)` — the blocks and nothing else, so a re-ingest date change cannot make unchanged content look edited. `assets_sha256` is the same canonicalisation over `assets`.
- **`counts`** carries one key per block type, **always all of them including the zeroes**: a count that disappears when it is zero cannot be told from a count nobody wrote.

### The block vocabulary

```
{"type": "heading", "level": int, "text": str}
{"type": "para",    "text": str}
{"type": "code",    "lang": str, "text": str}          # "" for a bare fence
{"type": "list",    "ordered": bool, "items": [str]}
{"type": "table",   "headers": [str], "rows": [[str]]}
{"type": "image",   "src": str, "alt": str, "width": int | None}
{"type": "video",   "src": str, "title": str}
{"type": "rule"}                                        # thematic break
{"type": "quote",   "blocks": [block]}                  # blockquotes nest
{"type": "html",    "text": str}                        # verbatim, never parsed
{"type": "disclosure", "summary": str, "open": bool, "blocks": [block]}
```

⭐ **Two container blocks, one shape.** `quote` and `disclosure` both hold
blocks rather than text, because both can wrap a list, a fence or a table.
⛔ **A disclosure is never an `html` block and is never flattened** — flattening
destroys the hiding and shows an answer its author withheld; storing it raw
makes its body invisible to the block-count gate. *Present but withheld* is a
third state, which is C5's lesson landing in the vocabulary. The archive records
the semantics and the label; that the markup is `<details><summary>` is the
renderer's decision (R13), and narration speaks the `summary` and stops.

`rule`, `quote`, `html` and `disclosure` are not speculative: 10 Java lessons
use `---` and one uses a blockquote, and 6 of 19 SPARQL lessons end in a
`<details>` disclosure. `video` is in the archive vocabulary but is not something the
Markdown reader produces.

## Where the files sit

```
depth1/
  corpus.json                                   the manifest (spec §4)
  archive/<address>/
    container.json                              spec §6
    raw/<variant>/unit-NN/lesson-M.json         the archive documents
    raw/<variant>/unit-NN/practice-M.json       where a unit sets work
    units/unit-NN/content.json                  the authored overlay, optional
    units/unit-NN/<local>                       what an asset's `local` resolves against
golden/
  <corpus>.plan.txt                             `studyforge plan` output, byte for byte — one per valid corpus
```

⭐ **`shared-origin/` adds one thing to this layout: the source material.**
Its `field-notes/` directory holds the two files its container map's `origin`
records, which is why it is the one corpus `validate` can check against a
source. ⚠️ Every other corpus's `origin` paths are *declared and absent*, which
is a first-class state (R2 — an archive ships on its own) and reads as
`Unchecked`, never as a failure.

⭐ **`archive/` is the archive root under every profile** — `ARCHIVE_DIRNAME`,
spelled once in `corpus.placement.names` and read by `validate`, `plan`, a build
and the adapter layout.

## Golden files

The fixtures **are** the golden files for the artefacts the spec pins down —
the manifest, the container map and the archive document, each written in its
canonical form, so a round-trip is a byte comparison against the file itself.

⭐ **`golden/` holds the one written output that has a golden: `studyforge
plan`.** `golden/depth1.plan.txt` and `golden/depth2.plan.txt` are what the
command prints for each corpus, byte for byte, asserted by
`tests/studyforge/cli/plan/test_cli.py`. ⚠️ **Beside the corpora rather than
inside one**, because a plan says what would be written *into* a corpus root
and a golden sitting in that root is a file the plan would have to explain.

⛔ **Nothing else has a golden file, and that is still deliberate.** The unit page's and
the page assets' outputs are designed but not pinned here, and a golden for output
nobody has designed is a fixture that will be wrong and will be trusted. A
golden lands with the design of the output it pins.

## `sdk-profile/` — a corpus that names an image profile

A copy of `runnable/` whose manifest declares the runtimes `python`, `node`, `java`, `gradle` and
`kotlin` and names a toolchain image profile in `profile`. The profile's name is data the
corpus declares: no framework module names one, and the tests that export this corpus
(`tests/studyforge/skills/execution/standalone/test_profile_export.py`, and `_real.py` against a
real toolchain checkout) read the name from this manifest.


## `claude_shape/` — the shape of a course on language SDKs, built by code

A Python package, not a tree of files: `python3 -m tests.fixtures.claude_shape` writes a
four-language course (Python, TypeScript, Java and Kotlin) with a profile and a live block,
authors its four graded practices and a two-domain mock exam in the profile's runner under
`--network none`, exports it thin on the profile, and reads the served result in headless Chrome
(first-visit language question, four-language tabs with a greyed language, each practice graded
in the browser, Run on an example, the mock exam scored, the live-run field with and without the
`live` compose profile against a host that does not resolve). It lives here, not beside the
tests, because it is a fixture builder; `test_shape.py` checks only what needs no container.
