"""Mirror of `src/studyforge/corpus/discovery/scan.py` (R12).

⛔ **This module tests IDENTITY, not rendering** (R4). A moved page is still
correctly identified; its relative assets legitimately break, because they
resolve relative to the page (R8). ⚠️ **There is deliberately no test here
requiring a moved page to render** — such a test would force absolute asset
paths and break the `file://` floor.
"""

from __future__ import annotations

import json

import pytest

from studyforge.address import Address
from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.discovery import DiscoveryError, pages, scan
from studyforge.corpus.placement import (
    CONTAINER_SUFFIX,
    UNIT_SUFFIX,
    Identity,
    identity,
    profile_for,
)

#: Two corpora, deliberately at different depths, so the per-corpus depth
#: mapping is exercised rather than assumed.
PROSE = "prose-corpus"
CODE = "code-corpus"
PROSE_ADDRESS = Address.of("modules")
CODE_ADDRESS = Address.of("basics", "16-streams-api")
DEPTHS = {PROSE: 1, CODE: 2}


def block(corpus, address, **overrides):
    return Identity(corpus=corpus, address=address, variant="text", **overrides)


def page(declared):
    return f"<!doctype html><html><head>{identity.render(declared)}</head><body>x</body></html>"


def write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_page(root, relative, declared):
    return write(root, relative, page(declared))


# --- the walk ---------------------------------------------------------------


def test_the_walk_finds_both_page_suffixes_and_nothing_else(tmp_path):
    write_page(tmp_path, f"a{UNIT_SUFFIX}", block(PROSE, PROSE_ADDRESS, unit=1))
    write_page(tmp_path, f"b{CONTAINER_SUFFIX}", block(PROSE, PROSE_ADDRESS, kind="container"))
    write(tmp_path, "index.html", "<html>the root index</html>")
    write(tmp_path, "README.md", "material")
    found = [path.name for path in pages(tmp_path)]
    assert found == [f"a{UNIT_SUFFIX}", f"b{CONTAINER_SUFFIX}"]


def test_the_walk_reaches_inside_the_generated_dot_directory(tmp_path):
    # ⛔ Load-bearing: under `tree` every generated page lives below
    # `.studyforge/`. A walk that skipped dot-directories would report a
    # perfectly empty site for an entire placement profile.
    write_page(tmp_path, f".studyforge/modules/x{UNIT_SUFFIX}", block(PROSE, PROSE_ADDRESS, unit=1))
    assert [path.name for path in pages(tmp_path)] == [f"x{UNIT_SUFFIX}"]


def test_the_walk_order_is_sorted_by_the_path_relative_to_the_root(tmp_path):
    # ⛔ R10. `rglob` answers in filesystem order and two machines answer
    # differently; the scan states its order instead of inheriting one.
    for relative in (f"z/a{UNIT_SUFFIX}", f"a/z{UNIT_SUFFIX}", f"a/a{UNIT_SUFFIX}"):
        write_page(tmp_path, relative, block(PROSE, PROSE_ADDRESS, unit=1))
    walked = [path.relative_to(tmp_path).as_posix() for path in pages(tmp_path)]
    assert walked == sorted(walked)
    assert walked == [f"a/a{UNIT_SUFFIX}", f"a/z{UNIT_SUFFIX}", f"z/a{UNIT_SUFFIX}"]


def test_a_root_that_is_not_a_directory_is_refused_without_naming_it(tmp_path):
    absent = tmp_path / "no-such-root"
    with pytest.raises(DiscoveryError) as raised:
        pages(absent)
    # ⛔ R7: the root is an absolute path on somebody's machine.
    assert str(absent) not in str(raised.value)
    assert "no-such-root" not in str(raised.value)


# --- identity, never the path (R4) ------------------------------------------


def test_a_page_moved_to_a_different_directory_is_still_correctly_identified(tmp_path):
    # ⭐ The acceptance clause, and the whole of R4 in one assertion.
    declared = block(CODE, CODE_ADDRESS, unit=7)
    write_page(tmp_path, f"somewhere/else/entirely/page{UNIT_SUFFIX}", declared)
    site = scan(tmp_path, DEPTHS)
    assert len(site.units) == 1
    assert site.unit(CODE, CODE_ADDRESS, 7) is site.units[0]
    assert site.units[0].identity == declared
    # ⚠️ The path is recorded so a reader can be sent to the file — and it is
    # not what answered the question above.
    assert site.units[0].path.as_posix() == f"somewhere/else/entirely/page{UNIT_SUFFIX}"


def test_a_renamed_artifact_is_still_found_and_correctly_identified(tmp_path):
    declared = block(CODE, CODE_ADDRESS, unit=7)
    write_page(tmp_path, f"16-streams-api/not-the-name-we-minted{UNIT_SUFFIX}", declared)
    site = scan(tmp_path, DEPTHS)
    assert site.unit(CODE, CODE_ADDRESS, 7) is not None
    assert site.units[0].identity == declared


def test_two_corpora_with_different_placement_profiles_are_found_by_one_scan(tmp_path):
    # ⭐ The acceptance clause. The scan never learns that profiles exist: it
    # is handed two real profiles' answers and reads identity out of both.
    tree = profile_for("tree")
    sibling = profile_for("sibling")
    under_tree = tree.unit(CODE_ADDRESS, 7, "Introduction to the Streams API")
    beside_source = sibling.unit(PROSE_ADDRESS, 1, "What a triple is", origin="modules/README.md")
    assert under_tree.page.parts[0] == ".studyforge"
    assert beside_source.page.parts[0] == "modules"

    write_page(tmp_path, under_tree.page.as_posix(), block(CODE, CODE_ADDRESS, unit=7))
    write_page(tmp_path, beside_source.page.as_posix(), block(PROSE, PROSE_ADDRESS, unit=1))

    site = scan(tmp_path, DEPTHS)
    assert site.corpora == (CODE, PROSE)
    assert site.unit(CODE, CODE_ADDRESS, 7) is not None
    assert site.unit(PROSE, PROSE_ADDRESS, 1) is not None
    assert site.unidentified == ()


def test_a_container_page_is_identified_as_one(tmp_path):
    write_page(
        tmp_path,
        f"anywhere/streams{CONTAINER_SUFFIX}",
        block(CODE, CODE_ADDRESS, kind="container"),
    )
    site = scan(tmp_path, DEPTHS)
    assert len(site.containers) == 1
    assert site.units == ()


def test_each_corpus_address_is_checked_against_its_own_declared_depth(tmp_path):
    # ⚠️ The depth is per corpus, which is why `scan` takes a mapping. A
    # depth-2 address filed under the depth-1 corpus is a reported fault, not
    # a silently accepted page.
    write_page(tmp_path, f"a{UNIT_SUFFIX}", block(PROSE, CODE_ADDRESS, unit=1))
    site = scan(tmp_path, DEPTHS)
    assert site.artifacts == ()
    assert len(site.unidentified) == 1
    assert "segment(s)" in site.unidentified[0].fault
    assert "level(s)" in site.unidentified[0].fault


# --- reported by name, never skipped silently (R6) --------------------------


def test_an_artifact_with_no_identity_block_is_reported_by_name(tmp_path):
    # ⭐ The acceptance clause. A page that quietly vanishes from a site is the
    # failure discovery exists to make impossible.
    write(tmp_path, f"orphan{UNIT_SUFFIX}", "<html><body>no block here</body></html>")
    site = scan(tmp_path, DEPTHS)
    assert site.artifacts == ()
    assert [found.path.as_posix() for found in site.unidentified] == [f"orphan{UNIT_SUFFIX}"]
    assert "carries no identity block" in site.unidentified[0].fault


def test_one_unidentifiable_page_does_not_hide_the_ones_after_it(tmp_path):
    write(tmp_path, f"a-broken{UNIT_SUFFIX}", "<html>nothing</html>")
    write_page(tmp_path, f"b-good{UNIT_SUFFIX}", block(CODE, CODE_ADDRESS, unit=7))
    site = scan(tmp_path, DEPTHS)
    assert len(site.unidentified) == 1
    assert site.unit(CODE, CODE_ADDRESS, 7) is not None


def test_a_block_that_is_not_valid_json_is_reported_without_echoing_it(tmp_path):
    payload = "{not json, and it holds " + "/" + "home/somebody/secret"
    write(
        tmp_path,
        f"bad{UNIT_SUFFIX}",
        f'<script type="application/json" id="studyforge-identity">{payload}</script>',
    )
    site = scan(tmp_path, DEPTHS)
    fault = site.unidentified[0].fault
    assert "not valid JSON" in fault
    # ⛔ R7, rubric §1f: a refusal that quotes an unreadable block has only
    # relocated whatever it held into a log.
    assert "secret" not in fault


def test_a_page_naming_a_corpus_the_scan_holds_no_depth_for_is_reported(tmp_path):
    write_page(tmp_path, f"stray{UNIT_SUFFIX}", block("some-other-corpus", PROSE_ADDRESS, unit=1))
    site = scan(tmp_path, DEPTHS)
    assert site.artifacts == ()
    fault = site.unidentified[0].fault
    assert "no depth for" in fault
    # ⛔ The declared name is described, never echoed.
    assert "some-other-corpus" not in fault


def test_a_page_that_is_not_valid_utf8_is_reported_rather_than_raising(tmp_path):
    path = tmp_path / f"binary{UNIT_SUFFIX}"
    path.write_bytes(b"\xff\xfe not text at all")
    site = scan(tmp_path, DEPTHS)
    assert "not valid UTF-8" in site.unidentified[0].fault


def test_no_fault_a_scan_records_carries_an_absolute_path(tmp_path):
    # ⛔ R7. This is a scan over a real root, and every one of these lines is
    # printed. The root is the one thing that must not survive into any of them.
    write(tmp_path, f"a{UNIT_SUFFIX}", "<html>nothing</html>")
    write(tmp_path, f"b{UNIT_SUFFIX}", '<script id="studyforge-identity">{{</script>')
    write_page(tmp_path, f"c{UNIT_SUFFIX}", block("unknown-corpus", PROSE_ADDRESS, unit=1))
    site = scan(tmp_path, DEPTHS)
    assert len(site.unidentified) == 3
    for found in site.unidentified:
        assert str(tmp_path) not in found.fault
        assert not found.path.is_absolute()


# --- what does NOT get caught -----------------------------------------------


def test_a_personal_data_leak_stops_the_scan_rather_than_becoming_a_finding(tmp_path):
    # ⛔ Ruling 58. `PersonalDataLeak` is not a `DiscoveryError`, so it travels
    # as itself. Filed among the unidentified it would read as one more page
    # that could not be identified, in a report whose whole purpose is that
    # nobody reads it line by line.
    leaky = dict(block(CODE, CODE_ADDRESS, unit=7).document)
    leaky["origin"] = "/" + "home/jane/notes.md"
    write(
        tmp_path,
        f"leak{UNIT_SUFFIX}",
        f'<script type="application/json" id="studyforge-identity">{json.dumps(leaky)}</script>',
    )
    with pytest.raises(PersonalDataLeak):
        scan(tmp_path, DEPTHS)


def test_an_empty_root_scans_to_an_empty_site_rather_than_failing(tmp_path):
    site = scan(tmp_path, DEPTHS)
    assert site.artifacts == ()
    assert site.unidentified == ()
    assert site.corpora == ()
