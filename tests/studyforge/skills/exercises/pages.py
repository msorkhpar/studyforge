"""The pages `AX-07`'s three mirrors are read on, written once.

⭐ **Shared so the three test modules cannot drift about what a page is.**
⛔ Nothing here asserts anything: a helper that asserted would be a fourth
instrument nobody names.
"""

from __future__ import annotations

from pathlib import Path

from tests.support import repository_root

#: A page with three fences at two depths, so a region origin has an ancestor
#: to be tested against and a sibling section to be kept out of.
PAGE = """# Adding up

Prose the reader reads.

```java
int a = 1;
```

## Edge cases

More prose.

```java
int b = 2;
```

# Elsewhere

```
not tagged
```
"""

#: A reason is a sentence, and every fixture writes a real one.
BECAUSE = "carried by the reading floor; no exercise is built from it"


def fixture_corpus() -> Path:
    """The runnable fixture corpus — a real source with real fences and real graders."""
    return repository_root() / "tests" / "fixtures" / "runnable"


def fence_openers(text: str) -> int:
    """Count fenced blocks by an instrument of the tests' own, not the module's.

    ⛔ Deliberately naive and deliberately NOT the scan under test: it counts
    lines opening with three backticks and halves them. A fixture that needed
    more than this is a fixture that claim should be re-read on.
    """
    return sum(1 for line in text.splitlines() if line.startswith("```")) // 2


def written(root: Path, name: str, text: str) -> str:
    """Write one file into a temporary corpus and return its relative path."""
    (root / name).write_text(text, encoding="utf-8")
    return name


#: ⭐ **`W453`'s positive control**: a code-dense page with little prose. Under
#: the withdrawn length band its prose alone planned it zero; planned by its
#: aspects it gets one exercise per important idea, related ideas sharing one.
DENSE = """# Parsing a record

A record is one line of fields split by a bar.

## Reading a field

```python
def field(record, n):
    return record.split("|")[n]
```

## A missing field

```python
field("a|b", 5)  # raises IndexError
```

## A number in a field

```python
int(field("a|42", 1))
```

## Trimming

```python
field(" a |b", 0).strip()
```

## Setting up

```shell
python3 -m venv .venv
```
"""
