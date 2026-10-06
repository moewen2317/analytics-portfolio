# Cheap-meal coupons are accepted about seven times in ten; bar coupons about four in ten

Which situational and personal factors make a driver accept a coupon? I used 12,007 simulated driving scenarios to compare three classifiers and mine association rules, then turned the findings into targeting advice for a marketing team.

## The question

Which contextual and demographic factors most strongly influence whether a driver accepts a coupon recommendation?

## Data and set-up

- The in-vehicle coupon recommendation dataset (UCI Machine Learning Repository, from Wang et al., 2017). Participants on Amazon Mechanical Turk judged hypothetical driving scenarios.
- 12,079 rows; 72 duplicates removed, leaving 12,007. 56.8% of scenarios ended in acceptance.
- Feature engineering: trip type (social, leisure, home, work), time-of-day groups, expiry flags, weather and temperature groups, travel-time flags, visit-frequency scores for bars, coffee houses and restaurants, and grouped income and age.
- Preprocessing and model sit in one scikit-learn pipeline so nothing is learned from the test set. 80/20 stratified split, with 5-fold cross-validation on top.

## Which model worked best

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | Cross-validated F1 |
|---|---|---|---|---|---|---|
| Random forest | 0.727 | 0.722 | 0.845 | 0.779 | 0.793 | 0.758 |
| Decision tree | 0.671 | 0.664 | 0.852 | 0.746 | 0.727 | 0.711 |
| Logistic regression | 0.675 | 0.697 | 0.758 | 0.726 | 0.729 | 0.717 |

The random forest led on accuracy, F1 and ROC-AUC. I used it mainly to rank drivers, not to deploy a predictor.

<figure>
<img src="figures/coupon-roc.png" alt="ROC curves for logistic regression, decision tree and random forest. The random forest curve sits above the others with an AUC of 0.79.">
<figcaption>The random forest separates acceptances from rejections better than the simpler models (AUC 0.79 against 0.73).</figcaption>
</figure>

## What drives acceptance

**Coupon type matters most.** Carry-out and restaurant coupons under $20 are accepted roughly seven times in ten. Bar coupons are accepted about four times in ten, and coffee house and $20 to $50 restaurant coupons sit in between.

<figure>
<img src="figures/coupon-by-type.png" alt="Grouped bar chart of rejection and acceptance rates by coupon type. Carry-out and cheap restaurant coupons have the highest acceptance.">
<figcaption>Acceptance is highest for carry-out and cheap restaurant coupons, and lowest for bars.</figcaption>
</figure>

**Past habits matter next.** In the random forest, the top four features are indicators for four of the five coupon types, followed by how often someone visits coffee houses, a total food-venue visit score, short expiry, bar visit frequency, travel time over 15 minutes and leisure trips.

<figure>
<img src="figures/coupon-importance.png" alt="Horizontal bar chart of the top 15 random forest feature importances, led by coupon type indicators and coffee house visit frequency.">
<figcaption>Coupon type and visit habits lead the random forest's feature importance.</figcaption>
</figure>

**Timing and company shape the picture, though not through feature importance.** Acceptance peaks around 2PM and is weakest at 7AM, when about half of coupons are accepted. Drivers with friends accept more often than drivers alone (roughly two in three against just over one in two).

<figure>
<img src="figures/coupon-by-time.png" alt="Grouped bar chart of acceptance by time of day. Acceptance is highest at 2PM and 10AM and lowest at 7AM.">
<figcaption>Acceptance peaks in the middle of the day and is weakest at 7AM.</figcaption>
</figure>

**Income matters little.** Acceptance rates vary only mildly across income bands, so context and habits are better targeting signals than demographics.

## Association rules, read against the base rate

Apriori (minimum support 0.05, confidence at least 0.6) surfaced readable combinations. Lift needs care here: the lifts the algorithm printed (4.94, 2.56 and 2.35) belong to rules whose outcome bundles acceptance with a trip attribute. Compared with the 56.8% overall acceptance rate, the effect of each condition on acceptance alone is more modest:

| If the scenario is... | Acceptance rate | Against the 56.8% base rate |
|---|---|---|
| Sunny, on a work trip (7AM), one-day expiry | 61.2% | about 1.1 times |
| Under-$20 restaurant coupon, travelling with friends | 80.4% | about 1.4 times |
| One-day expiry, travelling with friends | 73.7% | about 1.3 times |

In this dataset every 7AM trip is a work trip (both appear 2,976 times), so the first rule describes one group of drivers twice. Trips with friends, a partner or children all appear to go to "no urgent place" too, which is why friends plus cheap restaurant coupons stand out.

## Recommendations the evidence supports

1. Lead with cheap-meal coupons and carry-out offers; be selective with bar coupons.
2. Send offers around midday and afternoon, not first thing in the morning.
3. Use visit-frequency habits to choose who gets which coupon.
4. For group travel, test a coupon framed for sharing.

## What this can't show

- Responses are self-reported answers to hypothetical scenarios. Real redemption may differ.
- The same people answered several scenarios, but the data has no respondent ID. A random split can therefore put one person's rows in both training and test sets, which probably flatters the accuracy figures.
- Random forest importance is split across the levels of a one-hot column, so time of day and passenger type look weaker than the charts suggest. `scripts/coupon_rules_and_importance.py` computes permutation importance on the raw columns and the association rules with acceptance as the only outcome.
- The models use fixed hyperparameters with no tuning, and I did not check whether longer expiry raises acceptance on its own.
