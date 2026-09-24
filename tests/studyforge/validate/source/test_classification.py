"""Mirror of `src/studyforge/validate/source/classification.py` (R12).

⛔ **Silence is the double ingest.** Every assertion here is about a file the
manifest did not account for, or accounted for twice, or that the repository
itself calls generated output — and about the one degradation this check is
allowed: saying out loud that it could not read the declaration.

⚠️ The imports come through the package surface, not through the submodule,
except where a test asserts what the submodule itself carries.
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
    classification,
    enumeration,
    source_files,
)
from tests.studyforge.validate import corpora
from tests.studyforge.validate.source.test_enumeration import declared_output, scanned
from tests.support import init_repository

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
    # ⛔ **The hole this closes.** A real corpus holds files that are not
    # material at all — a licence, ignore files, an editor's workspace — and
    # without this state `exclude` would make every `why` a small lie.
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
    # ⛔ Skipping ANY `archive/` would lose a source's own from every reading.
    # Only the root beside `corpus.json` is skipped.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "src" / ARCHIVE_DIR).mkdir()
    (root / "src" / ARCHIVE_DIR / "old.md").write_text("# Old\n", encoding="utf-8")
    assert scanned(root) == {"src/one.md", f"src/{ARCHIVE_DIR}/old.md"}
    report = validate(root)
    assert f"src/{ARCHIVE_DIR}/old.md" in {
        f.where for f in report.findings if f.rule == "unclassified"
    }


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


def test_a_corpus_with_no_material_says_so_before_it_says_anything_else(tmp_path):
    # ⚠️ An empty corpus root reports "nothing to classify" and does not also
    # complain that it could not read a declaration it had no use for.
    report = validate(corpora.one_unit(tmp_path / "c"))
    assert "unclassified" in {u.rule for u in report.unchecked}
    assert "ignore-declaration" not in {u.rule for u in report.unchecked}


# --------------------------------------------------------------------------
# ⛔ Only the corpus root's own `.git` and `.studyforge` are skipped
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
    # ⛔ **Refused, never skipped and never scanned.** A vendored repository's
    # objects are not prose, and a submodule's `.git` is a file, which a walk
    # skipping only the directory form would scan.
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
    # ⛔ Beneath `archive/`, membership
    # accounts for every file, and this check never sees it.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root)
    where = plant(root, f"{ARCHIVE_DIR}/demo/.git/HEAD")
    assert where in named(root, RULE_ARCHIVE_STRAY)
    assert named(root, RULE_NESTED_REPOSITORY) == []


# --------------------------------------------------------------------------
# ⛔ An INCLUDED file no origin names is refused by name
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
    # ⛔ With every origin absent nothing here is judged: the absent-source reading stands.
    root = corpora.one_unit(tmp_path / "c", origin="src/missing.md")
    plant(root, "src/present.md", corpora.SOURCE)
    assert validate(root).rules == ("origin-missing",)


def test_W280_every_name_importers_read_from_this_module_still_imports_from_it():
    # ⛔ The split's first clause: the split moved the enumeration out, and an importer that named a
    # name from `classification` before it still reads the SAME object from there.
    moved = ("IGNORE_TIMEOUT", "REPOSITORY_STORE", "SKIP_DIRS", "Scan", "repository_ignores")
    for name in (*moved, "source_files"):
        assert getattr(classification, name) is getattr(enumeration, name), name
    kept = ("RULE_CONTESTED", "RULE_IGNORE_DECLARATION", "RULE_INCLUDED_UNREAD")
    for name in (*kept, "RULE_NESTED_REPOSITORY", "RULE_UNCLASSIFIED", "check_unclassified"):
        assert name in vars(classification), name
    assert set(classification.__all__) >= {*moved, *kept, "source_files", "check_unclassified"}
