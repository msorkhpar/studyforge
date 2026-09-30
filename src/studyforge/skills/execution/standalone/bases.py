r"""The published base images a thin export builds its course's images from.

**What it does.** Reads a lock file that names the three bases a course's images
start from (the study server, the toolchain's runner and its editor), each by
image name, tag AND digest, and refuses a lock that could not be pulled, could
name an account, or does not match what this framework and the pinned toolchain
compute.

**How you use it.**

    locked = read(Path("bases.json"))          # Bases, or BasesRefused
    locked.serve.reference                     # "studyforge-serve:<tag>@sha256:<64 hex>"
    check(locked, version=..., toolchain={"runner": tag, "editor": tag}, serve_tag=...)
    key(locked.runner)                         # "<first twelve hex digits of its digest>"

The lock is one JSON object: `bases_api` (`1`), then `serve`, `runner` and
`editor`, each `{"image": ..., "tag": ..., "digest": ...}`:

    {
      "bases_api": 1,
      "serve":  {"image": "studyforge-serve", "tag": "0.1.0-<64 hex>", "digest": "sha256:<64 hex>"},
      "runner": {"image": "runner", "tag": "java-maven-amd64-<12 hex>", "digest": "sha256:<64>"},
      "editor": {"image": "editor", "tag": "java-maven-amd64-<12 hex>", "digest": "sha256:<64>"}
    }

**Depends on.** `studyforge.version` for the version test. It starts no process
and reads no image.

## ⛔ The namespace is never in the lock

An `image` is a bare name: a `/`, a `:` or an `@` in it is refused, so the lock is
the same for every publisher and the account is read from `STUDYFORGE_NAMESPACE`
when an image is built or pulled. ⛔ A digest of sixty-four zeros is the documented
placeholder of an example, and a lock read for a real export refuses it.

## ⭐ The tag says what the digest holds

The runner's and the editor's tag must be the tag the pinned toolchain computes for
the course's declared set, and the study server's must begin with this framework's
version and, in a checkout that carries `docker/serve/build.py`, be the tag that
script computes. A digest cannot be compared with a tag, but a lock whose tag is the
wrong one names an image built from other inputs.
"""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from studyforge.skills.execution.standalone import closure
from studyforge.version import is_supported

#: The lock's shape's version.
BASES_API = 1

#: The three bases, in the order a lock names them.
KINDS = ("serve", "runner", "editor")

#: The keys of one base.
FIELDS = ("image", "tag", "digest")

#: A bare image name: no registry, no account, no tag, no digest.
IMAGE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")

#: What an image tag may look like.
TAG = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$")

#: A digest: the algorithm and sixty-four lower-case hex digits.
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")

#: ⛔ The documented placeholder of an example lock: it names no image.
PLACEHOLDER = "sha256:" + "0" * 64

#: How many hex digits of a digest a course image's tag carries.
KEY_DIGITS = 12

#: Where the serving base's own build script sits in a checkout, beside its build file.
SERVE_BUILD = Path("docker") / "serve" / "build.py"


class BasesRefused(ValueError):
    """A lock this skill will not export a course from, and why."""


@dataclass(frozen=True, slots=True)
class Base:
    """One published base image."""

    image: str
    tag: str
    digest: str

    @property
    def reference(self) -> str:
        """`image:tag@digest`, unqualified: the tag says what it is, the digest pins it."""
        return f"{self.image}:{self.tag}@{self.digest}"


@dataclass(frozen=True, slots=True)
class Bases:
    """The three bases a thin export builds from."""

    serve: Base
    runner: Base
    editor: Base


def key(base: Base) -> str:
    """Return the short form of a base's digest that a course image's tag carries."""
    return base.digest.split(":", 1)[1][:KEY_DIGITS]


def read(path: Path, *, placeholder: bool = False) -> Bases:
    """Read the lock at `path`, or refuse by name; `placeholder` admits an example's zeros."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as missing:
        raise BasesRefused(
            f"the bases lock cannot be read: {missing.strerror or 'unreadable'}"
        ) from missing
    return from_text(text, placeholder=placeholder)


def from_text(text: str, *, placeholder: bool = False) -> Bases:
    """Return the bases a lock's text names, or refuse the first thing wrong with it."""
    try:
        document = json.loads(text)
    except ValueError as garbled:
        raise BasesRefused("the bases lock is not JSON") from garbled
    if not isinstance(document, dict):
        raise BasesRefused("the bases lock is not a JSON object")
    if not is_supported(document.get("bases_api"), {BASES_API}):
        raise BasesRefused(f"the bases lock must declare bases_api {BASES_API}")
    unknown = sorted(set(document) - {"bases_api", *KINDS})
    if unknown:
        raise BasesRefused(f"the bases lock holds keys it does not read: {unknown}")
    return Bases(**{kind: _base(kind, document.get(kind), placeholder) for kind in KINDS})


def _base(kind: str, entry: object, placeholder: bool) -> Base:
    """One base of the lock, every field checked."""
    if not isinstance(entry, Mapping):
        raise BasesRefused(f"the bases lock names no {kind} base")
    extra = sorted(set(entry) - set(FIELDS))
    missing = [one for one in FIELDS if not isinstance(entry.get(one), str)]
    if extra or missing:
        raise BasesRefused(
            f"the {kind} base must hold exactly {list(FIELDS)} as text "
            f"(missing {missing}, unread {extra})"
        )
    image, tag, digest = (str(entry[one]) for one in FIELDS)
    if not IMAGE.match(image):
        raise BasesRefused(
            f"the {kind} image is not a bare name: no account, registry, tag or digest "
            "belongs in it"
        )
    if not TAG.match(tag):
        raise BasesRefused(f"the {kind} tag is not an image tag")
    if not DIGEST.match(digest):
        raise BasesRefused(f"the {kind} digest is not sha256: and sixty-four lower-case hex digits")
    if digest == PLACEHOLDER and not placeholder:
        raise BasesRefused(
            f"the {kind} digest is the example's placeholder: pin the published image's"
        )
    return Base(image, tag, digest)


def check(
    bases: Bases,
    *,
    version: str,
    toolchain: Mapping[str, str],
    serve_tag: str | None = None,
) -> None:
    """Refuse a lock whose tags are not the ones this framework and the toolchain compute.

    `toolchain` maps `runner` and `editor` to the tag the pinned toolchain computes for
    the course's unprimed image (the part after the colon). `serve_tag` is the tag
    `docker/serve/build.py` computes, or `None` where this framework is not a checkout.
    """
    for kind in ("runner", "editor"):
        want, got = toolchain[kind], getattr(bases, kind).tag
        if want != got:
            raise BasesRefused(
                f"the {kind} base is locked at tag {got}, and the pinned toolchain computes "
                f"{want} for this course's declared set: lock the image built from it"
            )
    served = bases.serve.tag
    if serve_tag is not None and served != serve_tag:
        raise BasesRefused(
            f"the serve base is locked at tag {served}, and this framework's checkout computes "
            f"{serve_tag}: lock the image built from it"
        )
    if not served.startswith(f"{version}-"):
        raise BasesRefused(
            f"the serve base is locked at tag {served}, which is not this framework's "
            f"version {version}"
        )


def computed_serve_tag(source: Path) -> str | None:
    """Return the tag `docker/serve/build.py` computes for the checkout holding `source`, or None.

    `source` is the directory the `studyforge` package sits in; the checkout is its parent.
    ⛔ The digest is that script's own: the version, the build file and every vendored file by
    path and content, and a test holds the two answers equal. A package that is installed, not
    checked out, holds no build file, and the answer is None.
    """
    root = Path(source).resolve().parent
    dockerfile = root / SERVE_BUILD.parent / "Dockerfile"
    pyproject = root / "pyproject.toml"
    if not dockerfile.is_file() or not pyproject.is_file():
        return None
    version = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"]
    digest = hashlib.sha256()
    for part in (version, dockerfile.read_text(encoding="utf-8")):
        digest.update(part.encode("utf-8") + b"\0")
    for one in closure.vendored(Path(source)):
        digest.update(one.encode("utf-8") + b"\0" + (Path(source) / one).read_bytes() + b"\0")
    return f"{version}-{digest.hexdigest()}"
