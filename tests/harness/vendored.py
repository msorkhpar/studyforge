"""The vendored third-party files a repository sweep may pass over, and only while unmodified.

**What it does.** Answers whether one file is a vendored bundle shipped exactly as its upstream
release did, so a sweep of the framework's OWN text (control characters in a stream, process ids
in prose) does not read a minified third-party library as if it were authored here.

**How you use it.** `pristine(name, text)` before a sweep reads `name`; True means skip it.

## ⛔ Exempt by path AND by pin, never by suffix

A file is passed over only under its exact path, and only while what follows its vendoring
header still hashes to the release pin the build itself checks (`render.page.diagram.checked`).
One edited byte and the exemption lapses, so the sweep reads the file again — the same rule
`tests/floor/size.py` keeps for its own `VENDORED` list.

## ⛔ Never the personal-data floor

This list is for the code-hygiene sweeps only. The personal-data floor sweeps vendored files
like any other, by design (`tests/floor/personal_data/test_shapes.py`).
"""

from __future__ import annotations

from studyforge.render.pageassets.errors import AssetError

#: `path from the repository root -> how its unmodified state is checked`.
MERMAID = "src/studyforge/render/assets/mermaid.min.js"


def _mermaid_is_pinned(text: str) -> bool:
    from studyforge.render.page import diagram_checked as checked

    try:
        checked(text)
    except AssetError:
        return False
    return True


PINNED = {MERMAID: _mermaid_is_pinned}


def pristine(name: str, text: str) -> bool:
    """Whether `name` (a repository path, or an asset name) is a vendored bundle exactly as pinned."""
    for path, check in PINNED.items():
        if name == path or name == f"asset:{path.rsplit('/', 1)[-1]}":
            return check(text)
    return False
