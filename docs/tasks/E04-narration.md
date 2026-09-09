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

**Rulings that bite here:** R7 (the gate applies again here, regardless of what
ran upstream), R8 (`file://`), R10 (reproducible), R12 (tests).

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

Audio is **generated, not committed**, and git-ignored: one corpus's narration
is gigabytes and it is reproducible from the archive. Regeneration is
incremental — an unchanged speech unit is not re-synthesised, because the
alternative is re-rendering an entire corpus to fix one sentence.

⚠️ **A fresh clone is therefore silent until narration is generated, and that is
the honest statement.** An earlier draft of this task claimed both that audio is
git-ignored *and* that "a clone speaks with no synthesis service running". Both
cannot be true. What survives is the placement claim — a unit's directory is
self-contained once the audio exists — and the degradation is already designed
for: SF-18 presents a unit with no audio as a stated state rather than a dead
control, and SK-03 treats an absent narration service as a known partial state.
⭐ Getting generated media *to* a clone is a delivery question, and spec §5 rules
that delivery never changes an href, so a mechanism can be added later without
touching a single page (`v2-backlog.md`).

**Acceptance.** A unit's clips are produced, named `<speech-id>-<digest>` by
SF-16's minter, and play from the page over `file://`. **Re-running with no
content change writes nothing and requests nothing. Re-running after a wording
change synthesises exactly the changed segments** — asserted by comparing the
set of files written, never by trusting the run's own report, which is precisely
what reported "0 synthesised" over 619 stale clips. **Every `<audio>` source on
a generated page resolves to a file on disk, and every file on disk is named by
a page — asserted in both directions.** Generated audio is git-ignored.
Synthesis failure for one unit does not corrupt another's clips.

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
