"""
STAGE 2 - ANALYSIS #1
DATA QUALITY VERIFICATION
============================================================

BUSINESS QUESTION
------------------
Which companies laid off staff more than once? For those companies,
how much time passed between their layoff rounds? Were the rounds
close together (an ongoing crisis) or spread far apart (separate,
unrelated downturns)?

WHY PYTHON INSTEAD OF SQL
---------------------------
This requires comparing each layoff event to the PREVIOUS event for
the SAME company, sorted by date. SQL can do this with a self-join or
a LAG() window function, but it takes several lines and is harder to
read at a beginner level. Pandas has a single method built exactly for
this ("difference from the row before it, within a group"), so the
code stays short and easy to explain in an interview.
"""

import pandas as pd

# ---------------------------------------------------------------------------
# STEP 1: Load the cleaned dataset
# ---------------------------------------------------------------------------
# Same as Stage 1 - parse_dates=["date"] converts the date column from
# plain text into pandas' real datetime type, so we can do date math
# (like subtracting one date from another) instead of treating dates
# as strings.
df = pd.read_csv("layoff2.csv", parse_dates=["date"])

# Some rows have a missing date (we saw 1 in Stage 1's verification).
# We can't calculate "days between events" for a row with no date, so
# we exclude those specific rows FOR THIS ANALYSIS ONLY. This is not
# the same as deleting them from the dataset - we're just skipping
# them in this one calculation because a missing date makes the
# calculation impossible, not because the row is bad data.
#
# df["date"].notna() returns True for every row where date IS present,
# False where it's missing (NaN). Wrapping the whole dataframe in
# df[...] with that condition keeps only the True rows.
df_with_dates = df[df["date"].notna()].copy()
# .copy() makes an independent copy of this filtered data. Without it,
# pandas sometimes gives a "view" into the original df, and editing it
# later can trigger a confusing warning. Using .copy() avoids that.

# ---------------------------------------------------------------------------
# STEP 2: Count how many layoff events each company had
# ---------------------------------------------------------------------------
# .groupby("company") groups all rows by company name.
# .size() counts how many rows fall into each group - i.e., how many
# separate layoff events each company had in the dataset.
event_counts = df_with_dates.groupby("company").size()

# This gives us a pandas "Series" (a single column of values, with
# company names as the label for each value, not a full table yet).
# We only care about companies with MORE than one event, so we filter:
repeat_companies = event_counts[event_counts > 1].index
# .index pulls out just the company NAMES (the labels) from that
# filtered Series, as a list-like object we can use to filter the
# main dataframe next.

print(f"Number of companies with more than one layoff event: {len(repeat_companies)}")

# ---------------------------------------------------------------------------
# STEP 3: Build a dataframe containing only repeat-layoff companies
# ---------------------------------------------------------------------------
# .isin(repeat_companies) checks, for every row, whether that row's
# company name appears in our repeat_companies list. It returns
# True/False for each row, and df[...] keeps only the True ones.
df_repeats = df_with_dates[df_with_dates["company"].isin(repeat_companies)].copy()

# We sort by company first (so all of one company's events are grouped
# together) and then by date (so within each company, events are in
# chronological order - earliest first). This ordering is REQUIRED
# for the next step to work correctly, since .diff() only makes sense
# on data that's in the right order.
df_repeats = df_repeats.sort_values(by=["company", "date"])

# ---------------------------------------------------------------------------
# STEP 4: Calculate days between each company's layoff events
# ---------------------------------------------------------------------------
# .groupby("company")["date"].diff() looks at the date column, and for
# each row, subtracts the PREVIOUS row's date - but only comparing rows
# within the same company group (that's what makes groupby different
# from a plain .diff() on the whole column, which would incorrectly
# compare across different companies).
#
# The first event for each company will show "NaT" (Not a Time - the
# missing-value marker for dates), since there's no earlier event to
# compare it to. That's expected and correct.
df_repeats["days_since_previous_layoff"] = (
    df_repeats.groupby("company")["date"].diff().dt.days
)
# .dt.days converts the raw difference (which pandas returns as a
# "Timedelta", e.g. "45 days") into a plain whole number (45), which
# is easier to read and to use in Power BI later.

# ---------------------------------------------------------------------------
# STEP 5: Build a per-company summary table
# ---------------------------------------------------------------------------
# .agg() lets us calculate several different summary statistics at
# once, for each group, and name the resulting columns ourselves.
# Here, for each company, we calculate:
#   - how many layoff events they had
#   - the date of their first and last layoff event
#   - the total people laid off across all their events combined
#   - the average number of days between their layoff events
company_summary = df_repeats.groupby("company").agg(
    number_of_layoff_events=("date", "count"),
    first_layoff_date=("date", "min"),
    last_layoff_date=("date", "max"),
    total_laid_off_all_events=("total_laid_off", "sum"),
    average_days_between_layoffs=("days_since_previous_layoff", "mean"),
)

# .reset_index() turns "company" from a row label back into a normal
# column. This matters because Power BI (and most tools) expect every
# piece of data to live in a regular column, not as an index label.
company_summary = company_summary.reset_index()

# Round the average to 1 decimal place, purely for readability -
# "134.3 days" is easier to scan than "134.28571428571428 days".
company_summary["average_days_between_layoffs"] = company_summary[
    "average_days_between_layoffs"
].round(1)

# Sort so the companies with the MOST layoff events appear first -
# these are the most "repeat offenders" and the most interesting rows
# for a reader to see at the top of the table.
company_summary = company_summary.sort_values(
    by="number_of_layoff_events", ascending=False
)

print("\nTop repeat-layoff companies:")
print(company_summary.head(10).to_string(index=False))

# ---------------------------------------------------------------------------
# STEP 6: Export both tables for Power BI
# ---------------------------------------------------------------------------
# We export TWO files because they answer different questions and will
# power different visuals in Power BI (explained in the Power BI plan
# below).
#
# index=False stops pandas from writing its own row-number column into
# the CSV (e.g. 0, 1, 2...) which we don't want - Power BI doesn't need
# it and it would just be a confusing extra column.
company_summary.to_csv("repeat_layoff_companies_summary.csv", index=False)
df_repeats.to_csv("repeat_layoff_events_detail.csv", index=False)

print("\nExported: repeat_layoff_companies_summary.csv")
print("Exported: repeat_layoff_events_detail.csv")
