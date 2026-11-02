"""Toy shot model for the page template.

Not a published expected-goals model, and not fit to any match file.
Paper pages replace this module. Keep the Pyodide cells in index.qmd
in sync with INTERCEPT, DEFAULT_PENALTY, ANGLE_WEIGHT, and DEFAULT_ANGLE_RAD.
"""

import math

INTERCEPT = 1.15
DEFAULT_PENALTY = 0.09
ANGLE_WEIGHT = 1.4
DEFAULT_ANGLE_RAD = 0.4


def toy_xg(distance_m, penalty=DEFAULT_PENALTY, angle_rad=DEFAULT_ANGLE_RAD):
    """Logistic probability. Farther shots score lower. Wider angles score higher."""
    score = INTERCEPT - penalty * distance_m + ANGLE_WEIGHT * angle_rad
    return 1.0 / (1.0 + math.exp(-score))


def main():
    value = toy_xg(18)
    print(
        f"18m, penalty {DEFAULT_PENALTY}, angle {DEFAULT_ANGLE_RAD} rad -> {value:.3f}"
    )


if __name__ == "__main__":
    main()
