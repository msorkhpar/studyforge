"""Mirror of the profile half of `record.py` and `toolchain.select` (R12): a corpus's image profile.

⭐ **A corpus that names a profile (`profile` in `corpus.json`) runs on the profile's images**,
which the toolchain layers on the base of its declared runtimes. ⛔ So its local record asks the
toolchain for the PROFILE's tags, with the command the contract names under `profile_tag`, exactly
as the export's lock check does, and never records the plain base's tag in their place.

⛔ **A profile and a prime do not combine locally.** The contract's profile tag command takes no
prime, and a profile image is built on the unprimed base, so no tag the toolchain computes names an
image that carries both. The record refuses such a corpus by name rather than record either half.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from studyforge.corpus.manifest import parse
from studyforge.skills.execution import onboard, record
from studyforge.skills.execution.contract import ContractRefused
from studyforge.skills.execution.onboard import ExecutionRefused
from tests.studyforge.skills.execution.contracts import corpus, editor_contract, manifest_document
from tests.studyforge.skills.execution.test_record import RUNNER_BYTES, Asked, made

#: The profile the synthetic corpus names.
NAME = "example-profile"

#: The contract's `profile_tag` block, in the shape the real component declares it.
PROFILE_TAG = {
    "printed_by": [
        "python3",
        "profile.py",
        "--profile",
        "<profile>",
        "--image",
        "<runner|editor>",
        "--runtimes",
        "<the declared set>",
        "--print-tag",
        "--platform",
        "<platform>",
    ],
    "profile_tag_api": 1,
}

#: What the fake component prints for each profile image.
RUNNER_TAG = f"example/runner-{NAME}:node-python-amd64-0123456789ab"
EDITOR_TAG = f"example/editor-{NAME}:node-python-amd64-ba9876543210"


def contract(block: object = PROFILE_TAG) -> str:
    """The synthetic contract, carrying `block` as its `profile_tag` (or none for `None`)."""
    document = editor_contract()
    if block is not None:
        document["profile_tag"] = block
    return json.dumps(document)


def profiled(root: Path, *, runtimes=("node", "python"), text: str | None = None, **moved):
    """Generate and write a corpus that names the profile."""
    document = manifest_document(corpus_api=8, runtimes=list(runtimes), profile=NAME, **moved)
    execution = onboard.generate(
        parse(json.dumps(document)), editor_text=text or contract(), root=corpus(root)
    )
    onboard.write(execution, root)
    return execution


def asked_for(argv: list[str], option: str) -> str:
    return argv[argv.index(option) + 1]


def test_the_runner_is_asked_with_the_contracts_profile_command_not_its_base_tag_from(tmp_path):
    execution = profiled(tmp_path)
    asked = Asked(0, RUNNER_TAG + "\n")
    record.record_runner(execution, tmp_path, tmp_path / "tc", ask=asked, platform="linux/amd64")
    [(argv, cwd)] = asked.calls
    assert argv == [
        "python3",
        "profile.py",
        "--profile",
        NAME,
        "--image",
        "runner",
        "--runtimes",
        "node,python",
        "--print-tag",
        "--platform",
        "linux/amd64",
    ]
    assert cwd == tmp_path / "tc"
    written = (tmp_path / onboard.RUNNER_ENV).read_text(encoding="utf-8")
    lines = [one for one in written.splitlines() if one and not one.startswith("#")]
    assert lines == [f"STUDYFORGE_RUNNER_IMAGE={RUNNER_TAG}"]
    assert NAME in written and "profile_tag.printed_by" in written
    assert str(tmp_path) not in written


def test_the_editor_is_asked_for_the_profiles_editor_image(tmp_path):
    execution = profiled(tmp_path)
    asked = Asked(0, EDITOR_TAG + "\n")
    record.record_editor(execution, tmp_path, tmp_path / "tc", ask=asked, platform="linux/arm64")
    [(argv, _)] = asked.calls
    assert asked_for(argv, "--image") == "editor"
    assert asked_for(argv, "--profile") == NAME
    assert asked_for(argv, "--platform") == "linux/arm64"
    written = (tmp_path / onboard.EDITOR_ENV).read_text(encoding="utf-8")
    assert [one for one in written.splitlines() if one and not one.startswith("#")] == [
        f"EDITOR_IMAGE={EDITOR_TAG}"
    ]


@pytest.mark.parametrize("platform", [None, "", "linux/s390x", "linux/amd64 --x"])
def test_a_profiled_corpus_is_refused_without_one_platform_it_can_name(tmp_path, platform):
    # ⭐ The host's platform is the caller's to name: this package reads nothing of the machine.
    execution = profiled(tmp_path)
    asked = Asked(0, RUNNER_TAG)
    with pytest.raises(ExecutionRefused, match="platform="):
        record.record_runner(execution, tmp_path, tmp_path, ask=asked, platform=platform)
    assert asked.calls == []
    assert not (tmp_path / onboard.RUNNER_ENV).exists()


@pytest.mark.parametrize(
    "printed",
    [
        "example/runner:node-python-amd64-0123456789ab",  # the plain base's own tag
        f"example/editor-{NAME}:node-python-amd64-0123456789ab",  # the other image's
        "example/runner-other:node-python-amd64-0123456789ab",  # another profile's
        f"example/runner-{NAME}:",
    ],
)
def test_only_one_tag_of_the_profiles_own_runner_is_recorded(tmp_path, printed):
    execution = profiled(tmp_path)
    with pytest.raises(ExecutionRefused, match="not one tag"):
        record.record_runner(
            execution, tmp_path, tmp_path, ask=Asked(0, printed), platform="linux/amd64"
        )
    assert not (tmp_path / onboard.RUNNER_ENV).exists()


def test_a_profile_command_that_fails_is_refused_by_the_contracts_own_key(tmp_path):
    execution = profiled(tmp_path)
    with pytest.raises(ExecutionRefused, match="profile_tag.printed_by exited 2"):
        record.record_editor(
            execution, tmp_path, tmp_path, ask=Asked(2, ""), platform="linux/amd64"
        )


def test_a_profile_and_a_prime_do_not_combine_and_neither_tag_is_recorded(tmp_path):
    execution = profiled(tmp_path, runtimes=("java", "maven"))
    assert execution.primed is not None and execution.primed.projects, "no prime: vacuous"
    for recorder, where in (
        (record.record_runner, onboard.RUNNER_ENV),
        (record.record_editor, onboard.EDITOR_ENV),
    ):
        asked = Asked(0, RUNNER_TAG)
        with pytest.raises(ExecutionRefused, match="profile") as refused:
            recorder(execution, tmp_path, tmp_path, ask=asked, platform="linux/amd64")
        assert "prime" in str(refused.value)
        assert asked.calls == []
        assert not (tmp_path / where).exists()


def test_a_toolchain_that_declares_no_profile_tag_cannot_onboard_a_profiled_corpus(tmp_path):
    with pytest.raises(ContractRefused, match="profile_tag"):
        profiled(tmp_path, text=contract(None))


@pytest.mark.parametrize(
    "block",
    [
        dict(PROFILE_TAG, profile_tag_api=99),
        dict(PROFILE_TAG, printed_by=[one for one in PROFILE_TAG["printed_by"] if one[0] != "<"]),
        dict(PROFILE_TAG, printed_by="python3 profile.py"),
    ],
)
def test_a_profile_tag_block_this_skill_cannot_fill_is_refused(tmp_path, block):
    with pytest.raises(ContractRefused, match="profile_tag"):
        profiled(tmp_path, text=contract(block))


def test_the_toolchain_selection_names_the_profile_and_its_tag_command(tmp_path):
    profiled(tmp_path)
    kept = json.loads((tmp_path / onboard.TOOLCHAIN_FILE).read_text(encoding="utf-8"))
    assert kept["profile"]["name"] == NAME
    assert kept["profile"]["tag_from"] == [
        "python3",
        "profile.py",
        "--profile",
        NAME,
        "--image",
        "editor",
        "--runtimes",
        "node,python",
        "--print-tag",
        "--platform",
        "<platform>",
    ]


def test_the_readers_document_says_the_profiles_images_are_what_runs(tmp_path):
    profiled(tmp_path)
    document = (tmp_path / onboard.READER_DOC).read_text(encoding="utf-8")
    assert f"profile: `{NAME}`" in document
    assert "--image runner" in document and "--image editor" in document
    assert "profile_tag.printed_by" in document
    # ⛔ A slot in a printed command would be read by a shell as a redirection.
    fenced = document.split("```")[1::2]
    assert not any("<platform>" in block for block in fenced)


def test_a_corpus_that_names_no_profile_keeps_every_byte_it_had(tmp_path):
    # ⭐ The same contract, with the block present: only a corpus that names a profile reads it.
    plain = tmp_path / "plain"
    with_block = tmp_path / "with-block"
    plain.mkdir()
    with_block.mkdir()
    made(plain)
    document = manifest_document()
    execution = onboard.generate(
        parse(json.dumps(document)), editor_text=contract(), root=corpus(with_block)
    )
    onboard.write(execution, with_block)
    for where in (onboard.TOOLCHAIN_FILE, onboard.READER_DOC):
        assert (with_block / where).read_bytes() == (plain / where).read_bytes()
    record.record_runner(execution, with_block, with_block, ask=Asked())
    assert (with_block / onboard.RUNNER_ENV).read_text(encoding="utf-8") == RUNNER_BYTES
