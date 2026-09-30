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
ONES = "sha256:" + "1" * 64
TWOS = "sha256:" + "2" * 64
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
        "runner": {"image": bases.PUBLISHED["runner"], "tag": RUNNER_TAG, "digest": ONES},
        "editor": {"image": bases.PUBLISHED["editor"], "tag": EDITOR_TAG, "digest": TWOS},
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
    runner = f"studyforge-code-toolchain-runner:{RUNNER_TAG}@sha256:{'1' * 64}"
    assert locked.runner.reference == runner
    assert locked.serve.reference == f"studyforge-serve:{serve_tag()}@{ZEROS}"
    assert bases.key(locked.editor) == "2" * bases.KEY_DIGITS


def test_the_published_names_are_the_prefixed_ones_and_the_serve_name_stays():
    assert bases.PUBLISHED == {
        "serve": "studyforge-serve",
        "runner": "studyforge-code-toolchain-runner",
        "editor": "studyforge-code-toolchain-editor",
    }
    locked = parsed(lock())
    names = (locked.serve.image, locked.runner.image, locked.editor.image)
    assert names == tuple(bases.PUBLISHED.values())


@pytest.mark.parametrize("kind", ["runner", "editor"])
def test_the_retired_bare_name_is_refused_and_the_new_one_is_named(kind):
    with pytest.raises(bases.BasesRefused) as refused:
        parsed(with_field(kind, image=kind))
    assert f"studyforge-code-toolchain-{kind}" in str(refused.value)
    assert "no longer publishes" in str(refused.value)


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


# A runner or editor base built on a runtime set the course may only be part of.

PINNED = ("java", "maven", "node", "python")
SUFFIX = {"runner": "amd64-f8f1db0be48a", "editor": "amd64-14e3f747ce03"}


def tags_for(runtimes) -> dict[str, str]:
    """A toolchain stand-in: four pinned runtimes, written in its order, all others refused."""
    unknown = [one for one in runtimes if one not in PINNED]
    if unknown:
        raise ValueError("not pinned")
    ordered = "-".join(one for one in PINNED if one in runtimes)
    return {kind: f"{ordered}-{suffix}" for kind, suffix in SUFFIX.items()}


def polyglot(runner: str | None = None, editor: str | None = None) -> bases.Bases:
    every = tags_for(PINNED)
    return parsed(
        lock(
            runner={**lock()["runner"], "tag": runner or every["runner"]},
            editor={**lock()["editor"], "tag": editor or every["editor"]},
        )
    )


def superset_check(locked: bases.Bases, declared=("java", "maven")) -> None:
    exact = tags_for(declared)
    check(locked, toolchain=exact, declared=declared, tags_for=tags_for)


def test_a_base_locked_at_exactly_the_declared_set_is_accepted():
    exact = tags_for(("java", "maven"))
    locked = polyglot(exact["runner"], exact["editor"])
    superset_check(locked)


def test_a_base_built_on_a_superset_of_the_declared_set_is_accepted():
    superset_check(polyglot())
    superset_check(polyglot(), declared=("python",))


def test_a_base_built_on_a_set_that_lacks_a_declared_runtime_is_refused_by_name():
    exact = tags_for(("java", "maven"))
    with pytest.raises(bases.BasesRefused, match=r"lacks .*\['node'\]"):
        superset_check(polyglot(exact["runner"], exact["editor"]), declared=("java", "node"))
    with pytest.raises(bases.BasesRefused, match=r"lacks .*\['node', 'python'\]"):
        superset_check(polyglot(exact["runner"], exact["editor"]), declared=("node", "python"))


def test_a_runtime_the_toolchain_does_not_know_is_refused_and_named():
    locked = polyglot("java-cobol-amd64-f8f1db0be48a")
    with pytest.raises(bases.BasesRefused, match=r"does not know: \['cobol'\]"):
        superset_check(locked)


@pytest.mark.parametrize(
    ("tag", "message"),
    [
        ("java-java-maven-amd64-f8f1db0be48a", "repeats"),
        ("maven-java-amd64-f8f1db0be48a", "computes"),
        ("amd64-f8f1db0be48a", "does not name a runtime set"),
        ("_amd64-f8f1db0be48a", "does not name a runtime set"),
        ("java--maven-amd64-f8f1db0be48a", "does not name a runtime set"),
        ("java-maven-arm64-f8f1db0be48a", "computes"),
    ],
)
def test_a_malformed_repeated_or_reordered_runtime_segment_is_refused(tag, message):
    with pytest.raises(bases.BasesRefused, match=message):
        superset_check(polyglot(runner=tag))


def test_a_superset_tag_with_another_suffix_is_refused():
    with pytest.raises(bases.BasesRefused, match="computes java-maven-node-python-amd64-f8f1"):
        superset_check(polyglot(runner="java-maven-node-python-amd64-000000000000"))
    with pytest.raises(bases.BasesRefused, match="editor base is locked"):
        superset_check(polyglot(editor="java-maven-node-python-amd64-f8f1db0be48a"))


def test_without_a_toolchain_to_ask_only_the_exact_tag_is_accepted():
    with pytest.raises(bases.BasesRefused, match="runner base is locked at tag"):
        check(polyglot(), toolchain=tags_for(("java", "maven")))
