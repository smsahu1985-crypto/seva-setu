"""
SevaSetu – Training Pipeline
Trains a LightGBM LambdaRank model for volunteer-task recommendation.

Usage:
    python train.py
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import roc_auc_score
from generate_dataset import generate_dataset, FEATURE_COLUMNS

os.makedirs("models", exist_ok=True)
os.makedirs("data", exist_ok=True)


# ─────────────────────────────────────────────
# EVALUATION UTILITIES
# ─────────────────────────────────────────────

def dcg_at_k(scores, k):
    scores = np.array(scores[:k])
    if len(scores) == 0:
        return 0.0
    gains = (2 ** scores) - 1
    discounts = np.log2(np.arange(2, len(scores) + 2))
    return float(np.sum(gains / discounts))


def ndcg_at_k(y_true_sorted_by_pred, y_true_ideal, k):
    dcg = dcg_at_k(y_true_sorted_by_pred, k)
    idcg = dcg_at_k(sorted(y_true_ideal, reverse=True), k)
    return dcg / idcg if idcg > 0 else 0.0


def precision_at_k(predicted_scores, k, threshold=60):
    topk = predicted_scores[:k]
    hits = sum(1 for s in topk if s >= threshold)
    return hits / k


def recall_at_k(predicted_scores, relevant_items_count, k, threshold=60):
    topk = predicted_scores[:k]
    hits = sum(1 for s in topk if s >= threshold)
    return hits / relevant_items_count if relevant_items_count > 0 else 0.0


def evaluate_model(model, df, feature_cols, k_values=(3, 5, 10)):
    results = {f"NDCG@{k}": [] for k in k_values}
    results.update({f"P@{k}": [] for k in k_values})
    results.update({f"R@{k}": [] for k in k_values})
    auc_scores = []

    for vol_id, group in df.groupby("volunteer_id"):
        X = group[feature_cols].values
        y_true = group["match_score"].values
        y_binary = group["relevance_label"].values

        preds = model.predict(X)
        sorted_idx = np.argsort(preds)[::-1]

        y_sorted = y_true[sorted_idx]
        y_norm = y_true / 100.0

        for k in k_values:
            y_sorted_norm = y_norm[sorted_idx]
            results[f"NDCG@{k}"].append(
                ndcg_at_k(y_sorted_norm[:k].tolist(), y_norm.tolist(), k)
            )

            results[f"P@{k}"].append(
                precision_at_k(y_sorted.tolist(), k, threshold=60)
            )

            relevant = sum(1 for s in y_true if s >= 60)

            results[f"R@{k}"].append(
                recall_at_k(y_sorted.tolist(), relevant, k, threshold=60)
            )

        if len(np.unique(y_binary)) > 1:
            auc_scores.append(roc_auc_score(y_binary, preds))

    print("\n──────────────────────────────────")
    print("  EVALUATION RESULTS")
    print("──────────────────────────────────")

    for metric, vals in results.items():
        print(f"  {metric}: {np.mean(vals):.4f}")

    if auc_scores:
        print(f"  AUC:     {np.mean(auc_scores):.4f}")

    print("──────────────────────────────────")

    return {m: float(np.mean(v)) for m, v in results.items()}


# ─────────────────────────────────────────────
# MAIN TRAINING
# ─────────────────────────────────────────────

def train():
    print("=" * 55)
    print(" SevaSetu Volunteer Recommendation – Training ")
    print("=" * 55)

    # Step 1: Load / Generate dataset
    csv_path = "data/interactions.csv"

    if not os.path.exists(csv_path):
        print("\n[1/5] Generating synthetic dataset...")
        df, _, _ = generate_dataset(
            n_volunteers=250,
            n_tasks=120,
            pairs_per_volunteer=30,
            output_csv=csv_path
        )
    else:
        print(f"\n[1/5] Loading dataset from {csv_path}")
        df = pd.read_csv(csv_path)

    print(f"Samples: {len(df):,}")
    print(f"Volunteers: {df['volunteer_id'].nunique()}")
    print(f"Score Range: {df['match_score'].min():.1f} - {df['match_score'].max():.1f}")

    # Step 2: Prepare Features
    print("\n[2/5] Preparing features...")

    feature_cols = [c for c in FEATURE_COLUMNS if c in df.columns]

    X = df[feature_cols].fillna(0).values

    # IMPORTANT FIX: convert continuous scores into integer ranking labels
    y = pd.cut(
        df["match_score"],
        bins=[0, 20, 40, 60, 80, 100],
        labels=[0, 1, 2, 3, 4],
        include_lowest=True
    ).astype(int).values

    y_bin = df["relevance_label"].values
    groups = df["volunteer_id"].values

    # Step 3: Group Split
    print("\n[3/5] Splitting train/test...")

    gss = GroupShuffleSplit(
        n_splits=1,
        test_size=0.2,
        random_state=42
    )

    train_idx, test_idx = next(gss.split(X, y, groups))

    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    groups_train = groups[train_idx]
    groups_test = groups[test_idx]

    df_test = df.iloc[test_idx].copy()

    def build_group_sizes(arr):
        _, counts = np.unique(arr, return_counts=True)
        return counts.tolist()

    group_train_sizes = build_group_sizes(groups_train)
    group_test_sizes = build_group_sizes(groups_test)

    print(f"Train Samples: {len(X_train):,}")
    print(f"Test Samples : {len(X_test):,}")

    # Step 4: Train LightGBM Ranker
    print("\n[4/5] Training LightGBM LambdaRank...")

    dtrain = lgb.Dataset(
        X_train,
        label=y_train,
        group=group_train_sizes,
        feature_name=feature_cols
    )

    dvalid = lgb.Dataset(
        X_test,
        label=y_test,
        group=group_test_sizes,
        feature_name=feature_cols,
        reference=dtrain
    )

    params = {
        "objective": "lambdarank",
        "metric": "ndcg",
        "ndcg_eval_at": [3, 5, 10],
        "boosting_type": "gbdt",
        "learning_rate": 0.05,
        "num_leaves": 63,
        "max_depth": 7,
        "min_child_samples": 10,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "lambda_l1": 0.1,
        "lambda_l2": 0.2,

        # IMPORTANT FIX
        "label_gain": [0, 1, 3, 7, 15],

        "verbosity": -1,
        "seed": 42
    }

    callbacks = [
        lgb.early_stopping(30, verbose=False),
        lgb.log_evaluation(50)
    ]

    model = lgb.train(
        params,
        dtrain,
        num_boost_round=500,
        valid_sets=[dvalid],
        callbacks=callbacks
    )

    print(f"\nBest Iteration: {model.best_iteration}")

    # Step 5: Evaluate
    print("\n[5/5] Evaluating model...")

    metrics = evaluate_model(model, df_test, feature_cols)

    # Feature Importance
    importance = pd.DataFrame({
        "feature": feature_cols,
        "importance": model.feature_importance(importance_type="gain")
    }).sort_values("importance", ascending=False)

    print("\nTop Features:")
    print(importance.head(10).to_string(index=False))

    # Save model
    model_path = "models/lgbm_ranker.pkl"
    meta_path = "models/model_meta.json"

    joblib.dump(model, model_path)

    with open(meta_path, "w") as f:
        json.dump({
            "feature_columns": feature_cols,
            "metrics": metrics,
            "best_iteration": model.best_iteration
        }, f, indent=2)

    print(f"\n✅ Model saved: {model_path}")
    print(f"✅ Meta saved : {meta_path}")
    print("\nTraining Complete.")

    return model


if __name__ == "__main__":
    train()