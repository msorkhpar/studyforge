"""Mirror of `src/studyforge/skills/execution/buildfiles.py` (R12).

⭐ Pure string functions: a build file is found at any depth, its directory is the path less the
tool's file name, and a Gradle build without checksums is passed over where another has them.
"""

from __future__ import annotations

from studyforge.skills.execution.buildfiles import (
    GRADLE_CHECKSUMS,
    depth,
    directory_of,
    is_build_file,
    under,
    warmable,
)


def test_a_build_file_is_the_tool_s_own_at_any_depth_and_names_its_directory():
    assert is_build_file("a/b/pom.xml", "maven") and not is_build_file("a/xpom.xml", "maven")
    assert directory_of("a/b/pom.xml", "maven") == "a/b"
    assert directory_of("pom.xml", "maven") == ""


def test_depth_and_containment_count_path_parts():
    assert (depth(""), depth("a"), depth("a/b")) == (0, 1, 2)
    assert under("a/b.x", "a") and under("a.x", "") and not under("ab/c.x", "a")


def test_only_gradle_builds_with_checksums_are_warmable_where_any_has_them():
    names = {f"p/{GRADLE_CHECKSUMS}"}
    assert warmable("gradle", {"p", "e"}, names) == {"p"}
    assert warmable("gradle", {"p", "e"}, set()) == {"p", "e"}
    assert warmable("maven", {"p", "e"}, names) == {"p", "e"}
