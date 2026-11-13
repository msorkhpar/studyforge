"""The crate report a packer reads."""

from __future__ import annotations

from seedcrate.data import Lot


def render(lots: list[Lot], chosen: tuple[str, ...], capacity: int) -> str:
    """One line per chosen lot, in input order, under the capacity and over the total value."""
    picked = [lot for lot in lots if lot.name in chosen]
    lines = [f"crate capacity: {capacity} kg"]
    lines += [f"  {lot.name:<8} {lot.weight:>3} kg {lot.value:>8.2f}" for lot in picked]
    lines.append(f"total value: {sum(lot.value for lot in picked):.2f}")
    return "\n".join(lines)
