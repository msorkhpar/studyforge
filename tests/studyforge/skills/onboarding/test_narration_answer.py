"""The onboarding skill's half of optional narration: the author is ASKED, and the answer is data.

⭐ **Narration is optional**, so onboarding asks whether the author wants it.
Spread over the modules it touches — `manifest` (the version that reads the key
back), `onboard` (the report says the answer, or that nobody asked), `recorded`
(the sentence) and `standing` (off is not *narrated: 0*) — and read here
through each one's public call.
"""

from __future__ import annotations

import json

import pytest

from studyforge.corpus.manifest import ManifestError, parse
from studyforge.skills.onboarding import artifacts, hand_edited, onboard, reonboard
from studyforge.skills.onboarding.manifest import NARRATION_API, promote, render
from studyforge.skills.onboarding.recorded import narration
from studyforge.skills.onboarding.standing import lines, standing_of
from tests.studyforge.generate.corpora import a_corpus
from tests.studyforge.generate.test_narration import narrate
from tests.studyforge.skills.onboarding import corpora


@pytest.mark.parametrize("answer", [True, False])
def test_the_answer_lands_in_corpus_json_at_the_version_that_reads_it(answer):
    document = promote({**corpora.DRAFT, "narration": answer})

    assert document["narration"] is answer
    assert document["corpus_api"] == NARRATION_API
    assert parse(render(document)).narration is answer


def test_the_key_is_unreadable_one_version_below_the_one_promote_writes():
    # ⛔ The behavioural pin for `NARRATION_API`, as for `NOT_MATERIAL_API`.
    document = promote({**corpora.DRAFT, "narration": False})
    with pytest.raises(ManifestError, match="narration"):
        parse(render({**document, "corpus_api": NARRATION_API - 1}))


def test_a_draft_nobody_asked_keeps_its_version_and_invents_no_answer():
    document = promote(corpora.DRAFT)
    assert "narration" not in document
    assert document["corpus_api"] < NARRATION_API


@pytest.mark.parametrize(
    ("draft", "said"),
    [({}, "not asked"), ({"narration": True}, "yes"), ({"narration": False}, "no")],
)
def test_the_onboarding_report_says_the_answer_or_that_nobody_asked(tmp_path, draft, said):
    made = onboard({**corpora.DRAFT, **draft}, framework_commit=corpora.COMMIT)
    (line,) = [line for line in made.lines() if line.strip().startswith("narration ")]
    assert line.split(None, 1)[1].startswith(said)


def test_off_is_said_as_complete_and_never_as_short():
    said = narration('{"narration": false}', False)
    assert "complete" in said
    assert not any(word in said for word in ("missing", "unfinished", "short", "0 of"))


def test_the_answer_is_settled_on_a_corpus_already_onboarded(tmp_path):
    root = corpora.material(tmp_path / "corpus")
    onboard(corpora.DRAFT, framework_commit=corpora.COMMIT, root=root).write(root)

    # ⭐ The version the answer needs moves with it; the person names only the answer.
    reonboard(root, settle={"narration": False}).write(root, regenerate=True)

    written = json.loads((root / artifacts.MANIFEST).read_text(encoding="utf-8"))
    assert written["narration"] is False
    assert written["corpus_api"] == NARRATION_API
    assert hand_edited(root) == []


def test_standing_says_off_rather_than_counting_nothing_narrated(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    narrate(root)
    manifest = root / "corpus.json"
    document = json.loads(manifest.read_text(encoding="utf-8"))
    manifest.write_text(json.dumps({**document, "corpus_api": 5, "narration": False}), "utf-8")

    said = lines(standing_of(root))

    assert any(line.startswith("- narrated: off") for line in said), said
    assert not any("0 of" in line for line in said if "narrated" in line)
