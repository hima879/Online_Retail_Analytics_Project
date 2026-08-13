"""
Step 6: Interactive Streamlit Dashboard (Enhanced UI)
Live dashboard for exploring retail analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add project root to path so we can import from scripts if needed
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = PROJECT_ROOT / 'outputs'

# Page configuration MUST be the first Streamlit command
st.set_page_config(
    page_title="Online Retail Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# Theme constants — used for both custom CSS and Plotly charts
# -------------------------------------------------------------------
PRIMARY = "#6C5CE7"      # violet
ACCENT = "#00CEC9"       # teal
WARN = "#FDCB6E"         # amber
DANGER = "#FF7675"       # coral
SUCCESS = "#55EFC4"      # mint
BG_CARD = "#FFFFFF"
TEXT_DARK = "#2D3436"
MUTED = "#636E72"

SEGMENT_COLORS = {
    'Champions': PRIMARY,
    'Loyal Customers': ACCENT,
    'At Risk': WARN,
    'Hibernating': DANGER
}

PLOTLY_TEMPLATE = "plotly_white"
CHART_COLORWAY = [PRIMARY, ACCENT, WARN, DANGER, SUCCESS, "#0984E3", "#E17055"]

# -------------------------------------------------------------------
# Custom CSS — fonts, spacing, card styling, header banner
# -------------------------------------------------------------------
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    /* Hide default Streamlit chrome for a cleaner look */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }}

    /* Hero banner */
    .hero-banner {{
        background: linear-gradient(120deg, {PRIMARY} 0%, {ACCENT} 100%);
        padding: 2rem 2.2rem;
        border-radius: 18px;
        margin-bottom: 1.6rem;
        box-shadow: 0 10px 30px rgba(108, 92, 231, 0.25);
    }}
    .hero-title {{
        font-family: 'Poppins', sans-serif;
        color: white;
        font-size: 2.1rem;
        font-weight: 700;
        margin: 0;
    }}
    .hero-subtitle {{
        color: rgba(255,255,255,0.9);
        font-size: 0.95rem;
        margin-top: 0.3rem;
        font-weight: 400;
    }}

    /* KPI cards */
    div[data-testid="stMetric"] {{
        background: {BG_CARD};
        border: 1px solid #EEF0F3;
        border-radius: 16px;
        padding: 1.1rem 1.2rem 0.9rem 1.2rem;
        box-shadow: 0 4px 14px rgba(45, 52, 54, 0.06);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 22px rgba(108, 92, 231, 0.18);
    }}
    div[data-testid="stMetricLabel"] {{
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: {MUTED};
    }}
    div[data-testid="stMetricValue"] {{
        font-family: 'Poppins', sans-serif;
        color: {TEXT_DARK};
        font-weight: 700;
    }}

    /* Section headers */
    .section-title {{
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1.15rem;
        color: {TEXT_DARK};
        margin-bottom: 0.2rem;
        border-left: 5px solid {PRIMARY};
        padding-left: 0.6rem;
    }}

    /* Chart container cards */
    .chart-card {{
        background: {BG_CARD};
        border-radius: 16px;
        padding: 0.8rem 0.6rem 0.2rem 0.6rem;
        border: 1px solid #EEF0F3;
        box-shadow: 0 4px 14px rgba(45, 52, 54, 0.05);
        margin-bottom: 1rem;
    }}

    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #F7F6FF 0%, #FFFFFF 100%);
        border-right: 1px solid #EEF0F3;
    }}
    section[data-testid="stSidebar"] h1 {{
        font-family: 'Poppins', sans-serif;
        color: {PRIMARY};
        font-weight: 700;
    }}

    /* Divider */
    hr {{
        border: none;
        border-top: 1px solid #EEF0F3;
        margin: 1.4rem 0;
    }}

    .footer-note {{
        text-align: center;
        color: {MUTED};
        font-size: 0.85rem;
        padding-top: 1rem;
    }}
</style>
""", unsafe_allow_html=True)


def style_fig(fig, title=None):
    """Apply a consistent, polished look to every Plotly chart."""
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        colorway=CHART_COLORWAY,
        font=dict(family="Inter, sans-serif", size=13, color=TEXT_DARK),
        title=dict(text=title, font=dict(family="Poppins, sans-serif", size=16, color=TEXT_DARK)) if title else None,
        margin=dict(l=10, r=10, t=50 if title else 20, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter, sans-serif"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#F0F1F5", zeroline=False)
    return fig


# -------------------------------------------------------------------
# Load data with caching (for performance)
# -------------------------------------------------------------------
@st.cache_data
def load_data():
    """Load cleaned transactions and RFM segment data."""
    df = pd.read_csv(DATA_DIR / 'cleaned_retail.csv', parse_dates=['InvoiceDate'])
    rfm = pd.read_csv(OUTPUT_DIR / 'rfm_segments.csv')
    return df, rfm

@st.cache_data
def load_summary_stats(df):
    """Compute summary KPIs from the full dataset."""
    total_revenue = df['TotalPrice'].sum()
    total_orders = df['InvoiceNo'].nunique()
    total_customers = df['CustomerID'].nunique()
    avg_order_value = total_revenue / total_orders
    return total_revenue, total_orders, total_customers, avg_order_value

# Load data
try:
    df, rfm = load_data()
    total_revenue, total_orders, total_customers, avg_order_value = load_summary_stats(df)
except FileNotFoundError as e:
    st.error(f"Error loading data: {e}. Please make sure you've run all pipeline scripts first.")
    st.stop()

# -------------------------------------------------------------------
# Sidebar filters
# -------------------------------------------------------------------
st.sidebar.title("🔍 Filters")
st.sidebar.caption("Refine the dashboard by country and date range.")
st.sidebar.markdown("---")

# Country filter (sorted, with 'United Kingdom' as default)
countries = sorted(df['Country'].unique())
default_countries = ['United Kingdom'] if 'United Kingdom' in countries else [countries[0]]
selected_countries = st.sidebar.multiselect(
    "🌍 Select Country",
    options=countries,
    default=default_countries
)

# Date range filter
min_date = df['InvoiceDate'].min().date()
max_date = df['InvoiceDate'].max().date()
date_range = st.sidebar.date_input(
    "📅 Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Full dataset: **{total_orders:,}** orders · **{total_customers:,}** customers")

# Apply filters
filtered = df.copy()
if selected_countries:
    filtered = filtered[filtered['Country'].isin(selected_countries)]
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[(filtered['InvoiceDate'].dt.date >= start_date) &
                        (filtered['InvoiceDate'].dt.date <= end_date)]

# -------------------------------------------------------------------
# Hero header
# -------------------------------------------------------------------
st.markdown(f"""
<div class="hero-banner">
    <p class="hero-title">📊 Online Retail Analytics Dashboard</p>
    <p class="hero-subtitle">End-to-end view of revenue, customers, and buying patterns — filter from the sidebar to explore.</p>
</div>
""", unsafe_allow_html=True)

# KPI row
col1, col2, col3, col4 = st.columns(4)

with col1:
    revenue = filtered['TotalPrice'].sum()
    st.metric("💰 Total Revenue", f"£{revenue:,.2f}",
              delta=f"{(revenue / total_revenue * 100 - 100):.1f}% of total" if total_revenue > 0 else None)

with col2:
    orders = filtered['InvoiceNo'].nunique()
    st.metric("📦 Total Orders", f"{orders:,}",
              delta=f"{orders / total_orders * 100 - 100:.1f}%" if total_orders > 0 else None)

with col3:
    customers = filtered['CustomerID'].nunique()
    st.metric("👥 Unique Customers", f"{customers:,}",
              delta=f"{customers / total_customers * 100 - 100:.1f}%" if total_customers > 0 else None)

with col4:
    aov = revenue / orders if orders > 0 else 0
    st.metric("📊 Avg Order Value", f"£{aov:,.2f}",
              delta=f"£{aov - avg_order_value:,.2f}" if avg_order_value > 0 else None)

st.markdown("<hr>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Organize the rest into tabs for a cleaner, less cluttered feel
# -------------------------------------------------------------------
tab_trends, tab_segments, tab_patterns, tab_data = st.tabs(
    ["📈 Trends & Products", "👤 Segments & Geography", "📅 Time Patterns", "📋 Raw Data"]
)

# ---------------- Tab 1: Trends & Products ----------------
with tab_trends:
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<p class="section-title">Monthly Revenue Trend</p>', unsafe_allow_html=True)
        monthly = filtered.groupby('InvoiceYearMonth')['TotalPrice'].sum().reset_index()
        monthly = monthly.sort_values('InvoiceYearMonth')
        if not monthly.empty:
            fig = px.area(monthly, x='InvoiceYearMonth', y='TotalPrice',
                          labels={'InvoiceYearMonth': 'Month', 'TotalPrice': 'Revenue (£)'})
            fig.update_traces(line=dict(color=PRIMARY, width=3), fillcolor="rgba(108, 92, 231, 0.15)")
            fig = style_fig(fig)
            fig.update_layout(xaxis_tickangle=-45)
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No data for selected filters.")

    with col_right:
        st.markdown('<p class="section-title">Top 10 Products</p>', unsafe_allow_html=True)
        top_products = filtered.groupby(['StockCode', 'Description'])['TotalPrice'].sum().reset_index()
        top_products = top_products.sort_values('TotalPrice', ascending=False).head(10)
        if not top_products.empty:
            top_products['Label'] = top_products['Description'].apply(lambda x: x[:30] + '...' if len(x) > 30 else x)
            fig = px.bar(top_products, x='TotalPrice', y='Label', orientation='h',
                         labels={'TotalPrice': 'Revenue (£)', 'Label': 'Product'},
                         color='TotalPrice', color_continuous_scale=[ACCENT, PRIMARY])
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
            fig = style_fig(fig)
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No data for selected filters.")

# ---------------- Tab 2: Segments & Geography ----------------
with tab_segments:
    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.markdown('<p class="section-title">Revenue by Country (Top 10)</p>', unsafe_allow_html=True)
        country_rev = filtered.groupby('Country')['TotalPrice'].sum().reset_index()
        country_rev = country_rev.sort_values('TotalPrice', ascending=False).head(10)
        if not country_rev.empty:
            fig = px.bar(country_rev, x='Country', y='TotalPrice',
                         labels={'TotalPrice': 'Revenue (£)', 'Country': 'Country'},
                         color='TotalPrice', color_continuous_scale=[ACCENT, PRIMARY])
            fig.update_layout(coloraxis_showscale=False)
            fig = style_fig(fig)
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No data for selected filters.")

    with col_right2:
        st.markdown('<p class="section-title">Customer Segments</p>', unsafe_allow_html=True)
        filtered_customers = filtered['CustomerID'].unique()
        rfm_filtered = rfm[rfm['CustomerID'].isin(filtered_customers)]
        if not rfm_filtered.empty:
            segment_counts = rfm_filtered['Segment'].value_counts().reset_index()
            segment_counts.columns = ['Segment', 'Count']
            fig = px.pie(segment_counts, values='Count', names='Segment',
                         color='Segment', hole=0.45,
                         color_discrete_map=SEGMENT_COLORS)
            fig.update_traces(textinfo='percent+label', textfont_size=12)
            fig = style_fig(fig)
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption("🟣 Champions &nbsp;|&nbsp; 🟢 Loyal &nbsp;|&nbsp; 🟡 At Risk &nbsp;|&nbsp; 🔴 Hibernating")
        else:
            st.info("No segment data for selected filters.")

# ---------------- Tab 3: Time Patterns ----------------
with tab_patterns:
    col_hour, col_day = st.columns(2)

    with col_hour:
        st.markdown('<p class="section-title">Revenue by Hour of Day</p>', unsafe_allow_html=True)
        hourly = filtered.groupby('InvoiceHour')['TotalPrice'].sum().reset_index()
        if not hourly.empty:
            fig = px.bar(hourly, x='InvoiceHour', y='TotalPrice',
                         labels={'InvoiceHour': 'Hour', 'TotalPrice': 'Revenue (£)'})
            fig.update_traces(marker_color=ACCENT)
            fig = style_fig(fig)
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No data for selected filters.")

    with col_day:
        st.markdown('<p class="section-title">Revenue by Day of Week</p>', unsafe_allow_html=True)
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily = filtered.groupby('InvoiceDayOfWeek')['TotalPrice'].sum().reset_index()
        if not daily.empty:
            daily['InvoiceDayOfWeek'] = pd.Categorical(daily['InvoiceDayOfWeek'], categories=day_order, ordered=True)
            daily = daily.sort_values('InvoiceDayOfWeek')
            fig = px.bar(daily, x='InvoiceDayOfWeek', y='TotalPrice',
                         labels={'InvoiceDayOfWeek': 'Day', 'TotalPrice': 'Revenue (£)'})
            fig.update_traces(marker_color=PRIMARY)
            fig = style_fig(fig)
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No data for selected filters.")

# ---------------- Tab 4: Raw Data ----------------
with tab_data:
    st.markdown('<p class="section-title">Filtered Transaction Data</p>', unsafe_allow_html=True)
    st.dataframe(filtered.head(100), use_container_width=True)
    st.caption(f"Showing first 100 rows of {len(filtered):,} filtered transactions.")

# -------------------------------------------------------------------
# Footer
# -------------------------------------------------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    '<p class="footer-note">Built with Streamlit • Data from UCI Online Retail Dataset • End-to-end analytics pipeline</p>',
    unsafe_allow_html=True
) 