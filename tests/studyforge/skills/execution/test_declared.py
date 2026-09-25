"""Mirror of `src/studyforge/skills/execution/declared.py` (R12).

⭐ A first write leaves `validate` as clean as it found it.

⭐ Read end to end on an onboarded corpus: onboarding declares a runtime (as
`reonboard` does), the execution skill writes once, and `validate` is asked —
the same question a corpus's own gate asks. ⛔ The control is the same corpus
with the runtime declared only in memory, which the skill refuses.
"""

from __future__ import annotations

import json

import pytest

from studyforge.corpus.manifest import parse
from studyforge.corpus.placement import PRACTICE_DIRNAME
from studyforge.skills import execution
from studyforge.skills.execution import declared
from studyforge.validate import validate
from tests.studyforge.skills.execution.contracts import editor_text, made_runnable
from tests.studyforge.skills.onboarding.test_committed_output import onboarded


def findings(root) -> set[tuple[str, str]]:
    return {(finding.rule, finding.where) for finding in validate(root).findings}


def test_a_runnable_corpus_s_first_write_adds_nothing_to_validate_and_makes_every_bind(tmp_path):
    # ⚠️ The fixture carries findings of its own, unrelated to this skill, so
    # the claim is read as a difference: the write adds none.
    root = onboarded(tmp_path)
    assert not (root / PRACTICE_DIRNAME).exists(), "a corpus with no practices: vacuous otherwise"
    manifest = made_runnable(root)
    before = findings(root)
    made = execution.generate(manifest, editor_text=editor_text(), root=root)
    execution.write(made, root)
    assert (root / execution.READER_DOC).is_file()
    assert findings(root) == before
    assert PRACTICE_DIRNAME in made.bound
    for directory in made.bound:
        assert (root / directory).is_dir(), f"compose would make {directory} root-owned"


def test_onboarding_declares_the_skill_s_files_only_for_a_corpus_that_declares_runtimes(tmp_path):
    root = onboarded(tmp_path)
    before = parse((root / "corpus.json").read_text(encoding="utf-8")).content
    assert before.why_not_material(execution.READER_DOC) is None
    after = made_runnable(root).content
    assert after.why_not_material(execution.READER_DOC) == execution.onboard.WHY_READER


def test_a_manifest_that_does_not_declare_the_skill_s_files_is_refused_and_nothing_written(
    tmp_path,
):
    root = onboarded(tmp_path)
    document = json.loads((root / "corpus.json").read_text(encoding="utf-8"))
    document.update(runtimes=["python"], exercises=True)
    document["corpus_api"] = max(document["corpus_api"], 4)
    made = execution.generate(parse(json.dumps(document)), editor_text=editor_text(), root=root)
    with pytest.raises(execution.ExecutionRefused, match=r"EXECUTION\.md .*Re-run onboarding"):
        execution.write(made, root)
    assert not (root / execution.READER_DOC).exists()
    assert not (root / execution.COMPOSE_FILE).exists()
    assert not (root / PRACTICE_DIRNAME).exists()


def test_a_corpus_with_no_manifest_on_disk_is_not_refused_and_one_with_is_asked(tmp_path):
    assert declared.undeclared(tmp_path, ["EXECUTION.md"]) == ()
    root = onboarded(tmp_path / "onboarded")
    assert declared.undeclared(root, [execution.COMPOSE_FILE, "EXECUTION.md"]) == ("EXECUTION.md",)


def test_the_control_validate_does_see_an_undeclared_reader_document(tmp_path):
    # ⛔ Without this, the difference above could be empty because `validate`
    # never looks at the root document at all.
    root = onboarded(tmp_path)
    (root / execution.READER_DOC).write_text("# Execution\n", encoding="utf-8")
    assert ("unclassified", execution.READER_DOC) in findings(root)
