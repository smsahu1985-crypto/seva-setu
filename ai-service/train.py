"""
train.py
SevaSetu Priority AI – Training Pipeline
Hybrid: sentence-transformers (MiniLM) embeddings + structured features → LightGBM
"""

import os, pickle, warnings
import numpy as np
import pandas as pd
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (accuracy_score, f1_score,
                             classification_report, confusion_matrix)
import lightgbm as lgb

warnings.filterwarnings("ignore")

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
DATA_PATH  = BASE_DIR / "dataset.csv"
MODEL_PATH = BASE_DIR / "model.pkl"
ENC_PATH   = BASE_DIR / "encoder.pkl"

# ─── Config ──────────────────────────────────────────────────────────────────
EMBED_MODEL   = "all-MiniLM-L6-v2"   # 80 MB, fast, great quality
LABEL_ORDER   = ["Low", "Medium", "High", "Critical"]
RANDOM_STATE  = 42

# ─── Urgency keyword heuristics (boost signal) ───────────────────────────────
CRITICAL_KEYWORDS = [
    "urgent", "immediate", "emergency", "tonight", "now", "critical",
    "rescue", "stranded", "blood", "life-threatening", "dying",
    "landslide", "flood victims", "medicine delivery today",
]
HIGH_KEYWORDS = [
    "tomorrow", "shelter", "ration distribution", "water shortage",
    "this evening", "relief camp", "sanitation",
]
MEDIUM_KEYWORDS = [
    "weekend", "this week", "awareness", "community kitchen",
    "logistics", "donation packaging",
]
LOW_KEYWORDS = [
    "next week", "next month", "admin", "data entry", "social media",
    "grant", "survey", "sorting books",
]

def keyword_score(text: str) -> dict:
    t = text.lower()
    return {
        "kw_critical": sum(1 for k in CRITICAL_KEYWORDS if k in t),
        "kw_high":     sum(1 for k in HIGH_KEYWORDS if k in t),
        "kw_medium":   sum(1 for k in MEDIUM_KEYWORDS if k in t),
        "kw_low":      sum(1 for k in LOW_KEYWORDS if k in t),
    }

# ─── Feature engineering ─────────────────────────────────────────────────────

def build_features(df: pd.DataFrame,
                   embedder: SentenceTransformer,
                   cat_encoder: OrdinalEncoder,
                   fit_encoder: bool = False) -> np.ndarray:
    """
    Returns X matrix:
      - 384-dim MiniLM embeddings of (title + description)
      - 4 keyword heuristic scores
      - categorical ordinal encodings
      - numerical features
      - deadline urgency ratio
    """

    # 1. Text embeddings
    combined_text = (df["task_title"] + " " + df["task_description"]).tolist()
    print("  Encoding text embeddings …")
    emb = embedder.encode(combined_text, batch_size=64,
                          show_progress_bar=True, normalize_embeddings=True)

    # 2. Keyword heuristic scores
    kw_feats = pd.DataFrame([keyword_score(t) for t in combined_text])

    # 3. Categorical features
    cat_cols = ["task_category", "disaster_type", "ngo_manual_urgency"]
    if fit_encoder:
        cat_enc_data = cat_encoder.fit_transform(df[cat_cols].fillna("Unknown"))
    else:
        cat_enc_data = cat_encoder.transform(df[cat_cols].fillna("Unknown"))

    # 4. Numerical + engineered features
    deadline_hours = df["deadline_hours"].clip(upper=720).values
    volunteers     = df["requested_volunteers_count"].clip(upper=30).values
    created_hour   = df["created_hour"].values

    # Urgency ratio: lower deadline → higher urgency
    urgency_ratio = 1.0 / (deadline_hours + 1)

    # Night-time created (more likely emergency)
    is_night = ((created_hour >= 20) | (created_hour <= 5)).astype(int)

    num_feats = np.column_stack([
        deadline_hours,
        volunteers,
        created_hour,
        urgency_ratio,
        is_night,
    ])

    X = np.hstack([emb, kw_feats.values, cat_enc_data, num_feats])
    return X


# ─── Main training ────────────────────────────────────────────────────────────

def train():
    # ── Load data ──
    if not DATA_PATH.exists():
        print("Dataset not found. Generating …")
        from generate_dataset import generate_dataset
        generate_dataset(output_path=str(DATA_PATH))

    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows")
    print(df["priority_label"].value_counts(), "\n")

    # ── Label encoding ──
    label_enc = LabelEncoder()
    label_enc.fit(LABEL_ORDER)
    y = label_enc.transform(df["priority_label"])

    # ── Build feature matrix ──
    embedder    = SentenceTransformer(EMBED_MODEL)
    cat_encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)

    X = build_features(df, embedder, cat_encoder, fit_encoder=True)
    print(f"\nFeature matrix shape: {X.shape}")

    # ── Train / test split ──
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, stratify=y, random_state=RANDOM_STATE
    )

    # ── LightGBM ──
    print("\nTraining LightGBM …")
    model = lgb.LGBMClassifier(
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=63,
        max_depth=8,
        min_child_samples=10,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=0.1,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=-1,
    )

    # 5-fold cross-val for confidence
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv,
                                 scoring="f1_macro", n_jobs=-1)
    print(f"5-Fold CV F1 (macro): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Final fit on full training set
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        callbacks=[lgb.early_stopping(50, verbose=False),
                   lgb.log_evaluation(period=100)],
    )

    # ── Evaluate ──
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1  = f1_score(y_test, y_pred, average="macro")

    print(f"\n{'='*50}")
    print(f"Test Accuracy : {acc:.4f}")
    print(f"Test F1 Macro : {f1:.4f}")
    print(f"{'='*50}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred,
                                 target_names=label_enc.classes_))
    print("Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    cm_df = pd.DataFrame(cm,
                          index=[f"True_{c}" for c in label_enc.classes_],
                          columns=[f"Pred_{c}" for c in label_enc.classes_])
    print(cm_df)

    # ── Feature importance ──
    n_emb = 384
    feat_names = (
        [f"emb_{i}" for i in range(n_emb)]
        + ["kw_critical", "kw_high", "kw_medium", "kw_low"]
        + ["cat_category", "cat_disaster", "cat_manual_urgency"]
        + ["deadline_hours", "volunteers_count", "created_hour",
           "urgency_ratio", "is_night"]
    )
    importance = model.feature_importances_
    non_emb_mask = [i for i, n in enumerate(feat_names) if not n.startswith("emb_")]
    imp_df = pd.DataFrame({
        "feature": [feat_names[i] for i in non_emb_mask],
        "importance": importance[non_emb_mask],
    }).sort_values("importance", ascending=False)

    print("\nTop Non-Embedding Feature Importances:")
    print(imp_df.head(12).to_string(index=False))

    # ── Save ──
    artifacts = {
        "model":        model,
        "label_encoder": label_enc,
        "cat_encoder":  cat_encoder,
        "embed_model_name": EMBED_MODEL,
        "label_order":  LABEL_ORDER,
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(artifacts, f)
    print(f"\n✅  Model saved → {MODEL_PATH}")

    # Keep embedder separate for fast reload
    with open(ENC_PATH, "wb") as f:
        pickle.dump({"embedder_name": EMBED_MODEL}, f)
    print(f"✅  Encoder info saved → {ENC_PATH}")


if __name__ == "__main__":
    train()
