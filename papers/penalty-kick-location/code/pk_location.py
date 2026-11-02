"""Penalty-kick location: the 2x2 game, the statistical game, and Table 2.

The Pyodide cells in index.qmd repeat these formulas. They have to run
without mounting this file. If a coefficient or a payoff changes, change
it here and in the cell.

This module does not download or store the authors' CSV. Pass the rows in.
The pinned file is pk_data_shotlevel_chrono.csv at commit ff98e29.
"""

import math
import random

# Table 1 payoffs to the taker. The keeper's payoff is the complement.
# Equation 3 on page 4 is printed as 7*p, which does not solve to 1/4.
# These four numbers are the table, and they do.
CENTER_VS_STAY = 0.3
CENTER_VS_DIVE = 0.9
CORNER_VS_DIVE = 0.7
DEFAULT_CORNER_VS_STAY = 0.9

STAT_MEAN_CORNER = 0.8
STAT_MEAN_CENTER = 0.75
DEFAULT_STAT_SD = 0.05
STAT_SIM_N = 100_000
STAT_SIM_SEED = 20251395

SUBSET_A = ("Top Left", "Bottom Left", "Top Right", "Bottom Right")
SUBSET_B = (
    "Top Middle Left",
    "Bottom Middle Left",
    "Top Middle Right",
    "Bottom Middle Right",
)

# Printed Model (1) coefficients, for the indifference slope the paper states.
PAPER_INTERCEPT = -0.794
PAPER_CONVERSION = 1.492
PAPER_OFF_TARGET = -0.477


def mixed_equilibrium(corner_vs_stay=DEFAULT_CORNER_VS_STAY):
    """Mixed equilibrium of Table 1.

    p is the taker's probability of shooting center. q is the keeper's
    probability of staying center. value_taker is the taker's equilibrium
    conversion rate. At the paper's payoffs all three are 1/4, 1/4, and 3/4.
    """
    a = CENTER_VS_STAY
    b = CENTER_VS_DIVE
    c = corner_vs_stay
    d = CORNER_VS_DIVE
    denom = a - c - b + d
    if abs(denom) < 1e-12:
        raise ValueError("payoffs do not leave the opponent indifferent")
    p_shoot_center = (d - c) / denom
    q_stay_center = (d - b) / denom
    if abs(p_shoot_center) < 1e-12:
        p_shoot_center = 0.0
    if abs(q_stay_center) < 1e-12:
        q_stay_center = 0.0
    value_taker = a * q_stay_center + b * (1.0 - q_stay_center)
    return {
        "p_shoot_center": p_shoot_center,
        "q_stay_center": q_stay_center,
        "value_taker": value_taker,
        "value_keeper": 1.0 - value_taker,
    }


def analytic_corner_share(
    sd=DEFAULT_STAT_SD,
    mean_corner=STAT_MEAN_CORNER,
    mean_center=STAT_MEAN_CENTER,
):
    """P(corner draw > center draw) for independent normals with a shared SD."""
    if sd <= 0:
        raise ValueError("sd must be positive")
    z = (mean_corner - mean_center) / (sd * math.sqrt(2.0))
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def simulate_statistical_game(
    n=STAT_SIM_N,
    sd=DEFAULT_STAT_SD,
    seed=STAT_SIM_SEED,
    mean_corner=STAT_MEAN_CORNER,
    mean_center=STAT_MEAN_CENTER,
):
    """One seeded sample of the statistical game.

    Each kick draws two conversion rates and takes the larger one.
    The paper used a billion kicks. The page uses 100,000.
    """
    rng = random.Random(seed)
    corner_n = 0
    center_n = 0
    corner_sum = 0.0
    center_sum = 0.0
    for _ in range(n):
        corner = rng.gauss(mean_corner, sd)
        center = rng.gauss(mean_center, sd)
        if corner > center:
            corner_n += 1
            corner_sum += corner
        else:
            center_n += 1
            center_sum += center
    return {
        "n": n,
        "sd": sd,
        "corner_share": corner_n / n,
        "corner_conversion": corner_sum / corner_n if corner_n else None,
        "center_conversion": center_sum / center_n if center_n else None,
        "analytic_corner_share": analytic_corner_share(sd, mean_corner, mean_center),
    }


def _solve(xtx, xty):
    """Solve xtx beta = xty by Gaussian elimination. xtx is copied."""
    p = len(xty)
    a = [xtx[i][:] + [xty[i]] for i in range(p)]
    for col in range(p):
        pivot = max(range(col, p), key=lambda r: abs(a[r][col]))
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        if abs(scale) < 1e-15:
            raise ValueError("singular design")
        for j in range(col, p + 1):
            a[col][j] /= scale
        for row in range(p):
            if row == col:
                continue
            factor = a[row][col]
            for j in range(col, p + 1):
                a[row][j] -= factor * a[col][j]
    return [a[i][p] for i in range(p)]


def ordinary_least_squares(y, columns):
    """OLS with an intercept. columns is a list of predictor lists.

    Returns coefficients in the order intercept, then each column,
    plus the classical standard errors, R-squared, adjusted R-squared,
    residual standard error, residual degrees of freedom, and the F statistic.
    """
    n = len(y)
    p = 1 + len(columns)
    xtx = [[0.0] * p for _ in range(p)]
    xty = [0.0] * p
    for i in range(n):
        row = [1.0] + [col[i] for col in columns]
        for a in range(p):
            xty[a] += row[a] * y[i]
            for b in range(p):
                xtx[a][b] += row[a] * row[b]
    beta = _solve(xtx, xty)
    resid = []
    for i in range(n):
        row = [1.0] + [col[i] for col in columns]
        fitted = sum(beta[j] * row[j] for j in range(p))
        resid.append(y[i] - fitted)
    rss = sum(e * e for e in resid)
    ybar = sum(y) / n
    tss = sum((v - ybar) ** 2 for v in y)
    df = n - p
    r2 = 1.0 - rss / tss
    adj = 1.0 - (1.0 - r2) * (n - 1) / df
    sigma2 = rss / df
    identity = [[1.0 if i == j else 0.0 for j in range(p)] for i in range(p)]
    se = []
    for j in range(p):
        column = _solve(xtx, [identity[i][j] for i in range(p)])
        se.append(math.sqrt(sigma2 * column[j]))
    f_stat = ((tss - rss) / (p - 1)) / (rss / df)
    return {
        "n": n,
        "coefficients": beta,
        "std_errors": se,
        "r2": r2,
        "adj_r2": adj,
        "residual_se": math.sqrt(sigma2),
        "df": df,
        "f": f_stat,
        "mse": rss / n,
    }


def _as_float(row, key):
    return float(row[key])


def fit_model(kicks, squared=False):
    """Table 2. y is prop_shots_other. Predictors are the leave-one-out columns."""
    y = [_as_float(row, "prop_shots_other") for row in kicks]
    conversion = [_as_float(row, "conversion_rate_other") for row in kicks]
    off_target = [_as_float(row, "prop_nc_missed_other") for row in kicks]
    columns = [conversion, off_target]
    names = ["intercept", "conversion", "off_target"]
    if squared:
        columns.append([v * v for v in conversion])
        names.append("conversion_squared")
    fit = ordinary_least_squares(y, columns)
    fit["names"] = names
    named = {
        name: {"coef": fit["coefficients"][i], "se": fit["std_errors"][i]}
        for i, name in enumerate(names)
    }
    fit["named"] = named
    if not squared:
        conv = named["conversion"]["coef"]
        off = named["off_target"]["coef"]
        # Off-target = 1 - on-target given a miss. The slope of an
        # indifference line in (conversion, on-target) is coef_conv / coef_off,
        # which is negative. The paper reports the absolute value, 3.12.
        fit["tradeoff"] = abs(conv / off)
        fit["tradeoff_other_way"] = abs(off / conv)
    return fit


def predict_model1(conversion, off_target, fit=None):
    """Shot-share prediction from Model (1).

    With no fit, uses the paper's rounded coefficients from equation 7.
    """
    if fit is None:
        intercept = PAPER_INTERCEPT
        b_conv = PAPER_CONVERSION
        b_off = PAPER_OFF_TARGET
    else:
        named = fit["named"]
        intercept = named["intercept"]["coef"]
        b_conv = named["conversion"]["coef"]
        b_off = named["off_target"]["coef"]
    return intercept + b_conv * conversion + b_off * off_target


def partition_counts(kicks):
    """Shots, makes, saves, and misses by the eight goal cells."""
    counts = {}
    for row in kicks:
        name = row["Partition"]
        slot = counts.setdefault(name, {"shots": 0, "makes": 0, "saves": 0, "misses": 0})
        slot["shots"] += 1
        slot["makes"] += int(row["Made"])
        slot["saves"] += int(row["Save"])
        slot["misses"] += int(row["Missed Goal"])
    return counts


def top_bottom_rates(kicks):
    """Page 9. Top cells miss the frame more and are saved less."""
    counts = partition_counts(kicks)
    out = {}
    for label, names in (
        ("top", [name for name in counts if name.startswith("Top")]),
        ("bottom", [name for name in counts if name.startswith("Bottom")]),
    ):
        shots = sum(counts[name]["shots"] for name in names)
        saves = sum(counts[name]["saves"] for name in names)
        misses = sum(counts[name]["misses"] for name in names)
        out[label] = {
            "shots": shots,
            "saves": saves,
            "misses": misses,
            "miss_rate": misses / shots,
            "save_rate": saves / shots,
        }
    return out


def pearson(xs, ys):
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    return num / (den_x * den_y)


def subset_correlations(counts):
    """Volume against conversion, on the four corner cells and the four middle cells."""

    def series(names):
        shots = [counts[name]["shots"] for name in names]
        conversion = [counts[name]["makes"] / counts[name]["shots"] for name in names]
        return pearson(shots, conversion)

    return {"subset_a": series(SUBSET_A), "subset_b": series(SUBSET_B)}


def lasso_path_point(kicks, lam, iters=400):
    """Gaussian lasso on standardized predictors. Intercept is not penalized.

    The objective matches glmnet and scikit-learn: RSS / (2n) + lam * L1.
    Coefficients are returned on the original scale of the two Model (1) predictors.
    """
    y = [_as_float(row, "prop_shots_other") for row in kicks]
    raw = [
        [_as_float(row, "conversion_rate_other") for row in kicks],
        [_as_float(row, "prop_nc_missed_other") for row in kicks],
    ]
    n = len(y)
    means = [sum(col) / n for col in raw]
    scales = []
    standardized = []
    for col, mean in zip(raw, means):
        var = sum((v - mean) ** 2 for v in col) / n
        scale = math.sqrt(var)
        scales.append(scale)
        standardized.append([(v - mean) / scale for v in col])
    ybar = sum(y) / n
    centered = [v - ybar for v in y]
    beta = [0.0, 0.0]
    for _ in range(iters):
        for j in (0, 1):
            rho = 0.0
            other = 1 - j
            column = standardized[j]
            other_col = standardized[other]
            other_b = beta[other]
            for i in range(n):
                rho += column[i] * (centered[i] - other_col[i] * other_b)
            z = rho / n
            if z > lam:
                beta[j] = z - lam
            elif z < -lam:
                beta[j] = z + lam
            else:
                beta[j] = 0.0
    original = [beta[j] / scales[j] for j in (0, 1)]
    intercept = ybar - sum(original[j] * means[j] for j in (0, 1))
    rss = 0.0
    for i in range(n):
        fitted = intercept + original[0] * raw[0][i] + original[1] * raw[1][i]
        err = y[i] - fitted
        rss += err * err
    return {
        "lambda": lam,
        "intercept": intercept,
        "conversion": original[0],
        "off_target": original[1],
        "mse": rss / n,
    }


def drop_one_partition(kicks):
    """Refit Model (1) after removing each goal cell, and record the tradeoff.

    Leave-one-out columns are rebuilt on the kicks that remain, so a dropped
    cell no longer sits inside the other rows' expectations.
    """
    counts = partition_counts(kicks)
    out = []
    for dropped in counts:
        kept = [row for row in kicks if row["Partition"] != dropped]
        rebuilt = _rebuild_leave_one_out(kept)
        fit = fit_model(rebuilt, squared=False)
        out.append(
            {
                "dropped": dropped,
                "n": len(kept),
                "tradeoff": fit["tradeoff"],
                "r2": fit["r2"],
            }
        )
    return out


def _rebuild_leave_one_out(kicks):
    counts = partition_counts(kicks)
    n = len(kicks)
    rebuilt = []
    for row in kicks:
        slot = counts[row["Partition"]]
        made = int(row["Made"])
        save = int(row["Save"])
        miss = int(row["Missed Goal"])
        failures = (slot["saves"] + slot["misses"]) - (save + miss)
        other = {
            "Partition": row["Partition"],
            "Made": row["Made"],
            "Save": row["Save"],
            "Missed Goal": row["Missed Goal"],
            "conversion_rate_other": (slot["makes"] - made) / (slot["shots"] - 1),
            "prop_nc_missed_other": (slot["misses"] - miss) / failures,
            "prop_shots_other": (slot["shots"] - 1) / (n - 1),
        }
        rebuilt.append(other)
    return rebuilt


def resampling_t_expectation(correlation, n_draws=30, n_cells=4):
    """The t the authors' normal draws are centered on, before sampling noise.

    pk_resampling.R draws n_draws normals and has no seed, so the printed
    t statistics are one draw. The standard error uses n_cells - 2.
    """
    se = math.sqrt((1.0 - correlation ** 2) / (n_cells - 2))
    expected_t = correlation / (se / math.sqrt(n_draws))
    return {"se": se, "expected_t": expected_t}


def main():
    game = mixed_equilibrium()
    print(
        "table 1 equilibrium "
        f"p={game['p_shoot_center']:.3f} "
        f"q={game['q_stay_center']:.3f} "
        f"value={game['value_taker']:.3f}"
    )
    share = analytic_corner_share()
    sample = simulate_statistical_game()
    print(
        f"analytic corner share {share:.3f}; "
        f"seeded {sample['n']} draws {sample['corner_share']:.3f}, "
        f"corner {sample['corner_conversion']:.3f}, "
        f"center {sample['center_conversion']:.3f}"
    )


if __name__ == "__main__":
    main()
