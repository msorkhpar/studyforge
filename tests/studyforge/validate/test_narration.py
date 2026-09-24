"""Mirror of `src/studyforge/validate/narration.py` (R12) — a stale clip is a RED `validate`.

⛔ **Every corpus here is narrated by the SHIPPED stage against the recording fake
service** (`tests/studyforge/cli/narrate/plant.narrated`), so the record, the clip
names and the audio directories are the ones a real run writes. ⭐ The paragraph
is then edited the way an author edits a lesson — its words and its digest — so
the ONLY thing wrong with the corpus is that one clip says the old words.

⭐ **The expected population is read off the join directly** (`speakable_of` +
`read_state` + `playable_of_units`, in `stale_by_join`), never off the check's
own report, so a check that skipped a unit cannot make the expectation skip it.
"""

from __future__ import annotations

import io
from pathlib import Path

from studyforge.generate.declarations import read_corpus, unit_location
from studyforge.narrate.playable import playable_of_units
from studyforge.narrate.speakable import speakable_of
from studyforge.narrate.synth import audio_dir, read_state, state_file
from studyforge.unit.builder import build_unit
from studyforge.validate import validate
from studyforge.validate.cli import main
from studyforge.validate.narration import (
    NO_VOICE,
    RULE_NARRATION_RECORD,
    RULE_NARRATION_STALE,
)
from studyforge.validate.report import INVALID, OK
from studyforge.validate.run import CHECKS
from tests.studyforge.cli.narrate.plant import (
    LESSON,
    WORDS,
    edit_one_paragraph,
    narrated,
    record_of,
    write_record,
)
from tests.studyforge.cli.narrate.service import VOICE
from tests.studyforge.generate.corpora import a_corpus

#: The narration rules this module owns. ⭐ Asserted as a set so another check's
#: `Unchecked` lines (the fixture carries no source tree) are not this module's.
OURS = {RULE_NARRATION_STALE, RULE_NARRATION_RECORD}

#: ⛔ A hostname SHAPE the R7 gate refuses, assembled so no literal sits in the tree.
LEAKY_VOICE = "voicebox" + ".local"


def stale_by_join(root: Path) -> list[str]:
    """⛔ THE INDEPENDENT READING: every speech id the join marks stale, walked here."""
    corpus, state = read_corpus(root), read_state(state_file(root))
    stale: list[str] = []
    for source in corpus.units:
        document = build_unit(source.directory, declared_practices=source.declared_practices)
        units = speakable_of(document).units
        probed = audio_dir(root, unit_location(corpus, source))
        stale += [entry.speech_id for entry in playable_of_units(units, state, audio=probed).stale]
    return sorted(stale)


def ours(report):
    return [finding for finding in report.findings if finding.rule in OURS]


def test_the_check_is_in_the_one_list():
    from studyforge.validate.narration import check_narration_current

    assert check_narration_current in CHECKS


def test_a_corpus_with_no_record_is_quiet(tmp_path):
    # ⭐ C5: the reading floor is complete without narration.
    root = a_corpus(tmp_path, "depth1")
    assert not state_file(root).exists()
    report = validate(root)
    assert ours(report) == [] and report.ok, report.lines()
    assert not any(item.rule == RULE_NARRATION_STALE for item in report.unchecked)


def test_a_freshly_narrated_corpus_is_green(tmp_path):
    root = narrated(tmp_path)
    assert record_of(root)["clips"], "nothing was narrated; the reading would be vacuous"
    report = validate(root)
    assert report.ok, report.lines()
    assert stale_by_join(root) == []


def test_an_edited_paragraph_is_red_and_named(tmp_path):
    root = narrated(tmp_path)
    speech_id = edit_one_paragraph(root)
    report = validate(root)
    assert report.exit_code == INVALID
    assert report.rules == (RULE_NARRATION_STALE,), report.lines()
    (finding,) = report.findings
    assert finding.where == "archive/depth-one/raw/prose/unit-01"
    assert f"'{speech_id}'" in finding.message
    assert f"studyforge narrate <corpus-root> --voice {VOICE}" in finding.message


def test_the_finding_count_is_the_joins_count(tmp_path):
    root = narrated(tmp_path)
    edited = edit_one_paragraph(root)
    named = sorted(finding.message.split("'")[1] for finding in ours(validate(root)))
    assert named == stale_by_join(root) == [edited]


def test_the_finding_never_reproduces_the_text(tmp_path):
    # ⛔ R7: neither the words the clip says nor the words the page says.
    root = narrated(tmp_path)
    edit_one_paragraph(root)
    lines = "\n".join(validate(root).lines())
    assert WORDS[0] not in lines and WORDS[1] not in lines
    assert "subject, a predicate" not in lines


def test_narration_off_for_the_run_judges_no_clip(tmp_path):
    # ⭐ W460's seam: `narrate.enabled.narration_on` is asked, and off is quiet.
    root = narrated(tmp_path)
    edit_one_paragraph(root)
    assert ours(validate(root, narration=False)) == []
    assert ours(validate(root, narration=True)) != []


def test_the_command_line_turns_narration_off(tmp_path):
    root = narrated(tmp_path)
    edit_one_paragraph(root)
    out = io.StringIO()
    assert main([str(root), "--no-narration"], out=out) == OK, out.getvalue()
    out = io.StringIO()
    assert main([str(root)], out=out) == INVALID
    assert f"[{RULE_NARRATION_STALE}]" in out.getvalue()


def test_a_record_the_build_would_refuse_is_a_finding(tmp_path):
    root = narrated(tmp_path)
    state_file(root).write_text("{ not json", encoding="utf-8")
    report = validate(root)
    assert report.rules == (RULE_NARRATION_RECORD,), report.lines()
    assert report.findings[0].where == ".studyforge/narration.json"


def test_a_record_with_no_voice_says_what_to_name(tmp_path):
    root = narrated(tmp_path)
    document = record_of(root)
    document["conditions"]["voice"] = ""
    write_record(root, document)
    edit_one_paragraph(root)
    (finding,) = validate(root).findings
    assert f"--voice {NO_VOICE}" in finding.message


def test_a_voice_carrying_personal_data_is_not_printed(tmp_path):
    # ⛔ The hostname shape `archive.scrub` refuses; a placeholder, not an identity.
    root = narrated(tmp_path)
    document = record_of(root)
    document["conditions"]["voice"] = LEAKY_VOICE
    write_record(root, document)
    edit_one_paragraph(root)
    report = validate(root)
    assert "personal-data" in report.rules
    assert LEAKY_VOICE not in "\n".join(report.lines())
    assert any(f"--voice {NO_VOICE}" in finding.message for finding in report.findings)


def test_a_unit_that_will_not_build_is_unchecked_not_clean(tmp_path):
    root = narrated(tmp_path)
    (root / LESSON).write_text("[]", encoding="utf-8")
    report = validate(root)
    assert any(item.rule == RULE_NARRATION_STALE for item in report.unchecked), report.lines()
