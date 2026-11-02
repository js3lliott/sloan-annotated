"""Field-goal logistic regression for Clark, Johnson, and Stimpson (2013).

The paper's Table 1 coefficients are printed below as PAPER. REFIT is the
binomial logistic fit on the grouped nflverse attempts in
``data/fg_agg_2000_2011.csv``. Pyodide cells in ``index.qmd`` repeat
``sigmoid``, ``linear_predictor``, ``probability``, ``added_points``,
``fit_logit``, ``PAPER``, and ``REFIT``.
"""

import math
import re

# Table 1, as printed. Distance is yards. Flags are 0/1.
PAPER = {
    "intercept": 5.953,
    "distance": -0.106,
    "cold": -0.341,
    "turf": 0.299,
    "altitude": 0.694,
    "precipitation": -0.280,
    "wind": -0.140,
}

# Filled from the nflverse refit. Three-decimal display is not these values.
# See fit_report.json, written by build_fg_table.py.
REFIT = {
    "intercept": 5.6139871232,
    "distance": -0.1062558424,
    "cold": -0.3468118695,
    "turf": 0.2949930939,
    "altitude": 0.6905322823,
    "precipitation": -0.2238229349,
    "wind": -0.1650584236,
}

COEF_NAMES = (
    "intercept",
    "distance",
    "cold",
    "turf",
    "altitude",
    "precipitation",
    "wind",
)

# Our precipitation words. The paper does not print its list.
PRECIP_PATTERN = r"rain|snow|shower|drizzle|sleet|flurr|storm"
COLD_CUTOFF_F = 50
WIND_CUTOFF_MPH = 10
VINATIERI_DISTANCE = 45


def sigmoid(score):
    """Probability from a log-odds score."""
    if score > 30:
        return 1.0
    if score < -30:
        return 0.0
    return 1.0 / (1.0 + math.exp(-score))


def linear_predictor(distance, cold, turf, altitude, precipitation, wind, coefs):
    """Log-odds. ``coefs`` is PAPER or REFIT."""
    return (
        coefs["intercept"]
        + coefs["distance"] * distance
        + coefs["cold"] * cold
        + coefs["turf"] * turf
        + coefs["altitude"] * altitude
        + coefs["precipitation"] * precipitation
        + coefs["wind"] * wind
    )


def probability(distance, cold, turf, altitude, precipitation, wind, coefs):
    """Make probability for one kick."""
    return sigmoid(
        linear_predictor(
            distance, cold, turf, altitude, precipitation, wind, coefs
        )
    )


def added_points(made, prob):
    """3 * (outcome - predicted probability). A miss is ``made`` = 0."""
    return 3.0 * (made - prob)


def _solve(matrix, rhs):
    """Solve a square linear system. ``matrix`` is copied."""
    size = len(rhs)
    rows = [list(matrix[i]) + [rhs[i]] for i in range(size)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(rows[row][col]))
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        if scale == 0:
            raise ZeroDivisionError("singular logistic Hessian")
        for j in range(col, size + 1):
            rows[col][j] /= scale
        for row in range(size):
            if row == col:
                continue
            factor = rows[row][col]
            for j in range(col, size + 1):
                rows[row][j] -= factor * rows[col][j]
    return [rows[i][size] for i in range(size)]


def fit_logit(groups):
    """Binomial logistic regression by Newton steps.

    Each group is ``(distance, cold, turf, altitude, precipitation, wind,
    made, n)``. ``made`` is the number of makes and ``n`` is the number of
    attempts. Returns coefficients in ``COEF_NAMES`` order, then standard
    errors in that same order.
    """
    width = 7
    beta = [0.0] * width
    hessian = None
    for _ in range(40):
        hessian = [[0.0] * width for _ in range(width)]
        gradient = [0.0] * width
        for dist, cold, turf, alt, precip, wind, made, n in groups:
            design = (1.0, float(dist), float(cold), float(turf), float(alt), float(precip), float(wind))
            score = 0.0
            for b_i, x_i in zip(beta, design):
                score += b_i * x_i
            prob = sigmoid(score)
            weight = n * prob * (1.0 - prob)
            residual = made - n * prob
            for i in range(width):
                gradient[i] += residual * design[i]
                if weight == 0.0:
                    continue
                for j in range(width):
                    hessian[i][j] += weight * design[i] * design[j]
        step = _solve(hessian, gradient)
        beta = [b_i + s_i for b_i, s_i in zip(beta, step)]
        if max(abs(s_i) for s_i in step) < 1e-12:
            break
    standard_errors = []
    for i in range(width):
        unit = [0.0] * width
        unit[i] = 1.0
        column = _solve(hessian, unit)
        variance = column[i]
        standard_errors.append(math.sqrt(variance) if variance > 0 else float("nan"))
    return beta, standard_errors


def is_turf(surface, stadium=None):
    """1 if the surface counts as artificial turf on this page.

    nflverse labels Heinz Field, 2003–2009, as ``dessograss`` (201 attempts).
    This page classifies that label as grass, not turf. Steelers.com, 11 Feb
    2008, calls the surface DD GrassMaster, "a 97 percent natural grass surface
    and root system stabilized by synthetic fibers":
    https://www.steelers.com/news/steelers-will-continue-to-play-on-grass-at-heinz-field-959603
    """
    label = surface or "grass"
    if label == "dessograss" and stadium in (None, "Heinz Field"):
        return 0
    return int(label != "grass")


def flag_attempt(
    temp,
    wind,
    roof,
    surface,
    home_team,
    game_id,
    weather,
    cold_cutoff=COLD_CUTOFF_F,
    stadium=None,
):
    """Six flags for one kick. Precipitation words are this page's list."""
    outdoors = roof in ("outdoors", "open")
    cold = int(outdoors and temp is not None and temp < cold_cutoff)
    turf = is_turf(surface, stadium)
    altitude = int(home_team == "DEN" or game_id == "2005_04_SF_ARI")
    text = (weather or "").lower()
    has_keyword = re.search(PRECIP_PATTERN, text) is not None
    precipitation = int(outdoors and has_keyword and "chance" not in text)
    windy = int(outdoors and wind is not None and wind >= WIND_CUTOFF_MPH)
    return {
        "cold": cold,
        "turf": turf,
        "altitude": altitude,
        "precipitation": precipitation,
        "wind": windy,
    }


def load_groups(path):
    """Read the committed aggregate. Columns match ``DATA.md``."""
    groups = []
    with open(path, encoding="utf-8") as handle:
        header = handle.readline()
        if "dist" not in header:
            raise ValueError("unexpected aggregate header: " + header.strip())
        for line in handle:
            dist, cold, turf, alt, precip, wind, made, n = line.strip().split(",")
            groups.append(
                (
                    float(dist),
                    int(cold),
                    int(turf),
                    int(alt),
                    int(precip),
                    int(wind),
                    int(made),
                    int(n),
                )
            )
    return groups


def main():
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "fg_agg_2000_2011.csv"
    groups = load_groups(path)
    beta, standard_errors = fit_logit(groups)
    print("attempts", sum(group[-1] for group in groups))
    for name, estimate, error in zip(COEF_NAMES, beta, standard_errors):
        print(f"{name:16} {estimate:.6f}  SE {error:.4f}  stored {REFIT[name]:.6f}")
        if abs(estimate - REFIT[name]) > 5e-5:
            raise SystemExit(f"{name} drifted from REFIT")
    snow = probability(45, 1, 0, 0, 1, 1, REFIT)
    mild = probability(45, 0, 0, 0, 0, 0, REFIT)
    print(f"Vinatieri flags, refit {snow:.4f}")
    print(f"mild, refit {mild:.4f}")
    print(f"lift {mild - snow:.4f}")


if __name__ == "__main__":
    main()
