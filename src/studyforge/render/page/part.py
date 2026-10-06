"""One section of a unit page and, where it sets work, the panel the reader acts in.

**What it does.** Renders a section and the panel that follows it: the section's own blocks
(`page.section`), then, for a practice, the panel (`page.practice`) tagged with the language it is
written in when the reading modes ask for one.

**How you use it.** `page.document` calls `part.render(section, placement, narration, document,
heads_page=...)` once per section and joins the answers.

**Depends on.** `page.section`, `page.practice`, `page.editions` and `render.modes`.

## ⛔ The panel sits AFTER the section rather than inside it

It is the shape `section`'s own attachments region already has: the statement, the hint and the
starting code are the material's blocks and belong to the material; the editor slot, Run, Submit
and the result are this framework's controls and belong beside it. ⭐ Keeping it outside
`<section>` also keeps it out of the outline, exactly as the narrated deck above the section is.

⚠️ **Joined here rather than given a slot of its own**, because a unit may carry SEVERAL practices
and a slot is one region per page: a panel has to follow the practice it is about, or a reader
reads two statements and then two sets of controls with nothing saying which is which.

## ⭐ A language edition is tagged as an edition, not as a language

A practice written in several languages is one practice (`page.editions`): its statement and its
panel carry `data-edition` and never `data-lang`, so no reading mode hides one and the workspace
shows the one the reader chose. Every other practice is tagged as it always was.
"""

from __future__ import annotations

from studyforge.render import modes
from studyforge.render.page import editions, practice
from studyforge.render.page import section as section_module
from studyforge.render.page.assets import Placement
from studyforge.render.page.narration import Narration

#: What separates a section from its panel.
JOIN = "\n"


def render(
    section: dict, placement: Placement, narration: Narration, document: dict, *, heads_page: bool
) -> str:
    """Return one section and, where it sets work, the panel that follows it.

    ⚠️ `heads_page` is `section.render`'s own word, passed STRAIGHT through and REQUIRED:
    `page.document` is its only caller and the only holder of the page.
    """
    many = editions.edited_with(document, section) is not None
    rendered = section_module.render(
        section, placement, narration, heads_page=heads_page, edited=many
    )
    panel = practice.render(section, document, placement)
    if not many:
        panel = modes.tag_panel(placement.offer, section.get("lang"), panel)
    return f"{rendered}{JOIN}{panel}" if panel else rendered
