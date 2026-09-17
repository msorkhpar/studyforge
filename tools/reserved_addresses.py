"""`W310`: the RESERVED-ADDRESS vocabulary — ONE list, read by two policies that never meet.

**What it does.** Names the addresses that are unreachable BY CONSTRUCTION and therefore
identify nobody: RFC 6761's reserved TLDs and RFC 2606's documentation domains. ⛔ It holds
the VOCABULARY and nothing else — no verdict, no message, no exit code. What a caller DOES
with a reserved address is that caller's POLICY, and the two callers do different things.

**How you use it.** `is_reserved(domain)` answers the membership question for a domain the
caller has already parsed; `alternation(names)` renders the same vocabulary as a regular
expression fragment, for a caller that must find one INSIDE text and composes its own
grammar around it. ⭐ Both read the tuples below at CALL time, so moving the vocabulary
moves every reading derived from it — which is what the mirror plants.

**Depends on.** Nothing: no import but `__future__`'s annotation directive. ⛔ That is a
CONTRACT and not an accident. `tools/mergegate.py` imports neither `studyforge` nor
`tools.quality`, so that a tree too broken to import is still one whose merge is REFUSED
rather than one that crashes the gate — and this module sits on that import path, through
`tools.authorship`. ⚠️ **A dependency added here is a dependency added to the merge path.**

## ⛔ THE TWO POLICIES, AND WHY SHARING A LIST IS NOT SHARING A VERDICT

⭐ **Ruling 47's shape, cited rather than re-derived: one vocabulary, two policies.**

- ⛔ `tools.authorship` refuses a merge whose commits CROSS OFFICES. To it, a reserved
  address means *this line is an OFFICE's*, so the line is COUNTED.
- ⛔ `tools.quality.personal_data.shapes` refuses personal data in a tracked file. To it,
  a reserved address means *this leaks nobody*, so the address is EXEMPT.

⛔ **They agree on what is RESERVED and on nothing else.** ⚠️ A change that made one accept
what the other accepts would be this module built wrong. ⭐ The floor also exempts this
project's own attribution trailer, which is at a REAL domain and is therefore NOT here: it
is exempt because every commit carries it, not because it identifies nobody. ⛔ Putting it
in this file would tell the MERGE PATH that a real domain is an office's, which is exactly
the widening `W310` must not become.

## ⛔ WHY A MODULE, AND NOT A TABLE IN A DOCUMENT

⚠️ **This repository's OTHER shared vocabulary is a table in a document that two tests
read** — one side asserts its column, the other asserts its own, and neither imports the
other. ⛔ **That form was FORCED rather than preferred:** Ruling 31 forbids `tools/quality`
from importing the framework, so those two sides cannot share code at all and settle for
sharing evidence.

⭐ **This seam has no such wall.** `tools/quality` already imports a sibling top-level
`tools` package, and the direction that is forbidden here runs the other way: the merge path
may not reach the FLOOR. Both sides may reach a module that reaches neither. ⛔ **So the
stronger instrument is available and is the one taken: a shared table makes a divergence
DETECTABLE, a shared module makes it IMPOSSIBLE.**

⛔ **And data on DISK would have cost the merge path the property this row must not spend.**
A JSON file read at import is one more way for the gate to CRASH on a tree whose files are
missing, unreadable or malformed — which is the failure `tools/mergegate.py` exists to turn
into a refusal. ⭐ Literals in a module are read by an import that already had to succeed.
"""

from __future__ import annotations

#: ⛔ RFC 6761's reserved TLDs. An address under one of these cannot be delivered anywhere,
#: by the standard rather than by anybody's configuration.
RESERVED_TLDS = ("invalid", "test", "example", "localhost")

#: ⛔ RFC 2606's documentation domains. Registered so that documents can name an address
#: without naming a person's, and reachable by nobody.
RESERVED_DOMAINS = ("example.com", "example.net", "example.org")


def is_reserved(domain: str) -> bool:
    """Report whether `domain` is reserved — unreachable by construction, so nobody's.

    ⛔ **A property of the ADDRESS, never a roster.** It knows no office's name, no
    person's and no machine's: it asks only whether the domain IS one of the reserved
    names, or sits UNDER one. ⚠️ Case and surrounding space are the caller's sloppiness
    rather than the caller's meaning, so both are absorbed here.
    """
    cleaned = domain.strip().lower()
    if not cleaned:
        return False
    if cleaned in RESERVED_TLDS or cleaned in RESERVED_DOMAINS:
        return True
    return any(cleaned.endswith(f".{name}") for name in (*RESERVED_TLDS, *RESERVED_DOMAINS))


def alternation(names: tuple[str, ...]) -> str:
    """Return `names` as a regex alternation, longest first, with every dot escaped.

    ⛔ **THE VOCABULARY RENDERED FOR A REGEX READER, AND NEVER A GRAMMAR.** It carries no
    `@`, no local part, no subdomain prefix and no anchor — ⚠️ because *where a reserved
    name may sit inside a domain* is the CALLER's policy, and the two callers answer it
    differently: one parses an address and tests the suffix, the other must find a domain
    inside free text and owns its own boundaries. ⛔ A grammar returned from here would be
    this module deciding a policy for both of them.

    ⭐ Longest first, so a caller that anchors the end is offered the longer parse before
    the shorter one. ⚠️ Either parse names a reserved address, so the order is a courtesy
    to whoever reads the compiled pattern rather than a correctness condition.
    """
    ordered = sorted(names, key=len, reverse=True)
    return "|".join(name.replace(".", r"\.") for name in ordered)
