"""Mirror of `src/studyforge/corpus/discovery/assemble.py` (R12).

⭐ **The acceptance clause *a stale cache is detected and the scan wins* is two
assertions here, not one**: the verdict says `stale`, and the returned site is
the one on disk rather than the one the cache remembered.
"""

from __future__ import annotations

import json

from studyforge.address import Address
from studyforge.corpus.discovery import (
    FRESH,
    SITE_API,
    STALE,
    UNVERIFIABLE,
    assemble,
    cache_path,
    scan_sha256,
)
from studyforge.corpus.discovery import cache as cache_module
from studyforge.corpus.placement import (
    SITE_CACHE_FILENAME,
    UNIT_SUFFIX,
    Identity,
    identity,
    profile_for,
)

CORPUS = "code-corpus"
ADDRESS = Address.of("basics", "16-streams-api")
DEPTHS = {CORPUS: 2}


def block(**overrides):
    return Identity(corpus=CORPUS, address=ADDRESS, variant="text", **overrides)


def write_page(root, relative, declared):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"<!doctype html><html><head>{identity.render(declared)}</head><body>x</body></html>",
        encoding="utf-8",
    )
    return path


def where(root):
    return cache_path(root, profile_for("tree"))


# --- the first run ----------------------------------------------------------


def test_a_first_run_writes_the_cache_and_says_it_did_not_exist(tmp_path):
    write_page(tmp_path, f"a{UNIT_SUFFIX}", block(unit=7))
    found = assemble(tmp_path, DEPTHS, cache=where(tmp_path))
    assert found.verdict == UNVERIFIABLE
    assert found.rewritten is True
    assert where(tmp_path).is_file()
    assert any("does not exist yet" in line for line in found.report)
    assert found.site.unit(CORPUS, ADDRESS, 7) is not None


def test_a_second_run_over_an_unchanged_tree_is_fresh_and_rewrites_nothing(tmp_path):
    write_page(tmp_path, f"a{UNIT_SUFFIX}", block(unit=7))
    assemble(tmp_path, DEPTHS, cache=where(tmp_path))
    before = where(tmp_path).read_text(encoding="utf-8")
    again = assemble(tmp_path, DEPTHS, cache=where(tmp_path))
    assert again.verdict == FRESH
    assert again.rewritten is False
    assert where(tmp_path).read_text(encoding="utf-8") == before


# --- ⭐ a stale cache is DETECTED, and the scan wins -------------------------


def test_a_cache_written_before_a_page_moved_is_detected_as_stale(tmp_path):
    write_page(tmp_path, f"one/a{UNIT_SUFFIX}", block(unit=7))
    assemble(tmp_path, DEPTHS, cache=where(tmp_path))
    (tmp_path / "two").mkdir()
    (tmp_path / "one" / f"a{UNIT_SUFFIX}").rename(tmp_path / "two" / f"a{UNIT_SUFFIX}")

    found = assemble(tmp_path, DEPTHS, cache=where(tmp_path))
    assert found.verdict == STALE
    # ⛔ The scan wins: the site returned is the tree, not the cache.
    assert found.site.units[0].path.as_posix() == f"two/a{UNIT_SUFFIX}"
    # ⭐ And it is still the same unit — identity survived the move (R4).
    assert found.site.unit(CORPUS, ADDRESS, 7) is not None
    assert found.rewritten is True
    assert json.loads(where(tmp_path).read_text("utf-8"))["scan_sha256"] == scan_sha256(found.site)


def test_a_cache_written_before_a_page_was_added_is_detected_as_stale(tmp_path):
    write_page(tmp_path, f"a{UNIT_SUFFIX}", block(unit=7))
    assemble(tmp_path, DEPTHS, cache=where(tmp_path))
    write_page(tmp_path, f"b{UNIT_SUFFIX}", block(unit=8))
    found = assemble(tmp_path, DEPTHS, cache=where(tmp_path))
    assert found.verdict == STALE
    assert len(found.site.units) == 2


def test_a_cache_that_remembers_a_page_the_tree_no_longer_holds_is_stale(tmp_path):
    write_page(tmp_path, f"a{UNIT_SUFFIX}", block(unit=7))
    write_page(tmp_path, f"b{UNIT_SUFFIX}", block(unit=8))
    assemble(tmp_path, DEPTHS, cache=where(tmp_path))
    (tmp_path / f"b{UNIT_SUFFIX}").unlink()
    found = assemble(tmp_path, DEPTHS, cache=where(tmp_path))
    assert found.verdict == STALE
    assert len(found.site.units) == 1


def test_the_scan_wins_even_when_the_cache_is_a_plausible_lie(tmp_path):
    # ⚠️ The strongest form of the clause: a cache whose digest matches its own
    # contents but describes a tree that never existed. Nothing in `assemble`
    # reads a cached artifact list, so there is no path on which it could win.
    write_page(tmp_path, f"a{UNIT_SUFFIX}", block(unit=7))
    invented = {
        "site_api": SITE_API,
        "scan_sha256": "0" * 64,
        "artifacts": [{"path": "invented.unit.html", "identity": block(unit=99).document}],
        "unidentified": [],
    }
    target = where(tmp_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(invented), encoding="utf-8")

    found = assemble(tmp_path, DEPTHS, cache=target)
    assert found.verdict == STALE
    assert found.site.unit(CORPUS, ADDRESS, 99) is None
    assert found.site.unit(CORPUS, ADDRESS, 7) is not None


# --- ⛔ an unsupported or absent `site_api` does not raise -------------------


def test_an_unsupported_site_api_re_scans_and_rewrites_and_says_so(tmp_path):
    write_page(tmp_path, f"a{UNIT_SUFFIX}", block(unit=7))
    target = where(tmp_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"site_api": 99, "artifacts": []}), encoding="utf-8")

    found = assemble(tmp_path, DEPTHS, cache=target)
    assert found.verdict == UNVERIFIABLE
    assert found.rewritten is True
    assert json.loads(target.read_text("utf-8"))["site_api"] == SITE_API
    # ⛔ R6: reported, naming the path, what was declared and what is spoken.
    said = "\n".join(found.report)
    assert SITE_CACHE_FILENAME in said and "99" in said and "site_api [1]" in said
    # ⭐ Nothing is carried forward, which is what makes this R9's refusal.
    assert found.site.units[0].path.as_posix() == f"a{UNIT_SUFFIX}"


def test_a_cache_with_no_version_key_is_treated_the_same_way(tmp_path):
    write_page(tmp_path, f"a{UNIT_SUFFIX}", block(unit=7))
    target = where(tmp_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"artifacts": []}), encoding="utf-8")
    found = assemble(tmp_path, DEPTHS, cache=target)
    assert found.verdict == UNVERIFIABLE and found.rewritten is True
    assert any("no site_api" in line for line in found.report)


def test_a_malformed_cache_is_replaced_rather_than_raising(tmp_path):
    write_page(tmp_path, f"a{UNIT_SUFFIX}", block(unit=7))
    target = where(tmp_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{ half a doc", encoding="utf-8")
    found = assemble(tmp_path, DEPTHS, cache=target)
    assert found.verdict == UNVERIFIABLE and found.rewritten is True
    assert cache_module.read(target).supported is True


# --- R6: the report, and R7: what may not be in it --------------------------


def test_every_unidentified_page_is_named_in_the_report(tmp_path):
    write_page(tmp_path, f"good{UNIT_SUFFIX}", block(unit=7))
    (tmp_path / f"orphan{UNIT_SUFFIX}").write_text("<html>nothing</html>", encoding="utf-8")
    found = assemble(tmp_path, DEPTHS, cache=where(tmp_path))
    assert found.report[0].startswith(f"orphan{UNIT_SUFFIX}:")
    assert "carries no identity block" in found.report[0]


def test_no_line_of_the_report_carries_an_absolute_path(tmp_path):
    (tmp_path / f"orphan{UNIT_SUFFIX}").write_text("<html>nothing</html>", encoding="utf-8")
    for _ in range(2):
        found = assemble(tmp_path, DEPTHS, cache=where(tmp_path))
        for line in found.report:
            assert str(tmp_path) not in line
    assert any(line.startswith(".studyforge/site.json") for line in found.report)


def test_the_cache_may_be_declined_and_nothing_is_written(tmp_path):
    # ⭐ What `studyforge validate` wants, and what a caller with no write
    # access needs: the scan, and an honest "not judged".
    write_page(tmp_path, f"a{UNIT_SUFFIX}", block(unit=7))
    found = assemble(tmp_path, DEPTHS)
    assert found.verdict == UNVERIFIABLE and found.rewritten is False
    assert not (tmp_path / ".studyforge").exists()
    assert any("was not judged" in line for line in found.report)
    assert found.site.unit(CORPUS, ADDRESS, 7) is not None


def test_the_verdict_never_changes_what_is_returned(tmp_path):
    # ⛔ Structural, not a rule anybody follows: the site is `scan`'s result on
    # every branch, so there is nothing for a wrong verdict to corrupt.
    write_page(tmp_path, f"a{UNIT_SUFFIX}", block(unit=7))
    verdicts = {}
    for _ in range(2):
        found = assemble(tmp_path, DEPTHS, cache=where(tmp_path))
        verdicts[found.verdict] = found.site
    assert set(verdicts) == {UNVERIFIABLE, FRESH}
    assert len(set(scan_sha256(site) for site in verdicts.values())) == 1
