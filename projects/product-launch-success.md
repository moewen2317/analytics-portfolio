# Brand familiarity, discounts, ad spend and shelf space explain 59% of launch success

Which controllable levers raise the probability that a new product launch succeeds? Regression on 1,500 launches ranks four of them and finds no sign that season or store region matters.

## The question

What factors are most predictive of a product's launch success probability?

## Data and set-up

- 1,500 product launches. The outcome is `success_probability`, a number between 0 and 1.
- I excluded first-month units sold and revenue (they happen after launch), the binary `is_successful` flag (derived from the outcome) and ID columns.
- A correlation heatmap screened the remaining variables. Brand familiarity (r = 0.53), launch discount (0.37), ad spend (0.33) and shelf space (0.20) showed clear relationships. Price, social media mentions, product category, competitor count and weekday launch were all within 0.04 of zero. I kept season and store region as additional checks.

## From one lever to six

Simple regressions on one predictor give a feel for each lever. Brand familiarity alone explains 28.6% of the variation in success probability, and launch discount alone explains 14.0%. Adding both lifts R² to 0.416, and the six-variable model reaches 0.593 (adjusted 0.591).

| Lever | Coefficient | What it means |
|---|---|---|
| Brand familiarity (0 to 1) | 0.410 | From unknown to fully familiar adds about 41 percentage points |
| Launch discount | 0.0075 per point | Each extra 10 points of discount adds about 7.5 percentage points |
| Ad spend | 0.0000525 per dollar | Each extra $1,000 adds about 5.3 percentage points |
| Shelf space | 0.0125 per sq ft | Each extra square foot adds about 1.25 percentage points |
| Season index | 0.0025 (p = 0.44) | No detectable effect |
| Store region index | 0.0002 (p = 0.95) | No detectable effect |

The four levers are all significant at p < 0.001. Their coefficients barely moved between the smaller and larger models, which is reassuring about stability.

<figure>
<img src="figures/launch-scatter.png" alt="Two scatter plots with fitted lines: success probability rising with brand familiarity score and with launch discount percentage, with a cluster of points at zero.">
<figcaption>Success probability rises with both brand familiarity and discount, with a pile-up of launches at exactly zero.</figcaption>
</figure>

## What the model can and cannot support

The analysis ranks levers by their effect per unit. It does not rank them by value for money, because discounts, advertising and shelf space all cost different amounts that the data does not contain. A budget recommendation needs those costs first.

Season and region showed no detectable effect here. That is weaker than saying they do not matter: a non-significant coefficient means the data cannot distinguish the effect from zero.

## What this can't show

- The outcome is a probability bounded between 0 and 1, but a linear model can predict outside that range, and the six-variable model's intercept is negative (−0.44). Many launches sit at exactly zero, which produces the diagonal band in the residual plot. A fractional logit or beta regression respects the bounds. `scripts/product_launch_checks.py` fits one and reports how often the linear model leaves the 0 to 1 range.
- Residuals are not normal (Shapiro-Wilk p < 0.001 for both simple models), though with 1,500 observations the coefficient estimates are still usable. Heteroscedasticity-robust standard errors guard against the uneven spread; the script reports those too.
- The regression output warns of a large condition number (3.26e4). It most likely comes from measuring ad spend in dollars, so rescaling to thousands of dollars and checking variance inflation factors would confirm.
- These are associations in observational data, not tested effects. Discounts and ad spend are management decisions, so launches that got more of them may differ in other ways.
- I chose predictors partly by their correlation with the outcome, which can miss variables that only matter in combination.

<figure>
<img src="figures/launch-residuals.png" alt="Residuals against fitted values for the brand familiarity and launch discount models, showing a straight diagonal band of points along the bottom edge.">
<figcaption>The diagonal band along the bottom is the zero floor on the outcome, which a linear model cannot represent.</figcaption>
</figure>
