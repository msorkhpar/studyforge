"""Make the course shape on disk: `python3 -m tests.fixtures.claude_shape <verb> ...`.

    author  --out DIR --image IMAGE     write the source, author the exercises in IMAGE's
                                        container (`--network none`) and write the archive
    source  --out DIR                   write the source only
    read    --origin URL --out SHOTS --container NAME --corpus DIR [--steps a,b] [--live LABEL]
                                        read a running instance in a headless browser; NAME is
                                        its runner container, CORPUS the authored corpus
    export  --out DIR --corpus DIR --toolchain DIR --work DIR
                                        record, build and commit a copy of an authored corpus
                                        under WORK, then write the thin learner tree to OUT
                                        (the images it names are the ones built on this host)

⭐ `author` is the one step that needs a container: the Java and Kotlin gates run Gradle. Its
output is the corpus the tests read; ⛔ run it through the heavy-job slot, one at a time.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from tests.fixtures.claude_shape import course, export, runner


def image_id(reference: str) -> str:
    done = subprocess.run(  # noqa: S603 - argv, no shell
        ["docker", "image", "inspect", "--format", "{{.Id}}", reference],
        capture_output=True, text=True, check=True, stdin=subprocess.DEVNULL,
    )
    return done.stdout.strip()


def exporting(args) -> int:
    toolchain, work = Path(args.toolchain), Path(args.work)
    checkout = export.prepared(Path(args.corpus), work / "checkout", toolchain)
    profile = course.PROFILE
    names = {
        "serve": f"studyforge-serve:{serve_tag()}",
        "runner": f"code-server-toolchain/runner:{export.base_tag(toolchain, 'runner')}",
        "editor": f"code-server-toolchain/editor:{export.base_tag(toolchain, 'editor')}",
        "profile-runner": f"code-server-toolchain/runner-{profile}:{export.computed(toolchain, 'runner', profile)}",
        "profile-editor": f"code-server-toolchain/editor-{profile}:{export.computed(toolchain, 'editor', profile)}",
    }
    ids = {kind: image_id(name) for kind, name in names.items()}
    ids["where"] = str(work / "bases.json")
    locked = export.lock(toolchain, profile, serve_tag(), ids)
    out = Path(args.out)
    made = export.exported(checkout, out, toolchain, locked)
    print(f"exported: {len(made.written)} file(s) written by the export, {len(made.kept)} kept")
    return 0


def reading_of(args) -> int:
    from tests.fixtures.claude_shape import reading

    corpus = Path(args.corpus)
    practice = {"python": 1, "typescript": 2, "java": 3, "kotlin": 4}
    base = "level-1/01-messages/prose/unit-03"

    def place(lang: str, which: str) -> None:
        number = practice[lang]
        bundle = corpus / "exercises" / base / f"practice-{number}"
        main = json.loads((bundle / "bundle.json").read_text(encoding="utf-8"))["main_file"]
        wanted = bundle / which / main
        target = f"/work/practice/{base}/practice-{number}/{main}"
        subprocess.run(  # noqa: S603 - argv, no shell
            ["docker", "cp", str(wanted), f"{args.container}:{target}"], check=True,
            stdin=subprocess.DEVNULL,
        )

    steps = tuple(one for one in args.steps.split(",") if one) or reading.STEPS
    seen = reading.read_all(args.origin, Path(args.out), place, steps, args.live)
    (Path(args.out) / f"reading-{args.live.replace(' ', '-')}.json").write_text(
        json.dumps(seen, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return 0


def serve_tag() -> str:
    done = subprocess.run(  # noqa: S603 - argv, no shell
        [sys.executable, "docker/serve/build.py", "--print-tag"], capture_output=True, text=True,
        check=True, stdin=subprocess.DEVNULL,
    )
    return done.stdout.strip().split(":", 1)[1]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("verb", choices=("author", "source", "export", "read"))
    parser.add_argument("--out", required=True)
    parser.add_argument("--image", default="")
    parser.add_argument("--corpus", default="")
    parser.add_argument("--toolchain", default="")
    parser.add_argument("--work", default="")
    parser.add_argument("--origin", default="")
    parser.add_argument("--container", default="")
    parser.add_argument("--steps", default="")
    parser.add_argument("--live", default="without the live profile")
    args = parser.parse_args(argv)
    if args.verb == "export":
        return exporting(args)
    if args.verb == "read":
        return reading_of(args)
    root = Path(args.out)
    course.write_source(root)
    if args.verb == "source":
        return 0
    if not args.image:
        print("author needs --image, the runner image the gates run in", file=sys.stderr)
        return 2
    used = runner.InContainer(args.image)
    authored = course.author(root, used)
    for page, missed in authored.shortfalls:
        print(f"shortfall: {page}: {missed.slot} {missed.gate}: {missed.says}", file=sys.stderr)
    print(f"authored: {len(authored.written)} file(s) written, {used.runs} container run(s)")
    if authored.shortfalls:
        return 1
    course.write_archive(root)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
