"""Mirror of `src/studyforge/cli/plan/derive.py`'s narration half: a silenced corpus plans no copy.

⭐ A build of a corpus whose `corpus.json` says `narration: false` copies no clip
(`generate.narration.narrated`), so the plan — the build's own enumeration —
names none either, and reads no record.
"""

from __future__ import annotations

import json

from studyforge.cli.plan import plan_for
from studyforge.narrate.synth import state_file
from tests.studyforge.generate.test_clips import narrated


def clip_copies(plan) -> list[str]:
    return [c.path for c in plan.creations if c.narration and not c.path.endswith("/")]


def test_a_silenced_corpus_plans_no_clip_copy_and_reads_no_record(tmp_path):
    root, _ = narrated(tmp_path, "depth1")
    voiced = plan_for(root)
    assert clip_copies(voiced), "the control: a narrated corpus plans its copies"

    manifest = root / "corpus.json"
    document = json.loads(manifest.read_text(encoding="utf-8"))
    manifest.write_text(json.dumps({**document, "corpus_api": 5, "narration": False}), "utf-8")
    silent = plan_for(root)

    assert clip_copies(silent) == []
    record = state_file(root).relative_to(root).as_posix()
    assert record in voiced.read_files and record not in silent.read_files
