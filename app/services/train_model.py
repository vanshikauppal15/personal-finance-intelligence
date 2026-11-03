import os

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

DATA_PATH = "data/labeled_transactions.csv"
MODEL_PATH = "models/category_model.joblib"


def build_model():
    # TF-IDF turns text into numbers; Logistic Regression learns from them
    return make_pipeline(
        TfidfVectorizer(lowercase=True, ngram_range=(1, 2)),
        LogisticRegression(max_iter=1000),
    )


def main():
    df = pd.read_csv(DATA_PATH)
    X, y = df["Description"], df["Category"]

    # Test 1: random 80/20 split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = build_model().fit(X_train, y_train)
    pred = model.predict(X_test)
    print("Test 1 - random split accuracy:", round(accuracy_score(y_test, pred), 3))
    print(classification_report(y_test, pred, zero_division=0))

    # Test 2: hold out whole merchants the model has never seen
    held_out = df["Description"].drop_duplicates().sample(frac=0.25, random_state=1)
    is_test = df["Description"].isin(held_out)
    model2 = build_model().fit(df.loc[~is_test, "Description"], df.loc[~is_test, "Category"])
    pred2 = model2.predict(df.loc[is_test, "Description"])
    acc2 = accuracy_score(df.loc[is_test, "Category"], pred2)
    print("Test 2 - unseen merchants accuracy:", round(acc2, 3))

    # Final model: train on ALL the data, then save it
    final_model = build_model().fit(X, y)
    os.makedirs("models", exist_ok=True)
    joblib.dump(final_model, MODEL_PATH)
    print("\nSaved model to", MODEL_PATH)

    # Try it on UPI payments to names it has never seen
    samples = ["UPI/Rahul Sharma", "UPI/Amit Kumar", "UPI/Neha Gupta"]
    for text, label, probs in zip(
        samples, final_model.predict(samples), final_model.predict_proba(samples)
    ):
        print(f"{text} -> {label} (confidence {probs.max():.2f})")


if __name__ == "__main__":
    main()