# SafeTrade Data Cleaning & Analysis Pipeline

##  Overview

This sub-project focuses on transforming raw survey data into a clean, structured, and analysis-ready dataset to support the SafeTrade concept — a safer online trading platform.

The goal was to simulate a real-world data workflow:

> **Raw data → Cleaning → Feature engineering → Usable insights**

---

## Objectives

* Clean and standardize messy survey data
* Handle missing values appropriately
* Convert unstructured text into structured features
* Prepare the dataset for analysis and decision-making
* Generate reproducible outputs and reports

---

##  Project Structure

```
SafeTrade_Data_Project/
│
├── data/
│   ├── raw/            # Original dataset (untouched)
│   ├── cleaned/        # Final cleaned datasets
│
├── notebooks/
│   └── data_cleaning.ipynb
│
├── reports/
│   ├── missing_report.csv
│   ├── missing_report.md
│
└── README.md
```

---

##  Data Processing Pipeline

### 1. Data Ingestion

* Loaded data from a live source (Google Sheets / Excel)
* Converted into a Pandas DataFrame

---

### 2. Column Standardization

* Renamed columns to `snake_case`
* Removed spaces and inconsistencies
* Fixed column naming errors

---

### 3. Data Cleaning

* Handled missing values based on column type:

  * Structured fields → cleaned carefully
  * Optional text fields → preserved meaning
* Converted incorrect data types (e.g., phone → string)
* Removed inconsistencies in categorical values

---

### 4. Feature Engineering

#### 🔹 Categorical Standardization

* `scam_experience` → structured categories
* `safety_feeling` → normalized + scored (1–5)

#### 🔹 Multi-Value Columns

Split and encoded:

* `top_concerns`
* `wanted_features`

Converted into binary indicator features (0/1)

#### 🔹 Pricing Model

Transformed messy inputs into:

* `price_category` (low, high, none, percentage)
* `price_estimate` (numeric approximation)

#### 🔹 Payment Behavior

* `when_pay` → `payment_timing` (before / after)

---

### 5. Data Outputs

#### Clean Dataset:

* `data/cleaned/safetrade_cleaned.csv`
* `data/cleaned/safetrade_cleaned.xlsx`

#### Reports:

* Missing data report (CSV + Markdown)
* Reproducible outputs for validation

---

##  Key Insights (Example)

* Majority of users prefer **paying after a transaction**
* High concern around:

  * Fake sellers
  * Payment fraud
* Strong demand for:

  * Escrow-based payments
  * Verified users
* Most users are only willing to pay **low transaction fees**

---

## Key Learnings

* Importance of structured data pipelines
* Handling messy real-world survey data
* Converting qualitative input into quantitative signals
* Building reproducible and scalable workflows

---

## Next Steps

* Exploratory Data Analysis (EDA)
* Visualization (Power BI / Tableau)
* Fraud risk scoring model
* Integration into SafeTrade system design

---

## Tools Used

* Python
* Pandas
* Jupyter Notebook

---

## Author

Tshidiso Molefe

---

## Notes

This project is part of a larger SafeTrade system aimed at improving trust and safety in online marketplaces through data-driven insights.
