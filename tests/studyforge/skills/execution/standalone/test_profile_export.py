"""A corpus that names an image profile: the lock, the prime layer's base and the thin export.

⭐ The profile's name is the fixture's own declaration (`tests/fixtures/sdk-profile`), and the
toolchain is a synthetic checkout that answers the profile command as the real one does, so
nothing here knows a profile and nothing needs the sibling on disk. ⛔ The self-contained
export, every lock without a profile and every corpus that declares none are what they were:
their tests are the files beside this one, unmodified.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from studyforge.corpus.manifest import load
from studyforge.skills.execution.standalone import bases, vendor, write
from tests.fixture_checks import FIXTURES
from tests.studyforge.skills.execution.standalone.test_bases import ONES, TWOS, lock, parsed
from tests.studyforge.skills.execution.standalone.test_vendor import TAGS, answering, course
from tests.studyforge.skills.execution.standalone.test_write import (
    GIT,
    INPUTS,
    git,
    thin_toolchain,
)

DECLARED = FIXTURES / "sdk-profile" / "corpus.json"
NAME = json.loads(DECLARED.read_text(encoding="utf-8"))["profile"]
RUNNER_TAG, EDITOR_TAG = "profile-runner-tag", "profile-editor-tag"
THREES, FOURS = "sha256:" + "3" * 64, "sha256:" + "4" * 64


def profile_lock(**changes) -> dict:
    """A lock naming the fixture's profile, with `changes` replacing whole entries of it."""
    entry = {
        "name": NAME,
        "runner": {
            "image": bases.profile_image("runner", NAME), "tag": RUNNER_TAG, "digest": THREES,
        },
        "editor": {
            "image": bases.profile_image("editor", NAME), "tag": EDITOR_TAG, "digest": FOURS,
        },
    }
    entry.update(changes)
    return lock(profile=entry)


def answered(asked: list[list[str]] | None = None, refuse: bool = False):
    """`git` for real; the build command and the profile command answered as the toolchain does."""
    fake = answering(TAGS)

    def run(argv, cwd):
        if argv[0] == "git":
            return git(argv, cwd)
        if "--print-tag" in argv:
            if asked is not None:
                asked.append(list(argv))
            if refuse:
                return 2, ""
            image = argv[argv.index("--image") + 1]
            return 0, f"t/{image}-{NAME}:{RUNNER_TAG if image == 'runner' else EDITOR_TAG}\n"
        code, printed = fake(argv, cwd)
        document = json.loads(printed)
        document["inputs"] = INPUTS[document["image"]]
        return code, json.dumps(document)

    return run


def checkout(where: Path, declared: Path | None = DECLARED) -> Path:
    """The fixture corpus as a git checkout; `declared` is another manifest laid over it."""
    root = course(Path(shutil.copytree(DECLARED.parent, where / "course")))
    if declared not in (None, DECLARED):
        shutil.copyfile(declared, root / "corpus.json")
    subprocess.run([*GIT, "init", "-q"], cwd=root, check=True)
    subprocess.run([*GIT, "add", "-A"], cwd=root, check=True)
    subprocess.run([*GIT, "commit", "-q", "-m", "fixture"], cwd=root, check=True)
    return root


def without_profile(where: Path) -> Path:
    """The fixture's manifest with its `profile` key removed, written beside the test's files."""
    declared = json.loads(DECLARED.read_text(encoding="utf-8"))
    path = where / "undeclared.json"
    path.write_text(json.dumps({k: v for k, v in declared.items() if k != "profile"}), "utf-8")
    return path


def export(where: Path, locked: bases.Bases | None, *, declared=DECLARED, run=None, name="out"):
    out = where / name
    made = write.release(
        checkout(where / f"{name}-src", declared),
        out,
        toolchain=thin_toolchain(where / f"{name}-tc"),
        platform="linux/amd64",
        bases=locked,
        run=run or answered(),
    )
    return out, made


@pytest.fixture(scope="module")
def profiled(tmp_path_factory):
    where = tmp_path_factory.mktemp("profiled")
    asked: list[list[str]] = []
    out, made = export(where, parsed(profile_lock()), run=answered(asked))
    return out, made, asked


def test_the_fixture_declares_the_runtimes_and_names_its_profile_as_data():
    declared = load(DECLARED)
    assert declared.runtimes == ("gradle", "java", "kotlin", "node", "python")
    assert declared.profile == NAME


def test_the_lock_resolves_the_profile_s_images_by_tag_and_digest(profiled):
    out, made, _ = profiled
    document = json.loads((out / write.MANIFEST).read_text(encoding="utf-8"))
    one = document["bases"]["profile"]
    assert one["name"] == NAME
    assert one["runner"] == {
        "image": bases.profile_image("runner", NAME),
        "tag": RUNNER_TAG,
        "digest": THREES,
    }
    assert set(document["bases"]) == {*bases.KINDS, "profile"}
    assert write.kept_paths(made) == document["keeps"]


def test_the_toolchain_is_asked_for_the_profile_once_per_image_over_the_declared_set(profiled):
    _, _, asked = profiled
    assert [argv[argv.index("--image") + 1] for argv in asked] == ["runner", "editor"]
    for argv in asked:
        assert argv[argv.index("--profile") + 1] == NAME
        assert argv[argv.index("--runtimes") + 1] == "gradle,java,kotlin,node,python"
        assert argv[-2:] == ["--platform", "linux/amd64"]


def test_the_prime_layers_start_from_the_profile_images_and_never_from_the_plain_bases(profiled):
    out, made, _ = profiled
    built = (out / "compose.yaml").read_text(encoding="utf-8")
    runner_ref = f"{bases.profile_image('runner', NAME)}:{RUNNER_TAG}@{THREES}"
    editor_ref = f"{bases.profile_image('editor', NAME)}:{EDITOR_TAG}@{FOURS}"
    assert runner_ref in built and editor_ref in built
    assert f"@{ONES}" not in built and f"@{TWOS}" not in built
    assert made.names.runner_base.endswith(f"{RUNNER_TAG}@{THREES}")
    assert made.names.runner.endswith("-" + "3" * bases.KEY_DIGITS)
    assert made.names.editor.endswith("-" + "4" * bases.KEY_DIGITS)


def test_the_pull_file_runs_the_course_images_the_profile_layers_name(profiled):
    out, made, _ = profiled
    pulled = (out / "compose.pull.yaml").read_text(encoding="utf-8")
    assert made.names.runner in pulled and made.names.editor in pulled


def test_a_profile_that_names_a_runner_only_builds_the_editor_layer_on_the_plain_base(tmp_path):
    only_runner = profile_lock()
    del only_runner["profile"]["editor"]
    _, made = export(tmp_path, parsed(only_runner))
    assert made.names.runner_base.endswith(f"{RUNNER_TAG}@{THREES}")
    assert made.names.editor_base == parsed(lock()).editor.reference
    assert made.names.editor.endswith("-" + "2" * bases.KEY_DIGITS)


def test_a_profile_the_toolchain_does_not_have_is_refused_by_the_toolchain_s_answer(tmp_path):
    with pytest.raises(vendor.VendorRefused, match="refused profile claude-sdks"):
        export(tmp_path, parsed(profile_lock()), run=answered(refuse=True))
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("kind", ["runner", "editor"])
def test_a_profile_tag_the_toolchain_does_not_compute_is_refused_before_a_file_is_written(
    tmp_path, kind
):
    stale = profile_lock()
    stale["profile"][kind] = {**stale["profile"][kind], "tag": "stale"}
    refusal = f"the {kind} of profile {NAME!r} is locked at tag stale"
    with pytest.raises(bases.BasesRefused, match=refusal):
        export(tmp_path, parsed(stale))
    assert not (tmp_path / "out").exists()


def test_a_lock_that_names_no_profile_for_a_course_that_declares_one_is_refused(tmp_path):
    with pytest.raises(bases.BasesRefused, match="names no profile"):
        export(tmp_path, parsed(lock()))


def test_a_lock_naming_a_profile_the_course_does_not_declare_is_refused(tmp_path):
    with pytest.raises(bases.BasesRefused, match="declares no profile"):
        export(tmp_path, parsed(profile_lock()), declared=without_profile(tmp_path))
    other = profile_lock(name="other")
    other["profile"]["runner"]["image"] = bases.profile_image("runner", "other")
    del other["profile"]["editor"]
    with pytest.raises(bases.BasesRefused, match="names profile 'other'"):
        export(tmp_path, parsed(other), name="other")


def test_a_course_that_declares_a_profile_is_never_exported_self_contained(tmp_path):
    with pytest.raises(vendor.VendorRefused, match="export it thin"):
        export(tmp_path, None)
    assert not (tmp_path / "out").exists()


def test_the_declared_runtimes_that_the_profile_layers_on_are_the_toolchain_s_to_judge(tmp_path):
    """A course lacking runtimes the profile layers on is refused by the toolchain's answer."""
    refusing = answered(refuse=True)
    with pytest.raises(vendor.VendorRefused):
        export(tmp_path, parsed(profile_lock()), run=refusing)


def test_the_profile_entry_changes_no_file_a_course_without_one_writes(tmp_path):
    """The same corpus exported with and without a profile differs in the profile's names alone.

    ⭐ Only the compose files and the release record name an image a layer starts from; every
    other file of the tree, the site's recipe and the runner's among them, is the same bytes.
    """
    bare, _ = export(tmp_path, parsed(lock()), declared=without_profile(tmp_path), name="bare")
    profiled_out, _ = export(tmp_path, parsed(profile_lock()), name="with")
    kept = {p.relative_to(bare).as_posix() for p in bare.rglob("*") if p.is_file()}
    kept_with = {
        p.relative_to(profiled_out).as_posix() for p in profiled_out.rglob("*") if p.is_file()
    }
    assert kept == kept_with
    for one in sorted(kept - {"corpus.json", "compose.yaml", "compose.pull.yaml",
                              ".studyforge/release.json"}):
        assert (bare / one).read_bytes() == (profiled_out / one).read_bytes(), one
