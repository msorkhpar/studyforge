"""R14's index: that it is ignored, that it is documented, and that both hold.

⛔ **This module asserts, it does not create.** The rule that ignores
`graphify-out/` in this repository is FND-01's and is already in `.gitignore`;
what lives here is the check that it stays true, in both directions. A test
that only proved the index is ignored would pass just as happily on a
`.gitignore` that ignores the whole tree.

⚠️ **The graph itself is deliberately not asserted.** It is local, rebuilt and
never committed (R14), so a test requiring `graphify-out/graph.json` to exist
would fail on every clean checkout and in FND-03's container — it would be
asserting one machine's state. What *is* checkable everywhere is the ignore
rule, the documented procedure, and — where a corpus repository happens to be
checked out beside this one — that the corpus's index is ignored the R3-safe
way. The last of those skips rather than fails when the sibling is absent.

⭐ **Why a corpus repository needs a different mechanism at all.** R3 forbids
editing a source repository's root ignore file — it is one of the three edits
never permitted, *however declared* — so `graphify-out/` cannot be added to it.
The ruled fix is a `.gitignore` containing `*` placed **inside** the generated
directory: it adds a file rather than editing one, and it ignores itself, so it
is recreated by the rebuild rather than committed. `docs/conventions/graphify.md`
carries the recipe; this module checks a real repository against it.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from tests.support import repository_root, run, tool_on_path

#: The generated index directory, in every repository this project touches.
INDEX_DIR = "graphify-out"

#: Paths that MUST be ignored in this repository. `.gitkeep` is in the list on
#: purpose: `graphify-out/` excludes the directory, and git cannot re-include a
#: file inside an excluded directory, so a `.gitkeep` there is ignored too. The
#: conventions document claimed the opposite until FND-02 checked it.
IGNORED_HERE = (
    "graphify-out/graph.json",
    "graphify-out/GRAPH_REPORT.md",
    "graphify-out/graph.html",
    "graphify-out/manifest.json",
    "graphify-out/cache/semantic/anything.json",
    "graphify-out/.gitkeep",
)

#: Paths that must NOT be ignored — the other direction, without which the
#: test above passes on a `.gitignore` that swallows the whole repository.
#: The last two are near-misses: a file of the same basename outside the
#: directory, and a path that merely starts with the directory's name.
TRACKED_HERE = (
    "src/studyforge/__init__.py",
    "docs/conventions/graphify.md",
    "tests/fixtures/depth1/corpus.json",
    "graph.json",
    "docs/graphify-out.md",
)

#: Corpus repositories that carry their own index. Siblings on disk until
#: FND-05 stands the parent workspace up (CLAUDE.md, R18).
SIBLING_CORPORA = ("Claude-senior-java-engineer", "CodeSignal")

#: Env override for a workspace that is not this repository's parent — a
#: worktree, a container mount, FND-05's parent once it exists.
WORKSPACE_ENV = "STUDYFORGE_WORKSPACE"

#: What the R3-safe ignore file contains, and nothing else.
CORPUS_IGNORE_BODY = "*\n"


def workspace_root() -> Path:
    """Where sibling repositories live."""
    override = os.environ.get(WORKSPACE_ENV)
    return Path(override).expanduser() if override else repository_root().parent


def git() -> str:
    tool = tool_on_path("git")
    assert tool is not None, "git is not installed; this test cannot answer"
    return tool


def is_ignored(path: str, cwd: Path) -> bool:
    """Whether git, run in `cwd`, would ignore `path`. The path need not exist.

    `git check-ignore -q` exits 0 when the path is ignored and 1 when it is
    not; anything else is git failing rather than answering, and is raised
    rather than read as a verdict.

    ⚠️ Duplicated from `tests/test_repository.py`, which had it first and which
    FND-02 was told not to touch. `tests/support.py`'s own rule says a block
    repeated between test files is extracted and imported — see the finding in
    `docs/tasks/handoffs/FND-02.md`; the extraction belongs to whoever owns
    both files next, not to a task told to leave one of them alone.
    """
    result = run([git(), "check-ignore", "-q", "--no-index", path], cwd=cwd)
    assert result.returncode in (0, 1), (
        f"git check-ignore failed on {path!r} in {cwd.name}: "
        f"{result.stdout + result.stderr}"
    )
    return result.returncode == 0


def conventions() -> str:
    """`docs/conventions/graphify.md`, which is FND-02's other deliverable."""
    return (repository_root() / "docs" / "conventions" / "graphify.md").read_text("utf-8")


# --- this repository's index ----------------------------------------------


def test_the_knowledge_index_is_ignored_here():
    # FND-01 owns the rule; FND-02 owns the assertion that it still holds.
    tracked = [path for path in IGNORED_HERE if not is_ignored(path, repository_root())]
    assert tracked == [], "the knowledge index is committable: " + ", ".join(tracked)


def test_the_ignore_is_scoped_to_the_index_directory():
    # ⚠️ Both directions, or the test above passes on a `.gitignore` that
    # ignores everything — which looks green and is strictly worse.
    swallowed = [path for path in TRACKED_HERE if is_ignored(path, repository_root())]
    assert swallowed == [], "these are no longer committable: " + ", ".join(swallowed)


def test_the_index_directory_is_not_committed():
    result = run([git(), "ls-files", INDEX_DIR], cwd=repository_root())
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "", (
        f"{INDEX_DIR} has tracked files; it is a local index, never merged (R14)"
    )


# --- a corpus repository's index, where one is checked out ------------------


@pytest.mark.parametrize("name", SIBLING_CORPORA)
def test_a_corpus_repository_ignores_its_index_without_editing_its_root(name):
    """⛔ The R3-safe mechanism, checked against a real repository.

    Skips rather than fails when the sibling is absent: this repository is
    checked out on its own far more often than beside a corpus, and a test
    that needs somebody else's clone is a test that fails for a reason that
    has nothing to do with the change being reviewed.
    """
    corpus = workspace_root() / name
    if not (corpus / ".git").exists():
        pytest.skip(
            f"{name} is not checked out beside this repository "
            f"(set {WORKSPACE_ENV} to point at the workspace root)"
        )
    if not (corpus / INDEX_DIR).is_dir():
        pytest.skip(f"{name} has no {INDEX_DIR}/ yet; build it first (see graphify.md)")

    inside = f"{INDEX_DIR}/graph.json"
    assert is_ignored(inside, corpus), (
        f"{name} would commit its knowledge index; it is local, never merged (R14)"
    )
    outside = "README.md"
    assert not is_ignored(outside, corpus), (
        f"{name}'s ignore rule is over-broad: it swallows {outside}"
    )


def test_the_corpus_ignore_file_is_the_ruled_one_where_it_exists():
    """The mechanism is `*` inside the directory — never an edit to the root.

    ⛔ Checked as bytes, because the two failure modes are both silent: a
    `!.gitignore` negation would make the file committable and therefore an
    addition to a repository this project may not add to, and a narrower
    pattern would leave part of the index visible to `git status`.
    """
    checked = 0
    for name in SIBLING_CORPORA:
        ignore = workspace_root() / name / INDEX_DIR / ".gitignore"
        if not ignore.is_file():
            continue
        checked += 1
        assert ignore.read_text("utf-8") == CORPUS_IGNORE_BODY, (
            f"{name}/{INDEX_DIR}/.gitignore is not the ruled one-line `*`"
        )
    if not checked:
        pytest.skip("no corpus repository with a built index is checked out")


# --- the documented procedure ----------------------------------------------


#: Every command the conventions document prescribes. ⚠️ These are the ones
#: FND-02 actually ran, and the list is deliberately not aspirational:
#: `graphify extract` was in an earlier draft of this test and is **not** here,
#: because it needs an LLM backend this project does not configure and was
#: never verified. A runbook entry nobody has run is a runbook entry that fails
#: for the first person who copies it.
DOCUMENTED_COMMANDS = (
    "graphify update",
    "--force",
    "graphify export html",
    "graphify query",
    "graphify path",
    "graphify explain",
)


def test_the_conventions_document_records_the_rebuild_commands():
    # The acceptance is that an agent can rebuild without asking anyone. Each
    # of these is a command somebody must be able to copy.
    text = conventions()
    missing = [command for command in DOCUMENTED_COMMANDS if command not in text]
    assert missing == [], "the rebuild runbook is missing: " + ", ".join(missing)


def test_the_conventions_document_records_the_rebuild_point():
    # ⛔ *When* matters as much as *how*: a graph rebuilt mid-task indexes a
    # state nobody will see again, and the wave-close rebuild is what keeps
    # this repository's own graph from describing an empty tree.
    text = conventions()
    assert "Never mid-task" in text
    assert "M0 close" in text


def test_the_conventions_document_records_the_corpus_ignore_recipe():
    # ⛔ R3's fix has to be *in the document*, or the next integrator edits a
    # root ignore file and breaks the one rule a corpus repository has.
    text = conventions()
    assert f"{INDEX_DIR}/.gitignore" in text
    assert "R3" in text
    assert "git check-ignore" in text


def test_the_conventions_document_corrects_the_gitkeep_claim():
    """⚠️ Asserts the correction is stated, not that the word is absent.

    The document said `graphify-out/` was "git-ignored except for a
    `.gitkeep`" until FND-02 ran `git check-ignore` on it: the rule excludes
    the *directory*, git cannot re-include a file inside an excluded
    directory, and neither this repository nor the extraction source tracks
    one. An earlier version of this test banned the token — which would have
    forbidden the document from explaining the correction at all, and is why
    the mistake could come back.
    """
    assert "there cannot be one" in conventions(), (
        "the conventions document no longer says why a committed .gitkeep is impossible"
    )
    # And the claim is still true of this repository, not just written down.
    assert is_ignored("graphify-out/.gitkeep", repository_root()), (
        "git no longer ignores graphify-out/.gitkeep; the document's correction is stale"
    )
