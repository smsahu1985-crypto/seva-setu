"""
app.py
SevaSetu Request Autofill – FastAPI Microservice

Run:
    uvicorn app:app --reload --port 8002
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
import time
import sys
import os

# Ensure local imports resolve correctly regardless of working directory
sys.path.insert(0, str(Path(__file__).parent))

from predict import autofill

# ─────────────────────────────────────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="SevaSetu – Request Autofill AI",
    description=(
        "AI microservice that parses a free-text help request and automatically "
        "fills NGO form fields: category, urgency, location, skills, volunteers needed, etc."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# Request / Response schemas
# ─────────────────────────────────────────────────────────────────────────────

class AutofillRequest(BaseModel):
    request_description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        example="Need 5 volunteers in Pune for food distribution tomorrow",
    )

class ConfidenceScores(BaseModel):
    category:                   float
    subcategory:                float
    urgency_level:              float
    location_city:              float
    deadline_hours:             float
    required_skills:            float
    volunteers_needed:          float
    estimated_people_affected:  float
    is_medical_emergency:       float
    is_disaster_related:        float
    transport_required:         float

class AutofillResponse(BaseModel):
    success: bool

    # Core fields
    request_title:              str
    category:                   str
    subcategory:                str
    urgency_level:              str
    priority_label:             str

    # People
    estimated_people_affected:  int
    family_count:               int

    # Location
    location_city:              str
    location_state:             str

    # Timing
    deadline_hours:             int

    # Skills / Items
    required_skills:            list[str]
    required_items:             list[str]

    # Volunteer
    volunteers_needed:          int

    # Boolean flags
    is_medical_emergency:       bool
    is_disaster_related:        bool
    transport_required:         bool

    # Contact
    contact_preference:         str

    # Volunteer task fields
    task_type:                  str
    effort_level:               str
    min_experience_level:       str
    shift_type:                 str

    # Public request fields
    need_type:                  str
    children_involved:          bool
    elderly_involved:           bool

    # Meta
    confidence:                 dict
    processing_time_ms:         float
    disclaimer:                 str


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
def root():
    return {
        "service":     "SevaSetu Request Autofill AI",
        "version":     "1.0.0",
        "status":      "running",
        "endpoints": {
            "autofill": "POST /autofill",
            "health":   "GET  /health",
            "docs":     "GET  /docs",
        },
    }


@app.get("/health", tags=["Info"])
def health():
    model_path = Path(__file__).parent / "models" / "autofill_model.pkl"
    model_ready = model_path.exists()
    return {
        "status":      "healthy" if model_ready else "degraded",
        "model_ready": model_ready,
        "message":     "Model loaded and ready." if model_ready else "Model not found. Run: python train.py",
    }


@app.post("/autofill", response_model=AutofillResponse, tags=["Autofill"])
def autofill_endpoint(payload: AutofillRequest):
    """
    Parse a free-text help/volunteer request and return predicted form fields.

    ⚠️  AI Autofill is assistive only. Please review all autofilled fields before submission.
    """
    t0 = time.time()

    try:
        result = autofill(payload.request_description)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e) + " — train the model first: python train.py",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {e}")

    elapsed_ms = round((time.time() - t0) * 1000, 2)

    return AutofillResponse(
        success=True,
        **result,
        processing_time_ms=elapsed_ms,
        disclaimer=(
            "⚠️ AI Autofill is assistive only. "
            "Please review all autofilled fields before submission."
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Batch endpoint (bonus)
# ─────────────────────────────────────────────────────────────────────────────

class BatchRequest(BaseModel):
    descriptions: list[str] = Field(..., max_length=20)

@app.post("/autofill/batch", tags=["Autofill"])
def autofill_batch(payload: BatchRequest):
    """
    Autofill up to 20 requests at once. Returns list of results in same order.
    """
    results = []
    for desc in payload.descriptions:
        try:
            r = autofill(desc)
            r["success"] = True
            r["input"] = desc
        except Exception as e:
            r = {"success": False, "error": str(e), "input": desc}
        results.append(r)
    return {"results": results, "count": len(results)}
