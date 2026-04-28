from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "fraud_model.pkl"

CITY_STATE = {
    "Pune": "Maharashtra",
    "Mumbai": "Maharashtra",
    "Nashik": "Maharashtra",
    "Nagpur": "Maharashtra",
    "Delhi": "Delhi",
    "Bengaluru": "Karnataka",
    "Chennai": "Tamil Nadu",
    "Kolkata": "West Bengal",
    "Hyderabad": "Telangana",
    "Jaipur": "Rajasthan",
    "Lucknow": "Uttar Pradesh",
    "Ahmedabad": "Gujarat",
    "Surat": "Gujarat",
    "Bhopal": "Madhya Pradesh",
    "Patna": "Bihar",
    "Guwahati": "Assam",
    "Kochi": "Kerala",
    "Indore": "Madhya Pradesh",
    "Visakhapatnam": "Andhra Pradesh",
    "Coimbatore": "Tamil Nadu",
}

SPAM_PHRASES = [
    "send money now",
    "wire transfer immediately",
    "click link for donation",
    "guaranteed relief",
    "100% authentic",
    "donate via upi now",
    "urgent transfer needed",
    "verify your account",
    "prize money",
    "lottery winner",
    "free gift",
    "government approved scheme",
    "send your bank details",
    "limited time offer",
    "act now or lose",
    "double your donation",
    "secret relief fund",
]

CATEGORY_ITEM_KEYWORDS = {
    "food_relief": ["food", "ration", "meal", "packet", "water"],
    "medical_aid": ["medicine", "oxygen", "first aid", "bandage", "doctor", "patient"],
    "disaster_relief": ["blanket", "tarpaulin", "shelter", "food", "water", "clothes"],
    "logistics": ["vehicle", "transport", "fuel", "delivery", "truck"],
    "shelter": ["tent", "blanket", "sleeping", "shelter", "mattress"],
    "education": ["book", "notebook", "pencil", "teacher", "uniform"],
    "elderly_care": ["elderly", "medicine", "meal", "wheelchair", "care"],
    "blood_donation": ["blood", "plasma", "donor"],
    "mental_health": ["counsel", "therapy", "support", "trauma"],
    "cleanup": ["clean", "glove", "mask", "sanitizer", "garbage"],
    "water_sanitation": ["water", "soap", "sanitation", "purification", "toilet"],
    "childcare": ["child", "toy", "clothes", "food", "book"],
    "fundraising": ["donation", "fund", "campaign", "money"],
    "animal_welfare": ["animal", "pet", "cage", "medicine", "rescue"],
    "administration": ["stationery", "laptop", "internet", "office"],
}

FEATURE_COLUMNS = [
    "request_title",
    "request_description",
    "category",
    "location_city",
    "location_state",
    "people_affected",
    "volunteers_needed",
    "required_items",
    "deadline_hours",
    "contact_phone",
    "user_type",
    "created_at_hour",
    "desc_length",
    "desc_word_count",
    "has_spam_phrase",
    "title_desc_mismatch",
    "qty_requested",
    "qty_per_person_ratio",
    "deadline_too_short",
    "is_late_night",
    "city_state_mismatch",
    "phone_suspicious",
    "repeated_words",
    "description_vague",
    "exclamation_count",
    "caps_ratio",
    "category_item_mismatch",
]


def normalize_request(payload: dict[str, Any]) -> dict[str, Any]:
    data = dict(payload)
    data.setdefault("request_title", "")
    data.setdefault("request_description", "")
    data.setdefault("category", "unknown")
    data.setdefault("location_city", "")
    data.setdefault("location_state", "")
    data.setdefault("people_affected", 1)
    data.setdefault("volunteers_needed", 0)
    data.setdefault("required_items", [])
    data.setdefault("deadline_hours", 24)
    data.setdefault("contact_phone", "")
    data.setdefault("user_type", "public")
    data.setdefault("created_at_hour", 12)
    return data


def _required_items_to_text(required_items: Any) -> str:
    if required_items is None:
        return ""
    if isinstance(required_items, list):
        return "|".join(str(item) for item in required_items)
    return str(required_items)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _has_repeated_words(text: str) -> int:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
        if counts[word] >= 3 and len(word) > 2:
            return 1
    return 0


def _extract_quantity(text: str, people_affected: int, required_items: str) -> int:
    numbers = [int(match) for match in re.findall(r"\b\d{1,7}\b", text)]
    useful_numbers = [number for number in numbers if number not in range(0, 25)]
    if useful_numbers:
        return max(useful_numbers)
    if required_items:
        return max(people_affected, 1)
    return 0


def _infer_deadline_hours(text: str, deadline_hours: int) -> int:
    text_lower = text.lower()
    minute_match = re.search(r"\b(\d{1,3})\s*(minute|minutes|min|mins)\b", text_lower)
    if minute_match and int(minute_match.group(1)) <= 90:
        return 1
    if any(phrase in text_lower for phrase in ["right now", "immediately", "send now", "asap"]):
        return min(deadline_hours, 1)
    return deadline_hours


def _title_desc_mismatch(title: str, description: str) -> int:
    title_words = {word for word in re.findall(r"[a-zA-Z]+", title.lower()) if len(word) > 3}
    desc_words = {word for word in re.findall(r"[a-zA-Z]+", description.lower()) if len(word) > 3}
    if not title_words or not desc_words:
        return 0
    overlap = len(title_words & desc_words) / max(len(title_words), 1)
    return int(overlap < 0.15)


def _category_item_mismatch(category: str, required_items: str, description: str) -> int:
    expected = CATEGORY_ITEM_KEYWORDS.get(category, [])
    if not expected or category == "unknown":
        return 0
    combined = f"{required_items} {description}".lower()
    return int(not any(keyword in combined for keyword in expected))


def engineer_features(payload: dict[str, Any]) -> dict[str, Any]:
    data = normalize_request(payload)
    title = str(data.get("request_title", ""))
    description = str(data.get("request_description", ""))
    combined_text = f"{title} {description}"
    required_items = _required_items_to_text(data.get("required_items"))
    people_affected = max(_safe_int(data.get("people_affected"), 1), 0)
    deadline_hours = _infer_deadline_hours(combined_text, _safe_int(data.get("deadline_hours"), 24))
    created_at_hour = _safe_int(data.get("created_at_hour"), 12)
    phone = re.sub(r"\D", "", str(data.get("contact_phone", "")))
    city = str(data.get("location_city", "")).strip()
    state = str(data.get("location_state", "")).strip()
    qty_requested = _extract_quantity(combined_text, people_affected, required_items)
    desc_lower = description.lower()

    data["required_items"] = required_items
    data["people_affected"] = people_affected
    data["volunteers_needed"] = _safe_int(data.get("volunteers_needed"), 0)
    data["deadline_hours"] = deadline_hours
    data["created_at_hour"] = created_at_hour
    data["desc_length"] = len(description)
    data["desc_word_count"] = len(description.split())
    data["has_spam_phrase"] = int(any(phrase in desc_lower for phrase in SPAM_PHRASES))
    data["title_desc_mismatch"] = _title_desc_mismatch(title, description)
    data["qty_requested"] = qty_requested
    data["qty_per_person_ratio"] = round(qty_requested / max(people_affected, 1), 3) if qty_requested else 0
    data["deadline_too_short"] = int(deadline_hours <= 1)
    data["is_late_night"] = int(created_at_hour < 4 or created_at_hour >= 23)
    data["city_state_mismatch"] = int(bool(city and state and CITY_STATE.get(city) and CITY_STATE[city] != state))
    data["phone_suspicious"] = int(bool(phone) and (len(phone) != 10 or len(set(phone)) <= 2 or phone in {"1234567890", "9876543210", "1234512345", "9999988888"}))
    data["repeated_words"] = _has_repeated_words(combined_text)
    data["description_vague"] = int(len(description.split()) < 6)
    data["exclamation_count"] = description.count("!")
    data["caps_ratio"] = round(sum(1 for char in description if char.isupper()) / max(len(description), 1), 3)
    data["category_item_mismatch"] = _category_item_mismatch(str(data.get("category", "")), required_items, description)

    return {column: data.get(column, "") for column in FEATURE_COLUMNS}


def rule_score(features: dict[str, Any]) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    qty = _safe_int(features.get("qty_requested"), 0)
    people = max(_safe_int(features.get("people_affected"), 1), 1)
    ratio = float(features.get("qty_per_person_ratio") or 0)
    deadline = _safe_int(features.get("deadline_hours"), 24)

    if qty >= 1000:
        score += 40
        reasons.append("Unrealistic quantity requested")
    elif ratio >= 100:
        score += 55
        reasons.append("Requested quantity too high for affected people count")
    elif ratio >= 50:
        score += 24
        reasons.append("Requested quantity too high for affected people count")

    if deadline <= 1:
        score += 25
        reasons.append("Deadline unrealistic")
    elif deadline <= 2 and qty > people * 20:
        score += 12
        reasons.append("Very short deadline for request size")

    if features.get("has_spam_phrase"):
        score += 22
        reasons.append("Repeated scam or donation language detected")
    if features.get("phone_suspicious"):
        score += 15
        reasons.append("Phone number pattern suspicious")
    if features.get("is_late_night"):
        score += 10
        reasons.append("Late-night suspicious timing")
    if features.get("city_state_mismatch"):
        score += 14
        reasons.append("City and state do not match")
    if features.get("repeated_words"):
        score += 10
        reasons.append("Repeated spam-like words detected")
    if features.get("description_vague"):
        score += 8
        reasons.append("Description is too vague for verification")
    if features.get("category_item_mismatch"):
        score += 10
        reasons.append("Category and requested items appear inconsistent")
    if float(features.get("caps_ratio") or 0) > 0.45:
        score += 7
        reasons.append("Excessive capitalized urgency language")
    if _safe_int(features.get("exclamation_count"), 0) >= 3:
        score += 6
        reasons.append("Excessive urgency punctuation")

    return min(score, 100), reasons


def load_model(model_path: Path = MODEL_PATH) -> Any | None:
    if not model_path.exists():
        return None
    try:
        return joblib.load(model_path)
    except Exception as exc:
        print(f"Warning: could not load fraud model from {model_path}: {exc}")
        return None


def risk_level(score: int) -> str:
    if score >= 90:
        return "critical"
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def recommended_action(level: str) -> str:
    return {
        "low": "approve_with_standard_checks",
        "medium": "verify_details",
        "high": "manual_review",
        "critical": "manual_review",
    }[level]


def predict_fraud(payload: dict[str, Any], model: Any | None = None) -> dict[str, Any]:
    features = engineer_features(payload)
    rules_score, reasons = rule_score(features)

    ml_score = rules_score
    model_loaded = True
    if model is None:
        model = load_model()
    if model is None:
        model_loaded = False
    else:
        frame = pd.DataFrame([features])
        probability = model["pipeline"].predict_proba(frame)[0][1]
        ml_score = int(round(probability * 100))

    final_score = max(rules_score, int(round((0.62 * rules_score) + (0.38 * ml_score))))
    if rules_score >= 85:
        final_score = max(final_score, rules_score)
    final_score = int(np.clip(final_score, 0, 100))
    level = risk_level(final_score)

    if not reasons and final_score >= 40:
        reasons.append("ML classifier found an unusual request pattern")
    if not model_loaded:
        reasons.append("Model file not found; rule-only fallback used")

    return {
        "fraud_score": final_score,
        "risk_level": level,
        "is_suspicious": final_score >= 40,
        "reasons": reasons,
        "recommended_action": recommended_action(level),
    }


def predict_batch(requests: list[dict[str, Any]], model: Any | None = None) -> list[dict[str, Any]]:
    if model is None:
        model = load_model()
    results = []
    for index, request in enumerate(requests):
        result = predict_fraud(request, model=model)
        result["index"] = index
        results.append(result)
    return sorted(results, key=lambda item: item["fraud_score"], reverse=True)


if __name__ == "__main__":
    sample = {
        "request_title": "Urgent Need for 1000 Oxygen Cylinders",
        "request_description": "Need 1000 cylinders in 30 minutes send now",
        "category": "medical_aid",
        "location_city": "Pune",
        "location_state": "Maharashtra",
        "people_affected": 5,
        "volunteers_needed": 0,
        "required_items": ["oxygen cylinders"],
        "deadline_hours": 1,
        "contact_phone": "9999999999",
        "user_type": "public",
        "created_at_hour": 3,
    }
    print(predict_fraud(sample))
