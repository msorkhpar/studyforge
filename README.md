# studyforge

**Status: planned, not built.** This repository currently contains a complete
design and task backlog. No framework code exists yet.

A source-agnostic framework that converts any body of teaching material into a
local, offline study site: a reading page per unit, narrated audio, a table of
contents, navigation, progress tracking, and — where the material supports it —
runnable practices with real graders.

It is extracted from the CodeSignal study system, which proved every one of
these surfaces against real material, and generalised so that any source can
populate the same contracts and get the same site out.

**The product is a set of skills**, not a bespoke pipeline: someone points a
skill at material they care about and gets this format back, then keeps it as a
durable personal record they can review, re-run and extend. The
`Claude-senior-java-engineer` tutorial repository is v1's proving ground, not
its destination.

---

## Start here

| Read | For |
|---|---|
| [`docs/specs/2026-09-08-studyforge-v1-design.md`](docs/specs/2026-09-08-studyforge-v1-design.md) | The design, and rulings **R1–R19** that every task cites |
| [`docs/tasks/README.md`](docs/tasks/README.md) | **81 tasks, 13 epics, 9 milestones** — the index, ordering and critical path |
| [`docs/conventions/`](docs/conventions/) | Module structure, graphify usage, the agent working agreement |
| [`docs/tasks/v2-backlog.md`](docs/tasks/v2-backlog.md) | Deliberately unplanned future work |

**Nothing has been implemented.** The first work is milestone **M0** —
`FND-01`…`FND-05`, `TC-00` and `TC-01` in parallel, then `EX-00`. Everything
else depends on it.

⛔ **`EX-00` is a spike that gates an entire epic.** It measures whether the
Java exercise strategy yields anything usable, for the cost of one agent-day,
before E08 is built. If it comes back negative, that is a successful spike and
E08 changes shape. Run it early. ⚠️ **It needs `TC-00`'s pinned image** — its
deliverable is a wall-clock measurement that decides the shape of E08, and one
taken on whatever JDK the host happens to have is not reproducible (R15).

## The workspace

Components are separate repositories composed as **submodules** of one parent
workspace (R18), so a single checkout is a complete system while each keeps its
own remote and cadence:

```
<workspace>/
  studyforge/                  this repo — the framework
  code-server-toolchain/       to be created (E12) — the embedded IDE image
  narrate-service/             to be created (E13) — batch speech synthesis
  CodeSignal/                  the extraction source; untouched in v1
  Claude-senior-java-engineer/ consumer 1, built in v1
  ISO-8583-jPOS-tutorial/      v2 adapter target
  Claude-SPARQL-tutorial/      v2 adapter target
```

`FND-05` stands the parent up. Until then the components are siblings on disk.

## Milestones

Ordered so each ends in something demonstrable, rather than nine layers that
only become a product at the end.

| | | Tasks |
|---|---|---|
| **M0** | Foundations; exercise feasibility known | 8 |
| **M1** | One page renders | 18 |
| **M2** | **All 166 Java units readable offline** — first genuinely useful state | 19 |
| **M3** | Served, with an API and a pass record | 5 |
| **M4** | Narrated; media footprint known | 11 |
| **M5** | Runs code | 6 |
| **M6** | Real practices with proven graders | 5 |
| **M7** | Built by the skills; accepted | 8 |
| **M8** | **A second, unnamed source converted by the skills alone** | 1 |

⭐ **M8 is the only milestone that tests the claim this project makes.**
Everything before it is satisfied by a framework with exactly one consumer.

## Two open items carried into implementation

Neither blocks M0; both are recorded so they are not rediscovered late.

1. **The container execution path has never run in anger.** CodeSignal ships
   `--no-docker` with `network_mode: host` and mounts no socket, so its
   `docker exec` mode is untested. `SF-20` must prove it against a real
   container — Run/Submit, the E08 gates and R15 all rest on it. The ruling on
   *where* execution runs is settled in spec §8.3; ⛔ the socket is never
   mounted into the serving process.
2. **R12 implies roughly 18,000 lines of new test code** that no task budget
   names, and **three tasks carry 51% of the port surface** (`SF-19` 2,743,
   `SF-12` 1,407, `SF-14` 1,179 of ~10,500). "Most tasks are solo" is false
   comfort. Recorded in E05's preamble.

## Provenance

The design was reviewed adversarially before being committed to. Every
"measured fact" in it was counted against the real repositories rather than
assumed — a process that corrected the curriculum section count, the
implementation/test pairing ceiling, the heading uniformity claim, and both
external tutorial shapes, and that produced the plan's single most valuable
addition (`EX-00`). Facts in these documents carry their counts; where
something is a hypothesis it says so.

## Licence

Not yet chosen.
