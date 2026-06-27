from fastapi import APIRouter

from app.api.v1.endpoints import health, project, evaluation

api_router = APIRouter()

# Register endpoints
api_router.include_router(health.router, tags=["System"])
api_router.include_router(project.router, prefix="/projects", tags=["Projects"])
api_router.include_router(evaluation.router, prefix="/evaluations", tags=["Evaluations"])
