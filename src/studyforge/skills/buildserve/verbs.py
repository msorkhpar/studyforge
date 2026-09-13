"""The skill's one seam onto the verbs: every argument list it hands a verb, and the one call.

**What it does.** Spells, once, the arguments this skill passes to `validate`,
`narrate`, `build` and `serve`, and makes the one call that hands a list to its
registered verb in `studyforge.cli.VERBS`.

**How you use it.**

    code = call(build(corpus, site), out)
    code = call(serve(corpus, site, port), out, started=on_listening)

**Depends on.** `studyforge.cli.VERBS`, and nothing else.

## ⛔ A changed verb is an edit HERE and nowhere else in this package

⚠️ `W230` may change `studyforge serve`'s arguments (`SF-19b/3`: `--site` is a
configured path, and `serve.make_instance(root)` needs none). ⭐ So no other module
in this package spells a verb flag or reaches the table, and
`tests/studyforge/skills/buildserve/test_thin.py` asserts both. The mirror test
parses every list below with that verb's own parser, reached through the table,
so a verb whose interface moves goes RED here rather than in a reader's shell.
"""

from __future__ import annotations

from collections.abc import Sequence

from studyforge.cli import VERBS


class NotAVerb(ValueError):
    """An argument list whose first word is no registered verb. ⛔ It never echoes the word."""


def validate(corpus: str) -> list[str]:
    """The arguments that validate one corpus."""
    return ["validate", corpus]


def narrate(corpus: str, voice: str, service: str | None = None) -> list[str]:
    """The arguments that narrate one corpus in `voice`, from `service` when one is named."""
    asked = ["narrate", corpus, "--voice", voice]
    return asked + ([] if service is None else ["--service", service])


def build(corpus: str, site: str) -> list[str]:
    """The arguments that build one corpus into `site`."""
    return ["build", corpus, "--out", site]


def serve(corpus: str, site: str, port: int | None = None) -> list[str]:
    """The arguments that serve the site `build` wrote, on `port` when one is named."""
    return ["serve", corpus, "--site", site] + ([] if port is None else ["--port", str(port)])


def call(argv: Sequence[str], out=None, **hooks: object) -> int:
    """Hand one argument list to its registered verb and return the exit code.

    ⛔ The only call into `VERBS` in this package. `hooks` are the verb's own
    keyword-only arguments — `serve`'s `started=` — passed through unchanged.
    """
    verb = VERBS.get(argv[0]) if argv else None
    if verb is None:
        raise NotAVerb("the argument list does not begin with a registered verb")
    return verb.run(list(argv[1:]), out=out, **hooks)
