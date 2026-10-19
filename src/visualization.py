"""Phase 7: Charts (saved as PNG into images/)."""
import os
import matplotlib
matplotlib.use("Agg")  # no GUI needed; saves files directly
import matplotlib.pyplot as plt
import seaborn as sns
from src import analysis as an
from src.data_generator import MONTHLY_BUDGET

sns.set_theme(style="whitegrid", palette="Set2")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _save(fig, folder, name):
    fig.tight_layout()
    fig.savefig(os.path.join(folder, name), dpi=130)
    plt.close(fig)


def make_all_charts(df, folder="images"):
    os.makedirs(folder, exist_ok=True)
    cat, mon = an.category_summary(df), an.monthly_summary(df)
    e = an.expenses_only(df)

    # 1 bar: category totals
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(x=cat.index, y=cat.Total, hue=cat.index, legend=False, ax=ax)
    ax.set(title="Total Expense by Category", xlabel="", ylabel="Amount (Rs.)")
    ax.tick_params(axis="x", rotation=30)
    _save(fig, folder, "01_category_bar.png")

    # 2 pie: share
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(cat.Total, labels=cat.index, autopct="%1.1f%%", startangle=140,
           colors=sns.color_palette("Set3", len(cat)))
    ax.set_title("Expense Distribution by Category")
    _save(fig, folder, "02_expense_pie.png")

    # 3 line: income vs expense
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(mon.index, mon.Income, marker="o", label="Income")
    ax.plot(mon.index, mon.Expense, marker="o", label="Expense")
    ax.fill_between(mon.index, mon.Expense, mon.Income, alpha=.15, color="green", label="Savings")
    ax.set(title="Monthly Income vs Expense", ylabel="Amount (Rs.)")
    ax.tick_params(axis="x", rotation=45); ax.legend()
    _save(fig, folder, "03_monthly_income_vs_expense.png")

    # 4 heatmap: category x month
    mat = an.monthly_category_matrix(df)
    mat.columns = [MONTHS[c - 1] for c in mat.columns]
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.heatmap(mat, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax, cbar_kws={"label": "Rs."})
    ax.set(title="Spending Heatmap: Category x Month", xlabel="", ylabel="")
    _save(fig, folder, "04_category_month_heatmap.png")

    # 5 weekday
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    sns.barplot(data=e, x="Weekday", y="Amount", order=order, estimator="sum", errorbar=None,
                hue="Weekday", legend=False, ax=ax, palette="coolwarm")
    ax.set(title="Total Spending by Weekday", xlabel="", ylabel="Amount (Rs.)")
    _save(fig, folder, "05_weekday_spending.png")

    # 6 payment methods
    pay = an.payment_summary(df)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(pay, labels=pay.index, autopct="%1.1f%%", wedgeprops=dict(width=.45))
    ax.set_title("Spending by Payment Method")
    _save(fig, folder, "06_payment_methods.png")

    # 7 savings rate
    fig, ax = plt.subplots(figsize=(10, 4.5))
    colors = ["#d95f5f" if v < 20 else "#5fa85f" for v in mon["Savings_Rate_%"]]
    ax.bar(mon.index, mon["Savings_Rate_%"], color=colors)
    ax.axhline(20, ls="--", color="gray", label="20% target")
    ax.set(title="Monthly Savings Rate (%)", ylabel="%"); ax.legend()
    ax.tick_params(axis="x", rotation=45)
    _save(fig, folder, "07_savings_rate.png")

    # 8 budget vs actual (avg monthly)
    spend = e.groupby("Category")["Amount"].sum() / e["YearMonth"].nunique()
    bud = [MONTHLY_BUDGET.get(c, 0) for c in spend.index]
    fig, ax = plt.subplots(figsize=(10, 5))
    x = list(range(len(spend)))
    ax.bar([i - .2 for i in x], spend.values, .4, label="Avg monthly spend")
    ax.bar([i + .2 for i in x], bud, .4, label="Monthly budget")
    ax.set_xticks(x); ax.set_xticklabels(spend.index, rotation=30)
    ax.set(title="Average Monthly Spend vs Budget", ylabel="Rs."); ax.legend()
    _save(fig, folder, "08_budget_vs_actual.png")
