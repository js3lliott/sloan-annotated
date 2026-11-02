# BRIEF: No More Throwing Darts at the Wall: Developing Fair Handicaps for Darts using a Markov Decision Process

## Paper

- Title: No More Throwing Darts at the Wall: Developing Fair Handicaps for Darts using a Markov Decision Process
- Authors: Timothy C. Y. Chan, Craig Fernandes, Rachael Walker
- Year: 2024 (Other Sports track, Paper ID 193939)
- Venue: MIT Sloan Sports Analytics Conference research paper
- Link: https://cdn.prod.website-files.com/68d6be744d7efccc2207f571/68d6be744d7efccc22080818_193939%20-%20No%20More%20Throwing%20Darts%20at%20the%20Wall-%20Developing%20Fair%20Handicaps%20for%20Darts.pdf (PDF, 1,847,052 bytes, HTTP 200)
- Slug: papers/darts-handicaps/

## Question

- How should a 501 darts match be handicapped so that players of different skill have a fair chance?
- Is the current points-per-dart head start fair?
- Could an optimized head start, or a new "dynamic credit" (one perfect throw), do better?

## Data the paper used

- Provider and dataset: Haugh & Wang's fitted bivariate-Gaussian skill models for professional players.
  - "we opt to use the fitted skill models from the most recent study" (p5; ref [2]: Haugh & Wang, "Play like the pros? Solving the game of darts as a dynamic zero sum game").
  - Michael Smith "was chosen to represent the average professional" (p6).
- Seasons / competitions / sample size: the paper doesn't restate the throw sample. Smith's raw counts are in the public Raw_Data.xlsx (see below).
- Public? Yes. https://github.com/wangchunsem/OptimalDarts
- License, if it is public: none. The repo has no license file (GitHub API: license null).

## Data this page will use

- Source: the Haugh & Wang OptimalDarts repo, pinned at commit `f68bedcc592b4bcfda69f6d72d69aede91ebaff1` (2022-02-08 08:14 EST).
  - **This is not on PLAN.md's allowed-source list**; flagged in the scout report.
- URL: https://github.com/wangchunsem/OptimalDarts. Pinned raw URLs are in `DATA.md`; the key file is ALL_Model_Fits.mat (22,400 bytes).
- License: no license, so we may **not** copy or commit the .mat, .xlsx or .py files.
  - The builder fetches them at build/run time from the pinned URLs: build time for precomputed tables, run time via pyfetch for cells that read Σ.
  - The page shows only what we compute, credits Haugh & Wang, and links the repo.
- Same data as the paper? Yes.
  - The paper says it uses these authors' fitted models.
  - Caveat for the checker: the paper doesn't name the exact file or commit.
- Substitute: no. The page must not show the "Rebuilt on substitute data" callout. `DATA.md` says `substitute: no`.
- .mat contents:
  - Structs ModelFit_All_Doubles, ModelFit_B50, ModelFit_T17…T20; 16 players.
  - Smith is player 11 (index 10), per player_lastname_list in function_board.py.
  - Smith's bull (B50) Σ = [[49.47, −1.09], [−1.09, 67.13]] mm².
  - Board radii (mm): 6.35, 15.9, 99, 107, 162, 170.
- Raw_Data.xlsx (Smith):
  - Aiming T20: 3,761 T20, 4,624 S20, 203 ×15, 293 ×5, 58 ×3, 109 ×1; hit rate 0.4157.
  - Aiming D20: 206 D20, 124 S20, 136 recorded as missed.
  - Aiming bull: 23 DB, 50 SB.
- Pyodide prep:
  - Precompute at build time: hit-probability tables P(region | target, ε) for ε = 1…9 on a reduced target grid (about 1–3 MB float32, generated rather than committed if derived files count as copies).
  - Precompute V*(θ, β = 0, i = 3, u = 0) and the policy per ε (small JSON).
  - Live in-browser: β = 0, a coarse target set, θ ≤ 170 (seconds in numpy).
  - Simulate about 1,000 games per click (the paper ran 10,000).

## Method, in order

0. **PPD** (Eq 1, p3–4): points scored ÷ darts thrown. This is the basis of today's heuristic handicap.
1. **Board and skill:**
   - Integrate 𝒩(μ, εΣ) over board regions on "2mm-by-2mm pixels" (p5; the repo uses 1 mm).
   - ε scales Smith's covariance (p6). Figures 3–4 are on p7.
2. **MDP:**
   - States s = (θ ∈ 0…501, β ∈ 0…9, i ∈ 1…3, u ∈ 0…120): "over 1.8 million distinct states" (p4).
   - Actions: 729 throw targets (Figure 2, p5) + 62 credit regions (20 singles, 20 doubles, 20 trebles, SB, DB).
   - Cost: 1 per completed turn.
   - Transitions (Eq 2): win, bust, regular throw, end of turn; mirrored for credits.
3. **Solve** with "a standard policy iteration algorithm" (p8) for V* and the optimal policy.
   - Figures 5–6 (p8–9): ε = 1 is "concentrated at the T20"; at ε = 9 "this policy shifts towards the T19"; at ε = 100 it targets "the centre of the board".
   - Figure 7 (p10): V* vs score; the gap between ε 1 and 2 is larger than between ε 8 and 9.
4. **Handicaps:**
   - Heuristic head start, Eq 6 (p11): start = 501 × PPD_weaker / PPD_stronger. Figure 10 (p12): ε = 9 "would still require roughly two more turns".
   - Optimized head start (Figure 11b, p13): the starting score that equalizes V*.
   - Credits (Figure 12b, p14): ε = 1 "requires just under 6 turns … equivalent to an ϵ = 2 player receiving approximately 3" credits (p11; Figure 9).
5. **Fairness check:** simulate 10,000 games per pair (p14).
   - Figure 13 (p15): P(stronger wins).
   - Figure 14 (p15): turns-to-finish histograms, ε 1 vs 8.
   - Figure 15 (p18): the heuristic.
   - This step produces the figure.

## Assumptions to put on a slider

- **Execution error ε:** the multiplier on Smith's throw covariance. Range 1–9, plus a jump to 100; paper default 1 (average pro).
  - Shows the landing cloud and the distribution of optimal aims moving T20 → T19 → centre.
- **Credits β for the weaker player:** range 0–9; paper default 0.
  - Shows expected turns vs the ε = 1 player's (just under 6), crossing at about 3 credits for ε = 2.
- **Toggle:** handicap type (heuristic / optimized head start / credits), with live simulated win probability.

## Real play

- Michael Smith (OptimalDarts player 11) on a 40 checkout: state θ = 40, i = 3, β = 0 (a "D20 out").
  - Show his real D20 attempts from Raw_Data.xlsx (206 D20 / 124 S20 / 136 recorded as missed).
  - Then show the solver's chosen aim at ε = 1 and ε = 9. Which target the solver picks is not stated in the paper; compute it, don't assume.
- Second scene: the 501 opening dart (T20 vs T19).
- These are throw situations from the public data, not a specific match. The paper has no match example.

## Figure

- Paper figure: Figure 13 (p15), probability the stronger player wins after 10,000 simulated matches: (a) optimized head start, (b) credits.
  - Also Figure 11b (p13) and Figure 12b (p14), the lookup tables; Figure 15 (p18), the heuristic.
- Our panel: the same win-probability matrix from our simulation, beside our recomputed Figure 11b/12b tables.
- Reproduction: redraw.

## What should hold up, and what may not

**Expect to hold:**
- The policy shift T20 → T19 → centre.
- Credits closer to 50/50 than head starts (Figure 13b: 0.47–0.51).
- Appendix A Table 1 (p18), 30 darts at DB, columns DB / SB / Other:

| ε | DB | SB | Other |
|---|---|---|---|
| 1 | 10 | 16 | 4 |
| 2 | 5 | 14 | 11 |
| 3 | 4 | 11 | 15 |
| 4 | 3 | 9 | 18 |
| 5 | 2 | 8 | 20 |
| 6 | 2 | 7 | 21 |
| 7 | 2 | 6 | 22 |
| 8 | 1 | 6 | 23 |
| 9 | 1 | 5 | 24 |

- Our pilot Monte Carlo with Smith's B50 Σ gives ε 2–9 within about 1 dart of the table.

**Expect to break:**
- ε = 1 DB: our 8.8 / 17.7 / 3.4 vs the paper's 10 / 16 / 4.
- Exact V* and lookup tables: the 729-target coordinates are **UNKNOWN** (Figure 2 dot plot only), and the 2 mm vs 1 mm grids differ.
- Figure 7 V* numbers are UNKNOWN (figure only).
- Figure 13/15 cells are read from images.

**Paper lookup values for the checker** (row = stronger ε; columns = weaker ε, ascending):
- Figure 11b, optimized starting score for the weaker player:
  - ε1: 350, 269, 216, 174, 140, 110, 81, 59
  - ε2: 395, 328, 278, 238, 203, 172, 144
  - ε3: 423, 366, 320, 282, 249, 218
  - ε4: 438, 388, 347, 311, 279
  - ε5: 448, 404, 366, 332
  - ε6: 455, 415, 380
  - ε7: 460, 423
  - ε8: 464
- Figure 12b, credits (fractional = average over games):
  - ε1: 2.71, 4.2, 4.9, 5.32, 5.59, 5.77, 5.91, 6.02
  - ε2: 0.95, 2.04, 2.78, 3.26, 3.6, 3.85, 4.04
  - ε3: 0.6, 0.92, 1.34, 1.77, 2.09, 2.35
  - ε4: 0.43, 0.68, 0.84, 0.95, 1.06
  - ε5: 0.32, 0.53, 0.67, 0.77
  - ε6: 0.25, 0.43, 0.55
  - ε7: 0.21, 0.35
  - ε8: 0.17
- Figure 13a: ε1 row about 0.48 → 0.45 (now favours the weaker player). Figure 13b: 0.47–0.51.
- Figure 15, heuristic, ε1 row: 0.54, 0.57, 0.59, 0.62, 0.64, 0.66, 0.68, 0.69. The text says "still has a 70% chance" for ε1 vs 9.
- The paper text says credits apply when "β > 1"; this is likely a typo for β ≥ 1.

**Difficulty: 3/5.**
Main risks:
- the full 1.8M-state solve must be offline;
- the target-set and grid mismatch;
- figure-read values;
- no license, so data is fetched, never committed.

## Learning layers

- **Intro animation:** two players racing from 501, one pro and one ε = 6. The weaker player's dart cloud is visibly wider and they fall turns behind.
- **Guided build:** required steps before the figure:
  1. hit probabilities from εΣ;
  2. a small MDP solve (θ ≤ 170);
  3. V* and the policy;
  4. a handicap from the lookup;
  5. simulate games.
- **Advanced:**
  - why no head start can rescue a very weak player (checkout difficulty);
  - credits vs head start;
  - the ε = 100 extreme;
  - the DB-throw ε test (Appendix A).

## Exercises

- **Fill-in-the-blank:** complete `start = 501 * ppd_weak / ______` (answer: `ppd_strong`), from Eq 6.
  - Alternate: one Bellman step at θ = 40, i = 3, β = 0: V(40) = min over targets of Σ_z P(z | target)·V(next state). Hitting D20 ends the game (cost so far only).
- **Quick check (primary):** "You throw 30 darts at DB and get 2 DB, 8 SB, 20 other. What is your ε?"
  - Choices: 2 / 5 / 9. Correct: 5 (Appendix A Table 1).
- **Extra quick checks:**
  - "Why does a weak player aim at T19 instead of T20?" Choices: T19's neighbours (7, 3) score more on a miss than T20's (5, 1) / T19 is bigger / the rules require it. Correct: the first (p8).
  - "Why can no head start rescue a very weak player?" Choices: their checkout alone can take longer than the pro's whole game / head starts are capped at 100 / the pro throws first. Correct: the first.
- **Glossary terms to add** (key, term, definition):
  - `darts-501`, 501: both players start at 501 and race to exactly 0, finishing on a double.
  - `bust`, bust: going below 0, to 1, or to 0 without a double; the turn's points are wiped.
  - `checkout`, checkout: finishing the game.
  - `double-treble`, double / treble: the thin outer / inner rings scoring 2× / 3×.
  - `bullseye`, DB / SB: double bull (50) / single bull (25).
  - `ppd`, PPD: points per dart.
  - `execution-error`, execution error ε: a multiplier on throw-scatter variance; 1 = average pro.
  - `mdp`, MDP: a model of states, actions, random outcomes and costs, used to find the best policy.
  - `policy-iteration`, policy iteration: alternate evaluating a policy and improving it until it stops changing.
  - `value-function`, V*: expected turns to finish when playing optimally from a state.
  - `dynamic-credit`, dynamic credit: one perfect, guaranteed hit on any chosen region.

## Out of scope

- The full 1.8M-state solve in the browser.
- The paper's exact 729-target set (UNKNOWN).
- The zero-sum game solver (function_solve_zsg_gpu.py).
- Committing or rehosting OptimalDarts files (no license).
- Copying the paper's figures.

## Done when

- [ ] `index.qmd` follows `papers/_template/index.qmd` section for section
- [ ] Every `TODO(paper)` marker is gone
- [ ] `DATA.md` matches the callout (present only if substitute is yes)
- [ ] `quarto render` succeeds
- [ ] The checker has compared the page to the paper
- [ ] Jordan merges. Agents and reviewers do not
