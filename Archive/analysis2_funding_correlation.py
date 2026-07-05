"""
STAGE 2 - ANALYSIS #2
Funding vs. Layoff Severity Correlation
============================================================

BUSINESS QUESTION
------------------
Is there a relationship between how much money a company raised
(funds_raised_millions) and the PERCENTAGE of its workforce it laid
off (percentage_laid_off)? Do well-funded companies cut a smaller
share of staff, a larger share, or is there no real relationship?

WHY PYTHON INSTEAD OF SQL
---------------------------
Correlation compares every value in one column to every value in
another column, relative to each column's own average, all at once.
SQL has no built-in function for this - you'd have to hand-write the
Pearson correlation formula using SUM, AVG, and STDDEV. Pandas gives
us this as a single, well-tested method.

NOTE ON PROJECT STRUCTURE FROM THIS POINT FORWARD
---------------------------------------------------
Starting with this script, we build ONE master enriched dataset by
adding new columns as we go, instead of creating a new CSV for every
analysis. This script re-creates the "repeat layoff" flag from
Analysis #1 as a column (instead of a separate file) and adds two new
columns from this analysis. The single output at the end is
"layoffs_master_enriched.csv".
"""

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# STEP 1: Load the cleaned dataset
# ---------------------------------------------------------------------------
df = pd.read_csv("layoff2.csv", parse_dates=["date"])

# ---------------------------------------------------------------------------
# STEP 2: Re-add the repeat-layoff information from Analysis #1 as COLUMNS
# ---------------------------------------------------------------------------
# Instead of keeping Analysis #1's output as a separate file, we fold its
# key finding into the main dataset as two new columns:
#   - number_of_layoff_events: how many times this company appears total
#   - is_repeat_layoff_company: True/False flag for "more than once"
#
# .transform("count") is similar to .groupby().size() from Analysis #1,
# but transform() returns a value for EVERY row (matching the original
# dataframe's length) instead of collapsing rows into one-per-group.
# This is exactly what we need to add it back as a column rather than
# a separate summary table.
df["number_of_layoff_events"] = df.groupby("company")["company"].transform("count")

# A simple comparison (> 1) turns that count into a True/False column.
df["is_repeat_layoff_company"] = df["number_of_layoff_events"] > 1

# ---------------------------------------------------------------------------
# STEP 3: Calculate the raw correlation
# ---------------------------------------------------------------------------
# .corr() calculates the Pearson correlation coefficient between two
# numeric columns. This is a number between -1 and +1:
#   +1  = perfect positive relationship (as one goes up, so does the other)
#    0  = no linear relationship at all
#   -1  = perfect negative relationship (as one goes up, the other goes down)
#
# Rows where EITHER column is missing (NaN) are automatically excluded
# by .corr() - it doesn't need us to filter them out manually first.
raw_correlation = df["funds_raised_millions"].corr(df["percentage_laid_off"])
print(f"Raw correlation (funds raised vs. % laid off): {raw_correlation:.3f}")

# ---------------------------------------------------------------------------
# STEP 4: Why we ALSO check a log-transformed version
# ---------------------------------------------------------------------------
# From Stage 1's summary stats, funds_raised_millions is heavily skewed:
# most companies raised under $409M (75th percentile), but a few raised
# over $100,000M. Pearson correlation assumes a roughly linear, evenly
# spread relationship - a few extreme outliers can distort it, making
# the true pattern among "typical" companies harder to see.
#
# np.log1p(x) calculates log(1 + x) using NumPy. We use log1p instead
# of a plain log() because some companies raised $0, and a plain
# logarithm of 0 is undefined (an error) - adding 1 first avoids that
# problem while barely changing the result for larger numbers.
# Log transforms compress large values much more than small ones,
# which reduces the outsized influence of a few extremely large
# funding rounds on the correlation calculation.
df["log_funds_raised"] = np.log1p(df["funds_raised_millions"])

log_correlation = df["log_funds_raised"].corr(df["percentage_laid_off"])
print(f"Log-transformed correlation (log funds raised vs. % laid off): {log_correlation:.3f}")

# ---------------------------------------------------------------------------
# STEP 5: Add a readable "funding bracket" column
# ---------------------------------------------------------------------------
# A raw correlation number is useful for statisticians but hard for a
# business audience to visualize directly. Grouping companies into
# clear funding brackets makes the relationship easy to show as a bar
# chart in Power BI later (e.g. "average % laid off by funding size").
#
# pd.cut() splits a numeric column into bins based on VALUE RANGES we
# choose ourselves (as opposed to pd.qcut, which splits by percentile,
# creating groups of equal size but with less intuitive boundaries).
# We use pd.cut here because "companies that raised under $50M" is a
# meaningful, explainable business category - a percentile-based cut
# wouldn't have a clean real-world interpretation.
funding_bins = [-1, 50, 500, 2000, np.inf]
funding_labels = ["Small (<$50M)", "Medium ($50-500M)", "Large ($500M-2B)", "Mega (>$2B)"]

df["funding_bracket"] = pd.cut(
    df["funds_raised_millions"], bins=funding_bins, labels=funding_labels
)
# Starting the first bin at -1 (instead of 0) ensures companies with
# exactly $0 raised are correctly included in "Small", since pd.cut's
# bin edges are exclusive on the left side by default.

# ---------------------------------------------------------------------------
# STEP 6: Summarize average severity per funding bracket
# ---------------------------------------------------------------------------
# .groupby("funding_bracket") groups rows by the bracket we just created.
# .agg() again calculates multiple statistics per group in one call:
#   - the average percentage laid off in that bracket
#   - how many companies fall into that bracket (sample size matters -
#     a bracket with only 3 companies is less trustworthy than one with 500)
bracket_summary = df.groupby("funding_bracket", observed=True).agg(
    average_percentage_laid_off=("percentage_laid_off", "mean"),
    number_of_companies=("company", "count"),
)
bracket_summary["average_percentage_laid_off"] = bracket_summary[
    "average_percentage_laid_off"
].round(3)
bracket_summary = bracket_summary.reset_index()

print("\nAverage % laid off by funding bracket:")
print(bracket_summary.to_string(index=False))

# ---------------------------------------------------------------------------
# STEP 7: Save the enriched master dataset
# ---------------------------------------------------------------------------
# This is now the ONE dataset carrying forward every analysis's new
# columns. Analysis #3 and #4 will load THIS file and keep adding to
# it, rather than starting back from layoff2.csv each time.
df.to_csv("layoffs_master_enriched.csv", index=False)
print("\nExported: layoffs_master_enriched.csv")
print(f"Columns now in the master dataset: {list(df.columns)}")
