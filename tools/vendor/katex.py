"""Re-vendor KaTeX into `src/studyforge/render/assets/`, reproducibly.

    npm pack katex@0.16.22                      # or fetch the registry tarball by hand
    python3 tools/vendor/katex.py katex-0.16.22.tgz

The tarball must match `INTEGRITY`, the npm registry's sha512 for that version, or nothing is
written. It writes `katex.min.js` and `katex.min.css`, each with a vendoring header and nothing
else changed, `katex.LICENSE`, and the 20 woff2 faces into `katex/`. It prints each face's sha256
in the form of the `FACES` pins of `studyforge.render.page.math`, which the build checks before it
inlines a face into the stylesheet it writes, so a page opened from a file (R8) draws KaTeX's
faces with no request.
"""

from __future__ import annotations

import base64
import hashlib
import re
import sys
import tarfile
from pathlib import Path

VERSION = "0.16.22"
INTEGRITY = "sha512-XCHRdUw4lf3SKBaJe4EvgqIuWwkPSo9XoeO8GjQW94Bp7TWv9hNhzZjZ+OH9yf1UmLygb7DIT5GSFQiyt16zYg=="
ASSETS = Path(__file__).resolve().parents[2] / "src" / "studyforge" / "render" / "assets"
FACE = re.compile(r"src:url\(fonts/(KaTeX_[A-Za-z0-9_-]+)\.woff2\)")

JS_HEADER = f"""/* KaTeX {VERSION} -- katex.org -- MIT, see katex.LICENSE beside this file.
   VENDORED, UNMODIFIED apart from this header. Do not edit: re-vendor with
   `npm pack katex@{VERSION}` and take dist/katex.min.js. */
"""
CSS_HEADER = f"""/* KaTeX {VERSION} -- katex.org -- MIT, see katex.LICENSE beside this file.
   VENDORED, UNMODIFIED apart from this header. Do not edit: re-vendor with
   `npm pack katex@{VERSION}` and take dist/katex.min.css, and dist/fonts/*.woff2 into katex/.
   The build inlines each face this file names, so no page requests a font file. */
"""


def integrity(data: bytes) -> str:
    return "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode()


def main(argv: list[str]) -> int:
    tarball = Path(argv[1])
    raw = tarball.read_bytes()
    if integrity(raw) != INTEGRITY:
        print("refused: the tarball is not KaTeX " + VERSION + " as the npm registry published it")
        return 1
    with tarfile.open(tarball) as archive:

        def read(name: str) -> bytes:
            return archive.extractfile(f"package/{name}").read()

        css = read("dist/katex.min.css").decode("utf-8")
        faces = sorted({match.group(1) for match in FACE.finditer(css)})
        if not faces or len(FACE.findall(css)) != css.count("@font-face"):
            print("refused: the stylesheet's font sources did not have the expected shape")
            return 1
        (ASSETS / "katex").mkdir(exist_ok=True)
        for face in faces:
            content = read(f"dist/fonts/{face}.woff2")
            (ASSETS / "katex" / f"{face}.woff2").write_bytes(content)
            print(f'    "{face}.woff2": "{hashlib.sha256(content).hexdigest()}",')
        (ASSETS / "katex.min.css").write_text(
            CSS_HEADER + css.rstrip("\n") + "\n", encoding="utf-8", newline="\n"
        )
        script = read("dist/katex.min.js").decode("utf-8")
        (ASSETS / "katex.min.js").write_text(
            JS_HEADER + script.rstrip("\n") + "\n", encoding="utf-8", newline="\n"
        )
        (ASSETS / "katex.LICENSE").write_bytes(read("LICENSE"))
    print(f"vendored KaTeX {VERSION}: {len(faces)} faces")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
