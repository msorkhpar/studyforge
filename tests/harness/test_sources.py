"""Mirror of `tests/harness/sources.py`: the tooling original's registry tests, carried (`REL-02`).

⭐ **Every positive here is paired with the legitimate use it is one word
from.** A check that fires on `an ISO date` or on `a Java package segment`
would be switched off within a day, and then R1 would be enforced by nobody.
The whole-tree sweep stays with the tooling's floor, which `REL-03` sorts.
"""

from __future__ import annotations

import pytest

from tests.harness.sources import KNOWN_SOURCES, named_sources

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


def test_the_registry_is_inhabited_and_every_entry_carries_a_reason():
    # ⛔ Ruling 48 again: a registry that emptied would make every test above
    # that asserts *absence* pass, and only this one would notice.
    assert len(KNOWN_SOURCES) >= 4
    for corpus, pattern, why in KNOWN_SOURCES:
        assert corpus and why and pattern.pattern
        assert len(why) > 30, corpus
