"""The block-type coverage table, for a human. `python3 -m tests.fixture_checks`.

**What it does.** Prints, per valid corpus, how many of the eleven block types
it exercises and which required ones it does not.

**How you use it.** Run it. ⛔ It asserts nothing — the assertions live in
`tests/test_fixture_consistency.py`, and a report that could fail a build would
be a second, quieter definition of the same rule.

**Depends on.** The package.
"""

from __future__ import annotations

from tests.fixture_checks import BLOCK_FIELDS, FIXTURES, REQUIRED_TYPES, VALID, block_types


def main() -> None:
    """Print the coverage table for every valid corpus."""
    for corpus in VALID:
        counted = block_types(FIXTURES / corpus)
        print(f"\n{corpus}: {len(counted)} of {len(BLOCK_FIELDS)} block types")
        for kind in BLOCK_FIELDS:
            required = kind in REQUIRED_TYPES[corpus]
            mark = "ok " if counted.get(kind) else ("MISSING" if required else "n/a")
            print(f"  {kind:<8} {counted.get(kind, 0):>3}  {mark}")


if __name__ == "__main__":
    main()
