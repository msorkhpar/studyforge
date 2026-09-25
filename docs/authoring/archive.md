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
archive/<address>/units/unit-NN/                  a unit's own files, when it has any
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
`studyforge.skills.adapter.Layout` computes every one of them, and the
[adapter skill](../../src/studyforge/skills/adapter/SKILL.md) shows how to use
it.

**If `corpus.json` declares `curriculum.containers`, the adapter skill's scaffold
writes the filing for you**: which units each container holds, at which
address, and the unit count taken from the file names. Reading each unit's
material into blocks is then the only part you write, and a change to the
filing is made in `corpus.json`, never in the adapter
([`curriculum`](corpus.md#curriculum--where-your-reading-order-is-recorded)).
That holds for a record whose modules are linked entries too, once
`curriculum.linked` says so.

**If your material is Markdown, the reader is already written.**
`studyforge.archive.markdown.parse(text)` returns a document's blocks in the
vocabulary below, and raises `MarkdownError` naming any construct it cannot
hold rather than dropping it. `documents` is then one loop over the
container's units, parsing the file each unit's `origin` names.

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
  "origin": "basics/01-getting-started/contents.md",
  "units": [
    {
      "n": 1,
      "title": "What a build tool is for",
      "practices": 1,
      "origin": "basics/01-getting-started/build-tools.md"
    }
  ]
}
```

| Key | | |
|---|---|---|
| `container_api` | the version of this document format | this build reads `1`, `2` and `3` |
| `address` | exactly `len(levels)` segments | and it must match the directory holding the file |
| `titles` | one per segment, in the same order | what the reader sees |
| `variant` | **one** variant per container | so the map cannot promise a variant the archive does not hold |
| `ingested` | the date it was read | |
| `origin` | the file in **your** repository this map was read from | optional; see below |
| `note` | free text a person added | preserved across regeneration, never overwritten |
| `units` | what this container holds | each `{ n, title, practices, origin, practice_origin, url_slug, label, note }` |

**`practice_origin` is the second source file a unit may have**, and it is how
a practice joins the topic page it practises without rewriting that page's
source. It needs `container_api: 3`, and the rule for when to use it is in
[Exercises](exercises.md#where-a-practice-may-live).

**A generator owns this file, and a generator that would discard somebody's
judgement stops.** `title`, `titles` and `note` are the fields a person may
have corrected by hand; they are round-tripped rather than rewritten.

**Record a title as the source writes it, outline number and all.** The site
lists and orders every unit itself, so a leading outline number such as
`5.1.1.1 ` or `3.2.1. ` is left off every title and heading a reader is shown or
hears, on every corpus. A number that is part of the words (`Java 21 features`,
`ISO 8583 messages`) is kept. Do not strip it yourself: `origin.section` is
matched against the heading exactly as the file writes it. A unit's `label` may
be its outline number (`4.2.4`): it keeps the unit's identity and order and names
its page file, and a listing shows the unit's place in its container instead.

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

## `assets` and `attachments` — the files a unit comes with

**Both are lists, both are always written, and an empty one is `[]`.** "Absent"
and "empty" are then not two states a reader has to tell apart.

**One entry vocabulary, not two.** An entry is
`remote local sha256 bytes content_type kind`, and `remote` is `null` for a file
your adapter produced itself. `local` is the file's path **inside that unit's
own archive directory** — `<address>/units/unit-NN/` — so `media/diagram.svg`
means `<address>/units/unit-02/media/diagram.svg`.

**They differ in what they are for, and that decides where each reaches the
reader:**

| | What it is | What the site does with it |
|---|---|---|
| `assets` | a file a **block already names** — an `image`'s or a `video`'s `src` | the page **shows** it, through that block, and the build places it beside the page |
| `attachments` | a companion file **no block names** — a dataset a lesson loads, a notebook, a sample document | the page **links** it for download, and the build copies it into the attachments directory the placement profile gives that unit |

**So an attachment is declared once and lands three times:** `studyforge plan`
names the directory it will occupy, the unit page carries the link, and the
build copies the file into it. A file listed under `assets` that no block names
is a file nothing will reach — list that one under `attachments` instead.

**Neither list is a `content` declaration, and neither belongs in one.**
`corpus.json`'s `content` classifies **your source material** — whether a file's
prose is read into the archive — and these files are already *in* the archive,
written by your adapter. Their placed copies are the build's own output, which
the non-destructive check tells from your material by path. So an attachment needs no `content.include`
entry, adding one would claim its prose is ingested, and no build touches your
original in order to place one.

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
document recurses on that property rather than naming those two by hand.

**A list item is a string, or an array of its parts in reading order**: runs of
text, nested `list` blocks, and `code` blocks. Keep a step's snippet inside its
step, and the sentence after the snippet after it in the same item:

```json
{"type": "list", "ordered": true, "items": [
  ["Return an array:", {"type": "code", "lang": "java", "text": "int[] pair();"}, "Then read both values."],
  "Return an object."
]}
```

A list whose numbering carries on after a code block written *between* items
records the number it starts at as `start`.

**`html` exists because real material contains raw markup**, and a reader that
raised on anything it did not recognise would stop an ingest dead.

**A construct that fits none of the eleven is a finding about the vocabulary,
not a block to throw away.** Report what you cannot read; never drop it. A
dropped block is absent from the digest *and* from the counts, so nothing
downstream can notice it went missing.

---

## Four rules that are not negotiable

### An address is recorded, never derived

**Do not slugify a title to get an address.** It is the tempting shortcut and
it is wrong: real catalogues serve many units at a slug their title does not
produce. A derivation sends each of those links to a page that is not there,
and a link that fails is worse than no link, because it asserts an address the
reader then cannot find.

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

**One unreadable container map halts every consumer that walks the tree**, and
the failure is then reported at the reader rather than at the writer that
caused it. A reading that can be taken again is never worth a file nothing can
load.

### No personal data reaches an archive

**The gate refuses; it does not rewrite.** An absolute home path, an email, an
account id, a machine name — the write fails and the refusal names *the field*,
never the value.

**Any string in hand-written material can be an absolute path.** This is not a
check you run at the end; it is a gate every string passes on the way in.

**Sample data in a lesson passes when it reaches nobody.** Write a sample
address on a reserved domain and a sample home directory under the account
`user`, and the gate lets them through verbatim:

| passes | refused |
|---|---|
| `alice@example.com`, `ops@mail.example.org`, `x@example.net` | an address on any registrable domain, including `test.com`, `b.com` and `example.co` |
| an address under `.example`, `.invalid`, `.test` or `.localhost` | an address under `.local`, and any local hostname |
| the home path `/home/` followed by the account `user`, and anything below it | any other account after `/home/`, any account after `/Users/`, a tilde followed by a name |

Nothing else is admitted, and there is no manifest switch: a sample on a real
domain is edited to a reserved one.

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

- [What `validate` checks](validate.md) — every check your archive is about to
  meet.
- [Exercises](exercises.md) — the `exercise` key, and when to write no practice
  document at all.
- [Worked examples](examples.md) — two archives that exist, and the commands
  that read them.
