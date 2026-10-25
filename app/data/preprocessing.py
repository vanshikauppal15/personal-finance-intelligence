import pandas as pd
from app.data.validation import (
    DATE_COLUMN_ALIASES,
    DESCRIPTION_COLUMN_ALIASES,
    AMOUNT_COLUMN_ALIASES,
    DEBIT_COLUMN_ALIASES,
    CREDIT_COLUMN_ALIASES,
    _normalize_column_name,
)


class CSVPreprocessingError(Exception):
    """Raised when cleaning fails in a way that makes the data unusable."""
    pass


def _find_matching_column(df: pd.DataFrame, aliases: list[str]) -> str | None:
    """
    Given a DataFrame and a list of acceptable alias names, return the
    ACTUAL column name in df that matches one of the aliases (case-insensitive).
    Returns None if no match found.
    """
    normalized_map = {_normalize_column_name(col): col for col in df.columns}
    for alias in aliases:
        if alias in normalized_map:
            return normalized_map[alias]
    return None


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renames whatever columns were detected into our standard internal names:
    'date', 'description', 'amount'.
    Handles both single-amount-column and debit/credit-column formats.
    """
    date_col = _find_matching_column(df, DATE_COLUMN_ALIASES)
    desc_col = _find_matching_column(df, DESCRIPTION_COLUMN_ALIASES)
    amount_col = _find_matching_column(df, AMOUNT_COLUMN_ALIASES)
    debit_col = _find_matching_column(df, DEBIT_COLUMN_ALIASES)
    credit_col = _find_matching_column(df, CREDIT_COLUMN_ALIASES)

    working_df = df.copy()

    rename_map = {date_col: "date", desc_col: "description"}

    if amount_col:
        rename_map[amount_col] = "amount"
        working_df = working_df.rename(columns=rename_map)
    elif debit_col and credit_col:
        working_df = working_df.rename(columns=rename_map)
        # Debit = money out (should be negative), Credit = money in (positive)
        working_df["debit_clean"] = pd.to_numeric(working_df[debit_col], errors="coerce").fillna(0)
        working_df["credit_clean"] = pd.to_numeric(working_df[credit_col], errors="coerce").fillna(0)
        working_df["amount"] = working_df["credit_clean"] - working_df["debit_clean"]
        working_df = working_df.drop(columns=[debit_col, credit_col, "debit_clean", "credit_clean"])
    else:
        raise CSVPreprocessingError("Could not map amount columns during preprocessing.")

    return working_df[["date", "description", "amount"]]


def clean_amount_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures 'amount' is a clean float column.
    Handles currency symbols, commas, and stray whitespace if present as strings.
    """
    working_df = df.copy()

    if not pd.api.types.is_numeric_dtype(working_df["amount"]):
        working_df["amount"] = (
            working_df["amount"]
            .astype(str)
            .str.replace("₹", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

    working_df["amount"] = pd.to_numeric(working_df["amount"], errors="coerce")
    return working_df


def clean_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts the 'date' column to proper datetime objects.
    ISO-style dates (2026-01-03) are read year-first; anything else
    (05/01/2026) is read day-first, as Indian banks write them.
    Unparseable rows become NaT so we can drop them later.
    """
    working_df = df.copy()
    date_text = working_df["date"].astype(str).str.strip()

    looks_iso = date_text.str.match(r"^\d{4}-\d{2}-\d{2}")

    iso_dates = pd.to_datetime(date_text.where(looks_iso), format="ISO8601", errors="coerce")
    other_dates = pd.to_datetime(date_text.where(~looks_iso), errors="coerce", dayfirst=True)

    working_df["date"] = iso_dates.fillna(other_dates)
    return working_df

def clean_description_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strips whitespace and normalizes blank/missing descriptions to 'Unknown'.
    """
    working_df = df.copy()
    working_df["description"] = (
        working_df["description"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
        .replace("nan", "Unknown")
    )
    return working_df


def drop_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops rows where date or amount could not be parsed — these are unusable
    for downstream analysis. Also drops exact duplicate rows.
    """
    working_df = df.copy()
    before_count = len(working_df)

    working_df = working_df.dropna(subset=["date", "amount"])
    working_df = working_df.drop_duplicates()

    after_count = len(working_df)
    dropped = before_count - after_count

    return working_df, dropped


def preprocess_transactions(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Full preprocessing pipeline: map columns -> clean each column -> drop invalid rows.
    Returns the cleaned DataFrame and a small report dict (useful for user feedback later).
    """
    df = map_columns(df)
    df = clean_amount_column(df)
    df = clean_date_column(df)
    df = clean_description_column(df)
    df, dropped_count = drop_invalid_rows(df)

    df = df.sort_values("date").reset_index(drop=True)

    report = {
        "total_rows_after_cleaning": len(df),
        "rows_dropped": dropped_count,
    }

    return df, report