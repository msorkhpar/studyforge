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
| `corpus_api` | **required** | Which version of this format the file speaks. An unknown value is **refused**, never quietly migrated. This build reads `1` to `7`. A key needs at least the version that introduced it: `2` for `content.not_material`, `3` for `media.max_files`, `4` for `runtimes`, `5` for `narration`, `6` for `onboarding_doc` and `7` for `curriculum` |
| `source` | **required** | An id for the corpus — a short stable name. **Not a URL to fetch from** |
| `title` | **required** | What the reader sees at the top of the site |
| `levels` | **required** | Names your container levels, and by its length fixes the depth of every address |
| `variants` | **required** | Filing and presentation only. A variant is *not* a thing that runs |
| `curriculum` | *optional* | Which document records your reading order and grouping, the address each of its groups is filed at, and optionally the filename prefix each group's files carry, as a check. Absent means your adapter reads its record itself |
| `exercises` | **required** | Whether this corpus is on the execution track at all. `false` is an answer |
| `runtimes` | *optional* | Which runtimes your material's commands need, by name. Absent means none, and a corpus with none needs no runner |
| `narration` | *optional* | Whether the site speaks. `false` is a site with no voice: no player, no clip served, nothing called missing. Absent means narrated whenever clips are recorded |
| `onboarding_doc` | *optional* | Where onboarding writes the document a reader opens first, as a path inside the corpus ending `.md`, or `false` for none. Absent means `ONBOARDING.md` at the root |
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

**Two states are not enough.** In a real repository most of the files that
are not read in are not material at all — a licence, ignore files, an editor's
workspace, a cache — and only a few are material deliberately withheld from the
reader. Filing the rest under `exclude` makes every `why` a small lie and
produces an audit nobody reads.

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
ceiling on the count — because no one count suits every repository. Declaring
it is how you say yours has one.

**Crossing a limit stops the build and says so, naming the number and the
limit — the count for `max_files`, the file for `max_file_bytes`.** It never
silently starts ignoring media — which would produce clones that are silent
with no error — and it never silently keeps committing. The default ceilings
sit under the limits git hosting commonly imposes, about 5 GB for a repository
and 100 MiB for a single file, so a corpus finds out at build time rather than
when a push is refused.

**A corpus that does not commit its clips publishes them as release volumes.**
With `commit` set to `never`, `studyforge narrate <root> --pack <dir>` packs
every clip the narration record locates into stored zip volumes of at most
999 MB, with a `SHA256SUMS`, in a directory outside the corpus, and writes two
restore scripts into `.studyforge/narration-release/`, and sets
`.studyforge/assets/narration-clips.js` to `released`. Commit both.
`studyforge narrate <root> --publish <dir>` is a dry run: it checks every
volume and prints the one `gh release create` command that attaches them to a
release of the checkout's `origin`, under the tag (`--tag`, default
`narration-1.0.0`). The framework uploads nothing; you run that command with
your own `gh` login. A reader
runs `sh .studyforge/narration-release/restore.sh` (or `restore.ps1`) from a
clone: each clip lands where the narration record says, the volumes are
checked before anything is extracted, the downloads are deleted, and last the
script is set to `present`, so the next page load plays the clips. A site you
built into another `--out` keeps its own copies: build it again after a restore.
Narration stays optional: a clone that never restores has a complete site.

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

**Narration is optional.** Some readers want the material without a voice, and
a site without one is complete. **Needs `corpus_api: 5`.**

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
- **Leave it out** and the site plays clips whenever they are recorded.

**Nothing is deleted.** With `false`, clips already on disk stay where they are
and are simply not served. `studyforge build` and `studyforge serve` take
`--narration` or `--no-narration` to override your answer for one run, and a run
with narration on plays the same clips again without synthesising anything.
A build says what it left alone: an `unlinked` line for each clip an earlier
narrated build copied into an `--out` that a build with narration off now
leaves unplayed, and a `stale` line for each clip it plays whose paragraph no
longer says those words. Neither changes its exit code.
`studyforge serve --no-narration` refuses a site that was built with narration
and tells you to build again with `--no-narration`, because the player is part
of each page.

**When the clips are not on disk, a page shows no narration control.** That is
the normal state of a fresh clone whose clips are a separate download. The page
finds out from `.studyforge/assets/narration-clips.js`, a small script the build
writes next to the stylesheet, and never by asking for a clip, so the browser's
console stays clean. A page built with no clip on disk still links every clip
its narration record names, so once the clips are restored into place, and the
restore has set that script to `present`, the next page load plays them without
a rebuild. Served, `studyforge serve` checks the disk itself on every page load.
A build never changes the script from `released`, which is what packing the
clips for release sets, so a site you commit after packing still tells a fresh
clone that its clips have to be fetched.

---

## `onboarding_doc` — where the reader document goes

Onboarding writes one document for a person opening your repository: what the
corpus declares and the commands that run it from a fresh clone. **By default it
is `ONBOARDING.md` at the root.** Say somewhere else, or say you want none.
**Needs `corpus_api: 6`.**

```json
{ "onboarding_doc": "docs/archive/ONBOARDING.md" }
```

- **A path** is relative to the corpus root and ends `.md`: no leading `/`, no
  `.` or `..` segment, no glob character. It may not be a path onboarding
  already writes, or lie under `.studyforge/` or the archive directory.
- **`false`** writes no reader document. The generated pin check then says how
  to install the library itself rather than naming a file.
- **Leave it out** and it is `ONBOARDING.md` at the root.

**Moving the file by hand is not how you move it.** The next re-onboarding
writes it back where the manifest says, and `hand_edited` reports the gap until
then. Declare the place, then re-onboard with
`reonboard('.', settle={"onboarding_doc": "docs/archive/ONBOARDING.md"}).write('.', regenerate=True)`,
from `studyforge.skills.onboarding`, run at the corpus root:
the document is written there, nothing is written at the root, and a copy you
already moved there unchanged is rewritten in place rather than refused. The
copy onboarding wrote at the root is removed, because onboarding no longer
writes it there — unless you edited it, in which case nothing is written and
the refusal names it: move your edited copy out of the generated paths, or
restore it, and regenerate.

---

## `curriculum` — where your reading order is recorded

**Most material records its own order and grouping in one document**: a README,
a table of contents, a summary. Name it here, and name the address each of its
groups is filed at, and the framework files every unit from it. **Needs
`corpus_api: 7`.**

```json
{
  "curriculum": {
    "record": "SUMMARY.md",
    "containers": [
      { "label": "The Basics", "address": "basics", "prefix": "basics-" },
      { "label": "Going Deeper", "address": "deeper", "prefix": "deep_" }
    ]
  }
}
```

That is the fragment; the rest of the file is as above.

- **`record`** is the document, as a path inside the corpus ending `.md`: no
  leading `/`, no `.` or `..` segment, no glob character. It may be the only key.
- **`containers`** lists the record's groups in the record's order. `label` is
  the group's heading exactly as the record writes it, and `address` is where
  that group is filed, one segment per level in `levels`. The units are the
  record's entries under each label, numbered by their position; an ordinal the
  record writes must match that position.
- **`prefix`** is optional, per group: the text before the number in the names
  of that group's files — `basics-` for `basics-3.md`, `s` for `s10.md`, the
  empty string for `10.md`. A prefix holds no digit, `/`, space or glob
  character.

**A prefix never decides where a unit goes.** The record does. The prefix is a
second reading of the same files, and the two must agree: a unit filed under a
group whose prefix its name does not carry, a unit named for another group, or
a file named for a group that the record never lists is refused, by the adapter
and by `studyforge validate` alike. A file your repository ignores is not
counted.

**Each label, address and prefix appears once.** The reconnaissance skill
drafts this block from what it finds: the record, each group with a proposed
address it asks you to confirm, and a prefix only where every file already
agrees with the record.

**Leave it out and nothing changes.** Your adapter reads its record itself, as
any adapter may.

---

## Next

- [Placement](placement.md) — what `tree` and `sibling` do, and how to see
  every path before one is written.
- [What an adapter must produce](archive.md) — the other half of your job.
- [Worked examples](examples.md) — two complete manifests, both runnable.
