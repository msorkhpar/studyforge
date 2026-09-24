"""`studyforge serve` with narration off, in both forms, over clips on disk.

⭐ **Narration is optional**: clips may be generated and still not served.
Read here over real connections:

- off serves no clip — a typed clip address answers `404` — and says so;
- off over a site BUILT with narration refuses, naming each page and the fix,
  because the player is in the page's bytes and `serve` never edits a page;
- on, the positive control, serves the very same clip `200`;
- the clips on disk are byte-identical before and after every serve.
"""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import threading
from pathlib import Path

import pytest

from studyforge.cli import VERBS
from studyforge.cli.serve import main
from studyforge.cli.unvoiced import BUILT_VOICED, SERVED_SILENT
from studyforge.validate.report import INVALID, OK
from tests.fixture_checks import FIXTURES
from tests.studyforge.cli.serving import verb_running
from tests.studyforge.generate.test_narration import PLAYER, narrate
from tests.studyforge.serve.serving import fetch


def a_narrated_corpus(where: Path, name: str = "depth1", *, declared: bool | None = None) -> Path:
    """A fixture copy with a record and a clip per speech unit, `narration` as declared."""
    root = where / name
    shutil.copytree(FIXTURES / name, root)
    if declared is not None:
        manifest = root / "corpus.json"
        document = json.loads(manifest.read_text(encoding="utf-8"))
        document.update(corpus_api=5, narration=declared)
        manifest.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    assert narrate(root)
    return root


def build(root: Path, *flags: str) -> None:
    """Build the corpus into its own root, through the verb."""
    code = VERBS["build"].run([str(root), "--out", str(root), *flags], out=io.StringIO())
    assert code == OK


def clips(root: Path) -> dict[str, str]:
    """Every clip under `root`, by its path relative to it, with a digest of its bytes."""
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*.mp3"))
    }


def first_page(root: Path) -> str:
    return next(iter(sorted(root.rglob("*.unit.html")))).relative_to(root).as_posix()


def test_site_form_off_serves_no_clip_and_on_serves_it(tmp_path):
    root = a_narrated_corpus(tmp_path)
    before = clips(root)
    clip = next(iter(before))
    build(root, "--no-narration")

    argv = [str(root), "--site", str(root), "--port", "0"]
    with verb_running([*argv, "--no-narration"]) as serving:
        assert fetch(serving.server, "/" + clip)[0] == 404
        status, _, body = fetch(serving.server, "/" + first_page(root))
        assert status == 200 and PLAYER.encode() not in body
        assert f"narration off  {SERVED_SILENT}" in serving.out.getvalue()

    build(root)
    with verb_running(argv) as serving:
        assert fetch(serving.server, "/" + clip)[0] == 200
        assert PLAYER.encode() in fetch(serving.server, "/" + first_page(root))[2]
        assert "narration off" not in serving.out.getvalue()
    assert clips(root) == before


def refused(argv: list[str]) -> tuple[int, str, list]:
    """Run the verb; a server it wrongly starts is stopped at once, so a regression fails."""
    out, seen = io.StringIO(), []

    def started(server):
        seen.append(server)
        threading.Thread(target=server.shutdown, daemon=True).start()

    return main(argv, out=out, started=started), out.getvalue(), seen


def test_off_over_a_site_built_with_narration_refuses_naming_each_page(tmp_path):
    root = a_narrated_corpus(tmp_path)
    build(root)

    code, said, seen = refused([str(root), "--site", str(root), "--port", "0", "--no-narration"])

    assert code == INVALID and seen == [], said
    assert f"narrated {first_page(root)}  {BUILT_VOICED}" in said
    assert "serve http" not in said


@pytest.mark.parametrize("declared", [False, None])
def test_root_form_honours_each_corpus_s_own_answer(tmp_path, declared):
    served = tmp_path / "served"
    root = a_narrated_corpus(served, declared=declared)
    before = clips(root)
    clip = next(iter(before))
    build(root)

    with verb_running([str(served), "--port", "0"]) as serving:
        status = fetch(serving.server, f"/{root.name}/{clip}")[0]
        said = serving.out.getvalue()
    if declared is False:
        assert status == 404
        assert f"narration off  corpus depth1-demo: {SERVED_SILENT}" in said
    else:
        assert status == 200
        assert "narration off" not in said
    assert clips(root) == before


def test_root_form_override_refuses_a_voiced_build_and_serves_a_silent_one(tmp_path):
    served = tmp_path / "served"
    root = a_narrated_corpus(served)
    build(root)

    code, said, seen = refused([str(served), "--port", "0", "--no-narration"])
    assert code == INVALID and seen == [], said
    assert f"narrated {root.name}/{first_page(root)}  {BUILT_VOICED}" in said

    build(root, "--no-narration")
    clip = next(iter(clips(root)))
    with verb_running([str(served), "--port", "0", "--no-narration"]) as serving:
        assert fetch(serving.server, f"/{root.name}/{clip}")[0] == 404


def test_the_override_voices_a_corpus_its_author_silenced(tmp_path):
    root = a_narrated_corpus(tmp_path, declared=False)
    build(root, "--narration")
    clip = next(iter(clips(root)))

    with verb_running([str(root), "--site", str(root), "--port", "0", "--narration"]) as serving:
        assert fetch(serving.server, "/" + clip)[0] == 200
