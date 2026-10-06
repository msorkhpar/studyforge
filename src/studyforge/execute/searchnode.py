r"""The search index built at build time: the vendored ranking library run once under `node`.

**What it does.** Hands the index's documents to `minisearch.js` running under `node` and returns
what `JSON.stringify(index)` wrote, the string the search part gives to `MiniSearch.loadJSON`.

**How you use it.** `search_index_builder(node)` is the `build` that
`render.pageassets.search_files` takes; `serialised(documents, options, library, node)` is what it
calls. `NODE_ON_PATH` finds `node` on `PATH`; `None` says there is none.

**Depends on.** `json`, `re`, `shutil`, `subprocess`, and `render.pageassets` for `Unbuilt`. ⭐ Here
and not beside the page reader because this package is the one that starts processes (§8.3):
`render` says what a page says, and hands the program to run to this.

## ⚠️ Without `node`, nothing breaks

No `node`, one that exits non-zero, one that is not there to run, or output that is not a
serialised index: each raises `Unbuilt` with the reason, and `search_files` writes the records as
a build always did, for the page to build. The build succeeds either way.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections.abc import Callable

from studyforge.render.pageassets import Unbuilt

#: ⭐ What `node` runs: the library, fed `{library, options, documents}` on standard input,
#: writes the serialised index on standard output.
BUILD_SCRIPT = r"""
let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  const job = JSON.parse(input);
  const module = { exports: {} };
  new Function('module', 'exports', job.library)(module, module.exports);
  const index = new module.exports(job.options);
  index.addAll(job.documents);
  process.stdout.write(JSON.stringify(index));
});
"""

#: How a serialised index ends.
SERIALISED_END = re.compile(r'"serializationVersion":\d+\}$')

#: How long `node` may take before the build falls back.
NODE_SECONDS = 600

#: Stands for "the `node` on `PATH`" where a caller names none.
NODE_ON_PATH = "on-path"


def node_program(node: str | None = NODE_ON_PATH) -> str | None:
    """The `node` to run: the one named, the one on `PATH`, or none."""
    return shutil.which("node") if node == NODE_ON_PATH else node


def serialised(
    documents: list[dict], options: dict, library: str, node: str | None = NODE_ON_PATH
) -> str:
    """The serialised index of `documents`, built by `library` under `node`.

    ⛔ Raises `Unbuilt` with the reason when there is no `node`, it fails, or what it wrote is
    not a serialised index.
    """
    program = node_program(node)
    if not program:
        raise Unbuilt("node was not found")
    job = {"library": library, "options": options, "documents": documents}
    try:
        done = subprocess.run(  # noqa: S603 - argv, no shell
            [program, "-e", BUILD_SCRIPT],
            input=json.dumps(job, ensure_ascii=False).encode("utf-8"),
            capture_output=True,
            timeout=NODE_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise Unbuilt(f"node could not be run ({type(error).__name__})") from None
    if done.returncode != 0:
        raise Unbuilt(f"node exited with status {done.returncode}")
    # ⭐ Checked by its shape, never decoded: `JSON.stringify` of an index is one object whose
    # last key is `serializationVersion`. The search part's `loadJSON` is what reads it.
    try:
        out = done.stdout.decode("utf-8")
    except ValueError:
        raise Unbuilt("node wrote no serialised index") from None
    if not (out.startswith("{") and SERIALISED_END.search(out[-64:])):
        raise Unbuilt("node wrote no serialised index")
    return out


def search_index_builder(node: str | None = NODE_ON_PATH) -> Callable[[list, dict, str], str]:
    """The `build` that precompiles a search index under `node`."""

    def build(documents: list, options: dict, library: str) -> str:
        return serialised(documents, options, library, node)

    return build
