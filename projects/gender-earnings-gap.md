# Women earn about 15% less per hour than men, and age and education barely change that

Using a US labour-force survey extract of 149,316 workers, I measured the gender earnings gap and tested whether it survives controls for age and education. It does: the estimate stays between about 15% and 16% across ten specifications.

## The question

How large is the gender difference in earnings, and how sensitive is it to the controls I add?

## Data and set-up

- A 2014 extract from the US Current Population Survey's outgoing rotation groups (`morg-2014-emp.csv`), with 149,316 workers.
- New variables: a `female` indicator, hourly wage `w` (usual weekly earnings divided by usual weekly hours), its logarithm `lnw`, and age polynomials up to the fourth power.
- Education dummies for the master's, professional and doctoral levels.
- Models fitted with `statsmodels`, results compared side by side with `stargazer`.

## The raw gap

Mean weekly earnings were $765.68 for women and $1,008.99 for men, a gap of 24.1%. Weekly earnings mix pay rates with hours worked. Switching to the log of hourly wage, the gap is much smaller:

| Specification (outcome: log hourly wage) | Female coefficient | Approx. gap | R² |
|---|---|---|---|
| Gender only | −0.164 | −15.1% | 0.016 |
| Plus age, age squared, cubed and fourth power | −0.165 | −15.2% | 0.139 |
| Plus professional and doctoral degree | −0.160 | −14.8% | 0.046 |
| Plus professional and master's degree | −0.178 | −16.3% | 0.088 |

Standard errors are about 0.003 throughout, so every estimate is distinguishable from zero by a wide margin. Coefficients on a log outcome are approximate percentage differences: exp(−0.164) − 1 is about −15.1%.

## How to read the numbers

**The gap is about 15% per hour, and about 24% per week.** The difference between the two is consistent with women working fewer paid hours on average. I did not tabulate hours by gender to confirm that split.

**Age and education barely move the estimate.** Across the ten full-sample specifications the female coefficient stays between −0.160 and −0.178. Adding a master's degree dummy widens the gap slightly, which fits women being more likely than men to hold a master's degree.

**A low R² is not a flaw here.** Gender alone explains 1.6% of the variation in log wages. The goal was to estimate a gap, not to predict an individual's pay. Wages vary for many reasons that gender does not capture.

## What this can't show

- This is a conditional gap, not a cause. The data cannot separate discrimination from occupation, industry, experience and hours, and I make no claim about which of these drives the gap. Adding occupation and hours would be the natural next step.
- The extract comes with a sampling weight, and my regressions did not use it. The estimates describe this sample and should not be read as exact population figures.
- Weekly earnings run from $0.01 to $2,884.61 in the extract. The upper end looks like a top-coded value and the lower end is implausible for a worker. Residuals are strongly skewed (skewness −1.3, kurtosis 21), so a robustness check that trims extreme values is worthwhile.
- Age, age squared, age cubed and age to the fourth power are highly collinear in raw form. The regression output reports a condition number of 5.5e8. Centring age would fix this and leave the female coefficient unchanged.
- I only included some education levels in each model. A single model with all levels (high school as the reference) would be cleaner. `scripts/earnings_gap_checks.py` runs these checks: full education dummies, centred age, survey weights, trimmed earnings and robust standard errors.
