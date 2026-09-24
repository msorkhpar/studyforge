"""Mirror of `src/studyforge/skills/reconnaissance/furniture.py` (R12).

⭐ The draft proposes the `not_material` globs and leaves every reason open.
⛔ Asserted both ways: a furnished source drafts its globs, and a control with
no furniture drafts none. The manifest reader judges, and onboarding is the collision
check, never a restatement of it.
⛔ A file a declared glob covers is never re-proposed, and a proposal that
stands down says so by name. Both asserted both ways.
"""

from __future__ import annotations

import json

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.manifest import KEY_VERSIONS, Classification, ManifestError, parse
from studyforge.skills.onboarding import RECORD_FILE, onboard
from studyforge.skills.reconnaissance import survey
from studyforge.skills.reconnaissance.furniture import propose
from studyforge.validate.source import source_files
from tests.studyforge.skills.onboarding import corpora
from tests.studyforge.skills.reconnaissance import sources
from tests.support import init_repository

#: A recorded commit nobody's checkout has. ⛔ A placeholder (R7).
COMMIT = corpora.COMMIT


def globs(proposal):
    return [entry["glob"] for entry in proposal["content"].get("not_material", [])]


def test_a_furnished_source_drafts_a_glob_for_everything_no_include_reads(tmp_path):
    proposal = survey(sources.furnished(tmp_path / "c")).proposal
    assert globs(proposal) == sources.FURNISHED_GLOBS
    # ⛔ Only a file an include reads is withheld: the aggregate, and nothing else.
    assert proposal["content"]["exclude"] == ["src/Whole.md"]
    # ⭐ `not_material` needs 2; the record this source carries is drafted as
    # `curriculum` (`W340`), which needs more, and the draft asks for the higher.
    assert proposal["corpus_api"] == max(2, KEY_VERSIONS[(None, "curriculum")])
    assert "curriculum" in proposal


def test_the_manifest_reader_leaves_nothing_unclassified_once_a_person_gives_the_reasons(tmp_path):
    root = sources.furnished(tmp_path / "c")
    content = parse(json.dumps(sources.settled(survey(root).proposal))).content
    judged = [path.relative_to(root).as_posix() for path in source_files(root).files]
    assert len(judged) == 12
    verdicts = {where: content.classify(where) for where in judged}
    assert Classification.UNCLASSIFIED not in verdicts.values(), verdicts
    assert Classification.CONTESTED not in verdicts.values(), verdicts


def test_every_reason_is_left_open_and_the_draft_is_refused_until_one_is_given(tmp_path):
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
# ⛔ no glob collides with onboarding's generated set, before or after onboarding
# --------------------------------------------------------------------------


def test_onboarding_takes_the_draft_and_a_resurvey_re_proposes_nothing_it_declared(tmp_path):
    root = sources.furnished(tmp_path / "c")
    first = survey(root).proposal
    made = onboard(first, framework_commit=COMMIT, reasons=sources.reasons(first))
    made.write(root)

    again = survey(root).proposal
    # ⛔ The written manifest's globs cover every file, so none returns.
    assert globs(again) == []
    # ⭐ Onboarding still takes the re-survey's draft, and `promote` refuses a drafted glob equal
    # to a generated one, so this is the collision check, asked of the owner.
    remade = onboard(again, framework_commit=COMMIT, reasons=sources.reasons(again))
    declared = [entry["glob"] for entry in remade.not_material]
    assert len(declared) == len(set(declared))
    written = parse((root / "corpus.json").read_text(encoding="utf-8")).content
    judged = [path.relative_to(root).as_posix() for path in source_files(root).files]
    verdicts = {where: written.classify(where) for where in judged}
    assert Classification.UNCLASSIFIED not in verdicts.values(), verdicts


def test_an_onboarding_record_carrying_a_home_path_is_refused_as_itself(tmp_path):
    # ⛔ R7: the record is a list of paths, the shape a home directory arrives
    # in, so it is gated before a field is read. ⚠️ A placeholder, split so the
    # literal never sits in this file whole.
    root = sources.furnished(tmp_path / "c")
    record = root / RECORD_FILE
    record.parent.mkdir(parents=True)
    record.write_text(json.dumps({"files": [{"where": "/" + "home/jane/x"}]}), encoding="utf-8")
    with pytest.raises(PersonalDataLeak):
        propose(root, ["src/*.md"], [])


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


# --------------------------------------------------------------------------
# ⛔ A file a declared glob covers is never re-proposed
# --------------------------------------------------------------------------


def declare(root, *declared):
    """Write a manifest declaring `declared` as `not_material`, as onboarding would."""
    entries = [{"glob": glob, "why": sources.REASON} for glob in declared]
    manifest = {"content": {"not_material": entries}}
    (root / "corpus.json").write_text(json.dumps(manifest), encoding="utf-8")
    return root


def test_a_glob_at_DEPTH_keeps_what_it_covers_out_and_holds_its_directory(tmp_path):
    root = declare(sources.furnished(tmp_path / "c"), "notes/about/**", "LICENSE")
    # ⭐ `notes/**` would sweep a covered file again, so the uncovered one is named exactly.
    assert globs(survey(root).proposal) == [
        ".gitattributes",
        ".gitignore",
        "NOTES.md",
        "README.md",
        "notes/two.md",
        "src/.keep",
    ]
    assert propose(root, ["src/*.md"], ["src/Whole.md"]).covered == 2


def test_a_directory_ONLY_PARTLY_covered_proposes_only_its_uncovered_files(tmp_path):
    root = declare(sources.furnished(tmp_path / "c"), "notes/*.md")
    proposed = globs(survey(root).proposal)
    assert "notes/about/**" in proposed
    assert "notes/**" not in proposed and "notes/two.md" not in proposed
    assert propose(root, ["src/*.md"], ["src/Whole.md"]).covered == 1


def test_control_a_declared_glob_covering_nothing_changes_no_proposal(tmp_path):
    root = declare(sources.furnished(tmp_path / "c"), "nothing/here/**")
    # ⭐ The manifest itself is never judged: validate's walk does not classify it.
    assert globs(survey(root).proposal) == sources.FURNISHED_GLOBS
    assert propose(root, ["src/*.md"], ["src/Whole.md"]).covered == 0


def test_a_manifest_carrying_a_home_path_is_refused_as_itself(tmp_path):
    # ⛔ R7: the declared globs are paths, so the manifest is gated before one is read.
    # ⚠️ A placeholder, split so the literal never sits in this file whole.
    root = declare(sources.furnished(tmp_path / "c"), "/" + "home/jane/x")
    with pytest.raises(PersonalDataLeak):
        propose(root, ["src/*.md"], [])


# --------------------------------------------------------------------------
# ⛔ A proposal that stands down says so by name
# --------------------------------------------------------------------------


def stood_down(root):
    return [q for q in survey(root).uncertainties if "stood down" in q.question]


def test_a_root_git_does_not_answer_for_says_so_even_when_it_proposes_nothing(tmp_path):
    root = sources.flat_prose(tmp_path / "c")
    (root / "README.md").unlink()
    [question] = stood_down(root)
    assert "git's ignore rules were not read" in question.why
    # ⭐ The report a person reads, which is what onboarding's step prints.
    assert any("stood down" in line for line in survey(root).lines())


def test_a_root_inside_another_repositorys_IGNORED_directory_says_it_judged_no_file(tmp_path):
    outer = init_repository(tmp_path / "outer")
    (outer / ".gitignore").write_text("copy/\n", encoding="utf-8")
    root = sources.furnished(outer / "copy")
    found = propose(root, ["src/*.md"], [])
    assert (found.judged, found.consulted, found.entries) == (0, True, ())
    [question] = stood_down(root)
    assert "it judged no file" in question.why


def test_control_a_root_that_is_its_own_git_working_tree_does_not_stand_down(tmp_path):
    root = sources.flat_prose(tmp_path / "c")
    (root / "README.md").unlink()
    init_repository(root)
    assert propose(root, ["*.md"], []).stands_down is None
    assert stood_down(root) == []
