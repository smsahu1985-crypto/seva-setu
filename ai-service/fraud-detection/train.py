from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, precision_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from generate_dataset import generate_dataset
from predict import FEATURE_COLUMNS, engineer_features


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "dataset.csv"
MODEL_PATH = BASE_DIR / "models" / "fraud_model.pkl"

TEXT_COLUMNS = ["request_title", "request_description", "required_items"]
CATEGORICAL_COLUMNS = ["category", "location_city", "location_state", "user_type"]
NUMERIC_COLUMNS = [
    column
    for column in FEATURE_COLUMNS
    if column not in TEXT_COLUMNS and column not in CATEGORICAL_COLUMNS and column != "contact_phone"
]


def load_or_create_dataset() -> pd.DataFrame:
    if not DATA_PATH.exists():
        generate_dataset(output_path=str(DATA_PATH))
    return pd.read_csv(DATA_PATH)


def prepare_training_frame(df: pd.DataFrame) -> pd.DataFrame:
    engineered_rows = []
    for record in df.to_dict(orient="records"):
        engineered_rows.append(engineer_features(record))
    return pd.DataFrame(engineered_rows, columns=FEATURE_COLUMNS)


def build_pipeline() -> Pipeline:
    text_features = ColumnTransformer(
        transformers=[
            ("title", TfidfVectorizer(max_features=700, ngram_range=(1, 2)), "request_title"),
            ("description", TfidfVectorizer(max_features=2200, ngram_range=(1, 2)), "request_description"),
            ("items", TfidfVectorizer(max_features=500, ngram_range=(1, 2)), "required_items"),
        ],
        remainder="drop",
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("text", text_features, TEXT_COLUMNS),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_COLUMNS,
            ),
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                NUMERIC_COLUMNS,
            ),
        ]
    )

    classifier = VotingClassifier(
        estimators=[
            (
                "logreg",
                LogisticRegression(
                    C=1.8,
                    class_weight={0: 1.0, 1: 1.35},
                    max_iter=1200,
                    random_state=42,
                ),
            ),
            (
                "rf",
                RandomForestClassifier(
                    n_estimators=220,
                    max_depth=18,
                    min_samples_leaf=2,
                    class_weight={0: 1.0, 1: 1.35},
                    random_state=42,
                    n_jobs=1,
                ),
            ),
        ],
        voting="soft",
        weights=[2, 1],
    )

    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("classifier", classifier),
        ]
    )


def train_model() -> dict:
    df = load_or_create_dataset()
    if "label" not in df.columns:
        raise ValueError("Dataset must include a 'label' column.")

    x = prepare_training_frame(df)
    y = df["label"].astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)

    probabilities = pipeline.predict_proba(x_test)[:, 1]
    threshold = 0.62
    predictions = (probabilities >= threshold).astype(int)

    metrics = {
        "threshold": threshold,
        "precision": round(float(precision_score(y_test, predictions)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
        "classification_report": classification_report(y_test, predictions, digits=4),
        "rows": int(len(df)),
        "features": FEATURE_COLUMNS,
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "metrics": metrics}, MODEL_PATH)
    return metrics


if __name__ == "__main__":
    training_metrics = train_model()
    print(f"Saved model to {MODEL_PATH}")
    print(f"Rows: {training_metrics['rows']}")
    print(f"High-risk precision: {training_metrics['precision']}")
    print(f"ROC AUC: {training_metrics['roc_auc']}")
    print(training_metrics["classification_report"])
