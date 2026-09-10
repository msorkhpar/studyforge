"""Mirror of `tools/knowledge/__main__.py` (R12) — the two documented commands.

The exit code is the deliverable: `census` is how a person checks the claim the
tripwire makes, so it has to answer the same way the tripwire does.
"""

from __future__ import annotations

import json

from tools.knowledge import BRIDGE_FLOOR, index_path, read_graph
from tools.knowledge.__main__ import main
from tools.tests.quality.test_knowledge_index import write_index


def test_a_missing_index_exits_one_and_says_where_it_looked(tmp_path, capsys):
    assert main(["census", "--root", str(tmp_path)]) == 1
    assert "no knowledge index" in capsys.readouterr().out


def test_census_reports_the_numbers_and_does_not_rewrite_the_graph(tmp_path, capsys):
    path = write_index(tmp_path, "0" * 40, BRIDGE_FLOOR)
    before = path.read_bytes()
    assert main(["census", "--root", str(tmp_path)]) == 0
    assert path.read_bytes() == before
    assert f"floor {BRIDGE_FLOOR}" in capsys.readouterr().out


def test_census_exits_one_below_the_floor(tmp_path, capsys):
    write_index(tmp_path, "0" * 40, BRIDGE_FLOOR - 1)
    assert main(["census", "--root", str(tmp_path)]) == 1


def test_bridge_writes_the_graph_back(tmp_path, capsys):
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    (tmp_path / "docs" / "specs" / "spec.md").write_text("**R7 — A rule.** body\n", "utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "m.py").write_text('"""Cites R7."""\n', encoding="utf-8")
    path = index_path(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "built_at_commit": "0" * 40,
                "nodes": [
                    {
                        "id": "r",
                        "label": "R7 — A rule",
                        "file_type": "rationale",
                        "source_file": "docs/specs/spec.md",
                    },
                    {
                        "id": "m",
                        "label": "m.py",
                        "file_type": "code",
                        "source_file": "src/m.py",
                        "source_location": "L1",
                    },
                ],
                "links": [],
            }
        ),
        encoding="utf-8",
    )
    # ⚠️ Exits 1 because one edge is below the floor — the write is the point,
    # and the exit code still answers the question the floor asks.
    main(["bridge", "--root", str(tmp_path)])
    links = read_graph(path)["links"]
    assert [(link["source"], link["target"]) for link in links] == [("r", "m")]
