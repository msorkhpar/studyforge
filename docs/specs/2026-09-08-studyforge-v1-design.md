# studyforge — design

**What this document is.** The design of the framework as it exists: what it
does, the rules it holds itself to, the contracts it reads and writes, and the
reason behind a behaviour wherever the reason helps a reader. The code is the
authority on *how*; this document is the authority on *what* and *why*.
Decisions that shape the code but are not rules of the design are in
[the decisions file](../decisions.md), each pointing back at the rule it serves.

---

## 1. What this is

`studyforge` turns **any body of teaching material** into a local, offline study
site: a reading page per unit, narrated, navigable, with a table of contents,
progress tracking, and — where the material supports it — practices with real
graders or quizzes checked by the local study server.

It is extracted from the CodeSignal study system, which proved every one of
these surfaces against real material. What CodeSignal did for one source,
`studyforge` does for any source:

> *"a second source — another course site, a book, a repository of exercises —
> must be able to populate the same API and get the same tutorial site out of
> it. The endpoint shapes are the contract; the reading page is a consumer of
> them."*

⭐ **The framework is designed against several material shapes at once, so the
generalisation is real rather than retrofitted.** A framework proven on a small
source and then applied to a large one has been tested; one grown around a large
source and later pointed at a small one has been fitted.

### The four shapes the contracts must fit

| Source | Container levels | Runnable | Graders |
|---|---|---|---|
| `Claude-senior-java-engineer` | 2 — section → module | Maven multi-module | **test classes paired with the implementation, authoritative** |
| CodeSignal | 2 — path → course | Gradle and Python, containerised | hidden upstream; local tests advisory only |
| ISO-8583-jPOS-tutorial | **1** — group, encoded in filename prefixes | Java examples in the prose, no build file | **none** shipped by the source |
| Claude-SPARQL-tutorial | **1** — course | a containerised query server and notebooks | none, but **every lesson ends in an exercise** |

A contract that cannot express all four is wrong. A contract that requires
special-casing any of them is wrong.

⭐ **The *Graders* column records what a source ships**, which is what a planner
reads to know whether a corpus's own tests can back its practices. It is not what
a reader gets: exercises are also authored at ingestion from a source's examples,
code and pages ([*Exercises authored for every
corpus*](#exercises-authored-for-every-corpus), §7). A row claiming graders for a
corpus whose manifest says `exercises: false` is refused by the test that reads
this table against each pinned corpus's `corpus.json`.

### What the shapes teach

Each shape carries a constraint the design would otherwise meet late.

**C1 — A hierarchy can be encoded in filenames, not directories.** A corpus's
groups may live in one flat directory, distinguished only by a filename prefix
(`1.md`, `s1.md`, `c1.md`). Nothing in the filesystem expresses the grouping.
This is what R4 is for: the adapter maps prefix to group, and a generated
artifact is locatable by the identity it carries inside it, never by its path.

**C2 — A corpus can carry the same material twice, at different granularities.**
A source may ship per-unit files *and* whole-series aggregates that concatenate
them. An adapter that globs every Markdown file ingests everything twice and
nothing complains. So the manifest declares what is in and what is out (§4), a
file nobody classified is a validation failure, and reconnaissance (§9) detects
the overlap rather than leaving it to be noticed.

**C3 — Real Markdown carries constructs a strict parser must already know.** The
Markdown reader raises on anything it does not recognise, which is the reason the
vocabulary has to be right before a new source is attempted. The constructs that
matter in practice: raw HTML, thematic breaks, blockquotes, and XML **inside a
fence**. ⭐ **Fence-awareness, not tag counting**: a reader that scans for `<`
without tracking fences reads a `pom.xml` sample as markup, and either raises or
renders it as HTML.

⛔ **A disclosure is a third state, not markup.** `<details>`/`<summary>` in
teaching material usually hides an exercise's answer. Flattening it into ordinary
blocks keeps the text and destroys the hiding; storing it as one opaque raw-HTML
block keeps the hiding and makes the body invisible to everything else —
uncounted, unhighlighted, unnarrated. *Present but withheld* is real content, and
it is the `disclosure` block, which holds blocks exactly as `quote` does (§6).

**C4 — Material includes companion files that are neither blocks nor media.** A
dataset a lesson loads, a notebook, a sample document: the reader needs them, and
they are not prose, not images, not video. The archive carries them as
**attachments** — files a unit references and the reader can open — distinct from
the media a page renders inline (§6).

**C5 — An exercise can exist with no grader, and that is not "no exercise".** A
lesson may end in a prompt that nothing checks. The exercise contract therefore
distinguishes three states, not two: **no exercise**; an **ungraded** exercise (a
prompt the reader works, with nothing to check it); and a **graded** exercise,
whose trust is `authoritative` or `advisory` under R5. Only the third can complete
a practice. ⭐ **A source with no grader is not a source with no exercises** —
graded ones are authored for it at ingestion (§7) — and ungraded stays a
first-class state for a prompt nothing can back.

---

## 2. Governing rules

These are rulings, not preferences. A task that violates one is not done.

**R1 — The framework knows nothing about any source.** `studyforge` must not
import from, name, or branch on any adapter. Every source-specific fact
arrives as data, through the manifest or the archive.

⭐ **AMENDED 2026-09-23 — what *names* means, carried from the review rubric when it
was archived.** ⛔ **A source's name in framework source is a failure even inside a
comment**, because the next reader takes a name as licence to branch on it. A fixture
under `tests/` that names a *shape* is fine; a module under `src/` that names a *corpus*
is not. ⚠️ **A name is matched in the forms people actually write it** — the repository
slug, and the corpus named in English (*the Java corpus*) — and each is anchored on a
word only a corpus's name takes: a bare `ISO` is far more often an ISO 8601 date, and a
check that cannot tell the two apart is switched off within a day. ⭐ The floor's
source-names check is the enforcement, so R1 is answered on every run rather than by a
reviewer's grep.

**R2 — The adapter seam is on disk, not in Python.** An adapter's entire
obligation is to write a valid archive. It gets no callbacks and no framework
API. This is what lets adapters be built in any language, tested in isolation,
and assigned to different agents in parallel.

**R3 — Generation is non-destructive, and every exception is declared,
additive and asserted.** No existing file in a source repository is moved,
renamed or deleted. The framework *adds* artifacts alongside the material.

⛔ **An edit to an existing file is permitted only where the corpus manifest
declares it** — `permitted_edits`, naming the file, the exact insertion and why
(§4). An undeclared edit is a build failure. A declared edit that proves not to
be additive — it removes or rewrites an existing line — is **also** a build
failure, so a declaration cannot be used to smuggle a rewrite past the rule.
⛔ **The check reads the declaration**; it never hardcodes one corpus's
exception. The Java repo's additive `<module>practice</module>` line in the
root `pom.xml` is one entry in that list, not a special case in the framework.

⛔ **Three edits are never permitted, however declared:** the repository's root
ignore file — write new ignore files *inside* generated directories instead;
any version-control configuration; and any file the material's own reader
depends on as content.

⛔ **Content is a property of the file in its repository, not of the site's
`content` policy** (`W278`, `INT-13/1`). A file the policy includes or contests
is content, and so is **repository-root documentation**: a root `README`,
`LICENSE`, `LICENCE` or `COPYING`, of any suffix, which the repository's own
readers read whatever the manifest classifies it as for the site. ⭐ The
manifest parser refuses such a declaration and the non-destructive check a
declared change to it, through one predicate.

⭐ **The reverse of every declared edit is recorded.** An onboarding that cannot
be undone is one nobody will run against a repository they care about.

⛔ **R3 DISTINGUISHES THE BUILD'S OWN PRIOR OUTPUT FROM THE USER'S MATERIAL, and
a file the build wrote last time is not somebody's material** — it is the
build's own previous answer, and replacing it is the build answering again.
⭐ **So a rebuild may overwrite exactly the paths its own generation created, and
which those are is not a guess: `studyforge plan` enumerates every path a build
creates before it creates one.** ⛔ **R3 still protects everything else
absolutely — a hand-edited file, a foreign file, or any path the enumeration
does not name is REFUSED BY NAME and never replaced** — ⚠️ **and an enumeration
that has drifted from what the build writes is a build failure rather than a
licence, because the two are asserted to agree path for path.** ⭐ **Ruled by
the user, 2026-09-12, answering *what does a rebuild do*; the six decisions it
belongs to are in the delivery epic, `docs/tasks/E09-delivery.md`.**

**R4 — Location is data; identity is embedded.** The framework never infers
what a file *is* from where it sits. Every generated artifact carries its own
address inside it, and the server discovers artifacts by scanning.

⚠️ **Precisely: identity survives a move; presentation need not.** A moved page
is still correctly identified, still appears in the contents, still resolves as
the unit it is. Its stylesheet, scripts and sibling audio resolve *relative to
the page* (R8, §5), so a page moved away from its assets renders unstyled and
silent. Both are true and neither is a defect — conflating them would either
force absolute asset paths (breaking the `file://` floor) or force a fixed tree
(breaking placement). Discovery's acceptance tests identity, not rendering.

**R5 — Nothing generated is presented as more authoritative than it is.**
Inherited from CodeSignal's R10. A grader written by us against a hidden
upstream grader is `advisory`. A grader that shipped with the material and is
proven by the gates in §7 is `authoritative`. The framework refuses to render
the first as the second.

⭐ **EXTENDED 2026-09-19 (`W389`) — R5 keeps every word above and gains one case.** A
grader **authored at ingestion** — tests written by a model from the page, or from the
source's own example code — is `generated`, and therefore `advisory`. It ships only
when it clears §7's [authoring gates](#exercises-authored-for-every-corpus-w389), whose
record ships beside it and which `studyforge validate` re-reads; an exercise that
cannot clear a gate does not ship, and the coverage report names the gate that refused
it and why. ⛔ **The vocabulary does not grow.** No third trust level is minted:
`generated` still can never be `authoritative`, and a gate record is evidence for a
claim, never a promotion of it. ⭐ **What the READER is shown is a sentence, not the
vocabulary** (the user's ruling, 2026-09-19): `provenance` and `trust` are the
framework's internal words, and §7 fixes the learner-facing wording each one renders
as. ⛔ **A label is never omitted because it is unflattering.**

**R6 — Fail loud, never silently short.** A unit with no content, a broken
curriculum link, an unmatched class, a declared practice that is absent — each
is reported by name and exits non-zero. Inherited from CodeSignal's
`run_capture_audit` and the reason `layout.py` exists at all.

⭐ **AMENDED 2026-09-23 — R6's general form: enumerate the legal, never the illegal.**
Carried from the module-structure convention when the conventions were archived. It is
the rule that most often decides *how* a refusal is written, so it lives beside the
rule that demands one.

> ⛔ **A list of forbidden things is an open set: the unforeseen case is admitted
> silently. A list of permitted things is a closed set: the unforeseen case is
> refused, and somebody has to decide.**

⚠️ **Both lists are always incomplete; what differs is what incompleteness does.** An
open set fails toward acceptance — nothing raises, and the defect is found by its
consequences, which is precisely what R6 forbids. A closed set fails toward refusal,
loudly, at the boundary, naming the thing it did not expect. A refusal costs a
question; a silent admission costs whatever the unforeseen case does.

- ⭐ **Where the legal set can be written down it is enumerated, through one
  predicate** — keys, versions, profiles, skip causes, contract fields, filename
  components, slugs, legal pairings of values. A derived class, such as the
  characters a label may hold, is computed from that predicate and never typed out a
  second time. ⚠️ A hand-written character blacklist for filenames once let a vertical
  tab, a form feed, a non-breaking space, a line separator, a quote, a colon and an
  asterisk through two gates at once, and one of them breaks R8's `file://` floor.
- ⭐ **Better still, the illegal value is made unrepresentable**: a key is required to
  be a slug rather than slugified into a possible collision, and a parameter is typed
  so that a leaking value cannot be passed. ⛔ **The tell of the wrong shape is a check
  that grows by one entry every time somebody hits a case nobody thought of** — adding
  the entry conceals the shape for one more round. A list that is genuinely right (a
  sanctioned exception) is short, and each entry carries its reason.
- ⛔ **The domain limit.** Where the legal set cannot be written down — free text,
  whose permitted set is *all text that is not personal data* — a forbidden list is
  forced and known-incomplete by construction. What is owed then is depth, never
  length: every layer is asserted on its own, because the argument for depth is that
  no layer is sufficient, and the docstring says the list is known-incomplete so that
  nobody mistakes it for a closed set. R7's layered gates are the worked example.
  ⭐ **Enumerability is a property of the domain, not a choice the author makes.**
- ⚠️ **A guarantee does not extend to what sits beside it.** Closing one set says
  nothing about its neighbour, and the closed half is the one everybody reads —
  including its own author. When a guarantee is asserted, the adjacent thing that is
  *not* asserted is named beside it. *A file being clean is not a property of the
  file.*
- ⛔ **Where one helper names several faults, every caller either refuses all of them
  or says in its own body which it does not, and why.** A phrase in a refusal
  vocabulary that no caller can reach is a missing guard: a path helper named three
  faults and one of its two callers guarded only two, so a tilde-rooted edit target
  was accepted while the sentence refusing it existed and could never be printed.

Where each of these is enforced is recorded in [the decisions file](../decisions.md),
under *Refusals, errors and personal data*.

**R7 — No personal data reaches disk or the wire.** Every string entering the
archive passes `assert_clean`, which **refuses** rather than rewrites. No
absolute home path, account id, name or email in any generated file, log or
report.

⭐ **AMENDED 2026-09-23 — how R7 is upheld in code.** Carried from the review rubric and
from the personal-data conventions when they were archived. The rule above states the
outcome; these are the properties the code holds so that the outcome never depends on
somebody noticing.

- ⛔ **R7 has three subjects: this repository's tracked files, the archive, and the
  rendered page.** A home path that reaches a page has reached a file R7 governs,
  however clean the other two are.
- ⛔ **Every string composed for the archive, a log, a report or an outbound request
  passes the personal-data gate, and the gate refuses.** A gate that scrubs silently
  produces a clean file and a false belief.
- ⛔ **A refusal describes the fault and never formats the value.** A branch that exists
  *because* a value is an absolute path, and prints that value, has taken the one input
  guaranteed to carry a home directory and written it into a log from inside the check
  meant to prevent it. ⛔ **An exception object is never formatted into a message
  either**: `OSError` formats itself with the filename it was given, so a refusal names
  the field it means — `strerror`, `errno` — and says what it knows itself. ⚠️ **The
  rule is blanket, including where one exception type happens to be harmless**,
  because auditing each type at each call site is the work nobody does twice, and the
  site that gets skipped is the one holding a filename.
- ⛔ **A *why it failed* field carries a code, never a captured stream.** When the
  framework runs another process, the reason it records is an exit code, a timeout
  with its bound, or a failure class — never standard output, standard error, a
  filename or an argument. A captured stream is the richest source of absolute paths
  there is, and the counts are the useful half anyway.
- ⛔ **The personal-data refusal travels through every caller as itself.** It is not a
  `ValueError` and belongs to no package's error family, deliberately: a family exists
  so that a walk can catch one type per item and continue, so translating a leak into
  one turns a hard stop into a skipped item, logged as *that unit did not build* under a
  green report. ⭐ A package that promises *only this error* states the exception that
  crosses it in its own contract instead of swallowing it.
- ⛔ **An emitter and its gate agree on one input.** Where one module refuses to emit a
  value class and another admits it, both are run on the same input, and a
  disagreement is a defect in either direction: a lax gate is a hole, a strict one a
  silent drop.
- ⛔ **A gate whose verdict is part of a published contract is a pure function of its
  input.** The archive gate is half of what `studyforge validate` promises an adapter
  (R2), so it imports nothing that could read the environment and gives the same
  verdict on every machine. ⭐ The repository's own hygiene sweep is the mirror image:
  its subject *is* this machine's leak surface, so it may derive the machine's identity
  at run time. ⛔ Neither is a model for the other, and *align them* is the wrong
  instinct.
- ⭐ **One shape vocabulary, two policies.** Those two gates have different subjects and
  may differ in what they do with a match, never in which shapes they recognise. They
  share evidence rather than code: one table, whose product copy is
  `tests/harness/personal-data-shapes.json`, gives every shape a column per gate, and
  ⛔ **a row whose columns disagree carries a `why`**, so a divergence is declared with
  a reason instead of discovered by a reviewer. The rows are measured against the real
  implementations, so a row that stops being true is a build failure. ⭐ The last rows
  are controls that nothing refuses — a table whose every row read *refuse* would be
  satisfied by gates that refused everything — and every spelling is stored as
  fragments, because a real shape written whole into the table would be a finding
  against the table.
- ⛔ **A gate's false positive on ordinary source is a defect in the gate.** An author
  who renames a field to get past R7 pays a real cost and leaves no trace, and the next
  author pays it again; a checker people rename fields around is on its way to being
  switched off. ⚠️ The shape known to be over-broad is the local hostname, which also
  matches a Python attribute access at the end of an expression; its remedy narrows
  that one lookahead while keeping the hostname shape, in both gates together.
- ⭐ **A sanctioned negative fixture is the one place a personal-data shape is
  required**, because a gate needs an input to refuse. It is legal only while all five
  hold: the value is fabricated and unreachable (an RFC 2606 reserved domain, a user
  who is obviously nobody); it is traceable to nobody on any machine; it lives in one
  named directory whose purpose is to be refused, with a file beside it naming the rule
  and what the gate should say; tests assert both directions — nothing else in the
  fixture tree carries the shape, and the sanctioned value really does trip the gate —
  and the registry of such directories is itself asserted. ⛔ A repository-wide sweep
  excludes that directory and only that one, by name; a sweep that excludes `tests/`
  wholesale has stopped checking the tree where fixtures live.

**R8 — The site works over `file://` with no network and no server.** Every
asset is local. A served origin adds the API, progress and Run/Submit; it is
never a prerequisite for reading.

**R9 — Contracts are versioned.** An unknown version is refused, never migrated
in place at read time.

⛔ **The list of versioned fields lives in `studyforge.version.CONTRACT_FIELDS`,
not here** (ruled round 15). This sentence used to enumerate five and the code
now holds seven; a list written twice is a list that disagrees with itself, and
this one already did. ⚠️ The register below says *which contract*; the constant
says *which field name*; a task that versions a new contract adds it to the
constant **in the same commit**, or the guard cannot see it.

⭐ **Why this drifted is worth keeping.** The five originally listed are every
document the framework **writes**. The authored overlay is the one it only ever
**reads** — so it fell out of an enumeration built, without anyone deciding it,
around authorship. ⛔ **A contract is versioned because somebody reads it, not
because we wrote it** (SF-09's diagnosis, and the reason R21 exists).

⚠️ **A declared v1 limitation: titles must slugify to something** (ruled round
16). `slugify` replaces every non-ASCII-alphanumeric run with a separator — it
does **not** transliterate — so an accented title is mangled rather than
converted (`Ströme` becomes `str-me`) and a title with no ASCII letters at all
produces an empty slug and is refused. ⛔ **That is a limitation of this
framework, not a defect in the corpus**, and every refusal must say so: R1 means
the framework knows nothing about a source, including which alphabet it is
written in.

⛔ **Open — transliteration.** Taking it later renames every generated page, so
it is recorded now rather than discovered by the first non-English corpus. ⚠️ All
four designed corpora are English, so nothing has ever exercised this. ⭐ A
consequence that is *not* deferred: two titles differing only in accented
characters can collide, invisibly in the source, which is why **SF-25 checks
generated names and not only addresses**.

⭐ **AMENDED 2026-09-23 — a version gate checks the type before the value.** Carried
from the module-structure convention when it was archived. `True in {1}` and
`1.0 in {1}` are both true in Python, so a JSON `true` or `1.0` passes a bare
membership test — the one check whose whole job is to refuse a document this build
cannot read. ⛔ The gate refuses a value that is not an `int`, and refuses a `bool`
explicitly because `bool` is a subclass of `int`. ⭐ There is one implementation,
`studyforge.version` (§3.2), and every versioned contract is read through it: one
membership test per contract is one chance per contract to write the porous one.

**R10 — Generated output is byte-for-byte reproducible.** No clocks, no
dependence on filesystem enumeration order. The same inputs produce the same
bytes on any machine.

⚠️ **A content digest in a filename is not a violation of this rule** — it is
deterministic, and therefore reproducible by construction. The rule that bans
digests is narrower, and it is about *churn*: ⛔ **a shared asset linked by
every page carries a plain name**, because a digest there renames a file and
rewrites every page that links it whenever a colour changes, buying nothing a
local reader wanted. An artifact linked by **one** page, regenerated in the same
run as that page, is not in that class; §8.2 rules on it.

⭐ **AMENDED 2026-09-23 — what R10 forbids in code, and its two exemptions.** Carried
from the review rubric and the module-structure convention when they were archived.

- ⛔ **No clocks and no randomness in anything that reaches a generated file**: no
  wall-clock or monotonic reads, no uuids, no random bytes. A timer used for a log line
  is still a clock if that log is an artifact. ⭐ **There are two exemptions and only
  two:** `container.json`'s `ingested` field, which is excluded from `content_sha256`
  so it cannot make unchanged content look edited (§6); and synthesised audio bytes,
  because a speech model is not byte-stable and the clip is content-addressed instead
  (§8.2). ⛔ **A new exemption is an amendment to this rule**, never a local decision.
- ⛔ **No dependence on filesystem enumeration order.** Every listing is sorted before
  it is used, and an `os.walk` sorts its directory and file lists *in place*, because
  sorting the outer call orders nothing.
- ⛔ **No dependence on set iteration order.** String hashing is salted per process, so
  a set of strings iterates stably within one run and differently across two. A set is
  sorted before it reaches an artifact; a `dict`'s insertion order is guaranteed and is
  fine.
- ⛔ **An order that reaches a file is the format.** A constant that decides a
  serialised order is asserted element for element, in order, against the artifact —
  membership and length leave exactly that property unasserted. ⭐ When two orders
  disagree, the one that reaches disk wins, because changing it rewrites every
  document that was already correct.
- ⭐ **The claim is proved by building twice into two directories and comparing**: the
  two are identical, or identical apart from `ingested` and said so.

**R11 — No file grows past the size a person can hold in their head.** Soft
ceiling **400 lines** for a module, **600** for a test module. A unit
approaching it becomes a **package** of focused modules with one clear purpose
each. This is inherited debt to be paid *during* extraction, not after: the
largest modules in the port surface are several times the ceiling, and they
arrive as **packages or not at all**. ⚠️ **Every measurement of a source
repository in this document is a dated snapshot** (§8) — a task counts its own
port surface at start rather than inheriting a number, and *how much* of a
source module is ported at all is its own question: the Java repo ships its
graders (§7), so CodeSignal's grader-guessing scaffolder is largely **not**
ported rather than ported large. The test is not line count but the isolation
question — *can someone understand what this unit does without reading its
internals, and can its internals change without breaking consumers?* If not,
the boundary is wrong. Smaller units are also what makes agent work reliable:
an agent reasons better about code it can hold in context at once, and its
edits are more accurate in focused files.

⭐ **AMENDED 2026-09-23 — the ceiling's units, its one opt-out, and a split that is
one-way.** Carried from the module-structure convention and the review rubric when
they were archived.

| Unit | Soft ceiling | On exceeding |
|---|---|---|
| source module | 400 lines | split into a package, or justify it in the docstring |
| test module | 600 lines | split along the seam the source split |
| function | 50 lines | almost always a missing helper |
| template file | — | markup only, never logic |

⭐ **A line is a physical line** — what `wc -l` reports — so the floor's arithmetic is
checkable from a shell. ⚠️ **The ceiling binds every authored file under `src/`,
stylesheets and skill documents included**, although the shipped checker counts
Python modules only; a non-Python file near the ceiling is read by a person, because
the instrument cannot see it.

⛔ **The opt-out is one line in the module's first docstring, and nowhere else**:

```text
Size exception: the substitution table is one literal mapping, and splitting it
would hide half the placeholders from the reader of the other half.
```

It begins `Size exception:` at the start of a line, case included, so the checker and
every reader agree on one spelling; it is read from the docstring with `ast`, never
from a comment beside the code, because the exception is recorded where the next
reader of the module meets it; and it is one sentence saying why splitting would be
*worse* — a reason too short to be one is reported as none. ⛔ **It is refused whenever
the honest answer to the isolation question is no**: a justification is not a licence.
An exception left in a module that is now under its ceiling is stale and is removed,
and a ported module is not exempt by inheritance.

⭐ **A one-way seam is a valid split.** A parser must build the model it defines, so
asking the two halves never to import each other would forbid the split or invent a
third module to hold the constructors. What a one-way seam owes instead: its direction
stated in the package contract, and asserted over the source, including against the
forbidden import written in its relative spelling. Mutual independence is the
strongest form, not the required one.

**R12 — Every module ships with its own tests, and the test tree mirrors the
source tree.** A module without tests is not done. A package's tests are split
the same way the package is, so a failing test names a module, not a subsystem.

⭐ **AMENDED 2026-09-23 — the mirror's exact form, and the configuration it needs.**
Carried from the module-structure convention and the review rubric when they were
archived. `src/studyforge/<path>/<stem>.py` is tested at
`tests/studyforge/<path>/test_<stem>.py`, and a dunder drops its underscores so the
name stays readable (`__init__.py` at `test_init.py`, `__main__.py` at
`test_main.py`); the floor's mirror check is the authority on where a test lives.
⭐ **A package's `__init__.py` is its contract (R17), so its mirror is a test that
imports the package's public names** — what stops the surface drifting from the code.

⛔ **Two settings are behaviour, not style.** `--import-mode=importlib` in the test
configuration is required: the mirror puts a `test_init.py` in every package
directory, and under pytest's default import mode those collide on module name and
the suite fails to collect before it runs a test. ⛔ **And an ignore rule is checked
against the paths that must stay tracked** as well as those that must not: a pattern
that swallows a fixture gives a suite that passes on the machine that has the file and
fails on a fresh clone, with nothing in `git status` to say why.

**R13 — Markup, styling and scripts are source files, never code strings.**
Templates in template files, CSS and JS in asset files, loaded and composed by
code. Inherited from CodeSignal, where 80 KB of triple-quoted strings meant
changing a colour required editing Python. Loop bodies and inline wrappers stay
in code — a template file for a closing tag removes no duplication.

⭐ **AMENDED 2026-09-23 — where markup lives, and how a template is used.** Carried
from the module-structure convention and the review rubric when they were archived.
Templates live in `render/templates/`, stylesheets and scripts in `render/assets/`,
loaded and composed by code.

- ⛔ **A template is used exactly, minus one trailing newline** — no reflow, no
  re-indent, no whitespace collapse — because pages are compared byte for byte (R10).
  Markup emitted on one line is authored on one line, however long.
- ⛔ **Substitution fails on an unfilled placeholder**; a placeholder never reaches a
  page as a literal, and a new placeholder arrives with a test of that failure.
- ⭐ **What stays in code is a fragment**: a loop body, an inline wrapper, a one-line
  container. ⛔ A stylesheet, a script, or a whole element with attributes is never a
  fragment. A docstring may show markup; it is not emitted.

**R14 — ⛔ WITHDRAWN 2026-09-12, by user ruling. The number is retained and is
never reused.**

⭐ **The search path is `git grep`, `grep -rn` and `sed -n`.** ⛔ **No document
in this project may name a code-graph or index tool, and no task's context
budget may assume one exists.**

⚠️ **What it used to say, and why it is gone.** R14 required every repository in
the working set to carry a built knowledge index and required an agent to query
it before reading files. ⛔ **The instruction could not be obeyed.** The index
directory was git-ignored, so it existed only in the main checkout and was
**absent from every linked worktree** — which is where the offices work — and
the one copy was stale by the floor's own check, which says a stale index is
worse than an absent one. ⭐ The tool has since been removed from the machine
this project is built on, so the instruction is now false as well as
unfollowable.

⛔ **The id is WITHDRAWN IN PLACE and nothing is renumbered.** R1–R21 are cited
by number across the whole corpus, including frozen records that cannot be
edited (Ruling 106). ⚠️ **Renumbering would silently redirect every historical
`R14` citation to a different rule** — unrecoverable, because the records cannot
be edited to follow. ⭐ A withdrawn rule that explains itself is what every
existing citation must still resolve to.

**R15 — Every step whose result depends on installed tooling runs in a
container.** A build, a test run, a grader verdict, a synthesis job: each is
reproducible because its toolchain is pinned in an image, not inherited from
whoever's machine it ran on. A step that only works on one person's machine is
not done.

⚠️ **This is deliberately not "every process runs in a container".** The
framework's own serving process is standard-library only with no dependencies,
so containerising it buys no reproducibility — and it costs something real. See
§8.3: **the serving process must never receive the Docker socket**, and that
rules out the naive reading of this ruling (§8.3). Execution reaches the toolchain
container from outside it; the web-facing process is never the thing holding
root-equivalent access to the host.

**R16 — The product is a set of skills, not a bespoke pipeline.** The end state
is that someone points a skill at material they care about and gets this format
back — pages, narration, contents, navigation, practices, examples, and their
own progress — and keeps it as their durable personal record. The Java repo is
the proving ground for that, not the destination (§9).

**R17 — Every package states its contract in its own docstring:** what it does,
how you use it, and what it depends on. A reader who has not seen the spec must
be able to use a package correctly from that alone.

⭐ **AMENDED 2026-09-23 — the three questions, and what a surface is.** Carried from the
module-structure convention and the review rubric when they were archived.

- ⭐ **Every package's `__init__.py`, and every module, answers three things in its
  first docstring**: what it does, in one sentence and in this document's vocabulary;
  how you use it — the entry point, not a tour of the internals; and what it depends
  on, with, where it matters, what it deliberately does not. ⛔ A reader who has not
  seen this document answers all three from the docstring alone, so
  `"""Path utilities."""` fails. The habit worth keeping is recording *why* a decision
  was made and what broke before it: that is what prevents the regression.
- ⛔ **`__init__.py` is the contract.** If a consumer has to import a submodule
  directly, the surface is wrong.
- ⭐ **A name a second package needs is exported on the owning package's `__all__`**
  and imported from the package. A name on no surface is not shared, whatever a
  second package's import says; the fix is to export it, never to reach past the
  surface.
- ⭐ **A reader that deliberately lets another package's exception through exports the
  set as a `RAISES` tuple on its surface**, and a caller catches the tuple whole rather
  than retyping a list from prose — callers that retyped it dropped members, and one
  crashed a command whose contract is that nothing raises.

**R18 — Components are separate repositories, pinned by one workspace.** Each
component — the framework, the toolchain image, the narration service, each
corpus — has its own release cadence and is checked out under a single parent
workspace so one directory holds a complete, working system. **The parent's
recorded component commits are the version pin**: they capture exactly which
combination of components a working configuration used, which is what makes R9's
per-contract versioning reproducible *across* repositories rather than only
inside them. ⛔ A component is never vendored, copied or forked into another; it
is pinned.

⚠️ **Amended 2026-09-09: nothing in this project is pushed to any remote, ever.**
That is a standing decision, not a temporary state, and it removes the mechanism
this ruling originally named. **Git submodules have no legal form here** and are
not used:

- an **absolute** local path in `.gitmodules` writes a home directory into a
  tracked file — ⛔ a direct R7 violation;
- a **relative** URL is R7-clean but git resolves it against the parent's own
  remote, which does not exist;
- a **real remote** URL names a commit that was never pushed, so it resolves to
  nothing anywhere, including here.

⭐ **The pin survives; the fetch does not, and the pin was always the valuable
half.** A submodule is exactly two things — a URL and a commit — and only the URL
half depended on pushing. So the parent records each component's verified commit
in a tracked file and **verifies it against the local checkout**, which is
mechanically checkable in the way this project checks everything else.

⚠️ **The honest claim shrinks, and it is stated rather than implied.** This
reproduces a working configuration **on this machine and across time** — which is
what R9's cross-repository versioning actually needs — and **not across
machines**. ⛔ Any document claiming otherwise is wrong. If pushing is ever
adopted, submodules become legal again and the recorded commits are already the
data they would need.

**R19 — The consuming half of a corpus is generated, not hand-authored.** A
source repository's obligation is the archive (R2) and the source-specific
reading behind it. Everything else a working corpus needs — the manifest, the
ignore rules, the compose file, the toolchain selection, the build entry point,
the non-destructive assertion, the reader's own documentation — is produced by a
skill, from the manifest and from the components' published consuming contracts
(§9). ⛔ **Anything a second source would have to retype is a hole in the
skills**, and a hand-edit to a generated artifact is a **finding against the
skill that should have produced it**, never a fix.

This is the argument `SF-28` already won for the build pipeline, applied to the
rest of the seam: an orchestration or a deployment that lives inside one
consumer is a framework with one consumer. ⭐ **The measure is what a second
source costs**, not what the first one looks like when finished.

**R20 — The extraction is one-way. This framework mines its source; a consumer
never sees it.**

⭐ **Affirmatively: `studyforge` may and should use CodeSignal freely.** It is the
extraction source — read it, port from it, measure it, mine it for the rulings
that were expensive to learn. That is the whole point of it, and a framework
task's `Context` naming a path inside it is correct and expected.

⛔ **And a client application never has access to it.** Everything a consumer
needs from CodeSignal is carried **in** `studyforge` — as a ruling, a contract, a
skill, or the integration catalogue (§9) — never as a pointer into CodeSignal's
tree. ⛔ **No task in a consumer repository cites a path inside the extraction
source**, and no skill sends an integrator there to find out how something was
done.

⭐ **This framework is the brain.** Knowledge flows *in* from the extraction
source and *out* to consumers, and never sideways between them.

Three reasons, and the third is the one that compounds:

- **The source is moving.** §8 already warns that every measurement of it is a
  dated snapshot; a consumer reading it directly inherits whatever it looks like
  that week, with no record of what was actually relied on.
- **It does not generalise.** The second consumer's material has nothing to do
  with a course site's payload format, and a plan that sends its integrator to
  read one is teaching them the wrong thing carefully.
- ⭐ **Knowledge must accumulate in one place or it decays once per
  integration.** If each new consumer re-derives from CodeSignal, the framework
  is a library and the expertise lives nowhere. If each one distils what it
  learned back into `studyforge`, the *next* integration starts further along.
  That is what makes this a framework rather than a thing that has been used
  twice.

⚠️ **This constrains the plan, not the prose.** These documents explain *why* a
rule exists by naming what it cost CodeSignal, and that history is exactly what
makes a ruling followable rather than arbitrary. What R20 forbids is a
**dependency**: a consumer's task whose `Context` is a path in the extraction
source, or an acceptance that can only be judged by comparing against it.

**R21 — A contract is located before it is described.** Every document the
framework reads or writes states three things *before* any task builds against
it: **the file it lives in**, **the key that versions it** (R9), and **the one
producer that writes it**.

⛔ **A contract described but not located is a contract two tasks will locate
differently**, and R9's versioning is exactly the thing that cannot repair it:
by the time the disagreement surfaces, one invented location has shipped inside
a version that refuses to migrate. ⭐ A task that meets an unlocated contract
**stops and asks**. It does not choose, and choosing quietly is the specific
failure this rule names.

⚠️ **This was not a hypothetical when it was written.** Three had already
happened in the first week: §7's exercise declaration named six fields and no
document, so the fixture task could not fixture the thing R5 exists to enforce;
`container.json` was described as generated in §6 and hand-authorable in its own
task; and the block vocabulary described `html` without saying what a disclosure
*is*, so two merged documents ruled it in opposite directions. ⭐ None was a
mistake by the task that hit it — each was a **gap the task was obliged to fill
and not equipped to fill**, which is why the rule binds on the spec rather than
on the builder.

**The register of located contracts, and what is still open:**

| Contract | File | Versioned by | Written by |
|---|---|---|---|
| manifest | `corpus.json` | `corpus_api` — ⭐ **`2`, which added `content.not_material`** (ruling 90) | adapter (drafted by reconnaissance, §9) |
| container map | `<address>/container.json` | `container_api` | adapter; `EX-04` amends counts (§6) |
| archive document | `raw/<variant>/unit-NN/<kind>-M.json` | `raw_api` | adapter |
| exercise declaration | the `exercise` key of a `practice-M.json` | that document's `raw_api` | adapter; `EX-04` for generated (§7) |
| served unit | `unit.json` | `api` | `SF-10` |
| table of contents | `toc.json` | TOC schema version | `SF-13` |
| local status | `status.json` | TOC schema version | `SF-14` |
| authored overlay | `<address>/units/unit-NN/content.json` | `content_api` (`SF-09`) | a person |
| discovery cache | `.studyforge/site.json` | `site_api` (Ruling 95) | `SF-04` — ⛔ **the one writer** |
| narration regeneration state | `.studyforge/narration.json` (Ruling 351) | `narration_api` (Ruling 351) | `SF-17` — ⛔ **the one writer** (Ruling 330) |
| progress record | `.studyforge/progress/progress.json` | `progress_api` | `SF-21` — ⛔ **the one writer**; transcribed PO round 67 (`SF-21/1`) |
| personal archive manifest | `personal-archive.json`, a member of the archive file | `personal_archive_api` | `SK-06` — ⛔ **the one writer**; transcribed PO round 72 (`SK-06/5`) |
| coverage report | ⛔ **open** | n/a — not read back | whatever produced the gap |
| component consuming contract | `consuming.json` | `consuming_api` + `provides` | each component (`TC-05`, E13) |
| **workspace pin file** | `workspace.json` | `workspace_api` | `FND-05a`; a row per component |

⛔ **THE ROW THAT READ *narration manifest … `NS-02` / `SF-17`* WAS TWO CONTRACTS
WEARING ONE NAME, and the `/` is what hid it** — ⭐ **located CTO round 67,
Ruling 330, which is R21's own *one producer* clause applied to its own register.**

- ⛔ **`NS-02`'s batch manifest is a RESPONSE BODY and takes no row here.** ⚠️ **This
  table's columns are `File` and `Written by`, and the clause below is *`R9` governs
  what is written*: a wire shape is written to nobody's disk.** ⭐ **It is the
  service's PROMISE, and the promise register already exists and is two rows above —
  `consuming.json`, versioned by `consuming_api` + `provides`.** ⛔ **Minting a tenth
  `*_api` for it would put a framework version key on a shape the framework does not
  write, making it a second authority on a component's promise — the failure §8.2
  removes when it rules that the service never writes into a corpus.**
- ⭐ **`SF-17`'s half IS a file row and is now CLOSED above — located by Ruling 351 and
  filled in by `SF-17` itself, the task that builds it.** ⚠️ **It is the state that makes
  *"re-running with no content change writes nothing and requests nothing"* (E04,
  `SF-17`'s Acceptance) decidable, so the framework reads it back and R9 binds it.**
  ⛔ **It was owed before step 3.4 opens, not before 3.2, and the two cells were
  transcribed here in the commit that minted the key** — ⭐ **`narration_api` is
  registered in `version.CONTRACT_FIELDS` in that same commit, per that tuple's own
  convention, and it is read through `check` rather than `is_supported`: unlike the
  discovery cache two rows above, this record is rebuildable only by re-synthesising
  every clip in the corpus, so R9's refusal is spent by stopping.**

⚠️ **AND THE ORDERING THE SPLIT EXPOSED, which is the part a location alone would have
missed:** ⛔ **`narrate-service`'s `consuming.json` is written by TWO tasks — E13 assigns it
to `NS-03` (profiles) and `NS-04` (voices), *"both must contribute their half"* — so the file
names its own holes in `not_yet_declared` rather than being absent.** ⭐ **`NS-03` is in
`NS-02`'s own step and `NS-04` is the step after** — ⛔ **so `NS-02` could have been built
before the file that versions its output existed.** ⚠️ **The edge was owed in `E13` before
step 3.2 dispatched `NS-02`** (Ruling 330(c)).

⛔ **CORRECTED, CTO round 69 — this paragraph asserted the POPULATION of another office's
file and both halves went false as the tasks landed** (Ruling 335, and `NS-03/2` + `NS-02/3`
reporting it two waves running). ⭐ **What it said, kept so the correction is legible:**
*"`narrate-service` ships no `consuming.json` today"* and *"`NS-03` is in `NS-02`'s OWN STEP
with no `Depends on` edge between them"*. ⚠️ **The first was false from `NS-03`'s landing and
the second from round 53's edge; the repaired form POINTS at `not_yet_declared`, which
resolves at read time, instead of claiming what the component ships.**

⭐ **`workspace_api` is the eighth versioned contract and the first that lives
outside `src/`** — which is why the register and the framework's own constant are
not the same list. ⛔ **Ruled: this table is the register; `CONTRACT_FIELDS` is
the framework's *subset* of it.** ⭐ **So a key entering `CONTRACT_FIELDS` owes its row here in the commit that mints it; `SF-21/1` and `SK-06/5` are the two that did not, and the register transcribed both.** ⚠️ A contract the framework does not read is
still a contract — the pin file is read by `tools/`, and `R9` governs what is
*written*, not what `src/` happens to import.

⭐ **`consuming.json` carries two versions, and conflating them is the defect it
exists to prevent** (ruled 2026-09-09, round 4). The pin file (R18) records
**which build** a component was at; `provides` records **which promise** it is
making. ⛔ They change at different rates and neither substitutes for the other:
a component rebuilds constantly without changing its promise, and can change its
promise without a new build. `consuming_api` versions the file's own schema, and
a consumer records the `provides` it was built against; a mismatch is refused,
never migrated (R9). ⚠️ **Everything else about the file belongs to the component
that ships it** — E12 for the toolchain, E13 for narration — because it describes
a runtime nobody has built yet, and designing it now would be designing against
zero sources. ⭐ What is ruled here is only what stops **two components inventing
two shapes**, which is the failure this seam is actually exposed to: it is the
one seam neither side can inspect from its own repository.

⛔ **Every row this register marks `open` is an instance waiting to happen**, and
each is owed by the task named beside it *before* that task builds. ⚠️ **The
COUNT is not typed here and its removal is `PO-38/2`** — ⛔ **this sentence said
*"Four"* one line below a table of two, and a third number stood on the board;
three documents held three counts of one set and two of them were on the same
page.** ⭐ **The open set is whatever the table above marks `open`, read at read
time — a document that GOVERNS a register may not carry a typed measurement of
it** (Ruling 181), ⛔ **and the fix is to REMOVE the count, not to correct it**
(Ruling 150's form). ⚠️ The overlay's row is the
sharpest: it is the one document a **person** edits, which makes it the most
likely to drift, and R9 does not list it. Either R9 gains it or R9 says in words
why a hand-edited document needs no version — but not silence.

⭐ **AMENDED 2026-09-23 — when a file takes a row.** Carried from the review rubric when
it was archived, because the question had been derived from scratch twice. ⭐ **A file
takes a row here when a party other than the one that writes it reads it back** —
another component, a corpus repository, or the framework reading what another
producer wrote. ⛔ It does not take one merely for being a file, for being written and
read back by its own writer, or for carrying a version key: a version key shows that
its author expected the shape to move, which is why the question must be asked, and
is not what answers it. ⭐ **So a task that mints a persisted format says who reads it
back.** Where every reader is inside the writing component, no row is minted and the
task says so; the row is owed the moment a party outside that component opens the
file, or a second writer appears in the same store. ⚠️ **And a content-addressed
filename does not discharge a contract whose subject is the conditions the content was
produced under**: a clip named by the digest of its words answers *has the wording
changed*, but a voice change or a service promise bump leaves every filename
byte-identical while every clip is stale — which is why the narration regeneration
state is a located, versioned file rather than an inference from names.

---

## 3. Architecture

### 3.1 The workspace

Five repositories, each with its own remote, composed as submodules of one
parent so a single checkout is a complete system (R18):

```
learning-workspace/               the parent — thin: docs, compose, scripts
  studyforge/                     submodule — the framework
  code-server-toolchain/          submodule — the IDE image (§8.1)
  narrate-service/                submodule — synthesis (§8.2)
  corpora/
    java-senior/                  submodule — consumer 1, built in v1
    codesignal/                   submodule — added at v2 convergence
```

The parent holds almost no code. What it holds is **the combination**: which
commit of each component works with which, plus the compose files and scripts
that run them together. That pin is the artifact — a component is pinned,
never vendored, copied or forked into another (R18).

Two consequences worth stating up front, because both are first-run failures:
a plain clone yields empty submodule directories and must recurse; and a change
to a component is **two commits** — one in the component, one in the parent
recording the new pin. Neither is a defect; both need documenting (FND-05).

### 3.2 Inside the framework

Every unit below is a **package** of focused modules, not a file (R11). The
tree names responsibilities; the modules inside each are the owning task's to
draw, subject to the size ceiling.

```
studyforge/
  src/studyforge/
    version.py   the R9 gate: one implementation of "is this a version I speak"
    address/     logical N-segment address, keys, slugs, identifiers
    corpus/      manifest · container map · placement profiles · discovery
    archive/     the archive document · block vocabulary · Markdown reader
                 · the personal-data gate
    unit/        the served unit document · authored overlay · section keys
    contents/    table of contents and local status, as data
    render/      page renderer · root index · templates/ · assets/
    narrate/     speakable contract · synthesis
    serve/       app · content, state, assets and run routes · security
                 · caching.  A package precisely because it replaces a
                 2,743-line file (R11)
    execute/     the command runner — the only process-spawning package
    progress/    the reader's local record
    exercise/    workspace and trust contract
    validate/    the CLI that defines "a valid archive"
    cli/         build, serve, plan, reconcile — the framework's entry points
    skills/      the authoring and conversion skills (§9)
  tests/         mirrors src/ package for package (R12)
  docker/        dev, test and serve images (R15)

Claude-senior-java-engineer/      consumer 1 — built in v1
  ingest/         curriculum · lessons · sources · emit · audit
  exercise/       body-blanking · the two gates
  practice/       generated exercise sources (additive Maven module)
  docker/ docker-compose.yml
  index.html  .studyforge/{assets,archive,site.json}
  00-base/ 01-java-basics/ ... 45-java-persistence/   UNCHANGED

code-server-toolchain/            shared, its own repo (§8.1)
  Dockerfile entrypoint.sh
  lockdown/         the practice-focus workbench extension
  seed/             default settings and keybindings
  prime/            build-time cache-warming contract

CodeSignal/                       untouched in v1; converges in v2
```

**Dependency direction is one-way.** `studyforge` never imports a consumer. A
consumer never imports `studyforge` internals — it writes an archive and
invokes the CLI.

⭐ **AMENDED 2026-09-23 — standard library only, declared and imported.** Carried from
the module-structure convention and the review rubric when they were archived.
⛔ **Framework source imports nothing outside the standard library and itself, and
`pyproject.toml` declares no runtime dependency** — the reader's host needs Python and
a Docker CLI and nothing else (§8.3). ⚠️ The declaration and the code can disagree, so
both are checked. ⭐ Test and lint dependencies are fine and are **declared**, as
optional groups, never assumed present: an undeclared test dependency is a suite that
passes for its author and errors for everyone else. ⛔ **Vendored third-party assets —
the highlighter, the media player, the faces — are committed with their licence beside
them and are never edited**; a change is a re-vendor.

---

## 4. The address model

CodeSignal's `CourseRef.key` is already a single joined string precisely so
its halves cannot be swapped. v1 widens it from *exactly two* segments to
*exactly `len(levels)`*.

```json
// corpus.json — what makes a directory a source
{ "corpus_api": 2,
  "source": "java-senior",
  "title": "Senior Java Engineer",
  "levels": ["section", "module"],
  "variants": ["java"],
  "exercises": true,
  "placement": "sibling",
  "content": {
    "include": ["*/README_*.md"],
    "exclude": [],
    "not_material": [
      { "glob": "README.md",
        "why": "the repository's own navigation; the site carries its own contents" } ] },
  "permitted_edits": [
    { "path": "pom.xml",
      "kind": "insert-line",
      "anchor": "<modules>",
      "content": "  <module>practice</module>",
      "why": "Maven compiles only what sits on a source root (§7)" } ] }
```

### The complete key list — ⛔ **the example above is an instance, not the contract**

⚠️ **The example omits optional keys and that is correct.** ⭐ **A canonical
example is a *realistic* manifest, and a realistic manifest omits the optional
keys it does not need** — so the example is not where you learn what a manifest
*may* carry. This list is. ⛔ **Without it `media` was unteachable from this
document**: the contract owned a key the spec never named, and a reader looking
for the vocabulary found only one corpus's choices.

| Key | | Notes |
|---|---|---|
| `corpus_api` | **required** | R9's version key. An unknown value is refused, never migrated. ⭐ **`2` added `content.not_material`** (ruling 90), ⭐ **`3` added `media.max_files`** (`W207`) and ⭐ **`4` added `runtimes`** (`W350`), ⭐ **`5` added `narration`** (`W460`, amended 2026-09-23) and ⭐ **`6` added `onboarding_doc`** (`W461`); this build reads `1` to `6` |
| `source` | **required** | ⛔ **A corpus id, not a fetch URL** (ruling 51) |
| `title` | **required** | |
| `levels` | **required** | Names the *container* levels and fixes the depth |
| `variants` | **required** | ⛔ Filing and presentation only — never *runnable* |
| `curriculum` | *optional* | Where the curriculum is recorded (`record`), the address each of its groups is filed at (`containers`), and per group an optional filename `prefix` that is a declared cross-check and never files a unit (`W340`) |
| `exercises` | **required** | §7's gate onto the execution track |
| `runtimes` | *optional* | Names, never versions, from a closed vocabulary. ⛔ **Absent means none: no runner, complete at the reading floor** (§7, C5) |
| `narration` | *optional* | Whether a build and a serve voice the corpus (`W460`). ⭐ **Absent means voiced whenever clips are recorded**; ⛔ **`false` is the reading floor exactly, complete and never short** (C5) |
| `onboarding_doc` | *optional* | Where onboarding writes its reader document (`W461`): a corpus-relative `.md` path, or `false` for none. ⭐ **Absent means `ONBOARDING.md` at the root**; ⛔ a fixed name was a branch nobody could move (R1, R19) |
| `placement` | **required** | |
| `content` | **required** | `include` is plain globs; every `exclude` and every `not_material` entry carries its `why` |
| `media` | *optional* | Defaulted. ⛔ **A corpus with no media declares nothing** |
| `permitted_edits` | *optional* | Defaults to `[]`. ⭐ ISO's is structurally empty and that is a pass |

⛔ **The contract is `MANIFEST_KEYS` and `REQUIRED_KEYS` in
`corpus/manifest/document.py`; this table is derived from them and the derivation
**must be** asserted rather than maintained by hand.**

> ⛔ **CTO, 2026-09-10 — the assertion does NOT exist yet, and this paragraph
> said it did.** ⚠️ **Measured: no test anywhere reads this document.**
> `tests/studyforge/corpus/manifest/test_init.py` names `MANIFEST_KEYS` only
> inside an `__all__` surface check. ⭐ **The table's *content* is correct** — all
> ten keys match `MANIFEST_KEYS` and all eight *required* match `REQUIRED_KEYS`,
> verified key by key. ⛔ **It is the claim of coverage that was false, and that
> is worse than an unasserted table: the next reader trusts the sentence and does
> not look.** ⚠️ **Ruling 48's shape, landed inside Ruling 30's landing.**
> ⭐ **Owed as a task on `FND-08`'s seam** — it is a document walk with a
> code-side comparison, which is exactly what that task builds. **PO to place and
> number it.**

⚠️ **And the assertion is deliberately
*two* one-way checks, never an equality** (⭐ **ruling 30, which reversed ruling
28**):

- **subset** — every key this table names exists in `MANIFEST_KEYS`, so the spec
  cannot teach a key the code does not have;
- **coverage** — every key in `MANIFEST_KEYS` appears in this table, so the code
  cannot own a key the spec never names. ⭐ **That is the half that closes
  `media`.**

⛔ **Equality was ruling 28's remedy and it was wrong in a way worth recording,
because it would have been *enforced*.** Equality can only be satisfied by making
the **example** exhaustive — and `SK-07` **generates** manifests from it, so an
exhaustive example propagates `media` into every corpus that has none, and R9
freezes it there at first declaration. ⭐ **The scope this was argued over is a
canonical example whose consumer is a generator** (ruling 52); a hand-written
example with no generator downstream would not have carried the same cost.

`content` is **C2's countermeasure, and it is a schema field because C2 is a
schema problem.** ISO ships both per-unit files *and* whole-series aggregates
that are concatenations of them, so a `src/*.md` glob ingests every unit twice
and nothing complains. Nothing in the manifest could say otherwise.

```json
"content": {
  "include": ["src/*.md"],
  "exclude": [
    { "path": "src/ISO.md",
      "why": "whole-series aggregate: a concatenation of 1.md…16.md (C2)" } ],
  "not_material": [
    { "glob": "docs/studyforge/*",
      "why": "this integration's own working notes about the corpus, not the corpus" },
    { "glob": "LICENSE",
      "why": "the repository's licence; it teaches nothing and is not withheld from anyone" } ] }
```

⭐ **The asymmetry is deliberate: an inclusion needs no justification; an
exclusion does.** An excluded file is material being withheld from the reader,
and a withholding nobody has to explain is one nobody audits — the same argument
`permitted_edits` already makes about an edit. So `include` is plain globs and
every `exclude` entry carries its `why`.

### `runtimes` — what a corpus's material needs to run (`W350`)

⭐ **The shape is `TC-00`'s proposal as round 112 accepted it.** An optional
list of names from a **closed** vocabulary — `gradle`, `java`, `kotlin`,
`maven`, `node`, `python`, `shell`, `sqlite` — which agrees name for name with
what `code-server-toolchain`'s pin file pins (§8.1). ⛔ **Names only, never
versions**: the corpus says *which*, the pin file says *which version*, and a
version here would be a second place one is chosen.

- ⭐ **Order carries no meaning**; `Manifest.runtimes` holds the set sorted, so
  two equal declarations are one value (R10). A repeated name is refused.
- ⛔ **`maven`, `gradle` and `kotlin` are refused by name without `java`** in the
  same list — nothing is inferred, the rule `corpus_api` follows.
- ⛔ **Refused beside `exercises: false`**: it would declare a runner for a
  corpus with nothing runnable (§7).
- ⭐ **Absent means none, and none is complete.** The framework neither builds,
  probes nor starts a container for such a corpus; `exercises: true` without
  `runtimes` is an ungraded corpus's honest shape.
- ⛔ **It is `corpus_api: 4`'s key, and a top-level one** — `KEY_VERSIONS` keys
  it under no block (`TC-00/2`), so under `1`–`3` it is refused naming both
  numbers rather than parsed. ⭐ **The vocabulary is spelled once**, in
  `corpus/manifest/runtimes.py` (`TC-00/3`).

### `narration` — whether a corpus is voiced (`W460`, AMENDED 2026-09-23, user ruling)

⛔ **USER RULING, 2026-09-23:** *"I need some changes regarding the narrition.
First of all it should be optional and while serving or even while caputring the
matterial skills should ask if user is interested in the narrition or not.
Somebody might wants to just cover the course wihtout voices as mentioned the
voice might be cgenerated but still not serving them would be an option"*.

- ⭐ **A top-level bool, `corpus_api: 5`'s key** — `KEY_VERSIONS` keys it under no
  block, so under `1`–`4` it is refused naming both numbers. The onboarding
  skill ASKS the author and writes the answer; a draft that carried none writes
  no key and keeps its version.
- ⭐ **Absent means voiced**: every corpus before the key keeps the three states
  of `W202` answer 4 — no record, a record whose clips play, a promise the disk
  did not keep.
- ⛔ **`false` is the FIRST of those states exactly, whatever the record says**:
  a build reads no record, renders every page with no player and no gap notice,
  and copies no clip — byte for byte the build of a corpus nobody narrated.
  ⛔ **Nothing is deleted, moved or rewritten** (R3): the record and the clips
  stay where `narrate` put them, so voicing the corpus again plays them with no
  re-synthesis.
- ⭐ **`studyforge build` and `studyforge serve` take `--narration` /
  `--no-narration`**, which override the declaration for that run, and the
  build-and-serve skill ASKS for it. ⛔ **Narration is in a page's bytes** (R8:
  the built page is the product), so `serve` never edits a page on the way out:
  with narration off it refuses a site built with narration, naming each page
  and the build that fixes it, and it refuses every clip file under the root it
  serves by path.
- ⛔ **Off is not degraded**: no page, report or `validate` finding calls it
  short, and practices, quizzes, progress and contents are unchanged.

### ⛔ `content` has **three** states, and the third is `not_material` (ruling 90)

⛔ **Two states were not enough, because a real repository is mostly a third.**
Measured against one, 2026-09-10: of 141 files, **38 included, 3 excluded, 100
unclassified — and only 3 of that hundred were material withheld from anybody.**
The rest were a licence, ignore files, an IDE workspace, a graph cache. Filing
those under `exclude` makes every `why` a small lie and produces an audit nobody
reads.

⭐ **The three states are about whether a file's prose is read into the archive**,
never about materiality in the abstract:

- `include` — **read in.**
- `exclude` — **prose that *would* be read, deliberately not read**, per file,
  with its `why`. ⭐ *Withheld* is the honest word here because it is true here.
- `not_material` — ⛔ **not prose to read at all**: the repository's own
  scaffolding, content *about* the material rather than the material.

⭐ **A source `README.md` is `not_material`, and it is not a special case** — it
is the corpus's own navigation, and navigation is scaffolding. ⚠️ **The reader
loses nothing**: the generated site carries its own contents from the manifest's
container maps, so every address, title and ordinal the README records is already
declared. ⛔ **`X1` is not weakened; its domain is now stated** — *an inclusion
needs no justification; **every declaration that the framework will not read a
file** needs one.*

⚠️ **`not_material` takes globs where `exclude` takes one named path**, and the
two audits differ because the harms differ. A new member of an exclusion's set is
a new withholding and needs its own reason; a new member of a `not_material`
glob's set is not a harm **unless it is actually material** — which is caught per
file, against a real tree, by the rule below. ⛔ **The category also cannot be
enumerated**: writing the finding that produced this field took the count from
100 to 101, because the new entry was the file containing it.

⛔ **A file matched by BOTH `include` and `not_material` is a finding of its own**
(`contested`), and it exits 1. ⭐ **Never a precedence** — one order would drop
material the reader was promised and the other would read the scaffolding aloud.
⚠️ **This is what stops the third state becoming a drain.**

> ⛔ **Rule 1a — a `not_material` entry is either an EXACT PATH, or a glob whose
> wildcard lies inside a directory prefix that is itself entirely not-material.**
> ⛔ **A pattern whose correctness depends on which files happen NOT to exist is
> refused, however exactly it matches today.**

⭐ **The check is one sentence and it is mechanical: reject an entry containing a
wildcard whose fixed prefix is not a directory.** ⚠️ **It is not redundant with
`contested`**, which catches a loose glob only when the swept file is *also* in
`include`; the hole is the file that does not exist yet, classified by a `why`
that was never about it — ⛔ **and the `unclassified` catch that would have
surfaced it goes quiet precisely because the file is now classified.** ⭐ Ruling
90's own examples pass unchanged: `docs/studyforge/*` is a wildcard under a
directory, `LICENSE` and `.gitignore` are exact paths; `[CLR]*` is refused,
because it covers three root files only by the accident of which fourth file
exists, and a `why` cannot be true of a `CHANGELOG.md` nobody has written yet.
⚠️ **Five honest globs, not three clever ones** — and `SK-07` must **generate**
entries that satisfy this rule.

⛔ **Silence is the failure C2 describes, so silence is what this removes.** A
file under the source root that matches none of the three is **unclassified**,
and `studyforge validate` names it and exits 1 (R6). A file that matches
`include` and is then not ingested is also a failure. ⚠️ It follows that a corpus
cannot grow a file without someone deciding what it is — which is the point,
because the alternative is a second aggregate appearing and being read as
thirty-eight more units.

⭐ **The reconnaissance skill (§9) drafts this**, and detecting the overlap is
exactly what C2 asks of it: two files whose digests say one contains the other is
a finding it reports, not something left to be noticed after ingest.

`levels` names the **container** levels and fixes the depth. A unit is an
ordinal inside the deepest container. `variants` replaces CodeSignal's closed
`LANGUAGES` tuple, removing the framework's last dependency on
`tools/catalog/`.

⚠️ **`variants` is a filing and presentation key, and nothing more.** It says
how the archive is partitioned and what a variant selector offers the reader.
⛔ It never implies that anything is buildable, runnable or gradable — that is
declared per exercise (§7) — and it is **not** a code fence's language, which is
a block's own attribute from the archive. CodeSignal blocked eight SQL courses
for exactly this reason: one list answered both *"can this be filed here?"* and
*"can we generate a test for it?"*, so a language with no grader could not be
filed at all. Three questions, three answers, none of them derived from another.

⛔ **A single-variant prose corpus declares `variants: ["prose"]`: the word is the
framework's, not each corpus's** (`Q9`, ruled at PO round 107; landed by `W347`).
⚠️ Every corpus must name at least one variant, and a word each corpus invents
for the same case is a different label in the one variant selector. ⭐ The
reconnaissance skill proposes it — `SINGLE_VARIANT` in
`skills/reconnaissance/proposal.py` — and a person still confirms it.

`permitted_edits` is R3's declaration: the complete, enumerated set of existing
files this corpus may have added to, each with its insertion and its reason. An
empty list is the normal case, and it is the one a purely additive source should
be able to keep.

| Source | `levels` | example address |
|---|---|---|
| SPARQL | `["course"]` | `sparql-tutorial` + unit 07 |
| Java-senior | `["section","module"]` | `concurrency/23-executors` + unit 02 |
| CodeSignal | `["path","course"]` | `kotlin-programming-for-beginners/getting-started-with-kotlin` + unit 03 |
| ISO-8583 | `["group"]` | `iso-fundamentals` + unit 02 |

Depth is uniform **within** a source. A ragged source is normalised by its
adapter. This is a deliberate YAGNI: a free node tree would turn every flat
contract downstream — progress keys, hrefs, editor task files, the source-tree
mirror — into a tree walk, for flexibility no known source needs. Revisited in
v2 only if a real source demands it.

`levels` also supplies the **display labels** the breadcrumb and index use, so
the Java site says "Section › Module › Lesson" while CodeSignal says
"Path › Course › Unit", from data.

---

## 5. Placement and discovery

The single largest departure from CodeSignal, which prescribes one tree.

**Placement is a policy**, declared per source, mapping an address to physical
locations. Two profiles ship in v1:

- `tree` — CodeSignal's existing shape. All output under one generated root.
- `sibling` — output lands in a declared `study/` directory **beside the source
  file it was generated from**.

The Java repo uses `sibling`, because the material already has a layout the
reader knows and R3 forbids restructuring it:

```
Claude-senior-java-engineer/
  index.html                                     generated root index
  .studyforge/assets/                            shared css, js, prism, plyr
  archive/<address>/raw/java/unit-NN/lesson-1.json  the archive, beside corpus.json (§6)
  .studyforge/site.json                          discovery cache
  16-streams-api/
    README.md                                    UNTOUCHED
    README_4.4.1.md                              UNTOUCHED
    study/
      streams-api.section.html                   module page
      basics.16-streams-api.4.4.1-introduction-to-the-streams-api.unit.html
      audio/basics.16-streams-api.4.4.1-introduction-to-the-streams-api/*.mp3
      practice/basics.16-streams-api.4.4.1-introduction-to-the-streams-api/
```

⛔ **AMENDED PO round 76 — the archive root is `archive/`, beside `corpus.json`, under
every profile** (`W241`, `INT-06/6`). ⚠️ **This example once read `.studyforge/archive/`:
`plan` printed that root and nothing read it.** ⭐ **§6's `<archive-root>` is this directory.**

⛔ **AMENDED (`W323`, a user requirement) — under `sibling` every generated
artifact lands in a `study/` directory beside its source file, never loose in
that directory.** ⚠️ **This example once put the page and a per-unit
`<stem>.audio/` directly beside the `README`s**, which measured on the first
corpus as 38 sources, 38 pages and 38 media directories interleaved in one
listing, and put a page and a media directory at the **repository root** for
every source file that sat there. ⭐ **The only generated file at the corpus
root is `index.html`**; the media sits one directory per kind under `study/`,
with the unit's stem below that, so a source directory gains exactly one name.

**Every generated page carries a real name, never `index.html`.** Names come
from the unit's own numbering and title, so they are human-readable in a
directory listing and unambiguous to a scanner.

⛔ **AMENDED (`W254`): under `sibling`, a unit's page and media names begin with
its container's address, dot-joined** (`basics.16-streams-api.` above, for a
unit at `basics/16-streams-api`). ⚠️ **Numbering and title alone were not
unique:** two containers whose series mirror each other in one directory gave
two units one name. A slug carries no `.` and depth is uniform, so two
containers never share a name. What one container still repeats (one label,
one title) is refused by name, by `validate`, `plan` and a build.

**Discovery replaces path inference.** At startup the server scans the source
root for `*.unit.html` and `*.section.html`, reads each file's embedded
identity block, and assembles the site from what it finds. `site.json` is a
cache of that scan, never the authority. Consequences, all intended:

- The framework does not care where artifacts are; a source may place them
  anywhere the reader finds natural.
- A moved or renamed artifact still identifies itself correctly.
- A stale cache is detectable rather than silently wrong.
- Two sources with different placement profiles are served by one server.

Assets and audio resolve **relative to the page that references them**, so a
unit page opened directly from `file://` works with no server and no rewriting
(R8).

⛔ **Delivery is orthogonal to placement, and an href never encodes how a file
arrived.** A generated artifact is addressed relative to the page that
references it, and that address is the same whether the file was generated
locally, committed, or restored from somewhere else. Any future delivery
mechanism moves the same bytes to the same paths. ⚠️ CodeSignal proved this in
reverse, expensively: when 11.7 GiB of media left git for release assets, **the
layout on disk did not move and every page still addressed a clip as plain
`audio/<clip>.mp3`** — which is the only reason that change was a script rather
than a re-render of 1,290 pages.

**Generated media is committed by default.** ⭐ *Regenerable is not the same as
available*: a clone that carries its own audio speaks with no synthesis service,
no GPU and no network, and that is what R8 is for. A corpus that ignores its
media asks every reader to stand up a service before they can hear anything.

⭐ **A build's output is committed too: its pages, the root index and the asset bundle**
(PO round 78, `W242/1`). The same argument holds: a clone that ignores its pages has no reading
floor. ⛔ **So the only generated ignore rules ABOUT THE CORPUS are the media policy's, written
inside the generated directory they are about and never in the root ignore file (R3).**
⚠️ This dates Ruling 91's first half, which declared `sibling` output in `.gitignore`.

⛔ **`site.json` was in that list and is not any more** (`W425`, PO round 132; measured
2026-09-20 on the first corpus). ⚠️ **The argument does not reach it, and the difference is
structural rather than a preference:** every other artifact in the list is READ by somebody — a
reader opens the pages and the index, a page loads the bundle — and **nothing reads the cache**.
`corpus.discovery.assemble` scans on every call and returns the scan; no branch hands back a
cached `Site`. ⛔ So a clone carrying the cache gains nothing, while every reader who serves the
corpus gets a modified file **for doing the one thing the tool is for**: `tools.workspace verify`
refused the workspace within a minute of a serve, on `.studyforge/site.json` alone. ⭐ **So the
cache is ignored where it sits**, by the same mechanism the progress store uses one directory
over — an ignore file INSIDE the generated directory, never the repository's root one — and the
rule is written by the framework rather than by a hand-added line per corpus (R19).

⛔ **The default has a ceiling, and crossing it is a decision, not an accident.**
Narration is the largest thing this framework generates, and a corpus can
outgrow what a git remote will take: CodeSignal reached **11.42 GiB of pack
against a ~5 GB soft limit, with one file at 150.9 MiB against a hard 100 MiB
per-file block** — and found out when the push became *impossible*, after the
history already held the blob. So the policy is manifest data, the footprint is
**measured**, and a corpus that crosses its limits **stops and says so**, naming
the number and the limit. ⛔ It never silently switches to ignoring media, which
would produce clones that are silent with no error, and it never silently keeps
committing.

⚠️ **Extraction — packing media out of git and restoring it — is deliberately
not built in v1.** No source in scope needs it, and building a delivery
mechanism for a problem nobody has is how a framework acquires machinery it
cannot justify. What v1 builds is the **awareness**: the policy, the
measurement, and the honest refusal. Because delivery is orthogonal to
placement, the mechanism plugs in later behind the same decision without
touching a single page.

### The placement dry-run

A consumer cannot write its ignore rules, declare its `permitted_edits` (R3) or
review an onboarding without knowing every path the framework will create. So
placement is **askable before it is exercised**:

```
studyforge plan <repo>
```

emits, from the manifest alone and before anything is generated, the complete
set of paths that will be created, the set of existing files that will be
edited, and the declared reason for each. It is what the onboarding skill
renders ignore rules from, what the non-destructive check asserts against, and
what lets a person read what is about to happen to their repository before it
happens. The placement policy already computes all of it; nothing exposed it.

---

## 6. The ingestion contract

An adapter writes exactly this, and nothing else is asked of it (R2):

```
corpus.json                                   the manifest (§4)
<archive-root>/<address>/
    container.json
    raw/<variant>/unit-NN/lesson-M.json
    raw/<variant>/unit-NN/practice-M.json     optional
```

⛔ **A file under the archive root that is not a member of this layout is refused by name (`archive-stray`), never skipped** (`W248`, amended PO round 79).

⛔ **A list item is a string, or an array of its parts in reading order** (`W258`, amended from `INT-09/6`). The block vocabulary is `archive/blocks.py`'s eleven rows, and a `list` block keeps its three fields; what changed is what one of its `items` may be. ⭐ An item holding no nested list is a string, byte-identical to every list written before. An item holding one is an array of text strings and whole `list` blocks, in the order the author wrote them, and a nested `list`'s items follow the same rule. ⚠️ A nested list is never folded into its parent's text, and it is not a block in reading order: `counts` does not count it. ⭐ Not a `raw_api` change, because every document without a nested list reads exactly as it did.

⛔ **An ordered list keeps the number it starts at** (`W264`, amended from `W258/3`). A `list` block may carry a fourth key, `start`, after its three fields: the first item's number, an integer, written only when the list is ordered and that number is not `1`. ⭐ The page opens the list at it and the narration counts from it, at the top level and nested. ⭐ A list that starts at one carries no `start` and is byte-identical to every list written before, so is its document's `content_sha256`. ⚠️ Not a `raw_api` change for that reason, and the key a block may carry beyond its fields is `archive/blocks.py`'s `optional`.

⛔ **Raw HTML IS in the vocabulary: it is the `html` block, the Markdown reader emits it for a run of block-level markup, and the page renders it VERBATIM — the one block type that bypasses escaping, by declaration and never by what its text looks like** (`Q2`, `W347`). ⭐ It stays: nothing is removed and `raw_api` does not change. ⚠️ The question was ruled at PO round 107 on the premise that raw HTML was *not* in the shipped vocabulary; that premise was measured wrong, and the register corrected it in its round 113. A tag-shaped line the reader keeps as a `para` is still escaped (`render/page/blocks/verbatim.py`).

```json
// container.json — generalises CodeSignal's course-map.json
{ "container_api": 1,
  "address": ["concurrency", "23-executors"],
  "titles":  ["Concurrency", "Executors and Thread Pools"],
  "variant": "java",
  "ingested": "2026-09-08",
  "origin": "23-executors/README.md",
  "note": "…",
  "units": [ { "n": 1, "title": "Thread pools and the Executor framework",
               "practices": 1, "origin": "23-executors/README_5.1.md",
               "note": "…" } ] }
```

⭐ **`origin` is called `origin` and not `source`** because `source` is already
the corpus's own identifier in the manifest, and two fields one word apart
meaning different things is a defect waiting for a tired reader.

One variant per container, preserving CodeSignal's invariant that removed the
"the map promised Java and the archive has none" failure class entirely.

**Who writes it — one answer.** An earlier draft had three tasks claiming it.
The ruling: an adapter **generates** `container.json` on ingest (JS-05), and
`EX-04` **updates only the declared practice counts** within it. Anything a
human adds — a note, a corrected title — lives in fields the generator round-
trips rather than overwrites, and a generator that would discard one **stops**
(R6). It is not hand-authored-only; it is generator-owned with preserved
judgement.

⚠️ **`ingested` is a clock, and it is exempt from R10.** A date stamped at
ingest time makes a document differ on every re-run, which would otherwise
break byte-for-byte reproducibility. It earns the exemption the same way §8.2's
audio does — it is genuinely useful (it answers "how stale is this capture?")
and it is excluded from `content_sha256`, so it cannot make unchanged content
look edited. Reproducibility claims elsewhere are stated as *"identical bytes
apart from `ingested`"*, never silently.

**Attachments** (C4). A unit may reference files that are neither prose nor
inline media — a dataset a lesson loads, a notebook, a sample document. They
are archived alongside the unit and placed by the placement policy, and the
page links them for download rather than rendering them. Distinct from media,
which the page displays.

**Provenance.** A unit may record where it came from. `origin` is written by the
adapter, carried into the unit document **verbatim**, and rendered by the page
and the index. It is optional, because a corpus may be its owner's own material;
it is **not optional chrome** where it exists, because material that came from
somebody else is credited on the page that shows it.

⛔ **An address is recorded, never derived.** Composing an address from a title
is the tempting shortcut and it is measured wrong: on CodeSignal's catalog,
**157 of 1,290 units (12.2%) are served at a slug their title does not
produce**, so a derivation sends one link in eight to a page that is not there —
and a link that fails is worse than no link, because it asserts an address the
reader then cannot find. Where two records name an address for the same unit — a
container map and an archive document — a disagreement is a **refusal** (R6),
never a preference: one would be linked from the page and the other from the
index, and the reader would be sent to two different places with nothing
failing.

⛔ **A title is not an address: where the curriculum index and a unit's own file
disagree on the unit's TITLE, the curriculum index's title wins** (`Q3`, a user
ruling recorded at PO round 107; landed by `W347`). ⚠️ So the refusal above does not
extend to titles, and the precedence is stated here rather than left as a
constant inside one adapter's code.

⭐ **For a repository-shaped source this is a feature, not a formality.** R3
guarantees the original file is never touched, so an `origin` pointing at it is
a permanent, working link from every generated page back into the reader's own
material.

**Re-ingest semantics.** `content_sha256` covers a unit's blocks and answers one
question: *did the source change since we read it?* On re-ingest, a digest that
disagrees with the source means the material has been edited upstream. The
ruling: the archive is **replaced** and the change is **reported** (R6) — never
silently overwritten, and never silently kept. Anything derived from that unit
(pages, narration, exercises) is invalidated by the same signal. Without this,
a corpus drifts out of date with no symptom, which is the failure `layout.py`'s
docstring describes in a different guise.

⛔ **A generator stages beside its target, validates, then moves into place.** A
document that fails its own validation is **never** left at the path something
else will read. Keeping a bad file "so the reading is not lost" was measured to
cost a whole phase of CodeSignal's capture: one unreadable container map halts
every consumer that walks the tree, and the failure is then reported at the
reader rather than at the writer that caused it — **116 archives, 0 pages, 0
narration**, and a broken test suite. A reading that can be taken again is not
worth a file nothing can load.

**`studyforge validate <repo>` is the definition of done** for any adapter:
manifest parses and `corpus_api` is known; every `container.json` address
matches the directory holding it; every archive document parses, carries a
known `raw_api`, and its `content_sha256` matches its blocks; `assert_clean`
passes on every string; unit ordinals are contiguous from 1; declared practice
counts match what is present. Exit 1 naming every failure.

An agent building an adapter therefore has a green/red signal that depends on
nobody's judgement.

---

## 7. Exercises

### The contract

A unit carries zero or more exercises, and an exercise is in one of **three**
states (C5) — a distinction the first draft collapsed, at the cost of throwing
away real teaching content:

| State | What it is | Can complete a practice? |
|---|---|---|
| **none** | the unit teaches, it does not set work | — |
| **ungraded** | a prompt the reader works, with nothing to check it | **no** |
| **graded** | a workspace plus a grader, `authoritative` or `advisory` (R5) | only on a passing grader run |

**Ungraded is why this matters.** All 19 SPARQL lessons end in an exercise; none
ships a test. Recording those as "no exercise" would delete the exercise from
the reader's material to satisfy a two-state model. They are presented as work,
clearly marked as unchecked, and they never complete anything.

Zero remains a **first-class outcome**, not a degraded one — ISO-8583 has none
(§1's table, amended by `W339`: it read *"few or none"* here), and that is
correct.

Each exercise declares a workspace — `main_path`, `test_path`, `run_command`,
`test_command` — plus `provenance` (`bundled` | `generated` | `user`) and
`trust` (`authoritative` | `advisory`). The framework refuses to render a
`generated` grader as authoritative (R5).

⛔ **AMENDED by `W357` — an ungraded unit may name its file.** `main_path` and
`run_command` are the file and how it runs, and every record carries them.
`test_path`, `test_command`, `provenance` and `trust` are the **grader**, written
whole — `trust` alone may be omitted, and defaults from `provenance` — or not at
all. A record with no grader is the **ungraded** state, and it is how the reader's
terminal command (`SF-44`) resolves a file that nothing checks. See
[*A file with no test*](#a-file-with-no-test-w357) below.

### Where that declaration lives

⛔ **It is an `exercise` object inside the practice archive document** —
`<archive-root>/<address>/raw/<variant>/unit-NN/practice-M.json` — versioned by
that document's existing `raw_api`, and written by the **adapter** (R2).

```json
{ "raw_api": 1, "kind": "practice", "ordinal": 1,
  "blocks": [ … the prompt the reader works … ],
  "exercise": {
    "main_path": "practice/…/Executors.java",
    "test_path":  "…/ExecutorsTest.java",
    "run_command":  ["mvn", "-q", "-pl", "23-executors", "compile"],
    "test_command": ["mvn", "-q", "-pl", "23-executors", "test"],
    "provenance": "bundled",
    "trust": "authoritative" } }
```

Four reasons, and the third is the one that decided it:

- **No new document and no new version.** R9 enumerates the versioned contracts
  and each one costs something forever. ⭐ A contract that rides a version it is
  already inside is strictly cheaper than one that adds a sixth.
- **The adapter is the only thing that knows.** `run_command` is a fact about the
  source's build; `provenance` is a fact about where the grader came from. R2
  says an adapter's whole obligation is to write a valid archive, and this is
  archive content. ⛔ Putting it in the authored overlay would make a human type
  it, which R19 forbids.
- ⭐ **§7's three states fall out of the structure, with no flag to remember.**
  **none** — there is no `practice-M.json`. **ungraded** — a `practice-M.json`
  with blocks and **no `exercise` key** (or, since `W357`, a record naming a
  file and no grader). **graded** — the record names a grader. So the
  common case is a corpus that writes nothing: ISO is `none` for all 38 units and
  writes no practice document at all; SPARQL is `ungraded` for all 19 and writes
  a prompt with no workspace. ⛔ A design in which every corpus must declare its
  emptiness is a design fitted to the Java repo, which is the exception (§11.0).
  ⚠️ **DATED 2026-09-19 (`W389`): the STRUCTURE above is unchanged and the reading
  of it is now history.** ⭐ Those two readings are of the corpora *as their sources
  ship them*; from `M10` both are re-ingested with exercises authored for them
  ([above](#exercises-authored-for-every-corpus-w389)), so `none` stops being the
  common case and stays the honest one wherever the gates refuse everything.
- **R5 gets one place to enforce.** `provenance` and `trust` sit on the same
  document, so `studyforge validate` refuses `trust: "authoritative"` alongside
  `provenance: "generated"` — one rule, one file, exit 1.

⛔ **`trust` is declared but never believed.** An adapter writes what it claims;
the framework checks the claim against `provenance` and refuses the combination
R5 exists to prevent. `EX-04` writes the same key for a generated grader that
cleared both gates — the same document, because a generated grader is still
archive content — and it may only ever write `advisory`.

### A file with no test (`W357`)

⭐ **One record, two shapes, and nothing in between:**

```json
"exercise": {
  "main_path": "practice/untested/hello.py",
  "run_command": ["python3", "practice/untested/hello.py"] }
```

| The record carries | State | Can complete a practice? |
|---|---|---|
| `main_path`, `run_command` | **ungraded** — a file, and nothing checks it | **no** |
| those, plus the whole grader | **graded** | only on a passing grader run |

- ⭐ **Graded is the grader's presence, not the key's.** Before `W357` the key's
  presence was the graded state. Now the record's `test_path` is. It is still
  read off the structure, with no flag to set.
- ⛔ **Half a grader is refused**, naming what is missing, and so is a
  `provenance` or `trust` with no grader. Both are facts about a grader, and
  trust in a grader that does not exist is the claim R5 exists to stop.
- ⭐ **The practice with no `exercise` key stays valid and stays ungraded.**
  A corpus whose prompts name no file (the 19 SPARQL lessons) still writes
  nothing.
- ⭐ **Why a record and not a second declaration.** The unit document's
  `workspace` is this record, so the file reaches the one place Run and the
  terminal command already read. That needs no new key in the archive document
  and none in the unit document. The argument is in
  `W357`'s handoff.
- ⭐ **Not a `raw_api` change.** Every document valid before is valid now and
  means what it meant, and an older build refuses the new shape rather than
  misreading it. That is the test §6 applies to `list.start`.

**Run and Submit are different acts.** Run executes the reader's program so
they can see what it printed. Only a `test` run can complete a practice. This
is inherited verbatim from CodeSignal's progress rules and is not negotiable:
a program that prints successfully has demonstrated nothing about its tests.

### Java exercise generation — the two gates

The Java repo inverts CodeSignal's central problem. CodeSignal must *guess* at
a grader it cannot see, which is why its scaffolder is 1,793 lines of
judgement. The Java repo **ships the grader** — 168 test classes that are real
ground truth, paired 1:1 with implementation classes in almost every module.

So generation is mechanical, and — more importantly — **self-verifying**:

```
for each (Impl.java, ImplTest.java) pair:
    select the methods this lesson teaches      (see "Selection" below)
    for each selected method:
        blank EXACTLY THAT ONE body  -> candidate hole
        GATE 1: run ImplTest         MUST FAIL, and the failure attributed
    blank all holes that cleared Gate 1          -> starting code
    GATE 2: run ImplTest against the original    MUST PASS
    both hold  -> ship, provenance=bundled, trust=authoritative
    either fails -> no exercise for that hole, named in the report
```

⚠️ **Gate 1 is per-method, and this is not a detail.** Blanking every body in a
class and requiring the test class to fail proves only *"this test touches this
class"* — which is nearly always true and therefore nearly vacuous. The claim
being made is per-method (*this* body is what the lesson teaches, and the test
discriminates on it), so the check must be per-method too. A class-granular
gate would let a practice ship where most of the work is already done, marked
`authoritative`, which is precisely the failure R5 exists to prevent.

The cost is real: roughly one build per candidate method rather than one per
class. `EX-02` caches by content address, and `EX-00` measures whether the cost
is tolerable before any of E08 is built.

Gate 2 proves the grader itself works. **No human reads anything, and no
assertion is authored by an LLM.** A hole that clears both is provably solvable
— git holds the reference solution — and provably non-trivial.

⛔ **SCOPED, NOT STRUCK, 2026-09-19 (`W389`).** ⭐ **That sentence stays true of every
exercise this section derives** — `bundled`, `authoritative`, blanked from a grader the
source already ships — ⚠️ **and it is exactly why those keep the stronger label.** ⛔ **It
was never a rule about the whole framework, and reading it as one is what left most
sources with nothing to practise.** ⭐ **An exercise whose assertions ARE authored is
`generated`/`advisory` and clears a different set of gates**
([below](#exercises-authored-for-every-corpus-w389)); the two never trade labels.

### Selection and size

A gate says whether a hole is *valid*. It says nothing about whether the
resulting exercise is *reasonable*, and the corpus makes that gap concrete:
implementation classes run to a median of 211 lines and a maximum of **787**
(`39-data-structures/CommonDataStructures.java`, ~100 methods, graded by a
937-line test). Blanking that class yields one all-or-nothing practice that is
a rewrite, not an exercise.

So generation selects rather than blanks wholesale:

- **The lesson README names the methods.** Measured: **162 of the 166 lesson
  READMEs name an implementation class that exists in their own module** — a
  97% signal, far stronger than positional matching, and the same signal that
  drives attachment (§7 below). The methods a lesson discusses are the methods
  it teaches.
- **An exercise has a size cap.** A pair that would exceed it emits **several**
  practices, not one; a hole that cannot be brought under it alone is reported,
  not shipped.
- **Some shapes have nothing to blank, and that is predictable now.** Records,
  sealed hierarchies, interfaces and enums teach through their *declaration* —
  accessors, `equals` and `hashCode` are implicit and unblankable. `09-records`,
  `10-sealed`, and much of `05-pattern-matching` and `28-enhanced-enums` are
  expected to yield zero. That is honest, and it is predicted here so it is not
  mistaken for a defect once generation runs.

Expected yield is well below 100%, and that is the honest outcome, not a bug.
Units with no gate-passing exercise ship as reading-only and are named in the
coverage report (R6). ⛔ **A low yield is never fixed by loosening a gate or
generating an assertion** — that converts a proof into theatre.

### Attachment

Exercises attach to units by ordinal, falling back to title/classname
similarity. Measured across the repo: **87% of modules are cleanly 1:1**.
The outliers — `08-object-oriented` (3 lessons, 11 classes),
`22-locks-semaphores` (2/4), `21-synchronization` (2/3), `01-java-basics`
(4/5), `25-fork-join` (5/4), `29-date-time-api` (8/7) — are handled by
attaching unmatched pairs to their module's final unit as additional
practices. Nothing is dropped silently; everything unmatched is named.
`00-base` holds `PerformanceTestUtil` and no lessons: it is not a container,
but stays on the classpath.

### Where generated sources live

Reader-facing practice material co-locates beside the `.md` (§5). The
*compilable* sources cannot: Maven only compiles what sits on a source root.
They go in an additive `practice/` module mirroring addresses, joined to the
build by one line in the root `pom.xml` — the single existing-file change R3
permits, asserted by `OPS-05`.

### Exercises authored for every corpus (`W389`)

⛔ **ADDED 2026-09-19 — the user's direction, and one of this project's core ideas.**

> *"Bottom line we are building CodeSignal or LeetCode with the idea of LLM extracting
> the content from a given source and make it an enjoyable interactive easy to read and
> navigate website."*

⛔ **Everything above this heading described what a source SHIPS. This subsection is what
a READER gets, and the two stopped being the same thing here.** ⭐ **Delivered as
milestone `M10`** (the task index's `M10`, and epic `E14`, in `docs/tasks/`).

#### 1. Three source cases, one pipeline

| the source has | where the exercise comes from | provenance · trust |
|---|---|---|
| **code and tests** | derived by blanking, through the two gates above — **unchanged** | `bundled` · `authoritative` |
| **code, no tests** | the source's own example is the reference solution; the ask, the starter and the tests are authored from the page | `generated` · `advisory` |
| **neither** | the ask, a reference solution, the starter and the tests are all authored from the page | `generated` · `advisory` |

⭐ **The first row may ALSO gain authored exercises** beyond what blanking yields; those
are `generated`, and they never borrow the derived ones' label. ⛔ **The three rows are
not three pipelines**: one authoring pass, one set of gates per exercise kind, one
bundle shape, one coverage report.

#### 2. Authoring happens once, at ingestion

⭐ **A skill the converting agent runs writes the exercises and commits them into the
CORPUS repository** as source-side material — the *exercise bundle*. The adapter reads
the bundle and writes `practice-M.json` from it, so R2's on-disk seam is untouched and
the framework still knows nothing about any source (R1).

⛔ **No model runs at build time and no model runs at serve time.** The site stays
offline over `file://` (R8) and the build stays byte-reproducible from the committed
bundles (R10). ⭐ **The non-determinism lives in authoring, exactly where a human author's
does** — and, like a human author's, it is reviewed once and then fixed in the tree.

#### 3. Nothing the source already has is lost

⛔ **The reading floor is untouched.** Every example the source ships still renders on the
page, verbatim, whether or not an exercise was built from it.

⭐ **The proof is a *source ledger*.** Every fenced example and every test file the source
carries is an entry, and each entry is either the basis of at least one exercise — named
by that exercise's `origin`, using `SF-36`'s sub-file origins — or carried with a written
reason it is not. ⛔ **An entry with neither is refused** (R6): a silent drop is how
"nothing is lost" becomes a sentence nobody can check.

#### 4. How many exercises a page gets follows the page

⛔ **SUPERSEDED 2026-09-23 by the user's ruling below (`W453`). The paragraph that follows
is kept readable so every citation of it still resolves, and it is NOT in force where it
sets the count by a band of the page's length.**

> ⭐ **The skill writes a per-page *plan* before it authors anything:** a count inside a
> band set by the page's length, moved by the page's distinct checkable skills and by a
> difficulty tier, with every reason written down. ⛔ **The plan is a CEILING, never a
> quota.** What ships is what clears the gates, and every shortfall is named with the gate
> that refused it. ⛔ **A count is never met by lowering a bar.**

⛔ **AMENDED 2026-09-23 (`W453`, USER RULING) — a page is planned by its ASPECTS, not by
its length.** The ruling, verbatim, at the pilot review (on `ISO-M10/6`): *"Depending on
the context of the page there might be no practice, 2 or more, The target is covering all
the aspects not just having something minimum we are looking for quality"*. ⭐ **Refined by
the user the same day**, verbatim: *"regarding the coverage don't over do it! at the same
time we are not a university that wants to grade the knowdlge! Sometimes a single practice
might cover better than 4 unrelated small practices. It's all about quality and the
importants ofthe text. Like for the first quiz the dates do not matter. The version might
matter. And for sure 4 questions were a lot"*.

- ⭐ **The skill writes a per-page *plan* before it authors anything**, naming the page's
  *aspects*: the IMPORTANT ideas it teaches that a reader could be checked on, read from
  its prose AND its code. ⛔ **Trivia is not an aspect** — a date, a name or an incidental
  number is not; the idea it illustrates may be.
- ⛔ **Every aspect is accounted for**: checked by a named exercise (or quiz), or carried by
  a written reason. **An aspect with neither is refused**, the same honesty §3's ledger asks
  of files. ⭐ **One exercise may check many aspects, and one exercise practising related
  ideas is preferred** over several small unrelated ones; a minor aspect is carried by a
  short reason. ⭐ **A quiz asks few questions.**
- ⛔ **Near-duplicates are refused**: two exercises never check one aspect.
- ⛔ **No length ceiling, and no quota.** Zero stays legitimate, with its reason written.
  The record is what was judged important and why — never a coverage percentage.
- ⛔ **Unchanged: the plan is a CEILING, never a quota** (R6). What ships is what clears the
  gates, and every shortfall is named with the gate that refused it. ⛔ **A count is never
  met by lowering a bar.** ⭐ **The same aspects always produce the same plan** (R10).

#### 5. What an exercise says

⭐ **Every authored exercise states a real-life ask**: a scenario, the ask itself, and an
input/output contract the reader can code against. ⭐ **It is graded by tests of the main
ask and by a test of every edge case it names**, so a Submit can report *main ask ✓,
edge cases n/m* rather than one undivided pass or fail.

#### 6. The authoring gates for a code exercise

⭐ **Run by the framework, in the pinned runner image, on every authored bundle. A bundle
ships only if every gate holds.**

| gate | what must hold | what it proves |
|---|---|---|
| **G1 reference** | every test passes on the reference solution, on two runs, with the same outcome each time | the exercise is solvable, and its tests are not flaky |
| **G2 starter** | **every** test fails on the starter, not merely one | no test is vacuous; the reader starts with the work undone |
| **G3 edge, per case** | for each edge case *e* there is a planted solution that solves the main ask and ignores *e*; on it every main-ask test passes and *e*'s test fails | each edge-case test catches the one omission it names |
| **G4 map** | every test the report names maps to exactly one case, and every case is backed by at least one test | the Submit breakdown is total |
| **G5 origin** | where the source supplied code, the `origin` resolves to a ledger entry whose digest matches the source | the exercise is built from what the source has |

⚠️ **G3 is per-case for the same reason the derivation gate above is per-method.** A gate
coarser than the claim it backs is theatre, and it was expensive to learn that once.

⛔ **G1–G3 are MECHANICAL and re-runnable**: the bundle carries the reference, the starter
and each plant, so anyone holding it can take the reading again.

#### 7. A corpus whose subject is not code — the quiz shape

⛔ **RULED by the user, 2026-09-19: the quiz shape is IN `M10`.** ⚠️ **It was proposed for a
v2 backlog and the user said no** — a history book, a standards walkthrough or a prose
tutorial must be able to activate its reader too, and deferring that left most material
at the reading floor indefinitely.

⭐ **The form.** A quiz is an exercise whose `kind` is `quiz` rather than `code`. In place
of a workspace it carries **questions**: a stem, an ordered set of options, exactly one
keyed as correct, one sentence per option saying why it is right or wrong, and an
`origin` naming the passage of the page it came from.

⭐ **How it is authored from the page.** The same pass that plans code exercises plans
quiz ones, from the same ledger: each question is written from one passage, and the
passage is recorded by address, not paraphrased into the question's provenance.

⛔ **SUPERSEDED 2026-09-23 by the user's ruling below (`W451`). The two paragraphs that
follow are kept readable so every citation of them still resolves, and they are NOT in
force where they say the key ships in the page or that the page grades itself.**

> ⭐ **How it is graded without a compiler.** The key and the per-option sentences ship
> inside the practice document, and the page grades the reader's answers itself — no
> container, no network, no model, and identical over `file://` and over a served origin.
> ⛔ **A quiz practice completes only when every question is answered correctly**, and that
> completion is recorded through the reader's own state, never through a run verdict:
> `is_pass`'s rule for a RUN is untouched and a quiz produces no run.
>
> ⚠️ **The key is in the material, and the site does not pretend otherwise.** An offline
> page cannot hide the answer it is about to grade with, exactly as an offline workspace
> cannot hide its test file. ⛔ **Claiming to hide either would be the theatre R5 exists to
> prevent**; the honest design shows the reader the answer after they answer.

⛔ **AMENDED 2026-09-23 (`W451`, USER RULING) — the local study server grades a quiz, and
the key never reaches the page.** The ruling, verbatim: *"the quiz itself again should not
require an online or agent check for the answer user provided. It will be just a test with
the correct answer residing on the server side. When user answers it will get validated
and result will be returned to the user with explanation if needed"*.

- ⛔ **No built page and no asset a page loads carries a quiz's key or any per-option
  sentence.** The key stays in the practice document on disk — the bundle's record, as
  ingested — which is server-side material.
- ⭐ **The local study server grades.** The page sends what the reader chose to a `serve`
  route, which reads the key from the unit's generated document and answers, per question,
  right or wrong **with the CHOSEN option's sentence** — never the keyed option's, so a
  wrong answer is explained rather than corrected. ⛔ **No model, no network and no
  container: a fixed comparison**, and the route never reaches the Docker socket (§8.3). It
  sits behind `serve`'s guards like every other route (R8).
- ⭐ **Completion keeps its meaning**: a quiz completes only when every question is
  answered correctly, decided by the framework's one rule on the server and shown in the
  reader's own page; ⛔ **never a run verdict** — `is_pass`'s rule for a RUN is untouched,
  a quiz produces no run, and grading records nothing.
- ⭐ **Over `file://` a quiz shows its questions and options and says checking them needs
  the local study server**, exactly as Run and Submit already do. ⚠️ This is the register's
  default and it is reversible.
- ⭐ **The quiz gates Q1–Q5 and the bundle record are unchanged**; only where the key is
  read and who grades changed.

⭐ **The honesty gates for a quiz.** A compiler cannot back these, so the gates are
different and their difference is stated rather than smoothed over:

| gate | what must hold | what it proves |
|---|---|---|
| **Q1 answerable** | an independent pass given the page and the question — and nothing else — picks the key, twice, with the same outcome | the page actually contains the answer |
| **Q2 not free** | the same pass given the question and its options but NOT the page does not pick the key | the question tests what this page taught, not general knowledge |
| **Q3 discriminating** | every wrong option is refuted by a named passage of the page | a distractor nobody can rule out is a trick, not a check |
| **Q4 key total and single** | exactly one option is keyed, the options are distinct after normalisation, and every option carries its one sentence | the reader is told why, for whichever option they chose |
| **Q5 origin** | every question's `origin` resolves to a ledger entry whose digest matches the page as ingested | the question is built from the page it is attached to |

⛔ **Q1–Q3 are MODEL JUDGEMENTS taken once at authoring and shipped as a record; Q4 and
Q5 are mechanical and `studyforge validate` re-runs them.** ⭐ **So a quiz grader is
`generated`/`advisory` ALWAYS, and there is no path by which one becomes
`authoritative`** — that is the difference between a proof you can re-take and a reading
somebody took for you, and R5 turns on exactly that distinction.

#### 8. The reference solution is always available

⛔ **RULED by the user, 2026-09-19: always available, never gated behind a passing
Submit.** ⚠️ **It was proposed as a reward for a first pass and the user said no.**

⭐ **Every authored code exercise ships its reference solution as reader-facing
material**, and the page offers it at any time. ⛔ **It is never revealed
automatically** — the reader asks — and asking is never recorded as a failure, because a
reader who reads the answer has still read the material and this is not an exam.
⚠️ **The gates already require the reference to exist** (G1), so shipping it costs
nothing and withholding it would have been a pretence: the bundle is on the reader's
disk either way.

#### 9. What the reader is told, in a learner's words

⛔ **RULED by the user, 2026-09-19: an authored grader is labelled, and the label is
worded for a learner.** ⭐ **R5's vocabulary stays INTERNAL** — `provenance` and `trust`
are the framework's words, in the record and in `validate`, and a reader never sees
either token. ⭐ **The framework fixes the sentence each case renders as, and it is the
framework's constant, not a corpus's string** (R1):

| the record says | the page says |
|---|---|
| `bundled` · `authoritative` | **Checked by the tests that ship with this material.** |
| `generated` · `advisory`, kind `code` | **Written for this site. Its tests were proven against a worked solution before it shipped.** |
| `generated` · `advisory`, kind `quiz` | **Written for this site from this page.** |
| no grader (ungraded) | **Nothing here checks your answer.** |

⛔ **The label is never omitted because it is unflattering**, and it is never softened
into a sentence that implies more than the gate record supports.

#### 10. What is recorded, and what `validate` refuses

- ⭐ **The exercise record gains `cases`** — an `id` as the test report spells it, a `kind`
  (`main` or `edge`), and `says`, the one sentence the reader sees — plus the `report`
  (its format and its path) and the `origin`.
- ⭐ **A gate record ships beside every authored bundle.** It holds the digest of every
  input — statement, starter, reference, tests, each plant, each cited passage — and each
  gate's outcome. ⛔ **`studyforge validate` refuses a `generated` exercise whose gate
  record is absent, or whose digests no longer match the files beside it.**
- ⭐ **Submit reports the breakdown from the test run's machine-readable report**, folded
  through `cases` into *main ask* plus *edge cases n/m*, naming each failed case by its
  `says`. ⛔ **The pass rule does not change**: a practice completes only when every case
  passes, and the breakdown is a report, never a second definition of a pass.

#### 11. When a gate refuses

⛔ **The exercise does not ship.** The skill may re-author that one bundle within a fixed
attempt budget, and ⛔ **never by loosening a gate, dropping a case or deleting a
question**. When the budget runs out, the coverage report names the page, the exercise,
the gate, the case and the run's last output, and a page left with nothing shipped is
named as such (R6). ⭐ **That is the low-yield rule above, applied to authored work: a
shortfall is reported, not engineered away.**

---

## 8. Inherited technical apparatus

CodeSignal solved a number of problems the hard way, and the solutions are
recorded here because **every one of them was measured, and none is obvious
from the outside.** Re-deriving any of them is waste; changing one without
knowing why it is that way is a regression.

⚠️ **CodeSignal is a live repository, and every measurement of it in these
documents is a snapshot with a date.** In the 32 hours after this spec was
frozen it took ~55 commits and 12,568 insertions across 108 files, and three of
the modules this project ports grew by up to 21%. Treat every line count, file
count and percentage here as **as of 2026-09-08** and as an estimate by the time
you read it. ⭐ **A task re-measures its own port surface at start rather than
inheriting a number, and ports from HEAD** — fixes that landed after the freeze
are free if you port current source and are re-derived at full cost if you port
the snapshot.

### 8.1 The code-server toolchain image — its own repository

The embedded IDE is the single most reusable asset in the project and becomes
a **standalone repository**, `code-server-toolchain`. The seam:

| Shared — lives in the image repo | Per-project — lives in the consuming repo |
|---|---|
| `Dockerfile`, `entrypoint.sh` | `docker-compose.yml` |
| the workbench lockdown extension | **mounts** — which paths, which read-only |
| seed settings and keybindings | container name, port binding, password env |
| toolchain selection and pinning | the `prime/` project supplied at build time |
| extension list and verification | uid/gid mapping to the repository's owner |

What the image already gets right, and must keep getting right:

- ⚠️ **Version-pinning and SHA-256 verification are a TARGET here, not an
  inherited property.** Three archive downloads are verified today (Gradle,
  Kotlin, Node) — but `eclipse-temurin:26-jdk`, `ghcr.io/astral-sh/uv:latest`
  and `codercom/code-server:latest` are all floating `:latest` tags, and
  `apt-get`, `uv python install`, `npm install -g` and every marketplace
  extension id are unpinned. **A `:latest` base image means the image is not
  reproducible (R10)**, so `TC-01` must *reach* this state rather than preserve
  it, and "functionally identical to CodeSignal's" is not sufficient acceptance.
- **Extensions are installed at build time into a directory in the image**,
  not onto a volume, so an image upgrade always carries them — and the build
  **verifies the installed list and fails on a missing id**, with a documented
  fallback where a marketplace may stop serving one.
- **PATH is set twice, deliberately.** `ENV` reaches non-login shells; the
  integrated terminal starts bash as a *login* shell and `/etc/profile` then
  overwrites PATH, silently dropping everything under `/opt` — so a tool works
  under `docker exec` and is "command not found" in the terminal. A
  `profile.d` script fixes it.
- **The build cache is primed by building a real trivial project.** `prime/`
  copies the consuming repository's wrapper and build files with one minimal
  source and test per language, so the first offline build needs no download.
  The sources must be *real*: a `NO-SOURCE` compile task never resolves the
  compiler classpath, so an empty prime silently primes nothing. Version
  guards fail the build if `prime/` and the image's pinned versions disagree.
- **The lockdown extension is packaged as a `.vsix` and installed**, never
  copied into the extensions directory — the workbench reads `extensions.json`
  and never scans, so a copied folder is present, correct and silently never
  loaded.
- **Named-volume mount points are created in the image, owned by the runtime
  uid.** Docker creates a missing mount point root-owned, which leaves the
  server unable to write its own config.
- **`ENTRYPOINT` and `CMD` are both re-declared**, because the base image bakes
  arguments that a compose `command:` would otherwise be appended to.

And what the *compose* side gets right, which stays per-project:

- ⚠️ **Loopback-only port binding, never `0.0.0.0`** — an unencrypted IDE with
  a shell. Also a **target, not a preserved property**: the editor honours it,
  but the synthesis service is published on all interfaces today, contradicting
  its own compose file's header. `TC-05` and `OPS-03` fix it rather than copy
  it.
- **Only the sources are mounted** — not the repository, not `$HOME`.
- **The container runs as the repository owner's uid:gid**, so files it creates
  are not root-owned on the host.
- **A bind source must exist on the host before the container starts**, or
  docker creates it root-owned and the writer can never write it. ⭐ **The
  general form: every bind source exists before the start — where another
  service in the project creates one, the editor is gated on that service's
  health check; where the project creates it itself, it is created before the
  containers come up.** ⚠️ **`TC-05/5`, corrected 2026-09-19 (`W400`): this
  bullet used to say *"the backend creates it and the container waits on the
  backend's health check"*, which describes a two-service project — and a
  corpus served by this framework has no backend service in the editor's own
  compose file.** ⭐ **The per-mount and ordering keys that carry the general
  form live in `code-server-toolchain`'s consuming contract, which `TC-05`
  owns; this section states the ruling, not the shape of one project.**

#### ⛔ AMENDED PO round 74 — the browser editor comes after the framework milestone (user direction, 2026-09-12)

> *"We can even move the code-server to when after we are a framework! Because that functionallity is needed mostly for when exercises are in the picture. We can still have a dockerfile to run code in Java, Kotlin, Python, and Nodejs and maybe even shell and sql using an in memory database or whatver that course requires without the need of having the code-server to be deployed or shown in the web to client. Client still can run things in their terminal update the file and run them by a command which then will be run against that unit test associated with the file if there is any."*

1. ⭐ **The execution track opens with a RUNNER IMAGE, not an editor** (`TC-00`, `M5`): pinned, no IDE, never served. ⛔ **The user's list is a requirement — Java, Kotlin, Python, Node.js, and possibly shell and SQL against an in-memory database, or whatever the course requires — and R1 makes the set a corpus gets MANIFEST DATA.**
2. ⭐ **The reader runs a unit's test from their own terminal** (`SF-44`, `M5`). ⛔ **A file with no test is not a failure** (§7, C5).
3. ⭐ **This section's image, the editor, lands at `M7`, and every measured property above binds it then.** ⛔ **§8.3 is untouched: the Docker socket is never mounted into the serving process.**

⭐ **Ruled by the register as reversible, because the words do not decide it:** the terminal command and graded Submit both take `SF-20`'s two modes as §8.3 already states them — the runner container when it is up, the host otherwise, with identical observable behaviour.

### 8.2 The narration service — its own repository

Narration gets the same treatment as the IDE, and for the same reasons:
`narrate-service` becomes a standalone repository exposing a **batch synthesis
API over HTTP**, containerised, with the engine behind an adapter.

| Shared — lives in the service repo | Per-project — lives in the consumer |
|---|---|
| the batch job API and its manifest format | which segments to synthesise |
| engine adapters and the voice catalogue | voice selection for the corpus |
| containerisation, CPU and GPU variants | **where the files land** (R4) |
| content-addressed caching | the personal-data gate |
| the optional agent-callable adapter | incremental regeneration policy |

Four decisions, three of them corrections to what exists today:

- **The unit of work is a batch of keyed segments, not one blob.** ⚠️ An earlier
  draft of this section said today's client sends one request per unit and gets
  one mp3 back. **That was wrong** — it has always looped one HTTP request per
  *speech unit*, which is why the conclusion still holds and the premise needed
  correcting. The page's highlight sync needs **one clip per speech unit**
  (§8.4), so the API takes a list of `{id, text}` and returns one artifact per
  id plus a manifest. A batch rather than a request per segment because a corpus
  is thousands of segments, and per-request overhead is the difference between
  minutes and hours. ⛔ **THE BATCH API ARRIVES IN TWO STEPS, and this paragraph
  describes the FINISHED shape rather than the first one.** ⭐ The service is
  stood up behind a single-utterance route first; the batch route and its
  content-addressed cache land after it, and `E13` carries the split and which
  task owns which half. ⚠️ **Written here because `E13` sends a taker to this
  section FIRST, so a reader of this paragraph alone would build the whole batch
  API in the task that only stands the service up** (`NS-01/1`, settled in code
  by `NS-02`; this sentence is the remainder Ruling 335 leaves to this register).
- **The service never writes into a corpus.** It returns artifacts for the
  caller to fetch and place through the placement policy. A synthesis service
  that knew where a study site keeps its audio would be a second authority on
  layout, which is precisely what R4 removes.
- **⛔ The gate runs client-side, before the request** — never in the service.
  This is carried from today's implementation and the reasoning is worth
  restating: **an mp3 that speaks an account identifier is personal data on
  disk that cannot be grepped for afterwards.** The service is a third party
  from the framework's point of view; ungated text must never reach it (R7).
- **The engine is pluggable and must not require particular hardware.**
  Today's deployment pins a GPU build for one specific card generation and
  reserves every NVIDIA device on the host. That is fine as *a* deployment and
  unacceptable as *the* deployment (R15): the service ships a CPU path that
  works anywhere, with GPU as an opt-in profile.

Two properties of the current implementation carry over unchanged because they
are already right: **chunking is the service's job** — the endpoint accepts a
very long input and splits internally, so no client keeps stitching logic — and
**writes are atomic**, landing in a temporary sibling and being renamed, so an
interrupted run never leaves a truncated file that looks finished.

⚠️ **Synthesised audio is the one carve-out from R10's byte-for-byte clause.** A
speech model is not guaranteed to emit identical bytes for identical input, so
audio is not byte-for-byte reproducible the way generated HTML is. It is instead
**content-addressed and cached**: a segment whose text and voice parameters are
unchanged is never re-synthesised, and the manifest records the address. R10
continues to apply in full to every other generated artifact.

### A clip's filename carries a digest of the words it says

⛔ **A narration clip is named `<speech-id>-<8 hex of sha256(spoken text)>`.** It
is minted by **one** function — the speakable contract, which already owns both
what is said and what it is called — and both the renderer that links the clip
and the client that places it go through it. A second minter is a page asking
for a file the placer never wrote, with no symptom but silence.

The obvious alternative was to keep a plain positional name and decide currency
with a *check* — a sidecar manifest of content addresses, or a re-submission to
the service, whose cache is content-addressed anyway and would decline the work.
Both were rejected, and the reason is the failure they permit: ⛔ **a check can
be skipped, and the skip is silent.** CodeSignal's synthesis runner decided a
clip was current by whether the file existed. When its catalog was re-captured,
**619 clips went on speaking the previous wording** and 442 more were orphaned
by documents that had changed shape — the run reported *"0 synthesised"* and
every gate was green. Nothing distinguishes a correct incremental run from that
one by inspection.

⭐ **The digest makes it structural rather than checked.** Change the spoken text
and the name changes; the page then links a clip that is not on disk, and the
client synthesises it. **A stale clip cannot be addressed.** It needs no
discipline, survives a stage being run on its own, and survives a
re-implementation.

⚠️ **The speech id stays positional, and this is not a reversal of that.** The id
is what a *structure* edit must not renumber, so that retitling a section does
not orphan a unit's audio. The digest is what a *text* edit must change. They
answer different questions and the filename carries both.

⚠️ **This is not the shared-asset case** R10 rules hash-free. That objection is
about a stylesheet linked by every page, where a digest means rewriting the
whole corpus for a colour change. Here the page is already rewritten whenever
the text changes — in the same generator run.

⚠️ **The old clip stays on disk under its old digest, playable by nothing.**
Reconciliation deletes what a unit's document no longer names, and ⛔ **only for
the units the run actually read** — never on behalf of one it skipped.

**What it costs:** a prose edit renames a file, so an incremental build writes an
audio file it would otherwise have kept. That is one synthesis of one segment —
the segment the author just changed — and the service's content-addressed cache
means an unchanged segment is still never re-synthesised.

### 8.3 Where execution runs — the resolved question

**The problem.** R15 wants reproducible execution. The Run/Submit route and
E08's gates must invoke a pinned Maven toolchain. The obvious reading — put the
server in a container too — requires mounting the Docker socket into it, and a
socket inside a network-listening process is root-equivalent access to the host.

**What CodeSignal actually does**, which is the evidence that settled this: it
**refuses** that trade. Its compose file states plainly that *no docker socket
is mounted anywhere*; the study server runs with `network_mode: host` and is
started with `--no-docker`, taking its toolchain from the host PATH. The
`docker exec` mode exists in its runner and **the shipped deployment does not
exercise it.** So the path studyforge depends on is, today, untested in anger.

**The ruling.**

1. **The toolchain is containerised; the serving process is not.** Maven, the
   JDK and their caches are pinned in the image (§8.1) — that is where
   reproducibility actually lives. The server is a standard-library HTTP
   process with no dependencies, so a container adds nothing to it.
2. ⛔ **The Docker socket is never mounted into the serving process.** Not as a
   convenience, not behind a flag, not "only locally". This is the single
   non-negotiable in this section.
3. **Execution crosses into the container from outside it.** The runner, which
   is the only package permitted to start a process (SF-20), invokes the
   toolchain container from the host. Commands come from a generated document
   on disk; nothing a client sends becomes a command.
4. **The `docker exec` path must be proven, not assumed.** It is the one
   inherited mechanism with no deployment behind it. `SF-20`'s acceptance —
   *"both modes produce identical observable behaviour"* — is therefore a real
   test to write, not a formality to restate.
5. **If full containerisation is ever required**, the answer is a separate
   execution broker owning the toolchain, which the server posts jobs to — the
   same shape as the narration service (§8.2). It is not in v1 scope, and it is
   recorded here so nobody reaches for the socket instead.

**What this costs the reader:** the host needs Python (standard library only)
and a Docker CLI. Nothing else. The toolchain, its caches and every pinned
version stay in the image.

### 8.4 What carries over from CodeSignal essentially unchanged

These are proven surfaces. v1 generalises their addressing and changes nothing
else. Re-deriving them would be waste.

- **Reading page** — serif reading column, shared `unit.css`/`unit.js` with
  deliberately unhashed names, browser-side Prism highlighting (never
  build-time), light/dark palette with every token defined in both themes.
- **Narration** — positional (never content-derived) speech **ids**, display text
  and spoken text as two renderings of one list, clip-level highlight sync. The
  clip **filename** adds a content digest, for the reason ruled in §8.2; whether
  the clips are committed is a manifest policy, ruled in §5.
- **Video** — vendored Plyr with `loadSprite:false`; nothing may reach the
  network. Unused by the Java source, kept because the contract is generic.
- **Table of contents** — `toc.json` (stable, reproducible) and `status.json`
  (local, volatile) as two documents, so a consumer can cache one and poll the
  other. Generalised from fixed nesting to `len(levels)`.
- **Backend** — `/api/v1/content` (cacheable, strong ETag) vs `/api/v1/state`
  (never cached) vs `/api/v1/assets` (Range, weak ETag); loopback only;
  cross-site requests refused.
- **Runner** — `docker exec` into the toolchain container when up, host `bash`
  otherwise; line-by-line streaming; one exit line; every line scrubbed.
- **Progress** — see below: it is two records, not one.

⛔ **A fence with no info string renders as plain text, and the renderer never
guesses a language** (`Q7`, ruled at PO round 107; landed by `W347`). ⚠️ A guess is a
silent wrong highlight, which is worse than no highlight. ⭐ A `code` block
whose `lang` is empty carries no highlighter class and the caption `code`
(`render/page/blocks/figure.py`).

⭐ **AMENDED 2026-09-23 — the reading room's identity, and the palettes it may never
ship.** Carried from the UI design convention when the conventions were archived. That
convention held a whole design brief; what a rendered page is held to belongs here,
beside the reading page it governs, and the brief's process advice to a designer does
not.

⭐ **One framework identity, and a per-corpus theme that defaults to it.** Every
studyforge site shares one look, drawn from the subject every such site shares —
reading and study — and a corpus may declare its own theme as manifest data (R19),
chosen from its own subject. ⛔ **It is built to be read for hours, so it is judged on a
real generated page**, light and dark and at phone width, with its contrast computed
rather than eyeballed, and what is reported is what was seen.

- ⛔ **Colour is a role-named token and nothing else.** Every colour is a CSS custom
  property named by its role — ground, raised surface, ink and its quieter inks, rule,
  accent, the semantic states — and a stylesheet paints only with tokens. Both themes
  are designed: the dark tokens are defined under `prefers-color-scheme: dark`, guarded
  so an explicit light choice wins, and again under an explicit dark choice. One
  dominant ground, one sharp accent, and semantic colour kept apart from the accent.
  ⛔ A saturated colour never grounds a whole page; it belongs on one element.
- ⛔ **Contrast is computed and reported**: body text at least 4.5:1 against its actual
  background, large text and non-text marks at least 3:1.
- ⭐ **Faces are vendored font files loaded by a relative `@font-face`, pinned by digest
  with their licence beside them, and SIL OFL faces only** — ⛔ never a CDN, because a
  generated page opens from `file://` with no network (R8). A face has a reason to be
  there; a bare system stack or one of the generic defaults is not a choice.
- ⭐ **Structure encodes information.** Numbering only where order is real, dividers
  only between things that are separate, one bold element carrying the identity with
  everything around it quiet, prose at a readable measure, and a page that stacks at
  phone width with no horizontal scroll.
- ⛔ **Motion answers an action and never holds content hostage**: it animates
  `transform` and `opacity` only, honours `prefers-reduced-motion`, and no element's
  resting state depends on an animation having run.
- ⛔ **Interaction and accessibility.** Expand and collapse are two controls, never one
  toggle whose label flips; `:focus-visible` is visible everywhere; `<button>` acts and
  `<a>` navigates; an icon-only button has a label, a decorative glyph is hidden from
  assistive technology and a live message is announced; a skip link reaches the main
  content, heading levels run in order, and a sticky header never covers what the
  reader jumps to.
- ⛔ **Copy is written from the reader's side** — sentence case, active voice, no
  builder vocabulary, and no label that stops being true, such as a *New* badge on a
  site where everything is new to its reader.
- ⛔ **The tells of generated design are refused**: content chopped into identical
  rounded cards, pill tags in several accents, all-caps eyebrow labels, meta strings
  joined by middle dots, arrows appended to links, a monospace face for small labels,
  a stripe down a card's edge, and gradient washes or badges that tell the reader
  nothing.

⭐ **The rejected palettes are data, and the floor reads them.** A list of rejected
palettes written as prose was right, was read by nothing, and a repaint's first stage
shipped half of one. So the tells that can be read off a colour are the two tables
below, which the palette check reads over every stylesheet the framework ships: a
rejected identity that returns is a floor finding, by name. ⛔ **The tables are the
authority and the check is only their reader**, so a new rejected identity is a row
added here, with no code change. ⚠️ **A green check means *no rejected palette is
shipped*, never *the identity is met*** — a face, the card kit or an eyebrow label is a
tell no hue can see.

Every colour is read as three measures: **hue** in degrees; **chroma**, `max − min` of
its channels over 255, in percent; and **light**, `(max + min) / 2` over 255, in
percent. ⛔ **Chroma and not HSL saturation, deliberately**: a near-white paper with a
one-step tint reports a saturation near 40% and a chroma near 3%, so a bound written in
saturation would refuse the paper that was accepted. ⭐ **A row's parts are joined by
`+`, and every part must hold in one theme** — light and dark are read apart, each over
the tokens it defines — with the parts on one role met by that theme's colours for it.
⛔ **The conjunction is the instrument**: cool slate alone is the accepted identity, and
it is the triple that was rejected, so a row that fired on one part would refuse the
accepted identity on its first run.

| Role | Read from |
|---|---|
| `ground` | `--bg` |
| `raised` | `--surface`, `--surface-2`, `--panel` |
| `ink` | `--fg`, `--fg-soft`, `--muted` |
| `rule` | `--rule`, `--rule-strong` |
| `accent` | `--accent`, `--sign`, `--focus` |
| `gradient stop` | ⛔ no token — every colour inside ONE `linear-gradient(` or `radial-gradient(`, its `var()` resolved in that theme; a row's stop parts must meet in the SAME gradient |

| Rejected identity | Every part must be present | Why |
|---|---|---|
| Warm cream and terracotta | `ground: hue 20-70, light >= 85, chroma >= 3` + `accent: hue 5-32, chroma >= 25, light 25-65` | the first tell of generated design, and the one a repaint's first stage shipped |
| Near-black ground, acid-green accent | `ground: light <= 12` + `accent: hue 75-165, chroma >= 45` | a tinted near-black standing in for a dark ground, where a real mid-dark with character is asked for |
| Near-black ground, vermilion accent | `ground: light <= 12` + `accent: hue 0-20, chroma >= 45` | the same tell's other accent |
| Cool slate with teal-green and amber | `ground: hue 190-250, chroma <= 20` + `accent: hue 150-190, chroma >= 20` + `accent: hue 35-60, chroma >= 30` | the user's own rejection — *"very generic and repetitive between the designs you always generate"*. ⛔ It is the TRIPLE: the slate alone is accepted |
| A saturated brand colour as the page ground | `ground: chroma >= 30` | a full guide-sign-green ground was rejected outright |
| A purple-to-blue gradient | `gradient stop: hue 258-300, chroma >= 20` + `gradient stop: hue 200-255, chroma >= 20` | a generated-design tell, read where a gradient actually is |

#### ⭐ What the user ACCEPTED, 2026-09-19

⛔ **The rejected table is half of what a repaint needs, and the other half is what was
accepted** — six refusals do not say what to build.

| Part | What was accepted |
|---|---|
| neutrals | a cool slate scale, ground through rule, in both themes |
| the accent | ONE loud accent, live where it means *next* or *you are here*, and nowhere else |
| green | ⛔ **none in the identity** — *"I am not a fan of green"* |
| themes | both, each designed, with the reader able to choose between them and the system |
| ink | the quieter inks in separate contrast bands — one band for all three is what *"too dim"* named |

⭐ **Two reference pages of the user's own were named as the standard**: their
documentation reference, for the slate scale and the ink bands, and their route
planner, for the one loud accent and the contrast it holds. ⛔ **They are named in words
and nothing else** — neither page's location, bytes, palette nor screenshot enters this
repository, so nothing here can go stale against them, and a repaint that needs one
asks the user for it. ⚠️ **The no-green bound is not read by the palette check**: it is a
rule over the shipped tokens rather than a rejected identity, and the reading room's
own palette tests hold it.

### 8.5 Progress is two records

**Two different things are being recorded, and they are established by different
means.**

A **read mark** is the reader's own assertion that they have read a unit. It
needs no server, no grader and no origin, so under R8 it must exist without one:
it lives in the browser's local storage, and the site says plainly that it is
**one browser, one machine, not in the repository, and gone with site data.**

A **practice pass** is a fact established by a grader run. A grader run required
the runner, which required the server, so the record is written where the fact
was established: the git-ignored JSON file, read-validate-modify-write under a
lock, atomic replace, `first_passed_at` set once and never moved.

⛔ **The obvious alternative — one store — fails in both directions.** Put
everything in local storage and a pass becomes a claim by a client that the
server cannot check, lost with site data and not worth restoring. Put everything
server-side and R8's floor means a reader who only ever double-clicks a page has
no record at all.

⚠️ **The motivation was CodeSignal's and is temporary; the requirement is ours
and is structural.** CodeSignal reached this because it happens to have no
practices to submit — a state of one corpus that could change tomorrow.
`studyforge` reaches it because **§7 admits three exercise states and two of
them can never complete anything**, and R8 says a server is never a prerequisite
for reading. ⭐ **It binds hardest on exactly the sources this framework exists
to serve.** The Java repo, with 168 graders paired 1:1, is the exception; an
arbitrary repository ships no graders at all, so every unit in it is `none` or
`ungraded` — and a server-side-only store would record *nothing whatever* for
the entire corpus.

⛔ **A read mark is an explicit act.** Never inferred from scrolling, from the
narration reaching the end, or from a page having been opened. Inference marks a
unit read when somebody skims, and a record the reader cannot trust is worse
than none.

⛔ **The two are joined by the address (§4) and by nothing else.** A key shape
that disagrees is a mark written under one name and read back under another,
with no symptom but a badge that never lights. The state route may *report* a
client's read mark; it may **never** treat one as a pass.

⛔ **The mark carries no clock.** A timestamp is a second fact nobody asked for,
and it turns the personal-archive merge into an ordering problem rather than a
set union.

⛔ **Local storage is touched in exactly one source file**, which defines the
store and is shared by the unit page, the container page and the index. Two
implementations are the key-disagreement failure above, reached by another road.

⚠️ **A shared script is concatenated ahead of every file that uses it, and the
order is asserted against the real composed bundle** — never against a test
harness's own concatenation. CodeSignal placed its store *after* the page script
that read it at startup; the guard skipped, the setting silently never came
back, **the suite stayed green**, and it was found only by loading a page in a
browser. A harness that arranges the world conveniently proves nothing.

---

## 9. The skills layer — what is actually being built

R16. The pipeline is the means; **the skills are the product.** The end state
is that somebody points a skill at material they care about — a course site, a
book, a paper collection, a repository of exercises, their own notes — and gets
this format back, then keeps it as a durable personal record they can review,
re-run and extend.

The division between them is the same seam as everywhere else (R2): one
understands *a source*, the rest are source-agnostic.

- **Reconnaissance.** Given arbitrary material, work out its shape: how deep
  the hierarchy is, what the units are, whether there are variants, whether
  anything is runnable, whether any grader ships with it. Produces a draft
  `corpus.json` and an honest report of what it could not determine. This is
  the only skill that reasons about unfamiliar material.
- **Adapter authoring.** Scaffold an adapter for that shape, against
  `studyforge validate` as the definition of done — so the skill's output is
  checkable by machine rather than by opinion.
- **Corpus onboarding.** R19's realisation: take a repository from nothing to a
  serving study site. It writes the manifest, the adapter package and its tests,
  the ignore rules, the compose file, the toolchain selection and its prime
  project, the build entry point, the non-destructive assertion and the reader's
  documentation — and it writes an **uninstall** that reverses every edit it
  made. ⭐ **The one manual step is: add the framework, run this skill.**
  Everything after that is generated, and anything a second source has to type
  by hand is a defect in this skill.
- **Build and serve.** One invocation from raw material to a running site:
  ingest, validate, unit documents, pages, narration, contents, exercises.
- **Delivery planning.** The product owner for an integration: turns *"convert
  this repository"* into an ordered backlog whose every task ends in something a
  person can be shown, with acceptance the framework itself can evaluate. It
  runs in the target repository, and ⛔ **its only channel is this framework** —
  it may ask questions, and it may file findings, but it may not patch (§12) and
  it may not read the extraction source (R20). It maintains the **integration
  catalogue**, below.
- **Personal archive.** Export and re-import a corpus *with its progress* —
  code, practices, examples and what the reader has completed — so the record
  survives a machine, and a corpus can be handed to somebody else without its
  owner's progress leaking with it (R7).

**What this buys the Java repo:** it is built by the same skills anyone else
would use, so if the skills are awkward there, they are awkward everywhere.
The Java corpus is the proving ground, not a special case.

### A skill precedes the artifact it produces

⛔ **A skill written after the thing it "produces" is a retrospective, not a
tool.** It has been validated against exactly one source — the one it was
reverse-engineered from — which is no validation at all, and the first genuine
test of it is the second source, which is precisely where it must not fail.

So the skills divide by what they actually are:

- **Skills that are how an artifact comes to exist** — reconnaissance, adapter
  authoring, corpus onboarding, and the authoring reference they point at.
  These land **before** the first corpus is built, and the Java corpus is their
  **first output** rather than their input.
- **Wrappers over entry points that already work** — build-and-serve, exercise
  derivation, personal archive. These genuinely cannot precede what they wrap,
  and they land last.

⚠️ **The cost is real and is accepted:** the first three are written before
anybody knows what a second adapter looks like. The answer is that they start
deliberately minimal and grow — a skill that scaffolds a package layout, a test
tree and an audit command, and leaves the source-specific reading to be filled
in, is buildable early and is already what its definition asks for. The
alternative is worse: a corpus built by hand, and skills written afterwards to
claim they produced it.

### The integration catalogue

R20 says a consumer never reads the repository this framework was extracted
from. That is only honest if what a consumer would have gone looking for is
**here** — so the framework carries a catalogue of what goes wrong when material
meets it, written for somebody planning work rather than somebody writing code:
a plausible short parse that raises nothing; a corpus carrying the same material
twice; a hierarchy encoded in filenames; an exercise with no grader, which is
not "no exercise"; media that outgrows a git remote; an address derived from a
title, which sends one link in eight nowhere.

⭐ **It is a growing asset, not a founding document.** Each integration's
findings (§12) are distilled back into it, so the next integration starts
further along than the last. ⚠️ **This is the mechanism by which the framework
gets better at being adopted**, as distinct from getting better at rendering
pages — and without it, every new consumer re-derives the same lessons from a
moving repository and the expertise lives nowhere.

### How a consumer obtains the skills

R18 settles the distribution: the framework is **pinned**, never copied, because
a copied skill is a fork that a framework fix never reaches. ⚠️ **Pinned, not
submoduled** — R18's 2026-09-09 amendment removes submodules, so the framework is
present as a **sibling checkout at a recorded commit** and the parent's pin file
is what records which one. The load-bearing half is unchanged: ⛔ never vendored,
never copied, never forked.

But there is a real tension worth naming, because it is where copying starts:
**a pin is a commit, while skill discovery is path-based** — a skill has to be
findable at a path inside the repository the agent is working in.

⭐ **The pin is the authority; the discoverable path is a generated pointer.**
Onboarding writes thin **skill stubs** into the target repository that name the
pinned framework's skill and delegate to it, carrying the pinned version and
nothing else. ⛔ **A stub that has drifted from its pin is a build failure** —
that is what stops a stub becoming a fork by accretion. It is the same shape as
pinning a published image tag rather than forking a Dockerfile.

⭐ **AMENDED 2026-09-23 — a page that hands a reader a command declares the modules it
does not own.** Carried from the commanded-pages convention when the conventions were
archived. Every `docs/authoring/` page and every shipped `SKILL.md` that gives a
`python3 -m` command is one population, and ⛔ **a commanded module must run in this
repository unless the page declares that it belongs to the consumer.** The declaration
is a line of its own whose backticked tokens are the modules, in one spelling:

```text
**Consumer-side modules:** `<module>`
```

This fence is the one place the spelling is written down, and a page that uses it names
this document beside it. The authoring suite's reader — `DECLARES_CONSUMER_SIDE` in
`tests/authoring/support.py` — is the authority on that spelling: a page that disagrees
with the reader is the defect, and `tests/test_consumer_side_contract.py` fails when the
fence and the reader drift apart. ⛔ **The exemption belongs to the page that declares it**, so a module declared
consumer-side on one page earns nothing on another. ⭐ **Why a declaration and not a
list:** a list of exempt modules kept beside the checker is a second copy no page's
reader can see, and a skill that sends a stranger to run a module absent from the
repository they are standing in is a first-run failure the stranger cannot diagnose.

---

## 10. Out of scope for v1

Named explicitly so no agent builds them.

- Any CodeSignal change. It is untouched; convergence is v2.
- ISO-8583 and SPARQL adapters. The contracts are designed for them; the
  adapters are v2.
- Cross-corpus dedupe, concept equivalence, multi-variant merged units.
- Turning the uniform `Interview Q&A Section` into a quiz or flashcard mode.
- Search across corpora.
- Ragged-depth hierarchies.
- Drift-check tooling. Nothing has diverged yet; revisit when it does.

---

## 11. Acceptance

### 11.0 What a corpus is entitled to, and what it earns

⛔ **A corpus is complete when it delivers everything its material supports —
not when it delivers everything the framework can do.** Two tracks, and the
manifest decides which apply:

**The reading floor — every corpus, always.** Units readable offline over
`file://` with no network and no server; narration; a table of contents and a
root index with working deep links; navigation between units; the reader's own
read marks. ⭐ **This is a complete product on its own.** A corpus that stops
here is not a degraded one — for prose, a book, a paper collection or a set of
notes, it is the whole thing, and R8's floor means it needs nothing running.

**The execution track — only where the material is runnable.** A workspace, Run
and Submit, a pinned toolchain container, graded practices. Gated on the
manifest's `exercises` (§4) and on §7's three states. ⛔ **A corpus with no
graders skipping this entire track is a pass**, not a shortfall (C5) — and it is
the *common* case, not the exception. The Java tutorial, with 168 test classes
paired 1:1, is extraordinary; most material is not like it.

⛔ **AMENDED 2026-09-19 (`W389`, user direction) — the gate is the MATERIAL, no longer
what the source packaged.** ⭐ **A corpus enters the execution track when its subject
admits a checkable coding task**, whether or not the source ships a grader: from `M10`
the exercises are [authored at ingestion](#exercises-authored-for-every-corpus-w389).
⭐ **A corpus whose subject admits no checkable coding task still gets *checked*
practice — the quiz shape** — and a quiz needs no container, no network and no server,
so it sits **on the reading floor**, not in the execution track. ⛔ **Skipping the track
remains a PASS**; what stops being a pass is a reader with nothing to practise.
⭐ **The reading floor is still a complete product on its own, and still offline.**

⛔ **AMENDED 2026-09-23 (`W451`, user ruling) — *"no server"* above is SUPERSEDED.** A quiz
still needs no container, no network and no model, and it still sits on the reading
floor rather than in the execution track — ⭐ **but its answers are checked by the local
study server**, which holds the key the page no longer carries (§7 §7's amendment). Over
`file://` a quiz shows its questions and says checking them needs that server.

⛔ **AMENDED 2026-09-23 (`W460`, user ruling) — *"narration"* above is OPTIONAL.** ⭐ *"it
should be optional … Somebody might wants to just cover the course wihtout voices"*: a
corpus whose `corpus.json` says `narration: false`, or a run given `--no-narration`, is
the reading floor without its voice, and ⛔ **that is complete, not short** (C5) — no
player, no clip served, no "missing" notice, and every clip kept on disk (§4, `narration`).

⚠️ **The order follows from that.** The reading floor comes first and completely,
because it is what every consumer gets and the only thing some consumers want.
The execution track is built when a corpus needs it — which is a real decision
about a real source, not a milestone everyone waits behind.

⛔ **AMENDED PO round 74 (user direction, quoted in §8.1's amendment and §12's):** ⭐ **the track's container is the runner image, and the browser editor joins at `M7`.** ⚠️ **The track now runs AFTER the first corpus and the framework proof — `M4` → `M6` → `M8` → `M5` → `M7` — and the Java corpus re-validates at `M9`.**

### 11.1 The framework

1. `studyforge validate` passes on a valid archive and fails, naming the
   specific failure, on each invalid fixture — **including a source whose
   material the adapter silently failed to read in full** (SF-25).
2. Both `FND-04` fixtures — one **depth-1**, one depth-2 — build, render, and
   serve with **no corpus-specific code anywhere in the framework** (R1),
   asserted rather than assumed.
3. A corpus's units are readable offline over `file://` — no network, no server
   — with narration, syntax highlighting, working navigation, and read marks
   recorded and surviving a reload (§8.5).
4. The root index renders a hierarchy of any declared depth with working deep
   links. Its **only inputs** are the two contents documents — asserted; and ⛔
   **it fetches nothing at runtime**, because `fetch` of a sibling file is
   refused over `file://`, there being no origin to ask, so contents data is
   delivered into the page at generation time.
5. `studyforge plan` names every path a build will create and every declared
   edit, before anything is generated, and what a build then does matches it.
6. No source module exceeds 400 lines and no test module exceeds 600, or the
   exception is stated and justified in the module's own docstring (R11).
7. Every package has tests, and the test tree mirrors the source tree (R12).
8. Tests, generation and serving all run in a container from a clean checkout,
   with Docker as the only prerequisite (R15).
9. ⛔ **WITHDRAWN 2026-09-12 with R14.** The number is retained so nothing
   below it moves; there is no index and no criterion here.

### 11.2 Any corpus the framework builds

10. It was produced **by the skills** of §9, and git can say so: the adapter was
    scaffolded and the deployment artifacts generated **before** any of their
    contents was hand-written, so the scaffolding commits precede the
    source-reading commits. Every subsequent hand-edit to a generated artifact
    is recorded as a finding against the skill that should have produced it
    (R19).
11. `git status` shows **no modification to any pre-existing file** except the
    entries its manifest declares in `permitted_edits`, and the check that
    asserts it reads the declaration rather than naming the file (R3).
12. Its ingest audit exits 0, or exits 1 naming exactly the known outliers.
13. Its media footprint is measured and inside its declared limits, or the build
    said so and stopped (SF-32).
14. ⛔ **It reaches the reading floor in full**, and reaches whatever of the
    execution track its material actually supports — with the coverage report
    stating honestly which units are reading-only.
    ⭐ **EXTENDED 2026-09-19 (`W389`), and binding from `M10`:** every page whose
    material admits a checkable task carries its planned exercises, or the coverage
    report names that page with the gate that refused each one
    ([§7](#exercises-authored-for-every-corpus-w389)). ⛔ **"Reading-only" is a
    reading the gates produced, never a default nobody tried to move.**

### 11.3 The Java corpus, when it is built

Consumer 1's numbers, kept because they are measured and because they are the
worked example the catalogue draws on — **not because the framework's acceptance
depends on them.**

15. All **166** units reach the reading floor, and the root index renders the
    full 10 → 45 → 166 hierarchy.
16. Every exercise that ships has cleared both gates; the coverage report names
    every pair that did not.
17. Run and Submit work from the page against the dockerised Maven toolchain;
    only a passing Submit completes a practice.

---

## 12. Validating that the framework is a framework

Everything in §11 is satisfied by a framework with exactly one consumer. The
claim this project actually makes is larger, and it is only testable against a
source nobody designed for.

**A second source is onboarded after v1 is otherwise accepted.** It is a real
repository, chosen then, and ⛔ **it is deliberately not named in these
documents** — a named target invites the framework to be shaped around it, which
is R1's whole subject. The anonymity is the control.

**How it is conducted.**

- ⛔ **Whoever integrates the second source does not modify `studyforge`.**
  Anything the framework cannot do is filed as a **finding**, not patched. The
  framework's submodule pin does not move during the exercise; where it must,
  every commit it moves across is listed against the finding that forced it. ⭐ A
  test of extensibility run by somebody who can edit the thing being tested
  measures nothing.
- The route is reconnaissance → adapter authoring → corpus onboarding, with no
  hand-authored framework code.
- **The work is planned by the delivery-planning skill** (§9), acting as the
  product owner for that repository: an ordered backlog whose every task ends in
  something demonstrable, so the conversion is watchable step by step rather
  than reported finished at the end. ⭐ Its findings are the deliverable below,
  and it distils them into the integration catalogue so the *third* source
  starts further along than the second.

**What it must assert.**

1. The corpus reaches the Java corpus's floor — readable over `file://`,
   narrated, navigable, read marks recorded — **minus what the source genuinely
   lacks.**
2. ⚠️ **A source with no graders yielding zero exercises is a pass**, not a
   shortfall (§7, C5). This is written down here so the exercise is not judged
   against a corpus that happens to ship 168 test classes.
   ⛔ **DATED 2026-09-19 (`W389`, user direction) — true up to and including `M9`,
   and superseded from `M10`.** ⭐ **Zero is a pass only for material that admits no
   checkable task**; a source with no graders is authored ones
   ([§7](#exercises-authored-for-every-corpus-w389)), and what is then judged is the
   coverage report — every planned exercise shipped, or named with the gate that
   refused it. ⚠️ **The sentence's original purpose survives intact**: nothing here
   is measured against a corpus that happens to ship 168 test classes.
3. The framework pin did not move, or every commit it moved across is accounted
   for.
4. ⛔ **Everything the integrator did by hand is a defect in the onboarding
   skill, named.** That list is what turns "extensible" into something with
   edges.

⭐ **The deliverable is the findings log, not the site.** An exercise that
produces a working study site and reports no findings has not been conducted
honestly — these skills will have seen exactly one source, and the odds that an
unknown repository fits it perfectly are not good. The finding count is the
**yield**, not the failure, in the same sense the exercise-feasibility spike
already uses correctly: a negative result is a successful experiment.

### ⛔ AMENDED PO round 74 — the second source is named, it goes first, and the Java corpus re-validates (user direction, 2026-09-12)

> *"M6 M8 M5 M7 is the order I want also we were supposed to run it against ISO 8583 project first and if it worked and we are sure we are a framework ( now if it worked M5 and M7 should be finished then) and then apply it to java-senior project to revalidate being a framework."*

1. ⭐ **The second source is `ISO-8583-jPOS-tutorial`, and the exercise is `M8`** (`QA-04`). ⛔ **The anonymity clause above is withdrawn for it by the user's own words; the control it bought is the cost.** ⚠️ Q18 had already named it as the track's second finish line.
2. ⭐ **It runs BEFORE the execution track, not after v1 is otherwise accepted.** ⛔ **ISO never enters that track (zero build files, graders and exercises; Q18), so at `M5` and `M7` it passes with zero exercises (§7, C5), and those milestones are proved on the framework's own fixtures.** ⚠️ **DATED 2026-09-19 (`W389`, user direction): that clause is RECORD, and it stands for `M5` and `M7`, which closed under it.** ⛔ **"Never" is now wrong and `M10` is why** — ISO enters the track there, with a practice module and exercises [authored from its pages](#exercises-authored-for-every-corpus-w389), and it is the corpus `M10` is proved on. ⭐ **Its two earlier finish lines are not reopened; `M10` is a third.**
3. ⭐ **`Claude-senior-java-engineer` then re-validates the framework at `M9`** (`QA-05`), ⛔ **under every rule in this section.**
4. ⛔ **The no-patch rule holds for the integrator of `M8` and of `M9`.** ⭐ **Between them, `M5` and `M7` are framework work, and every commit the framework pin moves across is listed (bullet 1 above).**
