r"""The prime — one project per seeded build tool, out of the corpus's own build.

**What it does.** Finds, for each build tool the component seeds and the
corpus declares, the corpus's **own** build — its shallowest build file's
directory and every build file under it — and, in each of that build's modules,
the smallest **real** source and test with every file of the build they name
(`specimens`), so an image can be warmed with a project that actually
compiles: a multi-module build is primed as the build it is.

**How you use it.** `prime_for(root, runtimes, seeded=…)` returns a `Prime`;
`Prime.copies()` is every `(path in the prime, corpus-relative path)` pair a
generator copies.

**Depends on.** `pathlib`, `describe`, the exercise layout's two directory
names, `specimens` for what each module copies and which file is a test, and
`execute.conventions` for every build file, source suffix and skipped
directory it selects by. ⛔ It reads the corpus and writes
nothing, and it names no source (R1): every filename it selects by belongs to a
*build tool*, a *language* or the *framework's own exercise layout*, never to
any corpus.

## ⛔ THE PRIME IS THE COMPONENT'S LAYOUT, AND ITS NAMES ARE THE CONTRACT'S

⚠️ **Measured:** a prime holding the corpus's files at their
corpus-relative paths is REFUSED by the runner's build (exit 2), because the
component warms **one project directory per seeded tool** and nothing else at
the top. ⭐ **So each project is copied to `<tool>/…`, re-rooted at its own
build's directory**, and `<tool>` is a key of the contract's own
`runner.prime.seeds` map, which arrives here as `seeded`. ⛔ No tool name is
chosen here for the directory: a runtime the contract does not seed gets no
directory, and a seed key the contract renames renames the directory.

⭐ **Re-rooting keeps what a JVM build needs**: a specimen's path *below* its
build's directory is preserved, so a package directory still sits where the
build file expects it.

## ⛔ THE PRIME IS THE CORPUS'S OWN BUILD, NEVER THE SUM OF ITS EXERCISES'

⚠️ **An authored exercise carries a build role**: a `pom.xml` in its
bundle, and a copy of it laid into the reader's workspace. ⛔ **Neither is the
corpus's declared build**, and matching build files at any depth would sweep
every one into the prime. ⭐ So the bundle directory is never read from, and
neither is any workspace a bundle on disk owns — both named by the exercise
layout's own constants, never by a corpus.

## ⛔ AN EMPTY PRIME PRIMES NOTHING WHILE APPEARING TO SUCCEED

⚠️ **The failure this module exists to prevent, spelled out because it is
silent:** a `NO-SOURCE` compile task never resolves the compiler classpath. An
image warmed with an empty prime builds, tags, and reports success — and then a
reader's first offline build downloads the world, or fails with no network at
all. Nothing says anything is wrong until then.

⭐ **So a seeded tool with no build file, or a build with no source or no test
in it, is REFUSED by name.** That refusal is the step's whole point. ⭐ It is
asked of the BUILD: a module of a multi-module build that carries nothing to
compile is primed through its build file, which the component's warmer
resolves whether or not the module compiles anything, and is never refused. ⚠️ A
corpus that declares no seeded tool gets an EMPTY prime and no refusal: the
component warms nothing for it, so there is nothing to prime.

## ⛔ NOTHING HERE IS AUTHORED, AND THAT IS R19 AND §8.1 AGREEING

⛔ **This module writes no build file, no dependency version and no test
framework.** §8.1 says the prime *copies the consuming repository's wrapper and
build files*; the corpus's own material is what supplies them, and its own
tests already use its own framework at its own version.

⚠️ **A version typed here is a version that disagrees with the corpus the day
the corpus moves**, and §8.1's own version guard would then fail a build over a
disagreement this skill created. ⭐ Selecting is the only honest operation: the
smallest real file the corpus already has cannot be wrong about the corpus.

## ⭐ WHICH RUNTIMES OWE A BUILD FILE IS THE CONTRACT'S ANSWER, NOT THIS MODULE'S

⚠️ `seeded` arrives from the component's own prime block, which maps a runtime
to the cache volume that runtime is seeded into. ⛔ **A runtime the contract
seeds and the corpus cannot build is refused; one it does not seed is not**, so
a corpus of plain scripts is never asked for a build file it has no reason to
own — and gets no project in the prime either.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.corpus.manifest import SOURCE_SUFFIXES
from studyforge.corpus.placement import PRACTICE_DIRNAME
from studyforge.describe import describe
from studyforge.execute import BUILD_FILES, SKIPPED
from studyforge.exercise.bundle import BUNDLE_FILENAME, BUNDLES_DIRNAME
from studyforge.skills.execution.specimens import Specimen, per_module


class PrimeRefused(ValueError):
    """A prime that would prime nothing, and exactly what is missing from it."""


@dataclass(frozen=True, slots=True)
class Project:
    """One seeded tool's project: the corpus's own build, and what it compiles."""

    #: The seed key, which is also the project's directory in the prime.
    tool: str
    #: The build's directory, corpus-relative; `""` when it is the corpus root.
    root: str
    build_files: tuple[str, ...]
    specimens: tuple[Specimen, ...]

    def copies(self) -> tuple[tuple[str, str], ...]:
        """`(path in the prime, corpus-relative path)` for every file, sorted.

        ⭐ Re-rooted at the build's directory and nothing more, because a
        package directory is part of a JVM source's identity and a specimen
        moved out of its package no longer compiles.
        """
        found = {*self.build_files}
        for specimen in self.specimens:
            found.update(specimen.files())
        cut = len(self.root) + 1 if self.root else 0
        return tuple(sorted((f"{self.tool}/{origin[cut:]}", origin) for origin in found))


@dataclass(frozen=True, slots=True)
class Prime:
    """Everything a warmed build needs: one project per seeded tool, or none."""

    projects: tuple[Project, ...]

    @property
    def build_files(self) -> tuple[str, ...]:
        """Every build file the prime carries, corpus-relative and sorted."""
        return tuple(sorted(one for project in self.projects for one in project.build_files))

    @property
    def specimens(self) -> tuple[Specimen, ...]:
        """Every project's specimens, in project order."""
        return tuple(one for project in self.projects for one in project.specimens)

    def copies(self) -> tuple[tuple[str, str], ...]:
        """`(path in the prime, corpus-relative path)` for every file, sorted."""
        return tuple(sorted(pair for project in self.projects for pair in project.copies()))

    def document(self) -> dict[str, object]:
        """Return the prime as data, for the selection document a corpus keeps."""
        return {
            "projects": [
                {
                    "tool": project.tool,
                    "root": project.root,
                    "build_files": list(project.build_files),
                    "specimens": [
                        {
                            "language": one.language,
                            "module": one.module,
                            "source": one.source,
                            "test": one.test,
                            "support": list(one.support),
                        }
                        for one in project.specimens
                    ],
                }
                for project in self.projects
            ]
        }


def prime_for(root: Path, runtimes: Sequence[str], *, seeded: Sequence[str] = ()) -> Prime:
    """Select a prime for `runtimes` out of the corpus at `root`, or refuse."""
    if not isinstance(root, Path):
        raise PrimeRefused(f"the corpus root must be a path, got {describe(root)}")
    declared = tuple(sorted({name for name in runtimes if isinstance(name, str)}))
    held = _files(root)
    text = _reader(root)
    missing: list[str] = []
    found = [_project(tool, declared, held, text, missing) for tool in declared if tool in seeded]
    if missing:
        raise PrimeRefused(
            "this corpus cannot be primed for what it declared, and an empty prime "
            "primes nothing while appearing to succeed (§8.1): " + "; ".join(missing)
        )
    return Prime(projects=tuple(one for one in found if one is not None))


def stale_in(root: Path, directory: str, kept: set[str]) -> tuple[str, ...]:
    """Every entry under `directory` a write removes, corpus-relative and sorted.

    ⛔ **A prime is regenerated whole.** A file an earlier selection copied and
    this one does not would still be handed to the build, which would compile
    what nobody selected, so onboarding's write removes each one this names.
    ⛔ **A link is never followed**: a linked directory is not descended into,
    and a link — to a file or a directory, kept or not — is named as itself, so
    removing it removes the link and never what it points at. The skill writes
    only files here, so any link is stale.
    """
    top = root / directory
    if top.is_symlink() or not top.is_dir():
        return ()
    found, queue = [], [top]
    while queue:
        for path in queue.pop().iterdir():
            if path.is_dir() and not path.is_symlink():
                queue.append(path)
                continue
            where = path.relative_to(root).as_posix()
            if path.is_symlink() or where not in kept:
                found.append(where)
    return tuple(sorted(found))


def linked(root: Path, directory: str) -> str | None:
    """Why `directory` is not a plain directory of the corpus's own bookkeeping, or `None`.

    ⛔ **A write prunes the prime, so the prime must be where it says it is.** A
    link at the prime or at any directory above it (below the corpus root) would
    turn a removal into the removal of the author's own files, so it is refused
    before anything is touched, as is a path that resolves outside its first
    directory.
    """
    here = root
    for part in PurePosixPath(directory).parts:
        here = here / part
        if here.is_symlink():
            where = here.relative_to(root).as_posix()
            return (
                f"{where} is a symbolic link, and this skill writes and prunes its prime "
                "only inside the corpus's own bookkeeping; replace the link with a directory"
            )
    first = PurePosixPath(directory).parts[0]
    if not (root / directory).resolve().is_relative_to((root / first).resolve()):
        return f"{directory} resolves outside {first}, so it is not written"
    return None


def _files(root: Path) -> tuple[tuple[str, int], ...]:
    """Every file under `root` worth selecting from, as `(relative path, size)`.

    ⛔ Never an exercise's: not its bundle, and not a workspace a bundle owns.
    """
    found = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if any(part in SKIPPED for part in relative.split("/")):
            continue
        if path.is_file() and not path.is_symlink():
            found.append((relative, path.stat().st_size))
    exercised = _exercise_material(where for where, _ in found)
    return tuple(one for one in found if not one[0].startswith(exercised))


def _exercise_material(held) -> tuple[str, ...]:
    """Return the prefixes exercise material occupies: the bundles, and their workspaces.

    ⭐ A workspace is found from its bundle, because the two roots share one
    tail (`exercise.bundle.Places`): `<bundles>/<tail>` and `<practice>/<tail>`.
    """
    prefixes = [f"{BUNDLES_DIRNAME}/"]
    for where in held:
        parts = where.split("/")
        if parts[0] == BUNDLES_DIRNAME and parts[-1] == BUNDLE_FILENAME and len(parts) > 2:
            prefixes.append("/".join([PRACTICE_DIRNAME, *parts[1:-1]]) + "/")
    return tuple(prefixes)


def _project(
    tool: str,
    declared: Sequence[str],
    held: Sequence[tuple[str, int]],
    text: Callable[[str], str],
    missing: list[str],
) -> Project | None:
    """One seeded tool's project out of the corpus's own build, or a reason why not.

    ⚠️ **Rooted at the SHALLOWEST directory holding one of the tool's build
    files**, and every build file under it is kept, because a multi-module
    project keeps its build files beside each module. ⛔ Two builds at the same
    shallowest depth are two projects, and the component warms one per tool,
    so that is refused by name rather than one picked.
    """
    names = [where for where, _ in held]
    wanted = [where for where in names if _is_build_file(where, tool)]
    if not wanted:
        missing.append(
            f"{tool} is declared and its cache is seeded from a build, and this "
            f"corpus carries none of that tool's build files"
        )
        return None
    roots = {_directory_of(where, tool) for where in wanted}
    depth = min(_depth(one) for one in roots)
    shallowest = sorted(one for one in roots if _depth(one) == depth)
    if len(shallowest) > 1:
        missing.append(
            f"{tool} is declared and this corpus carries {len(shallowest)} separate builds "
            f"at the same depth ({', '.join(one or '.' for one in shallowest)}), and the "
            f"component warms one project per tool; keep one build and make the rest its "
            f"modules"
        )
        return None
    base = shallowest[0]
    inside = [(where, size) for where, size in held if _under(where, base)]
    modules = sorted(one for one in roots if one == base or _under(one, base))
    return Project(
        tool=tool,
        root=base,
        build_files=tuple(sorted(where for where in wanted if _under(where, base))),
        specimens=_specimens(tool, base, declared, inside, modules, text, missing),
    )


def _is_build_file(where: str, tool: str) -> bool:
    """Whether `where` is one of `tool`'s own build files, at any depth."""
    return any(where == one or where.endswith(f"/{one}") for one in BUILD_FILES.get(tool, ()))


def _directory_of(where: str, tool: str) -> str:
    """Return the build directory a build file belongs to: its path less the tool's name."""
    for one in BUILD_FILES.get(tool, ()):
        if where == one:
            return ""
        if where.endswith(f"/{one}"):
            return where[: -len(one) - 1]
    return where.rsplit("/", 1)[0] if "/" in where else ""


def _depth(directory: str) -> int:
    return len(directory.split("/")) if directory else 0


def _under(where: str, base: str) -> bool:
    return not base or where.startswith(f"{base}/")


def _specimens(
    tool: str,
    base: str,
    declared: Sequence[str],
    held: Sequence[tuple[str, int]],
    modules: Sequence[str],
    text: Callable[[str], str],
    missing: list[str],
) -> tuple[Specimen, ...]:
    """Each module's real source and real test per declared language, with what they name.

    ⭐ **Chosen module by module** (`specimens`), so a multi-module build
    compiles as the build it is, and a module with nothing in the language is
    primed through its build file alone. ⚠️ A declared language with no file
    in this build is not this build's language and is passed over; one with a
    source and no test anywhere in the build, or a test and no source, is
    refused; and a build with no source and no test at all is refused, because
    it would compile nothing.
    """
    found, before = [], len(missing)
    languages = [runtime for runtime in declared if SOURCE_SUFFIXES.get(runtime)]
    where = f"the {tool} build at {base or '.'}"
    for runtime in languages:
        suffixes = SOURCE_SUFFIXES[runtime]
        candidates = [(one, size) for one, size in held if one.endswith(suffixes) and size > 0]
        chosen = per_module(runtime, candidates, modules, text)
        sources = any(one.source for one in chosen)
        tests = any(one.test for one in chosen)
        if sources and tests:
            found.extend(chosen)
        elif sources:
            missing.append(f"{runtime} is declared and {where} carries no test for it")
        elif tests:
            missing.append(f"{runtime} is declared and {where} carries no source for it")
    if not found and len(missing) == before:
        missing.append(
            f"{where} carries no source and no test in any declared language "
            f"({', '.join(languages) or 'none declared'}), so it would compile nothing"
        )
    return tuple(found)


def _reader(root: Path) -> Callable[[str], str]:
    """Return a reader of a corpus-relative file's text, each file read once."""
    cache: dict[str, str] = {}

    def text(where: str) -> str:
        if where not in cache:
            cache[where] = (root / where).read_text(encoding="utf-8", errors="replace")
        return cache[where]

    return text
