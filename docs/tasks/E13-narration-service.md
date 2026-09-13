# E13 — Narration service (shared repository)

Narration becomes a standalone repository, **`narrate-service`**: a
containerised batch synthesis API that turns keyed text segments into audio
artifacts. Spec §8.2 is the authority for this epic; read it before starting.

**The seam.** The service synthesises. It **never writes into a corpus** — it
returns artifacts, and the framework places them through its placement policy
(R4). A synthesis service that knew where a study site keeps its audio would be
a second authority on layout, which is exactly what R4 removes.

**Why its own repository.** Same argument as E12: several consumers, its own
release cadence, and correctness established by *measurement* (model, hardware,
driver) rather than by reading code. It is also useful entirely outside this
project — "narrate arbitrary text" is a general capability.

⛔ **The personal-data gate stays client-side and pre-request** (R7, NS-05).
Never in the service. An mp3 that speaks an account identifier is personal data
on disk that **cannot be grepped for afterwards** — unlike text, it is
unrecoverable once written and unfindable once shipped. From the framework's
point of view this service is a third party, and ungated text must never reach
it.

⚠️ **R10 carve-out.** Synthesised audio is not byte-for-byte reproducible — a
speech model may not emit identical bytes for identical input. Audio is instead
**content-addressed and cached**. R10 still applies in full to everything else.

⭐ **This epic depends on nothing in the framework and can start at M0**, like
E12. It was scheduled behind milestones it does not need.

⭐ **This service publishes a machine-readable consuming contract too** —
`consuming.json`, the same obligation TC-05 carries and for the same reason
(R19): image tag, ports, GPU-profile requirements and their opt-in flag,
environment, healthcheck, and the voices available. `SK-07` renders a corpus's
narration deployment from it, and ⛔ **a consumer never reads this repository's
Dockerfile or compose file** to work out how to run it. It belongs to whichever
task lands the profiles (NS-03) and the voice catalogue (NS-04); both must
contribute their half.

⛔ **AND A THIRD CONTRIBUTOR, WHICH THE SENTENCE ABOVE DOES NOT NAME AND RULING
330 CREATED.** ⭐ **`NS-02`'s batch manifest is a WIRE shape and takes no §R9 row;
it is the service's PROMISE, and the promise is versioned by `provides` in this
same file** (spec §R9, Ruling 330(b)). ⚠️ **So `provides` is bumped by any task
that changes what the service promises — `NS-02` included — and *two halves* was
a complete claim only while the manifest had nowhere to be versioned.**

⛔ **`NS-03` CREATES THE FILE.** ⭐ **Three contributors and no named creator is
`consuming.json` with the defect it exists to prevent** — ⚠️ **the seam neither
side can inspect from its own repository, which is why the spec rules only *what
stops two components inventing two shapes*.** ⛔ **`NS-03` lands the file, its
schema and `consuming_api`; `NS-02` and `NS-04` amend it.** ⭐ **That is the
DIRECTION the ordering below is derived from, and it is stated here rather than
inferred from which row happened to dispatch first.**

---

### NS-01 — Extract the service into its own repository
**Milestone** **M3** · **Depends on** — · **Team** pair
**Owns** `narrate-service` — the repository, the HTTP surface, the Kokoro engine
**Context** ~40k — spec §8.2, `CS/.pipeline/tools/tts/synth.py`, `CSD/docker-compose.yml` synthesis service

**Definition.** Stand up the repository and move synthesis behind an HTTP API
of its own, rather than a client pointed at somebody else's container. Carries
over the two properties today's implementation already gets right:
**chunking is the service's job** — it accepts a very long input and splits
internally, so no client keeps stitching logic — and **writes are atomic**,
landing in a temporary sibling and being renamed, so an interrupted run never
leaves a truncated file that looks finished.

**Acceptance.** The service synthesises a known string to a playable artifact
from a clean checkout. The API is documented. No consumer repository is
modified.

**Out of scope.** Batching (NS-02) and hardware independence (NS-03).

---

### NS-02 — Batch job API and content-addressed cache
**Milestone** **M3** · **Depends on** NS-01, NS-03 · **Team** pair
**Owns** the job API and the artifact store
**Context** ~35k — NS-01 output, spec §8.2

⛔ **THE `NS-03` EDGE IS RULING 330(c)'s AND IT WAS MINTED BY THE REGISTER, ROUND
53** — ⭐ **the version key for this row's output lives in `consuming.json`, and
`NS-03` is the task that lands that file** (the preamble above). ⚠️ **Without the
edge both rows of step 3.2 are dispatchable in parallel and ship in either order,
and half the orders leave a manifest versioned by a file that does not exist.**
⛔ **The edge is DIRECTIONAL and the reverse is a CYCLE: `NS-04` also contributes
to `consuming.json` and already depends on `NS-02`, so the file cannot be
COMPLETE before this row builds** — ⭐ **which is why the edge is to the row that
CREATES the file and not to every row that writes it.**

**Definition.** The shape the framework actually needs. Today's client sends
one request per unit and receives one file; narration ids are **positional and
per-speech-unit**, and the page's highlight sync needs **one clip per speech
unit** (E04). So a job is a list of `{id, text}` segments plus voice and format
parameters, and the response is a **manifest** — one artifact per id, each with
a content address — which the caller then fetches.

A batch rather than a request per segment because a corpus is thousands of
segments and per-request overhead is the difference between minutes and hours.
It also lets the service parallelise internally without any client knowing.

**Idempotent by content address.** Re-submitting a segment whose text and voice
parameters are unchanged returns the cached artifact without re-synthesising.
This is what makes incremental regeneration possible for the consumer (SF-17)
and it is the mechanism the R10 carve-out names.

**Acceptance.** A job of many segments returns one artifact per id plus a
manifest. Re-submitting an unchanged job synthesises nothing and returns the
same addresses. Changing one segment's text re-synthesises that segment only.
A partially failing job reports which ids failed and still returns the rest —
it does not discard successful work.

---

### NS-03 — Engine adapters and hardware independence
**Milestone** **M3** · **Depends on** NS-01 · **Team** pair
**Owns** the engine adapter interface, the CPU and GPU profiles
**Context** ~30k — NS-01 output, current synthesis service definition

**Definition.** R15's enforcement. The current deployment pins a GPU build for
one specific card generation and reserves **every** NVIDIA device on the host.
That is a legitimate *deployment*; it is not acceptable as *the* deployment —
"a step that only works on one person's machine is not done".

Introduces an engine adapter interface with at least two profiles: a **CPU
path that works anywhere**, as the default, and a **GPU profile** as opt-in.
Adding a different speech engine later must not touch the API.

**Acceptance.** Synthesis works on a machine with no GPU and no vendor runtime.
The GPU profile still works where the hardware exists. Switching profiles is a
deployment choice, not a code change. The engine in use is reported by the
service so a caller can record which one produced an artifact.

---

### NS-04 — Voice catalogue and selection
**Milestone** **M3** · **Depends on** NS-02 · **Team** solo
**Owns** the voice catalogue
**Context** ~20k — NS-02 output

**Definition.** Which voices exist, what they are called, and how a consumer
picks one per corpus. A voice is part of a segment's content address (NS-02),
so changing a corpus's voice correctly invalidates its cached audio — and
correctly does *not* invalidate another corpus's.

**Acceptance.** The catalogue is discoverable through the API. A corpus can
select a voice. Changing it re-synthesises that corpus and no other. An unknown
voice is refused with a clear message rather than silently defaulted.

---

### NS-05 — Framework client
**Milestone** **M3** · **Depends on** NS-02, SF-08 · **Team** solo
**Owns** `narrate/client.py` in `studyforge`
**Context** ~30k — NS-02 output, SF-08 output, `CS/.pipeline/tools/tts/synth.py`

**Definition.** The framework's thin, standard-library client for the service.
Submits batch jobs, fetches artifacts, and hands them to the placement policy —
**it decides nothing about where they land** (R4).

⛔ **This is where the gate lives.** Every segment passes `scrub` then
`assert_clean` **before the request leaves** — the same order the archive
writer uses, so a leak stops the run instead of being narrated aloud into a
file nobody can search. The service is a third party; this is the boundary.

Handles the service being absent as a **known state**, not a crash: a corpus
with no narration is a corpus that reads fine (R6, R8).

**Acceptance.** A leaking segment stops the run before any request is made —
asserted by inspecting what was sent, not what was written. Artifacts are
placed through the policy. The service being down produces a clear message and
no partial state. Standard library only.

---

### NS-06 — Agent-callable adapter
**Milestone** **M3** · **Depends on** NS-02 · **Team** solo
**Owns** the service's agent-facing surface
**Context** ~25k — `CS/.pipeline/tools/tts/server.py`, NS-02 output

**Definition.** An optional adapter letting an agent call synthesis directly,
carried over from CodeSignal's existing tool server. Useful for one-off
narration outside a corpus build, and for the skills of E11.

⚠️ One carried lesson, worth stating because it cost a debugging session:
**the protocol stream carries protocol bytes and nothing else.** A single stray
print, warning or traceback on the protocol channel corrupts it and the client
drops the connection reporting only a parse error. The existing server rebinds
its output handle for the whole run and keeps the real one privately, so a
careless print degrades to a log line instead of breaking the transport. Keep
that.

**Acceptance.** An agent can synthesise a segment through the adapter. A
deliberate print inside the synthesis path does not break the transport. The
adapter is optional — the service works fully without it.
