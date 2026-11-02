SUBSTITUTE DATA: nflverse play-by-play 2000–2011 (open, CC-BY-4.0) instead of the paper's ArmchairAnalysis.com dataset, which is not openly downloadable. The games are the same, but the weather, surface, altitude and precipitation flags must be re-derived from nflverse fields, and nflverse has 11,893 field-goal attempts vs the paper's 11,896.

# BRIEF: Going for Three: Predicting the Likelihood of Field Goal Success with Logistic Regression

## Paper

- Title: Going for Three: Predicting the Likelihood of Field Goal Success with Logistic Regression
- Authors: Torin K. Clark, Aaron W. Johnson, Alexander J. Stimpson (MIT)
- Year: 2013
- Venue: MIT Sloan Sports Analytics Conference research paper
- Link: https://cdn.prod.website-files.com/68d6be744d7efccc2207f571/68d6be744d7efccc220807cf_SSAC13%20-%20Going%20for%20Three.pdf (PDF, 758,646 bytes, HTTP 200)
- Slug: papers/going-for-three/

## Question

- Beyond distance, what changes whether an NFL field goal is good? The paper tests weather, turf, altitude, playoff and game pressure, home/away, and "icing".
- It then asks how kickers, seasons and stadiums rank once those conditions are accounted for, using "added points".

## Data the paper used

- Provider and dataset: ArmchairAnalysis.com NFL data. Models were fit in SPSS/SYSTAT (p2).
- Seasons / competitions / sample size: "All 11,896 field goal attempts from the 2000-2011 NFL seasons (excluding preseason games)" (p2).
- Coding rules (p3 footnotes):
  - conditions are taken at kickoff;
  - altitude means only Denver or Mexico City (Oct 2, 2005);
  - "chance of rain" counts as no precipitation;
  - a timeout by either coach counts as icing.
- Public? No. It is a commercial download.
- License, if it is public: n/a

## Data this page will use

- Source: nflverse play-by-play, release tag `pbp` of nflverse/nflverse-data, files play_by_play_2000…2011.parquet.
- URL: https://github.com/nflverse/nflverse-data/releases/tag/pbp. Per-season URLs and sizes are in `DATA.md`.
- License: CC-BY-4.0 (repo license per the GitHub API). We may copy, display and commit derived data with attribution.
  - Credit line on the page: "Data: nflverse (github.com/nflverse), CC-BY-4.0."
  - Do not commit the raw parquet files (about 199 MB).
- Same data as the paper? No.
- Substitute: yes. The page must show the "Rebuilt on substitute data" callout.
  - **What transfers:** the same games and kicks (11,893 vs 11,896 attempts), distance, outcome, roof, surface, home team.
  - **What does not:**
    - the paper's weather coding;
    - precipitation, which we take from free-text weather (keyword list is ours);
    - temp and wind, which are blank for 23.6% of attempts (domes and closed roofs);
    - the exact Table 2–6 rankings.
- nflverse counts: 11,893 attempts (11,419 REG, 474 POST): 9,605 made, 2,011 missed, 277 blocked.
- Fields used: game_id, play_id, season, season_type, kicker_player_name, field_goal_attempt, field_goal_result, kick_distance, roof, surface, temp, wind, weather, home_team, game_stadium.
- Our flags:
  - cold = temp < 50 with roof outdoors/open;
  - turf = surface ≠ grass;
  - altitude = home_team DEN, or game_id 2005_04_SF_ARI (Estadio Azteca);
  - precipitation = weather text matches rain|snow|shower|drizzle|sleet|flurr|storm, without "chance", outdoors;
  - wind = wind ≥ 10, outdoors.
- Pyodide prep (offline, at build time): filter to field_goal_attempt == 1 in REG/POST and build the flags. Then either:
  - (a) per-kick rows: 11,893 rows, about 690 KB CSV (game_id, play_id, kicker, distance, flags, made); or
  - (b) grouped counts by (distance, cold, turf, altitude, precip, windy): 726 rows, 14,338 bytes.
  - Fit the logistic regression in-browser with a short numpy Newton loop; statsmodels may not be in Pyodide.

## Method, in order

1. **Build the flags** from nflverse fields, as above.
2. **Fit the logistic regression** of made on distance plus the six flags.
   - Paper Table 1 (p3), coefficient (SE, Wald):
     - β0 5.953 (0.220, 25.2, p<0.0005)
     - distance −0.106 (0.003, 35.5)
     - cold −0.341 (0.061, 5.63)
     - turf 0.299 (0.053, 5.62)
     - altitude 0.694 (0.157, 4.43)
     - precipitation −0.280 (0.099, 2.84, p=0.005)
     - wind −0.140 (0.055, 2.55, p=0.011)
   - Not significant: humid p=0.844 (Wald 0.20), postseason p=0.196 (1.29), pressure p=0.539 (0.61), away p=0.501 (0.67), icing p=0.118 (1.56).
3. **Predict the Vinatieri kick and draw the condition curves** (Figure 1, p3). This step produces the figure.
   - The 45-yd kick "converted only 53% of the time"; mild Oakland weather would raise it "by 0.18".
4. **Added points per kick** = 3 × (outcome − p). Example (p4): a 77% kick is +0.69 if made, −2.31 if missed.
5. **Rankings:**
   - Kickers with >50 attempts (55 kickers): Table 2 (p4) and A.2 (p10) for added points; Table 3 (p4) and A.3 (p11) for make %; Table 4 (p4) for rank gaps.
   - Seasons with ≥20 attempts: Table 5 (p5).
   - Stadiums: Table 6 (p5–6).
6. **Trends and classification:**
   - +0.017 added points per attempt per season, t(11) = 5.34, p<0.0005 (Figure 2, p5).
   - Experience +0.017 (Wald 3.21, p=0.001); season year +0.037 (Wald 4.86) (p5).
   - Best cutoff ≈ 37%; neither logistic regression nor SVM beats naive classification (p6).

## Assumptions to put on a slider

- **Kick distance:** yards to the posts. Range 18–65; paper example 45 (Vinatieri).
  - Toggles for cold, precipitation, wind, turf and altitude redraw the Figure 1 curves.
- **Cold-temperature cutoff:** where "cold" starts. Range 30–60°F; paper default 50°F.
  - Refit live on the grouped data. p7: "Temperatures below about 50 °F were all relatively similar".

## Real play

- nflverse game_id `2001_19_OAK_NE`, play_id `3818`: A. Vinatieri, 45 yards, made, Q4 0:32.
  - nflverse desc: "(:32) 4-A.Vinatieri 45 yard field goal is GOOD".
  - Weather: "Snow throughout game, 3-5 inches expected Temp: 25° F, Humidity: 100%, Wind: NE 3 mph"; outdoors, grass.
- Differences from the paper, to show on the page:
  - The paper says "27 seconds left"; nflverse logs the snap at 0:32.
  - The paper dates the game January 19, 2002. nflverse labels it season 2001, week 19 (divisional round).
  - nflverse wind is 3 mph, so our wind flag = 0, but the paper calls it windy (p3).
- Step through: distance term → cold → precipitation → (paper's) wind → probability → added points for the make.

## Figure

- Paper figure: Figure 1 (p3), make probability vs distance for the Vinatieri conditions vs mild weather.
  - Also Figure 2 (p5), the added-points trend by season.
  - Appendix Figures A.1–A.8 and Tables A.4–A.5 are on p8–15.
- Our panel: the same curves recomputed from our nflverse refit, with the paper's printed coefficients as a dashed overlay.
- Reproduction: redraw.

## What should hold up, and what may not

**Pilot refit on nflverse** (ours, not the paper's numbers):
- β0 5.609 (SE 0.133); distance −0.106; cold −0.355; turf 0.292; altitude 0.695; precipitation −0.225; wind −0.166.

**Expect to hold:**
- Every slope is within about 0.06 of Table 1.
- Our refit gives 52.3% for the Vinatieri conditions (cold + precipitation + wind) and +0.175 for mild weather, vs the paper's 53% and +0.18.

**Expect to break:**
- The intercept. The paper's printed β0 = 5.953 gives 60.4% for Vinatieri (76.5% mild), so it doesn't reproduce its own 53%.
  - Table 1's own Wald 25.2 × SE 0.220 ≈ 5.54, closer to the refit; 5.953 may be a typo.
  - Use the refit coefficients and explain this on the page.
- Exact kicker, season and stadium ranks: show them as "our rank vs paper's rank".
- The precipitation and wind flags, given 23.6% missing temp/wind.
- Pressure and icing coding (Table A.1, p9): not rebuilt in the core page.

**Difficulty: 2/5.**
Main risks:
- precipitation coding from free text;
- missing dome weather;
- the inconsistent printed intercept;
- the raw parquet is too large for the browser, so pre-aggregate.

**Paper ranking values for the checker** (quoted):
- Table 2 / A.2, added points per attempt: Bironas 0.262, Gould 0.204, Barth 0.195, Kasay 0.160, Carpenter 0.134 … Christie −0.200, Novak −0.201, Seder −0.342, Cortez −0.405, Richey −0.467. Vinatieri is 16th at 0.0732 (p10).
- Table 3, make %: Hartley 87.7 (57), Stover 86.8 (335), Gould 86.2 (224), Bironas 86.1 (223), S. Graham 85.4 (254) … Rayner 72.2 (90), Novak 71.9 (64), Seder 71.0 (62), Cortez 70.7 (75), Richey 66.1 (56).
- Table 4, rank gap: Janikowski +25, Carpenter +19, Succop +16, Scobee +15, Crosby +14 … Gostkowski −20.
- Table 5, seasons: best Janikowski 2009 +19.4, Rackers 2005 +18.7; worst Marler 2003 −20.0.
- Table 6, stadiums (45-yd kick; 3,410 games; 51 stadiums; ANOVA F(50,3089) = 131.8):
  - Hardest, with ranks printed as 2, 4, 5, 6, 7: Lambeau −0.063, Heinz −0.049, Cleveland −0.049, Soldier −0.047, Arrowhead −0.042.
  - Easiest: Georgia Dome, Metrodome, Superdome and Ford Field each +0.0461; Denver +0.0957.
- UNKNOWN: the paper's exact precipitation keyword list.

## Learning layers

- **Intro animation:** the same 45-yard kick drawn twice, once in Foxborough snow and once in mild Oakland, with the make probability ticking from about 53% to about 70%.
- **Guided build:** required steps before the figure:
  1. build the flags;
  2. fit the logistic regression;
  3. predict the Vinatieri kick;
  4. compute added points.
- **Advanced:**
  - the cold-cutoff sensitivity;
  - the printed-vs-refit intercept;
  - kicker rankings by added points vs make %;
  - the season trend;
  - the classification baseline (naive beats the model, p6).

## Exercises

- **Fill-in-the-blank:** complete `z = b0 + b_dist*45 + b_cold + b_precip + ______` (answer: `b_wind`), then `p = 1/(1+exp(-z))`.
  - With the refit, p ≈ 0.523.
  - Follow-up: added points for the make = 3 × (1 − p) ≈ 1.43.
- **Quick check (primary):** "A kicker makes a kick the model gave 90%. How many added points?"
  - Choices: +0.10 / +0.30 / +2.70. Correct: +0.30.
- **Extra quick checks:**
  - "Why can the same 45-yd kick be 53% in one game and about 70% in another?" Choices: cold, precipitation and wind flags / different kicker / icing. Correct: the weather flags.
  - "Why might make % overrate a dome kicker?" Choices: easier average kicks / domes have shorter goalposts / they kick fewer field goals. Correct: easier average kicks.
- **Glossary terms to add** (key, term, definition):
  - `logistic-regression`, logistic regression: models the log-odds of a yes/no outcome as a straight-line sum of inputs.
  - `log-odds`, log-odds: ln(p/(1−p)).
  - `wald-statistic`, Wald statistic: a significance test statistic; in Table 1 it is about coefficient ÷ standard error.
  - `p-value`, p-value: the chance of an effect this large if there were truly none.
  - `added-points`, added points: 3 × (made − predicted probability), summed or averaged per kicker.
  - `icing`, icing: a timeout called just before the kick.
  - `situational-pressure`, situational pressure: score margin and time left combined into a pressure level (Table A.1).
  - `artificial-turf`, artificial turf: any non-grass playing surface.
  - `altitude-flag`, altitude flag: a game played ≥4,000 ft above sea level (Denver; Mexico City, Oct 2, 2005).
  - `nflverse`, nflverse: an open, community-maintained NFL play-by-play dataset (CC-BY-4.0).

## Out of scope

- The pressure and icing coding of Table A.1.
- The full appendix tables.
- The SVM classifier.
- Reproducing the exact ArmchairAnalysis weather.
- Committing the raw parquet.

## Done when

- [ ] `index.qmd` follows `papers/_template/index.qmd` section for section
- [ ] Every `TODO(paper)` marker is gone
- [ ] `DATA.md` matches the callout (present only if substitute is yes)
- [ ] `quarto render` succeeds
- [ ] The checker has compared the page to the paper
- [ ] Jordan merges. Agents and reviewers do not
