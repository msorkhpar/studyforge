# E04 — Narration

Reading the material aloud, and keeping what is spoken aligned with what is
shown.

**Shared context for this epic.** The whole design rests on one idea: displayed
text and spoken text are **two renderings of one list**, not two lists that
happen to agree. A single module owns both halves — the string handed to speech
synthesis and the stable id that string is addressed by — and every consumer
copies those ids rather than deriving its own. The page writes them into its
markup; the synthesis pass names its audio files after them. Drift is
structurally impossible rather than merely unlikely.

**Ids are positional, never content-derived.** Hashing content would rename
every clip whenever a typo was fixed, and byte-for-byte reproducibility (R10)
needs stable ids anyway. Position gives both for free — and it is why SF-09
refuses to key a section off its heading.

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

**Every speakable string re-enters the personal-data gate here**, regardless of
what ran upstream (R7). The speech path is gated independently because it
produces files under names derived from content structure, and a leak there
would be durable.

**Acceptance.** Ids are stable under a content edit that does not change
structure. Every id in a rendered page has a corresponding clip and every clip
has an id in the page — asserted in both directions. A code block produces a
caption, not a reading of the code. The gate refuses a leaking string.

---

### SF-17 — Narration synthesis
**Milestone** M4 · **Depends on** SF-16, SF-03, NS-05 · **Team** solo
**Owns** `narrate/synth.py`
**Context** ~35k — `CS/tools/tts/`, `CS/tools/run_unit_audio.py`, OPS-02 output

**Definition.** Turning speakable units into audio clips and placing them
through the placement policy — for the Java corpus, beside the page that plays
them (§5), so a unit's directory is self-contained and a clone speaks with no
synthesis service running.

Audio is **generated, not committed**, and git-ignored: one course's narration
is tens of megabytes and it is reproducible from the archive. Regeneration is
incremental — an unchanged speech unit is not re-synthesised, because the
alternative is re-rendering an entire corpus to fix one sentence.

**Acceptance.** A unit's clips are produced, named by speech id, and play from
the page over `file://`. Re-running with no content change synthesises nothing.
Generated audio is git-ignored. Synthesis failure for one unit does not corrupt
another's clips.

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
