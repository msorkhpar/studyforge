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
**Milestone** M4 · **Depends on** SF-10 · **Team** pair
**Owns** `narrate/speakable.py`
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

**Every speakable string re-enters the personal-data gate here**, regardless of
what ran upstream (R7). The speech path is gated independently because it
produces files under names derived from content structure, and a leak there
would be durable.

**Acceptance.** Ids are stable under a content edit that does not change
structure. **The filename changes under exactly that same edit** — asserted, and
it is the inverse of the line above rather than a restatement of it. Every id in
a rendered page has a corresponding clip and every clip has an id in the page —
asserted in both directions. A code block produces a caption, not a reading of
the code. The gate refuses a leaking string.

---

### SF-17 — Narration synthesis
**Milestone** M4 · **Depends on** SF-16, SF-03, NS-05 · **Team** solo
**Owns** `narrate/synth.py`
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
a page — asserted in both directions.** A clone with the clips present plays
them with no synthesis service running. **This module contains no reference to
git or to any ignore file** — asserted. Synthesis failure for one unit does not
corrupt another's clips.

---

### SF-32 — Media footprint policy ⭐ THE SKILL KNOWS WHEN TO STOP COMMITTING
**Milestone** **M4** · **Depends on** SF-02, SF-17 · **Team** solo
**Owns** `corpus/media.py`
**Context** ~20k — spec §5, SF-02's manifest, SK-07's ignore-rule generation

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
**Milestone** M4 · **Depends on** SF-12, SF-16 · **Team** pair
**Owns** `render/assets/narration.js`, `render/assets/narration.css`
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
