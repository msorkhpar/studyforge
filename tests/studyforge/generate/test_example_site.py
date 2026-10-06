"""An example with a tab per language, end to end through `write_site`.

⭐ A corpus that declares modes gets the block, its tab bar and the tab rules in the files
it already writes; a corpus that declares none gets the panels under labels and no bar, no
rule, no script and no extra file; and a corpus with no example builds to the bytes it did.
"""

from __future__ import annotations

from tests.studyforge.generate.test_modes_site import LANGUAGES_ONLY, files
from tests.studyforge.generate.test_section_language import build, pages
from tests.studyforge.validate.test_languages import READING, document

EXAMPLE = {
    "type": "example",
    "id": "ex",
    "output": "compiler",
    "tabs": [{"lang": "aa", "span": 2}, {"lang": "bb", "span": 1}],
    "blocks": [
        {"type": "code", "lang": "aa", "text": "a"},
        {"type": "code", "lang": "text", "text": "printed"},
        {"type": "code", "lang": "bb", "text": "b"},
    ],
}
WITH = [document(ordinal=1, blocks=[{"type": "para", "text": "Words."}, EXAMPLE])]
WITHOUT = [document(ordinal=1)]
BOTH = {**READING, "modes": [*READING["modes"], {**READING["modes"][0], "id": "both",
                                                 "tabs": ["aa", "bb"]}]}


def only_unit_page(out) -> str:
    return next(b for b in pages(out).values() if b'data-example="ex"' in b).decode("utf-8")


def test_a_modes_corpus_gets_the_example_its_bar_and_the_tab_rules(tmp_path):
    out = build(tmp_path, "modal", WITH, BOTH)
    page = only_unit_page(out)
    assert page.count('role="tab"') == 2 and 'data-output="compiler"' in page
    assert "Does not compile, on purpose" in page
    css = files(out)[".studyforge/assets/modes.css"].decode("utf-8")
    assert 'html[data-mode="both"] div[data-example] [data-lang="aa"] { order: 0; }' in css
    assert b"MODE_TABS = " in files(out)[".studyforge/assets/modes.js"]


def test_a_corpus_that_declares_no_modes_gets_no_bar_no_rule_no_script_and_no_file(tmp_path):
    out = build(tmp_path, "languages", WITH, LANGUAGES_ONLY)
    page = only_unit_page(out)
    assert 'role="tab"' not in page and "tablist" not in page
    assert page.count('role="tabpanel"') == 2
    written = files(out)
    assert not [name for name in written if name.endswith(("modes.css", "modes.js"))]
    assert b"example-tabs" not in b"".join(written.values())


def test_the_shared_bundle_keeps_its_bytes_whether_or_not_a_page_holds_an_example(tmp_path):
    plain = files(build(tmp_path, "plain", WITHOUT, {}))
    held = files(build(tmp_path, "held", WITH, {}))
    # ⭐ The search index says what the pages say, so it is the one shared file that differs.
    shared = [
        name
        for name in plain
        if name.startswith(".studyforge/assets/") and not name.endswith("search-index.js")
    ]
    assert shared and all(plain[name] == held[name] for name in shared)
    assert b"data-example" not in b"".join(plain.values())


def test_a_unit_with_no_example_carries_no_tab_markup_in_a_corpus_that_declares_modes(tmp_path):
    built = pages(build(tmp_path, "a", WITHOUT, BOTH))
    for body in built.values():
        assert b"data-example" not in body and b'role="tab' not in body
