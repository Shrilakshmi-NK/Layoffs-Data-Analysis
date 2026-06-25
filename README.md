# Global Layoffs Data Analysis using SQL

## 📌 Project Overview

This project focuses on cleaning and analyzing a global layoffs dataset using MySQL. The objective was to improve data quality, perform exploratory data analysis (EDA), and identify trends in workforce reductions across companies, industries, countries, and time periods.

The project demonstrates practical SQL skills including data cleaning, data transformation, aggregation, Common Table Expressions (CTEs), window functions, and business-oriented analysis.

---

## 📊 Dataset

The dataset contains information related to layoffs across companies worldwide, including:

- Company
- Industry
- Country
- Location
- Total Laid Off
- Percentage Laid Off
- Funding Stage
- Date
- Funds Raised

---

## 🧹 Data Cleaning

The following data cleaning operations were performed:

- Removed duplicate records using `ROW_NUMBER()`
- Standardized company names and industry values
- Cleaned country and location fields
- Converted date values into a consistent format
- Handled null and missing values
- Improved overall data consistency and quality

### Data Cleaning Techniques Used

- `ROW_NUMBER()`
- `UPDATE`
- `DELETE`
- `TRIM()`
- `STR_TO_DATE()`
- `CASE` Statements
- Common Table Expressions (CTEs)

---

## 🔍 Exploratory Data Analysis

Performed SQL-based analysis to answer business questions such as:

- Which companies experienced the highest layoffs?
- Which industries were most affected?
- Which countries had the largest workforce reductions?
- How did layoffs change over time?
- Which funding stages were associated with higher layoffs?
- What were the yearly and monthly layoff trends?
- Which companies had the highest layoffs within each year?

---

## 🛠 SQL Concepts Used

- SELECT Statements
- WHERE Clauses
- GROUP BY
- ORDER BY
- Aggregate Functions
- CASE Statements
- Common Table Expressions (CTEs)
- Window Functions
- ROW_NUMBER()
- DENSE_RANK()
- Rolling Totals
- Date Functions

---

## 📈 Key Insights

- Certain industries experienced significantly higher layoffs than others.
- Layoffs varied across countries and years.
- Several highly funded companies still underwent major workforce reductions.
- Monthly analysis revealed periods of concentrated layoffs activity.
- Workforce reductions were influenced by both industry type and company growth stage.

---

## 💻 Technologies Used

- MySQL
- SQL

---

## 📂 Project Structure

```
Global-Layoffs-Data-Analysis/
│
├── Data Cleaning.sql
├── Data Exploration.sql
├── layoffs.csv
└── README.md
```

---

## 🎯 Learning Outcomes

Through this project, I gained hands-on experience in:

- Data Cleaning and Transformation
- Exploratory Data Analysis (EDA)
- SQL Query Optimization
- Window Functions and Ranking Techniques
- Business-Oriented Data Analysis
- Data Quality Improvement

