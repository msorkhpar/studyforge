"""No text the framework writes into a corpus cites a process id.

Mirrors no source module. It gathers what the framework writes into a corpus,
from each writer's own entry point and never from a list of strings typed here:

- onboarding's whole file set, which carries the adapter scaffold, the pin, its
  stubs, the generated tests and the reader's document;
- the execution skill's compose file, toolchain file and `EXECUTION.md`, from a
  corpus that has a prime, practice workspaces and narration, so every optional
  paragraph is written; and the runner's environment file;
- the page stylesheet and script a build writes beside every page, which a
  corpus commits under `.studyforge/assets/`.

It reads them with the population command `docs/decisions.md` states, so the
grammar is the file's and never a second spelling of it. ⛔ **Unlike a message,
generated text may not cite an ALIASED id either**: the decisions file lives in
the framework's repository, and a stranger reading a corpus has only the
corpus. Generated text says the thing itself, or cites a spec rule.
"""

from __future__ import annotations

import json
import re

from studyforge.corpus.manifest import parse
from studyforge.render.pageassets import bundle
from studyforge.skills.execution import onboard as execution
from studyforge.skills.execution import record
from studyforge.skills.onboarding.onboard import onboard
from tests.studyforge.skills.execution import contracts
from tests.studyforge.skills.onboarding import corpora
from tests.test_decisions import population, scratch_repository

#: A face embedded in the stylesheet, whose base64 is data and never prose.
EMBEDDED = re.compile(r'url\("data:[^"]*"\)')

#: A tag of the shape the component's own `tag_from` prints.
TAG = "studyforge-runner:0123456789ab"

#: The draft a person settled, carrying a reason of their own words. ⚠️ Not the
#: onboarding tests' fixture as it is: a person's reason is copied into
#: `corpus.json` verbatim, and what a person writes is not what this reads.
SETTLED = {
    **corpora.DRAFT,
    "content": {
        "include": ["src/*.md"],
        "not_material": [
            {"glob": "README.md", "why": "navigation that records the units; no unit reads it"}
        ],
    },
}


def written(tmp_path) -> dict[str, str]:
    """`label -> text` for everything the framework writes into a corpus."""
    made = onboard(SETTLED, framework_commit=corpora.COMMIT)
    texts = {f"onboarding/{item.where}": item.text for item in made.files}
    manifest = parse(json.dumps(contracts.manifest_document()))
    runnable = execution.generate(
        manifest,
        editor_text=contracts.editor_text(),
        root=contracts.corpus(tmp_path / "corpus"),
        narration_text=contracts.narration_text(),
    )
    texts |= {f"execution/{where}": text for where, text in runnable.files}
    image = runnable.runner.selection.image_env
    texts[f"execution/{execution.RUNNER_ENV}"] = record.text(image, TAG)
    texts |= {
        f"assets/{name}": EMBEDDED.sub('url("data:")', text)
        for name, text in bundle.written_files().items()
    }
    return texts


def cited(tmp_path, texts: dict[str, str]) -> list[str]:
    """Every process id the decisions file's command prints over `texts`."""
    files = {f"src/{label}": text for label, text in texts.items()}
    return population(scratch_repository(tmp_path, files))


def test_every_writer_is_read(tmp_path):
    # ⛔ A writer dropped from the gathering would make the assertion below
    # vacuous for it, so each one is named by a file it always writes.
    labels = set(written(tmp_path / "w"))
    assert any(one.startswith("onboarding/") and one.endswith("/emit.py") for one in labels)
    for expected in (
        "onboarding/ONBOARDING.md",
        f"execution/{execution.READER_DOC}",
        f"execution/{execution.COMPOSE_FILE}",
        f"execution/{execution.RUNNER_ENV}",
        f"assets/{bundle.STYLESHEET_NAME}",
        f"assets/{bundle.SCRIPT_NAME}",
    ):
        assert expected in labels, f"{expected} is not among what is read"


def test_every_optional_paragraph_of_the_readers_document_is_written(tmp_path):
    text = written(tmp_path / "w")[f"execution/{execution.READER_DOC}"]
    for heading in ("## Narration", "## The prime", "binds too", "before the start"):
        assert heading in text, f"{heading!r} is not written, so it is not read"


def test_an_id_planted_in_generated_text_is_read(tmp_path):
    planted = "SK-" + "99/9"
    texts = written(tmp_path / "w")
    label = f"execution/{execution.READER_DOC}"
    texts[label] += f"\nwithout a name (`{planted}`).\n"
    assert cited(tmp_path / "c", texts) == [planted]


def test_no_text_the_framework_writes_into_a_corpus_cites_a_process_id(tmp_path):
    texts = written(tmp_path / "w")
    found = cited(tmp_path / "all", texts)
    if found:
        where = {
            label: cited(tmp_path / f"one{n}", {label: text})
            for n, (label, text) in enumerate(texts.items())
        }
        assert {label: ids for label, ids in where.items() if ids} == {}
    assert found == []
