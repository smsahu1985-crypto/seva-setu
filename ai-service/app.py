"""
app.py
SevaSetu Priority AI – FastAPI Service
Run: uvicorn app:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict
import time

from predict import predict_priority

# ─── FastAPI app ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="SevaSetu Priority AI",
    description="AI-powered volunteer task priority scoring for NGOs",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request / Response schemas ───────────────────────────────────────────────

class TaskInput(BaseModel):
    task_title: str = Field(..., example="Urgent medical volunteers needed at flood camp")
    task_description: str = Field(..., example="Flood victims stranded. Need triage support tonight.")
    task_category: str = Field(..., example="Medical")
    location: str = Field(..., example="Assam")
    disaster_type: str = Field(default="None", example="Flood")
    requested_volunteers_count: int = Field(default=3, ge=1, le=500, example=3)
    deadline_hours: float = Field(default=72, ge=0, le=8760, example=6)
    created_hour: int = Field(default=12, ge=0, le=23, example=21)
    ngo_manual_urgency: str = Field(default="medium",
                                     example="critical",
                                     description="critical | high | medium | low")

    class Config:
        json_schema_extra = {
            "example": {
                "task_title": "Urgent medical volunteers needed at flood camp tonight",
                "task_description": "Flood victims stranded. Need 3 medical volunteers for triage immediately.",
                "task_category": "Medical",
                "location": "Assam",
                "disaster_type": "Flood",
                "requested_volunteers_count": 3,
                "deadline_hours": 6,
                "created_hour": 21,
                "ngo_manual_urgency": "critical",
            }
        }


class PriorityResponse(BaseModel):
    label: str
    score: float
    confidence: float
    probabilities: Dict[str, float]
    reasoning: str
    latency_ms: float


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "SevaSetu Priority AI", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


@app.post("/predict-priority", response_model=PriorityResponse, tags=["Prediction"])
def predict_priority_endpoint(task: TaskInput):
    """
    Predict the priority label and score for an NGO volunteer task.

    **Labels**: Critical | High | Medium | Low

    **Score**: 0–100 numeric priority (higher = more urgent)

    **Confidence**: Model certainty [0.0 – 1.0]
    """
    t0 = time.perf_counter()
    try:
        result = predict_priority(task.dict())
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e) + " — Please train the model first: `python train.py`",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

    latency = round((time.perf_counter() - t0) * 1000, 2)
    return PriorityResponse(latency_ms=latency, **result)


@app.post("/predict-batch", tags=["Prediction"])
def predict_batch(tasks: list[TaskInput]):
    """
    Batch predict priorities for multiple tasks at once.
    Returns list ordered by score descending (most urgent first).
    """
    if len(tasks) > 50:
        raise HTTPException(status_code=400, detail="Max 50 tasks per batch request.")

    results = []
    for i, task in enumerate(tasks):
        try:
            res = predict_priority(task.dict())
            res["task_index"] = i
            res["task_title"] = task.task_title
            results.append(res)
        except Exception as e:
            results.append({"task_index": i, "task_title": task.task_title,
                            "error": str(e)})

    # Sort by score descending
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return {"count": len(results), "tasks": results}


# ─── Run directly ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
