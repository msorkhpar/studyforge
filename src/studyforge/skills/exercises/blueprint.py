r"""A project practice's blueprint: the methods to write, shown on the statement page.

**What it does.** Holds `Method`, one entry of the blueprint (the file, the signature, the
contract, the modeling idea, the lesson that taught it, and an optional stub body), writes the
blueprint as the Markdown section appended to the statement (`blueprint_markdown`), checks that
the reference defines every method it names (`undefined`), gives the starter a stub for each
method the previous step does not have yet (`stubbed`), and turns a file new in the step into its
starter by stubbing only the blueprint methods' bodies (`stub_bodies`).

**How you use it.**

    method = Method("planner/model.py", "def add_caps(model, data) -> None", contract, idea,
                    Lesson("3.2 Budget caps", "../budgets/caps.html"), stub="return None")
    statement += blueprint_markdown((method,))
    undefined({"planner/model.py": reference}, (method,))     # [] when the reference has it
    starters = stubbed(starters, (method,))                   # a stub where it was missing
    starter = stub_bodies(reference, "planner/model.py", (method,))  # a new file's starter

**Depends on.** `ast`, `io`, `re` and `tokenize`, and this package's `drafts.AuthoringError`. Standard library only.

## ⭐ GENEROUS ENOUGH TO FINISH WITHOUT THE SOLUTION

⭐ Each method is shown with four things a reader needs and the reference does not say outright:
its **signature**, its **contract** (what goes in, what comes out, what stays true), the
**modeling idea** it needs, and a link to the **lesson** that taught that idea. ⛔ All four are
required, so a blueprint cannot ship an entry that is only a name.

## ⭐ A METHOD THE PREVIOUS STEP LACKS STARTS AS A STUB

⚠️ A step's tests import what the step adds, and a starter without it fails every test of that
file on an import error, which says nothing about the task. ⭐ So a module-level function the
starter does not define is appended to its file as a stub: the signature, the contract as its
docstring, and the `stub` body the manifest gives, such as `return ()`, which fails the step's
tests on an assertion. ⛔ A method inside a class is not stubbed: its class is the previous
step's code, and the snapshot declares it there.

## ⭐ A FILE NEW IN THE STEP STARTS AS THE REFERENCE, ITS BLUEPRINT BODIES STUBBED

⚠️ A file the previous step lacks has no earlier code to start from, and an empty file, or bare
stubs with no imports or constants, leaves the reader to rebuild what the step does not teach.
⭐ So its starter is the step's own file with only the bodies of its blueprint methods replaced:
each keeps its decorators and signature and gets the contract as its docstring and the `stub`
body; imports, constants, classes and every other function stay as the reference has them. ⭐ A
new file with no blueprint method ships unchanged.
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
from dataclasses import dataclass

from studyforge.skills.exercises.drafts import AuthoringError

#: The heading the blueprint is written under, inside the statement.
BLUEPRINT_HEADING = "Blueprint"

#: A signature's name: `def name(` or `async def name(`, after any indentation.
_NAME = re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)\s*\(")

#: The body a stub gets when the manifest gives none.
DEFAULT_STUB = "raise NotImplementedError"


@dataclass(frozen=True, slots=True)
class Lesson:
    """The lesson that taught a method's idea: its title and the link to its page."""

    title: str
    href: str


@dataclass(frozen=True, slots=True)
class Method:
    """One method of the blueprint, as the statement page shows it."""

    file: str
    signature: str
    contract: str
    idea: str
    lesson: Lesson
    stub: str | None = None

    @property
    def name(self) -> str:
        """The function's name, read off its signature."""
        found = _NAME.match(self.signature)
        if found is None:
            raise AuthoringError(
                f"a blueprint signature in '{self.file}' does not start with 'def name(', so "
                f"the method it names cannot be found in the reference"
            )
        return found.group(1)


def blueprint_markdown(methods: tuple[Method, ...]) -> str:
    """Return the blueprint section of the statement, one entry per method, in the given order."""
    if not methods:
        return ""
    out = [f"### {BLUEPRINT_HEADING}", ""]
    out += [
        "Write each method below. The tests check each one by itself and the whole program end "
        "to end, so you may change any other part of the code as you see fit.",
        "",
    ]
    for method in methods:
        out += [
            f"#### `{method.name}` in `{method.file}`",
            "",
            "```python",
            method.signature.rstrip().removesuffix(":"),
            "```",
            "",
            f"- **Contract.** {method.contract.strip()}",
            f"- **Modeling idea.** {method.idea.strip()}",
            f"- **Taught in** [{method.lesson.title}]({method.lesson.href}).",
            "",
        ]
    return "\n".join(out)


def undefined(references: dict[str, str], methods: tuple[Method, ...]) -> list[str]:
    """Return a sentence for each method the reference's file does not define."""
    found = []
    for method in methods:
        text = references.get(method.file)
        if text is None:
            found.append(f"'{method.name}' is in '{method.file}', which is not a source file")
        elif method.name not in _defined(text, method.file):
            found.append(f"the reference's '{method.file}' does not define '{method.name}'")
    return found


def stubbed(starters: dict[str, str], methods: tuple[Method, ...]) -> dict[str, str]:
    """Return the starters with a stub appended for each method its file does not define."""
    out = dict(starters)
    for method in methods:
        text = out.get(method.file, "")
        if method.name in _defined(text, method.file):
            continue
        signature = method.signature.rstrip().removesuffix(":")
        body = (method.stub or DEFAULT_STUB).strip()
        contract = method.contract.strip().replace('"""', "'''")
        stub = f'{signature}:\n    """{contract}"""\n    {body}\n'
        out[method.file] = f"{text.rstrip()}\n\n\n{stub}" if text.strip() else stub
    return out


def stub_bodies(text: str, path: str, methods: tuple[Method, ...]) -> str:
    """Return `text` with the body of each blueprint method of `path` replaced by its stub.

    ⭐ Only a function at module level or directly in a class is a blueprint method; a nested
    function of the same name is part of some other body and is left alone.
    """
    mine = {method.name: method for method in methods if method.file == path}
    if not mine:
        return text
    tree = _parse(text, path)
    found = [
        node
        for parent in (tree, *(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)))
        for node in parent.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name in mine
    ]
    lines = text.splitlines(keepends=True)
    for node in sorted(found, key=lambda one: one.lineno, reverse=True):
        method = mine[node.name]
        row, col = _header_end(lines, node, path)
        indent = " " * (node.col_offset + 4)
        body = (method.stub or DEFAULT_STUB).strip()
        contract = method.contract.strip().replace('"""', "'''")
        head = lines[row - 1][: col + 1]
        stub = f'{head}\n{indent}"""{contract}"""\n{indent}{body}\n'
        lines[row - 1 : node.end_lineno] = [stub]
    return "".join(lines)


def _header_end(
    lines: list[str], node: ast.FunctionDef | ast.AsyncFunctionDef, path: str
) -> tuple[int, int]:
    """The (line, column) of the colon that ends a function's signature, outside any bracket."""
    source = "".join(lines[node.lineno - 1 :])
    depth = 0
    started = False
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.NAME and token.string == "def":
            started = True
        elif started and token.type == tokenize.OP:
            if token.string in "([{":
                depth += 1
            elif token.string in ")]}":
                depth -= 1
            elif token.string == ":" and depth == 0:
                return node.lineno + token.start[0] - 1, token.start[1]
    raise AuthoringError(f"the signature of '{node.name}' in '{path}' has no closing colon")


def _parse(text: str, path: str) -> ast.Module:
    """The module's syntax tree, or an authoring error naming the line that does not parse."""
    try:
        return ast.parse(text, filename=path)
    except SyntaxError as error:
        raise AuthoringError(f"'{path}' does not parse, at line {error.lineno}") from None


def _defined(text: str, path: str) -> set[str]:
    """Every function name a module defines, at module level or in a class."""
    tree = _parse(text, path)
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    }
