import pandas as pd

# Columns we recognize as meaning "date"
DATE_COLUMN_ALIASES = ["date", "transaction date", "txn date", "value date"]

# Columns we recognize as meaning "description"
DESCRIPTION_COLUMN_ALIASES = ["description", "narration", "remarks", "particulars"]

# Columns we recognize as meaning "amount" (single signed column)
AMOUNT_COLUMN_ALIASES = ["amount", "txn amount"]

# Columns we recognize as separate debit/credit columns
DEBIT_COLUMN_ALIASES = ["debit", "withdrawal", "debit amount"]
CREDIT_COLUMN_ALIASES = ["credit", "deposit", "credit amount"]

class CSVValidationError(Exception):
    """Raised when an uploaded CSV fails basic structural checks."""
    pass


def _normalize_column_name(col: str) -> str:
    """Lowercase and strip whitespace so 'Date ' and 'date' match the same alias."""
    return col.strip().lower()

def validate_csv_structure(file_path: str) -> pd.DataFrame:
    """
    Performs basic structural validation on an uploaded CSV file.
    Raises CSVValidationError with a clear message if the file is unusable.
    Returns the loaded DataFrame if validation passes.
    """
    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        raise CSVValidationError("The uploaded file is empty.")
    except pd.errors.ParserError:
        raise CSVValidationError("The uploaded file is not a valid CSV.")
    except UnicodeDecodeError:
        raise CSVValidationError("The file encoding is not supported. Please upload a UTF-8 encoded CSV.")

    if df.empty:
        raise CSVValidationError("The CSV file contains no data rows.")

    if len(df.columns) < 2:
        raise CSVValidationError("The CSV file does not have enough columns to be a transaction statement.")

    normalized_columns = [_normalize_column_name(c) for c in df.columns]

    has_date = any(alias in normalized_columns for alias in DATE_COLUMN_ALIASES)
    has_description = any(alias in normalized_columns for alias in DESCRIPTION_COLUMN_ALIASES)
    has_amount = any(alias in normalized_columns for alias in AMOUNT_COLUMN_ALIASES)
    has_debit_credit = (
        any(alias in normalized_columns for alias in DEBIT_COLUMN_ALIASES)
        and any(alias in normalized_columns for alias in CREDIT_COLUMN_ALIASES)
    )

    if not has_date:
        raise CSVValidationError(
            "Could not find a date column. Expected one of: " + ", ".join(DATE_COLUMN_ALIASES)
        )

    if not has_description:
        raise CSVValidationError(
            "Could not find a description column. Expected one of: " + ", ".join(DESCRIPTION_COLUMN_ALIASES)
        )

    if not (has_amount or has_debit_credit):
        raise CSVValidationError(
            "Could not find an amount column, or debit/credit columns. "
            f"Expected one of: {', '.join(AMOUNT_COLUMN_ALIASES)}, "
            f"or both a debit column ({', '.join(DEBIT_COLUMN_ALIASES)}) "
            f"and a credit column ({', '.join(CREDIT_COLUMN_ALIASES)})."
        )

    return df


