"""Mirror of `src/studyforge/skills/reconnaissance/curriculum.py` (R12).

⭐ **Detection and declaration are one act.** What the survey detects — the
record, its groups, the prefixes that agree with them — is written into the
draft's `curriculum`, and the adapter's filing reads that declaration back into
exactly the grouping the survey detected. ⛔ A prefix that does not agree is
never drafted: it stays a cross-check.
"""

from __future__ import annotations

from studyforge.corpus.manifest import KEY_VERSIONS, parse
from studyforge.skills.adapter.curriculum import filed
from studyforge.skills.onboarding import promote, render
from studyforge.skills.reconnaissance import survey
from tests.studyforge.skills.reconnaissance import sources


def test_the_survey_writes_what_it_detected_into_the_draft(tmp_path):
    proposal = survey(sources.prefixed_groups(tmp_path / "c")).proposal

    assert proposal["curriculum"] == {
        "record": "README.md",
        "containers": [
            {"label": "Fundamentals", "address": "fundamentals", "prefix": ""},
            {"label": "Server", "address": "server", "prefix": "s"},
            {"label": "Client", "address": "client", "prefix": "c"},
        ],
    }
    assert proposal["corpus_api"] == KEY_VERSIONS[(None, "curriculum")]


def test_the_declaration_files_back_exactly_what_the_survey_detected(tmp_path):
    # ⭐ The draft is promoted as onboarding would, and the adapter's
    # filing reads it — the survey's grouping, unit for unit, from the manifest.
    root = sources.prefixed_groups(tmp_path / "c")
    found = survey(root)
    manifest = parse(render(promote(found.proposal, reasons=sources.reasons(found.proposal))))

    groups = filed(root, manifest)

    assert [(group.label, len(group.units)) for group in groups] == [
        ("Fundamentals", 4),
        ("Server", 3),
        ("Client", 3),
    ]
    assert [u.origin for u in groups[1].units] == ["src/s1.md", "src/s2.md", "src/s3.md"]


def test_every_part_of_the_declaration_is_asked_about(tmp_path):
    questions = [u.question for u in survey(sources.prefixed_groups(tmp_path / "c")).uncertainties]
    assert any("README.md the document that records this curriculum" in q for q in questions)
    assert any("addresses the groups are served at" in q for q in questions)
    assert any("3 of 3 group(s) are cross-checked by filename prefix" in q for q in questions)


def test_names_the_record_does_not_agree_with_draft_no_prefix(tmp_path):
    # ⛔ A server-named file the record never lists makes the two
    # partitions differ, so the prefix rule is not drafted as a cross-check.
    root = sources.prefixed_groups(tmp_path / "c")
    sources.write(root, {"src/s9.md": sources.unit("Unlisted")})

    containers = survey(root).proposal["curriculum"]["containers"]

    assert all("prefix" not in each for each in containers)


def test_a_record_without_groups_is_declared_as_where_the_curriculum_lives(tmp_path):
    proposal = survey(sources.flat_prose(tmp_path / "c")).proposal
    assert proposal["curriculum"] == {"record": "README.md"}


def test_a_two_level_record_declares_its_place_and_leaves_the_groups_to_its_adapter(tmp_path):
    proposal = survey(sources.nested_sections(tmp_path / "c")).proposal
    assert proposal["curriculum"] == {"record": "README.md"}


def test_labels_that_would_share_an_address_draft_no_groups_and_ask(tmp_path):
    files = {"src/a1.md": sources.unit("A"), "src/b1.md": sources.unit("B")}
    files["README.md"] = (
        "# Course\n\n# Part: One\n\n- [1. A](src/a1.md)\n\n# Part, One\n\n- [1. B](src/b1.md)\n"
    )
    found = survey(sources.write(tmp_path / "c", files))

    assert "containers" not in found.proposal["curriculum"]
    assert any("what address is each" in u.question for u in found.uncertainties)


def test_a_source_with_no_record_drafts_no_curriculum(tmp_path):
    files = {"src/a.md": sources.unit("A"), "src/b.md": sources.unit("B")}
    proposal = survey(sources.write(tmp_path / "c", files)).proposal
    assert "curriculum" not in proposal
