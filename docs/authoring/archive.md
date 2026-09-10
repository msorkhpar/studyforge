# What an adapter must produce

**An adapter is the piece of code that reads your material and writes the
archive.** It is the only piece anyone has to write per corpus, and this page
is its entire specification.

**The seam is on disk, not in Python.** There is no callback to register, no
plugin interface and no framework API your adapter calls. It writes files; the
checker reads them. That is why an adapter can be written in any language, and
why two people can write two adapters at once without agreeing on anything but
this page.

---

## The tree

```
corpus.json                                       the manifest
archive/<address>/container.json                  one per container
archive/<address>/raw/<variant>/unit-NN/lesson-M.json
archive/<address>/raw/<variant>/unit-NN/practice-M.json     optional
```

`<address>` is one directory per level, so a depth-1 corpus has one segment and
a depth-2 corpus has two:

```
archive/algebra/container.json                            depth 1
archive/basics/01-getting-started/container.json          depth 2
```

**Never compute one of these paths by hand.** The tree is five joins deep and
four of them fail *silently* when they are wrong. `unit-3/` instead of
`unit-03/` produces a tree the checker reports as *unit missing* — at the
reader, not at the writer, and only after everything else has looked fine.

---

## `container.json` — the map

**One per container, and it declares what the container holds before anything
looks for it.** That is what makes "a unit the map promised is not there" a
detectable failure rather than a silently shorter site.

```json
{
  "container_api": 2,
  "address": ["basics", "01-getting-started"],
  "titles": ["Basics", "Getting Started"],
  "variant": "java",
  "ingested": "2026-09-10",
  "origin": "basics/01-getting-started/README.md",
  "units": [
    {
      "n": 1,
      "title": "What a build tool is for",
      "practices": 1,
      "origin": "basics/01-getting-started/README_1.md"
    }
  ]
}
```

| Key | | |
|---|---|---|
| `container_api` | the version of this document format | this build reads `1` and `2` |
| `address` | exactly `len(levels)` segments | and it must match the directory holding the file |
| `titles` | one per segment, in the same order | what the reader sees |
| `variant` | **one** variant per container | which removed an entire failure class: *the map promised one thing and the archive has none* |
| `ingested` | the date it was read | |
| `origin` | the file in **your** repository this map was read from | optional; see below |
| `note` | free text a person added | preserved across regeneration, never overwritten |
| `units` | what this container holds | each `{ n, title, practices, origin, url_slug, label, note }` |

**A generator owns this file, and a generator that would discard somebody's
judgement stops.** `title`, `titles` and `note` are the fields a person may
have corrected by hand; they are round-tripped rather than rewritten.

---

## The unit document

**One JSON document per lesson or practice, and its keys are a fixed list in a
fixed order.** The order is the reading order — *what it is, where it came
from, what it says, what it is made of* — and it is what reaches disk, so two
runs of the same adapter over unchanged material produce identical bytes.

**Fifteen keys, always written:**

```
raw_api  source  address  variant  unit  kind  ordinal  ingested
title  blocks  video  assets  attachments  counts  content_sha256
```

**Four more, written only when they have something to say, always after the
digest:**

```
assets_sha256  starting_code  media_skipped  exercise
```

**A document carrying any other key is refused.** A key nothing reads is how a
misspelled one goes unnoticed for a year.

**`ingested` is the one field exempt from byte-for-byte reproducibility.** It
is a clock, it is genuinely useful — it answers *how stale is this?* — and it is
excluded from `content_sha256`, so it cannot make unchanged content look
edited. Two runs of a correct adapter differ in `ingested` and in nothing else,
and that is the sentence to use when you claim reproducibility: *identical
bytes apart from `ingested`*.

---

## `blocks` — the vocabulary is closed at eleven types

**A unit's body is a sequence of typed blocks. There are eleven types and that
list is a contract, not a convenience.**

| Type | Carries |
|---|---|
| `heading` | `level`, `text` |
| `para` | `text` |
| `code` | `lang`, `text` |
| `table` | `headers`, `rows` |
| `list` | `ordered`, `items` |
| `image` | `src`, `alt`, `width` |
| `video` | `src`, `title` |
| `rule` | nothing — it is a horizontal rule |
| `quote` | `blocks` — it holds other blocks |
| `html` | `text` — raw markup the reader wants preserved |
| `disclosure` | `summary`, `open`, `blocks` — it holds other blocks |

**`quote` and `disclosure` hold other blocks**, so anything that walks a
document recurses on that property rather than naming those two by hand — which
is how the second one nearly got missed.

**`html` exists because real material contains raw markup**, and a reader that
raised on anything it did not recognise would stop an ingest dead. In one
surveyed tutorial, raw HTML appeared in 18 files.

**A construct that fits none of the eleven is a finding about the vocabulary,
not a block to throw away.** Report what you cannot read; never drop it. A
dropped block is absent from the digest *and* from the counts, so nothing
downstream can notice it went missing.

---

## Four rules that are not negotiable

### An address is recorded, never derived

**Do not slugify a title to get an address.** It is the tempting shortcut and
it is measured wrong: on one real catalogue, **157 of 1,290 units — 12.2%, one
in eight** — are served at a slug their title does not produce. A derivation
therefore sends one link in eight to a page that is not there, and a link that
fails is worse than no link, because it asserts an address the reader then
cannot find.

**Where two records name an address for the same unit** — a container map and a
unit document — **a disagreement is a refusal, never a preference.** One would
be linked from the page and the other from the index, and the reader would be
sent to two different places with nothing failing.

### `origin` is verbatim, and it is not decoration

**`origin` is the relative path of the file the material was read from**,
copied exactly. Because your files are never touched, it stays a permanent
working link from every generated page back into your own material — and it is
the field a re-read would use.

It is optional, because your corpus may be your own writing. **Where it exists
it is not optional chrome**: material that came from somebody else is credited
on the page that shows it.

### Stage beside the target, then move

**Build the whole archive next to where it is going, and move it into place
only when every file exists.** A document that fails its own validation is
never left at a path something else will read.

**The price of getting this wrong was measured**: one unreadable container map
halts every consumer that walks the tree, and the failure is then reported at
the reader rather than at the writer that caused it. The bill was 116 archives,
0 pages, 0 narration and a broken suite. A reading that can be taken again is
never worth a file nothing can load.

### No personal data reaches an archive

**The gate refuses; it does not rewrite.** An absolute home path, an email, an
account id, a machine name — the write fails and the refusal names *the field*,
never the value.

**Any string in hand-written material can be an absolute path.** This is not a
check you run at the end; it is a gate every string passes on the way in.

---

## Re-reading material that changed

**`content_sha256` covers a unit's blocks and answers exactly one question: did
the source change since we read it?**

On a re-read, a digest that disagrees with the source means the material was
edited upstream. **The archive is replaced and the change is reported** — never
silently overwritten, and never silently kept. Everything derived from that
unit — its page, its narration, its exercises — is invalidated by the same
signal. Without it a corpus drifts out of date with no symptom at all.

---

## Next

- [What `validate` checks](validate.md) — the twelve checks your archive is
  about to meet.
- [Exercises](exercises.md) — the `exercise` key, and when to write no practice
  document at all.
- [Worked examples](examples.md) — two archives that exist, and the commands
  that read them.
