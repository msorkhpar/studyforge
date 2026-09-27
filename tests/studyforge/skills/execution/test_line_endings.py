"""Every file the execution skill writes has LF line ends, on every host.

⛔ Python's text mode writes `\\r\\n` for `\\n` on Windows. The skill's files are
read by compose and by containers, and each is hashed (the hand-edit record, the
site image's tag), so a Windows publisher would otherwise write other bytes than
a Linux one from the same declarations: a moved tag, and a record that reads as
hand-edited. ⭐ So every text write in the package names `newline="\\n"`.
"""

from __future__ import annotations

import ast
from pathlib import Path

import studyforge.skills.execution as package

PACKAGE = Path(package.__file__).parent


def unpinned(tree: ast.AST) -> list[int]:
    """The lines of every `write_text` call that does not name `newline="\\n"`."""
    return [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "write_text"
        and not any(
            keyword.arg == "newline"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value == "\n"
            for keyword in node.keywords
        )
    ]


def test_every_text_write_in_the_skill_writes_lf():
    found = {
        path.name: lines
        for path in sorted(PACKAGE.glob("*.py"))
        if (lines := unpinned(ast.parse(path.read_text(encoding="utf-8"))))
    }
    assert found == {}, f"a text write that is CRLF on Windows: {found}"


def test_the_check_can_say_no():
    assert unpinned(ast.parse('p.write_text(t, encoding="utf-8")')) == [1]
    assert unpinned(ast.parse('p.write_text(t, encoding="utf-8", newline="\\n")')) == []
