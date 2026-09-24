"""The spec's rejected-palette table, READ over the stylesheets we ship.

**What it does.** Puts the document's side (`rejected`) and the tree's side
(`shipped`) together and answers one question: is any theme this framework ships
an identity the spec's §8.4 table REJECTS? ⛔ **A list nothing reads cannot
stop a repaint that ships the first half of *warm cream + serif display +
terracotta*** — so the table is read, not only written.

⭐ **The spec holds the table, so the check that reads it is the product's.**

**How you use it.** `check_rejected_palettes(root)` is registered in
`tests.floor.CHECKS` and fails the floor once per shipped theme that matches a
rejected row; `palette_census(root)` is registered in `NOTICES` and prints the
denominator on every run. `matched` is the predicate both channels
share.

**Depends on.** `rejected` and `shipped` beside it, `tests.floor.report` for
the answer, and `pathlib`.

## ⛔ WHAT A GREEN RUN HERE DOES NOT SAY

⚠️ **It reads COLOUR and nothing else.** A serif display face, the card kit,
pill tags and an eyebrow label are §2 tells no hue can see. ⭐ So the census says
so in its own line: green here is *no rejected PALETTE is shipped*, and
never *§2 is met*.

## ⛔ THE ROW IS THE UNIT AND THE CONJUNCTION IS THE INSTRUMENT

⭐ **Cool slate is the ACCEPTED identity; slate WITH teal-green AND amber is a
rejected one.** ⛔ A row that fired on one part would refuse the accepted
identity, so every part must hold in ONE theme, and the parts written on one
role must be met inside ONE group of that role — one gradient, or that theme's
colours for a token role.

## ⚠️ THE EXEMPTION MECHANISM IS THE DOCUMENT

⛔ **An identity stops being refused only when its ROW LEAVES THE TABLE**, which
is the same edit as changing the rule. ⭐ There is no allow-list here and no flag:
the instrument and the table cannot come apart.
"""

from __future__ import annotations

from pathlib import Path

from tests.floor.palettes.rejected import (
    CEILING,
    GRADIENT_ROLE,
    ROLE_HEADER,
    SIGNATURE_HEADER,
    UI_CONVENTION,
    Band,
    Part,
    Signature,
    band,
    convention,
    part,
    roles,
    signatures,
    table,
)
from tests.floor.palettes.shipped import (
    STYLESHEET_DIR,
    Theme,
    blocks,
    gradients,
    stylesheets,
    themes,
)
from tests.floor.report import Finding

RULE_PALETTE = "rejected-palette"


def matched(signature: Signature, theme: Theme, carried: dict[str, tuple[str, ...]]) -> bool:
    """Whether every part of `signature` holds in `theme`, per role, inside one group."""
    for role in signature.roles():
        wanted = [one for one in signature.parts if one.role == role]
        groups = theme.groups(role, carried)
        if not any(
            all(any(one.holds(read) for read in group) for one in wanted) for group in groups
        ):
            return False
    return True


def check_rejected_palettes(root: Path) -> list[Finding]:
    """Return one finding per shipped theme that is an identity the convention rejects."""
    carried, rejected = convention(root)
    findings: list[Finding] = []
    for theme in themes(root):
        for signature in rejected:
            if not matched(signature, theme, carried):
                continue
            findings.append(
                Finding(
                    theme.stylesheet,
                    theme.line,
                    RULE_PALETTE,
                    f"the theme {theme.label!r} is the identity "
                    f"{signature.name!r}, which `{UI_CONVENTION}` REJECTS "
                    f"({signature.ground}). Every part of its signature is present here: "
                    f"{'; '.join(one.text for one in signature.parts)}. Change the palette, "
                    f"or take the rejection out of that table with the reason "
                    f"why — never leave the two disagreeing.",
                )
            )
    return findings


def palette_census(root: Path) -> list[str]:
    """Print the denominator on every run: the rows read, the themes read, and what is NOT read."""
    carried, rejected = convention(root)
    read = themes(root)
    shipped = sum(
        1 for theme in read for signature in rejected if matched(signature, theme, carried)
    )
    return [
        f"rejected palettes: {len(rejected)} rejected identities read from {UI_CONVENTION} "
        f"over {len(read)} theme(s) in {len(stylesheets(root))} stylesheet(s) under "
        f"{STYLESHEET_DIR}/, on {len(carried)} role(s); {shipped} shipped. ⚠️ COLOUR only — a "
        f"face, the card kit, a pill tag and an eyebrow label are §2 tells no hue can see, so "
        f"a green line here is never `§2 is met`."
    ]


__all__ = [
    "CEILING",
    "GRADIENT_ROLE",
    "ROLE_HEADER",
    "RULE_PALETTE",
    "SIGNATURE_HEADER",
    "STYLESHEET_DIR",
    "UI_CONVENTION",
    "Band",
    "Part",
    "Signature",
    "Theme",
    "band",
    "blocks",
    "check_rejected_palettes",
    "convention",
    "gradients",
    "matched",
    "palette_census",
    "part",
    "roles",
    "signatures",
    "stylesheets",
    "table",
    "themes",
]
