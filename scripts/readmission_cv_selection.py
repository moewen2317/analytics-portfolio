"""Choose the readmission model by cross-validation, then touch the test set once.

Usage:  python scripts/readmission_cv_selection.py path/to/Dataset_partA.xlsx

The original notebook compared four model variants on the test set and then
picked one. Here the choice (model family, C, gamma, class weighting and the
decision threshold) is made on the training data only. The test set is scored
a single time at the end, with a 95% Wilson interval on recall.
"""
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_predict, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, fbeta_score, roc_auc_score


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    a = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - a) / d, (c + a) / d


df = pd.read_excel(sys.argv[1]).drop(columns=["hospital_id", "room_number"])
X = df.drop(columns=["readmitted", "days_until_readmission"])
y = df["readmitted"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
cv = StratifiedKFold(5, shuffle=True, random_state=42)

candidates = {
    "Logistic regression": (
        Pipeline([("s", StandardScaler()), ("m", LogisticRegression(max_iter=5000))]),
        {"m__C": [0.01, 0.1, 1, 10, 100], "m__class_weight": [None, "balanced"]},
    ),
    "SVC": (
        Pipeline([("s", StandardScaler()), ("m", SVC())]),
        {"m__C": [0.1, 1, 10], "m__gamma": ["scale", "auto"], "m__class_weight": [None, "balanced"]},
    ),
}

# Missing a readmission is worse than an extra follow-up, so score with F2 (recall counts double).
best = None
for name, (pipe, grid) in candidates.items():
    gs = GridSearchCV(pipe, grid, cv=cv, scoring="f1", n_jobs=-1).fit(X_tr, y_tr)
    print(f"{name}: best CV F1 = {gs.best_score_:.3f}  params = {gs.best_params_}")
    if best is None or gs.best_score_ > best[1]:
        best = (name, gs.best_score_, gs.best_estimator_)
name, _, model = best
print(f"\nSelected on training data: {name}")

# Choose the decision threshold on out-of-fold scores, still using training data only.
oof = cross_val_predict(model, X_tr, y_tr, cv=cv, method="decision_function")
grid_t = np.quantile(oof, np.linspace(0.3, 0.95, 66))
f2 = [fbeta_score(y_tr, oof >= t, beta=2) for t in grid_t]
thr = grid_t[int(np.argmax(f2))]
print(f"Threshold chosen by out-of-fold F2: {thr:.3f}")

# Single look at the test set.
model.fit(X_tr, y_tr)
score = model.decision_function(X_te)
pred = score >= thr
tn, fp, fn, tp = confusion_matrix(y_te, pred).ravel()
lo, hi = wilson(tp, tp + fn)
print("\nTest set (scored once)")
print(f"  confusion matrix: TN={tn} FP={fp} FN={fn} TP={tp}")
print(f"  recall    = {tp/(tp+fn):.3f}  (95% interval {lo:.3f} to {hi:.3f})")
print(f"  precision = {tp/(tp+fp):.3f}")
print(f"  ROC-AUC   = {roc_auc_score(y_te, score):.3f}")
