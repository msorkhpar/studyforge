# Skill — execution onboarding

**Give a corpus whose material is runnable the three things the reading floor
does not need: a compose file for the browser editor, a toolchain selection,
and a prime project.** Everything below is derived from the corpus's own
`corpus.json` and from the pinned component's own `consuming.json`. Nothing is
typed twice and nothing is typed here.

⛔ **Most corpora never run this skill, and that is the design** (spec §11.0).
The reading floor — narrated, navigable, offline, no server — is what *every*
corpus gets and is a complete product for prose material. A container is what a
corpus with **runnable code** earns. Folding this into corpus onboarding would
put a Docker dependency in front of somebody converting a book.

---

## When this skill does nothing, and says nothing

⭐ **A corpus is runnable when its manifest declares `runtimes`, and not
otherwise.** An absent key is `()` — no runner, no editor, no prime — and §7's
C5 says such a corpus is **complete**, not short.

⛔ **So a corpus that declares no runtime gets no file from this skill and no
error.** Not a warning, not a stub, not an empty compose file. The honest
answer to *"where is my container?"* for a book is *"your corpus never asked
for one"*, and a generator that emitted a broken compose file to avoid saying
so would be the theatre R5 forbids.

---

## Before you start

1. The corpus, already onboarded — `corpus.json` exists and
   `studyforge validate` is clean. That is the other skill's job
   (`studyforge.skills.onboarding`), and this one refuses to run before it.
2. `code-server-toolchain`, **checked out as a sibling at the commit
   `workspace.json` pins**. ⛔ Never a submodule and never vendored: nothing in
   this project is pushed to a remote, so a submodule URL has no legal form.
3. Docker on the host, for step 4 onwards. Steps 1–3 touch no daemon.

---

## ⛔ The one file this skill reads from that component

`consuming.json`, at the component's root, **and nothing else**.

⛔ **Never its `Dockerfile`** (R18). A consumer that renders its compose file by
reading a Dockerfile has forked the component: the next version of the image
moves a path the consumer copied, nothing refuses, and the two drift in silence
until a reader's build cannot write its own cache.

⛔ **Never its `README.md`, never its own renderer under `consuming/`.** Prose
is for a person and a second program is a second implementation. The contract
is machine-readable so that this skill can be a *reader* rather than a *port*.

⭐ **A key this skill needs and that contract does not carry is a FINDING
against the component, never a value written in here.** `contract.require`
raises and names the key path it wanted; that refusal is the finding's evidence.
The moment somebody answers such a refusal by typing the value into this
package, the component's contract has stopped being sufficient and nobody can
tell.

⭐ **The promise is recorded, never negotiated** (R9). `contract.EDITOR_PROMISE`
is the `provides` this renderer was written against. A component that provides
**less** is refused by name; a component that provides **more** is read, because
its own contract says new keys move `provides` and old ones keep working. A
`consuming_api` this skill does not know is refused outright: that field
versions the file's *shape*, and a shape nobody has read is not a shape to guess
at.

---

## The steps

### 1. Read the manifest, and stop here for most corpora

`Execution.for_corpus(manifest, ...)`. When `manifest.runtimes` is empty the
result is **empty** — no paths, no text, no refusal — and you are done.

### 2. Select the toolchain

`toolchain.select(manifest.runtimes, editor)` answers three questions from data:

| question | where the answer comes from |
|---|---|
| which runtimes the editor carries | the contract's own selectable list, intersected with what the corpus declared |
| which declared runtime it will **not** carry, and why | the contract's `not_carried` block, quoted by key rather than explained here |
| how to build the image and how to ask it for its tag | the contract's own argv, with the declared set substituted into the slot it left |

⛔ **Never pin a tag you did not compute, and never edit one by hand.** The tag
is a function of the build's inputs, so a hand-made one names nothing. Run the
printed `tag_from` command in the pinned checkout and record what it prints
beside the commit `workspace.json` pins.

⚠️ A runtime the corpus declared and the editor does not carry is **reported,
not dropped in silence** — it is a real difference between what a reader can
run in the browser and what a graded practice runs in the runner.

### 3. Render the compose file

`composefile.render(...)` writes one service per component block it is given,
and every value in it is read out of a contract. It refuses to emit a file that
breaks any of spec §8.1's four rulings, and §8.3's socket rule besides:

| ruling | what the renderer does | what it refuses |
|---|---|---|
| loopback only, never `0.0.0.0` | publishes every port on the contract's own host bind | a contract that asks for a published port on all interfaces |
| only the sources are mounted | emits exactly the binds the contract declares, with the corpus's source root in the one marked per-project | a second host path, and the repository or a home directory in any of them |
| the container runs as the repository owner | emits the contract's own `user:` interpolation | a block that declares no way to set the uid |
| a bind source exists before the start | names every mount that must exist first, in the file and in the reader's document | silence about one |
| ⛔ §8.3 — no Docker socket | emits none, anywhere, under any key | a contract that declares one |

⭐ **Per-project values arrive as compose interpolations with defaults**, so the
rendered file is complete with no argument and still adapts to the host it is on.
That is how *"sufficient from the contract alone"* and *"the port and the uid
differ per host"* are both true at once.

### 4. Build the prime project

⛔ **An empty prime primes nothing while appearing to succeed.** A `NO-SOURCE`
compile task never resolves the compiler classpath, so an image warmed with an
empty prime downloads the world on a reader's first offline build — and reports
nothing wrong until then.

⭐ **So the prime is made of the corpus's own build files and the corpus's own
smallest real source and test**, per declared runtime, copied rather than
invented. ⛔ **Nothing here authors a build file, a dependency version or a test
framework.** A version typed in this package is a version that disagrees with
the corpus the day the corpus moves, and §8.1's version guard would then fail a
build for a disagreement this skill created.

`prime.prime_for(root, runtimes)` refuses, by name, a declared runtime with no
build file, with no source, or with no test. ⚠️ **That refusal is the whole
point of the step** — it is the difference between an unprimed image and an
image that says it is primed.

### 4a. When a graded exercise imports a library

⛔ **A graded run is `--network none`, so every dependency an exercise's tests
import must already be in the runner image.** Two halves carry it, and both are
the corpus's data (R1):

- ⭐ **The exercise's build role.** An authored bundle lists its build files
  under `build` in `bundle.json` and ships them under `build/`; `emit` lays
  each into the reader's workspace, and the exercise's command names it by a
  workspace-relative path (`mvn -o -q -f practice/…/pom.xml test`). ⛔ No jar,
  no repository and no absolute path is ever written into the corpus.
- ⭐ **The runner's prime.** The image is built with `--prime` from a build
  that declares every dependency the exercises' build roles name, so the
  image's seed holds them (`W390`) and the tool finds them with no flag.

⚠️ **Nothing checks the two agree except the gates, and that is enough:** the
authoring skill runs every gate in the pinned runner image, so an exercise
whose build names something the prime did not warm fails `G1` and never ships.

⭐ **Every run's output lands in `target/` inside the exercise's workspace**
(`exercise.bundle.RUN_OUTPUT_DIRNAME`), the report included — so the corpus
ignores every run artifact with the one line `target/`
(`RUN_OUTPUT_IGNORE`) in an ignore file of its own under `practice/`. ⛔ Never
an edit to the corpus's root ignore file (R3).

### 5. Write, and re-run whenever anything moves

`Execution.write(root)` writes every generated file and **re-running changes
nothing**: the same manifest and the same contract render the same bytes.

⛔ **A hand-edit to any of these files is a finding against this skill, not a
fix** (R19). It is reverted the next time somebody runs step 5, and a tool that
eats your changes is a tool nobody runs twice. Customisation enters as manifest
data; if the manifest cannot say it, the manifest is missing a field and *that*
is the finding.

### 6. Build the image and bring the editor up

Run the `build` argv step 2 printed, with `--prime` pointing at the written
prime directory. Then run the `tag_from` argv, record the tag, and set the
contract's own image environment variable to it. Bring the compose file up, and
confirm the editor answers the health path the contract names.

⛔ **The framework never starts a container for you** (§8.3). Not behind a flag,
not "only locally". This skill writes a compose file and a document; the person
running it runs `docker compose`.

---

## What lands in the corpus

| path | what it is |
|---|---|
| `.studyforge/execution/compose.yaml` | the compose file, rendered from the contracts |
| `.studyforge/execution/toolchain.json` | the selection: the set, what is carried, what is not and why, and the two argv |
| `.studyforge/execution/prime/<runtime>/…` | the corpus's own build files, source and test, copied |
| `EXECUTION.md` | what a reader opens first: what to build, what to run, and what this corpus declared |

⭐ Every one of them is **generated**, and this skill declares each as
`content.not_material` so `studyforge validate` is clean the moment they exist.
⛔ An artifact added without a glob is a RED test here rather than an
`unclassified` finding in somebody's repository.

---

## What this skill deliberately does not do

- ⛔ **It starts nothing.** No daemon, no socket, no `docker` invocation.
- ⛔ **It does not name a source.** Not one runtime, path or version in this
  package comes from knowing which corpus is being converted (R1).
- ⛔ **It does not copy the component's API.** Not a route, not a port number,
  not a mount path: every one is read from `consuming.json` at run time, so a
  component that moves one moves this skill's output with it.
- ⛔ **It does not write into the corpus's own files.** Everything is additive
  (R3), and the check onboarding generated keeps asserting it.
