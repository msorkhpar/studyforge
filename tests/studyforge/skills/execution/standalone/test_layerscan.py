"""Mirror of `src/studyforge/skills/execution/standalone/layerscan.py` (R12).

⭐ Each test builds a `docker save` archive by hand, so no daemon runs here.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import shutil
import stat
import tarfile

import pytest

from studyforge.archive.scrub import findings
from studyforge.skills.execution.standalone import layerscan

#: Personal-data shapes the shared pattern set refuses, made up and assembled here so the
#: repository's own sweep does not read them as this file's (as `test_scrub` does).
LEAK = "jane.doe@" + "mailhost.org"
HOME = "/" + "home/someone"


def _layer(files: dict[str, bytes], *, links: dict[str, str] | None = None) -> bytes:
    """One uncompressed layer tarball, owned by root, read-only, like a real one."""
    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode="w") as tar:
        dirs = {
            "/".join(path.split("/")[:i]) for path in files for i in range(1, path.count("/") + 1)
        }
        for name in sorted(dirs):
            info = tarfile.TarInfo(name)
            info.type, info.mode, info.uid, info.gid = tarfile.DIRTYPE, 0o555, 0, 0
            tar.addfile(info)
        for name, data in files.items():
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.uid, info.gid = len(data), 0o444, 0, 0
            tar.addfile(info, io.BytesIO(data))
        for name, target in (links or {}).items():
            info = tarfile.TarInfo(name)
            info.type, info.linkname = tarfile.SYMTYPE, target
            tar.addfile(info)
    return out.getvalue()


def _diff_id(layer: bytes) -> str:
    return "sha256:" + hashlib.sha256(layer).hexdigest()


def _save(path, layers: list[bytes], *, gzipped: frozenset[int] = frozenset(), history=()):
    """Write a `docker save` archive of `layers` (bottom first) to `path`."""
    config = {
        "config": {"Labels": {"note": "fine"}},
        "rootfs": {"type": "layers", "diff_ids": [_diff_id(one) for one in layers]},
        "history": list(history),
    }
    blobs = {}
    names = []
    for index, layer in enumerate(layers):
        stored = gzip.compress(layer) if index in gzipped else layer
        name = f"blobs/sha256/{hashlib.sha256(stored).hexdigest()}"
        blobs[name] = stored
        names.append(name)
    raw = json.dumps(config).encode()
    blobs[f"blobs/sha256/{hashlib.sha256(raw).hexdigest()}"] = raw
    manifest = [{"Config": f"blobs/sha256/{hashlib.sha256(raw).hexdigest()}", "Layers": names}]
    blobs["manifest.json"] = json.dumps(manifest).encode()
    with tarfile.open(path, "w") as tar:
        for name, data in blobs.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))


BASE_ONE = _layer({"usr/share/doc/pkg/AUTHORS": f"maintainer {LEAK}\n".encode()})
BASE_TWO = _layer({"opt/tool/README": f"report bugs to {LEAK}\n".encode()})
ADDED = _layer(
    {"app/course/lesson.md": b"clean text\n", "app/course/notes.txt": f"by {LEAK}\n".encode()},
    links={"app/home": f"{HOME}/course"},
)


def _run(tmp_path, layers, base, **save):
    _save(tmp_path / "image.tar", layers, **save)
    (tmp_path / "base.json").write_text(json.dumps(base), encoding="utf-8")
    out = tmp_path / "added"
    code = layerscan.main([str(tmp_path / "image.tar"), str(tmp_path / "base.json"), str(out)])
    return code, out


def _found(out) -> list[str]:
    hits = []
    for path in sorted(out.rglob("*")):
        if path.is_file() and not path.is_symlink():
            text = path.read_text(encoding="utf-8", errors="replace")
            hits += [where for where, _ in findings(text, str(path.relative_to(out)))]
    return hits


def test_only_the_layers_on_top_of_the_base_are_written(tmp_path):
    base = [_diff_id(BASE_ONE), _diff_id(BASE_TWO)]
    code, out = _run(tmp_path, [BASE_ONE, BASE_TWO, ADDED], base, gzipped=frozenset({1}))
    assert code == 0
    written = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
    assert "layer-2/app/course/lesson.md" in written
    assert not any("usr/" in one or "opt/" in one for one in written)
    # ⭐ The one leak the course added is found; the base's two are not looked at.
    assert set(_found(out)) == {"layer-2/app/course/notes.txt:1", "layer-2.paths:5"}


def test_a_compressed_layer_is_read_like_a_plain_one(tmp_path):
    code, out = _run(tmp_path, [BASE_ONE, ADDED], [_diff_id(BASE_ONE)], gzipped=frozenset({1}))
    assert code == 0 and (out / "layer-1/app/course/lesson.md").read_bytes() == b"clean text\n"


def test_a_link_target_and_every_path_are_listed_for_the_sweep(tmp_path):
    code, out = _run(tmp_path, [BASE_ONE, ADDED], [_diff_id(BASE_ONE)])
    listed = (out / "layer-1.paths").read_text(encoding="utf-8").splitlines()
    assert f"app/home -> {HOME}/course" in listed and "app/course/lesson.md" in listed
    assert not (out / "layer-1/app/home").exists()


def test_the_image_config_is_written_without_the_base_history(tmp_path):
    history = [
        {"created_by": f"base step {HOME}/one"},
        {"created_by": "ENV X=1", "empty_layer": True},
        {"created_by": "COPY course /app"},
    ]
    code, out = _run(tmp_path, [BASE_ONE, ADDED], [_diff_id(BASE_ONE)], history=history)
    config = json.loads((out / "config.json").read_text(encoding="utf-8"))
    assert [one["created_by"] for one in config["history"]] == ["ENV X=1", "COPY course /app"]
    assert config["config"]["Labels"] == {"note": "fine"}


def test_what_is_written_is_the_current_users_to_delete(tmp_path):
    code, out = _run(tmp_path, [BASE_ONE, ADDED], [_diff_id(BASE_ONE)])
    assert code == 0
    for path in out.rglob("*"):
        assert path.stat().st_mode & stat.S_IWUSR, path
    shutil.rmtree(out)
    assert not out.exists()


def test_no_base_means_the_whole_image(tmp_path):
    code, out = _run(tmp_path, [BASE_ONE, ADDED], [])
    assert code == 0 and (out / "layer-0/usr/share/doc/pkg/AUTHORS").is_file()


def test_an_image_not_built_on_the_base_is_refused(tmp_path, capsys):
    code, out = _run(tmp_path, [BASE_ONE, ADDED], [_diff_id(BASE_TWO)])
    assert code == 1 and not out.exists()
    assert "not built on" in capsys.readouterr().err


def test_a_path_that_climbs_out_is_listed_and_never_written(tmp_path):
    climbing = _layer({"../escape": b"x", "ok": b"y"})
    code, out = _run(tmp_path, [climbing], [])
    assert code == 0 and not (tmp_path / "escape").exists()
    assert "../escape" in (out / "layer-0.paths").read_text(encoding="utf-8")


@pytest.mark.parametrize("argv", [[], ["a", "b"]])
def test_the_usage_is_printed_for_wrong_arguments(argv, capsys):
    assert layerscan.main(argv) == 2
    assert "usage" in capsys.readouterr().err
