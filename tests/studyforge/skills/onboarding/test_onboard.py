"""Mirror of `src/studyforge/skills/onboarding/onboard.py` (R12).

⭐ **The property this file exists for is the one the design rests on:** the
manifest is promoted twice, and the second pass must not change what the first
one scaffolded. If it ever does, the two-pass is load-bearing rather than a
convenience, and that is a defect this test reports rather than hides.
"""

from __future__ import annotations

import json

import pytest

from studyforge.corpus.manifest import Classification, parse
from studyforge.skills.adapter import ScaffoldRefused, plan_for, scaffold
from studyforge.skills.adapter.scaffold import bytecode_ignores
from studyforge.skills.onboarding import artifacts
from studyforge.skills.onboarding.manifest import PromotionRefused
from studyforge.skills.onboarding.onboard import onboard
from studyforge.skills.onboarding.pin import RECORD_FILE
from studyforge.skills.onboarding.record import INSTALLED_API, OnboardingRefused
from tests.studyforge.skills.onboarding import corpora
from tests.support import init_repository, is_ignored


def _made(**changes):
    return onboard(corpora.draft(**changes), framework_commit=corpora.COMMIT)


def _media_ignores(made):
    """The ignore files the media policy asked for: every one but the bytecode files."""
    bytecode = bytecode_ignores(made.paths)
    return [w for w in made.paths if w.rsplit("/", 1)[-1] == ".gitignore" and w not in bytecode]


def test_re_scaffolding_from_the_written_manifest_changes_nothing():
    # ⛔ The two-pass promotion's honesty check. A scaffold varies only on what
    # `Plan` carries, and `content.not_material` is none of it — so the files
    # planned from the provisional manifest must equal those planned from the
    # written one, byte for byte.
    made = _made()
    written = parse(next(item.text for item in made.files if item.where == artifacts.MANIFEST))

    again = scaffold(plan_for(written))

    planned = {item.where: item.text for item in made.files}
    assert all(planned[item.where] == item.text for item in again.files)


def test_exactly_one_file_is_a_persons():
    # ⭐ R19's promise, said in one breath.
    assert _made().hand_written == ("ingest/read.py",)


def test_the_adapters_globs_are_in_the_manifest_without_anybody_copying_them():
    # ⛔ No person copies lines out of a report: the scaffold's own globs are
    # already in the document that gets written.
    made = _made()
    manifest = parse(next(item.text for item in made.files if item.where == artifacts.MANIFEST))

    globs = {entry.glob for entry in manifest.content.not_material}
    assert {"ingest/**", "tests/ingest/**"} <= globs, "the adapter's own globs were not carried"
    assert {entry["glob"] for entry in artifacts.NOT_MATERIAL} <= globs, (
        "this skill's own output was not declared either"
    )


def _notes_draft(*entries):
    return corpora.draft(content={**corpora.DRAFT["content"], "not_material": list(entries)})


def test_a_persons_not_material_block_survives_onboarding():
    # ⛔ A draft carrying a block, onboarded.
    made = onboard(_notes_draft(corpora.NOTES), framework_commit=corpora.COMMIT)
    manifest = parse(next(item.text for item in made.files if item.where == artifacts.MANIFEST))

    assert corpora.NOTES in made.not_material
    assert manifest.content.classify("notes/a.txt") is Classification.NOT_MATERIAL
    assert {"ingest/**", "tests/ingest/**"} <= {
        entry.glob for entry in manifest.content.not_material
    }


def test_a_drafted_glob_the_scaffold_also_generates_is_refused():
    # ⚠️ Only the SECOND promotion can see this: the provisional pass has no
    # scaffold yet, so a refusal here proves the check runs where it must.
    mine = {"glob": "ingest/**", "why": "a person's reason for the adapter directory"}

    with pytest.raises(PromotionRefused) as refused:
        onboard(_notes_draft(mine), framework_commit=corpora.COMMIT)

    assert "ingest/**" in str(refused.value) and "content.not_material[0]" in str(refused.value)


def test_every_file_it_writes_is_declared_in_the_manifest_it_writes():
    made = _made()
    manifest = parse(next(item.text for item in made.files if item.where == artifacts.MANIFEST))

    unclassified = [
        item.where
        for item in made.files
        if item.where != artifacts.MANIFEST
        and manifest.content.classify(item.where) is not Classification.NOT_MATERIAL
    ]
    assert not unclassified, f"the manifest it writes does not classify: {unclassified}"


def test_it_writes_everything_or_nothing(tmp_path):
    root = corpora.material(tmp_path / "corpus")
    (root / "ONBOARDING.md").write_text("mine\n", encoding="utf-8")

    made = _made()
    with pytest.raises(OnboardingRefused) as refused:
        made.write(root)

    assert "ONBOARDING.md" in str(refused.value)
    assert not (root / "corpus.json").exists(), "a refused write left something behind"


def test_every_collision_is_named_at_once(tmp_path):
    root = corpora.material(tmp_path / "corpus")
    (root / "ONBOARDING.md").write_text("mine\n", encoding="utf-8")
    (root / "corpus.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(OnboardingRefused) as refused:
        _made().write(root)

    message = str(refused.value)
    assert "ONBOARDING.md" in message and "corpus.json" in message


def test_a_refusal_names_no_absolute_path(tmp_path):
    # ⛔ R7: the first thing an integrator does with a refusal is paste it.
    root = corpora.material(tmp_path / "corpus")
    (root / "ONBOARDING.md").write_text("mine\n", encoding="utf-8")

    with pytest.raises(OnboardingRefused) as refused:
        _made().write(root)

    assert str(tmp_path) not in str(refused.value)


def test_regenerating_rewrites_the_generated_files_and_keeps_the_one_that_is_yours(tmp_path):
    # ⭐ After step 4 the hand-written file always exists, so refusing on it
    # would make "regenerate rather than hand-edit" advice nobody can follow (R19).
    root = corpora.material(tmp_path / "corpus")
    made = _made()
    made.write(root)
    (root / made.hand_written[0]).write_text("# mine\n", encoding="utf-8")
    (root / artifacts.READER_DOC).write_text("edited by hand\n", encoding="utf-8")

    with pytest.raises(OnboardingRefused):
        made.write(root)
    written = made.write(root, regenerate=True)

    assert "edited by hand" not in (root / artifacts.READER_DOC).read_text(encoding="utf-8")
    assert (root / made.hand_written[0]).read_text(encoding="utf-8") == "# mine\n"
    assert made.hand_written[0] not in written, "a regeneration reported writing somebody's file"


def _both_writers(made):
    """Onboarding's writer, and the scaffold's own, over one onboarding's plan."""
    return {"onboarding": made, "scaffold": scaffold(plan_for(made.manifest))}


@pytest.mark.parametrize("writer", ["onboarding", "scaffold"])
def test_both_writers_keep_an_edited_hand_written_module_on_a_regenerate(tmp_path, writer):
    # ⛔ Both writers must agree on this fixture: each keeps the file, and
    # neither refuses the whole write.
    root = corpora.material(tmp_path / "corpus")
    made = _made()
    made.write(root)
    chosen = _both_writers(made)[writer]
    assert chosen.hand_written == made.hand_written, "the two writers name different seams"
    mine = root / made.hand_written[0]
    mine.write_text("# mine\n", encoding="utf-8")
    before = mine.read_bytes()

    written = chosen.write(root, regenerate=True)

    assert mine.read_bytes() == before, f"{writer}'s regenerate rewrote the person's module"
    assert made.hand_written[0] not in written
    expected = set(chosen.paths) - set(made.hand_written)
    assert set(written) == expected, f"{writer} wrote {sorted(set(written) ^ expected)} otherwise"


@pytest.mark.parametrize("writer", ["onboarding", "scaffold"])
def test_both_writers_refuse_a_first_write_over_the_hand_written_module_by_name(tmp_path, writer):
    root = corpora.material(tmp_path / "corpus")
    made = _made()
    mine = root / made.hand_written[0]
    mine.parent.mkdir(parents=True)
    mine.write_text("# mine\n", encoding="utf-8")

    with pytest.raises((OnboardingRefused, ScaffoldRefused)) as refused:
        _both_writers(made)[writer].write(root)

    assert made.hand_written[0] in str(refused.value)
    assert mine.read_text(encoding="utf-8") == "# mine\n"
    assert not (root / "corpus.json").exists(), f"{writer} wrote something anyway"


def test_running_it_twice_produces_the_same_bytes():
    # ⭐ The skill's acceptance: re-running changes nothing.
    first = {item.where: item.text for item in _made().files}
    second = {item.where: item.text for item in _made().files}

    assert first == second


def test_the_record_carries_a_digest_for_every_other_file(tmp_path):
    root = corpora.material(tmp_path / "corpus")
    made = _made()
    made.write(root)

    record = json.loads((root / RECORD_FILE).read_text(encoding="utf-8"))
    assert record["installed_api"] == INSTALLED_API
    assert [entry["where"] for entry in record["files"]] == [
        item.where for item in made.files if item.where != RECORD_FILE
    ]


def test_the_report_names_every_path_and_the_one_that_is_yours():
    lines = "\n".join(_made().lines())

    assert "corpus.json" in lines
    assert "ingest/read.py" in lines
    assert "1 to write" in lines
    assert "studyforge validate" in lines


def test_a_write_from_another_library_than_the_pin_names_is_refused_and_writes_nothing(
    tmp_path, monkeypatch
):
    # ⛔ The pin names the library it was made by; a write run by
    # another version would record a pin this Python does not import.
    from studyforge.skills.onboarding import library
    from studyforge.skills.onboarding.pin import PinRefused

    root = corpora.material(tmp_path / "corpus")
    before = sorted(path for path in root.rglob("*"))
    made = onboard(corpora.DRAFT, framework_commit=corpora.COMMIT)
    monkeypatch.setattr(library, "version", lambda: "0.0.1")

    with pytest.raises(PinRefused, match="the library running it is 0.0.1"):
        made.write(root)

    assert sorted(path for path in root.rglob("*")) == before


def test_a_library_whose_version_cannot_be_read_is_refused_before_anything_is_planned(
    monkeypatch,
):
    from studyforge.skills.onboarding import library
    from studyforge.skills.onboarding.pin import PinRefused

    def unreadable():
        raise library.LibraryRefused("no version here")

    monkeypatch.setattr(library, "version", unreadable)

    with pytest.raises(PinRefused, match="no version here"):
        onboard(corpora.DRAFT, framework_commit=corpora.COMMIT)


def test_the_report_names_the_library_it_pins():
    from studyforge.skills.onboarding.library import version

    assert f"studyforge {version()}, built from {corpora.COMMIT}" in "\n".join(_made().lines())


def test_the_pin_is_refused_before_anything_is_planned():
    with pytest.raises(Exception) as refused:
        onboard(corpora.DRAFT, framework_commit="../studyforge")

    assert "commit" in str(refused.value)


# --------------------------------------------------------------------------
# ⛔ A build's output is committed; ignore rules live in a file inside
# the generated root, or nowhere
# --------------------------------------------------------------------------


@pytest.mark.parametrize("placement", ["tree", "sibling"])
def test_with_media_committed_the_one_ignore_file_is_the_frameworks_own(placement, tmp_path):
    # ⛔ For the CORPUS: no page, no clip and no index is
    # ignored when media is committed. ⭐ The one exception is not
    # the corpus's — the discovery cache `studyforge serve` writes, and the
    # file hides itself because a clone has no use for either.
    made = _made(placement=placement)
    root = corpora.material(init_repository(tmp_path / "corpus"))
    made.write(root)

    assert _media_ignores(made) == [".studyforge/.gitignore"]
    assert not (root / ".gitignore").exists()
    assert is_ignored(".studyforge/site.json", cwd=root)
    assert is_ignored(".studyforge/.gitignore", cwd=root)
    assert not is_ignored(".studyforge/course/units/unit-01/audio/c.mp3", cwd=root)


def test_media_that_is_not_committed_is_ignored_from_inside_the_generated_root(tmp_path):
    made = _made(media={"commit": "never"})
    root = corpora.material(init_repository(tmp_path / "corpus"))
    made.write(root)

    assert _media_ignores(made) == [".studyforge/.gitignore"]
    assert not (root / ".gitignore").exists()
    assert is_ignored(".studyforge/course/units/unit-01/audio/c.mp3", cwd=root)
    # ⭐ The cache is covered here too, and this file does NOT hide
    # itself — a clone has to read the media rules it also carries.
    assert is_ignored(".studyforge/site.json", cwd=root)
    assert not is_ignored(".studyforge/.gitignore", cwd=root)
    assert not is_ignored(".studyforge/course/units/unit-01/a.unit.html", cwd=root)


def test_media_that_is_not_committed_under_sibling_is_refused_before_anything_is_written():
    with pytest.raises(OnboardingRefused) as refused:
        _made(placement="sibling", media={"commit": "never"})

    assert "is never edited" in str(refused.value)


# --------------------------------------------------------------------------
# ⛔ Re-onboarding keeps every not_material glob the manifest declares
# --------------------------------------------------------------------------

#: A second person's glob after `corpora.NOTES`, so the ORDER is asserted too.
LOGS = {"glob": "logs/*.txt", "why": "the integrator's run logs, which no unit reads"}


def _onboarded(tmp_path):
    """A corpus first onboarded from a draft carrying two person's globs."""
    root = corpora.material(tmp_path / "corpus")
    onboard(_notes_draft(corpora.NOTES, LOGS), framework_commit=corpora.COMMIT).write(root)
    return root, (root / "corpus.json").read_bytes()


def _declared(root):
    return json.loads((root / "corpus.json").read_text(encoding="utf-8"))["content"]["not_material"]


def test_only_onboardings_write_writes_corpus_json_and_the_scaffolds_regenerate_never_does(
    tmp_path,
):
    # ⭐ The brief's question. `onboard` and `promote` do no I/O; `Onboarding.write`
    # writes the manifest, on a regenerate too; the adapter's regenerate never does.
    root, before = _onboarded(tmp_path)
    made = onboard(corpora.DRAFT, framework_commit=corpora.COMMIT, existing=before.decode())
    assert (root / "corpus.json").read_bytes() == before, "onboard() wrote the manifest"

    scaffold(plan_for(made.manifest)).write(root, regenerate=True)
    assert (root / "corpus.json").read_bytes() == before, "the scaffold's regenerate touched it"

    assert "corpus.json" in made.write(root, regenerate=True)


def test_a_re_onboarding_from_a_resurvey_draft_keeps_every_declared_glob_byte_for_byte(tmp_path):
    # ⛔ Clause 1, the witness: a re-survey drafts no glob the manifest covers,
    # so the draft carries none. The manifest is regenerated byte-identical.
    root, before = _onboarded(tmp_path)

    made = onboard(corpora.DRAFT, framework_commit=corpora.COMMIT, existing=before.decode())
    made.write(root, regenerate=True)

    assert (root / "corpus.json").read_bytes() == before
    assert _declared(root)[:2] == [corpora.NOTES, LOGS]
    globs = [entry["glob"] for entry in _declared(root)]
    assert len(globs) == len(set(globs)), "a generated glob was carried as a person's too"


def test_a_regenerate_that_would_drop_a_declared_glob_refuses_by_name_and_writes_nothing(tmp_path):
    # ⛔ Clause 1's other arm: a caller who never passes `existing` loses nothing.
    root, before = _onboarded(tmp_path)
    (root / artifacts.READER_DOC).write_text("edited by hand\n", encoding="utf-8")

    with pytest.raises(OnboardingRefused) as refused:
        _made().write(root, regenerate=True)

    message = str(refused.value)
    assert "notes/**" in message and "logs/*.txt" in message and "existing=" in message
    assert (root / "corpus.json").read_bytes() == before
    assert (root / artifacts.READER_DOC).read_text(encoding="utf-8") == "edited by hand\n"


def test_a_drafted_glob_given_another_reason_is_refused_by_name_never_by_precedence(tmp_path):
    _, before = _onboarded(tmp_path)
    other = {"glob": corpora.NOTES["glob"], "why": "a different reason for the same notes"}

    with pytest.raises(OnboardingRefused) as refused:
        onboard(_notes_draft(other), framework_commit=corpora.COMMIT, existing=before.decode())

    assert "notes/**" in str(refused.value) and "logs/*.txt" not in str(refused.value)


def test_a_drafted_glob_the_manifest_declares_is_not_added_twice_and_a_new_one_follows(tmp_path):
    # ⭐ Never widened or narrowed: kept first as written, then the draft's new glob.
    _, before = _onboarded(tmp_path)
    fresh = {"glob": "extra/**", "why": "material a person set aside after onboarding"}
    draft = _notes_draft(corpora.NOTES, {"glob": LOGS["glob"], "why": None}, fresh)

    made = onboard(draft, framework_commit=corpora.COMMIT, existing=before.decode())

    assert list(made.not_material[:3]) == [corpora.NOTES, LOGS, fresh]
    globs = [entry["glob"] for entry in made.not_material]
    assert len(globs) == len(set(globs))


def test_a_first_onboarding_with_no_manifest_is_unchanged(tmp_path):
    # ⭐ Clause 2: no `existing`, the same files; no manifest on disk, no refusal.
    first = {item.where: item.text for item in _made().files}
    assert first == {
        item.where: item.text
        for item in onboard(corpora.DRAFT, framework_commit=corpora.COMMIT, existing=None).files
    }
    root = corpora.material(tmp_path / "corpus")

    written = _made().write(root, regenerate=True)

    assert (
        "corpus.json" in written
        and (root / "corpus.json").read_text(encoding="utf-8") == (first["corpus.json"])
    )


def test_a_manifest_that_does_not_parse_is_refused_by_name_rather_than_overwritten(tmp_path):
    with pytest.raises(OnboardingRefused, match="existing corpus.json does not parse"):
        onboard(corpora.DRAFT, framework_commit=corpora.COMMIT, existing="{}\n")
    root = corpora.material(tmp_path / "corpus")
    _made().write(root)
    (root / "corpus.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(OnboardingRefused, match="cannot be kept"):
        _made().write(root, regenerate=True)

    assert (root / "corpus.json").read_text(encoding="utf-8") == "{}\n"


# --------------------------------------------------------------------------
# ⛔ What is written never depends on which checkout wrote it (R10)
# --------------------------------------------------------------------------


def _both_checkouts(tmp_path):
    """One corpus repository as a main checkout AND a linked worktree, nothing beside either.

    ⭐ The same material in both, so the only difference between them is the
    checkout the skill runs in — which is the one thing that must move no byte.
    """
    worktree = corpora.material(corpora.linked_worktree(tmp_path))
    main = corpora.material(tmp_path / "corpus")
    return main, worktree


def _generated_bytes(root, paths):
    return {where: (root / where).read_bytes() for where in paths}


def test_a_worktree_and_its_main_checkout_write_byte_identical_files(tmp_path):
    # ⛔ The row itself: an onboard and a reonboard, each run once from the main
    # checkout and once from a linked worktree of the SAME repository, write the
    # same bytes — every stub, the reader's document, and `installed.json`.
    from studyforge.skills.onboarding import reonboard

    main, worktree = _both_checkouts(tmp_path)
    written = {}
    for root in (main, worktree):
        made = onboard(corpora.DRAFT, framework_commit=corpora.COMMIT, root=root)
        made.write(root)
        first = _generated_bytes(root, made.paths)
        reonboard(root).write(root, regenerate=True)
        written[root] = (first, _generated_bytes(root, made.paths))

    assert written[main] == written[worktree]
    assert written[main][0] == written[main][1]
    assert RECORD_FILE in written[main][0] and artifacts.READER_DOC in written[main][0]


def test_no_root_named_writes_into_a_worktree_rather_than_being_refused(tmp_path):
    # ⭐ There is no address at all, so a document composed without `root`
    # cannot disagree with one.
    _main, worktree = _both_checkouts(tmp_path)

    written = onboard(corpora.DRAFT, framework_commit=corpora.COMMIT).write(worktree)

    assert artifacts.READER_DOC in written


def test_a_worktree_anywhere_is_written_and_names_no_path_to_the_framework(tmp_path):
    # ⚠️ A worktree anywhere on disk. ⭐ The library is installed, so
    # where the checkout sits does not enter what is written.
    main = tmp_path / "here" / "corpus"
    corpora.linked_worktree(tmp_path / "here")
    elsewhere = tmp_path / "there" / "two"
    corpora.git(main, "worktree", "add", "-q", str(elsewhere))
    corpora.material(elsewhere)

    onboard(corpora.DRAFT, framework_commit=corpora.COMMIT, root=elsewhere).write(elsewhere)

    text = (elsewhere / artifacts.READER_DOC).read_text(encoding="utf-8")
    assert "python3 -m studyforge.skills.onboarding.verify ." in text
    assert "../studyforge" not in text and str(tmp_path) not in text
