# Expense Tracker App – Complete Guide

## 1. What is it?
**Simple:** an app that records what you spend and shows where your money goes.
**Technical:** a pipeline that ingests transactional data (date, category, amount, type, payment method), cleans and enriches it with pandas, aggregates it (category / time / payment), applies rule-based detection (budget breaches, z-score anomalies) and presents results via charts and a Streamlit dashboard.

**Why it matters:** budgeting, cost control, business expense monitoring, financial planning. Used in spirit by Google Pay, CRED, Mint, PhonePe, Splitwise, RazorpayX.

## 2. Tech stack options
| Option | Tools | Dashboard | Difficulty |
|---|---|---|---|
| A (Easy) | Python, Pandas, Matplotlib, CSV | No (charts only) | ⭐ |
| **B (Intermediate) ← chosen** | Pandas, NumPy, Seaborn, Streamlit | Yes | ⭐⭐ |
| C (Advanced) | + SQL/SQLite, scikit-learn forecasting, Plotly, FastAPI, Docker | Yes + API | ⭐⭐⭐⭐ |

Option B is best for students: recruiters see a working app, but no heavy infrastructure.

## 3. Architecture
```
 [Synthetic generator / CSV upload]
              │
              ▼
 ┌─────────── PROCESSING (src/) ───────────┐
 │ cleaning.py  → dedupe, types, text fix  │
 │ features     → month, weekday, savings  │
 │ analysis.py  → aggregates, budget check │
 └─────────────────┬───────────────────────┘
                   ▼
   outputs/ (CSV, insights)   images/ (charts)   app.py (dashboard)
```

## 4. Phase plan
| Phase | Do | Why | Output | Avoid |
|---|---|---|---|---|
| 1 Setup | venv + install libs | reproducibility | working env | installing globally |
| 2 Data | `src/data_generator.py` | no real data | data/expenses.csv | unrealistic constant values |
| 3 Cleaning | `src/cleaning.py` | wrong data → wrong charts | cleaned_expenses.csv | dropping rows blindly |
| 4 EDA | summaries, `describe()` | understand data | category/monthly tables | skipping sanity checks |
| 5 Features | month, weekday, savings | enable time analysis | new columns | leaking Type into amount sign |
| 6 Analysis | budgets, anomalies | find problems | alerts CSVs | hard-coding magic numbers |
| 7 Visuals | `src/visualization.py` | communicate | 8 PNGs | too many colours, no titles |
| 8 Insights | `generate_insights` | decisions | insights_report.txt | stating numbers w/o meaning |
| 9 GitHub | commit + push | proof of work | public repo | committing venv / secrets |

## 5. Folder structure
`data/` datasets · `notebooks/` experiments · `src/` reusable code · `outputs/` reports · `images/` charts for README · `docs/` guides · `app.py` dashboard · `main.py` pipeline runner · `requirements.txt` dependencies.

## 6. Installation
**Windows**
```bat
python --version
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
**Mac / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 7. Code
Everything is in `src/`, `main.py`, `app.py` – fully commented.

## 8. Simulation (how data behaves)
1. **Fixed items** each month: salary ₹55,000 (bonus in Mar/Sep), rent ₹12,000, subscriptions, internet.
2. **Variable items:** per category, number of transactions ~ Poisson, amount ~ Normal(mean, std).
3. **Trends:** seasonal multipliers – Shopping ×1.4–1.8 in Oct–Dec (festivals), Transport ×1.5 in May–Jun (travel), Health higher in Jan–Feb, electricity ×1.5 in summer.
4. **Dirty data:** lowercase/space categories, missing amounts, one invalid date, 5 duplicates.
5. **Overspending:** per-category monthly budget; any month above budget is flagged with % over.
6. **Output:** summaries, alerts, charts, insights.

Proof to save: terminal output of `python main.py`, all PNGs in `images/`, `outputs/insights_report.txt`, dashboard screenshots.

## 9. Run & expected output
`python main.py` prints cleaning stats, a category table and 9 insights, and writes 8 charts + 5 output files. `streamlit run app.py` opens the dashboard.

## 10. GitHub steps
```bash
git init
git add .
git commit -m "feat: project structure and synthetic data generator"
git branch -M main
git remote add origin https://github.com/<your-username>/Expense-Tracker-App.git
git push -u origin main
```
- **Repo name:** `Expense-Tracker-App`
- **Description:** Data science expense tracker with synthetic data, budget alerts, insights and Streamlit dashboard
- **Topics:** `data-science` `python` `pandas` `streamlit` `data-visualization` `fintech` `eda` `expense-tracker`

## 11. Day-wise proof plan
| Day | Task | Commit message |
|---|---|---|
| 1 | Setup, folders, requirements | `chore: project setup` |
| 2 | Data generator + cleaning | `feat: synthetic data and cleaning` |
| 3 | Analysis + insights | `feat: analysis, budgets, anomalies` |
| 4 | Charts + Streamlit | `feat: visualisations and dashboard` |
| 5 | README, screenshots, push | `docs: README and screenshots` |

## 12. Screenshots to capture
Dataset preview (`expenses.csv` head) · cleaning log · category table · `01_category_bar` · `02_expense_pie` · `03_monthly_income_vs_expense` · heatmap · overspending alerts · dashboard (Overview, Trends, Budget alerts tabs).

## 13. Interview preparation
1. **Explain the project.** I built a pipeline that generates/ingests expenses, cleans them, analyses category and monthly spend, flags budget breaches and shows insights in a Streamlit dashboard.
2. **Why synthetic data?** Real financial data is private. I modelled realistic behaviour (Poisson counts, normal amounts, seasonality) and injected dirty rows to practise cleaning.
3. **How did you clean it?** Stripped/title-cased text, removed duplicates, coerced dates and amounts, dropped invalid rows, engineered month/weekday features.
4. **How do you detect overspending?** Compare monthly category spend to a budget; flag and rank by % over.
5. **How do you detect anomalies?** Z-score within each category; transactions beyond 2.5 SD are flagged.
6. **Key insight?** Rent is largest, but Shopping is the largest controllable category and breaches budget most often, especially in festive months.
7. **Why Streamlit?** Pure Python, fast to build, shareable, free hosting on Streamlit Cloud.
8. **Challenges?** Inconsistent labels, missing values, ensuring Income/Expense aren't mixed in totals.
9. **Improvements?** Bank/UPI statement import, ML forecasting, alerts, database storage.
10. **Non-technical explanation?** It shows where your money goes and warns you before you overspend.

**HR version:** "I took a real-world problem, built it end to end, and documented it on GitHub." **Technical version:** pandas ETL + aggregation + z-score anomaly detection + Streamlit.

## 14. Future improvements
Mobile app · real-time logging (ESP32 buttons / UPI SMS parsing) · Prophet/ARIMA spend forecasting · budget alert emails/Telegram · savings-goal tracker · SQLite/PostgreSQL storage.

## 15. Troubleshooting
| Error | Fix |
|---|---|
| `ModuleNotFoundError: src` | Run commands from the project root folder |
| `pip` not recognised | Use `python -m pip install ...` |
| `streamlit` not recognised | Activate venv, then `python -m streamlit run app.py` |
| Charts don't pop up | They're saved to `images/` (headless mode); open the PNGs |
| `FileNotFoundError: data/expenses.csv` | Run `python main.py` first (dashboard also auto-generates data) |
| `ValueError` converting dates | Use `pd.to_datetime(..., errors="coerce")` (already in `cleaning.py`) |
| Seaborn `palette` warning | Use `hue=` with `legend=False` (already done) |
| Git push rejected | `git pull origin main --rebase` then push again |
