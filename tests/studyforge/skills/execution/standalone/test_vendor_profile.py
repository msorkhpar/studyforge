"""Mirror of `vendor.profile_tags` in `src/studyforge/skills/execution/standalone/vendor.py` (R12).

⭐ The toolchain is a synthetic checkout answering as the real one does; the profile is made up.
"""

from __future__ import annotations

import sys

import pytest

from studyforge.skills.execution.standalone import vendor

RUNTIMES = ("java", "python")


def answering(asked, code=0, printed="t/{image}-example-profile:{image}-tag\n"):
    def run(argv, cwd):
        asked.append((list(argv), cwd))
        return code, printed.format(image=argv[argv.index("--image") + 1])

    return run


def test_the_toolchain_is_asked_for_each_image_with_the_profile_the_set_and_the_platform(tmp_path):
    asked: list = []
    tags = vendor.profile_tags(
        tmp_path, "example-profile", RUNTIMES, platform="linux/amd64", run=answering(asked)
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
            tmp_path, "example-profile", RUNTIMES, platform="linux/amd64",
            run=answering([], code=2, printed="refused: some text\n"),
        )


@pytest.mark.parametrize("printed", ["\n", "no-colon\n", "repo:bad tag\n", "repo:\n"])
def test_an_answer_that_is_not_one_tag_is_refused(tmp_path, printed):
    with pytest.raises(vendor.VendorRefused, match="printed no tag"):
        vendor.profile_tags(
            tmp_path, "example-profile", RUNTIMES, platform="linux/amd64",
            run=answering([], printed=printed),
        )
