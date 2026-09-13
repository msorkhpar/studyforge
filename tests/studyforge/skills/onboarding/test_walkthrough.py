"""SK-07's acceptance, run end to end on a repository this skill has never seen.

⭐ **The clauses, and each one is a command here rather than an opinion:**

1. a repository goes from nothing to a `validate`-clean corpus with the
   framework beside it and one call;
2. ⛔ **no `.gitmodules` and no `git submodule add` anywhere in what it emits**;
3. the corpus carries an R3-safe ignore file and the repository's own root
   ignore file is byte-identical to before;
4. afterwards nothing existing has changed — additions only (R3);
5. **re-running changes nothing**, and the uninstall returns the repository to
   its prior state, asserted by comparing the tree.

⚠️ **The negative control is the point of the first clause.** `SK-02/1`
measured `NOT valid: 8 finding(s)` — one `unclassified` per generated file —
and the remedy was a person copying two lines. So the control here scaffolds
*without* the declaration and asserts that those findings come back: a test
that only ever sees green cannot tell you the green means anything.
"""

from __future__ import annotations

import os
import subprocess
import sys

from studyforge.corpus.manifest import parse
from studyforge.skills.adapter import plan_for, scaffold
from studyforge.skills.onboarding import onboard, uninstall
from studyforge.skills.onboarding.manifest import promote, render
from studyforge.validate import validate
from tests.studyforge.skills.adapter import corpora as adapter
from tests.studyforge.skills.onboarding import corpora
from tests.support import repository_root

#: How long a subprocess is given. ⚠️ A bound rather than a hope.
TIMEOUT = 180


def _ingest(root):
    """Run the adapter the way an integrator would, from inside the corpus."""
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join([str(root), str(repository_root() / "src")])
    environment.pop("PYTEST_ADDOPTS", None)
    return subprocess.run(
        [sys.executable, "-m", "ingest", str(root), adapter.INGESTED],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        check=False,
    )


def _tree(root):
    """Every path under `root`, relative and sorted — what a diff would compare."""
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))


def _onboarded(tmp_path):
    """Steps 1–4 of the procedure: material, onboarding, and the one file that is yours."""
    root = corpora.material(tmp_path / "corpus")
    made = onboard(corpora.DRAFT, framework_commit=corpora.COMMIT)
    made.write(root)
    (root / made.hand_written[0]).write_text(adapter.READ, encoding="utf-8")
    return root, made


def test_a_repository_of_material_reaches_a_validate_clean_corpus(tmp_path):
    # ⛔ Clause 1. Nothing between the material and the exit code below was
    # typed by anybody: the manifest, the adapter and the declaration that
    # classifies it were all generated in one call.
    root, _ = _onboarded(tmp_path)

    result = _ingest(root)
    assert result.returncode == 0, result.stdout + result.stderr

    report = validate(root)
    assert report.ok, "\n".join(str(finding) for finding in report.findings)
    assert not report.findings


def test_without_the_declaration_the_same_corpus_reports_one_finding_per_generated_file(tmp_path):
    # ⛔ The negative control, and it is `SK-02/1`'s own measurement re-run.
    # ⚠️ Same tree, same adapter, same walk — the *only* difference is that the
    # manifest does not carry `content.not_material`.
    root = corpora.material(tmp_path / "corpus")
    document = promote(corpora.DRAFT)
    (root / "corpus.json").write_text(render(document), encoding="utf-8")
    made = scaffold(plan_for(parse(render(document))))
    made.write(root)
    (root / made.hand_written[0]).write_text(adapter.READ, encoding="utf-8")

    report = validate(root)

    unclassified = [finding for finding in report.findings if finding.rule == "unclassified"]
    assert not report.ok, "the control passed, so the clean run above proves nothing"
    assert len(unclassified) >= len(made.files), (
        "every generated file should be unclassified without the declaration"
    )


def _unclassified_notes(tmp_path, content):
    """Onboard the material plus a notes file, and return what validate cannot classify."""
    root = corpora.material(tmp_path / "corpus")
    (root / "notes").mkdir()
    (root / "notes/a.txt").write_text("what the integrator noticed\n", encoding="utf-8")
    onboard(corpora.draft(content=content), framework_commit=corpora.COMMIT).write(root)
    report = validate(root)
    return [finding.where for finding in report.findings if finding.rule == "unclassified"]


def test_a_persons_not_material_block_classifies_the_files_it_declares(tmp_path):
    # ⛔ INT06-1 end to end: the draft's block reaches the written manifest, so
    # `validate` finds nothing unclassified — and the control, the same tree and
    # the same draft without the block, names the file. Without the control the
    # first half could pass on a walk that never saw `notes/`.
    content = dict(corpora.DRAFT["content"])

    declared = _unclassified_notes(tmp_path / "with", {**content, "not_material": [corpora.NOTES]})
    control = _unclassified_notes(tmp_path / "without", content)

    assert not any("notes/a.txt" in where for where in declared), declared
    assert any("notes/a.txt" in where for where in control), "the control saw no notes file"


def test_nothing_it_emits_makes_the_framework_a_submodule(tmp_path):
    # ⛔ Clause 2. R18 was amended: nothing here is pushed to any remote, so a
    # submodule URL has no legal form.
    root, made = _onboarded(tmp_path)

    assert not (root / ".gitmodules").exists()
    emitted = "\n".join(item.text for item in made.files)
    assert "git submodule add" not in emitted
    assert ".gitmodules" not in emitted or "not (_root() / '.gitmodules').exists()" in emitted


def test_the_repositorys_own_root_ignore_file_is_untouched(tmp_path):
    # ⛔ Clause 3, and W15's measured breach: tooling appended a generated
    # directory to a source repository's root ignore file on an ordinary
    # commit. Any rule this skill needs goes inside its own directory instead.
    root = corpora.material(tmp_path / "corpus")
    (root / ".gitignore").write_text("target/\n", encoding="utf-8")
    before = (root / ".gitignore").read_bytes()

    onboard(corpora.DRAFT, framework_commit=corpora.COMMIT).write(root)

    assert (root / ".gitignore").read_bytes() == before


def test_afterwards_nothing_that_existed_has_changed(tmp_path):
    # ⛔ Clause 4 (R3), measured rather than described: every pre-existing file
    # is byte-identical, and the manifest declares no permitted edit.
    root = corpora.material(tmp_path / "corpus")
    before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}

    made = onboard(corpora.DRAFT, framework_commit=corpora.COMMIT)
    made.write(root)

    assert all(path.read_bytes() == text for path, text in before.items())
    assert made.manifest.permitted_edits == ()


def test_re_running_it_changes_nothing(tmp_path):
    # ⛔ Clause 5's first half. A generator whose second run differs from its
    # first is one nobody can regenerate from, which is the whole of R19.
    root, _ = _onboarded(tmp_path)
    before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}

    onboard(corpora.DRAFT, framework_commit=corpora.COMMIT).write(root, regenerate=True)

    changed = [
        path.relative_to(root).as_posix()
        for path, text in before.items()
        if path.read_bytes() != text
    ]
    assert changed == [], f"a second run rewrote {changed}"


def test_the_uninstall_returns_the_repository_to_its_prior_state(tmp_path):
    # ⛔ Clause 5's second half, asserted by comparing the trees.
    root = corpora.material(tmp_path / "corpus")
    before = _tree(root)

    onboard(corpora.DRAFT, framework_commit=corpora.COMMIT).write(root)
    removed = uninstall(root)

    assert _tree(root) == before
    assert "corpus.json" in removed


def test_the_reader_is_left_a_document_written_from_the_corpus_own_declarations(tmp_path):
    root, _ = _onboarded(tmp_path)

    text = (root / "ONBOARDING.md").read_text(encoding="utf-8")

    assert "A Walkthrough Corpus" in text
    assert "ingest/read.py" in text
    assert str(tmp_path) not in text, "the reader's document carries an absolute path (R7)"


def test_nothing_it_writes_carries_an_absolute_path(tmp_path):
    # ⛔ R7, over every byte this skill emits rather than over the ones a
    # reviewer thought to look at.
    root, made = _onboarded(tmp_path)

    for item in made.files:
        assert str(tmp_path) not in item.text, item.where
        assert "/home/" not in item.text, item.where
