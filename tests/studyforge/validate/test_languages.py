"""The language checks: a tag names a declared language, and each reading has something to show."""

from __future__ import annotations

from studyforge.validate import validate
from tests.studyforge.validate import corpora

READING = {
    "corpus_api": 8,
    "languages": [
        {"id": "aa", "label": "Aa", "fence_labels": ["aa"]},
        {"id": "bb", "label": "Bb", "fence_labels": ["bb"]},
    ],
    "modes": [
        {
            "id": "only-aa",
            "label": "Aa",
            "summary": "Aa only",
            "prose": "aa",
            "tabs": ["aa"],
            "practices": ["aa"],
        },
        {
            "id": "only-bb",
            "label": "Bb",
            "summary": "Bb only",
            "prose": "bb",
            "tabs": ["bb"],
            "practices": ["bb"],
        },
    ],
}

PRACTICE_BLOCKS = corpora.PRACTICE_BLOCKS


def document(kind="lesson", ordinal=1, unit=1, **extra):
    blocks = corpora.BLOCKS if kind == "lesson" else PRACTICE_BLOCKS
    return {
        "source": "demo",
        "address": ["demo"],
        "variant": "prose",
        "unit": unit,
        "kind": kind,
        "ordinal": ordinal,
        "ingested": "2026-01-05",
        "title": "Unit 1",
        "blocks": blocks,
        **extra,
    }


def corpus(tmp_path, documents, *, manifest=None, practices=0):
    declared = {**corpora.MANIFEST, **(READING if manifest is None else manifest)}
    placed = {
        f"demo/raw/prose/unit-01/{parts['kind']}-{parts['ordinal']}.json": parts
        for parts in documents
    }
    units = [corpora.unit_entry(1, practices=practices, origin="src/one.md")]
    return corpora.write(
        tmp_path / "c",
        manifest=declared,
        containers={"demo": corpora.container(units)},
        documents=placed,
    )


def rules(report):
    return sorted(finding.rule for finding in report.findings)


def test_two_tagged_lessons_of_declared_languages_are_valid(tmp_path):
    root = corpus(tmp_path, [document(ordinal=1, lang="aa"), document(ordinal=2, lang="bb")])
    assert validate(root).findings == ()


def test_an_untagged_document_is_common_and_valid_in_a_corpus_that_declares_modes(tmp_path):
    assert validate(corpus(tmp_path, [document()])).findings == ()


def test_a_language_the_corpus_does_not_declare_is_refused_by_name(tmp_path):
    root = corpus(
        tmp_path,
        [document(ordinal=1, lang="aa"), document(ordinal=2, lang="cc"), document(ordinal=3)],
    )
    report = validate(root)
    assert rules(report) == ["language-undeclared"]
    assert "'cc'" in report.findings[0].message
    assert "lesson-2.json" in report.findings[0].where


def test_a_tag_in_a_corpus_that_declares_no_language_is_refused(tmp_path):
    manifest = dict(corpora.MANIFEST)
    root = corpus(tmp_path, [document(lang="aa")], manifest={})
    assert manifest == corpora.MANIFEST
    assert rules(validate(root)) == ["language-undeclared"]


def test_a_corpus_that_declares_no_language_and_tags_nothing_is_unchanged(tmp_path):
    root = corpus(tmp_path, [document()], manifest={})
    assert validate(root).findings == ()


def test_a_unit_with_a_practice_and_no_lesson_has_no_prose_when_modes_are_declared(tmp_path):
    root = corpus(tmp_path, [document(kind="practice")], practices=1)
    report = validate(root)
    assert "unit-prose" in rules(report)


def test_the_same_unit_passes_when_the_corpus_declares_no_modes(tmp_path):
    languages_only = {"corpus_api": 8, "languages": READING["languages"]}
    documents = [document(kind="practice", lang="aa")]
    root = corpus(tmp_path, documents, manifest=languages_only, practices=1)
    assert "unit-prose" not in rules(validate(root))


def test_a_mode_that_lists_no_unit_is_refused_by_name(tmp_path):
    root = corpus(tmp_path, [document(ordinal=1, lang="aa")])
    report = validate(root)
    assert rules(report) == ["mode-empty"]
    assert "'only-bb'" in report.findings[0].message


def test_a_practice_in_a_language_lists_the_unit_in_the_modes_that_offer_it(tmp_path):
    documents = [
        document(ordinal=1, lang="aa"),
        document(kind="practice", ordinal=1, lang="bb"),
    ]
    report = validate(corpus(tmp_path, documents, practices=1))
    assert "mode-empty" not in rules(report)
