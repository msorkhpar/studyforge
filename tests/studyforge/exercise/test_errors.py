"""The one exception this package raises."""

from studyforge.exercise import ExerciseError
from studyforge.exercise import errors as module


def test_it_is_a_value_error():
    # ⚠️ Following SF-01's split and the two contracts either side of this one:
    # an exercise is a value read from a document, so it fails the way a
    # manifest and an authored overlay fail.
    assert issubclass(ExerciseError, ValueError)


def test_it_is_the_package_s_own_family_and_not_borrowed():
    # ⛔ Not `ArchiveError` and not `ContentError`. `archive.document` wraps
    # this at its boundary precisely because the two are different families —
    # a caller reading a file wants one answer from `archive`, and a caller
    # reading a record wants one answer from here.
    from studyforge.archive.errors import ArchiveError
    from studyforge.unit.errors import ContentError

    assert not issubclass(ExerciseError, ArchiveError)
    assert not issubclass(ExerciseError, ContentError)


def test_the_module_depends_on_nothing():
    # ⭐ The reason it is a module of its own: `safety` and `record` both raise
    # it, and putting it in either would make the other import a module it has
    # no business knowing.
    source = module.__doc__ or ""
    assert "Depends on.** Nothing" in source
