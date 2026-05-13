import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text


# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Amazon Sales Dashboard (2015–2025)",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
span[data-baseweb="tag"] {
    background-color: #146EB4 !important;
}
span[data-baseweb="tag"] span[role="presentation"] {
    color: white !important;
}
span[data-baseweb="tag"] [data-testid="stMultiSelectDeleteIcon"] {
        display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Connect to Neon PostgreSQL
# ─────────────────────────────────────────────
DB_URL = "postgresql+psycopg2://neondb_owner:npg_7BXVlnbo8Hsv@ep-shy-bar-aqhbrn00.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DB_URL)




# ─────────────────────────────────────────────
# Sidebar – global filters
# ─────────────────────────────────────────────
st.sidebar.header("🔍 Filters")

years = sorted(df["order_year"].dropna().unique())
year_range = st.sidebar.select_slider(
    "Year range", options=years, value=(years[0], years[-1])
)

all_categories = sorted(df["category"].dropna().unique())
sel_categories = st.sidebar.multiselect(
    "Category", all_categories, default=all_categories
)

all_states = sorted(df["customer_state"].dropna().unique())
sel_states = st.sidebar.multiselect("State", all_states, default=all_states)

all_payment = sorted(df["payment_method"].dropna().unique())
sel_payment = st.sidebar.multiselect(
    "Payment method", all_payment, default=all_payment
)

prime_only = st.sidebar.checkbox("Prime members only", value=False)

# Apply filters
mask = (
    df["order_year"].between(*year_range)
    & df["category"].isin(sel_categories)
    & df["customer_state"].isin(sel_states)
    & df["payment_method"].isin(sel_payment)
)
if prime_only:
    mask &= df["is_prime_member"] == True

filtered = df[mask].copy()

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.title("🛒 Amazon India Sales Dashboard  (2015 – 2025)")
st.caption(
    f"Showing **{len(filtered):,}** transactions after filters  |  "
    f"Total dataset: **{len(df):,}** rows"
)

# ─────────────────────────────────────────────
# KPI row
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
filtered = df[mask].copy()

# Ensure numeric columns are properly typed
for col in ["final_amount_inr", "customer_rating", "delivery_days",
            "discount_percent", "product_rating", "original_price_inr"]:
    filtered[col] = pd.to_numeric(filtered[col], errors="coerce")

total_revenue = filtered["final_amount_inr"].sum()
avg_order     = filtered["final_amount_inr"].mean()
total_orders  = len(filtered)
avg_rating    = filtered["customer_rating"].mean()
return_rate   = (filtered["return_status"] == "Returned").mean() * 100

k1.metric("💰 Total Revenue", f"₹{total_revenue/1e7:.2f} Cr")
k2.metric("🛍️ Total Orders",  f"{total_orders:,}")
k3.metric("📦 Avg Order Value", f"₹{avg_order:,.0f}")
k4.metric("⭐ Avg Customer Rating", f"{avg_rating:.2f}")
k5.metric("↩️ Return Rate", f"{return_rate:.1f}%")

st.divider()

# ─────────────────────────────────────────────
# Tab layout
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Revenue Trends", "🗺️ Geography", "👤 Customers", "🏷️ Products", "💳 Payments"]
)

# ══════════════════════════════════════════════
# TAB 1 – Revenue Trends
# ══════════════════════════════════════════════
with tab1:
    st.subheader("Yearly Revenue & Order Volume")

    yearly = (
        filtered.groupby("order_year")
        .agg(revenue=("final_amount_inr", "sum"), orders=("transaction_id", "count"))
        .reset_index()
    )
    yearly["revenue_cr"] = yearly["revenue"] / 1e7

    fig_yr = make_subplots(specs=[[{"secondary_y": True}]])
    fig_yr.add_trace(
        go.Bar(x=yearly["order_year"], y=yearly["revenue_cr"],
               name="Revenue (Cr ₹)", marker_color="#FF9900"),
        secondary_y=False,
    )
    fig_yr.add_trace(
        go.Scatter(x=yearly["order_year"], y=yearly["orders"],
                   name="Orders", mode="lines+markers",
                   line=dict(color="#232F3E", width=2)),
        secondary_y=True,
    )
    fig_yr.update_layout(
        xaxis_title="Year",
        yaxis_title="Revenue (Cr ₹)",
        yaxis2_title="Number of Orders",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_yr, use_container_width=True)

    st.subheader("Monthly Revenue Heatmap")
    monthly = (
        filtered.groupby(["order_year", "order_month"])["final_amount_inr"]
        .sum()
        .reset_index()
    )
    pivot = monthly.pivot(index="order_year", columns="order_month", values="final_amount_inr").fillna(0)
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    pivot.columns = [month_names[c - 1] for c in pivot.columns]
    fig_heat = px.imshow(
        pivot / 1e6,
        color_continuous_scale="YlOrRd",
        labels=dict(color="Revenue (Lakh ₹)"),
        aspect="auto",
    )
    fig_heat.update_layout(xaxis_title="Month", yaxis_title="Year")
    st.plotly_chart(fig_heat, use_container_width=True)

    st.subheader("Festival Sale vs Regular Sale Revenue")
    fest = (
        filtered.groupby(["order_year", "is_festival_sale"])["final_amount_inr"]
        .sum()
        .reset_index()
    )
    fest["label"] = fest["is_festival_sale"].map({True: "Festival", False: "Regular"})
    fig_fest = px.bar(
        fest, x="order_year", y="final_amount_inr", color="label",
        barmode="group",
        labels={"final_amount_inr": "Revenue (₹)", "order_year": "Year"},
        color_discrete_map={"Festival": "#FF9900", "Regular": "#146EB4"},
    )
    st.plotly_chart(fig_fest, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 – Geography
# ══════════════════════════════════════════════
with tab2:
    st.subheader("Revenue by State")

    state_rev = (
        filtered.groupby("customer_state")
        .agg(revenue=("final_amount_inr", "sum"), orders=("transaction_id", "count"))
        .reset_index()
        .sort_values("revenue", ascending=True)
    )
    fig_state = px.bar(
        state_rev, x="revenue", y="customer_state", orientation="h",
        labels={"revenue": "Revenue (₹)", "customer_state": "State"},
        color="revenue", color_continuous_scale="oranges",
    )
    fig_state.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_state, use_container_width=True)

    st.subheader("Customer Tier Distribution by State")
    tier_state = (
        filtered.groupby(["customer_state", "customer_tier"])
        .size()
        .reset_index(name="count")
    )
    fig_ts = px.bar(
        tier_state, x="customer_state", y="count", color="customer_tier",
        barmode="stack",
        labels={"count": "Customers", "customer_state": "State"},
    )
    st.plotly_chart(fig_ts, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 – Customers
# ══════════════════════════════════════════════
with tab3:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Orders by Age Group")
        age_grp = filtered["customer_age_group"].value_counts().reset_index()
        age_grp.columns = ["age_group", "count"]
        fig_age = px.pie(
            age_grp, names="age_group", values="count",
            color_discrete_sequence=px.colors.sequential.Oranges_r,
            hole=0.4,
        )
        st.plotly_chart(fig_age, use_container_width=True)

    with c2:
        st.subheader("Spending Tier Breakdown")
        spend_tier = filtered["customer_spending_tier"].value_counts().reset_index()
        spend_tier.columns = ["tier", "count"]
        fig_spend = px.bar(
            spend_tier, x="tier", y="count",
            color="count", color_continuous_scale="Blues",
            labels={"count": "Customers", "tier": "Spending Tier"},
        )
        fig_spend.update_layout(showlegend=False)
        st.plotly_chart(fig_spend, use_container_width=True)

    st.subheader("Prime vs Non-Prime: Avg Order Value Over Years")
    prime_trend = (
        filtered.groupby(["order_year", "is_prime_member"])["final_amount_inr"]
        .mean(numeric_only=True)
        .reset_index()
    )
    prime_trend["label"] = prime_trend["is_prime_member"].map({True: "Prime", False: "Non-Prime"})
    fig_prime = px.line(
        prime_trend, x="order_year", y="final_amount_inr", color="label",
        markers=True,
        color_discrete_map={"Prime": "#FF9900", "Non-Prime": "#232F3E"},
        labels={"final_amount_inr": "Avg Order Value (₹)", "order_year": "Year"},
    )
    st.plotly_chart(fig_prime, use_container_width=True)

    st.subheader("Return Status Distribution")
    ret = filtered["return_status"].value_counts().reset_index()
    ret.columns = ["status", "count"]
    fig_ret = px.pie(
        ret, names="status", values="count",
        color_discrete_sequence=["#FF9900", "#146EB4", "#232F3E"],
        hole=0.35,
    )
    st.plotly_chart(fig_ret, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 – Products
# ══════════════════════════════════════════════
with tab4:
    st.subheader("Top 10 Sub-categories by Revenue")
    sub_rev = (
        filtered.groupby("subcategory")["final_amount_inr"]
        .sum()
        .nlargest(10)
        .reset_index()
        .sort_values("final_amount_inr")
    )
    fig_sub = px.bar(
        sub_rev, x="final_amount_inr", y="subcategory", orientation="h",
        labels={"final_amount_inr": "Revenue (₹)", "subcategory": "Sub-category"},
        color="final_amount_inr", color_continuous_scale="YlOrRd",
    )
    fig_sub.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_sub, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Avg Discount % by Sub-category (Top 10)")
        disc = (
            filtered.groupby("subcategory")["discount_percent"]
            .mean()
            .nlargest(10)
            .reset_index()
            .sort_values("discount_percent")
        )
        fig_disc = px.bar(
            disc, x="discount_percent", y="subcategory", orientation="h",
            labels={"discount_percent": "Avg Discount (%)", "subcategory": "Sub-category"},
            color="discount_percent", color_continuous_scale="Reds",
        )
        fig_disc.update_layout(showlegend=False)
        st.plotly_chart(fig_disc, use_container_width=True)

    with c2:
        st.subheader("Product Rating Distribution")
        fig_rating = px.histogram(
            filtered, x="product_rating", nbins=20,
            labels={"product_rating": "Product Rating", "count": "# Products"},
            color_discrete_sequence=["#FF9900"],
        )
        fig_rating.update_layout(plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_rating, use_container_width=True)

    st.subheader("Top 15 Brands by Revenue")
    brand_rev = (
        filtered.groupby("brand")["final_amount_inr"]
        .sum()
        .nlargest(15)
        .reset_index()
        .sort_values("final_amount_inr")
    )
    fig_brand = px.bar(
        brand_rev, x="final_amount_inr", y="brand", orientation="h",
        color="final_amount_inr", color_continuous_scale="oranges",
        labels={"final_amount_inr": "Revenue (₹)", "brand": "Brand"},
    )
    fig_brand.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_brand, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5 – Payments & Delivery
# ══════════════════════════════════════════════
with tab5:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Payment Method Share")
        pay = filtered["payment_method"].value_counts().reset_index()
        pay.columns = ["method", "count"]
        fig_pay = px.pie(
            pay, names="method", values="count",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4,
        )
        st.plotly_chart(fig_pay, use_container_width=True)

    with c2:
        st.subheader("Delivery Type Distribution")
        dtype = filtered["delivery_type"].value_counts().reset_index()
        dtype.columns = ["type", "count"]
        fig_dt = px.bar(
            dtype, x="type", y="count",
            labels={"count": "Orders", "type": "Delivery Type"},
            color="count", color_continuous_scale="Blues",
        )
        fig_dt.update_layout(showlegend=False)
        st.plotly_chart(fig_dt, use_container_width=True)

    st.subheader("Average Delivery Days by State")
    del_state = (
        filtered.groupby("customer_state")["delivery_days"]
        .mean(numeric_only=True)
        .reset_index()
        .sort_values("delivery_days", ascending=False)
    )
    fig_del = px.bar(
        del_state, x="customer_state", y="delivery_days",
        labels={"delivery_days": "Avg Delivery Days", "customer_state": "State"},
        color="delivery_days", color_continuous_scale="RdYlGn_r",
    )
    st.plotly_chart(fig_del, use_container_width=True)

    st.subheader("Payment Method Trend Over Years")
    pay_yr = (
        filtered.groupby(["order_year", "payment_method"])
        .size()
        .reset_index(name="count")
    )
    fig_pay_yr = px.line(
        pay_yr, x="order_year", y="count", color="payment_method",
        markers=True,
        labels={"count": "Orders", "order_year": "Year", "payment_method": "Payment Method"},
    )
    st.plotly_chart(fig_pay_yr, use_container_width=True)

# ─────────────────────────────────────────────
# Raw data explorer
# ─────────────────────────────────────────────
with st.expander("🔎 Raw Data Explorer"):
    st.dataframe(filtered.head(500), use_container_width=True)
    st.caption("Showing first 500 rows of filtered data.")

# ─────────────────────────────────────────────
# Year-wise summary section
# ─────────────────────────────────────────────
st.divider()
year_filter = st.selectbox("Select Year", sorted(df['order_year'].unique()))

filtered_df = df[df['order_year'] == year_filter]

for col in ["final_amount_inr"]:
    filtered_df[col] = pd.to_numeric(filtered_df[col], errors="coerce")

total_revenue   = filtered_df['final_amount_inr'].sum()
average_revenue = filtered_df['final_amount_inr'].mean()
top_brand       = filtered_df.groupby('brand')['final_amount_inr'].sum().idxmax()
top_item        = filtered_df.groupby('subcategory')['final_amount_inr'].sum().idxmax()
top_payment     = filtered_df.groupby('payment_method')['final_amount_inr'].sum().idxmax()

month_sales     = filtered_df.groupby('order_month')['final_amount_inr'].sum()
max_month       = month_sales.idxmax()
min_month       = month_sales.idxmin()

city_sales      = filtered_df.groupby('customer_city')['final_amount_inr'].sum()
max_city        = city_sales.idxmax()
min_city        = city_sales.idxmin()

product_sales       = filtered_df.groupby('product_name')['final_amount_inr'].sum()
most_sold_product   = product_sales.idxmax()
least_sold_product  = product_sales.idxmin()

st.markdown(f"<h4 style='color:#00008B;'>Amazon Dashboard for {year_filter}</h4>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
col1.markdown(
    f"<span style='font-size:18px; font-weight:bold;'>💰 Total Revenue:</span> "
    f"<span style='font-size:16px;'>{total_revenue:,.2f} INR</span>",
    unsafe_allow_html=True
)
col2.markdown(f"<p style='font-size:20px; font-weight:bold;'>📊 Average Revenue: {average_revenue:,.2f} INR</p>", unsafe_allow_html=True)

col3, col4 = st.columns(2)
col3.metric("🏷️ Top Brand", top_brand)
col4.metric("📦 Top Item", top_item)

col5, col6 = st.columns(2)
col5.metric("💳 Top Payment Method", top_payment)
col6.metric("📅 Max Sales Month", max_month)

col9, col10 = st.columns(2)
col9.metric("⭐ Most Sold Product", most_sold_product)
col10.metric("⚠️ Least Sold Product", least_sold_product)

st.metric("🌆 Max Sales City", max_city)
st.metric("📉 Least Sales City", min_city)
