"""
generate_dataset.py
SevaSetu Request Autofill – Synthetic Dataset Generator
3000+ realistic Indian NGO / community help request rows
"""

import random, json
import pandas as pd
import numpy as np
from pathlib import Path

random.seed(42)
np.random.seed(42)

# ─── Geography ───────────────────────────────────────────────────────────────
CITIES_STATES = {
    "Pune": "Maharashtra", "Mumbai": "Maharashtra", "Nashik": "Maharashtra",
    "Nagpur": "Maharashtra", "Delhi": "Delhi", "Bengaluru": "Karnataka",
    "Chennai": "Tamil Nadu", "Kolkata": "West Bengal", "Hyderabad": "Telangana",
    "Jaipur": "Rajasthan", "Lucknow": "Uttar Pradesh", "Ahmedabad": "Gujarat",
    "Surat": "Gujarat", "Bhopal": "Madhya Pradesh", "Patna": "Bihar",
    "Guwahati": "Assam", "Kochi": "Kerala", "Coimbatore": "Tamil Nadu",
    "Indore": "Madhya Pradesh", "Visakhapatnam": "Andhra Pradesh",
}
CITIES = list(CITIES_STATES.keys())

# ─── Template bank ───────────────────────────────────────────────────────────
# Each template: (text_fn, expected_fields_dict)

TEMPLATES = []

def T(fn, fields): 
    TEMPLATES.append((fn, fields))

# ── DISASTER RELIEF ──────────────────────────────────────────────────────────
T(lambda c,n,h: f"Flood relief needed for {n} people in {c}, need food and blankets urgently within {h} hours",
  lambda c,n,h: dict(category="disaster_relief", subcategory="flood_relief", location_city=c,
                     estimated_people_affected=n, urgency_level="critical", deadline_hours=h,
                     required_items=["food","blankets"], is_disaster_related=True,
                     transport_required=True, need_type="disaster_relief"))

T(lambda c,n,h: f"Cyclone affected {n} families in {c} need immediate shelter and food. Urgent help needed in {h} hours",
  lambda c,n,h: dict(category="disaster_relief", subcategory="cyclone_relief", location_city=c,
                     estimated_people_affected=n*4, urgency_level="critical", deadline_hours=h,
                     family_count=n, required_items=["food","shelter","blankets"],
                     is_disaster_related=True, transport_required=True))

T(lambda c,n,h: f"Earthquake relief camp in {c}. {n} survivors need medical aid and food within {h} hours",
  lambda c,n,h: dict(category="disaster_relief", subcategory="earthquake_relief", location_city=c,
                     estimated_people_affected=n, urgency_level="critical", deadline_hours=h,
                     required_items=["food","medicine","first_aid"], is_disaster_related=True,
                     is_medical_emergency=True, transport_required=True))

T(lambda c,n,h: f"Landslide in {c} has displaced {n} people. Need rescue and relief within {h} hours",
  lambda c,n,h: dict(category="disaster_relief", subcategory="rescue_operation", location_city=c,
                     estimated_people_affected=n, urgency_level="critical", deadline_hours=h,
                     required_skills=["rescue","driving"], is_disaster_related=True,
                     transport_required=True))

# ── FOOD & NUTRITION ─────────────────────────────────────────────────────────
T(lambda c,n,h: f"Need {n} volunteers for food distribution in {c} tomorrow morning",
  lambda c,n,h: dict(category="food_relief", subcategory="food_distribution", location_city=c,
                     volunteers_needed=n, urgency_level="high", deadline_hours=24,
                     required_skills=["food_distribution","logistics"], shift_type="morning"))

T(lambda c,n,h: f"Ration distribution for {n} poor families in {c}. Need volunteers in {h} hours",
  lambda c,n,h: dict(category="food_relief", subcategory="ration_distribution", location_city=c,
                     family_count=n, estimated_people_affected=n*4,
                     volunteers_needed=max(2,n//20), urgency_level="high", deadline_hours=h,
                     required_items=["ration_packets"]))

T(lambda c,n,h: f"Community kitchen in {c} needs {n} volunteers to cook meals for homeless people",
  lambda c,n,h: dict(category="food_relief", subcategory="community_kitchen", location_city=c,
                     volunteers_needed=n, urgency_level="medium", deadline_hours=48,
                     required_skills=["food_distribution"], shift_type="any"))

T(lambda c,n,h: f"Urgent: {n} malnourished children in {c} need food supplements and nutrition support",
  lambda c,n,h: dict(category="food_relief", subcategory="nutrition_support", location_city=c,
                     estimated_people_affected=n, urgency_level="high", deadline_hours=h,
                     children_involved=True, required_items=["nutrition_supplements","food"]))

# ── MEDICAL ──────────────────────────────────────────────────────────────────
T(lambda c,n,h: f"Medical emergency in {c}. {n} patients need immediate attention. Doctors and nurses required within {h} hours",
  lambda c,n,h: dict(category="medical", subcategory="emergency_medical", location_city=c,
                     estimated_people_affected=n, urgency_level="critical", deadline_hours=h,
                     is_medical_emergency=True, required_skills=["medical"],
                     volunteers_needed=max(2,n//5)))

T(lambda c,n,h: f"Need {n} blood donors urgently in {c}. Patient in critical condition",
  lambda c,n,h: dict(category="medical", subcategory="blood_donation", location_city=c,
                     volunteers_needed=n, urgency_level="critical", deadline_hours=6,
                     is_medical_emergency=True, required_items=["blood_donation"],
                     need_type="blood_donation"))

T(lambda c,n,h: f"Free medical camp in {c} needs {n} volunteer doctors and paramedics this weekend",
  lambda c,n,h: dict(category="medical", subcategory="medical_camp", location_city=c,
                     volunteers_needed=n, urgency_level="medium", deadline_hours=72,
                     required_skills=["medical"], shift_type="weekend",
                     min_experience_level="experienced"))

T(lambda c,n,h: f"Medicine delivery needed for {n} elderly patients in {c} within {h} hours. Bike riders needed",
  lambda c,n,h: dict(category="logistics", subcategory="medicine_delivery", location_city=c,
                     estimated_people_affected=n, urgency_level="high", deadline_hours=h,
                     transport_required=True, is_medical_emergency=True,
                     required_skills=["driving","logistics"], required_items=["medicine"],
                     elderly_involved=True))

T(lambda c,n,h: f"Need {n} volunteers to assist in COVID vaccination drive in {c}",
  lambda c,n,h: dict(category="medical", subcategory="vaccination_drive", location_city=c,
                     volunteers_needed=n, urgency_level="medium", deadline_hours=48,
                     required_skills=["medical","logistics"]))

# ── LOGISTICS & TRANSPORT ────────────────────────────────────────────────────
T(lambda c,n,h: f"Need {n} volunteers with bikes to deliver medicine in {c} tonight",
  lambda c,n,h: dict(category="logistics", subcategory="medicine_delivery", location_city=c,
                     volunteers_needed=n, urgency_level="high", deadline_hours=8,
                     transport_required=True, is_medical_emergency=True,
                     required_skills=["driving","logistics"], shift_type="evening"))

T(lambda c,n,h: f"Relief materials stuck at warehouse in {c}. Need {n} transport volunteers with vehicles within {h} hours",
  lambda c,n,h: dict(category="logistics", subcategory="relief_transport", location_city=c,
                     volunteers_needed=n, urgency_level="high", deadline_hours=h,
                     transport_required=True, required_skills=["driving","logistics"]))

T(lambda c,n,h: f"Need {n} car/van volunteers to transport elderly people to hospital in {c}",
  lambda c,n,h: dict(category="logistics", subcategory="patient_transport", location_city=c,
                     volunteers_needed=n, urgency_level="high", deadline_hours=12,
                     transport_required=True, elderly_involved=True,
                     required_skills=["driving"], is_medical_emergency=True))

# ── SHELTER ──────────────────────────────────────────────────────────────────
T(lambda c,n,h: f"Need to set up temporary shelter for {n} displaced families in {c}. Volunteers needed urgently",
  lambda c,n,h: dict(category="shelter", subcategory="temporary_shelter", location_city=c,
                     family_count=n, estimated_people_affected=n*4,
                     volunteers_needed=max(3,n//5), urgency_level="high", deadline_hours=h,
                     required_items=["tarpaulin","blankets"], is_disaster_related=True))

T(lambda c,n,h: f"Winter clothing and blankets needed for {n} homeless people in {c}",
  lambda c,n,h: dict(category="shelter", subcategory="winter_relief", location_city=c,
                     estimated_people_affected=n, urgency_level="medium", deadline_hours=48,
                     required_items=["blankets","warm_clothing"]))

# ── EDUCATION ────────────────────────────────────────────────────────────────
T(lambda c,n,h: f"Need {n} volunteer teachers for free coaching classes for underprivileged children in {c}",
  lambda c,n,h: dict(category="education", subcategory="tutoring", location_city=c,
                     volunteers_needed=n, urgency_level="low", deadline_hours=168,
                     required_skills=["teaching"], children_involved=True,
                     min_experience_level="regular", shift_type="any"))

T(lambda c,n,h: f"Distributing school supplies to {n} children in {c}. Need {max(2,n//30)} volunteers",
  lambda c,n,h: dict(category="education", subcategory="supplies_distribution", location_city=c,
                     estimated_people_affected=n, children_involved=True,
                     volunteers_needed=max(2,n//30), urgency_level="low", deadline_hours=72,
                     required_items=["school_supplies","books"]))

# ── ELDERLY CARE ─────────────────────────────────────────────────────────────
T(lambda c,n,h: f"Need {n} volunteers to visit and assist {n*3} elderly people living alone in {c}",
  lambda c,n,h: dict(category="elderly_care", subcategory="home_visits", location_city=c,
                     volunteers_needed=n, urgency_level="medium", deadline_hours=72,
                     elderly_involved=True, required_skills=["counseling"],
                     estimated_people_affected=n*3))

T(lambda c,n,h: f"Elderly care home in {c} needs {n} volunteers for daily assistance and companionship",
  lambda c,n,h: dict(category="elderly_care", subcategory="care_home_support", location_city=c,
                     volunteers_needed=n, urgency_level="medium", deadline_hours=48,
                     elderly_involved=True, required_skills=["counseling","medical"],
                     shift_type="any"))

# ── MENTAL HEALTH / COUNSELING ───────────────────────────────────────────────
T(lambda c,n,h: f"Trauma counseling needed for {n} disaster survivors in {c}. Need certified counselors",
  lambda c,n,h: dict(category="mental_health", subcategory="trauma_counseling", location_city=c,
                     estimated_people_affected=n, urgency_level="high", deadline_hours=h,
                     required_skills=["counseling"], min_experience_level="experienced",
                     is_disaster_related=True))

T(lambda c,n,h: f"Mental health awareness camp in {c} needs {n} volunteer counselors this weekend",
  lambda c,n,h: dict(category="mental_health", subcategory="awareness_camp", location_city=c,
                     volunteers_needed=n, urgency_level="low", deadline_hours=72,
                     required_skills=["counseling","teaching"], shift_type="weekend"))

# ── ANIMAL RESCUE ────────────────────────────────────────────────────────────
T(lambda c,n,h: f"Stray animals injured in floods in {c}. Need {n} volunteers for rescue and care",
  lambda c,n,h: dict(category="animal_welfare", subcategory="animal_rescue", location_city=c,
                     volunteers_needed=n, urgency_level="medium", deadline_hours=h,
                     required_skills=["rescue","medical"], is_disaster_related=True))

T(lambda c,n,h: f"Animal shelter in {c} needs {n} volunteers for feeding and care",
  lambda c,n,h: dict(category="animal_welfare", subcategory="shelter_support", location_city=c,
                     volunteers_needed=n, urgency_level="low", deadline_hours=72,
                     shift_type="any"))

# ── CLEANUP ──────────────────────────────────────────────────────────────────
T(lambda c,n,h: f"Post-flood cleanup drive in {c}. Need {n} volunteers with cleaning equipment",
  lambda c,n,h: dict(category="cleanup", subcategory="disaster_cleanup", location_city=c,
                     volunteers_needed=n, urgency_level="medium", deadline_hours=h,
                     required_skills=["cleanup","logistics"], is_disaster_related=True,
                     effort_level="high", required_items=["cleaning_supplies"]))

T(lambda c,n,h: f"Community cleanliness drive in {c} this Sunday. Need {n} enthusiastic volunteers",
  lambda c,n,h: dict(category="cleanup", subcategory="community_cleanup", location_city=c,
                     volunteers_needed=n, urgency_level="low", deadline_hours=96,
                     required_skills=["cleanup"], shift_type="weekend", effort_level="medium"))

# ── WATER / SANITATION ───────────────────────────────────────────────────────
T(lambda c,n,h: f"Water shortage in {c}. Need {n} volunteers for water distribution to {n*50} people",
  lambda c,n,h: dict(category="water_sanitation", subcategory="water_distribution", location_city=c,
                     volunteers_needed=n, estimated_people_affected=n*50,
                     urgency_level="high", deadline_hours=h,
                     required_items=["water_cans"], transport_required=True))

T(lambda c,n,h: f"Sanitation drive needed at flood relief camp in {c}. {n} volunteers required immediately",
  lambda c,n,h: dict(category="water_sanitation", subcategory="sanitation", location_city=c,
                     volunteers_needed=n, urgency_level="high", deadline_hours=h,
                     required_skills=["cleanup"], is_disaster_related=True, effort_level="medium"))

# ── FUNDRAISING / AWARENESS ──────────────────────────────────────────────────
T(lambda c,n,h: f"Fundraising drive for flood victims in {c}. Need {n} volunteers for door-to-door campaign",
  lambda c,n,h: dict(category="fundraising", subcategory="donation_drive", location_city=c,
                     volunteers_needed=n, urgency_level="medium", deadline_hours=72,
                     required_skills=["logistics"]))

T(lambda c,n,h: f"Awareness campaign about dengue fever prevention in {c}. Need {n} volunteers",
  lambda c,n,h: dict(category="awareness", subcategory="health_awareness", location_city=c,
                     volunteers_needed=n, urgency_level="medium", deadline_hours=72,
                     required_skills=["teaching","counseling"]))

# ── CHILDCARE ────────────────────────────────────────────────────────────────
T(lambda c,n,h: f"Need volunteers to care for {n} orphaned children in {c} disaster relief camp",
  lambda c,n,h: dict(category="childcare", subcategory="orphan_support", location_city=c,
                     estimated_people_affected=n, children_involved=True,
                     volunteers_needed=max(2,n//5), urgency_level="high", deadline_hours=h,
                     required_skills=["counseling","teaching"], is_disaster_related=True))

T(lambda c,n,h: f"Childcare support needed at relief camp in {c} for {n} children while parents work",
  lambda c,n,h: dict(category="childcare", subcategory="childcare_support", location_city=c,
                     estimated_people_affected=n, children_involved=True,
                     volunteers_needed=max(2,n//10), urgency_level="medium", deadline_hours=48,
                     required_skills=["teaching","counseling"]))

# ── WOMEN SAFETY ─────────────────────────────────────────────────────────────
T(lambda c,n,h: f"Safe shelter needed for {n} women and children in {c} escaping domestic violence",
  lambda c,n,h: dict(category="women_safety", subcategory="shelter_support", location_city=c,
                     estimated_people_affected=n, children_involved=True,
                     urgency_level="high", deadline_hours=h,
                     required_skills=["counseling"], need_type="shelter"))

# ── ADMIN / DATA ENTRY ───────────────────────────────────────────────────────
T(lambda c,n,h: f"Need {n} volunteers for data entry and documentation work for NGO in {c}",
  lambda c,n,h: dict(category="administration", subcategory="data_entry", location_city=c,
                     volunteers_needed=n, urgency_level="low", deadline_hours=168,
                     required_skills=["data_entry"], effort_level="low",
                     min_experience_level="beginner", shift_type="any"))

# ─────────────────────────────────────────────────────────────────────────────
# Urgency overrides
# ─────────────────────────────────────────────────────────────────────────────
URGENCY_WORDS = {
    "critical": ["immediately", "critical", "life-threatening", "emergency", "urgent now"],
    "high":     ["urgently", "within 12 hours", "tonight", "today", "ASAP"],
    "medium":   ["tomorrow", "this week", "soon", "within 48 hours"],
    "low":      ["next week", "whenever", "this month", "no rush"],
}

def inject_urgency_word(text: str, urgency: str) -> str:
    if random.random() < 0.4:
        word = random.choice(URGENCY_WORDS.get(urgency, []))
        if word and word not in text:
            text = text.rstrip(".") + f". Situation is {word}."
    return text

# ─────────────────────────────────────────────────────────────────────────────
# Title generator
# ─────────────────────────────────────────────────────────────────────────────
TITLE_TEMPLATES = {
    "disaster_relief":    "Disaster Relief Support – {city}",
    "food_relief":        "Food Distribution Need – {city}",
    "medical":            "Medical Assistance Request – {city}",
    "logistics":          "Logistics Volunteer Need – {city}",
    "shelter":            "Shelter Support – {city}",
    "education":          "Education Volunteer Request – {city}",
    "elderly_care":       "Elderly Care Support – {city}",
    "mental_health":      "Mental Health Support – {city}",
    "animal_welfare":     "Animal Welfare Help – {city}",
    "cleanup":            "Cleanup Drive – {city}",
    "water_sanitation":   "Water & Sanitation Help – {city}",
    "fundraising":        "Fundraising Drive – {city}",
    "awareness":          "Awareness Campaign – {city}",
    "childcare":          "Childcare Support – {city}",
    "women_safety":       "Women Safety Support – {city}",
    "administration":     "Admin Volunteer Need – {city}",
}

def make_title(category: str, city: str) -> str:
    tmpl = TITLE_TEMPLATES.get(category, "Help Request – {city}")
    return tmpl.format(city=city)

# ─────────────────────────────────────────────────────────────────────────────
# Flatten list fields for CSV
# ─────────────────────────────────────────────────────────────────────────────
def flatten_row(fields: dict, city: str) -> dict:
    state = CITIES_STATES.get(city, "Unknown")
    row = {
        "request_title":           fields.get("request_title", make_title(fields.get("category","general"), city)),
        "category":                fields.get("category", "general"),
        "subcategory":             fields.get("subcategory", ""),
        "urgency_level":           fields.get("urgency_level", "medium"),
        "priority_label":          _urgency_to_priority(fields.get("urgency_level","medium")),
        "estimated_people_affected":fields.get("estimated_people_affected", 0),
        "location_city":           city,
        "location_state":          state,
        "deadline_hours":          fields.get("deadline_hours", 48),
        "required_skills":         "|".join(fields.get("required_skills", [])),
        "required_items":          "|".join(fields.get("required_items", [])),
        "volunteers_needed":       fields.get("volunteers_needed", 0),
        "is_medical_emergency":    int(fields.get("is_medical_emergency", False)),
        "is_disaster_related":     int(fields.get("is_disaster_related", False)),
        "transport_required":      int(fields.get("transport_required", False)),
        "contact_preference":      random.choice(["phone","whatsapp","email"]),
        # volunteer task fields
        "task_type":               fields.get("subcategory", ""),
        "effort_level":            fields.get("effort_level", "medium"),
        "min_experience_level":    fields.get("min_experience_level", "beginner"),
        "shift_type":              fields.get("shift_type", "any"),
        # public request fields
        "need_type":               fields.get("need_type", fields.get("subcategory","general")),
        "family_count":            fields.get("family_count", 0),
        "children_involved":       int(fields.get("children_involved", False)),
        "elderly_involved":        int(fields.get("elderly_involved", False)),
    }
    return row

def _urgency_to_priority(urgency: str) -> str:
    return {"critical": "Critical", "high": "High",
            "medium": "Medium", "low": "Low"}.get(urgency, "Medium")

# ─────────────────────────────────────────────────────────────────────────────
# Main generation
# ─────────────────────────────────────────────────────────────────────────────
def generate_dataset(n: int = 3200, output_path: str = "data/dataset.csv"):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    rows_text = []
    rows_labels = []

    per_template = max(1, n // len(TEMPLATES))

    for text_fn, fields_fn in TEMPLATES:
        for _ in range(per_template):
            city = random.choice(CITIES)
            n_people = random.choice([10, 20, 30, 50, 75, 100, 150, 200])
            n_vols   = random.choice([2, 3, 5, 8, 10, 15, 20])
            hours    = random.choice([4, 6, 8, 12, 24, 48, 72])

            try:
                text   = text_fn(city, n_people, hours)
                fields = fields_fn(city, n_people, hours)
            except Exception:
                continue

            # Inject urgency words
            urgency = fields.get("urgency_level", "medium")
            text    = inject_urgency_word(text, urgency)

            rows_text.append(text)
            flat = flatten_row(fields, city)
            flat["request_description"] = text
            rows_labels.append(flat)

    # Trim / shuffle
    df = pd.DataFrame(rows_labels).sample(frac=1, random_state=42).reset_index(drop=True)
    df = df.head(n)
    df.to_csv(output_path, index=False)
    print(f"✅  Dataset saved → {output_path}  ({len(df)} rows)")
    print(df["category"].value_counts().head(10))
    return df


if __name__ == "__main__":
    generate_dataset()
