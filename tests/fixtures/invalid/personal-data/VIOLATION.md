# personal-data

**Rule violated:** R7 — no personal data reaches disk or the wire; the gate
**refuses** rather than rewrites (spec §6: *"`assert_clean` passes on every
string"*).

**The one defect:** the `para` block in
`archive/solo/raw/prose/unit-01/lesson-1.json` carries an absolute home path.
It also carries an email address on a reserved domain, which the gate admits
as sample data, so the home path is what it refuses. Its `content_sha256`
correctly covers those blocks, its ordinals are contiguous, its address
matches its directory and its versions are known: the corpus is valid in
every respect except this one.

⛔ **Every value here is fabricated.** `/home/example/project` names an
account nobody has, and it is not the one placeholder home path the gate
admits (account `user`), so the gate refuses it. `jane.doe@example.invalid` is
under the RFC 2606 reserved `.invalid` TLD, so it can never be delivered.
Nothing in this file came from any real machine, account or person.

**Expected of `studyforge validate` and of `assert_clean`:**
exit 1, naming the file and the *shape* that matched — never echoing the
matched text, because a refusal that quotes the leak has only relocated it
into a log.
