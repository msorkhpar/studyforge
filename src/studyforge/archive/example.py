"""What an `example` block's tabs and output may be, once.

**What it does.** States the three small vocabularies of the `example` block that
`archive.blocks` holds as a row: the keys of one tab, the outputs a block may be
flagged with, and the block types an example may hold.

**How you use it.** `archive.markdown.example` writes blocks to this shape and
`validate.blocks` reads them against it, spelling the same words (a test pins the two
equal: an archive's names are not shared across the package edge).

**Depends on.** Nothing.

⭐ **An example's tabs.** An `example` block holds its blocks flat in `blocks`, and its
`tabs` cut that run into consecutive spans, one per language:
`{"lang": "<id>", "span": <how many blocks>}`, and optionally `"code": "<corpus-relative file>"`.
⭐ An example block may also carry `"support": ["<corpus-relative file or folder>", ...]`: the
files its code imports to run (a shared harness folder), which a release keeps beside the code
named by the tabs. Written only where an adapter sets it.
Every walker that recurses on `blocks`
reaches an example's code with no change. A block has from one to `EXAMPLE_MAX_TABS`
tabs. `output` names why the block exists beside a
program: one of `EXAMPLE_OUTPUTS`.
"""

from __future__ import annotations

EXAMPLE_TAB_KEYS = ("lang", "span")
#: ⭐ A tab may also name `code`: the corpus-relative path of the file its code is, so a served
#: page can offer Run for the test beside it. Written only where an adapter sets it, so a tab
#: without one is the tab it always was.
EXAMPLE_TAB_OPTIONAL = ("code",)
#: How many tabs one example may have: a tab bar of more is a menu, not a choice between versions.
EXAMPLE_MAX_TABS = 8
EXAMPLE_OUTPUTS = ("compiler", "warning")
#: The types an example's blocks may be: its code and the output it printed.
EXAMPLE_BLOCKS = ("code",)
