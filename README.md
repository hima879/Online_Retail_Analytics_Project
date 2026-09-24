# 🛍️ Online Retail Analytics

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0-blueviolet)](https://pandas.pydata.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3-orange)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end retail analytics project analysing **391,150** transactions from a UK-based online gift retailer (Dec 2010 – Dec 2011). It covers data cleaning, exploratory analysis, SQL business queries, RFM customer segmentation, cohort retention analysis, and an interactive Streamlit dashboard.

🔗 **Live Dashboard:** [Streamlit App](https://onlineretailanalyticsproject-8wzfxzycjxgqmxcutnp8ef.streamlit.app/)

---

## 📌 Project Highlights

| Metric | Value |
|---|---|
| Total Revenue | £8.3M |
| Total Orders | 22,500+ |
| Unique Customers | 4,300+ |
| Best Month | December 2011 (£1.1M) |
| Top Country | UK (82% of sales) |
| Month 1 → Month 2 Retention | 28% |
| Customer Segments | 6 (Champions, Loyal, At-Risk, etc.) |

---

## ✨ Key Features

- **Data Cleaning** — handles missing values, cancellations, negative quantities, and outliers.
- **Exploratory Data Analysis (EDA)** — visualises sales trends, top products, and country-wise performance.
- **SQL Business Queries** — answers key business questions (monthly revenue, top customers, product popularity).
- **RFM Segmentation** — clusters customers using Recency, Frequency, and Monetary value with K-Means.
- **Cohort Retention Analysis** — tracks customer retention over time with monthly cohort heatmaps.
- **Interactive Dashboard** — explores all metrics and segments in a Streamlit app.

---

## 📊 Dataset Overview

The dataset (`online_retail_raw.xlsx`) contains transactions from a UK-based online retailer between **01/12/2010** and **09/12/2011**, sourced from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/Online+Retail).

| Field | Description |
|---|---|
| `InvoiceNo` | Invoice number (cancellations start with 'C') |
| `StockCode` | Product code |
| `Description` | Product name |
| `Quantity` | Units purchased |
| `InvoiceDate` | Date and time of transaction |
| `UnitPrice` | Price per unit (GBP) |
| `CustomerID` | Unique customer identifier |
| `Country` | Customer's country |

After cleaning, the data is saved as `cleaned_retail.parquet` for fast loading and `retail.db` (SQLite) for querying.

---

## 📁 Project Structure

```
Online_Retail_Analytics_Project/
├── README.md
├── requirements.txt
├── data/
│   ├── online_retail_raw.xlsx   # Raw dataset (not included in repo)
│   ├── cleaned_retail.csv       # Cleaned data (CSV)
│   ├── cleaned_retail.parquet   # Fast loading format
│   └── retail.db                # SQLite database
├── scripts/
│   ├── 01_data_cleaning.py      # Data cleaning pipeline
│   ├── 02_sql_analysis.py       # SQL business queries
│   ├── 03_eda_visualizations.py # Exploratory analysis plots
│   ├── 04_rfm_segmentation.py   # RFM + K-Means clustering
│   └── 05_cohort_analysis.py    # Cohort retention analysis
├── sql/
│   └── queries.sql              # Standalone SQL queries
├── charts/                      # Generated visualizations
├── outputs/                     # Analysis results (CSVs)
└── dashboard/
    └── app.py                   # Streamlit dashboard
```

---

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/hima879/Online_Retail_Analytics_Project.git
   cd Online_Retail_Analytics_Project
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Place the raw dataset**
   Download `online_retail_raw.xlsx` from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/Online+Retail) and place it inside the `data/` folder.

---

## 🛠️ Usage

### Run the analysis pipeline

Execute the scripts in order (or individually). All outputs — charts, CSVs, and the database — are saved in their respective folders.

```bash
cd scripts
python 01_data_cleaning.py
python 02_sql_analysis.py
python 03_eda_visualizations.py
python 04_rfm_segmentation.py
python 05_cohort_analysis.py
```

### Launch the dashboard

```bash
cd dashboard
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## 📈 Results & Insights

### 🧹 Data Cleaning
- Removed **~5,400** cancelled orders (invoice numbers starting with 'C')
- Dropped **135,000+** rows with missing `CustomerID`
- Filtered out negative quantities and non-positive unit prices

### 📊 Sales Trends
- Monthly revenue peaks in **November and December** (holiday season)
- **Top 5 countries** by revenue: UK, Netherlands, Ireland, Germany, France
- **Best-selling product:** *WHITE HANGING HEART T-LIGHT HOLDER* (2,300+ units)

### 🧑‍🤝‍🧑 Customer Segmentation (RFM + K-Means)

| Segment | Characteristics | % of Customers |
|---|---|---|
| **Champions** | High recency, frequency, monetary | 12% |
| **Loyal** | Frequent recent buyers | 18% |
| **Potential** | Average RFM, but active | 25% |
| **At-Risk** | High spend, no recent purchases | 20% |
| **New** | Recent first-time buyers | 15% |
| **Hibernating** | Low on all metrics | 10% |

### 📉 Cohort Retention
- Month-over-month retention drops from **100%** (month 0) to **~28%** after the first month
- **12-month retention** is ~4% — a clear opportunity for re-engagement campaigns

---

## 🖥️ Dashboard Preview

*(Add a screenshot of your dashboard here)*

The Streamlit dashboard offers interactive views of:
- **Key metrics** — revenue, orders, customers
- **Sales trends** — line and bar charts
- **Product performance** — top products and category breakdown
- **RFM segmentation** — scatter plots and segment distribution
- **Cohort retention** — heatmap

---

## 🧰 Technologies Used

- **Python** — data processing (Pandas, NumPy)
- **SQLite** — data storage and querying
- **Scikit-learn** — K-Means clustering
- **Matplotlib & Seaborn** — static visualisations
- **Plotly** — interactive charts in the dashboard
- **Streamlit** — web dashboard framework

---

## 🤝 Contributing

Contributions are welcome! Fork the repository and submit a pull request with your improvements. For major changes, open an issue first to discuss what you'd like to change.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Dataset provided by the [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/Online+Retail).
- Inspired by real-world retail analytics challenges.

**Happy analysing!** 📊
