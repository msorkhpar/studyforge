"""The shapes the origin tell was decided on, and the two spellings it retired.

**What it does.** Holds the probe corpus by letter, each with what the tell
must answer for it, and the superseded token match that both earlier spellings
used.

**How you use it.** `PROBES[label]` is `(source, is_reader)`;
`_token_tell(source, BY_NAME_SPELLING)` re-runs a retired tell.

**Depends on.** `ast`. ⛔ **Dead as an implementation, live as a control** —
nothing that ships imports this module, and `test_tell.py` is its only reader.
"""

import ast

#
# ⭐ **The probe shapes, lettered** so the decision's record and this file name
# the same rows. Every one of them is run three ways below:
# against the tell that ships, and against both superseded spellings.
#
READER, DELEGATES = True, False
PROBES: dict[str, tuple[str, bool]] = {
    "A import json / json.loads": (
        "import json\n\n\ndef read(text):\n    return json.loads(text)\n",
        READER,
    ),
    "B import json / json.load": (
        "import json\n\n\ndef read(handle):\n    return json.load(handle)\n",
        READER,
    ),
    "C from json import loads / loads": (
        "from json import loads\n\n\ndef read(text):\n    return loads(text)\n",
        READER,
    ),
    "D from json import load / load": (
        "from json import load\n\n\ndef read(handle):\n    return load(handle)\n",
        READER,
    ),
    "E import json as j / j.load": (
        "import json as j\n\n\ndef read(handle):\n    return j.load(handle)\n",
        READER,
    ),
    "F from archive.document import load / load": (
        "from studyforge.archive.document import load\n\n\n"
        "def read(paths):\n    return [load(path) for path in paths]\n",
        DELEGATES,
    ),
    "G from archive import document / document.load": (
        "from studyforge.archive import document\n\n\n"
        "def read(paths):\n    return [document.load(path) for path in paths]\n",
        DELEGATES,
    ),
    "H own load, and json.loads beside it": (
        "import json\n\n\ndef load(path):\n    return json.loads(path.read_text())\n\n\n"
        "def read(paths):\n    return [load(path) for path in paths]\n",
        READER,
    ),
    "I own load, no json anywhere": (
        "def load(path):\n    return path.read_text()\n\n\n"
        "def read(paths):\n    return [load(path) for path in paths]\n",
        DELEGATES,
    ),
    "J from json import load, then shadowed": (
        "from json import load\n\n\ndef load(path):\n    return path.read_text()\n\n\n"
        "def read(paths):\n    return [load(path) for path in paths]\n",
        READER,
    ),
    "K an attribute on something unimported": (
        "class Reader:\n    def read(self, handle):\n        return self.load(handle)\n",
        DELEGATES,
    ),
    "L a load on the result of a call": (
        "import json\n\n\ndef write(document, path):\n"
        "    path.write_text(json.dumps(document))\n\n\n"
        "def read(source):\n    return source.open().load()\n",
        DELEGATES,
    ),
}


def _token_tell(source: str, spellings: tuple[str, ...]) -> bool:
    """The superseded tell: match call *tokens* against `spellings`.

    ⛔ **Dead as an implementation, live as a control.** The tell was decided
    by what each spelling got wrong, and *"the old one missed two readers"* is
    a claim until something runs it. ⚠️ It records an attribute call twice — as
    its bare name and, on a plain module name, as `module.name` — which is what
    let `("loads", "json.load")` mean `json`'s `load` and is exactly why it
    could not see `j.load`.
    """
    called: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            called.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            called.add(node.func.attr)
            if isinstance(node.func.value, ast.Name):
                called.add(f"{node.func.value.id}.{node.func.attr}")
    return any(spelling in called for spelling in spellings)


#: The by-name spelling. ⛔ Two false positives: it reads delegation as decoding.
BY_NAME_SPELLING = ("loads", "load")
#: The later narrowing. ⛔ Two false negatives, and a false negative in a
#: coverage check is the silent one.
NARROWED_SPELLING = ("loads", "json.load")

#: The eight shapes the tell was measured on, by letter. ⚠️ `I`–`K` are later
#: additions and are held out of the two counting assertions below: over these
#: eight, *two* are missed and *two* wrongly flagged, and a control that quietly
#: widens its own population stops being a check on that reading.
MEASURED_SHAPES = "ABCDEFGH"
