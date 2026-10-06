"""An example block: the code of one example, one run of fences cut into a tab per language.

**What it does.** Turns the `example` region `regions` found into the archive's
`example` block, and turns a run of regions into the blocks of a page, so an
example sits in the page's text where the author wrote it.

**How you use it.** `blocks_of(found, languages)` for the regions of a page, or
`example_block(region, languages)` for one. `languages` maps each fence label a
corpus's languages declare to that language's id (the manifest's
`fence_labels`, read by the caller: ⛔ this package does not read a manifest).

    <!-- example: id tabs: a,b [output: compiler] -->
    ```a          a fence of a declared language opens that language's tab
    ...
    ```
    ```text       any other fence is that tab's output, shown with it
    ...
    ```
    ```b          the next language's tab
    ...
    <!-- /example -->

**Depends on.** `document` (`parse`), `regions` and `errors`. ⛔ It names no
language (R1): the ids and labels are the corpus's data.

## ⭐ Why one flat run and spans

The block holds its fences flat in `blocks`, as `quote` and `disclosure` do, and
`tabs` says how many of them each language owns (`archive.blocks.EXAMPLE_TAB_KEYS`).
Every walker that recurses on `blocks` therefore reaches an example's code with no change,
and a document that holds no example is the bytes it was.

## ⛔ What is refused, by line

An example that holds anything but code fences; a fence before the first
language's, or in a language that has no tab; tabs that are not the header's
`tabs`, in the header's order, each exactly once; a header language no fence
opens. ⚠️ Lines are 1-based, and no refusal quotes the text (R7).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from studyforge.archive.markdown.document import parse
from studyforge.archive.markdown.errors import MarkdownError
from studyforge.archive.markdown.regions import COMMON, EXAMPLE, LANG, Region


def blocks_of(
    found: Iterable[Region], languages: Mapping[str, str], *, lang_default: str = ""
) -> list[dict]:
    """Return the blocks of `found`, an example region as one `example` block.

    ⭐ A common or a language region is parsed as it always was, so a page that
    writes no example reads as it did.
    """
    blocks: list[dict] = []
    for region in found:
        if region.kind == EXAMPLE:
            blocks.append(example_block(region, languages))
        elif region.kind in (COMMON, LANG):
            blocks.extend(parse(region.text, lang_default=lang_default))
    return blocks


def example_block(region: Region, languages: Mapping[str, str]) -> dict:
    """Return the `example` block for `region`, refusing a shape it cannot read."""
    fences = parse(region.text)
    if any(block.get("type") != "code" for block in fences):
        raise MarkdownError(f"line {region.line}: an example holds code fences and nothing else")
    spans: list[dict] = []
    for block in fences:
        lang = languages.get((block.get("lang") or "").strip())
        if lang is not None:
            spans.append({"lang": lang, "span": 1})
        elif spans:
            spans[-1]["span"] += 1
        else:
            raise MarkdownError(
                f"line {region.line}: an example opens with the fence of one of its languages"
            )
    if tuple(span["lang"] for span in spans) != region.tabs:
        raise MarkdownError(
            f"line {region.line}: the fences of an example are its tabs, each once and in "
            f"the order the header lists them"
        )
    block: dict = {"type": "example", "id": region.id, "tabs": spans, "blocks": fences}
    if region.output is not None:
        block["output"] = region.output
    return block
