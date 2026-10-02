"""A corpus that declares modes writes the modes client; one that declares none writes nothing of it."""

from __future__ import annotations

from studyforge.generate import write_site
from studyforge.render import pageassets
from tests.studyforge.generate.test_section_language import build, pages
from tests.studyforge.validate.test_languages import READING, document

DOCUMENTS = [document(ordinal=1), document(ordinal=2, lang="aa"), document(ordinal=3, lang="bb")]
LANGUAGES_ONLY = {"corpus_api": 8, "languages": READING["languages"]}


def files(out):
    return {
        path.relative_to(out).as_posix(): path.read_bytes()
        for path in sorted(out.rglob("*"))
        if path.is_file()
    }


def test_a_corpus_with_no_modes_builds_to_the_same_bytes_with_or_without_languages(tmp_path):
    plain = build(tmp_path, "plain", DOCUMENTS, {})
    declared = build(tmp_path, "declared", DOCUMENTS, LANGUAGES_ONLY)
    assert files(plain) == files(declared)
    joined = b"".join(files(declared).values())
    for word in (b"data-mode", b"modes.css", b"modes.js", b"mode-question", b"boot.mode"):
        assert word not in joined


def test_modes_add_two_files_and_leave_the_shared_bundle_as_it_was(tmp_path):
    plain = files(build(tmp_path, "plain", DOCUMENTS, {}))
    modal = files(build(tmp_path, "modal", DOCUMENTS, READING))
    added = sorted(set(modal) - set(plain))
    assert added == [".studyforge/assets/modes.css", ".studyforge/assets/modes.js"]
    for name in pageassets.written_files():
        assert modal[f".studyforge/assets/{name}"] == plain[f".studyforge/assets/{name}"]


def test_every_page_kind_carries_the_default_mode_the_link_the_switch_and_the_script(tmp_path):
    built = pages(build(tmp_path, "modal", DOCUMENTS, READING))
    assert len(built) == 3
    for name, body in built.items():
        text = body.decode("utf-8")
        assert '<html lang="en" data-mode="only-aa">' in text, name
        assert text.count("modes.css") == 1 and text.count("modes.js") == 1, name
        assert 'aria-label="Reading mode"' in text and 'data-section="mode-question"' in text
        # ⭐ In the head, not at body level: a body-level script is a row of the rail's span.
        assert text.index("modes.js") < text.index("<body>"), name
        assert 'modes.js" defer></script>' in text, name


def test_the_default_mode_is_the_declared_one_not_the_first(tmp_path):
    declared = {**READING, "default_mode": "only-bb"}
    built = pages(build(tmp_path, "second", DOCUMENTS, declared))
    assert all(b'<html lang="en" data-mode="only-bb">' in body for body in built.values())


def test_a_tagged_sections_outline_lines_carry_its_language_and_untagged_ones_do_not(tmp_path):
    built = pages(build(tmp_path, "modal", DOCUMENTS, READING))
    text = next(body for body in built.values() if b'data-section="prose' in body).decode()
    outline = text[text.index('aria-label="Outline"') : text.index("</nav>", text.index("Outline"))]
    assert outline.count('data-lang="aa"') == 3 and outline.count('data-lang="bb"') == 3
    assert '<li data-level="1"><a href="#s-prose">' in outline


def test_a_second_build_changes_nothing(tmp_path):
    first = files(build(tmp_path, "one", DOCUMENTS, READING))
    second = files(build(tmp_path, "two", DOCUMENTS, READING))
    assert first == second
    assert write_site  # the entry point the helper drives
