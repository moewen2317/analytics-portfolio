"""Gender earnings gap robustness checks.

Usage:  python scripts/earnings_gap_checks.py path/to/morg-2014-emp.csv

Runs the gap regression with: centred age, a full set of education dummies,
survey weights, trimmed earnings, and robust standard errors.
Education uses CPS grade92 codes: 39 high school graduate, 40 some college,
41 and 42 associate, 43 bachelor's, 44 master's, 45 professional, 46 doctorate.
"""
import sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv(sys.argv[1])
df["female"] = (df["sex"] == 2).astype(int)
df["w"] = df["earnwke"] / df["uhours"]
df = df[df["w"] > 0].copy()
df["lnw"] = np.log(df["w"])

age_c = (df["age"] - df["age"].mean()) / 10
df["a1"], df["a2"], df["a3"], df["a4"] = age_c, age_c**2, age_c**3, age_c**4

g = df["grade92"]
df["ed_somecoll"] = g.isin([40]).astype(int)
df["ed_assoc"] = g.isin([41, 42]).astype(int)
df["ed_ba"] = (g == 43).astype(int)
df["ed_ma"] = (g == 44).astype(int)
df["ed_prof"] = (g == 45).astype(int)
df["ed_phd"] = (g == 46).astype(int)

age = "a1 + a2 + a3 + a4"
edu = "ed_somecoll + ed_assoc + ed_ba + ed_ma + ed_prof + ed_phd"
specs = {
    "gender only": "lnw ~ female",
    "centred age quartic": f"lnw ~ female + {age}",
    "full education dummies": f"lnw ~ female + {edu}",
    "age + full education": f"lnw ~ female + {age} + {edu}",
}

rows = []
for label, f in specs.items():
    m = smf.ols(f, data=df).fit(cov_type="HC1")
    rows.append((label, "unweighted", m.params["female"], m.bse["female"], m.rsquared, int(m.nobs)))

# Survey-weighted version of the fullest model, if a weight column exists.
if "weight" in df.columns:
    mw = smf.wls(f"lnw ~ female + {age} + {edu}", data=df, weights=df["weight"]).fit(cov_type="HC1")
    rows.append(("age + full education", "weighted", mw.params["female"], mw.bse["female"], mw.rsquared, int(mw.nobs)))

# Trim the bottom and top 1% of hourly wages.
lo, hi = df["w"].quantile([0.01, 0.99])
t = df[(df["w"] >= lo) & (df["w"] <= hi)]
mt = smf.ols(f"lnw ~ female + {age} + {edu}", data=t).fit(cov_type="HC1")
rows.append(("age + full education", "trimmed 1% tails", mt.params["female"], mt.bse["female"], mt.rsquared, int(mt.nobs)))

out = pd.DataFrame(rows, columns=["specification", "sample", "female_coef", "robust_se", "r2", "n"])
out["approx_gap_pct"] = (np.exp(out["female_coef"]) - 1) * 100
print(out.round(4).to_string(index=False))
