# The integration catalogue

**What an integrator learns the hard way, written down once so the next source
starts further along than the last one.** Owned by the framework Product Owner;
entries are contributed by whoever measured them, from either side.

⛔ **Contribution and adoption are two different jobs, and only the first had an
owner until 2026-09-10.** ⭐ **Adopting a consumer's contributions — and recording a
decision for each one that is not adopted — is **wave check 6**, run by the
framework PO at every wave-open.** ⚠️ **A contribution silently not adopted is
indistinguishable from one nobody read**, which is why the refusals are written
down beside the adoptions rather than left as silence.

⛔ **Created 2026-09-09, and its absence was the point.** This file is referenced
by spec §9, by `SK-07`, and by at least three rulings — and it **did not exist**.
`ls docs/` returned `conventions specs tasks`. ⚠️ Meanwhile PO-Integration had
written **ten durable entries in this document's own shape**, with nowhere to put
them.

⭐ **That is C6 arriving from the integration side, and it is the sharpest
instance yet**: *a ruling is made, is correct, and never reaches the artifact it
governs* — here the artifact was **the artifact itself**. ⛔ **A mechanism that is
specified, referenced by rulings, and has no file is a mechanism that exists in
everybody's plans and nobody's repository.**

---

## What belongs here, and what does not

⭐ **The test is R19, and it is one question: *would the next source have to
learn this again?***

| Belongs | Does not |
|---|---|
| A **limit** of the framework that a corpus will meet — named, with what to do instead | A bug. That is a finding against a task |
| A **trap real material sets** — measured in a real repository, with the number | A trap somebody imagined |
| A **scoping fact** a planner needs before committing to a corpus | A ruling. That belongs in the spec, an epic, or a convention |
| A **degradation that is correct but surprising** | Anything a skill could generate. ⛔ **That is a hole in the skill** (R19), and filing it here hides it |

⛔ **A catalogue entry is not a substitute for a ruling.** If the answer is *the
framework should change*, it is a finding and it goes to a task. This file is for
what stays true after the framework is right.

⚠️ **And it is not a place to record paths inside the extraction source** (R20).
What a consumer needs is carried **here**, in its own words.

---

## Entries

### 1. A construct outside the block vocabulary degrades to prose, visibly

**Measured:** SF-07, 166 lesson files. `math` was proposed as a block type and
**refused** — inventing a type against **zero** sources is R1's error from the
other direction.

⭐ **What an integrator needs to know:** *"never silently drop"* is a promise
about structure the vocabulary **knows**. A construct outside it degrades to
**prose, visibly, with the text intact** — it is not lost, and it is not
rendered. ⛔ A corpus whose material leans on `$$…$$` should expect readable
plain text, not typeset mathematics, and should decide whether that is
acceptable **before** ingestion rather than after.

### 2. A claim about another repository is verified in that repository

**Measured:** the extraction source's `naming.py` docstring says **1,282** where
its own tree holds **1,290** (`W12`). ⚠️ A CTO-verified ruling was separately
overruled because what got verified was a *fixture's* consistency, not the claim
about the source the fixture was built to match.

⭐ **What an integrator needs to know:** ⛔ **a number inherited from a document
is not a measurement**, however authoritative the document. Re-count in the
repository the claim is about, and record the command. This has now cost this
project two round trips in two directions.

### 3. A count without its denominator is not a measurement

**Measured:** SF-07 reported `rule` in *10 of 166 lesson files* and *15 of 218
markdown files* — same corpus, two denominators, both correct. ⚠️ Separately,
*"18 ISO files carry raw HTML"* survived **three documents and two review
rounds** with no denominator attached.

⭐ **What an integrator needs to know:** every count in a reconnaissance report
carries what it is out of. ⛔ A bare count cannot be re-run, and one that cannot
be re-run cannot be corrected.

### 4. A sample is not a census, and a proxy is not the thing

**Measured:** an index was declared current because **one** symbol was present;
it was stale by **224 nodes**. In the same round, an mtime check called a current
index stale, and its verdict flipped **FAIL → PASS in 33 minutes with no content
change**.

⭐ **What an integrator needs to know:** ⛔ **verify the property you care about,
not something correlated with it.** Timestamps are a proxy for content; one
symbol is a proxy for a tree; a rendered page is a proxy for an archive. Each
fails **silently and confidently**, which is the combination that costs the most.

### 5. Ordering is not covered by a count, and it flatters

**Measured (ISO, 38 units in 3 groups):** a filename sort puts **35 of 38 units
at the wrong index**. The count is right, every page renders, every link
resolves, and nothing raises. ⚠️ **And it flatters: unit 1 of each group stays
first**, so the page anybody spot-checks is correct.

⛔ **What an integrator needs to know:** a count assertion is all the framework
currently has, and **ordering is a different claim**. ⚠️ The only
machine-checkable order oracle in that corpus is its three aggregate documents —
⛔ **precisely the files a `content.exclude` would delete**, so excluding the
duplicate destroys the evidence for the ordering. Decide that trade deliberately.

### 6. Heading level does not identify role

**Measured (ISO):** `README.md` is 675 lines; lines 313–675 carry **361 headings
digest-identical to the whole heading tree of `TestCases.md`** — ⛔ **53.7% of the
curriculum document is a copy of another document's structure**, and no
whole-file digest sees it. The file **can never be excluded**: it is the only
record of the corpus's addresses, titles, ordinals and grouping.

⛔ **Consequence:** `#` means *container* **3** times and *chapter of another
document* **17** times. ⚠️ **A parser keyed on heading level emits 21 containers
for a 3-container corpus and raises nothing.**

### 7. The duplicate that cannot be excluded is a region, not a file

**Measured:** `content.exclude` names **files**; the duplicate above is a
**region inside a file that must be kept**.

⭐ **What an integrator needs to know:** ⛔ **the manifest is not going to grow
sub-file exclusion**, and it should not. The answer is **detect and report, not
remedy** — reconnaissance names the overlap and says which set is canonical, and
a person decides. ⚠️ A tool that silently picked one would be choosing which half
of a curriculum a reader never sees.

### 8. Runnability is decided by the **reader's obligation**, not the file's shape

**Measured (ISO):** `exercises: false` was reached on three counts — **zero
imperative prompts, zero solution blocks, zero runners** — and ⭐ **the first count
is the one that decided it, because it is the only one about what the reader is
asked to *do*.**

⛔ **The sharp case, and it is why shape is not enough:** `TestCases.md` is **191
Gherkin scenario declarations that look exactly like a grader corpus and ask the
reader to do nothing.** ⚠️ Any classifier keyed on *what the files look like* marks
that corpus runnable and is wrong.

> ⛔ **CORRECTED 2026-09-10 — this entry said 188, and 188 was a count over the
> wrong set** (`F24`, filed by PO-Integration against themselves). ⚠️ **188 is the
> *heading* count; the declaration count is 191.** ⛔ **And it looked corroborated
> because 188 is *also* this corpus's `java` fence count** — ⭐ **a coincidence
> between two counts over two different sets is the strongest false confirmation
> available, because the reader who checks it finds agreement.**
>
> ⭐ **Entry 9 is this entry's own rule and it applies here: state the ratio, the
> denominator, AND the set it is over.** ⚠️ **188 carried a denominator and still
> travelled wrong, because the *set* was unstated** — ⛔ **so the set is the field
> entry 9 was missing, and it is added to entry 9 by this correction.**
>
> ⛔ **The number reached `BOARD.md` in four places and this catalogue in one.**
> ⭐ **The record keeps its number and gains this banner** rather than being
> silently corrected — entry 9's own rule, applied to entry 8.

⭐ **So ask: is the reader asked to produce something?** ⛔ Not *does this look
like test code* — code-shaped material that demands nothing of the reader is
**prose about code**, and §7's `none` state is the correct answer for it.

### 9. A denominator omitted makes a real trap sound weaker

⚠️ **Measured, and this is the catalogue's own rule turned on its author.** Three
published numbers were corrected: `35 of 38 misplaced` was **35 of 38 per-group
(3 sorts) and 37 of 38 corpus-wide (1 sort)**; `14 of 38 collisions` was **15 of
38 (39.5%) in 7 classes**, ⛔ **the 7th three-way and reaching into
fundamentals**; `675 lines` was **674**, a `split('\n')` off-by-one.

⛔ **Two of the three made a real trap sound *weaker* than it is — the direction
that gets a finding dismissed.** ⭐ **Corpus-wide sorting leaves exactly one unit
in place**, and the filename-hierarchy trap is what makes the corpus-wide sort
the likelier mistake in the first place.

⚠️ **The lesson is not "check your arithmetic".** It is that ⛔ **an understated
number and a correct one are indistinguishable to the reader**, and the
understated one gets the finding closed. ⭐ **State the ratio, the denominator,
and the set it is over** — and when a number is superseded, **the record keeps its
numbers and gains a banner**, because a record that is silently corrected cannot
be audited.

### 10. A default that guesses is worse than a default that is plain

**Measured (ISO):** the 5 fenced blocks with no info string are **ASCII-art trees
and field layouts**, not code.

⭐ **What an integrator needs to know:** plain text is the right default for an
un-tagged fence — ⛔ a guess highlights a diagram as Java. ⚠️ **And it is a
narration problem too: a 23-line box-drawing tree read aloud is 23 lines of
punctuation.** Material that leans on ASCII diagrams should expect to write
`alt`/summary text for them.

### 11. A hierarchy in filenames is usually a *redundant* encoding — find the record first

**Measured (ISO, `1e49225`; set: the 41 files in `src/`):** zero directories; 38
unit files in three prefix groups of **16 + 11 + 11**, plus 3 aggregates, **0**
files matching no rule — **and** the curriculum document records the same three
groups in the author's own words, in reading order, with a title and an ordinal
for each of the 38. ⭐ **The two partitions agree exactly.**

⭐ **What an integrator needs to know:** ⛔ **reading the names is derivation;
reading the document is a record**, and §6 prices derivation at one link in eight
going nowhere. Propose *"the curriculum is recorded in `<file>`"* and keep the
prefix rule as a **cross-check that must agree**, never as the source. ⚠️ A skill
that proposes the regex has produced a plausible manifest for this corpus and an
unjustifiable one for the next.

### 12. A scan for markup cannot tell the document's own HTML from another language quoted in a fence

**Measured (ISO, `1e49225`; set: the 41 files in `src/`, then the 38 ingested):**
HTML elements in prose or code **0 of 41**; tag-like tokens outside a fence **0**;
files carrying an ` ```xml ` fence **18 of 41** — of which **3 are the aggregates
that are excluded**, so among the 38 ingested it is **15**.

⛔ **The recorded lesson was the opposite of the real one.** *"18 files contain
raw HTML"* teaches a reader to trust an angle-bracket scan; the real lesson is
that **the fence is what makes the difference**, and a scan that does not track
fence state cannot see it. ⚠️ **Cost of getting it wrong: raw HTML, blockquotes
and thematic breaks were scheduled into the block vocabulary on this evidence,
and this corpus uses none of the three.**

⭐ **The spec half of this is already corrected** — §1's C3 carries the retraction
— ⛔ **and the catalogue half is this entry**, because the *method* error outlives
the one number it produced.

### 13. Title-derived slugs collide hardest where two series mirror each other

**Measured (ISO, `1e49225`; set: the 38 unit titles the curriculum records,
slugged naively):** **7 collision classes**, **15 of 38 units (39.5%)** inside
one, **6 classes of exactly two** — the deliberate server/client mirror — **1
class of three** reaching into the fundamentals group, and **0 collisions inside
a single container**.

⭐ **The shape is what generalises, not the number:** teaching material that
covers the same topics for two audiences produces near-total title collision **by
construction**, and it is the *good* material that does this. ⛔ A second measured
data point for *an address is recorded, never derived*, from a corpus of an
entirely different shape from the one that produced the first.

### 14. A reconnaissance report decays; assert instead

**Measured (ISO; set: the 41 files in `src/`):** round 1 reported *"three files
end without a trailing newline"*. The real answer is **32 of 41**. ⛔ Round 1
generalised from the three files where the discrepancy happened to be visible,
and its harness **printed** numbers where the round-2 harness **asserts** them.

⭐ **The difference is not effort — it is `print(n)` versus `assert n ==
expected`.** ⛔ **A reconnaissance deliverable is a script that fails, not a
document that states**, and it is re-run when the **framework** moves, not only
when the material does: three of that integration's twelve open questions closed
between two rounds a day apart, one of them by a merged schema changing.

### 15. The check and the exposure are not in the same place — verify an ignore rule in **both** directions

**Measured (ISO):** a knowledge-index tool appended a line to the corpus's root
ignore file during a session in which no command wrote a file — ⛔ in the one
repository where non-destructive generation is absolute, under an owner
specifically watching for it. ⚠️ **The same tool wrote a machine-local absolute
path into a settings file inside the corpus**, which is a personal-data exposure
created by **tooling** rather than by an author.

⭐ **What an integrator needs to know:** ⛔ **the non-destructive check runs at
build time and this class of edit happens at index time**, long before any build,
so a corpus's diff against its own tracked files is worth running at the *start*
of a session. Make a generated directory ignore **itself**, and verify both ways:

```
printf '*\n' > <corpus>/<generated dir>/.gitignore
git check-ignore -v <generated dir>/<a file>   # expect the rule, from that file
git check-ignore -q <a real source file>       # expect exit 1 -- NOT ignored
```

⚠️ **A rule that ignores everything is easy to write and easy to get
catastrophically right**, which is why the negative direction is not optional.

### 16. *"Complete at the reading floor"* is only checkable if the never-used surface is **listed**

**Measured (ISO):** **0 build files, 0 `.java` files, 0 graders** anywhere in the
repository, and a narration footprint of **21–83 MiB against a ~5 GB soft
limit** — roughly **1%**.

⛔ **Two plans look identical** — one for a corpus genuinely complete without the
execution track, one whose planner forgot it existed. ⭐ **What separates them is a
table naming every framework capability the corpus will never use, with the
reason**: for that corpus the runner, Run and Submit, the practice panel, the
whole exercise-generation and toolchain-image epics, execution onboarding, the
server-side practice record, attachments, video, multi-variant filing, and the
media-footprint *refusal* path.

⭐ **A corpus with no graders is complete at the reading floor, not short** — but
saying so is an assertion and the table is its evidence. ⚠️ It is also the only
way the framework learns **which of its consumers exercises none of that
surface**.

> ⭐ **SHARPENED 2026-09-10 by `SK-08`, and the sharpening is the half this entry
> was missing.** ⛔ **A table that is written is not a table that is checked.**
> ⚠️ **The trap is that a *partial* never-used table is worse than none, because
> it looks exactly like a complete one and therefore looks like the check was
> done** — and the capability a planner forgets is, by construction, the one
> they also forget to list.
>
> ⭐ **So the check is COVERAGE against an enumeration of the framework's
> capabilities, never SUBSET.** ⛔ Naming ten capabilities that exist proves
> nothing: **the claim this table makes is about the ones that were not named**,
> and only an enumeration can see those. ⚠️ Run the other direction too — a
> capability listed as unused that the corpus's own terminal milestone
> *delivers* is a row saying nothing about this corpus, and it inflates the
> table that is meant to be the evidence.
>
> ⭐ **What makes it runnable rather than aspirational is that the enumeration
> now exists**: `docs/capability-index.md`, generated. ⛔ Before it, the only
> enumeration was thirteen epic documents, which is why this entry could ask for
> the table and not for the check.

### 17. Neither the verb nor the pronoun decides runnability — entry 8's counter-example

**Measured (ISO):** the imperative scan (`implement | write a | your task |
exercise`) over a 3,863-line Gherkin document returns **0**; the same scan plus
one plausible phrase, *"complete the"*, returns **14** — ⛔ **all fourteen with a
*system* as grammatical subject**, not one addressing the reader. ⚠️ **Under any
threshold rule, 14 > 0 flips `exercises` to `true` for a corpus that asks the
reader to do nothing.**

**And the obvious repair fails in the other direction:** second-person address is
**2 occurrences in 3,863 lines** in the material that is *not* exercises, and
**350 across 34 of 38** prose units. ⛔ **A pronoun scan marks 34 of 38 units as
exercises.**

⭐ **Both tests are cheap, both look principled, and on one real corpus they are
wrong in opposite directions.** ⛔ **The question that survives is entry 8's —
whether the reader is under an obligation** — and answering it costs reading,
which is why nobody wants it to be the answer.

### 18. A rule that forbids globs meets a content-addressed cache, and one of the two has to give

**Measured (ISO):** a generated directory of **79 files, 67 of them content-hash
named** (`<64 hex>.json`). ⛔ **A "name each file, one reason each" rule is not
expensive against it — it is unsatisfiable**: the list is invalidated by the tool
that produced it, and it would cost 79 entries and ≥1,580 characters of reason
that stay correct until the next re-index.

⚠️ **And the sharpest version is when the framework mandates the tool:** a
convention requiring a knowledge graph, a skill writing its ignore rules, and a
validator refusing its output are **three correct decisions composing into a
corpus that cannot pass**.

> ⭐ **AMENDED 2026-09-10 by the framework, and the amendment is why the entry
> stays.** ⛔ **`W28` ruled *the corpus is what the corpus's own repository
> tracks*** — a declared-output directory that ignores itself is no longer
> enumerated at all, so the 79 stop being findings. ⚠️ **What does not go away is
> the shape**: an auditable-by-enumeration rule and a content-addressed directory
> are incompatible, and the framework had to move rather than the corpus. ⭐ **The
> entry records the *collision*, not the one instance that has since been fixed.**

### 19. A pattern that is correct only because of which files do **not** exist is not a declaration

⛔ **Adopted 2026-09-10 (check 6's third run), from the ruling that closed
`F18`.** ⚠️ **Ruled and not yet shipped: it lands with `SF-35`**, and it is
recorded now because the rule is what a corpus author meets, not the commit.

**Measured (ISO):** after the framework stopped enumerating declared output,
**17 tracked files** remained unclassified. ⭐ **Three globs cover all 17** — and
`[CLR]*` covers `CLAUDE.md`, `LICENSE` and `README.md` **only because
`TestCases.md` begins with T.** ⛔ **The integrator who measured that refused to
propose it**, and the refusal is the entry.

> ⛔ **A declaration that a file will not be read is either an EXACT PATH, or a
> glob whose wildcard lies inside a directory prefix that is itself entirely
> not-material.**

⚠️ **Why the obvious objection does not save the clever glob.** A framework can
already catch a loose pattern that sweeps up **material** — the file is in
`include` too, and that collision is a finding. ⛔ **The hole is the file that
does not exist yet:** a `CHANGELOG.md` next year, matched by `[CLR]*` and not
yet in `include`, is classified by a reason that was never about it — ⛔ **and
the *unclassified* check that would have surfaced it goes quiet, because the
file is now classified.**

⭐ **So the cost of a clever glob is not paid by the author who writes it.** It
is paid by whoever adds a file to that repository months later and is told
nothing. ⛔ **Five honest entries, not three clever ones**, and the test is one
question: *would this pattern still be right if somebody added a file tomorrow?*

⚠️ **And this is where a generator earns its place (R19):** a skill that drafts a
manifest must draft **exact paths and directory-scoped globs**, because a
generator fitted to today's tree is the same defect with nobody to notice it.

### 20. A refusal that quotes the value it refused is where personal data leaves a repository

⛔ **Adopted 2026-09-10, from `SK-08`, and measured on the framework side rather
than a corpus's.** ⚠️ **Seventeen refusals in ONE new package reproduced the
value they were refusing** — `f"{task_id}: ..."`, `f"{value!r} is not a
marker"` — written by somebody who had read R7 that morning and believed they
were following it.

⭐ **What an integrator needs to know, and it generalises past this project:**
⛔ **the branch that fires *because* a value is not a slug, not an ordinal, not
a member of a closed set, is exactly the branch an absolute path arrives at.**
So quoting the offender takes the one input **guaranteed** to carry somebody's
home directory and puts it in a log, a CI transcript, or a pasted bug report —
and the first thing anybody does with a refusal is paste it somewhere.

⚠️ **The reason this is a trap and not a slip is that the wrong phrasing is the
helpful one.** *"`/home/…/private` is not a marker"* is a better error message
by every ordinary standard, and every reviewer who has ever asked for a clearer
error has asked for exactly this.

> ⭐ **A refusal names the FIELD, never the value.** *"a finding's `marker` is
> not a marker; the vocabulary is closed at local, structural, none."*
> ⛔ Counting is safe where quoting is not: *"2 capabilities are named twice"*
> tells the caller what to look for without reproducing anything.

⭐ **And where a value genuinely must be quoted, constrain its shape BEFORE
quoting it, never after.** A document cited by name in six refusals is first
refused unless it is a **bare filename** — after which quoting it cannot carry
a path, by construction rather than by care. ⚠️ **That is the same move as
passing `path.name` instead of `path`**, arriving at a plain string parameter
where nobody thinks to look for it.

⛔ **Do not rely on noticing this in review.** It was found by a probe that
calls every public callable with a poisoned home path and fails the build on
any refusal that echoes it — and it found all seventeen at once, in a package
whose author had just written the rule down in its own docstring.

### 21. The curriculum record's end is a **label**, and reading past it is silent

⛔ **Adopted 2026-09-18 by `QA-04`, from the first corpus's clean conversion.**

**Measured (ISO):** the record the adapter reads for reading order, titles,
ordinals and grouping is **two documents in one file** — the curriculum for 38
units, and below it an outline of a document the manifest declares
`not_material`. ⛔ **The only thing that marks the boundary is a label.**

⭐ **What makes it a trap rather than a parsing detail:** the **361 heading
lines** below that label carry **no link into the material**. ⛔ **So a reader
that ran on instead of stopping would fold all 361 into the last container,
read ZERO extra units out of them, and report success** — the right unit count,
the right three groups, `validate` clean, the adapter's own audit clean.

⭐ **What an integrator needs to know:** ⛔ **the count is not the check.** Every
instrument the framework offers agrees on 38 whether or not the reader stopped
where the record stops, *because the failure adds no unit*. ⭐ **So the boundary
is asserted DIRECTLY and in both directions** — the refusal fires the moment the
anchor is gone, and does not fire on the record as it stands. ⚠️ **A refusal
nobody has watched fire is a refusal nobody knows still works.**

⚠️ **Why this is an entry and not a hole in a skill** (R19): ⛔ **the anchor is
source-specific** — a label here, a horizontal rule in the next corpus, a
front-matter key in the one after — ⭐ **so no generator can write this test, and
filing it here hides nothing.** ⛔ **What a skill CAN generate is the
OBLIGATION** to write the run's findings down, and that half is a hole, filed
separately.

⚠️ **Relation to entry 7.** Entry 7 is the same region seen from the
*exclusion* side — *what do I drop*. ⭐ **This is the reader's side — *where do I
stop*** — ⛔ **and unlike a bad exclusion, stopping in the wrong place raises
nothing anywhere.**

### 22. A framework wave's reach into a built corpus is decided by the **layer**, not the size — regenerate and diff

⛔ **Adopted 2026-09-18 by `QA-04`, from the first corpus's regeneration.**

⭐ **R19 means a fix reaches a corpus only by regeneration, so a planner has to
price one.** ⛔ **The price is not proportional to how much framework landed.**

**Measured (ISO):** a pin advanced across **nine closed rows**, three of which
changed what a reader sees on every page. ⭐ **What the regeneration moved, in
its two steps:**

| step | what moved |
|---|---|
| regenerate the consuming half | ⭐ **8 files, every one of them the framework's own generated half** — the install record, the pin, three skill stubs, the reader's document, the manifest, the generated non-destructive check. ⛔ **Zero archive documents. Zero pages. Zero clips** |
| rebuild the site on the advanced pin | ⭐ **1 file — the site stylesheet**, which is where the three rows a reader sees landed. ⛔ **The archive re-ingested BYTE FOR BYTE at its recorded date, and the build replaced every page it declares WITH THE SAME BYTES** |

⭐ **What an integrator needs to know:** ⛔ **a regeneration is a DIFF, and the
diff is the deliverable, not the site.** ⚠️ **Predict which artifacts should move
BEFORE running it**, from which layer each row landed in — renderer, template,
stylesheet, scaffold, generated document — ⛔ **and treat anything else that
moves as unexplained and STOP.** ⭐ **A byte that moves for a reason nobody
predicted is the whole signal a regeneration gives**, and a rebuild that is
simply declared green throws it away.

⚠️ **The corollary that costs real money:** ⛔ **re-synthesis is the expensive
step and a regeneration does not imply it.** Narration is content-addressed, so
a regeneration that does not move the speakable text writes **no clip at all**
— ⭐ **but a row that DOES move that text re-narrates the whole corpus.** ⛔ **So
that is the one change class worth looking for by name before advancing a pin**,
and it is not visible from the row count.

### 23. Size narration against a **measured** per-unit ratio — the pre-synthesis estimate is the weaker number

⛔ **Adopted 2026-09-18 by `QA-04`, from the first corpus narrated end to end.**

**Measured (ISO), counted on disk rather than taken from a report:** **38 of 38**
units narrated → **1,364 clips**, **110,783,344 bytes**, at `mp3`, one voice,
`chunk_chars` 1800. ⭐ **That is ≈36 clips and ≈2.8 MiB per unit of prose.**
⚠️ **A second run with nothing changed wrote 0 clips**, so the cost is paid once
per text, not once per build.

⚠️ **This catalogue's own entry 16 records 21–83 MiB for the same corpus**, taken
2026-09-10 — ⛔ **before a single clip existed.** ⭐ **The measurement lands above
the top of that range, and this entry states both rather than quietly replacing
one:** ⚠️ **why they disagree is NOT established here, and asserting a cause
would be inventing one.**

⭐ **Why this is a scoping fact and not something a skill already produces:**
⛔ **`studyforge plan` prints a footprint for a corpus that already HAS a
manifest.** ⚠️ **A planner deciding whether to commit to a corpus at all has no
manifest yet** — ⭐ **what they have is a table of contents and a unit count, and
what they need is a number to multiply it by.** ⛔ **That number is ≈2.8 MiB per
unit, and it is a FLOOR on the disk a corpus costs, never a ceiling.**

⛔ **The direction matters, and it is why the weaker number is the dangerous
one:** the media limit is a **refusal** path. ⭐ **Under-sizing does not degrade
the product — it stops the build.**

---

## ⛔ Decisions on contributions **not** adopted — 2026-09-10, check 6's second run, **amended by the third**

⭐ **A contribution silently not adopted is indistinguishable from a contribution
nobody read.** ⛔ **So every item is dispositioned here, including the refusals,
and each names why against the *belongs / does not* table above.**

⭐ **CHECK 6, THIRD RUN — 2026-09-10, measured on `../ISO-8583-jPOS-tutorial` @
`6c8dc85` against this file @ `d1270cd`.** ⛔ **`docs/studyforge/catalogue-contributions.md`
is UNCHANGED since `1e49225`** — ⭐ **still sixteen contributions, so the run
adopts no new entry from that file.** ⚠️ **What the third run exists for is the
two DEFERRALS, and both of their triggers have now fired**: `F18` ruled (Ruling
90/98) and `F19` ruled (Ruling 91), both in the direction *the framework
changes*. ⭐ **Both rows below are closed, and one of them left a durable
constraint behind, which is entry 19.**

⚠️ **The run also names what it did NOT sweep:** `questions-for-framework.md`
(+317 lines) and `tasks.md` (+68) moved in the same window and are **questions
and a plan**, not catalogue contributions — ⛔ **they are routed through the
board's question channel, and a check that quietly widened its own instrument
would be the defect this catalogue's entry 4 describes.**

| Contribution | Decision | Why |
|---|---|---|
| *Excluding a file can discard the only witness to something else* | ⭐ **Already carried** | Entry 5's closing paragraph states the same trade — the aggregates are both pure duplication and the only machine-checkable order oracle. ⛔ **Not a second entry; a duplicate entry is the defect this catalogue exists to stop** |
| *A count restated at a new set travels further than the measurement* | ⭐ **Already carried** | Entry 8's correction banner **is** this contribution, and entry 9 gained the *set* field by it. ⭐ **It landed by the mechanism it argues for** |
| ⛔ *A placement profile that interleaves output with the source will have its output re-read as source* | ⛔ ~~**DEFERRED**~~ → ✅ **CLOSED as a FINDING, 2026-09-10 (check 6, third run)** | ⛔ **The trigger fired: `F19` ruled (Ruling 91, CTO round 26), and it ruled that the framework changes.** ⭐ **`W28` made `source_files()` ask git what the repository ignores, so generated output under an interleaved profile is no longer enumerated at all** — ⛔ **which is *"if the framework changes, it was a finding"*, exactly as the deferral said.** ⚠️ **Its residue is not a catalogue entry either:** *`studyforge plan` prints the ignore lines its profile requires* is now an **acceptance condition on `SF-31`**, and *verify the rule in both directions* is already **entry 15** |
| ⛔ *A manifest needs three states for a file* | ⛔ ~~**DEFERRED**~~ → ✅ **CLOSED as a FINDING, 2026-09-10 (check 6, third run)** | ⛔ **The trigger fired: `F18` ruled (Ruling 90, sharpened by Ruling 98), and it ruled that the framework changes** — `content` gains `not_material`, and the task is `SF-35`. ⭐ **So the contribution as filed does NOT become an entry: adopting it would publish a limit that is being removed, which is the one thing a catalogue must not do.** ⚠️ **What the ruling CREATED is durable and is adopted as entry 19 below** — ⛔ **a new constraint on how the third state may be written, which no ruling removes because it is the ruling** |
| ⭐ *The `F2` correction* | ✅ **Landed, and it was already landed** | ⛔ **Measured this run rather than assumed: spec §1's C3 carries the retraction and `E02` carries it too.** ⭐ **Its catalogue-shaped half is now entry 12** — the method error, not the number |
| ⭐ *The `F8` donation — a plausible short parse in real material* | ✅ **ADOPTED, and it is a fixture, not an entry** | ⛔ **A contents document listing 36 of 38 units as list items and 2 as headings: a parser written against the list form reads 36, emits 36, and raises nothing.** ⭐ **Carried as `W32` on the board with an owner and a trigger** — ⚠️ **a catalogue entry would have been the wrong destination for something a fixture can assert** |

---

## ⛔ The `QA-04` sort — 2026-09-18, every finding the first conversion produced, and where each one went

⭐ **`M8`'s deliverable is the findings log, and the log's hard part is the
SORT.** ⛔ **A sort that puts everything in this catalogue has not been done;
neither has one that puts nothing here.** ⚠️ **So every finding the conversion
produced is dispositioned below against the *belongs / does not* table at the
top of this file, including — especially — the refusals.**

⛔ **THE RULE THAT DECIDES MOST OF THEM:** ⭐ ***anything a skill could generate is
a hole in the skill (R19), and filing it here HIDES it.*** ⚠️ **Most of what a
first conversion produces is exactly that**, which is why **13 of the 16 items
below are refused** and the three that are admitted are the ones no generator
could ever have written.

| what the conversion found | verdict | why, against the admission rule |
|---|---|---|
| the generated non-destructive check reads working-tree state — RED on a correct re-build, satisfied by committing | ⛔ **REFUSED — hole, filed and CLOSED** (`W331`) | ⭐ **The check is GENERATED.** Filing it here would publish, as a durable limit, a defect the framework had already removed — ⛔ the one thing this catalogue must not do (its own `F18` precedent) |
| a re-survey of an onboarded corpus flips four recorded answers and cannot run unattended | ⛔ **REFUSED — hole, filed** (`W341`) | ⭐ **Reconnaissance reading the manifest's own declarations is a SKILL's job**, so this is a hole with a row, not a truth about material |
| one hand-added file under a declared `not_material` glob presents a corpus complete at the reading floor as unfinished | ⛔ **REFUSED — same hole, same row** (`W341`) | ⚠️ **Tempting, because it reads like a trap real material sets.** ⛔ **It is not: the framework can tell a person's file from its own and does not** |
| a superseded GENERATED glob is promoted to a person's and nothing will ever drop it | ⛔ **REFUSED — hole, filed** (`W342`) | ⭐ **The manifest's own `content` handling decides this**; a corpus meets it only because the framework cannot recognise its own output across a version |
| the procedure pins a commit and builds against a moving working tree; the pin check asks whether the checkout HOLDS the pin, not whether it is AT it | ⛔ **REFUSED — hole, filed** (`W343`) | ⭐ **The generated pin check is the framework's.** ⚠️ **The durable half — *a build reads the source its pin names*** — ⛔ **is a RULING the row must land, not an entry** |
| `R8`'s floor is evidenced INDIRECTLY, because the only instrument that opens a `file://` URL lives where a corpus cannot reach it | ⛔ **REFUSED — hole, filed** (`W344`) | ⚠️ **The finding is true of the tool the office had and false of the framework's capability.** ⭐ **A catalogue entry would teach the next source to accept the weaker claim** |
| the spec's corpus table still names this corpus's graders as a file the user ruled out | ⛔ **REFUSED — hole, filed** (`W339`) | ⭐ **A wrong line in the spec is a defect against a document**, and this catalogue is not where a spec is corrected |
| a corpus's ADDRESS MODEL — where its curriculum lives, and its filename→container mapping — lives in adapter code where the manifest cannot show it | ⛔ **REFUSED — hole, filed** (`W340`) | ⚠️ **The sharpest refusal of the set, because the mapping IS this corpus's headline contribution to the design.** ⛔ **And that is precisely why it may not be filed here: *a constant a second corpus would have to retype* is R19's own definition of a hole** |
| a fence with no info string; the label for un-highlighted prose; raw HTML; which title wins when the index and the file disagree | ⛔ **REFUSED — RULINGS** | ⭐ **The table at the top of this file excludes a ruling in its own words** — it belongs in the spec, an epic or a convention. ⚠️ **That they are ruled in a board archive and nowhere a next source reads is a FINDING, not an entry** |
| a corpus that declares no graded practice is complete at the reading floor, not short | ⛔ **REFUSED — already carried** (entry 16) | ⛔ **A duplicate entry is the defect this catalogue exists to stop** |
| the scaffold writes Python packages into a corpus and generates no ignore rule for their bytecode, which carries an absolute home path | ⛔ **REFUSED — hole, and NOT yet filed** | ⚠️ **Measured: the host repository's ignore file is written for the host's own language and knows nothing about Python.** ⭐ **Entry 15 ALREADY carries the remedy** — *an ignore rule goes inside the directory it is about, verified both ways* — ⛔ **so a second entry would hide that the skill does not apply its own principle to what it generates** |
| narration is additive to the pages, asserted by stripping it; a second narrate run wrote 0 clips; a second run of the procedure leaves a valid corpus | ⛔ **REFUSED — not findings** | ⭐ **The framework working as designed.** ⚠️ **Recorded as a negative result in the log, which is what a negative result is for** |
| the curriculum record is two documents in one file and only a label marks the boundary | ✅ **ADOPTED — entry 21** | ⭐ **The anchor is SOURCE-SPECIFIC, so no generator can write this test** — ⛔ **filing it hides nothing, and the next source meets the same class of boundary in a different spelling** |
| what a regeneration across a whole framework wave actually moves | ✅ **ADOPTED — entry 22** | ⭐ **A scoping fact a planner needs before committing to a corpus**, and the framework being *right* does not remove it: it is the cost of R19, measured |
| narration's real per-unit footprint, against the estimate this file already carried | ✅ **ADOPTED — entry 23** | ⭐ **`plan` answers this only once a manifest exists; a planner has no manifest yet.** ⛔ **And the media limit is a REFUSAL path, so the weaker number is the dangerous one** |
| the adapter skill obliges no findings log, so `M8`'s own deliverable was produced by hand | ⛔ **REFUSED — hole, and NOT yet filed** | ⭐ **The conversion named this itself, in the docstring of the one test it hand-wrote.** ⛔ **A skill that could generate the obligation and does not is a hole by R19's plain reading** |

## Owed here, not yet written

| Entry | Owed by | Note |
|---|---|---|
| ⛔ **Finding 44 — routed here rather than fixed in `SK-01`** | PO-Integration, with the PO | ⭐ **Two of its three numbers came from the integration side**, so it is a cross-source fact. ⛔ **Fixing it inside `SK-01` would have buried it in one skill, where the next source cannot find it** — which is R19's shape: what a second integrator would have to re-derive belongs *here* |
| ✅ ~~**PO-Integration's ten entries**~~ | — | ⭐ **DISCHARGED 2026-09-10 by wave check 6's second run.** ⛔ **Sixteen contributions measured, not ten**, and the identity is `16 = 6 already counterparted + 8 adopted + 2 deferred`: **6** had counterparts already (the 4 named in round 19 — entries 5, 6, 7, 9 — plus the 2 whose material had landed inside existing entries and is recorded as *already carried* below), **8 are adopted above as entries 11–18**, and **2 are deferred** behind `F18`/`F19` with a trigger. ⚠️ **The `F2` and `F8` rows below are dispositioned in the same table and are NOT among the 16** — they are `F`-series items, not catalogue contributions, which is why adding them reaches 18. ⚠️ **Adoption is the framework PO's, on a wave-open trigger** — the contribution was never the missing half |
| **What a re-run of reconnaissance is** (`F17`) | PO-Integration → PO | ⛔ **Nothing defines a re-run against a moving framework.** The last one happened because a person asked, which is not a mechanism |
| **`OPS-05` checks at build time; tooling writes at index time** (`F12`) | PO → `OPS-05`, `SK-07` | See `W15` on the board |
