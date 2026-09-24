# digest-mismatch

**Rule violated:** spec §6 — *"its `content_sha256` matches its blocks"*.
The re-ingest signal: a digest that disagrees with the blocks means the
material changed since it was read, and the archive is replaced and the
change reported (R6).

**The one defect:** `archive/solo/raw/prose/unit-01/lesson-1.json` carries
`"content_sha256"` of sixty-four zeroes. Its blocks, counts, address,
ordinals and version are all valid, and every other file in the corpus is
valid.

**Expected of `studyforge validate`:** exit 1, naming the document
and that its digest does not cover its blocks.
