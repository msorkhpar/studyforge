"""Mirror of `src/studyforge/skills/execution/prime.py` (R12).

⛔ **The claim under test is a negative one**: an empty prime primes nothing
while appearing to succeed, so every refusal is asserted with the clean case
beside it. ⭐ Nothing here authors a build file or a test framework — the
selection is out of the corpus's own material, so the assertions are about
*which* file was chosen and never about what was written into one.
"""

from __future__ import annotations

import pytest

from studyforge.skills.execution import prime
from tests.studyforge.skills.execution.contracts import corpus

#: The runtimes the synthetic component seeds a cache for.
SEEDED = ("gradle", "maven")


def test_a_corpus_with_a_build_file_a_source_and_a_test_is_primed(tmp_path):
    made = prime.prime_for(corpus(tmp_path), ("java", "maven"), seeded=SEEDED)
    assert made.build_files == ("sources/app/pom.xml",)
    assert [one.language for one in made.specimens] == ["java"]
    assert made.specimens[0].source.endswith("Demo.java")
    assert made.specimens[0].test.endswith("DemoTest.java")


def test_every_selected_path_is_a_file_the_corpus_already_carried(tmp_path):
    root = corpus(tmp_path)
    made = prime.prime_for(root, ("java", "maven"), seeded=SEEDED)
    for where in made.copies():
        assert (root / where).is_file(), where


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
    assert [one.language for one in made.specimens] == ["python"]


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
    root = corpus(tmp_path, java=False)
    (root / "sources/app/pom.xml").unlink()
    with pytest.raises(prime.PrimeRefused) as refused:
        prime.prime_for(root, ("java", "maven"), seeded=SEEDED)
    assert str(refused.value).count(";") >= 2


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
    assert prime.is_a_test(where)


@pytest.mark.parametrize(
    "where",
    ["src/main/java/demo/A.java", "src/latest/A.java", "src/contest.py", "src/protest.js"],
)
def test_these_paths_do_not(where):
    # ⚠️ The negative control, and it is not decoration: a stem check that
    # matched `contest` or `latest` would select ordinary code as a test.
    assert not prime.is_a_test(where)


def test_a_root_that_is_not_a_path_is_refused_without_quoting_it(tmp_path):
    with pytest.raises(prime.PrimeRefused) as refused:
        prime.prime_for("/some/absolute/place", ("java",), seeded=SEEDED)
    assert "/some/absolute/place" not in str(refused.value)


def test_the_document_names_every_file_the_prime_carries(tmp_path):
    made = prime.prime_for(corpus(tmp_path), ("java", "maven"), seeded=SEEDED)
    document = made.document()
    named = set(document["build_files"]) | {
        one["source"] for one in document["specimens"]
    } | {one["test"] for one in document["specimens"]}
    assert named == set(made.copies())
