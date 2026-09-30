"""The serving base image's recipe and its publish step, read as the data they are.

Mirrors `docker/serve/`. The image is what a course's site image starts `FROM`, so
this module keeps three promises: its tag is COMPUTED from its inputs, its publish
step takes the registry namespace from one environment variable and pushes only when
told to, and its recipe carries the served runtime and nothing else. No Docker is
started here; the recipe and the plan are read, and the publish step is driven with
a runner that records what it is asked to run.

Standard library only, plus the two scripts under test.
"""

from __future__ import annotations

import io
import re
import shutil
import sys
from pathlib import Path

import pytest

from tests.support import repository_root

SERVE = repository_root() / "docker" / "serve"
sys.path.insert(0, str(SERVE))
import build  # noqa: E402
import publish  # noqa: E402

from studyforge.skills.execution.siteimage import BASE  # noqa: E402
from studyforge.skills.execution.standalone import closure, images  # noqa: E402

NAMESPACE = "example/space"


class Recorder:
    """A `subprocess.run` stand-in that records what it was asked to run and succeeds."""

    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def __call__(self, step, **_kwargs):
        self.calls.append(list(step))
        return type("Done", (), {"returncode": 0})()


def publish_main(argv, env):
    """Drive `publish.main`; return its status, its stdout, and the runner's record."""
    out, run = io.StringIO(), Recorder()
    return publish.main(argv, env=env, run=run, out=out), out.getvalue(), run


def checkout_copy(tmp_path: Path) -> Path:
    """The parts of the checkout a plan reads, copied so a test may plant a change in them."""
    root = tmp_path / "checkout"
    shutil.copytree(
        repository_root() / "src", root / "src", ignore=shutil.ignore_patterns("__pycache__")
    )
    (root / "docker" / "serve").mkdir(parents=True)
    shutil.copyfile(SERVE / build.DOCKERFILE, root / "docker" / "serve" / build.DOCKERFILE)
    shutil.copyfile(repository_root() / "pyproject.toml", root / "pyproject.toml")
    return root


# --- the namespace ---------------------------------------------------------


@pytest.mark.parametrize(
    "env", [{}, {publish.NAMESPACE_VARIABLE: ""}, {publish.NAMESPACE_VARIABLE: "  "}]
)
def test_an_unset_or_empty_namespace_refuses_before_anything_is_planned_or_run(env):
    status, out, run = publish_main(["--push"], env)
    assert status == 2
    assert out == "" and run.calls == []


@pytest.mark.parametrize("bad", ["Upper", "has space", "-x", "a//b", "a;rm"])
def test_a_namespace_that_is_not_a_registry_namespace_refuses(bad):
    status, out, run = publish_main([], {publish.NAMESPACE_VARIABLE: bad})
    assert status == 2 and out == "" and run.calls == []


def test_the_namespace_is_read_from_the_one_variable_and_from_no_flag_or_default():
    source = (SERVE / "publish.py").read_text(encoding="utf-8")
    assert publish.NAMESPACE_VARIABLE == "STUDYFORGE_NAMESPACE"
    assert "--namespace" not in source and "docker login" not in source
    with pytest.raises(publish.Refused):
        publish.namespace({"TOOLCHAIN_NAMESPACE": NAMESPACE})


def test_no_registry_account_is_written_in_the_recipe_or_its_scripts():
    for name in ("Dockerfile", "build.py", "publish.py"):
        text = (SERVE / name).read_text(encoding="utf-8")
        assert not re.search(r"docker\.io/|ghcr\.io/|quay\.io/|\blogin\b.*\bdocker\b", text), name
        assert "studyforge-local" not in text, name


# --- the dry run and the push ----------------------------------------------


def test_a_dry_run_prints_the_exact_commands_and_runs_none_of_them():
    status, out, run = publish_main(
        ["--dry-run", "--push"], {publish.NAMESPACE_VARIABLE: NAMESPACE}
    )
    tag = build.planned().tag
    lines = out.splitlines()
    assert status == 0 and run.calls == []
    assert lines[:3] == [
        "python3 docker/serve/build.py",
        f"docker tag {tag} {NAMESPACE}/{tag}",
        f"docker push {NAMESPACE}/{tag}",
    ]
    assert "DIGEST" in lines[3]


def test_only_push_pushes_and_nothing_logs_in():
    env = {publish.NAMESPACE_VARIABLE: NAMESPACE}
    _, _, without = publish_main([], env)
    _, _, with_push = publish_main(["--push"], env)
    assert [call[:2] for call in without.calls] == [
        ["python3", "docker/serve/build.py"],
        ["docker", "tag"],
    ]
    assert [call[:2] for call in with_push.calls][-1] == ["docker", "push"]
    assert all("login" not in call for call in without.calls + with_push.calls)


def test_a_failing_step_stops_the_publish_with_its_status():
    def failing(step, **_kwargs):
        return type("Done", (), {"returncode": 3})()

    out = io.StringIO()
    status = publish.main(
        ["--push"], env={publish.NAMESPACE_VARIABLE: NAMESPACE}, run=failing, out=out
    )
    assert status == 3 and "docker push" not in out.getvalue()


# --- the tag ---------------------------------------------------------------


def test_the_tag_is_the_version_and_a_digest_of_the_inputs_and_is_stable():
    plan = build.planned()
    assert re.fullmatch(r"studyforge-serve:\d+\.\d+\.\d+-[0-9a-f]{64}", plan.tag)
    assert build.planned().tag == plan.tag
    assert plan.tag == f"{build.REPOSITORY}:{plan.version}-{plan.digest}"


def test_a_moved_library_byte_or_build_file_or_version_names_a_new_tag(tmp_path):
    root = checkout_copy(tmp_path)
    before = build.planned(root).tag
    assert before == build.planned().tag, "the same inputs name the same image in any checkout"
    served = root / "src" / build.planned(root).files[0]
    served.write_bytes(served.read_bytes() + b"\n# moved\n")
    after_library = build.planned(root).tag
    dockerfile = root / "docker" / "serve" / build.DOCKERFILE
    dockerfile.write_text(dockerfile.read_text(encoding="utf-8") + "# moved\n", encoding="utf-8")
    after_file = build.planned(root).tag
    pyproject = root / "pyproject.toml"
    pyproject.write_text(
        pyproject.read_text(encoding="utf-8").replace('version = "0.1.0"', 'version = "9.9.9"', 1)
    )
    after_version = build.planned(root).tag
    assert len({before, after_library, after_file, after_version}) == 4


def test_the_published_name_is_the_namespace_and_the_computed_tag():
    _, out, _ = publish_main(["--dry-run"], {publish.NAMESPACE_VARIABLE: NAMESPACE})
    assert f"{NAMESPACE}/{build.planned().tag}" in out


def test_no_tag_is_written_by_hand_in_the_recipe():
    text = (SERVE / "Dockerfile").read_text(encoding="utf-8")
    assert "studyforge-serve" not in text and ":latest" not in text
    assert re.findall(r"^FROM (\S+)", text, re.M) == [BASE]


# --- the recipe ------------------------------------------------------------


def test_the_recipe_is_the_pinned_python_the_library_and_the_entrypoint_the_site_uses():
    text = (SERVE / "Dockerfile").read_text(encoding="utf-8")
    generated = images.serve_dockerfile(commit="0" * 40, version="0")
    entrypoint = next(line for line in text.splitlines() if line.startswith("ENTRYPOINT"))
    assert entrypoint in generated.splitlines()
    env = next(line for line in text.splitlines() if line.startswith("ENV"))
    assert env in generated.splitlines()
    assert "COPY library/ /opt/studyforge/library/" in text.splitlines()
    assert [line for line in text.splitlines() if line.startswith("COPY")] == [
        "COPY library/ /opt/studyforge/library/"
    ]


def test_the_image_runs_unprivileged_and_needs_no_network():
    text = (SERVE / "Dockerfile").read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if not line.startswith("#")]
    assert lines[-2] == f"USER {images.RUNS_AS}" and lines[-1].startswith("ENTRYPOINT")
    assert not [line for line in lines if re.match(r"(RUN|ADD)\b", line)], (
        "a recipe that runs a command or adds a URL reaches for the network or installs at build"
    )


def test_the_staged_context_holds_the_served_runtime_and_no_course_and_no_clip(tmp_path):
    plan = build.planned()
    build.stage(plan, tmp_path)
    staged = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file())
    assert staged[0] == build.DOCKERFILE
    library = {name.removeprefix("library/") for name in staged[1:]}
    assert library == set(plan.files)
    assert not closure.forbidden(
        name.removesuffix(".py").replace("/", ".").removesuffix(".__init__")
        for name in library
        if name.endswith(".py")
    )
    assert not [name for name in library if "/audio/" in name or name.endswith((".mp3", ".ogg"))]
    assert all(name.startswith("studyforge/") for name in library)


def test_the_build_argv_names_the_computed_tag_and_the_version():
    plan = build.planned()
    command = build.argv(plan, Path("/path/to/context"), None, "never")
    assert command[:4] == ["docker", "build", "--tag", plan.tag]
    assert f"SERVE_VERSION={plan.version}" in command and "--pull=false" in command
