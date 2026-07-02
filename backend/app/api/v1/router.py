from fastapi import APIRouter

from app.api.v1.endpoints import evaluation, health, judges, providers, project, rubrics

api_router = APIRouter()

# Register endpoints
api_router.include_router(health.router, tags=["System"])
api_router.include_router(project.router, prefix="/projects", tags=["Projects"])
api_router.include_router(providers.router, tags=["Providers"])
api_router.include_router(judges.router, tags=["Judges"])
api_router.include_router(rubrics.router, tags=["Rubrics"])
api_router.include_router(
    evaluation.router, prefix="/evaluations", tags=["Evaluations"]
)
