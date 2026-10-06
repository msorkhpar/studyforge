"""A corpus of any number of languages: its modes, its question, and a section for several.

⭐ The row's claims, end to end through `write_site`, with the fixture of four languages and the
same corpus cut to one, two and three: the first-visit question and the switch list exactly the
declared modes, a section may name several languages and belongs to each of their modes, a corpus
whose sections each name one language is matched as it always was, and nothing in the framework's
mode and tab sources names a language or counts them.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from studyforge.validate import validate
from tests.studyforge.generate import four_corpus as corpus
from tests.studyforge.validate import corpora
from tests.studyforge.validate.test_languages import document

ASSETS = ".studyforge/assets"
SRC = Path(__file__).resolve().parents[3] / "src" / "studyforge"

#: Every file of the framework that writes or serves a mode or a tab.
SOURCES = (
    "render/modes.py",
    "render/example_tabs.py",
    "render/assets/modes.js",
    "render/assets/modes.css",
    "render/assets/example-tabs.js",
    "render/assets/example-tabs.css",
    "render/page/blocks/example.py",
    "generate/entrylanguages.py",
    "corpus/manifest/reading.py",
)
LANGUAGE_NAMES = re.compile(
    r"\b(python|typescript|java|kotlin|swift|rust|golang|ruby|scala|clojure|haskell)\b", re.I
)


def text(out, where):
    return (out / where).read_text(encoding="utf-8")




@pytest.mark.parametrize("count", [1, 2, 3, 4])
def test_the_switch_the_question_and_the_rules_follow_the_declared_modes_whatever_their_number(
    tmp_path, count
):
    out = corpus.build(tmp_path, "c", corpus.declared(count))
    page = text(out, corpus.PAGES[1])
    chosen = corpus.LANGS[:count]
    asked = re.findall(r'<li><button type="button" data-mode-choice="([^"]+)">', page)
    switched = re.findall(r'<button type="button" data-mode-choice="([^"]+)" data-mode-prose', page)
    assert asked == switched == [f"only-{x}" for x in chosen]
    css = text(out, f"{ASSETS}/modes.css")
    for x in chosen:
        assert f'html[data-mode="only-{x}"] section[data-lang]' in css
    assert css.count("html[data-mode=") == len(re.findall(r"html\[data-mode=\"", css))
    assert {m for m in re.findall(r'html\[data-mode="([^"]+)"\]', css)} == {
        f"only-{x}" for x in chosen
    }


def test_a_section_that_names_several_languages_is_one_section_and_a_unit_of_each(tmp_path):
    out = corpus.build(tmp_path, "c", corpus.declared())
    page = text(out, corpus.PAGES[3])
    assert re.search(r'<section [^>]*data-lang="aa bb"', page), "the section names both"
    assert "It is read in: Aa only, Bb only." in page, "the note names each mode that reads it"
    css = text(out, f"{ASSETS}/modes.css")
    assert 'section[data-lang]:not([data-lang~="cc"])' in css
    index = text(out, "index.html")
    row = re.search(r'<li id="demo/unit-03"[^>]*>', index)
    assert row and 'data-entry-lang="aa bb"' in row.group(0)
    assert 'data-entry-label>Aa, Bb</span>' in index


def test_sections_that_each_name_one_language_are_matched_as_they_always_were(tmp_path):
    units = tuple(unit for unit in corpus.UNITS if unit[0] in (1, 2))
    out = corpus.build(tmp_path, "c", corpus.declared(absent=None), units=units)
    css = text(out, f"{ASSETS}/modes.css")
    assert 'section[data-lang]:not([data-lang="cc"])' in css
    assert 'data-lang~=' not in css.replace("data-langs~=", "").replace("data-entry-lang~=", "")


def test_a_corpus_with_a_section_for_several_languages_validates_and_each_is_listed(tmp_path):
    units = [corpora.unit_entry(1, origin="src/one.md")]
    one = corpus.declared(2)
    placed = {"demo/raw/prose/unit-01/lesson-1.json": document(lang="aa bb")}
    root = corpora.write(
        tmp_path / "ok",
        manifest={**corpora.MANIFEST, **one},
        containers={"demo": corpora.container(units)},
        documents=placed,
    )
    assert validate(root).findings == ()
    placed = {"demo/raw/prose/unit-01/lesson-1.json": document(lang="aa zz")}
    root = corpora.write(
        tmp_path / "bad",
        manifest={**corpora.MANIFEST, **one},
        containers={"demo": corpora.container(units)},
        documents=placed,
    )
    found = [f for f in validate(root).findings if f.rule == "language-undeclared"]
    assert len(found) == 1 and "'zz'" in found[0].message


def test_the_mode_and_tab_sources_name_no_language(tmp_path):
    for name in SOURCES:
        body = (SRC / name).read_text(encoding="utf-8")
        assert LANGUAGE_NAMES.findall(body) == [], name
    assert tmp_path  # the fixtures above are the only languages these files meet
