"""Mirror of `src/studyforge/skills/execution/standalone/bases.py` (R12).

⭐ The lock is read from text, so each refusal is a sentence written here. ⛔ Every digest
below is the documented placeholder (sixty-four zeros) or a made-up hex string: none names
an image, and `read(..., placeholder=True)` is how an example is admitted.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from studyforge.skills.execution.standalone import bases
from studyforge.skills.onboarding import library

ZEROS = bases.PLACEHOLDER
RUNNER_TAG = "a"
EDITOR_TAG = "b"


def serve_tag() -> str:
    """The tag this checkout's own build script computes for the serving base."""
    return str(bases.computed_serve_tag(library.PACKAGE.parent))


def lock(**changes) -> dict:
    """A well-formed lock of placeholder digests, with `changes` replacing whole entries."""
    document = {
        "bases_api": 1,
        "serve": {"image": "studyforge-serve", "tag": serve_tag(), "digest": ZEROS},
        "runner": {"image": "runner", "tag": RUNNER_TAG, "digest": "sha256:" + "1" * 64},
        "editor": {"image": "editor", "tag": EDITOR_TAG, "digest": "sha256:" + "2" * 64},
    }
    document.update(changes)
    return document


def parsed(document: dict, **kwargs) -> bases.Bases:
    return bases.from_text(json.dumps(document), placeholder=True, **kwargs)


def with_field(kind: str, **fields) -> dict:
    document = lock()
    document[kind] = {**document[kind], **fields}
    return document


def test_a_lock_names_each_base_by_image_tag_and_digest():
    locked = parsed(lock())
    assert locked.runner.reference == f"runner:{RUNNER_TAG}@sha256:{'1' * 64}"
    assert locked.serve.reference == f"studyforge-serve:{serve_tag()}@{ZEROS}"
    assert bases.key(locked.editor) == "2" * bases.KEY_DIGITS


def test_the_placeholder_is_admitted_for_an_example_and_refused_for_an_export():
    text = json.dumps(lock())
    with pytest.raises(bases.BasesRefused, match="placeholder"):
        bases.from_text(text)
    assert bases.from_text(text, placeholder=True).serve.digest == ZEROS


@pytest.mark.parametrize(
    ("document", "message"),
    [
        ("not json", "not JSON"),
        ("[1]", "not a JSON object"),
        (json.dumps({**lock(), "bases_api": 2}), "bases_api"),
        (json.dumps({**lock(), "bases_api": True}), "bases_api"),
        (json.dumps({**lock(), "extra": 1}), "keys it does not read"),
        (json.dumps({k: v for k, v in lock().items() if k != "editor"}), "no editor base"),
        (json.dumps(with_field("runner", image="acct/runner")), "not a bare name"),
        (json.dumps(with_field("runner", image="runner:1")), "not a bare name"),
        (json.dumps(with_field("runner", image="Runner")), "not a bare name"),
        (json.dumps(with_field("runner", tag="a b")), "not an image tag"),
        (json.dumps(with_field("editor", digest="sha256:abc")), "digest"),
        (json.dumps(with_field("editor", digest="sha256:" + "A" * 64)), "digest"),
        (json.dumps(with_field("editor", digest="md5:" + "1" * 64)), "digest"),
        (json.dumps(with_field("serve", note="x")), "exactly"),
        (json.dumps({**lock(), "serve": {"image": "s", "tag": "t"}}), "exactly"),
    ],
)
def test_a_lock_that_could_not_be_pulled_or_names_an_account_is_refused(document, message):
    with pytest.raises(bases.BasesRefused, match=message):
        bases.from_text(document, placeholder=True)


def test_a_lock_that_cannot_be_read_is_refused_by_name(tmp_path):
    with pytest.raises(bases.BasesRefused, match="cannot be read"):
        bases.read(tmp_path / "missing.json")
    written = tmp_path / "bases.json"
    written.write_text(json.dumps(lock()), encoding="utf-8")
    assert bases.read(written, placeholder=True).runner.tag == RUNNER_TAG


def check(locked: bases.Bases, **changes) -> None:
    arguments = {
        "version": library.version(),
        "toolchain": {"runner": RUNNER_TAG, "editor": EDITOR_TAG},
        "serve_tag": serve_tag(),
    }
    arguments.update(changes)
    bases.check(locked, **arguments)


def test_a_lock_that_matches_the_framework_and_the_toolchain_passes():
    check(parsed(lock()))


def test_a_runner_or_editor_tag_the_toolchain_does_not_compute_is_refused():
    with pytest.raises(bases.BasesRefused, match="runner base is locked at tag a"):
        check(parsed(lock()), toolchain={"runner": "z", "editor": EDITOR_TAG})
    with pytest.raises(bases.BasesRefused, match="editor base is locked at tag b"):
        check(parsed(lock()), toolchain={"runner": RUNNER_TAG, "editor": "z"})


def test_a_serve_tag_this_checkout_does_not_compute_or_of_another_version_is_refused():
    with pytest.raises(bases.BasesRefused, match="checkout computes"):
        check(parsed(lock()), serve_tag="0.0.0-other")
    stale = with_field("serve", tag="9.9.9-" + "0" * 64)
    with pytest.raises(bases.BasesRefused, match="not this framework's version"):
        check(parsed(stale), serve_tag=None)
    check(parsed(lock()), serve_tag=None)  # an installed package has no script to ask


def test_the_computed_serve_tag_is_the_one_the_build_script_prints():
    root = Path(library.PACKAGE.parent).resolve().parent
    printed = subprocess.run(
        [sys.executable, str(root / "docker" / "serve" / "build.py"), "--print-tag"],
        capture_output=True,
        text=True,
        check=True,
        cwd=root,
    ).stdout.strip()
    assert printed == f"studyforge-serve:{serve_tag()}"


def test_a_package_that_is_not_a_checkout_computes_no_serve_tag(tmp_path):
    (tmp_path / "src").mkdir()
    assert bases.computed_serve_tag(tmp_path / "src") is None


def test_a_locked_base_is_immutable():
    locked = parsed(lock())
    with pytest.raises(AttributeError):
        locked.serve.digest = "x"  # type: ignore[misc]
    assert copy.deepcopy(locked) == locked
