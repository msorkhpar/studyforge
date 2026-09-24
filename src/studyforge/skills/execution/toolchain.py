r"""Which runtimes an image carries, and how to build it — from declarations alone.

**What it does.** Joins what a corpus declared (`corpus.json`'s `runtimes`)
with what a component's contract says its image can carry, and returns the
build and tag commands with the declared set substituted into the slot the
contract left for it.

**How you use it.** `select(runtimes, contract, block="editor")` returns a
`Selection`; `Selection.document()` is the JSON a corpus keeps.

**Depends on.** `contract` for every value, and `describe` for refusals. ⛔ No
I/O, no Docker, and nothing source-specific (R1): the runtimes arrive as data
and this module never learns which corpus declared them.

## ⭐ THE SET IS THE CORPUS'S AND THE VOCABULARY IS THE COMPONENT'S

⛔ **Neither list is written here.** The corpus's is `manifest.runtimes`, whose
vocabulary is `corpus.manifest.runtimes.RUNTIMES`; the image's is the
contract's own selectable list. ⚠️ **They are not the same list and must not be
made one** — a corpus may legitimately declare a runtime an *editor* cannot
carry while the *runner* can, which is exactly what the contract's own
`not_carried` block exists to say.

⭐ **A withheld runtime is reported, never dropped in silence.** It is a real
difference between what a reader can run in the browser and what a graded
practice runs, and the reason quoted for it is the contract's own sentence.

## ⛔ A TAG IS COMPUTED, NEVER WRITTEN

⭐ The contract states that a tag is a function of the build's inputs, so a
hand-made one names nothing. ⛔ **This module emits the *command* that computes
a tag and never a tag**, and the document it writes says so — a literal tag in
a generated file is a value that was true on one host on one day.

## ⚠️ `SET_SEPARATOR` IS A HOLE IN THE CONTRACT, HELD OPEN ON PURPOSE

⛔ **The contract puts `<the declared set>` in ONE argv slot and declares
nowhere how a set is written into it.** It declares the separator for the
*tag* — sorted and joined with a hyphen — and that is a different string for a
different purpose, so it is not an answer.

⭐ **So this constant is provisional, it is a finding against the component's
contract, and a test asserts the contract still carries no key that
would settle it.** ⚠️ The day the component declares one, that test goes RED,
this constant is deleted and the value is read. ⛔ It is not a fix and it must
not be allowed to become one by being quietly forgotten.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from studyforge.archive.scrub import scrub
from studyforge.describe import describe
from studyforge.skills.execution.contract import ContractRefused, optional, require, words

#: The slot a contract's `prime.declared_by` leaves for the prime directory.
DIRECTORY_SLOT = "<directory>"

#: The slot a contract leaves in its build argv for the runtimes a consumer
#: declared. ⛔ Read from the contract's own text rather than assumed: a
#: command whose argv carries no slot is refused rather than run with the set
#: appended to whatever it happened to end with.
PLACEHOLDER = "<the declared set>"

#: ⚠️ **Provisional. See the module contract above.** How the
#: declared set is written into the one argv slot the contract leaves for it.
SET_SEPARATOR = ","

#: The contract key that would settle `SET_SEPARATOR`, named here so a test can
#: assert it is still absent rather than a reader having to remember it is.
SEPARATOR_KEY = ("runtimes", "argument_separator")


@dataclass(frozen=True, slots=True)
class Selection:
    """What one image will carry for one corpus, and the two commands for it."""

    #: What the corpus declared, sorted — the manifest's own value.
    declared: tuple[str, ...]
    #: What this image can carry of it, sorted.
    carried: tuple[str, ...]
    #: `(runtime, the contract's own reason)` for each declared runtime this
    #: image will not carry. ⭐ The reason is quoted, never composed here.
    withheld: tuple[tuple[str, str], ...]
    #: The environment variable the contract names for its image.
    image_env: str
    #: What a compose file or a run line puts where the image goes.
    image_value: str
    #: The argv that builds it, with the declared set substituted.
    build: tuple[str, ...]
    #: The argv that prints its tag, with the declared set substituted.
    tag_from: tuple[str, ...]
    #: The image label a consumer reads the set back from, once it has one.
    read_back_from: str
    #: `<block>.image.repository`, which every tag this image is built under begins with.
    repository: str
    #: `<block>.prime.declared_by`, its directory slot left open, or `None` for a
    #: block that declares no prime. ⭐ A contract before `provides` 3 declares
    #: none for the editor, and its editor is then built and recorded unprimed.
    prime_flag: str | None = None

    def primed_by(self, directory: str) -> str | None:
        """Return this image's prime flag with `directory` in its slot, or `None` for none.

        ⭐ `None` is a block that declares no prime: before `provides` 3 the
        editor's contract declares none, and its editor is built unprimed (`W466`).
        """
        if self.prime_flag is None:
            return None
        if DIRECTORY_SLOT not in self.prime_flag:
            raise ContractRefused(f"a prime.declared_by has no {DIRECTORY_SLOT} slot")
        return self.prime_flag.replace(DIRECTORY_SLOT, directory)

    def document(self) -> dict[str, object]:
        """Return the selection as a corpus keeps it: data, and no tag."""
        return {
            "declared": list(self.declared),
            "carried": list(self.carried),
            "withheld": [{"runtime": name, "why": why} for name, why in self.withheld],
            "image": {
                "env_var": self.image_env,
                "value": self.image_value,
                "read_back_from": self.read_back_from,
            },
            "build": list(self.build),
            "tag_from": list(self.tag_from),
            "no_tag_is_recorded_here": (
                "a tag is a function of the build's inputs, so a hand-written one names "
                "nothing. Run tag_from in the pinned checkout and record what it prints "
                "beside the commit the workspace pins"
            ),
        }

    def render(self) -> str:
        """Render the document as the bytes a corpus keeps, newline-terminated."""
        return json.dumps(self.document(), indent=2, ensure_ascii=False) + "\n"


def select(
    runtimes: Sequence[str], contract: Mapping[str, object], *, block: str = "editor"
) -> Selection:
    """Join a corpus's declared runtimes with one image block of a contract."""
    declared = tuple(sorted(runtimes))
    selectable = frozenset(words(contract, block, "runtimes", "selectable"))
    reasons = optional(contract, block, "runtimes", "not_carried", default={})
    if not isinstance(reasons, Mapping):
        raise ContractRefused(
            f"the contract's {scrub(block)}.runtimes.not_carried must be an object, "
            f"got {describe(reasons)}"
        )
    carried = tuple(name for name in declared if name in selectable)
    withheld = tuple(
        (name, _reason(reasons, name, block)) for name in declared if name not in selectable
    )
    return Selection(
        declared=declared,
        carried=carried,
        withheld=withheld,
        image_env=_string(contract, block, "image", "env_var"),
        image_value=_image_value(contract, block),
        build=_argv(contract, carried, block, "image", "built_by"),
        tag_from=_argv(contract, carried, block, "image", "tag_from"),
        read_back_from=_string(contract, block, "runtimes", "read_back_from"),
        repository=_string(contract, block, "image", "repository"),
        prime_flag=_prime_flag(contract, block),
    )


def _prime_flag(contract: Mapping[str, object], block: str) -> str | None:
    """Return `<block>.prime.declared_by`, or `None` when the block declares no prime."""
    flag = optional(contract, block, "prime", "declared_by")
    if flag is None:
        return None
    if not isinstance(flag, str) or not flag:
        raise ContractRefused(
            f"the contract's {scrub(block)}.prime.declared_by must be a non-empty string, "
            f"got {describe(flag)}"
        )
    return flag


def _reason(reasons: Mapping[str, object], name: str, block: str) -> str:
    """Quote the contract's own sentence for a runtime this image will not carry."""
    why = reasons.get(name)
    if isinstance(why, str) and why.strip():
        return why
    raise ContractRefused(
        f"the contract's {scrub(block)}.runtimes.selectable omits a runtime this corpus "
        f"declared and its not_carried block gives no reason for it. ⛔ A corpus is "
        f"owed the reason, and inventing one here would be this skill answering for "
        f"the component (R19)"
    )


def _image_value(contract: Mapping[str, object], block: str) -> str:
    """Return what goes where the image does: a compose interpolation or a run value.

    ⚠️ **Two spellings, because the two blocks are consumed two ways**: an
    editor is brought up by compose and a runner by a `docker run` line, and
    the contract names them apart. ⛔ Neither is composed here.
    """
    for key in ("compose_value", "run_value"):
        found = optional(contract, block, "image", key)
        if isinstance(found, str) and found:
            return found
    raise ContractRefused(
        f"the contract's {scrub(block)}.image declares neither compose_value nor run_value, "
        f"so nothing says what a consumer writes where the image goes"
    )


def _argv(
    contract: Mapping[str, object],
    carried: Sequence[str],
    *path: str,
) -> tuple[str, ...]:
    """One contract argv with the declared set substituted into its one slot."""
    argv = words(contract, *path)
    if PLACEHOLDER not in argv:
        raise ContractRefused(
            f"the contract's {scrub('.'.join(path))} leaves no slot for the declared set, "
            f"so nothing says where a consumer's runtimes go in it"
        )
    joined = SET_SEPARATOR.join(carried)
    return tuple(joined if piece == PLACEHOLDER else piece for piece in argv)


def _string(contract: Mapping[str, object], *path: str) -> str:
    """Return a required non-empty string at `path`."""
    found = require(contract, *path)
    if not isinstance(found, str) or not found:
        raise ContractRefused(
            f"the contract's {scrub('.'.join(path))} must be a non-empty string, "
            f"got {describe(found)}"
        )
    return found
