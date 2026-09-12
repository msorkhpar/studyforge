"""The one installed command, and the table of verbs it dispatches to.

**What it does.** Reads the first argument as a verb, hands the rest to that
verb's own `cli.main`, and returns its exit code unchanged. It parses nothing
else: every flag a verb takes belongs to that verb's parser, so the dispatcher
cannot come to disagree with a stage about what an argument means.

**How you use it.** `main(argv) -> int`, which is what `[project.scripts]`
registers as `studyforge`, and `python3 -m studyforge.cli`. `VERBS` is the
registered table, read by the authoring checks rather than re-listed by them.

**Depends on.** each stage's `cli` module, and `argparse` for nothing but the
usage text. ⛔ No stage imports this one — the direction is one-way, so a stage
stays runnable as `python3 -m studyforge.<stage>` with the dispatcher absent.

## ⛔ A verb is registered here only when it can be RUN

⭐ `serve` and `reconcile` are named in this package's contract as commands the
framework will have; they are **not** in `VERBS`, because registering a verb
against a callable that does not exist yet makes an installed command that
fails on first invocation. ⚠️ That is the state `pyproject.toml` refused for
the whole command and the reasoning does not change one level down.

⛔ **The table is the population the authoring checks derive from.** A fenced
`studyforge <verb>` line in any document is checked against `VERBS`, reached
from `[project.scripts]`, so a document cannot offer a command this table does
not provide and a verb cannot be retired while a document still gives it.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from studyforge.cli.plan.cli import main as plan_main
from studyforge.cli.site.cli import main as build_main
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.cli import main as validate_main

#: The command a user types. ⛔ One name, and `pyproject.toml` registers this
#: same spelling — `tests/studyforge/cli/test_dispatch.py` asserts they agree,
#: because a usage line that names a command nobody installed is worse than no
#: usage line.
PROGRAM = "studyforge"


@dataclass(frozen=True)
class Verb:
    """One registered subcommand: what it is called, what it does, what runs it."""

    name: str
    summary: str
    run: Callable[..., int]


#: ⛔ **The registered table.** Ordered as a reader meets them: check the
#: archive, ask what a build would write, then write it.
VERBS: Mapping[str, Verb] = {
    verb.name: verb
    for verb in (
        Verb("validate", "decide whether a corpus's archive is valid", validate_main),
        Verb("plan", "say what a build would write, before it writes it", plan_main),
        Verb("build", "write the site for one corpus into a directory you name", build_main),
    )
}


def usage() -> list[str]:
    """Return the whole help text, one line at a time."""
    width = max(len(name) for name in VERBS)
    out = [
        f"usage: {PROGRAM} <verb> [options]",
        "",
        "Turn a body of teaching material into a local, offline study site.",
        "",
        "verbs:",
    ]
    out += [f"  {verb.name.ljust(width)}  {verb.summary}" for verb in VERBS.values()]
    out += [
        "",
        f"Run `{PROGRAM} <verb> --help` for the arguments one verb takes.",
    ]
    return out


def main(argv: list[str] | None = None, out=None) -> int:
    """Dispatch one verb and return its exit code, or say what the verbs are.

    ⛔ `2` for no verb and for an unknown one, which is `validate`'s `UNUSABLE`
    imported rather than respelled: the tool could not run, and that is not a
    verdict about anybody's corpus.
    """
    import sys

    stream = sys.stdout if out is None else out
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments or arguments[0] in ("-h", "--help", "help"):
        for line in usage():
            print(line, file=stream)
        return 0 if arguments else UNUSABLE
    verb = arguments[0]
    if verb not in VERBS:
        print(f"{verb}: not a studyforge verb", file=stream)
        for line in usage():
            print(line, file=stream)
        return UNUSABLE
    return VERBS[verb].run(arguments[1:], out=out)
