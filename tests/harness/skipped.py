"""What a test run could not reach, printed in every run's summary.

⭐ **The product suite's OWN `unreachable_population` and `skip_reason`**, so the disclosure
prints in any checkout.

**How you use it.** The root `conftest.py` writes `unreachable_population(stats)` under every
run's summary, where `stats` is pytest's own tally (`terminalreporter.stats`).

**Depends on.** `collections` — the standard library.

⛔ **A disclosure and never a verdict**: it returns lines and no exit code, because
what an environment cannot reach is host state no branch controls. ⚠️ Printed on an EMPTY
population too: `green` with nothing skipped and `green` with a hole are two answers, and only
a line present in BOTH tells them apart.
"""

from __future__ import annotations

from collections import Counter

#: ⛔ **The label every test run prints, reached or not**.
UNREACHABLE = "unreachable population"

#: What pytest prefixes to a skip's own reason, dropped so the reason reads as typed.
SKIP_PREFIX = "Skipped: "


def skip_reason(report: object) -> str:
    """Return the reason a skipped report gave, as its author wrote it.

    ⭐ Read off pytest's `longrepr` — `(path, line, "Skipped: reason")` for a skip —
    and never matched against a list: a reason no list anticipated still prints.
    """
    longrepr = getattr(report, "longrepr", None)
    text = longrepr[2] if isinstance(longrepr, tuple) and len(longrepr) == 3 else longrepr
    reason = str(text or "no reason given")
    return reason.removeprefix(SKIP_PREFIX)


def unreachable_population(stats: dict) -> list[str]:
    """Return the tests this run did not reach, as a COUNT and each REASON.

    ⛔ **Derived from the run's own tally** (`terminalreporter.stats`), never typed:
    a test count, one per skipped report, as pytest's closing line counts them.
    ⛔ **A disclosure and never a verdict** — it returns lines and
    no exit code, because what is unreachable is host state no branch controls.
    """
    reasons = Counter(skip_reason(report) for report in stats.get("skipped", []))
    total = sum(reasons.values())
    if not total:
        return [f"{UNREACHABLE}: 0 skipped test(s) — this run reached every test it collected"]
    lines = [
        f"{UNREACHABLE}: {total} skipped test(s) — this run's green does not cover them "
        f"(a disclosure, never a failure)"
    ]
    for reason, count in sorted(reasons.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"  {count} × {reason}")
    return lines
