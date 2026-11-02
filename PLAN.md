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

Five papers, in this order. `papers/index.qmd` repeats the same order in its `paper-order` front matter and in the table. Do not sort either list another way.

Each paper already has a directory. None of them has `index.qmd` yet, so the site says the page is coming soon and links the directory. Do not link a missing page. A later paper can join this list only after one of these five has a merged page, unless Jordan asks otherwise.

| Order | Paper | Directory | Source for the rebuild | Substitute |
| --- | --- | --- | --- | --- |
| 1 | Penalty-kick location (Uribe, Sanders et al. 2025). Alivia Uribe, Shane Sanders, Justin Ehrlich, James J. Reade, and Carl Singleton. "Do Behavioral Considerations Cloud Penalty-Kick Location Optimization in Professional Soccer?" [PDF](https://cdn.prod.website-files.com/68d6be744d7efccc2207f571/68d6be744d7efccc220808ea_Do%20Behavioral%20Considerations%20Cloud%20Penalty-Kick%20Location%20Optimization%20in%20Professional%20Soccer.pdf). | `papers/penalty-kick-location/` | The authors' repository. Pin the commit in `DATA.md` and fetch it. | **No.** The page uses the authors' files. |
| 2 | Going for Three (Clark, Johnson, Stimpson 2013). Torin K. Clark, Aaron W. Johnson, and Alexander J. Stimpson. "Going for Three: Predicting the Likelihood of Field Goal Success with Logistic Regression." [PDF](https://cdn.prod.website-files.com/68d6be744d7efccc2207f571/68d6be744d7efccc220807cf_SSAC13%20-%20Going%20for%20Three.pdf). | `papers/going-for-three/` | nflverse play-by-play, 2000–2011. The paper used Armchair Analysis. | **Yes.** nflverse is a later public charting, not the authors' extract. Map seasons and fields in the callout. |
| 3 | What Does it Take to Call a Strike? (Green & Daniels 2014). Etan Green and David P. Daniels. "What Does it Take to Call a Strike? Three Biases in Umpire Decision Making." [PDF](https://cdn.prod.website-files.com/5f1af76ed86d6771ad48324b/5fee06d10c650358b6bee059_2014_SSAC_What-Does-it-Take-to-Call-a-Strike.pdf). | `papers/call-a-strike/` | Baseball Savant pitch-level files, 2009–2011, plus Retrosheet game logs for the home-plate umpire. | **Yes.** The authors' umpire-joined extract is not published. Savant has no umpire id. |
| 4 | Wide Open Spaces (Fernández & Bornn 2018). "Wide Open Spaces: A statistical technique for measuring space creation in professional soccer." [PDF](https://cdn.prod.website-files.com/68d6be744d7efccc2207f571/68d6be744d7efccc22080634_A%20statistical%20technique%20for%20measuring%20space%20creation%20in%20professional%20soccer.pdf). | `papers/wide-open-spaces/` | Metrica Sports sample tracking data. The paper used private TRACAB tracking. | **Yes.** Anonymized sample matches are not the paper's tracking. Say what does not transfer. |
| 5 | Fair darts handicaps (Chan, Fernandes, Walker 2024). Timothy C. Y. Chan, Craig Fernandes, and Rachael Walker. "No More Throwing Darts at the Wall: Developing Fair Handicaps for Darts using a Markov Decision Process." [PDF](https://cdn.prod.website-files.com/68d6be744d7efccc2207f571/68d6be744d7efccc22080818_193939%20-%20No%20More%20Throwing%20Darts%20at%20the%20Wall-%20Developing%20Fair%20Handicaps%20for%20Darts.pdf). | `papers/darts-handicaps/` | OptimalDarts, the Haugh and Wang skill-model fits. Pin the commit in `DATA.md` and fetch it. | **No.** The page uses those fits. The paper does not name the commit. |

Record the URL, license, and sample in `DATA.md`.

## Allowed sources

A rebuild may use the sources in this list. The first five papers use the source named for them above. Do not commit raw dumps.

Files without a clear license are linked at a pinned commit and fetched at build or run time, never copied into the repo.

License notes for the four sources added with this list were read from each source's own page on 2 November 2026. Where a source states no license, this file does not invent one. Pins below are the commits already recorded in that paper's `DATA.md`. A note in that file that still says the source is waiting on approval is superseded by this list.

### StatsBomb open data

- Link: https://github.com/statsbomb/open-data
- License: follow the license in that repository.
- Credit: credit StatsBomb as that license requires.

### NFL Big Data Bowl

- Link: the named release the page uses. Record that URL in `DATA.md`.
- License: that release's data terms.
- Credit: name the release on the page. Do not commit the tracking files.

### nflverse

- Link: https://github.com/nflverse
- License: nflverse-data is Creative Commons Attribution 4.0 International (CC-BY-4.0), as stated by that repository's license.
- Credit: `Play-by-play data: nflverse (github.com/nflverse/nflverse-data), licensed CC-BY-4.0.`

### Baseball Savant

- Link: https://baseballsavant.mlb.com/
- License: MLB's terms. Do not commit a bulk download.
- Credit: `Pitch data: MLB Advanced Media via Baseball Savant (baseballsavant.mlb.com).`

### Penalty-kick authors' repository

- Link: https://github.com/sdsander-syr/soccer_pk_shot_location
- Pin: `ff98e29120d8597a6c6b21670fbe43ae7dc816b4`
- License: none stated. The repository page reports no license, and that commit contains no license file.
- Credit: `Penalty data: Uribe, Sanders, Ehrlich, Reade & Singleton (2025), github.com/sdsander-syr/soccer_pk_shot_location.`
- These files have no clear license, so the pinned-commit rule applies.

### OptimalDarts

- Link: https://github.com/wangchunsem/OptimalDarts
- Pin: `f68bedcc592b4bcfda69f6d72d69aede91ebaff1`
- License: none stated. The repository page reports no license. `readme.txt` at that commit describes the fits and the code and states no license.
- Credit: `Skill models: M. B. Haugh & C. Wang, 'Play like the pros? Solving the game of darts as a dynamic zero sum game' (github.com/wangchunsem/OptimalDarts).`
- These files have no clear license, so the pinned-commit rule applies. Do not paste the repository's code into `code/`.

### Metrica Sports sample tracking data

- Link: https://github.com/metrica-sports/sample-data
- Pin: `e706dd506b360d69d9d123d5b8026e7294b13996`
- License: no license file. The README at that commit, under "Legal stuff", states: "Please be responsible with the use of this data." and "If you use it for anything public, please aknowledge the source." That is the source's spelling. It is not a license.
- Credit: `Tracking and event data: Metrica Sports sample data (github.com/metrica-sports/sample-data). Players and teams are anonymized.`
- These files have no clear license, so the pinned-commit rule applies. The credit line is how the page meets the README's request to name the source.

### Retrosheet

- Link: https://www.retrosheet.org/
- Terms: https://www.retrosheet.org/notice.txt
- Game logs: https://www.retrosheet.org/gamelogs/ — the strike paper uses `gl2009.zip`, `gl2010.zip`, and `gl2011.zip`, as recorded in `papers/call-a-strike/DATA.md`.
- License: the notice says recipients are free to make any desired use of the information, including selling it, giving it away, or producing a commercial product based upon the data. The one requirement is that the following statement appear prominently. Show it verbatim, including the two spaces after the first period and the quotes around the URL:

```
     The information used here was obtained free of
     charge from and is copyrighted by Retrosheet.  Interested
     parties may contact Retrosheet at "www.retrosheet.org".
```

- Credit: that statement. It is the attribution line on every page that uses Retrosheet.

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
