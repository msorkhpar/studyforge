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

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E13-narration-service.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
