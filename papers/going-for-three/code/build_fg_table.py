"""Build the derived field-goal tables from nflverse play-by-play.

Raw parquet stays in the cache directory (default ``/tmp/nflverse-pbp``).
This script writes only the small aggregates named in ``DATA.md``.

    python3 papers/going-for-three/code/build_fg_table.py
"""

import json
import math
import os
import re
import urllib.request
from pathlib import Path

import pandas as pd

from fg_logistic import (
    PAPER,
    COEF_NAMES,
    PRECIP_PATTERN,
    COLD_CUTOFF_F,
    WIND_CUTOFF_MPH,
    added_points,
    fit_logit,
    is_turf,
    probability,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGURES = ROOT / "figures"
CACHE = Path(os.environ.get("NFLVERSE_CACHE", "/tmp/nflverse-pbp"))
SEASONS = range(2000, 2012)
PBP_URL = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{year}.parquet"
COLUMNS = [
    "game_id",
    "play_id",
    "season",
    "season_type",
    "kicker_player_name",
    "kicker_player_id",
    "field_goal_attempt",
    "field_goal_result",
    "kick_distance",
    "roof",
    "surface",
    "temp",
    "wind",
    "weather",
    "home_team",
    "game_stadium",
]

# Same building, more than one nflverse name. Different buildings stay apart
# (Foxboro vs Gillette, RCA Dome vs Lucas Oil, old Mile High vs Invesco are
# the exception: the paper's Denver row covers both Mile High buildings).
BUILDING = {
    "Mile High Stadium": "Mile High (Denver)",
    "Invesco Field at Mile High": "Mile High (Denver)",
    "Sports Authority Field at Mile High": "Mile High (Denver)",
    "Hubert H. Humphrey Metrodome": "Metrodome",
    "Mall of America Field": "Metrodome",
    "Louisiana Superdome": "Superdome",
    "Mercedes-Benz Superdome": "Superdome",
    "TWA Dome": "Edward Jones Dome",
    "Dome at America's Center": "Edward Jones Dome",
    "Edward Jones Dome": "Edward Jones Dome",
    "Seahawks Stadium": "CenturyLink Field",
    "Qwest Field": "CenturyLink Field",
    "CenturyLink Field": "CenturyLink Field",
    "Network Associates Coliseum": "Oakland Coliseum",
    "McAfee Coliseum": "Oakland Coliseum",
    "Oakland-Alameda County Coliseum": "Oakland Coliseum",
    "O.co Coliseum": "Oakland Coliseum",
    "Pro Player Stadium": "Sun Life Stadium",
    "Dolphin Stadium": "Sun Life Stadium",
    "Sun Life Stadium": "Sun Life Stadium",
    "3Com Park": "Candlestick Park",
    "Monster Park": "Candlestick Park",
    "Candlestick Park": "Candlestick Park",
    "Adelphia Coliseum": "LP Field",
    "The Coliseum": "LP Field",
    "LP Field": "LP Field",
    "Ericsson Stadium": "Bank of America Stadium",
    "Bank of America Stadium": "Bank of America Stadium",
    "Alltel Stadium": "EverBank Field",
    "Jacksonville Municipal Stadium": "EverBank Field",
    "EverBank Field": "EverBank Field",
    "PSINet Stadium": "M&T Bank Stadium",
    "Ravens Stadium": "M&T Bank Stadium",
    "M&T Bank Stadium": "M&T Bank Stadium",
    "New Meadowlands Stadium": "MetLife Stadium",
    "MetLife Stadium": "MetLife Stadium",
}

# Paper Table A.2 / A.3. Counts and make rates are the printed career totals.
PAPER_KICKERS = [
    ("Rob Bironas", "R.Bironas", 0.262, 0.8610, 223),
    ("Robbie Gould", "R.Gould", 0.204, 0.8616, 224),
    ("Connor Barth", "C.Barth", 0.195, 0.8391, 87),
    ("John Kasay", "J.Kasay", 0.160, 0.8385, 322),
    ("Dan Carpenter", "D.Carpenter", 0.134, 0.8217, 129),
    ("Joe Nedney", "J.Nedney", 0.130, 0.8480, 250),
    ("Sebastian Janikowski", "S.Janikowski", 0.117, 0.7995, 384),
    ("Garrett Hartley", "G.Hartley", 0.108, 0.8772, 57),
    ("Matt Stover", "M.Stover", 0.101, 0.8687, 335),
    ("Ryan Succop", "R.Succop", 0.0911, 0.8118, 85),
    ("Phil Dawson", "P.Dawson", 0.0889, 0.8385, 322),
    ("David Akers", "D.Akers", 0.0865, 0.8315, 445),
    ("Jason Hanson", "J.Hanson", 0.0816, 0.8302, 324),
    ("Ryan Longwell", "R.Longwell", 0.0740, 0.8249, 354),
    ("Jeff Wilkins", "J.Wilkins", 0.0737, 0.8419, 253),
    ("Adam Vinatieri", "A.Vinatieri", 0.0732, 0.8431, 376),
    ("Shayne Graham", "S.Graham", 0.0705, 0.8543, 254),
    ("Nate Kaeding", "N.Kaeding", 0.0692, 0.8419, 215),
    ("Mason Crosby", "M.Crosby", 0.0594, 0.7989, 174),
    ("Jeff Reed", "J.Reed", 0.0558, 0.8267, 277),
    ("Josh Brown", "J.Brown", 0.0536, 0.8110, 291),
    ("Gary Anderson", "G.Anderson", 0.0490, 0.8443, 122),
    ("Mike Vanderjagt", "M.Vanderjagt", 0.0481, 0.8510, 208),
    ("Josh Scobee", "J.Scobee", 0.0377, 0.7844, 218),
    ("Matt Bryant", "M.Bryant", 0.0273, 0.8382, 241),
    ("Morten Andersen", "M.Andersen", 0.0078, 0.8297, 182),
    ("Neil Rackers", "N.Rackers", 0.0021, 0.7959, 343),
    ("Stephen Gostkowski", "S.Gostkowski", -0.0040, 0.8470, 183),
    ("John Carney", "J.Carney", -0.0175, 0.8299, 288),
    ("Steven Hauschka", "S.Hauschka", -0.0263, 0.7885, 52),
    ("Jason Elam", "J.Elam", -0.0268, 0.8264, 311),
    ("Olindo Mare", "O.Mare", -0.0269, 0.8110, 328),
    ("Rian Lindell", "R.Lindell", -0.0271, 0.8086, 324),
    ("Jay Feely", "J.Feely", -0.0280, 0.8143, 350),
    ("Mike Hollis", "M.Hollis", -0.0559, 0.7701, 87),
    ("Mike Nugent", "M.Nugent", -0.0568, 0.8086, 162),
    ("Paul Edinger", "P.Edinger", -0.0587, 0.7514, 181),
    ("Shaun Suisham", "S.Suisham", -0.0635, 0.7824, 170),
    ("Matt Prater", "M.Prater", -0.0695, 0.7934, 121),
    ("Nick Folk", "N.Folk", -0.0721, 0.7785, 149),
    ("Brett Conway", "B.Conway", -0.0742, 0.7966, 59),
    ("Lawrence Tynes", "L.Tynes", -0.0823, 0.8019, 212),
    ("Kris Brown", "K.Brown", -0.0838, 0.7622, 307),
    ("Doug Brien", "D.Brien", -0.0846, 0.7895, 114),
    ("Martin Gramatica", "M.Gramatica", -0.102, 0.7596, 183),
    ("John Hall", "J.Hall", -0.115, 0.7485, 171),
    ("Todd Peterson", "T.Peterson", -0.138, 0.7754, 138),
    ("Billy Cundiff", "B.Cundiff", -0.141, 0.7742, 186),
    ("Graham Gano", "G.Gano", -0.147, 0.7375, 80),
    ("Dave Rayner", "D.Rayner", -0.170, 0.7222, 90),
    ("Steve Christie", "S.Christie", -0.200, 0.7500, 120),
    ("Nick Novak", "N.Novak", -0.201, 0.7188, 64),
    ("Tim Seder", "T.Seder", -0.342, 0.7097, 62),
    ("Jose Cortez", "J.Cortez", -0.405, 0.7067, 75),
    ("Wade Richey", "W.Richey", -0.467, 0.6607, 56),
]


def download_seasons():
    CACHE.mkdir(parents=True, exist_ok=True)
    paths = []
    for year in SEASONS:
        path = CACHE / f"play_by_play_{year}.parquet"
        if not path.exists() or path.stat().st_size < 1000:
            url = PBP_URL.format(year=year)
            print("download", url)
            urllib.request.urlretrieve(url, path)
        paths.append(path)
    return paths


def load_plays(paths):
    frames = [pd.read_parquet(path, columns=COLUMNS) for path in paths]
    return pd.concat(frames, ignore_index=True)


def add_flags(frame, cold_cutoff):
    """Flags from DATA.md. Precipitation words are this page's list."""
    outdoors = frame["roof"].isin(["outdoors", "open"])
    out = frame.copy()
    out["outdoors"] = outdoors
    temp = out["temp"]
    out["cold"] = (outdoors & temp.notna() & (temp < cold_cutoff)).astype(int)
    # Blank temperature unless the cold rule can see it. Domes stay missing.
    out["temp_out"] = temp.where(outdoors & temp.notna())
    # Heinz Field `dessograss` is grass here. See is_turf in fg_logistic.py.
    stadium = out["game_stadium"] if "game_stadium" in out.columns else None
    surface = out["surface"]
    if stadium is None:
        out["turf"] = surface.fillna("grass").map(lambda label: is_turf(label)).astype(int)
    else:
        out["turf"] = [
            is_turf(label, stad)
            for label, stad in zip(surface, stadium)
        ]
        out["turf"] = pd.Series(out["turf"], index=out.index).astype(int)
    out["alt"] = (
        (out["home_team"] == "DEN") | (out["game_id"] == "2005_04_SF_ARI")
    ).astype(int)
    weather = out["weather"].fillna("").str.lower()
    keyword = weather.str.contains(PRECIP_PATTERN, regex=True)
    chance = weather.str.contains("chance", regex=False)
    out["precip"] = (outdoors & keyword & ~chance).astype(int)
    wind = out["wind"]
    out["windy"] = (outdoors & wind.notna() & (wind >= WIND_CUTOFF_MPH)).astype(int)
    return out


def coef_dict(beta):
    return {name: float(beta[i]) for i, name in enumerate(COEF_NAMES)}


def wald_table(beta, errors):
    rows = []
    for name, estimate, error in zip(COEF_NAMES, beta, errors):
        wald = estimate / error
        # Two-sided normal tail.
        p_value = math.erfc(abs(wald) / math.sqrt(2.0))
        rows.append(
            {
                "name": name,
                "estimate": estimate,
                "se": error,
                "wald": wald,
                "p": p_value,
            }
        )
    return rows


def display_name(key):
    if "." in key:
        left, right = key.split(".", 1)
        return f"{left}. {right}"
    return key


def canonical_kicker(frame):
    """One name per kicker id. nflverse splits 'S.Janikowski' and 'S. Janikowski'."""
    mode = frame.groupby("kicker_player_id")["kicker_player_name"].agg(
        lambda names: names.value_counts().index[0]
    )
    key = frame["kicker_player_id"].map(mode).str.replace(" ", "", regex=False)
    # Josh Brown and Jeff Reed share an id with a second spelling. Keep the id's mode.
    return key


def season_slope(seasons, values):
    n = len(seasons)
    x = [year - 2000.0 for year in seasons]
    y = list(values)
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    sxx = sum((xi - x_mean) ** 2 for xi in x)
    slope = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y)) / sxx
    intercept = y_mean - slope * x_mean
    resid = [yi - (intercept + slope * xi) for xi, yi in zip(x, y)]
    dof = n - 2
    sigma2 = sum(r * r for r in resid) / dof
    se = math.sqrt(sigma2 / sxx)
    return slope, se, slope / se, dof


def classification(frame, prob):
    made = frame["made"].to_numpy()
    naive = float(made.mean())
    best = None
    grid = []
    cutoff = 0.20
    while cutoff <= 0.8001:
        predict_make = prob >= cutoff
        correct = (predict_make & (made == 1)) | ((~predict_make) & (made == 0))
        accuracy = float(correct.mean())
        grid.append((round(cutoff, 3), accuracy))
        if best is None or accuracy > best[1]:
            best = (round(cutoff, 3), accuracy)
        cutoff += 0.005
    def at(cut):
        predict_make = prob >= cut
        correct = (predict_make & (made == 1)) | ((~predict_make) & (made == 0))
        return float(correct.mean())
    return {
        "naive_all_make": naive,
        "at_0.50": at(0.50),
        "at_0.37": at(0.37),
        "best_cutoff": best[0],
        "best_accuracy": best[1],
    }


def experience_fit(frame, base_names):
    """Experience is seasons observed in 2000–2011 up to the current season.

    Careers that started before 2000 are left-censored. Counting the current
    season or only prior seasons shifts the intercept and leaves the slope.
    """
    career_n = frame.groupby("kicker_id").size()
    eligible = set(career_n[career_n >= 50].index)
    sub = frame[frame["kicker_id"].isin(eligible)].copy()
    seasons = sub.groupby("kicker_id")["season"].agg(lambda s: sorted(set(int(v) for v in s)))
    exp = []
    for kicker, season in zip(sub["kicker_id"], sub["season"]):
        exp.append(sum(1 for year in seasons[kicker] if year <= int(season)))
    sub["exp"] = exp
    sub["year"] = sub["season"] - 2000
    rows = list(
        zip(
            sub["dist"],
            sub["cold"],
            sub["turf"],
            sub["alt"],
            sub["precip"],
            sub["windy"],
            sub["exp"],
            sub["year"],
            sub["made"],
        )
    )
    beta, errors = fit_extended(rows)
    labels = list(base_names) + ["experience", "season_year"]
    return {
        "attempts": int(len(sub)),
        "kickers": int(sub["kicker_id"].nunique()),
        "coefficients": {name: beta[i] for i, name in enumerate(labels)},
        "se": {name: errors[i] for i, name in enumerate(labels)},
        "wald": {name: beta[i] / errors[i] for i, name in enumerate(labels)},
    }


def fit_extended(rows):
    """Newton fit with two extra columns: experience and season year."""
    width = 9
    beta = [0.0] * width
    hessian = None
    for _ in range(40):
        hessian = [[0.0] * width for _ in range(width)]
        gradient = [0.0] * width
        for dist, cold, turf, alt, precip, wind, exp, year, made in rows:
            design = (1.0, float(dist), float(cold), float(turf), float(alt), float(precip), float(wind), float(exp), float(year))
            score = sum(b * x for b, x in zip(beta, design))
            prob = 1.0 / (1.0 + math.exp(-max(min(score, 30.0), -30.0)))
            weight = prob * (1.0 - prob)
            residual = made - prob
            for i in range(width):
                gradient[i] += residual * design[i]
                for j in range(width):
                    hessian[i][j] += weight * design[i] * design[j]
        step = _solve_local(hessian, gradient)
        beta = [b + s for b, s in zip(beta, step)]
        if max(abs(s) for s in step) < 1e-12:
            break
    errors = []
    for i in range(width):
        unit = [0.0] * width
        unit[i] = 1.0
        column = _solve_local(hessian, unit)
        errors.append(math.sqrt(column[i]) if column[i] > 0 else float("nan"))
    return beta, errors


def _solve_local(matrix, rhs):
    size = len(rhs)
    rows = [list(matrix[i]) + [rhs[i]] for i in range(size)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(rows[row][col]))
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        for j in range(col, size + 1):
            rows[col][j] /= scale
        for row in range(size):
            if row == col:
                continue
            factor = rows[row][col]
            for j in range(col, size + 1):
                rows[row][j] -= factor * rows[col][j]
    return [rows[i][size] for i in range(size)]


def stadium_table(games, coefs):
    games = games.copy()
    games["building"] = games["game_stadium"].map(lambda name: BUILDING.get(name, name))
    games["p45"] = [
        probability(45, cold, turf, alt, precip, wind, coefs)
        for cold, turf, alt, precip, wind in zip(
            games["cold"], games["turf"], games["alt"], games["precip"], games["windy"]
        )
    ]
    mean_p = float(games["p45"].mean())
    games["rel"] = games["p45"] - mean_p
    surface_n = games.groupby(["building", "turf"]).size().reset_index(name="n")
    multi = surface_n.groupby("building")["turf"].nunique()
    split = set(multi[multi > 1].index)
    labels = []
    for building, turf in zip(games["building"], games["turf"]):
        if building in split:
            labels.append(f"{building}, {'turf' if turf == 1 else 'grass'}")
        else:
            labels.append(building)
    games["stad_key"] = labels
    grouped = games.groupby("stad_key").agg(
        games=("p45", "size"),
        rel=("rel", "mean"),
        p45=("p45", "mean"),
        seasons=("season", "nunique"),
    )
    kept = grouped[grouped["games"] >= 5].sort_values("rel")
    # ANOVA on the 45-yard probability, stadiums with at least 5 games.
    sub = games[games["stad_key"].isin(set(kept.index))]
    groups = [g["p45"].to_numpy() for _, g in sub.groupby("stad_key")]
    k = len(groups)
    n_obs = sum(len(g) for g in groups)
    grand = float(sub["p45"].mean())
    ssb = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
    ssw = sum(float(((g - g.mean()) ** 2).sum()) for g in groups)
    dfb, dfw = k - 1, n_obs - k
    f_stat = (ssb / dfb) / (ssw / dfw)
    records = []
    for name, row in kept.sort_values("rel").iterrows():
        records.append(
            {
                "stadium": name,
                "games": int(row["games"]),
                "seasons": int(row["seasons"]),
                "p45": float(row["p45"]),
                "relative": float(row["rel"]),
            }
        )
    return {
        "games": int(len(games)),
        "regular": int((games["season_type"] == "REG").sum()) if "season_type" in games else None,
        "mean_p45": mean_p,
        "anova_F": f_stat,
        "anova_df": [dfb, dfw],
        "stadiums_at_least_5": k,
        "rows": records,
    }


def write_curves(path, coefs, title, subtitle, our_coefs=None):
    """Redraw Figure 1. Distances 18–65. Not a scan of the PDF."""
    def poly(coef, flags, color, width, dash):
        points = []
        for yard in range(18, 66):
            prob = probability(yard, *flags, coef)
            x = 70 + (yard - 18) * (540 / 47)
            y = 360 - prob * 250
            points.append(f"{x:.1f},{y:.1f}")
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        return (
            f'<polyline fill="none" stroke="{color}" stroke-width="{width}"{dash_attr} '
            f'points="{" ".join(points)}"/>'
        )

    snow_flags = (1, 0, 0, 1, 1)
    mild_flags = (0, 0, 0, 0, 0)
    parts = [
        poly(coefs, snow_flags, "#1b2430", 3, None),
        poly(coefs, mild_flags, "#1f6b4a", 3, None),
    ]
    if our_coefs is not None:
        parts.append(poly(our_coefs, snow_flags, "#1b2430", 2, "7 5"))
        parts.append(poly(our_coefs, mild_flags, "#1f6b4a", 2, "7 5"))
    snow_p = probability(45, *snow_flags, coefs)
    mild_p = probability(45, *mild_flags, coefs)
    marker_x = 70 + (45 - 18) * (540 / 47)
    marker_y = 360 - snow_p * 250
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 460" role="img" aria-label="{title}">
  <rect width="680" height="460" fill="#f7f4ee"/>
  <text x="28" y="36" fill="#1b2430" font-family="Georgia, serif" font-size="22">{title}</text>
  <text x="28" y="58" fill="#5c564c" font-family="Helvetica, sans-serif" font-size="13">{subtitle}</text>
  <line x1="70" y1="360" x2="610" y2="360" stroke="#1b2430" stroke-width="1.4"/>
  <line x1="70" y1="110" x2="70" y2="360" stroke="#1b2430" stroke-width="1.4"/>
  {''.join(parts)}
  <circle cx="{marker_x:.1f}" cy="{marker_y:.1f}" r="5.5" fill="#b64a28"/>
  <text x="320" y="392" fill="#5c564c" font-family="Helvetica, sans-serif" font-size="13">kick distance (yards)</text>
  <text x="22" y="250" fill="#5c564c" font-family="Helvetica, sans-serif" font-size="13" transform="rotate(-90 22 250)">make probability</text>
  <text x="78" y="124" fill="#5c564c" font-family="Helvetica, sans-serif" font-size="12">1</text>
  <text x="78" y="249" fill="#5c564c" font-family="Helvetica, sans-serif" font-size="12">0.5</text>
  <text x="78" y="374" fill="#5c564c" font-family="Helvetica, sans-serif" font-size="12">0</text>
  <line x1="64" y1="235" x2="70" y2="235" stroke="#1b2430"/>
  <text x="86" y="430" fill="#1b2430" font-family="Helvetica, sans-serif" font-size="13">45 yards in snow and wind: {snow_p:.1%}. Mild weather: {mild_p:.1%}. Difference {(mild_p - snow_p) * 100:+.1f} points.</text>
</svg>
'''
    path.write_text(svg)


def write_legend_svg(path, coefs, paper):
    """Our curves solid, Table 1 curves dashed."""
    def poly(coef, flags, color, width, dash):
        points = []
        for yard in range(18, 66):
            prob = probability(yard, *flags, coef)
            x = 70 + (yard - 18) * (540 / 47)
            y = 360 - prob * 250
            points.append(f"{x:.1f},{y:.1f}")
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        return (
            f'<polyline fill="none" stroke="{color}" stroke-width="{width}"{dash_attr} '
            f'points="{" ".join(points)}"/>'
        )

    snow = (1, 0, 0, 1, 1)
    mild = (0, 0, 0, 0, 0)
    snow_p = probability(45, *snow, coefs)
    mild_p = probability(45, *mild, coefs)
    marker_x = 70 + (45 - 18) * (540 / 47)
    marker_y = 360 - snow_p * 250
    body = "".join(
        [
            poly(coefs, snow, "#1b2430", 3, None),
            poly(coefs, mild, "#1f6b4a", 3, None),
            poly(paper, snow, "#1b2430", 2, "7 5"),
            poly(paper, mild, "#1f6b4a", 2, "7 5"),
        ]
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 460" role="img" aria-label="Our rebuild of Figure 1">
  <rect width="680" height="460" fill="#f7f4ee"/>
  <text x="28" y="36" fill="#1b2430" font-family="Georgia, serif" font-size="22">Our rebuild of Figure 1</text>
  <text x="28" y="58" fill="#5c564c" font-family="Helvetica, sans-serif" font-size="13">Solid: nflverse refit. Dashed: Table 1 as printed. 11,893 attempts, 2000–2011.</text>
  <line x1="70" y1="360" x2="610" y2="360" stroke="#1b2430" stroke-width="1.4"/>
  <line x1="70" y1="110" x2="70" y2="360" stroke="#1b2430" stroke-width="1.4"/>
  {body}
  <circle cx="{marker_x:.1f}" cy="{marker_y:.1f}" r="5.5" fill="#b64a28"/>
  <text x="320" y="392" fill="#5c564c" font-family="Helvetica, sans-serif" font-size="13">kick distance (yards)</text>
  <text x="22" y="250" fill="#5c564c" font-family="Helvetica, sans-serif" font-size="13" transform="rotate(-90 22 250)">make probability</text>
  <text x="86" y="418" fill="#1b2430" font-family="Helvetica, sans-serif" font-size="13">Refit at 45 yards in snow and wind: {snow_p:.1%}. Mild weather: {mild_p:.1%}. Difference {(mild_p - snow_p) * 100:+.1f} points.</text>
  <text x="86" y="440" fill="#5c564c" font-family="Helvetica, sans-serif" font-size="13">Navy is cold, precipitation, and wind. Green is mild weather. The dot is 45 yards.</text>
</svg>
'''
    path.write_text(svg)


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    plays = load_plays(download_seasons())
    kicks = plays[
        plays["field_goal_attempt"].fillna(0).eq(1)
        & plays["season_type"].isin(["REG", "POST"])
    ].copy()
    kicks = add_flags(kicks, COLD_CUTOFF_F)
    kicks["made"] = (kicks["field_goal_result"] == "made").astype(int)
    kicks["dist"] = kicks["kick_distance"].astype(float)
    kicks["kicker_id"] = kicks["kicker_player_id"]
    kicks["kicker"] = canonical_kicker(kicks)

    attempts = int(len(kicks))
    made = int(kicks["made"].sum())
    missed = int((kicks["field_goal_result"] == "missed").sum())
    blocked = int((kicks["field_goal_result"] == "blocked").sum())
    reg = int((kicks["season_type"] == "REG").sum())
    post = int((kicks["season_type"] == "POST").sum())
    missing_weather = float(kicks["temp"].isna().mean())

    groups = (
        kicks.groupby(["dist", "cold", "turf", "alt", "precip", "windy"], as_index=False)
        .agg(made=("made", "sum"), n=("made", "size"))
        .sort_values(["dist", "cold", "turf", "alt", "precip", "windy"])
    )
    agg_path = DATA / "fg_agg_2000_2011.csv"
    groups.to_csv(agg_path, index=False)
    fit_groups = [
        (r.dist, r.cold, r.turf, r.alt, r.precip, r.windy, r.made, r.n)
        for r in groups.itertuples(index=False)
    ]
    beta, errors = fit_logit(fit_groups)
    coefs = coef_dict(beta)
    table = wald_table(beta, errors)

    # Footnote 3 counts "chance of rain" as precipitation. The paper says that
    # alternate coding barely moves the coefficient. Ours does not.
    weather = kicks["weather"].fillna("").str.lower()
    keyword = weather.str.contains(PRECIP_PATTERN, regex=True)
    chance_rows = kicks.copy()
    chance_rows["precip"] = (chance_rows["outdoors"] & keyword).astype(int)
    chance_groups = (
        chance_rows.groupby(["dist", "cold", "turf", "alt", "precip", "windy"], as_index=False)
        .agg(made=("made", "sum"), n=("made", "size"))
    )
    chance_fit = [
        (r.dist, r.cold, r.turf, r.alt, r.precip, r.windy, r.made, r.n)
        for r in chance_groups.itertuples(index=False)
    ]
    beta_chance, errors_chance = fit_logit(chance_fit)
    chance_wald = wald_table(beta_chance, errors_chance)
    precip_note = {
        "baseline": next(row for row in table if row["name"] == "precipitation"),
        "chance_counted": next(row for row in chance_wald if row["name"] == "precipitation"),
        "chance_attempts": int(chance_rows["precip"].sum()),
    }

    heinz = kicks[(kicks["game_stadium"] == "Heinz Field") & (kicks["surface"] == "dessograss")]
    dessograss_note = {
        "attempts": int(len(heinz)),
        "seasons": sorted(int(year) for year in heinz["season"].unique()),
        "turf_flag": int(heinz["turf"].max()) if len(heinz) else None,
    }

    # Temperature file for the cold-cutoff slider. temp is blank when the
    # cold rule cannot see it (dome, closed roof, or missing).
    temp_groups = kicks.copy()
    temp_groups["temp_i"] = temp_groups["temp_out"].astype("Int64")
    temp_agg = (
        temp_groups.groupby(
            ["dist", "temp_i", "turf", "alt", "precip", "windy"], dropna=False, as_index=False
        )
        .agg(made=("made", "sum"), n=("made", "size"))
        .sort_values(["dist", "temp_i", "turf", "alt", "precip", "windy"])
    )
    temp_path = DATA / "fg_by_temp.csv"
    temp_agg.to_csv(temp_path, index=False)

    # Refit at cutoff 50 from the temperature file must match the binary file.
    temp_rows = []
    for row in temp_agg.itertuples(index=False):
        temp = row.temp_i
        cold = 0 if pd.isna(temp) else int(temp < COLD_CUTOFF_F)
        temp_rows.append((row.dist, cold, row.turf, row.alt, row.precip, row.windy, row.made, row.n))
    beta_check, _ = fit_logit(temp_rows)
    for name, left, right in zip(COEF_NAMES, beta, beta_check):
        if abs(left - right) > 1e-8:
            raise SystemExit(f"temp aggregate drifted on {name}")

    cold_path = []
    for cutoff in range(30, 61):
        rows = []
        for row in temp_agg.itertuples(index=False):
            temp = row.temp_i
            cold = 0 if pd.isna(temp) else int(temp < cutoff)
            rows.append((row.dist, cold, row.turf, row.alt, row.precip, row.windy, row.made, row.n))
        b_cut, e_cut = fit_logit(rows)
        cold_path.append(
            {
                "cutoff": cutoff,
                "cold": b_cut[2],
                "se": e_cut[2],
                "wald": b_cut[2] / e_cut[2],
                "n_cold": int(sum(r[1] * r[7] for r in rows)),
            }
        )

    def predict(row_coefs, cold, turf, alt, precip, wind, dist=45):
        return probability(dist, cold, turf, alt, precip, wind, row_coefs)

    vin = kicks[(kicks["game_id"] == "2001_19_OAK_NE") & (kicks["play_id"] == 3818)].iloc[0]
    snow = predict(coefs, 1, 0, 0, 1, 1)
    mild = predict(coefs, 0, 0, 0, 0, 0)
    our_wind = predict(coefs, 1, 0, 0, 1, 0)
    paper_snow = predict(PAPER, 1, 0, 0, 1, 1)
    paper_mild = predict(PAPER, 0, 0, 0, 0, 0)
    rounded = {name: round(coefs[name], 3) for name in COEF_NAMES}
    rounded_snow = predict(rounded, 1, 0, 0, 1, 1)
    rounded_mild = predict(rounded, 0, 0, 0, 0, 0)

    # Per-kick probabilities from the unrounded refit, for rankings.
    kicks["prob"] = [
        probability(d, c, t, a, p, w, coefs)
        for d, c, t, a, p, w in zip(
            kicks["dist"], kicks["cold"], kicks["turf"], kicks["alt"], kicks["precip"], kicks["windy"]
        )
    ]
    kicks["ap"] = [added_points(m, p) for m, p in zip(kicks["made"], kicks["prob"])]

    kickers = kicks.groupby("kicker").agg(
        attempts=("made", "size"),
        makes=("made", "sum"),
        added=("ap", "sum"),
    )
    ranked = kickers[kickers["attempts"] > 50].copy()
    ranked["added_per"] = ranked["added"] / ranked["attempts"]
    ranked["make_pct"] = ranked["makes"] / ranked["attempts"]
    ranked["rank_added"] = ranked["added_per"].rank(ascending=False, method="min").astype(int)
    ranked["rank_pct"] = ranked["make_pct"].rank(ascending=False, method="min").astype(int)
    ranked["gap"] = ranked["rank_pct"] - ranked["rank_added"]
    paper_by_key = {key: (name, ap, pct, n) for name, key, ap, pct, n in PAPER_KICKERS}
    kicker_rows = []
    for key, row in ranked.sort_values("rank_added").iterrows():
        paper = paper_by_key.get(key)
        kicker_rows.append(
            {
                "kicker": display_name(key),
                "key": key,
                "attempts": int(row["attempts"]),
                "makes": int(row["makes"]),
                "make_pct": float(row["make_pct"]),
                "added_per": float(row["added_per"]),
                "rank_added": int(row["rank_added"]),
                "rank_pct": int(row["rank_pct"]),
                "gap": int(row["gap"]),
                "paper_added": None if paper is None else paper[1],
                "paper_make_pct": None if paper is None else paper[2],
                "paper_attempts": None if paper is None else paper[3],
                "paper_name": None if paper is None else paper[0],
            }
        )
    missing = sorted(set(paper_by_key) - set(ranked.index))
    extra = sorted(set(ranked.index) - set(paper_by_key))

    seasons = (
        kicks.groupby("season")
        .agg(attempts=("made", "size"), added_per=("ap", "mean"), added=("ap", "sum"))
        .reset_index()
        .sort_values("season")
    )
    slope, slope_se, slope_t, slope_df = season_slope(
        [int(y) for y in seasons["season"]],
        [float(v) for v in seasons["added_per"]],
    )
    season_rows = [
        {
            "season": int(r.season),
            "attempts": int(r.attempts),
            "added_per": float(r.added_per),
            "added": float(r.added),
        }
        for r in seasons.itertuples(index=False)
    ]
    by_season = (
        kicks.groupby(["kicker", "season"])
        .agg(attempts=("made", "size"), added=("ap", "sum"))
        .reset_index()
    )
    long = by_season[by_season["attempts"] >= 20].sort_values("added", ascending=False)
    best_seasons = [
        {
            "kicker": display_name(r.kicker),
            "season": int(r.season),
            "attempts": int(r.attempts),
            "added": float(r.added),
        }
        for r in list(long.head(8).itertuples(index=False))
    ]
    worst_seasons = [
        {
            "kicker": display_name(r.kicker),
            "season": int(r.season),
            "attempts": int(r.attempts),
            "added": float(r.added),
        }
        for r in list(long.tail(8).itertuples(index=False))
    ]

    cls = classification(kicks, kicks["prob"].to_numpy())
    exp = experience_fit(kicks, COEF_NAMES)

    game_cols = [
        "game_id",
        "season",
        "season_type",
        "home_team",
        "game_stadium",
        "roof",
        "surface",
        "temp",
        "wind",
        "weather",
    ]
    games = plays[plays["season_type"].isin(["REG", "POST"])][game_cols].drop_duplicates("game_id")
    games = add_flags(games, COLD_CUTOFF_F)
    stad = stadium_table(games, coefs)

    # Walk the Vinatieri kick one term at a time.
    walk = []
    running = {"cold": 0, "turf": 0, "altitude": 0, "precipitation": 0, "wind": 0}
    steps = [
        ("distance", None),
        ("cold", "cold"),
        ("precipitation", "precipitation"),
        ("wind", "wind"),
    ]
    for label, flag in steps:
        if flag:
            running[flag] = 1
        walk.append(
            {
                "step": label,
                "probability": probability(
                    45,
                    running["cold"],
                    running["turf"],
                    running["altitude"],
                    running["precipitation"],
                    running["wind"],
                    coefs,
                ),
            }
        )

    asset_sizes = {
        path.name: path.stat().st_size
        for path in sorted(CACHE.glob("play_by_play_*.parquet"))
    }

    report = {
        "attempts": attempts,
        "regular": reg,
        "postseason": post,
        "made": made,
        "missed": missed,
        "blocked": blocked,
        "missing_temp_share": missing_weather,
        "agg_rows": int(len(groups)),
        "temp_rows": int(len(temp_agg)),
        "agg_bytes": agg_path.stat().st_size,
        "temp_bytes": temp_path.stat().st_size,
        "coefficients": table,
        "rounded_coefficients": rounded,
        "vinatieri": {
            "game_id": "2001_19_OAK_NE",
            "play_id": 3818,
            "kicker": str(vin["kicker_player_name"]),
            "desc": str(vin["desc"]) if "desc" in kicks.columns else "",
            "distance": float(vin["dist"]),
            "temp": None if pd.isna(vin["temp"]) else float(vin["temp"]),
            "wind_mph": None if pd.isna(vin["wind"]) else float(vin["wind"]),
            "weather": str(vin["weather"]),
            "roof": str(vin["roof"]),
            "surface": str(vin["surface"]),
            "cold": int(vin["cold"]),
            "turf": int(vin["turf"]),
            "altitude": int(vin["alt"]),
            "precipitation": int(vin["precip"]),
            "windy": int(vin["windy"]),
            "made": int(vin["made"]),
        },
        "probabilities": {
            "refit_snow_wind": snow,
            "refit_mild": mild,
            "refit_lift": mild - snow,
            "refit_our_wind_off": our_wind,
            "paper_printed_snow_wind": paper_snow,
            "paper_printed_mild": paper_mild,
            "paper_printed_lift": paper_mild - paper_snow,
            "rounded_snow_wind": rounded_snow,
            "rounded_mild": rounded_mild,
            "rounded_lift": rounded_mild - rounded_snow,
            "added_points_make_refit": added_points(1, snow),
            "added_points_make_rounded": added_points(1, rounded_snow),
        },
        "walk": walk,
        "kickers_over_50": len(ranked),
        "kicker_unmatched_paper_keys": missing,
        "kicker_extra_keys": extra,
        "kickers": kicker_rows,
        "seasons": season_rows,
        "season_slope_per_year": slope,
        "season_slope_se": slope_se,
        "season_slope_t": slope_t,
        "season_slope_df": slope_df,
        "season_rows_at_least_20": int(len(long)),
        "best_seasons": best_seasons,
        "worst_seasons": worst_seasons,
        "classification": cls,
        "experience": exp,
        "cold_cutoff": cold_path,
        "stadium": {
            "games": stad["games"],
            "mean_p45": stad["mean_p45"],
            "anova_F": stad["anova_F"],
            "anova_df": stad["anova_df"],
            "stadiums_at_least_5": stad["stadiums_at_least_5"],
            "lambeau": next(
                row for row in stad["rows"] if row["stadium"] == "Lambeau Field"
            ),
        },
        "asset_bytes": asset_sizes,
        "precip_pattern": PRECIP_PATTERN,
        "dessograss": dessograss_note,
        "precip_chance": precip_note,
    }
    # desc may not have been loaded. Fill from a targeted read if empty.
    if not report["vinatieri"]["desc"]:
        one = pd.read_parquet(
            CACHE / "play_by_play_2001.parquet",
            columns=["game_id", "play_id", "desc"],
        )
        hit = one[(one["game_id"] == "2001_19_OAK_NE") & (one["play_id"] == 3818)]
        report["vinatieri"]["desc"] = str(hit.iloc[0]["desc"])

    (DATA / "fit_report.json").write_text(json.dumps(report, indent=2))
    ranked_out = pd.DataFrame(kicker_rows)
    ranked_out.to_csv(DATA / "kicker_ranks.csv", index=False)
    pd.DataFrame(season_rows).to_csv(DATA / "season_added_points.csv", index=False)
    pd.DataFrame(stad["rows"]).to_csv(DATA / "stadium_difficulty.csv", index=False)

    write_curves(
        FIGURES / "paper-original.svg",
        PAPER,
        "Figure 1 redrawn from Table 1",
        "Printed coefficients. The paper says 53% at 45 yards. These coefficients give the rate below.",
    )
    write_legend_svg(FIGURES / "our-rebuild.svg", coefs, PAPER)

    print("dessograss", dessograss_note)
    print("precip chance", precip_note["baseline"]["estimate"], precip_note["chance_counted"]["estimate"], precip_note["chance_counted"]["p"])
    print("attempts", attempts, "made", made, "missed", missed, "blocked", blocked)
    print("agg", len(groups), agg_path.stat().st_size, "temp", len(temp_agg), temp_path.stat().st_size)
    for row in table:
        print(f"{row['name']:16} {row['estimate']:.10f}  SE {row['se']:.4f}  Wald {row['wald']:.2f}")
    print("snow", snow, "mild", mild, "lift", mild - snow)
    print("rounded", rounded_snow, rounded_mild, rounded_mild - rounded_snow)
    print("paper printed", paper_snow, paper_mild)
    print("our wind off", our_wind)
    print("kickers", len(ranked), "missing", missing, "extra", extra)
    print("slope", slope, "t", slope_t, "df", slope_df)
    print("class", cls)
    print("exp", exp["coefficients"]["experience"], exp["coefficients"]["season_year"])
    print("anova", stad["anova_F"], stad["anova_df"], "games", stad["games"])
    print("walk", walk)
    print("vin flags", report["vinatieri"])


if __name__ == "__main__":
    main()
