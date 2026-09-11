"""QA-03 — the visual and browser verification harness.

**What it does.** Opens a page this repository generated in a real browser over
`file://` and reads back what a unit test cannot see: the pixels, the computed
colours in both themes, the order focus moves in, what survives with scripts
off, and every request the page issued.

**How you use it.** The fixtures in `conftest.py` give a test a built site and a
tab. `discovery.require_browser()` is what makes a check skip — loudly, with the
remedy named — on a machine with no browser.

**Depends on.** The standard library, `pytest`, and `studyforge.render` for
building the pages it opens. ⛔ **No driver library and no `pip install`** —
`browser.py` says why.

## ⛔ Why this exists

⭐ **In the extraction source a highlight-token misclassification italicised
every string in one language, the tests passed, and only a screenshot caught
it.** A project whose reading surface is its product cannot verify that surface
by assertion alone, and four later tasks have acceptance no unit test reaches:
`SF-14` (works with JavaScript disabled), `SF-18` (a highlight tracking
playback), `SF-24` (keyboard-operable), `QA-02` (contrast for every token in two
themes). This lands at M1 rather than M7 so those four use it instead of each
improvising one.

## ⛔ The evidence state, stated here because a reader will look here first

⭐ **These checks are `pinned green` IN THE DEV IMAGE and `unpinned green`
anywhere else**, and which one a run was is **printed** rather than assumed.
⛔ **`QA-03/1` — *the pinned dev image has no browser* — was closed by `W36`**,
which installed one pinned by version and checksum. Until then 57 of these
checks did not run in the one environment Ruling 40 makes authoritative, and
`quality floor: clean` said nothing about any of them.

⚠️ **A host run is still taken against an engine nobody pinned**, so a review of
one states the browser version and does not call it pinned.
`discovery.evidence_state()` decides which state a run may claim, keyed on the
image's own marker; `discovery.report_line()` prints that and the version at the
end of every suite run whether or not a browser was found.

## The acceptance clauses, and where each one runs

⛔ `ACCEPTANCE` is asserted total against this package's own test modules in
`test_init.py`, so a clause cannot be quietly dropped by deleting a file.
"""

from __future__ import annotations

#: `E10`'s acceptance for QA-03, mapped to the module that answers it. ⭐ Each
#: is run twice — against the built site, and against a tree damaged in exactly
#: the way that clause exists to catch (`site.DAMAGE`).
ACCEPTANCE = {
    "renders a generated page in a real browser and captures it": "test_capture",
    "verifies computed contrast for every palette token in both themes": "test_contrast",
    "drives keyboard traversal": "test_keyboard",
    "runs a page with JavaScript disabled": "test_no_script",
    "opens over file:// and issues no network request (R8)": "test_offline",
}
