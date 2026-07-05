"""
STAGE 1 — DATA QUALITY VERIFICATION
=====================================

PURPOSE
-------
Your MySQL script already did the real cleaning work: removing duplicates,
standardizing text, fixing dates, and handling nulls. This script does NOT
repeat that. Instead, it's a quick "trust but verify" pass — we load the
cleaned CSV in Python and confirm it actually looks the way SQL says it
should before we build anything on top of it.

Think of this like a final quality-check inspector on an assembly line:
the product is already built, we're just making sure nothing broke on
the way out the door (e.g. during CSV export, which is a common place for
subtle issues like date formats or number types to get scrambled).

WHY THIS MATTERS FOR THE PROJECT
---------------------------------
If you skip this step and there's a hidden issue (say, dates got exported
as text instead of real dates), every chart and insight built afterward
could be subtly wrong. Five minutes of verification now saves hours of
confused debugging later.
"""

import pandas as pd

# ---------------------------------------------------------------------------
# STEP 1: Load the data
# ---------------------------------------------------------------------------
# pd.read_csv() reads a CSV file into a "DataFrame" — pandas' main data
# structure, basically a table with rows and labeled columns (like an
# Excel sheet, but you can manipulate it with code).
#
# parse_dates=["date"] tells pandas: "the 'date' column contains dates,
# please convert it to an actual datetime type, not just text." This
# matters because SQL already converted this column to a proper DATE type,
# so we want Python to recognize it the same way — otherwise things like
# sorting by date or extracting the month would behave like sorting text
# alphabetically instead of chronologically.
df = pd.read_csv("layoff2.csv", parse_dates=["date"])

print("=" * 60)
print("STAGE 1: DATA QUALITY VERIFICATION")
print("=" * 60)

# ---------------------------------------------------------------------------
# STEP 2: Check the shape and column types
# ---------------------------------------------------------------------------
# df.shape returns (number_of_rows, number_of_columns). This is a quick
# sanity check: does the row count roughly match what you saw in MySQL
# after your DELETE statements? If MySQL Workbench showed ~1994 rows
# after cleaning, we expect to see the same number here.
print(f"\n[Shape] Rows: {df.shape[0]}, Columns: {df.shape[1]}")

# df.dtypes shows the data type pandas assigned to each column
# (e.g. int64 for whole numbers, float64 for decimals, object for text,
# datetime64 for dates). We're checking that:
#   - total_laid_off and funds_raised_millions are numeric (not text)
#   - date is datetime64 (not object/text)
# If any of these come back as "object" when they shouldn't, that's a
# sign something went wrong in the SQL->CSV export, not a Python problem
# to silently patch — it would mean going back to check the export step.
print("\n[Data Types]")
print(df.dtypes)

# ---------------------------------------------------------------------------
# STEP 3: Confirm duplicates are actually gone
# ---------------------------------------------------------------------------
# df.duplicated() checks every row against every other row and returns
# True/False for whether it's an exact repeat of one seen before.
# .sum() then adds up all the Trues (True counts as 1, False as 0) to
# give a total count of duplicate rows.
# We EXPECT this to be 0, since your SQL script already removed duplicates.
# We're not fixing anything here — just confirming SQL's work held up
# through the CSV export.
duplicate_count = df.duplicated().sum()
print(f"\n[Duplicates] Exact duplicate rows found: {duplicate_count}")

# ---------------------------------------------------------------------------
# STEP 4: Review missing values
# ---------------------------------------------------------------------------
# df.isnull() marks every cell True if it's missing (NaN) or False if it
# has a value. .sum() adds these up per column, giving a missing-value
# count for each one.
#
# IMPORTANT: we are NOT filling these in or deleting rows here. Your SQL
# script made deliberate decisions about which nulls to fix (e.g. filling
# industry from a sister row) and which to leave alone (e.g. rows where
# percentage_laid_off is genuinely unknown). This step just documents the
# current state so we know what we're working with going forward.
print("\n[Missing Values per Column]")
print(df.isnull().sum())

# ---------------------------------------------------------------------------
# STEP 5: Sanity-check numeric ranges
# ---------------------------------------------------------------------------
# df.describe() gives summary statistics (min, max, mean, etc.) for
# numeric columns in one call. We're using this to eyeball whether any
# numbers look impossible — for example, a negative total_laid_off, or a
# percentage_laid_off above 1.0 (since it's stored as a decimal fraction,
# e.g. 0.15 = 15%, so anything above 1.0 wouldn't make sense).
print("\n[Numeric Summary]")
print(df[["total_laid_off", "percentage_laid_off", "funds_raised_millions"]].describe())

# A more targeted check: explicitly flag rows where percentage_laid_off
# is out of the valid 0-to-1 range, if any exist. This uses "boolean
# indexing" — df[condition] returns only the rows where condition is True.
invalid_pct = df[(df["percentage_laid_off"] < 0) | (df["percentage_laid_off"] > 1)]
print(f"\n[Range Check] Rows with percentage_laid_off outside 0-1: {len(invalid_pct)}")

# ---------------------------------------------------------------------------
# STEP 6: Confirm the date range makes sense
# ---------------------------------------------------------------------------
# .min() and .max() on a datetime column give the earliest and latest
# dates in the dataset. This is just a plausibility check — does the
# range match what you'd expect for a "recent layoffs" dataset (e.g.
# 2020 through 2023), rather than some obviously wrong date like 1970
# or 2099 that would suggest a parsing error?
print(f"\n[Date Range] Earliest: {df['date'].min()}, Latest: {df['date'].max()}")

print("\n" + "=" * 60)
print("Verification complete. Review the output above before proceeding.")
print("=" * 60)
