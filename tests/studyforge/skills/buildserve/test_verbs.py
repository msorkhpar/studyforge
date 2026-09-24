"""Mirror of `src/studyforge/skills/buildserve/verbs.py` (R12): the seam agrees with the verbs.

⛔ Every argument list is parsed by that verb's OWN parser, reached through the
registered table rather than imported by name. So a verb whose interface changes
(`W230`) turns this module RED, naming the seam, before any reader runs the skill.
"""

from __future__ import annotations

import importlib
import io

import pytest

from studyforge.cli import VERBS
from studyforge.skills.buildserve import verbs
from studyforge.skills.buildserve.verbs import NotAVerb, build, call, narrate, serve, validate
from studyforge.validate.cli import UNUSABLE

CORPUS, SITE = "corpus-root", "site-directory"

LISTS = {
    "validate": validate(CORPUS),
    "validate+no-narration": validate(CORPUS, narration=False),
    "narrate": narrate(CORPUS, "a-voice"),
    "narrate+service": narrate(CORPUS, "a-voice", "http://127.0.0.1:1"),
    "build": build(CORPUS, SITE),
    "serve": serve(CORPUS, SITE),
    "serve+port": serve(CORPUS, SITE, 0),
}


def parser_of(verb: str):
    """The verb's own parser, from the module its registered callable lives in."""
    return importlib.import_module(VERBS[verb].run.__module__).build_parser()


@pytest.mark.parametrize("which", sorted(LISTS))
def test_every_list_the_seam_builds_is_accepted_by_that_verbs_own_parser(which):
    argv = LISTS[which]
    assert argv[0] in VERBS, f"{argv[0]!r} is not a registered verb"
    parsed = vars(parser_of(argv[0]).parse_args(argv[1:]))
    assert CORPUS in parsed.values()
    if SITE in argv:
        assert SITE in parsed.values(), f"{argv[0]} parsed the site into nothing"


def test_the_optional_arguments_reach_the_verb_only_when_given():
    assert vars(parser_of("serve").parse_args(serve(CORPUS, SITE, 8123)[1:]))["port"] == 8123
    given = parser_of("narrate").parse_args(LISTS["narrate+service"][1:])
    assert "http://127.0.0.1:1" in vars(given).values()
    assert len(serve(CORPUS, SITE)) < len(serve(CORPUS, SITE, 0))
    assert len(narrate(CORPUS, "v")) < len(narrate(CORPUS, "v", "u"))
    # ⭐ `W457`: only an explicit False turns narration off; None and True say nothing.
    assert vars(parser_of("validate").parse_args(LISTS["validate+no-narration"][1:])) == {
        "root": CORPUS,
        "narration": False,
    }
    assert validate(CORPUS) == validate(CORPUS, narration=True) == validate(CORPUS, narration=None)


def test_the_call_hands_the_list_to_the_registered_verb(tmp_path):
    out = io.StringIO()
    assert call(validate(str(tmp_path / "absent")), out) == UNUSABLE
    assert out.getvalue().strip().endswith("absent: not a directory")


@pytest.mark.parametrize("argv", [[], ["frobnicate", "x"]])
def test_a_list_that_names_no_verb_is_refused_without_echoing_it(argv):
    with pytest.raises(NotAVerb) as refused:
        call(argv)
    assert "frobnicate" not in str(refused.value)


def test_the_seam_is_the_only_caller_of_the_table():
    # ⭐ The contract W230's taker relies on; `test_thin.py` asserts it over the package.
    assert "VERBS" in vars(verbs)
