**Kind:** index

Task handoff notes land here, one file per task ID.
See ../../conventions/agent-protocol.md.

## ⛔ Every document here declares what it is

⚠️ **Not everything in this directory is a task handoff, and the filename never
said which were.** Measured 2026-09-10: **10 of 53** were surveys, ruling
records or session logs, and **8 of those 10 already carried `— handoff` in
their own title**, because their authors started from the template.

⭐ **So each document declares its kind on its second line, and
`tools/quality/handoffs.py` reads the declaration rather than the name:**

```text
**Kind:** task handoff — W20        the six sections, the title, the markers
**Kind:** task handoff — W17, W19   two tasks; the title names both
**Kind:** ruling record             a CTO or PO round, or one ruling written up
**Kind:** session log               a coordinator's record of one session
**Kind:** survey                    a read-only investigation; nothing landed
**Kind:** index                     this file
```

⛔ **An undeclared document is refused** — the closed set failing the way a
closed set should, loudly and by name, where an exclusion list would have
admitted it silently and then been one entry short. A new kind of document
costs one entry in `DOCUMENT_KINDS` and the sentence saying what it owes.

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
