"""
STAGE 2 - ANALYSIS #3
Layoff Severity Segmentation
============================================================

BUSINESS QUESTION
------------------
Can we group each layoff event into a clear, business-readable
severity tier (Mild / Moderate / Severe / Critical) based on the
PERCENTAGE of staff laid off? Once we have these tiers, do certain
industries, funding brackets, or repeat-layoff companies show up more
often in the more severe tiers?

WHY PYTHON INSTEAD OF SQL
---------------------------
Bucketing a number into categories can technically be done with a
nested CASE WHEN in SQL, but it gets long and error-prone as the
number of tiers grows, and it's annoying to adjust later. Pandas does
this in one line with pd.cut(). More importantly, once the tier is a
column sitting next to the columns we already built (funding_bracket,
is_repeat_layoff_company), cross-checking all of them together is a
single pivot_table call - much faster to write and re-run than
stacking several SQL queries together.

CONTINUING THE MASTER DATASET
-------------------------------
This script loads layoffs_master_enriched.csv (the output of
Analysis #2, which already contains the repeat-layoff and funding
columns) and adds severity tier columns to it, rather than starting
over from the plain cleaned file.
"""

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# STEP 1: Load the master dataset from Analysis #2
# ---------------------------------------------------------------------------
df = pd.read_csv("layoffs_master_enriched.csv", parse_dates=["date"])
# Note: funding_bracket was saved as plain text in the CSV (pandas
# "Categorical" types don't survive a round-trip through CSV - they
# come back as normal text). That's fine; we don't need the special
# category type for anything we're doing further, just the text values.

# ---------------------------------------------------------------------------
# STEP 2: Define severity tiers using pd.cut()
# ---------------------------------------------------------------------------
# percentage_laid_off is a decimal fraction (0.05 = 5%, 1.0 = 100%).
# We're splitting it into four business-meaningful bands. As in
# Analysis #2, we use pd.cut() (fixed value ranges we choose) rather
# than pd.qcut() (automatic percentile-based ranges), because "cut
# more than half the company" is a meaningful real-world threshold,
# while a percentile boundary like "top 23.7%" isn't something a
# business audience would find intuitive.
severity_bins = [-0.01, 0.10, 0.25, 0.50, 1.01]
# Starting at -0.01 and ending at 1.01 (instead of 0 and 1.0) ensures
# the exact edge values of 0% and 100% are safely included, since
# pd.cut's bins are exclusive on the left edge by default.
severity_labels = ["Mild (<=10%)", "Moderate (10-25%)", "Severe (25-50%)", "Critical (>50%)"]

df["severity_tier"] = pd.cut(
    df["percentage_laid_off"], bins=severity_bins, labels=severity_labels
)
# Rows where percentage_laid_off is missing (NaN) automatically get
# NaN in severity_tier too - pd.cut can't categorize a value it
# doesn't have. We leave these as missing rather than guessing, since
# your SQL cleaning already made a deliberate decision to keep these
# rows (they had a valid total_laid_off even without a percentage).

# ---------------------------------------------------------------------------
# STEP 3: Check how many events fall into each tier
# ---------------------------------------------------------------------------
# .value_counts() counts how many rows have each unique value in a
# column - a quick way to see the overall shape of our new tiers
# before cross-checking them against other columns.
print("Layoff events per severity tier:")
print(df["severity_tier"].value_counts().sort_index())

# ---------------------------------------------------------------------------
# STEP 4: Cross-tabulate severity tier against industry
# ---------------------------------------------------------------------------
# pd.pivot_table() reshapes data by putting one column's unique values
# as rows, another column's unique values as columns, and filling in
# an aggregated number where they intersect - similar to a PivotTable
# in Excel.
#
# Here: rows = industry, columns = severity_tier, values = how many
# layoff EVENTS fall into each combination. aggfunc="size" just counts
# rows in each combination (we don't need to average or sum anything
# here, just count how often each combination occurs).
industry_severity_table = pd.pivot_table(
    df,
    index="industry",
    columns="severity_tier",
    values="company",   # any column works here since we're just counting rows
    aggfunc="size",
    fill_value=0,        # if a combination never occurs, show 0 instead of blank
    observed=True,
)

print("\nIndustry x Severity Tier (event counts):")
print(industry_severity_table)

# ---------------------------------------------------------------------------
# STEP 5: Check whether repeat-layoff companies skew toward higher severity
# ---------------------------------------------------------------------------
# Same pivot_table idea, but comparing severity tier against the
# is_repeat_layoff_company flag we built in Analysis #2. This directly
# answers: "when a repeat-layoff company has an event, is it more
# often a severe one, compared to a one-time layoff company?"
#
# normalize="index" (used inside pd.crosstab, a shortcut function
# specifically for two-column count tables) converts the raw counts
# into PERCENTAGES within each row, so we can fairly compare a group
# with many events to a group with few - raw counts alone wouldn't
# tell us if severe events are proportionally more common in one
# group, only that there might be more events in general.
repeat_vs_severity = pd.crosstab(
    df["is_repeat_layoff_company"], df["severity_tier"], normalize="index"
)
repeat_vs_severity = (repeat_vs_severity * 100).round(1)
# Multiplying by 100 and rounding turns the 0-1 proportions into
# readable percentages, e.g. 0.386 becomes 38.6.

print("\n% of events in each severity tier, by repeat-layoff status:")
print(repeat_vs_severity)

# ---------------------------------------------------------------------------
# STEP 6: Save the enriched master dataset
# ---------------------------------------------------------------------------
df.to_csv("layoffs_master_enriched.csv", index=False)
print("\nUpdated: layoffs_master_enriched.csv")
print(f"Columns now in the master dataset: {list(df.columns)}")
