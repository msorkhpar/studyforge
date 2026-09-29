r"""The automation that keeps a learner repository's read-only preview online.

**What it does.** Holds the text of `.github/workflows/pages.yml`, the workflow a learner
`main` carries, and names the one file of `.github/preview/`, the copy of the preview
builder that the workflow runs. On every push to `main` the workflow builds the preview
from `main`'s own tree and deploys it to GitHub Pages, so the preview never drifts and no
`gh-pages` branch exists.

**How you use it.** `workflow()` is the workflow's text; `builder()` maps each path of
`.github/preview/` to the bytes of its source, `preview.py`. `write`
puts both into the learner tree and lists them in the manifest.

**Depends on.** Nothing but the two files it reads. ⛔ It starts no process and makes no
request; the workflow's pinned actions are constants below, resolved once.

## ⛔ The workflow is fixed to the least it needs

⭐ Triggers: a push to `main` and a manual run, nothing else (no `pull_request_target`, no
schedule). ⭐ Permissions: `contents: read`, `pages: write` and `id-token: write`, which is
what the Pages deployment asks for. ⭐ Every action is one of GitHub's own (`actions/`)
and is pinned by the full commit SHA of a release, with the release in a comment: a moved
tag changes nothing. ⛔ The text names no owner, no repository and no account (the run reads
them from the `github` context) and uses no secret.

## ⭐ One source for the builder

⭐ `.github/preview/preview.py` is the framework's own `preview`, byte for byte, in one file that
uses only the Python standard library, so a GitHub-hosted runner runs it with plain `python3`.
⛔ Nothing here edits it on the way.
"""

from __future__ import annotations

from pathlib import Path

#: Where the learner tree keeps the workflow, and its builder.
WORKFLOW = ".github/workflows/pages.yml"
BUILDER_DIR = ".github/preview"

#: The script the workflow runs: the framework's own `preview`, alone in its file.
SCRIPT = "preview.py"
SOURCES = (SCRIPT,)

#: Every path the export writes itself under `.github/`: a course that tracks one is refused.
OWNED = (WORKFLOW,)

#: The directory the workflow builds into and uploads.
SITE = "_site"

#: ⭐ Every action the workflow uses: `owner/name`, the FULL commit SHA, and the release it is.
#: Resolved with `git ls-remote https://github.com/actions/<name> 'refs/tags/v*'`, the latest
#: stable major of each; a release is changed here and nowhere else.
ACTIONS = {
    "actions/checkout": ("3d3c42e5aac5ba805825da76410c181273ba90b1", "v7.0.1"),
    "actions/configure-pages": ("45bfe0192ca1faeb007ade9deae92b16b8254a0d", "v6.0.0"),
    "actions/upload-pages-artifact": ("fc324d3547104276b827a68afc52ff2a11cc49c9", "v5.0.0"),
    "actions/deploy-pages": ("368f82528645a54fb793d4d04e342629a3f51346", "v5.0.1"),
}


def _uses(name: str) -> str:
    sha, release = ACTIONS[name]
    return f"uses: {name}@{sha} # {release}"


def workflow() -> str:
    """Return `.github/workflows/pages.yml`, whole."""
    return "\n".join(
        [
            "# Written by studyforge's execution skill (standalone). Regenerate it; never edit it.",
            "# Builds this repository's read-only preview from this tree on every push to main",
            "# and deploys it to GitHub Pages. Switch it on once: Settings, Pages, Source:",
            '# "GitHub Actions".',
            "name: Pages",
            "",
            "on:",
            "  push:",
            "    branches: [main]",
            "  workflow_dispatch:",
            "",
            "permissions:",
            "  contents: read",
            "  pages: write",
            "  id-token: write",
            "",
            "concurrency:",
            "  group: pages",
            "  cancel-in-progress: false",
            "",
            "jobs:",
            "  build:",
            "    runs-on: ubuntu-latest",
            "    timeout-minutes: 10",
            "    steps:",
            "      - name: Check out the course",
            f"        {_uses('actions/checkout')}",
            "        with:",
            "          persist-credentials: false",
            "      - name: Build the read-only preview",
            f"        run: python3 {BUILDER_DIR}/{SCRIPT} . {SITE}",
            "      - name: Configure Pages",
            f"        {_uses('actions/configure-pages')}",
            "      - name: Upload the preview",
            f"        {_uses('actions/upload-pages-artifact')}",
            "        with:",
            f"          path: {SITE}",
            "  deploy:",
            "    needs: build",
            "    runs-on: ubuntu-latest",
            "    timeout-minutes: 10",
            "    environment:",
            "      name: github-pages",
            "      url: ${{ steps.deployment.outputs.page_url }}",
            "    steps:",
            "      - name: Deploy to GitHub Pages",
            "        id: deployment",
            f"        {_uses('actions/deploy-pages')}",
            "",
        ]
    )


def builder() -> dict[str, bytes]:
    """Return the builder's files by their path in the learner tree: the framework's own bytes."""
    here = Path(__file__).parent
    return {f"{BUILDER_DIR}/{one}": (here / one).read_bytes() for one in SOURCES}
