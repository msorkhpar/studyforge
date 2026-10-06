"""Where a learner's services sit: what the editor opens, and the two ports.

**What it does.** `binds` is what the editor opens, sources first, and `ports` is the site's and
the editor's port: the course's recorded ones, else the defaults.

**How you use it.**

    binds(manifest, editor)    # ((sources, inside), *extra)
    ports(root, editor)        # (site port, editor port)

**Depends on.** `execute.instance` for the recorded ports, `execution.binds` for the editor's own
answer about its mounts, and `execution.contract` for the contract's blocks. It writes nothing.
"""

from __future__ import annotations

from pathlib import Path

from studyforge.execute import instance
from studyforge.skills.execution.binds import code_bind, source_root, workspaces_bind
from studyforge.skills.execution.contract import blocks


def binds(manifest, editor) -> tuple[tuple[str, str], ...]:
    """Return what the editor opens, sources first: the execution skill's own answer."""
    sources = source_root(manifest)
    inside = next(
        str(entry["container_path"])
        for entry in blocks(editor, "mounts")
        if entry.get("per_project") is True
    )
    extra = [one for one in (workspaces_bind(editor, sources), code_bind(editor, sources)) if one]
    return ((sources, inside), *extra)


def ports(root: Path, editor) -> tuple[int, int]:
    """Return the site's and the editor's ports: the course's recorded ones, else the defaults."""
    try:
        recorded = instance.read(root)
    except OSError, ValueError:
        recorded = {}
    editor_default = next(
        int(one["host"]) for one in blocks(editor, "ports") if one.get("per_project")
    )
    return (
        int(recorded.get(instance.SITE_PORT, instance.DEFAULT_SITE_PORT)),
        int(recorded.get(instance.EDITOR_PORT, editor_default)),
    )
