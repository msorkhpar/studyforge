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
    authored.ledger                     # the ledger rows kept, added, changed, dropped

**Depends on.** This package's `drafts`, `gating`, `loop`, `ledger`,
`accounting`, `merge`, `writes`, `plan` and `coverage`; `exercise` for an origin's two
spellings; `exercise.bundle` for where a unit's bundles sit; `archive.scrub`
for R7. Standard library only.

## ⛔ THE LEDGER IS TAKEN ONCE, BEFORE ANY EXERCISE IS GATED

⭐ **The one ordering constraint.** `G5` and `Q5` ask the ledger about an
origin *during* the gate run, and the accounting closes over the same object at
the end, so the two cannot disagree about what the source was.

## ⛔ ONLY INSIDE THE CORPUS ROOT, AND ONLY ADDITIVELY (R3) — `writes`' rule

⭐ **Every file is checked before any is written**, and a refusal never leaves
half a pass in the tree. ⚠️ The ledger is the one file rewritten, and `merge`
is why that is additive. ⛔ Its read, merge and write happen under
`writes.exclusive`, so two passes at once take turns and lose no row.

## ⛔ A PASS OVER PART OF A CORPUS OWNS ONLY WHAT IT READ

⭐ **The ledger is one file for the whole corpus, and this pass owns only the
rows of the files it read.** `merge` keeps every other row byte-identical, and
`_elsewhere` reads what units outside the pass account for, so a page this pass
was not handed never loses the exercise its entries are built on.

## ⛔ RE-RUNNING WITH NOTHING CHANGED REWRITES NOTHING (R10)

⭐ **A unit whose committed coverage report matches its page's digests and its
plan is not re-authored**, so a model is never asked again for work already
proven, and what it said the first time stays. A ledger entry whose bytes are
unchanged keeps the reason it was given. ⚠️ **A stale unit is refused,
naming its directory**: its bundles were proven against material that has
changed, and generation never rewrites what it did not write. ⭐ **Every page
is read before any is authored**, so the refusal comes first and counts every
stale unit the pass was handed (`coverage.stale_summary`), never one at a time
after the pages before it were authored.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from studyforge.archive.scrub import assert_clean
from studyforge.exercise import Origin, origin_document, origin_in
from studyforge.exercise.bundle import BUNDLES_DIRNAME, Places
from studyforge.skills.exercises.accounting import account, accounts_for, ledger_document
from studyforge.skills.exercises.coverage import (
    COVERAGE_API,
    COVERAGE_FILENAME,
    STALE_COMMAND,
    Stale,
    stale_of,
    stale_summary,
)
from studyforge.skills.exercises.drafts import Author, AuthoringError, Judge, Page, require_page
from studyforge.skills.exercises.gating import Runner, json_bytes
from studyforge.skills.exercises.ledger import Entry, Ledger, key_of, source_digest, take
from studyforge.skills.exercises.loop import Shortfall, author_page, carried_practices, plan_page
from studyforge.skills.exercises.merge import Delta, merged
from studyforge.skills.exercises.plan import plan_document
from studyforge.skills.exercises.writes import commit, exclusive

#: The source ledger, at the root of the bundles' tree.
LEDGER_PATH = f"{BUNDLES_DIRNAME}/ledger.json"


@dataclass(frozen=True, slots=True)
class Covered:
    """One unit after the pass: what shipped, what did not, and whether it was authored now."""

    page: str
    unit: str
    shipped: tuple[str, ...]
    shortfalls: tuple[Shortfall, ...]
    authored: bool
    reasoned: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Authored:
    """The whole pass: every unit, and every path it created or found already there."""

    pages: tuple[Covered, ...]
    written: tuple[str, ...]
    kept: tuple[str, ...]
    #: ⭐ What the pass did to the committed ledger, row by row.
    ledger: Delta = Delta()

    @property
    def shortfalls(self) -> tuple[tuple[str, Shortfall], ...]:
        """Every refused exercise, with the page it was planned for."""
        return tuple((page.page, missed) for page in self.pages for missed in page.shortfalls)

    @property
    def bare(self) -> tuple[str, ...]:
        """⛔ Every page left with nothing shipped, named as such (R6)."""
        return tuple(page.page for page in self.pages if not page.shipped)

    @property
    def reasoned(self) -> tuple[tuple[str, str], ...]:
        """⭐ Every aspect no exercise was planned to check, with its page.

        The part of a thin plan a reviewer reads first: each one carries its
        written reason in the unit's coverage report.
        """
        return tuple((page.page, aspect) for page in self.pages for aspect in page.reasoned)


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
    read = [_reading(base, page, ledger) for page in _in_order(pages)]
    _require_fresh([stale for *_, stale in read if stale is not None])
    for page, unit, plan, recorded, _ in read:
        where = f"the page '{page.path}'"
        reasoned = tuple(aspect.id for aspect in plan.reasoned)
        if recorded is not None:
            kept = _reused(recorded, page, unit)
            covered.append(replace(kept, reasoned=reasoned))
            accounts |= _accounts_in(recorded, where)
            continue
        carried = carried_practices(base, page, where)
        outcome = author_page(
            page, ledger, author, judge, runner, source=source, where=where, carried=carried
        )
        for gated in outcome.shipped:
            files.extend(gated.files)
            accounts |= dict(gated.accounts)
        document = {
            "coverage_api": COVERAGE_API,
            "page": page.path,
            "kind": page.kind,
            "quiz": page.quiz,
            "case": outcome.case,
            "digests": _fingerprint(page, ledger),
            "sources": _sources(base, page),
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
                reasoned=reasoned,
            )
        )
    with exclusive(base, "the authoring pass"):  # ⛔ a concurrent pass waits (`writes`)
        accounts = _elsewhere(base, ledger, {c.unit for c in covered}) | accounts
        prior = _read(base / LEDGER_PATH, "the ledger")
        reasons = _reasons(ledger, accounts, author, prior)
        accounted = account(ledger, accounts, reasons, "the ledger")
        document, delta = merged(base, prior, ledger_document(ledger, accounted), "the ledger")
        files.append((LEDGER_PATH, _document_bytes(document, "the ledger")))
        written, kept = commit(base, files, "the authoring pass", replaces=(LEDGER_PATH,))
    return Authored(tuple(covered), written, kept, delta)


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


def _sources(base: Path, page: Page) -> dict[str, str]:
    """Return what the files the page's exercises are copied from digest to, by path."""
    return {
        path: source_digest(base, path, f"the page '{page.path}'") for path in sorted(page.sources)
    }


def _reading(base: Path, page: Page, ledger: Ledger) -> tuple:
    """Read one page before anything is authored: its unit, its plan, its report, and staleness.

    ⛔ **Every page is read before any is authored**, so a stale unit is
    refused before an author is asked for anything.
    """
    where = f"the page '{page.path}'"
    require_page(page, ledger, where)
    unit = _unit_of(page)
    plan = plan_page(page, ledger, where)
    recorded = _read(base / unit / COVERAGE_FILENAME, where)
    if recorded is None:
        if (base / unit).exists():
            raise _moved(unit, where, "holds exercises and no coverage report")
        return page, unit, plan, None, None
    planned = {"kind": page.kind, "quiz": page.quiz, "plan": plan_document(plan)}
    stale = stale_of(
        unit, recorded, page.path, _fingerprint(page, ledger), planned, _sources(base, page)
    )
    return page, unit, plan, recorded, stale


def _require_fresh(stale: list[Stale]) -> None:
    """⛔ Refuse the pass up front when any unit it was handed is stale, naming the first.

    ⚠️ **A report written under another `coverage_api`, or planned under
    another `plan_api`, is stale by its contract**, both read through
    `version.check`: a plan's count set by a rule this build no longer applies
    is re-planned by its aspects, never silently kept.
    """
    if stale:
        first = stale[0]
        raise _moved(
            first.unit, f"the authoring pass: {stale_summary(stale)}", f"is stale: {first.says}"
        )


def _reused(recorded: dict, page: Page, unit: str) -> Covered:
    """Keep a unit whose recorded report still describes it, as it recorded itself."""
    missed = tuple(
        Shortfall(entry.get("slot"), entry.get("gate"), entry.get("says"), entry.get("output", ""))
        for entry in recorded.get("shortfalls", ())
    )
    return Covered(page.path, unit, tuple(recorded.get("shipped", ())), missed, authored=False)


def _elsewhere(base: Path, ledger: Ledger, units: set[str]) -> dict[str, Origin]:
    """Return what the units OUTSIDE this pass account for, among the files it read.

    ⛔ **A file this pass read may carry a page it was not handed**, and that
    page's committed exercises still account for its entries — without them a
    pass over one page would re-excuse another page's built-on example.
    """
    read = {source.path for source in ledger.sources}
    found: dict[str, Origin] = {}
    for path in sorted(base.glob(f"{BUNDLES_DIRNAME}/**/{COVERAGE_FILENAME}")):
        unit = path.parent.relative_to(base).as_posix()
        if unit not in units:
            recorded = _read(path, f"the unit '{unit}'") or {}
            accounts = _accounts_in(recorded, f"the unit '{unit}'").items()
            found |= {name: origin for name, origin in accounts if origin.path in read}
    return found


def _accounts_in(recorded: dict, where: str) -> dict[str, Origin]:
    """Return the `(exercise, origin)` pairs a kept unit's report recorded, for the accounting."""
    found: dict[str, Origin] = {}
    for entry in recorded.get("accounts", ()):
        if not isinstance(entry, dict):
            raise AuthoringError(
                f"{where}: a committed coverage report's account is not an object."
            )
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


def _moved(unit: str, where: str, why: str) -> AuthoringError:
    """Return the refusal for a unit whose committed exercises may not be rewritten (R3)."""
    return AuthoringError(
        f"{where}. The unit at '{unit}' {why}. Its exercises were proven against that "
        f"material, and generation never rewrites what it did not write. Remove '{unit}' and "
        f"its practice counterpart from the corpus (`{STALE_COMMAND} --remove`) and run the "
        f"pass again: the ledger keeps every other page's rows."
    )
