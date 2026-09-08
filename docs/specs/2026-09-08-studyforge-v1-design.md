# studyforge v1 — design

**Date:** 2026-09-08
**Status:** approved for planning
**Scope:** the source-agnostic LMS framework, plus its first consumer — the
`Claude-senior-java-engineer` tutorial repository.

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

v1 delivers the framework and **one** adapter. The framework is *designed*
against four material shapes so the generalisation is real rather than
retrofitted, but only the Java adapter is built.

### The four shapes the contracts must fit

All four were **counted, not assumed** — the two tutorials were cloned and
inspected on 2026-09-08, and both differed materially from what was first
written here.

| Source | Container levels | Units | Runnable | Graders |
|---|---|---|---|---|
| `Claude-senior-java-engineer` | 2 — section → module | 166 | Maven multi-module | **168 test classes, authoritative** |
| CodeSignal | 2 — path → course | 1,290 declared | Gradle + Python, dockerised | hidden upstream; local tests advisory only |
| ISO-8583-jPOS-tutorial | **1** — group (fundamentals / server / client) | 38 (16 + 11 + 11) | no build file | prose scenarios in `TestCases.md` |
| Claude-SPARQL-tutorial | **1** — course | 19 | **yes** — Docker: Fuseki + Jupyter | none, but **every lesson carries an exercise** |

A contract that cannot express all four is wrong. A contract that requires
special-casing any of them is wrong.

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

**C3 — Raw HTML appears in real Markdown.** 18 of ISO's files contain it; the
Java corpus has none. SF-07's parser raises on anything it does not recognise —
correct behaviour that would stop an ISO ingest dead. The vocabulary needs raw
HTML, thematic breaks and blockquotes before any second source is attempted.

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

**R3 — Generation is non-destructive.** No existing file in a source repository
is moved, renamed, or rewritten. The LMS *adds* artifacts alongside the
material. The single stated exception for the Java repo is one additive
`<module>practice</module>` line in the root `pom.xml`; `OPS-05` asserts
nothing else changed.

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

**R9 — Contracts are versioned.** `corpus_api`, `container_api`, `raw_api`,
`unit.json` `api`, TOC schema version. An unknown version is refused, never
migrated in place at read time.

**R10 — Generated output is byte-for-byte reproducible.** No clocks, no
content hashes in filenames, no dependence on filesystem enumeration order.
The same inputs produce the same bytes on any machine.

**R11 — No file grows past the size a person can hold in their head.** Soft
ceiling **400 lines** for a module, **600** for a test module. A unit
approaching it becomes a **package** of focused modules with one clear purpose
each. This is inherited debt to be paid *during* extraction, not after:
CodeSignal's `backend.py` (2,743 lines) and `scaffold.py` (1,793) are ported as
packages, never as files. The test is not line count but the isolation
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

**R14 — Graphify is the project's knowledge index, and agents query it before
exploring.** Every repository in this project carries a built graph. An agent
answering a "where / what calls / how does X work" question **asks the graph
first** and reads files second. The graph is rebuilt when structure changes.
This is what keeps a task's context budget honest: the alternative is every
agent grepping the whole tree to re-derive what the graph already knows.

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

**R18 — Components are separate repositories, composed as submodules of one
workspace.** Each component — the framework, the toolchain image, the narration
service, each corpus — has its own remote and its own release cadence, and is
checked out under a single parent workspace so one directory holds a complete,
working system. **The parent's recorded submodule commits are the version
pin**: they capture exactly which combination of components a working
configuration used, which is what makes R9's per-contract versioning
reproducible *across* repositories rather than only inside them. A component is
never vendored, copied or forked into another; it is pinned.

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
    skills/      the authoring and conversion skills (§9)
  tests/         mirrors src/ package for package (R12)
  docker/        dev, test and serve images (R15)
  graphify-out/  the project's knowledge index (R14)

Claude-senior-java-engineer/      consumer 1 — built in v1
  ingest/         curriculum · lessons · sources · emit · audit
  exercise/       body-blanking · the two gates
  practice/       generated exercise sources (additive Maven module)
  docker/ docker-compose.yml
  index.html  .studyforge/{assets,archive,site.json}
  graphify-out/
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
{ "corpus_api": 1,
  "source": "java-senior",
  "title": "Senior Java Engineer",
  "levels": ["section", "module"],
  "variants": ["java"],
  "exercises": true,
  "placement": "sibling" }
```

`levels` names the **container** levels and fixes the depth. A unit is an
ordinal inside the deepest container. `variants` replaces CodeSignal's closed
`LANGUAGES` tuple, removing the framework's last dependency on
`tools/catalog/`.

| Source | `levels` | example address |
|---|---|---|
| SPARQL | `["course"]` | `sparql-tutorial` + unit 07 |
| Java-senior | `["section","module"]` | `concurrency/23-executors` + unit 02 |
| CodeSignal | `["path","course"]` | `kotlin-programming-for-beginners/getting-started-with-kotlin` + unit 03 |
| ISO-8583 | `["section","subsection"]` | `iso-fundamentals/data-elements` + unit 02 |

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
- `sibling` — output lands **beside the source file it was generated from**.

The Java repo uses `sibling`, because the material already has a layout the
reader knows and R3 forbids restructuring it:

```
Claude-senior-java-engineer/
  index.html                                     generated root index
  .studyforge/assets/                            shared css, js, prism, plyr
  .studyforge/archive/<address>/raw/java/unit-NN/lesson-1.json
  .studyforge/site.json                          discovery cache
  16-streams-api/
    README.md                                    UNTOUCHED
    README_4.4.1.md                              UNTOUCHED
    streams-api.section.html                     module page
    4.4.1-introduction-to-the-streams-api.unit.html
    4.4.1-introduction-to-the-streams-api.audio/*.mp3
    4.4.1-introduction-to-the-streams-api.practice/
```

**Every generated page carries a real name, never `index.html`.** Names come
from the unit's own numbering and title, so they are unique, human-readable in
a directory listing, and unambiguous to a scanner.

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

```json
// container.json — generalises CodeSignal's course-map.json
{ "container_api": 1,
  "address": ["concurrency", "23-executors"],
  "titles":  ["Concurrency", "Executors and Thread Pools"],
  "variant": "java",
  "ingested": "2026-09-08",
  "note": "…",
  "units": [ { "n": 1, "title": "Thread pools and the Executor framework",
               "practices": 1, "note": "…" } ] }
```

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

**Re-ingest semantics.** `content_sha256` covers a unit's blocks and answers one
question: *did the source change since we read it?* On re-ingest, a digest that
disagrees with the source means the material has been edited upstream. The
ruling: the archive is **replaced** and the change is **reported** (R6) — never
silently overwritten, and never silently kept. Anything derived from that unit
(pages, narration, exercises) is invalidated by the same signal. Without this,
a corpus drifts out of date with no symptom, which is the failure `layout.py`'s
docstring describes in a different guise.

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

Zero remains a **first-class outcome**, not a degraded one — ISO-8583 will have
few or none, and that is correct.

Each exercise declares a workspace — `main_path`, `test_path`, `run_command`,
`test_command` — plus `provenance` (`bundled` | `generated` | `user`) and
`trust` (`authoritative` | `advisory`). The framework refuses to render a
`generated` grader as authoritative (R5).

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
  mistaken for a defect in M6.

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

- **The unit of work is a batch of keyed segments, not one blob.** Today's
  client sends one request per unit and gets one mp3 back. But narration ids
  are positional and per-speech-unit (§8.3), and the page's highlight sync
  needs **one clip per speech unit** — so the API takes a list of
  `{id, text}` and returns one artifact per id plus a manifest. A batch rather
  than a request per segment because a corpus is thousands of segments, and
  per-request overhead is the difference between minutes and hours.
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

⚠️ **Synthesised audio is the one carve-out from R10.** A speech model is not
guaranteed to emit identical bytes for identical input, so audio is not
byte-for-byte reproducible the way generated HTML is. It is instead
**content-addressed and cached**: a segment whose text and voice parameters are
unchanged is never re-synthesised, and the manifest records the address. R10
continues to apply in full to every other generated artifact.

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
- **Narration** — positional (never content-derived) speech ids, display text
  and spoken text as two renderings of one list, clip-level highlight sync,
  audio generated and git-ignored.
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
- **Progress** — one git-ignored JSON file, read-validate-modify-write under a
  lock, atomic replace; `first_passed_at` set once and never moved.

---

## 9. The skills layer — what is actually being built

R16. The pipeline is the means; **the skills are the product.** The end state
is that somebody points a skill at material they care about — a course site, a
book, a paper collection, a repository of exercises, their own notes — and gets
this format back, then keeps it as a durable personal record they can review,
re-run and extend.

Four skills, and the division between them is the same seam as everywhere else
(R2): one understands *a source*, the rest are source-agnostic.

- **Reconnaissance.** Given arbitrary material, work out its shape: how deep
  the hierarchy is, what the units are, whether there are variants, whether
  anything is runnable, whether any grader ships with it. Produces a draft
  `corpus.json` and an honest report of what it could not determine. This is
  the only skill that reasons about unfamiliar material.
- **Adapter authoring.** Scaffold an adapter for that shape, against
  `studyforge validate` as the definition of done — so the skill's output is
  checkable by machine rather than by opinion.
- **Build and serve.** One invocation from raw material to a running site:
  ingest, validate, unit documents, pages, narration, contents, exercises.
- **Personal archive.** Export and re-import a corpus *with its progress* —
  code, practices, examples and what the reader has completed — so the record
  survives a machine, and a corpus can be handed to somebody else without its
  owner's progress leaking with it (R7).

**What this buys the Java repo:** it is built by the same skills anyone else
would use, so if the skills are awkward there, they are awkward everywhere.
The Java corpus is the proving ground, not a special case.

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

## 11. Acceptance for v1

1. `studyforge validate` passes on the Java repo's archive.
2. All **166** units are readable offline over `file://` — no network, no
   server — with narration, syntax highlighting, and working navigation.
3. The root index renders the full 10 → 45 → 166 hierarchy with working deep
   links, from `toc.json` alone.
4. Every exercise that ships has cleared both gates; the coverage report names
   every pair that did not.
5. Run and Submit work from the page against the dockerised Maven toolchain;
   only a passing Submit completes a practice.
6. `git status` in the Java repo shows **no modification to any pre-existing
   file** except the one `pom.xml` module line.
7. `ingest-audit` exits 0, or exits 1 naming exactly the known outliers.
8. No source module exceeds 400 lines and no test module exceeds 600, or the
   exception is stated and justified in the module's own docstring (R11).
9. Every package has tests, and the test tree mirrors the source tree (R12).
10. Tests, generation and serving all run in a container from a clean
    checkout, with Docker as the only prerequisite (R15).
11. The Java corpus was produced **by the skills** of §9, not by bespoke
    one-off scripts (R16).
12. Both repositories carry a current graphify index (R14).
