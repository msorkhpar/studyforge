"""Mirror of `src/studyforge/corpus/media/__init__.py` (R12)."""

from __future__ import annotations

import studyforge.corpus.media as package
from studyforge.corpus.media import measure, require_committable, verdict_for


def test_the_package_exports_the_three_steps_a_caller_takes():
    # ⭐ Measure, decide, act — the sequence the contract states, reachable
    # from the package so no caller has to know which module holds which.
    for name in ("measure", "verdict_for", "ignore_lines", "require_committable"):
        assert name in package.__all__
        assert callable(getattr(package, name))


def test_everything_exported_exists():
    for name in package.__all__:
        assert hasattr(package, name), name


def test_the_export_list_is_sorted():
    # ⛔ R10's habit, and a diff that does not depend on where a name was added.
    assert package.__all__ == sorted(package.__all__)


def test_the_package_reads_no_manifest_of_its_own():
    # ⛔ The policy is handed in, never loaded here: this package is given what
    # `corpus.json` said, so a caller cannot end up with two readings of one
    # document. Asserted on the seam rather than on prose.
    import inspect

    source = "".join(
        inspect.getsource(module) for module in (package.footprint, package.verdict, package.errors)
    )
    assert "corpus.manifest import load" not in source
    assert "MANIFEST_FILENAME" not in source


def test_a_full_pass_from_disk_to_a_decision(tmp_path):
    # ⭐ The whole contract in one run: files on disk, the corpus's own policy,
    # a verdict, and a build that is allowed to continue.
    from studyforge.address import Address
    from studyforge.corpus.manifest import DEFAULT_MEDIA
    from studyforge.corpus.placement import profile_for

    unit = profile_for("tree").unit(Address.of("basics", "01-intro"), 1, "Intro")
    clip = tmp_path / unit.audio / "u-1-s1-abcd1234.mp3"
    clip.parent.mkdir(parents=True)
    clip.write_bytes(b"x" * 4096)

    verdict = verdict_for(DEFAULT_MEDIA, measure(tmp_path, [unit]))
    assert verdict.footprint.total_bytes == 4096
    assert verdict.commits is True
    require_committable(verdict)
