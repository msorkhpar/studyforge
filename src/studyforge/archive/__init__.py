"""The adapter seam: the archive document, the block vocabulary, and the personal-data gate.

**What it does.** Defines what an adapter writes and what the framework will
read — a versioned document per unit, whose body is a sequence of typed blocks
— plus the Markdown reader that produces those blocks and the gate every string
passes on the way in.

**How you use it.** An adapter writes archive documents to disk and runs
`studyforge validate`; that is its entire obligation and its definition of done
(R2). ⛔ The seam is **on disk, not in Python**: there are no callbacks, no
plugin registry and no framework API for an adapter to call, which is what lets
adapters be written in any language and assigned to different agents in
parallel.

**Depends on.** `address`. ⛔ Not on `render` or `serve`: the archive is the
input to a page, and a vocabulary that knows how it will be displayed has
already stopped being a vocabulary.

⛔ **The gate refuses rather than rewrites** (R7). No absolute home path,
account id, name or email reaches the archive. A scrubber that silently
rewrote would leave nobody knowing personal data had been there.

⚠️ **The vocabulary must cover what real material contains**, not what a clean
corpus contains: raw HTML appears in 18 files of one surveyed tutorial, and a
parser that raises on anything it does not recognise stops an ingest dead (C3).
Attachments — a dataset a lesson loads, a notebook — are a class of their own,
neither block nor rendered media (C4).

**Skeleton at FND-01.** Filled by SF-06, SF-07, SF-08 (E02).
"""
