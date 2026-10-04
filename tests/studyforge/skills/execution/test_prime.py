"""Mirror of `src/studyforge/skills/execution/prime.py` (R12).

⛔ **The claim under test is a negative one**: an empty prime primes nothing
while appearing to succeed, so every refusal is asserted with the clean case
beside it. ⭐ Nothing here authors a build file or a test framework — the
selection is out of the corpus's own material, so the assertions are about
*which* file was chosen and never about what was written into one.
"""

from __future__ import annotations

import pytest

from studyforge.exercise.bundle import emit, write
from studyforge.skills.execution import prime, specimens
from tests.studyforge.exercise.bundle import dependency
from tests.studyforge.skills.execution.contracts import corpus

#: The runtimes the synthetic component seeds a cache for.
SEEDED = ("gradle", "maven")


def put(path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_a_corpus_with_a_build_file_a_source_and_a_test_is_primed(tmp_path):
    made = prime.prime_for(corpus(tmp_path), ("java", "maven"), seeded=SEEDED)
    assert made.build_files == ("sources/app/pom.xml",)
    assert [one.language for one in made.specimens] == ["java"]
    assert made.specimens[0].source.endswith("Demo.java")
    assert made.specimens[0].test.endswith("DemoTest.java")


def test_every_selected_path_is_a_file_the_corpus_already_carried(tmp_path):
    root = corpus(tmp_path)
    made = prime.prime_for(root, ("java", "maven"), seeded=SEEDED)
    for _, origin in made.copies():
        assert (root / origin).is_file(), origin


def test_the_copies_preserve_the_package_directory(tmp_path):
    # ⚠️ A JVM source moved out of its package no longer compiles, so the
    # relative path is part of the specimen rather than decoration.
    made = prime.prime_for(corpus(tmp_path), ("java", "maven"), seeded=SEEDED)
    assert "src/main/java/demo/Demo.java" in made.specimens[0].source


def test_a_seeded_runtime_with_no_build_file_is_refused_by_name(tmp_path):
    root = corpus(tmp_path)
    (root / "sources/app/pom.xml").unlink()
    with pytest.raises(prime.PrimeRefused) as refused:
        prime.prime_for(root, ("java", "maven"), seeded=SEEDED)
    assert "maven" in str(refused.value) and "build files" in str(refused.value)


def test_a_runtime_the_component_does_not_seed_is_not_asked_for_a_build_file(tmp_path):
    # ⭐ Both directions, and the reason: a corpus of plain scripts is never
    # asked for a build file it has no reason to own. Which runtimes owe one is
    # the CONTRACT's answer, arriving as `seeded`.
    root = corpus(tmp_path)
    (root / "sources/app/run.py").write_text("def one():\n    return 1\n", encoding="utf-8")
    (root / "sources/app/test_run.py").write_text("def test_one():\n    pass\n", encoding="utf-8")
    made = prime.prime_for(root, ("python",), seeded=SEEDED)
    # ⭐ And it gets no project: the component warms nothing for a runtime it
    # does not seed, and anything else at the prime's top is refused.
    assert made.projects == () and made.copies() == ()


def test_a_declared_language_with_no_source_is_refused(tmp_path):
    root = corpus(tmp_path, java=False)
    with pytest.raises(prime.PrimeRefused) as refused:
        prime.prime_for(root, ("java", "maven"), seeded=SEEDED)
    assert "no source" in str(refused.value)


def test_a_declared_language_with_no_test_is_refused(tmp_path):
    root = corpus(tmp_path)
    (root / "sources/app/src/test/java/demo/DemoTest.java").unlink()
    with pytest.raises(prime.PrimeRefused) as refused:
        prime.prime_for(root, ("java", "maven"), seeded=SEEDED)
    assert "no test" in str(refused.value)


def test_every_missing_piece_is_named_at_once_rather_than_one_per_round_trip(tmp_path):
    root = corpus(tmp_path)
    (root / "sources/app/pom.xml").unlink()
    (root / "sources/app/src/test/java/demo/DemoTest.java").unlink()
    (root / "sources/app/settings.gradle").write_text("", encoding="utf-8")
    with pytest.raises(prime.PrimeRefused) as refused:
        prime.prime_for(root, ("gradle", "java", "maven"), seeded=SEEDED)
    said = str(refused.value)
    assert "maven is declared" in said and "no test" in said


def test_an_empty_file_is_never_selected_as_a_specimen(tmp_path):
    # ⛔ The whole point: an empty source primes nothing while looking like one.
    root = corpus(tmp_path)
    (root / "sources/app/src/main/java/demo/Empty.java").write_text("", encoding="utf-8")
    made = prime.prime_for(root, ("java", "maven"), seeded=SEEDED)
    assert not made.specimens[0].source.endswith("Empty.java")


def test_the_smallest_real_source_is_the_one_selected(tmp_path):
    root = corpus(tmp_path)
    (root / "sources/app/src/main/java/demo/Big.java").write_text(
        "package demo;\n" + "// filler\n" * 80, encoding="utf-8"
    )
    made = prime.prime_for(root, ("java", "maven"), seeded=SEEDED)
    assert made.specimens[0].source.endswith("Demo.java")


def test_build_output_and_dependency_trees_are_never_selected_from(tmp_path):
    root = corpus(tmp_path)
    for skipped in ("target", "node_modules"):
        where = root / "sources/app" / skipped / "demo"
        where.mkdir(parents=True)
        (where / "Tiny.java").write_text("class T{}\n", encoding="utf-8")
    made = prime.prime_for(root, ("java", "maven"), seeded=SEEDED)
    assert "target" not in made.specimens[0].source
    assert "node_modules" not in made.specimens[0].source


def test_a_build_file_is_found_at_any_depth(tmp_path):
    # ⚠️ A multi-module project keeps its build files beside each module.
    root = corpus(tmp_path)
    (root / "sources/app/nested").mkdir()
    (root / "sources/app/nested/pom.xml").write_text("<project/>\n", encoding="utf-8")
    made = prime.prime_for(root, ("java", "maven"), seeded=SEEDED)
    assert "sources/app/nested/pom.xml" in made.build_files


@pytest.mark.parametrize(
    "where",
    [
        "src/test/java/demo/A.java",
        "spec/demo/A.java",
        "src/main/java/demo/ATest.java",
        "src/main/java/demo/ATests.java",
        "src/a_test.py",
        "src/test_a.py",
        "src/a.test.js",
        "src/a.spec.js",
    ],
)
def test_these_paths_read_as_tests(where):
    assert specimens.is_a_test(where)


@pytest.mark.parametrize(
    "where",
    ["src/main/java/demo/A.java", "src/latest/A.java", "src/contest.py", "src/protest.js"],
)
def test_these_paths_do_not(where):
    # ⚠️ The negative control, and it is not decoration: a stem check that
    # matched `contest` or `latest` would select ordinary code as a test.
    assert not specimens.is_a_test(where)


def test_a_root_that_is_not_a_path_is_refused_without_quoting_it(tmp_path):
    with pytest.raises(prime.PrimeRefused) as refused:
        prime.prime_for("/some/absolute/place", ("java",), seeded=SEEDED)
    assert "/some/absolute/place" not in str(refused.value)


def test_the_document_names_every_file_the_prime_carries(tmp_path):
    made = prime.prime_for(corpus(tmp_path), ("java", "maven"), seeded=SEEDED)
    named = set()
    for project in made.document()["projects"]:
        named |= set(project["build_files"])
        named |= {one["source"] for one in project["specimens"]}
        named |= {one["test"] for one in project["specimens"]}
    assert named == {origin for _, origin in made.copies()}


# --------------------------------------------------------------------------
# ⛔ The component's layout — one project per seeded tool
# --------------------------------------------------------------------------


def test_each_project_is_copied_under_its_seed_key_re_rooted_at_its_build(tmp_path):
    made = prime.prime_for(corpus(tmp_path), ("java", "maven"), seeded=SEEDED)
    assert made.copies() == (
        ("maven/pom.xml", "sources/app/pom.xml"),
        ("maven/src/main/java/demo/Demo.java", "sources/app/src/main/java/demo/Demo.java"),
        (
            "maven/src/test/java/demo/DemoTest.java",
            "sources/app/src/test/java/demo/DemoTest.java",
        ),
    )


def test_the_prime_top_is_only_ever_a_seed_key(tmp_path):
    # ⭐ The directory names are the contract's (`runner.prime.seeds`), never
    # this module's: a tool the contract does not seed gets no directory.
    root = corpus(tmp_path)
    (root / "sources/app/settings.gradle").write_text("", encoding="utf-8")
    made = prime.prime_for(root, ("gradle", "java", "maven"), seeded=("maven",))
    assert {inside.split("/")[0] for inside, _ in made.copies()} == {"maven"}


def test_a_build_at_the_corpus_root_is_re_rooted_to_nothing(tmp_path):
    put(tmp_path / "pom.xml", "<project/>\n")
    put(tmp_path / "src/main/java/a/A.java", "package a;\nclass A {}\n")
    put(tmp_path / "src/test/java/a/ATest.java", "package a;\nclass ATest {}\n")
    made = prime.prime_for(tmp_path, ("java", "maven"), seeded=SEEDED)
    assert made.projects[0].root == ""
    assert ("maven/src/main/java/a/A.java", "src/main/java/a/A.java") in made.copies()


def test_a_specimen_outside_the_build_is_never_selected(tmp_path):
    # ⚠️ A source outside the build's directory has no place in its project,
    # however small it is: it would not compile where the build looks.
    root = corpus(tmp_path)
    put(root / "notes/X.java", "class X{}\n")
    put(root / "notes/XTest.java", "class XTest{}\n")
    made = prime.prime_for(root, ("java", "maven"), seeded=SEEDED)
    assert all(origin.startswith("sources/app/") for _, origin in made.copies())


def test_two_builds_at_the_same_depth_are_refused_by_name(tmp_path):
    root = corpus(tmp_path)
    put(root / "sources/other/pom.xml", "<project/>\n")
    with pytest.raises(prime.PrimeRefused) as refused:
        prime.prime_for(root, ("java", "maven"), seeded=SEEDED)
    said = str(refused.value)
    assert "sources/app" in said and "sources/other" in said and "one project" in said


def test_a_build_with_a_source_and_no_language_of_its_own_is_refused(tmp_path):
    root = corpus(tmp_path, java=False)
    with pytest.raises(prime.PrimeRefused) as refused:
        prime.prime_for(root, ("java", "maven"), seeded=SEEDED)
    assert "compile nothing" in str(refused.value)


# --------------------------------------------------------------------------
# ⛔ The prime is the corpus's own build, never its exercises'
# --------------------------------------------------------------------------


def exercised(root):
    """A corpus whose own build is at its root, with one emitted exercise under it."""
    put(root / "pom.xml", "<project/>\n")
    put(root / "src/main/java/demo/Demo.java", "package demo;\npublic class Demo { }\n")
    put(root / "src/test/java/demo/DemoTest.java", "package demo;\nclass DemoTest { }\n")
    bundle = dependency.write_bundle(root)
    write(root, emit(root, bundle, source="demo", ingested="2026-01-05"), "the exercise")
    return bundle


def test_an_exercise_build_role_is_never_swept_into_the_prime(tmp_path):
    bundle = exercised(tmp_path)
    # ⭐ The fixture is real: the build role and its workspace copy both exist.
    assert (tmp_path / bundle.places.in_bundle(bundle.places.build_path("pom.xml"))).is_file()
    assert (tmp_path / bundle.places.in_workspace(dependency.BUILD_FILE)).is_file()
    made = prime.prime_for(tmp_path, ("java", "maven"), seeded=SEEDED)
    assert made.build_files == ("pom.xml",)


def test_no_exercise_file_is_ever_a_specimen(tmp_path):
    bundle = exercised(tmp_path)
    made = prime.prime_for(tmp_path, ("java", "maven"), seeded=SEEDED)
    for _, origin in made.copies():
        assert not origin.startswith((bundle.places.bundle, bundle.places.workspace)), origin
    assert made.specimens[0].source == "src/main/java/demo/Demo.java"


def multi_module(root):
    """A build of three modules under one root build file: two teach, one has nothing to compile."""
    put(root / "pom.xml", "<project><modules><module>a</module></modules></project>\n")
    for module in ("a", "b", "empty"):
        put(root / module / "pom.xml", "<project/>\n")
    put(root / "a/src/main/java/a/Tiny.java", "package a; class Tiny {}\n")
    put(root / "a/src/main/java/a/Shape.java", "package a; class Shape { int sides; }\n")
    put(root / "a/src/test/java/a/ShapeTest.java", "package a; class ShapeTest { Shape s; }\n")
    put(root / "b/src/main/java/b/Longer.java", "package b; class Longer { int one; int two; }\n")
    put(root / "b/src/test/java/b/LongerTest.java", "package b; class LongerTest { Longer l; }\n")
    return root


def test_a_multi_module_build_is_primed_as_a_build_module_by_module(tmp_path):
    made = prime.prime_for(multi_module(tmp_path), ("java", "maven"), seeded=SEEDED)
    (project,) = made.projects
    assert project.root == ""
    assert project.build_files == ("a/pom.xml", "b/pom.xml", "empty/pom.xml", "pom.xml")
    by_module = {one.module: one for one in project.specimens}
    assert sorted(by_module) == ["a", "b"], "every module that teaches gets its own specimen"
    assert by_module["a"].files() == (
        "a/src/main/java/a/Shape.java",
        "a/src/main/java/a/Tiny.java",
        "a/src/test/java/a/ShapeTest.java",
    ), "the test is copied with the class it names, so the module compiles"
    assert by_module["b"].files() == (
        "b/src/main/java/b/Longer.java",
        "b/src/test/java/b/LongerTest.java",
    )


def test_a_module_with_no_sources_is_primed_through_its_build_file_and_never_refused(tmp_path):
    made = prime.prime_for(multi_module(tmp_path), ("java", "maven"), seeded=SEEDED)
    assert ("maven/empty/pom.xml", "empty/pom.xml") in made.copies()
    assert not any(one.module == "empty" for one in made.specimens)


def test_the_document_names_each_specimens_module_and_what_it_carries(tmp_path):
    made = prime.prime_for(multi_module(tmp_path), ("java", "maven"), seeded=SEEDED)
    (project,) = made.document()["projects"]
    first = project["specimens"][0]
    assert first["module"] == "a"
    assert first["support"] == ["a/src/main/java/a/Shape.java"]


def test_a_single_module_build_copies_its_smallest_pair_and_nothing_they_do_not_name(tmp_path):
    made = prime.prime_for(corpus(tmp_path), ("java", "maven"), seeded=SEEDED)
    assert [pair[1] for pair in made.copies()] == [
        "sources/app/pom.xml",
        "sources/app/src/main/java/demo/Demo.java",
        "sources/app/src/test/java/demo/DemoTest.java",
    ]


def test_every_file_under_the_prime_that_this_selection_does_not_copy_is_stale(tmp_path):
    for where in ("p/maven/pom.xml", "p/maven/src/Old.java", "other/kept.txt"):
        put(tmp_path / where, "x\n")
    assert prime.stale_in(tmp_path, "p", {"p/maven/pom.xml"}) == ("p/maven/src/Old.java",)
    assert prime.stale_in(tmp_path, "absent", set()) == ()


def test_a_linked_directory_in_the_prime_is_named_as_a_link_and_never_walked(tmp_path):
    put(tmp_path / "src/Lesson.java", "class Lesson {}\n")
    put(tmp_path / "p/maven/pom.xml", "x\n")
    (tmp_path / "p/maven/src").symlink_to(tmp_path / "src", target_is_directory=True)
    (tmp_path / "p/maven/pom-link.xml").symlink_to(tmp_path / "src/Lesson.java")
    stale = prime.stale_in(tmp_path, "p", {"p/maven/pom.xml", "p/maven/pom-link.xml"})
    assert stale == ("p/maven/pom-link.xml", "p/maven/src"), "a link is stale, kept or not"


def test_a_prime_that_is_itself_a_link_is_never_walked(tmp_path):
    put(tmp_path / "src/Lesson.java", "class Lesson {}\n")
    (tmp_path / ".studyforge/execution").mkdir(parents=True)
    (tmp_path / ".studyforge/execution/prime").symlink_to(
        tmp_path / "src", target_is_directory=True
    )
    assert prime.stale_in(tmp_path, ".studyforge/execution/prime", set()) == ()


def test_a_prime_reached_through_a_link_is_named_and_a_plain_one_is_not(tmp_path):
    where = ".studyforge/execution/prime"
    assert prime.linked(tmp_path, where) is None, "an absent prime is written, not refused"
    (tmp_path / where).mkdir(parents=True)
    assert prime.linked(tmp_path, where) is None
    other = tmp_path / "elsewhere"
    other.mkdir()
    (tmp_path / ".studyforge/execution/prime").rmdir()
    (tmp_path / ".studyforge/execution").rename(other / "execution")
    (tmp_path / ".studyforge/execution").symlink_to(other / "execution", target_is_directory=True)
    why = prime.linked(tmp_path, where)
    assert why is not None and why.startswith(".studyforge/execution is a symbolic link")
    assert str(tmp_path) not in why, "the refusal names no host path"
    assert prime.linked(tmp_path, ".studyforge/../outside") is not None


def gradle_build(root, where: str, *, checksums: bool) -> None:
    """A Gradle build at `where` with one Kotlin source and test, and its checksum file if asked."""
    base = root / where if where else root
    put(base / "settings.gradle.kts", 'rootProject.name = "b"\n')
    put(base / "build.gradle.kts", 'plugins { kotlin("jvm") version "2.4.20" }\n')
    put(base / "src/main/kotlin/a/A.kt", "package a\nclass A\n")
    put(base / "src/test/kotlin/a/ATest.kt", "package a\nclass ATest { val a: A? = null }\n")
    if checksums:
        put(base / "gradle/verification-metadata.xml", "<verification-metadata/>\n")


def test_a_gradle_build_with_checksums_is_the_prime_over_a_shallower_one_without(tmp_path):
    # ⭐ The component refuses a Gradle prime with no checksum file, so a deeper build that
    # carries one is the prime; the shallower one (an example build) is not warmed from here.
    gradle_build(tmp_path, "examples", checksums=False)
    gradle_build(tmp_path, "tools/prime", checksums=True)
    made = prime.prime_for(tmp_path, ("gradle", "kotlin"), seeded=SEEDED)
    assert [one.root for one in made.projects] == ["tools/prime"]
    assert "tools/prime/gradle/verification-metadata.xml" in made.build_files
    assert all(origin.startswith("tools/prime/") for _, origin in made.copies())


def test_where_the_shallowest_gradle_build_has_checksums_or_none_does_it_is_the_prime(tmp_path):
    # ⛔ Every corpus that primed before primes the same build.
    both = tmp_path / "both"
    gradle_build(both, "examples", checksums=True)
    gradle_build(both, "tools/prime", checksums=True)
    made = prime.prime_for(both, ("gradle", "kotlin"), seeded=SEEDED)
    assert [p.root for p in made.projects] == ["examples"]
    neither = tmp_path / "neither"
    gradle_build(neither, "examples", checksums=False)
    gradle_build(neither, "tools/prime", checksums=False)
    assert [
        p.root for p in prime.prime_for(neither, ("gradle", "kotlin"), seeded=SEEDED).projects
    ] == ["examples"]


def test_two_gradle_builds_with_checksums_at_one_depth_are_still_refused(tmp_path):
    gradle_build(tmp_path, "examples", checksums=False)
    gradle_build(tmp_path, "tools/one", checksums=True)
    gradle_build(tmp_path, "tools/two", checksums=True)
    with pytest.raises(prime.PrimeRefused) as refused:
        prime.prime_for(tmp_path, ("gradle", "kotlin"), seeded=SEEDED)
    assert "tools/one" in str(refused.value) and "tools/two" in str(refused.value)
