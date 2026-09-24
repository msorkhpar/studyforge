"""Mirror of `src/studyforge/corpus/manifest/content/parse.py` (R12).

⛔ Every test here is about what a declaration must look like to be read at
all. What a **built** policy then answers is `test_policy.py`'s.
"""

from __future__ import annotations

import pytest

from studyforge.corpus.manifest import MIN_WHY_CHARS, ManifestError, NotMaterial, parse_content
from tests.studyforge.corpus.manifest.content.policies import WHY, policy, scaffolding

#: ⭐ The three worked examples of `not_material`, copied rather than paraphrased. Rule 1a
#: was derived from what a loose glob does to rule 4, **not** fitted to these;
#: they are here so that a later tightening of the rule that would have
#: refused the ruling's own examples fails loudly.
NOT_MATERIAL_GLOBS = ("docs/studyforge/*", "LICENSE", ".gitignore")


@pytest.mark.parametrize("include", [[], None, "src/*.md", [""], [7]])
def test_a_corpus_that_includes_nothing_is_refused(include):
    with pytest.raises(ManifestError, match="content.include"):
        policy(include=include)


def test_an_exclusion_must_say_why():
    with pytest.raises(ManifestError, match="why this file is withheld"):
        policy(exclude=[{"path": "src/ISO.md"}])


def test_an_exclusion_whose_reason_is_a_token_is_refused():
    # ⛔ Same argument and same number the quality floor already uses for a
    # size exception: it only stops `"why": "n/a"` being a way through.
    with pytest.raises(ManifestError, match=f"at least {MIN_WHY_CHARS} characters"):
        policy(exclude=[{"path": "src/ISO.md", "why": "aggregate"}])


def test_an_exclusion_names_one_file_and_never_a_pattern():
    # ⭐ One justification covering a pattern is one justification for a set
    # whose membership changes when somebody adds a file.
    with pytest.raises(ManifestError, match="must name one file"):
        policy(exclude=[{"path": "src/*.md", "why": "every aggregate, all at once, forever"}])


def test_the_same_file_cannot_be_excluded_twice():
    entry = {"path": "src/ISO.md", "why": "whole-series aggregate, declared once too often"}
    with pytest.raises(ManifestError, match=r"already excluded by content\.exclude\[0\]"):
        policy(exclude=[entry, entry])


@pytest.mark.parametrize(
    "pattern", ["/etc/passwd", "../outside/*.md", "~/notes.md", "src/../../escape.md"]
)
def test_a_path_that_escapes_the_source_root_is_refused(pattern):
    with pytest.raises(ManifestError, match="stay inside it"):
        policy(include=[pattern])


#: The three faults, and the phrase each one is named by. ⚠️ Pinned because
#: a refusal is a **format**: a later move of the function that produces the
#: middle clause, and `match="stay inside it"` above would have read green
#: through a transposition of the three phrases.
ESCAPE_PHRASES = [
    ("/etc/passwd", "begins with a slash"),
    ("~/notes.md", "begins with a tilde"),
    ("../outside/x.md", "climbs above the root with '..'"),
    ("src/../../escape.md", "climbs above the root with '..'"),
]


@pytest.mark.parametrize("pattern,phrase", ESCAPE_PHRASES)
def test_the_refusal_says_which_way_the_path_left_and_says_it_the_same_way(pattern, phrase):
    # ⛔ The whole sentence, byte for byte, at the site that emits it — not
    # the substring that survives any rewording of it.
    with pytest.raises(ManifestError) as raised:
        policy(include=[pattern])
    assert str(raised.value) == (
        f"content.include[0] must be relative to the source root and stay inside "
        f"it; it {phrase}, and it is not reproduced here because that shape is "
        f"where a home directory lives"
    )
    assert pattern not in str(raised.value)


def test_an_unknown_key_in_content_is_refused():
    with pytest.raises(ManifestError, match="unknown key"):
        parse_content({"include": ["*.md"], "exclude": [], "ignore": ["x"]})


@pytest.mark.parametrize("value", [None, [], "content", 7])
def test_content_must_be_an_object(value):
    with pytest.raises(ManifestError, match="'content' must be an object"):
        parse_content(value)


@pytest.mark.parametrize("glob", NOT_MATERIAL_GLOBS)
def test_the_rulings_own_three_examples_are_accepted(glob):
    assert scaffolding((glob, WHY)).not_material == (NotMaterial(glob, WHY),)


# --- rule 1a: an exact path, or one directory's wildcard --------------------


@pytest.mark.parametrize(
    "glob", ["docs/studyforge/*", "docs/studyforge/**", "src/notes/*.md", "a/b/c/*"]
)
def test_a_wildcard_under_a_directory_is_accepted(glob):
    assert scaffolding((glob, WHY)).not_material == (NotMaterial(glob, WHY),)


@pytest.mark.parametrize("glob", ["LICENSE", ".gitignore", "docs/studyforge/notes.md"])
def test_an_exact_path_is_accepted(glob):
    assert scaffolding((glob, WHY)).not_material == (NotMaterial(glob, WHY),)


@pytest.mark.parametrize("glob", ["[CLR]*", "*.md", "*", "[A-Z]*", "?ICENSE", "docs*/notes.md"])
def test_a_wildcard_with_no_directory_before_it_is_refused(glob):
    # ⛔ **`[CLR]*` is the measured case and it is refused.** It covers three
    # root files only because a fourth happens to begin with another letter —
    # the collision encoded rather than the intent — and a `why` cannot be
    # true of a file nobody has written yet.
    with pytest.raises(ManifestError, match="wildcard where no directory precedes it"):
        scaffolding((glob, WHY))


def test_a_wildcard_inside_a_directory_name_is_refused():
    # ⚠️ The wildcard must lie *under* a directory, not *span* one: the fixed
    # prefix of `docs/study*/x.md` is not a directory anybody declared.
    with pytest.raises(ManifestError, match="wildcard where no directory precedes it"):
        scaffolding(("docs/study*/x.md", WHY))


def test_the_rule_1a_refusal_does_not_reproduce_the_pattern():
    # ⭐ The actionable half is which rule was broken; the author has what
    # they wrote in front of them, and a refusal that echoes a path is where
    # a home directory ends up in a build log (R7).
    with pytest.raises(ManifestError) as raised:
        scaffolding(("[CLR]*", WHY))
    assert "[CLR]*" not in str(raised.value)


# --- what the third state refuses -------------------------------------------


def test_a_not_material_entry_must_say_why():
    # ⛔ And it may not say "withheld", because nothing is: every declaration
    # that the framework will not read a file needs a reason, and this one's
    # reason is a different sentence from an exclusion's.
    with pytest.raises(ManifestError, match="why this file was never material"):
        policy(not_material=[{"glob": "LICENSE"}])


def test_a_nineteen_character_reason_is_refused_and_a_twenty_character_one_is_not():
    # ⛔ The boundary in literal characters, never `MIN_WHY_CHARS * "x"`: an
    # assertion built from the constant it pins passes whatever the constant
    # becomes.
    short, long = "the repo's own note", "the repo's own notes"
    assert (len(short), len(long)) == (19, 20)
    with pytest.raises(ManifestError, match="at least 20 characters"):
        scaffolding(("LICENSE", short))
    assert scaffolding(("LICENSE", long)).not_material[0].why == long


def test_the_length_the_module_enforces_is_the_one_this_file_pins():
    # ⚠️ The one place the constant is read, and it is read to catch a drift
    # between the module and the two literals above rather than to build them.
    assert MIN_WHY_CHARS == 20


def test_the_same_glob_cannot_be_declared_twice():
    with pytest.raises(ManifestError, match=r"already declared by content\.not_material\[0\]"):
        scaffolding(("LICENSE", WHY), ("LICENSE", WHY))


def test_an_unknown_key_in_a_not_material_entry_is_refused():
    with pytest.raises(ManifestError, match="unknown key"):
        policy(not_material=[{"path": "LICENSE", "why": WHY}])


@pytest.mark.parametrize("declared", [None, "LICENSE", 7, {}])
def test_not_material_must_be_a_list(declared):
    with pytest.raises(ManifestError, match="'content.not_material' must be a list"):
        policy(not_material=declared)


@pytest.mark.parametrize("entry", [None, "LICENSE", 7, []])
def test_a_not_material_entry_must_be_an_object(entry):
    with pytest.raises(ManifestError, match=r"content\.not_material\[0\] must be an object"):
        policy(not_material=[entry])


@pytest.mark.parametrize("glob", [None, "", 7, ["LICENSE"]])
def test_a_not_material_glob_must_be_a_non_empty_string(glob):
    with pytest.raises(ManifestError, match=r"content\.not_material\[0\]\.glob"):
        policy(not_material=[{"glob": glob, "why": WHY}])


@pytest.mark.parametrize("glob", ["/etc/passwd", "../outside/*", "~/notes.md"])
def test_a_not_material_glob_that_escapes_the_source_root_is_refused(glob):
    with pytest.raises(ManifestError, match="stay inside it"):
        scaffolding((glob, WHY))


def test_a_bracket_class_is_a_wildcard_wherever_it_falls():
    # ⛔ **Found by a mutant surviving.** `WILDCARDS` names three
    # characters and only two of them were ever exercised in a position that
    # tells them apart: replacing `[` with `]` left the whole suite green.
    # ⭐ Both halves are asserted, because `[` is read by two different rules.
    #
    # Rule 1a: the class is a wildcard, so what precedes it must be a
    # directory — accepted under one, refused at the root.
    assert scaffolding(("docs/[ab]*.md", WHY)).not_material[0].glob == "docs/[ab]*.md"
    with pytest.raises(ManifestError, match="wildcard where no directory precedes it"):
        scaffolding(("[ab]*.md", WHY))


def test_an_exclusion_naming_an_unclosed_bracket_is_still_a_glob():
    # ⚠️ The other rule that reads `WILDCARDS`, and the case that pins `[`
    # by itself: an exclusion carries no closing bracket to be mistaken for
    # the wildcard, so only `[` can refuse this one.
    with pytest.raises(ManifestError, match="must name one file"):
        policy(exclude=[{"path": "src/[abc.md", "why": "a bracket class, spelled by mistake"}])
