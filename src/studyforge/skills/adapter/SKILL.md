# Skill — adapter authoring

**Given a corpus that has been surveyed and a manifest that records what it is,
build the adapter that fills it.** The deliverable is an archive
`studyforge validate` accepts, and the exit code is the whole of the agreement.

⛔ **This skill does not reason about unfamiliar material.** Reconnaissance did
that and its answer is `corpus.json`. If you find yourself deciding here what a
container is, what the reading order is, or which files are material, you are
in the wrong skill and the manifest is incomplete.

---

## The rule that governs every judgement below

⛔ **Done is a machine's answer, not a person's.**

```
studyforge validate <corpus-root>   # 0, or a named list of what is wrong
```

> ⚠️ **A note on the spelling.** This is R2's name for the seam and it is the
> installed command, registered by `pyproject.toml`. ⭐ `docs/authoring/` gives
> the module form that reaches the same code from a checkout nobody installed.
> ⛔ **Every fenced line in this skill is written the way it actually runs.** An
> agent executes a fence.

⭐ Everything in this procedure exists to make that command reachable by
somebody who has never read the framework's internals. `validate` runs checks
about the archive alone, about placement and about the source, and each can
report its own rule ids. A count is not carried here, because it moves.
⭐ The checks are `studyforge.validate.CHECKS`, and this prints their number at
the ref you are reading:

```
python3 -c "import studyforge.validate as v; print(len(v.CHECKS), 'checks')"
```

⚠️ Rule ids have no public registry to count from. `validate`
reports every one of them in a single run, so there is never a reason to fix
one problem per invocation.

⚠️ **A "definition of done" the author has to argue for is not one.** The
adapter's tests below assert the exit code, never a shape somebody agreed
looked right.

---

## Procedure

### 1. Start from the manifest, and read the plan back before writing anything

```
python3 -c "from studyforge.corpus.manifest import load; \
            from studyforge.skills.adapter import plan_for, scaffold; \
            print('\n'.join(scaffold(plan_for(load('corpus.json'))).lines()))"
```

⛔ **Do not start by opening the material.** The manifest already says how many
container levels there are, what the variants are called, and whether this
corpus has exercises at all — and every one of those changes what gets
scaffolded. Starting from the files means re-deriving what somebody already
recorded, and disagreeing with it silently.

⚠️ **The report names one file as yours and every other one as generated.**
Read that listing before you agree to it: it is the whole shape of the work.
⛔ **This page types no count of it** — the listing above is the count, at the
ref you run it at, and a number written here went stale the moment the scaffold
gained a file.

### 2. Answer the execution question by reading it, not by deciding it

⭐ **`exercises: false` is an answer** (§7's three states, C5). A corpus with no
graders is **complete at the reading floor, not short**, and the scaffold emits
no practice path for one — so a scaffold with a `practice` step you did not
expect means the manifest declares exercises and somebody has to produce them.

⛔ **Do not "leave the practice path in, just in case."** A path that is never
taken reads as unfinished work for the entire life of the corpus.

### 3. Scaffold, and let the framework own every path

```python
made = scaffold(plan_for(load("corpus.json")))
made.write(corpus_root)  # ⛔ refuses rather than overwriting anything
```

⛔ **Never compute an archive path by hand.** `studyforge.skills.adapter.Layout`
is the only thing that knows the layout, and the reason is structural: the tree
is five joins deep and four of them fail *silently* when they are wrong.

**There are four places an adapter writes, and this is all of them:**

```text
<corpus-root>/corpus.json
<corpus-root>/archive/<address>/container.json
<corpus-root>/archive/<address>/raw/<variant>/unit-NN/<kind>-N.json
<corpus-root>/archive/<address>/units/unit-NN/
```

⭐ **That tree is `Layout`'s own arithmetic, not a drawing of it**, and this
prints it at the ref you are reading:

```
python3 -c "from studyforge.skills.adapter import archive_tree; print(archive_tree())"
```

⚠️ `unit-3/` instead of `unit-03/` produces a tree `validate` reports as *unit
missing* — at the reader, not at the writer, and only after everything else
looks fine.

#### ⛔ The fourth line is the one adapters get wrong

⭐ **A unit's OWN files go in `units/unit-NN/`, beside `raw/` and never inside a
variant.** `raw/` is per *variant* and holds documents; this one is per *unit*
and holds everything a unit owns that is not a document:

- **every `assets` and `attachments` entry's `local` resolves against it** — a
  `"local": "media/diagram.svg"` is that file *inside the fourth line's
  directory*, and it is what the built page's `<img>` reaches for;
- the authored overlay sits in it as `content.json`, which is a person's file
  and not yours.

⛔ **Neither is written out here as a whole path, deliberately.** The fence
above is the only drawing, and it is computed; a path spelled twice is a path
that diverges once.

⛔ **Ask `Layout.unit_files(address, unit)` for the directory; never join it.**
A variant in that path, or `unit-2/` for `unit-02/`, puts the file where no
build looks: **every media-bearing page then renders a broken glyph** and
nothing else fails at all.

⚠️ **`validate` has an opinion about this now** (`media-missing`): a declared
asset or attachment the archive does not hold where the entry says is named and
refused, so the disagreement surfaces at you rather than at a reader. ⭐ A
capture that named its media and deliberately did not fetch it says so with
`media_skipped`, and that is a state rather than a shortfall.

### 4. ⛔ Run the generated tests **before** you write a line, and read the failure

```
python3 -m pytest tests/<package>
```

⭐ **This is the highest-value step and the one most often skipped.** The suite
fails, and the failure is the specification: it names what `read.containers`
must return, what `read.documents` must return, and that the audit's source-side
count does not exist yet.

⛔ **A scaffold whose tests pass on delivery would be worse than no tests.**
Green against a corpus with no material in it is the one signal nobody
re-reads.

### 5. Write the reading step, and nothing else

⛔ **`read.py` is the only module you write by hand.** Everything downstream of
*"here are the containers and here are the units"* is identical for every
corpus and is already written.

Two rules, and both are §6:

- ⛔ **An address is recorded, never derived.** Do not slugify a title to get
  one. **In one real corpus, 157 of 1,290 units (12.2%) are served at
  a slug their title does not produce** — so a title-derived address is not
  merely fragile, it is wrong for one unit in eight before anybody notices.
- ⭐ **`origin` is verbatim, and it is not decoration.** It is the relative path
  of the file the material was read from, and R3 guarantees that file is never
  touched — so it stays a working link from every generated page back into the
  reader's own material, and it is the field a re-fetch would use.

⭐ **Where `corpus.json` declares `curriculum.containers`** (`corpus_api` 7,
`W340`), the scaffold has already written `containers` and `expected_units`:
`studyforge.skills.adapter.curriculum` files each unit from the declared record
at its declared address, and refuses when the record, or a declared filename
prefix, disagrees with the tree. ⛔ **Change the filing in `corpus.json`, never
in `read.py`.** Only `documents` is yours.

⚠️ **Report what you cannot read; never drop it** (R6). A block the reader does
not recognise is absent from the digest *and* from the counts, so nothing
downstream can notice it went missing. The block vocabulary is closed at **11
types** (`studyforge.archive.blocks`); a construct that fits none of them is a
finding about the vocabulary, not a block to discard.

### 6. Write the count the framework cannot make

⛔ **`read.expected_units` counts from the SOURCE.** ⭐ It sits in `read.py`
with the other two steps, because counting the source *is* reading the source —
and because a scaffold with two hand-written modules has already lost the
property R19 depends on. A check that recounts the
parser's own output agrees with itself by construction and catches nothing —
which is why `validate` can never make this one, and why the audit is the
adapter's and not the framework's.

⚠️ Until it is written the audit reports an **unchecked claim** and exits
non-zero. That is deliberate: *saying an archive was not counted is not the
same as saying it is fine.*

⭐ **Its first run should name the known outliers and nothing else, and that
output is the specification for the follow-up work** — never a problem to be
silenced. An audit that passes because it was taught to ignore things is worse
than no audit.

### 7. Emit for real, and let it refuse

```
python3 -m <package> <corpus-root>
```

- ⛔ **Stage, then move** (§6). The generated `emit` builds the whole archive
  beside its destination and moves it only when every file exists. A container
  map that fails halts every consumer that walks the tree, and the failure is
  then reported at the reader rather than at the writer.
- ⛔ **Nothing outside the archive directory is written, moved or renamed**
  (R3). An edit exists only where the manifest **declares** it.
- ⛔ **No personal data reaches the archive** (R7). The gate refuses; it does
  not rewrite. A refusal names the field, never the value — and *any* string in
  hand-written material can be an absolute path.
- ⭐ **Two runs differ only in `ingested`** (R10). The generated suite asserts
  it, so a dict order or a directory listing that leaked into the output is a
  test failure rather than a mystery three integrations later.

⛔ **Declare the adapter itself, or the first run reports every file of it.**

⚠️ **A scaffolded adapter that the manifest does not declare is reported file
by file, as `unclassified`, and the corpus is `NOT valid`.** ⭐ Correctly: the adapter is code this
corpus is *built with*, and a manifest that said nothing about it left it
unaccounted for, which is how a corpus is read twice or not at all.

⭐ **`corpus_api: 2` is the vocabulary for it, and the scaffold hands you the
data.** `content.not_material` takes **globs**, each with its own reason:

```python
made.not_material  # ({"glob": "ingest/**", "why": ...}, {"glob": "tests/ingest/**", ...})
```

- ⛔ **Paste those into `corpus.json` rather than writing your own.**
  Customisation enters as manifest data (R19) — and *produced* data is the only
  kind that does not go stale when this skill's file list changes.
- ⚠️ **Two globs, not eight paths.** `content.exclude` matches by **exact path
  equality** — `{"path": "ingest"}` classifies nothing at all —
  and `exclude` means *material withheld*, which the adapter is not.
- ⛔ **At `corpus_api: 1` there is no third state**, so a v1 manifest can only
  say this in `exclude`, one exact path at a time, in the wrong words. That is
  the version's limitation and R9 is the answer to it: bump the manifest.

### 8. Hand over the exit code **and** what it does not cover

⛔ Never hand over *"validate passes"* alone. `validate` judges the archive; it
cannot judge whether the archive is the material. What goes with it:

- the audit's output, including every unchecked claim;
- every construct the reader met and could not classify;
- ⭐ **the diff, if any, between what the scaffold generated and what is on
  disk.** That diff is a **finding about this skill** (R19), and it is the only
  signal that the next corpus will need the same hand-edit.

⛔ **And every one of those is WRITTEN, into the findings log, before the run is
declared done — never carried only in a hand-back message**, which is lost with
the message. ⭐ **The log's place, its form and the command that
refuses a run without one are the onboarding skill's step 7**; each entry asks
*could a skill have generated this?*, and a diff against the scaffold answers
`yes` by construction.

---

## What this skill must never do

- ⛔ **Never hand-edit a generated file.** Customisation enters as manifest data
  (R19). `write(..., regenerate=True)` rewrites every generated file the
  scaffold lists and **keeps the one you wrote, untouched** — so re-scaffolding after the framework
  moves is an ordinary, safe thing to do. ⭐ Onboarding's `write` follows the
  same rule, `write_files`, so the two paths cannot disagree.
- ⛔ **Never write into the source repository beyond the archive** (R3), and
  never beyond what `permitted_edits` declares.
- ⛔ **`permitted_edits` may never name** the repository's root ignore file, any
  version-control configuration, or a file R3 reads as content — **repository-root
  documentation included, whatever `content` classifies it as** (R3). ⭐ The
  one predicate is `studyforge.corpus.manifest.edits.reads_as_content`, the stems
  it reads as root documentation are `studyforge.corpus.manifest.edits.ROOT_DOCUMENTATION`,
  and all three are refused by `studyforge.corpus.manifest.edits.parse_edits`.
  ⛔ Read the names there: this skill keeps no copy, and a manifest declaring one
  is refused by name when it loads.
- ⛔ **Never derive an address, an ordinal or a reading order.** §6 rules them
  recorded. If nothing records one, that is reconnaissance's open question
  coming back, and it is answered there.
- ⛔ **Never import an adapter from the framework, and never add a name to the
  framework for one** (R1, R2). The seam is on disk. An adapter that needed a
  framework change to exist is an adapter that has moved the seam.
- ⛔ **Never let the framework's own repository be the reference.** What a
  consumer needs is carried here — in this document, in a contract, or in a
  ruling (R20). A path into the extraction source is an edge that breaks the
  next time anything moves.

---

## Appendix — the contract this skill scaffolds against

⛔ **This appendix is the only copy.** The modules in this directory state the
*rule* and point here; they do not restate the numbers, and — R1 — they name no
corpus at all.

### A1 — what `validate` judges

| | what they are |
|---|---|
| checks | structure, paths and source; the fence under *The rule that governs every judgement below* prints how many |
| rule ids | every distinct way one run can say *no* |
| block types | **11**: the closed vocabulary a document body is made of |

⭐ **The two halves are not substitutes.** The structure checks compare the
archive against itself — a digest against the blocks it was taken from — and
agree by construction where a construct was never recognised at all. The
**source** checks count something the parser did not produce, and they are the
only ones that can see material that went missing between the file and the
archive.

### A2 — the three formats, and the versions this build reads

| document | key | the set this build reads |
|---|---|---|
| `corpus.json` | `corpus_api` | `studyforge.corpus.manifest.KNOWN_CORPUS_API` |
| `container.json` | `container_api` | `studyforge.corpus.container.KNOWN_CONTAINER_API` |
| `unit-NN/<kind>-N.json` | `raw_api` | `studyforge.archive.document.KNOWN_RAW_API` |

⚠️ **A version gate checks the type before the value** (R9). `True in {1}` and
`1.0 in {1}` are both true in Python, so a JSON `true` passes a naive
membership test — which is the one check whose whole job is to refuse a
document this build cannot read. The framework's helper already does this;
an adapter that wrote its own would not.

⭐ **`corpus_api: 2` is why `content.not_material` exists** — the third state
step 7 needs — and **`container_api: 2` is why an `origin` may name a region.** A unit whose
material is *part* of a file records the file as `origin` and the heading it
opens at as `origin_section` — and a map that uses that shape while calling
itself `container_api: 1` is **refused**, rather than read as whole files.

### A3 — an archive document is 15 keys, and 4 more that are appended

The required 15 are, in the order they reach disk: `raw_api`, `source`,
`address`, `variant`, `unit`, `kind`, `ordinal`, `ingested`, `title`, `blocks`,
`video`, `assets`, `attachments`, `counts`, `content_sha256`.

⛔ **The order is the format** (R10): the document is serialised with
`sort_keys=False`, so two runs are comparable byte for byte. The optional four
— `assets_sha256`, `starting_code`, `media_skipped`, `exercise` — are
**appended, never inserted**, so every document written before one existed
still renders the bytes it always did.

⚠️ **Never assemble one of these by hand.** `studyforge.archive.document.build`
runs every gate — the personal-data gate among them — and computes the digest
and the counts. A hand-built dict skips all of it and validates until it does
not.

### A4 — what a scaffold is, and the one file that is yours

⛔ **The whole file set, and how many there are, is the scaffold's own listing
— step 1's fence — never this table.** ⭐ The table names the modules and what
each is for; the scaffold also writes files that are not modules, and a
count typed here would undercount them.

```text
<package>/__init__.py     the contract, and what done means
<package>/read.py         ⛔ YOURS. Three steps: containers, documents, the count
<package>/emit.py         build beside the destination, then move (§6)
<package>/audit.py        the source-side count validate cannot make
<package>/__main__.py     one command, and its exit code is the answer
tests/<package>/test_read.py    run this first; the failure is the specification
tests/<package>/test_emit.py    the whole obligation, in one assertion
tests/<package>/test_audit.py   the count exists, and it agrees
```

⭐ **The ratio is the point.** If a second source has to retype any generated
file, that is a hole in this skill and it is reported as one — never patched
locally (R19).
