"""Mirror of `src/studyforge/cli/site/report.py` (R12)."""

from __future__ import annotations

from pathlib import PurePosixPath

from studyforge.cli.site.report import ALREADY_THERE, exit_code, lines
from studyforge.generate import Written
from studyforge.validate.report import INVALID, OK


def written(**parts) -> Written:
    """A `Written` with only the fields a case cares about."""
    return Written(
        **{name: tuple(PurePosixPath(p) for p in paths) for name, paths in parts.items()}
    )


def test_a_clean_build_exits_zero():
    assert exit_code(written(pages=["index.html"])) == OK


def test_any_refusal_exits_one():
    # ⛔ `1`, not `0`: R3 held, and a script that cannot tell "wrote everything"
    # from "left half of it alone" will publish a half-built site.
    assert exit_code(written(pages=["a.html"], refused=["b.html"])) == INVALID


def test_the_header_names_what_the_caller_asked_for():
    out = lines(written(), "corpus", "site")
    assert out[0] == "build corpus  into site"


def test_pages_and_assets_are_reported_together_and_sorted():
    # ⛔ Sorted (R10) and one list: the acceptance that matters is a path-for-
    # path diff against `studyforge plan`, and an order nobody can predict is
    # a diff nobody can read.
    out = lines(written(pages=["b.html", "a.html"], assets=["assets/page.css"]), "c", "s")
    assert out[1:] == ["wrote a.html", "wrote assets/page.css", "wrote b.html"]


def test_a_refusal_names_the_path_and_says_nothing_was_lost():
    out = lines(written(refused=["index.html"]), "c", "s")
    assert out[1] == f"refuse index.html  {ALREADY_THERE}"
    assert "nothing was overwritten" in out[1]


def test_every_path_it_prints_is_relative_to_the_output_root():
    # ⛔ R7: a report is the most-pasted artifact this command produces, so no
    # line may carry a directory belonging to whoever ran it.
    out = lines(written(pages=["index.html"], refused=["a/b.html"]), "corpus", "site")
    for line in out[1:]:
        assert not line.split()[1].startswith("/"), f"{line!r} carries an absolute path"
