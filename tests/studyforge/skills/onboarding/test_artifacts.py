"""Mirror of `src/studyforge/skills/onboarding/artifacts.py` (R12).

⚠️ **R3's generated check moved to `nondestructive` and so did its three
clauses** (`W331`): they are in `test_nondestructive.py`, which runs the check
rather than only parsing it.

⭐ **The test that matters most here asserts coverage, not a list.** A seventh
artifact added without a `content.not_material` glob is an `unclassified`
finding in somebody else's repository, discovered by them; this asks the same
question here, of every path the module says it writes.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import replace

from studyforge.archive.scrub import assert_clean
from studyforge.cli.narrate.stage import narrate_corpus
from studyforge.corpus.manifest import MIN_WHY_CHARS, Classification, parse
from studyforge.narrate.client import NarrateClient
from studyforge.skills.adapter import plan_for
from studyforge.skills.onboarding import artifacts, hand_edited
from studyforge.skills.onboarding.manifest import promote, render
from studyforge.skills.onboarding.onboard import onboard
from studyforge.skills.onboarding.pin import FRAMEWORK
from studyforge.skills.onboarding.standing import Standing
from tests.studyforge.cli.narrate.service import BASE, FMT, VOICE, FakeService
from tests.studyforge.skills.adapter import corpora as adapter
from tests.studyforge.skills.onboarding import corpora
from tests.support import repository_root

#: How long one command is given. ⚠️ A bound rather than a hope.
TIMEOUT = 180

EDIT = {
    "path": "pom.xml",
    "kind": "insert-line",
    "anchor": "</modules>",
    "content": "<module>study</module>",
    "why": "the build file the toolchain image needs one module added to",
}


def _document(manifest, hand_written=(), **given):
    return artifacts.reader_document(manifest, hand_written, commit=corpora.COMMIT, **given)


def _manifest(**changes):
    return parse(render(promote(corpora.draft(**changes), not_material=artifacts.NOT_MATERIAL)))


def test_every_path_this_skill_writes_is_classified_by_a_glob_it_declares():
    # ⛔ Coverage, over the paths themselves. The manifest is the only thing
    # that can answer `validate`'s unclassified check, and a path this module
    # writes without a glob is a finding it created for its consumer.
    unclassified = [
        where
        for where in artifacts.paths()
        if where != artifacts.MANIFEST and not artifacts.classified(where)
    ]
    assert not unclassified, f"these have no not_material glob: {unclassified}"


def test_the_globs_are_answered_by_the_manifest_itself_and_not_only_by_this_module():
    # ⭐ The behavioural half: `classified` is this module's own opinion, and
    # `ContentPolicy.classify` is what the corpus will actually be judged by.
    manifest = _manifest()

    for where in artifacts.paths():
        if where == artifacts.MANIFEST:
            continue
        assert manifest.content.classify(where) is Classification.NOT_MATERIAL, where


def test_the_manifest_is_not_declared_not_material_by_the_document_it_is():
    assert not artifacts.classified(artifacts.MANIFEST)


def test_this_skill_never_writes_a_repository_root_ignore_file():
    # ⛔ R3, and W15's measured breach: tooling appended to a source
    # repository's root ignore file on an ordinary commit, unrequested.
    roots = [where for where in artifacts.paths() if where in (".gitignore", ".gitattributes")]
    assert not roots, f"this skill writes a repository-root ignore file: {roots}"


def test_no_ignore_rule_this_skill_writes_reaches_the_archive():
    # ⛔ SF-32's verdict: generated media is committed by default, so an ignore
    # rule that swept it out would flip a corpus's policy without anybody
    # declaring it. ⭐ This skill now writes no ignore rule at all, at any
    # depth — the assertion is over every path it occupies, not one name.
    rules = [where for where in artifacts.paths() if where.rsplit("/", 1)[-1] == ".gitignore"]
    assert not rules, f"this skill writes an ignore rule: {rules}"


def test_the_reader_document_is_written_from_the_declarations_rather_than_invented():
    text = _document(_manifest(), ("ingest/read.py",))

    assert "A Walkthrough Corpus" in text
    assert "course" in text
    assert "ingest/read.py" in text
    assert "Not read" in text, "a unit count without a reading would be invented"
    assert "units:" not in text


def test_a_corpus_with_no_graders_is_told_it_is_complete_rather_than_short():
    # ⛔ §7's three states, C5: a corpus with no graders is complete at the
    # reading floor. Telling its reader otherwise is the failure C5 describes.
    text = _document(_manifest(exercises=False))

    assert "complete product" in text
    assert "waiting on one" in text


def test_a_corpus_with_graders_is_told_about_the_execution_track():
    assert "Run and Submit" in _document(_manifest(exercises=True))


def test_the_reader_is_told_the_two_ways_forward_before_the_media_stops_fitting():
    # ⭐ And never that the policy was flipped for them.
    text = _document(_manifest())

    assert "will not pick one for you" in text
    assert "change to `corpus.json`" in text


def test_the_declared_edits_are_quoted_to_the_reader_with_their_reasons():
    text = _document(_manifest(permitted_edits=[EDIT]))

    assert "pom.xml" in text
    assert EDIT["why"] in text


def test_every_reason_clears_the_minimum_the_manifest_enforces():
    # ⚠️ A reason the document refuses is a reason the integrator has to
    # invent, which is the retyping R19 forbids. ⛔ The minimum is imported
    # from the module that owns it, never re-typed as a number here.
    for entry in artifacts.NOT_MATERIAL:
        assert len(entry["why"].strip()) >= MIN_WHY_CHARS, entry["glob"]


# --------------------------------------------------------------------------
# ⛔ `W313` — the document states what the build read, and nothing it did not
# --------------------------------------------------------------------------

READ = Standing(read=True, declared=3, units=2, narrated=1, reading_only=2, recorded=True)


def test_a_reading_is_stated_figure_by_figure():
    text = _document(_manifest(), standing=READ)

    assert "- units: 3 declared, 2 with material" in text
    assert "- narrated: 1 of 2\n" in text
    assert "- reading-only: 2 of 2" in text
    assert "container: none needed" in text
    assert "Nothing has been ingested" not in text and "Not read" not in text


def test_a_unit_declaring_a_practice_is_stated_as_needing_a_container():
    # ⛔ Both ways (R12): the same reading with one unit that is not reading-only.
    text = _document(_manifest(), standing=replace(READ, reading_only=1))

    assert "container: needed, because 1 unit(s) declare a graded practice" in text
    assert "none needed" not in text


def test_a_corpus_with_no_narration_record_is_told_so_beside_the_zero():
    silent = _document(_manifest(), standing=replace(READ, narrated=0, recorded=False))
    recorded = _document(_manifest(), standing=replace(READ, narrated=0))

    assert "- narrated: 0 of 2 (there is no narration record yet)" in silent
    assert "no narration record" not in recorded


def test_before_ingest_it_says_plainly_that_nothing_is_known_and_prints_no_figure():
    text = _document(_manifest(), standing=Standing())

    assert "Nothing has been ingested" in text
    assert "units:" not in text and "narrated:" not in text


def test_a_corpus_the_build_refuses_is_named_as_unread_with_the_refusal():
    text = _document(_manifest(), standing=Standing(refused="the record\nis broken"))

    assert "Not known" in text
    assert "> the record is broken" in text
    assert "units:" not in text


def test_the_commands_carry_the_pin_the_framework_sibling_and_the_adapter_package():
    manifest = _manifest()
    text = _document(manifest)

    assert f"git -C ../{FRAMEWORK} checkout --detach {corpora.COMMIT}" in text
    assert f"python3 -m {plan_for(manifest).package} .\n" in text
    assert "studyforge validate" not in text, "a command that is not on a fresh clone's path"
    assert "submodule" in text and "git submodule" not in text


def _fenced(text):
    """Every line inside a fence of the document, in order — what a reader would run."""
    lines, inside = [], False
    for line in text.splitlines():
        if line.startswith("```"):
            inside = not inside
        elif inside:
            lines.append(line)
    return lines


def _run_as_written(root, text, bin_dir):
    """Run every fenced line through a shell at `root`, exactly as it is printed."""
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in ("PYTHONPATH", "PYTEST_ADDOPTS")
    }
    environment["PATH"] = os.pathsep.join([str(bin_dir), environment.get("PATH", "")])
    environment.update(corpora.SYNTHETIC_GIT)
    results = []
    for line in _fenced(text):
        done = subprocess.run(
            ["sh", "-c", line],
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            check=False,
        )
        results.append((line, done.returncode, done.stdout + done.stderr))
    return results


def _fresh_clone(tmp_path):
    """A corpus beside a framework checkout at the pin, whose `src` is this tree's."""
    root = corpora.material(tmp_path / "corpus")
    (root.parent / FRAMEWORK / "src").symlink_to(repository_root() / "src")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "python3").symlink_to(sys.executable)
    return root, bin_dir


def _regenerate(root):
    made = onboard(corpora.SETTLED, framework_commit=corpora.COMMIT, root=root)
    made.write(root, regenerate=True)
    return (root / artifacts.READER_DOC).read_text(encoding="utf-8")


def _narrate(root):
    client = NarrateClient(BASE, voice=VOICE, fmt=FMT, transport=FakeService())
    narrate_corpus(root, client, voice=VOICE, fmt=FMT)


def test_every_command_runs_as_written_before_ingest_and_after_narration(tmp_path):
    # ⛔ Clauses 1, 2 and 4, over one fabricated corpus: every fenced line is
    # EXECUTED from the corpus root, and the state is read before and after.
    root, bin_dir = _fresh_clone(tmp_path)
    made = onboard(corpora.SETTLED, framework_commit=corpora.COMMIT, root=root)
    made.write(root)
    (root / made.hand_written[0]).write_text(adapter.READ, encoding="utf-8")
    before = (root / artifacts.READER_DOC).read_text(encoding="utf-8")

    ran = _run_as_written(root, before, bin_dir)
    _narrate(root)
    after = _regenerate(root)

    assert "Nothing has been ingested" in before
    assert len(ran) == len(_fenced(before)) > 1
    assert [(line, code) for line, code, _ in ran if code != 0] == [], ran
    assert "- units: 2 declared, 2 with material" in after
    assert "- narrated: 2 of 2\n" in after
    assert "- reading-only: 2 of 2" in after and "container: none needed" in after
    assert all(code == 0 for _, code, _ in _run_as_written(root, after, bin_dir))


def test_regeneration_is_idempotent_clean_and_follows_the_state(tmp_path):
    # ⛔ Clause 3: a second run diffs empty, R7's gate passes, and the reading
    # moves when — and only when — the corpus does.
    root, bin_dir = _fresh_clone(tmp_path)
    made = onboard(corpora.SETTLED, framework_commit=corpora.COMMIT, root=root)
    made.write(root)
    (root / made.hand_written[0]).write_text(adapter.READ, encoding="utf-8")
    ingest = [line for line in _fenced(_regenerate(root)) if " -m ingest " in line]
    _run_as_written(root, "```\n" + "\n".join(ingest) + "\n```", bin_dir)

    first = _regenerate(root)
    tree = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
    second = _regenerate(root)
    moved = [path for path, body in tree.items() if path.read_bytes() != body]
    _narrate(root)
    third = _regenerate(root)

    assert first == second
    assert moved == []
    assert hand_edited(root) == []
    assert "- narrated: 0 of 2 (there is no narration record yet)" in first
    assert "- narrated: 2 of 2\n" in third
    for text in (first, third):
        assert_clean(text, artifacts.READER_DOC)
        assert str(tmp_path) not in text


# --------------------------------------------------------------------------
# ⛔ `W321` — the document addresses the framework where the PIN resolves it
# --------------------------------------------------------------------------


def _worktree_clone(tmp_path):
    """A corpus that IS a linked worktree, with the framework beside its MAIN checkout.

    ⛔ Nothing beside the worktree itself — which is why a document addressing
    `../studyforge` from here reaches a directory that is not the framework.
    """
    root = corpora.material(corpora.linked_worktree(tmp_path), framework=False)
    (tmp_path / FRAMEWORK / "src").symlink_to(repository_root() / "src")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "python3").symlink_to(sys.executable)
    return root, bin_dir


def _written(root):
    """Onboard `root`, naming it, and return the reader document that was written."""
    made = onboard(corpora.SETTLED, framework_commit=corpora.COMMIT, root=root)
    made.write(root)
    (root / made.hand_written[0]).write_text(adapter.READ, encoding="utf-8")
    return made, (root / artifacts.READER_DOC).read_text(encoding="utf-8")


def test_every_command_runs_as_written_from_a_corpus_that_is_a_linked_worktree(tmp_path):
    # ⛔ The bar `W313` set, on the shape that broke: every fenced line is
    # EXECUTED from the worktree, and the ascent is the pin's own.
    root, bin_dir = _worktree_clone(tmp_path)
    made, text = _written(root)

    ran = _run_as_written(root, text, bin_dir)

    assert made.framework == f"../../{FRAMEWORK}"
    assert f"git -C ../../{FRAMEWORK} checkout --detach {corpora.COMMIT}" in text
    assert len(ran) == len(_fenced(text)) > 1
    assert [(line, code) for line, code, _ in ran if code != 0] == [], ran
    assert str(tmp_path) not in text and "/home/" not in text


def test_the_address_this_document_used_to_carry_does_not_run_from_that_worktree(tmp_path):
    # ⛔ The negative control, run negatively: the same document addressed
    # relative to the CORPUS ROOT — what was printed before this row — reaches
    # a directory beside the worktree, and its commands fail there.
    root, bin_dir = _worktree_clone(tmp_path)
    made, _ = _written(root)

    stale = artifacts.reader_document(made.manifest, made.hand_written, commit=corpora.COMMIT)

    assert f"git -C ../{FRAMEWORK} checkout --detach" in stale
    assert not (root.parent / FRAMEWORK).exists(), "nothing stands beside the worktree"
    assert [(line, code) for line, code, _ in _run_as_written(root, stale, bin_dir) if code != 0]


def test_a_corpus_that_is_its_own_main_checkout_reads_exactly_as_it_did(tmp_path):
    # ⭐ Both ways (R12), and `W313`'s clause 2 is not broken by this row: the
    # fresh clone's document still says `../studyforge` and still runs.
    root, bin_dir = _fresh_clone(tmp_path)
    _made, text = _written(root)

    assert f"git -C ../{FRAMEWORK} checkout --detach {corpora.COMMIT}" in text
    assert all(code == 0 for _, code, _ in _run_as_written(root, text, bin_dir))


def test_the_document_says_what_the_address_is_relative_to_without_a_second_answer(tmp_path):
    # ⛔ Clause 2: the sentence beside the fence describes the LAYOUT, and the
    # address itself is `pin.framework_from`'s one answer — never a caveat
    # telling the reader to re-read a printed `../studyforge` from elsewhere.
    root, _bin = _worktree_clone(tmp_path)
    _made, text = _written(root)

    assert "beside this repository's main checkout" in text
    assert f"it is `../../{FRAMEWORK}` from this" in text
    assert text.count(f"../{FRAMEWORK}") == text.count(f"../../{FRAMEWORK}")
