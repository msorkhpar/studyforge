r"""What provides narration, where it answers, and the promise this skill was written against.

**What it does.** Names the component that synthesises narration, the loopback
address it publishes on, the `provides` promise the framework's narration client
was built against, and the two documents that hold the rest of its contract. It
also spells, once, the three sentences an operator reads when a site is silent:
what provides narration, how to have it, and what its first start fetches.

**How you use it.** `COMPONENT`, `ADDRESS`, `PROMISE` and `CONTRACT` are the
facts; `AVAILABLE`, `HOW`, `FETCHED` and the `REMEDY` that composes them are the
sentences `states` prints. ⭐ The procedure beside this package (`SKILL.md`)
states the same facts and is asserted against this module, so the document and
the printed remedy cannot drift.

**Depends on.** `cli.narrate.cli` for `DEFAULT_SERVICE`, so the address a skill
sends an operator to is the address the verb actually calls. ⛔ Nothing else:
this module opens no file, no socket and no container.

## ⭐ R1 PERMITS THIS, AND IT IS WORTH SAYING WHY

R1 is that the framework knows nothing about any **source**. `narrate-service`
is not a source: it is one of this framework's own components, installed or built
beside it, and this framework's narration client was written against
its contract. ⛔ A skill that would not name it leaves an operator to discover
that narration exists at all.

## ⛔ THIS SKILL STARTS NO CONTAINER, AND THE RULE IS NOT THIS SKILL'S

Spec §8.3: the Docker socket is never mounted into the serving process — not
behind a flag, not "only locally". ⭐ So the service is started **beside** a
site by the person running it, never **by** it, and what this module carries is
a sentence and a pointer rather than a command.

## ⛔ THE ROUTES ARE NOT COPIED HERE, AND THAT IS THE POINT

⭐ The component owns its API and versions it with `provides`, whose own
documentation asks every caller to **record the number it built against**.
`PROMISE` is that record. ⛔ Not one route, one header or one field is repeated
here: a second copy of an API is a copy that goes stale in silence, and
`CONTRACT` names the two documents that answer every other question.

## ⛔ NOTHING HERE REACHES BEYOND LOOPBACK

`ADDRESS` is loopback and the component publishes on loopback only. ⚠️ Its
**first** start is the exception an operator must be told about before it
happens rather than by a command failing in their hands, which is what
`FETCHED` says: container images are pulled and an engine model is downloaded
once. ⛔ After that nothing this framework does leaves the machine.
"""

from __future__ import annotations

from studyforge.cli.narrate.cli import DEFAULT_SERVICE

#: The component that synthesises narration. ⭐ A component of this framework,
#: never a source (R1): a client installs or builds it beside the framework.
COMPONENT = "narrate-service"

#: Where it answers. ⛔ Imported, never respelled: `studyforge narrate`'s own
#: default, so a skill cannot send an operator to a port the verb never calls.
ADDRESS = DEFAULT_SERVICE

#: ⛔ The `provides` promise the framework's narration client was built against.
#: The component's API asks every caller to record the one it built against and
#: refuses a mismatch rather than migrating it, so this is a **record**, not a
#: constraint this skill imposes. ⚠️ Read from the component's own
#: `consuming.json`; `tests/studyforge/skills/buildserve/test_narration.py`
#: re-reads it wherever the sibling is on disk.
PROMISE = 3

#: The component's own documents — everything this module deliberately does not copy.
CONTRACT = ("consuming.json", "docs/api.md")

#: What provides narration. ⭐ The sentence an operator reads first.
AVAILABLE = f"narration is provided by the {COMPONENT} component, which answers on {ADDRESS}"

#: How to have it. ⭐ A sentence the operator runs themselves: §8.3 keeps container
#: starting out of this skill, which only names the command.
HOW = (
    f"clone the {COMPONENT} repository and run docker compose up -d --build in it, "
    "or point --service (or the STUDYFORGE_NARRATE_SERVICE variable) at a running one, "
    "then run again with --voice <voice>"
)

#: ⚠️ What the first start fetches, said before it happens rather than after it fails.
FETCHED = (
    "its first start pulls container images and downloads an engine model; "
    "after that nothing leaves loopback"
)

#: The whole remedy, on one line, for every state a reachable service would settle.
REMEDY = f"{AVAILABLE}; {HOW}. {FETCHED}"
