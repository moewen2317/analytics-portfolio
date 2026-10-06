"""Validate the app-user segmentation: silhouette scores, agreement and sizes.

Usage:  python scripts/segmentation_validation.py path/to/Dataset_partB.xlsx
"""
import sys
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, adjusted_rand_score

df = pd.read_excel(sys.argv[1])
cols = ["avg_daily_steps", "weekly_calories_burned"]
Z = StandardScaler().fit_transform(df[cols])

print("Silhouette score by number of clusters (higher is better, 1 is best)")
print(f"{'k':>3} {'K-means':>9} {'Ward':>9}")
for k in range(2, 9):
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(Z)
    hc = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(Z)
    print(f"{k:>3} {silhouette_score(Z, km):>9.3f} {silhouette_score(Z, hc):>9.3f}")

km = KMeans(n_clusters=3, n_init=10, random_state=42).fit_predict(Z)
hc = AgglomerativeClustering(n_clusters=3, linkage="ward").fit_predict(Z)
print(f"\nAgreement between K-means and Ward at k=3 (adjusted Rand index): {adjusted_rand_score(km, hc):.3f}")

out = df[cols].assign(kmeans=km, ward=hc)
for label in ("kmeans", "ward"):
    g = out.groupby(label)[cols].agg(["mean"]).round(0)
    g["size"] = out.groupby(label).size()
    print(f"\n{label} segments (original units)")
    print(g)
