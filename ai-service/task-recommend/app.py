from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from recommend import TaskRecommender

app = FastAPI(
    title="SevaSetu Volunteer Recommendation API",
    description="AI-powered volunteer task recommendation engine for NGOs",
    version="1.1.0"
)

# --------------------------------------------------
# CORS (React frontend support)
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Load recommender once on startup
# --------------------------------------------------

recommender = TaskRecommender()


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class RecommendRequest(BaseModel):
    volunteer_profile: Dict[str, Any]
    tasks: List[Dict[str, Any]]

    top_k: int = 5
    apply_diversity: bool = True
    filter_full_tasks: bool = False

    # NEW: frontend distance filter
    radius_km: Optional[int] = None


class BatchRecommendRequest(BaseModel):
    volunteers: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    top_k: int = 5


# --------------------------------------------------
# ROUTES
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "SevaSetu Volunteer Recommendation AI",
        "version": "1.1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": recommender.model is not None
    }


@app.post("/recommend-tasks")
def recommend_tasks(req: RecommendRequest):
    try:
        results = recommender.recommend(
            volunteer=req.volunteer_profile,
            tasks=req.tasks,
            top_k=req.top_k,
            apply_diversity=req.apply_diversity,
            filter_full_tasks=req.filter_full_tasks,
            radius_km=req.radius_km
        )

        return {
            "success": True,
            "count": len(results),
            "radius_used": req.radius_km,
            "recommendations": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend-batch")
def recommend_batch(req: BatchRecommendRequest):
    try:
        results = recommender.recommend_batch(
            volunteers=req.volunteers,
            tasks=req.tasks,
            top_k=req.top_k
        )

        return {
            "success": True,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))