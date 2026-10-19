"""Phase 4 + 6 + 8: EDA, analysis, overspending detection and insights."""
import pandas as pd
from src.data_generator import MONTHLY_BUDGET


def expenses_only(df):
    return df[df["Type"] == "Expense"]


def category_summary(df):
    e = expenses_only(df)
    s = e.groupby("Category")["Amount"].agg(Total="sum", Transactions="count", Average="mean").round(0)
    s["Share_%"] = (s["Total"] / s["Total"].sum() * 100).round(1)
    return s.sort_values("Total", ascending=False)


def monthly_summary(df):
    m = df.pivot_table(index="YearMonth", columns="Type", values="Amount", aggfunc="sum", fill_value=0)
    for col in ("Income", "Expense"):
        if col not in m:
            m[col] = 0
    m["Savings"] = m["Income"] - m["Expense"]
    m["Savings_Rate_%"] = (m["Savings"] / m["Income"].replace(0, float("nan")) * 100).round(1)
    m["Expense_MoM_%"] = (m["Expense"].pct_change() * 100).round(1)
    return m


def monthly_category_matrix(df):
    return expenses_only(df).pivot_table(index="Category", columns="Month_Num",
                                         values="Amount", aggfunc="sum", fill_value=0)


def payment_summary(df):
    return expenses_only(df).groupby("Payment_Method")["Amount"].sum().sort_values(ascending=False)


def detect_overspending(df, budgets=MONTHLY_BUDGET):
    """Flag every (month, category) where spend > budget."""
    spend = expenses_only(df).groupby(["YearMonth", "Category"])["Amount"].sum().reset_index()
    spend["Budget"] = spend["Category"].map(budgets)
    spend = spend.dropna(subset=["Budget"])
    spend["Over_By"] = spend["Amount"] - spend["Budget"]
    spend["Over_%"] = (spend["Over_By"] / spend["Budget"] * 100).round(1)
    return spend[spend["Over_By"] > 0].sort_values("Over_%", ascending=False)


def detect_anomalies(df, z=2.5):
    """Unusually large transactions within their category (z-score)."""
    e = expenses_only(df).copy()
    g = e.groupby("Category")["Amount"]
    e["Z"] = ((e["Amount"] - g.transform("mean")) / g.transform("std")).round(2)
    return e[e["Z"] > z].sort_values("Z", ascending=False)[["Date", "Category", "Amount", "Z"]]


def generate_insights(df):
    e = expenses_only(df)
    cat, mon = category_summary(df), monthly_summary(df)
    over = detect_overspending(df)
    income, spent = df[df.Type == "Income"].Amount.sum(), e.Amount.sum()
    flexible = e[~e.Category.isin(["Rent", "Bills", "Subscriptions"])]
    wk = e.groupby("Weekday")["Amount"].mean().sort_values(ascending=False)
    L = []
    if income:
        L.append(f"Total income Rs.{income:,.0f} vs total expenses Rs.{spent:,.0f} -> savings Rs.{income-spent:,.0f} "
                 f"({(income-spent)/income*100:.1f}% savings rate).")
    L.append(f"Biggest spending category: {cat.index[0]} (Rs.{cat.Total.iloc[0]:,.0f}, {cat['Share_%'].iloc[0]}% of expenses).")
    if len(flexible):
        L.append(f"Largest controllable (non-fixed) category: {flexible.groupby('Category')['Amount'].sum().idxmax()} "
                 f"- the best place to cut costs.")
    L.append(f"Highest-spend month: {mon['Expense'].idxmax()} (Rs.{mon['Expense'].max():,.0f}); "
             f"lowest: {mon['Expense'].idxmin()} (Rs.{mon['Expense'].min():,.0f}).")
    if mon["Savings_Rate_%"].notna().any():
        L.append(f"Lowest savings rate: {mon['Savings_Rate_%'].idxmin()} ({mon['Savings_Rate_%'].min()}%).")
    if len(over):
        c = over.Category.value_counts()
        L.append(f"Budget exceeded {len(over)} times across {over.YearMonth.nunique()} months; "
                 f"most frequent offender: {c.index[0]} ({c.iloc[0]} months).")
        w = over.iloc[0]
        L.append(f"Worst overspend: {w.Category} in {w.YearMonth} - {w['Over_%']}% above budget (Rs.{w.Over_By:,.0f}).")
    else:
        L.append("No category exceeded its monthly budget.")
    L.append(f"Most expensive weekday on average: {wk.index[0]} (Rs.{wk.iloc[0]:,.0f}/transaction).")
    L.append(f"Most used payment method (by amount): {payment_summary(df).index[0]}.")
    return L
