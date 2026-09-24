"""The identifier half of R7: derived at run time, kept nowhere.

⭐ **Part of the product's own floor**, which `python3 -m tests.floor` runs from any
checkout. It began as a copy of the developer tooling's check; that tooling, and its
records, live on the branch `archive/process`, and nothing here depends on them.

**What it does.** Reads this machine's own identifiers — account name,
hostname, home directory, git author — and reports any tracked file that
carries one.

⛔ **The git arm reads the GLOBAL and SYSTEM scopes ONLY, never a scope an
office can write** (the argument is on `IDENTITY_SCOPES` below).
⭐ **The machine's real git identity sits in the user's own global file; a value
in `.git/config` is a working convention this repository sets for itself** — and
reading the second made this check's verdict on an unchanged tree a function of
who happened to be working.

**How you use it.** `check_identifiers(repo_root)`. `identifiers()` returns
`{what it is: the value}` for the machine it runs on; `check_identifiers`
accepts an override so the mechanism can be tested with fabricated values.
⭐ `identity_notice(repo_root)` is registered in `tests.floor.NOTICES` and
prints WHICH arms had a value to compare — **labels only, never values**.

⛔ **The arm DISCLOSES whether it was armed.** ⚠️ An arm
that derives nothing compares against nothing, and the floor printed the same
clean line it prints when a real identifier WAS derived and found in no tracked
file. ⛔ **Those two readings are indistinguishable and only one of them is a
guarantee** — *nothing printed* and *there was nothing to say* must
not be the same line. ⭐ **It is a NOTICE and never a failure:** an unarmed arm
is CORRECT inside the pinned image, which has no passwd entry and configures no
git identity by design.

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

from tests.floor import config
from tests.floor.report import Finding

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


#: ⛔ **The git scopes this module reads, in precedence order, and the only ones**.
#: ⚠️ **`--local` and `--worktree` are deliberately absent**, and the
#: argument is whose datum each scope holds:
#:
#: - ⭐ **Global and system are the MACHINE's.** `~/.gitconfig` is where a real
#:   name and address actually sit, so R7's git arm keeps its subject and keeps
#:   firing. ⛔ Emptying this tuple would be the weakening this must never
#:   become, and `identifiers()` would then be blind to the one scope that holds
#:   the datum.
#: - ⛔ **Local and worktree are the REPOSITORY's.** Every office holding a
#:   linked worktree shares one `.git/config` while `extensions.worktreeConfig`
#:   is unset, and a placeholder written there is indistinguishable from a real
#:   name to this check — four characters against `MIN_IDENTIFIER_CHARS`. So
#:   reading it reported this repository's own checkout vocabulary as a leak, in
#:   documents nobody had touched.
#:
#: ⭐ **The mirror image of `board/dispatch.py`, which reads `--local` and
#: refuses the global file for the same reason read the other way round:** a
#: branch description is the repository's own dispatch, an identity is the
#: machine's. ⛔ **An office's own author line is therefore passed PER INVOCATION
#: and set nowhere** — `git -c user.name=… -c user.email=… commit` — which is
#: the only form that never enters a shared slot.
IDENTITY_SCOPES = ("--global", "--system")


#: ⛔ **Every arm `identifiers()` can return, and what each derives FROM**.
#: ⭐ **This is the DENOMINATOR the floor prints**, for this reason: an arm that
#: derived nothing was never compared, so a tree clean of it is not a guarantee
#: about it. ⚠️ **A census, never a second derivation** —
#: `identity_notice` reports the keys `identifiers()` actually returned and
#: re-reads no scope of its own, so the two cannot disagree. ⛔ A label derived
#: and missing from here is PRINTED as drift rather than dropped.
IDENTIFIER_LABELS = (
    ("account name", "the passwd entry"),
    ("hostname", "the network name"),
    ("short hostname", "the network name, up to its first dot"),
    ("home directory", "$HOME, and only one carrying an account name"),
    ("git author name", "git user.name"),
    ("git author email", "git user.email"),
)


def _usable(value: str | None) -> str | None:
    """`value` if it is specific enough to be evidence, else None."""
    if not value:
        return None
    value = value.strip()
    if len(value) < MIN_IDENTIFIER_CHARS or value.lower() in GENERIC_IDENTIFIERS:
        return None
    return value


def _git_identity(key: str) -> str | None:
    """`key` as the MACHINE has it, or None when no scope this reads has it.

    ⛔ **Every scope is named on the command line** (`IDENTITY_SCOPES`), so no
    reading can fall through to the repository the process happens to be
    standing in. ⚠️ Asked scope by scope rather than with one bare `--get`,
    because git's own precedence puts `--local` first and that is exactly the
    answer this must not take.
    """
    git = shutil.which("git")
    if git is None:
        return None
    for scope in IDENTITY_SCOPES:
        try:
            result = subprocess.run(  # noqa: S603 - fixed argv, no shell
                [git, "config", scope, "--get", key],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
        except OSError, subprocess.SubprocessError:
            return None
        # ⛔ Exit 1 is *this scope has nothing*, never a failure: ask the next.
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    return None


def identifiers() -> dict[str, str]:
    """Derive `{what it is: the value}` for this machine now, and keep it nowhere.

    ⛔ The return value is used for one comparison and discarded. It is never
    written to a file, never logged, never put in a finding's message, and
    never cached between runs — the whole point of deriving it is that nothing
    has to hold it.

    ⚠️ It is legitimately empty in some environments. Inside the dev image
    there is no passwd entry and no global git file, so this half of the check
    has nothing to compare and quietly does nothing — which is correct, because
    a leak originates on the machine that has those values, not in the
    container. `check_shapes` runs everywhere regardless.

    ⛔ **What that paragraph used to say — *"git has no identity"* in there —
    was FALSE, and it was measured.** ⚠️ `docker/dev/check`
    mounts the git common directory into the image so a linked worktree can
    answer git at all, so a repository-scoped identity was readable from inside
    the container off that mount. ⭐ **It is true again now, and by
    construction rather than by luck: `IDENTITY_SCOPES` names no scope that
    mount carries.**
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
        usable = _usable(_git_identity(key))
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


def _census(armed: list[str], unarmed: list[str], known: list[str]) -> str:
    """Build the line carrying which arms armed, which did not, and the denominator."""
    head = (
        f"personal data (R7, W307): the identifier arm derived {len(armed)} of "
        f"{len(known)} identifier(s) on this machine — "
    )
    head += f"ARMED: {', '.join(armed)}." if armed else "ARMED: NONE, so NOTHING was compared."
    if unarmed:
        return (
            f"{head} NOT ARMED, and nothing was compared for these: "
            f"{', '.join(unarmed)} — a clean floor is NOT a guarantee about any of "
            f"them (FND-07)."
        )
    return f"{head} NOT ARMED: none — every arm had a value to compare."


def _standing_clause() -> str:
    """Build the line saying what an unarmed arm means, and why it is not a failure."""
    return (
        f"  ⛔ Labels only, never values (R7) — printing one would be the leak this check "
        f"exists to prevent. ⭐ An UNARMED arm is CORRECT in the pinned image, which has "
        f"no passwd entry and configures no git identity, so this is a NOTICE and never a "
        f"failure. ⚠️ The git arm reads {' and '.join(IDENTITY_SCOPES)} ONLY (W305), so an "
        f"identity in a repository's own config arms nothing here. ⭐ check_shapes sweeps "
        f"every tracked file regardless and is unaffected by any of this."
    )


def identity_notice(root: Path) -> list[str]:
    """Report which identifier arms had a value to compare, by label and never by value.

    ⛔ **A NOTICE, never a check**. An arm that derives nothing is
    CORRECT inside the pinned image — no passwd entry, and no git identity at
    either scope `IDENTITY_SCOPES` names — so this may not fail a build, and it
    is registered in `NOTICES` alone.

    ⛔ **It reports what `identifiers()` returned and derives nothing of its
    own.** A second, independent reading could disagree with the one the check
    actually used, and then the disclosure would be about a different run than
    the verdict.

    ⚠️ `root` is taken for the `NOTICES` signature and deliberately unread: what
    arms is a property of the MACHINE, never of the tree being swept.
    """
    derived = identifiers()
    sources = dict(IDENTIFIER_LABELS)
    known = [label for label, _ in IDENTIFIER_LABELS]
    armed = [label for label in known if label in derived]
    unarmed = [label for label in known if label not in derived]

    lines = [_census(armed, unarmed, known), _standing_clause()]
    for label in unarmed:
        lines.append(f"    NOT ARMED — {label}: nothing usable from {sources[label]}.")
    drift = sorted(label for label in derived if label not in sources)
    if drift:
        lines.append(
            f"    ⛔ DERIVED and absent from IDENTIFIER_LABELS, so this census is STALE "
            f"and its denominator UNDERSTATES the arm: {', '.join(drift)}."
        )
    return lines
