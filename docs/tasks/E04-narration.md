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

---

### SF-16 — Speakable contract
**Milestone** **M3** · **Depends on** SF-10 · **Team** pair
**Owns** `narrate/speakable/` — ⭐ **the DIRECTORY, and `W183`'s decision above is why**: this delivered as a package and the line said `speakable.py` until after it had.
**Context** ~55k — `CS/tools/study/speakable.py`, `CS/tests/test_speakable.py`

**Definition.** The single source of truth for both halves of narration: what
is said, and what each spoken unit is called. Decides how each block type
becomes speech — prose read as written, a code block reduced to a caption
rather than read aloud, a table summarised rather than enumerated cell by cell.

⛔ **It also mints the clip filename**, because it is the only module that holds
both the id and the spoken text. Both the renderer that links a clip and the
client that places it call this one function. ⚠️ **A second minter is a page
asking for a file the placer never wrote, with no symptom but silence** — and it
is the specific way CodeSignal broke this: the runner was handed a bare speech
id while the page asked for the digest form, so every clip was missing and every
run re-synthesised the lot.

⛔ **Narration speaks a disclosure's summary and stops. It never walks the
body** (CTO ruling, `handoffs/CTO-2026-09-09-rulings-q1-q3.md`).

A `disclosure` block (SF-07) is content the author decided the reader should
**choose** to see. Reading it aloud overrides that decision silently, on a
surface the reader cannot see — the page still shows the section collapsed while
the audio gives away what is inside it. ⭐ **The decisive argument is §8.5's,
about read marks: a record the reader cannot trust is worse than none.**
Narration that *sometimes* reads out the answer is narration nobody can leave
playing, and that loses the feature for the whole corpus rather than for one
lesson. The constituency is real: all six SPARQL uses hide an exercise answer.

⚠️ **Withheld is not dropped, and R6 applies.** The summary gets a speech id; the
body gets **none**, so a clip for it cannot be minted or addressed. The unit's
speakable record states how many blocks it withheld, and the narration coverage
report names units with unspoken content — so the omission reads as a decision
rather than as a bug in the walker. ⛔ Do not invent a spoken sentence announcing
the hidden section: that is narration writing prose the author did not.

⚠️ **No manifest knob, deliberately.** The rule is uniform, so R1 holds with no
per-corpus data at all, and a knob nobody has asked for is the flexibility §4's
YAGNI refuses. If a real source wants its disclosures spoken, that is a v2
finding with a source behind it.

#### ⛔ One acceptance condition added by the PO, 2026-09-10 (round 24) — **Ruling 93 (`Q20`), carried by check 3**

⛔ **A FENCE IS NOT NARRATED, WHATEVER ITS LANGUAGE. And there is NO new field.**

⭐ **Option 2 of three, and option 3 is refused on a precedent this project has
already paid for.** ⚠️ **A manifest field listing *"which fence languages
narrate"* is a list of language names in the framework's configuration,
answering a question a fence already answers about itself** — ⛔ **which is the
CodeSignal failure verbatim: one list answered *"can this be filed here?"* and
*"can we generate a test for it?"*, and eight SQL courses became unfileable.**
⭐ **The spec already separated those two questions once** — `variants` is a
filing and presentation key and is **not** a code fence's language, which is a
block's own attribute from the archive. ⛔ **A `narrate_languages` field would
re-merge them.**

⭐ **The escape hatch is the archive, and it costs no field at all.** If a corpus
genuinely wants its Given/When/Then narrated, **its adapter emits those steps as
prose blocks rather than as `gherkin` fences** — the decision is made once, at
extraction, by the side that knows the material, and it arrives as data (R1).
⛔ **The framework never learns the word "gherkin".**

⚠️ **What the reader loses: nothing on the page.** The fence renders exactly as
written. ⛔ **What the *listener* loses, measured on ISO, is 2,106 lines of
`Given`/`When`/`Then` read aloud** — and integration catalogue entry 10 already
ruled that direction: *a 23-line box-drawing tree read aloud is 23 lines of
punctuation.* ⭐ **The reading floor narrates prose and shows everything; those
are two surfaces on purpose.**

⛔ **This costs E04 one acceptance condition and the spec's block vocabulary one
sentence.** ⚠️ **The spec sentence is OWED and lands with this task** — ⭐ **it is
the cheapest half of the ruling and the half that goes missing, which is C6.**
**Owed before M3; `ISO-12` is unblocked by it** (`PO-24/2`).

**Every speakable string re-enters the personal-data gate here**, regardless of
what ran upstream (R7). The speech path is gated independently because it
produces files under names derived from content structure, and a leak there
would be durable.

**Acceptance.** Ids are stable under a content edit that does not change
structure. **The filename changes under exactly that same edit** — asserted, and
it is the inverse of the line above rather than a restatement of it. Every id in
a rendered page has a corresponding clip and every clip has an id in the page —
asserted in both directions. ⛔ **And the CARDINALITY, which is a THIRD assertion
rather than a restatement of those two: `|clips| == |spoken units|`** — ⭐ **the
only form that states INJECTIVITY, because a COLLISION satisfies both directions
above** (Ruling 187). ⛔ **Plus the NEGATIVE, and it is this task's because this
task mints the name: two spoken units differing only in `origin.section` mint
DIFFERENT clip names** — ⚠️ **asserted against a fixture in which two units share
one `origin.path`, which `tests/fixtures/` does not carry today (`W95`).** A code
block produces a caption, not a reading of the code. **A disclosure's summary is spoken and no block inside it has an id** —
asserted against `depth1` unit 3, and the withheld count appears in the coverage
report. The gate refuses a leaking string.

---

### SF-17 — Narration synthesis
**Milestone** **M3** · **Depends on** SF-16, SF-03, NS-05 · **Team** solo
**Owns** `narrate/synth/` — ⭐ **the DIRECTORY** (`W183`): delivered as a package at the R11 ceiling, one row after `SF-16` reached the same answer for the same reason.
**Context** ~35k — `CS/tools/tts/`, `CS/tools/run_unit_audio.py`, OPS-02 output

**Definition.** Turning speakable units into audio clips and placing them
through the placement policy — for the Java corpus, beside the page that plays
them (§5), so that once a unit's audio exists its directory is self-contained
and plays with no synthesis service running.

Audio is **generated, and by default committed.** ⭐ *Regenerable is not the same
as available*: a clone that has the clips speaks with no synthesis service, no
GPU and no network, which is the whole point of R8. A corpus that ignores its
audio is asking every reader to stand up a TTS service before they can hear
anything, and most of them will not.

⚠️ **This reverses an earlier draft of this task, which said audio is
git-ignored — and which also claimed a clone would speak. Both could not be
true.** Committing resolves it in the direction that serves the reader. It has a
ceiling, and the ceiling is the whole of `SF-32`.

⛔ **Whether media is committed is a manifest policy, not a property of this
module** (`media` in `corpus.json`, SF-02). This module writes clips to the path
the placement policy gives it and has no opinion about git. ⭐ That separation is
what makes the switch cheap when a corpus outgrows the default: spec §5 rules
delivery orthogonal to placement, so an href never encodes how a file arrived,
and moving media out of git later moves the same bytes to the same paths.

Regeneration is incremental — an unchanged speech unit is not re-synthesised,
because the alternative is re-rendering an entire corpus to fix one sentence.
⚠️ SF-18 still presents a unit with no audio as a stated state rather than a
dead control, and SK-03 still treats an absent narration service as a known
partial state; committing the clips makes those the exception rather than every
fresh clone's first experience.

**Acceptance.** A unit's clips are produced, named `<speech-id>-<digest>` by
SF-16's minter, and play from the page over `file://`. **Re-running with no
content change writes nothing and requests nothing. Re-running after a wording
change synthesises exactly the changed segments** — asserted by comparing the
set of files written, never by trusting the run's own report, which is precisely
what reported "0 synthesised" over 619 stale clips. **Every `<audio>` source on
a generated page resolves to a file on disk, and every file on disk is named by
a page — asserted in both directions.** ⚠️ **That pair proves SURJECTIVITY and NOT
injectivity — any set of clips colliding onto one filename passes both directions
with the suite green** — ⛔ **so the reading that catches a collision is `SF-16`'s
`|clips| == |spoken units|`, owed before `SF-16` SHIPS and not here** (Ruling 187,
`W97`). A clone with the clips present plays
them with no synthesis service running. **This module contains no reference to
git or to any ignore file** — asserted. Synthesis failure for one unit does not
corrupt another's clips.

---

### SF-32 — Media footprint policy ⭐ THE SKILL KNOWS WHEN TO STOP COMMITTING
**Milestone** **M3** · **Depends on** SF-02, SF-17 · **Team** solo
**Owns** `corpus/media/` — ⚠️ **UNBUILT, and named as a DIRECTORY on the `W183` forecast, not on a measurement**: every built sibling under `corpus/` is a package, and this is the cheapest place to prove the decision rather than pay for it a third time. ⭐ **Delivering as a single module is NOT a defect** — the line is the ceiling's forecast, and the row narrows it in its handoff if one module was enough.
**Context** ~20k — spec §5, SF-02's manifest, SK-07's ignore-rule generation

⛔ ~~**`SF-32` owns these two field names, and renaming them is free exactly
until M2.**~~ **THE WINDOW HAS CLOSED — Ruling 104, CTO round 28, 2026-09-10.**

⛔ **`max_total_bytes` and `max_file_bytes` are frozen. Renaming either is now
an R9 migration and is `SF-32`'s to plan, not `SF-32`'s to do casually.**

⭐ **The trigger this note set for itself has fired, in both halves.** Measured
on `4bc66f0`:

```bash
grep -n 'max_total_bytes' tests/fixtures/depth*/corpus.json   # written
grep -n 'max_total_bytes' src/studyforge/cli/plan/report.py   # and now READ
#   lines 122-123 print the limits; 135-141 compare a projection against them
python3 -m studyforge.cli.plan tests/fixtures/depth2 --bytes-per-unit 2000000000
#   media footprint  EXCEEDS max_total_bytes — … against a limit of 5000000000
```

⚠️ **The note's own wording said *"the moment an adapter writes them, at M2"*,
and it is a stronger case than that: they are written by both `FND-04`
fixtures **and** read by a shipped command whose output is a committed golden.**
⛔ **A rename now moves two goldens, a `corpus_api` field and a consumer
contract three tasks are already told to build against** (`SF-31`'s *For
dependents*). ⭐ **Raised by `SF-31` as an R9 deadline expiring; recorded here
rather than in a handoff, because a deadline that expires only in a record is a
deadline nobody meets.**

**Definition.** Generated media is **committed by default** (SF-17), because a
clone that carries its own audio speaks with nothing running. That default holds
until a corpus is too big for it, and this module is what knows the difference.

It answers one question — *should this corpus's media be in git?* — from the
manifest's `media` policy and a **measurement** of what was actually generated:

```json
"media": { "commit": "auto",
           "max_total_bytes": 2147483648,
           "max_file_bytes": 94371840,
           "max_files": 20000 }
```

⛔ **`max_files` IS NOT ACCEPTED BY THE SHIPPED READER AND THIS EXAMPLE DOES NOT VALIDATE TODAY** — ⭐ **[`W207`](rows/W207.md) carries it, and the choice between adding the limit and dropping the key is that row's to make out loud.** ⚠️ **Named here rather than quietly corrected, because deleting the key would delete the only written record that a count limit was ever wanted.**

- `commit: always` — commit it, whatever the size. The corpus owner's call.
- `commit: never` — ignore it; the corpus supplies its own delivery.
- `commit: auto` *(default)* — commit while under the limits, and ⛔ **refuse and
  report the moment any limit is crossed.**

⛔ **`auto` never silently switches.** A generator that quietly started ignoring
media would produce a corpus whose clones are silent, with no error and no
symptom until a reader complains. And one that quietly kept committing produces
the CodeSignal outcome: **11.42 GiB of pack against a ~5 GB soft limit, one file
at 150.9 MiB against a hard 100 MiB per-file limit, and a push that was
impossible rather than merely large** — discovered at the remote, after the
history already contained the blob. ⭐ **Crossing the ceiling is a decision, and
this module's job is to put it in front of a person early**, naming the number,
the limit it crossed, and the two ways forward.

⚠️ **The defaults are hosting facts, not taste.** The per-file default sits under
GitHub's hard 100 MiB block; the total sits well under the pack pressure that
made CodeSignal's push impossible. They are defaults precisely because another
host has different ones — which is why they are manifest data.

**What it is not.** ⛔ **It does not implement extraction.** Packing media into
release assets and restoring it is real work with real traps and it is
**deliberately not in v1** (`v2-backlog.md`, V2-14) — no corpus in scope needs
it. This task builds the **awareness**: measure, compare, report, and generate
the right ignore rules for whichever answer applies. ⭐ When extraction is built,
it plugs in behind this decision without touching a page, because spec §5 rules
delivery orthogonal to placement.

**Consumers.** `SK-07` generates ignore rules from its verdict. `SF-31`'s
dry-run reports the *projected* footprint before anything is generated, so the
question is asked before the gigabytes exist. The coverage tracker reports the
actual one.

**Acceptance.** A corpus under the limits commits its media and a clone plays it.
A corpus over any one limit **fails, naming the limit, the measured value and
the file or count responsible** — never silently switching policy. `always` and
`never` are honoured without measurement. The verdict is derived from the files
actually on disk, not from a prediction. **The module names no host and no
forge** — the limits are data (R1). Changing a limit in the manifest changes the
verdict and nothing else.

---

### SF-18 — Player and highlight sync
**Milestone** **M3** · **Depends on** SF-12, SF-16 · **Team** pair
**Owns** `render/assets/narration.js`, `render/assets/narration.css`, and the narration renderer in `render/page/` — ⛔ **the third is `W183`'s COVERAGE direction and it was taken mid-delivery on written authorisation, disjointness measured at the time.** ⚠️ **`render/page/` as a whole is E03's**, and this is a NAMED surface inside it: the module that writes the `data-audio` attribute onto a unit, disjoint from E03's navigation module and from E05's mark control, which are named by their own rows. ⭐ **The attribute's CONSTANT is E03's and stays E03's** — this row writes it, it does not name it.
**Context** ~45k — `CS/tools/study/assets/*.js`, `CS` design note 02

**Definition.** The reading page's narration control: play and pause,
per-clip advance, and a highlight tracking the currently-spoken unit at
speech-unit granularity — the granularity SF-16 chose precisely so this is
achievable without word-level timing data.

**It degrades honestly** (R6). A unit with no generated audio says so rather
than presenting a dead control. A browser blocking autoplay is a known state
with a stated remedy — press play once — not a silent failure. Neither is
treated as an error, and neither is hidden.

**Acceptance.** Highlight tracks playback across a full unit. Works over
`file://`. A unit with no audio shows the stated message and no dead control.
Fully keyboard accessible. No network request (R8) — the player and its assets
are vendored, and anything that would fetch on init is disabled explicitly.
