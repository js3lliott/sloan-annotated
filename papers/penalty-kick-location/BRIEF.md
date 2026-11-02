# BRIEF: Do Behavioral Considerations Cloud Penalty-Kick Location Optimization in Professional Soccer?

## Paper

- Title: Do Behavioral Considerations Cloud Penalty-Kick Location Optimization in Professional Soccer? Classical/Statistical Game Theory & Empirical Testing using Polynomial and ML Regularized Lasso Regression
  - This is the title printed on the PDF.
  - The conference listing instead ends "...Polynomial Regression and ML Gradient Boosting". Use the PDF title.
- Authors: Alivia Uribe, Shane Sanders, Justin Ehrlich, James J. Reade, Carl Singleton
- Year: 2025 (Soccer track, Paper ID 20251395)
- Venue: MIT Sloan Sports Analytics Conference research paper
- Link: https://cdn.prod.website-files.com/68d6be744d7efccc2207f571/68d6be744d7efccc220808ea_Do%20Behavioral%20Considerations%20Cloud%20Penalty-Kick%20Location%20Optimization%20in%20Professional%20Soccer.pdf
  - PDF is 812,034 bytes; HTTP 200.
  - The paper's own code and data: https://github.com/sdsander-syr/soccer_pk_shot_location (printed on p1).
- Slug: papers/penalty-kick-location/

## Question

- If penalty takers only cared about scoring, they would not shoot less often at the spots that score more often. Do they?
- The paper sets up two predictions:
  - A classical 2×2 game, whose mixed equilibrium predicts no link between how often a spot is used and how often it scores.
  - A "statistical game", where nature draws which spot is better on each kick. It predicts a positive link.
- It then tests both against real kicks. It asks whether shooters give up some scoring chance to avoid the embarrassment of missing the target.

## Data the paper used

- Provider and dataset:
  - The authors' own shot-level file of penalty kicks.
  - The goal face is split into 8 cells: top/bottom × left, middle-left, middle-right, right.
- Seasons / competitions / sample size: 536 penalties from the men's UEFA Champions League and Europa League, 2015–2020 (Table 2 n = 536, p10).
- Public? Yes, in the authors' GitHub repo.
- License, if it is public: none stated. The repo has no license file; the GitHub API returns license = null. Treat it as all rights reserved.

## Data this page will use

- Source: the authors' own public files (repo above).
  - This source is **not** on the repo's allowed-source list (StatsBomb, Big Data Bowl, nflverse, Savant). See "Out of scope" and the scout report.
  - Pinned commit: `ff98e29120d8597a6c6b21670fbe43ae7dc816b4` (2024-11-30 00:02 EST).
- URL: the pinned raw files are listed in `DATA.md`. The main inputs are:
  - pk_data_shotlevel_chrono.csv (536 rows): https://raw.githubusercontent.com/sdsander-syr/soccer_pk_shot_location/ff98e29120d8597a6c6b21670fbe43ae7dc816b4/pk_data_shotlevel_chrono.csv
  - pk_data_R.csv (8 partitions): https://raw.githubusercontent.com/sdsander-syr/soccer_pk_shot_location/ff98e29120d8597a6c6b21670fbe43ae7dc816b4/pk_data_R.csv
- License: no license, so we may **not** copy or commit these files.
  - The page fetches them at run time from the pinned URLs, using pyodide.http / pyfetch inside a `{pyodide}` cell.
  - Display is limited to the figures and statistics we compute. Credit the authors and link the repo.
  - Ask the authors before rehosting anything.
- Same data as the paper? Yes. Our pilot reproduces Table 2 Model (1) exactly from these files.
- Substitute: no. The page must not show the "Rebuilt on substitute data" callout. `DATA.md` says `substitute: no`.
- Size and Pyodide fit: about 33 KB in total, so no prep is needed.
  - Columns: Partition, Made, Save, Missed Goal, conversion_rate_other, prop_nc_missed_other, prop_shots_other, top, corner, top_corner. The `_other` columns are leave-one-out values for the kick's own cell.
  - The data has no player, match or date IDs; rows are only in chronological order.

## Method, in order

1. **Solve the 2×2 game** (Table 1, p3). Payoffs (Taker, Goalie):
   - Shoot Center: vs Stay Center (3/10, 7/10); vs Dive Corner (9/10, 1/10).
   - Shoot Corner: vs Stay Center (9/10, 1/10); vs Dive Corner (7/10, 3/10).
   - Result (Eq 3–4, p4): p_t* = 1/4 (Shoot Center), q_G* = 1/4 (Stay Center); π_T* = 3/4, π_G* = 1/4.
2. **Simulate the statistical game** (p5–7):
   - π(Corner) ~ N(0.8, 0.05) and π(Center) ~ N(0.75, 0.05).
   - Corner is optimal with p* ≈ 0.76. Conversion when taken is 0.814 (Corner) vs 0.796 (Center), over 1 billion simulated kicks.
   - Resampling 100 × 100 gives Pearson r(volume, conversion) = +0.729 (p7).
3. **Describe the real kicks** (p9):
   - Top vs bottom shots: off target 12.88% vs 2.48%; saved 5.30% vs 23.51%.
   - Partition correlations: SubsetA (corners) r = −0.749 and SubsetB (middles) r = −0.997.
   - 30 bootstrap resamples give t = −7.71 and −10.85, significant at α = 0.001.
4. **Fit Table 2** (p10): OLS of prop_shots_other on conversion_rate_other and prop_nc_missed_other.
   - Model (1): const −0.794 (0.024); off-target-given-not-converted −0.477 (0.009); conversion 1.492 (0.034); R² 0.852; adj R² 0.852; RSE 0.047 (df 533); F 1,539.231.
   - Model (2): const −1.687 (0.115); off-target −0.445 (0.009); conversion 3.997 (0.317); conversion² −1.748 (0.220); R² 0.868; adj R² 0.867; RSE 0.045 (df 532); F 1,166.289.
5. **Lasso check** (p11): coefficients 1.154 (conversion) and −0.387 (off-target); bootstrapped SE 0.024 / 0.007; best-fit MSE 0.0022. The best λ is UNKNOWN (Figure 4, p12, is image only).
6. **Indifference curves** (Eq 7–10, Figure 5, p12–13). This step produces the figure.
   - Shooters trade 1 pt of conversion for 3.12 pts of on-target rate (0.32 the other way).
   - "optimization utility … 3.12 times as important" (p13). The model explains 85.2% of variation (p14).

## Assumptions to put on a slider

- **Corner-vs-center payoff**, the Table 1 cell "Shoot Corner / Stay Center": the chance a corner shot scores when the keeper stays home. Range 0.70–0.99; paper default 0.90.
  - p*, q* and the game value update. They equal 1/4, 1/4 and 3/4 only at the paper's payoffs.
- **Statistical-game noise**, the SD of π(Corner) and π(Center): range 0.01–0.15; paper default 0.05. Means stay at 0.80 / 0.75.
  - Simulate 100,000 kicks in-browser (the paper used 1 billion). The corner share is ≈ 0.76 at the default.
- **Weight on staying on target** in the shooter's utility: range 0–1. Default implied by the paper: 3.12 : 1 vs conversion (p13). Redraws the indifference line from Eq 9–10.

## Real play

- The public data has no player, match or date IDs, so no named kick can be identified. Say so on the page.
- **Labelled substitute: the kick in data row 7** of pk_data_shotlevel_chrono.csv (pandas index 6).
  - Partition Top Left; Made = 1.
  - Top Left totals (pk_data_R.csv): 52 shots, 43 goals, 3 saves, 6 misses.
  - Leave this kick out:
    - conversion_rate_other = 42/51 = 0.8235
    - prop_nc_missed_other = 6/9 = 0.667
    - prop_shots_other = 51/535 = 0.0953
    - All three match the CSV.
  - Model (1) predicts −0.794 + 1.492·0.8235 − 0.477·0.667 ≈ 0.117, vs the actual 0.095.
- **Contrast kick:** row 8 (index 7), Bottom Middle Left, with conversion 0.574 and miss share 0.
- **Partition counts** (shots / makes / saves / misses):

| Partition | Shots | Makes | Saves | Misses |
|---|---|---|---|---|
| TL | 52 | 43 | 3 | 6 |
| TML | 23 | 18 | 1 | 4 |
| TMR | 29 | 21 | 3 | 5 |
| TR | 28 | 26 | 0 | 2 |
| BL | 188 | 149 | 34 | 5 |
| BML | 48 | 28 | 20 | 0 |
| BMR | 36 | 24 | 12 | 0 |
| BR | 132 | 98 | 29 | 5 |

## Figure

- Paper figure: Figure 5 (p12–13), indifference curves between conversion rate and on-target rate.
  - Supporting: Figure 3 (p8), GAM heat maps of conversion rate vs volume over the goal face; Figure 4 (p12), Lasso fit vs λ.
- Our panel:
  - Recompute the Model (1) fit and draw the Eq 9–10 indifference line (slope 3.12).
  - Overlay the 8 partitions (volume vs conversion) from pk_data_R.csv.
  - Optional: a goal-face heat map. The paper's GAM settings are UNKNOWN, so our smoother will differ.
- Reproduction: redraw. No permission to reproduce the PDF figure.

## What should hold up, and what may not

**Expect to hold** (checked by our pilot in numpy):
- Model (1) coefficients −0.794 / −0.477 / 1.492 and R² 0.852.
- The p9 rates (17/132, 10/404, 7/132, 95/404).
- SubsetB r = −0.997.
- The 2×2 equilibrium 1/4, 1/4, 3/4.
- Statistical-game corner share ≈ 0.76.

**Expect to break, or only approximately:**
- SubsetA r comes out at −0.751 vs the paper's −0.749.
- Lasso coefficients: the paper used R glmnet; scikit-learn will differ slightly.
- Figure 3 GAM surfaces (settings UNKNOWN).
- The resampling r = +0.729 and the 1-billion-kick figures, which use a smaller in-browser sample.
- The paper's α wording ("α = 0.000000000000001", p7) is odd. Quote it; don't reinterpret it.

**Difficulty: 2/5.**
Main risks:
- figure-only results (Figure 3 GAM, Figure 4 λ path);
- no kick identifiers;
- no license, so data is fetched at run time and never committed.

## Learning layers

- **Intro animation:** eight goal cells fill with dots as 536 kicks land. The top corners glow with a high conversion rate but get few dots.
- **Guided build:** required steps before the figure:
  1. solve the 2×2 game;
  2. simulate the statistical game;
  3. compute top/bottom miss and save rates;
  4. fit Model (1).
- **Advanced:**
  - Model (2) with the squared term.
  - The Lasso check.
  - Partition correlations with bootstrap.
  - The sensitivity of the 3.12 trade-off to dropping one partition.

## Exercises

- **Fill-in-the-blank:**
  - Complete `conv_other = (43 - ______) / (52 - 1)` for the row 7 Top Left kick (answer: `1`, giving 0.8235).
  - Then predict with Model (1) (answer ≈ 0.117).
  - Alternate: solve Eq 3, .7p + .1(1−p) = .1p + .3(1−p), for p (answer 1/4).
- **Quick check (primary):** "In Model (1), what sign would a pure scoring-maximiser give the off-target coefficient?"
  - Choices: positive / zero / negative.
  - Correct: zero. The fitted value is −0.477, which is the behavioral effect.
- **Extra quick checks:**
  - "In the 2×2 game, why is the shooter indifferent at the keeper's mix?" Choices: both shots pay 3/4 / corners always score / the keeper never dives. Correct: both pay 3/4.
  - "Top shots convert more per attempt. Why are they used less?" Choices: they miss the frame more (12.88% vs 2.48%) / keepers save them more / they are illegal. Correct: they miss the frame more.
- **Glossary terms to add** (key, term, definition):
  - `msne`, mixed-strategy Nash equilibrium: each player randomises so the other gains nothing by changing.
  - `best-response`, best response: the move that does best against a given opponent move.
  - `goal-partition`, partition: one of the 8 cells of the goal face used to bin kicks.
  - `conversion-rate`, conversion rate: goals divided by attempts to a cell.
  - `leave-one-out`, leave-one-out: a statistic computed without the current row, so the row cannot influence itself.
  - `off-target-share`, off-target given not converted: misses ÷ (misses + saves) for a cell.
  - `ols`, OLS: ordinary least squares regression.
  - `lasso`, Lasso: regression that shrinks coefficients with an L1 penalty λ.
  - `bootstrap`, bootstrap: resampling the data to estimate how much a statistic varies.
  - `indifference-curve`, indifference curve: combinations of two rates the shooter likes equally.

## Out of scope

- Re-running 1 billion simulated kicks.
- Reproducing the Figure 3 GAM exactly (settings UNKNOWN).
- Naming players or matches (not in the data).
- Committing or rehosting the authors' CSVs (no license).
- Copying the paper's figures.

## Done when

- [ ] `index.qmd` follows `papers/_template/index.qmd` section for section
- [ ] Every `TODO(paper)` marker is gone
- [ ] `DATA.md` matches the callout (present only if substitute is yes)
- [ ] `quarto render` succeeds
- [ ] The checker has compared the page to the paper
- [ ] Jordan merges. Agents and reviewers do not
