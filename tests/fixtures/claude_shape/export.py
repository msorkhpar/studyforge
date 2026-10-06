"""Export the course shape thin, on its image profile, the way a course is published.

⭐ The steps a course owner takes after the authoring pass, in order: record the execution
files and both images' tags from the pinned toolchain, build the site into the checkout, commit,
and write the learner tree with a bases lock that names the profile. Every tag is asked of the
toolchain and every image is named by the id of the image built from it, so a compose built
from the tree starts from the images on this host. ⛔ Nothing is pushed and no account is named:
the namespace is the placeholder the tree carries.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from studyforge.corpus.manifest import parse
from studyforge.skills.execution import generate, record_editor, record_runner, write as write_execution
from studyforge.skills.execution.standalone import bases, write

RUNTIMES = "gradle,java,kotlin,node,python"
PLATFORM = ("--platform", "linux/amd64")
GIT = ("git", "-c", "user.name=Example", "-c", "user.email=contact@example.com")


def run(argv, cwd):
    """The caller's one way in: a real process, `python3` being this interpreter."""
    done = subprocess.run(  # noqa: S603 - argv, no shell
        [sys.executable if one == "python3" else one for one in argv],
        cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False,
    )
    return done.returncode, done.stdout


def prepared(corpus: Path, checkout: Path, toolchain: Path) -> Path:
    """Copy the authored corpus to `checkout`, record its execution, build its site, commit."""
    shutil.copytree(corpus, checkout)
    manifest = parse((checkout / "corpus.json").read_text(encoding="utf-8"))
    editor_text = (toolchain / "consuming.json").read_text(encoding="utf-8")
    execution = generate(manifest, editor_text=editor_text, root=checkout)
    write_execution(execution, checkout)
    record_runner(execution, checkout, toolchain, ask=run)
    record_editor(execution, checkout, toolchain, ask=run)
    built = subprocess.run(  # noqa: S603 - argv, no shell
        [sys.executable, "-m", "studyforge.cli", "build", str(checkout), "--out", str(checkout),
         "--no-narration"], capture_output=True, text=True, check=False,
        stdin=subprocess.DEVNULL,
    )
    assert built.returncode == 0, built.stderr
    for argv in (("init", "-q"), ("add", "-A"), ("commit", "-q", "-m", "course")):
        subprocess.run([*GIT, *argv], cwd=checkout, check=True, stdin=subprocess.DEVNULL)
    return checkout


def computed(toolchain: Path, image: str, profile: str) -> str:
    """The tag the toolchain computes for the profile's `image`, without its repository."""
    code, printed = run(
        ["python3", "docker/profile_packages/package_build.py", "--profile", profile, "--image",
         image, "--runtimes", RUNTIMES, *PLATFORM, "--print-tag"], toolchain)
    assert code == 0, image
    return printed.strip().split(":", 1)[1]


def base_tag(toolchain: Path, image: str) -> str:
    code, printed = run(
        ["python3", "consuming/builds.py", image, "--runtimes", RUNTIMES, *PLATFORM], toolchain)
    assert code == 0, image
    return json.loads(printed)["tag"].split(":", 1)[1]


def lock(toolchain: Path, profile: str, serve_tag: str, ids: dict[str, str]) -> bases.Bases:
    """The bases lock: every tag asked of the toolchain, every digest the id of the image built."""
    document = {
        "bases_api": 1,
        "serve": {"image": "studyforge-serve", "tag": serve_tag, "digest": ids["serve"]},
        "runner": {"image": "studyforge-code-toolchain-runner", "tag": base_tag(toolchain, "runner"),
                   "digest": ids["runner"]},
        "editor": {"image": "studyforge-code-toolchain-editor", "tag": base_tag(toolchain, "editor"),
                   "digest": ids["editor"]},
        "profile": {
            "name": profile,
            "runner": {"image": bases.profile_image("runner", profile),
                       "tag": computed(toolchain, "runner", profile), "digest": ids["profile-runner"]},
            "editor": {"image": bases.profile_image("editor", profile),
                       "tag": computed(toolchain, "editor", profile), "digest": ids["profile-editor"]},
        },
    }
    where = Path(ids["where"])
    where.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return bases.read(where)


def exported(checkout: Path, out: Path, toolchain: Path, locked: bases.Bases) -> object:
    return write.release(
        checkout, out, toolchain=toolchain, platform="linux/amd64", bases=locked, run=run
    )
