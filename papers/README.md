# Papers

One directory per paper, plus `papers/_template/`, which is the page every rebuild copies.

```
papers/<name>/
  BRIEF.md     scout spec
  index.qmd    the page, copied from papers/_template/index.qmd
  DATA.md      source, license, sample, and the substitute flag
  code/        Python the Pyodide cells keep in sync with
  figures/     the paper figure (only if we may reproduce it) and our rebuild
```

`<name>` is lowercase and hyphenated. It must not start with `_`. Quarto skips underscore directories unless `_quarto.yml` lists them, and the template is listed on purpose so the example renders.

`DATA.md`, `BRIEF.md`, and this file are repository notes. They are not website pages. The site lists `index.qmd` files only.

## Template

`papers/_template/` is a working page, not a paper. It implements every required section and learning layer, with a toy shot model so the widgets run:

- a Pyodide cell you can edit and run
- a fill-in-the-blank exercise, with a hint, a solution, and a check
- a slider that redraws a Plotly chart
- a frame-by-frame play drawn with D3
- a quick-check question
- hover glossary terms, fed by `assets/glossary.json`
- the paper figure beside our rebuild
- the "Rebuilt on substitute data" callout

Copy the directory. Do not edit the template to sneak in a real paper.

## Page order

Keep these level-2 headings, in this order:

1. Intro (learning layer 1, with an animation)
2. The question
3. The data
4. Guided build (learning layer 2: method, code, blank, slider)
5. A real play
6. Check yourself
7. Paper figure and our rebuild
8. What held up and what didn't
9. Advanced (learning layer 3)
10. The original

## Pipeline

1. A scout writes `papers/<name>/BRIEF.md` from `papers/_template/BRIEF.md`.
2. A builder opens one pull request that adds the page, code, data notes, and figures.
3. A checker compares the page to the paper.
4. Jordan merges. Nobody else does.
