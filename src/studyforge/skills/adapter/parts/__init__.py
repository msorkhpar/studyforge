r"""What a scaffolded adapter is made of: one closed list, in the order it is built.

**What it does.** Holds every file the scaffold emits — five modules that are
the adapter and three that test it — as a `Part` each, plus the composer every
generated module's text is assembled by.

**How you use it.** Through `studyforge.skills.adapter.scaffold`, which walks
`PARTS`. Directly, only to ask what a scaffold contains:

    from studyforge.skills.adapter.parts import PARTS

    [part.where for part in PARTS]     # the paths, relative to the corpus root

**Depends on.** `plan` for the facts a part may vary on. ⛔ Nothing else, and
nothing outside this package imports a part renderer: a file that is not in
`PARTS` is a file the procedure in `SKILL.md` does not mention, and that is the
one thing this list exists to make impossible.

## ⭐ The list is data, so it is assertable

⛔ **Every part carries the step of `SKILL.md` that builds it.** A part with no
step is a file the procedure never tells anybody to look at; a step with no
part is a step that produces nothing. The test module asserts both directions,
which is how a file added in a hurry fails rather than accumulates.

## ⛔ Exactly one part is not generated, and it is named

⚠️ **R19: a hand-edit to a generated artifact is a finding, not a fix.** That
rule is unusable unless a reader can tell which files it covers, so `Part`
carries `generated` and exactly one part sets it `False` — the module that
reads the source. ⭐ Everything else is regenerable, and a diff in one is a
defect report about this skill.

## ⚠️ Why the composer sits in its own module

`compose` holds `Part` and `module`; `adapter` and `suite` hold the renderers
and import them. ⛔ Not a tidiness split: with the composer in this file, every
renderer module would import the package that imports it, and the cycle
resolves only because of where the import statement happens to sit.
"""

from __future__ import annotations

from studyforge.skills.adapter.parts.adapter import ADAPTER_PARTS
from studyforge.skills.adapter.parts.compose import DQ, Part, module
from studyforge.skills.adapter.parts.suite import SUITE_PARTS

#: Every file a scaffold emits, in the order `SKILL.md` builds them. ⛔ The
#: adapter first and its tests second, because the tests name the modules and a
#: test for a module nobody has seen is a test nobody reads.
PARTS: tuple[Part, ...] = (*ADAPTER_PARTS, *SUITE_PARTS)

__all__ = ["ADAPTER_PARTS", "DQ", "PARTS", "SUITE_PARTS", "Part", "module"]
