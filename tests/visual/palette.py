"""Which palette tokens are colours, and which of them a page can actually show.

**What it does.** Reads `render/assets/palette.css` for its custom properties,
separates the colours from the measures and the font stacks, and holds the
**ledger** that says, for every colour token, how the harness covers it.

**How you use it.** `colour_tokens()` is the list every theme check walks.
`LEDGER` says what covers each one; `test_contrast.py` asserts the ledger is
total over the stylesheet, so a token added tomorrow fails here rather than
quietly leaving the check.

**Depends on.** `re`, `pathlib`, and `studyforge.render.pageassets.ASSET_DIR`
for where the stylesheet lives. ⛔ It reads the file; it does not import a list
of token names from anywhere, because a list retyped here is a list that agrees
with itself and not with the stylesheet.

## ⛔ Why there is a ledger at all

⚠️ *"Contrast for every palette token in both themes"* is not one check, because
the tokens do not all have the same job. `--fg` is text and has a ratio; `--rule`
is a hairline and has no text on it; `--hl-bg` belongs to a narration highlight
that **does not exist until M3**. ⛔ Left implicit, a check that walks "every
token" quietly covers the third of them it can reach and reports success for all
of them — which is the shape of defect this whole task exists to catch.

⭐ **So every token names its own coverage, the ledger is asserted total, and a
token that nothing can reach yet says so with the milestone that will reach it.**
"""

from __future__ import annotations

import re
from pathlib import Path

from studyforge.render.pageassets import ASSET_DIR

#: The stylesheet that defines every token. One file, by `SF-11`'s design.
PALETTE = Path(ASSET_DIR) / "palette.css"

#: How a token is covered. ⛔ Four values and no fifth: a token that fits none
#: of them is a token whose coverage nobody decided.
MEASURED = "measured"  # text is painted with it; it has a ratio and a ground
SURFACE = "surface"  # it is a ground others are measured against
STRUCTURAL = "structural"  # painted, but never as text — a rule, a focus ring
UNPAINTED = "unpainted"  # ⛔ NO stylesheet references it: nothing can measure it

#: ⚠️ Not anchored to the start of a line: `palette.css` wraps the font stacks
#: over two lines and a comment can sit ahead of a declaration, so an anchored
#: pattern reads the file correctly only by luck. `[^;{}]` is what ends a value.
_DECLARATION = re.compile(r"(--[a-z0-9-]+)\s*:\s*([^;{}]+)[;}]")
_COLOUR = re.compile(r"^(#[0-9a-f]{3,8}|rgba?\(|hsla?\(|color\()", re.IGNORECASE)

#: ⛔ Every colour token: how it is covered, the ground its ratio is taken
#: against, and why. The keys are asserted equal to what `colour_tokens()`
#: finds, in **both** directions, so this table cannot drift from the file.
#:
#: ⚠️ **The `UNPAINTED` rows are the honest half, and they are derived rather
#: than believed**: `unpainted()` greps every stylesheet for `var(--token)`, and
#: `test_contrast_math` asserts the two sets are equal. ⛔ So a token that gains
#: its first use in CSS fails **here**, and somebody has to say what ground it
#: sits on — which is the moment a contrast question exists to ask.
#:
#: ⭐ The ground is a token and not a colour. It is what makes the ratio for
#: `--tok-number` computable on a page whose fixture happens to contain no
#: numeric literal — measured through the browser's own resolution of both
#: tokens, never from a number typed here.
LEDGER: dict[str, tuple[str, str | None, str]] = {
    "--bg": (SURFACE, None, "the page ground; every prose ratio is taken against it"),
    "--surface": (SURFACE, None, "raised panels — the disclosure, the code caption bar"),
    "--surface-2": (UNPAINTED, None, "defined, and no stylesheet paints with it — QA-03/2"),
    "--fg": (MEASURED, "--bg", "body text, headings, list items"),
    "--fg-soft": (MEASURED, "--bg", "quotes and secondary prose"),
    "--muted": (MEASURED, "--surface", "the code caption and the copy button"),
    "--rule": (STRUCTURAL, None, "a hairline border; no text sits on it"),
    "--rule-strong": (STRUCTURAL, None, "a heavier hairline; no text sits on it"),
    "--accent": (MEASURED, "--bg", "links, including every entry in the outline"),
    "--accent-soft": (UNPAINTED, None, "defined, and no stylesheet paints with it — QA-03/2"),
    "--practice": (UNPAINTED, None, "defined, and no stylesheet paints with it — QA-03/2"),
    "--practice-soft": (UNPAINTED, None, "defined, and no stylesheet paints with it — QA-03/2"),
    "--code-bg": (SURFACE, None, "the ground every syntax colour is measured against"),
    "--code-fg": (MEASURED, "--code-bg", "code text no highlighter claimed"),
    "--tok-comment": (MEASURED, "--code-bg", "a Prism token class inside a code block"),
    "--tok-string": (MEASURED, "--code-bg", "a Prism token class inside a code block"),
    "--tok-keyword": (MEASURED, "--code-bg", "a Prism token class inside a code block"),
    "--tok-number": (MEASURED, "--code-bg", "a Prism token class inside a code block"),
    "--tok-type": (MEASURED, "--code-bg", "a Prism token class inside a code block"),
    "--tok-function": (MEASURED, "--code-bg", "a Prism token class inside a code block"),
    "--tok-punct": (MEASURED, "--code-bg", "a Prism token class inside a code block"),
    "--hl-bg": (UNPAINTED, None, "the narration highlight; SF-18 paints it at M3"),
    "--hl-bar": (UNPAINTED, None, "the narration progress bar; SF-18, M3"),
    "--hl-fg": (UNPAINTED, None, "text inside the narration highlight; SF-18, M3"),
    "--hl-code": (UNPAINTED, None, "the highlight's wash over code; SF-18, M3"),
    "--panel": (UNPAINTED, None, "the player region; SF-18 paints it at M3 (SF-12/3)"),
    "--focus": (STRUCTURAL, None, "the focus ring; `test_keyboard` asserts it is visible"),
}


def unpainted(directory: Path | None = None) -> tuple[str, ...]:
    """Colour tokens no stylesheet in the asset directory paints with.

    ⛔ Derived by reading the stylesheets, never listed. A token nothing paints
    with cannot be contrast-checked and cannot be *wrong* in a way any reader
    sees — so it is not a gap in this harness, it is a finding about the
    palette, and the ledger is where the two are told apart.
    """
    root = Path(ASSET_DIR) if directory is None else directory
    used = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(root.glob("*.css")) if path != PALETTE
    )
    return tuple(token for token in colour_tokens() if f"var({token})" not in used)


def declarations(text: str | None = None) -> dict[str, list[str]]:
    """Every custom property in the stylesheet, mapped to the values declared for it.

    ⭐ A list per token, because a token declared twice is a token declared once
    per theme — which is the shape the check for *"defined in both"* needs and
    the shape a `dict[str, str]` would throw away.
    """
    source = PALETTE.read_text(encoding="utf-8") if text is None else text
    found: dict[str, list[str]] = {}
    for name, value in _DECLARATION.findall(source):
        found.setdefault(name, []).append(" ".join(value.split()))
    return found


def colour_tokens(text: str | None = None) -> tuple[str, ...]:
    """The tokens whose declared value is a colour, in the order the file declares them.

    ⛔ Decided from the value, never from the name. `--focus` is a colour and
    `--font-mono` is not, and a rule that read the prefix would have to be kept
    in step with whatever the next token is called.
    """
    return tuple(
        name
        for name, values in declarations(text).items()
        if any(_COLOUR.match(value) for value in values)
    )


def defined_in_both(text: str | None = None) -> dict[str, int]:
    """How many times each colour token is declared — one means one theme only."""
    found = declarations(text)
    return {name: len(found[name]) for name in colour_tokens(text)}
