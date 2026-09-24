# Worked examples

**Two complete corpora, both in this repository, both of which you can run the
commands against right now.** The commands below are run from the root of your
framework checkout. `tests/fixtures/` holds other corpora for the framework's
own tests; these two are the ones to copy from.

**They are deliberately the two ends of the range.** One is a repository-shaped
source with two container levels, graded practices and a declared edit to a
build file. The other is a flat set of prose with one level and no exercises at
all.

**The flat one is here because a reference that only demonstrates the
complicated case teaches people that the simple case is unsupported.** It is
not: depth 1 is fully supported.

| | **A — flat prose** | **B — a repository with exercises** |
|---|---|---|
| Where | `tests/fixtures/depth1/` | `tests/fixtures/depth2/` |
| `levels` | `["course"]` — depth **1** | `["section", "module"]` — depth **2** |
| Containers | 1 | 3 |
| Units | 3 | 6 |
| Archive documents | 4 — one unit has two | 8 — of which 2 are practices |
| `variants` | `["prose"]` | `["java"]` |
| `exercises` | **`false`** | `true` |
| `placement` | `tree` | `sibling` |
| `permitted_edits` | `[]` | one `insert-line` into `pom.xml` |
| `media` in the manifest | **absent** — the default | declared, with limits |

---

## A — flat prose, no exercises

**The manifest**, in full, from
[`tests/fixtures/depth1/corpus.json`](../../tests/fixtures/depth1/corpus.json):

```json
{
  "corpus_api": 1,
  "source": "depth1-demo",
  "title": "Depth One Demo",
  "levels": ["course"],
  "variants": ["prose"],
  "exercises": false,
  "placement": "tree",
  "content": {
    "include": ["depth-one/*.md"],
    "exclude": [
      {
        "path": "depth-one/ALL.md",
        "why": "whole-series aggregate: an ordered concatenation of 01, 02 and 03, identical to them joined. Ingesting it would read every unit twice."
      }
    ]
  },
  "permitted_edits": []
}
```

**Read what it does *not* say.** No `media` block — the defaults apply and a
corpus with no media declares nothing. No `not_material`, so `corpus_api` `1`
is enough; a manifest may declare the lowest version its keys need.
`permitted_edits` is empty, which is the ordinary case and a pass.

**`exercises: false` is the interesting field.** This corpus is finished. It
has no practice documents, no `exercise` keys and no graders, and none of that
is missing.

**The one `exclude` entry is the shape to copy.** `depth-one/ALL.md` is a
concatenation of the three chapters beside it. A `depth-one/*.md` glob would
otherwise read every unit twice and nothing would complain — that is the whole
reason `exclude` carries a `why`.

**The tree:**

```
tests/fixtures/depth1/
  corpus.json
  archive/depth-one/container.json
  archive/depth-one/raw/prose/unit-01/lesson-1.json
  archive/depth-one/raw/prose/unit-02/lesson-1.json
  archive/depth-one/raw/prose/unit-03/lesson-1.json
  archive/depth-one/raw/prose/unit-03/lesson-2.json
```

**Unit 3 has two lesson documents.** Nothing says a unit is one document.

**Check it:**

```
studyforge validate tests/fixtures/depth1
```

```
.: [origin-not-a-file] not checked — none of the 4 declared origin path(s) is on disk, so whether each names a file rather than a directory could not be checked
.: [unclassified] not checked — no source material is present beside the archive, so there is nothing to classify
.: [short-read] not checked — none of the 3 declared origin file(s) is present, and no file under the corpus root is source the manifest's 'content' declares, so the source tree is absent and no unit's completeness was checked
valid: 0 finding(s), 3 unchecked claim(s)
```

**Exit `0`.** The three unchecked claims are the checks about *source files*,
and this fixture is an archive with no source tree beside it — so the checker
says it could not put those questions rather than passing them.

**See what a build would create:**

```
studyforge plan tests/fixtures/depth1
```

Its last line, `plan:`, counts each kind of line above it, and one of its
counts is `0 file(s) to edit`. **Zero files to edit** — that is
`permitted_edits: []` read back to you.

---

## B — a repository with two levels and graded practices

**The manifest**, from
[`tests/fixtures/depth2/corpus.json`](../../tests/fixtures/depth2/corpus.json):

```json
{
  "corpus_api": 1,
  "source": "depth2-demo",
  "title": "Depth Two Demo",
  "levels": ["section", "module"],
  "variants": ["java"],
  "exercises": true,
  "placement": "sibling",
  "content": {
    "include": ["*/*/README*.md"],
    "exclude": []
  },
  "media": {
    "commit": "auto",
    "max_total_bytes": 5000000000,
    "max_file_bytes": 104857600
  },
  "permitted_edits": [
    {
      "path": "pom.xml",
      "kind": "insert-line",
      "anchor": "<modules>",
      "content": "  <module>practice</module>",
      "why": "Maven compiles only what sits on a source root, so the generated practice module has to be listed."
    }
  ]
}
```

**Three things differ from A and each is a decision, not a detail.**

**`placement: "sibling"`** — this repository already has a layout its readers
know, so pages land beside the material they came from rather than in a
parallel tree.

**`permitted_edits`** — one line into `pom.xml`, with the reason. Without it
the build tool would not compile the generated practice module. **That edit is
the only thing in the entire build permitted to change a file that already
existed**, and it exists because the manifest says so, not because anything
knows what Maven is.

**`media`** — declared explicitly rather than defaulted, with both ceilings.
Same values as the defaults; declaring them makes the policy visible in the
one file a reviewer reads.

**The tree**, one container of three:

```
tests/fixtures/depth2/
  corpus.json
  archive/basics/01-getting-started/container.json
  archive/basics/01-getting-started/raw/java/unit-01/lesson-1.json
  archive/basics/01-getting-started/raw/java/unit-01/practice-1.json
  archive/basics/01-getting-started/raw/java/unit-02/lesson-1.json
  archive/basics/01-getting-started/raw/java/unit-03/lesson-1.json
  archive/advanced/02-going-further/...
  archive/advanced/03-putting-it-together/...
```

**The address is two directories deep** because `levels` has two entries, and
`archive/basics/01-getting-started/container.json` declares
`"address": ["basics", "01-getting-started"]`. **The two must agree** — that is
check 1, and a mismatch is the `address-directory` rule.

**Check it:**

```
studyforge validate tests/fixtures/depth2
```

**Exit `0`, zero findings, the same three unchecked claims** — for the same
reason, and with different counts, because this corpus declares more origins.

```
studyforge plan tests/fixtures/depth2
```

**This plan counts `1 file(s) to edit`**, and its `edit pom.xml` lines give the
anchor, the line added, the reason and how the edit is undone. Its pages are
created under each module's own `study/` directory.

---

## What to copy

**If your material is a folder of prose, papers or notes:** copy A. One level,
one variant, `exercises: false`, `placement: "tree"`. You are describing a
book, and the framework has no opinion about that being simpler than a course.

**If your material is a repository with a build:** copy B. Levels that match
your directories, `placement: "sibling"` so your readers keep their bearings,
and `permitted_edits` only if a generated artifact genuinely has to be listed
somewhere for a build to see it.

**Then go back to [the route](README.md)** and run the plan command before you
write a line of adapter code.

---

## A note on these two examples

**They are fixtures, and that is deliberate.** Every invariant they claim is
stated in `tests/fixture_checks/` and asserted by
`tests/test_fixture_consistency.py`, and this page's manifests, trees and
output are compared with them by `tests/test_authoring_reference.py`, so an
example on this page that stopped being true of the shipped code would fail a
test rather than mislead you.
