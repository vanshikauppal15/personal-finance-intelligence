from app.data.validation import validate_csv_structure, CSVValidationError

try:
    df = validate_csv_structure("data/sample_transactions.csv")
    print("Validation passed!")
    print(df.head())
except CSVValidationError as e:
    print("Validation failed:", e)