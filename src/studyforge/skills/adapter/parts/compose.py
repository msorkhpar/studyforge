r"""One generated file, and the contract every generated module gets by construction.

**What it does.** Defines `Part` — a file the scaffold emits, the step of
`SKILL.md` that builds it, and whether it is generated — and `module`, which
assembles a generated module's text from R17's three questions plus a summary.

**How you use it.** A renderer builds its body as a list of lines and calls
`module(summary=..., does=..., uses=..., depends=..., body=lines)`.

**Depends on.** `plan`, for the type a renderer is handed. ⛔ Not on `parts`
itself: the renderer modules import this one, and a composer that lived in the
package's `__init__` would be imported by the modules that package imports.

## ⚠️ Why a generated module is composed rather than pasted

⛔ **A contract inside a string literal is a contract no rule reaches.**
`tools.quality` reads this repository's modules; nothing reads a module that
does not exist yet. So the four pieces are keyword-only, all four are checked,
and a generated module that would ship without a `Depends on` line raises here
— in the framework's own suite — rather than being noticed by whoever reviews
the corpus repository, if anybody does.

⚠️ **And the delimiter is a value.** A generated module's docstring uses the
same three characters this file would need to write literally; `DQ` is how the
two never meet.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from studyforge.skills.adapter.plan import Plan

#: A docstring delimiter, as a value rather than as a literal.
DQ = '"""'

#: R17's three questions, in the order a generated contract answers them.
#: ⭐ Named here so the test asserts the shape rather than matching prose.
CONTRACT_PARTS = ("What it does", "How you use it", "Depends on")


@dataclass(frozen=True, slots=True)
class Part:
    """One file a scaffold emits, and the step of the procedure that builds it."""

    where: str
    step: int
    why: str
    generated: bool
    render: Callable[[Plan], str]

    def path_for(self, plan: Plan) -> str:
        """Return this part's path in the corpus repository, with the package name filled in."""
        return self.where.format(package=plan.package)


def module(*, summary: str, does: str, uses: str, depends: str, body: Iterable[str]) -> str:
    """Assemble one generated module: an R17 contract, then the code."""
    for name, piece in (
        ("summary", summary),
        ("does", does),
        ("uses", uses),
        ("depends", depends),
    ):
        if not isinstance(piece, str) or not piece.strip():
            raise ValueError(f"a generated module needs a {name}; R17 is not optional")
    head = [
        f"{DQ}{summary}",
        "",
        f"**{CONTRACT_PARTS[0]}.** {does}",
        "",
        f"**{CONTRACT_PARTS[1]}.** {uses}",
        "",
        f"**{CONTRACT_PARTS[2]}.** {depends}",
        DQ,
        "",
        "from __future__ import annotations",
        "",
    ]
    return "\n".join([*head, *body, ""])
