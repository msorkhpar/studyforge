r"""Which of a course's tracked paths its learner `main` keeps, and which move to the build branch.

**What it does.** Reads a course checkout's tracked files and gives every
top-level entry, every entry of `.studyforge/` and every entry of
`.studyforge/execution/` one verdict, `KEEP` or `MOVE`, with the sentence that
decides it. `kept(root)` is every tracked file under a `KEEP`.

**How you use it.**

    verdicts = classify(root)            # (Verdict(path, verdict, why), ...)
    files = kept(root, verdicts)         # tracked files the learner's main carries

**Depends on.** `generate` for the course's declarations and the built site's
footprint, `corpus.placement` for the framework's own directory names,
`corpus.manifest` for the content policy, and `git`, asked for the tracked
files. ⛔ It writes nothing and moves nothing: a verdict is a proposal the
procedure in `SKILL.md` carries out, on `main` only.

## ⛔ The question, and the default

⭐ **Is it used to work with the course, or is it about building it?** Kept:
the course's declaration, the built site, the archive the server reads, the
practices AND the authored exercises they come from (the engine and its
exercises belong together), the course's own code and lessons, its own scripts,
progress tracker and toolchain configuration, its licence, the narration record
and restore scripts, and what the course's images are built from. ⛔ **What moves
is what is about building the course with studyforge**: ingestion, the build's
documentation, the generated conversion tests, an assistant's guidance files and
the build's own records. **A path nothing here recognises moves too**, with a
sentence saying so, because a path moved by mistake is one checkout of
`studyforge/build` away; what a learner or the engine could use is named here,
so it is never left to that default.

## ⭐ What an example's Run needs is KEPT, and why

⚠️ An example tab may name `code`, and an example block may declare `support` (a folder its code
imports, such as a shared harness). The top-level entry holding any such path is kept, whole,
because the served page's Run copies the learner tree and finds nothing of an entry that moved.
The entries are read from the archive's lesson documents (`generate.exampleruns.needed`).

## ⭐ The authored exercises are KEPT, and why

⚠️ The bundle root (`exercises/`) holds every statement, starter, test, reference
solution and plant. It was moved once because the study server never reads it;
that reading was too narrow. The exercises are what the course's practices are
graded against, and the course's engine and its exercises are one thing: a
learner who studies the course has the exercises beside it. ⛔ Keeping the tree
is a `main` decision only: the site, runner and editor images leave it out of
their build contexts (`images.DOCKERIGNORE`), so it never swells an image.

## ⚠️ The archive is KEPT, and why

⚠️ The archive is ingestion's output, and it would move if nothing read it.
⛔ **The study server reads it**: `generate.read_corpus` takes each unit's
material from it, and `serve.published.allowed_runs` takes every practice's Run
and Submit command from its documents. A learner `main` without it serves pages
whose practices can never run.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.corpus.manifest import MANIFEST_FILENAME
from studyforge.corpus.manifest.content.policy import Classification
from studyforge.corpus.placement import ARCHIVE_DIRNAME, GENERATED_ROOT, PRACTICE_DIRNAME
from studyforge.exercise.bundle.layout import BUNDLES_DIRNAME
from studyforge.generate import read_corpus
from studyforge.generate.exampleruns import needed as example_files

KEEP = "keep"
MOVE = "move"

#: ⛔ The one process this package needs, handed in by its caller (§8.3): `run(argv, cwd)`
#: runs one argv and answers `(exit code, stdout)`, exactly as the execution skill's
#: `record` asks for the component's tags. Nothing in this package imports a way to start one.
Run = Callable[[Sequence[str], Path], tuple[int, str]]

#: `.studyforge/execution/`, the one directory whose entries are judged one by one.
EXECUTION = f"{GENERATED_ROOT}/execution"

#: The execution skill's prime, whose top-level entries name the course's own code.
PRIME = f"{EXECUTION}/prime"

#: What a licence file is called, lower-cased and without an extension.
LICENCES = ("license", "licence", "copying", "notice")

#: ⭐ Entries of `.studyforge/` a learner needs, and why.
GENERATED_KEPT = {
    "assets": "the built pages' stylesheet and script",
    "narration.json": "the narration record: which clip each page plays",
    "narration-release": "the narration restore scripts and the checksums of every clip",
    ".gitignore": "ignores the regenerated discovery cache and the restored clips",
}

#: ⭐ Entries of `.studyforge/execution/` a learner needs, and why.
EXECUTION_KEPT = {
    "runservice.pl": "the runner's run service, baked into the course's runner image",
    "prime": "the course's build files the runner and editor images are warmed from",
    "code": "where the server copies the course's code for the editor; only its ignore file",
    "allowed": "where the server writes the runner's allowlist; only its ignore file",
    "liverun.pl": "the live runner's script, baked into the course's runner image",
    "egress.py": "the live runs' egress proxy, started from the course's site image",
}

#: ⭐ Top-level entries used to work with the course, kept by name (or by stem, lower-cased):
#: the course's own scripts, its progress trackers, and the configuration that selects its
#: toolchain.
WORKING_KEPT = {
    "scripts": "the course's own scripts, used to work with the project",
    "progress": "the course's own progress tracker",
    ".sdkman": "the course's own toolchain configuration",
    ".tool-versions": "the course's own toolchain configuration",
    ".java-version": "the course's own toolchain configuration",
    ".python-version": "the course's own toolchain configuration",
    ".nvmrc": "the course's own toolchain configuration",
    ".mvn": "the course's own build tool configuration",
}

#: Why paths the builder recognises move, by name.
KNOWN_MOVES = {
    "ingest": "the adapter that produced the archive: ingestion",
    "tests": "the checks onboarding generated to hold the build: how the course was built",
    "docs": "documents about the build: hand-offs and the onboarding report",
    "CLAUDE.md": "guidance for an AI assistant maintaining the repository",
    ".claude": "an AI assistant's command files for maintaining the repository",
    "AGENTS.md": "guidance for an AI assistant maintaining the repository",
    "EXECUTION.md": "the execution report onboarding wrote: how the course was built",
    "README.md": "the author's overview and the curriculum record ingestion read; the "
    "learner README replaces it, and the built site carries the contents",
    "pin.json": "the framework pin: which studyforge built the course",
    "installed.json": "onboarding's record of what it installed",
    "skills": "the skill stubs the build ran",
    "compose.yaml": "the builder's compose file; the learner's root compose.yaml replaces it",
    "written.json": "the execution skill's record of what it wrote",
    "toolchain.json": "the builder's toolchain selection; the learner's images are vendored",
    "site": "the builder's site image context; the learner's is vendored",
}

#: The sentence for a path nothing here recognises.
UNKNOWN = "not needed to study or run the course; when in doubt a path moves"


@dataclass(frozen=True, slots=True)
class Verdict:
    """One tracked entry, what the learner `main` does with it, and why."""

    path: str
    verdict: str
    why: str


#: ⭐ `.github` is the learner repository's hosting infrastructure, not build material: its
#: workflows and helpers run on GitHub for the learner's copy (the Pages workflow that
#: deploys the read-only preview and the builder it runs), so it is kept, and the export
#: writes it into the tree even when the course tracks none.
HOSTING = ".github"
HOSTED = Verdict(
    HOSTING,
    KEEP,
    "learner-facing hosting infrastructure: the workflow that deploys the read-only preview "
    "to GitHub Pages and the builder it runs, not material about building the course",
)


def tracked(root: Path, run: Run) -> tuple[str, ...]:
    """Every file git tracks in the checkout at `root`, as a forward-slash path.

    ⛔ A directory that is not a git checkout is refused as a `ValueError`: the
    split is of what the course tracks, and it tracks nothing there.
    """
    code, listed = run(["git", "-C", str(root), "ls-files", "-z"], Path(root))
    if code != 0:
        raise ValueError("the course is not a git checkout, so nothing it tracks can be split")
    return tuple(sorted(one for one in listed.split("\0") if one))


def classify(root: Path, files: Sequence[str]) -> tuple[Verdict, ...]:
    """One verdict per top-level entry, per `.studyforge/` entry and per execution entry."""
    root = Path(root)
    files = tuple(files)
    corpus = read_corpus(root)
    built = _built(corpus.footprint.files, corpus.footprint.directories)
    code = _code(files)
    lessons = _lessons(corpus.manifest, files)
    examples = frozenset(PurePosixPath(one).parts[0] for one in example_files(corpus))
    verdicts: list[Verdict] = []
    for entry in _entries(files, ()):
        if entry == GENERATED_ROOT:
            verdicts.extend(_generated(files, built))
        else:
            verdicts.append(_top(entry, built, code, lessons, examples))
    return tuple(verdicts)


def kept(verdicts: Iterable[Verdict], files: Sequence[str]) -> tuple[str, ...]:
    """Every tracked file beneath a `KEEP` verdict."""
    keeps = [one.path for one in verdicts if one.verdict == KEEP]
    return tuple(
        one for one in files if any(one == path or one.startswith(path + "/") for path in keeps)
    )


def table(verdicts: Iterable[Verdict]) -> str:
    """Return the KEEP/MOVE table, one verdict a line: what the split moves, and why."""
    return "".join(f"{one.verdict.upper():4}  {one.path}  {one.why}\n" for one in verdicts)


def _top(
    entry: str,
    built: frozenset[str],
    code: frozenset[str],
    lessons: frozenset[str],
    examples: frozenset[str] = frozenset(),
) -> Verdict:
    """Return the verdict for one top-level entry of the course."""
    if entry == MANIFEST_FILENAME:
        return Verdict(
            entry, KEEP, "the course's declaration: the server reads it to serve the course"
        )
    if entry == ARCHIVE_DIRNAME:
        return Verdict(
            entry,
            KEEP,
            "prepared material the server reads: each unit's documents, and every "
            "practice's Run and Submit command",
        )
    if entry == PRACTICE_DIRNAME:
        return Verdict(entry, KEEP, "the practice workspaces a learner edits and submits")
    if entry == BUNDLES_DIRNAME:
        return Verdict(
            entry,
            KEEP,
            "the authored exercises the practices are graded against: statements, starters, "
            "tests, reference solutions and plants; the course's engine and its exercises "
            "belong together",
        )
    stem = PurePosixPath(entry).stem.lower()
    working = WORKING_KEPT.get(entry) or (WORKING_KEPT[stem] if stem == "progress" else None)
    if working:
        return Verdict(entry, KEEP, working)
    if entry in built:
        return Verdict(entry, KEEP, "the built site")
    if entry in code:
        return Verdict(
            entry, KEEP, "the course's code, which its lessons link and its practices build with"
        )
    if entry in lessons:
        return Verdict(entry, KEEP, "the course's own lessons")
    if entry in examples:
        return Verdict(
            entry,
            KEEP,
            "holds a file an example's Run strip names as its code, or a folder the example "
            "declares as support: the served page's Run needs it beside the lesson",
        )
    if PurePosixPath(entry).stem.lower() in LICENCES:
        return Verdict(entry, KEEP, "the course's licence")
    if entry == ".gitignore":
        return Verdict(entry, KEEP, "the course's own ignore rules")
    if entry == HOSTING:
        return HOSTED
    return Verdict(entry, MOVE, KNOWN_MOVES.get(entry, UNKNOWN))


def _generated(files: Sequence[str], built: frozenset[str]) -> list[Verdict]:
    """Return the verdicts for `.studyforge/`'s entries, and for `.studyforge/execution/`'s."""
    found: list[Verdict] = []
    for entry in _entries(files, (GENERATED_ROOT,)):
        name = PurePosixPath(entry).name
        if entry == EXECUTION:
            for inner in _entries(files, (GENERATED_ROOT, "execution")):
                leaf = PurePosixPath(inner).name
                if leaf in EXECUTION_KEPT:
                    found.append(Verdict(inner, KEEP, EXECUTION_KEPT[leaf]))
                else:
                    found.append(Verdict(inner, MOVE, KNOWN_MOVES.get(leaf, _env_or_unknown(leaf))))
        elif name in GENERATED_KEPT:
            found.append(Verdict(entry, KEEP, GENERATED_KEPT[name]))
        elif entry in built:
            found.append(Verdict(entry, KEEP, "the built pages"))
        else:
            found.append(Verdict(entry, MOVE, KNOWN_MOVES.get(name, UNKNOWN)))
    return found


def _env_or_unknown(leaf: str) -> str:
    """Why an execution entry moves: the builder's env files are said by name."""
    if leaf.endswith(".env"):
        return (
            "the builder's recorded tags and instance values; a learner's course.env replaces them"
        )
    return UNKNOWN


def _entries(files: Sequence[str], parent: tuple[str, ...]) -> list[str]:
    """Return the distinct entries one level below `parent`, as paths, in sorted order."""
    depth = len(parent)
    found: dict[str, None] = {}
    for one in files:
        parts = PurePosixPath(one).parts
        if len(parts) > depth and parts[:depth] == parent:
            found.setdefault("/".join(parts[: depth + 1]), None)
    return sorted(found)


def _built(files: Iterable[PurePosixPath], directories: Iterable[PurePosixPath]) -> frozenset[str]:
    """Return the entries the build writes: a root file, or a `.studyforge/` child."""
    found: set[str] = set()
    for path in (*files, *directories):
        parts = PurePosixPath(path).parts
        if parts and parts[0] == GENERATED_ROOT and len(parts) > 1:
            found.add(f"{GENERATED_ROOT}/{parts[1]}")
        elif parts:
            found.add(parts[0])
    return frozenset(found)


def _code(files: Sequence[str]) -> frozenset[str]:
    """Return the top-level entries the execution prime mirrors: the course's own code."""
    prime = PurePosixPath(PRIME).parts
    found = set()
    for one in files:
        parts = PurePosixPath(one).parts
        if parts[: len(prime)] == prime and len(parts) > len(prime) + 1:
            found.add(parts[len(prime) + 1])
    # ⭐ A build that does not sit at the course root is re-rooted in the prime, so its
    # entries are not the course's top-level names. ⭐ The top-level entry that holds the
    # same file below a directory of its own is the course's code too.
    inside = {
        "/".join(PurePosixPath(one).parts[len(prime) + 1 :])
        for one in files
        if PurePosixPath(one).parts[: len(prime)] == prime
    }
    for one in files:
        parts = PurePosixPath(one).parts
        if len(parts) < 3 or parts[0] == GENERATED_ROOT or parts[0] in KNOWN_MOVES:
            continue
        if any("/".join(parts[index:]) in inside for index in range(1, len(parts) - 1)):
            found.add(parts[0])
    return frozenset(found)


def _lessons(manifest, files: Sequence[str]) -> frozenset[str]:
    """Return the top-level entries holding a file the content policy includes."""
    return frozenset(
        PurePosixPath(one).parts[0]
        for one in files
        if not one.startswith(GENERATED_ROOT + "/")
        and manifest.content.classify(one) is Classification.INCLUDED
    )
