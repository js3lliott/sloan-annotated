# Data notes

- substitute: yes
- paper_source: ArmchairAnalysis.com NFL data, 2000–2011, "All 11,896 field goal attempts … (excluding preseason games)" (p2). Commercial; not public.
- page_source:
  - nflverse play-by-play, release tag `pbp`: https://github.com/nflverse/nflverse-data/releases/tag/pbp
  - Release assets are rebuilt in place and can't be pinned to a commit. Record each asset's size and updated_at at build time, and re-check these before use. Sizes are in bytes; times are EST/EDT as of 2026-11-01; all URLs return HTTP 200.

| File | Bytes | updated_at |
|---|---|---|
| [play_by_play_2000.parquet](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2000.parquet) | 13,404,971 | 2025-07-16 10:29 EDT |
| [play_by_play_2001.parquet](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2001.parquet) | 14,007,738 | 2026-08-13 08:38 EDT |
| [play_by_play_2002.parquet](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2002.parquet) | 14,742,308 | 2026-08-13 08:39 EDT |
| [play_by_play_2003.parquet](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2003.parquet) | 14,620,361 | 2025-04-30 02:35 EDT |
| [play_by_play_2004.parquet](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2004.parquet) | 14,568,240 | 2025-04-30 02:37 EDT |
| [play_by_play_2005.parquet](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2005.parquet) | 14,612,857 | 2025-04-30 02:38 EDT |
| [play_by_play_2006.parquet](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2006.parquet) | 18,555,685 | 2025-04-30 02:33 EDT |
| [play_by_play_2007.parquet](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2007.parquet) | 18,716,524 | 2025-04-30 02:41 EDT |
| [play_by_play_2008.parquet](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2008.parquet) | 18,565,820 | 2025-04-30 02:34 EDT |
| [play_by_play_2009.parquet](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2009.parquet) | 18,905,386 | 2025-04-30 02:36 EDT |
| [play_by_play_2010.parquet](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2010.parquet) | 19,059,048 | 2025-04-30 02:34 EDT |
| [play_by_play_2011.parquet](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2011.parquet) | 19,117,830 | 2025-04-30 02:38 EDT |

  - Total: 198,876,768 bytes. A `.csv.gz` alternative exists for each season (2001 = 13,890,995 bytes).
- license: CC-BY-4.0 (nflverse/nflverse-data). Attribution is required.
- seasons: 2000–2011 regular season and postseason. Sample: 11,893 field-goal attempts (11,419 REG, 474 POST): 9,605 made, 2,011 missed, 277 blocked.
- commit_policy:
  - Do not commit the raw parquet files.
  - Small derived files are allowed under CC-BY-4.0 with attribution. `code/build_fg_table.py` regenerates them from the URLs above. Byte sizes in the table were re-checked when that script downloaded the files; they matched.
  - `data/fg_agg_2000_2011.csv`: 724 rows. Columns `dist, cold, turf, alt, precip, windy, made, n`. `made` is the number of makes and `n` is the number of attempts. This is the table the logistic fit uses.
  - `data/fg_by_temp.csv`: temperature left blank unless the cold rule can see it, so the cold cutoff can be refit. Same other flags.
  - `data/kicker_ranks.csv`, `data/season_added_points.csv`, `data/stadium_difficulty.csv`: summaries from that fit. `data/fit_report.json` is the script's audit of the headline comparisons.
  - No per-kick file is committed.
- derived_rules:
  - cold = temp < 50 and roof outdoors/open;
  - turf = surface ≠ grass, except Heinz Field `dessograss`. Those 201 attempts, seasons 2003–2009, are grass on this page. That is our classification. Steelers.com (11 Feb 2008) calls DD GrassMaster "a 97 percent natural grass surface and root system stabilized by synthetic fibers" (https://www.steelers.com/news/steelers-will-continue-to-play-on-grass-at-heinz-field-959603);
  - alt = home_team DEN, or game_id 2005_04_SF_ARI;
  - precip = weather matches rain|snow|shower|drizzle|sleet|flurr|storm, without "chance", outdoors. That word list is ours. The paper does not print one;
  - windy = wind ≥ 10, outdoors.
  - temp/wind are missing for 23.6% of attempts; treat these as not cold and not windy.
  - A make is `field_goal_result == made`. Missed and blocked are not makes.
  - Kicker ranks group on `kicker_player_id`, because nflverse spells some names with and without a space.
- credit: "Play-by-play data: nflverse (github.com/nflverse/nflverse-data), licensed CC-BY-4.0."
