import random
from datetime import date, timedelta
import pandas as pd

random.seed(7)

# category: (description templates, (min amount, max amount))
SPEND = {
    "Food": (["Swiggy Order", "Zomato Order", "Dominos Pizza", "Chai Point",
              "McDonalds", "UPI/SWIGGY/okicici", "Cafe Coffee Day"], (120, 650)),
    "Groceries": (["DMart Groceries", "BigBasket Order", "Blinkit", "Zepto",
                   "Reliance Fresh", "UPI/BLINKIT/paytm"], (200, 2200)),
    "Travel": (["Uber Ride", "Ola Cabs", "Rapido Bike", "IRCTC Ticket",
                "Metro Card Recharge", "Redbus Booking", "Indian Oil Fuel"], (60, 1800)),
    "Bills": (["Airtel Postpaid", "Jio Recharge", "Electricity Bill BESCOM",
               "Tata Sky DTH", "ACT Fibernet Broadband"], (250, 1600)),
    "Shopping": (["Amazon Pay", "Flipkart Order", "Myntra Fashion",
                  "Ajio Retail", "Decathlon"], (300, 3500)),
    "Entertainment": (["Netflix Subscription", "Spotify Premium", "BookMyShow",
                       "PVR Cinemas", "Hotstar"], (120, 900)),
    "Healthcare": (["Apollo Pharmacy", "Practo Consultation", "1mg Medicines",
                    "Dr Lal Pathlabs"], (150, 2500)),
    "Education": (["Udemy Course", "Coursera Subscription", "Skillshare",
                   "College Fee Payment", "Amazon Books"], (300, 4000)),
    "Other": (["ATM Withdrawal", "UPI/Rahul Sharma", "UPI/Priya Verma",
               "Gift Shop"], (100, 3000)),
}

rows = []


def add(day, description, amount, category):
    rows.append({
        "Date": day.isoformat(),
        "Description": description,
        "Amount": round(amount, 2),
        "Transaction Type": "Credit" if amount > 0 else "Debit",
        "Category": category,
    })


day = date(2025, 11, 1)
end = date(2026, 10, 31)
while day <= end:
    if day.day == 1:
        add(day, "Salary Credit", 55000, "Income")
    if day.day == 5:
        add(day, "NEFT Rent Payment", -15000, "Rent")
    for _ in range(random.choices([0, 1, 2, 3], weights=[2, 4, 3, 1])[0]):
        category = random.choice(list(SPEND))
        names, (low, high) = SPEND[category]
        add(day, random.choice(names), -random.uniform(low, high), category)
    day += timedelta(days=1)

# Two deliberately unusual transactions for Phase 4 to find
add(date(2026, 3, 14), "Amazon Pay", -28500, "Shopping")
add(date(2026, 7, 22), "Apollo Pharmacy", -19800, "Healthcare")

df = pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)
df.to_csv("data/labeled_transactions.csv", index=False)
df.drop(columns="Category").to_csv("data/sample_12_months.csv", index=False)

print(len(df), "rows written")
print(df["Category"].value_counts())