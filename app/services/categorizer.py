import re

import pandas as pd

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