# Analytics portfolio

Five data analytics projects, each written up as a short case study: the question, the data, what the models found, and what the analysis cannot show.

Live site: https://moewen2317.github.io/analytics-portfolio/

| Project | Question | Case study |
|---|---|---|
| Hospital readmissions and app-user segmentation | Can data available at discharge predict which patients come back? | [projects/readmission-and-segmentation.md](projects/readmission-and-segmentation.md) |
| Coupon acceptance | What makes a driver accept a coupon? | [projects/coupon-acceptance.md](projects/coupon-acceptance.md) |
| Product launch success | Which levers raise the chance a launch succeeds? | [projects/product-launch-success.md](projects/product-launch-success.md) |
| Gender earnings gap | How large is the gap, and do age and education explain it? | [projects/gender-earnings-gap.md](projects/gender-earnings-gap.md) |
| Airline delays | What drives delays, and when do they peak? | [projects/airline-delays.md](projects/airline-delays.md) |

## Repository layout

- `index.html`, `assets/`: the portfolio site (served by GitHub Pages).
- `projects/`: one markdown case study per project. The site is generated from these.
- `figures/`: charts used in the case studies.
- `scripts/`: runnable checks that reproduce or tighten specific numbers (see below).
- `notebooks/`: the original analysis notebooks.
- `site.json`, `build.py`: site text and the generator. Run `python build.py` after editing a case study.

## Scripts

Each script takes the path to its dataset as the only argument. Datasets are not included.

| Script | What it adds |
|---|---|
| `scripts/readmission_cv_selection.py` | Picks the model and decision threshold by cross-validation, then scores the test set once, with a confidence interval on recall |
| `scripts/segmentation_validation.py` | Silhouette scores, K-means and Ward agreement, segment sizes |
| `scripts/coupon_rules_and_importance.py` | Association rules measured against the base rate, plus permutation importance on raw columns |
| `scripts/product_launch_checks.py` | Rescaled ad spend, variance inflation factors, robust standard errors, fractional logit |
| `scripts/earnings_gap_checks.py` | Centred age, full education dummies, survey weights, trimmed earnings |

```
pip install -r requirements.txt
python scripts/segmentation_validation.py path/to/Dataset_partB.xlsx
```
