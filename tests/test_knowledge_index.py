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
import re
from pathlib import Path

import pytest

from tests.support import git, is_ignored, repository_root, run
from tools.tests.workspace import support as workspace_support

# ⛔ **The SHIPPED resolver, imported rather than re-derived** (`W127`). This
# module used to answer *"where do the sibling components live?"* with its own
# `repository_root().parent` — a **second implementation of a rule this
# repository already ships**, which is the duplication `review-rubric.md` §1a
# says this project has refused five times. ⚠️ Imported from `__main__` because
# that is where the rule and its explanation live, and where
# `tools/tests/workspace/test_main.py` already imports it from: a **third** home
# would be this defect again, one directory over.
from tools.workspace.__main__ import workspace_root as shipped_workspace_root

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

#: Env override for a workspace the shipped resolver cannot reach — a container
#: mount, FND-05's parent once it exists, or a synthetic tree in a plant.
#: ⛔ **Not for a worktree any more**: `W127` measured that the shipped resolver
#: answers correctly from one, and the override existed to paper over the
#: re-derivation this module no longer carries.
WORKSPACE_ENV = "STUDYFORGE_WORKSPACE"

#: What the R3-safe ignore file contains, and nothing else.
CORPUS_IGNORE_BODY = "*\n"


def workspace_root() -> Path:
    """Where sibling repositories live, as `tools.workspace` already computes it.

    ⛔ **The derivation is NOT repeated here** (`W127`). This module answered
    `repository_root().parent`, which is a **worktree's** parent — and agents
    work in worktrees, so the corpus checks below skipped on a tree that had
    both corpora sitting right beside it. ⭐ The shipped resolver reads
    `git rev-parse --git-common-dir`, which names the **main** checkout.

    ⚠️ The override still wins, because it is an instruction rather than a
    derivation: it is how a caller points the checks at a tree the resolver
    cannot see from where it is running.
    """
    override = os.environ.get(WORKSPACE_ENV)
    if override:
        return Path(override).expanduser()
    return shipped_workspace_root(repository_root())


def conventions() -> str:
    """`docs/conventions/graphify.md`, which is FND-02's other deliverable."""
    return convention("graphify.md")


def convention(name: str) -> str:
    """Any document in `docs/conventions/`, read as text."""
    return (repository_root() / "docs" / "conventions" / name).read_text("utf-8")


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


# --- `W127`: the resolver is the shipped one, and these checks can still fail --
#
# ⛔ **Why every check in this block is SYNTHETIC.** R3 forbids writing into a
# source repository, so a plant that damaged a real sibling would be the
# violation these checks exist to catch. ⭐ And synthetic means they RUN in the
# pinned image, where the real siblings are absent — a plant that skipped in the
# one authoritative environment would prove nothing there.


def synthetic_corpus(root: Path, name: str, ignore_body: str | None) -> Path:
    """A git repository named like a corpus, with an index of the given shape.

    `ignore_body` of `None` means no `graphify-out/` at all; otherwise the
    directory is created and the body is written verbatim — including a wrong
    one, which is the point.
    """
    corpus = root / name
    workspace_support.repository(corpus)
    if ignore_body is not None:
        (corpus / INDEX_DIR).mkdir()
        (corpus / INDEX_DIR / ".gitignore").write_text(ignore_body, encoding="utf-8")
    return corpus


def test_the_workspace_is_the_main_checkouts_parent_even_from_a_worktree(tmp_path, monkeypatch):
    """⛔ The defect `W127` closes, asserted so it cannot come back.

    This module re-derived `repository_root().parent`. ⚠️ A `git worktree` lives
    **outside** the repository it belongs to, so that is the worktree's own
    parent — and agents work in worktrees, which is why the corpus checks above
    skipped on a tree that had both corpora right beside it. ⭐ Asserted against
    a real synthetic worktree rather than against this machine's, so it is
    evidence in the pinned image too.
    """
    root, main_checkout = workspace_support.workspace(tmp_path / "w")
    elsewhere = tmp_path / "far" / "away"
    elsewhere.parent.mkdir(parents=True)
    workspace_support.run(main_checkout, "worktree", "add", "-q", "-b", "side", str(elsewhere))

    monkeypatch.delenv(WORKSPACE_ENV, raising=False)
    monkeypatch.setattr(f"{__name__}.repository_root", lambda: elsewhere)

    assert workspace_root() == root, "the workspace is the MAIN checkout's parent"
    assert workspace_root() != elsewhere.parent, (
        "this is the answer the re-derived resolver gave, and it holds no component"
    )


def test_a_corpus_check_skips_and_names_the_corpus_when_it_is_genuinely_absent(
    tmp_path, monkeypatch
):
    """⭐ The skip branch stays LIVE, which is what keeps the pinned image honest.

    ⛔ The hazard of `W127` is the inverse of the defect it fixes: three skips
    that become three checks which cannot fail. This asserts the first half —
    an absent corpus still **skips**, naming itself, rather than passing.
    """
    monkeypatch.setenv(WORKSPACE_ENV, str(tmp_path / "empty"))
    (tmp_path / "empty").mkdir()
    with pytest.raises(pytest.skip.Exception) as raised:
        test_a_corpus_repository_ignores_its_index_without_editing_its_root(SIBLING_CORPORA[0])
    assert SIBLING_CORPORA[0] in str(raised.value)
    assert "is not checked out" in str(raised.value)


def test_a_corpus_check_fails_on_an_unignored_index_rather_than_passing(tmp_path, monkeypatch):
    """⛔ The second half: the assertion is REACHABLE and it can go red.

    A corpus carrying `graphify-out/` with no ignore file would commit its
    index, and that is exactly the silent failure R14 is about.
    """
    synthetic_corpus(tmp_path, SIBLING_CORPORA[0], ignore_body=None)
    (tmp_path / SIBLING_CORPORA[0] / INDEX_DIR).mkdir()
    monkeypatch.setenv(WORKSPACE_ENV, str(tmp_path))
    with pytest.raises(AssertionError, match="would commit its knowledge index"):
        test_a_corpus_repository_ignores_its_index_without_editing_its_root(SIBLING_CORPORA[0])


def test_the_ignore_body_check_fails_on_a_negation_rather_than_passing(tmp_path, monkeypatch):
    """⛔ The `!.gitignore` negation named in the check's own docstring, planted.

    ⚠️ Adversarial to the **search term**: the file exists and is found, so the
    `continue` branch is not what answers — the byte comparison is.
    """
    synthetic_corpus(tmp_path, SIBLING_CORPORA[0], ignore_body="*\n!.gitignore\n")
    monkeypatch.setenv(WORKSPACE_ENV, str(tmp_path))
    with pytest.raises(AssertionError, match="not the ruled one-line"):
        test_the_corpus_ignore_file_is_the_ruled_one_where_it_exists()


def test_both_corpus_checks_pass_on_a_correctly_ignored_index(tmp_path, monkeypatch):
    """⭐ The third state, without which the two plants above prove only half.

    A check that fails on everything is as useless as one that passes on
    everything, so the ruled body is asserted to be **accepted**.
    """
    synthetic_corpus(tmp_path, SIBLING_CORPORA[0], ignore_body=CORPUS_IGNORE_BODY)
    synthetic_corpus(tmp_path, SIBLING_CORPORA[1], ignore_body=CORPUS_IGNORE_BODY)
    monkeypatch.setenv(WORKSPACE_ENV, str(tmp_path))
    for name in SIBLING_CORPORA:
        test_a_corpus_repository_ignores_its_index_without_editing_its_root(name)
    test_the_corpus_ignore_file_is_the_ruled_one_where_it_exists()


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
    # ⭐ FND-07's three, and the first of them is what makes R14 affordable:
    # `explain` and `path` answer from a worktree with no index of its own.
    "--graph",
    "python3 -m tools.knowledge census",
    "python3 -m tools.knowledge bridge",
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


#: ⛔ Every `graphify` invocation in the document that carries `--graph` — the
#: copy-paste block FND-07 added. A reader pastes these, so they have to run.
WORKTREE_INVOCATIONS = re.compile(r"^graphify (explain|path) (.+?) --graph", re.M)

#: What an unambiguous argument looks like: a node id, which is lowercase,
#: alphanumeric and underscored. ⛔ A **label** is what does not work, and the
#: two commands fail differently — `explain` refuses, `path` guesses.
NODE_ID = re.compile(r'^"[a-z0-9_]+"$')


def test_the_conventions_document_carries_the_worktree_invocation():
    # ⭐ FND-07 item 3. Measured 2026-09-09: **33 worktrees, 2 with a graph** —
    # the per-worktree rebuild was never payable, and an unaffordable rule is
    # one that gets skipped, which is what happened to R14 for a milestone.
    text = conventions()
    assert "--graph" in text
    assert "query" in text and "does not" in text, (
        "the document must say which command still needs a local index"
    )


def test_every_worktree_invocation_is_given_a_node_id_and_not_a_label():
    # ⛔ **The first version of this block did not run.** It passed labels, and
    # `R7 — No personal data…` matches two nodes: `explain` refused and `path`
    # picked the higher-scoring one — the fixture, which has no bridge edges —
    # then printed `No directed path found`, which reads as a fact and is not.
    # ⚠️ The warning prints *above* the answer, so a reader who scrolls to the
    # result never sees it.
    #
    # ⭐ A runbook entry nobody has run is a runbook entry that fails for the
    # first person who copies it, and this document already says so about
    # `graphify extract`. This is that rule, asserted.
    found = WORKTREE_INVOCATIONS.findall(conventions())
    assert found, "the worktree invocation block is gone"
    labelled = [
        f"{command} {argument}"
        for command, arguments in found
        for argument in arguments.split(" ")
        if argument.startswith('"') and not NODE_ID.match(argument)
    ]
    assert labelled == [], (
        f"these pass a label where a node id is needed, and a label can be ambiguous: {labelled}"
    )


def test_the_document_says_how_path_fails_on_an_ambiguous_label():
    # ⚠️ Naming `explain`'s behaviour is not enough, and that is the whole of
    # the correction: `path` does not behave like `explain`. It warns and then
    # answers anyway, so the caveat has to name the command that is dangerous.
    text = conventions()
    ambiguity = text[text.index("Ambiguity:") :]
    assert "`explain` refuses" in ambiguity
    assert "`path` resolves it silently" in ambiguity
    assert "warning is *above* the answer" in ambiguity


def test_the_conventions_document_carries_the_census_command_itself():
    # ⛔ The circular reference this closes: this document said the census was
    # in `handoffs/FND-02.md`, that handoff said it was in this document, and
    # **neither one had it**. A reference is not a command.
    text = conventions()
    assert "python3 -m tools.knowledge census" in text
    assert "python3 -m tools.knowledge bridge" in text
    assert "cross a file boundary" in text, (
        "the document must say what the census counts, or the number means nothing"
    )


def test_the_conventions_document_says_a_rebuild_without_a_bridge_is_incomplete():
    # ⛔ The third state: present, current and unbridged. Every green light on,
    # and the one question that matters returns silence.
    text = conventions()
    assert "unbridged" in text
    assert "one operation with two commands" in text


# --- Ruling 96: the index line, and what the rebuild step became ------------


def test_the_rubric_requires_an_index_line_in_every_review():
    # ⛔ Ruling 96's whole mechanism. The exit code went; what replaces it is a
    # line the reviewer must quote, and a requirement that lives only in a
    # round's handoff is one that binds whoever read that round.
    text = convention("review-rubric.md")
    assert "INDEX LINE" in text
    assert "python3 -m tools.quality | grep '^knowledge index: '" in text


def test_the_rubric_names_all_four_states_of_the_index_line():
    # ⚠️ A vocabulary with a silent member is one a reader fills in from
    # memory, which is why the floor prints `fresh` too.
    text = convention("review-rubric.md")
    for state in (
        "knowledge index: fresh",
        "knowledge index: stale",
        "knowledge index: unverifiable",
        "knowledge index: none",
    ):
        assert state in text, f"the rubric's index line does not show `{state}`"


def test_the_rubric_says_stale_does_not_block_approve_and_is_not_a_licence():
    # ⛔ Both halves, because either alone is the wrong document. Ruling 80
    # forbids the exit code; the sentence it replaced must still be readable.
    text = convention("review-rubric.md")
    assert "does not block APPROVE" in text
    assert "not a licence" in text


def test_ruling_89_is_narrowed_to_a_courtesy_and_keeps_no_pass_condition():
    # ⛔ `W39` narrows rather than deletes: the next agent still inherits the
    # index, and the step loses only the power to invalidate a number.
    text = convention("review-rubric.md")
    assert "Ruling 89, NARROWED by `W39`" in text
    assert "Pass condition: none" in text
    assert "graphify update . && python3 -m tools.knowledge bridge" in text


def test_the_interim_rebuild_step_is_gone_from_the_delivery_flow():
    # ⛔ The expiry was met rather than lapsed, so the word that named it must
    # not survive: an INTERIM step nobody deletes is the mechanism it refused
    # to be.
    text = convention("delivery-flow.md")
    assert "### ⛔ INTERIM" not in text
    assert "Whoever merges to a release branch runs this" not in text
    assert "is DELETED by `W39`" in text


def test_the_delivery_flow_no_longer_calls_a_stale_index_a_failure():
    # ⚠️ The document listed staleness beside unbridged as a floor failure.
    # After Ruling 96 only one of the two still is.
    text = convention("delivery-flow.md")
    assert "it is a **notice**" in text
    assert "current but unbridged* one is still a finding" in text


def test_the_rubrics_grep_matches_what_the_floor_actually_prints():
    # ⛔ The loop closed between the document and the tool. A rubric that tells
    # a reviewer to grep for a string the floor no longer prints produces an
    # empty index line, and an empty line reads exactly like a clean one.
    from tools.quality.knowledge_index import PREFIX

    assert f"grep '^{PREFIX}'" in convention("review-rubric.md")
