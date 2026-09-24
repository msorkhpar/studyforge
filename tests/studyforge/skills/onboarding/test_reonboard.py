"""Mirror of `src/studyforge/skills/onboarding/reonboard.py` (R12).

⭐ **The property this file exists for:** a change to an onboarded corpus's
manifest enters as DATA and lands through a regenerate, so `hand_edited` reads
`[]` afterwards — and the hand-typed entry the authoring guide once prescribed
is named by it, which is the negative that makes the positive mean something.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import json

import pytest

from studyforge.skills.onboarding import (
    artifacts,
    hand_edited,
    library,
    onboard,
    recorded_draft,
    reonboard,
)
from studyforge.skills.onboarding.manifest import PromotionRefused
from studyforge.skills.onboarding.pin import PIN_FILE, stub_paths
from studyforge.skills.onboarding.record import OnboardingRefused
from tests.studyforge.skills.onboarding import corpora

#: What an exercise authoring run adds, in the guide's shape (a glob and a reason).
ADDED = (
    {"glob": "exercises/**", "why": "authored exercise bundles and their gate records"},
    {"glob": "practice/**", "why": "the reader's own workspace files, from each bundle"},
)


def _onboarded(tmp_path, draft=corpora.DRAFT):
    root = corpora.material(tmp_path / "corpus")
    onboard(draft, framework_commit=corpora.COMMIT, root=root).write(root)
    assert hand_edited(root) == [], "the control: a fresh onboarding is not hand-edited"
    return root


def _manifest(root):
    return json.loads((root / artifacts.MANIFEST).read_text(encoding="utf-8"))


def _globs(root):
    return [entry["glob"] for entry in _manifest(root)["content"]["not_material"]]


# --- the path, and its negative ---------------------------------------------


def test_a_regenerate_with_nothing_changed_writes_the_same_manifest_byte_for_byte(tmp_path):
    root = _onboarded(tmp_path)
    before = (root / artifacts.MANIFEST).read_bytes()

    reonboard(root).write(root, regenerate=True)

    assert (root / artifacts.MANIFEST).read_bytes() == before
    assert hand_edited(root) == []


def test_globs_entered_as_data_land_and_nothing_generated_reads_as_hand_edited(tmp_path):
    root = _onboarded(tmp_path)

    reonboard(root, not_material=ADDED).write(root, regenerate=True)

    assert hand_edited(root) == []
    declared = _manifest(root)["content"]["not_material"]
    assert [entry for entry in declared if entry["glob"] in {"exercises/**", "practice/**"}] == [
        dict(entry) for entry in ADDED
    ]
    assert len(_globs(root)) == len(set(_globs(root))), "a generated glob was declared twice"


def test_a_hand_typed_not_material_entry_is_named(tmp_path):
    # ⛔ The negative at its smallest: ONE entry
    # typed into `corpus.json` by hand is an R19 finding against the corpus.
    root = _onboarded(tmp_path)
    document = _manifest(root)
    document["content"]["not_material"].append(dict(ADDED[0]))
    (root / artifacts.MANIFEST).write_text(json.dumps(document, indent=2) + "\n", "utf-8")

    assert hand_edited(root) == [artifacts.MANIFEST]


def test_a_persons_recorded_glob_is_kept_byte_for_byte_and_the_new_one_follows(tmp_path):
    root = _onboarded(tmp_path, corpora.SETTLED)
    kept = _manifest(root)["content"]["not_material"][0]

    reonboard(root, not_material=ADDED[:1]).write(root, regenerate=True)

    declared = _manifest(root)["content"]["not_material"]
    assert declared[:2] == [kept, dict(ADDED[0])]
    assert hand_edited(root) == []


def test_a_glob_the_skill_generates_is_refused_rather_than_declared_twice(tmp_path):
    # ⛔ Retyped with the generator's own reason it is a collision; with another
    # reason it is a re-reasoned recorded glob. Either way it is named, never kept.
    root = _onboarded(tmp_path)
    retyped = _manifest(root)["content"]["not_material"][0]
    assert retyped["glob"] in reonboard(root).generated

    with pytest.raises(PromotionRefused, match="also generated"):
        reonboard(root, not_material=[retyped])
    with pytest.raises(OnboardingRefused, match="another reason"):
        reonboard(root, not_material=[{**retyped, "why": "a person retyping a generated glob"}])


# --- an answer moves only when it is named ------------------------------------


def test_a_settled_answer_moves_and_the_record_follows_it(tmp_path):
    root = _onboarded(tmp_path)

    reonboard(root, not_material=ADDED, settle={"exercises": True}).write(root, regenerate=True)

    assert _manifest(root)["exercises"] is True
    assert hand_edited(root) == []


def test_an_answer_nobody_settled_is_still_refused_by_name(tmp_path):
    # ⛔ The refusal is narrowed to what a person named, never switched off.
    root = _onboarded(tmp_path)
    moved = reonboard(root, settle={"exercises": True})
    unnamed = dataclasses.replace(moved, settled=("title",))

    with pytest.raises(OnboardingRefused, match="exercises"):
        unnamed.write(root, regenerate=True)
    assert _manifest(root)["exercises"] is False


@pytest.mark.parametrize("key", ["content", "not_a_field"])
def test_settle_takes_only_the_manifests_own_top_level_answers(tmp_path, key):
    root = _onboarded(tmp_path)

    with pytest.raises(OnboardingRefused, match=key):
        reonboard(root, settle={key: True})


def test_the_recorded_draft_carries_only_the_globs_it_is_given():
    # ⭐ What the manifest already declares arrives through `existing=`, so this
    # never has to know which glob a generator owns.
    text = onboard(corpora.SETTLED, framework_commit=corpora.COMMIT).files[0].text

    draft = recorded_draft(text, not_material=ADDED[:1])

    assert draft["content"]["not_material"] == [dict(ADDED[0])]
    assert {key: value for key, value in draft.items() if key != "content"} == {
        key: value for key, value in json.loads(text).items() if key != "content"
    }


def test_a_corpus_never_onboarded_is_refused_by_name(tmp_path):
    root = corpora.material(tmp_path / "corpus")

    with pytest.raises(OnboardingRefused, match="never onboarded"):
        reonboard(root)


# --- the pin: moved by a regenerate, or refused by the corpus's own check ------


#: A second commit, as an operator re-pinning would pass it (checked for shape only).
SECOND = "b" * 40


def _drift_check(root):
    """The pin-drift test the onboarding generated into `root`, loaded as its suite would."""
    spec = importlib.util.spec_from_file_location("generated_pin", root / artifacts.PIN_TEST)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded.test_no_stub_has_drifted_from_the_pin


def test_a_re_pin_through_the_skill_moves_the_pin_and_every_stub_together(tmp_path):
    root = _onboarded(tmp_path)

    reonboard(root, framework_commit=SECOND).write(root, regenerate=True)

    assert json.loads((root / PIN_FILE).read_text(encoding="utf-8"))["commit"] == SECOND
    assert all(f"pin: {SECOND}" in (root / where).read_text("utf-8") for where in stub_paths())
    _drift_check(root)()
    assert hand_edited(root) == []


def test_a_pin_moved_by_hand_is_refused_by_the_corpus_side_check_and_named(tmp_path):
    # ⛔ At its smallest: the pin advanced, the stubs left behind.
    root = _onboarded(tmp_path)
    pinned = root / PIN_FILE
    document = json.loads(pinned.read_text(encoding="utf-8"))
    pinned.write_text(json.dumps({**document, "commit": SECOND}), "utf-8")

    with pytest.raises(AssertionError, match="name a commit or a version the pin does not"):
        _drift_check(root)()
    assert hand_edited(root) == [PIN_FILE]


# --- a pin that no longer names the library running this -------------------


#: The pin a corpus onboarded before installed-library pins carries: a sibling checkout at a commit.
SIBLING_PIN = {
    "pin_api": 1,
    "framework": "studyforge",
    "where": "sibling",
    "commit": corpora.COMMIT,
    "skills": ["reconnaissance", "adapter", "onboarding"],
}


def test_a_pin_from_before_the_installed_library_is_refused_without_a_re_pin(tmp_path):
    root = _onboarded(tmp_path)
    (root / PIN_FILE).write_text(json.dumps(SIBLING_PIN), encoding="utf-8")

    with pytest.raises(OnboardingRefused, match="predates the installed library"):
        reonboard(root)


def test_a_pin_from_before_the_installed_library_migrates_with_a_re_pin(tmp_path):
    # ⭐ The one step an already-onboarded corpus runs: re-pin from the library.
    root = _onboarded(tmp_path)
    (root / PIN_FILE).write_text(json.dumps(SIBLING_PIN), encoding="utf-8")

    reonboard(root, framework_commit=SECOND).write(root, regenerate=True)

    pinned = json.loads((root / PIN_FILE).read_text(encoding="utf-8"))
    assert (pinned["where"], pinned["version"], pinned["commit"]) == (
        "installed",
        library.version(),
        SECOND,
    )
    _drift_check(root)()
    assert hand_edited(root) == []


def test_a_pin_naming_another_version_is_refused_without_a_re_pin(tmp_path, monkeypatch):
    root = _onboarded(tmp_path)
    monkeypatch.setattr(library, "version", lambda: "9.9.9")

    with pytest.raises(OnboardingRefused, match="other than the 9.9.9 running this"):
        reonboard(root)


def test_a_pin_naming_another_commit_than_a_built_library_is_refused_until_re_pinned(
    tmp_path, monkeypatch
):
    # ⭐ A built wheel knows its commit, so a pin naming another is stale.
    from studyforge.skills.onboarding import library

    root = corpora.material(tmp_path / "corpus")
    onboard(corpora.DRAFT, framework_commit=corpora.COMMIT).write(root)
    monkeypatch.setattr(library, "commit", lambda: "b" * 40)

    with pytest.raises(OnboardingRefused, match="another commit than the one running"):
        reonboard(root)
    reonboard(root, framework_commit="b" * 40).write(root, regenerate=True)

    assert json.loads((root / PIN_FILE).read_text(encoding="utf-8"))["commit"] == "b" * 40
