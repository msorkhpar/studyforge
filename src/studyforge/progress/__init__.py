"""The reader's local record of what they have read and what they have completed.

**What it does.** Stores and reads the two things a reader accumulates: which
sections they have marked read, and which practices they have completed. Local,
theirs, and never uploaded anywhere.

**How you use it.** Ask for a corpus's progress; record a section or a
practice. The served API exposes it; the page's own script keeps the same
record over `file://` where there is no server to ask, so a reader who never
starts one still keeps their place (R8).

**Depends on.** `address`. ⛔ Not on `serve` — the store is what the server
serves, not the other way round.

⚠️ **Two records, not one.** Reading progress and practice completion have
different sources of truth and different lifetimes: reading is asserted by the
reader, completion is earned from a grader, and collapsing them means a reader
can mark themselves through an exercise they never passed.

⭐ **This is the durable artifact the reader keeps** (R16) — the thing that
makes a generated site a personal record rather than a rendering.

**Skeleton at FND-01.** Filled by SF-21 (E05) and SF-30's `file://` half (E05).
"""
