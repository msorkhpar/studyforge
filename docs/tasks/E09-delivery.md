# E09 — Delivery

Making the Java corpus a thing somebody can actually open, and proving the
promises the rest of the plan made.

**Shared context for this epic.** Delivery is where the abstractions meet a
person on a machine, and it is where R3 (non-destructive), R8 (`file://` floor)
and R15 (containers) are either true or merely claimed. OPS-05 exists precisely
to convert a promise into a test.

**The consuming side of two shared components.** The toolchain image (E12) and
the narration service (E13) are shared and pinned as submodules; the compose
file, the mount list and the deployment choices are **this corpus's**, and they
stay here. See §8.1's seam table before writing OPS-01 or OPS-03.

⛔ **Most of this epic is now SK-07's output, not hand-written work** (R19).
`OPS-01`, `OPS-03`, `OPS-04`, `OPS-05` and `OPS-06` describe artifacts that must
**exist** in the Java repository; they no longer describe artifacts somebody
types there. Each remains a task because somebody must decide *what* this corpus
needs — which toolchains, which voice, which mounts, what the reader is told —
but the deciding is expressed as **manifest data**, and the artifact is
generated from it.

⚠️ **Read each of these as a specification of SK-07's output for this corpus.**
If a task here cannot be expressed as data plus a generator, that is the
finding, and it is a finding against the framework rather than against this
epic — because the second source will hit it too. This is the same argument
`SF-28` won for the build pipeline, finished.

---

## ⛔ W202 — WHAT A BUILD IS. THE SIX DECISIONS, ANSWERED, AND EVERY ROW HERE CITES THEM

⭐ **This section is the ONE home of the six answers.** ⛔ **A row that consumes
one CITES this section and does not re-derive it** (`W202`'s clause 4), and ⛔ **an
office that finds one inconvenient records a finding rather than deviating.**
⚠️ **1, 2 and 4 are the USER's own, given directly on 2026-09-12 with the options
and their costs in front of them: they are product promises and no office may
re-open one.** ⭐ **3, 5 and 6 are the register's, taken PO round 63.**

### ⭐ 1 — WHERE A BUILD WRITES → **NOWHERE BY DEFAULT. `--out` STAYS REQUIRED.**

⛔ **The command refuses without an explicit output directory, and it refuses
again if that directory does not already exist** — a build mints its own pages
and never its own root. ⭐ **This is what ships today, so the BEHAVIOUR does not
change; its STATUS does — it is now a decision rather than an accident of a
scoping increment.**

⚠️ **The costs, accepted out loud:** there is no zero-argument demo and every
invocation carries the flag. ⭐ **What it buys: no path is ever guessed, R3 is
never engaged by a default, and the existing refusal already explains itself.**

### ⭐ 2 — WHAT A REBUILD DOES → **OVERWRITE ONLY WHAT THE BUILD ITSELF WROTE.**

⛔ **A rebuild replaces the files the build created and REFUSES ANYTHING ELSE BY
NAME.** ⭐ **The footprint is KNOWN rather than guessed: `studyforge plan`
already enumerates every path a build creates, goldened and asserted** — that
enumeration is what makes this honest rather than a shrug, and it is why the
answer is (a) and not *refuse unless `--force`*.

⛔ **THE R3 REFINEMENT THIS CARRIES IS THE SPEC'S AND LIVES AT R3** — ⭐ **R3
distinguishes the build's own prior output from the user's material** — ⚠️ **and
it is stated ONCE, in
[the spec at R3](../specs/2026-09-08-studyforge-v1-design.md), not restated here.**

⚠️ **Today's behaviour is the OTHER one:** measured at `6ffba1e`, a second
`studyforge build` into the same directory refuses all eight paths and exits
`1`. ⛔ **Nothing owned the change, so the register minted the row that does.**

### ⛔ 3 — WHO INVOKES NARRATION, AND WHEN → **NOT THE BUILD. A SEPARATE, EXPLICIT STAGE.**

⛔ **A BUILD NEVER SYNTHESISES AND NEVER TALKS TO THE NARRATION SERVICE.**
⭐ **Synthesis is its own stage with its own verb, `studyforge narrate <corpus>`:
it is the only thing in this framework that probes the service, writes clips, or
writes the narration record.** ⛔ **A build READS that record and never writes
one.**

⭐ **WHEN: the record and the clips are INPUTS to a build, exactly like the
archive.** ⛔ **So the order is `narrate` then `build`, and a `narrate` after a
build is answered by a REBUILD rather than by a page rewrite** — which is only
affordable because answer 2 made a rebuild legal. ⭐ **WHO: a person, or the
build-and-serve skill (`SK-03`). Never a build, never a test, never `serve`.**

⚠️ **Four grounds, and the first is the one that would have been paid for late:**

1. ⛔ **R8 and §11.0 — the reading floor is offline with no server.** ⭐ **A
   build that probed a synthesis service would make the FLOOR'S OWN PRODUCER
   depend on a network service, which is the property the floor exists to have.**
2. ⛔ **Answer 2 depends on the build's footprint being exactly what
   `studyforge plan` enumerates.** ⚠️ **Clips are placed by `corpus.placement`,
   beside the material — NOT under `--out`** — ⭐ **so a build that also
   synthesised would write outside its own enumerated footprint and *overwrite
   only what the build itself wrote* would stop being decidable.**
3. ⭐ **This epic already asserts stage independence** — *regenerating one
   lesson's narration should not rebuild every page* — ⛔ **and that property is
   only TRUE if narration is a stage a caller can invoke alone.**
4. ⭐ **`narrate.synth`'s shipped contract already assumes this caller:**
   *`probe()` is the caller's, and a build probes once for a whole corpus rather
   than once per unit* (`NS-05`'s *For dependents*). ⛔ **The library was built
   for a caller nobody had named; this names it.**

⛔ **THE CONSEQUENCE FOR `M3`:** ⭐ **the verb is what makes *narration is
generated* performable, so it is an `M3` obligation and it is `SF-42` below.**
⭐ **Its STEP MEMBERSHIP is [`README.md`](README.md)'s: step `3.6`, given by
[`W206`](rows/W206.md) in PO round 64.**

### ⭐ 4 — A CORPUS WITH NO NARRATION RECORD → **PLAYER WHEN PROMISED; COMPLAIN ONLY ON A BROKEN PROMISE.**

| state | ⛔ what the page shows |
|---|---|
| no record at all | ⭐ clean prose page — **no player, no notice** |
| record present, every clip on disk | player, and the audio plays |
| ⛔ record PROMISED a clip that is **not** on disk | player, **and the page names the gap** |

⛔ **THE DEFECT THIS FIXES:** ⭐ **today a corpus that was NEVER NARRATED renders
IDENTICALLY to one whose audio FAILED.** ⚠️ **After this, *never narrated* and
*narration broke* are distinguishable to a reader.**

⭐ **It follows the spec rather than fighting it:** §7's three states (C5) and
§11.0's reading floor say a corpus without narration is **COMPLETE, NOT SHORT**,
so a finished prose corpus carries no permanent *something is missing* notice.
⛔ **The rejected option — a visible disabled player — is the one that
contradicts that, and it was refused on exactly that ground.**

⚠️ **Cost, accepted: more machinery, and the third row of the table is only
fully testable once something actually narrates a corpus** — ⭐ **which is
answer 3's verb.**

### ⭐ 5 — WHERE THE BUILD PACKAGE HOMES → **`generate/` STAYS, AND NOW ON MERIT.**

⚠️ **It was chosen to dodge [`W200`](rows/W200.md) — the root ignore file's bare
`build/` would have swallowed `src/studyforge/build/`.** ⛔ **That is not a
reason to keep a name, so here is one:**

1. ⭐ **`generate` is the SPEC'S OWN WORD for this act** — R3 is *"Generation is
   non-destructive"* and R19 is *"the consuming half of a corpus is
   generated"*. ⛔ **The package is named after the rule that binds it.**
2. ⛔ **`build/` is reserved by convention in a Python source tree** — every
   packaging toolchain writes one — ⭐ **so `W200`'s ignore rule is CORRECT about
   `build/` in general and only over-broad about its scope.**
3. ⭐ **`build` is the VERB A READER TYPES; `generate` is the package that
   answers it.** ⛔ **The two are allowed to differ, and one already does:
   `cli/plan/` matches its verb because a CLI package must, and an engine
   package is not a verb.**

⛔ **[`W200`](rows/W200.md) IS NOT DISCHARGED BY THIS.** ⚠️ **Its subject is a
bare pattern that ignores more than it means to; that stands whatever this
package is called** — ⭐ **and this answer removes the deadline from it, not the
row.**

### ⛔ 6 — DRAIN OR STOP → **BOTH, AT A NAMED SEAM. IT DIVERGES FROM `validate` DELIBERATELY.**

⛔ **ANSWERED AGAINST `validate`'s PRECEDENT EXPLICITLY, which `W202` required.**
⭐ **`validate` DRAINS every check because its PRODUCT IS THE REPORT (R6): a
finding is its output, so stopping early would be shipping less of the thing
asked for.** ⛔ **A build's product is a SITE, so the rule is different and it is
not two personalities — it is one rule read against two products:**

> ⭐ **A BUILD DRAINS WHAT IT CAN STILL FINISH AROUND, AND STOPS ON WHAT MAKES
> FINISHING IMPOSSIBLE. `validate` DRAINS EVERYTHING BECAUSE ITS PRODUCT IS THE
> REPORT.**

| ⛔ the seam | ⭐ what happens | why |
|---|---|---|
| an occupied path (`refused`), a declared-but-unfetched file (`missing`) | ⭐ **DRAINED** — every one named, one exit code at the end | ⭐ a site is still produced around them, and `Written` already records them rather than raising |
| an unreadable manifest, container map or contents document | ⛔ **STOPS** | ⛔ there is no site to finish; and `studyforge validate` is the command ONE STEP EARLIER whose whole job is that report |

⭐ **THIS RATIFIES THE TREE RATHER THAN CHANGING IT.** ⛔ **`generate/writing.py`
already names `refused` and `missing` instead of raising, and
`generate/declarations.py`'s own docstring already states the stop and its
ground.** ⚠️ **So the office's *"changing it is one function"* was priced against
a build that stops everywhere, and the register's reading at `6ffba1e` is that
the seam already sits where the answer puts it** — ⭐ **what was missing was
anybody having DECIDED it, which is what makes the next module's author stop
re-deriving it.** ⛔ **What each module owes now is a CITATION of this answer in
place of its own paragraph of reasoning.**

## ⛔ W193 — WHICH CLIPS MAY BE DELETED → **NONE BY A BUILD, NONE UNASKED BY `narrate`, AND A PRUNE IS ITS OWN REQUEST**

⭐ **Answered by the register, PO round 64, where a builder and a narrator already look.**

1. ⛔ **A BUILD DELETES NO CLIP, EVER.** ⭐ **It follows from answers 2 and 3: clips sit
   beside the material under `corpus.placement`, outside the footprint `studyforge plan`
   enumerates, and a build only READS them.**
2. ⛔ **`studyforge narrate` DELETES NONE AS A SIDE EFFECT OF NARRATING.** ⭐ **It merges
   into the record (`SF-17`'s behaviour), so a run over any part of a corpus removes
   nothing.** ⚠️ **`SF-42`'s Acceptance already complies; a taker who adds deletion there
   has taken this decision in a code branch.**
3. ⭐ **A PRUNE IS ITS OWN EXPLICIT REQUEST, and its predicate is over the DOCUMENT, never
   the disk:** ⛔ **an entry whose speech id is absent from the corpus, over a walk of the
   WHOLE corpus — a partial walk refuses by name.** ⛔ **It deletes only clips the record
   names; any other file beside them is not its to touch** (answer 2's discrimination by
   PATH).
4. ⛔ **THE DISCLOSURE IS OWED EITHER WAY:** ⭐ **`narrate` reports how many record entries
   the corpus as walked did not produce.**

⛔ **R3 is the outer bound: a generated clip is still a file in somebody's repository.**
⭐ **Clauses 3 and 4 are carried out by [`W218`](BOARD-ARCHIVE.md#w218-w193s-rule-is-written-and-nothing-carries-it-out-dead-clips-count-against-a-shipped-ceiling-and-no-instrument-discloses-or-prunes-them)**: `narrate` prints the
dead-entry count on every run, and `--prune` in place of `--voice` is the prune. ⚠️ What it
HOLDS rather than deletes is in [its handoff](handoffs/W218.md), and reaching it is [`W226`](rows/W226.md).
⛔ **A scope added to `narrate` or `reconcile` lands in `Walk.unwalked`, or `--prune` reads
out-of-scope entries as dead** (`W218/4`: no partial REQUEST exists today; the partial walk
asserted is a declared unit with no material).

## ⛔ SF-38/8 — WHERE A BUILT PAGE'S AUDIO LIVES → UNDER `--out`, COPIED THERE BY THE BUILD

⭐ **Answered by the register, PO round 66, FROM THE USER'S OWN ANSWERS 1 AND 4 — no new
promise.** ⛔ **The defect (`SF-38/8`, host, `3937c65`, both `FND-04` fixtures): with `--out`
anywhere but the corpus root, no audio href resolves, the player is live, and no gap is named.**

| remedy | ⛔ what it breaks |
|---|---|
| refuse every `--out` but the corpus root | ⛔ **answer 1** — `--out` is the reader's choice of where a site goes; one permitted choice empties it |
| the page names a gap | ⛔ **answer 4, row 2** — every clip IS on disk, and that row promises the audio PLAYS |
| ⭐ **the build copies each clip its pages address into its own output** | ⭐ **nothing** — answer 3 names the record and clips inputs *exactly like the archive*, and `SF-37` copies the archive's media so every reference a built page emits resolves to a file the build wrote |

⛔ **What stays true:** a build never synthesises, never writes beside the material, and
deletes no clip (answer 3; `W193` answer 1, whose *"only READS them"* is about the ORIGINALS).
⭐ **A copy under `--out` is the build's own output, enumerated by `studyforge plan`** (answer 2,
R3). ⛔ **At `--out` = the corpus root nothing is copied.** ⚠️ **Cost, accepted: a second copy of
the clips; a later `narrate` reaches the site by a REBUILD (answer 3's order); a copy the record
no longer names is not deleted (answer 2).** ⭐ **Carried out by [`W224`](rows/W224.md).**

---

### OPS-01 — Java toolchain image
**Milestone** **M6** · **Depends on** TC-03, TC-06 · **Team** solo
**Owns** `JS/docker/toolchain/`
**Context** ~30k — TC-02, TC-03, TC-05 outputs

**Definition.** This corpus's build of the shared toolchain image: **JDK 21 and
Maven**, and none of the Kotlin, Node or Python the CodeSignal build carries —
the selection TC-02 made possible, and the reason a smaller image is the normal
case rather than an optimisation.

Supplies the corpus's **prime project** (TC-03): a trivial project against the
repository's parent POM that resolves the plugin and dependency set into a
local repository the image ships, so the reader's first offline build needs no
download. ⚠️ Its sources must be real — an empty prime primes nothing while
appearing to succeed.

Pins a published image tag (TC-06); it does not fork the Dockerfile (R18).

⭐ **Expressed as data:** the toolchain list, the pinned tag and the prime
project's shape are manifest entries SK-07 renders from — not a hand-written
Dockerfile in this repository.

**Acceptance.** `mvn -o test` runs offline in the container against the real
repository. The editor opens on a practice workspace. The image is measurably
smaller than the full CodeSignal build. The pinned tag is recorded. **The build
context was generated by SK-07 and regenerates identically.**

---

### OPS-02 — Narration deployment
**Milestone** **M6** · **Depends on** NS-03 · **Team** solo
**Owns** the corpus's narration deployment configuration
**Context** ~20k — NS-03, NS-04 outputs

**Definition.** How this corpus reaches the narration service: which profile
(**CPU by default**, GPU opt-in — R15), which voice, and the fact that the
service is needed only at generation time. A reader who never regenerates
narration never needs it running (R8), and the site must make that obvious
rather than leaving somebody to discover it.

**Acceptance.** Narration generates on a machine with no GPU. The site plays
existing audio with the service stopped. The voice selection is recorded in the
corpus, so a change to it correctly invalidates only this corpus's audio.

---

### OPS-03 — Compose and study server
**Milestone** **M6** · **Depends on** OPS-01, OPS-02, SF-19b · **Team** solo
**Owns** `JS/docker-compose.yml`
**Context** ~30k — `TC/consuming.json` and `TC/docs/consuming.md`, the narration service's equivalent, SF-19b output  ⚠️ *not the extraction source (R20)*

**Definition.** The corpus's compose file — the per-project half of §8.1's
seam. One documented command brings the study site up.

⭐ **Generated by SK-07 from `TC/consuming.json` and the narration service's
equivalent**, plus this corpus's mount list and port choices as manifest data.
⛔ Never written by reading either component's Dockerfile (R18). The four
rulings below are properties the *generator* must honour and a test must assert
— not four things a person is trusted to remember.

The four inherited rulings, each with its failure mode, all of which TC-05
documents and this file must honour:

- **Loopback-only port binding, never `0.0.0.0`** — the editor is an
  unencrypted IDE with a shell.
- **Mount only the sources** — not the repository, not `$HOME`.
- **Run as the repository owner's uid:gid**, or the container leaves root-owned
  files on the host.
- **A bind source must exist before its container starts**, or docker creates
  it root-owned and the writer can never write it. Ordering is enforced by a
  health check, not by hope.

Two service policies carried deliberately: the **reading server restarts unless
stopped**, so it survives a reboot and the reader starts it once and forgets
it; the **editor container does not auto-start**, because starting a shell
because somebody opened a reading page is not a decision this file gets to make.

**Acceptance.** One command serves the site. The server returns after a host
restart. The editor container does not start unless asked. The port binds to
loopback only — asserted. Files created in the container are owned by the host
user.

---

### OPS-04 — Build pipeline
**Milestone** **M7** · **Depends on** SF-28, JS-06, SF-14, EX-04 · **Team** pair
**Owns** `JS/ingest/pipeline.py` — corpus configuration over SF-28, not orchestration
**Context** ~40k — every prior stage's entry point

**Definition.** One command from source material to finished site: ingest →
validate → unit documents → pages → narration → exercises → contents → index.

**Incremental and reproducible.** An unchanged lesson is not re-rendered; an
unchanged speech segment is not re-synthesised (E13's content addressing). The
alternative — rebuilding 166 units and their narration to fix one sentence — is
the difference between a tool somebody uses and one they avoid.

⚠️ **The entry points this task wires are the same ones E11's skills invoke.**
Keep them clean and named; a skill that has to reach past a public entry point
into internals is a sign this task drew its surface wrong.

**Acceptance.** A clean run produces all 166 unit pages, the root index, the
assets, the narration and the coverage report. A second run with no changes
rewrites nothing. The result opens over `file://`. Each stage can be run
independently.

⛔ **AND ONE CLAUSE RE-HOMED HERE FROM `SF-28` BY THE REGISTER, PO ROUND 61**
([`W197`](rows/W197.md)): ⭐ ***this task is expressible as CONFIGURATION over the
framework's build — demonstrated, not asserted.*** ⚠️ **It was written as an
acceptance clause on `SF-28` at M4, where this task does not yet exist, so it
could only ever have been discharged by inspection.** ⛔ **It is the same defect
Ruling 129 named one document over, and it lands where it can first be RUN.**

---

### OPS-05 — Non-destructive guarantee ⭐ NOW A FRAMEWORK CHECK
**Milestone** **M4** · **Depends on** SF-02, SF-03 · **Team** solo
**Owns** `studyforge/validate/nondestructive.py` — **framework code, not corpus code**
**Context** ~20k — R3, spec §5's placement dry-run

**Definition.** R3 as a **test rather than a promise**. After a build, no
pre-existing file in the target repository is modified, moved or deleted, except
the entries its manifest declares in `permitted_edits`.

⚠️ **This moved out of the Java corpus and into the framework, and the move is
the point.** It was written as `JS/ingest/guarantee.py`, asserting one hardcoded
exception — the `<module>practice</module>` line. A per-corpus test with a
per-corpus exception baked into it is one every future source rewrites, and the
one they will rewrite by loosening. ⛔ **The check reads the declaration** (R3):
it is the same check for every corpus, and what differs is data.

It also verifies the two things a declaration could otherwise be used to hide:
that each declared edit is genuinely **additive** — it adds a line, it does not
remove or rewrite one — and that no declared edit touches the three categories
R3 forbids outright (the root ignore file, version-control configuration, or a
file the material's own reader depends on as content).

This matters more than it looks. The entire argument for the `sibling` placement
profile, and for the LMS "enhancing rather than restructuring", rests on it
being true. Untested, it is an intention that erodes the first time a generator
finds it convenient to rewrite a README.

**Acceptance.** Passes on a correct build of the Java corpus. **Fails, naming the
file**, when a generator is deliberately made to touch an existing README.
**Fails when a declared edit rewrites a line rather than adding one.** Fails when
a corpus declares an edit to its root ignore file. Passes on a corpus whose
`permitted_edits` is empty and which touches nothing. **Contains no reference to
any corpus** — asserted (R1).

---

### OPS-06 — Reader documentation
**Milestone** **M7** · **Depends on** OPS-04 · **Team** solo
**Owns** `JS/README` study section
**Context** ~20k — SK-07's documentation template, EX-05's coverage numbers  ⚠️ *not the extraction source (R20)*

**Definition.** How to open and use the site, written for the **reader**, not
the builder. The shape that works, distilled into SK-07's template rather than
copied from another repository (R20): lead with the one address that matters,
state plainly that no agent and no service need be running to read the material,
and give an "if something looks wrong" section covering the failure modes that
actually happen rather than the ones that theoretically could.

⭐ **Generated by SK-07 from the corpus's actual state**, not written by hand:
how many units have narration, how many have exercises, how many are
reading-only, what needs a container and what does not. A hand-written README
tells the reader what was true on the day somebody wrote it. ⚠️ The prose that
is genuinely editorial — tone, the "if something looks wrong" entries this
corpus has actually seen — is manifest data or a declared hand-authored file
(SK-07), never an edit to the generated output.

Must cover: first-run on a fresh clone — **including the recursive clone**, the
single most common way somebody concludes the project is broken (FND-05); what
needs a container and what does not; and the real failure modes — no narration
generated yet, editor container down, styles missing.

**States coverage honestly**: how many units have exercises and how many are
reading-only, from EX-05's numbers, without softening them.

**Acceptance.** A reader following it from a fresh clone on another machine
reaches a working site. Every stated command works as written. Coverage
numbers match EX-05 exactly. No personal data anywhere in it (R7).

---

### SF-28 — The site build
**Milestone** **M4** · **Depends on** SF-10, SF-13, SF-14, SF-31 · **Team** pair
**Owns** `studyforge/generate/` — the corpus walk and the page writer — and
`tests/studyforge/generate/`
**Context** ~40k — spec §3.2, §9; the measured entry-point table in
[`handoffs/W195.md`](handoffs/W195.md)

⛔ **SPLIT BY THE REGISTER, PO ROUND 61 — [`W197`](rows/W197.md), and the split
lands here because the epic is where a task's definition lives.** ⭐ **One row
carrying one Definition and FIVE separately-headed acceptance additions minted by
four rulings becomes SIX rows and one re-homed clause.** ⛔ **NOTHING IS DROPPED
SILENTLY: the table says where every item went, and the two that leave this row's
milestone say so with the ruling that put them here.**

| the item, as `W197` tabulated it | where it is now | what minted it |
|---|---|---|
| the unit-page build | ⭐ **this row** | the original Definition |
| container pages, root index, the contents document | ⭐ **this row** | the original Definition |
| the contents → `Links`/`Crumb` join | ⭐ **this row** | the original Definition |
| `exercises: false` → `declared_practices = 0` | ⭐ **this row** | PO, 2026-09-10, from `SF-12/4` |
| plan and build agree PATH FOR PATH | ⭐ **this row** — it is the build's own pass condition | Ruling 99 |
| the media copy | ⭐ **`SF-37`** | PO, 2026-09-10, from `QA-03/8` |
| narration wiring — who invokes synthesis, and when | ⭐ **`SF-38`** | the original Definition; `W187`'s stopping point |
| `serve` | ⭐ **`SF-39`** | the original Definition |
| `[project.scripts]` and the eleven-file caveat sweep | ⭐ **`SF-40`**, which becomes its ONLY minter | Ruling 157 |
| the `OPS-*` regeneration diff | ⛔ **`SF-41`, and it moves to M7** — unmeetable at M4 a SECOND time | Ruling 129 |
| *`OPS-04` is expressible as configuration over this* | ⛔ **re-homed into `OPS-04`'s own Acceptance, M7** | the original Acceptance |

⛔ **THE PARTITION IS NOT INHERITED FROM THE HANDOFF THAT PROPOSED IT** (`W197`
clause 3): it is re-derived from this section's own five headed parts, and it
differs from the proposal in two places — Ruling 129's clause is NOT absorbed by
the build (it cannot run at M4) and `serve` is NOT the serving API (`SF-19a`
owns `serve/`; this is the CLI stage over it).

**Definition.** The framework's build, living **in the framework**: walk a
corpus's archive and write the site. Ingest is the adapter's; serving is
`SF-19a`'s and `SF-39`'s; **this row is everything between them.**

⛔ **This row exists because the plan had a hole that would have surfaced in v2,
too late.** `OPS-04` owned `JS/ingest/pipeline.py` — a file in the *consumer
repository* — which made the orchestration Java-specific. `SK-03`, the
source-agnostic build-and-serve skill, would then have been a wrapper around a
Java script, and the second adapter would have rewritten the pipeline. That
breaks R1, R2 and R16 simultaneously.

⭐ **Each stage is independently invocable**, because a reader regenerating one
lesson's narration should not rebuild every page. ⛔ **That property binds
`SF-37`, `SF-38` and `SF-39` as well, and `SF-40` is where the verbs that make
it observable are registered.**

**Acceptance.** Builds both `FND-04` fixtures with no corpus-specific code, and
no module in `generate/` names a source. ⛔ **Every page kind the fixtures
declare is WRITTEN — unit pages, container pages, the root index and the
contents document** — and the contents document is what supplies each page's
prev/next `Links` and its `Crumb` trail, so no caller retypes a trail.

⛔ **A corpus whose manifest carries `"exercises": false` builds units with
`practices.declared = 0`, and its pages therefore do NOT say "More to come".**
⭐ **`exercises: false` is a *declaration of zero*, not an absence** — one
direction only: `exercises: true` implies no count for any unit. ⚠️ **Without
this, every page of a complete prose corpus claims to be unfinished, which
contradicts spec §7's three states (C5) and §11.0's reading floor: a graderless
corpus is *complete at M4, not short*.** ⛔ **The renderer and `unit.builder` are
both correct — `None` is not zero — so the translation is this task's and
nobody else's.** Ruled by the PO 2026-09-10 from `SF-12/4`.

#### ⛔ Ruling 99 (CTO round 28) — plan and build agree PATH FOR PATH

⛔ **`studyforge plan` and this build agree PATH FOR PATH, on both `FND-04`
fixtures, asserted by running both and diffing** — not by inspection.

```bash
python3 -m studyforge.cli.plan tests/fixtures/depth1 | sed -n 's/^create //p' \
  | cut -d' ' -f1 | sort > /tmp/planned
<this task's build command> --out <root>            # then enumerate what it wrote
diff /tmp/planned /tmp/built                        # exit 0 is the pass
```

⭐ **Pass condition: `diff` exits 0 for `depth1` and for `depth2`, and the two
committed goldens — `tests/fixtures/golden/depth1.plan.txt` and
`depth2.plan.txt` — still match `plan`'s output at the same ref.** ⛔ **Both
halves, because a plan and a build that drifted together would pass the diff
alone.**

⚠️ **This clause was written on `SF-31` and could not be executed there: at M2
`src/` contained no writer at all.** ⭐ **`SF-31` produced three independent
substitutes and the goldens, and filed the clause rather than declaring it met.**
⛔ **`OPS-05` then asserts the other direction — that what was planned is what
happened, and that nothing else moved (R3).**

#### ⭐ WHAT THIS ROW STILL OWES AT `a606033`, and it is less than the whole

⛔ **PART OF THIS ROW IS ALREADY DELIVERED, so a taker who reads the Acceptance
alone will rebuild it.** ⭐ **`studyforge.generate` landed at `a606033` as the
first non-test caller the page renderer has ever had** — its surface is
`sources(root)`, `write_pages(root, into)`, `declared_practices(manifest, n)`,
`read_manifest(root)`, `containers(root, manifest)`.

| the clause | ⛔ what is left |
|---|---|
| the unit-page build | ⭐ **DONE** — unit pages are walked, built, placed, rendered and written |
| `exercises: false` → `declared = 0` | ⭐ **DONE** — implemented as a declaration of zero, both directions demonstrated |
| Ruling 99's path-for-path diff | ⚠️ **HALF** — the unit-page half runs against the committed plan goldens; the rest of the diff cannot pass until the rest of the site is written |
| container pages, root index, contents | ⛔ **OWED** |
| the contents → `Links`/`Crumb` join | ⛔ **OWED** — it exists only in `tests/studyforge/render/page/sites.py`, whose own docstring names this row as the caller it stands in for, and landing it here is what lets `bar_for`/`trail_for` be DELETED rather than duplicated |
| a rebuild policy | ⛔ **NOT THIS ROW'S TO INVENT** — `write_pages` writes over nothing and names what it refused; the decision is `W202`'s |

⚠️ **Three carries a taker should read before starting, and none is re-derived
here:** [`W198`](rows/W198.md) — nothing in `src/` declares where a unit's
authored overlay sits in an archive, so the build cannot apply one;
[`W201`](rows/W201.md) — the corpus walk is written three times and this row is
the one that can collapse them; [`W200`](rows/W200.md) — the root ignore file's
bare `build/` swallows a package named `build/`, which is why the package is
`generate/`.

---

### SF-37 — The build's media copy
**Milestone** **M4** · **Depends on** SF-28 · **Team** solo
**Owns** `studyforge/generate/media.py` — the media pass — and its tests. ⛔ **A
NAMED MODULE and not the package, so this row and `SF-38` can be dispatched into
one wave without two owners of one surface**
**Context** ~15k — `SF-12`'s handoff, `QA-03/8`

⛔ **SPLIT OUT OF `SF-28` BY THE REGISTER, PO ROUND 61** ([`W197`](rows/W197.md));
⭐ **the clause is the PO's of 2026-09-10, from `QA-03/8`, and it is carried here
verbatim in substance rather than restated.**

**Definition.** A built site's media resolves on disk. The renderer emits
`<img src="images/<basename>">` and **copies nothing** — `SF-12`'s own handoff
says so — and no task owned the copy, so today a media-bearing page renders the
broken-image glyph with its `alt` text wrapped under a correctly styled caption.

**Acceptance.** ⛔ **Every `src` and `href` a built page emits resolves to a file
the build wrote**, asserted over the **depth-1 fixture, which is the
media-bearing one**. ⭐ **Asserted in both directions (R12): a planted reference
to a file the build did not write turns the arm RED, and the pass condition is
the MOVED exit code** (Rulings 124, 348).

⚠️ **No existing test can see the defect**: `SF-12`'s reference check resolves
against a tree its own test *writes*, the bytes are stable, and the golden
matches. ⛔ **M4 is the earliest ref at which it can be observed, which is why
the clause lands at M4 and not earlier.**

---

### SF-38 — Narration in the build
**Milestone** **M4** · **Depends on** SF-28, SF-16, SF-17 · **Team** solo
**Owns** `studyforge/generate/narration.py` — the narration pass — and its tests
**Context** ~25k — E04, `narrate.synth`, `narrate.client.place`

⛔ **SPLIT OUT OF `SF-28` BY THE REGISTER, PO ROUND 61** ([`W197`](rows/W197.md)).
⭐ **It is `W187`'s stopping point, named for the third time: `W187` delivered the
document-level door and refused to invent who invokes narration and when.**

**Definition.** The build's narration pass: what a build does about audio.
Every page `studyforge.generate` writes today renders `SILENT`.

⭐ **UNBLOCKED, PO ROUND 63.** ⛔ **It stood blocked on
[`W202`](BOARD-ARCHIVE.md#w202-six-decisions-a-build-cannot-ship-without-answered-three-by-the-user-and-three-by-the-register)
items 3 and 4; both are ANSWERED above and this row CITES them rather than
re-deriving either.** ⚠️ **A taker who reaches a different answer inside this row
has taken a product decision in a code branch, which is the act `W202` existed
to prevent — the remedy is a finding, not a deviation.**

⛔ **WHAT ANSWER 3 MAKES THIS ROW: THE READ SIDE, AND ONLY THE READ SIDE.**
⭐ **A build never synthesises and never probes the service; the narration record
and its clips are INPUTS, like the archive. Producing them is `SF-42`'s verb and
`SF-17`'s library.** ⚠️ **So this module opens a record, resolves each unit's
clip against disk, and hands the renderer the three states — it makes no
request and mints no clip.**

**Acceptance.** ⛔ **Answer 4's three states, one test each, over the `FND-04`
fixtures:** a corpus with **no record** builds a page with **no player and no
notice**; a record whose every clip is **on disk** builds a page with a player
whose sources resolve; a record **promising a clip that is absent** builds a
page that **names the gap**. ⭐ **Asserted in both directions (R12): the
no-record page must not merely lack a source — a planted player on it turns the
arm RED — because *silently identical to a failed narration* is the exact defect
answer 4 exists to remove.**

⛔ **No module in this package imports `narrate.client` or `narrate.synth`'s
request path**, asserted — ⭐ **that import is the shape of a build that
synthesises, and answer 3 forbids it.** ⛔ **A corpus with no narration record
still BUILDS, exit `0`.** ⭐ **The pass is independently invocable: regenerating
narration does not rewrite pages whose speech did not change.**

#### ⛔ AMENDED PO ROUND 64 — THE READ SIDE MERGED AT `6199164` AND THIS ROW DOES NOT CLOSE

⭐ **Merged:** the renderer's three states (`render.page`'s `Narration.missing` and
`promised`, the gap panel) and the no-synthesis assertion over `generate/`, all asserted
over LIBRARY entry points. ⛔ **Measured at `5d37f73`, role `wt/po`, HOST: no module in
`src/studyforge/generate/` names the record, `playable` or `Narration`;
`generate/narration.py` does not exist; `generate/units.py` renders every page
`SILENT`.** ⚠️ **So no BUILD can produce the second or third state, and the Acceptance
above is a build's.**

⛔ **WHAT REMAINS — the Acceptance above is UNCHANGED and binds it:**

1. ⭐ **`generate/narration.py` opens the corpus's record, calls `playable_of` WITH
   `audio=`** (ask `synth.incremental.audio_dir`), **and partitions `silent` as
   [`handoffs/SF-38.md`](handoffs/SF-38.md) *For dependents* names** — ⛔ `NOT_RECORDED`
   is never a gap.
2. ⛔ **`generate/units.py`'s call into `render` passes that narration instead of
   `SILENT`.** ⚠️ **That call site is on this row's surface by necessity;
   `generate/writing.py` is `SF-43`'s and is not.**
3. ⛔ **The three states are asserted THROUGH `generate`, over the `FND-04` fixtures** —
   ⭐ **the renderer tests that merged are that half and do not discharge this one.**

#### ⭐ CLOSED PO ROUND 66 — `d2943d4`

⭐ **Both halves in; the whole Acceptance is judged at `f382a4a` in
[the record](BOARD-ARCHIVE.md#po-round-66-wave-19-closed-wave-20-named-sf-388-answered-from-the-users-own-answers-three-mints).**
⚠️ ***A player whose sources resolve* holds where `--out` is the corpus root, the only form its
tests build; elsewhere it is false, answered in
[§ SF-38/8](#sf-388-where-a-built-pages-audio-lives-under-out-copied-there-by-the-build) and
carried by [`W224`](rows/W224.md).**

---

### SF-39 — `studyforge serve`, the CLI stage
**Milestone** **M4** · **Depends on** SF-19a, SF-40 · **Team** solo
**Owns** `studyforge/cli/serve.py`
**Context** ~15k — `SF-19a`'s app wiring, spec §8.3

⛔ **SPLIT OUT OF `SF-28` BY THE REGISTER, PO ROUND 61** ([`W197`](rows/W197.md)).
⛔ **THIS ROW DOES NOT OWN `serve/`: `SF-19a` does.** ⭐ **It is the CLI stage that
starts what `SF-19a` built, and the distinction is the surface — a row whose
`Owns` reached into `serve/` would be a second author of the serving API.**

**Definition.** `studyforge serve` over a built site: the verb, its arguments,
and its exit behaviour. Serving the bytes is `SF-19a`'s.

**Acceptance.** Serves both `FND-04` fixtures from a built root. ⛔ **No module
in `cli/` names a source.** ⛔ **The Docker socket is never mounted into the
serving process** (spec §8.3) — not behind a flag, not "only locally".
⭐ **A site built by `SF-28` still opens over `file://` with no server**
(R8, spec §11.0), asserted rather than assumed, because a serve verb is the
first thing that can quietly make the floor depend on it.

---

### SF-40 — The console entry point, and the caveat sweep
**Milestone** **M4** · **Depends on** SF-28 · **Team** solo
**Owns** `pyproject.toml`'s `[project.scripts]` table — ⛔ **this row is its ONLY
minter, re-homed from `SF-28` by the register in PO round 61** — and the eleven
files the sweep below tabulates
**Context** ~25k — Ruling 157, `tests/test_authoring_reference.py`

⛔ **SPLIT OUT OF `SF-28` BY THE REGISTER, PO ROUND 61** ([`W197`](rows/W197.md)),
⭐ **on the coordinator's reading that ITEM 7 ALONE IS A WAVE.** ⚠️ **Ruling 157
named `SF-28` as `[project.scripts]`'s only minter; the ROLE moves with the work
and the row that holds it is this one. Nothing else may register a verb.**

**Definition.** The framework gets an installed command, and every document that
says it does not is corrected in the same branch.

⛔ **A check with a SCHEDULED EXPIRY is an acceptance condition on the task that
expires it.** `tests/test_authoring_reference.py`'s
`test_no_fence_anywhere_offers_a_console_script_that_does_not_exist` exists only
because there is no entry point. ⭐ **This task builds one, and the check is
CONVERTED — never deleted.**

⛔ **It is not deleted, and the rubric already says why at §2e:** *a row that goes
green by DISAPPEARING has removed or hidden the exception.* ⭐ **The blanket
refusal becomes a DERIVATION from `[project.scripts]`, and the population stays
whatever `commanded_pages()` returns:**

> **Converted predicate:** a fenced `studyforge <verb>` line names a verb the
> entry-point table registers. A verb that is not registered still fails; a
> registered one passes. ⛔ **Derived from `pyproject.toml`, never from a list
> in the test.**

⭐ **AND THE SECOND HALF, WHICH IS THE POINT: the divergence-caveat population
must read EMPTY.** ⛔ **A caveat that outlives its ground is the second copy
nobody re-measures** — the exact failure `CLAUDE.md` was rewritten over at round
34. So the test asserts **both directions**: the spelling is registered, **and**
no document still says the entry point is not built yet.

```bash
# ⛔ This row's second acceptance half. Both lines must print NOTHING at its merge ref.
git grep -InE 'console entry point|before .?SF-28.? registers|belongs to .?SF-28' \
  -- docs/authoring src/ tests/ pyproject.toml
# and the spelling the two SKILL.md fences and the adapter test pin:
git grep -In 'python3 -m studyforge\.validate' -- src/studyforge/skills tests/studyforge/skills
```

⛔ **CORRECTED BY THE REGISTER, PO ROUND 63, AND THE DEFECT WAS MINE: the
alternation above carried the literal `\[project\.scripts\]`, WHICH IS THE VERY
TABLE THIS ROW EXISTS TO ADD.** ⭐ **So sweep A could print nothing only if the
table were never named — including inside `pyproject.toml`, which declares it —
and the acceptance became UNSATISFIABLE the moment the row succeeded.**
⚠️ **`SF-40/1`, raised by the delivering office against the register; the office
measured the corrected pattern and it prints nothing.** ⛔ **The class — an
acceptance that cannot be met is indistinguishable from one nobody checked —
already has two open rows and is not re-minted here:
[`W49`](rows/W49.md) (acceptance clauses naming no instrument that can return
`no`) and [`W37`](rows/W37.md) (the repo-wide sweep for checks that cannot fail
by construction).** ⭐ **This case is recorded as `W49`'s second witness, which
is what the freeze's own lesson asks for: REACH before new text.**

⛔ **BLAST RADIUS — MEASURED BY THE PO AT `cab8a04`, AND IT IS ELEVEN FILES.**
⚠️ **`W61/4` counted FOUR; CTO round 41 corrected it to SIX; the derived
population is ELEVEN.** ⭐ **The two the CTO's six missed are the two that matter
most — `pyproject.toml` and `src/studyforge/cli/__init__.py` are where the
absence is DECLARED, so a sweep that misses them misses the ground the caveat is
about.** ⛔ **`PO-34/2`.** ⚠️ **A reading with an as-of: the population is
RE-MEASURED at dispatch and the figure below is a pointer to a reading, not a
reading** — ⛔ **and the sweep's own grep, not this table, is its pass condition.**

| # | file | what this row breaks in it |
|---|---|---|
| 1 | `docs/authoring/README.md` | the divergence caveat |
| 2 | `docs/authoring/validate.md` | the divergence caveat |
| 3 | ⛔ **`pyproject.toml`** | ⛔ **the declaration of absence itself** — `# No [project.scripts] yet` |
| 4 | ⛔ **`src/studyforge/cli/__init__.py`** | ⛔ **the module docstring restates the absence** |
| 5 | `src/studyforge/cli/plan/__main__.py` | *"belongs to `SF-28`"* |
| 6 | `src/studyforge/skills/adapter/SKILL.md` | the caveat **and** the fence |
| 7 | `src/studyforge/skills/onboarding/SKILL.md` | the caveat **and** the fence |
| 8 | `src/studyforge/validate/__main__.py` | *"before `SF-28` registers it"* |
| 9 | `tests/studyforge/validate/test_main.py` | *"before `SF-28` registers it"* |
| 10 | `tests/test_authoring_reference.py` | ⛔ **the predicate itself** |
| 11 | `tests/studyforge/skills/adapter/test_init.py` | ⛔ **asserts `python3 -m studyforge.validate <corpus-root>` is in the adapter skill** — no caveat text, so a caveat sweep alone cannot see it |

⚠️ **`src/studyforge/generate/__init__.py` and `tests/studyforge/generate/test_init.py`
also state the absence, in the `SF-28` spelling, and they landed after that
reading was taken** — ⭐ **which is exactly why the population is re-measured at
dispatch rather than read off this table.**

⛔ **A task that discovers eleven red files at its own merge gate spends a round
on it.** ⭐ **The CTO proved row 11 is not hypothetical: re-spelling the adapter
fence back to `studyforge validate <corpus-root>` gave `2 failed`, the second on
exactly that assertion.**

**Acceptance.** ⛔ **Both `git grep` lines above print NOTHING at this row's merge
ref**, the converted predicate derives its verb list from `pyproject.toml`, and
⭐ **a planted fence naming an unregistered verb still FAILS** — the pass
condition is the MOVED exit code (Rulings 124, 348), because a predicate that
cannot fail is the thing §2e refuses.

---

### SF-42 — `studyforge narrate`, the CLI stage ⭐ THE ACT `M3` IS WAITING ON
**Milestone** **M3** · **Depends on** SF-17, SF-40, NS-05 · **Team** solo
**Owns** `studyforge/cli/narrate/` — ⛔ **and NOT `narrate/`, which is `SF-16`'s
and `SF-17`'s**: a row whose `Owns` reached inside `narrate/` would be a second
author of the synthesis library. ⭐ **`SF-39`'s shape exactly, one stage over.**
**Context** ~20k — [answer 3 above](#3-who-invokes-narration-and-when-not-the-build-a-separate-explicit-stage),
`narrate.synth.synthesise`, `NS-05`'s *For dependents*, `SF-40`'s dispatcher notes

⛔ **MINTED BY THE REGISTER, PO ROUND 63, AS THE DIRECT CONSEQUENCE OF ANSWER 3.**
⭐ **Answer 3 says a build never synthesises, so SOMETHING ELSE MUST — and
nothing did: `narrate.synth` has been a library with no caller outside tests
since it landed.** ⚠️ **That absence is why `M3` could not close with all five
of its steps closed: its *Done when* is *"narration is generated"* and this
repository ran no synthesis.**

**Definition.** `studyforge narrate <corpus>` — the verb that turns a corpus's
speakable units into clips on disk and writes the narration record. It probes
the service once for the whole corpus, hands `narrate.synth` the answer, and
places what comes back through `corpus.placement`. ⛔ **Synthesising is
`SF-17`'s; this is the stage a person can type.**

**Acceptance.** ⛔ **A `FND-04` fixture corpus is NARRATED END TO END against a
running `narrate-service`, and clip files exist on disk afterwards** — ⭐ **which
is the leg `M3` is missing, and it is asserted as a reading of the DISK, never
as the run's own report** (`SF-17`'s *"0 synthesised" over 619 stale clips*).
⛔ **Re-running with no content change writes nothing and REQUESTS nothing**,
asserted over the set of ids submitted through a recording transport, not over
the report. ⛔ **An ABSENT service is a named refusal and never a traceback** —
`probe()` never raises for absence (R6, R8) — ⭐ **and a corpus with no narration
service still reads, which is the floor.** ⛔ **No module in `cli/` names a
source.** ⚠️ **Exit codes follow `cli/site/`'s: `0` narrated, `1` something the
corpus declared could not be produced, `2` the tool could not run at all.**

⭐ **STEP MEMBERSHIP GIVEN, PO ROUND 64: step `3.6` in [`README.md`](README.md)**,
⛔ **a NEW step, because `3.5` closed at `abee048` and a closed step's membership is
part of its close record** ([`W206`](rows/W206.md)).

---

### SF-43 — The rebuild, and the footprint it may replace
**Milestone** **M4** · **Depends on** SF-28, SF-40 · **Team** solo
**Owns** `studyforge/generate/writing.py`'s replacement policy and
`studyforge/cli/site/` — ⛔ **NAMED MODULES, so this row and `SF-38` can be
dispatched into one wave without two owners of one surface**
**Context** ~20k — [answer 2 above](#2-what-a-rebuild-does-overwrite-only-what-the-build-itself-wrote),
spec R3, `cli/plan/derive.plan_for` and its committed goldens

⛔ **MINTED BY THE REGISTER, PO ROUND 63.** ⭐ **Answer 2 is a USER decision and
nothing in the tree owned the change it implies.** ⚠️ **MEASURED at `6ffba1e`,
role `wt/po`, HOST, from an installed console script: a second
`studyforge build` into the same directory refuses every path it wrote the first
time and exits `1`** — ⛔ **which is the option the user did NOT choose.**

**Definition.** A rebuild replaces the files the build itself created and
refuses everything else by name. ⭐ **The permission is the ENUMERATION's, not
the directory's: a path `studyforge plan` names for this corpus may be
overwritten; a path it does not name is refused exactly as today**, which is the
spec's R3 refinement made operational.

**Acceptance.** ⛔ **Build twice into one directory: the second run exits `0` and
the tree is byte-identical to the first** — the pages are deterministic, so a
difference is a defect rather than a rebuild. ⛔ **A file at a path the
enumeration does NOT name survives untouched and is REFUSED BY NAME**, asserted
by planting a foreign file in the output root and reading it back byte for byte
after a rebuild. ⚠️ **The discrimination is by PATH and never by content — a
build cannot know a file was hand-edited** — ⭐ **so the honest promise is the
enumeration's, and that is why answer 2 rests on `studyforge plan` rather than
on a timestamp or a manifest of hashes.** ⛔ **Nothing outside the enumeration is
ever deleted and the output root is never emptied.** ⛔ **The enumeration and the
build still agree PATH FOR PATH** (Ruling 99) — ⚠️ **and this row makes that
agreement LOAD-BEARING FOR R3 rather than merely goldened, which raises what a
drift between them costs.**

---

### SF-41 — The `OPS-*` artifacts are regenerated and diffed
**Milestone** **M7** · **Depends on** OPS-01, OPS-03, OPS-04, OPS-05, OPS-06 · **Team** solo
**Owns** the `OPS-*` renderer beside `skills/onboarding/artifacts.py`, and its two
registration points — `artifacts.paths()` and `NOT_MATERIAL`
**Context** ~30k — R19, `SK-07/1`, E11's split table

⛔ **RE-HOMED A SECOND TIME BY THE REGISTER, PO ROUND 61** ([`W197`](rows/W197.md)),
⭐ **and the second re-homing is the finding.**

⛔ **THE CLAUSE.** *`OPS-01`, `OPS-03`, `OPS-04`, `OPS-05` and `OPS-06` are
PRODUCED BY THE ONBOARDING SKILL for a corpus, not hand-written — asserted by
regenerating them and diffing.* ⭐ **Ruling 129 moved it off `SK-07` in E11
because it could not be executed there.**

⚠️ **IT COULD NOT BE EXECUTED ON `SF-28` EITHER, AND FOR THE SAME REASON ONE
DOCUMENT FURTHER ON.** ⛔ **`SF-28` is M4. Of the five artifacts the clause
names, `OPS-05` is the only one at M4 — `OPS-01` and `OPS-03` are M6, and
`OPS-04` and `OPS-06` are M7 — so at `SF-28`'s merge ref there is nothing to
regenerate for four of the five.** ⭐ **Ruling 129's own remedy is the right one
and it is applied again rather than argued with: an unmeetable clause is SPLIT,
and it lands where it can first be RUN.**

#### ⛔ THE GENERAL FORM, STATED ONCE SO THE NEXT RE-HOME IS NOT A RE-PARENTING

⛔ **A CLAUSE DOES NOT BECOME SATISFIABLE BY MOVING TO A DIFFERENT ROW. IT BECOMES
SATISFIABLE BY MOVING TO A ROW THAT CAN REACH ITS SUBJECTS.** ⭐ **Ruling 129 moved
this clause off `SK-07` because `SK-07` could not reach the five `OPS-*` artifacts,
and put it on a row that could not reach four of them either — a re-parenting, not a
repair.** ⚠️ **The test is one question, asked at the destination and not at the
origin: *at THIS row's milestone, does every subject the clause names EXIST?*** ⛔ **If
the answer is no for any subject, the destination is wrong however natural it reads.**

⭐ **Applied twice in PO round 61, in both directions: this clause moved DOWN the plan
to M7 where its subjects exist, and *`OPS-04` is expressible as configuration over the
build* moved SIDEWAYS into `OPS-04`'s own Acceptance, which is the row that IS the
subject.**

**Acceptance.** Each of the five artifacts is regenerated from manifest data and
diffs clean against what the corpus repository holds. ⛔ **A sixth artifact added
without a glob fails in THIS repository rather than surfacing as `unclassified`
in somebody else's.** ⚠️ **R20: the diff is asserted over a corpus this
framework's own fixtures provide, never over a path inside a consumer
repository** — ⛔ **that dependency is what made the clause wrong on `SK-07`, and
re-homing it twice without fixing it would carry the defect a third time.**

---

### OPS-07 — Stale artifact reconciliation
**Milestone** **M7** · **Depends on** OPS-04 · **Team** solo
**Owns** `studyforge/cli/reconcile.py`
**Context** ~25k — SF-04 output, OPS-04 output

**Definition.** Discovery is scan-based (R4): the site is whatever artifacts
exist. So a lesson deleted or renamed upstream leaves its generated page,
audio and practice material behind, and **discovery faithfully reports a unit
that no longer exists** — a phantom in the contents that no rebuild removes,
because OPS-04 is incremental in the *add* direction only.

Names every generated artifact whose source is gone, and removes it on request.
⚠️ **Names first, removes second, and never removes anything it did not
generate** — it is deleting files inside somebody's material repository, which
is exactly where R3's caution applies most.

⛔ **A scoped run reconciles only within its scope.** It names and removes on
behalf of the units it **actually read**, never on behalf of one it skipped, and
its report says which scope it covered. This is not hypothetical: SF-28 makes
every stage independently invocable and OPS-04 is incremental precisely so a
reader can regenerate one unit — so a reconcile invoked for one unit that
removed everything the *whole corpus* no longer names would delete the corpus,
inside somebody's material repository. ⚠️ A filtered report written over a full
one lies about everything it did not look at.

⚠️ **The same sentence governs narration pruning** (spec §8.2): a re-worded
passage leaves its old clip on disk under the old digest, and the run that
deletes it must be a run that read that unit.

**Acceptance.** A deleted lesson's artifacts are named. Removal takes them and
nothing else. A hand-written file inside a generated directory is never
removed. Reports and removes nothing on a clean corpus. **A scoped run leaves
every out-of-scope artifact untouched and says so in its report.**
