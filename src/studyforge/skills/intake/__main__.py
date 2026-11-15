"""`python3 -m studyforge.skills.intake check|render|questions`: the intake command line.

`check [BRIEF]` prints each open finding, then `open: N`, and exits 1 when N is above 0.
`render [BRIEF]` writes `brief.md` beside the brief. `questions [--track T]` lists the
questions a track asks, each with its kind, its choices and the gate it depends on. Every
failure prints one line to stderr and exits 2; messages never repeat what a brief contains.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from studyforge.validate.source import repository_ignores

from . import BANK, BRIEF_PATH, TRACKS, BriefError, Question, check, load, render

USAGE = ("usage: python3 -m studyforge.skills.intake check [BRIEF] | render [BRIEF] "
         "| questions [--track T]")


def _fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


#: A path inside `.private/`. Git judges a path inside the folder by the folder's rule whether
#: or not the folder exists yet; asked about the bare folder name, it would miss a `.private/`
#: rule while the folder is absent.
INSIDE_PRIVATE = Path(".private") / "intake-probe"


def _private_state(root: Path) -> tuple[bool, bool]:
    """Whether `.private/` is ignored, and whether it holds files git tracks anyway.

    Both questions go to the framework's one ignore reader in one call, so intake starts no
    process of its own. Git never reports a tracked file as ignored, so a file on disk under
    an ignored `.private/` that git does not report is one it tracks (or one a negated rule
    lets through): either way it reaches a commit. The reader's `None` (no git, or not a
    repository) is a refusal, never "not ignored"; an OSError carries a one-line reason.
    """
    probe = root / INSIDE_PRIVATE
    folder = root / ".private"
    files = sorted(p for p in folder.rglob("*") if p.is_file()) if folder.is_dir() else []
    ignored = repository_ignores(root, [probe, *files])
    if ignored is None:
        raise OSError("git cannot judge .private/ (is the brief inside a git repository?)")
    is_ignored = probe in ignored
    return is_ignored, is_ignored and any(path not in ignored for path in files)


def _check(path: Path) -> int:
    brief = load(path)
    ignored, tracked = _private_state(path.resolve().parent.parent)
    findings = check(brief, private_ignored=ignored, private_tracked=tracked)
    for line in findings:
        print(line)
    print(f"open: {len(findings)}")
    return 1 if findings else 0


def _render(path: Path) -> int:
    brief = load(path)
    target = path.parent / "brief.md"
    try:
        target.write_text(render(brief), encoding="utf-8", newline="\n")
    except OSError:
        raise OSError("brief.md: cannot write beside the brief") from None
    try:
        print(target.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        print(target)
    return 0


#: What a brief records for each kind of answer, as `questions` prints it.
KIND_NOTES = {
    "text": "text",
    "boolean": "boolean, recorded as JSON true or false",
    "choice": "choice, recorded as exactly one of: {}",
    "private_ref": "private_ref, recorded as env:NAME or private:FILE, optionally with #KEY",
}


def _token(value: object) -> str:
    """A gate value as a brief spells it: JSON `true`/`false` for a boolean."""
    return json.dumps(value) if isinstance(value, bool) else str(value)


def _kind(question: Question) -> str:
    return KIND_NOTES[question.kind].format(", ".join(question.choices))


def _questions(track: str | None) -> int:
    tracks = (track,) if track else TRACKS
    for name in tracks:
        if track is None:
            print(f"== {name} ==")
        for question in BANK:
            if name in question.tracks:
                print(f"{question.id} [{question.tier}] {question.ask}")
                print(f"  why: {question.why}")
                print(f"  default: {question.default}")
                print(f"  kind: {_kind(question)}")
                if question.depends_on is not None:
                    gate, values = question.depends_on
                    print(f"  depends on {gate} = {', '.join(map(_token, values))}")
    return 0


def main(argv: list[str]) -> int:
    """Run one verb; return the process exit status."""
    verb, rest = (argv[0], argv[1:]) if argv else ("", [])
    try:
        if verb in ("check", "render") and len(rest) <= 1:
            path = Path(rest[0] if rest else BRIEF_PATH)
            return _check(path) if verb == "check" else _render(path)
        if verb == "questions" and rest == []:
            return _questions(None)
        if verb == "questions" and len(rest) == 2 and rest[0] == "--track":
            return _questions(rest[1]) if rest[1] in TRACKS else _fail(USAGE)
    except (BriefError, OSError) as err:
        return _fail(str(err))
    return _fail(USAGE)


if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    sys.exit(main(sys.argv[1:]))
