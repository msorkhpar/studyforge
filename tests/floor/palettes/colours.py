"""One colour, read as the three measures every bound in the UI convention is written in.

**What it does.** Turns a colour a stylesheet writes — `#rgb`, `#rrggbb`,
`rgb(…)` or `rgba(…)` — into a hue, a chroma and a light, which are the measures
the spec's §8.4 rejected-palette table states its bands in.

**How you use it.** `colour(value)` for a value off a stylesheet, `measure(r, g,
b)` for a triple you already have, and `Colour.reading()` for the three numbers
in a finding somebody has to be able to check by hand.

**Depends on.** `dataclasses` and `re` — the standard library, and nothing else.

## ⛔ CHROMA, AND NOT HSL SATURATION

⚠️ **On the accepted paper:** a near-white with a
one-step tint reports an HSL saturation near 40% and a chroma near 3%. ⛔ A bound
written in saturation would refuse that paper on its first run — so chroma here
is `max − min` over 255, where a near-white and a near-black both read near
zero, and the convention's bands are written in it.

⭐ **A grey has no hue and its hue reads `0`.** No band can reach that value by
accident: every hue band in the document carries a chroma bound beside it, which
is the property that makes the zero safe rather than a special case here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_HEX = re.compile(r"#([0-9a-f]{3}|[0-9a-f]{6})\b", re.IGNORECASE)
_RGB = re.compile(r"rgba?\(\s*(\d+)\s*[, ]\s*(\d+)\s*[, ]\s*(\d+)", re.IGNORECASE)


@dataclass(frozen=True)
class Colour:
    """One colour as the three measures every bound in the document is written in."""

    hue: float
    chroma: float
    light: float

    def reading(self) -> str:
        """Return the three measures, rounded, for a finding somebody can check by hand."""
        return f"hue {self.hue:.0f}, chroma {self.chroma:.0f}%, light {self.light:.0f}%"


def measure(red: int, green: int, blue: int) -> Colour:
    """Read one RGB triple as hue, chroma and light."""
    high, low = max(red, green, blue), min(red, green, blue)
    span = high - low
    if span == 0:
        hue = 0.0
    elif high == red:
        hue = 60.0 * (((green - blue) / span) % 6)
    elif high == green:
        hue = 60.0 * (((blue - red) / span) + 2)
    else:
        hue = 60.0 * (((red - green) / span) + 4)
    return Colour(hue, span / 255 * 100, (high + low) / 2 / 255 * 100)


def colour(value: str) -> Colour | None:
    """Return the first colour written in `value`, or None when it writes none."""
    found = _HEX.search(value)
    if found is not None:
        digits = found.group(1)
        if len(digits) == 3:
            digits = "".join(digit * 2 for digit in digits)
        return measure(*(int(digits[at : at + 2], 16) for at in (0, 2, 4)))
    found = _RGB.search(value)
    if found is not None:
        return measure(*(min(255, int(found.group(at))) for at in (1, 2, 3)))
    return None


__all__ = ["Colour", "colour", "measure"]
