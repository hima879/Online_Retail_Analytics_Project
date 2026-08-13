"""
Step 1: Data Cleaning Pipeline
Handles missing values, cancellations, duplicates, and prepares data for analysis
File: scripts/01_data_cleaning.py
"""
import numpy as np
try:
    import pandas as pd
except ImportError as exc:
    raise ImportError("pandas is required for data cleaning; install it with `pip install pandas`") from exc
import os
import sys
from pathlib import Path

# Set up paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = PROJECT_ROOT / 'outputs'

# Creat outputs directory if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok = True)

print("Step 1: Data Cleaning")

# 1. Load raw data
print("\n1. Loading raw data...")

# Try Excel first (more reliable)
raw_path = DATA_DIR / 'Online Retail.xlsx'

# Check if file exists, try different names
if not raw_path.exists():
    # Try alternative names - prioritize Excel files
    alternatives = [
        DATA_DIR / 'Online%20Retail.xlsx',
        DATA_DIR / 'online_retail.xlsx',
        DATA_DIR / 'online_retail_raw.xlsx',
        DATA_DIR / 'Online%20Retail.csv',
        DATA_DIR / 'Online Retail.csv',
        DATA_DIR / 'online_retail.csv',
        DATA_DIR / 'OnlineRetail.csv',
        DATA_DIR / 'online_retail_raw.csv'
    ]
    for alt in alternatives:
        if alt.exists():
            raw_path = alt
            break
    else:
        print(f"ERROR: No data file found in {DATA_DIR}")
        print("Please download the dataset from:")
        print("https://archive.ics.uci.edu/ml/datasets/Online+Retail")
        sys.exit(1)

print(f"    Loading from: {raw_path}")

# Load based on file extension with error handling
try:
    if raw_path.suffix in ['.csv']:
        # Try to read CSV with error handling
        df = pd.read_csv(raw_path, encoding='latin1', on_bad_lines='skip')
    else:
        # Read Excel file
        df = pd.read_excel(raw_path, sheet_name='Online Retail')
except Exception as e:
    print(f"   Error loading file: {e}")
    print("   Trying alternative method...")
    
    # Fallback: try reading with different parameters
    if raw_path.suffix in ['.csv']:
        df = pd.read_csv(raw_path, encoding='latin1', engine='python', on_bad_lines='skip')
    else:
        # Try reading Excel without specifying sheet
        df = pd.read_excel(raw_path)

print(f"   Initial shape: {df.shape}")
print(f"   Columns: {df.columns.tolist()}")

# Load based on file extension
if raw_path.suffix == '.csv':
    df = pd.read_csv(raw_path, encoding='latin1')
else:
    df = pd.read_excel(raw_path, sheet_name='Online Retail')

print(f"   Initial shape: {df.shape}")
print(f"   Columns: {df.columns.tolist()}")

# Convert InvoiceDate to datetime
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])


# 2. Handle CustomerID issues
print("\nStep 2: Handling CustomerID....")
print(f"   Missing CustomerID count: {df['CustomerID'].isnull().sum()}")

# Replace 0 with NaN (as per project guide - this export encodes missing as 0)
df['CustomerID'] = df['CustomerID'].replace(0, np.nan)

# Drop rows with missing CustomerID (needed for RFM and segmentation)
missing_customerid = df['CustomerID'].isnull().sum()
df = df.dropna(subset=['CustomerID'])
print(f"   Dropped {missing_customerid} rows with missing CustomerID")

# 3. Split out cancellations
print("\nStep 3: Handling cancellations....")

df['InvoiceNo'] = df['InvoiceNo'].astype(str)
is_cancellation = df['InvoiceNo'].str.startswith('C')
cancellations = df[is_cancellation].copy()
df_non_cancelled = df[~is_cancellation].copy()

print(f"   Cancellations found: {len(cancellations)}")
print(f"   Non-cancelled transactions: {len(df_non_cancelled)}")

# Save cancellations separately potential returns analysis later
cancellations_path = OUTPUT_DIR / 'cancellations_only.csv'
cancellations.to_csv(cancellations_path, index=False)
print(f"   Cancellations saved to: {cancellations_path}")

# 4. Remove accounting adjustments (invoices with 'A')
print("\nStep 4: Removing accounting adjustments...")

is_accounting = df_non_cancelled['InvoiceNo'].str.startswith('A')
accounting_adj = df_non_cancelled[is_accounting]
df_non_accounting = df_non_cancelled[~is_accounting].copy()

print(f"   Accounting adjustments removed: {len(accounting_adj)}")

# 5. Remove non-product stock codes
print("\nStep 5: Removing non-product stock codes...")

# Common non-product codes (these are typically for postage, bank charges, etc.)
non_product_codes = ['POSTAGE', 'BANK CHARGES', 'DOT', 'M', 'CRUK', 'AMAZONFEE']
df_non_product_removed = df_non_accounting[
    ~df_non_accounting['StockCode'].astype(str).isin(non_product_codes)
].copy()

print(f"   Rows removed: {len(df_non_accounting) - len(df_non_product_removed)}")

# 6. Remove invalid quantities and prices
print("\nStep 6: Removing invalid quantities and prices...")

before = len(df_non_product_removed)
df_cleaned = df_non_product_removed[
    (df_non_product_removed['Quantity'] > 0) & 
    (df_non_product_removed['UnitPrice'] > 0)
].copy()

removed = before - len(df_cleaned)
print(f"   Removed {removed} rows with zero/negative Quantity or UnitPrice")

# 7. Handle missing descriptions
print("\nStep 7: Handling missing descriptions...")

# For rows with missing description, fill with the most common description for that StockCode
missing_desc_mask = df_cleaned['Description'].isnull()
missing_desc_count = missing_desc_mask.sum()
print(f"   Missing descriptions: {missing_desc_count}")

if missing_desc_count > 0:
    # Create a mapping of stock code to most common description
    desc_mapping = (
        df_cleaned[~df_cleaned['Description'].isnull()]
        .groupby('StockCode')['Description']
        .agg(lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown')
        .to_dict()
    )
    
    # Fill missing descriptions
    df_cleaned['Description'] = df_cleaned.apply(
        lambda row: desc_mapping.get(row['StockCode'], 'Unknown') 
        if pd.isnull(row['Description']) 
        else row['Description'],
        axis=1
    )
    
    # Check if any remain
    remaining_missing = df_cleaned['Description'].isnull().sum()
    print(f"   Remaining missing descriptions after fill: {remaining_missing}")

# 8. Remove duplicates
print("\nStep 8: Removing duplicates...")

before = len(df_cleaned)
df_cleaned = df_cleaned.drop_duplicates()
removed = before - len(df_cleaned)
print(f"   Removed {removed} duplicate rows")

# 9. Create derived columns for downstream analysis
print("\nStep 9: Creating derived columns...")
# TotalPrice (quantity * unit price)
df_cleaned['TotalPrice'] = df_cleaned['Quantity'] * df_cleaned['UnitPrice']

# InvoiceYearMonth for time-based aggregations
df_cleaned['InvoiceYearMonth'] = df_cleaned['InvoiceDate'].dt.to_period('M').astype(str)

# Invoice date components
df_cleaned['InvoiceDayOfWeek'] = df_cleaned['InvoiceDate'].dt.day_name()
df_cleaned['InvoiceHour'] = df_cleaned['InvoiceDate'].dt.hour

# 10. Summary statistics and final output
print("\nSetp 10: Final summary...")

print(f"\n   Final shape: {df_cleaned.shape}")
print(f"   Date range: {df_cleaned['InvoiceDate'].min()} to {df_cleaned['InvoiceDate'].max()}")
print(f"   Unique customers: {df_cleaned['CustomerID'].nunique()}")
print(f"   Unique products: {df_cleaned['StockCode'].nunique()}")
print(f"   Unique countries: {df_cleaned['Country'].nunique()}")

# Save cleaned data
cleaned_path = DATA_DIR / 'cleaned_retail.csv'
df_cleaned.to_csv(cleaned_path, index=False)
print(f"\n   Cleaned data saved to: {cleaned_path}")

print("\n" + "=" * 60)
print("DATA CLEANING COMPLETE!")
print("=" * 60)

# Display the first few rows
print("\nPreview of cleaned data:")
print(df_cleaned.head())

# Print memory usage
print(f"\nMemory usage: {df_cleaned.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

print("""CLEANED DATA AFTERWARDS

InvoiceNo  StockCode  Description                          Quantity  InvoiceDate           UnitPrice  CustomerID  Country           TotalPrice  InvoiceYearMonth  InvoiceDayOfWeek  InvoiceHour
536365     85123A     WHITE HANGING HEART T-LIGHT HOLDER  6         2010-12-01 08:26:00  2.55       17850.0     United Kingdom    15.30       2010-12           Wednesday          8
536365     71053      WHITE METAL LANTERN                 6         2010-12-01 08:26:00  3.39       17850.0     United Kingdom    20.34       2010-12           Wednesday          8
536365     84406B     CREAM CUPID HEARTS COAT HANGER      8         2010-12-01 08:26:00  2.75       17850.0     United Kingdom    22.00       2010-12           Wednesday          8
536365     84029G     KNITTED UNION FLAG HOT WATER BOTTLE 6         2010-12-01 08:26:00  3.39       17850.0     United Kingdom    20.34       2010-12           Wednesday          8
536365     84029E     RED WOOLLY HOTTIE WHITE HEART.      6         2010-12-01 08:26:00  3.39       17850.0     United Kingdom    20.34       2010-12           Wednesday          8
536365     22752      SET 7 BABUSHKA NESTING BOXES        2         2010-12-01 08:26:00  7.65       17850.0     United Kingdom    15.30       2010-12           Wednesday          8
536365     21730      GLASS STAR FROSTED T-LIGHT HOLDER   6         2010-12-01 08:26:00  4.25       17850.0     United Kingdom    25.50       2010-12           Wednesday          8
536366     22633      HAND WARMER UNION JACK              6         2010-12-01 08:28:00  1.85       17850.0     United Kingdom    11.10       2010-12           Wednesday          8
536366     22632      HAND WARMER RED POLKA DOT           6         2010-12-01 08:28:00  1.85       17850.0     United Kingdom    11.10       2010-12           Wednesday          8
536367     84879      ASSORTED COLOUR BIRD ORNAMENT      32         2010-12-01 08:34:00  1.69       13047.0     United Kingdom    54.08       2010-12           Wednesday          8
""")