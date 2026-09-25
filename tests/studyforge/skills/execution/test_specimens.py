"""Mirror of `src/studyforge/skills/execution/specimens.py` (R12).

⭐ Each claim is read on a small build laid out in memory, where every file's
text is chosen so exactly one resolution rule decides what is copied.
"""

from __future__ import annotations

from studyforge.skills.execution import specimens

M = "src/main/java/p"
T = "src/test/java/p"


def build(files: dict[str, str]):
    """`held`, `modules` and a reader for a build laid out from `files`."""
    held = [(where, len(text.encode("utf-8"))) for where, text in files.items()]
    return held, files.__getitem__


def chosen(files: dict[str, str], modules: list[str]) -> dict[str, specimens.Specimen]:
    held, text = build(files)
    return {one.module: one for one in specimens.per_module("java", held, modules, text)}


def test_each_module_gets_its_own_source_and_test_and_the_classes_its_test_names():
    found = chosen(
        {
            f"a/{M}/Tiny.java": "class Tiny {}",
            f"a/{M}/Shape.java": "class Shape { double area() { return 0; } }",
            f"a/{T}/ShapeTest.java": "class ShapeTest { Shape s; }",
            f"b/{M}/Other.java": "class Other {}",
            f"b/{T}/OtherTest.java": "class OtherTest { Other o; }",
        },
        ["", "a", "b"],
    )
    assert sorted(found) == ["a", "b"]
    assert found["a"].source == f"a/{M}/Tiny.java"
    assert found["a"].test == f"a/{T}/ShapeTest.java"
    assert found["a"].support == (f"a/{M}/Shape.java",), "the test compiles only with what it names"
    assert found["b"].files() == (f"b/{M}/Other.java", f"b/{T}/OtherTest.java")


def test_a_name_resolves_in_the_naming_files_own_module_first():
    found = chosen(
        {
            f"a/{M}/Shape.java": "class Shape {}",
            f"a/{T}/ShapeTest.java": "class ShapeTest { Shape s; }",
            f"b/{M}/Shape.java": "class Shape { int sides; }",
            f"b/{T}/BTest.java": "class BTest {}",
        },
        ["a", "b"],
    )
    assert f"b/{M}/Shape.java" not in found["a"].files()


def test_another_modules_file_is_reached_only_through_a_mention_of_its_directory():
    files = {
        "base/src/main/java/base/Util.java": "package base; public class Util {}",
        "base/src/test/java/base/UtilTest.java": "class UtilTest { Util u; }",
        "lesson/src/main/java/lesson/Person.java": "class Person {}",
        "lesson/src/test/java/lesson/PersonTest.java": "class PersonTest { Person p; }",
        "app/src/main/java/app/App.java": "class App {}",
        "app/src/test/java/app/AppTest.java": (
            "import base.Util;\nclass AppTest { Util u; /* a Person, by the way */ }"
        ),
    }
    found = chosen(files, ["app", "base", "lesson"])
    assert "base/src/main/java/base/Util.java" in found["app"].support, "an import reaches it"
    assert "lesson/src/main/java/lesson/Person.java" not in found["app"].files(), (
        "a word that happens to be another lesson's class copies nothing"
    )


def test_a_source_never_resolves_a_name_to_a_test():
    found = chosen(
        {
            f"{M}/Main.java": "class Main { /* see Helper */ }",
            f"{T}/MainTest.java": "class MainTest {}",
            f"{T}/Helper.java": "class Helper { int one; int two; }",
        },
        [""],
    )
    assert (found[""].source, found[""].test) == (f"{M}/Main.java", f"{T}/MainTest.java")
    assert found[""].support == (), "a test is not on a source's classpath"


def test_a_second_type_a_file_declares_is_found_by_its_name():
    found = chosen(
        {
            f"{M}/Z.java": "class Z {}",
            f"{M}/Shapes.java": "class Shapes {}\nclass Square {}",
            f"{T}/SquareTest.java": "class SquareTest { Square s; }",
        },
        [""],
    )
    assert found[""].source == f"{M}/Z.java"
    assert found[""].support == (f"{M}/Shapes.java",)


def test_the_smallest_copy_wins_not_the_smallest_file():
    found = chosen(
        {
            f"{M}/Big.java": "class Big {}" + " " * 60,
            f"{M}/A.java": "class A { Big b; }" + " " * 40,
            f"{M}/Small.java": "class Small { A a; }",
            f"{M}/Alone.java": "class Alone { int x; int y; int z; }",
            f"{T}/AloneTest.java": "class AloneTest { Alone a; }",
        },
        [""],
    )
    assert found[""].source == f"{M}/Alone.java", "Small's copy carries A and Big"


def test_a_module_with_nothing_in_the_language_gets_no_specimen():
    found = chosen(
        {f"a/{M}/A.java": "class A {}", f"a/{T}/ATest.java": "class ATest {}"}, ["a", "empty"]
    )
    assert sorted(found) == ["a"]


def test_a_module_with_only_a_source_is_primed_with_that_source():
    found = chosen(
        {f"a/{M}/A.java": "class A {}", f"b/{T}/BTest.java": "class BTest {}"}, ["a", "b"]
    )
    assert (found["a"].source, found["a"].test) == (f"a/{M}/A.java", None)
    assert (found["b"].source, found["b"].test) == (None, f"b/{T}/BTest.java")


def test_a_file_is_in_the_deepest_module_that_holds_it():
    assert specimens.module_of("a/b/src/X.java", ["", "a", "a/b"]) == "a/b"
    assert specimens.module_of("c/src/X.java", ["", "a"]) == ""
    assert specimens.module_of("ab/X.java", ["a"]) == "", "a prefix is a directory, not a string"


def test_an_empty_file_is_never_a_specimen():
    found = chosen(
        {f"{M}/Empty.java": "", f"{M}/A.java": "class A {}", f"{T}/ATest.java": "class ATest {}"},
        [""],
    )
    assert f"{M}/Empty.java" not in found[""].files()
