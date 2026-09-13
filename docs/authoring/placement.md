# Placement — where the output goes

**You decide where generated files land, and it is one field in the manifest.**
Nothing downstream cares which you chose.

```json
{ "placement": "tree" }
```

---

## The two profiles

| Profile | Pages go | Use it when |
|---|---|---|
| `tree` | under one generated root, in directories spelling the address | your material has no layout worth preserving — a folder of notes, a set of papers, a book split into chapters |
| `sibling` | **beside the source file each one was generated from** | your repository already has a layout the reader knows, and moving things would be rude |

**`sibling` is what makes "your files are never touched" liveable.** A reader
who already knows their way around `16-streams-api/` finds the generated page
in `16-streams-api/`, next to the file it came from — not in a parallel tree
they now have to learn.

**A third profile is added by registering one, and no consumer changes.**
Nothing anywhere downstream names a profile; that is asserted over the whole of
the framework rather than promised.

---

## What gets created

Under `tree`, everything lives under one generated root:

```
index.html                                          the root index
.studyforge/assets/                                 shared css and js
.studyforge/site.json                               the discovery cache
archive/<address>/...                               the archive, beside corpus.json
.studyforge/<address>/units/unit-NN/unit-NN-<title>.unit.html
.studyforge/<address>/units/unit-NN/audio/
.studyforge/<address>/units/unit-NN/images/
```

Under `sibling`, the pages and their media move out beside the material:

```
index.html                                          the root index
.studyforge/assets/                                 shared css and js
16-streams-api/README_4.4.1.md                      YOURS — untouched
16-streams-api/streams-api.section.html             the container page
16-streams-api/4.4.1-introduction.unit.html         the unit page
16-streams-api/4.4.1-introduction.audio/            its narration
```

**Every generated page has a real name and is never `index.html`.** Names come
from the unit's own numbering and title, so a directory listing is readable and
a scan is unambiguous. The single `index.html` a build writes is the root
index.

**The name comes from the unit's identity, never from your source filename.**

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
- a final line: `plan: N path(s) to create, N file(s) to edit, N ignore
  line(s), N refusal(s)`.

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
