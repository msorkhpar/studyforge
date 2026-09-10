"""Mirror of `tools/knowledge/bridge.py` (R12) — the doc↔code bridge.

⛔ Every fixture here is built in `tmp_path` except the two that read this
repository's own spec, which is a tracked file and therefore always present.
Nothing reads `graphify-out/`, so nothing skips.
"""

from __future__ import annotations

from pathlib import Path

from tools.knowledge.bridge import (
    ORIGIN,
    RELATION,
    applied,
    bridge,
    census,
    citations,
    ruling_nodes,
    rulings,
    unbridged_rulings,
)

REPOSITORY = Path(__file__).resolve().parents[3]


def graph_with(nodes, links=()):
    return {"nodes": list(nodes), "links": list(links)}


def code(node_id, source_file, line, label="thing()"):
    return {
        "id": node_id,
        "label": label,
        "file_type": "code",
        "source_file": source_file,
        "source_location": f"L{line}",
    }


def ruling(name, node_id=None):
    return {
        "id": node_id or f"docs_specs_spec_{name.lower()}",
        "label": f"{name} — a rule this project made",
        "file_type": "rationale",
        "source_file": "docs/specs/spec.md",
        "source_location": None,
    }


# --- reading the spec -------------------------------------------------------


def test_every_ruling_the_spec_defines_is_found():
    # ⚠️ 21, not 16. Five of them wrap onto a second line, and a line-anchored
    # pattern finds sixteen and looks like it worked — which is why `re.S` is
    # in the pattern and why this asserts the count rather than a sample.
    found = rulings(REPOSITORY)
    assert len(found) == 21
    assert found["R7"] == "No personal data reaches disk or the wire"
    assert set(found) == {f"R{number}" for number in range(1, 22)}


def test_a_ruling_that_wraps_onto_a_second_line_is_still_read_whole(tmp_path):
    spec = tmp_path / "docs" / "specs"
    spec.mkdir(parents=True)
    (spec / "spec.md").write_text(
        "**R1 — One line.** body\n\n**R2 — Two words\nover two lines.** body\n",
        encoding="utf-8",
    )
    found = rulings(tmp_path)
    assert found == {"R1": "One line", "R2": "Two words over two lines"}


# --- finding the ruling nodes, never minting them ---------------------------


def test_the_ruling_nodes_are_found_in_the_graph():
    # ⛔ The correction this module was rewritten for. An earlier version
    # minted its own R1–R21 because a badly filtered search reported none; the
    # graph had all of them, and a duplicate endpoint answers every query
    # twice, half-connected each time.
    found = ruling_nodes(graph_with([ruling("R7"), code("c", "src/a.py", 1)]))
    assert found == {"R7": "docs_specs_spec_r7"}


def test_a_ruling_node_outside_the_spec_is_not_one():
    # ⚠️ `tests/fixtures/invalid/personal-data/VIOLATION.md` carries a node
    # labelled "R7 — …" and it is a fixture, not the ruling.
    elsewhere = dict(ruling("R7"), source_file="tests/fixtures/invalid/x/VIOLATION.md")
    assert ruling_nodes(graph_with([elsewhere])) == {}


def test_a_ruling_the_graph_has_no_node_for_is_reported_not_invented(tmp_path):
    spec = tmp_path / "docs" / "specs"
    spec.mkdir(parents=True)
    (spec / "spec.md").write_text("**R1 — One.** body\n**R2 — Two.** body\n", encoding="utf-8")
    missing = unbridged_rulings(tmp_path, graph_with([ruling("R1")]))
    assert missing == ["R2"]


# --- citations --------------------------------------------------------------


def test_a_citation_lands_on_the_definition_that_made_it(tmp_path):
    # ⭐ Keyed by the line a definition starts on, because that is what a code
    # node records. ⚠️ The first version attached a file's citations to every
    # node in it: R7 alone reached 215 code nodes and 969 edges.
    source = tmp_path / "src"
    source.mkdir(parents=True)
    (source / "m.py").write_text(
        '"""A module. Cites R1."""\n\n\ndef one():\n    """Cites R7."""\n\n\ndef two():\n'
        '    """Cites nothing."""\n',
        encoding="utf-8",
    )
    found = citations(tmp_path)
    assert found == {("src/m.py", 1): {"R1"}, ("src/m.py", 4): {"R7"}}


def test_a_word_that_merely_contains_a_ruling_name_is_not_a_citation(tmp_path):
    source = tmp_path / "src"
    source.mkdir(parents=True)
    (source / "m.py").write_text('"""R7X and CR7 and 1.R7 are not R7."""\n', encoding="utf-8")
    # ⚠️ `1.R7` is word-bounded on the R, so it does match — recorded here
    # rather than claimed otherwise, because a test that overstates a pattern
    # is how the pattern gets trusted where it should not be.
    assert citations(tmp_path) == {("src/m.py", 1): {"R7"}}


# --- the bridge itself ------------------------------------------------------


def test_the_bridge_joins_a_ruling_to_the_code_that_cites_it(tmp_path):
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    (tmp_path / "docs" / "specs" / "spec.md").write_text("**R7 — A rule.** body\n", "utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "m.py").write_text('"""Cites R7."""\n', encoding="utf-8")
    graph = graph_with([ruling("R7"), code("m", "src/m.py", 1)])
    nodes, edges = bridge(tmp_path, graph)
    assert nodes == []  # ⛔ found, never minted
    assert [(e["source"], e["target"], e["relation"]) for e in edges] == [
        ("docs_specs_spec_r7", "m", RELATION)
    ]
    assert edges[0]["_origin"] == ORIGIN


def test_applying_the_bridge_twice_is_applying_it_once(tmp_path):
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    (tmp_path / "docs" / "specs" / "spec.md").write_text("**R7 — A rule.** body\n", "utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "m.py").write_text('"""Cites R7."""\n', encoding="utf-8")
    graph = graph_with([ruling("R7"), code("m", "src/m.py", 1)])
    once = applied(tmp_path, graph)
    assert census(applied(tmp_path, once)) == census(once)


# --- the census -------------------------------------------------------------


def test_a_docstring_pointing_at_its_own_file_is_not_a_bridge():
    # ⛔ The measurement that made an unbridged graph look 7.9% bridged: 495 of
    # 510 one-code-endpoint edges never left their own file.
    prose = {"id": "d", "file_type": "rationale", "source_file": "src/m.py"}
    graph = graph_with(
        [prose, code("m", "src/m.py", 1)],
        [{"source": "d", "target": "m", "relation": "rationale_for"}],
    )
    assert census(graph)["bridged"] == 0


def test_an_edge_that_crosses_files_between_prose_and_code_is_a_bridge():
    graph = graph_with(
        [ruling("R7"), code("m", "src/m.py", 1)],
        [{"source": "docs_specs_spec_r7", "target": "m", "relation": RELATION}],
    )
    counted = census(graph)
    assert counted == {"edges": 1, "bridged": 1, "from_bridge": 0}


def test_code_to_code_and_prose_to_prose_are_never_bridges():
    graph = graph_with(
        [code("a", "src/a.py", 1), code("b", "src/b.py", 1), ruling("R1"), ruling("R2")],
        [
            {"source": "a", "target": "b", "relation": "calls"},
            {"source": "docs_specs_spec_r1", "target": "docs_specs_spec_r2", "relation": "cites"},
        ],
    )
    assert census(graph)["bridged"] == 0
