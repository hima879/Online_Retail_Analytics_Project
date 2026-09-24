"""
Step 6: Interactive Streamlit Dashboard — Dark Theme (Clean UI)
Live dashboard for exploring retail analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = PROJECT_ROOT / 'outputs'

st.set_page_config(
    page_title="Online Retail Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# Dark theme palette
# -------------------------------------------------------------------
BG = "#0D1117"            # app background
BG_SIDEBAR = "#11151C"    # sidebar background
CARD = "#161B22"          # card surface
BORDER = "#262D38"        # card borders
TEXT = "#E6E9F0"          # primary text
MUTED = "#8B93A7"         # secondary text

PRIMARY = "#818CF8"       # indigo
ACCENT = "#2DD4BF"        # teal
WARN = "#FBBF24"          # amber
DANGER = "#F87171"        # red
SUCCESS = "#34D399"       # green

SEGMENT_COLORS = {
    'Champions': PRIMARY,
    'Loyal Customers': ACCENT,
    'At Risk': WARN,
    'Hibernating': DANGER
}
CHART_COLORWAY = [PRIMARY, ACCENT, WARN, DANGER, SUCCESS, "#60A5FA", "#FB923C"]

# -------------------------------------------------------------------
# Custom CSS — dark theme, cards, spacing
# -------------------------------------------------------------------
st.markdown(f"""
<style>
    html, body, [class*="css"], .stApp {{
        background-color: {BG};
        color: {TEXT};
        font-family: 'Segoe UI', system-ui, sans-serif;
    }}

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header {{visibility: hidden;}}
    .block-container {{padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px;}}

    /* ---- Page header ---- */
    .page-header {{
        margin-bottom: 1.4rem;
    }}
    .page-title {{
        font-size: 1.7rem;
        font-weight: 700;
        color: {TEXT};
        margin: 0;
    }}
    .page-subtitle {{
        color: {MUTED};
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }}

    /* ---- KPI cards ---- */
    div[data-testid="stMetric"] {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 1rem 1.1rem 0.8rem 1.1rem;
    }}
    div[data-testid="stMetricLabel"] {{
        color: {MUTED};
        font-weight: 600;
        font-size: 0.85rem;
    }}
    div[data-testid="stMetricValue"] {{
        color: {TEXT};
        font-weight: 700;
        font-size: 1.5rem;
    }}
    div[data-testid="stMetricDelta"] svg {{display: none;}}

    /* ---- Section titles ---- */
    .section-title {{
        font-size: 1.05rem;
        font-weight: 600;
        color: {TEXT};
        margin-bottom: 0.1rem;
    }}
    .section-sub {{
        color: {MUTED};
        font-size: 0.85rem;
        margin-bottom: 0.6rem;
    }}

    /* ---- Chart container cards ---- */
    .chart-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 0.9rem 0.7rem 0.2rem 0.7rem;
        margin-bottom: 1rem;
    }}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {{
        background-color: {BG_SIDEBAR};
        border-right: 1px solid {BORDER};
    }}
    section[data-testid="stSidebar"] * {{color: {TEXT};}}
    section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {{
        color: {MUTED} !important;
    }}
    section[data-testid="stSidebar"] hr {{border-color: {BORDER};}}

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background-color: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {CARD};
        border: 1px solid {BORDER};
        border-radius: 8px 8px 0 0;
        color: {MUTED};
        padding: 0.5rem 1rem;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {CARD};
        border-bottom: 2px solid {PRIMARY};
        color: {TEXT};
    }}
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{display: none;}}

    /* ---- Dataframe / misc ---- */
    div[data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 12px;
        overflow: hidden;
    }}
    .stInfo {{
        background-color: {CARD};
        border: 1px solid {BORDER};
        color: {MUTED};
    }}

    hr {{border: none; border-top: 1px solid {BORDER}; margin: 1.2rem 0;}}

    .footer-note {{
        text-align: center;
        color: {MUTED};
        font-size: 0.85rem;
    }}
</style>
""", unsafe_allow_html=True)


def style_fig(fig, title=None):
    """Apply a consistent dark look to every Plotly chart."""
    fig.update_layout(
        template="plotly_dark",
        colorway=CHART_COLORWAY,
        font=dict(family="Segoe UI, sans-serif", size=13, color=TEXT),
        title=None,
        margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5,
                    bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED)),
        hoverlabel=dict(bgcolor="#1F2530", font_size=12, font_family="Segoe UI, sans-serif",
                        font_color=TEXT),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, color=MUTED)
    fig.update_yaxes(showgrid=True, gridcolor="#222836", zeroline=False, color=MUTED)
    return fig


# -------------------------------------------------------------------
# Load data
# -------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_DIR / 'cleaned_retail.csv', parse_dates=['InvoiceDate'])
    rfm = pd.read_csv(OUTPUT_DIR / 'rfm_segments.csv')
    return df, rfm

@st.cache_data
def load_summary_stats(df):
    total_revenue = df['TotalPrice'].sum()
    total_orders = df['InvoiceNo'].nunique()
    total_customers = df['CustomerID'].nunique()
    avg_order_value = total_revenue / total_orders
    return total_revenue, total_orders, total_customers, avg_order_value

try:
    df, rfm = load_data()
    total_revenue, total_orders, total_customers, avg_order_value = load_summary_stats(df)
except FileNotFoundError as e:
    st.error(f"Error loading data: {e}. Please make sure you've run all pipeline scripts first.")
    st.stop()

# -------------------------------------------------------------------
# Sidebar — filters + quick guide
# -------------------------------------------------------------------
st.sidebar.title("Filters")

with st.sidebar.expander("❓ How to use this dashboard", expanded=False):
    st.markdown(
        "1. **Pick countries** and a **date range** below.\n"
        "2. KPIs at the top update instantly.\n"
        "3. Switch tabs to explore trends, segments and patterns."
    )

st.sidebar.markdown("---")

countries = sorted(df['Country'].unique())
default_countries = ['United Kingdom'] if 'United Kingdom' in countries else [countries[0]]
selected_countries = st.sidebar.multiselect(
    "🌍 Country",
    options=countries,
    default=default_countries
)

min_date = df['InvoiceDate'].min().date()
max_date = df['InvoiceDate'].max().date()
date_range = st.sidebar.date_input(
    "📅 Date range",
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
# Header
# -------------------------------------------------------------------
st.markdown(f"""
<div class="page-header">
    <p class="page-title">📊 Online Retail Dashboard</p>
    <p class="page-subtitle">Revenue, customers and buying patterns — adjust filters in the sidebar to explore.</p>
</div>
""", unsafe_allow_html=True)

# KPI row — deltas show share of total (neutral color)
col1, col2, col3, col4 = st.columns(4)

with col1:
    revenue = filtered['TotalPrice'].sum()
    share = f"{revenue / total_revenue * 100:.1f}% of total" if total_revenue > 0 else "—"
    st.metric("💰 Total Revenue", f"£{revenue:,.0f}", delta=share, delta_color="off")

with col2:
    orders = filtered['InvoiceNo'].nunique()
    share = f"{orders / total_orders * 100:.1f}% of total" if total_orders > 0 else "—"
    st.metric("📦 Orders", f"{orders:,}", delta=share, delta_color="off")

with col3:
    customers = filtered['CustomerID'].nunique()
    share = f"{customers / total_customers * 100:.1f}% of total" if total_customers > 0 else "—"
    st.metric("👥 Customers", f"{customers:,}", delta=share, delta_color="off")

with col4:
    aov = revenue / orders if orders > 0 else 0
    st.metric("📊 Avg Order Value", f"£{aov:,.2f}",
              delta=f"vs £{avg_order_value:,.2f} overall", delta_color="off")

st.markdown("<hr>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Tabs
# -------------------------------------------------------------------
tab_trends, tab_segments, tab_patterns, tab_data = st.tabs(
    ["📈 Trends & Products", "👤 Segments & Geography", "📅 Time Patterns", "📋 Data"]
)

# ---------------- Tab 1: Trends & Products ----------------
with tab_trends:
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<p class="section-title">Monthly Revenue</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">How total revenue changes month by month.</p>', unsafe_allow_html=True)
        monthly = filtered.groupby('InvoiceYearMonth')['TotalPrice'].sum().reset_index()
        monthly = monthly.sort_values('InvoiceYearMonth')
        if not monthly.empty:
            fig = px.area(monthly, x='InvoiceYearMonth', y='TotalPrice',
                          labels={'InvoiceYearMonth': 'Month', 'TotalPrice': 'Revenue (£)'})
            fig.update_traces(line=dict(color=PRIMARY, width=3), fillcolor="rgba(129,140,248,0.15)")
            fig = style_fig(fig)
            fig.update_layout(xaxis_tickangle=-45)
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No data for the selected filters.")

    with col_right:
        st.markdown('<p class="section-title">Top 10 Products</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">Best-selling products by total revenue.</p>', unsafe_allow_html=True)
        top_products = filtered.groupby(['StockCode', 'Description'])['TotalPrice'].sum().reset_index()
        top_products = top_products.sort_values('TotalPrice', ascending=False).head(10)
        if not top_products.empty:
            top_products['Label'] = top_products['Description'].apply(lambda x: x[:30] + '…' if len(x) > 30 else x)
            fig = px.bar(top_products, x='TotalPrice', y='Label', orientation='h',
                         labels={'TotalPrice': 'Revenue (£)', 'Label': 'Product'},
                         color='TotalPrice', color_continuous_scale=[ACCENT, PRIMARY])
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
            fig = style_fig(fig)
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No data for the selected filters.")

# ---------------- Tab 2: Segments & Geography ----------------
with tab_segments:
    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.markdown('<p class="section-title">Revenue by Country</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">Top 10 countries by total revenue.</p>', unsafe_allow_html=True)
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
            st.info("No data for the selected filters.")

    with col_right2:
        st.markdown('<p class="section-title">Customer Segments</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">Share of customers in each RFM segment.</p>', unsafe_allow_html=True)
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
            st.caption("Champions · Loyal Customers · At Risk · Hibernating")
        else:
            st.info("No segment data for the selected filters.")

# ---------------- Tab 3: Time Patterns ----------------
with tab_patterns:
    col_hour, col_day = st.columns(2)

    with col_hour:
        st.markdown('<p class="section-title">Revenue by Hour</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">Busiest hours of the day.</p>', unsafe_allow_html=True)
        hourly = filtered.groupby('InvoiceHour')['TotalPrice'].sum().reset_index()
        if not hourly.empty:
            fig = px.bar(hourly, x='InvoiceHour', y='TotalPrice',
                         labels={'InvoiceHour': 'Hour of day', 'TotalPrice': 'Revenue (£)'})
            fig.update_traces(marker_color=ACCENT)
            fig = style_fig(fig)
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No data for the selected filters.")

    with col_day:
        st.markdown('<p class="section-title">Revenue by Day of Week</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">Busiest days of the week.</p>', unsafe_allow_html=True)
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
            st.info("No data for the selected filters.")

# ---------------- Tab 4: Raw Data ----------------
with tab_data:
    st.markdown('<p class="section-title">Filtered Transactions</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">First 100 rows of the currently filtered data.</p>', unsafe_allow_html=True)
    st.dataframe(filtered.head(100), use_container_width=True)
    st.caption(f"Showing first 100 rows of {len(filtered):,} filtered transactions.")

# -------------------------------------------------------------------
# Footer
# -------------------------------------------------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    '<p class="footer-note">Built with Streamlit · Data: UCI Online Retail Dataset</p>',
    unsafe_allow_html=True
)
