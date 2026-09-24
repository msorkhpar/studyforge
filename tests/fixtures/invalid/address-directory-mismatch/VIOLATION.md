# address-directory-mismatch

**Rule violated:** spec §6 — *"every `container.json` address matches the
directory holding it"*, and R6 (fail loud). The archive documents agree with
the container map; both disagree with the directory.

**The one defect:** the container map and its unit documents declare the
address `["solo"]` while the directory holding them is `archive/not-solo/`.
Digests, ordinals, versions and every string are otherwise valid.

**Expected of `studyforge validate`:** exit 1, naming the directory
and the address it holds. ⚠️ It is *not* resolved by preferring one over the
other — §6 rules that a disagreement about an address is a refusal, because
one reading would be linked from the page and the other from the index.
