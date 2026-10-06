"""Product launch regression checks: rescaled ad spend, VIF, robust errors, and a
fractional logit that respects the 0 to 1 bounds of the outcome.

Usage:  python scripts/product_launch_checks.py path/to/Dataset.xlsx
"""
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

df = pd.read_excel(sys.argv[1])
df["ad_spend_k"] = df["ad_spend_usd"] / 1000  # thousands of dollars
formula = ("success_probability ~ brand_familiarity_score + launch_discount_pct"
           " + ad_spend_k + shelf_space_sqft + season_index + store_region_index")

ols = smf.ols(formula, data=df).fit(cov_type="HC3")
print("OLS with heteroscedasticity-robust (HC3) standard errors")
print(ols.summary().tables[1])
print(f"R-squared {ols.rsquared:.3f}; condition number {ols.condition_number:,.0f}\n")

X = sm.add_constant(df[["brand_familiarity_score", "launch_discount_pct", "ad_spend_k",
                        "shelf_space_sqft", "season_index", "store_region_index"]])
vif = pd.Series([variance_inflation_factor(X.values, i) for i in range(1, X.shape[1])],
                index=X.columns[1:])
print("Variance inflation factors (above about 5 is worth a look):")
print(vif.round(2).to_string(), "\n")

fitted = ols.fittedvalues
print(f"Linear model predictions outside [0, 1]: {((fitted < 0) | (fitted > 1)).mean():.1%}")
print(f"Share of launches with success_probability exactly 0: {(df['success_probability'] == 0).mean():.1%}\n")

flogit = smf.glm(formula, data=df, family=sm.families.Binomial()).fit(cov_type="HC3")
print("Fractional logit (outcome treated as a proportion; robust standard errors)")
print(flogit.summary().tables[1])

# Average marginal effects in percentage points per unit of each predictor.
p = flogit.predict(df)
beta = flogit.params.drop("Intercept")
ame = (beta * (p * (1 - p)).mean() * 100).round(2)
print("\nApproximate average marginal effects, percentage points per unit:")
print(ame.to_string())
