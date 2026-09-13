"""One corpus root in, one `Plan` out — from the declarations and nothing else.

**What it does.** Reads `corpus.json`, every container map beneath the
archive and the narration record when there is one, places each declared
container and unit under the corpus's own profile, and collects the result.

**How you use it.** `plan_for(root)`, or `plan_for(root, bytes_per_unit=N)` to
project the media footprint at a rate.

**Depends on.** `corpus.manifest`, `corpus.container`, `corpus.placement`,
`cli.plan.report`, `validate.corpus` for the archive directory's one
spelling, and `narrate.synth` / `narrate.speakable` for the record and its
clip names. ⛔ It opens three kinds of file and no others, and no unit document.

## ⛔ The narration record is a plan input (`E09` § SF-38/8, `W224`)

⭐ A build copies each clip a page addresses into any `--out` but the corpus
root, so the plan names every copy: one `create` line per clip the record files
under a declared unit, at that unit's audio directory — asked of placement.
⛔ **The unit is read off the speech id's own unit token**, which the
declarations can answer; an entry whose filename does not carry the id it is
filed under is `narrate.playable`'s MISFILED, which no page addresses, so it is
not named. ⚠️ An entry whose id no page produces any more cannot be told apart
without opening the material, so it IS named — `W224`'s handoff records it.

## ⛔ Nothing raises

Everything that goes wrong becomes a `Refusal`. A plan that stopped at the
first defect would make an integrator fix one problem per run against 166
units, which is the same argument `validate.Report.of` makes about draining
every check.

## ⚠️ Two artifacts claiming one path appear as two lines, not one

That collision is `validate`'s finding to raise — `duplicate-path` — and this
module does not restate the rule. ⭐ It does not hide the fact either: sorting
by path is what puts the pair next to each other, where a reader sees them.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path, PurePosixPath

from studyforge.cli.plan.report import Creation, MediaProjection, Plan, Refusal
from studyforge.corpus.container import CONTAINER_FILENAME, Container
from studyforge.corpus.container import RAISES as CONTAINER_RAISES
from studyforge.corpus.container import parse as parse_container
from studyforge.corpus.manifest import MANIFEST_FILENAME, Manifest
from studyforge.corpus.manifest import RAISES as MANIFEST_RAISES
from studyforge.corpus.manifest import parse as parse_manifest
from studyforge.corpus.placement import (
    AUDIO_DIRNAME,
    UNIT_MEDIA_DIRNAMES,
    PlacementError,
    Profile,
    profile_for,
)
from studyforge.narrate.speakable import SpeakableError
from studyforge.narrate.speakable.naming import SEGMENT, parse_clip_name, unit_token
from studyforge.narrate.synth import StateError, read_state, state_file
from studyforge.validate.corpus import ARCHIVE_DIR

#: What a clip's `create` line says about who writes it, and when a build does.
CLIP_COPY = (
    "`studyforge narrate` writes it beside the material; a build into any other "
    "output copies it there"
)


def plan_for(root: Path | str, *, bytes_per_unit: int | None = None) -> Plan:
    """Build the plan for the corpus rooted at `root`.

    `bytes_per_unit` is the media projection's rate. ⭐ **A parameter rather
    than a constant**, so `SF-32`'s measurement plugs in without this contract
    changing and so a person asking *"would 200 MB a unit still fit?"* can ask
    it. ⛔ Absent, the footprint reports itself unprojected and says why.
    """
    root = Path(root)
    manifest, refusals = _manifest(root)
    if manifest is None:
        return _unplannable(refusals)
    profile = profile_for(manifest.placement)
    held, unreadable = _containers(root, manifest)
    refusals += unreadable
    clips, record, misrecorded = _recorded(root)
    refusals += misrecorded
    creations = _corpus_creations(profile)
    units = 0
    for where, container in held:
        made, failed = _container_creations(container, profile, where, clips)
        creations += made
        refusals += failed
        units += len(container.units)
    media = MediaProjection(manifest.media, units, bytes_per_unit)
    return Plan(
        source=manifest.source,
        title=manifest.title,
        profile=profile.name,
        describes=profile.describes,
        read_files=(MANIFEST_FILENAME, *(where for where, _ in held), *record),
        creations=tuple(sorted(creations, key=lambda creation: creation.path)),
        edits=manifest.permitted_edits,
        ignore=profile.ignore_lines(media=media.ignored),
        media=media,
        refusals=tuple(refusals),
    )


def _unplannable(refusals: list[Refusal]) -> Plan:
    """Return the plan for a corpus whose manifest will not read: refusals, nothing else.

    ⛔ **Not an empty plan.** An empty `create` list means *"this build writes
    nothing into your repository"*, which is a claim, and it is one nothing
    here is entitled to make. The summary counts the refusal and the exit code
    is 1.
    """
    return Plan(
        source="?",
        title="?",
        profile="?",
        describes="?",
        read_files=(MANIFEST_FILENAME,),
        creations=(),
        edits=(),
        ignore=(),
        media=None,
        refusals=tuple(refusals),
    )


def _manifest(root: Path) -> tuple[Manifest | None, list[Refusal]]:
    """Read `corpus.json`, or say why not.

    ⛔ `exc.strerror`, never `exc`: an `OSError` formats itself with the
    filename it was given, and this one is absolute (R7).
    """
    try:
        text = (root / MANIFEST_FILENAME).read_text(encoding="utf-8")
    except OSError as exc:
        reason = exc.strerror or exc.__class__.__name__
        return None, [Refusal(MANIFEST_FILENAME, f"cannot be read: {reason}")]
    except UnicodeDecodeError:
        return None, [Refusal(MANIFEST_FILENAME, "is not UTF-8 text")]
    try:
        return parse_manifest(text, MANIFEST_FILENAME), []
    except MANIFEST_RAISES as error:
        # ⛔ **The reader's own tuple** (`W213`), which was a retyped pair here.
        # It includes `PersonalDataLeak`, untranslated (Ruling 58): its message
        # says it is a leak, so a plan does not report it as a parse error.
        return None, [Refusal(MANIFEST_FILENAME, str(error))]


def _containers(
    root: Path, manifest: Manifest
) -> tuple[list[tuple[str, Container]], list[Refusal]]:
    """Every container map under the archive, in sorted path order (R10)."""
    held: list[tuple[str, Container]] = []
    refusals: list[Refusal] = []
    for path in sorted((root / ARCHIVE_DIR).rglob(CONTAINER_FILENAME)):
        where = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except OSError, UnicodeDecodeError:
            refusals.append(Refusal(where, "cannot be read as UTF-8 text"))
            continue
        try:
            held.append((where, parse_container(text, where, manifest)))
        except CONTAINER_RAISES as error:
            # ⛔ **The reader's own tuple, never a list retyped here** (`W208`).
            # This site caught `ContainerError` and `PersonalDataLeak` and
            # missed `AddressError`, which `container`'s contract argues for in
            # the same paragraph — so a container map whose address was the
            # wrong depth CRASHED the one command whose whole contract is that
            # nothing raises. ⭐ A member added to the reader now arrives here.
            refusals.append(Refusal(where, str(error)))
    return held, refusals


def _recorded(root: Path) -> tuple[dict[str, tuple[str, ...]], tuple[str, ...], list[Refusal]]:
    """Return the clip filenames the record files under each unit token, and what was read.

    ⛔ Nothing raises: an unreadable record is a refusal, exactly as a container
    map is. An absent record is the ordinary case and is not read.
    """
    file = state_file(root)
    where = file.relative_to(root).as_posix()
    try:
        state = read_state(file)
    except StateError as error:
        return {}, (where,), [Refusal(where, str(error))]
    if not state.present:
        return {}, (), []
    grouped: dict[str, set[str]] = {}
    refusals: list[Refusal] = []
    for speech_id, clip in state.clips.items():
        name = clip.filename
        if not name.strip():
            continue
        if PurePosixPath(name).name != name or name in (".", ".."):
            # ⛔ The value is not echoed (R7). A copy of it would leave its unit's
            # audio directory, and a page's href never would.
            refusals.append(Refusal(where, "records a clip filename that is not one file name"))
            continue
        try:
            filed, _ = parse_clip_name(PurePosixPath(name).stem)
        except SpeakableError:
            continue
        if filed == speech_id:
            grouped.setdefault(speech_id.split(SEGMENT, 1)[0], set()).add(name)
    return {token: tuple(sorted(names)) for token, names in grouped.items()}, (where,), refusals


def _token(container: Container, n: int) -> str | None:
    """Return the unit token a declared unit's speech ids begin with, or None if it has none."""
    try:
        return unit_token(container.address.unit_key(n))
    except SpeakableError:
        return None


def _corpus_creations(profile: Profile) -> list[Creation]:
    """Return the four paths every corpus gets, whatever its addresses are.

    ⚠️ **The archive is one of them and it is not this build's output.** It is
    listed because a plan answers *"what will be in my repository afterwards"*,
    and its line says who writes it.
    """
    where = profile.corpus()
    return [
        Creation(where.root_index.as_posix(), "the root index"),
        Creation(f"{where.assets.as_posix()}/", "the shared stylesheets, scripts and player"),
        Creation(
            f"{where.archive.as_posix()}/",
            "the archive root — an adapter writes it (R2) and every build reads it",
        ),
        Creation(where.site_cache.as_posix(), "the discovery cache, never the authority"),
    ]


def _container_creations(
    container: Container, profile: Profile, where: str, clips: Mapping[str, tuple[str, ...]]
) -> tuple[list[Creation], list[Refusal]]:
    """Every path one container and its declared units occupy."""
    key = container.address.key
    made: list[Creation] = []
    failed: list[Refusal] = []
    try:
        page = profile.container(container.address, container.titles, origin=container.origin)
        made.append(Creation(page.page.as_posix(), f"the page for container {key}"))
    except PlacementError as error:
        failed.append(Refusal(where, str(error)))
    for unit in container.units:
        try:
            at = profile.unit(
                container.address, unit.n, unit.title, origin=unit.origin, label=unit.label
            )
        except PlacementError as error:
            failed.append(Refusal(where, f"unit {unit.n}: {error}"))
            continue
        made.append(Creation(at.page.as_posix(), f"{key} unit {unit.n}'s page"))
        # ⛔ Asked by kind, never read back off the minted directory name.
        # `tree` calls it `audio` and `sibling` calls it `<stem>.audio`, so a
        # description taken from the name would say something different under
        # each profile — `UnitLocations.href`'s *ask, never compose* rule
        # arriving one layer up.
        made += [
            Creation(
                f"{at.media_dir(kind).as_posix()}/",
                f"{key} unit {unit.n}'s {kind}",
                narration=kind == AUDIO_DIRNAME,
            )
            for kind in UNIT_MEDIA_DIRNAMES
        ]
        audio = at.media_dir(AUDIO_DIRNAME).as_posix()
        made += [
            Creation(f"{audio}/{name}", f"{key} unit {unit.n}'s clip — {CLIP_COPY}", narration=True)
            for name in (clips.get(_token(container, unit.n) or "", ()) if clips else ())
        ]
    return made, failed
