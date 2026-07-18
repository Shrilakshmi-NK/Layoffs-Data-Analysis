# Global Layoffs Analysis (2020–2023)
### End-to-End Analytics Project — MySQL → Python → Power BI

---

## 1. Project Overview
A three-stage analytics pipeline analyzing global tech layoffs from 2020–2023, using MySQL for data cleaning and foundational SQL EDA, Python for advanced statistical analysis, and Power BI for the final interactive dashboard.

## 2. Business Problem
Between 2020 and 2023, thousands of companies conducted layoffs. Raw totals alone don't reveal *why* or *how* — this project investigates whether layoff severity is tied to company funding, whether layoffs were one-time shocks or repeated events, and which companies behaved statistically differently from their peers.

## 3. Dataset Description
- **Source:** [add original dataset source/link]
- **Size:** ~2,360 raw records → 1,994 after cleaning
- **Fields:** company, location, industry, total_laid_off, percentage_laid_off, date, stage, country, funds_raised_millions

## 4. SQL Work Completed
- Removed duplicate records using `ROW_NUMBER()` window function
- Standardized inconsistent text values (industry, country) and trimmed whitespace
- Converted date strings to proper `DATE` type
- Handled NULL/blank values (backfilled industry from related records, removed unrecoverable rows)
- Exploratory SQL: totals by company/industry/country, monthly trends, rolling totals, top companies by year (ranked with `DENSE_RANK()`)

## 5. Python Analyses Performed
1. **Repeat Layoff Companies** — identified companies with multiple layoff rounds and calculated time between events
2. **Funding vs. Layoff Severity Correlation** — tested the relationship between funds raised and % of staff laid off (raw + log-transformed)
3. **Layoff Severity Segmentation** — bucketed events into Mild/Moderate/Severe/Critical tiers and cross-tabulated against repeat-layoff status and industry
4. **Statistical Outlier Detection** — flagged layoff events that were abnormal relative to their funding bracket, using the IQR method

Output: a single enriched, dashboard-ready dataset (`layoffs_master_enriched_final.csv`)

## 6. Key Business Insights
- Companies that raised more funding laid off a consistently smaller *percentage* of staff (38.6% for Small vs. 16.0% for Mega-funded companies)
- Repeat-layoff companies were ~3x less likely to have a Critical-severity (>50%) event than one-time layoff companies — repeated cuts tend to be smaller and more controlled
- 94 layoff events were statistically abnormal for their funding level — mostly full (100%) shutdowns among Medium-to-Mega funded companies
- Healthcare, Food, Finance, and Retail had the highest concentration of Critical-severity events

## 7. Technologies Used
- **MySQL / MySQL Workbench** — data cleaning, SQL-based EDA
- **Python** (pandas, NumPy) — statistical analysis, feature engineering
- **Power BI** — interactive dashboard and final storytelling layer
- **Git/GitHub** — version control and project hosting

## 8. Power BI Dashboard Overview
- **Headline visuals:** funding vs. severity scatter plot, severity-tier breakdown by repeat-layoff status
- **Supporting visuals:** top repeat-layoff companies table, statistical outlier spotlight table
- **Slicers:** industry, country, funding bracket, date range
- [Add dashboard screenshot(s) here once built]

## 9. Folder Structure
```
├── sql/
│   ├── data_cleaning.sql
│   └── data_exploration.sql
├── python/
│   ├── stage1_data_quality_check.py
│   ├── stage2_analysis1_repeat_layoffs.py
│   ├── stage2_analysis2_funding_correlation.py
│   ├── stage2_analysis3_severity_segmentation.py
│   └── stage2_analysis4_outlier_detection.py
├── data/
│   ├── layoffs_raw.csv
│   └── layoffs_master_enriched_final.csv
├── powerbi/
│   └── layoffs_dashboard.pbix
└── README.md
```

## 10. Future Improvements
- Incorporate a second dataset (e.g., stock performance or hiring data) to test whether layoffs preceded or followed other business signals
- Automate the SQL → Python → Power BI refresh pipeline
- Add a predictive model estimating layoff likelihood/severity from company attributes

<img width="787" height="440" alt="image" src="https://github.com/user-attachments/assets/e88a9a5f-d315-44bb-8002-324c6dcce013" />
