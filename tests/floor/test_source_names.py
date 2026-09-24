"""Mirror of `tests/floor/source_names.py` (R12).

⭐ **Every positive here is paired with the legitimate use it is one word
from.** A check that fires on `an ISO date` or on `a Java package segment`
would be switched off within a day, and then R1 would be enforced by nobody.
"""

from __future__ import annotations

import pytest

from tests.floor.source_names import (
    KNOWN_SOURCES,
    check_source_names,
    named_sources,
)
from tests.support import repository_root

#: One spelling per registry entry, plus the spellings a slug grep misses.
#: ⚠️ The last two are the whole reason this is a module rather than one more
#: alternative in a shell pattern: a corpus named in English rather than by
#: its slug.
NAMES_A_SOURCE = [
    "extracted from CodeSignal's own material",
    "the senior-java tutorial ships 168 graders",
    "measured against the java-senior repository",
    "ISO-8583's material carries 96 card-shaped strings",
    "the jPOS tutorial is a v2 target",
    "all 19 SPARQL lessons end in an exercise",
    "the Java corpus numbers every module",
    "the Java repo's additive pom line",
    "the ISO corpus ships three aggregates",
    'classify("src/ISO.md")',
]

#: ⚠️ The controls, and they carry the real risk. Two of these are words this
#: framework uses constantly for reasons that have nothing to do with a corpus.
NAMES_NO_SOURCE = [
    "'ingested' must be an ISO date, YYYY-MM-DD",
    "a leading digit is illegal in a Java package segment",
    "inherited from the extraction source's progress rules",
    "the four designed shapes",
    "one designed shape's directories are flat",
    "a file named settings.local.json",
    "the first consuming corpus's additive line",
]


@pytest.mark.parametrize("text", NAMES_A_SOURCE)
def test_a_corpus_named_in_framework_source_is_a_finding(text):
    assert named_sources(text), text


@pytest.mark.parametrize("text", NAMES_NO_SOURCE)
def test_and_the_words_that_merely_look_like_one_are_not(text):
    assert named_sources(text) == [], text


def test_the_finding_names_the_role_and_never_the_corpus():
    # ⛔ A finding that quoted the name would put it in the build log, and
    # §7c's own sentence is that the next reader takes a name as licence.
    (_line, corpus, why) = named_sources("ISO-8583's material carries 96 strings")[0]
    assert "8583" not in corpus and "8583" not in why
    assert corpus == "a v2 target"


#: ⭐ A name wrapped across a line break, in prose, in a comment and across two
#: concatenated string literals, and each is reported on the line it starts on.
SPLIT_ACROSS_A_BREAK = [
    "the Java\ncorpus numbers every module",
    "# the ISO\n# corpus ships three aggregates",
    '    "measured against the ISO "\n    "repository"',
    "the senior-\njava material ships 168 graders",
    "* the ISO-\n* 8583 material",
]

#: ⚠️ The controls: the same words wrapped where they name no corpus.
SPLIT_AND_NO_SOURCE = [
    "an ISO\ndate, YYYY-MM-DD",
    "an ISO-\n8601 date",
    "a leading digit is illegal in a Java\npackage segment",
]


@pytest.mark.parametrize("text", SPLIT_ACROSS_A_BREAK)
def test_a_corpus_named_across_a_line_break_is_a_finding_on_its_first_line(text):
    assert [line for line, _corpus, _why in named_sources(text)] == [1], text


@pytest.mark.parametrize("text", SPLIT_AND_NO_SOURCE)
def test_and_the_same_words_wrapped_where_they_name_nothing_are_not(text):
    assert named_sources(text) == [], text


def test_a_name_the_next_line_holds_whole_is_reported_once_on_that_line():
    assert [line for line, _c, _w in named_sources("before\nthe Java corpus\nafter")] == [2]


def test_this_repository_names_no_source_in_framework_code():
    root = repository_root()
    findings = check_source_names(root)
    assert findings == [], "\n".join(str(f) for f in findings)


def test_and_the_check_that_says_so_can_actually_fire(tmp_path):
    # ⛔ **A check states its denominator.** The test above asserts an empty list,
    # and an empty list is what a check that reads nothing returns. This one shows the same
    # function finding something, on a tree it builds, so "clean" means clean
    # rather than "never ran".
    module = tmp_path / "src" / "studyforge" / "thing.py"
    module.parent.mkdir(parents=True)
    module.write_text('"""Doc."""\n# measured on the jPOS tutorial\n', encoding="utf-8")
    findings = check_source_names(tmp_path)
    assert [f.rule for f in findings] == ["source-name"]
    assert findings[0].line == 2


def test_a_document_may_name_a_corpus_and_a_module_may_not(tmp_path):
    # ⭐ The exemption, and it is structural rather than a list: `docs/` is not
    # a scan root and `tests/` is not framework source, so a corpus's name is
    # legal there without anything being excused. ⛔ There is nowhere under
    # `src/` to add a file to, which is the property being asserted.
    for where in ("docs/notes.md", "tests/studyforge/test_thing.py", "tools/thing.py"):
        path = tmp_path / where
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('"""The jPOS tutorial and CodeSignal."""\n', encoding="utf-8")
    assert check_source_names(tmp_path) == []
    # ...and the inhabitation half: the same text under `src/` is refused.
    module = tmp_path / "src" / "studyforge" / "thing.py"
    module.parent.mkdir(parents=True)
    module.write_text('"""The jPOS tutorial."""\n', encoding="utf-8")
    assert len(check_source_names(tmp_path)) == 1


@pytest.mark.parametrize(
    "where",
    [
        "src/studyforge/skills/thing/SKILL.md",
        "src/studyforge/render/templates/thing.html",
        "src/studyforge/render/assets/thing.css",
        "src/studyforge/render/assets/thing.js",
    ],
)
def test_every_file_the_framework_ships_is_read_and_not_only_its_modules(tmp_path, where):
    # ⛔ A skill's page ships inside the package and a client reads it as the
    # framework's own words, so a corpus it names is a corpus the framework
    # knows (R1), exactly as it would be in a docstring.
    path = tmp_path / where
    path.parent.mkdir(parents=True)
    path.write_text("measured on the jPOS tutorial\n", encoding="utf-8")
    findings = check_source_names(tmp_path)
    assert [(f.path, f.line) for f in findings] == [(where, 1)]


def test_the_registry_is_inhabited_and_every_entry_carries_a_reason():
    # ⛔ The denominator again: a registry that emptied would make every test above
    # that asserts *absence* pass, and only this one would notice.
    assert len(KNOWN_SOURCES) >= 4
    for corpus, pattern, why in KNOWN_SOURCES:
        assert corpus and why and pattern.pattern
        assert len(why) > 30, corpus


def test_no_module_under_src_can_be_skipped(tmp_path):
    # ⛔ The no-allow-list property, asserted behaviourally. ⚠️ My first
    # version grepped this module for `EXEMPT`, `ALLOW`, `IGNORE` — and failed
    # on `re.IGNORECASE`, which is the lexical-guard failure in miniature: it
    # was measuring spelling, and spelling is not the property. Ten modules at
    # ten depths, every one naming a corpus, and every one must be reported.
    names = [f"src/studyforge/{'sub/' * depth}m{depth}.py" for depth in range(10)]
    for where in names:
        path = tmp_path / where
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('"""The jPOS tutorial."""\n', encoding="utf-8")
    findings = check_source_names(tmp_path)
    assert sorted(f.path for f in findings) == sorted(names)


def test_the_product_suites_own_registry_is_this_registry():
    # ⛔ Two product copies of R1's registry — this floor's, and the one the product's tests
    #    read — must stay one rule after the tooling (and its twins test) has gone.
    from tests.harness import sources

    def shape(registry):
        return [(corpus, pattern.pattern, pattern.flags, why) for corpus, pattern, why in registry]

    assert shape(sources.KNOWN_SOURCES) == shape(KNOWN_SOURCES)


@pytest.mark.parametrize(
    "text", NAMES_A_SOURCE + NAMES_NO_SOURCE + SPLIT_ACROSS_A_BREAK + SPLIT_AND_NO_SOURCE
)
def test_the_product_suites_own_reader_reads_as_this_reader(text):
    # ⛔ The two readers are one rule too, not only the two registries.
    from tests.harness import sources

    assert sources.named_sources(text) == named_sources(text)
