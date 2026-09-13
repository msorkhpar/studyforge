"""Mirror of `tools/quality/locations.py` (R12).

⛔ **Asserted in BOTH directions, and the negative arm is the one `W150` lives on**: a
citation that RESOLVES must never be read as a lost path, or the notice prints a
population in which one member is real. ⭐ Every plant the row names has a test here —
the PATH harm, the INTEGER harm, the resolving citation, the record, the declared
impurity — and each tree is a real git repository under `tmp_path`, because the
population is what git TRACKS (`W148`). ⚠️ A citation this module needs is built in a
STRING LITERAL, which the module under test does not read, so this file is not a member
of its own population.
"""

from __future__ import annotations

import tools.quality as quality
import tools.quality.locations as locations
from tests.support import assert_package_contract, git, init_repository, repository_root, run
from tools.quality.locations import (
    HARM_INTEGER,
    HARM_PATH,
    INTEGER,
    OWN,
    PATH,
    REF,
    location_notice,
    remedy,
    resolve,
    scan,
)
from tools.quality.report import DISK_WALK, TRACKED_WALK

TARGET = "pkg/target.py"


def write(root, files: dict[str, str]):
    """Write `files` under `root` and return it."""
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def tree(tmp_path, files: dict[str, str]):
    """A git repository under `tmp_path` TRACKING `files` and the target module."""
    root = write(init_repository(tmp_path / "repo"), {TARGET: "x = 1\n", **files})
    result = run([git(), "add", "--", TARGET, *files], cwd=root)
    assert result.returncode == 0, result.stdout + result.stderr
    return root


def verdicts(root) -> list[tuple[str, int, str, str]]:
    """Every citation the scan read, as `(document, line, spelling, verdict)`."""
    return [(c.document, c.line, c.spelling, c.verdict) for c in scan(root).citations]


def test_states_its_contract():
    assert_package_contract(locations, "tools.quality.locations")


# --- the two harms, each named -------------------------------------------------


def test_a_BARE_BASENAME_into_a_file_the_document_does_not_own_is_the_PATH_harm(tmp_path):
    root = tree(tmp_path, {"docs/live.md": "the lock is at `target.py:1`\n"})
    assert verdicts(root) == [("docs/live.md", 1, "target.py:1", PATH)]
    first, site, fix = location_notice(root)
    assert f"{HARM_PATH}: 1;" in first
    assert f"{HARM_INTEGER}: 0;" in first
    assert site == "  docs/live.md:1 cites `target.py:1`"
    assert fix.startswith(f"  remedy — {HARM_PATH}")


def test_a_RESOLVING_line_number_citation_is_the_INTEGER_harm_and_never_the_PATH_harm(tmp_path):
    root = tree(tmp_path, {"docs/live.md": "the lock is at `pkg/target.py:1`\n"})
    assert verdicts(root) == [("docs/live.md", 1, "pkg/target.py:1", INTEGER)]
    (only,) = location_notice(root)
    assert f"{HARM_PATH}: 0;" in only
    assert f"{HARM_INTEGER}: 1;" in only


def test_a_citation_that_RESOLVES_FROM_ITS_DOCUMENT_is_never_a_lost_path(tmp_path):
    # ⛔ THE NEGATIVE ARM. Both spellings name the target from where the document sits.
    root = tree(
        tmp_path,
        {"pkg/notes.md": "`target.py:1`\n", "docs/deep/live.md": "`../../pkg/target.py:1`\n"},
    )
    assert {row[3] for row in verdicts(root)} == {INTEGER}
    assert len(verdicts(root)) == 2


def test_resolve_names_the_file_from_the_root_or_the_document_and_nothing_else():
    tracked = frozenset({TARGET})
    assert resolve("docs/live.md", TARGET, tracked) == TARGET
    assert resolve("pkg/notes.md", "target.py", tracked) == TARGET
    assert resolve("docs/live.md", "target.py", tracked) is None


def test_a_document_citing_its_OWN_line_is_admitted(tmp_path):
    root = tree(tmp_path, {"docs/live.md": "see `docs/live.md:1` above\n"})
    assert verdicts(root) == [("docs/live.md", 1, "docs/live.md:1", OWN)]


def test_a_fenced_REF_admits_the_integer_and_never_the_path(tmp_path):
    # ⭐ Ruling 169 speaks about a reading's INTEGER. The unfenced-ref block is a
    # live citation wearing a costume, and a basename is lost with or without a ref.
    text = (
        "```text\nmeasured at abc1234\npkg/target.py:1 read\ntarget.py:1 read\n```\n\n"
        "```text\npkg/target.py:1 no ref\n```\n"
    )
    root = tree(tmp_path, {"docs/live.md": text})
    assert [(row[1], row[3]) for row in verdicts(root)] == [(3, REF), (4, PATH), (8, INTEGER)]


def test_a_ref_written_in_DIGITS_ONLY_is_the_declared_gap_and_reads_as_no_ref(tmp_path):
    # ⚠️ Found by a plant, not reasoned: a real short sha can be all digits, and a
    # seven-digit number is not a ref this predicate can tell apart from a count.
    text = "```text\nmeasured at 2153778\npkg/target.py:1 read\n```\n"
    root = tree(tmp_path, {"docs/live.md": text})
    assert [(row[1], row[3]) for row in verdicts(root)] == [(3, INTEGER)]


def test_the_two_harms_are_spelled_apart_and_each_remedy_is_the_output_shape():
    assert HARM_PATH != HARM_INTEGER
    assert remedy(PATH).startswith(HARM_PATH)
    assert "<n>" in remedy(PATH)
    assert "Ruling 163" in remedy(PATH)
    assert remedy(INTEGER).startswith(HARM_INTEGER)
    assert "Ruling 169" in remedy(INTEGER)


# --- what is NOT read, by name ----------------------------------------------------


def test_a_RECORD_is_not_read_and_the_exclusion_is_no_wider_than_the_records(tmp_path):
    lost = "`target.py:1`\n"
    root = tree(
        tmp_path,
        {
            "docs/tasks/handoffs/W1.md": lost,
            "docs/tasks/BOARD-ARCHIVE.md": lost,
            "docs/tasks/rows/W1.md": lost,
        },
    )
    assert verdicts(root) == [("docs/tasks/rows/W1.md", 1, "target.py:1", PATH)]


def test_a_python_STRING_LITERAL_is_a_FIXTURE_member_counted_and_never_read(tmp_path):
    root = tree(tmp_path, {"tests/test_x.py": 'EXPECTED = "target.py:1: [size] too long."\n'})
    result = scan(root)
    assert result.citations == ()
    assert result.literals == 1
    assert "1 in string literals" in location_notice(root)[0]


def test_python_COMMENTS_and_DOCSTRINGS_are_read(tmp_path):
    source = '"""Cites target.py:1 here."""\n\n# and target.py:1 here\nx = 1\n'
    root = tree(tmp_path, {"tools/x.py": source})
    assert [(row[1], row[3]) for row in verdicts(root)] == [(1, PATH), (3, PATH)]


def test_a_suffix_NO_tracked_file_carries_is_NOT_A_PATH(tmp_path):
    root = tree(tmp_path, {"docs/live.md": "host `evil.example:8765`, ratio 4.5:1\n"})
    result = scan(root)
    assert result.citations == ()
    assert result.pathless == 2


def test_a_BACKSLASH_escape_before_a_basename_is_the_declared_parse_gap(tmp_path):
    root = tree(
        tmp_path,
        {"docs/live.md": "a transcript `\\nW20.md:198`\n", "docs/b.md": "W20.md:198\n"},
    )
    assert verdicts(root) == [("docs/b.md", 1, "W20.md:198", PATH)]


def test_git_failing_to_answer_is_the_DISK_walk_and_still_reads(tmp_path):
    root = write(tmp_path / "plain", {TARGET: "x = 1\n", "docs/live.md": "`target.py:1`\n"})
    result = scan(root)
    assert result.walk == DISK_WALK
    assert [c.verdict for c in result.citations] == [PATH]


# --- the registry and the live tree ---------------------------------------------------


def test_it_is_a_NOTICE_and_never_moves_the_exit_code():
    assert location_notice in quality.NOTICES
    assert location_notice not in quality.CHECKS


def test_the_LIVE_tree_is_read_and_this_rows_own_modules_carry_neither_harm():
    result = scan(repository_root())
    assert result.walk == TRACKED_WALK
    assert result.documents > 0
    assert result.citations, "0 citations read over the whole tree is a blind scan"
    owned = {
        "tools/quality/citations.py",
        "tools/quality/locations.py",
        "tools/tests/quality/test_citations.py",
        "tools/tests/quality/test_locations.py",
    }
    harmed = [c for c in result.citations if c.document in owned and c.verdict in (PATH, INTEGER)]
    assert harmed == []
