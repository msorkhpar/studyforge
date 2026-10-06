"""Running the ranking library under `node`, and what a build does when it cannot.

Mirrors `execute/searchnode.py`. ⚠️ The clause that matters is the fallback: no `node`,
or one that fails, never fails a build; it warns once with the reason and writes the records as a
build always did.
"""

from __future__ import annotations

import json

import pytest

from studyforge.execute import searchnode
from studyforge.render.pageassets import Unbuilt, text
from studyforge.render.pageassets import search as searchindex
from tests.studyforge.render.pageassets.test_search import PAGES, _parse, built, needs_node

DOCUMENTS = [
    {"id": "0.0", "title": "Hooks", "heading": "", "text": "a hook runs a command"},
    {"id": "0.1", "title": "Hooks", "heading": "Plugins", "text": "a plugin marketplace"},
]
OPTIONS = {"fields": ["title", "heading", "text"], "storeFields": ["title", "heading"]}


def _program(tmp_path, name, body):
    program = tmp_path / name
    program.write_text("#!/bin/sh\n" + body + "\n", encoding="utf-8")
    program.chmod(0o755)
    return str(program)


@needs_node
def test_node_writes_the_serialised_index_of_the_documents():
    out = searchnode.serialised(DOCUMENTS, OPTIONS, text("minisearch.js"))
    parsed = json.loads(out)
    assert parsed["documentCount"] == 2 and parsed["serializationVersion"] == 2
    assert parsed["documentIds"] == {"0": "0.0", "1": "0.1"}
    assert "text" not in json.dumps(parsed["storedFields"])


@pytest.mark.parametrize(
    ("body", "reason"),
    [("exit 3", "node exited with status 3"), ("echo not-json", "node wrote no serialised index"),
     ("echo '[1]'", "node wrote no serialised index")],
)
def test_a_node_that_fails_names_the_reason(tmp_path, body, reason):
    with pytest.raises(Unbuilt, match=reason):
        searchnode.serialised(DOCUMENTS, OPTIONS, "", _program(tmp_path, "node", body))


def test_no_node_and_one_that_cannot_run_name_the_reason(tmp_path):
    with pytest.raises(Unbuilt, match="node was not found"):
        searchnode.serialised(DOCUMENTS, OPTIONS, "", None)
    with pytest.raises(Unbuilt, match="node could not be run"):
        searchnode.serialised(DOCUMENTS, OPTIONS, "", str(tmp_path / "absent"))


def test_the_node_on_path_is_the_default_and_none_means_none(monkeypatch):
    monkeypatch.setattr(searchnode.shutil, "which", lambda name: f"/opt/bin/{name}")
    assert searchnode.node_program() == "/opt/bin/node"
    assert searchnode.node_program(None) is None
    assert searchnode.node_program("/elsewhere/node") == "/elsewhere/node"


def test_without_node_the_build_warns_once_and_writes_the_records(capsys):
    out = built(PAGES, node=None)
    err = capsys.readouterr().err
    assert err == searchindex.warn("node was not found") + "\n"
    assert _parse(out[searchindex.INDEX_NAME])["version"] == searchindex.VERSION
    assert out[searchindex.BUILD_NAME] == text(searchindex.BUILD_NAME)


def test_a_build_with_a_node_that_fails_falls_back_and_names_the_reason(capsys, tmp_path):
    out = built(PAGES, node=_program(tmp_path, "node", "exit 3"))
    assert capsys.readouterr().err == searchindex.warn("node exited with status 3") + "\n"
    assert _parse(out[searchindex.INDEX_NAME])["version"] == searchindex.VERSION
    assert searchindex.BUILD_NAME in out


def test_a_build_given_no_builder_falls_back_and_says_so(capsys):
    out = searchindex.files(PAGES)
    assert capsys.readouterr().err == searchindex.warn("no index builder was given") + "\n"
    assert searchindex.BUILD_NAME in out
