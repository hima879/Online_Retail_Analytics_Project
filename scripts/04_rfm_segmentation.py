"""
Step 4: RFM Analysis & K-Means Segmentation
Customer segmentation using RFM framework and unsupervised ML
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from pathlib import Path

# Set up paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = PROJECT_ROOT / 'outputs'
CHARTS_DIR = PROJECT_ROOT / 'charts'

# Create directories if needed
OUTPUT_DIR.mkdir(exist_ok=True)
CHARTS_DIR.mkdir(exist_ok=True)

# Set plot style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

print("STEP 4: RFM ANALYSIS & K-MEANS SEGMENTATION")

# 1. Load cleaned data
print("\n1. Loading cleaned data...")
df = pd.read_csv(DATA_DIR / 'cleaned_retail.csv', parse_dates=['InvoiceDate'])
print(f"   Loaded {len(df):,} transactions")

# 2. Compute RFM metrics per customer
print("\n2. Computing RFM metrics...")

# Reference date: one day after max invoice date (to compute recency)
reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

# Group by CustomerID
rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
    'InvoiceNo': 'nunique',  # Frequency (distinct orders)
    'TotalPrice': 'sum'  # Monetary (total spend)
}).rename(columns={
    'InvoiceDate': 'Recency',
    'InvoiceNo': 'Frequency',
    'TotalPrice': 'Monetary'
}).reset_index()

print(f"   RFM computed for {len(rfm):,} customers")
print(f"   Recency range: {rfm['Recency'].min()} to {rfm['Recency'].max()} days")
print(f"   Frequency range: {rfm['Frequency'].min()} to {rfm['Frequency'].max()} orders")
print(f"   Monetary range: £{rfm['Monetary'].min():.2f} to £{rfm['Monetary'].max():,.2f}")

# Save raw RFM
rfm.to_csv(OUTPUT_DIR / 'rfm_raw.csv', index=False)
print(f"   Raw RFM saved to: {OUTPUT_DIR / 'rfm_raw.csv'}")

# 3. Log-transform Monetary (to handle skew)
print("\n3. Log-transforming Monetary (for clustering)...")
rfm['Monetary_log'] = np.log1p(rfm['Monetary'])

# Check skew before/after
print(f"   Monetary skew (raw): {rfm['Monetary'].skew():.2f}")
print(f"   Monetary skew (log): {rfm['Monetary_log'].skew():.2f}")

# 4. Standardize features (Recency, Frequency, Monetary_log)
print("\n4. Standardizing features...")

features = ['Recency', 'Frequency', 'Monetary_log']
X = rfm[features].copy()

# StandardScaler: mean=0, std=1
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled_df = pd.DataFrame(X_scaled, columns=features, index=rfm.index)

print(f"   Scaled features: mean ≈ 0, std ≈ 1")
print(f"   Recency scaled range: {X_scaled[:, 0].min():.2f} to {X_scaled[:, 0].max():.2f}")

# 5. Find optimal k using Elbow Method and Silhouette Score
print("\n5. Finding optimal number of clusters (k)...")

k_range = range(2, 11)
inertias = []
silhouette_scores = []

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    inertias.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X_scaled, labels))

# Print metrics
print("   k | Inertia | Silhouette")
print("   ---|---------|------------")
for k, inertia, sil in zip(k_range, inertias, silhouette_scores):
    print(f"   {k:2d} | {inertia:8,.0f} | {sil:.4f}")

# 6. Plot Elbow and Silhouette
print("\n6. Generating elbow & silhouette plots...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
# Elbow plot
ax1.plot(k_range, inertias, marker='o', linewidth=2, markersize=8, color='#2E86C1')
ax1.axvline(x=4, color='red', linestyle='--', alpha=0.5, label='k=4 (chosen)')
ax1.set_title('Elbow Method: Inertia vs k', fontsize=14, fontweight='bold')
ax1.set_xlabel('Number of Clusters (k)', fontsize=12)
ax1.set_ylabel('Inertia (Within-cluster variance)', fontsize=12)
ax1.grid(True, alpha=0.3)
ax1.legend()

# Silhouette plot
ax2.plot(k_range, silhouette_scores, marker='s', linewidth=2, markersize=8, color='#28B463')
ax2.axvline(x=4, color='red', linestyle='--', alpha=0.5, label='k=4 (chosen)')
ax2.set_title('Silhouette Score vs k', fontsize=14, fontweight='bold')
ax2.set_xlabel('Number of Clusters (k)', fontsize=12)
ax2.set_ylabel('Silhouette Score (higher = better)', fontsize=12)
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.tight_layout()
fig.savefig(CHARTS_DIR / 'fig6_elbow_silhouette.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"   Saved: {CHARTS_DIR / 'fig6_elbow_silhouette.png'}")

# 7. Apply K-Means with k=4
print("\n7. Applying K-Means with k=4...")

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
rfm['Cluster'] = kmeans.fit_predict(X_scaled)

# Rename clusters based on segment characteristics
# Lower cluster number usually means better customers, but let's map properly
# We'll analyze the cluster centers to name them

# Compute cluster centers in original scale (for interpretation)
cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
cluster_stats = pd.DataFrame(cluster_centers, columns=features)
cluster_stats['Cluster'] = range(4)

# Determine segment names
# Sort by Recency ascending (better) and Monetary descending (better)
# We want: Low Recency + High Monetary = Champions
#          Low Recency + Medium Monetary = Loyal
#          Medium Recency + Medium Monetary = At Risk
#          High Recency + Low Monetary = Hibernating

# Convert log(Monetary+1) back to actual Monetary in pounds
cluster_stats['Monetary'] = np.expm1(cluster_stats['Monetary_log'])

# Based on typical patterns in retail data, let's infer labels
# Let's analyze to label correctly
segment_labels = {}
for i in range(4):
    r = cluster_stats.loc[i, 'Recency']
    f = cluster_stats.loc[i, 'Frequency']
    m = cluster_stats.loc[i, 'Monetary']
    
    # Heuristic for labeling
    if r < 30 and f > 5 and m > 2000:
        label = 'Champions'
    elif r < 60 and f > 3 and m > 500:
        label = 'Loyal Customers'
    elif r < 120 and f > 1:
        label = 'At Risk'
    else:
        label = 'Hibernating'
    
    segment_labels[i] = label

# Apply labels
rfm['Segment'] = rfm['Cluster'].map(segment_labels)

print("   Cluster centers (original scale):")
print("   Cluster | Segment        | Recency | Frequency | Monetary")
print("   --------|----------------|---------|-----------|----------")
for i in range(4):
    r = cluster_stats.loc[i, 'Recency']
    f = cluster_stats.loc[i, 'Frequency']
    m = cluster_stats.loc[i, 'Monetary']
    label = segment_labels[i]
    print(f"      {i}    | {label:14} | {r:7.1f} | {f:9.1f} | £{m:,.0f}")

# 8. Segment sizes and summary statistics
print("\n8. Segment summary...")

segment_summary = rfm.groupby('Segment').agg({
    'CustomerID': 'count',
    'Recency': 'mean',
    'Frequency': 'mean',
    'Monetary': 'mean'
}).rename(columns={'CustomerID': 'Count'}).round(2)

segment_summary['Percentage'] = (segment_summary['Count'] / segment_summary['Count'].sum() * 100).round(1)
segment_summary = segment_summary.sort_values('Count', ascending=False)

print("\n   Segment            | Count | %    | Avg Recency | Avg Freq | Avg Monetary")
print("   -------------------|-------|------|-------------|----------|--------------")
for idx, row in segment_summary.iterrows():
    print(f"   {idx:18} | {row['Count']:5} | {row['Percentage']:4.1f}% | {row['Recency']:11.1f} | {row['Frequency']:8.1f} | £{row['Monetary']:,.0f}")

# Save segment summary
segment_summary.to_csv(OUTPUT_DIR / 'segment_summary.csv')
print(f"\n   Segment summary saved to: {OUTPUT_DIR / 'segment_summary.csv'}")

# Save full RFM with segments
rfm.to_csv(OUTPUT_DIR / 'rfm_segments.csv', index=False)
print(f"   Full RFM with segments saved to: {OUTPUT_DIR / 'rfm_segments.csv'}")

# 9. Visualize segments
print("\n9. Generating segment visualizations...")

# Figure 7: Pie chart - segment distribution
fig7, ax7 = plt.subplots(figsize=(10, 7))
segment_counts = rfm['Segment'].value_counts()
colors = ['#2E86C1', '#28B463', '#F39C12', '#E74C3C']  # Champions, Loyal, At Risk, Hibernating
wedges, texts, autotexts = ax7.pie(segment_counts, 
                                    labels=segment_counts.index,
                                    autopct='%1.1f%%',
                                    colors=colors[:len(segment_counts)],
                                    startangle=90,
                                    explode=[0.02]*len(segment_counts))
ax7.set_title('Customer Segment Distribution', fontsize=16, fontweight='bold')
plt.tight_layout()
fig7.savefig(CHARTS_DIR / 'fig7_segment_pie.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"   Saved: {CHARTS_DIR / 'fig7_segment_pie.png'}")

# Figure 8: Recency vs Monetary (log scale) by segment
fig8, ax8 = plt.subplots(figsize=(12, 7))

# Color map
color_map = {
    'Champions': '#2E86C1',
    'Loyal Customers': '#28B463',
    'At Risk': '#F39C12',
    'Hibernating': '#E74C3C'
}

for segment in rfm['Segment'].unique():
    subset = rfm[rfm['Segment'] == segment]
    ax8.scatter(subset['Recency'], np.log1p(subset['Monetary']),
                label=segment, alpha=0.6, s=30,
                color=color_map.get(segment, '#7F8C8D'))

ax8.set_title('Recency vs Monetary Value (log scale) by Segment', fontsize=16, fontweight='bold')
ax8.set_xlabel('Recency (days since last purchase)', fontsize=12)
ax8.set_ylabel('log(Monetary + 1)', fontsize=12)
ax8.legend()
ax8.grid(True, alpha=0.3)

plt.tight_layout()
fig8.savefig(CHARTS_DIR / 'fig8_recency_vs_monetary.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"   Saved: {CHARTS_DIR / 'fig8_recency_vs_monetary.png'}")

# 10. Business recommendations
print("SEGMENTATION COMPLETE!")

print("\n📊 Business Recommendations by Segment:")
print("-" * 60)

for segment in ['Champions', 'Loyal Customers', 'At Risk', 'Hibernating']:
    if segment in segment_summary.index:
        row = segment_summary.loc[segment]
        count = row['Count']
        pct = row['Percentage']
        avg_monetary = row['Monetary']

        if segment == 'Champions':
            print(f"🔹 {segment} ({count} customers, {pct:.1f}%):")
            print(f"   - VIP treatment, early access, loyalty rewards")
            print(f"   - Avg spend: £{avg_monetary:,.0f} - PROTECT THIS SEGMENT")
        elif segment == 'Loyal Customers':
            print(f"🔹 {segment} ({count} customers, {pct:.1f}%):")
            print(f"   - Upsell & cross-sell campaigns")
            print(f"   - Avg spend: £{avg_monetary:,.0f} - GROW THIS SEGMENT")
        elif segment == 'At Risk':
            print(f"🔹 {segment} ({count} customers, {pct:.1f}%):")
            print(f"   - Win-back email campaigns (urgent!)")
            print(f"   - Avg spend: £{avg_monetary:,.0f} - RECOVER THIS SEGMENT")
        elif segment == 'Hibernating':
            print(f"🔹 {segment} ({count} customers, {pct:.1f}%):")
            print(f"   - Low-cost reactivation offers only")
            print(f"   - Avg spend: £{avg_monetary:,.0f} - LOW PRIORITY")
        print()

print("=" * 60)