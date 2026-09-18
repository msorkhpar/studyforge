# Totals

A function that adds up a basket of prices. The version you are given skips one.

## Problem statement

Make `total` in `practice/fails/total.py` count every price, then run its test.

## Lesson: A test that fails

The file runs, and its grader says it is wrong until the first price is counted.

## Starting code

```python
"""Add up a basket of prices."""


def total(prices):
    """Return the sum of every price in `prices`."""
    return sum(prices[1:])


if __name__ == "__main__":
    print(total([1, 2, 3]))
```
