# SevaSetu Priority AI 🚨

> AI-powered volunteer task priority scoring for NGOs  
> **Hackathon Project: SevaSetu**

---

## Overview

SevaSetu Priority AI is a hybrid NLP model that automatically assigns priority labels (**Critical / High / Medium / Low**) and numeric scores (0–100) to NGO volunteer tasks. It helps volunteers see the most urgent tasks first.

### How it works

```
Task (title + description + metadata)
          │
          ▼
  MiniLM Embeddings (384-dim semantic vectors)
          +
  Keyword Heuristics (urgency signal boost)
          +
  Structured Features (deadline, category, disaster type …)
          │
          ▼
     LightGBM Classifier
          │
          ▼
  Priority Label + Score + Confidence + Reasoning
```

---

## Project Structure

```
priority_ai/
├── generate_dataset.py   # Synthetic training data generator (2400+ rows)
├── train.py              # Full training pipeline with metrics
├── predict.py            # Inference pipeline (predict_priority function)
├── app.py                # FastAPI REST API
├── requirements.txt      # Python dependencies
├── dataset.csv           # Auto-generated after running generate_dataset.py
├── model.pkl             # Saved model artifacts (after training)
├── encoder.pkl           # Encoder info
└── README.md
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate training data

```bash
python generate_dataset.py
```

Generates `dataset.csv` with 2400 realistic rows.

### 3. Train the model

```bash
python train.py
```

Prints accuracy, F1 scores, confusion matrix, and feature importances.  
Saves `model.pkl`.

### 4. Test predictions

```bash
python predict.py
```

Runs 4 sample predictions from Critical → Low.

### 5. Start the API

```bash
uvicorn app:app --reload --port 8000
```

Visit: http://localhost:8000/docs (Swagger UI)

---

## API Usage

### POST `/predict-priority`

```bash
curl -X POST http://localhost:8000/predict-priority \
  -H "Content-Type: application/json" \
  -d '{
    "task_title": "Urgent medical volunteers needed at flood camp tonight",
    "task_description": "Flood victims stranded. Need 3 medical volunteers for triage immediately.",
    "task_category": "Medical",
    "location": "Assam",
    "disaster_type": "Flood",
    "requested_volunteers_count": 3,
    "deadline_hours": 6,
    "created_hour": 21,
    "ngo_manual_urgency": "critical"
  }'
```

**Response:**

```json
{
  "label": "Critical",
  "score": 94.5,
  "confidence": 0.9223,
  "probabilities": {
    "Critical": 0.9223,
    "High": 0.0612,
    "Medium": 0.0121,
    "Low": 0.0044
  },
  "reasoning": "Predicted Critical (confidence 92%) — very tight deadline (6h); active disaster context (Flood); life-critical keywords detected; NGO flagged as critical.",
  "latency_ms": 85.4
}
```

### POST `/predict-batch`

Send up to 50 tasks at once. Returns sorted by score descending (most urgent first).

---

## Model Details

| Component | Choice | Why |
|-----------|--------|-----|
| Text encoder | `all-MiniLM-L6-v2` | Fast, ~80MB, great semantic quality |
| Classifier | LightGBM | Fast training, handles mixed features, great on tabular |
| Features | Embeddings + keywords + categoricals + numerics | Hybrid = robust |

### Feature groups

1. **384-dim MiniLM embeddings** — semantic meaning of task text
2. **Keyword heuristics** — explicit urgency signal counts (4 features)
3. **Categorical encoding** — task_category, disaster_type, ngo_manual_urgency
4. **Numerical** — deadline_hours, volunteers_count, created_hour, urgency_ratio, is_night_flag

### Label → Score mapping

| Label | Base Score | Range |
|-------|-----------|-------|
| Critical | 90 | 80–100 |
| High | 70 | 60–80 |
| Medium | 45 | 35–55 |
| Low | 20 | 10–30 |

---

## Priority Decision Logic

| Pattern | Label |
|---------|-------|
| Medical + immediate + disaster zone | Critical |
| Blood donation urgency | Critical |
| Rescue / stranded / landslide | Critical |
| Medicine delivery today | Critical |
| Food distribution tomorrow | High |
| Shelter setup this evening | High |
| Relief camp sanitation this week | High |
| Weekend donation packaging | Medium |
| Awareness campaign this week | Medium |
| Educational sorting next week | Low |
| Admin/data entry next month | Low |

---

## Improving with Real Data

Once you collect real NGO task data:

1. **Export labels** from NGO feedback / admin review
2. **Retrain** with `python train.py` (just replace or extend `dataset.csv`)
3. Consider switching to **DistilBERT fine-tuning** for even better semantic understanding
4. Add **active learning**: collect corrections from NGO admins as a signal
5. Add **temporal features**: time since disaster event, seasonal patterns

---

## Integration with SevaSetu

In your NGO task creation flow:

```python
from predict import predict_priority

# When NGO creates a task:
result = predict_priority(task_dict)

# Store in DB:
task.priority_label = result["label"]
task.priority_score = result["score"]
task.priority_confidence = result["confidence"]

# Volunteers see tasks sorted by priority_score DESC
```

---

*Built for SevaSetu Hackathon 🇮🇳*
