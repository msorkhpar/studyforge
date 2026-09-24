# personal-data

**Rule violated:** R7 — no personal data reaches disk or the wire; the gate
**refuses** rather than rewrites (spec §6: *"`assert_clean` passes on every
string"*).

**The one defect:** the `para` block in
`archive/solo/raw/prose/unit-01/lesson-1.json` carries two personal-data
shapes — an absolute home path and an email address. Its `content_sha256`
correctly covers those blocks, its ordinals are contiguous, its address
matches its directory and its versions are known: the corpus is valid in
every respect except this one.

⛔ **Every value here is fabricated.** `/home/example/project` is the
documented placeholder home path and `jane.doe@example.invalid` is under the
RFC 2606 reserved `.invalid` TLD, so it can never be delivered. Nothing in
this file came from any real machine, account or person. `contact@example.com`
is deliberately **not** used: it is the scrubber's own replacement value, and
a gate that skips its own placeholder would not refuse this fixture at all.

**Expected of `studyforge validate` and of `assert_clean`:**
exit 1, naming the file and the *shape* that matched — never echoing the
matched text, because a refusal that quotes the leak has only relocated it
into a log.
