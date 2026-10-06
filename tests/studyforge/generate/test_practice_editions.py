"""One practice written in four languages is one card, built end to end through `write_site`.

⭐ The corpus declares four languages and a mode for each. Its practice unit holds one practice in
every language, each a document of its own that names the same `edition` and its own `lang`, and
one ordinary practice beside them. The built page carries ONE card for the four, the sentence naming
the editions by their declared names, the switch at the top of every edition's panel, no
`data-lang` on an edition (so no mode hides it), and the per-mode opening language on the
workspace. ⛔ Read both ways: the same corpus with no `edition` key lists four cards, each tagged
and greyed as before.
"""

from __future__ import annotations

import re

from tests.studyforge.generate import four_corpus as four
from tests.studyforge.validate import corpora

PAGE = ".studyforge/demo/units/unit-01/unit-01-practices-1.unit.html"


def practices(edition: str | None) -> tuple:
    """A unit of one practice in each language, titled as an adapter titles one, and one more."""
    extra = (edition,) if edition else ()
    found = [
        (
            "practice",
            lang,
            corpora.PRACTICE_BLOCKS,
            f"Keep a conversation ({four.LABELS[lang]})",
            *extra,
        )
        for lang in four.LANGS
    ]
    found.append(("practice", None, corpora.PRACTICE_BLOCKS, "A common practice"))
    return (
        (1, "Practices", [("lesson", None, [four.words("Common words.")], None), *found]),
    )


def page(tmp_path, name: str, edition: str | None) -> str:
    out = four.build(
        tmp_path,
        name,
        four.declared(absent="grey"),
        units=practices(edition),
        code=True,
        graded=True,
    )
    return (out / PAGE).read_text(encoding="utf-8")


def cards(markup: str) -> list[str]:
    listed = markup[markup.index('<ol data-practices-part="cards">') :]
    listed = listed[: listed.index("</ol>")]
    return ['<li id="card-' + one for one in listed.split('<li id="card-')[1:]]


def test_four_language_documents_that_name_one_edition_are_one_card(tmp_path):
    markup = page(tmp_path, "edited", "conversation")
    found = cards(markup)
    assert len(found) == 2, "one card for the four editions, one for the common practice"
    card = found[0]
    assert ">Keep a conversation</a>" in card
    assert "Available in: " in card
    names = re.findall(r'data-edition="[a-z]+"[^>]*>([A-Za-z]+)<', card)
    assert names == ["Aa", "Bb", "Cc", "Dd"]
    assert "of 4 languages" in card
    assert "data-practice-lang" not in card, "an edition is never greyed by a mode"
    assert "Practice (2)" in markup


def test_each_editions_panel_has_the_switch_and_no_reading_mode_can_hide_one(tmp_path):
    markup = page(tmp_path, "edited2", "conversation")
    opening = r'<section id="s-practice-[a-z0-9-]+"[^>]*data-edition="[^"]+"[^>]*>'
    statements = re.findall(opening, markup)
    assert len(statements) == 4
    assert not any("data-lang" in one for one in statements)
    panels = re.findall(r'<section data-practice="[^"]+"[^>]*data-edition="[^"]+"[^>]*>', markup)
    assert len(panels) == 4
    row = r'<p data-practice-part="editions" role="group" aria-label="Language" hidden>'
    rows = re.findall(row, markup)
    assert len(rows) == 4
    table = re.search(r"data-edition-modes='([^']+)'", markup)
    assert table and '"only-bb":["bb"]' in table.group(1)


def test_without_the_edition_key_the_same_four_documents_are_four_tagged_cards(tmp_path):
    markup = page(tmp_path, "plain", None)
    found = cards(markup)
    assert len(found) == 5
    for word in ("data-edition", 'data-practice-part="editions"', "data-practice-editions"):
        assert word not in markup
    assert sum("data-practice-lang=" in one for one in found) == 4
