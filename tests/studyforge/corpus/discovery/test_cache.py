"""Mirror of `src/studyforge/corpus/discovery/cache.py` (R12).

⛔ **Ruling 95's two traps are asserted here**, because a builder copying
the unit content's `content_api` faithfully would get both wrong: an unsupported
`site_api` **does not raise**, and `site_api` is **not** the staleness
mechanism.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import PurePosixPath

from studyforge.address import Address
from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.discovery import SITE_API, SITE_KEYS, Artifact, Site, Unidentified
from studyforge.corpus.discovery import cache as cache_module
from studyforge.corpus.placement import (
    GENERATED_ROOT,
    IGNORE_FILENAME,
    SITE_CACHE_FILENAME,
    Identity,
    profile_for,
)
from studyforge.version import CONTRACT_FIELDS
from tests.support import init_repository, is_ignored

ADDRESS = Address.of("basics", "16-streams-api")
UNIT = Artifact(
    PurePosixPath("anywhere/seven.unit.html"),
    Identity(corpus="code-corpus", address=ADDRESS, variant="text", unit=7),
)
SITE = Site((UNIT,), (Unidentified(PurePosixPath("orphan.unit.html"), "carries no block"),))


def dirty(root):
    """What `git status` has to say about `root`, untracked files included.

    ⭐ **The question a workspace pin check asks**, asked here of a
    throwaway repository: a corpus that is served and is still clean is the
    whole of the rule, and it is not answerable by looking at the ignore file's
    text.
    """
    environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        env=environment,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return [line[3:] for line in result.stdout.splitlines()]


def written(tmp_path, document):
    path = tmp_path / SITE_CACHE_FILENAME
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


# --- R21: the contract is located, versioned, and has one writer ------------


def test_site_api_is_registered_in_the_shared_tuple():
    # ⛔ The convention `CONTRACT_FIELDS` states of itself: a task that versions
    # a new contract registers it there in the same commit, or the shared guard
    # cannot see it.
    assert "site_api" in CONTRACT_FIELDS


def test_the_cache_is_written_with_the_keys_in_a_stated_order():
    assert list(cache_module.document(SITE)) == list(SITE_KEYS)
    assert cache_module.document(SITE)["site_api"] == SITE_API


def test_the_cache_goes_where_placement_says_and_the_answer_is_profile_independent(tmp_path):
    # ⚠️ The same under every profile, because a profile that could move the
    # cache would make two corpora on one disk unfindable by one scan.
    answers = {cache_module.cache_path(tmp_path, profile_for(name)) for name in ("tree", "sibling")}
    assert len(answers) == 1
    assert answers.pop() == tmp_path / ".studyforge" / SITE_CACHE_FILENAME


# --- R10: the same tree renders to the same bytes ---------------------------


def test_an_unchanged_site_renders_to_identical_bytes():
    assert cache_module.render(SITE) == cache_module.render(SITE)


def test_the_bytes_do_not_depend_on_the_order_the_site_was_built_in():
    other = Artifact(PurePosixPath("a/first.unit.html"), UNIT.identity)
    assert cache_module.render(Site((UNIT, other))) == cache_module.render(Site((other, UNIT)))


def test_there_is_no_clock_in_the_document():
    # ⚠️ §6 gives `ingested` an exemption from R10; this document needs none,
    # because the question a date would answer is answered by `scan_sha256`.
    assert "ingested" not in cache_module.render(SITE)


def test_the_render_round_trips_through_read(tmp_path):
    path = tmp_path / "deep" / SITE_CACHE_FILENAME
    cache_module.write(path, SITE)
    cached = cache_module.read(path)
    assert cached is not None and cached.supported
    assert cached.scan_sha256 == cache_module.document(SITE)["scan_sha256"]


def test_write_creates_the_directory_and_leaves_no_staging_file(tmp_path):
    path = tmp_path / ".studyforge" / SITE_CACHE_FILENAME
    cache_module.write(path, SITE)
    assert path.is_file()
    # ⭐ `W425`: the ignore file is written beside the cache in the same act,
    # and it is the ONLY other thing this writer leaves behind.
    assert sorted(item.name for item in path.parent.iterdir()) == [
        IGNORE_FILENAME,
        SITE_CACHE_FILENAME,
    ]


# --- ⛔ `W425`: the cache is ignored where it sits, or a served corpus is dirty


def test_the_cache_is_ignored_by_git_the_first_time_it_is_written(tmp_path):
    # ⭐ The whole rule, measured the way a workspace pin check measures it:
    # a repository that is clean, serves, and is still clean.
    repository = init_repository(tmp_path)
    cache_module.write(repository / GENERATED_ROOT / SITE_CACHE_FILENAME, SITE)
    assert dirty(repository) == []


def test_the_ignore_file_hides_itself_so_nothing_new_is_left_to_commit(tmp_path):
    repository = init_repository(tmp_path)
    cache_module.write(repository / GENERATED_ROOT / SITE_CACHE_FILENAME, SITE)
    ignore = repository / GENERATED_ROOT / IGNORE_FILENAME
    assert ignore.is_file()
    assert is_ignored(f"{GENERATED_ROOT}/{IGNORE_FILENAME}", cwd=repository)


def test_the_cache_goes_dirty_the_moment_the_rule_stops_being_written(tmp_path):
    # ⛔ The plant this row exists to keep failing. Written by hand exactly as
    # `write` would leave the directory MINUS the ignore file, so a green run
    # here is evidence about the rule and not about the fixture.
    repository = init_repository(tmp_path)
    (repository / GENERATED_ROOT).mkdir(parents=True)
    (repository / GENERATED_ROOT / SITE_CACHE_FILENAME).write_text(
        cache_module.render(SITE), encoding="utf-8"
    )
    assert dirty(repository) == [f"{GENERATED_ROOT}/{SITE_CACHE_FILENAME}"]


def test_an_ignore_file_already_there_is_reported_and_never_rewritten(tmp_path):
    # ⛔ It is not this writer's to change — it may carry the corpus's media
    # policy, which a clone has to read. A corpus generated before this rule
    # is regenerated, not silently repaired.
    directory = tmp_path / GENERATED_ROOT
    directory.mkdir(parents=True)
    theirs = "# theirs\n**/audio/\n"
    (directory / IGNORE_FILENAME).write_text(theirs, encoding="utf-8")
    said = cache_module.write(directory / SITE_CACHE_FILENAME, SITE)
    assert (directory / IGNORE_FILENAME).read_text(encoding="utf-8") == theirs
    assert any("does not ignore" in line and SITE_CACHE_FILENAME in line for line in said)


def test_an_ignore_file_that_already_covers_the_cache_is_left_alone_and_says_nothing(tmp_path):
    directory = tmp_path / GENERATED_ROOT
    directory.mkdir(parents=True)
    theirs = f"# theirs\n{SITE_CACHE_FILENAME}\n**/audio/\n"
    (directory / IGNORE_FILENAME).write_text(theirs, encoding="utf-8")
    assert cache_module.write(directory / SITE_CACHE_FILENAME, SITE) == ()
    assert (directory / IGNORE_FILENAME).read_text(encoding="utf-8") == theirs


def test_a_negation_means_the_file_is_deciding_something_this_writer_cannot_read(tmp_path):
    directory = tmp_path / GENERATED_ROOT
    directory.mkdir(parents=True)
    (directory / IGNORE_FILENAME).write_text(
        f"{SITE_CACHE_FILENAME}\n!{SITE_CACHE_FILENAME}\n", encoding="utf-8"
    )
    assert any("does not ignore" in line for line in cache_module.write(directory / "x.json", SITE))


def test_no_line_the_ignore_file_reports_carries_a_path(tmp_path):
    # ⛔ R7: these lines reach a served report, so they name files and never
    # the directory somebody's corpus sits in.
    said = cache_module.write(tmp_path / "deep" / SITE_CACHE_FILENAME, SITE)
    assert said and not any(str(tmp_path) in line or "/" in line.split()[0] for line in said)


# --- ⛔ trap 1: an unsupported or absent `site_api` does NOT raise -----------


def test_an_unsupported_site_api_is_reported_and_not_raised(tmp_path):
    path = written(tmp_path, {"site_api": 99, "scan_sha256": "abc", "artifacts": []})
    cached = cache_module.read(path)
    assert cached is not None
    assert cached.supported is False
    assert "99" in cached.says and "the cache is not read" in cached.says


def test_an_absent_site_api_is_reported_and_not_raised(tmp_path):
    path = written(tmp_path, {"scan_sha256": "abc", "artifacts": []})
    cached = cache_module.read(path)
    assert cached is not None and cached.supported is False
    assert "no site_api" in cached.says


def test_the_bool_hole_is_closed_because_the_predicate_is_the_shared_one(tmp_path):
    # ⛔ `True == 1` in Python, so a JSON `true` walks through a bare
    # membership test. `version.is_supported` is why it does not walk through
    # this one — and using it rather than `check` is what keeps this a report.
    path = written(tmp_path, {"site_api": True, "scan_sha256": "abc"})
    cached = cache_module.read(path)
    assert cached is not None and cached.supported is False
    assert "as a bool" in cached.says


def test_a_supported_site_api_says_so_plainly(tmp_path):
    path = written(tmp_path, {"site_api": SITE_API, "scan_sha256": "abc"})
    cached = cache_module.read(path)
    assert cached is not None and cached.supported is True
    assert cached.scan_sha256 == "abc"


# --- a derived artifact reads as absent or faulted, never as an exception ---


def test_an_absent_cache_reads_as_none(tmp_path):
    # ⛔ `None` is "no file", which is not the same finding as "nothing
    # readable" — collapsing them makes only one of two states visible.
    assert cache_module.read(tmp_path / SITE_CACHE_FILENAME) is None


def test_a_malformed_cache_reads_as_a_fault_rather_than_raising(tmp_path):
    path = tmp_path / SITE_CACHE_FILENAME
    path.write_text("{ not json, and it names " + "/" + "home/jane", encoding="utf-8")
    cached = cache_module.read(path)
    assert cached is not None and cached.fault is not None
    assert cached.supported is False
    # ⛔ R7: the payload is never echoed.
    assert "jane" not in cached.says


def test_a_cache_that_is_not_an_object_reads_as_a_fault(tmp_path):
    path = tmp_path / SITE_CACHE_FILENAME
    path.write_text("[1, 2, 3]", encoding="utf-8")
    cached = cache_module.read(path)
    assert cached is not None and cached.fault == "is not a JSON object"


def test_a_cache_that_is_not_utf8_reads_as_a_fault(tmp_path):
    path = tmp_path / SITE_CACHE_FILENAME
    path.write_bytes(b"\xff\xfe")
    cached = cache_module.read(path)
    assert cached is not None and cached.fault == "is not valid UTF-8"


def test_a_scan_digest_that_is_not_a_string_is_not_believed(tmp_path):
    path = written(tmp_path, {"site_api": SITE_API, "scan_sha256": 7})
    cached = cache_module.read(path)
    assert cached is not None and cached.scan_sha256 is None


# --- R7 -------------------------------------------------------------------


def test_the_cache_is_gated_like_every_other_document_reader(tmp_path):
    # ⛔ W7. This file is generated, but it is generated into a repository
    # somebody clones, and it is the one document in this contract a person can
    # hand-edit with nothing noticing.
    path = written(tmp_path, {"site_api": SITE_API, "origin": "/" + "home/jane/notes.md"})
    try:
        cache_module.read(path)
    except PersonalDataLeak:
        return
    raise AssertionError("a hand-edited cache carrying a home directory was read")


def test_read_names_the_file_by_its_bare_name_unless_told_otherwise(tmp_path):
    # ⛔ The default must be the safe one: an absolute path is what a caller
    # has, and it is the one thing a refusal may not carry.
    path = written(tmp_path, {"site_api": 99})
    assert cache_module.read(path).says.startswith(SITE_CACHE_FILENAME)
    named = cache_module.read(path, ".studyforge/site.json")
    assert named.says.startswith(".studyforge/site.json")
    assert str(tmp_path) not in named.says
