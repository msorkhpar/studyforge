# The integration catalogue

**What an integrator learns the hard way, written down once so the next source
starts further along than the last one.** Owned by the framework Product Owner;
entries are contributed by whoever measured them, from either side.

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

---

## Owed here, not yet written

| Entry | Owed by | Note |
|---|---|---|
| ⛔ **Finding 44 — routed here rather than fixed in `SK-01`** | PO-Integration, with the PO | ⭐ **Two of its three numbers came from the integration side**, so it is a cross-source fact. ⛔ **Fixing it inside `SK-01` would have buried it in one skill, where the next source cannot find it** — which is R19's shape: what a second integrator would have to re-derive belongs *here* |
| ⛔ **PO-Integration's ten entries** | PO-Integration | ⭐ **Already written in this document's shape** — adopting them is a copy, and the only thing that was missing was this file. They land by their next commit |
| **What a re-run of reconnaissance is** (`F17`) | PO-Integration → PO | ⛔ **Nothing defines a re-run against a moving framework.** The last one happened because a person asked, which is not a mechanism |
| **`OPS-05` checks at build time; tooling writes at index time** (`F12`) | PO → `OPS-05`, `SK-07` | See `W15` on the board |
