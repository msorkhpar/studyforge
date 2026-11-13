"""Mirror of `vendor.profile_tags` in `src/studyforge/skills/execution/standalone/vendor.py` (R12).

⭐ The toolchain is a synthetic checkout answering as the real one does; the profile is made up.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from studyforge.skills.execution.standalone import vendor
from tests.studyforge.skills.execution.standalone.test_vendor import PROFILE_TAG

RUNTIMES = ("java", "python")


def checkout_of(tmp_path, block=PROFILE_TAG):
    """A synthetic toolchain whose contract carries `block` as its `profile_tag`, or none."""
    document = {"consuming_api": 1, "provides": 6, "component": "code-server-toolchain"}
    if block is not None:
        document["profile_tag"] = block
    (tmp_path / "consuming.json").write_text(json.dumps(document), encoding="utf-8")
    return tmp_path


def answering(asked, code=0, printed="t/{image}-example-profile:{image}-tag\n"):
    def run(argv, cwd):
        asked.append((list(argv), cwd))
        image = argv[argv.index("--image") + 1] if "--image" in argv else "none"
        return code, printed.format(image=image)

    return run


def test_the_toolchain_is_asked_for_each_image_with_the_profile_the_set_and_the_platform(tmp_path):
    asked: list = []
    tags = vendor.profile_tags(
        checkout_of(tmp_path),
        "example-profile",
        RUNTIMES,
        platform="linux/amd64",
        run=answering(asked),
    )
    assert tags == {"runner": "runner-tag", "editor": "editor-tag"}
    assert [(argv[0], cwd) for argv, cwd in asked] == [(sys.executable, tmp_path)] * 2
    assert asked[0][0][1:] == [
        "docker/profile_packages/package_build.py",
        "--profile",
        "example-profile",
        "--image",
        "runner",
        "--runtimes",
        "java,python",
        "--print-tag",
        "--platform",
        "linux/amd64",
    ]
    assert asked[1][0][asked[1][0].index("--image") + 1] == "editor"


def test_a_profile_the_toolchain_refuses_is_refused_by_name_without_its_text(tmp_path):
    with pytest.raises(vendor.VendorRefused, match="refused profile example-profile .*exit 2"):
        vendor.profile_tags(
            checkout_of(tmp_path),
            "example-profile",
            RUNTIMES,
            platform="linux/amd64",
            run=answering([], code=2, printed="refused: some text\n"),
        )


@pytest.mark.parametrize("printed", ["\n", "no-colon\n", "repo:bad tag\n", "repo:\n"])
def test_an_answer_that_is_not_one_tag_is_refused(tmp_path, printed):
    with pytest.raises(vendor.VendorRefused, match="printed no tag"):
        vendor.profile_tags(
            checkout_of(tmp_path),
            "example-profile",
            RUNTIMES,
            platform="linux/amd64",
            run=answering([], printed=printed),
        )


def test_the_command_is_the_one_the_contract_names_not_one_written_here(tmp_path):
    asked: list = []
    named = dict(
        PROFILE_TAG,
        printed_by=[
            "python3",
            "elsewhere.py",
            "<platform>",
            "<profile>",
            "<runner|editor>",
            "<the declared set>",
        ],
    )
    vendor.profile_tags(
        checkout_of(tmp_path, named),
        "example-profile",
        RUNTIMES,
        platform="linux/arm64",
        run=answering(asked, printed="t/x:tag\n"),
    )
    assert asked[0][0][1:] == [
        "elsewhere.py",
        "linux/arm64",
        "example-profile",
        "runner",
        "java,python",
    ]


def test_a_toolchain_that_declares_no_profile_tag_is_refused_and_never_asked(tmp_path):
    asked: list = []
    with pytest.raises(vendor.VendorRefused, match="declares no profile_tag"):
        vendor.profile_tags(
            checkout_of(tmp_path, None),
            "example-profile",
            RUNTIMES,
            platform="linux/amd64",
            run=answering(asked),
        )
    assert asked == []


def without(slot):
    return [one for one in PROFILE_TAG["printed_by"] if one != slot]


@pytest.mark.parametrize(
    "block, match",
    [
        (dict(PROFILE_TAG, profile_tag_api=99), "shape this skill has not read"),
        (dict(PROFILE_TAG, printed_by="python3 x"), "not a command"),
        (dict(PROFILE_TAG, printed_by=without("<platform>")), "names no <platform> slot"),
        (dict(PROFILE_TAG, printed_by=without("<profile>")), "names no <profile> slot"),
    ],
)
def test_a_profile_tag_block_this_skill_cannot_fill_is_refused(tmp_path, block, match):
    with pytest.raises(vendor.VendorRefused, match=match):
        vendor.profile_tags(
            checkout_of(tmp_path, block),
            "example-profile",
            RUNTIMES,
            platform="linux/amd64",
            run=answering([]),
        )


def test_no_consuming_json_at_all_is_refused(tmp_path):
    with pytest.raises(vendor.VendorRefused, match="no consuming.json"):
        vendor.profile_tags(
            tmp_path, "example-profile", RUNTIMES, platform="linux/amd64", run=answering([])
        )


def test_the_provisional_constant_is_gone():
    assert not hasattr(vendor, "PROFILE_TAG_BY")


# ---------------------------------------------------------------------------
# `vendor.pinned` for a course that names a profile: its local record holds the profile's tags.
# ---------------------------------------------------------------------------


#: What `profile_check` returns for a course naming the profile, over the synthetic answers.
PROFILED = {
    "profile_declared": "example-profile",
    "profile_tags": {"runner": "runner-tag", "editor": "editor-tag"},
}


def test_a_profiled_course_with_no_prime_is_pinned_by_the_profile_tags_it_recorded(tmp_path):
    from tests.studyforge.skills.execution.standalone.test_vendor import course, toolchain

    asked: list = []
    vendor.pinned(
        course(
            tmp_path / "c",
            runner="t/runner-example-profile:runner-tag",
            editor="t/editor-example-profile:editor-tag",
        ),
        toolchain(tmp_path / "tc"),
        RUNTIMES,
        tmp_path / "no-prime",
        PROFILED,
        platform="linux/amd64",
        run=answering(asked),
    )
    assert asked == [], "the profile's tags were computed once, by profile_check"


@pytest.mark.parametrize(
    "runner",
    [
        "t/runner:primed",  # the plain base's, which lacks what the profile adds
        "t/runner-other-profile:runner-tag",  # another profile's
        "t/runner-example-profile:other-tag",  # a tag this checkout does not compute
    ],
)
def test_a_profiled_course_that_recorded_another_runner_is_refused(tmp_path, runner):
    from tests.studyforge.skills.execution.standalone.test_vendor import course, toolchain

    with pytest.raises(vendor.VendorRefused, match="profile runner.*re-onboard"):
        vendor.pinned(
            course(tmp_path / "c", runner=runner, editor="t/editor-example-profile:editor-tag"),
            toolchain(tmp_path / "tc"),
            RUNTIMES,
            tmp_path / "no-prime",
            PROFILED,
            platform="linux/amd64",
            run=answering([]),
        )


def test_a_profiled_course_with_a_prime_is_still_pinned_by_its_primed_base_tags(tmp_path):
    # ⭐ A profile and a prime do not combine in the local record, which refuses such a course,
    # so its recorded tags are its primed bases' and the export's course layer adds the profile.
    from tests.studyforge.skills.execution.standalone.test_vendor import TAGS, course, toolchain
    from tests.studyforge.skills.execution.standalone.test_vendor import answering as builds

    prime = tmp_path / "prime"
    (prime / "maven").mkdir(parents=True)
    (prime / "maven" / "pom.xml").write_text("<project/>\n", encoding="utf-8")
    vendor.pinned(
        course(tmp_path / "c"),
        toolchain(tmp_path / "tc"),
        RUNTIMES,
        prime,
        PROFILED,
        platform="linux/amd64",
        run=builds(TAGS),
    )


# ---------------------------------------------------------------------------
# `vendor.ask` for a course that names a profile and has no prime: no course layer is asked.
# ---------------------------------------------------------------------------


def refusing_a_missing_prime(asked: list):
    """The synthetic build command, refusing a prime that is not a directory as the real one does."""
    from tests.studyforge.skills.execution.standalone.test_vendor import TAGS
    from tests.studyforge.skills.execution.standalone.test_vendor import answering as builds

    fake = builds(TAGS, asked)

    def run(argv, cwd):
        if "--prime" in argv and not Path(argv[argv.index("--prime") + 1]).is_dir():
            asked.append(list(argv))
            return 2, ""
        return fake(argv, cwd)

    return run


def test_a_profiled_course_with_no_prime_asks_the_unprimed_pair_and_no_course_layer(tmp_path):
    from tests.studyforge.skills.execution.standalone.test_vendor import toolchain

    asked: list = []
    got = vendor.ask(
        toolchain(tmp_path / "tc"),
        RUNTIMES,
        tmp_path / "no-prime",
        platform="linux/amd64",
        run=refusing_a_missing_prime(asked),
        profile="example-profile",
    )
    assert list(got.builds) == ["runner", "editor"]
    assert not any("--prime" in argv for argv in asked)
    assert got.inputs == (".dockerignore", "docker/minimal")


def test_a_profiled_course_with_no_prime_passes_pinned_and_ask_as_release_calls_them(tmp_path):
    from tests.studyforge.skills.execution.standalone.test_vendor import course, toolchain

    asked: list = []
    checkout, prime = toolchain(tmp_path / "tc"), tmp_path / "c" / ".studyforge/execution/prime"
    root = course(
        tmp_path / "c",
        runner="t/runner-example-profile:runner-tag",
        editor="t/editor-example-profile:editor-tag",
    )
    run = refusing_a_missing_prime(asked)
    vendor.pinned(root, checkout, RUNTIMES, prime, PROFILED, platform="linux/amd64", run=run)
    got = vendor.ask(
        checkout, RUNTIMES, prime, platform="linux/amd64", run=run, profile="example-profile"
    )
    assert list(got.builds) == ["runner", "editor"]
    assert not any("--prime" in argv for argv in asked)


def test_a_profiled_course_with_a_prime_still_asks_all_four_builds(tmp_path):
    from tests.studyforge.skills.execution.standalone.test_vendor import toolchain

    prime = tmp_path / "prime"
    (prime / "maven").mkdir(parents=True)
    (prime / "maven" / "pom.xml").write_text("<project/>\n", encoding="utf-8")
    asked: list = []
    got = vendor.ask(
        toolchain(tmp_path / "tc"),
        RUNTIMES,
        prime,
        platform="linux/amd64",
        run=refusing_a_missing_prime(asked),
        profile="example-profile",
    )
    assert list(got.builds) == list(vendor.BUILDS)
    builds = [one for one in asked if one[0] != "git"]
    assert ["--prime" in one for one in builds] == [False, False, True, True]


def test_a_course_with_no_profile_still_asks_its_course_layers_with_its_prime(tmp_path):
    """⭐ The non-profile path is unchanged: its layers are asked, and the toolchain judges."""
    from tests.studyforge.skills.execution.standalone.test_vendor import toolchain

    asked: list = []
    with pytest.raises(vendor.VendorRefused, match="refused the runner-prime build"):
        vendor.ask(
            toolchain(tmp_path / "tc"),
            RUNTIMES,
            tmp_path / "no-prime",
            platform="linux/amd64",
            run=refusing_a_missing_prime(asked),
        )
