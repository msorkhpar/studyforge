"""The record's file keys beside `main_path`: the files the reader edits, the try-it file, and a
project's read-only files.

**What it does.** `files_in`, `try_file_in` and `read_only_in` each read one key of an `exercise`
object: absent is `None`, present is checked and returned as workspace paths spelled from the
corpus root. ⛔ Each refuses a path that is not safe, a file named twice, and a file given two
roles, naming the key and never the value.

**How you use it.** `record.from_document` calls all three for a `code` record and nothing else.

**Depends on.** `safety` for what a path may be, and `errors`. Standard library only.

## ⭐ A PROJECT IS A PRACTICE THAT NAMES READ-ONLY FILES

⭐ `read_only` lists what a project practice shows the reader and grades them with, beyond the
one `test_path`: its other tests, their fixtures, its data and the expected report. ⛔ None of them
is the reader's to edit, so none may also be `main_path`, `test_path` or one of `files`.
"""

from __future__ import annotations

from studyforge.exercise.errors import ExerciseError
from studyforge.exercise.safety import require_path


def files_in(value: dict, where: str) -> tuple[str, ...] | None:
    """Read `files`: absent is none; present is a non-empty list of distinct workspace paths."""
    if "files" not in value:
        return None
    listed = value["files"]
    if not isinstance(listed, list) or not listed:
        raise ExerciseError(
            f"{where}: 'files' lists the further files the reader edits, as a non-empty array "
            f"of paths. A practice of one file leaves the key out."
        )
    paths = tuple(require_path(one, "a file the reader edits", where) for one in listed)
    taken = {value.get("main_path"), value.get("test_path")}
    if len(set(paths)) != len(paths) or any(path in taken for path in paths):
        raise ExerciseError(
            f"{where}: 'files' names a file twice, or one that is already the main file or "
            f"the test file."
        )
    return paths


def try_file_in(value: dict, where: str) -> str | None:
    """Read `try_file`: absent is none; present is one of `files`, and Run is not the grader."""
    if "try_file" not in value:
        return None
    path = require_path(value["try_file"], "try_file", where)
    if path not in (value.get("files") or ()):
        raise ExerciseError(
            f"{where}: 'try_file' names a file that 'files' does not list. The try-it file is one "
            f"of the files the reader edits, so it is listed there too."
        )
    if "test_command" in value and value.get("run_command") == value["test_command"]:
        raise ExerciseError(
            f"{where}: 'try_file' is set but 'run_command' equals 'test_command'. Run executes "
            f"the try-it file and Submit grades; the two commands are different."
        )
    return path


def read_only_in(value: dict, where: str) -> tuple[str, ...] | None:
    """Read `read_only`: absent is none; present is a non-empty list of distinct paths."""
    if "read_only" not in value:
        return None
    listed = value["read_only"]
    if not isinstance(listed, list) or not listed:
        raise ExerciseError(
            f"{where}: 'read_only' lists a project's read-only files, as a non-empty array of "
            f"paths. A practice that is not a project leaves the key out."
        )
    paths = tuple(require_path(one, "a read-only file", where) for one in listed)
    taken = {value.get("main_path"), value.get("test_path"), *(value.get("files") or ())}
    if len(set(paths)) != len(paths) or any(path in taken for path in paths):
        raise ExerciseError(
            f"{where}: 'read_only' names a file twice, or one that is already the main file, the "
            f"test file or a file the reader edits."
        )
    return paths
