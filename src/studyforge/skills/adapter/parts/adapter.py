r"""The four generated modules of an adapter: the surface, emit, audit, the command.

**What it does.** Renders the four modules of an adapter that are generated
whole and stay generated, and joins them to the fifth — the reading step, which
`parts.reading` holds because it is the one a person writes.

**How you use it.** Through `PARTS`. `ADAPTER_PARTS` is this half of that list.

**Depends on.** `parts.compose` for the composer, `parts.reading` for the one
hand-written part, `plan` for the facts a renderer may vary on. ⛔ Nothing else:
a renderer that needed to read a source would be the framework knowing about
one (R1).

## ⛔ Why the split from `parts.reading` is here and not somewhere else

⚠️ **R11:** as one file this was 428 lines, over R11's ceiling, and the
split is the default rather than a size exception. ⭐ The seam it took is the
one that already existed — **generated versus hand-written** — so the module
boundary and R19's boundary are the same boundary, and a reader asking *which
files are mine* gets the answer from the import list.

## ⛔ Stage, then move — and the generated `emit` does it in that order

⚠️ §6: a container map that fails its own validation is never left at the path
`validate` will read. One unreadable map halts every consumer that walks the
tree, and the failure is then reported at the reader rather than at the writer.
⭐ So the generated emit builds the whole archive beside its destination and
moves it only once every file exists.

## ⛔ One run, one date — applied after the reader, never handed to it

⚠️ **One date per run (R10):** a container map once took the date `read` recorded while its
documents took the run's, so one emission could disagree with itself. ⭐ The
run's `ingested` now replaces each container's after `read` returns it, and
`read`'s signature is unchanged: an adapter written before this keeps reading,
and regenerating `emit` is the whole fix (R19).
"""

from __future__ import annotations

from studyforge.skills.adapter.parts.compose import Part, module
from studyforge.skills.adapter.parts.reading import READ_PART
from studyforge.skills.adapter.plan import Plan


def _surface(plan: Plan) -> str:
    """Render the adapter package's own contract: what it is, and what `done` means."""
    return module(
        summary=f"The {plan.source} adapter: read this source, write an archive, prove it.",
        does=(
            "Reads this repository's own material and writes the archive "
            f"`studyforge validate` accepts. {plan.depth} container level(s), "
            f"variant(s) {', '.join(plan.variants)}, document kind(s) "
            f"{', '.join(plan.kinds)} — every one of those from `corpus.json`."
        ),
        uses=(
            f"`python3 -m {plan.package} <corpus-root>` writes the archive and audits it. "
            "The exit code is the answer; there is no other agreement with the framework."
        ),
        depends=(
            "`studyforge` as a sibling checkout, and nothing else. "
            "⛔ The framework never imports this package: the seam is on disk (R2)."
        ),
        body=[
            "",
            f"from {plan.package}.audit import audit",
            f"from {plan.package}.emit import emit",
            f"from {plan.package}.read import containers, documents",
            "",
            '__all__ = ["audit", "containers", "documents", "emit"]',
        ],
    )


def _emit(plan: Plan) -> str:
    """Everything downstream of reading: build, stage, move. Generated whole."""
    return module(
        summary="Write the archive: build it beside its destination, then move it (§6).",
        does=(
            "Takes what `read` returned and writes every container map and every archive "
            "document at the paths `studyforge validate` walks. ⛔ Nothing reaches the "
            "destination until every file has been built, and every map and document of one "
            "run carries that run's one `ingested`."
        ),
        uses="`emit(root, ingested='YYYY-MM-DD')` returns the paths it wrote, sorted.",
        depends=(
            "`studyforge.skills.adapter` for the layout, `studyforge.archive.document` and "
            "`studyforge.corpus` for the two formats. ⛔ Never on `read`'s internals — only "
            "on what it returns."
        ),
        body=[
            "",
            "import dataclasses",
            "import shutil",
            "from pathlib import Path",
            "",
            "from studyforge.archive.document import build",
            "from studyforge.archive.document import render as render_document",
            "from studyforge.corpus.container import render as render_map",
            "from studyforge.corpus.manifest import MANIFEST_FILENAME",
            "from studyforge.corpus.manifest import load as load_manifest",
            "from studyforge.skills.adapter import Layout, plan_for",
            "",
            f"from {plan.package} import read",
            "",
            "",
            "class EmitRefused(RuntimeError):",
            '    """An emission this adapter will not perform, and the field that is why.',
            "",
            "    ⛔ Names the field and what would settle it, never a path or a value (R7).",
            '    """',
            "",
            "",
            "def emit(root, *, ingested: str, into=None, replace: bool = False) -> list[str]:",
            '    """Write the whole archive, or write nothing at all.',
            "",
            "    `root` is where the material and `corpus.json` are; `into` is where the",
            "    archive goes, and defaults to `root`. ⭐ The two are separable so a test",
            "    can emit this corpus into a temporary directory and validate it there,",
            "    without the suite writing into the repository it is reading.",
            '    """',
            "    root = Path(root)",
            "    target = Path(root if into is None else into)",
            "    plan = plan_for(load_manifest(root / MANIFEST_FILENAME))",
            "    layout = Layout(target, plan.archive_dir)",
            "    if layout.archive.exists() and not replace:",
            "        raise EmitRefused(",
            '            "the archive directory already exists; pass replace=True to rebuild it. "',
            '            "⛔ Nothing outside it is written, moved or renamed either way (R3)."',
            "        )",
            "    staging = Layout(layout.staging, plan.archive_dir)",
            "    if layout.staging.exists():",
            "        shutil.rmtree(layout.staging)",
            "    written = []",
            "    for reading in read.containers(root):",
            "        # ⛔ One run, one date. The run's `ingested` is applied AFTER",
            "        # `read`, never handed to it, so whatever date `read` recorded is replaced",
            "        # and a map can never disagree with the documents beneath it.",
            "        container = dataclasses.replace(reading, ingested=ingested)",
            "        written.append(_write(staging.container_map(container.address),",
            "                              render_map(container), staging))",
            "        for fields in read.documents(root, container):",
            "            document = build(source=plan.source, ingested=ingested, **fields)",
            "            where = staging.document(",
            '                document["address"],',
            '                document["variant"],',
            '                document["unit"],',
            '                document["kind"],',
            '                document["ordinal"],',
            "            )",
            "            written.append(_write(where, render_document(document), staging))",
            "    if not written:",
            "        shutil.rmtree(layout.staging, ignore_errors=True)",
            "        raise EmitRefused(",
            '            "read.containers returned nothing, so this run would move an empty "',
            '            "archive into place. An empty corpus is a silent failure, not a result."',
            "        )",
            "    # ⛔ §6: only now does anything move. A map that could not be built has",
            "    # already raised, and nothing was ever left at the path validate reads.",
            "    if layout.archive.exists():",
            "        shutil.rmtree(layout.archive)",
            "    (layout.staging / plan.archive_dir).replace(layout.archive)",
            "    shutil.rmtree(layout.staging, ignore_errors=True)",
            "    return sorted(written)",
            "",
            "",
            "def _write(path: Path, text: str, staging: Layout) -> str:",
            '    """Write one staged file and return where it will land, root-relative (R7)."""',
            "    path.parent.mkdir(parents=True, exist_ok=True)",
            '    path.write_text(text, encoding="utf-8")',
            "    return staging.relative(path)",
        ],
    )


def _audit(plan: Plan) -> str:
    """R6's enforcement for one corpus: the count `validate` cannot make."""
    return module(
        summary="Audit this ingest: what `validate` checks, plus the count only this side makes.",
        does=(
            "Runs `studyforge validate` and adds the one check it cannot: a unit count taken "
            "from the **source**, not from the archive. ⚠️ A check that recounts the "
            "parser's own output agrees with itself by construction and catches nothing."
        ),
        uses=f"`python3 -m {plan.package}.audit <corpus-root>`. Exit 0 means both halves agree.",
        depends="`studyforge.validate`, `studyforge.skills.adapter`, and this package's `read`.",
        body=[
            "",
            "import sys",
            "from pathlib import Path",
            "",
            "from studyforge.corpus.container import CONTAINER_FILENAME",
            "from studyforge.corpus.manifest import MANIFEST_FILENAME",
            "from studyforge.corpus.manifest import load as load_manifest",
            "from studyforge.skills.adapter import RAW_DIR, Layout, plan_for",
            "from studyforge.validate import INVALID, UNUSABLE, validate",
            "",
            f"from {plan.package} import read",
            "",
            "#: Why the source-side count is the check that matters. ⛔ Reported as an",
            "#: unchecked claim while it is unwritten — saying so is not the same as",
            "#: saying the archive is fine.",
            "UNCHECKED = (",
            '    "expected_units is not written, so nothing has counted this corpus from its "',
            '    "own source. `studyforge validate` recounts what the adapter wrote; only "',
            '    "this function can disagree with it."',
            ")",
            "",
            "#: The rule id this module adds to the ones `validate` reports.",
            'RULE_SOURCE_COUNT = "source-count"',
            "",
            "",
            "def audit(root) -> tuple[list[str], int]:",
            '    """Return the lines a person reads and the exit code a script reads."""',
            "    root = Path(root)",
            "    report = validate(root)",
            "    lines = list(report.lines())",
            "    code = report.exit_code",
            "    expected = read.expected_units(root)",
            "    if expected is None:",
            '        lines.append(f"corpus.json: [{RULE_SOURCE_COUNT}] not checked — {UNCHECKED}")',
            "        return lines, INVALID",
            "    found = _on_disk(root)",
            "    for key in sorted(set(expected) | set(found)):",
            "        if expected.get(key) != found.get(key):",
            "            lines.append(",
            '                f"{key}: [{RULE_SOURCE_COUNT}] the source records "',
            '                f"{expected.get(key, 0)} unit(s); the archive holds "',
            '                f"{found.get(key, 0)}"',
            "            )",
            "            code = INVALID",
            "    return lines, code",
            "",
            "",
            "def _on_disk(root: Path) -> dict[str, int]:",
            '    """Count the unit directories the archive actually holds, by address."""',
            "    plan = plan_for(load_manifest(root / MANIFEST_FILENAME))",
            "    layout = Layout(root, plan.archive_dir)",
            "    found: dict[str, int] = {}",
            "    for path in sorted(layout.archive.rglob(CONTAINER_FILENAME)):",
            "        key = path.parent.relative_to(layout.archive).as_posix()",
            "        raw = path.parent / RAW_DIR",
            '        found[key] = sum(1 for unit in raw.rglob("unit-*") if unit.is_dir())',
            "    return found",
            "",
            "",
            "def main(argv=None) -> int:",
            '    """Audit one corpus root named on the command line."""',
            "    argv = list(sys.argv[1:] if argv is None else argv)",
            "    if len(argv) != 1:",
            f'        print("usage: python3 -m {plan.package}.audit <corpus-root>")',
            "        return UNUSABLE",
            "    lines, code = audit(argv[0])",
            "    for line in lines:",
            "        print(line)",
            "    return code",
            "",
            "",
            'if __name__ == "__main__":  # pragma: no cover - the command line',
            "    raise SystemExit(main())",
        ],
    )


def _command(plan: Plan) -> str:
    """Render the one command: emit, then audit, then say which it was."""
    return module(
        summary="The ingest command: write the archive, then audit what was written.",
        does=(
            "One run of the whole adapter. Emits, audits, prints both, and returns the "
            "audit's exit code — so the answer to *did this work* is a number, not an opinion."
        ),
        uses=f"`python3 -m {plan.package} <corpus-root> [YYYY-MM-DD]`.",
        depends="This package's `emit` and `audit`, and `studyforge.validate` for the codes.",
        body=[
            "",
            "import sys",
            "from datetime import date",
            "",
            "from studyforge.validate import UNUSABLE",
            "",
            f"from {plan.package}.audit import audit",
            f"from {plan.package}.emit import emit",
            "",
            "",
            "def main(argv=None) -> int:",
            '    """Emit and audit one corpus root; return the audit\'s exit code."""',
            "    argv = list(sys.argv[1:] if argv is None else argv)",
            "    if not 1 <= len(argv) <= 2:",
            f'        print("usage: python3 -m {plan.package} <corpus-root> [YYYY-MM-DD]")',
            "        return UNUSABLE",
            "    root = argv[0]",
            "    # ⚠️ R10: re-running produces identical bytes apart from `ingested`, so the",
            "    # date is an argument first and today's date only as a fallback.",
            "    ingested = argv[1] if len(argv) == 2 else date.today().isoformat()",
            "    for where in emit(root, ingested=ingested, replace=True):",
            '        print(f"wrote {where}")',
            "    lines, code = audit(root)",
            "    for line in lines:",
            "        print(line)",
            "    return code",
            "",
            "",
            'if __name__ == "__main__":  # pragma: no cover - the command line',
            "    raise SystemExit(main())",
        ],
    )


#: The adapter's own modules, in the order `SKILL.md` builds them.
ADAPTER_PARTS: tuple[Part, ...] = (
    Part(
        where="{package}/__init__.py",
        step=3,
        why="the adapter's contract: what it is, and what its definition of done is",
        generated=True,
        render=_surface,
    ),
    READ_PART,
    Part(
        where="{package}/emit.py",
        step=3,
        why="build the whole archive beside its destination, then move it (§6)",
        generated=True,
        render=_emit,
    ),
    Part(
        where="{package}/audit.py",
        step=6,
        why="R6's enforcement: the source-side count `validate` cannot make",
        generated=True,
        render=_audit,
    ),
    Part(
        where="{package}/__main__.py",
        step=3,
        why="one command — emit, audit, and an exit code that is the answer",
        generated=True,
        render=_command,
    ),
)
