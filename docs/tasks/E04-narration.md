# E04 — Narration

Reading the material aloud, and keeping what is spoken aligned with what is
shown.

**Shared context for this epic.** The whole design rests on one idea: displayed
text and spoken text are **two renderings of one list**, not two lists that
happen to agree. A single module owns both halves — the string handed to speech
synthesis and the stable id that string is addressed by — and every consumer
copies those ids rather than deriving its own. The page writes them into its
markup; the synthesis pass names its audio files from them. Drift is
structurally impossible rather than merely unlikely.

**An id is positional; a filename is positional plus a digest, and the two are
answering different questions.**

- ⛔ **The speech id is positional, never content-derived.** It is what a
  *structure* edit must not renumber — which is why SF-09 refuses to key a
  section off its heading, and why fixing a typo must not orphan a unit's audio.
- ⛔ **The clip's filename is `<speech-id>-<8 hex of sha256(spoken text)>`**
  (spec §8.2). It is what a *text* edit must change. CodeSignal decided currency
  by whether a file existed, and after a re-capture **619 clips went on speaking
  the previous wording** while the run reported "0 synthesised" and every gate
  stayed green. A stale clip that cannot be addressed cannot be served; a stale
  clip that merely fails a check can, the moment somebody skips the check.

⚠️ **An earlier draft of this epic gave "hashing renames every clip when a typo
is fixed" as the argument against digests. That is the argument *for* them** —
the rename is the mechanism. What it correctly protected was the *id*, and the
id is still positional. Both hold, and the filename carries both.

#### ⭐ `Q23`, ASKED BY PO-INTEGRATION AND RULED — **how is a clip keyed when 17 units share one source file?**

⛔ **Neither half of the key comes from the source path.** ⭐ **The speech id comes
from the unit's LOGICAL ADDRESS (`SF-01`) and the digest from the SPOKEN TEXT**, so
seventeen units sharing one `origin.path` key to seventeen distinct clips **by
construction**, with no corpus knowledge anywhere (R1).

⚠️ **The question arrived because `F21`'s ruling gave one integration's fourth
container `origin {path, section}`, and a reader could take `path` for the key.**
⛔ **`origin` is PROVENANCE, and provenance is never identity.** ⭐ **The
distinction was already carried by the two bullets above — *an id is positional* —
and this clause is the answer stated against the question so the next reader does
not have to re-derive it from a naming contract.**

⭐ **Registered and answered before its deadline task shipped, which is the whole
point of the deadline mechanism:** `delivery-flow.md` — a question that arrives
AFTER its deadline task has shipped has become a finding, and the cost is a schema
change under R9 rather than a schema decision.

#### ⛔ `W183` — WHAT AN `Owns` LINE NAMES, DECIDED OUT LOUD, SO THE NEXT ROW DOES NOT RE-DERIVE IT

⛔ **AN `Owns` LINE NAMES A SURFACE, NOT A MODULE.** ⭐ **It is the population
another row reads to find its collisions, so it must name what will be there
AFTER delivery — and a row naming a file that the R11 ceiling will split has
handed the collision paragraph a path that does not exist.**

⚠️ **This epic bought the decision twice, in one package, for one cause** —
`SF-16` split to `narrate/speakable/` and `SF-17` reached the same answer one row
later, both mid-delivery — ⭐ **and it is not two accidents: the line was drafted
against an imagined module and the ceiling was met at delivery.**

⛔ **AND IT IS NOT A SWEEP TO DIRECTORIES.** ⚠️ **Measured across the plan's live
`Owns` entries, in a developer worktree on the host: of those naming a `.py` file
and BUILT, the large majority delivered AS a file** — ⭐ **so `Owns` naming one
module is right where one module is genuinely enough, and rewriting every line to
a directory would answer the question by erasing it.** ⛔ **Both measured
exceptions are this epic's, and both are ported CodeSignal modules whose ceiling
was foreseeable BEFORE dispatch.** ⭐ **THE TEST, therefore:** name the
**directory** where the row's own R11 ceiling makes a split foreseeable at mint
time; name the **module** otherwise. ⚠️ **That forecast is a judgement about the
ceiling and never a pre-dispatch line-count estimate — `W64/8` retired exactly
that.** ⛔ **NO COUNT IS WRITTEN HERE** (Ruling 150's form): the population is
re-measured by whoever needs it, at their own ref.

⛔ **THE SECOND DIRECTION, AND IT COST MORE: a line can be too narrow in COVERAGE,
not only in granularity.** ⚠️ **No row owned the renderer that emits `data-audio`
at all**, though a frozen record assigns it and a neighbouring acceptance needs
it — ⭐ so the office had to widen into `render/page/` on written authorisation,
measuring disjointness itself, mid-delivery. ⛔ **A row's `Owns` covers every
surface its OWN Acceptance forces it to touch, or the acceptance is naming work
the row is not permitted to do.**

---

#### ⛔ RULING 187 (CTO round 48) — *asserted in both directions* proves SURJECTIVITY, not INJECTIVITY, and `SF-17` cannot catch a clip collision

⛔ **`SF-17`'s *"every `<audio>` source resolves to a file on disk, and every file
on disk is named by a page — asserted in both directions"* CANNOT detect a
collision.** ⚠️ **Seventeen clips colliding onto one filename means every `<audio>`
still resolves AND every file is still named by a page** — ⭐ **both stated
directions pass, the suite stays green, and sixteen units play the wrong audio.**

⭐ **THE OWED ASSERTION, and it is `SF-16`'s because the minter is `SF-16`'s:**
⛔ **`|clips| == |spoken units|`** — a cardinality equality, which is the only form
that states injectivity — **plus `SF-16`'s negative: two spoken units that differ
only in `origin.section` mint DIFFERENT names.** ⚠️ **Owed before `SF-16` ships,
NOT before `SF-17`**, because by `SF-17` the collision has already happened and
the assertion that would have caught it is the minter's.

⛔ **It is the sixth appearance of this family — the right property over the wrong
RELATION** (`CTO-45/1`, `CTO-46/1`, Ruling 182, Ruling 185, Ruling 186, this), and
that is why it is a ruling rather than one more acceptance clause.

**Display and speech legitimately differ.** A URL is dropped, an identifier is
respaced, a twenty-line method becomes one caption sentence. Because alignment
is at speech-unit granularity rather than word level, that difference never has
to be reconciled word by word — which is the design decision that makes the
whole feature tractable.

**Media is committed by default, and the default has a ceiling.** A clone that
carries its own audio speaks with nothing running, which is what R8 is for. But
narration is the largest thing this framework generates, and a corpus can
outgrow what a git remote will take — CodeSignal did, at **11.42 GiB of pack and
one file at 150.9 MiB**, and discovered it when the push became *impossible*
rather than merely large. So the policy is manifest data (SF-02), the footprint
is **measured and reported** (SF-32), and crossing the ceiling is a loud,
early, explained event rather than a failed push.

**Rulings that bite here:** R7 (the gate applies again here, regardless of what
ran upstream), R8 (`file://`), R10 (reproducible), R12 (tests), R19 (the
consuming half — including ignore rules — is generated from the policy).

#### ⛔ WHO INVOKES NARRATION, AND WHAT A PAGE SHOWS WITHOUT IT — ANSWERED, AND NOT ANSWERED HERE

⛔ **`W202` items 3 and 4 are ANSWERED, and this epic carries a POINTER rather
than a second copy** — ⭐ **their one home is
[`E09-delivery.md`'s `W202` section](E09-delivery.md#w202-what-a-build-is-the-six-decisions-answered-and-every-row-here-cites-them),
answers 3 and 4.** ⚠️ **Two sentences of consequence for the rows in THIS epic;
every detail is behind that pointer:**

- ⛔ **A BUILD NEVER SYNTHESISES.** ⭐ **`studyforge narrate` (`SF-42`, `M3`, in
  that epic) becomes the only caller of `narrate.synth` outside tests; `SF-17`
  stays the library and gains no verb.** ⚠️ **`W187`'s stopping point, named for
  the third time and now closed.**
- ⛔ **A PAGE SHOWS A PLAYER WHEN A RECORD PROMISES ONE, AND COMPLAINS ONLY ON A
  BROKEN PROMISE** — ⭐ **no record at all means a clean prose page with no
  player and no notice, because §7's three states (C5) make a narrationless
  corpus COMPLETE, not short.** ⚠️ **`SF-18`'s *"a unit with no generated audio
  says so"* is NARROWED by that: it says so when a record PROMISED the clip and
  says nothing when no record exists** — ⛔ **the distinction the tree cannot
  currently make, and the whole reason the user chose the expensive option.**

---

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E04-narration.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
