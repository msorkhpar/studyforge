"""The onboarding skill's steps 2 and 3, run as the skill document fences them.

⭐ **A fence is executed, not read.** Step 2's fence gets the draft from the
survey and passes `reasons`, so an agent that runs it on a corpus whose draft
proposes a `not_material` glob reaches the listing rather than a refusal.
⛔ The one line a person edits, the `reasons` mapping, is replaced by the
reasons the draft asks for, and the commit a wheel would carry is handed in;
every other line runs as written.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from studyforge.skills.onboarding import RECORD_FILE
from studyforge.skills.reconnaissance import survey
from tests.studyforge.skills.onboarding import corpora
from tests.support import repository_root

SKILL = repository_root() / "src/studyforge/skills/onboarding/SKILL.md"

#: The line of step 2's fence a person writes, and nothing else is replaced.
REASONS = re.compile(r"^reasons = .*$", re.MULTILINE)


def fence(step: str) -> str:
    """The first Python fence under the heading that opens `step`."""
    text = SKILL.read_text(encoding="utf-8")
    section = text[text.index(f"### {step}") :]
    return re.search(r"```python\n(.*?)```", section, re.DOTALL).group(1)


def test_step_two_gets_the_draft_from_the_survey_and_passes_reasons():
    step = fence("2.")
    assert 'survey(".").proposal' in step
    assert "reasons=reasons" in step


def test_steps_two_and_three_run_as_fenced_on_a_draft_with_open_globs(tmp_path):
    root = corpora.material(tmp_path / "corpus")
    opened = [e["glob"] for e in survey(root).proposal["content"].get("not_material", [])]
    assert opened, "the draft proposes a glob, so a fence without reasons is refused"
    given = {glob: "a reason a person gave, written by the test" for glob in opened}
    step = REASONS.sub(f"reasons = {given!r}", fence("2."), count=1)
    # ⚠️ A built wheel carries the commit it was built from; this test's
    # library is a source tree, so the commit is handed in, and only that.
    call = "onboard(draft, reasons=reasons)"
    assert call in step
    step = step.replace(
        call, f"onboard(draft, reasons=reasons, framework_commit={corpora.COMMIT!r})"
    )

    here = Path.cwd()
    os.chdir(root)
    try:
        scope: dict = {}
        exec(step, scope)  # noqa: S102 - the skill's own fence, run as an agent runs it
        exec(fence("3."), scope)  # noqa: S102
    finally:
        os.chdir(here)

    assert (root / "corpus.json").is_file() and (root / RECORD_FILE).is_file()
