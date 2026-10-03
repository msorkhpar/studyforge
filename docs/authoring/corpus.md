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
| `corpus_api` | **required** | Which version of this format the file speaks. An unknown value is **refused**, never quietly migrated. This build reads `1` to `8`. A key needs at least the version that introduced it: `2` for `content.not_material`, `3` for `media.max_files`, `4` for `runtimes`, `5` for `narration`, `6` for `onboarding_doc`, `7` for `curriculum` and `8` for `curriculum.linked` and for a `not_material` glob that opens `*/` |
| `source` | **required** | An id for the corpus — a short stable name. **Not a URL to fetch from** |
| `title` | **required** | What the reader sees at the top of the site |
| `levels` | **required** | Names your container levels, and by its length fixes the depth of every address |
| `variants` | **required** | Filing and presentation only. A variant is *not* a thing that runs |
| `curriculum` | *optional* | Which document records your reading order and grouping, the address each of its groups is filed at, optionally the filename prefix each group's files carry, as a check, and whether the record opens each container of your last level with a linked entry. Absent means your adapter reads its record itself |
| `exercises` | **required** | Whether this corpus is on the execution track at all. `false` is an answer |
| `runtimes` | *optional* | Which runtimes your material's commands need, by name. Absent means none, and a corpus with none needs no runner |
| `profile` | *optional* | The toolchain image profile your runner and editor are built on, beyond the base of your `runtimes`: a name, such as the toolchain lists it. Needs `runtimes`; absent means the bases alone |
| `live` | *optional* | Which examples and practices may be run live against a reader's own API key: one host, the name of the variable the key is given under, and what runs. Needs `runtimes`; absent means no live run |
| `narration` | *optional* | Whether the site speaks. `false` is a site with no voice: no player, no clip served, nothing called missing. Absent means narrated whenever clips are recorded |
| `onboarding_doc` | *optional* | Where onboarding writes the document a reader opens first, as a path inside the corpus ending `.md`, or `false` for none. Absent means `ONBOARDING.md` at the root |
| `languages` | *optional* | The languages a section may be tagged with: a list of `{id, label, fence_labels}`. Absent means no tagging and today's behaviour |
| `modes` | *optional* | The reading modes a reader chooses between: a list of `{id, label, summary, prose, tabs, practices}` and an optional boolean `practice_choice`. Needs `languages`; absent means no question |
| `default_mode` | *optional* | The id of the mode shown without scripts. Needs `modes`; absent means the first declared mode |
| `outside_mode` | *optional* | What an entry does in a mode that does not show its language: `open` or `locked`. Needs `modes`; absent means `open` |
| `absent_language` | *optional* | What an example block and a practice show for a language they lack: `hide` or `grey`. Needs `modes`; absent means `hide` |
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

### A `not_material` glob is a path, a directory's wildcard, or one name in every directory

A `not_material` entry is an exact path (`LICENSE`), or a wildcard under a
directory that is itself entirely not material (`scripts/**`). A wildcard with
no directory in front of it, such as `*.xml`, is refused: its reason could not
be true of a file nobody has written yet.

**A repository of many uniform modules keeps the same scaffolding in each of
them**, and saying so once per module is one copy of one reason per module.
So one more form is accepted: `*/` followed by a fixed name, meaning that name
in every directory at the root. **Needs `corpus_api: 8`.**

```json
{
  "content": {
    "not_material": [
      { "glob": "*/pom.xml", "why": "each module's build file: it builds the examples and teaches nothing itself" },
      { "glob": "*/src/**", "why": "each module's sources and tests: code the practices are built from, not prose to read" }
    ]
  }
}
```

What follows the `*/` is judged like any other entry, so `*/*.md` and `*/**`
are still refused. A material file one of these sweeps up is also matched by
`include`, and that is refused as `contested`, so nothing is lost in silence.

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

**`never` keeps the clips out of git, and nothing else.** The generated
`.studyforge/.gitignore` then covers each unit's `audio/` directory. The copies
of images, video and attachments a page shows stay committed, because they are
copies of files your archive commits and a clone's pages reach for them.
[Placement](placement.md) lists every media directory and whether it is
committed.

**A corpus that does not commit its clips publishes them as release volumes.**
With `commit` set to `never`, `studyforge narrate <root> --pack <dir>` packs
every clip the narration record locates into stored zip volumes of at most
999 MB, with a `SHA256SUMS`, in a directory outside the corpus, and writes two
restore scripts into `.studyforge/narration-release/` with the volumes' digests
and a `clips.sha256` naming every clip. Commit all of it: a
restore trusts only these committed digests, so it refuses a wrong or replaced
release and never writes a file that is not one of the corpus's clips.
`studyforge narrate <root> --publish <dir>` is a dry run: it checks every
volume and prints the one `gh release create` command that attaches them to a
release of the checkout's `origin`, under the tag (`--tag`, default
`narration-1.0.0`). The framework uploads nothing; you run that command with
your own `gh` login. A tag's release is created once: for new clips, pack
again under a new tag, or replace the assets with the `gh release upload …
--clobber` line the dry run prints. After you upgrade the framework, pack
again before you publish. A corpus whose `commit` is not `never` is not packed
at all: its clones already carry the clips. A reader
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

**What is spoken is a lesson's prose**: headings,
paragraphs, list items, table rows and a disclosure's summary. A practice, a
code example and a quiz are shown and never spoken, and no caption stands in
for a code example. A lesson's code-example panel is a code example: a list whose every item is one link to a code file and a short label
(`Source: …`, `Test: …`) says nothing, and a heading whose blocks hold such a
list and nothing spoken (the *Code Examples* heading) says nothing either. A corpus
narrated before this limit keeps every prose clip;
`studyforge narrate <root> --prune` retires the clips no page plays any more.

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
finds out by asking for its first clip, once: if that clip does not load, it
asks for no other clip and hides every narration control. That one request is
one error line in the browser's console, `404` served or `ERR_FILE_NOT_FOUND`
over `file://`. A page built with no clip on disk still links every clip its
narration record names, so once the clips are restored into place the next page
load plays them without a rebuild, opened as files or served alike. A site
built by an earlier version may still hold `.studyforge/assets/narration-clips.js`,
which no page reads any more: the build names it on a `retired` line and leaves
it, so delete it and commit the deletion.

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

## `profile` — an image profile as the base of your layers

Optional. A toolchain may carry profiles: images layered on the base of a declared set that hold
what not every corpus needs, such as pinned Python wheels, npm packages or JVM jars for offline
practices. Name one in `profile` and the export builds the runner's and the editor's course
layers on that profile's images instead of the plain bases. The key needs `runtimes` and at least
the runtimes the profile layers on, which the toolchain checks when the course is exported. The
framework names no profile; the name is yours. A course that names a profile is exported thin
only, with a bases lock that carries a `profile` entry (see the execution skill, *A course's main
stands alone*); a corpus with no `profile` is exported exactly as before.

## `live` — runs against a reader's own key

Optional, and a corpus without it is built and served exactly as before. A corpus that teaches a
service whose real API a reader may call with their own key can name the examples and practices that
may run that way: `{"host": "api.example.test", "key_variable": "EXAMPLE_API_KEY", "examples":
[{"path": "examples/a/run.py", "command": ["python3", "examples/a/run.py"]}], "practices":
["<practice key>"]}`. `host` is the one bare lower-case hostname a live run may reach; the framework
names none. `key_variable` is the NAME of the environment variable the reader's key is given to a live
run under, never a value. An example is a code file a page links and the argv that runs it (the same
safe form a practice's command has); a practice runs its own `run_command`. The key needs `runtimes`.

The reader types the key in the served site; it is kept in the browser (the tab only, unless they opt
in to keeping it on the device) and sent only in the body of a live-run request. A live run happens
only in a course served from its own compose with the `live` profile; a read-only preview and a
corpus served any other way show no key field and no control. Live runs are never graded.

**What a live-capable example may and may not contain.** A live example is ordinary code with one
extra property: it can be started with a key. So that no key can ever rest in the course:

- ⛔ **No key, anywhere in the corpus.** Not in the source, the command, a fixture, a recorded
  exchange, a log, a comment or a test. The example reads the variable the manifest names, by that
  name, from its environment; it reads no file for it, and the framework reads none either.
- ⛔ **No captured secret.** A recorded exchange shown on a page carries no key, header, request
  id, organisation id or token, and is labelled as captured, with the model and the date.
- ⛔ **The key is never printed or kept.** The program does not print its environment, its client
  configuration or a request's headers, and it writes the key to no file; an error it prints names
  what failed and never the value it was given.
- **One host.** It reaches only the host the manifest names; a second host is refused by the
  proxy and is a defect of the example.
- **A command is argv**, written in the safe form the manifest checks, never a shell string.
- **Grading is separate.** The example's offline test, the one a Run or a Submit uses, runs
  against the course's scripted stand-in with no key and no network; the live command is another
  argv beside it. A live-capable practice is graded exactly as before; the live run is never graded.

## `languages` and `modes` — reading modes

All four keys are optional, and a corpus that declares none is read exactly as before.
`languages` lists `{id, label, fence_labels}`; a fence label belongs to one language.
`modes` lists `{id, label, summary, prose, tabs, practices}` with an optional boolean
`practice_choice`: `prose` is one declared language id, `tabs` and `practices` are lists
of declared language ids, each named once. `modes` needs `languages`; `default_mode` (a
declared mode id, the first mode when absent) and `outside_mode` (`open`, the default,
or `locked`) need `modes`. A manifest is refused by name for an undeclared language, a
repeated id, a shared fence label, a `default_mode` that is no mode or an `outside_mode`
that is neither value. The keys need `corpus_api` 8, which this build already writes;
validation never asks a unit to have anything in a language.

**What a reader sees.** A corpus that declares `modes` writes `modes.css` and `modes.js`
beside `page.css` and `page.js`, and every page carries a switch listing the declared
modes. On a first visit a card asks which one to read, listing each mode's label and
summary; the choice is kept in the browser the way the theme is, through guarded reads
and writes, so a page where the browser refuses storage still renders and simply asks
nothing. A mode shows the sections tagged with its `prose` language and the untagged
ones; the page's outline drops the lines that point at hidden sections. With scripts
off, in a crawl, and before an answer, a page shows the `default_mode` view: the root
element carries `data-mode` with that value and the stylesheet keys on it. A page opened
from a file asks on every load. A corpus that declares no `modes` gets none of this: no
switch, no question, no script, no style and no file.

**An entry with nothing for the mode.** A unit whose sections are all tagged, and a
module whose units all are, is never hidden: in a mode that does not read its languages
its row in the index, the rail and the module's list stays, greyed, with a label naming
its languages (`data-entry-lang` on the row; a unit with any untagged section is read in
every mode and carries nothing). Under `outside_mode: open` it is greyed and still a
link; opening it shows every section in its own language under a one-line note naming
the modes that read it normally, and the previous and next links walk through it. Under
`locked` its row is an anchor with no `href`, `aria-disabled`, out of the tab order (the
address stays in `data-href` and comes back when a mode that reads it is chosen); the
previous and next links pass over it (the bar holds the neighbours up to the first one
every mode reads, and shows the first the chosen mode opens); and a direct link to it
shows only a note naming the modes that read it with a control for each. In both
settings the counts (`of N read` on a group, the progress line and strip, the Up next
slip, a module's unit count) cover the pages the mode reads. A link to a section the mode
hides shows that section while the link is the target. With scripts off the page is the
`default_mode` view in every respect, including which rows are closed and what the bar
shows.

**An example with a tab for each language.** An `example` block holds from one to eight
tabs, each naming a declared language once; validation refuses a ninth, a repeated language and
an undeclared one, and the Markdown marker `<!-- example: <id> tabs: a,b,c,d -->` refuses the
same. A mode's `tabs` list says which of the block's tabs the mode shows and in what order: the
first it lists opens, a click changes that block only, and a mode that lists one language shows
that tab and no bar. At phone width the bar wraps inside the block, every tab is at least 44 px,
and the keys are those of the WAI-ARIA tabs pattern (Left and Right wrap, Home, End, one tab in the
tab order). With scripts off every panel is present under its language's label.

**A section for several languages.** A section, a lesson or a practice may be tagged with several
declared languages (`lang` names them, joined by single spaces; the Markdown marker writes
`<!-- lang: a,b -->`). It reads in the mode of each of them and in no other, its unit belongs to
each of them, and the note a page outside a mode shows names every mode that reads it. A corpus
whose sections each name one language builds the style rules it always did; the rules match a tag
as a list of words only once some section names several.

**Any number of languages and modes.** The framework counts neither: a corpus of one, two, three
or four languages is read the same way, the first-visit question and the switch list exactly the
declared modes, and nothing in the framework names a language.

**A language a block or a practice lacks.** `absent_language` (`hide`, the default, or `grey`;
needs `modes`) decides what an example block and a practice card show for a declared language they
are not written in. Under `hide` they show nothing for it, as they always did. Under `grey`:

- an example block has, for each declared language it has no tab for, a **disabled tab**
  (`aria-disabled`, no panel, still focusable so its reason can be read; a click selects nothing and
  the arrow keys, Home and End still reach it without selecting it), and one sentence,
  `Available in: <languages>.`, naming the languages that do carry it, built from the corpus's own
  `languages`. A mode that lists none of the block's languages still shows the block, with the
  disabled tab and the sentence, never hides it; the first enabled tab the mode lists opens;
- a practice card carries the languages its section is tagged with and a sentence naming them; in a
  mode whose `practices` list holds none of them the card is greyed, its link is `aria-disabled`
  and does not open, and Previous and Next in the practice workspace pass over it; a practice a
  mode lists reads in its own language whatever that mode's `prose`, and its panel is tagged so
  a mode that hides its statement hides it too;
- a read-only preview keeps all of it: the panel's note replaces the panel, the banner is
  unchanged, and the page reads the default mode until a question is answered (a page opened from a
  file asks on every load).

A corpus that leaves the key out, or says `hide`, builds to the bytes it always did.

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
  that group is filed, one segment per level in `levels`, **written as one key
  joined by `/`**: `"basics/01-getting-started"` at depth 2, never the list
  that `container.json` writes. The units are the record's entries under each
  label, numbered by their position; an ordinal the record writes must match
  that position.
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
address it asks you to confirm, a prefix only where every file already agrees
with the record, and `linked` only where the record opens every container of a
two-level corpus with a linked entry.

### `linked` — when the record opens each container with a link

**Some records write the last level as linked entries rather than labels.** A
section is a bare line, and under it each module is a list entry linking the
module's own contents page, with the module's units indented beneath it:

```
1. Getting Started

- [1.1. First Steps](01-first-steps/README.md)
    - [1.1.1. Installing](01-first-steps/lesson_1.1.1.md)
    - [1.1.2. Running](01-first-steps/lesson_1.1.2.md)
- [1.2. Next Steps](02-next-steps/README.md)
    - [1.2.1. Configuring](02-next-steps/lesson_1.2.1.md)
```

Declare the labels as the groups one level up, and name your last level in
`linked`. **Needs `corpus_api: 8`.**

```json
{
  "levels": ["section", "module"],
  "curriculum": {
    "record": "README.md",
    "containers": [{ "label": "Getting Started", "address": "getting-started" }],
    "linked": "module"
  }
}
```

- **Each linked entry opens one container** of the level `linked` names, which
  must be the last of `levels`. Its address is the label's address followed by
  the name of the directory holding the page it links, `getting-started/01-first-steps`
  here, so that name has to be usable as an address segment. Its titles are the
  label's and the entry's, and the linked page is its `origin`.
- **Its units are the entries indented beneath it**, in the record's order. An
  entry nested beneath another unit is a unit of the same container, in its
  place, and every unit keeps the record's ordinal as its label, so `1.1.2.1`
  still reads as nested. An ordinal must be its place among its siblings: the
  entries at its depth under the same parent.
- **The linked pages are not units.** Declare them `not_material`
  (`*/README.md` here); an `include` that read them would be read by no unit.
- **The count the audit checks** is the included files in each linked page's
  directory, taken without the record.
- **A record that does not have this shape everywhere is refused**: a unit
  above a group's first linked entry, a linked entry with no unit beneath it,
  or two containers linked from one directory. A group declares no `prefix`
  under `linked`.

**Leave it out and nothing changes.** Your adapter reads its record itself, as
any adapter may.

---

## Next

- [Placement](placement.md) — what `tree` and `sibling` do, and how to see
  every path before one is written.
- [What an adapter must produce](archive.md) — the other half of your job.
- [Worked examples](examples.md) — two complete manifests, both runnable.
