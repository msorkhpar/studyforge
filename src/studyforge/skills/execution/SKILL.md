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

1. The corpus, already onboarded with its `runtimes` declared —
   `corpus.json` exists, declares this skill's files not material (onboarding
   does that for a corpus that declares runtimes), and `studyforge validate` is
   clean. That is the other skill's job
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
| ⭐ any engine, Windows included | writes every bind relative to the compose file, and every other store as a named volume or a `tmpfs` | an absolute, drive-letter, home or backslash bind source (`rulings.bind_findings`) |

⭐ **The file runs on Docker Desktop and on Windows** (a register direction).
Docker Desktop shares no host `/tmp` and Windows has none, so nothing is ever
mounted from a temporary directory, and a relative bind is the one form Compose
resolves on every host. ⭐ Every `docker` the framework runs is the plain CLI
with the caller's environment: `DOCKER_CONTEXT` (or the current context) picks
the engine, and nothing switches it. ⭐ The editor and the runner carry an
`org.studyforge.binds` label saying which directory of the corpus each mount
holds, so `studyforge serve` on the host knows them by that label and compose's
own working-directory label, never by the engine's spelling of a bind's source,
which on Docker Desktop for Windows is a path inside its VM (`execute.labels`).

⭐ **Per-project values arrive as compose interpolations with defaults**, so the
rendered file is complete with no argument and still adapts to the host it is on.
That is how *"sufficient from the contract alone"* and *"the port and the uid
differ per host"* are both true at once. ⭐ **The project name, the editor's
host port and both container names are among them** (`STUDYFORGE_PROJECT`,
`STUDYFORGE_EDITOR_PORT`, `STUDYFORGE_EDITOR_NAME`, `STUDYFORGE_RUNNER_NAME`, and
the study server's `STUDYFORGE_SITE_PORT` and `STUDYFORGE_SITE_NAME`),
each defaulting to the value it always had; ⛔ the loopback address stays
literal, so only the port number is ever interpolated.

⛔ **No editor bind reaches a quiz's key.** `binds.unkeyed` refuses a sources
or workspaces directory that is, holds or sits inside the bundles' or the
archive's directory: the key lives only in the page it grades, and the editor is a
process a reader opens any bound file in.

⛔ **The file has THREE services, and the editor binds its sources and two more directories:**

- ⭐ **The editor binds the practice workspaces beside the sources.** Every
  practice workspace — the source's own and every authored one — lives under
  the directory `emit` places them in (`corpus.placement.PRACTICE_DIRNAME`),
  which is not under the sources' common root. It is bound at the contract's
  workspace root under its own name, read from that one spelling
  (`binds.workspaces_bind`), and named in the list of bind sources that exist first.
  ⭐ `write` makes every directory the compose file binds (`Execution.bound`),
  so a corpus with no practices yet still starts with none made by hand. ⚠️ An editor that
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
- ⭐ **The study server is the third service** (`siteservice`), the installed
  library's `serve /corpus --published`, published on the editor's own
  loopback bind at `STUDYFORGE_SITE_PORT` — the same port inside and out, so the
  `Host` a browser sends is one `serve` admits. It is told the editor's browser
  origin (`http://127.0.0.1:${STUDYFORGE_EDITOR_PORT}`), the editor's binds and
  health URL, and the runner's service name, and hands the origin to a page
  through its run index: no built file names a port. ⭐ Its image is
  `${STUDYFORGE_SITE_IMAGE:-}` in the `site` profile, which step 5b's record turns
  on, so a corpus with no staged image still brings up the other two.
- ⛔ **The site reaches the runner over the compose network's internal side, and
  never through the Docker socket.** The runner leaves `network_mode: none` for
  the `runs` network, declared `internal: true` (no route out, as `none` had
  none), which only the site and the runner join; the editor, which hands a
  person a shell, stays off it. The runner runs the run service
  (`runservice.pl`, written beside the compose file and mounted read-only) in
  place of its idle command, still publishes no port, and runs only the argv
  in `.studyforge/execution/allowed/runs`, which the study server rewrites from
  the corpus's records before every run.
- ⚠️ **The run service asks for no credential, and this is why that is enough:**
  the only other member of its network is the site, the one process that may
  ask for a run at all; what it may ask for is an argv the records already name,
  run in the container where a reader's code already runs. A shared secret
  would be read from the same corpus by both containers, so it would guard
  nothing the allowlist does not.

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
- ⛔ **The prime is never reached through a link.** `write` refuses, before
  touching anything, a prime directory that is a symbolic link, or has one
  above it below the corpus root, or resolves outside `.studyforge`
  (`prime.linked`): pruning through a link would delete the author's files.
  A link inside the prime is removed as a link, never followed, and before
  anything is written.

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
fix** (R19) — ⭐ all but `instance.env`, which is the publisher's (step 5a). It is reverted the next time somebody runs step 5, and a tool that
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

⭐ **This checkout's instance** — its compose project, the editor's and the
study server's host ports and the three container names — is
`.studyforge/execution/instance.env`, **the one place a port is set, and the
publisher's file**. `write` writes the defaults there once, when there is no
file, and never overwrites it; ⭐ from then on a port set there BY HAND is never
a hand-edit finding (`written.PUBLISHERS`: the file is not recorded).
`record_instance` is the CHECKED way to change it — it keeps every value it is
not handed. A SECOND checkout of the same corpus on one host sets its own,
which the compose command and the study server both read:

    record_instance(execution, corpus, project=..., port=..., editor=..., runner=...,
                    site_port=..., site=...)

⛔ **A value that cannot work is refused by its name**, never reported as an edit
(`execute.preflight`): a port outside 1–65535, the editor's and the site's
ports equal, a container or project name compose would refuse, a key the file
does not carry (one that tries to set a bind is told why: the loopback address
stays literal in the compose file, and widening it needs the editor's
authentication), and a compose file publishing off loopback while the editor
runs `--auth=none`. ⭐ `studyforge serve` refuses before it binds, and the
compose file's `preflight` service (`studyforge preflight /corpus`, in the
site's image, read-only, no network) runs before every other service, each of
which `depends_on` it with `required: ${STUDYFORGE_PREFLIGHT:-false}`. Before a
site image is staged the editor and the runner start as they always did; the
staged `site.env` sets it `true`, because compose only warns about a failed
OPTIONAL dependency and starts every service anyway. ⭐ The site's healthcheck
asks its own page, so `up --wait` reports it healthy only once it answers.

### 5b. Stage the study server's image — from the library the corpus pinned

    from studyforge.skills.execution import stage_site

    staged = stage_site(corpus)            # Staged(tag, argv, written)

`stage_site` checks that the library this Python imports is the one
`.studyforge/pin.json` names — its version AND the commit its wheel was built
from — and ⛔ refuses otherwise, and refuses a source tree, which carries no
commit. It copies that library into `.studyforge/execution/site/library/`
(ignored), writes the build file beside it on a base pulled by digest, and
records `STUDYFORGE_SITE_IMAGE=<tag>` and the `site` profile in
`.studyforge/execution/site.env`. ⭐ The tag is a digest of exactly those
bytes. Run `staged.argv` from the corpus root: it is the one `docker build`.
⭐ The compose file's `site` service carries the same build (`context: ./site`),
so step 6's command builds the image the first time it is brought up, and
`EXECUTION.md` prints the same command ending `build site` for building it
alone: compose reads the tag from `site.env`, and no shell reads it first.
Re-run 5b when the library or the pin moves.

### 6. Build the images and bring all three up — one command

Run the runner's and the editor's `built_by` argv **from the component's
checkout** — each with the flag its block declares (`runner.prime.declared_by`,
`editor.prime.declared_by`) pointing at the written prime directory by its full
path. `EXECUTION.md` prints both lines with this corpus's directory in the slot,
says which of them carry the flag, and each builds the tag step 5a recorded for
it. Then, from the corpus root:

    docker compose --env-file .studyforge/execution/runner.env \
      --env-file .studyforge/execution/editor.env \
      --env-file .studyforge/execution/instance.env \
      --env-file .studyforge/execution/site.env \
      -f .studyforge/execution/compose.yaml up -d --wait

In PowerShell on Windows, the same command continues its lines with a backtick
(`EXECUTION.md` prints it on one line, which runs unchanged in both):

    docker compose --env-file .studyforge/execution/runner.env `
      --env-file .studyforge/execution/editor.env `
      --env-file .studyforge/execution/instance.env `
      --env-file .studyforge/execution/site.env `
      -f .studyforge/execution/compose.yaml up -d --wait

⭐ **Every command this skill prints runs in PowerShell as in a POSIX shell**,
so a course publishes and runs from Windows, on Docker Desktop. None carries a
substitution, a variable or `id -u`; each value is in an env file compose reads.

⭐ That one command starts the study server, the editor AND the runner, each
from the tag the corpus recorded — nobody sets an image variable by hand. Open
the site on `127.0.0.1:<STUDYFORGE_SITE_PORT>`; a Run, a Submit and an example's
test then run in the runner, through its run service. ⭐ To move a port, set
it in `instance.env` by hand or with `record_instance` (step 5a), and run the
same command again: nothing is rebuilt, and neither way is a hand-edit finding.

⛔ **Every port is published on `127.0.0.1` alone.** The editor carries no
password because loopback is its whole access control: a reader who widens
either bind must restore the editor's authentication first.

⭐ **Serving on the host stays the development path**: `studyforge serve <root>`
finds the same editor and runner by `instance.env` and reaches the runner with
`docker exec`, as it always has. ⛔ A corpus with these files declares its runner,
so its code never falls back to the host: with the runner down, nothing runs, and
each page hides Run, Submit and Run tests and says why.

⛔ **The framework never starts a container for you** (§8.3). Not behind a flag,
not "only locally". This skill writes a compose file and a document; the person
running it runs `docker compose`, and the study server — on the host or in its
container — never holds the socket.

---

## 7. A course's `main` stands alone — the learner tree and the split

⭐ A published course's `main` holds everything used to work with the course:
its material (its modules, `practice/`, the authored `exercises/`, its own
scripts, progress tracker and toolchain configuration, the built pages), the
narration restore scripts, and one Docker setup that builds and serves the
site, the runner and the editor with no studyforge, no toolchain checkout and
no narration service. Only what is about BUILDING the course moves to the
branch `studyforge/build`: ingestion, the build's documentation, the generated
conversion tests, assistant guidance files and the build's own records —
**moved, never deleted**. ⛔ The images do not carry what `main` keeps for the
engine's sake: `exercises/` and `scripts/` are in `.dockerignore`.

The step writes that tree; the split is a procedure run on it. ⛔ As in step
5a, the skill starts no process: the caller hands in a `run` that takes `(argv, cwd)`, which
runs one argv and answers `(exit code, stdout)`.

    from pathlib import Path
    from subprocess import DEVNULL, run

    from studyforge.skills.execution.standalone import classify, release, table, tracked

    def ask(argv, cwd):
        done = run(argv, cwd=cwd, stdin=DEVNULL, capture_output=True, text=True, timeout=300)
        return done.returncode, done.stdout

    course = Path("<course>")
    print(table(classify(course, tracked(course, ask))))   # the table alone
    released = release(course, Path("<empty dir>"), toolchain=Path("<checkout>"), run=ask)

- ⭐ `standalone.table` over `standalone.classify` prints the KEEP/MOVE table
  and writes nothing. KEEP is what
  serving, studying or working with the course uses (`corpus.json`, `archive/`,
  `practice/`, `exercises/`, `scripts/`, a progress tracker, a toolchain
  configuration such as `.sdkman`, the
  footprint's pages, every entry the prime mirrors, the licence, the built
  `.studyforge/<container>/` pages, `assets/`, the narration record and
  restore scripts, and `runservice.pl`, `prime/`, `code/`, `allowed/`).
  Everything else MOVEs, with its reason; an entry nothing recognises MOVEs and
  says so.
- ⭐ The vendored serving runtime is the import closure of the server's entry
  points (`served`), proved by importing and serving the fixture from that tree
  alone. ⛔ It holds no module in `FORBIDDEN` (no skill, no synthesis, no
  release client), and every edge it does not follow is declared in `DEFERRED`
  with its reason.
- ⛔ The toolchain checkout must compute the primed tags the course recorded
  (`runner.env`, `editor.env`), or it is refused: check out the toolchain commit
  the course was built with. Its builds arrive as data from the command its
  `consuming.json` names under `builds`; no Dockerfile is read (R18).
- ⭐ The tree holds `compose.yaml` (builds every image locally:
  `docker compose up -d --build`) and `compose.pull.yaml` (the same three
  services, images only), `course.env` (every variable at its default), a
  learner `README.md`, and `.studyforge/release.json`, the manifest whose
  `keeps` lists every path. ⛔ Every port binds `127.0.0.1`, every service runs
  as `1000:1000`, and every mount is a named volume: no host path, no socket.
- ⭐ Six images: three shared bases (`studyforge-serve`, `studyforge-runner`,
  `studyforge-editor`) and three thin course images (`<course>-site` in two
  narrations, `without-narration` and `with-narration`, `<course>-runner`,
  `<course>-editor`), all under `${STUDYFORGE_NAMESPACE:-studyforge-local}`.
  ⭐ The `without-narration` site's pages carry no `data-audio`, so a page asks
  for no clip and the console stays clear.
  ⛔ The namespace is a placeholder until the owner publishes.

### The split, step by step

1. Export into an empty directory with `standalone.release`.
2. In the course repository, branch `studyforge/build` from `main`: it keeps
   everything, so nothing is lost.
3. On a branch from `main` that will become the learner `main`:
   `git rm -r -q .`, copy the exported tree in, `git add -A`, commit.
4. ⛔ Check that `git ls-files` equals the manifest's `keeps`, line for line.
   A difference is a file the export wrote and did not list, or the reverse:
   stop and regenerate, never hand-edit.
5. Clone that branch alone into a new directory and prove it there:
   `docker compose up -d --build` with its own project name and ports; the site
   answers, a practice Submit runs in the runner, the editor opens a practice
   with no chat, the site works with no narration, and with the clips restored
   the `with-narration` target plays them. Then tear it down with
   `docker compose down -v --rmi all`.
6. ⛔ The editor built this way skips the toolchain's build-time session proofs:
   run the toolchain's activation and confinement proofs against it before any
   image is published.
7. Publishing is the owner's step, never this skill's. The commands, for the
   owner to run: `docker compose build` with `STUDYFORGE_NAMESPACE` set to the
   registry namespace, then `docker push` for each of the six images
   `.studyforge/release.json` lists, once per narration for the site.

⛔ An export is per platform (its `platform` argument, default this machine): an image's
build arguments name that platform's pinned downloads.

---

## What lands in the corpus

| path | what it is |
|---|---|
| `.studyforge/execution/compose.yaml` | the compose file, rendered from the contracts: the study server, the editor and the runner |
| `.studyforge/execution/runservice.pl` | the runner's run service, mounted read-only into it (step 3) |
| `.studyforge/execution/allowed/.gitignore` | keeps the run service's allowlist, which the study server writes, out of the repository |
| `.studyforge/execution/site.env` | the study server's image and the profile that brings it up (step 5b) |
| `.studyforge/execution/site/site.containerfile` | the study server's build, on a base pulled by digest; the library copy beside it is ignored (step 5b) |
| `.studyforge/execution/runner.env` | the primed runner's tag, as the component printed it (step 5a) |
| `.studyforge/execution/editor.env` | the editor's tag, primed as the contract declares, as the component printed it (step 5a) |
| `.studyforge/execution/written.json` | every file above and its digest, so a hand-edit to one is reported (step 5) |
| `.studyforge/execution/instance.env` | this checkout's project, site and editor ports and container names: the one place a port is set, the publisher's file, written once and never recorded as the skill's (step 5a) |
| `.studyforge/execution/toolchain.json` | the selection: the set, what is carried, what is not and why, and the two argv |
| `.studyforge/execution/prime/<tool>/…` | one project per seeded tool: the corpus's own build, and each module's source and test with what they name, re-rooted at the build |
| `EXECUTION.md` | what a reader opens first: what to build, what to run, and what this corpus declared |

⭐ Every one of them is **generated**, and each is declared
`content.not_material` so `studyforge validate` is clean the moment they exist.
⛔ **Onboarding writes those globs, not this skill**: onboarding owns
`corpus.json` and records its digest, so it declares this skill's `NOT_MATERIAL`
for every corpus whose manifest declares `runtimes` — run `reonboard` with
`runtimes` settled before this skill. ⛔ **`write` refuses a manifest that does
not declare them** (`declared.refuse_undeclared`), naming each path and that
remedy, before its first byte, rather than leave `validate` RED. An artifact
added without a glob is a RED test here rather than an `unclassified` finding
in somebody's repository.

---

## What this skill deliberately does not do

- ⛔ **It starts nothing.** No daemon, no socket, no `docker` invocation. The
  one process step 5a needs — the component's own `tag_from` — is handed in by
  the caller, and step 5b returns its one build's argv for the caller to run.
- ⛔ **It does not name a source.** Not one runtime, path or version in this
  package comes from knowing which corpus is being converted (R1).
- ⛔ **It does not copy the component's API.** Not a route, not a port number,
  not a mount path: every one is read from `consuming.json` at run time, so a
  component that moves one moves this skill's output with it.
- ⛔ **It does not write into the corpus's own files.** Everything is additive
  (R3), and the check onboarding generated keeps asserting it.
