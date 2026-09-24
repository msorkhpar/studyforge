"""The quiz gates' contract, its public surface, and the one line it adds outside itself.

⛔ **The gate framework's seam carries a bound — *`families.py`, `record.py`,
`digests.py` and `runs.py` never name the quiz family*.** ⭐ That bound is read
here against the tree rather than promised in prose.
"""

from __future__ import annotations

import ast

from studyforge.exercise import gates
from studyforge.exercise.gates import quiz
from tests.studyforge.exercise.gates.test_configuration import gates_modules
from tests.support import assert_package_contract, repository_root


def quiz_modules():
    """Every module of the quiz sub-package — this file's population."""
    found = [path for path in gates_modules() if "/quiz/" in path.as_posix()]
    assert found, "the sweep found no module, so it would pass over nothing"
    return found


def test_the_sub_package_states_its_contract():
    assert_package_contract(quiz, "studyforge.exercise.gates.quiz")


def test_the_public_surface_is_declared_and_complete():
    assert set(quiz.__all__) == {
        "JUDGED",
        "JUDGED_FIELDS",
        "MECHANICAL",
        "QUESTION_ROLE",
        "QUIZ",
        "Q1",
        "Q2",
        "Q3",
        "Q4",
        "Q5",
        "WHOLE_QUESTION",
        "Judgement",
        "check_quiz",
        "cited_for",
        "cited_role",
        "judged_gate",
        "key_total_and_single",
        "origin_still_resolves",
        "question_digest",
        "require_advisory",
        "require_judgements",
        "require_quiz",
        "verdict",
    }
    for name in quiz.__all__:
        assert hasattr(quiz, name), name


def test_the_parent_package_names_this_sub_package_in_its_own_table():
    # ⚠️ R17: the parent's contract is where a reader finds out this exists,
    # and it is also the one line that makes the family register at all —
    # there is no discovery mechanism in `src/`.
    assert "`quiz`" in (gates.__doc__ or "")
    assert gates.QUIZ is quiz.QUIZ


def test_the_sub_package_is_reachable_without_naming_a_module_inside_it():
    # ⭐ The import surface the authoring skill uses: the sub-package,
    # never `studyforge.exercise.gates.quiz.judged`.
    assert quiz.check_quiz is not None and quiz.question_digest is not None
    assert quiz.QUIZ.gates == (quiz.Q1, quiz.Q2, quiz.Q3, quiz.Q4, quiz.Q5)


def test_nothing_here_imports_execute_starts_a_process_or_reaches_the_filesystem():
    # ⛔ The parent package's layering, inherited: nothing in `gates/` runs
    # anything, and a quiz has nothing to run in the first place.
    reached: list[str] = []
    for path in quiz_modules():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                reached += [alias.name for alias in node.names]
            if isinstance(node, ast.ImportFrom) and node.module:
                reached.append(node.module)
    print(sorted(set(reached)))
    assert not [name for name in reached if name.startswith("studyforge.execute")]
    assert not [
        name
        for name in reached
        if name.split(".")[0] in ("subprocess", "shutil", "socket", "urllib", "pathlib", "os")
    ]


def test_the_seam_is_used_rather_than_widened():
    # ⛔ The gate framework's own bound, read off the tree: the modules it
    # names exist, and none of them names the quiz sub-package.
    package = repository_root() / "src" / "studyforge" / "exercise" / "gates"
    untouched = ("families.py", "record.py", "digests.py", "runs.py", "evidence.py", "code.py")
    for name in untouched:
        assert (package / name).is_file(), name
    # ⭐ And the seam's shape, read rather than recited: not one of those
    # modules names this sub-package.
    for name in untouched:
        text = (package / name).read_text(encoding="utf-8")
        assert "gates.quiz" not in text, name
