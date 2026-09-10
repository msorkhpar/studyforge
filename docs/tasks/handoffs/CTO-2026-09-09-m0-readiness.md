# CTO-2026-09-09-m0-readiness — handoff

**Kind:** ruling record

**Status:** done — the audit. ⛔ **M0 itself is `blocked`:** `FND-05` cannot be
completed as written, and `FND-01`'s lint acceptance cannot be run on the
machines available. Both are planning defects, not agent failures.

**Scope.** A readiness audit of M0 against the spec, plus four rulings the plan
asked for. Everything numeric below was **counted on 2026-09-09** against the
real repositories, per `CLAUDE.md`'s *verify claims by counting*. Where a
document's number held, it is recorded as held; where it did not, it is
corrected with the count.

---

## What landed

- `docs/conventions/review-rubric.md` — the merge gate. One runnable command per
  ruling (R7, R10, R11, R12, R13, R17, dependencies, R1, handoff, acceptance,
  scope), plus the APPROVE / CHANGES REQUESTED / REJECT verdicts and what each
  means. Every command in it was executed against this repository or a
  purpose-built failing fixture before it was written down.
- This audit.

⚠️ **The rubric names two things `FND-01` must supply**, and they are contracts,
not suggestions:

1. A **stable size-check command** with a non-zero exit. The rubric defers to it
   as the authority rather than re-deriving a line count; the fallback shell loop
   exists only for when the checker is unreachable.
2. ⭐ **The opt-out marker is ruled, and it is exactly `Size exception:`** at the
   start of a line inside the module's **first** docstring — the one
   `ast.get_docstring` returns. One sentence, saying why splitting would be
   worse. `FND-01`'s checker must recognise that and nothing else, or the rubric
   and the build disagree about what a valid opt-out is.

---

## Ruling 1 — the ISO-8583 `levels` contradiction

⭐ **§1 is right. §4's table row is wrong. ISO's `levels` is `["group"]` —
depth 1.**

The corrected row for §4:

| Source | `levels` | example address |
|---|---|---|
| ISO-8583 | `["group"]` | `iso-fundamentals` + unit 02 |

**Why, in order of weight.**

1. **The repository has no second container level to express.** Counted:
   `ISO/src/` holds 41 Markdown files — 38 unit files (`1.md`…`16.md`,
   `s1.md`…`s11.md`, `c1.md`…`c11.md`) plus three aggregates. That is §1's
   "38 (16 + 11 + 11)", exactly. The only grouping signal is the filename
   prefix, which is precisely what C1 describes. There is no directory, no
   front-matter and no index expressing a subsection.
2. **The `1.1`-style numbering inside a file is within-unit sectioning, not a
   container level.** `src/1.md` opens `## 1. Introduction to ISO-8583`, then
   `### 1.1.`, then `#### 1.1.1.`. Reading `1.1` as a "subsection" container
   would make each *file* a container and each *heading* a unit — 38 containers
   and several hundred units — and it breaks §4's own definition that "a unit is
   an ordinal inside the deepest container". The archive already has a home for
   that structure: blocks and section keys (§3.2, `unit/`).
3. **§4's table is not systematically depth-2.** It already carries a depth-1
   row — SPARQL, `["course"]`. So the ISO row is an isolated stale entry, not a
   different reading of the model.
4. **`["section","subsection"]` is recognisably the pre-count assumption.** §1
   says the two tutorials "were cloned and inspected on 2026-09-08, and both
   differed materially from what was first written here". The discarded row
   names a subsection (`data-elements`) that does not exist in the repository;
   the surviving row names three groups that do.
5. **The backlog already agrees with §1.** `v2-backlog.md`'s `V2-06` reads
   "**One** container level, three groups (fundamentals 16, server 11,
   client 11 = 38 units)". §4's table is outvoted by §1, C1 and V2-06.

**Downstream, which is what this was blocking.**

- ⭐ **ISO is a `depth1/` corpus.** It tests the same fixture path SPARQL does,
  not the `depth2/` path.
- ⭐ **Two of the four designed shapes are depth-1, not one.** `FND-04` calls
  `depth1/` "the SPARQL shape"; it is the SPARQL **and** ISO shape, and on the
  four-source sample depth-1 is the *majority*. ⚠️ Do not read §11.1's "one
  depth-1, one depth-2" as "one exotic, one normal" — the depth-1 path is the
  common case and M1 is right to run against it first.
- The label is `group`, per §1's own parenthetical. `levels` supplies the
  breadcrumb's display labels (§4), so the adapter is free to render it as
  "Group" or "Track"; what is fixed is that there is **one** of them.

⚠️ **Assumption stated:** no ruling covers what to do when two sections of the
spec disagree. I have ruled by evidence — the repository as counted, plus the
two places that corroborate §1 — rather than by which section is later in the
document. If the project wants a general rule, the one I would write is *the
measured table wins over the illustrative one*.

---

## Ruling 2 — `FND-05` is blocked, and the brief's premise needs correcting

⭐ **Confirmed blocked. But the blocker is narrower and sharper than "no
repository has a remote", and the difference changes what can be salvaged.**

**Measured 2026-09-09** (⛔ the URLs are not reproduced here — they carry an
account identity, R7):

| Component | Remote | Exists |
|---|---|---|
| `SF/` (`studyforge`) | ⛔ **none** | yes |
| `JS/` (`Claude-senior-java-engineer`) | ✅ one `origin`, HTTPS | yes |
| `CS/`, `CSD/` (`CodeSignal`) | ✅ one `origin`, HTTPS | yes |
| `ISO/`, `SPARQL/` | ✅ one `origin` each, HTTPS | yes |
| `TC/` (`code-server-toolchain`) | — | ⛔ **does not exist** — E12 creates it |
| `NS/` (`narrate-service`) | — | ⛔ **does not exist** — E13 creates it |

So there are **two** blockers, and only the first is about remotes:

1. **`studyforge` itself has no remote.** ⚠️ R18 says every component "has its
   own remote". That ruling is **currently false of the framework**, which is
   the one component the parent exists to pin.
2. **Two of the five components have not been created yet**, and cannot be
   before E12 and E13 — which are M5 and later. ⛔ **No amount of remote
   provisioning fixes this**, so `FND-05` as scoped is not an M0 task under any
   circumstance.

**Does a submodule need a fetchable URL? Yes, in the sense that matters here.**
Git will accept a local filesystem path as a submodule URL, so the mechanics
would work on this machine. Both available forms fail anyway:

- An **absolute** local path in `.gitmodules` writes a home directory into a
  tracked file. ⛔ Direct R7 violation, and `.gitmodules` is committed.
- A **relative** URL (`../studyforge`) is legal and R7-clean, but git resolves it
  against **the parent's own remote URL**. The parent has none, so it resolves to
  nothing on any other machine.

And `FND-05`'s acceptance is explicit that this is the point: *"A recursive clone
**on a clean machine**"*, *"reproducible by another checkout"*. Neither is
testable without fetchable remotes. A locally-pinned submodule set would pass a
test the acceptance did not ask for.

**What unblocks it, precisely.**

1. ⭐ **A remote for `studyforge`** — an empty repository created by the owner
   under the same account as the siblings, then `git remote add origin <url>`.
   ⚠️ This is an account action and is **not an agent's to take**. The URL lives
   in `.git/config`, which is untracked; ⛔ no agent writes it into a document.
2. **Remotes for `code-server-toolchain` and `narrate-service`** — gated on E12
   and E13 creating the repositories at all.

**What can proceed with no remote at all — and it is most of the task's value:**

- The **parent repository itself**, created locally with its docs, compose files
  and scripts. A git repository does not need a remote to exist.
- ⭐ **The entire workflow document** — clone, update, advance, and the
  two-commit rule. That is `FND-05`'s fourth acceptance clause verbatim and it
  needs no network. It is also the deliverable that prevents the two documented
  silent first-run failures, which is the task's stated reason for existing.
- The **non-recursive-clone guard** — a `git submodule status`-based check that
  fails with a message pointing at the documented command. Testable today by
  cloning from a local path without `--recurse-submodules`.
- **One real submodule:** `corpora/java-senior` (`JS/`) has a remote and is in
  v1 scope. It can be added, pinned and verified now.

⭐ **Ruling: split the task.**

- **`FND-05a` — the parent, the workflow document, the guard, and the `JS/`
  submodule.** Stays in M0. Deliverable today. Its acceptance drops
  "every component" to "every component that exists".
- **`FND-05b` — composing `studyforge`, `TC/` and `NS/`.** Blocked on a remote
  for `studyforge` and on E12/E13. ⛔ **Not an M0 task.** Its natural home is
  alongside the milestone that creates the last component it pins.

⚠️ **Leaving `FND-05` in M0 whole makes M0 permanently unachievable, and M0
gates every other task in the plan.** That is the reason to split it now rather
than let it sit as a red item nobody can clear.

---

## Ruling 3 — `FND-02`'s scope

⭐ **`FND-02`'s scope as written is correct. `docs/conventions/graphify.md` is
the planning defect, and there is a second, worse one underneath it — `FND-02`
cannot meet its own acceptance in `JS/` without violating R3.**

**Measured 2026-09-09:** `CSD/graphify-out/` is present. `SF/`, `JS/`, `ISO/`
and `SPARQL/` have **none**. `graphify` is on PATH.

**On the scope itself.** `FND-02` **Owns** "`graphify-out/` in all three
repositories" and its Definition builds two of them, CodeSignal already having
one. That is internally consistent and its acceptance — "Both graphs build" —
matches. It is correct **for v1**, because §10 puts the ISO and SPARQL adapters
out of scope: those two repositories are *design inputs* to this spec, counted
once in §1 and cited as C1–C5. No v1 task queries them. Building and maintaining
two graphs nobody reads, to satisfy a literal reading of R14, is cost with no
consumer.

**But R14 says "every repository in this project carries a built graph", and
`graphify.md`'s table lists exactly three.** The two are not reconciled anywhere,
and the gap will be discovered by the first agent that assumes an ISO graph
exists. The fix is one sentence in `graphify.md`: ⭐ **R14 binds on a repository
when it enters the project's working set — when a corpus is onboarded — not
before.** That preserves the rule and prices it honestly.

**⛔ The serious defect: `FND-02` cannot satisfy its own acceptance in `JS/`.**

`FND-02`'s acceptance ends "`graphify-out/` is git-ignored". `JS/` is a
**consumer repository**, so R3 applies to it. There are two ways to ignore a
directory there, and R3 forbids the obvious one outright:

- Add a line to `JS/`'s root `.gitignore`. ⛔ **Never permitted, however
  declared** — R3 names the repository's root ignore file as one of the three
  edits no `permitted_edits` entry can authorise.
- ⭐ **Write the ignore file *inside* the generated directory**, which is what
  that same clause tells you to do instead.

**The fix, and it is mechanical:** the graph lands in a directory that carries
its own ignore file — `graphify-out/.gitignore` containing a single `*`. A
`.gitignore` whose pattern is `*` ignores every path in that directory including
itself, so `git status` in `JS/` stays clean, nothing is tracked, and **zero
pre-existing files are touched**. `FND-02` should state this rather than leave
the next agent to reach for the root ignore file, which is the natural move and
is a REJECT under the rubric.

⚠️ **Note this does *not* apply to `SF/`.** This repository's own `.gitignore`
already carries `graphify-out/` and is free to.

**Third finding, for the plan rather than for `FND-02`.** §12's second source is
deliberately unnamed and does not exist yet. When it arrives, R14 requires a
graph for it and **nothing in the plan builds one** — `SK-07` (corpus
onboarding) is the only candidate owner and its list of generated artifacts does
not include the graph or its ignore file. ⭐ Under R19 that is a hole in the
skill: *anything a second source would have to retype is a hole in the skills*,
and "build the graph, and ignore it correctly without touching the root ignore
file" is exactly such a step. Recommend adding it to `SK-07`'s definition
before M2, while the skill is being written rather than after.

---

## Ruling 4 — where the module-size checker belongs

⭐ **`tools/size_check.py` at the repository root — outside `src/`, outside the
mirrored `tests/` tree — with its own mirrored test at
`tools/tests/test_size_check.py`, plus a thin pytest wrapper at
`tests/test_quality_floor.py` that shells out to it.**

`FND-01` can proceed on this.

**Why not `src/studyforge/`.** It becomes shipped API the moment it lands there.
R17 then obliges it to publish a contract, R9's versioning reasoning starts to
apply to it, and `module-structure.md` is explicit that a package's
`__init__.py` is "what consumers import, and nothing else". ⛔ A consumer of a
study-site framework importing its line-counter is absurd, and once it is
importable somebody will.

**Why the R12 objection does not survive contact.** R12's words are "the test
tree mirrors the **source** tree" and its stated purpose is that "a failing test
names a module, not a subsystem". The requirement is **locality**, not a single
global `tests/` directory. `tools/` mirrors itself: `tools/size_check.py` →
`tools/tests/test_size_check.py`. A failure names a module. R12 is satisfied in
substance, and the rubric's §4a check is written to expect exactly this shape.

**Why both a script and a pytest wrapper, rather than one or the other.**

- `FND-01` requires a check that **"fails the build"**, and `FND-03` lists
  "tests, lint and size checks" as three separately invocable things. A check
  that only exists as a pytest case cannot be run standalone by a pre-commit
  hook or a CI step that has not installed pytest.
- ⭐ But a check nobody remembers to run is a ceiling that erodes, which is the
  exact failure `FND-01`'s own rationale describes. The wrapper makes the suite
  fail too, from **one** implementation. Two implementations would be two
  definitions of 400 lines, disagreeing eventually.

**Four conditions on it.**

1. **Standard library only.** It runs inside `FND-03`'s image, where no
   third-party package is guaranteed, and it is the thing that decides whether a
   build passes.
2. ⛔ **`tools/` is excluded from the packaging config.** Otherwise it ships
   anyway and the whole point is lost. `FND-01`'s acceptance should assert this.
3. **It checks itself.** `tools/` is inside the tree it walks — a size checker
   over the ceiling is the one bug nobody would forgive.
4. **The opt-out marker is `Size exception:`** in the module's first docstring,
   as ruled above and as the rubric encodes.

⚠️ **Naming collision, and it will bite whoever ports from CodeSignal.** `CS/`
uses `.pipeline/tools/study/` as its **source** directory — `tools/` there means
the pipeline, not the build floor. Here `tools/` means build tooling and nothing
else. ⛔ Nothing from `CS/tools/study/` is ever ported into `SF/tools/`; that
material's destination is `src/studyforge/`.

⚠️ **Assumption stated:** §3.2's tree does not name a home for build tooling at
all — it lists `src/`, `tests/`, `docker/` and `graphify-out/`. That is a gap in
the spec, not a licence to file the checker under `src/`. I am ruling under the
assumption that §3.2 enumerates the **shipped and generated** surfaces and is
silent on the build floor, and recommend adding `tools/` to it.

---

## Findings

Defects seen outside the scope of the rubric. Not fixed. Named precisely.

### ⛔ F1 — `FND-01`'s lint acceptance cannot be run

Measured on this machine: `python3` 3.14.4, `pytest` 9.0.2, `pip3`, `docker`,
`git` 2.53.0, `graphify`. **No `ruff`, no `black`, no `uv`, no `poetry`.**
`FND-01`'s acceptance says "Lint and format run clean" and there is nothing
installed to run.

**Ruling:** declare the linter as a **test-only dependency** — which
`module-structure.md` permits — and let `FND-03`'s image install it at *image
build* time. That is consistent with `FND-03`'s acceptance, which requires no
network to **run** tests, and says nothing about building the image. Until
`FND-03` lands, `FND-01`'s lint clause is **Blocked** under the rubric, not
failed. ⛔ Do not quietly drop the clause: an unenforced format is the same class
of erosion as an unenforced ceiling.

### ⛔ F2 — C3 is wrong about which repository, and the correction makes it more urgent

§1's **C3** states "**18 of ISO's files contain raw HTML**; the Java corpus has
none", and `E02-content-pipeline.md:78` and `v2-backlog.md`'s `V2-06` repeat it.

**Counted 2026-09-09, on both of `ISO/`'s branches, over all 41 Markdown files,
with fenced and indented code stripped:**

| | raw HTML | blockquote | thematic break |
|---|---|---|---|
| `ISO/` | **0 of 38** | **0** | **0** |
| `SPARQL/` | **6 of 19** — `<details>`/`<summary>` | 0 | 0 |
| `JS/` lesson READMEs | **0 of 166** | **1 of 166** | **10 of 166** |

26 of ISO's files do contain `<tag>`-shaped text, and **all of it is XML inside
fenced code blocks** — Maven POM fragments, Spring bean definitions, jPOS channel
configuration. The "18" is a count of angle brackets, not of raw HTML.

⭐ **C3's conclusion survives entirely. Its attribution does not, and correcting
it moves the requirement earlier.** As written, raw HTML is a v2 problem
belonging to a repository whose adapter is out of scope. As counted:

- **Raw HTML is a SPARQL requirement**, and it is load-bearing rather than
  cosmetic — `<details>`/`<summary>` is how those lessons hide an exercise
  answer. Dropping the vocabulary either loses the answer or leaks it.
- ⛔ **Thematic break and blockquote are `JS/` requirements — consumer 1, at
  M6.** They are not a second-source concern at all. `SF-07` lands at M1 and its
  vocabulary must already cover them, or M6 discovers it.

**Two consequences worth acting on.**

1. ⭐ **The real ISO constraint is sharper than the one recorded, and it is still
   live.** ISO's Markdown puts XML in fenced code blocks. A parser that scans for
   `<` without being fence-aware reads a `pom.xml` sample as raw HTML and either
   raises — stopping the ingest dead, which is the failure C3 predicted by the
   wrong route — or renders it as markup. That is a **fence-handling** test, and
   it should be a named fixture in `FND-04`.
2. ⚠️ **A `<details>` block interacts with narration, and nobody has ruled on
   it.** If the speakable contract (`SF-08`) walks the block, ⛔ **the audio reads
   the hidden answer aloud** — the reader hears the solution to an exercise they
   have not attempted, with the page still showing it collapsed. There is no
   ruling covering this. It needs one before E04.

### ⚠️ F3 — every other measured number in the spec held

Re-counted 2026-09-09 and **correct as stated**: ISO 38 units (16 + 11 + 11);
ISO's aggregates at 3,858 / 2,813 / 2,509 lines; SPARQL 19 lessons, with `.ttl`
datasets and two notebooks (C4 confirmed); `JS/` 166 lesson READMEs, 168
`*Test.java`, 45 numbered modules plus `00-base`; `39-data-structures`'s
implementation class at 787 lines against a 937-line test; `CS/` `backend.py`
2,743 and `scaffold.py` 1,793; and 157/1,290 is 12.2%.

⭐ Recorded because it matters: **the spec's measurement discipline is sound and
C3 is the exception, not the pattern.** Do not treat this audit as a reason to
re-derive numbers that have been checked.

### ⚠️ F4 — no M0 work has been committed

`SF/` has no `src/`, no `tests/`, no `tools/`, no `pyproject.toml`. Branches
`main`, `release/m0-foundations`, `feat/FND-01-scaffolding`,
`feat/FND-04-fixtures` and two `chore/` branches all sit at the same commit.
M0 is at zero, which is consistent with the plan and is recorded only so the
audit's baseline is unambiguous.

### ⚠️ F5 — ruling-range drift in two documents

`docs/tasks/README.md:288` says "all of R1–R19" and `CLAUDE.md:33` says "The full
set is R1–R19 in the spec", while the spec has **R20**, `agent-protocol.md` says
R1–R20, and `CLAUDE.md`'s own body cites R20 twice. An agent following the
reading list literally skips the ruling that governs the whole extraction
direction. One-line fix in two files, for whoever owns the docs.

### ⚠️ F6 — `graphify-out/` and the rubric

`SF/`'s `.gitignore` already ignores `graphify-out/`, and `graphify.md` says the
graph is "rebuilt, not merged". The rubric therefore fails any diff containing
it. Flagged so nobody is surprised: it is deliberate.

---

## Decisions

- **Ruled by evidence, not by document order**, where §1 and §4 conflict. Stated
  as an assumption in Ruling 1, with a proposed general rule.
- **Split `FND-05` rather than declaring it blocked and leaving it.** A blocked
  task in the milestone that gates everything else is worse than a smaller task
  that lands.
- **Put the size checker outside `src/` and answered R12 by mirroring `tools/`
  onto itself**, rather than by exempting it. An exemption in the very tool that
  enforces the floor sets the wrong precedent on day one.
- **Made the rubric defer to `FND-01`'s checker** rather than carry a second
  implementation of the ceiling, and fixed the opt-out marker so the two cannot
  drift apart.

---

## Surprises

- ⭐ **The brief I was given said the sibling repositories have no remotes. Four
  of the five do.** The blocker is `studyforge` itself, plus two components that
  do not exist. That changes `FND-05` from "wait for infrastructure" to "split,
  and land most of it today", which is a materially better outcome — and it is
  the reason the audit checked rather than inherited.
- **C3's "18 files" is the only measured claim in the spec that did not survive
  a recount**, and the recount made the underlying requirement *earlier* and
  *larger* rather than smaller. An inherited number being wrong in the safe
  direction was not the outcome I expected.
- **`FND-02`'s R3 collision** is invisible from the task text. It only appears
  when you ask *how* `graphify-out/` gets ignored in a repository this project
  is forbidden to modify.

---

## For dependents

**`FND-01`** — three things are now fixed and you should build to them: the
checker lives at `tools/size_check.py`, the opt-out marker is a line beginning
`Size exception:` in the module's first docstring, and `tools/` is excluded from
the packaging config. Your lint acceptance is **Blocked** until `FND-03` lands;
declare the linter as a test-only dependency and say so in your handoff.

**`FND-02`** — your scope is correct. ⛔ Do not touch `JS/`'s root `.gitignore`;
put a `.gitignore` containing `*` inside the generated `graphify-out/` directory
instead. Add the sentence to `graphify.md` that R14 binds when a repository
enters the working set.

**`FND-04`** — ISO is a **depth-1** shape, so `depth1/` covers two of the four
designed sources and is the common case, not the exotic one. Add a fixture whose
unit contains a **fenced code block full of XML**, and one containing raw HTML,
a blockquote and a thematic break — all three are consumer-1 or SPARQL
requirements, measured, not hypothetical.

**`FND-05`** — split as ruled. Land `FND-05a` now; `FND-05b` waits on a remote
for `studyforge` and on E12/E13.

**`SF-07` / E02** — your vocabulary needs raw HTML, thematic breaks and
blockquotes, and the evidence is `SPARQL/` and `JS/`, not `ISO/`. Your harder
requirement is **fence-awareness**: ISO is 26 files of XML inside code fences and
a naive `<` scan misreads all of it.

**`SF-08` / E04** — ⚠️ unruled question, and it needs an answer before you
build: does the speakable contract read the contents of a `<details>` block? If
it does, the narration speaks an exercise answer the page is deliberately hiding.

**Everyone** — `docs/conventions/review-rubric.md` is the merge gate. Read §9
before you finish: your task's **Acceptance** bullets get pasted into the review
with the command and its output beneath each one, and ⛔ restating a condition is
not meeting it.
