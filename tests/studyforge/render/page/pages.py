"""Both framework fixture corpora, built the way a build would, and where their goldens sit.

⛔ **Imported, never copied.** Three test modules render these two documents and
a fourth regenerates the goldens; four spellings of "build the depth-2 unit with
its overlay" is four places to forget when the builder's signature changes.

Run `python3 -m tests.studyforge.render.page.pages` to rewrite the goldens after
a deliberate change to the page. ⚠️ A golden that changes without a deliberate
change to the page is the R10 failure the test exists to catch — regenerate only
once you know which change you made.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.address import Address
from studyforge.corpus import placement as placement_module
from studyforge.corpus.placement import CorpusLocations, UnitLocations
from studyforge.narrate.speakable import clip_name, speakable_of
from studyforge.render.page import Narration, Placement, render
from studyforge.unit import content
from studyforge.unit.builder import build_unit
from tests.support import repository_root

#: Where the committed goldens live. ⚠️ Under `tests/fixtures/` because the
#: repository's ignore rules exempt exactly that tree from `*.unit.html`, which
#: is otherwise ignored as build output everywhere.
GOLDEN_DIR = repository_root() / "tests" / "fixtures" / "pages"

#: The corpus root of each fixture, relative to the repository.
FIXTURES = repository_root() / "tests" / "fixtures"

#: The clip suffix these fixtures are built with.
#:
#: ⛔ **A FIXTURE'S STAND-IN FOR A RECORD, AND NOT A DECISION THE FRAMEWORK MAKES.**
#: A clip's real filename is whatever synthesis placed — `narrate/client.py` names
#: it from a format the SERVICE answered with — and
#: `.studyforge/narration.json` records it per clip. ⚠️ A build reads that record;
#: this harness has no service and no record, so it stands one in. ⛔ Nothing under
#: `src/` may do the same: a renderer that assumed a format would be a second
#: authority on it, and the symptom is a page linking files that are not there
#: with the suite green.
FIXTURE_CLIP_SUFFIX = ".mp3"


@dataclass(frozen=True)
class Case:
    """One fixture unit, ready to render, and the golden it is compared against."""

    name: str
    document: dict
    placement: Placement

    @property
    def narration(self) -> Narration:
        """What a build would hand the renderer once this unit had been narrated.

        ⭐ **Keyed on `SpeechUnit.position` and named by `clip_name`** — the one
        minter, called rather than imitated, so this harness cannot disagree with
        the names synthesis actually writes.
        """
        units = speakable_of(self.document).units
        clips = {unit.position: clip_name(unit) + FIXTURE_CLIP_SUFFIX for unit in units}
        return Narration.of(clips, self.placement)

    def render(self) -> bytes:
        """This case's page exactly as a build would write it.

        ⛔ **The ONE producer.** `tests/harness/goldens.py` and `regenerate()`
        below both call it, so the bytes a golden is compared against and the
        bytes it is rewritten from cannot come from two different calls — which
        is the defect this module's own docstring names and which returned the
        moment `narration` became an argument one caller passed and the other
        did not.
        """
        return render(self.document, self.placement, narration=self.narration)

    @property
    def golden(self) -> Path:
        """The committed page for this case, named as placement would name it."""
        return GOLDEN_DIR / Path(self.placement.unit.page).name


def depth1_unit_02() -> Case:
    """A prose corpus, `tree` placement, no overlay, no exercises.

    ⚠️ `declared_practices=0` is what a build reads off `corpus.json`'s
    `"exercises": false`: a corpus that declares no exercises has declared a
    count of zero, which is **not** the same as nothing having said — and the
    difference is a "more to come" panel on every page of a prose corpus.
    """
    document = build_unit(
        FIXTURES / "depth1/archive/depth-one/raw/prose/unit-02",
        declared_practices=0,
    )
    return Case("depth1-unit-02", document, _placement("depth1-demo", "tree", document))


def depth2_unit_01() -> Case:
    """A two-level corpus, `sibling` placement, an authored overlay, one practice."""
    document = build_unit(
        FIXTURES / "depth2/archive/basics/01-getting-started/raw/java/unit-01",
        overlay=content.load(
            FIXTURES / "depth2/archive/basics/01-getting-started/units/unit-01/content.json",
            2,
        ),
        declared_practices=1,
    )
    return Case(
        "depth2-unit-01",
        document,
        _placement(
            "depth2-demo",
            "sibling",
            document,
            origin="basics/01-getting-started/README_1.1.md",
        ),
    )


#: Every case, in a stated order. ⛔ A tuple rather than a directory walk, so the
#: suite's own list of golden pages does not depend on filesystem order (R10).
CASES = (depth1_unit_02, depth2_unit_01)


def sample_placement() -> Placement:
    """A placement with no corpus behind it, for the modules that only need hrefs.

    ⭐ Built from `UnitLocations` directly rather than from a profile, so a test
    of the renderer cannot fail because a placement profile changed its shape —
    the profiles have their own tests, and this is not one of them.
    """
    base = PurePosixPath("out/units/unit-01")
    return Placement(
        corpus="demo",
        unit=UnitLocations(
            page=base / "unit-01-a-unit.unit.html",
            audio=base / "audio",
            images=base / "images",
            video=base / "video",
            practice=base / "practice",
            attachments=base / "attachments",
        ),
        shared=CorpusLocations(
            root_index=PurePosixPath("index.html"),
            assets=PurePosixPath("out/assets"),
            archive=PurePosixPath("out/archive"),
            site_cache=PurePosixPath("out/site.json"),
        ),
    )


def _placement(corpus: str, profile_name: str, document: dict, origin: str | None = None):
    """The placement decision a build would have made for this document."""
    profile = placement_module.profile_for(profile_name)
    return Placement(
        corpus=corpus,
        unit=profile.unit(
            Address(tuple(document["address"])),
            document["unit"],
            document["title"],
            origin=origin,
        ),
        shared=profile.corpus(),
    )


def regenerate() -> list[Path]:
    """Rewrite every golden from the current renderer, and say which changed."""
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    changed = []
    for build in CASES:
        case = build()
        page = case.render()
        if not case.golden.exists() or case.golden.read_bytes() != page:
            case.golden.write_bytes(page)
            changed.append(case.golden)
    return changed


if __name__ == "__main__":  # pragma: no cover - a maintenance entry point
    for path in regenerate() or []:
        print(f"rewrote {path.name}")
