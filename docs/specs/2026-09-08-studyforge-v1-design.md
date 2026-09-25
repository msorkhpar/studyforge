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
matter in practice, and where the four shapes carry them:

| Construct | Where it occurs | Consequence |
|---|---|---|
| raw HTML | the SPARQL tutorial, 6 of 19 lessons — `<details>`/`<summary>` | the `disclosure` block, below |
| thematic break | the Java tutorial | the `rule` block |
| blockquote | the Java tutorial | the `quote` block |
| XML inside a fence | the ISO tutorial — build files and configuration samples | a code block, never markup |

⭐ **Fence-awareness, not tag counting**: a reader that scans for `<`
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

These are rulings, not preferences. A change that violates one is not done.

**R1 — The framework knows nothing about any source.** `studyforge` must not
import from, name, or branch on any adapter. Every source-specific fact
arrives as data, through the manifest or the archive.

⛔ **A source's name in framework source is a failure even inside a comment**,
because the next reader takes a name as licence to branch on it. A fixture
under `tests/` that names a *shape* is fine; a file under `src/` that names a
*corpus* is not, a skill's page as much as a module, because it ships with the
framework and is read as the framework's own words. ⚠️ **A name is matched in the forms people actually write it** —
the repository slug, and the corpus named in English (*the Java corpus*) — and
each is anchored on a word only a corpus's name takes: a bare `ISO` is far more
often an ISO 8601 date, and a check that cannot tell the two apart is switched
off within a day. ⭐ The floor's source-names check is the enforcement, so R1 is
answered on every run rather than by a reviewer's grep.

**R2 — The adapter seam is on disk, not in Python.** An adapter's entire
obligation is to write a valid archive. It gets no callbacks and no framework
API. This is what lets adapters be built in any language, tested in isolation,
and written independently of each other. `studyforge validate` is an adapter's
definition of done (§6).

**R3 — Generation is non-destructive, and every exception is declared,
additive and asserted.** No existing file in a source repository is moved,
renamed or deleted. The framework *adds* artifacts alongside the material.

⛔ **An edit to an existing file is permitted only where the corpus manifest
declares it** — `permitted_edits`, naming the file, the exact insertion and why
(§4). An undeclared edit is a build failure. A declared edit that proves not to
be additive — it removes or rewrites an existing line — is **also** a build
failure, so a declaration cannot be used to smuggle a rewrite past the rule.
⛔ **The check reads the declaration**; it never hardcodes one corpus's
exception. An additive `<module>practice</module>` line in a corpus's root
`pom.xml` is one entry in that list, not a special case in the framework.

⛔ **Three edits are never permitted, however declared:** the repository's root
ignore file — new ignore files are written *inside* generated directories
instead; any version-control configuration; and any file the material's own
reader depends on as content.

⛔ **Content is a property of the file in its repository, not of the site's
`content` policy.** A file the policy includes or contests is content, and so is
**repository-root documentation**: a root `README`, `LICENSE`, `LICENCE` or
`COPYING`, of any suffix, which the repository's own readers read whatever the
manifest classifies it as for the site. ⭐ The manifest parser refuses such a
declaration and the non-destructive check a declared change to it, through one
predicate.

⭐ **The reverse of every declared edit is recorded.** An `insert-line`
declaration records the anchor and the line, so its reverse is that line
removed, and onboarding writes an uninstall that performs it (§9). An onboarding
that cannot be undone is one nobody will run against a repository they care
about.

⛔ **R3 distinguishes the build's own prior output from the user's material.** A
file the build wrote last time is the build's own previous answer, and replacing
it is the build answering again. ⭐ **So a rebuild may overwrite exactly the paths
its own generation creates, and which those are is not a guess: `studyforge
plan` enumerates every path a build creates before it creates one** (§5). ⛔ **R3
still protects everything else absolutely** — a hand-edited file, a foreign file,
or any path the enumeration does not name is **refused by name and never
replaced**, and the build exits `1` — ⚠️ and the plan and the build are asserted
to agree path for path, so an enumeration that has drifted from what the build
writes is a failure rather than a licence.

**R4 — Location is data; identity is embedded.** The framework never infers
what a file *is* from where it sits. Every generated artifact carries its own
address inside it, and the server discovers artifacts by scanning.

⚠️ **Precisely: identity survives a move; presentation need not.** A moved page
is still correctly identified, still appears in the contents, still resolves as
the unit it is. Its stylesheet, scripts and sibling audio resolve *relative to
the page* (R8, §5), so a page moved away from its assets renders unstyled and
silent. Both are true and neither is a defect — conflating them would either
force absolute asset paths (breaking the `file://` floor) or force a fixed tree
(breaking placement). Discovery is tested on identity, not on rendering.

**R5 — Nothing generated is presented as more authoritative than it is.** A
grader written against a hidden upstream grader is `advisory`. A grader that
ships with the material is **not** `authoritative` for shipping: it earns that
label only through the derivation in §7, whose record `studyforge validate`
re-reads, and without one it is `bundled` · `advisory`. The framework refuses to
render anything as more than its record supports.

⭐ **A grader authored at ingestion** — tests written from the page, or from the
source's own example code — is `generated`, and therefore `advisory`. It ships
only when it clears §7's [authoring gates](#exercises-authored-for-every-corpus),
whose record ships beside it and which `studyforge validate` re-reads; an
exercise that cannot clear a gate does not ship, and the coverage report names
the gate that refused it and why. ⛔ **There is no third trust level.** Only
`bundled` may be `authoritative`, and a gate record is evidence for a claim,
never a promotion of it. ⭐ **What the reader is shown is a sentence, not the
vocabulary**: `provenance` and `trust` are the framework's internal words, and
§7 fixes the learner-facing wording each one renders as. ⛔ **A label is never
omitted because it is unflattering.**

**R6 — Fail loud, never silently short.** A unit with no content, a broken
curriculum link, an unmatched class, a declared practice that is absent — each
is reported by name and exits non-zero.

⭐ **R6's general form: enumerate the legal, never the illegal.** It is the rule
that most often decides *how* a refusal is written, so it lives beside the rule
that demands one.

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
  second time. ⚠️ A hand-written character blacklist for filenames lets through a
  vertical tab, a form feed, a non-breaking space, a line separator, a quote, a colon
  and an asterisk, and one of them breaks R8's `file://` floor.
- ⭐ **Better still, the illegal value is made unrepresentable**: a key is required to
  be a slug rather than slugified into a possible collision, and a parameter is typed
  so that a leaking value cannot be passed. ⛔ **The tell of the wrong shape is a check
  that grows by one entry every time somebody hits a case nobody thought of.** A list
  that is genuinely right (a sanctioned exception) is short, and each entry carries its
  reason.
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
  vocabulary that no caller can reach is a missing guard.
- ⭐ **A walk over many items gathers every failure and names them in one refusal**,
  leading with the count, so a fix is not one full run per failure.

Where each of these is enforced is recorded in [the decisions file](../decisions.md),
under *Refusals, errors and personal data*.

**R7 — No personal data reaches disk or the wire.** Every string entering the
archive passes `assert_clean`, which **refuses** rather than rewrites. No
absolute home path, account id, name or email in any generated file, log or
report. The rule states the outcome; these are the properties the code holds so
that the outcome never depends on somebody noticing.

- ⛔ **R7 has three subjects: this repository's tracked files, the archive, and the
  rendered page.** A home path that reaches a page has reached a file R7 governs,
  however clean the other two are.
- ⛔ **Every string composed for the archive, a log, a report or an outbound request
  passes the personal-data gate, and the gate refuses.** A gate that scrubs silently
  produces a clean file and a false belief. Narration text is gated before the
  request to the synthesis service is built (§8.2).
- ⛔ **A refusal describes the fault and never formats the value.** A branch that exists
  *because* a value is an absolute path, and prints that value, has taken the one input
  guaranteed to carry a home directory and written it into a log from inside the check
  meant to prevent it. ⛔ **An exception object is never formatted into a message
  either**: `OSError` formats itself with the filename it was given, so a refusal names
  the field it means — `strerror`, `errno` — and says what it knows itself. ⚠️ **The
  rule is blanket, including where one exception type happens to be harmless**,
  because auditing each type at each call site is the work nobody does twice.
- ⛔ **A *why it failed* field carries a code, never a captured stream.** When the
  framework runs another process, the reason it records is an exit code, a timeout
  with its bound, or a failure class — never standard output, standard error, a
  filename or an argument. A captured stream is the richest source of absolute paths
  there is.
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
  at run time. ⛔ Neither is a model for the other.
- ⭐ **One shape vocabulary, two policies.** Those two gates have different subjects and
  may differ in what they do with a match, never in which shapes they recognise. They
  share evidence rather than code: one table, `tests/harness/personal-data-shapes.json`,
  gives every shape a column per gate, and ⛔ **a row whose columns disagree carries a
  `why`**. The rows are measured against the real implementations, so a row that stops
  being true is a build failure. ⭐ The last rows are controls that nothing refuses — a
  table whose every row read *refuse* would be satisfied by gates that refused
  everything — and every spelling is stored as fragments, because a real shape written
  whole into the table would be a finding against the table.
- ⭐ **A lesson's sample data passes when it is unreachable by construction.** The
  archive gate admits two forms and no others: an email address whose domain is
  reserved (RFC 2606's `example.com`, `example.net`, `example.org` and names under
  them; any name under RFC 6761's `.example`, `.invalid`, `.test` or `.localhost`),
  and the placeholder home path, whose account segment is exactly `user` (a slash,
  `home`, a slash, `user`, then anything). ⛔ Everything that identifies a user or a
  machine is still refused: an address on a registrable domain however sample-like
  (`test.com`, `example.co`), every other account segment, the macOS and tilde
  spellings, every local hostname and every token. The admission reads only the
  matched text, so the verdict is the same on every machine, and the reserved names
  are the hygiene sweep's own list, asserted equal.
- ⛔ **A gate's false positive on ordinary source is a defect in the gate.** An author
  who renames a field to get past R7 pays a real cost and leaves no trace, and a checker
  people rename fields around is on its way to being switched off. ⚠️ The shape known to
  be over-broad is the local hostname, which also matches a Python attribute access at
  the end of an expression; its lookahead is narrowed in both gates together.
- ⭐ **A sanctioned negative fixture is the one place a personal-data shape is
  required**, because a gate needs an input to refuse. It is legal only while all five
  hold: the value is fabricated and unreachable (a home path under an account that is
  obviously nobody's and is not the admitted placeholder); it is traceable to nobody on any machine; it lives in one
  named directory whose purpose is to be refused, with a file beside it naming the rule
  and what the gate should say; tests assert both directions — nothing else in the
  fixture tree carries the shape, and the sanctioned value really does trip the gate —
  and the registry of such directories is itself asserted. ⛔ A repository-wide sweep
  excludes that directory and only that one, by name.

**R8 — The site works over `file://` with no network and no server.** Every
asset is local. A served origin adds the API, progress, Run and Submit, and quiz
checking; it is never a prerequisite for reading.

**R9 — Contracts are versioned.** An unknown version is refused, never migrated
in place at read time.

⭐ **The list of versioned fields lives in `studyforge.version.CONTRACT_FIELDS`**,
and the register under R21 says which file each one versions. A contract that
gains a version key is added to the constant in the same change, or the guard
cannot see it. ⛔ **A contract is versioned because somebody reads it, not because
the framework wrote it** — the authored overlay is one the framework only ever
reads, and it is versioned all the same.

⭐ **A version gate checks the type before the value.** `True in {1}` and
`1.0 in {1}` are both true in Python, so a JSON `true` or `1.0` passes a bare
membership test — the one check whose whole job is to refuse a document this build
cannot read. ⛔ The gate refuses a value that is not an `int`, and refuses a `bool`
explicitly because `bool` is a subclass of `int`. ⭐ There is one implementation,
`studyforge.version` (§3.2), and every versioned contract is read through it: one
membership test per contract is one chance per contract to write the porous one.

⭐ **A contract whose document is derived may discard an unknown version instead of
refusing it** — the discovery cache is rebuilt by the scan it caches, so an unknown
`site_api` is reported, not read, and rewritten. ⛔ **A record that is rebuildable
only at real cost refuses** — the narration record would take re-synthesising every
clip, so an unknown `narration_api` stops the run.

⚠️ **A stated limitation: titles must slugify to something.** `slugify` replaces
every non-ASCII-alphanumeric run with a separator — it does **not** transliterate —
so an accented title is mangled rather than converted (`Ströme` becomes `str-me`)
and a title with no ASCII letters at all produces an empty slug and is refused.
⛔ **That is a limitation of this framework, not a defect in the corpus**, and every
refusal says so: R1 means the framework knows nothing about a source, including
which alphabet it is written in. ⭐ Two titles differing only in accented characters
can collide, invisibly in the source, which is why `validate`, `plan` and a build
check generated **names**, not only addresses, and refuse a duplicate path by name.

**R10 — Generated output is byte-for-byte reproducible.** No clocks, no
dependence on filesystem enumeration order. The same inputs produce the same
bytes on any machine.

⚠️ **A content digest in a filename is not a violation of this rule** — it is
deterministic, and therefore reproducible by construction. The rule that bans
digests is narrower, and it is about *churn*: ⛔ **a shared asset linked by
every page carries a plain name**, because a digest there renames a file and
rewrites every page that links it whenever a colour changes. An artifact linked by
**one** page, regenerated in the same run as that page, is not in that class; §8.2
rules on it.

- ⛔ **No clocks and no randomness in anything that reaches a generated file**: no
  wall-clock or monotonic reads, no uuids, no random bytes. A timer used for a log line
  is still a clock if that log is an artifact. ⭐ **There are two exemptions and only
  two:** the archive's `ingested` date, which is excluded from `content_sha256` so it
  cannot make unchanged content look edited (§6); and synthesised audio bytes, because
  a speech model is not byte-stable and the clip is content-addressed instead (§8.2).
  ⛔ **A new exemption is a change to this rule**, never a local decision.
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

**R11 — No file grows past the size a person can hold in their head.** A unit
approaching its ceiling becomes a **package** of focused modules with one clear
purpose each. The test is not line count but the isolation question — *can
someone understand what this unit does without reading its internals, and can its
internals change without breaking consumers?* If not, the boundary is wrong.
Smaller units are also what makes agent work reliable: an agent reasons better
about code it can hold in context at once, and its edits are more accurate in
focused files.

| Unit | Soft ceiling | On exceeding |
|---|---|---|
| source module | 400 lines | split into a package, or justify it in the docstring |
| test module | 600 lines | split along the seam the source split |
| function | 50 lines | almost always a missing helper |
| template file | — | markup only, never logic |

⭐ **A line is a physical line** — what `wc -l` reports — so the floor's arithmetic is
checkable from a shell. ⭐ **The ceiling binds every authored file under `src/`**:
the floor's size check counts Python modules and the stylesheets, scripts and page
templates the framework ships as source, and excludes a vendored third-party file
by its path, each with its reason.

⛔ **The opt-out is one line in a Python module's first docstring, and nowhere
else**:

```text
Size exception: the substitution table is one literal mapping, and splitting it
would hide half the placeholders from the reader of the other half.
```

It begins `Size exception:` at the start of a line, case included, so the checker and
every reader agree on one spelling; it is read from the docstring with `ast`, never
from a comment beside the code, because the exception is recorded where the next
reader of the module meets it; and it says why splitting would be *worse* — a reason
too short to be one is reported as none. ⛔ **It is refused whenever the honest answer
to the isolation question is no**: a justification is not a licence. ⛔ **It is a
design claim and only a design claim**: never a promise that later work will split the
module, which reads to a stranger as permanent and names nothing they can find. The
floor's size check refuses one (`size-deferral`), whether it names a work item or says so
in words, anywhere in the justification. A module that should be split is split. An exception left in a module that is now under its
ceiling is stale and is removed. ⚠️ A stylesheet, a
script or a template has no docstring and so no opt-out: its remedy is a split at a
named seam.

⭐ **A one-way seam is a valid split.** A parser must build the model it defines, so
asking the two halves never to import each other would forbid the split or invent a
third module to hold the constructors. What a one-way seam owes instead: its direction
stated in the package contract, and asserted over the source, including against the
forbidden import written in its relative spelling. Mutual independence is the
strongest form, not the required one.

**R12 — Every module ships with its own tests, and the test tree mirrors the
source tree.** A module without tests is not done. A package's tests are split
the same way the package is, so a failing test names a module, not a subsystem.

`src/studyforge/<path>/<stem>.py` is tested at `tests/studyforge/<path>/test_<stem>.py`,
and a dunder drops its underscores so the name stays readable (`__init__.py` at
`test_init.py`, `__main__.py` at `test_main.py`); the floor's mirror check is the
authority on where a test lives. ⭐ **A package's `__init__.py` is its contract (R17),
so its mirror is a test that imports the package's public names** — what stops the
surface drifting from the code.

⛔ **Two settings are behaviour, not style.** `--import-mode=importlib` in the test
configuration is required: the mirror puts a `test_init.py` in every package
directory, and under pytest's default import mode those collide on module name and
the suite fails to collect before it runs a test. ⛔ **And an ignore rule is checked
against the paths that must stay tracked** as well as those that must not: a pattern
that swallows a fixture gives a suite that passes on the machine that has the file and
fails on a fresh clone, with nothing in `git status` to say why.

**R13 — Markup, styling and scripts are source files, never code strings.**
Templates in template files, CSS and JS in asset files, loaded and composed by
code: changing a colour is a line in a stylesheet, never an edit to Python.
Templates live in `render/templates/`, stylesheets and scripts in
`render/assets/`.

- ⛔ **A template is used exactly, minus one trailing newline** — no reflow, no
  re-indent, no whitespace collapse — because pages are compared byte for byte (R10).
  Markup emitted on one line is authored on one line, however long.
- ⛔ **Substitution fails on an unfilled placeholder**; a placeholder never reaches a
  page as a literal, and a new placeholder arrives with a test of that failure.
- ⭐ **What stays in code is a fragment**: a loop body, an inline wrapper, a one-line
  container — a template file for a closing tag removes no duplication. ⛔ A
  stylesheet, a script, or a whole element with attributes is never a fragment. A
  docstring may show markup; it is not emitted.

**R14** is not assigned. The number is kept free so that R15–R21 keep theirs.

**R15 — Every step whose result depends on installed tooling runs in a
container.** A build of a corpus's code, a test run, a grader verdict, a
synthesis job: each is reproducible because its toolchain is pinned in an
image, not inherited from whoever's machine it ran on.

⚠️ **This is deliberately not "every process runs in a container".** The
framework's own serving process is standard-library only with no dependencies,
so containerising it buys no reproducibility — and it would cost something real:
**the serving process must never receive the Docker socket** (§8.3). Execution
reaches the toolchain container from outside it; the web-facing process is never
the thing holding root-equivalent access to the host.

**R16 — The product is a set of skills, not a bespoke pipeline.** Someone points
a skill at material they care about and gets this format back — pages,
narration, contents, navigation, practices, examples, and their own progress —
and keeps it as their durable personal record (§9).

**R17 — Every package states its contract in its own docstring:** what it does,
how you use it, and what it depends on. A reader who has not seen this document
must be able to use a package correctly from that alone.

- ⭐ **Every package's `__init__.py`, and every module, answers three things in its
  first docstring**: what it does, in one sentence and in this document's vocabulary;
  how you use it — the entry point, not a tour of the internals; and what it depends
  on, with, where it matters, what it deliberately does not. ⛔ `"""Path
  utilities."""` fails. The habit worth keeping is recording *why* a decision was made
  and what it prevents.
- ⛔ **`__init__.py` is the contract.** If a consumer has to import a submodule
  directly, the surface is wrong.
- ⭐ **A name a second package needs is exported on the owning package's `__all__`**
  and imported from the package. A name on no surface is not shared, whatever a
  second package's import says; the fix is to export it, never to reach past the
  surface.
- ⭐ **A reader that deliberately lets another package's exception through exports the
  set as a `RAISES` tuple on its surface**, and a caller catches the tuple whole rather
  than retyping a list from prose, which drops members.

**R18 — Components are separate repositories, and each is consumed only through
its published contract.** The framework, the toolchain images
(`code-server-toolchain`, §8.1), the narration service (`narrate-service`, §8.2)
and each corpus are separate repositories with their own release cadence. ⛔ A
component is never vendored, copied or forked into another.

- ⭐ **A component publishes what a consumer may rely on in one file,
  `consuming.json`**, and the framework reads that file and nothing else of the
  component — never its `Dockerfile`, its README or its own renderer. A value the
  framework needs and the file does not carry is a finding against the component,
  never a value typed into the framework (R19).
- ⭐ **`consuming.json` carries two versions, and conflating them is the defect it
  exists to prevent.** `consuming_api` versions the file's own schema; `provides`
  records **which promise** the component makes. A consumer records the `provides`
  it was built against, and a mismatch is refused, never migrated (R9). A component
  rebuilds constantly without changing its promise, and can change its promise
  without a new build.
- ⭐ **A corpus installs the framework as a library and pins it.** Onboarding records
  the installed library's version and the commit it was built from in the corpus's
  `.studyforge/pin.json`, and the skill stubs it writes name that pin (§9). ⭐ A built
  wheel carries the commit it was built from, so onboarding pins it without being
  told; a source tree carries none, and then the caller names it. ⛔ **Never
  a path to a checkout** — a path carries somebody's home directory (R7), and a
  stranger converting their own material has the installed library, not a
  checkout — and ⛔ **never a git submodule**: nothing here is pushed to a remote, so
  a submodule URL has no legal form.

**R19 — The consuming half of a corpus is generated, not hand-authored.** A
source repository's obligation is the archive (R2) and the source-specific
reading behind it. Everything else a working corpus needs — the manifest, the
ignore rules, the compose file, the toolchain selection, the build entry point,
the non-destructive assertion, the reader's own documentation — is produced by a
skill, from the manifest and from the components' published consuming contracts
(§9). ⛔ **Anything a second source would have to retype is a hole in the
skills**, and a hand-edit to a generated artifact is a **finding against the
skill that should have produced it**, never a fix. Customisation enters as
manifest data.

An orchestration or a deployment that lives inside one consumer is a framework
with one consumer. ⭐ **The measure is what a second source costs**, not what the
first one looks like when finished.

**R20 — The extraction is one-way. This framework mines its source; a consumer
never sees it.** `studyforge` may use CodeSignal freely — it is the extraction
source, and the rulings it paid for are recorded here. ⛔ **A consumer never has
access to it**: everything a consumer needs from CodeSignal is carried **in**
`studyforge` — as a rule, a contract, a skill, or the integration catalogue
(§9) — never as a pointer into CodeSignal's tree. No skill sends an integrator
there to find out how something was done.

⭐ **This framework is the brain.** Knowledge flows *in* from the extraction
source and *out* to consumers, and never sideways between them, for three
reasons: the source is moving, so a consumer reading it inherits whatever it
looks like that week; it does not generalise, so an integrator sent to read one
course site's payload format is taught the wrong thing carefully; and ⭐
**knowledge must accumulate in one place or it decays once per integration** —
if each consumer distils what it learned back into `studyforge`, the *next*
integration starts further along.

⚠️ **This constrains dependencies, not prose.** This document explains *why* a
rule exists by naming what it cost CodeSignal, and that history is what makes a
rule followable rather than arbitrary. What R20 forbids is a consumer's
dependency on the extraction source, or an acceptance that can only be judged by
comparing against it.

**R21 — A contract is located before it is described.** Every document the
framework reads or writes states three things *before* anything builds against
it: **the file it lives in**, **the key that versions it** (R9), and **the one
producer that writes it**. ⛔ **A contract described but not located is a
contract two builders will locate differently**, and R9's versioning cannot
repair it: by the time the disagreement surfaces, one invented location has
shipped inside a version that refuses to migrate. ⭐ A change that meets an
unlocated contract **stops and asks**; choosing quietly is the failure this rule
names.

⭐ **When a file takes a row.** A file takes a row here when a party other than
the one that writes it reads it back — another component, a corpus repository,
or the framework reading what another producer wrote. ⛔ It does not take one
merely for being a file, for being written and read back by its own writer, or
for carrying a version key. ⚠️ **A content-addressed filename does not discharge
a contract whose subject is the conditions the content was produced under**: a
clip named by the digest of its words answers *has the wording changed*, but a
voice change leaves every filename byte-identical while every clip is stale —
which is why the narration record is a located, versioned file rather than an
inference from names.

**The register of located contracts:**

| Contract | File | Versioned by | Written by |
|---|---|---|---|
| manifest | `corpus.json` | `corpus_api` | corpus onboarding, from reconnaissance's draft (§9) |
| container map | `archive/<address>/container.json` | `container_api` | adapter |
| archive document | `archive/<address>/raw/<variant>/unit-NN/<kind>-M.json` | `raw_api` | adapter |
| exercise declaration | the `exercise` key of a `practice-M.json` | that document's `raw_api` | adapter; the exercise bundle's emitter for an authored exercise (§7) |
| authored overlay | `units/unit-NN/content.json`, beside the unit it overlays | `content_api` | a person |
| identity block | embedded in every generated page | `identity_api` | the page renderer |
| served unit | the `/api/v1/content/units/<key>` response | `api` | `unit.builder` |
| contents and local status | the `/api/v1/content/toc` response, and the root index's embedded data | `toc_api` | `contents` |
| discovery cache | `.studyforge/site.json` | `site_api` | `corpus.discovery` — the one writer |
| narration record | `.studyforge/narration.json` | `narration_api` | `studyforge narrate` — the one writer |
| progress record | `.studyforge/progress/progress.json` | `progress_api` | `progress` — the one writer |
| framework pin | `.studyforge/pin.json` | `pin_api` | corpus onboarding |
| install record | `.studyforge/installed.json` | `installed_api` | corpus onboarding |
| execution record | `.studyforge/execution/written.json` | `written_api` | execution onboarding — read by onboarding's hand-edit check |
| exercise bundle | `exercises/<address>/<variant>/unit-NN/practice-M/bundle.json` | `bundle_api` | the exercise-authoring skill |
| gate record | `gates.json`, in the practice's directory under `exercises/` | `gates_api`; a record with no key is read as `1` only in its earlier three-key shape (`inputs`, `origins`, `gates`), and any other record without it is refused | the exercise-authoring skill, and an adapter that derives an exercise (§7) |
| source ledger | `exercises/ledger.json` | `ledger_api` | the exercise-authoring skill |
| coverage report | `coverage.json`, one per unit beside its bundles | `coverage_api` | the exercise-authoring skill |
| personal archive manifest | `personal-archive.json`, a member of the archive file | `personal_archive_api` | the personal-archive skill |
| component consuming contract | `consuming.json` | `consuming_api` + `provides` | each component |

⭐ **`CONTRACT_FIELDS` is the framework's subset of this register**: every version
key the framework writes, the skills' records among them, and each reader of one
checks it through `studyforge.version` and never compares it by hand. Two keys
version a part of a row rather than a row of their own: `plan_api` versions the
plan inside a coverage report, and `quiz_api` versions a quiz's own document,
`tests/quiz.json` inside its bundle.

---

## 3. Architecture

### 3.1 The workspace

The system is several repositories, each consumed through a published contract
and never copied into another (R18):

```text
studyforge/                 the framework: a library, its command, and the skills (§9)
code-server-toolchain/      the runner and editor images (§8.1)
narrate-service/            the synthesis service (§8.2)
<corpus>/                   one repository of material, per corpus
  corpus.json               the manifest (§4)
  archive/                  what the corpus's adapter writes (§6)
  exercises/                authored exercise bundles, where the corpus has them (§7)
  .studyforge/              what the framework generates and records for it
```

A corpus installs the framework as a library into the Python that runs its
checks, and records the version it installed in `.studyforge/pin.json` (R18).
It reaches the images and the service only through what their `consuming.json`
promises: it builds each component's image from that component and records the
tag the build prints, and it records the `provides` it was built against. ⭐ **A
change to a component is released by that component**, and a consumer moves to
it by rebuilding and recording the new tag. ⛔ The framework locates no sibling
checkout at run time; only its own test suite may be pointed at sibling
checkouts, through the `STUDYFORGE_WORKSPACE` environment variable.

### 3.2 Inside the framework

Every unit below is a **package** of focused modules, not a file (R11). The
tree names responsibilities; each package's `__init__.py` states its contract
(R17).

```text
src/studyforge/
  version.py     the R9 gate: one implementation of "is this a version I speak"
  describe.py    how a refusal names a value without reproducing it (R7)
  address/       logical N-segment address, keys, slugs, identifiers
  corpus/        manifest · container map · placement profiles · discovery · media policy
  archive/       the archive document · block vocabulary · Markdown reader
                 · the personal-data gate
  unit/          the served unit document · authored overlay · section keys · trust
  contents/      table of contents and local status, as data
  generate/      one corpus's whole site, written in one pass
  render/        page renderer · container pages · root index · templates/ · assets/
  narrate/       speakable contract · the synthesis client and its record
  serve/         app · content, state, assets, run and quiz routes · security · caching
  execute/       the command runner — the only package that runs a corpus's commands
  progress/      the reader's record of practice passes
  exercise/      the exercise record, its states, the bundle, the gates, quizzes
  validate/      what "a valid archive" means, and the command that decides it
  cli/           validate, plan, narrate, build, serve, check — the command's verbs
  skills/        the authoring and conversion skills (§9)
tests/           mirrors src/ package for package (R12), plus the floor
docker/          the development image the gates run in (R15)
```

**Dependency direction is one-way.** `studyforge` never imports a consumer. A
consumer never imports `studyforge` internals — it writes an archive and
invokes the command, or runs a skill.

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

A unit's address is a single joined key, so its segments cannot be swapped,
with exactly `len(levels)` segments: the corpus declares how deep it is, and
every address in it has that depth.

```json
// corpus.json — what makes a directory a source
{ "corpus_api": 6,
  "source": "java-senior",
  "title": "Senior Java Engineer",
  "levels": ["section", "module"],
  "variants": ["java"],
  "exercises": true,
  "runtimes": ["java", "maven"],
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

### The complete key list — the example above is an instance, not the contract

⚠️ **A realistic manifest omits the optional keys it does not need**, so the
example is not where you learn what a manifest *may* carry. This list is.

| Key | | Notes |
|---|---|---|
| `corpus_api` | **required** | R9's version key. An unknown value is refused, never migrated. ⭐ **`2` added `content.not_material`**, **`3` added `media.max_files`**, **`4` added `runtimes`**, **`5` added `narration`**, **`6` added `onboarding_doc`** and **`7` added `curriculum`**; this build reads `1` to `7`, and a key used under a version older than the one that added it is refused naming both numbers |
| `source` | **required** | ⛔ **A corpus id, not a fetch URL** |
| `title` | **required** | |
| `levels` | **required** | Names the *container* levels and fixes the depth |
| `variants` | **required** | ⛔ Filing and presentation only — never *runnable* |
| `curriculum` | *optional* | Where the curriculum is recorded (`record`), the address each of its groups is filed at (`containers`), and per group an optional filename `prefix` that is a declared cross-check and never files a unit |
| `exercises` | **required** | §7's gate onto the execution track |
| `runtimes` | *optional* | Names, never versions, from a closed vocabulary. ⛔ **Absent means none: no runner, complete at the reading floor** (§7, C5) |
| `narration` | *optional* | Whether a build and a serve voice the corpus. ⭐ **Absent means voiced whenever clips are recorded**; ⛔ **`false` is the reading floor exactly, complete and never short** (C5) |
| `onboarding_doc` | *optional* | Where onboarding writes its reader document: a corpus-relative `.md` path, or `false` for none. ⭐ **Absent means `ONBOARDING.md` at the root** |
| `placement` | **required** | `tree` or `sibling` (§5) |
| `content` | **required** | `include` is plain globs; every `exclude` and every `not_material` entry carries its `why` |
| `media` | *optional* | Defaulted (§5). ⛔ **A corpus with no media declares nothing** |
| `permitted_edits` | *optional* | Defaults to `[]`, which is the normal case (R3) |

⛔ **The contract is `MANIFEST_KEYS`, `REQUIRED_KEYS` and `KEY_VERSIONS` in
`corpus/manifest/document.py`.** This table names every key the code has and no
key it lacks, and marks *required* exactly the keys in `REQUIRED_KEYS`; a test
holds it to both, each way. It is not derived from the example, and the example is deliberately
not exhaustive: onboarding **generates** manifests, and an exhaustive example
would propagate every optional key into every corpus, where R9 freezes it at
first declaration.

### `content` — what is read, what is withheld, and what is not material

`content` is **C2's countermeasure, and it is a schema field because C2 is a
schema problem.** A source that ships per-unit files *and* aggregates that
concatenate them is ingested twice by a plain glob, and nothing complains.

```json
"content": {
  "include": ["src/*.md"],
  "exclude": [
    { "path": "src/All.md",
      "why": "whole-series aggregate: a concatenation of the per-unit files (C2)" } ],
  "not_material": [
    { "glob": "docs/studyforge/*",
      "why": "this integration's own working notes about the corpus, not the corpus" },
    { "glob": "LICENSE",
      "why": "the repository's licence; it teaches nothing and is not withheld from anyone" } ] }
```

The three states are about whether a file's prose is read into the archive:

- `include` — **read in.**
- `exclude` — **prose that *would* be read, deliberately not read**, one named path
  per entry, with its `why`. *Withheld* is the honest word here because it is true
  here.
- `not_material` — ⛔ **not prose to read at all**: the repository's own
  scaffolding, content *about* the material rather than the material — a licence,
  ignore files, an editor workspace, the corpus's own `README.md`.

⭐ **X1 — an inclusion needs no justification; every declaration that the
framework will not read a file needs one.** An excluded file is material being
withheld from the reader, and a withholding nobody has to explain is one nobody
audits — the same argument `permitted_edits` makes about an edit.

⭐ **A source `README.md` is `not_material`, and it is not a special case** — it
is the corpus's own navigation, and navigation is scaffolding. ⚠️ The reader
loses nothing: the site carries its own contents from the container maps.

⚠️ **`not_material` takes globs where `exclude` takes one named path**, because the
harms differ. A new member of an exclusion's set is a new withholding and needs its
own reason; a new member of a `not_material` glob's set is not a harm **unless it is
actually material** — which is caught per file, against a real tree:

- ⛔ **A file matched by both `include` and `not_material` is `contested`**, a
  finding of its own that exits 1. **Never a precedence** — one order would drop
  material the reader was promised and the other would read the scaffolding aloud.
- ⛔ **A `not_material` entry is either an exact path, or a glob whose wildcard lies
  inside a directory prefix that is itself entirely not-material.** A pattern whose
  correctness depends on which files happen *not* to exist is refused, however
  exactly it matches today: `docs/studyforge/*` is a wildcard under a directory,
  `LICENSE` and `.gitignore` are exact paths, and `[CLR]*` is refused, because a
  `why` cannot be true of a `CHANGELOG.md` nobody has written yet.
- ⛔ **A file under the source root that matches none of the three is
  `unclassified`**, and `studyforge validate` names it and exits 1 (R6). A file
  that matches `include` and is then not ingested is also a failure. It follows
  that a corpus cannot grow a file without someone deciding what it is — the
  alternative is a second aggregate appearing and being read as a second copy of
  every unit.

⭐ **The reconnaissance skill (§9) drafts this**, and detecting an overlap is what
C2 asks of it: two files whose content says one contains the other is a finding it
reports, not something left to be noticed after ingest.

### `curriculum` — where the reading order is recorded, and how its groups are filed

An optional top-level key, added by `corpus_api: 7`, for a corpus whose own
document records its reading order and grouping:

```json
"curriculum": {
  "record": "README.md",
  "containers": [
    { "label": "jPOS Server Implementation", "address": "jpos-server", "prefix": "s" }
  ]
}
```

- ⭐ **`record`** is required inside the block: the Markdown document, inside the
  corpus, that records the reading order and the grouping. `{"record": …}` alone is
  a complete declaration.
- ⭐ **`containers`** lists the record's groups in the record's order: each `label`
  exactly as the record writes it, and the `address` that group is filed at, checked
  against `levels`. This is what an adapter would otherwise carry as a constant, and
  a second corpus would retype (R19).
- ⛔ **`prefix` is a declared cross-check, never what files a unit.** The record
  files every unit; the prefix — the text before the number in a group's filenames,
  which may be empty — is a second partition of the same files, and the adapter
  skill's filing refuses when the two disagree, in either direction. A filename
  prefix is never a source of grouping on its own (C1, §6: an address is recorded,
  never derived).
- ⛔ **Strict by design**: the block and each group are closed key sets, and a
  repeated label, address or prefix is refused. Reconnaissance drafts the block,
  proposing addresses for a person to confirm, and writes a prefix only where the
  filenames partition the units exactly as the record does.
- ⭐ **Absent means no declared curriculum**, and the adapter files units as it
  always has.

### `runtimes` — what a corpus's material needs to run

An optional list of names from a **closed** vocabulary — `gradle`, `java`,
`kotlin`, `maven`, `node`, `python`, `shell`, `sqlite` — which agrees name for
name with what `code-server-toolchain` pins (§8.1). ⛔ **Names only, never
versions**: the corpus says *which*, the component's pin file says *which
version*, and a version here would be a second place one is chosen.

- ⭐ **Order carries no meaning**; the manifest holds the set sorted, so two equal
  declarations are one value (R10). A repeated name is refused.
- ⛔ **`maven`, `gradle` and `kotlin` are refused without `java`** in the same
  list — nothing is inferred.
- ⛔ **Refused beside `exercises: false`**: it would declare a runner for a corpus
  with nothing runnable (§7).
- ⭐ **Absent means none, and none is complete.** The framework neither builds,
  probes nor starts a container for such a corpus; `exercises: true` without
  `runtimes` is an ungraded corpus's honest shape.
- ⭐ **The vocabulary is spelled once**, in `corpus/manifest/runtimes.py`.

### `narration` — whether a corpus is voiced

Narration is optional. Somebody may want to read a course without voices, and a
corpus whose clips were synthesised may still be served silent.

- ⭐ **A top-level bool.** The onboarding skill asks the author and writes the
  answer; a draft that carried none writes no key.
- ⭐ **Absent means voiced**: a unit's page plays the clips its narration record
  locates, and a clip the record promises and the disk does not have is reported
  on the page — ⭐ **unless no clip is on disk at all**. Then the clips are a
  download nobody has taken (§5, on delivery): every page links the clips its
  record names, reports none of them missing, and shows no narration control
  until they arrive.
- ⛔ **`false` is the reading floor exactly, whatever the record says**: a build
  reads no record, renders every page with no player and no gap notice, and
  copies no clip. ⛔ **Nothing is deleted, moved or rewritten** (R3): the record and
  the clips stay where `studyforge narrate` put them, so voicing the corpus again
  plays them with no re-synthesis.
- ⭐ **A build names what it will not act on, and its exit does not change.** A voiced
  build reports each clip it plays whose words its paragraph no longer says
  (`stale`), pointing at `studyforge validate`, which lists each one with the
  `narrate` command that re-voices it. A build with narration off into an `--out`
  an earlier voiced build used reports each clip left there that no page links
  (`unlinked`), and says how to be rid of it. ⛔ A build deletes neither.
- ⭐ **`studyforge build` and `studyforge serve` take `--narration` /
  `--no-narration`**, which override the declaration for that run, and the
  build-and-serve skill asks for it. ⛔ **Narration is in a page's bytes** (R8: the
  built page is the product), so `serve` never edits a page on the way out: with
  narration off it refuses a site built with narration, naming each page and the
  build that fixes it, and it refuses every clip file under the root it serves.
- ⛔ **Off is not degraded**: no page, report or `validate` finding calls it
  short, and practices, quizzes, progress and contents are unchanged.

### `levels`, `variants` and `permitted_edits`

`levels` names the **container** levels and fixes the depth. A unit is an
ordinal inside the deepest container. `levels` also supplies the **display
labels** the breadcrumb and index use, so one site says "Section › Module ›
Lesson" while another says "Path › Course › Unit", from data.

| Shape | `levels` | example address |
|---|---|---|
| one course | `["course"]` | `sparql-tutorial` + unit 07 |
| sections of modules | `["section","module"]` | `concurrency/23-executors` + unit 02 |
| paths of courses | `["path","course"]` | `kotlin-programming-for-beginners/getting-started-with-kotlin` + unit 03 |
| groups | `["group"]` | `iso-fundamentals` + unit 02 |

Depth is uniform **within** a source; a ragged source is normalised by its
adapter. A free node tree would turn every flat contract downstream — progress
keys, hrefs, editor task files — into a tree walk, for flexibility no known
source needs.

⚠️ **`variants` is a filing and presentation key, and nothing more.** It says
how the archive is partitioned and what a variant selector offers the reader.
⛔ It never implies that anything is buildable, runnable or gradable — that is
declared per exercise (§7) — and it is **not** a code fence's language, which is
a block's own attribute in the archive. One list answering both *"can this be
filed here?"* and *"can we generate a test for it?"* means a language with no
grader cannot be filed at all. Three questions, three answers, none derived from
another.

⛔ **A single-variant prose corpus declares `variants: ["prose"]`: the word is the
framework's, not each corpus's.** Every corpus names at least one variant, and a
word each corpus invents for the same case is a different label in the one
variant selector. ⭐ Reconnaissance proposes it — `SINGLE_VARIANT` in
`skills/reconnaissance/proposal.py` — and a person confirms it.

`permitted_edits` is R3's declaration: the complete, enumerated set of existing
files this corpus may have added to, each with its insertion and its reason.
The one kind is `insert-line`. An empty list is the normal case, and it is the
one a purely additive source keeps.

---

## 5. Placement and discovery

**Placement is a policy**, declared per corpus, mapping an address to physical
locations. Two profiles ship:

| Profile | Where a unit's page and its files go |
|---|---|
| `tree` | under one generated root, `.studyforge/`, in directories that spell the address, with `units/unit-NN/` below the container |
| `sibling` | in a `study/` directory beside the source file the unit was generated from |

`tree` is for material with no layout worth preserving. `sibling` is for a
repository whose layout the reader already knows, which R3 forbids
restructuring:

```text
my-java-course/
  index.html                                   the root index
  corpus.json
  archive/<address>/raw/java/unit-NN/lesson-1.json   the archive (§6)
  .studyforge/assets/                          the shared stylesheet, script, faces and player,
                                               and narration-clips.js: whether the clips are here
  16-streams-api/
    README.md                                  untouched
    README_4.4.1.md                            untouched
    study/
      streams-api.section.html                 the container's page
      basics.16-streams-api.unit-02-introduction-to-the-streams-api.unit.html
      audio/basics.16-streams-api.unit-02-introduction-to-the-streams-api/
      practice/basics.16-streams-api.unit-02-introduction-to-the-streams-api/
```

- ⭐ **The archive root is `archive/`, beside `corpus.json`, under every profile.**
- ⭐ **Under `sibling`, everything generated lands in one `study/` directory beside
  its source file, never loose in that directory.** A source directory gains
  exactly one name; its media sits one directory per kind under `study/`, with the
  unit's stem below that, so many units can share one `study/`. The only
  generated file at the corpus root is `index.html`.
- ⭐ **Every generated page carries a real name, never `index.html`.** A scanner
  reads names and a reader browses directories, and an `index.html` is neither
  unique in a listing nor distinguishable from the root index. A unit's name is
  its label — the corpus's own numbering where the container map records one,
  otherwise `unit-NN` — and its title's slug; a container page is named from its
  deepest title.
- ⛔ **Under `sibling`, a unit's page and media names begin with its container's
  address, dot-joined** (`basics.16-streams-api.` above, for a unit at
  `basics/16-streams-api`). Where many units share a directory, numbering and
  title alone are not unique: two containers whose series mirror each other would
  give two units one name. A slug carries no `.` and depth is uniform, so two
  containers never share a name. What one container still repeats (one label,
  one title) is refused by name, by `validate`, `plan` and a build.

**Where a build writes is the corpus owner's decision.** `studyforge build`
takes `--out` with no default, and `studyforge serve --site` serves what it
wrote; a default would answer by convention what only the owner can. A build
into the corpus root lays the site out exactly as the placement profile says.

**Discovery replaces path inference.** The server scans a root for
`*.unit.html` and `*.section.html`, reads each file's embedded identity block,
and assembles the site from what it finds. Consequences, all intended:

- The framework does not care where artifacts are; a corpus may place them
  wherever the reader finds natural.
- A moved or renamed artifact still identifies itself correctly.
- Two corpora with different placement profiles are served by one server.

⛔ **`site.json` is a cache of that scan, never the authority.** The scan runs
every time and its result is what is returned; no branch hands back a cached
site. A stale cache is detectable by a content digest recorded in it, never by a
modification time. ⭐ **The cache is this machine's, and it is ignored where it
sits**: the framework writes an ignore file inside `.studyforge/` for it, never
a line in the repository's root ignore file (R3), so serving a corpus leaves its
working tree unmodified.

Assets and audio resolve **relative to the page that references them**, so a
unit page opened directly from `file://` works with no server and no rewriting
(R8).

⛔ **Delivery is orthogonal to placement, and an href never encodes how a file
arrived.** A generated artifact is addressed relative to the page that
references it, and that address is the same whether the file was generated
locally, committed, or restored from somewhere else. Any delivery mechanism
moves the same bytes to the same paths. ⚠️ CodeSignal proved this in reverse:
when its media left git for release assets, the layout on disk did not move and
every page still addressed a clip as plain `audio/<clip>.mp3` — which is the only
reason that change was a script rather than a re-render of every page.

⭐ **A page learns whether its clips arrived without asking for a clip.** A
request for a file that is not there is an error in the browser's console, over
`file://` and served alike, and a site whose clips are a download is often
opened before anyone has fetched them. ⛔ So a narrated page never probes a clip:
it links `.studyforge/assets/narration-clips.js`, a script that is always there,
and shows its narration controls — the transport and the passages that answer a
click — only when that script says `present`. The script says one of three
things, and what writes it is what moved the clips:

| writer | says |
|---|---|
| a build | `present` or `absent`, from the disk; ⛔ never over `released` |
| the release pack, as the clips become a download | `released` |
| the restore, once the clips are back in place | `present` |

⛔ **A build never turns `released` into `present`**: the author who packed the
clips still has them on disk, and a site committed from that disk must tell a
fresh checkout they are not there. ⭐ **Served, the server answers the same
request from the disk as it is at that moment** and rewrites nothing, so a
served page is right whoever last wrote the file. ⭐ Because a page built with no
clip on disk already links every clip, a restore is heard on the next page load,
with no rebuild.

### Generated media and pages are committed

⭐ **Generated media is committed by default.** *Regenerable is not the same as
available*: a clone that carries its own audio speaks with no synthesis service,
no GPU and no network, and that is what R8 is for. ⭐ **A build's pages, the root
index and the asset bundle are committed too**, for the same reason: a clone that
ignores its pages has no reading floor. ⛔ **So the only generated ignore rules
about a corpus are the media policy's and the machine-local ones**, written inside
the generated directory they are about and never in the root ignore file (R3).

⛔ **The default has a ceiling, and crossing it is a decision, not an accident.**
Narration is the largest thing this framework generates, and a corpus can outgrow
what a git remote will take — a repository limit of a few gigabytes, a per-file
block of 100 MiB — and find out only when a push becomes impossible, after the
history already holds the blob. So the policy is manifest data:

| `media` key | Meaning |
|---|---|
| `commit` | `auto` (the default) commits while the media fits and stops when it does not; `always` commits whatever the size; `never` is a corpus that holds its narration clips elsewhere: only the clips' `audio/` directories are ignored, and the copies of images, video and attachments a page shows stay committed, because they copy files the archive commits |
| `max_total_bytes` | the total ceiling, `auto` only; defaults to 5 GB |
| `max_file_bytes` | the per-file ceiling, `auto` only; defaults to 100 MiB |
| `max_files` | the file-count ceiling, `auto` only; **no default** — unstated means unbounded, and the count is measured and reported either way |

The footprint is **measured**, by `studyforge plan` and again by a build after it
copies media, and a corpus that crosses a limit **stops and says so**, naming the
number and the limit, and the build exits `1`. ⛔ It never silently switches to
ignoring media, which would produce clones that are silent with no error, and it
never silently keeps committing.

⭐ **A corpus that does not commit its clips publishes them as release volumes.**
Delivery is orthogonal to placement, so the mechanism plugs in behind the same
decision without touching a page:

- **`studyforge narrate <root> --pack <dir>`** packs every clip the narration
  record locates, at the path the record names relative to the corpus root,
  into one **stored** zip split into volumes of **at most 999 MB**, with a
  `SHA256SUMS` over the volumes, in a directory outside the corpus. Clips are
  already compressed, so the split is what matters, not the compression. ⛔ A
  pack is **deterministic** (sorted members, one timestamp, fixed permissions,
  no attributes of the machine), and a clip the record promises and the disk
  lacks is refused before anything is written. ⛔ **Only a corpus whose
  `media.commit` is `never` is packed**: one that commits its clips already
  hands every clone the clips, and a pack would mark them `released`.
- **The pack writes two restore scripts into the corpus**,
  `.studyforge/narration-release/restore.sh` and `restore.ps1`, with the tag
  filled in and nothing else. ⛔ **No account name is in either**: the
  repository is read from the checkout's `origin` when the script runs, and a
  placeholder is the default. A restore downloads the volumes (the public
  download address, or for a private repository the API by asset id with
  `GITHUB_TOKEN` or an authenticated `gh`), **checks every volume against the
  digests the pack committed beside the scripts** (never only against the
  release's own `SHA256SUMS`, which proves a download intact and not that the
  release belongs to this corpus), refuses a zip whose members are not exactly
  the committed `clips.sha256` paths, extracts into a staging directory, checks
  each clip's committed digest, moves each to `<corpus root>/<where>/<filename>`
  as the record names it, and deletes the downloads. ⛔ A restore writes no file
  that is not one of the corpus's clips, and a refusal leaves the corpus as it was. The token is read from the
  environment and never written or printed. A second run gives the same tree.
- ⭐ **The pack sets the clip signal to `released`** and **the restore sets it to
  `present` as its very last step** (`.studyforge/assets/narration-clips.js`,
  §8.4), so an interrupted restore never claims the clips arrived. A site built
  into another `--out` holds its own copies and its own signal, and is built
  again after a restore.
- ⛔ **The upload is the owner's.** `studyforge narrate <root> --publish <dir>
  --tag <tag>` is a dry run: it checks every volume against `SHA256SUMS`,
  refuses a clip signal that does not say `released`, reads
  the repository from the checkout's git configuration, and prints the one
  `gh release create` command, which the owner runs with their own `gh` login.
  ⛔ The framework starts no process for it and uploads nothing (§8.3). A tag's
  release is created once, so the dry run also prints how to go on when it
  exists: a new tag, or the `gh release upload --clobber` that replaces its
  assets. Scripts an earlier framework rendered for the same tag are refused
  as exactly that, and the corpus is packed again.
- ⭐ **Narration stays optional**: a clone that never restores is the reading
  floor, complete, and the onboarding guide says how to get the clips.

### The placement dry-run

A consumer cannot write its ignore rules, declare its `permitted_edits` (R3) or
review an onboarding without knowing every path the framework will create. So
placement is **askable before it is exercised**:

```text
studyforge plan <root>
```

prints, from the manifest and the container maps alone and before anything is
generated, every path a build will create or replace, every directory it claims
for media, every path it expects another command to write, the files it will
edit and the declared reason for each, the ignore lines it needs, and the media
policy with its measured footprint. It is what the onboarding skill renders
ignore rules from, what the non-destructive check asserts against, and what lets
a person read what is about to happen to their repository before it happens.
⛔ **The plan and the build agree path for path**, and that agreement is
asserted (R3).

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

`<archive-root>` is `archive/`, beside `corpus.json` (§5). ⛔ **A file under the
archive root that is not a member of this layout is refused by name
(`archive-stray`), never skipped.**

### The container map

```json
// container.json — one per container
{ "container_api": 3,
  "address": ["concurrency", "23-executors"],
  "titles":  ["Concurrency", "Executors and Thread Pools"],
  "variant": "java",
  "ingested": "2026-09-08",
  "origin": "23-executors/README.md",
  "note": "…",
  "units": [ { "n": 1, "title": "Thread pools and the Executor framework",
               "practices": 1, "origin": "23-executors/README_5.1.md",
               "label": "5.1", "note": "…" } ] }
```

- ⭐ **`origin` is called `origin` and not `source`**, because `source` is already
  the corpus's own identifier in the manifest.
- ⭐ **A unit's `origin` is a whole file, or a region of one**: a string names the
  file; an object `{"path": …, "section": …}` names the region that opens at that
  heading (`container_api` 2). ⭐ **`practice_origin`** names a second file holding
  that unit's practice documents, where they are not in the file its prose came
  from (`container_api` 3). A web source that has no file records its own
  addressing as `url_slug` instead. `label` is the corpus's own display numbering
  for the unit.
- ⭐ **One variant per container**, so a map can never promise one variant while
  the archive holds another.
- ⭐ **Who writes it — one answer.** The adapter generates it on ingest. A person
  may amend exactly the editorial fields — `title`, `titles`, `note` — and a
  generator round-trips them rather than overwriting them; a generator that would
  discard one **stops** (R6).
- ⚠️ **`ingested` is a date, and it is exempt from R10.** It answers *how stale is
  this capture?*, and it is excluded from `content_sha256`, so it cannot make
  unchanged content look edited. Reproducibility is stated as *"identical bytes
  apart from `ingested`"*, never silently.

### The archive document

A `lesson-M.json` or `practice-M.json` carries the unit's identity (`source`,
`address`, `variant`, `unit`, `kind`, `ordinal`), its `ingested` date and
`title`, its `blocks`, its `video`, `assets` and `attachments`, the per-type
`counts` of its blocks, and `content_sha256` over the blocks; a practice
document may add the `exercise` record (§7). ⛔ **A key the format does not
define is refused**: an unknown sibling of `blocks` is outside the digest, and
a typo'd key is a grader that is invisible while the corpus passes.

**The block vocabulary** is `archive/blocks.py`'s table, and a new block type is
a `raw_api` change: `heading`, `para`, `code`, `table`, `list`, `image`,
`video`, `rule`, `quote`, `html` and `disclosure`. `quote` and `disclosure` hold
blocks; every walker recurses on that property rather than naming the two.

- ⭐ **A list item is a string, or an array of its parts in reading order** — runs
  of text, whole nested `list` blocks, whose items follow the same rule, and whole
  `code` blocks. A part is part of its item, not a block in reading order, so
  `counts` does not count it. ⭐ A step, its snippet and the sentence after the
  snippet stay one item: closing the list around the code would detach that
  sentence. The page shows the code inside the item, and the item's clip speaks
  the code's one caption where the code sits.
- ⭐ **An ordered list keeps the number it starts at**: a `list` may carry `start`
  after its three fields, written only when the list is ordered and does not
  start at `1`. The page opens the list at it and the narration counts from it.
  A list that starts at one carries no `start`.
- ⛔ **Raw HTML is the `html` block**: the Markdown reader emits it for a run of
  block-level markup, and the page renders it **verbatim** — the one block type
  that bypasses escaping, by declaration and never by what its text looks like. A
  tag-shaped line the reader keeps as a `para` is still escaped.
- ⭐ **`disclosure` is content present but withheld** (C3): a `summary`, whether it
  starts `open`, and the blocks it holds. That its markup is `<details>` is the
  renderer's decision, not the archive's.
- ⭐ **A `code` block's `lang` is the fence's own info string**, and an empty one
  renders as plain text (§8.4).

⭐ **An optional key is written only when it says something, after the keys every
document carries**, so a document that does not use it is byte-identical to one
written before it existed. That is the test that decides whether a new key is a
`raw_api` change: every document valid before is valid after and means what it
meant, and an older build refuses the new shape rather than misreading it.

### What the archive records about its material

**Attachments** (C4). A unit may reference files that are neither prose nor
inline media — a dataset a lesson loads, a notebook, a sample document. They
are archived alongside the unit and placed by the placement policy, and the
page links them for download rather than rendering them. Distinct from media,
which the page displays.

**Provenance.** `origin` is written by the adapter, carried into the served unit
document **verbatim**, and rendered by the page and the index. It is optional,
because a corpus may be its owner's own material; where it exists it is **not
optional chrome**, because material that came from somebody else is credited on
the page that shows it. ⭐ For a repository-shaped source, R3 guarantees the
original file is never touched, so an `origin` pointing at it is a permanent,
working link from every generated page back into the reader's own material.

⛔ **An address is recorded, never derived.** It is recorded by the container map,
and a group's address may also be recorded in the manifest's `curriculum` (§4),
which is still a record and never a derivation. Composing an address from a title
is the tempting shortcut and it is wrong: on a real course catalogue, a
sizeable share of units is served at a slug its title does not produce, so a
derivation sends those links to pages that are not there. Where two
records name an address for the same unit — a container map and an archive
document — a disagreement is a **refusal** (R6), never a preference: one would
be linked from the page and the other from the index, and the reader would be
sent to two different places with nothing failing.

**Re-ingest.** `content_sha256` covers a unit's blocks and answers one question:
*did the source change since we read it?* On re-ingest, a digest that disagrees
means the material was edited upstream: the archive is **replaced** and the
change is **reported** (R6) — never silently overwritten, and never silently
kept — and anything derived from that unit (pages, narration, exercises) is
invalidated by the same signal.

⛔ **A generator stages beside its target, validates, then moves into place.** A
document that fails its own validation is **never** left at the path something
else will read: one unreadable container map halts every consumer that walks
the tree, and the failure is then reported at the reader rather than at the
writer that caused it. A reading that can be taken again is not worth a file
nothing can load.

### `studyforge validate` is the definition of done

`studyforge validate <root>` decides whether a corpus's archive is valid, for
any adapter, and exits `1` naming every failure. Among what it checks: the
manifest parses and `corpus_api` is known; every file under the source root is
classified by `content`, nothing is `contested`, and everything included was
read in full; every `container.json` address matches the directory holding it,
and every `origin` resolves to its file and, for a region, to exactly one
heading; every archive document parses, carries a known `raw_api`, holds only
the layout's files, and its `content_sha256` matches its blocks; `assert_clean`
passes on every string; unit ordinals are contiguous from 1; declared practice
counts match what is present; no two artifacts claim one generated path; every
exercise record is well formed and R5's pairs hold; every authored exercise's
bundle holds only its permitted files and its gate record verifies against them
(§7); the source ledger accounts for every page; and the narration record agrees
with the clips and the words they speak, unless the run is given
`--no-narration`.

An agent building an adapter therefore has a green/red signal that depends on
nobody's judgement.

---

## 7. Exercises

### The contract

A unit carries zero or more exercises, and an exercise is in one of **three**
states (C5):

| State | What it is | Can complete a practice? |
|---|---|---|
| **none** | the unit teaches, it does not set work | — |
| **ungraded** | a prompt the reader works, with nothing to check it | **no** |
| **graded** | a workspace plus a grader, `authoritative` or `advisory` (R5) | only on a passing grader run |

**Ungraded is why this matters.** A lesson that ends in a prompt nothing checks
still sets work; recording it as "no exercise" would delete it from the reader's
material to satisfy a two-state model. It is presented as work, clearly marked
as unchecked, and it never completes anything. Zero exercises remains a
**first-class outcome**, not a degraded one.

A graded exercise declares its workspace — `main_path`, `test_path`,
`run_command`, `test_command` — plus `provenance` (`bundled` | `generated` |
`user`) and `trust` (`authoritative` | `advisory`). ⛔ Only `bundled` may be
`authoritative`, and only with a derivation record behind it (§7); the framework
refuses to render anything else as authoritative (R5).

### Where that declaration lives

⛔ **It is an `exercise` object inside the practice archive document** —
`<archive-root>/<address>/raw/<variant>/unit-NN/practice-M.json` — versioned by
that document's `raw_api`, and written by the **adapter** (R2).

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

- **No new document and no new version.** A contract that rides a version it is
  already inside is strictly cheaper than one that adds another.
- **The adapter is the only thing that knows.** `run_command` is a fact about the
  source's build; `provenance` is a fact about where the grader came from. This
  is archive content, and putting it in the authored overlay would make a human
  type it, which R19 forbids.
- ⭐ **The three states fall out of the structure, with no flag to remember.**
  **none** — there is no `practice-M.json`. **ungraded** — a `practice-M.json`
  with blocks and no `exercise` key, or a record naming a file and no grader.
  **graded** — the record names a grader. A corpus whose units set no work
  writes no practice document at all.
- **R5 gets one place to enforce.** `provenance` and `trust` sit on the same
  record, so the archive writer and `studyforge validate` refuse `trust:
  "authoritative"` beside any provenance but `bundled` — one rule, one file.

⛔ **`trust` is declared but never believed.** An adapter writes what it claims;
the framework checks the claim against `provenance` and refuses the combination
R5 exists to prevent. `trust` may be omitted, and then defaults from
`provenance`: `authoritative` for `bundled`, `advisory` for the rest. ⛔ **An
`authoritative` claim, declared or defaulted, needs the derivation record** below,
so a shipped grader that was not derived declares `advisory`.

⛔ **The record's keys are a closed set, written in one order**: `main_path`,
`test_path`, `run_command`, `test_command`, `provenance`, `trust`, `kind`,
`cases`, `report`, `origin`, `questions`. A key the record does not define is
refused. Each key after `trust` is written only where the record carries it.

### A file with no test

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

- ⭐ **Graded is the grader's presence, not the key's.** The record's `test_path`
  is the graded state, read off the structure with no flag to set.
- ⛔ **Half a grader is refused**, naming what is missing, and so is a
  `provenance` or `trust` with no grader. Both are facts about a grader, and
  trust in a grader that does not exist is the claim R5 exists to stop.
- ⭐ **The practice with no `exercise` key stays valid and stays ungraded.** A
  corpus whose prompts name no file writes nothing.
- ⭐ **Why a record and not a second declaration.** The unit document's workspace
  is this record, so the file reaches the one place Run and the terminal command
  already read, with no new key in either document.

**Run and Submit are different acts.** Run executes the reader's program so
they can see what it printed. Only a `test` run can complete a practice: a
program that prints successfully has demonstrated nothing about its tests.
⭐ **From a terminal, `studyforge check <file>`** runs the test for the unit's
file the reader edited, or its program when nothing checks it — and a file with
no test is not a failure. The command run is the one the unit's generated
document names; nothing the reader types becomes a command.

### Exercises derived from a shipped grader — the two gates

A source that **ships its grader** — test classes paired with the
implementation they test — inverts the usual problem. Nothing has to be
guessed: an exercise can be derived mechanically by blanking what a lesson
teaches, and the derivation is **self-verifying**. This is the only way an
exercise earns `bundled` · `authoritative`, and an adapter that derives one
holds these gates:

```text
for each (Impl, ImplTest) pair:
    select the methods this lesson teaches
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
class"* — nearly always true and therefore nearly vacuous. The claim is
per-method (*this* body is what the lesson teaches, and the test discriminates on
it), so the check is per-method too. A class-granular gate would let a practice
ship where most of the work is already done, marked `authoritative`, which is
precisely the failure R5 exists to prevent. Gate 2 proves the grader itself
works. **No human reads anything, and no assertion is authored by a model**,
which is exactly why such an exercise keeps the stronger label.

⭐ **The derivation is recorded, and `validate` re-reads it.** The adapter writes
the two gates into the practice's gate record, `gates.json` under `exercises/`, as
the `derivation` family: `D1` is Gate 1, with one `hole:<method>` entry per blanked
method and the attributed failure as its value, and `D2` is Gate 2. The record
digests the `starter`, the `reference` (the original) and the `tests`, spelled
from the corpus root. ⛔ **`studyforge validate` refuses every `authoritative`
exercise without such a record** (`derivation-record`): no record, one that will
not read, a `D1` naming no hole, a `starter` or `tests` that is not the
exercise's own `main_path` or `test_path`, or a starter that still digests to the
original. It refuses a record whose `D1` or `D2` did not hold
(`derivation-shortfall`), and one whose named files changed since the gates ran
(`derivation-digest`).

- **The lesson names the methods.** The methods a lesson discusses are the methods
  it teaches, so selection follows the lesson's own text rather than position.
- **An exercise has a size cap.** A pair that would exceed it emits **several**
  practices, not one; a hole that cannot be brought under it alone is reported,
  not shipped.
- **Some shapes have nothing to blank, and that is predictable.** Records, sealed
  hierarchies, interfaces and enums teach through their *declaration*; their
  accessors are implicit and unblankable, and such units are expected to yield no
  derived exercise.
- **Nothing unmatched is dropped silently.** Pairs attach to units by ordinal,
  falling back to title and class-name similarity; a pair that matches no unit
  attaches to its container's final unit as an additional practice, and
  everything unmatched is named.
- **Compilable sources live on a source root.** Reader-facing practice material
  sits beside the page (§5); sources a build tool must compile go in an additive
  `practice/` module mirroring addresses, joined to the build by the one line
  `permitted_edits` declares (R3).

Expected yield is well below 100%, and that is the honest outcome, not a bug.
Units with no gate-passing exercise ship as reading-only and are named in the
coverage report (R6). ⛔ **A low yield is never fixed by loosening a gate or
generating an assertion** — that converts a proof into theatre; an assertion
that is authored is `generated` and belongs to the next section.

### Exercises authored for every corpus

⭐ **The idea at the centre of the product: a practice site in the manner of
CodeSignal or LeetCode, built from any given source.** A model reads the material
once, at ingestion, and authors the exercises its pages support; the gates below
prove each one before it ships.

#### 1. Three source cases, one pipeline

| the source has | where the exercise comes from | provenance · trust |
|---|---|---|
| **code and tests** | derived by blanking, through the two gates above | `bundled` · `authoritative` |
| **code, no tests** | the source's own example is the reference solution; the ask, the starter and the tests are authored from the page | `generated` · `advisory` |
| **neither** | the ask, a reference solution, the starter and the tests are all authored from the page | `generated` · `advisory` |

⭐ **The first row may also gain authored exercises** beyond what blanking yields;
those are `generated`, and they never borrow the derived ones' label. ⛔ **The
three rows are not three pipelines**: one authoring pass, one set of gates per
exercise kind, one bundle shape, one coverage report.

#### 2. Authoring happens once, at ingestion

⭐ **The exercise-authoring skill writes the exercises and commits them into the
corpus repository** as source-side material — one *exercise bundle* per exercise,
under `exercises/<address>/<variant>/unit-NN/practice-M/`. A bundle holds
`bundle.json`, `statement.md`, the gate record `gates.json`, and the files under
`starter/`, `reference/`, `tests/`, `plants/` and `build/`, and nothing else. The
bundle's emitter writes the unit's `practice-M.json` from it and lays the starter,
the tests and any build files into the reader's workspace under
`practice/<address>/<variant>/unit-NN/practice-M/`; the reader edits that copy,
never the bundle, so the gate record's digests stay true. R2's on-disk seam is
untouched, and the framework still knows nothing about any source (R1).

⛔ **No model runs at build time and no model runs at serve time.** The site stays
offline over `file://` (R8) and the build stays byte-reproducible from the
committed bundles (R10). ⭐ **The non-determinism lives in authoring, exactly where
a human author's does** — and, like a human author's, it is reviewed once and then
fixed in the tree.

#### 3. Nothing the source already has is lost

⛔ **The reading floor is untouched.** Every example the source ships still renders on
the page, verbatim, whether or not an exercise was built from it.

⭐ **The proof is a *source ledger*, `exercises/ledger.json`.** Every fenced example
and every test file the source carries is an entry, and each entry is either the
basis of at least one exercise — named by that exercise's `origin` — or carried with a
written reason it is not. ⛔ **An entry with neither is refused** (R6), and
`studyforge validate` re-scans every material page against the committed ledger, so
a ledger that lost a page's rows is a finding rather than a quiet pass.

#### 4. How many exercises a page gets follows the page

- ⭐ **The skill writes a per-page *plan* before it authors anything**, naming the
  page's *aspects*: the important ideas it teaches that a reader could be checked
  on, read from its prose and its code. ⛔ **Trivia is not an aspect** — a date, a
  name or an incidental number is not; the idea it illustrates may be.
- ⛔ **Every aspect is accounted for**: checked by a named exercise (or quiz), or
  carried by a written reason. **An aspect with neither is refused**, the same
  honesty §3's ledger asks of files. ⭐ **One exercise may check many aspects, and one
  exercise practising related ideas is preferred** over several small unrelated
  ones; a minor aspect is carried by a short reason. ⭐ **A quiz asks few
  questions.**
- ⛔ **Near-duplicates are refused**: two exercises never check one aspect.
- ⛔ **No length ceiling, and no quota.** Zero stays legitimate, with its reason
  written. The record is what was judged important and why — never a coverage
  percentage.
- ⛔ **The plan is a ceiling, never a quota** (R6). What ships is what clears the
  gates, and every shortfall is named with the gate that refused it. ⛔ **A count
  is never met by lowering a bar.** ⭐ **The same aspects always produce the same
  plan** (R10).

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
coarser than the claim it backs is theatre.

⛔ **Every gate answers, always.** A gate with nothing to read answers *did not hold*
and says why — never *held vacuously*. ⛔ **G1–G3 are mechanical and re-runnable**:
the bundle carries the reference, the starter and each plant, so anyone holding it can
take the reading again.

#### 7. A corpus whose subject is not code — the quiz shape

⭐ A history book, a standards walkthrough or a prose tutorial activates its reader
too. **A quiz is an exercise whose `kind` is `quiz` rather than `code`.** In place of a
workspace it carries **questions**: a stem, an ordered set of options, exactly one
keyed as correct, one sentence per option saying why it is right or wrong, and an
`origin` naming the passage of the page it came from.

⭐ **How it is authored from the page.** The same pass that plans code exercises plans
quiz ones, from the same ledger: each question is written from one passage, and the
passage is recorded by address, not paraphrased into the question's provenance.

⭐ **The local study server grades a quiz, and the key never reaches the page.**

- ⛔ **No built page and no asset a page loads carries a quiz's key or any per-option
  sentence.** The key stays in the practice document on disk, which is server-side
  material, and the content route withholds it.
- ⭐ **The page sends what the reader chose to `serve`'s quiz route**, which reads the
  key from the unit's document and answers, per question, right or wrong **with the
  chosen option's sentence** — never the keyed option's, so a wrong answer is
  explained rather than corrected. ⛔ **No model, no network and no container: a fixed
  comparison**, and the route imports nothing that could start a process or reach a
  socket (§8.3). It sits behind `serve`'s guards like every other route.
- ⭐ **Completion keeps its meaning**: a quiz completes only when every question is
  answered correctly, decided by the framework's one grading rule. ⛔ **Never a run
  verdict** — the pass rule for a run is untouched, and a quiz produces no run.
- ⭐ **Over `file://` a quiz shows its questions and options and says checking them
  needs the local study server**, exactly as Run and Submit do.

⭐ **The honesty gates for a quiz.** A compiler cannot back these, so the gates are
different and their difference is stated rather than smoothed over:

| gate | what must hold | what it proves |
|---|---|---|
| **Q1 answerable** | an independent pass given the page and the question — and nothing else — picks the key, twice, with the same outcome | the page actually contains the answer |
| **Q2 not free** | the same pass given the question and its options but NOT the page does not pick the key | the question tests what this page taught, not general knowledge |
| **Q3 discriminating** | every wrong option is refuted by a named passage of the page | a distractor nobody can rule out is a trick, not a check |
| **Q4 key total and single** | exactly one option is keyed, the options are distinct after normalisation, and every option carries its one sentence | the reader is told why, for whichever option they chose |
| **Q5 origin** | every question's `origin` resolves to a ledger entry whose digest matches the page as ingested | the question is built from the page it is attached to |

⛔ **Q1–Q3 are model judgements taken once at authoring and shipped as a record; Q4 and
Q5 are mechanical and `studyforge validate` re-runs them.** ⭐ **So a quiz grader is
`generated` · `advisory` always, and there is no path by which one becomes
`authoritative`** — that is the difference between a proof you can re-take and a
reading somebody took for you, and R5 turns on exactly that distinction.

#### 8. The reference solution is always available

⭐ **Every authored code exercise ships its reference solution as reader-facing
material**, inside the practice as a disclosure the reader opens — *Show a worked
solution* — at any time, never gated behind a passing Submit. ⛔ **It is never revealed
automatically**, and asking is never recorded as a failure, because a reader who reads
the answer has still read the material and this is not an exam. ⚠️ **The gates already
require the reference to exist** (G1), so shipping it costs nothing, and withholding it
would be a pretence: the bundle is on the reader's disk either way.

#### 9. What the reader is told, in a learner's words

⭐ **R5's vocabulary stays internal** — `provenance` and `trust` are the framework's
words, in the record and in `validate`, and a reader never sees either token. ⭐ **The
framework fixes the sentence each case renders as, and it is the framework's template,
not a corpus's string** (R1):

| the record says | the page says |
|---|---|
| `bundled` · `authoritative` | **Checked by the tests that ship with this material.** |
| `bundled` · `advisory` | **Checked by tests that ship with this material. They have not been proven to catch a wrong answer.** |
| `user` · `advisory` | **Checked by tests written by hand for this practice. They have not been proven to catch a wrong answer.** |
| `generated` · `advisory`, kind `code` | **Written for this site. Its tests were proven against a worked solution before it shipped.** |
| `generated` · `advisory`, kind `quiz` | **Written for this site from this page.** |
| no grader (ungraded) | **Nothing here checks your answer.** |

⛔ **The label is never omitted because it is unflattering**, and it is never softened
into a sentence that implies more than the gate record supports.

#### 10. What is recorded, and what `validate` refuses

- ⭐ **The exercise record carries `cases`** — an `id` as the test report spells it, a
  `kind` (`main` or `edge`), and `says`, the one sentence the reader sees — plus the
  `report` (its format, JUnit XML, and its path in the workspace's run output
  directory) and the `origin`. `cases` and `report` are facts about a grader and are
  refused on a record with none.
- ⭐ **A gate record ships beside every authored bundle.** It holds the digest of every
  input — statement, starter, reference, tests, each plant, each build file, each cited
  passage — and every gate's verdict. ⛔ **`studyforge validate` refuses a `generated`
  exercise whose gate record is absent, incomplete, or whose digests no longer match the
  files beside it**, and a bundle holding any file its shape does not permit — a run's
  report among them, which carries the machine's hostname (R7).
- ⭐ **Submit reports the breakdown from the test run's machine-readable report**, folded
  through `cases` into *main ask* plus *edge cases n/m*, naming each failed case by its
  `says`. ⛔ **The pass rule does not change**: a practice completes only when every case
  passes, and the breakdown is a report, never a second definition of a pass.

#### 11. When a gate refuses

⛔ **The exercise does not ship.** The skill may re-author that one exercise within a
fixed number of attempts, and ⛔ **never by loosening a gate, dropping a case or deleting
a question**. When the attempts run out, the unit's coverage report names the page, the
exercise, the gate, the case and the run's last output, and a page left with nothing
shipped is named as such (R6). ⭐ **That is the low-yield rule above, applied to
authored work: a shortfall is reported, not engineered away.**

---

## 8. Inherited technical apparatus

CodeSignal solved a number of problems the hard way, and the solutions are
recorded here because **none of them is obvious from the outside.** Re-deriving
any of them is waste; changing one without knowing why it is that way is a
regression.

### 8.1 The code-server toolchain — its own repository

The toolchain is a **standalone repository**, `code-server-toolchain`, that
publishes two images and describes both in its `consuming.json` (R18):

- **the runner** — the runtimes a corpus declares (§4's `runtimes`) and nothing
  else, idling offline, for a reader's graded runs. ⭐ **The reader starts it**,
  with the source root alone mounted at `/work`, `--network none`, no port and no
  socket; the framework only probes that it is up and runs commands in it (§8.3).
- **the editor** — a browser editor (code-server) over the same runtimes, opened
  from a practice beside the page.

⭐ **One file chooses every runtime version**, the component's `pins.json`, which
pins its base image by digest; both images take their versions from it and
neither may choose one of its own. A runner image's tag is computed from the
declared runtime set, the architecture and a hash of every build input, so a
corpus's compose file names exactly the image its declaration builds.

| Shared — lives in the component | Per-project — generated into the corpus (§9) |
|---|---|
| `Dockerfile`s, entrypoint, build scripts | the compose file |
| the practice-focus lockdown extension | **mounts** — which paths, which read-only |
| seed settings and keybindings | container name and port binding |
| runtime selection and pinning | the prime project supplied at build time |
| extension list and verification | uid:gid mapping to the repository's owner |

What the images must keep getting right:

- **Extensions are installed at build time into a directory in the image**, not
  onto a volume, so an image upgrade always carries them — and the build
  **verifies the installed list and fails on a missing id**.
- **PATH is set twice, deliberately.** `ENV` reaches non-login shells; the
  integrated terminal starts bash as a *login* shell and `/etc/profile` then
  overwrites PATH, silently dropping everything under `/opt` — so a tool works
  under `docker exec` and is "command not found" in the terminal. A `profile.d`
  script fixes it.
- **The build cache is primed by building a real trivial project.** The prime
  project carries one minimal source and test per language, so the first offline
  build needs no download. The sources must be *real*: a compile task with no
  source never resolves the compiler classpath, so an empty prime silently primes
  nothing. An exercise's own build dependencies are warmed into the prime from the
  same declaration, so a graded run resolves them with no network.
- **The lockdown extension is packaged as a `.vsix` and installed**, never copied
  into the extensions directory — the workbench reads `extensions.json` and never
  scans, so a copied folder is present, correct and silently never loaded.
- **Named-volume mount points are created in the image, owned by the runtime
  uid.** Docker creates a missing mount point root-owned, which leaves the server
  unable to write its own config.
- **`ENTRYPOINT` and `CMD` are both re-declared**, because the base image bakes
  arguments that a compose `command:` would otherwise be appended to.

And what the compose side gets right, which stays per-project:

- ⛔ **Loopback-only port binding, never `0.0.0.0`.** The editor runs with **no
  password**, which is safe only because it binds to `127.0.0.1`: loopback is the
  whole of its access control, and widening the bind is a decision to put an
  unauthenticated shell on the network, which requires restoring authentication.
- **Only the sources are mounted** — not the repository, not `$HOME`.
- **The container runs as the repository owner's uid:gid**, so files it creates
  are not root-owned on the host.
- **Every bind source exists before the containers start**, or docker creates it
  root-owned and the writer can never write it: where another service creates one,
  the editor waits on that service's health check; where the project creates it,
  it is created before the containers come up. The per-mount and ordering keys
  live in the component's consuming contract.

⭐ **A corpus with runnable material needs the runner, not the editor.** The reader
can edit a file in their own editor and run `studyforge check` from a terminal
(§7); the browser editor is an addition for the practice beside the page. ⛔
**§8.3 binds both: the Docker socket is never mounted into the serving process.**

### 8.2 The narration service — its own repository

Narration gets the same treatment as the toolchain: `narrate-service` is a
standalone repository exposing a **synthesis API over HTTP**, containerised, with
the engine behind an adapter, published on `127.0.0.1` only.

| Shared — lives in the service repo | Per-project — lives in the consumer |
|---|---|
| the job API and its manifest format | which segments to synthesise |
| engine adapters and the voice catalogue | voice selection for the corpus |
| containerisation, CPU and GPU variants | **where the files land** (R4) |
| content-addressed caching | the personal-data gate |
| the optional agent-callable adapter | incremental regeneration policy |

- **The unit of work is a batch of keyed segments, not one blob.** The page's
  highlight sync needs **one clip per speech unit** (§8.4), so a job takes a list
  of `{id, text}` and returns one artifact per id plus a manifest. A batch rather
  than a request per segment, because a corpus is thousands of segments and
  per-request overhead is the difference between minutes and hours. A
  single-utterance route stands beside it for one-off use.
- **The service never writes into a corpus.** It returns artifacts for the caller
  to fetch and place through the placement policy. A synthesis service that knew
  where a study site keeps its audio would be a second authority on layout, which
  is precisely what R4 removes.
- ⛔ **The personal-data gate runs client-side, before the request** — never in the
  service. **An mp3 that speaks an account identifier is personal data on disk
  that cannot be grepped for afterwards.** The service is a third party from the
  framework's point of view; ungated text never reaches it (R7), and the gate is
  asserted on what was *sent*, not on what was written.
- **The engine is pluggable and requires no particular hardware.** The service
  ships a CPU path that works anywhere, with GPU as an opt-in profile (R15).
- **Chunking is the service's job** — it accepts a very long input and splits
  internally, so no client keeps stitching logic — and **writes are atomic**,
  landing in a temporary sibling and being renamed, so an interrupted run never
  leaves a truncated file that looks finished.

⚠️ **Synthesised audio is the one carve-out from R10's byte-for-byte clause.** A
speech model is not guaranteed to emit identical bytes for identical input. Audio
is instead **content-addressed and cached**: a segment whose text and voice are
unchanged is never re-synthesised. R10 applies in full to every other generated
artifact.

**`studyforge narrate <root> --voice <voice>`** is the framework's side: it
submits a corpus's speech units, places the clips beside the material, and
records in `.studyforge/narration.json` the conditions each clip was synthesised
under — the voice, the audio format, the engine's model and the service's
promise (`provides`). ⭐ **A re-run with
nothing changed requests nothing**, and a change in any condition re-requests
every clip it made stale. `studyforge narrate <root> --prune` deletes the clips
of record entries the corpus no longer produces, over a walk of the whole corpus.
`--pack` and `--publish` carry a corpus's clips out of git as release volumes
(§5, *Generated media and pages are committed*); neither reaches the service.

### A clip's filename carries a digest of the words it says

⛔ **A narration clip is named `<speech-id>-<8 hex of sha256(spoken text)>`.** It
is minted by **one** function — the speakable contract, which owns both what is
said and what it is called — and both the renderer that links the clip and the
client that places it go through it. A second minter is a page asking for a file
the placer never wrote, with no symptom but silence.

The obvious alternative is a plain positional name and a *check* for currency — a
sidecar manifest, or a re-submission to the service. ⛔ **A check can be skipped,
and the skip is silent**: a runner that decides a clip is current by whether the
file exists goes on playing the previous wording after a re-capture, reports
*"0 synthesised"*, and every gate is green. Nothing distinguishes a correct
incremental run from that one by inspection.

⭐ **The digest makes it structural rather than checked.** Change the spoken text
and the name changes; the page then links a clip that is not on disk, and the
client synthesises it. **A stale clip cannot be addressed.**

⚠️ **The speech id stays positional.** The id is what a *structure* edit must not
renumber, so that retitling a section does not orphan a unit's audio; the digest
is what a *text* edit must change. They answer different questions and the
filename carries both. ⚠️ **This is not the shared-asset case** R10 rules
hash-free: the page is already rewritten whenever its text changes, in the same
generator run.

⚠️ **The old clip stays on disk under its old digest, playable by nothing**, until
a prune deletes what the corpus's documents no longer name — ⛔ **only for units
the run actually read**, never on behalf of one it skipped. **What it costs:** a
prose edit renames one file and synthesises one segment — the segment the author
just changed.

### 8.3 Where execution runs

**The problem.** R15 wants reproducible execution, so Run, Submit and the
authoring gates invoke a pinned toolchain. The obvious reading — put the server
in a container too — requires mounting the Docker socket into it, and a socket
inside a network-listening process is root-equivalent access to the host.

**The ruling.**

1. **The toolchain is containerised; the serving process is not.** The runtimes
   and their caches are pinned in the runner image (§8.1) — that is where
   reproducibility lives. The server is a standard-library HTTP process with no
   dependencies, so a container adds nothing to it.
2. ⛔ **The Docker socket is never mounted into the serving process.** Not as a
   convenience, not behind a flag, not "only locally".
3. **Execution crosses into the container from outside it.** `execute`, the only
   package that runs a corpus's commands, probes whether the corpus's runner
   container is up and runs `docker exec` into it with the command's argv
   verbatim; when it is not up, it runs the same argv on the host. ⭐ **Both modes
   have identical observable behaviour** — the merged output streamed line by
   line, every line relative to the source root and scrubbed (R7), and exactly
   one exit line — and that is asserted, not assumed. ⛔ The runner never starts,
   stops or builds a container. Commands come from a generated document on disk;
   **nothing a client sends becomes a command.**
4. **If full containerisation is ever required**, the answer is a separate
   execution broker owning the toolchain, which the server posts jobs to — the
   same shape as the narration service (§8.2) — and never the socket.

**What this costs the reader:** the host needs Python (standard library only)
and a Docker CLI. Nothing else. The toolchain, its caches and every pinned
version stay in the image.

### 8.4 The reading surface

These are proven surfaces, generalised in their addressing and otherwise kept.

- **Reading page** — a serif reading column; one shared stylesheet and one shared
  script, `page.css` and `page.js`, with deliberately unhashed names (R10);
  browser-side Prism highlighting, never build-time; light and dark palettes with
  every token defined in both themes, and a control that lets the reader choose
  light, dark or their system's setting.
- **Narration** — positional (never content-derived) speech **ids**, display text
  and spoken text as two renderings of one list, clip-level highlight sync. The
  clip **filename** adds a content digest (§8.2); whether clips are committed is
  the manifest's media policy (§5); whether a corpus is voiced at all is its
  `narration` key (§4).
- **Video** — vendored Plyr with its icon sprite substituted rather than fetched;
  nothing may reach the network.
- ⛔ **The source's own outline number is not served.** A title or heading the
  source writes as `5.1.1.1 Thread states`, `3.2.1. Batch processing` or `10.7.2 —
  ORM frameworks` is shown and narrated as its words alone, on the page, in its
  chrome and in the contents, because the site lists and orders everything
  itself. It is a rule the framework applies to every corpus, not a manifest
  setting. ⛔ A number that is part of the words is kept: the rule takes only a
  leading dotted number or a leading number closed by a stop, each part at most
  three digits, followed by a space, and it keeps a two-part number with no stop
  when a lower-case word follows it (`1.5 million`). ⭐ The archive and the
  container maps keep the number, as recorded, and a page's place is still named
  from the recorded title. A clip is named by a digest of its words, so a heading
  that loses its number is a new clip.
- **Table of contents** — the contents document (stable, reproducible) and the
  local status (volatile) as two documents, so a consumer can cache one and poll
  the other, at any declared depth. ⛔ **The root index fetches nothing at
  runtime**: `fetch` of a sibling file is refused over `file://`, there being no
  origin to ask, so its contents data is delivered into the page at generation
  time.
- **Backend** — `/api/v1/content` (cacheable, strong ETag) and `/api/v1/state`
  (never cached, derived from the filesystem on every request) as two namespaces
  with opposite caching rules; `/api/v1/assets` (Range, weak ETag);
  `/api/v1/run` for Run and Submit and `/api/v1/quiz` for quiz checking. ⛔ The
  server binds loopback only, refuses a non-loopback peer, refuses a `Host` that
  is not a loopback name, and refuses cross-site requests.
- **Runner** — `docker exec` into the runner container when it is up, the host
  otherwise; line-by-line streaming; one exit line; every line scrubbed (§8.3).
- **Progress** — two records, not one (§8.5).

⛔ **A fence with no info string renders as plain text, and the renderer never
guesses a language.** A guess is a silent wrong highlight, which is worse than no
highlight. A `code` block whose `lang` is empty carries no highlighter class and
the caption `code`. ⭐ The vendored Prism bundle declares its languages, and a
fence in an undeclared language falls back to plain text and says so.

#### The reading room's identity

⭐ **One framework identity.** Every studyforge site shares one look, drawn from
the subject every such site shares — reading and study. ⛔ **It is built to be read
for hours, so it is judged on a real generated page**, light and dark and at phone
width, with its contrast computed rather than eyeballed, and what is reported is
what was seen.

- ⛔ **Colour is a role-named token and nothing else.** Every colour is a CSS custom
  property named by its role — ground, raised surface, ink and its quieter inks, rule,
  accent, the semantic states — and a stylesheet paints only with tokens. Both themes
  are designed: the dark tokens are defined under `prefers-color-scheme: dark`, guarded
  so an explicit light choice wins, and again under an explicit dark choice. One
  dominant ground, one sharp accent, and semantic colour kept apart from the accent.
  ⛔ A saturated colour never grounds a whole page; it belongs on one element.
- ⛔ **Contrast is computed and reported**: body text at least 4.5:1 against its actual
  background, large text and non-text marks at least 3:1.
- ⭐ **Faces are vendored SIL Open Font License files, pinned by digest with their
  licence beside them, and embedded in the stylesheet** — ⛔ never a CDN and never a
  relative `url()`, because a generated page opens from `file://` with no network
  (R8), and a browser's file-origin policy refuses a font outside the page's own
  directory. Charis sets the prose, Andika the headings, navigation and controls, and
  JetBrains Mono code and nothing else. ⛔ **Code draws no ligature**: `!=` joined
  into a not-equal sign reads as a different operator, so every rule that sets the
  code face turns ligatures off, and the practice editor's `editor.fontLigatures` is
  off so the two still draw code alike.
- ⭐ **Structure encodes information.** Numbering only where order is real, dividers
  only between things that are separate, groups kept where the corpus has them — the
  index's progress strip has one segment per top-level group and never overflows its
  column, and the rail lists each container inside the groups above it — one bold element carrying the identity with
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

⭐ **The rejected palettes are data, and the floor reads them.** The tells that can be
read off a colour are the two tables below, which the palette check reads over every
stylesheet the framework ships: a rejected identity that returns is a floor finding,
by name. ⛔ **The tables are the authority and the check is only their reader**, so a
new rejected identity is a row added here, with no code change. ⚠️ **A green check
means *no rejected palette is shipped*, never *the identity is met*** — a face, the
card kit or an eyebrow label is a tell no hue can see.

Every colour is read as three measures: **hue** in degrees; **chroma**, `max − min` of
its channels over 255, in percent; and **light**, `(max + min) / 2` over 255, in
percent. ⛔ **Chroma and not HSL saturation, deliberately**: a near-white paper with a
one-step tint reports a saturation near 40% and a chroma near 3%, so a bound written in
saturation would refuse an accepted paper. ⭐ **A row's parts are joined by `+`, and
every part must hold in one theme** — light and dark are read apart, each over the
tokens it defines — with the parts on one role met by that theme's colours for it.
⛔ **The conjunction is the instrument**: cool slate alone is the accepted identity, and
it is the triple that is rejected, so a row that fired on one part would refuse the
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
| Warm cream and terracotta | `ground: hue 20-70, light >= 85, chroma >= 3` + `accent: hue 5-32, chroma >= 25, light 25-65` | the commonest tell of generated design |
| Near-black ground, acid-green accent | `ground: light <= 12` + `accent: hue 75-165, chroma >= 45` | a tinted near-black standing in for a dark ground, where a real mid-dark with character is asked for |
| Near-black ground, vermilion accent | `ground: light <= 12` + `accent: hue 0-20, chroma >= 45` | the same tell's other accent |
| Cool slate with teal-green and amber | `ground: hue 190-250, chroma <= 20` + `accent: hue 150-190, chroma >= 20` + `accent: hue 35-60, chroma >= 30` | generic and repetitive between generated designs. ⛔ It is the TRIPLE: the slate alone is accepted |
| A saturated brand colour as the page ground | `ground: chroma >= 30` | a saturated colour grounding a whole page |
| A purple-to-blue gradient | `gradient stop: hue 258-300, chroma >= 20` + `gradient stop: hue 200-255, chroma >= 20` | a generated-design tell, read where a gradient actually is |

#### The accepted identity

⭐ **The rejected table is half of what a repaint needs, and the other half is what
the identity is:**

| Part | The identity |
|---|---|
| neutrals | a cool slate scale, ground through rule, in both themes |
| the accent | ONE loud accent, live where it means *next* or *you are here*, and nowhere else |
| green | ⛔ **none in the identity** |
| themes | both, each designed, with the reader able to choose between them and the system |
| ink | the quieter inks in separate contrast bands, so none of them reads too dim |

⚠️ **The no-green bound is not read by the palette check**: it is a rule over the
shipped tokens rather than a rejected identity, and the reading surface's own palette
tests hold it.

### 8.5 Progress is two records

**Two different things are being recorded, and they are established by different
means.**

A **read mark** is the reader's own assertion that they have read a unit. It
needs no server, no grader and no origin, so under R8 it must exist without one:
it lives in the browser's local storage, and the site says plainly that it is
**one browser, one machine, not in the repository, and gone with site data.**

A **practice pass** is a fact established by a grader run. A grader run requires
the runner, which requires the server, so the record is written where the fact
was established: the corpus's git-ignored `.studyforge/progress/progress.json`,
read-validate-modify-write under a lock, atomic replace, `first_passed_at` set once
and never moved. A Submit's breakdown rides beside its verdict and is never a
second rule for a pass.

⛔ **The obvious alternative — one store — fails in both directions.** Put
everything in local storage and a pass becomes a claim by a client that the
server cannot check, lost with site data. Put everything server-side and R8's
floor means a reader who only ever double-clicks a page has no record at all. ⭐
**It binds hardest on exactly the sources this framework exists to serve**: §7
admits three exercise states and two of them can never complete anything, so a
server-side-only store would record nothing whatever for a corpus with no
graders.

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

⛔ **Durable browser storage is touched in exactly one source file**,
`study-progress.js`, which defines the store and is shared by the unit page, the
container page and the index; the reader's display preferences are a record of
their own inside it, so a preference that fails to parse cannot take every mark
with it. Two implementations are the key-disagreement failure above, reached by
another road.

⚠️ **A shared script is concatenated ahead of every file that uses it, and the
order is asserted against the real composed bundle** — never against a test
harness's own concatenation. A store placed *after* the page script that reads it
at startup skips its guard, the setting silently never comes back, and the suite
stays green. A harness that arranges the world conveniently proves nothing.

---

## 9. The skills layer — what is actually being built

R16. The pipeline is the means; **the skills are the product.** Somebody points a
skill at material they care about — a course site, a book, a paper collection, a
repository of exercises, their own notes — and gets this format back, then keeps
it as a durable personal record they can review, re-run and extend.

The division between them is the same seam as everywhere else (R2): one
understands *a source*, the rest are source-agnostic. Each skill is a `SKILL.md`
procedure shipped in the framework's package, with whatever executable support
it calls beside it.

- **Reconnaissance.** Given arbitrary material, work out its shape: how deep the
  hierarchy is, what the units are, whether there are variants, whether anything
  is runnable and which runtimes it needs, whether any grader ships with it, and
  whether any file duplicates another (C2). Produces a draft `corpus.json` and an
  honest report of what it could not determine. This is the only skill that
  reasons about unfamiliar material.
- **Adapter authoring.** Scaffold an adapter for that shape — a package layout, a
  test tree and an audit command, with the archive's paths computed by the
  framework — against `studyforge validate` as the definition of done, so the
  skill's output is checkable by machine rather than by opinion.
- **Corpus onboarding.** R19's realisation: take a repository from nothing to a
  corpus this framework can build. It writes the manifest, the adapter package
  and its tests, the ignore rules, the non-destructive assertion, the framework
  pin and its skill stubs, and the reader's document — and it writes an
  **uninstall** that reverses every edit it made. It asks the author whether the
  corpus is narrated. ⭐ **The one manual step is: install the framework, run this
  skill.** Anything a second source has to type by hand is a defect in this skill.
  ⭐ **It records every file it wrote with the digest it wrote**, in
  `.studyforge/installed.json`, so a hand-edit to a generated file is named
  (R19), and a regenerate is safe: a file the regenerate no longer writes is
  removed when its bytes are still the ones recorded, and when a person has
  edited it the regenerate is refused before anything is written, naming it
  (R3). Its generated checks run under pytest or as plain scripts, so a Python
  holding only the installed library can run them.
- **Execution onboarding.** For a corpus whose material is runnable: the compose
  file for the runner and the browser editor, the runner image's selection from
  the declared runtimes, and the prime project — all rendered from
  `code-server-toolchain`'s `consuming.json` (§8.1), with the image tags it records
  in environment files the compose command reads. ⭐ It keeps its own record of what
  it wrote, `.studyforge/execution/written.json`, which onboarding's hand-edit check
  reads beside its own, so one check answers for both skills. ⭐ **Most corpora never
  run this skill, and that is the design** (§11.0).
- **Authoring exercises.** Plan every page by its aspects, author the exercises
  and quizzes its material supports, run the gates over each, and commit what
  clears them as bundles, with the ledger and the coverage report (§7).
- **Build and serve.** One invocation from a corpus to a running site: validate,
  narrate when asked, build into a directory the owner names, and serve it.
- **Delivery planning.** The product owner for an integration: turns *"convert
  this repository"* into an ordered backlog whose every task ends in something a
  person can be shown, with acceptance the framework itself can evaluate.
  ⭐ **It plans against what the installed framework offers** — `python3 -m
  studyforge.skills.delivery` lists every command the installation runs and every
  skill it ships — never against a version the framework may become, so no task
  waits for the framework to grow. ⛔ **A capability the plan needs and the offer
  lacks is a finding the plan files**, and the task that needs it names that
  finding as what it waits on. ⭐ **The plan says where the corpus finishes** — at
  the reading floor or on the execution track (§11.0), with the evidence that
  decided it — and names every offered capability the corpus will never use, with
  the reason. It runs in the target repository, and ⛔ **its only channel is this framework** —
  it may ask questions, and it may file findings, but it may not patch (§12) and
  it may not read the extraction source (R20). It feeds the **integration
  catalogue**, below.
- **Personal archive.** Export and re-import a corpus *with its progress* —
  code, practices, examples and what the reader has completed — so the record
  survives a machine, and a corpus can be handed to somebody else without its
  owner's progress leaking with it (R7).

### A skill precedes the artifact it produces

⛔ **A skill written after the thing it "produces" is a retrospective, not a
tool.** It has been validated against exactly one source — the one it was
reverse-engineered from — which is no validation at all, and the first genuine
test of it is the second source, which is precisely where it must not fail.

So the skills divide by what they actually are:

- **Skills that are how an artifact comes to exist** — reconnaissance, adapter
  authoring, corpus onboarding, and the authoring reference they point at. These
  come **before** a corpus is built, and a corpus is their output rather than
  their input.
- **Wrappers over entry points that already work** — build-and-serve, exercise
  authoring, personal archive. These genuinely cannot precede what they wrap.

⚠️ **A skill that starts minimal is still a skill.** One that scaffolds a package
layout, a test tree and an audit command, and leaves the source-specific reading
to be filled in, is already what its definition asks for. The alternative is
worse: a corpus built by hand, and skills written afterwards to claim they
produced it.

### The integration catalogue

R20 says a consumer never reads the repository this framework was extracted
from. That is only honest if what a consumer would have gone looking for is
**here** — so the framework carries [a catalogue](../integration-catalogue.md)
of what goes wrong when material meets it, written for somebody planning work
rather than somebody writing code: a plausible short parse that raises nothing;
a corpus carrying the same material twice; a hierarchy encoded in filenames; an
exercise with no grader, which is not "no exercise"; media that outgrows a git
remote; an address derived from a title.

⭐ **It is a growing asset, not a founding document.** Each integration's
findings (§12) are distilled back into it, so the next integration starts
further along than the last. ⚠️ **This is the mechanism by which the framework
gets better at being adopted**, as distinct from getting better at rendering
pages.

### How a consumer obtains the skills

The framework is **installed as a library, and pinned**, never copied, because a
copied skill is a fork that a framework fix never reaches (R18). ⚠️ **A pin is a
version, while skill discovery is path-based** — a skill has to be findable at a
path inside the repository the agent is working in.

⭐ **The pin is the authority; the discoverable path is a generated pointer.**
Onboarding writes `.studyforge/pin.json` — the installed library's version and
the commit it was built from — and a thin **skill stub** per skill into the
corpus. A stub names its skill, the pin it was written at, and the command that
prints the procedure from the installed package; ⛔ **it carries no path at all.**
⛔ **A stub that has drifted from its pin is a build failure**: the generated
`test_framework_pin.py` fails when a stub names another pin, or when the library
the corpus's Python imports is not the pinned version or was not built from the
pinned commit; a library with no commit stamp is reported as unverifiable, never
passed. That is what stops a stub
becoming a fork by accretion — the same shape as pinning a published image tag
rather than forking a Dockerfile.

### A page that hands a reader a command declares the modules it does not own

Every `docs/authoring/` page and every shipped `SKILL.md` that gives a
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
fence and the reader drift apart. ⛔ **The exemption belongs to the page that declares
it**, so a module declared consumer-side on one page earns nothing on another. ⭐ **Why a
declaration and not a list:** a list of exempt modules kept beside the checker is a
second copy no page's reader can see, and a skill that sends a stranger to run a module
absent from the repository they are standing in is a first-run failure the stranger
cannot diagnose.

---

## 10. Out of scope

Named explicitly so nobody builds them by accident.

- Cross-corpus dedupe, concept equivalence, and multi-variant merged units.
- Search across corpora.
- Ragged-depth hierarchies (§4).
- Transliterating non-ASCII titles into slugs (R9's stated limitation).
- Packing generated media other than narration out of git: only clips have
  release volumes (§5).
- A per-corpus visual theme: every site wears the one framework identity (§8.4).
- A model at build time or at serve time (§7).
- Mounting the Docker socket into the serving process, in any form (§8.3).

---

## 11. Acceptance

### 11.0 What a corpus is entitled to, and what it earns

⛔ **A corpus is complete when it delivers everything its material supports —
not when it delivers everything the framework can do.** Two tracks, and the
manifest decides which apply:

**The reading floor — every corpus, always.** Units readable offline over
`file://` with no network and no server; narration, unless the corpus or the
run turns it off; a table of contents and a root index with working deep links;
navigation between units; the reader's own read marks. ⭐ **This is a complete
product on its own.** A corpus that stops here is not a degraded one — for prose,
a book, a paper collection or a set of notes, it is the whole thing, and R8's
floor means it needs nothing running. ⛔ **A corpus without narration is complete,
not short** (C5): no player, no clip served, no "missing" notice, and every clip
kept on disk (§4).

**Checked practice for any subject.** ⭐ **A corpus whose subject admits no
checkable coding task still gets checked practice — the quiz shape** (§7). A quiz
needs no container, no network and no model, so it sits **on the reading floor**,
not in the execution track; its answers are checked by the local study server,
which holds the key the page never carries, and over `file://` a quiz shows its
questions and says checking them needs that server.

**The execution track — only where the material is runnable.** A workspace, Run
and Submit, a pinned runner container, graded practices, and optionally the
browser editor. ⭐ **A corpus enters it when its subject admits a checkable coding
task**, whether or not the source ships a grader: the exercises are [authored at
ingestion](#exercises-authored-for-every-corpus). It is gated on the manifest's
`exercises` and `runtimes` (§4) and on §7's three states. ⛔ **A corpus whose
material admits no checkable coding task skipping this entire track is a pass**,
not a shortfall (C5); what is never a pass is a reader with nothing to practise
where the material supports practice.

⚠️ **The order follows from that.** The reading floor comes first and completely,
because it is what every consumer gets and the only thing some consumers want.
The execution track is added when a corpus needs it — a real decision about a
real source, not a stage everyone waits behind.

### 11.1 The framework

1. `studyforge validate` passes on a valid archive and fails, naming the
   specific failure, on each invalid fixture — **including a source whose
   material the adapter silently failed to read in full**.
2. A **depth-1** fixture and a depth-2 fixture both build, render and serve
   with **no corpus-specific code anywhere in the framework** (R1), asserted
   rather than assumed.
3. A corpus's units are readable offline over `file://` — no network, no server
   — with narration, syntax highlighting, working navigation, and read marks
   recorded and surviving a reload (§8.5).
4. The root index renders a hierarchy of any declared depth with working deep
   links. Its **only inputs** are the two contents documents — asserted; and ⛔
   **it fetches nothing at runtime** (§8.4).
5. `studyforge plan` names every path a build will create and every declared
   edit, before anything is generated, and what a build then does matches it.
6. No source module exceeds 400 lines and no test module exceeds 600, or the
   exception is stated and justified in the module's own docstring (R11).
7. Every package has tests, and the test tree mirrors the source tree (R12).
8. Tests, generation and serving all run in a container from a clean checkout,
   with Docker as the only prerequisite (R15).
9. Framework source imports only the standard library and itself, and the
   package declares no runtime dependency (§3.2).

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
    said so and stopped (§5).
14. ⛔ **It reaches the reading floor in full**, and whatever of the execution
    track its material supports: every page whose material admits a checkable
    task carries its planned exercises or quizzes, or the coverage report names
    that page with the gate that refused each one (§7). ⛔ **"Reading-only" is a
    reading the gates produced, never a default nobody tried to move.**

---

## 12. Validating that the framework is a framework

Everything in §11 is satisfied by a framework with exactly one consumer. The
claim this framework makes is larger, and it is only testable against a source
nobody designed for.

**The test is a source converted by the skills alone.** A real repository is
onboarded by reconnaissance → adapter authoring → corpus onboarding, with no
hand-authored framework code, and the result is judged against this section.

**How it is conducted.**

- ⛔ **Whoever integrates the source does not modify `studyforge`.** Anything the
  framework cannot do is filed as a **finding**, not patched. The framework pin
  does not move during the integration; where it must, every change it moves
  across is listed against the finding that forced it. ⭐ A test of extensibility
  run by somebody who can edit the thing being tested measures nothing.
- **The work is planned by the delivery-planning skill** (§9), acting as the
  product owner for that repository: an ordered backlog, made against the installed
  framework's offer, whose every task ends in something demonstrable, so the
  conversion is watchable step by step rather than reported finished at the end. A
  capability the source needs and the framework does not offer is a finding the
  plan files, and the task that needs it waits on it. ⭐ Its findings are the deliverable below, and it
  distils them into the integration catalogue so the *next* source starts further
  along.

**What it must assert.**

1. The corpus reaches the reading floor — readable over `file://`, navigable,
   read marks recorded, narrated where it asks to be — **minus what the source
   genuinely lacks.**
2. Every page whose material admits a checkable task carries its planned
   exercises or quizzes, or the coverage report names it with the gate that
   refused each one (§7). ⚠️ **Zero exercises is a pass only for material that
   admits no checkable task**, and the integration is never judged against a
   corpus that happens to ship its own graders.
3. The framework pin did not move, or every change it moved across is accounted
   for.
4. ⛔ **Everything the integrator did by hand is a defect in the onboarding
   skill, named.** That list is what turns "extensible" into something with
   edges.

⭐ **The deliverable is the findings log, not the site.** An integration that
produces a working study site and reports no findings has not been conducted
honestly — the odds that an unknown repository fits the skills perfectly are not
good. The finding count is the **yield**, not the failure: a negative result is a
successful experiment.
