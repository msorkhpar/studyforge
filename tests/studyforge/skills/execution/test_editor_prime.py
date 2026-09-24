"""The editor's prime, declared by the contract as the runner's is.

⚠️ The editor's build accepts `--prime` and a prime moves its tag, so a contract
that declared a prime only under `runner.prime` would leave the editor built and
recorded unprimed. ⭐ From `provides` 3 the contract declares `editor.prime`; the editor's build,
its tag command and the recorded tag are then all primed, and the document's
sentence says exactly which printed lines carry the flag — held here against
the block it prints, for a contract with the key and for one without.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from studyforge.corpus.manifest import parse
from studyforge.skills.execution import onboard, record
from studyforge.skills.execution.contract import ContractRefused
from tests.studyforge.skills.execution.contracts import corpus, editor_contract, manifest_document
from tests.studyforge.skills.execution.test_record import EDITOR_TAG, Asked

#: What the synthetic contract's prime flag reads with this corpus's directory in it.
FLAG = f"--prime <this corpus>/{onboard.PRIME_DIR}"


def contract(flag: str | None = "--prime <directory>") -> str:
    """The synthetic contract at `provides` 3, its editor declaring `flag` (or no prime)."""
    document = editor_contract()
    document["provides"] = 3
    if flag is not None:
        document["editor"]["prime"] = {
            "seeds": {"gradle": "gradle-home", "maven": "maven-repo"},
            "declared_by": flag,
        }
    return json.dumps(document)


def made(root: Path, text: str, **moved: object) -> onboard.Execution:
    """Generate and write for the synthetic corpus at `root`, against `text`."""
    manifest = parse(json.dumps(manifest_document(**moved)))
    execution = onboard.generate(manifest, editor_text=text, root=corpus(root))
    onboard.write(execution, root)
    return execution


def build_block(document: str) -> list[str]:
    """The fenced lines under "Build the images", as the reader copies them."""
    section = document.split("\n## Build the images\n", 1)[1]
    return re.search(r"```\n(.+?)\n```", section, re.S)[1].splitlines()


def the_prime_sentence(document: str) -> str:
    """The prose under "The prime" after its list, flattened."""
    section = document.split("\n## The prime\n", 1)[1].split("\n## ", 1)[0]
    paragraphs = [one for one in section.split("\n\n") if one.strip()]
    return " ".join(paragraphs[-1].split())


def test_the_editor_is_asked_its_tag_with_the_same_prime_as_the_runner(tmp_path):
    execution = made(tmp_path, contract())
    asked = Asked(0, EDITOR_TAG)
    record.record_editor(execution, tmp_path, tmp_path / "component", ask=asked)
    [(argv, _)] = asked.calls
    prime = str((tmp_path / onboard.PRIME_DIR).resolve())
    assert argv == [
        "python3",
        "build.py",
        "--runtimes",
        "java,maven",
        "--print-tag",
        "--prime",
        prime,
    ]
    assert argv[-2:] == record.argv(execution, tmp_path)[-2:], "one prime, both images"
    written = (tmp_path / onboard.EDITOR_ENV).read_text(encoding="utf-8")
    assert f"EDITOR_IMAGE={EDITOR_TAG}\n" in written and str(tmp_path) not in written


def test_every_editor_line_the_document_prints_carries_the_prime(tmp_path):
    document = dict(made(tmp_path, contract()).files)[onboard.READER_DOC]
    runner_build, editor_build, editor_tag = build_block(document)
    assert all(line.endswith(f" {FLAG}") for line in (runner_build, editor_build, editor_tag))
    assert editor_build.startswith("python3 build.py --runtimes java,maven")
    assert editor_tag.startswith("python3 build.py --runtimes java,maven --print-tag")
    assert "with the same prime, and writes" in document


@pytest.mark.parametrize(
    "flag", ["--prime <directory>", None], ids=["editor-prime", "no-editor-prime"]
)
def test_the_prime_sentence_says_exactly_which_printed_lines_carry_it(tmp_path, flag):
    document = dict(made(tmp_path, contract(flag)).files)[onboard.READER_DOC]
    carrying = [FLAG in line for line in build_block(document)]
    sentence = the_prime_sentence(document)
    if all(carrying):
        assert sentence.startswith(f"All three lines above carry `{FLAG}`"), sentence
    else:
        assert carrying == [True, False, False]
        assert sentence.startswith(f"The runner's build above carries `{FLAG}`."), sentence
        assert "unprimed" in sentence
    assert "to the builds above" not in document


def test_a_corpus_with_no_prime_prints_and_asks_the_editor_unprimed(tmp_path):
    execution = made(tmp_path, contract(), runtimes=["python"])
    document = dict(execution.files)[onboard.READER_DOC]
    assert "--prime" not in document
    asked = Asked(0, "example/editor:python-amd64-ba9876543210")
    record.record_editor(execution, tmp_path, tmp_path, ask=asked)
    assert "--prime" not in asked.calls[0][0]


def test_an_editor_prime_with_no_directory_slot_is_refused_by_its_key(tmp_path):
    with pytest.raises(ContractRefused, match="prime.declared_by has no <directory> slot"):
        made(tmp_path, contract("--prime"))
