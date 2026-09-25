"""Mirror of `src/studyforge/validate/links.py` (R12): a link that leads nowhere names its unit.

⛔ **Every expectation is a literal**, written before the run. The corpus is built
in `tmp_path` by `tests/studyforge/validate/corpora.py` (`linked`), on both
placement profiles, because where a page sits is what a link is read from.
"""

from __future__ import annotations

import pytest

from studyforge.validate import validate
from studyforge.validate.corpus import read
from studyforge.validate.links import RULE_LINK_UNRESOLVED, check_links_resolve, links
from tests.studyforge.validate.corpora import LINKED
from tests.studyforge.validate.corpora import linked as corpus


@pytest.mark.parametrize("placement", ["tree", "sibling"])
def test_a_link_that_leads_nowhere_names_its_unit_and_its_words(tmp_path, placement):
    found = [item for item in check_links_resolve(read(corpus(tmp_path, placement)))]
    assert [(item.rule, item.where) for item in found] == [
        (RULE_LINK_UNRESOLVED, "archive/demo/raw/prose/unit-01")
    ] * 4
    assert [item.message.split(";")[0] for item in found] == [
        "unit demo/unit-01 (Unit 1) links 'gone' to a file that is not in the corpus",
        "unit demo/unit-01 (Unit 1) links 'out' to a path that leads outside the corpus",
        "unit demo/unit-01 (Unit 1) links 'rooted' to a rooted path, which leads outside "
        "the corpus",
        "unit demo/unit-01 (Unit 1) links 'nowhere' to an anchor that names no heading of "
        "this unit",
    ]
    # ⛔ R7: a finding names the link's words and never its href.
    assert not any("Gone.java" in item.message or "hosts" in item.message for item in found)


@pytest.mark.parametrize("placement", ["tree", "sibling"])
def test_a_corpus_whose_links_all_lead_somewhere_has_no_finding(tmp_path, placement):
    text = LINKED.split(" [gone]")[0]
    root = corpus(tmp_path, placement, text)
    assert list(check_links_resolve(read(root))) == []
    assert RULE_LINK_UNRESOLVED not in validate(root).rules


def test_validate_runs_the_check(tmp_path):
    found = validate(corpus(tmp_path)).findings
    assert [item.rule for item in found].count(RULE_LINK_UNRESOLVED) == 4


def test_a_corpus_a_build_cannot_read_is_unchecked_and_never_passed(tmp_path):
    root = corpus(tmp_path)
    (root / "corpus.json").write_text("{", encoding="utf-8")
    walk = read(root)
    walk.root = root
    (item,) = list(check_links_resolve(walk))
    assert (item.rule, item.where) == (RULE_LINK_UNRESOLVED, ".")
    assert "no link was followed" in item.why


def test_every_prose_field_at_any_depth_is_read_and_code_is_not():
    blocks = [
        {"type": "heading", "level": 2, "text": "[h](a)"},
        {"type": "para", "text": "[p](b) `[c](code)`"},
        {"type": "code", "lang": "md", "text": "[c](code)"},
        {
            "type": "list",
            "ordered": False,
            "items": ["[i](c)", ["[j](d)", {"type": "para", "text": "[k](e)"}]],
        },
        {"type": "table", "headers": ["[t](f)"], "rows": [["[r](g)"]]},
        {"type": "quote", "blocks": [{"type": "para", "text": "[q](h)"}]},
        {"type": "disclosure", "summary": "[s](i)", "open": False, "blocks": []},
    ]
    assert [href for _, href in links([{"blocks": blocks}])] == list("abcdefghi")
