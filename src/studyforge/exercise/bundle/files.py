"""The further files a practice's reader edits: reading the key, keeping them apart, showing them.

**What it does.** `read_files` reads a bundle's `files` key (absent is none; present is a
non-empty list of distinct workspace paths), `require_files_apart` refuses an edited file that
shares its path with the main file, the test file, a build file or run output, and `shown` lays
the main file and the further files out as the reference's blocks and the starting code's
blocks. ⭐ An exercise of one file passes no `files` and gets the blocks it always did.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from studyforge.describe import describe
from studyforge.exercise.bundle.layout import RUN_OUTPUT_DIRNAME, is_run_output
from studyforge.exercise.errors import ExerciseError
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
