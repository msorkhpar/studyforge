r"""Which of a build's own files a prime copies, module by module, so each one compiles.

**What it does.** Given one build's files, its modules and one declared
language, returns one `Specimen` per module that carries that language: the
module's smallest real source and smallest real test, each with every file of
the build it names (`closure`), so the module compiles on its own terms.

**How you use it.** `prime` calls `per_module(...)` for each declared language
of a build; `module_of(where, modules)` answers which module a file is in.

**Depends on.** `re` and `execute.conventions.is_a_test`. ⛔ Nothing
source-specific (R1): a name is found by the language's own keywords and a
file's own stem, never by a name a corpus chose.

## ⛔ THE SMALLEST SOURCE AND THE SMALLEST TEST DO NOT COMPILE TOGETHER BY LUCK

⚠️ **Measured on a 46-module Maven build:** the smallest source and the
smallest test across the whole build sat in two modules, and the test named a
class its own module held and the prime did not, so the build the prime handed
the component did not compile. ⭐ **So a specimen is chosen per module, and it
carries what it names**: every file of the build whose stem or declared type
the specimen's text mentions, and what those name in turn. A mention in a
comment copies one file too many, which compiles; a name missed copies one
too few, which does not — so the reading errs wide.

⭐ **A name resolves in the naming file's own module first**, because two
modules of one course may each teach a `Shape`. ⚠️ **Measured:** a name the
module does not hold, looked for across the whole build, found an unrelated
lesson's `Person` or `Color` for nearly every module and copied a third of the
build into each. ⭐ So a name reaches another module's file only when the
naming file ALSO names that file's directory — which is what an import of it
spells (`import ….base.PerformanceTestUtil`, `from base import …`). ⛔ A source
never resolves a name to a test: a test is not on a source's classpath.

## ⭐ A MODULE WITH NOTHING TO COMPILE IS PRIMED THROUGH ITS BUILD FILE

A module that carries no file in the language gets no specimen and is **not**
refused here: its build file is in the prime, and the build resolves what that
file declares whether or not it compiles anything. ⛔ Whether the BUILD as a
whole compiles something is `prime`'s question, asked once per build.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from studyforge.execute import is_a_test

#: A word, as the C-family languages and Python spell an identifier.
WORD = re.compile(r"[A-Za-z_$][\w$]*")

#: A type a file declares, by the keywords the JVM languages, C# and TypeScript
#: share. ⭐ So a second top-level type in a file is still found by its name.
DECLARED = re.compile(r"\b(?:class|interface|enum|record|object|trait)\s+([A-Za-z_$][\w$]*)")


@dataclass(frozen=True, slots=True)
class Specimen:
    """One module's real source and real test in one language, and what they name."""

    language: str
    #: The module's directory, corpus-relative; `""` when it is the corpus root.
    module: str = ""
    source: str | None = None
    test: str | None = None
    #: Every other file of the build the two name, sorted.
    support: tuple[str, ...] = ()

    def files(self) -> tuple[str, ...]:
        """Every file this specimen copies, sorted."""
        return tuple(sorted({*(one for one in (self.source, self.test) if one), *self.support}))


def module_of(where: str, modules: Sequence[str]) -> str:
    """Return the deepest module directory `where` sits under; `""` is the root."""
    inside = [one for one in modules if not one or where.startswith(f"{one}/")]
    return max(inside, key=len, default="")


def per_module(
    language: str,
    held: Sequence[tuple[str, int]],
    modules: Sequence[str],
    text: Callable[[str], str],
) -> tuple[Specimen, ...]:
    """One specimen per module that carries `language`'s files, in module order.

    `held` is `(path, size)` for every file of the build in the language, and
    `text(path)` its contents.
    """
    sizes = {where: size for where, size in held if size > 0}
    home = {where: module_of(where, modules) for where in sizes}
    names = _names(sizes, text)
    found = []
    for module in sorted(set(home.values())):
        mine = [where for where in sizes if home[where] == module]

        def reach(start: str) -> tuple[str, ...]:
            return closure(start, home, names, text)

        source = _smallest([one for one in mine if not is_a_test(one)], reach, sizes)
        test = _smallest([one for one in mine if is_a_test(one)], reach, sizes)
        picked = {one for one in (source, test) if one}
        support = {other for one in picked for other in reach(one)} - picked
        found.append(Specimen(language, module, source, test, tuple(sorted(support))))
    return tuple(found)


def closure(
    start: str,
    home: Mapping[str, str],
    names: Mapping[str, tuple[str, ...]],
    text: Callable[[str], str],
) -> tuple[str, ...]:
    """Every file `start` names, and what those name in turn, `start` included, sorted."""
    seen, queue = {start}, [start]
    while queue:
        where = queue.pop()
        testing = is_a_test(where)
        words = set(WORD.findall(text(where)))
        for word in words:
            held = [one for one in names.get(word, ()) if testing or not is_a_test(one)]
            near = [one for one in held if home[one] == home[where]]
            far = [one for one in held if _directory(one) in words]
            for one in near or far:
                if one not in seen:
                    seen.add(one)
                    queue.append(one)
    return tuple(sorted(seen))


def _directory(where: str) -> str:
    """Return the name of the directory a file sits in: its package, or its module's."""
    parts = where.split("/")
    return parts[-2] if len(parts) > 1 else ""


def _names(sizes: Mapping[str, int], text: Callable[[str], str]) -> dict[str, tuple[str, ...]]:
    """Map every name a file answers to — its stem and each type it declares — to its files."""
    found: dict[str, set[str]] = {}
    for where in sizes:
        stem = where.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        for name in {stem, *DECLARED.findall(text(where))}:
            found.setdefault(name, set()).add(where)
    return {name: tuple(sorted(files)) for name, files in found.items()}


def _smallest(
    candidates: Sequence[str],
    reach: Callable[[str], tuple[str, ...]],
    sizes: Mapping[str, int],
) -> str | None:
    """Return the candidate whose copy is smallest with all it names; ties by size, then path."""
    if not candidates:
        return None
    weighed = [
        (sum(sizes[one] for one in reach(where)), sizes[where], where) for where in candidates
    ]
    return min(weighed)[2]
