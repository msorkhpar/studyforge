"""The thin export of a course that declares live runs (R12).

⭐ Read against `compose.render`, `images.runner_dockerfile`, `learner.readme` and `split`:
a live course's export carries the live runner and the egress proxy in the compose profile
`live`, the scripts baked into images rather than bound from a checkout, and the examples the
live runner starts in. ⛔ A course that declares none is byte-identical to what it was.
"""

from __future__ import annotations

import pytest

from studyforge.skills.execution.standalone import compose, images, learner, live, split
from tests.studyforge.skills.execution.standalone.test_bases import lock, parsed
from tests.studyforge.skills.execution.standalone.test_compose import BUILDS, plan

HOST = "api.example.invalid"


def thin(**changes) -> compose.Plan:
    locked = parsed(lock())
    names = images.names_for(
        slug="a-course", course="c0ffee", serve="", builds=BUILDS, bases=locked
    )
    return plan(names=names, bases=locked, **changes)


def services(live: bool) -> dict:
    """The pull file's services, as the document `compose.render` handed to `emit`."""
    documents = []
    real = compose.emit
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            compose, "emit", lambda document: documents.append(document) or real(document)
        )
        compose.render(thin(live=(HOST, "EXAMPLE_API_KEY") if live else None))
    return documents[1]["services"]


def test_a_live_course_adds_a_runner_and_a_proxy_in_the_live_profile_only():
    found = services(True)
    for name in ("live", "egress"):
        assert found[name]["profiles"] == ["live"]
    assert found["live"]["environment"]["STUDYFORGE_LIVE_KEY_NAME"] == "EXAMPLE_API_KEY"
    assert found["egress"]["environment"]["EGRESS_ALLOW_HOST"] == HOST
    assert found["site"]["environment"]["STUDYFORGE_LIVE_SERVICE"] == "live"


def test_the_proxy_replaces_the_site_images_entrypoint_and_binds_no_checkout_file():
    found = services(True)
    assert found["egress"]["entrypoint"] == ["python3"]
    assert found["egress"]["command"] == ["/corpus/.studyforge/execution/egress.py"]
    for name in ("live", "egress"):
        for volume in found[name].get("volumes", []):
            assert not volume.startswith(("./", "/", "~")), volume


def test_the_live_runner_reaches_no_network_but_the_proxy_net_and_the_runs_net():
    found = services(True)
    assert sorted(found["live"]["networks"]) == ["live-net", "runs"]
    assert sorted(found["egress"]["networks"]) == ["live-net", "live-out"]


def test_a_course_that_declares_no_live_run_is_byte_identical():
    assert compose.render(thin()) == compose.render(thin(live=None))
    found = services(False)
    assert "live" not in found and "egress" not in found
    assert "STUDYFORGE_LIVE_SERVICE" not in found["site"]["environment"]


def test_the_live_runner_image_carries_its_script_and_the_examples_it_starts_in():
    text = images.runner_dockerfile("a-course", live=True, live_dirs=("examples",))
    assert "COPY .studyforge/execution/liverun.pl /opt/studyforge/liverun.pl" in text
    assert "COPY examples /work/examples" in text


def test_a_runner_image_without_live_is_what_it_was():
    plain = images.runner_dockerfile("a-course")
    assert "liverun" not in plain and "COPY examples" not in plain
    assert images.runner_dockerfile("a-course", live=False, live_dirs=("examples",)) == plain


def test_the_learner_readme_explains_the_live_profile_only_for_a_live_course():
    base = ("A Course", "a-course", 1, 2, "ns", False)
    assert "Live runs (optional)" not in learner.readme(learner.Course(*base))
    said = learner.readme(learner.Course(*base, live=(HOST, "EXAMPLE_API_KEY")))
    assert HOST in said and "--profile live" in said and "EXAMPLE_API_KEY" in said


def test_the_live_scripts_are_kept_in_the_export():
    assert split.EXECUTION_KEPT["liverun.pl"] and split.EXECUTION_KEPT["egress.py"]


def test_a_course_whose_build_sits_below_a_directory_keeps_that_directory():
    prime = ".studyforge/execution/prime/gradle"
    files = (
        f"{prime}/java/build.gradle.kts",
        f"{prime}/java/src/main/java/a/A.java",
        "examples/one/jvm/java/build.gradle.kts",
        "examples/one/jvm/java/src/main/java/a/A.java",
        "docs/notes/java/build.gradle.kts",
        "somewhere/readme.txt",
    )
    assert "examples" in split._code(files)
    assert "docs" not in split._code(files)
    assert "somewhere" not in split._code(files)


def test_a_manifest_names_the_directories_its_live_examples_run_from():
    class Example:
        def __init__(self, path):
            self.path = path

    class Block:
        examples = (
            Example("examples/a/b.py"),
            Example("examples/c/d.py"),
            Example("tools/e.py"),
            Example("loose.py"),
        )

    class Manifest:
        pass

    held = Manifest()
    held.live = Block()
    assert live.directories(held) == ("examples", "tools")
    held.live = None
    assert live.directories(held) == ()
