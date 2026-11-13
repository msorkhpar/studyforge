"""A project practice's read-only windows: one per file the reader may read and not edit.

**What it does.** `read_only_windows(editor, root, paths)` answers, for a project's read-only
files (its other tests, their fixtures, its data, the expected report), the window each opens in:
`{"read_only": [{"path": ..., "url": ...} | None, ...]}`, in the record's own order.

**How you use it.** `workbench.prepared` merges the answer into what it returns for a practice;
a practice that names no read-only file gets `{}` and its answer is what it always was.

**Depends on.** `editor` for what an editor holds; the URL of a window is the caller's
`open_url` (`workbench`'s), handed in so the two modules do not import each other.

## ⛔ ALIGNED WITH THE RECORD, SO A MISSING FILE IS A HOLE AND NEVER A SHIFT

⭐ The page's explorer names each read-only file's button `ro:N`, N its position in the record.
So a file the editor or the corpus lacks is answered as `None` in its place rather than dropped:
dropping it would move every later button onto the wrong file. ⛔ A window on a file that is not
there would open an empty, dirty buffer titled with its name, so it gets no URL at all.

## ⛔ READ-ONLY IS THE SETTINGS', NOT THIS MODULE'S

⭐ `workbench.settings` makes every file read-only and excludes back out only the reader's own
files, so a read-only file needs nothing here to stay locked: it is simply never excluded.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path

from studyforge.execute.editor import Editor

#: The key the answer carries the windows under, as the record names the files.
READ_ONLY = "read_only"


def read_only_windows(
    editor: Editor, root: Path, paths: Iterable[str], open_url: Callable[[Editor, str], str | None]
) -> dict:
    """Return `{"read_only": [...]}` with one window or `None` per path, or `{}` for none."""
    listed = list(paths)
    if not listed:
        return {}
    windows: list[dict | None] = []
    for path in listed:
        inside = editor.inside(path)
        held = inside is not None and (Path(root) / path).is_file()
        windows.append({"path": inside, "url": open_url(editor, path)} if held else None)
    return {READ_ONLY: windows}
