r"""The runtimes the material evidences — the draft's `runtimes` key.

**What it does.** Reads the build files and source files `capability` found and
proposes the runtimes a runner must carry for them, beside `exercises`, with the
evidence for each. ⛔ **A runtime nothing in the material evidences is never
proposed**, and prose material gets no key at all.

**How you use it.** `propose(capability)` returns a `Runtimes`: `names` is what
the draft declares (empty means *no key*), `api` the `corpus_api` that
declaring them needs, and `questions()` what a person is asked about them.

**Depends on.** `capability` for the evidence, `report`, and
`studyforge.corpus.manifest` for the vocabulary **and nothing else from it**.
⛔ **The vocabulary is spelled once, by the manifest reader, and imported here** — a second
spelling in a skill is the copy that stops agreeing. ⚠️ This is not the reader:
the draft is still a proposal a person edits (`proposal`'s docstring).

## ⛔ Enumerate the evidence, never guess

`BUILD_EVIDENCE` and `SOURCE_EVIDENCE` are **closed maps**, the rule
`capability`'s `BUILD_FILES` keeps: a build file or suffix they do not name
evidences nothing, and a build this skill recognises but no runtime in the
vocabulary names is **asked about by name** rather than mapped to a near miss.
⭐ The cost of the closed map is one question, and the question is how it grows.

## ⛔ A source file a build holds evidences only what that build builds

⚠️ **Measured, and the reason this rule exists.** A course built by Maven kept
a Python file among its conversion notes and a shell script among the author's
tools, and the draft proposed `python` and `shell` beside `java` and `maven`,
though no grader runs either. ⭐ So a source file inside a build's tree, under
the nearest directory holding a build file this skill reads, evidences a
runtime only when that build builds it (`BUILDS`): a `.java` under a `pom.xml`
does, a `.py` under a `pom.xml` does not. ⚠️ Only a language some build builds
is judged so; a build says nothing about a database file or a shell script. ⛔ **Set aside, never dropped**: the
question beside the draft names every file set aside and why. A file no build
holds, in a corpus of loose scripts, evidences what it always did.

## ⭐ Only a graded corpus declares any (§7)

The manifest reader refuses `runtimes` beside `exercises: false`: a corpus that sets
no runnable unit needs no runner. ⛔ So a corpus whose material evidences a
runtime but ships no grader drafts **no key**, and says so in one question —
evidence is reported, never silently dropped, and never declared against the
reader's rule.

## ⚠️ The JVM rule is the owner's, applied rather than restated

A name in the manifest's `REQUIRES_JAVA` is refused without `java` beside it.
⭐ A build tool or language that runs on a JVM **evidences a JVM**, so `java` is
drafted with it — read from `REQUIRES_JAVA`, never listed here a second time.

## ⛔ `runtimes` is `corpus_api` 4's key

`RUNTIMES_API` is re-derived because the owner's key-to-version map is not on
`studyforge.corpus.manifest.__all__`, the shape onboarding's
`NOT_MATERIAL_API` took. ⛔ **Pinned behaviourally, never against a literal**:
the mirror parses a drafted manifest one version lower and asserts the refusal.
A draft carrying the key below it is refused on read-back.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import PurePosixPath

from studyforge.corpus.manifest import REQUIRES_JAVA, RUNTIMES
from studyforge.skills.reconnaissance.capability import Capability
from studyforge.skills.reconnaissance.report import Uncertainty

#: The `corpus_api` in which `runtimes` became legal. ⚠️ Re-derived; see above.
RUNTIMES_API = 4

#: What a build file evidences. ⛔ Closed; a name in `BUILD_FILES` absent here
#: evidences a build no runtime in the vocabulary names, and is asked about.
#: ⚠️ `build.gradle.kts` is the build's own script language, not the material's:
#: it evidences `gradle`, and Kotlin *source* is what evidences `kotlin`.
BUILD_EVIDENCE: dict[str, tuple[str, ...]] = {
    "pom.xml": ("maven",),
    "build.gradle": ("gradle",),
    "build.gradle.kts": ("gradle",),
    "settings.gradle": ("gradle",),
    "package.json": ("node",),
    "pyproject.toml": ("python",),
    "setup.py": ("python",),
}

#: What a source file's suffix evidences. ⛔ Closed. ⚠️ `.sql` is absent on
#: purpose: SQL names a language, and which engine runs it is not on the page —
#: the vocabulary's own note on why `sqlite` is spelled for the engine.
SOURCE_EVIDENCE: dict[str, tuple[str, ...]] = {
    ".java": ("java",),
    ".kt": ("kotlin",),
    ".py": ("python",),
    ".js": ("node",),
    ".mjs": ("node",),
    ".cjs": ("node",),
    ".sh": ("shell",),
    ".bash": ("shell",),
    ".sqlite": ("sqlite",),
    ".sqlite3": ("sqlite",),
}


#: What each runtime a build file evidences builds. ⛔ Closed, as the maps above
#: are: a source file under a build that builds none of its runtimes is set aside.
BUILDS: dict[str, tuple[str, ...]] = {
    "maven": ("java", "kotlin"),
    "gradle": ("java", "kotlin"),
    "python": ("python",),
    "node": ("node",),
}


#: Every runtime some build builds: the languages `BUILDS` judges.
BUILT = frozenset(name for names in BUILDS.values() for name in names)


@dataclass
class Runtimes:
    """What the material evidences, and what the draft declares from it."""

    #: Each evidenced runtime and the paths that evidence it.
    evidence: dict[str, list[str]] = field(default_factory=dict)
    #: Build files `capability` recognises that no runtime in the vocabulary names.
    unnamed_builds: list[str] = field(default_factory=list)
    #: Whether a grader ships with the material, so the key may be declared.
    graded: bool = False
    #: Source files a build holds that it does not build, and what each would evidence.
    set_aside: dict[str, list[str]] = field(default_factory=dict)

    @property
    def names(self) -> tuple[str, ...]:
        """The sorted runtimes the draft declares; empty means the key is absent."""
        return tuple(sorted(self.evidence)) if self.graded else ()

    @property
    def api(self) -> int:
        """The `corpus_api` that declaring `names` needs, or 1 when it declares none."""
        return RUNTIMES_API if self.names else 1

    def questions(self) -> Iterator[Uncertainty]:
        """Ask about what was drafted, and about evidence the draft could not declare."""
        cited = "; ".join(f"{name}: {where[:3]}" for name, where in sorted(self.evidence.items()))
        unnamed = (
            f"; recognised but named by no runtime in {list(RUNTIMES)}: {self.unnamed_builds[:3]}"
            if self.unnamed_builds
            else ""
        ) + (
            "; set aside, as the build that holds them builds no such source — "
            + "; ".join(f"{name}: {where}" for name, where in sorted(self.set_aside.items()))
            if self.set_aside
            else ""
        )
        if self.names:
            yield Uncertainty(
                question=f"are {list(self.names)} the runtimes this corpus's graders need?",
                why=f"drafted from what the material evidences — {cited}{unnamed}",
                settles_it=(
                    "remove a runtime the graders never run, and add one the material needs "
                    f"but this skill could not see; each is one of {list(RUNTIMES)}"
                ),
            )
        elif self.graded:
            yield Uncertainty(
                question="which runtimes do this corpus's graders need?",
                why=f"graders ship with the material, but nothing evidences a runtime{unnamed}",
                settles_it=f"declare 'runtimes' from {list(RUNTIMES)}, or none if nothing runs",
            )
        elif self.evidence or self.unnamed_builds:
            yield Uncertainty(
                question="the material evidences runtimes but no grader: is anything run?",
                why=(
                    f"no 'runtimes' is drafted, because the draft is 'exercises: false' and a "
                    f"corpus that sets no runnable unit declares none (§7) — {cited}{unnamed}"
                ),
                settles_it=(
                    "point at the graders and declare the runtimes beside 'exercises: true', "
                    "or confirm the code is illustrative and the corpus runs nothing"
                ),
            )


def propose(capability: Capability) -> Runtimes:
    """Return the runtimes `capability`'s files evidence, and whether they may be declared."""
    found = Runtimes(graded=capability.graded)
    builds: dict[PurePosixPath, set[str]] = {}
    for where in capability.build_files:
        name = PurePosixPath(where).name
        if name in BUILD_EVIDENCE:
            _cite(found, BUILD_EVIDENCE[name], where)
            built = builds.setdefault(PurePosixPath(where).parent, set())
            built.update(b for r in BUILD_EVIDENCE[name] for b in BUILDS.get(r, ()))
        else:
            found.unnamed_builds.append(where)
    for where in capability.source_files + capability.test_files:
        names = SOURCE_EVIDENCE.get(PurePosixPath(where).suffix.lower(), ())
        built = _holding(PurePosixPath(where), builds)
        # ⭐ Only a language some build builds is judged by the build holding it:
        # a build says nothing about a database file or a shell script.
        judged = [name for name in names if name in BUILT]
        if built is None or not judged or any(name in built for name in judged):
            _cite(found, names, where)
        else:
            for name in names:
                found.set_aside.setdefault(name, []).append(where)
    return found


def _holding(path: PurePosixPath, builds: dict[PurePosixPath, set[str]]) -> set[str] | None:
    """Return what the nearest build above `path` builds, or `None` when no build holds it."""
    for directory in path.parents:
        if directory in builds:
            return builds[directory]
    return None


def _cite(found: Runtimes, names: tuple[str, ...], where: str) -> None:
    """Record `where` as evidence for each of `names`, and a JVM for any that needs one."""
    jvm = ("java",) if any(name in REQUIRES_JAVA for name in names) else ()
    for name in names + jvm:
        found.evidence.setdefault(name, []).append(where)
