"""Mirror of `src/studyforge/corpus/manifest/live.py` (R12): the `live` key.

⭐ An optional block naming the one API host a live run may reach, the NAME of the variable a
reader's key is given under, and what may run live. Absent is the manifest as it was; present, it
is narrow: a bare host, a variable's name, argv commands, corpus-relative paths. The names below
are made up: no code knows a host or a variable.
"""

from __future__ import annotations

import pytest

from studyforge.corpus.manifest import KEY_VERSIONS, ManifestError, from_document, versions_needed
from studyforge.corpus.manifest.live import Live, LiveExample
from studyforge.exercise import ExerciseError, require_command, require_path

BASE = {
    "corpus_api": 8,
    "source": "example-corpus",
    "title": "Example Corpus",
    "levels": ["section"],
    "variants": ["python"],
    "exercises": True,
    "runtimes": ["python"],
    "placement": "tree",
    "content": {"include": ["*/README*.md"], "exclude": []},
}
EXAMPLE = {"path": "examples/a/run.py", "command": ["python3", "examples/a/run.py"]}
LIVE = {"host": "api.example.test", "key_variable": "EXAMPLE_API_KEY", "examples": [EXAMPLE]}


def manifest(**keys):
    return from_document({**BASE, **keys})


def refused(live, match):
    with pytest.raises(ManifestError, match=match):
        manifest(live=live)


def test_an_absent_live_block_is_none_and_the_manifest_reads_as_before():
    assert manifest().live is None


def test_a_declared_block_is_read_whole():
    found = manifest(live={**LIVE, "practices": ["01-a/unit-01/practice-1"]}).live
    assert found == Live(
        "api.example.test",
        "EXAMPLE_API_KEY",
        (LiveExample("examples/a/run.py", ("python3", "examples/a/run.py")),),
        ("01-a/unit-01/practice-1",),
    )


@pytest.mark.parametrize(
    "host",
    [
        "",
        "Api.Example.test",
        "https://api.example.test",
        "api.example.test:443",
        "a.test/x",
        "user@api.example.test",
        "127.0.0.1",
        "10.0.0.1",
        "localhost",
        "-a.example.test",
        3,
        None,
    ],
)
def test_a_host_that_is_not_a_bare_lower_case_name_is_refused(host):
    refused({**LIVE, "host": host}, "'live.host' must be a bare lower-case hostname")


@pytest.mark.parametrize("name", ["", "lower", "1A", "A B", "A=1", "A" * 65, "KEY;rm", 3, None])
def test_a_key_variable_that_is_no_name_is_refused(name):
    refused({**LIVE, "key_variable": name}, "'live.key_variable' must be the NAME")


def test_a_key_is_never_a_declaration_a_value_shaped_name_would_still_only_be_a_name():
    # ⭐ The variable's NAME is all this block can hold: a value with a lower-case letter, a
    # dash or a space cannot be written into it.
    refused({**LIVE, "key_variable": "sk-ant-api03-abc"}, "must be the NAME")


@pytest.mark.parametrize(
    "entry",
    [
        {"path": "../x.py", "command": ["python3", "x.py"]},
        {"path": "/abs/x.py", "command": ["python3", "x.py"]},
        {"path": "a/-rf", "command": ["python3", "x.py"]},
        {"path": "a\\b.py", "command": ["python3", "x.py"]},
        {"path": "a/x.py", "command": "python3 x.py"},
        {"path": "a/x.py", "command": []},
        {"path": "a/x.py", "command": ["python3", "a b"]},
        {"path": "a/x.py", "command": ["python3", "x.py;ls"]},
        {"path": "a/x.py", "command": ["python3", "$HOME"]},
        {"path": "a/x.py", "command": ["python3", "/etc/passwd"]},
        {"path": "a/x.py", "command": ["python3", "../x.py"]},
        {"path": "a/x.py"},
        {"command": ["python3", "x.py"]},
        {"path": "a/x.py", "command": ["python3", "x.py"], "env": "A=1"},
    ],
)
def test_an_example_that_is_not_a_path_and_an_argv_is_refused(entry):
    refused({**LIVE, "examples": [entry]}, "live.examples")


def test_the_shapes_agree_with_what_the_runner_refuses():
    # ⭐ `live.py` spells `exercise.safety`'s sets itself (that package imports this one); this
    # keeps the two from drifting: whatever one refuses the other refuses.
    samples = ["a/x.py", "../x", "-rf", "a b", "a;b", "a/b-c_d.e", "/abs", "a\\b", "a/./b", ""]
    for sample in samples:
        try:
            require_path(sample, "path", "t")
            runs = True
        except ExerciseError:
            runs = False
        assert runs == (EXAMPLE["path"] == sample or _declares(sample)), sample
    for token in ["x.py", "-q", "k=v", "a b", "a;b", "$X", "/abs", "../x", "a/../b", "a:b@c+d"]:
        try:
            require_command(["python3", token], "c", "t")
            runs = True
        except ExerciseError:
            runs = False
        assert runs == _declares_command(token), token


def _declares(path):
    try:
        manifest(live={**LIVE, "examples": [{"path": path, "command": ["python3", "x.py"]}]})
    except ManifestError:
        return False
    return True


def _declares_command(token):
    try:
        manifest(live={**LIVE, "examples": [{"path": "a/x.py", "command": ["python3", token]}]})
    except ManifestError:
        return False
    return True


@pytest.mark.parametrize("key", ["", "Upper/key", "one", "a//b", "a/b/", "a b/c", "../a/b", 3])
def test_a_practice_that_is_no_practice_key_is_refused(key):
    refused({**LIVE, "practices": [key]}, "live.practices")


def test_a_block_naming_nothing_to_run_or_naming_twice_is_refused():
    refused({"host": "api.example.test", "key_variable": "EXAMPLE_API_KEY"}, "names no example")
    refused({**LIVE, "examples": [EXAMPLE, EXAMPLE]}, "names a path twice")
    refused({**LIVE, "practices": ["a-b/c-d", "a-b/c-d"]}, "names a key twice")


def test_a_block_with_a_key_it_does_not_carry_is_refused_by_name():
    refused({**LIVE, "url": "https://api.example.test"}, "unknown keys")
    refused(["not", "an", "object"], "'live' must be an object")


def test_live_runs_need_the_runtimes_they_run_in():
    without = {k: v for k, v in BASE.items() if k != "runtimes"}
    with pytest.raises(ManifestError, match="declares 'live' and no 'runtimes'"):
        from_document({**without, "exercises": False, "live": LIVE})


def test_the_key_is_gated_at_the_version_this_build_already_writes():
    assert KEY_VERSIONS[(None, "live")] == 8
    assert versions_needed({**BASE, "live": LIVE}) == [("runtimes", 4), ("live", 8)]
    with pytest.raises(ManifestError, match="uses 'live', which corpus_api 8 added"):
        manifest(corpus_api=7, live=LIVE)
