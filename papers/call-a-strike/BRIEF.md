SUBSTITUTE DATA: Baseball Savant (Statcast search) pitch data for the 2009–2011 regular seasons, pre-binned into a location × count grid, instead of the paper's pitch-level PITCHf/x sample (1,036,335 calls by 75 umpires with ≥7,500 calls). Savant serves the same underlying MLBAM pitch tracking, but without umpire IDs, so umpires must be joined from Retrosheet game logs, and the browser only sees grid counts, not individual calls.

# BRIEF: What Does it Take to Call a Strike? Three Biases in Umpire Decision Making

## Paper

- Title: What Does it Take to Call a Strike? Three Biases in Umpire Decision Making
- Authors: Etan Green, David P. Daniels (Stanford)
- Year: 2014
- Venue: MIT Sloan Sports Analytics Conference research paper
- Link: https://cdn.prod.website-files.com/5f1af76ed86d6771ad48324b/5fee06d10c650358b6bee059_2014_SSAC_What-Does-it-Take-to-Call-a-Strike.pdf (PDF, 711,567 bytes, HTTP 200)
- Slug: papers/call-a-strike/

## Question

- Does the game state change whether a pitch in the same location is called a strike? Game state here means the count and the previous call.
- How large are these biases, measured as a "strike threshold": how sure an umpire must be before he calls a strike half the time?
- The paper finds umpires:
  - avoid calling strike three;
  - avoid calling ball four;
  - avoid two called strikes in a row.
- The biases deepen under time pressure.

## Data the paper used

- Provider and dataset: MLB Advanced Media PITCHf/x pitch-level data with home-plate umpire identities.
- Seasons / competitions / sample size:
  - "calls made in the 2009-11 MLB regular seasons (over one million calls)" (p2).
  - Restricted to "umpires with at least 7500 calls … leaves 75 umpires" (p2 fn 2).
  - Table 1 N = 1,036,335 (p6).
- Public? The PITCHf/x feed was public; the authors' extract with umpire joins is not published.
- License, if it is public: MLBAM terms. The extract has no license.

## Data this page will use

- Source: Baseball Savant Statcast search CSV, 2009–2011 regular season, pulled one day per request.
  - Plus Retrosheet game logs for the home-plate umpire. **Retrosheet is not on PLAN.md's allowed-source list**; flagged in the scout report.
- URL:
  - Savant (one day): https://baseballsavant.mlb.com/statcast_search/csv?all=true&hfGT=R%7C&hfSea=2009%7C&player_type=pitcher&game_date_gt=2009-06-01&game_date_lt=2009-06-01&type=details
  - Retrosheet: https://www.retrosheet.org/gamelogs/gl2009.zip, gl2010.zip, gl2011.zip
- License:
  - Savant data is under MLB's terms of use. Do not commit a bulk download (PLAN.md); commit only the small derived grid named in `DATA.md`, if MLB terms allow.
  - Retrosheet may be used with its required notice (see `DATA.md`).
- Same data as the paper? No.
- Substitute: yes. The page must show the "Rebuilt on substitute data" callout.
  - **What transfers:**
    - the same seasons and pitch-tracking source (MLBAM);
    - location, count, batter stance and strike-zone top/bottom;
    - pooled strike maps and count effects.
  - **What does not:**
    - Savant's 2009–11 location fields may be reprocessed versions of the original feed;
    - there are no umpire IDs in Savant, so umpires come from a Retrosheet join;
    - our call count won't equal 1,036,335;
    - the browser sees binned counts, not individual calls, so the Table 1 model is fit on grid cells.
- Test day 2009-06-01: 1,440,774 bytes; 2,612 pitches; 1,479 called (description ∈ {ball, called_strike, blocked_ball}).
  - At about 550 bytes per pitch, 2009–11 is roughly 1.2–1.3 GB raw. Exact season totals and sizes are UNKNOWN (not downloaded).
  - Savant caps a query at about 25,000 rows, so pull day by day. `pybaseball.statcast()` wraps the same endpoint.
- Fields used: game_pk, game_date, home_team, away_team, inning, at_bat_number, pitch_number, balls, strikes, description, plate_x, plate_z, sz_top, sz_bot, stand, on_1b, batter, pitcher, des. The `umpire` column is empty for these years.
- Pyodide prep (offline):
  - Keep called pitches only.
  - z_n = (plate_z − sz_bot)/(sz_top − sz_bot).
  - last_pitch ∈ {none, ball, called strike}, taken from the previous pitch in the same at-bat.
  - Bin plate_x into 0.1 ft bins over [−2, 2] and z_n into 0.05 bins over [−0.5, 1.5], × balls (0–3) × strikes (0–2) × last_pitch (3) × stand (L/R).
  - Store only nonzero cells (n_called, n_strike): at most 115,200 cells, about 1–2 MB.
  - Per-umpire table: about 75 umpires × 3 states × a coarse 8×8 grid.
  - Smooth in-browser with a Gaussian filter on the numerator and denominator (scipy.ndimage).

## Method, in order

1. **Normalize pitch height** by the batter's zone. Keep called pitches.
2. **Kernel-regress P(strike | location):** a "bivariate Gaussian kernel" with Silverman's bandwidth per axis (p1 fn 1).
   - Figure 1a/1b (p2): center >99% strikes; far outside <1%; "the ring in which the probability of a strike rises from 10% to 90% is a foot wide".
3. **Difference maps by state** (Figure 2, p3): 3 balls, 2 strikes, last pitch ball, last pitch called strike, vs the baseline.
   - Baseline: "fewer than 3 balls and fewer than 2 strikes, and the last pitch in the at-bat was not a call" (p4 fn 8).
   - Drops reach up to about 20 pp at the zone edge.
   - This step produces the figure.
4. **Time pressure** (p3; Figure 3, p4): "For about 2% of calls … These calls occur in 3-ball counts with a runner on first, except for calls with 2 strikes and 2 outs." Time pressure deepens the 2-strike bias.
5. **Semi-parametric model** (p6, Appx A): P(strike) = puh(z1, z2) + ω·xᵀβ, with ω = 1 − 2|p − 0.5|.
   - Table 1 (p6), N = 1,036,335, coefficient (t):
     - 3 balls 0.081*** (14.29)
     - 2 strikes −0.19*** (−37.30)
     - full count −0.025 (−2.45)
     - last pitch ball 0.0049 (1.55)
     - last pitch called strike −0.17*** (−42.01)
   - Borderline calls are strikes "58% of the time" at 3 balls and "only 31%" at 2 strikes.
   - Full count: "about 13 percentage points (0.081−0.19−0.025)".
6. **Strike thresholds** (p4–5; Appx B, p6–7):
   - U(s) = p − (1−p)·xᵀγ_s; U(b) = (1−p) − p·xᵀγ_b; threshold p_j = (1+γ_s)/(2+γ_s+γ_b).
   - p1: the average umpire "needs to be 64% sure" for strike three; the least biased "55% sure".
   - "Bias flips about 1% of calls. Almost once a game" an at-bat ends without the deserved strikeout.
   - Figure 4 (p5) modal thresholds: about 50% (last call ball), about 60% (last call strike), about 35% (3 balls), >60% (2 strikes). Exact modes are UNKNOWN (figure only).

## Assumptions to put on a slider

- **Kernel bandwidth multiplier:** how wide the smoothing kernel is relative to Silverman's rule. Range 0.25×–3×; paper default 1× Silverman.
  - The bandwidth in feet is UNKNOWN; the paper only names the rule.
  - Watch the 10%→90% ring sharpen or blur from "a foot wide".
- **Umpire strike aversion γ_s** (γ_b fixed at 0): range 0–1; unbiased default 0.
  - The threshold (1+γ_s)/(2+γ_s) moves from 50% to 67%. Mark 55% and 64% (p1).
- **Toggle:** count state (0-0 / 3-0 / 0-2 / 3-2) for the difference map, as in Figure 2.

## Real play

- Savant game_pk `244961`, 2009-06-01, NYY @ CLE, inning 3, at_bat_number 15, pitch_number 9.
  - Count 3-2. Pitcher Jeremy Sowers (CLE), batter Brett Gardner (MLBAM 458731).
  - description = ball; plate_x −0.701 ft; z_n 0.248. Savant des: "Brett Gardner walks."
  - Home-plate umpire per the Retrosheet gl2009 row for 20090601 NYA @ CLE: Mark Carlson (carlm901).
- The same at-bat's pitch 3, at 0-2, was also called a ball, at plate_x 0.721 and z_n 0.112. That is a two-strike borderline take.
- Step through: pitch location → baseline P(strike) → state shift → call.

## Figure

- Paper figure: Figure 2 (p3), difference maps of strike probability for four game states vs baseline.
  - Also Figure 1a/1b (p2, pooled map and call density), Figure 3 (p4, time pressure) and Figure 4 (p5, threshold distributions).
- Our panel: the Figure 2 difference maps recomputed from the binned Savant grid, plus the pooled Figure 1a map.
- Reproduction: redraw.

## What should hold up, and what may not

**Expect to hold:**
- The pooled-map shape: >99% center, <1% far out, about a 1 ft transition ring.
- Sign and rough size of the count effects: 3 balls up; 2 strikes down by up to about 19–20 pp in the corners; last called strike down.
- The full-count arithmetic, −0.134.

**Expect to break:**
- Exact N.
- Table 1 t-stats, since the grid-cell fit differs from a pitch-level fit.
- The Figure 2–3 contour values (UNKNOWN; figures only).
- Per-umpire thresholds (Figure 4, 64%/55%), which depend on an exact Retrosheet join that may drop doubleheader or postponed games.

**Difficulty: 4/5.**
Main risks:
- about 550 daily Savant pulls (about 1 GB+), so pre-aggregation is mandatory;
- possible Savant reprocessing of 2009–11 locations;
- the umpire join;
- per-umpire structural fits are slow in-browser, so precompute them.

## Learning layers

- **Intro animation:** the same borderline pitch replayed at 0-0, 3-0 and 0-2, with its strike probability sliding as the count changes.
- **Guided build:** required steps before the figure:
  1. normalize height;
  2. smooth the pooled strike map;
  3. compute the state difference maps.
- **Advanced:**
  - the semi-parametric model with the ω weighting;
  - time-pressure maps;
  - strike thresholds per umpire;
  - bandwidth sensitivity.

## Exercises

- **Fill-in-the-blank:** complete `full_count = 0.081 + (-0.19) + ______` (answer: `-0.025`; total −0.134, "about 13 percentage points").
  - Alternate: `z_n = (plate_z - sz_bot) / ______` (answer: `(sz_top - sz_bot)`), checked on the walkthrough pitch (0.248).
- **Quick check (primary):** "With no bias (γ_s = γ_b = 0), what is the strike threshold?"
  - Choices: 35% / 50% / 64%. Correct: 50%.
- **Extra quick checks:**
  - "Which count makes borderline pitches most likely called strikes?" Choices: 3 balls / 2 strikes / full count. Correct: 3 balls (58%).
  - "Why weight by ω = 1 − 2|p − 0.5|?" Choices: bias only matters for close pitches / to down-weight lefties / to remove time pressure. Correct: close pitches.
- **Glossary terms to add** (key, term, definition). Reuse the existing `statcast` key.
  - `called-pitch`, called pitch: a pitch the batter does not swing at, so the umpire decides ball or strike.
  - `kernel-regression`, kernel regression: a smoothed local average of nearby calls, weighted by distance.
  - `silverman-rule`, Silverman's rule: a standard formula for picking the kernel width from the data's spread and count.
  - `normalized-height`, normalized height: pitch height as a fraction of the batter's own zone, from 0 (bottom) to 1 (top).
  - `game-state`, game state: the count plus the previous call.
  - `strike-threshold`, strike threshold: the true strike probability at which an umpire calls a strike half the time; 50% is unbiased.
  - `time-pressure`, time pressure: a 3-ball count with a runner on first (excluding 2 strikes and 2 outs), where the call must be instant.
  - `semi-parametric`, semi-parametric model: a free-form location map plus simple state terms.
  - `pitchfx`, PITCHf/x: MLB's camera-based pitch tracking, used 2007–2016; Savant hosts its records.

## Out of scope

- Pitch-level refits of Table 1 in the browser.
- Committing any Savant bulk download.
- Exact reproduction of Figure 4 per-umpire thresholds; precomputed and labelled approximate if shown at all.
- Copying the paper's figures.

## Done when

- [ ] `index.qmd` follows `papers/_template/index.qmd` section for section
- [ ] Every `TODO(paper)` marker is gone
- [ ] `DATA.md` matches the callout (present only if substitute is yes)
- [ ] `quarto render` succeeds
- [ ] The checker has compared the page to the paper
- [ ] Jordan merges. Agents and reviewers do not
