# bad-corpus-api

**Rule violated:** R9 — contracts are versioned, and an unknown version is
refused rather than migrated in place. Spec §6: *"the manifest parses and
`corpus_api` is known"*.

**The one defect:** `corpus.json` declares `"corpus_api": 99`. Everything
else in this corpus is valid.

**Expected of `studyforge validate` (SF-25):** exit 1, naming `corpus.json`
and the version it cannot read. Nothing is migrated and nothing is written.
