"""
predict.py
SevaSetu Priority AI – Inference Pipeline
"""

import pickle
import numpy as np
from pathlib import Path
from functools import lru_cache
from sentence_transformers import SentenceTransformer

BASE_DIR   = Path(__file__).parent
MODEL_PATH = BASE_DIR / "model.pkl"

# ─── Label → numeric priority score mapping ──────────────────────────────────
LABEL_SCORE_MAP = {
    "Critical": 90,
    "High":     70,
    "Medium":   45,
    "Low":      20,
}

# ─── Keyword heuristics (same as train.py) ───────────────────────────────────
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

def _keyword_score(text: str) -> dict:
    t = text.lower()
    return {
        "kw_critical": sum(1 for k in CRITICAL_KEYWORDS if k in t),
        "kw_high":     sum(1 for k in HIGH_KEYWORDS if k in t),
        "kw_medium":   sum(1 for k in MEDIUM_KEYWORDS if k in t),
        "kw_low":      sum(1 for k in LOW_KEYWORDS if k in t),
    }


# ─── Model singleton ─────────────────────────────────────────────────────────

_artifacts   = None
_embedder    = None

def _load_artifacts():
    global _artifacts, _embedder
    if _artifacts is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"model.pkl not found at {MODEL_PATH}. Run train.py first."
            )
        with open(MODEL_PATH, "rb") as f:
            _artifacts = pickle.load(f)
        _embedder = SentenceTransformer(_artifacts["embed_model_name"])
    return _artifacts, _embedder


# ─── Feature builder (mirrors train.py) ──────────────────────────────────────

def _build_single_feature(task: dict, artifacts: dict,
                           embedder: SentenceTransformer) -> np.ndarray:
    combined_text = task["task_title"] + " " + task["task_description"]

    # Embedding
    emb = embedder.encode([combined_text], normalize_embeddings=True)[0]

    # Keywords
    kw = _keyword_score(combined_text)
    kw_arr = np.array([kw["kw_critical"], kw["kw_high"],
                        kw["kw_medium"], kw["kw_low"]])

    # Categorical
    import pandas as pd
    cat_df = pd.DataFrame([{
        "task_category":     task.get("task_category", "Unknown"),
        "disaster_type":     task.get("disaster_type", "None"),
        "ngo_manual_urgency": task.get("ngo_manual_urgency", "medium"),
    }])
    cat_enc = artifacts["cat_encoder"].transform(cat_df)

    # Numerical
    deadline_hours = min(float(task.get("deadline_hours", 72)), 720)
    volunteers     = min(float(task.get("requested_volunteers_count", 3)), 30)
    created_hour   = float(task.get("created_hour", 12))
    urgency_ratio  = 1.0 / (deadline_hours + 1)
    is_night       = 1.0 if (created_hour >= 20 or created_hour <= 5) else 0.0

    num_arr = np.array([deadline_hours, volunteers, created_hour,
                         urgency_ratio, is_night])

    return np.hstack([emb, kw_arr, cat_enc[0], num_arr]).reshape(1, -1)


# ─── Public API ──────────────────────────────────────────────────────────────

def predict_priority(task_dict: dict) -> dict:
    """
    Parameters
    ----------
    task_dict : dict with keys:
        task_title, task_description, task_category, location,
        disaster_type, requested_volunteers_count,
        deadline_hours, created_hour, ngo_manual_urgency

    Returns
    -------
    dict:
        {
            "label": "Critical",          # priority class
            "score": 92.4,               # numeric 0-100
            "confidence": 0.88,          # model probability for top class
            "probabilities": {           # all class probabilities
                "Critical": 0.88,
                "High": 0.09,
                "Medium": 0.02,
                "Low": 0.01
            },
            "reasoning": "..."           # human-readable explanation
        }
    """
    artifacts, embedder = _load_artifacts()

    X = _build_single_feature(task_dict, artifacts, embedder)

    model       = artifacts["model"]
    label_enc   = artifacts["label_encoder"]
    label_order = artifacts["label_order"]

    # Predict
    pred_idx   = model.predict(X)[0]
    pred_proba = model.predict_proba(X)[0]
    label      = label_enc.inverse_transform([pred_idx])[0]

    # Build probability dict keyed by class name
    proba_dict = {
        label_enc.classes_[i]: round(float(p), 4)
        for i, p in enumerate(pred_proba)
    }

    # Numeric score: base score ± confidence shift
    base_score  = LABEL_SCORE_MAP[label]
    confidence  = float(proba_dict[label])
    score_jitter = (confidence - 0.5) * 20          # ±10 around base
    final_score  = round(float(np.clip(base_score + score_jitter, 0, 100)), 1)

    # Reasoning
    reasoning = _explain(task_dict, label, confidence)

    return {
        "label":         label,
        "score":         final_score,
        "confidence":    round(confidence, 4),
        "probabilities": proba_dict,
        "reasoning":     reasoning,
    }


def _explain(task: dict, label: str, confidence: float) -> str:
    parts = []
    text = (task.get("task_title", "") + " " + task.get("task_description", "")).lower()
    deadline = float(task.get("deadline_hours", 72))
    manual   = task.get("ngo_manual_urgency", "")
    disaster = task.get("disaster_type", "None")

    if label == "Critical":
        if deadline <= 12:
            parts.append(f"very tight deadline ({int(deadline)}h)")
        if disaster not in ("None", "", None):
            parts.append(f"active disaster context ({disaster})")
        if any(k in text for k in ["rescue", "stranded", "blood", "emergency"]):
            parts.append("life-critical keywords detected")
    elif label == "High":
        if deadline <= 48:
            parts.append(f"short deadline ({int(deadline)}h)")
        if disaster not in ("None", "", None):
            parts.append(f"disaster context ({disaster})")
    elif label == "Medium":
        if 48 <= deadline <= 120:
            parts.append(f"moderate deadline ({int(deadline)}h)")
    else:
        parts.append(f"low urgency deadline ({int(deadline)}h)")

    if manual in ("critical", "high"):
        parts.append(f"NGO flagged as {manual}")

    reason = f"Predicted {label} (confidence {confidence:.0%})"
    if parts:
        reason += " — " + "; ".join(parts) + "."
    return reason


# ─── Quick CLI test ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    samples = [
        {
            "task_title": "Urgent medical volunteers needed at flood camp tonight",
            "task_description": "Flood victims stranded. Need 3 medical volunteers immediately for triage.",
            "task_category": "Medical",
            "location": "Assam",
            "disaster_type": "Flood",
            "requested_volunteers_count": 3,
            "deadline_hours": 6,
            "created_hour": 21,
            "ngo_manual_urgency": "critical",
        },
        {
            "task_title": "Volunteers needed tomorrow for ration distribution",
            "task_description": "Need 5 organized volunteers at 8am for food distribution at relief camp.",
            "task_category": "Food & Nutrition",
            "location": "Guwahati",
            "disaster_type": "Flood",
            "requested_volunteers_count": 5,
            "deadline_hours": 20,
            "created_hour": 14,
            "ngo_manual_urgency": "high",
        },
        {
            "task_title": "Donation packaging drive this weekend",
            "task_description": "Need 6 volunteers to sort and pack hygiene kits at warehouse on Saturday.",
            "task_category": "Logistics & Transport",
            "location": "Pune",
            "disaster_type": "None",
            "requested_volunteers_count": 6,
            "deadline_hours": 96,
            "created_hour": 10,
            "ngo_manual_urgency": "medium",
        },
        {
            "task_title": "Educational material sorting next week",
            "task_description": "Need volunteer to sort donated books and label them. No urgency, flexible timing.",
            "task_category": "Education",
            "location": "Mumbai",
            "disaster_type": "None",
            "requested_volunteers_count": 1,
            "deadline_hours": 240,
            "created_hour": 11,
            "ngo_manual_urgency": "low",
        },
    ]

    print("=" * 60)
    print("SevaSetu Priority AI – Sample Predictions")
    print("=" * 60)
    for s in samples:
        result = predict_priority(s)
        print(f"\n📋 Task : {s['task_title'][:60]}")
        print(f"   Label : {result['label']}  |  Score : {result['score']}  |  Conf : {result['confidence']:.0%}")
        print(f"   {result['reasoning']}")
        print(f"   Proba : { {k: f'{v:.2f}' for k,v in result['probabilities'].items()} }")
