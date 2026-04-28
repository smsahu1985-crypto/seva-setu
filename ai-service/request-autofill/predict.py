"""
predict.py
SevaSetu Request Autofill – Inference Engine

Hybrid approach:
  1. ML models (TF-IDF + LightGBM) for categorical fields
  2. Regex / rule extractors for numeric and entity fields
  3. Confidence scores per field
"""

import re, pickle
import numpy as np
from pathlib import Path
from functools import lru_cache

BASE_DIR   = Path(__file__).parent
MODEL_PATH = BASE_DIR / "models" / "autofill_model.pkl"

# ─── Lazy singleton ──────────────────────────────────────────────────────────
_artifacts = None

def _load():
    global _artifacts
    if _artifacts is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Run: python train.py"
            )
        with open(MODEL_PATH, "rb") as f:
            _artifacts = pickle.load(f)
    return _artifacts


# ─── City / state extraction ─────────────────────────────────────────────────
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

def extract_city(text: str) -> tuple[str, float]:
    for city in CITY_STATE_MAP:
        if re.search(rf'\b{city}\b', text, re.I):
            return city, 0.95
    return "", 0.3

# ─── Number extractors ───────────────────────────────────────────────────────
def extract_people_affected(text: str) -> tuple[int, float]:
    patterns = [
        (r'(\d+)\s*(?:people|persons|survivors|residents|individuals)', 0.90),
        (r'(\d+)\s*(?:families)', 0.85),   # will multiply ×4 below
        (r'for\s+(\d+)', 0.60),
        (r'helping\s+(\d+)', 0.65),
    ]
    for pat, conf in patterns:
        m = re.search(pat, text, re.I)
        if m:
            val = int(m.group(1))
            # multiply families × 4
            if 'famil' in pat:
                val *= 4
            return val, conf
    return 0, 0.3

def extract_family_count(text: str) -> tuple[int, float]:
    m = re.search(r'(\d+)\s*(?:families|households)', text, re.I)
    if m:
        return int(m.group(1)), 0.90
    return 0, 0.3

def extract_volunteers_needed(text: str) -> tuple[int, float]:
    patterns = [
        (r'need\s+(\d+)\s+volunteer', 0.95),
        (r'(\d+)\s+volunteer', 0.90),
        (r'(\d+)\s+(?:doctors|nurses|counselors|riders|drivers|helpers|workers)', 0.85),
        (r'need\s+(\d+)\s+people', 0.70),
    ]
    for pat, conf in patterns:
        m = re.search(pat, text, re.I)
        if m:
            return int(m.group(1)), conf
    return 0, 0.3

def extract_deadline_hours(text: str) -> tuple[int, float]:
    candidates = [
        (r'within\s+(\d+)\s*hours?', lambda m: int(m.group(1)), 0.95),
        (r'in\s+(\d+)\s*hours?',     lambda m: int(m.group(1)), 0.92),
        (r'next\s+(\d+)\s*hours?',   lambda m: int(m.group(1)), 0.92),
        (r'within\s+(\d+)\s*days?',  lambda m: int(m.group(1))*24, 0.90),
        (r'in\s+(\d+)\s*days?',      lambda m: int(m.group(1))*24, 0.88),
    ]
    for pat, fn, conf in candidates:
        m = re.search(pat, text, re.I)
        if m:
            return fn(m), conf

    keyword_map = [
        (r'\btonight\b',       8,   0.85),
        (r'\bimmediately\b|\bimmediately\b|\burgently\b|\basap\b', 6, 0.80),
        (r'\btomorrow\s+morning\b', 12, 0.82),
        (r'\btomorrow\b',      24,  0.80),
        (r'\bthis\s+evening\b', 10, 0.80),
        (r'\bthis\s+weekend\b', 72, 0.75),
        (r'\bthis\s+week\b',   120, 0.70),
        (r'\bnext\s+week\b',   168, 0.70),
    ]
    for pat, hrs, conf in keyword_map:
        if re.search(pat, text, re.I):
            return hrs, conf
    return 48, 0.40

# ─── Skill extractor ─────────────────────────────────────────────────────────
SKILL_KEYWORDS = {
    "medical":           ["medical", "doctor", "nurse", "paramedic", "health", "clinical"],
    "logistics":         ["logistics", "supply", "delivery", "distribution", "transport"],
    "teaching":          ["teach", "tutor", "coach", "educate", "training", "lesson"],
    "driving":           ["bike", "car", "van", "drive", "driver", "rider", "vehicle", "transport"],
    "rescue":            ["rescue", "evacuation", "evacuate", "search and rescue", "stranded"],
    "counseling":        ["counsel", "therapy", "psycho", "mental health", "support", "trauma"],
    "packaging":         ["pack", "packaging", "kit", "bundle", "sort", "label"],
    "data_entry":        ["data entry", "documentation", "digitize", "admin", "register", "records"],
    "food_distribution": ["food", "ration", "meal", "kitchen", "cook", "nutrition", "distribute"],
    "cleanup":           ["clean", "cleanup", "sanitation", "hygiene", "sanitize"],
}

def extract_skills(text: str) -> tuple[list, float]:
    found = []
    t = text.lower()
    for skill, keywords in SKILL_KEYWORDS.items():
        if any(kw in t for kw in keywords):
            found.append(skill)
    conf = 0.85 if found else 0.3
    return found, conf

# ─── Required items extractor ────────────────────────────────────────────────
ITEM_KEYWORDS = {
    "food":              ["food", "meal", "ration", "nutrition"],
    "blankets":          ["blanket", "quilt", "bedding"],
    "medicine":          ["medicine", "drug", "medical supply", "pharmacy"],
    "water_cans":        ["water", "drinking water", "tanker"],
    "shelter":           ["shelter", "tent", "tarpaulin"],
    "warm_clothing":     ["clothing", "clothes", "warm wear", "jacket"],
    "school_supplies":   ["books", "notebook", "stationery", "school supply"],
    "first_aid":         ["first aid", "bandage", "dressing"],
    "blood_donation":    ["blood", "donor"],
    "cleaning_supplies": ["cleaning", "disinfectant", "bleach"],
    "nutrition_supplements": ["nutrition supplement", "protein", "supplement"],
}

def extract_items(text: str) -> tuple[list, float]:
    found = []
    t = text.lower()
    for item, keywords in ITEM_KEYWORDS.items():
        if any(kw in t for kw in keywords):
            found.append(item)
    return found, (0.85 if found else 0.3)

# ─── Binary flags ─────────────────────────────────────────────────────────────
def rule_flags(text: str) -> dict:
    t = text.lower()
    return {
        "is_medical_emergency": any(w in t for w in [
            "medical", "doctor", "nurse", "blood", "patient", "hospital",
            "emergency", "medicine", "paramedic", "icu", "ambulance"]),
        "is_disaster_related":  any(w in t for w in [
            "flood", "cyclone", "earthquake", "landslide", "disaster",
            "relief camp", "rescue", "evacuation", "stranded"]),
        "transport_required":   any(w in t for w in [
            "transport", "bike", "car", "van", "vehicle", "delivery",
            "drive", "driver", "rider", "pickup", "drop"]),
        "children_involved":    any(w in t for w in [
            "children", "child", "kids", "orphan", "student", "school",
            "girl", "boy", "juvenile"]),
        "elderly_involved":     any(w in t for w in [
            "elderly", "senior", "old age", "aged", "pensioner"]),
    }

# ─── Title generator ──────────────────────────────────────────────────────────
TITLE_MAP = {
    "disaster_relief":    "Disaster Relief Support",
    "food_relief":        "Food Distribution Request",
    "medical":            "Medical Assistance Request",
    "logistics":          "Logistics & Transport Help",
    "shelter":            "Shelter Support Request",
    "education":          "Education Volunteer Request",
    "elderly_care":       "Elderly Care Support",
    "mental_health":      "Mental Health Support",
    "animal_welfare":     "Animal Welfare Help",
    "cleanup":            "Cleanup Drive Request",
    "water_sanitation":   "Water & Sanitation Help",
    "fundraising":        "Fundraising Drive",
    "awareness":          "Awareness Campaign",
    "childcare":          "Childcare Support",
    "women_safety":       "Women Safety Support",
    "administration":     "Admin Volunteer Need",
}

def _make_title(category: str, city: str) -> str:
    base = TITLE_MAP.get(category, "Community Help Request")
    if city:
        return f"{base} – {city}"
    return base

# ─── Contact preference ───────────────────────────────────────────────────────
def extract_contact_preference(text: str) -> str:
    t = text.lower()
    if "whatsapp" in t: return "whatsapp"
    if "email" in t or "mail" in t: return "email"
    if "call" in t or "phone" in t: return "phone"
    return "whatsapp"   # default in India

# ─── ML prediction ───────────────────────────────────────────────────────────
def _predict_field(text: str, field: str, artifacts: dict) -> tuple[str, float]:
    vec  = artifacts["vectorizer"]
    clfs = artifacts["classifiers"]
    les  = artifacts["label_encoders"]
    if field not in clfs:
        return "", 0.0
    X     = vec.transform([text])
    proba = clfs[field].predict_proba(X)[0]
    idx   = int(np.argmax(proba))
    conf  = float(proba[idx])
    label = les[field].inverse_transform([idx])[0]
    return str(label), round(conf, 4)

def _predict_bool(text: str, field: str, artifacts: dict) -> tuple[bool, float]:
    vec  = artifacts["vectorizer"]
    bm   = artifacts["bool_models"]
    if field not in bm:
        return False, 0.0
    X     = vec.transform([text])
    proba = bm[field].predict_proba(X)[0]
    val   = bool(np.argmax(proba))
    conf  = float(max(proba))
    return val, round(conf, 4)


# ─── Main autofill function ───────────────────────────────────────────────────
def autofill(request_description: str) -> dict:
    """
    Given a free-text request description, return predicted form fields
    with per-field confidence scores.
    """
    arts  = _load()
    text  = request_description.strip()

    # ── ML categorical predictions ──
    category,     cat_conf    = _predict_field(text, "category",           arts)
    subcategory,  sub_conf    = _predict_field(text, "subcategory",        arts)
    urgency,      urg_conf    = _predict_field(text, "urgency_level",      arts)
    effort,       eff_conf    = _predict_field(text, "effort_level",       arts)
    min_exp,      exp_conf    = _predict_field(text, "min_experience_level", arts)
    shift,        shf_conf    = _predict_field(text, "shift_type",         arts)
    need_type,    nt_conf     = _predict_field(text, "need_type",          arts)

    # ── ML boolean predictions + rule fusion ──
    rule_fl = rule_flags(text)
    bool_fields = {}
    for bfield in ["is_medical_emergency", "is_disaster_related",
                   "transport_required", "children_involved", "elderly_involved"]:
        ml_val, ml_conf = _predict_bool(text, bfield, arts)
        rule_val = rule_fl.get(bfield, False)
        # OR fusion: if either rule or ML says True, use True
        fused_val  = bool(ml_val or rule_val)
        fused_conf = ml_conf if fused_val == ml_val else 0.80
        bool_fields[bfield] = {"value": fused_val, "confidence": fused_conf}

    # ── Rule-based numeric / entity extraction ──
    city,      city_conf  = extract_city(text)
    state = CITY_STATE_MAP.get(city, "")

    people,    ppl_conf   = extract_people_affected(text)
    families,  fam_conf   = extract_family_count(text)
    vols,      vol_conf   = extract_volunteers_needed(text)
    deadline,  ddl_conf   = extract_deadline_hours(text)
    skills,    skl_conf   = extract_skills(text)
    items,     itm_conf   = extract_items(text)

    # Priority from urgency
    priority_map = {"critical": "Critical", "high": "High",
                    "medium": "Medium", "low": "Low"}
    priority_label = priority_map.get(urgency, "Medium")

    # Title generation
    request_title = _make_title(category, city)

    # Contact preference
    contact_pref = extract_contact_preference(text)

    # ── Build response ──
    result = {
        # Meta
        "request_title":            request_title,
        "category":                 category,
        "subcategory":              subcategory,
        "urgency_level":            urgency,
        "priority_label":           priority_label,

        # Affected people
        "estimated_people_affected": people,
        "family_count":             families,

        # Location
        "location_city":            city,
        "location_state":           state,

        # Timing
        "deadline_hours":           deadline,

        # Skills / items
        "required_skills":          skills,
        "required_items":           items,

        # Volunteers
        "volunteers_needed":        vols,

        # Flags
        "is_medical_emergency":     bool_fields["is_medical_emergency"]["value"],
        "is_disaster_related":      bool_fields["is_disaster_related"]["value"],
        "transport_required":       bool_fields["transport_required"]["value"],

        # Contact
        "contact_preference":       contact_pref,

        # Volunteer task fields
        "task_type":                subcategory,
        "effort_level":             effort,
        "min_experience_level":     min_exp,
        "shift_type":               shift,

        # Public request fields
        "need_type":                need_type,
        "children_involved":        bool_fields["children_involved"]["value"],
        "elderly_involved":         bool_fields["elderly_involved"]["value"],

        # Confidence scores
        "confidence": {
            "category":              cat_conf,
            "subcategory":           sub_conf,
            "urgency_level":         urg_conf,
            "location_city":         city_conf,
            "deadline_hours":        ddl_conf,
            "required_skills":       skl_conf,
            "volunteers_needed":     vol_conf,
            "estimated_people_affected": ppl_conf,
            "is_medical_emergency":  bool_fields["is_medical_emergency"]["confidence"],
            "is_disaster_related":   bool_fields["is_disaster_related"]["confidence"],
            "transport_required":    bool_fields["transport_required"]["confidence"],
        },
    }

    return result


# ─── CLI test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json
    samples = [
        "Need 3 volunteers with bikes to deliver medicine in Pune tonight",
        "Flood relief needed for 50 people in Nashik, need food and blankets urgently",
        "Need urgent food packets and blankets for 20 flood affected families in Pune within next 12 hours",
        "Medical emergency in Guwahati. 30 patients need immediate attention. Doctors and nurses required within 6 hours",
        "Elderly care home in Kochi needs 5 volunteers for daily assistance and companionship",
        "Need 10 volunteer teachers for free coaching classes for underprivileged children in Delhi",
        "Blood donation drive in Hyderabad. Need 15 donors urgently today",
    ]
    for s in samples:
        print(f"\n{'='*60}")
        print(f"INPUT: {s}")
        print(f"{'─'*60}")
        result = autofill(s)
        # Print key fields
        keys = ["request_title","category","subcategory","urgency_level",
                "location_city","deadline_hours","volunteers_needed",
                "estimated_people_affected","required_skills","required_items",
                "is_medical_emergency","is_disaster_related","transport_required"]
        for k in keys:
            print(f"  {k:30s}: {result[k]}")
        print(f"  {'confidence':30s}: { {k:v for k,v in list(result['confidence'].items())[:5]} }")
