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
| [`docs/specs/2026-09-08-studyforge-v1-design.md`](docs/specs/2026-09-08-studyforge-v1-design.md) | The design, and rulings **R1–R20** that every task cites |
| [`docs/tasks/README.md`](docs/tasks/README.md) | **83 tasks, 13 epics, 9 milestones** — the index, ordering and critical path |
| [`docs/conventions/`](docs/conventions/) | Module structure, the agent working agreement, the review rubric |
| [`docs/tasks/v2-backlog.md`](docs/tasks/v2-backlog.md) | Deliberately unplanned future work |

**Nothing has been implemented.** The first work is milestone **M0** —
`FND-01`…`FND-05`, all parallel. Everything else depends on it.

⭐ **The first consumer is a small corpus, not the 166-unit Java tutorial.** A
framework proven on a small source and then applied to a large one has been
tested; one grown around a large source and later pointed at a small one has
been fitted. So the plan's spine is the **reading floor** — narrated, navigable,
offline, no server — which is a complete product for prose material and lands by
M4. The execution track (containers, Run and Submit, graded practices) begins at
M5, and a corpus enters it only if its material is actually runnable.

## The workspace

Components are separate repositories that sit **side by side** on disk, pinned
by a tracked file rather than composed as submodules (R18, amended — see
`docs/conventions/workspace.md`). ⛔ Nothing is pushed to any remote, so a
submodule has no legal form here; `workspace.json` records the commit of each
component and `python3 -m tools.workspace verify` checks it. ⚠️ That reproduces
a configuration **across time on this machine**, and deliberately **not** across
machines:

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
| **M0** | Foundations | 5 |
| **M1** | One page renders | 15 |
| **M2** | **A corpus is readable** — first genuinely useful state | 12 |
| **M3** | Narrated; media footprint known | 10 |
| **M4** | Served, with an API and a pass record | 7 |
| **M5** | Runs code — *execution track begins* | 12 |
| **M6** | The Java corpus reads | 9 |
| **M7** | The Java corpus has practices | 12 |
| **M8** | **A further, unnamed source converted by the skills alone** | 1 |

⭐ **A prose corpus is finished at M4** — the reading floor is a complete
product, not a degraded one (spec §11.0).

⭐ **M8 is the only milestone that tests the claim this project makes.**
Everything before it is satisfied by a framework with two consumers it was
designed against.

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
