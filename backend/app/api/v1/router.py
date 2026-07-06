from fastapi import APIRouter

from app.advanced_ai.routes.agents import router as agents_router
from app.advanced_ai.routes.conversations import router as conversations_router
from app.advanced_ai.routes.dashboards import router as dashboards_router
from app.advanced_ai.routes.policies import router as policies_router
from app.advanced_ai.routes.rag import router as rag_router
from app.advanced_ai.routes.regressions import router as regressions_router
from app.advanced_ai.routes.safety import router as safety_router
from app.advanced_ai.routes.security import router as security_router
from app.advanced_ai.routes.tool_calls import router as tool_calls_router
from app.analytics.routes import (
    analytics_router,
    insights_router,
    leaderboards_router,
    reports_router,
    system_router,
    trends_router,
)
from app.api.v1.endpoints import (
    evaluation,
    health,
    judges,
    metrics,
    project,
    providers,
    rubrics,
)
from app.datasets.routers import benchmark_router, dataset_router, experiment_router
from app.enterprise.routes.admin import router as ent_admin_router
from app.enterprise.routes.api_keys import router as ent_keys_router
from app.enterprise.routes.audit import router as ent_audit_router
from app.enterprise.routes.billing import router as ent_billing_router
from app.enterprise.routes.organizations import router as ent_org_router
from app.enterprise.routes.workspaces import router as ent_ws_router
from app.jobs.routes.job import router as jobs_router
from app.platform.routes.mcp_api import router as mcp_router
from app.platform.routes.playground_api import router as playground_router
from app.platform.routes.plugins_api import router as plugins_router
from app.platform.routes.public_api import router as public_router
from app.platform.routes.webhooks_api import router as webhooks_router

api_router = APIRouter()

# Register endpoints
api_router.include_router(health.router, tags=["System"])
api_router.include_router(metrics.router, tags=["System"])
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

# Register Advanced AI, RAG & Enterprise Intelligence endpoints
api_router.include_router(rag_router)
api_router.include_router(safety_router)
api_router.include_router(security_router)
api_router.include_router(agents_router)
api_router.include_router(conversations_router)
api_router.include_router(regressions_router)
api_router.include_router(tool_calls_router)
api_router.include_router(policies_router)
api_router.include_router(dashboards_router)

api_router.include_router(webhooks_router)
api_router.include_router(plugins_router)
api_router.include_router(mcp_router)
api_router.include_router(playground_router)
api_router.include_router(public_router)

# Register Enterprise SaaS routes
api_router.include_router(ent_org_router)
api_router.include_router(ent_ws_router)
api_router.include_router(ent_billing_router)
api_router.include_router(ent_keys_router)
api_router.include_router(ent_audit_router)
api_router.include_router(ent_admin_router)
