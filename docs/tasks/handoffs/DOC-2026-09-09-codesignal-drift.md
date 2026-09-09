# DOC-2026-09-09 — handoff

Documentation review: `studyforge`'s design re-read against 32 hours of further
CodeSignal work, and against a decision taken since the design was frozen —
that a second, unnamed repository will be converted by the skills alone as the
test that this is a framework (spec §12).

**Status:** done

---

## What landed

**Spec** (`docs/specs/2026-09-08-studyforge-v1-design.md`, 828 → ~1,180 lines):

| | Change |
|---|---|
| R3 | Generalised from one hardcoded exception to a **declared, enumerated, asserted** set of additive edits, plus three categories never permitted however declared |
| R10 | Narrowed — a content digest in a filename is *not* a violation; the churn argument applies to **shared assets**, not to a per-page artifact |
| R11 | Dropped the two-file census for the principle plus "measure your own port surface at start" |
| **R19** | **New.** The consuming half of a corpus is generated, not hand-authored |
| §4 | `permitted_edits` in the manifest; `variants` is a **filing key only** |
| §5 | Delivery is orthogonal to placement; the **placement dry-run** |
| §6 | `origin` provenance on containers and units; **stage, validate, then move** |
| §8 preamble | Every CodeSignal measurement is a dated snapshot; port from HEAD |
| §8.2 | Corrected a false premise about the narration client; **the clip-filename digest ruling** |
| §8.5 | **New.** Progress is two records |
| §9 | Corpus onboarding; **a skill precedes the artifact it produces**; how a consumer obtains skills (pin + generated stubs) |
| §11 | Acceptance 2, 3, 6 and 11 rewritten — 11 was previously *unfalsifiable* |
| **§12** | **New.** Validating that the framework is a framework |

**Tasks** — four added, one milestone added, one epic resequenced:

- `TC-00` (M0) — minimal pinned JDK+Maven image. **Unblocks EX-00.**
- `SF-31` (M2) — `studyforge plan`, the placement dry-run.
- `SF-30` (M2) — reader state on the `file://` floor.
- `SK-07` (M2) — corpus onboarding. The second source's whole experience.
- `SF-32` (M4) — media footprint policy.
- `QA-04` / **M8** — the second source; the deliverable is the findings log.
- `SK-01`, `SK-02`, `SK-05` moved **M7 → M1/M2**.
- `OPS-05` moved out of the Java corpus into the framework.
- Amended: SF-02, SF-07, SF-08, SF-16, SF-17, SF-21, SF-25, SF-26, JS-01, JS-05,
  OPS-01/03/06/07, TC-05, E03/E04/E05/E07/E09/E10/E11/E12/E13 shared context.

---

## Decisions

**The provenance field is `origin`, not `source`.** `source` is already the
corpus's own identifier in `corpus.json`; two fields one word apart meaning
different things is a defect waiting for a tired reader.

**`OPS-05` kept its id while changing repository.** It is referenced from six
places; renaming it would have cost more than the inconsistency of an `OPS-`
task owning framework code. Its **Owns** line says where it actually lives.

**The two-agent split is recorded in `README.md`, not the spec.** It is how this
project is staffed, not a property of the design. The three seams it depends on
*are* in the spec, because they are contracts.

**Customisation is manifest data, never a hand-edit** (SK-07). This is the
ruling that lets "everything is generated" and "every corpus is different" both
be true. One declared escape hatch exists — hand-authored files the generator
never touches, *named in the manifest* so what is hand-held is visible rather
than discovered when a regeneration destroys it.

**Generated media is committed by default — reversing this review's own first
answer.** The reader ruled it: ⭐ *regenerable is not the same as available*, and
a clone that carries its own audio speaks with no service, no GPU and no network,
which is what R8 exists for. The earlier draft had audio git-ignored, which made
a fresh clone silent and made SF-17 self-contradictory in the other direction.

⚠️ **The interesting half is the ceiling, and it is why this is a task and not a
one-line default.** Narration is the largest thing the framework generates, and
CodeSignal proved a corpus can outgrow a git remote — 11.42 GiB of pack, one
file at 150.9 MiB — and that you find out *at the push*, after the history holds
the blob. So `SF-32` measures the footprint and ⛔ **refuses loudly at the
limit, never silently switching policy in either direction**: silently ignoring
media gives you clones that are quiet with no error; silently committing gives
you CodeSignal's push. The limits are manifest data because they are hosting
facts, not taste.

⛔ **Extraction itself is deliberately not built** (`v2-backlog.md`, V2-14). No
source in scope needs it, and building a delivery mechanism for a problem nobody
has is how a framework acquires machinery it cannot justify. §5's
delivery-orthogonal-to-placement ruling is what makes that safe to defer: when
extraction is built it moves the same bytes to the same paths, so not one page
changes.

---

## Surprises

**Acceptance item 11 was not merely unsatisfiable — it was unfalsifiable.** All
six skills were M7; the corpus was built by hand across M2–M6. "Was produced by
the skills" was a claim about history that nothing recorded. It is now something
git can answer: the scaffolding commits precede the source-reading commits.

**`EX-00` could not have run.** M0, no dependencies, and its first instruction
is to run `mvn test` — with the toolchain image at M5 and R15 forbidding a host
JDK. Worse than a scheduling slip: its deliverable is a **wall-clock measurement
that decides the shape of all of E08**, and one taken on an unpinned toolchain
cannot carry that.

**Three of §8's inherited-apparatus claims were checked and are still exactly
true** — no Docker socket mounted anywhere, the server still `--no-docker` with
`network_mode: host`, the three floating `:latest` tags still floating, and the
synthesis service still published on all interfaces while its own compose header
claims loopback-only. §8.1 and §8.3 needed no change.

**§8.2 stated a premise that was wrong when written.** "Today's client sends one
request per unit and gets one mp3 back" — it has always looped one request per
*speech unit*. The batch-API conclusion survives; the premise is corrected in
place rather than quietly deleted.

**Two of the review's own findings were withdrawn on a second pass** — a
governing rule about polite fetching (nothing in v1 touches a network) and a
census of files over the size ceiling (stale within 32 hours of being counted).
Both are in `v2-backlog.md` instead. Recorded because the *reason* generalises:
a rule with no caller, and a number that decays, both cost more than they buy.

---

## Findings — outside this scope, not fixed

**`CodeSignal/.pipeline/tools/run_unit_audio.py`'s docstring is stale.** It opens
*"The clips are committed."* Zero audio files are tracked — they became release
assets on 2026-09-08. This matters here because `SF-17` names that file as its
context source, so the port would inherit a false premise about how narration
reaches a clone. Not ours to fix; flagged for whoever next touches that module.

**`studyforge` has no `graphify-out/`.** R14 requires every repository to carry
a built graph and spec §11 item 12 asserts it. `FND-02` owns it; it has simply
not run yet. Noted so it is not mistaken for a convention nobody follows.

**`studyforge` has no remote.** R18 says each component has its own. `FND-05`
owns the workspace composition. Not blocking anything at M0.

---

## For dependents

**Everyone:** the spec is now R1–**R19** and has a **§12**. The instruction that
saves the most work is in §8's preamble — **port from HEAD, and measure your own
port surface at task start.** A dozen Markdown parser defects were fixed upstream
after the freeze; they are free if you port current source and cost full price
if you port the version quoted in a task's *Context*.

**Whoever picks up M0:** start `TC-00` before `EX-00`. `E12` and `E13` can also
start at M0 — neither depends on anything in the framework, and under a
two-agent split they are the only work available while the critical path is
blocked.

**Whoever picks up E07 or E09:** these epics are now largely the **output** of
`SK-02` and `SK-07`, not hand-written work. Anything you find yourself typing
that a second source would also have to type is a **finding against a skill**
(R19) — record it, do not absorb it.

**Whoever picks up SF-17 or E07:** the Java corpus's narration is estimated at
**~0.9 GiB** — scaled from CodeSignal's measured 57,427 clips at a ~125 KiB mean
— which is comfortably inside SF-32's default limits. ⭐ **That is an estimate
and must be measured at M4, not inherited.** Java lessons may be longer or
shorter than CodeSignal's; if the real number lands somewhere else, SF-32 is
what says so and the manifest's `media` block is where the answer changes.

**Whoever picks up SF-25:** the completeness check is the highest-value single
thing in this revision. `validate` is the only signal an integrator has (R2), and
a digest computed from the blocks cannot detect that the adapter never *saw* a
section. Build the deliberately-lossy fixture; it is the one that proves the
check works.
