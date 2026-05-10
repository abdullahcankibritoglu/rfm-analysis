import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
import datetime as dt
warnings.filterwarnings("ignore")

# ============================================================
# 1. DATA LOADING
# ============================================================
df = pd.read_csv("online_retail.csv", encoding="latin1")

print(f"Raw data: {df.shape[0]} rows, {df.shape[1]} columns")
print(df.dtypes)
print(df.describe())

missing = df.isnull().sum()
missing_pct = missing * 100.0 / df.shape[0]
missing_df = pd.DataFrame({
    "Missing Count": missing,
    "Missing Pct":   round(missing_pct, 2)
})
print(missing_df[missing_df["Missing Count"] > 0])

# ============================================================
# 2. DATA CLEANING
# ============================================================
print(f"\nStep 0 — Raw:                  {df.shape[0]:>7} rows")

df.dropna(subset=["CustomerID"], inplace=True)
print(f"Step 1 — Drop missing CustID:  {df.shape[0]:>7} rows")

df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
print(f"Step 2 — Drop cancellations:   {df.shape[0]:>7} rows")

df = df[~((df["Quantity"] <= 0) | (df["UnitPrice"] <= 0))]
print(f"Step 3 — Drop invalid values:  {df.shape[0]:>7} rows")

# ============================================================
# 3. FEATURE ENGINEERING
# ============================================================
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["TotalPrice"]  = df["Quantity"] * df["UnitPrice"]
df["Year"]        = df["InvoiceDate"].dt.year
df["Month"]       = df["InvoiceDate"].dt.month
df["Day"]         = df["InvoiceDate"].dt.day
df["Hour"]        = df["InvoiceDate"].dt.hour
df["DayOfWeek"]   = df["InvoiceDate"].dt.day_name()

# ============================================================
# 4. EDA VISUALIZATIONS
# ============================================================

# 4a. Top 10 Countries
top_10_country = (
    df.groupby("Country")["TotalPrice"]
    .sum().reset_index()
    .sort_values("TotalPrice", ascending=False)
    .head(10)
)
fig_countries = px.bar(
    top_10_country, x="Country", y="TotalPrice",
    title="Top 10 Countries — Total Revenue (£)",
    template="plotly_white", text="TotalPrice"
)
fig_countries.update_traces(texttemplate="%{text:.2s}", textposition="outside")
fig_countries.write_html("visualizations/top_countries.html")
fig_countries.show()

# 4b. Daily Sales Trend + 30-Day Rolling Average
daily_sales = df.groupby(df["InvoiceDate"].dt.date)["TotalPrice"].sum().reset_index()
daily_sales.columns = ["Date", "TotalSales"]
daily_sales["Rolling_30"] = daily_sales["TotalSales"].rolling(30).mean()

fig_daily = go.Figure()
fig_daily.add_trace(go.Scatter(
    x=daily_sales["Date"], y=daily_sales["TotalSales"],
    name="Daily Sales", line=dict(color="royalblue", width=1)
))
fig_daily.add_trace(go.Scatter(
    x=daily_sales["Date"], y=daily_sales["Rolling_30"],
    name="30-Day Average", line=dict(color="crimson", width=2)
))
fig_daily.update_layout(title="Daily Sales Trend + 30-Day Rolling Average", template="plotly_white")
fig_daily.write_html("visualizations/daily_sales.html")
fig_daily.show()

# 4c. Order Density Heatmap
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Sunday"]
heatmap_data = df.pivot_table(
    index="Hour", columns="DayOfWeek",
    values="InvoiceNo", aggfunc="count"
)
fig_heatmap = px.imshow(
    heatmap_data[day_order],
    title="Order Density — Hour & Day of Week",
    template="plotly_white",
    color_continuous_scale="Blues"
)
fig_heatmap.write_html("visualizations/heatmap.html")
fig_heatmap.show()

# 4d. Top 10 Products
top_10_product = (
    df.groupby("Description")["Quantity"]
    .sum().nlargest(10).reset_index()
)
fig_products = px.bar(
    top_10_product, x="Quantity", y="Description",
    orientation="h", title="Top 10 Products by Quantity",
    template="plotly_white"
)
fig_products.update_layout(yaxis={"categoryorder": "total ascending"})
fig_products.write_html("visualizations/top_products.html")
fig_products.show()

# ============================================================
# 5. RFM CALCULATION
# ============================================================
reference_date = df["InvoiceDate"].dt.normalize().max() + dt.timedelta(days=1)

rfm = df.groupby("CustomerID").agg(
    Recency   = ("InvoiceDate", lambda x: (reference_date - x.dt.normalize().max()).days),
    Frequency = ("InvoiceNo",   "nunique"),
    Monetary  = ("TotalPrice",  "sum")
).reset_index()

print(f"\nRFM table: {rfm.shape[0]} customers")
print(rfm.describe().round(2))

# ============================================================
# 6. RFM SCORING
# ============================================================
rfm["R_Score"] = pd.qcut(rfm["Recency"], q=5, labels=[5, 4, 3, 2, 1])
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])
rfm["M_Score"] = pd.qcut(rfm["Monetary"], q=5, labels=[1, 2, 3, 4, 5])

rfm[["R_Score", "F_Score", "M_Score"]] = rfm[["R_Score", "F_Score", "M_Score"]].astype(int)
rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)
rfm["RFM_Total"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

# ============================================================
# 7. SEGMENTATION
# ============================================================
def assign_segment(row):
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 3 and f >= 3:
        return "Loyal Customers"
    elif r >= 4 and f <= 2:
        return "New Customers"
    elif r <= 2 and f >= 3 and m >= 3:
        return "At Risk"
    elif r <= 2 and f >= 4 and m >= 4:
        return "Cannot Lose Them"
    elif r <= 2 and f <= 2 and m <= 2:
        return "Lost"
    else:
        return "Hibernating"

rfm["Segment"] = rfm.apply(assign_segment, axis=1)
print("\nSegment Distribution:")
print(rfm["Segment"].value_counts())

# Segment summary
segment_summary = rfm.groupby("Segment").agg(
    Customer_Count  = ("CustomerID", "count"),
    Avg_Recency     = ("Recency",    "mean"),
    Avg_Frequency   = ("Frequency",  "mean"),
    Avg_Monetary    = ("Monetary",   "mean")
).round(1).sort_values("Customer_Count", ascending=False)
print("\nSegment Summary:")
print(segment_summary)

# ============================================================
# 8. RFM VISUALIZATIONS
# ============================================================

# 8a. Treemap
fig_treemap = px.treemap(
    rfm, path=["Segment"], values="Monetary",
    color="RFM_Total", color_continuous_scale="RdYlGn",
    title="Customer Segments Treemap — Revenue Weighted"
)
fig_treemap.write_html("visualizations/treemap.html")
fig_treemap.show()

# 8b. Scatter
fig_scatter = px.scatter(
    rfm, x="Recency", y="Monetary", size="Frequency",
    color="Segment", title="RFM Scatter — Recency vs Monetary",
    template="plotly_white", hover_data=["CustomerID", "RFM_Score"]
)
fig_scatter.write_html("visualizations/scatter.html")
fig_scatter.show()

# ============================================================
# 9. COHORT RETENTION ANALYSIS
# ============================================================
df["Cohort_Month"] = df.groupby("CustomerID")["InvoiceDate"].transform("min").dt.to_period("M")
df["Order_Month"]  = df["InvoiceDate"].dt.to_period("M")
df["Cohort_Index"] = (df["Order_Month"] - df["Cohort_Month"]).apply(lambda x: x.n)
df["Cohort_Month"] = df["Cohort_Month"].astype(str)

cohort_data      = df.groupby(["Cohort_Month", "Cohort_Index"])["CustomerID"].nunique().reset_index()
cohort_pivot     = cohort_data.pivot_table(index="Cohort_Month", columns="Cohort_Index", values="CustomerID")
cohort_retention = cohort_pivot.divide(cohort_pivot[0], axis=0).round(3) * 100

fig_cohort = px.imshow(
    cohort_retention,
    title="Cohort Retention Analysis (%)",
    color_continuous_scale="Blues",
    template="plotly_white"
)
fig_cohort.write_html("visualizations/cohort.html")
fig_cohort.show()

# ============================================================
# 10. REUSABLE PIPELINE
# ============================================================
def run_rfm_pipeline(df):
    df = df.copy()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df.dropna(subset=["CustomerID"], inplace=True)
    df["CustomerID"] = df["CustomerID"].astype(int)
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    df = df[~((df["Quantity"] <= 0) | (df["UnitPrice"] <= 0))]
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

    reference_date = df["InvoiceDate"].dt.normalize().max() + dt.timedelta(days=1)

    rfm = df.groupby("CustomerID").agg(
        Recency   = ("InvoiceDate", lambda x: (reference_date - x.dt.normalize().max()).days),
        Frequency = ("InvoiceNo",   "nunique"),
        Monetary  = ("TotalPrice",  "sum")
    ).reset_index()

    rfm["R_Score"] = pd.qcut(rfm["Recency"], q=5, labels=[5, 4, 3, 2, 1])
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], q=5, labels=[1, 2, 3, 4, 5])
    rfm[["R_Score", "F_Score", "M_Score"]] = rfm[["R_Score", "F_Score", "M_Score"]].astype(int)
    rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)
    rfm["Segment"]  = rfm.apply(assign_segment, axis=1)

    print(f"✅ Pipeline complete — {rfm.shape[0]} customers, {rfm['Segment'].nunique()} segments")
    print(rfm["Segment"].value_counts())
    return rfm

print(f"\n✅ {rfm.shape[0]} müşteri, {rfm['Segment'].nunique()} segment")
print(rfm["Segment"].value_counts())
