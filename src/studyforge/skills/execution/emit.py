r"""The smallest deterministic YAML this framework's generated files need.

**What it does.** Turns mappings, lists and scalars into compose-shaped YAML,
with every string that YAML would read as something else quoted.

**How you use it.** `emit(document)` returns the text, newline-terminated.

**Depends on.** The standard library. ⛔ Framework source takes **no
third-party package** (R11's neighbour rule and this repository's floor), so a
YAML library is not available to it and is not wanted: what is emitted here is
a document this framework composed, never one it parsed.

## ⚠️ WHAT THIS DELIBERATELY IS NOT

⛔ **It is not a YAML implementation and must not grow into one.** No anchors,
no tags, no multi-line scalars, no flow style beyond the empty collection. ⭐ A
value it cannot write is a value a generated file should not carry, and the
honest response to one is a refusal upstream rather than a feature here.

⭐ **Quoting is decided by the value, not by taste.** `no` is YAML 1.1's false
and a restart policy of `no` that arrived unquoted would become a boolean; a
string carrying a colon would become a mapping. ⚠️ Both are silent, and both
produce a file that parses and does the wrong thing.
"""

from __future__ import annotations

from collections.abc import Mapping

#: Bare words YAML reads as something other than a string. ⛔ `no` is the one
#: that matters here and the rest are its neighbours: a vocabulary with one
#: member is a vocabulary that grows by surprise.
RESERVED = ("no", "yes", "on", "off", "true", "false", "null", "none", "~")

#: Characters that make a bare scalar ambiguous to a YAML reader.
AMBIGUOUS = ":#\"'\n\t"


def emit(document: object) -> str:
    """One document as YAML text."""
    return _emit(document, 0)


def _emit(value: object, depth: int) -> str:
    """`value` at `depth`, as whole lines."""
    pad = "  " * depth
    if isinstance(value, Mapping):
        return "".join(f"{pad}{key}:{_after(item, depth)}" for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return "".join(f"{pad}-{_after(item, depth)}" for item in value)
    return f"{pad}{scalar(value)}\n"


def _after(value: object, depth: int) -> str:
    """Write what follows a key or a dash: inline when scalar, nested when not."""
    if isinstance(value, Mapping):
        return "\n" + _emit(value, depth + 1) if value else " {}\n"
    if isinstance(value, (list, tuple)):
        return "\n" + _emit(value, depth + 1) if value else " []\n"
    return f" {scalar(value)}\n"


def scalar(value: object) -> str:
    """One scalar, quoted wherever YAML would otherwise read it as something else."""
    if value is True or value is False:
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if text == "" or text != text.strip() or any(one in text for one in AMBIGUOUS):
        # ⛔ A line break inside double quotes is FOLDED into a space by a YAML
        # reader, so a multi-line value (a build argument listing one file per
        # line) is written escaped, and reads back byte for byte.
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return '"' + escaped.replace("\n", "\\n").replace("\t", "\\t") + '"'
    if text.lower() in RESERVED:
        return f'"{text}"'
    return text
