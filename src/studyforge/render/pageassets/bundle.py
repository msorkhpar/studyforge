"""What goes into a page's stylesheet and script, in what order, under what name.

**What it does.** Composes the parts into the two files every page links, and
fixes the order — which for CSS is meaning, not tidiness.

**How you use it.** `stylesheet()` and `script()` return text;
`STYLESHEET_NAME` and `SCRIPT_NAME` are what to write it as.

**Depends on.** `source`. Nothing here touches a page or a corpus.

## Why the order is stated and not sorted

⛔ **Two rules of equal specificity: the last one wins.** So the sequence below
*is* part of the design, and `source.names()` — which sorts — must never be
used to build a bundle. Reset before palette before anything that paints;
`code-highlight` after `reading`, because it refines what `reading` sets on the
same elements.

⛔ **And it must not depend on directory order** (R10): two machines
enumerating `assets/` can disagree, and a page that differs between them is a
page that cannot be compared byte for byte.

## The name carries no digest

⛔ **`page.css`, not `page.8f3a21.css`.** A content digest in the name means a
new filename, and a rewrite of *every page that links it*, every time a colour
changes — at a thousand units that is a thousand-file diff for one hex value.
The cost of the plain name is a browser holding a stale copy until reload,
which on a local study site is free (§8.2). ⚠️ This is the opposite of the rule
for a **narration clip**, whose filename carries a digest precisely because a
stale clip is a wrong voice reading current text; the difference is that
nothing links a clip by a name a thousand pages repeat.

⭐ **The sprite has exactly one source on disk.** `video-player.js` carries a
placeholder that is filled from the vendored `plyr.svg` when the script is
composed, so no derived copy of the sprite is committed beside it.
"""

from __future__ import annotations

from studyforge.render.pageassets import faces
from studyforge.render.pageassets.source import text

#: The stylesheet, weakest first. ⚠️ Vendored `plyr.css` comes after the
#: authored parts so a player control takes its own look rather than the
#: reading column's, and `video-player.css` comes after *it* — that is the
#: standing rule for a view that needs something different: theme the vendored
#: stylesheet from outside, never fork it, so re-vendoring does not strand the
#: change.
#:
#: ⛔ `chrome.css` sits after `reading.css` and before `code-highlight.css`, and
#: both halves of that are meaning. It comes *after* the reading surface because
#: it refines what `reading.css` sets on `body` and on `body`'s children — the
#: page column (`PO-22/6`) is exactly that refinement, and at equal specificity
#: the last rule wins. It comes *before* the highlight part because the
#: highlight refines the inside of a code block, which no chrome rule reaches.
#:
#: ⭐ `lists.css`, `onward.css` and `notes.css` follow `chrome.css` directly:
#: the four are one part split at named seams for R11 (`W362`; `chrome.css`
#: names them), and they share its position's argument.
#:
#: ⭐ `practice.css` (`SF-24`) follows those four directly and for their reason:
#: the practice panel is a region this framework emits, reached by an attribute
#: and painted in palette tokens, so it belongs with the other authored region
#: parts and before anything that refines the inside of a code block. ⛔ It comes
#: after `notes.css` because the panel sits under a section the reading surface
#: has already set, and at equal specificity the last rule wins.
#:
#: ⭐ `practice-quiz.css` (`AX-09`) follows `practice.css` directly and for that
#: part's own reason: the two are one region split at a named seam for R11 — the
#: panel and the run on one side, the questions on the other — and a quiz wears
#: `data-practice-quiz` rather than `data-practice`, so neither file's rules can
#: reach the other's element and the order between them settles nothing but
#: where a reader of the bundle finds them.
#:
#: ⛔ `narration.css` sits after `code-highlight.css` and before the vendored
#: parts, and both halves of that are meaning too. It comes *after* the
#: highlight because the narration highlight washes over the inside of a code
#: block the highlighter has just painted, and at equal specificity the last
#: rule wins. It comes *before* `plyr.css` because the rule stated above is
#: unchanged: nothing authored may follow the vendored player theme, or a video
#: control stops taking its own look.
STYLE_PARTS = (
    "reset.css",
    "palette.css",
    "focus.css",
    "reading.css",
    "chrome.css",
    "lists.css",
    "onward.css",
    "notes.css",
    "practice.css",
    "practice-quiz.css",
    "code-highlight.css",
    "narration.css",
    "plyr.css",
    "video-player.css",
)

#: The script. ⛔ A library before the code that calls it: `video-player.js`
#: returns immediately when `Plyr` is undefined, so the order is what makes it
#: run at all.
#:
#: ⛔ **`study-progress.js` DEFINES the reader's store and `read-mark.js` is the
#: only thing that uses it, so the first must precede the second — and that is
#: not a tidiness argument.** The extraction source placed its store *after* the
#: page script that read it at startup: the guard skipped, the setting silently
#: never came back, the suite stayed green, and it was found only by loading a
#: page in a browser. ⭐ `read-mark.js` therefore reads the store through its
#: published name with **no existence guard**, so a wrong order fails loudly
#: instead of shipping a feature that is quietly absent — and it is **LAST**, so
#: a throw of its own reaches no other part.
#:
#: ⭐ `progress-view.js` (`W362`) reads the store too, so it follows
#: `study-progress.js`; it sits before `read-mark.js` because that part's
#: LAST-ness is the property being kept.
#:
#: ⭐ `narration.js` needs no library and defines nothing anybody else reads, so
#: its position is not load-bearing the way the two above are — but it is stated
#: rather than left to the alphabet like every other entry here. It sits before
#: `read-mark.js` because that part's LAST-ness is the property being kept, and
#: after `video-player.js` so the two media parts read together.
#:
#: ⭐ `practice.js` (`SF-24`) needs no library and no store: it draws the panel
#: and reaches the API only through `window.studyforge.run`, which the SERVING
#: PROCESS adds to the page it answers — so a built page names no client and no
#: origin (R8, `W370`). ⛔ It is before `read-mark.js` because that part's
#: LAST-ness is the property being kept, and after `narration.js` so the parts
#: that draw a region of their own read together.
#:
#: ⭐ `practice-editor.js` and `practice-quiz.js` (`AX-09`) follow `practice.js`
#: for the same reason `practice-quiz.css` follows `practice.css`: they are that
#: part split at named seams for R11 — the panel and the run, the two editor
#: windows, and the quiz. ⛔ **The order between the three settles nothing**, and
#: that is a property rather than luck: each one selects its own elements, none
#: defines anything another reads. ⚠️ `practice-quiz.js` asks
#: `window.studyforge.quiz` — not `.run` — whether an origin exists, because
#: since the user's ruling of 2026-09-23 the local study server grades a quiz and
#: the page holds no key (spec §7 §7, amended 2026-09-23). ⚠️ They are before
#: `read-mark.js` because that part's LAST-ness is the property being kept.
#:
#: ⭐ `theme.js` (`W388` stage 2) reads and writes the store's DISPLAY record,
#: so it follows `study-progress.js` for the same reason `progress-view.js`
#: does; it sits before `read-mark.js` because that part's LAST-ness is the
#: property being kept. ⚠️ It is not what stops the page flashing the wrong
#: theme — a deferred part cannot be — and `page.html`'s head boot is.
SCRIPT_PARTS = (
    "prism.js",
    "plyr.js",
    "study-progress.js",
    "theme.js",
    "copy-code.js",
    "video-player.js",
    "narration.js",
    "practice.js",
    "practice-editor.js",
    "practice-quiz.js",
    "progress-view.js",
    "read-mark.js",
)

#: ⛔ Plain names, no content digest. See this module's docstring.
STYLESHEET_NAME = "page.css"
SCRIPT_NAME = "page.js"

#: The placeholder `video-player.js` carries, and the part that fills it.
SPRITE_PLACEHOLDER = "__PLYR_SPRITE__"
SPRITE_PART = "plyr.svg"

#: What separates two parts in a bundle. A newline, so a part ending in a
#: line comment cannot swallow the first line of the next one.
JOIN = "\n"


def stylesheet() -> str:
    """Return the whole page stylesheet: the embedded faces, then `STYLE_PARTS` in order.

    ⭐ The faces come first because an `@font-face` rule is order-free and the
    parts after it are not; putting the one block that cannot conflict ahead of
    everything keeps "the order is meaning" true of the parts alone (`W362`).
    """
    return faces.rules() + JOIN + compose(STYLE_PARTS)


def script() -> str:
    """Return the whole page script, with the icon sprite substituted in.

    ⛔ Substituted here rather than fetched: Plyr would otherwise pull its
    sprite from a CDN on every init, and the floor is a page opened from a
    file with no network at all (R8).
    """
    sprite = text(SPRITE_PART).strip().replace("\n", "")
    composed = compose(SCRIPT_PARTS)
    if SPRITE_PLACEHOLDER not in composed:
        return composed
    return composed.replace(f"'{SPRITE_PLACEHOLDER}'", sprite_literal(sprite))


def compose(parts: tuple[str, ...]) -> str:
    """Join the named parts in the given order, exactly as they are on disk."""
    return JOIN.join(text(name) for name in parts)


def sprite_literal(sprite: str) -> str:
    r"""Return the sprite as a single-quoted JavaScript string literal.

    ⚠️ Backslashes first, then quotes. The other order escapes the backslash
    this function just added, turning one escaped quote into a literal
    backslash followed by an unescaped one — which ends the string early and
    leaves the rest of the sprite as broken syntax on every page.
    """
    escaped = sprite.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def written_files() -> dict[str, str]:
    """`filename -> content` for everything a build writes beside a page.

    ⭐ One function, so a renderer never assembles the pair itself and the two
    names can never drift apart from the two bodies.
    """
    return {STYLESHEET_NAME: stylesheet(), SCRIPT_NAME: script()}
