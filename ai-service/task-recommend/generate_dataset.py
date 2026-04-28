"""
SevaSetu – Synthetic Dataset Generator
Generates realistic volunteer profiles, NGO tasks, and labeled interaction pairs.
"""

import random
import json
import numpy as np
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

SKILLS = [
    "medical", "logistics", "teaching", "driving",
    "rescue", "counseling", "packaging", "data_entry",
    "food_distribution", "cleanup"
]

LANGUAGES = ["Hindi", "English", "Marathi", "Bengali", "Tamil",
             "Telugu", "Kannada", "Gujarati", "Punjabi", "Odia"]

TASK_CATEGORIES = [
    "medical_aid", "food_distribution", "shelter_setup",
    "disaster_rescue", "education_support", "logistics_transport",
    "counseling_support", "cleanup_drive", "data_collection", "awareness_campaign"
]

CATEGORY_SKILL_MAP = {
    "medical_aid":          ["medical", "counseling"],
    "food_distribution":    ["food_distribution", "packaging", "logistics"],
    "shelter_setup":        ["logistics", "cleanup", "packaging"],
    "disaster_rescue":      ["rescue", "medical", "driving"],
    "education_support":    ["teaching", "counseling"],
    "logistics_transport":  ["driving", "logistics"],
    "counseling_support":   ["counseling", "teaching"],
    "cleanup_drive":        ["cleanup", "logistics"],
    "data_collection":      ["data_entry", "teaching"],
    "awareness_campaign":   ["teaching", "counseling", "data_entry"],
}

DISASTER_TYPES = ["flood", "earthquake", "fire", "drought",
                  "pandemic", "cyclone", "landslide", "none"]

NGOS = [
    "HelpIndia Foundation", "RapidRelief NGO", "CareBridge Trust",
    "HopeFirst Society", "SevaSetu Initiative", "GreenHands Welfare",
    "UdayKiran Foundation", "NayaSaathi Org"
]

# Indian cities with approximate lat/lon
CITIES = {
    "Mumbai":    (19.0760, 72.8777),
    "Delhi":     (28.6139, 77.2090),
    "Bangalore": (12.9716, 77.5946),
    "Kolkata":   (22.5726, 88.3639),
    "Chennai":   (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Pune":      (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur":    (26.9124, 75.7873),
    "Lucknow":   (26.8467, 80.9462),
}

LOCALITIES = ["Andheri", "Bandra", "Dadar", "Kurla", "Malad",
              "Borivali", "Thane", "Navi Mumbai", "Powai", "Vikhroli",
              "Connaught Place", "Lajpat Nagar", "Saket", "Dwarka",
              "Koramangala", "Indiranagar", "Whitefield", "Jayanagar"]

VEHICLE_TYPES = ["none", "bike", "car", "van"]
VOLUNTEER_LEVELS = ["beginner", "regular", "experienced"]
AVAILABILITY_TYPES = ["full_time", "part_time", "weekends", "evenings", "custom"]

EFFORT_LEVELS = ["low", "medium", "high"]


# ─────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(a))


def jitter_coords(lat, lon, radius_km=5):
    """Add random offset to coordinates (simulate different areas)."""
    d_lat = random.uniform(-radius_km / 111, radius_km / 111)
    d_lon = random.uniform(-radius_km / 111, radius_km / 111)
    return round(lat + d_lat, 5), round(lon + d_lon, 5)


# ─────────────────────────────────────────────
# VOLUNTEER GENERATOR
# ─────────────────────────────────────────────

def generate_volunteer(vol_id):
    city = random.choice(list(CITIES.keys()))
    base_lat, base_lon = CITIES[city]
    lat, lon = jitter_coords(base_lat, base_lon, radius_km=8)

    num_skills = random.choices([1, 2, 3, 4], weights=[20, 40, 30, 10])[0]
    skills = random.sample(SKILLS, num_skills)

    num_langs = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
    languages = random.sample(LANGUAGES, num_langs)

    level = random.choices(VOLUNTEER_LEVELS, weights=[30, 45, 25])[0]
    past_tasks = {"beginner": random.randint(0, 5),
                  "regular": random.randint(5, 25),
                  "experienced": random.randint(25, 100)}[level]

    reliability = {"beginner": random.uniform(50, 80),
                   "regular": random.uniform(65, 90),
                   "experienced": random.uniform(75, 100)}[level]

    availability = random.choice(AVAILABILITY_TYPES)
    hours_per_week = {"full_time": random.randint(30, 50),
                      "part_time": random.randint(10, 25),
                      "weekends": random.randint(8, 16),
                      "evenings": random.randint(5, 15),
                      "custom": random.randint(3, 20)}[availability]

    pref_categories = random.sample(TASK_CATEGORIES, random.randint(1, 3))

    return {
        "volunteer_id": f"V{vol_id:04d}",
        "full_name": f"Volunteer_{vol_id}",
        "age": random.randint(18, 65),
        "city": city,
        "area": random.choice(LOCALITIES),
        "latitude": lat,
        "longitude": lon,
        "skills": skills,
        "languages_known": languages,
        "vehicle_type": random.choices(VEHICLE_TYPES, weights=[35, 30, 25, 10])[0],
        "availability": availability,
        "available_hours_per_week": hours_per_week,
        "past_tasks_completed": past_tasks,
        "reliability_score": round(reliability, 1),
        "average_response_time": random.randint(5, 120),  # minutes
        "preferred_task_types": pref_categories,
        "max_travel_km": random.choices([5, 10, 15, 20, 30, 50], weights=[15, 25, 25, 20, 10, 5])[0],
        "last_active_time": (datetime.now() - timedelta(hours=random.randint(0, 72))).isoformat(),
        "volunteer_level": level,
    }


# ─────────────────────────────────────────────
# TASK GENERATOR
# ─────────────────────────────────────────────

def generate_task(task_id):
    city = random.choice(list(CITIES.keys()))
    base_lat, base_lon = CITIES[city]
    lat, lon = jitter_coords(base_lat, base_lon, radius_km=10)

    category = random.choice(TASK_CATEGORIES)
    related_skills = CATEGORY_SKILL_MAP[category]
    num_skills = random.choices([1, 2, 3], weights=[40, 45, 15])[0]
    required_skills = random.sample(related_skills, min(num_skills, len(related_skills)))
    # Sometimes add extra skills
    if random.random() < 0.2:
        extra = random.choice([s for s in SKILLS if s not in required_skills])
        required_skills.append(extra)

    priority = random.choices(range(30, 101), weights=[1] * 71)[0]
    # Boost priority for rescue/medical
    if category in ["disaster_rescue", "medical_aid"]:
        priority = min(100, priority + random.randint(10, 30))

    total_needed = random.choices([2, 3, 5, 8, 10, 15, 20], weights=[15, 20, 25, 20, 10, 7, 3])[0]
    assigned = random.randint(0, max(0, total_needed - 1))

    deadline = random.choices([6, 12, 24, 48, 72, 168], weights=[10, 15, 25, 25, 15, 10])[0]
    duration = random.choices([1, 2, 3, 4, 6, 8], weights=[15, 25, 25, 20, 10, 5])[0]

    effort = random.choice(EFFORT_LEVELS)
    if category == "disaster_rescue":
        effort = "high"

    vehicle_req = "none"
    if category in ["logistics_transport", "disaster_rescue"] or "driving" in required_skills:
        vehicle_req = random.choice(["bike", "car", "van"])

    num_pref_langs = random.choices([0, 1, 2], weights=[30, 50, 20])[0]
    pref_langs = random.sample(LANGUAGES, num_pref_langs) if num_pref_langs > 0 else []

    return {
        "task_id": f"T{task_id:04d}",
        "task_title": f"{category.replace('_', ' ').title()} Task {task_id}",
        "task_description": f"Volunteer needed for {category.replace('_', ' ')} in {city}.",
        "task_category": category,
        "location_city": city,
        "area": random.choice(LOCALITIES),
        "latitude": lat,
        "longitude": lon,
        "disaster_type": random.choice(DISASTER_TYPES) if category == "disaster_rescue" else "none",
        "required_skills": required_skills,
        "required_volunteers_count": total_needed,
        "currently_assigned_count": assigned,
        "task_priority_score": priority,
        "deadline_hours_remaining": deadline,
        "estimated_duration_hours": duration,
        "physical_effort_level": effort,
        "requires_vehicle": vehicle_req,
        "preferred_languages": pref_langs,
        "ngo_name": random.choice(NGOS),
        "created_time": (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
    }


# ─────────────────────────────────────────────
# MATCH SCORE COMPUTATION (Ground Truth)
# ─────────────────────────────────────────────

VEHICLE_HIERARCHY = {"none": 0, "bike": 1, "car": 2, "van": 3}
LEVEL_MAP = {"beginner": 0, "regular": 1, "experienced": 2}
EFFORT_MAP = {"low": 0, "medium": 1, "high": 2}
AVAIL_WEEKDAY = {"full_time", "part_time"}
AVAIL_WEEKEND = {"weekends", "full_time"}
AVAIL_EVENING = {"evenings", "full_time", "part_time"}


def compute_availability_match(availability, task):
    deadline = task["deadline_hours_remaining"]
    # Simplistic: critical tasks are urgent, match all; 
    # weekday tasks clash with weekends-only
    if deadline <= 12:
        # Urgent – all availability types partially match
        return 0.8 if availability in {"weekends"} else 1.0
    if deadline <= 48:
        return 1.0 if availability != "weekends" else 0.7
    return 1.0 if availability in {"full_time", "part_time"} else 0.85


def compute_vehicle_match(vol_vehicle, task_vehicle_req):
    if task_vehicle_req == "none":
        return 1.0
    vol_rank = VEHICLE_HIERARCHY.get(vol_vehicle, 0)
    req_rank = VEHICLE_HIERARCHY.get(task_vehicle_req, 0)
    if vol_rank >= req_rank:
        return 1.0
    elif vol_rank == req_rank - 1:
        return 0.5
    return 0.0


def compute_ground_truth_score(volunteer, task):
    """
    Weighted formula to produce a realistic match score (0–100).
    This is the ground truth the model will learn to approximate.
    """
    # --- Skill match ---
    vol_skills = set(volunteer["skills"])
    task_skills = set(task["required_skills"])
    if task_skills:
        skill_ratio = len(vol_skills & task_skills) / len(task_skills)
    else:
        skill_ratio = 0.5
    skill_score = skill_ratio  # 0–1

    # --- Distance score ---
    dist = haversine(volunteer["latitude"], volunteer["longitude"],
                     task["latitude"], task["longitude"])
    max_travel = volunteer["max_travel_km"]
    if dist <= max_travel:
        dist_score = 1.0 - (dist / (max_travel * 2))  # mild penalty
    else:
        # Beyond range: sharp penalty
        overshoot = dist - max_travel
        dist_score = max(0.0, 0.3 - overshoot / max_travel * 0.3)

    # --- Priority ---
    priority_score = task["task_priority_score"] / 100.0

    # --- Deadline urgency ---
    deadline = task["deadline_hours_remaining"]
    urgency_score = max(0, 1.0 - deadline / 168.0)  # 1 week max

    # --- Availability match ---
    avail_score = compute_availability_match(volunteer["availability"], task)

    # --- Vehicle ---
    vehicle_score = compute_vehicle_match(volunteer["vehicle_type"], task["requires_vehicle"])

    # --- Language ---
    vol_langs = set(volunteer["languages_known"])
    task_langs = set(task["preferred_languages"])
    lang_score = 1.0 if (not task_langs or vol_langs & task_langs) else 0.5

    # --- Level vs effort ---
    vol_lvl = LEVEL_MAP.get(volunteer["volunteer_level"], 1)
    task_effort = EFFORT_MAP.get(task["physical_effort_level"], 1)
    if vol_lvl >= task_effort:
        level_score = 1.0
    else:
        gap = task_effort - vol_lvl
        level_score = max(0.0, 1.0 - gap * 0.4)

    # --- Reliability (higher = better for critical tasks) ---
    reliability = volunteer["reliability_score"] / 100.0

    # --- Workload balance (prefer tasks with slots available) ---
    slots_left = task["required_volunteers_count"] - task["currently_assigned_count"]
    slot_score = 1.0 if slots_left > 0 else 0.0

    # --- Preferred task type ---
    pref_score = 1.0 if task["task_category"] in volunteer["preferred_task_types"] else 0.7

    # --- Hours fit ---
    hours_fit = 1.0 if volunteer["available_hours_per_week"] >= task["estimated_duration_hours"] else 0.6

    # --- Weighted combination ---
    raw = (
        skill_score     * 0.30 +
        dist_score      * 0.20 +
        priority_score  * 0.15 +
        urgency_score   * 0.10 +
        avail_score     * 0.05 +
        vehicle_score   * 0.05 +
        lang_score      * 0.04 +
        level_score     * 0.04 +
        reliability     * 0.03 +
        slot_score      * 0.02 +
        pref_score      * 0.01 +
        hours_fit       * 0.01
    )  # sums to 1.0

    # Boost for exact skill match + nearby + critical
    if skill_ratio == 1.0 and dist <= 5 and task["task_priority_score"] >= 80:
        raw = min(1.0, raw * 1.15)

    # Penalty if task is full
    if slots_left <= 0:
        raw *= 0.3

    score = raw * 100.0

    # Add realistic noise
    noise = np.random.normal(0, 3)
    score = float(np.clip(score + noise, 0, 100))
    return round(score, 2)


# ─────────────────────────────────────────────
# FEATURE EXTRACTION (shared with train/recommend)
# ─────────────────────────────────────────────

def extract_features(volunteer, task):
    vol_skills = set(volunteer["skills"])
    task_skills = set(task["required_skills"])

    # Skill features
    if task_skills:
        skill_match_ratio = len(vol_skills & task_skills) / len(task_skills)
        skill_exact_match = float(task_skills.issubset(vol_skills))
        skill_count_matched = len(vol_skills & task_skills)
    else:
        skill_match_ratio = 0.5
        skill_exact_match = 0.0
        skill_count_matched = 0

    # Distance
    dist = haversine(volunteer["latitude"], volunteer["longitude"],
                     task["latitude"], task["longitude"])
    max_travel = volunteer.get("max_travel_km", 20)
    within_limit = float(dist <= max_travel)
    dist_score = max(0.0, 1.0 - dist / max(max_travel, 1))
    dist_normalized = dist / max(max_travel, 1)

    # Priority & urgency
    priority_norm = task["task_priority_score"] / 100.0
    deadline = task["deadline_hours_remaining"]
    urgency = max(0.0, 1.0 - deadline / 168.0)
    is_critical = float(deadline <= 12)

    # Availability
    avail_score = compute_availability_match(volunteer["availability"], task)
    avail_full_time = float(volunteer["availability"] == "full_time")
    avail_weekends_only = float(volunteer["availability"] == "weekends")

    # Vehicle
    vehicle_score = compute_vehicle_match(volunteer["vehicle_type"], task["requires_vehicle"])
    has_vehicle = float(volunteer["vehicle_type"] != "none")

    # Language
    vol_langs = set(volunteer.get("languages_known", []))
    task_langs = set(task.get("preferred_languages", []))
    lang_match = float(not task_langs or bool(vol_langs & task_langs))

    # Level vs effort
    vol_lvl = LEVEL_MAP.get(volunteer.get("volunteer_level", "regular"), 1)
    task_effort = EFFORT_MAP.get(task.get("physical_effort_level", "medium"), 1)
    level_effort_diff = vol_lvl - task_effort  # positive = over-qualified (good), negative = under
    level_fit = float(vol_lvl >= task_effort)

    # Reliability
    reliability_norm = volunteer.get("reliability_score", 70) / 100.0

    # Workload
    slots_left = task["required_volunteers_count"] - task["currently_assigned_count"]
    slot_ratio = slots_left / max(task["required_volunteers_count"], 1)
    task_not_full = float(slots_left > 0)

    # Preferred type
    pref_match = float(task["task_category"] in volunteer.get("preferred_task_types", []))

    # Hours fit
    hours_fit = float(volunteer.get("available_hours_per_week", 10) >= task["estimated_duration_hours"])

    # Volunteer experience
    past_tasks = volunteer.get("past_tasks_completed", 0)
    past_tasks_log = np.log1p(past_tasks)
    experience_norm = min(past_tasks / 100.0, 1.0)

    # Response time (lower is better)
    avg_resp = volunteer.get("average_response_time", 60)
    response_score = max(0.0, 1.0 - avg_resp / 120.0)

    # Same city bonus
    same_city = float(volunteer.get("city", "") == task.get("location_city", ""))

    # Task fill ratio (how full is the task)
    fill_ratio = task["currently_assigned_count"] / max(task["required_volunteers_count"], 1)

    return {
        "skill_match_ratio":    skill_match_ratio,
        "skill_exact_match":    skill_exact_match,
        "skill_count_matched":  skill_count_matched,
        "distance_km":          dist,
        "distance_score":       dist_score,
        "distance_normalized":  dist_normalized,
        "within_travel_limit":  within_limit,
        "task_priority_score":  priority_norm,
        "deadline_urgency":     urgency,
        "is_critical_deadline": is_critical,
        "availability_match":   avail_score,
        "avail_full_time":      avail_full_time,
        "avail_weekends_only":  avail_weekends_only,
        "vehicle_match":        vehicle_score,
        "has_vehicle":          has_vehicle,
        "language_match":       lang_match,
        "level_effort_diff":    float(level_effort_diff),
        "level_fit":            level_fit,
        "reliability_score":    reliability_norm,
        "slots_remaining":      float(max(slots_left, 0)),
        "slot_ratio":           slot_ratio,
        "task_not_full":        task_not_full,
        "fill_ratio":           fill_ratio,
        "preferred_type_match": pref_match,
        "hours_fit":            hours_fit,
        "past_tasks_log":       float(past_tasks_log),
        "experience_norm":      experience_norm,
        "response_score":       response_score,
        "same_city":            same_city,
    }


FEATURE_COLUMNS = list(extract_features(
    generate_volunteer(0), generate_task(0)
).keys())


# ─────────────────────────────────────────────
# DATASET GENERATION
# ─────────────────────────────────────────────

def generate_dataset(n_volunteers=200, n_tasks=100, pairs_per_volunteer=25, output_csv="data/interactions.csv"):
    import os
    os.makedirs("data", exist_ok=True)

    print(f"Generating {n_volunteers} volunteers and {n_tasks} tasks...")
    volunteers = [generate_volunteer(i) for i in range(1, n_volunteers + 1)]
    tasks = [generate_task(j) for j in range(1, n_tasks + 1)]

    print("Generating interaction pairs...")
    rows = []
    for vol in volunteers:
        # Sample tasks for this volunteer (not necessarily all)
        sampled_tasks = random.sample(tasks, min(pairs_per_volunteer, len(tasks)))
        for task in sampled_tasks:
            score = compute_ground_truth_score(vol, task)
            feats = extract_features(vol, task)
            row = {
                "volunteer_id": vol["volunteer_id"],
                "task_id": task["task_id"],
                "match_score": score,
                "relevance_label": int(score >= 60),  # binary label
            }
            row.update(feats)
            rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"Dataset saved: {output_csv} | Rows: {len(df)}")

    # Also save raw volunteer/task JSON for API demo
    with open("data/sample_volunteers.json", "w") as f:
        json.dump(volunteers[:10], f, indent=2)
    with open("data/sample_tasks.json", "w") as f:
        json.dump(tasks[:20], f, indent=2)

    return df, volunteers, tasks


if __name__ == "__main__":
    df, volunteers, tasks = generate_dataset(
        n_volunteers=200,
        n_tasks=100,
        pairs_per_volunteer=30,
        output_csv="data/interactions.csv"
    )
    print("\nSample rows:")
    print(df[["volunteer_id", "task_id", "match_score"] + FEATURE_COLUMNS[:5]].head())
    print(f"\nTotal interactions: {len(df)}")
    print(f"Score distribution:\n{df['match_score'].describe()}")
