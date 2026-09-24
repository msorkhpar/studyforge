"""`W461`: onboarding places its reader document where the corpus says, and a gap is reported.

⭐ **Found at a corpus** (`ISO-32/1`, `ISO-32/2`): the user ruled that a corpus's
`ONBOARDING.md` moves to its archive, and the corpus moved it — but onboarding
wrote it at the root by a fixed name, so the next regenerate put it back, the
generated pin check still pointed a reader at the root, and `hand_edited` read
`[]` with a generated file missing from where the record put it.

Read here through the public calls: `onboard`, `reonboard`, `hand_edited`, and
the manifest's own reader.
"""

from __future__ import annotations

import json

import pytest

from studyforge.corpus.manifest import ONBOARDING_DOC, ManifestError, parse
from studyforge.corpus.manifest.fields import onboarding_doc_of
from studyforge.skills.onboarding import artifacts, hand_edited, onboard, reonboard
from studyforge.skills.onboarding.manifest import ONBOARDING_DOC_API, promote, render
from studyforge.skills.onboarding.pin import PIN_DIR, RECORD_FILE
from studyforge.skills.onboarding.record import OnboardingRefused, gone
from tests.studyforge.skills.onboarding import corpora

#: Where the corpus in `ISO-32` keeps the document now.
ARCHIVED = "docs/archive/ONBOARDING.md"


def _written(tmp_path, **changes):
    root = corpora.material(tmp_path / "corpus")
    made = onboard(corpora.draft(**changes), framework_commit=corpora.COMMIT)
    made.write(root)
    return root, made


def _globs(root):
    document = json.loads((root / artifacts.MANIFEST).read_text(encoding="utf-8"))
    return {entry["glob"]: entry["why"] for entry in document["content"]["not_material"]}


def _tree(root):
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


# --------------------------------------------------------------------------
# ⛔ Clause 1: the manifest places it, and every generated line points there
# --------------------------------------------------------------------------


def test_the_manifest_places_the_reader_document_and_nothing_lands_at_the_root(tmp_path):
    root, made = _written(tmp_path, onboarding_doc=ARCHIVED)

    assert not (root / ONBOARDING_DOC).exists(), "the document was written at the root"
    assert (root / ARCHIVED).read_text(encoding="utf-8").startswith("# A Walkthrough Corpus")
    assert _globs(root).get(ARCHIVED) == artifacts.WHY_READER
    assert ONBOARDING_DOC not in _globs(root)
    assert made.manifest.corpus_api == ONBOARDING_DOC_API
    assert hand_edited(root) == []


def test_the_generated_pin_check_points_where_the_document_is(tmp_path):
    root, _made = _written(tmp_path, onboarding_doc=ARCHIVED)
    text = (root / artifacts.PIN_TEST).read_text(encoding="utf-8")

    assert f"({ARCHIVED} says how)" in text
    assert f"({ONBOARDING_DOC} says how)" not in text


def test_false_writes_no_reader_document_and_the_check_says_how_itself(tmp_path):
    root, made = _written(tmp_path, onboarding_doc=False)

    assert [item.where for item in made.files if item.where.endswith(ONBOARDING_DOC)] == []
    assert artifacts.WHY_READER not in _globs(root).values()
    text = (root / artifacts.PIN_TEST).read_text(encoding="utf-8")
    assert "says how" not in text
    assert "a wheel built from the framework at the pinned commit" in text
    assert hand_edited(root) == []


def test_a_corpus_that_says_nothing_is_onboarded_exactly_as_before(tmp_path):
    root, made = _written(tmp_path)

    assert (root / ONBOARDING_DOC).is_file()
    assert _globs(root)[ONBOARDING_DOC] == artifacts.WHY_READER
    assert "onboarding_doc" not in json.loads((root / artifacts.MANIFEST).read_text("utf-8"))
    assert made.manifest.corpus_api < ONBOARDING_DOC_API
    assert f"({ONBOARDING_DOC} says how)" in (root / artifacts.PIN_TEST).read_text("utf-8")


def test_the_key_is_unreadable_one_version_below_the_one_promote_writes():
    # ⛔ The behavioural pin for `ONBOARDING_DOC_API`, as for `NARRATION_API`.
    document = promote(corpora.draft(onboarding_doc=ARCHIVED))
    assert document["corpus_api"] == ONBOARDING_DOC_API
    with pytest.raises(ManifestError, match="onboarding_doc"):
        parse(render({**document, "corpus_api": ONBOARDING_DOC_API - 1}))


# --------------------------------------------------------------------------
# ⛔ The corpus that found it, end to end: moved by hand, then settled (R10)
# --------------------------------------------------------------------------


def test_a_corpus_that_moved_it_settles_the_place_and_a_regenerate_writes_nothing_at_the_root(
    tmp_path,
):
    root, _made = _written(tmp_path)
    (root / ARCHIVED).parent.mkdir(parents=True)
    (root / ONBOARDING_DOC).rename(root / ARCHIVED)

    # ⛔ Clause 2 on the corpus's own shape: the move is reported, not read as `[]`.
    assert hand_edited(root) == [gone(ONBOARDING_DOC)]

    # ⭐ The copy moved unchanged is the framework's, so it is rewritten, not refused.
    reonboard(root, settle={"onboarding_doc": ARCHIVED}).write(root, regenerate=True)

    assert not (root / ONBOARDING_DOC).exists(), "a regenerate wrote the root again"
    assert (root / ARCHIVED).is_file()
    assert hand_edited(root) == []
    globs = _globs(root)
    assert globs.get(ARCHIVED) == artifacts.WHY_READER
    assert ONBOARDING_DOC not in globs, "the old place stayed declared as somebody's glob"
    placed = [e["where"] for e in json.loads((root / RECORD_FILE).read_text("utf-8"))["files"]]
    assert ARCHIVED in placed and ONBOARDING_DOC not in placed

    # ⭐ R10: the next regenerate, with nothing settled, rewrites every byte as it was.
    before = _tree(root)
    reonboard(root).write(root, regenerate=True)
    assert _tree(root) == before
    assert not (root / ONBOARDING_DOC).exists()


def test_a_file_of_yours_at_the_new_place_is_still_refused(tmp_path):
    # ⛔ `W353` holds: only bytes the record holds for a generated path now EMPTY
    # are recognised as moved, so somebody's own document there is never taken.
    root, _made = _written(tmp_path)
    (root / ARCHIVED).parent.mkdir(parents=True)
    (root / ARCHIVED).write_text("# my own archive notes\n", encoding="utf-8")
    (root / ONBOARDING_DOC).unlink()

    with pytest.raises(OnboardingRefused, match="not known to be the framework's"):
        reonboard(root, settle={"onboarding_doc": ARCHIVED}).write(root, regenerate=True)
    assert (root / ARCHIVED).read_text(encoding="utf-8") == "# my own archive notes\n"


def test_a_copy_of_a_generated_file_still_in_place_is_not_taken_as_moved(tmp_path):
    root, _made = _written(tmp_path)
    (root / ARCHIVED).parent.mkdir(parents=True)
    (root / ARCHIVED).write_bytes((root / ONBOARDING_DOC).read_bytes())

    with pytest.raises(OnboardingRefused, match="not known to be the framework's"):
        reonboard(root, settle={"onboarding_doc": ARCHIVED}).write(root, regenerate=True)


# --------------------------------------------------------------------------
# ⛔ The place is a corpus path of its own, and a refusal never quotes it (R7)
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "/srv/elsewhere/ONBOARDING.md",
        "../ONBOARDING.md",
        "./ONBOARDING.md",
        "docs//ONBOARDING.md",
        "docs/*.md",
        "docs\\ONBOARDING.md",
        "ONBOARDING.txt",
        ".md",
        "",
        True,
        None,
        3,
    ],
)
def test_a_place_that_is_not_a_corpus_markdown_path_is_refused_without_quoting_it(value):
    with pytest.raises(ManifestError, match="'onboarding_doc' must be false") as raised:
        onboarding_doc_of(value, "corpus.json")
    if isinstance(value, str) and ("/" in value or "ONBOARDING" in value):
        # ⭐ A bare `.md` is in the rule itself; every value that could be a path is not.
        assert value not in str(raised.value)


def test_a_clean_place_and_false_are_read_back_as_declared():
    assert onboarding_doc_of(ARCHIVED, "corpus.json") == ARCHIVED
    assert onboarding_doc_of(False, "corpus.json") is None


@pytest.mark.parametrize(
    "place", [f"{PIN_DIR}/skills/adapter.md", f"{PIN_DIR}/notes.md", "archive/ONBOARDING.md"]
)
def test_a_place_another_writer_owns_is_refused_before_anything_is_planned(tmp_path, place):
    with pytest.raises(OnboardingRefused, match="onboarding_doc"):
        onboard(corpora.draft(onboarding_doc=place), framework_commit=corpora.COMMIT)


# --------------------------------------------------------------------------
# ⛔ Clause 2: a generated file missing from its recorded place is reported (R6)
# --------------------------------------------------------------------------


def test_every_generated_file_missing_from_its_recorded_place_is_reported(tmp_path):
    root, made = _written(tmp_path)
    generated = [item.where for item in made.files if item.generated and item.where != RECORD_FILE]
    assert ONBOARDING_DOC in generated, "the population moved"

    for where in generated:
        path = root / where
        kept = path.read_bytes()
        path.unlink()
        assert hand_edited(root) == [gone(where)], where
        path.write_bytes(kept)

    assert hand_edited(root) == []


def test_the_person_s_own_module_missing_is_theirs_and_never_reported(tmp_path):
    root, made = _written(tmp_path)
    (root / made.hand_written[0]).unlink()

    assert hand_edited(root) == []


def test_a_gap_is_a_sentence_a_person_reads_and_names_no_absolute_path(tmp_path):
    root, _made = _written(tmp_path)
    (root / ONBOARDING_DOC).unlink()

    (said,) = hand_edited(root)

    assert said.startswith(f"{ONBOARDING_DOC} is missing: {RECORD_FILE} records it")
    assert "regenerate" in said and artifacts.MANIFEST in said
    assert str(tmp_path) not in said


def test_an_edit_and_a_gap_are_both_reported_the_edit_first(tmp_path):
    root, _made = _written(tmp_path)
    (root / ONBOARDING_DOC).unlink()
    pin = root / artifacts.PIN_FILE
    pin.write_text(pin.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    assert hand_edited(root) == [artifacts.PIN_FILE, gone(ONBOARDING_DOC)]
