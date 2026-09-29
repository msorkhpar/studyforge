"""Mirror of `src/studyforge/skills/execution/standalone/images.py` (R12)."""

from __future__ import annotations

import re

from studyforge.skills.execution.siteimage import BASE
from studyforge.skills.execution.standalone import images

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
    assert made.site == "a-course-site:c0ffee-${COURSE_NARRATION:-without-narration}"
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
