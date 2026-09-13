"""A profile bound to one corpus: every declared artifact placed at once.

**What it does.** `bind(profile, containers)` places every container and every
declared unit under `profile`, separates units whose own placement lands on one
path by naming their container, and records every path two artifacts still claim.

**How you use it.**

    placed = bind(profile_for(manifest.placement), containers)
    placed.unit(address, 7, "Streams", origin=origin, label=label)   # as any profile
    placed.collisions   # each names both claimants and the one path

**Depends on.** `profile`, `locations`, `errors`, and `corpus.container` for the
declarations. ⛔ No I/O.

## ⛔ Placement of one unit cannot see its neighbour (`INT09-5`)

Under `sibling` a page's directory comes from `origin` and its name from the
unit's numbering and title, so two containers whose series mirror each other in
one source directory place two units at one path. Every call is correct and the
pair is wrong. Measured at `973fc67`: `validate` refused it as `duplicate-path`
while `plan` and a build exited 0, and the build silently replaced pages.

## The ruling, and its cost (reversible)

⭐ **A unit whose placed paths collide with another declared unit's is named with
its container's deepest address segment in front of its stem.** The address is
identity (§4, unique by construction), so it is the one datum that separates two
units the numbering and title cannot. Every other unit keeps its name.

- ⭐ **A corpus with no collision is byte-identical**: the qualified branch is
  never taken, so no existing page moves.
- ⚠️ **Names depend on the corpus, not only on the unit.** Declaring a mirrored
  unit later renames the page it now collides with. §5 already pays for that:
  a renamed artifact still identifies itself, and hrefs are regenerated.
- ⛔ **What the qualifier cannot separate is refused, never resolved** — no
  precedence, no last writer. `plan`, a build and `validate` all read
  `collisions`, so no instrument disagrees about it.

Rejected: the origin's filename (R1, R4 — `names.py` says why), and qualifying
every unit (every page of every `sibling` corpus moves, for a collision most
corpora never have).
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import PurePosixPath

from studyforge.address import Address
from studyforge.corpus.container.document import Container, Unit
from studyforge.corpus.placement.errors import PlacementError
from studyforge.corpus.placement.locations import ContainerLocations, UnitLocations
from studyforge.corpus.placement.names import UNIT_MEDIA_DIRNAMES
from studyforge.corpus.placement.profile import Profile

#: The kind a unit's page is claimed as; its media are claimed by their own kind.
PAGE = "page"


@dataclass(frozen=True, slots=True)
class Claimant:
    """One artifact that wants a path: a container's page, or a unit's page or media."""

    container: Container
    ordinal: int | None
    kind: str = PAGE

    def describe(self) -> str:
        """Name the artifact by address, never by a value read from the material (R7)."""
        key = self.container.address.key
        if self.ordinal is None:
            return f"container {key}'s page"
        if self.kind == PAGE:
            return f"{key} unit {self.ordinal}'s page"
        return f"{key} unit {self.ordinal}'s {self.kind} directory"


@dataclass(frozen=True, slots=True)
class Collision:
    """One path two artifacts claim, after qualification had its chance."""

    path: PurePosixPath
    first: Claimant
    second: Claimant

    @property
    def message(self) -> str:
        """Name both claimants and the one path, and why nothing separated them."""
        return (
            f"{self.second.describe()} is placed at {self.path.as_posix()!r}, which "
            f"{self.first.describe()} already claims. Naming a colliding unit by its "
            f"container still leaves one path, so one would overwrite the other; give "
            f"one of them a distinct title, label, origin directory or address."
        )


class BoundProfile(Profile):
    """A registered profile, answering for one corpus's declarations.

    ⛔ Not registered: a manifest names the profile, and this is that profile
    told which units collide. Every question but `unit` is the profile's own.
    """

    def __init__(
        self,
        profile: Profile,
        qualifiers: Mapping[tuple[str, int], str],
        collisions: tuple[Collision, ...] = (),
    ) -> None:
        """Wrap `profile`; `qualifiers` maps `(address key, ordinal)` to a qualifier."""
        self.profile = profile
        self.name = profile.name
        self.describes = profile.describes
        self.qualifiers = dict(qualifiers)
        self.collisions = collisions

    def unit(self, address, ordinal, title, *, origin=None, label=None, qualifier=None):
        """Where one unit's artifacts go, qualified when this corpus says it collides."""
        if qualifier is None and isinstance(address, Address):
            qualifier = self.qualifiers.get((address.key, ordinal))
        if qualifier is None:
            return self.profile.unit(address, ordinal, title, origin=origin, label=label)
        return self.profile.unit(
            address, ordinal, title, origin=origin, label=label, qualifier=qualifier
        )

    def container(self, address, titles, *, origin=None) -> ContainerLocations:
        """Return the profile's own answer: a container page is never qualified."""
        return self.profile.container(address, titles, origin=origin)

    def media_ignore_lines(self) -> tuple[str, ...]:
        """Return the profile's own lines."""
        return self.profile.media_ignore_lines()

    def ignore_home(self) -> PurePosixPath | None:
        """Return the profile's own home."""
        return self.profile.ignore_home()


def bind(profile: Profile, containers: Iterable[Container]) -> BoundProfile:
    """Place one corpus's declarations under `profile`, qualifying what collides.

    ⚠️ A unit that cannot be placed at all is left out here: the caller's own
    `unit` call raises the same `PlacementError`, where it reports it.
    """
    if isinstance(profile, BoundProfile):
        profile = profile.profile
    held = tuple(containers)
    claims: dict[PurePosixPath, list[tuple[Container, Unit]]] = {}
    for container, unit, at in _placed(profile, held):
        for path in (at.page, *at.directories):
            claims.setdefault(path, []).append((container, unit))
    qualifiers = {
        (container.address.key, unit.n): container.address.segments[-1]
        for claimants in claims.values()
        if len(claimants) > 1
        for container, unit in claimants
    }
    bound = BoundProfile(profile, qualifiers)
    return BoundProfile(profile, qualifiers, tuple(_collisions(bound, held)))


def _placed(
    profile: Profile, held: tuple[Container, ...]
) -> Iterator[tuple[Container, Unit, UnitLocations]]:
    """Every declared unit that places, with its unqualified locations."""
    for container in held:
        for unit in container.units:
            try:
                at = profile.unit(
                    container.address, unit.n, unit.title, origin=unit.origin, label=unit.label
                )
            except PlacementError:
                continue
            yield container, unit, at


def _collisions(bound: BoundProfile, held: tuple[Container, ...]) -> Iterator[Collision]:
    """Every path claimed twice once qualified: container pages, unit pages and media."""
    first: dict[PurePosixPath, Claimant] = {}
    for path, claimant in _claims(bound, held):
        already = first.setdefault(path, claimant)
        if already is not claimant:
            yield Collision(path, already, claimant)


def _claims(
    bound: BoundProfile, held: tuple[Container, ...]
) -> Iterator[tuple[PurePosixPath, Claimant]]:
    for container in held:
        try:
            page = bound.container(container.address, container.titles, origin=container.origin)
        except PlacementError:
            pass
        else:
            yield page.page, Claimant(container, None)
        for unit in container.units:
            try:
                at = bound.unit(
                    container.address, unit.n, unit.title, origin=unit.origin, label=unit.label
                )
            except PlacementError:
                continue
            yield at.page, Claimant(container, unit.n)
            for kind in UNIT_MEDIA_DIRNAMES:
                yield at.media_dir(kind), Claimant(container, unit.n, kind)
