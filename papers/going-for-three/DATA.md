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
  - A small derived file is allowed under CC-BY-4.0 with attribution. The proposed file is `papers/going-for-three/data/fg_agg_2000_2011.csv`: 726 rows, 14,338 bytes; columns dist, cold, turf, alt, precip, windy, sum (made), count.
  - Optionally also a per-kick file of about 690 KB. The builder regenerates it from the URLs above with `code/`, not by hand.
- derived_rules:
  - cold = temp < 50 and roof outdoors/open;
  - turf = surface ≠ grass;
  - alt = home_team DEN, or game_id 2005_04_SF_ARI;
  - precip = weather matches rain|snow|shower|drizzle|sleet|flurr|storm, without "chance", outdoors;
  - windy = wind ≥ 10, outdoors.
  - temp/wind are missing for 23.6% of attempts; treat these as not cold and not windy.
- credit: "Play-by-play data: nflverse (github.com/nflverse/nflverse-data), licensed CC-BY-4.0."
