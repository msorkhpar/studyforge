"""Mirror of `vendor.profile_tags` in `src/studyforge/skills/execution/standalone/vendor.py` (R12).

⭐ The toolchain is a synthetic checkout answering as the real one does; the profile is made up.
"""

from __future__ import annotations

import json
import sys

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
        checkout_of(tmp_path), "example-profile", RUNTIMES, platform="linux/amd64",
        run=answering(asked)
    )
    assert tags == {"runner": "runner-tag", "editor": "editor-tag"}
    assert [(argv[0], cwd) for argv, cwd in asked] == [(sys.executable, tmp_path)] * 2
    assert asked[0][0][1:] == [
        "docker/profile_packages/package_build.py", "--profile", "example-profile",
        "--image", "runner", "--runtimes", "java,python", "--print-tag",
        "--platform", "linux/amd64",
    ]
    assert asked[1][0][asked[1][0].index("--image") + 1] == "editor"


def test_a_profile_the_toolchain_refuses_is_refused_by_name_without_its_text(tmp_path):
    with pytest.raises(vendor.VendorRefused, match="refused profile example-profile .*exit 2"):
        vendor.profile_tags(
            checkout_of(tmp_path), "example-profile", RUNTIMES, platform="linux/amd64",
            run=answering([], code=2, printed="refused: some text\n"),
        )


@pytest.mark.parametrize("printed", ["\n", "no-colon\n", "repo:bad tag\n", "repo:\n"])
def test_an_answer_that_is_not_one_tag_is_refused(tmp_path, printed):
    with pytest.raises(vendor.VendorRefused, match="printed no tag"):
        vendor.profile_tags(
            checkout_of(tmp_path), "example-profile", RUNTIMES, platform="linux/amd64",
            run=answering([], printed=printed),
        )


def test_the_command_is_the_one_the_contract_names_not_one_written_here(tmp_path):
    asked: list = []
    named = dict(PROFILE_TAG, printed_by=["python3", "elsewhere.py", "<platform>", "<profile>",
                                          "<runner|editor>", "<the declared set>"])
    vendor.profile_tags(
        checkout_of(tmp_path, named), "example-profile", RUNTIMES, platform="linux/arm64",
        run=answering(asked, printed="t/x:tag\n"),
    )
    assert asked[0][0][1:] == [
        "elsewhere.py", "linux/arm64", "example-profile", "runner", "java,python",
    ]


def test_a_toolchain_that_declares_no_profile_tag_is_refused_and_never_asked(tmp_path):
    asked: list = []
    with pytest.raises(vendor.VendorRefused, match="declares no profile_tag"):
        vendor.profile_tags(
            checkout_of(tmp_path, None), "example-profile", RUNTIMES, platform="linux/amd64",
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
            checkout_of(tmp_path, block), "example-profile", RUNTIMES, platform="linux/amd64",
            run=answering([]),
        )


def test_no_consuming_json_at_all_is_refused(tmp_path):
    with pytest.raises(vendor.VendorRefused, match="no consuming.json"):
        vendor.profile_tags(
            tmp_path, "example-profile", RUNTIMES, platform="linux/amd64", run=answering([])
        )


def test_the_provisional_constant_is_gone():
    assert not hasattr(vendor, "PROFILE_TAG_BY")
