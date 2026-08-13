"""
Step 3: Exploratory Data Analysis
Creates visualizations to understand the data patterns
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set up paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
CHARTS_DIR = PROJECT_ROOT / 'charts'

# Create charts directory if it doesn't exist
CHARTS_DIR.mkdir(exist_ok=True)

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

print("STEP 3: EXPLORATORY DATA ANALYSIS")

# 1. Load cleaned data
print("\n1. Loading cleaned data...")
df = pd.read_csv(DATA_DIR / 'cleaned_retail.csv', parse_dates=['InvoiceDate'])
print(f"   Loaded {len(df):,} transactions")
print(f"   Date range: {df['InvoiceDate'].min()} to {df['InvoiceDate'].max()}")

# 2. Figure 1: Monthly revenue trend
print("\n2. Creating Figure 1: Monthly Revenue Trend...")
monthly_revenue = df.groupby('InvoiceYearMonth')['TotalPrice'].sum().reset_index()
monthly_revenue = monthly_revenue.sort_values('InvoiceYearMonth')

fig1, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(monthly_revenue['InvoiceYearMonth'], monthly_revenue['TotalPrice'], 
         marker='o', linewidth=2, markersize=8, color='#2E86C1')
ax1.set_title('Monthly Revenue Trend (Dec 2010 - Dec 2011)', fontsize=16, fontweight='bold')
ax1.set_xlabel('Month', fontsize=12)
ax1.set_ylabel('Revenue (£)', fontsize=12)
ax1.tick_params(axis='x', rotation=45)
ax1.grid(True, alpha=0.3)

# Add value labels on top of each point
for i, (month, revenue) in enumerate(zip(monthly_revenue['InvoiceYearMonth'], monthly_revenue['TotalPrice'])):
    ax1.text(i, revenue + 20000, f'£{revenue:,.0f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
fig1.savefig(CHARTS_DIR / 'fig1_monthly_revenue.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"   Saved: {CHARTS_DIR / 'fig1_monthly_revenue.png'}")

# 3. Figure 2: Top 10 products by revenue
print("\n3. Creating Figure 2: Top 10 Products...")
top_products = df.groupby(['StockCode', 'Description'])['TotalPrice'].sum().reset_index()
top_products = top_products.sort_values('TotalPrice', ascending=False).head(10)

# Create shortened labels for readability
top_products['ShortDesc'] = top_products['Description'].apply(lambda x: x[:30] + '...' if len(x) > 30 else x)

fig2, ax2 = plt.subplots(figsize=(12, 7))
bars = ax2.barh(top_products['ShortDesc'], top_products['TotalPrice'], color='#28B463')
ax2.set_title('Top 10 Products by Revenue', fontsize=16, fontweight='bold')
ax2.set_xlabel('Revenue (£)', fontsize=12)
ax2.set_ylabel('Product', fontsize=12)
ax2.invert_yaxis()  # Highest at top

# Add value labels
for bar in bars:
    width = bar.get_width()
    ax2.text(width + 5000, bar.get_y() + bar.get_height()/2, 
             f'£{width:,.0f}', ha='left', va='center', fontsize=10)

plt.tight_layout()
fig2.savefig(CHARTS_DIR / 'fig2_top_products.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"   Saved: {CHARTS_DIR / 'fig2_top_products.png'}")

# Print top products for reference
print("   Top 5 products:")
for i, row in top_products.head(5).iterrows():
    print(f"     {row['StockCode']}: {row['Description'][:50]} - £{row['TotalPrice']:,.2f}")

# 4. Figure 3: Revenue by country (excluding UK)
print("\n4. Creating Figure 3: Revenue by Country (excluding UK)...")
country_revenue = df[df['Country'] != 'United Kingdom'].groupby('Country')['TotalPrice'].sum().reset_index()
country_revenue = country_revenue.sort_values('TotalPrice', ascending=False).head(10)

fig3, ax3 = plt.subplots(figsize=(12, 6))
bars = ax3.bar(country_revenue['Country'], country_revenue['TotalPrice'], color='#D35400')
ax3.set_title('Top 10 Countries by Revenue (excluding UK)', fontsize=16, fontweight='bold')
ax3.set_xlabel('Country', fontsize=12)
ax3.set_ylabel('Revenue (£)', fontsize=12)
ax3.tick_params(axis='x', rotation=45)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 5000,
             f'£{height:,.0f}', ha='center', va='bottom', fontsize=9)


plt.tight_layout()
fig3.savefig(CHARTS_DIR / 'fig3_country_revenue.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"   Saved: {CHARTS_DIR / 'fig3_country_revenue.png'}")

# 5. Figure 4: Distribution of order values (right-skewed)
print("\n5. Creating Figure 4: Order Value Distribution...")

# Calculate order totals
order_totals = df.groupby('InvoiceNo')['TotalPrice'].sum().reset_index()

fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(14, 5))

# Histogram with KDE
sns.histplot(order_totals['TotalPrice'], bins=50, kde=True, ax=ax4a, color='#8E44AD')
ax4a.set_title('Distribution of Order Values', fontsize=14, fontweight='bold')
ax4a.set_xlabel('Order Value (£)', fontsize=12)
ax4a.set_ylabel('Frequency', fontsize=12)
ax4a.axvline(order_totals['TotalPrice'].mean(), color='red', linestyle='--', label=f'Mean: £{order_totals["TotalPrice"].mean():.2f}')
ax4a.axvline(order_totals['TotalPrice'].median(), color='green', linestyle='--', label=f'Median: £{order_totals["TotalPrice"].median():.2f}')
ax4a.legend()

# Log-transformed for better view
sns.histplot(np.log1p(order_totals['TotalPrice']), bins=30, kde=True, ax=ax4b, color='#1ABC9C')
ax4b.set_title('Log-Transformed Order Values', fontsize=14, fontweight='bold')
ax4b.set_xlabel('log(Order Value + 1)', fontsize=12)
ax4b.set_ylabel('Frequency', fontsize=12)

plt.tight_layout()
fig4.savefig(CHARTS_DIR / 'fig4_order_value_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"   Saved: {CHARTS_DIR / 'fig4_order_value_distribution.png'}")
print(f"   Mean order value: £{order_totals['TotalPrice'].mean():.2f}")
print(f"   Median order value: £{order_totals['TotalPrice'].median():.2f}")

# 6. Figure 5: Hour of day / day of week patterns
print("\n6. Creating Figure 5: Hour and Day Patterns...")

# Hourly pattern
hourly_sales = df.groupby('InvoiceHour')['TotalPrice'].sum().reset_index()

# Day of week pattern (ordered)
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
daily_sales = df.groupby('InvoiceDayOfWeek')['TotalPrice'].sum().reset_index()
daily_sales['InvoiceDayOfWeek'] = pd.Categorical(daily_sales['InvoiceDayOfWeek'], categories=day_order, ordered=True)
daily_sales = daily_sales.sort_values('InvoiceDayOfWeek')

fig5, (ax5a, ax5b) = plt.subplots(1, 2, figsize=(14, 5))

# Hourly
ax5a.bar(hourly_sales['InvoiceHour'], hourly_sales['TotalPrice'], color='#2980B9', alpha=0.7)
ax5a.set_title('Revenue by Hour of Day', fontsize=14, fontweight='bold')
ax5a.set_xlabel('Hour of Day', fontsize=12)
ax5a.set_ylabel('Revenue (£)', fontsize=12)
ax5a.grid(True, alpha=0.3)

# Daily
ax5b.bar(daily_sales['InvoiceDayOfWeek'], daily_sales['TotalPrice'], color='#E67E22', alpha=0.7)
ax5b.set_title('Revenue by Day of Week', fontsize=14, fontweight='bold')
ax5b.set_xlabel('Day of Week', fontsize=12)
ax5b.set_ylabel('Revenue (£)', fontsize=12)
ax5b.tick_params(axis='x', rotation=45)
ax5b.grid(True, alpha=0.3)

plt.tight_layout()
fig5.savefig(CHARTS_DIR / 'fig5_hour_day_patterns.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"   Saved: {CHARTS_DIR / 'fig5_hour_day_patterns.png'}")

# Print best hour and day
best_hour = hourly_sales.loc[hourly_sales['TotalPrice'].idxmax()]
best_day = daily_sales.loc[daily_sales['TotalPrice'].idxmax()]
print(f"   Best hour: {best_hour['InvoiceHour']}:00 - £{best_hour['TotalPrice']:,.2f}")
print(f"   Best day: {best_day['InvoiceDayOfWeek']} - £{best_day['TotalPrice']:,.2f}")

# 7. Summary
print("\n" + "=" * 60)
print("EDA COMPLETE! All charts saved to charts/")
print("=" * 60)

print("\nGenerated Charts:")
for chart in sorted(CHARTS_DIR.glob('*.png')):
    print(f"  - {chart.name}")