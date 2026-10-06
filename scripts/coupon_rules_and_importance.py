"""Coupon analysis checks: relationships in the data, rules against the base rate,
and permutation importance on the raw columns.

Usage:  python scripts/coupon_rules_and_importance.py path/to/Coupon_Recommendation.csv
"""
import sys
from itertools import combinations
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance

df = pd.read_csv(sys.argv[1]).drop_duplicates().reset_index(drop=True)
base = df["Y"].mean()
print(f"{len(df)} rows after de-duplication; base acceptance rate {base:.3f}\n")

# 1. Do the trip attributes overlap? (explains why some mined rules repeat themselves)
print("Time of day by destination:")
print(pd.crosstab(df["time"], df["destination"]), "\n")
print("Passenger by destination:")
print(pd.crosstab(df["passanger"], df["destination"]), "\n")

# 2. Rules whose only outcome is acceptance, with lift measured against the base rate.
items = ["destination", "passanger", "weather", "time", "coupon", "expiration", "gender", "age", "income"]
B = pd.get_dummies(df[items].astype(str), prefix=items, prefix_sep="=").astype(bool)
y = df["Y"].to_numpy() == 1
cols = list(B.columns)
M = B.to_numpy()
rows = []
for size in (1, 2, 3):
    for combo in combinations(range(len(cols)), size):
        # skip combos that take two values of the same variable
        if len({cols[i].split("=")[0] for i in combo}) < size:
            continue
        mask = M[:, list(combo)].all(axis=1)
        support = mask.mean()
        if support < 0.05:
            continue
        conf = y[mask].mean()
        if conf >= 0.6:
            rows.append((" + ".join(cols[i] for i in combo), support, conf, conf / base))
rules = pd.DataFrame(rows, columns=["if", "support", "acceptance_rate", "lift_vs_base"])
print("Top rules for acceptance (support >= 0.05, acceptance rate >= 0.6):")
print(rules.sort_values("lift_vs_base", ascending=False).head(15).round(3).to_string(index=False), "\n")

# 3. Permutation importance on the raw columns, scored on held-out data.
X = df.drop(columns="Y")
y_s = df["Y"]
cat = X.select_dtypes(include="object").columns.tolist()
pre = ColumnTransformer([("c", OneHotEncoder(handle_unknown="ignore"), cat)], remainder="passthrough")
model = Pipeline([("pre", pre), ("rf", RandomForestClassifier(
    n_estimators=200, max_depth=10, min_samples_leaf=10, random_state=42, n_jobs=-1))])
X_tr, X_te, y_tr, y_te = train_test_split(X, y_s, test_size=0.2, random_state=42, stratify=y_s)
model.fit(X_tr, y_tr)
pi = permutation_importance(model, X_te, y_te, scoring="roc_auc", n_repeats=10, random_state=42, n_jobs=-1)
imp = pd.Series(pi.importances_mean, index=X.columns).sort_values(ascending=False)
print("Permutation importance (drop in ROC-AUC when the column is shuffled):")
print(imp.head(12).round(4).to_string())
