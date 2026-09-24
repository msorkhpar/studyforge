"""Mirror of `src/studyforge/skills/adapter/parts/adapter.py` (R12)."""

from __future__ import annotations

import ast
import json

from studyforge.corpus.manifest import parse
from studyforge.skills.adapter import plan_for, scaffold
from studyforge.skills.adapter.parts.adapter import ADAPTER_PARTS
from tests.studyforge.skills.adapter import corpora


def files(**changes):
    """The adapter's five modules, rendered for the walkthrough corpus."""
    document = json.loads(json.dumps(corpora.MANIFEST))
    document.update(changes)
    made = scaffold(plan_for(parse(json.dumps(document))))
    return {item.where: item.text for item in made.files}


def test_the_five_modules_are_the_adapter():
    where = [part.where for part in ADAPTER_PARTS]
    assert where == [
        "{package}/__init__.py",
        "{package}/read.py",
        "{package}/emit.py",
        "{package}/audit.py",
        "{package}/__main__.py",
    ]


def test_every_module_parses_and_states_a_contract():
    for where, text in files().items():
        if not where.endswith(".py"):
            continue
        assert ast.get_docstring(ast.parse(text)), f"{where} has no contract (R17)"


def test_the_reading_step_refuses_by_naming_what_to_return():
    text = files()["ingest/read.py"]
    assert "raise NotImplementedError" in text
    assert "is not written yet" in text
    assert "studyforge.corpus.container.Container" in text
    assert "build() keyword dicts" in text


def test_the_source_side_count_lives_with_the_other_reading_steps():
    # ⛔ A scaffold with two hand-written modules has lost the property R19
    # depends on: counting the source is reading the source.
    assert "def expected_units" in files()["ingest/read.py"]
    assert "def expected_units" not in files()["ingest/audit.py"]
    assert "read.expected_units(root)" in files()["ingest/audit.py"]


def test_nothing_but_the_reading_step_raises_not_implemented():
    for where, text in files().items():
        if where.endswith("read.py"):
            continue
        assert "NotImplementedError" not in text, f"{where} is generated and still refuses"


def test_the_emission_stages_before_it_moves():
    # ⛔ §6. A container map that failed must never be left where validate reads.
    text = files()["ingest/emit.py"]
    assert text.index("staging = Layout(") < text.index(".replace(layout.archive)")
    assert "layout.staging" in text


def test_the_emission_dates_every_container_with_the_run_and_not_the_reader():
    # ⛔ The date is applied AFTER `read`, before the map is
    # rendered, and the documents are read from the dated container.
    text = files()["ingest/emit.py"]
    dated = text.index("container = dataclasses.replace(reading, ingested=ingested)")
    assert dated < text.index("render_map(container)")
    assert dated < text.index("read.documents(root, container)")
    assert "render_map(reading)" not in text
    assert "twenty" not in files()["ingest/audit.py"], "a generated module restates a count"


def test_the_emission_refuses_an_empty_archive():
    assert "An empty corpus is a silent failure" in files()["ingest/emit.py"]


def test_the_emission_refuses_to_overwrite_unless_asked():
    text = files()["ingest/emit.py"]
    assert "already exists; pass replace=True" in text


def test_no_module_computes_an_archive_path_for_itself():
    # ⛔ R19's whole point: the path arithmetic is the framework's.
    for where, text in files().items():
        assert "raw/" not in text, f"{where} spells a layout segment by hand"
        assert "unit-" not in text or where.endswith("audit.py"), where


def test_a_corpus_with_no_exercises_gets_no_practice_path():
    assert "practice" not in files(exercises=False)["ingest/emit.py"]


def test_the_package_name_reaches_every_generated_import():
    made = files()
    assert "from ingest import read" in made["ingest/emit.py"]
    assert "from ingest.emit import emit" in made["ingest/__main__.py"]
