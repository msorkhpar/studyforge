"""Every golden this repository commits, and the one case that writes it.

⛔ **The census, not a fourth comparison.** Three renderers already compare their
own goldens where their own tests live, and `studyforge plan` compares its three
beside the CLI. What nothing asserted before this module is the shape *between*
them: that the two golden directories hold **exactly** what those cases claim,
that no two cases claim **one** file, and that every claimed file is pinned by a
byte comparison in one place a reader can count.

⚠️ **Why the census and not another comparison.** A golden nobody regenerates is
green forever: it is compared against nothing, so it is evidence of nothing, and
it survives the renderer that produced it being deleted. ⛔ And a *collision* —
two cases naming one golden — satisfies "every case has a golden" **and** "every
golden has a case" while pinning only the case that writes last (asserted in both directions
proves surjectivity, never injectivity).

**How you use it.**

    from tests.harness import goldens

    for golden in goldens.claimed():       # every committed golden, with its writer
        assert golden.emit() == golden.path.read_bytes()

    goldens.mismatches(goldens.claimed())  # [] or one message per golden, naming its module
    goldens.orphans()                      # committed files no case claims
    goldens.collisions()                   # files more than one case claims

**Depends on.** The three regenerators and the plan CLI — ⛔ **imported, never
re-listed.** A second list of the cases here is a second thing to forget, and it
would agree with the renderers right up to the moment one of them gained a case.

⚠️ **A `Golden` names the module that rewrites it**, because that is what a
reader of a failing run needs: not "the renderer changed" but
`python3 -m tests.studyforge.render.page.pages` (R12, and the harness's acceptance
clause that a failure names the module and not the subsystem).
"""

from __future__ import annotations

import io
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from studyforge.cli.plan import cli as plan_cli
from tests.fixture_checks import FIXTURES, VALID
from tests.studyforge.render.container import containers
from tests.studyforge.render.index import indexes
from tests.studyforge.render.page import pages
from tests.support import repository_root

#: The two directories that hold a golden, and the whole of them. ⛔ Derived from
#: the regenerators' own constant and from the CLI's fixtures root, so neither
#: path is spelled twice.
PAGE_TREE = pages.GOLDEN_DIR
PLAN_TREE = FIXTURES / "golden"
TREES = (PAGE_TREE, PLAN_TREE)

#: How a plan golden is named, from the corpus it describes.
PLAN_SUFFIX = ".plan.txt"

#: What a plan is written as. ⚠️ The golden on disk is bytes; the command prints
#: text, and `utf-8` is what a build would encode it with.
PLAN_ENCODING = "utf-8"


@dataclass(frozen=True)
class Golden:
    """One committed golden, the module that rewrites it, and how it is produced.

    `writer` is a dotted module name and not prose: it is both the name a failure
    reports and the argument to `python3 -m` that regenerates the file, so the
    message a reader gets is the command they need.
    """

    path: Path
    writer: str
    case: str
    emit: Callable[[], bytes]


def claimed() -> tuple[Golden, ...]:
    """Every golden any case in this repository claims, in a stated order.

    ⛔ A tuple in writer order, never a directory walk: the census's own
    enumeration may not depend on the order a filesystem hands files back (R10).
    """
    return (*_pages(), *_indexes(), *_containers(), *_plans())


def committed() -> tuple[Path, ...]:
    """Every file actually sitting in the golden directories, sorted."""
    return tuple(
        sorted(
            (path for tree in TREES for path in tree.iterdir() if path.is_file()),
            key=str,
        )
    )


def mismatches(goldens: tuple[Golden, ...]) -> list[str]:
    """One message per golden that is absent or whose bytes moved, naming its module.

    ⛔ Never a bare inequality. A golden that moved and a golden that was never
    committed are different failures with different remedies, and the message
    says which, where in the file, and what to run if the change was deliberate.
    """
    found: list[str] = []
    for golden in goldens:
        if not golden.path.exists():
            found.append(f"{golden.writer}: {golden.case}: {golden.path.name} is not committed")
            continue
        was = golden.path.read_bytes()
        now = golden.emit()
        if now != was:
            found.append(
                f"{golden.writer}: {golden.case}: {golden.path.name} {_where(was, now)}; "
                f"if that change was deliberate, run python3 -m {golden.writer}"
            )
    return found


def orphans() -> list[str]:
    """Every committed golden that no case claims — evidence of nothing, green forever.

    ⛔ Reported relative to the repository root: an absolute path in a failure
    message carries somebody's home directory (R7).
    """
    mine = {golden.path for golden in claimed()}
    root = repository_root()
    return sorted(str(path.relative_to(root)) for path in committed() if path not in mine)


def collisions() -> list[str]:
    """Every golden path more than one case claims (the injectivity half)."""
    seen: dict[Path, list[str]] = {}
    for golden in claimed():
        seen.setdefault(golden.path, []).append(f"{golden.writer}:{golden.case}")
    return sorted(
        f"{path.name} is claimed by {', '.join(cases)}"
        for path, cases in seen.items()
        if len(cases) > 1
    )


def plan_text(name: str) -> bytes:
    """What `studyforge plan` prints for one fixture corpus, as a build would encode it."""
    out = io.StringIO()
    plan_cli.main([str(FIXTURES / name)], out=out)
    return out.getvalue().encode(PLAN_ENCODING)


def _pages() -> tuple[Golden, ...]:
    """The unit pages, one per case the page regenerator declares."""
    built = [build() for build in pages.CASES]
    return tuple(
        Golden(
            path=case.golden,
            writer=pages.__name__,
            case=case.name,
            emit=case.render,
        )
        for case in built
    )


def _indexes() -> tuple[Golden, ...]:
    """The root indexes, one per fixture corpus the index regenerator derives."""
    return tuple(
        Golden(path=case.golden, writer=indexes.__name__, case=case.name, emit=case.render)
        for case in indexes.cases()
    )


def _containers() -> tuple[Golden, ...]:
    """The container pages, one per container the fixtures declare."""
    return tuple(
        Golden(path=case.golden, writer=containers.__name__, case=case.name, emit=case.render)
        for case in containers.cases()
    )


def _plans() -> tuple[Golden, ...]:
    """The plans, one per valid fixture corpus.

    ⚠️ The writer is the CLI module rather than a regenerator: a plan golden is
    rewritten by redirecting the command, which is why `tests/studyforge/cli/
    plan/test_cli.py` and not a `regenerate()` is what a reader is sent to.
    """
    return tuple(
        Golden(
            path=PLAN_TREE / f"{name}{PLAN_SUFFIX}",
            writer=plan_cli.__name__,
            case=name,
            emit=partial(plan_text, name),
        )
        for name in VALID
    )


def _where(was: bytes, now: bytes) -> str:
    """Where two byte streams first differ, and how long each is."""
    for offset, (left, right) in enumerate(zip(was, now, strict=False)):
        if left != right:
            return f"differs at byte {offset} ({left:#04x} committed, {right:#04x} produced)"
    return f"is {len(was)} bytes and {len(now)} were produced"
