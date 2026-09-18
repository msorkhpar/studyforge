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

⛔ **The archive is the one shared artifact NOT under the generated root**
(`INT-06/6`). It is the adapter's output (R2), and `validate`, the adapter's
definition of done, reads it at `names.ARCHIVE_DIRNAME` beside `corpus.json`.
`corpus()` once composed `.studyforge/archive` from that name, so `plan` printed a
root nothing read, and a malformed map there validated clean.

## Ignore lines are a profile's answer, not a caller's guess (Ruling 91)

⛔ **`SF-31`'s acceptance is that `studyforge plan` prints the ignore lines its
profile requires**, and R1 forbids the caller reaching that by asking which
profile it has. So the profile answers — `ignore_file`, and `output_globs` for
what is committed instead. `cli.plan` and `SK-07` are the callers.

⛔ **A build's output is committed, and the only generated ignore rules are the
media policy's** (`W242`, `INT-06/7` and `/8`). §5's *regenerable is not the same
as available* holds for the page that plays a clip as much as for the clip: a
clone that ignores its pages has no reading floor, and one that ignores only the
bundle has pages that render unstyled with no error. ⚠️ The pages, the root
index and the discovery cache were once ignored here, and under `sibling` those
rules had no home R3 allows and matched `*.html` and `*.json`.

⛔ **The home is a `.gitignore` inside the generated directory the rules are
about, never the repository root** (R3). A profile whose media **no one**
generated directory encloses has no home — whether nothing encloses it or one
directory per source directory does (`W323`) — and `ignore_file` raises rather
than hand a caller rules nothing may hold.

⭐ **What is committed is recognised instead, by `validate` asking the plan**
for this corpus's own placed paths — exact paths from its declarations, never a
glob a manifest would have to carry.
"""

from __future__ import annotations

from pathlib import PurePosixPath

from studyforge.address import Address
from studyforge.corpus.placement.errors import PlacementError
from studyforge.corpus.placement.locations import (
    ContainerLocations,
    CorpusLocations,
    IgnoreFile,
    UnitLocations,
)
from studyforge.corpus.placement.names import (
    ARCHIVE_DIRNAME,
    ASSETS_DIRNAME,
    IGNORE_FILENAME,
    ROOT_INDEX_FILENAME,
    SITE_CACHE_FILENAME,
)
from studyforge.describe import describe
from studyforge.sourcepath import SOURCE_PATH_DESCRIBED, source_path_fault

#: Where everything a reader does not browse lives. ⚠️ Dot-prefixed so it sorts
#: out of the way in a repository whose directories are the material — which is
#: the whole point of `sibling`.
GENERATED_ROOT = ".studyforge"

#: The ignore file inside the generated root, for a profile whose media lives
#: below it. ⛔ Inside the directory the rules are about and never the
#: repository root: that is the one mechanism R3 leaves.
GENERATED_IGNORE_HOME = PurePosixPath(GENERATED_ROOT, IGNORE_FILENAME)


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

    def media_ignore_lines(self) -> tuple[str, ...]:
        """Return the lines covering the per-unit media directories this profile mints.

        ⛔ Answered by every subclass, like `unit` and `container`, and for the
        same reason: a profile that puts media somewhere new and inherited a
        stale glob would report ignore rules that ignore nothing, which is the
        one failure mode a dry-run exists to prevent. Written relative to
        `ignore_home`'s directory, which is how git reads a nested ignore file.
        """
        raise NotImplementedError

    def ignore_home(self) -> PurePosixPath | None:
        """Return the ignore file this profile's media rules live in, or None.

        ⛔ Answered by every subclass. A home is inside a directory this
        framework generates, and it is ONE file — so a profile whose media is
        enclosed by one generated directory per source directory has none,
        as much as one whose media is enclosed by nothing at all (`W323`).
        """
        raise NotImplementedError

    def ignore_lines(self, *, media: bool) -> tuple[str, ...]:
        """Return the ignore lines a build under this profile requires.

        `media` says whether the generated media is to be ignored — it is the
        corpus's `media` policy inverted, and the caller passes it rather than
        this method reading a manifest.

        ⛔ **Only media is ever ignored, and it is committed by default**, so
        the default answer is empty. Pages, the root index, the bundle and the
        discovery cache are what a clone reads (§5, `W242`).
        """
        return self.media_ignore_lines() if media else ()

    def ignore_file(self, *, media: bool) -> IgnoreFile | None:
        """Return the ignore file a build requires, or None when it requires none.

        ⛔ **Raises `PlacementError` when rules are required and no file may
        hold them**, and refuses a home at the repository root (R3). A caller
        handed rules with nowhere to put them pastes them into the root file.
        """
        lines = self.ignore_lines(media=media)
        if not lines:
            return None
        home = self.ignore_home()
        if home is None or len(home.parts) < 2:
            raise PlacementError(
                f"the corpus's media policy does not commit generated media, and placement "
                f"{self.name!r} has no ignore file that may hold the rules: no single "
                f"directory this framework generates encloses its media, and the repository's "
                f"root ignore file is never edited (R3). Commit the media, or choose a "
                f"placement whose media lives under {GENERATED_ROOT}/"
            )
        return IgnoreFile(home=home, lines=lines)

    def corpus(self) -> CorpusLocations:
        """Return the paths that exist once per corpus. ⛔ The same under every profile."""
        generated = PurePosixPath(GENERATED_ROOT)
        return CorpusLocations(
            root_index=PurePosixPath(ROOT_INDEX_FILENAME),
            assets=generated / ASSETS_DIRNAME,
            archive=PurePosixPath(ARCHIVE_DIRNAME),
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
        f"no placement profile by that name; this build registers {registered()}, "
        f"and was given {describe(name)}"
    )


def registered() -> tuple[str, ...]:
    """Every registered profile name, sorted.

    ⛔ Sorted, not insertion-ordered: `studyforge plan` prints this and R10
    forbids an output that depends on import order.
    """
    return tuple(sorted(_PROFILES))


def origin_directory(origin: object, address: Address, what: str = "artifact") -> PurePosixPath:
    """Return the source directory an artifact is placed beside.

    `what` names the thing being placed, so a container's refusal does not
    call it a unit — the two records that carry an `origin` are different
    records, and an integrator sent to the wrong one looks in the wrong place.

    ⛔ Refuses an origin that escapes the source root — a generated artifact
    written outside the repository is R3's prohibition reached by accident.
    """
    if not isinstance(origin, str) or not origin.strip():
        raise PlacementError(
            f"the 'sibling' profile places an artifact beside its source file, and the "
            f"{what} at {address.key!r} records no usable 'origin' — the container map "
            f"must carry one for every {what} placed under this profile"
        )
    # ⛔ The offending origin is DESCRIBED, never echoed (R7). It is corpus
    # data, and the shapes being refused here are exactly the shapes that
    # carry a home directory — so a refusal that quoted it would copy personal
    # data into a build log, from the check that exists to catch it. Name the
    # fault and the record, and let the integrator look at the one named.
    #
    # ⚠️ The predicate is `sourcepath`'s and not this module's. It used to be
    # `is_absolute() or ".." in parts` here and a different forbidden list in
    # `container.fields.optional_path`, and the gap between the two lists was
    # reachable by `C:/Users/<name>/x`, which neither refused (Ruling 44).
    fault = source_path_fault(origin)
    if fault is not None:
        raise PlacementError(
            f"the 'origin' recorded for the {what} at {address.key!r} is {fault}; an "
            f"origin is {SOURCE_PATH_DESCRIBED} and stays inside it"
        )
    return PurePosixPath(origin).parent
