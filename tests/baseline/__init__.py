"""The recorded behaviour the compatibility baseline compares against, and how each record is made.

Mirrors no source module. `tests/test_compatibility_baseline.py` compares the live
code with three recordings in this directory; this module is the one place that
says how each was produced, and `python3 -m tests.baseline --rewrite` is the one
command that rewrites them.

**What is recorded, and how.**

- `sites.json`: the sha256 of every file `studyforge.generate.write_site` writes for each
  valid fixture corpus, keyed by corpus and then by path inside the output root.
  Produced by building each fixture under `tests/fixtures/` into an empty directory.
- `exports.json`: the sha256 of every file of the thin and the self-contained export of
  the runnable fixture, released against the synthetic toolchain the export tests use
  and a placeholder-digest lock, after `normalised` has taken out what is a function of
  the checkout rather than of the export: the course commit, the library commit, the
  serving base's tag and the site image's inputs digest, and, in the self-contained
  mode only, the vendored library under `.studyforge/images/serve/`.
- `manifests.json`: every declaration `studyforge.corpus.manifest.parse` reads off each
  fixture manifest and off three synthetic ones (only the required keys at version 1,
  and every key at versions 7 and 8), as the parsed value.

Every recording was written from the code as it stood before any change that adds a
language, never from output a later change produced.

⛔ **Rewriting is a deliberate act.** A rewrite says that a behaviour a reader of an
existing corpus could see has moved, so it belongs in a change that gives the reason.
A change that merely adds an optional feature leaves all three files as they are.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

from studyforge.corpus.manifest import parse
from studyforge.generate import write_site
from tests.support import repository_root

DIRECTORY = Path(__file__).resolve().parent
FIXTURES = repository_root() / "tests" / "fixtures"
SITE_CORPORA = ("depth1", "depth2", "shared-origin", "runnable")
SERVE_TREE = ".studyforge/images/serve/"
RELEASE = ".studyforge/release.json"

#: Declared by hand, so that no optional key reaches the record by being added to the parser.
REQUIRED_AT_ONE = {
    "corpus_api": 1,
    "source": "example-corpus",
    "title": "Example Corpus",
    "levels": ["section", "module"],
    "variants": ["java"],
    "exercises": True,
    "placement": "tree",
    "content": {"include": ["*/*/README*.md"], "exclude": []},
}
EVERY_KEY = {
    **REQUIRED_AT_ONE,
    "corpus_api": 8,
    "runtimes": ["java", "maven", "python"],
    "narration": False,
    "onboarding_doc": "docs/START.md",
    "curriculum": {
        "record": "SUMMARY.md",
        "containers": [
            {"label": "The Basics", "address": "basics"},
            {"label": "Appendix", "address": "appendix"},
        ],
        "linked": "module",
    },
    "content": {
        "include": ["src/*.md"],
        "exclude": [
            {"path": "src/README.md", "why": "the container introduction, never read as a unit"}
        ],
        "not_material": [
            {"glob": "*/name", "why": "files generated beside the source, never prose"}
        ],
    },
    "media": {"commit": "never", "max_total_bytes": 1000, "max_file_bytes": 100, "max_files": 5},
    "permitted_edits": [
        {
            "path": "pom.xml",
            "kind": "insert-line",
            "anchor": "<modules>",
            "content": "  <module>x</module>",
            "why": "the practice module has to be listed to compile",
        }
    ],
}


#: The same, a version earlier: a curriculum whose groups carry a filing prefix and are not linked.
EVERY_KEY_AT_SEVEN = {
    **EVERY_KEY,
    "corpus_api": 7,
    "levels": ["group"],
    "content": {
        **EVERY_KEY["content"],
        "not_material": [{"glob": "generated/**", "why": "files generated beside the source"}],
    },
    "curriculum": {
        "record": "SUMMARY.md",
        "containers": [
            {"label": "The Basics", "address": "basics", "prefix": "basics-"},
            {"label": "Appendix", "address": "appendix"},
        ],
    },
}


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_hashes(root: Path, skip: str | None = None) -> dict[str, str]:
    """`{path: sha256}` for every file under `root`, sorted by path."""
    found = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_file() and not (skip and relative.startswith(skip)):
            found[relative] = _hash(path.read_bytes())
    return found


def sites() -> dict[str, dict[str, str]]:
    """The hashes of what a build writes for each valid fixture corpus."""
    built = {}
    for name in SITE_CORPORA:
        with tempfile.TemporaryDirectory() as scratch:
            write_site(FIXTURES / name, Path(scratch))
            built[name] = tree_hashes(Path(scratch))
    return built


def normalised(root: Path, whole: bool) -> dict[str, str]:
    """`{path: sha256}` for an export, less what the checkout alone decides (see the module)."""
    document = json.loads((root / RELEASE).read_text(encoding="utf-8"))
    commit = document["exported_from"]
    for key in ("exported_from", "library", "deferred_edges"):
        document.pop(key)
    document["keeps"] = [kept for kept in document["keeps"] if not kept.startswith(SERVE_TREE)]
    serve = re.compile(r"\d+\.\d+\.\d+-[0-9a-f]{64}")
    site = re.compile(rf"(-site:{commit[:12]}-)[0-9a-f]{{12}}(-)")

    def clean(text: str) -> str:
        text = site.sub(r"\1<site-inputs>\2", serve.sub("<serve-tag>", text))
        return text.replace(commit, "<commit>").replace(commit[:12], "<commit12>")

    found = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if not path.is_file() or (whole and relative.startswith(SERVE_TREE)):
            continue
        if relative == RELEASE:
            data = clean(json.dumps(document, indent=1, sort_keys=True)).encode("utf-8")
        else:
            raw = path.read_bytes()
            try:
                data = clean(raw.decode("utf-8")).encode("utf-8")
            except UnicodeDecodeError:
                data = raw
        found[relative] = _hash(data)
    return found


def exports(where: Path) -> dict[str, dict[str, str]]:
    """Both exports of the runnable fixture, released the way the export tests release it."""
    from tests.studyforge.skills.execution.standalone.test_bases import lock, parsed
    from tests.studyforge.skills.execution.standalone.test_write import export

    thin, _ = export(where, parsed(lock()), "thin")
    whole, _ = export(where, None, "whole")
    return {"thin": normalised(thin, False), "self-contained": normalised(whole, True)}


def manifests() -> dict[str, Any]:
    """Every declaration the parser reads off each recorded manifest."""
    documents = {
        name: (FIXTURES / name / "corpus.json").read_text(encoding="utf-8") for name in SITE_CORPORA
    }
    documents["required-keys-at-version-1"] = json.dumps(REQUIRED_AT_ONE)
    documents["every-key-at-version-7"] = json.dumps(EVERY_KEY_AT_SEVEN)
    documents["every-key-at-version-8"] = json.dumps(EVERY_KEY)
    return {name: _declarations(parse(text)) for name, text in documents.items()}


def _declarations(manifest: Any) -> dict[str, Any]:
    """The parsed value as the recordings hold it.

    A declaration a later optional key added and a manifest never made (its value is the
    absent one, `None`) is left out: the recordings were written before that key existed,
    and an absent key is today. A manifest that does declare it records it in full.
    """
    value = json.loads(json.dumps(dataclasses.asdict(manifest), default=list))
    for later in ("reading", "profile", "live"):
        if value.get(later) is None:
            value.pop(later, None)
    return value


def recorded(name: str) -> Any:
    return json.loads((DIRECTORY / name).read_text(encoding="utf-8"))["recorded"]


def rewrite() -> None:
    """Write all three recordings from the live code. ⛔ Deliberate only: see the module."""
    scratch = Path(tempfile.mkdtemp(dir=repository_root().parent))
    try:
        for name, value in (
            ("sites.json", sites()),
            ("exports.json", exports(scratch)),
            ("manifests.json", manifests()),
        ):
            text = json.dumps({"recorded": value}, indent=1, sort_keys=True) + "\n"
            (DIRECTORY / name).write_text(text, encoding="utf-8")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
