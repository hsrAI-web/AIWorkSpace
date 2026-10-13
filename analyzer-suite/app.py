from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
st.set_page_config(page_title="Insight Studio", page_icon="📊", layout="wide")
st.sidebar.title("Insight Studio")
choice = st.sidebar.radio("Choose an app", ["Stock Portfolio", "Ad Campaigns", "Personal Expenses"])
st.sidebar.caption("Three CSV-powered apps · sample data included")

SCHEMAS = {
    "Stock Portfolio": ("stocks.csv", ["date", "symbol", "sector", "shares", "cost_basis", "price"], ["shares", "cost_basis", "price"]),
    "Ad Campaigns": ("campaigns.csv", ["date", "campaign", "platform", "spend", "impressions", "clicks", "conversions", "revenue"], ["spend", "impressions", "clicks", "conversions", "revenue"]),
    "Personal Expenses": ("expenses.csv", ["date", "category", "merchant", "amount", "payment_method"], ["amount"]),
}

def ratio(a, b):
    return a / b if b else None

def percent(value):
    return "—" if value is None else f"{value:.1%}"

def money(value):
    return f"${value:,.2f}"

def metrics(items):
    for col, (label, value) in zip(st.columns(len(items)), items):
        col.metric(label, value)

def load():
    filename, required, numeric = SCHEMAS[choice]
    uploaded = st.sidebar.file_uploader("Upload your CSV", type="csv", key=filename)
    try:
        df = pd.read_csv(uploaded if uploaded else ROOT / "data" / filename)
        missing = set(required) - set(df.columns)
        if missing:
            raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
        if df.empty:
            raise ValueError("The CSV has no rows.")
        df = df[required].copy()
        if df.isna().any().any():
            raise ValueError("Required fields cannot be blank.")
        df["date"] = pd.to_datetime(df["date"], errors="raise").dt.normalize()
        for field in numeric:
            df[field] = pd.to_numeric(df[field], errors="raise")
            if (~df[field].between(0, 1e15)).any():
                raise ValueError(f"{field} must contain finite, nonnegative numbers.")
        for field in set(required) - set(numeric) - {"date"}:
            df[field] = df[field].astype(str).str.strip()
            if df[field].eq("").any():
                raise ValueError(f"{field} cannot be blank.")
        if choice == "Stock Portfolio" and df.duplicated(["date", "symbol"]).any():
            raise ValueError("Each date/symbol pair must be unique.")
        if choice == "Ad Campaigns":
            if (df["clicks"] > df["impressions"]).any() or (df["conversions"] > df["clicks"]).any():
                raise ValueError("Conversions must not exceed clicks; clicks must not exceed impressions.")
        st.sidebar.download_button("Download sample CSV", (ROOT / "data" / filename).read_bytes(), filename, "text/csv")
        st.sidebar.caption("Using uploaded data" if uploaded else "Using synthetic sample data · USD")
        return df
    except (ValueError, TypeError, pd.errors.ParserError, UnicodeError) as exc:
        st.error(f"Cannot read this CSV: {exc}")
        st.info("Use the sample CSV column names and YYYY-MM-DD dates.")
        st.stop()

def filters(df, field):
    selected = st.sidebar.multiselect(field.replace("_", " ").title(), sorted(df[field].unique()), default=sorted(df[field].unique()), key=choice + field)
    period = st.sidebar.date_input("Date range", (df.date.min().date(), df.date.max().date()), min_value=df.date.min().date(), max_value=df.date.max().date(), key=choice + "dates")
    if len(period) != 2:
        st.info("Select both a start and an end date.")
        st.stop()
    result = df[df[field].isin(selected) & df.date.between(pd.Timestamp(period[0]), pd.Timestamp(period[1]))].copy()
    if result.empty:
        st.info("No rows match these filters. Choose more categories or a wider date range.")
        st.stop()
    return result

def table(df, name):
    st.dataframe(df, hide_index=True, width="stretch")
    st.download_button("Export filtered data", df.to_csv(index=False).encode(), name, "text/csv", key=name)

st.title(choice + " Analyzer")
df = load()

if choice == "Stock Portfolio":
    st.caption("Explore holdings, allocation, and unrealized returns using dated portfolio snapshots.")
    df = filters(df, "sector")
    symbols = st.sidebar.multiselect("Symbols", sorted(df.symbol.unique()), default=sorted(df.symbol.unique()))
    df = df[df.symbol.isin(symbols)].copy()
    if df.empty:
        st.info("Select at least one symbol.")
        st.stop()
    df["value"] = df.shares * df.price
    df["cost"] = df.shares * df.cost_basis
    df["gain"] = df.value - df.cost
    latest_date = df.date.max()
    latest = df[df.date.eq(latest_date)].copy()
    st.caption(f"Holdings as of {latest_date:%d %b %Y}. Trend totals sum the holdings present on each date.")
    value, cost = latest.value.sum(), latest.cost.sum()
    metrics([("Portfolio value", money(value)), ("Cost basis", money(cost)), ("Unrealized gain", money(value-cost)), ("Return on cost", percent(ratio(value-cost, cost)))])
    overview, holdings, history = st.tabs(["Overview", "Holdings", "History"])
    with overview:
        left, right = st.columns(2)
        with left:
            st.subheader("Sector allocation ($)")
            st.bar_chart(latest.groupby("sector").value.sum())
        with right:
            st.subheader("Gain by holding ($)")
            st.bar_chart(latest.set_index("symbol").gain)
        if value:
            biggest = latest.loc[latest.value.idxmax()]
            st.info(f"Largest holding: {biggest.symbol}, {biggest.value/value:.1%} of filtered portfolio value.")
    with holdings:
        latest["return_pct"] = latest.gain.div(latest.cost.where(latest.cost.ne(0))) * 100
        table(latest, "holdings.csv")
    with history:
        st.subheader("Portfolio value and cost basis ($)")
        st.line_chart(df.groupby("date")[["value", "cost"]].sum())
        st.caption("Changes can reflect price movements and changes in holdings. Return on cost excludes dividends, fees, and realized gains.")
        table(df, "portfolio_history.csv")

elif choice == "Ad Campaigns":
    st.caption("Compare acquisition performance across platforms and campaigns. All views share the sidebar filters.")
    df = filters(df, "platform")
    campaigns = st.sidebar.multiselect("Campaigns", sorted(df.campaign.unique()), default=sorted(df.campaign.unique()))
    df = df[df.campaign.isin(campaigns)].copy()
    if df.empty:
        st.info("Select at least one campaign.")
        st.stop()
    totals = df[SCHEMAS[choice][2]].sum()
    metrics([("Spend", money(totals.spend)), ("Clicks", f"{totals.clicks:,.0f}"), ("Conversions", f"{totals.conversions:,.0f}"), ("ROI", percent(ratio(totals.revenue-totals.spend, totals.spend)))])
    def aggregate(field):
        result = df.groupby(field)[SCHEMAS[choice][2]].sum()
        result["CTR_pct"] = result.clicks.div(result.impressions.where(result.impressions.ne(0))) * 100
        result["CPC"] = result.spend.div(result.clicks.where(result.clicks.ne(0)))
        result["CPA"] = result.spend.div(result.conversions.where(result.conversions.ne(0)))
        result["ROAS"] = result.revenue.div(result.spend.where(result.spend.ne(0)))
        result["ROI_pct"] = (result.revenue-result.spend).div(result.spend.where(result.spend.ne(0))) * 100
        return result
    overview, platforms, details, trend = st.tabs(["Overview", "Platform comparison", "Campaign details", "Time series"])
    with overview:
        metrics([("Revenue", money(totals.revenue)), ("ROAS", "—" if totals.spend == 0 else f"{totals.revenue/totals.spend:.2f}×"), ("Click-through rate", percent(ratio(totals.clicks, totals.impressions))), ("Conversion rate", percent(ratio(totals.conversions, totals.clicks)))])
        st.bar_chart(aggregate("campaign")[["spend", "revenue"]])
        st.caption("ROI = (attributed revenue − ad spend) / ad spend. ROAS = revenue / spend. Other business costs are excluded; undefined ratios display as blank or —.")
    with platforms:
        summary = aggregate("platform")
        st.bar_chart(summary[["spend", "revenue"]])
        table(summary.reset_index(), "platform_summary.csv")
    with details:
        table(aggregate("campaign").reset_index(), "campaign_summary.csv")
        table(df, "campaign_rows.csv")
    with trend:
        metric = st.selectbox("Trend metric", ["spend", "clicks", "conversions", "revenue"])
        st.line_chart(df.pivot_table(index="date", columns="platform", values=metric, aggfunc="sum").fillna(0))

else:
    st.caption("Path C · Understand spending habits and compare your expenses with a monthly budget.")
    df = filters(df, "category")
    monthly_budget = st.sidebar.number_input("Monthly budget ($)", min_value=0.0, value=2500.0, step=100.0)
    monthly = df.groupby(df.date.dt.to_period("M").astype(str)).amount.sum()
    metrics([("Total expenses", money(df.amount.sum())), ("Transactions", str(len(df))), ("Average transaction", money(df.amount.mean())), ("Monthly average", money(monthly.mean()))])
    overview, transactions, budgets = st.tabs(["Overview", "Transactions", "Budget tracker"])
    with overview:
        left, right = st.columns(2)
        with left:
            st.subheader("Spending by category ($)")
            st.bar_chart(df.groupby("category").amount.sum().sort_values(ascending=False))
        with right:
            st.subheader("Daily spending ($)")
            st.line_chart(df.groupby("date").amount.sum())
        top = df.groupby("merchant").amount.sum().sort_values(ascending=False).head(5)
        st.subheader("Top merchants")
        st.dataframe(top.reset_index(), hide_index=True)
    with transactions:
        table(df.sort_values("date", ascending=False), "filtered_expenses.csv")
    with budgets:
        comparison = monthly.rename("spent").to_frame()
        comparison["budget"] = monthly_budget
        comparison["remaining"] = monthly_budget - comparison.spent
        st.bar_chart(comparison[["spent", "budget"]])
        table(comparison.reset_index(names="month"), "budget_summary.csv")
        st.caption("Budget comparison uses filtered expenses and the full monthly budget. Partial months and selected categories may understate total spending.")
