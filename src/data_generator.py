"""Phase 2: Create a realistic SYNTHETIC expense dataset.

Why synthetic?  Real bank data is private.  We simulate one user's finances
for 12 months with: fixed monthly items (salary, rent, bills), random daily
spending (food, transport, shopping...), seasonal spikes (festival shopping,
travel in holiday months) and a few deliberately "dirty" rows so the cleaning
step has real work to do.
"""
import numpy as np
import pandas as pd

# category -> (avg transactions/month, mean amount, std amount, payment-method weights)
CATEGORIES = {
    "Food":          (22, 280, 120, {"UPI": .55, "Card": .25, "Cash": .20}),
    "Transport":     (14, 180,  90, {"UPI": .60, "Card": .10, "Cash": .30}),
    "Shopping":      (4,  1800, 900, {"Card": .55, "UPI": .40, "Cash": .05}),
    "Entertainment": (4,  550, 250, {"UPI": .50, "Card": .45, "Cash": .05}),
    "Health":        (1.5, 900, 500, {"UPI": .50, "Card": .30, "Cash": .20}),
    "Education":     (1,  1500, 600, {"UPI": .60, "Card": .40}),
}
# Month-specific multipliers: simulate trends and spikes
SEASONALITY = {
    "Shopping":      {10: 1.8, 11: 1.6, 12: 1.4},   # festive season
    "Entertainment": {5: 1.3, 6: 1.4, 12: 1.5},
    "Transport":     {5: 1.5, 6: 1.5, 12: 1.4},     # travel months
    "Health":        {1: 1.5, 2: 1.4},
}
MONTHLY_BUDGET = {  # used later for overspending detection
    "Food": 7000, "Transport": 3000, "Shopping": 5000,
    "Entertainment": 2500, "Health": 1500, "Education": 2000,
    "Rent": 12000, "Bills": 3500, "Subscriptions": 700,
}


def _pick(rng, weights):
    return rng.choice(list(weights), p=np.array(list(weights.values())) / sum(weights.values()))


def generate_expenses(year: int = 2024, seed: int = 42, dirty: bool = True) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for month in range(1, 13):
        days = pd.Period(f"{year}-{month:02d}").days_in_month
        # ---- fixed monthly income / expenses ----
        rows.append((f"{year}-{month:02d}-01", "Salary", "Monthly salary", 55000, "Income", "Bank Transfer"))
        if month in (3, 9):
            rows.append((f"{year}-{month:02d}-15", "Salary", "Performance bonus", 8000, "Income", "Bank Transfer"))
        rows.append((f"{year}-{month:02d}-02", "Rent", "House rent", 12000, "Expense", "Bank Transfer"))
        rows.append((f"{year}-{month:02d}-05", "Subscriptions", "OTT + music", 649, "Expense", "Card"))
        rows.append((f"{year}-{month:02d}-{rng.integers(8, 12):02d}", "Bills", "Electricity bill",
                     int(rng.normal(1300, 250) * (1.5 if month in (4, 5, 6) else 1)), "Expense", "UPI"))
        rows.append((f"{year}-{month:02d}-12", "Bills", "Internet + mobile", 999, "Expense", "UPI"))
        # ---- variable daily spending ----
        for cat, (n_tx, mu, sd, pay) in CATEGORIES.items():
            mult = SEASONALITY.get(cat, {}).get(month, 1.0)
            n = max(1, rng.poisson(n_tx))
            for _ in range(n):
                day = int(rng.integers(1, days + 1))
                amt = max(30, rng.normal(mu * mult, sd))
                rows.append((f"{year}-{month:02d}-{day:02d}", cat, f"{cat} expense",
                             round(float(amt)), "Expense", _pick(rng, pay)))
    df = pd.DataFrame(rows, columns=["Date", "Category", "Description", "Amount", "Type", "Payment_Method"])

    if dirty:  # inject realistic data-quality problems
        idx = rng.choice(df.index, 12, replace=False)
        df.loc[idx[:4], "Category"] = df.loc[idx[:4], "Category"].str.lower()          # casing
        df.loc[idx[4:6], "Category"] = " " + df.loc[idx[4:6], "Category"] + " "         # spaces
        df.loc[idx[6:8], "Amount"] = np.nan                                              # missing
        df.loc[idx[8], "Date"] = "not a date"                                            # bad date
        df = pd.concat([df, df.sample(5, random_state=seed)], ignore_index=True)        # duplicates
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


if __name__ == "__main__":
    out = generate_expenses()
    out.to_csv("data/expenses.csv", index=False)
    print(out.head(), f"\nSaved {len(out)} rows")
