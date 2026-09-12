"""Mirror of `src/studyforge/corpus/manifest/edits.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.corpus.manifest import ManifestError, parse_content, parse_edits

#: The Java corpus's real declaration — the one existing-file change R3 permits
#: there, and the one `OPS-05` asserts against.
POM_EDIT = {
    "path": "pom.xml",
    "kind": "insert-line",
    "anchor": "<modules>",
    "content": "  <module>practice</module>",
    "why": "Maven compiles only what sits on a source root (spec §7).",
}

#: A content policy under which the lesson READMEs are material and `pom.xml`
#: is not — which is the Java corpus's shape, and what makes the pom edit legal
#: while a README edit is not.
JAVA_CONTENT = parse_content({"include": ["*/*/README*.md"], "exclude": []})


def edits(*entries):
    return parse_edits(list(entries), JAVA_CONTENT)


def test_an_empty_list_is_the_normal_case():
    # ⭐ Two of the four designed shapes declare nothing, and a purely
    # additive source should be able to keep it that way.
    assert parse_edits([], JAVA_CONTENT) == ()
    assert parse_edits(None, JAVA_CONTENT) == ()


def test_a_declared_edit_is_carried_verbatim():
    (edit,) = edits(POM_EDIT)
    assert edit.path == "pom.xml"
    assert edit.anchor == "<modules>"
    assert edit.content == "  <module>practice</module>"
    assert "source root" in edit.why


def test_the_reverse_of_a_declared_edit_is_recorded():
    # ⭐ An onboarding that cannot be undone is one nobody will run against a
    # repository they care about. ⚠️ Derived, not a second field — the
    # declaration already records the insertion exactly, and a second field
    # would be a second thing to keep in step.
    (edit,) = edits(POM_EDIT)
    assert edit.reversal.path == "pom.xml"
    assert edit.reversal.kind == "remove-line"
    assert edit.reversal.content == edit.content
    assert "remove-line" in str(edit.reversal)


# --- the three R3 never permits, however declared ---------------------------


@pytest.mark.parametrize("path", [".gitignore", ".hgignore"])
def test_the_root_ignore_file_is_never_editable(path):
    # ⛔ Write a new ignore file INSIDE a generated directory instead — which
    # is what FND-02 did for a generated directory, and it works.
    with pytest.raises(ManifestError, match="root ignore file"):
        edits({**POM_EDIT, "path": path})


def test_an_ignore_file_inside_a_generated_directory_is_not_the_root_one():
    # ⚠️ The prohibition is about the REPOSITORY's ignore file. The mechanism
    # R3 leaves open must stay open, or the rule forbids its own remedy.
    (edit,) = edits({**POM_EDIT, "path": "practice/.gitignore"})
    assert edit.path == "practice/.gitignore"


@pytest.mark.parametrize(
    "path", [".gitattributes", ".gitmodules", ".mailmap", ".git/config", "nested/.git/hooks/x"]
)
def test_version_control_configuration_is_never_editable(path):
    with pytest.raises(ManifestError, match="version-control configuration"):
        edits({**POM_EDIT, "path": path})


@pytest.mark.parametrize(
    "path", ["basics/01-getting-started/README.md", "advanced/02-x/README_2.1.md"]
)
def test_a_file_the_reader_depends_on_as_content_is_never_editable(path):
    # ⭐ The prohibition that used to be unenforceable prose, and is checkable
    # now only because `content` exists: a file the corpus's own policy
    # classifies as INCLUDED **is** content. ⚠️ The ISO corpus is the live
    # case — its `permitted_edits` is `[]` and its `README.md` is material, so
    # this holds it there structurally rather than by anyone remembering.
    with pytest.raises(ManifestError, match="depends on as content"):
        edits({**POM_EDIT, "path": path})


def test_the_same_prohibition_does_not_fire_on_a_file_that_is_not_content():
    # The pom is matched by no include glob, so editing it stays legal.
    assert edits(POM_EDIT)[0].path == "pom.xml"


# --- shape ------------------------------------------------------------------


@pytest.mark.parametrize("field", ["path", "kind", "anchor", "content", "why"])
def test_every_field_is_required(field):
    entry = {key: value for key, value in POM_EDIT.items() if key != field}
    with pytest.raises(ManifestError, match=f"{field} must be a non-empty str"):
        edits(entry)


def test_an_unknown_kind_is_refused_rather_than_guessed_at():
    with pytest.raises(ManifestError, match="kind must be one of"):
        edits({**POM_EDIT, "kind": "replace-file"})


def test_an_edit_must_say_why_at_length():
    with pytest.raises(ManifestError, match="characters of reason"):
        edits({**POM_EDIT, "why": "needed"})


def test_the_same_file_cannot_be_declared_twice():
    with pytest.raises(ManifestError, match="twice"):
        edits(POM_EDIT, POM_EDIT)


@pytest.mark.parametrize("path", ["/etc/passwd", "../outside/pom.xml"])
def test_an_edit_may_not_reach_outside_the_source_root(path):
    with pytest.raises(ManifestError, match="stay inside it"):
        edits({**POM_EDIT, "path": path})


@pytest.mark.parametrize(
    "path,phrase",
    [
        ("/etc/passwd", "begins with a slash"),
        ("../outside/pom.xml", "climbs above the root with '..'"),
        ("src/../../pom.xml", "climbs above the root with '..'"),
    ],
)
def test_the_twin_refusal_says_it_in_the_same_words_as_the_content_one(path, phrase):
    # ⛔ W19 unified the middle clause onto one function and `W59` moved that
    # function out of `content`; this is the byte-level pin at the second
    # site, so a move that quietly changed what either caller emits fails
    # here. ⭐ It is the same sentence as `content/test_parse.py`'s with a
    # different field name in front of it.
    with pytest.raises(ManifestError) as raised:
        edits({**POM_EDIT, "path": path})
    assert str(raised.value) == (
        f"permitted_edits path must be relative to the source root and stay "
        f"inside it; it {phrase}, and it is not reproduced here because that "
        f"shape is where a home directory lives"
    )
    assert path not in str(raised.value)


@pytest.mark.parametrize("value", ["pom.xml", 7, {"path": "pom.xml"}])
def test_permitted_edits_must_be_a_list(value):
    with pytest.raises(ManifestError, match="must be a list"):
        parse_edits(value, JAVA_CONTENT)


def test_an_unknown_key_in_an_entry_is_refused():
    with pytest.raises(ManifestError, match="unknown key"):
        edits({**POM_EDIT, "reverse": "remove the line"})
