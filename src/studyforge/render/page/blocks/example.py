"""One example with a tab per language: the block, drawn as WAI-ARIA tabs under a visible label.

**What it does.** Renders the archive's `example` block, a run of code fences cut into a
tab per language, as one block: a tab bar, one panel per language, and a flag for an
example whose point is a compiler message.

**How you use it.** The dispatcher answers for the `example` type with `render`, and
reaches it with the placement, which may carry the corpus's reading `offer`.

**Depends on.** `archive.blocks`, `templates`, `markup`, and the dispatcher's own
`render_one` for each fence. ⛔ It names no language (R1): a tab's id and label are the
corpus's data, taken from the offer.

## ⭐ What the markup says, and what the script and the stylesheet add

- **Every panel is present, each under a visible language label, in the default
  mode's tab order.** With scripts off, in a crawl and in the preview, the page is that
  and nothing needs a script. The tab bar ships `hidden`.
- **`modes.css` hides by the mode** (`html[data-mode]`): a language the mode does not
  list loses its tab and panel, and an example with nothing in a listed language is
  hidden whole. The script (`example-tabs.js`) then shows the bar, opens the first tab
  of the mode, and keeps the arrow keys. A click changes this block only and is
  not remembered.
- **A corpus that greys what a language lacks** (`absent_language: grey`) also gets, for each
  declared language the block has no tab for, a disabled tab and one sentence naming the
  languages that do carry it, built from the corpus's own declaration.
- **The tab bar, the stylesheet and the script exist only for a corpus that declares
  modes**, so an example of a corpus with none is its panels under labels and nothing
  else: no bar is emitted.

## ⛔ Not narrated, and no class

A fence yields no speech and the labels are shown, not spoken, so no audio attribute is
written. The hooks are `data-*` attributes of this module's own, so the shared surface
class set is unchanged.
"""

from __future__ import annotations

from studyforge.render import modes, templates
from studyforge.render.markup import escape, escape_attribute

#: The block types this module answers for.
RENDERS = ("example",)

#: What a flagged output says is the point of the block, by output name (R13: the words
#: are the templates'). ⛔ An output the archive's vocabulary admits and this lacks is drawn
#: unflagged, and `validate` refuses one outside the vocabulary.
FLAGS = {"compiler": "example-flag-compiler.html", "warning": "example-flag-warning.html"}


def render(
    block: dict,
    position: int,
    *,
    placement: object = None,
    section: str = "",
    children: str = "",
    path: tuple[int, ...] = (),
    narration: object = None,
) -> str:
    """Return the example as one block with a tab for each language it has.

    ⛔ `children` is not used: the fences are drawn here, one by one, so each lands in the
    panel of its own language, and each is drawn at the address it has in the block.
    """
    del children, narration
    from studyforge.render.page.blocks import render_one  # the dispatcher imports this module

    offer = getattr(placement, "offer", None)
    labels = dict(getattr(offer, "languages", ()) or ())
    tabs = _in_mode_order(block.get("tabs") or [], offer)
    fences = block.get("blocks") or []
    spans, start = {}, 0
    for tab in block.get("tabs") or []:
        spans[tab["lang"]] = (start, start + tab["span"])
        start += tab["span"]
    stem = escape_attribute("-".join(("example", section, *(str(index) for index in path))))
    panels, buttons = [], []
    for tab in tabs:
        lang = tab["lang"]
        low, high = spans[lang]
        drawn = "\n".join(
            render_one(fence, index, placement=placement, section=section, path=path)
            for index, fence in enumerate(fences[low:high], low)
        )
        panel = f"{stem}-panel-{escape_attribute(lang)}"
        button = f"{stem}-tab-{escape_attribute(lang)}"
        label = escape(labels.get(lang, lang))
        panels.append(
            templates.fill(
                "example-panel.html",
                id=panel,
                tab=button,
                lang=escape_attribute(lang),
                label=label,
                children=drawn,
            )
        )
        buttons.append(
            templates.fill(
                "example-tab.html",
                id=button,
                panel=panel,
                lang=escape_attribute(lang),
                label=label,
            )
        )
    missing = _missing(offer, tabs)
    note = f"{stem}-missing"
    for lang in missing:
        buttons.append(
            templates.fill(
                "example-tab-missing.html",
                id=f"{stem}-tab-{escape_attribute(lang)}",
                note=escape_attribute(note),
                lang=escape_attribute(lang),
                label=escape(labels.get(lang, lang)),
            )
        )
    output = block.get("output")
    return templates.fill(
        "example.html",
        id=escape_attribute(str(block.get("id") or "")),
        langs=escape_attribute(" ".join(tab["lang"] for tab in tabs)),
        missing=f' data-missing="{escape_attribute(" ".join(missing))}"' if missing else "",
        note=(
            templates.fill(
                "example-missing.html",
                id=escape_attribute(note),
                carriers=modes.carriers(offer, " ".join(tab["lang"] for tab in tabs)),
            )
            if missing
            else ""
        ),
        output=f' data-output="{escape_attribute(output)}"' if output in FLAGS else "",
        flag=templates.fill(FLAGS[output]) if output in FLAGS else "",
        bar=templates.fill("example-bar.html", tabs="".join(buttons)) if offer else "",
        panels="".join(panels),
    )


def _in_mode_order(tabs: list, offer: object) -> list:
    """The tabs in the default mode's order: its languages first, then the others as written."""
    default = getattr(offer, "default", None)
    mode = next((c for c in getattr(offer, "choices", ()) if c.id == default), None)
    if mode is None:
        return list(tabs)
    rank = {lang: index for index, lang in enumerate(mode.tabs)}
    return sorted(tabs, key=lambda tab: rank.get(tab["lang"], len(rank)))


def _missing(offer: object, tabs: list) -> list[str]:
    """The declared languages the block has no tab for, when the corpus greys them.

    ⭐ In declared order, and empty unless the corpus says `absent_language: grey`, so the block
    of every other corpus is the panels and the tabs it has. ⛔ An example with no tab at all has
    nothing to say it is in.
    """
    if not getattr(offer, "grey", False) or not tabs:
        return []
    carried = {tab["lang"] for tab in tabs}
    return [lang for lang, _ in getattr(offer, "languages", ()) if lang not in carried]
