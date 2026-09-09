"""The command runner — the only package in the framework that spawns a process.

**What it does.** Runs a reader's build, test or program inside a pinned
toolchain, captures its output, and filters it down to what the reader asked
for.

**How you use it.** Hand it a workspace and a command; take back an outcome
with a status, the captured output, and how long it took. ⛔ Nothing else in
the framework spawns a process — concentrating that in one package is what
makes "what can this program execute" a question with a readable answer rather
than an audit of the whole tree.

**Depends on.** The standard library. ⛔ Not on `serve`: the direction is
serve-depends-on-execute, and inverting it is how the web-facing process ends
up holding the socket that spec §8.3 forbids it.

⚠️ **Reproducibility comes from the image, not the host** (R15). A verdict that
only holds on one person's machine is not a verdict. The container is pinned in
E12's toolchain image; this package reaches it from outside.

⚠️ **Raw build output is not reader output.** A hundred lines of downloading
and task graph around three lines of test failure is a result the reader has to
excavate, so filtering is part of the contract rather than a nicety.

**Skeleton at FND-01.** Filled by SF-20 and SF-29 (E05).
"""
