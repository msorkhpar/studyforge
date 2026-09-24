"""Mirror of `src/studyforge/skills/execution/written.py` (R12): its outputs, guarded.

⚠️ A wrong tag hand-written into `editor.env` must not leave `hand_edited` at
`[]` and the corpus's suite GREEN. ⭐ Held here on a REAL onboarded corpus that a
REAL execution run wrote into: every file the execution skill writes is reported
by onboarding's own `hand_edited` when its bytes move or it is gone, in a
sentence (R6); and running the skill again over an unchanged corpus rewrites no
byte (R10).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from studyforge.corpus.manifest import parse
from studyforge.skills.execution import onboard as execution
from studyforge.skills.execution import record, written
from studyforge.skills.onboarding import hand_edited
from tests.studyforge.skills.execution.contracts import editor_text
from tests.studyforge.skills.execution.test_record import EDITOR_TAG, TAG, Asked
from tests.studyforge.skills.onboarding.test_committed_output import onboarded

#: Every file the execution skill writes for a corpus that declares a runtime
#: nothing seeds, which is what the onboarded corpus below declares.
OUTPUTS = (
    execution.COMPOSE_FILE,
    execution.TOOLCHAIN_FILE,
    execution.READER_DOC,
    execution.RUNNER_ENV,
    execution.EDITOR_ENV,
    execution.INSTANCE_ENV,
)


def run_the_skill(root: Path, *, editor_tag: str = EDITOR_TAG) -> None:
    """Generate, write and record both tags over the onboarded corpus, as the procedure does."""
    document = json.loads((root / "corpus.json").read_text(encoding="utf-8"))
    document.update(runtimes=["python"], exercises=True)
    document["corpus_api"] = max(document["corpus_api"], 4)
    made = execution.generate(parse(json.dumps(document)), editor_text=editor_text(), root=root)
    execution.write(made, root)
    record.record_runner(made, root, root, ask=Asked(0, TAG))
    record.record_editor(made, root, root, ask=Asked(0, editor_tag))


def snapshot(root: Path) -> dict[str, bytes]:
    """Every file in the corpus but git's own, by path."""
    return {
        one.relative_to(root).as_posix(): one.read_bytes()
        for one in sorted(root.rglob("*"))
        if one.is_file() and ".git" not in one.relative_to(root).parts
    }


@pytest.fixture
def root(tmp_path) -> Path:
    corpus = onboarded(tmp_path)
    run_the_skill(corpus)
    return corpus


def test_a_corpus_both_skills_wrote_reads_nothing_edited(root):
    assert hand_edited(root) == []
    listed = [entry["where"] for entry in written.entries(root)]
    assert listed == sorted(OUTPUTS), "the record lists every file the skill wrote, and itself not"


def test_a_wrong_tag_planted_in_the_editors_file_is_reported(root):
    # ⚠️ Without the execution skill's own record, `hand_edited` would read `[]` here.
    target = root / execution.EDITOR_ENV
    planted = "EDITOR_IMAGE=example/editor:java-maven-amd64-000000000000\n"
    target.write_text(target.read_text(encoding="utf-8").rsplit("EDITOR_IMAGE=", 1)[0] + planted)
    [sentence] = hand_edited(root)
    assert sentence.startswith(f"{execution.EDITOR_ENV} was edited by hand: ")
    assert "not a fix" in sentence
    assert "re-run the execution skill's write and record steps" in sentence
    assert str(root) not in sentence, "a report is pasted: no absolute path in it (R7)"


@pytest.mark.parametrize("where", OUTPUTS)
def test_a_hand_edit_to_any_execution_output_is_reported_in_a_sentence(root, where):
    with (root / where).open("a", encoding="utf-8") as appended:
        appended.write("# mine\n")
    assert hand_edited(root) == [
        f"{where} was edited by hand: {written.RECORD} holds the digest the execution skill "
        f"wrote there, and the bytes there now are not it. {written.REMEDY}"
    ]


@pytest.mark.parametrize("where", OUTPUTS)
def test_an_execution_output_that_is_gone_is_reported_in_a_sentence(root, where):
    (root / where).unlink()
    [sentence] = hand_edited(root)
    assert sentence.startswith(f"{where} is missing: {written.RECORD} records that")


def test_a_regenerate_over_an_unchanged_corpus_rewrites_no_byte(root):
    before = snapshot(root)
    assert written.RECORD in before
    run_the_skill(root)
    assert snapshot(root) == before
    assert hand_edited(root) == []


def test_a_regenerate_writes_back_what_it_writes_and_still_reports_what_it_did_not(root):
    # ⭐ `write` rewrites its own files and re-stamps them; the two environment
    # files are the record step's, so a write alone leaves a hand-edit to one
    # of them standing, and named, until that step is run again.
    for where in (execution.COMPOSE_FILE, execution.EDITOR_ENV):
        with (root / where).open("a", encoding="utf-8") as appended:
            appended.write("# mine\n")
    document = json.loads((root / "corpus.json").read_text(encoding="utf-8"))
    document.update(runtimes=["python"], exercises=True)
    document["corpus_api"] = max(document["corpus_api"], 4)
    made = execution.generate(parse(json.dumps(document)), editor_text=editor_text(), root=root)
    execution.write(made, root)
    assert [one.split(" ", 1)[0] for one in hand_edited(root)] == [execution.EDITOR_ENV]
    run_the_skill(root)
    assert hand_edited(root) == []


def test_a_re_recorded_tag_is_the_new_record_and_not_a_hand_edit(root):
    run_the_skill(root, editor_tag="example/editor:python-amd64-ffffffffffff")
    assert hand_edited(root) == []


def test_the_record_is_the_skills_own_output_and_needs_no_manifest_change():
    assert written.RECORD.startswith(f"{execution.DIRECTORY}/")
    assert execution.classified(written.RECORD)


def test_a_record_that_cannot_be_read_is_refused_rather_than_read_as_nothing_edited(root):
    (root / written.RECORD).write_text("{not json", encoding="utf-8")
    with pytest.raises(written.WrittenRefused, match="not readable JSON"):
        hand_edited(root)


@pytest.mark.parametrize("declared", [True, 1.0, 2], ids=repr)
def test_a_record_version_this_build_does_not_read_is_refused(root, declared):
    # ⛔ `True == 1` and `1.0 == 1`, so only `version.check` refuses them.
    path = root / written.RECORD
    document = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps({**document, "written_api": declared}), encoding="utf-8")
    with pytest.raises(written.WrittenRefused, match="written_api"):
        hand_edited(root)


def test_a_recorded_path_outside_the_corpus_is_never_read(root):
    document = json.loads((root / written.RECORD).read_text(encoding="utf-8"))
    document["files"].append({"where": "../elsewhere", "sha256": "0" * 64})
    (root / written.RECORD).write_text(json.dumps(document), encoding="utf-8")
    assert hand_edited(root) == []
