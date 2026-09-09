"""The shape half of R7: patterns that hold no value.

**What it does.** Recognises the four personal-data shapes a tracked file must
not carry — an absolute home path, an email address, an local hostname, a bearer
token — and sweeps the tree for them, skipping the registered negative-fixture
directories.

**How you use it.** `check_shapes(repo_root)` for the sweep; `shape_matches`
for one string. ⭐ **Adding a rule is one entry in `SHAPES`** and the sweep is
already tree-wide, so a new shape reaches every file the moment it exists.

**Depends on.** `config` for the tree and the registry, and `re`. Nothing else,
and deliberately nothing that holds a value.

⛔ **Every rule here is a shape, never a literal.** This module can be read by
anybody without learning anything about anyone — which is the property that
lets it be committed at all.
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.quality import config
from tools.quality.report import Finding

RULE_SHAPE = "personal-data"

#: R7's shapes. ⛔ Every one is a *shape*: none contains a value, so this
#: module can be read by anybody without learning anything about anyone.
#:
#: ⚠️ Two deliberate divergences from the reviewer's grep in
#: `docs/conventions/review-rubric.md` §1a, both because a build-failing check
#: may not cry wolf the way a human grep may — a reviewer dismisses a hit in
#: writing, a gate that fires on correct code just gets switched off.
#:
#: - ⛔ **`$HOME` and `~/` are NOT flagged.** They are references, not values,
#:   and `CLAUDE.md` names the environment variable as the *sanctioned* way to
#:   carry a real value in shipped code. A check that flagged them would be
#:   telling people not to use the safe form. Measured: 6 hits on this tree,
#:   every one a document explaining the rule.
#: - ⛔ **`/root/` is NOT flagged.** It is the same path on every machine and
#:   identifies nobody, whereas `/home/<x>` and `/Users/<x>` carry an account
#:   name in the very next segment. Measured: 0 hits, so including it would buy
#:   only the first false positive from a container path.
SHAPES = (
    (
        "home path",
        # The next segment after `/home` or `/Users` is an account name. The
        # lookbehind stops the same letters mid-path — `/var/lib/home/cache`
        # names nobody — from matching.
        #
        # ⭐ Note how the surrounding prose writes the shape: `/home/<name>`,
        # with angle brackets. That is not decoration. `<` is outside the
        # character class, so a placeholder written that way cannot match,
        # which is how a document about this rule stays swept AND clean. A
        # comment that spelled out a plausible account name instead would be a
        # finding against this very file — correctly.
        re.compile(r"(?<![\w.])/(?:home|Users)/[A-Za-z0-9._\-]+"),
    ),
    (
        "email address",
        # ⚠️ The local part must be at least TWO characters, and that is not
        # arbitrary. Measured on this tree, the only email-shaped text outside
        # the sanctioned fixture was `n@router.get` — prose in
        # `docs/tasks/E02-content-pipeline.md` and `review-rubric.md`
        # illustrating that `\n@router.get` is address-shaped. It appears both
        # escaped and bare, so no lookbehind for a backslash can reach both,
        # and the thing they have in common is a one-character local part.
        #
        # ⭐ Fixed in the pattern rather than by exempting the two documents,
        # deliberately: exempting a file stops sweeping it for real leaks, and
        # those two are prose about R7, which is exactly where a real home path
        # would be pasted by accident. The cost is that `a@b.example` would not
        # be caught; that is stated rather than hidden.
        re.compile(r"\b[A-Za-z0-9._%+\-]{2,}@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    ),
    (
        "local hostname",
        # A machine name. The trailing guard keeps `settings.local.json` — a
        # filename, not a host — out of it.
        re.compile(r"(?<![\w.])[A-Za-z0-9-]+\.local(?![\w.])"),
    ),
    (
        "bearer token",
        # A credential rather than an identity, and refused for the same
        # reason: it must not reach a tracked file. Shared with FND-04's
        # fixture sweep so the two agree on what R7 covers.
        re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{8,}"),
    ),
)

#: Addresses that are unreachable by construction, and therefore identify
#: nobody: RFC 2606's reserved TLDs, the `example.*` domains, `localhost`, and
#: the attribution trailer this project's commits carry. ⛔ Deliberately tiny.
#: An address at a real domain is a leak even if the author believes nobody
#: owns it.
ALLOWED_ADDRESS = re.compile(
    r"@(?:localhost|noreply\.[A-Za-z0-9.\-]+"
    r"|(?:[A-Za-z0-9.\-]+\.)?example\.(?:com|org|net)"
    r"|[A-Za-z0-9.\-]*\.(?:invalid|test|example|localhost)"
    r"|anthropic\.com)\b",
    re.IGNORECASE,
)

#: An identifier this short, or this generic, matches too much to be evidence
#: of anything. ⚠️ A machine whose account is called `root` or `ubuntu` would
#: otherwise make every mention of those words a finding, and a check that
#: fires on correct code is a check somebody turns off.


def article(noun: str) -> str:
    """Return `"a"` or `"an"`, so a finding reads as a sentence, not as output."""
    return "an" if noun[:1].lower() in "aeiou" else "a"


def shape_matches(text: str) -> list[tuple[int, str]]:
    """`(line number, shape name)` for every personal-data shape in `text`.

    ⛔ Returns the *name* of what matched and never the matched text. Every
    caller reports what it is handed, so the value has nowhere to escape to.
    """
    found: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for name, pattern in SHAPES:
            for match in pattern.finditer(line):
                if name == "email address" and ALLOWED_ADDRESS.search(match.group(0)):
                    continue
                found.append((number, name))
                break
    return found


def check_shapes(root: Path) -> list[Finding]:
    """Every personal-data shape in the tree, outside the registered directories."""
    findings: list[Finding] = []
    for path in config.text_files(root):
        relative = config.relative(path, root)
        if config.is_sanctioned_personal_data(relative):
            continue
        text = config.read_text(path)
        if text is None:
            continue
        for number, name in shape_matches(text):
            findings.append(
                Finding(
                    path=relative,
                    line=number,
                    rule=RULE_SHAPE,
                    message=(
                        f"carries {article(name)} {name} (R7). Replace it with a "
                        f"documented placeholder, or read the value from the "
                        f"environment at run time."
                    ),
                )
            )
    return findings
