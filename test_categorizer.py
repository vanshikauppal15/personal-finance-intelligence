import pandas as pd
from app.services.categorizer import categorize_by_rules

labeled = pd.read_csv("data/labeled_transactions.csv")
labeled["predicted"] = labeled["Description"].apply(categorize_by_rules)

matched = labeled[labeled["predicted"] != "Uncategorized"]
wrong = matched[matched["predicted"] != matched["Category"]]

print("Total rows:          ", len(labeled))
print("Matched by rules:    ", len(matched))
print("Uncategorized:       ", len(labeled) - len(matched))
print("Wrong among matched: ", len(wrong))

print("\nWhat the rules could not categorize:")
print(labeled[labeled["predicted"] == "Uncategorized"]["Description"].value_counts())

if len(wrong):
    print("\nWrong predictions:")
    print(wrong[["Description", "Category", "predicted"]].drop_duplicates())