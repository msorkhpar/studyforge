"""Digests: what a reading was taken over, and whether the file under it has moved.

⭐ **Bundle authoring's `validate` arm is `drifted`**, and the gate framework's acceptance clause
*"a bundle clearing every gate produces a record whose digests match the files
beside it"* is the first case here — asserted in both directions, because a
drift detector that answers the same before and after has detected nothing.
"""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.gates import (
    ALGORITHMS,
    DIGEST_WIDTH,
    SHA256,
    digest_of_bytes,
    drifted,
    require_digest,
    require_role,
    taken_over,
)

WHERE = "corpus/adding-up/unit-01/practice-1"

FILES = (("statement", "statement.md"), ("starter", "starter.py"))


def bundle(root):
    """Two files on disk, and the digests taken over them."""
    (root / "statement.md").write_text("add up a basket\n", encoding="utf-8")
    (root / "starter.py").write_text("def total(prices):\n    ...\n", encoding="utf-8")
    return taken_over(root, FILES, WHERE)


def test_the_digests_match_the_files_beside_them_and_stop_matching_when_one_moves(tmp_path):
    inputs = bundle(tmp_path)
    assert [entry.role for entry in inputs] == ["statement", "starter"]
    assert drifted(tmp_path, inputs, WHERE) == ()

    # ⭐ The plant, OBSERVED: the file's own digest changes, printed on both
    # sides, and only then is the reading taken again.
    before = inputs[1].digest
    (tmp_path / "starter.py").write_text("def total(prices):\n    return 0\n", encoding="utf-8")
    after = digest_of_bytes((tmp_path / "starter.py").read_bytes())
    print("recorded:", before)
    print("on disk now:", after)
    assert before != after

    reasons = drifted(tmp_path, inputs, WHERE)
    assert len(reasons) == 1
    assert "starter.py" in reasons[0]


def test_a_digest_names_its_algorithm_and_is_the_width_that_algorithm_writes():
    value = digest_of_bytes(b"")
    algorithm, _, hexadecimal = value.partition(":")
    assert algorithm == SHA256 and algorithm in ALGORITHMS
    assert len(hexadecimal) == DIGEST_WIDTH[SHA256]
    assert require_digest(value, WHERE) == value


def test_a_digest_this_build_cannot_compute_is_refused_rather_than_trusted():
    with pytest.raises(ExerciseError, match="a digest is written"):
        require_digest("md5:" + "0" * 32, WHERE)
    with pytest.raises(ExerciseError, match="hex characters"):
        require_digest("sha256:" + "0" * 63, WHERE)
    with pytest.raises(ExerciseError, match="a digest is written"):
        require_digest(None, WHERE)


def test_an_input_that_is_not_there_is_a_reading_that_was_never_taken(tmp_path):
    with pytest.raises(ExerciseError, match="never taken"):
        taken_over(tmp_path, (("starter", "absent.py"),), WHERE)


def test_a_path_outside_the_bundle_never_becomes_an_input(tmp_path):
    # ⛔ R7 and `safety`: a record is a tracked file, so its paths are
    # workspace-relative. The shape is assembled at run time.
    outside = "/" + "/".join(("home", "someone", "starter.py"))
    for path in (outside, "../starter.py", "work\\starter.py"):
        with pytest.raises(ExerciseError):
            taken_over(tmp_path, (("starter", path),), WHERE)


def test_the_role_set_is_open_and_the_role_shape_is_closed():
    # ⭐ The half the quiz gates extend: a role this module never heard of is carried,
    # and one a record could not print is refused.
    assert require_role("question:3", WHERE) == "question:3"
    assert require_role("plant:test_an_empty_list_totals_zero", WHERE)
    for bad in ("has space", "", None, 7):
        with pytest.raises(ExerciseError, match="names what the file is"):
            require_role(bad, WHERE)
