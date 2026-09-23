# E15 — Release-ready

Every repository this framework owns is cleaned for release. The process that built the
framework moves to an archive branch in the same repository, the main line keeps the
product, the board becomes light, and the next corpus needs only the README and the skills.

**Shared context for this epic — read this before any task.**

⛔ **The authority is the user: the release-ready direction of 2026-09-18 and the six
rulings of 2026-09-19.** ⭐ **They are SETTLED, and a row here that re-asks one of them is
re-deriving a settled thing.** The argument that minted this epic is [`W438`](rows/W438.md).

⛔ **This document carries no measured figure, deliberately.** How many files, lines,
branches, worktrees and `tools.*` importers there are is a reading, and a reading in an epic
is stale the round after it is written. ⭐ **The inventory was measured at `a469adc2` and
lives in [`W438`'s handoff](handoffs/W438.md), with the command that took each figure.**
⛔ **Every task below re-takes its own population at its own ref**, with the same command,
before it acts.

## ⛔ The six rulings, and what each one binds here

| the ruling (user, 2026-09-19) | what it binds here |
|---|---|
| ⭐ Process history goes to a separate BRANCH in the same repository, never a new repository and never deletion | `REL-10` cuts it; every removal on the main line is reachable from it |
| ⭐ Handoffs all go to that branch, and a distilled decisions file replaces them on the main line | `REL-01` writes the file BEFORE `REL-10` moves a single handoff |
| ⭐ Epics `E00`–`E14` are kept as HIGH-LEVEL design only; the task text goes to the archive | `REL-11` |
| ⭐ The review rubric is archived; its product-contract clauses move into the spec | `REL-08` sorts the clauses, `REL-10` moves what is left |
| ⭐ The Python floor stays `>=3.14` until publishing is ruled | every task: ⛔ `requires-python` is not touched |
| ⭐ Merged local branches may be deleted; history stays reachable through merge commits | `REL-12` |

⭐ **And the direction of 2026-09-18:** the board is LIGHT — a project manager's board, not a
channel between agents; code that exists only to build the framework moves to the archive
branch; ⛔ **the next corpus (`M9`) reads the README and the skills and nothing else**, with
the library installable and every image built and used LOCALLY by tag.

## ⛔ Three properties, and every row here is judged against them

1. ⛔ **Nothing is lost.** A path that leaves the main line is on the archive branch, byte
   for byte, and the removal commit is reachable from the main line. A ruling that still
   shapes the product is in the decisions file or the spec before its handoff leaves.
2. ⛔ **The product never depends on the process.** No product test imports the tooling,
   no product test reads a board, a row, a handoff or an epic, and no skill points at a
   path outside the installed package. ⭐ **This is proved by taking the process AWAY in
   a scratch export and running the product suite**, never by reading imports.
3. ⛔ **The close is a CLEAN checkout, installed.** A reading taken in a working checkout
   with the tooling beside it proves nothing about what a stranger receives.

## ⛔ The order, and why it is this one

⭐ **Distil, decouple, package, sort, move, read.** The decisions file is written first
because it is the one step whose inputs leave the main line in `REL-10`: a ruling that is
not carried before its handoff moves can only be recovered by reading the archive, which
is the cost this milestone exists to remove. The product suite is decoupled from the
tooling next, because moving the tooling first turns the suite red for a reason nobody can
fix on the main line. The package is made self-sufficient before the move, because a skill
that still points at a sibling checkout or at `docs/tasks/` breaks the moment its target
leaves. ⛔ **The close run is last, from a clean clone of the main line**, installed into
an empty environment, with the skills read from the INSTALLED package.

⚠️ **In-step edges are read off each task's `Depends on`, never inferred from step
membership.**

## ⚠️ What is NOT in this epic, and where it is instead

- ⛔ **Registry publishing is not in scope.** It waits on a future user ruling, and so does
  any change to the Python floor.
- ⛔ **The corpus repository's own cleanup is the integration agent's**, in that repository,
  as rows — never a task here. [`README.md`](README.md)'s `M11` section names them.
- ⛔ **CodeSignal is untouched** (R20), and the Java and SPARQL corpora are `M9`'s and v2's.
- ⛔ **No archived text is rewritten.** A record moves whole; its freeze holds on the
  archive branch exactly as it held here.

---

### REL-01 — The decisions file
**Milestone** **M11** · **Depends on** — · **Team** pair
**Owns** `docs/decisions.md`
**Context** ~60k — the spec's R1–R21, `docs/tasks/rulings-index.md`, the handoffs a product
docstring cites

**Definition.** The one document on the main line that carries every decision still
shaping the product, so no reader of the product ever needs the archive. An entry states
the decision, the reason in a sentence, and the spec rule it serves. ⭐ **It carries the
process ids it replaces as aliases**, so a reader who meets an old id in a docstring can
find the decision until `REL-09` rewrites that docstring.

⛔ **It distils; it does not copy.** A decision the spec already states is a pointer to the
spec, never a second copy of it. ⛔ **It cites no handoff, no row and no board anchor**,
because those leave the main line in `REL-10`.

⭐ **The file's header carries the command that derives its population**: every process id
cited in `src/`, `tests/`, `docs/specs/` and `docs/authoring/`. An id is either an alias in
the file or named in this task's handoff as one that explains nothing without the archive
— which is exactly the population `REL-09` rewrites.

**Acceptance.** The header's command, run at the task's ref, prints no id that is neither an
alias in the file nor on the handoff's list. `grep -nE 'handoffs/|rows/|BOARD' docs/decisions.md`
prints nothing. Each entry names a spec rule or says why it serves none. A plant — an id
added to a docstring in a scratch copy — makes the command print it.

---

### REL-02 — The product suite stands without the tooling
**Milestone** **M11** · **Depends on** — · **Team** pair
**Owns** the root `conftest.py`, `pyproject.toml`'s `[tool.pytest.ini_options]`, and every
module under `tests/` that imports `tools` or opens a process document
**Context** ~50k — the root `conftest.py`, `tools/treestate.py`, `tools/treereaders.py`,
`tools/workspace/`, the importers `W438`'s handoff lists

**Definition.** The product's test suite runs with nothing from the tooling present. The
tree-state exit condition the root `conftest.py` wires from `tools/` either becomes the
product suite's own, standard library only, or goes with the tooling; the task decides which
and records why. The test roots stop naming `tools/tests`. A product test that imports
`tools.workspace`, `tools.quality` or `tools.mergegate` reads what it needs through a helper
under `tests/`; a product test that reads an epic, the rubric, a convention, the board
archive or a handoff is rewritten against the spec, the decisions file or a fixture — or,
if what it guards is process, it is marked to go with the tooling in `REL-10`.

⚠️ **One package is NOT this task's: `tests/studyforge/skills/delivery/`.** Its tests read the
epics because the delivery skill does, and they change with the skill in `REL-06`.

⛔ **Nothing is weakened to get there.** A test that moves keeps its assertion; one that is
rewritten keeps its plant.

**Acceptance.** `git grep -nE '^\s*(from|import) tools' -- tests conftest.py` prints nothing.
In a scratch export of the task's tip with `tools/`, `docs/tasks/` and `docs/conventions/`
removed, `python3 -m pytest tests -q --ignore=tests/studyforge/skills/delivery` is GREEN. The full suite on the unmodified tree is
GREEN. A stray file planted during a run still fails the session. Every test marked to go
with the tooling is listed in the handoff with the reason.

---

### REL-03 — The product floor is the product's
**Milestone** **M11** · **Depends on** — · **Team** pair
**Owns** the checks under `tools/quality/` that police the product — R7, R11, R12 and R17
— and their new home
**Context** ~40k — `tools/quality/`, spec R7, R11, R12 and R17,
`docs/conventions/module-structure.md`

**Definition.** The rules that keep the product honest — no personal data (R7), the size
bound (R11), the mirrored tests (R12), the module contracts (R17) — keep running on the main
line after the tooling leaves. Each check is sorted: one that polices the product moves into
the product's suite or a `dev` extra that `pyproject.toml` declares; one that polices the
process — the board, the register, rows, handoffs, rulings, rounds — stays with the tooling
and leaves in `REL-10`. ⛔ **Standard library only**, as the floor always was.

⛔ **A check is moved, never re-written weaker.** Its plants move with it.

**Acceptance.** In the same scratch export as `REL-02`'s, a planted file over the size bound,
a planted personal-data shape, an unmirrored module and a public function with no contract
are each refused by the product's own command. The sorting is a table in the handoff naming
every check under `tools/quality/` and its side. `python3 -m tools.quality` is still GREEN on
the unmodified tree.

---

### REL-04 — The skills ship in the package
**Milestone** **M11** · **Depends on** — · **Team** solo
**Owns** `pyproject.toml`'s `[tool.setuptools.package-data]`, and how a skill document is
located from an installed package
**Context** ~25k — `pyproject.toml`, `src/studyforge/skills/`, spec §9

**Definition.** Every `SKILL.md` is package data, and an installed `studyforge` can hand a
reader the text of each skill with no checkout present. ⭐ **The skill documents are the
product** (R16, R19); a wheel that carries the code and not the procedure ships half of it.

**Acceptance.** A wheel built from a clean export of the task's tip contains every `SKILL.md`
under `src/studyforge/skills/`. Installed from that wheel into an empty environment, in a
directory with no checkout beside it, each skill document is read through the installed
package and is byte-identical to the tree's. A skill document missing from the wheel fails a
test.

---

### REL-05 — Onboarding pins the installed library, not a sibling checkout
**Milestone** **M11** · **Depends on** REL-04 · **Team** pair
**Owns** `src/studyforge/skills/onboarding/` — the pin it writes, the stubs it writes, the
generated pin test
**Context** ~40k — the onboarding skill, its `W270` and `W321` arguments, the pin and
stubs it writes into a corpus

**Definition.** A corpus records which framework it was converted with by the installed
library's version and commit, and its skill stubs resolve through the installed package —
⛔ **never through a path to a sibling checkout.** The generated pin test checks the pin
against the installed library.

⚠️ **The workspace's pin file is a DEVELOPMENT arrangement (R18) and is not what a stranger
has.** The next corpus installs the library; it does not check the framework out beside
itself.

**Acceptance.** Onboarding a fixture corpus in a scratch directory with no `studyforge`
sibling succeeds, and every stub it writes resolves to a skill document through the
installed package. `git grep -n '\.\./studyforge' -- src/studyforge/skills` prints nothing.
A stub naming another version than the pin fails the generated test. Re-running onboarding
with nothing changed rewrites nothing (R10).

---

### REL-06 — The delivery skill reads a packaged capability index
**Milestone** **M11** · **Depends on** REL-04 · **Team** pair
**Owns** `src/studyforge/skills/delivery/` — where the index it reads comes from
**Context** ~35k — the delivery skill, `capability.py`, `epics.py`,
`docs/capability-index.md`

**Definition.** The delivery skill's first step reads the capability index from the
installed package, not from `docs/tasks/`. ⛔ **The order matters and is the reason this
task exists**: `REL-11` trims the epics to high-level design, after which the task headings
the generator parses are gone from the main line — so the index a planner reads must be
generated and shipped BEFORE the epics are trimmed. ⭐ **The generator stays product code**
(a corpus's own plan uses it); only what it is pointed at changes, and the test that compares
the shipped index with a regeneration is re-pointed at what the package ships.

**Acceptance.** The skill's first command, run in a directory with no `docs/tasks/`, prints
the index from the installed package. In `REL-02`'s scratch export,
`python3 -m pytest tests/studyforge/skills/delivery -q` is GREEN. `grep -n "docs/tasks" src/studyforge/skills/delivery/SKILL.md`
prints nothing. The packaged index is byte-identical to a regeneration at the task's ref,
and a hand-edit to it fails a test.

---

### REL-07 — The README is an author's whole reading list
**Milestone** **M11** · **Depends on** REL-04, REL-05, REL-06 · **Team** solo
**Owns** `README.md`
**Context** ~30k — `README.md`, `docs/authoring/`, the skill documents

**Definition.** The document a stranger converting their own material reads first. It says
what the framework is, how to install it, how to build its images locally by tag, and which
skill to run in which order, and it sends the reader to `docs/authoring/` and the skills —
⛔ **and to nothing that leaves the main line**: no board, no task index, no epic, no
convention, no capability index file.

⚠️ **The tracked `ONBOARDING.md` is NOT this task's.** Its content was routed to the user as
a decision in an earlier round and is still theirs; this task does not touch it.

**Acceptance.** Every link in `README.md` resolves at the task's ref, and none resolves into
`docs/tasks/`, `docs/conventions/` or `tools/`. Every fenced `studyforge` command in it is a
verb the installed command offers. Each skill is named with the step it serves.

---

### REL-08 — The rubric and the conventions, sorted into product and process
**Milestone** **M11** · **Depends on** REL-01 · **Team** pair
**Owns** `docs/specs/2026-09-08-studyforge-v1-design.md`'s new product-contract clauses, and
the sorting of `docs/conventions/`
**Context** ~80k — `docs/conventions/review-rubric.md` whole, the other conventions, the spec

**Definition.** Every clause of the review rubric is sorted: one that states what the product
must be — a contract a user of the product relies on — moves into the spec, in the section
of the rule it serves; one that states how offices work is left for the archive. ⭐ **The
same sort is taken over each convention**: a product convention (module structure, the
personal-data shapes, commanded pages, the UI identity) moves into the spec or
`docs/authoring/`, and a process convention (the board, the agent protocol, the delivery
flow, the workspace) is left for the archive.

⛔ **A clause moved into the spec is a spec amendment and is written as one**, dated and
argued, never pasted.

**Acceptance.** The handoff tables every rubric section and every convention with its side
and, for a moved clause, the spec section it landed in. `git grep -nE 'review-rubric|docs/conventions/'
-- src tests docs/specs docs/authoring README.md` prints nothing that a product reader
follows, and each residue is listed as going with the tooling in `REL-10`.

---

### REL-09 — Process ids leave the product's prose
**Milestone** **M11** · **Depends on** REL-01 · **Team** team
**Owns** docstrings and comments under `src/` and `tests/` that cite a process id
**Context** ~40k per subteam — `REL-01`'s list, the modules it names
**Effort** proportional to the population `REL-01`'s command prints, split by package

**Definition.** A docstring or comment that cites a row, a round or a numbered ruling that
explains nothing without the archive is rewritten to carry the reason itself, or to cite the
decisions file's entry or a spec rule. ⛔ **The code does not change**: this is prose, and a
diff that moves a line of logic is out of scope.

⭐ **Subtasks**, one per top-level package under `src/studyforge/` and one for `tests/`, so no
two subteams edit one file.

**Acceptance.** `REL-01`'s command, restricted to `src/` and `tests/`, prints no id that is not
an alias in the decisions file. The suite is GREEN and no non-comment line changed — checked
by comparing the syntax trees of every touched module before and after with docstrings
stripped.

---

### REL-10 — The archive branch, and the main line without the process
**Milestone** **M11** · **Depends on** REL-01, REL-02, REL-03, REL-06, REL-07, REL-08 · **Team** pair
**Owns** the branch `archive/process`, and the one removal commit on the main line
**Context** ~30k — `REL-02`, `REL-03` and `REL-08` handoffs, the six rulings

**Definition.** The process leaves the main line in one commit, and everything it removes is
on an archive branch in this repository. ⭐ **The branch is cut at the ref the removal
commit's parent names**, so it holds every path byte for byte. What leaves: `tools/`,
`docs/tasks/handoffs/`, `docs/tasks/rows/`, `docs/tasks/BOARD-ARCHIVE.md`,
`docs/tasks/rulings-index.md`, the process conventions and the rubric, and every test
`REL-02` marked. What stays: `src/`, the product tests, `docs/specs/`, `docs/authoring/`,
`docs/decisions.md`, `README.md` and the packaging.

⛔ **Never a deletion of history** (ruling 1): the archive branch is a local branch, never
pushed, and the removal commit's parent is reachable from the main line. ⭐ **From the cut on,
a handoff is committed to the archive branch**, and what it decides that still shapes the
product goes into the decisions file on the main line in the same act.

**Acceptance.** For every path the removal commit deletes, the archive branch's tree holds it
with the same blob. `git grep -nE '^\s*(from|import) tools'` on the main line prints nothing.
The product suite and the product floor are GREEN on the main line with no `tools/` present.
At the cut, the removal commit's parent is the archive branch's tip, so
`git merge-base --is-ancestor archive/process <main>` exits zero.

---

### REL-11 — A light board, and epics as high-level design
**Milestone** **M11** · **Depends on** REL-10 · **Team** pair
**Owns** `docs/tasks/BOARD.md`, `docs/tasks/README.md`, the epics `docs/tasks/E*.md`,
`docs/capability-index.md` and `CLAUDE.md`
**Context** ~40k — the board, the task index, the epics' preambles

**Definition.** The board becomes a project manager's board: the milestones, what is open,
who has it and what is next — ⛔ **no register, no round, no carrier and no instrument
vocabulary.** Each epic keeps its preamble and its shared context as high-level design, and
its task text goes to the archive branch (ruling 3). The task index keeps the milestone order
and each milestone's *Done when*. `CLAUDE.md` keeps the product's hard rules and points at the
README, the spec and the decisions file. `docs/capability-index.md` leaves the main line,
because `REL-06` ships the index the skill reads.

⭐ **`E15` is trimmed in the same form once `M11` closes** — the register's act at the close,
not a task's — so this epic's own tasks stay dispatchable until then.

**Acceptance.** `grep -lE '^### [A-Z]{2,4}-[0-9]' docs/tasks/E0*.md docs/tasks/E1[0-4]*.md`
prints nothing, and the archive branch holds every trimmed text. No link on the board, in the
task index, in an epic or in `CLAUDE.md` resolves into a path `REL-10` removed. The board names
no process instrument.

---

### REL-12 — Merged branches and idle worktrees are pruned
**Milestone** **M11** · **Depends on** REL-10, REL-11 · **Team** solo
**Owns** the local branches and linked worktrees of this repository
**Context** ~10k — `git branch`, `git worktree list`, ruling 6

**Definition.** Every local branch already merged into the main line or the archive branch is
deleted, and every linked worktree no office is using is removed (ruling 6). ⛔ **A branch that
is not merged is never deleted**: it is listed and routed to the user. ⛔ **A worktree with an
uncommitted change is never removed**, and one an office is running in is never touched.

**Acceptance.** Before each deletion, the branch's tip is an ancestor of the main line or of
the archive branch, checked with `git merge-base --is-ancestor` and recorded. Afterwards
`git branch --merged <main>` lists only the main line, and `git worktree list` lists only the
main checkout and the worktrees the handoff names as live. Each unmerged branch is in the
handoff with its tip.

---

### REL-13 — The framework's siblings are release-ready
**Milestone** **M11** · **Depends on** REL-01, REL-04, TC-00, NS-01 · **Team** pair
**Owns** the release cleanup inside `TC/` and `NS/` — their READMEs, their process-id prose,
their branches and worktrees
**Context** ~40k — each sibling at its pin, its `README.md` and `consuming.json`

**Definition.** Each shared component this framework owns meets the same bar: a clean
checkout of its main builds its images locally by tag and passes its own suite; its README is
a stranger's reading list; its prose cites no process id that explains nothing outside this
project's archive; its merged branches and idle worktrees are pruned (ruling 6); and the
workspace pin advances to the result. ⛔ **Its `consuming.json` is the contract and stays
one** — a cleanup that changes a field a consumer reads is out of scope.

**Acceptance.** A clean clone of each sibling's main, at the commit the workspace pins after
this task, builds its images by tag with no pull beyond its declared pinned bases and passes
its own suite. A grep for a process id in each sibling prints only what its handoff lists as
kept with a reason. Each sibling's merged branches are gone, each tip checked reachable first.

---

### REL-14 — `M11`'s close, read from a clean checkout
**Milestone** **M11** · **Depends on** REL-11, REL-12, REL-13 · **Team** solo
**Owns** nothing — this row produces evidence
**Context** ~40k — `README.md`, `docs/authoring/`, the skills, the first corpus at its pin

**Definition.** The reading that closes the milestone, taken from what a stranger receives. A
clean clone of the main line into an empty directory; the package installed from it into an
empty environment; the first corpus, at its pin, taken through `studyforge validate`, `build`
and `serve` with the skill documents read from the INSTALLED package; and the reading list an
`M9` author follows checked to be the README, `docs/authoring/` and the skills — nothing else.

⛔ **It owns no code**: a row that could edit what it measures measures nothing. A shortfall
becomes a finding against the row that owns it.

**Acceptance.** Each of these is recorded with the ref and the environment it was taken in: the
install exits zero; `validate` exits zero on the first corpus; `build` produces its site; `serve`
answers on loopback; every skill document the run reads comes from the installed package; and
following every link from `README.md` reaches only the README, `docs/authoring/`,
`docs/decisions.md`, the spec and the skills.
