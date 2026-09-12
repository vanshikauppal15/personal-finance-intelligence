from app.data.validation import validate_csv_structure
from app.data.preprocessing import preprocess_transactions

df = validate_csv_structure("data/sample_transactions.csv")
cleaned_df, report = preprocess_transactions(df)

print(report)
print(cleaned_df.head())
print(cleaned_df.dtypes)