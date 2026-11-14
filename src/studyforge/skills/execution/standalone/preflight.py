r"""Everything a release can decide before it writes a file, asked at once and named at once.

**What it does.** Asks every precondition of `write.release` that needs no file written: the
published account, an empty target, the course's sorted findings log, its declarations and
runtimes, what it tracks, the toolchain's pinned and computed tags, the editor contract, the
bases lock, the course's own README sections and the README's pictures. It returns every reason
it found, and an empty list when the course is clear to release.

**How you use it.**

    reasons = preflight(course, out, toolchain=checkout, platform="linux/amd64",
                        bases=read_bases(lock), run=run)       # run: split.Run
    print("\n".join(reasons) or "clear")

`write.release` runs the same checks first and raises one `ReleaseRefused` over all of them.

**Depends on.** `generate.read_corpus`, the execution contract, this package's `split`,
`vendor`, `bases`, `own` and `tour`, the delivery skill's findings log (`closing`) and its
`one_or_all` form. ⛔ It writes nothing, and it starts no process: every command goes through
the `run` the caller hands in.

## ⛔ A refusal names its whole population, never its first witness

⚠️ A release that refused one precondition at a time made a course owner pay a full run per
refusal, each one visible only after the last was fixed. ⭐ So the checks here are independent
where they can be: each that fails adds its reason and the rest still run. ⛔ A check whose
input another check refused is not asked (no runtime declared: the toolchain is not asked for
a build), since it would only repeat that reason in other words.

## ⛔ What stays mid-run

⚠️ Three refusals cannot be decided before writing, and stay where they happen in `release`:
a toolchain input the checkout does not hold (`vendor.copy`, met while copying), the rulings over
the compose text the release renders (`compose.render`), and the preview of the finished tree
(`preview`, which reads the tree). Each still refuses by name.

## ⭐ The findings log is a precondition

A course is released after its conversion's findings are sorted: the log at
`.studyforge/findings.md` must exist, read back (`closing`), and end `open: 0`. ⛔ Only its
last line is read here; the log's own shape is the delivery skill's to decide.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from studyforge.generate import RAISES as CORPUS_RAISES
from studyforge.generate import read_corpus
from studyforge.skills.delivery import LOG, LogRefused, closing
from studyforge.skills.execution.contract import (
    CONSUMING,
    EDITOR_API,
    EDITOR_COMPONENT,
    EDITOR_PROMISE,
    ContractRefused,
    read,
    require,
)
from studyforge.skills.execution.standalone import bases as locked
from studyforge.skills.execution.standalone import learner, own, pages, record, split, tour, vendor
from studyforge.skills.onboarding import library

#: How a course gets the log the release needs, said in every refusal of it.
LOG_HOW = (
    "write the log per the onboarding skill's step 7 and sort it per the delivery skill's step 9"
)

#: The README's pictures: what a file may be, and how much of the repository they may take.
SHOT_SUFFIXES = (".png", ".webp")
SHOT_MAX_BYTES = 160 * 1024
SHOTS_MAX_BYTES = 700 * 1024

#: ⭐ What a sorted log's report ends with (`closing`'s last line).
SORTED = "open: 0"


@dataclass(frozen=True, slots=True)
class Ready:
    """What the checks read, handed to the release so nothing is asked twice."""

    manifest: object
    files: tuple[str, ...]
    verdicts: tuple[split.Verdict, ...]
    kept: tuple[str, ...]
    profiled: dict
    asked: object
    editor: object
    mine: own.Own
    shots: tuple[tuple[str, Path], ...]
    commit: str


def preflight(
    root: Path,
    out: Path,
    *,
    toolchain: Path,
    platform: str,
    bases: locked.Bases | None = None,
    published_account: str | None = None,
    screenshots: Path | None = None,
    run: split.Run,
) -> list[str]:
    """Return every reason `write.release` would refuse the course at `root`; empty when clear."""
    return gather(
        root,
        out,
        toolchain=toolchain,
        platform=platform,
        bases=bases,
        published_account=published_account,
        screenshots=screenshots,
        run=run,
    )[0]


def gather(
    root: Path,
    out: Path,
    *,
    toolchain: Path,
    platform: str,
    bases: locked.Bases | None,
    published_account: str | None,
    screenshots: Path | None,
    run: split.Run,
) -> tuple[list[str], Ready | None]:
    """Return every reason found, and what was read when there is none."""
    root, out, toolchain = Path(root), Path(out), Path(toolchain)
    reasons: list[str] = []
    if published_account is not None and not learner.is_account(published_account):
        reasons.append("published_account is not a Docker Hub account (4 to 30 a-z, 0-9)")
    if out.exists() and any(out.iterdir()):
        reasons.append("the target directory is not empty; name a new or empty one")
    reasons += findings(root)
    shots = pictures(screenshots, reasons)
    try:
        mine = own.read(root)
    except ValueError as error:
        reasons.append(str(error))
        mine = None
    try:
        manifest = read_corpus(root).manifest
    except CORPUS_RAISES as error:
        reasons.append(str(error))
        return reasons, None
    if not manifest.runtimes:
        reasons.append("the course declares no runtime, so it has nothing to run standalone")
    tracked = _tracked(root, run, reasons)
    toolchain_read = _toolchain(root, toolchain, manifest, bases, platform, run, reasons)
    if reasons or tracked is None or toolchain_read is None or mine is None:
        return reasons, None
    files, verdicts, kept, commit = tracked
    profiled, asked, editor = toolchain_read
    ready = Ready(manifest, files, verdicts, kept, profiled, asked, editor, mine, shots, commit)
    return reasons, ready


def findings(root: Path) -> list[str]:
    """Refuse a course whose findings log is absent, unreadable or not sorted."""
    path = Path(root) / LOG
    text = path.read_text(encoding="utf-8") if path.is_file() else None
    try:
        report = closing(text)
    except LogRefused as refused:
        return [f"{refused}: {LOG_HOW}"]
    last = report[-1] if report else ""
    if not last.startswith(SORTED):
        return [f"the findings log at {LOG} is not sorted ({last}): {LOG_HOW}"]
    return []


def pictures(source: Path | None, reasons: list[str]) -> tuple[tuple[str, Path], ...]:
    """Return the README's pictures as `(role, path)`; add every reason one is refused."""
    if source is None:
        return ()
    if not Path(source).is_dir():
        reasons.append(f"the pictures' directory {Path(source).name} is not a directory")
        return ()
    roles = [role for role, _ in tour.ROLES]
    found: list[tuple[str, Path]] = []
    refused = len(reasons)
    for one in sorted(Path(source).iterdir()):
        if one.stem not in roles or one.suffix not in SHOT_SUFFIXES:
            reasons.append(f"{one.name} is not a picture the README shows: {roles}")
        elif one.stat().st_size > SHOT_MAX_BYTES:
            reasons.append(f"{one.name} is over {SHOT_MAX_BYTES // 1024} KB")
        else:
            found.append((one.stem, one))
    if sum(one.stat().st_size for _, one in found) > SHOTS_MAX_BYTES:
        reasons.append(f"the pictures together are over {SHOTS_MAX_BYTES // 1024} KB")
    if len({role for role, _ in found}) != len(found):
        reasons.append("a role has two pictures; keep one")
    return tuple(found) if len(reasons) == refused else ()


def _tracked(root: Path, run: split.Run, reasons: list[str]):
    """Return what the course tracks, its verdicts, what it keeps and its commit, or None."""
    try:
        files = split.tracked(root, run)
    except ValueError as error:
        reasons.append(str(error))
        return None
    verdicts = split.classify(root, files)
    if not any(one.path == split.HOSTING for one in verdicts):
        verdicts = (*verdicts, split.HOSTED)
    kept = split.kept(verdicts, files)
    owned = [one for one in kept if one in pages.OWNED or one.startswith(pages.BUILDER_DIR + "/")]
    if owned:
        reasons.append(
            f"the course tracks {owned}, which the export writes itself; move or rename them"
        )
    code, printed = run(["git", "-C", str(root), "rev-parse", "HEAD"], root)
    if code != 0:
        reasons.append("the course is not a git checkout, so no commit versions its images")
        return None
    return files, tuple(verdicts), tuple(kept), printed.strip()


def _toolchain(root, checkout, manifest, bases, platform, run, reasons):
    """Ask the toolchain and the lock everything they can refuse; return what they said, or None.

    ⭐ The order is the release's: the profile, the recorded tags, the builds, the editor
    contract, then the lock over what the toolchain computed. A step whose input was refused
    is skipped; the others still run.
    """
    if not manifest.runtimes:
        return None
    prime = root / split.PRIME
    profiled = None
    try:
        profiled = vendor.profile_check(manifest, bases, checkout, platform=platform, run=run)
        vendor.pinned(
            root, checkout, manifest.runtimes, prime, profiled, platform=platform, run=run
        )
    except vendor.VendorRefused as refused:
        reasons.append(str(refused))
    asked = None
    try:
        asked = vendor.ask(
            checkout, manifest.runtimes, prime, platform=platform, run=run, profile=manifest.profile
        )
    except vendor.VendorRefused as refused:
        reasons.append(str(refused))
    editor = None
    try:
        text = (checkout / CONSUMING).read_text(encoding="utf-8")
        editor = require(
            read(text, component=EDITOR_COMPONENT, api=EDITOR_API, promise=EDITOR_PROMISE),
            "editor",
        )
    except OSError:
        reasons.append(f"the toolchain checkout carries no {CONSUMING}")
    except ContractRefused as refused:
        reasons.append(str(refused))
    if bases is not None and asked is not None and profiled is not None:
        try:
            locked.check(
                bases,
                version=library.version(),
                toolchain=record.unprimed_tags(asked),
                declared=manifest.runtimes,
                tags_for=vendor.asker(checkout, platform=platform, run=run),
                serve_tag=locked.computed_serve_tag(library.PACKAGE.parent),
                **profiled,
            )
        except (locked.BasesRefused, vendor.VendorRefused) as refused:
            reasons.append(str(refused))
    if profiled is None or asked is None or editor is None:
        return None
    return profiled, asked, editor
