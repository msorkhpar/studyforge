"""The Claude-course-shaped fixture: its source tree is well formed, without Docker.

⭐ The end-to-end reading (authoring in the profile runner, the thin export, the browser) is
`python3 -m tests.fixtures.claude_shape`; this checks only what needs no container: the manifest the
shape declares and the pages and example files the source writes.
"""

from __future__ import annotations

import json

from studyforge.corpus.manifest import parse
from tests.fixtures.claude_shape import course, examples


def test_the_manifest_declares_four_languages_a_profile_and_a_live_block(tmp_path):
    course.write_source(tmp_path)
    text = (tmp_path / "corpus.json").read_text(encoding="utf-8")
    manifest = parse(text)
    assert [one["id"] for one in json.loads(text)["languages"]] == [
        "python", "typescript", "java", "kotlin"]
    assert manifest.profile == course.PROFILE
    assert manifest.live is not None and manifest.live.host == course.HOST
    assert manifest.live.key_variable == course.VARIABLE


def test_the_source_writes_the_pages_and_the_example_projects(tmp_path):
    course.write_source(tmp_path)
    written = {p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file()}
    assert set(examples.files()) <= written
    assert any(one.startswith("course/") and one.endswith(".md") for one in written)


def test_no_example_or_page_names_a_real_host_or_a_real_key():
    text = "".join(examples.files().values())
    assert course.HOST.endswith(".invalid")
    assert "sk-" not in text and "anthropic.com" not in text


def test_the_conversation_example_names_the_file_each_tab_runs():
    from tests.fixtures.claude_shape import lessons

    block = next(b for b in lessons.conversation_blocks() if b["type"] == "example")
    assert [tab["lang"] for tab in block["tabs"]] == list(lessons.LANGUAGES)
    assert all(tab["code"].startswith(examples.ROOT) for tab in block["tabs"])
    assert "code" not in lessons.agent_blocks()[3]["tabs"][0]
