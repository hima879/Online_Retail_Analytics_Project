"""
Step 2: SQL Business Analysis
Loads cleaned data into SQLite and runs business queries
"""

import pandas as pd
import sqlite3
import os
from pathlib import Path

# Set up paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = PROJECT_ROOT / 'outputs'
SQL_DIR = PROJECT_ROOT / 'sql'

# Create directories if needed
OUTPUT_DIR.mkdir(exist_ok=True)
SQL_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("STEP 2: SQL BUSINESS ANALYSIS")
print("=" * 60)

# 1. Load cleaned data
print("\n1. Loading cleaned data...")
df = pd.read_csv(DATA_DIR / 'cleaned_retail.csv', parse_dates=['InvoiceDate'])
print(f"   Loaded {len(df):,} transactions")

# 2. Create SQLite database
print("\n2. Creating SQLite database...")
db_path = DATA_DIR / 'retail.db'
conn = sqlite3.connect(db_path)

# Load data into SQLite
df.to_sql('transactions', conn, if_exists='replace', index=False)
print(f"   Database created at: {db_path}")

# 3. Run SQL queries
print("\n3. Running SQL queries...")

# Dictionary to store results
query_results = {}

# Query 1: Monthly revenue trend
query1 = """
SELECT 
    InvoiceYearMonth AS month,
    ROUND(SUM(TotalPrice), 2) AS revenue,
    COUNT(DISTINCT InvoiceNo) AS orders,
    ROUND(AVG(TotalPrice), 2) AS avg_order_value
FROM transactions
GROUP BY InvoiceYearMonth
ORDER BY month;
"""
monthly_revenue = pd.read_sql(query1, conn)
query_results['monthly_revenue'] = monthly_revenue
print(f"   ✓ Monthly revenue trend: {len(monthly_revenue)} months")

# Query 2: Top 10 products by revenue
query2 = """
SELECT 
    StockCode,
    Description,
    ROUND(SUM(TotalPrice), 2) AS revenue,
    COUNT(DISTINCT InvoiceNo) AS order_count,
    SUM(Quantity) AS total_quantity
FROM transactions
GROUP BY StockCode, Description
ORDER BY revenue DESC
LIMIT 10;
"""
top_products = pd.read_sql(query2, conn)
query_results['top_products'] = top_products
print(f"   ✓ Top 10 products identified")

# Query 3: Revenue by country
query3 = """
SELECT 
    Country,
    ROUND(SUM(TotalPrice), 2) AS revenue,
    COUNT(DISTINCT CustomerID) AS customers,
    COUNT(DISTINCT InvoiceNo) AS orders
FROM transactions
WHERE Country != 'United Kingdom'
GROUP BY Country
ORDER BY revenue DESC
LIMIT 10;
"""
country_revenue = pd.read_sql(query3, conn)
query_results['country_revenue'] = country_revenue
print(f"   ✓ Top 10 countries by revenue")

# Query 4: Average order value
query4 = """
SELECT 
    ROUND(AVG(order_total), 2) AS avg_order_value
FROM (
    SELECT 
        InvoiceNo,
        SUM(TotalPrice) AS order_total
    FROM transactions
    GROUP BY InvoiceNo
);
"""
avg_order_value = pd.read_sql(query4, conn)
query_results['avg_order_value'] = avg_order_value
print(f"   ✓ Average order value: £{avg_order_value.iloc[0, 0]:,.2f}")

# Query 5: Repeat customer rate
query5 = """
WITH customer_orders AS (
    SELECT 
        CustomerID,
        COUNT(DISTINCT InvoiceNo) AS order_count
    FROM transactions
    GROUP BY CustomerID
)
SELECT 
    COUNT(CASE WHEN order_count > 1 THEN 1 END) AS repeat_customers,
    COUNT(*) AS total_customers,
    ROUND(100.0 * COUNT(CASE WHEN order_count > 1 THEN 1 END) / COUNT(*), 1) AS repeat_rate_pct
FROM customer_orders;
"""
repeat_rate = pd.read_sql(query5, conn)
query_results['repeat_rate'] = repeat_rate
print(f"   ✓ Repeat customer rate: {repeat_rate.iloc[0, 2]:.1f}%")

# Query 6: Best day of week
query6 = """
SELECT 
    InvoiceDayOfWeek AS day,
    ROUND(SUM(TotalPrice), 2) AS revenue,
    COUNT(DISTINCT InvoiceNo) AS orders
FROM transactions
GROUP BY InvoiceDayOfWeek
ORDER BY revenue DESC;
"""
best_day = pd.read_sql(query6, conn)
query_results['best_day'] = best_day
print(f"   ✓ Best day: {best_day.iloc[0, 0]} (£{best_day.iloc[0, 1]:,.2f})")

# Query 7: Top customers by lifetime spend
query7 = """
SELECT 
    CustomerID,
    ROUND(SUM(TotalPrice), 2) AS lifetime_value,
    COUNT(DISTINCT InvoiceNo) AS frequency,
    COUNT(*) AS total_items,
    MAX(InvoiceDate) AS last_purchase
FROM transactions
GROUP BY CustomerID
ORDER BY lifetime_value DESC
LIMIT 20;
"""
top_customers = pd.read_sql(query7, conn)
query_results['top_customers'] = top_customers
print(f"   ✓ Top 20 customers identified")

# Query 8: RFM components (for next step)
query8 = """
SELECT 
    CustomerID,
    JULIANDAY((SELECT MAX(InvoiceDate) FROM transactions)) - JULIANDAY(MAX(InvoiceDate)) AS recency_days,
    COUNT(DISTINCT InvoiceNo) AS frequency,
    ROUND(SUM(TotalPrice), 2) AS monetary
FROM transactions
GROUP BY CustomerID
ORDER BY monetary DESC;
"""
rfm_components = pd.read_sql(query8, conn)
query_results['rfm_components'] = rfm_components
print(f"   ✓ RFM components extracted for {len(rfm_components):,} customers")

# 4. Save all results
print("\n4. Saving results...")

# Save each query result to CSV
for name, df_result in query_results.items():
    output_path = OUTPUT_DIR / f'sql_{name}.csv'
    df_result.to_csv(output_path, index=False)
    print(f"   Saved: {output_path}")

# 5. Save SQL queries to a separate file for reference
print("\n5. Saving SQL queries to file...")

sql_queries_file = SQL_DIR / 'queries.sql'
with open(sql_queries_file, 'w') as f:
    f.write("-- ============================================================\n")
    f.write("-- SQL QUERIES FOR ONLINE RETAIL ANALYSIS\n")
    f.write("-- Generated by 02_sql_analysis.py\n")
    f.write("-- ============================================================\n\n")
    
    # Query 1
    f.write("-- 1. Monthly revenue trend\n")
    f.write(query1)
    f.write("\n\n")
    
    # Query 2
    f.write("-- 2. Top 10 products by revenue\n")
    f.write(query2)
    f.write("\n\n")
    
    # Query 3
    f.write("-- 3. Revenue by country (excluding UK)\n")
    f.write(query3)
    f.write("\n\n")
    
    # Query 4
    f.write("-- 4. Average order value\n")
    f.write(query4)
    f.write("\n\n")
    
    # Query 5
    f.write("-- 5. Repeat customer rate\n")
    f.write(query5)
    f.write("\n\n")
    
    # Query 6
    f.write("-- 6. Best day of week\n")
    f.write(query6)
    f.write("\n\n")
    
    # Query 7
    f.write("-- 7. Top customers by lifetime spend\n")
    f.write(query7)
    f.write("\n\n")
    
    # Query 8
    f.write("-- 8. RFM components (for customer segmentation)\n")
    f.write(query8)

print(f"   SQL queries saved to: {sql_queries_file}")

# 6. Print summary
print("\n" + "=" * 60)
print("SQL ANALYSIS COMPLETE!")
print("=" * 60)

# Calculate total revenue
total_revenue = pd.read_sql('SELECT ROUND(SUM(TotalPrice), 2) FROM transactions', conn).iloc[0, 0]
total_orders = pd.read_sql('SELECT COUNT(DISTINCT InvoiceNo) FROM transactions', conn).iloc[0, 0]
total_customers = pd.read_sql('SELECT COUNT(DISTINCT CustomerID) FROM transactions', conn).iloc[0, 0]

print(f"\nSummary Statistics:")
print(f"  Total revenue: £{total_revenue:,.2f}")
print(f"  Total orders: {total_orders:,}")
print(f"  Total customers: {total_customers:,}")
print(f"  Average order value: £{avg_order_value.iloc[0, 0]:,.2f}")

# Close connection
conn.close()
print("\nDatabase connection closed.")

print("\n" + "=" * 60)