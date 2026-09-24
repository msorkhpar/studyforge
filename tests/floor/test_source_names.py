"""Mirror of `tools/quality/source_names.py` (R12).

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

#: One spelling per registry entry, plus the spellings the reviewer's grep
#: missed. ⚠️ The last two are the whole reason this is a module rather than a
#: seventh alternative in a shell pattern: measured 2026-09-09, rubric §7c
#: found 7 hits in `src/` and this registry found 19, and every one of the
#: twelve extra was a corpus named in English rather than by its slug.
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
    # legal there without anything being excused. ⛔ There is nowhere to add a
    # module to, which is the property being asserted.
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
