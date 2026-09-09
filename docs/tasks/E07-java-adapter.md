# E07 — Java ingestion adapter

The first consumer. Turns `Claude-senior-java-engineer` into a valid corpus.

**Shared context for this epic.** The adapter's **entire** obligation is to
write a valid archive (R2): a manifest, 45 container maps, and 166 archive
documents. Nothing downstream is its concern — it does not render, does not
narrate, does not know a page exists. `studyforge validate` (SF-25) is its
definition of done, which is why SF-25 is a dependency of JS-05: the adapter is
built against a machine-checkable signal rather than anybody's judgement.

**The material.** 10 curriculum sections → 45 modules → **166 lesson READMEs**
(166 sub-READMEs + 45 module READMEs + 1 root = the 212 files on disk, so
nothing is unaccounted for). Lessons are *mostly* uniform: **132 of 166 carry
exactly nine `##` headings** — *Concept Explanation, Code Examples, Common
Pitfalls, Interview Q&A Section* and the rest — and the remainder range from 6
to 13, some with numbered variants (`## 3.2.4. Checked vs. Unchecked
Exceptions`). They ingest as ordinary heading blocks, which still gives SF-15
its jump list and E04 its narration chunking cheaply — but **not for free**:
every consumer of that structure must handle a ragged heading set, not the
canonical nine.

**Why this is wiring, not parser work.** SF-07's strict Markdown reader already
exists and is proven. The adapter reads structure and delegates content.

⛔ **R3 — nothing existing is modified.** No README is moved, renamed or
rewritten. Generated artifacts land beside them (§5). OPS-05 asserts it.

**Measured facts this epic depends on** — established by counting the real
repository, not assumed:

| | |
|---|---|
| Curriculum sections | **10** |
| Lesson READMEs | 166 — **all 166 links resolve; zero broken** |
| Lessons with exactly the canonical nine headings | 132 of 166 (**79%**) |
| Implementation classes | 177 |
| Test classes | 168 |
| **Impl classes with no `<Name>Test.java`** | **14** — nine of them in `08-object-oriented` |
| **Maximum name-paired exercises** | **163**, not 168 |
| **Lessons naming an impl class that exists in their module** | **162 of 166 (97%)** — the attachment signal |
| Modules where lessons ↔ classes are cleanly 1:1 | 87% (39 of 45) |
| Outliers | `08-object-oriented` (3 lessons / 11 classes), `22-locks-semaphores` (2/4), `21-synchronization` (2/3), `01-java-basics` (4/5), `25-fork-join` (5/4), `29-date-time-api` (8/7) |
| Not a lesson container | `00-base` — 0 READMEs, holds a shared test utility |
| Markdown constructs beyond SF-07's vocabulary | 10 files with `---` thematic breaks, 1 with a blockquote |
| Images · video · raw HTML · mermaid | **zero of each** — the material is clean prose, code fences and tables |

---

⚠️ **This epic is SK-02's and SK-07's first output, not their input** (spec §9,
E11). The adapter package, its test tree and its audit command are **scaffolded
by the skills** before any source reading is written here — reversing the
original plan, where these tasks came first and the skills were reverse-
engineered from them at M7. What remains genuinely this epic's own work is the
part that is irreducibly source-specific: reading Java's curriculum, its lessons
and its class pairings.

⭐ **Anything in this epic that a second source would also have to write is a
finding against a skill** (R19), not work to be repeated. Record it; do not
absorb it.

---

### JS-01 — Corpus manifest and placement
**Milestone** M2 · **Depends on** SF-02, SF-03, SK-07 · **Team** solo
**Owns** `JS/ingest/corpus.py`, `JS/corpus.json`
**Context** ~25k — spec §4–§5, `JS/README.md` curriculum section

**Definition.** The corpus's declaration: two container levels
(`section`, `module`), one variant (`java`), exercises enabled, sibling
placement. Fixes the artifact naming scheme for this corpus.

⛔ **Ignore rules must NOT edit the repository's existing root `.gitignore`.**
It is a pre-existing 110-line file, and R3 forbids editing a root ignore file
outright — no declaration permits it. Generated audio and discovery caches are
ignored by **new** `.gitignore` files written *inside the generated directories
themselves*, which are new files and therefore R3-clean. ⭐ This ruling has since
been generalised: it is R3's second forbidden category, and SK-07 applies it to
every corpus rather than this one remembering it.

This is a small thing that matters: `OPS-05` is the one task whose entire value
is that it cannot be relaxed, and this is exactly the pressure that would relax
it.

**Acceptance.** The manifest loads. Declared placement resolves a real unit's
page beside its own `.md`. Names are unique across all 166 units. The declared
level labels render as "Section › Module › Lesson". **The root `.gitignore` is
byte-identical after a full build.**

---

### JS-02 — Curriculum parser
**Milestone** M2 · **Depends on** JS-01 · **Team** pair
**Owns** `JS/ingest/curriculum.py`
**Context** ~40k — `JS/README.md`, a sample of module `README.md` files

**Definition.** Reads the root README's curriculum into the ordered hierarchy.

**The README is authoritative, not the directory listing.** Ordering, titles
and membership all come from it, including the source's own numbering
(`4.4.1`), which is the ordering authority and the basis of artifact names. A
directory that exists but is not linked is not part of the curriculum; a link
pointing at a missing file **stops the run** (R6).

`00-base` is recognised as a utility module: no lessons, not a container, and
it stays on the classpath for E08.

⚠️ **Two link formats and one dead end.** Most entries read
`- [1.1. Title](path)`, a handful read `- 1.5. [Title](path)` — the number
outside the link. And `08-object-oriented` carries fourth-level bullets
(`2.3.1.1`–`2.3.3.3`) that have **no README and no home in a two-level address
model**; they are curriculum detail, not units. Recognise both formats; report
the fourth-level bullets rather than inventing units for them.

**Acceptance.** Produces exactly 10 sections, 45 modules, 166 lessons. Every
lesson resolves to a file that exists — verified: **all 166 links resolve
today, zero broken**. Both link formats parse. Fourth-level bullets are
reported, not ingested. A deliberately broken link fails by
name. Ordering matches the README top to bottom.

---

### JS-03 — Lesson reader
**Milestone** M2 · **Depends on** SF-07, JS-02 · **Team** solo
**Owns** `JS/ingest/lessons.py`
**Context** ~35k — SF-07 output, a sample of `JS/**/README_*.md`

**Definition.** Each lesson README through the strict Markdown reader into
blocks. Headings arrive as heading blocks and are not special-cased — they are
simply structure. ⚠️ The set is **ragged**: 132 of 166 lessons carry the
canonical nine, the rest carry 6 to 13, some numbered. Anything consuming that
structure handles the real distribution, not the ideal one.

⚠️ **Two constructs in this corpus are outside SF-07's vocabulary today** — 10
files use `---` thematic breaks and one (`33-dry-principle/README_8.3.1.md`)
uses a blockquote. A parser whose rule is *raise, never drop* will stop on 11
files. Extending the vocabulary is SF-07's job and must happen before this task
runs, or M2 stalls on it.

Any construct the reader refuses is reported by file and line and **never
dropped** (R6). That report is the definition of the fix-up work; it is not a
reason to loosen the parser, because a parser that shrugs is how CodeSignal
previously lost bold, images and code-fence languages without anyone noticing.

**Acceptance.** All 166 lessons parse, or every failure is named with file and
line. Heading structure is preserved. No lesson yields zero blocks.

---

### JS-04 — Source pairing
**Milestone** M2 · **Depends on** JS-02 · **Team** pair
**Owns** `JS/ingest/sources.py`
**Context** ~40k — `JS/*/src/`, spec §7 attachment rules

**Definition.** Pairs each implementation class with its test class, then
attaches pairs to lessons.

⭐ **Attach by the class the lesson README already names.** Measured: **162 of
the 166 lessons name an implementation class that exists in their own module** —
a 97% exact signal, far stronger than ordinal position with similarity
fallback, which was this task's original design and is now the *fallback* for
the remaining four. The material tells you the answer; read it rather than
inferring it.

The four that name no existing class are precisely JS-06's first report:
`02-control-flow/README_1.2.5.md`, `03-methods/README_1.3.3.md`,
`10-sealed/README_2.5.3.md`, `22-locks-semaphores/README_6.3.1.md`,
`29-date-time-api/README_7.3.2.md` — verify this list rather than trusting it,
since it is a count of a moving target.

⚠️ **This same signal is EX-01's method-selection input** (spec §7). The
methods a lesson discusses are the methods it teaches, and therefore the
methods worth blanking. Expose it as output, not as an internal detail.

**The pairing matters more than the attachment.** E08's gates need
implementation ↔ test pairs; attachment only decides *which lesson* an exercise
appears under, so an imperfect attachment costs placement, not correctness.
⚠️ **14 implementation classes have no matching test**, nine of them in
`08-object-oriented` — so the ceiling is **163 pairs, not 168**. The six
outlier modules attach unmatched pairs to their module's final lesson.
**Nothing is dropped silently** (R6).

**Acceptance.** Reproduces the measured counts: 177 implementation classes, 168
test classes, **163 name-pairs, 14 unpaired implementations named
individually**. At least 160 lessons attach via the named-class signal. The six
outlier modules are named and their pairs attached rather than lost. The
method-selection signal is exposed for EX-01.

---

### JS-05 — Archive emission
**Milestone** M2 · **Depends on** JS-03, JS-04, SF-06, SF-25 · **Team** pair
**Owns** `JS/ingest/emit.py`
**Context** ~45k — SF-06 and SF-25 outputs, JS-03/JS-04 outputs

**Definition.** Writes the manifest, 45 container maps and 166 archive
documents. **This is the whole of the adapter's obligation** (R2).

⭐ **Records `origin` for every container and every unit** (spec §6): the
relative path of the README the material was read from. Verbatim, never derived
from a title. For this corpus R3 guarantees that file is never touched, so the
recorded path is a permanent working link from every generated page back into
the reader's own material — and it is the same field a source fetched from
somewhere else would use for its upstream address.

⚠️ **Stage, validate, then move** (spec §6). A container map that fails its own
validation is never left at the path `validate` and SF-10 will read: one
unreadable map halts every consumer that walks the tree, and the failure is then
reported at the reader rather than at the writer.

**Acceptance.** `studyforge validate` passes on the emitted archive. Re-running
produces identical bytes apart from `ingested` (R10). **No pre-existing file is
modified** beyond the manifest's declared `permitted_edits` (R3). Every unit
carries an `origin` that resolves to a file that exists. **A deliberately
corrupted emission leaves no file at the target path.** Declared practice counts
in container maps match what E08 will later emit, or are recorded as zero until
it does.

---

### JS-06 — Ingest audit
**Milestone** M2 · **Depends on** JS-05 · **Team** solo
**Owns** `JS/ingest/audit.py`
**Context** ~25k — JS-02…JS-05 outputs

**Definition.** R6's enforcement for this corpus. Exits 1 naming every lesson
with no blocks, every broken curriculum link, every unmatched class, every
module whose lesson and class counts disagree, and every declared practice that
is absent.

Its first run should name **exactly the six known outliers and nothing else** —
and that output is the specification for any follow-up work, not a problem to
be silenced. An audit that passes because it was taught to ignore things is
worse than no audit.

**Acceptance.** Exits 1 with a named list on a deliberately damaged corpus.
Exits 0, or exits 1 naming only known outliers, on the real corpus. The output
is readable — a list of names and reasons, not a stack trace.
