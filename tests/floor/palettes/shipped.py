"""What this framework actually SHIPS: every theme of every stylesheet under `render/assets`.

**What it does.** Reads the shipped stylesheets and returns one `Theme` per look
a reader can see — the base `:root` tokens, and each block that overrides them —
with every colour already read as its three measures, and with each gradient
kept as its own group of stops.

**How you use it.** `themes(root)` for the population, `stylesheets(root)` for
the files it was read from, and `blocks(text)` for one stylesheet's innermost
rule blocks.

**Depends on.** `tests.floor.config` for reading a file and naming it
relative to the root, `tests.floor.palettes.colours` for the measures, and
`re`, `dataclasses` and `pathlib`.

## ⛔ WHY A THEME AND NOT A FILE

⚠️ **A rejected identity is a LOOK, and a look is a theme.** Light and dark are
read apart, each over the tokens it actually defines layered on the base, so a
warm ground in one theme and a terracotta accent in the other are never read as
one palette — nobody sees that pair.

⛔ **One look is read once.** A block that redeclares what the base already says
— a `:root` inside an `@media`, say — resolves to the same theme and is dropped,
because naming it twice would report one identity as two.

## ⚠️ A GRADIENT IS A GROUP, NOT A POOL

⛔ **Two stops in two different gradients are not a gradient between them.** So
each gradient's stops are kept together, `var()` resolved against the theme
being read, and a row written over gradient stops has to meet inside ONE of
them. ⭐ A stylesheet that declares no colour token is a PAINTING one: its
gradients belong to every theme, because that is how they are served.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tests.floor import config
from tests.floor.palettes.colours import Colour, colour

#: Where the framework's own stylesheets are. ⚠️ A per-corpus theme (R19) is
#: generated from manifest data and is not here yet; when it is, it arrives as a
#: second population and not as a second rule.
STYLESHEET_DIR = "src/studyforge/render/assets"

_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_BLOCK = re.compile(r"([^{}]*)\{([^{}]*)\}", re.DOTALL)
_DECLARATION = re.compile(r"--([a-z0-9-]+)\s*:\s*([^;]+)", re.IGNORECASE)
_GRADIENT = re.compile(r"(?:linear|radial)-gradient\(", re.IGNORECASE)

#: One stop of a gradient: a colour written out, or a token it paints with.
_STOP = re.compile(
    r"#(?:[0-9a-f]{3}|[0-9a-f]{6})\b|rgba?\([^)]*\)|var\(\s*--[a-z0-9-]+", re.IGNORECASE
)


@dataclass(frozen=True)
class Theme:
    """One shipped theme: where it is declared, the colour it gives each token, its gradients."""

    stylesheet: str
    label: str
    line: int
    tokens: dict[str, Colour]
    gradients: tuple[tuple[Colour, ...], ...]

    def groups(self, role: str, carried: dict[str, tuple[str, ...]]) -> list[tuple[Colour, ...]]:
        """Return the groups this theme offers `role`: one per gradient, or one for its tokens."""
        if not carried.get(role):
            return list(self.gradients) if role in carried else []
        found = tuple(
            self.tokens[token.lstrip("-")]
            for token in carried[role]
            if token.lstrip("-") in self.tokens
        )
        return [found] if found else []


def blocks(text: str) -> list[tuple[str, str, int]]:
    """Every innermost `selector { … }` of a stylesheet, as `(selector, body, line)`.

    ⭐ Innermost by construction: the pattern forbids a brace inside the body, so
    an `@media` wrapper contributes its inner block and nothing else.
    """
    stripped = _COMMENT.sub(lambda hit: "\n" * hit.group().count("\n"), text)
    found: list[tuple[str, str, int]] = []
    for hit in _BLOCK.finditer(stripped):
        selector = " ".join(hit.group(1).split()).rpartition("}")[2].strip()
        line = stripped[: hit.end(1)].count("\n") + 1
        found.append((selector, hit.group(2), line))
    return found


def gradients(body: str, tokens: dict[str, Colour]) -> tuple[tuple[Colour, ...], ...]:
    """Every gradient in `body` as its own group of colours, `var()` resolved against `tokens`."""
    found: list[tuple[Colour, ...]] = []
    for hit in _GRADIENT.finditer(body):
        depth, at = 1, hit.end()
        while at < len(body) and depth:
            depth += (body[at] == "(") - (body[at] == ")")
            at += 1
        inside = body[hit.end() : at - 1]
        group: list[Colour] = []
        for stop in _STOP.findall(inside):
            read = tokens.get(stop[stop.index("--") + 2 :]) if "--" in stop else colour(stop)
            if read is not None:
                group.append(read)
        if group:
            found.append(tuple(group))
    return tuple(found)


def stylesheets(root: Path) -> list[Path]:
    """Every stylesheet this framework ships, in a fixed order."""
    return sorted((root / STYLESHEET_DIR).glob("*.css"))


def themes(root: Path) -> list[Theme]:
    """Every theme the shipped stylesheets declare — the base, and each block overriding it."""
    read: list[tuple[str, str, int, dict[str, Colour], str]] = []
    base: dict[str, Colour] = {}
    for path in stylesheets(root):
        text = config.read_text(path)
        if text is None:
            continue
        name = config.relative(path, root)
        for selector, body, line in blocks(text):
            tokens = {
                token: found
                for token, value in _DECLARATION.findall(body)
                if (found := colour(value)) is not None
            }
            read.append((name, selector, line, tokens, body))
            if selector == ":root":
                base.update(tokens)
    painted = [body for _name, _selector, _line, tokens, body in read if not tokens]
    found: list[Theme] = []
    seen: set[tuple[tuple[str, Colour], ...]] = set()
    for name, selector, line, tokens, body in read:
        if not tokens:
            continue
        layered = base | tokens
        key = tuple(sorted(layered.items()))
        if key in seen:
            continue
        seen.add(key)
        painting = gradients(body, layered)
        for elsewhere in painted:
            painting += gradients(elsewhere, layered)
        found.append(Theme(name, selector, line, layered, painting))
    return found


__all__ = ["STYLESHEET_DIR", "Theme", "blocks", "gradients", "stylesheets", "themes"]
