"""Mirror of `tools/quality/pointers.py` (R12).

⛔ **Every positive here is paired with the mention it is one backtick from.**
That pairing is not a style choice: the whole finding this task was scoped on
is that the naive walker's hits were **11 of 11 false**, so a suite that only
proved the check fires would prove the wrong half.

⭐ **The mention corpus is verbatim.** `MEASURED_MENTIONS` holds the real lines
from the real documents, at the sha they were measured on, rather than
invented lookalikes — because the shapes that broke the naive walker are ones
nobody would have thought to invent (a double-backtick span wrapping a
single-backtick one; a regex whose character classes read as a link).
"""

from __future__ import annotations

import pytest

from tests.support import repository_root
from tools.quality import config
from tools.quality.pointers import (
    RULE_ANCHOR,
    RULE_POINTER,
    Pointer,
    check_pointers,
    heading_slugs,
    pointer_coverage,
    pointers,
    prose_lines,
    scan,
    slug,
    strip_code_spans,
)

#: ⛔ **The eleven false positives, verbatim, from the nine lines that carry
#: them** — re-measured on `2926dc2`. Two lines carry two links each.
#:
#: ⚠️ The one line broken across two Python strings is 101 characters in its
#: source document and would breach `LINE_LENGTH` here; implicit concatenation
#: reassembles it exactly rather than paraphrasing it shorter.
MEASURED_MENTIONS = [
    "| markup carrying it (line 310) | `# [Test cases](TestCases.md)` |",
    "in `handoffs/FND-05a.md`, `` `# [Test cases](TestCases.md)` `` quoted in a board",
    "cell, `` `- [1.1. Title](path)` `` in an epic. A repo-wide check that is",
    "`- [1.1. Title](path)`, a handful read `- 1.5. [Title](path)` — the number",
    "way. `SAFE_NAME` is `^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$`: no",
    "  in a handoff, `` `# [Test cases](TestCases.md)` `` quoted in a board cell.",
    "`1. [Title](src/1.md)` — the form every top-level entry of all three",
    "| Java-senior | 205 as `- [1.1. Title](x)` | **6 as `- 1.5. [Title](x)`**"
    ", ordinal outside the link |",
    "| all three | `N. [Title](x)`, the ordinal **as** the list marker | — |",
]

#: How many links a fence-aware walker that does **not** strip code spans finds
#: in the corpus above. ⛔ This number is the task's whole justification, so it
#: is asserted rather than described.
NAIVE_HITS = 11


def write(tmp_path, name: str, text: str):
    """Write a document into a temporary tree and return its path."""
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --- the negative direction: a mention is not a pointer --------------------


def test_the_measured_mentions_are_what_broke_the_naive_walker():
    # ⛔ Watch the naive walker fail on this corpus first. Without this the
    # next assertion is satisfied by a corpus that contains no links at all,
    # which is Ruling 48's defect wearing a passing test.
    import re

    naive = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)\)")
    hits = [match for line in MEASURED_MENTIONS for match in naive.finditer(line)]
    assert len(hits) == NAIVE_HITS


def test_not_one_measured_mention_is_read_as_a_pointer(tmp_path):
    write(tmp_path, "mentions.md", "\n".join(MEASURED_MENTIONS) + "\n")
    assert check_pointers(tmp_path) == []
    assert scan(tmp_path).pointers == ()


@pytest.mark.parametrize("line", MEASURED_MENTIONS)
def test_each_measured_mention_alone_is_not_a_pointer(tmp_path, line):
    # Parametrised as well as collectively: a failure names the shape.
    write(tmp_path, "one.md", line + "\n")
    assert check_pointers(tmp_path) == []


def test_a_fenced_block_is_quoted_material(tmp_path):
    write(
        tmp_path,
        "fenced.md",
        "```\n[gone](nowhere.md)\n```\n\n[also gone](missing.md)\n",
    )
    findings = check_pointers(tmp_path)
    assert [finding.line for finding in findings] == [5]


def test_a_double_backtick_span_wrapping_a_single_one_strips_whole(tmp_path):
    # ⛔ The shape a fixed `` `[^`]*` `` pattern gets wrong: it reads the inner
    # ticks as delimiters and strips the wrong half, leaving the link exposed.
    write(tmp_path, "nested.md", "text `` `[a](gone.md)` `` more\n")
    assert check_pointers(tmp_path) == []


# --- the positive direction: a pointer that resolves to nothing fails ------


def test_a_dangling_pointer_fails_naming_the_file_and_the_line(tmp_path):
    write(tmp_path, "doc.md", "one\n\n[the report](reports/missing.md)\n")
    findings = check_pointers(tmp_path)
    assert len(findings) == 1
    finding = findings[0]
    assert finding.path == "doc.md"
    assert finding.line == 3
    assert finding.rule == RULE_POINTER
    assert "reports/missing.md" in finding.message


def test_a_pointer_that_resolves_is_silent(tmp_path):
    write(tmp_path, "docs/target.md", "# There\n")
    write(tmp_path, "docs/doc.md", "[there](target.md)\n")
    assert check_pointers(tmp_path) == []


def test_a_pointer_to_a_directory_resolves(tmp_path):
    # Measured: the tree carries exactly one, `README.md` -> `docs/conventions/`.
    write(tmp_path, "docs/conventions/one.md", "# One\n")
    write(tmp_path, "README.md", "[conventions](docs/conventions/)\n")
    assert check_pointers(tmp_path) == []


def test_a_relative_pointer_resolves_against_its_own_document(tmp_path):
    write(tmp_path, "docs/tasks/target.md", "# T\n")
    write(tmp_path, "docs/notes/doc.md", "[t](../tasks/target.md)\n")
    assert check_pointers(tmp_path) == []


def test_a_pointer_out_of_the_repository_fails(tmp_path):
    # ⛔ R18 pins siblings and R20 makes the extraction one-way, so a link that
    # leaves this checkout asserts something no checkout can guarantee.
    write(tmp_path, "doc.md", "[sibling](../elsewhere/README.md)\n")
    findings = check_pointers(tmp_path)
    assert len(findings) == 1
    assert findings[0].rule == RULE_POINTER
    assert "leaves this repository" in findings[0].message


def test_an_external_url_is_out_of_scope(tmp_path):
    write(
        tmp_path,
        "doc.md",
        "[a](https://example.invalid/x) [b](mailto:contact@example.com) [c](//host/x)\n",
    )
    assert check_pointers(tmp_path) == []
    assert scan(tmp_path).pointers == ()


def test_no_finding_carries_an_absolute_path(tmp_path):
    # R7: an absolute path in a build log carries the user's home directory.
    write(tmp_path, "deep/doc.md", "[x](missing.md)\n")
    for finding in check_pointers(tmp_path):
        assert not finding.path.startswith("/")
        assert str(tmp_path) not in finding.message


# --- anchors ---------------------------------------------------------------


def test_an_anchor_that_names_a_heading_resolves(tmp_path):
    write(tmp_path, "target.md", "# Title\n\n## A Second Heading\n")
    write(tmp_path, "doc.md", "[go](target.md#a-second-heading)\n")
    assert check_pointers(tmp_path) == []


def test_an_anchor_that_names_no_heading_fails(tmp_path):
    write(tmp_path, "target.md", "# Title\n\n## A Second Heading\n")
    write(tmp_path, "doc.md", "[go](target.md#no-such-heading)\n")
    findings = check_pointers(tmp_path)
    assert len(findings) == 1
    assert findings[0].rule == RULE_ANCHOR
    assert findings[0].line == 1
    assert "no-such-heading" in findings[0].message


def test_a_same_document_anchor_is_resolved_against_itself(tmp_path):
    write(tmp_path, "doc.md", "# Here\n\n[up](#here)\n\n[nowhere](#gone)\n")
    findings = check_pointers(tmp_path)
    assert [finding.line for finding in findings] == [5]
    assert findings[0].rule == RULE_ANCHOR


def test_an_anchor_on_a_non_markdown_target_fails(tmp_path):
    write(tmp_path, "data.json", "{}\n")
    write(tmp_path, "doc.md", "[d](data.json#field)\n")
    findings = check_pointers(tmp_path)
    assert len(findings) == 1
    assert findings[0].rule == RULE_ANCHOR
    assert "not a markdown document" in findings[0].message


def test_a_missing_file_is_reported_once_not_twice(tmp_path):
    # The file is the finding; the anchor cannot be checked and is not guessed.
    write(tmp_path, "doc.md", "[x](gone.md#section)\n")
    findings = check_pointers(tmp_path)
    assert len(findings) == 1
    assert findings[0].rule == RULE_POINTER


# --- slugs -----------------------------------------------------------------


def test_the_trees_one_real_anchor_slugs_to_its_heading():
    # ⛔ Re-measured: the task was scoped on "zero anchors in the tree" and the
    # tree now carries one. This is that exact pair, and it is the reason the
    # hyphen-run collapse below is a decision rather than an accident.
    heading = "The wave checks — ⛔ **SIX at open, and check 4 AGAIN at close**"
    assert slug(heading) == "the-wave-checks-six-at-open-and-check-4-again-at-close"


@pytest.mark.parametrize(
    ("heading", "expected"),
    [
        ("Simple Heading", "simple-heading"),
        ("**Bold** and `code`", "bold-and-code"),
        ("Trailing punctuation!", "trailing-punctuation"),
        ("A — B", "a-b"),
        ("  Padded  ", "padded"),
        ("R11's ceiling", "r11s-ceiling"),
        ("⛔ leading emoji", "leading-emoji"),
    ],
)
def test_slug_shapes(heading, expected):
    assert slug(heading) == expected


def test_headings_inside_a_fence_are_not_headings():
    # ⚠️ A shell transcript in a fence is full of `#` comments; reading those
    # as headings invents anchors no renderer offers.
    text = "# Real\n\n```bash\n# not a heading\n```\n"
    assert heading_slugs(text) == {"real"}


def test_a_duplicated_heading_takes_a_suffix():
    assert heading_slugs("# Same\n\n# Same\n\n# Same\n") == {"same", "same-1", "same-2"}


def test_a_closed_atx_heading_drops_its_closing_hashes():
    assert heading_slugs("## Closed ##\n") == {"closed"}


# --- the seam and the coverage channel -------------------------------------


def test_prose_lines_keeps_real_line_numbers():
    text = "a\n```\nb\n```\nc\n"
    assert prose_lines(text) == [(1, "a"), (5, "c")]


def test_strip_code_spans_preserves_columns():
    line = "x `abc` y"
    stripped = strip_code_spans(line)
    assert len(stripped) == len(line)
    assert stripped == "x       y"


def test_pointers_reports_the_line_it_was_written_on():
    text = "one\ntwo\n[three](a.md)\n"
    assert pointers("doc.md", text) == [Pointer("doc.md", 3, "a.md")]


def test_a_pointer_splits_its_target_into_path_and_anchor():
    assert Pointer("d.md", 1, "a/b.md#sec").path_part == "a/b.md"
    assert Pointer("d.md", 1, "a/b.md#sec").anchor == "sec"
    assert Pointer("d.md", 1, "#sec").path_part == ""
    assert Pointer("d.md", 1, "a/b.md").anchor == ""


def test_coverage_states_a_denominator(tmp_path):
    write(tmp_path, "target.md", "# T\n")
    write(tmp_path, "doc.md", "[t](target.md) and [t](target.md#t)\n")
    line = pointer_coverage(tmp_path)[0]
    assert "2 read in 2 markdown files" in line
    assert "1 carrying an anchor" in line
    assert "0 unresolved" in line


def test_coverage_and_findings_describe_the_same_walk(tmp_path):
    write(tmp_path, "doc.md", "[a](gone.md) `[b](also-gone.md)`\n")
    result = scan(tmp_path)
    assert len(result.pointers) == 1
    assert len(result.findings) == 1
    assert "1 unresolved" in pointer_coverage(tmp_path)[0]


def test_the_walk_is_the_shared_one_not_a_second(tmp_path):
    # Acceptance 6: no second file-walking helper. `markdown_files` is a
    # narrowing of `text_files`, so a tool-output directory is skipped here
    # because it is skipped there.
    write(tmp_path, "doc.md", "# D\n")
    write(tmp_path, "__pycache__/cached.md", "[x](gone.md)\n")
    assert [config.relative(p, tmp_path) for p in config.markdown_files(tmp_path)] == ["doc.md"]
    assert check_pointers(tmp_path) == []


# --- the tree itself -------------------------------------------------------


def test_the_repository_has_no_dangling_pointer():
    assert check_pointers(repository_root()) == []


def test_the_repository_walk_reads_something():
    # ⛔ Ruling 48: the assertion above passes on an empty walk. This is the
    # denominator that stops `0 = 0` from reading as coverage.
    result = scan(repository_root())
    assert result.files > 50
    assert len(result.pointers) > 20
