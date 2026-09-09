# ordinal-gap

**Rule violated:** spec §6 — *"unit ordinals are contiguous from 1"*, and R6
(a gap is reported, never silently tolerated).

**The one defect:** the container declares units 1 and 3 and ships archive
documents for units 1 and 3. Unit 2 does not exist anywhere. The map and the
archive **agree** with each other on purpose — this fixture is about the gap,
not about a map/archive disagreement, which is a different check.

**Expected of `studyforge validate` (SF-25):** exit 1, naming the container
and the missing ordinal.
