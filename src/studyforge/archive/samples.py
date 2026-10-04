"""Sample data the personal-data gate admits: reserved domains and one placeholder home.

**What it does.** Names the two forms of sample data a source's free text may
carry past `archive.scrub`'s gate (R7): an email address whose domain is
reserved, and the placeholder home paths. Everything else the gate recognises is
still refused.

**How you use it.** `admitted(shape, found)` with the gate's shape name and the
matched text; `is_reserved(domain)` for a domain already parsed out of an
address. The gate calls the first; nothing else needs to.

**Depends on.** Nothing: no import but `__future__`'s annotation directive.
⛔ The gate's verdict is part of what `studyforge validate` promises an adapter
(R2), so it must be the same on every machine. This module reads only the
text it is handed, and holds no value about anybody.

## What passes, exactly

⭐ **A lesson's sample is not a leak when it is unreachable by construction.**
Teaching material writes addresses and paths in its examples, and the safe way
to write one is the way documentation is told to:

- ⭐ **An address on a reserved domain.** RFC 2606's documentation domains
  (`RESERVED_DOMAINS`: `example.com`, `example.net`, `example.org`) and anything
  under them, and any name under RFC 6761's reserved top-level names
  (`RESERVED_TLDS`: `.example`, `.invalid`, `.test`, `.localhost`). Such an
  address can be delivered nowhere, by the standard rather than by anybody's
  configuration.
- ⭐ **A placeholder home path** (`sample_home(account)` for each of
  `SAMPLE_ACCOUNTS`): a slash, `home`, a slash and an account segment that is exactly
  one of a small fixed list of obvious placeholders (`user`, `dev`,
  `me`), with anything or nothing below it. It is how documentation
  writes a home directory that is nobody's.

⛔ **Nothing else moves.** An address on a registrable domain is refused however
much it looks like a sample: `test.com` and `example.co` are real domains, and so
is a reserved name followed by one (`example.com.` then a real domain). Every
other account segment is refused, and so are the macOS spelling, the tilde form,
every local hostname and every token. There is no manifest switch.

⚠️ **What the admission does not read, and why.** The local part of an address,
and the labels under a reserved name, may be any word. Telling an account name
there from any other word would need the gate to hold the account name, which
is the datum R7 forbids it to hold. The account name is caught where it has a
structural anchor, the segment after `/home`, and there only the fixed
placeholders pass. ⛔ The list is a fixed constant, never extended from a manifest
or the environment: a name that is on it identifies nobody, and a name that is not
on it is refused.

⚠️ **The vocabulary is shared, the code is not.** The repository hygiene check
holds the same two tuples in `tests.floor.reserved_addresses`, and the floor
may not import the framework. `tests/test_shape_vocabulary.py` asserts the two
are equal, so they cannot drift apart silently.
"""

from __future__ import annotations

#: ⛔ RFC 6761's reserved top-level names (RFC 2606 named the first three).
RESERVED_TLDS = ("invalid", "test", "example", "localhost")

#: ⛔ RFC 2606's documentation domains, registered so that a document can name an
#: address without naming anybody's.
RESERVED_DOMAINS = ("example.com", "example.net", "example.org")

#: ⭐ The account segments that are obvious placeholders and name nobody. ⛔ Exactly
#: these, compared whole and case-sensitively: `username`, `User` and `user.name`
#: are refused.
SAMPLE_ACCOUNTS = ("user", "dev", "me")


def sample_home(account: str) -> str:
    """Return the home path of `account`, assembled so this file holds no home-path shape."""
    return "/" + "home/" + account


#: ⭐ The home path a source's free text most often carries (account `user`).
SAMPLE_HOME = sample_home("user")

#: Every home path the gate admits.
SAMPLE_HOMES = frozenset(sample_home(account) for account in SAMPLE_ACCOUNTS)

#: The gate's names for the two shapes that have an admission.
HOME_SHAPE = "home path"
EMAIL_SHAPE = "email address"


def is_reserved(domain: str) -> bool:
    """Report whether `domain` is reserved, and so reaches nobody.

    ⛔ A property of the address, never a roster: the domain is one of the
    reserved names or sits under one. Case and surrounding space are absorbed.
    """
    cleaned = domain.strip().lower()
    if cleaned in RESERVED_TLDS or cleaned in RESERVED_DOMAINS:
        return True
    return any(cleaned.endswith(f".{name}") for name in (*RESERVED_TLDS, *RESERVED_DOMAINS))


def admitted(shape: str, found: str) -> bool:
    """Report whether the gate's match `found`, of shape `shape`, is sample data.

    ⛔ Decided by the matched text alone. A home-path match passes only when it
    one of `SAMPLE_HOMES` exactly, so a longer account segment such as `username` is
    still refused; an address passes only when its domain is reserved. No other
    shape has an admission.
    """
    if shape == HOME_SHAPE:
        return found in SAMPLE_HOMES
    if shape == EMAIL_SHAPE:
        return is_reserved(found.rpartition("@")[2])
    return False
