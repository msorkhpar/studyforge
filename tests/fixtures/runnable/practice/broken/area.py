"""Measure a rectangle."""


def area(width, height):
    """Return the area of a `width` by `height` rectangle."""
    if width < 0 or height < 0:
        break
    return width * height


if __name__ == "__main__":
    print(area(2, 3))
