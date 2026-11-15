"""The from-scratch guide and its sample brief agree with the intake skill.

Mirrors no source module: it holds `docs/authoring/from-scratch.md` to the fixture it shows,
`tests/fixtures/intake/data-analyst/brief.json`. The sample passes the checker, the brief the
guide embeds is that sample's rendering byte for byte, and every step of the walk names the
skill that owns it.
"""

from __future__ import annotations

import re

from studyforge.skills.intake.brief import load
from studyforge.skills.intake.check import check
from studyforge.skills.intake.render import render
from tests.support import repository_root

GUIDE = "docs/authoring/from-scratch.md"
FIXTURE = "tests/fixtures/intake/data-analyst/brief.json"
BEGIN, END = "<!-- brief:begin -->", "<!-- brief:end -->"
#: The fence the guide wraps the rendering in, so the brief reads as a file, not as headings.
OPEN_FENCE, CLOSE_FENCE = "```markdown\n", "```\n"
STEP_SKILLS = (
    "intake", "catalogue", "onboarding", "execution", "lessons", "exercises", "buildserve",
    "delivery",
)
_STEP = re.compile(r"^## (\d+)\. .*$", re.MULTILINE)


def _guide() -> str:
    return (repository_root() / GUIDE).read_text(encoding="utf-8")


def _embedded(text: str) -> str:
    start, end = text.index(BEGIN) + len(BEGIN), text.index(END)
    block = text[start:end].strip("\n") + "\n"
    assert block.startswith(OPEN_FENCE) and block.endswith(CLOSE_FENCE), block[:40]
    return block[len(OPEN_FENCE) : -len(CLOSE_FENCE)]


def _step_openings(text: str) -> list[str]:
    """Each numbered step's heading and its first paragraph."""
    openings = []
    for match in _STEP.finditer(text):
        body = text[match.end() :].lstrip("\n")
        openings.append(match.group(0) + "\n" + body.split("\n\n", 1)[0])
    return openings


def test_the_sample_brief_passes_the_checker():
    assert check(load(repository_root() / FIXTURE), private_ignored=True) == []


def test_the_guide_embeds_the_sample_brief_rendering():
    assert _embedded(_guide()) == render(load(repository_root() / FIXTURE))


def test_the_guide_names_every_step_skill():
    openings = _step_openings(_guide())
    assert [int(m.group(1)) for m in _STEP.finditer(_guide())] == list(range(1, 10))
    joined = "\n".join(openings)
    missing = [name for name in STEP_SKILLS if not re.search(rf"\b{name}\b", joined)]
    assert missing == []
