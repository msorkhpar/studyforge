"""Run one audit probe in a child process and read back what it observed.

**What it does.** Invokes `tests/harness/probes/audit.py` for one subject and
returns its record: every read and every process start the interpreter itself saw
while the probe was armed.

**How you use it.**

    from tests.harness import probe

    seen = probe.observe("index", tmp_path)
    seen.opened        # ('open\\t/…/toc.json', …) — the population, printed first
    seen.digest        # what the probe rendered, so an empty population is not a pass

**Depends on.** `tests.support.run` for the subprocess — ⛔ the one spelling in
this repository, with fixed argv and no shell — and nothing else.

⚠️ **A child process rather than an in-process hook**, and it is not a
preference: `sys.addaudithook` cannot be undone, so a hook installed in the
pytest process would observe every test that ran afterwards. The probe's own
module docstring carries the rest of the reasoning.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from tests.support import repository_root, run

#: The probe, as `python3 -m` spells it.
PROBE = "tests.harness.probes.audit"


@dataclass(frozen=True)
class Record:
    """What one probe observed, and what it did while being observed."""

    subject: str
    opened: tuple[str, ...]
    spawned: tuple[str, ...]
    digest: str | None
    produced: int | None

    def population(self) -> str:
        """Every observation, one per line, for printing BEFORE any verdict."""
        lines = [f"{self.subject}: {len(self.opened)} read(s), {len(self.spawned)} spawn(s)"]
        lines += [f"  read   {entry}" for entry in self.opened]
        lines += [f"  spawn  {entry}" for entry in self.spawned]
        if self.digest is not None:
            lines.append(f"  made   {self.produced} bytes, sha256 {self.digest}")
        return "\n".join(lines)


def observe(subject: str, work: Path) -> Record:
    """Run one probe subject with `work` as its scratch directory.

    ⛔ A failed probe raises rather than returning an empty record: "it observed
    nothing" and "it never ran" must never arrive as the same answer, which is
    the same rule `tests.support.is_ignored` states for git's exit codes.
    """
    result = run([sys.executable, "-m", PROBE, subject, str(work)], cwd=repository_root())
    assert result.returncode == 0, (
        f"probe {subject!r} exited {result.returncode} and observed nothing: "
        f"{result.stdout}{result.stderr}"
    )
    record = json.loads(result.stdout.splitlines()[-1])
    return Record(
        subject=subject,
        opened=tuple(record["opened"]),
        spawned=tuple(record["spawned"]),
        digest=record.get("digest"),
        produced=record.get("bytes"),
    )
