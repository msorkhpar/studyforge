"""A language a block or a practice lacks is greyed, and only when the corpus asks for it.

⭐ The row's claims, end to end through `write_site`: with `absent_language: grey` a block that
lacks a language the corpus declares has a disabled tab for it and one sentence naming the
languages that carry it, built from the declaration and not from a count; a practice card says
which languages it is written in and carries them in a sentence; the rules that show them are
one set per mode; and a corpus that leaves the key out, or says `hide`, builds to the bytes it
always did.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from studyforge.corpus.manifest import ManifestError
from tests.studyforge.generate import four_corpus as corpus
from tests.studyforge.generate.test_modes_site import files

ASSETS = ".studyforge/assets"
SRC = Path(__file__).resolve().parents[3] / "src" / "studyforge"

#: The files that write what a greyed language adds.
SOURCES = (
    "render/absent_language.py",
    "render/assets/absent-language.js",
    "render/assets/absent-language.css",
)
LANGUAGE_NAMES = re.compile(
    r"\b(python|typescript|java|kotlin|swift|rust|golang|ruby|scala|clojure|haskell)\b", re.I
)


def grey(count: int = 4, **extra):
    """The manifest of the corpus of `count` languages, saying `absent_language: grey`."""
    extra.setdefault("absent", "grey")
    return corpus.declared(count, **extra)


def text(out, where):
    return (out / where).read_text(encoding="utf-8")


def block(page: str, ident: str) -> str:
    """One example block's markup: from its opening tag to the next block, or the page's end."""
    start = page.index(f'<div data-example="{ident}"')
    following = page.find('<div data-example="', start + 1)
    return page[start : following if following != -1 else len(page)]


def tabs(markup: str) -> list[tuple[str, bool]]:
    """`(language, disabled)` of each tab in a block's markup, in order."""
    return [
        (m.group(1), 'aria-disabled="true"' in m.group(0))
        for m in re.finditer(r'<button[^>]*role="tab"[^>]*data-lang="([^"]+)"[^>]*>', markup)
    ]


def test_a_corpus_that_greys_names_the_tabs_a_block_lacks_and_the_languages_that_carry_it(tmp_path):
    out = corpus.build(tmp_path, "c", grey(mixed=True))
    page = text(out, corpus.PAGES[1])
    duo, solo = block(page, "duo"), block(page, "solo")
    assert tabs(duo) == [("aa", False), ("bb", False), ("cc", True), ("dd", True)]
    assert 'data-missing="cc dd"' in duo and "Available in: Aa, Bb." in duo
    assert tabs(solo) == [("cc", False), ("aa", True), ("bb", True), ("dd", True)]
    assert "Available in: Cc." in solo
    ids = re.findall(r'aria-describedby="([^"]+)"', duo)
    assert ids and all(f'id="{one}"' in duo for one in ids)
    assert "aria-controls" not in "".join(
        m.group(0) for m in re.finditer(r"<button[^>]*aria-disabled[^>]*>", duo)
    )


def test_the_sentence_is_built_from_the_declaration_and_not_from_a_count(tmp_path):
    renamed = grey(mixed=True)
    for language in renamed["languages"]:
        language["label"] = f"Lang {language['id'].upper()}"
    out = corpus.build(tmp_path, "c", renamed)
    page = text(out, corpus.PAGES[1])
    assert "Available in: Lang AA, Lang BB." in block(page, "duo")
    three = corpus.build(tmp_path, "three", grey(3, mixed=True))
    only_cc = block(text(three, corpus.PAGES[1]), "solo")
    assert tabs(only_cc) == [("cc", False), ("aa", True), ("bb", True)]
    assert "Available in: Cc." in only_cc


def test_the_grey_rules_name_each_languages_mode_and_never_hide_a_block_whole(tmp_path):
    out = corpus.build(tmp_path, "c", grey(mixed=True))
    css = text(out, f"{ASSETS}/modes.css")
    for x in corpus.LANGS:
        rule = f'html[data-mode="only-{x}"] div[data-example][data-missing~="{x}"]'
        assert f"{rule} [data-example-missing] {{ display: block; }}" in css
    assert ":not([data-langs~=" not in css, "an example is never hidden whole"
    js = text(out, f"{ASSETS}/modes.js")
    assert "aria-disabled" in js and "data-practice-carriers" in js


def test_a_corpus_that_hides_what_a_language_lacks_builds_to_the_bytes_it_always_did(tmp_path):
    omitted = files(corpus.build(tmp_path, "omitted", grey(absent=None, mixed=True)))
    hidden = files(corpus.build(tmp_path, "hidden", grey(absent="hide", mixed=True)))
    assert omitted == hidden
    joined = b"".join(omitted.values())
    for word in (b"data-missing", b"Available in", b"data-practice-lang", b"example-tab-missing"):
        assert word not in joined
    assert b"absent-language" not in joined and b"data-practice-carriers" not in joined


def test_only_the_grey_corpus_adds_the_greyed_files_content(tmp_path):
    plain = files(corpus.build(tmp_path, "plain", grey(absent=None, mixed=True)))
    greyed = files(corpus.build(tmp_path, "grey", grey(mixed=True)))
    assert set(plain) == set(greyed)
    changed = sorted(name for name in plain if plain[name] != greyed[name])
    assert f"{ASSETS}/modes.css" in changed and f"{ASSETS}/modes.js" in changed
    for name in plain:
        if name.startswith(ASSETS) and name not in changed:
            assert plain[name] == greyed[name]


def test_an_absent_language_that_is_neither_value_is_refused_by_name(tmp_path):
    with pytest.raises(ManifestError) as refused:
        corpus.build(tmp_path, "c", grey(absent="gray"))
    assert "'absent_language' must be one of ['hide', 'grey']" in str(refused.value)
    alone = {"corpus_api": 8, "absent_language": "grey"}
    with pytest.raises(ManifestError) as lonely:
        corpus.build(tmp_path, "d", alone)
    assert "'absent_language' without 'modes'" in str(lonely.value)


def test_a_practice_card_names_its_languages_and_the_languages_that_carry_it(tmp_path):
    out = corpus.build(tmp_path, "c", grey())
    page = text(out, corpus.PAGES[5])
    cards = re.findall(
        r'<li id="card-[^"]+"[^>]*data-practice-lang="([^"]+)">.*?'
        r"<p data-practice-carriers>([^<]*)</p>",
        page,
        re.S,
    )
    assert cards == [
        ("aa bb", "Available in: Aa, Bb."),
        ("cc", "Available in: Cc."),
        ("aa bb cc dd", "Available in: Aa, Bb, Cc, Dd."),
        ("dd", "Available in: Dd."),
    ]
    panels = re.findall(r'<section data-lang="([^"]+)" data-practice=', page)
    assert panels == [] or all(" " in one or one in corpus.LANGS for one in panels)


def test_a_practice_card_carries_no_language_unless_the_corpus_greys(tmp_path):
    out = corpus.build(tmp_path, "c", grey(absent=None))
    page = text(out, corpus.PAGES[5])
    assert "data-practice-lang" not in page and "data-practice-carriers" not in page
    assert len(re.findall(r"data-practice-card=", page)) == 4


def test_the_files_that_grey_a_language_name_none(tmp_path):
    for name in SOURCES:
        body = (SRC / name).read_text(encoding="utf-8")
        assert LANGUAGE_NAMES.findall(body) == [], name
    assert tmp_path
