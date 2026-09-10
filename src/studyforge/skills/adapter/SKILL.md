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
studyforge validate <corpus-root>        # 0, or a named list of what is wrong
```

⭐ Everything in this procedure exists to make that command reachable by
somebody who has never read the framework's internals. **Measured at
`f816454`:** `validate` runs **12 checks** — 8 about the archive alone, 2 about
placement, 2 about the source — and can report **23 distinct rule ids**. It
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

⚠️ **The report names one file as yours and seven as generated.** Read that
line before you agree to it: it is the whole shape of the work.

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
is the only thing that knows the layout, and the reason is measured: the tree
is five joins deep and four of them fail *silently* when they are wrong.

```text
<corpus-root>/corpus.json
<corpus-root>/archive/<address>/container.json
<corpus-root>/archive/<address>/raw/<variant>/unit-NN/lesson-N.json
```

⚠️ `unit-3/` instead of `unit-03/` produces a tree `validate` reports as *unit
missing* — at the reader, not at the writer, and only after everything else
looks fine.

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
  one. **Measured on one real corpus: 157 of 1,290 units (12.2%) are served at
  a slug their title does not produce** — so a title-derived address is not
  merely fragile, it is wrong for one unit in eight before anybody notices.
- ⭐ **`origin` is verbatim, and it is not decoration.** It is the relative path
  of the file the material was read from, and R3 guarantees that file is never
  touched — so it stays a working link from every generated page back into the
  reader's own material, and it is the field a re-fetch would use.

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

⚠️ **Measured 2026-09-10, at `corpus_api: 1`:** scaffolding an eight-file
adapter into a clean corpus and validating produced **8 `unclassified` findings
— one per file — and `NOT valid`.** ⭐ Correctly: the adapter is code this
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
  equality** — **measured:** `{"path": "ingest"}` classifies nothing at all —
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

---

## What this skill must never do

- ⛔ **Never hand-edit a generated file.** Customisation enters as manifest data
  (R19). `write(..., regenerate=True)` rewrites the seven generated files and
  **still refuses the one you wrote** — so re-scaffolding after the framework
  moves is an ordinary, safe thing to do.
- ⛔ **Never write into the source repository beyond the archive** (R3), and
  never beyond what `permitted_edits` declares.
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

### A1 — what `validate` judges, measured at `f816454`

| | count | what they are |
|---|---|---|
| checks | **12** | 8 structure, 2 paths, 2 source |
| rule ids | **23** | every distinct way one run can say *no* |
| block types | **11** | the closed vocabulary a document body is made of |

⭐ **The two halves are not substitutes.** The structure checks compare the
archive against itself — a digest against the blocks it was taken from — and
agree by construction where a construct was never recognised at all. The
**source** checks count something the parser did not produce, and they are the
only ones that can see material that went missing between the file and the
archive.

### A2 — the three formats, and the version each is at

| document | key | at `f816454` | this build reads |
|---|---|---|---|
| `corpus.json` | `corpus_api` | **2** | 1 and 2 |
| `container.json` | `container_api` | **2** | 1 and 2 |
| `unit-NN/<kind>-N.json` | `raw_api` | **1** | 1 |

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

**Eight files, seven generated:**

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

⭐ **The ratio is the point.** If a second source has to retype any of the
seven, that is a hole in this skill and it is reported as one — never patched
locally (R19).
