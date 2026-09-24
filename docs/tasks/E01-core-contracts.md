# E01 — Core contracts

The framework's identity layer: what a thing *is* and where it *lives*, kept
strictly apart. Everything else in the project depends on this epic, and its
mistakes are the expensive kind — an address model that leaks a source's
assumptions makes R1 unenforceable everywhere downstream.

**Shared context for this epic.** CodeSignal's `layout.py` is the ancestor of
all five tasks and worth reading once for its reasoning, not its structure. It
was written because eight modules each rebuilt study paths from their own
string pieces, so moving the tree meant finding all eight — and missing one
left half the pipeline looking in the old place *with nothing failing loudly*.
That lesson survives; the single prescribed tree does not (§5).

**The split this epic introduces.** `layout.py` answered two questions at once:
*what is this thing* and *where does it go*. v1 separates them — SF-01 owns
identity, SF-03 owns location, SF-04 recovers identity from artifacts found on
disk. That separation is what makes flexible placement possible (R4).

**Rulings that bite here:** R1 (no source knowledge), R4 (location is data),
R9 (versioned contracts), R10 (reproducible), R11 (packages).

---

## The tasks

This epic is kept as high-level design. The text of its tasks — each one's
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch
`archive/process`, whole:

```sh
git show archive/process:docs/tasks/E01-core-contracts.md
```

Which milestone and step each task belongs to is in [`README.md`](README.md).
