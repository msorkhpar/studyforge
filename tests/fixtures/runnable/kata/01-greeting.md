# Greeting

A function that greets someone by name, and the test that says whether it does.

## Problem statement

Make `greet` in `practice/passes/greet.py` return the greeting for any name.

```python
greet("<who>")  # returns "Hello, <who>"
```

## Lesson: A test that passes

The file as shipped already satisfies its grader, so its test passes.

## Starting code

```python
"""Greet someone by name."""


def greet(who):
    """Return the greeting for `who`."""
    return f"Hello, {who}"


if __name__ == "__main__":
    print(greet("reader"))
```
