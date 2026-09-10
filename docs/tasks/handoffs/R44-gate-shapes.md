# R44-gate-shapes — handoff

**Kind:** ruling record

*Ruling 44 — the gate's open set, and the three layers that answer it.*

**Status:** done — one commit.

**What landed:**

- **`src/studyforge/sourcepath.py`** — new. `source_path_fault(value)` and
  `is_source_path(value)`: one predicate, one permitted set, for every field a
  reader types as a path. This is the import a consumer wants.
- **`corpus.container.fields.optional_path`** and
  **`corpus.placement.profile.origin_directory`** now ask it. Same verdict,
  always; each keeps its own error type and its own sentence.
- **`archive.scrub`** — the home-path shape gained its second spelling
  (`~<name>/`), and the pattern set split: `SHAPES` (refuse) and
  `SCRUBBED = SHAPES + ALSO_SCRUBBED` (rewrite).
- **`tests/test_gate_layers.py`** — the matrix: nine shapes, three layers, two
  control rows, and `RESIDUAL` declaring what the gate cannot see.
- **`tests/studyforge/test_sourcepath.py`** — the permitted set exercised.

⛔ **Not fixed by adding two regexes.** The ruling said an open set answers to
defence in depth with every layer asserted, and that is what landed.

---

## What the probe measured, before anything changed

⚠️ **The probe cross-checks `assert_clean` against `list(leaks(...))`**, because
the coordinator's own probe of this hole reported all four shapes REFUSED —
`leaks` is a generator and truthiness on a generator is always `True`. Every
verdict below is two readings that had to agree.

```text
shape                              gate      path reader   is_absolute
POSIX home path                    REFUSED   REFUSED       True
macOS home path                    REFUSED   REFUSED       True
tilde-rooted path                  passes    REFUSED       False
tilde-username path                passes    REFUSED       False
home under a longer prefix         passes    REFUSED       True
Windows drive home path            REFUSED   passes        False   ⛔
UNC share home path                passes    passes        False   ⛔⛔
a directory merely named home      passes    REFUSED       True    (control)
a location inside the source       passes    passes        False   (control)
```

⭐ **Two rows the ruling did not have.** `C:/Users/<name>/x` passes the *path
reader* and is caught only by the gate — the exact reverse of Ruling 42's
dependence, in the direction nobody had looked. And
`\\host\home\<name>\README.md` passed **both**: a third hole, found by
measuring the two that were reported.

---

## The decision the ruling asked for

> *"You cannot fix two overlapping refusal sets without deciding which is the
> rule."*

⭐ **The rule is: where the legal set can be written down, write it down.**
`container.fields.optional_path` refused `startswith("/")`, `startswith("~")`,
`".." in parts`. `placement.profile.origin_directory` refused `is_absolute()`,
`".." in parts`. Two forbidden lists, two open sets, and the gap between them
was reachable — ⛔ *and neither of them was wrong on its own terms*, which is
why adding entries to both was never going to end.

New module **`src/studyforge/sourcepath.py`** states the permitted set instead:

```text
a source path is legal when ALL of these hold
  at least one segment          excludes  ""  "   "  "/"
  not absolute                  excludes  /home/<n>/x, /export/home/<n>/x, /anything
  first segment not ~-rooted    excludes  ~/x, ~<n>/x
  no segment is ".."            excludes  ../outside, a/../../b
  no segment carries "\"        excludes  \\host\home\<n>, a\b
  no segment carries ":"        excludes  C:/Users/<n>/x, file:///etc/passwd
```

Both readers now ask it; each keeps its own error type and its own sentence
(the rule is `sourcepath`'s, the document is the caller's — SF-01's precedent).
⚠️ **The last two rows narrow the legal set below what POSIX permits, on
purpose**, and the module says so: a file really may be called `notes:draft.md`
on Linux and this rule will not place it. That is the price of refusing
`C:/Users/<name>`, it is bounded, and an adapter is told exactly which
character it may not use.

---

## The gate: one shape gained a second spelling, and the set split in two

⭐ **`~<name>/` is not a fourth entry — it is the second spelling of the home
path shape.** `~<name>/notes` and `/home/<name>/notes` name the same account by
the same structural anchor, so `SHAPES` still holds three environmental
shapes and that ruling is untouched. The branch requires a leading letter and a
following slash, because prose says `~5` and `~50 lines` constantly (asserted).

⛔ **`/export/home/<name>` cannot be closed at the gate, and this is the finding
worth more than the fix.** It is *the same shape* as `/var/lib/home/cache`.
Nothing distinguishes them. A gate that refused the first refuses the second,
and `assert_clean` refusing a legitimate corpus with a diagnosis that looks
exactly like a leak is the failure the pattern set is already ruled against
(the no-card-pattern argument).

⭐ **So the pattern set split along the module's own oldest ruling.** *"Scrub
our words; refuse the source's"* was written about which **response** each
subject gets. It decides the **width** too, because the two responses have
opposite costs:

```text
SHAPES            the source's free text   narrow   a false positive costs the corpus
ALSO_SCRUBBED     ambiguous shapes         --       never refused, only rewritten
SCRUBBED          our own output           wide     a false positive costs one log line
                  = SHAPES + ALSO_SCRUBBED          superset by construction, not by assertion
```

`/export/home/<name>`, `\host\home\<name>` and a bare `~/` are rewritten in
anything this framework writes, and never refused in anything a source wrote.

---

## `tests/test_gate_layers.py` — the layers named, each asserted

The matrix, with two control rows, plus five properties:

- **each layer does what the matrix says** — 9 rows × 3 layers;
- ⭐ **no path field relies on the gate** — the path rule refuses all seven
  spellings, including the three the gate cannot see;
- ⛔ **`RESIDUAL` is declared** — the three shapes the gate passes are named in
  the source, so closing one is a deliberate edit and a fourth appearing is a
  failure;
- ⚠️ **the gate refuses nothing that names nobody** — `/var/lib/home/cache`;
- ⚠️ **the scrubber leaves a clean path alone** — or every `REWRITES` cell
  above would be satisfied by a scrubber that rewrote everything.

⭐ Also: `_path_field` runs **both** readers and asserts they agree, so finding
3 is closed structurally and not by having fixed it once.

---

## Every control run negatively

Applying the new rule to this task's own instruments, before trusting them:

```text
tests/studyforge/test_sourcepath.py
  rule never fires (return None)        26 failed, 12 passed
  rule always fires                     18 failed, 20 passed
  as shipped                            38 passed

tests/test_gate_layers.py
  tilde branch removed from the gate     2 failed, 11 passed
  scrubber narrowed back to SHAPES       4 failed,  9 passed
  placement back to its own list         5 failed,  8 passed
  as shipped                            13 passed
```

---

## ⭐ The W19 pin fired on its own author

`test_and_the_same_origin_past_that_reader_is_reproduced_verbatim` went red on
this branch, exactly as its comment instructed it would:

> *"If this half ever fails, somebody added a guard downstream and the safety
> argument has moved: read the new guard and rewrite this pair against it,
> rather than deleting the record of where the safety comes from."*

It is now `..._is_refused_by_placement_unquoted`, and a **third** test holds the
leak channel open on a *legal* origin so the pair cannot pass vacuously — the
collision line still quotes whatever placement hands it, and what keeps a home
directory out of it is `source_path_fault` at two call sites instead of one.

---

## Migrations owned by this commit

- `optional_path`'s message was `"an absolute or escaping path"` for every
  fault — a forbidden list read aloud. It now names the fault; the test became
  an eight-row table of `(value, fault)`, three rows of which the old
  predicate did not refuse at all.
- `test_scrub_leaves_a_relative_path_alone` asserted `scrub` left
  `/var/lib/home/cache` alone, with a comment arguing about **the gate**. ⛔
  That test conflated the two responses, which is the conflation this commit
  separates. It is now two tests, one per response.
- Four files carried a literal `C:/Users/<name>` in a new table and tripped the
  repository's own R7 sweep. Built by concatenation now, like every other
  poison in the suite. ⚠️ The check and the tree are green in the same commit.

---

## Decisions

1. ⭐ **The rule is "enumerate the legal where the legal set has an end".**
   Ruling 44 asked which of two overlapping refusal sets is the rule. Neither:
   both were forbidden lists, both open, and the gap between them was
   reachable. The permitted set replaced them.
2. ⛔ **A tilde is *not* added to the free-text gate, and a tilde-username is.**
   `~/src` names *a* home and never *whose*, so by this gate's own ruled
   criterion — *"did this build put it there?"* — refusing a lesson that says
   `cd ~/src` is the no-card-pattern failure. `~<name>/` names an account by
   the same anchor as `/home/<name>/`, so it is the same shape written twice
   and not a fourth entry. ⚠️ This is the one place I did **not** do what the
   ruling's table asked, and it is deliberate.
3. ⛔ **`/export/home/<name>` is not closed at the gate, because it cannot be.**
   It is the same shape as `/var/lib/home/cache`. It is closed for every path
   field and rewritten in our own output; the residual is declared.
4. ⭐ **The pattern set split by *consequence*, not by taste.** A false positive
   in `scrub` costs one over-redacted log line; a false positive in
   `assert_clean` costs the corpus. That asymmetry is this module's oldest
   ruling and had never been applied to the patterns themselves.
5. ⚠️ **The permitted set is narrower than POSIX**: no `:` and no `\` in a
   segment, so `notes:draft.md` is unplaceable. Named in the module, because
   the alternative is `C:/Users/<name>` and `\\host\home\<name>` reaching
   disk, and the cost of *this* choice is visible to the adapter author who
   hits it.
6. ⭐ **The W19 pin was rewritten, not deleted**, exactly as its own comment
   instructed — and a third test was added so the pair cannot pass vacuously.

## Surprises

- ⛔ **The ruling's table had two shapes; the tree had four.** The two
  additions are where the interesting information was: `C:/Users/<name>/x` is
  caught **only by the gate** and `\\host\home\<name>` was caught by
  **nothing**. ⭐ The first is the reverse of Ruling 42's dependence, which
  means the two layers each cover a hole the other has — measured, on this
  tree, which is what turns defence-in-depth from a slogan into a fact.
- ⚠️ **Half of the reported hole turned out to be unclosable at the layer the
  ruling named it against**, and finding that out cost more than the fix. The
  budget assumed "widen the gate"; the work was "prove the gate cannot be
  widened here, then find the layer that can".
- ⭐ **The W19 pin fired on its own author.** I wrote the instruction *"if this
  half ever fails, somebody added a guard downstream — rewrite this pair
  against it"* eight days of work ago and then triggered it myself.
- ⚠️ **Four of my own new tables tripped the repository's R7 sweep** on a
  literal `C:/Users/<name>`. The check I was extending caught me writing its
  own poison — which is the sweep working, and a reminder that a poison table
  is built by concatenation like every other one in this suite.

## Measurement

Pinned image, `docker/dev/check`:

```text
base  8e8a2c5   2261 passed, 8 skipped   quality floor: clean
tip             2330 passed, 8 skipped   quality floor: clean
ruff format --check .   307 files already formatted
ruff check .            All checks passed!
```

File sizes against R11: `scrub.py` 365/400, `sourcepath.py` 97/400,
`test_scrub.py` 548/600, `test_paths.py` 443/600, `test_gate_layers.py` 153/600.

---

## Findings

⛔ **Filed unmarked in the first version of this handoff, and that was C6.**
This branch is cut from `8e8a2c5`, after the marker convention merged, so C5
does not cover it. Three findings, three markers.

### 1. `[local]` The residual is real, and it is stated rather than closed

A **title** or a **block of prose** a source authored, carrying
`/export/home/<name>/x`, still reaches disk. It is refused for every path
field and rewritten in anything this framework writes, but free text has one
layer and that layer cannot see it — `/export/home/<name>/x` and
`/var/lib/home/cache/x` are the same shape.

⭐ **Cost named:** if this is ever to close, it closes with the
declaration-based residual class already specified in `scrub`'s contract — a
corpus declaring the exemption, counted and named in the build report — ⛔ not
a fourth regex. `RESIDUAL` in `tests/test_gate_layers.py` names the three
shapes, so a fourth appearing is a build failure rather than a discovery.
⚠️ Marked local rather than structural because the *mechanism* is now written
down in `scrub`'s contract and asserted, so the next author meets it rather
than re-deriving it.

### 2. `[structural]` The two personal-data gates have drifted apart in their shapes

`tools/quality/personal_data` and `archive.scrub` are ruled to have **different
subjects** — one is a local development check that may know this machine, the
other gates untrusted corpus content and may know nothing. ⛔ **That ruling
justifies two policies; it never justified two vocabularies**, and the two have
drifted:

```text
in tools/quality, absent from scrub   .local hostname
in scrub, absent from tools/quality   bare-home `~/`, `\home\<name>`, tilde-username
```

A `.local` hostname is personal data in an archive document exactly as much as
in a source file. ⚠️ **This would happen again to anybody who touches either
gate**, because nothing compares them and no reviewer has caught it — twice
now. ⭐ Ruling 31 forbids the import, so the answer is to **share the evidence,
not the code**: one committed table of poison shapes with, per layer, whether
it must refuse / scrub / report, and a test on each side that reads it. A
divergence then has to be declared with a reason instead of discovered.

⭐ **Answered by Ruling 47 and scheduled to me with W20.** Recorded here so the
route is in the handoff and not only in a message.

### 3. `[local]` `scrub` and `scrub_document` have no production caller yet

The wide set is therefore correct-and-unused until a build report exists.
⭐ **Cost named:** none today, and the reason it is filed is so the first caller
does not re-derive whether it may rely on the wide set. It may — that is what
`SCRUBBED` is for, and `tests/test_gate_layers.py` asserts it on every shape.

## For dependents

- ⭐ **Import `studyforge.sourcepath` rather than writing a path check.** Any new
  reader with a path-shaped field asks `source_path_fault(value)` and raises its
  own package's error with its own sentence. ⛔ A third spelling of this rule is
  the defect this commit removed; `tests/test_gate_layers.py::_path_field`
  asserts the existing two never disagree, and a third belongs in that assertion
  on the day it exists.
- ⚠️ **`assert_clean` is not a path check and must not be used as one.** It is
  narrow on purpose and there are three shapes it cannot see. A field that is a
  path is protected by the layer above it.
- ⭐ **`scrub` is now wider than the gate.** Text this framework emits may be
  scrubbed more eagerly than a corpus is refused — including `/var/lib/home/…`,
  which is a deliberate over-redaction. Anything asserting `scrub(x) == x` on a
  path containing a `home` segment will need `shape_in(x) is None` instead.
- ⛔ **`SF-10` and anything adding a new document reader:** the gate is one
  layer of three and the matrix in `tests/test_gate_layers.py` is where a new
  layer registers. Adding a reader without a path rule is how the next
  `\\host\home\<name>` gets in.
- ⚠️ **W20 carries Ruling 47** (finding 2's shared evidence table), so anybody
  planning to touch either gate before W20 lands should expect the table to
  arrive and to be the place a divergence is declared.
