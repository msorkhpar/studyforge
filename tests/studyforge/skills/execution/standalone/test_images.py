"""Mirror of `src/studyforge/skills/execution/standalone/images.py` (R12)."""

from __future__ import annotations

import re
import shutil
import subprocess

from studyforge.skills.execution.siteimage import BASE
from studyforge.skills.execution.standalone import bases, images
from tests.studyforge.skills.execution.standalone.test_bases import lock, parsed

BUILDS = {
    "runner": {"tag": "example/runner:java-maven-amd64-0123456789ab"},
    "editor": {"tag": "example/editor:java-maven-amd64-ba9876543210"},
}


def names() -> images.Names:
    return images.names_for(slug="a-course", course="c0ffee", serve="0.1.0-abc", builds=BUILDS)


def test_the_shared_bases_keep_the_toolchains_tag_so_every_course_names_them_alike():
    made = names()
    assert made.runner_base == "studyforge-runner:java-maven-amd64-0123456789ab"
    assert made.editor_base == "studyforge-editor:java-maven-amd64-ba9876543210"
    assert made.serve == "studyforge-serve:0.1.0-abc"
    other = images.names_for(slug="b-course", course="d00d", serve="0.1.0-abc", builds=BUILDS)
    assert (other.serve, other.runner_base, other.editor_base) == (
        made.serve,
        made.runner_base,
        made.editor_base,
    )


def test_the_course_images_carry_the_course_and_the_site_its_variant():
    made = names()
    inputs = images.site_inputs("a-course", "0.1.0-abc")
    assert made.site == f"a-course-site:c0ffee-{inputs}-${{COURSE_NARRATION:-without-narration}}"
    assert re.fullmatch(r"[0-9a-f]{12}", inputs)
    assert made.runner == "a-course-runner:c0ffee"
    assert made.editor == "a-course-editor:c0ffee"


def test_every_name_is_qualified_by_a_placeholder_namespace_never_an_account():
    assert images.qualified("x:1") == "${STUDYFORGE_NAMESPACE:-studyforge-local}/x:1"
    assert images.NAMESPACE_DEFAULT == "studyforge-local"


def test_the_serving_base_is_the_pinned_python_and_the_vendored_library_alone():
    text = images.serve_dockerfile(commit="c" * 40, version="0.1.0")
    assert f"FROM {BASE}\n" in text
    assert re.search(r"@sha256:[0-9a-f]{64}", BASE)
    assert "COPY library/ /opt/studyforge/library/" in text
    assert 'ENTRYPOINT ["python3", "-m", "studyforge.cli"]' in text
    assert text.count("FROM ") == 1


def test_the_site_has_both_variants_and_only_the_voiced_one_carries_clips():
    text = images.site_dockerfile("a-course")
    silent, voiced = text.split(f"AS {images.NARRATIONS[1]}", 1)
    assert f"AS {images.NARRATIONS[0]}" in silent
    assert "--exclude='./.studyforge/*/audio'" in silent
    assert "-name audio" in voiced
    assert f"sha256sum -c --quiet {images.CLIPS}" in voiced


def test_the_progress_store_is_made_in_the_image_so_its_volume_is_seeded_as_the_learner(tmp_path):
    silent = images.site_dockerfile("a-course").split(f"AS {images.NARRATIONS[1]}", 1)[0]
    made = silent.index(f"mkdir -p /corpus/{images.PROGRESS}")
    assert images.PROGRESS == ".studyforge/progress"
    assert made < silent.index(f"chown -R {images.RUNS_AS} /corpus")


def test_a_voiced_site_that_skipped_the_checksums_would_be_seen():
    planted = images.site_dockerfile("a-course").replace("sha256sum -c", "true")
    assert "sha256sum -c" not in planted.split(f"AS {images.NARRATIONS[1]}", 1)[1]


def test_the_course_runner_bakes_the_run_service_and_runs_it():
    text = images.runner_dockerfile("a-course")
    assert "FROM ${RUNNER_PRIMED}" in text
    assert f"COPY {images.RUNSERVICE} " in text
    assert '"perl"' in text


def test_a_course_with_its_own_npm_packages_installs_them_offline_in_its_runner_at_build_time():
    # ⚠️ Measured: an example's Run failed with "Cannot find package '@anthropic-ai/sdk'": the
    # copy of the course's code holds no node_modules, and the runner has no network.
    text = images.runner_dockerfile("a-course", packages=True)
    lines = text.splitlines()
    copy = lines.index("COPY package.json package-lock.json /work/")
    install = lines.index(f"RUN cd /work && {images.PACKAGE_INSTALL}")
    assert copy < install < lines.index("WORKDIR /work")
    assert "--offline" in images.PACKAGE_INSTALL.split()
    assert "--ignore-scripts" in images.PACKAGE_INSTALL.split()


def test_a_course_without_npm_packages_has_the_runner_it_had():
    # ⛔ Byte for byte: no package line, and the default is the file it always was.
    text = images.runner_dockerfile("a-course")
    assert text == images.runner_dockerfile("a-course", packages=False)
    assert "npm" not in text and "package.json" not in text


def test_the_site_context_leaves_out_the_build_files_and_the_learners_state_and_keeps_clips():
    ignored = images.DOCKERIGNORE.splitlines()
    for gone in (".git", ".env", ".studyforge/images", ".studyforge/progress", "compose.yaml"):
        assert gone in ignored, gone
    assert not any("audio" in one for one in ignored)
    assert "!.studyforge/execution/code/.gitignore" in ignored


def test_the_authored_exercises_and_scripts_never_enter_an_images_build_context():
    ignored = images.DOCKERIGNORE.splitlines()
    assert "exercises" in ignored and "scripts" in ignored


def test_a_context_that_let_the_exercises_in_would_be_caught():
    planted = [one for one in images.DOCKERIGNORE.splitlines() if one != "exercises"]
    assert "exercises" not in planted


PAGE = '<p data-audio="audio/a-0123abcd.mp3">One</p><li data-audio="">Two</li><p>Three</p>'


def stripped(tmp_path, command):
    """Run the site's strip step over a copy of one page, as the image build would."""
    (tmp_path / "unit.html").write_text(PAGE, encoding="utf-8")
    sh = command.replace(images.CORPUS, str(tmp_path))
    subprocess.run(["sh", "-c", sh], check=True)
    return (tmp_path / "unit.html").read_text(encoding="utf-8")


def test_a_site_with_no_clips_carries_no_reference_to_one(tmp_path):
    # ⭐ A page naming a clip that no image holds asks for it, and the browser
    # logs a 404 on every page. The build removes the reference where it removes the clips.
    assert shutil.which("sed"), "the strip step is sed; this test runs where the build does"
    silent = images.site_dockerfile("a-course").split(f"AS {images.NARRATIONS[1]}", 1)[0]
    assert images.STRIP_CLIPS in silent
    assert stripped(tmp_path, images.STRIP_CLIPS) == "<p>One</p><li>Two</li><p>Three</p>"


def test_the_voiced_site_keeps_the_references_its_pages_probe():
    voiced = images.site_dockerfile("a-course").split(f"AS {images.NARRATIONS[1]}", 1)[1]
    assert "data-audio" not in voiced


def test_a_silent_site_that_kept_the_references_would_be_seen():
    planted = images.site_dockerfile("a-course").replace(images.STRIP_CLIPS, "true")
    silent = planted.split(f"AS {images.NARRATIONS[1]}", 1)[0]
    assert "sed -i" not in silent


def test_the_voiced_sites_clips_and_their_owner_are_one_layer():
    """⛔ A copy and a later `chown` in another `RUN` stores every clip twice."""
    voiced = images.site_dockerfile("a-course").split(f"AS {images.NARRATIONS[1]}", 1)[1]
    runs = [one for one in voiced.split("\nRUN ")[1:]]
    assert len(runs) == 1
    assert "cp -R" in runs[0] and f"chown -R {images.RUNS_AS} /corpus" in runs[0]
    assert "COPY" not in voiced


def test_the_voiced_site_is_not_built_on_the_silent_one():
    text = images.site_dockerfile("a-course")
    assert f"FROM {images.NARRATIONS[0]}" not in text
    assert text.count("FROM ${SERVE_BASE} AS ") == 2


def _tree(root):
    """A build context holding clips under both placements, and a course's own `audio/` folders."""
    files = [
        ".studyforge/01-basics/audio/u1/a.mp3",  # a `tree` corpus's clip
        ".studyforge/01-basics/unit.html",
        "src/study/audio/u2/b.mp3",  # a `sibling` corpus's clip
        "src/study/audio/u2/c.mp3",
        "src/study/u2.unit.html",
        "src/audio/theme.mp3",  # the course's own material: never a clip
        "lessons/audio/README.md",
    ]
    for one in files:
        (root / one).parent.mkdir(parents=True, exist_ok=True)
        (root / one).write_bytes(b"x")
    return files


def _kept(root):
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())


def test_the_silent_site_leaves_the_clips_of_either_placement_out_and_keeps_the_rest(tmp_path):
    """⛔ The `tree` rule alone shipped a sibling corpus's clips in the site with no narration."""
    text = images.site_dockerfile("a-course")
    silent = text.split(f"AS {images.NARRATIONS[1]}", 1)[0]
    assert images.CLIP_EXCLUDES in silent
    context, out = tmp_path / "context", tmp_path / "out"
    _tree(context)
    out.mkdir()
    sh = f"tar -C {context} --exclude=./.git {images.CLIP_EXCLUDES} -cf - . | tar -C {out} -xf -"
    subprocess.run(["sh", "-c", sh], check=True)
    assert _kept(out) == [
        ".studyforge/01-basics/unit.html",
        "lessons/audio/README.md",
        "src/audio/theme.mp3",
        "src/study/u2.unit.html",
    ]


def test_the_voiced_site_finds_the_clip_directories_of_either_placement_and_no_other(tmp_path):
    voiced = images.site_dockerfile("a-course").split(f"AS {images.NARRATIONS[1]}", 1)[1]
    assert images.CLIP_FINDER in voiced
    context, out = tmp_path / "context", tmp_path / "out"
    _tree(context)
    loop = (
        f'{images.CLIP_FINDER} | while IFS= read -r dir; do mkdir -p "{out}/$dir"; '
        f'cp -R "$dir/." "{out}/$dir/"; done'
    )
    subprocess.run(["sh", "-c", f"cd {context}; {loop}"], check=True)
    assert _kept(out) == [
        ".studyforge/01-basics/audio/u1/a.mp3",
        "src/study/audio/u2/b.mp3",
        "src/study/audio/u2/c.mp3",
    ]


def test_the_site_tag_moves_when_the_vendored_library_does_and_only_then():
    # ⭐ A re-pushed site image under an unchanged tag would leave everyone who
    # pulled it on the stale one; the serving base's tag carries the library's digest.
    before = images.names_for(slug="a-course", course="c0ffee", serve="0.1.0-aaa", builds=BUILDS)
    after = images.names_for(slug="a-course", course="c0ffee", serve="0.1.0-bbb", builds=BUILDS)
    again = images.names_for(slug="a-course", course="c0ffee", serve="0.1.0-aaa", builds=BUILDS)
    assert before.site != after.site
    assert before.site == again.site
    # ⭐ The runner and the editor keep their tags: their inputs did not change.
    assert (before.runner, before.editor) == (after.runner, after.editor)


def test_the_site_tag_moves_when_the_sites_own_build_file_does(monkeypatch):
    before = images.site_inputs("a-course", "0.1.0-abc")
    monkeypatch.setattr(images, "DOCKERIGNORE", images.DOCKERIGNORE + "extra\n")
    assert images.site_inputs("a-course", "0.1.0-abc") != before


def test_the_self_contained_names_and_recipes_are_pinned():
    """⛔ Thin mode adds a path; it changes nothing the self-contained export writes."""
    import hashlib

    def digest(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    assert names() == images.names_for(
        slug="a-course", course="c0ffee", serve="0.1.0-abc", builds=BUILDS, bases=None
    )
    assert names().site == (
        "a-course-site:c0ffee-5afc2ae3d2fa-${COURSE_NARRATION:-without-narration}"
    )
    assert digest(images.site_dockerfile("a-course")) == (
        "b78156c3d6c16774eb40df138111eab553a39e396439f2efa51c8c4b56654669"
    )
    assert digest(images.runner_dockerfile("a-course")) == (
        "0ba7f1abd0a563e7f6f1bf81a9020196d3567fff3e5cd9832293993486d132ec"
    )
    assert digest(images.serve_dockerfile(commit="c", version="0.1.0")) == (
        "dba9e85da904b2b11abc81e1df19a4670e816222898568d95f3b030fc22ae348"
    )


def thin(**changes) -> images.Names:
    return images.names_for(
        slug="a-course", course="c0ffee", serve="", builds=BUILDS, bases=parsed(lock(**changes))
    )


def test_a_thin_export_names_each_base_by_tag_and_digest():
    made = thin()
    locked = parsed(lock())
    assert made.serve == locked.serve.reference
    assert made.runner_base == locked.runner.reference
    assert made.editor_base == locked.editor.reference
    assert "@sha256:" in made.serve and "@sha256:" in made.runner_base


def test_a_base_that_changes_names_a_new_course_image_and_only_its_own():
    before = thin()
    new_runner = dict(lock()["runner"], digest="sha256:" + "3" * 64)
    new_editor = dict(lock()["editor"], digest="sha256:" + "4" * 64)
    new_serve = dict(lock()["serve"], digest="sha256:" + "5" * 64)
    after_runner, after_editor, after_serve = (
        thin(runner=new_runner),
        thin(editor=new_editor),
        thin(serve=new_serve),
    )
    assert after_runner.runner != before.runner and after_runner.editor == before.editor
    assert after_editor.editor != before.editor and after_editor.runner == before.runner
    assert after_serve.site != before.site
    assert (after_serve.runner, after_serve.editor) == (before.runner, before.editor)
    assert before.runner == f"a-course-runner:c0ffee-{'1' * bases.KEY_DIGITS}"
    assert before.editor == f"a-course-editor:c0ffee-{'2' * bases.KEY_DIGITS}"


def test_a_thin_site_recipe_starts_from_the_published_base_by_tag_and_digest():
    base = parsed(lock()).serve
    text = images.site_dockerfile("a-course", base)
    account = f"${{{images.NAMESPACE_VARIABLE}:?{images.NAMESPACE_UNSET}}}"
    froms = [line for line in text.splitlines() if line.startswith("FROM ")]
    assert froms == [f"FROM {account}/{base.reference} AS {n}" for n in images.NARRATIONS]
    assert f"ARG {images.NAMESPACE_VARIABLE}\n" in text
    assert "SERVE_BASE" not in text and images.NAMESPACE_DEFAULT not in text
    assert " " not in account and images.NAMESPACE_VARIABLE in account


def test_a_thin_site_recipe_names_no_account_and_its_stages_are_the_self_contained_ones():
    base = parsed(lock()).serve
    thin_text = images.site_dockerfile("a-course", base)
    whole = images.site_dockerfile("a-course")
    body = lambda text: text.split("AS without-narration", 1)[1].split("FROM", 1)[0]  # noqa: E731
    assert body(thin_text) == body(whole)
    assert not re.search(r"(?i)docker\.io|hub\.docker", thin_text)


def test_the_site_tag_moves_with_the_serve_digest_and_with_the_thin_recipe():
    base = parsed(lock()).serve
    other = parsed(lock(serve=dict(lock()["serve"], digest="sha256:" + "5" * 64))).serve
    assert images.site_inputs("a", base.reference, base) != images.site_inputs(
        "a", other.reference, other
    )
    assert images.site_inputs("a", base.reference, base) != images.site_inputs("a", base.reference)
