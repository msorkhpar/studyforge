"""What a path inside the source may be — the permitted set, exercised (Ruling 44).

⭐ **Every negative here is paired with the positive it is one character from.**
A rule that refuses `~/x` is worth nothing if it also refuses `x`, and a rule
that refuses `C:/Users/<name>` is worth nothing if it also refuses `notes.md`;
the pairing is what shows the rule biting on the thing it names.
"""

import pytest

from studyforge.sourcepath import is_source_path, source_path_fault

HOME = "/" + "home/jane"
USERS = "/" + "Users/jane"

#: `(value, the fault it is named by)`. ⛔ Three of these — the tilde forms
#: aside — were refused by **neither** of the two forbidden lists this rule
#: replaced, and one of them, `\\host\home\<name>`, was not in Ruling 44's
#: table either: this module's own probe found it while measuring the two the
#: ruling named.
NOT_A_SOURCE_PATH = [
    ("", "an empty path"),
    ("   ", "an empty path"),
    ("/", "an absolute path"),
    (f"{HOME}/material/README.md", "an absolute path"),
    ("/export" + HOME + "/material/README.md", "an absolute path"),
    ("~/material/README.md", "a path rooted at a home directory"),
    ("~" + "jane/material/README.md", "a path rooted at a home directory"),
    ("../outside/x.md", "a path leaving the source root"),
    ("a/../../b.md", "a path leaving the source root"),
    ("C:" + USERS + "/material/README.md", "a path carrying a drive letter or scheme"),
    ("file:///etc/passwd", "a path carrying a drive letter or scheme"),
    (r"\\host\home\jane\README.md", "a path written with Windows separators"),
    (r"material\jane\README.md", "a path written with Windows separators"),
]

IS_A_SOURCE_PATH = [
    "README.md",
    "src/one.md",
    "basics/01/README.md",
    "./src/one.md",
    "a/b/c/d/e/f.md",
    "material-2026/lesson_1.md",
    "docs/~drafts.md",
    "src/home/index.md",
]


@pytest.mark.parametrize(("value", "fault"), NOT_A_SOURCE_PATH)
def test_the_permitted_set_excludes_it_and_says_which_requirement_it_missed(value, fault):
    assert source_path_fault(value) == fault
    assert not is_source_path(value)


@pytest.mark.parametrize("value", IS_A_SOURCE_PATH)
def test_and_a_location_inside_the_source_passes(value):
    # ⚠️ The negative control for the table above, run as its own test rather
    # than trusted. `src/home/index.md` and `docs/~drafts.md` are the two rows
    # that matter: the home rule and the tilde rule must be anchored at the
    # front of the path, or an ordinary directory named `home` and an ordinary
    # file whose name starts with a tilde stop being placeable.
    assert source_path_fault(value) is None
    assert is_source_path(value)


@pytest.mark.parametrize(("value", "_fault"), NOT_A_SOURCE_PATH)
def test_the_fault_never_reproduces_the_value(value, _fault):
    # ⛔ Every value this rule refuses is a candidate home directory, so the
    # noun phrase it returns must carry nothing from it (R7). Checked against
    # the segments, not the whole string, because a fault that echoed only the
    # account name would still be the leak.
    fault = source_path_fault(value)
    assert fault is not None
    for segment in value.replace("\\", "/").split("/"):
        if len(segment) > 2:
            assert segment not in fault


@pytest.mark.parametrize("value", [None, 3, ["src/one.md"], b"src/one.md"])
def test_a_value_that_is_not_a_str_is_not_a_source_path(value):
    # ⭐ `is_source_path` answers for any object because its callers read
    # decoded JSON; `source_path_fault` is typed `str` and its callers check
    # the type first, each with their own sentence about what they wanted.
    assert not is_source_path(value)
