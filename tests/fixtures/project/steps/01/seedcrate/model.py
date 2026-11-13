"""Choosing the lots: a 0-1 knapsack over whole kilograms, with must-ship lots fixed in."""

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


def must_ship(lots: list[Lot]) -> tuple[str, ...]:
    """The names of the lots that have to ship, in input order."""
    return tuple(lot.name for lot in lots if lot.must)


def best_selection(lots: list[Lot], capacity: int) -> tuple[str, ...]:
    """The lots the crate carries: every must-ship lot, then the best fit for the room left."""
    forced = [lot for lot in lots if lot.must]
    room = capacity - sum(lot.weight for lot in forced)
    if room < 0:
        raise ValueError("the must-ship lots alone weigh more than the crate holds")
    chosen = {lot.name for lot in forced}
    chosen |= set(knapsack([lot for lot in lots if not lot.must], room))
    return tuple(lot.name for lot in lots if lot.name in chosen)
