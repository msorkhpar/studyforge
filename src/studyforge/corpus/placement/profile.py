"""The profile: one address in, one location set out — and the registry of them.

**What it does.** Defines what a placement profile must answer, and holds the
registry a manifest's `placement` name is looked up in.

**How you use it.** `profile_for("sibling").unit(address, 7, "java", origin=…)`.

**Depends on.** `names`, `locations`, `errors`.

## A third profile is added without changing any consumer

⭐ That is SF-03's acceptance, and it is what the registry is for. A profile is
a `Profile` subclass with a `name`, registered with `register()`; every
consumer asks `profile_for(manifest.placement)` and none of them names a
profile. ⛔ There is no `if placement == "tree"` anywhere in this package or
downstream of it, and `test_profile` asserts that of the whole of `src/`.

## The seam with SF-02, drawn deliberately

⚠️ `corpus.manifest.PLACEMENT_PROFILES` lists **the names a manifest may
declare**; this registry holds **what each one does**. The CTO judged that
correct as written — they are different questions, and a manifest must be able
to refuse an unknown name without importing a placement engine. ⛔ But they
must not drift, so `test_profile` asserts the two sets are equal and fails a
profile registered here that a manifest may not name.

## The generated root

⚠️ Both profiles put the *shared* artifacts in one place — assets, archive and
the discovery cache — and differ only in where **pages** land. That is the
honest difference: `sibling` exists so the reader's own directories gain a page
beside the file they already know, not so a corpus's archive is scattered
through it.
"""

from __future__ import annotations

from pathlib import PurePosixPath

from studyforge.address import Address
from studyforge.corpus.placement.errors import PlacementError
from studyforge.corpus.placement.locations import (
    ContainerLocations,
    CorpusLocations,
    UnitLocations,
)
from studyforge.corpus.placement.names import (
    ARCHIVE_DIRNAME,
    ASSETS_DIRNAME,
    ROOT_INDEX_FILENAME,
    SITE_CACHE_FILENAME,
)

#: Where everything a reader does not browse lives. ⚠️ Dot-prefixed so it sorts
#: out of the way in a repository whose directories are the material — which is
#: the whole point of `sibling`.
GENERATED_ROOT = ".studyforge"


class Profile:
    """The map from a logical address to physical locations.

    ⛔ Subclasses answer `unit` and `container`; everything else is shared,
    because a profile that could move the archive would make two corpora on one
    disk unfindable by one scan.
    """

    #: The name a manifest declares. Set by every subclass.
    name = ""

    #: One line, for `studyforge plan` and for a person choosing between them.
    describes = ""

    def unit(
        self,
        address: Address,
        ordinal: int,
        title: str,
        *,
        origin: str | None = None,
        label: str | None = None,
    ) -> UnitLocations:
        """Where one unit's artifacts go."""
        raise NotImplementedError

    def container(
        self,
        address: Address,
        titles: tuple[str, ...],
        *,
        origin: str | None = None,
    ) -> ContainerLocations:
        """Where one container's own page goes."""
        raise NotImplementedError

    def corpus(self) -> CorpusLocations:
        """Return the paths that exist once per corpus. ⛔ The same under every profile."""
        generated = PurePosixPath(GENERATED_ROOT)
        return CorpusLocations(
            root_index=PurePosixPath(ROOT_INDEX_FILENAME),
            assets=generated / ASSETS_DIRNAME,
            archive=generated / ARCHIVE_DIRNAME,
            site_cache=generated / SITE_CACHE_FILENAME,
        )

    def __repr__(self) -> str:
        """Return the profile's declared name, which is what a plan prints."""
        return f"<placement {self.name!r}>"


#: The registry. ⛔ Mutated only through `register`, and read only through
#: `profile_for`, so adding a profile is one call and touches no consumer.
_PROFILES: dict[str, Profile] = {}


def register(profile: Profile) -> Profile:
    """Add a profile to the registry, refusing a name already taken."""
    if not profile.name:
        raise PlacementError(f"{type(profile).__name__} declares no name")
    if profile.name in _PROFILES:
        raise PlacementError(f"a placement profile named {profile.name!r} is already registered")
    _PROFILES[profile.name] = profile
    return profile


def profile_for(name: object) -> Profile:
    """Return the registered profile `name`, or raise listing the ones there are."""
    if name in _PROFILES:
        return _PROFILES[str(name)]
    raise PlacementError(
        f"no placement profile named {name!r}; this build registers {registered()}"
    )


def registered() -> tuple[str, ...]:
    """Every registered profile name, sorted.

    ⛔ Sorted, not insertion-ordered: `studyforge plan` prints this and R10
    forbids an output that depends on import order.
    """
    return tuple(sorted(_PROFILES))


def origin_directory(origin: object, address: Address) -> PurePosixPath:
    """Return the source directory an artifact is placed beside.

    ⛔ Refuses an origin that escapes the source root — a generated artifact
    written outside the repository is R3's prohibition reached by accident.
    """
    if not isinstance(origin, str) or not origin.strip():
        raise PlacementError(
            f"the 'sibling' profile places an artifact beside its source file, and "
            f"{address.key!r} records no usable 'origin' — the container map must "
            f"carry one for every unit under this profile"
        )
    path = PurePosixPath(origin)
    if path.is_absolute() or ".." in path.parts:
        # ⛔ The offending origin is DESCRIBED, never echoed (R7). It is corpus
        # data, and the one shape being refused here is exactly the shape that
        # carries a home directory — so a refusal that quoted it would copy
        # personal data into a build log, from the check that exists to catch
        # it. Following `version._said`: name the fault and the unit, and let
        # the integrator look at the one record named.
        fault = "an absolute path" if path.is_absolute() else "a path leaving the source root"
        raise PlacementError(
            f"the 'origin' recorded for {address.key!r} is {fault}; an origin is "
            f"relative to the source root and stays inside it"
        )
    return path.parent
