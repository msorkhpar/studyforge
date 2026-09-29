"""Mirror of `src/studyforge/narrate/release/ignores.py` (R12): the rules keeping clips out of git.

⭐ Every clause is asked of git, in a repository holding the corpus, never of the
list of files alone:

- a `tree` corpus needs no file, its onboarding wrote the one it has;
- a `sibling` corpus gets one file in each `study/` directory that holds clips, and
  after a restore puts the clips back git sees no untracked file;
- a manifest that classifies the file nowhere is refused before anything is written,
  and the refusal names what to declare;
- writing is repeatable, and keeps a line somebody already put in the file.
"""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath

import pytest

from studyforge.narrate.release import (
    PackRefused,
    clips_of,
    media_ignores,
    write_media_ignores,
)
from tests.studyforge.cli.narrate.plant import released_corpus
from tests.support import git, init_repository, run


def declared(root: Path) -> Path:
    """Declare each ignore file the pack adds as scaffolding, one exact path each."""
    manifest = root / "corpus.json"
    document = json.loads(manifest.read_text(encoding="utf-8"))
    document["corpus_api"] = max(document["corpus_api"], 2)  # `not_material` arrived in 2
    studies = {PurePosixPath(m).parent.parent.parent for m, _ in clips_of(root)}
    homes = sorted(study / ".gitignore" for study in studies)
    document["content"].setdefault("not_material", []).extend(
        {"glob": home.as_posix(), "why": "the ignore rules the narration pack writes beside clips"}
        for home in homes
    )
    manifest.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return root


def sibling(tmp_path: Path) -> Path:
    return declared(released_corpus(tmp_path, "depth2"))


def test_a_tree_corpus_needs_no_file_of_the_pack(tmp_path):
    root = released_corpus(tmp_path, "depth1")
    assert media_ignores(root) == ()
    assert write_media_ignores(root, ()) == ()


def test_a_sibling_corpus_gets_a_file_in_each_study_directory_that_holds_clips(tmp_path):
    root = sibling(tmp_path)
    files = media_ignores(root)
    holding = {PurePosixPath(member).parents[3] for member, _ in clips_of(root)}
    assert files and {one.home.parent.parent for one in files} == holding
    assert all(one.home.name == ".gitignore" and one.home.parent.name == "study" for one in files)


def test_written_files_make_git_ignore_every_clip_and_nothing_else(tmp_path):
    root = sibling(tmp_path)
    repository = init_repository(root)
    clips = [member for member, _ in clips_of(root)]
    assert run([git(), "add", "-A", "--dry-run"], cwd=repository).stdout.count(".mp3") == len(clips)
    written = write_media_ignores(root, media_ignores(root))
    assert written and all(where.endswith("study/.gitignore") for where in written)
    added = run([git(), "add", "-A", "--dry-run"], cwd=repository).stdout
    assert ".mp3" not in added
    assert all(where in added for where in written), "the rules themselves are committed"
    assert "corpus.json" in added


def test_writing_twice_changes_nothing_and_keeps_a_line_someone_added(tmp_path):
    root = sibling(tmp_path)
    files = media_ignores(root)
    assert write_media_ignores(root, files)
    assert write_media_ignores(root, files) == ()
    home = root / files[0].home
    home.write_text(home.read_text(encoding="utf-8").replace("audio/\n", "notes/\n"), "utf-8")
    assert write_media_ignores(root, files) == (files[0].home.as_posix(),)
    text = home.read_text(encoding="utf-8")
    assert "notes/" in text and text.count("audio/") == 1


def test_a_manifest_that_classifies_the_file_nowhere_is_refused_naming_the_remedy(tmp_path):
    root = released_corpus(tmp_path, "depth2")
    with pytest.raises(PackRefused, match="content.not_material"):
        media_ignores(root)
    assert not list(root.rglob("study/.gitignore"))


def test_the_restored_clips_are_untracked_noise_without_the_files(tmp_path):
    # ⭐ The control: with nothing written, git reads every clip as new.
    root = sibling(tmp_path)
    repository = init_repository(root)
    status = run([git(), "status", "--porcelain", "-uall"], cwd=repository).stdout
    assert status.count(".mp3") == len(clips_of(root))
