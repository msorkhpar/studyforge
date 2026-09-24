"""Mirror of `src/studyforge/corpus/discovery/freshness.py` (R12).

⛔ **`site_api` is not the staleness mechanism**, and the digest is what is.
⛔ **No clock either**: there is no `mtime` in this module and there must never
be one (R10).
"""

from __future__ import annotations

import ast
import json
from pathlib import PurePosixPath

from studyforge.address import Address
from studyforge.corpus.discovery import (
    FRESH,
    STALE,
    UNVERIFIABLE,
    VERDICTS,
    Artifact,
    Site,
    Unidentified,
    freshness,
    scan_sha256,
)
from studyforge.corpus.discovery import cache as cache_module
from studyforge.corpus.placement import Identity
from tests.support import repository_root

ADDRESS = Address.of("basics", "16-streams-api")


def artifact(path, **overrides):
    return Artifact(
        PurePosixPath(path),
        Identity(corpus="code-corpus", address=ADDRESS, variant="text", **overrides),
    )


SITE = Site((artifact("anywhere/seven.unit.html", unit=7),))


def test_there_are_three_verdicts_and_they_are_named():
    assert VERDICTS == (FRESH, STALE, UNVERIFIABLE)


# --- the digest -------------------------------------------------------------


def test_the_same_site_digests_the_same_way_twice():
    # ⛔ R10. Two runs over an unchanged tree must agree on any machine.
    assert scan_sha256(SITE) == scan_sha256(SITE)


def test_the_digest_does_not_depend_on_the_order_the_site_was_built_in():
    one = artifact("a.unit.html", unit=1)
    two = artifact("b.unit.html", unit=2)
    assert scan_sha256(Site((one, two))) == scan_sha256(Site((two, one)))


def test_a_page_added_moved_renamed_or_re_identified_changes_the_digest():
    base = scan_sha256(SITE)
    added = scan_sha256(Site((*SITE.artifacts, artifact("b.unit.html", unit=8))))
    moved = scan_sha256(Site((artifact("elsewhere/seven.unit.html", unit=7),)))
    reidentified = scan_sha256(Site((artifact("anywhere/seven.unit.html", unit=8),)))
    assert len({base, added, moved, reidentified}) == 4


def test_a_page_that_could_not_be_identified_is_part_of_the_digest():
    # ⭐ Otherwise a cache written before the page broke would read as fresh,
    # and the R6 finding would be the thing the staleness signal hid.
    orphan = Unidentified(PurePosixPath("orphan.unit.html"), "no block")
    with_fault = Site(SITE.artifacts, (orphan,))
    assert scan_sha256(with_fault) != scan_sha256(SITE)


def test_the_digest_is_taken_over_the_bytes_the_cache_holds():
    # ⭐ One definition of the canonical form serves the digest and the file.
    canonical = json.dumps(SITE.document, separators=(",", ":"), ensure_ascii=False)
    assert json.loads(canonical) == json.loads(json.dumps(SITE.document))
    assert cache_module.document(SITE)["scan_sha256"] == scan_sha256(SITE)


# --- ⛔ trap 2: `site_api` is NOT the staleness mechanism --------------------


def test_the_digest_does_not_move_when_the_version_key_does_not_and_vice_versa():
    # ⛔ Two signals, two tests. `site_api` is a constant of the build; the
    # digest is a function of the tree. Folding one into the other would make
    # an old-but-accurate cache read as stale and give a current-but-wrong one
    # nothing to be told apart by.
    assert "site_api" not in SITE.document
    changed = Site((artifact("anywhere/seven.unit.html", unit=8),))
    assert scan_sha256(changed) != scan_sha256(SITE)
    assert cache_module.SITE_API == cache_module.document(changed)["site_api"]


def test_the_version_key_is_a_constant_and_not_bumped_per_scan():
    # ⚠️ `CONTRACT_FIELDS` is read by every other contract in the build. A
    # member whose value changed per run would break R9's meaning for all of
    # them.
    first = cache_module.document(SITE)["site_api"]
    second = cache_module.document(Site((artifact("z.unit.html", unit=9),)))["site_api"]
    assert first == second == cache_module.SITE_API


# --- ⛔ The signal is content, never a clock ----------------------


def test_this_module_names_no_filesystem_timestamp():
    # ⛔ Measured, not asserted from memory: an mtime verdict and a content
    # verdict once disagreed in opposite directions at once, the mtime verdict
    # flipped FAIL→PASS 33 minutes later with nothing moved, and
    # `git worktree add` resets every mtime — which is where this project's own
    # merges are measured.
    source = (
        repository_root() / "src" / "studyforge" / "corpus" / "discovery" / "freshness.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    # ⭐ The module contract is where the argument is written down and names
    # `mtime` four times; `ast.unparse` drops comments outright, so what is
    # left is the code and nothing else. A grep over the file would read the
    # docstring and always be red.
    if tree.body and isinstance(tree.body[0], ast.Expr):
        tree.body = tree.body[1:]
    code = ast.unparse(tree)
    assert "mtime" not in code
    assert "st_mtime" not in code and "getmtime" not in code


# --- the verdict ------------------------------------------------------------


def test_a_matching_digest_is_fresh():
    assert freshness(SITE, scan_sha256(SITE)) == FRESH


def test_a_digest_that_disagrees_with_the_tree_is_stale():
    assert freshness(SITE, scan_sha256(Site((artifact("z.unit.html", unit=9),)))) == STALE


def test_a_question_that_could_not_be_put_is_unverifiable_and_not_stale():
    # ⚠️ "I cannot answer" is not "the answer is no". The caller reduces an
    # absent cache, an unreadable one and an unsupported one to `None` and
    # reports which — this function is given no file to guess between them.
    assert freshness(SITE, None) == UNVERIFIABLE
