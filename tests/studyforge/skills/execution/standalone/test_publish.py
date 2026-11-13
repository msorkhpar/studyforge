"""The publishing hand-off prints commands; no docker runs here."""

import json
import subprocess

import pytest

from studyforge.skills.execution.standalone import images, publish

DIGEST = "sha256:" + "a" * 64
RELEASE = {
    "images": {
        "serve": "${STUDYFORGE_NAMESPACE:-studyforge-local}/studyforge-serve:1",
        "site": "${STUDYFORGE_NAMESPACE:-studyforge-local}/demo-site:abc-0123"
        "-${COURSE_NARRATION:-without-narration}",
        "runner": "${STUDYFORGE_NAMESPACE:-studyforge-local}/demo-runner:abc",
    },
    "bases": {
        "serve": {"image": "studyforge-serve", "tag": "1", "digest": DIGEST},
        "profile": {"name": "p", "runner": {"image": "r-p", "tag": "2", "digest": DIGEST}},
    },
}
#: The same release from a corpus that carries narration clips.
NARRATED = {**RELEASE, "keeps": ["README.md", images.CLIPS]}


def test_the_commit_sets_a_placeholder_author_on_the_command():
    argv = publish.commit_argv("msg")
    assert argv[:5] == ["git", "-c", "user.name=Example", "-c", "user.email=noreply@example.invalid"]
    steps = publish.fresh_tree_commands("main", "msg")
    assert steps[0][:2] == ["git", "init"] and steps[-1] == argv


def test_a_fresh_commit_uses_the_placeholder_not_the_machine_identity(tmp_path):
    env = {"HOME": str(tmp_path), "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
    (tmp_path / "f").write_text("x", encoding="utf-8")
    for argv in publish.fresh_tree_commands("main", "learner tree"):
        subprocess.run(argv, cwd=tmp_path, env=env, check=True)
    shown = subprocess.run(
        ["git", "log", "--format=%an <%ae>"], cwd=tmp_path, env=env, capture_output=True, text=True
    ).stdout
    assert shown.strip() == "Example <noreply@example.invalid>"


def test_images_come_from_the_manifest_not_a_fixed_count():
    assert publish.images_of(RELEASE) == [
        "demo-runner:abc",
        "demo-site:abc-0123-without-narration",
        "studyforge-serve:1",
    ]
    with pytest.raises(ValueError):
        publish.images_of({})


def test_the_pinned_digests_include_profile_images():
    assert publish.pinned_digests(RELEASE) == {"studyforge-serve:1": DIGEST, "r-p:2": DIGEST}


def _docker_lines(lines):
    return [line for line in lines if "docker" in line.split("|")[0]]


def test_the_build_sets_the_namespace_and_by_default_names_no_context():
    lines = publish.owner_commands(RELEASE, "ns-placeholder", "scratch")
    assert lines[0] == "set -e"
    assert lines[1] == (
        "STUDYFORGE_NAMESPACE=ns-placeholder COURSE_NARRATION=without-narration"
        " docker compose build"
    )
    docker = _docker_lines(lines)
    assert docker and all("--context" not in line for line in docker)
    assert all("desktop-linux" not in line for line in lines)


def test_a_named_context_reaches_every_docker_line():
    lines = publish.owner_commands(RELEASE, "ns", "scratch", context="remote-builder")
    docker = _docker_lines(lines)
    assert docker
    for line in docker:
        assert line.count("docker --context remote-builder ") == line.count("docker ")


def test_no_line_carries_an_unexpanded_or_quoted_image_name():
    for release in (RELEASE, NARRATED):
        for line in publish.owner_commands(release, "ns", "scratch"):
            assert "${" not in line and "COURSE_NARRATION:-" not in line
            assert "'ns/" not in line


def test_a_corpus_without_clips_publishes_only_the_site_without_narration():
    assert publish.editions(RELEASE) == ("without-narration",)
    lines = publish.owner_commands(RELEASE, "ns", "scratch")
    assert not any("with-narration" in line.replace("without-narration", "") for line in lines)
    assert "docker push ns/demo-site:abc-0123-without-narration" in lines


def test_a_corpus_with_clips_builds_scans_and_pushes_both_editions():
    assert publish.editions(NARRATED) == ("without-narration", "with-narration")
    assert publish.images_of(NARRATED) == [
        "demo-runner:abc",
        "demo-site:abc-0123-with-narration",
        "demo-site:abc-0123-without-narration",
        "studyforge-serve:1",
    ]
    lines = publish.owner_commands(NARRATED, "ns", "scratch")
    voiced_build = (
        "STUDYFORGE_NAMESPACE=ns COURSE_NARRATION=with-narration docker compose build site"
    )
    assert voiced_build in lines
    builds = [i for i, one in enumerate(lines) if " compose build" in one]
    scans = [i for i, one in enumerate(lines) if "studyforge.archive.scrub check" in one]
    pushes = [i for i, one in enumerate(lines) if " push " in one]
    assert len(builds) == 2 and max(builds) < min(scans)
    assert len(scans) == 4 and len(pushes) == 4 and max(scans) < min(pushes)
    for edition in publish.editions(NARRATED):
        assert f"docker push ns/demo-site:abc-0123-{edition}" in lines


def test_main_prints_the_list_and_takes_a_context(tmp_path, capsys):
    release = tmp_path / "release.json"
    release.write_text(json.dumps(NARRATED), encoding="utf-8")
    assert publish.main([str(release), "ns", "scratch"]) == 0
    plain = capsys.readouterr().out.splitlines()
    assert "docker push ns/demo-site:abc-0123-with-narration" in plain
    assert publish.main(["--context", "remote-builder", str(release), "ns", "scratch"]) == 0
    named = capsys.readouterr().out.splitlines()
    assert "docker --context remote-builder push ns/demo-site:abc-0123-with-narration" in named
    assert publish.main([str(release), "ns"]) == 2
    assert publish.main(["--context", str(release), "ns", "scratch"]) == 2


def test_scan_precedes_every_push_and_uses_the_shared_pattern_set():
    lines = publish.owner_commands(RELEASE, "ns", "scratch")
    pushes = [i for i, one in enumerate(lines) if " push " in one]
    scans = [i for i, one in enumerate(lines) if "studyforge.archive.scrub check" in one]
    assert len(scans) == 3 and len(pushes) == 3 and max(scans) < min(pushes)
    assert all("exit 1" in lines[i] for i in scans)


def test_digest_lines_follow_the_pushes_and_stop_on_a_mismatch():
    lines = publish.owner_commands(RELEASE, "ns", "scratch")
    checks = [i for i, one in enumerate(lines) if "digest mismatch" in one]
    assert len(checks) == 2 and min(checks) > max(i for i, o in enumerate(lines) if " push " in o)
    assert all("exit 1" in lines[i] and DIGEST in lines[i] for i in checks)


def test_digest_comparison_is_exact():
    assert publish.digest_matches(DIGEST, DIGEST + "\n")
    assert not publish.digest_matches(DIGEST, "sha256:" + "b" * 64)
    assert not publish.digest_matches("latest", "latest")
