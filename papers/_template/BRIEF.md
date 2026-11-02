# BRIEF: [Paper title]

Scout spec for one paper. The builder turns this file plus the page template into a single pull request. Replace every bracket. Do not leave the template's toy model in place.

## Paper

- Title: [full title]
- Authors: [names]
- Year: [year]
- Venue: MIT Sloan Sports Analytics Conference research paper
- Link: [canonical URL of the paper]
- Slug: [papers/<name>/, lowercase, hyphenated, must not start with `_`]

## Question

[The question the paper asks, in its terms. One short paragraph. Do not add a claim the paper does not make.]

## Data the paper used

- Provider and dataset: [name]
- Seasons / competitions / sample size: [what the paper states]
- Public? [yes or no]
- License, if it is public: [name and link]

## Data this page will use

- Source: [StatsBomb open data, a named NFL Big Data Bowl release, nflverse, or Baseball Savant]
- URL: [link]
- License: [what we are allowed to copy, display, and commit]
- Same data as the paper? [yes or no]
- If no, substitute: yes. The page must show the "Rebuilt on substitute data" callout. State what transfers and what does not.
- If yes, substitute: no. The page must not show that callout. `DATA.md` must say `substitute: no`.

## Method, in order

1. [First step the reader will code]
2. [Next step]
3. [The step that produces the figure]

## Assumptions to put on a slider

- [Parameter]: [what it means, the range, and the paper's default]

## Real play

[One possession, play, or pitch sequence the walkthrough will step through. Name the ids in the public data. If the public data cannot identify that play, say so and pick a substitute sequence.]

## Figure

- Paper figure: [number and what it shows]
- Our panel: [what we recompute]
- Reproduction: [redraw, or a licensed copy of the original]

## What should hold up, and what may not

- Expect to hold: [specific comparison]
- Expect to break: [sample, features, or definition that will not match]

## Learning layers

- Intro animation: [the question in motion, one sentence]
- Guided build: [which steps are required before the figure]
- Advanced: [the sensitivity, baseline, or failure case]

## Exercises

- Fill-in-the-blank: [the line the reader completes, and the answer]
- Quick check: [the question, the choices, and the correct one]
- Glossary terms to add: [key, term, one-sentence definition]

## Out of scope

[What this page will not rebuild.]

## Done when

- [ ] `index.qmd` follows `papers/_template/index.qmd` section for section
- [ ] Every `TODO(paper)` marker is gone
- [ ] `DATA.md` matches the callout (present only if substitute is yes)
- [ ] `quarto render` succeeds
- [ ] The checker has compared the page to the paper
- [ ] Jordan merges. Agents and reviewers do not
