# Skill — execution onboarding

**Give a corpus whose material is runnable the three things the reading floor
does not need: a compose file for the browser editor and the runner, a
toolchain selection, and a prime project** — and the recorded tags of both
images. Everything below is derived from the corpus's own
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
2. `code-server-toolchain`, **installed or built beside the framework**, at the
   version you use. ⛔ Never vendored into the corpus.
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

    from studyforge.corpus.manifest import parse
    from studyforge.skills.execution import generate, write

    manifest = parse((corpus / "corpus.json").read_text(encoding="utf-8"))
    execution = generate(
        manifest,
        editor_text=...,     # code-server-toolchain's consuming.json, as text
        root=corpus,
        narration_text=...,  # narrate-service's consuming.json, as text, or None
    )

⭐ **Where the two texts come from:** each is the `consuming.json` at the root
of that component, **read at the version you installed or built** — never a
newer working tree than the images you run.
`narration_text` is optional: without it the reader's document says nothing
about narration and the narration contract's rulings are not asserted.

When `manifest.runtimes` is empty the result is **empty** —
`execution.runnable` is false, no paths, no text, no refusal — and you are done.

### 2. Select the toolchain

`toolchain.select(manifest.runtimes, editor)` answers three questions from data:

| question | where the answer comes from |
|---|---|
| which runtimes the editor carries | the contract's own selectable list, intersected with what the corpus declared |
| which declared runtime it will **not** carry, and why | the contract's `not_carried` block, quoted by key rather than explained here |
| how to build the image and how to ask it for its tag | the contract's own argv, with the declared set substituted into the slot it left |

⛔ **Never pin a tag you did not compute, and never edit one by hand.** The tag
is a function of the build's inputs, so a hand-made one names nothing. Step 5a
runs each image's `tag_from` in the pinned checkout and records what it prints;
nothing here does, and nobody types one.

⚠️ A runtime the corpus declared and the editor does not carry is **reported,
not dropped in silence** — it is a real difference between what a reader can
run in the browser and what a graded practice runs in the runner.

### 3. Render the compose file

`composefile.render(...)` writes one service per component block it is given,
and every value in it is read out of a contract. It refuses to emit a file that
breaks any of spec §8.1's four compose rules, and §8.3's socket rule besides:

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
differ per host"* are both true at once. ⭐ **The project name, the editor's
host port and both container names are among them** (`STUDYFORGE_PROJECT`,
`STUDYFORGE_EDITOR_PORT`, `STUDYFORGE_EDITOR_NAME`, `STUDYFORGE_RUNNER_NAME`),
each defaulting to the value it always had; ⛔ the loopback address stays
literal, so only the port number is ever interpolated.

⛔ **No editor bind reaches a quiz's key.** `binds.unkeyed` refuses a sources
or workspaces directory that is, holds or sits inside the bundles' or the
archive's directory: the key never leaves the local server, and the editor is a
process a reader opens any bound file in.

⛔ **The file has TWO services, and the editor binds its sources and two more directories:**

- ⭐ **The editor binds the practice workspaces beside the sources.** Every
  practice workspace — the source's own and every authored one — lives under
  the directory `emit` places them in (`corpus.placement.PRACTICE_DIRNAME`),
  which is not under the sources' common root. It is bound at the contract's
  workspace root under its own name, read from that one spelling
  (`onboard.workspaces_bind`), and named in the list of bind sources that exist first. ⚠️ An editor that
  binds the sources alone can open no practice file: the frame gets no URL.
- ⭐ **The editor binds the copy of the corpus's code too**
  (`binds.code_bind`), at the contract's workspace root under the name `code`:
  a lesson's link to a code file opens there, beside its test, and the test
  runs there, so the author's files are never what a run writes into. ⭐ The
  skill writes the copy's one committed file, an ignore file that ignores
  everything else in it, so the directory exists in every checkout before the
  start. ⭐ **A corpus whose material sits at its root** has no directory of its
  own that is not the repository, so the copy IS its sources bind
  (`binds.source_root`).
- ⭐ **The runner a Submit execs into is the second service**
  (`runnerservice`), every value read from the contract's `runner` block: the
  container name is `runner.run.name_template` with the corpus's `source` in its
  slot, which is the name `execute.commands.container_for` looks it up by; the
  corpus's root bound where `runner.mounts` says; its network mode, its init and
  its restart policy. ⛔ **Its image is `${<runner.image.env_var>:?…}` and never
  a tag**, which step 5a records.

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

`prime.prime_for(root, runtimes, seeded=…)` refuses, by name, a seeded tool
with no build file, and a build with no source or no test in it. ⚠️ **That
refusal is the whole point of the step** — it is the difference between an
unprimed image and an image that says it is primed.

⛔ **The prime is in the component's layout, and its names are the contract's.** The component warms **one project directory per seeded tool** and
refuses anything else at the prime's top. So each tool the corpus declares and
`runner.prime.seeds` names gets `prime/<tool>/`, holding the corpus's own
build **re-rooted at its build file's directory**: the shallowest directory
holding one of that tool's build files, every build file under it, and the
smallest real source and test inside it. A tool the contract does not seed gets
no directory, and a corpus that declares none gets no prime at all.

- ⭐ **A multi-module build is primed as a build.** Each module — each
  directory under the build that holds one of the tool's build files — gets its
  own smallest source and test (`specimens.per_module`), and each carries every
  file of the build it names, so the module compiles: a name resolves in its
  own module first, and in another module only when the file also names that
  file's directory, as its import does. ⚠️ Measured: the smallest pair across a
  whole 46-module build sat in two modules and did not compile together.
- ⭐ **A module that carries no code is primed through its build file**, never
  refused: the component's warmer resolves what that file declares whether or
  not the module compiles anything. Only a BUILD with no source or no test at
  all is refused.
- ⚠️ **A test that fails in the corpus's own build is the corpus's finding**,
  named by the component's warmer, and it does not fail the prime.
- ⭐ **A regenerated prime replaces the old one whole**: a file an earlier
  selection copied and this one does not is removed (`prime.stale_in`).

- ⛔ **Two builds for one tool at the same depth are refused**, naming both.
  The component warms one project per tool: make the rest its modules.
- ⛔ **An exercise is never part of the prime.** Nothing under `exercises/` is
  read, nor any workspace under `practice/` that a bundle on disk owns, so no
  exercise's build role is swept in. ⭐ The prime is the corpus's own declared
  build, and every dependency an exercise names must be declared there too.

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
  image's seed holds them and the tool finds them with no flag.

⚠️ **Nothing checks the two agree except the gates, and that is enough:** the
authoring skill runs every gate in the pinned runner image, so an exercise
whose build names something the prime did not warm fails `G1` and never ships.

⭐ **Every run's output lands in `target/` inside the exercise's workspace**
(`exercise.bundle.RUN_OUTPUT_DIRNAME`), the report included — so the corpus
ignores every run artifact with the one line `target/`
(`RUN_OUTPUT_IGNORE`) in an ignore file of its own under `practice/`. ⛔ Never
an edit to the corpus's root ignore file (R3).

### 5. Write, and re-run whenever anything moves

`write(execution, corpus)` writes every generated file and **re-running changes
nothing**: the same manifest and the same contract render the same bytes.

⛔ **A hand-edit to any of these files is a finding against this skill, not a
fix** (R19). It is reverted the next time somebody runs step 5, and a tool that
eats your changes is a tool nobody runs twice. ⭐ **It is also REPORTED:**
`write` and step 5a record each file's digest in
`.studyforge/execution/written.json`, and onboarding's `hand_edited` names, in
a sentence, every one whose bytes moved or that is gone. Running the skill
again over an unchanged corpus rewrites no byte, that record included.

⛔ **A reader's document this skill did not write is refused, and the refusal
writes nothing.** `write` reaches every refusal before its first byte, so a
refused run leaves every file it would have written as it was, the compose
file included. ⭐ **The skill knows its own document** by either of two
answers: a line opening with `onboard.MARK`, the unchanging first sentence of
the generated notice, or `written.json` holding the digest of the bytes now
there. So a document an earlier version of the skill wrote is regenerated,
whatever the rest of its notice said then.

Customisation enters as manifest data; if the manifest cannot say it, the
manifest is missing a field and *that* is the finding.

### 5a. Record both tags — the skill does it, never the reader's typing

⛔ **A tag is a function of the build's inputs, so the only honest way to hold
one is to ask the build.** After step 5 — the runner's tag folds in the prime
on disk — call both, with the component's pinned checkout:

    record_runner(execution, corpus, component, ask=ask)
    record_editor(execution, corpus, component, ask=ask)

Each composes the contract's own `tag_from` for its image, with that image's
own prime flag (`runner.prime.declared_by`, `editor.prime.declared_by`) pointing
at the written prime — ⭐ one prime warms both images. ⚠️ A contract before
`provides` 3 declares no `editor.prime`, and its editor is then asked, printed
and recorded unprimed. Each hands that ONE argv to `ask` (which runs it and answers `(exit code, stdout)`),
refuses anything but one tag of that image's own `repository`, and writes one
environment file:

| step | writes | holding |
|---|---|---|
| `record_runner` | `.studyforge/execution/runner.env` | `<runner.image.env_var>=<tag>` |
| `record_editor` | `.studyforge/execution/editor.env` | `<editor.image.env_var>=<tag>` |

⭐ `--print-tag` hashes files and starts no Docker; this package itself imports
nothing that can start a process, which is why the caller hands the one process
in. The `ask` in `record`'s own docstring is one that works.

⛔ **A hand-edit to either file is a finding against this skill.** Re-run 5a —
both calls — when the component's pin, the prime or the host's architecture
moves.

⭐ **This checkout's instance** — its compose project, the editor's host port
and both container names — is `.studyforge/execution/instance.env`. `write`
records the defaults there when nothing is recorded, and never overwrites it.
A SECOND checkout of the same corpus on one host records its own four, which
the compose command and the study server both read:

    record_instance(execution, corpus, project=..., port=..., editor=..., runner=...)

### 6. Build the images and bring both up — one command

Run the runner's and the editor's `built_by` argv **from the component's
checkout** — each with the flag its block declares (`runner.prime.declared_by`,
`editor.prime.declared_by`) pointing at the written prime directory by its full
path. `EXECUTION.md` prints both lines with this corpus's directory in the slot,
says which of them carry the flag, and each builds the tag step 5a recorded for
it. Then, from the corpus root:

    docker compose --env-file .studyforge/execution/runner.env \
      --env-file .studyforge/execution/editor.env \
      --env-file .studyforge/execution/instance.env \
      -f .studyforge/execution/compose.yaml up -d --wait

⭐ That one command starts the editor AND the runner, each from the tag the
corpus recorded — nobody sets an image variable by hand. Confirm the editor
answers the health path the contract names; a Submit then runs in the runner rather
than on the host.

⛔ **The framework never starts a container for you** (§8.3). Not behind a flag,
not "only locally". This skill writes a compose file and a document; the person
running it runs `docker compose`, and the study server never holds the socket.

---

## What lands in the corpus

| path | what it is |
|---|---|
| `.studyforge/execution/compose.yaml` | the compose file, rendered from the contracts: the editor and the runner |
| `.studyforge/execution/runner.env` | the primed runner's tag, as the component printed it (step 5a) |
| `.studyforge/execution/editor.env` | the editor's tag, primed as the contract declares, as the component printed it (step 5a) |
| `.studyforge/execution/written.json` | every file above and its digest, so a hand-edit to one is reported (step 5) |
| `.studyforge/execution/instance.env` | this checkout's project, editor port and container names (step 5a) |
| `.studyforge/execution/toolchain.json` | the selection: the set, what is carried, what is not and why, and the two argv |
| `.studyforge/execution/prime/<tool>/…` | one project per seeded tool: the corpus's own build, and each module's source and test with what they name, re-rooted at the build |
| `EXECUTION.md` | what a reader opens first: what to build, what to run, and what this corpus declared |

⭐ Every one of them is **generated**, and this skill declares each as
`content.not_material` so `studyforge validate` is clean the moment they exist.
⛔ An artifact added without a glob is a RED test here rather than an
`unclassified` finding in somebody's repository.

---

## What this skill deliberately does not do

- ⛔ **It starts nothing.** No daemon, no socket, no `docker` invocation. The
  one process step 5a needs — the component's own `tag_from` — is handed in by
  the caller.
- ⛔ **It does not name a source.** Not one runtime, path or version in this
  package comes from knowing which corpus is being converted (R1).
- ⛔ **It does not copy the component's API.** Not a route, not a port number,
  not a mount path: every one is read from `consuming.json` at run time, so a
  component that moves one moves this skill's output with it.
- ⛔ **It does not write into the corpus's own files.** Everything is additive
  (R3), and the check onboarding generated keeps asserting it.
