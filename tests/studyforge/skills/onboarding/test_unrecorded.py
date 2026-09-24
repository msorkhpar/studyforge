"""End to end: a regeneration never takes a person's file at a newly generated path.

⭐ **The clauses, through `Onboarding.write`, each asserted both ways (clause 3, R12):**

1. a regenerate refuses, by name, to write ANY generated path that is already on
   disk and that the install record does not list as generated — not only the
   ignore files — and writes nothing at all;
2. a corpus whose record PREDATES a path (a later framework added it) gains it
   when the path is free, and is refused when something is already there —
   ⛔ even bytes identical to the framework's: the decision is to refuse, never
   to adopt, because adopting is silent. ⭐ A missing record is the limit of
   the same case — it predates every path — so it claims nothing on disk.

⚠️ The corpus is a fabricated one under pytest's `tmp_path`; nothing real is read.
"""

from __future__ import annotations

import json

import pytest

from studyforge.skills.onboarding import artifacts, record
from studyforge.skills.onboarding.onboard import onboard
from studyforge.skills.onboarding.pin import RECORD_FILE
from studyforge.skills.onboarding.record import OnboardingRefused, hand_edited
from tests.studyforge.skills.onboarding import corpora

#: The path a later framework is taken to have added. ⭐ Deliberately not an
#: ignore file, so the guard is shown to reach beyond those.
ADDED = artifacts.READER_DOC


def _made():
    return onboard(corpora.draft(), framework_commit=corpora.COMMIT)


def _predating(tmp_path, *, added=ADDED):
    """A corpus onboarded by a framework that did not yet generate `added`."""
    root = corpora.material(tmp_path / "corpus")
    made = _made()
    made.write(root)
    (root / added).unlink()
    earlier = [item for item in made.files if item.where not in (added, RECORD_FILE)]
    (root / RECORD_FILE).write_text(record.render(earlier), encoding="utf-8")
    return root, made


def _tree(root):
    return {p: p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def _claimed(root):
    listed = json.loads((root / RECORD_FILE).read_text(encoding="utf-8"))["files"]
    return {entry["where"] for entry in listed if entry.get("hand_written") is not True}


# --------------------------------------------------------------------------
# ⛔ Clause 1: any generated path, refused by name, and nothing written
# --------------------------------------------------------------------------


def test_a_persons_file_at_a_newly_generated_path_is_refused_by_name(tmp_path):
    root, _ = _predating(tmp_path)
    (root / ADDED).write_text("notes a person wrote first\n", encoding="utf-8")
    before = _tree(root)

    with pytest.raises(OnboardingRefused) as refused:
        _made().write(root, regenerate=True)

    assert f"['{ADDED}']" in str(refused.value)
    assert "does not list them as generated" in str(refused.value)
    assert str(tmp_path) not in str(refused.value)
    assert _tree(root) == before, "a refused regenerate wrote something"


def test_the_same_file_is_rewritten_once_the_record_lists_it_as_generated(tmp_path):
    # ⭐ The other way: the guard reads the record, not the name. A listed file
    # edited by hand is R19's finding (`hand_edited`), and a regenerate rewrites it.
    root = corpora.material(tmp_path / "corpus")
    made = _made()
    made.write(root)
    (root / ADDED).write_text("edited by hand\n", encoding="utf-8")
    assert ADDED in _claimed(root)

    written = made.write(root, regenerate=True)

    assert ADDED in written
    assert "edited by hand" not in (root / ADDED).read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# ⚠️ Clause 2: a record that predates a path — adopted never, gained when free
# --------------------------------------------------------------------------


def test_a_record_that_predates_a_free_path_gains_it_and_then_claims_it(tmp_path):
    root, made = _predating(tmp_path)
    assert ADDED not in _claimed(root)

    written = made.write(root, regenerate=True)

    assert ADDED in written and (root / ADDED).exists()
    assert ADDED in _claimed(root), "the regenerate wrote the path and did not record it"
    assert hand_edited(root) == []


def test_even_the_frameworks_own_bytes_at_an_unrecorded_path_are_refused_not_adopted(tmp_path):
    # ⛔ The decision: adoption would be silent, so it never happens. Nothing
    # proves who put identical bytes there, and the cost of refusing is one move.
    root, made = _predating(tmp_path)
    wanted = next(item.text for item in made.files if item.where == ADDED)
    (root / ADDED).write_text(wanted, encoding="utf-8")

    with pytest.raises(OnboardingRefused, match="move each aside"):
        made.write(root, regenerate=True)

    assert ADDED not in _claimed(root)


def test_the_persons_module_is_never_refused_whatever_the_record_says_of_it(tmp_path):
    # ⭐ It is left exactly as it is by `write_files`, so there is nothing to take.
    root, made = _predating(tmp_path)
    mine = root / made.hand_written[0]
    mine.write_text("# mine\n", encoding="utf-8")

    made.write(root, regenerate=True)

    assert mine.read_text(encoding="utf-8") == "# mine\n"


# --------------------------------------------------------------------------
# ⚠️ Clause 2's limit: no record at all claims nothing
# --------------------------------------------------------------------------


def test_with_no_record_every_generated_file_already_here_is_refused(tmp_path):
    root = corpora.material(tmp_path / "corpus")
    made = _made()
    made.write(root)
    (root / RECORD_FILE).unlink()
    before = _tree(root)

    with pytest.raises(OnboardingRefused) as refused:
        made.write(root, regenerate=True)

    message = str(refused.value)
    assert ADDED in message and artifacts.MANIFEST in message
    assert f"{RECORD_FILE} is not here" in message
    assert made.hand_written[0] not in message, "the person's module was named as taken"
    assert _tree(root) == before


def test_with_no_record_and_nothing_here_a_regenerate_writes_everything(tmp_path):
    root = corpora.material(tmp_path / "corpus")

    written = _made().write(root, regenerate=True)

    assert ADDED in written and RECORD_FILE in written
