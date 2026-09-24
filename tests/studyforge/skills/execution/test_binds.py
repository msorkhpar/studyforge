"""Mirror of `src/studyforge/skills/execution/binds.py` (R12) — what the editor may see.

⭐ `W465`'s clause 1 as the skill decides it: no directory the editor binds
reaches the bundles' or the archive's directory, where a quiz's key is kept.
The derivation of the sources directory is `test_onboard.py`'s.
"""

from __future__ import annotations

import json

import pytest

from studyforge.corpus.manifest import parse
from studyforge.corpus.placement import ARCHIVE_DIRNAME
from studyforge.exercise.bundle.layout import BUNDLES_DIRNAME
from studyforge.skills.execution import binds, onboard
from tests.studyforge.skills.execution.contracts import corpus, editor_text, manifest_document


@pytest.mark.parametrize(
    "bind",
    [
        BUNDLES_DIRNAME,
        f"{BUNDLES_DIRNAME}/unit",
        ARCHIVE_DIRNAME,
        f"{ARCHIVE_DIRNAME}/iso/raw",
        ".",
    ],
)
def test_a_bind_that_is_holds_or_sits_inside_a_keyed_directory_is_refused(bind):
    with pytest.raises(binds.ExecutionRefused, match="quiz's key"):
        binds.unkeyed("sources", bind)


@pytest.mark.parametrize("bind", ["sources", "practice", "src/exercises-notes", "archives"])
def test_a_bind_beside_them_is_kept(bind):
    binds.unkeyed(bind)


@pytest.mark.parametrize("keyed", [BUNDLES_DIRNAME, ARCHIVE_DIRNAME])
def test_material_declared_inside_a_keyed_directory_refuses_the_whole_generation(tmp_path, keyed):
    document = manifest_document(content={"include": [f"{keyed}/**/*.md"], "exclude": []})
    with pytest.raises(onboard.ExecutionRefused, match="quiz's key"):
        onboard.generate(parse(json.dumps(document)), editor_text=editor_text(), root=tmp_path)


def test_the_generated_editor_binds_no_keyed_directory(tmp_path):
    made = onboard.generate(
        parse(json.dumps(manifest_document())), editor_text=editor_text(), root=corpus(tmp_path)
    )
    text = dict(made.files)[onboard.COMPOSE_FILE]
    editor = text.split("\n  editor:\n", 1)[1].split("\n  runner:\n", 1)[0]
    hosts = [
        line.split('"', 2)[1].split(":", 1)[0]
        for line in editor.splitlines()
        if line.startswith('      - "../')
    ]
    assert hosts == ["../../sources", "../../practice"]
    for host in hosts:
        binds.unkeyed(host.removeprefix("../../"))
