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

---

### TC-01 — Extract the image into its own repository
**Milestone** M5 · **Depends on** — · **Team** pair
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

---

### TC-02 — Toolchain selection and pinning
**Milestone** M5 · **Depends on** TC-01 · **Team** pair
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

**Acceptance.** A Java+Maven-only build produces a working image measurably
smaller than the full one. A full build still produces today's image. Selecting
a toolchain that is not pinned fails with a clear message. Every selected
toolchain reports its version at build time.

---

### TC-03 — Cache-priming contract
**Milestone** M5 · **Depends on** TC-01 · **Team** pair
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
**Milestone** M5 · **Depends on** TC-01 · **Team** solo
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
**Milestone** M5 · **Depends on** TC-02, TC-03 · **Team** solo
**Owns** `TC/docs/consuming.md` and a reference compose fragment
**Context** ~35k — `CSD/docker-compose.yml` code-server service, spec §8.1

**Definition.** The consumer-side half of the seam, documented rather than
shipped: what a project must provide, and the rulings it must not break. A
reference fragment shows the shape; it is a template to copy and adapt, never
an included file, because the mount list is exactly the part that must differ
per project.

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

---

### TC-06 — Versioning and consumer pinning
**Milestone** M5 · **Depends on** TC-02 · **Team** solo
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
