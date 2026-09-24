"""Mirror of `src/studyforge/execute/instance.py` (R12) — the names a checkout recorded.

⭐ `W465`: a second instance of one corpus is found by what IT recorded, and a
checkout that recorded nothing is found exactly as before.
"""

from __future__ import annotations

import pytest

from studyforge.execute import RunRefused, container_for, editor_container_for, instance

SOURCE = "demo"


def recorded_file(root, content: str) -> None:
    target = root / instance.INSTANCE_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def second() -> dict[str, str]:
    return {
        instance.PROJECT: "studyforge-demo-second",
        instance.EDITOR_PORT: "18443",
        instance.EDITOR_NAME: "demo-second-editor",
        instance.RUNNER_NAME: "demo-second-runner",
    }


def test_a_checkout_that_recorded_nothing_is_found_by_the_names_it_always_had(tmp_path):
    names = instance.recorded(tmp_path, SOURCE)
    assert names == instance.Names(container_for(SOURCE), editor_container_for(SOURCE))


def test_a_second_instance_is_found_by_the_names_it_recorded(tmp_path):
    recorded_file(tmp_path, instance.text(second(), header="# a header\n"))
    names = instance.recorded(tmp_path, SOURCE)
    assert names == instance.Names("demo-second-runner", "demo-second-editor")


def test_a_name_that_is_not_one_safe_word_is_read_as_absent(tmp_path):
    recorded_file(tmp_path, f"{instance.RUNNER_NAME}=a;b\n{instance.EDITOR_NAME}=-x\n")
    names = instance.recorded(tmp_path, SOURCE)
    assert names == instance.Names(container_for(SOURCE), editor_container_for(SOURCE))


def test_the_defaults_are_the_values_every_instance_always_had():
    values = instance.defaults(SOURCE, port=8443)
    assert values == {
        instance.PROJECT: "studyforge-demo",
        instance.EDITOR_PORT: "8443",
        instance.EDITOR_NAME: editor_container_for(SOURCE),
        instance.RUNNER_NAME: container_for(SOURCE),
    }
    # ⭐ The editor's default is still compose's own derivation from the project.
    assert values[instance.EDITOR_NAME] == f"{values[instance.PROJECT]}-editor-1"


def test_the_file_holds_every_variable_once_and_reads_back_as_written():
    text = instance.text(second(), header="# a header\n")
    assert text.startswith("# a header\n" + instance.HOLDS)
    assert instance.parsed(text) == second()


@pytest.mark.parametrize(
    ("variable", "value"),
    [
        # ⛔ The bind is not a value: an address in the port is refused.
        (instance.EDITOR_PORT, "0.0.0.0:8443"),
        (instance.EDITOR_PORT, "80"),
        (instance.EDITOR_PORT, "70000"),
        (instance.EDITOR_PORT, "8443 "),
        (instance.EDITOR_NAME, "two words"),
        (instance.RUNNER_NAME, "a/b"),
        (instance.PROJECT, "Upper"),
        (instance.PROJECT, "a.b"),
    ],
)
def test_a_value_compose_would_read_otherwise_is_refused(variable, value):
    values = dict(second(), **{variable: value})
    with pytest.raises(RunRefused):
        instance.text(values, header="")


def test_a_record_missing_a_variable_is_refused():
    values = second()
    del values[instance.RUNNER_NAME]
    with pytest.raises(RunRefused, match="missing"):
        instance.checked(values)
