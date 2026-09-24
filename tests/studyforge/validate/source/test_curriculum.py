"""Mirror of `src/studyforge/validate/source/curriculum.py` (R12).

⭐ `validate` holds a declared curriculum to the tree whoever wrote the adapter:
a disagreement is a finding under its own rule id, a tree that agrees yields none,
and a file the repository ignores is no more material here than anywhere else.
"""

from __future__ import annotations

import json

from studyforge.corpus.manifest import MANIFEST_FILENAME
from studyforge.validate import validate
from studyforge.validate.corpus import read
from studyforge.validate.source import RULE_CURRICULUM, check_curriculum
from tests.studyforge.skills.adapter.test_curriculum import corpus, manifest
from tests.support import init_repository


def findings(root):
    return list(check_curriculum(read(root)))


def test_a_tree_that_agrees_with_the_declaration_yields_nothing(tmp_path):
    assert findings(corpus(tmp_path)) == []


def test_a_file_the_record_forgot_is_a_finding_under_its_own_rule(tmp_path):
    root = corpus(tmp_path, extra=["lessons/deep_3.md"])

    found = findings(root)

    assert [(each.rule, each.where) for each in found] == [(RULE_CURRICULUM, MANIFEST_FILENAME)]
    assert "lessons/deep_3.md is named for deeper and not filed there" in found[0].message


def test_validate_itself_reports_it_whoever_wrote_the_adapter(tmp_path):
    # ⭐ No adapter here at all: the declaration is refused by `validate` alone.
    root = corpus(tmp_path, extra=["lessons/deep_3.md"])
    assert RULE_CURRICULUM in {finding.rule for finding in validate(root).findings}


def test_a_file_the_repository_ignores_is_not_material_to_the_check(tmp_path):
    root = init_repository(corpus(tmp_path, extra=["lessons/deep_3.md"]))
    (root / ".gitignore").write_text("lessons/deep_3.md\n", encoding="utf-8")
    assert findings(root) == []


def test_a_corpus_that_declares_no_groups_is_not_checked(tmp_path):
    document = manifest()
    document["curriculum"] = {"record": "SUMMARY.md"}
    root = corpus(tmp_path, extra=["lessons/deep_3.md"], document=document)
    assert findings(root) == []
    del document["curriculum"]
    (root / MANIFEST_FILENAME).write_text(json.dumps({**document, "corpus_api": 6}), "utf-8")
    assert findings(root) == []
