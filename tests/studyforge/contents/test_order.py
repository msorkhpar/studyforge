"""Mirror of `src/studyforge/contents/order.py` (R12)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from studyforge.contents import (
    LINK_FIELDS,
    LINK_KEYS,
    ContentsError,
    build,
    links,
    neighbours,
    order,
    positions,
)
from studyforge.corpus.placement import ROOT_INDEX_FILENAME
from tests.studyforge.contents.corpora import (
    a_container,
    a_manifest,
    depth2_manifest,
    fixture_contents,
)
from tests.support import repository_root

DEPTH2_ORDER = (
    "advanced/02-going-further/unit-01",
    "advanced/02-going-further/unit-02",
    "basics/01-getting-started/unit-01",
    "basics/01-getting-started/unit-02",
    "basics/01-getting-started/unit-03",
)


def test_the_reading_order_is_a_depth_first_walk_of_the_tree():
    built = fixture_contents("depth2")
    assert tuple(entry.key for entry in order(built)) == DEPTH2_ORDER


def test_a_depth_one_corpus_reads_in_ordinal_order():
    built = fixture_contents("depth1")
    assert [entry.ordinal for entry in order(built)] == [1, 2, 3]


def test_the_walk_is_the_same_walk_every_time():
    # ⛔ R10: nothing here consults a set, a clock or a filesystem.
    built = fixture_contents("depth2")
    assert order(built) == order(built)


def test_positions_agree_with_the_walk():
    built = fixture_contents("depth2")
    assert positions(built) == {key: n for n, key in enumerate(DEPTH2_ORDER, start=1)}


def test_the_first_unit_has_no_previous_and_the_last_has_no_next():
    built = fixture_contents("depth2")
    first = neighbours(built, DEPTH2_ORDER[0])
    last = neighbours(built, DEPTH2_ORDER[-1])
    assert first.previous is None
    assert first.next.key == DEPTH2_ORDER[1]
    assert last.next is None
    assert last.previous.key == DEPTH2_ORDER[-2]


def test_neighbours_report_where_the_unit_sits_in_the_whole_corpus():
    here = neighbours(fixture_contents("depth2"), DEPTH2_ORDER[2])
    assert (here.position, here.total) == (3, 5)


def test_a_unit_this_corpus_does_not_declare_is_refused_not_answered_emptily():
    # ⛔ An absent neighbour and an absent unit are different facts, and a bar
    # rendered from the second is a page that quietly points nowhere.
    with pytest.raises(ContentsError) as raised:
        neighbours(fixture_contents("depth2"), "basics/01-getting-started/unit-09")
    assert "declares 5 unit(s)" in str(raised.value)


def test_the_bar_a_middle_unit_gets_carries_all_three_slots_in_a_stated_order():
    found = links(fixture_contents("depth2"), DEPTH2_ORDER[2])
    assert tuple(found) == LINK_FIELDS
    assert all(tuple(slot) == LINK_KEYS for slot in found.values())


def test_an_absent_slot_is_missing_rather_than_present_and_empty():
    built = fixture_contents("depth2")
    assert "previous" not in links(built, DEPTH2_ORDER[0])
    assert "next" not in links(built, DEPTH2_ORDER[-1])
    assert "index" in links(built, DEPTH2_ORDER[0])


def test_every_href_is_relative_and_none_is_rooted():
    # ⛔ R8: a rooted href works under a server and breaks over `file://`.
    built = fixture_contents("depth2")
    for key in DEPTH2_ORDER:
        for slot in links(built, key).values():
            assert not slot["href"].startswith("/")
            assert ":" not in slot["href"]


def test_the_same_target_has_a_different_href_from_each_asking_page():
    # ⭐ Why no href is stored: under `sibling` the neighbours of one unit sit
    # in different directories, so there is no single correct answer.
    built = fixture_contents("depth2")
    from_second = links(built, DEPTH2_ORDER[1])["next"]["href"]
    from_third = links(built, DEPTH2_ORDER[3])["previous"]["href"]
    assert from_second != from_third
    assert from_second.startswith("../")


def test_the_index_link_is_labelled_with_the_corpuss_own_title():
    # ⛔ R1: any word this framework chose would be its own sentence in every
    # corpus's chrome.
    built = fixture_contents("depth2")
    slot = links(built, DEPTH2_ORDER[0])["index"]
    assert slot["label"] == built.title == "Depth Two Demo"
    assert slot["href"].endswith(ROOT_INDEX_FILENAME)


def test_a_neighbour_is_labelled_with_the_units_own_title():
    built = fixture_contents("depth2")
    assert links(built, DEPTH2_ORDER[0])["next"]["label"] == "Where to go next"


def test_a_lone_unit_gets_an_index_link_and_nothing_else():
    manifest = depth2_manifest()
    container = a_container(manifest, ("a", "b"), ("A", "B"), units=[{"n": 1, "title": "Only"}])
    built = build(manifest, (container,))
    assert tuple(links(built, "a/b/unit-01")) == ("index",)


def test_no_markup_reaches_a_link():
    # ⛔ R13: contents as data means data; rendering is somebody else's row.
    built = fixture_contents("depth2")
    for key in DEPTH2_ORDER:
        for slot in links(built, key).values():
            assert "<" not in slot["href"] and "<" not in slot["label"]


def test_this_module_is_where_the_ordering_lives():
    # ⛔ One orderer. A second `sorted` over entries anywhere else in the
    # package would be a second answer to the question this module owns.
    package = repository_root() / "src" / "studyforge" / "contents"
    sorters = {
        path.name: sum(
            1
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "sorted"
        )
        for path in sorted(package.glob("*.py"))
    }
    # ⭐ `tree` sorts segments — that is where sibling order is decided — and
    # `document`/`status` sort only to name unknown keys in a refusal.
    assert sorters["order.py"] == 0
    assert sorters["entries.py"] == 0
    assert sorters["tree.py"] == 1


def test_the_walk_is_recursive_rather_than_depth_two_by_hand():
    # ⭐ Generalised from a fixed nesting to `len(levels)`: a three-level
    # corpus walks with no change to this module.
    manifest = a_manifest(levels=["a", "b", "c"])
    containers = (
        a_container(manifest, ("x", "y", "z"), ("X", "Y", "Z"), units=[{"n": 1, "title": "One"}]),
        a_container(manifest, ("x", "y", "w"), ("X", "Y", "W"), units=[{"n": 1, "title": "Two"}]),
    )
    built = build(manifest, containers)
    assert [entry.title for entry in order(built)] == ["Two", "One"]


def test_the_package_never_imports_the_renderer():
    # ⛔ The direction is renderer-depends-on-contents, never the reverse.
    package = repository_root() / "src" / "studyforge" / "contents"
    for path in sorted(package.glob("*.py")):
        assert "studyforge.render" not in Path(path).read_text(encoding="utf-8")
