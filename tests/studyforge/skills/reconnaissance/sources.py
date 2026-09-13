"""Synthetic sources shaped like the material reconnaissance actually meets (SK-01).

⭐ **Every shape here reproduces a trap measured in a real repository**, at the
smallest size that still sets it. The measurements are recorded in
`docs/tasks/handoffs/SK-01.md`; these are the regression floor for them.

⛔ Synthetic on purpose. A fixture that depends on a sibling repository being
checked out is a fixture that skips, and a skipped check is not evidence.
"""

from __future__ import annotations

from pathlib import Path


def write(root: Path, files: dict[str, str]) -> Path:
    """Write one synthetic source tree and return its root."""
    for where, text in files.items():
        path = root / where
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def unit(title: str, body: str = "Prose.") -> str:
    """One unit file: a heading and a paragraph."""
    return f"# {title}\n\n{body}\n"


def flat_prose(root: Path) -> Path:
    """19 numbered files in one directory, listed by a README. No code anywhere.

    ⭐ SPARQL's shape, and two of the four designed shapes are this one.
    """
    files = {f"src/{n:02d}.md": unit(f"Lesson {n}") for n in range(1, 20)}
    listing = "\n".join(f"- [{n}. Lesson {n}](src/{n:02d}.md)" for n in range(1, 20))
    files["README.md"] = f"# A Prose Course\n\nWords about the course.\n\n{listing}\n"
    return write(root, files)


def prefixed_groups(root: Path) -> Path:
    """One flat directory, three groups by filename prefix, recorded in a README.

    ⭐ **Trap 1, at the smallest size that sets it.** The filesystem expresses
    no grouping; the README expresses it in the author's words, and the two
    partitions agree.
    """
    files = {}
    listing = []
    for prefix, name, count in (("", "Fundamentals", 4), ("s", "Server", 3), ("c", "Client", 3)):
        listing.append(f"\n# {name}\n")
        for n in range(1, count + 1):
            where = f"src/{prefix}{n}.md"
            files[where] = unit(f"{name} chapter {n}")
            listing.append(f"- [{n}. {name} chapter {n}]({where})")
    files["README.md"] = "".join(line + "\n" for line in listing)
    return write(root, files)


def nested_sections(root: Path) -> Path:
    """Modules in flat directories; sections recorded as **bare numbered lines**.

    ⭐ **Trap 4 from the other side**, and the Java corpus's real shape: there
    is not one heading in the curriculum region, so a heading-keyed parser
    proposes zero sections for a two-level corpus.
    """
    files: dict[str, str] = {}
    listing = ["# A Two Level Course", "", "## Curriculum", ""]
    modules = [("Basics", ["Variables", "Loops"]), ("Objects", ["Classes", "Records"])]
    section = 0
    for section_name, group in (("Foundations", modules[:1]), ("Design", modules[1:])):
        section += 1
        listing += [f"{section}. {section_name}", ""]
        for index, (module, units) in enumerate(group, 1):
            where = f"{section}{index}-{module.lower()}"
            files[f"{where}/README.md"] = unit(module)
            listing.append(f"- [{section}.{index}. {module}]({where}/README.md)")
            for order, name in enumerate(units, 1):
                target = f"{where}/README_{section}.{index}.{order}.md"
                files[target] = unit(name)
                listing.append(f"    - [{section}.{index}.{order}. {name}]({target})")
        listing.append("")
    files["README.md"] = "\n".join(listing) + "\n"
    return write(root, files)


def aggregated(root: Path) -> Path:
    """Per-unit files **and** a whole-series aggregate that concatenates them.

    ⭐ **Trap 2.** The aggregate is an exact ordered concatenation, so the
    detector can assert digest equality rather than similarity.
    """
    bodies = {f"src/{n}.md": unit(f"Chapter {n}", f"Body of chapter {n}.") for n in (1, 2, 3)}
    files = dict(bodies)
    files["src/Whole.md"] = "\n".join(bodies[f"src/{n}.md"] for n in (1, 2, 3))
    files["README.md"] = "# Aggregated\n\n" + "\n".join(
        f"- [{n}. Chapter {n}](src/{n}.md)" for n in (1, 2, 3)
    )
    return write(root, files)


def copied_heading_tree(root: Path) -> Path:
    """A curriculum whose second half reproduces another document's heading tree.

    ⭐ **Trap 4's sibling and the half a whole-file digest cannot see**: no file
    duplicates a file, and the curriculum document still cannot be excluded.
    """
    other = "# Test cases\n\n" + "\n".join(f"## Case {n}\n\nText.\n" for n in range(1, 16))
    files = {f"src/{n}.md": unit(f"Chapter {n}") for n in (1, 2, 3)}
    files["TestCases.md"] = other
    # ⚠️ The whole of `TestCases.md`'s heading tree, reproduced inside the one
    # document that also records the corpus — so no file duplicates a file and
    # the document still cannot be excluded.
    files["README.md"] = (
        "# Copied\n\n"
        + "\n".join(f"- [{n}. Chapter {n}](src/{n}.md)" for n in (1, 2, 3))
        + f"\n\n{other}"
    )
    return write(root, files)


def runnable(root: Path) -> Path:
    """A prose corpus that also ships a build and real tests."""
    files = {f"src/{n}.md": unit(f"Chapter {n}") for n in (1, 2)}
    files["README.md"] = "# Runnable\n\n" + "\n".join(
        f"- [{n}. Chapter {n}](src/{n}.md)" for n in (1, 2)
    )
    files["pom.xml"] = "<project/>\n"
    files["src/test/java/ThingTest.java"] = "class ThingTest {}\n"
    return write(root, files)


def unlisted(root: Path) -> Path:
    """A corpus whose README lists two of its three units."""
    files = {f"src/{n}.md": unit(f"Chapter {n}") for n in (1, 2, 3)}
    files["README.md"] = "# Partial\n\n" + "\n".join(
        f"- [{n}. Chapter {n}](src/{n}.md)" for n in (1, 2)
    )
    return write(root, files)


def marker_ordinals(root: Path) -> Path:
    """Entries whose ordinal **is** the list marker: `1. [Title](x)`, emphasised.

    ⭐ **The majority form, and it was the one the reader missed.** All three
    measured corpora write their top-level entries this way, and two of them
    wrap the title in `**`. A reader that strips the list marker before looking
    for an ordinal eats the ordinal and reports the corpus as unnumbered.
    """
    files = {f"src/{n}.md": unit(f"Chapter {n}") for n in (1, 2, 3)}
    files["README.md"] = "# Marker Ordinals\n\n" + "\n".join(
        f"{n}. [**Chapter {n}**](src/{n}.md)" for n in (1, 2, 3)
    )
    return write(root, files)


def over_deep_ordinals(root: Path) -> Path:
    """Linked units whose ordinals have four components — more levels than names."""
    files = {}
    listing = ["# Deep", ""]
    for a in (1, 2):
        listing.append(f"{a}. Part {a}")
        for b in (1, 2):
            target = f"src/{a}-{b}.md"
            files[target] = unit(f"Unit {a}.{b}")
            listing.append(f"- [{a}.{b}.1.1. Unit {a}.{b}]({target})")
    files["README.md"] = "\n".join(listing) + "\n"
    return write(root, files)


def record_beside_units(root: Path) -> Path:
    """A curriculum record at the root that lists a unit sitting beside it.

    ⭐ **The shape that made the record a unit.** One unit shares the record's
    directory, so a directory wildcard for that unit also matches the record.
    """
    files = {
        "intro.md": unit("Introduction"),
        "chapters/1.md": unit("Chapter 1"),
        "chapters/2.md": unit("Chapter 2"),
    }
    files["README.md"] = (
        "# Beside\n\n"
        "- [1. Introduction](intro.md)\n"
        "- [2. Chapter 1](chapters/1.md)\n"
        "- [3. Chapter 2](chapters/2.md)\n"
    )
    return write(root, files)


#: A file cut into three top-level regions, two of them with a subsection.
CASES = (
    "# 1. Card issuance\n\n## 1.1 Activation\n\nText.\n\n"
    "# 2. Accounts\n\nText.\n\n"
    "# 3. Payments\n\n## 3.1 Clearing\n\nText.\n"
)


def linked_regions(
    root: Path, link: bool = True, cases: str = CASES, linked_aggregate: bool = False
) -> Path:
    """A record whose last group label is a heading linking a file of regions.

    ⭐ **W250's finding, at the smallest size that sets it.** Two groups under
    unlinked headings, one unit written as a linked heading inside its run (the
    minority form, and its file has subsections), then a heading that links a
    file whose headings are regions, followed by a copy of that file's heading
    tree. ⚠️ `link=False` is the control: the same heading, linking nothing.
    `linked_aggregate` makes the second group's label a heading linking a
    file of regions that DOES open entries.
    """
    files = {f"src/{n}.md": unit(f"Chapter {n}") for n in (1, 2)}
    files["src/3.md"] = "# Chapter 3\n\n## Part one\n\nText.\n\n## Part two\n\nText.\n"
    files.update({f"src/s{n}.md": unit(f"Server {n}") for n in (1, 2)})
    server = "Server"
    if linked_aggregate:
        files["src/Server.md"] = files["src/s1.md"] + "\n" + files["src/s2.md"]
        server = "[Server](src/Server.md)"
    files["TestCases.md"] = cases
    heading = "# [Test cases](TestCases.md)" if link else "# Test cases"
    copy = "\n".join(line for line in cases.splitlines() if line.startswith("#"))
    files["README.md"] = (
        "# Fundamentals\n\n1. [Chapter 1](src/1.md)\n2. [Chapter 2](src/2.md)\n\n"
        f"## 3. [Chapter 3](src/3.md)\n\n# {server}\n\n"
        "1. [Server 1](src/s1.md)\n2. [Server 2](src/s2.md)\n\n"
        f"{heading}\n\n{copy}\n"
    )
    return write(root, files)
