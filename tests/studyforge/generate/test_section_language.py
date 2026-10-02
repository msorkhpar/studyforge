"""A page holds every section, and a language tag shows on the section it names only.

⭐ The row's own claims, end to end through `write_site`: tagged sections reach
the page in the order the unit has them and carry `data-lang`; an untagged
document builds to the same bytes in a corpus that declares languages and modes
and in one that declares neither.
"""

from __future__ import annotations

import re

from studyforge.generate import write_site
from tests.studyforge.validate import corpora
from tests.studyforge.validate.test_languages import READING, document

SECTION = re.compile(r'<section id="[^"]*" data-section="([^"]+)"[^>]*?( data-lang="([^"]+)")?>')


def build(tmp_path, name, documents, manifest):
    placed = {
        f"demo/raw/prose/unit-01/{parts['kind']}-{parts['ordinal']}.json": parts
        for parts in documents
    }
    root = corpora.write(
        tmp_path / name,
        manifest={**corpora.MANIFEST, **manifest},
        containers={"demo": corpora.container([corpora.unit_entry(1, origin="src/one.md")])},
        documents=placed,
    )
    out = tmp_path / f"{name}-out"
    out.mkdir()
    write_site(root, out)
    return out


def pages(out):
    return {
        path.relative_to(out).as_posix(): path.read_bytes()
        for path in sorted(out.rglob("*.html"))
    }


def unit_page(out) -> str:
    found = [text for text in pages(out).values() if b'data-section="prose' in text]
    assert len(found) == 1
    return found[0].decode("utf-8")


def test_the_page_holds_every_section_and_tags_only_the_tagged_ones(tmp_path):
    documents = [
        document(ordinal=1),
        document(ordinal=2, lang="aa"),
        document(ordinal=3, lang="bb"),
    ]
    body = unit_page(build(tmp_path, "tagged", documents, READING))
    sections = [(m.group(1), m.group(3)) for m in SECTION.finditer(body)]
    assert sections == [("prose", None), ("prose-2", "aa"), ("prose-3", "bb")]
    assert body.count("data-lang=") == 2


def test_a_tagged_practice_is_a_section_of_the_page_too(tmp_path):
    documents = [document(ordinal=1), document(kind="practice", ordinal=1, lang="aa")]
    body = unit_page(build(tmp_path, "practice", documents, READING))
    assert ("practice-prose", "aa") in [(m.group(1), m.group(3)) for m in SECTION.finditer(body)]


def test_an_untagged_document_builds_to_the_same_bytes_whether_or_not_modes_are_declared(tmp_path):
    documents = [document(ordinal=1), document(ordinal=2)]
    plain = build(tmp_path, "plain", documents, {})
    modes = build(tmp_path, "modes", documents, READING)
    assert pages(plain) == pages(modes)
    assert b"data-lang" not in b"".join(pages(modes).values())
