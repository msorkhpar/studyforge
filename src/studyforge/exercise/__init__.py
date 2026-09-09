"""What a practice is: the workspace it runs in, and how much its verdict is trusted.

**What it does.** Defines the three states an exercise can be in, the workspace
a reader works in, and the trust attached to whatever checks their answer.

**How you use it.** Read an exercise from a unit document; ask what state it is
in before rendering anything that implies a grade.

**Depends on.** `unit`, `address`. ⛔ Not on `execute` — running a grader is a
separate concern from saying what a grader's word is worth.

⛔ **Three states, not two** (C5). *No exercise*; an **ungraded** exercise — a
prompt the reader works, with nothing to check it; and a **graded** exercise,
whose verdict is then `authoritative` or `advisory` (R5). Only the third can
complete a practice. Collapsing the middle state into "no exercise" discards
real teaching content: one surveyed corpus has an exercise in every one of its
19 lessons and a test for none of them.

⛔ **Nothing generated is presented as more authoritative than it is** (R5). A
grader written by us against a hidden upstream grader is `advisory`. A grader
that shipped with the material and passes the gates is `authoritative`. The
framework refuses to render the first as the second.

⭐ **A corpus with no graders is complete, not short.** It finishes at the
reading floor, which is a whole product for prose material.

**Skeleton at FND-01.** Filled by SF-23 (E06).
"""
