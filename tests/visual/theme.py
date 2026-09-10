"""What the browser says the colours on an open page actually are.

**What it does.** Two readings, both taken by the browser and neither computed
here: `resolve()` asks what every palette token evaluates to under the current
theme, and `text_elements()` walks the rendered document for everything that
paints text, with its colour, its effective background, its size and its weight.

**How you use it.** `resolve(page)` and `text_elements(page)`, on a page that is
already open under a chosen scheme.

**Depends on.** `page.OpenPage` and `palette`. ⛔ No colour arithmetic —
`contrast.py` owns that, and keeping the reading apart from the sum is what
lets the sum be tested in the pinned image.

## ⚠️ The effective background is walked, not read

`getComputedStyle(el).backgroundColor` on a paragraph is `rgba(0, 0, 0, 0)` —
transparent — because the ground belongs to an ancestor. A ratio taken against
that transparent value is a ratio against black, which passes for light text and
fails for dark, and in both cases describes nothing. So the walk climbs until it
finds a colour that is actually painted.
"""

from __future__ import annotations

import json

from tests.visual.page import OpenPage
from tests.visual.palette import colour_tokens

#: Resolve every token by setting it on a probe and reading the result back.
#: ⭐ Through `color`, because that is the property whose computed value the
#: browser reports as an `rgb()` string — the same form `text_elements` returns,
#: so the two readings are directly comparable without a second parser.
_RESOLVE = """
(() => {
  const probe = document.createElement('span');
  probe.setAttribute('style', 'position:absolute;left:-9999px;top:-9999px');
  document.body.appendChild(probe);
  const out = {};
  for (const token of %s) {
    probe.style.color = 'rgb(1, 2, 3)';
    probe.style.color = 'var(' + token + ')';
    const seen = getComputedStyle(probe).color;
    out[token] = seen === 'rgb(1, 2, 3)' ? null : seen;
  }
  probe.remove();
  return out;
})()
"""

_ELEMENTS = """
(() => {
  const ground = (el) => {
    let node = el;
    while (node) {
      const paint = getComputedStyle(node).backgroundColor;
      if (paint && paint !== 'transparent' && !/^rgba\\(0, 0, 0, 0\\)$/.test(paint)) return paint;
      node = node.parentElement;
    }
    return getComputedStyle(document.documentElement).backgroundColor;
  };
  const out = [];
  for (const el of document.querySelectorAll('body *')) {
    const own = Array.from(el.childNodes)
      .filter((n) => n.nodeType === 3 && n.textContent.trim());
    if (!own.length) continue;
    const style = getComputedStyle(el);
    if (style.visibility === 'hidden' || style.display === 'none') continue;
    if (style.opacity === '0') continue;
    out.push({
      tag: el.tagName,
      cls: String(el.className || ''),
      colour: style.color,
      ground: ground(el),
      size: parseFloat(style.fontSize),
      weight: parseInt(style.fontWeight, 10) || 400,
      text: own.map((n) => n.textContent.trim()).join(' ').slice(0, 48)
    });
  }
  return out;
})()
"""


def resolve(page: OpenPage) -> dict[str, str]:
    """`token -> the colour string this theme resolves it to`.

    ⛔ A token that does not resolve comes back as `None` and is *kept*, not
    dropped: the caller has to decide, and a reading that silently omitted it
    would report full coverage of a palette with a hole in it.
    """
    reading = page.evaluate(_RESOLVE % json.dumps(list(colour_tokens())))
    return dict(reading)  # type: ignore[arg-type]


def text_elements(page: OpenPage) -> list[dict]:
    """Every visible element painting its own text, with the colours it paints in."""
    return list(page.evaluate(_ELEMENTS))  # type: ignore[arg-type]


def tokens_by_colour(resolved: dict[str, str]) -> dict[str, set[str]]:
    """Invert `resolve()`, keeping every token that shares a value.

    ⚠️ A `dict[colour, token]` would be wrong and would look right. `--accent`
    and `--focus` are the *same colour* in both themes, so an inversion that
    kept one would report the other as never painted — and the fix somebody
    then made would be to delete a check.
    """
    grouped: dict[str, set[str]] = {}
    for token, colour in resolved.items():
        if colour is not None:
            grouped.setdefault(colour, set()).add(token)
    return grouped
