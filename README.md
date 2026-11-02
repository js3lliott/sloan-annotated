# Sloan Annotated

An interactive learning site that rebuilds MIT Sloan Sports Analytics Conference research papers. A page is for learning the paper: the question, the data, the method in runnable code, the paper's figure beside ours, and a clear note when the rebuild used substitute data.

Code runs in the browser with Pyodide. Charts are Plotly or D3. The site is a Quarto project published to GitHub Pages. Claude Code and Cursor do the implementation. Jordan approves every merge.

## Preview locally

Install [Quarto](https://quarto.org/docs/get-started/) 1.8 or newer. The Quarto Live extension is already in `_extensions/`, so you do not need `quarto add` for a checkout of this repo.

From the repository root:

```bash
quarto preview
```

That serves the site and reloads as you edit. Open the template at `papers/_template/index.qmd` and run the code cell, move the distance-penalty slider, fill the blank, and submit the quick check.

A full static build, the same one CI runs:

```bash
quarto render
```

Output lands in `_site/`, which is gitignored. The template page does not need a local Python kernel. Cells marked `{pyodide}` run in the browser after the page loads. Do not add `{python}` cells that execute during `quarto render`.

## Repository layout

```
_quarto.yml                 site config and the render list
_extensions/r-wasm/live/    vendored Quarto Live (Pyodide cells and exercises)
index.qmd                   landing page
about.qmd                   what the site is and who merges
PLAN.md                     goals, template, pipeline, first papers
CLAUDE.md                   instructions for coding agents
assets/glossary.json        shared hover-glossary definitions
assets/learning.js          glossary tooltips and quick-check grading
styles/theme.scss           theme
papers/README.md            per-paper directory contract
papers/index.qmd            paper listing
papers/_template/           the one page template, rendered as a demo
  BRIEF.md                  spec a scout fills in
  index.qmd                 section order and working widgets
  DATA.md                   source, license, substitute flag
  code/                     Python the cells stay in sync with
  figures/                  paper figure and our rebuild
.github/workflows/pages.yml render on every PR, deploy from main
.cursor/rules/              editor rules for the same conventions
```

`PLAN.md`, `CLAUDE.md`, `README` files, and `DATA.md` are not website pages. `_quarto.yml` lists the `.qmd` files that render. A new paper at `papers/<name>/index.qmd` is picked up by the `papers/*/*.qmd` glob. `<name>` must not start with `_`.

## Contribution workflow

1. **Scout.** Write `papers/<name>/BRIEF.md` from `papers/_template/BRIEF.md`. Name the paper, the question, the public data, and whether that data is a substitute.
2. **Build.** One pull request turns the brief into `index.qmd`, `code/`, `DATA.md`, and `figures/`. Copy `papers/_template/`. Keep its section order. Remove every `TODO(paper)` marker.
3. **Check.** Someone other than the builder compares the page to the paper: question, sample, figure, and the substitute label.
4. **Merge.** Jordan merges. Agents do not. Reviewers do not merge on Jordan's behalf.

`quarto render` has to succeed before a page is ready. The GitHub Actions workflow renders on pull requests and deploys to GitHub Pages only from `main`.

## Data

Allowed sources for the first papers are listed in `PLAN.md`, with the link, the license or terms, and the credit line for each:

- [StatsBomb open data](https://github.com/statsbomb/open-data)
- NFL Big Data Bowl releases
- [nflverse](https://github.com/nflverse)
- [Baseball Savant](https://baseballsavant.mlb.com/)
- [Penalty-kick authors' repository](https://github.com/sdsander-syr/soccer_pk_shot_location)
- [OptimalDarts](https://github.com/wangchunsem/OptimalDarts)
- [Metrica Sports sample data](https://github.com/metrica-sports/sample-data)
- [Retrosheet](https://www.retrosheet.org/)

Follow each source's license. Files without a clear license are linked at a pinned commit and fetched at build or run time, never copied into the repo. Do not commit raw dumps. If the page is not using the paper's own data, it must show a callout titled **Rebuilt on substitute data**.
