# Skill — corpus onboarding

**Take a repository of teaching material from nothing to a corpus this
framework can build, and leave nothing for anybody to retype.** The one manual
step is: install the framework library into the Python you run this with.

⛔ **This skill does not reason about unfamiliar material and it does not write
an adapter's reading step.** Reconnaissance answers the first and a
person answers the second, in exactly one file that this skill names for them.

---

## The rule that governs every judgement below

⛔ **The consuming half of a corpus is generated, never hand-authored** (R19).

⭐ Everything this skill emits is regenerable, so a diff in one of its files is
a **defect report against this skill** rather than a local fix — it is silently
reverted the next time somebody runs it, and a tool that eats your changes is a
tool nobody runs twice.

⭐ **Customisation enters as data in the manifest.** Placement profile, level
labels, variants, permitted edits, what is material and what is not: every one
of them is a field in `corpus.json`. ⛔ **If a corpus needs something the
manifest cannot say, the manifest is missing a field, and that is the
finding.**

⚠️ **The measurement that made this skill exist.** Scaffolding an adapter into
a clean corpus and running `studyforge validate` gave `NOT valid: 8 finding(s)`
— one `unclassified` per generated file — and closing it meant a person copying
two lines out of a report into `corpus.json` (`SK-02/1`). ⛔ **Two lines is
still retyping**, and a second source pays it again. This skill writes them.

---

## Before you start

You need three things, and nothing else:

1. the repository of material, on disk;
2. this framework, **installed as a library** into the Python that runs these
   steps and the corpus's own checks — ⛔ **never a checkout this repository
   reaches by path, never a submodule** (R18, amended: nothing in this project
   is pushed to any remote, so a submodule URL has no legal form), never
   vendored, never copied. It is not published to a package index: build a
   wheel from the framework and install it;
3. reconnaissance's draft, which is a `dict` and not yet a manifest.

⛔ **The pin is the INSTALLED library**. This skill reads the version
of the `studyforge` this Python imports and writes it into the corpus's pin
beside the commit you pass as `framework_commit` — the commit that library was
built from. ⛔ **Never a path**, relative or absolute: a path carries somebody's
home directory (R7), and a sibling checkout is a development arrangement a
stranger with the installed library does not have.

⭐ **Every skill stub names its skill and the command that prints its procedure
from the installed package** — the skill-document locator,
`studyforge.skills.documents`, run as a module with the skill's name — never a
file in a checkout.

⭐ **And one command says whether the library this Python imports is the
version a corpus is pinned to** — exit 0 when it is, 1 when it is another, and a
sentence either way. The generated `test_framework_pin.py` asks the same
question, of the same library, from inside the corpus:

```
python3 -m studyforge.skills.onboarding.verify .
```

⚠️ **The version is verified; the commit is recorded.** An installed wheel
carries no git history, so nothing can be asked whether it holds a commit; the
commit is your statement of what the library was built from, checked for its
shape. ⛔ A library whose version cannot be read is refused by name, and
nothing is written.

⛔ **A corpus onboarded before this — its pin names a framework checkout beside
it (`"where": "sibling"`) — keeps working until it re-onboards**: its committed
stubs and pin test do not import this library. ⭐ Its next regenerate must
re-pin, from the installed library: `reonboard('.', framework_commit=<the
commit the library was built from>)`. Without `framework_commit` that
re-onboarding is refused by name, because the commit a sibling was at says
nothing about the library installed now — and so is one whose pin names a
version other than the one running.

---

## Procedure

### 1. Read the draft back, and settle every reason it could not invent

```
python3 -c "from studyforge.skills.reconnaissance import survey; \
  found = survey('.'); print('\n'.join(found.lines()))"
```

⚠️ **A draft's `content.exclude` is a list of bare paths, and a manifest's is a
list of reasons.** That gap is deliberate and this skill does not close it by
inventing prose: an exclusion says *material was withheld from the reader*, and
only a person knows why.

⭐ So `promote` takes a `reasons` mapping and **refuses, naming every path that
still has none, at once.** A corpus that excludes nothing needs no mapping and
onboards unattended.

⭐ **The same mapping settles a proposed `not_material` glob** (`W249`).
Reconnaissance drafts each with `"why": null`; `promote` pairs it by glob and
names every glob still open in one refusal. A reason already written is kept.

### 2. Ask what will be written, before anything is on disk

```
python3 -c "from studyforge.skills.onboarding import onboard; \
  made = onboard(draft, framework_commit=commit); print('\n'.join(made.lines()))"
```

⭐ Every path, its length, which step produced it, and **the one file that is
yours**. ⛔ Read this before `write`, for the same reason `validate` reports
every finding at once: an integrator who discovers the file set one refusal at
a time has been given a guessing game.

### 3. Write it — all of it, or none of it

```
python3 -c "from studyforge.skills.onboarding import onboard; \
  onboard(draft, framework_commit=commit).write('.')"
```

⛔ **It refuses rather than overwriting, and names every collision at once**
(R3: generation is non-destructive; no existing file is moved, renamed or
rewritten). ⭐ **`git status` afterwards shows additions and nothing else** —
plus whatever the manifest's own `permitted_edits` declares, which is the only
form an edit may take and is checked by a test this skill generates.

⛔ **That generated check answers R3, and not `git status`** (`W331`). ⚠️ **It
answered `git status` until this row, and so it went RED on a CORRECT run**: a
re-build replaces the pages an earlier build wrote, and `git add` turns a file
that never existed into an `A ` entry rather than a `??` one — both read as
*"an existing file changed"*. ⭐ **It went green the moment the work was
committed, which is the proof it was measuring committing.** ⛔ **The verdict may
not move between uncommitted, staged and committed**, so it now reads two things
and neither is the tree's dirtiness:

- ⭐ **what a build DECLARES it writes.** `studyforge plan` enumerates that from
  this corpus's own declarations, before anything runs, and `reads_as_content`
  below says which paths R3 reads as this corpus's content. A path in both that
  `permitted_edits` does not declare is the breach — **stated by the plan, so
  committing cannot answer it.**
- ⭐ **the tree, through that same declaration.** Both status letters are read
  and a rename's origin is taken from its own field; an ADDITION is never a
  breach, and what is left must be named by the plan, by
  `.studyforge/installed.json` (`W329`) or by `permitted_edits` — or sit inside
  `.studyforge/`, which `studyforge.validate.source.SKIP_DIRS` already declares
  is this tool's directory and never the corpus's material.

⚠️ **What the second reading cannot do, said rather than implied:** a committed
tree holds no record of what changed, so an undeclared rewrite nobody planned is
invisible to it. ⭐ That is why the first reading exists and why it comes first.

⛔ **`permitted_edits` may never name** the repository's root ignore file, any
version-control configuration, or a file R3 reads as content — **repository-root
documentation included, whatever `content` classifies it as** (`W278`). ⭐ The one
predicate is `studyforge.corpus.manifest.edits.reads_as_content`, the stems it reads
as root documentation are `studyforge.corpus.manifest.edits.ROOT_DOCUMENTATION`, and
all three are refused by `studyforge.corpus.manifest.edits.parse_edits`. ⛔ Read the
names there: this skill keeps no copy, and a draft declaring one is refused by name.

⛔ **A corpus already onboarded is RE-onboarded from what it records, never
re-surveyed and never hand-edited** (`W439`). ⭐ Its `corpus.json` and its pin are
the draft — every answer a person already settled — and a change enters as data:

```
python3 -c "from studyforge.skills.onboarding import hand_edited, reonboard; \
  reonboard('.', not_material=[{'glob': 'notes/**', 'why': '<why it is not material>'}]) \
  .write('.', regenerate=True); print(hand_edited('.'))"
```

- ⭐ **`not_material` is only the globs you ADD.** Each one the manifest already
  declares is kept byte for byte, in its order, with its reason (`W283`), and each
  one a generator owns is derived again — ⛔ **so none is retyped**, and one that
  is retyped is refused by name as a collision.
- ⭐ **`settle` names a recorded answer you mean to change** — `{"exercises": True}`
  when a corpus starts authoring. ⛔ Any answer it does not name that would move is
  still refused by name (`W329`, below); `content` is never settled here, because a
  new content shape is a new onboarding.
- ⭐ **`framework_commit` re-pins**, to the library running `reonboard`. Without it
  the recorded pin and its skills are kept — ⛔ only while the pin names the
  version running, and never for a pin that predates the installed library. ⛔ **The pin, every stub and `ONBOARDING.md` move together or not at all**:
  a pin advanced by hand leaves the stubs behind, which the generated
  `test_framework_pin.py` refuses (`test_no_stub_has_drifted_from_the_pin`) and
  `hand_edited` names as `.studyforge/pin.json`.
- ⛔ **`hand_edited('.')` printing `[]` is the proof**, and a `corpus.json` edited in
  an editor fails it: `.studyforge/installed.json` digests the manifest as generated.

⚠️ **Why not `survey('.')`**: on an onboarded corpus it reads this framework's own
generated half as material and proposes answers the manifest does not record
(`W329`), so every regenerate from it is a string of refusals. ⭐ Underneath,
`reonboard` is `onboard(recorded draft, existing=<its text>)` —
`existing=` stays the mechanism for a caller that builds its own draft, and
`write(..., regenerate=True)` refuses by name, writing nothing, when that draft
would still drop a declared glob.

⛔ **And a second run of this whole procedure writes the SAME `corpus.json`, byte
for byte, or refuses by name** (`W329`). ⚠️ **It did neither**: a re-survey read
this framework's own generated half as the corpus's material, so it counted the
scaffold's `tests/**/test_*.py` as graders and this skill wrote `exercises: true`
— three lines below its own report printing `graded practices  no`, with no
refusal — and `buildserve` then presents a corpus COMPLETE at the reading floor
as unfinished (§7, C5). The archive a build had written moved `placement` the
same way. ⭐ **`recorded.moved` compares every answer the manifest on disk
records with the one about to be written**, over the manifest's own fields
rather than a list somebody remembers to extend, and names every one that
would move. ⛔ **A reading that disagrees with a recorded answer is a question,
never a rewrite.**

⛔ **And a regenerate never takes a file of yours at a path a later framework
generates** (`W353`). A generated path already on disk that
`.studyforge/installed.json` does not list as generated is refused by name, and
nothing is written — ⚠️ even when its bytes are what the framework would write,
because adopting it would be silent. ⭐ Move each named file aside, regenerate,
and keep what was yours outside the generated paths.

What lands, and why each one exists:

| what | why it is generated rather than typed |
|---|---|
| `corpus.json` | the draft promoted, with **every generated file already declared `content.not_material`** |
| the adapter package and its suite | the adapter skill's scaffold, wired in — one file that is yours and every other one generated; ⛔ how many is the scaffold's own listing (`scaffold(...).lines()`, the adapter skill's step 1), never a number typed here (`W345`) |
| `.studyforge/pin.json` and the skill stubs | the installed library's version and the commit it was built from, and thin pointers that carry both and name the command that prints each procedure from the installed package |
| `tests/` — two checks | R3's assertion, read from what a build declares it writes and from the tree through that same declaration, with this corpus's edits baked in; and the pin check — the installed library is the pinned version, ships every stubbed skill, and no stub has drifted |
| `ONBOARDING.md` | what a reader gets, read off the corpus's own declarations, with commands that run from a fresh clone (`W313`) — and **no live figure**: where the corpus stands is a command it prints, because nothing rewrites a generated document when narrating or re-ingesting moves the answer (`W332`) |
| `.studyforge/installed.json` | what step 6 undoes, a digest per generated file, and the one module that is yours, marked `hand_written` with no digest |

### 4. Write the one file that is a person's

```
python3 -m pytest tests -q          # ⛔ it fails, and the failure is the specification
```

⭐ **`made.hand_written` names it** — `ingest/read.py`, three functions. Every
other file in the corpus is downstream of it and is generated.

⛔ **That command leaves the corpus valid, and this skill is what makes that
true** (`W329`). ⚠️ **Measured**: it writes `tests/__pycache__/*.pyc`, the
manifest this skill generated declared `tests/*.py`, and so the step this page
commands left `studyforge validate` exiting 1 on bytecode. ⭐ **Settled as
manifest data** — the generated glob is `tests/**`, which covers what the
generated tests produce — **never by telling you to clean up after a step you
were told to run.** `ingest/**` and `tests/ingest/**` always read this way.

⭐ **The install record marks it `hand_written` and keeps no digest of it**, so
a regenerate neither rewrites what you wrote nor records it (`INT-09/1`).
⛔ `hand_edited(root)` names every **generated** file whose bytes differ from
the record, and never yours: an empty list is R19 checked, not assumed.

### 5. Ingest, and let the machine say whether it worked

```
python3 -m ingest . <ingested-date>
studyforge validate .
```

⭐ **Exit 0 is the whole agreement.** ⛔ Not a shape somebody agreed looked
right — the same rule the adapter skill is written against.

⛔ **Nothing here has to be regenerated afterwards, and that is `W332`'s fix.**
`ONBOARDING.md` states **no** figure: how many units this corpus has, how many
are narrated and whether any needs a container are read on demand, by the
command that document prints, which reads the archive and the narration record
as they are at the moment it is typed:

```
python3 -m studyforge.skills.onboarding .
```

⚠️ **`W313` put those figures INTO the document and nothing refreshed them.**
⛔ Measured on the first corpus: it said *narrated: 0 of 38* while every unit
page carried audio, because narrating writes the narration record and no verb
rewrites a generated document. ⭐ **A count is a fact, and a fact in a generated
document can only be kept freshly wrong; a pointer resolves when it is read**
(Ruling 161). ⛔ **So the old instruction to re-run step 3 is GONE rather than
repeated louder** — an instruction that has to be remembered after every
narration is the defect, not the remedy.

**Consumer-side modules:** `ingest`

⛔ **That line is a declaration, read by a check, and it is the only thing that
exempts a commanded module from having to resolve in this repository.** Its
spelling is declared in `docs/conventions/commanded-pages.md`. ⭐ **The
corpus repository owns `ingest`** — the adapter skill's scaffold writes it into the
material's own tree, so it is importable where this skill is *pointed* and
nowhere here. ⚠️ **Every other `python3 -m` form on this page is the framework's
and is asserted runnable**, so a typo in one of them fails a check rather than
reaching a reader.

> ⚠️ **A note on the spelling.** `studyforge validate` is the installed
> command, registered by `pyproject.toml`, and it is the seam's name in the
> design documents and in prose. ⭐ `docs/authoring/` gives the module form that
> reaches the same code from a checkout nobody installed. ⛔ **The fenced form
> above is the one that runs**, because an agent executes a fence rather than
> reading it.

### 6. If it was the wrong repository, take it back out

```
python3 -c "from studyforge.skills.onboarding import uninstall; \
  print('\n'.join(uninstall('.')))"
```

⛔ **It removes exactly what it wrote, and refuses if any of it changed** —
naming every changed file at once. ⭐ **A file you filled in is not silently
destroyed**, which is why `ingest/read.py` is the usual reason a clean
uninstall refuses: it is removed only while it is still the stub.

### 7. ⛔ Write the findings log — the run is not done until it exists

⛔ **Exit 0 at step 5 says the archive is valid. It does not say what this run
found, and a run that found things and wrote them nowhere is not done** (`W346`).
⚠️ **Measured on the first conversion:** no step obliged a log, so its
milestone's whole deliverable was rebuilt by hand a milestone later from commit
bodies — ⛔ **and two of its seven numbered findings existed only in a hand-back
message and were found in no ref at all.**

⭐ **The log lives at `.studyforge/findings.md`**, the one place this procedure
names for it, and `studyforge.skills.delivery.LOG` spells it. `.studyforge/` is
this tool's directory and `validate` skips it, so writing the log never makes
the corpus it describes invalid. ⛔ **It is written by the run, before the run
is declared done — never from memory afterwards.**

```python
from pathlib import Path
from studyforge.skills.delivery import LOG, Entry, FindingsLog

log = FindingsLog(run="<what this run was>", entries=(Entry(finding), ...))
Path(LOG).write_text("\n".join(log.lines()) + "\n", "utf-8")
```

- ⭐ **Every entry is a `Finding`** — the delivery skill's own record: a marker
  and, per claim, measured here or received. **Everything done by hand in steps
  1–6 is one**: a hand-settled manifest answer, a hand-edited generated file, a
  test a generator should have written.
- ⭐ **Every entry carries a disposition slot**: the question the integration
  catalogue's admission rule turns on — *could a skill have generated this?* —
  answered `yes` (a hole in a skill, R19, and which one), `no` (a candidate
  catalogue entry, and why no generator could write it), or left `open`.
  ⚠️ **`open` is allowed: the sort starts half done rather than finished**,
  and the delivery skill's step 9 is where it is finished.
- ⛔ **A run that found nothing says so with one `none` finding.** An empty log
  and a missing one read the same, and only one of them is news.

⛔ **Then close the run on it.** This exits non-zero, naming every gap at once,
when there is no log, when it holds no finding, or when a finding has no slot —
⛔ **a run without a log is refused, never silently green:**

```
python3 -c "from pathlib import Path; \
  from studyforge.skills.delivery import LOG, closing; \
  log = Path(LOG); \
  print('\n'.join(closing(log.read_text('utf-8') if log.exists() else None)))"
```

⭐ It prints every finding with its answer, and how many are still `open` —
⛔ **an unsorted log is reported as unsorted, never read as done.**

---

## ⛔ The escape hatch, because there always has to be one

⭐ A corpus may keep **hand-authored files this skill never generates and never
overwrites**, composed with the generated ones rather than replacing them. They
are named in the manifest, so what is hand-held is *visible* rather than
discovered when a regeneration destroys it.

⛔ **An override that shadows a generated file entirely is a finding**: it means
the generator could not express something, and hiding that behind an override is
how a framework acquires a consumer it cannot serve.

---

## Appendix — what this skill decides, and what it refuses to

⭐ **The `corpus_api` it writes is never below what the draft asked for and
never above what the data needs.** A manifest using `content.not_material` is
`2`; one that does not stays at the draft's version. ⛔ **A generator that emits
a key merely because the contract has one freezes that key on everybody** — R9 makes a rename a migration from the moment
the first manifest declares it, and *what a generator emits by default becomes
the convention*.

⭐ **It invents no key, and drops an empty optional one.** It adds no `media`
block — an absent one is a **stated** default of the manifest schema, so omission is the
declared path rather than a workaround — and it drops an empty
`permitted_edits`. ⚠️ A block a *person* put in the draft is theirs and
survives: the rule is that this generator adds nothing, not that it discards
what somebody declared.

⛔ **That includes `content.not_material`** (`INT06-1`): the draft's entries are
carried through as written, **merged** with the globs the onboarding generates.
⛔ **A glob declared on both sides is refused, never resolved by precedence** —
the refusal names the draft's entry and the generated side, every collision at
once — because the manifest refuses a repeated glob as two audits, and a person
retyping a generated declaration is the retyping R19 forbids.

⛔ **It never flips the media policy.** Generated media is committed by default;
when a corpus crosses the footprint ceiling this skill says so in the onboarding
report and names the two ways forward. **The manifest says what happens, and a
person changes the manifest.**

⛔ **It never writes an absolute path into any file it emits** (R7) — not into
the pin, not into the record, not into a refusal's message.
