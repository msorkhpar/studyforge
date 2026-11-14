# Fixing a variable

A forced lot is fixed to one. The crate's planners now mark some lots as must-ship, in a new
`must` column of the lots file.

`seedcrate/model.py` gains a function that names the must-ship lots:

```python
def must_ship(lots: list[Lot]) -> tuple[str, ...]:
    """The names of the lots that have to ship, in input order."""
    return tuple(lot.name for lot in lots if lot.must)
```

`best_selection` is left to the practice: put every must-ship lot in the crate, take their weight
off the capacity, refuse a set of must-ship lots that alone weighs more than the crate holds, and
solve the smaller knapsack over the lots that are free.
