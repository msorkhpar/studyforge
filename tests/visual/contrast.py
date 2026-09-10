"""WCAG contrast, computed from what the browser said the colours were.

**What it does.** Parses a CSS `rgb()`/`rgba()` string, composites a translucent
colour over its backdrop, and returns the WCAG 2.1 contrast ratio between two
colours and the threshold a given piece of text has to clear.

**How you use it.** `ratio(parse(fg), parse(bg))`, and `threshold(size, weight)`
for what that ratio has to beat.

**Depends on.** `re` only. ⛔ Deliberately no browser: this is the one part of
the harness that is pure arithmetic, so it is the one part that **runs in the
pinned image** — every other clause here is unpinned for want of a browser, and
a package where nothing at all could run in the image would be a package a
reader stops looking at.

⚠️ **The numbers are the specification's, not a library's.** sRGB channels are
linearised with the 0.04045 / 12.92 / 2.4 curve and weighted 0.2126 / 0.7152 /
0.0722; the ratio is `(L1 + 0.05) / (L2 + 0.05)`. They are written out because a
constant nobody can check against the spec is a constant that gets tuned until
the test passes.
"""

from __future__ import annotations

import re

#: WCAG 2.1 AA, normal text.
AA_NORMAL = 4.5

#: WCAG 2.1 AA, large text — 24px, or 18.66px when bold.
AA_LARGE = 3.0

#: The pixel size at which text counts as large, and the smaller size that also
#: counts once the weight reaches `BOLD`.
LARGE_PX = 24.0
LARGE_BOLD_PX = 18.66
BOLD = 700

_RGB = re.compile(
    r"rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)(?:\s*[,/]\s*([\d.%]+))?\s*\)",
    re.IGNORECASE,
)


class ColourError(ValueError):
    """A colour string the browser produced that this module cannot read."""


def parse(value: str) -> tuple[float, float, float, float]:
    """Read `rgb(r, g, b)` or `rgba(r, g, b, a)` into channels plus alpha.

    ⛔ Raises on anything else, including `transparent` and the empty string.
    Returning a default would turn *"this token does not resolve"* — the exact
    failure `palette.css` says is invisible to whoever authored it — into a
    silent pass against black.
    """
    match = _RGB.search(value or "")
    if match is None:
        raise ColourError(f"not a colour this harness can read: {value!r}")
    red, green, blue = (float(match.group(index)) for index in (1, 2, 3))
    raw_alpha = match.group(4)
    if raw_alpha is None:
        alpha = 1.0
    elif raw_alpha.endswith("%"):
        alpha = float(raw_alpha[:-1]) / 100.0
    else:
        alpha = float(raw_alpha)
    return red, green, blue, alpha


def over(colour: tuple[float, float, float, float], backdrop: tuple[float, float, float, float]):
    """Composite a possibly translucent `colour` over an opaque `backdrop`.

    ⚠️ Needed because `--hl-code` and the shadows are `rgba`, and a ratio taken
    against an alpha channel the maths ignored is a number about a colour
    nobody sees.
    """
    alpha = colour[3]
    return tuple(colour[index] * alpha + backdrop[index] * (1 - alpha) for index in range(3)) + (
        1.0,
    )


def luminance(colour: tuple[float, float, float, float]) -> float:
    """Relative luminance of an opaque sRGB colour, per WCAG 2.1."""
    channels = []
    for raw in colour[:3]:
        component = raw / 255.0
        channels.append(
            component / 12.92 if component <= 0.04045 else ((component + 0.055) / 1.055) ** 2.4
        )
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def ratio(foreground: tuple[float, ...], background: tuple[float, ...]) -> float:
    """The WCAG contrast ratio between two colours, foreground composited if needed."""
    background = tuple(background[:3]) + (1.0,)
    if len(foreground) == 4 and foreground[3] < 1.0:
        foreground = over(foreground, background)  # type: ignore[arg-type]
    lighter, darker = sorted(
        (luminance(foreground), luminance(background)),  # type: ignore[arg-type]
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def threshold(size_px: float, weight: int) -> float:
    """What ratio text of this size and weight has to clear for AA."""
    if size_px >= LARGE_PX or (weight >= BOLD and size_px >= LARGE_BOLD_PX):
        return AA_LARGE
    return AA_NORMAL
