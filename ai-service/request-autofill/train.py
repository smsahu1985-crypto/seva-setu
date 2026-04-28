"""
train.py
SevaSetu Request Autofill – Training Pipeline

Architecture:
  TF-IDF (char + word ngrams) → multi-output LightGBM / Logistic classifiers
  One model per output field.
  Fast, accurate, fully local, no GPU required.
"""

import pickle, warnings
import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
import lightgbm as lgb

warnings.filterwarnings("ignore")

BASE_DIR   = Path(__file__).parent
DATA_PATH  = BASE_DIR / "data" / "dataset.csv"
MODEL_PATH = BASE_DIR / "models" / "autofill_model.pkl"
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

# ─── Numeric extraction helpers ──────────────────────────────────────────────
import re

def extract_number(text: str, default: int = 0) -> int:
    nums = re.findall(r'\b(\d+)\b', text)
    # heuristic: first "large" number for people, first small for volunteers
    ints = [int(x) for x in nums if int(x) > 0]
    return ints[0] if ints else default

def extract_people(text: str) -> int:
    patterns = [
        r'(\d+)\s*(?:people|persons|survivors|families|residents)',
        r'(?:for|helping|support)\s+(\d+)',
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m: return int(m.group(1))
    return 0

def extract_volunteers(text: str) -> int:
    patterns = [
        r'need\s+(\d+)\s+volunteer',
        r'(\d+)\s+volunteer',
        r'(\d+)\s+(?:doctors|nurses|counselors|riders|drivers)',
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m: return int(m.group(1))
    return 0

def extract_deadline(text: str) -> int:
    patterns = [
        (r'within\s+(\d+)\s*hours?', 1),
        (r'in\s+(\d+)\s*hours?', 1),
        (r'next\s+(\d+)\s*hours?', 1),
        (r'within\s+(\d+)\s*days?', 24),
        (r'in\s+(\d+)\s*days?', 24),
        (r'tonight|tonight', 8),
        (r'tomorrow', 24),
        (r'this\s+weekend', 72),
        (r'this\s+week', 120),
        (r'next\s+week', 168),
        (r'urgently|immediately|asap', 6),
    ]
    for pat, mult in patterns:
        if isinstance(mult, int) and mult in (8, 24, 72, 120, 168, 6):
            m = re.search(pat, text, re.I)
            if m: return mult
        else:
            m = re.search(pat, text, re.I)
            if m:
                try:    return int(m.group(1)) * mult
                except: return mult
    return 48

def extract_city(text: str) -> str:
    cities = [
        "Pune", "Mumbai", "Nashik", "Nagpur", "Delhi", "Bengaluru", "Bangalore",
        "Chennai", "Kolkata", "Hyderabad", "Jaipur", "Lucknow", "Ahmedabad",
        "Surat", "Bhopal", "Patna", "Guwahati", "Kochi", "Coimbatore",
        "Indore", "Visakhapatnam",
    ]
    for city in cities:
        if re.search(rf'\b{city}\b', text, re.I):
            return city.capitalize()
    return ""

CITY_STATE_MAP = {
    "Pune": "Maharashtra", "Mumbai": "Maharashtra", "Nashik": "Maharashtra",
    "Nagpur": "Maharashtra", "Delhi": "Delhi", "Bengaluru": "Karnataka",
    "Bangalore": "Karnataka", "Chennai": "Tamil Nadu", "Kolkata": "West Bengal",
    "Hyderabad": "Telangana", "Jaipur": "Rajasthan", "Lucknow": "Uttar Pradesh",
    "Ahmedabad": "Gujarat", "Surat": "Gujarat", "Bhopal": "Madhya Pradesh",
    "Patna": "Bihar", "Guwahati": "Assam", "Kochi": "Kerala",
    "Coimbatore": "Tamil Nadu", "Indore": "Madhya Pradesh",
    "Visakhapatnam": "Andhra Pradesh",
}


# ─── Target columns we train classifiers for ─────────────────────────────────
CLF_TARGETS = [
    "category", "subcategory", "urgency_level", "effort_level",
    "min_experience_level", "shift_type", "need_type",
]

BOOL_TARGETS = [
    "is_medical_emergency", "is_disaster_related", "transport_required",
    "children_involved", "elderly_involved",
]

# ─── TF-IDF vectorizer ───────────────────────────────────────────────────────
def build_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 3),
        max_features=15000,
        sublinear_tf=True,
        strip_accents="unicode",
        min_df=2,
    )


# ─── Train one LightGBM classifier ───────────────────────────────────────────
def train_lgbm(X_train, y_train, X_test, y_test, label: str):
    le = LabelEncoder()
    y_tr = le.fit_transform(y_train)
    y_te = le.transform(y_test)

    n_classes = len(le.classes_)
    obj = "binary" if n_classes == 2 else "multiclass"
    metric = "binary_logloss" if n_classes == 2 else "multi_logloss"

    model = lgb.LGBMClassifier(
        n_estimators=200, learning_rate=0.1, num_leaves=31,
        class_weight="balanced", random_state=42, verbose=-1,
        objective=obj, metric=metric,
    )
    model.fit(X_train, y_tr,
              eval_set=[(X_test, y_te)],
              callbacks=[lgb.early_stopping(30, verbose=False)])

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_te, y_pred)
    f1  = f1_score(y_te, y_pred, average="macro", zero_division=0)
    print(f"  [{label}]  acc={acc:.3f}  f1={f1:.3f}  classes={list(le.classes_)}")
    return model, le


def train_logistic(X_train, y_train, X_test, y_test, label: str):
    """Logistic for boolean targets (0/1)."""
    model = LogisticRegression(max_iter=500, class_weight="balanced",
                               C=1.0, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"  [{label}]  acc={acc:.3f}")
    return model


# ─── Main ─────────────────────────────────────────────────────────────────────
def train():
    if not DATA_PATH.exists():
        print("Dataset not found – generating …")
        from generate_dataset import generate_dataset
        generate_dataset(output_path=str(DATA_PATH))

    df = pd.read_csv(DATA_PATH).fillna("")
    print(f"Loaded {len(df)} rows\n")

    texts = df["request_description"].tolist()

    # ── Vectorise ──
    print("Fitting TF-IDF …")
    vec = build_vectorizer()
    X   = vec.fit_transform(texts)

    X_tr, X_te, idx_tr, idx_te = train_test_split(
        range(len(texts)), range(len(texts)),
        test_size=0.15, random_state=42
    )
    # Rebuild using sklearn split on matrix
    from sklearn.model_selection import train_test_split as tts
    X_train, X_test = X[list(range(len(texts)))[:int(len(texts)*0.85)]], \
                      X[list(range(len(texts)))[int(len(texts)*0.85):]]
    df_train = df.iloc[:int(len(df)*0.85)].reset_index(drop=True)
    df_test  = df.iloc[int(len(df)*0.85):].reset_index(drop=True)

    classifiers = {}
    label_encoders = {}

    # ── Categorical classifiers ──
    print("\nTraining categorical classifiers …")
    for col in CLF_TARGETS:
        if col not in df.columns:
            continue
        y_tr = df_train[col].astype(str).tolist()
        y_te = df_test[col].astype(str).tolist()
        if len(set(y_tr)) < 2:
            continue
        model, le = train_lgbm(X_train, y_tr, X_test, y_te, col)
        classifiers[col]    = model
        label_encoders[col] = le

    # ── Boolean classifiers ──
    print("\nTraining boolean classifiers …")
    bool_models = {}
    for col in BOOL_TARGETS:
        if col not in df.columns:
            continue
        y_tr = df_train[col].astype(int).tolist()
        y_te = df_test[col].astype(int).tolist()
        if len(set(y_tr)) < 2:
            continue
        model = train_logistic(X_train, y_tr, X_test, y_te, col)
        bool_models[col] = model

    # ── Save ──
    artifacts = {
        "vectorizer":     vec,
        "classifiers":    classifiers,
        "label_encoders": label_encoders,
        "bool_models":    bool_models,
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(artifacts, f)
    print(f"\n✅  Model saved → {MODEL_PATH}")


if __name__ == "__main__":
    train()
