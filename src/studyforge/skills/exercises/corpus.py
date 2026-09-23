r"""The whole pass over a corpus: the ledger once, every page, the reasons, and the commit.

**What it does.** Takes the source ledger once, authors every page through
`loop.author_page`, asks the author for a written reason for every ledger entry
nothing shipped accounts for, closes the accounting, and commits everything —
bundles, the reader's workspace files, each unit's coverage report and the
ledger — into the corpus repository, additively.

**How you use it.**

    authored = author_corpus(root, source="demo", material=material, graders=graders,
                             pages=pages, author=author, judge=judge, runner=runner)
    authored.shortfalls                 # (page, Shortfall) for every refused exercise
    authored.bare                       # every page left with nothing shipped (R6)

**Depends on.** This package's `drafts`, `gating`, `loop`, `ledger`,
`accounting` and `plan`; `exercise` for an origin's two spellings and a path's
rule; `exercise.bundle` for where a unit's bundles sit; `archive.scrub` for R7.
Standard library only.

## ⛔ THE LEDGER IS TAKEN ONCE, BEFORE ANY EXERCISE IS GATED

⭐ **`AX-07`'s one ordering constraint.** `G5` and `Q5` ask the ledger about an
origin *during* the gate run, and the accounting closes over the same object at
the end, so the two cannot disagree about what the source was.

## ⛔ ONLY INSIDE THE CORPUS ROOT, AND ONLY ADDITIVELY (R3)

⭐ **Every file is checked before any is written.** A file already there with
the same bytes is kept; one there with different bytes refuses the whole pass,
naming it, and nothing is written — so a refusal never leaves half a pass in
the tree. ⛔ Every path is corpus-root-relative and passes `require_path`, so
nothing this pass writes can land outside the root.

## ⛔ RE-RUNNING WITH NOTHING CHANGED REWRITES NOTHING (R10)

⭐ **A unit whose committed coverage report matches its page's digests and its
plan is not re-authored**, so a model is never asked again for work already
proven, and what it said the first time stays. A ledger entry whose bytes are
unchanged keeps the reason it was given. ⚠️ **A unit whose page moved is
refused, naming its directory**: its bundles were proven against material that
has changed, and rewriting them is what R3 forbids.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from studyforge.archive.scrub import assert_clean
from studyforge.exercise import Origin, origin_document, origin_in, require_path
from studyforge.exercise.bundle import BUNDLES_DIRNAME, Places
from studyforge.skills.exercises.accounting import account, accounts_for, ledger_document
from studyforge.skills.exercises.drafts import Author, AuthoringError, Judge, Page, require_page
from studyforge.skills.exercises.gating import Runner, json_bytes
from studyforge.skills.exercises.ledger import Entry, Ledger, key_of, take
from studyforge.skills.exercises.loop import Shortfall, author_page
from studyforge.skills.exercises.plan import plan_document, plan_for

#: Each unit's coverage report, beside its bundles and never inside one.
COVERAGE_FILENAME = "coverage.json"

#: The source ledger, at the root of the bundles' tree.
LEDGER_PATH = f"{BUNDLES_DIRNAME}/ledger.json"

#: The coverage report's version, and its key order (R10).
COVERAGE_API = 1
COVERAGE_KEYS = (
    "coverage_api",
    "page",
    "kind",
    "case",
    "digests",
    "plan",
    "shipped",
    "accounts",
    "shortfalls",
)

#: The keys of one named shortfall in a coverage report, in write order.
SHORTFALL_REPORT_KEYS = ("slot", "gate", "says", "output")


@dataclass(frozen=True, slots=True)
class Covered:
    """One unit after the pass: what shipped, what did not, and whether it was authored now."""

    page: str
    unit: str
    shipped: tuple[str, ...]
    shortfalls: tuple[Shortfall, ...]
    authored: bool


@dataclass(frozen=True, slots=True)
class Authored:
    """The whole pass: every unit, and every path it created or found already there."""

    pages: tuple[Covered, ...]
    written: tuple[str, ...]
    kept: tuple[str, ...]

    @property
    def shortfalls(self) -> tuple[tuple[str, Shortfall], ...]:
        """Every refused exercise, with the page it was planned for."""
        return tuple((page.page, missed) for page in self.pages for missed in page.shortfalls)

    @property
    def bare(self) -> tuple[str, ...]:
        """⛔ Every page left with nothing shipped, named as such (R6)."""
        return tuple(page.page for page in self.pages if not page.shipped)


def author_corpus(
    root: Path | str,
    *,
    source: str,
    material: Iterable[str],
    graders: Iterable[str],
    pages: Sequence[Page],
    author: Author,
    judge: Judge | None = None,
    runner: Runner | None = None,
) -> Authored:
    """Run the whole pass: author, gate and commit every page — ⛔ additively, once (R3, R10)."""
    base = Path(root)
    ledger = take(base, material, graders, "the ledger")
    files: list[tuple[str, bytes]] = []
    covered: list[Covered] = []
    accounts: dict[str, Origin] = {}
    for page in _in_order(pages):
        where = f"the page '{page.path}'"
        require_page(page, ledger, where)
        unit = _unit_of(page)
        plan = plan_for(page.words, page.skills, page.tier, where)
        fingerprint = _fingerprint(page, ledger)
        recorded = _read(base / unit / COVERAGE_FILENAME, where)
        if recorded is not None:
            covered.append(_reused(recorded, page, unit, fingerprint, plan_document(plan), where))
            accounts |= _accounts_in(recorded, where)
            continue
        if (base / unit).exists():
            raise _moved(unit, where, "holds exercises and no coverage report")
        outcome = author_page(page, ledger, author, judge, runner, source=source, where=where)
        for gated in outcome.shipped:
            files.extend(gated.files)
            accounts |= dict(gated.accounts)
        document = {
            "coverage_api": COVERAGE_API,
            "page": page.path,
            "kind": page.kind,
            "case": outcome.case,
            "digests": fingerprint,
            "plan": plan_document(outcome.plan),
            "shipped": [gated.places.bundle for gated in outcome.shipped],
            "accounts": [
                {"exercise": name, "origin": origin_document(origin)}
                for gated in outcome.shipped
                for name, origin in gated.accounts
            ],
            "shortfalls": [_shortfall_document(missed) for missed in outcome.shortfalls],
        }
        files.append((f"{unit}/{COVERAGE_FILENAME}", _document_bytes(document, where)))
        covered.append(
            Covered(
                page.path,
                unit,
                tuple(document["shipped"]),
                outcome.shortfalls,
                authored=True,
            )
        )
    reasons = _reasons(ledger, accounts, author, _read(base / LEDGER_PATH, "the ledger"))
    accounted = account(ledger, accounts, reasons, "the ledger")
    files.append((LEDGER_PATH, _document_bytes(ledger_document(ledger, accounted), "the ledger")))
    written, kept = commit(base, files, "the authoring pass")
    return Authored(tuple(covered), written, kept)


def commit(
    root: Path, files: Sequence[tuple[str, bytes]], where: str
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Create every file not already there, refusing ALL of them if any would be rewritten.

    ⛔ **R3, checked whole before a byte is written.** A file present with the
    same bytes is kept, which is what makes a re-run write nothing (R10); a
    file present with different bytes — or two of this pass's own files at one
    path — refuses the pass and names the path.
    """
    wanted: dict[str, bytes] = {}
    for path, data in files:
        inside = require_path(path, "a path the authoring pass writes", where)
        if wanted.setdefault(inside, data) != data:
            raise AuthoringError(
                f"{where}: two of this pass's own files land on '{inside}' with "
                f"different bytes, so one of them would be lost."
            )
    rewritten = [
        path
        for path, data in wanted.items()
        if (root / path).exists() and not _same(root / path, data)
    ]
    if rewritten:
        raise AuthoringError(
            f"{where}: {len(rewritten)} file(s) this pass would write are already in the "
            f"corpus with different contents, the first at '{rewritten[0]}'. Generation "
            f"is non-destructive (R3): nothing was written, and no existing file is "
            f"rewritten to make room."
        )
    written, kept = [], []
    for path, data in wanted.items():
        target = root / path
        if target.exists():
            kept.append(path)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        written.append(path)
    return tuple(written), tuple(kept)


def _in_order(pages: Sequence[Page]) -> tuple[Page, ...]:
    """Return the pages in unit order, refusing two pages that would share one unit."""
    ordered = tuple(sorted(pages, key=_unit_of))
    units = [_unit_of(page) for page in ordered]
    repeated = sorted({unit for unit in units if units.count(unit) > 1})
    if repeated:
        raise AuthoringError(
            f"the authoring pass: {len(repeated)} unit(s) are claimed by two pages, the "
            f"first '{repeated[0]}'. A unit's exercises are one page's, or their "
            f"ordinals and their coverage report would be two pages' at once."
        )
    return ordered


def _unit_of(page: Page) -> str:
    """Return the directory a unit's bundles and its coverage report sit under."""
    return Places(page.address, page.variant, page.unit, 1).bundle.rsplit("/", 1)[0]


def _fingerprint(page: Page, ledger: Ledger) -> dict[str, str]:
    """Return what the page and its test files digested to, by path — the unit's identity."""
    wanted = {page.path, *page.graders}
    return {source.path: source.digest for source in ledger.sources if source.path in wanted}


def _reused(
    recorded: dict, page: Page, unit: str, fingerprint: dict, plan: dict, where: str
) -> Covered:
    """Keep a unit whose recorded report still describes it — ⛔ or refuse it, naming it."""
    same = (
        recorded.get("page") == page.path
        and recorded.get("kind") == page.kind
        and recorded.get("digests") == fingerprint
        and recorded.get("plan") == plan
    )
    if not same:
        raise _moved(unit, where, "was authored from material or a plan that has since moved")
    missed = tuple(
        Shortfall(entry.get("slot"), entry.get("gate"), entry.get("says"), entry.get("output", ""))
        for entry in recorded.get("shortfalls", ())
    )
    return Covered(page.path, unit, tuple(recorded.get("shipped", ())), missed, authored=False)


def _accounts_in(recorded: dict, where: str) -> dict[str, Origin]:
    """Return the `(exercise, origin)` pairs a kept unit's report recorded, for the accounting."""
    found: dict[str, Origin] = {}
    for entry in recorded.get("accounts", ()):
        if not isinstance(entry, dict):
            raise AuthoringError(f"{where}: a committed coverage report's account is not an object.")
        origin = origin_in(entry, where)
        if origin is not None:
            found[entry.get("exercise")] = origin
    return found


def _reasons(
    ledger: Ledger, accounts: dict[str, Origin], author: Author, prior: dict | None
) -> dict[str, str]:
    """Collect a reason for every entry nothing shipped accounts for — ⭐ kept while unchanged."""
    carried = _prior_reasons(prior)
    reasons: dict[str, str] = {}
    for entry in ledger.entries:
        if any(accounts_for(entry, origin) for origin in accounts.values()):
            continue
        said = carried.get(_identity(entry))
        reasons[key_of(entry)] = said if said is not None else author.excuse(entry)
    return reasons


def _prior_reasons(prior: dict | None) -> dict[tuple, str]:
    """Return the reasons a committed ledger gave, keyed by what each entry was."""
    if prior is None:
        return {}
    return {
        (row.get("kind"), row.get("path"), row.get("ordinal"), row.get("digest")): row["reason"]
        for row in prior.get("entries", ())
        if isinstance(row, dict) and isinstance(row.get("reason"), str)
    }


def _identity(entry: Entry) -> tuple:
    """Return what an entry was: kind, path, position and the digest of its bytes."""
    return (entry.kind, entry.path, entry.ordinal, entry.digest)


def _shortfall_document(missed: Shortfall) -> dict:
    """One refused exercise as its unit's report names it, in `SHORTFALL_REPORT_KEYS` order."""
    return {"slot": missed.slot, "gate": missed.gate, "says": missed.says, "output": missed.output}


def _document_bytes(document: object, where: str) -> bytes:
    """Encode a document as this pass writes it, gated for personal data first (R7)."""
    assert_clean(document, where)
    return json_bytes(document)


def _read(path: Path, where: str) -> dict | None:
    """Read one document this skill wrote earlier, or `None` when there is none."""
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError, UnicodeDecodeError, ValueError:
        raise AuthoringError(
            f"{where}: a document this skill committed earlier will not read, so "
            f"nothing can say whether the unit it describes has moved."
        ) from None
    if not isinstance(value, dict):
        raise AuthoringError(f"{where}: a document this skill committed is not an object.")
    return value


def _same(path: Path, data: bytes) -> bool:
    """Is the file at `path` exactly these bytes? ⛔ A directory is never the same."""
    return path.is_file() and path.read_bytes() == data


def _moved(unit: str, where: str, why: str) -> AuthoringError:
    """Return the refusal for a unit whose committed exercises may not be rewritten (R3)."""
    return AuthoringError(
        f"{where}: the unit at '{unit}' {why}. Its exercises were proven against that "
        f"material, and rewriting them is what R3 forbids. Remove '{unit}' and "
        f"'{LEDGER_PATH}' from the corpus and run the pass again."
    )
