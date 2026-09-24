"""`validate` over a corpus whose `corpus.json` records narration off (`W460`), through `W457`'s seam.

⭐ The user's ruling, 2026-09-23: narration is optional. A corpus that recorded
*no* judges no clip, stale or not, because `validate` asks the one predicate
(`narrate.narration_on`) and the predicate reads the recorded answer. ⛔ Nothing
here calls a silenced corpus short.
"""

from __future__ import annotations

import json

from studyforge.validate import validate
from studyforge.validate.narration import RULE_NARRATION_STALE
from tests.studyforge.cli.narrate.plant import edit_one_paragraph, narrated


def recording(root, narration: bool) -> None:
    manifest = root / "corpus.json"
    document = json.loads(manifest.read_text(encoding="utf-8"))
    manifest.write_text(json.dumps({**document, "corpus_api": 5, "narration": narration}))


def stale(report) -> list:
    return [finding for finding in report.findings if finding.rule == RULE_NARRATION_STALE]


def test_a_corpus_that_recorded_no_reports_no_stale_clip(tmp_path):
    root = narrated(tmp_path)
    edit_one_paragraph(root)
    assert stale(validate(root)), "the control: the edited paragraph's clip is stale"

    recording(root, False)

    report = validate(root)
    assert stale(report) == [] and report.ok, report.lines()
    assert stale(validate(root, narration=True)), "the run's answer still wins"
