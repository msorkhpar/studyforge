"""Mirror of `src/studyforge/validate/source/classification.py` (R12).

⛔ **Silence is the double ingest.** Every assertion here is about a file the
manifest did not account for, or accounted for twice, or that the repository
itself calls generated output — and about the one degradation this check is
allowed: saying out loud that it could not read the declaration.

⚠️ The imports come through the package surface, not through the submodule,
except where a test reaches for a private name or monkeypatches one. Those two
name `classification` directly because that is the module they are about.
"""

import json

import pytest

from studyforge.corpus.placement import ARCHIVE_DIRNAME as ARCHIVE_DIR
from studyforge.validate import validate
from studyforge.validate.source import (
    RULE_ARCHIVE_STRAY,
    RULE_CONTESTED,
    RULE_NESTED_REPOSITORY,
    RULE_UNCLASSIFIED,
    SKIP_DIRS,
    classification,
    source_files,
)
from tests.studyforge.validate import corpora
from tests.support import git, init_repository, run


def declared_output(root, *lines):
    """Make `root` a repository that declares `lines` as generated output."""
    init_repository(root)
    (root / ".gitignore").write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")


def track(root, where):
    """Put `where` in the repository's index, so git's ignore rules yield to it."""
    result = run([git(), "add", "--force", where], cwd=root)
    assert result.returncode == 0, result.stdout + result.stderr


def scanned(root):
    """The scan's files as posix strings relative to `root`."""
    return {path.relative_to(root).as_posix() for path in source_files(root).files}


# --------------------------------------------------------------------------
# the classification check
# --------------------------------------------------------------------------


def test_a_file_the_manifest_classifies_as_neither_is_refused(tmp_path):
    # ⛔ **Silence is the double ingest.** One corpus ships per-unit files
    # beside whole-series aggregates that are digest-identical concatenations
    # of them, so a glob sweeping both reads every unit twice and nothing
    # complains.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "src" / "strays.txt").write_text("unaccounted for\n", encoding="utf-8")
    report = validate(root)
    assert "unclassified" in report.rules
    assert "src/strays.txt" in report.findings[0].where


# --------------------------------------------------------------------------
# ⛔ the third state — never material, rather than withheld
# --------------------------------------------------------------------------

#: A reason long enough to be one, written where a corpus would write it.
WHY = "the repository's own scaffolding, never read aloud"


def redeclare(root, content, corpus_api=2):
    """Rewrite this corpus's `corpus.json` with `content` and a version."""
    declared = {**corpora.MANIFEST, "corpus_api": corpus_api, "content": content}
    (root / "corpus.json").write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    return root


def test_a_file_the_manifest_calls_never_material_is_not_a_finding(tmp_path):
    # ⛔ **The hole this closes.** Measured against a real corpus: 100 of its
    # files were reported unclassified and only 3 were material withheld from
    # anybody — the rest a licence, ignore files, an editor's workspace. There
    # was no honest state for them and `exclude` made every `why` a small lie.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "LICENSE").write_text("A licence.\n", encoding="utf-8")
    redeclare(root, {"include": ["src/*.md"], "not_material": [{"glob": "LICENSE", "why": WHY}]})
    report = validate(root)
    assert report.findings == ()
    assert report.exit_code == 0


def test_the_third_state_does_not_silence_the_unclassified_catch(tmp_path):
    # ⛔ Rule 4 is not weakened by one line: a file the third state does not
    # name is still unaccounted for, and still exits 1.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "LICENSE").write_text("A licence.\n", encoding="utf-8")
    (root / "notes.txt").write_text("unaccounted for\n", encoding="utf-8")
    redeclare(root, {"include": ["src/*.md"], "not_material": [{"glob": "LICENSE", "why": WHY}]})
    report = validate(root)
    assert report.rules == ("unclassified",)
    assert [finding.where for finding in report.findings] == ["notes.txt"]
    assert report.exit_code == 1


def test_a_file_matched_by_include_and_not_material_is_a_finding_of_its_own(tmp_path):
    # ⛔ **Never a precedence, and its own rule id.** This is what stops the
    # third state becoming a drain: a glob that sweeps up material says so
    # loudly, per file, against a real tree.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    redeclare(root, {"include": ["src/*.md"], "not_material": [{"glob": "src/*", "why": WHY}]})
    report = validate(root)
    assert report.rules == ("contested",)
    assert report.findings[0].where == "src/one.md"
    assert report.exit_code == 1


def test_the_contested_finding_is_not_filed_under_the_unclassified_rule(tmp_path):
    # ⚠️ A different fact: the manifest classified this file twice and
    # disagreed with itself, which is not the same as never classifying it —
    # and a script filters on the two separately.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    redeclare(root, {"include": ["src/*.md"], "not_material": [{"glob": "src/*", "why": WHY}]})
    assert "unclassified" not in validate(root).rules
    assert RULE_CONTESTED != RULE_UNCLASSIFIED


def test_a_manifest_using_the_third_state_at_the_older_version_is_refused(tmp_path):
    # ⛔ R9: the version is the corpus's statement of which contract it was
    # written to, and it is refused rather than upgraded on its behalf.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    redeclare(
        root,
        {"include": ["src/*.md"], "not_material": [{"glob": "LICENSE", "why": WHY}]},
        corpus_api=1,
    )
    report = validate(root)
    assert "manifest" in report.rules
    assert "not_material" in report.findings[0].message


def test_a_corpus_with_no_material_beside_the_archive_says_so(tmp_path):
    report = validate(corpora.one_unit(tmp_path / "c"))
    assert "unclassified" in {u.rule for u in report.unchecked}


def test_the_archive_is_never_swept_as_source_material(tmp_path):
    # ⚠️ The archive is generated output living inside the corpus root;
    # sweeping it would classify the adapter's own writing as unclassified.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    assert scanned(root) == {"src/one.md"}


def test_a_sources_own_nested_archive_directory_is_material_and_never_skipped(tmp_path):
    # ⛔ `W241/2`: the scan skipped ANY `archive/`, so a source keeping its own
    # lost it from every reading. Only the root beside `corpus.json` is skipped.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "src" / ARCHIVE_DIR).mkdir()
    (root / "src" / ARCHIVE_DIR / "old.md").write_text("# Old\n", encoding="utf-8")
    assert scanned(root) == {"src/one.md", f"src/{ARCHIVE_DIR}/old.md"}
    report = validate(root)
    assert f"src/{ARCHIVE_DIR}/old.md" in {
        f.where for f in report.findings if f.rule == "unclassified"
    }


def test_the_manifest_itself_is_not_material(tmp_path):
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    assert "corpus.json" not in {p.name for p in source_files(root).files}


def test_the_generated_root_and_the_vcs_directory_are_skipped():
    assert ".git" in SKIP_DIRS
    assert ".studyforge" in SKIP_DIRS


# --------------------------------------------------------------------------
# ⛔ W28 — what is material is the corpus's declaration, not this file's guess
# --------------------------------------------------------------------------


def test_the_framework_names_only_its_own_two_directories():
    # ⛔ **`SKIP_DIRS` was R1 in miniature.** Two of its five names were the
    # framework knowing about two ecosystems it was told nothing about, and a
    # list of other people's build directories is wrong for the first corpus
    # that uses a third. These two are the framework's own: `.studyforge` is
    # this tool's, `.git` holds the declaration. ⚠️ The archive root left the
    # list (`W248`): it is skipped at the corpus root only.
    assert SKIP_DIRS == (".git", ".studyforge")
    assert ARCHIVE_DIR not in SKIP_DIRS
    assert "node_modules" not in SKIP_DIRS
    assert "__pycache__" not in SKIP_DIRS


def test_a_corpus_that_uses_neither_ecosystem_is_unaffected(tmp_path):
    # ⭐ The acceptance's third clause. Dropping two names may not change what
    # a corpus naming neither of them scans — under git and without it.
    plain = corpora.one_unit(tmp_path / "plain", source=corpora.SOURCE)
    assert scanned(plain) == {"src/one.md"}
    versioned = corpora.one_unit(tmp_path / "versioned", source=corpora.SOURCE)
    init_repository(versioned)
    assert scanned(versioned) == {"src/one.md"}


def test_a_file_the_repository_declares_as_output_is_not_material(tmp_path):
    # ⛔ **The whole task, in one assertion.** Measured against a real corpus,
    # 100 of 159 enumerated files were the repository's own declared output and
    # every one was reported as unclassified material.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "generated").mkdir()
    (root / "generated" / "graph.json").write_text("{}\n", encoding="utf-8")
    declared_output(root, "generated/")
    assert scanned(root) == {"src/one.md", ".gitignore"}


def test_the_same_file_is_material_when_the_repository_does_not_declare_it(tmp_path):
    # ⛔ **The negative control for the test above, and it is the whole reason
    # to trust it.** Same tree, same file, one line removed from the
    # declaration: the file must come back. Without this, a `source_files` that
    # dropped everything under a directory called `generated` would pass.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "generated").mkdir()
    (root / "generated" / "graph.json").write_text("{}\n", encoding="utf-8")
    declared_output(root)
    assert "generated/graph.json" in scanned(root)


def test_the_framework_no_longer_guesses_at_another_ecosystems_output(tmp_path):
    # ⛔ **R1, stated as a test.** A corpus that does NOT declare `node_modules`
    # as output gets it scanned, because the framework has no opinion about
    # what an ecosystem calls its build directory. The corpus decides.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    for directory in ("node_modules", "__pycache__"):
        (root / directory).mkdir()
        (root / directory / "thing.txt").write_text("x\n", encoding="utf-8")
    declared_output(root)
    assert {"node_modules/thing.txt", "__pycache__/thing.txt"} <= scanned(root)
    declared_output(root, "node_modules/", "__pycache__/")
    assert not {"node_modules/thing.txt", "__pycache__/thing.txt"} & scanned(root)


def test_a_tracked_file_is_material_even_when_a_pattern_would_ignore_it(tmp_path):
    # ⚠️ git's index wins over its ignore rules, and this test holds that
    # property: a file somebody committed is material even if a later
    # `.gitignore` names it. Adding `--no-index` to the query would reverse it.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "src" / "kept.md").write_text("# Kept\n", encoding="utf-8")
    declared_output(root, "src/kept.md")
    assert "src/kept.md" not in scanned(root), "the control: the pattern does bite"
    track(root, "src/kept.md")
    assert "src/kept.md" in scanned(root)


def test_an_untracked_file_that_is_not_declared_output_is_still_material(tmp_path):
    # ⛔ **Newly written material is material.** This is what forbids reading
    # the declaration as `git ls-files`: a file added and not yet committed is
    # exactly the file an adapter author is about to ingest, and answering
    # "not tracked, therefore not material" would hide it.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root)
    (root / "src" / "brand-new.md").write_text("# New\n", encoding="utf-8")
    assert "src/brand-new.md" in scanned(root)


# --------------------------------------------------------------------------
# ⛔ the degradation, and it may not guess
# --------------------------------------------------------------------------


def test_a_corpus_root_that_is_not_a_repository_says_so_and_still_scans(tmp_path):
    # ⛔ **The walk stands and `validate` SAYS SO.** Refusing a non-repository
    # corpus is wrong (R2: an archive is a shippable artifact on its own), and
    # silently falling back to a scan that over-reports is worse than either,
    # because it looks like a clean run.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "src" / "strays.txt").write_text("unaccounted for\n", encoding="utf-8")
    report = validate(root)
    assert "ignore-declaration" in {u.rule for u in report.unchecked}
    assert not source_files(root).consulted
    assert "src/strays.txt" in {f.where for f in report.findings}


def test_a_repository_is_not_reported_unchecked(tmp_path):
    # ⛔ The negative control for the claim above: an `Unchecked` that is always
    # emitted says nothing. It must be absent exactly when git answered.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root)
    assert source_files(root).consulted
    assert "ignore-declaration" not in {u.rule for u in validate(root).unchecked}


def test_an_unchecked_declaration_does_not_fail_the_run(tmp_path):
    # ⚠️ `Unchecked` is loud and counted, and it is not a `Finding`. A corpus
    # with nothing else wrong and no git is valid, and says what it could not
    # read.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    report = validate(root)
    assert report.findings == ()
    assert report.exit_code == 0
    assert "ignore-declaration" in {u.rule for u in report.unchecked}


def test_git_being_absent_degrades_the_same_way_as_a_missing_repository(tmp_path, monkeypatch):
    # ⚠️ The other half of "could not answer". A machine without git must reach
    # the same announced fallback, never a silent one.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root, "src/")
    assert source_files(root).consulted, "the control: with git installed it answers"
    assert "src/one.md" not in scanned(root)
    monkeypatch.setattr(classification.shutil, "which", lambda name: None)
    scan = source_files(root)
    assert not scan.consulted
    assert "src/one.md" in {p.relative_to(root).as_posix() for p in scan.files}


def test_an_unexpected_answer_from_git_is_not_read_as_nothing_is_ignored(tmp_path):
    # ⛔ **128 is "not a repository, or worse", and "or worse" is the point.**
    # Reading any non-verdict return code as an empty ignore set is the
    # fail-open this task exists to remove.
    # ⭐ Asked with an empty candidate list on purpose: git still discriminates
    # "a repository, nothing ignored" (frozenset()) from "not a repository"
    # (None), so `consulted` is truthful even for a corpus with no files.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root)
    assert classification.repository_ignores(root, []) == frozenset()
    outside = tmp_path / "not-a-repository"
    outside.mkdir()
    assert classification.repository_ignores(outside, []) is None


def test_a_candidate_outside_the_root_is_refused_naming_neither_path(tmp_path):
    # ⛔ R7, reached when `W257` made the reader public: `relative_to`'s own
    # message quotes the root, which is the input that carries a home directory.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root)
    stray = tmp_path / "elsewhere" / "file.md"
    with pytest.raises(ValueError) as refused:
        classification.repository_ignores(root, [stray])
    assert str(tmp_path) not in str(refused.value)
    assert refused.value.__suppress_context__, "the chained message still quotes the root"


def test_a_corpus_with_no_material_says_so_before_it_says_anything_else(tmp_path):
    # ⚠️ An empty corpus root reports "nothing to classify" and does not also
    # complain that it could not read a declaration it had no use for.
    report = validate(corpora.one_unit(tmp_path / "c"))
    assert "unclassified" in {u.rule for u in report.unchecked}
    assert "ignore-declaration" not in {u.rule for u in report.unchecked}


# --------------------------------------------------------------------------
# ⛔ W259 — only the corpus root's own `.git` and `.studyforge` are skipped
# --------------------------------------------------------------------------


def plant(root, where, text="planted\n"):
    """Write one file at `where` beneath the corpus root and return `where`."""
    path = root / where
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return where


def named(root, rule):
    """Where `validate` reports a finding under `rule`, as it names them."""
    return [f.where for f in validate(root).findings if f.rule == rule]


@pytest.mark.parametrize("versioned", [False, True], ids=["export", "repository"])
def test_a_nested_studyforge_directory_is_scanned_and_its_file_named(tmp_path, versioned):
    # ⛔ **The row's harm.** The framework writes `.studyforge` at the corpus
    # root only, so one beneath it is a source's own directory, and a scan that
    # skipped the name at any depth lost it without a word.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    if versioned:
        declared_output(root)
    where = plant(root, "src/.studyforge/notes.md")
    assert where in scanned(root)
    assert where in named(root, RULE_UNCLASSIFIED)


@pytest.mark.parametrize("versioned", [False, True], ids=["export", "repository"])
def test_the_roots_own_studyforge_directory_reads_clean(tmp_path, versioned):
    # ⭐ The other way (R12): the root's own is the framework's, and planting a
    # file there changes nothing the report says.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    if versioned:
        declared_output(root)
    before = validate(root).findings
    plant(root, ".studyforge/notes.md")
    assert not {where for where in scanned(root) if where.startswith(".studyforge/")}
    assert validate(root).findings == before


@pytest.mark.parametrize("store", ["directory", "gitfile"])
def test_a_nested_repository_store_is_refused_by_name_and_never_entered(tmp_path, store):
    # ⛔ **Refused, never skipped and never scanned** (`W259`'s ruling). A
    # vendored repository's objects are not prose, and a submodule's `.git` is
    # a file, which the old walk scanned while it skipped the directory form.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root)
    if store == "directory":
        init_repository(root / "vendor" / "lib")
    else:
        plant(root, "vendor/lib/.git", "gitdir: ../../.git/modules/lib\n")
    report = validate(root)
    assert [f.where for f in report.findings if f.rule == RULE_NESTED_REPOSITORY] == [
        "vendor/lib/.git"
    ]
    entered = [f for f in report.findings if ".git" in f.where.split("/")]
    assert [f.rule for f in entered] == [RULE_NESTED_REPOSITORY]


def test_a_nested_store_the_repository_declares_as_output_is_not_refused(tmp_path):
    # ⭐ What is output is the corpus's declaration, for a store as for a file.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    init_repository(root / "vendor" / "lib")
    declared_output(root)
    assert named(root, RULE_NESTED_REPOSITORY) == ["vendor/lib/.git"], "the control"
    declared_output(root, "vendor/")
    assert named(root, RULE_NESTED_REPOSITORY) == []


def test_a_nested_store_is_refused_where_no_declaration_can_be_read(tmp_path):
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    plant(root, "vendor/lib/.git/HEAD", "ref: refs/heads/main\n")
    assert not source_files(root).consulted
    assert named(root, RULE_NESTED_REPOSITORY) == ["vendor/lib/.git"]
    assert "vendor/lib/.git/HEAD" not in scanned(root)


def test_the_roots_own_repository_store_reads_clean(tmp_path):
    # ⭐ Both forms at the root: a checkout's directory, and a linked worktree's gitfile.
    versioned = corpora.one_unit(tmp_path / "versioned", source=corpora.SOURCE)
    declared_output(versioned)
    assert source_files(versioned).stores == ()
    worktree = corpora.one_unit(tmp_path / "worktree", source=corpora.SOURCE)
    plant(worktree, ".git", "gitdir: elsewhere\n")
    assert source_files(worktree).stores == ()
    assert ".git" not in scanned(worktree)


def test_a_store_beneath_the_archive_root_stays_an_archive_stray(tmp_path):
    # ⛔ `W248` keeps reading exactly as it did: beneath `archive/`, membership
    # accounts for every file, and this check never sees it.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root)
    where = plant(root, f"{ARCHIVE_DIR}/demo/.git/HEAD")
    assert where in named(root, RULE_ARCHIVE_STRAY)
    assert named(root, RULE_NESTED_REPOSITORY) == []


# --------------------------------------------------------------------------
# ⛔ `W266` — an INCLUDED file no origin names is refused by name
# --------------------------------------------------------------------------

#: A whole-series aggregate: the unit's own prose again, which a glob sweeps in beside it.
AGGREGATE = "src/all-units.md"


def test_an_INCLUDED_aggregate_NO_origin_names_is_refused_BY_NAME_exit_1(tmp_path):
    # ⛔ Clause 1 and clause 3's RED arm: the aggregate shape, un-excluded.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    plant(root, AGGREGATE, corpora.SOURCE)
    report = validate(root)
    assert report.rules == ("included-unread",)
    assert [finding.where for finding in report.findings] == [AGGREGATE]
    assert report.exit_code == 1


def test_the_SAME_aggregate_EXCLUDED_is_the_control_and_reads_clean(tmp_path):
    # ⭐ Clause 2 and clause 3's GREEN arm: withheld with its reason, it is not unread material.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    plant(root, AGGREGATE, corpora.SOURCE)
    redeclare(root, {"include": ["src/*.md"], "exclude": [{"path": AGGREGATE, "why": WHY}]})
    report = validate(root)
    assert report.findings == ()
    assert report.exit_code == 0


def test_a_file_EVERY_unit_reads_is_clean_and_ONE_only_a_CONTAINER_names_is_NOT_read(tmp_path):
    # ⭐ Clause 2: a unit's origin is read. ⛔ A container's `origin` only PLACES its page,
    # which is exactly how an aggregate hides (it is ISO's shape), so it is not a read.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    assert validate(root).findings == (), "⭐ the file the unit reads is clean"
    held = root / "archive" / "demo" / "container.json"
    held.write_text(
        held.read_text(encoding="utf-8").replace(
            '"container_api": 1,', '"container_api": 1,\n  "origin": "src/all-units.md",'
        ),
        encoding="utf-8",
    )
    plant(root, AGGREGATE, corpora.SOURCE)
    assert [f.where for f in validate(root).findings] == [AGGREGATE]


def test_a_fresh_STRAY_included_file_is_named(tmp_path):
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    plant(root, "src/zz-stray.md", "# Stray\n")
    assert [f.where for f in validate(root).findings] == ["src/zz-stray.md"]


def test_NOT_MATERIAL_code_and_DECLARED_OUTPUT_are_never_refused_as_unread(tmp_path):
    # ⭐ Neither is material a unit reads: the hand-written ingest module is `not_material`,
    # and a file the repository declares as output never enters the scan.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root, "src/draft.md")
    plant(root, "ingest/adapter.py", "print('reads the source')\n")
    plant(root, "src/draft.md", "# Draft\n")
    redeclare(root, {"include": ["src/*.md"], "not_material": [{"glob": "ingest/**", "why": WHY}]})
    report = validate(root)
    assert "included-unread" not in report.rules, report.rules


def test_NO_origin_on_disk_is_origin_missing_s_answer_and_never_unread(tmp_path):
    # ⛔ W255/W261 keep their own reading: with every origin absent nothing here is judged.
    root = corpora.one_unit(tmp_path / "c", origin="src/missing.md")
    plant(root, "src/present.md", corpora.SOURCE)
    assert validate(root).rules == ("origin-missing",)
