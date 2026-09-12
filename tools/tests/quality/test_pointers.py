"""Mirror of `tools/quality/pointers.py` (R12) — the CHECK, not the parser.

⛔ **The parser's own tests moved to `test_markdown.py` with the parser**
(`W148`); what is asserted here is everything that needs a DISK: what resolves,
what does not, which documents are read at all, and what the coverage line
says about how it found them.

⚠️ **The two rows this module carries are asserted in a REAL git repository and
not in a bare `tmp_path`**, deliberately. ⛔ `W148`'s clause 3: *"a test that
would pass with the disk walk still in place is not the test"* — and a
`tmp_path` under no repository is exactly where the disk walk still runs, by
design (Ruling 216's third answer). ⭐ So every clause of `W148` and `W35` below
takes `init_repository` and `git add`, and the `tmp_path` tests that remain are
asserting the disk-walk fallback on purpose.
"""

from __future__ import annotations

from tests.support import git, init_repository, repository_root, run
from tools.quality import config
from tools.quality.pointers import (
    RULE_ANCHOR,
    RULE_POINTER,
    check_pointers,
    pointer_coverage,
    scan,
)
from tools.quality.report import DISK_WALK, TRACKED_WALK


def write(tmp_path, name: str, text: str):
    """Write a document into a temporary tree and return its path."""
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def add(root, *paths: str):
    """`git add` those paths in `root`, and refuse a silent failure."""
    result = run([git(), "add", "--", *paths], cwd=root)
    assert result.returncode == 0, result.stdout + result.stderr


# --- the parser reaching the check -----------------------------------------


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


# --- W148: the document population is what git TRACKS ----------------------


def repository(tmp_path):
    """A throwaway repository carrying two TRACKED documents and nothing else."""
    init_repository(tmp_path)
    write(tmp_path, "docs/target.md", "# Target\n")
    write(tmp_path, "docs/tracked.md", "[t](target.md)\n")
    add(tmp_path, "docs/target.md", "docs/tracked.md")
    return tmp_path


def test_an_untracked_document_is_not_counted_as_repository_state(tmp_path):
    # ⛔ THE SYMPTOM `W148` WAS MINTED OVER, in miniature. One untracked
    # markdown file at a main checkout's root made the floor read `458 markdown
    # files` there and `457` in every linked worktree — same content, ZERO
    # extra pointers, so the denominator moved and the numerator did not, and a
    # reader comparing the two would have concluded both were invariant.
    root = repository(tmp_path)
    before = scan(root)
    write(root, "UNTRACKED-AT-THE-ROOT.md", "# Untracked\n\n[t](docs/target.md)\n")
    after = scan(root)
    assert (after.files, len(after.pointers)) == (before.files, len(before.pointers))
    assert after.files == 2
    assert after.walk == TRACKED_WALK


def test_the_disk_walk_reads_that_same_untracked_file_and_would_have_passed(tmp_path):
    # ⚠️ `W148` clause 3 run NEGATIVELY: *"a test that would pass with the disk
    # walk still in place is not the test"*. ⛔ The identical three files in a
    # tree git cannot answer for give a population of THREE, which is the
    # figure the assertion above would read if the narrowing were not there.
    write(tmp_path, "docs/target.md", "# Target\n")
    write(tmp_path, "docs/tracked.md", "[t](target.md)\n")
    write(tmp_path, "UNTRACKED-AT-THE-ROOT.md", "# Untracked\n\n[t](docs/target.md)\n")
    result = scan(tmp_path)
    assert result.files == 3
    assert result.walk == DISK_WALK


def test_an_untracked_documents_dangling_pointer_is_not_this_floors_finding(tmp_path):
    # ⭐ The COST of the narrowing, asserted rather than discovered later: a
    # document that is not repository state is not read here, so its broken
    # link earns nothing. ⛔ It is still swept for PERSONAL DATA — that
    # population is `config.text_files`, which `W148` deliberately does not
    # touch, and `test_config.py` holds the assertion that it still sees it.
    root = repository(tmp_path)
    write(root, "scratch.md", "[gone](nowhere.md)\n")
    assert check_pointers(root) == []


def test_the_figure_names_the_walk_that_produced_it(tmp_path):
    root = repository(tmp_path)
    line = pointer_coverage(root)[0]
    assert "(tracked walk)" in line
    assert "not reproducible from another checkout" not in line


def test_a_tree_git_cannot_answer_for_says_so_and_is_not_a_failure(tmp_path):
    # ⛔ Ruling 216's THIRD answer, and `W148` clause 4: neither a silent
    # fall-through to the disk nor a hard failure — the figure SAYS which walk
    # produced it, and what that costs the reader.
    write(tmp_path, "doc.md", "# D\n")
    line = pointer_coverage(tmp_path)[0]
    assert "(disk walk)" in line
    assert "not reproducible from another checkout" in line
    assert check_pointers(tmp_path) == []


def test_the_repositorys_own_figure_is_taken_over_the_tracked_walk():
    # ⛔ The property that makes a floor reading quotable between two offices
    # (Ruling 277): this figure is the same from the main checkout and from
    # every linked worktree, and the line says which walk produced it.
    assert scan(repository_root()).walk == TRACKED_WALK
    assert "(tracked walk)" in pointer_coverage(repository_root())[0]


# --- W35: an ignored target does not resolve (Ruling 80) --------------------


def ignoring_repository(tmp_path):
    """A repository that ignores `graphify-out/` and links into it from a tracked doc."""
    root = repository(tmp_path)
    write(root, ".gitignore", "graphify-out/\n")
    add(root, ".gitignore")
    write(root, "docs/tracked.md", "[the index](../graphify-out/GRAPH_REPORT.md)\n")
    return root


def test_a_pointer_into_a_git_ignored_tree_is_a_finding(tmp_path):
    # ⛔ The ASYMMETRY `W35` names: this walk already honoured `.gitignore` when
    # choosing what to READ, and now honours it when deciding what RESOLVES.
    root = ignoring_repository(tmp_path)
    write(root, "graphify-out/GRAPH_REPORT.md", "# Built on this machine\n")
    findings = check_pointers(root)
    assert len(findings) == 1
    assert findings[0].rule == RULE_POINTER
    assert findings[0].line == 1
    assert "git IGNORES" in findings[0].message


def test_the_ignored_target_earns_the_same_finding_whether_or_not_it_was_built(tmp_path):
    # ⛔ Ruling 80's whole subject, in both directions: the machine that
    # generated the artifact and a fresh clone that did not must reach the same
    # verdict — and the same MESSAGE, which is why the ignore question is asked
    # BEFORE existence rather than after it.
    root = ignoring_repository(tmp_path)
    absent = check_pointers(root)
    write(root, "graphify-out/GRAPH_REPORT.md", "# Built on this machine\n")
    built = check_pointers(root)
    assert len(absent) == len(built) == 1
    assert absent[0] == built[0]
    assert "git IGNORES" in built[0].message


def test_an_untracked_but_not_ignored_target_still_resolves(tmp_path):
    # ⚠️ `W35` is about the IGNORE declaration and NOT about the index, and the
    # two are different questions on purpose. A file written and not yet added
    # is not ignored, so a link to it resolves exactly as it did before.
    root = repository(tmp_path)
    write(root, "docs/unadded.md", "# Not added yet\n")
    write(root, "docs/tracked.md", "[u](unadded.md)\n")
    assert check_pointers(root) == []


def test_a_tree_git_cannot_answer_for_reports_no_ignored_target(tmp_path):
    # ⚠️ `config.ignored_paths` fails OPEN by design: an unanswerable question
    # means nothing is ignored, which reports too little here rather than
    # inventing a finding no reader could act on. ⛔ The reading still says so.
    write(tmp_path, "target.md", "# T\n")
    write(tmp_path, "doc.md", "[t](target.md)\n")
    assert check_pointers(tmp_path) == []
    assert "(disk walk)" in pointer_coverage(tmp_path)[0]


def test_the_repository_has_no_pointer_into_an_ignored_tree():
    # ⛔ Ruling 48: the assertion is `0`, so the denominator is quoted with it.
    # MEASURED at `bec9d5c`, role `wt/dev2`: 0 ignored targets among 308
    # distinct existing targets reached by 1528 pointers.
    result = scan(repository_root())
    assert [finding for finding in result.findings if "git IGNORES" in finding.message] == []
    assert len(result.pointers) > 20
