# SevaSetu Fraud Detection AI

FastAPI microservice for helping SevaSetu admins detect suspicious public and NGO requests before resources are wasted.

The service returns:

- `fraud_score` from 0 to 100
- `risk_level`: `low`, `medium`, `high`, or `critical`
- `is_suspicious`
- human-readable reasons
- recommended admin action

Important: Fraud Detection AI is a decision-support system. Final approval should be done by human admins.

## Project Structure

```text
ai-service/fraud-detection/
├── app.py
├── train.py
├── predict.py
├── generate_dataset.py
├── requirements.txt
├── README.md
├── models/
│   └── fraud_model.pkl
└── data/
    └── dataset.csv
```

## Setup

```bash
cd ai-service/fraud-detection
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux, activate with:

```bash
source .venv/bin/activate
```

## Generate Dataset

`generate_dataset.py` creates 10,000+ synthetic Indian public and NGO requests with legitimate and fraudulent labels.

```bash
python generate_dataset.py
```

Output:

```text
data/dataset.csv
```

## Train Model

```bash
python train.py
```

Output:

```text
models/fraud_model.pkl
```

The model is a practical hackathon-friendly hybrid:

- rule engine for high-precision fraud signals and admin explanations
- ML classifier using text TF-IDF, categorical features, and engineered numeric anomaly features
- ensemble classifier tuned to be conservative for high-risk fraud

## Run API

```bash
uvicorn app:app --reload
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## API Routes

### `GET /`

Service metadata.

### `GET /health`

Health check and model loading status.

### `POST /detect-fraud`

Scores one request.

Example:

```json
{
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
  "created_at_hour": 3
}
```

Example response:

```json
{
  "success": true,
  "fraud_score": 92,
  "risk_level": "critical",
  "is_suspicious": true,
  "reasons": [
    "Unrealistic quantity requested",
    "Deadline unrealistic",
    "Late-night suspicious timing",
    "Phone number pattern suspicious"
  ],
  "recommended_action": "manual_review"
}
```

Minimal request example:

```json
{
  "request_description": "Need 500 food packets in 10 minutes",
  "location_city": "Pune",
  "people_affected": 3
}
```

### `POST /detect-batch`

Scores many requests and returns them sorted by highest fraud risk first.

```json
{
  "requests": [
    {
      "request_description": "Need 500 food packets in 10 minutes",
      "location_city": "Pune",
      "people_affected": 3
    },
    {
      "request_description": "Need 20 volunteers for food distribution tomorrow",
      "category": "food_relief",
      "location_city": "Mumbai",
      "location_state": "Maharashtra",
      "people_affected": 100,
      "deadline_hours": 24
    }
  ]
}
```

## Fraud Signals

The system checks:

- impossible quantities and inflated inventory needs
- exaggerated urgency and impossible deadlines
- vague descriptions
- repeated spam or scam language
- title and description mismatch
- category and item mismatch
- suspicious phone number patterns
- late-night suspicious timing
- city and state mismatch
- NGO-style fake donation campaigns and repeated campaign language

## Admin Workflow

The admin dashboard can use this API to:

- show flagged requests first
- sort by `fraud_score`
- display reasons beside each request
- approve legitimate requests
- reject clear spam
- mark false positives as safe
- send high and critical cases to manual review

Recommended action mapping:

- `low`: approve with normal checks
- `medium`: verify details
- `high`: manual review
- `critical`: urgent manual review

## Limitations

- The default dataset is synthetic and should be replaced or fine-tuned with real SevaSetu moderation history.
- The service detects risk signals; it does not prove fraud.
- Some genuine emergencies can look suspicious because urgent requests often contain unusual quantities or deadlines.
- Phone reuse and duplicate request detection are stronger when connected to production request history.
- Geo validation currently uses a fixed city-state map.

## Future Improvements

- Add request history features per user, phone number, NGO, and device.
- Add duplicate detection using semantic similarity.
- Add real moderation feedback loop from admin decisions.
- Add city/state validation from a maintained geo database.
- Add separate NGO campaign fraud model.
- Add explainability dashboard charts for admins.
- Add threshold tuning by district, category, and disaster context.
