"""
generate_dataset.py
Generates a realistic synthetic training dataset for the SevaSetu Priority AI model.
"""

import random
import pandas as pd
import numpy as np

random.seed(42)
np.random.seed(42)

# ─── Vocabulary pools ────────────────────────────────────────────────────────

CRITICAL_TITLES = [
    "Urgent medical volunteers needed at flood relief camp",
    "Emergency blood donors required immediately",
    "Rescue team needed near landslide zone tonight",
    "Critical medicine delivery volunteers needed today",
    "Immediate evacuation support needed in cyclone area",
    "Emergency medical aid volunteers for flood victims",
    "Life-threatening situation – rescue volunteers needed NOW",
    "Urgent: stranded flood victims need immediate help",
    "Emergency food and water distribution in disaster zone",
    "Critical: trauma support volunteers needed at hospital",
    "Urgent rescue operation – volunteers needed immediately",
    "Emergency relief – medical camp setup tonight",
]

HIGH_TITLES = [
    "Volunteers needed tomorrow for ration distribution",
    "Shelter setup support needed by tomorrow morning",
    "Food distribution volunteers needed this evening",
    "Water distribution support for flood-affected area",
    "Urgent: temporary shelter construction volunteers",
    "Relief camp logistics volunteers needed tomorrow",
    "Medical camp volunteers needed this week",
    "Volunteer drivers needed for medicine transport tomorrow",
    "Sanitation volunteers needed at relief camp",
    "Psychosocial support volunteers needed this week",
]

MEDIUM_TITLES = [
    "Volunteers needed this weekend for donation packaging",
    "Transport volunteers for weekly supply delivery",
    "Awareness campaign volunteers needed this Saturday",
    "Donation collection drive volunteers this weekend",
    "Community kitchen volunteers needed this week",
    "Health camp registration volunteers needed Sunday",
    "Help needed for refugee documentation support",
    "Skill training session support volunteers",
    "Library books sorting volunteers this weekend",
    "Legal aid camp volunteers needed next few days",
]

LOW_TITLES = [
    "Educational material sorting volunteers needed next week",
    "Admin assistance for NGO office next week",
    "Social media content creation volunteer needed",
    "Website update volunteer needed",
    "Research assistant volunteer for grant writing",
    "Data entry volunteers needed next month",
    "Community survey volunteers for planning phase",
    "Fundraising preparation volunteers next week",
    "Video editing volunteer for awareness campaign",
    "Volunteer coordinator assistant needed",
]

CRITICAL_DESCRIPTIONS = [
    "Situation is life-threatening. Floodwaters rising rapidly. Medical volunteers with first aid training needed urgently tonight. People are stranded without food or medicine.",
    "Severe blood shortage at district hospital. Patients in critical condition need transfusions immediately. Please respond within the next 2 hours.",
    "Landslide has cut off a village. Search and rescue operation ongoing. Need trained rescue volunteers immediately with ropes and basic equipment.",
    "Medicine supply running out at relief camp. Transport volunteers with own vehicle needed to pick up medicines and deliver to camp tonight.",
    "Cyclone evacuation underway. Need strong volunteers to help shift elderly and disabled persons to safety shelters immediately.",
    "Severe flood displacement. 200+ families stranded. Need medical triage volunteers to handle injuries and illness. Time-critical situation.",
    "Emergency: children with high fever at disaster camp. Need pediatric volunteers or nurses immediately. No medical facility nearby.",
    "Gas leak near residential area. Need support volunteers to assist evacuation and crowd management. Emergency services are overwhelmed.",
]

HIGH_DESCRIPTIONS = [
    "Ration distribution drive for 500 displaced families tomorrow morning at 8am. Need 5 organized volunteers for crowd management and distribution.",
    "Setting up temporary shelter for 100 flood-affected people arriving tomorrow evening. Need volunteers for construction and arrangement.",
    "Daily food distribution at refugee camp needs reinforcement. Existing volunteers are exhausted. Need fresh team starting tomorrow.",
    "Water tanker distribution route needs 3 volunteer coordinators to manage queues and ensure equitable distribution in affected zones.",
    "Medical camp starting this week for flood survivors. Need volunteers to assist doctors with registration, triage, and patient flow.",
    "Relief supplies from central warehouse need to be packed and transported to 5 distribution points. Need 6 volunteers tomorrow morning.",
    "Sanitation drive needed at relief camp to prevent disease outbreak. Need 4 volunteers for cleaning and awareness. Starts tomorrow.",
]

MEDIUM_DESCRIPTIONS = [
    "Weekend donation packaging drive for hygiene kits. Need 6 volunteers to sort, pack, and label kits at our warehouse on Saturday.",
    "Monthly supply transport to remote village. Need 2 volunteers with driving license for a 4-hour round trip this weekend.",
    "Awareness campaign about disease prevention in flood-affected communities. Need volunteers for door-to-door visits this Saturday.",
    "Community kitchen needs extra hands this week for cooking and serving meals for 150 daily visitors.",
    "Health camp registration drive on Sunday. Need 3 volunteers to manage paperwork and assist with patient flow.",
    "Skill training session for youth in relief camp. Need 2 volunteer trainers for a half-day workshop this week.",
    "Refugee documentation assistance: helping families register for government relief. Need 2 volunteers with language skills.",
]

LOW_DESCRIPTIONS = [
    "Sorting and cataloguing donated educational materials for distribution next week. No special skills required. Indoor work.",
    "Administrative support needed at our main office. Tasks include data entry, filing, and basic computer work. Flexible timing next week.",
    "Looking for a volunteer to manage our NGO social media for one month. Need someone with basic content creation skills.",
    "Need a volunteer developer to update our NGO website with new donation information. Remote work, deadline next month.",
    "Research volunteer needed to help write our annual grant report. Need someone with writing skills. Work from home. No urgency.",
    "Data entry volunteer needed to digitize paper records over 2-3 weeks. Can work from home at own pace.",
    "Community survey volunteer needed for needs assessment in a village. Low urgency, planning phase for next quarter.",
]

CATEGORIES = ["Medical", "Food & Nutrition", "Rescue & Evacuation", "Shelter", 
               "Education", "Logistics & Transport", "Sanitation", "Psychosocial Support",
               "Administration", "Fundraising", "Awareness", "Skill Training"]

LOCATIONS = ["Assam", "Guwahati", "Chennai", "Pune", "Mumbai", "Odisha", "Bihar",
             "Kerala", "Uttarakhand", "Himachal Pradesh", "West Bengal", "Andhra Pradesh",
             "Karnataka", "Rajasthan", "Gujarat", "Madhya Pradesh"]

DISASTER_TYPES = ["Flood", "Cyclone", "Landslide", "Drought", "Earthquake", 
                  "Fire", "None", "None", "None", "Industrial Accident"]

MANUAL_URGENCY = ["critical", "high", "medium", "low"]

# ─── Helper to create a row ───────────────────────────────────────────────────

def make_row(label: str, noise_prob: float = 0.08) -> dict:
    """Build one synthetic sample row."""

    if label == "Critical":
        title = random.choice(CRITICAL_TITLES)
        desc  = random.choice(CRITICAL_DESCRIPTIONS)
        cat   = random.choice(["Medical", "Rescue & Evacuation", "Food & Nutrition", "Logistics & Transport"])
        deadline_hours = random.choice([1, 2, 3, 4, 6, 8, 12])
        volunteers = random.randint(1, 6)
        manual_urgency = random.choices(["critical", "high"], weights=[0.85, 0.15])[0]
        disaster = random.choices(["Flood", "Cyclone", "Landslide", "Earthquake", "None"],
                                   weights=[0.35, 0.25, 0.20, 0.10, 0.10])[0]
        created_hour = random.choice(list(range(0, 24)))

    elif label == "High":
        title = random.choice(HIGH_TITLES)
        desc  = random.choice(HIGH_DESCRIPTIONS)
        cat   = random.choice(["Food & Nutrition", "Shelter", "Medical", "Sanitation", "Logistics & Transport"])
        deadline_hours = random.choice([12, 18, 24, 30, 36, 48])
        volunteers = random.randint(2, 8)
        manual_urgency = random.choices(["high", "critical", "medium"], weights=[0.75, 0.10, 0.15])[0]
        disaster = random.choices(["Flood", "Cyclone", "None", "None"],
                                   weights=[0.35, 0.25, 0.20, 0.20])[0]
        created_hour = random.choice(list(range(6, 22)))

    elif label == "Medium":
        title = random.choice(MEDIUM_TITLES)
        desc  = random.choice(MEDIUM_DESCRIPTIONS)
        cat   = random.choice(["Awareness", "Logistics & Transport", "Food & Nutrition",
                                "Psychosocial Support", "Skill Training"])
        deadline_hours = random.choice([48, 72, 96, 120])
        volunteers = random.randint(2, 10)
        manual_urgency = random.choices(["medium", "high", "low"], weights=[0.70, 0.15, 0.15])[0]
        disaster = random.choices(["None", "Flood", "None", "None"],
                                   weights=[0.60, 0.20, 0.10, 0.10])[0]
        created_hour = random.choice(list(range(8, 20)))

    else:  # Low
        title = random.choice(LOW_TITLES)
        desc  = random.choice(LOW_DESCRIPTIONS)
        cat   = random.choice(["Education", "Administration", "Fundraising", "Awareness"])
        deadline_hours = random.choice([120, 168, 240, 336, 504])
        volunteers = random.randint(1, 4)
        manual_urgency = random.choices(["low", "medium"], weights=[0.85, 0.15])[0]
        disaster = "None"
        created_hour = random.choice(list(range(9, 18)))

    # Inject label noise for realism
    final_label = label
    if random.random() < noise_prob:
        all_labels = ["Critical", "High", "Medium", "Low"]
        neighbours = {
            "Critical": ["High"],
            "High": ["Critical", "Medium"],
            "Medium": ["High", "Low"],
            "Low": ["Medium"],
        }
        final_label = random.choice(neighbours[label])

    return {
        "task_title": title,
        "task_description": desc,
        "task_category": cat,
        "location": random.choice(LOCATIONS),
        "disaster_type": disaster,
        "requested_volunteers_count": volunteers,
        "deadline_hours": deadline_hours,
        "created_hour": created_hour,
        "ngo_manual_urgency": manual_urgency,
        "priority_label": final_label,
    }


# ─── Main generation ─────────────────────────────────────────────────────────

def generate_dataset(n: int = 2400, output_path: str = "data\\dataset.csv") -> pd.DataFrame:
    rows = []

    # Slightly imbalanced distribution reflecting real-world NGO tasks
    distribution = {
        "Critical": int(n * 0.28),
        "High":     int(n * 0.30),
        "Medium":   int(n * 0.24),
        "Low":      int(n * 0.18),
    }

    for label, count in distribution.items():
        for _ in range(count):
            rows.append(make_row(label))

    # Fill any rounding remainder with Critical/High
    while len(rows) < n:
        rows.append(make_row(random.choice(["Critical", "High"])))

    df = pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    print(f"✅  Dataset saved → {output_path}  ({len(df)} rows)")
    print(df["priority_label"].value_counts())
    return df


if __name__ == "__main__":
    generate_dataset()
