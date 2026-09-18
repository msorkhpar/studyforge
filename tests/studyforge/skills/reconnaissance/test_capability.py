"""Is anything runnable, and does a grader ship with it? (SK-01)"""

from __future__ import annotations

from studyforge.skills.reconnaissance import assess, take
from studyforge.skills.reconnaissance.capability import observe
from studyforge.skills.reconnaissance.report import Observation, Uncertainty
from tests.studyforge.skills.reconnaissance import sources


def seen(root):
    return list(observe(assess(take(root))))


def test_a_prose_only_corpus_reports_no_runnable_code_and_no_graders(tmp_path):
    # ⭐ E11's named acceptance, and it is a **finished verdict** rather than a
    # blank section: a corpus with no graders is complete at the reading floor,
    # not short (§11.0, C5).
    verdicts = [
        i.measured
        for i in seen(sources.flat_prose(tmp_path / "c"))
        if isinstance(i, Observation) and i.what == "verdict"
    ]
    assert verdicts == ["no runnable code, no graders — complete at the reading floor"]


def test_a_corpus_with_a_build_and_tests_is_both(tmp_path):
    able = assess(take(sources.runnable(tmp_path / "c")))
    assert able.runnable and able.graded
    assert able.build_files == ["pom.xml"]


def test_and_it_does_not_claim_the_reading_floor_verdict(tmp_path):
    assert not [
        i
        for i in seen(sources.runnable(tmp_path / "c"))
        if isinstance(i, Observation) and i.what == "verdict"
    ]


def test_a_build_with_no_recognisable_tests_is_a_question(tmp_path):
    # ⚠️ An ungraded exercise is a first-class state (§7), so this asks rather
    # than concluding either way.
    root = sources.runnable(tmp_path / "c")
    (root / "src/test/java/ThingTest.java").unlink()
    asked = [i for i in seen(root) if isinstance(i, Uncertainty)]
    assert any("graders this skill did not recognise" in q.question for q in asked)


def test_non_prose_files_with_no_build_are_asked_about(tmp_path):
    # ⛔ The closed set costs exactly one question, and the question names what
    # was looked for — which is also how the set grows.
    root = sources.flat_prose(tmp_path / "c")
    (root / "script.sh").write_text("echo hi\n", encoding="utf-8")
    asked = [i for i in seen(root) if isinstance(i, Uncertainty)]
    assert any("meant to be run" in q.question for q in asked)


# --------------------------------------------------------------------------
# ⛔ W329: the framework's own generated half is not this corpus's capability
# --------------------------------------------------------------------------

#: What onboarding generates into a corpus that has no graders of its own.
SCAFFOLD = {
    "tests/test_non_destructive.py": "def test_non_destructive(): pass\n",
    "tests/ingest/test_read.py": "def test_read(): pass\n",
    "ingest/read.py": "def read(): pass\n",
}


def verdict(root):
    """The finished verdict, or nothing where this corpus claims none."""
    return [i.measured for i in seen(root) if isinstance(i, Observation) and i.what == "verdict"]


def test_generated_checks_the_record_names_are_not_this_corpus_graders(tmp_path):
    # ⛔ The measured failure: a re-survey of an onboarded corpus counted the
    # scaffold's own `tests/**/test_*.py` as graders, dropped this verdict and
    # drafted `exercises: true` — so a corpus COMPLETE at the reading floor was
    # presented to its reader as unfinished (C5).
    root = sources.onboarded(sources.flat_prose(tmp_path / "c"), SCAFFOLD)

    able = assess(take(root))

    assert not able.graded and able.test_files == []
    assert verdict(root) == ["no runnable code, no graders — complete at the reading floor"]


def test_the_same_files_unrecorded_ARE_counted_so_the_clause_above_measures_something(tmp_path):
    # ⭐ The control. Without the record the identical tree is graded, which is
    # what a corpus that ships its own graders must keep doing.
    root = sources.write(sources.flat_prose(tmp_path / "c"), SCAFFOLD)

    assert assess(take(root)).graded
    assert verdict(root) == []


def test_bytecode_the_generated_checks_leave_behind_is_not_a_grader(tmp_path):
    # ⛔ `SKILL.md` step 4 commands `python3 -m pytest tests`, and its bytecode
    # is named `test_*.pyc`. ⚠️ Nothing here recognises bytecode: this pass now
    # keeps `inventory`'s one walk rule, which has always called `__pycache__`
    # never material, instead of a looser second rule of its own.
    root = sources.onboarded(sources.flat_prose(tmp_path / "c"), SCAFFOLD)
    sources.write(root, {"tests/__pycache__/test_non_destructive.cpython-314.pyc": "\x00"})

    assert assess(take(root)).test_files == []


def test_a_grader_inside_a_directory_the_walk_enters_is_still_counted(tmp_path):
    # ⭐ The control for the clause above: the rule dropped `__pycache__`, not
    # every directory, and a corpus's own graded tests are unaffected.
    root = sources.runnable(tmp_path / "c")
    sources.write(root, {"node_modules/pkg/thing.test.js": "it('x')\n"})

    able = assess(take(root))

    assert able.graded and "src/test/java/ThingTest.java" in able.test_files
    assert not [where for where in able.test_files if where.startswith("node_modules/")]


def test_the_archive_a_build_wrote_is_not_this_corpus_own_source(tmp_path):
    # ⛔ The fourth flipped answer, and no brief named it: `placement` reads
    # `capability.source_files`, and an archive is full of `.json`. ⭐ It is
    # `validate`'s answer rather than the install record's, because onboarding
    # did not write the archive — a build did.
    root = sources.flat_prose(tmp_path / "c")
    sources.write(root, {"archive/course/container.json": "{}\n"})

    assert assess(take(root)).source_files == []


def test_a_json_file_the_corpus_itself_carries_is_still_counted(tmp_path):
    # ⭐ The control: the archive is dropped by where it sits, not by its suffix.
    root = sources.flat_prose(tmp_path / "c")
    sources.write(root, {"data/course.json": "{}\n"})

    assert assess(take(root)).source_files == ["data/course.json"]
