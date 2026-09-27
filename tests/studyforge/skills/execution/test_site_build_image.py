"""The site's build line, as `EXECUTION.md` prints it, builds the tag `site.env` names.

⭐ **A HOST reading, opt-in behind `STUDYFORGE_RUNNER_BUILDS=1`**, because it
builds an image. A fixture corpus is generated; its site context is staged with
a stand-in build file on the site image's own pinned base (`siteimage.BASE`,
never pulled here: pull it once by that digest), and `site.env` names a tag no
other reading uses. ⛔ The printed line is split by `shlex` and run with no shell
at all, which is how it runs the same in PowerShell as in sh: a line that
needed `$(…)` would hand docker the literal text and fail here.

⛔ The image is removed whatever happens.
"""

from __future__ import annotations

import os
import shlex
import subprocess
import uuid

import pytest

from studyforge.skills.execution import onboard, siteimage, siteservice
from tests.harness import engine
from tests.studyforge.exercise.bundle.test_dependency_image import CONSENT
from tests.studyforge.skills.execution.test_instance import generated
from tests.support import tool_on_path


def docker(*arguments: str, cwd=None, env=None):
    return subprocess.run(
        ["docker", *arguments],
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )


def test_the_printed_site_build_builds_the_tag_site_env_names_with_no_shell():
    if os.environ.get(CONSENT) != "1":
        pytest.skip(f"set {CONSENT}=1 to let this module build an image")
    if tool_on_path("docker") is None:
        pytest.skip("no docker CLI in this environment (the pinned dev image carries none)")
    if docker("image", "inspect", siteimage.BASE).returncode != 0:
        pytest.skip("the site image's pinned base is not on this engine; pull it by its digest")
    tag = f"studyforge-site:w511-reading-{uuid.uuid4().hex[:12]}"
    with engine.shared("site-build") as root:
        made, _ = generated(root)
        onboard.write(made, root)
        context = root / siteimage.SITE_DIR
        context.mkdir(parents=True, exist_ok=True)
        (context / siteimage.BUILD_FILE).write_text(
            f'FROM {siteimage.BASE}\nENTRYPOINT ["python3", "-c", "print(0)"]\n', encoding="utf-8"
        )
        (root / onboard.SITE_ENV).write_text(siteimage.site_env(tag, "0" * 40), encoding="utf-8")
        for placeholder in (onboard.RUNNER_ENV, onboard.EDITOR_ENV):
            (root / placeholder).write_text("# a placeholder: nothing here is started\n")
        document = (root / onboard.READER_DOC).read_text(encoding="utf-8")
        [line] = [one for one in document.splitlines() if one.endswith(" build site")]
        argv = shlex.split(line)
        assert argv[-1] == siteservice.SERVICE
        # The synthetic contract's other required values, which no corpus file holds.
        env = dict(
            os.environ,
            CODE_SERVER_PASSWORD="placeholder",
            EDITOR_IMAGE="example/editor:never-pulled",
            STUDYFORGE_RUNNER_IMAGE="example/runner:never-pulled",
        )
        try:
            built = subprocess.run(
                argv, cwd=root, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True
            )
            assert built.returncode == 0, (built.stdout + built.stderr)[-4000:]
            assert docker("image", "inspect", tag).returncode == 0, "no image by site.env's tag"
        finally:
            docker("image", "rm", "--force", tag)
