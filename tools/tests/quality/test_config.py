"""Mirror of `tools/quality/config.py` (R12)."""

from __future__ import annotations

import tomllib

from tests.support import git, init_repository, repository_root, run, tracked_files
from tools.quality import config, report


def test_the_size_exception_marker_is_the_ruled_literal():
    # ⛔ Fixed by ruling, case included: the review rubric greps for exactly
    # this token, so a marker that drifts passes here and fails there.
    assert config.SIZE_EXCEPTION_MARKER == "Size exception:"


def test_ceilings_are_the_documented_ones():
    # docs/conventions/module-structure.md states 400 and 600. If these move,
    # that document moved first — this assertion is the tripwire.
    assert config.SOURCE_LINE_CEILING == 400
    assert config.TEST_LINE_CEILING == 600


def test_ruff_line_length_agrees_with_the_always_on_checker():
    # ⛔ Two tools disagreeing about the same file is worse than one tool.
    # `pyproject.toml`'s `[tool.ruff] line-length` and `config.LINE_LENGTH`
    # are the same number or this fails.
    pyproject = tomllib.loads((repository_root() / "pyproject.toml").read_text("utf-8"))
    assert pyproject["tool"]["ruff"]["line-length"] == config.LINE_LENGTH


def test_test_files_get_the_test_ceiling():
    assert config.ceiling_for("tests/studyforge/test_init.py") == config.TEST_LINE_CEILING
    assert config.ceiling_for("src/studyforge/serve/app.py") == config.SOURCE_LINE_CEILING
    assert config.ceiling_for("tools/quality/size.py") == config.SOURCE_LINE_CEILING
    # The tooling's tests live beside the tooling and are still tests.
    assert config.ceiling_for("tools/tests/quality/test_size.py") == config.TEST_LINE_CEILING


def test_a_path_merely_containing_tests_is_not_a_test_file():
    # `is_test_file` matches a root, not a substring: a source module named
    # `contests.py` must not inherit the looser ceiling.
    assert not config.is_test_file("src/studyforge/contests.py")
    assert not config.is_test_file("testsuite/thing.py")


def test_fixtures_are_never_read():
    # FND-04's fixtures are deliberately shaped wrong — an invalid corpus is
    # the point of half of them — so holding them to the repository's style
    # would be a category error.
    assert config.is_excluded("tests/fixtures/depth1/corpus.json")
    assert config.is_excluded("src/studyforge/__pycache__/x.py")
    assert not config.is_excluded("tests/studyforge/test_init.py")


def test_relative_is_repo_relative_with_forward_slashes():
    root = repository_root()
    assert config.relative(root / "tools" / "quality" / "config.py", root) == (
        "tools/quality/config.py"
    )


def test_python_files_finds_the_tree_and_is_sorted():
    files = config.python_files(repository_root())
    names = [config.relative(path, repository_root()) for path in files]
    assert "src/studyforge/__init__.py" in names
    assert "tools/quality/config.py" in names
    assert "tests/support.py" in names
    assert "tools/tests/quality/test_config.py" in names  # it checks itself
    assert names == sorted(names)
    assert not [name for name in names if "__pycache__" in name]


# --- what "in the repository" means (FND-06) -------------------------------
#
# ⚠️ This is the second time a gate's *scope* rather than its patterns has been
# the defect, so the scope is pinned by tests rather than by a docstring.


def sweep(root):
    """The repo-relative paths `text_files` would read under `root`."""
    return sorted(config.relative(path, root) for path in config.text_files(root))


def make(root, relative: str, text: str = "x\n"):
    """Write a file at `relative` under `root`, creating parents."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_a_git_ignored_path_is_not_the_repository_s(tmp_path):
    # ⛔ The defect this fixes. `.idea/workspace.xml` legitimately carries the
    # paths of whoever has the project open; it is ignored, it has not entered
    # the repository and it never will. Gating on it made the floor
    # unconditionally red for anyone with an IDE running.
    init_repository(tmp_path)
    make(tmp_path, ".gitignore", ".idea/\ngraphify-out/\n")
    make(tmp_path, ".idea/workspace.xml")
    make(tmp_path, "graphify-out/GRAPH_REPORT.md")
    make(tmp_path, "docs/notes.md")
    assert sweep(tmp_path) == [".gitignore", "docs/notes.md"]


def test_an_untracked_new_file_is_still_swept(tmp_path):
    # ⭐ The case that separates "ignored" from "untracked", and the reason the
    # rule is the first and not the second. A file you have just written and
    # not yet added is exactly what a gate on personal data *entering* the
    # repository must catch — before it enters, not in the commit that carries
    # it. `git ls-files` would miss it.
    init_repository(tmp_path)
    make(tmp_path, ".gitignore", ".idea/\n")
    make(tmp_path, "docs/brand-new-and-unadded.md")
    assert "docs/brand-new-and-unadded.md" in sweep(tmp_path)


def test_a_re_included_fixture_path_is_swept(tmp_path):
    # ⚠️ This repository's own ignore file ignores `site.json` and
    # `*.unit.html` everywhere and then re-includes `tests/fixtures/**`, so a
    # golden fixture stays trackable. A sweep that stopped at the first
    # matching pattern would skip exactly the tree the personal-data registry
    # is about.
    init_repository(tmp_path)
    make(tmp_path, ".gitignore", "site.json\n*.unit.html\n!tests/fixtures/**\n")
    make(tmp_path, "site.json")
    make(tmp_path, "tests/fixtures/depth1/site.json")
    make(tmp_path, "tests/fixtures/depth1/page.unit.html")
    assert sweep(tmp_path) == [
        ".gitignore",
        "tests/fixtures/depth1/page.unit.html",
        "tests/fixtures/depth1/site.json",
    ]


def test_a_tree_that_is_not_a_repository_is_swept_whole(tmp_path):
    # ⚠️ Fails OPEN. An unanswerable question means everything is read, which
    # reports too much rather than too little; the other direction would
    # silently stop checking.
    make(tmp_path, "docs/notes.md")
    assert sweep(tmp_path) == ["docs/notes.md"]
    assert config.ignored_paths(tmp_path, [tmp_path / "docs" / "notes.md"]) == set()


def test_the_git_directory_is_never_a_candidate(tmp_path):
    # ⛔ `.git` is not "ignored" as far as git is concerned — it is simply not
    # part of the worktree — so the tool-output pre-filter is doing real work
    # rather than duplicating the ignore call.
    init_repository(tmp_path)
    make(tmp_path, "docs/notes.md")
    assert not [name for name in sweep(tmp_path) if name.startswith(".git/")]
    assert config.is_tool_output(".git/COMMIT_EDITMSG")


def test_the_real_repository_reads_its_own_documents_and_fixtures():
    swept = sweep(repository_root())
    assert "docs/conventions/review-rubric.md" in swept
    assert "tests/fixtures/invalid/personal-data/VIOLATION.md" in swept
    assert "pyproject.toml" in swept
    assert not [name for name in swept if name.startswith(".idea/")]


def track(root, *paths: str):
    """`git add` those paths in `root`, and refuse a silent failure."""
    result = run([git(), "add", "--", *paths], cwd=root)
    assert result.returncode == 0, result.stdout + result.stderr


def test_markdown_files_is_a_narrowing_of_the_shared_walk(tmp_path):
    # ⭐ FND-08 acceptance 6: no second file-walking helper. The narrowing is
    # one `suffix` test, so exclusions and the sort order are inherited.
    init_repository(tmp_path)
    make(tmp_path, ".gitignore", "graphify-out/\n")
    make(tmp_path, "docs/notes.md")
    make(tmp_path, "docs/data.json", "{}\n")
    make(tmp_path, "graphify-out/GRAPH_REPORT.md")
    make(tmp_path, "__pycache__/cached.md")
    track(tmp_path, ".gitignore", "docs/notes.md", "docs/data.json", "__pycache__/cached.md")
    found = [config.relative(path, tmp_path) for path in config.markdown_files(tmp_path)]
    assert found == ["docs/notes.md"]
    assert set(found) <= set(sweep(tmp_path))


def test_markdown_files_reads_the_fixture_tree_by_decision(tmp_path):
    # ⚠️ `tests/fixtures/` is in `EXCLUDED_DIRS`, so a `python_files`-shaped
    # walk would not see it — and this walk is `text_files`-shaped, where
    # `EXCLUDED_DIRS` never applied. The decision is recorded rather than
    # inherited: a fixture may be shaped wrong, but its README is prose.
    init_repository(tmp_path)
    make(tmp_path, "tests/fixtures/README.md")
    track(tmp_path, "tests/fixtures/README.md")
    assert config.is_excluded("tests/fixtures/README.md")
    found = [config.relative(path, tmp_path) for path in config.markdown_files(tmp_path)]
    assert found == ["tests/fixtures/README.md"]


# --- W148: the document population is the INDEX; the R7 sweep is not --------
#
# ⛔ The hard constraint this row was written under, pinned by tests rather
# than by a docstring: the narrowing is at `markdown_files` and NEVER at
# `text_files`, because `text_files` is the personal-data sweep's population
# (`personal_data/shapes.py` and `personal_data/identity.py` both walk it) and a
# file written and not yet added is exactly what that gate must catch.


def test_the_narrowing_is_NOT_in_the_personal_data_sweeps_population(tmp_path):
    # ⛔ THE TEST THAT MATTERS MOST IN THIS ROW. If this ever fails, an
    # untracked file has left the R7 gate and the floor has gone quiet by going
    # blind — which `rows/W148.md` names as what the row must not become.
    init_repository(tmp_path)
    make(tmp_path, "docs/tracked.md")
    track(tmp_path, "docs/tracked.md")
    make(tmp_path, "docs/brand-new-and-unadded.md")
    make(tmp_path, "notes-and-unadded.txt")
    swept = sweep(tmp_path)
    assert "docs/brand-new-and-unadded.md" in swept
    assert "notes-and-unadded.txt" in swept
    # ⭐ And the same file is OUT of the document population, in one assertion,
    # so the two walks are read apart rather than assumed to differ.
    documents = [config.relative(path, tmp_path) for path in config.markdown_files(tmp_path)]
    assert documents == ["docs/tracked.md"]


def test_the_population_says_which_walk_produced_it(tmp_path):
    init_repository(tmp_path)
    make(tmp_path, "docs/tracked.md")
    track(tmp_path, "docs/tracked.md")
    assert config.markdown_population(tmp_path).walk == report.TRACKED_WALK


def test_a_tree_git_cannot_answer_for_falls_back_and_SAYS_so(tmp_path):
    # ⛔ Ruling 216's THIRD answer. Not a silent fall-through and not a hard
    # failure: `tracked_paths` returns None, the walk is named `disk`, and
    # `WALK_CAVEAT` carries what that costs a reader.
    make(tmp_path, "docs/notes.md")
    assert config.tracked_paths(tmp_path) is None
    population = config.markdown_population(tmp_path)
    assert population.walk == report.DISK_WALK
    assert [config.relative(path, tmp_path) for path in population.paths] == ["docs/notes.md"]
    assert report.WALK_CAVEAT[report.DISK_WALK] != ""
    assert report.WALK_CAVEAT[report.TRACKED_WALK] == ""


def test_tracked_paths_reads_the_INDEX_and_not_the_disk(tmp_path):
    # ⚠️ `None` is never an empty set, and an empty index is never `None`:
    # a repository that genuinely tracks nothing ANSWERS, with nothing.
    init_repository(tmp_path)
    assert config.tracked_paths(tmp_path) == set()
    make(tmp_path, "one.md")
    assert config.tracked_paths(tmp_path) == set()
    track(tmp_path, "one.md")
    assert config.tracked_paths(tmp_path) == {tmp_path / "one.md"}


def test_the_repositorys_own_document_population_agrees_with_git_ls_files():
    # ⭐ `W148` clause 1: the figure the floor prints and `git ls-files '*.md'`
    # are the same number, so a reading is reproducible from any checkout.
    root = repository_root()
    population = config.markdown_population(root)
    assert population.walk == report.TRACKED_WALK
    assert len(population.paths) == len(tracked_files(("*.md",)))
