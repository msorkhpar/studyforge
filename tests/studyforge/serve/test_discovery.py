"""Mirror of `src/studyforge/serve/discovery.py` (R12).

⭐ **The serving task's acceptance**: *"the server is given a root and finds the corpus
itself, with no configured paths"*; *"two corpora with different placement profiles serve from one
instance"*; *"a stale discovery cache is detected rather than trusted"*.

⛔ **"Serves the Java corpus discovered at startup" is NOT met here and nothing here is
called by that name**: it needs the Java corpus present, and stays an open case.
"""

from __future__ import annotations

import json
import shutil

import pytest

from studyforge.contents import found as present
from studyforge.corpus.discovery import FRESH, STALE, UNVERIFIABLE
from studyforge.corpus.manifest import MANIFEST_FILENAME
from studyforge.generate import write_site
from studyforge.generate.declarations import read_corpus
from studyforge.serve.discovery import DiscoveryRefused, ServedCorpus, discover, manifests
from tests.studyforge.generate.corpora import BOTH, FIXTURES
from tests.studyforge.serve.built import (
    a_workspace,
    depth_of,
    pages_of,
    source_of,
    unit_keys,
)


def cache_of(root):
    return root / read_corpus(root).shared.site_cache


def test_a_root_given_nothing_else_finds_both_corpora_and_both_profiles(tmp_path):
    workspace = a_workspace(tmp_path)
    found = discover(workspace)
    assert [served.relative.as_posix() for served in found.corpora] == list(BOTH)
    expected = {source_of(workspace / name): depth_of(workspace / name) for name in BOTH}
    assert found.depths == expected
    assert sorted(served.profile for served in found.corpora) == ["sibling", "tree"]
    assert set(found.by_source) == set(expected)


def test_the_startup_scan_finds_every_page_each_build_wrote(tmp_path):
    workspace = a_workspace(tmp_path)
    for served in discover(workspace).corpora:
        assert present(served.startup.site, served.source) == frozenset(unit_keys(served.root))
        assert served.startup.site.unidentified == ()


def test_a_corpus_root_served_directly_is_found_at_the_root(tmp_path):
    root = a_workspace(tmp_path, ("depth2",)) / "depth2"
    found = discover(root)
    assert [served.relative.as_posix() for served in found.corpora] == ["."]
    assert found.corpora[0].href("basics/page.unit.html") == "/basics/page.unit.html"


def test_manifests_are_found_at_any_depth_in_a_stated_order(tmp_path):
    for relative in ("b/corpus.json", "a/deep/er/corpus.json", "corpus.json"):
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / relative).write_text("{}\n", encoding="utf-8")
    (tmp_path / "c" / MANIFEST_FILENAME).mkdir(parents=True)  # a directory is not a manifest
    listed = [path.relative_to(tmp_path).as_posix() for path in manifests(tmp_path)]
    assert listed == ["a/deep/er/corpus.json", "b/corpus.json", "corpus.json"]


def test_a_root_with_no_corpus_is_refused_naming_no_absolute_path(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    for root in (empty, tmp_path / "missing"):
        with pytest.raises(DiscoveryRefused) as refused:
            discover(root)
        assert str(tmp_path) not in str(refused.value)


def test_a_manifest_that_cannot_be_read_is_reported_by_name_and_the_rest_are_served(tmp_path):
    workspace = a_workspace(tmp_path)
    broken = workspace / "broken"
    broken.mkdir()
    (broken / MANIFEST_FILENAME).write_text("{\n", encoding="utf-8")
    found = discover(workspace)
    assert [served.relative.as_posix() for served in found.corpora] == list(BOTH)
    refused = f"broken/{MANIFEST_FILENAME} is not served"
    assert any(line.startswith(refused) for line in found.report)
    assert not any(str(tmp_path) in line for line in found.report)


def test_a_root_whose_only_manifest_is_unreadable_is_refused_with_the_reason(tmp_path):
    broken = tmp_path / "root" / "broken"
    broken.mkdir(parents=True)
    (broken / MANIFEST_FILENAME).write_text("{\n", encoding="utf-8")
    with pytest.raises(DiscoveryRefused, match=f"broken/{MANIFEST_FILENAME} is not served"):
        discover(tmp_path / "root")


def test_two_corpora_declaring_one_source_under_two_profiles_refuse_the_instance(tmp_path):
    workspace = tmp_path / "workspace"
    for copy in ("first", "second"):
        shutil.copytree(FIXTURES / "depth2", workspace / copy)
    manifest = workspace / "second" / MANIFEST_FILENAME
    document = json.loads(manifest.read_text(encoding="utf-8"))
    document["placement"] = "tree"
    manifest.write_text(json.dumps(document), encoding="utf-8")
    profiles = {read_corpus(workspace / copy).profile.name for copy in ("first", "second")}
    assert len(profiles) == 2
    with pytest.raises(DiscoveryRefused) as refused:
        discover(workspace)
    said = str(refused.value)
    assert f"first/{MANIFEST_FILENAME}" in said and f"second/{MANIFEST_FILENAME}" in said
    assert str(tmp_path) not in said


def test_a_first_start_cannot_judge_the_cache_and_writes_it_and_a_second_finds_it_fresh(tmp_path):
    workspace = a_workspace(tmp_path)
    assert {served.verdict for served in discover(workspace).corpora} == {UNVERIFIABLE}
    assert {served.verdict for served in discover(workspace).corpora} == {FRESH}


def test_a_stale_cache_is_detected_at_startup_reported_and_rewritten(tmp_path):
    workspace = a_workspace(tmp_path)
    discover(workspace)
    for name in BOTH:
        cache = cache_of(workspace / name)
        document = json.loads(cache.read_text(encoding="utf-8"))
        document["scan_sha256"] = "0" * 64
        cache.write_text(json.dumps(document), encoding="utf-8")
    again = discover(workspace)
    assert {served.verdict for served in again.corpora} == {STALE}
    for name in BOTH:
        stale = f"{name}: the discovery cache is stale; the scan is the authority either way"
        assert stale in again.report
    assert {served.verdict for served in discover(workspace).corpora} == {FRESH}


def test_a_cache_that_cannot_be_written_is_reported_and_discovery_still_runs(tmp_path):
    root = a_workspace(tmp_path, ("depth1",)) / "depth1"
    cache = cache_of(root)
    cache.unlink(missing_ok=True)
    cache.mkdir(parents=True)
    found = discover(root)
    assert found.corpora[0].verdict == UNVERIFIABLE
    assert any("could not be written" in line for line in found.report)
    assert present(found.corpora[0].startup.site, found.corpora[0].source)


def test_rescan_reads_the_tree_now_and_never_the_startup_scan(tmp_path):
    root = a_workspace(tmp_path, ("depth2",)) / "depth2"
    served = discover(root).corpora[0]
    key = unit_keys(root)[0]
    for page in pages_of(root, key):
        page.unlink()
    assert key in present(served.startup.site, served.source)
    assert key not in present(served.rescan(), served.source)


def test_a_discovered_corpus_is_scanned_at_its_root_unless_a_scan_root_is_given(tmp_path):
    # ⭐ Where the record lives and where pages are scanned are
    # two fields, and the second defaults to the first.
    root = a_workspace(tmp_path, ("depth1",)) / "depth1"
    served = discover(root).corpora[0]
    assert served.scan_root == served.root == root
    assert present(served.rescan(), served.source)
    # ⭐ The other way: a site built elsewhere is scanned THERE, and the root is not read.
    site = tmp_path / "elsewhere"
    site.mkdir()
    fields = (served.corpus, root, served.relative, served.startup, served.digest)
    elsewhere = ServedCorpus(*fields, scan_root=site)
    assert (elsewhere.root, elsewhere.scan_root) == (root, site)
    assert not present(elsewhere.rescan(), elsewhere.source)
    write_site(root, site)
    assert present(elsewhere.rescan(), elsewhere.source) == present(served.rescan(), served.source)
    assert elsewhere.progress().directory == served.progress().directory


def test_a_manifest_under_a_corpus_s_own_bookkeeping_is_never_a_corpus(tmp_path):
    # ⚠️ Measured: the code copy once mirrored a root-level corpus's manifest,
    # and a restart refused two corpora with one source.
    root = a_workspace(tmp_path, ("depth2",)) / "depth2"
    planted = root / ".studyforge/execution/code" / MANIFEST_FILENAME
    planted.parent.mkdir(parents=True)
    shutil.copy(root / MANIFEST_FILENAME, planted)
    found = discover(root)
    assert [served.relative.as_posix() for served in found.corpora] == ["."]
    assert planted not in manifests(root)


def test_a_bookkeeping_name_with_no_corpus_above_it_is_an_ordinary_directory(tmp_path):
    # ⛔ The control: only a corpus's OWN `.studyforge/` is skipped.
    for relative in (".studyforge/one/corpus.json", "a/.studyforge/two/corpus.json"):
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / relative).write_text("{}\n", encoding="utf-8")
    listed = [path.relative_to(tmp_path).as_posix() for path in manifests(tmp_path)]
    assert listed == [".studyforge/one/corpus.json", "a/.studyforge/two/corpus.json"]


def test_a_corpus_below_the_served_root_has_its_bookkeeping_skipped_too(tmp_path):
    workspace = a_workspace(tmp_path)
    for name in BOTH:
        planted = workspace / name / ".studyforge/execution/code" / MANIFEST_FILENAME
        planted.parent.mkdir(parents=True)
        shutil.copy(workspace / name / MANIFEST_FILENAME, planted)
    found = discover(workspace)
    assert [served.relative.as_posix() for served in found.corpora] == list(BOTH)
