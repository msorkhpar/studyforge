# E05 — Serving and execution

Giving the site an origin, and letting the reader run their own code against
real graders.

**Shared context for this epic.** Serving is what a `file://` site *gains*, not
what it depends on (R8). The generated pages must keep working by
double-clicking; the server adds an origin — and an origin is what lets a page
call an API at all, since `file://` cannot.

**The separation this epic must not blur.** The server may not start a process;
only the runner may — a Run or Submit is a command the server hands to
`execute`, never a process it starts itself (`SF-22`). That is asserted by test,
not by convention, because a
server that can spawn is a server whose security posture has to be re-reasoned
every time a route is added. Commands come from a generated document on disk
and are handed over verbatim; **nothing a browser sends ever becomes a
command.**

**Rulings that bite here:** R7 (every output line is gated), R8 (`file://`
floor), R11 (the largest port in the project becomes a package), R12 (tests).

---

⚠️ **Concentration risk — read before scheduling this epic.** Three tasks carry
**more than half** the framework's real port surface: SF-19, SF-12 and SF-14.
The other ~23 framework tasks are an order of magnitude smaller each. "Most
tasks are solo" is therefore false comfort — the solo tasks are not where this
project lives. SF-19 is split below for exactly that reason. Note also that R12
implies roughly **18,000 lines of new test code** across the framework, which no
task budget currently names.

⚠️ **M3 is a serial bottleneck wearing a milestone's name**, and the plan should
say so rather than let somebody discover it. Two agents does not help here:
SF-19a is one task, it belongs to whoever owns the framework, and nothing splits
it further. Schedule around that rather than around the task count.

⭐ **Deliberately not restating line counts.** An earlier draft quoted three
exact figures; two of them were 9–21% stale within 32 hours (spec §8). A task
measures its own port surface at start and ports from HEAD.

---

### SF-19a — Serving API: content, assets, security
**Milestone** **M4** · **Depends on** SF-10 · **Team** team
**Owns** `serve/` — app wiring, `routes/content.py`, `routes/assets.py`, `security.py`, `caching.py`
**Context** ~90k — `CS/.pipeline/tools/study/backend.py` (**read by section, not whole**), `CS/.pipeline/tests/test_backend.py`

**Subtasks — each its own module (R11).**
(a) **Content namespace** — what a unit *is*. Cacheable, strong validators,
conditional requests.
(b) **Assets namespace** — the bytes. Range requests, weak validators.
(c) **Security** — loopback only, host allow-list, cross-site requests refused,
content policy.

**Definition.** Serves the material **as JSON**, so HTML is one renderer over
the content and not the content itself: changing a template must not be able to
break the data, and a second source must be able to populate the same API and
get the same site out of it. Serves generated files as static bytes unchanged,
so no page ever depends on the server existing.

The three-namespace split is the design's centre. A unit's content is
reproducible and identical on every machine; whether it exists *here*, and what
the reader has done, is local and changes underneath them. A consumer caches
the first aggressively and polls the second cheaply, and **neither can quietly
start deciding the other** — state is derived from the filesystem, so a record
claiming something exists with nothing on disk shows up as the disagreement it
is rather than being believed.

⚠️ **This is a 2,743-line module in CodeSignal and the single largest R11 debt
in the project.** It is ported as a package. A task that produces one large
module has not done the task. Read the source by section; do not load it whole.

**Acceptance.** Serves a corpus's content and assets. Content responses
revalidate correctly; conditional requests and ranges work. Cross-site and
non-loopback requests are refused. **No module of the package imports a
process-spawning library — asserted.** ⭐ `SF-22/6`: since Run and Submit the
package imports `execute`, which does, so the property is of `serve`'s own
modules — it reaches a process only through the runner, and only from the run
routes (`W361`). No module exceeds the size ceiling.

---

### SF-19b — Serving API: state, discovery, addressing
**Milestone** **M4** · **Depends on** SF-19a, SF-04, SF-13 · **Team** pair
**Owns** `serve/routes/state.py`, `serve/addressing.py`, discovery wiring
**Context** ~60k — SF-19a output, SF-04 and SF-13 outputs

**Definition.** The half of the API that is about *this machine*, plus the
routing and startup behaviour that makes the server corpus-agnostic.

**State is never cached and is derived from the filesystem**, never from a
record of intent — so a claim that something exists with nothing on disk shows
up as the disagreement it is rather than being believed. That derivation is the
reason the namespace split exists at all, and it is why state is separated from
content here rather than bolted onto it.

**Discovery wiring** (SF-04): the server is given a root and finds the corpus
itself, with no configured paths — which is what lets one instance serve two
corpora using different placement profiles.

**Acceptance.** Serves each `FND-04` fixture discovered at startup with no
configured paths. State responses never cache. N-segment addresses route correctly at
depth 1 and depth 2. Two corpora with different placement profiles serve from
one instance. A stale discovery cache is detected rather than trusted.

#### ⛔ Acceptance SPLIT by the PO, round 68 — `W80`, Ruling 151

> ~~Serves the Java corpus discovered at startup with no configured paths.~~

⛔ **A reading no framework office can take: that sibling has no manifest and no archive at its pin (`OPS-05/1`; R20, Ruling 173).** ⭐ **Framework half: the restated first clause.** ⛔ **The Java half is RE-HOMED to `OPS-03` (`M9` since PO round 74, integration side), `W77`'s shape — the one disposition `SK-03` and `OPS-05` also take.**

---

### SF-20 — Command runner
**Milestone** **M5** · **Depends on** SF-02, TC-00 · **Team** pair
**Owns** `execute/`
**Context** ~45k — `CS/.pipeline/tools/study/runner.py`, `CS/.pipeline/tests/test_runner.py`

**Definition.** The **only** package that runs a corpus's commands, and the
only package permitted to start a process — ⛔ **save two named sites, each of
which asks the local `git` a fixed question about a source checkout and runs
nothing a corpus supplies:** `validate/source/enumeration.py` (which of a
source's files git ignores) and `skills/onboarding/pin.py` (whether a checkout
holds the pinned commit). ⭐ **Any other package reaches a process only by
handing a command to `execute`.** A sweep over `src/` asserts the closed list,
and a process start planted anywhere else is refused by its module's name
(`W361`, `SF-20/4`). Two modes,
one contract: execute inside the toolchain container when it is up — so a run
from the page and a run from the reader's own terminal use the same toolchain,
daemon and caches, and therefore agree — and on the host otherwise. The mode is
probed and cached briefly, so a page polling for output does not re-probe on
every tick.

Output streams **line by line as the process writes it**, stdout and stderr
merged, ending in exactly one exit line: a status, or a timeout, or a stop.
Commands run in sequence and **the first failure ends the run**, so code that
fails to compile never gets its tests "run" against nothing — a green result
from an empty run is the worst possible outcome for a learner.

Each command starts in its own process session so a stop or timeout can kill
the whole group rather than orphaning children. **Every line passes the
personal-data gate before it is yielded** (R7) — build output prints paths, and
paths contain home directories.

⛔ **The container path must be PROVEN here, not assumed** (spec §8.3). It is
the one inherited mechanism with no deployment behind it: CodeSignal ships
`--no-docker` with `network_mode: host` and mounts no socket anywhere, so its
`docker exec` mode has never run in anger. Run/Submit, the E08 gates and R15's
whole reproducibility claim all rest on it.

⛔ **The socket is never mounted into the serving process** (§8.3, rule 2). The
runner reaches into the toolchain container from outside it. Not behind a flag,
not "only locally".

⛔ **PO round 74 — *"execute inside the toolchain container when it is up"* now names the RUNNER container, `TC-00`, which is up with no editor** (user direction; spec §8.1, amended). ⭐ **The edge is `TC-00`, re-pointed from `TC-01` (`PO-72/2`'s edge). The page's Run and the reader's terminal command (`SF-44`) go through this one runner, which is why they agree.** ⭐ **The terminal command takes this contract's two modes as they stand — the runner container when it is up, the host otherwise — ruled by the register as reversible** ([the record](BOARD-ARCHIVE.md#po-round-74-m4-closed-at-4d3c742-and-the-order-after-it-is-m6-m8-m5-m7-then-m9-user-direction)).

**Acceptance.** A failing compile stops before tests run. A timeout kills the
process group and emits the timeout exit line. Output containing a home path is
gated. Nothing a client sends can become a command — asserted. **Both modes
produce identical observable behaviour on the same practice — demonstrated
against a real container, not a mock.**

---

### SF-21 — Progress store
**Milestone** **M4** · **Depends on** SF-01 · **Team** solo
**Owns** `progress/`
**Context** ~40k — `CS/.pipeline/tools/study/progress.py`

**Definition.** The record of **practice passes** — facts established by a
grader run: **one git-ignored JSON file**, never a database, never inside served
content. It is what *this machine* has done, not what a unit *is*. Keyed by the
same address the run route uses, so a run and its record cannot name different
things; a key shape that disagrees with the page's is a pass recorded under one
name and read back under another, **with no symptom at all**.

⚠️ **This is half of the record, and the other half is SF-30** (spec §8.5). A
pass is established by a grader run, which required the runner, which required
the server — so it is written where the fact was established. A **read mark** is
the reader's own assertion, needs no server at all, and lives in the browser
(SF-30). ⛔ The state route may *report* a client's read mark; it may **never**
treat one as a pass.

**Only a test run can complete a practice.** A program that ran and printed
successfully has demonstrated nothing about its tests, and the page's Run
button must never be able to complete anything. The first pass is recorded once
and never moves again — a later failure does not un-pass a practice, and a later
pass does not make it newer.

⚠️ **`SK-06/1` (PO round 72): `record_run` is the only public write, so an archive merge appends runs.** It costs up to two runs over the larger count and many locked writes. ⭐ **The next row touching `progress/`, or `V2-12`'s sync, exposes a locked merge and a reader for a document not on disk. The steps are `handoffs/SK-06.md` § For dependents** ([the close](BOARD-ARCHIVE.md#po-round-72-sk-06-held-open-on-sk-063-so-step-44-and-m4-do-not-close)).

Every mutation is read-validate-modify-write under one lock, written to a
temporary sibling and atomically replaced, so a crash leaves either the old
file or the new one and never half of each.

⚠️ **CodeSignal's lock is a `threading.Lock` (`git -C CodeSignal grep -n 'threading.Lock()' -- '*progress.py'` → `<path>/progress.py:<n>:`), which
protects nothing against a second *process*.** That was safe there because one
server owned the file. It is not safe here: `SK-06` imports and merges progress
from outside the server, and `OPS-04` may run while the site is served. Use an
inter-process lock, or state explicitly why single-writer is guaranteed. Keys are sorted so the file is
stable under regeneration and a diff says what actually changed.

**Acceptance.** A run never sets passed. A crash mid-write leaves valid JSON. A
malformed file raises rather than being silently repaired. Keys sort stably.
The file is git-ignored.

---

### SF-30 — Reader state on the `file://` floor
**Milestone** **M2** · **Depends on** SF-11, SF-12 · **Team** solo
**Owns** `render/assets/study-progress.js`, the mark control in `render/page/`
**Context** ~30k — spec §8.5, SF-01's address

**Definition.** The reader's own record of what they have read, with no server
and no origin: an explicit **mark-as-read** control on the unit page, a store in
the browser, and the marks surfaced on the index and container pages.

⛔ **This task exists because R8, §7 and SF-21 were jointly inconsistent and
nobody owned the gap.** SF-21 is server-side; R8 says a served origin is never a
prerequisite for reading; §7 admits units with **no exercise** or an **ungraded**
one — which can never complete anything. So a reader who never starts the server
had no record of anything at all, and no task in the plan was going to notice.

⭐ **It binds hardest on exactly the sources this framework exists to serve.**
The Java corpus, with 168 graders paired 1:1, is the exception. An arbitrary
repository ships no graders, so every unit in it is `none` or `ungraded`, and a
server-side-only store would record **nothing whatever** for the entire corpus.

The rulings, each with the failure it prevents:

- ⛔ **An explicit act, never inferred** — not from scrolling, not from the
  narration reaching the end, not from the page having been opened. Inference
  marks a unit read when somebody skims, and a record the reader cannot trust is
  worse than none.
- ⛔ **The site says what the store is:** one browser, one machine, not in the
  repository, gone with site data. A reader who is not told this will assume
  otherwise and be wrong at the worst moment.
- ⛔ **Two versioned keys, never one record** — the marks and the reader's
  display preferences have different shapes and different lifetimes, and losing
  every mark because a preference failed to parse would be absurd.
- ⛔ **No clock.** A timestamp is a second fact nobody asked for, and it turns
  SK-06's merge into an ordering problem rather than a set union.
- ⛔ **One source file touches the store**, shared by the unit page, the
  container page (SF-27) and the index. Two implementations are a mark written
  under one name and read back under another, with no symptom but a badge that
  never lights.
- ⛔ **Joined to everything else by the address (SF-01) and nothing else.**
- ⚠️ **A stored value the control cannot display is discarded, not applied.**

⚠️ **The shared script is concatenated ahead of every file that uses it, and the
order is asserted against the real composed bundle** — never against a test
harness's own concatenation. CodeSignal placed its store *after* the page script
that read it at startup: the guard skipped, the setting silently never came
back, **the suite stayed green**, and it was found only by loading a page in a
browser. A harness that arranges the world conveniently proves nothing.

**Acceptance.** A unit is marked read over `file://` and the mark survives a
reload. The index and container pages show it. **The composed bundle defines the
store before its first use — asserted against the real composition, and the
assertion fails when the order is deliberately reversed.** Nothing writes a
clock. Clearing site data clears the marks and the page says that is what
happened. A server run never treats a read mark as a pass.

---

### SF-22 — Run and Submit
**Milestone** **M5** · **Depends on** SF-19a, SF-19b, SF-20, SF-21, SF-12 · **Team** team
**Owns** `serve/routes/run.py` and the page's execution client
**Context** ~70k — SF-19a/19b, SF-20, SF-21 outputs, `CS` design note 06 §2

**Definition.** The loop that closes the system. The page names a practice
**and a mode**; the server reads that practice's workspace from the generated
unit document and hands the one command that mode names — that exact string,
never anything a client sent — to the runner, streaming output back line by
line; the outcome is recorded.

⛔ **The page names a practice by `progress.practice_key`** (`SF-21/4`) — a pass recorded under any other spelling is one the page never reads.

⚠️ **PO round 71, from `W230`: register `run` in `serve.instance.instance_of`.** ⛔ **The verb calls `discover` and `instance_of` and never `make_instance`, so a route registered only in `make_instance` is not served** ([`handoffs/W230.md`](handoffs/W230.md)).

⚠️ **`SK-03/3`: no framework constant names the execution namespace, so `skills/buildserve/states.py` holds `EXECUTION_NAMESPACE = "run"` until this row registers `run`.** ⛔ **The constant moves into the framework with that registration, and the skill imports it from there.**

**Two modes because Run and Submit are different acts.** Run shows the reader
what their own program printed. Submit runs the grader, and only Submit can
complete a practice. Collapsing them would let a program that compiles and
prints mark a practice done.

Also writes the embedded editor's task file so the IDE's build task follows
whichever practice the reader has open — which is why the page and the terminal
never disagree about what "build" means.

⛔ **PO round 74 — SPLIT: the paragraph above and the Acceptance's *"The editor's task follows the open practice"* move to `SF-24` at `M7`, with the editor** (user direction). ⭐ **Run and Submit stay here at `M5`: they need the runner, not the editor.**

**Acceptance.** Run streams program output. Submit streams grader output and,
on success, completes the practice. Run never completes a practice. A stopped
run is recorded as stopped. Output is gated on the wire. The editor's task
follows the open practice.

---

### SF-29 — Run output filter
**Milestone** **M5** · **Depends on** SF-20 · **Team** solo
**Owns** `execute/quiet.py`
**Context** ~30k — `CS/.pipeline/tools/study/quiet.py`, `CS/.pipeline/tests/test_quiet.py`

**Definition.** The filter between the runner and the page that drops build
noise so a reader sees their program's output and their grader's verdict rather
than a build tool's progress log.

CodeSignal has a whole 203-line module for this against Gradle. **Maven is
considerably noisier** — a default `mvn test` emits plugin banners, dependency
resolution, module separators and reactor summaries around a handful of lines
the reader actually wants. Shipping unfiltered output would make Run and Submit
technically working and practically unusable, which is the kind of failure that
does not show up in any test.

Ported and generalised: the filter is per-toolchain, declared rather than
hardcoded, so a Gradle corpus and a Maven corpus each get theirs.

⚠️ **Filtering never removes a failure.** A dropped line must never be one that
would have told the reader why their code failed. When in doubt the line
survives — noise is an annoyance, a swallowed stack trace is a lie.

**Acceptance.** A Maven test run's output is reduced to program output plus
verdict. A compile error survives filtering intact. A stack trace survives
intact. The filter is selectable per toolchain, and an unknown toolchain passes
output through unfiltered rather than guessing.

---

### SF-44 — The terminal command
**Milestone** **M5** · **Depends on** SF-20, SF-23, TC-00 · **Team** pair
**Owns** one `studyforge` verb under `cli/`, named by its taker
**Context** ~30k — spec §7 and §8.3, `SF-20` and `SF-23` outputs

⭐ **Minted PO round 74 from the user's direction, 2026-09-12:** *"Client still can run things in their terminal update the file and run them by a command which then will be run against that unit test associated with the file if there is any."* ⛔ **No row covered it: `SF-20` starts processes and has no verb, and `SF-22` is a served route.**

**Definition.** The reader edits a unit's file in their own editor and runs one command naming it. The command resolves the file to its unit's exercise in the generated unit document (§7: `main_path`, `test_path`, `run_command`, `test_command`) and hands the command that document names to `SF-20`, streaming its output.

- ⭐ **A file with an associated test runs that test**, and the exit code says whether it passed.
- ⛔ **A file with no associated test is not a failure** (§7's three states, C5): the command says so and exits `0`. ⚠️ **Whether it then runs the program is the taker's to state before code.**
- ⛔ **Nothing the reader types becomes a command** (§8.3, rule 3): the argument selects a file, and the command comes from disk.
- ⛔ **The Docker socket is never mounted into a serving process (§8.3), and nothing leaves the machine.** ⭐ **Its mode is `SF-20`'s: the runner container when it is up, the host otherwise, with identical observable behaviour (§8.3, rule 4) — ruled by the register, reversible until this row is taken.** ⚠️ **Whether a passing run records a practice pass is the taker's to state before code** ([the record](BOARD-ARCHIVE.md#po-round-74-m4-closed-at-4d3c742-and-the-order-after-it-is-m6-m8-m5-m7-then-m9-user-direction)).

**Acceptance.** Over a corpus with a graded, an ungraded and a reading-only unit: a file with a test runs it, and a failing test exits non-zero; a file with no test exits `0` and says there is none; an argument that is no unit's file is refused by name; every output line is gated (R7); no command is ever read from the argument — asserted.
