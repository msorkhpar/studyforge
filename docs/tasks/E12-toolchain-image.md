# E12 — Toolchain image (shared repository)

The embedded IDE is the most reusable thing CodeSignal built, and it becomes
its own repository: **`code-server-toolchain`**. Spec §8.1 is the authority for
this epic and should be read in full before starting any task in it.

**The seam.** The **image** is shared; the **compose file and its mounts** are
not. A consuming project supplies its own compose file, its own mount list, its
own container name and port, and a `prime/` project to warm the build cache.
Everything else — toolchains, extensions, the workbench lockdown, seed
settings, the entrypoint — comes from the image.

**Why this is a separate repo rather than a directory.** Three consumers
already exist or are planned (CodeSignal, the Java corpus, any future adapter),
each on its own release cadence, and the image is the one component whose
correctness is established by *measurement* rather than by reading code. A
consumer pins a tag; it does not fork a Dockerfile.

**Rulings that bite here:** R15 (containers), R10 (reproducible builds), R17
(document the contract).

⚠️ **Everything in spec §8.1's bullet list was measured, and none of it is
obvious.** A task that "simplifies" one of them without reproducing the
original failure has introduced a regression that will surface as a silent
misbehaviour — an extension that never loads, a tool that is missing only in
the terminal, a volume the server cannot write. Read §8.1 first.

⭐ **This epic is the head of the execution track (`TC-00`, M5), and nothing
before it needs it.** A corpus reaches the whole reading floor — narrated, navigable,
offline — without a container ever starting (spec §11.0), so putting a Docker
image in front of somebody converting a book was the wrong shape.

⚠️ **It briefly sat at M0–M2 on the theory that `SK-07` could not render a
compose file without `TC-05`.** True, and resolved the other way: onboarding
split, and `SK-09` — the execution half — lives with the contract it
needs, at M7 since PO round 74. `SK-07` at M2 generates the reading floor's artifacts and asks for no
container.

⭐ **It still depends on nothing in the framework**, so under a two-agent split
it remains work the framework agent can pull forward whenever its own critical
path is blocked. What changed is that nothing *waits* for it.

⛔ **REORDERED PO round 74 — user direction, 2026-09-12:** *"We can even move the code-server to when after we are a framework! Because that functionallity is needed mostly for when exercises are in the picture."* ⭐ **So `TC-00`, the runner image, stays at `M5` and CREATES `TC/`; `TC-01`…`TC-06` add the code-server image to it at `M7`.** ⛔ **§8.1's measured list binds that image unchanged when it lands** (spec §8.1, amended).

---

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E12-toolchain-image.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
