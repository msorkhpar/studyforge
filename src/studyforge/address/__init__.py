"""The logical address of a unit: N segments, joined, so its halves cannot be swapped.

**What it does.** Models where a unit sits in a corpus's hierarchy, and the
keys, slugs and identifiers derived from it. The depth is not two and not
fixed: it is exactly `len(levels)` from the corpus manifest, because a real
source may have one container level (a course, a group) or two (section →
module), and a contract that cannot express both is wrong (spec §1, §4).

**How you use it.** Build an address from a corpus's `levels` and the segment
values; ask it for its key, its slug, and its stable identifier. ⛔ Never
assemble one of those strings by hand elsewhere — the joined key exists
precisely so that two segments cannot be passed in the wrong order without a
type saying so, and that guarantee is void the moment a caller re-derives it.

**Depends on.** Nothing. This is the bottom of the framework, and every other
package depends on it rather than the reverse.

⚠️ **Identity survives a move; presentation need not** (R4). An address is
embedded in the artifact it names, so a page moved away from its assets is
still correctly identified and still resolves as the unit it is — while
rendering unstyled and silent, because assets resolve relative to the page.
Both are true and neither is a defect.

**Skeleton at FND-01.** Filled by SF-01 (E01).
"""
