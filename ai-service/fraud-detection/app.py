from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from predict import MODEL_PATH, load_model, predict_batch, predict_fraud


model_store: dict[str, Any] = {"model": None}


class FraudRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    request_title: str = ""
    request_description: str = ""
    category: str = "unknown"
    location_city: str = ""
    location_state: str = ""
    people_affected: int = Field(default=1, ge=0)
    volunteers_needed: int = Field(default=0, ge=0)
    required_items: list[str] | str = Field(default_factory=list)
    deadline_hours: int = Field(default=24, ge=0)
    contact_phone: str = ""
    user_type: str = "public"
    created_at_hour: int = Field(default=12, ge=0, le=23)


class BatchFraudRequest(BaseModel):
    requests: list[FraudRequest]


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_store["model"] = load_model()
    yield


app = FastAPI(
    title="SevaSetu Fraud Detection AI",
    description="Decision-support API for detecting suspicious public and NGO requests.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "service": "SevaSetu Fraud Detection AI",
        "status": "running",
        "message": "Use POST /detect-fraud or POST /detect-batch to score requests.",
        "human_review_required": True,
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "success": True,
        "status": "healthy",
        "model_loaded": model_store["model"] is not None,
        "model_path": str(MODEL_PATH),
    }


@app.post("/detect-fraud")
def detect_fraud(request: FraudRequest) -> dict[str, Any]:
    result = predict_fraud(request.model_dump(), model=model_store["model"])
    return {"success": True, **result}


@app.post("/detect-batch")
def detect_batch(batch: BatchFraudRequest) -> dict[str, Any]:
    requests = [request.model_dump() for request in batch.requests]
    results = predict_batch(requests, model=model_store["model"])
    return {
        "success": True,
        "count": len(results),
        "results": results,
    }
