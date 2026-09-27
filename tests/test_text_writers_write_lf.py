"""Every text writer in `src/` names its line ending: LF on every host, never the platform's.

⭐ **Why.** A text file opened for writing without `newline=` translates each `\\n`
into `os.linesep`, so the same build writes CRLF on Windows and LF on Linux: a
generated page, a cache, a progress record or a scaffolded file would differ by
host and read as changed to git. ⭐ Passing `newline="\\n"` (or writing bytes)
makes the bytes the same on every host, and changes nothing on Linux.

⛔ **The population is DERIVED**: every call in `src/` that opens text for
writing — `Path.write_text`, `open`/`Path.open`/`os.fdopen`/`io.open` with a
mode that writes and is not binary, the `tempfile` text files and
`io.TextIOWrapper` — is read off the syntax tree, so the next writer is inside
the sweep without anybody adding it. ⚠️ Only a literal mode is read: a mode
held in a variable is not a writer this can see, and `src/` holds none.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "src"

#: Calls whose mode argument sits at this position when it is passed positionally.
MODE_AT = {"open": 1, "fdopen": 1}
#: A `.open` on one of these modules is the built-in's shape (`io.open(file, mode)`).
MODULE_OPENERS = {"io", "codecs"}
#: Files `tempfile` opens, whose mode comes first and defaults to binary.
TEMPFILES = {"NamedTemporaryFile", "TemporaryFile", "SpooledTemporaryFile"}


def _name(call: ast.Call) -> tuple[str | None, ast.expr | None]:
    """The called name and, for an attribute, what it is called on."""
    func = call.func
    if isinstance(func, ast.Attribute):
        return func.attr, func.value
    if isinstance(func, ast.Name):
        return func.id, None
    return None, None


def _mode(call: ast.Call, position: int) -> ast.expr | None:
    for keyword in call.keywords:
        if keyword.arg == "mode":
            return keyword.value
    return call.args[position] if len(call.args) > position else None


def _writes_text(mode: ast.expr | None) -> bool:
    """Whether a literal mode opens text for writing."""
    if not (isinstance(mode, ast.Constant) and isinstance(mode.value, str)):
        return False
    return "b" not in mode.value and any(flag in mode.value for flag in "wax+")


def _is_text_writer(call: ast.Call) -> bool:
    name, receiver = _name(call)
    if name == "write_text":
        # ⭐ A method: `Path.write_text`. A bare name is a helper of our own.
        return receiver is not None
    if name == "TextIOWrapper":
        return True
    if name in TEMPFILES:
        return _writes_text(_mode(call, 0))
    if name == "open" and receiver is not None:
        if isinstance(receiver, ast.Name) and receiver.id == "os":
            return False  # `os.open` is a descriptor, never text
        builtin_shape = isinstance(receiver, ast.Name) and receiver.id in MODULE_OPENERS
        return _writes_text(_mode(call, 1 if builtin_shape else 0))
    if name in MODE_AT and (receiver is None or name == "fdopen"):
        return _writes_text(_mode(call, MODE_AT[name]))
    return False


def platform_newline_writers(source: str) -> list[int]:
    """The lines of every text writer in `source` that names no `newline=`."""
    return sorted(
        node.lineno
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and _is_text_writer(node)
        and not any(keyword.arg == "newline" for keyword in node.keywords)
    )


def sweep(root: Path) -> list[str]:
    return [
        f"{path.relative_to(root).as_posix()}:{line}"
        for path in sorted(root.rglob("*.py"))
        for line in platform_newline_writers(path.read_text(encoding="utf-8"))
    ]


def test_no_text_writer_in_src_writes_the_platform_line_ending():
    found = sweep(SOURCE)
    assert found == [], (
        'a text writer names no newline="\\n", so it writes CRLF on Windows: ' + ", ".join(found)
    )


@pytest.mark.parametrize(
    "line",
    [
        'path.write_text(text, encoding="utf-8")',
        'open(path, "w", encoding="utf-8")',
        'open(path, mode="a", encoding="utf-8")',
        'path.open("x", encoding="utf-8")',
        'path.open(mode="w")',
        'os.fdopen(handle, "w", encoding="utf-8")',
        'io.open(path, "w")',
        'tempfile.NamedTemporaryFile("w", suffix=".txt")',
        'tempfile.NamedTemporaryFile(mode="w+")',
        "io.TextIOWrapper(stream)",
    ],
)
def test_a_text_writer_without_newline_is_found(line):
    assert platform_newline_writers(line) == [1]


@pytest.mark.parametrize(
    "line",
    [
        'path.write_text(text, encoding="utf-8", newline="\\n")',
        'open(path, "w", encoding="utf-8", newline="\\n")',
        'path.open("x", encoding="utf-8", newline="\\n")',
        'io.TextIOWrapper(stream, newline="\\n")',
        "path.write_bytes(data)",
        'open(path, "wb")',
        'open(path, "xb")',
        "open(path)",
        'path.open("rb")',
        'path.open(encoding="utf-8")',
        "os.open(path, os.O_RDONLY)",
        "tempfile.NamedTemporaryFile()",
        'archive.open(info, "w")',
        "write_text(path, body)",
        "open(path, chosen)",
    ],
)
def test_a_binary_reader_or_lf_writer_is_left_alone(line):
    assert platform_newline_writers(line) == []
