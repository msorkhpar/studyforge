"""The release option that names the published Docker Hub account in the README (R12)."""

from __future__ import annotations

import pytest

from studyforge.skills.execution.standalone import write

from tests.studyforge.skills.execution.standalone.test_write import (
    answered,
    checkout,
    on_disk,
    toolchain,
)


def test_a_published_account_reaches_the_readme_only(tmp_path):
    base = tmp_path / "base"
    named = tmp_path / "named"
    for out, kwargs in ((base, {}), (named, {"published_account": "exampleaccount"})):
        write.release(
            checkout(tmp_path / (out.name + "src")),
            out,
            toolchain=toolchain(tmp_path / (out.name + "tc")),
            platform="linux/amd64",
            run=answered(),
            **kwargs,
        )
    assert "account `exampleaccount`:" in (named / "README.md").read_text(encoding="utf-8")
    for one in on_disk(base):
        if one != "README.md" and one != write.MANIFEST:
            assert (base / one).read_bytes() == (named / one).read_bytes(), one
    assert "exampleaccount" not in b"".join(
        (named / one).read_bytes() for one in on_disk(named) if one != "README.md"
    ).decode("utf-8", "ignore")


@pytest.mark.parametrize("bad", ["", "abc", "Example1", "has-dash", "x" * 31, "a b c d"])
def test_a_published_account_that_is_not_a_docker_hub_account_is_refused(tmp_path, bad):
    with pytest.raises(write.ReleaseRefused, match="published_account"):
        write.release(
            tmp_path,
            tmp_path / "out",
            toolchain=tmp_path,
            platform="linux/amd64",
            run=answered(),
            published_account=bad,
        )
