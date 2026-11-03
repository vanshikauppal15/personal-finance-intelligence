import re
from pathlib import Path

import joblib
import pandas as pd

# Project root = two folders above this file (app/services/categorizer.py)
MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "category_model.joblib"

# Model predictions below this confidence get flagged for the user to review
CONFIDENCE_THRESHOLD = 0.5

# Order matters: the FIRST category whose keywords match wins.
# "Education" comes before "Shopping" so "Amazon Books" is Education,
# not Shopping (plain "Amazon Pay").
CATEGORY_KEYWORDS = {
    "Income": ["salary"],
    "Rent": ["rent"],
    "Education": ["udemy", "coursera", "skillshare", "college fee", "amazon books"],
    "Food": ["swiggy", "zomato", "dominos", "chai point", "mcdonalds", "cafe coffee day"],
    "Groceries": ["dmart", "bigbasket", "blinkit", "zepto", "reliance fresh"],
    "Travel": ["uber", "ola", "rapido", "irctc", "metro", "redbus", "indian oil"],
    "Bills": ["airtel", "jio", "electricity", "dth", "fibernet"],
    "Shopping": ["amazon", "flipkart", "myntra", "ajio", "decathlon"],
    "Entertainment": ["netflix", "spotify", "bookmyshow", "pvr", "hotstar"],
    "Healthcare": ["pharmacy", "practo", "1mg", "pathlabs"],
    "Other": ["atm withdrawal", "gift shop"],
}


def _build_pattern(keywords):
    # \b means "word boundary", so "jio" matches "Jio Recharge"
    # but NOT "Ajio" (the bug we hit earlier, now prevented)
    joined = "|".join(re.escape(k) for k in keywords)
    return re.compile(r"\b(?:" + joined + r")\b", re.IGNORECASE)


_PATTERNS = {cat: _build_pattern(kws) for cat, kws in CATEGORY_KEYWORDS.items()}


def categorize_by_rules(description: str) -> str:
    """Return the first matching category, or 'Uncategorized'."""
    for category, pattern in _PATTERNS.items():
        if pattern.search(description):
            return category
    return "Uncategorized"


def add_rule_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 'category' column to a cleaned transactions DataFrame."""
    result = df.copy()
    result["category"] = result["description"].apply(categorize_by_rules)
    return result

_model = None


def _load_model():
    """Load the saved model once, then reuse it."""
    global _model
    if _model is None and MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)
    return _model


def categorize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rules first, then the ML model for whatever the rules missed.
    Adds: category, category_source, confidence, needs_review.
    """
    result = add_rule_categories(df)
    result["category_source"] = "rules"
    result["confidence"] = 1.0
    result["needs_review"] = False

    unknown = result["category"] == "Uncategorized"
    if not unknown.any():
        return result

    model = _load_model()
    if model is None:
        # No saved model found: be honest and flag these for review
        result.loc[unknown, "category"] = "Other"
        result.loc[unknown, "category_source"] = "fallback"
        result.loc[unknown, "needs_review"] = True
        return result

    probs = model.predict_proba(result.loc[unknown, "description"])
    best = probs.max(axis=1)
    result.loc[unknown, "category"] = model.classes_[probs.argmax(axis=1)]
    result.loc[unknown, "category_source"] = "model"
    result.loc[unknown, "confidence"] = best.round(2)
    result.loc[unknown, "needs_review"] = best < CONFIDENCE_THRESHOLD
    return result