"""A configuration practice whose reader edits SEVERAL files, graded with pytest.

⭐ **The fixture, once.** The reader edits a settings file (the main file), a memory file and a
hook script; the tests read all three from beside themselves and judge what the files say. One
planted wrong solution per edge case, each a `PlantSpec` whose replacement names the file it
changes, so every file is planted somewhere. ⛔ Nothing here asserts: the gates do.
"""

from __future__ import annotations

from studyforge.exercise import EDGE, MAIN, Case, Origin
from studyforge.exercise.bundle import PlantSpec, Replacement
from studyforge.skills.exercises import Brief, CodeDraft, EditedFile

ALLOW = Case(
    "test_the_settings_allow_the_test_command", MAIN, "the settings allow the test command"
)
SECRETS = Case("test_secrets_are_denied", EDGE, "the settings deny reading secrets")
MEMORY = Case(
    "test_the_memory_names_the_test_command", EDGE, "the memory file names the test command"
)
GUARD = Case(
    "test_the_guard_blocks_with_exit_two", EDGE, "the guard script blocks with exit code 2"
)

SETTINGS = "settings.json"
NOTES = "docs/memory.md"
HOOK = "hooks/guard.sh"

REFERENCE_SETTINGS = (
    '{\n  "permissions": {\n    "allow": ["Bash(npm test)"],\n'
    '    "deny": ["Read(./.env)"]\n  }\n}\n'
)
STARTER_SETTINGS = '{\n  "permissions": {\n    "allow": [],\n    "deny": []\n  }\n}\n'
REFERENCE_NOTES = "# Project\n\nRun `npm test` before every commit.\n"
STARTER_NOTES = "# Project\n"
REFERENCE_HOOK = "#!/bin/sh\necho blocked >&2\nexit 2\n"
STARTER_HOOK = "#!/bin/sh\nexit 0\n"

PLANTS = {
    SECRETS.id: PlantSpec((Replacement(SETTINGS, '"deny": ["Read(./.env)"]', '"deny": []'),)),
    MEMORY.id: PlantSpec(
        (Replacement(NOTES, "Run `npm test` before every commit.", "Be careful."),)
    ),
    GUARD.id: PlantSpec((Replacement(HOOK, "exit 2", "exit 1"),)),
}

TESTS = """import json
from pathlib import Path

HERE = Path(__file__).parent


def test_the_settings_allow_the_test_command():
    settings = json.loads((HERE / "settings.json").read_text())
    assert "Bash(npm test)" in settings["permissions"]["allow"]


def test_secrets_are_denied():
    settings = json.loads((HERE / "settings.json").read_text())
    assert "Read(./.env)" in settings["permissions"]["deny"]


def test_the_memory_names_the_test_command():
    assert "npm test" in (HERE / "docs" / "memory.md").read_text()


def test_the_guard_blocks_with_exit_two():
    assert "exit 2" in (HERE / "hooks" / "guard.sh").read_text()
"""

REPORT = "target/report.xml"


def draft(brief: Brief, **parts) -> CodeDraft:
    """The practice as a draft."""
    ws = brief.places.workspace
    made = CodeDraft(
        title="Project setup",
        lang="json",
        main_file=SETTINGS,
        test_file="test_setup.py",
        run_command=("sh", f"{ws}/{HOOK}"),
        test_command=(
            "python3",
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            f"--junitxml={ws}/{REPORT}",
            f"{ws}/test_setup.py",
        ),
        cases=(ALLOW, SECRETS, MEMORY, GUARD),
        report=REPORT,
        origin=Origin("lessons/basket.md", None),
        statement="Set up the project: allow the test command, deny secrets, name the test\n"
        "command in the memory file and make the guard script block.\n",
        starter=STARTER_SETTINGS,
        reference=REFERENCE_SETTINGS,
        tests=TESTS,
        plants=dict(PLANTS),
        assertions_only=True,
        files={
            NOTES: EditedFile(STARTER_NOTES, REFERENCE_NOTES),
            HOOK: EditedFile(STARTER_HOOK, REFERENCE_HOOK),
        },
    )
    from dataclasses import replace

    return replace(made, **parts)
