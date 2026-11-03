import pandas as pd
from app.data.validation import validate_csv_structure
from app.data.preprocessing import preprocess_transactions
from app.services.categorizer import categorize_transactions

# Part 1: the whole 12-month statement, through the full pipeline
raw = validate_csv_structure("data/sample_12_months.csv")
df, report = preprocess_transactions(raw)
result = categorize_transactions(df)

print(report)
print("\nCategory source:")
print(result["category_source"].value_counts())
print("\nNeeds review:", int(result["needs_review"].sum()))
print("\nCategory counts:")
print(result["category"].value_counts())

# Part 2: descriptions the system has never seen
unseen = pd.DataFrame({
    "description": ["UPI/Amit Kumar", "Zomato Gold", "Starbucks Coffee", "Random Shop 123"],
    "amount": [-500, -300, -250, -800],
})
print("\nUnseen descriptions:")
print(categorize_transactions(unseen)[["description", "category", "category_source", "confidence", "needs_review"]])