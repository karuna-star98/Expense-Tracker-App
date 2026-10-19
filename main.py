"""Run the whole pipeline:  python main.py

data generation -> cleaning -> analysis -> charts -> insights report
"""
import os
from src.data_generator import generate_expenses
from src.cleaning import clean_data
from src import analysis as an
from src.visualization import make_all_charts

for d in ("data", "outputs", "images"):
    os.makedirs(d, exist_ok=True)

print("1/5 Generating synthetic data...")
raw = generate_expenses()
raw.to_csv("data/expenses.csv", index=False)
print(f"    {len(raw)} raw rows saved to data/expenses.csv")

print("2/5 Cleaning...")
df = clean_data(raw.copy())
df.to_csv("data/cleaned_expenses.csv", index=False)

print("3/5 Analysing...")
cat, mon = an.category_summary(df), an.monthly_summary(df)
over, anom = an.detect_overspending(df), an.detect_anomalies(df)
cat.to_csv("outputs/category_summary.csv")
mon.to_csv("outputs/monthly_summary.csv")
over.to_csv("outputs/overspending_alerts.csv", index=False)
anom.to_csv("outputs/anomalies.csv", index=False)
print(cat.to_string())

print("4/5 Creating charts in images/ ...")
make_all_charts(df)

print("5/5 Writing insights report...")
insights = an.generate_insights(df)
with open("outputs/insights_report.txt", "w", encoding="utf-8") as f:
    f.write("EXPENSE TRACKER - KEY INSIGHTS\n" + "=" * 32 + "\n")
    for i, line in enumerate(insights, 1):
        f.write(f"{i}. {line}\n")
print()
for i, line in enumerate(insights, 1):
    print(f"{i}. {line}")
print("\nDone. Next: streamlit run app.py")
