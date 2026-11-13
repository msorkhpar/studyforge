r"""A project practice's two file surfaces: the list on the page, and the explorer over the editor.

**What it does.** A project practice (`Exercise.read_only` is set) has a whole package of files,
so it gets two surfaces where a practice of a few files gets a sentence and a tab each:

- `files_list(exercise)` — every file, as a folder tree inside a closed `<details>`, each marked
  as the reader's to edit or read-only. ⭐ It is in the built page and needs no server, so a page
  opened as a file still says what the project holds (R8).
- `explorer(exercise)` — the same tree as the tablist over the editor's one frame: one button per
  file, folders as labels between them. ⛔ It ships hidden, like the tablist it replaces, and only
  a running editor's answer shows it.

**How you use it.** `page.practice.render` asks `is_project(exercise)` and, for a project, fills
the panel's file slot with `files_list` and its tabs slot with `explorer`.

**Depends on.** `studyforge.exercise` for the record, `render.templates` and `render.markup`.
⛔ Not on `serve`: which file a button opens is the server's answer, read by `practice-files.js`.

## ⭐ A BUTTON IS NAMED FOR ITS WINDOW, NOT FOR ITS FILE

⭐ The server answers one window per file in the record's own order (`main`, each of `files`,
`test`, each of `read_only`), and `practice-files.js` resolves a button's `data-practice-tab`
against that answer: `main`, `file:N`, `test` and `ro:N`. ⛔ So no path is composed in the script,
and a file the editor does not hold has no window and its button stays hidden.
"""

from __future__ import annotations

import posixpath

from studyforge.exercise import KEPT, Exercise
from studyforge.render import templates
from studyforge.render.markup import escape, escape_attribute

#: The two surfaces, and their one file each (R13).
LIST_TEMPLATE = "practice-project-files.html"
EXPLORER_TEMPLATE = "practice-explorer.html"

#: ⭐ The words a breakdown says about a project step's kept cases, only where it has some.
KEPT_WORDS = ' data-practice-kept="Earlier steps: {passed} of {total} still pass."'

#: What a read-only file says beside its name, in the list and in the explorer.
READ_ONLY = "read-only"


def is_project(exercise: Exercise) -> bool:
    """Answer whether this practice is a project: it names read-only files beside its own."""
    return exercise.read_only is not None and not exercise.is_quiz and not exercise.is_deck


def files_part(exercise: Exercise, otherwise) -> str:
    """The panel's file slot: a project's list of files, or `otherwise(exercise)`."""
    return files_list(exercise) if is_project(exercise) else otherwise(exercise)


def tabs_part(exercise: Exercise, otherwise) -> str:
    """The panel's tabs slot: a project's explorer, or `otherwise(exercise)`."""
    return explorer(exercise) if is_project(exercise) else otherwise(exercise)


def kept_words(exercise: Exercise) -> str:
    """The breakdown's attribute for kept cases (`KEPT`), or nothing where it declares none."""
    return KEPT_WORDS if any(case.kind == KEPT for case in exercise.cases or ()) else ""


def entries(exercise: Exercise) -> list[tuple[str, str, bool]]:
    """Every file as `(window, workspace path, editable)`, folders first, then by name.

    ⭐ The workspace path is the corpus path with the folder every file shares taken off, which
    is the practice's own folder.
    """
    named = [("main", exercise.main_path or "", True)]
    named += [(f"file:{n}", path, True) for n, path in enumerate(exercise.files or ())]
    named += [("test", exercise.test_path, False)] if exercise.test_path else []
    named += [(f"ro:{n}", path, False) for n, path in enumerate(exercise.read_only or ())]
    base = posixpath.commonpath([posixpath.dirname(path) for _, path, _ in named])
    shown = [(window, posixpath.relpath(path, base), mine) for window, path, mine in named]
    return sorted(shown, key=lambda one: _order(one[1]))


def files_list(exercise: Exercise) -> str:
    """Return the closed list of every file of the project, as a folder tree."""
    found = entries(exercise)
    mine = sum(1 for _, _, editable in found if editable)
    rows = [
        f"<li><code>{escape(path)}</code>"
        f"{'' if editable else f' <span data-practice-readonly>{READ_ONLY}</span>'}</li>"
        for _, path, editable in found
    ]
    return templates.fill(
        LIST_TEMPLATE, count=str(len(found)), mine=str(mine), rows="\n".join(rows) + "\n"
    )


def explorer(exercise: Exercise) -> str:
    """Return the explorer: the tablist over the frame, one button per file, hidden until served."""
    found = entries(exercise)
    out = []
    folder = None
    for window, path, editable in found:
        here = posixpath.dirname(path)
        if here and here != folder:
            out.append(f'<p data-practice-folder aria-hidden="true">{escape(here)}/</p>')
        folder = here
        said = f"{path}, {'yours to edit' if editable else READ_ONLY}"
        out.append(
            f'<button type="button" role="tab" data-practice-tab="{escape_attribute(window)}"'
            f' aria-selected="{"true" if window == "main" else "false"}"'
            f' aria-label="{escape_attribute(said)}"'
            f"{' data-practice-readonly' if not editable else ''}"
            f">{escape(posixpath.basename(path))}</button>"
        )
    return templates.fill(EXPLORER_TEMPLATE, buttons="\n".join(out) + "\n")


def _order(path: str) -> tuple:
    """Sort a path as an explorer does: by folder, a folder's files before its sub-folders."""
    parts = path.split("/")
    return (*((1, part) for part in parts[:-1]), (0, parts[-1]))
