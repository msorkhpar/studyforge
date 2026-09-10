"""Mirror of `src/studyforge/contents/tree.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.contents import ContentsError, build, order, render
from tests.studyforge.contents.corpora import (
    a_container,
    a_manifest,
    depth2_manifest,
    fixture_containers,
    fixture_contents,
    fixture_manifest,
)


def test_a_depth_one_corpus_builds_one_level_of_groups():
    built = fixture_contents("depth1")
    assert built.depth == 1
    assert [group.segment for group in built.groups] == ["depth-one"]
    assert built.groups[0].groups == ()
    assert [entry.ordinal for entry in built.groups[0].entries] == [1, 2, 3]


def test_a_depth_two_corpus_builds_two_levels_from_the_same_code():
    # ⭐ SF-13's acceptance in one assertion: one builder, both depths.
    built = fixture_contents("depth2")
    assert built.depth == 2
    assert [group.segment for group in built.groups] == ["advanced", "basics"]
    assert [child.segment for child in built.groups[0].groups] == ["02-going-further"]
    assert built.groups[0].entries == ()


def test_level_labels_come_from_the_manifest_and_not_from_this_framework():
    # ⛔ R1: the words are the corpus's own.
    built = fixture_contents("depth2")
    assert built.groups[0].level == "section"
    assert built.groups[0].groups[0].level == "module"
    assert built.levels == fixture_manifest("depth2").levels


def test_the_order_the_caller_enumerates_containers_in_does_not_reach_the_bytes():
    # ⛔ R10, and this is the reproducibility test that matters: a caller's
    # enumeration is not a committed input, so reversing it must change nothing.
    manifest = fixture_manifest("depth2")
    containers = fixture_containers("depth2")
    forwards = render(build(manifest, containers))
    backwards = render(build(manifest, tuple(reversed(containers))))
    assert forwards == backwards


def test_siblings_are_ordered_by_segment_as_text_not_by_title():
    # ⚠️ "Advanced" sorts before "Basics" by title too, so the fixture cannot
    # tell the two rules apart. This one can: the titles order one way and the
    # segments the other.
    manifest = depth2_manifest()
    containers = (
        a_container(manifest, ("zulu", "01"), ("Alpha", "First")),
        a_container(manifest, ("alpha", "01"), ("Zulu", "First")),
    )
    built = build(manifest, containers)
    assert [group.segment for group in built.groups] == ["alpha", "zulu"]
    assert [group.title for group in built.groups] == ["Zulu", "Alpha"]


def test_units_keep_the_order_their_container_declares():
    # ⛔ Not re-sorted: the container reader has already refused any map whose
    # ordinals are not contiguous from 1, so a sort here would add nothing and
    # would be a second orderer.
    manifest = a_manifest()
    container = a_container(
        manifest,
        ("course",),
        ("A Course",),
        units=[{"n": 1, "title": "First"}, {"n": 2, "title": "Second"}],
    )
    built = build(manifest, (container,))
    assert [entry.title for entry in order(built)] == ["First", "Second"]


def test_the_contents_count_what_is_declared_and_never_what_exists():
    # ⛔ The short parse with no symptom, in this task's own terms. Nothing in
    # `build` opens a file, so an ungenerated unit cannot go missing here.
    manifest = a_manifest()
    container = a_container(
        manifest,
        ("course",),
        ("A Course",),
        units=[{"n": n, "title": f"U{n}"} for n in range(1, 9)],
    )
    assert len(order(build(manifest, (container,)))) == 8


def test_a_container_at_the_wrong_depth_is_refused():
    manifest = a_manifest()
    other = depth2_manifest()
    container = a_container(other, ("a", "b"), ("A", "B"))
    with pytest.raises(ContentsError) as raised:
        build(manifest, (container,))
    assert "level(s)" in str(raised.value)


def test_two_maps_at_one_address_are_refused_rather_than_one_replacing_the_other():
    manifest = a_manifest()
    containers = (
        a_container(manifest, ("course",), ("A Course",)),
        a_container(manifest, ("course",), ("A Course",)),
    )
    with pytest.raises(ContentsError) as raised:
        build(manifest, containers)
    assert "two container maps" in str(raised.value)


def test_two_titles_for_one_address_prefix_are_refused():
    # ⚠️ Otherwise one loses silently and the reader sees whichever map was
    # read first — an answer that depends on enumeration order (R10).
    manifest = depth2_manifest()
    containers = (
        a_container(manifest, ("basics", "01"), ("Basics", "One")),
        a_container(manifest, ("basics", "02"), ("The Basics", "Two")),
    )
    with pytest.raises(ContentsError) as raised:
        build(manifest, containers)
    assert "called" in str(raised.value)


def test_a_container_whose_titles_do_not_cover_its_levels_is_refused():
    manifest = depth2_manifest()
    container = a_container(manifest, ("basics", "01"), ("Basics", "One"))
    thin = type(container)(
        address=container.address,
        titles=("Basics",),
        variant=container.variant,
        ingested=container.ingested,
        units=container.units,
    )
    with pytest.raises(ContentsError) as raised:
        build(manifest, (thin,))
    assert "title(s)" in str(raised.value)


def test_an_unplaceable_unit_is_refused_as_a_contents_error():
    # ⛔ Re-typed, not re-worded: `placement` owns what a page may be called.
    manifest = a_manifest()
    container = a_container(manifest, ("course",), ("A Course",), units=[{"n": 1, "title": "---"}])
    with pytest.raises(ContentsError) as raised:
        build(manifest, (container,))
    assert "has no place in this corpus" in str(raised.value)


def test_a_corpus_with_no_containers_builds_an_empty_contents_rather_than_raising():
    # ⭐ An adapter that has ingested nothing yet is a real state, and it is
    # not the same as a corpus whose contents would not build.
    built = build(a_manifest(), ())
    assert built.groups == ()
    assert order(built) == ()


def test_the_page_recorded_for_a_unit_is_the_one_its_profile_chose():
    # ⛔ Asked, never composed — `tree` and `sibling` disagree about it.
    tree = fixture_contents("depth1")
    sibling = fixture_contents("depth2")
    assert order(tree)[0].page.as_posix().startswith(".studyforge/")
    assert order(sibling)[0].page.as_posix().startswith("advanced/02-going-further/")
