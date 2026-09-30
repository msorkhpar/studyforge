"""Mirror of `src/studyforge/skills/execution/standalone/record.py` (R12)."""

from __future__ import annotations

from types import SimpleNamespace

from studyforge.skills.execution.standalone import images, record, split
from tests.studyforge.skills.execution.standalone.test_bases import lock, parsed
from tests.studyforge.skills.execution.standalone.test_compose import BUILDS

ASKED = SimpleNamespace(
    commit="c" * 40,
    builds={
        "runner": {"tag": "t/runner:a", "inputs": ["docker/minimal"]},
        "editor": {"tag": "t/editor:b", "inputs": ["docker/editor", "docker/minimal"]},
        "runner-prime": {
            "tag": "t/runner:a-p",
            "inputs": ["docker/prime", "prime", ".dockerignore"],
        },
        "editor-prime": {"tag": "t/editor:b-p", "inputs": ["prime", "docker/prime"]},
    },
)


def document(bases=None) -> dict:
    names = images.names_for(
        slug="a", course="c0ffee", serve="0.1.0-abc", builds=BUILDS, bases=bases
    )
    return record.manifest(
        "a",
        "c" * 40,
        "d" * 40,
        "0.1.0",
        ASKED,
        "linux/amd64",
        names,
        (split.Verdict("corpus.json", split.KEEP, "why"),),
        ("corpus.json",),
        ("compose.yaml",),
        bases,
    )


def test_a_self_contained_manifest_lists_its_paths_and_names_no_bases():
    made = document()
    assert made["keeps"] == [record.MANIFEST, "compose.yaml", "corpus.json"]
    assert made["release_api"] == record.RELEASE_API
    assert "bases" not in made
    assert made["toolchain"]["tags"]["runner-prime"] == "t/runner:a-p"


def test_a_thin_manifest_adds_the_locked_bases_and_nothing_else():
    locked = parsed(lock())
    thin, whole = document(locked), document()
    assert set(thin) - set(whole) == {"bases"}
    assert thin["bases"]["runner"] == {
        "image": "studyforge-code-toolchain-runner",
        "tag": "a",
        "digest": "sha256:" + "1" * 64,
    }


def test_a_thin_tree_copies_only_what_the_course_layers_read():
    assert record.thin_inputs(ASKED) == (".dockerignore", "docker/prime", "prime")


def test_the_unprimed_tags_are_the_parts_after_the_repository():
    assert record.unprimed_tags(ASKED) == {"runner": "a", "editor": "b"}
