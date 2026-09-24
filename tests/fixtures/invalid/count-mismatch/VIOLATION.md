# count-mismatch

**Rule violated:** spec §6 — a document's `counts` are what it claims about its
own blocks, and a claim nothing recomputes is a claim nobody checks.

**The one defect:** `archive/solo/raw/prose/unit-01/lesson-1.json` says
`"paras": 2` and carries one paragraph. ⛔ Its `content_sha256` is correct, so
the digest check passes and **only** the count check fires — which is the point
of the fixture: a corpus can be byte-exact and still lie about itself.

⚠️ Why counts deserve a fixture of their own: `counts` is the field a consumer
reads *instead of* walking the blocks — a table of contents, a progress
estimate, a narration length. A wrong count is not caught by the digest,
renders no error, and is discovered as a reader's confusion.

**Expected of `studyforge validate`:** exit 1, naming the document and
that its counts disagree with its blocks.
