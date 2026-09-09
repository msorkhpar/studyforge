"""What makes a directory a source: the manifest, the container map, placement, discovery.

**What it does.** Reads `corpus.json` — the declaration that turns a directory
of teaching material into something this framework can build — and answers the
questions that follow from it: what the container levels are, what a container
contains, where generated output lands, and what artifacts already exist on
disk.

**How you use it.** Load the manifest first; everything else in this package
takes it. `placement` answers "where would this land" without writing anything,
which is what `studyforge plan` exposes so a corpus owner sees the diff before
a build makes it. `discovery` scans a source root for `*.unit.html` and
`*.section.html` and reads each file's embedded identity block.

**Depends on.** `address`. ⛔ Not on `render`, `serve` or any adapter (R1).

⛔ **Discovery replaces path inference** (R4). The framework never infers what a
file *is* from where it sits. `site.json` is a **cache of the scan and never the
authority** — a stale cache is detected and the scan wins.

⛔ **Generation is non-destructive** (R3). An edit to an existing file is
permitted only where the manifest's `permitted_edits` declares it, naming the
file, the exact insertion and why; a declared edit that turns out to remove or
rewrite a line is a build failure too, so a declaration cannot smuggle a
rewrite past the rule. The check reads the declaration and never hardcodes any
one corpus's exception.

**Skeleton at FND-01.** Filled by SF-02, SF-03, SF-04, SF-05 (E01) and SF-32 (E04).
"""
