"""Re-vendor Mermaid into `src/studyforge/render/assets/`, reproducibly.

    npm pack mermaid@11.4.1                     # or fetch the registry tarball by hand
    python3 tools/vendor/mermaid.py mermaid-11.4.1.tgz

The tarball must match `INTEGRITY`, the npm registry's sha512 for that version, or nothing is
written. It writes `mermaid.min.js` (the single-file IIFE build, `dist/mermaid.min.js`) with a
vendoring header and nothing else changed, and `mermaid.LICENSE`, and prints the sha256 of the
bundle as the registry shipped it, which `studyforge.render.page.diagram.SHA256` pins.
"""

from __future__ import annotations

import base64
import hashlib
import sys
import tarfile
from pathlib import Path

VERSION = "11.4.1"
INTEGRITY = (
    "sha512-Mb01JT/x6CKDWaxigwfZYuYmDZ6xtrNwNlidKZwkSrDaY9n90"
    "tdrJTV5Umk+wP1fZscGptmKFXHsXMDEVZ+Q6A=="
)
ASSETS = Path(__file__).resolve().parents[2] / "src" / "studyforge" / "render" / "assets"

HEADER = f"""/* Mermaid {VERSION} -- mermaid.js.org -- MIT, see mermaid.LICENSE beside this file.
   VENDORED, UNMODIFIED apart from this header. Do not edit: re-vendor with
   `npm pack mermaid@{VERSION}` and take dist/mermaid.min.js, checked against the
   registry's sha512. The bundle carries its own dependencies under their licences. */
"""


def integrity(data: bytes) -> str:
    return "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode()


def main(argv: list[str]) -> int:
    tarball = Path(argv[1])
    raw = tarball.read_bytes()
    if integrity(raw) != INTEGRITY:
        print(f"refused: the tarball is not Mermaid {VERSION} as the npm registry published it")
        return 1
    with tarfile.open(tarball) as archive:

        def read(name: str) -> bytes:
            return archive.extractfile(f"package/{name}").read()

        bundle = read("dist/mermaid.min.js")
        licence = read("LICENSE")
    if b"MIT License" not in licence:
        print("refused: the package's LICENSE is not the MIT licence")
        return 1
    script = bundle.decode("utf-8")
    (ASSETS / "mermaid.min.js").write_text(
        HEADER + script.rstrip("\n") + "\n", encoding="utf-8", newline="\n"
    )
    (ASSETS / "mermaid.LICENSE").write_bytes(licence)
    print(f'SHA256 = "{hashlib.sha256(bundle).hexdigest()}"')
    print(f"vendored Mermaid {VERSION}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
