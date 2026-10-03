"""Mirror of `src/studyforge/skills/execution/standalone/vendor.py` (R12).

⭐ The toolchain is a synthetic checkout: a `consuming.json` whose `builds`
block names a command, and a `run` that answers that command as the real one
does. ⛔ Nothing here needs the sibling on disk, so nothing here skips.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.skills.execution.standalone import vendor
from tests.studyforge.skills.execution import contracts
from tests.studyforge.skills.execution.standalone.test_compose import BUILDS

PRINTED_BY = [
    "python3",
    "consuming/builds.py",
    vendor.IMAGE_SLOT,
    "--runtimes",
    vendor.SET_SLOT,
    "--prime",
    "<a prime directory, for a course layer>",
]


PROFILE_TAG = {
    "profile_tag_api": vendor.PROFILE_TAG_API,
    "printed_by": [
        "python3", "docker/profile_packages/package_build.py", "--profile", "<profile>",
        "--image", "<runner|editor>", "--runtimes", vendor.SET_SLOT, "--print-tag",
        "--platform", "<platform>",
    ],
}


def toolchain(where: Path, **builds) -> Path:
    """A checkout whose contract declares `builds`, with one input root on disk."""
    document = contracts.editor_contract()
    document["builds"] = {"builds_api": vendor.BUILDS_API, "printed_by": PRINTED_BY, **builds}
    document["profile_tag"] = PROFILE_TAG
    where.mkdir(parents=True)
    (where / "consuming.json").write_text(json.dumps(document), encoding="utf-8")
    (where / "docker" / "minimal").mkdir(parents=True)
    (where / "docker" / "minimal" / "Dockerfile").write_text("FROM x\n", encoding="utf-8")
    (where / "docker" / "minimal" / "__pycache__").mkdir()
    (where / "docker" / "minimal" / "__pycache__" / "plan.cpython.pyc").write_bytes(b"\0")
    (where / ".dockerignore").write_text(".git\n", encoding="utf-8")
    return where


#: ⛔ A synthetic home path, assembled so no file carries one.
STRANGER = f"/home/{'somebodyelse'}/checkout"


def answering(tags: dict[str, str], asked: list[list[str]] | None = None, **extra):
    """A `run` that answers the build command as the toolchain would, and `git`."""

    def run(argv, cwd):
        if asked is not None:
            asked.append(list(argv))
        if argv[0] == "git":
            return 0, "c" * 40 + "\n"
        image = argv[2]
        primed = "--prime" in argv
        document = {
            **BUILDS[image],
            "builds_api": vendor.BUILDS_API,
            "image": image,
            "tag": tags[f"{image}{'+' if primed and '-' not in image else ''}"],
            "inputs": ["docker/minimal", ".dockerignore"],
            **extra,
        }
        return 0, json.dumps(document)

    return run


TAGS = {
    "runner": "t/runner:a",
    "editor": "t/editor:b",
    "runner-prime": "t/runner:a-prime-c",
    "editor-prime": "t/editor:b-prime-c",
    "runner+": "t/runner:primed",
    "editor+": "t/editor:primed",
}


def course(where: Path, runner: str = "t/runner:primed", editor: str = "t/editor:primed") -> Path:
    execution = where / ".studyforge" / "execution"
    execution.mkdir(parents=True)
    (execution / "runner.env").write_text(
        f"# a comment\nSTUDYFORGE_RUNNER_IMAGE={runner}\n", encoding="utf-8"
    )
    (execution / "editor.env").write_text(f"EDITOR_IMAGE={editor}\n", encoding="utf-8")
    return where


def test_the_four_builds_are_asked_with_the_set_the_platform_and_a_prime_only_for_a_layer(tmp_path):
    asked: list[list[str]] = []
    got = vendor.ask(
        toolchain(tmp_path / "tc"),
        ("java", "maven"),
        tmp_path / "prime",
        platform="linux/amd64",
        run=answering(TAGS, asked),
    )
    assert list(got.builds) == list(vendor.BUILDS)
    assert got.commit == "c" * 40
    assert got.inputs == (".dockerignore", "docker/minimal")
    builds = [one for one in asked if one[0] != "git"]
    assert all("java,maven" in one and one[-2:] == ["--platform", "linux/amd64"] for one in builds)
    assert ["--prime" in one for one in builds] == [False, False, True, True]


def test_a_checkout_that_computes_the_course_s_recorded_tags_is_the_pinned_one(tmp_path):
    vendor.pinned(
        course(tmp_path / "c"),
        toolchain(tmp_path / "tc"),
        ("java",),
        tmp_path / "p",
        platform="linux/amd64",
        run=answering(TAGS),
    )


def test_a_checkout_that_computes_another_tag_is_refused_by_name(tmp_path):
    with pytest.raises(vendor.VendorRefused, match="check out the toolchain commit"):
        vendor.pinned(
            course(tmp_path / "c", editor="t/editor:other"),
            toolchain(tmp_path / "tc"),
            ("java",),
            tmp_path / "p",
            platform="linux/amd64",
            run=answering(TAGS),
        )


def test_a_contract_with_no_builds_or_another_shape_is_refused(tmp_path):
    checkout = toolchain(tmp_path / "tc")
    document = json.loads((checkout / "consuming.json").read_text(encoding="utf-8"))
    document["builds"]["builds_api"] = 99
    (checkout / "consuming.json").write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(vendor.VendorRefused, match="shape"):
        vendor.ask(checkout, ("java",), tmp_path, platform="linux/amd64", run=answering(TAGS))


def test_a_build_the_toolchain_refuses_is_refused_with_its_reason(tmp_path):
    def refusing(argv, cwd):
        return 2, ""

    with pytest.raises(vendor.VendorRefused, match="refused the runner build \\(exit 2\\)"):
        vendor.ask(
            toolchain(tmp_path / "tc"), ("nope",), tmp_path, platform="linux/amd64", run=refusing
        )


def test_the_context_is_copied_as_bytes_without_what_an_interpreter_wrote(tmp_path):
    checkout = toolchain(tmp_path / "tc")
    written = vendor.copy(checkout, tmp_path / "out", ["docker/minimal", ".dockerignore"])
    assert written == (".dockerignore", "docker/minimal/Dockerfile")
    assert (tmp_path / "out" / "docker" / "minimal" / "Dockerfile").read_bytes() == b"FROM x\n"
    assert not (tmp_path / "out" / "docker" / "minimal" / "__pycache__").exists()


def test_an_input_the_toolchain_does_not_hold_is_refused(tmp_path):
    with pytest.raises(vendor.VendorRefused, match="does not hold"):
        vendor.copy(toolchain(tmp_path / "tc"), tmp_path / "out", ["lockdown"])


def test_what_a_build_says_beyond_the_kept_keys_is_dropped_unread(tmp_path):
    got = vendor.ask(
        toolchain(tmp_path / "tc"),
        ("java",),
        tmp_path,
        platform="linux/amd64",
        run=answering(TAGS, context=STRANGER),
    )
    assert all("context" not in build for build in got.builds.values())


def test_a_kept_key_that_carries_a_home_path_is_refused_by_the_gate(tmp_path):
    with pytest.raises(PersonalDataLeak):
        vendor.ask(
            toolchain(tmp_path / "tc"),
            ("java",),
            tmp_path,
            platform="linux/amd64",
            run=answering(TAGS, args={"HOME_DIR": STRANGER}),
        )


def test_the_unprimed_tags_of_a_set_are_asked_without_a_prime_and_read_past_unrelated_args(
    tmp_path,
):
    asked: list[list[str]] = []
    # A platform-tagged extension file name reads like an address; assembled, so no file holds one.
    vsix = {"FETCH": f"https://example.invalid/debugpy-1.0{'@'}linux-x64.vsix"}
    got = vendor.unprimed_tags(
        toolchain(tmp_path / "tc"),
        ("java", "node"),
        platform="linux/amd64",
        run=answering(TAGS, asked, args=vsix),
    )
    assert got == {"runner": "a", "editor": "b"}
    builds = [one for one in asked if one[0] != "git"]
    assert len(builds) == 2
    assert all("java,node" in one and "--prime" not in one for one in builds)
    # the tree-writing path reads the same file name past, and still gates every key
    vendor.ask(
        toolchain(tmp_path / "tc3"),
        ("java",),
        tmp_path,
        platform="linux/amd64",
        run=answering(TAGS, args=vsix),
    )
    address = {"FETCH": "contact " + "someone" + "@" + "registrable" + ".net"}
    with pytest.raises(PersonalDataLeak):
        vendor.ask(
            toolchain(tmp_path / "tc2"),
            ("java",),
            tmp_path,
            platform="linux/amd64",
            run=answering(TAGS, args=address),
        )


def test_a_toolchain_that_refuses_a_set_refuses_its_tags(tmp_path):
    with pytest.raises(vendor.VendorRefused, match="refused the runner build"):
        vendor.unprimed_tags(
            toolchain(tmp_path / "tc"),
            ("java",),
            platform="linux/amd64",
            run=lambda argv, cwd: (2, ""),
        )
