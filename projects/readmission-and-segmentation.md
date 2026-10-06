# Flagging 68 of 79 readmitted patients using only what is known at discharge

A hospital wants to know which patients are likely to come back, so that follow-up calls and extra discharge planning go to the right people. I built and compared classification models on 1,500 patient records, then used the same toolkit to segment 1,000 fitness-app users.

## The question

Can patient demographics, hospital-stay characteristics, comorbidity and discharge-planning variables predict whether a patient will be readmitted?

## Data and set-up

- 1,500 patients, 21.1% of whom were readmitted.
- Ten predictors: age, length of stay, prior admissions, comorbidity score, follow-up appointment scheduled, discharge disposition, patient satisfaction, days to follow-up, admission type and insurance type.
- Dropped `hospital_id` and `room_number` because they identify a place, not a patient. Dropped `days_until_readmission` because it only exists once a patient has already been readmitted, so using it would leak the answer.
- 75/25 stratified train/test split (375 test patients, 79 of them readmitted). Both models sit in a pipeline with standardisation, and were tuned with 5-fold cross-validated grid search on F1.

## What the models found

Accuracy looks healthy for every model, but accuracy is the wrong yardstick when only one patient in five is readmitted. The standard models caught 43 of the 79 readmitted patients and missed 36. Reweighting the classes made the models care more about the rare outcome:

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | Missed | Flagged unnecessarily |
|---|---|---|---|---|---|---|---|
| Logistic regression (tuned) | 0.843 | 0.652 | 0.544 | 0.593 | 0.901 | 36 | 23 |
| SVC (tuned) | 0.867 | 0.754 | 0.544 | 0.632 | 0.915 | 36 | 14 |
| Logistic regression (class-weighted) | 0.800 | 0.517 | 0.785 | 0.623 | 0.901 | 17 | 58 |
| SVC (class-weighted) | 0.848 | 0.596 | 0.861 | 0.705 | 0.919 | 11 | 46 |

<figure>
<img src="figures/readmission-errors.png" alt="Bar chart of missed readmissions and unnecessary flags for six model variants. Missed readmissions fall from 36 to 11 for the class-weighted SVC, while unnecessary flags rise from 14 to 46.">
<figcaption>Class weighting cut missed readmissions from 36 to 11 and raised unnecessary flags from 14 to 46.</figcaption>
</figure>

I would recommend the class-weighted SVC as a decision-support tool. A missed readmission costs the patient and the hospital more than an extra follow-up call, so recall matters more than precision here. It should prompt a clinician's attention, not replace their judgement.

## What drives the risk

In the logistic regression (standardised inputs, so coefficients are comparable), higher comorbidity scores, more prior admissions and longer stays push predicted risk up. A scheduled follow-up appointment and higher patient satisfaction push it down. That points to actions a hospital controls: book the follow-up before the patient leaves.

<figure>
<img src="figures/readmission-coefficients.png" alt="Horizontal bar chart of logistic regression coefficients. Comorbidity score, prior admissions and length of stay are positive; follow-up appointment scheduled and patient satisfaction are negative.">
<figcaption>Comorbidity, prior admissions and length of stay raise risk; a scheduled follow-up and higher satisfaction lower it.</figcaption>
</figure>

## Segmenting 1,000 fitness-app users

The second task grouped app users by average daily steps and weekly calories burned. After standardising both variables I ran K-means and Ward hierarchical clustering with three clusters. The elbow plot bends gradually rather than sharply, so three is a defensible choice, not an obvious one.

| Segment (K-means) | Average daily steps | Weekly calories burned |
|---|---|---|
| Fewer steps, average burn | about 5,600 | about 1,970 |
| Many steps, low burn | about 8,800 | about 1,450 |
| Many steps, high burn | about 8,500 | about 2,570 |

Ward clustering returns almost the same three segments: every segment average lands within 5% of the K-means value. That agreement is the useful result. It suggests the segments are not an artefact of one algorithm.

<figure>
<img src="figures/segments-kmeans.png" alt="Scatter plot of average daily steps against weekly calories burned, coloured by three K-means clusters that tile a single continuous cloud of points.">
<figcaption>The three segments partition one continuous cloud of users, so treat them as practical groupings, not natural clusters.</figcaption>
</figure>

## What this can't show

- The test set holds only 79 readmitted patients. The class-weighted SVC's 86% recall has a 95% interval of roughly 77% to 92%.
- I compared four model variants on the same test set before choosing one, so the headline recall is probably a little optimistic. A stricter version picks the variant by cross-validation on the training data and uses the test set once. The script in `scripts/readmission_cv_selection.py` does that.
- Tuned and untuned cross-validated F1 scores (0.633 for logistic regression, 0.653 for SVC) differ by less than one standard deviation across folds, so I treat the two model families as similar in discrimination.
- If the patient satisfaction score is collected after discharge, it would not be available when a risk decision has to be made. That timing needs checking before any real use.
- The clustering uses only two variables, and the plots show no gaps between groups. Silhouette scores and cluster sizes are in `scripts/segmentation_validation.py`.
