"""Print the plan for this season's lots and the bank's standard 10 kg crate."""

from pathlib import Path

from seedcrate.solve import plan

if __name__ == "__main__":
    print(plan(Path(__file__).resolve().parent / "data" / "lots.csv", 10))
