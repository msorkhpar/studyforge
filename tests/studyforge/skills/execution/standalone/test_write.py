"""Mirror of `src/studyforge/skills/execution/standalone/write.py` (R12).

⭐ End to end on the runnable fixture: a git checkout of it, with the two tags
its execution records, released against a synthetic toolchain that answers as
the real one does. ⛔ The manifest is read against the files actually on disk,
so a written file it forgot, or a listed file nobody wrote, turns it red.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from studyforge.skills.execution.standalone import (
    closure,
    compose,
    images,
    learner,
    pages,
    split,
    write,
)
from tests.studyforge.execute.runnable import fixture_copy
from tests.studyforge.skills.execution.standalone.test_compose import plan
from tests.studyforge.skills.execution.standalone.test_pages import problems
from tests.studyforge.skills.execution.standalone.test_vendor import (
    TAGS,
    answering,
    course,
    toolchain,
)

#: ⛔ A placeholder identity: the fixture's commit is nobody's.
GIT = ["git", "-c", "user.name=Example", "-c", "user.email=contact@example.com"]


def git(argv, cwd):
    """A real `run` for `git`: the caller's side of `split.Run`, as a person would write it."""
    done = subprocess.run(argv, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return done.returncode, done.stdout


def answered(tags=TAGS):
    """`git` answered for real, the toolchain's builds answered by the synthetic checkout."""
    fake = answering(tags)
    return lambda argv, cwd: git(argv, cwd) if argv[0] == "git" else fake(argv, cwd)


def checkout(tmp_path: Path) -> Path:
    """The runnable fixture as a one-commit git checkout recording the primed tags."""
    root = course(fixture_copy(tmp_path / "course"))
    subprocess.run([*GIT, "init", "-q"], cwd=root, check=True)
    subprocess.run([*GIT, "add", "-A"], cwd=root, check=True)
    subprocess.run([*GIT, "commit", "-q", "-m", "fixture"], cwd=root, check=True)
    return root


@pytest.fixture(scope="module")
def released(tmp_path_factory) -> tuple[Path, write.Released]:
    where = tmp_path_factory.mktemp("release")
    out = where / "learner"
    made = write.release(
        checkout(where),
        out,
        toolchain=toolchain(where / "tc"),
        platform="linux/amd64",
        run=answered(),
    )
    return out, made


def on_disk(out: Path) -> list[str]:
    return sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())


def test_the_manifest_lists_exactly_the_files_the_tree_holds(released):
    out, made = released
    listed = json.loads((out / write.MANIFEST).read_text(encoding="utf-8"))["keeps"]
    assert listed == on_disk(out)
    assert write.kept_paths(made) == listed


def test_a_file_written_behind_the_manifest_s_back_would_be_seen(tmp_path, monkeypatch):
    real = write._ignore_env
    monkeypatch.setattr(write, "_ignore_env", lambda path: real(path) and False)
    out = tmp_path / "learner"
    write.release(
        checkout(tmp_path),
        out,
        toolchain=toolchain(tmp_path / "tc"),
        platform="linux/amd64",
        run=answered(),
    )
    listed = json.loads((out / write.MANIFEST).read_text(encoding="utf-8"))["keeps"]
    assert listed != on_disk(out)


def test_the_tree_carries_the_course_the_runtime_the_toolchain_and_both_compose_files(released):
    out, made = released
    for one in (
        "corpus.json",
        "compose.yaml",
        "compose.pull.yaml",
        "course.env",
        "README.md",
        ".dockerignore",
        f"{compose.TOOLCHAIN}/docker/minimal/Dockerfile",
        f"{compose.IMAGES}/serve/Dockerfile",
        f"{compose.IMAGES}/site/Dockerfile",
        f"{compose.IMAGES}/runner/Dockerfile",
        f"{compose.NO_PRIME}/README",
    ):
        assert (out / one).is_file(), one
    library = out / compose.IMAGES / "serve" / "library"
    assert (library / closure.PACKAGE / closure.STAMP).read_text(encoding="utf-8").strip()
    assert not (library / "studyforge" / "skills").exists()
    assert {v.path for v in made.verdicts if v.verdict == split.KEEP} >= {"corpus.json", "practice"}


def test_the_learner_s_gitignore_ignores_their_own_settings(released):
    out, _ = released
    assert ".env" in (out / ".gitignore").read_text(encoding="utf-8").splitlines()


def test_a_target_that_is_not_empty_is_refused(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "left.txt").write_text("x", encoding="utf-8")
    with pytest.raises(write.ReleaseRefused, match="not empty"):
        write.release(tmp_path, out, toolchain=tmp_path, platform="linux/amd64", run=answered())


def test_a_course_that_declares_no_runtime_is_refused(tmp_path):
    root = checkout(tmp_path)
    document = json.loads((root / "corpus.json").read_text(encoding="utf-8"))
    document["runtimes"] = []
    (root / "corpus.json").write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(write.ReleaseRefused, match="no runtime"):
        write.release(
            root,
            tmp_path / "out",
            toolchain=toolchain(tmp_path / "tc"),
            platform="linux/amd64",
            run=answered(),
        )


#: ⛔ Every account an exported file may name: the variable, its placeholder, the local default.
ALLOWED_ACCOUNTS = {images.NAMESPACE_DEFAULT, learner.NAMESPACE_PLACEHOLDER, ""}
ACCOUNT_USES = re.compile(rf"{images.NAMESPACE_VARIABLE}(?::-|=)([^}}\s]*)")
REGISTRY_HOST = re.compile(r"(?i)\b(?:docker\.io|index\.docker\.io|hub\.docker\.com)\b")


def account_literals(out: Path) -> list[str]:
    """Every account an exported file names other than the allowed ones, or a registry host."""
    found = []
    for path in sorted(out.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        text = path.read_bytes().decode("utf-8", errors="ignore")
        name = path.relative_to(out).as_posix()
        found += [
            f"{name}: {m.group(1)}"
            for m in ACCOUNT_USES.finditer(text)
            if m.group(1) not in ALLOWED_ACCOUNTS
        ]
        found += [f"{name}: {m.group(0)}" for m in REGISTRY_HOST.finditer(text)]
    return found


def test_no_exported_file_names_a_docker_hub_account(released):
    out, _ = released
    assert account_literals(out) == []


def test_an_exported_file_that_named_an_account_would_be_caught(released, tmp_path):
    out, _ = released
    copy = tmp_path / "copy"
    shutil.copytree(out, copy)
    with (copy / "compose.pull.yaml").open("a", encoding="utf-8") as one:
        one.write(f"# ${{{images.NAMESPACE_VARIABLE}:-some-account}}\n")
    (copy / "course.env").write_text(f"{images.NAMESPACE_VARIABLE}=some-account\n")
    assert len(account_literals(copy)) == 2


def test_the_exported_pull_file_has_no_default_account_and_course_env_leaves_it_empty(released):
    out, _ = released
    pulled = (out / "compose.pull.yaml").read_text(encoding="utf-8")
    assert f"${{{images.NAMESPACE_VARIABLE}:-" not in pulled
    assert f"${{{images.NAMESPACE_VARIABLE}:?" in pulled
    built = (out / "compose.yaml").read_text(encoding="utf-8")
    assert f"${{{images.NAMESPACE_VARIABLE}:-{images.NAMESPACE_DEFAULT}}}/" in built
    settings = (out / "course.env").read_text(encoding="utf-8").splitlines()
    assert f"{images.NAMESPACE_VARIABLE}=" in settings


def rendered_pair() -> tuple[str, str]:
    """Both compose files, as the synthetic plan renders them."""
    return compose.render(plan())


def pictures(where: Path, *names: str, size: int = 2048) -> Path:
    """A directory of README pictures, each `size` bytes of nothing in particular."""
    where.mkdir(parents=True, exist_ok=True)
    for name in names:
        (where / name).write_bytes(b"\0" * size)
    return where


def release_with(
    tmp_path: Path, shots: Path, preview_to: Path | None = None
) -> tuple[Path, write.Released]:
    out = tmp_path / "learner"
    made = write.release(
        checkout(tmp_path),
        out,
        toolchain=toolchain(tmp_path / "tc"),
        platform="linux/amd64",
        screenshots=shots,
        preview_to=preview_to,
        run=answered(),
    )
    return out, made


@pytest.fixture(scope="module")
def pictured(tmp_path_factory) -> tuple[Path, write.Released]:
    where = tmp_path_factory.mktemp("pictured")
    return release_with(where, pictures(where / "shots", "index.webp", "lesson.png", "quiz.webp"))


def relative_links(text: str) -> list[str]:
    """Every relative link and image target of a Markdown text, without its anchor."""
    found = re.findall(r"\]\(([^)\s]+)\)", text)
    return [one.split("#")[0] for one in found if not re.match(r"[a-z]+:|#", one)]


def test_every_relative_link_and_image_of_the_readme_reaches_a_file_of_the_tree(pictured):
    out, _ = pictured
    text = (out / "README.md").read_text(encoding="utf-8")
    links = relative_links(text)
    assert len(links) >= 3, "born vacuous: the README links almost nothing"
    assert [one for one in links if not (out / one).exists()] == []


def test_a_readme_link_to_a_file_the_tree_does_not_hold_would_be_caught(pictured):
    out, _ = pictured
    planted = (out / "README.md").read_text(encoding="utf-8") + "\n[gone](docs/gone.md)\n"
    assert [one for one in relative_links(planted) if not (out / one).exists()] == ["docs/gone.md"]


def test_the_pictures_are_copied_beside_the_build_files_listed_and_shown_in_the_readme(pictured):
    out, made = pictured
    shown = sorted(
        re.findall(r"!\[[^\]]+\]\(([^)]+)\)", (out / "README.md").read_text(encoding="utf-8"))
    )
    # ⭐ A picture stands beside its feature: the fixture has no quiz, so the quiz picture
    # is kept in the tree and the README shows the two the course can use.
    assert shown == [f"{compose.IMAGES}/readme/index.webp", f"{compose.IMAGES}/readme/lesson.png"]
    assert (out / compose.IMAGES / "readme" / "quiz.webp").is_file()
    listed = json.loads((out / write.MANIFEST).read_text(encoding="utf-8"))["keeps"]
    assert set(shown) <= set(listed) and listed == on_disk(out)
    assert set(shown) <= set(write.kept_paths(made))


def test_no_image_build_context_and_no_site_layer_carries_the_pictures():
    ignored = images.DOCKERIGNORE.splitlines()
    assert compose.IMAGES in ignored, "the site and runner contexts are the tree, minus the images"
    built, pulled = rendered_pair()
    assert f"{compose.IMAGES}/readme" not in built + pulled


def test_the_readme_states_the_counts_of_the_tree_it_sits_in(pictured):
    from studyforge.skills.execution.standalone.facts import read

    out, _ = pictured
    text = (out / "README.md").read_text(encoding="utf-8")
    counted = read(out)
    assert counted.units and f"{counted.units} unit" in text
    assert counted.practices is None or f"{counted.practices} practice" in text


@pytest.mark.parametrize(
    ("names", "size", "match"),
    [
        (("cover.png",), 10, "not a picture the README shows"),
        (("index.gif",), 10, "not a picture the README shows"),
        (("index.png", "index.webp"), 10, "two pictures"),
        (("index.png",), write.SHOT_MAX_BYTES + 1, "over"),
        (
            ("index.png", "lesson.png", "quiz.png", "practice.png", "example.png"),
            150 * 1024,
            "together",
        ),
    ],
)
def test_a_picture_the_readme_does_not_show_or_that_is_too_big_is_refused(
    tmp_path, names, size, match
):
    shots = pictures(tmp_path / "shots", *names, size=size)
    with pytest.raises(write.ReleaseRefused, match=match):
        release_with(tmp_path, shots)


def test_a_tree_released_with_no_pictures_carries_none_and_links_none(released):
    out, _ = released
    assert not (out / compose.IMAGES / "readme").exists()
    assert "![" not in (out / "README.md").read_text(encoding="utf-8")


def test_the_release_writes_the_preview_beside_it_when_asked(tmp_path):
    root = checkout(tmp_path)
    (root / "index.html").write_text(
        '<!doctype html><html><head></head><body><a href="#c">c</a></body></html>', encoding="utf-8"
    )
    subprocess.run([*GIT, "add", "-A"], cwd=root, check=True)
    subprocess.run([*GIT, "commit", "-q", "-m", "index"], cwd=root, check=True)
    out = tmp_path / "learner"
    made = write.release(
        root,
        out,
        toolchain=toolchain(tmp_path / "tc"),
        platform="linux/amd64",
        preview_to=tmp_path / "site",
        run=answered(),
    )
    assert made.previewed is not None and (tmp_path / "site" / "index.html").is_file()
    assert not (tmp_path / "site" / ".studyforge").exists()
    assert (
        "README.md" not in made.previewed.files and not (tmp_path / "site" / "README.md").exists()
    )
    assert not (out / "site").exists()


def test_the_tree_carries_the_pages_workflow_and_its_builder_and_the_manifest_lists_them(released):
    out, made = released
    manifest = json.loads((out / write.MANIFEST).read_text(encoding="utf-8"))
    assert (out / pages.WORKFLOW).read_text(encoding="utf-8") == pages.workflow()
    assert problems((out / pages.WORKFLOW).read_text(encoding="utf-8")) == []
    for where, data in pages.builder().items():
        assert (out / where).read_bytes() == data, where
    assert {pages.WORKFLOW, *pages.builder()} <= set(manifest["keeps"])
    kept = {v["path"]: v for v in manifest["verdicts"]}[".github"]
    assert kept["verdict"] == split.KEEP and "hosting infrastructure" in kept["why"]


def test_a_workflow_the_manifest_forgot_would_be_seen(released):
    out, _ = released
    listed = json.loads((out / write.MANIFEST).read_text(encoding="utf-8"))["keeps"]
    assert [one for one in listed if one != pages.WORKFLOW] != on_disk(out)


def test_the_export_names_no_owner_in_anything_it_wrote_under_github(released):
    out, _ = released
    for one in (out / ".github").rglob("*"):
        if one.is_file():
            assert not re.search(r"/home/|[\w.+-]+@[\w-]+\.[a-z]{2,}", one.read_text("utf-8")), one


def test_the_workflow_changes_no_image_tag_and_no_compose_file(released):
    out, made = released
    assert ".github" not in images.DOCKERIGNORE
    text = (out / "compose.yaml").read_text(encoding="utf-8") + (
        out / "compose.pull.yaml"
    ).read_text(encoding="utf-8")
    assert ".github" not in text and "pages.yml" not in text


def test_a_course_that_tracks_the_workflow_the_export_writes_is_refused(tmp_path):
    root = checkout(tmp_path)
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / pages.WORKFLOW).write_text("name: mine\n", encoding="utf-8")
    subprocess.run([*GIT, "add", "-A"], cwd=root, check=True)
    subprocess.run([*GIT, "commit", "-q", "-m", "workflow"], cwd=root, check=True)
    with pytest.raises(write.ReleaseRefused, match="writes itself"):
        write.release(
            root,
            tmp_path / "learner",
            toolchain=toolchain(tmp_path / "tc"),
            platform="linux/amd64",
            run=answered(),
        )
