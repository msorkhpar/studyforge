"""The publishing hand-off prints commands; no docker runs here."""

import subprocess

import pytest

from studyforge.skills.execution.standalone import publish

DIGEST = "sha256:" + "a" * 64
RELEASE = {
    "images": {
        "serve": "${STUDYFORGE_NAMESPACE:-studyforge-local}/studyforge-serve:1",
        "site": "${STUDYFORGE_NAMESPACE:-studyforge-local}/demo-site:abc",
        "runner": "${STUDYFORGE_NAMESPACE:-studyforge-local}/demo-runner:abc",
    },
    "bases": {
        "serve": {"image": "studyforge-serve", "tag": "1", "digest": DIGEST},
        "profile": {"name": "p", "runner": {"image": "r-p", "tag": "2", "digest": DIGEST}},
    },
}


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
        "demo-site:abc",
        "studyforge-serve:1",
    ]
    with pytest.raises(ValueError):
        publish.images_of({})


def test_the_pinned_digests_include_profile_images():
    assert publish.pinned_digests(RELEASE) == {"studyforge-serve:1": DIGEST, "r-p:2": DIGEST}


def test_every_docker_line_sets_the_context_and_the_build_sets_the_namespace():
    lines = publish.owner_commands(RELEASE, "ns-placeholder", "scratch")
    assert lines[0] == "set -e"
    assert lines[1].startswith("STUDYFORGE_NAMESPACE=ns-placeholder docker --context desktop-linux")
    for line in lines:
        if "docker" in line.split("|")[0]:
            assert "--context desktop-linux" in line


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
