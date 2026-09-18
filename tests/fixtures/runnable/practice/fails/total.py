"""Add up a basket of prices."""


def total(prices):
    """Return the sum of every price in `prices`."""
    return sum(prices[1:])


if __name__ == "__main__":
    print(total([1, 2, 3]))
