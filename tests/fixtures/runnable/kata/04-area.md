# Area

A function that measures a rectangle. The version you are given does not compile.

## Problem statement

Make `practice/broken/area.py` compile, then run its test.

## Lesson: A file that does not compile

A `break` outside a loop is refused when the file is compiled, before any test can run.

## Starting code

```python
"""Measure a rectangle."""


def area(width, height):
    """Return the area of a `width` by `height` rectangle."""
    if width < 0 or height < 0:
        break
    return width * height


if __name__ == "__main__":
    print(area(2, 3))
```
