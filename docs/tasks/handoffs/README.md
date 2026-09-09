Task handoff notes land here, one file per task ID.
See ../../conventions/agent-protocol.md.

## ⛔ A handoff is a record, and a quotation inside one is not a live defect

⚠️ **Read the date and the surrounding sentence before filing a finding from a
handoff.** These files say what was true when the task ran. They are annotated
with triage outcomes (`[local]` / `[structural]`, and a ruling), but their
original text is kept **verbatim** and is deliberately never rewritten — a
record that gets edited to match the present is a record of nothing.

⭐ **The worked example, because it has now been re-reported three times:**
several handoffs quote *"README and CLAUDE.md say R1–R19"*. That was true when it
was written. Both documents were corrected to **R1–R21** rounds ago, and every
remaining hit is a **quotation inside a historical handoff**. Grepping the tree
finds the quotations; checking the live documents finds the answer.

⛔ **Before reporting a defect you found in a handoff, check the file it is
about.** The handoff is evidence of what somebody saw; only the live document is
evidence of what is true.
