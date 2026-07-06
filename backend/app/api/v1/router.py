from fastapi import APIRouter

from app.api.v1.endpoints import evaluation, health, judges, project, providers, rubrics
from app.datasets.routers import benchmark_router, dataset_router, experiment_router
from app.jobs.routes.job import router as jobs_router
from app.analytics.routes import (
    analytics_router,
    reports_router,
    leaderboards_router,
    insights_router,
    trends_router,
    system_router,
)

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
api_router.include_router(dataset_router)
api_router.include_router(benchmark_router)
api_router.include_router(experiment_router)
api_router.include_router(jobs_router)

# Register Analytics and Observability endpoints
api_router.include_router(analytics_router)
api_router.include_router(reports_router)
api_router.include_router(leaderboards_router)
api_router.include_router(insights_router)
api_router.include_router(trends_router)
api_router.include_router(system_router)

