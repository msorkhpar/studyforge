# studyforge v1 — design

**Date:** 2026-09-08 · **revised 2026-09-09**
**Status:** approved for planning
**Scope:** the source-agnostic LMS framework, plus its first consumer — the
`Claude-senior-java-engineer` tutorial repository.

⚠️ **The 2026-09-09 revision** re-read this design against 32 hours of further
CodeSignal work, and against a decision taken since: after v1 is accepted, a
second, unnamed repository is converted by the skills alone, as the test that
this is a framework rather than one pipeline with a good vocabulary (§12).
That lens changed the priorities. What it added: R3 generalised from one
hardcoded exception to a declared set (§4, R3); R19 and the corpus-onboarding
skill (§9); the placement dry-run (§5); provenance in the archive (§6); progress
as two records (§8.5); clip filenames carrying a digest (§8.2); and the ruling
that a skill precedes the artifact it produces (§9). Findings that were
CodeSignal's operational detail rather than this framework's concern were
deliberately **not** carried; they are in `docs/tasks/v2-backlog.md`.

---

## 1. What this is

`studyforge` turns **any body of teaching material** into a local, offline study
site: a reading page per unit, narrated, navigable, with a table of contents,
progress tracking, and — where the material supports it — runnable practices
with real graders.

It is extracted from the CodeSignal study system, which proved every one of
these surfaces against real material. What CodeSignal did for one source,
`studyforge` does for any source. The framework's own docs already anticipated
this; `backend.py` states it outright:

> *"a second source — another course site, a book, a repository of exercises —
> must be able to populate the same API and get the same tutorial site out of
> it. The endpoint shapes are the contract; the reading page is a consumer of
> them."*

v1 delivers the framework and its **first consumer**. The framework is *designed*
against four material shapes so the generalisation is real rather than
retrofitted.

⚠️ **The first consumer is a small corpus, and it is deliberately not the
largest one available.** An earlier plan made the 166-unit Java tutorial both
the first adapter and the definition of done, which welded the framework's
milestones to one source's shape — the exact conflation R1 exists to prevent.
Building against something small first means the framework reaches a **complete,
useful state** early, and the Java corpus becomes a consumer like any other
rather than the reason the framework exists. ⭐ A framework proven on a small
source and then applied to a large one has been tested; one grown around a large
source and later pointed at a small one has been fitted.

### The four shapes the contracts must fit

All four were **counted, not assumed** — the two tutorials were cloned and
inspected on 2026-09-08, and both differed materially from what was first
written here.

| Source | Container levels | Units | Runnable | Graders |
|---|---|---|---|---|
| `Claude-senior-java-engineer` | 2 — section → module | 166 | Maven multi-module | **168 test classes, authoritative** |
| CodeSignal | 2 — path → course | 1,290 declared | Gradle + Python, dockerised | hidden upstream; local tests advisory only |
| ISO-8583-jPOS-tutorial | **1** — group (fundamentals / server / client) | 38 (16 + 11 + 11) | no build file | **none** — amended below (`W339`) |
| Claude-SPARQL-tutorial | **1** — course | 19 | **yes** — Docker: Fuseki + Jupyter | none, but **every lesson carries an exercise** |

A contract that cannot express all four is wrong. A contract that requires
special-casing any of them is wrong.

⛔ **AMENDED 2026-09-18 (`W339`) — ISO's *Graders* cell read *"prose scenarios in
`TestCases.md`"*, and that file is OUT by the user's ruling** (`Q5`, final,
recorded at [PO round 105](../tasks/BOARD-ARCHIVE.md#po-round-105)). ⭐ **The
corpus carries no graded practice at all, so it is complete at the reading
floor, not short** (§11.0, C5). ⚠️ A planner reads this column to decide whether
a corpus enters the execution track, which is why the cell is corrected here
rather than left to a later reader: `tests/test_spec_corpus_table.py` reads the
*Graders* column against the manifest each workspace-pinned corpus carries, and
a row claiming graders for a corpus whose manifest says `exercises: false` is
refused.

### What the two tutorials taught us

Neither behaved as first described, and each surfaced a constraint the design
would otherwise have met late:

**C1 — A hierarchy can be encoded in filenames, not directories.** ISO's three
groups live in one flat `src/`, distinguished only by prefix: `1.md`…`16.md`,
`s1.md`…`s11.md`, `c1.md`…`c11.md`. Nothing in the filesystem expresses the
grouping. This is a **validation** of R4, not a problem: the adapter maps prefix
to group, and the generated artifact beside `s4.md` is locatable only by the
identity it carries internally. A design that inferred meaning from paths would
have failed here.

**C2 — A corpus can carry the same material twice, at different granularities.**
ISO ships both per-unit files *and* whole-series aggregates (`ISO.md` 3,858
lines, `Server.md` 2,813, `Client.md` 2,509). An adapter that globs `src/*.md`
ingests everything twice and nothing complains. The manifest must be able to
declare what is in and what is out, and reconnaissance (§9) must detect the
overlap rather than leaving it to be noticed.

**C3 — Real Markdown carries constructs a strict parser must already know.**
SF-07's parser raises on anything it does not recognise — correct behaviour, and
the reason the vocabulary has to be right before a second source is attempted
rather than after.

⚠️ **Recounted 2026-09-09; the first draft of this constraint attributed it to
the wrong repository.** It said "18 of ISO's files contain raw HTML". With code
fences stripped, ISO has **0 of 38**: the 26 files carrying `<tag>`-shaped text
are all XML *inside fenced blocks* — Maven POM, Spring beans, jPOS channel
configuration. The requirement survives; its constituency moved, and moved
**earlier**:

| Construct | Where it is actually measured | Consequence |
|---|---|---|
| raw HTML | **SPARQL, 6 of 19** — `<details>`/`<summary>` | a v2 source, but see below |
| thematic break | **Java, 10 of 166** | consumer 1, at M9 |
| blockquote | **Java, 1 of 166** | consumer 1, at M9 |
| **XML inside a fence** | **ISO, 26 of 41** | the real ISO constraint |

⭐ **So the ISO constraint is fence-awareness, not tag counting.** A parser that
scans for `<` without tracking fences reads a `pom.xml` sample as markup and
either raises — stopping the ingest dead, which is the failure this constraint
predicted by the wrong route — or renders it as HTML. That is a testable
property and `FND-04` carries a fixture for it.

⛔ **And a disclosure is a third state, not markup.** All six SPARQL uses hide an
*exercise answer*. Flattening `<details>` into ordinary blocks keeps the text and
destroys the hiding — the answer is then shown outright. Storing the tags as one
opaque raw-HTML block keeps the hiding and makes the body invisible to
everything else: uncounted, unhighlighted, unreachable by the block-count gate.
⭐ **Both fail, oppositely, and the resolution is the one C5 already taught this
project: "shown" and "absent" are not the only states.** *Present but withheld*
is real content, and it gets a container block of its own — `disclosure`, holding
blocks exactly as `quote` does. §7's speakable ruling then decides what narration
does with it.

**C4 — Material includes companion files that are neither blocks nor media.**
SPARQL ships `.ttl` datasets its lessons load and two Jupyter notebooks. A
reader needs them; they are not prose, not images, not video. The archive needs
an **attachment** class — a file a unit references and the reader must be able
to open — distinct from the media the page renders inline.

**C5 — An exercise can exist with no grader, and that is not "no exercise".**
All 19 SPARQL lessons end in an exercise or challenge; none has a test. The
first draft of §7 collapsed this into "zero exercises", which would have
discarded real teaching content. The exercise contract must distinguish three
states, not two: **no exercise**; an **ungraded** exercise (a prompt the reader
works, with nothing to check it); and a **graded** exercise, whose trust is then
`authoritative` or `advisory` under R5. Only the third can complete a practice.

---

## 2. Governing rules

These are rulings, not preferences. A task that violates one is not done.

**R1 — The framework knows nothing about any source.** `studyforge` must not
import from, name, or branch on any adapter. Every source-specific fact
arrives as data, through the manifest or the archive.

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
belongs to are in [`../tasks/E09-delivery.md`](../tasks/E09-delivery.md).**

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

**R6 — Fail loud, never silently short.** A unit with no content, a broken
curriculum link, an unmatched class, a declared practice that is absent — each
is reported by name and exits non-zero. Inherited from CodeSignal's
`run_capture_audit` and the reason `layout.py` exists at all.

**R7 — No personal data reaches disk or the wire.** Every string entering the
archive passes `assert_clean`, which **refuses** rather than rewrites. No
absolute home path, account id, name or email in any generated file, log or
report.

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

**R12 — Every module ships with its own tests, and the test tree mirrors the
source tree.** A module without tests is not done. A package's tests are split
the same way the package is, so a failing test names a module, not a subsystem.

**R13 — Markup, styling and scripts are source files, never code strings.**
Templates in template files, CSS and JS in asset files, loaded and composed by
code. Inherited from CodeSignal, where 80 KB of triple-quoted strings meant
changing a colour required editing Python. Loop bodies and inline wrappers stay
in code — a template file for a closing tag removes no duplication.

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
| `corpus_api` | **required** | R9's version key. An unknown value is refused, never migrated. ⭐ **`2` added `content.not_material`** (ruling 90), ⭐ **`3` added `media.max_files`** (`W207`) and ⭐ **`4` added `runtimes`** (`W350`); this build reads `1`, `2`, `3` and `4` |
| `source` | **required** | ⛔ **A corpus id, not a fetch URL** (ruling 51) |
| `title` | **required** | |
| `levels` | **required** | Names the *container* levels and fixes the depth |
| `variants` | **required** | ⛔ Filing and presentation only — never *runnable* |
| `exercises` | **required** | §7's gate onto the execution track |
| `runtimes` | *optional* | Names, never versions, from a closed vocabulary. ⛔ **Absent means none: no runner, complete at the reading floor** (§7, C5) |
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
framework's, not each corpus's** (`Q9`, ruled at [PO round 107](../tasks/BOARD-ARCHIVE.md#po-round-107); landed by `W347`).
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

⭐ **A build's output is committed too: its pages, the root index, the asset bundle and
`site.json`** (PO round 78, `W242/1`). The same argument holds: a clone that ignores its pages
has no reading floor. ⛔ **So the only generated ignore rules are the media policy's, written
inside the generated directory they are about and never in the root ignore file (R3).**
⚠️ This dates Ruling 91's first half, which declared `sibling` output in `.gitignore`.

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

⛔ **Raw HTML IS in the vocabulary: it is the `html` block, the Markdown reader emits it for a run of block-level markup, and the page renders it VERBATIM — the one block type that bypasses escaping, by declaration and never by what its text looks like** (`Q2`, `W347`). ⭐ It stays: nothing is removed and `raw_api` does not change. ⚠️ The question was ruled at [PO round 107](../tasks/BOARD-ARCHIVE.md#po-round-107) on the premise that raw HTML was *not* in the shipped vocabulary; that premise was measured wrong, and the register corrected it in its round 113. A tag-shaped line the reader keeps as a `para` is still escaped (`render/page/blocks/verbatim.py`).

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
ruling recorded at [PO round 107](../tasks/BOARD-ARCHIVE.md#po-round-107); landed by `W347`). ⚠️ So the refusal above does not
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
  with blocks and **no `exercise` key**. **graded** — the key is present. So the
  common case is a corpus that writes nothing: ISO is `none` for all 38 units and
  writes no practice document at all; SPARQL is `ungraded` for all 19 and writes
  a prompt with no workspace. ⛔ A design in which every corpus must declare its
  emptiness is a design fitted to the Java repo, which is the exception (§11.0).
- **R5 gets one place to enforce.** `provenance` and `trust` sit on the same
  document, so `studyforge validate` refuses `trust: "authoritative"` alongside
  `provenance: "generated"` — one rule, one file, exit 1.

⛔ **`trust` is declared but never believed.** An adapter writes what it claims;
the framework checks the claim against `provenance` and refuses the combination
R5 exists to prevent. `EX-04` writes the same key for a generated grader that
cleared both gates — the same document, because a generated grader is still
archive content — and it may only ever write `advisory`.

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
  docker creates it root-owned; the backend creates it and the container waits
  on the backend's health check.

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
guesses a language** (`Q7`, ruled at [PO round 107](../tasks/BOARD-ARCHIVE.md#po-round-107); landed by `W347`). ⚠️ A guess is a
silent wrong highlight, which is worse than no highlight. ⭐ A `code` block
whose `lang` is empty carries no highlighter class and the caption `code`
(`render/page/blocks/figure.py`).

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
2. ⭐ **It runs BEFORE the execution track, not after v1 is otherwise accepted.** ⛔ **ISO never enters that track (zero build files, graders and exercises; Q18), so at `M5` and `M7` it passes with zero exercises (§7, C5), and those milestones are proved on the framework's own fixtures.**
3. ⭐ **`Claude-senior-java-engineer` then re-validates the framework at `M9`** (`QA-05`), ⛔ **under every rule in this section.**
4. ⛔ **The no-patch rule holds for the integrator of `M8` and of `M9`.** ⭐ **Between them, `M5` and `M7` are framework work, and every commit the framework pin moves across is listed (bullet 1 above).**
