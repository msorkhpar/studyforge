# E12 — Toolchain image (shared repository)

The embedded IDE is the most reusable thing CodeSignal built, and it becomes
its own repository: **`code-server-toolchain`**. Spec §8.1 is the authority for
this epic and should be read in full before starting any task in it.

**The seam.** The **image** is shared; the **compose file and its mounts** are
not. A consuming project supplies its own compose file, its own mount list, its
own container name and port, and a `prime/` project to warm the build cache.
Everything else — toolchains, extensions, the workbench lockdown, seed
settings, the entrypoint — comes from the image.

**Why this is a separate repo rather than a directory.** Three consumers
already exist or are planned (CodeSignal, the Java corpus, any future adapter),
each on its own release cadence, and the image is the one component whose
correctness is established by *measurement* rather than by reading code. A
consumer pins a tag; it does not fork a Dockerfile.

**Rulings that bite here:** R15 (containers), R10 (reproducible builds), R17
(document the contract).

⚠️ **Everything in spec §8.1's bullet list was measured, and none of it is
obvious.** A task that "simplifies" one of them without reproducing the
original failure has introduced a regression that will surface as a silent
misbehaviour — an extension that never loads, a tool that is missing only in
the terminal, a volume the server cannot write. Read §8.1 first.

⭐ **This epic is the head of the execution track (`TC-00`, M5), and nothing
before it needs it.** A corpus reaches the whole reading floor — narrated, navigable,
offline — without a container ever starting (spec §11.0), so putting a Docker
image in front of somebody converting a book was the wrong shape.

⚠️ **It briefly sat at M0–M2 on the theory that `SK-07` could not render a
compose file without `TC-05`.** True, and resolved the other way: onboarding
split, and `SK-09` — the execution half — lives with the contract it
needs, at M7 since PO round 74. `SK-07` at M2 generates the reading floor's artifacts and asks for no
container.

⭐ **It still depends on nothing in the framework**, so under a two-agent split
it remains work the framework agent can pull forward whenever its own critical
path is blocked. What changed is that nothing *waits* for it.

⛔ **REORDERED PO round 74 — user direction, 2026-09-12:** *"We can even move the code-server to when after we are a framework! Because that functionallity is needed mostly for when exercises are in the picture."* ⭐ **So `TC-00`, the runner image, stays at `M5` and CREATES `TC/`; `TC-01`…`TC-06` add the code-server image to it at `M7`.** ⛔ **§8.1's measured list binds that image unchanged when it lands** (spec §8.1, amended).

---

### TC-00 — The runner image ⛔ UNBLOCKS EX-00 AND SF-44
**Milestone** **M5** · **Depends on** — · **Team** solo
**Owns** `TC/` — it creates the repository — and the runner image in `TC/docker/minimal/`
**Context** ~15k — spec R15, EX-00

**Definition.** A deliberately small image containing **only a pinned JDK and
Maven**, with no IDE, no extensions and no other toolchain. It exists because
`EX-00` is an M0 gate that must run builds, and R15 says a step whose result
depends on installed tooling runs in a container — while the editor's image is M7.

⚠️ **This is not an early draft of TC-01 and must not grow into one.** Its only
consumers are EX-00 and EX-02's gate runs. When TC-02 lands the pinned selection
for real, this image either becomes a profile of it or is deleted; what it must
never do is become a second place where a JDK version is chosen.

⭐ **The reason it earns its keep at M0** is that EX-00 decides the shape of all
of E08 from a wall-clock measurement, and a number measured on somebody's host
JDK cannot carry that decision.

⛔ **RE-SCOPED PO round 74 — user direction, 2026-09-12:** *"We can still have a dockerfile to run code in Java, Kotlin, Python, and Nodejs and maybe even shell and sql using an in memory database or whatver that course requires without the need of having the code-server to be deployed or shown in the web to client."*

- ⭐ **The runtime list is the user's REQUIREMENT, recorded here and not narrowed:** Java, Kotlin, Python, Node.js, and possibly shell and SQL against an in-memory database — ⛔ **or whatever the course requires.**
- ⛔ **R1: the framework knows no course, so the runtimes a corpus gets are DECLARED in its manifest, and this image builds the declared set from pinned versions.** ⚠️ **The manifest key is a contract change at spec §4, which this row's taker proposes before code (§9); it is not designed here.**
- ⛔ **No IDE, no extensions, never served to a browser.** The *"only a pinned JDK and Maven"* sentence above is superseded by the list; *"must not grow into TC-01"* stands.
- ⭐ **It CREATES `TC/`, and `TC-01` declares it** — the edge half of [`W156`](BOARD-ARCHIVE.md#w156-a-row-owns-inside-a-component-it-does-not-create-with-its-creator-in-the-same-step-and-no-declared-edge). ⚠️ **`TC-02` selects the editor's toolchains from THESE pins at `M7`, so a version is still chosen in one place.**
- ⚠️ **The Acceptance's *"the Java repository"* reads a consumer corpus** ([`W83`](rows/W83.md)), **and that corpus is `M9`'s.**

**Acceptance.** `mvn -o test` runs against the Java repository inside it. The
JDK and Maven versions are pinned by digest, not by tag. The image tag is
recorded where EX-00's report can name it. It contains no toolchain EX-00 does
not use.

---

### TC-01 — Extract the image into its own repository
**Milestone** **M7** · **Depends on** TC-00 · **Team** pair
**Owns** `TC/` — the repository, `Dockerfile`, `entrypoint.sh`, `seed/`
**Context** ~45k — spec §8.1, `CSD/docker/code-server/` (all of it)

**Definition.** Stand up `code-server-toolchain` as a repository and move the
image into it, preserving every measured property in §8.1 verbatim: pinned
versions with SHA-256 verification against the publisher's checksum; extensions
installed into an image directory and **verified**, failing the build on a
missing id; PATH exported in `profile.d` as well as `ENV`, because the
integrated terminal is a login shell and `/etc/profile` silently drops `/opt`;
named-volume mount points created in the image owned by the runtime uid;
`ENTRYPOINT` and `CMD` both re-declared because the base bakes arguments.

Every non-obvious line keeps — or gains — a comment saying **what broke without
it**. That is what makes the image maintainable by somebody who was not there.

**Acceptance.** The image builds from the new repository and is functionally
identical to CodeSignal's. A shell inside it finds every toolchain **both**
under `docker exec` and in the integrated terminal. The extension verification
fails the build when an id is removed. CodeSignal is not modified.

**Out of scope.** Parameterisation (TC-02) and any compose file.

⛔ **PO round 74:** `TC/` exists from `TC-00`, so *"stand up `code-server-toolchain` as a repository"* now reads *add the code-server image to it*, at `M7` (the user's direction, above).

---

### TC-02 — Toolchain selection and pinning
**Milestone** **M7** · **Depends on** TC-01 · **Team** pair
**Owns** the image's build-argument surface
**Context** ~35k — TC-01 output

**Definition.** Today's image installs JDK, Gradle, Kotlin, Node/TypeScript and
Python because one project needed all five. A shared image must let a consumer
choose: the Java corpus needs **JDK and Maven** and has no use for Kotlin or
Node; a future Python-only corpus needs neither. Introduces a declared
toolchain set with pinned versions and per-toolchain build arguments, so a
consumer builds only what it uses and a smaller image is the normal case.

**Maven joins the toolchain set** — CodeSignal is Gradle-only, and the Java
corpus is a Maven multi-module build.

Verification stays: every toolchain selected is checked for presence and
version at build time, and the build fails rather than shipping an image whose
contents do not match its arguments.

⚠️ **PO round 74: the runner's pins come first (`TC-00`, `M5`). This row selects the editor's toolchains FROM them and never chooses a second version.**

**Acceptance.** A Java+Maven-only build produces a working image measurably
smaller than the full one. A full build still produces today's image. Selecting
a toolchain that is not pinned fails with a clear message. Every selected
toolchain reports its version at build time.

---

### TC-03 — Cache-priming contract
**Milestone** **M7** · **Depends on** TC-01 · **Team** pair
**Owns** `TC/prime/` — the contract, and the Gradle and Maven warmers
**Context** ~40k — spec §8.1, `CSD/docker/code-server/prime/`

**Definition.** The build-time warm cache is what makes a reader's first
offline build work with no download, and it is the part of the image that is
inherently **per-consumer** — it must be built from *that project's* wrapper
and build files. This task turns an ad-hoc directory into a declared contract:
what a consumer supplies, where it is mounted during the build, and what the
image guarantees about the resulting cache.

Two carried rulings, both measured, both easy to lose:

- **The prime project's sources must be real.** A `NO-SOURCE` compile task
  never resolves the compiler classpath, so an empty prime primes nothing while
  appearing to succeed. Every compile and test task must actually run.
- **Version guards fail the build** when the prime project's pinned versions
  disagree with the image's build arguments, because a cache warmed for a
  different version is worse than no cache — it is a cache that misses in ways
  nobody looks for.

Adds a **Maven warmer** alongside the Gradle one: a trivial project against the
consuming repository's parent POM, resolving the plugin and dependency set into
a local repository the image ships.

⚠️ **Two facts about the Java corpus that make this harder than the Gradle
case.** It has **no Maven wrapper** — there is no pinned distribution to mirror
the way `gradlew` pins one, so the image's Maven version *is* the version, and
pinning it is this task's job. And its parent POM declares Testcontainers,
WireMock, Mockito, DataFaker, Awaitility and Logback as inherited test
dependencies **that no test actually uses** — but Maven resolves them for every
module regardless, so the warmer must pull the whole declared set or the
reader's first offline build fails everywhere. Warm what the POM declares, not
what the tests reference.

**Acceptance.** A first `gradle build --offline` succeeds in a container with
no network. A first `mvn -o test` succeeds likewise. A prime project with no
sources fails the build with the stated reason. A version mismatch fails with
the stated reason.

---

### TC-04 — Workbench lockdown extension
**Milestone** **M7** · **Depends on** TC-01 · **Team** solo
**Owns** `TC/lockdown/`
**Context** ~30k — `CSD/docker/code-server/lockdown/`, `CSD/docker-compose.yml` workbench settings

**Definition.** The practice-focus extension that makes an embedded IDE behave
like a practice panel rather than a general workbench, versioned and released
as an artifact of this repository rather than a folder in one project's build.
Plain CommonJS against the `vscode` module the workbench provides — no build
step, no dependencies — and its identifier is renamed off `codesignal.*`, since
it now belongs to no single consumer.

⚠️ **It is packaged into a `.vsix` and installed, never copied into the
extensions directory.** The workbench reads `extensions.json` and never scans,
so a copied folder is present, correct, and silently never loaded. Measured.
The build verifies it appears in the installed list.

**Acceptance.** The extension loads in a running container — verified from the
installed list, not from the file being present. Renaming the identifier breaks
no consumer that pins the documented id. The workbench lockdown behaves as it
does in CodeSignal today.

---

### TC-05 — Compose and mount contract
**Milestone** **M7** · **Depends on** TC-02, TC-03 · **Team** solo
**Owns** `TC/docs/consuming.md`, `TC/consuming.json`, and a reference compose fragment
**Context** ~35k — `CSD/docker-compose.yml` code-server service, spec §8.1

**Definition.** The consumer-side half of the seam: what a project must provide,
and the rulings it must not break. A reference fragment shows the shape; it is a
template to copy and adapt, never an included file, because the mount list is
exactly the part that must differ per project.

⭐ **The prose is for a person; a machine-readable twin is for the onboarding
skill.** R19 says the consuming half of a corpus is *generated*, and `SK-09`
cannot render a compose file from prose. So this task also publishes
`consuming.json`: the image tag, the ports, the required mounts and their
read-only flags, the uid/gid expectation, the environment variables and which
have no default, the healthcheck, and the toolchains present. ⛔ **A consumer
never reads the Dockerfile** — R18's "pinned, never vendored" is only true if
the pin carries enough to consume it, and reading the Dockerfile is the first
step toward forking it.

⚠️ **The two must not drift.** The document quotes the JSON rather than
restating it, and a test asserts every key the document mentions exists.

The four rulings a consumer inherits, each with its failure recorded:

- **Loopback-only port binding, never `0.0.0.0`.** This is an unencrypted IDE
  with a shell.
- **Mount only the sources** — not the repository, not `$HOME`.
- **Run as the repository owner's uid:gid**, or files created in the container
  are root-owned on the host.
- **A bind source must exist on the host before the container starts**, or
  docker creates it root-owned and the writer can never write it. Ordering is
  enforced by a health check, not by hope.

**Acceptance.** A consumer following the document reaches a working container
with only its own compose file. Each of the four rulings is stated with its
failure mode. The reference fragment is marked as a template, not an include.
**`consuming.json` is sufficient to generate a working compose file with no
other input** — demonstrated by `SK-09` doing exactly that, not asserted.

⚠️ **`TC-05/2`, corrected 2026-09-19 (`W400`): this clause — and the sentence
above it that says why `consuming.json` exists at all — named `SK-07` from their
first writing, and `SK-07` renders no compose file.** ⭐ **`SK-07` generates
the reading floor's artifacts; `SK-09` is the execution half that renders the
compose file, and it already depends on this task.** ⛔ **The demonstration is
owed by [`SK-09`](E11-skills-authoring.md#sk-09-execution-onboarding), whose own
Acceptance carries it.**

---

### TC-06 — Versioning and consumer pinning
**Milestone** **M7** · **Depends on** TC-02 · **Team** solo
**Owns** the image's release and tagging scheme
**Context** ~20k — TC-01…TC-03 outputs

**Definition.** How a consumer depends on this image without being broken by
it: a tagging scheme that encodes the toolchain set and its pinned versions, a
statement of what may change within a tag and what forces a new one, and a
short upgrade note per release saying what a consumer must re-verify. A
consumer pins a tag; nobody forks the Dockerfile (R10).

**Acceptance.** Two consumers can pin different tags simultaneously. A
toolchain version bump produces a new tag rather than mutating one. The scheme
is documented with a worked example.
