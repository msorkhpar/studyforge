"""The identifier half of R7: derived at run time, kept nowhere.

**What it does.** Reads this machine's own identifiers — account name,
hostname, home directory, git author — and reports any tracked file that
carries one.

**How you use it.** `check_identifiers(repo_root)`. `identifiers()` returns
`{what it is: the value}` for the machine it runs on; `check_identifiers`
accepts an override so the mechanism can be tested with fabricated values.

**Depends on.** `getpass`, `socket`, `os` and `config`; `git` if it happens to
be installed — its absence narrows the sweep and never fails it.

⛔ **Nothing here is ever written down.** The values are computed on demand,
compared, and discarded: never persisted, never cached between runs, never put
in a finding's message. ⭐ **A check that stores what it is looking for is the
leak it exists to prevent.**

⛔ **This is why there is no username *pattern* anywhere in this package, and
there must never be one.** To match "this is the user's account name" a pattern
would have to hold that name — the exact datum R7 forbids — and the only
alternative is an unanchored pattern matching every symbol in every codebase. A
gate that must contain the secret to detect the secret is self-defeating.
Deriving the value at run time is the escape from that, and it is available
here precisely because this module runs on the machine that has it.
"""

from __future__ import annotations

import getpass
import os
import re
import shutil
import socket
import subprocess
from pathlib import Path

from tools.quality import config
from tools.quality.report import Finding

RULE_IDENTIFIER = "personal-data-identifier"

MIN_IDENTIFIER_CHARS = 3
GENERIC_IDENTIFIERS = frozenset(
    {
        "root",
        "user",
        "users",
        "home",
        "test",
        "tests",
        "dev",
        "admin",
        "nobody",
        "runner",
        "ubuntu",
        "debian",
        "docker",
        "localhost",
        "build",
        "builder",
        "app",
        "node",
        "python",
        "git",
        "ci",
        "main",
        "default",
        "container",
        "workspace",
        "local",
        "example",
    }
)


def _usable(value: str | None) -> str | None:
    """`value` if it is specific enough to be evidence, else None."""
    if not value:
        return None
    value = value.strip()
    if len(value) < MIN_IDENTIFIER_CHARS or value.lower() in GENERIC_IDENTIFIERS:
        return None
    return value


def _git_config(key: str) -> str | None:
    """One git config value, or None when git is absent or has nothing to say."""
    git = shutil.which("git")
    if git is None:
        return None
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [git, "config", "--get", key],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except OSError, subprocess.SubprocessError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def identifiers() -> dict[str, str]:
    """Derive `{what it is: the value}` for this machine now, and keep it nowhere.

    ⛔ The return value is used for one comparison and discarded. It is never
    written to a file, never logged, never put in a finding's message, and
    never cached between runs — the whole point of deriving it is that nothing
    has to hold it.

    ⚠️ It is legitimately empty in some environments. Inside the dev image
    there is no passwd entry, `HOME` is `/tmp`, and git has no identity, so
    this half of the check has nothing to compare and quietly does nothing —
    which is correct, because a leak originates on the machine that has those
    values, not in the container. `check_shapes` runs everywhere regardless.
    """
    found: dict[str, str] = {}

    try:
        account = _usable(getpass.getuser())
    except OSError, KeyError:
        account = None  # a bare numeric uid has no passwd entry
    if account:
        found["account name"] = account

    try:
        host = socket.gethostname()
    except OSError:
        host = ""
    for label, value in (("hostname", host), ("short hostname", host.split(".")[0])):
        usable = _usable(value)
        if usable:
            found[label] = usable

    home = os.environ.get("HOME") or ""
    # ⚠️ Only a home that carries an account name. `/tmp` and `/root` are the
    # same on every machine, so matching them would report the container's own
    # environment as a leak.
    if re.fullmatch(r"/(?:home|Users)/[^/]+/?", home) and _usable(home.rstrip("/").split("/")[-1]):
        found["home directory"] = home.rstrip("/")

    for label, key in (("git author name", "user.name"), ("git author email", "user.email")):
        usable = _usable(_git_config(key))
        if usable:
            found[label] = usable

    return found


def check_identifiers(root: Path, values: dict[str, str] | None = None) -> list[Finding]:
    """Every tracked file carrying one of this machine's own identifiers.

    `values` exists so the mechanism can be tested with fabricated identifiers
    on a machine that has none of them — ⛔ never so that a real one can be
    written into a test.
    """
    if values is None:
        values = identifiers()
    if not values:
        return []

    # Word-bounded, so a three-character account name cannot match inside a
    # longer word and turn every file into a finding.
    matchers = [
        (label, re.compile(r"(?<![A-Za-z0-9_\-])" + re.escape(value) + r"(?![A-Za-z0-9_\-])"))
        for label, value in values.items()
    ]

    findings: list[Finding] = []
    for path in config.text_files(root):
        relative = config.relative(path, root)
        text = config.read_text(path)
        if text is None:
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            for label, matcher in matchers:
                if matcher.search(line):
                    findings.append(
                        Finding(
                            path=relative,
                            line=number,
                            rule=RULE_IDENTIFIER,
                            message=(
                                f"carries this machine's {label} (R7). Session context is "
                                f"read-only background, never material to write down — use "
                                f"a placeholder."
                            ),
                        )
                    )
                    break
    return findings
