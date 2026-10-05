"""Question pools with a per-domain draw and multiple-response items, read in a real browser.

**What it asserts.** A sitting that names a count `per_domain` draws exactly that many questions of
each domain, whole scenarios kept together; two attempts draw different forms and a reload of one
attempt keeps its form; a multiple-response question cannot be submitted with the wrong number of
options chosen, and is right only with exactly its keyed pair, in a mock and in a plain quiz drawn
one question at a time.

⛔ WHY THIS NEEDS A BROWSER. The draw, the stored attempt and the submit refusal exist only while a
page is running.
"""

from __future__ import annotations

import copy
import json
import time
from pathlib import Path

import pytest

from tests.studyforge.exercise.quiz import mock_exam, mock_form
from tests.studyforge.exercise.quiz.mock_corpus import ORIGIN, form_corpus, mock_corpus
from tests.studyforge.serve.routes.quizzing import page_of
from tests.visual.mock_form_state import STATE
from tests.visual.page import OpenPage

POOL = mock_form.questions(ORIGIN)
DOMAIN = {one["id"]: one["domain"] for one in POOL}
SCENARIO = {one["id"]: one.get("scenario") for one in POOL}
KEYED = mock_form.keyed(POOL)
EXAM = 'section[data-mock-form]'


def part(name: str) -> str:
    return f'[data-form-part="{name}"]'


def click(page: OpenPage, selector: str) -> None:
    page.evaluate(f"document.querySelector({selector!r}).click()")
    time.sleep(0.05)


def state(page: OpenPage) -> dict:
    return page.evaluate(STATE)


def begin(page: OpenPage) -> dict:
    click(page, part("begin"))
    return state(page)


def reopen(page: OpenPage) -> None:
    page.open(page.evaluate("location.href.split('#')[0]"))
    page.open_practice()


@pytest.fixture(scope="module")
def pooled(tmp_path_factory: pytest.TempPathFactory) -> str:
    sittings = [{"id": "quick", "title": "Quick form", "per_domain": {"AS1": 4, "AS2": 3}}]
    original = mock_form.mock
    mock_form.mock = lambda: {**original(), "sittings": sittings}
    try:
        root = form_corpus(tmp_path_factory.mktemp("pool-draw"))
    finally:
        mock_form.mock = original
    return "file://" + str(page_of(root))


def plain_pair(tmp: Path) -> str:
    asked = [{k: v for k, v in one.items() if k != "domain"} for one in mock_exam.questions(ORIGIN)]
    first = copy.deepcopy(asked[0])
    keyed = [option["id"] for option in first["options"]][:2]
    for option in first["options"]:
        option["correct"] = option["id"] in keyed
    first["select"] = 2
    root = mock_corpus(tmp, mock=False, questions=[first, asked[1]])
    return "file://" + str(page_of(root)), first["id"], keyed


@pytest.fixture(scope="module")
def plain(tmp_path_factory: pytest.TempPathFactory):
    return plain_pair(tmp_path_factory.mktemp("plain-pair"))


def fresh(page: OpenPage, url: str) -> OpenPage:
    page.open(url)
    page.evaluate("localStorage.clear()")
    page.open(url)
    page.open_practice()
    return page


def test_a_sitting_draws_exactly_its_count_per_domain(open_page: OpenPage, pooled: str):
    page = fresh(open_page, pooled)
    assert state(page)["sittings"][0].startswith("Quick form: 7 questions"), state(page)["sittings"]
    for _ in range(8):
        drawn = begin(page)["drawn"]
        domains = [DOMAIN[one] for one in drawn]
        assert domains.count("AS1") == 4 and domains.count("AS2") == 3, drawn
        for scenario in {SCENARIO[one] for one in drawn if SCENARIO[one]}:
            mine = [q for q, s in SCENARIO.items() if s == scenario]
            assert all(one in drawn for one in mine), "a scenario was split"
        click(page, part("again"))


def test_two_attempts_draw_different_forms_and_a_reload_keeps_one(open_page: OpenPage, pooled: str, capture_dir: Path):
    page = fresh(open_page, pooled)
    forms = []
    for _ in range(6):
        forms.append(tuple(begin(page)["drawn"]))
        reopen(page)
        assert tuple(state(page)["drawn"]) == forms[-1], "a reload changed the attempt's form"
        click(page, part("again"))
    assert len(set(forms)) >= 2, "six attempts all drew one form"
    page.capture(capture_dir / "pool-attempt.png")


def pick(page: OpenPage, question: str, option: str) -> None:
    click(page, f'[data-practice-question="{question}"] input[value="{option}"]')


def test_a_multiple_response_item_in_a_mock_cannot_be_submitted_short(open_page: OpenPage, pooled: str):
    page = fresh(open_page, pooled)
    for _ in range(40):
        drawn = begin(page)["drawn"]
        if "p9" in drawn:
            break
        click(page, part("again"))
    else:
        pytest.fail("p9 was never drawn")
    for question in drawn:
        if question != "p9":
            keyed = KEYED[question]
            for option in keyed if isinstance(keyed, list) else [keyed]:
                pick(page, question, option)
    pick(page, "p9", KEYED["p9"][0])
    click(page, part("submit"))
    read = state(page)
    assert not read["result"] and "p9" not in read["missing"] and read["missing"].startswith("Choose exactly")
    click(page, part("submit"))
    assert not state(page)["result"], "a second submit got past a short item"
    pick(page, "p9", KEYED["p9"][1])
    click(page, part("submit"))
    read = state(page)
    assert read["result"] and read["verdicts"]["p9"] == "correct"
    assert "7 of 7 (100%)" in read["overall"]


def read_quiz(page: OpenPage, question: str) -> dict:
    return page.evaluate(
        "(() => { const q = document.querySelector('[data-practice-question=\"%s\"]');"
        " const r = q.querySelector('[data-form-part=\"review\"]');"
        " return {verdict: q.getAttribute('data-practice-verdict'),"
        "  hint: (q.querySelector('[data-form-part=\"choose\"]')||{}).textContent,"
        "  review: r ? r.textContent : ''}; })()" % question
    )


@pytest.mark.parametrize("chosen,right", [(["a"], None), (["a", "c"], False), (["b", "c"], False), (["a", "b"], True), (["b", "a"], True)])
def test_a_select_two_item_in_a_plain_quiz_is_right_only_with_the_exact_pair(open_page: OpenPage, plain, chosen, right, capture_dir: Path):
    url, question, keyed = plain
    assert keyed == ["a", "b"]
    page = fresh(open_page, url)
    for option in chosen:
        click(page, f'section[data-form-kind="quiz"] [data-practice-question="{question}"] input[value="{option}"]')
    read = page.evaluate(
        f"(() => {{ const q = document.querySelector('[data-practice-question=\"{question}\"]');"
        " return {verdict: q.getAttribute('data-practice-verdict'),"
        " kinds: Array.from(q.querySelectorAll('input')).map((i) => i.type),"
        " hint: q.querySelector('[data-form-part=\"choose\"]').textContent}; })()"
    )
    assert set(read["kinds"]) == {"checkbox"} and read["hint"] == "Choose 2."
    expected = None if right is None else ("correct" if right else "wrong")
    assert read["verdict"] == expected, (chosen, read)
    if chosen == ["a", "b"]:
        page.capture(capture_dir / "select-two-right.png")
    if chosen == ["a", "c"]:
        page.capture(capture_dir / "select-two-wrong.png")
