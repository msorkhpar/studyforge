# Placement — where the output goes

**You decide where generated files land, and it is one field in the manifest.**
Nothing downstream cares which you chose.

```json
{ "placement": "tree" }
```

---

## The two profiles

| Profile | Where output goes | Use it when |
|---|---|---|
| `tree` | all output under one generated root, in directories that spell the address | your material has no layout worth preserving — a folder of notes, a set of papers, a book split into chapters |
| `sibling` | each artifact in a study/ directory beside the source file it was generated from | your repository already has a layout the reader knows, and moving things would be rude |

**The middle column is the profile's own sentence**, the one `studyforge plan`
prints for you before you choose — not a description of it written here.

**`sibling` is what makes "your files are never touched" liveable.** A reader
who already knows their way around `16-streams-api/` finds the generated pages
in `16-streams-api/study/`, one directory beside the file they came from — not
in a parallel tree they now have to learn. **One directory, whatever the unit
count**, so your own listing stays readable: that is the whole of what `study/`
is for.

**A third profile is added by registering one, and no consumer changes.**
Nothing anywhere downstream names a profile; that is asserted over the whole of
the framework rather than promised.

---

## What gets created

**Both trees below are drawn by the placement code itself**, one line per path
it places, for one container holding one unit. Nothing here is typed out: if a
build would put a file somewhere else, these fences say somewhere else, and the
test that reads this page fails until they do.

Three substitutions, and the rest is literal: **`<address>`** is as many
directories or name parts as your corpus declares levels — the shape is the
same at one and at three; **`<title>`** is the slug of the unit's or the
container's own title; **`<your-directory>`** is whatever directory your source
file was in.

Under `tree`, everything lives under one generated root:

```tree
index.html                                                     the root index
.studyforge/assets/                                            shared css and js
archive/                                                       the adapter's, beside corpus.json
.studyforge/site.json                                          the discovery cache
.studyforge/<address>/<title>.section.html                     the container page
.studyforge/<address>/units/unit-NN/unit-NN-<title>.unit.html  the unit page
.studyforge/<address>/units/unit-NN/audio/
.studyforge/<address>/units/unit-NN/images/
.studyforge/<address>/units/unit-NN/video/
.studyforge/<address>/units/unit-NN/practice/
.studyforge/<address>/units/unit-NN/attachments/
```

Under `sibling`, the shared four do not move and the pages do — into one
`study/` directory beside the material:

```sibling
index.html                                                     the root index
.studyforge/assets/                                            shared css and js
archive/                                                       the adapter's, beside corpus.json
.studyforge/site.json                                          the discovery cache
<your-directory>/study/<title>.section.html                    the container page
<your-directory>/study/<address>.unit-NN-<title>.unit.html     the unit page
<your-directory>/study/audio/<address>.unit-NN-<title>/
<your-directory>/study/images/<address>.unit-NN-<title>/
<your-directory>/study/video/<address>.unit-NN-<title>/
<your-directory>/study/practice/<address>.unit-NN-<title>/
<your-directory>/study/attachments/<address>.unit-NN-<title>/
```

**Your own file is not in either list, and that is the point.** Under
`sibling`, `<your-directory>` keeps everything it already had and gains exactly
one entry — `study/` — whatever the unit count, and the corpus root gains
exactly one generated file, `index.html`.

**A media directory is claimed, not created.** It appears above, and
`studyforge plan` names it, because that is where a clip or an attachment would
go; a build creates it only when it copies a file into it.

**Under `sibling` the media is one directory per kind, with the unit one level
down.** Many units share one `study/`, so the kind is what the listing shows
and the unit's own name discriminates inside it. **The cost is stated rather
than hidden:** one unit's artifacts no longer sort as one run, so deleting a
unit is a page plus one directory per kind — which is why nothing composes
those paths and everything asks for them.

**Every generated page has a real name and is never `index.html`.** Names come
from the unit's own numbering and title, so a directory listing is readable and
a scan is unambiguous. The single `index.html` a build writes is the root
index.

**The name comes from the unit's identity, never from your source filename** —
and under `sibling` it carries the container's address in front, because two
containers whose numbering mirrors each other can share one directory and once
claimed one path between them.

---

## How a page knows what it is

**Every generated artifact carries an identity block inside it** — the corpus,
the address, the unit, the kind, the variant. The server does not infer what a
file is from where it sits; it scans, reads each file's own statement, and
assembles the site from that.

Four things follow, all of them intended:

- **The framework does not care where artifacts are.** Put them where your
  readers will find them natural.
- **A moved page still identifies itself correctly** — it still appears in the
  contents and still resolves as the unit it is.
- **A stale cache is detectable** rather than silently wrong. `site.json` is a
  cache of the scan, never the authority.
- **Two corpora with different profiles are served by one server.**

**One thing does not survive a move, and it is not a defect.** A page's
stylesheet and its sibling audio resolve *relative to the page*, so a moved
page renders unstyled and silent. That is the price of the offline floor: a
unit page opened straight off the filesystem with no server has to address its
assets relatively, and absolute paths would break exactly the case the whole
design is for.

---

## See every path before one is written

**You cannot write your ignore rules, declare your `permitted_edits` or review
what is about to happen to your repository without knowing every path the build
will create.** So placement is askable before it is exercised:

```
python3 -m studyforge.cli.plan <your-repository>
```

It reads the manifest alone — nothing is generated — and prints:

- every path that will be **created**, with what it is;
- every existing file that will be **edited**, and the declared reason;
- the **ignore lines** the media policy requires, each with the file inside the
  generated root that holds it — none while media is committed, because pages
  and media are what a clone reads;
- the **media policy** in force and the limits it will stop at;
- a final `plan:` line, which counts each kind of line above it.

**⚠️ The list above is what `plan` is for, not a transcript of its output.**
Run it and read the real thing: it names paths this page draws as placeholders,
at your own addresses, and it distinguishes a directory it **claims** — one a
build creates only when it copies a file into it — from a path it **creates**.

**Run this at step 3, before you write a line of adapter code.** It is the
cheapest way to find out that your manifest says something you did not mean.

---

## Delivery is not placement

**An href never encodes how a file arrived.** A generated artifact is addressed
relative to the page that references it, and that address is the same whether
the file was generated locally, committed, or restored from somewhere else.

**This was proved in reverse, expensively.** When 11.7 GiB of media left git
for release assets on one corpus, the layout on disk did not move and every
page still addressed a clip as plain `audio/<clip>.mp3` — which is the only
reason that change was a script instead of a re-render of 1,290 pages.

---

## Next

- [Exercises](exercises.md) — the other manifest field that changes what gets
  built.
- [Worked examples](examples.md) — one corpus of each profile, with the plan
  output for both.
