"""Choosing the lots: a 0-1 knapsack over whole kilograms."""

from __future__ import annotations

from seedcrate.data import Lot


def knapsack(lots: list[Lot], capacity: int) -> tuple[str, ...]:
    """The names of the most valuable lots whose weights fit `capacity`, in input order."""
    if capacity < 0:
        return ()
    table: list[tuple[float, tuple[int, ...]]] = [(0.0, ())] * (capacity + 1)
    for index, lot in enumerate(lots):
        for room in range(capacity, lot.weight - 1, -1):
            value, chosen = table[room - lot.weight]
            if value + lot.value > table[room][0]:
                table[room] = (value + lot.value, chosen + (index,))
    return tuple(lots[index].name for index in sorted(table[capacity][1]))


def best_selection(lots: list[Lot], capacity: int) -> tuple[str, ...]:
    """The lots the crate carries."""
    return knapsack(lots, capacity)
