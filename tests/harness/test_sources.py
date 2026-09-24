"""Mirror of `tests/harness/sources.py`: the tooling original's registry tests, carried.

⭐ **Every positive here is paired with the legitimate use it is one word
from.** A check that fires on `an ISO date` or on `a Java package segment`
would be switched off within a day, and then R1 would be enforced by nobody.
The whole-tree sweep stays with the tooling's floor.
"""

from __future__ import annotations

import pytest

from tests.harness.sources import KNOWN_SOURCES, named_sources

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


def test_the_finding_names_the_role_and_never_the_corpus():
    # ⛔ A finding that quoted the name would put it in the build log, and
    # §7c's own sentence is that the next reader takes a name as licence.
    (_line, corpus, why) = named_sources("ISO-8583's material carries 96 strings")[0]
    assert "8583" not in corpus and "8583" not in why
    assert corpus == "a v2 target"


def test_the_registry_is_inhabited_and_every_entry_carries_a_reason():
    # ⛔ Again, a sweep states its denominator: a registry that emptied would make every test above
    # that asserts *absence* pass, and only this one would notice.
    assert len(KNOWN_SOURCES) >= 4
    for corpus, pattern, why in KNOWN_SOURCES:
        assert corpus and why and pattern.pattern
        assert len(why) > 30, corpus
