"""Mirror of `src/studyforge/generate/writing.py` (R12)."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath

import pytest

from studyforge.generate import Footprint, Written
from studyforge.generate.writing import copy, mint, place, same_root

A = PurePosixPath("one/a.html")
B = PurePosixPath("two/b.html")

#: ⛔ A footprint that owns nothing — R3's floor, and the default every one of
#: the clauses below runs against unless it is testing the rebuild policy.
NOBODYS = Footprint()

#: A footprint that claims `A` as the build's own, the way a plan declaring it
#: would. ⭐ Built from `Footprint`'s own members rather than from a corpus, so
#: these clauses stay about `place` and `copy`.
MINE = Footprint(files=frozenset({A}))


# --------------------------------------------------------------------------
# ⛔ place — R3 by refusing, not by remembering
# --------------------------------------------------------------------------


def test_a_path_that_does_not_exist_is_written_and_its_directories_minted(tmp_path):
    written, refused, replaced = [], [], []

    place(tmp_path, A, b"body", written, refused, replaced, footprint=NOBODYS)

    assert (tmp_path / A).read_bytes() == b"body"
    assert (written, refused) == ([A], [])


def test_a_path_that_exists_is_named_and_never_opened_for_writing(tmp_path):
    (tmp_path / A).parent.mkdir(parents=True)
    (tmp_path / A).write_bytes(b"a reader's own file")
    written, refused, replaced = [], [], []

    place(tmp_path, A, b"body", written, refused, replaced, footprint=NOBODYS)

    assert (tmp_path / A).read_bytes() == b"a reader's own file"
    assert (written, refused) == ([], [A])


def test_an_existing_directory_at_the_target_is_refused_rather_than_crashed_into(tmp_path):
    """⚠️ A directory `exists()` too, and the refusal is the same one."""
    (tmp_path / A).mkdir(parents=True)
    written, refused, replaced = [], [], []

    place(tmp_path, A, b"body", written, refused, replaced, footprint=NOBODYS)

    assert (written, refused) == ([], [A])
    assert (tmp_path / A).is_dir()


def test_only_the_directories_a_target_needs_are_minted(tmp_path):
    written, refused, replaced = [], [], []

    place(tmp_path, A, b"body", written, refused, replaced, footprint=NOBODYS)

    assert sorted(path.name for path in tmp_path.iterdir()) == ["one"]


# --------------------------------------------------------------------------
# ⛔ copy — the same refusal, without the bytes going through memory
# --------------------------------------------------------------------------


def test_a_file_is_copied_byte_for_byte_and_its_directories_minted(tmp_path):
    source = tmp_path / "origin.bin"
    source.write_bytes(b"\x00\x01\x02")
    written, refused, replaced = [], [], []

    copy(tmp_path, A, source, written, refused, replaced, footprint=NOBODYS)

    assert (tmp_path / A).read_bytes() == b"\x00\x01\x02"
    assert (written, refused) == ([A], [])


def test_a_file_already_at_the_target_is_named_and_never_opened_for_writing(tmp_path):
    source = tmp_path / "origin.bin"
    source.write_bytes(b"new")
    (tmp_path / A).parent.mkdir(parents=True)
    (tmp_path / A).write_bytes(b"a reader's own file")
    written, refused, replaced = [], [], []

    copy(tmp_path, A, source, written, refused, replaced, footprint=NOBODYS)

    assert (tmp_path / A).read_bytes() == b"a reader's own file"
    assert (written, refused) == ([], [A])


def test_an_executable_bit_in_the_archive_does_not_reach_the_generated_tree(tmp_path):
    """⛔ Content only — see `copy`'s docstring.

    ⭐ **Found by planting**: `copy2` passed every other clause in this module,
    because the two spellings differ in exactly the field nothing was asserting.
    A material file that arrived executable would otherwise put an executable
    byte into a reader's repository.
    """
    source = tmp_path / "origin.bin"
    source.write_bytes(b"body")
    source.chmod(0o777)
    written, refused, replaced = [], [], []

    copy(tmp_path, A, source, written, refused, replaced, footprint=NOBODYS)

    assert not os.access(tmp_path / A, os.X_OK)


def test_a_copy_into_an_output_root_that_does_not_exist_is_refused(tmp_path):
    from studyforge.generate import BuildError

    source = tmp_path / "origin.bin"
    source.write_bytes(b"body")
    missing = tmp_path / "nowhere"

    with pytest.raises(BuildError):
        copy(missing, A, source, [], [], [], footprint=NOBODYS)

    assert not missing.exists()


# --------------------------------------------------------------------------
# ⛔ mint — a directory the plan declared
# --------------------------------------------------------------------------


def test_a_declared_directory_is_created_and_is_not_recorded_as_a_write(tmp_path):
    refused = []

    mint(tmp_path, PurePosixPath("one/images"), refused)

    assert (tmp_path / "one/images").is_dir()
    assert refused == []


def test_a_directory_that_is_already_there_is_simply_already_there(tmp_path):
    (tmp_path / "one/images").mkdir(parents=True)
    refused = []

    mint(tmp_path, PurePosixPath("one/images"), refused)

    assert refused == []


def test_every_writer_here_refuses_the_emission_census_own_filler(tmp_path, monkeypatch):
    """⛔ `SF-28/2`, closed for all three writers rather than for the first one.

    ⭐ **The census fills a `Path` parameter with `Path("alpha")`** — a *relative*
    path, resolved against whatever the process's working directory happens to
    be, which for a test run is the repository. ⚠️ A second path parameter is
    the shape that actually lands a file, so this asserts the guard from the
    caller's side: run from inside a checkout-shaped directory, with the census's
    own value, all three refuse and nothing appears.
    """
    from studyforge.generate import BuildError
    from tests.emission.fillers import filler_for

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "origin.bin"
    source.write_bytes(b"body")
    census = Path("alpha")
    # ⛔ **The census's OWN value for the new parameter**, not one this module
    # chose. A footprint is now a second thing the probe fills, and the trap
    # this guard exists for is a filled parameter rather than a poisoned one.
    filled = filler_for(Footprint)
    assert not filled.owns(A)

    for call in (
        lambda: place(census, A, b"body", [], [], [], footprint=filled),
        lambda: copy(census, A, source, [], [], [], footprint=filled),
        lambda: mint(census, PurePosixPath("alpha"), []),
    ):
        with pytest.raises(BuildError):
            call()

    assert sorted(path.name for path in tmp_path.iterdir()) == ["origin.bin"]


def test_a_readers_own_file_where_a_directory_belongs_is_named_and_left_alone(tmp_path):
    """⛔ R3: `mkdir(exist_ok=True)` still raises on a file, and a build must not."""
    (tmp_path / "one").mkdir()
    (tmp_path / "one/images").write_bytes(b"a reader's own file")
    refused = []

    mint(tmp_path, PurePosixPath("one/images"), refused)

    assert refused == [PurePosixPath("one/images")]
    assert (tmp_path / "one/images").read_bytes() == b"a reader's own file"


# --------------------------------------------------------------------------
# ⭐ Written — two passes' records, added
# --------------------------------------------------------------------------


def test_two_records_add_in_the_order_the_passes_ran():
    first = Written(pages=(A,), refused=(B,))
    second = Written(pages=(B,), assets=(A,), media=(A,), missing=(B,))

    both = first + second

    assert both.pages == (A, B)
    assert both.assets == (A,)
    assert both.media == (A,)
    assert both.refused == (B,)
    assert both.missing == (B,)


def test_paths_is_every_file_written_and_never_a_refusal_or_an_absence():
    record = Written(
        pages=(A,),
        assets=(B,),
        media=(PurePosixPath("three/c.svg"),),
        refused=(PurePosixPath("c.html"),),
        missing=(PurePosixPath("d.svg"),),
    )

    assert record.paths == (A, B, PurePosixPath("three/c.svg"))


def test_an_empty_record_is_the_identity_of_the_sum():
    record = Written(pages=(A,), assets=(B,), refused=(A,))

    assert record + Written() == record


def test_adding_something_that_is_not_a_record_is_refused():
    with pytest.raises(TypeError):
        Written() + object()


def test_an_output_root_that_does_not_exist_is_refused_and_never_minted(tmp_path):
    """⛔ Measured: `tests/emission` calls this with `Path('alpha')`.

    ⭐ A writer that minted its own root created `alpha/alpha` **in the
    repository** on every full test run, silently, because a relative root
    resolves against the process's working directory. ⛔ The refusal names
    neither the root nor the target (R7).
    """
    from studyforge.generate import BuildError

    missing = tmp_path / "nowhere"
    written, refused, replaced = [], [], []

    with pytest.raises(BuildError) as raised:
        place(missing, A, b"body", written, refused, replaced, footprint=NOBODYS)

    assert not missing.exists()
    assert (written, refused) == ([], [])
    assert str(tmp_path) not in str(raised.value)


def test_a_file_where_the_output_root_should_be_is_refused_too(tmp_path):
    from studyforge.generate import BuildError

    (tmp_path / "root").write_bytes(b"not a directory")

    with pytest.raises(BuildError):
        place(tmp_path / "root", A, b"body", [], [], [], footprint=NOBODYS)


# --------------------------------------------------------------------------
# ⛔ The rebuild policy — the build's own prior output, and nothing else
# --------------------------------------------------------------------------


def test_a_path_the_plan_declares_as_the_builds_own_is_replaced_and_recorded(tmp_path):
    (tmp_path / A).parent.mkdir(parents=True)
    (tmp_path / A).write_bytes(b"the build's own previous answer")
    written, refused, replaced = [], [], []

    place(tmp_path, A, b"the new answer", written, refused, replaced, footprint=MINE)

    assert (tmp_path / A).read_bytes() == b"the new answer"
    assert (written, refused, replaced) == ([A], [], [A])


def test_a_replaced_path_is_still_one_of_the_paths_the_run_wrote(tmp_path):
    """⛔ Ruling 99: `paths` is the path-for-path diff against `studyforge plan`.

    ⭐ A rebuild must diff exactly as a first build does, so `replaced` is a
    cross-cutting record and never a fourth category that removes a path from
    the enumeration.
    """
    (tmp_path / A).parent.mkdir(parents=True)
    (tmp_path / A).write_bytes(b"before")
    written, refused, replaced = [], [], []

    place(tmp_path, A, b"after", written, refused, replaced, footprint=MINE)

    record = Written(pages=tuple(written), refused=tuple(refused), replaced=tuple(replaced))
    assert record.paths == (A,)


def test_a_path_the_plan_does_not_declare_is_refused_even_beside_one_it_does(tmp_path):
    """⛔ The other half of the decision: anything else is refused BY NAME."""
    for at in (A, B):
        (tmp_path / at).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / at).write_bytes(b"a reader's own file")
    written, refused, replaced = [], [], []

    place(tmp_path, A, b"mine", written, refused, replaced, footprint=MINE)
    place(tmp_path, B, b"not mine", written, refused, replaced, footprint=MINE)

    assert refused == [B]
    assert (tmp_path / B).read_bytes() == b"a reader's own file"


def test_a_file_inside_a_declared_directory_is_the_builds_own(tmp_path):
    """⭐ The plan enumerates a unit's media as a DIRECTORY, never file by file.

    ⛔ Found by planting: a footprint matching only the plan's exact file lines
    passed every page clause in this module and refused every copied media file
    on a rebuild, which is the case the row exists for.
    """
    at = PurePosixPath("units/unit-01/images/diagram.svg")
    (tmp_path / at).parent.mkdir(parents=True)
    (tmp_path / at).write_bytes(b"old")
    source = tmp_path / "origin.bin"
    source.write_bytes(b"new")
    footprint = Footprint(directories=(PurePosixPath("units/unit-01/images"),))
    written, refused, replaced = [], [], []

    copy(tmp_path, at, source, written, refused, replaced, footprint=footprint)

    assert (tmp_path / at).read_bytes() == b"new"
    assert (written, refused, replaced) == ([at], [], [at])


def test_a_sibling_of_a_declared_directory_is_not_inside_it(tmp_path):
    """⛔ Planted: a prefix test spelled as a string `startswith` calls
    `units/unit-01/images-of-mine/x.png` part of `units/unit-01/images`."""
    at = PurePosixPath("units/unit-01/images-of-mine/x.png")
    (tmp_path / at).parent.mkdir(parents=True)
    (tmp_path / at).write_bytes(b"a reader's own file")
    source = tmp_path / "origin.bin"
    source.write_bytes(b"new")
    footprint = Footprint(directories=(PurePosixPath("units/unit-01/images"),))
    written, refused, replaced = [], [], []

    copy(tmp_path, at, source, written, refused, replaced, footprint=footprint)

    assert (written, refused, replaced) == ([], [at], [])
    assert (tmp_path / at).read_bytes() == b"a reader's own file"


def test_a_directory_standing_where_a_declared_page_belongs_is_still_refused(tmp_path):
    """⛔ Replacing this build's own FILE is a write; removing a tree is a
    deletion, and nothing in this module deletes."""
    (tmp_path / A).mkdir(parents=True)
    written, refused, replaced = [], [], []

    place(tmp_path, A, b"body", written, refused, replaced, footprint=MINE)

    assert (written, refused, replaced) == ([], [A], [])
    assert (tmp_path / A).is_dir()


def test_a_footprint_that_owns_nothing_is_the_floor_the_build_had_before(tmp_path):
    """⭐ `Footprint()` — the default on `Corpus`, the fallback for a plan that
    refused, and what the emission census's filler builds."""
    (tmp_path / A).parent.mkdir(parents=True)
    (tmp_path / A).write_bytes(b"a reader's own file")
    written, refused, replaced = [], [], []

    place(tmp_path, A, b"body", written, refused, replaced, footprint=Footprint())

    assert (written, refused, replaced) == ([], [A], [])


def test_a_writer_cannot_be_reached_without_answering_whose_file_this_is(tmp_path):
    """⛔ `footprint` is keyword-only and required, so a pass added later fails
    at the call rather than overwriting at a reader's."""
    with pytest.raises(TypeError):
        place(tmp_path, A, b"body", [], [], [])
    with pytest.raises(TypeError):
        copy(tmp_path, A, tmp_path, [], [], [])


def test_the_same_bytes_are_replaced_or_refused_purely_on_which_path_they_sit_at(tmp_path):
    """⛔ **By PATH, never by content** — the rule stated as one measurement.

    ⭐ Identical bytes at two paths get opposite treatment, so no reading of the
    file can be what decided. ⚠️ The converse is asserted too: different bytes
    at the SAME named path are still replaced, so content cannot be smuggled in
    later as a tie-breaker without breaking this clause.
    """
    mine = b"a reader's own file"
    for at in (A, B):
        (tmp_path / at).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / at).write_bytes(mine)
    written, refused, replaced = [], [], []

    place(tmp_path, A, b"new", written, refused, replaced, footprint=MINE)
    place(tmp_path, B, b"new", written, refused, replaced, footprint=MINE)

    assert (replaced, refused) == ([A], [B])
    assert (tmp_path / B).read_bytes() == mine

    # ⭐ Bytes byte-for-byte equal to what the build would write, at the named
    # path: still a replacement, because nothing compared them.
    (tmp_path / A).write_bytes(b"new")
    again = []
    place(tmp_path, A, b"new", [], [], again, footprint=MINE)
    assert again == [A]


def test_a_foreign_file_in_the_output_root_survives_a_rebuild_byte_for_byte(tmp_path):
    """⛔ The refusal half, read back through the BYTES rather than the record."""
    foreign = PurePosixPath("notes.txt")
    mine = b"a reader's own file, at a path no plan names"
    (tmp_path / foreign).write_bytes(mine)
    refused = []

    for _ in range(2):
        place(tmp_path, foreign, b"clobbered", [], refused, [], footprint=MINE)

    assert refused == [foreign, foreign]
    assert (tmp_path / foreign).read_bytes() == mine


# --------------------------------------------------------------------------
# same_root — whether a build's output IS the corpus root (`W224`)
# --------------------------------------------------------------------------


def test_same_root_asks_the_filesystem_not_the_spelling(tmp_path):
    corpus = tmp_path / "corpus"
    elsewhere = tmp_path / "out"
    corpus.mkdir()
    elsewhere.mkdir()

    assert same_root(corpus, corpus)
    assert same_root(Path(f"{corpus}/../{corpus.name}"), corpus)
    assert not same_root(elsewhere, corpus)


def test_same_root_refuses_an_output_root_that_is_not_a_directory(tmp_path):
    from studyforge.generate import BuildError

    with pytest.raises(BuildError, match="output root") as raised:
        same_root(tmp_path / "absent", tmp_path)
    assert str(tmp_path) not in str(raised.value)
