# Skill — source reconnaissance

**Given material nobody has read, work out its shape and propose a corpus
manifest.** Produce a draft `corpus.json`, a proposed level vocabulary, and an
honest report of what could not be determined.

⛔ **This is the only skill that reasons about an unfamiliar source.** Every
other skill operates on contracts (R2). If a second skill starts needing to
understand a source, the seam has been drawn wrong.

---

## The rule that governs every judgement below

⛔ **A confident wrong answer about a hierarchy costs an entire ingestion.**
*"These 19 files look flat, but files 12–19 reference a grouping I cannot see —
please confirm"* costs a question.

⭐ So the deliverable is **the proposal and the open questions together**. A
report with no open questions about unfamiliar material is a report that
guessed (R6). Every question states **what would settle it**, because a
question a reader cannot act on becomes a silent guess one layer down.

---

## Procedure

### 1. Run the measurement, and read it before deciding anything

```
python3 -c "from studyforge.skills.reconnaissance import survey; \
            print('\n'.join(survey('<path>').lines()))"
```

⛔ **Do not start by reading the files.** Start with the counts. The
integration catalogue's own rule: *a number inherited from a document is not a
measurement, and a count without its denominator is not a measurement.*

### 2. Find the document that records the curriculum — before looking at names

⭐ **This is the single highest-value step and the one most often skipped.**

A flat directory whose filenames carry a prefix — `1.md`, `s1.md`, `c1.md` —
*does* encode a grouping. ⛔ But **reading the names is derivation, and reading
the document is a record** (§6: an address is recorded, never derived).

> **Measured.** ISO-8583: 41 files, **zero** directories, three prefix groups
> of 16 / 11 / 11 — **and** `README.md` records the same three groups in the
> author's own words, in reading order, with a title and an ordinal for each of
> the 38 units. The two partitions agree exactly.

⛔ **So propose *"the curriculum is recorded in `<file>`"*, and keep the prefix
rule as a cross-check that must agree — never as the source.** A skill that
proposes the regex has produced a plausible manifest for that corpus and an
unjustifiable one for the next.

⚠️ If nothing records the curriculum, **say so and stop guessing.** Do not sort
filenames and move on — see step 4.

### 3. Read the record as a **region**, and never trust heading level

⛔ **In a curriculum document, heading level does not identify role. Role is
positional.** Both measured corpora set this trap, in opposite directions:

| | what the record does | what a syntax-keyed parser produces |
|---|---|---|
| ISO-8583 | 3 containers as `#` headings, in a file with **21** top-level headings | **21 containers for a 3-container corpus**, and no error |
| Java-senior | 10 sections as **bare numbered lines**, with **0** headings in the region | **0 sections for a 10-section corpus** |

⭐ A group label is *"a line inside the curriculum region that introduces a run
of entries and is not itself an entry"*. Both corpora fall out of that one rule
and neither falls out of a syntax rule.

⚠️ **And the region matters as much as the rule.** ISO's `README.md` is 674
lines, of which lines **313–674 (53.7%) are a structural copy of
`TestCases.md`** — 361 of its 367 headings, digest-identical. ⛔ The file **cannot be excluded**: it is the only record of
the corpus's addresses, titles, ordinals and grouping. `content.exclude` names
files; this is not a file. So the answer is a region, not an exclusion.

### 4. ⛔ Do not derive the reading order. Find the oracle, or ask.

> **Measured.** A filename sort places **37 of 38** ISO units at the wrong
> index in the corpus-wide reading order — **35 of 38** even when each group is
> sorted on its own. Every page renders, every link resolves, the table of
> contents is complete, and chapter 2 is chapter 11.
>
> ⚠️ **It flatters, which is why it survives review:** unit 1 of every group is
> still first, in all three groups — so the page anybody opens to spot-check is
> correct.

⛔ **A count assertion does not see this**, and a count assertion is what the
framework has. An ordering claim needs an **oracle**, and the oracle is
whatever *records* the order. If nothing records it, put that in the report.

### 5. Detect duplication in both shapes, and report the one you cannot fix

- **Whole-file.** ⛔ Assert digest equality, not similarity: where a corpus
  ships per-unit files *and* whole-series aggregates, the aggregates are exact
  ordered concatenations (ISO: 9,181 of 18,304 lines, **50.2%**). A glob over
  `*.md` ingests everything twice and **nothing fails**.
- **Structural.** A region of one document reproducing another's heading tree.
  No file duplicates a file, so the whole-file test finds nothing.

⚠️ **Report the second even when nothing can be done about it.** A report that
says *"no duplication found"* about a corpus in that state is wrong in a way
its reader will act on — they will trust a heading count, a word count, or a
narration estimate, and every one is nearly double.

⭐ **And before excluding anything, extract what it attests.** ISO's three
aggregates are pure duplication *and* an independent machine-checkable
recording of the reading order — the one property of that corpus nothing else
can verify. Deduplication removes the copy **and the attestation the copy
constituted**.

### 6. Decide depth from ordinals, not from the presence of groups

⛔ **A grouping is not automatically a second level.**

| | groups | ordinals | container levels |
|---|---|---|---|
| ISO-8583 | 3 | `1.` … `16.`, restarting per group | **1** (`group`) |
| Java-senior | 10 | `1.1.` and `1.1.1.` | **2** (`section`, `module`) |

⚠️ Java's group is *already inside* its ordinals — every entry under "Java
Fundamentals" begins `1.` — so counting the group again gives three levels for
a two-level corpus.

### 7. Answer the execution question, and let "none" be an answer

⭐ **A corpus with no graders is complete at the reading floor, not short**
(§11.0, C5). ⛔ Report *"no runnable code, no graders"* as a **finished
verdict** with its evidence, never as a blank section — the difference decides
whether the corpus is planned to M4 or to M8.

### 8. Hand over the proposal **and** the questions

⛔ Never present the draft manifest alone. The questions are the other half of
the deliverable, and the level vocabulary is always one of them: §4 rules the
names are the corpus's own, and this skill cannot know them.

---

## What this skill must never do

- ⛔ **Never write into the source repository** (R3). Reconnaissance reads.
- ⛔ **Never derive an address from a title.** §6 rules an address recorded,
  never derived — measured, **157 of 1,290 units (12.2%)** of one real corpus
  are served at a slug their title does not produce.
- ⛔ **Never smooth over an uncertainty to make the report look finished.**

## ⚠️ One correction worth carrying, because the ruling was wrong

E10 and an earlier ruling say `slugify` collides on **accents** — that `Café`
and `Cafe` become one slug. ⛔ **Measured: they do not.** An accent is a
non-alphanumeric, so it collapses to a *separator*: `caf` and `cafe`.

⭐ **The class that actually occurs is punctuation.** `'Streams: an API'` and
`'Streams, an API'` both give `streams-an-api`. **A skill built for the accent
case would miss the case that happens.**

⚠️ And it is not rare: **15 of 38 units (39.5%)**, in **7** slug classes,
collide under a corpus-wide title-derived slug in one corpus — 14 of them
because two of its series deliberately mirror each other — *Basic Setup*, *Error Handling*, *Testing*, once for the server
and once for the client. It is the **good** material that does this.
