"""The framework names no corpus's image profile: a profile is a name the corpus declares.

⭐ R1 for the toolchain's profiles. The one place a profile's name is written is a fixture or a
test, as data a corpus declares; no module of the framework, no skill and no recipe under
`src/` spells one. ⛔ A name hard-coded in the plan would pass every test that uses the same name,
so this reads the source for it.
"""

from __future__ import annotations

from pathlib import Path

from tests.support import repository_root

#: The names of the profiles the toolchain ships a course may declare. Spelled here, in a test.
PROFILES = ("claude-sdks", "jvm-frameworks", "fixture-libs", "fixture-packages", "kotlin-editor")


TEXT = {".py", ".md", ".json", ".sh", ".txt", ".yaml", ".toml"}


def source_files(root: Path):
    for path in sorted((root / "src").rglob("*")):
        if path.is_file() and path.suffix in TEXT:
            yield path


def test_no_file_under_src_names_a_toolchain_profile():
    found = [
        f"{path.relative_to(repository_root()).as_posix()}: {name}"
        for path in source_files(repository_root())
        for name in PROFILES
        if name in path.read_text(encoding="utf-8", errors="replace")
    ]
    assert found == []


def test_a_name_in_the_source_would_be_seen(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "plan.py").write_text('PROFILE = "claude-sdks"\n', encoding="utf-8")
    seen = [
        name
        for path in source_files(tmp_path)
        for name in PROFILES
        if name in path.read_text(encoding="utf-8")
    ]
    assert seen == ["claude-sdks"]
