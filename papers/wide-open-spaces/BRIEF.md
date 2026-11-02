SUBSTITUTE DATA: Metrica Sports' public anonymized sample tracking (Sample Game 2, 25 Hz) instead of the paper's private TRACAB data (20 Spanish-league matches, and the Jan 2017 FC Barcelona 1-1 Villarreal match), which is not public. Players are anonymous (Player1, Player2, …), the pitch-value net must be retrained on Metrica, and the Table 1/2 player rankings cannot be reproduced.

# BRIEF: Wide Open Spaces: A statistical technique for measuring space creation in professional soccer

## Paper

- Title: Wide Open Spaces: A statistical technique for measuring space creation in professional soccer
- Authors:
  - The PDF prints no author names. The conference site lists Javier Fernández.
  - The paper is commonly cited as Fernández & Bornn (2018), and its video links are on lukebornn.com. Bornn is **not** printed in the PDF; the checker should confirm before the page names him.
- Year: 2018 (Other Sports Track, Paper ID 5675)
- Venue: MIT Sloan Sports Analytics Conference research paper
- Link: https://cdn.prod.website-files.com/68d6be744d7efccc2207f571/68d6be744d7efccc22080634_A%20statistical%20technique%20for%20measuring%20space%20creation%20in%20professional%20soccer.pdf (PDF, 2,171,254 bytes, HTTP 200)
- Slug: papers/wide-open-spaces/

## Question

- Can tracking data measure the off-ball value of a player who:
  - moves into valuable open space ("space occupation"), or
  - drags a defender away to open space for a teammate ("space generation")?
- The paper defines these through:
  - a pitch-control model;
  - a learned pitch-value model;
  - two gain metrics over a time window.

## Data the paper used

- Provider and dataset: TRACAB optical tracking.
- Seasons / competitions / sample size:
  - Pitch-value net: "TRACAB tracking-data of 20 matches of first and second Spanish division, consisting of 2.4 million examples" (p8).
  - Match analysis: FC Barcelona vs Villarreal, January 2017, 1-1. 845 situations, with w = 3 s, δ = 5 m, α = 3 m (p12).
- Public? No.
- License, if it is public: n/a

## Data this page will use

- Source: Metrica Sports sample data. **Not on PLAN.md's allowed-source list**; flagged in the scout report.
  - Pinned commit `e706dd506b360d69d9d123d5b8026e7294b13996` (2021-04-15 12:34 EDT).
  - Sample Game 2 (CSV) for the walkthrough; Games 1 and 2 for retraining the pitch-value net.
- URL: https://github.com/metrica-sports/sample-data. Pinned raw file URLs and sizes are in `DATA.md`.
- License: no license file. The README asks: "Please be responsible with the use of this data" and "If you use it for anything public, please aknowledge the source."
  - Credit on the page: "Tracking and event data: Metrica Sports sample data (github.com/metrica-sports/sample-data)."
  - Do not commit raw tracking. The builder fetches the pinned files at build time and derives the small clip.
- Same data as the paper? No.
- Substitute: yes. The page must show the "Rebuilt on substitute data" callout.
  - **What transfers:**
    - the model formulas (influence, pitch control, Q, SOG/SOL, SG/SGG);
    - 25 Hz positions on a 105 × 68 m pitch;
    - event-synced frames.
  - **What does not:**
    - player identities, since Metrica is anonymized;
    - the TRACAB-trained value surface, which is retrained on 2 Metrica games instead of 2.4M examples;
    - the Barcelona–Villarreal tables (Table 1/2).
    - Metrica has no velocities; we derive them from positions.
- Format: coordinates run 0–1 (×105 and ×68 for metres); 25 Hz; the tracking CSVs have a 3-line header.
- Pyodide prep (at build time):
  - Convert to metres. Smooth velocities, for example with a Savitzky–Golay filter over 7 frames.
  - Cut a clip of about 20 s around the walkthrough goal: about 500 frames × 23 entities, about 0.5 MB.
  - Optionally add a 5 Hz excerpt of the attack for SOG/SGG counting.
  - Train the pitch-value net offline (sklearn MLPRegressor, one hidden layer, Adam) on defensive situations ≥3 s apart from Games 1 and 2. Ship the weights as JSON (about 100 KB) and run the forward pass with numpy in Pyodide.
  - Compute pitch control in-browser on a coarse 1 m grid (105 × 68).

## Method, in order

1. **Player influence** (Eq 1, p4; Eqs 12–13, p18): a bivariate normal f_i normalized by its value at the player, I_i(p,t) = f_i(p,t)/f_i(p_i(t),t).
   - Appendix A.1 (p18–19):
     - Σ_i = R(θ) S S R(θ)⁻¹;
     - S = diag((R_i + R_i·Srat)/2, (R_i − R_i·Srat)/2);
     - Srat = s²/13² (max speed 13 m/s);
     - μ = p_i + 0.5·ṗ_i.
   - Influence radius R_i lies "in the range [4, 10]" m vs distance to the ball. Figure 9 (p19) shows about 4 m at 0 m rising to 10 m by about 18 m, flat after.
   - **The exact formula is UNKNOWN** (figure only).
   - Figure 2 (p5): "Player influence area for player 15 meters away from the ball, running at 6.36 m/s in a 45 degrees angle".
2. **Pitch control** (Eq 2, p5): PC(p,t) = σ(Σ_i I_i − Σ_j I_j), where σ is the logistic function. Figure 3 (p6) shows a team surface.
3. **Pitch value** (Eqs 3–5, p7–8):
   - Target: the sum of defender influence D_ij, capped at 1, on a 21 × 15 grid.
   - Feed-forward net with one hidden layer, trained with Adam on situations ≥3 s apart.
   - 10-fold CV MSE 0.085 (SD 0.001).
   - Figures 4–5 (p8–9) show raw values and values normalized by distance to goal.
   - UNKNOWN: hidden-layer size, learning rate, and the distance-to-goal normalization formula (only "normalized on a [0, 1] range").
4. **Quality of owned space** (Eq 6, p9): Q_i(t) = PC_i(t)·V_i(t). Figure 6 (p10) shows control × value. This step produces the figure.
5. **Gain** G (Eq 7, p10): the text calls it "the mean difference of quality" over [t+1, t+w+1], but the printed formula shows the mean of Q. Exact form is ambiguous.
6. **SOG / SOL** (Eqs 8–9, p10): G ≥ ϵ, or ≤ −ϵ.
   - **ϵ is UNKNOWN** (not stated).
   - Active if speed > 1.5 m/s (p11).
7. **SG / SGG** (Eqs 10–11, p11): ∃ opponent j with d(i′,j,t) ≤ δ ∧ d(i,j,t+w) ≤ δ ∧ d(i′,j,t+w) > δ ∧ d(i,j,t+w) − d(i,j,t) > α. SGG applies when also G ≥ ϵ.

## Assumptions to put on a slider

- **Player speed:** stretches the influence ellipse via Srat = s²/169. Range 0–13 m/s; paper example 6.36 m/s (Figure 2).
- **Influence radius R_i:** overrides the distance-to-ball rule. Range 4–10 m (paper's stated range; default from Figure 9).
- **Window w:** range 1–5 s; paper 3 s. **Closeness δ:** range 2–10 m; paper 5 m. Watch SOG/SGG counts change.

## Real play

- Metrica Sample Game 2, period 2, Home team goal (events file rows 1114–1119):
  - Frame 73877: Player10 interception.
  - Frames 73902 → 73923: Player10 passes to Player8.
  - Frames 73955 → 73983: Player8 crosses to Player9.
  - Frame 73983 (2959.32 s): Player9 heads on target, goal. Away Player18 loses the aerial.
- Compute Q for Player9 and Player8 over w = 3 s (75 frames) from frame 73923.
- Check whether Player9's run is active SOG (>1.5 m/s) and whether any defender was dragged (SG).
- The paper's Barcelona examples can't be identified in public data; this is a labelled substitute.

## Figure

- Paper figure: Figure 6 (p10), pitch control, field value, and value of owned space for the attacking team.
  - Also Figures 2–3 (p5–6), influence and pitch control; Figures 4–5 (p8–9), pitch value; Figure 9 (p19), radius vs distance.
- Our panel: the same three surfaces recomputed at a frame of the walkthrough goal, using our Metrica-trained value net.
- Reproduction: redraw.
- The paper's videos all return HTTP 500 (dead): http://www.lukebornn.com/sloan/field_value.mp4, space_occupation_1.mp4, space_occupation_2.mp4.

## What should hold up, and what may not

**Expect to hold:**
- the influence and pitch-control geometry: σ(1) = 0.73 for a lone player at their own position (our arithmetic);
- ellipse stretch with speed;
- qualitative Figure 4–5 behaviour (value rises near the ball and toward goal).

**Expect to break:**
- the value-net fit: 2 anonymized games vs 2.4M TRACAB examples, so MSE 0.085 will not match;
- velocities from noisy finite differences;
- every Table 1/2 number.

**Table 1 (p13), SOG count (share), ΣSOG:**
- Iniesta 96 (14.8%), 15.77
- Busquets 90, 14.85
- Messi 81, 14.72 (33.33% active)
- A. Gomes 74, 12.58
- Suarez 70, 12.27
- … Digne 26, 3.48
- Iniesta + Busquets + Messi "over 41%"; Messi's SOG is 71% in front of the ball.

**Table 2 (p14), SG generated (share) / received / ΣSGG / SOL:**
- Neymar 28 (18.9%) / 6 / 5.97, SOL 51 / −8.53
- Suarez 25 / 5.60
- Messi 22 / 4.32
- Busquets 15 / 3.83
- Pique 14 / 3.66
- Iniesta 13 / 2.62, SOL 75 / −11.79

These are quoted only; they are not reproducible on public data.

**Difficulty: 4/5.**
Main risks:
- The radius formula, ϵ, net size and distance normalization are UNKNOWN. Choose defaults and label them as ours.
  - A widely shared community replication uses R = min(4 + d³/(18³/6), 10). This is **not in the paper**; verify against Figure 9 first.
- The CPU cost of per-frame pitch control in Pyodide.
- Small training data.

## Learning layers

- **Intro animation:** the walkthrough attack played at 25 Hz, with the pitch-control surface shifting as Player9 runs into the box.
- **Guided build:** required steps before the figure:
  1. one player's influence;
  2. team pitch control;
  3. pitch value from the trained net;
  4. Q = PC × V.
- **Advanced:**
  - SOG/SOL and SG/SGG over the window;
  - sensitivity to w, δ, α and ϵ;
  - the community radius rule vs flat radii.

## Exercises

- **Fill-in-the-blank:** complete `pc = 1 / (1 + np.exp(-______))` for a lone player at their own spot, where influence = 1 (answer: `1`, so PC = 0.731).
  - Alternate: `srat = speed**2 / ______` (answer: `13**2` or `169`). At 6.5 m/s, Srat = 0.25; with R_i = 10, the S diagonals are (10 + 2.5)/2 = 6.25 and (10 − 2.5)/2 = 3.75.
- **Quick check (primary):** "What separates SGG from SOG?"
  - Choices: SGG credits the player whose run pulled a defender off a teammate / SGG counts only goals / SGG ignores the time window. Correct: the first.
- **Extra quick checks:**
  - "Why does a sprinting player's control zone stretch forward?" Choices: covariance rotated and scaled by speed, and centre shifted by 0.5 s of motion / the ball is faster / defenders slow down. Correct: the first.
  - "Can a player have high pitch control but low Q?" Choices: yes, if the space has low value / no, Q equals control. Correct: yes.
- **Glossary terms to add** (key, term, definition). Reuse the existing `tracking-data` key.
  - `pitch-control`, pitch control: the probability that a team would win the ball at each spot.
  - `player-influence`, influence: one player's normalized Gaussian "reach" surface.
  - `covariance-matrix`, covariance matrix: sets the shape and orientation of a 2-D Gaussian.
  - `logistic-function`, logistic (sigmoid): squashes any number into (0, 1).
  - `pitch-value`, pitch value: how much a spot is worth given where the ball is.
  - `feed-forward-net`, feed-forward neural net: layers of weighted sums with nonlinear activations; here one hidden layer.
  - `adam`, Adam: a common gradient-descent optimizer.
  - `sog`, SOG / SOL: space occupation gain / loss beyond threshold ϵ over window w.
  - `sgg`, SG / SGG: space generation (a defender dragged off a teammate) / its gain.
  - `active-occupation`, active occupation: gaining space while moving faster than 1.5 m/s (jogging).

## Out of scope

- Rebuilding Tables 1–2 (private match).
- Training on TRACAB.
- Committing Metrica raw tracking.
- Reviving the dead videos.
- Copying the paper's figures.

## Done when

- [ ] `index.qmd` follows `papers/_template/index.qmd` section for section
- [ ] Every `TODO(paper)` marker is gone
- [ ] `DATA.md` matches the callout (present only if substitute is yes)
- [ ] `quarto render` succeeds
- [ ] The checker has compared the page to the paper
- [ ] Jordan merges. Agents and reviewers do not
