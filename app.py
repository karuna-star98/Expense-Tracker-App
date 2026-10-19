"""Streamlit dashboard.  Run:  streamlit run app.py"""
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from src.data_generator import generate_expenses, MONTHLY_BUDGET
from src.cleaning import clean_data
from src import analysis as an

st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")
st.title("💰 Expense Tracker Dashboard")


@st.cache_data
def load(uploaded=None):
    if uploaded is not None:
        raw = pd.read_csv(uploaded)
    elif os.path.exists("data/expenses.csv"):
        raw = pd.read_csv("data/expenses.csv")
    else:
        raw = generate_expenses()
    return clean_data(raw, verbose=False)


up = st.sidebar.file_uploader("Upload your own CSV (Date, Category, Description, Amount, Type, Payment_Method)", type="csv")
df = load(up)

st.sidebar.header("🔍 Filters")
cats = st.sidebar.multiselect("Categories", sorted(df.Category.unique()), default=sorted(df.Category.unique()))
d_min, d_max = df.Date.min().date(), df.Date.max().date()
rng = st.sidebar.date_input("Date range", (d_min, d_max), min_value=d_min, max_value=d_max)
pay = st.sidebar.multiselect("Payment method", sorted(df.Payment_Method.unique()), default=sorted(df.Payment_Method.unique()))

f = df[df.Category.isin(cats) & df.Payment_Method.isin(pay)]
if len(rng) == 2:
    f = f[(f.Date.dt.date >= rng[0]) & (f.Date.dt.date <= rng[1])]
if f.empty:
    st.warning("No data for the selected filters."); st.stop()

inc = f[f.Type == "Income"].Amount.sum()
exp = f[f.Type == "Expense"].Amount.sum()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Income", f"₹{inc:,.0f}")
c2.metric("Expenses", f"₹{exp:,.0f}")
c3.metric("Savings", f"₹{inc-exp:,.0f}")
c4.metric("Savings rate", f"{(inc-exp)/inc*100:.1f}%" if inc else "n/a")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends", "🚨 Budget alerts", "🧾 Data"])
with tab1:
    a, b = st.columns(2)
    cs = an.category_summary(f)
    a.subheader("Spend by category"); a.bar_chart(cs["Total"])
    b.subheader("Expense share")
    fig, ax = plt.subplots(); ax.pie(cs["Total"], labels=cs.index, autopct="%1.1f%%", startangle=90); ax.axis("equal")
    b.pyplot(fig)
    st.subheader("Category summary"); st.dataframe(cs)
with tab2:
    ms = an.monthly_summary(f)
    st.subheader("Income vs expense"); st.line_chart(ms[["Income", "Expense"]])
    st.subheader("Savings rate (%)"); st.bar_chart(ms["Savings_Rate_%"])
    st.subheader("Category × month heatmap data"); st.dataframe(an.monthly_category_matrix(f))
with tab3:
    over = an.detect_overspending(f)
    st.subheader(f"Budget exceeded {len(over)} times")
    st.dataframe(over, use_container_width=True)
    st.subheader("Unusually large transactions"); st.dataframe(an.detect_anomalies(f))
    st.subheader("💡 Insights")
    for line in an.generate_insights(f):
        st.write("•", line)
with tab4:
    st.dataframe(f, use_container_width=True)
    st.download_button("Download filtered CSV", f.to_csv(index=False), "filtered_expenses.csv")
