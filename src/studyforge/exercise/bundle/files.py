"""The further files a practice's reader edits: reading the key, keeping them apart, showing them.

**What it does.** `read_files` reads a bundle's `files` key (absent is none; present is a
non-empty list of distinct workspace paths), `require_files_apart` refuses an edited file that
shares its path with the main file, the test file, a build file or run output, and `shown` lays
the main file and the further files out as the reference's blocks and the starting code's
blocks. ⭐ An exercise of one file passes no `files` and gets the blocks it always did.
⭐ A project's read-only files (`read_only`) are read and kept apart here too: `read_read_only`,
`require_read_only_apart`, and `read_only_files` and `read_only_record` for what `emit` writes.
⭐ A project's record names its build files read-only too, since its workspace holds them.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from studyforge.describe import describe
from studyforge.exercise.bundle.layout import RUN_OUTPUT_DIRNAME, is_run_output
from studyforge.exercise.errors import ExerciseError
from studyforge.exercise.gates import TESTS
from studyforge.exercise.safety import require_path

if TYPE_CHECKING:
    from studyforge.exercise.bundle.document import Bundle


def read_files(value: object, where: str) -> tuple[str, ...]:
    """Read the further edited files: absent is none, present is non-empty and distinct."""
    if value is None:
        return ()
    if not isinstance(value, list) or not value:
        raise ExerciseError(
            f"{where}: 'files' lists the further files the reader edits beside the main file, "
            f"as a non-empty array of workspace-relative paths, and it is {describe(value)}. "
            f"An exercise of one file leaves the key out."
        )
    paths = tuple(require_path(one, "a file the reader edits", where) for one in value)
    if len(set(paths)) != len(paths):
        raise ExerciseError(f"{where}: 'files' names one file more than once.")
    return paths


def require_files_apart(bundle: Bundle, where: str) -> None:
    """Refuse an edited file that is the main file, the test file, a build file or run output."""
    for path in bundle.files:
        if path in (bundle.main_file, bundle.test_file, *bundle.build):
            raise ExerciseError(
                f"{where}: an edited file shares its path with the main file, the test file or "
                f"a build file, so the workspace would hold one file for two roles."
            )
        if is_run_output(path):
            raise ExerciseError(
                f"{where}: an edited file sits in '{RUN_OUTPUT_DIRNAME}/', which every run "
                f"writes and a corpus ignores, so it would be neither kept nor tracked."
            )


def read_read_only(value: object, where: str) -> tuple[str, ...]:
    """Read a project's read-only files: absent is none, present is non-empty and distinct."""
    if value is None:
        return ()
    if not isinstance(value, list) or not value:
        raise ExerciseError(
            f"{where}: 'read_only' lists a project's read-only files beside the test file, as a "
            f"non-empty array of workspace-relative paths, and it is {describe(value)}."
        )
    paths = tuple(require_path(one, "a read-only file", where) for one in value)
    if len(set(paths)) != len(paths):
        raise ExerciseError(f"{where}: 'read_only' names one file more than once.")
    return paths


def require_read_only_apart(bundle: Bundle, where: str) -> None:
    """Refuse a read-only file that is an edited file, the test file, a build file or run output."""
    for path in bundle.read_only:
        if path in (*bundle.edited, bundle.test_file, *bundle.build) or is_run_output(path):
            raise ExerciseError(
                f"{where}: a read-only file shares its path with a file of another role, or sits "
                f"in '{RUN_OUTPUT_DIRNAME}/', so the workspace would hold one file for two roles."
            )


def read_only_files(base: Path, bundle: Bundle, where: str) -> tuple[tuple[str, bytes], ...]:
    """Each read-only file as the workspace gets it, read from the bundle's `tests/` folder."""
    out = []
    for path in bundle.read_only:
        held = bundle.places.in_bundle(f"{TESTS}/{path}")
        try:
            out.append((bundle.places.in_workspace(path), (base / held).read_bytes()))
        except OSError:
            raise ExerciseError(
                f"{where}: the bundle declares a read-only file at '{held}' and holds none."
            ) from None
    return tuple(out)


def read_only_record(bundle: Bundle) -> dict:
    """The record's `read_only` key, each path as the corpus root sees it; empty for most.

    ⭐ A project's build files (`pytest.ini`) follow its read-only files: the workspace holds
    them, every file of a project is visible, and none is the reader's to edit. ⚠️ The bundle
    still keeps them in the build role, so they ship from `build/` and are digested as such.
    """
    if not bundle.read_only:
        return {}
    shown = (*bundle.read_only, *bundle.build)
    return {"read_only": [bundle.places.in_workspace(path) for path in shown]}


def require_try_file(bundle: Bundle, where: str) -> None:
    """Refuse a try-it file that is not one of `files`, or a Run that would grade like Submit."""
    if bundle.try_file is None:
        return
    if bundle.try_file not in bundle.files:
        raise ExerciseError(
            f"{where}: 'try_file' names a file that 'files' does not list. The try-it file is one "
            f"of the files the reader edits, so it is listed there too."
        )
    if bundle.run_command == bundle.test_command:
        raise ExerciseError(
            f"{where}: 'try_file' is set but 'run_command' equals 'test_command'. Run executes "
            f"the try-it file and Submit grades; the two commands are different."
        )


#: The language a further file is shown in, by its suffix; a file with none of these is shown in
#: the practice's own language. ⚠️ A display word for the page, never a decision about the file.
_FILE_LANGS = {
    ".json": "json",
    ".md": "markdown",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".sh": "bash",
    ".xml": "xml",
}


def _lang_of(path: str, default: str) -> str:
    """Return the language a further file is shown in, by its suffix."""
    return _FILE_LANGS.get(PurePosixPath(path).suffix.lower(), default)


def shown(
    lang: str, reference: str, starter: str, more: tuple[tuple[str, str, str], ...]
) -> tuple[list[dict], list[dict]]:
    """Return the reference's blocks and the starting code's blocks, further files after the main.

    ⭐ `more` is `(path, starter, reference)` for each further file: each follows the main
    file's own code under a line naming it.
    """
    reference_blocks = [{"type": "code", "lang": lang, "text": reference}]
    starting_blocks = [{"type": "code", "lang": lang, "text": starter}]
    for path, text, reference_text in more:
        named = {"type": "para", "text": f"File: {path}"}
        shown_as = _lang_of(path, lang)
        reference_blocks += [named, {"type": "code", "lang": shown_as, "text": reference_text}]
        starting_blocks += [named, {"type": "code", "lang": shown_as, "text": text}]
    return reference_blocks, starting_blocks
