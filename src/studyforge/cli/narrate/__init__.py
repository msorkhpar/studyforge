"""The `narrate` verb: the CLI stage that puts a corpus's clips on disk.

**What it does.** Holds the argument parsing, the corpus walk, the report and
the exit code for `studyforge narrate`. Synthesis itself is `narrate.synth`'s
the client is `narrate.client`'s and the wire `narrate.wire`'s; this package is
their caller — ⛔ never a second author of any of them.

**How you use it.**

    studyforge narrate <corpus-root> --voice <voice>
    studyforge narrate <corpus-root> --prune
    python3 -m studyforge.cli.narrate <corpus-root> --voice <voice>

`main(argv) -> int` is the callable the dispatcher registers;
`narrate_corpus(root, client, voice=…, fmt=…)` is the stage with its client
handed in.

**Depends on.** `generate.declarations`, `unit.builder`, `narrate.speakable`,
`narrate.synth`, `narrate.answers`, `narrate.client`, `narrate.wire`, and
`validate` for the exit codes.
⛔ Nothing here knows any source (R1).

⭐ **Narration is recorded by `narrate` and a build only copies it, and that is
this package's reason to exist**: a build never
synthesises, so something a person can type must — and the order is `narrate`
then `build`. ⚠️ Clips land beside the material through `corpus.placement`,
never under a build's `--out`.
"""

from __future__ import annotations

from studyforge.cli.narrate.cli import DEFAULT_FORMAT, DEFAULT_SERVICE, build_parser, main
from studyforge.cli.narrate.disclosure import Walk, dead_entries
from studyforge.cli.narrate.prune import Pruned, prune_corpus
from studyforge.cli.narrate.report import (
    NO_SERVICE,
    exit_code,
    lines,
    prune_exit_code,
    prune_lines,
)
from studyforge.cli.narrate.stage import Narrated, narrate_corpus, survey

#: ⛔ The package's whole public surface.
__all__ = [
    "DEFAULT_FORMAT",
    "DEFAULT_SERVICE",
    "NO_SERVICE",
    "Narrated",
    "Pruned",
    "Walk",
    "build_parser",
    "dead_entries",
    "exit_code",
    "lines",
    "main",
    "narrate_corpus",
    "prune_corpus",
    "prune_exit_code",
    "prune_lines",
    "survey",
]
