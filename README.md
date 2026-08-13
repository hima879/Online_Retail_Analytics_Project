# Online Retail Analytics Project

An end-to-end retail analytics project analyzing 391,150 transactions from a UK-based online gift retailer.

## Project Structure
Online_Retail_Analytics_Project/
├── README.md
├── requirements.txt
├── data/
│ ├── online_retail_raw.xlsx # Raw dataset
│ ├── cleaned_retail.csv # Cleaned data
│ ├── cleaned_retail.parquet # Fast loading format
│ └── retail.db # SQLite database
├── scripts/
│ ├── 01_data_cleaning.py # Data cleaning pipeline
│ ├── 02_sql_analysis.py # SQL business queries
│ ├── 03_eda_visualizations.py # Exploratory analysis
│ ├── 04_rfm_segmentation.py # RFM + K-Means clustering
│ └── 05_cohort_analysis.py # Cohort retention analysis
├── sql/
│ └── queries.sql # Standalone SQL queries
├── charts/ # Generated visualizations
├── outputs/ # Analysis results (CSVs)
└── dashboard/
└── app.py # Streamlit dashboard

## Setup
```bash
pip install -r requirements.txt
Run Pipeline

cd scripts
python 01_data_cleaning.py
python 02_sql_analysis.py
python 03_eda_visualizations.py
python 04_rfm_segmentation.py
python 05_cohort_analysis.py
Run Dashboard

cd dashboard
streamlit run app.py
