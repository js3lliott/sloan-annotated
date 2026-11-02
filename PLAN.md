# Plan

## Goals

Rebuild MIT Sloan Sports Analytics Conference research papers as a learning site. A reader should be able to see the question the paper asks, run the method, move a key assumption, and compare our figure with the paper's. The site is one Quarto project in this repository, with Plotly and D3 in the browser and Python through Pyodide, hosted on GitHub Pages.

The model is an annotated implementation, aimed at learning rather than at a library. Every paper uses the same page. The first wave is five papers on public data. A rebuild that is not on the paper's data is labelled.

Claude Code and Cursor write the pages. Jordan approves every merge.

## Page template

`papers/_template/index.qmd` is the only page layout. Copy the directory. Keep these level-2 headings, in order:

| Section | Job |
| --- | --- |
| Intro | Learning layer 1. A short open and an animation of the question. |
| The question | The paper's question, in its terms. |
| The data | What the paper used, what we used, the license, and the substitute callout when it applies. |
| Guided build | Learning layer 2. The method in order, with Pyodide cells, one fill-in-the-blank, and a slider on a key assumption. |
| A real play | A step-through of one real possession, play, or pitch from the public data. |
| Check yourself | A quick conceptual check. |
| Paper figure and our rebuild | The paper's figure beside the figure this page recomputes. |
| What held up and what didn't | A specific account of the match and the miss. |
| Advanced | Learning layer 3. A sensitivity, a baseline, or a fragile case. |
| The original | Authors, year, venue, and a link to the paper. |

Learning layers are not separate sites. They are those three stretches of the same page: intro, guided build, advanced.

Interactive pieces the template already runs, so a new page reuses them instead of inventing new chrome:

- `{pyodide}` cells via the vendored Quarto Live extension, edited and run in the browser
- a fill-in-the-blank exercise (`______`), with a hint, a solution, and a grade
- an Observable slider bound to a Plotly chart
- a D3 frame stepper for the real play
- a `form.quick-check` graded by `assets/learning.js`
- `button.glossary-term` definitions from `assets/glossary.json`
- a two-column figure block
- a callout with the class `substitute-data` and the title "Rebuilt on substitute data"

`TODO(paper)` marks a line the builder must replace. A finished paper page has none left.

## Pipeline

One paper, four roles. The merge is Jordan's.

1. **Brief.** A scout writes `papers/<name>/BRIEF.md` from `papers/_template/BRIEF.md`. The brief names the question, the public source, the slider, the play, the figure, and whether the source is a substitute. `<name>` is lowercase and hyphenated and does not start with `_`.
2. **Build pull request.** A builder copies `papers/_template/` to `papers/<name>/` and replaces the demo with the paper. The pull request contains the brief (if it is not already on `main`), `index.qmd`, `code/`, `DATA.md`, and `figures/`. It does not contain a second page design.
3. **Check.** A checker, not the builder, reads the page against the paper. The question matches. The sample matches `DATA.md`. The figure comparison is honest. The substitute callout is present if and only if `DATA.md` says `substitute: yes`. `quarto render` succeeds. No `TODO(paper)` remains.
4. **Merge.** Jordan merges into `main`. That push renders the site and deploys it. Agents do not merge. A green check is not permission to merge.

## First papers

Five papers. Public data only, from StatsBomb open data, the NFL Big Data Bowl, nflverse, or Baseball Savant. Do not commit the raw dumps. Record the URL, license, and sample in `DATA.md`.

| Paper | Source for the rebuild | Substitute |
| --- | --- | --- |
| William Spearman, "Beyond Expected Goals," 2018 Sloan research paper. [Public copy](https://www.researchgate.net/publication/327139841_Beyond_Expected_Goals). Off-ball scoring from tracking. | [StatsBomb open data](https://github.com/statsbomb/open-data), event data and freeze frames. Follow that repository's license. | **Yes.** Event data is not the paper's tracking. The callout stays, and it says what does not transfer. |
| Javier Fernández, Luke Bornn, and Dan Cervone, "Decomposing the Immeasurable Sport," 2019. [Conference page](https://www.sloansportsconference.com/research-papers/decomposing-the-immeasurable-sport-a-deep-learning-expected-possession-value-framework-for-soccer). Expected possession value from full tracking. | StatsBomb open data, same license rule. | **Yes.** A public event feed is not their tracking model. Say so in the callout. |
| Michael Horton, "Learning Feature Representations from Football Tracking." [Conference page](https://www.sloansportsconference.com/research-papers/learning-feature-representations-from-football-tracking). The paper uses the 2019 NFL Big Data Bowl tracking release. | That same 2019 Big Data Bowl tracking release, under the competition's data terms. Link it. Do not commit the tracking files. | **No**, when the page uses that release. Any other feed, including nflverse play-by-play, is a substitute and must be labelled. |
| Connor Heaton and Prasenjit Mitra, "Learning Contextual Event Embeddings to Predict Player Performance in the MLB." [Conference page](https://www.sloansportsconference.com/research-papers/learning-contextual-event-embeddings-to-predict-player-performance-in-the-mlb). Pitch sequences. | [Baseball Savant](https://baseballsavant.mlb.com/) pitch-level files, under MLB's terms. Do not commit a bulk download. | **Only if** the paper's file is not the public Savant extract (different seasons, or fields Savant does not publish). The brief says which, before the page claims they are the same data. |
| A. W. Johnson, A. J. Stimpson, and T. Clark, "Turning the Tide: Big Plays and Psychological Momentum in the NFL," 2012 Sloan conference paper (poster). [Library record](https://hsl.mit.edu/biblio/turning-tide-big-plays-and-psychological-momentum-nfl-poster/). Play-by-play, 2000–2010. | [nflverse](https://github.com/nflverse) play-by-play. Attribute nflverse. Commit a small derived sample only if the license allows and `DATA.md` names it. | **Yes.** nflverse is a later public charting, not the authors' extract. Map seasons and fields in the callout. |

A later paper can join this list only after one of these five has a merged page, unless Jordan asks otherwise. Three to five is the bound for the start.

## Definition of done

A paper page is done when all of these are true:

- `BRIEF.md` is filled in, and the page follows it.
- The ten sections and three learning layers above are present, in order.
- The reader can run the method in a `{pyodide}` cell.
- A slider moves one assumption the paper depends on, and a chart updates.
- There is a fill-in-the-blank step and a quick-check question, and both can be answered from the page.
- Glossary terms the page needs are in `assets/glossary.json` and marked in the prose.
- One real play, possession, or pitch from the stated data is stepped through. If the public data cannot identify the paper's example, the page says so and walks a labelled substitute.
- The paper's figure and our rebuild are side by side, with the figure number and the sample.
- "What held up and what didn't" names a comparison, not a vibe.
- The original paper is linked.
- `DATA.md` records source, license, sample, and `substitute: yes` or `substitute: no`.
- The "Rebuilt on substitute data" callout is on the page if and only if `substitute: yes`. Its text names the paper's data, our data, what transfers, and what does not.
- No `TODO(paper)` remains.
- `quarto render` exits 0.
- A checker has signed off against the paper.
- Jordan has merged the pull request.

## Substitute-data rule

Public data and the paper's data are different facts.

- If the page uses the paper's own public files, `DATA.md` says `substitute: no`, and the page does not show the substitute callout.
- If the page uses anything else, including a public dataset that merely resembles the paper's, `DATA.md` says `substitute: yes`, and the page shows a warning callout with the class `substitute-data` and the heading "Rebuilt on substitute data."
- The callout is specific. "We used public data" is not a label. Name both datasets, the seasons, and the features that will not match the paper's tables or figures.
- Do not quietly swap tracking for event data, or a private Statcast extract for a Savant download, and then present the figure as a reproduction.

The template page shows the callout filled in, because its toy curve is not any paper's data. That demo is the pattern. It is not a paper result.
