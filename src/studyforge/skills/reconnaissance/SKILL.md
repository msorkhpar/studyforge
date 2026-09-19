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

⛔ **A heading that links a file is not a unit by the link alone (W250).** Where
it stands in the labels' shape and opens no entry, and the file it links is cut
into regions by its headings, it is a group label whose units are those regions:
each unit's `origin` is `{path, section}` (Ruling 92). A linked file that is one
unit stays an entry, and the survey asks about it by name.

> **Measured** at ISO `ab9e765`: read as an entry, `# [Test cases](TestCases.md)`
> gave **39 units in 3 groups**. Read as a label, it gives **55 units in 4 groups**,
> 17 of them regions of `TestCases.md`, one per top-level heading.

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
| ISO-8583 | 3, as `#` headings | `1.` … `16.`, restarting per group | **1** (`group`) |
| Java-senior | 10, as bare numbered lines | `1.1.` and `1.1.1.` | **2** (`section`, `module`) |

⚠️ Java's group is *already inside* its ordinals — every entry under "Java
Fundamentals" begins `1.` — so counting the group again gives three levels for
a two-level corpus.

### 7. Answer the execution question, and let "none" be an answer

⭐ **A corpus with no graders is complete at the reading floor, not short**
(§11.0, C5). ⛔ Report *"no runnable code, no graders"* as a **finished
verdict** with its evidence, never as a blank section — the difference decides
whether the corpus finishes at the reading floor or enters the execution track.
⚠️ Neither is a milestone id read as a position: the order milestones run in is
the one the capability index prints, not the order their ids sort to.

⭐ **A graded corpus's draft declares the `runtimes` its material evidences**
(`W351`) — a build file or a source suffix, each from a closed map, and `java`
beside any name that runs on a JVM. ⛔ **Never a runtime nothing evidences**,
never the key for prose, and never beside `exercises: false`: evidence there is
one question instead. A draft carrying the key declares `corpus_api` 4, the
version the reader requires for it, and every drafted runtime is asked about.

### 8. Hand over the proposal **and** the questions

⛔ Never present the draft manifest alone. The questions are the other half of
the deliverable, and the level vocabulary is always one of them: §4 rules the
names are the corpus's own, and this skill cannot know them.

⛔ **A field the draft fills is filled with a value `SF-02` accepts.** `source`
is the slug of the curriculum record's title and `variants` is `["prose"]`,
both asked about; no include glob matches the curriculum record — a directory
whose wildcard would catch it is listed file by file.

⛔ **`source` never depends on the directory surveyed (`W249`).** A worktree, a
clone and an archive of one commit draft one `source`. Nothing is read from
git, and never a remote URL.

⭐ **The draft proposes the `not_material` globs; the reasons stay yours
(`W240/3`).** Only a file an include reads is proposed for `exclude`. Every
other file `validate` will classify gets a glob with `"why": null`, and so do
the record and the root's furniture. Nothing onboarding recorded writing is
proposed, so no glob collides with `SK-07`'s. Give each reason to `promote`
in `reasons`, keyed by its glob.

### 9. ⛔ On a corpus this framework already onboarded, survey the corpus

⚠️ **A second survey reads the framework's own consuming half back**, and the
worst symptom is silent. ⭐ **Measured on a clean run:** the raw repository gave
*"build files 0, graders 0"* and a draft of `exercises: false`; the same
repository after onboarding gave **12 files that look like graders — the
scaffold's own `tests/**/test_*.py`** — dropped the verdict line and drafted
`exercises: true`. ⛔ **A COMPLETE corpus is then presented to its reader as
unfinished** (§7, C5). The archive a build wrote flipped `placement` the same
way, and the generated documents were re-proposed as this corpus's material.

⭐ **`.studyforge/installed.json` names every file of it, and it is the one
instrument** — `installed.generated` reads it, `inventory` sets those files
aside, and every pass measures the corpus rather than the framework. ⛔ **Do
not invent a second way to recognise a generated file**: not a name, not a
suffix, not a directory. ⚠️ What a *build* writes is `validate`'s answer rather
than the record's, and `inventory.enumerated` is `source_files` — so this survey
stops exactly where `validate` stops.

⛔ **A re-survey never proposes again what the corpus already declares, and
a proposal that stands down says so (`W269`).** A file a `not_material` glob
in the root's own `corpus.json` covers is not proposed, and no directory glob
sweeps it. A survey that judged no file, or judged without git's ignore
rules, asks one question naming why, even when it proposes nothing. ⚠️ A
root inside another repository's ignored directory judges no file: survey
the corpus as its own working tree.

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

---

## Appendix — the measurements the code points at

⛔ **This appendix is the only copy.** The modules in this directory state the
*rule* and point here; they do not restate the numbers, and — R1 — they do not
name a corpus at all. ⭐ A pointer is only better than a restatement if the far
end holds, so anything a docstring stops saying is written down here first.

### A1 — no measured corpus can be read from its tree

| | the directories say | the record says |
|---|---|---|
| ISO-8583 | one flat `src/`, 41 files, **0** directories | three groups, named by the author, 16 + 11 + 11 |
| Java-senior | 45 flat module directories | **10 sections**, each grouping several modules |
| SPARQL | one flat `src/`, 19 files | one ungrouped course |

⭐ That is not a quirk of three repositories; it is what hand-written curricula
do. ⚠️ ISO's prefix partition and its `README.md` agree **exactly**, which is
what makes the prefix rule usable as a cross-check and unusable as a source.

### A2 — entries arrive in more than one shape, and the odd ones are silent

| corpus | majority form | minority form |
|---|---|---|
| ISO-8583 | 36 of 38 as list items | **2 as headings** |
| Java-senior | 205 as `- [1.1. Title](x)` | **6 as `- 1.5. [Title](x)`**, ordinal outside the link |
| all three | `N. [Title](x)`, the ordinal **as** the list marker | — |

⛔ A parser written for the majority form reads the wrong number and **raises
nothing**. ⭐ So every form is read, and the *disagreement between forms* is
itself reported: it is the tell that a hand-maintained document has drifted.

⚠️ **22 of ISO's 38 recorded titles are written** `**Like This**` — emphasis is
presentation, not name, and a manifest that kept the marks shows them to a
reader.

### A3 — why a "densest run of entries" threshold cannot work

| corpus | largest gap *inside* the curriculum | nearest stray entry outside it |
|---|---|---|
| Java-senior | 8 lines | 22 lines away |
| ISO-8583 | **34** lines (its outline runs to three levels of unlinked text) | — |

⛔ **Any threshold that keeps ISO whole swallows Java's stray**, and any
threshold that excludes Java's stray cuts ISO's curriculum in half. ⭐ So the
region is the **whole span** from first entry to last, the entries above the
first label are *reported* rather than trimmed, and the only constant left is
how much may sit above the first label — not where the curriculum ends.

⚠️ **And the first label can sit above the first entry.** ISO records its first
container two lines above its first entry, because a document's own opening is
a label for everything below it.

### A4 — "no runnable code, no graders" is a measured verdict

| corpus | build files | files that look like graders |
|---|---|---|
| ISO-8583 | **0 of any kind** | 0 |
| SPARQL | **0 of any kind** | 0 |
| Java-senior | 47 | 168, of 792 non-prose files |

⭐ ISO's whole vocabulary is five block types. ⛔ **It is finished at M4, not
short** (§11.0, C5). ⚠️ Java's 168 are what a closed set of test markers
matched; whether they grade the *teaching material* is a question this skill
asks and cannot answer.
