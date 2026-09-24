"""Mirror of `src/studyforge/corpus/manifest/errors.py` (R12)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import studyforge
from studyforge.corpus.manifest import (
    ManifestError,
    errors,
    from_document,
    parse_content,
    parse_edits,
    parse_media,
)
from studyforge.corpus.manifest import edits as edits_module
from studyforge.corpus.manifest.content import parse as parse_module

#: The whole source tree, so the claim below is about the framework rather
#: than about the three files that happen to be open.
SOURCE_ROOT = Path(studyforge.__file__).parent

#: ⭐ Ruling 135's home for `_escape`, and the only two modules that may take
#: it. Written out rather than derived: a list built from what imports it
#: today would agree with whatever the tree happens to do.
MAY_NAME_ESCAPE = (
    "corpus/manifest/content/parse.py",
    "corpus/manifest/edits.py",
    "corpus/manifest/errors.py",
)

#: Every fault `_escape` distinguishes, with the phrase it answers. ⛔ The
#: phrases are spelled here, not read back from the function: a test that
#: asked the function what it says would pass whatever it said.
FAULTS = [
    ("/etc/passwd", "begins with a slash"),
    ("~/notes.md", "begins with a tilde"),
    ("../outside/x.md", "climbs above the root with '..'"),
    ("src/../../escape.md", "climbs above the root with '..'"),
]


def modules_naming_escape() -> list[str]:
    """Every module under `src/` that binds or reads the name `_escape`."""
    named = []
    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
        for node in ast.walk(tree):
            spellings = set()
            if isinstance(node, ast.Name):
                spellings.add(node.id)
            elif isinstance(node, ast.FunctionDef):
                spellings.add(node.name)
            elif isinstance(node, ast.alias):
                spellings.update({node.name, node.asname})
            if "_escape" in spellings:
                named.append(path.relative_to(SOURCE_ROOT).as_posix())
                break
    return named


#: Every public entry point, with an argument each one refuses. ⛔ One
#: exception type or a caller writes an `except` clause per module.
REFUSALS = [
    (parse_content, ({"include": []},)),
    (parse_media, ({"commit": "sometimes"},)),
    (parse_edits, ("not a list", parse_content({"include": ["*.md"]}))),
    (from_document, ({"corpus_api": 99},)),
]


def test_a_manifest_error_is_a_value_error():
    # ⚠️ `address`'s precedent, and this line is the whole of the manifest's
    # exposure to it: a *value* error subclasses `ValueError`. If the CTO
    # overrules the split, this is what changes.
    assert issubclass(ManifestError, ValueError)


@pytest.mark.parametrize("function,arguments", REFUSALS)
def test_every_public_entry_point_raises_this_one_type(function, arguments):
    with pytest.raises(ManifestError):
        function(*arguments)


@pytest.mark.parametrize("function,arguments", REFUSALS)
def test_nothing_repairs_a_value_quietly(function, arguments):
    # ⛔ R6. The alternative to raising is a manifest that means something
    # nobody wrote, and a corpus built from it that nobody can explain.
    try:
        function(*arguments)
    except ManifestError as error:
        assert str(error).strip(), f"{function.__name__} raised with no message"
    else:
        pytest.fail(f"{function.__name__} accepted a value it should refuse")


def test_a_refusal_names_the_field_and_the_permitted_class_but_not_the_value():
    # ⭐ A manifest is the first file an integrator writes by hand, so its
    # refusals are the first thing this framework ever says to them.
    # ⛔ Which is also why the value is not repeated back: any string in a
    # hand-written file can be an absolute path (R7, Ruling 14). The field and
    # the permitted set are what the reader cannot see; the value is in the
    # file in front of them.
    with pytest.raises(ManifestError) as raised:
        parse_media({"commit": "sometimes"})
    message = str(raised.value)
    assert "media.commit" in message
    assert "sometimes" not in message
    assert "always" in message


def test_a_refusal_over_a_closed_set_says_what_the_set_is():
    with pytest.raises(ManifestError) as raised:
        from_document({"corpus_api": 99})
    # ⚠️ The whole set, sorted; it grew to two when `content.not_material`
    # landed, to three when `media.max_files` did, to four when `runtimes`
    # did and to five when `narration` did. ⛔ Spelled out rather
    # than read from `KNOWN_CORPUS_API`: the point of the assertion is that the
    # refusal *names* the set, and one built from the set would say nothing
    # about what the message contains.
    assert "[1, 2, 3, 4, 5]" in str(raised.value)


def test_it_can_be_caught_as_a_value_error_by_a_caller_that_does_not_import_it():
    # A CLI that catches `ValueError` around "read this corpus" gets this for
    # free, which is what the shared base is for.
    with pytest.raises(ValueError, match="content"):
        parse_content(None)


# --- Ruling 135: the one phrase R7 lets a refusal say about a path ---------


@pytest.mark.parametrize("pattern,phrase", FAULTS)
def test_the_escaping_phrase_names_the_fault_and_repeats_no_part_of_the_path(pattern, phrase):
    # ⛔ Three faults, three sentences, and none of them is the path. This is
    # the assertion `content/test_init.py` used to make about a re-export; it
    # is here now because the function is, and it says more than the bridge
    # did — the bridge pinned one fault out of three.
    assert errors._escape(pattern) == phrase
    assert pattern not in errors._escape(pattern)


def test_both_refusals_say_it_with_the_one_function_W19_unified_them_onto():
    # ⭐ Not two copies that agree today. `is`, so a second definition
    # appearing anywhere fails here rather than drifting for a release.
    assert parse_module._escape is errors._escape
    assert edits_module._escape is errors._escape


def test_only_this_module_and_its_two_callers_name_the_escaping_phrase():
    # ⛔ Ruling 135's second half: it moved, and it did **not** become
    # public on the way. Nothing outside `corpus/manifest` may reach it, and
    # a fourth module wanting it is a contract decision, not an import.
    named = modules_naming_escape()
    # ⭐ The inhabitation assertion, before the claim: a sweep that found
    # nothing would pass the line below just as loudly.
    assert named, f"the sweep found no module at all under {SOURCE_ROOT.name}"
    assert named == list(MAY_NAME_ESCAPE), named


def test_the_sweep_above_would_notice(tmp_path, monkeypatch):
    # ⛔ All three readings. Reading 1 is the test above, on the
    # live tree. Reading 2 plants a fourth namer in the spelling the clause
    # did not picture — not a definition and not the name, but
    # an *aliased import*, which is exactly the bridge shape this row deleted.
    for name in MAY_NAME_ESCAPE:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text("def _escape(pattern):\n    return pattern\n", "utf-8")
    (tmp_path / "render" / "page").mkdir(parents=True)
    (tmp_path / "render" / "page" / "text.py").write_text(
        "from studyforge.corpus.manifest.errors import _escape as _e\n", encoding="utf-8"
    )
    monkeypatch.setattr("tests.studyforge.corpus.manifest.test_errors.SOURCE_ROOT", tmp_path)
    assert modules_naming_escape() == [*MAY_NAME_ESCAPE, "render/page/text.py"]

    # ⭐ Reading 3, the impossible subject: a tree where nothing names it must
    # read differently from both of the above, or the sweep is answering the
    # same thing to everything.
    empty = tmp_path / "elsewhere"
    empty.mkdir()
    (empty / "quiet.py").write_text("VALUE = 'escape'\n", encoding="utf-8")
    monkeypatch.setattr("tests.studyforge.corpus.manifest.test_errors.SOURCE_ROOT", empty)
    assert modules_naming_escape() == []
