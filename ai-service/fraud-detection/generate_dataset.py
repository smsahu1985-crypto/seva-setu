"""
generate_dataset.py
SevaSetu Fraud Detection â€“ Synthetic Dataset Generator
Produces 10,000+ labeled rows: legitimate (0) and fraudulent (1) requests.
"""

import random
import re
import numpy as np
import pandas as pd
from pathlib import Path

random.seed(42)
np.random.seed(42)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# GEOGRAPHY
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

CITY_STATE = {
    "Pune": "Maharashtra", "Mumbai": "Maharashtra", "Nashik": "Maharashtra",
    "Nagpur": "Maharashtra", "Delhi": "Delhi", "Bengaluru": "Karnataka",
    "Chennai": "Tamil Nadu", "Kolkata": "West Bengal", "Hyderabad": "Telangana",
    "Jaipur": "Rajasthan", "Lucknow": "Uttar Pradesh", "Ahmedabad": "Gujarat",
    "Surat": "Gujarat", "Bhopal": "Madhya Pradesh", "Patna": "Bihar",
    "Guwahati": "Assam", "Kochi": "Kerala", "Indore": "Madhya Pradesh",
    "Visakhapatnam": "Andhra Pradesh", "Coimbatore": "Tamil Nadu",
}
CITIES = list(CITY_STATE.keys())

# Mismatched city-state pairs for geo anomaly signal
WRONG_STATE = {
    "Pune": "Gujarat", "Mumbai": "Rajasthan", "Delhi": "Tamil Nadu",
    "Bengaluru": "Bihar", "Chennai": "Uttar Pradesh", "Kolkata": "Karnataka",
}

CATEGORIES = [
    "food_relief", "medical_aid", "disaster_relief", "logistics",
    "shelter", "education", "elderly_care", "blood_donation",
    "mental_health", "cleanup", "water_sanitation", "childcare",
    "fundraising", "animal_welfare", "administration",
]

LEGIT_ITEMS = {
    "food_relief":      ["food packets", "ration", "cooked meals", "water"],
    "medical_aid":      ["medicine", "first aid kit", "oxygen", "bandages"],
    "disaster_relief":  ["blankets", "tarpaulin", "food", "water", "clothes"],
    "logistics":        ["vehicle", "fuel", "packaging material"],
    "shelter":          ["tents", "blankets", "sleeping bags"],
    "education":        ["books", "notebooks", "pencils", "uniforms"],
    "elderly_care":     ["medicine", "food", "wheelchair"],
    "blood_donation":   ["blood", "plasma"],
    "cleanup":          ["cleaning supplies", "gloves", "masks"],
    "water_sanitation": ["water cans", "purification tablets", "soap"],
    "childcare":        ["toys", "food", "clothes", "books"],
    "fundraising":      ["donation", "fund"],
    "animal_welfare":   ["pet food", "medicines", "cages"],
    "administration":   ["stationery", "laptop", "internet"],
    "mental_health":    ["counseling", "support materials"],
}

SPAM_PHRASES = [
    "send money now", "wire transfer immediately", "click link for donation",
    "guaranteed relief", "100% authentic", "donate via UPI now",
    "urgent transfer needed", "verify your account", "prize money",
    "lottery winner", "free gift", "government approved scheme",
    "send your bank details", "limited time offer", "act now or lose",
    "double your donation", "secret relief fund",
]

LEGIT_DESCRIPTIONS = [
    "Flood affected families in {city} urgently need food and blankets. {n} people displaced.",
    "Medical camp in {city} requires {n} volunteer doctors this weekend.",
    "Need {n} volunteers for food distribution at relief camp in {city} tomorrow.",
    "Blood donors urgently needed in {city} for accident victim at City Hospital.",
    "{n} elderly residents in {city} need daily medicine and meals.",
    "Post-cyclone cleanup drive in {city}. Need {n} enthusiastic volunteers.",
    "Ration distribution for {n} poor families in {city} next Saturday.",
    "Free coaching classes for underprivileged children in {city}. Need {n} teachers.",
    "Earthquake relief camp in {city}. {n} survivors need food and shelter.",
    "Water shortage in {city} locality. Need volunteers for distribution to {n} families.",
    "Temporary shelter setup for {n} displaced people in {city} after fire incident.",
    "Need {n} bike volunteers to deliver medicines to elderly patients in {city}.",
    "Animal rescue drive after floods in {city}. {n} volunteers required.",
    "Mental health counseling camp for trauma survivors in {city}. {n} counselors needed.",
    "Awareness drive on dengue prevention in {city}. Need {n} volunteers.",
]

FRAUD_DESCRIPTIONS = [
    "Need {n} oxygen cylinders in 10 minutes send now URGENT URGENT URGENT",
    "SEND MONEY NOW for {n} families in {city} donate via UPI link immediately",
    "Need {n} food packets RIGHT NOW government approved verified 100% authentic",
    "Click the link to donate for flood victims in {city} limited time offer",
    "Urgent transfer of funds needed for {n} patients send bank details",
    "Need {n} volunteers immediately secret relief fund approved by government",
    "LOTTERY WINNER selected for relief fund in {city} claim your prize now",
    "Send {n} blankets and ration in 5 minutes or people will die",
    "Guaranteed relief for {n} families double your donation act now",
    "Free gift for donors helping {n} people in {city} verify your UPI",
    "Need help {n} {n} {n} urgent urgent urgent send everything now",
    "Flood relief {city} {city} {city} 9999999 people affected send money wire transfer",
    "Crisis in {city}. Need 10000 medicine cylinders food blankets tents doctors NOW",
    "Anonymous request for {n} items no details necessary just send ASAP",
    "Very urgent very urgent {n} people dying send resources no questions asked",
]


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# PHONE NUMBER GENERATORS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def legit_phone():
    prefixes = ["98", "97", "96", "95", "94", "93", "91", "90", "89", "88", "87", "86", "85", "84", "83", "82", "81", "80", "79", "78", "77", "76", "75", "74", "73", "72", "71", "70"]
    return random.choice(prefixes) + str(random.randint(10000000, 99999999))

def suspicious_phone():
    patterns = [
        "9999999999", "1234567890", "0000000000", "1111111111",
        "9876543210", "1234512345", "9999988888",
    ]
    if random.random() < 0.5:
        return random.choice(patterns)
    # Repeated digit patterns
    d = random.randint(1, 9)
    return str(d) * 10


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ROW GENERATORS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def make_legit_row(idx):
    city  = random.choice(CITIES)
    state = CITY_STATE[city]
    cat   = random.choice(CATEGORIES)
    n     = random.choice([10, 20, 30, 50, 75, 100, 150, 200])
    n_vol = random.choice([2, 3, 5, 8, 10, 15, 20])

    desc_tmpl = random.choice(LEGIT_DESCRIPTIONS)
    desc = desc_tmpl.format(city=city, n=n)

    items = random.sample(LEGIT_ITEMS.get(cat, ["supplies"]),
                          k=min(2, len(LEGIT_ITEMS.get(cat, ["supplies"]))))

    title_prefixes = [
        f"Help needed in {city}",
        f"Volunteer request â€“ {city}",
        f"Relief drive â€“ {city}",
        f"Urgent aid â€“ {cat.replace('_',' ').title()}",
        f"Community support â€“ {city}",
    ]

    deadline = random.choice([6, 12, 24, 48, 72, 168])
    hour     = random.choices(range(24), weights=[
        1,1,1,1,1,2,4,6,8,8,8,7,7,8,8,8,7,6,5,4,3,2,2,1
    ])[0]

    # Fraud signal features (all low for legit)
    qty_requested     = n
    people_affected   = n + random.randint(0, 50)
    qty_per_person    = qty_requested / max(people_affected, 1)

    return {
        "request_title":       random.choice(title_prefixes),
        "request_description": desc,
        "category":            cat,
        "location_city":       city,
        "location_state":      state,
        "people_affected":     people_affected,
        "volunteers_needed":   n_vol,
        "required_items":      "|".join(items),
        "deadline_hours":      deadline,
        "contact_phone":       legit_phone(),
        "user_type":           random.choice(["public", "ngo"]),
        "created_at_hour":     hour,
        # Engineered fraud signals
        "desc_length":         len(desc),
        "desc_word_count":     len(desc.split()),
        "has_spam_phrase":     0,
        "title_desc_mismatch": 0,
        "qty_requested":       qty_requested,
        "qty_per_person_ratio":round(qty_per_person, 3),
        "deadline_too_short":  int(deadline < 1),
        "is_late_night":       int(hour < 4 or hour >= 23),
        "city_state_mismatch": 0,
        "phone_suspicious":    0,
        "repeated_words":      0,
        "description_vague":   int(len(desc.split()) < 6),
        "exclamation_count":   desc.count("!"),
        "caps_ratio":          round(sum(1 for c in desc if c.isupper()) / max(len(desc), 1), 3),
        "label":               0,   # legitimate
        "fraud_type":          "none",
    }


def make_fraud_row(idx):
    city       = random.choice(CITIES)
    fraud_type = random.choice([
        "impossible_quantity", "spam_language", "geo_mismatch",
        "deadline_abuse", "suspicious_phone", "duplicate_spam",
        "inflated_numbers", "prank", "fake_campaign",
    ])

    cat = random.choice(CATEGORIES)

    # Build fraudulent description
    n_fake    = random.choice([500, 1000, 5000, 10000, 50000])
    desc_tmpl = random.choice(FRAUD_DESCRIPTIONS)
    desc      = desc_tmpl.format(city=city, n=n_fake)

    # Inject spam phrase
    if random.random() < 0.6:
        spam = random.choice(SPAM_PHRASES)
        desc = desc + " " + spam

    # Caps abuse
    if random.random() < 0.4:
        desc = desc.upper()

    # Repeated words / exclamation abuse
    if random.random() < 0.5:
        desc += " URGENT! URGENT! URGENT! HELP NOW!!!"

    people_affected = random.choice([1, 2, 3, 5, 0])  # very low vs massive request

    # Geo mismatch
    city_state_mismatch = 0
    state = CITY_STATE[city]
    if fraud_type == "geo_mismatch" or random.random() < 0.3:
        state = WRONG_STATE.get(city, "Unknown State")
        city_state_mismatch = 1

    # Suspicious phone
    phone = suspicious_phone() if (fraud_type == "suspicious_phone" or random.random() < 0.4) else legit_phone()
    phone_suspicious = int(phone in [
        "9999999999", "1234567890", "0000000000", "1111111111",
        "9876543210", "1234512345", "9999988888",
    ] or len(set(phone)) <= 2)

    # Deadline
    deadline = random.choice([0, 1, 2]) if fraud_type == "deadline_abuse" else random.choice([1, 2, 0])
    deadline_too_short = int(deadline < 1)

    # Late night
    hour = random.choice([0, 1, 2, 3, 23]) if random.random() < 0.5 else random.randint(0, 23)
    is_late_night = int(hour < 4 or hour >= 23)

    # Spam detection
    desc_lower = desc.lower()
    has_spam   = int(any(sp in desc_lower for sp in SPAM_PHRASES))

    # Caps ratio
    caps_ratio = round(sum(1 for c in desc if c.isupper()) / max(len(desc), 1), 3)

    # Repeated words
    words = desc.lower().split()
    word_counts = {}
    for w in words:
        word_counts[w] = word_counts.get(w, 0) + 1
    repeated = int(any(v >= 3 for v in word_counts.values()))

    qty_per_person = n_fake / max(people_affected, 1)

    # Title mismatch (sometimes)
    title = random.choice([
        f"URGENT HELP {city}",
        "Emergency Request",
        "Send Everything Now",
        f"Critical Need {city}",
        "Immediate Assistance Required",
        "HELP HELP HELP",
        f"Fake Relief Fund {city}",
    ])

    items = random.sample(LEGIT_ITEMS.get(cat, ["supplies"]), k=1)

    return {
        "request_title":       title,
        "request_description": desc,
        "category":            cat,
        "location_city":       city,
        "location_state":      state,
        "people_affected":     people_affected,
        "volunteers_needed":   random.choice([0, 0, 0, 1]),
        "required_items":      "|".join(items),
        "deadline_hours":      deadline,
        "contact_phone":       phone,
        "user_type":           random.choice(["public", "ngo"]),
        "created_at_hour":     hour,
        # Fraud signal features
        "desc_length":         len(desc),
        "desc_word_count":     len(desc.split()),
        "has_spam_phrase":     has_spam,
        "title_desc_mismatch": int(random.random() < 0.5),
        "qty_requested":       n_fake,
        "qty_per_person_ratio":round(min(qty_per_person, 9999), 3),
        "deadline_too_short":  deadline_too_short,
        "is_late_night":       is_late_night,
        "city_state_mismatch": city_state_mismatch,
        "phone_suspicious":    phone_suspicious,
        "repeated_words":      repeated,
        "description_vague":   int(len(desc.split()) < 6),
        "exclamation_count":   desc.count("!"),
        "caps_ratio":          caps_ratio,
        "label":               1,   # fraudulent
        "fraud_type":          fraud_type,
    }


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# MAIN
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def generate_dataset(n_total: int = 10500, fraud_ratio: float = 0.35,
                     output_path: str = "data/dataset.csv"):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    n_fraud = int(n_total * fraud_ratio)
    n_legit = n_total - n_fraud

    print(f"Generating {n_legit} legitimate + {n_fraud} fraudulent rows ...")

    legit_rows = [make_legit_row(i) for i in range(n_legit)]
    fraud_rows = [make_fraud_row(i) for i in range(n_fraud)]

    df = pd.DataFrame(legit_rows + fraud_rows)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    df.to_csv(output_path, index=False)
    print(f"Saved -> {output_path}  ({len(df)} rows)")
    print(f"    Label distribution:\n{df['label'].value_counts().to_string()}")
    print(f"    Fraud types:\n{df[df['label']==1]['fraud_type'].value_counts().to_string()}")
    return df


if __name__ == "__main__":
    generate_dataset()
