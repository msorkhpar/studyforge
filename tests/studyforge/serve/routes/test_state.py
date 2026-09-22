"""Mirror of `src/studyforge/serve/routes/state.py` (R12).

⭐ **E05 SF-19b**: *"State responses never cache"*; *"N-segment addresses route correctly
at depth 1 and depth 2"*; *"state is derived from the filesystem, never from a record of
intent — a claim that something exists with nothing on disk shows up as the
disagreement it is"*. ⭐ **E05 SF-21**: a read mark is never a pass, and a run never
completes a practice.
"""

from __future__ import annotations

import json
import shutil

import pytest

from studyforge.address import parse_unit_key
from studyforge.corpus.discovery import FRESH, STALE
from studyforge.generate.declarations import read_corpus
from studyforge.progress import Progress
from studyforge.serve.discovery import discover
from studyforge.serve.response import NO_STORE, Request
from studyforge.serve.routes.state import (
    GATED,
    MALFORMED,
    NO_PAGE,
    NO_SUCH_CORPUS,
    NO_SUCH_STATE,
    NO_SUCH_UNIT,
    NOT_DECLARED,
    UNREADABLE,
    UNSCANNABLE,
    route,
)
from tests.studyforge.generate.corpora import BOTH
from tests.studyforge.serve.built import (
    LATER,
    SECTION,
    a_workspace,
    depth_of,
    pages_of,
    practice,
    record,
    source_of,
    unit_keys,
)
from tests.studyforge.serve.serving import LEAK

CACHING_HEADERS = ("ETag", "Last-Modified", "Expires", "Age", "Vary")


def get(discovered, rest, **headers):
    return route(discovered, Request("GET", "/api/v1/state/" + rest, headers), rest)


def answer(response):
    return json.loads(response.body)


@pytest.fixture
def workspace(tmp_path):
    return a_workspace(tmp_path)


def assert_never_cached(response):
    assert response.header("Cache-Control") == NO_STORE, response.status
    for name in CACHING_HEADERS:
        assert response.header(name) is None, (response.status, name)


def test_no_state_answer_of_any_status_carries_a_validator_or_a_lifetime(workspace):
    discovered = discover(workspace)
    one = workspace / "depth1"
    name, key = source_of(one), unit_keys(one)[0]
    answers = [
        get(discovered, ""),
        get(discovered, "corpora"),
        get(discovered, name),
        get(discovered, f"{name}/units/{key}"),
        get(discovered, "nobody"),
        get(discovered, f"{name}/units/{key}/extra"),
        get(discovered, f"{name}/elsewhere"),
    ]
    Progress(one, depth_of(one)).path.parent.mkdir(parents=True)
    Progress(one, depth_of(one)).path.write_text("{\n", encoding="utf-8")
    answers.append(get(discovered, name))
    assert {response.status for response in answers} == {200, 404, 422}
    for response in answers:
        assert_never_cached(response)


def test_a_conditional_request_is_answered_whole_because_state_has_no_validator(workspace):
    discovered = discover(workspace)
    name = source_of(workspace / "depth2")
    response = get(discovered, name, **{"If-None-Match": "*", "If-Modified-Since": "x"})
    assert response.status == 200
    assert answer(response)["resource"] == "corpus-state"


@pytest.mark.parametrize("name", BOTH)
def test_every_unit_routes_at_its_corpus_depth_to_the_pages_that_identify_as_it(workspace, name):
    discovered = discover(workspace)
    root = workspace / name
    source = source_of(root)
    assert unit_keys(root)
    for key in unit_keys(root):
        assert len(key.split("/")) == depth_of(root) + 1
        response = get(discovered, f"{source}/units/{key}")
        assert response.status == 200, key
        body = answer(response)
        assert (body["corpus"], body["key"], body["declared"], body["present"]) == (
            source,
            key,
            True,
            True,
        )
        served = sorted(workspace / href[1:] for href in body["pages"])
        assert served == sorted(pages_of(root, key)) and served


@pytest.mark.parametrize("name", BOTH)
def test_a_unit_key_under_the_other_corpus_is_not_routed(workspace, name):
    discovered = discover(workspace)
    other = next(workspace / each for each in BOTH if each != name)
    for key in unit_keys(workspace / name):
        response = get(discovered, f"{source_of(other)}/units/{key}")
        assert (response.status, answer(response)["error"]) == (404, NO_SUCH_UNIT), key


def test_two_corpora_with_different_profiles_answer_from_one_instance_without_bleeding(workspace):
    discovered = discover(workspace)
    listed = answer(get(discovered, ""))["corpora"]
    assert sorted((c["profile"], c["depth"]) for c in listed) == [("sibling", 2), ("tree", 1)]
    one, two = workspace / "depth1", workspace / "depth2"
    key = unit_keys(two)[0]
    record(two, key)
    assert list(answer(get(discovered, source_of(two)))["practices"]) == [practice(two, key)]
    first = answer(get(discovered, source_of(one)))
    assert (first["practices"], first["disagreements"]) == ({}, [])
    assert first["status"]["corpus"] == source_of(one)
    for each in unit_keys(one):
        assert answer(get(discovered, f"{source_of(one)}/units/{each}"))["practices"] == {}
    unit = answer(get(discovered, f"{source_of(two)}/units/{key}"))
    assert unit["practices"][SECTION]["passed"] is True


def test_a_page_removed_after_startup_reads_absent_and_the_tree_reads_stale(workspace):
    discovered = discover(workspace)
    root = workspace / "depth2"
    name, key = source_of(root), unit_keys(root)[-1]
    before = answer(get(discovered, f"{name}/units/{key}"))
    assert before["present"] and before["discovery"]["since_startup"] == FRESH
    for page in pages_of(root, key):
        page.unlink()
    unit = answer(get(discovered, f"{name}/units/{key}"))
    corpus = answer(get(discovered, name))
    assert (unit["declared"], unit["present"], unit["pages"]) == (True, False, [])
    assert unit["discovery"]["since_startup"] == STALE
    assert corpus["missing"] == [key]
    assert [u["present"] for u in corpus["status"]["units"] if u["key"] == key] == [False]


def test_a_stale_cache_at_startup_is_reported_as_stale_and_the_answer_is_the_scans(workspace):
    discover(workspace)
    root = workspace / "depth1"
    cache = root / read_corpus(root).shared.site_cache
    document = json.loads(cache.read_text(encoding="utf-8"))
    ghost = dict(document["artifacts"][0], path="nowhere/ghost.unit.html")
    document["artifacts"].append(ghost)
    document["scan_sha256"] = "0" * 64
    cache.write_text(json.dumps(document), encoding="utf-8")
    discovered = discover(workspace)
    body = answer(get(discovered, source_of(root)))
    assert body["discovery"] == {"cache": STALE, "since_startup": FRESH}
    unit = answer(get(discovered, f"{source_of(root)}/units/{unit_keys(root)[0]}"))
    assert not any("ghost" in href for href in unit["pages"])


def test_a_recorded_pass_for_a_unit_with_no_page_is_a_disagreement_and_never_a_pass(workspace):
    discovered = discover(workspace)
    root = workspace / "depth2"
    name, key = source_of(root), unit_keys(root)[0]
    record(root, key)
    assert answer(get(discovered, f"{name}/units/{key}"))["practices"][SECTION]["passed"] is True
    for page in pages_of(root, key):
        page.unlink()
    unit = answer(get(discovered, f"{name}/units/{key}"))
    corpus = answer(get(discovered, name))
    said = [{"practice": practice(root, key), "unit": key, "claims": "a pass", "but": NO_PAGE}]
    assert (unit["practices"], unit["disagreements"]) == ({}, said)
    assert (corpus["practices"], corpus["disagreements"]) == ({}, said)


def test_a_record_for_a_unit_the_corpus_never_declared_is_a_disagreement(workspace):
    discovered = discover(workspace)
    root = workspace / "depth1"
    address, _ = parse_unit_key(unit_keys(root)[0], depth_of(root))
    ghost = address.unit_key(99)
    record(root, ghost, mode="run")
    unit = answer(get(discovered, f"{source_of(root)}/units/{ghost}"))
    assert (unit["declared"], unit["present"], unit["practices"]) == (False, False, {})
    said = {"practice": practice(root, ghost), "unit": ghost, "claims": "a run"}
    assert unit["disagreements"] == [dict(said, but=NOT_DECLARED)]
    nothing = address.unit_key(98)
    response = get(discovered, f"{source_of(root)}/units/{nothing}")
    assert (response.status, answer(response)["error"]) == (404, NO_SUCH_UNIT)


def test_a_run_never_completes_a_practice_and_the_first_pass_never_moves(workspace):
    discovered = discover(workspace)
    root = workspace / "depth2"
    name, key = source_of(root), unit_keys(root)[0]

    def reported():
        return answer(get(discovered, f"{name}/units/{key}"))["practices"][SECTION]

    record(root, key, mode="run", exit_code=0)
    assert (reported()["passed"], reported()["last"]["passed"]) == (False, False)
    record(root, key, mode="test", exit_code=1)
    assert reported()["passed"] is False
    record(root, key, mode="test", exit_code=0)
    first = reported()
    assert (first["passed"], first["last"]["passed"]) == (True, True)
    record(root, key, mode="run", exit_code=0, when=LATER)
    record(root, key, mode="test", exit_code=1, when=LATER)
    later = reported()
    assert (later["passed"], later["last"]["passed"], later["runs"]) == (True, False, 5)
    assert later["first_passed_at"] == first["first_passed_at"]


def test_a_pass_is_never_reported_as_a_read_mark_and_nothing_a_request_carries_is_read(workspace):
    discovered = discover(workspace)
    root = workspace / "depth2"
    for key in unit_keys(root):
        record(root, key)
    plain = get(discovered, source_of(root))
    carried = get(
        discovered, source_of(root), Cookie=f"read={unit_keys(root)[0]}", **{"X-Read": "all"}
    )
    assert plain.body == carried.body
    status = answer(plain)["status"]
    assert [unit["read"] for unit in status["units"]] == [False] * len(unit_keys(root))
    assert status["next"] == status["units"][0]["key"]


def malformed_json(root, key):
    return "{\n"


def a_read_mode(root, key):
    record(root, key)
    document = json.loads(Progress(root, depth_of(root)).path.read_text(encoding="utf-8"))
    document["practices"][practice(root, key)]["last"]["mode"] = "read"
    return json.dumps(document)


@pytest.mark.parametrize("written", [malformed_json, a_read_mode])
def test_a_malformed_record_answers_422_and_is_left_exactly_as_it_is(workspace, written):
    discovered = discover(workspace)
    root = workspace / "depth2"
    key = unit_keys(root)[0]
    store = Progress(root, depth_of(root))
    text = written(root, key)
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_text(text, encoding="utf-8")
    for rest in (source_of(root), f"{source_of(root)}/units/{key}"):
        response = get(discovered, rest)
        assert (response.status, answer(response)["error"]) == (422, MALFORMED)
    assert store.path.read_text(encoding="utf-8") == text


def test_an_unreadable_record_a_leaking_one_and_a_vanished_root_answer_fixed_500s(workspace):
    discovered = discover(workspace)
    one, two = workspace / "depth1", workspace / "depth2"
    Progress(one, depth_of(one)).path.mkdir(parents=True)
    unreadable = get(discovered, source_of(one))
    key = unit_keys(two)[0]
    record(two, key)
    store = Progress(two, depth_of(two)).path
    store.write_text(store.read_text(encoding="utf-8").replace("make test", LEAK), "utf-8")
    leaking = get(discovered, f"{source_of(two)}/units/{key}")
    assert (unreadable.status, answer(unreadable)["error"]) == (500, UNREADABLE)
    assert (leaking.status, answer(leaking)["error"]) == (500, GATED)
    assert LEAK.encode() not in leaking.body
    name = source_of(one)
    shutil.rmtree(one)
    vanished = get(discovered, name)
    assert (vanished.status, answer(vanished)["error"]) == (500, UNSCANNABLE)


def test_an_unknown_corpus_or_state_is_404(workspace):
    discovered = discover(workspace)
    name = source_of(workspace / "depth1")
    for rest, message in (("nobody", NO_SUCH_CORPUS), (f"{name}/elsewhere", NO_SUCH_STATE)):
        response = get(discovered, rest)
        assert (response.status, answer(response)["error"]) == (404, message)


def test_the_index_names_every_corpus_where_it_sits_and_the_report(workspace):
    discovered = discover(workspace)
    body = answer(get(discovered, ""))
    assert [c["root"] for c in body["corpora"]] == list(BOTH)
    assert [c["state"] for c in body["corpora"]] == [
        f"/api/v1/state/{source_of(workspace / name)}" for name in BOTH
    ]
    assert body["report"] == list(discovered.report) and body["report"]


def test_the_submit_breakdown_is_published_beside_the_verdict_and_is_never_one(workspace):
    # ⛔ `AX-02/3`, closed here: the recorded breakdown reached the progress
    # document and stopped there, so nothing on the wire carried it. ⭐ Both
    # directions — a run with a breakdown publishes the map, and one without
    # publishes `None` rather than `{}`, because absent and empty are different
    # claims and the record refuses an empty map.
    discovered = discover(workspace)
    root = workspace / "depth2"
    name, key = source_of(root), unit_keys(root)[0]

    def reported():
        return answer(get(discovered, f"{name}/units/{key}"))["practices"][SECTION]["last"]

    record(root, key, mode="run", exit_code=0)
    assert reported()["cases"] is None
    broken = {"test_the_ask": True, "test_an_edge": False}
    record(root, key, mode="test", exit_code=0, when=LATER, cases=broken)
    said = reported()
    assert said["cases"] == broken
    # ⛔ **And it is a REPORT and never a second verdict**: this Submit exited
    # zero with a failed edge, and `passed` says so unchanged (`AX-02`).
    assert said["passed"] is True
