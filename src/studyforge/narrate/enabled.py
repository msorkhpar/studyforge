r"""Whether narration is ON for one corpus and one run — ⛔ the one predicate that says so.

**What it does.** Answers one question every stage that reads narration asks
before it reads it: *is narration part of this corpus, for this run?*

**How you use it.**

    from studyforge.narrate.enabled import narration_on

    if narration_on(root, asked=arguments.narration):   # None: nobody asked this run
        ...judge, build or serve the clips...

**Depends on.** Nothing. ⛔ It opens no record and no clip: whether a corpus HAS
narration is the record's question (`synth.read_state`, whose `present=False`
is the reading floor, C5); whether narration is WANTED is this one's.

## ⛔ ONE PREDICATE, SO "NARRATION OFF" HAS ONE MEANING EVERYWHERE

⭐ **The user ruled narration optional per corpus and per run (2026-09-23)**,
and three stages read clips: `validate` judges whether they are current,
`build` links them and `serve` answers them. ⚠️ Three private answers to *is it
off?* would drift the way three readers of one record always have, and the
symptom would be a `validate` that reports stale clips for a corpus whose site
carries no player. ⭐ So each stage asks here.

## ⭐ THE ORDER: THIS RUN'S ANSWER, THEN THE CORPUS'S, THEN ON

1. `asked` — the run's own option — wins whenever it was given, either way.
2. ⚠️ **The corpus's recorded choice is not read yet.** Where it lives (a
   manifest field or the onboarding skill's committed record) is the decision
   of the row that makes narration optional; ⛔ **that row reads it HERE, from
   `root`, and nowhere else**, so every stage learns it at once.
3. Otherwise ON — ⭐ the behaviour every corpus had before the ruling, so a
   corpus nobody has asked about is judged exactly as it was.
"""

from __future__ import annotations

from pathlib import Path


def narration_on(root: Path | str, *, asked: bool | None = None) -> bool:
    """Return whether narration is on for the corpus at `root` in this run.

    ⛔ `asked` is `None` when the run was given no answer, never `False`: a run
    that said nothing has not turned narration off.
    """
    if asked is not None:
        return bool(asked)
    return True
