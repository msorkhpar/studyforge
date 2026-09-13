"""Mirror of `src/studyforge/skills/reconnaissance/furniture.py` (R12, W249, `INT-07/2`).

⭐ The draft proposes the `not_material` globs and leaves every reason open.
⛔ Asserted both ways: a furnished source drafts its globs, and a control with
no furniture drafts none. SF-02 judges, and SK-07's `onboard` is the collision
check, never a restatement of it.
"""

from __future__ import annotations

import json

import pytest

from studyforge.corpus.manifest import Classification, ManifestError, parse
from studyforge.skills.onboarding import onboard
from studyforge.skills.reconnaissance import survey
from studyforge.skills.reconnaissance.furniture import propose
from studyforge.validate.source import source_files
from tests.studyforge.skills.reconnaissance import sources

#: A recorded commit nobody's checkout has. ⛔ A placeholder (R7).
COMMIT = "a" * 40


def globs(proposal):
    return [entry["glob"] for entry in proposal["content"].get("not_material", [])]


def test_a_furnished_source_drafts_a_glob_for_everything_no_include_reads(tmp_path):
    proposal = survey(sources.furnished(tmp_path / "c")).proposal
    assert globs(proposal) == sources.FURNISHED_GLOBS
    # ⛔ Only a file an include reads is withheld: the aggregate, and nothing else.
    assert proposal["content"]["exclude"] == ["src/Whole.md"]
    assert proposal["corpus_api"] == 2


def test_sf02_leaves_nothing_unclassified_once_a_person_gives_the_reasons(tmp_path):
    root = sources.furnished(tmp_path / "c")
    content = parse(json.dumps(sources.settled(survey(root).proposal))).content
    judged = [path.relative_to(root).as_posix() for path in source_files(root).files]
    assert len(judged) == 12
    verdicts = {where: content.classify(where) for where in judged}
    assert Classification.UNCLASSIFIED not in verdicts.values(), verdicts
    assert Classification.CONTESTED not in verdicts.values(), verdicts


def test_every_reason_is_left_open_and_sf02_refuses_the_draft_until_one_is_given(tmp_path):
    proposal = survey(sources.furnished(tmp_path / "c")).proposal
    assert all(entry["why"] is None for entry in proposal["content"]["not_material"])
    open_reasons = sources.settled(proposal)
    open_reasons["content"]["not_material"] = proposal["content"]["not_material"]
    with pytest.raises(ManifestError, match=r"not_material\[0\]\.why"):
        parse(json.dumps(open_reasons))


def test_the_open_reasons_are_asked_about_with_the_population_they_were_judged_over(tmp_path):
    asked = survey(sources.furnished(tmp_path / "c")).uncertainties
    [question] = [q for q in asked if "never material" in q.question]
    assert "7 glob(s)" in question.question
    assert "of 12 file(s)" in question.why


# --------------------------------------------------------------------------
# ⛔ no glob collides with SK-07's generated set, before or after onboarding
# --------------------------------------------------------------------------


def test_onboarding_takes_the_draft_and_a_resurvey_proposes_nothing_onboarding_wrote(tmp_path):
    root = sources.furnished(tmp_path / "c")
    first = survey(root).proposal
    made = onboard(first, framework_commit=COMMIT, reasons=sources.reasons(first))
    made.write(root)

    again = survey(root).proposal
    assert globs(again) == globs(first)
    # ⭐ `promote` refuses a drafted glob equal to a generated one, so this is the
    # collision check, asked of the owner rather than restated.
    remade = onboard(again, framework_commit=COMMIT, reasons=sources.reasons(again))
    declared = [entry["glob"] for entry in remade.not_material]
    assert len(declared) == len(set(declared))
    judged = [path.relative_to(root).as_posix() for path in source_files(root).files]
    verdicts = {where: remade.manifest.content.classify(where) for where in judged}
    assert Classification.UNCLASSIFIED not in verdicts.values(), verdicts


# --------------------------------------------------------------------------
# ⭐ the controls
# --------------------------------------------------------------------------


def test_a_source_with_no_furniture_drafts_a_glob_for_its_record_alone(tmp_path):
    proposal = survey(sources.aggregated(tmp_path / "c")).proposal
    assert globs(proposal) == ["README.md"]


def test_a_source_whose_every_file_is_read_drafts_no_not_material_at_all(tmp_path):
    root = sources.flat_prose(tmp_path / "c")
    (root / "README.md").unlink()
    proposal = survey(root).proposal
    assert "not_material" not in proposal["content"]
    assert proposal["corpus_api"] == 1
    assert not [q for q in survey(root).uncertainties if "never material" in q.question]


def test_a_directory_holding_a_read_file_is_never_swept_by_a_directory_glob(tmp_path):
    root = sources.furnished(tmp_path / "c")
    found = propose(root, ["src/*.md", "notes/two.md"], [])
    assert "notes/about/**" in found.globs and "notes/**" not in found.globs
    assert "src/.keep" in found.globs
    assert found.judged == 12
