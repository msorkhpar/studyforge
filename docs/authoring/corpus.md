# What a corpus is

**A corpus is your material plus one file that says what it is.** That file is
`corpus.json`, it sits at the root of your repository, and it is the only place
anything about *your* material is written down.

**Everything that differs between two sources and is not the source's own
content is a field in this file.** That is what makes "every corpus is
different" and "every artifact is generated" both true at once. If your corpus
needs something this file cannot express, **the manifest is missing a field**
— that is a defect to report, and it is never a reason to hand-edit generated
output.

---

## The whole file

```json
{
  "corpus_api": 2,
  "source": "field-notes",
  "title": "Field Notes on Distributed Systems",
  "levels": ["chapter"],
  "variants": ["prose"],
  "exercises": false,
  "placement": "tree",
  "content": {
    "include": ["chapters/*.md"],
    "exclude": [
      {
        "path": "chapters/all-chapters.md",
        "why": "whole-book aggregate: an ordered concatenation of the chapters beside it, so ingesting it would read every unit twice"
      }
    ],
    "not_material": [
      {
        "glob": "README.md",
        "why": "the repository's own navigation; the generated site carries its own contents"
      },
      {
        "glob": "LICENSE",
        "why": "the repository's licence; it teaches nothing and is withheld from nobody"
      }
    ]
  }
}
```

**That is a realistic manifest, which means it omits the optional keys it does
not need.** It is an instance, not the contract. The contract is the table
below.

---

## Every key

**Every key a manifest may carry. The ones marked required have no default.**

| Key | | What it says |
|---|---|---|
| `corpus_api` | **required** | Which version of this format the file speaks. An unknown value is **refused**, never quietly migrated. This build reads `1` to `5`; `2` added `content.not_material`, `3` added `media.max_files`, `4` added `runtimes` and `5` added `narration` |
| `source` | **required** | An id for the corpus — a short stable name. **Not a URL to fetch from** |
| `title` | **required** | What the reader sees at the top of the site |
| `levels` | **required** | Names your container levels, and by its length fixes the depth of every address |
| `variants` | **required** | Filing and presentation only. A variant is *not* a thing that runs |
| `exercises` | **required** | Whether this corpus is on the execution track at all. `false` is an answer |
| `runtimes` | *optional* | Which runtimes your material's commands need, by name. Absent means none, and a corpus with none needs no runner |
| `narration` | *optional* | Whether the site speaks. `false` is a site with no voice: no player, no clip served, nothing called missing. Absent means narrated whenever clips are recorded |
| `placement` | **required** | `tree` or `sibling` |
| `content` | **required** | Which of your files are read in, which are deliberately not, and which are not prose at all |
| `media` | *optional* | Whether generated narration is committed, and the limits past which the build stops. A corpus with no media declares nothing |
| `permitted_edits` | *optional* | Defaults to `[]`. The enumerated set of existing files a build may add a line to. An empty list is the normal case |

**A key this table does not name is refused.** So is a required key that is
missing. Both fail at the moment the manifest is read, before anything else
happens, because nothing downstream can be judged without it.

---

## `levels` is the shape of your material

**`levels` names your container levels and its length is the depth of every
address in the corpus.** An address is a list of exactly that many segments.

```
"levels": ["chapter"]                 depth 1 — chapters/units.       e.g. ["algebra"]
"levels": ["section", "module"]       depth 2 — sections/modules/units e.g. ["basics", "01-getting-started"]
```

**Depth 1 is not a degenerate case and it is not second class.** A flat set of
chapters, papers or notes is depth 1, and the entire framework works on it.
[Worked examples](examples.md) works one through end to end for exactly this
reason: a reference that only ever demonstrates the complicated shape teaches
people that the simple shape is unsupported.

**A container holds units; a unit holds documents.** `levels` names the
containers only. Units are numbered, not named, at every depth.

---

## `content` has three states, and the third is the one people miss

**`content` answers one question per file: is this file's prose read into the
archive?** It is not a statement about importance.

| State | Takes | Needs a reason | Means |
|---|---|---|---|
| `include` | plain globs | no | **read in** |
| `exclude` | one named `path` per entry | **yes — a `why`** | prose that *would* be read, deliberately withheld from the reader |
| `not_material` | globs | **yes — a `why`** | **not prose to read at all** — the repository's own scaffolding |

**The asymmetry is deliberate: an inclusion needs no justification; every
declaration that the framework will *not* read a file does.** An excluded file
is material being kept from the reader, and a withholding nobody has to explain
is one nobody audits.

**Two states were not enough, and the measurement is why.** Counted against one
real repository: of 141 files, 38 were included, 3 excluded, and **100 were
neither** — a licence, ignore files, an IDE workspace, a graph cache. Only 3 of
that hundred were material withheld from anybody. Filing the rest under
`exclude` makes every `why` a small lie and produces an audit nobody reads.

**Your own `README.md` is `not_material`, and it is not a special case.** It is
your repository's navigation, and navigation is scaffolding. The reader loses
nothing: the generated site carries its own contents.

### What happens to a file you did not classify

**It is reported, and the corpus is invalid until you say something about it.**
A file matching none of the three is `unclassified`, and that is a refusal
rather than a shrug — silence is exactly the failure the three states exist to
prevent.

**A file matching `include` *and* `not_material` is also refused**, under its
own rule. Deciding by rule order which one wins would settle by accident
something nobody declared.

**Reasons have a floor.** A `why` shorter than 20 characters is refused, which
is only there to stop `"why": "n/a"` from being a way through.

---

## `permitted_edits` — the one way a build may touch a file you wrote

**Generation only ever adds.** No file that existed in your repository is
moved, renamed or rewritten. The single exception is an edit your manifest
*declares*, and a declaration carries four things: the `path`, the `kind`, what
to insert and where, and the `why`.

```json
{
  "permitted_edits": [
    {
      "path": "pom.xml",
      "kind": "insert-line",
      "anchor": "<modules>",
      "content": "  <module>practice</module>",
      "why": "the build compiles only what sits on a source root, so the generated practice module has to be listed"
    }
  ]
}
```

**`insert-line` is the only kind there is.** Additive, reversible, and the
reversal is recorded so the edit can be undone.

**An empty list is a pass, not an omission.** Most corpora need no edits at
all, and the checker reads your declaration rather than knowing anything about
your repository.

---

## `media` — narration, and the limit that stops a build

**Generated narration is committed by default**, because *regenerable* is not
the same as *available*: a clone that carries its own audio speaks with no
service, no GPU and no network.

| Field | Default | |
|---|---|---|
| `commit` | `"auto"` | `always`, `never` or `auto` |
| `max_total_bytes` | `5000000000` | the whole corpus's media |
| `max_file_bytes` | `104857600` | any one clip |
| `max_files` | *none* | how many clips there may be. **Needs `corpus_api: 3`** |

**`max_files` is the one you cross while the byte limits are fine.** Narration
makes many small files: 20 000 clips at 20 KB each is 400 MB, which is under
both ceilings above, and it is still 20 000 paths every `clone`, `status` and
`checkout` pays for. It has **no default** — leave it out and there is no
ceiling on the count — because the two byte defaults come from a measurement
and nobody has measured a count. Declaring it is how you say your repository
has one.

**Crossing a limit stops the build and says so, naming the number and the
limit — the count for `max_files`, the file for `max_file_bytes`.** It never silently starts ignoring media — which would produce clones
that are silent with no error — and it never silently keeps committing. The
default ceilings are not arbitrary: one real corpus reached 11.42 GiB of packed
history against a ~5 GB soft limit, with a single 150.9 MiB file against a hard
100 MiB block, and found out when the push became impossible.

---

## `runtimes` — what your material needs to run

**A list of names, never versions.** You say *which* runtimes a runner must
carry; the runner image chooses *which version* of each, once, for every
corpus. **Needs `corpus_api: 4`.**

```json
{ "exercises": true, "runtimes": ["java", "maven"] }
```

That is the fragment; the rest of the file is as above.

| Name | |
|---|---|
| `java` | a JDK |
| `maven`, `gradle`, `kotlin` | each **needs `java` in the same list** — nothing is inferred |
| `node` | Node.js and its built-in test runner |
| `python` | Python and pytest |
| `shell` | `bash` |
| `sqlite` | the SQLite engine — named for the engine, because *SQL* is a language |

**Order does not matter**, and each name appears once. A name outside the list
above is refused, and so is `runtimes` beside `exercises: false`: a corpus that
sets no runnable work needs no runner.

**Leave it out and your corpus declares no runtimes.** That is a complete
answer, not a gap: the site reads, narrates and navigates with no container at
all. `exercises: true` without `runtimes` is fine too — exercises nobody runs
still need nothing to run them.

---

## `narration` — whether the site speaks

**Narration is optional.** In the words of the ruling that made it so: *"it
should be optional and while serving or even while caputring the matterial
skills should ask if user is interested in the narrition or not. Somebody might
wants to just cover the course wihtout voices as mentioned the voice might be
cgenerated but still not serving them would be an option"*. **Needs
`corpus_api: 5`.**

```json
{ "narration": false }
```

That is the fragment; the rest of the file is as above. The onboarding skill
asks you and writes it; you do not type it.

- **`false`** builds and serves the reading floor exactly: no player on any
  page, no clip served, no notice that anything is missing. Practices, quizzes,
  progress and contents are unchanged. **It is a complete site, not a short
  one.**
- **`true`** plays the clips `studyforge narrate` records.
- **Leave it out** and the site plays clips whenever they are recorded, which is
  how every corpus behaved before the key existed.

**Nothing is deleted.** With `false`, clips already on disk stay where they are
and are simply not served. `studyforge build` and `studyforge serve` take
`--narration` or `--no-narration` to override your answer for one run, and a run
with narration on plays the same clips again without synthesising anything.
`studyforge serve --no-narration` refuses a site that was built with narration
and tells you to build again with `--no-narration`, because the player is part
of each page.

---

## Next

- [Placement](placement.md) — what `tree` and `sibling` do, and how to see
  every path before one is written.
- [What an adapter must produce](archive.md) — the other half of your job.
- [Worked examples](examples.md) — two complete manifests, both runnable.
