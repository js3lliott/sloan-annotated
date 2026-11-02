# CLAUDE.md

Guidance for coding agents working in this repository. Jordan approves every merge. Do not merge, do not enable auto-merge, and do not ask an admin to merge for you.

## What this is

A Quarto website that rebuilds MIT Sloan Sports Analytics Conference papers one page at a time. Readers run Python in the browser. The layout is fixed. `PLAN.md` is the spec. `papers/_template/` is the implementation of that spec.

## Conventions

- One page design. Copy `papers/_template/` to `papers/<name>/`. Keep the level-2 headings and their order. See `papers/README.md`.
- `<name>` is lowercase and hyphenated. It must not start with `_`. Quarto does not render underscore paths unless `_quarto.yml` lists them.
- New paper pages are rendered by the `papers/*/*.qmd` entry already in `_quarto.yml`. Add the page to the listing in `papers/index.qmd` if a glob does not pick it up.
- The website format is `html`. The vendored Quarto Live 0.1.3 extension attaches its filter to that format. Do not switch the project to `format: live-html`. This release does not define that format.
- Runnable code is a `{pyodide}` cell. Do not add `{python}` cells. Those execute during `quarto render` and break the static GitHub Pages build.
- Paper pages keep `engine: markdown` and `filters: [live]` in the YAML, copied from the template. The markdown engine stops Quarto from sending `{pyodide}` cells to Jupyter. The `live` filter is what turns those cells into editors. Without it they render as static code.
- Hide `{ojs}` widget source with `//| echo: false`. The JavaScript stays in the `.qmd` and off the page.
- Keep each Pyodide cell in sync with the module in `papers/<name>/code/`. The cell has to run without a local file mount. Repeating a short function is expected. Say which file it mirrors.
- Charts in the browser use Observable JS (`{ojs}`): Plotly for the assumption slider, D3 for a play diagram. Quarto provides `d3` and `Inputs` to OJS cells.
- Placeholders use the exact token `TODO(paper)`. A paper pull request is not ready while any remain. The template is allowed to keep them.
- Do not invent paper results, samples, or author names. If the brief does not state a fact, read the paper or leave a `TODO(paper)`.
- Glossary definitions live in `assets/glossary.json`. Mark a term with `<button type="button" class="glossary-term" data-term="key">`. The key must exist in the JSON.
- Quick checks are `<form class="quick-check" data-answer="...">`. Each radio group needs a `name` unique on that page.
- Fill-in-the-blank uses a `{pyodide}` exercise cell, a `______` blank of at least six underscores, a `{.hint}` div, a solution cell, and a `#| check: true` cell. Copy the template's wiring.

## How to add a paper

1. Read `PLAN.md`, `papers/_template/BRIEF.md`, and the paper.
2. If you are scouting, stop after a solid `papers/<name>/BRIEF.md`.
3. If you are building, copy the whole `_template` directory, then replace the toy. Wire the real data notes in `DATA.md` before writing numbers into the page.
4. Open one pull request for that paper's page, code, data notes, and figures. Do not mix two papers. Do not restyle the site in a paper PR.
5. Run `quarto render` from the repo root. Fix the failure. Do not merge.

## Data and licensing

Allowed sources for the first wave are the eight below. The first five papers, in order, are in `PLAN.md` and `papers/index.qmd`. Read the license before copying anything into the repo.

Files without a clear license are linked at a pinned commit and fetched at build or run time, never copied into the repo.

- Do not commit raw tracking dumps, full Statcast extracts, or the StatsBomb open-data tree.
- `DATA.md` records `substitute: yes` or `substitute: no`, the paper's source, our source, the license, and the sample.
- A small derived file is allowed only when the license permits it and `DATA.md` names the file. A source file with no clear license is not that kind of file.
- Paper figures: redraw, or reproduce only with permission. Cite the figure number. Do not drop a PDF screenshot in `figures/` and call it fair.

License notes for the last four were read from each source's own page on 2 November 2026. Pins are the commits already in that paper's `DATA.md`.

1. [StatsBomb open data](https://github.com/statsbomb/open-data). Follow the license in that repository. Credit StatsBomb as that license requires.
2. A named NFL Big Data Bowl release. Follow that release's data terms, link the release in `DATA.md`, and name it on the page. Do not commit the tracking files.
3. [nflverse](https://github.com/nflverse). nflverse-data is CC-BY-4.0. Credit: `Play-by-play data: nflverse (github.com/nflverse/nflverse-data), licensed CC-BY-4.0.`
4. [Baseball Savant](https://baseballsavant.mlb.com/). MLB's terms. Do not commit a bulk download. Credit: `Pitch data: MLB Advanced Media via Baseball Savant (baseballsavant.mlb.com).`
5. [Penalty-kick authors' repository](https://github.com/sdsander-syr/soccer_pk_shot_location), commit `ff98e29120d8597a6c6b21670fbe43ae7dc816b4`. No license is stated: the repository page reports none, and that commit has no license file. Credit: `Penalty data: Uribe, Sanders, Ehrlich, Reade & Singleton (2025), github.com/sdsander-syr/soccer_pk_shot_location.`
6. [OptimalDarts](https://github.com/wangchunsem/OptimalDarts), commit `f68bedcc592b4bcfda69f6d72d69aede91ebaff1`. No license is stated: the repository page reports none, and `readme.txt` at that commit states none. Credit: `Skill models: M. B. Haugh & C. Wang, 'Play like the pros? Solving the game of darts as a dynamic zero sum game' (github.com/wangchunsem/OptimalDarts).` Do not paste the repository's code into `code/`.
7. [Metrica Sports sample tracking data](https://github.com/metrica-sports/sample-data), commit `e706dd506b360d69d9d123d5b8026e7294b13996`. No license file. The README at that commit, under "Legal stuff", states: "Please be responsible with the use of this data." and "If you use it for anything public, please aknowledge the source." Credit: `Tracking and event data: Metrica Sports sample data (github.com/metrica-sports/sample-data). Players and teams are anonymized.`
8. [Retrosheet](https://www.retrosheet.org/). Terms: [notice.txt](https://www.retrosheet.org/notice.txt). Game logs: [the game-log index](https://www.retrosheet.org/gamelogs/). The notice says recipients may make any desired use of the information, including a commercial product, if this statement appears prominently. Use it verbatim as the credit line:

```
     The information used here was obtained free of
     charge from and is copyrighted by Retrosheet.  Interested
     parties may contact Retrosheet at "www.retrosheet.org".
```

## Substitute data

The callout is mandatory when `substitute: yes` and forbidden when `substitute: no`.

```markdown
::: {.callout-warning .substitute-data}
## Rebuilt on substitute data

[Paper dataset] is not what this page fits. This page uses [public dataset].

- Paper data: ...
- This page: ...
- What still transfers: ...
- What does not: ...
:::
```

"Public" does not mean "the same data." Tracking rebuilt on event data is a substitute. A private Statcast extract rebuilt on Baseball Savant is a substitute unless the brief shows they are the same files. nflverse in place of an author-built play-by-play file is a substitute.

## Render checks

Before a pull request is ready:

- `quarto render` exits 0.
- The new page opens, the Pyodide cell runs, the slider moves the chart, the blank can be answered, the quick check responds, and a glossary term shows its definition.
- The substitute callout matches `DATA.md`.
- Headings match the template. No second layout, no new global CSS unless a paper cannot be read without it. Prefer a local fenced div.

CI renders on pull requests and deploys to GitHub Pages from `main` only. A green render is not a merge.

## Do not

- Do not merge.
- Do not deploy from a laptop with `quarto publish`.
- Do not upgrade Quarto Live inside a paper PR. The extension is shared.
- Do not set `pyodide.resources` at the project root to a broad folder. An empty list is intentional, so the filter does not try to mount every project asset into the browser filesystem. A single paper page may set its own small resource list if a cell must read a local file.
