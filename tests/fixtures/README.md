# Shared contract fixtures (FND-04)

Two synthetic corpora and five deliberately invalid ones. **Every downstream
epic tests against these**, so that twelve epics are not each inventing their
own idea of valid input — which is how parallel work drifts into twelve
incompatible mental models.

They are synthetic on purpose. A fixture that depends on 166 real files is a
fixture nobody can debug.

`tests/fixture_checks/` states every invariant below — one module per seam:
`vocabulary`, `corpus`, `shape`, `digests`, `addresses`, `media`,
`personal_data` — and `tests/test_fixture_consistency.py` asserts them. Those
modules are the authority on what these files claim. Read them before changing
one of these files, and run `python3 -m tests.fixture_checks` for the
block-type coverage table.

## The two valid corpora

⭐ **`depth1/` is the common case, not the exotic one.** Two of the four
designed source shapes are depth 1 — SPARQL (`["course"]`) and ISO-8583
(`["group"]`; spec §1 is right and §4's table row is stale). It is given at
least the care `depth2/` gets, and it exercises two things `depth2/` does not:
a unit with **two** archive documents, and real media on disk with real
digests.

| | `depth1/` | `depth2/` |
|---|---|---|
| Shape it stands for | SPARQL, ISO-8583 — **2 of the 4** | Java-senior, CodeSignal |
| `levels` | `["course"]` — **1** | `["section","module"]` — **2** |
| Containers | 1 | 2 |
| Units | 3 (4 archive documents) | 5 (3 + 2) |
| Variants | 1 (`prose`) | 1 (`java`) |
| Exercises | **zero** | 2 practices |
| Placement | `tree` | `sibling` |
| `permitted_edits` | `[]` — the normal case | one `pom.xml` insert (R3) |
| `media` in the manifest | **absent** — the default case | declared, `auto` + limits |
| Authored overlay | none | `basics/01-getting-started` unit 1 only |
| Block types exercised | 10 of 11 (no `video`) | **11 of 11** |

`depth1` exists to keep the 1-level and no-exercise paths first-class from
wave 0 rather than discovered late. ⛔ **A corpus with no graders is complete,
not short** (spec §7, C5) — nothing here should be read as a degraded corpus.

`depth2` carries, deliberately, one unit **with** an authored overlay
(`units/unit-01/content.json`) and two **without**, because SF-10's two shapes
— derived and authored — are different code paths and each needs an input.

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
| `basics/01-getting-started` 1 | a lesson, a practice, the authored overlay | SF-10(b), and a practice's three-section layout |
| `basics/01-getting-started` 2 | `table`, `rule`, no overlay | SF-10(a), the derived shape |
| `basics/01-getting-started` 3 | a `video` block, a `video` record, `media_skipped` | media named and deliberately not fetched |
| `advanced/02-going-further` 1 | a lesson, a practice, `url_slug` | a second container, SF-05's carried field |
| `advanced/02-going-further` 2 | a closing lesson, plus a fenced Maven POM | a container whose last unit has no exercise; fence awareness at depth 2 |

## Fence awareness — the highest-value thing in this set

⛔ **A parser that scans for `<` without tracking fences is wrong, and it fails
silently.** The spec's C3 says 18 ISO files contain raw HTML. A recount with
code fences stripped found **0 of 38**: all 26 `<tag>`-shaped matches were XML
*inside fenced code blocks* — Maven POM, Spring beans, jPOS config. The "18"
was counting angle brackets.

So `depth1` unit 3 `lesson-2.json` carries three fenced blocks of XML and HTML
— one of them a fence *about* a `<details>` — **and** a raw `html` block, in one
document. Coverage of each block type separately cannot prove a parser tells
them apart; only material where the two are the same text can.
`test_the_same_tags_appear_fenced_and_raw_in_one_corpus` asserts that overlap
still exists, so it cannot be edited away by accident.

⚠️ **The overlap is now exactly `<p>` and `</p>`, and that is load-bearing.**
Once real disclosures became `disclosure` blocks, the only raw `html` left in
`depth1` is the callout — so the callout **must** contain a `<p>`, or the test
goes red for a reason that has nothing to do with fences. It is the one thing
in this change that bites if forgotten.

⚠️ **The recount does not weaken the vocabulary requirement — it relocates
it.** `rule`, `quote`, `html` and `disclosure` are all needed at **M1**: the
disclosure is a *SPARQL* requirement (6 of 19 lessons, every one of them hiding
an exercise answer), and thematic breaks (10 lessons) and blockquotes (1) are
the *Java corpus's*. All four appear in both corpora here.

## The invalid corpora

`invalid/<name>/` is a complete, tiny corpus that is valid in **every respect
but one**. Each carries a `VIOLATION.md` naming the rule it breaks, the file
that breaks it, and what `studyforge validate` (SF-25) is expected to say.

| Fixture | The one rule broken |
|---|---|
| `bad-corpus-api/` | R9 — unknown `corpus_api`, refused rather than migrated |
| `address-directory-mismatch/` | §6 — a container map's address must match the directory holding it |
| `digest-mismatch/` | §6 — `content_sha256` must cover the blocks |
| `ordinal-gap/` | §6 — unit ordinals contiguous from 1 |
| `personal-data/` | R7 — `assert_clean` must refuse, never rewrite |

⚠️ **`invalid/personal-data/` deliberately contains personal-data shapes.**
Both values in it are fabricated — an obviously-placeholder absolute home path
and an address under the RFC 2606 reserved `.invalid` TLD, which can never be
delivered. Nothing in it came from any real machine, account or person, and
its own `VIOLATION.md` says so. **A repository-wide R7 sweep (SF-08) must
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

`rule`, `quote`, `html` and `disclosure` are SF-07's additions and are not
speculative: 10
Java lessons use `---` and one uses a blockquote, and 6 of 19 SPARQL lessons
end in a `<details>` disclosure. ⚠️ Spec §1's "18 ISO files contain raw
HTML" does **not** survive a recount and is not the reason — see *Fence
awareness*. `video` is in the archive vocabulary but is not something the
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
```

⚠️ **`archive/` is a placeholder for `<archive-root>`, which placement owns
(SF-03).** Under the `sibling` profile the real root is `.studyforge/archive/`;
the fixtures use a plain directory so they can be browsed. A consumer of these
fixtures should take the root as a parameter, never as a constant.

## Golden files

The fixtures **are** the golden files for the artefacts the spec pins down —
the manifest, the container map and the archive document, each written in its
canonical form, so a round-trip is a byte comparison against the file itself.

⛔ **Nothing else has a golden file, and that is deliberate.** SF-10, SF-11 and
SF-12 are unwritten; a golden for output nobody has designed is a fixture that
will be wrong and will be trusted. `docs/tasks/handoffs/FND-04.md` lists every
deferred golden and the task that owes it.
