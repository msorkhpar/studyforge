r"""The image profile a thin export's course layers may be built on, as the bases lock names it.

**What it does.** Reads the lock's optional `profile` entry, `{"name", "runner"?, "editor"?}`, whose
images are the published profile images built on the base of the course's declared runtimes, and
checks it against the course's own declaration and the tags the pinned toolchain computes.

**How you use it.** `bases.read` reads the entry through `read`; `bases.check` calls `check`;
`built_on(bases)` is the runner and the editor a course's layers start from. `image(kind, name)` is
the name a registry sees for a profile's image.

**Depends on.** `bases` for `Base`, only to type it: the base reader is handed in. ⛔ Nothing here
names a profile (R1): the name is the course's declaration and the lock's.

## ⭐ A profile image is a published base of its own

Its name is the base's published name, then the profile's (`<published runner name>-<profile>`),
with its own tag and digest. Each image is optional, but the runner is needed because the course's
graded runner layer is built on it. ⛔ A profile in the lock that the course does not declare, a
course that declares one the lock lacks, and a tag the toolchain does not compute are each refused
by name.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from studyforge.skills.execution.standalone.bases import Base, Bases

#: The lock's key, the two images it may name, and what a profile's name looks like.
KEY = "profile"
KINDS = ("runner", "editor")
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True, slots=True)
class Profile:
    """The profile images a course names; each is optional."""

    name: str
    runner: Base | None = None
    editor: Base | None = None


def image(published: Mapping[str, str], kind: str, name: str) -> str:
    """Return the name a registry sees for profile `name`'s `kind` image."""
    if kind not in KINDS or not NAME.match(name):
        raise _refused("a profile image is a runner or an editor of a hyphenated profile name")
    return f"{published[kind]}-{name}"


def read(
    entry: object,
    published: Mapping[str, str],
    base: Callable[[str, object, str], Base],
) -> Profile:
    """Return the lock's `profile` entry; `base(kind, entry, published_name)` reads one image."""
    if not isinstance(entry, Mapping):
        raise _refused("the bases lock's profile must be an object")
    extra = sorted(set(entry) - {"name", *KINDS})
    name = entry.get("name")
    if extra or not isinstance(name, str) or not NAME.match(name):
        raise _refused(
            f"the bases lock's profile must hold a 'name' of lower-case words joined by hyphens "
            f"and, each optional, {list(KINDS)} (unread {extra})"
        )
    found = {
        kind: base(kind, entry[kind], image(published, kind, name))
        for kind in KINDS
        if kind in entry
    }
    if not found:
        raise _refused(f"the bases lock names profile {name!r} and no image of it")
    return Profile(name, **found)


def built_on(bases: Bases) -> tuple[Base, Base]:
    """Return the runner and editor a course's layers start from: the profile's, else the base's."""
    one = bases.profile
    return (
        one.runner if one and one.runner else bases.runner,
        one.editor if one and one.editor else bases.editor,
    )


def check(locked: Profile | None, declared: str | None, computed: Mapping[str, str] | None) -> None:
    """Refuse a lock whose profile is not the course's, or has tags the toolchain does not compute.

    `computed` maps `runner` and `editor` to the tag, after its repository, the pinned toolchain
    computes for the declared profile over the course's runtimes. ⭐ A course that declares no
    profile and a lock that names none are not asked anything.
    """
    if locked is None and declared is None:
        return
    if declared is not None and not NAME.match(declared):
        raise _refused("the declared profile is not a hyphenated profile name")
    if declared is None:
        raise _refused(
            f"the bases lock names profile {locked.name!r}, and the course declares no profile: "
            "remove it from the lock, or declare it in the manifest"
        )
    if locked is None:
        raise _refused(
            f"the course declares profile {declared!r}, and the bases lock names no profile: "
            "lock the images built from it"
        )
    if locked.name != declared:
        raise _refused(
            f"the bases lock names profile {locked.name!r}, and the course declares {declared!r}"
        )
    if locked.runner is None:
        raise _refused(
            f"the bases lock names no runner for profile {declared!r}, and the course's runner "
            "layer is built on it"
        )
    if computed is None:
        raise _refused(f"profile {declared!r} cannot be checked: no tags were computed for it")
    for kind in KINDS:
        one = getattr(locked, kind)
        if one is not None and one.tag != computed[kind]:
            raise _refused(
                f"the {kind} of profile {declared!r} is locked at tag {one.tag}, and the pinned "
                f"toolchain computes {computed[kind]} for this course's runtimes: lock the image "
                "built from it"
            )


def _refused(message: str) -> ValueError:
    """Return the refusal a lock's profile is answered with: `bases.BasesRefused`, imported late."""
    from studyforge.skills.execution.standalone.bases import BasesRefused  # noqa: PLC0415

    return BasesRefused(message)
