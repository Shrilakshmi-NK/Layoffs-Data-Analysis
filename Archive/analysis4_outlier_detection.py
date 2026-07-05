"""
STAGE 2 - ANALYSIS #4
Statistical Outlier Detection
============================================================

BUSINESS QUESTION
------------------
Are there layoff events that are statistically unusual RELATIVE TO
what's normal for a company of that funding size - not just "high
percentage" in an absolute sense? A 40% layoff is very different for
a Mega-funded company than for a Small startup, so we compare each
event to its own funding bracket's typical range, not to the whole
dataset at once.

WHY PYTHON INSTEAD OF SQL
---------------------------
This needs a two-step calculation PER GROUP: first find each funding
bracket's "normal range" using quartiles, then compare every row
against its own group's range. Pandas' groupby().transform() lets us
calculate a group statistic and immediately spread it back onto every
row in that group, in a couple of lines. SQL would need a subquery
joined back to the main table to achieve the same result.

WHY THE IQR METHOD (NOT A SIMPLE Z-SCORE)
--------------------------------------------
A z-score outlier method assumes the data is roughly bell-shaped
(normally distributed) around the average. percentage_laid_off is NOT
bell-shaped - the Stage 1 summary showed most values bunched under
30%, with a long tail up to 100%. The IQR (Interquartile Range) method
is more robust to this kind of skew, because it's based on the MIDDLE
50% of the data (which stays stable even with a skewed tail) rather
than the average and standard deviation (which extreme values can
distort). This is the same reasoning we used for the log-transform in
Analysis #2 - checking that skew before choosing a statistical method.

CONTINUING THE MASTER DATASET
-------------------------------
Loads layoffs_master_enriched.csv (with all columns from Analyses
#1-3) and adds the final two columns for this project.
"""

import pandas as pd

# ---------------------------------------------------------------------------
# STEP 1: Load the master dataset
# ---------------------------------------------------------------------------
df = pd.read_csv("layoffs_master_enriched.csv", parse_dates=["date"])

# ---------------------------------------------------------------------------
# STEP 2: Calculate the IQR boundaries for EACH funding bracket
# ---------------------------------------------------------------------------
# .groupby("funding_bracket")["percentage_laid_off"] selects the
# percentage column, split into groups by funding bracket.
#
# .transform(lambda x: ...) runs a custom calculation on each group,
# but instead of collapsing each group into one row (like .agg() did
# in earlier analyses), it returns a result the SAME LENGTH as the
# original data - one value per row, repeated for every row in that
# row's group. This is exactly what we need: every company should see
# ITS OWN bracket's boundary values sitting right next to it in the
# same row, ready for a direct comparison.
#
# lambda x: x.quantile(0.25) is a small, throwaway function (a
# "lambda") that takes in a group's values (x) and returns their 25th
# percentile (Q1 - the value below which the lowest 25% of that
# group's data falls). We use a lambda here because we need a custom
# calculation (quantile at a specific percentage) that doesn't have
# its own shortcut name like "mean" or "count" did in earlier scripts.
q1_by_bracket = df.groupby("funding_bracket")["percentage_laid_off"].transform(
    lambda x: x.quantile(0.25)
)
q3_by_bracket = df.groupby("funding_bracket")["percentage_laid_off"].transform(
    lambda x: x.quantile(0.75)
)

# The IQR (Interquartile Range) is simply the width of the middle 50%
# of the data: Q3 minus Q1. A bigger IQR means that bracket's layoff
# percentages are more spread out; a smaller IQR means they're more
# tightly clustered together.
iqr_by_bracket = q3_by_bracket - q1_by_bracket

# The standard IQR outlier rule defines the "normal" range as:
#   lower bound = Q1 - 1.5 x IQR
#   upper bound = Q3 + 1.5 x IQR
# Anything outside this range is considered a statistical outlier.
# The 1.5 multiplier is a widely used convention in statistics (the
# same one used to draw the "whiskers" on a box plot) - it's not an
# arbitrary number we invented, it's a standard threshold.
lower_bound = q1_by_bracket - 1.5 * iqr_by_bracket
upper_bound = q3_by_bracket + 1.5 * iqr_by_bracket

# ---------------------------------------------------------------------------
# STEP 3: Flag outliers and label their direction
# ---------------------------------------------------------------------------
# A straightforward comparison: is this row's percentage_laid_off
# outside its own bracket's normal range?
df["is_statistical_outlier"] = (
    (df["percentage_laid_off"] < lower_bound) | (df["percentage_laid_off"] > upper_bound)
)

# np.select() lets us assign different text labels based on multiple
# conditions, checked in order - similar to an IF/ELIF/ELSE chain, but
# written for an entire column at once instead of one value at a time.
import numpy as np

conditions = [
    df["percentage_laid_off"] > upper_bound,
    df["percentage_laid_off"] < lower_bound,
]
choices = ["Unusually High for Funding Level", "Unusually Low for Funding Level"]
# The final argument, default=, is what gets used for every row that
# doesn't match any of the conditions above - in this case, a normal,
# non-outlier event.
df["outlier_direction"] = np.select(conditions, choices, default="Typical")

# Rows with a missing percentage_laid_off can't be compared to a
# boundary at all, so both new columns will correctly show False /
# "Typical" for them by default, since NaN comparisons in pandas
# always evaluate to False rather than raising an error.

# ---------------------------------------------------------------------------
# STEP 4: Review the results
# ---------------------------------------------------------------------------
print("Outlier count by direction:")
print(df["outlier_direction"].value_counts())

print("\nOutlier rate by funding bracket:")
# groupby + mean on a True/False column gives the PROPORTION of True
# values, since pandas treats True as 1 and False as 0 internally -
# this is a common, useful shortcut for turning a boolean flag into a
# percentage without writing a separate calculation.
outlier_rate_by_bracket = df.groupby("funding_bracket", observed=True)[
    "is_statistical_outlier"
].mean()
print((outlier_rate_by_bracket * 100).round(1))

print("\nSample of flagged 'Unusually High' events:")
high_outliers = df[df["outlier_direction"] == "Unusually High for Funding Level"]
print(
    high_outliers[
        ["company", "funding_bracket", "percentage_laid_off", "total_laid_off"]
    ]
    .sort_values(by="percentage_laid_off", ascending=False)
    .head(8)
    .to_string(index=False)
)

# ---------------------------------------------------------------------------
# STEP 5: Save the final enriched master dataset
# ---------------------------------------------------------------------------
df.to_csv("layoffs_master_enriched.csv", index=False)
print("\nUpdated: layoffs_master_enriched.csv")
print(f"Final columns in the master dataset: {list(df.columns)}")
